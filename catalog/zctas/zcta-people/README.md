# People & Education — ZIP Code Tabulation Areas

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/collection.json)** · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/zcta-people.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

Who lives here: median age and the shares under 18 and 65 or over ([B01002](https://data.census.gov/table/ACSDT5Y2024.B01002), [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001)), the four mutually exclusive non-Hispanic race shares this catalog carries — White, Black or African American, American Indian and Alaska Native, Asian — plus Hispanic or Latino of any race and its complement, people of color ([B03002](https://data.census.gov/table/ACSDT5Y2024.B03002)), and the share of adults 25 and over holding a bachelor's degree or higher ([B15003](https://data.census.gov/table/ACSDT5Y2024.B15003)).

Curated indicators for all **33,791** ZIP Code Tabulation Areas in the United States, Puerto Rico and the island areas, from the U.S. Census Bureau's [American Community Survey](https://www.census.gov/programs-surveys/acs.html) **2020–2024 5-year estimates** (`acsdt5y2024`, the table-based [Summary File](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)). The Census Bureau calls the ACS "the premier source of detailed information about the nation's people and housing". The 5-year file is the only ACS release published for ZCTAs at all — [areas published](https://www.census.gov/programs-surveys/acs/geography-acs/areas-published.html) lists the 5-digit ZCTA under the 5-year estimates and nowhere else.

Every estimate ships with its margin of error — `<column>_moe`, at the 90% confidence level, the level the Census Bureau publishes — and the headline statistics also carry a coefficient of variation (`<column>_cv` = `moe / 1.645 / estimate`) so small-area noise can be flagged rather than mapped as if certain. Derived percentages propagate error with the Census Bureau's own formulas from [ACS Accuracy of the Data](https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf): sums add in quadrature, proportions use the subset formula with the ratio formula as fallback. ACS jam values for suppressed or unestimable cells are NULL here, never numbers, and medians are published as the Bureau publishes them — a median cannot be aggregated to a larger area. Each column's description names its ACS table, its exact universe, and the lines summed to make it.

A ZIP Code Tabulation Area [is not a ZIP code](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html) — it is the Census Bureau's block-built approximation of a USPS 5-digit delivery area — and it nests in nothing, so `state` is NULL on every row and there is no prefix join to counties or tracts. Relating ZCTAs to other geographies is a spatial operation. Beyond the 19 polygons with no ACS row at all, suppression here is small: `median_age` is NULL on **2.87%** of ZCTAs and `pct_bachelors_plus` on **2.04%** (measured).

Geometries are the Census Bureau's [2020 cartographic boundary files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) for ZIP Code Tabulation Areas (GENZ2020, 1:500,000), reprojected to EPSG:4326 and joined on `GEOID`. Cartographic rather than TIGER/Line because TIGER extends census geographies into open water while the cartographic files clip to the shoreline, which is what a choropleth wants. GENZ2020 and not GENZ2024 because no cartographic ZCTA file has been published since: the 2020-based ZCTAs are the current ones, and they are the vintage this release tabulates ([ACS geography boundaries by year](https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year/2024.html) gives 5-digit ZCTA as "2020 Census"). The ZCTA file is also the one boundary file in this catalog with no state attribute, which is why `state` is NULL here.

The join is driven by geometry, so a geography with 2020 boundaries but no ACS tabulation keeps its row with NULL values instead of disappearing: 17 ZCTAs in the island areas, which have cartographic boundaries but no ACS 5-year estimates because the Island Areas run a separate decennial-only program. Two more, 11717 and 11798, have boundaries and no matching ACS row, both in Suffolk County, New York — the county whose 2024 re-delineation also leaves 14 tracts and 39 block groups without ACS rows elsewhere in this catalog. No ACS ZCTA row is dropped in the other direction: all 33,772 tabulated ZCTAs have a polygon. Keeping these rows means a national map has no holes and a consumer can see the absence; dropping them would make "every US geography" quietly mean something narrower.

This is one themed chunk of five at this geography. The other themes are [Income & Poverty](https://source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/collection.json), [Housing & Rent](https://source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/collection.json), [Commuting & Connectivity](https://source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/collection.json) and [Health, Disability & Income by Race](https://source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/collection.json), split that way so a consumer who wants one theme reads one file. Chunks at the same geography hold the same rows and the same geometry, so they join 1:1 on `geoid`. A sixth collection, [All Indicators](https://source.coop/portolan-mirrors/us-census-catalog/zctas/zctas/collection.json), carries all 135 columns on the same rows in one wide table — at this many features width costs little, so take that one if a question crosses themes. A ZCTA nests in nothing: it can cross county and state lines, so there is no prefix join from `geoid` to any other collection here, and `state` is NULL on every row. Relating ZCTAs to counties or tracts is a spatial operation (or a Census relationship file), not a string operation. Every other geography in this catalog is organized the same way — [block groups](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/catalog.json), [census tracts](https://source.coop/portolan-mirrors/us-census-catalog/tracts/catalog.json), [counties](https://source.coop/portolan-mirrors/us-census-catalog/counties/catalog.json), [states](https://source.coop/portolan-mirrors/us-census-catalog/states/catalog.json), [places and CDPs](https://source.coop/portolan-mirrors/us-census-catalog/places/catalog.json) and [congressional districts](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/catalog.json) — and the [blocks](https://source.coop/portolan-mirrors/us-census-catalog/blocks/collection.json) collection carries 2020 Decennial counts, a different survey and vintage rather than a finer version of these numbers.

The PMTiles archive is a census-geography pyramid built with [tylertoo](https://github.com/geoparquet-io/tylertoo): z0–z5 are county polygons carrying the Census Bureau's own published county estimates, and z6–z12 are the ZIP Code Tabulation Areas themselves. ZCTAs do not nest inside counties, so the county band is orientation at national zooms — real county values — and not a roll-up of these features. Thinning this many polygons down to a national zoom would show a biased subset (small urban geographies drop first) rather than less data, so the coarse zooms step up to a coarser census geography instead of a thinned sample of this one. Every band carries the same column names, so one style expression classifies every zoom — but below z6 you are looking at counties, not ZIP Code Tabulation Areas, and the values there are the Bureau's official estimates for those geographies, with their own meaning, rather than a visualization-only average: clicking a coarse feature identifies a real county by `geoid` and `name`. The `*_moe` columns are excluded from the tiles at every zoom — a margin of error is computed for one specific geography and cannot be carried across bands — while the `*_cv` columns are kept. Statistics come from the GeoParquet, never from the tiles.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](https://source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![ACS](https://img.shields.io/badge/ACS-blue) ![American Community Survey](https://img.shields.io/badge/American_Community_Survey-blue) ![demographics](https://img.shields.io/badge/demographics-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![margins of error](https://img.shields.io/badge/margins_of_error-blue) ![age](https://img.shields.io/badge/age-blue) ![race](https://img.shields.io/badge/race-blue) ![ethnicity](https://img.shields.io/badge/ethnicity-blue) ![education](https://img.shields.io/badge/education-blue) ![equity](https://img.shields.io/badge/equity-blue) ![ZCTA](https://img.shields.io/badge/ZCTA-blue)

## Spatial Coverage

- **Bounding Box**: [-176.696678, 17.926684, -65.221081, 71.341223]

## Temporal Coverage

- **Start**: 2020-01-01T00:00:00Z
- **End**: 2024-12-31T23:59:59Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | 5-digit ZIP Code Tabulation Area code, e.g. `90210`. **Not a ZIP code**: a ZCTA is the Census Bureau's approximation of the area a USPS 5-digit ZIP delivery area covers, built from 2020 census blocks, and the two are not interchangeable (see the collection's known issues). ZCTAs do not nest in any other census geography — a ZCTA can cross county and state lines — so there is no prefix join to counties, tracts or states, and the first two characters are a postal region, not a state FIPS code. Matches `GEOID20`/`ZCTA5CE20` in the Census Bureau's 2020 cartographic boundary ZCTA file; the ACS `860Z200US` prefix is stripped. |
| name | string | `'ZCTA5 ' || ZCTA5CE20` from the 2020 cartographic boundary ZCTA file — "ZCTA5 90210". A ZCTA has no containing geography to name it by, because it crosses county and state lines, and the Census Bureau publishes no other name for one; this is the label data.census.gov uses. |
| state | string | Always NULL in this collection. A ZIP Code Tabulation Area is not inside any state: it approximates a USPS ZIP delivery area, which can cross state lines, the ACS publishes ZCTAs at the nation level only, and the 2020 cartographic boundary ZCTA file carries no state attribute (its fields are `ZCTA5CE20`, `AFFGEOID20`, `GEOID20`, `NAME20`, `LSAD20`, `ALAND20`, `AWATER20`). The column is kept so the schema matches the other collections; deriving a value from the first digits of the code would be wrong, because those are a postal region. To assign ZCTAs to states, do it spatially, and expect ties. |
| population | int64 | Total population. Universe: total population. The single line of [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) (Total Population), published as an integer. Carried on every ACS collection so a rate can be weighted or sanity-checked without a second download. NULL on 0.06% of ZCTAs — the 19 ZCTAs that have a 2020 cartographic boundary but no row in the ACS tabulation (17 in the island areas, plus 11717 and 11798 in Suffolk County, New York). |
| population_moe | double | Margin of error for `population` at the 90% confidence level, the level the Census Bureau publishes. Component margins add in quadrature — `sqrt(Σ moe²)` — which is the Census Bureau's formula for the margin of a sum. NULL when every component is a jam value. |
| aland_sqkm | double | Land area in square kilometres, rounded to 3 decimals. `ALAND20 / 1e6` from the 2020 cartographic boundary ZCTA file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
| pop_density | double | People per square kilometre of land area, rounded to 1 decimal: `population / aland_sqkm`. NULL where `ALAND` is 0 or `population` is NULL. |
| median_age | double | Median age in years. Universe: total population. Line 1 of [B01002](https://data.census.gov/table/ACSDT5Y2024.B01002) (Median Age by Sex); the male and female medians on lines 2 and 3 are not published here. Like every median, not aggregable. |
| median_age_moe | double | Margin of error for `median_age` at the 90% confidence level, the level the Census Bureau publishes. Published as the Census Bureau publishes it for this line. A median's margin cannot be recomputed from a distribution, so it is passed through untouched. |
| pct_under_18 | double | Percent of the population under 18 years old. Universe: total population. The under-18 lines of [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001) (Sex by Age) over line 1. The components are resolved from the table shells by label — "Under 5 years", "5 to 9 years", "10 to 14 years", "15 to 17 years", once per sex, 8 lines for this vintage — so a renumbered line fails the build instead of silently shifting. |
| pct_under_18_moe | double | Margin of error for `pct_under_18` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_65_plus | double | Percent of the population 65 years and over. Universe: total population. The 65-and-over lines of [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001) over line 1, resolved from the shells by label ("65 and 66 years" through "85 years and over", once per sex, 12 lines for this vintage). |
| pct_65_plus_moe | double | Margin of error for `pct_65_plus` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_white_nh | double | Percent of the population that is White alone and not Hispanic or Latino. Universe: total population. Line 3 of [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) over line 1 — line 3 sits under line 2, "Not Hispanic or Latino", so this is the non-Hispanic branch. |
| pct_white_nh_moe | double | Margin of error for `pct_white_nh` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_black | double | Percent of the population that is Black or African American alone and not Hispanic or Latino. Universe: total population. Line 4 of [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) over line 1 (the "Not Hispanic or Latino" branch, so this share and `pct_hispanic` do not overlap). |
| pct_black_moe | double | Margin of error for `pct_black` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_native | double | Percent of the population that is American Indian and Alaska Native alone and not Hispanic or Latino. Universe: total population. Line 5 of [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) over line 1. Small everywhere outside Indian Country and reservations, and at block-group scale usually within its own margin of error. |
| pct_native_moe | double | Margin of error for `pct_native` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_asian | double | Percent of the population that is Asian alone and not Hispanic or Latino. Universe: total population. Line 6 of [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) over line 1. |
| pct_asian_moe | double | Margin of error for `pct_asian` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_hispanic | double | Percent of the population that is Hispanic or Latino, of any race. Universe: total population. Line 12 of [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) over line 1. Hispanic origin is asked separately from race, which is why this crosses every race category; here it is disjoint from the five race shares because those are all drawn from the non-Hispanic branch. |
| pct_hispanic_moe | double | Margin of error for `pct_hispanic` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_people_of_color | double | Percent of the population that is **not** White-alone non-Hispanic: `100 − pct_white_nh`. Universe: total population. Derived from [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002). A complement, so it carries `pct_white_nh`'s own margin of error unchanged — a share and its complement have the same sampling error. |
| pct_people_of_color_moe | double | Margin of error for `pct_people_of_color` at the 90% confidence level, the level the Census Bureau publishes. A complement carries the margin of error of the share it was taken from, unchanged — `100 − p` has the same sampling error as `p`. |
| pct_bachelors_plus | double | Percent of adults 25 and over whose highest attainment is a bachelor's degree or more. Universe: population 25 years and over. Lines 22–25 of [B15003](https://data.census.gov/table/ACSDT5Y2024.B15003) (Bachelor's, Master's, Professional school, Doctorate) over line 1. Associate's degrees (line 21) are deliberately excluded. |
| pct_bachelors_plus_moe | double | Margin of error for `pct_bachelors_plus` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2020 cartographic boundary ZIP Code Tabulation Area file (GENZ2020, 1:500,000), which clips to the shoreline — TIGER/Line would extend the ZIP Code Tabulation Area into open water. GENZ2020 because the Census Bureau has published no cartographic ZCTA file since: the 2020-based ZCTAs are the current ones, and they are the vintage the ACS tabulates. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./zcta-people.pmtiles | 191.1 MB | 1220ee7f0a04... |
| ./zcta-people.parquet | 66.3 MB | 1220ccad7005... |
| ./thumbnail.png | 90.9 KB | 1220833f0a8f... |
| ./styles/default.json | 1.9 KB | 1220c0290408... |
| ./styles/education.json | 1.8 KB | 12201952b1a4... |
| ./styles/people-of-color.json | 1.8 KB | 1220837b5c0b... |
| ./styles/seniors.json | 1.7 KB | 1220b7dbe54a... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01001.dat | 191.1 MB | 12201637b18a... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01002.dat | 25.4 MB | 122004784637... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01003.dat | 17.5 MB | 122038d1a992... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b03002.dat | 79.4 MB | 1220ef1a9310... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b15003.dat | 88.0 MB | 1220d0c8609e... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/documentation/ACS20245YR_Table_Shells.txt | 5.4 MB | 12205b46f4af... |
| https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip | 63.6 MB | 1220c69a4ede... |
| https://www2.census.gov/geo/docs/maps-data/data/geo_tallies2020/Natl_Geographic_Tallies_2020.txt | 1.7 KB | 122006db85a1... |
| https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html | - | - |
| https://www.census.gov/programs-surveys/acs/library/handbooks/general.html | - | - |
| https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf | 378.9 KB | 12204d325820... |
| https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2024_ACSSubjectDefinitions.pdf | 1.1 MB | 12206e0c5b1a... |
| https://www.census.gov/programs-surveys/geography/about/glossary.html | - | - |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./zcta-people.pmtiles")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)

## Processing Notes

This collection is a themed cut of [All Indicators — ZIP Code Tabulation Areas](https://source.coop/portolan-mirrors/us-census-catalog/zctas/zctas/collection.json), the wide 135-column table at this geography: the same rows, the same geometry and the same seven context columns, with 29 columns kept and the other themes' dropped. Nothing is recomputed — every value here is the value in the wide file — so the build notes below describe the single ACS read both were made from.

Built 2026-11-12 from the ACS 2020–2024 5-year table-based Summary File (https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/), downloaded the same day over plain HTTPS — the summary file needs no API key. Tables read for this collection: B01001, B01002, B01003, B03002, B15003. Each national `.dat` file is one row per geography with estimate and margin of error side by side, and every summary level is picked off `GEO_ID` by prefix in a single pass per file — this collection's is `860Z200US`, read off the files themselves rather than taken from a summary-level table (the `Z2` is the 2020 ZCTA vintage).

Jam values (the sentinels the ACS publishes in place of unestimable values, e.g. -666666666 for an uncomputable median, and -555555555 for a controlled MOE) become NULL: any estimate or margin at or below -111111111 is dropped rather than published as a number. Counts are sums of the specified lines with margins added in quadrature; percentages use the Census Bureau's proportion formula with the ratio formula as fallback; medians are passed through untouched; coefficients of variation are `moe / 1.645 / estimate` on the headline columns. Every line number is pinned against the release's own table shells before the build starts (44 pins verified, 0 failures, plus 4 derived line groups resolved from the shells), so a vintage bump that moves a line fails loudly instead of publishing a mislabeled column.

Geometry is the 2020 cartographic boundary file (cb_2020_us_zcta520_500k.zip) for ZIP Code Tabulation Areas (1:500,000), reprojected to EPSG:4326 with ogr2ogr — not DuckDB's `ST_Transform`, which computes correct coordinates but stamps the source CRS into the GeoParquet metadata. Geometry drives the join, so a geography with boundaries but no ACS tabulation keeps its row with NULL values.

Cross-checked end to end against the published St. Louis census catalog, which runs the same formulas on the same vintage: 314 of 314 block groups joined, 0 mismatches on median household income, its margin of error, the poverty rate and its margin of error — exact equality, not approximate.

Validated: 33,791 rows against the 33,791 ZCTAs in the Census Bureau's own [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html) (33,642 US + 132 Puerto Rico + 17 island areas), 33,791 distinct `geoid`, no percentage outside 0–100, every one of the 33,772 tabulated ACS ZCTAs matched to a polygon, and 19 polygons with no ACS row kept with NULL values. Spot-checked against data.census.gov: 90210 median household income $187,801, 00601 (Adjuntas, PR) $19,454, 60614 (Chicago) $136,448.

Converted to GeoParquet with geoparquet-io (gpio): ZSTD compression, Hilbert row order, and a covering `bbox` column with row-group statistics, so a spatial filter can skip most of the file over the network. Tiled to PMTiles with tylertoo as a census-geography pyramid, so coarse zooms carry a coarser census geography — counties, then tracts — with that geography's own official values, instead of a thinned sample of this collection's features; the collections small enough to draw nationally (counties, states, congressional districts) are tiled as real polygons at every zoom.


## Attribution

U.S. Census Bureau

## License

[CC0-1.0](https://www.census.gov/about/policies/open-gov/open-data.html)

## Contact

Chris Holmes <cholmes@9eo.org>

## Known Issues

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 17 ZCTAs, 279 places and 4 delegate districts.

**A ZCTA is not a ZIP code.** ZIP Code Tabulation Areas are the Census Bureau's approximation of USPS 5-digit ZIP delivery areas, built by assigning each 2020 census block the most common ZIP code of the addresses in it ([what a ZCTA is](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html)). Consequences that bite: a ZCTA boundary is not a ZIP boundary, some ZIP codes have no ZCTA (PO-box-only and point ZIPs), ZCTA codes can differ from the ZIP code of an address inside them, and the Bureau re-delineates them only with each decennial census. Joining customer ZIP codes to this file is an approximation, and it is the user's job to say so.

`state` is NULL on every row and there is no prefix join. A ZCTA can cross state and county lines, the ACS tabulates ZCTAs at the nation level only, and the 2020 cartographic boundary ZCTA file carries no state attribute to fall back on. The column is kept so the schema matches the catalog's other collections. Assign ZCTAs to states spatially (and expect ties), or use a Census relationship file.

Two ZCTAs — 11717 and 11798, in Suffolk County, New York — have 2020 boundaries but no row in this ACS tabulation and publish with NULL values; they are the same two communities (Brentwood and Wyandanch) that the re-delineated Suffolk County tracts and block groups show up in elsewhere in this catalog.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: below z6 you are looking at counties, not ZIP Code Tabulation Areas. The values there are the Census Bureau's own estimates for those geographies, not an aggregation of this file, and `*_moe` columns are not in the tiles. Statistics come from the GeoParquet.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
