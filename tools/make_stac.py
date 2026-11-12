#!/usr/bin/env python3
"""Finalize this catalog's STAC metadata. Runs AFTER `portolan add`.

Ported from the St. Louis census catalog's `tools/finalize_stac.py` and
widened to the national catalog's twelve collections. It patches what the
Portolan CLI does not emit, from the three modules that hold this catalog's
prose and facts:

  tools/collection_meta.py  titles, descriptions, keywords, source assets
  tools/column_docs.py      one description per column, per collection
  tools/specs.py            which ACS table and lines every column came from

## Run order

    bash   tools/download_sources.sh        # upstream files into staging/
    python tools/build_acs.py               # 11 ACS GeoParquet collections
    python tools/build_blocks.py            # catalog/blocks/, 52 partitions
    python tools/make_tiles.py              # PMTiles per collection
    python tools/collection_meta.py --write # .portolan/metadata.yaml
    portolan add catalog/<collection>/ …    # CLI writes collection.json
    python tools/make_styles.py             # MapLibre styles + legends
    python tools/make_stac.py               # <- THIS SCRIPT
    python tests/run_all.py                 # gates
    python tools/publish.py --confirm       # publish

`collection_meta.py --write` has to precede `portolan add`, because the CLI
reads `.portolan/metadata.yaml`. Everything else here is applied on top of
what the CLI wrote, so this script runs last. It needs the data files and the
tiles on disk; running it before they exist is why it reports what it could
not find instead of guessing.

## What it writes

- `title` and `description` from `collection_meta`, with the feature count
  read out of the file rather than hardcoded
- `table:columns[].description` for **every** column, verified against the
  parquet schema as DuckDB reports it. A column with no description in
  `column_docs` fails the run — an undocumented column cannot reach the
  published catalog quietly
- `providers`: U.S. Census Bureau as producer and licensor, Portolan Mirrors
  as processor and host, matching `catalog/catalog.json`
- `license: CC0-1.0` plus a `rel="license"` link to the Bureau's open-data
  policy, and `rel="via"` links to data.census.gov and the program pages
- `source` assets for the exact upstream files each collection was built
  from, at their census.gov URLs, plus `metadata`-role documentation assets
- PMTiles link and asset with `pmtiles:layers` (the layer name is the
  collection id), style assets titled from the style files themselves, with
  the default style carrying `roles: ["style", "default"]`
- `file:size` and `file:checksum` (sha2-256 multihash) on every local asset,
  cached in `staging/checksums.json` so a re-run is cheap
- temporal extents: 2020-01-01/2024-12-31 for ACS, 2020-04-01 for blocks
- `keywords`, `themes`, and the STAC extension pins
- the `block-groups/` and `tracts/` sub-catalogs, and `child` links from the
  root catalog to all five top-level entries

Idempotent: every field is set or replaced, never appended to, so running it
twice leaves the same bytes. `self` links are stripped from collections (a
static catalog that hardcodes its own location cannot be mirrored); the root
catalog's `self` link is tracked in git on purpose and is left alone.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import collection_meta as meta  # noqa: E402
import column_docs as cd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
CHECKSUM_CACHE = ROOT / "staging" / "checksums.json"
SOURCE_SIZES = ROOT / "staging" / "source_sizes.json"

PORTOLAN_SCHEMA_DEFAULT = (
    "https://schemas.portolan-sdi.org/portolan/v0.2.0/schema.json")
FILE_EXT = "https://stac-extensions.github.io/file/v2.1.0/schema.json"
TABLE_EXT = "https://stac-extensions.github.io/table/v1.2.0/schema.json"
THEMES_EXT = "https://stac-extensions.github.io/themes/v1.0.0/schema.json"
WML_EXT = "https://stac-extensions.github.io/web-map-links/v1.3.0/schema.json"

PARQUET_TYPE = "application/vnd.apache.parquet"
PMTILES_TYPE = "application/vnd.pmtiles"
STYLE_TYPE = "application/vnd.mapbox.style+json"

PRODUCER = {
    "name": "U.S. Census Bureau",
    "description": ("Produces the American Community Survey, the Decennial "
                    "Census, and the TIGER/cartographic boundary geographies "
                    "this catalog is built from."),
    "roles": ["producer", "licensor"],
    "url": "https://www.census.gov/",
}
HOST = {
    "name": "Portolan Mirrors",
    "description": ("Converted the published summary files and boundary "
                    "files to cloud-native formats and maintains this "
                    "mirror. Not an official Census Bureau product."),
    "roles": ["processor", "host"],
    "url": meta.REPO,
}

# data.census.gov's own scheme for what program a collection belongs to, so
# "everything from the ACS" is answerable without string-matching titles.
THEME_SCHEME_ACS = meta.ACS_PROGRAM
THEME_SCHEME_PL = meta.PL_PROGRAM


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def duck(sql: str) -> list[dict]:
    """Run one DuckDB query, return rows. Empty list on failure."""
    r = subprocess.run(["duckdb", "-json", "-c", sql],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"duckdb failed: {r.stderr.strip()}\nSQL: {sql}")
    return json.loads(r.stdout or "[]")


_cache: dict | None = None


def _load_cache() -> dict:
    global _cache
    if _cache is None:
        try:
            _cache = json.loads(CHECKSUM_CACHE.read_text())
        except (OSError, json.JSONDecodeError):
            _cache = {}
    return _cache


def save_cache() -> None:
    if _cache is not None:
        CHECKSUM_CACHE.parent.mkdir(parents=True, exist_ok=True)
        CHECKSUM_CACHE.write_text(json.dumps(_cache, indent=1, sort_keys=True))


def multihash(path: Path) -> str:
    """sha2-256 multihash, cached on (path, size, mtime).

    The cache is what makes re-running cheap: hashing the 5.2 GB of block
    partitions every time would make this script something people avoid
    running, and a metadata step nobody re-runs goes stale.
    """
    st = path.stat()
    try:
        key = str(path.relative_to(ROOT))
    except ValueError:  # a symlinked data file living outside the repo
        key = str(path)
    cache = _load_cache()
    hit = cache.get(key)
    if hit and hit.get("size") == st.st_size and hit.get("mtime") == int(
            st.st_mtime):
        return hit["multihash"]
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    mh = "1220" + h.hexdigest()
    cache[key] = {"size": st.st_size, "mtime": int(st.st_mtime),
                  "multihash": mh}
    return mh


def stamp_asset(base: Path, asset: dict, checksums: bool = True) -> None:
    """file:size (+ file:checksum) for an asset whose href is local."""
    href = asset.get("href", "")
    if "://" in href or "*" in href:
        return
    p = (base / href).resolve()
    if not p.is_file():
        return
    asset["file:size"] = p.stat().st_size
    if checksums:
        asset["file:checksum"] = multihash(p)


def source_meta(url: str) -> dict:
    """`file:size` (+ `file:checksum`) recorded for an upstream file.

    Written by `--fetch-source-sizes`; absent on a fresh clone, in which case
    source assets simply carry no size. Never guessed: the size is the
    `Content-Length` census.gov served, and the checksum is only recorded
    when the staged local copy's length matches that exactly — so it is the
    hash of the bytes the Bureau served, not of something reassembled here.
    """
    try:
        recorded = json.loads(SOURCE_SIZES.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    entry = recorded.get(url)
    if entry is None:
        return {}
    if isinstance(entry, int):          # older cache format
        return {"file:size": entry}
    out = {"file:size": entry["size"]}
    if entry.get("checksum"):
        out["file:checksum"] = entry["checksum"]
    return out


def ensure_link(links: list, rel: str, href: str, type_: str | None = None,
                title: str | None = None, **extra) -> None:
    """Set a link, replacing one with the same (rel, href) if present."""
    for link in links:
        if link.get("rel") == rel and link.get("href") == href:
            if type_:
                link["type"] = type_
            if title:
                link["title"] = title
            link.update(extra)
            return
    link = {"rel": rel, "href": href}
    if type_:
        link["type"] = type_
    if title:
        link["title"] = title
    link.update(extra)
    links.append(link)


def root_title() -> str:
    return json.loads((CATALOG / "catalog.json").read_text()).get(
        "title", "US Census Demographics — Cloud-Native Mirror")


def portolan_schema() -> str:
    """Whatever profile version the root catalog pins, so nothing diverges."""
    exts = json.loads((CATALOG / "catalog.json").read_text()).get(
        "stac_extensions", [])
    for e in exts:
        if "schemas.portolan-sdi.org" in e:
            return e
    return PORTOLAN_SCHEMA_DEFAULT


# --------------------------------------------------------------------------
# data files
# --------------------------------------------------------------------------

DUCK_TO_TABLE = {
    "BIGINT": "int64", "INTEGER": "int32", "SMALLINT": "int16",
    "TINYINT": "int8", "HUGEINT": "int128", "UBIGINT": "uint64",
    "UINTEGER": "uint32", "DOUBLE": "double", "FLOAT": "float",
    "VARCHAR": "string", "BOOLEAN": "boolean", "DATE": "date",
    "BLOB": "binary", "GEOMETRY": "binary",
    "TIMESTAMP": "timestamp", "TIMESTAMP WITH TIME ZONE": "timestamp",
}


def duck_type(t: str) -> str:
    """DuckDB type name -> table-extension type name."""
    up = t.upper()
    if up in DUCK_TO_TABLE:
        return DUCK_TO_TABLE[up]
    if up.startswith("STRUCT"):
        # Spelled the way the table extension and the St. Louis catalog
        # spell the GeoParquet covering column.
        inner = t[t.index("(") + 1:t.rindex(")")]
        fields = ", ".join(
            f"{p.strip().split(' ', 1)[0]}: "
            f"{duck_type(p.strip().split(' ', 1)[1])}"
            for p in inner.split(",") if " " in p.strip())
        return f"struct<{fields}>"
    return t.lower()


def data_source(cid: str) -> str:
    """The SQL FROM target for a collection's data, or '' if absent."""
    d = CATALOG / meta.COLL_REL[cid]
    if cid == "blocks":
        parts = sorted(d.glob("state_fips=*/*.parquet"))
        if not parts:
            return ""
        return (f"read_parquet('{d}/state_fips=*/*.parquet', "
                f"hive_partitioning=true)")
    pq = d / f"{cid}.parquet"
    return f"'{pq}'" if pq.exists() else ""


def schema_of(cid: str) -> list[tuple[str, str]]:
    """(column, table-extension type) from the published parquet, via DuckDB."""
    src = data_source(cid)
    if not src:
        return []
    rows = duck(f"SELECT column_name, column_type FROM "
                f"(DESCRIBE SELECT * FROM {src})")
    return [(r["column_name"], duck_type(r["column_type"])) for r in rows]


def row_count(cid: str) -> int | None:
    src = data_source(cid)
    if not src:
        return None
    return duck(f"SELECT count(*) AS n FROM {src}")[0]["n"]


def table_columns(cid: str, existing: list[dict]) -> list[dict]:
    """table:columns for a collection, described and ordered like the file.

    Raises when a column has no description. That is the point: the gate is
    here rather than in a test because this is the only place that sees both
    the file's real schema and the documentation.
    """
    cols = schema_of(cid)
    if not cols:
        return existing
    had = {c["name"]: c for c in existing}
    gaps = cd.missing([n for n, _ in cols], cid)
    if gaps:
        raise SystemExit(
            f"{cid}: {len(gaps)} column(s) in the parquet have no "
            f"description in tools/column_docs.py: {', '.join(gaps)}\n"
            f"Add them there — an undocumented column must not publish.")
    out = []
    for name, dtype in cols:
        col = {"name": name,
               # Keep the type the CLI derived from the Arrow schema when it
               # has one; DuckDB's view of a GeoParquet geometry column is
               # less precise than Arrow's.
               "type": had.get(name, {}).get("type", dtype),
               "description": cd.describe(name, cid)}
        out.append(col)
    return out


# --------------------------------------------------------------------------
# one collection
# --------------------------------------------------------------------------

def style_assets(coll_dir: Path) -> dict:
    """Style files on disk -> assets, titled from the styles themselves."""
    out = {}
    styles = sorted((coll_dir / "styles").glob("*.json"))
    for sf in styles:
        obj = {}
        try:
            obj = json.loads(sf.read_text())
        except (OSError, json.JSONDecodeError):
            pass
        asset = {
            "href": f"./styles/{sf.name}",
            "type": STYLE_TYPE,
            "title": obj.get("name") or sf.stem.replace("-", " ").title(),
            "roles": ["style", "default"] if sf.stem == "default"
                     else ["style"],
        }
        desc = (obj.get("metadata") or {}).get("description")
        if desc:
            asset["description"] = desc
        out[f"styles/{sf.stem}"] = asset
    return out


def finalize_collection(cid: str, checksums: bool = True) -> str:
    rel = meta.COLL_REL[cid]
    coll_dir = CATALOG / rel
    f = coll_dir / "collection.json"
    if not f.exists():
        return f"✗ {rel}: no collection.json — run `portolan add` first"
    coll = json.loads(f.read_text())

    n = row_count(cid)
    coll["id"] = rel
    coll["title"] = meta.TITLES[cid]
    coll["description"] = meta.description(cid, n)
    coll["license"] = meta.LICENSE
    coll["keywords"] = meta.keywords(cid)

    has_pmtiles = (coll_dir / f"{cid}.pmtiles").exists()
    ext = set(coll.get("stac_extensions", []))
    ext.update({portolan_schema(), FILE_EXT, TABLE_EXT, THEMES_EXT})
    if has_pmtiles:
        ext.add(WML_EXT)
    coll["stac_extensions"] = sorted(ext)

    # Program as a theme, so a browser can group by survey rather than by
    # directory. The ids are the Census Bureau's own program shorthands.
    if cid == "blocks":
        coll["themes"] = [{
            "scheme": THEME_SCHEME_PL,
            "concepts": [{"id": "dec-pl94171",
                          "title": "2020 Census P.L. 94-171 Redistricting "
                                   "Data"}]}]
    else:
        coll["themes"] = [{
            "scheme": THEME_SCHEME_ACS,
            "concepts": [{"id": "acs5",
                          "title": "American Community Survey 5-year "
                                   "estimates"}]}]

    interval = (meta.BLOCKS_INTERVAL if cid == "blocks"
                else meta.ACS_INTERVAL)
    coll.setdefault("extent", {})["temporal"] = {"interval": [list(interval)]}

    # Spatial extent = the GeoParquet's own data bbox, not the union that
    # `portolan add` computes across assets: the PMTiles' A5 cell zooms
    # overhang the data footprint by a few degrees (a pentagon cell is
    # bigger than the features it aggregates), and the collection extent
    # should frame the data (PTL-DAT-005), not the padding.
    if cid != "blocks":
        pq_path = (CATALOG / meta.GROUP_OF[cid] / cid / f"{cid}.parquet"
                   if cid in meta.GROUP_OF
                   else CATALOG / cid / f"{cid}.parquet")
        if pq_path.exists():
            import pyarrow.parquet as _pq
            geo = json.loads(_pq.read_schema(pq_path).metadata[b"geo"])
            bbox = geo["columns"]["geometry"].get("bbox")
            if bbox:
                coll.setdefault("extent", {})["spatial"] = {"bbox": [bbox]}
    else:
        # Blocks: union the per-partition parquet bboxes (the items carry
        # them from `portolan add`'s data scan).
        boxes = []
        for item_file in sorted((CATALOG / "blocks").glob("state_fips=*/*.json")):
            item = json.loads(item_file.read_text())
            if item.get("bbox"):
                boxes.append(item["bbox"])
        if boxes:
            union = [min(b[0] for b in boxes), min(b[1] for b in boxes),
                     max(b[2] for b in boxes), max(b[3] for b in boxes)]
            coll.setdefault("extent", {})["spatial"] = {"bbox": [union]}

    if n is not None:
        coll["table:row_count"] = n
        if "geoparquet:feature_count" in coll:
            coll["geoparquet:feature_count"] = n
    coll["table:columns"] = table_columns(cid, coll.get("table:columns", []))
    coll.setdefault("table:primary_geometry", "geometry")

    coll["providers"] = [PRODUCER, HOST]
    # PTL-PRO-003: a mirror records its last sync date.
    coll["updated"] = meta.EXTRACTED + "T00:00:00Z"

    # Links: rebuilt for the rels this script owns, so a stale `via` from an
    # earlier run cannot survive as a claimed origin.
    depth = rel.count("/") + 1          # collection.json -> catalog root
    up = "../" * depth
    links = [l for l in coll.get("links", [])
             if l.get("rel") not in ("self", "via", "license", "pmtiles",
                                     "root", "parent")]
    ensure_link(links, "root", f"{up}catalog.json", "application/json",
                root_title())
    parent_title = (meta.GROUP_TITLES[meta.GROUP_OF[cid]]
                    if cid in meta.GROUP_OF else root_title())
    ensure_link(links, "parent", "../catalog.json", "application/json",
                parent_title)
    # Only linked once they exist: `portolan readme` writes README.md after
    # this script, and tests/test_links.py resolves every relative href.
    if (coll_dir / "README.md").exists():
        ensure_link(links, "describedby", "./README.md", "text/markdown",
                    "Collection README")
    if (coll_dir / "AGENTS.md").exists():
        ensure_link(links, "agents", "./AGENTS.md", "text/markdown",
                    "Agent/LLM usage guide")
    ensure_link(links, "license", meta.OPEN_DATA_POLICY, "text/html",
                "U.S. Census Bureau open data policy — U.S. Government work, "
                "public domain")
    ensure_link(links, "via", meta.DATA_CENSUS, "text/html",
                "data.census.gov — the authoritative source for this data")
    if cid == "blocks":
        ensure_link(links, "via", meta.PL_PROGRAM, "text/html",
                    "Decennial Census P.L. 94-171 Redistricting Data program")
        ensure_link(links, "via", meta.PL_DIR, "text/html",
                    "2020 P.L. 94-171 state archives (source data)")
    else:
        ensure_link(links, "via", meta.ACS_PROGRAM, "text/html",
                    "American Community Survey program documentation")
        ensure_link(links, "via", meta.ACS_5YR_DATA, "text/html",
                    "ACS 2020–2024 5-year table-based Summary File "
                    "(source data)")
    if has_pmtiles:
        ensure_link(links, "pmtiles", f"./{cid}.pmtiles", PMTILES_TYPE,
                    f"{meta.TITLES[cid]} (vector tiles)",
                    **{"pmtiles:layers": [cid]})
    coll["links"] = links

    # Assets. Source and style assets are rebuilt rather than merged, so a
    # file that stops being used stops being advertised.
    assets = {k: v for k, v in coll.get("assets", {}).items()
              if not (k.startswith(("source-", "doc-", "styles/")))}
    assets.pop("documentation", None)

    # Self-heal an add/fix pass that left the pmtiles under the collection's
    # own key, clobbering the parquet asset: the key <cid> belongs to the
    # GeoParquet, tiles live under <cid>-tiles.
    if assets.get(cid, {}).get("href", "").endswith(".pmtiles"):
        assets[f"{cid}-tiles"] = assets.pop(cid)
    if (coll_dir / f"{cid}.parquet").exists() and not any(
            a.get("href", "") == f"./{cid}.parquet" for a in assets.values()):
        assets[cid] = {"href": f"./{cid}.parquet"}
        assets.move_to_end(cid, last=False) if hasattr(assets, "move_to_end") \
            else None

    for key, asset in assets.items():
        href = asset.get("href", "")
        if href.endswith(".parquet") or href.endswith("*.parquet"):
            asset["type"] = PARQUET_TYPE
            asset.setdefault("roles", ["data"])
            asset["title"] = (f"{meta.TITLES[cid]} (GeoParquet, "
                              f"{'52 state partitions' if cid == 'blocks' else 'national'})")
        elif href.endswith(".pmtiles"):
            asset["type"] = PMTILES_TYPE
            asset.setdefault("roles", ["visual"])
            asset["title"] = f"{meta.TITLES[cid]} (PMTiles)"
            asset["pmtiles:layers"] = [cid]
    if has_pmtiles and not any(
            a.get("href", "").endswith(".pmtiles") for a in assets.values()):
        assets[f"{cid}-tiles"] = {
            "href": f"./{cid}.pmtiles", "type": PMTILES_TYPE,
            "roles": ["visual"], "title": f"{meta.TITLES[cid]} (PMTiles)",
            "pmtiles:layers": [cid]}
    if (coll_dir / "thumbnail.png").exists():
        assets.setdefault("thumbnail", {
            "href": "./thumbnail.png", "type": "image/png",
            "roles": ["thumbnail"],
            "title": f"{meta.TITLES[cid]} rendered with the default style"})

    styles = style_assets(coll_dir)
    assets.update(styles)

    src_assets = meta.source_assets(cid)
    for asset in src_assets.values():
        asset.update(source_meta(asset["href"]))
    assets.update(src_assets)

    for asset in assets.values():
        stamp_asset(coll_dir, asset, checksums)
    coll["assets"] = assets

    f.write_text(json.dumps(coll, indent=2, ensure_ascii=False) + "\n")

    # Items (the block partitions): type, role, size and checksum.
    n_items = 0
    for item_path in sorted(coll_dir.glob("**/*.json")):
        if item_path.name == "collection.json" or "styles" in item_path.parts:
            continue
        try:
            item = json.loads(item_path.read_text())
        except json.JSONDecodeError:
            continue
        if item.get("type") != "Feature":
            continue
        for asset in item.get("assets", {}).values():
            if asset.get("href", "").endswith(".parquet"):
                asset["type"] = PARQUET_TYPE
                asset.setdefault("roles", ["data"])
            stamp_asset(item_path.parent, asset, checksums)
        item_path.write_text(json.dumps(item, indent=2,
                                        ensure_ascii=False) + "\n")
        n_items += 1

    cols = len(coll["table:columns"])
    return (f"✓ {rel}: {cols} columns described, "
            f"{len(src_assets)} source/doc assets, {len(styles)} styles, "
            f"{'pmtiles' if has_pmtiles else 'no pmtiles yet'}"
            + (f", {n_items} items" if n_items else "")
            + (f", {n:,} rows" if n else ""))


# --------------------------------------------------------------------------
# sub-catalogs and root
# --------------------------------------------------------------------------

def finalize_group(group: str) -> str:
    d = CATALOG / group
    f = d / "catalog.json"
    cat = json.loads(f.read_text()) if f.exists() else {
        "type": "Catalog", "stac_version": "1.1.0", "id": group}
    cat["type"] = "Catalog"
    cat.setdefault("stac_version", "1.1.0")
    cat["id"] = group
    cat["title"] = meta.GROUP_TITLES[group]
    cat["description"] = meta.GROUP_DESCRIPTIONS[group]
    cat["stac_extensions"] = sorted(
        set(cat.get("stac_extensions", [])) | {portolan_schema()})
    links = [l for l in cat.get("links", [])
             if l.get("rel") not in ("self", "child", "root", "parent")]
    ensure_link(links, "root", "../catalog.json", "application/json",
                root_title())
    ensure_link(links, "parent", "../catalog.json", "application/json",
                root_title())
    for cid in meta.GROUPS[group]:
        if (CATALOG / meta.COLL_REL[cid] / "collection.json").exists():
            links.append({"rel": "child",
                          "href": f"./{cid}/collection.json",
                          "type": "application/json",
                          "title": meta.TITLES[cid]})
    cat["links"] = links
    f.write_text(json.dumps(cat, indent=2, ensure_ascii=False) + "\n")
    n = sum(1 for l in links if l["rel"] == "child")
    return f"✓ {group}/catalog.json: {n} child collections"


def finalize_root() -> str:
    f = CATALOG / "catalog.json"
    cat = json.loads(f.read_text())
    # Everything hand-authored in the tracked root — id, title, description,
    # providers, the self/vcs/issues links — stays. Only the children are
    # this script's to own.
    links = [l for l in cat.get("links", []) if l.get("rel") != "child"]
    children = []
    for group in meta.GROUPS:
        if (CATALOG / group / "catalog.json").exists():
            children.append((f"./{group}/catalog.json",
                             meta.GROUP_TITLES[group]))
    for cid in ("counties", "states", "blocks"):
        if (CATALOG / cid / "collection.json").exists():
            children.append((f"./{cid}/collection.json", meta.TITLES[cid]))
    for href, title in children:
        links.append({"rel": "child", "href": href,
                      "type": "application/json", "title": title})
    cat["links"] = links
    f.write_text(json.dumps(cat, indent=2, ensure_ascii=False) + "\n")
    return f"✓ catalog.json: {len(children)} children"


# --------------------------------------------------------------------------
# upstream sizes
# --------------------------------------------------------------------------

STAGED = [ROOT / "staging" / "census-cache",
          ROOT / "staging" / "blocks-cache"]


def fetch_source_sizes() -> None:
    """HEAD every upstream source URL; record its size, and its checksum.

    Opt-in and cached, because it is the only network call in this script and
    a size nobody can verify is worse than no size. Directory listings are
    skipped — there is no single file to measure.

    The checksum is of the staged local copy, and only when that copy's
    length equals the `Content-Length` census.gov just served. That equality
    is what makes it honest to publish the hash as the hash of the upstream
    bytes; without a staged copy, the asset carries a size and no checksum.
    """
    import urllib.request

    urls = set()
    for cid in meta.ALL_COLLECTIONS:
        for asset in meta.source_assets(cid).values():
            if "source" in asset["roles"] and not asset["href"].endswith("/"):
                urls.add(asset["href"])
    try:
        recorded = json.loads(SOURCE_SIZES.read_text())
    except (OSError, json.JSONDecodeError):
        recorded = {}
    for url in sorted(urls):
        entry = recorded.get(url)
        if isinstance(entry, dict) and entry.get("checksum"):
            continue
        name = url.rsplit("/", 1)[-1]
        req = urllib.request.Request(url, method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                length = r.headers.get("Content-Length")
        except Exception as exc:  # noqa: BLE001 — a size is nice-to-have
            print(f"  (no size: {exc})  {url}")
            continue
        if not length:
            print(f"  (no Content-Length)  {url}")
            continue
        size = int(length)
        rec = {"size": size}
        for d in STAGED:
            p = d / name
            if p.is_file() and p.stat().st_size == size:
                rec["checksum"] = multihash(p)
                break
        recorded[url] = rec
        print(f"  {size:>14,}  {'sha256 ✓' if 'checksum' in rec else '        '}"
              f"  {name}")
    SOURCE_SIZES.parent.mkdir(parents=True, exist_ok=True)
    SOURCE_SIZES.write_text(json.dumps(recorded, indent=1, sort_keys=True))
    save_cache()
    hashed = sum(1 for v in recorded.values()
                 if isinstance(v, dict) and v.get("checksum"))
    print(f"✓ {len(recorded)} upstream sizes ({hashed} with a verified "
          f"checksum) in {SOURCE_SIZES.relative_to(ROOT)}")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Finalize STAC metadata for the US census catalog. Runs "
                    "AFTER `portolan add`; see the module docstring for the "
                    "full pipeline order.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Idempotent. Safe to re-run after any add/readme/style cycle.")
    ap.add_argument("collections", nargs="*", metavar="COLLECTION",
                    help="restrict to these collection ids "
                         f"(default: all — {', '.join(meta.ALL_COLLECTIONS)})")
    ap.add_argument("--no-checksums", action="store_true",
                    help="skip file:checksum (keeps file:size). Useful on a "
                         "first pass over the 5.2 GB of block partitions.")
    ap.add_argument("--fetch-source-sizes", action="store_true",
                    help="HEAD the upstream census.gov files and record their "
                         "Content-Length in staging/source_sizes.json, for "
                         "file:size on source assets. Network. Then exits.")
    args = ap.parse_args()

    if args.fetch_source_sizes:
        fetch_source_sizes()
        return

    targets = args.collections or meta.ALL_COLLECTIONS
    unknown = [c for c in targets if c not in meta.COLL_REL]
    if unknown:
        raise SystemExit(f"unknown collection id(s): {', '.join(unknown)}")

    problems = 0
    for cid in targets:
        line = finalize_collection(cid, checksums=not args.no_checksums)
        print(line)
        problems += line.startswith("✗")
    save_cache()
    for group in meta.GROUPS:
        if any(c in targets for c in meta.GROUPS[group]):
            print(finalize_group(group))
    if not args.collections:
        print(finalize_root())
    if problems:
        raise SystemExit(f"{problems} collection(s) not finalized")


if __name__ == "__main__":
    main()
