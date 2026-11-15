#!/usr/bin/env python3
"""QC the 25 themed PMTiles archives of the wide levels (2026-11-15).

For each archive: `tylertoo stats` (per-zoom sizes, max tile), then
`tylertoo decode` of the coarsest and the finest band into GeoParquet and a
value-for-value check against the parquet those tiles were built from.

  * the layer name is the collection id, which is what every generated
    style's source-layer expects;
  * no `*_moe` property survives in any tile and every `*_cv` column does;
  * a coarse-zoom tile's county values match catalog/counties/counties.parquet
    exactly (zcta-*/place-* band z0-5 on the Census Bureau's own county
    estimates; county-* carry those same counties as their own features, and
    state-*/cd-* carry their own polygons at every zoom, so for those the
    coarse check runs against the collection's own parquet);
  * a max-zoom feature matches the themed parquet exactly.

Writes staging/tiles-logs/<cid>.stats.txt per archive and a JSON summary at
staging/tiles-logs/wide-themes.tiles-qc.json.

    python3 tools/qc_wide_theme_tiles.py            # all 25
    python3 tools/qc_wide_theme_tiles.py cd-income  # one
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import duckdb

ROOT = Path("/Users/cholmes/repos/us-census-catalog")
TT = "/Users/cholmes/repos/tylertoo/target/release/tylertoo"
LOGDIR = ROOT / "staging" / "tiles-logs"
COUNTIES = ROOT / "catalog" / "counties" / "counties.parquet"
THEMES = ["income", "people", "housing", "connectivity", "wellbeing"]
# prefix -> (group, max zoom, coarse zoom, does the coarse band carry counties)
LEVELS = {
    "county": ("counties", 10, 2, True),
    "state": ("states", 8, 2, False),
    "zcta": ("zctas", 12, 3, True),
    "place": ("places", 12, 3, True),
    "cd": ("congressional-districts", 10, 2, False),
}
# A compared column must be one tiling does not touch: the geometry is
# simplified at coarse zooms and clipped at tile edges, the attributes are not.
CHECK_COLS = {"income": ["median_hh_income", "pct_below_poverty"],
              "people": ["pop_density", "pct_bachelors_plus"],
              "housing": ["median_home_value", "pct_vacant_units"],
              "connectivity": ["pct_no_internet", "pct_hh_no_vehicle"],
              "wellbeing": ["pct_uninsured", "median_hh_income_white_nh"]}


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"failed: {' '.join(map(str, cmd))}\n{r.stdout}\n{r.stderr}")
    return r.stdout


def stats(archive, cid):
    out = sh([TT, "stats", str(archive), "--largest", "5"])
    (LOGDIR / f"{cid}.stats.txt").write_text(out)
    per_zoom, tiles = {}, 0
    for line in out.splitlines():
        f = line.split()
        if len(f) == 7 and f[0].isdigit():
            per_zoom[int(f[0])] = int(f[6].replace(",", ""))
            tiles += int(f[1].replace(",", ""))
    return per_zoom, tiles


def decode(archive, zoom, tmp):
    out = Path(tmp) / f"z{zoom}.parquet"
    sh([TT, "decode", str(archive), str(out), "--zoom", str(zoom), "-f"])
    return out


def check(cid, theme, prefix, con, tmp):
    group, zmax, zcoarse, coarse_is_county = LEVELS[prefix]
    d = ROOT / "catalog" / group / cid
    archive, parquet = d / f"{cid}.pmtiles", d / f"{cid}.parquet"
    r = {"id": cid, "problems": []}
    bad = r["problems"].append

    per_zoom, tiles = stats(archive, cid)
    r["pmtiles_bytes"] = archive.stat().st_size
    r["max_tile_bytes"] = max(per_zoom.values())
    r["max_tile_zoom"] = max(per_zoom, key=per_zoom.get)
    r["zooms"] = f"{min(per_zoom)}-{max(per_zoom)}"
    r["tiles"] = tiles
    if max(per_zoom) != zmax:
        bad(f"deepest zoom is {max(per_zoom)}, expected {zmax}")

    fine = decode(archive, zmax, tmp)
    cols = [c[0] for c in con.execute(
        f"DESCRIBE SELECT * FROM read_parquet('{fine}')").fetchall()]
    r["tile_columns"] = len(cols)
    r["moe_in_tiles"] = [c for c in cols if c.endswith("_moe")]
    if r["moe_in_tiles"]:
        bad(f"_moe columns in tiles: {r['moe_in_tiles']}")
    pq_cv = [c[0] for c in con.execute(
        f"DESCRIBE SELECT * FROM read_parquet('{parquet}')").fetchall()
        if c[0].endswith("_cv")]
    r["cv_kept"] = sorted(set(pq_cv) & set(cols))
    if missing := sorted(set(pq_cv) - set(cols)):
        bad(f"_cv columns missing from tiles: {missing}")
    layers = [x[0] for x in con.execute(
        f"SELECT DISTINCT layer FROM read_parquet('{fine}')").fetchall()]
    r["layers"] = layers
    if layers != [cid]:
        bad(f"layer name(s) {layers}, expected ['{cid}']")

    # A max-zoom feature against the themed parquet, plus full coverage.
    sel = CHECK_COLS[theme]
    n_tile, n_pq = (con.execute(
        f"SELECT count(DISTINCT geoid) FROM read_parquet('{p}')").fetchone()[0]
        for p in (fine, parquet))
    r["max_zoom_geoids"] = {"tiles": n_tile, "parquet": n_pq}
    if n_tile != n_pq:
        bad(f"z{zmax} holds {n_tile} geoids, the parquet {n_pq}")
    mism = con.execute(f"""
        SELECT count(*) FROM (
          SELECT DISTINCT geoid, {', '.join(sel)} FROM read_parquet('{fine}')) t
        JOIN read_parquet('{parquet}') p USING (geoid)
        WHERE {' OR '.join(f'p.{c} IS DISTINCT FROM t.{c}' for c in sel)}
    """).fetchone()[0]
    r["max_zoom_mismatches"] = mism
    if mism:
        bad(f"{mism} max-zoom features disagree with the parquet on {sel}")
    r["max_zoom_spot"] = con.execute(
        f"SELECT geoid, {', '.join(sel)} FROM read_parquet('{fine}') "
        f"WHERE {sel[0]} IS NOT NULL ORDER BY geoid LIMIT 1").fetchone()

    # A coarse-zoom tile: for the pyramid archives (and county-*, whose own
    # features ARE counties) its values must equal counties.parquet exactly.
    coarse = decode(archive, zcoarse, tmp)
    src = COUNTIES if coarse_is_county else parquet
    n_coarse = con.execute(
        f"SELECT count(DISTINCT geoid) FROM read_parquet('{coarse}')"
    ).fetchone()[0]
    cmism = con.execute(f"""
        SELECT count(*) FROM (
          SELECT DISTINCT geoid, {', '.join(sel)}
          FROM read_parquet('{coarse}')) t
        JOIN read_parquet('{src}') p USING (geoid)
        WHERE {' OR '.join(f'p.{c} IS DISTINCT FROM t.{c}' for c in sel)}
    """).fetchone()[0]
    joined = con.execute(f"""
        SELECT count(*) FROM (SELECT DISTINCT geoid FROM
        read_parquet('{coarse}')) t JOIN read_parquet('{src}') p
        USING (geoid)""").fetchone()[0]
    r["coarse"] = {"zoom": zcoarse, "source": src.name, "geoids": n_coarse,
                   "joined": joined, "mismatches": cmism}
    if cmism:
        bad(f"{cmism} z{zcoarse} features disagree with {src.name} on {sel}")
    if not joined:
        bad(f"no z{zcoarse} geoid joins {src.name}")
    r["coarse_spot"] = con.execute(
        f"SELECT geoid, {', '.join(sel)} FROM read_parquet('{coarse}') "
        f"WHERE {sel[0]} IS NOT NULL ORDER BY geoid LIMIT 1").fetchone()
    return r


def main():
    want = sys.argv[1:]
    jobs = [(f"{p}-{t}", t, p) for p in LEVELS for t in THEMES
            if not want or f"{p}-{t}" in want]
    con = duckdb.connect()
    report, failed = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        for cid, theme, prefix in jobs:
            r = check(cid, theme, prefix, con, tmp)
            report.append(r)
            flag = "✓" if not r["problems"] else "✗"
            print(f"{flag} {cid:22s} {r['pmtiles_bytes']/1e6:>7.1f} MB  "
                  f"z{r['zooms']:<5s} {r['tiles']:>7,} tiles  max tile "
                  f"{r['max_tile_bytes']/1024:>7.1f} KB (z{r['max_tile_zoom']})"
                  f"  {r['tile_columns']} cols, {len(r['moe_in_tiles'])} _moe,"
                  f" {len(r['cv_kept'])} _cv  coarse "
                  f"{r['coarse']['joined']}/{r['coarse']['geoids']} joined "
                  f"{r['coarse']['mismatches']} bad  fine "
                  f"{r['max_zoom_mismatches']} bad")
            for p in r["problems"]:
                print(f"    ! {p}")
                failed += 1
    (LOGDIR / "wide-themes.tiles-qc.json").write_text(
        json.dumps(report, indent=1, default=str) + "\n")
    print(f"\n{len(report)} archive(s), {failed} problem(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
