# us-census-catalog

A git-backed [Portolan](https://github.com/portolan-sdi/portolan-spec) catalog
mirroring United States Census Bureau demographics as cloud-native
**GeoParquet** + **PMTiles** with **STAC** metadata, published on
[Source Cooperative](https://source.coop/portolan-mirrors/us-census-catalog).

- Catalog root: `https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json`
- ACS 2020–2024 5-year indicators (income, poverty, age, race, education,
  housing, vehicles, commuting, internet) at **block group**, **tract**,
  **county**, and **state** level — every estimate with its margin of error,
  headline statistics with a reliability (CV) column
- 2020 Decennial Census counts at **block** level (the smallest census
  geography, ~8.1M polygons)
- Statistics ship in themed "chunks": each collection is one geography ×
  one theme, with its own GeoParquet, PMTiles, and 3–5 legend-bearing map
  styles. Coarse zooms aggregate into [A5](https://a5geo.org/) cells so the
  national view shows all the data, not a thinned subset.
- A mirror that liberally references the source:
  [data.census.gov](https://data.census.gov/) is authoritative, and every
  collection links the exact upstream files it was built from

## Repository layout

| Path | Purpose |
|---|---|
| `catalog/` | The published tree — synced 1:1 to Source Cooperative. Parquet/PMTiles are generated, gitignored artifacts. |
| `staging/` | Downloaded census source files (gitignored) |
| `tools/` | The pipeline (fetch → build → tile → style → document) |
| `tests/` | Conformance and consistency gates |
| `docs/` | Design notes and data profiles |

## Pipeline

Run from the repo root, in order:

| Step | Command | What it does |
|---|---|---|
| 1 | `bash tools/download_sources.sh` | ACS table-based Summary File tables, cartographic boundary files, TIGER blocks, PL 94-171 (plain HTTPS, no API key) into `staging/` |
| 2 | `python3 tools/build_acs.py` | Parse national ACS tables, compute indicators with Census MOE formulas, join to boundary geometry → GeoParquet per collection |
| 3 | `python3 tools/make_tiles.py` | PMTiles per collection via [tylertoo](https://github.com/geoparquet-io/tylertoo), with A5 cell aggregation at coarse zooms |
| 4 | `python3 tools/make_stac.py` | STAC collections: column descriptions, providers, source assets, styles |
| 5 | `python3 tools/make_styles.py` | MapLibre styles with legends, class breaks measured from national distributions |
| 6 | `python3 tests/run_all.py` | Gates |
| 7 | `python3 tools/publish.py --confirm` | Publish to Source Cooperative |

## Licensing

Census Bureau data is a U.S. Government work in the public domain; this
mirror is published as **CC0-1.0**. See the Bureau's
[open data policy](https://www.census.gov/about/policies/open-gov/open-data.html)
and cite the U.S. Census Bureau when you use the numbers.

## Related

- Pattern sibling: [tge-labs/st-louis-open-data-mirror](https://source.coop/tge-labs/st-louis-open-data-mirror) (the city-scale ancestor of this pipeline)
- [Portolan spec](https://github.com/portolan-sdi/portolan-spec)
