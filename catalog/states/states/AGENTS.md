# Agent guide — All Indicators (States)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Every indicator in this catalog's ACS column set, in one table: income and poverty, age and race and education, housing cost and tenure, vehicles and commuting and internet access, health insurance and disability and nativity, and median household income by race and ethnicity. At this many features width costs little, so the whole 112-column table is published here as well as a theme at a time in the five themed chunks beside it — a cross-theme question needs no join.

**56 rows** — the 50 states, the District of Columbia, Puerto Rico and the four
island areas — ACS 2020–2024 5-year estimates, geometry from the 2024
cartographic boundary files. **52 of the 56 carry ACS data.**

## The full-table sixth sibling

This collection is one of **six** in the [`states/`](../AGENTS.md) group, and
the only one that is not a theme:

| collection | columns | what it holds |
|---|---|---|
| [state-income](../state-income/collection.json) ([guide](../state-income/AGENTS.md)) | 23 | Income & Poverty |
| [state-people](../state-people/collection.json) ([guide](../state-people/AGENTS.md)) | 29 | People & Education |
| [state-housing](../state-housing/collection.json) ([guide](../state-housing/AGENTS.md)) | 32 | Housing & Rent |
| [state-connectivity](../state-connectivity/collection.json) ([guide](../state-connectivity/AGENTS.md)) | 30 | Commuting & Connectivity |
| [state-wellbeing](../state-wellbeing/collection.json) ([guide](../state-wellbeing/AGENTS.md)) | 34 | Health, Disability & Income by Race |
| **`states`** (this one) | **112** | all of the above in one row per state |

All six hold the same 56 `geoid` values and the same geometry, so they join 1:1
on `geoid` (measured in [`states/AGENTS.md`](../AGENTS.md)) — but at this
geography a join is rarely worth it. The 112 columns are all here, and the
file is barely larger than a themed chunk: `geometry` is 3.86 MB of a themed
file's 3.88 MB (measured from the Parquet column metadata) and this table is
only about 49 KB more. **Use this collection for anything cross-theme**, and
reach for a themed chunk when a narrower schema is the point — one style, one
set of tiles, one set of column descriptions for a single subject.

Note the layout: the five themed children keep their data beside their
metadata, while this collection's `*.parquet` and `*.pmtiles` sit one directory
**up**, beside the group's `catalog.json`. The URLs below are unchanged from
before the group was split.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.pmtiles`, layer `states`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/states/states/collection.json` — carries a full description for every column

## Source tables

| table | title | universe |
|---|---|---|
| [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001) | Sex by Age | Total population |
| [B01002](https://data.census.gov/table/ACSDT5Y2024.B01002) | Median Age by Sex | Total population |
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) | Hispanic or Latino Origin by Race | Total population |
| [B05002](https://data.census.gov/table/ACSDT5Y2024.B05002) | Place of Birth by Nativity and Citizenship Status | Total population |
| [B08301](https://data.census.gov/table/ACSDT5Y2024.B08301) | Means of Transportation to Work | Workers 16 years and over |
| [B08303](https://data.census.gov/table/ACSDT5Y2024.B08303) | Travel Time to Work | Workers 16 years and over who did not work from home |
| [B15003](https://data.census.gov/table/ACSDT5Y2024.B15003) | Educational Attainment for the Population 25 Years and Over | Population 25 years and over |
| [B17020B](https://data.census.gov/table/ACSDT5Y2024.B17020B) | Poverty Status in the Past 12 Months by Age (Black or African American Alone) | Black or African American alone population for whom poverty status is determined |
| [B18101](https://data.census.gov/table/ACSDT5Y2024.B18101) | Sex by Age by Disability Status | Civilian noninstitutionalized population |
| [B19013](https://data.census.gov/table/ACSDT5Y2024.B19013) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) | Households |
| [B19013B](https://data.census.gov/table/ACSDT5Y2024.B19013B) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (Black or African American Alone Householder) | Households with a householder who is Black or African American alone |
| [B19013D](https://data.census.gov/table/ACSDT5Y2024.B19013D) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (Asian Alone Householder) | Households with a householder who is Asian alone |
| [B19013H](https://data.census.gov/table/ACSDT5Y2024.B19013H) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (White Alone, Not Hispanic or Latino Householder) | Households with a householder who is White alone, not Hispanic or Latino |
| [B19013I](https://data.census.gov/table/ACSDT5Y2024.B19013I) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (Hispanic or Latino Householder) | Households with a householder who is Hispanic or Latino |
| [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301) | Per Capita Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) | Total population |
| [B22010](https://data.census.gov/table/ACSDT5Y2024.B22010) | Receipt of Food Stamps/SNAP in the Past 12 Months by Disability Status for Households | Households |
| [B23025](https://data.census.gov/table/ACSDT5Y2024.B23025) | Employment Status for the Population 16 Years and Over | Population 16 years and over |
| [B25002](https://data.census.gov/table/ACSDT5Y2024.B25002) | Occupancy Status | Housing units |
| [B25003](https://data.census.gov/table/ACSDT5Y2024.B25003) | Tenure | Occupied housing units |
| [B25024](https://data.census.gov/table/ACSDT5Y2024.B25024) | Units in Structure | Housing units |
| [B25034](https://data.census.gov/table/ACSDT5Y2024.B25034) | Year Structure Built | Housing units |
| [B25044](https://data.census.gov/table/ACSDT5Y2024.B25044) | Tenure by Vehicles Available | Occupied housing units |
| [B25064](https://data.census.gov/table/ACSDT5Y2024.B25064) | Median Gross Rent (Dollars) | Renter-occupied housing units paying cash rent |
| [B25070](https://data.census.gov/table/ACSDT5Y2024.B25070) | Gross Rent as a Percentage of Household Income in the Past 12 Months | Renter-occupied housing units |
| [B25077](https://data.census.gov/table/ACSDT5Y2024.B25077) | Median Value (Dollars) | Owner-occupied housing units |
| [B26001](https://data.census.gov/table/ACSDT5Y2024.B26001) | Group Quarters Population | Population in group quarters |
| [B27001](https://data.census.gov/table/ACSDT5Y2024.B27001) | Health Insurance Coverage Status by Sex by Age | Civilian noninstitutionalized population |
| [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001) | Types of Computers in Household | Households |
| [B28002](https://data.census.gov/table/ACSDT5Y2024.B28002) | Presence and Types of Internet Subscriptions in Household | Households |
| [C17002](https://data.census.gov/table/ACSDT5Y2024.C17002) | Ratio of Income to Poverty Level in the Past 12 Months | Population for whom poverty status is determined |

## Schema

`geoid` is 2 characters and is the join key: every finer geography's `substr(geoid, 1, 2)` is this column.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 2-character state FIPS code. |
| `name` | string | Human-readable name, assembled from the boundary files' name parts (block group, tract, county, state as applicable). |
| `state` | string | Two-letter USPS state or territory code. |
| `population` | int64 | Total population. |
| `population_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `population`. |
| `aland_sqkm` | double | Land area in km² (water excluded), 3 decimals. |
| `pop_density` | double | People per square kilometre of land area, rounded to 1 decimal: `population / aland_sqkm`. |
| `median_hh_income` | double | Median household income in the past 12 months, in 2024 inflation-adjusted dollars. |
| `median_hh_income_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income`. |
| `median_hh_income_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income`. |
| `per_capita_income` | double | Per capita income in the past 12 months, in 2024 inflation-adjusted dollars — aggregate income divided by total population, so children and people with no income are in the denominator. |
| `per_capita_income_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `per_capita_income`. |
| `pct_below_poverty` | double | Percent of the population below the federal poverty level — an income-to-poverty ratio under 1.00. |
| `pct_below_poverty_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_below_poverty`. |
| `pct_below_poverty_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_below_poverty`. |
| `pct_below_2x_poverty` | double | Percent of the population with an income-to-poverty ratio under 2.00 — a common proxy for low income rather than deep poverty. |
| `pct_below_2x_poverty_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_below_2x_poverty`. |
| `pct_snap` | double | Percent of households that received Food Stamps/SNAP benefits at any time in the past 12 months. |
| `pct_snap_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_snap`. |
| `pct_unemployed` | double | Unemployment rate: unemployed people as a percent of the civilian labor force. |
| `pct_unemployed_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_unemployed`. |
| `median_age` | double | Median age in years. |
| `median_age_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_age`. |
| `pct_under_18` | double | Percent of the population under 18 years old. |
| `pct_under_18_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_under_18`. |
| `pct_65_plus` | double | Percent of the population 65 years and over. |
| `pct_65_plus_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_65_plus`. |
| `pct_white_nh` | double | Percent of the population that is White alone and not Hispanic or Latino. |
| `pct_white_nh_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_white_nh`. |
| `pct_black` | double | Percent of the population that is Black or African American alone and not Hispanic or Latino. |
| `pct_black_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_black`. |
| `pct_native` | double | Percent of the population that is American Indian and Alaska Native alone and not Hispanic or Latino. |
| `pct_native_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_native`. |
| `pct_asian` | double | Percent of the population that is Asian alone and not Hispanic or Latino. |
| `pct_asian_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_asian`. |
| `pct_hispanic` | double | Percent of the population that is Hispanic or Latino, of any race. |
| `pct_hispanic_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_hispanic`. |
| `pct_people_of_color` | double | Percent of the population that is not White-alone non-Hispanic: `100 − pct_white_nh`. |
| `pct_people_of_color_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_people_of_color`. |
| `pct_bachelors_plus` | double | Percent of adults 25 and over whose highest attainment is a bachelor's degree or more. |
| `pct_bachelors_plus_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_bachelors_plus`. |
| `housing_units` | int64 | Total housing units, occupied and vacant. |
| `housing_units_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `housing_units`. |
| `pct_vacant_units` | double | Percent of housing units that are vacant. |
| `pct_vacant_units_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_vacant_units`. |
| `households` | int64 | Households — occupied housing units. |
| `households_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `households`. |
| `pct_owner_occupied` | double | Percent of occupied housing units that are owner-occupied. |
| `pct_owner_occupied_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_owner_occupied`. |
| `median_gross_rent` | double | Median gross rent in dollars per month — contract rent plus the estimated average monthly cost of utilities and fuels. |
| `median_gross_rent_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_gross_rent`. |
| `median_gross_rent_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_gross_rent`. |
| `pct_rent_burdened` | double | Percent of renter households paying 30% or more of household income on gross rent — the standard affordability threshold. |
| `pct_rent_burdened_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_rent_burdened`. |
| `pct_rent_burdened_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_rent_burdened`. |
| `pct_severely_rent_burdened` | double | Percent of renter households paying 50% or more of household income on gross rent. |
| `pct_severely_rent_burdened_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_severely_rent_burdened`. |
| `median_home_value` | double | Median value of owner-occupied housing units, in dollars — the owner's estimate of what the property would sell for, not an assessment or a sale price. |
| `median_home_value_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_home_value`. |
| `median_home_value_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_home_value`. |
| `pct_built_pre_1940` | double | Percent of housing units built in 1939 or earlier. |
| `pct_built_pre_1940_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_built_pre_1940`. |
| `pct_single_family` | double | Percent of housing units in single-family structures. |
| `pct_single_family_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_single_family`. |
| `hh_no_vehicle` | int64 | Occupied housing units with no vehicle available, owner- and renter-occupied combined. |
| `hh_no_vehicle_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `hh_no_vehicle`. |
| `pct_hh_no_vehicle` | double | Percent of occupied housing units with no vehicle available. |
| `pct_hh_no_vehicle_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_hh_no_vehicle`. |
| `pct_hh_no_vehicle_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_hh_no_vehicle`. |
| `pct_commute_drive_alone` | double | Percent of workers who drove alone to work in a car, truck or van. |
| `pct_commute_drive_alone_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_commute_drive_alone`. |
| `pct_commute_transit` | double | Percent of workers who commuted by public transportation. |
| `pct_commute_transit_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_commute_transit`. |
| `pct_commute_transit_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_commute_transit`. |
| `pct_commute_walk_bike` | double | Percent of workers who walked or bicycled to work. |
| `pct_commute_walk_bike_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_commute_walk_bike`. |
| `pct_work_from_home` | double | Percent of workers who worked from home. |
| `pct_work_from_home_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_work_from_home`. |
| `pct_commute_45min_plus` | double | Percent of commuters whose one-way travel time to work is 45 minutes or more. |
| `pct_commute_45min_plus_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_commute_45min_plus`. |
| `pct_no_internet` | double | Percent of households with no internet access of any kind. |
| `pct_no_internet_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_no_internet`. |
| `pct_no_internet_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_no_internet`. |
| `pct_no_computer` | double | Percent of households with no computing device — no desktop or laptop, no smartphone, no tablet, no other computer. |
| `pct_no_computer_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_no_computer`. |
| `pct_uninsured` | double | Percent of the civilian noninstitutionalized population with no health insurance coverage. |
| `pct_uninsured_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_uninsured`. |
| `pct_uninsured_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_uninsured`. |
| `pct_with_disability` | double | Percent of the civilian noninstitutionalized population with a disability, as the ACS's six-question sequence defines it (hearing, vision, cognitive, ambulatory, self-care, independent living). |
| `pct_with_disability_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_with_disability`. |
| `pct_with_disability_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_with_disability`. |
| `pct_foreign_born` | double | Percent of the population that is foreign-born — anyone not a U.S. citizen at birth, naturalized citizens included. |
| `pct_foreign_born_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_foreign_born`. |
| `group_quarters_pop` | int64 | Population living in group quarters — correctional facilities, nursing facilities, college and university housing, military quarters, group homes, shelters. |
| `group_quarters_pop_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `group_quarters_pop`. |
| `median_hh_income_black` | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is Black or African American alone. |
| `median_hh_income_black_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_black`. |
| `median_hh_income_black_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_black`. |
| `median_hh_income_white_nh` | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is White alone, not Hispanic or Latino. |
| `median_hh_income_white_nh_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_white_nh`. |
| `median_hh_income_white_nh_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_white_nh`. |
| `median_hh_income_asian` | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is Asian alone. |
| `median_hh_income_asian_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_asian`. |
| `median_hh_income_asian_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_asian`. |
| `median_hh_income_hispanic` | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is Hispanic or Latino, of any race. |
| `median_hh_income_hispanic_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_hispanic`. |
| `median_hh_income_hispanic_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_hispanic`. |
| `pct_below_poverty_black` | double | Percent of the Black or African American alone population below the poverty level. |
| `pct_below_poverty_black_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_below_poverty_black`. |
| `pct_below_poverty_black_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_below_poverty_black`. |
| `geometry` | binary | Boundary polygon, WKB, EPSG:4326 / OGC:CRS84. |
| `bbox` | struct<xmin, ymin, xmax, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, with row-group statistics. |

## Field notes

- **Eleven of the 112 columns are NULL on all 56 rows** (measured), and all
  eleven are margins: `population_moe`, `pct_under_18_moe`, `pct_65_plus_moe`,
  `pct_white_nh_moe`, `pct_black_moe`, `pct_native_moe`, `pct_asian_moe`,
  `pct_hispanic_moe`, `pct_people_of_color_moe`, `pct_foreign_born_moe` and
  `group_quarters_pop_moe`. Every one of them belongs to a count of, or a share
  of, the **total population**, whose own margin is absent at this geography;
  the build writes NULL rather than a guess when an input margin is NULL
  (`tools/column_docs.py`), so those shares inherit the gap. Read `population`
  as a count to use rather than an estimate to put an interval on, and check
  for NULLs before putting any of these into a quadrature sum
  (`sqrt(sum(moe*moe))` over a NULL-bearing column returns NULL). Every other
  `*_moe` column here is populated on all 52 rows that have ACS data;
  [`counties`](../../counties/counties/collection.json) has the
  `population_moe` gap on 3,103 of its 3,235 rows.
- **That NULL is upstream, and it is not suppression.** Each of those columns
  comes from a total-population table (B01001, B01003, B03002, B05002, B26001), and in the release's own
  `.dat` files those rows carry the estimate beside `-555555555`, the
  **controlled-MOE** jam value a controlled estimate gets in place of a
  sampling margin — `0400000US06|39287377|-555555555` in
  `staging/census-cache/acsdt5y2024-b01003.dat`, read 2026-11-15. The build
  turns it into NULL rather than publishing it as a number
  (`tools/build_acs.py`). The same columns carry margins normally at the finer
  geographies, where the estimates are not controlled this way:
  `population_moe` is carried on 33,759 of 33,791 ZCTAs and on all 241,854
  populated block groups (measured).
- **Every other estimate has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. To compare two geographies, check
  whether their margins overlap before calling a difference real. To sum
  estimates across geographies, add the margins in quadrature
  (`sqrt(sum(moe*moe))`). **Never sum or average a median**: a median of a
  region is not derivable from the medians of its parts.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. Filtering or greying out by CV is the intended use.
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area, and neither number is wrong.
- **`pct_unemployed` divides by the civilian labor force** (B23025 line 3), not by the population 16 and over. That is what makes it an unemployment rate.
- **The rent-burden columns divide by renter households *excluding* those whose rent-to-income ratio the Bureau could not compute** (B25070 line 1 minus line 11, "Not computed"). Including them would understate the burden.
- **`pct_commute_45min_plus` divides by workers who did not work from home** (B08303's own universe), while every other commute share divides by all workers 16+ (B08301). The two denominators differ, so the shares do not sum across tables.
- **`pct_people_of_color` is a complement** (`100 − pct_white_nh`), which holds exactly on all 52 rows with data (measured). It carries `pct_white_nh`'s margin of error unchanged — and at this geography that margin is NULL, so neither column can be significance-tested from this file. The four non-Hispanic race shares plus `pct_hispanic` are also not exhaustive: they sum to between 69.12 and 99.78 across the 52 rows (measured), because B03002's remaining non-Hispanic categories are not published here.
- **`pct_uninsured` and `pct_with_disability` are shares of the civilian noninstitutionalized population**, not of everyone: people on active duty and people in institutions are outside the universe.
- **The race-iteration medians are classified by the householder's race**, not by every member's, and each has its own universe (households with a householder who is …). They are not shares of a common total and cannot be averaged together.
- **`pct_below_poverty_black` has a race-specific denominator** (the Black alone population for whom poverty status is determined), so it is not comparable to `pct_below_poverty`'s denominator.
- **The four race shares are all non-Hispanic** (`pct_white_nh`, `pct_black`, `pct_native`, `pct_asian`), drawn from B03002's "Not Hispanic or Latino" branch, so they and `pct_hispanic` are mutually exclusive and do not double-count.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 4 of 56 rows: American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have boundaries here but no ACS 5-year data, because the island areas run a separate decennial-only program. 52 rows carry data. |
| every other data column | NULL on exactly the same 4 rows and no others. **Nothing in this table is suppressed**: 95 of the 112 columns are populated on exactly those 52 rows, the four race-iteration medians included (measured — true at no other geography; `median_hh_income_black` is NULL on 39.47% of counties and 61.43% of tracts). The remaining 17 are the 11 all-NULL margins below, plus `geoid`, `name`, `state` and `aland_sqkm` on all 56 rows, plus `geometry` and `bbox`. |
| the 11 all-NULL margins | `population_moe` and the ten other margins listed in the field notes are NULL on all 56 rows. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 17 ZCTAs, 279 places and 4 delegate districts.

Margins of error are small at this geography and no column needs a reliability filter: across all 15 `*_cv` columns the highest median is 0.037 (`pct_commute_transit_cv`) and the single worst value anywhere in the table is 0.213 (`pct_below_poverty_black_cv`), both measured, against the 0.40 "unreliable" line. That is a statement about single values, not about comparisons — of the 51 adjacent pairs in a ranking of the 52 states by `median_hh_income`, only 15 have non-overlapping 90% intervals (measured). Still never compare two geographies without checking whether their margins overlap, and never aggregate a median.

The PMTiles carry real geometries at every zoom, band `0-8:geom` (`tools/make_tiles.py`) — the features are few enough to tile directly, so there is no coarser-geography band at coarse zooms (the catalog's finer collections switch to counties and tracts there). `*_moe` columns are excluded from every tile at every zoom; `*_cv` columns are kept. Statistics still come from the GeoParquet.

## Related collections

- The five themed siblings in this group, same 56 rows, joining 1:1 on `geoid`: [state-income](../state-income/collection.json), [state-people](../state-people/collection.json), [state-housing](../state-housing/collection.json), [state-connectivity](../state-connectivity/collection.json), [state-wellbeing](../state-wellbeing/collection.json). Their agent guides carry the per-theme field notes and 4–5 tested recipes each.
- [`states/` group guide](../AGENTS.md) — what this geography is, and when to step down from it.
- [`counties/counties`](../../counties/counties/collection.json) — the same 112 columns at the next geography down, 3,235 rows.
- [`zctas/zctas`](../../zctas/zctas/collection.json), [`places/places`](../../places/places/collection.json), [`congressional-districts/congressional-districts`](../../congressional-districts/congressional-districts/collection.json) — the same 112 columns at the other statistical geographies.
- [`block-groups/`](../../block-groups/catalog.json) and [`tracts/`](../../tracts/catalog.json) — the same indicators split into themed chunks at finer geographies, where a wide table is not published because a national block-group file is large.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run against the published URLs with DuckDB 1.4.1
immediately before it was written down, and its real output and wall-clock time
are quoted beside it. The timings are real network runs against
`data.source.coop`; this collection's data files were already on the mirror,
and the restructure into a group directory did not move them, so the URLs and
the timings below are unchanged. (The five themed siblings' guides quote no
timings, because those files had not been uploaded when their queries were
run.)

56 rows and 3.9 MB: no filter is ever needed for cost here, and `SELECT *` is a
reasonable thing to do.

### 1. The whole country, ranked

```sql
INSTALL httpfs; LOAD httpfs;
SELECT name, population, median_hh_income::int AS income,
       round(median_hh_income_cv, 4) AS cv, pct_below_poverty
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet'
WHERE median_hh_income IS NOT NULL
ORDER BY median_hh_income DESC LIMIT 5;
```

→ `District of Columbia | 681294 | 109870 | 0.011 | 15.44`, `Massachusetts |
7044056 | 103960 | 0.003 | 10.04`, `Maryland | 6206011 | 103678 | 0.004 |
9.45`, `New Jersey | 9343809 | 103556 | 0.003 | 9.72`, `Hawaii | 1445235 |
100389 | 0.007 | 10.04`. 4.2 s.

The `IS NOT NULL` filter is not cosmetic — four of the 56 rows have no ACS data
at all:

```sql
LOAD httpfs;
SELECT count(*) AS rows, count(population) AS with_acs_data,
       string_agg(name, ', ') FILTER (WHERE population IS NULL) AS no_data
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet';
```

→ `56 | 52 | American Samoa, United States Virgin Islands, Guam, Commonwealth
of the Northern Mariana Islands`. 1.4 s. The island areas run a decennial-only
program, so they have 2024 boundaries and no ACS 5-year estimates. Any
`ORDER BY … ASC` without that filter returns four NULL rows first, and any
`count(*)` denominator of 56 is wrong by four.

### 2. How much does a state average hide? (GEOID prefix join to counties)

```sql
LOAD httpfs;
SELECT s.state, s.median_hh_income::int AS state_income,
       min(c.median_hh_income)::int    AS poorest_county,
       max(c.median_hh_income)::int    AS richest_county,
       round(max(c.median_hh_income)/min(c.median_hh_income), 2) AS ratio
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet' s
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet' c
  ON s.geoid = substr(c.geoid, 1, 2)
WHERE s.median_hh_income IS NOT NULL AND c.median_hh_income IS NOT NULL
GROUP BY 1, 2 ORDER BY ratio DESC LIMIT 5;
```

→ `KY | 63726 | 22188 | 122497 | 5.52`, `GA | 77353 | 28380 | 143784 | 5.07`,
`TN | 69595 | 28814 | 135594 | 4.71`, `VA | 93170 | 38675 | 181765 | 4.7`,
`CO | 95470 | 36861 | 149594 | 4.06`. 6.2 s.

Kentucky's richest county has 5.5× the median income of its poorest, and the
state figure of $63,726 describes neither. `substr(c.geoid, 1, 2) = s.geoid`
is the whole join — a county GEOID begins with its state's FIPS code. This is
the query to run before quoting any state-level number as a description of
anywhere in particular.

### 3. Reliability at this geography: the CVs are tiny

```sql
LOAD httpfs;
SELECT max(median_hh_income_cv)  AS worst_income_cv,
       max(pct_below_poverty_cv) AS worst_poverty_cv,
       max(median_gross_rent_cv) AS worst_rent_cv,
       max(pct_uninsured_cv)     AS worst_uninsured_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet';
```

→ `0.011 | 0.031 | 0.01 | 0.042`. 2.2 s.

The *worst* CV on any of these columns across all 52 states with data is
0.042, far inside the 0.12 "reliable" threshold. So: no `_cv` filtering is
needed at state level, and conversely, class breaks measured from this
collection will be useless at tract or block-group level, where the same
columns run to 0.40 and beyond. Reliability is a property of geography size,
not of the column.

### 4. A national total, with its margin in quadrature

```sql
LOAD httpfs;
SELECT count(*)                                            AS states_counted,
       sum(households)                                     AS us_households,
       round(sqrt(sum(households_moe*households_moe)))     AS quadrature_moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet'
WHERE households IS NOT NULL AND state <> 'PR';
```

→ `51 | 129227496 | 48498`. 3.6 s. 129.2 million households across the 50
states and DC, ±48,498 at 90% confidence.

`sqrt(sum(moe*moe))` is the Census Bureau's own rule for a derived sum: the
margins are independent, so they add in quadrature rather than linearly
(linear addition gives ±279,582 here, measured — 5.8 times too wide).
Two conditions on using it:

- **It applies to counts, never to medians.** There is no formula that turns
  52 state medians into a national median; the quantity does not exist in this
  file and must not be constructed.
- **It silently returns NULL if any margin is NULL.** `population_moe` is NULL
  on all 56 rows of this collection (measured — see the field notes), as are
  ten other margins, so `sqrt(sum(population_moe*population_moe))` over these
  rows returns NULL rather than a number. That is the right answer, and it is
  the reason to check.

A related check worth knowing: the county rows **sum exactly** to the state row
for `households` in all 52 states, while the quadrature margin of that sum is
not the state's published margin — the Bureau estimates each state directly.
That one is measured in
[`states/state-housing/AGENTS.md`](../state-housing/AGENTS.md).

### Related recipes elsewhere

- The five themed cuts of this same table, each with its own tested recipes:
  [state-income](../state-income/AGENTS.md),
  [state-people](../state-people/AGENTS.md),
  [state-housing](../state-housing/AGENTS.md),
  [state-connectivity](../state-connectivity/AGENTS.md),
  [state-wellbeing](../state-wellbeing/AGENTS.md).
- The counties inside a state, each against its state:
  [`counties/AGENTS.md`](../../counties/AGENTS.md) and
  [`counties/county-income/AGENTS.md`](../../counties/county-income/AGENTS.md).
- Cities against their states, districts against their states:
  [`places/AGENTS.md`](../../places/AGENTS.md),
  [`congressional-districts/congressional-districts/AGENTS.md`](../../congressional-districts/congressional-districts/AGENTS.md).
- The geography most small-area social research is done at, for when 52 rows
  are too coarse: [`tracts/AGENTS.md`](../../tracts/AGENTS.md).
- 2020 Decennial complete counts, which sum to published state totals exactly:
  [`blocks/AGENTS.md`](../../blocks/AGENTS.md).

Statistics come from the GeoParquet. The state PMTiles archive is real polygons
at every zoom — it needs no coarser-geography band at coarse zooms — but
carries no `*_moe` columns.
