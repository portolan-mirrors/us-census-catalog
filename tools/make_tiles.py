#!/usr/bin/env python3
"""Build every PMTiles archive with tylertoo (A5 cells at coarse zooms).

One recipe per collection, and the recipes are the record of how each
published archive was made: the command lines below are the ones in
staging/tiles-logs/<id>.log, byte for byte. Nothing here mutates the
catalog until a job is named on the command line, because re-tiling an
archive that is already built and QC'd costs twenty minutes and gains
nothing.

Usage:
  python3 tools/make_tiles.py --list                 # recipes, no work
  python3 tools/make_tiles.py --print zctas          # the exact command
  python3 tools/make_tiles.py zctas places           # build those two
  python3 tools/make_tiles.py --all                  # everything

Three families of recipe:

  A5 + geometry   The fine geographies (block groups, tracts, blocks) and
                  the two wave-3 collections with tens of thousands of
                  features: A5 cell aggregation at coarse zooms, real
                  geometry at feature zooms. Counts are summed, rates,
                  medians and coefficients of variation averaged unweighted
                  over the geographies in the cell. `*_moe` columns are
                  excluded from the tiles — a margin of error that has been
                  averaged over an A5 cell is not a margin of error.
  geometry only   The coarse geographies (states, counties, congressional
                  districts): few enough features that every zoom can carry
                  the real polygons.
  blocks          Its own band split and its own column set (2020 Decennial
                  counts, no margins of error, no CVs).

See docs/design.md for the band design and the QC findings (the coarsest
geometry zooms in dense metros ride the 500K merge valve; the wide tables —
counties and congressional districts, 110 columns on few features — need
--max-compressed-tile-size 2M).
"""

import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import duckdb

ROOT = "/Users/cholmes/repos/us-census-catalog"
TT = "/Users/cholmes/repos/tylertoo/target/release/tylertoo"
LOGDIR = f"{ROOT}/staging/tiles-logs"
SPILL = f"{ROOT}/staging/tiles-tmp"

SKIP_ALWAYS = {"geoid", "name", "state", "geometry", "bbox"}

# (group, id, sum_cols, a5_band, geom_band) for the 9 themed ACS chunks and
# the two wave-3 collections that are fine enough to need A5 cells. A wave-3
# collection sits at the catalog root, so its group is None.
#
# zctas and places take the tract bands (0-5:a5, 6-12:geom): 33,791 ZCTAs and
# 32,612 places are the same order of magnitude as 85,184 tracts and far
# coarser than 242,298 block groups, and both are polygon sets a reader
# expects to see shaped at z6. Their sum_cols are every count column in the
# wide table, because the wide table carries all five.
WIDE_SUMS = ("population", "housing_units", "households", "hh_no_vehicle",
             "group_quarters_pop")

ACS_CHUNKS = [
    ("block-groups", "bg-income", ("population",), "0-7:a5", "8-13:geom"),
    ("block-groups", "bg-people", ("population",), "0-7:a5", "8-13:geom"),
    ("block-groups", "bg-housing", ("population", "housing_units", "households"), "0-7:a5", "8-13:geom"),
    ("block-groups", "bg-connectivity", ("population", "hh_no_vehicle"), "0-7:a5", "8-13:geom"),
    ("tracts", "tract-income", ("population",), "0-5:a5", "6-12:geom"),
    ("tracts", "tract-people", ("population",), "0-5:a5", "6-12:geom"),
    ("tracts", "tract-housing", ("population", "housing_units", "households"), "0-5:a5", "6-12:geom"),
    ("tracts", "tract-connectivity", ("population", "hh_no_vehicle"), "0-5:a5", "6-12:geom"),
    ("tracts", "tract-wellbeing", ("population", "group_quarters_pop"), "0-5:a5", "6-12:geom"),
    (None, "zctas", WIDE_SUMS, "0-5:a5", "6-12:geom"),
    (None, "places", WIDE_SUMS, "0-5:a5", "6-12:geom"),
]

# (id, band, max_compressed_tile_size) for the geometry-only archives.
# counties and congressional-districts carry 110 columns on a few thousand
# and a few hundred features, so a single z0 tile holds every attribute of
# every feature and overruns the default compressed-tile cap; 2M is the
# counties precedent (staging/tiles-logs/counties.log). states fits under the
# default because there are 56 of them.
GEOM_ONLY = [
    ("counties", "0-10:geom", "2M"),
    ("states", "0-8:geom", None),
    ("congressional-districts", "0-10:geom", "2M"),
]


def coll_dir(group, cid):
    return f"{ROOT}/catalog/{group}/{cid}" if group else f"{ROOT}/catalog/{cid}"


def columns(path):
    return [r[0] for r in duckdb.sql(
        f"DESCRIBE SELECT * FROM read_parquet('{path}')").fetchall()]


def classify(path, sum_cols):
    cols = columns(path)
    moe = [c for c in cols if c.endswith("_moe")]
    cv = [c for c in cols if c.endswith("_cv")]
    data_cols = [c for c in cols if c not in SKIP_ALWAYS and not c.endswith("_moe")]
    mean_cols = [c for c in data_cols if c not in sum_cols and c not in cv and
                 (c.startswith("pct_") or c.startswith("median_") or c in ("per_capita_income", "pop_density"))]
    return moe, list(sum_cols), mean_cols, cv


def moe_cols(path):
    return [c for c in columns(path) if c.endswith("_moe")]


def build_acs_cmd(group, cid, sum_cols, a5_band, geom_band, extra_pivot_shift=0):
    d = coll_dir(group, cid)
    path, out = f"{d}/{cid}.parquet", f"{d}/{cid}.pmtiles"
    moe, sum_cols, mean_cols, cv_cols = classify(path, sum_cols)
    cmd = [TT, "tiles", path, out]
    if extra_pivot_shift:
        lo, hi = a5_band.split(":")[0].split("-")
        lo2, hi2 = geom_band.split(":")[0].split("-")
        a5_band = f"{lo}-{int(hi)+extra_pivot_shift}:a5"
        geom_band = f"{int(lo2)+extra_pivot_shift}-{hi2}:geom"
    cmd += ["--band", a5_band, "--band", geom_band]
    for c in sum_cols:
        cmd += ["--accumulate-attribute", f"{c}:sum"]
    for c in mean_cols:
        cmd += ["--accumulate-attribute", f"{c}:mean"]
    for c in cv_cols:
        cmd += ["--accumulate-attribute", f"{c}:mean"]
    for c in moe:
        cmd += ["--exclude-property", c]
    cmd += ["--spill-dir", SPILL, "-f"]
    return cmd, out


def build_geom_cmd(cid, band, max_tile):
    d = coll_dir(None, cid)
    path, out = f"{d}/{cid}.parquet", f"{d}/{cid}.pmtiles"
    cmd = [TT, "tiles", path, out, "--band", band]
    if max_tile:
        cmd += ["--max-compressed-tile-size", max_tile]
    for c in moe_cols(path):
        cmd += ["--exclude-property", c]
    cmd += ["--spill-dir", SPILL, "-f"]
    return cmd, out


# ===== blocks: 2020 Decennial counts, 8.17M features =========================
BLOCK_SUMS = [
    "pop_total", "pop_white", "pop_black", "pop_aian", "pop_asian", "pop_nhpi",
    "pop_other", "pop_two_plus", "pop_hispanic", "pop_white_nh", "vap_total",
    "housing_units", "housing_occupied", "housing_vacant", "group_quarters_pop",
]
BLOCK_MEANS = ["pct_white_nh", "pct_black", "pct_hispanic", "pct_vacant",
               "pop_density"]


def build_blocks_cmd():
    out = f"{ROOT}/catalog/blocks/blocks.pmtiles"
    cmd = [TT, "tiles", f"{ROOT}/catalog/blocks/state_fips=*/*.parquet", out,
           "--band", "0-9:a5", "--band", "10-14:geom",
           "--layer-name", "blocks"]
    for c in BLOCK_SUMS:
        cmd += ["--accumulate-attribute", f"{c}:sum"]
    for c in BLOCK_MEANS:
        cmd += ["--accumulate-attribute", f"{c}:mean"]
    cmd += ["--spill-dir", SPILL, "-f", "-v"]
    return cmd, out


def recipes():
    """id -> a zero-argument builder returning (cmd, output path)."""
    out = {}
    for group, cid, sums, a5, geom in ACS_CHUNKS:
        out[cid] = (lambda g=group, c=cid, s=sums, a=a5, m=geom:
                    build_acs_cmd(g, c, s, a, m))
    for cid, band, cap in GEOM_ONLY:
        out[cid] = (lambda c=cid, b=band, p=cap: build_geom_cmd(c, b, p))
    out["blocks"] = build_blocks_cmd
    return out


def run_job(cid, cmd, out):
    t0 = time.time()
    with open(f"{LOGDIR}/{cid}.log", "w") as f:
        f.write("CMD: " + " ".join(cmd) + "\n\n")
        f.flush()
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    return cid, r.returncode, time.time() - t0, out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("collections", nargs="*", help="collection ids to build")
    ap.add_argument("--all", action="store_true", help="build every archive")
    ap.add_argument("--list", action="store_true",
                    help="list the recipes and exit")
    ap.add_argument("--print", dest="show", metavar="ID", action="append",
                    help="print a recipe's command line and exit")
    ap.add_argument("-j", "--jobs", type=int, default=3,
                    help="archives to build at once (default 3)")
    args = ap.parse_args()
    rec = recipes()

    if args.list:
        for cid in rec:
            print(cid)
        return 0
    if args.show:
        for cid in args.show:
            cmd, _ = rec[cid]()
            print(" ".join(cmd))
        return 0

    want = list(rec) if args.all else args.collections
    if not want:
        ap.error("name at least one collection, or --all / --list")
    if unknown := [c for c in want if c not in rec]:
        ap.error(f"unknown collections: {unknown}")

    jobs = [(cid, *rec[cid]()) for cid in want]
    print(f"Running {len(jobs)} job(s), {args.jobs} at a time")
    results = []
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(run_job, c, cmd, out): c for c, cmd, out in jobs}
        for fut in as_completed(futs):
            cid, rc, elapsed, out = fut.result()
            print(f"DONE {cid}: rc={rc} elapsed={elapsed:.1f}s")
            results.append((cid, rc, elapsed, out))
    print("\n=== SUMMARY ===")
    for cid, rc, elapsed, out in sorted(results):
        print(f"{cid}: rc={rc} time={elapsed:.1f}s out={out}")
    return 1 if any(rc for _, rc, _, _ in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
