# Age & Sex (2020 Census) — Block Groups

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-age-dec2020/collection.json)** · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-age-dec2020/bg-age-dec2020.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-age-dec2020/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

Sex by age for 23 age bands (P12), the full 2020 Census age pyramid: a total, a male/female split, and both sexes carried through the same 23 bands from under 5 to 85 and over. `pct_under18` and `pct_65plus` are this build's own sums of the published bands (not published columns themselves), named without the ACS collections' underscores (`pct_under18`, not `pct_under_18`) on purpose, so a query against both files by column name cannot silently select one sense when it meant the other.

All **242,298** census block groups in the 50 states, the District of Columbia and Puerto Rico, from the U.S. Census Bureau's [2020 Census Demographic and Housing Characteristics File](https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html) (DHC), table P12. The DHC is a 100% count from every return, the same survey family as the [blocks](https://source.coop/portolan-mirrors/us-census-catalog/blocks/collection.json) collection's P.L. 94-171 redistricting counts, read with the same per-state zip, Latin-1 geoheader and `LOGRECNO` join — but a different table set: blocks carries race, Hispanic origin, voting-age population and housing occupancy; this carries age, sex, household type and tenure, at block-groups and tracts rather than blocks.

**No margin of error, no coefficient of variation.** A 100% count carries no sampling error, so there is nothing here to estimate the uncertainty of — every column is the Bureau's tabulated count, full stop.

**Differential privacy.** The 2020 Census protects confidentiality with a disclosure avoidance system that injects statistical noise calibrated to a privacy-loss budget, most at block level and least at state level (state population totals are held exact; smaller geographies and smaller counts carry more). A block group or tract's individual cells can be off by a few people even though the file shows no margin of error; see the Census Bureau's [disclosure avoidance documentation](https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/process/disclosure-avoidance.html) and the [DHC technical documentation](https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/demographic-and-housing-characteristics-file-and-demographic-profile/2020census-demographic-and-housing-characteristics-file-and-demographic-profile-techdoc.pdf) (Chapter 4, "Confidentiality of the Data").

This sits beside the American Community Survey collections at the same geography, not in a separate decennial group: [Income & Poverty](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/collection.json), [People & Education](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/collection.json), [Housing & Rent](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/collection.json), [Commuting & Connectivity](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/collection.json). All of them share this collection's `geoid` and geometry and join 1:1 on `geoid` — but **do not subtract one from the other**. This is a different measurement: a 2020 Census 100% count with injected noise, not a 2020–2024 ACS 5-year sample estimate with a margin of error. The same theme at the other geography this batch covers is [Age & Sex (2020 Census) — Census Tracts](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-age-dec2020/collection.json).

The PMTiles archive is one band, the collection's own features at every zoom (`tylertoo tiles`, not the county/tract pyramid the ACS collections use) — bg and tract are the two finest geographies this batch covers and there is no coarser DHC band to step up to yet. There are no `*_moe` columns to exclude: this is a 100% count, not an estimate, so there is nothing to exclude.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them.

![census](https://img.shields.io/badge/census-blue) ![2020 Census](https://img.shields.io/badge/2020_Census-blue) ![decennial census](https://img.shields.io/badge/decennial_census-blue) ![DHC](https://img.shields.io/badge/DHC-blue) ![Demographic and Housing Characteristics](https://img.shields.io/badge/Demographic_and_Housing_Characteristics-blue) ![differential privacy](https://img.shields.io/badge/differential_privacy-blue) ![disclosure avoidance](https://img.shields.io/badge/disclosure_avoidance-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![age](https://img.shields.io/badge/age-blue) ![sex](https://img.shields.io/badge/sex-blue) ![age pyramid](https://img.shields.io/badge/age_pyramid-blue) ![block groups](https://img.shields.io/badge/block_groups-blue)

## Spatial Coverage

- **Bounding Box**: [-179.146711, -14.548699, -64.565599, 71.387815]

## Temporal Coverage

- **Start**: 2020-04-01T00:00:00Z
- **End**: 2020-04-01T00:00:00Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | 12-character census block-group GEOID — state (2) + county (3) + tract (6) + block group (1), e.g. `295101022004`. The join key across the census family: `substr(geoid, 1, 11)` is the tract, `substr(geoid, 1, 5)` the county, `substr(geoid, 1, 2)` the state FIPS code. Matches `GEOID` in the Census Bureau's 2024 cartographic boundary block-group file; the summary-level prefix the ACS summary file carries on `GEO_ID` (`1500000US`) is stripped. |
| name | string | Human-readable name, assembled from the cartographic boundary files with `concat_ws(', ', …)`: the block group's own `NAMELSAD`, the tract's `NAMELSAD`, then the county's `NAMELSAD` and `STATE_NAME` — "Block Group 4, Census Tract 1022, St. Louis city, Missouri". The block-group file carries only "Block Group 4", so the tract and county files supply the rest. |
| state | string | Two-letter USPS state code, carried from the DHC geoheader's own per-state build rather than read off the boundary files (tools/build_dhc.py's `STATES` list). |
| aland_sqkm | double | Land area in square kilometres, rounded to 3 decimals. `ALAND / 1e6` from the cartographic boundary file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
| total_population | int64 | Total population (P12 cell `P0120001`, "Total:"), the DHC's 100% count — not the ACS people collections' `population` estimate beside it. |
| male_total | int64 | Male population (P12, "Male:"). |
| male_under5 | int64 | Male population, Under 5 years (P12). |
| male_age5_9 | int64 | Male population, 5 to 9 years (P12). |
| male_age10_14 | int64 | Male population, 10 to 14 years (P12). |
| male_age15_17 | int64 | Male population, 15 to 17 years (P12). |
| male_age18_19 | int64 | Male population, 18 and 19 years (P12). |
| male_age20 | int64 | Male population, 20 years (P12). |
| male_age21 | int64 | Male population, 21 years (P12). |
| male_age22_24 | int64 | Male population, 22 to 24 years (P12). |
| male_age25_29 | int64 | Male population, 25 to 29 years (P12). |
| male_age30_34 | int64 | Male population, 30 to 34 years (P12). |
| male_age35_39 | int64 | Male population, 35 to 39 years (P12). |
| male_age40_44 | int64 | Male population, 40 to 44 years (P12). |
| male_age45_49 | int64 | Male population, 45 to 49 years (P12). |
| male_age50_54 | int64 | Male population, 50 to 54 years (P12). |
| male_age55_59 | int64 | Male population, 55 to 59 years (P12). |
| male_age60_61 | int64 | Male population, 60 and 61 years (P12). |
| male_age62_64 | int64 | Male population, 62 to 64 years (P12). |
| male_age65_66 | int64 | Male population, 65 and 66 years (P12). |
| male_age67_69 | int64 | Male population, 67 to 69 years (P12). |
| male_age70_74 | int64 | Male population, 70 to 74 years (P12). |
| male_age75_79 | int64 | Male population, 75 to 79 years (P12). |
| male_age80_84 | int64 | Male population, 80 to 84 years (P12). |
| male_age85_plus | int64 | Male population, 85 years and over (P12). |
| female_total | int64 | Female population (P12, "Female:"). |
| female_under5 | int64 | Female population, Under 5 years (P12). |
| female_age5_9 | int64 | Female population, 5 to 9 years (P12). |
| female_age10_14 | int64 | Female population, 10 to 14 years (P12). |
| female_age15_17 | int64 | Female population, 15 to 17 years (P12). |
| female_age18_19 | int64 | Female population, 18 and 19 years (P12). |
| female_age20 | int64 | Female population, 20 years (P12). |
| female_age21 | int64 | Female population, 21 years (P12). |
| female_age22_24 | int64 | Female population, 22 to 24 years (P12). |
| female_age25_29 | int64 | Female population, 25 to 29 years (P12). |
| female_age30_34 | int64 | Female population, 30 to 34 years (P12). |
| female_age35_39 | int64 | Female population, 35 to 39 years (P12). |
| female_age40_44 | int64 | Female population, 40 to 44 years (P12). |
| female_age45_49 | int64 | Female population, 45 to 49 years (P12). |
| female_age50_54 | int64 | Female population, 50 to 54 years (P12). |
| female_age55_59 | int64 | Female population, 55 to 59 years (P12). |
| female_age60_61 | int64 | Female population, 60 and 61 years (P12). |
| female_age62_64 | int64 | Female population, 62 to 64 years (P12). |
| female_age65_66 | int64 | Female population, 65 and 66 years (P12). |
| female_age67_69 | int64 | Female population, 67 to 69 years (P12). |
| female_age70_74 | int64 | Female population, 70 to 74 years (P12). |
| female_age75_79 | int64 | Female population, 75 to 79 years (P12). |
| female_age80_84 | int64 | Female population, 80 to 84 years (P12). |
| female_age85_plus | int64 | Female population, 85 years and over (P12). |
| pct_under18 | double | Share of total population under 18 (`male_under5 + male_age5_9 + male_age10_14 + male_age15_17 +` the matching female bins, over `total_population`), this build's own sum of the published bands — not a column P12 itself publishes, and not the ACS people collections' `pct_under_18`. |
| pct_65plus | double | Share of total population 65 and over (the six 65-and-over bands for both sexes, over `total_population`), this build's own sum — not the ACS people collections' `pct_65_plus`. |
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary block group file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the block group into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./bg-age-dec2020.parquet | 90.2 MB | 1220ac963f77... |
| ./thumbnail.png | 90.7 KB | 12202f16d2fd... |
| ./bg-age-dec2020.pmtiles | 911.8 MB | 1220540f632d... |
| ./styles/default.json | 1.8 KB | 1220c3dc58ea... |
| ./styles/under18.json | 1.8 KB | 12207ec64292... |
| https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/ | - | - |
| https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/demographic-and-housing-characteristics-file-and-demographic-profile/2020census-demographic-and-housing-characteristics-file-and-demographic-profile-techdoc.pdf | - | - |
| https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/demographic-and-housing-characteristics-file-and-demographic-profile/2020-dhc-table-matrix.xlsx | - | - |
| https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/process/disclosure-avoidance.html | - | - |
| https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_bg_500k.zip | 92.6 MB | 12207c4da3ed... |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./bg-age-dec2020.parquet")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/](https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/)

## Processing Notes

Built 2026-11-15 from the 2020 Census DHC per-state zips (https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/), downloaded one state at a time and deleted (zip and extract both) immediately after that state's rows were pulled — the national DHC source is roughly 15 GB compressed and several times larger extracted, so the build never holds more than one state on disk. tools/build_dhc.py.

Per state: the geoheader (97 fields, Latin-1, same layout PL 94-171 uses) is filtered to `SUMLEV = '150'`, `GEOCOMP = '00'` (the whole-geography total; block groups and tracts carry no other geographic component, but state and county records also carry urban/rural and housing-unit-count variants under other `GEOCOMP` values, which this filter excludes) and joined on `LOGRECNO` to the segment files carrying P12. Field positions were derived from the Census Bureau's own DHC Table Matrix (`TABLE_ID`, `SEGMENT_NUMBER`, `TOTAL_RECORDS`, `TABLE_SORT_ORDER` — cumulative field offsets within a segment, the same scheme tools/build_blocks.py documents for P.L. 94-171) and verified against the real field counts in every segment file this build reads, not assumed from the spreadsheet alone.

`GEOCODE` is the field trusted for the GEOID, matching tools/build_blocks.py. Geometry is the same 2024 cartographic boundary file the ACS collections at this geography join to (`cb_2024_us_bg_500k.zip`), so a DHC row and an ACS row for the same `geoid` always share the same polygon; the join is driven by geometry, so a geography with boundaries but no DHC row (there are none at bg/tract — measured) would keep its row with NULL values rather than disappear.

Validated: every state's P12 `total_population` sum equals the state's published 2020 apportionment population exactly (state totals are held invariant by the disclosure avoidance system — not noised); `occupied_total` (H4) equals `total_households` (P16) and `total_population_p17` (P17) equals `total_population` (P12) on every state, exactly; `male_total + female_total` equals `total_population` on every state; three values cross-checked against data.census.gov (see the build report in docs/dhc-build-notes.md).


## Attribution

U.S. Census Bureau

## License

[CC0-1.0](https://www.census.gov/about/policies/open-gov/open-data.html)

## Contact

Chris Holmes <cholmes@9eo.org>

## Known Issues

**The 2020 Census applied differential privacy.** Every count in this collection — not just the small ones — passed through the Census Bureau's disclosure avoidance system, which injects statistical noise calibrated to a privacy-loss budget. State population totals are held exact; housing unit counts and major group-quarters counts per block are held exact; everything else, including the counts in this collection, can carry injected noise, proportionally larger for a small count in a small geography than for a large one. There is no column here that quantifies that noise — see the Census Bureau's [disclosure avoidance documentation](https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/process/disclosure-avoidance.html) — so treat a single block group's count with more caution than a tract's, and a tract's with more caution than a state's.

**This is a different measurement from the ACS collections beside it, not a finer or coarser version of the same one.** The ACS `*_moe`/`*_cv` columns describe sampling error in a 5-year rolling survey; this collection has no sampling error and no margin of error because it is not a sample. Joining the two on `geoid` is fine; subtracting one's count from the other's estimate, or averaging them, treats two different measurements of two different things as if they disagreed about one.

`total_population` (P12) is the same universe as `total_population_p17` in the household collection at this geography — both are the DHC's total population count — but neither is published in this collection under the ACS `population` column name, to keep a column-name join from silently crossing collections.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
