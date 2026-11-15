#!/usr/bin/env python3
"""Column-prune each wide level's GeoParquet into its five themed children.

The 2026-11-15 restructure makes every coarse-or-sparse level a group with
five themed child collections mirroring the tract set, plus the original
wide table as a sixth child (tools/specs.py COLLECTIONS is the contract).
The themed tables are not a new extraction: every value in them is already
published in the level's wide table, so this script column-prunes that file
instead of re-running tools/build_acs.py.

    catalog/counties/counties.parquet  (112 cols, 3,235 rows, hilbert order)
      -> catalog/counties/county-income/county-income.parquet       (23 cols)
      -> catalog/counties/county-people/county-people.parquet       (29 cols)
      ...

What is kept, and why that needs no judgement call:

  theme columns   specs.out_columns(<THEME>_SPEC) — the estimate, its _moe
                  and, where the spec says so, its _cv, exactly the list the
                  matching tract-<theme> table publishes.
  context columns the wide table's columns that belong to NO theme spec:
                  geoid, name, state, population, population_moe,
                  aland_sqkm, pop_density, geometry, bbox. Derived by
                  subtracting out_columns(ALL_SPEC) from the wide schema
                  rather than listed here, so a column added to a theme
                  spec moves out of context automatically instead of being
                  published twice.

Both orders are the wide table's own: columns come out in wide-schema order
(which is spec order, so a themed file's schema is column-for-column the
matching tract-<theme> file's), and rows are copied in file order, which is
the Hilbert order gpio sorted the wide table into. Nothing is re-sorted.

Written with pyarrow — `pq.write_table(compression="zstd",
row_group_size=20000, write_statistics=True)` — which is the last step of
tools/build_acs.py's write path (`restore_stats`), and the `geo` schema
metadata is carried over from the wide file verbatim. That is exact rather
than lazy: pruning columns drops no rows, so the GeoParquet 1.1.0 block's
primary_column, WKB encoding, bbox covering, file bbox and geometry_types
all still describe the output. gpio is not re-run because `gpio convert`
would recompute metadata that is already correct and `gpio sort hilbert`
would re-sort rows this script is required to leave alone.

Usage:
  python3 tools/build_wide_themes.py --list          # targets, no work
  python3 tools/build_wide_themes.py county-income   # build those
  python3 tools/build_wide_themes.py --all           # all 25
  python3 tools/build_wide_themes.py --all --qc-only # re-run QC, no write

QC on every file written (and on --qc-only): row count equals the wide
table's, the geoid sequence is identical row for row, the schema matches
the matching tract-<theme> table's theme columns, every theme column
matches the wide table value for value over all rows, and three named
(geoid, column, value) spot checks per file are read back out of both files
with DuckDB and printed. Report JSON goes to
staging/tiles-logs/wide-themes.qc.json.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import duckdb
import pyarrow.parquet as pq

import specs

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
LOGDIR = ROOT / "staging" / "tiles-logs"

# theme name -> the spec list, for the suffix on each themed collection id
# (county-income -> income). The wide tables carry ALL_SPEC and are skipped.
THEME_SPECS = {
    "income": specs.INCOME_SPEC,
    "people": specs.PEOPLE_SPEC,
    "housing": specs.HOUSING_SPEC,
    "connectivity": specs.CONNECTIVITY_SPEC,
    "wellbeing": specs.WELLBEING_SPEC,
}

# The one themed table per theme that already exists, used as an independent
# check that a pruned schema is column-for-column what this catalog already
# publishes for that theme.
REFERENCE = {t: CATALOG / "tracts" / f"tract-{t}" / f"tract-{t}.parquet"
             for t in THEME_SPECS}


def targets():
    """[(wide parquet, out parquet, collection, theme)] for the 25 children."""
    out = []
    for coll in specs.COLLECTIONS:
        if coll.group is None or coll.id in specs.WIDE_IDS:
            continue
        if coll.group not in specs.WIDE_IDS:
            continue  # block-groups/tracts are built by build_acs.py
        theme = coll.id.rsplit("-", 1)[1]
        if theme not in THEME_SPECS:
            sys.exit(f"✗ {coll.id}: no theme spec for suffix {theme!r}")
        if THEME_SPECS[theme] is not coll.spec:
            sys.exit(f"✗ {coll.id}: spec is not {theme.upper()}_SPEC")
        wide = CATALOG / coll.group / f"{coll.group}.parquet"
        dest = CATALOG / coll.group / coll.id / f"{coll.id}.parquet"
        out.append((wide, dest, coll, theme))
    return out


# Every column that any theme spec publishes: what is NOT in here is context.
THEMED_EVERYWHERE = set(specs.out_columns(specs.ALL_SPEC))


def plan_columns(wide_cols, theme):
    """(kept columns in wide order, context columns, theme columns)."""
    want = specs.out_columns(THEME_SPECS[theme])
    missing = [c for c in want if c not in wide_cols]
    if missing:
        sys.exit(f"✗ {theme}: the wide table is missing {missing}")
    context = [c for c in wide_cols if c not in THEMED_EVERYWHERE]
    keep = [c for c in wide_cols if c in context or c in want]
    return keep, context, want


def build(wide, dest, coll, theme):
    dest.parent.mkdir(parents=True, exist_ok=True)
    src = pq.read_table(wide)
    keep, context, want = plan_columns(src.schema.names, theme)
    t = src.select(keep)
    # Carry the wide file's `geo` block: pruning columns drops no rows, so
    # its bbox, geometry_types and covering still describe this table.
    t = t.replace_schema_metadata(src.schema.metadata)
    pq.write_table(t, dest, compression="zstd", row_group_size=20000,
                   write_statistics=True)
    return {"columns": len(keep), "context": context, "theme": want,
            "bytes": dest.stat().st_size}


# ---------------------------------------------------------------------------
# QC
# ---------------------------------------------------------------------------
def spot_checks(theme):
    """Three columns per theme to read back by name, value for value."""
    cols = specs.out_columns(THEME_SPECS[theme])
    first = [s.name for s in THEME_SPECS[theme]]
    picks = [first[0], first[len(first) // 2], f"{first[0]}_moe"]
    return [c for c in dict.fromkeys(picks) if c in cols]


def qc(wide, dest, coll, theme, con):
    out = {"id": coll.id, "wide": wide.name, "problems": []}
    bad = out["problems"].append

    wf, df = pq.ParquetFile(wide), pq.ParquetFile(dest)
    out["rows"] = df.metadata.num_rows
    out["wide_rows"] = wf.metadata.num_rows
    out["columns"] = len(df.schema_arrow.names)
    out["bytes"] = dest.stat().st_size
    out["row_groups"] = [df.metadata.row_group(i).num_rows
                         for i in range(df.metadata.num_row_groups)]
    out["compression"] = df.metadata.row_group(0).column(0).compression
    if out["rows"] != out["wide_rows"]:
        bad(f"rows {out['rows']} != wide {out['wide_rows']}")

    # GeoParquet conventions, against the wide file and the tract reference.
    geo = json.loads(df.schema_arrow.metadata[b"geo"])
    wgeo = json.loads(wf.schema_arrow.metadata[b"geo"])
    rgeo = json.loads(pq.ParquetFile(REFERENCE[theme])
                      .schema_arrow.metadata[b"geo"])
    out["geoparquet"] = geo["version"]
    if geo != wgeo:
        bad("`geo` metadata differs from the wide table's")
    if geo["version"] != rgeo["version"] or \
            set(geo["columns"]["geometry"]) != set(rgeo["columns"]["geometry"]):
        bad("`geo` block is not shaped like the tract reference's")
    if "covering" not in geo["columns"]["geometry"]:
        bad("no covering bbox")
    if out["compression"] != "ZSTD":
        bad(f"compression is {out['compression']}, not ZSTD")
    stats_ok = all(df.metadata.row_group(i).column(j).statistics is not None
                   for i in range(df.metadata.num_row_groups)
                   for j in range(df.metadata.num_columns))
    if not stats_ok:
        bad("a row-group column has no statistics")

    # Schema: the theme columns must be exactly the matching tract table's,
    # in the same order; context is the wide table's non-themed columns.
    ref_cols = pq.ParquetFile(REFERENCE[theme]).schema_arrow.names
    got = list(df.schema_arrow.names)
    if got != list(ref_cols):
        bad(f"schema differs from {REFERENCE[theme].name}: "
            f"+{[c for c in got if c not in ref_cols]} "
            f"-{[c for c in ref_cols if c not in got]}")

    # Row order: geoid sequence identical to the wide table's, row for row.
    a = pq.read_table(wide, columns=["geoid"])["geoid"].to_pylist()
    b = pq.read_table(dest, columns=["geoid"])["geoid"].to_pylist()
    out["row_order_identical"] = a == b
    if a != b:
        bad("row order differs from the wide table's")

    # Values: every theme column, every row, against the wide table.
    theme_cols = [c for c in got if c in THEMED_EVERYWHERE]
    diffs = ", ".join(
        f"count_if(w.{c} IS DISTINCT FROM d.{c}) AS d_{c}" for c in theme_cols)
    row = con.execute(f"""
        SELECT {diffs} FROM (
          SELECT *, row_number() OVER () AS rn FROM read_parquet('{wide}')) w
        JOIN (
          SELECT *, row_number() OVER () AS rn FROM read_parquet('{dest}')) d
        USING (rn)""").fetchone()
    mismatched = {c: n for c, n in zip(theme_cols, row) if n}
    out["value_mismatches"] = mismatched
    out["columns_compared"] = len(theme_cols)
    if mismatched:
        bad(f"value mismatches: {mismatched}")

    # Three named spot checks, read out of both files by geoid.
    picks = spot_checks(theme)
    sel = ", ".join(picks)
    geoids = [r[0] for r in con.execute(
        f"SELECT geoid FROM read_parquet('{dest}') WHERE "
        f"{picks[0]} IS NOT NULL ORDER BY geoid LIMIT 3").fetchall()]
    out["spot_checks"] = []
    for g in geoids:
        w = con.execute(f"SELECT {sel} FROM read_parquet('{wide}') "
                        f"WHERE geoid = '{g}'").fetchone()
        d = con.execute(f"SELECT {sel} FROM read_parquet('{dest}') "
                        f"WHERE geoid = '{g}'").fetchone()
        for col, wv, dv in zip(picks, w, d):
            out["spot_checks"].append(
                {"geoid": g, "column": col, "wide": wv, "themed": dv,
                 "equal": wv == dv})
            if wv != dv:
                bad(f"spot check {g}/{col}: {wv} != {dv}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("collections", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--qc-only", action="store_true",
                    help="QC the existing files without rewriting them")
    args = ap.parse_args()

    jobs = targets()
    if args.list:
        for wide, dest, coll, theme in jobs:
            print(f"{coll.id:22s} {theme:13s} {wide.relative_to(ROOT)} -> "
                  f"{dest.relative_to(ROOT)}")
        return 0
    if not args.all:
        want = set(args.collections)
        if not want:
            ap.error("name at least one collection, or --all / --list")
        if unknown := want - {c.id for _, _, c, _ in jobs}:
            ap.error(f"unknown collections: {sorted(unknown)}")
        jobs = [j for j in jobs if j[2].id in want]

    con = duckdb.connect()
    LOGDIR.mkdir(parents=True, exist_ok=True)
    report, failed = [], []
    for wide, dest, coll, theme in jobs:
        t0 = time.time()
        if not args.qc_only:
            build(wide, dest, coll, theme)
        r = qc(wide, dest, coll, theme, con)
        r["seconds"] = round(time.time() - t0, 1)
        report.append(r)
        flag = "✓" if not r["problems"] else "✗"
        print(f"{flag} {coll.id:22s} {r['rows']:>7,} rows  "
              f"{r['columns']:>3} cols  {r['bytes'] / 1e6:>7.1f} MB  "
              f"{r['columns_compared']} theme cols compared, "
              f"{len(r['value_mismatches'])} mismatched  {r['seconds']}s")
        for p in r["problems"]:
            print(f"    ! {p}")
            failed.append(f"{coll.id}: {p}")

    (LOGDIR / "wide-themes.qc.json").write_text(
        json.dumps({"generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "files": report}, indent=1, default=str) + "\n")
    print(f"\n{len(report)} file(s); QC report "
          f"{(LOGDIR / 'wide-themes.qc.json').relative_to(ROOT)}")
    if failed:
        print(f"{len(failed)} problem(s)")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
