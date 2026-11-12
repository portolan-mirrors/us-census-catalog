# People & Education — Block Groups

Who lives here: median age and the shares under 18 and 65 or over ([B01002](https://data.census.gov/table/ACSDT5Y2024.B01002), [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001)), the five mutually exclusive non-Hispanic race shares plus Hispanic or Latino of any race and their complement, people of color ([B03002](https://data.census.gov/table/ACSDT5Y2024.B03002)), and the share of adults 25 and over holding a bachelor's degree or higher ([B15003](https://data.census.gov/table/ACSDT5Y2024.B15003)).

Curated indicators for all **242,298** census block groups in the United States, Puerto Rico and the island areas, from the U.S. Census Bureau's [American Community Survey](https://www.census.gov/programs-surveys/acs.html) **2020–2024 5-year estimates** (`acsdt5y2024`, the table-based [Summary File](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)). The Census Bureau calls the ACS "the premier source of detailed information about the nation's people and housing". The 5-year file is the only ACS release published at this geography: 1-year estimates stop well above it.

Every estimate ships with its margin of error — `<column>_moe`, at the 90% confidence level, the level the Census Bureau publishes — and the headline statistics also carry a coefficient of variation (`<column>_cv` = `moe / 1.645 / estimate`) so small-area noise can be flagged rather than mapped as if certain. Derived percentages propagate error with the Census Bureau's own formulas from [ACS Accuracy of the Data](https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf): sums add in quadrature, proportions use the subset formula with the ratio formula as fallback. ACS jam values for suppressed or unestimable cells are NULL here, never numbers, and medians are published as the Bureau publishes them — a median cannot be aggregated to a larger area. Each column's description names its ACS table, its exact universe, and the lines summed to make it.

Geometries are the Census Bureau's [2024 cartographic boundary files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) for census block groups (GENZ2024, 1:500,000), reprojected to EPSG:4326 and joined on `GEOID`. Cartographic rather than TIGER/Line because TIGER extends census geographies into open water while the cartographic files clip to the shoreline, which is what a choropleth wants. The boundary vintage matches the estimate vintage.

The join is driven by geometry, so a geography with 2024 boundaries but no ACS tabulation keeps its row with NULL values instead of disappearing: 405 block groups in the island areas, which have cartographic boundaries but no ACS 5-year estimates because the Island Areas run a separate decennial-only program. Suffolk County, New York was re-delineated in the 2024 vintage, which adds 39 block groups with boundaries and no matching ACS row. Keeping these rows means a national map has no holes and a consumer can see the absence; dropping them would make "every US geography" quietly mean something narrower.

This is one themed chunk of 4 at this geography — the others are [Income & Poverty](../bg-income/collection.json), [Housing & Rent](../bg-housing/collection.json) and [Commuting & Connectivity](../bg-connectivity/collection.json) — split that way because a single wide national table would make a consumer who wanted one column download all of them. Collections at the same geography join 1:1 on `geoid`. The same indicators are published for [counties](../../counties/collection.json) and [states](../../states/collection.json) as single wide tables.

The PMTiles archive carries the same columns as the GeoParquet. At feature zooms the tiles are the census geographies; at coarse zooms they are [A5](https://a5geo.org/) cell aggregations built by [tylertoo](https://github.com/geoparquet-io/tylertoo) — counts summed, rates and medians averaged unweighted over the geographies in the cell — because thinning hundreds of thousands of polygons at a national zoom would show a biased subset (small urban geographies drop first) rather than less data. Cell and feature zooms share column names, so one style expression classifies both. The aggregation is a visualization aid: statistics come from the GeoParquet, never from the tiles.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![ACS](https://img.shields.io/badge/ACS-blue) ![American Community Survey](https://img.shields.io/badge/American_Community_Survey-blue) ![demographics](https://img.shields.io/badge/demographics-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![margins of error](https://img.shields.io/badge/margins_of_error-blue) ![age](https://img.shields.io/badge/age-blue) ![race](https://img.shields.io/badge/race-blue) ![ethnicity](https://img.shields.io/badge/ethnicity-blue) ![education](https://img.shields.io/badge/education-blue) ![equity](https://img.shields.io/badge/equity-blue) ![block groups](https://img.shields.io/badge/block_groups-blue)

## Spatial Coverage

- **Bounding Box**: [-179.146711, -14.548699, 179.77847011250077, 71.387815]

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
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary block group file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the block group into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./thumbnail.png | 70.0 KB | 12200b960c87... |
| ./bg-people.pmtiles | 592.5 MB | 1220400022f7... |
| ./bg-people.parquet | 89.9 MB | 12209e7a7960... |
| ./styles/default.json | 1.9 KB | 12205519b770... |
| ./styles/education.json | 1.8 KB | 12202fc8b39f... |
| ./styles/people-of-color.json | 1.8 KB | 1220190132c1... |
| ./styles/seniors.json | 1.7 KB | 1220a009884f... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01001.dat | 191.1 MB | 12201637b18a... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01002.dat | 25.4 MB | 122004784637... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01003.dat | 17.5 MB | 122038d1a992... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b03002.dat | 79.4 MB | 1220ef1a9310... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b15003.dat | 88.0 MB | 1220d0c8609e... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/documentation/ACS20245YR_Table_Shells.txt | 5.4 MB | 12205b46f4af... |
| https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_bg_500k.zip | 92.6 MB | 12207c4da3ed... |
| https://www.census.gov/programs-surveys/acs/library/handbooks/general.html | 349.4 KB | 122063f2cc20... |
| https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf | 378.9 KB | 12204d325820... |
| https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2024_ACSSubjectDefinitions.pdf | 1.1 MB | 12206e0c5b1a... |
| https://www.census.gov/programs-surveys/geography/about/glossary.html | 471.2 KB | 122018028aab... |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./thumbnail.png")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)

## Processing Notes

Built 2026-11-12 from the ACS 2020–2024 5-year table-based Summary File (https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/), downloaded the same day over plain HTTPS — the summary file needs no API key. Tables read for this collection: B01001, B01002, B01003, B03002, B15003. Each national `.dat` file is one row per geography with estimate and margin of error side by side, and every summary level is picked off `GEO_ID` by prefix in a single pass per file — this collection's is `1500000US`, read off the files themselves rather than taken from a summary-level table.

Jam values (the sentinels the ACS publishes in place of unestimable values, e.g. -666666666 for an uncomputable median, and -555555555 for a controlled MOE) become NULL: any estimate or margin at or below -111111111 is dropped rather than published as a number. Counts are sums of the specified lines with margins added in quadrature; percentages use the Census Bureau's proportion formula with the ratio formula as fallback; medians are passed through untouched; coefficients of variation are `moe / 1.645 / estimate` on the headline columns. Every line number is pinned against the release's own table shells before the build starts (44 pins verified, 0 failures, plus 4 derived line groups resolved from the shells), so a vintage bump that moves a line fails loudly instead of publishing a mislabeled column.

Geometry is the 2024 cartographic boundary file (cb_2024_us_bg_500k.zip) for census block groups (1:500,000), reprojected to EPSG:4326 with ogr2ogr — not DuckDB's `ST_Transform`, which computes correct coordinates but stamps the source CRS into the GeoParquet metadata. Geometry drives the join, so a geography with boundaries but no ACS tabulation keeps its row with NULL values.

Cross-checked end to end against the published St. Louis census catalog, which runs the same formulas on the same vintage: 314 of 314 block groups joined, 0 mismatches on median household income, its margin of error, the poverty rate and its margin of error — exact equality, not approximate.



Converted to GeoParquet with geoparquet-io (gpio): ZSTD compression, Hilbert row order, and a covering `bbox` column with row-group statistics, so a spatial filter can skip most of the file over the network. Tiled to PMTiles with tylertoo, with A5 cell aggregation at coarse zooms (counts summed, rates averaged) — a visualization aid, not a statistical product.


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

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are A5 cell aggregations, not census geographies — counts summed, rates and medians averaged unweighted. Statistics come from the GeoParquet.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
