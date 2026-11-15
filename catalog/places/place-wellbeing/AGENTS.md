# Agent guide — Health, Disability & Income by Race (Places & CDPs)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Health coverage, disability, nativity and income by race — tables the Census Bureau does not publish for block groups at all. The uninsured share and the share with a disability ([B27001](https://data.census.gov/table/ACSDT5Y2024.B27001), [B18101](https://data.census.gov/table/ACSDT5Y2024.B18101)), the foreign-born share ([B05002](https://data.census.gov/table/ACSDT5Y2024.B05002)), the group-quarters population ([B26001](https://data.census.gov/table/ACSDT5Y2024.B26001)), median household income for Black, non-Hispanic White, Asian and Hispanic householders ([B19013B](https://data.census.gov/table/ACSDT5Y2024.B19013B), [B19013H](https://data.census.gov/table/ACSDT5Y2024.B19013H), [B19013D](https://data.census.gov/table/ACSDT5Y2024.B19013D), [B19013I](https://data.census.gov/table/ACSDT5Y2024.B19013I)), and the poverty rate of the Black alone population ([B17020B](https://data.census.gov/table/ACSDT5Y2024.B17020B)).

**32,612 rows**, one per place, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

**In this collection the NULLs are the subject.** Across all 32,612 places the four race-iteration medians are published on **82.38% / 30.65% / 20.76% / 14.20%** of rows (white_nh / hispanic / black / asian, measured) — and across the 883 places of 50,000 people or more, on **99.77% / 99.89% / 96.26% / 96.04%** (measured, recipe 1). The sparsity is almost entirely a fact about place size. `pct_uninsured` tells the same story from the other side: it is published nearly everywhere and has a **median coefficient of variation of 0.500**, the worst in the catalog outside block groups, with only 6.4% of places reaching the 0.12 "reliable" line.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.pmtiles`, layer `place-wellbeing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/collection.json` — carries a full description for every column

This is a themed cut of the wide 112-column place table, which is published as the sixth sibling in this group: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet` ([agent guide](../places/AGENTS.md)). Same 32,612 rows, same geometry, every column below included — reach for it when a question crosses themes, and for this one when it does not.

## Source tables

| table | title | universe |
|---|---|---|
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B05002](https://data.census.gov/table/ACSDT5Y2024.B05002) | Place of Birth by Nativity and Citizenship Status | Total population |
| [B17020B](https://data.census.gov/table/ACSDT5Y2024.B17020B) | Poverty Status in the Past 12 Months by Age (Black or African American Alone) | Black or African American alone population for whom poverty status is determined |
| [B18101](https://data.census.gov/table/ACSDT5Y2024.B18101) | Sex by Age by Disability Status | Civilian noninstitutionalized population |
| [B19013B](https://data.census.gov/table/ACSDT5Y2024.B19013B) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (Black or African American Alone Householder) | Households with a householder who is Black or African American alone |
| [B19013D](https://data.census.gov/table/ACSDT5Y2024.B19013D) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (Asian Alone Householder) | Households with a householder who is Asian alone |
| [B19013H](https://data.census.gov/table/ACSDT5Y2024.B19013H) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (White Alone, Not Hispanic or Latino Householder) | Households with a householder who is White alone, not Hispanic or Latino |
| [B19013I](https://data.census.gov/table/ACSDT5Y2024.B19013I) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (Hispanic or Latino Householder) | Households with a householder who is Hispanic or Latino |
| [B26001](https://data.census.gov/table/ACSDT5Y2024.B26001) | Group Quarters Population | Population in group quarters |
| [B27001](https://data.census.gov/table/ACSDT5Y2024.B27001) | Health Insurance Coverage Status by Sex by Age | Civilian noninstitutionalized population |

## Schema

`geoid` is 7 characters — state FIPS (2) + place FIPS (5) — and `substr(geoid, 1, 2)` is the only prefix join it supports, to [`states/state-wellbeing`](../../states/state-wellbeing/collection.json). Places nest in states but not in counties (a place can straddle a county line) and a place is not an aggregate of tracts or block groups, so there is no prefix path to the finer collections. The five themed siblings and the wide table all carry the same 32,612 `geoid` values, so `JOIN … USING (geoid)` is 1:1.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 7-character place GEOID: state FIPS 2 + place FIPS 5, e.g. `0644000` for Los Angeles city. |
| `name` | string | `NAMELSAD`, `STATE_NAME` from the 2024 cartographic boundary place file — "Los Angeles city, California", "Brentwood CDP, New York". The descriptor in the name says whether the place is a city, town, village, borough or CDP. |
| `state` | string | Two-letter USPS state or territory code. |
| `population` | int64 | Total population. |
| `population_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `population`. |
| `aland_sqkm` | double | Land area in km² (water excluded), 3 decimals. |
| `pop_density` | double | People per square kilometre of land area, rounded to 1 decimal: `population / aland_sqkm`. |
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

- **A blank race-iteration median means "not published here", never "low
  income".** All four are NULL wherever too few households of that
  householder's race live in the place for the Census Bureau to publish a
  median, which at this geography is most of the file: `median_hh_income_asian`
  is NULL on **85.80%** of places, `median_hh_income_black` on **79.24%**,
  `median_hh_income_hispanic` on **69.35%**, `median_hh_income_white_nh` on
  **17.62%**. A national place-level map of any of them is a map of where the
  group lives at least as much as of its income. Quote the denominator with
  every gap you report.
- **The race-iteration medians are classified by the householder's race**, not
  by every member's, and each has its own universe (households with a
  householder who is …). They are not shares of a common total, they cannot be
  averaged together, and a place's overall `median_hh_income` in
  [`place-income`](../place-income/collection.json) can sit **below** every
  race-specific median it contains — three medians, three universes, and a
  median is not a weighted average of sub-medians.
- **`pct_uninsured` and `pct_with_disability` are shares of the civilian
  noninstitutionalized population**, not of everyone: people on active duty and
  people in institutions are outside the universe. At place level that interacts
  badly with `group_quarters_pop` — a place that is mostly a prison or a
  dormitory has most of its residents outside both denominators.
- **`pct_below_poverty_black` has a race-specific denominator** (the Black
  alone population for whom poverty status is determined), so it is not
  comparable to `pct_below_poverty`'s denominator in
  [`place-income`](../place-income/collection.json). NULL on 46.72% of places:
  no Black-alone population for whom poverty status is determined, so no rate.
- **`group_quarters_pop` can equal `population`.** Measured, three places are
  100.0% group quarters — `3671620` Stony Brook University CDP, New York
  (9,530 people), `2875520` University CDP, Mississippi (5,315) and `3606644`
  Binghamton University CDP, New York (7,449) — and each has **0 households**
  and NULL on every household-denominated column in the group (recipe 4).
  Those NULLs are structural, not suppression. A large
  `group_quarters_pop` beside a small household count usually explains an odd
  median before anything else does.
- **`pct_foreign_born` counts anyone not a U.S. citizen at birth**, naturalized
  citizens included, so it is a nativity measure and not a citizenship or
  immigration-status measure.
- **Places are not a partition of the country.** Do not sum
  `group_quarters_pop` across place rows to get a state or national count —
  the land between places is absent from this file, not empty. For a total,
  use
  [`counties/county-wellbeing`](../../counties/county-wellbeing/collection.json)
  or
  [`states/state-wellbeing`](../../states/state-wellbeing/collection.json).
- **Most rows are small, and here that is the whole story.** 16,463 places
  have under 1,000 people and 883 have 50,000 or more (measured). The
  race-iteration medians go from 14.2%–82.4% published across all places to
  96.0%–99.9% published across the 883 largest (recipe 1). A population floor
  is how this collection becomes usable.
- **Louisville is `2148006`,** the consolidated Louisville/Jefferson County
  metro government (balance). `2148000` "Louisville city" is still in the
  boundary file and has no ACS row, so it publishes with NULL values. The
  worked case is in [`../AGENTS.md`](../AGENTS.md).
- **282 places carry geometry and no ACS data**: 279 in the island areas
  (MP 135, AS 77, GU 57, VI 10, measured), Brentwood CDP and Wyandanch CDP in
  Suffolk County, New York, and Louisville city. `ORDER BY … DESC` needs
  `NULLS LAST`.
- **Every estimate has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. To compare two places, check whether
  their margins overlap before calling a difference real. To sum estimates
  across geographies, add the margins in quadrature (`sqrt(sum(moe*moe))`).
  **Never sum or average a median**: a median of a region is not derivable
  from the medians of its parts.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate` —
  here every column except `pct_foreign_born` and `group_quarters_pop`. Rule
  of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. Measured place-level medians: `pct_uninsured` **0.500**,
  `pct_with_disability` 0.223, `median_hh_income_white_nh` 0.148,
  `median_hh_income_black` 0.217, `median_hh_income_asian` 0.210,
  `median_hh_income_hispanic` 0.209, `pct_below_poverty_black` 0.445. Only
  `pct_with_disability` and the four medians are usable without a hard gate,
  and none of them is reliable by default.
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale, and at this geography a percentage's margin can
  exceed 100 points — a flag to drop the row, not a value.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area, and neither number is wrong.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population`, `group_quarters_pop` | NULL on 0.86% of places — the 282 rows with 2024 boundaries and no ACS tabulation. Every other column is NULL on at least those rows. |
| `pct_uninsured`, `pct_with_disability` | NULL on 2.47% of places each (measured) — no civilian noninstitutionalized population, so no share. Not published for block groups at all. |
| `pct_foreign_born` | NULL on 2.43% of places (measured). |
| `median_hh_income_white_nh` | NULL on 17.62% of places (10.04% of tracts, 2.38% of counties) — the least sparse of the four, which is itself a fact about the distribution of the population. |
| `median_hh_income_hispanic` | **NULL on 69.35% of places** (44.43% of tracts, 19.60% of counties). |
| `median_hh_income_black` | **NULL on 79.24% of places** (61.43% of tracts, 39.47% of counties). |
| `median_hh_income_asian` | **NULL on 85.80% of places** (71.27% of tracts, 53.63% of counties) — the sparsest column in the catalog. |
| `pct_below_poverty_black` | NULL on 46.72% of places (12.84% of tracts, 5.87% of counties). |

Unreliability compounds the sparsity. Measured at place level, among the rows that publish a `_cv`:

| column | median CV | share over 0.40 |
|---|---|---|
| `pct_uninsured` | 0.500 | 58.1% |
| `pct_below_poverty_black` | 0.445 | 55.0% |
| `pct_with_disability` | 0.223 | — |
| `median_hh_income_black` | 0.217 | — |
| `median_hh_income_asian` | 0.210 | — |
| `median_hh_income_hispanic` | 0.209 | — |
| `median_hh_income_white_nh` | 0.148 | — |

`pct_uninsured` is the sharpest case in the catalog of a column that is nearly
always *published* and nearly never *reliable*: 27,976 places carry a CV, the
median is exactly 0.500, and only **6.4%** are under 0.12 (measured, recipe 2).
Treat the column as mappable only with `_cv` greying and a population floor.

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 279 places here, plus 4 states, 13 county equivalents, 126 tracts and 405 block groups elsewhere in the catalog.

Three more places have boundaries and no ACS row: `3608026` Brentwood CDP and `3683294` Wyandanch CDP, left without an ACS match by the 2024 re-delineation of Suffolk County, New York, and `2148000` Louisville city, whose ACS tabulation is the consolidated `2148006` metro government. Running the other way, every one of the 32,330 ACS-tabulated places matched a polygon.

Row count is the 2024 cartographic boundary place file's own feature count, 32,612. For scale, the Census Bureau's [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html) give 19,734 incorporated places and 12,454 census designated places (32,188) for the 2020 vintage; the 2024 vintage is four years of incorporations, dissolutions and CDP re-delineations later.

PMTiles coarse zooms are a different census geography from this collection's: z0–z5 are **counties**, carrying the Census Bureau's own county estimates for these same columns, and z6–z12 are the places themselves. The county band is national orientation, not a roll-up of this file — places do not tile a county. `*_moe` columns are not in the tiles; `*_cv` columns are. A place-level map of `median_hh_income_asian` is drawn on 14.20% of the rows, so style the NULLs as an explicit "not published" class; letting them fall through to the background reads as a value. Statistics come from the GeoParquet.

## Related collections

- [`places/place-income`](../place-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1 — the overall `median_hh_income` the race-specific medians sit beside, and `pct_below_poverty`'s all-population denominator.
- [`places/place-people`](../place-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1 — the race *shares*, which is a different question from income by race.
- [`places/place-housing`](../place-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1 — `households`, which is how to spot a group-quarters place.
- [`places/place-connectivity`](../place-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`places/places`](../places/collection.json) — the wide 112-column place table, the sixth sibling: every column of all five themes in one file.
- [`counties/county-wellbeing`](../../counties/county-wellbeing/collection.json) and [`states/state-wellbeing`](../../states/state-wellbeing/collection.json) — the same theme at geographies that **do** tile the country, and where the race-iteration medians are published far more often (`median_hh_income_asian` NULL on 53.63% of counties against 85.80% of places).
- [`tracts/tract-wellbeing`](../../tracts/tract-wellbeing/collection.json) — the same theme inside a city, at a geography that tiles it. **There is no block-group twin**: the Census Bureau does not publish these tables below tract.
- [`zctas/zcta-wellbeing`](../../zctas/zcta-wellbeing/collection.json) and [`congressional-districts/cd-wellbeing`](../../congressional-districts/cd-wellbeing/collection.json) — the same theme at the catalog's other non-nesting geographies.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, including group-quarters counts from a different survey and vintage, with no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted. For
scale instead: the file is **27.8 MB** over **32,612 rows**.

In this collection the NULLs are the subject, not an inconvenience: a query
that ignores them produces a confident answer about where a population *lives*
while claiming to be about its income.

### 1. How often is each race-iteration median published at all?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT round(100.0*count(median_hh_income_white_nh)/count(*), 2) AS pub_white_nh,
       round(100.0*count(median_hh_income_hispanic)/count(*), 2) AS pub_hispanic,
       round(100.0*count(median_hh_income_black)/count(*), 2)    AS pub_black,
       round(100.0*count(median_hh_income_asian)/count(*), 2)    AS pub_asian
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.parquet';
```

→ `82.38 | 30.65 | 20.76 | 14.2`.

And the same four columns over the places most people mean by "a city":

```sql
LOAD httpfs;
SELECT count(*) AS places,
       round(100.0*count(median_hh_income_white_nh)/count(*), 2) AS pub_white_nh,
       round(100.0*count(median_hh_income_hispanic)/count(*), 2) AS pub_hispanic,
       round(100.0*count(median_hh_income_black)/count(*), 2)    AS pub_black,
       round(100.0*count(median_hh_income_asian)/count(*), 2)    AS pub_asian
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.parquet'
WHERE population >= 50000;
```

→ `883 | 99.77 | 99.89 | 96.26 | 96.04`.

A national place-level map of `median_hh_income_asian` is drawn on **14.2%**
of the rows. The same column across the 883 places of 50,000 or more is drawn
on **96.04%** of them. Both numbers are about this file; which one you are
entitled to depends entirely on the population floor in your `WHERE` clause,
and the honest sentence names it: "in the 848 of 883 places over 50,000 where
the Asian-householder median is published" is true, "in American cities" is
not. Run this before mapping or ranking any of the four columns.

### 2. `pct_uninsured`: nearly always published, nearly never reliable

```sql
LOAD httpfs;
SELECT count(pct_uninsured_cv)                                  AS n,
       round(quantile_cont(pct_uninsured_cv, 0.5), 3)           AS median_cv,
       round(100.0*count(*) FILTER (WHERE pct_uninsured_cv > 0.40)
             / count(pct_uninsured_cv), 1)                      AS pct_unreliable,
       round(100.0*count(*) FILTER (WHERE pct_uninsured_cv < 0.12)
             / count(pct_uninsured_cv), 1)                      AS pct_reliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.parquet';
```

→ `27976 | 0.5 | 58.1 | 6.4`.

The median place's uninsured share has a CV of exactly **0.500** — the
estimate's own standard error is half the estimate. Fifty-eight percent of
places are over the 0.40 unreliable line and **6.4%** clear the 0.12 reliable
line. The column is NULL on only 2.47% of places, so suppression is not
protecting you here; the `_cv` gate is the only thing that is.

With both gates on, the answer is solid:

```sql
LOAD httpfs;
SELECT geoid, name, population, pct_uninsured, pct_uninsured_moe AS moe,
       round(pct_uninsured_cv, 3) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.parquet'
WHERE population > 25000 AND pct_uninsured_cv < 0.12
ORDER BY pct_uninsured DESC LIMIT 5;
```

→ `4868636 | Socorro city, Texas | 37123 | 32.79 | 3.27 | 0.061`, `1233250 |
Immokalee CDP, Florida | 26361 | 32.73 | 1.86 | 0.035`, `4805372 | Balch
Springs city, Texas | 27255 | 31.15 | 3.97 | 0.077`, `4877728 | West Odessa
CDP, Texas | 32594 | 30.27 | 3.34 | 0.067`, `4858820 | Port Arthur city,
Texas | 55828 | 29.47 | 1.96 | 0.04`.

Two of the five are CDPs, so a query restricted to incorporated cities would
drop Immokalee and West Odessa. Remember the universe: this is a share of the
**civilian noninstitutionalized** population, so active-duty personnel and
people in institutions are outside the denominator entirely.

### 3. Income by race against income overall (sibling join)

```sql
LOAD httpfs;
SELECT w.geoid, w.name, i.median_hh_income::int           AS overall,
       w.median_hh_income_white_nh::int                   AS white_nh,
       w.median_hh_income_black::int                      AS black,
       round(w.median_hh_income_black::double / w.median_hh_income_white_nh, 2) AS black_to_white
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.parquet' w
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet' i
  USING (geoid)
WHERE w.population > 100000
  AND w.median_hh_income_black_cv    < 0.10
  AND w.median_hh_income_white_nh_cv < 0.10
ORDER BY black_to_white LIMIT 5;
```

→ `0667000 | San Francisco city, California | 140970 | 178859 | 54384 | 0.3`,
`1245000 | Miami city, Florida | 62462 | 124330 | 41431 | 0.33`, `0606000 |
Berkeley city, California | 108092 | 150931 | 53563 | 0.35`, `1150000 |
Washington city, District of Columbia | 109870 | 170201 | 60764 | 0.36`,
`1304000 | Atlanta city, Georgia | 85652 | 135168 | 51197 | 0.38`.

The join is 1:1 on `geoid` — all six place collections hold the same 32,612
rows. Both `_cv` gates are load-bearing: these medians rest on small samples
and without the filter the ratio column fills with noise. Look at Miami's
`overall` column — $62,462, **below both** of the race-specific medians beside
it. That is not an error: the three medians have three different universes
(all households; non-Hispanic White householders; Black householders) and a
median is not a weighted average of sub-medians. The column this ranking
leaves out is the one that explains it: Miami is 71.49% Hispanic and its
Hispanic-householder median is $57,176 — below the overall $62,462 — and those
households are in neither of the two columns beside it (measured). Never
reconstruct an overall median from race-specific ones, and never read a
two-group ratio as the whole distribution.

### 4. The place that is entirely a dormitory (`group_quarters_pop`)

```sql
LOAD httpfs;
SELECT geoid, name, population, group_quarters_pop,
       round(100.0*group_quarters_pop/population, 1) AS pct_gq
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.parquet'
WHERE population > 5000 AND group_quarters_pop IS NOT NULL
ORDER BY pct_gq DESC LIMIT 5;
```

→ `3671620 | Stony Brook University CDP, New York | 9530 | 9530 | 100.0`,
`2875520 | University CDP, Mississippi | 5315 | 5315 | 100.0`, `3606644 |
Binghamton University CDP, New York | 7449 | 7449 | 100.0`, `3465249 | Rutgers
University-Busch Campus CDP, New Jersey | 5920 | 5843 | 98.7`, `4515040 |
Clemson University CDP, South Carolina | 7015 | 6920 | 98.6`.

Now what that does to every household statistic in the group:

```sql
LOAD httpfs;
SELECT w.geoid, w.name, w.population, w.group_quarters_pop,
       i.median_hh_income::int AS income, h.households, h.median_gross_rent::int AS rent
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.parquet' w
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet' i USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.parquet' h USING (geoid)
WHERE w.geoid IN ('3671620', '2875520', '3606644');
```

→ `3671620 | Stony Brook University CDP, New York | 9530 | 9530 | NULL | 0 |
NULL`, `2875520 | University CDP, Mississippi | 5315 | 5315 | NULL | 0 | NULL`,
`3606644 | Binghamton University CDP, New York | 7449 | 7449 | NULL | 0 |
NULL`.

**Zero households, 9,530 people.** Every median and every household share on
those rows is NULL because the universe is empty, not because the Census
Bureau suppressed anything — and a population floor alone does not exclude
them, because 9,530 people clears most floors. When a place's medians are all
NULL and its population is healthy, read `group_quarters_pop` and `households`
before concluding the data is broken. These rows are also why
`pct_uninsured`'s and `pct_with_disability`'s "civilian noninstitutionalized"
universe matters: a campus CDP's residents are largely outside it.

### 5. Disability and insurance together, reliability-gated

```sql
LOAD httpfs;
SELECT geoid, name, population, pct_with_disability,
       round(pct_with_disability_cv, 2) AS dis_cv,
       pct_uninsured, round(pct_uninsured_cv, 2) AS unins_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.parquet'
WHERE population > 25000
  AND pct_with_disability_cv < 0.10 AND pct_uninsured_cv < 0.20
ORDER BY pct_with_disability DESC LIMIT 5;
```

→ `0470320 | Sun City CDP, Arizona | 37486 | 32.89 | 0.04 | 3.19 | 0.12`,
`7210334 | Caguas zona urbana, Puerto Rico | 72922 | 28.25 | 0.02 | 6.06 |
0.08`, `7250260 | Mansión del Mar comunidad, Puerto Rico | 25510 | 27.53 |
0.03 | 5.38 | 0.12`, `2135866 | Henderson city, Kentucky | 27852 | 27.2 |
0.05 | 5.84 | 0.11`, `7263820 | Ponce zona urbana, Puerto Rico | 107805 |
26.97 | 0.02 | 4.03 | 0.07`.

Note the **two different `_cv` thresholds**: 0.10 on disability and 0.20 on
insurance, because at place level the two columns have very different
precision (median CV 0.223 against 0.500). Forcing one threshold on both drops
rows for the wrong reason. The two columns also move independently — Sun City
pairs the highest disability share here with a 3.19% uninsured share, because
it is a retirement CDP and nearly everyone in it has Medicare. Reading one as
a proxy for the other would be wrong in both directions. Four of these five
rows are CDPs, `comunidad`s or `zona urbana`s, none of them a "city".

### Related recipes elsewhere

- The 11 Louisvilles, the consolidated-city trap, and the one-row cross-theme
  profile: [`places/AGENTS.md`](../AGENTS.md).
- The same columns beside all 107 others, with wall-clock timings against the
  mirror: [`places/places/AGENTS.md`](../places/AGENTS.md).
- Overall income, the population-floor argument by size band, and the
  margin-overlap test:
  [`places/place-income/AGENTS.md`](../place-income/AGENTS.md).
- The race *shares*, which is a different question from income by race:
  [`places/place-people/AGENTS.md`](../place-people/AGENTS.md).
- The same race-iteration medians where they are published far more often:
  [`counties/county-wellbeing/AGENTS.md`](../../counties/county-wellbeing/AGENTS.md).
- The same theme inside a city, with the Fulton County denominator worked
  through:
  [`tracts/tract-wellbeing/AGENTS.md`](../../tracts/tract-wellbeing/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and its z0–z5 features are counties carrying the Census Bureau's own
county estimates rather than these places', so nothing above can be reproduced
from tiles.
