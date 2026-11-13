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
level. Block groups and tracts are split into themed collections (income,
people, housing, connectivity, and wellbeing at tracts only); the other five
geographies carry all 112 columns in one wide table each. Each collection's
own `AGENTS.md` documents its columns and carries tested queries; this file
covers what spans collections.

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
- Jam values (e.g. `-666666666`) in Census files mean "no estimate"; they
  are already `NULL` here. A query that averages a column needs no jam
  filtering, but remember NULLs reduce the row count.
- **`population_moe` is the one estimate that often has no margin.** Measured:
  NULL on all 56 rows of `states` and on 3,103 of 3,235 rows of `counties`
  (only small rural counties carry one), and populated normally at the finer
  geographies. `sqrt(sum(moe*moe))` over a NULL-bearing column returns NULL,
  so check before putting it in a quadrature sum.
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
  county or tract with its own `geoid` and `name`. `counties`, `states` and
  `congressional-districts` are real polygons at every zoom. `*_moe` columns
  are excluded from every tile; use the GeoParquet, not tiles, for
  statistics.
- Geometries are the Census cartographic boundary files (500k, shoreline-
  clipped), in EPSG:4326 — good for mapping and point-in-polygon, not for
  legal-boundary or area-measurement work. Blocks use TIGER/Line (not
  shoreline-clipped).

## Example queries

Four cross-collection recipes, each run against the published URLs with DuckDB
1.4.1 immediately before it was written down, with its real output quoted
beside it. Each collection's own `AGENTS.md` carries 4–5 more that go deeper
into that collection; these are the ones that span collections.

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

### Where to go from here

| question | collection |
|---|---|
| one number for a state or county | [states](states/AGENTS.md), [counties](counties/AGENTS.md) — all 112 columns in one wide table |
| a city, town or CDP | [places](places/AGENTS.md) — and never sum them to a total |
| a congressional district | [congressional-districts](congressional-districts/AGENTS.md) — 119th Congress |
| a ZIP code | [zctas](zctas/AGENTS.md) — read the ZCTA≠ZIP caveat first |
| inside a city or county | [tracts](tracts/AGENTS.md), then [block-groups](block-groups/AGENTS.md) |
| health, disability, income by race | [tracts/tract-wellbeing](tracts/tract-wellbeing/AGENTS.md) — not published below tract |
| an exact count for a small area | [blocks](blocks/AGENTS.md) — 2020 Decennial, no margins of error |

## Structure

Assets and structural links resolve relative to the object that carries them.
STAC browsers and `pystac` both resolve them. The data browser at
[source.coop](https://source.coop/portolan-mirrors/us-census-catalog) renders
each collection with map previews, legends, schema, and download links.
