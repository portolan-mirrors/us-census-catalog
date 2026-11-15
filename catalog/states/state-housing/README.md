# Housing & Rent — States

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/collection.json)** · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/states/state-housing/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

The housing stock and what it costs: total units and the vacancy rate ([B25002](https://data.census.gov/table/ACSDT5Y2024.B25002)), households and the owner-occupied share ([B25003](https://data.census.gov/table/ACSDT5Y2024.B25003)), median gross rent ([B25064](https://data.census.gov/table/ACSDT5Y2024.B25064)) and median owner-occupied home value ([B25077](https://data.census.gov/table/ACSDT5Y2024.B25077)), the share of renter households paying 30% and 50% or more of income on rent ([B25070](https://data.census.gov/table/ACSDT5Y2024.B25070)), the pre-1940 share ([B25034](https://data.census.gov/table/ACSDT5Y2024.B25034)) and the single-family share ([B25024](https://data.census.gov/table/ACSDT5Y2024.B25024)).

Curated indicators for all **56** states and state equivalents in the United States, Puerto Rico and the island areas, from the U.S. Census Bureau's [American Community Survey](https://www.census.gov/programs-surveys/acs.html) **2020–2024 5-year estimates** (`acsdt5y2024`, the table-based [Summary File](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)). The Census Bureau calls the ACS "the premier source of detailed information about the nation's people and housing". The Bureau also publishes 1-year estimates at this geography; the 5-year release is used throughout this catalog so every geography in it is the same vintage and directly comparable.

Every estimate ships with its margin of error — `<column>_moe`, at the 90% confidence level, the level the Census Bureau publishes — and the headline statistics also carry a coefficient of variation (`<column>_cv` = `moe / 1.645 / estimate`) so small-area noise can be flagged rather than mapped as if certain. Derived percentages propagate error with the Census Bureau's own formulas from [ACS Accuracy of the Data](https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf): sums add in quadrature, proportions use the subset formula with the ratio formula as fallback. ACS jam values for suppressed or unestimable cells are NULL here, never numbers, and medians are published as the Bureau publishes them — a median cannot be aggregated to a larger area. Each column's description names its ACS table, its exact universe, and the lines summed to make it.

Fifty-six rows: the 50 states, the District of Columbia, Puerto Rico and the four island areas. The island-area rows carry geometry and no ACS estimates, so every value column is NULL on 4 of 56 rows (**7.14%**), and the 52 rows that do carry data are the most reliable estimates in this catalog — no headline column has a median coefficient of variation above **0.037** (measured). `population_moe` is NULL on all 56 rows, so `population` here is a count to use rather than an estimate to put an interval on. Nothing is suppressed beyond the island areas: `median_gross_rent` and `median_home_value` are published for all 52 rows that carry ACS data, with median coefficients of variation of **0.004** and **0.003** (measured).

Geometries are the Census Bureau's [2024 cartographic boundary files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) for states and state equivalents (GENZ2024, 1:500,000), reprojected to EPSG:4326 and joined on `GEOID`. Cartographic rather than TIGER/Line because TIGER extends census geographies into open water while the cartographic files clip to the shoreline, which is what a choropleth wants. The boundary vintage matches the estimate vintage.

The join is driven by geometry, so a geography with 2024 boundaries but no ACS tabulation keeps its row with NULL values instead of disappearing: 4 rows (American Samoa, Guam, the Northern Mariana Islands, the U.S. Virgin Islands) in the island areas, which have cartographic boundaries but no ACS 5-year estimates because the Island Areas run a separate decennial-only program. Keeping these rows means a national map has no holes and a consumer can see the absence; dropping them would make "every US geography" quietly mean something narrower.

This is one themed chunk of six at this geography. The other themes are [Income & Poverty](https://source.coop/portolan-mirrors/us-census-catalog/states/state-income/collection.json), [People & Education](https://source.coop/portolan-mirrors/us-census-catalog/states/state-people/collection.json), [Commuting & Connectivity](https://source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/collection.json) and [Health, Disability & Income by Race](https://source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/collection.json), split that way so a consumer who wants one theme reads one file. Chunks at the same geography hold the same rows and the same geometry, so they join 1:1 on `geoid`. A sixth collection, [All Indicators](https://source.coop/portolan-mirrors/us-census-catalog/states/states/collection.json), carries all 112 columns on the same rows in one wide table — at this many features width costs little, so take that one if a question crosses themes. GEOIDs nest by prefix: the first 2 characters of every county, tract, block-group, place and district GEOID in this catalog are its state's `geoid`. Every other geography in this catalog is organized the same way — [block groups](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/catalog.json), [census tracts](https://source.coop/portolan-mirrors/us-census-catalog/tracts/catalog.json), [counties](https://source.coop/portolan-mirrors/us-census-catalog/counties/catalog.json), [ZCTAs](https://source.coop/portolan-mirrors/us-census-catalog/zctas/catalog.json), [places and CDPs](https://source.coop/portolan-mirrors/us-census-catalog/places/catalog.json) and [congressional districts](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/catalog.json) — and the [blocks](https://source.coop/portolan-mirrors/us-census-catalog/blocks/collection.json) collection carries 2020 Decennial counts, a different survey and vintage rather than a finer version of these numbers.

The PMTiles archive carries the same columns as the GeoParquet, minus the `*_moe` columns, and at every zoom the tiles are the real census geographies — there are few enough features here to draw them all at a national zoom, so this archive needs none of the coarser-geography coarse-zoom bands the catalog's finer collections carry. Built with [tylertoo](https://github.com/geoparquet-io/tylertoo). Statistics still come from the GeoParquet: margins of error are not in the tiles.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](https://source.coop/portolan-mirrors/us-census-catalog/states/state-housing/AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![ACS](https://img.shields.io/badge/ACS-blue) ![American Community Survey](https://img.shields.io/badge/American_Community_Survey-blue) ![demographics](https://img.shields.io/badge/demographics-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![margins of error](https://img.shields.io/badge/margins_of_error-blue) ![housing](https://img.shields.io/badge/housing-blue) ![rent](https://img.shields.io/badge/rent-blue) ![home values](https://img.shields.io/badge/home_values-blue) ![tenure](https://img.shields.io/badge/tenure-blue) ![vacancy](https://img.shields.io/badge/vacancy-blue) ![affordability](https://img.shields.io/badge/affordability-blue)

## Spatial Coverage

- **Bounding Box**: [-179.146711, 17.88329, -65.221081, 71.387815]

## Temporal Coverage

- **Start**: 2020-01-01T00:00:00Z
- **End**: 2024-12-31T23:59:59Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | 2-character state FIPS code, e.g. `29` for Missouri. Covers the 50 states, the District of Columbia, Puerto Rico and the four island areas. Matches `GEOID` in the 2024 cartographic boundary state file; the ACS `0400000US` prefix is stripped. |
| name | string | State name from the cartographic boundary state file's `NAME` field — "Missouri". |
| state | string | Two-letter USPS state or territory code (`MO`, `PR`, `GU`). Carried on every collection from the `STATEFP → USPS` lookup embedded in `tools/specs.py` rather than read off the boundary files, because the 2024 cartographic boundary block-group file has no `STUSPS` column while the tract, county and state files do. |
| population | int64 | Total population. Universe: total population. The single line of [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) (Total Population), published as an integer. Carried on every ACS collection so a rate can be weighted or sanity-checked without a second download. NULL on 4 of 56 rows: American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have boundaries here but no ACS 5-year data, because the island areas run a separate decennial-only program. 52 rows carry data. |
| population_moe | double | Margin of error for `population` at the 90% confidence level, the level the Census Bureau publishes. Component margins add in quadrature — `sqrt(Σ moe²)` — which is the Census Bureau's formula for the margin of a sum. NULL when every component is a jam value. |
| aland_sqkm | double | Land area in square kilometres, rounded to 3 decimals. `ALAND / 1e6` from the cartographic boundary file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
| pop_density | double | People per square kilometre of land area, rounded to 1 decimal: `population / aland_sqkm`. NULL where `ALAND` is 0 or `population` is NULL. |
| housing_units | int64 | Total housing units, occupied and vacant. Universe: housing units. Line 1 of [B25002](https://data.census.gov/table/ACSDT5Y2024.B25002) (Occupancy Status), published as an integer. |
| housing_units_moe | double | Margin of error for `housing_units` at the 90% confidence level, the level the Census Bureau publishes. Component margins add in quadrature — `sqrt(Σ moe²)` — which is the Census Bureau's formula for the margin of a sum. NULL when every component is a jam value. |
| pct_vacant_units | double | Percent of housing units that are vacant. Universe: housing units. Line 3 ("Vacant") over line 1 of [B25002](https://data.census.gov/table/ACSDT5Y2024.B25002). The ACS counts for-sale, for-rent, seasonal and migrant-worker units as vacant, so this is not a measure of abandonment. |
| pct_vacant_units_moe | double | Margin of error for `pct_vacant_units` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| households | int64 | Households — occupied housing units. One household per occupied unit, by definition. Universe: occupied housing units. Line 1 of [B25003](https://data.census.gov/table/ACSDT5Y2024.B25003) (Tenure), published as an integer. |
| households_moe | double | Margin of error for `households` at the 90% confidence level, the level the Census Bureau publishes. Component margins add in quadrature — `sqrt(Σ moe²)` — which is the Census Bureau's formula for the margin of a sum. NULL when every component is a jam value. |
| pct_owner_occupied | double | Percent of occupied housing units that are owner-occupied. Universe: occupied housing units. Line 2 ("Owner occupied") over line 1 of [B25003](https://data.census.gov/table/ACSDT5Y2024.B25003). The homeownership rate of households, not of people, and vacant units are outside the universe entirely. |
| pct_owner_occupied_moe | double | Margin of error for `pct_owner_occupied` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| median_gross_rent | double | Median gross rent in dollars per month — contract rent plus the estimated average monthly cost of utilities and fuels. Universe: renter-occupied housing units **paying cash rent**, so units occupied rent-free are excluded. Line 1 of [B25064](https://data.census.gov/table/ACSDT5Y2024.B25064). |
| median_gross_rent_moe | double | Margin of error for `median_gross_rent` at the 90% confidence level, the level the Census Bureau publishes. Published as the Census Bureau publishes it for this line. A median's margin cannot be recomputed from a distribution, so it is passed through untouched. |
| median_gross_rent_cv | double | Coefficient of variation for `median_gross_rent`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_rent_burdened | double | Percent of renter households paying 30% or more of household income on gross rent — the standard affordability threshold. Universe: renter-occupied housing units, less those whose ratio the Census could not compute. Lines 7–10 (30.0–34.9, 35.0–39.9, 40.0–49.9, 50.0 percent or more) of [B25070](https://data.census.gov/table/ACSDT5Y2024.B25070) over line 1 minus line 11 ("Not computed" — no cash rent, or no income). Including the not-computed units in the denominator would understate the burden. |
| pct_rent_burdened_moe | double | Margin of error for `pct_rent_burdened` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_rent_burdened_cv | double | Coefficient of variation for `pct_rent_burdened`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_severely_rent_burdened | double | Percent of renter households paying 50% or more of household income on gross rent. Universe: renter-occupied housing units, less those whose ratio could not be computed. Line 10 of [B25070](https://data.census.gov/table/ACSDT5Y2024.B25070) over line 1 minus line 11. A subset of `pct_rent_burdened`. |
| pct_severely_rent_burdened_moe | double | Margin of error for `pct_severely_rent_burdened` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| median_home_value | double | Median value of owner-occupied housing units, in dollars — the owner's estimate of what the property would sell for, not an assessment or a sale price. Universe: owner-occupied housing units. Line 1 of [B25077](https://data.census.gov/table/ACSDT5Y2024.B25077). |
| median_home_value_moe | double | Margin of error for `median_home_value` at the 90% confidence level, the level the Census Bureau publishes. Published as the Census Bureau publishes it for this line. A median's margin cannot be recomputed from a distribution, so it is passed through untouched. |
| median_home_value_cv | double | Coefficient of variation for `median_home_value`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_built_pre_1940 | double | Percent of housing units built in 1939 or earlier. Universe: housing units. Line 11 of [B25034](https://data.census.gov/table/ACSDT5Y2024.B25034) (Year Structure Built) over line 1. The oldest bucket the table publishes, and a standard screening proxy for lead-paint risk. |
| pct_built_pre_1940_moe | double | Margin of error for `pct_built_pre_1940` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_single_family | double | Percent of housing units in single-family structures. Universe: housing units. Lines 2 ("1, detached") + 3 ("1, attached") over line 1 of [B25024](https://data.census.gov/table/ACSDT5Y2024.B25024) (Units in Structure). Attached single-family — rowhouses, townhouses — is included; a duplex (line 4) is not. |
| pct_single_family_moe | double | Margin of error for `pct_single_family` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary state file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the state into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./state-housing.pmtiles | 1.6 MB | 12202e489ce3... |
| ./state-housing.parquet | 3.9 MB | 1220a12d8fb6... |
| ./styles/default.json | 2.3 KB | 12207ef94452... |
| ./styles/ownership.json | 2.2 KB | 122035582b68... |
| ./styles/pre-1940.json | 2.2 KB | 1220daa83216... |
| ./styles/rent-burden.json | 2.3 KB | 1220718dfddf... |
| ./styles/vacancy.json | 2.2 KB | 12204e29f3b6... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01003.dat | 17.5 MB | 122038d1a992... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25002.dat | 22.3 MB | 1220eb98debf... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25003.dat | 25.7 MB | 122068e963e1... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25024.dat | 45.6 MB | 122026ff26c6... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25034.dat | 47.8 MB | 1220806d6cb1... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25064.dat | 16.5 MB | 1220b36e6dc1... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25070.dat | 44.3 MB | 1220862ccc17... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25077.dat | 17.6 MB | 122089eb2153... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/documentation/ACS20245YR_Table_Shells.txt | 5.4 MB | 12205b46f4af... |
| https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_500k.zip | 3.1 MB | 12203e81cbb6... |
| https://www.census.gov/programs-surveys/acs/library/handbooks/general.html | - | - |
| https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf | 378.9 KB | 12204d325820... |
| https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2024_ACSSubjectDefinitions.pdf | 1.1 MB | 12206e0c5b1a... |
| https://www.census.gov/programs-surveys/geography/about/glossary.html | - | - |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./state-housing.pmtiles")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)

## Processing Notes

This collection is a themed cut of [All Indicators — States](https://source.coop/portolan-mirrors/us-census-catalog/states/states/collection.json), the wide 112-column table at this geography: the same rows, the same geometry and the same seven context columns, with 32 columns kept and the other themes' dropped. Nothing is recomputed — every value here is the value in the wide file — so the build notes below describe the single ACS read both were made from.

Built 2026-11-12 from the ACS 2020–2024 5-year table-based Summary File (https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/), downloaded the same day over plain HTTPS — the summary file needs no API key. Tables read for this collection: B01003, B25002, B25003, B25024, B25034, B25064, B25070, B25077. Each national `.dat` file is one row per geography with estimate and margin of error side by side, and every summary level is picked off `GEO_ID` by prefix in a single pass per file — this collection's is `0400000US`, read off the files themselves rather than taken from a summary-level table.

Jam values (the sentinels the ACS publishes in place of unestimable values, e.g. -666666666 for an uncomputable median, and -555555555 for a controlled MOE) become NULL: any estimate or margin at or below -111111111 is dropped rather than published as a number. Counts are sums of the specified lines with margins added in quadrature; percentages use the Census Bureau's proportion formula with the ratio formula as fallback; medians are passed through untouched; coefficients of variation are `moe / 1.645 / estimate` on the headline columns. Every line number is pinned against the release's own table shells before the build starts (44 pins verified, 0 failures, plus 4 derived line groups resolved from the shells), so a vintage bump that moves a line fails loudly instead of publishing a mislabeled column.

Geometry is the 2024 cartographic boundary file (cb_2024_us_state_500k.zip) for states and state equivalents (1:500,000), reprojected to EPSG:4326 with ogr2ogr — not DuckDB's `ST_Transform`, which computes correct coordinates but stamps the source CRS into the GeoParquet metadata. Geometry drives the join, so a geography with boundaries but no ACS tabulation keeps its row with NULL values.

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

**`population_moe` is NULL on every row at this geography.** Measured: carried on none of the 56 rows. `sqrt(sum(moe*moe))` over a NULL-bearing column returns NULL, so check before putting one in a quadrature sum, and read this count as something to use rather than as an estimate to put an interval on. Every other `*_moe` column in this collection is populated on every row where its estimate is — measured, with no exceptions.

That NULL is upstream, and it is not suppression: the column comes from a total-population table (B01003), and in the release's own `.dat` files those rows carry the estimate beside `-555555555`, the **controlled-MOE** jam value a controlled estimate gets in place of a sampling margin. The build turns it into NULL rather than publishing it as a number — `0500000US01001|59947|-555555555` in `acsdt5y2024-b01003.dat`, read 2026-11-15. The same column carries a margin normally at the finer geographies, where the estimates are not controlled this way: `population_moe` is carried on 33,759 of 33,791 ZCTAs and on all 241,854 populated block groups (measured).

Margins of error are negligible at this geography — no column has a median coefficient of variation above 0.037, and no single value above 0.213 (measured), so nothing here needs a reliability filter. They are still margins: check whether two states' margins overlap before calling a difference real, and never aggregate a median. A state's value is estimated directly by the Census Bureau and is not the sum or the average of its counties.

The PMTiles archive is real geographies at every zoom, with no coarser-geography coarse-zoom band (the catalog's finer collections switch to counties and tracts at coarse zooms; this one has few enough features not to). `*_moe` columns are not in the tiles — statistics come from the GeoParquet.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
