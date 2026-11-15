# Commuting & Connectivity — States

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/collection.json)** · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

How people get around and get online: households with no vehicle available, as a count and a share ([B25044](https://data.census.gov/table/ACSDT5Y2024.B25044)); commute mode shares for driving alone, public transportation, walking or cycling, and working from home ([B08301](https://data.census.gov/table/ACSDT5Y2024.B08301)); the share of commutes of 45 minutes or more ([B08303](https://data.census.gov/table/ACSDT5Y2024.B08303)); and the shares of households with no internet access and no computing device ([B28002](https://data.census.gov/table/ACSDT5Y2024.B28002), [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001)).

Curated indicators for all **56** states and state equivalents in the United States, Puerto Rico and the island areas, from the U.S. Census Bureau's [American Community Survey](https://www.census.gov/programs-surveys/acs.html) **2020–2024 5-year estimates** (`acsdt5y2024`, the table-based [Summary File](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)). The Census Bureau calls the ACS "the premier source of detailed information about the nation's people and housing". The Bureau also publishes 1-year estimates at this geography; the 5-year release is used throughout this catalog so every geography in it is the same vintage and directly comparable.

Every estimate ships with its margin of error — `<column>_moe`, at the 90% confidence level, the level the Census Bureau publishes — and the headline statistics also carry a coefficient of variation (`<column>_cv` = `moe / 1.645 / estimate`) so small-area noise can be flagged rather than mapped as if certain. Derived percentages propagate error with the Census Bureau's own formulas from [ACS Accuracy of the Data](https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf): sums add in quadrature, proportions use the subset formula with the ratio formula as fallback. ACS jam values for suppressed or unestimable cells are NULL here, never numbers, and medians are published as the Bureau publishes them — a median cannot be aggregated to a larger area. Each column's description names its ACS table, its exact universe, and the lines summed to make it.

Fifty-six rows: the 50 states, the District of Columbia, Puerto Rico and the four island areas. The island-area rows carry geometry and no ACS estimates, so every value column is NULL on 4 of 56 rows (**7.14%**), and the 52 rows that do carry data are the most reliable estimates in this catalog — no headline column has a median coefficient of variation above **0.037** (measured). `population_moe` is NULL on all 56 rows, so `population` here is a count to use rather than an estimate to put an interval on. Nothing is suppressed beyond the island areas, and even `pct_commute_transit` — the noisiest column in this catalog at every finer geography — has a median coefficient of variation of **0.037** here and a maximum of **0.197** (measured).

Geometries are the Census Bureau's [2024 cartographic boundary files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) for states and state equivalents (GENZ2024, 1:500,000), reprojected to EPSG:4326 and joined on `GEOID`. Cartographic rather than TIGER/Line because TIGER extends census geographies into open water while the cartographic files clip to the shoreline, which is what a choropleth wants. The boundary vintage matches the estimate vintage.

The join is driven by geometry, so a geography with 2024 boundaries but no ACS tabulation keeps its row with NULL values instead of disappearing: 4 rows (American Samoa, Guam, the Northern Mariana Islands, the U.S. Virgin Islands) in the island areas, which have cartographic boundaries but no ACS 5-year estimates because the Island Areas run a separate decennial-only program. Keeping these rows means a national map has no holes and a consumer can see the absence; dropping them would make "every US geography" quietly mean something narrower.

This is one themed chunk of six at this geography. The other themes are [Income & Poverty](https://source.coop/portolan-mirrors/us-census-catalog/states/state-income/collection.json), [People & Education](https://source.coop/portolan-mirrors/us-census-catalog/states/state-people/collection.json), [Housing & Rent](https://source.coop/portolan-mirrors/us-census-catalog/states/state-housing/collection.json) and [Health, Disability & Income by Race](https://source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/collection.json), split that way so a consumer who wants one theme reads one file. Chunks at the same geography hold the same rows and the same geometry, so they join 1:1 on `geoid`. A sixth collection, [All Indicators](https://source.coop/portolan-mirrors/us-census-catalog/states/states/collection.json), carries all 135 columns on the same rows in one wide table — at this many features width costs little, so take that one if a question crosses themes. GEOIDs nest by prefix: the first 2 characters of every county, tract, block-group, place and district GEOID in this catalog are its state's `geoid`. Every other geography in this catalog is organized the same way — [block groups](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/catalog.json), [census tracts](https://source.coop/portolan-mirrors/us-census-catalog/tracts/catalog.json), [counties](https://source.coop/portolan-mirrors/us-census-catalog/counties/catalog.json), [ZCTAs](https://source.coop/portolan-mirrors/us-census-catalog/zctas/catalog.json), [places and CDPs](https://source.coop/portolan-mirrors/us-census-catalog/places/catalog.json) and [congressional districts](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/catalog.json) — and the [blocks](https://source.coop/portolan-mirrors/us-census-catalog/blocks/collection.json) collection carries 2020 Decennial counts, a different survey and vintage rather than a finer version of these numbers.

The PMTiles archive carries the same columns as the GeoParquet, minus the `*_moe` columns, and at every zoom the tiles are the real census geographies — there are few enough features here to draw them all at a national zoom, so this archive needs none of the coarser-geography coarse-zoom bands the catalog's finer collections carry. Built with [tylertoo](https://github.com/geoparquet-io/tylertoo). Statistics still come from the GeoParquet: margins of error are not in the tiles.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](https://source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![ACS](https://img.shields.io/badge/ACS-blue) ![American Community Survey](https://img.shields.io/badge/American_Community_Survey-blue) ![demographics](https://img.shields.io/badge/demographics-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![margins of error](https://img.shields.io/badge/margins_of_error-blue) ![commuting](https://img.shields.io/badge/commuting-blue) ![transit](https://img.shields.io/badge/transit-blue) ![vehicles](https://img.shields.io/badge/vehicles-blue) ![internet access](https://img.shields.io/badge/internet_access-blue) ![digital divide](https://img.shields.io/badge/digital_divide-blue) ![states](https://img.shields.io/badge/states-blue)

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
| hh_no_vehicle | int64 | Occupied housing units with no vehicle available, owner- and renter-occupied combined. Universe: occupied housing units. Lines 3 + 10 of [B25044](https://data.census.gov/table/ACSDT5Y2024.B25044) (Tenure by Vehicles Available) — the "No vehicle available" line under each tenure — which is what makes this a tenure-blind count. Published as an integer; the two margins of error add in quadrature. |
| hh_no_vehicle_moe | double | Margin of error for `hh_no_vehicle` at the 90% confidence level, the level the Census Bureau publishes. Component margins add in quadrature — `sqrt(Σ moe²)` — which is the Census Bureau's formula for the margin of a sum. NULL when every component is a jam value. |
| pct_hh_no_vehicle | double | Percent of occupied housing units with no vehicle available. Universe: occupied housing units. Lines 3 + 10 over line 1 of [B25044](https://data.census.gov/table/ACSDT5Y2024.B25044). Households, not people: a car-free household of four counts once. |
| pct_hh_no_vehicle_moe | double | Margin of error for `pct_hh_no_vehicle` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_hh_no_vehicle_cv | double | Coefficient of variation for `pct_hh_no_vehicle`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_commute_drive_alone | double | Percent of workers who drove alone to work in a car, truck or van. Universe: workers 16 years and over. Line 3 ("Drove alone", under "Car, truck, or van") over line 1 of [B08301](https://data.census.gov/table/ACSDT5Y2024.B08301) (Means of Transportation to Work). The ACS asks about the usual means of transportation in the reference week, so a hybrid commuter reports one mode. |
| pct_commute_drive_alone_moe | double | Margin of error for `pct_commute_drive_alone` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_commute_transit | double | Percent of workers who commuted by public transportation. Universe: workers 16 years and over. Line 10 ("Public transportation") over line 1 of [B08301](https://data.census.gov/table/ACSDT5Y2024.B08301), which covers bus, subway and elevated rail, light rail, commuter rail and ferryboat. Taxi and ride-hailing (line 16) are a separate category in this vintage and are **not** included. |
| pct_commute_transit_moe | double | Margin of error for `pct_commute_transit` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_commute_transit_cv | double | Coefficient of variation for `pct_commute_transit`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_commute_walk_bike | double | Percent of workers who walked or bicycled to work. Universe: workers 16 years and over. Lines 18 ("Bicycle") + 19 ("Walked") over line 1 of [B08301](https://data.census.gov/table/ACSDT5Y2024.B08301). |
| pct_commute_walk_bike_moe | double | Margin of error for `pct_commute_walk_bike` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_work_from_home | double | Percent of workers who worked from home. Universe: workers 16 years and over. Line 21 ("Worked from home") over line 1 of [B08301](https://data.census.gov/table/ACSDT5Y2024.B08301). In a 2020–2024 5-year estimate this averages over the pandemic shift and its partial reversal, so it is not a reading of any single year. |
| pct_work_from_home_moe | double | Margin of error for `pct_work_from_home` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_commute_45min_plus | double | Percent of commuters whose one-way travel time to work is 45 minutes or more. Universe: workers 16 years and over **who did not work from home** — the table's own universe, which is why work-from-home does not deflate this share. Lines 11 + 12 + 13 (45 to 59 minutes, 60 to 89, 90 or more) over line 1 of [B08303](https://data.census.gov/table/ACSDT5Y2024.B08303) (Travel Time to Work). |
| pct_commute_45min_plus_moe | double | Margin of error for `pct_commute_45min_plus` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_no_internet | double | Percent of households with no internet access of any kind. Universe: households. Line 13 ("No Internet access") over line 1 of [B28002](https://data.census.gov/table/ACSDT5Y2024.B28002). Households that use the internet without paying for a subscription (line 12) are counted as having access, so this is the floor of the digital divide, not its full extent. |
| pct_no_internet_moe | double | Margin of error for `pct_no_internet` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_no_internet_cv | double | Coefficient of variation for `pct_no_internet`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_no_computer | double | Percent of households with no computing device — no desktop or laptop, no smartphone, no tablet, no other computer. Universe: households. Line 11 ("No Computer") over line 1 of [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001) (Types of Computers in Household). |
| pct_no_computer_moe | double | Margin of error for `pct_no_computer` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary state file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the state into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./state-connectivity.pmtiles | 1.6 MB | 1220545546c5... |
| ./state-connectivity.parquet | 3.9 MB | 1220070c3f52... |
| ./thumbnail.png | 25.4 KB | 12208799deca... |
| ./styles/default.json | 2.2 KB | 1220ca502e91... |
| ./styles/no-vehicle.json | 2.2 KB | 12201d5c9a7b... |
| ./styles/transit-commute.json | 2.3 KB | 122048316562... |
| ./styles/work-from-home.json | 2.2 KB | 1220096debe2... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01003.dat | 17.5 MB | 122038d1a992... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b08301.dat | 84.4 MB | 1220552b24c1... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b08303.dat | 61.2 MB | 12201b9b9243... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b25044.dat | 60.4 MB | 1220db636e7d... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b28001.dat | 49.1 MB | 1220c9a43c12... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b28002.dat | 55.4 MB | 122012446ff0... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/documentation/ACS20245YR_Table_Shells.txt | 5.4 MB | 12205b46f4af... |
| https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_500k.zip | 3.1 MB | 12203e81cbb6... |
| https://www.census.gov/programs-surveys/acs/library/handbooks/general.html | - | - |
| https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf | 378.9 KB | 12204d325820... |
| https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2024_ACSSubjectDefinitions.pdf | 1.1 MB | 12206e0c5b1a... |
| https://www.census.gov/programs-surveys/geography/about/glossary.html | - | - |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./state-connectivity.pmtiles")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)

## Processing Notes

This collection is a themed cut of [All Indicators — States](https://source.coop/portolan-mirrors/us-census-catalog/states/states/collection.json), the wide 135-column table at this geography: the same rows, the same geometry and the same seven context columns, with 30 columns kept and the other themes' dropped. Nothing is recomputed — every value here is the value in the wide file — so the build notes below describe the single ACS read both were made from.

Built 2026-11-12 from the ACS 2020–2024 5-year table-based Summary File (https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/), downloaded the same day over plain HTTPS — the summary file needs no API key. Tables read for this collection: B01003, B08301, B08303, B25044, B28001, B28002. Each national `.dat` file is one row per geography with estimate and margin of error side by side, and every summary level is picked off `GEO_ID` by prefix in a single pass per file — this collection's is `0400000US`, read off the files themselves rather than taken from a summary-level table.

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
