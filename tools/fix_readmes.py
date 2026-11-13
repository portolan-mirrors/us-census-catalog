#!/usr/bin/env python3
"""Fix child links in the READMEs `portolan readme` generates.

For a grouped collection the generator writes hrefs relative to the
catalog root instead of the README's own directory (e.g.
`tracts/README.md` links `tracts/tract-income/`, and the root
`catalog/README.md` links `catalog/blocks/`), so every child link 404s
when the README is rendered at its published location. Run this after
every `portolan readme`. Upstream bug to file against portolan-cli;
remove this shim when the generator is fixed.
"""
import re
from pathlib import Path

CATALOG = Path(__file__).resolve().parent.parent / "catalog"

FIXES = [
    # (readme, wrong prefix in hrefs, right prefix)
    (CATALOG / "README.md", "](catalog/", "]("),
    (CATALOG / "block-groups" / "README.md", "](block-groups/", "]("),
    (CATALOG / "tracts" / "README.md", "](tracts/", "]("),
]


def main() -> None:
    for path, wrong, right in FIXES:
        if not path.exists():
            continue
        text = path.read_text()
        fixed = text
        # The generator doubles the prefix (`](tracts/tracts/…`), and one
        # str.replace pass only strips one layer; loop to a fixed point.
        while wrong in fixed:
            fixed = fixed.replace(wrong, right)
        # Collection titles in the group READMEs render as raw ids
        # ("tracts/tract-income"); strip the group prefix for readability.
        fixed = re.sub(r"### \[(?:block-groups|tracts)/([a-z-]+)\]",
                       r"### [\1]", fixed)
        if fixed != text:
            path.write_text(fixed)
            print(f"fixed {path.relative_to(CATALOG.parent)}")


if __name__ == "__main__":
    main()
