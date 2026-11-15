# Agent guide — Health, Disability & Income by Race (ZIP Code Tabulation Areas)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

**Read this before anything else: a ZCTA is not a ZIP code, and it nests in nothing.** A ZIP Code Tabulation Area is the Census Bureau's approximation of a USPS 5-digit delivery area, built by giving each 2020 census block the most common ZIP code of the addresses in it ([what a ZCTA is](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html)). Three consequences:

- `state` is **NULL on all 33,791 rows**, so `WHERE state = 'CA'` returns nothing — silently, with no error.
- The first two characters of a `geoid` are a **postal region, not a state FIPS code**: `substr(geoid, 1, 2) = '06'` returns 289 rows and **not one of them is in California** — 288 intersect Connecticut and one, `06390`, is wholly in New York (measured in [`zcta-income`](../zcta-income/AGENTS.md)). A prefix join returns *wrong* rows rather than no rows.
- Relating a ZCTA to a county, tract or state is a **spatial** operation. Recipe 4 below does it, with a `bbox` covering-struct prefilter.

And the thing that bites hardest in *this* collection: **the NULLs are the subject, not an inconvenience.** The four race-iteration medians are published on 87.92% / 41.45% / 30.75% / 23.41% of ZCTAs (white_nh / hispanic / black / asian, measured). A blank means "not published here", never "low income", and `pct_below_poverty_black_cv` is over 0.40 on **50.7%** of the ZCTAs that publish one — so `*_cv` filtering is mandatory before mapping or ranking anything here.

## What this is

Health coverage, disability, nativity and income by race — the tables the Census Bureau does not publish for block groups. The uninsured share and the share with a disability ([B27001](https://data.census.gov/table/ACSDT5Y2024.B27001), [B18101](https://data.census.gov/table/ACSDT5Y2024.B18101)), the foreign-born share ([B05002](https://data.census.gov/table/ACSDT5Y2024.B05002)), the group-quarters population ([B26001](https://data.census.gov/table/ACSDT5Y2024.B26001)), median household income for Black, non-Hispanic White, Asian and Hispanic householders ([B19013B](https://data.census.gov/table/ACSDT5Y2024.B19013B), [B19013H](https://data.census.gov/table/ACSDT5Y2024.B19013H), [B19013D](https://data.census.gov/table/ACSDT5Y2024.B19013D), [B19013I](https://data.census.gov/table/ACSDT5Y2024.B19013I)), and the poverty rate of the Black alone population ([B17020B](https://data.census.gov/table/ACSDT5Y2024.B17020B)).

**33,791 rows**, one per ZIP Code Tabulation Area, ACS 2020–2024 5-year estimates, geometry from the 2020 cartographic boundary files — GENZ2020 is the only cartographic ZCTA edition the Census Bureau publishes, and the 2020-based ZCTAs are the ones the ACS tabulates.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/zcta-wellbeing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/zcta-wellbeing.pmtiles`, layer `zcta-wellbeing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/collection.json` — carries a full description for every column

This is a themed cut of the wide ZCTA table: the same 33,791 rows and the same geometry, 34 columns instead of 112. The wide sixth sibling is [`zctas/zctas`](../zctas/collection.json), whose own data files stay one directory up at `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zctas.parquet` (and `.pmtiles`).

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

`geoid` is the 5-digit ZCTA code and **joins nothing else in this catalog by prefix or by string**. It joins 1:1 to the five sibling ZCTA collections, and to nothing else: a ZCTA can cross county and state lines, so there is no prefix join to counties, tracts or states, and `substr(geoid, 1, 2)` is a postal region rather than a state FIPS code. `state` is NULL on every row for the same reason. To relate ZCTAs to states or counties, do it spatially (and expect a ZCTA to hit more than one), or use a Census relationship file.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 5-digit ZIP Code Tabulation Area code, e.g. `90210`. Not a ZIP code; does not nest in any other census geography. |
| `name` | string | `ZCTA5 ` + the code — "ZCTA5 90210". A ZCTA has no containing geography to name it by. |
| `state` | string | **Always NULL.** ZCTAs cross state lines, the ACS publishes them at the nation level only, and the 2020 cartographic boundary ZCTA file carries no state attribute. The column exists so the schema matches the catalog's other collections. |
| `population` | NULL on 0.06% of ZCTAs — the 19 rows with a 2020 cartographic boundary and no ACS tabulation (17 island-area ZCTAs plus 11717 and 11798 in Suffolk County, New York). Every other column is NULL on at least those rows. |
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
| `median_hh_income_black` | NULL on 69.25% of ZCTAs. |
| `median_hh_income_black_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_black`. |
| `median_hh_income_black_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_black`. |
| `median_hh_income_white_nh` | NULL on 12.08% of ZCTAs. |
| `median_hh_income_white_nh_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_white_nh`. |
| `median_hh_income_white_nh_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_white_nh`. |
| `median_hh_income_asian` | NULL on 76.59% of ZCTAs. |
| `median_hh_income_asian_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_asian`. |
| `median_hh_income_asian_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_asian`. |
| `median_hh_income_hispanic` | NULL on 58.55% of ZCTAs. |
| `median_hh_income_hispanic_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_hispanic`. |
| `median_hh_income_hispanic_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_hispanic`. |
| `pct_below_poverty_black` | NULL on 36.59% of ZCTAs. |
| `pct_below_poverty_black_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_below_poverty_black`. |
| `pct_below_poverty_black_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_below_poverty_black`. |
| `geometry` | binary | Boundary polygon, WKB, EPSG:4326 / OGC:CRS84. |
| `bbox` | struct<xmin, ymin, xmax, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, with row-group statistics. |

## Field notes

- **`state` is NULL on every row** and `geoid` joins nothing by prefix. See the schema note above; this is the single most common way to get a wrong answer out of this collection.
- **Every estimate has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. To compare two geographies, check
  whether their margins overlap before calling a difference real. To sum
  estimates across geographies, add the margins in quadrature
  (`sqrt(sum(moe*moe))`). **Never sum or average a median**: a median of a
  region is not derivable from the medians of its parts.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. At this geography the equity columns need it most: the median
  `pct_below_poverty_black_cv` is **0.406** and 50.7% of the ZCTAs that
  publish one are over 0.40 (measured, recipe 3).
- **The race-iteration medians are classified by the householder's race**, not by every member's, and each has its own universe (households with a householder who is …). They are not shares of a common total and cannot be averaged together.
- **A blank race-iteration median is "not published here", never a value.**
  Wherever too few households of that group live in the ZCTA, the Census
  Bureau publishes no median — so a map of one of these columns is as much a
  map of where the group lives as of its income. Quote the denominator whenever
  you quote a gap.
- **`pct_below_poverty_black` has a race-specific denominator** (the Black alone population for whom poverty status is determined), so it is not comparable to `pct_below_poverty`'s denominator in [`zcta-income`](../zcta-income/collection.json).
- **`pct_uninsured` and `pct_with_disability` are shares of the civilian noninstitutionalized population**, not of everyone: people on active duty and people in institutions are outside the universe. In a ZCTA that is mostly a military post or a correctional facility, most of the population is outside the denominator.
- **`group_quarters_pop` is the column that explains the catalog's strangest
  ZCTA rows.** 133 ZCTAs have over 2,000 people and under 100 households
  (measured, worked in [`zcta-connectivity`](../zcta-connectivity/AGENTS.md)) —
  campuses and bases, where `group_quarters_pop` is nearly all of
  `population`. Join this column in before trusting any household- or
  worker-denominated share.
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **A ZCTA's size varies enormously**: `aland_sqkm` runs from 0.004 to
  35,426.845 and `population` from 0 to 140,157, with a median of 2,656
  (measured). An unweighted mean over ZCTAs is not a national average.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population`, `group_quarters_pop` | NULL on 0.06% of ZCTAs — the 19 rows with a 2020 cartographic boundary and no ACS tabulation, not suppression. |
| `pct_uninsured`, `pct_with_disability` | NULL on 2.23% of ZCTAs. Not published for block groups at all. |
| `pct_foreign_born` | NULL on 1.83% of ZCTAs. |
| `median_hh_income_white_nh` | NULL on 12.08% of ZCTAs (10.04% of tracts, 2.38% of counties) — the least sparse of the four, which is itself a fact about the distribution of the population. |
| `median_hh_income_hispanic` | **NULL on 58.55% of ZCTAs** (44.43% of tracts, 19.60% of counties). |
| `median_hh_income_black` | **NULL on 69.25% of ZCTAs** (61.43% of tracts, 39.47% of counties). |
| `median_hh_income_asian` | **NULL on 76.59% of ZCTAs** (71.27% of tracts, 53.63% of counties) — the sparsest column in the catalog. |
| `pct_below_poverty_black` | NULL on 36.59% of ZCTAs: no Black-alone population for whom poverty status is determined, so no rate. |

Those 19 rows are 17 island-area ZCTAs — `00802`, `00820`, `00830`, `00840`, `00850`, `00851` (U.S. Virgin Islands), `96799` (American Samoa), `96910`, `96913`, `96915`, `96916`, `96917`, `96928`, `96929` (Guam), `96950`, `96951`, `96952` (Northern Mariana Islands) — plus `11717` and `11798` in Suffolk County, New York, measured by listing every row where `population IS NULL`. The island areas have 2020 cartographic boundaries but no ACS 5-year estimates, so they keep their geometry and publish NULL values rather than being dropped.

**598 ZCTAs (1.77%) have an ACS row with `population` exactly 0** (measured).

Row count checked against the Census Bureau's own [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html): 33,791 ZCTAs (33,642 United States + 132 Puerto Rico + 17 island areas), which is exactly the row count here. The ACS tabulates 33,772 of them, and every one of those 33,772 matched a polygon.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: z0–z5 are **counties**, carrying the Census Bureau's own county estimates under the same column names, and z6–z12 are the ZCTAs themselves. ZCTAs do not nest in counties, so the county band is national orientation, not a roll-up of these features. `*_moe` columns are not in the tiles at any zoom; `*_cv` columns are. Statistics come from the GeoParquet.

## Related collections

- [`zctas/zcta-income`](../zcta-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1. The overall `median_hh_income` these race iterations should be read beside.
- [`zctas/zcta-people`](../zcta-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1. Carries the race *shares*, which are published far more often than these medians.
- [`zctas/zcta-housing`](../zcta-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`zctas/zcta-connectivity`](../zcta-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`zctas/zctas`](../zctas/collection.json) ([agent guide](../zctas/AGENTS.md)) — the wide sixth sibling: all 112 columns, same 33,791 rows, data files one directory up.
- The same theme where GEOIDs *do* nest and the medians are published far more often: [`counties/county-wellbeing`](../../counties/county-wellbeing/collection.json), [`states/state-wellbeing`](../../states/state-wellbeing/collection.json), [`tracts/tract-wellbeing`](../../tracts/tract-wellbeing/collection.json), [`places/place-wellbeing`](../../places/place-wellbeing/collection.json), [`congressional-districts/cd-wellbeing`](../../congressional-districts/cd-wellbeing/collection.json).
- No twin at block-groups for this theme: the Census Bureau does not publish these tables at that geography.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, the geography ZCTAs are built from. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted. The
file is 69,676,429 bytes over 33,791 rows.

### 1. How often is each race-iteration median published at all?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT round(100.0*count(median_hh_income_white_nh)/count(*), 2) AS pct_published_white_nh,
       round(100.0*count(median_hh_income_hispanic)/count(*), 2) AS pct_published_hispanic,
       round(100.0*count(median_hh_income_black)/count(*), 2)    AS pct_published_black,
       round(100.0*count(median_hh_income_asian)/count(*), 2)    AS pct_published_asian,
       count(*) FILTER (WHERE median_hh_income_black    IS NOT NULL
                          AND median_hh_income_white_nh IS NOT NULL) AS both_black_white
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/zcta-wellbeing.parquet';
```

→ `87.92 | 41.45 | 30.75 | 23.41 | 10077`.

Run this before mapping any of those four columns. A national map of
`median_hh_income_asian` is drawn on **23.41%** of ZCTAs, and the 76% that are
blank are overwhelmingly ZCTAs where few Asian-householder households live — so
the map's *coverage* is a map of residential patterns and its *colour* is
income only where the colour exists. "No data" is never "low income" here.

The last number is the one that governs every gap statistic: a Black/white
household-income comparison is possible on **10,077 of 33,791 ZCTAs**, under a
third of the country, *before* any reliability filter. The same medians are
published much more widely at [county](../../counties/county-wellbeing/collection.json)
level (NULL on 39.47% against 69.25% here) — step up a geography when the
answer will be quoted as a single number.

### 2. Where are the most people uninsured? (`*_cv`-gated top-N)

```sql
LOAD httpfs;
SELECT geoid, population, pct_uninsured, pct_uninsured_moe AS moe,
       round(pct_uninsured_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/zcta-wellbeing.parquet'
WHERE population > 5000 AND pct_uninsured_cv < 0.12
ORDER BY pct_uninsured DESC LIMIT 5;
```

→ `46571 | 6315 | 63.78 | 9.71 | 0.09`, `46565 | 9014 | 61.65 | 2.75 | 0.03`,
`44627 | 7086 | 53.9 | 8.56 | 0.1`, `17509 | 5135 | 51.39 | 6.97 | 0.08`,
`44606 | 8182 | 46.9 | 4.02 | 0.05`.

A spatial check against [`states`](../../states/states/collection.json) puts
`46571` and `46565` wholly in Indiana, `44627` and `44606` in Ohio and `17509`
in Pennsylvania — the same cluster of rural uninsured communities the tract
guide finds in LaGrange County, Indiana. 61.65% ± 2.75 is an extraordinarily
tight margin for a ZCTA-level share, which is what makes the second row
credible without further work.

Remember the universe: `pct_uninsured` is a share of the **civilian
noninstitutionalised** population, so active-duty personnel and people in
institutions are outside the denominator entirely.

### 3. The equity columns are the noisiest here (`*_cv`, measured)

```sql
LOAD httpfs;
SELECT count(pct_below_poverty_black)    AS estimate_published,
       count(pct_below_poverty_black_cv) AS publishes_cv,
       round(quantile_cont(pct_below_poverty_black_cv, 0.5), 3) AS median_cv,
       round(100.0*count(*) FILTER (WHERE pct_below_poverty_black_cv > 0.40)
             / count(pct_below_poverty_black_cv), 1) AS pct_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/zcta-wellbeing.parquet';
```

→ `21427 | 15918 | 0.406 | 50.7`.

The **median** ZCTA's Black poverty rate has a coefficient of variation of
0.406 — above the "unreliable" line — and half of the ZCTAs that publish a CV
are past it. 21,427 ZCTAs publish the estimate and only 15,918 publish a CV,
because the CV is NULL wherever the estimate is 0, so a `_cv` filter is also a
filter on "has any measured Black poverty". There is no honest unfiltered map
of this column at this geography: grey out `pct_below_poverty_black_cv > 0.40`,
state the share you dropped, or move the question up to
[counties](../../counties/county-wellbeing/collection.json), where the same
column's median CV is 0.275.

### 4. Income by race inside one county — spatially, with the denominator

```sql
LOAD spatial; LOAD httpfs;
WITH c AS (
  SELECT geometry, bbox
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet'
  WHERE geoid = '13121'),                    -- Fulton County, Georgia
zc AS (
  SELECT w.median_hh_income_black, w.median_hh_income_white_nh,
         w.median_hh_income_black_cv, w.median_hh_income_white_nh_cv
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/zcta-wellbeing.parquet' w, c
  WHERE w.bbox.xmin <= c.bbox.xmax AND w.bbox.xmax >= c.bbox.xmin
    AND w.bbox.ymin <= c.bbox.ymax AND w.bbox.ymax >= c.bbox.ymin
    AND ST_Area(ST_Intersection(w.geometry, c.geometry)) / ST_Area(w.geometry) > 0.5)
SELECT count(*)                                  AS zctas_majority_in_fulton,
       count(median_hh_income_black)             AS black_published,
       count(median_hh_income_white_nh)          AS white_published,
       count(*) FILTER (WHERE median_hh_income_black    IS NOT NULL
                          AND median_hh_income_white_nh IS NOT NULL) AS both,
       count(*) FILTER (WHERE median_hh_income_black_cv    < 0.20
                          AND median_hh_income_white_nh_cv < 0.20)   AS both_reliable
FROM zc;
```

→ `37 | 31 | 31 | 29 | 17`.

37 ZCTAs have more than half their area in Fulton County; 29 publish both
medians and **17** survive a 0.20 CV gate on both. That is the denominator for
every sentence the next query produces:

```sql
LOAD spatial; LOAD httpfs;
WITH c AS (
  SELECT geometry, bbox
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet'
  WHERE geoid = '13121')
SELECT w.geoid, i.median_hh_income::int        AS overall,
       w.median_hh_income_white_nh::int        AS white_nh,
       w.median_hh_income_black::int           AS black,
       round(w.median_hh_income_black::double / w.median_hh_income_white_nh, 2) AS black_to_white
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/zcta-wellbeing.parquet' w
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet' i
  USING (geoid), c
WHERE w.bbox.xmin <= c.bbox.xmax AND w.bbox.xmax >= c.bbox.xmin
  AND w.bbox.ymin <= c.bbox.ymax AND w.bbox.ymax >= c.bbox.ymin
  AND ST_Area(ST_Intersection(w.geometry, c.geometry)) / ST_Area(w.geometry) > 0.5
  AND w.median_hh_income_black_cv    < 0.20
  AND w.median_hh_income_white_nh_cv < 0.20
ORDER BY black_to_white LIMIT 5;
```

→ `30312 | 82779 | 146717 | 35801 | 0.24`, `30310 | 53037 | 140260 | 41073 |
0.29`, `30314 | 42089 | 115208 | 36475 | 0.32`, `30315 | 50822 | 116496 | 40908
| 0.35`, `30318 | 83116 | 137301 | 53880 | 0.39`.

"In the 17 of 37 Fulton County ZCTAs where both medians are published
reliably, Black household income runs from 24% to 68% of non-Hispanic White
household income" is a true sentence (measured); "in Fulton County ZIP codes"
is not.

Note the first row: the ZCTA's overall median ($82,779) sits **between** the
two race-specific medians rather than near either. That is possible
because the three medians have three different universes (all households;
non-Hispanic White householders; Black householders) and a median is not a
weighted average of sub-medians. The `ST_Area(ST_Intersection(...)) > 0.5`
membership gate is doing real work too — `ST_Intersects` alone picks up ZCTAs
that merely touch the county across a generalized boundary, and
`substr(geoid, 1, 5)` cannot reach a county from a ZCTA code at all.

### 5. Disability and insurance together, reliability-gated

```sql
LOAD httpfs;
SELECT geoid, population, pct_with_disability, round(pct_with_disability_cv, 2) AS dis_cv,
       pct_uninsured, round(pct_uninsured_cv, 2) AS unins_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/zcta-wellbeing.parquet'
WHERE population > 5000
  AND pct_with_disability_cv < 0.10 AND pct_uninsured_cv < 0.20
ORDER BY pct_with_disability DESC LIMIT 5;
```

→ `00739 | 34578 | 35.99 | 0.03 | 5.45 | 0.12`, `63957 | 5144 | 34.11 | 0.06 |
12.8 | 0.13`, `00677 | 15483 | 33.4 | 0.05 | 5.97 | 0.17`, `00751 | 19343 |
33.25 | 0.05 | 4.45 | 0.17`, `00627 | 32734 | 32.89 | 0.04 | 5.01 | 0.14`.

Four of the five are in Puerto Rico and one in Missouri (checked spatially
against [`states`](../../states/states/collection.json)). The two columns move
independently: `00739` pairs a 36% disability share with 5.45% uninsured, while
`63957` pairs 34% with 12.8% — reading one as a proxy for the other would be
wrong in both directions. Note the two different `_cv` thresholds: the columns
have different precision at this geography (median CV 0.147 for
`pct_with_disability` against 0.284 for `pct_uninsured`, per the catalog's
measurements), and forcing one threshold on both drops rows for the wrong
reason.

### Related recipes elsewhere

- All 112 columns at once, one row per ZCTA:
  [`zctas/zctas/AGENTS.md`](../zctas/AGENTS.md).
- The `geoid`-prefix trap measured, and the spatial state membership test:
  [`zctas/zcta-income/AGENTS.md`](../zcta-income/AGENTS.md).
- `group_quarters_pop` in action — the campuses and bases where a
  household-denominated share collapses:
  [`zctas/zcta-connectivity/AGENTS.md`](../zcta-connectivity/AGENTS.md).
- The same race-iteration medians where they are published far more often:
  [`counties/county-wellbeing/AGENTS.md`](../../counties/county-wellbeing/AGENTS.md),
  [`tracts/tract-wellbeing/AGENTS.md`](../../tracts/tract-wellbeing/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and its z0–z5 features are counties rather than ZCTAs, so nothing
above can be reproduced from tiles.
