# Income & Poverty — Counties

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/collection.json)** · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/counties/county-income/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

Income, poverty and employment: median household income and per capita income ([B19013](https://data.census.gov/table/ACSDT5Y2024.B19013), [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301)), the share of people below the poverty line and below twice it ([C17002](https://data.census.gov/table/ACSDT5Y2024.C17002)), the share of households receiving SNAP ([B22010](https://data.census.gov/table/ACSDT5Y2024.B22010)), and the unemployment rate as a share of the civilian labor force ([B23025](https://data.census.gov/table/ACSDT5Y2024.B23025)), plus total population ([B01003](https://data.census.gov/table/ACSDT5Y2024.B01003)) and population density for context.

Curated indicators for all **3,235** counties and county equivalents in the United States, Puerto Rico and the island areas, from the U.S. Census Bureau's [American Community Survey](https://www.census.gov/programs-surveys/acs.html) **2020–2024 5-year estimates** (`acsdt5y2024`, the table-based [Summary File](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)). The Census Bureau calls the ACS "the premier source of detailed information about the nation's people and housing". The Bureau also publishes 1-year estimates at this geography; the 5-year release is used throughout this catalog so every geography in it is the same vintage and directly comparable.

Every estimate ships with its margin of error — `<column>_moe`, at the 90% confidence level, the level the Census Bureau publishes — and the headline statistics also carry a coefficient of variation (`<column>_cv` = `moe / 1.645 / estimate`) so small-area noise can be flagged rather than mapped as if certain. Derived percentages propagate error with the Census Bureau's own formulas from [ACS Accuracy of the Data](https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf): sums add in quadrature, proportions use the subset formula with the ratio formula as fallback. ACS jam values for suppressed or unestimable cells are NULL here, never numbers, and medians are published as the Bureau publishes them — a median cannot be aggregated to a larger area. Each column's description names its ACS table, its exact universe, and the lines summed to make it.

Counties are the coarsest geography most questions are actually asked at, and the most reliable in this catalog below state level: the median coefficient of variation on `median_hh_income` is **0.042** here against 0.125 at tract level (measured). One context column breaks the catalog's own rule — `population_moe` is NULL on **3,103 of the 3,235 rows**, only 132 small rural counties carrying a margin on `population` — so read `population` here as a count to use rather than an estimate to put an interval on. `median_hh_income` is published for 3,221 of the 3,235 rows — NULL on **0.43%**, against 1.59% of tracts and 7.69% of block groups.

Geometries are the Census Bureau's [2024 cartographic boundary files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) for counties and county equivalents (GENZ2024, 1:500,000), reprojected to EPSG:4326 and joined on `GEOID`. Cartographic rather than TIGER/Line because TIGER extends census geographies into open water while the cartographic files clip to the shoreline, which is what a choropleth wants. The boundary vintage matches the estimate vintage.

The join is driven by geometry, so a geography with 2024 boundaries but no ACS tabulation keeps its row with NULL values instead of disappearing: 13 county equivalents in the island areas, which have cartographic boundaries but no ACS 5-year estimates because the Island Areas run a separate decennial-only program. Keeping these rows means a national map has no holes and a consumer can see the absence; dropping them would make "every US geography" quietly mean something narrower.

This is one themed chunk of six at this geography. The other themes are [People & Education](https://source.coop/portolan-mirrors/us-census-catalog/counties/county-people/collection.json), [Housing & Rent](https://source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/collection.json), [Commuting & Connectivity](https://source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/collection.json) and [Health, Disability & Income by Race](https://source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/collection.json), split that way so a consumer who wants one theme reads one file. Chunks at the same geography hold the same rows and the same geometry, so they join 1:1 on `geoid`. A sixth collection, [All Indicators](https://source.coop/portolan-mirrors/us-census-catalog/counties/counties/collection.json), carries all 112 columns on the same rows in one wide table — at this many features width costs little, so take that one if a question crosses themes. GEOIDs nest by prefix: `substr(geoid, 1, 2)` is the state, and tracts and block groups join back on their own first 5 characters. Every other geography in this catalog is organized the same way — [block groups](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/catalog.json), [census tracts](https://source.coop/portolan-mirrors/us-census-catalog/tracts/catalog.json), [states](https://source.coop/portolan-mirrors/us-census-catalog/states/catalog.json), [ZCTAs](https://source.coop/portolan-mirrors/us-census-catalog/zctas/catalog.json), [places and CDPs](https://source.coop/portolan-mirrors/us-census-catalog/places/catalog.json) and [congressional districts](https://source.coop/portolan-mirrors/us-census-catalog/congressional-districts/catalog.json) — and the [blocks](https://source.coop/portolan-mirrors/us-census-catalog/blocks/collection.json) collection carries 2020 Decennial counts, a different survey and vintage rather than a finer version of these numbers.

The PMTiles archive carries the same columns as the GeoParquet, minus the `*_moe` columns, and at every zoom the tiles are the real census geographies — there are few enough features here to draw them all at a national zoom, so this archive needs none of the coarser-geography coarse-zoom bands the catalog's finer collections carry. Built with [tylertoo](https://github.com/geoparquet-io/tylertoo). Statistics still come from the GeoParquet: margins of error are not in the tiles.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](https://source.coop/portolan-mirrors/us-census-catalog/counties/county-income/AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![ACS](https://img.shields.io/badge/ACS-blue) ![American Community Survey](https://img.shields.io/badge/American_Community_Survey-blue) ![demographics](https://img.shields.io/badge/demographics-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![margins of error](https://img.shields.io/badge/margins_of_error-blue) ![income](https://img.shields.io/badge/income-blue) ![poverty](https://img.shields.io/badge/poverty-blue) ![SNAP](https://img.shields.io/badge/SNAP-blue) ![unemployment](https://img.shields.io/badge/unemployment-blue) ![equity](https://img.shields.io/badge/equity-blue) ![counties](https://img.shields.io/badge/counties-blue)

## Spatial Coverage

- **Bounding Box**: [-179.146711, 17.88329, -65.221081, 71.387815]

## Temporal Coverage

- **Start**: 2020-01-01T00:00:00Z
- **End**: 2024-12-31T23:59:59Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | 5-character county (or county-equivalent) GEOID — state (2) + county (3), e.g. `29510` for St. Louis city. Includes Puerto Rico municipios and the island-area county equivalents. Matches `GEOID` in the 2024 cartographic boundary county file; the ACS `0500000US` prefix is stripped. |
| name | string | Human-readable name from the cartographic boundary county file: `NAMELSAD`, `STATE_NAME` — "St. Louis city, Missouri". |
| state | string | Two-letter USPS state or territory code (`MO`, `PR`, `GU`). Carried on every collection from the `STATEFP → USPS` lookup embedded in `tools/specs.py` rather than read off the boundary files, because the 2024 cartographic boundary block-group file has no `STUSPS` column while the tract, county and state files do. |
| population | int64 | Total population. Universe: total population. The single line of [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) (Total Population), published as an integer. Carried on every ACS collection so a rate can be weighted or sanity-checked without a second download. NULL on 0.40% of counties — the 13 island-area county equivalents (AS 5, GU 1, MP 4, VI 3), which have cartographic boundaries but no ACS 5-year estimates. |
| population_moe | double | Margin of error for `population` at the 90% confidence level, the level the Census Bureau publishes. Component margins add in quadrature — `sqrt(Σ moe²)` — which is the Census Bureau's formula for the margin of a sum. NULL when every component is a jam value. |
| aland_sqkm | double | Land area in square kilometres, rounded to 3 decimals. `ALAND / 1e6` from the cartographic boundary file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
| pop_density | double | People per square kilometre of land area, rounded to 1 decimal: `population / aland_sqkm`. NULL where `ALAND` is 0 or `population` is NULL. |
| median_hh_income | double | Median household income in the past 12 months, in 2024 inflation-adjusted dollars. Universe: households. Line 1 of [B19013](https://data.census.gov/table/ACSDT5Y2024.B19013), published as the Census Bureau publishes it. A median cannot be aggregated: there is no way to combine the medians of two block groups into the median of their union. |
| median_hh_income_moe | double | Margin of error for `median_hh_income` at the 90% confidence level, the level the Census Bureau publishes. Published as the Census Bureau publishes it for this line. A median's margin cannot be recomputed from a distribution, so it is passed through untouched. |
| median_hh_income_cv | double | Coefficient of variation for `median_hh_income`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| per_capita_income | double | Per capita income in the past 12 months, in 2024 inflation-adjusted dollars — aggregate income divided by total population, so children and people with no income are in the denominator. Universe: total population. Line 1 of [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301). |
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
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary county file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the county into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./county-income.pmtiles | 18.0 MB | 122073db7592... |
| ./county-income.parquet | 12.3 MB | 122053260d3e... |
| ./styles/default.json | 2.3 KB | 1220d58c164b... |
| ./styles/poverty.json | 2.2 KB | 1220c1de6309... |
| ./styles/snap.json | 1.7 KB | 1220fbdbba18... |
| ./styles/unemployment.json | 1.7 KB | 1220fe76a1e1... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01003.dat | 17.5 MB | 122038d1a992... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b19013.dat | 17.1 MB | 1220b25a176b... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b19301.dat | 16.3 MB | 12209fc107e9... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b22010.dat | 36.4 MB | 1220728f19fa... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b23025.dat | 38.1 MB | 1220264a5bd9... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-c17002.dat | 40.1 MB | 1220dc3dc675... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/documentation/ACS20245YR_Table_Shells.txt | 5.4 MB | 12205b46f4af... |
| https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_500k.zip | 11.1 MB | 1220da405171... |
| https://www.census.gov/programs-surveys/acs/library/handbooks/general.html | - | - |
| https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf | 378.9 KB | 12204d325820... |
| https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2024_ACSSubjectDefinitions.pdf | 1.1 MB | 12206e0c5b1a... |
| https://www.census.gov/programs-surveys/geography/about/glossary.html | - | - |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./county-income.pmtiles")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)

## Processing Notes

This collection is a themed cut of [All Indicators — Counties](https://source.coop/portolan-mirrors/us-census-catalog/counties/counties/collection.json), the wide 112-column table at this geography: the same rows, the same geometry and the same seven context columns, with 23 columns kept and the other themes' dropped. Nothing is recomputed — every value here is the value in the wide file — so the build notes below describe the single ACS read both were made from.

Built 2026-11-12 from the ACS 2020–2024 5-year table-based Summary File (https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/), downloaded the same day over plain HTTPS — the summary file needs no API key. Tables read for this collection: B01003, B19013, B19301, B22010, B23025, C17002. Each national `.dat` file is one row per geography with estimate and margin of error side by side, and every summary level is picked off `GEO_ID` by prefix in a single pass per file — this collection's is `0500000US`, read off the files themselves rather than taken from a summary-level table.

Jam values (the sentinels the ACS publishes in place of unestimable values, e.g. -666666666 for an uncomputable median, and -555555555 for a controlled MOE) become NULL: any estimate or margin at or below -111111111 is dropped rather than published as a number. Counts are sums of the specified lines with margins added in quadrature; percentages use the Census Bureau's proportion formula with the ratio formula as fallback; medians are passed through untouched; coefficients of variation are `moe / 1.645 / estimate` on the headline columns. Every line number is pinned against the release's own table shells before the build starts (44 pins verified, 0 failures, plus 4 derived line groups resolved from the shells), so a vintage bump that moves a line fails loudly instead of publishing a mislabeled column.

Geometry is the 2024 cartographic boundary file (cb_2024_us_county_500k.zip) for counties and county equivalents (1:500,000), reprojected to EPSG:4326 with ogr2ogr — not DuckDB's `ST_Transform`, which computes correct coordinates but stamps the source CRS into the GeoParquet metadata. Geometry drives the join, so a geography with boundaries but no ACS tabulation keeps its row with NULL values.

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

**`population_moe` is NULL on almost every row at this geography.** Measured: carried on 132 of the 3,235 rows. The 132 that carry one are the smallest counties in the country: every one has a population under 7,000 (measured). `sqrt(sum(moe*moe))` over a NULL-bearing column returns NULL, so check before putting one in a quadrature sum, and read this count as something to use rather than as an estimate to put an interval on. Every other `*_moe` column in this collection is populated on every row where its estimate is — measured, with no exceptions.

That NULL is upstream, and it is not suppression: the column comes from a total-population table (B01003), and in the release's own `.dat` files those rows carry the estimate beside `-555555555`, the **controlled-MOE** jam value a controlled estimate gets in place of a sampling margin. The build turns it into NULL rather than publishing it as a number — `0500000US01001|59947|-555555555` in `acsdt5y2024-b01003.dat`, read 2026-11-15. The same column carries a margin normally at the finer geographies, where the estimates are not controlled this way: `population_moe` is carried on 33,759 of 33,791 ZCTAs and on all 241,854 populated block groups (measured).

Medians are published for nearly every county; the race iterations are the exception: NULL for `median_hh_income` on 0.43% of rows (measured). These are the Census Bureau's own suppressions, reported rather than patched.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

The PMTiles archive is real geographies at every zoom, with no coarser-geography coarse-zoom band (the catalog's finer collections switch to counties and tracts at coarse zooms; this one has few enough features not to). `*_moe` columns are not in the tiles — statistics come from the GeoParquet.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
