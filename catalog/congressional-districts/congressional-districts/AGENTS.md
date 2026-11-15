# Agent guide — All Indicators (Congressional Districts, 119th Congress)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections, and the [group guide](../AGENTS.md) covers what the six congressional-district collections share; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Every indicator in this catalog's ACS column set, in one table, for every congressional district: income and poverty, age and race and education, housing cost and tenure, vehicles and commuting and internet access, health insurance and disability and nativity, and median household income by race and ethnicity.

At 441 features width costs almost nothing, so the whole 112-column table is
published here as well as a theme at a time in the five themed chunks beside
it — a cross-theme question needs no join. **This collection is the sixth
sibling of its group**: [`cd-income`](../cd-income/collection.json),
[`cd-people`](../cd-people/collection.json),
[`cd-housing`](../cd-housing/collection.json),
[`cd-connectivity`](../cd-connectivity/collection.json) and
[`cd-wellbeing`](../cd-wellbeing/collection.json) hold the same 441 rows and
the same geometry, each with one theme's columns and its own class breaks
measured on the district distribution; this collection holds all of them. The
chunks are not a download saving: over 99% of each of these files is
`geometry` (99.29–99.48%, measured with `parquet_metadata`; 8,815,141 of
8,861,372 bytes of column data in `cd-income.parquet`). Pick a chunk for its
column set and its styles, and pick this wide table whenever a question
crosses themes.

**These are the districts of the 119th Congress**, the vintage the ACS 2020–2024 5-year release tabulates. Three independent confirmations: the release's own summary-level prefix is `5001900US` (the `19`), the cartographic boundary file is `cb_2024_us_cd119_500k` with `CDSESSN = '119'` on all 441 features, and the Census Bureau's [ACS geography boundaries by year](https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year/2024.html) lists "Congressional District, Delegate District DC, Resident Commissioner District PR" with the vintage "119th Congress of the United States". **District numbers are not stable between congresses**, so these GEOIDs must not be joined to an earlier congress's districts of the same number, a `geoid` here is not the same ground as the same `geoid` in an earlier congress, and these estimates must never be read as a time series.

**441 rows**, one per congressional district, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.pmtiles`, layer `congressional-districts`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts/collection.json` — carries a full description for every column
- **Group sub-catalog**: `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/catalog.json` — this collection and its five themed siblings

The metadata moved down a directory in the 2026-11-15 restructure and **the
data files did not**: `collection.json`, `README.md` and `styles/` now sit in
`congressional-districts/congressional-districts/`, while the `.parquet` and
`.pmtiles` stay one level up at `congressional-districts/`. The two data URLs
above are unchanged and remain correct. A themed sibling keeps both together:
`congressional-districts/cd-income/cd-income.parquet`.

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

`geoid` is 4 characters — state FIPS (2) + district (2) — so `substr(geoid, 1, 2)` joins [`states`](../../states/states/collection.json). At-large states use district `00` (AK, DE, ND, SD, VT, WY) and the non-voting delegate districts use `98`: `1198` District of Columbia, `7298` Puerto Rico, `6098` American Samoa, `6698` Guam, `6998` Northern Mariana Islands, `7898` U.S. Virgin Islands. Nothing finer joins by prefix — district boundaries follow 2020 census blocks, not counties or tracts.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 4-character congressional district GEOID: state FIPS 2 + district 2, e.g. `0612` for California's 12th. 119th Congress. |
| `name` | string | `NAMELSAD` from the 2024 cd119 cartographic boundary file plus the state name — "Congressional District 12, California", "Delegate District (at Large), District of Columbia". |
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

- **441 rows, not 435.** The 435 voting districts plus the District of Columbia delegate district (`1198`), Puerto Rico's Resident Commissioner district (`7298`) and the four island-area delegate districts (`6098`, `6698`, `6998`, `7898`), which carry geometry but no ACS estimates. Filter `state NOT IN ('DC','PR','AS','GU','MP','VI')` for the 435 voting districts, or `population IS NOT NULL` for the 437 rows with data.
- **Three ACS district rows are absent**: `09ZZ`, `17ZZ` and `33ZZ`, water-only pseudo-districts in Connecticut, Illinois and New Hampshire, have no polygon in the boundary file and so no row here. The ACS release tabulates 440 district rows (counted in the downloaded B01003 summary file); 437 of them have a polygon here, those three do not, and the four island-area delegate districts have a polygon and no ACS row — 437 + 4 = 441. Nothing is lost: the three ACS rows read `0|14`, `0|13` and `0|12`, population exactly 0.
- **Districts are equal-population by construction** — 546,488 to 1,021,191 across the 435 voting districts, 771,301 at the median (measured) — so every rate in this collection has a much narrower spread than at any other geography, and the margins of error are the narrowest in the catalog: all 15 `*_cv` columns have a median below 0.11, and the largest CV anywhere in the table is 0.48, on `median_hh_income_black`. Class breaks borrowed from county- or tract-level work collapse here — the tract poverty breaks put 290 of the 437 districts with data into a single class and leave one class empty (measured in [`cd-income`](../cd-income/AGENTS.md)) — which is why the themed siblings ship breaks measured on the district distribution.
- **A NULL margin can mean "controlled, no sampling error".** `population_moe` is NULL on 18 rows: the four island-area districts with no data at all, plus 14 districts whose ACS margin is the jam value `-555555555`, which `tools/build_acs.py` documents as "controlled, no sampling error" and turns into NULL. Those 14 are the eight single-district jurisdictions (AK `0200`, DE `1000`, DC `1198`, ND `3800`, SD `4600`, VT `5000`, WY `5600`, PR `7298`) plus all four Iowa districts and both West Virginia districts; the ACS row for Alaska reads `5001900US0200|735706|-555555555`. Because the derived-percentage margin needs its denominator's margin, every share built on total population is NULL on those same 18 rows — `pct_under_18_moe`, `pct_65_plus_moe`, the four non-Hispanic race-share margins, `pct_hispanic_moe`, `pct_people_of_color_moe` and `pct_foreign_born_moe`, each carried on 423 of the 441 rows. Read a missing margin as "not published", never as zero uncertainty and never as an unreliable estimate.
- **Every estimate has a `<name>_moe`**, at the 90% confidence level — the
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
- **`pct_people_of_color` is a complement** (`100 − pct_white_nh`) and carries `pct_white_nh`'s margin of error unchanged.
- **`pct_uninsured` and `pct_with_disability` are shares of the civilian noninstitutionalized population**, not of everyone: people on active duty and people in institutions are outside the universe.
- **The race-iteration medians are classified by the householder's race**, not by every member's, and each has its own universe (households with a householder who is …). They are not shares of a common total and cannot be averaged together.
- **`pct_below_poverty_black` has a race-specific denominator** (the Black alone population for whom poverty status is determined), so it is not comparable to `pct_below_poverty`'s denominator.
- **The four non-Hispanic race shares** — `pct_white_nh`, `pct_black`, `pct_native`, `pct_asian` — are all drawn from B03002's "Not Hispanic or Latino" branch, so they and `pct_hispanic` are mutually exclusive and do not double-count. They do not sum to 100: B03002's "Native Hawaiian and Other Pacific Islander", "Some other race" and "Two or more races" branches are not published here, so the five shares together run 64.23 to 99.78 with a median of 95.43 across districts (measured). `pct_people_of_color` is the complement of `pct_white_nh` and does cover the remainder.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.91% of districts — the four island-area delegate districts (American Samoa, Guam, the Northern Mariana Islands, the U.S. Virgin Islands), which have 2024 boundaries but no ACS 5-year estimates. |
| every other column | NULL on exactly those same four rows (0.91%), with one exception below. This is the most complete collection in the catalog: no suppression anywhere else, not even on the race-iteration medians. |
| `median_hh_income_asian` | NULL on 1.13% of districts: the four island-area rows plus one district with no published Asian-householder median. |

Row count checked against the Census Bureau's own [geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html): 441 congressional districts (436 United States including the District of Columbia delegate + 1 Puerto Rico + 4 island areas), which is exactly the row count here, and 441 distinct GEOIDs.

Spot-checked against data.census.gov: CA-12 median household income $108,648, NY-12 $147,775, AL-01 $66,291, and the DC delegate district's population 681,294 equals the `states` collection's District of Columbia population, as it must.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

The PMTiles archive is real polygons at every zoom (z0–z10), with no coarser-geography band at coarse zooms — there are few enough districts to draw them all nationally. Statistics still come from the GeoParquet: `*_moe` columns are not in the tiles.

## Related collections

- [`congressional-districts/cd-income`](../cd-income/collection.json) ([agent guide](../cd-income/AGENTS.md)) — Income & Poverty, the same 441 districts. Same `geoid`, joins 1:1.
- [`congressional-districts/cd-people`](../cd-people/collection.json) ([agent guide](../cd-people/AGENTS.md)) — People & Education, joins 1:1.
- [`congressional-districts/cd-housing`](../cd-housing/collection.json) ([agent guide](../cd-housing/AGENTS.md)) — Housing & Rent, joins 1:1.
- [`congressional-districts/cd-connectivity`](../cd-connectivity/collection.json) ([agent guide](../cd-connectivity/AGENTS.md)) — Commuting & Connectivity, joins 1:1.
- [`congressional-districts/cd-wellbeing`](../cd-wellbeing/collection.json) ([agent guide](../cd-wellbeing/AGENTS.md)) — Health, Disability & Income by Race, joins 1:1.
- [`zctas`](../../zctas/zctas/collection.json) and [`places`](../../places/places/collection.json) — the same 112 columns at the catalog's other wide geographies.
- [`counties`](../../counties/counties/collection.json) and [`states`](../../states/states/collection.json) — the same 112 columns; `substr(geoid, 1, 2)` joins a district to its state.
- [`block-groups/`](../../block-groups/catalog.json) and [`tracts/`](../../tracts/catalog.json) — the same indicators split into themed chunks, for looking inside a district.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, the geography districts are drawn from. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run against the published URLs with DuckDB 1.4.1
immediately before it was written down, and its real output is quoted beside
it. 441 rows and 9 MB: cost is never a reason to filter in this collection.

### 1. One district's profile

```sql
INSTALL httpfs; LOAD httpfs;
SELECT name, population, median_hh_income::int AS income, pct_below_poverty,
       pct_bachelors_plus, pct_commute_transit, pct_hh_no_vehicle,
       pct_uninsured, median_gross_rent::int AS rent, pct_rent_burdened
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.parquet'
WHERE geoid = '0612';            -- state FIPS 06 + district 12 = CA-12
```

→ `Congressional District 12, California | 748393 | 108648 | 12.54 | 54.06 |
11.67 | 15.1 | 4.54 | 2133 | 51.17`. **4.6 s**, and the income matches the
data.census.gov spot-check in the section above.

The GEOID is four characters: two of state FIPS, two of district number,
zero-padded — `0612`, not `CA12` and not `612`. At-large and delegate
districts use `98` (`1198` for the District of Columbia, `7298` for Puerto
Rico). `SELECT *` on one row returns all 112 columns if you want the whole
profile; this subset is just the readable version.

### 2. Where does that district rank nationally?

```sql
LOAD httpfs;
WITH r AS (
  SELECT geoid, name,
         rank() OVER (ORDER BY median_hh_income DESC)    AS rank_income,
         rank() OVER (ORDER BY pct_below_poverty DESC)   AS rank_poverty,
         rank() OVER (ORDER BY pct_commute_transit DESC) AS rank_transit
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.parquet'
  WHERE population IS NOT NULL)
SELECT name, rank_income, rank_poverty, rank_transit,
       (SELECT count(*) FROM r) AS of_districts
FROM r WHERE geoid = '0612';
```

→ `Congressional District 12, California | 57 | 187 | 26 | 437`. 3.2 s.

57th of 437 by income, 26th by transit commuting, middling on poverty. The
`WHERE population IS NOT NULL` is what makes the denominator honest: it drops
the four island-area delegate districts, which have boundaries and no ACS
estimates, and leaves the 437 rows that can actually be ranked. Without it,
`rank()` on a `DESC` ordering puts four NULL rows at the top and every rank
shifts by four.

For the 435 voting districts only, filter
`state NOT IN ('DC','PR','AS','GU','MP','VI')` instead.

### 3. Every district against its own state (GEOID prefix join)

```sql
LOAD httpfs;
SELECT d.name, d.median_hh_income::int AS district_income,
       s.median_hh_income::int         AS state_income,
       (d.median_hh_income - s.median_hh_income)::int AS gap
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.parquet' d
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet' s
  ON substr(d.geoid, 1, 2) = s.geoid
WHERE d.state = 'NY'
ORDER BY gap DESC LIMIT 5;
```

→ `Congressional District 12, New York | 147775 | 85974 | 61801`, `District 4 |
141082 | 85974 | 55108`, `District 3 | 139677 | 85974 | 53703`, `District 1 |
134242 | 85974 | 48268`, `District 2 | 128330 | 85974 | 42356`. 4.7 s. NY-12's
$147,775 matches the data.census.gov spot-check above.

`substr(geoid, 1, 2)` is the only prefix join available: districts are not
built from counties or tracts in any GEOID sense, and relating a district to
the tracts inside it is a spatial operation (the `bbox` + `ST_Intersects`
pattern in [`zctas/AGENTS.md`](../../zctas/AGENTS.md)).

### 4. Why `*_cv` filtering is pointless here — and where it is not

```sql
LOAD httpfs;
SELECT round(max(median_hh_income_cv), 3)       AS max_income_cv,
       round(max(pct_below_poverty_cv), 3)      AS max_poverty_cv,
       round(max(pct_rent_burdened_cv), 3)      AS max_rent_burden_cv,
       round(max(median_hh_income_black_cv), 3) AS max_black_income_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.parquet';
```

→ `0.021 | 0.05 | 0.033 | 0.48`. 2.8 s.

Districts are equal-population by construction, so the headline columns are
the most precise in the catalog: the *worst* CV on median household income
across all 441 districts is 0.021, six times inside the 0.12 reliability
threshold. A `WHERE median_hh_income_cv < 0.12` filter here removes nothing,
and class breaks borrowed from tract or county work will put almost every
district in one class.

The fourth number is the exception that keeps the habit worth having:
`median_hh_income_black_cv` reaches 0.48. The race-iteration medians rest on a
subset of households, so they carry real uncertainty even at this geography —
filter *those* on `_cv` as you would anywhere else.

### 5. What is inside a district? Spatially, because no prefix reaches it

```sql
LOAD spatial; LOAD httpfs;
WITH d AS (
  SELECT geoid, geometry, bbox
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.parquet'
  WHERE geoid = '0612')
SELECT c.geoid AS county_geoid, c.name AS county,
       round(ST_Area(ST_Intersection(c.geometry, d.geometry))
             / ST_Area(d.geometry) * 100, 2) AS pct_of_district_area
FROM d
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet' c
  ON  c.bbox.xmin <= d.bbox.xmax AND c.bbox.xmax >= d.bbox.xmin
  AND c.bbox.ymin <= d.bbox.ymax AND c.bbox.ymax >= d.bbox.ymin
WHERE ST_Intersects(c.geometry, d.geometry)
ORDER BY pct_of_district_area DESC;
```

→ `06001 | Alameda County, California | 99.96`, `06075 | San Francisco
County, California | 0.04`, `06013 | Contra Costa County, California | 0.0`.
(Run against local copies of these two published files, so no wall-clock time
is quoted for it.)

District boundaries follow 2020 census blocks, so no GEOID prefix relates a
district to a county, a tract or a block group — only `substr(geoid, 1, 2)`
to its state works, and everything finer is a spatial question. Three
counties intersect CA-12 and one of them is 99.96% of it: a bare
`ST_Intersects` list is a membership set with slivers in it, and the area
share is what tells you which rows are real. For a population-weighted
allocation rather than a membership list, use the Census Bureau's own
[relationship files](https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html)
and say which one. The `bbox`-overlap condition in the `ON` clause is the
cheap candidate filter; the same pattern at other geographies is in
[`zctas/AGENTS.md`](../../zctas/AGENTS.md).

### Related recipes elsewhere

- The state figures these districts are compared against, and the quadrature
  rule for summing: [`states/AGENTS.md`](../../states/AGENTS.md).
- Looking inside a district: [`tracts/AGENTS.md`](../../tracts/AGENTS.md) and
  [`block-groups/AGENTS.md`](../../block-groups/AGENTS.md), related spatially.
- One theme at a time on these same 441 districts, each with 4–5 more tested
  recipes and its own measured class breaks:
  [`cd-income`](../cd-income/AGENTS.md), [`cd-people`](../cd-people/AGENTS.md),
  [`cd-housing`](../cd-housing/AGENTS.md),
  [`cd-connectivity`](../cd-connectivity/AGENTS.md),
  [`cd-wellbeing`](../cd-wellbeing/AGENTS.md); what the six share is in the
  [group guide](../AGENTS.md).
- 2020 Decennial block counts, the geography districts are drawn from:
  [`blocks/AGENTS.md`](../../blocks/AGENTS.md).

Statistics come from the GeoParquet. The district PMTiles archive is real
polygons at every zoom (z0–z10) and needs no coarser-geography band at coarse
zooms. It carries the `*_cv` columns recipe 4 reads, but no `*_moe` columns —
and it is a map artifact either way: query the GeoParquet for numbers.
