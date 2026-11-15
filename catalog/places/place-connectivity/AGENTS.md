# Agent guide — Commuting & Connectivity (Places & CDPs)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

How people get around and get online: households with no vehicle available, as a count and a share ([B25044](https://data.census.gov/table/ACSDT5Y2024.B25044)); commute mode shares for driving alone, public transportation, walking or cycling, and working from home ([B08301](https://data.census.gov/table/ACSDT5Y2024.B08301)); the share of commutes of 45 minutes or more ([B08303](https://data.census.gov/table/ACSDT5Y2024.B08303)); and the shares of households with no internet access and no computing device ([B28002](https://data.census.gov/table/ACSDT5Y2024.B28002), [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001)).

**32,612 rows**, one per place, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

This is the **noisiest** of the five themed place chunks. The median place sends **0.0%** of its workers by transit; `pct_commute_transit` publishes a coefficient of variation on only 8,538 rows, and **74.0%** of those are over the 0.40 "unreliable" line (measured, recipes 1 and 2). `pct_hh_no_vehicle` runs a median CV of 0.526 and `pct_no_internet` 0.435. Every recipe below carries a population floor and a `_cv` gate because without both the output is sampling noise with place names attached.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.pmtiles`, layer `place-connectivity`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/collection.json` — carries a full description for every column

This is a themed cut of the wide 112-column place table, which is published as the sixth sibling in this group: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet` ([agent guide](../places/AGENTS.md)). Same 32,612 rows, same geometry, every column below included — reach for it when a question crosses themes, and for this one when it does not.

## Source tables

| table | title | universe |
|---|---|---|
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B08301](https://data.census.gov/table/ACSDT5Y2024.B08301) | Means of Transportation to Work | Workers 16 years and over |
| [B08303](https://data.census.gov/table/ACSDT5Y2024.B08303) | Travel Time to Work | Workers 16 years and over who did not work from home |
| [B25044](https://data.census.gov/table/ACSDT5Y2024.B25044) | Tenure by Vehicles Available | Occupied housing units |
| [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001) | Types of Computers in Household | Households |
| [B28002](https://data.census.gov/table/ACSDT5Y2024.B28002) | Presence and Types of Internet Subscriptions in Household | Households |

## Schema

`geoid` is 7 characters — state FIPS (2) + place FIPS (5) — and `substr(geoid, 1, 2)` is the only prefix join it supports, to [`states/state-connectivity`](../../states/state-connectivity/collection.json). Places nest in states but not in counties (a place can straddle a county line) and a place is not an aggregate of tracts or block groups, so there is no prefix path to the finer collections. The five themed siblings and the wide table all carry the same 32,612 `geoid` values, so `JOIN … USING (geoid)` is 1:1.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 7-character place GEOID: state FIPS 2 + place FIPS 5, e.g. `0644000` for Los Angeles city. |
| `name` | string | `NAMELSAD`, `STATE_NAME` from the 2024 cartographic boundary place file — "Los Angeles city, California", "Brentwood CDP, New York". The descriptor in the name says whether the place is a city, town, village, borough or CDP. |
| `state` | string | Two-letter USPS state or territory code. |
| `population` | int64 | Total population. |
| `population_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `population`. |
| `aland_sqkm` | double | Land area in km² (water excluded), 3 decimals. |
| `pop_density` | double | People per square kilometre of land area, rounded to 1 decimal: `population / aland_sqkm`. |
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
| `geometry` | binary | Boundary polygon, WKB, EPSG:4326 / OGC:CRS84. |
| `bbox` | struct<xmin, ymin, xmax, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, with row-group statistics. |

## Field notes

- **A `_cv` gate silently drops every zero estimate.** `pct_commute_transit`
  is published on 31,433 places but carries a `_cv` on only **8,538** — and
  the 22,895 rows with an estimate and no CV are **exactly** the 22,895 rows
  whose estimate is 0.0 (measured, recipe 1: the CV is undefined when the
  estimate is 0). So `WHERE pct_commute_transit_cv < 0.15` means "places with
  some transit commuting, measured reliably", never "all places". If you need
  the zeros, write `WHERE pct_commute_transit = 0 OR pct_commute_transit_cv <
  0.15`.
- **Transit is a big-place phenomenon and this is a small-place file.** The
  median place's `pct_commute_transit` is **0.0** and the 99th percentile
  13.27 (measured, recipe 1). A linear colour ramp on this column shows one
  colour; the `styles/` class breaks were measured from the distribution, not
  assumed.
- **`pct_commute_transit` covers bus, subway and elevated rail, light rail,
  commuter rail and ferryboat** (B08301 line 10). Taxi and ride-hailing (line
  16) are a separate category in this vintage and are **not** included.
- **`pct_commute_45min_plus` divides by workers who did not work from home**
  (B08303's own universe), while every other commute share here divides by all
  workers 16+ (B08301). The two denominators differ, so the shares do not sum
  across the two tables, and `pct_work_from_home` is not the complement of
  anything in B08303.
- **`pct_no_internet` is the floor of the digital divide, not its extent.**
  Households that use the internet without paying for a subscription (B28002
  line 12) count as *having* access; only line 13, "No Internet access", is in
  the numerator.
- **`hh_no_vehicle` is a count of occupied housing units**, owner- and
  renter-occupied combined (B25044), and `pct_hh_no_vehicle` divides by
  occupied units — households, not people and not workers. It is not the
  complement of `pct_commute_drive_alone`, whose universe is workers.
- **Places are not a partition of the country.** Do not sum `hh_no_vehicle`
  across place rows to get a state or national count — the land between places
  is absent from this file, not empty. For a total, use
  [`counties/county-connectivity`](../../counties/county-connectivity/collection.json)
  or
  [`states/state-connectivity`](../../states/state-connectivity/collection.json).
- **Most rows are small.** 16,463 places have under 1,000 people and 883 have
  50,000 or more (measured). Filter on `population` before any average,
  ranking or map.
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
  here `pct_hh_no_vehicle_cv`, `pct_commute_transit_cv` and
  `pct_no_internet_cv`. Rule of thumb: under 0.12 reliable, 0.12–0.40 use with
  caution, over 0.40 unreliable. `pct_commute_drive_alone`,
  `pct_commute_walk_bike`, `pct_work_from_home`, `pct_commute_45min_plus` and
  `pct_no_computer` have **no `_cv`**; gate those on `_moe`.
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
| `population`, `hh_no_vehicle` | NULL on 0.86% of places — the 282 rows with 2024 boundaries and no ACS tabulation. Every other column is NULL on at least those rows. |
| `pct_hh_no_vehicle`, `pct_no_internet`, `pct_no_computer` | NULL on 2.76% of places each (measured) — all divide by occupied units or households, so they fail together on places with none. |
| `pct_commute_drive_alone`, `pct_commute_transit`, `pct_commute_walk_bike`, `pct_work_from_home` | NULL on 3.62% of places each (measured) — B08301's worker denominator came out 0. |
| `pct_commute_45min_plus` | NULL on 3.91% of places (measured) — B08303's narrower universe (workers who did not work from home) empties slightly more often. |

Suppression is mild in this collection; **unreliability is the problem instead.** Measured medians of the three `_cv` columns at place level, with the share over the 0.40 line among the rows that publish one:

| column | rows with a `_cv` | median CV | share over 0.40 |
|---|---|---|---|
| `pct_commute_transit` | 8,538 | 0.691 | 74.0% |
| `pct_hh_no_vehicle` | 23,952 | 0.526 | 66.1% |
| `pct_no_internet` | 27,624 | 0.435 | 56.2% |

For comparison, `pct_commute_transit`'s median CV is 0.608 across the 2,417 counties that publish one (69.9% over 0.40) and 0.037 across 52 states (0.0% over 0.40). This column is barely usable below state level without a hard population floor, and the right move for a national transit question is [`states/state-connectivity`](../../states/state-connectivity/collection.json).

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 279 places here, plus 4 states, 13 county equivalents, 126 tracts and 405 block groups elsewhere in the catalog.

Three more places have boundaries and no ACS row: `3608026` Brentwood CDP and `3683294` Wyandanch CDP, left without an ACS match by the 2024 re-delineation of Suffolk County, New York, and `2148000` Louisville city, whose ACS tabulation is the consolidated `2148006` metro government. Running the other way, every one of the 32,330 ACS-tabulated places matched a polygon.

Row count is the 2024 cartographic boundary place file's own feature count, 32,612. For scale, the Census Bureau's [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html) give 19,734 incorporated places and 12,454 census designated places (32,188) for the 2020 vintage; the 2024 vintage is four years of incorporations, dissolutions and CDP re-delineations later.

PMTiles coarse zooms are a different census geography from this collection's: z0–z5 are **counties**, carrying the Census Bureau's own county estimates for these same columns, and z6–z12 are the places themselves. The county band is national orientation, not a roll-up of this file — places do not tile a county. `*_moe` columns are not in the tiles; `*_cv` columns are, which on this collection is the difference between a readable transit map and a misleading one. Statistics come from the GeoParquet.

## Related collections

- [`places/place-income`](../place-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`places/place-people`](../place-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`places/place-housing`](../place-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1 — `households` lives there, and it is this collection's denominator.
- [`places/place-wellbeing`](../place-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`places/places`](../places/collection.json) — the wide 112-column place table, the sixth sibling: every column of all five themes in one file.
- [`counties/county-connectivity`](../../counties/county-connectivity/collection.json) and [`states/state-connectivity`](../../states/state-connectivity/collection.json) — the same theme at geographies that **do** tile the country, and where a transit share is reliable.
- [`tracts/tract-connectivity`](../../tracts/tract-connectivity/collection.json) and [`block-groups/bg-connectivity`](../../block-groups/bg-connectivity/collection.json) — the same theme inside a city, at geographies that tile it.
- [`zctas/zcta-connectivity`](../../zctas/zcta-connectivity/collection.json) and [`congressional-districts/cd-connectivity`](../../congressional-districts/cd-connectivity/collection.json) — the same theme at the catalog's other non-nesting geographies.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no commute or internet columns.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted. For
scale instead: the file is **27.9 MB** over **32,612 rows**.

### 1. How rare is transit commuting? (the distribution first, always)

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(pct_commute_transit)                         AS published,
       round(avg(pct_commute_transit), 2)                 AS mean,
       quantile_cont(pct_commute_transit, 0.50)           AS p50,
       round(quantile_cont(pct_commute_transit, 0.99), 2) AS p99,
       max(pct_commute_transit)                           AS max
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet';
```

→ `31433 | 0.81 | 0.0 | 13.27 | 100.0`.

The median place sends **nobody** by transit, the 99th percentile sends one
worker in eight, and the maximum is 100. Now the part that bites a `_cv`-gated
query:

```sql
LOAD httpfs;
SELECT count(*) FILTER (WHERE pct_commute_transit IS NOT NULL
                          AND pct_commute_transit_cv IS NULL)  AS est_no_cv,
       count(*) FILTER (WHERE pct_commute_transit = 0)         AS est_zero,
       count(*) FILTER (WHERE pct_commute_transit = 0
                          AND pct_commute_transit_cv IS NULL)  AS zero_and_no_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet';
```

→ `22895 | 22895 | 22895`.

All three counts are the same number, and that is the finding: every place
with an estimate and no CV is a place whose estimate is exactly 0, because
`moe / 1.645 / estimate` is undefined there. A reliability gate therefore
restricts you to the 8,538 places with *some* transit commuting — which is
usually what you want, and is never what the query says. Write the zeros back
in explicitly if the question is "how many places have no transit at all".

### 2. The three `_cv` columns, and where this question belongs

```sql
LOAD httpfs;
SELECT 'pct_commute_transit' AS col, count(pct_commute_transit_cv) AS n,
       round(quantile_cont(pct_commute_transit_cv, 0.5), 3) AS median_cv,
       round(100.0*count(*) FILTER (WHERE pct_commute_transit_cv > 0.40)
             / count(pct_commute_transit_cv), 1) AS pct_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet'
UNION ALL
SELECT 'pct_hh_no_vehicle', count(pct_hh_no_vehicle_cv),
       round(quantile_cont(pct_hh_no_vehicle_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE pct_hh_no_vehicle_cv > 0.40)
             / count(pct_hh_no_vehicle_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet'
UNION ALL
SELECT 'pct_no_internet', count(pct_no_internet_cv),
       round(quantile_cont(pct_no_internet_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE pct_no_internet_cv > 0.40)
             / count(pct_no_internet_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet';
```

→ `pct_commute_transit | 8538 | 0.691 | 74.0`,
`pct_hh_no_vehicle | 23952 | 0.526 | 66.1`,
`pct_no_internet | 27624 | 0.435 | 56.2`.

All three medians sit above the 0.40 line: the *typical* place-level value of
each of these columns is unreliable on the Census Bureau's own rule of thumb.
And the same column one and two geographies up:

```sql
LOAD httpfs;
SELECT 'place' AS geography, count(pct_commute_transit_cv) AS publish_cv,
       round(quantile_cont(pct_commute_transit_cv, 0.5), 3) AS median_cv,
       round(100.0*count(*) FILTER (WHERE pct_commute_transit_cv > 0.40)
             / count(pct_commute_transit_cv), 1) AS pct_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet'
UNION ALL
SELECT 'county', count(pct_commute_transit_cv),
       round(quantile_cont(pct_commute_transit_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE pct_commute_transit_cv > 0.40)
             / count(pct_commute_transit_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet'
UNION ALL
SELECT 'state', count(pct_commute_transit_cv),
       round(quantile_cont(pct_commute_transit_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE pct_commute_transit_cv > 0.40)
             / count(pct_commute_transit_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet';
```

→ `place | 8538 | 0.691 | 74.0`, `county | 2417 | 0.608 | 69.9`,
`state | 52 | 0.037 | 0.0`.

Counties barely help; states fix it completely. A national statement about
transit use belongs at state level, and a place-level transit map needs a
population floor plus `_cv` greying. Run this before choosing a geography.

### 3. The transit places, floored and gated

```sql
LOAD httpfs;
SELECT geoid, name, population, pct_commute_transit AS transit,
       pct_commute_transit_moe AS moe, round(pct_commute_transit_cv, 3) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet'
WHERE population > 50000 AND pct_commute_transit_cv < 0.15
ORDER BY pct_commute_transit DESC LIMIT 5;
```

→ `3651000 | New York city, New York | 8483844 | 44.01 | 0.24 | 0.003`,
`3479610 | West New York town, New Jersey | 52004 | 37.13 | 4.2 | 0.069`,
`3474630 | Union City city, New Jersey | 66463 | 36.78 | 3.0 | 0.05`,
`3432250 | Hoboken city, New Jersey | 58668 | 36.56 | 2.25 | 0.037`,
`3436000 | Jersey City city, New Jersey | 294078 | 36.1 | 1.28 | 0.022`.

Four of the five are in New Jersey, across the Hudson from the fifth. New
York city's margin is **0.24 points on 44.01** — a CV of 0.003, the tightest
estimate in the file, because the place has 8.5 million people. West New York
town's margin is 4.2 points on a similar share, from a place 160 times
smaller. Same column, same gate, two very different amounts of information;
quote the margin whenever you quote the estimate.

### 4. Where households are offline

```sql
LOAD httpfs;
SELECT geoid, name, population, pct_no_internet, pct_no_internet_moe AS moe,
       round(pct_no_internet_cv, 3) AS cv, pct_no_computer
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet'
WHERE population > 25000 AND pct_no_internet_cv < 0.15
ORDER BY pct_no_internet DESC LIMIT 5;
```

→ `3639853 | Kiryas Joel village, New York | 38916 | 76.14 | 4.17 | 0.033 |
68.73`, `3648010 | Monsey CDP, New York | 28160 | 52.11 | 6.87 | 0.08 | 40.89`,
`3438580 | Lakewood CDP, New Jersey | 69585 | 38.5 | 4.8 | 0.076 | 19.37`,
`7276770 | San Juan zona urbana, Puerto Rico | 317995 | 22.06 | 0.83 | 0.023 |
18.25`, `7203368 | Arecibo zona urbana, Puerto Rico | 40831 | 19.75 | 2.44 |
0.075 | 18.38`.

Three quarters of Kiryas Joel's households report no internet access of any
kind, with a 4.17-point margin — a reliable estimate of a genuinely unusual
place, and a reminder that this column measures a choice as readily as a
constraint. `pct_no_computer` is printed beside it because the two diverge:
Lakewood is 38.5% offline but only 19.37% device-free, San Juan 22.06% and
18.25%. Remember the universe — households that use the internet *without* a
paid subscription count as having access, so `pct_no_internet` is the floor of
the digital divide, not its extent.

### 5. Car-free households against income (sibling join)

```sql
LOAD httpfs;
SELECT c.geoid, c.name, c.population, c.pct_hh_no_vehicle AS no_vehicle,
       round(c.pct_hh_no_vehicle_cv, 3) AS nv_cv, i.median_hh_income::int AS income
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet' c
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet' i
  USING (geoid)
WHERE c.population > 100000 AND c.pct_hh_no_vehicle_cv < 0.10
ORDER BY c.pct_hh_no_vehicle DESC LIMIT 5;
```

→ `3651000 | New York city, New York | 8483844 | 55.33 | 0.003 | 80483`,
`3436000 | Jersey City city, New Jersey | 294078 | 40.26 | 0.022 | 97710`,
`1150000 | Washington city, District of Columbia | 681294 | 36.01 | 0.014 |
109870`, `3451000 | Newark city, New Jersey | 310178 | 34.26 | 0.028 | 52060`,
`2507000 | Boston city, Massachusetts | 666442 | 33.25 | 0.015 | 97344`.

The join is 1:1 on `geoid` — all six place collections hold the same 32,612
rows. Car-free living is not one story: Jersey City at 40.26% has a median
household income of $97,710 and Newark at 34.26% has $52,060, half as much.
Reading `pct_hh_no_vehicle` as a poverty indicator would be wrong in both
cities for opposite reasons. The denominator is occupied housing units, not
people and not workers, so this column cannot be combined with
`pct_commute_drive_alone` — that one divides by workers 16 and over.

### Related recipes elsewhere

- The 11 Louisvilles, the consolidated-city trap, and the one-row cross-theme
  profile: [`places/AGENTS.md`](../AGENTS.md).
- The same columns beside all 107 others, with wall-clock timings against the
  mirror: [`places/places/AGENTS.md`](../places/AGENTS.md).
- The population-floor argument measured by size band, and the margin-overlap
  test: [`places/place-income/AGENTS.md`](../place-income/AGENTS.md).
- Transit shares where they are reliable:
  [`states/state-connectivity/AGENTS.md`](../../states/state-connectivity/AGENTS.md).
- Density against car ownership and transit inside a city:
  [`tracts/tract-connectivity/AGENTS.md`](../../tracts/tract-connectivity/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and its z0–z5 features are counties carrying the Census Bureau's own
county estimates rather than these places', so nothing above can be reproduced
from tiles.
