#!/usr/bin/env python3
"""Every thumbnail asset must be a rendered card, not a placeholder.

`portolan add` writes a 396x158 JPEG next to each collection and
registers it under the `thumbnail` asset key. That satisfies the
conformance rule PTL-VIZ-001, which only asks that an asset with the
`thumbnail` role exists. It does not ask whether the image is the
collection's own map.

Six published collections shipped that placeholder before anyone
noticed, and a seventh group repeated it one batch later. The rule
cannot catch it, so this gate does: a thumbnail must be the PNG the
render pipeline writes, and it must be large enough to hold a map.

Run from the repository root.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"

# A conus render at 1024x683 is ~50 KB at the low end. The CLI
# placeholder is ~2.3 KB. Anything under this floor is not a map.
MIN_BYTES = 20_000

failures: list[str] = []
checked = 0

for coll in sorted(CATALOG.rglob("collection.json")):
    doc = json.loads(coll.read_text())
    rel = coll.parent.relative_to(CATALOG)
    thumbs = [a for a in doc.get("assets", {}).values()
              if "thumbnail" in (a.get("roles") or [])]
    if not thumbs:
        continue  # PTL-VIZ-001 owns the "missing entirely" case
    for asset in thumbs:
        href = asset.get("href", "")
        checked += 1
        if not href.endswith(".png"):
            failures.append(
                f"{rel}: thumbnail is {href}, not a rendered .png. "
                f"This is the portolan add placeholder; render the card "
                f"and rerun make_stac.py")
            continue
        path = (coll.parent / href).resolve()
        if not path.is_file():
            failures.append(f"{rel}: thumbnail {href} is not on disk")
            continue
        size = path.stat().st_size
        if size < MIN_BYTES:
            failures.append(
                f"{rel}: thumbnail is {size:,} bytes, below the "
                f"{MIN_BYTES:,} floor. A blank or placeholder image")

# A stray placeholder must not survive either. It is never referenced
# once a real card exists, and publishing it wastes a public URL.
for stray in sorted(CATALOG.rglob("*.thumb.jpg")):
    failures.append(
        f"{stray.relative_to(CATALOG)}: leftover placeholder; delete it")

if failures:
    for f in failures:
        print(f"  {f}")
    sys.exit(f"✗ {len(failures)} thumbnail problem(s)")

print(f"OK: {checked} thumbnail asset(s) are rendered cards")
