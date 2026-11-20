# us-census-catalog

A git-backed [Portolan](https://github.com/portolan-sdi/portolan-spec) catalog
mirroring United States Census Bureau demographics as cloud-native
**GeoParquet** + **PMTiles** with **STAC** metadata, published on
[Source Cooperative](https://source.coop/portolan-mirrors/us-census-catalog).

- Catalog root: `https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json`
- **Explore it in the [Census Atlas](https://portolan-mirrors.github.io/us-census-catalog/)** —
  the catalog's own zero-build map explorer (`apps/explorer/`): every
  collection with its curated styles and legends, 2015–2019 → 2020–2024
  change maps with animated and swipe comparison, place/dataset search,
  and copyable download + DuckDB snippets per collection
- ACS 2020–2024 5-year indicators (income, poverty, age, race, education,
  housing, vehicles, commuting, internet, health insurance, disability,
  nativity) at **block group**, **tract**, **county**, **state**, **ZCTA**,
  **place** and **congressional district** level — every estimate with its
  margin of error, headline statistics with a reliability (CV) column
- 2020 Decennial Census counts at **block** level (the smallest census
  geography, ~8.1M polygons)
- Statistics ship in themed "chunks": each collection is one geography ×
  one theme (income, people, housing, connectivity, wellbeing), with its own
  GeoParquet, PMTiles, and 3–5 legend-bearing map styles. Every geography is
  a sub-catalog of those chunks, and the five coarse-or-sparse ones —
  counties, states, ZCTAs, places, congressional districts — add a sixth
  collection carrying all 112 columns in one wide table for a question that
  crosses themes. Coarse zooms of a PMTiles archive step up to a coarser
  census geography — counties at z0–z5, tracts in the middle — carrying the
  Census Bureau's own estimates for those geographies, so the national view
  shows official values for every part of the country rather than a thinned
  subset of the fine features.
- A mirror that liberally references the source:
  [data.census.gov](https://data.census.gov/) is authoritative, and every
  collection links the exact upstream files it was built from

## Quick start

No download, no API key, no sign-up — DuckDB range-reads the columns it needs
straight out of the published GeoParquet:

```sql
INSTALL httpfs; LOAD httpfs;

-- The richest counties in the country, with the unreliable estimates filtered out
SELECT name, population, median_hh_income
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet'
WHERE population > 100000 AND median_hh_income_cv < 0.05
ORDER BY median_hh_income DESC
LIMIT 5;
```

```
Loudoun County, Virginia        |  432998 | 181765.0
Santa Clara County, California  | 1902047 | 164281.0
San Mateo County, California    |  742340 | 158855.0
Fairfax County, Virginia        | 1147837 | 153637.0
Howard County, Maryland         |  336328 | 149763.0
```

Run against the published URL with DuckDB 1.4.1 on 2026-11-13: **about 5
seconds**, no file on disk. `median_hh_income_cv` is the reliability column — every headline
statistic has one, and `< 0.05` is what keeps a county of four thousand people
out of a national ranking. Swap `counties/counties.parquet` for
`states/states.parquet`, `places/places.parquet`, `zctas/zctas.parquet`,
`congressional-districts/congressional-districts.parquet`, or for any themed
chunk at `<geography>/<chunk>/<chunk>.parquet` — say
`counties/county-income/county-income.parquet`, which is the same rows with
23 columns instead of 112. Add `WHERE state = 'XX'` for one state; add
`LOAD spatial;` to get
`geometry` back as a `GEOMETRY` for point-in-polygon and distance work.

Then read the agent guides, which carry the join keys, the NULL stories, and
4–5 tested recipes per collection with their real output:

- [`catalog/AGENTS.md`](catalog/AGENTS.md) — cross-collection showcase queries
  and which collection answers which question
- [`catalog/<geography>/AGENTS.md`](catalog/) — what the six collections at
  one geography share, and when to step up or down a level
- [`catalog/<geography>/<collection>/AGENTS.md`](catalog/) — per-collection
  schema, quirks and recipes
- [`catalog/llms.txt`](catalog/llms.txt) — the one-page orientation for an
  automated client

## Repository layout

| Path | Purpose |
|---|---|
| `catalog/` | The published tree — synced 1:1 to Source Cooperative. Parquet/PMTiles are generated, gitignored artifacts. |
| `apps/explorer/` | The [Census Atlas](https://portolan-mirrors.github.io/us-census-catalog/) viewer — deployed to GitHub Pages by `.github/workflows/pages.yml`, reads the published catalog over HTTPS |
| `staging/` | Downloaded census source files (gitignored) |
| `tools/` | The pipeline (fetch → build → tile → style → document) |
| `tests/` | Conformance and consistency gates |
| `docs/` | Design notes and data profiles |

## Pipeline

Run from the repo root, in order:

| Step | Command | What it does |
|---|---|---|
| 1 | `bash tools/download_sources.sh`<br>`bash tools/download_blocks.sh` | ACS table-based Summary File tables, cartographic boundary files, TIGER blocks, PL 94-171 (plain HTTPS, no API key) into `staging/` |
| 2 | `python3 tools/build_acs.py` | Parse national ACS tables, compute indicators with Census MOE formulas, join to boundary geometry → GeoParquet per collection |
| 3 | `python3 tools/build_blocks.py` | 2020 PL 94-171 counts joined to TIGER blocks → `catalog/blocks/`, hive-partitioned by state |
| 3b | `python3 tools/build_wide_themes.py --all` | Column-prune each wide all-indicators table into its five themed child collections (same rows, same values — nothing recomputed) |
| 4 | `python3 tools/build_tile_staging.py`<br>`python3 tools/make_tiles.py --all` | PMTiles per collection via [tylertoo](https://github.com/geoparquet-io/tylertoo) `pyramid`: counties at z0–z5, tracts at the mid zooms, the collection's own features at the close zooms. The staging step builds the coarse-band inputs under `staging/agg/` |
| 5 | `python3 tools/collection_meta.py --write` | `.portolan/metadata.yaml` per collection — titles, descriptions, processing notes, known issues. Must precede `portolan add`, which reads them |
| 6 | `portolan add catalog/<collection>/ …` | The CLI writes each `collection.json` (and the 52 block items) |
| 7 | `python3 tools/make_styles.py` | MapLibre styles with legends, class breaks measured from national distributions |
| 8 | `python3 tools/make_stac.py` | Finalizes the STAC: a description for every column (verified against the parquet schema), providers, license, source assets, tiles and style assets, checksums, extents, sub-catalogs |
| 9 | `python3 tests/run_all.py` | Gates |
| 10 | `python3 tools/publish.py --confirm` | Publish to Source Cooperative |

Documentation lives in three modules: [`tools/column_docs.py`](tools/column_docs.py)
(every column — universe quoted from the ACS table shells, table linked, derivation
named), [`tools/collection_meta.py`](tools/collection_meta.py) (titles, descriptions,
keywords, upstream source assets, `metadata.yaml`), and each collection's own
`AGENTS.md`. `make_stac.py` fails the build if a column in a published parquet has no
description.

## Licensing

Census Bureau data is a U.S. Government work in the public domain; this
mirror is published as **CC0-1.0**. See the Bureau's
[open data policy](https://www.census.gov/about/policies/open-gov/open-data.html)
and cite the U.S. Census Bureau when you use the numbers.

## Related

- Pattern sibling: [tge-labs/st-louis-open-data-mirror](https://source.coop/tge-labs/st-louis-open-data-mirror) (the city-scale ancestor of this pipeline)
- [Portolan spec](https://github.com/portolan-sdi/portolan-spec)
