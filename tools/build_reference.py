#!/usr/bin/env python3
"""Build catalog/reference/: geography that carries no demographic numbers.

Four collections, from TIGER/Line 2024 and the 2020 Census relationship
files (see docs/spec-reference-layers.md for the full brief):

    urban-areas       UAC20, one national file, 2020 urban area polygons.
    landmarks-area     AREALM (56 state files) + MIL (1 national file),
                       combined into one table with a `landmark_kind`
                       column so a civilian landmark and a military one
                       read the same way.
    landmarks-point    POINTLM, 56 state files, point landmarks.
    crosswalks         2020 relationship (rel2020) files. Tabular, no
                       geometry. One parquet per relationship table.

Usage:
  python3 tools/build_reference.py --list
  python3 tools/build_reference.py urban-areas landmarks-area
  python3 tools/build_reference.py --all

The three spatial collections are written the same way
tools/build_blocks.py writes catalog/blocks/: `gpio convert geoparquet`
turns the shapefile into GeoParquet, keeping the source CRS (NAD83,
EPSG:4269 -- TIGER's native CRS, not reprojected), then
`gpio sort hilbert --add-bbox` writes the final file in Hilbert row
order with a bbox covering column, ZSTD and sized row groups. That
matches the write path tools/build_wide_themes.py documents and that
catalog/counties/county-income/county-income.parquet shows on disk.

`crosswalks` has no geometry, so it skips the gpio step and is written
directly with DuckDB (ZSTD, the same row-group size as the spatial
files, for consistency rather than necessity).

Downloads land in staging/reference-cache/ (gitignored) and are kept
between runs, so a second run of this script does not re-fetch them.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import duckdb
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import specs  # noqa: E402  -- read-only: reuses the STATEFP -> USPS table

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "staging" / "reference-cache"
SCRATCH = ROOT / "staging" / "reference-scratch"
OUT = ROOT / "catalog" / "reference"
LOGDIR = ROOT / "staging" / "tiles-logs"
REFERENCE_SCHEMA = (ROOT / "catalog" / "counties" / "county-income"
                    / "county-income.parquet")

GPIO = shutil.which("gpio") or "gpio"

TIGER = "https://www2.census.gov/geo/tiger/TIGER2024"
REL2020 = "https://www2.census.gov/geo/docs/maps-data/data/rel2020"

STATE_USPS = specs.STATE_USPS  # 56 FIPS codes: 50 states, DC, 5 territories

# --------------------------------------------------------------------------
# MTFCC decode table
# --------------------------------------------------------------------------
# The MAF/TIGER Feature Class Code (MTFCC) is a 5-character code the Census
# Bureau assigns to every TIGER feature. TIGER2024 has no 2024 edition of
# the code-definitions PDF; the nearest published vintage is 2022:
#   https://www2.census.gov/geo/pdfs/reference/mtfccs2022.pdf
# Every code below is copied from that PDF's "Feature Class" column. The
# code set is stable across editions -- each code here also appears, worded
# the same, in the 2021 and 2025 editions linked from
# https://www.census.gov/library/reference/code-lists/mt-feature-class-codes.html
# A code this build meets that is NOT in this table is left undecoded
# (feature_type is NULL) rather than guessed at; see the build report for
# which codes that happened to.
MTFCC = {
    "C3022": "Mountain Peak or Summit",
    "C3023": "Island",
    "C3024": "Levee",
    "C3025": "Jetty/Breakwater",
    "C3026": "Quarry (not water-filled), Open Pit Mine or Mine",
    "C3027": "Dam",
    "C3061": "Cul-de-sac",
    "C3062": "Traffic Circle",
    "C3066": "Gate",
    "C3067": "Toll Booth",
    "C3071": "Tower",
    "C3074": "Lighthouse Beacon",
    "C3075": "Tank/Tank Farm",
    "C3076": "Windmill Farm",
    "C3077": "Solar Farm",
    "C3078": "Monument or Memorial",
    "C3079": "Boundary Monument Point",
    "C3080": "Survey Control Point",
    "C3081": "Locality Point",
    "C3085": "Alaska Native Village Official Point",
    "K1121": "Apartment Building or Complex",
    "K1223": "Trailer Court or Mobile Home Park",
    "K1225": "Crew-of-Vessel Location",
    "K1226": "Housing Facility/Dormitory for Workers",
    "K1227": "Hotel, Motel, Resort, Spa, Hostel, YMCA, or YWCA",
    "K1228": "Campground",
    "K1229": "Shelter or Mission",
    "K1231": "Hospital/Hospice/Urgent Care Facility",
    "K1233": "Nursing Home, Retirement Home, or Home for the Aged",
    "K1235": "Juvenile Institution",
    "K1236": "Local Jail or Detention Center",
    "K1237": "Federal Penitentiary, State Prison, or Prison Farm",
    "K1238": "Other Correctional Institution",
    "K1239": "Convent, Monastery, Rectory, Other Religious Group Quarters",
    "K2100": "Governmental",
    "K2110": "Military Installation",
    "K2146": "Community Center",
    "K2165": "Government Center",
    "K2167": "Convention Center",
    "K2180": "Park",
    "K2181": "National Park Service Land",
    "K2182": "National Forest or Other Federal Land",
    "K2183": "Tribal Park, Forest, or Recreation Area",
    "K2184": "State Park, Forest, or Recreation Area",
    "K2185": "Regional Park, Forest, or Recreation Area",
    "K2186": "County Park, Forest, or Recreation Area",
    "K2187": "County Subdivision Park, Forest, or Recreation Area",
    "K2188": "Incorporated Place Park, Forest, or Recreation Area",
    "K2189": "Private Park, Forest, or Recreation Area",
    "K2190": ("Other Park, Forest, or Recreation Area (quasi-public, "
              "independent park commission, etc.)"),
    "K2191": "Post Office",
    "K2193": "Fire Department",
    "K2194": "Police Station",
    "K2195": "Library",
    "K2196": "City/Town Hall",
    "K2300": "Commercial Workplace",
    "K2361": "Shopping Center or Major Retail Center",
    "K2362": "Industrial Building or Industrial Park",
    "K2363": "Office Building or Office Park",
    "K2364": "Farm/Vineyard/Winery/Orchard",
    "K2366": "Other Employment Center",
    "K2400": "Transportation Terminal",
    "K2424": "Marina",
    "K2432": "Pier/Dock",
    "K2451": "Airport or Airfield",
    "K2452": "Train Station, Trolley or Mass Transit Rail Station",
    "K2453": "Bus Terminal",
    "K2454": "Marine Terminal",
    "K2455": "Seaplane Anchorage",
    "K2457": "Airport—Statistical Representation",
    "K2459": "Runway/Taxiway",
    "K2460": "Helicopter Landing Pad",
    "K2540": "University or College",
    "K2543": "School or Academy",
    "K2545": "Museum, Visitor Center, Cultural Center, or Tourist Attraction",
    "K2561": "Golf Course",
    "K2564": "Amusement Center",
    "K2582": "Cemetery",
    "K2586": "Zoo",
    "K3544": "Place of Worship",
    "G3500": "Urban Area",
}

# Codes this build actually met that MTFCC does not cover. Filled in by
# label_mtfcc() as each collection is built, read by the report at the end.
UNSOURCED_CODES: set[str] = set()


def mtfcc_case_sql(column: str) -> str:
    """A SQL CASE expression decoding `column` through MTFCC, else NULL."""
    whens = " ".join(
        f"WHEN {v!r} THEN {d!r}" for v, d in MTFCC.items())
    return f"CASE {column} {whens} ELSE NULL END"


def label_mtfcc(con, path: Path, column: str) -> None:
    """Record any MTFCC value in `path` that MTFCC does not decode."""
    rows = con.execute(
        f"SELECT DISTINCT {column} FROM read_parquet('{path}') "
        f"WHERE {column} NOT IN ({', '.join(repr(k) for k in MTFCC)})"
    ).fetchall()
    UNSOURCED_CODES.update(r[0] for r in rows if r[0] is not None)


# --------------------------------------------------------------------------
# Download + shell helpers
# --------------------------------------------------------------------------

def run(cmd, **kw):
    cmd = [str(c) for c in cmd]
    proc = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\n"
            f"stdout: {proc.stdout[-1500:]}\nstderr: {proc.stderr[-2500:]}")
    return proc.stdout


def fetch(url: str, dest: Path) -> Path:
    """Download `url` to `dest` unless it is already there."""
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    run(["curl", "-sf", "-o", tmp, url])
    tmp.rename(dest)
    return dest


def unzip_fresh(zip_path: Path, dest_dir: Path) -> Path:
    """Decompress `zip_path` into its own, empty `dest_dir`."""
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)
    run(["unzip", "-o", "-q", zip_path, "-d", dest_dir])
    return dest_dir


def gpio_hilbert(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.unlink(missing_ok=True)
    run([GPIO, "sort", "hilbert", src, dest, "--add-bbox"])


# --------------------------------------------------------------------------
# urban-areas: UAC20, one national zip
# --------------------------------------------------------------------------

def build_urban_areas() -> Path:
    zip_path = fetch(f"{TIGER}/UAC20/tl_2024_us_uac20.zip",
                      CACHE / "tl_2024_us_uac20.zip")
    work = unzip_fresh(zip_path, SCRATCH / "urban-areas")
    shp = next(work.glob("*.shp"))

    raw = SCRATCH / "urban-areas-raw.parquet"
    raw.unlink(missing_ok=True)
    run([GPIO, "convert", "geoparquet", shp, raw])

    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    label_mtfcc(con, raw, "MTFCC20")
    labeled = SCRATCH / "urban-areas-labeled.parquet"
    con.execute(f"""
        COPY (
          SELECT
            GEOID20                               AS geoid,
            NAMELSAD20                             AS name,
            MTFCC20                                AS mtfcc,
            {mtfcc_case_sql('MTFCC20')}            AS feature_type,
            round(ALAND20 / 1000000.0, 3)          AS aland_sqkm,
            round(AWATER20 / 1000000.0, 3)         AS awater_sqkm,
            geom AS geometry
          FROM read_parquet('{raw}')
        ) TO '{labeled}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    dest_dir = OUT / "urban-areas"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "urban-areas.parquet"
    gpio_hilbert(labeled, dest)
    shutil.rmtree(work, ignore_errors=True)
    return dest


# --------------------------------------------------------------------------
# landmarks-area: AREALM (56 state files) + MIL (1 national file)
# --------------------------------------------------------------------------

def build_landmarks_area() -> Path:
    parts = []
    for fips, usps in STATE_USPS.items():
        zip_path = fetch(f"{TIGER}/AREALM/tl_2024_{fips}_arealm.zip",
                         CACHE / f"tl_2024_{fips}_arealm.zip")
        work = unzip_fresh(zip_path, SCRATCH / f"arealm-{fips}")
        shp = next(work.glob("*.shp"))
        part = SCRATCH / f"arealm-{fips}.parquet"
        part.unlink(missing_ok=True)
        run([GPIO, "convert", "geoparquet", shp, part])
        parts.append((part, usps))
        shutil.rmtree(work, ignore_errors=True)

    mil_zip = fetch(f"{TIGER}/MIL/tl_2024_us_mil.zip",
                    CACHE / "tl_2024_us_mil.zip")
    mil_work = unzip_fresh(mil_zip, SCRATCH / "mil")
    mil_shp = next(mil_work.glob("*.shp"))
    mil_part = SCRATCH / "mil.parquet"
    mil_part.unlink(missing_ok=True)
    run([GPIO, "convert", "geoparquet", mil_shp, mil_part])

    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    selects = []
    for part, usps in parts:
        selects.append(f"""
          SELECT AREAID AS geoid, FULLNAME AS name, '{usps}' AS state,
                 'landmark' AS landmark_kind, MTFCC AS mtfcc,
                 round(ALAND / 1000000.0, 3) AS aland_sqkm,
                 round(AWATER / 1000000.0, 3) AS awater_sqkm, geom AS geometry
          FROM read_parquet('{part}')""")
    selects.append(f"""
          SELECT AREAID AS geoid, FULLNAME AS name, CAST(NULL AS VARCHAR) AS state,
                 'military' AS landmark_kind, MTFCC AS mtfcc,
                 round(ALAND / 1000000.0, 3) AS aland_sqkm,
                 round(AWATER / 1000000.0, 3) AS awater_sqkm, geom AS geometry
          FROM read_parquet('{mil_part}')""")
    union_sql = " UNION ALL ".join(selects)

    combined = SCRATCH / "landmarks-area-combined.parquet"
    con.execute(f"COPY ({union_sql}) TO '{combined}' "
                f"(FORMAT PARQUET, COMPRESSION ZSTD)")
    label_mtfcc(con, combined, "mtfcc")

    labeled = SCRATCH / "landmarks-area-labeled.parquet"
    con.execute(f"""
        COPY (
          SELECT geoid, name, state, landmark_kind, mtfcc,
                 {mtfcc_case_sql('mtfcc')} AS feature_type,
                 aland_sqkm, awater_sqkm, geometry
          FROM read_parquet('{combined}')
        ) TO '{labeled}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    dest_dir = OUT / "landmarks-area"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "landmarks-area.parquet"
    gpio_hilbert(labeled, dest)
    shutil.rmtree(mil_work, ignore_errors=True)
    return dest


# --------------------------------------------------------------------------
# landmarks-point: POINTLM, 56 state files
# --------------------------------------------------------------------------

def build_landmarks_point() -> Path:
    parts = []
    for fips, usps in STATE_USPS.items():
        zip_path = fetch(f"{TIGER}/POINTLM/tl_2024_{fips}_pointlm.zip",
                         CACHE / f"tl_2024_{fips}_pointlm.zip")
        work = unzip_fresh(zip_path, SCRATCH / f"pointlm-{fips}")
        shp = next(work.glob("*.shp"))
        part = SCRATCH / f"pointlm-{fips}.parquet"
        part.unlink(missing_ok=True)
        run([GPIO, "convert", "geoparquet", shp, part])
        parts.append((part, usps))
        shutil.rmtree(work, ignore_errors=True)

    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    selects = [
        f"""SELECT POINTID AS geoid, FULLNAME AS name, '{usps}' AS state,
                   MTFCC AS mtfcc, geom AS geometry
            FROM read_parquet('{part}')"""
        for part, usps in parts
    ]
    combined = SCRATCH / "landmarks-point-combined.parquet"
    con.execute(f"COPY ({' UNION ALL '.join(selects)}) TO '{combined}' "
                f"(FORMAT PARQUET, COMPRESSION ZSTD)")
    label_mtfcc(con, combined, "mtfcc")

    labeled = SCRATCH / "landmarks-point-labeled.parquet"
    con.execute(f"""
        COPY (
          SELECT geoid, name, state, mtfcc,
                 {mtfcc_case_sql('mtfcc')} AS feature_type, geometry
          FROM read_parquet('{combined}')
        ) TO '{labeled}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    dest_dir = OUT / "landmarks-point"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "landmarks-point.parquet"
    gpio_hilbert(labeled, dest)
    return dest


# --------------------------------------------------------------------------
# crosswalks: 2020 relationship (rel2020) files, tabular, no geometry
# --------------------------------------------------------------------------

# subdir -> [(source file(s), output name)]. Every rel2020 relationship
# this catalog carries. t10t20 is 56 per-state zips with no national file
# (the only one of the ten subdirs without one); every other relationship
# ships one national file and that is the one used here -- the per-state
# files in those subdirs repeat the same relationship in smaller pieces and
# add nothing a national read does not already have.
RELATIONSHIPS = {
    "t10t20": [("t10t20", "t10t20-tract")],
    "tract": [("tab20_tract20_tract10_natl.txt", "tract")],
    "blkgrp": [("tab20_blkgrp20_blkgrp10_natl.txt", "blkgrp")],
    "place": [("tab20_place20_place10_natl.txt", "place")],
    "cousub": [("tab20_cousub20_cousub10_natl.txt", "cousub")],
    "cbsa": [
        ("acs23_cbsa20_cbsa23_natl.txt", "cbsa-cbsa23"),
        ("acs23_necta20_cbsa23_natl.txt", "cbsa-necta23"),
        ("acs23_ua20_cbsa23_natl.txt", "cbsa-ua23"),
    ],
    "zcta520": [
        ("tab20_zcta510_zcta520_natl.txt", "zcta520-zcta510"),
        ("tab20_zcta520_county20_natl.txt", "zcta520-county20"),
        ("tab20_zcta520_cousub20_natl.txt", "zcta520-cousub20"),
        ("tab20_zcta520_place20_natl.txt", "zcta520-place20"),
        ("tab20_zcta520_tabblock20_natl.txt", "zcta520-tabblock20"),
        ("tab20_zcta520_tract20_natl.txt", "zcta520-tract20"),
    ],
    "ua": [
        ("tab20_cd11820_ua20_natl.txt", "ua-cd118"),
        ("tab20_sldl202220_ua20_natl.txt", "ua-sldl2022"),
        ("tab20_sldu202220_ua20_natl.txt", "ua-sldu2022"),
        ("tab20_ua10_ua20_natl.txt", "ua-ua10"),
        ("tab20_ua20_county20_natl.txt", "ua-county20"),
        ("tab20_ua20_cousub20_natl.txt", "ua-cousub20"),
        ("tab20_ua20_place20_natl.txt", "ua-place20"),
        ("tab20_ua20_zcta520_natl.txt", "ua-zcta520"),
    ],
    "puma520": [
        ("tab20_puma520_cousub20_natl.txt", "puma520-cousub20"),
        ("tab20_puma520_puma510_natl.txt", "puma520-puma510"),
        ("tab20_puma520_ua20_natl.txt", "puma520-ua20"),
        ("tab20_puma520_zcta520_natl.txt", "puma520-zcta520"),
    ],
    "aiannh": [
        ("tab20_aiannh20_county20_natl.txt", "aiannh-county20"),
        ("tab20_aiannh20_cousub20_natl.txt", "aiannh-cousub20"),
        ("tab20_aiannh20_tract20_natl.txt", "aiannh-tract20"),
    ],
}


def build_t10t20(con) -> Path:
    """The 52 per-state TAB2010_TAB2020 block relate files, concatenated.

    This is the one rel2020 table with no national file: every other
    relationship below reads straight from a single natl .txt. These are
    block-to-block (not tract-to-tract) because that is the only level the
    Census Bureau publishes this relationship at -- 2010 and 2020 tracts do
    not nest, so the official crosswalk is built from block-level land and
    water overlap instead. The state+county+tract columns in this file are
    exactly what later tract-trend work reads.
    """
    sub_dir = CACHE / "t10t20"
    work = SCRATCH / "t10t20-extract"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    for zip_path in sorted(sub_dir.glob("*.zip")):
        run(["unzip", "-o", "-q", zip_path, "-d", work])
    glob = str(work / "*.txt")
    dest = OUT / "crosswalks" / "t10t20-tract.parquet"
    dest.parent.mkdir(parents=True, exist_ok=True)
    src = (f"read_csv('{glob}', delim='|', header=true, "
          f"encoding='utf-8', union_by_name=true)")
    names = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {src}")
             .fetchall()]
    select_list = ", ".join(f'"{n}" AS {n.lower()}' for n in names)
    con.execute(f"""
        COPY (
          SELECT {select_list} FROM {src}
        ) TO '{dest}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 20000)
    """)
    shutil.rmtree(work, ignore_errors=True)
    return dest


def build_one_crosswalk(con, subdir: str, filename: str, out_name: str) -> Path:
    path = fetch(f"{REL2020}/{subdir}/{filename}",
                CACHE / "rel2020" / subdir / filename)
    src = f"read_csv('{path}', delim='|', header=true, encoding='utf-8')"
    names = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {src}")
             .fetchall()]
    select_list = ", ".join(f'"{n}" AS {n.lower()}' for n in names)
    dest = OUT / "crosswalks" / f"{out_name}.parquet"
    dest.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"""
        COPY (SELECT {select_list} FROM {src})
        TO '{dest}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 20000)
    """)
    return dest


def build_crosswalks() -> list[Path]:
    con = duckdb.connect()
    dests = []
    for subdir, items in RELATIONSHIPS.items():
        for item in items:
            if subdir == "t10t20":
                dests.append(build_t10t20(con))
            else:
                filename, out_name = item
                dests.append(build_one_crosswalk(con, subdir, filename, out_name))
    return dests


# --------------------------------------------------------------------------
# QC
# --------------------------------------------------------------------------

def qc_spatial(path: Path, con) -> dict:
    out = {"id": path.stem, "path": str(path.relative_to(ROOT)),
          "problems": []}
    bad = out["problems"].append
    pf = pq.ParquetFile(path)
    out["rows"] = pf.metadata.num_rows
    out["columns"] = len(pf.schema_arrow.names)
    out["bytes"] = path.stat().st_size
    meta = pf.schema_arrow.metadata or {}
    if b"geo" not in meta:
        bad("no 'geo' schema metadata")
    else:
        geo = json.loads(meta[b"geo"])
        ref = json.loads(pq.ParquetFile(REFERENCE_SCHEMA)
                         .schema_arrow.metadata[b"geo"])
        out["geoparquet"] = geo["version"]
        if geo["version"] != ref["version"]:
            bad(f"GeoParquet {geo['version']}, reference is {ref['version']}")
        if "covering" not in geo["columns"][geo["primary_column"]]:
            bad("no bbox covering metadata")
    comp = pf.metadata.row_group(0).column(0).compression
    out["compression"] = comp
    if comp != "ZSTD":
        bad(f"compression is {comp}, not ZSTD")
    out["crs_key_present"] = "crs" in json.loads(
        meta.get(b"geo", b"{}") or b"{}").get(
            "columns", {}).get("geometry", {})
    return out


def qc_tabular(path: Path) -> dict:
    pf = pq.ParquetFile(path)
    return {"id": path.stem, "path": str(path.relative_to(ROOT)),
            "rows": pf.metadata.num_rows,
            "columns": len(pf.schema_arrow.names),
            "bytes": path.stat().st_size,
            "compression": pf.metadata.row_group(0).column(0).compression,
            "problems": []}


BUILDERS = {
    "urban-areas": build_urban_areas,
    "landmarks-area": build_landmarks_area,
    "landmarks-point": build_landmarks_point,
    "crosswalks": build_crosswalks,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("collections", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        for cid in BUILDERS:
            print(cid)
        return 0

    want = list(BUILDERS) if args.all else args.collections
    if not want:
        ap.error("name at least one collection, or --all / --list")
    if unknown := [c for c in want if c not in BUILDERS]:
        ap.error(f"unknown collections: {unknown}")

    SCRATCH.mkdir(parents=True, exist_ok=True)
    LOGDIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")

    report = []
    for cid in want:
        t0 = time.time()
        result = BUILDERS[cid]()
        paths = result if isinstance(result, list) else [result]
        for p in paths:
            r = (qc_tabular(p) if cid == "crosswalks" else qc_spatial(p, con))
            r["seconds"] = round(time.time() - t0, 1)
            report.append(r)
            flag = "✓" if not r["problems"] else "✗"
            print(f"{flag} {r['id']:22s} {r['rows']:>9,} rows  "
                  f"{r['columns']:>3} cols  {r['bytes'] / 1e6:>7.1f} MB")
            for p2 in r["problems"]:
                print(f"    ! {p2}")

    (LOGDIR / "reference.qc.json").write_text(
        json.dumps({"generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
                   "files": report,
                   "unsourced_mtfcc": sorted(UNSOURCED_CODES)}, indent=1,
                  default=str) + "\n")
    print(f"\nunsourced MTFCC codes: {sorted(UNSOURCED_CODES) or 'none'}")
    failed = [p for r in report for p in r["problems"]]
    print("all checks passed" if not failed else f"{len(failed)} problem(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
