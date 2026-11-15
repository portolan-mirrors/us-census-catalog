# Batch 1 spec: reference layers (classification + crosswalks)

Add a new group `catalog/reference/` with four collections. These are
reference geography, not demographic statistics, so they stay out of the
seven geography groups.

| collection | source | note |
|---|---|---|
| `urban-areas` | TIGER2024 UAC20 (1 national zip, 70 MB) | 2020 urban area delineation |
| `landmarks-area` | TIGER2024 AREALM (56 state zips, 67 MB) + MIL (1 zip, 3 MB) | polygons; add a `landmark_kind` column = 'landmark' or 'military' |
| `landmarks-point` | TIGER2024 POINTLM (56 state zips, 28 MB) | points |
| `crosswalks` | 2020 relationship files under geo/docs/maps-data/data/rel2020/ | TABULAR, no geometry |

Sources:
- https://www2.census.gov/geo/tiger/TIGER2024/<PRODUCT>/
- https://www2.census.gov/geo/docs/maps-data/data/rel2020/  (subdirs:
  t10t20, tract, blkgrp, place, cousub, cbsa, zcta520, ua, puma520, aiannh)

`crosswalks` carries every rel2020 table, each as its own parquet in the
collection directory, named for the relationship (e.g. `t10t20-tract.parquet`).
t10t20 is the one that matters most: it maps 2010 tracts to 2020 tracts and
is what later trend work will depend on.

## Rules

- Decompress each zip in its own empty directory. Never run an interpreter
  from inside one.
- Convert to GeoParquet with the SAME conventions as the existing
  collections. Read `tools/build_wide_themes.py` for the exact write path
  (pyarrow, zstd, row_group_size, bbox covering, geo metadata) and reuse it.
  Verify the output schema conventions against
  `catalog/counties/county-income/county-income.parquet`.
- Keep the source CRS. Sort spatially (gpio sort hilbert --add-bbox) as
  `tools/build_blocks.py` does.
- Carry a `state` USPS column where the source is per-state.
- Decode MTFCC codes to a readable `feature_type` column using the Census
  MTFCC list; cite the URL you decoded from in processing_notes. Do not
  invent a meaning for a code you cannot source.
- Tiles: PMTiles for the three spatial collections via `tools/make_tiles.py`
  (follow the existing GEOM_LEVELS pattern; these are small). No pyramid.
  No tiles for `crosswalks` (tabular).
- Styles: `tools/make_styles.py`, one default + up to 3 per spatial
  collection, class breaks measured from the data, every `match` branch
  verified non-empty. Urban areas style on the UATYPE20/urban-rural class;
  landmarks on `feature_type`.
- STAC/docs: extend `tools/collection_meta.py` and `tools/column_docs.py`
  so the generators produce the metadata. DO NOT hand-write 30-page
  AGENTS.md files. One concise AGENTS.md per collection plus one for the
  group, each with at most 4 recipes, and every recipe RUN before you write
  it. Reuse the existing templated prose patterns.
- `tools/make_stac.py` must need no edits beyond what the generators feed
  it. If it does, make the smallest possible change and say so.

## Boundaries

- Do not touch anything under catalog/blocks, block-groups, tracts,
  counties, states, zctas, places, congressional-districts.
- Do not edit tools/build_acs.py, tools/specs.py, tools/publish.py.
- Do not git commit, push, publish, or upload. Do not render thumbnails.
- Run `python3 tests/run_all.py` at the end. PTL-VIZ-001 thumbnail errors
  on the new collections are expected and fine; nothing else may fail.

## Report

One table: collection, rows, columns, parquet MB, pmtiles MB, QC result.
Plus: which MTFCC codes you could not source, and any deviation from
this spec.
