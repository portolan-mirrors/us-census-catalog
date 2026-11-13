#!/usr/bin/env python3
"""Build the staging/agg/ inputs that tools/make_tiles.py's pyramid bands
read at coarse zooms, instead of A5 cell aggregation.

    python3 tools/build_tile_staging.py            # everything
    python3 tools/build_tile_staging.py --acs      # just the 5 county-pruned
                                                     # ACS theme files
    python3 tools/build_tile_staging.py --blocks   # just the blocks
                                                     # county/tract aggregates

Two kinds of output, both scratch (staging/ is gitignored) and both rebuilt
from the catalog's own published parquet files — nothing here touches
anything under catalog/ until make_tiles.py runs:

ACS theme county files
    staging/agg/<theme>-county.parquet for theme in {income, people,
    housing, connectivity, wellbeing}. Each is catalog/counties/
    counties.parquet, column-pruned to EXACTLY the matching bg-<theme> (or,
    for wellbeing, tract-wellbeing) parquet's column list. These are the
    Census Bureau's own county-level ACS estimates, not a client-side
    rollup of block groups or tracts — strictly better data, and it is what
    makes one style file render identically at every zoom, since every
    column name the style references is already the right name at the
    county level.

    zctas and places need no staging file: their column list is identical
    to counties.parquet's (verified at build time), so their county band in
    make_tiles.py points straight at catalog/counties/counties.parquet.

blocks county/tract aggregates
    staging/agg/blocks-county.parquet and staging/agg/blocks-tract.parquet.
    Built by summing the 2020 Decennial block counts
    (catalog/blocks/state_fips=*/*.parquet) grouped by the county (5-char)
    or tract (11-char) GEOID prefix, recomputing the rate columns from the
    summed counts (not averaging the per-block rates), and joining polygon
    geometry from the cached Census cartographic-boundary parquets in
    staging/geo/ (regenerate with `python3 tools/build_acs.py --stage
    geometry` if that directory is empty).

    Connecticut wrinkle: 2020 Census block GEOIDs carry Connecticut's old
    8-county prefixes (09001-09015), but TIGER/CB 2024 switched to the 9
    planning regions (09110-09190) that replaced them as the county
    equivalent in 2022. A tract's 6-digit tract number is preserved across
    the change, so this script crosswalks Connecticut's blocks onto the
    current county-equivalent prefix by matching that suffix against the CB
    2024 tract file before grouping, rather than dropping ~3.6M people's
    worth of Connecticut blocks as unjoinable. Every other state's GEOIDs
    match the CB files directly.

    A handful of GEOIDs nationwide (large-water or otherwise unpopulated
    placeholder tracts) have no match in the CB files at all; they are
    dropped from the aggregate. All of them have pop_total = 0, so the
    nationwide population total is unaffected — this script's
    ``--validate`` check (on by default) asserts the county and tract
    aggregates both sum to 334,735,155, the published national block total.
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/cholmes/repos/us-census-catalog")
AGG = ROOT / "staging" / "agg"
GEO = ROOT / "staging" / "geo"
CATALOG = ROOT / "catalog"
EXPECTED_BLOCK_POP = 334_735_155

THEMES = ["income", "people", "housing", "connectivity", "wellbeing"]
# theme -> the finest-grain parquet whose column list the county file must
# match exactly. income/people/housing/connectivity have the bg- and tract-
# level tables with identical schemas (checked column-for-column at build
# time); wellbeing exists only at tract level.
SCHEMA_SOURCE = {
    "income": CATALOG / "block-groups" / "bg-income" / "bg-income.parquet",
    "people": CATALOG / "block-groups" / "bg-people" / "bg-people.parquet",
    "housing": CATALOG / "block-groups" / "bg-housing" / "bg-housing.parquet",
    "connectivity": CATALOG / "block-groups" / "bg-connectivity"
    / "bg-connectivity.parquet",
    "wellbeing": CATALOG / "tracts" / "tract-wellbeing"
    / "tract-wellbeing.parquet",
}

COUNTIES = CATALOG / "counties" / "counties.parquet"
BLOCKS_GLOB = str(CATALOG / "blocks" / "state_fips=*" / "*.parquet")
CB_COUNTY = GEO / "cb_2024_us_county_4326.parquet"
CB_TRACT = GEO / "cb_2024_us_tract_4326.parquet"

BLOCK_SUM_COLS = [
    "pop_total", "pop_white", "pop_black", "pop_aian", "pop_asian",
    "pop_nhpi", "pop_other", "pop_two_plus", "pop_hispanic", "pop_white_nh",
    "vap_total", "housing_units", "housing_occupied", "housing_vacant",
    "group_quarters_pop",
]


def run_sql(sql: str):
    """Run a SQL script against duckdb with the spatial extension loaded."""
    proc = subprocess.run(
        ["duckdb", "-c", "INSTALL spatial; LOAD spatial;\n" + sql],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"duckdb failed:\n{proc.stdout}\n{proc.stderr}")
    print(proc.stdout.strip())


def columns(path) -> list[str]:
    proc = subprocess.run(
        ["duckdb", "-csv", "-c", f"DESCRIBE SELECT * FROM read_parquet('{path}')"],
        capture_output=True, text=True, check=True,
    )
    return [line.split(",")[0] for line in proc.stdout.splitlines()[1:]]


def build_acs_county_files():
    """staging/agg/<theme>-county.parquet, column-pruned from counties.parquet."""
    AGG.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        schema_path = SCHEMA_SOURCE[theme]
        cols = columns(schema_path)
        missing = [c for c in cols if c not in columns(COUNTIES)]
        if missing:
            sys.exit(f"{theme}: counties.parquet is missing columns "
                      f"{schema_path} has: {missing}")
        out = AGG / f"{theme}-county.parquet"
        col_list = ", ".join(cols)
        run_sql(f"""
            COPY (SELECT {col_list} FROM read_parquet('{COUNTIES}'))
            TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD);
            SELECT '{theme}-county' AS file, count(*) AS rows
            FROM read_parquet('{out}');
        """)


def build_blocks_aggregates(validate: bool = True):
    """staging/agg/blocks-county.parquet and blocks-tract.parquet."""
    AGG.mkdir(parents=True, exist_ok=True)
    for p in (CB_COUNTY, CB_TRACT):
        if not p.exists():
            sys.exit(f"missing {p} — run "
                      "`python3 tools/build_acs.py --stage geometry` first")

    sum_exprs = ",\n    ".join(f"sum(a.{c}) AS {c}" for c in BLOCK_SUM_COLS)
    rate_exprs = """
    CASE WHEN sum(a.pop_total) > 0
         THEN round(100.0 * sum(a.pop_white_nh) / sum(a.pop_total), 2) END
                                                      AS pct_white_nh,
    CASE WHEN sum(a.pop_total) > 0
         THEN round(100.0 * sum(a.pop_black) / sum(a.pop_total), 2) END
                                                      AS pct_black,
    CASE WHEN sum(a.pop_total) > 0
         THEN round(100.0 * sum(a.pop_hispanic) / sum(a.pop_total), 2) END
                                                      AS pct_hispanic,
    CASE WHEN sum(a.housing_units) > 0
         THEN round(100.0 * sum(a.housing_vacant) / sum(a.housing_units), 2) END
                                                      AS pct_vacant,
    round(sum(a.aland_sqkm), 3)                      AS aland_sqkm,
    CASE WHEN sum(a.aland_sqkm) > 0
         THEN round(sum(a.pop_total) / sum(a.aland_sqkm), 1) END
                                                      AS pop_density"""

    def band(geoid_expr, group_table, out_path):
        return f"""
        COPY (
          SELECT
            g.GEOID AS geoid,
            any_value(a.state) AS state,
            {sum_exprs},
            {rate_exprs},
            ST_AsWKB(g.geometry) AS geometry,
            {{'xmin': ST_XMin(g.geometry), 'ymin': ST_YMin(g.geometry),
              'xmax': ST_XMax(g.geometry), 'ymax': ST_YMax(g.geometry)}} AS bbox
          FROM {group_table} a
          JOIN read_parquet('{{cb}}') g ON g.GEOID = {geoid_expr}
          GROUP BY g.GEOID, g.geometry
        ) TO '{out_path}' (FORMAT PARQUET, COMPRESSION ZSTD);
        """

    sql = f"""
    CREATE TEMP TABLE blk AS
    SELECT * FROM read_parquet('{BLOCKS_GLOB}', hive_partitioning=true);

    -- Connecticut: 2020 block GEOIDs carry the old 8-county prefixes; CB
    -- 2024 geometry carries the 9 planning regions that replaced them in
    -- 2022. The 6-digit tract number is preserved, so crosswalk on that.
    CREATE TEMP TABLE ct_xwalk AS
    SELECT b.old_tract, c.GEOID AS new_tract
    FROM (SELECT DISTINCT substr(geoid,1,11) AS old_tract FROM blk
          WHERE substr(geoid,1,2)='09') b
    LEFT JOIN read_parquet('{CB_TRACT}') c
      ON substr(c.GEOID,1,2)='09' AND right(c.GEOID,6) = right(b.old_tract,6)
    QUALIFY row_number() OVER (PARTITION BY b.old_tract ORDER BY c.GEOID) = 1;

    CREATE TEMP TABLE blk2 AS
    SELECT
      blk.*,
      CASE WHEN substr(geoid,1,2)='09'
           THEN coalesce(x.new_tract, substr(geoid,1,11))
           ELSE substr(geoid,1,11) END AS canon_tract
    FROM blk
    LEFT JOIN ct_xwalk x ON x.old_tract = substr(blk.geoid,1,11);

    {band("substr(a.canon_tract,1,5)", "blk2", AGG / "blocks-county.parquet").replace("{cb}", str(CB_COUNTY))}
    {band("a.canon_tract", "blk2", AGG / "blocks-tract.parquet").replace("{cb}", str(CB_TRACT))}

    SELECT 'county' AS level, count(*) AS rows, sum(pop_total) AS pop_total
    FROM read_parquet('{AGG / "blocks-county.parquet"}')
    UNION ALL
    SELECT 'tract', count(*), sum(pop_total)
    FROM read_parquet('{AGG / "blocks-tract.parquet"}');
    """
    run_sql(sql)

    if validate:
        for level, path in (("county", AGG / "blocks-county.parquet"),
                             ("tract", AGG / "blocks-tract.parquet")):
            proc = subprocess.run(
                ["duckdb", "-csv", "-noheader", "-c",
                 f"SELECT sum(pop_total) FROM read_parquet('{path}')"],
                capture_output=True, text=True, check=True,
            )
            total = float(proc.stdout.strip())
            if total != EXPECTED_BLOCK_POP:
                sys.exit(f"{level} aggregate pop_total {total:,.0f} != "
                          f"{EXPECTED_BLOCK_POP:,}")
            print(f"  {level} aggregate validated: {total:,.0f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--acs", action="store_true",
                    help="only the 5 ACS theme county files")
    ap.add_argument("--blocks", action="store_true",
                    help="only the blocks county/tract aggregates")
    ap.add_argument("--no-validate", action="store_true",
                    help="skip the blocks population-total check")
    args = ap.parse_args()

    do_acs = args.acs or not (args.acs or args.blocks)
    do_blocks = args.blocks or not (args.acs or args.blocks)

    if do_acs:
        print("== ACS theme county files ==")
        build_acs_county_files()
    if do_blocks:
        print("== blocks county/tract aggregates ==")
        build_blocks_aggregates(validate=not args.no_validate)


if __name__ == "__main__":
    main()
