# Health, Disability & Income by Race — Census Tracts

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/collection.json)** · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

Health coverage, disability, nativity and income by race — the tables the Census Bureau does not publish for block groups, which is why this chunk has no block-group twin. The uninsured share and the share with a disability ([B27001](https://data.census.gov/table/ACSDT5Y2024.B27001), [B18101](https://data.census.gov/table/ACSDT5Y2024.B18101)), the foreign-born share ([B05002](https://data.census.gov/table/ACSDT5Y2024.B05002)), the group-quarters population ([B26001](https://data.census.gov/table/ACSDT5Y2024.B26001)), median household income for Black, non-Hispanic White, Asian and Hispanic householders ([B19013B](https://data.census.gov/table/ACSDT5Y2024.B19013B), [B19013H](https://data.census.gov/table/ACSDT5Y2024.B19013H), [B19013D](https://data.census.gov/table/ACSDT5Y2024.B19013D), [B19013I](https://data.census.gov/table/ACSDT5Y2024.B19013I)), and the poverty rate of the Black alone population ([B17020B](https://data.census.gov/table/ACSDT5Y2024.B17020B)).

Curated indicators for all **85,184** census tracts in the United States, Puerto Rico and the island areas, from the U.S. Census Bureau's [American Community Survey](https://www.census.gov/programs-surveys/acs.html) **2020–2024 5-year estimates** (`acsdt5y2024`, the table-based [Summary File](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)). The Census Bureau calls the ACS "the premier source of detailed information about the nation's people and housing". The 5-year file is the only ACS release published at this geography: 1-year estimates stop well above it.

Every estimate ships with its margin of error — `<column>_moe`, at the 90% confidence level, the level the Census Bureau publishes — and the headline statistics also carry a coefficient of variation (`<column>_cv` = `moe / 1.645 / estimate`) so small-area noise can be flagged rather than mapped as if certain. Derived percentages propagate error with the Census Bureau's own formulas from [ACS Accuracy of the Data](https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf): sums add in quadrature, proportions use the subset formula with the ratio formula as fallback. ACS jam values for suppressed or unestimable cells are NULL here, never numbers, and medians are published as the Bureau publishes them — a median cannot be aggregated to a larger area. Each column's description names its ACS table, its exact universe, and the lines summed to make it.

The four race-iteration medians are sparse by construction: `median_hh_income_asian` is NULL for **71.27%** of tracts, `median_hh_income_black` for **61.43%**, `median_hh_income_hispanic` for **44.43%** and `median_hh_income_white_nh` for **10.04%**, wherever that group has too few households in the tract for a published median. A map of one of these columns is as much a map of where the group lives as of its income.

Geometries are the Census Bureau's [2024 cartographic boundary files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) for census tracts (GENZ2024, 1:500,000), reprojected to EPSG:4326 and joined on `GEOID`. Cartographic rather than TIGER/Line because TIGER extends census geographies into open water while the cartographic files clip to the shoreline, which is what a choropleth wants. The boundary vintage matches the estimate vintage.

The join is driven by geometry, so a geography with 2024 boundaries but no ACS tabulation keeps its row with NULL values instead of disappearing: 126 tracts in the island areas, which have cartographic boundaries but no ACS 5-year estimates because the Island Areas run a separate decennial-only program. Suffolk County, New York was re-delineated in the 2024 vintage, which adds 14 tracts with boundaries and no matching ACS row. Keeping these rows means a national map has no holes and a consumer can see the absence; dropping them would make "every US geography" quietly mean something narrower.

This is one themed chunk of 5 at this geography — the others are [Income & Poverty](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/collection.json), [People & Education](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/collection.json), [Housing & Rent](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/collection.json) and [Commuting & Connectivity](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/collection.json) — split that way because a single wide national table would make a consumer who wanted one column download all of them. Collections at the same geography join 1:1 on `geoid`. The same indicators are published for [counties](https://source.coop/portolan-mirrors/us-census-catalog/counties/collection.json) and [states](https://source.coop/portolan-mirrors/us-census-catalog/states/collection.json) as single wide tables.

The PMTiles archive is a census-geography pyramid built with [tylertoo](https://github.com/geoparquet-io/tylertoo): z0–z5 are county polygons carrying the Census Bureau's own published county estimates, and z6–z12 are the census tracts themselves. Thinning this many polygons down to a national zoom would show a biased subset (small urban geographies drop first) rather than less data, so the coarse zooms step up to a coarser census geography instead of a thinned sample of this one. Every band carries the same column names, so one style expression classifies every zoom — but below z6 you are looking at counties, not tracts, and the values there are the Bureau's official estimates for those geographies, with their own meaning, rather than a visualization-only average: clicking a coarse feature identifies a real county by `geoid` and `name`. The `*_moe` columns are excluded from the tiles at every zoom — a margin of error is computed for one specific geography and cannot be carried across bands — while the `*_cv` columns are kept. Statistics come from the GeoParquet, never from the tiles.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![ACS](https://img.shields.io/badge/ACS-blue) ![American Community Survey](https://img.shields.io/badge/American_Community_Survey-blue) ![demographics](https://img.shields.io/badge/demographics-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![margins of error](https://img.shields.io/badge/margins_of_error-blue) ![health insurance](https://img.shields.io/badge/health_insurance-blue) ![disability](https://img.shields.io/badge/disability-blue) ![foreign-born](https://img.shields.io/badge/foreign--born-blue) ![income by race](https://img.shields.io/badge/income_by_race-blue) ![group quarters](https://img.shields.io/badge/group_quarters-blue) ![equity](https://img.shields.io/badge/equity-blue)

## Spatial Coverage

- **Bounding Box**: [-179.146711, 17.88329, -65.221081, 71.387815]

## Temporal Coverage

- **Start**: 2020-01-01T00:00:00Z
- **End**: 2024-12-31T23:59:59Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | 11-character census tract GEOID — state (2) + county (3) + tract (6), e.g. `29510102200`. Joins the block-group collections on `substr(geoid, 1, 11)` and the block collection on `substr(geoid, 1, 11)`. Matches `GEOID` in the 2024 cartographic boundary tract file; the ACS `1400000US` prefix is stripped. |
| name | string | Human-readable name from the cartographic boundary tract file: `NAMELSAD`, `NAMELSADCO`, `STATE_NAME` — "Census Tract 34.06, San Joaquin County, California". |
| state | string | Two-letter USPS state or territory code (`MO`, `PR`, `GU`). Carried on every collection from the `STATEFP → USPS` lookup embedded in `tools/specs.py` rather than read off the boundary files, because the 2024 cartographic boundary block-group file has no `STUSPS` column while the tract, county and state files do. |
| population | int64 | Total population. Universe: total population. The single line of [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) (Total Population), published as an integer. Carried on every ACS collection so a rate can be weighted or sanity-checked without a second download. NULL on 0.16% of tracts: 126 island-area tracts plus 14 in Suffolk County, NY. |
| population_moe | double | Margin of error for `population` at the 90% confidence level, the level the Census Bureau publishes. Component margins add in quadrature — `sqrt(Σ moe²)` — which is the Census Bureau's formula for the margin of a sum. NULL when every component is a jam value. |
| aland_sqkm | double | Land area in square kilometres, rounded to 3 decimals. `ALAND / 1e6` from the cartographic boundary file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
| pop_density | double | People per square kilometre of land area, rounded to 1 decimal: `population / aland_sqkm`. NULL where `ALAND` is 0 or `population` is NULL. |
| pct_uninsured | double | Percent of the civilian noninstitutionalized population with no health insurance coverage. Universe: civilian noninstitutionalized population — people on active duty and people in institutions are outside it. The "No health insurance coverage" lines of [B27001](https://data.census.gov/table/ACSDT5Y2024.B27001) over line 1, resolved from the table shells by label (9 age groups × 2 sexes = 18 lines for this vintage) rather than hardcoded. Not published for block groups, which is why there is no block-group twin of this collection. NULL on 0.94% of tracts. Not published for block groups at all. |
| pct_uninsured_moe | double | Margin of error for `pct_uninsured` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_uninsured_cv | double | Coefficient of variation for `pct_uninsured`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_with_disability | double | Percent of the civilian noninstitutionalized population with a disability, as the ACS's six-question sequence defines it (hearing, vision, cognitive, ambulatory, self-care, independent living). Universe: civilian noninstitutionalized population. The "With a disability" lines of [B18101](https://data.census.gov/table/ACSDT5Y2024.B18101) over line 1, resolved from the shells by label (6 age groups × 2 sexes = 12 lines for this vintage). NULL on 0.94% of tracts. Not published for block groups at all. |
| pct_with_disability_moe | double | Margin of error for `pct_with_disability` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_with_disability_cv | double | Coefficient of variation for `pct_with_disability`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_foreign_born | double | Percent of the population that is foreign-born — anyone not a U.S. citizen at birth, naturalized citizens included. Universe: total population. Line 13 ("Foreign-born") over line 1 of [B05002](https://data.census.gov/table/ACSDT5Y2024.B05002) (Place of Birth by Nativity and Citizenship Status). People born abroad to American parents (line 12) are native-born and are not in this share. |
| pct_foreign_born_moe | double | Margin of error for `pct_foreign_born` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| group_quarters_pop | int64 | Population living in group quarters — correctional facilities, nursing facilities, college and university housing, military quarters, group homes, shelters. Universe: population in group quarters. Line 1 of [B26001](https://data.census.gov/table/ACSDT5Y2024.B26001), published as an integer. A large value next to a small household population usually explains an odd median: a prison or a dorm dominates the geography. NULL on 0.16% of tracts — the island-area and re-delineated geographies, not suppression. |
| group_quarters_pop_moe | double | Margin of error for `group_quarters_pop` at the 90% confidence level, the level the Census Bureau publishes. Component margins add in quadrature — `sqrt(Σ moe²)` — which is the Census Bureau's formula for the margin of a sum. NULL when every component is a jam value. |
| median_hh_income_black | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is Black or African American alone. Universe: households with a householder who is Black or African American alone. Line 1 of [B19013B](https://data.census.gov/table/ACSDT5Y2024.B19013B), the B race iteration of [B19013](https://data.census.gov/table/ACSDT5Y2024.B19013). Classified by the householder's race, not by every member's. **NULL on 61.43% of tracts** (39.47% of counties): wherever too few Black-householder households live in the tract for the Census Bureau to publish a median. A map of this column is as much a map of where the group lives as of its income — read the NULLs as "not published here", never as a value. |
| median_hh_income_black_moe | double | Margin of error for `median_hh_income_black` at the 90% confidence level, the level the Census Bureau publishes. Published as the Census Bureau publishes it for this line. A median's margin cannot be recomputed from a distribution, so it is passed through untouched. |
| median_hh_income_black_cv | double | Coefficient of variation for `median_hh_income_black`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| median_hh_income_white_nh | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is White alone, not Hispanic or Latino. Universe: households with a householder who is White alone, not Hispanic or Latino. Line 1 of [B19013H](https://data.census.gov/table/ACSDT5Y2024.B19013H) (the H iteration). NULL on 10.04% of tracts (2.38% of counties) — the least sparse of the four race-iteration medians, which is itself a fact about the distribution of the population. |
| median_hh_income_white_nh_moe | double | Margin of error for `median_hh_income_white_nh` at the 90% confidence level, the level the Census Bureau publishes. Published as the Census Bureau publishes it for this line. A median's margin cannot be recomputed from a distribution, so it is passed through untouched. |
| median_hh_income_white_nh_cv | double | Coefficient of variation for `median_hh_income_white_nh`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| median_hh_income_asian | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is Asian alone. Universe: households with a householder who is Asian alone. Line 1 of [B19013D](https://data.census.gov/table/ACSDT5Y2024.B19013D) (the D iteration). **NULL on 71.27% of tracts** (53.63% of counties) — the sparsest column in the catalog. Present only where the Asian-householder sample supports a median. |
| median_hh_income_asian_moe | double | Margin of error for `median_hh_income_asian` at the 90% confidence level, the level the Census Bureau publishes. Published as the Census Bureau publishes it for this line. A median's margin cannot be recomputed from a distribution, so it is passed through untouched. |
| median_hh_income_asian_cv | double | Coefficient of variation for `median_hh_income_asian`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| median_hh_income_hispanic | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is Hispanic or Latino, of any race. Universe: households with a householder who is Hispanic or Latino. Line 1 of [B19013I](https://data.census.gov/table/ACSDT5Y2024.B19013I) (the I iteration). **NULL on 44.43% of tracts** (19.60% of counties). |
| median_hh_income_hispanic_moe | double | Margin of error for `median_hh_income_hispanic` at the 90% confidence level, the level the Census Bureau publishes. Published as the Census Bureau publishes it for this line. A median's margin cannot be recomputed from a distribution, so it is passed through untouched. |
| median_hh_income_hispanic_cv | double | Coefficient of variation for `median_hh_income_hispanic`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| pct_below_poverty_black | double | Percent of the Black or African American alone population below the poverty level. Universe: Black or African American alone population for whom poverty status is determined — a race-specific universe, so this is not comparable to `pct_below_poverty`'s denominator. Line 2 ("Income in the past 12 months below poverty level") over line 1 of [B17020B](https://data.census.gov/table/ACSDT5Y2024.B17020B). NULL on 12.84% of tracts (measured): no Black-alone population for whom poverty status is determined, so no rate. |
| pct_below_poverty_black_moe | double | Margin of error for `pct_below_poverty_black` at the 90% confidence level, the level the Census Bureau publishes. Propagated with the Census Bureau's proportion formula, `sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio formula (`+` instead of `−`) when the radicand goes negative because the numerator is not a true subset of the denominator. Multiplied by 100 to match the percentage, rounded to 2 decimals, and NULL rather than guessed when an input margin is NULL or the denominator is 0. |
| pct_below_poverty_black_cv | double | Coefficient of variation for `pct_below_poverty_black`: `moe / 1.645 / estimate`, rounded to 3 decimals — the standard error as a fraction of the estimate, with 1.645 converting the published 90% margin back to a standard error. A rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of error is NULL. Published on the headline statistics so a map can grey out the geographies whose value is swamped by its own error instead of drawing them as if certain. |
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary census tract file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the census tract into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./tract-wellbeing.parquet | 53.8 MB | 12202609fdb6... |
| ./tract-wellbeing.pmtiles | 240.3 MB | 1220b553e017... |
| ./thumbnail.png | 88.5 KB | 1220f0a28b11... |
| ./styles/default.json | 2.0 KB | 1220461aa46d... |
| ./styles/disability.json | 2.2 KB | 1220dc5c78fe... |
| ./styles/foreign-born.json | 1.7 KB | 1220ff6d0013... |
| ./styles/income-black-households.json | 2.7 KB | 1220a7fd2d56... |
| ./styles/income-white-households.json | 2.7 KB | 1220f3488463... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b01003.dat | 17.5 MB | 122038d1a992... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b05002.dat | 55.1 MB | 12207c97161f... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b17020b.dat | 33.1 MB | 1220cc2cc99c... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b18101.dat | 82.3 MB | 1220efd8f494... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b19013b.dat | 10.6 MB | 12200d0ad5b3... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b19013d.dat | 10.9 MB | 12207f9af083... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b19013h.dat | 9.1 MB | 1220827fd88b... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b19013i.dat | 10.2 MB | 12204e171f70... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b26001.dat | 7.0 MB | 12207c2991c9... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b27001.dat | 114.0 MB | 1220af9b1cad... |
| https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/documentation/ACS20245YR_Table_Shells.txt | 5.4 MB | 12205b46f4af... |
| https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_tract_500k.zip | 55.2 MB | 1220abdf8bda... |
| https://www.census.gov/programs-surveys/acs/library/handbooks/general.html | - | - |
| https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/MultiyearACSAccuracyofData2024.pdf | 378.9 KB | 12204d325820... |
| https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2024_ACSSubjectDefinitions.pdf | 1.1 MB | 12206e0c5b1a... |
| https://www.census.gov/programs-surveys/geography/about/glossary.html | - | - |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./tract-wellbeing.parquet")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/)

## Processing Notes

Built 2026-11-12 from the ACS 2020–2024 5-year table-based Summary File (https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/), downloaded the same day over plain HTTPS — the summary file needs no API key. Tables read for this collection: B01003, B05002, B17020B, B18101, B19013B, B19013D, B19013H, B19013I, B26001, B27001. Each national `.dat` file is one row per geography with estimate and margin of error side by side, and every summary level is picked off `GEO_ID` by prefix in a single pass per file — this collection's is `1400000US`, read off the files themselves rather than taken from a summary-level table.

Jam values (the sentinels the ACS publishes in place of unestimable values, e.g. -666666666 for an uncomputable median, and -555555555 for a controlled MOE) become NULL: any estimate or margin at or below -111111111 is dropped rather than published as a number. Counts are sums of the specified lines with margins added in quadrature; percentages use the Census Bureau's proportion formula with the ratio formula as fallback; medians are passed through untouched; coefficients of variation are `moe / 1.645 / estimate` on the headline columns. Every line number is pinned against the release's own table shells before the build starts (44 pins verified, 0 failures, plus 4 derived line groups resolved from the shells), so a vintage bump that moves a line fails loudly instead of publishing a mislabeled column.

Geometry is the 2024 cartographic boundary file (cb_2024_us_tract_500k.zip) for census tracts (1:500,000), reprojected to EPSG:4326 with ogr2ogr — not DuckDB's `ST_Transform`, which computes correct coordinates but stamps the source CRS into the GeoParquet metadata. Geometry drives the join, so a geography with boundaries but no ACS tabulation keeps its row with NULL values.

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

The race-iteration medians are NULL wherever that group has too few households in the tract for a published median: `median_hh_income_asian` 71.27% of tracts, `median_hh_income_black` 61.43%, `median_hh_income_hispanic` 44.43%, `median_hh_income_white_nh` 10.04%. A map of one of these columns is partly a map of where the group lives.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: below z6 you are looking at counties, not tracts. The values there are the Census Bureau's own estimates for those geographies, not an aggregation of this file, and `*_moe` columns are not in the tiles. Statistics come from the GeoParquet.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
