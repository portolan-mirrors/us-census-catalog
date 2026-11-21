# AGENTS.md — US Census Demographics Mirror

Guidance for AI agents and automated clients working with this catalog.

**One rule survives every edit to this file.** Every claim here is either quoted
from a source or measured from the data. If you cannot point at where a fact
came from, it does not belong in this file. An agent acting on an invented join
key or an invented column name produces a confident wrong answer, and nothing
downstream catches it.

## What this catalog holds

U.S. Census Bureau demographics as GeoParquet + PMTiles, rooted at
`https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json`.
ACS 2020–2024 5-year indicators at block group, tract, county, state, ZCTA,
place and congressional-district level, plus 2020 Decennial counts at block
level. Each collection's own `AGENTS.md` documents its columns and carries
tested queries; this file covers what spans collections.

## Before you write a query

Read the column list before you write SQL, and use only names you have read.
Each collection's `collection.json` carries its schema, and each collection's
own `AGENTS.md` documents every column with the census table it comes from. A
plausible name is not a real one: this catalog has `pct_no_internet`, not
`pct_broadband`, and the two run in opposite directions. A query against a
column that does not exist fails loudly, which is the good case; a query
against the wrong real column returns a confident wrong answer.

Four habits keep an answer honest, and the sections below give the detail:

1. Report the margin of error with any ACS estimate, and do not rank on a
   difference smaller than it.
2. Gate a ranking on `*_cv` so small, unreliable areas do not win it.
3. Filter `geo_change = 'identical'` before reporting change over time at
   tract or block-group level.
4. Say what the number is about. These are statistics about places, not
   about the people in them.

## Shape: seven geographies, five themes

**Every ACS geography is a sub-catalog of themed collections**, and the
themes are the same everywhere: income, people, housing, connectivity,
wellbeing. One theme is one file, so a consumer who wants median income
reads 23 columns rather than 112.

| sub-catalog | themed collections | wide table | rows |
|---|---|---|---|
| [block-groups/](block-groups/AGENTS.md) | `bg-{income,people,housing,connectivity}` | — | 242,298 |
| [tracts/](tracts/AGENTS.md) | `tract-{income,people,housing,connectivity,wellbeing}` | — | 85,184 |
| [counties/](counties/AGENTS.md) | `county-{income,people,housing,connectivity,wellbeing}` | `counties` | 3,235 |
| [states/](states/AGENTS.md) | `state-…` | `states` | 56 |
| [zctas/](zctas/AGENTS.md) | `zcta-…` | `zctas` | 33,791 |
| [places/](places/AGENTS.md) | `place-…` | `places` | 32,612 |
| [congressional-districts/](congressional-districts/AGENTS.md) | `cd-…` | `congressional-districts` | 441 |
| [blocks](blocks/AGENTS.md) | — (2020 Decennial, hive-partitioned by state) | — | 8,174,955 |

The five coarse-or-sparse geographies add a sixth collection carrying **all
112 columns** on the same rows: at 441 to 33,791 features width costs little,
so a cross-theme question there needs no join. Block groups and tracts have
no wide table — a 112-column file over 242,298 rows would make every
consumer download all of it — and block groups have no wellbeing chunk,
because the Census Bureau does not publish health insurance, disability,
nativity or income by race below tract.

**The URL patterns, which differ for the wide tables:**

```
<base>/<group>/<cid>/<cid>.parquet        every themed chunk
<base>/<group>/<group>.parquet            the five wide tables — NOT <group>/<group>/
```

A wide table's `collection.json`, `README.md` and `styles/` sit in
`<group>/<group>/` beside the themed chunks, but its GeoParquet and PMTiles
stayed one directory up, so every data URL this catalog has published keeps
working. `counties/counties.parquet` is right;
`counties/counties/counties.parquet` is a 404.

## Join keys

Every collection has a `geoid` column (string): the full census GEOID.
Lengths by geography — state 2, **congressional district 4**, county 5,
**ZCTA 5**, **place 7**, tract 11, block group 12, block 15.

GEOIDs nest by prefix wherever a geography is built from the one below it: a
block group's county is `substr(geoid, 1, 5)`, its tract
`substr(geoid, 1, 11)`, its state `substr(geoid, 1, 2)`; a block's block group
is `substr(geoid, 1, 12)`. Collections at the same geography join 1:1 on
`geoid`.

Three geographies break the prefix rule, and each breaks it differently:

- **ZCTAs nest in nothing.** A ZCTA can cross county and state lines, and
  `substr(geoid, 1, 2)` is a postal region, not a state FIPS code — a prefix
  join there returns wrong rows rather than no rows. The `state` column is
  **NULL on all 33,791 rows** (measured), so `WHERE state = 'CA'` silently
  returns nothing. Relate ZCTAs spatially; see
  [zctas/AGENTS.md](zctas/AGENTS.md).
- **Places** carry no county component: `substr(geoid, 1, 2)` reaches
  `states`, and nothing reaches `counties` (one place can intersect several —
  Houston intersects five, measured). Places also do not tile the country, so
  they must never be summed to a total.
- **Congressional districts** are `state FIPS (2) + district (2)`:
  `substr(geoid, 1, 2)` reaches `states`, and relating a district to the
  tracts inside it is spatial.

## Quirks that produce silently wrong answers

- ACS margins of error are published at the **90% confidence level**. To sum
  estimates across geographies, add MOEs in quadrature; never sum medians at
  all (a median of a region is not derivable from its parts).
- **Two ACS estimates are not different because the numbers differ.** Each is
  an interval. Before reporting that A is higher than B, check whether
  `A - A_moe > B + B_moe`; if the intervals overlap, the honest answer is
  "no measurable difference". The margins grow sharply as the geography
  shrinks: the median `pct_below_poverty` is **13.35% ± 2.37 points at county
  level, 10.70% ± 5.68 at tract level and 9.28% ± 7.36 at block-group level**
  (measured over every row carrying a margin). At block-group level the
  interval is wider than most of the differences anyone wants to rank, so a
  top-10 list there is mostly noise unless it is gated on `*_cv`.
- **A 2015–2019 tract is not always the same ground as its 2020–2024
  namesake.** The Census Bureau redrew tract and block-group boundaries for
  2020, and a GEOID can be reused for a different polygon. The trends
  collections carry a `geo_change` column for exactly this, with one row per
  geography per period. Measured over `tract-trends`: `identical` on 116,818
  rows, `subdivided` on 46,136, `mixed` on 6,150, `absorbed` on 806 and
  `no_acs_data` on 458 — so **roughly a third of tract rows are not a
  like-for-like comparison** and a change figure there mixes real change with
  a boundary edit. Filter to `geo_change = 'identical'` before reporting
  change at tract level. Counties are far more stable: 6,422 of 6,470
  `county-trends` rows are `identical` (measured).
- **An area statistic is not a fact about a person.** Two indicators moving
  together across tracts says nothing about any individual in them, and the
  income of a tract is not the income of anyone who lives there. Report these
  as properties of places. Treating them as properties of people is the
  ecological fallacy, and it is the most common way this data is misread.
- Jam values (e.g. `-666666666`) in Census files mean "no estimate"; they
  are already `NULL` here. A query that averages a column needs no jam
  filtering, but remember NULLs reduce the row count.
- **At county, state and district level a whole family of margins is NULL,
  not just `population_moe`.** Measured: `population_moe` and the margins of
  `pct_under_18`, `pct_65_plus`, the four non-Hispanic race shares,
  `pct_hispanic`, `pct_people_of_color` and `pct_foreign_born` are NULL on
  **all 56 rows** at state level (`group_quarters_pop_moe` too), carried on
  only **132 of 3,235** counties, and carried on **423 of 441** districts.
  Every column in that list comes from a total-population table (B01001,
  B01003, B03002, B05002, plus B26001 at state level), and the NULL is
  upstream rather than suppression: the release's own `.dat` carries
  `-555555555` there, the **controlled-MOE** jam value a controlled estimate
  gets in place of a sampling margin (`0500000US01001|59947|-555555555` in
  `acsdt5y2024-b01003.dat`, read 2026-11-15), and the build turns it into
  NULL instead of publishing it as a number. The rows that do keep a margin
  are the ones too small to be controlled — all 132 such counties have a
  population under 7,000 (measured) — and at ZCTA, place, tract and
  block-group level the whole family is populated normally (33,161 of 33,791
  ZCTAs, 31,755 of 32,612 places, 84,419 of 85,184 tracts). Every chunk at a
  geography carries the same margins, so this is a property of the geography,
  not of a theme. `sqrt(sum(moe*moe))` over a NULL-bearing column returns
  NULL, so check before putting one in a quadrature sum — and an interval you
  cannot draw is not the same as a difference that is not real.
- **`median_hh_income` is bottom-coded at 2,499 and top-coded at 250,001**,
  and `median_home_value` at 2,000,001. Those are published ceilings and
  floors, not jam values, so they are not NULL — and at block-group level the
  3,458 coded rows carry **no margin of error at all** (measured). A top-N on
  a median returns ties on the code; exclude it or filter on `*_cv IS NOT
  NULL` before ranking.
- A share whose `*_moe` is exactly `0.0` is a flag to inspect, not high
  precision — it usually means a tiny or group-quarters universe. `population`
  is not a household count, so gate household-denominated shares on
  `households`, not on `population`.
- Coarse zooms of a PMTiles archive are **a coarser census geography**, not
  the collection's own: counties at z0–z5, tracts in the middle (z6–z7 in the
  `bg-*` archives, z6–z9 in `blocks`), the collection's own features below
  that. In the ACS archives those bands carry the Census Bureau's own county
  and tract estimates under the same column names — official values, not an
  aggregation of the file — so a feature clicked at a coarse zoom is a real
  county or tract with its own `geoid` and `name`. The county, state and
  congressional-district archives — the wide tables and their themed chunks
  alike — are real polygons at every zoom and need no such band, while the
  `zcta-*` and `place-*` chunks take the same county band at z0–z5 as their
  wide parents. `*_moe` columns are excluded from every tile; use the
  GeoParquet, not tiles, for statistics.
- Geometries are the Census cartographic boundary files (500k, shoreline-
  clipped), in EPSG:4326 — good for mapping and point-in-polygon, not for
  legal-boundary or area-measurement work. Blocks use TIGER/Line (not
  shoreline-clipped).

## Example queries

Five cross-collection recipes, each run with DuckDB 1.4.1 immediately before
it was written down, with its real output quoted beside it. Recipes 1–4 were
run against the published URLs, and their numbers were re-verified against
the same files on 2026-11-15. Recipe 5 reads the themed chunks at the coarse
geographies, which had not been uploaded to the mirror when it was run, so it
was run against the local build with the `catalog/` paths swapped in and
quotes no wall-clock time. Each collection's own `AGENTS.md` carries 4–5 more
that go deeper into that collection; these are the ones that span
collections.

Start every session with `INSTALL httpfs; LOAD httpfs;` (and `LOAD spatial;`
for geometry). Nothing below downloads a file — DuckDB range-reads the columns
it needs.

### 1. The richest counties in the country, reliable estimates only

```sql
INSTALL httpfs; LOAD httpfs;
SELECT geoid, name, population, median_hh_income::int AS income,
       round(median_hh_income_cv, 3) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet'
WHERE population > 65000 AND median_hh_income_cv < 0.05
ORDER BY median_hh_income DESC LIMIT 10;
```

→ `51107 Loudoun County, Virginia | 432998 | 181765 | 0.011`, `06085 Santa
Clara County, California | 1902047 | 164281 | 0.007`, `06081 San Mateo County,
California | 742340 | 158855 | 0.011`, `51059 Fairfax County, Virginia |
1147837 | 153637 | 0.006`, `24027 Howard County, Maryland | 336328 | 149763 |
0.013`, `08035 Douglas County, Colorado | 377150 | 149594 | 0.01`, `06041
Marin County, California | 257969 | 149091 | 0.018`, `36059 Nassau County, New
York | 1389591 | 146202 | 0.006`, `13117 Forsyth County, Georgia | 267287 |
143784 | 0.012`, `51013 Arlington County, Virginia | 236254 | 142114 | 0.015`.
**5.3 s**.

The two filters are the recipe. `population > 65000` keeps out small counties
whose medians swing on a few households; `median_hh_income_cv < 0.05` keeps out
estimates whose margin would reorder the list. Drop them and the top of the
ranking fills with counties of a few thousand people.

### 2. The most rent-burdened large cities, each against its own state

```sql
LOAD httpfs;
SELECT p.name, p.population, p.pct_rent_burdened AS place_pct,
       round(p.pct_rent_burdened_cv, 3) AS cv, s.pct_rent_burdened AS state_pct
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet' p
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet' s
  ON substr(p.geoid, 1, 2) = s.geoid
WHERE p.population > 200000 AND p.pct_rent_burdened_cv < 0.05
ORDER BY p.pct_rent_burdened DESC LIMIT 5;
```

→ `Hialeah city, Florida | 226165 | 64.03 | 0.032 | 60.09`, `Sunrise Manor
CDP, Nevada | 200218 | 63.07 | 0.029 | 55.85`, `San Bernardino city,
California | 222724 | 63.04 | 0.026 | 55.31`, `Miami city, Florida | 459745 |
62.92 | 0.017 | 60.09`, `Port St. Lucie city, Florida | 232491 | 62.72 | 0.049
| 60.09`. 8.7 s.

`substr(geoid, 1, 2)` is the whole join: a place GEOID is state FIPS + place
FIPS, so its first two characters are the state row's `geoid`. The same prefix
works from counties (5), tracts (11), block groups (12) and districts (4).
Carrying `state_pct` is what makes the numbers mean something: Hialeah is 4
points above a Florida that is already the most rent-burdened state in the
country (60.09%, measured — ahead of Hawaii 56.67 and Nevada 55.85).

### 3. Density against car ownership, nationally

```sql
LOAD httpfs;
WITH j AS (
  SELECT ntile(10) OVER (ORDER BY p.pop_density) AS d,
         c.pct_hh_no_vehicle, c.pct_commute_transit, c.pct_commute_drive_alone
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/tract-people.parquet' p
  JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.parquet' c
    USING (geoid)
  WHERE p.pop_density IS NOT NULL AND c.pct_hh_no_vehicle IS NOT NULL)
SELECT d AS density_decile, round(avg(pct_hh_no_vehicle), 1) AS no_vehicle,
       round(avg(pct_commute_transit), 1) AS transit,
       round(avg(pct_commute_drive_alone), 1) AS drive_alone
FROM j GROUP BY 1 ORDER BY 1;
```

→

```
 1 |  4.8 |  0.4 | 76.9
 2 |  4.6 |  0.4 | 77.5
 3 |  4.9 |  0.6 | 75.3
 4 |  5.6 |  0.9 | 73.2
 5 |  6.4 |  1.3 | 71.6
 6 |  6.9 |  1.6 | 70.7
 7 |  7.6 |  2.1 | 69.4
 8 |  8.1 |  2.6 | 67.8
 9 | 10.3 |  4.4 | 64.8
10 | 27.5 | 19.3 | 45.7
```

8.6 s over two 56 MB files and 85,184 tracts.

The relationship is almost entirely in the top decile: deciles 1–8 are within 4
points of each other on car-free households, and then the tenth triples. That
is the finding, and it is invisible in a correlation coefficient. These are
unweighted means over tracts — the right unit for "what is a dense
neighbourhood like", and **not** national household shares, because tracts
differ in size.

### 4. Drilling from the national ranking down to a neighbourhood

```sql
LOAD httpfs;
WITH rich AS (
  SELECT geoid, name
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet'
  WHERE population > 65000 AND median_hh_income_cv < 0.05
  ORDER BY median_hh_income DESC LIMIT 1)
SELECT rich.name AS county, t.geoid, t.median_hh_income::int AS tract_income,
       round(t.median_hh_income_cv, 2) AS cv
FROM rich
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet' t
  ON substr(t.geoid, 1, 5) = rich.geoid
WHERE t.median_hh_income IS NOT NULL
ORDER BY t.median_hh_income LIMIT 5;
```

→ `Loudoun County, Virginia | 51107611010 | 79583 | 0.15`, `… | 51107610505 |
85616 | 0.14`, `… | 51107610603 | 87096 | 0.09`, `… | 51107611018 | 93315 |
0.15`, `… | 51107611602 | 95341 | 0.06`. 11.2 s.

The poorest tract in the country's richest county still has a median household
income of $79,583 — above the national tract median of $77,004 (measured in
[tract-income](tracts/tract-income/AGENTS.md)). This is the pattern for any
"zoom in on the winner" question: pick the row at one geography, then join down
by GEOID prefix. Carry the `_cv` all the way down, because it grows as the
geography shrinks — the county's was 0.011, these tracts' run to 0.15.

### 5. One theme at all seven geographies, and where it stops meaning anything

```sql
LOAD httpfs;
WITH q AS (
  SELECT 'states' AS geography, 1 AS ord, pct_rent_burdened AS v, pct_rent_burdened_cv AS cv
    FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet'
  UNION ALL SELECT 'congressional districts', 2, pct_rent_burdened, pct_rent_burdened_cv
    FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/cd-housing.parquet'
  UNION ALL SELECT 'counties', 3, pct_rent_burdened, pct_rent_burdened_cv
    FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet'
  UNION ALL SELECT 'ZCTAs', 4, pct_rent_burdened, pct_rent_burdened_cv
    FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet'
  UNION ALL SELECT 'places', 5, pct_rent_burdened, pct_rent_burdened_cv
    FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.parquet'
  UNION ALL SELECT 'tracts', 6, pct_rent_burdened, pct_rent_burdened_cv
    FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet'
  UNION ALL SELECT 'block groups', 7, pct_rent_burdened, pct_rent_burdened_cv
    FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet')
SELECT geography, count(v) AS published,
       round(quantile_cont(v, 0.10), 1) AS p10,
       round(quantile_cont(v, 0.50), 1) AS p50,
       round(quantile_cont(v, 0.90), 1) AS p90,
       round(quantile_cont(cv, 0.50), 3) AS median_cv
FROM q GROUP BY geography, ord ORDER BY ord;
```

→

```
states                  |     52 | 44.0 | 48.7 | 52.9 | 0.008
congressional districts |    437 | 43.9 | 50.2 | 58.0 | 0.021
counties                |   3222 | 30.9 | 44.8 | 55.6 | 0.103
ZCTAs                   |  30087 |  8.4 | 45.4 | 69.4 | 0.242
places                  |  27852 |  0.0 | 45.1 | 77.1 | 0.338
tracts                  |  83901 | 23.7 | 49.4 | 73.1 | 0.256
block groups            | 223130 |  0.0 | 48.7 | 90.3 | 0.419
```

The same column, the same theme file, the same seven column names at every
geography — that is what the themed split buys you. The median barely moves
(44.8 to 50.2 across all seven); the **spread** goes from 44.0–52.9 at state
level to 0.0–90.3 at block group, and the median coefficient of variation
from 0.008 to 0.419. Choose the geography by what you intend to say: a
ranking of block groups by rent burden is a ranking of noise, and a ranking
of states hides every neighbourhood.

The ordering is not monotonic in unit size, which is the other lesson. ZCTAs
and places spread wider than tracts because a ZCTA or a place can be a
handful of renter households, while every tract holds 1,200–8,000 people —
those two geographies are population-sorted by nothing at all. Note also how
many rows drop out: `pct_rent_burdened` is published on 27,852 of 32,612
places.

### Where to go from here

Every geography is a sub-catalog whose own `AGENTS.md` covers what its six
collections share, and each collection's `AGENTS.md` carries its schema,
NULL rates and tested recipes.

| question | where |
|---|---|
| one number for a state or county | [states/](states/AGENTS.md), [counties/](counties/AGENTS.md) — pick a theme, or the wide table for all 112 columns |
| a city, town or CDP | [places/](places/AGENTS.md) — and never sum them to a total |
| a congressional district | [congressional-districts/](congressional-districts/AGENTS.md) — 119th Congress, and not comparable to an earlier one |
| a ZIP code | [zctas/](zctas/AGENTS.md) — read the ZCTA≠ZIP caveat first |
| inside a city or county | [tracts/](tracts/AGENTS.md), then [block-groups/](block-groups/AGENTS.md) |
| health, disability, income by race | any geography's `*-wellbeing` chunk — [tract](tracts/tract-wellbeing/AGENTS.md), [county](counties/county-wellbeing/AGENTS.md), [state](states/state-wellbeing/AGENTS.md), [ZCTA](zctas/zcta-wellbeing/AGENTS.md), [place](places/place-wellbeing/AGENTS.md), [district](congressional-districts/cd-wellbeing/AGENTS.md) — never below tract |
| a cross-theme profile of one row | the wide table at [counties](counties/counties/AGENTS.md), [states](states/states/AGENTS.md), [ZCTAs](zctas/zctas/AGENTS.md), [places](places/places/AGENTS.md) or [districts](congressional-districts/congressional-districts/AGENTS.md) |
| an exact count for a small area | [blocks](blocks/AGENTS.md) — 2020 Decennial, no margins of error |

## Structure

Assets and structural links resolve relative to the object that carries them.
STAC browsers and `pystac` both resolve them. The data browser at
[source.coop](https://source.coop/portolan-mirrors/us-census-catalog) renders
each collection with map previews, legends, schema, and download links.
