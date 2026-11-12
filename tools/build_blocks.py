#!/usr/bin/env python3
"""Build the 2020 Decennial Census block collection: catalog/blocks/.

One GeoParquet partition per state (50 states + DC + PR), joining P.L. 94-171
redistricting counts to TIGER/Line 2024 TABBLOCK20 polygons on the 15-character
block GEOID. ~8.1 million blocks nationally.

    python3 tools/build_blocks.py                  # all states, 4 workers
    python3 tools/build_blocks.py 02 10            # just Alaska and Delaware
    python3 tools/build_blocks.py --workers 6
    python3 tools/build_blocks.py --validate-only  # re-run checks on outputs

Sources are the zips staged by tools/download_blocks.sh in
staging/blocks-cache/. Field positions for the PL segments come from the Census
Bureau's own R import scripts; see docs/blocks-build-notes.md for the citation
and the verification that pinned them.

Peak disk is bounded: each state unzips into its own scratch directory, and
that directory is removed as soon as the partition is written. TIGER unzips run
to ~1 GB for the largest states, so the scratch tree holds roughly
``workers x 2.5 GB`` at any moment.

The pipeline per state is three steps:

1. ``ogr2ogr`` converts the shapefile to EPSG:4326 Parquet. GDAL does the
   reprojection because DuckDB's ``ST_Transform`` writes CRS metadata that
   does not round-trip (the geometry is right, the stamped CRS is not).
2. DuckDB joins the four pipe-delimited PL files to that geometry and derives
   the rate and density columns. Its output is GeoParquet 1.0 with no bbox
   covering column, so it is scratch, not the partition.
3. ``gpio sort hilbert --add-bbox`` writes the partition: Hilbert row order
   (PTL-DAT-006), a bbox covering column with row-group statistics
   (PTL-DAT-007), ZSTD, and sized row groups, in one pass. It also normalizes
   the CRS the way the spec writes WGS84 lon/lat — by omitting the key.

``verify_output`` then reads the finished file back and asserts those
properties rather than trusting them, because every one of them is something a
writer upstream has been observed to drop.
"""

import argparse
import concurrent.futures
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "staging" / "blocks-cache"
SCRATCH = ROOT / "staging" / "blocks-scratch"
OUT_DIR = ROOT / "catalog" / "blocks"
REPORT = ROOT / "staging" / "blocks-build-report.json"

# fips, USPS code, PL file prefix (lowercase USPS). Matches the download list
# in tools/download_blocks.sh one for one.
STATES = [
    ("01", "AL", "al"), ("02", "AK", "ak"), ("04", "AZ", "az"),
    ("05", "AR", "ar"), ("06", "CA", "ca"), ("08", "CO", "co"),
    ("09", "CT", "ct"), ("10", "DE", "de"), ("11", "DC", "dc"),
    ("12", "FL", "fl"), ("13", "GA", "ga"), ("15", "HI", "hi"),
    ("16", "ID", "id"), ("17", "IL", "il"), ("18", "IN", "in"),
    ("19", "IA", "ia"), ("20", "KS", "ks"), ("21", "KY", "ky"),
    ("22", "LA", "la"), ("23", "ME", "me"), ("24", "MD", "md"),
    ("25", "MA", "ma"), ("26", "MI", "mi"), ("27", "MN", "mn"),
    ("28", "MS", "ms"), ("29", "MO", "mo"), ("30", "MT", "mt"),
    ("31", "NE", "ne"), ("32", "NV", "nv"), ("33", "NH", "nh"),
    ("34", "NJ", "nj"), ("35", "NM", "nm"), ("36", "NY", "ny"),
    ("37", "NC", "nc"), ("38", "ND", "nd"), ("39", "OH", "oh"),
    ("40", "OK", "ok"), ("41", "OR", "or"), ("42", "PA", "pa"),
    ("44", "RI", "ri"), ("45", "SC", "sc"), ("46", "SD", "sd"),
    ("47", "TN", "tn"), ("48", "TX", "tx"), ("49", "UT", "ut"),
    ("50", "VT", "vt"), ("51", "VA", "va"), ("53", "WA", "wa"),
    ("54", "WV", "wv"), ("55", "WI", "wi"), ("56", "WY", "wy"),
    ("72", "PR", "pr"),
]

# Field counts that pin the PL layout. A segment that does not match these is
# not the file this script knows how to read, so the run stops rather than
# silently reading counts out of the wrong columns.
NFIELDS = {"geo": 97, "seg1": 149, "seg2": 152, "seg3": 15}

# 0-based field positions, verified against the Census Bureau's R import
# scripts (2020PL_R_import_scripts.zip) and against the files themselves.
#
# geoheader (97):  SUMLEV 2, LOGRECNO 7, GEOID 8, GEOCODE 9, STATE 12,
#                  COUNTY 14, TRACT 32, BLOCK 34, AREALAND 84, POP100 90
# seg1 (149):      5 key fields, then P1 (71 cells) then P2 (73 cells).
#                  P1-k at 4+k  ->  P1-1 = 5
#                  P2-k at 75+k ->  P2-2 = 77, P2-5 = 80
# seg2 (152):      5 key fields, P3 (71), P4 (73), H1 (3).
#                  P3-k at 4+k  ->  P3-1 = 5
#                  H1-k at 148+k -> H1-1 = 149, H1-2 = 150, H1-3 = 151
# seg3 (15):       5 key fields, P5 (10). P5-1 = 5.
GEO_SUMLEV, GEO_LOGRECNO, GEO_GEOCODE = 2, 7, 9
GEO_STATE, GEO_COUNTY, GEO_TRACT, GEO_BLOCK = 12, 14, 32, 34
SEG_LOGRECNO = 4

SUMLEV_BLOCK = "750"

GPIO = shutil.which("gpio") or "gpio"

# Hive partition key. Portolan recognizes exactly one multi-file scheme,
# hive ``key=value/`` directories, and derives one STAC item per directory; a
# flat directory of 52 files instead yields 52 collection-level assets and no
# items at all. See docs/blocks-build-notes.md for the layout decision.
#
# The key is ``state_fips`` rather than ``state`` on purpose: a hive key is
# synthesized as a column when the glob is read, and ``state`` is already a
# column here holding the USPS code. Same concept, two spellings, so the key
# takes the name that does not collide.
PARTITION_KEY = "state_fips"
PARTITION_GLOB = f"{PARTITION_KEY}=*/*.parquet"


def partition_path(fips):
    return OUT_DIR / f"{PARTITION_KEY}={fips}" / f"{fips}.parquet"


def run(cmd, **kw):
    cmd = [str(c) for c in cmd]
    proc = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\n"
            f"stdout: {proc.stdout[-1500:]}\nstderr: {proc.stderr[-2500:]}"
        )
    return proc.stdout


def duckdb_sql(sql, json_out=False):
    fmt = ["-json"] if json_out else ["-noheader", "-list"]
    cmd = ["duckdb", *fmt, "-c", sql]
    out = run(cmd)
    return json.loads(out) if json_out else out


def columns_struct(n):
    """An explicit read_csv column spec: {'f0': 'VARCHAR', ...}.

    DuckDB's positional names are zero-padded to the width of the widest
    index, so a 97-field file gets ``column00`` and a 149-field file gets
    ``column000``. Naming the columns outright sidesteps that entirely.
    """
    return "{" + ", ".join(f"'f{i}': 'VARCHAR'" for i in range(n)) + "}"


def read_pl(path, n):
    """A read_csv call over one pipe-delimited PL file.

    Quoting and escaping are switched off: the PL files are not quoted, and a
    stray double quote inside a NAME field would otherwise swallow delimiters.

    ``encoding='latin-1'`` is required, not defensive. The geoheader carries
    place names in ISO-8859-1 -- Arizona's "Kayenta CCD" record is the first
    one to break a UTF-8 read -- and DuckDB validates the whole line even
    though every field this build reads is ASCII. Decoding is the fix;
    ``ignore_errors`` would silently drop whole blocks.
    """
    return (
        f"read_csv('{path}', delim='|', header=false, quote='', escape='', "
        f"encoding='latin-1', columns={columns_struct(n)})"
    )


def check_field_counts(paths):
    """Confirm each segment has the field count the layout above assumes."""
    for kind, path in paths.items():
        with open(path, encoding="latin-1") as fh:
            n = len(fh.readline().rstrip("\n").split("|"))
        if n != NFIELDS[kind]:
            raise RuntimeError(
                f"{path.name}: {n} fields, expected {NFIELDS[kind]}. "
                "The PL layout this script pins does not match this file."
            )


def verify_output(path):
    """Assert the finished partition is spec-conformant GeoParquet.

    Checks the four properties Portolan validation depends on and that a
    writer in this pipeline has been seen to drop: GeoParquet 1.1 metadata, a
    bbox covering column, min/max statistics on every bbox leaf in every row
    group (PTL-DAT-007), and ZSTD on the geometry column. The CRS key must be
    absent, which is how the spec spells WGS84 lon/lat.

    Raises on any failure, so a bad partition stops the run instead of
    reaching the catalog.
    """
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(path)
    md = pf.metadata
    meta = pf.schema_arrow.metadata or {}
    if b"geo" not in meta:
        raise RuntimeError(f"{path.name}: no 'geo' schema metadata")
    geo = json.loads(meta[b"geo"])
    col = geo["columns"][geo["primary_column"]]
    if not geo["version"].startswith("1.1"):
        raise RuntimeError(f"{path.name}: GeoParquet {geo['version']}, want 1.1")
    if not col.get("covering", {}).get("bbox"):
        raise RuntimeError(f"{path.name}: no bbox covering metadata")
    if col.get("crs") is not None:
        raise RuntimeError(
            f"{path.name}: crs is {col['crs']!r}; WGS84 lon/lat is written as "
            "an omitted crs key")

    leaves = [
        (i, md.row_group(0).column(i).path_in_schema)
        for i in range(md.row_group(0).num_columns)
    ]
    bbox_leaves = [i for i, name in leaves if name.startswith("bbox.")]
    if len(bbox_leaves) != 4:
        raise RuntimeError(f"{path.name}: {len(bbox_leaves)} bbox leaves, want 4")
    for g in range(md.num_row_groups):
        for i in bbox_leaves:
            if md.row_group(g).column(i).statistics is None:
                raise RuntimeError(
                    f"{path.name}: row group {g} missing bbox statistics")
    geom_idx = next(i for i, name in leaves if name == "geometry")
    comp = md.row_group(0).column(geom_idx).compression
    if comp != "ZSTD":
        raise RuntimeError(f"{path.name}: geometry compression is {comp}")
    return md.num_rows


def build_state(fips, usps, ab, keep_scratch=False):
    """Build one per-state partition. Returns a dict of validation counters."""
    t0 = time.time()
    pl_zip = CACHE / f"{ab}2020.pl.zip"
    tiger_zip = CACHE / f"tl_2024_{fips}_tabblock20.zip"
    for z in (pl_zip, tiger_zip):
        if not z.exists():
            raise FileNotFoundError(f"missing source: {z}")

    work = SCRATCH / f"build-{fips}"
    if work.exists():
        shutil.rmtree(work)
    pl_dir = work / "pl"
    tiger_dir = work / "tiger"
    pl_dir.mkdir(parents=True)
    tiger_dir.mkdir(parents=True)

    try:
        run(["unzip", "-o", "-q", pl_zip, "-d", pl_dir])
        run(["unzip", "-o", "-q", tiger_zip, "-d", tiger_dir])

        paths = {
            "geo": pl_dir / f"{ab}geo2020.pl",
            "seg1": pl_dir / f"{ab}000012020.pl",
            "seg2": pl_dir / f"{ab}000022020.pl",
            "seg3": pl_dir / f"{ab}000032020.pl",
        }
        for kind, p in paths.items():
            if not p.exists():
                raise FileNotFoundError(f"{kind} missing after unzip: {p}")
        check_field_counts(paths)

        shp = tiger_dir / f"tl_2024_{fips}_tabblock20.shp"
        if not shp.exists():
            raise FileNotFoundError(f"shapefile missing after unzip: {shp}")

        # --- 1. geometry to EPSG:4326 Parquet, via GDAL ---------------------
        geom_pq = work / "geom.parquet"
        run([
            "ogr2ogr", "-f", "Parquet", geom_pq, shp,
            "-sql", f"SELECT GEOID20, ALAND20 FROM tl_2024_{fips}_tabblock20",
            "-t_srs", "EPSG:4326", "-nln", "blocks",
            "-lco", "COMPRESSION=ZSTD", "-lco", "GEOMETRY_NAME=geometry",
        ])

        # --- 2. join the PL counts onto the geometry ------------------------
        g = lambda i: f"g.f{i}"          # noqa: E731  geoheader field
        s = lambda t, i: f"{t}.f{i}"     # noqa: E731  segment field

        joined = work / "joined.parquet"
        sql = f"""
        INSTALL spatial; LOAD spatial;
        CREATE TEMP TABLE pl AS
        SELECT
            {g(GEO_GEOCODE)}                              AS geoid,
            {g(GEO_STATE)} || {g(GEO_COUNTY)}
              || {g(GEO_TRACT)} || {g(GEO_BLOCK)}         AS geoid_parts,
            s1.f5::INTEGER                                AS pop_total,
            s1.f7::INTEGER                                AS pop_white,
            s1.f8::INTEGER                                AS pop_black,
            s1.f9::INTEGER                                AS pop_aian,
            s1.f10::INTEGER                               AS pop_asian,
            s1.f11::INTEGER                               AS pop_nhpi,
            s1.f12::INTEGER                               AS pop_other,
            s1.f13::INTEGER                               AS pop_two_plus,
            s1.f77::INTEGER                               AS pop_hispanic,
            s1.f80::INTEGER                               AS pop_white_nh,
            s2.f5::INTEGER                                AS vap_total,
            s2.f149::INTEGER                              AS housing_units,
            s2.f150::INTEGER                              AS housing_occupied,
            s2.f151::INTEGER                              AS housing_vacant,
            s3.f5::INTEGER                                AS group_quarters_pop
        FROM {read_pl(paths['geo'], NFIELDS['geo'])} g
        JOIN {read_pl(paths['seg1'], NFIELDS['seg1'])} s1
          ON {s('s1', SEG_LOGRECNO)} = {g(GEO_LOGRECNO)}
        JOIN {read_pl(paths['seg2'], NFIELDS['seg2'])} s2
          ON {s('s2', SEG_LOGRECNO)} = {g(GEO_LOGRECNO)}
        JOIN {read_pl(paths['seg3'], NFIELDS['seg3'])} s3
          ON {s('s3', SEG_LOGRECNO)} = {g(GEO_LOGRECNO)}
        WHERE {g(GEO_SUMLEV)} = '{SUMLEV_BLOCK}';

        CREATE TEMP TABLE geom AS
        SELECT GEOID20 AS geoid, ALAND20::BIGINT AS aland, geometry
        FROM read_parquet('{geom_pq}');

        COPY (
          SELECT
            t.geoid,
            '{usps}'                                      AS state,
            t.pop_total, t.pop_white, t.pop_black, t.pop_aian, t.pop_asian,
            t.pop_nhpi, t.pop_other, t.pop_two_plus,
            t.pop_hispanic, t.pop_white_nh,
            t.vap_total,
            t.housing_units, t.housing_occupied, t.housing_vacant,
            t.group_quarters_pop,
            CASE WHEN t.pop_total > 0
                 THEN round(100.0 * t.pop_white_nh / t.pop_total, 2) END
                                                          AS pct_white_nh,
            CASE WHEN t.pop_total > 0
                 THEN round(100.0 * t.pop_black / t.pop_total, 2) END
                                                          AS pct_black,
            CASE WHEN t.pop_total > 0
                 THEN round(100.0 * t.pop_hispanic / t.pop_total, 2) END
                                                          AS pct_hispanic,
            CASE WHEN t.housing_units > 0
                 THEN round(100.0 * t.housing_vacant / t.housing_units, 2) END
                                                          AS pct_vacant,
            CASE WHEN t.aland > 0
                 THEN round(t.pop_total / (t.aland / 1000000.0), 1) END
                                                          AS pop_density,
            round(t.aland / 1000000.0, 3)                 AS aland_sqkm,
            t.geometry
          FROM (
            SELECT gm.geoid, gm.aland, gm.geometry, p.* EXCLUDE (geoid)
            FROM geom gm JOIN pl p ON p.geoid = gm.geoid
          ) t
        ) TO '{joined}' (FORMAT PARQUET, COMPRESSION ZSTD);

        -- counters for the validation report
        COPY (
          SELECT
            (SELECT count(*) FROM pl)                              AS pl_rows,
            (SELECT count(*) FROM geom)                            AS tiger_rows,
            (SELECT count(*) FROM pl WHERE geoid <> geoid_parts)   AS geoid_mismatch,
            (SELECT count(*) FROM pl p
               WHERE NOT EXISTS (SELECT 1 FROM geom g WHERE g.geoid = p.geoid))
                                                                   AS pl_orphans,
            (SELECT count(*) FROM geom g
               WHERE NOT EXISTS (SELECT 1 FROM pl p WHERE p.geoid = g.geoid))
                                                                   AS tiger_orphans,
            (SELECT sum(pop_total)::BIGINT FROM pl)                AS pop_total,
            (SELECT sum(housing_units)::BIGINT FROM pl)            AS housing_units,
            (SELECT count(*) FROM pl
               WHERE housing_occupied + housing_vacant <> housing_units)
                                                                   AS housing_imbalance
        ) TO '{work / "counters.json"}' (FORMAT JSON, ARRAY false);
        """
        duckdb_sql(sql)
        counters = json.loads((work / "counters.json").read_text())

        # --- 3. write the partition: Hilbert order + bbox covering ---------
        out = partition_path(fips)
        out.parent.mkdir(parents=True, exist_ok=True)
        sorted_pq = work / "sorted.parquet"
        # gpio refuses to overwrite, and moving the finished file into place
        # keeps a failed rebuild from leaving a half-written partition.
        run([GPIO, "sort", "hilbert", joined, sorted_pq, "--add-bbox"])
        out.unlink(missing_ok=True)
        shutil.move(str(sorted_pq), str(out))

        counters.update(
            fips=fips, state=usps,
            rows=verify_output(out),
            bytes=out.stat().st_size,
            seconds=round(time.time() - t0, 1),
            path=str(out.relative_to(ROOT)),
        )
        return counters
    finally:
        if not keep_scratch:
            shutil.rmtree(work, ignore_errors=True)


def validate(results):
    """Cross-partition validation. Returns (report dict, list of problems)."""
    problems = []
    by_fips = {r["fips"]: r for r in results}

    us_pop = sum(r["pop_total"] for r in results if r["fips"] != "72")
    pr_pop = by_fips.get("72", {}).get("pop_total")
    total_rows = sum(r["rows"] for r in results)

    if len(results) == len(STATES):
        if us_pop != 331_449_281:
            problems.append(
                f"50 states + DC population {us_pop:,} != 331,449,281")
        if pr_pop != 3_285_874:
            problems.append(f"Puerto Rico population {pr_pop:,} != 3,285,874")

    for r in results:
        if r["pl_orphans"] or r["tiger_orphans"]:
            problems.append(
                f"{r['state']}: {r['pl_orphans']} PL blocks without geometry, "
                f"{r['tiger_orphans']} TIGER blocks without counts")
        if r["housing_imbalance"]:
            problems.append(
                f"{r['state']}: {r['housing_imbalance']} blocks where "
                "occupied + vacant != units")
        if r["geoid_mismatch"]:
            problems.append(
                f"{r['state']}: {r['geoid_mismatch']} blocks where GEOCODE != "
                "STATE+COUNTY+TRACT+BLOCK")
        if r["rows"] != r["tiger_rows"]:
            problems.append(
                f"{r['state']}: wrote {r['rows']} rows but TIGER has "
                f"{r['tiger_rows']}")

    # geoid uniqueness across every partition at once, and a single schema
    # across all of them (Portolan PTL-DAT-014 queries the glob as one table).
    files = sorted(OUT_DIR.glob(PARTITION_GLOB))
    if files:
        glob = str(OUT_DIR / PARTITION_GLOB)
        dup = duckdb_sql(
            f"SELECT count(*) - count(DISTINCT geoid) "
            f"FROM read_parquet('{glob}', hive_partitioning=false)"
        ).strip()
        if int(dup) != 0:
            problems.append(f"{dup} duplicate geoid values across partitions")

        import pyarrow.parquet as pq
        schemas = {}
        for f in files:
            sig = tuple((fl.name, str(fl.type)) for fl in pq.read_schema(f))
            schemas.setdefault(sig, []).append(f.parent.name)
        if len(schemas) > 1:
            problems.append(
                f"{len(schemas)} distinct schemas across partitions: "
                + "; ".join(str(v[:4]) for v in schemas.values()))

    return {
        "partitions": len(results),
        "files": len(files),
        "total_rows": total_rows,
        "us_population_50_states_plus_dc": us_pop,
        "pr_population": pr_pop,
        "total_bytes": sum(r["bytes"] for r in results),
        "per_state": sorted(results, key=lambda r: r["fips"]),
        "problems": problems,
    }, problems


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("fips", nargs="*", help="state FIPS codes (default: all)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--keep-scratch", action="store_true")
    ap.add_argument("--validate-only", action="store_true",
                    help="re-read the saved report and re-run cross-checks")
    args = ap.parse_args()

    if args.validate_only:
        results = json.loads(REPORT.read_text())["per_state"]
        report, problems = validate(results)
    else:
        wanted = set(args.fips)
        todo = [s for s in STATES if not wanted or s[0] in wanted]
        if wanted - {s[0] for s in todo}:
            sys.exit(f"unknown FIPS: {sorted(wanted - {s[0] for s in todo})}")

        SCRATCH.mkdir(parents=True, exist_ok=True)
        results, failures = [], []
        with concurrent.futures.ThreadPoolExecutor(args.workers) as pool:
            futures = {
                pool.submit(build_state, f, u, a, args.keep_scratch): (f, u)
                for f, u, a in todo
            }
            for fut in concurrent.futures.as_completed(futures):
                fips, usps = futures[fut]
                try:
                    r = fut.result()
                except Exception as exc:  # noqa: BLE001
                    failures.append((fips, usps, exc))
                    print(f"FAIL {usps} ({fips}): {exc}", flush=True)
                else:
                    results.append(r)
                    print(
                        f"ok   {usps} ({fips}): {r['rows']:>7,} blocks  "
                        f"pop {r['pop_total']:>11,}  "
                        f"{r['bytes'] / 1e6:>7.1f} MB  {r['seconds']:>5.1f}s",
                        flush=True)

        report, problems = validate(results)
        report["failures"] = [[f, u, str(e)] for f, u, e in failures]
        REPORT.write_text(json.dumps(report, indent=2))

    print("\n=== validation ===")
    print(f"partitions written : {report['partitions']}")
    print(f"files on disk      : {report['files']}")
    print(f"total blocks       : {report['total_rows']:,}")
    print(f"50 states + DC pop : {report['us_population_50_states_plus_dc']:,}"
          "  (published: 331,449,281)")
    pr = report["pr_population"]
    print(f"Puerto Rico pop    : {pr:,}" if pr is not None
          else "Puerto Rico pop    : (not in this run)",
          " (published: 3,285,874)")
    print(f"total size         : {report['total_bytes'] / 1e9:.2f} GB")
    if problems:
        print(f"\nPROBLEMS ({len(problems)}):")
        for p in problems:
            print(f"  - {p}")
    else:
        print("\nall checks passed")
    return 1 if problems or report.get("failures") else 0


if __name__ == "__main__":
    raise SystemExit(main())
