# Agent guide — Income & Poverty (States)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Income, poverty and employment: median household income and per capita income ([B19013](https://data.census.gov/table/ACSDT5Y2024.B19013), [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301)), the share of people below the poverty line and below twice it ([C17002](https://data.census.gov/table/ACSDT5Y2024.C17002)), the share of households receiving SNAP ([B22010](https://data.census.gov/table/ACSDT5Y2024.B22010)), and the unemployment rate as a share of the civilian labor force ([B23025](https://data.census.gov/table/ACSDT5Y2024.B23025)), plus total population ([B01003](https://data.census.gov/table/ACSDT5Y2024.B01003)) and population density for context.

**56 rows** — the 50 states, the District of Columbia, Puerto Rico and the four
island areas — ACS 2020–2024 5-year estimates, geometry from the 2024
cartographic boundary files. **52 of the 56 carry ACS data**; the four island
areas carry geometry and NULLs.

This is the most reliable income file in the catalog, and the bluntest. Nothing
in it is suppressed: every column is published on all 52 rows that have ACS
data, and the worst `median_hh_income_cv` on any of them is **0.011** —
measured, against a 0.12 "reliable" threshold. The counterpoint is the row
count. 52 rows answer "how do states compare"; they never answer "what is this
neighbourhood like", and a state median describes no particular place inside
the state. Recipe 3 measures how badly, and recipe 4 shows that a state's value
is estimated directly by the Census Bureau rather than built from its counties.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.pmtiles`, layer `state-income`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/collection.json` — carries a full description for every column

This is a themed cut of the wide 112-column table, which is published beside it
as the sixth collection in this group and holds the same 56 rows and the same
geometry: `https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet`
(its data files sit one directory up, beside the group's `catalog.json`). At
this geography the chunking buys almost nothing on download — `geometry` is
3.86 MB of this file's 3.88 MB (measured from the Parquet column metadata), and
the wide table is only about 49 KB larger. Choose a chunk for a narrower schema,
not to save bandwidth.

## Source tables

| table | title | universe |
|---|---|---|
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B19013](https://data.census.gov/table/ACSDT5Y2024.B19013) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) | Households |
| [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301) | Per Capita Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) | Total population |
| [B22010](https://data.census.gov/table/ACSDT5Y2024.B22010) | Receipt of Food Stamps/SNAP in the Past 12 Months by Disability Status for Households | Households |
| [B23025](https://data.census.gov/table/ACSDT5Y2024.B23025) | Employment Status for the Population 16 Years and Over | Population 16 years and over |
| [C17002](https://data.census.gov/table/ACSDT5Y2024.C17002) | Ratio of Income to Poverty Level in the Past 12 Months | Population for whom poverty status is determined |

## Schema

`geoid` is 2 characters and is the join key: every finer geography's
`substr(geoid, 1, 2)` is this column.

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
| `geometry` | binary | Boundary polygon, WKB, EPSG:4326 / OGC:CRS84. |
| `bbox` | struct<xmin, ymin, xmax, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, with row-group statistics. |

## Field notes

- **`population_moe` is NULL on all 56 rows** (measured), and so is the margin
  on every share whose denominator is the total population. At this geography
  the margin-of-error columns that are NULL on every row are
  `population_moe`, `pct_under_18_moe`, `pct_65_plus_moe`, `pct_white_nh_moe`,
  `pct_black_moe`, `pct_native_moe`, `pct_asian_moe`,
  `pct_people_of_color_moe`, `pct_hispanic_moe`, `pct_foreign_born_moe` and
  `group_quarters_pop_moe` — 11 of the wide table's 112 columns, measured
  across all six collections in this group. Only `population_moe` is in *this*
  collection; the rest live in [`state-people`](../state-people/collection.json)
  and [`state-wellbeing`](../state-wellbeing/collection.json). The build writes
  NULL rather than a guess when an input margin is NULL
  (`tools/column_docs.py`), so a share over a population denominator inherits
  the gap. Practical consequence: `sqrt(sum(population_moe*population_moe))`
  over these rows returns NULL, not a number.
- **That NULL is upstream, and it is not suppression.** Each of those columns
  comes from a total-population table (B01003), and in the release's own
  `.dat` files those rows carry the estimate beside `-555555555`, the
  **controlled-MOE** jam value a controlled estimate gets in place of a
  sampling margin — `0400000US06|39287377|-555555555` in
  `staging/census-cache/acsdt5y2024-b01003.dat`, read 2026-11-15. The build
  turns it into NULL rather than publishing it as a number
  (`tools/build_acs.py`). The same columns carry margins normally at the finer
  geographies, where the estimates are not controlled this way:
  `population_moe` is carried on 33,759 of 33,791 ZCTAs and on all 241,854
  populated block groups (measured).
- **Every other estimate here has a `<name>_moe`**, at the 90% confidence level
  — the level the Census Bureau publishes. To compare two geographies, check
  whether their margins overlap before calling a difference real. To sum
  estimates across geographies, add the margins in quadrature
  (`sqrt(sum(moe*moe))`). **Never sum or average a median**: a median of a
  region is not derivable from the medians of its parts.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. At this geography no filtering is needed — see Data quality — but
  the columns are there so one style or one query can run at every geography.
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **A state's value is the Census Bureau's own estimate for the state**, not a
  sum or an average of its counties. Counts do add up — county `households`
  sums exactly to the state row for all 52 states, measured in
  [`state-housing`](../state-housing/AGENTS.md) — but medians and rates do not,
  and the Bureau's published state margin is its own rather than the quadrature
  of its counties'. Recipe 4 measures the size of the mistake.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area, and neither number is wrong.
- **`pct_unemployed` divides by the civilian labor force** (B23025 line 3), not
  by the population 16 and over. That is what makes it an unemployment rate.
- **`pct_below_poverty`'s universe is the population for whom poverty status is
  determined**, which excludes institutionalized people, people in military
  group quarters and in college dormitories, and unrelated individuals under
  15. It is not a share of `population`.
- **`per_capita_income` divides aggregate income by the whole population**, so
  children and people with no income are in the denominator. It is not
  comparable to `median_hh_income`, whose universe is households.

## Data quality

Columns with notable missingness at this geography (measured over the file as
built, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 4 of 56 rows (7.14%): American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have boundaries here but no ACS 5-year data, because the island areas run a separate decennial-only program. 52 rows carry data. |
| every other ACS column | NULL on exactly the same 4 rows. Nothing in this collection is suppressed: `median_hh_income`, `per_capita_income`, `pct_below_poverty`, `pct_below_2x_poverty`, `pct_snap` and `pct_unemployed` are each published on all 52 rows with data (measured). |
| `population_moe` | NULL on all 56 rows — see the field notes. |

The 7.14% NULL rate is the highest of any geography in the catalog for
`median_hh_income` (0.43% of counties, 1.59% of tracts, measured), and it is
not suppression: it is four island areas out of only 56 rows. Read the two
numbers separately — coverage of *rows* is worst here, coverage of *data where
there is data* is perfect.

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern
Mariana Islands and the U.S. Virgin Islands have cartographic boundaries but no
ACS 5-year estimates, so their rows publish with NULL values rather than being
dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 17
ZCTAs, 279 places and 4 delegate districts.

Margins of error are small at this geography but not zero, and the ranking they
support is weaker than it looks: of the 51 adjacent pairs in a ranking of the 52
states by `median_hh_income`, only **15** have 90% intervals that do not
overlap (measured — recipe 5). Reliability of a single value and significance
of a comparison are different questions.

The PMTiles archive is real state polygons at every zoom, band `0-8:geom`
(`tools/make_tiles.py`) — there is no coarser-geography band at coarse zooms,
because 56 features tile directly. `*_moe` columns are excluded from every tile
at every zoom; `*_cv` columns are kept. Statistics come from the GeoParquet,
always.

## Related collections

- [`states/state-people`](../state-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`states/state-housing`](../state-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`states/state-connectivity`](../state-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`states/state-wellbeing`](../state-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`states/states`](../states/collection.json) ([agent guide](../states/AGENTS.md)) — the sixth sibling: all 112 columns in one table, same 56 rows, data files one directory up.
- [`counties/county-income`](../../counties/county-income/collection.json), [`tracts/tract-income`](../../tracts/tract-income/collection.json) and [`block-groups/bg-income`](../../block-groups/bg-income/collection.json) — the same theme at finer geographies, where the medians start to be suppressed and the margins widen.
- [`zctas/zcta-income`](../../zctas/zcta-income/collection.json), [`places/place-income`](../../places/place-income/collection.json), [`congressional-districts/cd-income`](../../congressional-districts/cd-income/collection.json) — the same theme at the other statistical geographies.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

Instead, the cost: 56 rows and 3.9 MB, of which 3.86 MB is geometry. No filter
is ever needed here for cost, and `SELECT * EXCLUDE (geometry)` is a reasonable
thing to do.

### 1. The whole country, ranked — and the four rows that are not there

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*) AS states, count(median_hh_income) AS published,
       quantile_cont(median_hh_income, 0.10)::int AS p10,
       quantile_cont(median_hh_income, 0.50)::int AS p50,
       quantile_cont(median_hh_income, 0.90)::int AS p90,
       round(max(median_hh_income_cv), 4) AS worst_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet';
```

→ `56 | 52 | 63753 | 77419 | 99113 | 0.011`.

Four of the 56 rows have no ACS data at all, and the worst coefficient of
variation across the other 52 is 0.011. The top of the ranking:

```sql
LOAD httpfs;
SELECT name, median_hh_income::int AS income, round(median_hh_income_cv, 4) AS cv,
       pct_below_poverty, pct_snap, pct_unemployed
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet'
WHERE median_hh_income IS NOT NULL
ORDER BY median_hh_income DESC LIMIT 5;
```

→ `District of Columbia | 109870 | 0.011 | 15.44 | 14.3 | 6.35`,
`Massachusetts | 103960 | 0.003 | 10.04 | 14.65 | 5.15`,
`Maryland | 103678 | 0.004 | 9.45 | 11.15 | 4.89`,
`New Jersey | 103556 | 0.003 | 9.72 | 9.15 | 6.31`,
`Hawaii | 100389 | 0.007 | 10.04 | 11.42 | 4.92`.

The `IS NOT NULL` filter is not cosmetic:

```sql
LOAD httpfs;
SELECT count(*) AS rows, count(population) AS with_acs_data,
       string_agg(name, ', ') FILTER (WHERE population IS NULL) AS no_data
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet';
```

→ `56 | 52 | American Samoa, United States Virgin Islands, Guam, Commonwealth
of the Northern Mariana Islands`. Any `ORDER BY … ASC` without the filter
returns four NULL rows first, and any `count(*)` denominator of 56 is wrong by
four. Note also that the District of Columbia tops the income ranking *and*
sits 9th of the 52 on `pct_below_poverty` (15.44%, measured) — a median is not
a summary of a distribution, and the two columns are not redundant.

### 2. Which geography should this question be asked at? (`*_cv`, three files)

```sql
LOAD httpfs;
SELECT 'state' AS geography, count(median_hh_income_cv) AS n,
       round(quantile_cont(median_hh_income_cv, 0.5), 3) AS median_cv,
       round(max(median_hh_income_cv), 3) AS max_cv,
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40)
             / count(median_hh_income_cv), 1) AS pct_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet'
UNION ALL
SELECT 'county', count(median_hh_income_cv),
       round(quantile_cont(median_hh_income_cv, 0.5), 3), round(max(median_hh_income_cv), 3),
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40) / count(median_hh_income_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet'
UNION ALL
SELECT 'tract', count(median_hh_income_cv),
       round(quantile_cont(median_hh_income_cv, 0.5), 3), round(max(median_hh_income_cv), 3),
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40) / count(median_hh_income_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet';
```

→

```
state  |    52 | 0.004 | 0.011 | 0.0
county |  3221 | 0.042 | 0.530 | 0.1
tract  | 83266 | 0.125 | 0.607 | 1.5
```

The median state CV is 0.004 and the worst is 0.011 — a factor of 30 better
than the median tract. So: **no `_cv` filtering is needed at state level**, and
conversely, class breaks or thresholds measured from this collection are
useless at tract or block-group level, where the same column runs past 0.40.
Reliability is a property of geography size, not of the column.

### 3. How much does a state figure hide? (GEOID prefix join to counties)

```sql
LOAD httpfs;
SELECT s.name AS state, s.median_hh_income::int AS state_income,
       count(*) AS counties,
       min(c.median_hh_income)::int AS poorest_county,
       max(c.median_hh_income)::int AS richest_county,
       round(max(c.median_hh_income)/min(c.median_hh_income), 2) AS ratio
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet' s
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet' c
  ON s.geoid = substr(c.geoid, 1, 2)
WHERE s.median_hh_income IS NOT NULL AND c.median_hh_income IS NOT NULL
GROUP BY 1, 2 ORDER BY ratio DESC LIMIT 5;
```

→ `Kentucky | 63726 | 120 | 22188 | 122497 | 5.52`,
`Georgia | 77353 | 159 | 28380 | 143784 | 5.07`,
`Tennessee | 69595 | 95 | 28814 | 135594 | 4.71`,
`Virginia | 93170 | 133 | 38675 | 181765 | 4.7`,
`Colorado | 95470 | 64 | 36861 | 149594 | 4.06`.

`s.geoid = substr(c.geoid, 1, 2)` is the whole join — a county GEOID begins
with its state's FIPS code, and the same prefix trick reaches tracts
(`substr(geoid, 1, 2)`) and block groups. Kentucky's richest county has 5.5×
the median income of its poorest and the state figure of $63,726 describes
neither. **This is the recipe to run before quoting any state number as a
description of anywhere in particular**, and it is the shape to reuse for "each
X against its own state" at every finer geography.

### 4. A state is estimated directly, not built from its counties

```sql
LOAD httpfs;
SELECT s.name AS state,
       s.median_hh_income::int                AS published_state_median,
       round(avg(c.median_hh_income))::int    AS mean_of_county_medians,
       round(median(c.median_hh_income))::int AS median_of_county_medians
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet' s
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet' c
  ON s.geoid = substr(c.geoid, 1, 2)
WHERE s.state IN ('KY','CA','TX') AND c.median_hh_income IS NOT NULL
GROUP BY 1, 2 ORDER BY 1;
```

→ `California | 99122 | 89387 | 83473`, `Kentucky | 63726 | 56863 | 57293`,
`Texas | 78476 | 66482 | 65035`.

Three ways of asking the same question, three different answers. The published
column is the Census Bureau's own estimate for the state, tabulated from the
state's own sample; the other two are arithmetic on county medians and are not
estimates of anything. Texas is off by $11,994 — the mean of its 254 county
medians weights a county of 33 people the same as one of 4,838,303 (measured).
**The middle and right columns
of this query are what not to compute.** Counts behave differently: county
`households` sums exactly to the state row for all 52 states (measured in
[`state-housing`](../state-housing/AGENTS.md)).

### 5. The ranking is mostly ties (margins, not estimates)

```sql
LOAD httpfs;
SELECT name, median_hh_income::int AS income, median_hh_income_moe::int AS moe,
       (median_hh_income - median_hh_income_moe)::int AS lo,
       (median_hh_income + median_hh_income_moe)::int AS hi
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet'
WHERE state IN ('MA','MD','NJ','HI')
ORDER BY income DESC;
```

→ `Massachusetts | 103960 | 527 | 103433 | 104487`,
`Maryland | 103678 | 597 | 103081 | 104275`,
`New Jersey | 103556 | 513 | 103043 | 104069`,
`Hawaii | 100389 | 1121 | 99268 | 101510`.

Ranks 2, 3 and 4 are a three-way tie: the intervals [103,043–104,069],
[103,081–104,275] and [103,433–104,487] all overlap, so "Maryland is richer
than New Jersey" is not supported by these estimates. Hawaii's interval is
genuinely below all three. How often does the ladder hold?

```sql
LOAD httpfs;
WITH r AS (
  SELECT name, median_hh_income AS v, median_hh_income_moe AS m,
         lead(median_hh_income)     OVER (ORDER BY median_hh_income DESC) AS nv,
         lead(median_hh_income_moe) OVER (ORDER BY median_hh_income DESC) AS nm
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet'
  WHERE median_hh_income IS NOT NULL)
SELECT count(*) AS adjacent_pairs,
       count(*) FILTER (WHERE v - m > nv + nm) AS intervals_disjoint
FROM r WHERE nv IS NOT NULL;
```

→ `51 | 15`. Only 15 of the 51 neighbouring pairs are separated by their own
margins. The CVs here are tiny and the rank order is still mostly noise between
neighbours — "most reliable file in the catalog" is a statement about single
values, not about the gaps between them.

### Related recipes elsewhere

- Every county against its own state, and the margin of a county sum:
  [`counties/county-income/AGENTS.md`](../../counties/county-income/AGENTS.md).
- The same columns where suppression and wide margins start to bite:
  [`tracts/tract-income/AGENTS.md`](../../tracts/tract-income/AGENTS.md).
- Income by race and ethnicity at this geography — published for every one of
  the 52 rows, which is true at no other geography:
  [`states/state-wellbeing/AGENTS.md`](../state-wellbeing/AGENTS.md).
- All 112 state columns in one table, with recipes timed against the published
  mirror: [`states/states/AGENTS.md`](../states/AGENTS.md).
- What this geography is for and when to step down from it:
  [`states/AGENTS.md`](../AGENTS.md).

Statistics come from the GeoParquet. The state PMTiles archive is real polygons
at every zoom — it needs no coarser-geography band — but carries no `*_moe`
columns, so none of the margin arithmetic above can be reproduced from tiles.
