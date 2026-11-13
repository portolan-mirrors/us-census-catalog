# Income & Poverty — Block Groups

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/collection.json)** · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

Income, poverty and employment: median household income and per capita income ([B19013](https://data.census.gov/table/ACSDT5Y2024.B19013), [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301)), the share of people below the poverty line and below twice it ([C17002](https://data.census.gov/table/ACSDT5Y2024.C17002)), the share of households receiving SNAP ([B22010](https://data.census.gov/table/ACSDT5Y2024.B22010)), and the unemployment rate as a share of the civilian labor force ([B23025](https://data.census.gov/table/ACSDT5Y2024.B23025)), plus total population ([B01003](https://data.census.gov/table/ACSDT5Y2024.B01003)) and population density for context.

Curated indicators for all **242,298** census block groups in the United States, Puerto Rico and the island areas, from the U.S. Census Bureau's [American Community Survey](https://www.census.gov/programs-surveys/acs.html) **2020–2024 5-year estimates** (`acsdt5y2024`, the table-based [Summary File](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)). The Census Bureau calls the ACS "the premier source of detailed information about the nation's people and housing". The 5-year file is the only ACS release published at this geography: 1-year estimates stop well above it.

Every estimate ships with its margin of error — `<column>_moe`, at the 90% confidence level, the level the Census Bureau publishes — and the headline statistics also carry a coefficient of variation (`<column>_cv` = `moe / 1.645 / estimate`) so small-area noise can be flagged rather than mapped as if certain. Derived percentages propagate error with the Census Bureau's own formulas from [ACS Accuracy of the Data](https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf): sums add in quadrature, proportions use the subset formula with the ratio formula as fallback. ACS jam values for suppressed or unestimable cells are NULL here, never numbers, and medians are published as the Bureau publishes them — a median cannot be aggregated to a larger area. Each column's description names its ACS table, its exact universe, and the lines summed to make it.

`median_hh_income` is NULL for **7.69%** of block groups — the Census Bureau suppresses a median when the sample behind it is too thin, which at this scale is often. The tract rate is 1.59%.

Geometries are the Census Bureau's [2024 cartographic boundary files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) for census block groups (GENZ2024, 1:500,000), reprojected to EPSG:4326 and joined on `GEOID`. Cartographic rather than TIGER/Line because TIGER extends census geographies into open water while the cartographic files clip to the shoreline, which is what a choropleth wants. The boundary vintage matches the estimate vintage.

The join is driven by geometry, so a geography with 2024 boundaries but no ACS tabulation keeps its row with NULL values instead of disappearing: 405 block groups in the island areas, which have cartographic boundaries but no ACS 5-year estimates because the Island Areas run a separate decennial-only program. Suffolk County, New York was re-delineated in the 2024 vintage, which adds 39 block groups with boundaries and no matching ACS row. Keeping these rows means a national map has no holes and a consumer can see the absence; dropping them would make "every US geography" quietly mean something narrower.

This is one themed chunk of 4 at this geography — the others are [People & Education](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/collection.json), [Housing & Rent](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/collection.json) and [Commuting & Connectivity](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/collection.json) — split that way because a single wide national table would make a consumer who wanted one column download all of them. Collections at the same geography join 1:1 on `geoid`. The same indicators are published for [counties](https://source.coop/portolan-mirrors/us-census-catalog/counties/collection.json) and [states](https://source.coop/portolan-mirrors/us-census-catalog/states/collection.json) as single wide tables.

The PMTiles archive carries the same columns as the GeoParquet. At feature zooms the tiles are the census geographies; at coarse zooms they are [A5](https://a5geo.org/) cell aggregations built by [tylertoo](https://github.com/geoparquet-io/tylertoo) — counts summed, rates and medians averaged unweighted over the geographies in the cell — because thinning hundreds of thousands of polygons at a national zoom would show a biased subset (small urban geographies drop first) rather than less data. Cell and feature zooms share column names, so one style expression classifies both. The aggregation is a visualization aid: statistics come from the GeoParquet, never from the tiles.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![ACS](https://img.shields.io/badge/ACS-blue) ![American Community Survey](https://img.shields.io/badge/American_Community_Survey-blue) ![demographics](https://img.shields.io/badge/demographics-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![margins of error](https://img.shields.io/badge/margins_of_error-blue) ![income](https://img.shields.io/badge/income-blue) ![poverty](https://img.shields.io/badge/poverty-blue) ![SNAP](https://img.shields.io/badge/SNAP-blue) ![unemployment](https://img.shields.io/badge/unemployment-blue) ![equity](https://img.shields.io/badge/equity-blue) ![block groups](https://img.shields.io/badge/block_groups-blue)

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
| median_hh_income | double | Median household income in the past 12 months, in 2024 inflation-adjusted dollars. Universe: households. Line 1 of [B19013](https://data.census.gov/table/ACSDT5Y2024.B19013), published as the Census Bureau publishes it. A median cannot be aggregated: there is no way to combine the medians of two block groups into the median of their union. **NULL on 7.69% of block groups.** The Census Bureau suppresses (jams) a median when the sample behind it is too thin, which at block-group scale is often; the comparable tract rate is 1.59%. Where it is present the margin can still be wide — check `median_hh_income_cv`. |
| median_hh_income_moe | double | Margin of error for `median_hh_income` at the 90% confidence level, the level the Census Bureau publishes. Published as the Census Bureau publishes it for this line. A median's margin cannot be recomputed from a distribution, so it is passed through untouched. |
| median_hh_income_cv | double | Coefficient of variation for `median_hh_income`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| per_capita_income | double | Per capita income in the past 12 months, in 2024 inflation-adjusted dollars — aggregate income divided by total population, so children and people with no income are in the denominator. Universe: total population. Line 1 of [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301). NULL on 0.99% of block groups. Part of that is an upstream coverage gap rather than suppression: [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301) publishes 242,069 block-group rows against 242,297 for [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003), and the missing 228 come through as NULL. |
| per_capita_income_moe | double | Margin of error for `per_capita_income` at the 90% confidence level, the level the Census Bureau publishes. Published as the Census Bureau publishes it for this line. A median's margin cannot be recomputed from a distribution, so it is passed through untouched. |
| pct_below_poverty | double | Percent of the population below the federal poverty level — an income-to-poverty ratio under 1.00. Universe: population for whom poverty status is determined, which excludes institutionalized people, people in military group quarters and in college dormitories, and unrelated individuals under 15. Lines 2 ("Under .50") + 3 (".50 to .99") of [C17002](https://data.census.gov/table/ACSDT5Y2024.C17002) over line 1. |
| pct_below_poverty_moe | double | Margin of error for `pct_below_poverty` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_below_poverty_cv | double | Coefficient of variation for `pct_below_poverty`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_below_2x_poverty | double | Percent of the population with an income-to-poverty ratio under 2.00 — a common proxy for low income rather than deep poverty. Universe: population for whom poverty status is determined. Lines 2–7 of [C17002](https://data.census.gov/table/ACSDT5Y2024.C17002) over line 1 (equivalently, everyone not in line 8, "2.00 and over"). |
| pct_below_2x_poverty_moe | double | Margin of error for `pct_below_2x_poverty` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_snap | double | Percent of households that received Food Stamps/SNAP benefits at any time in the past 12 months. Universe: households. Line 2 of [B22010](https://data.census.gov/table/ACSDT5Y2024.B22010) over line 1. Receipt by the household, not by individuals, and not a measure of current enrollment. |
| pct_snap_moe | double | Margin of error for `pct_snap` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_unemployed | double | Unemployment rate: unemployed people as a percent of the civilian labor force. Universe for the table is the population 16 years and over, but the denominator here is line 3, "Civilian labor force" — the labor force, not the whole population 16+, because that is what an unemployment rate divides by. Line 5 ("Unemployed") over line 3 of [B23025](https://data.census.gov/table/ACSDT5Y2024.B23025). Members of the Armed Forces and people not in the labor force are excluded from both parts. |
| pct_unemployed_moe | double | Margin of error for `pct_unemployed` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary block group file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the block group into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./thumbnail.png | 68.6 KB | 1220cd4ef018... |
| ./bg-income.pmtiles | 582.5 MB | 1220e7f5fe3f... |
| ./bg-income.parquet | 89.2 MB | 12209693f4da... |
| ./styles/default.json | 2.6 KB | 1220a4e438c5... |
| ./styles/poverty.json | 2.0 KB | 1220b02e8835... |
| ./styles/snap.json | 1.7 KB | 12201f94c228... |
| ./styles/unemployment.json | 1.7 KB | 1220febbfae1... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01003.dat | 17.5 MB | 122038d1a992... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b19013.dat | 17.1 MB | 1220b25a176b... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b19301.dat | 16.3 MB | 12209fc107e9... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b22010.dat | 36.4 MB | 1220728f19fa... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b23025.dat | 38.1 MB | 1220264a5bd9... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-c17002.dat | 40.1 MB | 1220dc3dc675... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/documentation/ACS20245YR_Table_Shells.txt | 5.4 MB | 12205b46f4af... |
| https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_bg_500k.zip | 92.6 MB | 12207c4da3ed... |
| https://www.census.gov/programs-surveys/acs/library/handbooks/general.html | - | - |
| https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf | 378.9 KB | 12204d325820... |
| https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2024_ACSSubjectDefinitions.pdf | 1.1 MB | 12206e0c5b1a... |
| https://www.census.gov/programs-surveys/geography/about/glossary.html | - | - |

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

Built 2026-11-12 from the ACS 2020–2024 5-year table-based Summary File (https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/), downloaded the same day over plain HTTPS — the summary file needs no API key. Tables read for this collection: B01003, B19013, B19301, B22010, B23025, C17002. Each national `.dat` file is one row per geography with estimate and margin of error side by side, and every summary level is picked off `GEO_ID` by prefix in a single pass per file — this collection's is `1500000US`, read off the files themselves rather than taken from a summary-level table.

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

Block-group medians are sparse where the sample is thin: NULL for `median_hh_income` on 7.69% of rows. These are the Census Bureau's own suppressions, reported rather than patched.

`per_capita_income` is incomplete upstream: B19301 publishes 242,069 block-group rows against 242,297 for B01003, and the missing 228 come through as NULL.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are A5 cell aggregations, not census geographies — counts summed, rates and medians averaged unweighted. Statistics come from the GeoParquet.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
