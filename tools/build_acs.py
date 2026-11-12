#!/usr/bin/env python3
"""Build the national ACS collections from the table-based Summary File.

Inputs (already in staging/census-cache/, see tools/download_sources.sh):
  acsdt5y2024-<table>.dat      one row per geography, GEO_ID + E###/M###
  ACS20245YR_Table_Shells.txt  line number -> label, for the pins
  cb_2024_us_{bg,tract,county,state}_500k.zip   2024 cartographic boundaries

Outputs: catalog/<group>/<id>/<id>.parquet for the nine themed block-group
and tract collections, plus catalog/counties/counties.parquet and
catalog/states/states.parquet.

Three stages, each resumable on its own:

  extract   One pass per .dat file. A table's columns all read their
            numerator and denominator from that same table, so one pass
            emits finished columns for all four summary levels at once —
            the 200 MB B01001 file is read once, not four times. Output is
            staging/acs-build/<table>.<level>.csv.
  geometry  unzip + ogr2ogr each national cartographic boundary shapefile
            to EPSG:4326 GeoParquet. ogr2ogr, not DuckDB ST_Transform:
            DuckDB computes the right coordinates but stamps the source
            CRS into the GeoParquet metadata.
  assemble  DuckDB joins the per-table CSVs onto the geometry (geometry
            drives the join, so a geography with boundaries but no ACS data
            keeps its row with NULL values), then gpio normalizes to
            spec-conformant GeoParquet: zstd, covering bbox with
            statistics, Hilbert row order.

Usage:
  python3 tools/build_acs.py                      # everything
  python3 tools/build_acs.py --stage extract      # one stage
  python3 tools/build_acs.py bg-income states     # some collections
  python3 tools/build_acs.py --validate           # checks only
"""

import argparse
import csv
import json
import subprocess
import sys
import zipfile
from math import sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from specs import (ACS_RELEASE, BUILD, CACHE, COLLECTIONS, CONTEXT_SPEC,
                   JAM, LEVELS, ROOT, STATE_USPS, Z90, check_all_shells,
                   out_columns, resolve_lines, tables)

CATALOG = ROOT / "catalog"
GEO = ROOT / "staging" / "geo"

STL_PUBLISHED = ("https://data.source.coop/tge-labs/st-louis-open-data-"
                 "mirror/demographics/acs-block-groups/acs-block-groups"
                 ".parquet")

# Attributes kept off each boundary file: the join key, the name parts the
# `name` column is built from, and ALAND for aland_sqkm / pop_density.
GEO_FIELDS = {
    "bg": ["GEOID", "NAMELSAD", "ALAND"],
    "tract": ["GEOID", "NAMELSAD", "NAMELSADCO", "STATE_NAME", "ALAND"],
    "county": ["GEOID", "NAMELSAD", "STATE_NAME", "ALAND"],
    "state": ["GEOID", "NAME", "ALAND"],
}


def run(cmd: list, **kw) -> subprocess.CompletedProcess:
    proc = subprocess.run([str(c) for c in cmd], capture_output=True,
                          text=True, **kw)
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(str(c) for c in cmd)}\n"
                           f"{proc.stdout[-500:]}\n{proc.stderr[-2000:]}")
    return proc


# --------------------------------------------------------------------------
# Stage 1: the ACS summary file
# --------------------------------------------------------------------------

def moe_sum(moes: list) -> float | None:
    """Margins of error for a sum add in quadrature (ACS Accuracy of the
    Data). Jammed components are already None and drop out."""
    known = [m for m in moes if m is not None]
    if not known:
        return None
    return sqrt(sum(m * m for m in known))


def pct_moe(num: float, num_moe: float | None, den: float,
            den_moe: float | None) -> float | None:
    """Census proportion formula, falling back to the ratio formula when
    the radicand goes negative (the numerator is not a subset, or sampling
    error makes it look that way)."""
    if num_moe is None or den_moe is None or den == 0:
        return None
    p = num / den
    radicand = num_moe ** 2 - p * p * den_moe ** 2
    if radicand < 0:
        radicand = num_moe ** 2 + p * p * den_moe ** 2
    return 100 * sqrt(radicand) / den


def dat_path(table: str) -> Path:
    return CACHE / f"acsdt5y{ACS_RELEASE[:4]}-{table.lower()}.dat"


def col_types(spec: list) -> dict[str, str]:
    """DuckDB types for a per-table CSV. Explicit, because a column that is
    all-NULL in the sample (median household income for a small race group
    at tract level, say) would otherwise be sniffed as VARCHAR."""
    types = {"geoid": "VARCHAR"}
    for s in spec:
        types[s.name] = "BIGINT" if s.kind == "count" else "DOUBLE"
        types[f"{s.name}_moe"] = "DOUBLE"
        if s.cv:
            types[f"{s.name}_cv"] = "DOUBLE"
    return types


def extract_table(table: str, spec: list) -> dict[str, int]:
    """One .dat file -> one CSV of finished columns per summary level.

    Jam values (anything at or below -111111111, which covers the
    -555555555 "controlled, no sampling error" MOE) become NULL, never
    numbers.
    """
    path = dat_path(table)
    if not path.exists():
        raise RuntimeError(f"missing source: {path}")

    # Which lines this table's columns need, and the resolved line groups.
    resolved = {}
    needed = set()
    for s in spec:
        if s.kind == "complement":
            continue
        lines = resolve_lines(s.lines, s.table)
        resolved[s.name] = lines
        needed.update(lines)
        if s.den:
            _, plus, minus = s.den
            needed.update(plus)
            needed.update(minus)

    columns = out_columns(spec)
    prefixes = {p: lvl for lvl, p in LEVELS.items()}
    files, writers = {}, {}
    counts = {lvl: 0 for lvl in LEVELS}
    BUILD.mkdir(parents=True, exist_ok=True)
    for lvl in LEVELS:
        f = open(BUILD / f"{table}.{lvl}.csv", "w", newline="",
                 encoding="utf-8")
        files[lvl] = f
        w = csv.writer(f)
        w.writerow(["geoid"] + columns)
        writers[lvl] = w

    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("|")
        idx = {}
        for i, name in enumerate(header):
            if name == "GEO_ID":
                continue
            idx[name.split("_", 1)[1]] = i  # B19013_E001 -> "E001"
        for line in needed:
            for kind in ("E", "M"):
                if f"{kind}{line:03d}" not in idx:
                    raise RuntimeError(f"{table}: no {kind}{line:03d} column "
                                       f"in {path.name}")

        def cell(row, kind, line):
            raw = row[idx[f"{kind}{line:03d}"]]
            if not raw or raw == ".":
                return None
            v = float(raw)
            return None if v <= JAM else v

        for line in f:
            lvl = prefixes.get(line[:9])
            if lvl is None:
                continue
            row = line.rstrip("\n").split("|")
            geoid = row[0].split("US", 1)[1]
            out = []
            vals: dict[str, float | None] = {}
            for s in spec:
                if s.kind == "complement":
                    v = vals[s.source]
                    out += [None if v is None else round(100 - v, 2),
                            vals[f"{s.source}_moe"]]
                    continue
                ests = [cell(row, "E", n) for n in resolved[s.name]]
                if all(e is None for e in ests):
                    est = moe = None
                else:
                    est = sum(e for e in ests if e is not None)
                    moe = moe_sum([cell(row, "M", n)
                                   for n in resolved[s.name]])
                if s.kind in ("count", "median"):
                    if s.kind == "count" and est is not None:
                        est = int(est)
                elif s.kind == "pct":
                    _, plus, minus = s.den
                    dplus = [cell(row, "E", n) for n in plus]
                    dminus = [cell(row, "E", n) for n in minus]
                    if est is None or any(v is None for v in dplus):
                        est = moe = None
                    else:
                        den = (sum(dplus)
                               - sum(v for v in dminus if v is not None))
                        if den <= 0:
                            est = moe = None
                        else:
                            dmoe = moe_sum([cell(row, "M", n)
                                            for n in plus + minus])
                            m = pct_moe(est, moe, den, dmoe)
                            est = round(100 * est / den, 2)
                            moe = None if m is None else round(m, 2)
                vals[s.name], vals[f"{s.name}_moe"] = est, moe
                out += [est, moe]
                if s.cv:
                    # cv = (moe / 1.645) / estimate — the ACS reliability
                    # convention. A zero or NULL estimate has no cv.
                    out.append(None if not est or moe is None
                               else round((moe / Z90) / est, 3))
            writers[lvl].writerow(["" if v is None else v
                                   for v in [geoid] + out])
            counts[lvl] += 1

    for f in files.values():
        f.close()
    return counts


def stage_extract(only_tables: set[str] | None = None) -> dict:
    by_table = tables()
    report = {}
    for table, spec in by_table.items():
        if only_tables and table not in only_tables:
            continue
        counts = extract_table(table, spec)
        report[table] = counts
        print(f"  {table:9s} " + "  ".join(f"{k}={v}"
                                           for k, v in counts.items()))
    return report


# --------------------------------------------------------------------------
# Stage 2: cartographic boundaries
# --------------------------------------------------------------------------

def geo_parquet(level: str) -> Path:
    """National cartographic boundary shapefile -> EPSG:4326 GeoParquet."""
    out = GEO / f"cb_2024_us_{level}_4326.parquet"
    if out.exists():
        return out
    GEO.mkdir(parents=True, exist_ok=True)
    zip_path = CACHE / f"cb_2024_us_{level}_500k.zip"
    shp_dir = GEO / f"cb_2024_us_{level}_500k"
    if not shp_dir.exists():
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(shp_dir)
    shp = next(shp_dir.glob("*.shp"))
    run(["ogr2ogr", "-f", "Parquet", out, shp,
         "-t_srs", "EPSG:4326",
         "-select", ",".join(GEO_FIELDS[level]),
         "-lco", "COMPRESSION=ZSTD", "-lco", "GEOMETRY_NAME=geometry"])
    return out


def stage_geometry() -> dict:
    report = {}
    for level in LEVELS:
        p = geo_parquet(level)
        n = duckdb_scalar(f"SELECT count(*) FROM read_parquet('{p}')")
        report[level] = n
        print(f"  {level:7s} {n:>7,} features  {p.name}")
    return report


# --------------------------------------------------------------------------
# Stage 3: assembly
# --------------------------------------------------------------------------

def connect():
    import duckdb
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    return con


def duckdb_scalar(sql: str):
    con = connect()
    try:
        return con.execute(sql).fetchone()[0]
    finally:
        con.close()


def usps_csv() -> Path:
    """The embedded STATEFP -> USPS lookup, as a file DuckDB can join."""
    BUILD.mkdir(parents=True, exist_ok=True)
    p = BUILD / "statefp_usps.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["statefp", "usps"])
        w.writerows(sorted(STATE_USPS.items()))
    return p


def csv_source(table: str, level: str, spec: list) -> str:
    path = BUILD / f"{table}.{level}.csv"
    if not path.exists():
        raise RuntimeError(f"missing extract: {path} (run --stage extract)")
    types = json.dumps(col_types(spec)).replace('"', "'")
    return f"read_csv('{path}', header=true, nullstr='', types={types})"


def name_expr(level: str) -> str:
    """Human-readable name from the boundary attributes.

    The 2024 block-group file carries only NAMELSAD ("Block Group 2"), so
    the tract and county files supply the rest of the name; concat_ws drops
    a part that is missing rather than leaving a dangling comma.
    """
    return {
        "bg": "concat_ws(', ', g.NAMELSAD, t.NAMELSAD, c.NAMELSAD, "
              "c.STATE_NAME)",
        "tract": "concat_ws(', ', g.NAMELSAD, g.NAMELSADCO, g.STATE_NAME)",
        "county": "concat_ws(', ', g.NAMELSAD, g.STATE_NAME)",
        "state": "g.NAME",
    }[level]


def assemble(coll, con) -> dict:
    level = coll.level
    out_dir = CATALOG / coll.group / coll.id if coll.group else CATALOG / coll.id
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{coll.id}.parquet"
    tmp = BUILD / f"{coll.id}.duckdb.parquet"

    by_table = tables()
    ctx_table = CONTEXT_SPEC[0].table
    # One CSV per table, joined on geoid; alias_of maps a table to its alias
    # so each column selects from the CSV it was computed in.
    alias_of = {ctx_table: "ctx"}
    joins = [f"LEFT JOIN {csv_source(ctx_table, level, by_table[ctx_table])} "
             f"ctx ON ctx.geoid = g.GEOID"]
    for table in dict.fromkeys(s.table for s in coll.spec):
        if table in alias_of:
            continue
        alias = f"t{len(alias_of)}"
        alias_of[table] = alias
        joins.append(f"LEFT JOIN {csv_source(table, level, by_table[table])} "
                     f"{alias} ON {alias}.geoid = g.GEOID")
    selects = [f"{alias_of[s.table]}.{col}"
               for s in coll.spec for col in out_columns([s])]

    if level == "bg":
        extra = (f"LEFT JOIN read_parquet('{geo_parquet('tract')}') t "
                 f"ON t.GEOID = substr(g.GEOID, 1, 11) "
                 f"LEFT JOIN read_parquet('{geo_parquet('county')}') c "
                 f"ON c.GEOID = substr(g.GEOID, 1, 5) ")
    else:
        extra = ""

    sql = f"""
        COPY (
            SELECT g.GEOID AS geoid,
                   {name_expr(level)} AS name,
                   u.usps AS state,
                   ctx.population, ctx.population_moe,
                   round(g.ALAND / 1e6, 3) AS aland_sqkm,
                   CASE WHEN g.ALAND = 0 OR ctx.population IS NULL
                        THEN NULL
                        ELSE round(ctx.population / (g.ALAND / 1e6), 1)
                   END AS pop_density,
                   {', '.join(selects)},
                   g.geometry
            FROM read_parquet('{geo_parquet(level)}') g
            {extra}
            LEFT JOIN read_csv('{usps_csv()}', header=true) u
                   ON u.statefp = substr(g.GEOID, 1, 2)
            {' '.join(joins)}
        ) TO '{tmp}' (FORMAT PARQUET, COMPRESSION ZSTD,
                      ROW_GROUP_SIZE 20000)
    """
    con.execute(sql)

    # gpio normalization: covering bbox + statistics, Hilbert order, zstd —
    # the same conversion the St. Louis catalog passes validation with.
    run(["gpio", "convert", "geoparquet", tmp, out])
    sorted_tmp = BUILD / f"{coll.id}.hilbert.parquet"
    run(["gpio", "sort", "hilbert", out, sorted_tmp])
    sorted_tmp.replace(out)
    restore_stats(out)
    tmp.unlink(missing_ok=True)

    n = duckdb_scalar(f"SELECT count(*) FROM read_parquet('{out}')")
    size = out.stat().st_size
    print(f"  {coll.id:20s} {n:>7,} rows  {size / 1e6:>8.1f} MB  "
          f"{out.relative_to(ROOT)}")
    return {"rows": n, "bytes": size, "path": str(out.relative_to(ROOT))}


def restore_stats(path: Path) -> None:
    """Rewrite with pyarrow so every row group carries min/max statistics
    (GDAL and gpio can drop them on the bbox covering column); the `geo`
    schema metadata and the Hilbert row order are preserved."""
    import pyarrow.parquet as pq
    t = pq.read_table(path)
    pq.write_table(t, path, compression="zstd", row_group_size=20000,
                   write_statistics=True)


def stage_assemble(only: set[str] | None) -> dict:
    con = connect()
    report = {}
    try:
        for coll in COLLECTIONS:
            if only and coll.id not in only:
                continue
            report[coll.id] = assemble(coll, con)
    finally:
        con.close()
    return report


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def validate(only: set[str] | None = None) -> int:
    con = connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    problems = []
    print("\n== row counts, uniqueness, pct range ==")
    for coll in COLLECTIONS:
        if only and coll.id not in only:
            continue
        out_dir = (CATALOG / coll.group / coll.id if coll.group
                   else CATALOG / coll.id)
        path = out_dir / f"{coll.id}.parquet"
        if not path.exists():
            problems.append(f"{coll.id}: not built")
            continue
        n, distinct = con.execute(
            f"SELECT count(*), count(DISTINCT geoid) "
            f"FROM read_parquet('{path}')").fetchone()
        pct_cols = [c for c in out_columns(coll.spec)
                    if c.startswith("pct_") and not c.endswith(("_moe", "_cv"))]
        bad = 0
        if pct_cols:
            cond = " OR ".join(f"{c} < 0 OR {c} > 100" for c in pct_cols)
            bad = con.execute(f"SELECT count(*) FROM read_parquet('{path}') "
                              f"WHERE {cond}").fetchone()[0]
        flag = "ok" if (n == distinct and bad == 0) else "PROBLEM"
        print(f"  {coll.id:20s} {n:>7,} rows  {distinct:>7,} distinct geoid  "
              f"{bad} out-of-range pct  [{flag}]")
        if n != distinct:
            problems.append(f"{coll.id}: {n - distinct} duplicate geoids")
        if bad:
            problems.append(f"{coll.id}: {bad} rows with a pct outside 0-100")

    print("\n== state medians (sanity: 55k-120k across the 50 states + DC) ==")
    states = CATALOG / "states" / "states.parquet"
    if states.exists():
        # Puerto Rico is a US state equivalent in the ACS but its median
        # household income is a third of the mainland's, so the sanity band
        # covers the 50 states and DC and PR is reported on its own.
        lo, hi, n_null = con.execute(
            f"SELECT min(median_hh_income), max(median_hh_income), "
            f"count(*) FILTER (WHERE median_hh_income IS NULL) "
            f"FROM read_parquet('{states}') WHERE state NOT IN "
            f"('AS','GU','MP','VI','PR')").fetchone()
        print(f"  median_hh_income across the 50 states + DC: {lo:,.0f} - "
              f"{hi:,.0f}  ({n_null} NULL)")
        if not (55000 <= lo and hi <= 120000):
            problems.append(f"state median_hh_income out of range: {lo}-{hi}")
        rows = con.execute(
            f"SELECT state, name, median_hh_income, population "
            f"FROM read_parquet('{states}') "
            f"WHERE state IN ('MS','MD','DC','PR','AS','GU') "
            f"ORDER BY state").fetchall()
        for s, nm, v, pop in rows:
            print(f"    {s} {nm:22s} income="
                  f"{'NULL' if v is None else f'{v:>9,.0f}'}  pop="
                  f"{'NULL' if pop is None else f'{pop:>11,}'}")

    print("\n== St. Louis cross-check against the published catalog ==")
    bg_income = CATALOG / "block-groups" / "bg-income" / "bg-income.parquet"
    if bg_income.exists():
        q = f"""
        WITH mine AS (
            SELECT geoid, median_hh_income, median_hh_income_moe,
                   pct_below_poverty, pct_below_poverty_moe
            FROM read_parquet('{bg_income}')
            WHERE substr(geoid, 1, 5) = '29510'
        ), theirs AS (
            SELECT geoid, median_hh_income, median_hh_income_moe,
                   pct_below_poverty, pct_below_poverty_moe
            FROM read_parquet('{STL_PUBLISHED}')
        )
        SELECT count(*) AS joined,
               (SELECT count(*) FROM mine) AS mine_n,
               (SELECT count(*) FROM theirs) AS theirs_n,
               count(*) FILTER (
                   WHERE m.median_hh_income IS DISTINCT FROM
                         t.median_hh_income) AS income_diff,
               count(*) FILTER (
                   WHERE m.median_hh_income_moe IS DISTINCT FROM
                         t.median_hh_income_moe) AS income_moe_diff,
               count(*) FILTER (
                   WHERE m.pct_below_poverty IS DISTINCT FROM
                         t.pct_below_poverty) AS pov_diff,
               count(*) FILTER (
                   WHERE m.pct_below_poverty_moe IS DISTINCT FROM
                         t.pct_below_poverty_moe) AS pov_moe_diff
        FROM mine m JOIN theirs t USING (geoid)
        """
        r = con.execute(q).fetchone()
        joined, mine_n, theirs_n, *diffs = r
        print(f"  {mine_n} St. Louis block groups here, {theirs_n} published, "
              f"{joined} joined")
        for label, d in zip(["median_hh_income", "median_hh_income_moe",
                             "pct_below_poverty", "pct_below_poverty_moe"],
                            diffs):
            print(f"    {label:24s} {d} mismatches")
            if d:
                problems.append(f"St. Louis cross-check: {d} {label} "
                                f"mismatches")
        if joined != theirs_n:
            problems.append(f"St. Louis cross-check: joined {joined} of "
                            f"{theirs_n} published block groups")

    print("\n== NULL rates ==")
    for coll in COLLECTIONS:
        if only and coll.id not in only:
            continue
        out_dir = (CATALOG / coll.group / coll.id if coll.group
                   else CATALOG / coll.id)
        path = out_dir / f"{coll.id}.parquet"
        if not path.exists():
            continue
        cols = (["population", "pop_density"]
                + [c for c in out_columns(coll.spec)
                   if not c.endswith(("_moe", "_cv"))])
        sel = ", ".join(f"100.0 * count(*) FILTER (WHERE {c} IS NULL) "
                        f"/ count(*) AS {c}" for c in cols)
        row = con.execute(f"SELECT {sel} FROM read_parquet('{path}')"
                          ).fetchone()
        print(f"  {coll.id}")
        for c, v in zip(cols, row):
            print(f"    {c:28s} {v:6.2f}% NULL")

    print("\n== GeoParquet metadata ==")
    for cid, path in (("bg-income", bg_income),
                      ("states", states)):
        if not path.exists():
            continue
        import pyarrow.parquet as pq
        meta = pq.read_schema(path).metadata or {}
        geo = json.loads(meta[b"geo"]) if b"geo" in meta else None
        if geo is None:
            problems.append(f"{cid}: no `geo` schema metadata")
            continue
        g = geo["columns"][geo["primary_column"]]
        print(f"  {cid}: GeoParquet {geo['version']}, "
              f"crs={'default/OGC:CRS84' if not g.get('crs') else 'set'}, "
              f"covering={'yes' if 'covering' in g else 'no'}, "
              f"types={g.get('geometry_types')}")
        if "covering" not in g:
            problems.append(f"{cid}: no covering bbox in `geo` metadata")

    con.close()
    print()
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(f"  ! {p}")
        return 1
    print("all checks passed")
    return 0


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("collections", nargs="*",
                    help="collection ids (default: all)")
    ap.add_argument("--stage", choices=["extract", "geometry", "assemble"],
                    action="append")
    ap.add_argument("--validate", action="store_true",
                    help="run the checks only")
    args = ap.parse_args()
    only = set(args.collections) or None
    if only:
        known = {c.id for c in COLLECTIONS}
        if unknown := only - known:
            raise SystemExit(f"unknown collections: {sorted(unknown)}")

    if args.validate:
        return validate(only)

    stages = set(args.stage or ["extract", "geometry", "assemble"])

    print("== table shells: verifying pinned line numbers ==")
    pins = check_all_shells()
    print(f"  {len(pins)} pins verified against "
          f"ACS{ACS_RELEASE}_Table_Shells.txt, 4 derived line groups "
          f"resolved")

    if "extract" in stages:
        print("== extract: one pass per ACS table ==")
        want = None
        if only:
            want = {s.table for c in COLLECTIONS if c.id in only
                    for s in c.spec} | {s.table for s in CONTEXT_SPEC}
        stage_extract(want)
    if "geometry" in stages:
        print("== geometry: cartographic boundaries -> EPSG:4326 ==")
        stage_geometry()
    if "assemble" in stages:
        print("== assemble: DuckDB join + gpio GeoParquet ==")
        stage_assemble(only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
