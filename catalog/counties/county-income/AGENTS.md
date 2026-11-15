# Agent guide — Income & Poverty (Counties)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Income, poverty and employment: median household income and per capita income ([B19013](https://data.census.gov/table/ACSDT5Y2024.B19013), [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301)), the share of people below the poverty line and below twice it ([C17002](https://data.census.gov/table/ACSDT5Y2024.C17002)), the share of households receiving SNAP ([B22010](https://data.census.gov/table/ACSDT5Y2024.B22010)), and the unemployment rate as a share of the civilian labor force ([B23025](https://data.census.gov/table/ACSDT5Y2024.B23025)), plus total population ([B01003](https://data.census.gov/table/ACSDT5Y2024.B01003)) and population density for context.

**3,235 rows**, one per county or county equivalent, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

Counties are the coarsest geography most questions are actually asked at, and the most reliable level in this catalog below states. This is the collection where a national income ranking mostly survives its own margins of error: the median `median_hh_income_cv` is **0.042** here against 0.125 at tract level and 0.202 at block group, and `median_hh_income` is published for 3,221 of the 3,235 rows (measured, below).

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.pmtiles`, layer `county-income`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/collection.json` — carries a full description for every column

This is one themed cut of the county table. The same rows with all 112 columns — every theme at once, no join — are the sixth sibling in this group, [`counties/counties`](../counties/collection.json), whose data files sit one directory up at `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet` (and `.pmtiles`).

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

`geoid` is 5 characters and is the join key: `substr(geoid, 1, 2)` → state FIPS; tracts and block groups join back on their own first 5 characters.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 5-character county GEOID: state 2 + county 3. |
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

- **`population_moe` is NULL on 3,103 of the 3,235 rows** (measured — only 132
  small rural counties carry one: 28 in Texas, 26 in Nebraska, 14 in South
  Dakota, 13 in Montana, …). Read `population` at this geography as a count to
  use rather than an estimate to put an interval on, and check for NULLs before
  putting `population_moe` into a quadrature sum — `sqrt(sum(moe*moe))` over a
  NULL-bearing column returns NULL. Every other `*_moe` column in **this**
  chunk is populated on all 3,222 rows that carry ACS data; that is not true of
  [`county-people`](../county-people/collection.json), where eight of the share
  margins follow `population_moe`'s pattern exactly.
- **Every other estimate has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. To compare two geographies, check
  whether their margins overlap before calling a difference real. To sum
  estimates across geographies, add the margins in quadrature
  (`sqrt(sum(moe*moe))`). **Never sum or average a median**: a median of a
  region is not derivable from the medians of its parts.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. Filtering or greying out by CV is the intended use — though at
  this geography it rarely removes anything: exactly **2** of the 3,221
  counties that publish a `median_hh_income_cv` are above 0.40, with a maximum
  of 0.53 (measured).
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
- **`pct_unemployed` divides by the civilian labor force** (B23025 line 3), not
  by the population 16 and over. That is what makes it an unemployment rate.
- **`per_capita_income` divides aggregate income by total population**, so
  children and people with no income are in the denominator. It is not a
  per-earner or per-household figure and does not track `median_hh_income`.
- **Connecticut's county equivalents are the 9 planning regions**
  (`09110`–`09190`, measured) in the 2024 vintage, not the 8 historical
  counties. A 2020-vintage block or tract GEOID's 5-character prefix does not
  match these rows.

## Data quality

Columns with notable missingness at this geography, measured over this file:

| column | missingness |
|---|---|
| `population` | NULL on 0.40% of counties (13 rows) — the island-area county equivalents (AS 5, GU 1, MP 4, VI 3, measured), which have cartographic boundaries but no ACS 5-year estimates. |
| `population_moe` | NULL on 95.92% of counties (3,103 of 3,235). Only 132 rows carry a margin on `population`. |
| `median_hh_income` | NULL on 0.43% of counties (14 rows) — against 1.59% of tracts and 7.69% of block groups. |
| `per_capita_income`, `pct_below_poverty`, `pct_below_2x_poverty`, `pct_snap`, `pct_unemployed` | NULL on 0.40% (13 rows) — the island areas only. Nothing in this chunk is suppressed for sample size except one income median. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

So 3,222 of the 3,235 rows carry ACS data, and 3,221 of those have a publishable income median. The single county with data and no median is `35011` De Baca County, New Mexico, population 1,576.

Margins of error at this geography are the narrowest in the catalog below state level, but they are not zero. Use the `*_cv` columns to flag or grey out unreliable values; never compare two counties without checking whether their margins overlap, and never aggregate a median.

The PMTiles archive carries real county polygons at every zoom — the band is `0-10:geom`, there are few enough features to draw them all at a national zoom, so there is no coarser-geography band at coarse zooms the way the tract and block-group collections have one. `*_moe` columns are excluded from the tiles at every zoom; `*_cv` columns are kept. Statistics come from the GeoParquet, always.

## Related collections

- [`counties/county-people`](../county-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`counties/county-housing`](../county-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`counties/county-connectivity`](../county-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`counties/county-wellbeing`](../county-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`counties/counties`](../counties/collection.json) — the sixth sibling: all 112 columns in one wide table, same 3,235 rows, data files one directory up. Use it instead of a join when a question crosses three or more themes.
- The same theme at the other geographies: [`states/state-income`](../../states/state-income/collection.json), [`tracts/tract-income`](../../tracts/tract-income/collection.json), [`block-groups/bg-income`](../../block-groups/bg-income/collection.json), [`zctas/zcta-income`](../../zctas/zcta-income/collection.json), [`places/place-income`](../../places/place-income/collection.json), [`congressional-districts/cd-income`](../../congressional-districts/cd-income/collection.json).
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error, and no income at all.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

For cost: this file is 12.3 MB over 3,235 rows, most of it geometry. Nothing
here needs a filter to be affordable, and a column-projected scan reads a small
fraction of that.

### 1. Where does county median household income sit, nationally?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*)                                                    AS counties,
       count(median_hh_income)                                     AS published,
       round(100.0*(count(*)-count(median_hh_income))/count(*), 2) AS pct_suppressed,
       quantile_cont(median_hh_income, 0.10)::int                  AS p10,
       quantile_cont(median_hh_income, 0.50)::int                  AS p50,
       quantile_cont(median_hh_income, 0.90)::int                  AS p90
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet';
```

→ `3235 | 3221 | 0.43 | 46875 | 65346 | 89168`.

0.43% suppressed against 1.59% at tract level and 7.69% at block group. Count
the gap carefully: 13 of the 14 missing rows are the island-area county
equivalents, which have 2024 boundaries and no ACS estimates at all, and the
fourteenth is De Baca County, New Mexico (`35011`), which has ACS data and too
thin a sample for a published median.

One state is the same query with `WHERE state = 'XX'`:

```sql
LOAD httpfs;
SELECT geoid, name, median_hh_income::int AS income, round(median_hh_income_cv, 3) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet'
WHERE state = 'MS'
ORDER BY median_hh_income DESC LIMIT 5;
```

→ `28033 | DeSoto County, Mississippi | 85297 | 0.018`, `28089 | Madison
County, Mississippi | 83441 | 0.021`, `28121 | Rankin County, Mississippi |
79357 | 0.024`, `28073 | Lamar County, Mississippi | 70909 | 0.04`, `28137 |
Tate County, Mississippi | 69704 | 0.047`.

No `_cv` gate was needed: every CV in the result is under 0.05. Compare the
same question at tract level, where the gate is load-bearing. The `name`
column already carries the state, so a readable ranking needs no join.

### 2. Which geography should this question be asked at? (`*_cv`, three files)

```sql
LOAD httpfs;
SELECT 'county' AS geography, count(median_hh_income_cv) AS n,
       round(quantile_cont(median_hh_income_cv, 0.5), 3) AS median_cv,
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40)
             / count(median_hh_income_cv), 1) AS pct_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet'
UNION ALL
SELECT 'tract', count(median_hh_income_cv),
       round(quantile_cont(median_hh_income_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40)
             / count(median_hh_income_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet'
UNION ALL
SELECT 'block group', count(median_hh_income_cv),
       round(quantile_cont(median_hh_income_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40)
             / count(median_hh_income_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.parquet';
```

→ `county | 3221 | 0.042 | 0.1`, `tract | 83266 | 0.125 | 1.5`, `block group |
220201 | 0.202 | 11.8`.

Run this before deciding which geography a question belongs at. At county level
one income median in a thousand is unreliable; at block group it is one in
eight. The price is resolution: 3,221 answers instead of 220,201. If the answer
will be quoted as a single number or ranked nationally, it belongs here.

### 3. Does the national ranking survive its margins? (margins, not estimates)

```sql
LOAD httpfs;
SELECT name, median_hh_income::int AS income,
       (median_hh_income - median_hh_income_moe)::int AS lo,
       (median_hh_income + median_hh_income_moe)::int AS hi
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet'
WHERE median_hh_income IS NOT NULL
ORDER BY median_hh_income DESC LIMIT 6;
```

→ `Loudoun County, Virginia | 181765 | 178327 | 185203`, `Santa Clara County,
California | 164281 | 162326 | 166236`, `San Mateo County, California | 158855
| 156004 | 161706`, `Fairfax County, Virginia | 153637 | 152002 | 155272`,
`Howard County, Maryland | 149763 | 146605 | 152921`, `Douglas County, Colorado
| 149594 | 147075 | 152113`.

The first four ranks are real: no interval touches the next. Ranks five and six
are not — Howard County's [146,605–152,921] and Douglas County's
[147,075–152,113] overlap almost completely, so "the fifth-richest county in
America" is a coin toss between them. Report the top four as ordered and the
next two as tied.

And the top of the ranking is unique:

```sql
LOAD httpfs;
WITH top AS (SELECT median_hh_income - median_hh_income_moe AS lo
             FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet'
             WHERE median_hh_income IS NOT NULL ORDER BY median_hh_income DESC LIMIT 1)
SELECT count(*) AS counties_whose_interval_reaches_the_top
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet', top
WHERE median_hh_income IS NOT NULL
  AND median_hh_income + median_hh_income_moe >= top.lo;
```

→ `1`. Exactly one county — Loudoun itself — has an upper bound that reaches
Loudoun's lower bound, so at the 90% level it is unambiguously the
highest-income county in the file. `estimate ± moe` is the Bureau's own
published interval, not an added assumption. This test is the reason to answer
a ranking question here rather than one geography down.

### 4. Income against housing cost (1:1 sibling join)

```sql
LOAD httpfs;
SELECT i.geoid, i.name, i.median_hh_income::int AS income, h.median_home_value::int AS home_value,
       round(h.median_home_value / i.median_hh_income, 1) AS value_to_income
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet' i
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet' h
  USING (geoid)
WHERE i.population > 100000
  AND i.median_hh_income_cv < 0.05 AND h.median_home_value_cv < 0.05
ORDER BY value_to_income DESC LIMIT 5;
```

→ `36047 | Kings County, New York | 80263 | 905000 | 11.3`, `36005 | Bronx
County, New York | 48676 | 529500 | 10.9`, `36061 | New York County, New York |
103931 | 1090500 | 10.5`, `06041 | Marin County, California | 149091 | 1507300
| 10.1`, `06075 | San Francisco County, California | 140970 | 1394500 | 9.9`.

The join is 1:1 on `geoid` — all six county collections hold the same 3,235
rows. `value_to_income` is a ratio of two medians from two different universes
(owner-occupied units vs all households); it is a useful screening index and
not a household-level statistic. If a question crosses three or more themes,
read [`counties/counties`](../counties/collection.json) instead of joining.

### 5. Each county against its own state (GEOID prefix join)

```sql
LOAD httpfs;
SELECT c.name, c.median_hh_income::int AS county_income,
       s.median_hh_income::int         AS state_income,
       round(100.0*c.median_hh_income/s.median_hh_income - 100, 1) AS pct_vs_state
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet' c
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet' s
  ON substr(c.geoid, 1, 2) = s.geoid
WHERE c.state = 'GA' AND c.median_hh_income_cv < 0.10
ORDER BY pct_vs_state DESC LIMIT 5;
```

→ `Forsyth County, Georgia | 143784 | 77353 | 85.9`, `Oconee County, Georgia |
121217 | 77353 | 56.7`, `Fayette County, Georgia | 111978 | 77353 | 44.8`,
`Cherokee County, Georgia | 108115 | 77353 | 39.8`, `Bryan County, Georgia |
103408 | 77353 | 33.7`.

`substr(geoid, 1, 2)` is the whole join: a county GEOID is state FIPS + county
FIPS, so the first two characters *are* the state row's `geoid`. The same
prefix trick reaches down as well as up — `substr(tract_geoid, 1, 5)` is a
county — with one exception: Connecticut's rows here are the 9 planning regions
(`09110`–`09190`), so a 2020-vintage Connecticut block GEOID's prefix will not
match.

### Related recipes elsewhere

- The whole county table at once, including the quadrature-sum consistency
  check against the state row: [`counties/counties/AGENTS.md`](../counties/AGENTS.md).
- Income inside a county at tract scale, and the margin-overlap test where it
  bites much harder: [`tracts/tract-income/AGENTS.md`](../../tracts/tract-income/AGENTS.md).
- Income by race beside these overall medians, published far more often here
  than at tract level: [`counties/county-wellbeing/AGENTS.md`](../county-wellbeing/AGENTS.md).
- Choosing between the six county collections, and stepping up or down a
  geography: [`counties/AGENTS.md`](../AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, so no test above that reads a margin of error can be reproduced from
tiles — even though, unlike the finer collections, every zoom of this archive
holds real county polygons.
