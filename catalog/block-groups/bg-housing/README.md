# Housing & Rent — Block Groups

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/collection.json)** · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

The housing stock and what it costs: total units and the vacancy rate ([B25002](https://data.census.gov/table/ACSDT5Y2024.B25002)), households and the owner-occupied share ([B25003](https://data.census.gov/table/ACSDT5Y2024.B25003)), median gross rent ([B25064](https://data.census.gov/table/ACSDT5Y2024.B25064)) and median owner-occupied home value ([B25077](https://data.census.gov/table/ACSDT5Y2024.B25077)), the share of renter households paying 30% and 50% or more of income on rent ([B25070](https://data.census.gov/table/ACSDT5Y2024.B25070)), the pre-1940 share ([B25034](https://data.census.gov/table/ACSDT5Y2024.B25034)) and the single-family share ([B25024](https://data.census.gov/table/ACSDT5Y2024.B25024)).

Curated indicators for all **242,298** census block groups in the United States, Puerto Rico and the island areas, from the U.S. Census Bureau's [American Community Survey](https://www.census.gov/programs-surveys/acs.html) **2020–2024 5-year estimates** (`acsdt5y2024`, the table-based [Summary File](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)). The Census Bureau calls the ACS "the premier source of detailed information about the nation's people and housing". The 5-year file is the only ACS release published at this geography: 1-year estimates stop well above it.

Every estimate ships with its margin of error — `<column>_moe`, at the 90% confidence level, the level the Census Bureau publishes — and the headline statistics also carry a coefficient of variation (`<column>_cv` = `moe / 1.645 / estimate`) so small-area noise can be flagged rather than mapped as if certain. Derived percentages propagate error with the Census Bureau's own formulas from [ACS Accuracy of the Data](https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf): sums add in quadrature, proportions use the subset formula with the ratio formula as fallback. ACS jam values for suppressed or unestimable cells are NULL here, never numbers, and medians are published as the Bureau publishes them — a median cannot be aggregated to a larger area. Each column's description names its ACS table, its exact universe, and the lines summed to make it.

One number to know before mapping this at block-group scale: `median_gross_rent` is NULL for **29.68%** of block groups and `median_home_value` for **10.03%**, because a block group with few renter or owner households has no publishable median. The tract collection's rates are 5.92% and 3.55%.

Geometries are the Census Bureau's [2024 cartographic boundary files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) for census block groups (GENZ2024, 1:500,000), reprojected to EPSG:4326 and joined on `GEOID`. Cartographic rather than TIGER/Line because TIGER extends census geographies into open water while the cartographic files clip to the shoreline, which is what a choropleth wants. The boundary vintage matches the estimate vintage.

The join is driven by geometry, so a geography with 2024 boundaries but no ACS tabulation keeps its row with NULL values instead of disappearing: 405 block groups in the island areas, which have cartographic boundaries but no ACS 5-year estimates because the Island Areas run a separate decennial-only program. Suffolk County, New York was re-delineated in the 2024 vintage, which adds 39 block groups with boundaries and no matching ACS row. Keeping these rows means a national map has no holes and a consumer can see the absence; dropping them would make "every US geography" quietly mean something narrower.

This is one themed chunk of four at this geography. The other themes are [Income & Poverty](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/collection.json), [People & Education](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/collection.json) and [Commuting & Connectivity](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/collection.json), split that way so a consumer who wants one theme reads one file. Chunks at the same geography hold the same rows and the same geometry, so they join 1:1 on `geoid`. The wellbeing tables — health insurance, disability, nativity and income by race — are not published at this geography at all; they start at [census tracts](https://source.coop/portolan-mirrors/us-census-catalog/tracts/catalog.json). GEOIDs nest by prefix: `substr(geoid, 1, 11)` is the tract, `substr(geoid, 1, 5)` the county and `substr(geoid, 1, 2)` the state. Every other geography in this catalog is organized the same way — [census tracts](https://source.coop/portolan-mirrors/us-census-catalog/tracts/catalog.json), [counties](https://source.coop/portolan-mirrors/us-census-catalog/counties/catalog.json), [states](https://source.coop/portolan-mirrors/us-census-catalog/states/catalog.json), [ZCTAs](https://source.coop/portolan-mirrors/us-census-catalog/zctas/catalog.json), [places and CDPs](https://source.coop/portolan-mirrors/us-census-catalog/places/catalog.json) and [congressional districts](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/catalog.json) — and the [blocks](https://source.coop/portolan-mirrors/us-census-catalog/blocks/collection.json) collection carries 2020 Decennial counts, a different survey and vintage rather than a finer version of these numbers.

The PMTiles archive is a census-geography pyramid built with [tylertoo](https://github.com/geoparquet-io/tylertoo): z0–z5 are county polygons and z6–z7 census tracts, each carrying the Census Bureau's own published estimates for that geography, and z8–z13 are the block groups themselves. Thinning this many polygons down to a national zoom would show a biased subset (small urban geographies drop first) rather than less data, so the coarse zooms step up to a coarser census geography instead of a thinned sample of this one. Every band carries the same column names, so one style expression classifies every zoom — but below z8 you are looking at counties and tracts, not block groups, and the values there are the Bureau's official estimates for those geographies, with their own meaning, rather than a visualization-only average: clicking a coarse feature identifies a real county or tract by `geoid` and `name`. The `*_moe` columns are excluded from the tiles at every zoom — a margin of error is computed for one specific geography and cannot be carried across bands — while the `*_cv` columns are kept. Statistics come from the GeoParquet, never from the tiles.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![ACS](https://img.shields.io/badge/ACS-blue) ![American Community Survey](https://img.shields.io/badge/American_Community_Survey-blue) ![demographics](https://img.shields.io/badge/demographics-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![margins of error](https://img.shields.io/badge/margins_of_error-blue) ![housing](https://img.shields.io/badge/housing-blue) ![rent](https://img.shields.io/badge/rent-blue) ![home values](https://img.shields.io/badge/home_values-blue) ![tenure](https://img.shields.io/badge/tenure-blue) ![vacancy](https://img.shields.io/badge/vacancy-blue) ![affordability](https://img.shields.io/badge/affordability-blue)

## Spatial Coverage

- **Bounding Box**: [-179.146711, 17.88329, -65.221081, 71.387815]

## Temporal Coverage

- **Start**: 2020-01-01T00:00:00Z
- **End**: 2024-12-31T23:59:59Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | 12-character census block-group GEOID — state (2) + county (3) + tract (6) + block group (1), e.g. `295101022004`. The join key across the census family: `substr(geoid, 1, 11)` is the tract, `substr(geoid, 1, 5)` the county, `substr(geoid, 1, 2)` the state FIPS code. Matches `GEOID` in the Census Bureau's 2024 cartographic boundary block-group file; the summary-level prefix the ACS summary file carries on `GEO_ID` (`1500000US`) is stripped. |
| name | string | Human-readable name, assembled from the cartographic boundary files with `concat_ws(', ', …)`: the block group's own `NAMELSAD`, the tract's `NAMELSAD`, then the county's `NAMELSAD` and `STATE_NAME` — "Block Group 4, Census Tract 1022, St. Louis city, Missouri". The block-group file carries only "Block Group 4", so the tract and county files supply the rest. |
| state | string | Two-letter USPS state or territory code (`MO`, `PR`, `GU`). Carried on every collection from the `STATEFP → USPS` lookup embedded in `tools/specs.py` rather than read off the boundary files, because the 2024 cartographic boundary block-group file has no `STUSPS` column while the tract, county and state files do. |
| population | int64 | Total population. Universe: total population. The single line of [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) (Total Population), published as an integer. Carried on every ACS collection so a rate can be weighted or sanity-checked without a second download. NULL on 0.18% of block groups — the island areas (405 block groups with 2024 boundaries but no ACS data) and the 39 Suffolk County, NY block groups re-delineated in this vintage. |
| population_moe | double | Margin of error for `population` at the 90% confidence level, the level the Census Bureau publishes. Component margins add in quadrature — `sqrt(Σ moe²)` — which is the Census Bureau's formula for the margin of a sum. NULL when every component is a jam value. |
| aland_sqkm | double | Land area in square kilometres, rounded to 3 decimals. `ALAND / 1e6` from the cartographic boundary file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
| pop_density | double | People per square kilometre of land area, rounded to 1 decimal: `population / aland_sqkm`. NULL where `ALAND` is 0 or `population` is NULL. 646 of 242,298 block groups are NULL: 444 with no ACS population plus 202 that are entirely water. |
| housing_units | int64 | Total housing units, occupied and vacant. Universe: housing units. Line 1 of [B25002](https://data.census.gov/table/ACSDT5Y2024.B25002) (Occupancy Status), published as an integer. |
| housing_units_moe | double | Margin of error for `housing_units` at the 90% confidence level, the level the Census Bureau publishes. Component margins add in quadrature — `sqrt(Σ moe²)` — which is the Census Bureau's formula for the margin of a sum. NULL when every component is a jam value. |
| pct_vacant_units | double | Percent of housing units that are vacant. Universe: housing units. Line 3 ("Vacant") over line 1 of [B25002](https://data.census.gov/table/ACSDT5Y2024.B25002). The ACS counts for-sale, for-rent, seasonal and migrant-worker units as vacant, so this is not a measure of abandonment. |
| pct_vacant_units_moe | double | Margin of error for `pct_vacant_units` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| households | int64 | Households — occupied housing units. One household per occupied unit, by definition. Universe: occupied housing units. Line 1 of [B25003](https://data.census.gov/table/ACSDT5Y2024.B25003) (Tenure), published as an integer. |
| households_moe | double | Margin of error for `households` at the 90% confidence level, the level the Census Bureau publishes. Component margins add in quadrature — `sqrt(Σ moe²)` — which is the Census Bureau's formula for the margin of a sum. NULL when every component is a jam value. |
| pct_owner_occupied | double | Percent of occupied housing units that are owner-occupied. Universe: occupied housing units. Line 2 ("Owner occupied") over line 1 of [B25003](https://data.census.gov/table/ACSDT5Y2024.B25003). The homeownership rate of households, not of people, and vacant units are outside the universe entirely. |
| pct_owner_occupied_moe | double | Margin of error for `pct_owner_occupied` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| median_gross_rent | double | Median gross rent in dollars per month — contract rent plus the estimated average monthly cost of utilities and fuels. Universe: renter-occupied housing units **paying cash rent**, so units occupied rent-free are excluded. Line 1 of [B25064](https://data.census.gov/table/ACSDT5Y2024.B25064). **NULL on 29.68% of block groups** — nearly a third. A block group with few renter households paying cash rent has no publishable rent median; the tract rate is 5.92%. Map this at block-group scale only if the holes are acceptable, or move up to tracts. |
| median_gross_rent_moe | double | Margin of error for `median_gross_rent` at the 90% confidence level, the level the Census Bureau publishes. Published as the Census Bureau publishes it for this line. A median's margin cannot be recomputed from a distribution, so it is passed through untouched. |
| median_gross_rent_cv | double | Coefficient of variation for `median_gross_rent`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_rent_burdened | double | Percent of renter households paying 30% or more of household income on gross rent — the standard affordability threshold. Universe: renter-occupied housing units, less those whose ratio the Census could not compute. Lines 7–10 (30.0–34.9, 35.0–39.9, 40.0–49.9, 50.0 percent or more) of [B25070](https://data.census.gov/table/ACSDT5Y2024.B25070) over line 1 minus line 11 ("Not computed" — no cash rent, or no income). Including the not-computed units in the denominator would understate the burden. NULL on 7.91% of block groups, where the denominator (renter households whose ratio could be computed) came out at or below 0. |
| pct_rent_burdened_moe | double | Margin of error for `pct_rent_burdened` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_rent_burdened_cv | double | Coefficient of variation for `pct_rent_burdened`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_severely_rent_burdened | double | Percent of renter households paying 50% or more of household income on gross rent. Universe: renter-occupied housing units, less those whose ratio could not be computed. Line 10 of [B25070](https://data.census.gov/table/ACSDT5Y2024.B25070) over line 1 minus line 11. A subset of `pct_rent_burdened`. |
| pct_severely_rent_burdened_moe | double | Margin of error for `pct_severely_rent_burdened` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| median_home_value | double | Median value of owner-occupied housing units, in dollars — the owner's estimate of what the property would sell for, not an assessment or a sale price. Universe: owner-occupied housing units. Line 1 of [B25077](https://data.census.gov/table/ACSDT5Y2024.B25077). **NULL on 10.03% of block groups** — a block group with few owner-occupied units has no publishable value median. The tract rate is 3.55%. |
| median_home_value_moe | double | Margin of error for `median_home_value` at the 90% confidence level, the level the Census Bureau publishes. Published as the Census Bureau publishes it for this line. A median's margin cannot be recomputed from a distribution, so it is passed through untouched. |
| median_home_value_cv | double | Coefficient of variation for `median_home_value`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_built_pre_1940 | double | Percent of housing units built in 1939 or earlier. Universe: housing units. Line 11 of [B25034](https://data.census.gov/table/ACSDT5Y2024.B25034) (Year Structure Built) over line 1. The oldest bucket the table publishes, and a standard screening proxy for lead-paint risk. |
| pct_built_pre_1940_moe | double | Margin of error for `pct_built_pre_1940` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_single_family | double | Percent of housing units in single-family structures. Universe: housing units. Lines 2 ("1, detached") + 3 ("1, attached") over line 1 of [B25024](https://data.census.gov/table/ACSDT5Y2024.B25024) (Units in Structure). Attached single-family — rowhouses, townhouses — is included; a duplex (line 4) is not. |
| pct_single_family_moe | double | Margin of error for `pct_single_family` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary block group file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the block group into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./bg-housing.parquet | 91.7 MB | 1220d34156d9... |
| ./bg-housing.pmtiles | 698.1 MB | 1220d14ab041... |
| ./thumbnail.png | 91.7 KB | 1220f9ba8530... |
| ./styles/default.json | 2.6 KB | 12204958989d... |
| ./styles/ownership.json | 1.8 KB | 1220f9b8201a... |
| ./styles/pre-1940.json | 1.8 KB | 12200971b63e... |
| ./styles/rent-burden.json | 2.5 KB | 12200ef7deaa... |
| ./styles/vacancy.json | 1.8 KB | 1220492f0258... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01003.dat | 17.5 MB | 122038d1a992... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25002.dat | 22.3 MB | 1220eb98debf... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25003.dat | 25.7 MB | 122068e963e1... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25024.dat | 45.6 MB | 122026ff26c6... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25034.dat | 47.8 MB | 1220806d6cb1... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25064.dat | 16.5 MB | 1220b36e6dc1... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25070.dat | 44.3 MB | 1220862ccc17... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25077.dat | 17.6 MB | 122089eb2153... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/documentation/ACS20245YR_Table_Shells.txt | 5.4 MB | 12205b46f4af... |
| https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_bg_500k.zip | 92.6 MB | 12207c4da3ed... |
| https://www.census.gov/programs-surveys/acs/library/handbooks/general.html | - | - |
| https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf | 378.9 KB | 12204d325820... |
| https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2024_ACSSubjectDefinitions.pdf | 1.1 MB | 12206e0c5b1a... |
| https://www.census.gov/programs-surveys/geography/about/glossary.html | - | - |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./bg-housing.parquet")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)

## Processing Notes



Built 2026-11-12 from the ACS 2020–2024 5-year table-based Summary File (https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/), downloaded the same day over plain HTTPS — the summary file needs no API key. Tables read for this collection: B01003, B25002, B25003, B25024, B25034, B25064, B25070, B25077. Each national `.dat` file is one row per geography with estimate and margin of error side by side, and every summary level is picked off `GEO_ID` by prefix in a single pass per file — this collection's is `1500000US`, read off the files themselves rather than taken from a summary-level table.

Jam values (the sentinels the ACS publishes in place of unestimable values, e.g. -666666666 for an uncomputable median, and -555555555 for a controlled MOE) become NULL: any estimate or margin at or below -111111111 is dropped rather than published as a number. Counts are sums of the specified lines with margins added in quadrature; percentages use the Census Bureau's proportion formula with the ratio formula as fallback; medians are passed through untouched; coefficients of variation are `moe / 1.645 / estimate` on the headline columns. Every line number is pinned against the release's own table shells before the build starts (44 pins verified, 0 failures, plus 4 derived line groups resolved from the shells), so a vintage bump that moves a line fails loudly instead of publishing a mislabeled column.

Geometry is the 2024 cartographic boundary file (cb_2024_us_bg_500k.zip) for census block groups (1:500,000), reprojected to EPSG:4326 with ogr2ogr — not DuckDB's `ST_Transform`, which computes correct coordinates but stamps the source CRS into the GeoParquet metadata. Geometry drives the join, so a geography with boundaries but no ACS tabulation keeps its row with NULL values.

Cross-checked end to end against the published St. Louis census catalog, which runs the same formulas on the same vintage: 314 of 314 block groups joined, 0 mismatches on median household income, its margin of error, the poverty rate and its margin of error — exact equality, not approximate.



Converted to GeoParquet with geoparquet-io (gpio): ZSTD compression, Hilbert row order, and a covering `bbox` column with row-group statistics, so a spatial filter can skip most of the file over the network. Tiled to PMTiles with tylertoo as a census-geography pyramid, so coarse zooms carry a coarser census geography — counties, then tracts — with that geography's own official values, instead of a thinned sample of this collection's features; the collections small enough to draw nationally (counties, states, congressional districts) are tiled as real polygons at every zoom.


## Attribution

U.S. Census Bureau

## License

[CC0-1.0](https://www.census.gov/about/policies/open-gov/open-data.html)

## Contact

Chris Holmes <cholmes@9eo.org>

## Known Issues

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 17 ZCTAs, 279 places and 4 delegate districts.

Suffolk County, New York (36103) was re-delineated in the 2024 vintage: 39 block groups and 14 tracts exist in the 2024 cartographic boundary files with no matching row in the 2020-based ACS tabulation, and publish with NULL ACS values. These are the only non-territory rows in the catalog with geometry but no data.

443 ACS block groups and 338 ACS tracts (the `9900xx`-style water geographies) have no polygon in the cartographic boundary files and therefore no row here. All of them have population 0, so the dropped population is exactly 0 — this is why the tract collections hold 85,184 rows against 85,382 in the ACS release.

Block-group medians are sparse where the sample is thin: NULL for `median_gross_rent` on 29.68% of rows, `median_home_value` on 10.03% of rows (measured). These are the Census Bureau's own suppressions, reported rather than patched.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: below z8 you are looking at counties and tracts, not block groups. The values there are the Census Bureau's own estimates for those geographies, not an aggregation of this file, and `*_moe` columns are not in the tiles. Statistics come from the GeoParquet.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
