# Agent guide — People & Education (Counties)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Who lives here: median age and the shares under 18 and 65 or over ([B01002](https://data.census.gov/table/ACSDT5Y2024.B01002), [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001)), the four mutually exclusive non-Hispanic race shares this catalog carries — White, Black or African American, American Indian and Alaska Native, Asian — plus Hispanic or Latino of any race and its complement, people of color ([B03002](https://data.census.gov/table/ACSDT5Y2024.B03002)), and the share of adults 25 and over holding a bachelor's degree or higher ([B15003](https://data.census.gov/table/ACSDT5Y2024.B15003)).

**3,235 rows**, one per county or county equivalent, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

Nothing in this chunk is suppressed for sample size: every estimate column is NULL on exactly the 13 island-area rows that have boundaries and no ACS tabulation (0.40%, measured). The catch at this geography is not the estimates — it is the **margins**: eight of the ten share margins here are NULL on 3,103 of the 3,235 rows, the same rows where `population_moe` is missing.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.pmtiles`, layer `county-people`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/collection.json` — carries a full description for every column

This is one themed cut of the county table. The same rows with all 112 columns — every theme at once, no join — are the sixth sibling in this group, [`counties/counties`](../counties/collection.json), whose data files sit one directory up at `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet` (and `.pmtiles`).

## Source tables

| table | title | universe |
|---|---|---|
| [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001) | Sex by Age | Total population |
| [B01002](https://data.census.gov/table/ACSDT5Y2024.B01002) | Median Age by Sex | Total population |
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) | Hispanic or Latino Origin by Race | Total population |
| [B15003](https://data.census.gov/table/ACSDT5Y2024.B15003) | Educational Attainment for the Population 25 Years and Over | Population 25 years and over |

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
| `geometry` | binary | Boundary polygon, WKB, EPSG:4326 / OGC:CRS84. |
| `bbox` | struct<xmin, ymin, xmax, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, with row-group statistics. |

## Field notes

- **This chunk has no `_cv` columns at all** — use `_moe`, and read the next
  bullet before you do.
- **Most of the margins here are NULL on 3,103 of the 3,235 rows.** Measured:
  `population_moe`, `pct_under_18_moe`, `pct_65_plus_moe`,
  `pct_white_nh_moe`, `pct_black_moe`, `pct_native_moe`, `pct_asian_moe`,
  `pct_hispanic_moe` and `pct_people_of_color_moe` are NULL on **exactly the
  same 3,103 rows** — all 3,235 rows agree on the pattern, verified — leaving
  132 small rural counties that carry them. Those nine are precisely the
  columns denominated on a total-population line (`B01001` line 1 for the age
  shares, `B03002` line 1 for the race shares, as `tools/column_docs.py`
  records), and `population` itself carries no margin at this geography. The
  two that do survive are `median_age_moe` (3,222 rows, i.e. every row with
  ACS data) and `pct_bachelors_plus_moe` (3,123 rows), which is denominated on
  `B15003` line 1, the population 25 and over.
- **So a significance test on a race or age share is not available for most
  counties here.** When one is needed, ask the question at state level, where
  the same columns are 52 rows wide, or use the estimates as point values and
  say so. Do not read a NULL margin as a zero margin, and never write
  `sqrt(sum(moe*moe))` over one of these columns without a NULL check —
  quadrature over a NULL-bearing column returns NULL.
- **Estimates themselves are complete.** Every value column in this chunk is
  published on all 3,222 rows that carry ACS data.
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **`pct_people_of_color` is a complement** (`100 − pct_white_nh`) and carries
  `pct_white_nh`'s margin of error unchanged. Measured: the two shares sum to
  exactly 100.00 on all 3,222 rows with data, and their margins are identical
  wherever both exist. It adds no information — it is there so a map can style
  it directly.
- **The non-Hispanic race shares carried here are `pct_white_nh`, `pct_black`,
  `pct_native` and `pct_asian`**, all drawn from B03002's "Not Hispanic or
  Latino" branch, so they and `pct_hispanic` are mutually exclusive and do not
  double-count. They also do not sum to 100: the remaining non-Hispanic lines
  of B03002 are not carried as columns. Measured, the five carried shares sum
  to a median of **96.09** and a minimum of **62.75**. Treat the remainder as
  "not broken out here", not as an error.
- **`pct_bachelors_plus` divides by the population 25 and over** (B15003 line
  1), not by everyone, and counts a bachelor's degree *or more* — so it
  includes master's, professional and doctorate degrees.
- **`median_age` is a median** and cannot be summed or averaged across
  counties, with or without weights.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area, and neither number is wrong.
- **Connecticut's county equivalents are the 9 planning regions**
  (`09110`–`09190`, measured) in the 2024 vintage, not the 8 historical
  counties. A 2020-vintage block or tract GEOID's 5-character prefix does not
  match these rows.

## Data quality

Columns with notable missingness at this geography, measured over this file:

| column | missingness |
|---|---|
| every estimate column (`median_age`, `pct_under_18`, `pct_65_plus`, the four race shares, `pct_hispanic`, `pct_people_of_color`, `pct_bachelors_plus`) | NULL on 0.40% of counties (13 rows) — the island-area county equivalents (AS 5, GU 1, MP 4, VI 3, measured), which have cartographic boundaries but no ACS 5-year estimates. Nothing else is suppressed. |
| `population_moe`, `pct_under_18_moe`, `pct_65_plus_moe`, `pct_white_nh_moe`, `pct_black_moe`, `pct_native_moe`, `pct_asian_moe`, `pct_hispanic_moe`, `pct_people_of_color_moe` | NULL on 95.92% of counties (3,103 of 3,235) — the same rows for all nine. |
| `pct_bachelors_plus_moe` | NULL on 3.46% of counties (112 rows). |
| `median_age_moe` | NULL on 0.40% (13 rows) — the island areas only. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

This is the one chunk at this geography where the data-quality story is about margins rather than estimates. A county-level race-share map is complete; a county-level claim that one county's race share differs from another's cannot be checked from this file for 96% of rows. Say which you are doing.

The PMTiles archive carries real county polygons at every zoom — the band is `0-10:geom`, there are few enough features to draw them all at a national zoom, so there is no coarser-geography band at coarse zooms the way the tract and block-group collections have one. `*_moe` columns are excluded from the tiles at every zoom. Statistics come from the GeoParquet, always.

## Related collections

- [`counties/county-income`](../county-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`counties/county-housing`](../county-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`counties/county-connectivity`](../county-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`counties/county-wellbeing`](../county-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1. Median household income **by race** lives there, not here.
- [`counties/counties`](../counties/collection.json) — the sixth sibling: all 112 columns in one wide table, same 3,235 rows, data files one directory up. Use it instead of a join when a question crosses three or more themes.
- The same theme at the other geographies: [`states/state-people`](../../states/state-people/collection.json), [`tracts/tract-people`](../../tracts/tract-people/collection.json), [`block-groups/bg-people`](../../block-groups/bg-people/collection.json), [`zctas/zcta-people`](../../zctas/zcta-people/collection.json), [`places/place-people`](../../places/place-people/collection.json), [`congressional-districts/cd-people`](../../congressional-districts/cd-people/collection.json).
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, including race and Hispanic origin counted rather than estimated. Different survey, different vintage, no margins of error — and the right source when the question is "how many", not "how precise".

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

For cost: this file is 12.3 MB over 3,235 rows, most of it geometry. Nothing
here needs a filter to be affordable.

### 1. The national distribution, and the oldest counties

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*) AS counties, count(median_age) AS published,
       quantile_cont(median_age, 0.10) AS p10,
       quantile_cont(median_age, 0.50) AS p50,
       quantile_cont(median_age, 0.90) AS p90,
       round(quantile_cont(pct_bachelors_plus, 0.10), 1) AS bach_p10,
       round(quantile_cont(pct_bachelors_plus, 0.50), 1) AS bach_p50,
       round(quantile_cont(pct_bachelors_plus, 0.90), 1) AS bach_p90
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet';
```

→ `3235 | 3222 | 35.8 | 41.7 | 48.5 | 14.4 | 22.3 | 38.7`.

The median county's median age is 41.7 and its degree share 22.3%. Both
distributions are right-skewed on the education side — the 90th percentile is
nearly three times the 10th — which is why the `styles/` class breaks for
`pct_bachelors_plus` are not equal-interval.

```sql
LOAD httpfs;
SELECT geoid, name, median_age, median_age_moe AS moe, population
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet'
WHERE population > 20000 ORDER BY median_age DESC LIMIT 5;
```

→ `12119 | Sumter County, Florida | 68.5 | 0.2 | 143408`, `12015 | Charlotte
County, Florida | 59.9 | 0.3 | 201064`, `53031 | Jefferson County, Washington |
59.8 | 0.4 | 33577`, `41015 | Curry County, Oregon | 57.7 | 1.1 | 23381`,
`26143 | Roscommon County, Michigan | 57.7 | 0.5 | 23737`.

`median_age_moe` is one of the two margins in this chunk that is populated for
every row with ACS data, and it is tight: Sumter County's 68.5 ± 0.2 is nearly
nine years clear of second place. Curry and Roscommon tie at 57.7 and their
margins (±1.1, ±0.5) overlap, so rank four and five are not separable.

### 2. Which margins actually exist here? (run this before any significance test)

```sql
LOAD httpfs;
SELECT count(*)                       AS counties,
       count(population_moe)          AS population_moe,
       count(median_age_moe)          AS median_age_moe,
       count(pct_white_nh_moe)        AS pct_white_nh_moe,
       count(pct_hispanic_moe)        AS pct_hispanic_moe,
       count(pct_65_plus_moe)         AS pct_65_plus_moe,
       count(pct_bachelors_plus_moe)  AS pct_bachelors_plus_moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet';
```

→ `3235 | 132 | 3222 | 132 | 132 | 132 | 3123`.

Measured, and it contradicts the catalog's general rule that every estimate
carries a margin. Four of these six margins exist for 132 counties out of
3,235. And it is the *same* 132 every time:

```sql
LOAD httpfs;
SELECT count(*) AS rows_where_all_nine_margins_agree_with_population_moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet'
WHERE (population_moe IS NULL) = (pct_under_18_moe IS NULL)
  AND (population_moe IS NULL) = (pct_65_plus_moe IS NULL)
  AND (population_moe IS NULL) = (pct_white_nh_moe IS NULL)
  AND (population_moe IS NULL) = (pct_black_moe IS NULL)
  AND (population_moe IS NULL) = (pct_native_moe IS NULL)
  AND (population_moe IS NULL) = (pct_asian_moe IS NULL)
  AND (population_moe IS NULL) = (pct_hispanic_moe IS NULL)
  AND (population_moe IS NULL) = (pct_people_of_color_moe IS NULL);
```

→ `3235` — every row agrees. The nine total-population-denominated margins
stand or fall together with `population_moe`. Use `median_age_moe` or
`pct_bachelors_plus_moe` when you need a county-level interval from this chunk,
and step up to [`states/state-people`](../../states/state-people/collection.json)
when the question needs an interval on a race share.

### 3. The complement and the sum, checked rather than assumed

```sql
LOAD httpfs;
SELECT count(*) FILTER (WHERE round(pct_people_of_color + pct_white_nh, 2) = 100.0) AS complement_exact,
       count(pct_white_nh)                                                          AS rows_with_data,
       round(quantile_cont(pct_white_nh + pct_black + pct_native
                           + pct_asian + pct_hispanic, 0.5), 2)                     AS median_sum_of_carried_shares,
       round(min(pct_white_nh + pct_black + pct_native
                 + pct_asian + pct_hispanic), 2)                                    AS min_sum
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet';
```

→ `3222 | 3222 | 96.09 | 62.75`.

Two facts worth keeping. `pct_people_of_color + pct_white_nh = 100.00` on all
3,222 rows with data, exactly — it is a complement, so it carries no
information `pct_white_nh` does not. And the five carried shares sum to a
median of 96.09, not 100: the rest of B03002's non-Hispanic branch is not
broken out into columns here. Do not normalise these five to 100 and do not
present the remainder as "other" — it is "not in this file".

### 4. Education against the income distribution (1:1 sibling join)

```sql
LOAD httpfs;
WITH j AS (
  SELECT ntile(5) OVER (ORDER BY i.median_hh_income) AS q,
         p.pct_bachelors_plus, p.median_age, p.pct_65_plus, p.pct_people_of_color
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet' i
  JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet' p
    USING (geoid)
  WHERE i.median_hh_income IS NOT NULL)
SELECT q AS income_quintile,
       round(avg(pct_bachelors_plus), 1)  AS bachelors_plus,
       round(avg(median_age), 1)          AS median_age,
       round(avg(pct_65_plus), 1)         AS pct_65_plus,
       round(avg(pct_people_of_color), 1) AS people_of_color
FROM j GROUP BY 1 ORDER BY 1;
```

→

```
1 | 17.6 | 42.7 | 21.4 | 43.5
2 | 20.4 | 42.3 | 21.2 | 25.1
3 | 23.0 | 42.1 | 21.1 | 21.6
4 | 26.3 | 41.8 | 20.6 | 21.4
5 | 36.2 | 40.7 | 18.2 | 28.7
```

The join is 1:1 on `geoid` — all six county collections hold the same 3,235
rows. The education gradient is monotone and steep: the richest fifth of
counties averages twice the degree share of the poorest fifth. The
people-of-color column is **not** monotone — highest in the poorest quintile
(43.5) and second-highest in the richest (28.7) — because both the rural South
and the expensive metros sit at the ends. A linear read of that column against
income would be wrong. Note also that `avg()` here averages *county* values,
one county one vote, which is not a population-weighted national figure.

### 5. Is one county's degree share really higher than another's?

```sql
LOAD httpfs;
SELECT name, pct_bachelors_plus AS degree, pct_bachelors_plus_moe AS moe,
       round(pct_bachelors_plus - pct_bachelors_plus_moe, 2) AS lo,
       round(pct_bachelors_plus + pct_bachelors_plus_moe, 2) AS hi
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet'
WHERE geoid IN ('51107', '24027');
```

→ `Howard County, Maryland | 64.46 | 1.43 | 63.03 | 65.89`, `Loudoun County,
Virginia | 64.55 | 1.02 | 63.53 | 65.57`.

Loudoun's estimate is 0.09 points above Howard's and the two 90% intervals sit
almost entirely on top of each other, so the two are indistinguishable. For
context, those are ranks four and five of the national list among counties over
50,000 people, which runs `51013` Arlington County, Virginia 77.08 ± 1.48,
`51510` Alexandria city, Virginia 66.16 ± 1.57, `51059` Fairfax County,
Virginia 64.99 ± 0.7, then this pair, then `11001` District of Columbia 64.25 ±
0.87 (measured). Arlington's lead is real; the four behind it are a cluster.
This test is only available because `pct_bachelors_plus_moe` is one of the two
populated margins here — the same check on a race share is impossible for 96%
of these rows.

### Related recipes elsewhere

- The whole county table at once: [`counties/counties/AGENTS.md`](../counties/AGENTS.md).
- The same columns at tract scale, where every margin is populated and a
  point-in-polygon lookup is the usual entry point:
  [`tracts/tract-people/AGENTS.md`](../../tracts/tract-people/AGENTS.md).
- Income by race, which is the other half of a race-and-income question:
  [`counties/county-wellbeing/AGENTS.md`](../county-wellbeing/AGENTS.md).
- Choosing between the six county collections, and stepping up or down a
  geography: [`counties/AGENTS.md`](../AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, so no test above that reads a margin of error can be reproduced from
tiles — even though, unlike the finer collections, every zoom of this archive
holds real county polygons.
