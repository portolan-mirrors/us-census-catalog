# Build and publish runbook

Operational knowledge for this catalog. Read this before you change data
or republish. Each item here cost a debugging session to learn.

## Regeneration chain

Run these in order after any data change. The order matters.

1. `python3 tools/build_*.py` — whichever builder owns the data.
2. `python3 tools/make_tiles.py <ids>` — PMTiles.
3. `python3 tools/make_styles.py --measure <ids>` — styles and class breaks.
4. `python3 tools/collection_meta.py --write` — `.portolan/metadata.yaml`.
5. `portolan add <new collection parquet>` — only for a NEW collection.
6. `python3 tools/make_stac.py` — the finalizer. It owns collection.json.
7. `cd catalog && portolan readme` — generated READMEs.
8. `python3 tools/fix_readmes.py` — MANDATORY after step 7. See below.
9. `python3 tests/run_all.py` — all gates must pass.

## Source Cooperative

Use the AWS profile `source-coop-svc`. The global CLAUDE.md records why.
Do not pass `--endpoint-url`. The endpoints come from the
`[services source-coop-proxy]` block in `~/.aws/config`.

Metadata and small files go through `tools/publish.py`. Multi-GB files go
through `aws s3 cp` directly. Large uploads fail intermittently with SSL
protocol errors or HTTP 520. Retry the single file. The upload is
idempotent.

Publishing never deletes. A file removed from `catalog/` stays in the
bucket until someone deletes the object.

Verify a publish by size, not by exit code:

```bash
curl -sI "https://data.source.coop/portolan-mirrors/us-census-catalog/<path>" \
  | awk -F': ' 'tolower($1)=="content-length"{print $2}'
```

## Traps

**The wide tables moved, their data did not.** A wide all-indicators table
(`specs.WIDE_IDS`) keeps its `collection.json` in
`catalog/<group>/<group>/` while its parquet and pmtiles stay in
`catalog/<group>/`. The asset hrefs use `../`. This keeps every published
data URL stable. `make_stac.data_dir()` and `data_prefix()` encode the
rule. `collection_meta.data_url()` encodes it for prose.

**Always run fix_readmes.py.** `portolan readme` writes child links
relative to the catalog root, not to the README that holds them. Filed as
portolan-cli#1114. `tools/fix_readmes.py` repairs the links and injects
the cross-location nav line. It is idempotent.

**Assets are forbidden on a Catalog.** Rule PTL-AST-005. A group catalog
advertises its card image with a `preview` LINK, not a thumbnail asset.
stac-js falls back to the link.

**Collection extents are deliberate framing bboxes.** They are narrower
than the data. The data crosses the antimeridian and a true bbox makes map
clients open on the Atlantic. See docs/conformance.md and
portolan-browser#109. Do not "correct" these extents.

**Hive item files must be named for the data file stem.** Block partition
items are `state_fips=NN/NN.json`, not `state_fips=NN.json`. The CLI's
own `add` disagrees with its own scanner. Filed as portolan-cli#1112.

**Connecticut.** 2020 blocks carry the old 8-county GEOIDs. The 2024
boundary files use 9 planning regions. Match on the preserved 6-digit
tract number. The national total must stay 334,735,155.

**ACS jam values.** Any value at or below -111111111 is a jam code, not
data. Write NULL. The value -555555555 means a controlled estimate with
no sampling error. At state, county and congressional-district level the
whole population-share family carries it, so those margins are NULL by
design, not by a bug.

**Margins never reach the tiles.** Tiling excludes every `*_moe` property
and keeps every `*_cv`.

**Name the collections when you run build_acs.py.** A bare run rebuilds
all 42 collections, because the wide tables need every theme's columns.
The rebuild is value-neutral, which was verified in batch 2 by an EXCEPT
both ways against the published file, geometry included. It is not
byte-identical though, so it dirties files you did not mean to touch and
forces a larger republish. Pass explicit ids instead.

**A wide table's parquet belongs in the group directory.** `assemble()`
in `build_acs.py` wrote it to `catalog/<group>/<id>/<id>.parquet` after
the 2026-11-15 restructure, one level below where every published `../`
href points. Fixed with `out_dir_for()`. Check this path after any
change to the builder.

## Thumbnails

chiitiler renders them. Settings: conus bbox `-125,24,-66,50`, framed to
`-127.95,19.311379,-63.05,53.135244`, zoom 4.47, 1024x683 PNG,
`USE_BASEMAP=false`. A group catalog reuses one child's thumbnail.
Rendering is deterministic: the same inputs give a byte-identical PNG.

## Writing rules

A repository hook enforces Simplified Technical English on commit bodies,
issue bodies and pull request bodies. An issue also needs a label and the
form headings. Pass a body with `--body-file <path>`, where the path
exists before the command starts. A heredoc or `$(...)` will be refused.
