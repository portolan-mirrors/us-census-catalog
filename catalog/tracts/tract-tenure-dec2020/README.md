# Tenure (2020 Census) — Census Tracts

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-tenure-dec2020/collection.json)** · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-tenure-dec2020/tract-tenure-dec2020.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-tenure-dec2020/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

Housing units (H1) and tenure of occupied housing units (H4 — owned with a mortgage or loan, owned free and clear, renter occupied). `pct_owned`, `pct_rented` and `pct_vacant_2020` are this build's own shares, named apart from the ACS housing collections' `pct_owner_occupied` and `pct_vacant_units` so the two are never selected as if they were one column.

All **85,184** census tracts in the 50 states, the District of Columbia and Puerto Rico, from the U.S. Census Bureau's [2020 Census Demographic and Housing Characteristics File](https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html) (DHC), tables H1 and H4. The DHC is a 100% count from every return, the same survey family as the [blocks](https://source.coop/portolan-mirrors/us-census-catalog/blocks/collection.json) collection's P.L. 94-171 redistricting counts, read with the same per-state zip, Latin-1 geoheader and `LOGRECNO` join — but a different table set: blocks carries race, Hispanic origin, voting-age population and housing occupancy; this carries age, sex, household type and tenure, at block-groups and tracts rather than blocks.

**No margin of error, no coefficient of variation.** A 100% count carries no sampling error, so there is nothing here to estimate the uncertainty of — every column is the Bureau's tabulated count, full stop.

**Differential privacy.** The 2020 Census protects confidentiality with a disclosure avoidance system that injects statistical noise calibrated to a privacy-loss budget, most at block level and least at state level (state population totals are held exact; smaller geographies and smaller counts carry more). A block group or tract's individual cells can be off by a few people even though the file shows no margin of error; see the Census Bureau's [disclosure avoidance documentation](https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/process/disclosure-avoidance.html) and the [DHC technical documentation](https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/demographic-and-housing-characteristics-file-and-demographic-profile/2020census-demographic-and-housing-characteristics-file-and-demographic-profile-techdoc.pdf) (Chapter 4, "Confidentiality of the Data").

This sits beside the American Community Survey collections at the same geography, not in a separate decennial group: [Income & Poverty](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/collection.json), [People & Education](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/collection.json), [Housing & Rent](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/collection.json), [Commuting & Connectivity](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/collection.json), [Health, Disability & Income by Race](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/collection.json). All of them share this collection's `geoid` and geometry and join 1:1 on `geoid` — but **do not subtract one from the other**. This is a different measurement: a 2020 Census 100% count with injected noise, not a 2020–2024 ACS 5-year sample estimate with a margin of error. The same theme at the other geography this batch covers is [Tenure (2020 Census) — Block Groups](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-tenure-dec2020/collection.json).

The PMTiles archive is one band, the collection's own features at every zoom (`tylertoo tiles`, not the county/tract pyramid the ACS collections use) — bg and tract are the two finest geographies this batch covers and there is no coarser DHC band to step up to yet. There are no `*_moe` columns to exclude: this is a 100% count, not an estimate, so there is nothing to exclude.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them.

![census](https://img.shields.io/badge/census-blue) ![2020 Census](https://img.shields.io/badge/2020_Census-blue) ![decennial census](https://img.shields.io/badge/decennial_census-blue) ![DHC](https://img.shields.io/badge/DHC-blue) ![Demographic and Housing Characteristics](https://img.shields.io/badge/Demographic_and_Housing_Characteristics-blue) ![differential privacy](https://img.shields.io/badge/differential_privacy-blue) ![disclosure avoidance](https://img.shields.io/badge/disclosure_avoidance-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![tenure](https://img.shields.io/badge/tenure-blue) ![owner occupied](https://img.shields.io/badge/owner_occupied-blue) ![renter occupied](https://img.shields.io/badge/renter_occupied-blue) ![housing units](https://img.shields.io/badge/housing_units-blue)

## Spatial Coverage

- **Bounding Box**: [-179.146711, -14.548699, -64.565599, 71.387815]

## Temporal Coverage

- **Start**: 2020-04-01T00:00:00Z
- **End**: 2020-04-01T00:00:00Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | 11-character census tract GEOID — state (2) + county (3) + tract (6), e.g. `29510102200`. Joins the block-group collections on `substr(geoid, 1, 11)` and the block collection on `substr(geoid, 1, 11)`. Matches `GEOID` in the 2024 cartographic boundary tract file; the ACS `1400000US` prefix is stripped. |
| name | string | Human-readable name from the cartographic boundary tract file: `NAMELSAD`, `NAMELSADCO`, `STATE_NAME` — "Census Tract 34.06, San Joaquin County, California". |
| state | string | Two-letter USPS state code, carried from the DHC geoheader's own per-state build rather than read off the boundary files (tools/build_dhc.py's `STATES` list). |
| aland_sqkm | double | Land area in square kilometres, rounded to 3 decimals. `ALAND / 1e6` from the cartographic boundary file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
| total_housing_units | int64 | Total housing units (H1 cell `P0010001` per the geoheader's own count, table `H1`, "Total"). Not the ACS housing collections' `housing_units`. |
| occupied_total | int64 | Occupied housing units (H4 cell `H0040001`, "Total:" — the universe of H4 is occupied housing units). Equals `total_households` in the household collection at this geography. |
| owned_with_mortgage | int64 | Occupied housing units owned with a mortgage or a loan (H4). |
| owned_free_clear | int64 | Occupied housing units owned free and clear, with no mortgage or loan (H4). |
| renter_occupied | int64 | Renter-occupied housing units (H4). |
| pct_owned | double | Share of occupied housing units that are owner-occupied, with or without a mortgage (`(owned_with_mortgage + owned_free_clear) / occupied_total`), this build's own derived share — not the ACS housing collections' `pct_owner_occupied`. |
| pct_rented | double | Share of occupied housing units that are renter-occupied (`renter_occupied / occupied_total`), this build's own derived share. |
| pct_vacant_2020 | double | Share of all housing units that are vacant (`(total_housing_units - occupied_total) / total_housing_units`), this build's own derived share — named apart from the ACS housing collections' `pct_vacant_units` so the two are never selected as if they were one column. |
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary census tract file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the census tract into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./tract-tenure-dec2020.pmtiles | 188.6 MB | 1220a6cb0649... |
| ./tract-tenure-dec2020.parquet | 50.9 MB | 1220a8367544... |
| ./thumbnail.png | 90.0 KB | 1220c91abdc0... |
| ./styles/default.json | 2.0 KB | 122012ecf719... |
| ./styles/vacant.json | 1.8 KB | 12200c2353d2... |
| https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/ | - | - |
| https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/demographic-and-housing-characteristics-file-and-demographic-profile/2020census-demographic-and-housing-characteristics-file-and-demographic-profile-techdoc.pdf | - | - |
| https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/demographic-and-housing-characteristics-file-and-demographic-profile/2020-dhc-table-matrix.xlsx | - | - |
| https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/process/disclosure-avoidance.html | - | - |
| https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_tract_500k.zip | 55.2 MB | 1220abdf8bda... |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./tract-tenure-dec2020.pmtiles")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/](https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/)

## Processing Notes

Built 2026-11-15 from the 2020 Census DHC per-state zips (https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/), downloaded one state at a time and deleted (zip and extract both) immediately after that state's rows were pulled — the national DHC source is roughly 15 GB compressed and several times larger extracted, so the build never holds more than one state on disk. tools/build_dhc.py.

Per state: the geoheader (97 fields, Latin-1, same layout PL 94-171 uses) is filtered to `SUMLEV = '140'`, `GEOCOMP = '00'` (the whole-geography total; block groups and tracts carry no other geographic component, but state and county records also carry urban/rural and housing-unit-count variants under other `GEOCOMP` values, which this filter excludes) and joined on `LOGRECNO` to the segment files carrying H1 and H4. Field positions were derived from the Census Bureau's own DHC Table Matrix (`TABLE_ID`, `SEGMENT_NUMBER`, `TOTAL_RECORDS`, `TABLE_SORT_ORDER` — cumulative field offsets within a segment, the same scheme tools/build_blocks.py documents for P.L. 94-171) and verified against the real field counts in every segment file this build reads, not assumed from the spreadsheet alone.

`GEOCODE` is the field trusted for the GEOID, matching tools/build_blocks.py. Geometry is the same 2024 cartographic boundary file the ACS collections at this geography join to (`cb_2024_us_tract_500k.zip`), so a DHC row and an ACS row for the same `geoid` always share the same polygon; the join is driven by geometry, so a geography with boundaries but no DHC row (there are none at bg/tract — measured) would keep its row with NULL values rather than disappear.

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


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
