### What happened?

`portolan readme` writes child links with wrong path prefixes. The links are relative to the catalog root, not to the README that holds them.

Three cases from one catalog:

<!-- ste-ok: LONG_SENTENCE this list item is three short sentences, not one long one -->
1. The root README links a child as `catalog/blocks/`. The correct link from that file is `blocks/`. The `catalog/` prefix is the publish directory. That directory does not exist on the published host.
<!-- ste-ok: LONG_SENTENCE this list item is three short sentences, not one long one -->
2. A group README links its children with the group's own directory. `tracts/README.md` links `tracts/tract-income/`. The correct link from that file is `tract-income/`.
<!-- ste-ok: LONG_SENTENCE this list item is three short sentences, not one long one -->
3. A group that holds a same-named child doubles the prefix. `counties/README.md` links `counties/counties/county-income/`. The correct link from that file is `county-income/`.

### Why it matters

Every generated README ships broken navigation. On source.coop each wrong link resolves outside the catalog. A reader who clicks "blocks/" on the catalog's front page lands on a different account's page. Catalog authors must post-process every README after every `portolan readme` run. The `us-census-catalog` repository carries such a shim in `tools/fix_readmes.py`.

### Priority

P2

### How to reproduce

Reproduced 2026-11-15 with portolan 0.8.0 on `portolan-mirrors/us-census-catalog`.

1. Lay out a catalog with a group sub-catalog and child collections, for example `catalog/tracts/tract-income/`.
2. Run `portolan readme` from the catalog root.
3. Open `tracts/README.md`. The child link reads `tracts/tract-income/` instead of `tract-income/`.
4. Open the root `README.md`. The child links carry the `catalog/` publish-directory prefix.

### Implementation notes

The generator appears to build each href from the catalog root. It then writes that href into a README below the root. Build each href relative to the README's own directory instead. A test catalog with a group, and with a child named like its group, covers all three cases.

### How to confirm the fix

Run `portolan readme` on a catalog with the layout above. Every relative link in every generated README resolves against that README's own directory. No link carries the publish directory or the group directory as a prefix.

### Version

portolan 0.8.0, macOS (Apple Silicon), Python 3.
