# 2020 Census Counts — Blocks

2020 Decennial Census counts for all **8,174,955** census blocks in the 50 states, the District of Columbia and Puerto Rico — the smallest geography the Census Bureau publishes anything for. From the [2020 Census P.L. 94-171 Redistricting Data Summary Files](https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html): total population and the seven race-alone counts plus two or more races ([P1](https://data.census.gov/table/DECENNIALPL2020.P1)), Hispanic or Latino and White-alone-not-Hispanic ([P2](https://data.census.gov/table/DECENNIALPL2020.P2)), the voting-age population 18 and over ([P3](https://data.census.gov/table/DECENNIALPL2020.P3)), housing units occupied and vacant ([H1](https://data.census.gov/table/DECENNIALPL2020.H1)), and the group-quarters population ([P5](https://data.census.gov/table/DECENNIALPL2020.P5)), with derived shares and population density.

These are **complete counts, not survey estimates**, so there are no margins of error and no coefficients of variation — the `*_moe` and `*_cv` columns the ACS collections carry do not exist here. They are, however, protected by the 2020 disclosure-avoidance system, which injects noise at block level while holding state totals exact: block counts are reliable in aggregate and should be read with care one block at a time. The Census Bureau publishes no income, education or commuting data at block level — for that, move up to the [block-group collections](../block-groups/catalog.json).

Roughly three in ten census blocks are unpopulated by design (28.97% have `pop_total = 0`, measured), so `pct_white_nh`, `pct_black` and `pct_hispanic` are NULL on that share of rows, and `pct_vacant` is NULL on the 27.64% with no housing units. That is a property of census blocks, not missing data: filter `pop_total > 0` before averaging a rate. Summed over the 50 states and DC, `pop_total` equals 331,449,281 — the published 2020 resident population, exactly; Puerto Rico equals 3,285,874.

Geometry is [TIGER/Line 2024 `TABBLOCK20`](https://www2.census.gov/geo/tiger/TIGER2024/TABBLOCK20/), not the cartographic boundary files the ACS collections use, because no cartographic edition is published for blocks. TIGER is unclipped, so a coastal block extends to the 3-mile limit rather than the shoreline, and `aland_sqkm` comes from the file's own `ALAND20` land-area field (water-only blocks have `ALAND20 = 0` and so a NULL `pop_density`). Field positions in the P.L. 94-171 files are pinned against the Census Bureau's own [R import scripts](https://www2.census.gov/programs-surveys/decennial/rdo/about/2020-census-program/Phase3/SupportMaterials/2020PL_R_import_scripts.zip) rather than read off a PDF — see the build notes in the repository for the field table and the three independent checks behind it.

The collection is **hive-partitioned by state**: 52 parquet files under `state_fips=<FIPS>/`, one STAC item each with its own bbox and row count, queryable as one table through the glob `state_fips=*/*.parquet` with `hive_partitioning=true`. The synthesized `state_fips` key carries the numeric FIPS code and sits alongside the `state` column's USPS code. Pull one state and you download one file.

The PMTiles archive carries the same columns as the GeoParquet. At feature zooms the tiles are the census geographies; at coarse zooms they are [A5](https://a5geo.org/) cell aggregations built by [tylertoo](https://github.com/geoparquet-io/tylertoo) — counts summed, rates and medians averaged unweighted over the geographies in the cell — because thinning hundreds of thousands of polygons at a national zoom would show a biased subset (small urban geographies drop first) rather than less data. Cell and feature zooms share column names, so one style expression classifies both. The aggregation is a visualization aid: statistics come from the GeoParquet, never from the tiles.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![2020 Census](https://img.shields.io/badge/2020_Census-blue) ![decennial census](https://img.shields.io/badge/decennial_census-blue) ![P.L. 94-171](https://img.shields.io/badge/P.L._94--171-blue) ![redistricting](https://img.shields.io/badge/redistricting-blue) ![population](https://img.shields.io/badge/population-blue) ![race](https://img.shields.io/badge/race-blue) ![ethnicity](https://img.shields.io/badge/ethnicity-blue) ![voting age population](https://img.shields.io/badge/voting_age_population-blue) ![housing occupancy](https://img.shields.io/badge/housing_occupancy-blue) ![group quarters](https://img.shields.io/badge/group_quarters-blue) ![United States](https://img.shields.io/badge/United_States-blue)

## Spatial Coverage

- **Bounding Box**: [-179.231086, 17.831518837698233, 179.85968107125612, 71.439786]

## Temporal Coverage

- **Start**: 2020-04-01T00:00:00Z
- **End**: 2020-04-01T00:00:00Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | 15-character 2020 census block GEOID — state (2) + county (3) + tract (6) + block (4), e.g. `020130001001000`. The geoheader's `GEOCODE` field, not its `GEOID` (which carries a `7500000US` summary-level prefix); the build asserts `GEOCODE == STATE || COUNTY || TRACT || BLOCK` on every row. `substr(geoid, 1, 12)` is the block group, so blocks join the ACS block-group collections by prefix. |
| state | string | Two-letter USPS state or territory code (`MO`, `PR`, `GU`). Carried on every collection from the `STATEFP → USPS` lookup embedded in `tools/specs.py` rather than read off the boundary files, because the 2024 cartographic boundary block-group file has no `STUSPS` column while the tract, county and state files do. In the block collection this sits alongside the hive partition key `state_fips`, which carries the numeric FIPS code. |
| pop_total | int32 | Total population of the block, from the 2020 Decennial Census. Universe: total population. Table P1, cell 1 (`P0010001`) of [P1](https://data.census.gov/table/DECENNIALPL2020.P1). Read from the 2020 P.L. 94-171 redistricting file at the field position pinned in `docs/blocks-build-notes.md` against the Census Bureau's own R import scripts. A complete count, not a survey estimate, so there is no margin of error — but it is protected by the 2020 disclosure-avoidance system, which injects noise at the block level and exact-counts states. Blocks tile their state exhaustively: summed over the 50 states and DC this column equals 331,449,281, the published 2020 resident population, exactly. 28.97% of all 8,174,955 blocks have a population of 0 (measured). |
| pop_white | int32 | Population reporting White alone. Universe: total population. Table P1, cell 3 (`P0010003`) of [P1](https://data.census.gov/table/DECENNIALPL2020.P1) — a race-alone count, crossing Hispanic origin, so it is not comparable to `pop_white_nh`. |
| pop_black | int32 | Population reporting Black or African American alone. Universe: total population. Table P1, cell 4 (`P0010004`) of [P1](https://data.census.gov/table/DECENNIALPL2020.P1). Race alone, crossing Hispanic origin. |
| pop_aian | int32 | Population reporting American Indian and Alaska Native alone. Universe: total population. Table P1, cell 5 (`P0010005`) of [P1](https://data.census.gov/table/DECENNIALPL2020.P1). |
| pop_asian | int32 | Population reporting Asian alone. Universe: total population. Table P1, cell 6 (`P0010006`) of [P1](https://data.census.gov/table/DECENNIALPL2020.P1). |
| pop_nhpi | int32 | Population reporting Native Hawaiian and Other Pacific Islander alone. Universe: total population. Table P1, cell 7 (`P0010007`) of [P1](https://data.census.gov/table/DECENNIALPL2020.P1). |
| pop_other | int32 | Population reporting Some Other Race alone. Universe: total population. Table P1, cell 8 (`P0010008`) of [P1](https://data.census.gov/table/DECENNIALPL2020.P1). |
| pop_two_plus | int32 | Population reporting two or more races. Universe: total population. Table P1, cell 9 (`P0010009`) of [P1](https://data.census.gov/table/DECENNIALPL2020.P1). The seven race-alone columns plus this one sum exactly to `pop_total`; P1's cell 2 ("Population of one race") is an intermediate subtotal and is deliberately not carried, which is why the sum closes. |
| pop_hispanic | int32 | Population of Hispanic or Latino origin, of any race. Universe: total population. Table P2, cell 2 (`P0020002`) of [P2](https://data.census.gov/table/DECENNIALPL2020.P2). Hispanic origin is asked separately from race, so this crosses all seven race columns. |
| pop_white_nh | int32 | Population reporting White alone and not Hispanic or Latino. Universe: total population. Table P2, cell 5 (`P0020005`) of [P2](https://data.census.gov/table/DECENNIALPL2020.P2) — the not-Hispanic branch, so this is a subset of `pop_white` and the two are not interchangeable. |
| vap_total | int32 | Voting-age population: people 18 years and over. Universe: population 18 years and over. Table P3, cell 1 (`P0030001`) of [P3](https://data.census.gov/table/DECENNIALPL2020.P3). The table this column comes from is the one P.L. 94-171 exists to publish — the race detail behind redistricting — and `pop_total − vap_total` is the under-18 population. |
| housing_units | int32 | Total housing units in the block, occupied and vacant. Universe: housing units. Table H1, cell 1 (`H0010001`) of [H1](https://data.census.gov/table/DECENNIALPL2020.H1). A complete count of units, not of households. |
| housing_occupied | int32 | Occupied housing units. Universe: housing units. Table H1, cell 2 (`H0010002`) of [H1](https://data.census.gov/table/DECENNIALPL2020.H1). `housing_occupied + housing_vacant == housing_units` holds on every block in this collection; the build checks it (0 violations). |
| housing_vacant | int32 | Vacant housing units. Universe: housing units. Table H1, cell 3 (`H0010003`) of [H1](https://data.census.gov/table/DECENNIALPL2020.H1). Includes seasonal, for-rent and for-sale units, so it is not a measure of abandonment. |
| group_quarters_pop | int32 | Population living in group quarters — correctional facilities, juvenile facilities, nursing facilities, college/university housing, military quarters, other group quarters. Universe: population in group quarters. Table P5, cell 1 (`P0050001`) of [P5](https://data.census.gov/table/DECENNIALPL2020.P5). Group-quarters residents are included in `pop_total` but live in no housing unit, which is how a block can hold hundreds of people and few or no units. |
| pct_white_nh | double | `pop_white_nh` as a percent of `pop_total`, 2 decimals. Universe: total population. NULL where `pop_total` is 0 — 28.97% of blocks (measured), because roughly three in ten census blocks are unpopulated by design. That is a property of census blocks, not missing data: filter `pop_total > 0` before averaging. |
| pct_black | double | `pop_black` as a percent of `pop_total`, 2 decimals. Universe: total population — and note the numerator is race-alone, crossing Hispanic origin, unlike the ACS collections' `pct_black`. NULL where `pop_total` is 0 (28.97% of blocks, measured). |
| pct_hispanic | double | `pop_hispanic` as a percent of `pop_total`, 2 decimals. Universe: total population. NULL where `pop_total` is 0 (28.97% of blocks, measured). |
| pct_vacant | double | `housing_vacant` as a percent of `housing_units`, 2 decimals. Universe: housing units. NULL where the block has no housing units — 27.64% of blocks (measured). |
| pop_density | double | People per square kilometre of land area, rounded to 1 decimal: `pop_total / aland_sqkm`. NULL where `ALAND20` is 0 — a water-only block has no land to divide by; 2.92% of the 8,174,955 blocks are NULL on this column (measured). |
| aland_sqkm | double | Land area in square kilometres, rounded to 3 decimals. `ALAND20 / 1e6` from the TIGER/Line 2024 block file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. TIGER/Line 2024 `TABBLOCK20`, which is **not** shoreline-clipped: a coastal block extends to the 3-mile limit. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |
| state_fips | string | Hive partition key, synthesized from the directory name when the `state_fips=*/*.parquet` glob is read — the 2-digit state FIPS code of the partition. Not a column in the parquet files themselves. Named `state_fips` rather than `state` so it does not shadow the USPS `state` column. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./blocks.pmtiles | 6.7 GB | 1220a6cad2bf... |
| ./state_fips=*/*.parquet | - | - |
| ./items.parquet | 50.5 KB | 1220532d3bc5... |
| ./styles/black-share.json | 2.1 KB | 122033e39965... |
| ./styles/default.json | 1.9 KB | 1220b991a401... |
| ./styles/hispanic-share.json | 2.1 KB | 12201b3ef825... |
| ./styles/vacancy.json | 2.1 KB | 1220f1f940ba... |
| ./styles/white-share.json | 2.2 KB | 1220f4c680bf... |
| https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/ | - | - |
| https://www2.census.gov/geo/tiger/TIGER2024/TABBLOCK20/ | - | - |
| https://www2.census.gov/programs-surveys/decennial/rdo/about/2020-census-program/Phase3/SupportMaterials/2020PL_R_import_scripts.zip | 10.5 KB | - |
| https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/summary-file/2020Census_PL94_171Redistricting_StatesTechDoc_English.pdf | - | - |
| https://www.census.gov/programs-surveys/geography/about/glossary.html | - | - |
| state_fips=01/01.parquet | 117.0 MB | 122020d8aa99... |
| state_fips=02/02.parquet | 67.3 MB | 12201a386ae6... |
| state_fips=04/04.parquet | 96.3 MB | 122074eea609... |
| state_fips=05/05.parquet | 104.6 MB | 1220b0b4b05e... |
| state_fips=06/06.parquet | 306.8 MB | 1220a71b7b96... |
| state_fips=08/08.parquet | 106.8 MB | 1220a4a69f25... |
| state_fips=09/09.parquet | 27.5 MB | 12201b110054... |
| state_fips=10/10.parquet | 9.4 MB | 1220236983a1... |
| state_fips=11/11.parquet | 1.9 MB | 1220b8bbcb48... |
| state_fips=12/12.parquet | 151.6 MB | 12204f3dee02... |
| state_fips=13/13.parquet | 133.7 MB | 1220f55fa694... |
| state_fips=15/15.parquet | 11.5 MB | 1220fab77a63... |
| state_fips=16/16.parquet | 99.7 MB | 122029cf9cf6... |
| state_fips=17/17.parquet | 125.2 MB | 12202f820d17... |
| state_fips=18/18.parquet | 83.8 MB | 1220b12e7b00... |
| state_fips=19/19.parquet | 69.0 MB | 1220e3969ac3... |
| state_fips=20/20.parquet | 68.2 MB | 12202d41eb6c... |
| state_fips=21/21.parquet | 128.5 MB | 122010ff637d... |
| state_fips=22/22.parquet | 92.4 MB | 1220c1b1c936... |
| state_fips=23/23.parquet | 55.6 MB | 1220236b2255... |
| state_fips=24/24.parquet | 50.1 MB | 12204f90a49d... |
| state_fips=25/25.parquet | 46.3 MB | 122004db8d5e... |
| state_fips=26/26.parquet | 95.4 MB | 12202be96600... |
| state_fips=27/27.parquet | 121.1 MB | 122074350049... |
| state_fips=28/28.parquet | 95.2 MB | 1220ef0ae9ef... |
| state_fips=29/29.parquet | 155.2 MB | 1220b6f9705b... |
| state_fips=30/30.parquet | 123.6 MB | 1220066b484a... |
| state_fips=31/31.parquet | 39.5 MB | 1220f70943e8... |
| state_fips=32/32.parquet | 63.6 MB | 12205bed35ed... |
| state_fips=33/33.parquet | 20.9 MB | 1220985b64f0... |
| state_fips=34/34.parquet | 52.0 MB | 1220f01a7470... |
| state_fips=35/35.parquet | 83.0 MB | 1220cf9a6645... |
| state_fips=36/36.parquet | 144.5 MB | 1220f0e2620e... |
| state_fips=37/37.parquet | 163.1 MB | 12206f74440c... |
| state_fips=38/38.parquet | 39.1 MB | 1220076bc767... |
| state_fips=39/39.parquet | 120.6 MB | 122078629bf3... |
| state_fips=40/40.parquet | 87.2 MB | 122032adb697... |
| state_fips=41/41.parquet | 153.2 MB | 1220600c2ee8... |
| state_fips=42/42.parquet | 183.2 MB | 1220aaac4da1... |
| state_fips=44/44.parquet | 12.2 MB | 1220d36be2c6... |
| state_fips=45/45.parquet | 89.0 MB | 1220560918c6... |
| state_fips=46/46.parquet | 46.1 MB | 12205d6bb9d2... |
| state_fips=47/47.parquet | 150.6 MB | 1220235780b9... |
| state_fips=48/48.parquet | 334.6 MB | 12206e40ac15... |
| state_fips=49/49.parquet | 87.2 MB | 122087f6817b... |
| state_fips=50/50.parquet | 27.6 MB | 12200f787058... |
| state_fips=51/51.parquet | 150.2 MB | 1220145fe3b9... |
| state_fips=53/53.parquet | 94.7 MB | 122029988392... |
| state_fips=54/54.parquet | 84.1 MB | 12204472cf17... |
| state_fips=55/55.parquet | 132.6 MB | 1220846952f1... |
| state_fips=56/56.parquet | 70.9 MB | 12201359443b... |
| state_fips=72/72.parquet | 18.7 MB | 1220e66ee1e8... |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./blocks.pmtiles")
print(gdf.head())
```

## STAC Metadata

- **root**: `../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/](https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/)

## Processing Notes

Built 2026-11-12 from two sets of Census Bureau files, downloaded the same day: the 2020 P.L. 94-171 redistricting archives (https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/) for the counts, and TIGER/Line 2024 TABBLOCK20 shapefiles (https://www2.census.gov/geo/tiger/TIGER2024/TABBLOCK20/) for the geometry. 52 states (50 + DC + PR), 104 archives, 7.4 GB.

Per state: ogr2ogr converts the shapefile to EPSG:4326 parquet keeping only `GEOID20` and `ALAND20`; DuckDB joins the four pipe-delimited P.L. files on `LOGRECNO`, filters `SUMLEV = '750'`, joins to the geometry on `GEOID20 = GEOCODE`, and derives the shares and density; `gpio sort hilbert --add-bbox` writes the final partition. Field positions are pinned against the Census Bureau's own R import scripts, field counts are re-checked per state and abort on a mismatch, and the geoheader is read as Latin-1 (it carries ISO-8859-1 place names; a UTF-8 read fails on Arizona).

Validated: `pop_total` over the 50 states + DC equals the published 331,449,281 exactly and Puerto Rico 3,285,874; `housing_occupied + housing_vacant == housing_units` on every block; GEOIDs unique across all 52 partitions; zero orphans in either direction between TIGER and the P.L. files; one schema across all partitions.

Converted to GeoParquet with geoparquet-io (gpio): ZSTD compression, Hilbert row order, and a covering `bbox` column with row-group statistics, so a spatial filter can skip most of the file over the network. Tiled to PMTiles with tylertoo, with A5 cell aggregation at coarse zooms (counts summed, rates averaged) — a visualization aid, not a statistical product.


## Attribution

U.S. Census Bureau

## License

[CC0-1.0](https://www.census.gov/about/policies/open-gov/open-data.html)

## Contact

Chris Holmes <cholmes@9eo.org>

## Known Issues

28.97% of blocks have `pop_total = 0` (measured), so `pct_white_nh`, `pct_black` and `pct_hispanic` are NULL on that share of rows, and `pct_vacant` is NULL on the 27.64% with no housing units. By design — most census blocks are unpopulated. Filter `pop_total > 0` before averaging a rate.

2020 block counts are protected by the Census Bureau's disclosure-avoidance system, which injects noise at block level while holding state totals exact. Reliable in aggregate; read a single block's counts with care.

Geometry is TIGER/Line, which is not shoreline-clipped: a coastal block extends to the 3-mile limit. Water-only blocks have `ALAND20 = 0` and so a NULL `pop_density`.

The race columns are race-alone counts crossing Hispanic origin (P1), while `pop_white_nh` is the not-Hispanic branch of P2. The two are not interchangeable, and `pct_black` here is not the same measure as `pct_black` in the ACS collections, which is non-Hispanic Black alone.

Blocks carry 2020 Decennial counts only. The Census Bureau publishes no income, education, commuting or internet data below block group, and this collection invents none.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
