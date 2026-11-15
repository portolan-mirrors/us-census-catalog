# Agent guide — People & Education (Places & CDPs)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Who lives here: median age and the shares under 18 and 65 or over ([B01002](https://data.census.gov/table/ACSDT5Y2024.B01002), [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001)), the four mutually exclusive non-Hispanic race shares this catalog carries — White, Black or African American, American Indian and Alaska Native, Asian — plus Hispanic or Latino of any race and its complement, people of color ([B03002](https://data.census.gov/table/ACSDT5Y2024.B03002)), and the share of adults 25 and over holding a bachelor's degree or higher ([B15003](https://data.census.gov/table/ACSDT5Y2024.B15003)).

**32,612 rows**, one per place, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

This is also the chunk you reach for when someone names a city, because `name` is here and `name` is how a human asks. It is the place to say what that costs: "Place" covers both incorporated places (cities, towns, villages, boroughs) and [census designated places](https://www.census.gov/programs-surveys/bas/information/cdp.html), **12,592 of the 32,612 rows are CDPs** (38.61%, measured), **23 rows** have a name beginning "Springfield" and **13** of them are literally "Springfield city" (measured, recipe 1). `geoid` is the stable key; `name` is a search term.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.pmtiles`, layer `place-people`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/collection.json` — carries a full description for every column

This is a themed cut of the wide 112-column place table, which is published as the sixth sibling in this group: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet` ([agent guide](../places/AGENTS.md)). Same 32,612 rows, same geometry, every column below included — reach for it when a question crosses themes, and for this one when it does not.

## Source tables

| table | title | universe |
|---|---|---|
| [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001) | Sex by Age | Total population |
| [B01002](https://data.census.gov/table/ACSDT5Y2024.B01002) | Median Age by Sex | Total population |
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) | Hispanic or Latino Origin by Race | Total population |
| [B15003](https://data.census.gov/table/ACSDT5Y2024.B15003) | Educational Attainment for the Population 25 Years and Over | Population 25 years and over |

## Schema

`geoid` is 7 characters — state FIPS (2) + place FIPS (5) — and `substr(geoid, 1, 2)` is the only prefix join it supports, to [`states/state-people`](../../states/state-people/collection.json). Places nest in states but not in counties (a place can straddle a county line) and a place is not an aggregate of tracts or block groups, so there is no prefix path to the finer collections. The five themed siblings and the wide table all carry the same 32,612 `geoid` values, so `JOIN … USING (geoid)` is 1:1.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 7-character place GEOID: state FIPS 2 + place FIPS 5, e.g. `0644000` for Los Angeles city. |
| `name` | string | `NAMELSAD`, `STATE_NAME` from the 2024 cartographic boundary place file — "Los Angeles city, California", "Brentwood CDP, New York". The descriptor in the name says whether the place is a city, town, village, borough or CDP. |
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

- **This collection has no `*_cv` columns at all.** Every other themed place
  chunk carries a few; this one carries none, because none of its columns is
  one of the catalog's headline statistics. Gate on `<name>_moe` here, and on
  `population`. A share whose `_moe` exceeds 100 points is noise, not a value
  — see recipe 3, where the unfiltered top five all read 100.0% with margins
  from 48 to 201 points.
- **`geoid` is the stable key; `name` is a search term.** `name` is
  `NAMELSAD` plus the state name, so a place's type is inside its name and
  duplicate names are everywhere: 23 rows begin "Springfield", 11 contain
  "Louisville". Resolve a name to a `geoid` once (recipe 1), then use the
  `geoid`. Puerto Rico's descriptors are `zona urbana` and `comunidad`, so a
  filter written around "city" or "town" silently drops the island.
- **Louisville is `2148006`,** the consolidated Louisville/Jefferson County
  metro government (balance). `2148000` "Louisville city" is still in the
  boundary file and has no ACS row, so it publishes with NULL values — the trap
  is exactly a name search landing on the dead row. The full worked case is in
  [`../AGENTS.md`](../AGENTS.md).
- **Places are not a partition of the country.** Do not sum place rows to a
  state or national total, and do not read "the land outside places" out of
  this file — it is absent, not zero. A population-weighted average over
  places is not a national average either, because the land between them is
  missing.
- **Most rows are small.** 16,463 places have under 1,000 people and 883 have
  50,000 or more (measured). The median place's `median_age` is 41.2 over all
  places and 37.7 over places of 20,000+, and the median
  `pct_bachelors_plus` 20.59 against 34.99 (measured, recipe 2). An unfiltered
  place-level distribution is a distribution of hamlets.
- **282 places carry geometry and no ACS data**: 279 in the island areas
  (MP 135, AS 77, GU 57, VI 10, measured), Brentwood CDP and Wyandanch CDP in
  Suffolk County, New York, and Louisville city. `ORDER BY … DESC` needs
  `NULLS LAST`.
- **Every estimate has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. To compare two places, check whether
  their margins overlap before calling a difference real. To sum estimates
  across geographies, add the margins in quadrature (`sqrt(sum(moe*moe))`).
  **Never sum or average a median**: a median of a region is not derivable
  from the medians of its parts, and `median_age` is a median.
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
- **The four race shares this file carries are all non-Hispanic** —
  `pct_white_nh`, `pct_black`, `pct_native`, `pct_asian` — drawn from B03002's "Not
  Hispanic or Latino" branch, so they and `pct_hispanic` are mutually
  exclusive and do not double-count. They do not sum to 100: B03002's
  "Native Hawaiian and Other Pacific Islander", "Some other race" and "Two or
  more races" non-Hispanic branches are not published here.
- **`pct_people_of_color` is a complement** (`100 − pct_white_nh`) and carries
  `pct_white_nh`'s margin of error unchanged — a share and its complement have
  the same sampling error.
- **The margins on these columns exist here and barely exist above here.**
  Measured, `population_moe` is populated on **32,267 of 32,612 places** and
  every share built on a total-population table —`pct_under_18_moe`,
  `pct_65_plus_moe`, the four race-share margins, `pct_hispanic_moe`,
  `pct_people_of_color_moe` — on **31,755**. The same columns are populated on
  only **132 of 3,235 counties** and **none of the 56 states**. So this is one
  of the few levels where an age or race share can be given an interval at
  all; stepping up to counties or states buys a cleaner estimate and loses the
  margin entirely.
- **`pct_bachelors_plus` excludes associate's degrees** deliberately: it is
  B15003 lines 22–25 (Bachelor's, Master's, Professional school, Doctorate)
  over line 1, and its universe is the population 25 and over, not everyone.
- **`median_age` is the combined median** (B01002 line 1); the male and female
  medians on lines 2 and 3 are not published here.
- **`pct_under_18` and `pct_65_plus` come from B01001's age bands**, and the
  shares between them are not published, so the two do not describe the whole
  age distribution.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.86% of places — the 282 rows with 2024 boundaries and no ACS tabulation. Every other column is NULL on at least those rows. |
| `population_moe` | NULL on 1.06% of places (345 rows, measured): the 282 data-free rows plus 63 more where the margin itself is not published. |
| `median_age` | NULL on 3.77% of places (measured) — the sparsest column here, because a median needs a distribution and the smallest places do not supply one. |
| `pct_bachelors_plus` | NULL on 2.50% of places (measured): no population 25 and over, or a suppressed denominator. |
| `pct_under_18`, `pct_65_plus`, the four race shares, `pct_hispanic`, `pct_people_of_color` | NULL on 2.43% of places each (measured) — all share B01001/B03002's total-population denominator, so they fail together. |

Nothing in this collection is suppressed the way a median is: these are shares of a total population, so the only NULLs are the data-free rows plus places whose denominator came out at 0. That makes this the **least holey** of the five themed place chunks, and the one safe place to start a place-level question — but the margins are still place-level margins, and 2.43% of rows missing is not 0%.

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 279 places here, plus 4 states, 13 county equivalents, 126 tracts and 405 block groups elsewhere in the catalog.

Three more places have boundaries and no ACS row: `3608026` Brentwood CDP and `3683294` Wyandanch CDP, left without an ACS match by the 2024 re-delineation of Suffolk County, New York, and `2148000` Louisville city, whose ACS tabulation is the consolidated `2148006` metro government. Running the other way, every one of the 32,330 ACS-tabulated places matched a polygon.

Row count is the 2024 cartographic boundary place file's own feature count, 32,612. For scale, the Census Bureau's [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html) give 19,734 incorporated places and 12,454 census designated places (32,188) for the 2020 vintage; the 2024 vintage is four years of incorporations, dissolutions and CDP re-delineations later.

Spot-checked against data.census.gov: Los Angeles city population 3,857,263; New York city 8,483,844.

PMTiles coarse zooms are a different census geography from this collection's: z0–z5 are **counties**, carrying the Census Bureau's own county estimates for these same columns, and z6–z12 are the places themselves. The county band is national orientation, not a roll-up of this file — places do not tile a county. `*_moe` columns are not in the tiles. Statistics come from the GeoParquet.

## Related collections

- [`places/place-income`](../place-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`places/place-housing`](../place-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`places/place-connectivity`](../place-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`places/place-wellbeing`](../place-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1 — and the place to go for income by race, which is not here.
- [`places/places`](../places/collection.json) — the wide 112-column place table, the sixth sibling: every column of all five themes in one file.
- [`counties/county-people`](../../counties/county-people/collection.json) and [`states/state-people`](../../states/state-people/collection.json) — the same theme at geographies that **do** tile the country.
- [`tracts/tract-people`](../../tracts/tract-people/collection.json) and [`block-groups/bg-people`](../../block-groups/bg-people/collection.json) — the same theme inside a city, at geographies that tile it.
- [`zctas/zcta-people`](../../zctas/zcta-people/collection.json) and [`congressional-districts/cd-people`](../../congressional-districts/cd-people/collection.json) — the same theme at the catalog's other non-nesting geographies.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, including age and race counts from a different survey and vintage, with no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted. For
scale instead: the file is **27.9 MB** over **32,612 rows**.

### 1. Finding the place somebody named

```sql
INSTALL httpfs; LOAD httpfs;
SELECT geoid, name, population, median_age
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.parquet'
WHERE name LIKE 'Springfield %'
ORDER BY population DESC NULLS LAST LIMIT 8;
```

→ `2970000 | Springfield city, Missouri | 169954 | 33.7`, `2567000 |
Springfield city, Massachusetts | 154749 | 33.7`, `1772000 | Springfield city,
Illinois | 113330 | 41.0`, `4169600 | Springfield city, Oregon | 61499 | 37.4`,
`3974118 | Springfield city, Ohio | 58190 | 37.9`, `5174592 | Springfield CDP,
Virginia | 31154 | 41.6`, `4770500 | Springfield city, Tennessee | 19255 |
34.5`, `1268275 | Springfield city, Florida | 8230 | 38.0`.

```sql
LOAD httpfs;
SELECT count(*) AS name_starts_springfield,
       count(*) FILTER (WHERE name LIKE 'Springfield city,%') AS springfield_city
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.parquet'
WHERE name LIKE 'Springfield %';
```

→ `23 | 13`.

Thirteen places are called "Springfield city" and ten more are Springfield
something-else, so "Springfield" is not an identifier. The `name` column is
`NAMELSAD` plus `STATE_NAME`, which means the state is already in the string —
`WHERE name = 'Springfield city, Illinois'` resolves exactly, and
`WHERE name LIKE 'Springfield %' AND state = 'IL'` resolves a near-miss.
Resolve once, read the `geoid`, and use the `geoid` from then on: it is stable
across the themed siblings, the wide table and the PMTiles archive, while a
name is one re-delineation away from changing. `ORDER BY … DESC NULLS LAST` is
required because 282 places have boundaries and no ACS data and would
otherwise sort first.

### 2. The place-level distribution is a distribution of hamlets

```sql
LOAD httpfs;
SELECT 'all places' AS universe, count(median_age) AS n,
       round(quantile_cont(median_age, 0.10), 1)        AS age_p10,
       round(quantile_cont(median_age, 0.50), 1)        AS age_p50,
       round(quantile_cont(median_age, 0.90), 1)        AS age_p90,
       round(quantile_cont(pct_bachelors_plus, 0.50), 2) AS degree_p50
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.parquet'
UNION ALL
SELECT 'population >= 20,000', count(median_age),
       round(quantile_cont(median_age, 0.10), 1),
       round(quantile_cont(median_age, 0.50), 1),
       round(quantile_cont(median_age, 0.90), 1),
       round(quantile_cont(pct_bachelors_plus, 0.50), 2)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.parquet'
WHERE population >= 20000;
```

→ `all places | 31384 | 31.0 | 41.2 | 58.1 | 20.59`,
`population >= 20,000 | 2327 | 32.3 | 37.7 | 44.3 | 34.99`.

The median place's median age is 41.2 and its degree share 20.59%. The median
place **of 20,000 or more people** is 37.7 and 34.99%. The unfiltered spread is
also four times wider at the tails — 31.0 to 58.1 against 32.3 to 44.3 —
because the long right tail is retirement villages and the long left tail is
campus CDPs. Decide which universe the question is about and say so in the
answer; "the typical American city" is the second row, not the first.

### 3. What an unfiltered ranking returns (and the `_moe` gate that fixes it)

```sql
LOAD httpfs;
SELECT geoid, name, population, pct_bachelors_plus AS degree, pct_bachelors_plus_moe AS moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.parquet'
ORDER BY pct_bachelors_plus DESC NULLS LAST LIMIT 5;
```

→ `4202072 | Allport CDP, Pennsylvania | 93 | 100.0 | 147.78`, `1744784 |
Lorenzo CDP, Illinois | 28 | 100.0 | 80.42`, `7254688 | Monte Verde comunidad,
Puerto Rico | 19 | 100.0 | 136.74`, `4841542 | Lasana CDP, Texas | 54 | 100.0 |
48.11`, `4880724 | Zarate CDP, Texas | 146 | 100.0 | 200.66`.

Five places of 19 to 146 people where 100% of adults hold a degree, with
margins of error of 48 to **201 percentage points**. A margin of 200 on a
0–100 scale is the ACS telling you it has no information; the estimate is a
handful of survey responses. Published, correct, and useless.

The same question, asked properly:

```sql
LOAD httpfs;
SELECT geoid, name, population, pct_bachelors_plus AS degree, pct_bachelors_plus_moe AS moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.parquet'
WHERE population > 50000 AND pct_bachelors_plus_moe < 3
ORDER BY pct_bachelors_plus DESC LIMIT 5;
```

→ `2407125 | Bethesda CDP, Maryland | 69397 | 87.07 | 1.51`, `0655282 | Palo
Alto city, California | 67237 | 82.31 | 2.53`, `0617610 | Cupertino city,
California | 58566 | 82.25 | 2.76`, `2545560 | Newton city, Massachusetts |
89044 | 81.14 | 2.45`, `2511000 | Cambridge city, Massachusetts | 118796 |
80.78 | 1.97`.

Both gates do work. The population floor removes the 19-person CDPs; the
`_moe` gate removes the places that are large but still thinly sampled on this
particular column. This collection has **no `_cv` columns**, so `_moe` is the
only reliability handle it offers — and note that the top row is a CDP, so
"city" is not the filter you want either.

### 4. Education against income, one state (sibling join)

```sql
LOAD httpfs;
SELECT p.name, p.population, p.pct_bachelors_plus AS degree,
       i.median_hh_income::int AS income, round(i.median_hh_income_cv, 3) AS income_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.parquet' p
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet' i
  USING (geoid)
WHERE p.state = 'CO' AND p.population > 30000 AND i.median_hh_income_cv < 0.08
ORDER BY p.pct_bachelors_plus DESC LIMIT 5;
```

→ `Boulder city, Colorado | 106433 | 76.8 | 87493 | 0.043`, `Erie town,
Colorado | 33808 | 69.63 | 173349 | 0.035`, `Highlands Ranch CDP, Colorado |
102257 | 67.84 | 159307 | 0.018`, `Lafayette city, Colorado | 30602 | 63.48 |
119040 | 0.052`, `Centennial city, Colorado | 108201 | 62.57 | 131928 |
0.027`.

The join is 1:1 on `geoid` — all six place collections hold the same 32,612
rows. Boulder tops the state on degrees and sits **last of these five on
income**, $87,493 against Erie's $173,349: a university town's adults are
highly educated and a large share of them are students. The `_cv` gate comes
from the income side, because `place-people` has none of its own; borrowing a
sibling's `_cv` for a reliability gate is legitimate only for the sibling's own
column, which is what is happening here.

### 5. The race shares, and who the largest places actually are

```sql
LOAD httpfs;
SELECT geoid, name, population, pct_hispanic, pct_hispanic_moe AS moe, pct_white_nh
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.parquet'
WHERE population > 100000
ORDER BY pct_hispanic DESC LIMIT 5;
```

→ `7263820 | Ponce zona urbana, Puerto Rico | 107805 | 99.24 | 0.24 | 0.32`,
`7206593 | Bayamón zona urbana, Puerto Rico | 166923 | 99.07 | 0.07 | 0.35`,
`7214290 | Carolina zona urbana, Puerto Rico | 138633 | 98.53 | 0.4 | 0.85`,
`7276770 | San Juan zona urbana, Puerto Rico | 317995 | 98.15 | 0.32 | 1.15`,
`0620802 | East Los Angeles CDP, California | 111647 | 95.52 | 0.75 | 2.17`.

Four of the top five are Puerto Rico's `zona urbana` places and the fifth is a
CDP, so a query that filtered `name LIKE '%city%'` would return none of them.
The margins here are a fraction of a point, which is what a large place looks
like on a share column. `pct_hispanic` and `pct_white_nh` are mutually
exclusive — the race shares are all drawn from B03002's non-Hispanic branch —
but they and the other three do **not** sum to 100 (the median place's five
shares sum to 96.7, measured), because B03002's
non-Hispanic "Pacific Islander", "Some other race" and "Two or more races"
branches are not published here. `100 − pct_white_nh` is published as
`pct_people_of_color` and carries `pct_white_nh_moe` unchanged.

### Related recipes elsewhere

- The 11 Louisvilles, the consolidated-city trap and the one-row cross-theme
  profile: [`places/AGENTS.md`](../AGENTS.md).
- The same columns beside all 107 others, with wall-clock timings against the
  mirror: [`places/places/AGENTS.md`](../places/AGENTS.md).
- Income by place, the population-floor argument measured by size band, and the
  margin-overlap test:
  [`places/place-income/AGENTS.md`](../place-income/AGENTS.md).
- Income by race at place level, and the campus CDPs with zero households:
  [`places/place-wellbeing/AGENTS.md`](../place-wellbeing/AGENTS.md).
- "Which tract am I in" point-in-polygon with a `bbox` prefilter, the pattern
  to use for a place too:
  [`tracts/tract-people/AGENTS.md`](../../tracts/tract-people/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns — and this collection has no `*_cv` columns either, so the tiles carry
no reliability information at all — and its z0–z5 features are counties rather
than places. Nothing above can be reproduced from tiles.
