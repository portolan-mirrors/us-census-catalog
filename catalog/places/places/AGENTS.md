# Agent guide — All Indicators (Places & CDPs)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Every indicator in this catalog's ACS column set, in one table, for every place the Census Bureau delineates: income and poverty, age and race and education, housing cost and tenure, vehicles and commuting and internet access, health insurance and disability and nativity, and median household income by race and ethnicity.

"Place" means two things at once: incorporated places (cities, towns, villages, boroughs) and [census designated places](https://www.census.gov/programs-surveys/bas/information/cdp.html) — the Bureau's statistical stand-ins for unincorporated communities. The `name` column's `NAMELSAD` descriptor says which: "Los Angeles city", "Brentwood CDP". Places do **not** tile the country: the land between them is simply not in this file, so place rows do not sum to a county or a state.

**32,612 rows**, one per place, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

## The full table, and the five themed cuts beside it

This collection is the **sixth sibling** of the [`places` group](../AGENTS.md).
The other five are themed cuts of exactly these rows, 23 to 34 columns each
instead of 112:

| sibling | theme | headline columns |
|---|---|---|
| [place-income](../place-income/collection.json) ([agent guide](../place-income/AGENTS.md)) | Income & Poverty | `median_hh_income`, `per_capita_income`, `pct_below_poverty`, `pct_snap`, `pct_unemployed` |
| [place-people](../place-people/collection.json) ([agent guide](../place-people/AGENTS.md)) | People & Education | `median_age`, `pct_under_18`, `pct_65_plus`, the four non-Hispanic race shares, `pct_hispanic`, `pct_bachelors_plus` |
| [place-housing](../place-housing/collection.json) ([agent guide](../place-housing/AGENTS.md)) | Housing & Rent | `housing_units`, `households`, `pct_owner_occupied`, `median_gross_rent`, `median_home_value`, `pct_rent_burdened` |
| [place-connectivity](../place-connectivity/collection.json) ([agent guide](../place-connectivity/AGENTS.md)) | Commuting & Connectivity | `hh_no_vehicle`, the B08301 commute-mode shares, `pct_commute_45min_plus`, `pct_no_internet`, `pct_no_computer` |
| [place-wellbeing](../place-wellbeing/collection.json) ([agent guide](../place-wellbeing/AGENTS.md)) | Health, Disability & Income by Race | `pct_uninsured`, `pct_with_disability`, `pct_foreign_born`, `group_quarters_pop`, `median_hh_income_{black,white_nh,asian,hispanic}`, `pct_below_poverty_black` |

All six hold the same 32,612 `geoid` values with the same geometry — measured,
in [`../AGENTS.md`](../AGENTS.md) — so `JOIN … USING (geoid)` across any of
them is 1:1 and loses nothing. Each themed file carries the same seven context
columns (`geoid`, `name`, `state`, `population`, `population_moe`,
`aland_sqkm`, `pop_density`) plus `geometry` and `bbox`, so a single-theme
question never needs a join.

**Use this file when the question crosses themes** — rent against income
against car ownership in one pass, or a profile of one named place — and a
themed sibling when it does not. The wide table is 32.9 MB on disk against
27.7–28.2 MB for each themed cut, so for a one-theme query over the network
the themed file is the cheaper read; for a three-theme query this one is,
because the alternative is three downloads and two joins. Both answers are
identical: the themed files were cut from these columns.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.pmtiles`, layer `places`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/places/collection.json` — carries a full description for every column
- **Group sub-catalog** (all six siblings): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/catalog.json`

Note the asymmetry: this collection's STAC metadata, README and styles live in
the `places/places/` directory beside the five themed children, but its **data
files stay one directory up**, at `places/places.parquet` and
`places/places.pmtiles`, where they have always been. Those two URLs are
unchanged by the restructure; every link in this file that went stale was a
metadata link, not a data link.

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

`geoid` is 7 characters — state FIPS (2) + place FIPS (5) — and `substr(geoid, 1, 2)` is the only prefix join it supports, to [`states`](../../states/states/collection.json). Places nest in states but not in counties (a place can straddle a county line) and a place is not an aggregate of tracts or block groups, so there is no prefix path to the finer collections.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 7-character place GEOID: state FIPS 2 + place FIPS 5, e.g. `0644000` for Los Angeles city. |
| `name` | string | `NAMELSAD`, `STATE_NAME` from the 2024 cartographic boundary place file — "Los Angeles city, California", "Brentwood CDP, New York". The descriptor in the name says whether the place is a city, town, village, borough or CDP. |
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

- **Places are not a partition of the country.** Do not sum place rows to a state total, and do not read "the land outside places" out of this file — it is absent, not zero.
- **Most rows are small.** The file runs from New York city (8,483,844 people) to villages of a few dozen, so an unweighted mean or median over places describes small places, not the country. Filter on `population` first.
- **Louisville is `2148006`,** the consolidated Louisville/Jefferson County metro government (balance). `2148000` "Louisville city" is still in the boundary file and has no ACS row, so it publishes with NULL values — the same trap exists for other consolidated city-counties.
- **282 places carry geometry and no ACS data**: 279 in the island areas (MP 135, AS 77, GU 57, VI 10), Brentwood CDP and Wyandanch CDP in Suffolk County, New York, and Louisville city. Every column is NULL on those rows.
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
- **The four race shares this file carries are all non-Hispanic** — `pct_white_nh`, `pct_black`, `pct_native`, `pct_asian` — drawn from B03002's "Not Hispanic or Latino" branch, so they and `pct_hispanic` are mutually exclusive and do not double-count. They do not sum to 100: B03002's non-Hispanic "Native Hawaiian and Other Pacific Islander", "Some other race" and "Two or more races" branches are not published here.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.86% of places — the 282 rows with 2024 boundaries and no ACS tabulation. Every other column is NULL on at least those rows. |
| `median_hh_income` | NULL on 12.71% of places; the suppression is concentrated in small places. |
| `median_gross_rent` | NULL on 31.32% of places — a third of them have too few cash-renting households for a median. |
| `median_home_value` | NULL on 12.78% of places. |
| `pct_rent_burdened` | NULL on 14.60% of places, where the computable-ratio denominator came out at or below 0. |
| `median_hh_income_black` | NULL on 79.24% of places. |
| `median_hh_income_white_nh` | NULL on 17.62% of places. |
| `median_hh_income_asian` | NULL on 85.80% of places — the sparsest column in the catalog. |
| `median_hh_income_hispanic` | NULL on 69.35% of places. |
| `pct_below_poverty_black` | NULL on 46.72% of places. |

Row count is the 2024 cartographic boundary place file's own feature count, 32,612. For scale, the Census Bureau's [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html) give 19,734 incorporated places and 12,454 census designated places (32,188) for the 2020 vintage; the 2024 vintage is four years of incorporations, dissolutions and CDP re-delineations later. The ACS tabulates 32,330 places, all of which matched a polygon.

Spot-checked against data.census.gov: Los Angeles city population 3,857,263 and median home value $921,200; New York city population 8,483,844.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: below z6 you are looking at counties, not places. The values there are the Census Bureau's own estimates for those geographies, not an aggregation of this file, and `*_moe` columns are not in the tiles. Statistics come from the GeoParquet.

## Related collections

- The five themed siblings — same 32,612 rows, same geometry, a slice of these columns each: [`place-income`](../place-income/collection.json), [`place-people`](../place-people/collection.json), [`place-housing`](../place-housing/collection.json), [`place-connectivity`](../place-connectivity/collection.json), [`place-wellbeing`](../place-wellbeing/collection.json). Join 1:1 on `geoid`.
- [`places/` group guide](../AGENTS.md) — what the six collections share: the geography, the name-matching recipes, and when to step up or down a level.
- [`zctas`](../../zctas/zctas/collection.json) and [`congressional-districts`](../../congressional-districts/congressional-districts/collection.json) — the same 112 columns at the catalog's other non-nesting geographies.
- [`counties`](../../counties/counties/collection.json) and [`states`](../../states/states/collection.json) — the same 112 columns at geographies that do tile the country, which is what you want for a total.
- [`block-groups/`](../../block-groups/catalog.json) and [`tracts/`](../../tracts/catalog.json) — the same indicators split into themed chunks, and the geographies to use inside a city.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run against the published URLs with DuckDB 1.4.1
immediately before it was written down, and its real output is quoted beside
it, wall-clock time included. The wide table's data URL did not move in the
restructure, so these timings still describe the file these queries name; the
themed siblings' guides quote file sizes instead of timings, because those
files had not yet reached the mirror when their queries were run.

Remember the two rules this geography enforces: **places do not tile the
country** (never sum them to a state or national total) and **most rows are
tiny** (always filter on `population` before an average or a ranking).

### 1. The biggest places, and one state's

```sql
INSTALL httpfs; LOAD httpfs;
SELECT geoid, name, population, median_hh_income::int AS income, pct_rent_burdened
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet'
ORDER BY population DESC NULLS LAST LIMIT 5;
```

→ `3651000 | New York city, New York | 8483844 | 80483 | 52.41`, `0644000 |
Los Angeles city, California | 3857263 | 81939 | 59.25`, `1714000 | Chicago
city, Illinois | 2711226 | 77902 | 48.35`, `4835000 | Houston city, Texas |
2328253 | 64813 | 54.06`, `0455000 | Phoenix city, Arizona | 1642323 | 81332 |
51.76`. 6.2 s. `NULLS LAST` is required: 282 places have boundaries and no ACS
data, and without it they sort first on a `DESC` ordering.

One state, with a size gate:

```sql
LOAD httpfs;
SELECT geoid, name, population, median_gross_rent::int AS rent
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet'
WHERE state = 'TX' AND population > 100000
ORDER BY median_gross_rent DESC NULLS LAST LIMIT 5;
```

→ `4827684 | Frisco city, Texas | 219304 | 2014`, `4870808 | Sugar Land city,
Texas | 110016 | 1957`, `4801924 | Allen city, Texas | 110265 | 1932`,
`4845744 | McKinney city, Texas | 210600 | 1901`, `4856348 | Pearland city,
Texas | 127514 | 1860`. 3.5 s. Drop `population > 100000` and this becomes a
list of small suburbs with wide margins; the gate is the query.

### 2. The most rent-burdened large cities (`*_cv`)

```sql
LOAD httpfs;
SELECT geoid, name, population, pct_rent_burdened,
       pct_rent_burdened_moe AS moe, round(pct_rent_burdened_cv, 3) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet'
WHERE population > 100000 AND pct_rent_burdened_cv < 0.05
ORDER BY pct_rent_burdened DESC LIMIT 5;
```

→ `0646842 | Menifee city, California | 110305 | 70.63 | 5.26 | 0.045`,
`0621712 | El Cajon city, California | 104449 | 70.1 | 4.31 | 0.037`,
`1225175 | Gainesville city, Florida | 145702 | 68.04 | 3.54 | 0.032`,
`1245060 | Miami Gardens city, Florida | 113177 | 67.96 | 5.43 | 0.049`,
`1232000 | Hollywood city, Florida | 155082 | 67.67 | 4.7 | 0.042`. 4.6 s.

Seven in ten renter households paying 30% or more of income on rent, with
margins of 4–5 points, in cities of 100,000+. The denominator is renter
households whose rent-to-income ratio the Bureau could compute (B25070 minus
its "Not computed" line), not all households — quote it that way.

### 3. Every city against its own state (GEOID prefix join)

```sql
LOAD httpfs;
SELECT p.name, p.population, p.median_hh_income::int AS place_income,
       s.median_hh_income::int AS state_income,
       round(p.median_hh_income::double / s.median_hh_income, 2) AS ratio
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet' p
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet' s
  ON substr(p.geoid, 1, 2) = s.geoid
WHERE p.population > 250000 AND p.median_hh_income_cv < 0.05
ORDER BY ratio DESC LIMIT 5;
```

→ `Gilbert town, Arizona | 280262 | 122551 | 79964 | 1.53`, `San Jose city,
California | 990138 | 146427 | 99122 | 1.48`, `Plano city, Texas | 290594 |
112253 | 78476 | 1.43`, `San Francisco city, California | 830235 | 140970 |
99122 | 1.42`, `Irvine city, California | 311690 | 136719 | 99122 | 1.38`.
5.1 s.

A place GEOID is state FIPS (2) + place FIPS (5), so `substr(geoid, 1, 2)` is
the state's `geoid` — the only prefix join this collection supports. There is
no county component in the GEOID at all and therefore **no**
`substr(geoid, 1, 5)` route to [`counties`](../../counties/counties/collection.json): that
relationship is spatial, and it is one-to-many. Measured, with the
`bbox`-overlap + `ST_Intersects` pattern from
[`zctas/AGENTS.md`](../../zctas/AGENTS.md), Houston city (`4835000`) intersects
five counties — Harris, Fort Bend, Montgomery, Brazoria and Waller.

### 4. The consolidated-city trap, in one query

```sql
LOAD httpfs;
SELECT geoid, name, population, median_hh_income::int AS income
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet'
WHERE geoid IN ('2148000', '2148006');
```

→ `2148006 | Louisville/Jefferson County metro government (balance), Kentucky
| 631818 | 66849` and `2148000 | Louisville city, Kentucky | NULL | NULL`.
2.5 s.

Searching this file for "Louisville city" finds the row with no data. The
consolidated metro government is the entity the ACS tabulates, and it is
`2148006`. Match places by GEOID where you can; where you must match by name,
check for a NULL `population` and look for a sibling row before concluding a
city has no data. The same shape of trap exists for other consolidated
city-counties, and for the 279 island-area places and 2 Suffolk County CDPs
that make up the rest of the 282 data-free rows.

### Related recipes elsewhere

- The 11 Louisvilles, the six-way row-count check and the one-row cross-theme
  profile: [`places/AGENTS.md`](../AGENTS.md).
- The population floor measured by size band, the margin-overlap test between
  two small places, and the state prefix join:
  [`places/place-income/AGENTS.md`](../place-income/AGENTS.md).
- Finding a place by name — the 23 Springfields — and what an ungated ranking
  returns: [`places/place-people/AGENTS.md`](../place-people/AGENTS.md).
- The rent median's 31.32% hole by place size, and why a resort town reports
  87% vacancy: [`places/place-housing/AGENTS.md`](../place-housing/AGENTS.md).
- Why a `_cv` gate drops all 22,895 zero-transit places, and where a transit
  question belongs:
  [`places/place-connectivity/AGENTS.md`](../place-connectivity/AGENTS.md).
- Income by race published on 14.2% of places (96.0% above 50,000), and the
  campus CDPs with zero households:
  [`places/place-wellbeing/AGENTS.md`](../place-wellbeing/AGENTS.md).
- The most rent-burdened large cities with each city's state rate beside it:
  [`catalog/AGENTS.md`](../../AGENTS.md).
- Looking inside a city — the geographies that do tile it:
  [`tracts/AGENTS.md`](../../tracts/AGENTS.md),
  [`block-groups/AGENTS.md`](../../block-groups/AGENTS.md).
- For a total over an area, use geographies that tile the country:
  [`counties/AGENTS.md`](../../counties/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and its z0–z5 features are counties rather than places, so nothing
above can be reproduced from tiles.
