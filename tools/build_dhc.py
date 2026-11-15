#!/usr/bin/env python3
"""Build the curated 2020 Census DHC subset: age/sex (P12), household type
and composition (P16, P17) and tenure (H1, H4), at block-groups and tracts.

See docs/spec-dhc.md for the brief and docs/runbook.md for the shared
build traps. This reuses the PL machinery's shape (tools/build_blocks.py):
per-state zip, Latin-1 pipe-delimited geoheader and segment files joined on
LOGRECNO, GEOCODE trusted for the GEOID. The DHC file is a much wider
family (44 segments, ~300 tables); only the five tables above are read.

DISK: the national DHC source is ~15 GB compressed and several times
larger extracted. This runs strictly one state at a time: download,
extract, pull the few fields this build needs into a small per-state
parquet (a few hundred KB), then delete the zip and the extract before the
next state. Only the small per-state parquets persist in
staging/dhc-build/ between states.

Usage:
  python3 tools/build_dhc.py --states                # download+parse, all states
  python3 tools/build_dhc.py --states 10 44           # just Delaware, Rhode Island
  python3 tools/build_dhc.py --assemble               # build the 6 published files
  python3 tools/build_dhc.py --all                    # states, then assemble
  python3 tools/build_dhc.py --validate               # checks only, on what exists

Spec correction (see docs/dhc-build-notes.md): the spec names P16 and P18
for "household type". P18 is GROUP QUARTERS POPULATION BY SEX BY AGE BY
MAJOR GROUP QUARTERS TYPE — institutionalized/noninstitutionalized counts,
not household composition. P17, HOUSEHOLD TYPE (INCLUDING LIVING ALONE) BY
RELATIONSHIP, is the table that actually carries household composition
(relationship to householder: spouse, child, parent, sibling, roommate).
This build reads P16 + P17, not P16 + P18.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "staging" / "dhc-cache"
SCRATCH = ROOT / "staging" / "dhc-scratch"
BUILD = ROOT / "staging" / "dhc-build"
GEO = ROOT / "staging" / "geo"
CATALOG = ROOT / "catalog"
REPORT = ROOT / "staging" / "dhc-build-report.json"
MIN_FREE_GB = 8

GPIO = shutil.which("gpio") or "gpio"

DHC_BASE = ("https://www2.census.gov/programs-surveys/decennial/2020/data/"
            "demographic-and-housing-characteristics-file")

# fips, usps, lowercase-ab (PL/DHC file prefix), FTP directory name.
# 50 states + DC + PR -- the same set tools/build_blocks.py covers. The
# other four territories (AS, GU, MP, VI) run a separate Island Areas
# census program and have no DHC state file.
STATES = [
    ("01", "AL", "al", "Alabama"), ("02", "AK", "ak", "Alaska"),
    ("04", "AZ", "az", "Arizona"), ("05", "AR", "ar", "Arkansas"),
    ("06", "CA", "ca", "California"), ("08", "CO", "co", "Colorado"),
    ("09", "CT", "ct", "Connecticut"), ("10", "DE", "de", "Delaware"),
    ("11", "DC", "dc", "District_of_Columbia"),
    ("12", "FL", "fl", "Florida"), ("13", "GA", "ga", "Georgia"),
    ("15", "HI", "hi", "Hawaii"), ("16", "ID", "id", "Idaho"),
    ("17", "IL", "il", "Illinois"), ("18", "IN", "in", "Indiana"),
    ("19", "IA", "ia", "Iowa"), ("20", "KS", "ks", "Kansas"),
    ("21", "KY", "ky", "Kentucky"), ("22", "LA", "la", "Louisiana"),
    ("23", "ME", "me", "Maine"), ("24", "MD", "md", "Maryland"),
    ("25", "MA", "ma", "Massachusetts"), ("26", "MI", "mi", "Michigan"),
    ("27", "MN", "mn", "Minnesota"), ("28", "MS", "ms", "Mississippi"),
    ("29", "MO", "mo", "Missouri"), ("30", "MT", "mt", "Montana"),
    ("31", "NE", "ne", "Nebraska"), ("32", "NV", "nv", "Nevada"),
    ("33", "NH", "nh", "New_Hampshire"), ("34", "NJ", "nj", "New_Jersey"),
    ("35", "NM", "nm", "New_Mexico"), ("36", "NY", "ny", "New_York"),
    ("37", "NC", "nc", "North_Carolina"), ("38", "ND", "nd", "North_Dakota"),
    ("39", "OH", "oh", "Ohio"), ("40", "OK", "ok", "Oklahoma"),
    ("41", "OR", "or", "Oregon"), ("42", "PA", "pa", "Pennsylvania"),
    ("44", "RI", "ri", "Rhode_Island"), ("45", "SC", "sc", "South_Carolina"),
    ("46", "SD", "sd", "South_Dakota"), ("47", "TN", "tn", "Tennessee"),
    ("48", "TX", "tx", "Texas"), ("49", "UT", "ut", "Utah"),
    ("50", "VT", "vt", "Vermont"), ("51", "VA", "va", "Virginia"),
    ("53", "WA", "wa", "Washington"), ("54", "WV", "wv", "West_Virginia"),
    ("55", "WI", "wi", "Wisconsin"), ("56", "WY", "wy", "Wyoming"),
    ("72", "PR", "pr", "Puerto_Rico"),
]

# Field counts pinning the layout: a segment that does not match is not the
# file this script knows how to read. Measured against Delaware's 2020 DHC
# zip and cross-checked against the derived positions below (both agree).
NFIELDS = {"geo": 97, "seg1": 239, "seg6": 247, "seg13": 255, "seg14": 216}

GEO_SUMLEV, GEO_GEOCOMP, GEO_LOGRECNO, GEO_GEOCODE = 2, 4, 7, 9
GEO_STATE, GEO_COUNTY, GEO_PLACE, GEO_TRACT, GEO_BLKGRP = 12, 14, 29, 32, 33
SEG_LOGRECNO = 4

LEVELS = {"bg": "150", "tract": "140"}

# --------------------------------------------------------------------------
# Column layout, derived from the 2020-dhc-table-matrix.xlsx "DHC
# Table_Segments" sheet (TABLE_ID, SEGMENT_NUMBER, TOTAL_RECORDS,
# TABLE_SORT_ORDER) and verified against the field counts above. See
# docs/dhc-build-notes.md for the full derivation and the field-count
# cross-check against the real Delaware files.
#
# H1 (segment 1, sort order 1 of 1 field): total housing units.
H1_START = 5
# H4 (segment 1, sort order 4, after H1(1)+H2(4)+H3(3) = 8 preceding
# fields): tenure of occupied housing units.
H4_START = 13
H4_COLS = ["owned_with_mortgage", "owned_free_clear", "renter_occupied"]
# P12 (segment 6, sort order 3): sex by age for selected age categories.
P12_START = 149
AGE_BINS = ["under5", "age5_9", "age10_14", "age15_17", "age18_19", "age20",
           "age21", "age22_24", "age25_29", "age30_34", "age35_39",
           "age40_44", "age45_49", "age50_54", "age55_59", "age60_61",
           "age62_64", "age65_66", "age67_69", "age70_74", "age75_79",
           "age80_84", "age85_plus"]
P12_COLS = (["male_total"] + [f"male_{b}" for b in AGE_BINS]
           + ["female_total"] + [f"female_{b}" for b in AGE_BINS])
assert len(P12_COLS) == 48  # + the P12 total itself = 49 cells
# P16 (segment 13, sort order 13): household type.
P16_START = 228
P16_COLS = ["family_households", "married_couple_family", "other_family",
           "other_family_male_no_spouse", "other_family_female_no_spouse",
           "nonfamily_households", "living_alone", "not_living_alone"]
assert len(P16_COLS) == 8  # + the P16 total itself = 9 cells
# P17 (segment 14, sort order 21): household type (incl. living alone) by
# relationship to householder.
P17_START = 185
P17_COLS = [
    "in_households", "householder_total", "householder_male",
    "male_living_alone", "male_not_living_alone", "householder_female",
    "female_living_alone", "female_not_living_alone", "spouse_opposite_sex",
    "spouse_same_sex", "partner_opposite_sex", "partner_same_sex",
    "biological_child", "biological_child_under18", "adopted_child",
    "adopted_child_under18", "stepchild", "stepchild_under18", "grandchild",
    "grandchild_under18", "sibling", "parent", "parent_in_law",
    "child_in_law", "other_relatives", "foster_child", "other_nonrelatives",
    "in_group_quarters", "institutionalized", "noninstitutionalized",
]
assert len(P17_COLS) == 30  # + the P17 total (= total_population) = 31

ALL_RAW_COLS = (
    ["total_housing_units"] + H4_COLS
    + ["total_population"] + P12_COLS
    + ["total_households"] + P16_COLS
    + ["total_population_p17"] + P17_COLS
)


def run(cmd, **kw):
    cmd = [str(c) for c in cmd]
    proc = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\n"
            f"stdout: {proc.stdout[-1500:]}\nstderr: {proc.stderr[-2500:]}")
    return proc.stdout


def duckdb_sql(sql, json_out=False):
    fmt = ["-json"] if json_out else ["-noheader", "-list"]
    out = run(["duckdb", *fmt, "-c", sql])
    return json.loads(out) if json_out else out


def free_gb(path=ROOT):
    usage = shutil.disk_usage(path)
    return usage.free / 1e9


def columns_struct(n):
    return "{" + ", ".join(f"'f{i}': 'VARCHAR'" for i in range(n)) + "}"


def read_seg(path, n):
    """Pipe-delimited DHC file, Latin-1 (geoheader carries non-ASCII place
    names), no quoting (unquoted pipe-delimited files)."""
    return (f"read_csv('{path}', delim='|', header=false, quote='', "
            f"escape='', encoding='latin-1', columns={columns_struct(n)})")


def check_field_counts(paths):
    for kind, path in paths.items():
        with open(path, encoding="latin-1") as fh:
            n = len(fh.readline().rstrip("\n").split("|"))
        if n != NFIELDS[kind]:
            raise RuntimeError(
                f"{path.name}: {n} fields, expected {NFIELDS[kind]}. The "
                "DHC layout this script pins does not match this file.")


def build_state(fips, usps, ab, dirname, keep_scratch=False):
    """Download, extract, pull bg+tract rows for the 5 target tables into
    staging/dhc-build/<fips>-bg.parquet and <fips>-tract.parquet. Deletes
    the zip and the extract before returning."""
    t0 = time.time()
    CACHE.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    zip_path = CACHE / f"{ab}2020.dhc.zip"
    url = f"{DHC_BASE}/{dirname}/{ab}2020.dhc.zip"

    work = SCRATCH / f"build-{fips}"
    try:
        if not zip_path.exists():
            run(["curl", "-fsSL", "--retry", "3", "--retry-delay", "10",
                "-o", f"{zip_path}.part", url])
            Path(f"{zip_path}.part").rename(zip_path)

        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
        run(["unzip", "-o", "-q", zip_path, "-d", work])

        paths = {
            "geo": work / f"{ab}geo2020.dhc",
            "seg1": work / f"{ab}000012020.dhc",
            "seg6": work / f"{ab}000062020.dhc",
            "seg13": work / f"{ab}000132020.dhc",
            "seg14": work / f"{ab}000142020.dhc",
        }
        for kind, p in paths.items():
            if not p.exists():
                raise FileNotFoundError(f"{kind} missing after unzip: {p}")
        check_field_counts(paths)

        g = lambda i: f"g.f{i}"          # noqa: E731
        s = lambda t, i: f"{t}.f{i}"     # noqa: E731

        def seg_select(alias, start, names, total_name):
            cols = [f"{s(alias, start)}::BIGINT AS {total_name}"]
            cols += [f"{s(alias, start + 1 + k)}::BIGINT AS {name}"
                    for k, name in enumerate(names)]
            return ", ".join(cols)

        select_h1 = f"{s('s1', H1_START)}::BIGINT AS total_housing_units"
        select_h4 = seg_select("s1", H4_START, H4_COLS, "occupied_total")
        select_p12 = seg_select("s6", P12_START, P12_COLS, "total_population")
        select_p16 = seg_select("s13", P16_START, P16_COLS,
                                "total_households")
        select_p17 = seg_select("s14", P17_START, P17_COLS,
                                "total_population_p17")

        for level, sumlev in LEVELS.items():
            out_path = BUILD / f"{fips}-{level}.parquet"
            sql = f"""
            COPY (
              SELECT
                {g(GEO_GEOCODE)}                              AS geoid,
                '{usps}'                                      AS state,
                {select_h1}, {select_h4},
                {select_p12}, {select_p16}, {select_p17}
              FROM {read_seg(paths['geo'], NFIELDS['geo'])} g
              JOIN {read_seg(paths['seg1'], NFIELDS['seg1'])} s1
                ON {s('s1', SEG_LOGRECNO)} = {g(GEO_LOGRECNO)}
              JOIN {read_seg(paths['seg6'], NFIELDS['seg6'])} s6
                ON {s('s6', SEG_LOGRECNO)} = {g(GEO_LOGRECNO)}
              JOIN {read_seg(paths['seg13'], NFIELDS['seg13'])} s13
                ON {s('s13', SEG_LOGRECNO)} = {g(GEO_LOGRECNO)}
              JOIN {read_seg(paths['seg14'], NFIELDS['seg14'])} s14
                ON {s('s14', SEG_LOGRECNO)} = {g(GEO_LOGRECNO)}
              WHERE {g(GEO_SUMLEV)} = '{sumlev}' AND {g(GEO_GEOCOMP)} = '00'
            ) TO '{out_path}' (FORMAT PARQUET, COMPRESSION ZSTD)
            """
            duckdb_sql(sql)

        rows = {}
        for level in LEVELS:
            rows[level] = int(duckdb_sql(
                f"SELECT count(*) FROM read_parquet("
                f"'{BUILD / f'{fips}-{level}.parquet'}')").strip())
        return {"fips": fips, "state": usps, "rows": rows,
                "seconds": round(time.time() - t0, 1)}
    finally:
        if not keep_scratch:
            shutil.rmtree(work, ignore_errors=True)
        zip_path.unlink(missing_ok=True)


# --------------------------------------------------------------------------
# Assembly: national parquet per (level, theme), joined to boundary geometry
# --------------------------------------------------------------------------

GEO_PARQUET = {"bg": GEO / "cb_2024_us_bg_4326.parquet",
              "tract": GEO / "cb_2024_us_tract_4326.parquet"}
GROUP_OF_LEVEL = {"bg": "block-groups", "tract": "tracts"}
PREFIX_OF_LEVEL = {"bg": "bg", "tract": "tract"}


def theme_select(level, theme):
    """(columns, from-expr) for one theme at one level, summed across any
    per-state partials with the same geoid (a no-op for bg/tract, which
    never split across states; kept for symmetry with how a national ZCTA
    would need summing if this build ever adds that level)."""
    glob = str(BUILD / f"*-{level}.parquet")
    # Connecticut: the 2020 Census (this file included, same as P.L.
    # 94-171) carries Connecticut's old 8-county GEOID prefixes. The 2024
    # cartographic boundary files this build joins to carry the 9 planning
    # regions that replaced them in 2022. The tract's 6-digit number (and,
    # for block groups, its trailing block-group digit) is preserved
    # across the change, so crosswalk on that -- the same fix
    # tools/build_tile_staging.py applies to blocks -- rather than drop a
    # state's worth of Connecticut rows as unjoinable.
    trailing = 6 if level == "tract" else 7
    geo_path = GEO_PARQUET[level]
    base = (
        f"(WITH raw AS (SELECT * FROM read_parquet('{glob}')), "
        f"ct_xwalk AS ("
        f"  SELECT b.old_geoid, c.GEOID AS new_geoid"
        f"  FROM (SELECT DISTINCT geoid AS old_geoid FROM raw"
        f"        WHERE substr(geoid,1,2)='09') b"
        f"  LEFT JOIN read_parquet('{geo_path}') c"
        f"    ON substr(c.GEOID,1,2)='09'"
        f"   AND right(c.GEOID,{trailing}) = right(b.old_geoid,{trailing})"
        f"  QUALIFY row_number() OVER ("
        f"    PARTITION BY b.old_geoid ORDER BY c.GEOID) = 1"
        f"), canon AS ("
        f"  SELECT CASE WHEN substr(raw.geoid,1,2)='09'"
        f"              THEN coalesce(x.new_geoid, raw.geoid)"
        f"              ELSE raw.geoid END AS geoid,"
        f"         raw.* EXCLUDE (geoid)"
        f"  FROM raw LEFT JOIN ct_xwalk x ON x.old_geoid = raw.geoid"
        f") SELECT geoid, any_value(state) AS state, "
        f"{{sums}} FROM canon GROUP BY geoid)")
    if theme == "age":
        cols = ["total_population"] + P12_COLS
    elif theme == "household":
        cols = (["total_households"] + P16_COLS
               + ["total_population_p17"] + P17_COLS)
    elif theme == "tenure":
        cols = ["total_housing_units", "occupied_total"] + H4_COLS
    else:
        raise ValueError(theme)
    # CAST to BIGINT: DuckDB's SUM(BIGINT) is HUGEINT, which Parquet has no
    # native physical type for, so an uncast sum round-trips as DOUBLE --
    # fine numerically at these magnitudes, but wrong for a 100% count.
    sums = ", ".join(f"sum({c})::BIGINT AS {c}" for c in cols)
    return cols, base.format(sums=sums)


def assemble_one(level, theme, con):
    cols, src = theme_select(level, theme)
    cid = f"{PREFIX_OF_LEVEL[level]}-{theme}-dec2020"
    group = GROUP_OF_LEVEL[level]
    out_dir = CATALOG / group / cid
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{cid}.parquet"
    tmp = BUILD / f"{cid}.tmp.parquet"

    derived = []
    if theme == "age":
        under18 = " + ".join(f"{s}_{b}" for s in ("male", "female")
                             for b in ("under5", "age5_9", "age10_14",
                                      "age15_17"))
        plus65 = " + ".join(f"{s}_{b}" for s in ("male", "female")
                            for b in ("age65_66", "age67_69", "age70_74",
                                     "age75_79", "age80_84", "age85_plus"))
        derived = [
            f"CASE WHEN t.total_population > 0 THEN round(100.0 * "
            f"({under18}) / t.total_population, 2) END AS pct_under18",
            f"CASE WHEN t.total_population > 0 THEN round(100.0 * "
            f"({plus65}) / t.total_population, 2) END AS pct_65plus",
        ]
    elif theme == "household":
        derived = [
            "CASE WHEN t.total_households > 0 THEN round(100.0 * "
            "t.family_households / t.total_households, 2) END "
            "AS pct_family_households",
            "CASE WHEN t.total_households > 0 THEN round(100.0 * "
            "t.living_alone / t.total_households, 2) END "
            "AS pct_living_alone",
        ]
    elif theme == "tenure":
        derived = [
            "CASE WHEN t.occupied_total > 0 THEN round(100.0 * "
            "(t.owned_with_mortgage + t.owned_free_clear) / "
            "t.occupied_total, 2) END AS pct_owned",
            "CASE WHEN t.occupied_total > 0 THEN round(100.0 * "
            "t.renter_occupied / t.occupied_total, 2) END AS pct_rented",
            "CASE WHEN t.total_housing_units > 0 THEN round(100.0 * "
            "(t.total_housing_units - t.occupied_total) / "
            "t.total_housing_units, 2) END AS pct_vacant_2020",
        ]

    name_expr = {
        "bg": "concat_ws(', ', g.NAMELSAD, tt.NAMELSAD, c.NAMELSAD, "
              "c.STATE_NAME)",
        "tract": "concat_ws(', ', g.NAMELSAD, g.NAMELSADCO, g.STATE_NAME)",
    }[level]
    extra_join = ""
    if level == "bg":
        extra_join = (
            f"LEFT JOIN read_parquet('{GEO_PARQUET['tract']}') tt "
            f"ON tt.GEOID = substr(g.GEOID, 1, 11) "
            f"LEFT JOIN read_parquet('{ROOT / 'staging' / 'geo' / 'cb_2024_us_county_4326.parquet'}') c "
            f"ON c.GEOID = substr(g.GEOID, 1, 5)")

    select_cols = ", ".join(f"t.{c}" for c in cols)
    sql = f"""
        INSTALL spatial; LOAD spatial;
        COPY (
          SELECT g.GEOID AS geoid,
                 {name_expr} AS name,
                 t.state,
                 round(g.ALAND / 1e6, 3) AS aland_sqkm,
                 {select_cols},
                 {', '.join(derived) if derived else 'NULL AS _unused'},
                 g.geometry
          FROM read_parquet('{GEO_PARQUET[level]}') g
          {extra_join}
          LEFT JOIN {src} t ON t.geoid = g.GEOID
        ) TO '{tmp}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 20000)
    """
    con.execute(sql)
    if not derived:
        # drop the placeholder column with DuckDB rather than leaving a
        # NULL _unused column in the published file
        con.execute(f"COPY (SELECT * EXCLUDE (_unused) FROM "
                    f"read_parquet('{tmp}')) TO '{tmp}' "
                    f"(FORMAT PARQUET, COMPRESSION ZSTD)")

    run([GPIO, "convert", "geoparquet", tmp, out])
    sorted_tmp = BUILD / f"{cid}.hilbert.parquet"
    run([GPIO, "sort", "hilbert", out, sorted_tmp])
    sorted_tmp.replace(out)
    restore_stats(out)
    tmp.unlink(missing_ok=True)

    n = int(duckdb_sql(f"SELECT count(*) FROM read_parquet('{out}')"))
    return {"id": cid, "rows": n, "bytes": out.stat().st_size,
            "path": str(out.relative_to(ROOT))}


def restore_stats(path):
    import pyarrow.parquet as pq
    t = pq.read_table(path)
    pq.write_table(t, path, compression="zstd", row_group_size=20000,
                   write_statistics=True)


def connect():
    import duckdb
    return duckdb.connect()


THEMES = ["age", "household", "tenure"]


def stage_assemble(only=None):
    con = connect()
    report = {}
    try:
        for level in LEVELS:
            for theme in THEMES:
                cid = f"{PREFIX_OF_LEVEL[level]}-{theme}-dec2020"
                if only and cid not in only:
                    continue
                r = assemble_one(level, theme, con)
                report[r["id"]] = r
                print(f"  {r['id']:28s} {r['rows']:>7,} rows  "
                     f"{r['bytes'] / 1e6:>7.2f} MB  {r['path']}")
    finally:
        con.close()
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--states", nargs="*", metavar="FIPS",
                    help="download+parse these state FIPS (default: all)")
    ap.add_argument("--assemble", nargs="*", metavar="ID",
                    help="build the published collections (default: all 6)")
    ap.add_argument("--all", action="store_true",
                    help="--states (all), then --assemble (all)")
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()

    if args.all:
        args.states, args.assemble = [], []

    if args.states is not None:
        wanted = set(args.states)
        todo = [s for s in STATES if not wanted or s[0] in wanted]
        results, failures = [], []
        for fips, usps, ab, dirname in todo:
            free = free_gb()
            if free < MIN_FREE_GB:
                print(f"STOP: {free:.1f} GB free, below the {MIN_FREE_GB} "
                     f"GB floor. Processed {len(results)}/{len(todo)} "
                     f"states before stopping.")
                break
            try:
                r = build_state(fips, usps, ab, dirname)
            except Exception as exc:  # noqa: BLE001
                failures.append((fips, usps, str(exc)))
                print(f"FAIL {usps} ({fips}): {exc}", flush=True)
            else:
                results.append(r)
                print(f"ok   {usps} ({fips}): bg={r['rows']['bg']:>6,} "
                     f"tract={r['rows']['tract']:>6,}  {r['seconds']:>5.1f}s "
                     f"  {free_gb():.1f} GB free", flush=True)
        REPORT.write_text(json.dumps(
            {"per_state": results, "failures": failures}, indent=2))
        if failures:
            print(f"\n{len(failures)} state(s) failed: "
                 f"{[f[1] for f in failures]}")

    if args.assemble is not None or args.all:
        only = set(args.assemble) if args.assemble else None
        print("\n=== assembling published collections ===")
        stage_assemble(only)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
