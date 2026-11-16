#!/usr/bin/env python3
"""A tileset's real layer name must match what points at it.

Three artifacts name the vector layer of a PMTiles archive, and nothing
made them agree: the archive's own metadata, the `source-layer` of every
layer in each style, and the `pmtiles:layers` field of the STAC asset.

They disagreed once. tylertoo names a layer after the input file stem
unless told otherwise, so a collection tiled from a staging file called
`county-trends-2024.parquet` got the layer `county-trends-2024` while
its style asked for `county-trends`. Every filter matched zero features
and the map drew a blank page. Both the style and the STAC asset looked
correct in isolation, so only a cross-check finds it.

Needs the `pmtiles` CLI. Skips with a notice when it is absent, because
a missing tool must not look like a pass.

Run from the repository root.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"

if not shutil.which("pmtiles"):
    print("SKIP: the pmtiles CLI is not installed; layer names unchecked")
    sys.exit(0)


def tileset_layers(archive: Path) -> list[str]:
    out = subprocess.run(["pmtiles", "show", "--metadata", str(archive)],
                         capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        raise RuntimeError(f"pmtiles show failed: {out.stderr[:200]}")
    doc = json.loads(out.stdout)
    return [l["id"] for l in doc.get("vector_layers", [])]


failures: list[str] = []
checked = 0

for coll in sorted(CATALOG.rglob("collection.json")):
    doc = json.loads(coll.read_text())
    rel = coll.parent.relative_to(CATALOG)
    for asset in doc.get("assets", {}).values():
        href = asset.get("href", "")
        if not href.endswith(".pmtiles"):
            continue
        archive = (coll.parent / href).resolve()
        if not archive.is_file():
            continue
        checked += 1
        actual = set(tileset_layers(archive))

        claimed = set(asset.get("pmtiles:layers") or [])
        if claimed and not claimed <= actual:
            failures.append(
                f"{rel}: STAC claims pmtiles:layers {sorted(claimed)} but "
                f"the archive holds {sorted(actual)}")

        for style in sorted((coll.parent / "styles").glob("*.json")):
            doc_s = json.loads(style.read_text())
            want = {l.get("source-layer") for l in doc_s.get("layers", [])
                    if l.get("source-layer")}
            missing = want - actual
            if missing:
                failures.append(
                    f"{rel}/styles/{style.name}: source-layer "
                    f"{sorted(missing)} is not in the archive "
                    f"{sorted(actual)}. This style renders nothing")

if failures:
    for f in failures:
        print(f"  {f}")
    sys.exit(f"✗ {len(failures)} layer-name mismatch(es)")

print(f"OK: {checked} tileset(s) agree with their styles and STAC")
