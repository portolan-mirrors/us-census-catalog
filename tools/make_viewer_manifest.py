#!/usr/bin/env python3
"""Generate apps/explorer/manifest.json and gazetteer.json from catalog/.

The explorer app loads one manifest instead of crawling 53 collections and
205 styles at startup. Re-run this script after any change to the catalog
metadata or styles. The script reads only the local tree plus, for the
trends class breaks and the gazetteer, the local GeoParquet through DuckDB.

Usage: python3 tools/make_viewer_manifest.py
"""
from __future__ import annotations

import json
import math
import posixpath
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
APP = ROOT / "apps" / "explorer"

PMTILES_TYPE = "application/vnd.pmtiles"
PARQUET_TYPE = "application/vnd.apache.parquet"

# The twelve trends indicators, with display metadata the app cannot derive
# from a column name alone. "unit": usd | pct | count | years.
TREND_INDICATORS = [
    ("population", "Population", "count"),
    ("median_hh_income", "Median household income", "usd"),
    ("per_capita_income", "Per capita income", "usd"),
    ("pct_below_poverty", "Poverty rate", "pct"),
    ("pct_unemployed", "Unemployment rate", "pct"),
    ("median_age", "Median age", "years"),
    ("pct_bachelors_plus", "Bachelor's degree or higher", "pct"),
    ("pct_people_of_color", "People of color", "pct"),
    ("households", "Households", "count"),
    ("pct_owner_occupied", "Owner-occupied share", "pct"),
    ("median_home_value", "Median home value", "usd"),
    ("median_gross_rent", "Median gross rent", "usd"),
]


def rel(path: Path) -> str:
    return path.relative_to(CATALOG).as_posix()


def resolve(base_dir: str, href: str) -> str:
    """Resolve an asset href against its collection directory."""
    return posixpath.normpath(posixpath.join(base_dir, href))


import re


def first_sentences(text: str, limit: int = 280) -> str:
    text = " ".join(text.split())
    # Markdown links and emphasis read as noise in the app's plain text.
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = text.replace("**", "").replace("`", "")
    if len(text) <= limit:
        return text
    cut = text[:limit]
    dot = cut.rfind(". ")
    return (cut[: dot + 1] if dot > 80 else cut.rstrip() + "…")


def load(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def duckdb_json(sql: str) -> list[dict]:
    out = subprocess.run(
        ["duckdb", "-json", "-c", sql],
        capture_output=True, text=True, check=True, cwd=ROOT,
    )
    return json.loads(out.stdout) if out.stdout.strip() else []


def nice(x: float) -> float:
    """Round to two significant digits so legend labels read cleanly."""
    if x == 0 or not math.isfinite(x):
        return 0.0
    exp = math.floor(math.log10(abs(x)))
    q = 10 ** (exp - 1)
    v = round(x / q) * q
    return round(v, max(0, -(exp - 1)))


def collection_entry(path: Path, group_id: str) -> dict:
    coll = load(path)
    base_dir = rel(path.parent)
    assets = coll.get("assets", {})
    entry: dict = {
        "title": coll.get("title", coll["id"]),
        "group": group_id,
        "dir": base_dir,
        "desc": first_sentences(coll.get("description", "")),
        "rows": coll.get("geoparquet:feature_count") or coll.get("table:row_count"),
        "bbox": coll["extent"]["spatial"]["bbox"][0],
        "cols": [c["name"] for c in coll.get("table:columns", [])],
        "data": [],
        "styles": [],
    }
    if (path.parent / "README.md").exists():
        entry["readme"] = base_dir + "/README.md"
    for key, a in assets.items():
        roles = a.get("roles") or []
        href = a.get("href", "")
        if a.get("type") == PMTILES_TYPE:
            entry["tiles"] = {
                "href": resolve(base_dir, href),
                "size": a.get("file:size"),
                "layer": (a.get("pmtiles:layers") or [coll["id"]])[0],
            }
        elif a.get("type") == PARQUET_TYPE and "data" in roles:
            entry["data"].append({
                "href": resolve(base_dir, href),
                "size": a.get("file:size"),
                "title": a.get("title", key),
                "glob": "*" in href,
            })
        elif "thumbnail" in roles:
            entry["thumb"] = resolve(base_dir, href)
        elif "style" in roles:
            sp = path.parent / href
            style = load(sp) if sp.exists() else {}
            meta = style.get("metadata", {})
            entry["styles"].append({
                "id": key,
                "href": resolve(base_dir, href),
                "title": a.get("title", key),
                "desc": a.get("description", "") or meta.get("description", ""),
                "column": meta.get("portolan:column"),
                "default": "default" in roles,
            })
    entry["styles"].sort(key=lambda s: (not s["default"], s["title"]))
    return entry


def trends_breaks(collections: dict) -> list[dict]:
    indicators = []
    files = {
        cid: str(ROOT / "catalog" / c["dir"]
                 / f"{posixpath.basename(c['dir'])}.parquet")
        for cid, c in collections.items() if c["group"] == "trends"
    }
    for col, label, unit in TREND_INDICATORS:
        ind = {"col": col, "label": label, "unit": unit,
               "breaks": {}, "chgBreaks": {}}
        for cid, f in files.items():
            qs = ", ".join(
                f"quantile_cont({col}, {q}) AS q{i}"
                for i, q in enumerate((1/7, 2/7, 3/7, 4/7, 5/7, 6/7))
            )
            row = duckdb_json(
                f"SELECT {qs} FROM read_parquet('{f}') WHERE {col} IS NOT NULL"
            )[0]
            breaks = sorted({nice(v) for v in row.values() if v is not None})
            ind["breaks"][cid] = breaks
            row = duckdb_json(
                f"SELECT quantile_cont(abs(chg_{col}), 0.5) AS a,"
                f" quantile_cont(abs(chg_{col}), 0.8) AS b,"
                f" quantile_cont(abs(chg_{col}), 0.95) AS c"
                f" FROM read_parquet('{f}') WHERE chg_{col} IS NOT NULL"
            )[0]
            a, b, c = (nice(row["a"] or 0), nice(row["b"] or 0), nice(row["c"] or 0))
            qpos = [v for v in dict.fromkeys([a, b, c]) if v > 0]
            ind["chgBreaks"][cid] = [-v for v in reversed(qpos)] + [0] + qpos
        indicators.append(ind)
    return indicators


def gazetteer() -> list[list]:
    rows: list[list] = []
    for level, f, zoom in (
        ("state", "catalog/states/states.parquet", None),
        ("county", "catalog/counties/counties.parquet", None),
    ):
        for r in duckdb_json(
            "SELECT name, state, geoid,"
            " bbox.xmin AS w, bbox.ymin AS s, bbox.xmax AS e, bbox.ymax AS n"
            f" FROM read_parquet('{f}') ORDER BY geoid"
        ):
            rows.append([
                level, r["name"], r["state"], r["geoid"],
                [round(r["w"], 3), round(r["s"], 3),
                 round(r["e"], 3), round(r["n"], 3)],
            ])
    return rows


def main() -> int:
    root_cat = load(CATALOG / "catalog.json")
    groups = []
    collections = {}
    for link in root_cat["links"]:
        if link["rel"] != "child":
            continue
        child_path = CATALOG / posixpath.normpath(link["href"])
        child = load(child_path)
        if child["type"] == "Collection":
            cid = child["id"]
            collections[cid] = collection_entry(child_path, cid)
            groups.append({"id": cid, "title": link.get("title", cid),
                           "collections": [cid]})
            continue
        gid = child["id"]
        members = []
        for cl in child["links"]:
            if cl["rel"] != "child":
                continue
            cpath = child_path.parent / posixpath.normpath(cl["href"])
            coll = load(cpath)
            collections[coll["id"]] = collection_entry(cpath, gid)
            members.append(coll["id"])
        groups.append({
            "id": gid,
            "title": child.get("title", gid),
            "desc": first_sentences(child.get("description", ""), 200),
            "collections": members,
        })

    manifest = {
        "title": root_cat.get("title", "US Census"),
        "updated": root_cat.get("updated"),
        "base": "https://data.source.coop/portolan-mirrors/us-census-catalog",
        "groups": groups,
        "collections": collections,
        "trends": {
            "collections": [cid for cid, c in collections.items()
                            if c["group"] == "trends"],
            "periods": ["2015-2019", "2020-2024"],
            "indicators": trends_breaks(collections),
        },
    }
    APP.mkdir(parents=True, exist_ok=True)
    with open(APP / "manifest.json", "w") as f:
        json.dump(manifest, f, separators=(",", ":"))
    with open(APP / "gazetteer.json", "w") as f:
        json.dump(gazetteer(), f, separators=(",", ":"))
    n_styles = sum(len(c["styles"]) for c in collections.values())
    print(f"manifest.json: {len(collections)} collections, "
          f"{len(groups)} groups, {n_styles} styles, "
          f"{(APP / 'manifest.json').stat().st_size:,} bytes")
    print(f"gazetteer.json: {(APP / 'gazetteer.json').stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
