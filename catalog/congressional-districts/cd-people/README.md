# People & Education — Congressional Districts (119th Congress)

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/collection.json)** · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/cd-people.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

Who lives here: median age and the shares under 18 and 65 or over ([B01002](https://data.census.gov/table/ACSDT5Y2024.B01002), [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001)), the four mutually exclusive non-Hispanic race shares this catalog carries — White, Black or African American, American Indian and Alaska Native, Asian — plus Hispanic or Latino of any race and its complement, people of color ([B03002](https://data.census.gov/table/ACSDT5Y2024.B03002)), and the share of adults 25 and over holding a bachelor's degree or higher ([B15003](https://data.census.gov/table/ACSDT5Y2024.B15003)).

Curated indicators for all **441** congressional districts of the 119th Congress in the United States, Puerto Rico and the island areas, from the U.S. Census Bureau's [American Community Survey](https://www.census.gov/programs-surveys/acs.html) **2020–2024 5-year estimates** (`acsdt5y2024`, the table-based [Summary File](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)). The Census Bureau calls the ACS "the premier source of detailed information about the nation's people and housing". The Bureau also publishes 1-year estimates at this geography; the 5-year release is used throughout this catalog so every geography in it is the same vintage and directly comparable.

Every estimate ships with its margin of error — `<column>_moe`, at the 90% confidence level, the level the Census Bureau publishes — and the headline statistics also carry a coefficient of variation (`<column>_cv` = `moe / 1.645 / estimate`) so small-area noise can be flagged rather than mapped as if certain. Derived percentages propagate error with the Census Bureau's own formulas from [ACS Accuracy of the Data](https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf): sums add in quadrature, proportions use the subset formula with the ratio formula as fallback. ACS jam values for suppressed or unestimable cells are NULL here, never numbers, and medians are published as the Bureau publishes them — a median cannot be aggregated to a larger area. Each column's description names its ACS table, its exact universe, and the lines summed to make it.

Districts are equal-population by construction — 546,488 to 1,021,191 people across the 435 voting districts, 771,301 at the median of all 437 rows with data (measured) — so the distribution of every rate here is far tighter than at any other geography, and the map styles' class breaks are measured accordingly. These are the districts of the **119th Congress** ([the vintage this ACS release tabulates](https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year/2024.html)); district numbers are not stable across congresses, so do not join these GEOIDs to an earlier congress's districts of the same number. Nothing is suppressed beyond the four island-area delegate districts, which are NULL on every column (**0.91%** of rows).

Geometries are the Census Bureau's [2024 cartographic boundary files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) for congressional districts of the 119th Congress (GENZ2024, 1:500,000), reprojected to EPSG:4326 and joined on `GEOID`. Cartographic rather than TIGER/Line because TIGER extends census geographies into open water while the cartographic files clip to the shoreline, which is what a choropleth wants. The file is `cb_2024_us_cd119_500k` — `CDSESSN = '119'` on all 441 features — matching the congress this release tabulates.

The join is driven by geometry, so a geography with 2024 boundaries but no ACS tabulation keeps its row with NULL values instead of disappearing: 4 delegate districts (American Samoa, Guam, the Northern Mariana Islands, the U.S. Virgin Islands) in the island areas, which have cartographic boundaries but no ACS 5-year estimates because the Island Areas run a separate decennial-only program. In the other direction, three ACS district rows have no polygon and so no row here: `09ZZ`, `17ZZ` and `33ZZ`, the water-only pseudo-districts Connecticut, Illinois and New Hampshire contribute to the tabulation, each with population 0. Keeping these rows means a national map has no holes and a consumer can see the absence; dropping them would make "every US geography" quietly mean something narrower.

This is one themed chunk of six at this geography. The other themes are [Income & Poverty](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/collection.json), [Housing & Rent](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/collection.json), [Commuting & Connectivity](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/collection.json) and [Health, Disability & Income by Race](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/collection.json), split that way so a consumer who wants one theme reads one file. Chunks at the same geography hold the same rows and the same geometry, so they join 1:1 on `geoid`. A sixth collection, [All Indicators](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts/collection.json), carries all 112 columns on the same rows in one wide table — at this many features width costs little, so take that one if a question crosses themes. A district nests in a state, so `substr(geoid, 1, 2)` reaches the state row; nothing finer joins by prefix, because district boundaries follow 2020 census blocks rather than counties or tracts. Every other geography in this catalog is organized the same way — [block groups](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/catalog.json), [census tracts](https://source.coop/portolan-mirrors/us-census-catalog/tracts/catalog.json), [counties](https://source.coop/portolan-mirrors/us-census-catalog/counties/catalog.json), [states](https://source.coop/portolan-mirrors/us-census-catalog/states/catalog.json), [ZCTAs](https://source.coop/portolan-mirrors/us-census-catalog/zctas/catalog.json) and [places and CDPs](https://source.coop/portolan-mirrors/us-census-catalog/places/catalog.json) — and the [blocks](https://source.coop/portolan-mirrors/us-census-catalog/blocks/collection.json) collection carries 2020 Decennial counts, a different survey and vintage rather than a finer version of these numbers.

The PMTiles archive carries the same columns as the GeoParquet, minus the `*_moe` columns, and at every zoom the tiles are the real census geographies — there are few enough features here to draw them all at a national zoom, so this archive needs none of the coarser-geography coarse-zoom bands the catalog's finer collections carry. Built with [tylertoo](https://github.com/geoparquet-io/tylertoo). Statistics still come from the GeoParquet: margins of error are not in the tiles.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![ACS](https://img.shields.io/badge/ACS-blue) ![American Community Survey](https://img.shields.io/badge/American_Community_Survey-blue) ![demographics](https://img.shields.io/badge/demographics-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![margins of error](https://img.shields.io/badge/margins_of_error-blue) ![age](https://img.shields.io/badge/age-blue) ![race](https://img.shields.io/badge/race-blue) ![ethnicity](https://img.shields.io/badge/ethnicity-blue) ![education](https://img.shields.io/badge/education-blue) ![equity](https://img.shields.io/badge/equity-blue) ![congressional districts](https://img.shields.io/badge/congressional_districts-blue)

## Spatial Coverage

- **Bounding Box**: [-179.146711, 17.88329, -65.221081, 71.387815]

## Temporal Coverage

- **Start**: 2020-01-01T00:00:00Z
- **End**: 2024-12-31T23:59:59Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | 4-character congressional district GEOID — state FIPS (2) + district (2), e.g. `0612` for California's 12th. `substr(geoid, 1, 2)` is the state FIPS code. At-large states use district `00` (AK, DE, ND, SD, VT, WY) and the non-voting delegate districts use `98` (`1198` District of Columbia, `7298` Puerto Rico, plus the four island areas). Districts of the **119th Congress**, which is the vintage the ACS 2020–2024 5-year release tabulates: matches `GEOID` in the `cb_2024_us_cd119_500k` cartographic boundary file (`CDSESSN = '119'` on every feature) and the ACS `5001900US` prefix, whose `19` is the congress number, is stripped. District numbers are not stable across congresses, so a `geoid` here does not join to a 118th-Congress district of the same number. |
| name | string | `NAMELSAD` from the cartographic boundary congressional district file plus the state name from the state file — "Congressional District 12, California", "Delegate District (at Large), District of Columbia". |
| state | string | Two-letter USPS state or territory code (`MO`, `PR`, `GU`). Carried on every collection from the `STATEFP → USPS` lookup embedded in `tools/specs.py` rather than read off the boundary files, because the 2024 cartographic boundary block-group file has no `STUSPS` column while the tract, county and state files do. |
| population | int64 | Total population. Universe: total population. The single line of [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) (Total Population), published as an integer. Carried on every ACS collection so a rate can be weighted or sanity-checked without a second download. NULL on 0.91% of districts — the four island-area delegate districts (American Samoa, Guam, the Northern Mariana Islands, the U.S. Virgin Islands), which have 2024 boundaries but no ACS 5-year estimates. Every other column in this collection is NULL on the same four rows and nowhere else. |
| population_moe | double | Margin of error for `population` at the 90% confidence level, the level the Census Bureau publishes. Component margins add in quadrature — `sqrt(Σ moe²)` — which is the Census Bureau's formula for the margin of a sum. NULL when every component is a jam value. |
| aland_sqkm | double | Land area in square kilometres, rounded to 3 decimals. `ALAND / 1e6` from the cartographic boundary file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
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
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary congressional district file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the congressional district into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./cd-people.pmtiles | 9.7 MB | 1220790d8aed... |
| ./cd-people.parquet | 8.5 MB | 122024b76fbf... |
| ./styles/default.json | 1.8 KB | 122085fc3530... |
| ./styles/education.json | 1.8 KB | 1220d130e18b... |
| ./styles/people-of-color.json | 1.8 KB | 1220f16c687d... |
| ./styles/seniors.json | 1.7 KB | 1220a677f77d... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01001.dat | 191.1 MB | 12201637b18a... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01002.dat | 25.4 MB | 122004784637... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01003.dat | 17.5 MB | 122038d1a992... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b03002.dat | 79.4 MB | 1220ef1a9310... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b15003.dat | 88.0 MB | 1220d0c8609e... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/documentation/ACS20245YR_Table_Shells.txt | 5.4 MB | 12205b46f4af... |
| https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_cd119_500k.zip | 6.7 MB | 12202b4238ae... |
| https://www2.census.gov/geo/docs/maps-data/data/geo_tallies2020/Natl_Geographic_Tallies_2020.txt | 1.7 KB | 122006db85a1... |
| https://www.census.gov/programs-surveys/decennial-census/about/rdo/congressional-districts.119th_Congress.html | - | - |
| https://www.census.gov/programs-surveys/acs/library/handbooks/general.html | - | - |
| https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf | 378.9 KB | 12204d325820... |
| https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2024_ACSSubjectDefinitions.pdf | 1.1 MB | 12206e0c5b1a... |
| https://www.census.gov/programs-surveys/geography/about/glossary.html | - | - |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./cd-people.pmtiles")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)

## Processing Notes

This collection is a themed cut of [All Indicators — Congressional Districts (119th Congress)](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts/collection.json), the wide 112-column table at this geography: the same rows, the same geometry and the same seven context columns, with 29 columns kept and the other themes' dropped. Nothing is recomputed — every value here is the value in the wide file — so the build notes below describe the single ACS read both were made from.

Built 2026-11-12 from the ACS 2020–2024 5-year table-based Summary File (https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/), downloaded the same day over plain HTTPS — the summary file needs no API key. Tables read for this collection: B01001, B01002, B01003, B03002, B15003. Each national `.dat` file is one row per geography with estimate and margin of error side by side, and every summary level is picked off `GEO_ID` by prefix in a single pass per file — this collection's is `5001900US`, read off the files themselves rather than taken from a summary-level table (the `19` is the congress number).

Jam values (the sentinels the ACS publishes in place of unestimable values, e.g. -666666666 for an uncomputable median, and -555555555 for a controlled MOE) become NULL: any estimate or margin at or below -111111111 is dropped rather than published as a number. Counts are sums of the specified lines with margins added in quadrature; percentages use the Census Bureau's proportion formula with the ratio formula as fallback; medians are passed through untouched; coefficients of variation are `moe / 1.645 / estimate` on the headline columns. Every line number is pinned against the release's own table shells before the build starts (44 pins verified, 0 failures, plus 4 derived line groups resolved from the shells), so a vintage bump that moves a line fails loudly instead of publishing a mislabeled column.

Geometry is the 2024 cartographic boundary file (cb_2024_us_cd119_500k.zip) for congressional districts of the 119th Congress (1:500,000), reprojected to EPSG:4326 with ogr2ogr — not DuckDB's `ST_Transform`, which computes correct coordinates but stamps the source CRS into the GeoParquet metadata. Geometry drives the join, so a geography with boundaries but no ACS tabulation keeps its row with NULL values.

Cross-checked end to end against the published St. Louis census catalog, which runs the same formulas on the same vintage: 314 of 314 block groups joined, 0 mismatches on median household income, its margin of error, the poverty rate and its margin of error — exact equality, not approximate.

Validated: 441 rows against the 441 districts in the Census Bureau's own [geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html) (436 US including the District of Columbia delegate + 1 Puerto Rico + 4 island areas), 441 distinct `geoid`, no percentage outside 0–100, population 546,488–1,021,191 across the 435 voting districts. Spot-checked: CA-12 median household income $108,648, NY-12 $147,775, AL-01 $66,291.

Converted to GeoParquet with geoparquet-io (gpio): ZSTD compression, Hilbert row order, and a covering `bbox` column with row-group statistics, so a spatial filter can skip most of the file over the network. Tiled to PMTiles with tylertoo as a census-geography pyramid, so coarse zooms carry a coarser census geography — counties, then tracts — with that geography's own official values, instead of a thinned sample of this collection's features; the collections small enough to draw nationally (counties, states, congressional districts) are tiled as real polygons at every zoom.


## Attribution

U.S. Census Bureau

## License

[CC0-1.0](https://www.census.gov/about/policies/open-gov/open-data.html)

## Contact

Chris Holmes <cholmes@9eo.org>

## Known Issues

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 17 ZCTAs, 279 places and 4 delegate districts.

**These are the districts of the 119th Congress**, which is the vintage the ACS 2020–2024 5-year release tabulates: the release's `GEO_ID` prefix is `5001900US` (the `19`) and the boundary file is `cb_2024_us_cd119_500k` with `CDSESSN = '119'`. Confirmed against the Census Bureau's [ACS geography boundaries by year](https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year/2024.html), which lists "Congressional District, Delegate District DC, Resident Commissioner District PR" with the vintage "119th Congress of the United States". District numbers are not stable between congresses — several states re-drew their maps for the 119th — so a GEOID here does not refer to the same ground as the same GEOID in an earlier congress, and estimates must not be compared across congresses as a time series.

441 rows, not 435: the 435 voting districts plus the District of Columbia delegate district (`1198`), Puerto Rico's Resident Commissioner district (`7298`) and the four island-area delegate districts (`6098`, `6698`, `6998`, `7898`), which carry geometry but no ACS estimates. Every column in this collection is NULL on exactly those four rows (0.91%).

Three districts the ACS tabulates are absent, by construction: `09ZZ`, `17ZZ` and `33ZZ` — water-only pseudo-districts in Connecticut, Illinois and New Hampshire, each with population 0 — have no polygon in the cartographic boundary file and so no row here.

Districts are equal-population by design (546,488–1,021,191 across the 435 voting districts, 771,301 at the median of all 437 rows with data — Puerto Rico's single Resident Commissioner district is the outlier at 3,234,309), so the spread of every rate is much narrower than at any other geography in this catalog. Class breaks measured at county or tract level will put almost every district in one or two classes; the styles shipped with this collection are measured on its own distribution.

**A family of margins is NULL at this geography, and `population_moe` is only the visible one.** Measured: `population_moe`, `pct_under_18_moe`, `pct_65_plus_moe`, `pct_white_nh_moe`, `pct_black_moe`, `pct_native_moe`, `pct_asian_moe`, `pct_hispanic_moe` and `pct_people_of_color_moe` are carried on 423 of the 441 rows. The 18 without one are the four island-area delegate districts, which carry no ACS data at all, plus the six at-large districts, the District of Columbia delegate and Puerto Rico districts, all four of Iowa's and both of West Virginia's (measured). `sqrt(sum(moe*moe))` over a NULL-bearing column returns NULL, so check before putting one in a quadrature sum, and read these estimates as something to use rather than as an estimate to put an interval on. Every other `*_moe` column in this collection is populated on every row where its estimate is — measured, with no exceptions.

That NULL is upstream, and it is not suppression: each column in the list above comes from a total-population table (B01001, B01003, B03002), and in the release's own `.dat` files those rows carry the estimate beside `-555555555`, the **controlled-MOE** jam value a controlled estimate gets in place of a sampling margin. The build turns it into NULL rather than publishing it as a number — `0500000US01001|59947|-555555555` in `acsdt5y2024-b01003.dat`, read 2026-11-15. The same columns carry margins normally at the finer geographies, where the estimates are not controlled this way: `population_moe` is carried on 33,759 of 33,791 ZCTAs and on all 241,854 populated block groups (measured).

Margins of error are the narrowest in this catalog — a district is ~770,000 people — and every `*_cv` column at this geography has a median coefficient of variation below 0.11 (measured). They are still margins: check whether two districts' margins overlap before calling a difference real, and never aggregate a median.

The PMTiles archive is real geographies at every zoom, with no coarser-geography coarse-zoom band (the catalog's finer collections switch to counties and tracts at coarse zooms; this one has few enough features not to). `*_moe` columns are not in the tiles — statistics come from the GeoParquet.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
