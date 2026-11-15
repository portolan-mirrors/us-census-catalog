# Agent guide — People & Education (States)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Who lives here: median age and the shares under 18 and 65 or over ([B01002](https://data.census.gov/table/ACSDT5Y2024.B01002), [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001)), the four mutually exclusive non-Hispanic race shares this catalog carries — White, Black or African American, American Indian and Alaska Native, Asian — plus Hispanic or Latino of any race and its complement, people of color ([B03002](https://data.census.gov/table/ACSDT5Y2024.B03002)), and the share of adults 25 and over holding a bachelor's degree or higher ([B15003](https://data.census.gov/table/ACSDT5Y2024.B15003)).

**56 rows** — the 50 states, the District of Columbia, Puerto Rico and the four
island areas — ACS 2020–2024 5-year estimates, geometry from the 2024
cartographic boundary files. **52 of the 56 carry ACS data**; the four island
areas carry geometry and NULLs.

Two things to know before using it. First, **this collection has no `_cv`
columns at all** (measured: zero columns matching `%_cv`), exactly as
[`tract-people`](../../tracts/tract-people/collection.json) has none — use
`<name>_moe` for reliability work here. Second, **eight of its margin columns
are NULL on every row**: `pct_under_18_moe`, `pct_65_plus_moe`, and the margins
of all six race-and-ethnicity shares (the four non-Hispanic races,
`pct_hispanic` and `pct_people_of_color`). Only `median_age_moe` and
`pct_bachelors_plus_moe` are
populated, on all 52 rows with data. That is the single most important fact in
this file, and recipe 1 measures it.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.pmtiles`, layer `state-people`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/collection.json` — carries a full description for every column

This is a themed cut of the wide 112-column table, which is published beside it
as the sixth collection in this group and holds the same 56 rows and the same
geometry: `https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet`
(its data files sit one directory up, beside the group's `catalog.json`). At
this geography the chunking buys almost nothing on download — `geometry` is
3.86 MB of a 3.88 MB themed file (measured from the Parquet column metadata),
and the wide table is only about 49 KB larger. Choose a chunk for a narrower
schema, not to save bandwidth.

## Source tables

| table | title | universe |
|---|---|---|
| [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001) | Sex by Age | Total population |
| [B01002](https://data.census.gov/table/ACSDT5Y2024.B01002) | Median Age by Sex | Total population |
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) | Hispanic or Latino Origin by Race | Total population |
| [B15003](https://data.census.gov/table/ACSDT5Y2024.B15003) | Educational Attainment for the Population 25 Years and Over | Population 25 years and over |

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

- **Eight `*_moe` columns in this collection are NULL on all 56 rows**
  (measured): `population_moe`, `pct_under_18_moe`, `pct_65_plus_moe`,
  `pct_white_nh_moe`, `pct_black_moe`, `pct_native_moe`, `pct_asian_moe`,
  `pct_hispanic_moe` and `pct_people_of_color_moe` — nine, counting
  `population_moe`. Every one of them is a count of, or a share of, the total
  population, and `population_moe` itself has no value at this geography; the
  build writes NULL rather than a guess when an input margin is NULL
  (`tools/column_docs.py`), so the shares inherit the gap. `median_age_moe` and
  `pct_bachelors_plus_moe` are populated on all 52 rows with data.
- **That NULL is upstream, and it is not suppression.** Each of those columns
  comes from a total-population table (B01001, B01003, B03002), and in the release's own
  `.dat` files those rows carry the estimate beside `-555555555`, the
  **controlled-MOE** jam value a controlled estimate gets in place of a
  sampling margin — `0400000US06|39287377|-555555555` in
  `staging/census-cache/acsdt5y2024-b01003.dat`, read 2026-11-15. The build
  turns it into NULL rather than publishing it as a number
  (`tools/build_acs.py`). The same columns carry margins normally at the finer
  geographies, where the estimates are not controlled this way:
  `population_moe` is carried on 33,759 of 33,791 ZCTAs and on all 241,854
  populated block groups (measured).
- **There are no `_cv` columns in this collection** (measured). The two
  populated margins are the reliability tool here, and at this geography they
  are small: 0.1–0.2 years on `median_age` and 0.13–0.87 points on
  `pct_bachelors_plus` across the 52 rows with data (measured).
- **The four race shares are all non-Hispanic**, drawn from B03002's "Not
  Hispanic or Latino" branch, so they and `pct_hispanic` are mutually exclusive
  and do not double-count. **They are also not exhaustive**: the four race
  shares plus `pct_hispanic` sum to between 69.12 and 99.78 across the 52 rows
  with data (measured — Hawaii is the 69.12), because B03002's remaining
  non-Hispanic categories (Native
  Hawaiian and Other Pacific Islander alone, Some other race alone, Two or more
  races) are not published here. Never treat the gap as an error or redistribute
  it.
- **`pct_people_of_color` is a complement** (`100 − pct_white_nh`), and it holds
  exactly on all 52 rows with data (measured). It, not the sum of the four
  shares, is the exhaustive non-White-alone-non-Hispanic figure.
- **`pct_bachelors_plus` divides by the population 25 and over**, not by
  everyone, and counts bachelor's, master's, professional-school and doctorate
  attainment (B15003 lines 22–25). Associate's degrees are deliberately
  excluded.
- **`median_age` is the single median of B01002 line 1.** Like every median it
  cannot be aggregated: there is no way to combine state medians into a
  national one.
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
  [`state-housing`](../state-housing/AGENTS.md) — but medians and rates do not.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area, and neither number is wrong.

## Data quality

Columns with notable missingness at this geography (measured over the file as
built, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 4 of 56 rows (7.14%): American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have boundaries here but no ACS 5-year data, because the island areas run a separate decennial-only program. 52 rows carry data. |
| every estimate column | NULL on exactly the same 4 rows. Nothing in this collection is suppressed: `median_age`, both age shares, all six race shares and `pct_bachelors_plus` are each published on all 52 rows with data (measured). |
| `population_moe`, `pct_under_18_moe`, `pct_65_plus_moe`, `pct_white_nh_moe`, `pct_black_moe`, `pct_native_moe`, `pct_asian_moe`, `pct_hispanic_moe`, `pct_people_of_color_moe` | NULL on all 56 rows — see the field notes. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern
Mariana Islands and the U.S. Virgin Islands have cartographic boundaries but no
ACS 5-year estimates, so their rows publish with NULL values rather than being
dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 17
ZCTAs, 279 places and 4 delegate districts.

The margins that exist are small, and the rankings they support are still
weaker than they look: Vermont's 43.79% bachelor's share and New Jersey's
43.63% have overlapping 90% intervals (measured — recipe 4), so ranks 2 and 3
in that ladder are a tie. Reliability of a single value and significance of a
comparison are different questions. For the race shares there is no margin at
all at this geography, so a difference between two states on `pct_asian` cannot
be tested from this file.

The PMTiles archive is real state polygons at every zoom, band `0-8:geom`
(`tools/make_tiles.py`) — there is no coarser-geography band at coarse zooms,
because 56 features tile directly. `*_moe` columns are excluded from every tile
at every zoom. Statistics come from the GeoParquet, always.

## Related collections

- [`states/state-income`](../state-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`states/state-housing`](../state-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`states/state-connectivity`](../state-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`states/state-wellbeing`](../state-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`states/states`](../states/collection.json) ([agent guide](../states/AGENTS.md)) — the sixth sibling: all 112 columns in one table, same 56 rows, data files one directory up.
- [`counties/county-people`](../../counties/county-people/collection.json), [`tracts/tract-people`](../../tracts/tract-people/collection.json) and [`block-groups/bg-people`](../../block-groups/bg-people/collection.json) — the same theme at finer geographies.
- [`zctas/zcta-people`](../../zctas/zcta-people/collection.json), [`places/place-people`](../../places/place-people/collection.json), [`congressional-districts/cd-people`](../../congressional-districts/cd-people/collection.json) — the same theme at the other statistical geographies.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, including race and Hispanic-origin counts from a complete enumeration rather than a sample. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

Instead, the cost: 56 rows and 3.9 MB, of which 3.86 MB is geometry. No filter
is ever needed here for cost.

### 1. Which margins actually exist? (run this first)

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*)                       AS rows,
       count(population)              AS with_acs_data,
       count(median_age_moe)          AS median_age_moe,
       count(pct_bachelors_plus_moe)  AS degree_moe,
       count(pct_under_18_moe)        AS under_18_moe,
       count(pct_white_nh_moe)        AS white_nh_moe,
       count(pct_hispanic_moe)        AS hispanic_moe,
       count(pct_people_of_color_moe) AS poc_moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet';
```

→ `56 | 52 | 52 | 52 | 0 | 0 | 0 | 0`.

Two margins out of ten. `median_age_moe` and `pct_bachelors_plus_moe` are
published on every row that has data; the age shares and all six race shares
have **no margin at all** at this geography, because they divide by the total
population and `population_moe` is itself NULL on all 56 rows. So a
significance test on `pct_asian` cannot be run from this file, and a quadrature
sum over any of those columns returns NULL rather than a number. The estimates
themselves are complete:

```sql
LOAD httpfs;
SELECT name, median_age, median_age_moe, pct_under_18, pct_65_plus,
       pct_bachelors_plus, pct_bachelors_plus_moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet'
WHERE median_age IS NOT NULL
ORDER BY median_age DESC LIMIT 3;
```

→ `Puerto Rico | 44.8 | 0.2 | 16.12 | 23.44 | 29.8 | 0.31`,
`Maine | 44.8 | 0.1 | 18.05 | 22.37 | 36.19 | 0.45`,
`New Hampshire | 43.3 | 0.1 | 18.24 | 20.14 | 40.65 | 0.49`.

Puerto Rico and Maine tie at 44.8 years, and with margins of 0.2 and 0.1 the
tie is real rather than a rounding artefact. The youngest end, same query with
`ORDER BY median_age`: `Utah | 32.0 | 0.1 | 27.8 | 11.86`,
`District of Columbia | 34.9 | 0.1 | 18.69 | 12.79`,
`Texas | 35.6 | 0.1 | 24.99 | 13.44`. Utah and DC arrive at young medians two
different ways — one by children, one by their absence.

### 2. The race shares do not sum to 100, and that is correct

```sql
LOAD httpfs;
SELECT name,
       round(pct_white_nh + pct_black + pct_native + pct_asian + pct_hispanic, 2) AS five_shares,
       pct_people_of_color,
       round(100 - (pct_white_nh + pct_black + pct_native + pct_asian + pct_hispanic), 2) AS unaccounted
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet'
WHERE state IN ('HI','OK','CA','WV')
ORDER BY unaccounted DESC;
```

→ `Hawaii | 69.12 | 79.08 | 30.88`, `Oklahoma | 90.54 | 37.88 | 9.46`,
`California | 94.67 | 66.23 | 5.33`, `West Virginia | 95.74 | 10.32 | 4.26`.

Hawaii's four race shares plus `pct_hispanic` account for 69% of its
population. The missing
31 points are the non-Hispanic categories this collection does not publish —
Native Hawaiian and Other Pacific Islander alone, Some other race alone, and
Two or more races, all of which exist in
[B03002](https://data.census.gov/table/ACSDT5Y2024.B03002). Three rules follow:
never normalise these five columns to 100, never read the residual as "other" (it is
three distinct categories), and use `pct_people_of_color` when you need an
exhaustive split — it is the exact complement of `pct_white_nh`:

```sql
LOAD httpfs;
SELECT count(*) AS rows_with_data,
       count(*) FILTER (WHERE abs(pct_people_of_color - (100 - pct_white_nh)) < 0.005) AS complement_holds,
       max(round(100 - (pct_white_nh+pct_black+pct_native+pct_asian+pct_hispanic), 2)) AS max_unaccounted
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet'
WHERE pct_white_nh IS NOT NULL;
```

→ `52 | 52 | 30.88`. The complement holds on all 52 rows; the five-share gap
reaches 30.88 points.

### 3. Every county against its own state (GEOID prefix join)

```sql
LOAD httpfs;
SELECT c.name AS county, s.name AS state,
       c.pct_bachelors_plus AS county_degree, s.pct_bachelors_plus AS state_degree,
       round(c.pct_bachelors_plus - s.pct_bachelors_plus, 2) AS points_above_state
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet' c
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet' s
  ON s.geoid = substr(c.geoid, 1, 2)
WHERE c.pct_bachelors_plus IS NOT NULL AND s.pct_bachelors_plus IS NOT NULL
  AND c.population > 100000
ORDER BY points_above_state DESC LIMIT 5;
```

→ `Arlington County, Virginia | Virginia | 77.08 | 42.16 | 34.92`,
`Hamilton County, Indiana | Indiana | 61.9 | 29.47 | 32.43`,
`Williamson County, Tennessee | Tennessee | 62.69 | 31.06 | 31.63`,
`Delaware County, Ohio | Ohio | 59.43 | 31.49 | 27.94`,
`Washtenaw County, Michigan | Michigan | 58.71 | 32.45 | 26.26`.

`s.geoid = substr(c.geoid, 1, 2)` is the whole join — a county GEOID begins
with its state's FIPS code, and the same prefix reaches tracts and block
groups. This "each X against its own state" shape is what the state files are
for: they are the denominator every finer geography gets compared against. The
`population > 100000` gate keeps the list to places where 60% of adults with
degrees is a statement about a labour market rather than about a college town
of 9,000.

### 4. Is the gap between two states real? (margins, not estimates)

```sql
LOAD httpfs;
SELECT name, pct_bachelors_plus AS degree, pct_bachelors_plus_moe AS moe,
       round(pct_bachelors_plus - pct_bachelors_plus_moe, 2) AS lo,
       round(pct_bachelors_plus + pct_bachelors_plus_moe, 2) AS hi
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet'
WHERE state IN ('CO','VT','NJ','CT')
ORDER BY degree DESC;
```

→ `Colorado | 45.7 | 0.25 | 45.45 | 45.95`, `Vermont | 43.79 | 0.64 | 43.15 |
44.43`, `New Jersey | 43.63 | 0.23 | 43.4 | 43.86`,
`Connecticut | 42.48 | 0.33 | 42.15 | 42.81`.

Vermont [43.15–44.43] and New Jersey [43.40–43.86] overlap, so their ranks are
not separable; Colorado's and Connecticut's intervals clear everything else.
Vermont's margin is nearly three times New Jersey's on a similar estimate —
small states have small samples, and the margin is the only column that tells
you so, because this collection has no `_cv`.

### 5. Education against income (1:1 sibling join)

```sql
LOAD httpfs;
SELECT round(corr(p.pct_bachelors_plus, i.median_hh_income), 3) AS r_degree_income,
       round(corr(p.median_age, i.median_hh_income), 3)         AS r_age_income,
       round(corr(p.pct_65_plus, i.pct_below_poverty), 3)       AS r_65_poverty,
       count(*)                                                 AS rows_used
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet' p
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet' i
  USING (geoid)
WHERE p.pct_bachelors_plus IS NOT NULL AND i.median_hh_income IS NOT NULL;
```

→ `0.772 | -0.243 | 0.279 | 52`.

The join is 1:1 on `geoid` — all six collections in this group hold the same 56
rows. Degree share and median income move together strongly across the 52
states; age and income barely at all. Read `rows_used` every time: 52 is the
whole population of states with data, so this is a complete-enumeration
correlation over a tiny N, not a sample statistic, and one outlier moves it.
The bottom of the degree ranking, for the same join:

```sql
LOAD httpfs;
SELECT p.name, p.pct_bachelors_plus AS degree, i.median_hh_income::int AS income,
       p.median_age, i.pct_below_poverty AS poverty
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet' p
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet' i
  USING (geoid)
WHERE p.pct_bachelors_plus IS NOT NULL
ORDER BY p.pct_bachelors_plus LIMIT 5;
```

→ `West Virginia | 24.13 | 59608 | 42.7 | 16.71`,
`Mississippi | 25.13 | 56447 | 38.6 | 18.9`,
`Arkansas | 25.73 | 60773 | 38.5 | 15.99`,
`Louisiana | 27.04 | 60756 | 38.0 | 18.93`,
`Kentucky | 27.55 | 63726 | 39.1 | 16.06`.

### Related recipes elsewhere

- Point-in-polygon lookups and the race-share distributions at the geography
  small-area research is done at:
  [`tracts/tract-people/AGENTS.md`](../../tracts/tract-people/AGENTS.md).
- The same columns at county level, with every county against its state:
  [`counties/county-people/AGENTS.md`](../../counties/county-people/AGENTS.md).
- Income and poverty beside these columns, including the state-median trap:
  [`states/state-income/AGENTS.md`](../state-income/AGENTS.md).
- All 112 state columns in one table, with recipes timed against the published
  mirror: [`states/states/AGENTS.md`](../states/AGENTS.md).
- What this geography is for and when to step down from it:
  [`states/AGENTS.md`](../AGENTS.md).

Statistics come from the GeoParquet. The state PMTiles archive is real polygons
at every zoom — it needs no coarser-geography band — but carries no `*_moe`
columns, so none of the margin arithmetic above can be reproduced from tiles.
