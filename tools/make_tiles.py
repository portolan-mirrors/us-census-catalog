#!/usr/bin/env python3
"""Build every PMTiles archive with tylertoo (A5 cells at coarse zooms).

Consolidated from the tiling run of 2026-11-12 (see staging/tiles-logs/
for the per-archive logs and exact command lines of that run). Three
parts, originally separate driver scripts, are concatenated below:
recipe definitions, the ACS/counties/states runner, and the blocks run.

Usage: python3 tools/make_tiles.py          # everything
See docs/design.md for the band design and QC findings (coarsest geom
zooms in dense metros ride the 500K merge valve; counties uses a 2M cap).
"""
#!/usr/bin/env python3
"""Shared recipe definitions for the ACS + counties/states tylertoo builds."""
import duckdb

ROOT = "/Users/cholmes/repos/us-census-catalog"
TT = "/Users/cholmes/repos/tylertoo/target/release/tylertoo"

SKIP_ALWAYS = {"geoid", "name", "state", "geometry", "bbox"}

# (group, id, sum_cols) for the 9 themed ACS chunks
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
]


def classify(path, sum_cols):
    cols = [r[0] for r in duckdb.sql(f"DESCRIBE SELECT * FROM read_parquet('{path}')").fetchall()]
    moe = [c for c in cols if c.endswith("_moe")]
    cv = [c for c in cols if c.endswith("_cv")]
    data_cols = [c for c in cols if c not in SKIP_ALWAYS and not c.endswith("_moe")]
    mean_cols = [c for c in data_cols if c not in sum_cols and c not in cv and
                 (c.startswith("pct_") or c.startswith("median_") or c in ("per_capita_income", "pop_density"))]
    return moe, list(sum_cols), mean_cols, cv


def build_acs_cmd(group, cid, sum_cols, a5_band, geom_band, extra_pivot_shift=0):
    path = f"{ROOT}/catalog/{group}/{cid}/{cid}.parquet"
    out = f"{ROOT}/catalog/{group}/{cid}/{cid}.pmtiles"
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
    cmd += ["--spill-dir", f"{ROOT}/staging/tiles-tmp", "-f"]
    return cmd, out


if __name__ == "__main__":
    for group, cid, sum_cols, a5_band, geom_band in ACS_CHUNKS:
        path = f"{ROOT}/catalog/{group}/{cid}/{cid}.parquet"
        cmd, out = build_acs_cmd(group, cid, sum_cols, a5_band, geom_band)
        print(cid, "->", " ".join(cmd))


# ===== runner (ACS/counties/states) =====
#!/usr/bin/env python3
import subprocess, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
# (recipes definitions are inlined above in this consolidated file)

LOGDIR = f"{ROOT}/staging/tiles-logs"

jobs = []
for group, cid, sum_cols, a5_band, geom_band in ACS_CHUNKS:
    if cid == "bg-income":
        continue  # already built + QC'd separately
    cmd, out = build_acs_cmd(group, cid, sum_cols, a5_band, geom_band)
    jobs.append((cid, cmd, out))

# also counties (with raised cap) and states (default cap)
import duckdb
TT = "/Users/cholmes/repos/tylertoo/target/release/tylertoo"

def moe_cols(path):
    cols = [r[0] for r in duckdb.sql(f"DESCRIBE SELECT * FROM read_parquet('{path}')").fetchall()]
    return [c for c in cols if c.endswith("_moe")]

counties_path = f"{ROOT}/catalog/counties/counties.parquet"
counties_out = f"{ROOT}/catalog/counties/counties.pmtiles"
cmd = [TT, "tiles", counties_path, counties_out, "--band", "0-10:geom", "--max-compressed-tile-size", "2M"]
for c in moe_cols(counties_path):
    cmd += ["--exclude-property", c]
cmd += ["--spill-dir", f"{ROOT}/staging/tiles-tmp", "-f"]
jobs.append(("counties", cmd, counties_out))

states_path = f"{ROOT}/catalog/states/states.parquet"
states_out = f"{ROOT}/catalog/states/states.pmtiles"
cmd = [TT, "tiles", states_path, states_out, "--band", "0-8:geom"]
for c in moe_cols(states_path):
    cmd += ["--exclude-property", c]
cmd += ["--spill-dir", f"{ROOT}/staging/tiles-tmp", "-f"]
jobs.append(("states", cmd, states_out))

print(f"Running {len(jobs)} jobs, 3 at a time")
for cid, cmd, out in jobs:
    print(cid, len(cmd), "args")

def run_job(cid, cmd, out):
    log_path = f"{LOGDIR}/{cid}.log"
    t0 = time.time()
    with open(log_path, "w") as f:
        f.write("CMD: " + " ".join(cmd) + "\n\n")
        f.flush()
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    elapsed = time.time() - t0
    return cid, r.returncode, elapsed, out

results = []
with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(run_job, cid, cmd, out): cid for cid, cmd, out in jobs}
    for fut in as_completed(futs):
        cid, rc, elapsed, out = fut.result()
        print(f"DONE {cid}: rc={rc} elapsed={elapsed:.1f}s")
        results.append((cid, rc, elapsed, out))

print("\n=== SUMMARY ===")
for cid, rc, elapsed, out in results:
    print(f"{cid}: rc={rc} time={elapsed:.1f}s out={out}")


# ===== blocks =====
#!/usr/bin/env python3
import subprocess, time, os

TT = "/Users/cholmes/repos/tylertoo/target/release/tylertoo"
ROOT = "/Users/cholmes/repos/us-census-catalog"

SUM_COLS = [
    "pop_total", "pop_white", "pop_black", "pop_aian", "pop_asian", "pop_nhpi",
    "pop_other", "pop_two_plus", "pop_hispanic", "pop_white_nh", "vap_total",
    "housing_units", "housing_occupied", "housing_vacant", "group_quarters_pop",
]
MEAN_COLS = ["pct_white_nh", "pct_black", "pct_hispanic", "pct_vacant", "pop_density"]

INPUT = f"{ROOT}/catalog/blocks/state_fips=*/*.parquet"
OUT = f"{ROOT}/catalog/blocks/blocks.pmtiles"
LOG = f"{ROOT}/staging/tiles-logs/blocks.log"

cmd = [TT, "tiles", INPUT, OUT,
       "--band", "0-9:a5", "--band", "10-14:geom",
       "--layer-name", "blocks"]
for c in SUM_COLS:
    cmd += ["--accumulate-attribute", f"{c}:sum"]
for c in MEAN_COLS:
    cmd += ["--accumulate-attribute", f"{c}:mean"]
cmd += ["--spill-dir", f"{ROOT}/staging/tiles-tmp", "-f", "-v"]

print(" ".join(cmd))

if __name__ == "__main__":
    import sys
    if "--run" in sys.argv:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        t0 = time.time()
        with open(LOG, "w") as f:
            f.write("CMD: " + " ".join(cmd) + "\n\n")
            f.flush()
            r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
        elapsed = time.time() - t0
        print(f"blocks build rc={r.returncode} elapsed={elapsed:.1f}s")
