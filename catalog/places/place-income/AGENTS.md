# Agent guide — Income & Poverty (Places & CDPs)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Income, poverty and employment: median household income and per capita income ([B19013](https://data.census.gov/table/ACSDT5Y2024.B19013), [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301)), the share of people below the poverty line and below twice it ([C17002](https://data.census.gov/table/ACSDT5Y2024.C17002)), the share of households receiving SNAP ([B22010](https://data.census.gov/table/ACSDT5Y2024.B22010)), and the unemployment rate as a share of the civilian labor force ([B23025](https://data.census.gov/table/ACSDT5Y2024.B23025)), plus total population ([B01003](https://data.census.gov/table/ACSDT5Y2024.B01003)) and population density for context.

**32,612 rows**, one per place, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

"Place" means two things at once: incorporated places (cities, towns, villages, boroughs) and [census designated places](https://www.census.gov/programs-surveys/bas/information/cdp.html) — the Bureau's statistical stand-ins for unincorporated communities. **12,592 of the 32,612 rows (38.61%, measured) are CDPs**, and the `name` column's `NAMELSAD` descriptor says which. The median place has **959** people (measured): this file is mostly not cities, so a `population` filter belongs in almost every query here. See [`../AGENTS.md`](../AGENTS.md) for what that means across the group.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.pmtiles`, layer `place-income`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/collection.json` — carries a full description for every column

This is a themed cut of the wide 112-column place table, which is published as the sixth sibling in this group: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet` ([agent guide](../places/AGENTS.md)). Same 32,612 rows, same geometry, every column below included — reach for it when a question crosses themes, and for this one when it does not.

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

`geoid` is 7 characters — state FIPS (2) + place FIPS (5) — and `substr(geoid, 1, 2)` is the only prefix join it supports, to [`states/state-income`](../../states/state-income/collection.json). Places nest in states but not in counties (a place can straddle a county line) and a place is not an aggregate of tracts or block groups, so there is no prefix path to the finer collections. The five themed siblings and the wide table all carry the same 32,612 `geoid` values, so `JOIN … USING (geoid)` is 1:1.

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
| `geometry` | binary | Boundary polygon, WKB, EPSG:4326 / OGC:CRS84. |
| `bbox` | struct<xmin, ymin, xmax, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, with row-group statistics. |

## Field notes

- **Places are not a partition of the country.** Do not sum place rows to a
  state or national total, and do not read "the land outside places" out of
  this file — it is absent, not zero. For a total over an area, use
  [`counties`](../../counties/AGENTS.md) or [`states`](../../states/AGENTS.md).
- **Most rows are small.** The file runs from New York city (8,483,844 people)
  to 512 places reporting a population of exactly 0, with **16,463 places
  under 1,000 people** and only **883 at 50,000 or more** (measured). An
  unweighted mean or median over places describes hamlets, not the country:
  the median place's `median_hh_income` is $67,199 over all places and $83,683
  over places of 20,000+ (measured, recipe 1). Filter on `population` first.
- **Louisville is `2148006`,** the consolidated Louisville/Jefferson County
  metro government (balance). `2148000` "Louisville city" is still in the
  boundary file and has no ACS row, so it publishes with NULL values. Match by
  `geoid` where you can; see recipe 5.
- **282 places carry geometry and no ACS data**: 279 in the island areas
  (MP 135, AS 77, GU 57, VI 10, measured), Brentwood CDP and Wyandanch CDP in
  Suffolk County, New York, and Louisville city. Every column is NULL on those
  rows, so `ORDER BY … DESC` needs `NULLS LAST`.
- **Every estimate has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. To compare two places, check whether
  their margins overlap before calling a difference real (recipe 4). To sum
  estimates across geographies, add the margins in quadrature
  (`sqrt(sum(moe*moe))`). **Never sum or average a median**: a median of a
  region is not derivable from the medians of its parts.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. Filtering or greying out by CV is the intended use, and at this
  geography it is not optional: the median `median_hh_income_cv` is **0.139**,
  past the reliable line, against 0.125 at tract and 0.042 at county
  (measured, recipe 2).
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale. At this geography a margin can exceed 100 points on a
  percentage column; that is a flag to drop the row, not a value.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area, and neither number is wrong.
- **`pct_unemployed` divides by the civilian labor force** (B23025 line 3), not
  by the population 16 and over. That is what makes it an unemployment rate;
  Armed Forces members and people not in the labor force are excluded from
  both parts.
- **`pct_below_poverty`'s universe excludes some people entirely** — the
  population for whom poverty status is determined leaves out institutionalized
  people, people in military group quarters and college dormitories, and
  unrelated individuals under 15. At place level that matters: a campus CDP can
  be 100% group quarters (see
  [`place-wellbeing`](../place-wellbeing/AGENTS.md)) and have no households at
  all, which is why `median_hh_income` is NULL there rather than low.
- **`pct_snap` is receipt by the household**, not by individuals, and not a
  measure of current enrollment.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.86% of places — the 282 rows with 2024 boundaries and no ACS tabulation. Every other column is NULL on at least those rows. |
| `population_moe` | NULL on 1.06% of places (345 rows, measured): the 282 data-free rows plus 63 more where the margin itself is not published. The estimate is there and the margin is not, so a `_moe IS NOT NULL` filter is stricter than it looks. |
| `median_hh_income` | NULL on 12.71% of places (1.59% of tracts, 0.43% of counties, for comparison). The suppression is concentrated in small places: **22.6%** of places under 1,000 people against **0.0%** of places of 10,000 or more (measured, recipe 2). |
| `per_capita_income` | NULL on 4.28% of places. |
| `pct_below_poverty`, `pct_below_2x_poverty` | NULL on 2.56% of places each (measured) — no population for whom poverty status is determined, so no rate. |
| `pct_snap` | NULL on 2.76% of places. |
| `pct_unemployed` | NULL on 3.47% of places. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 279 places here, plus 4 states, 13 county equivalents, 126 tracts and 405 block groups elsewhere in the catalog.

Three more places have boundaries and no ACS row, and they are the geography's own gap rows rather than a territory artefact: `3608026` Brentwood CDP and `3683294` Wyandanch CDP, left without an ACS match by the 2024 re-delineation of Suffolk County, New York, and `2148000` Louisville city, whose ACS tabulation is the consolidated `2148006` metro government. Running the other way, every one of the 32,330 ACS-tabulated places matched a polygon, so nothing in the ACS release is missing from this file.

Row count is the 2024 cartographic boundary place file's own feature count, 32,612. For scale, the Census Bureau's [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html) give 19,734 incorporated places and 12,454 census designated places (32,188) for the 2020 vintage; the 2024 vintage is four years of incorporations, dissolutions and CDP re-delineations later.

Margins of error at this geography can be large relative to the estimate — larger than anywhere in the catalog except block groups. Use the `*_cv` columns to flag or grey out unreliable values; never compare two places without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: z0–z5 are **counties**, carrying the Census Bureau's own county estimates for these same columns, and z6–z12 are the places themselves. The county band is national orientation, not a roll-up of this file — places do not tile a county. `*_moe` columns are not in the tiles; `*_cv` columns are. Statistics come from the GeoParquet.

## Related collections

- [`places/place-people`](../place-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`places/place-housing`](../place-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`places/place-connectivity`](../place-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`places/place-wellbeing`](../place-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`places/places`](../places/collection.json) — the wide 112-column place table, the sixth sibling: every column of all five themes in one file, for cross-theme questions.
- [`counties/county-income`](../../counties/county-income/collection.json) and [`states/state-income`](../../states/state-income/collection.json) — the same theme at geographies that **do** tile the country, which is what you want for a total, and where the medians are far less suppressed.
- [`tracts/tract-income`](../../tracts/tract-income/collection.json) and [`block-groups/bg-income`](../../block-groups/bg-income/collection.json) — the same theme inside a city, at geographies that tile it.
- [`zctas/zcta-income`](../../zctas/zcta-income/collection.json) and [`congressional-districts/cd-income`](../../congressional-districts/cd-income/collection.json) — the same theme at the catalog's other non-nesting geographies.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted. For
scale instead: the file is **27.7 MB** over **32,612 rows**.

Two rules this geography enforces run through all five recipes: **places do
not tile the country** (never sum them to a state or national total) and
**most rows are tiny** (always filter on `population` before an average, a
ranking or a map).

### 1. Where does place median household income sit — and over which places?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*)                                                    AS places,
       count(median_hh_income)                                     AS published,
       round(100.0*(count(*)-count(median_hh_income))/count(*), 2) AS pct_suppressed,
       quantile_cont(median_hh_income, 0.10)::int                  AS p10,
       quantile_cont(median_hh_income, 0.50)::int                  AS p50,
       quantile_cont(median_hh_income, 0.90)::int                  AS p90
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet';
```

→ `32612 | 28468 | 12.71 | 40366 | 67199 | 121841`.

Now the same query behind a population floor:

```sql
LOAD httpfs;
SELECT count(*)                                                    AS places,
       count(median_hh_income)                                     AS published,
       round(100.0*(count(*)-count(median_hh_income))/count(*), 2) AS pct_suppressed,
       quantile_cont(median_hh_income, 0.10)::int                  AS p10,
       quantile_cont(median_hh_income, 0.50)::int                  AS p50,
       quantile_cont(median_hh_income, 0.90)::int                  AS p90
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet'
WHERE population >= 20000;
```

→ `2327 | 2327 | 0.0 | 53514 | 83683 | 136949`.

Two different answers to "what does a place earn": **$67,199** across all
32,612 places, **$83,683** across the 2,327 with 20,000 or more people. The
first number is a fact about villages and CDPs — 16,463 of these rows have
under 1,000 people — and the second is a fact about towns and cities. Neither
is wrong; stating which one you computed is the whole job. Note also that the
12.71% suppression vanishes entirely above the floor.

One state is the same query with `WHERE state = 'XX'`, and the floor still
earns its place:

```sql
LOAD httpfs;
SELECT geoid, name, population, median_hh_income::int AS income, round(median_hh_income_cv, 3) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet'
WHERE state = 'MS' AND population > 10000 AND median_hh_income_cv < 0.15
ORDER BY median_hh_income DESC LIMIT 5;
```

→ `2844520 | Madison city, Mississippi | 27946 | 119338 | 0.061`, `2854040 |
Olive Branch city, Mississippi | 47019 | 100606 | 0.052`, `2808300 | Brandon
city, Mississippi | 25542 | 92783 | 0.035`, `2825100 | Flowood city,
Mississippi | 10587 | 83880 | 0.08`, `2853520 | Ocean Springs city,
Mississippi | 18646 | 79712 | 0.065`. The `name` column already carries the
state, so a state's top places need no join to be readable.

### 2. Why the population floor is the query (`*_cv` by size band)

```sql
LOAD httpfs;
SELECT CASE WHEN population < 1000  THEN 'under 1,000'
            WHEN population < 10000 THEN '1,000-9,999'
            WHEN population < 50000 THEN '10,000-49,999'
            ELSE '50,000+' END                                        AS size_band,
       count(*)                                                       AS places,
       round(quantile_cont(median_hh_income_cv, 0.5), 3)              AS median_cv,
       round(100.0*count(*) FILTER (WHERE median_hh_income IS NULL)
             / count(*), 1)                                           AS pct_suppressed
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet'
WHERE population IS NOT NULL
GROUP BY 1 ORDER BY min(population);
```

→ `under 1,000 | 16463 | 0.209 | 22.6`, `1,000-9,999 | 11641 | 0.126 | 1.2`,
`10,000-49,999 | 3343 | 0.059 | 0.0`, `50,000+ | 883 | 0.028 | 0.0`.

Both columns collapse monotonically with size. Below 1,000 people the median
CV is 0.209 — well into "use with caution" — and more than one place in five
has no income median at all; above 10,000 nothing is suppressed and the median
CV is 0.059. `WHERE population IS NOT NULL` is needed because the 282
data-free rows would otherwise form a band of their own.

And the same measurement across geographies, which is the case for working at
a level that tiles:

```sql
LOAD httpfs;
SELECT 'place' AS geography, count(median_hh_income_cv) AS n,
       round(quantile_cont(median_hh_income_cv, 0.5), 3) AS median_cv,
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40)
             / count(median_hh_income_cv), 1) AS pct_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet'
UNION ALL
SELECT 'tract', count(median_hh_income_cv),
       round(quantile_cont(median_hh_income_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40)
             / count(median_hh_income_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet'
UNION ALL
SELECT 'county', count(median_hh_income_cv),
       round(quantile_cont(median_hh_income_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40)
             / count(median_hh_income_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet';
```

→ `place | 28240 | 0.139 | 7.3`, `tract | 83266 | 0.125 | 1.5`,
`county | 3221 | 0.042 | 0.1`.

Places are the noisiest of the three, and one place median in fourteen is
outright unreliable against one tract in 67 and one county in a thousand. If
the question is "how rich is this neighbourhood", tracts are both finer and
cleaner; places are the right level only when the *named municipality* is the
subject.

### 3. Every city against its own state (GEOID prefix join)

```sql
LOAD httpfs;
SELECT p.name, p.population, p.median_hh_income::int AS place_income,
       s.median_hh_income::int AS state_income,
       round(p.median_hh_income::double / s.median_hh_income, 2) AS ratio
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet' p
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet' s
  ON substr(p.geoid, 1, 2) = s.geoid
WHERE p.population > 100000 AND p.median_hh_income_cv < 0.05
ORDER BY ratio LIMIT 5;
```

→ `Hartford city, Connecticut | 121127 | 46411 | 95781 | 0.48`, `Newark city,
New Jersey | 310178 | 52060 | 103556 | 0.5`, `Springfield city, Massachusetts
| 154749 | 52656 | 103960 | 0.51`, `Waterbury city, Connecticut | 114869 |
51886 | 95781 | 0.54`, `Paterson city, New Jersey | 158735 | 55997 | 103556 |
0.54`.

A place GEOID is state FIPS (2) + place FIPS (5), so `substr(geoid, 1, 2)` is
the state's `geoid` — the only prefix join this collection supports. There is
no county component in the GEOID at all and therefore **no**
`substr(geoid, 1, 5)` route to
[`counties/county-income`](../../counties/county-income/collection.json): that
relationship is spatial, and it is one-to-many. Measured with the
`bbox`-overlap + `ST_Intersects` pattern, Houston city (`4835000`) intersects
five counties — Harris (`48201`), Fort Bend (`48157`), Montgomery (`48339`),
Brazoria (`48039`) and Waller (`48473`). The `ratio` column is a ratio of two
medians from two different universes' samples; it is a screening index, and
the margins below it are not propagated.

### 4. Is the difference between two places real? (margins, not estimates)

```sql
LOAD httpfs;
SELECT geoid, name, population, median_hh_income::int AS income,
       median_hh_income_moe::int AS moe,
       (median_hh_income - median_hh_income_moe)::int AS lo,
       (median_hh_income + median_hh_income_moe)::int AS hi
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet'
WHERE geoid IN ('3951816', '3959010', '3972060')
ORDER BY income DESC;
```

→ `3951816 | Montrose-Ghent CDP, Ohio | 5903 | 180250 | 29951 | 150299 |
210201`, `3959010 | Ottawa Hills village, Ohio | 4798 | 167917 | 34441 |
133476 | 202358`, `3972060 | Sheffield village, Ohio | 4380 | 107837 | 13499 |
94338 | 121336`.

The first two are the richest and second-richest Ohio places of 4,000–6,000
people, and the $12,333 between them is **not a finding**: their 90% intervals
are [150,299–210,201] and [133,476–202,358], overlapping across most of their
width. The third place's interval, [94,338–121,336], touches neither, so
*that* difference is real. Run this check before reporting any pair of places
— at this geography the margins on a small place's median routinely run to
20% of the estimate, so a ranked list of small places is mostly a ranked list
of sampling noise. Never do the comparison by subtracting medians and ignoring
the margins, and never sum or average the medians themselves.

### 5. Poverty, population-floored and CV-gated

```sql
LOAD httpfs;
SELECT geoid, name, population, pct_below_poverty,
       pct_below_poverty_moe AS moe, round(pct_below_poverty_cv, 3) AS cv, pct_snap
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet'
WHERE population > 50000 AND pct_below_poverty_cv < 0.10
ORDER BY pct_below_poverty DESC LIMIT 5;
```

→ `7252431 | Mayagüez zona urbana, Puerto Rico | 58977 | 54.68 | 3.24 | 0.036
| 51.55`, `7263820 | Ponce zona urbana, Puerto Rico | 107805 | 49.63 | 2.13 |
0.026 | 54.77`, `7210334 | Caguas zona urbana, Puerto Rico | 72922 | 39.8 |
2.79 | 0.043 | 46.44`, `7276770 | San Juan zona urbana, Puerto Rico | 317995 |
38.23 | 1.25 | 0.02 | 35.48`, `3988000 | Youngstown city, Ohio | 59331 | 37.29
| 2.82 | 0.046 | 36.82`.

Puerto Rico's place types are `zona urbana` and `comunidad`, not "city" — a
name filter built around "city" or "town" silently drops the island, and the
four rows above are among the poorest large places in the file. `pct_snap` is
printed beside the poverty rate because they measure different universes
(households receiving SNAP at any time in 12 months; people below the poverty
line) and the pair diverges: Ponce's SNAP share exceeds its poverty share.
Neither column may be averaged across these rows to get "Puerto Rico" — for
that, read [`states/state-income`](../../states/state-income/collection.json)
row `72`.

### Related recipes elsewhere

- Finding a place by name, the 11 Louisvilles, and the one-row cross-theme
  profile: [`places/AGENTS.md`](../AGENTS.md).
- The same income columns beside all 107 others, with wall-clock timings
  against the mirror: [`places/places/AGENTS.md`](../places/AGENTS.md).
- Home value against income at place level, and the rent median's 31.32%
  hole: [`places/place-housing/AGENTS.md`](../place-housing/AGENTS.md).
- Income by race at place level, published on as few as 14.2% of rows:
  [`places/place-wellbeing/AGENTS.md`](../place-wellbeing/AGENTS.md).
- The same theme where the medians are cleanest, and totals are legitimate:
  [`counties/county-income/AGENTS.md`](../../counties/county-income/AGENTS.md).
- Looking inside a city at geographies that tile it:
  [`tracts/tract-income/AGENTS.md`](../../tracts/tract-income/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and its z0–z5 features are counties carrying the Census Bureau's own
county estimates rather than these places', so nothing above can be reproduced
from tiles.
