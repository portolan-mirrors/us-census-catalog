#!/usr/bin/env python3
"""Build every PMTiles archive with tylertoo `pyramid` (census geography at
coarse zooms, not A5 cells).

One recipe per collection, and the recipes are the record of how each
published archive was made: the command lines below are the ones in
staging/tiles-logs/<id>.pyramid.log, byte for byte. Nothing here mutates the
catalog until a job is named on the command line, because re-tiling an
archive that is already built and QC'd costs real time and gains nothing.

Usage:
  python3 tools/make_tiles.py --list                 # recipes, no work
  python3 tools/make_tiles.py --print bg-income       # the exact command
  python3 tools/make_tiles.py zctas places           # build those two
  python3 tools/make_tiles.py --all                  # everything

Three families of recipe, all built with `tylertoo pyramid --generalize`
(every band is raw GeoParquet features, never pre-aggregated cells):

  census pyramid  The ACS themed collections (block-groups/bg-*,
                   tracts/tract-*) and the two wave-3 collections (zctas,
                   places): county polygons at national zooms, tract
                   polygons at mid zooms (bg-* only — tract-* and zctas/
                   places go straight from county to their own geometry),
                   the collection's own feature geometry at close zooms.
                   Every band carries the SAME layer name, the collection
                   id, because every style's source-layer is the collection
                   id. `*_moe` columns are excluded from every tile — those
                   margins of error were computed by the Census Bureau for
                   one specific geography and are meaningless mixed across
                   zooms with a different geography in the band below.

                     bg-<theme>      0-5  county   (staging/agg)
                                     6-7  tract    (catalog/tracts/tract-<theme>)
                                     8-13 bg       (catalog/block-groups/bg-<theme>)
                     tract-<theme>   0-5  county   (staging/agg)
                                     6-12 tract    (catalog/tracts/tract-<theme>)
                     zctas, places   0-5  county   (catalog/counties/counties.parquet)
                                     6-12 own       (catalog/<cid>/<cid>.parquet)

                   The county band for each ACS theme is NOT a client-side
                   rollup of the finer geography: it is counties.parquet's
                   own columns for that theme, column-pruned to the exact
                   schema of the theme's finest table (see
                   tools/build_tile_staging.py). Those are the Census
                   Bureau's own county-level ACS estimates — strictly
                   better than summing or averaging block groups or tracts
                   client-side. zctas and places reuse counties.parquet
                   untouched: its column list is identical to theirs
                   (verified column-for-column), and its `state` column
                   carries real values where zctas' own is NULL.

  geometry only    The coarse geographies (states, counties, congressional
                   districts): few enough features that every zoom can
                   carry the real polygons. Unchanged by this rebuild.

  themed children  Since the 2026-11-15 restructure each of the five wide
                   levels is a group with five themed children (county-*,
                   state-*, zcta-*, place-*, cd-*), built from the pruned
                   parquets tools/build_wide_themes.py writes. A child
                   reuses its LEVEL's recipe with the themed parquet and
                   the themed layer name swapped in: county-*/state-*/cd-*
                   are geometry-only like their parents, zcta-*/place-*
                   take the census pyramid with the county band read from
                   staging/agg/<theme>-county.parquet. The wide parents'
                   own archives are not rebuilt or moved.

  blocks pyramid   2020 Decennial counts, no margins of error, no CVs, its
                   own three-band split:

                     0-5  county aggregate  (staging/agg/blocks-county.parquet)
                     6-9  tract aggregate   (staging/agg/blocks-tract.parquet)
                     10-14 blocks           (catalog/blocks/state_fips=*/*.parquet,
                                             a glob band input — confirmed working)

                   The county/tract aggregates are built by
                   tools/build_tile_staging.py: summed counts, recomputed
                   rates (pct_white_nh/pct_black/pct_hispanic/pct_vacant/
                   pop_density), geometry joined from the cached CB
                   county/tract parquets in staging/geo/. Connecticut's
                   2020 block GEOIDs carry its old 8-county prefixes while
                   the CB 2024 geometry uses the 9 planning regions that
                   replaced them in 2022; build_tile_staging.py crosswalks
                   on the preserved tract-number suffix before the join, so
                   no Connecticut population is dropped.

See docs/design.md for the full band design and QC findings, and
tools/build_tile_staging.py for how staging/agg/ is produced.
"""

import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import duckdb

ROOT = "/Users/cholmes/repos/us-census-catalog"
TT = "/Users/cholmes/repos/tylertoo/target/release/tylertoo"
AGG = f"{ROOT}/staging/agg"
LOGDIR = f"{ROOT}/staging/tiles-logs"

SKIP_ALWAYS = {"geoid", "name", "state", "geometry", "bbox"}


def coll_dir(group, cid):
    return f"{ROOT}/catalog/{group}/{cid}" if group else f"{ROOT}/catalog/{cid}"


def columns(path):
    return [r[0] for r in duckdb.sql(
        f"DESCRIBE SELECT * FROM read_parquet('{path}')").fetchall()]


def moe_cols(path):
    return [c for c in columns(path) if c.endswith("_moe")]


# (group, cid, theme) for the 9 themed ACS chunks: theme names the
# staging/agg/<theme>-county.parquet band and the matching
# catalog/tracts/tract-<theme>/tract-<theme>.parquet table.
BG_CHUNKS = [
    ("block-groups", "bg-income", "income"),
    ("block-groups", "bg-people", "people"),
    ("block-groups", "bg-housing", "housing"),
    ("block-groups", "bg-connectivity", "connectivity"),
]
TRACT_CHUNKS = [
    ("tracts", "tract-income", "income"),
    ("tracts", "tract-people", "people"),
    ("tracts", "tract-housing", "housing"),
    ("tracts", "tract-connectivity", "connectivity"),
    ("tracts", "tract-wellbeing", "wellbeing"),
]
WAVE3 = ["zctas", "places"]


def build_bg_cmd(group, cid, theme):
    d = coll_dir(group, cid)
    out = f"{d}/{cid}.pmtiles"
    bg_path = f"{d}/{cid}.parquet"
    tract_path = f"{ROOT}/catalog/tracts/tract-{theme}/tract-{theme}.parquet"
    county_path = f"{AGG}/{theme}-county.parquet"
    cmd = [TT, "pyramid", out,
           "--band", f"0-5:{county_path}:{cid}",
           "--band", f"6-7:{tract_path}:{cid}",
           "--band", f"8-13:{bg_path}:{cid}",
           "--generalize"]
    for c in moe_cols(bg_path):
        cmd += ["--exclude-property", c]
    cmd += ["--report", f"{LOGDIR}/{cid}.report.json", "-f"]
    return cmd, out


def build_themed_pyramid_cmd(group, cid, theme):
    """county band + the collection's own features: tract-* and, since the
    2026-11-15 restructure, the themed zcta-*/place-* children.

    One recipe because the band plan is the same one: the Census Bureau's own
    county estimates pruned to this theme's exact schema at z0-5
    (staging/agg/<theme>-county.parquet), the collection's own polygons at
    z6-12. The command lines it emits for the five tract archives are
    unchanged, byte for byte, from staging/tiles-logs/tract-*.pyramid.log.
    """
    d = coll_dir(group, cid)
    out = f"{d}/{cid}.pmtiles"
    tract_path = f"{d}/{cid}.parquet"
    county_path = f"{AGG}/{theme}-county.parquet"
    cmd = [TT, "pyramid", out,
           "--band", f"0-5:{county_path}:{cid}",
           "--band", f"6-12:{tract_path}:{cid}",
           "--generalize"]
    for c in moe_cols(tract_path):
        cmd += ["--exclude-property", c]
    cmd += ["--report", f"{LOGDIR}/{cid}.report.json", "-f"]
    return cmd, out


def build_wave3_cmd(cid):
    d = coll_dir(None, cid)
    out = f"{d}/{cid}.pmtiles"
    own_path = f"{d}/{cid}.parquet"
    county_path = f"{ROOT}/catalog/counties/counties.parquet"
    cmd = [TT, "pyramid", out,
           "--band", f"0-5:{county_path}:{cid}",
           "--band", f"6-12:{own_path}:{cid}",
           "--generalize"]
    for c in moe_cols(own_path):
        cmd += ["--exclude-property", c]
    cmd += ["--report", f"{LOGDIR}/{cid}.report.json", "-f"]
    return cmd, out


# ===== geometry-only archives: unchanged by this rebuild =====================
# (id, band, max_compressed_tile_size) for the coarse geographies: few enough
# features that every zoom carries the real polygons. counties and
# congressional-districts carry 110 columns on a few thousand / a few hundred
# features, so a single z0 tile overruns the default compressed-tile cap;
# 2M is the counties precedent (staging/tiles-logs/counties.log). states fits
# under the default because there are 56 of them.
GEOM_ONLY = [
    ("counties", "0-10:geom", "2M"),
    ("states", "0-8:geom", None),
    ("congressional-districts", "0-10:geom", "2M"),
]

# ===== reference/ (2026-11-15): geography with no demographic columns =====
# One band, full zoom range, same `tiles` (not `pyramid`) command as
# GEOM_ONLY above -- there is no county/tract band to build on top of,
# because these collections are not keyed to a geography level. landmarks-*
# go to z14 so a single landmark is still visible at neighborhood zoom;
# urban-areas stops at z10, like counties, since an urban area is a
# city/metro-scale polygon. The 2M cap matches the counties precedent: a
# national band of a few thousand to just over a million features
# overruns the default at z0 without one.
REFERENCE_SPATIAL = [
    ("urban-areas", "0-10:geom", "2M"),
    ("landmarks-area", "0-14:geom", "2M"),
    ("landmarks-point", "0-14:geom", "2M"),
]

# ===== DHC subset (2026-11-15): block-groups/bg-*-dec2020, tracts/tract- ===
# *-dec2020. Same census pyramid as the ACS bg-*/tract-* chunks above --
# county band at z0-5, tract band at z6-7 (bg only), the collection's own
# features below that -- built once staging/agg/<theme>-county.parquet
# existed (tools/build_tile_staging.py --dhc). theme here is the DHC theme
# token (age/household/tenure), which also names the county aggregate
# file; the tract/bg parquet paths carry the "-dec2020" suffix the ACS
# chunks do not, hence separate builder functions rather than reusing
# build_bg_cmd/build_themed_pyramid_cmd directly.
DHC_BG_CHUNKS = [
    ("block-groups", "bg-age-dec2020", "age"),
    ("block-groups", "bg-household-dec2020", "household"),
    ("block-groups", "bg-tenure-dec2020", "tenure"),
]
DHC_TRACT_CHUNKS = [
    ("tracts", "tract-age-dec2020", "age"),
    ("tracts", "tract-household-dec2020", "household"),
    ("tracts", "tract-tenure-dec2020", "tenure"),
]


def build_dhc_bg_cmd(group, cid, theme):
    d = coll_dir(group, cid)
    out = f"{d}/{cid}.pmtiles"
    bg_path = f"{d}/{cid}.parquet"
    tract_cid = cid.replace("bg-", "tract-")
    tract_path = (f"{ROOT}/catalog/tracts/{tract_cid}/{tract_cid}.parquet")
    county_path = f"{AGG}/{theme}-county.parquet"
    cmd = [TT, "pyramid", out,
           "--band", f"0-5:{county_path}:{cid}",
           "--band", f"6-7:{tract_path}:{cid}",
           "--band", f"8-13:{bg_path}:{cid}",
           "--generalize"]
    for c in moe_cols(bg_path):
        cmd += ["--exclude-property", c]
    cmd += ["--report", f"{LOGDIR}/{cid}.report.json", "-f"]
    return cmd, out


def build_dhc_tract_cmd(group, cid, theme):
    d = coll_dir(group, cid)
    out = f"{d}/{cid}.pmtiles"
    tract_path = f"{d}/{cid}.parquet"
    county_path = f"{AGG}/{theme}-county.parquet"
    cmd = [TT, "pyramid", out,
           "--band", f"0-5:{county_path}:{cid}",
           "--band", f"6-12:{tract_path}:{cid}",
           "--generalize"]
    for c in moe_cols(tract_path):
        cmd += ["--exclude-property", c]
    cmd += ["--report", f"{LOGDIR}/{cid}.report.json", "-f"]
    return cmd, out


def build_geom_cmd(cid, band, max_tile, group=None):
    d = coll_dir(group, cid)
    path, out = f"{d}/{cid}.parquet", f"{d}/{cid}.pmtiles"
    cmd = [TT, "tiles", path, out, "--band", band]
    if max_tile:
        cmd += ["--max-compressed-tile-size", max_tile]
    for c in moe_cols(path):
        cmd += ["--exclude-property", c]
    cmd += ["-f"]
    return cmd, out


# ===== the themed children of the five wide levels (2026-11-15) =============
# Every wide level became a group with five themed children mirroring the
# tract set (tools/specs.py COLLECTIONS), built from the themed parquets
# tools/build_wide_themes.py prunes out of the level's wide table. A child
# carries its parent's geometry exactly, so each one reuses its LEVEL's
# existing recipe with the themed parquet and the themed layer name swapped
# in — nothing about the band plan is new, and the wide parent's own parquet
# and pmtiles are not touched.
#
#   county-*, state-*, cd-*   geometry only, the level's own band and cap:
#                             few enough features to carry real polygons at
#                             every zoom. The 2M compressed-tile cap is kept
#                             from the counties/cd recipes even though a
#                             themed child is a quarter the width — the cap
#                             is a ceiling, and keeping it means the child
#                             and the parent cannot diverge on a z0 tile.
#   zcta-*, place-*           the census pyramid, county band at z0-5 from
#                             staging/agg/<theme>-county.parquet. The wide
#                             zctas/places archives point that band at
#                             counties.parquet itself, which they can
#                             because its 112 columns are exactly their own;
#                             a themed child needs the theme's 23-34 column
#                             pruning, which is the staging file every
#                             bg-*/tract-* archive already bands on.
THEMES = ["income", "people", "housing", "connectivity", "wellbeing"]
# group -> (collection-id prefix, band, max compressed tile size)
GEOM_LEVELS = [
    ("counties", "county", "0-10:geom", "2M"),
    ("states", "state", "0-8:geom", None),
    ("congressional-districts", "cd", "0-10:geom", "2M"),
]
# group -> collection-id prefix, for the levels that need the county band
PYRAMID_LEVELS = [("zctas", "zcta"), ("places", "place")]


# ===== blocks: 2020 Decennial counts, 8.17M features, its own 3-band plan ===
def build_blocks_cmd():
    out = f"{ROOT}/catalog/blocks/blocks.pmtiles"
    county_path = f"{AGG}/blocks-county.parquet"
    tract_path = f"{AGG}/blocks-tract.parquet"
    blocks_glob = f"{ROOT}/catalog/blocks/state_fips=*/*.parquet"
    cmd = [TT, "pyramid", out,
           "--band", f"0-5:{county_path}:blocks",
           "--band", f"6-9:{tract_path}:blocks",
           "--band", f"10-14:{blocks_glob}:blocks",
           "--generalize",
           "--report", f"{LOGDIR}/blocks.report.json",
           "-f"]
    return cmd, out


def recipes():
    """id -> a zero-argument builder returning (cmd, output path)."""
    out = {}
    for group, cid, theme in BG_CHUNKS:
        out[cid] = (lambda g=group, c=cid, t=theme: build_bg_cmd(g, c, t))
    for group, cid, theme in TRACT_CHUNKS:
        out[cid] = (lambda g=group, c=cid, t=theme:
                    build_themed_pyramid_cmd(g, c, t))
    for cid in WAVE3:
        out[cid] = (lambda c=cid: build_wave3_cmd(c))
    for cid, band, cap in GEOM_ONLY:
        out[cid] = (lambda c=cid, b=band, p=cap: build_geom_cmd(c, b, p))
    for cid, band, cap in REFERENCE_SPATIAL:
        out[cid] = (lambda c=cid, b=band, p=cap:
                    build_geom_cmd(c, b, p, group="reference"))
    for group, cid, theme in DHC_BG_CHUNKS:
        out[cid] = (lambda g=group, c=cid, t=theme: build_dhc_bg_cmd(g, c, t))
    for group, cid, theme in DHC_TRACT_CHUNKS:
        out[cid] = (lambda g=group, c=cid, t=theme:
                    build_dhc_tract_cmd(g, c, t))
    for group, prefix, band, cap in GEOM_LEVELS:
        for theme in THEMES:
            cid = f"{prefix}-{theme}"
            out[cid] = (lambda g=group, c=cid, b=band, p=cap:
                        build_geom_cmd(c, b, p, group=g))
    for group, prefix in PYRAMID_LEVELS:
        for theme in THEMES:
            cid = f"{prefix}-{theme}"
            out[cid] = (lambda g=group, c=cid, t=theme:
                        build_themed_pyramid_cmd(g, c, t))
    out["blocks"] = build_blocks_cmd
    return out


def run_job(cid, cmd, out):
    t0 = time.time()
    with open(f"{LOGDIR}/{cid}.pyramid.log", "w") as f:
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
