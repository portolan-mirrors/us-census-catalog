# Agent guide — Places & CDPs

Guidance for AI agents and automated clients working with this geography.

**Every claim in this file is quoted from a source or measured from the data.**
The catalog-level [AGENTS.md](../AGENTS.md) covers what spans geographies, and
each collection's own `AGENTS.md` carries its columns, NULL rates and tested
queries. This file covers what the six collections share. If you cannot point
at where a fact came from, it does not belong here.

## What this geography is

**This is the file somebody reaches for when they name a city, and it is
mostly not cities.**

A "place" is two things at once. Incorporated places are cities, towns,
villages and boroughs with a legal government.
[Census designated places](https://www.census.gov/programs-surveys/bas/information/cdp.html)
are the Census Bureau's statistical stand-ins for unincorporated communities —
no government, no legal boundary, delineated so the ACS has something to
tabulate. **12,592 of the 32,612 rows are CDPs** (38.61%, measured), and the
`name` column's `NAMELSAD` descriptor is what tells you which kind a row is:
"Los Angeles city", "Brentwood CDP", "Ottawa Hills village",
"Ponce zona urbana".

The size range is the thing to internalise. The file runs from New York city
(8,483,844 people) down through 1,432 places of between 1 and 50 people to 512
that report a population of exactly 0. The **median place has 959 people**;
**16,463 places have under 1,000** and only **883 have 50,000 or more** (all
measured). So an unfiltered place-level average, ranking or choropleth is a
statement about hamlets, and a `population` filter is part of almost every
correct query here — not a refinement, a precondition. Two measured examples:
the median place's `median_hh_income` is $67,199 across all places and $83,683
across places of 20,000+; the median place publishes an Asian-householder
income median on 14.2% of rows nationally and 96.04% of the 883 rows over
50,000.

Two structural facts follow the geography everywhere:

- **Places do not tile the country.** The land between them is simply not in
  these files — absent, not zero. Place rows must never be summed to a county,
  a state or a national total, and "the rest of the state" cannot be derived
  by subtraction either. For a total, use
  [counties](../counties/AGENTS.md) or [states](../states/AGENTS.md).
- **Places nest in a state but not in a county.** `geoid` is state FIPS (2) +
  place FIPS (5), so `substr(geoid, 1, 2)` reaches
  [states](../states/AGENTS.md) and **nothing** reaches counties: a place can
  straddle county lines, and Houston city (`4835000`) intersects five —
  Harris (`48201`), Fort Bend (`48157`), Montgomery (`48339`), Brazoria
  (`48039`) and Waller (`48473`), measured with a `bbox`-overlap +
  `ST_Intersects` query. Relating a place to counties or tracts is spatial and
  one-to-many.

**32,612 rows** per collection, one per place, ACS 2020–2024 5-year estimates,
geometry from the 2024 cartographic boundary files (GENZ2024, 1:500,000,
shoreline-clipped, EPSG:4326). The ACS tabulates 32,330 places and every one
of them matched a polygon, so nothing in the release is missing here; the
other 282 rows have boundaries and no ACS data, and are listed under
[Shared quirks](#shared-quirks).

## Six collections, one geography

```
catalog/places/
  place-income/        place-people/     place-housing/
  place-connectivity/  place-wellbeing/  places/
  places.parquet       places.pmtiles          <- the wide table's data
```

| collection | theme | headline columns |
|---|---|---|
| [place-income](place-income/collection.json) ([agent guide](place-income/AGENTS.md)) | Income & Poverty | `median_hh_income`, `per_capita_income`, `pct_below_poverty`, `pct_snap`, `pct_unemployed` |
| [place-people](place-people/collection.json) ([agent guide](place-people/AGENTS.md)) | People & Education | `median_age`, `pct_under_18`, `pct_65_plus`, the four non-Hispanic race shares, `pct_hispanic`, `pct_bachelors_plus` |
| [place-housing](place-housing/collection.json) ([agent guide](place-housing/AGENTS.md)) | Housing & Rent | `housing_units`, `households`, `pct_owner_occupied`, `median_gross_rent`, `median_home_value`, `pct_rent_burdened` |
| [place-connectivity](place-connectivity/collection.json) ([agent guide](place-connectivity/AGENTS.md)) | Commuting & Connectivity | `hh_no_vehicle`, the B08301 commute-mode shares, `pct_commute_45min_plus`, `pct_no_internet`, `pct_no_computer` |
| [place-wellbeing](place-wellbeing/collection.json) ([agent guide](place-wellbeing/AGENTS.md)) | Health, Disability & Income by Race | `pct_uninsured`, `pct_with_disability`, `pct_foreign_born`, `group_quarters_pop`, `median_hh_income_{black,white_nh,asian,hispanic}`, `pct_below_poverty_black` |
| [places](places/collection.json) ([agent guide](places/AGENTS.md)) | **All Indicators** — the wide table | all 112 columns of the five themes in one file |

Column counts: income 23, people 29, housing 32, connectivity 30, wellbeing
34, wide 112. Every chunk carries the same seven context columns — `geoid`,
`name`, `state`, `population`, `population_moe`, `aland_sqkm`, `pop_density` —
plus `geometry` and the `bbox` covering struct, so a single-theme question
never needs a join.

**The wide collection's data files sit one directory up.** The five themed
children keep their parquet and pmtiles inside their own directory
(`places/place-income/place-income.parquet`), but the wide table's bytes stay
at `places/places.parquet` and `places/places.pmtiles`, where they have always
been, while its `collection.json`, `README.md` and `styles/` live in
`places/places/`. The data URLs are therefore:

- themed child: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/<cid>/<cid>.parquet`
- wide table: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet`
- every child's STAC, wide one included: `.../places/<cid>/collection.json`
- this group's sub-catalog: `.../places/catalog.json`

Reach for the wide table when a question crosses themes or profiles one named
place; reach for a themed child when it does not. On disk the wide file is
32.9 MB against 27.7–28.2 MB for each themed cut, so one theme is a cheaper
read from the themed file and three themes are a cheaper read from the wide
one.

## The chunks join 1:1 on `geoid`

All six hold the same 32,612 `geoid` values with the same geometry. Measured,
with the local paths swapped in for the published URLs because the five themed
files had not yet reached the mirror — so no wall-clock time is quoted:

```sql
LOAD httpfs;
SELECT (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet')             AS income,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.parquet')             AS people,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.parquet')           AS housing,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet') AS connectivity,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.parquet')       AS wellbeing,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet')                                AS places;
```

→ `32612 | 32612 | 32612 | 32612 | 32612 | 32612`. And the stronger check,
that they are the *same* 32,612 and not merely as many:

```sql
LOAD httpfs;
SELECT count(*) AS geoids_in_all_six FROM (
  SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet');
```

→ `32612`. So `JOIN … USING (geoid)` loses nothing, and a full profile of one
place is one query across all five themed files — or a single `SELECT` from
the wide table, which for this shape is the better read:

```sql
LOAD httpfs;
SELECT i.geoid, i.name, i.population, i.median_hh_income::int AS income,
       p.median_age, p.pct_bachelors_plus AS degree, h.median_gross_rent::int AS rent,
       c.pct_commute_transit AS transit, w.pct_uninsured AS uninsured
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet' i
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-people/place-people.parquet'             p USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.parquet'           h USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-connectivity/place-connectivity.parquet' c USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-wellbeing/place-wellbeing.parquet'       w USING (geoid)
WHERE i.geoid = '2148006';
```

→ `2148006 | Louisville/Jefferson County metro government (balance), Kentucky
| 631818 | 66849 | 37.7 | 33.78 | 1120 | 1.76 | 6.01`.

Five files for one row is the expensive shape; join only the chunks you need,
or read the wide table. And that `geoid` is not an accident — it is the next
section.

## Finding the place somebody named

`geoid` is the stable key and `name` is a search term. `name` is `NAMELSAD`
plus `STATE_NAME` from the boundary file, so the state is inside the string and
so is the place type — which is exactly what makes name matching hazardous.
Measured: **23 rows** begin "Springfield" and 13 of them are literally
"Springfield city"; **11 rows** begin "Louisville". And one of those eleven is
a trap:

```sql
LOAD httpfs;
SELECT geoid, name, population, median_hh_income::int AS income
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet'
WHERE name LIKE 'Louisville%' ORDER BY geoid;
```

→ `0144344 | Louisville town, Alabama | 518 | 44439`, `0846355 | Louisville
city, Colorado | 20786 | 147319`, `1347560 | Louisville city, Georgia | 2132 |
49821`, `1744927 | Louisville village, Illinois | 1163 | 43750`, `2042925 |
Louisville city, Kansas | 175 | NULL`, **`2148000 | Louisville city, Kentucky |
NULL | NULL`**, **`2148006 | Louisville/Jefferson County metro government
(balance), Kentucky | 631818 | 66849`**, `2842280 | Louisville city,
Mississippi | 5983 | 36985`, `3129260 | Louisville city, Nebraska | 1449 |
94208`, `3945094 | Louisville city, Ohio | 9602 | 64375`, `4743820 |
Louisville city, Tennessee | 4383 | 89744`.

Three separate lessons in eleven rows:

1. **The Louisville anyone means is `2148006`,** and it is not called
   "Louisville". The ACS tabulates the consolidated Louisville/Jefferson
   County metro government (balance); `2148000` "Louisville city" is still in
   the 2024 boundary file, has no ACS row, and publishes every column as NULL.
   A query for `name LIKE 'Louisville city%' AND state = 'KY'` returns the
   dead row and nothing else. The same shape of trap exists for other
   consolidated city-counties.
2. **Two different kinds of NULL.** `2148000`'s NULL means "no ACS row for
   this boundary". `2042925` Louisville city, Kansas (population 175) has an
   ACS row and a suppressed income median — a different fact with the same
   appearance. Check `population`: NULL there means the first kind, a number
   there means the second.
3. **Ten of the eleven are not what was asked for.** Resolve a name to a
   `geoid` once, eyeball the candidates, then use the `geoid` from then on: it
   is identical across all six collections and the PMTiles archives, while a
   name is one re-delineation away from changing.

Two further name hazards, both measured: Puerto Rico's descriptors are
`zona urbana` and `comunidad`, so a filter written around "city" or "town"
silently drops the whole island — including San Juan zona urbana (317,995
people) and the poorest large places in the file. And many of the places
people name are CDPs, not cities: Bethesda CDP has the highest degree share of
any place over 50,000 (measured), and McLean CDP and East Honolulu CDP are two
of the five highest rents among places over 25,000 whose rent median has a CV
under 0.05 (measured, in [place-housing](place-housing/AGENTS.md)).

## When to step up or down a geography

Places are a *named-entity* geography, not an analytic one. Use them when the
municipality is the subject of the question — "how expensive is Austin" — and
step off them when it is not.

Suppression, the same columns at four levels (measured over the housing
chunks):

| column | place | ZCTA | tract | county |
|---|---|---|---|---|
| `median_gross_rent` | **31.32%** | 23.79% | 5.92% | 0.62% |
| `median_home_value` | **12.78%** | 10.45% | 3.55% | 0.56% |
| `median_hh_income` | 12.71% | 9.60% | 1.59% | 0.43% |

Reliability, the median coefficient of variation (measured):

| column | place | tract | county | state |
|---|---|---|---|---|
| `median_hh_income_cv` | 0.139 | 0.125 | 0.042 | 0.004 |
| `pct_uninsured_cv` | **0.500** | — | 0.098 | 0.010 |
| `pct_commute_transit_cv` | **0.691** | — | 0.608 | 0.037 |
| `pct_hh_no_vehicle_cv` | **0.526** | — | 0.172 | 0.015 |
| `pct_below_poverty_black_cv` | **0.445** | — | 0.275 | 0.031 |

Only block groups are worse. Share over the 0.40 "unreliable" line among
places that publish a CV, measured: `pct_commute_transit` 74.0%,
`pct_hh_no_vehicle` 66.1%, `pct_uninsured` 58.1%,
`pct_below_poverty_black` 55.0%.

- **Stay here** when the answer names a municipality, or when the question is
  about city-to-city comparison — with a population floor and a `_cv` gate.
- **Step down to [tracts](../tracts/AGENTS.md)** for anything *inside* a city.
  Tracts tile the city, places do not tile anything, and tract medians are
  both finer and cleaner (`median_hh_income` NULL on 1.59% of tracts against
  12.71% of places). [Block groups](../block-groups/AGENTS.md) go finer still,
  at five times the missing rent medians and with no twin for the wellbeing
  theme at all.
- **Step up to [counties](../counties/AGENTS.md) or
  [states](../states/AGENTS.md)** whenever the answer will be a single quoted
  number, whenever a **total** is wanted (places cannot produce one), or
  whenever the subject is a race-iteration median or a transit share.
  `median_hh_income_asian` is NULL on 85.80% of places against 53.63% of
  counties; `pct_commute_transit`'s median CV goes from 0.691 at place to
  0.037 at state. **But stepping up costs you the margins on the
  total-population columns.** Measured: `population_moe` is populated on
  **32,267 of 32,612 places**, and on **132 of 3,235 counties** and **0 of 56
  states** — and the same holds for every share built on a total-population
  table, so `pct_under_18_moe`, `pct_65_plus_moe`, the race-share margins and
  `pct_foreign_born_moe` are populated on **31,755 places**, on **132
  counties** and on **none of the 56 states** (all measured).
  (`group_quarters_pop_moe` is populated on 32,329 places.) If the answer
  needs an interval on an age share, a race share or
  the foreign-born share, places and tracts are where one exists; counties and
  states will give you a cleaner estimate with no margin at all.
- **[ZCTAs](../zctas/AGENTS.md)** are the other "everyone thinks they know
  this geography" level, and they nest in nothing at all — not even a state.
- **[Blocks](../blocks/AGENTS.md)** carry 2020 Decennial counts only — a
  different survey and vintage, not a finer version of these numbers.

## Shared quirks

- **Never sum place rows to a total.** Places do not tile the country; the
  land between them is absent from the file. This is the single most common
  way to get a confidently wrong answer out of this geography.
- **Filter on `population` before almost anything.** 16,463 of 32,612 places
  have under 1,000 people. An ungated top-N on a percentage column returns
  places of 19 to 146 people reading 100.0% with margins of error of 48 to 201
  percentage points (measured, in
  [place-people](place-people/AGENTS.md)).
- **`substr(geoid, 1, 2)` → state, and that is the only prefix join.** There
  is no county component in a place GEOID. Houston intersects five counties
  (measured); the relationship is spatial and one-to-many.
- Every estimate carries `<name>_moe` at the **90%** confidence level. Headline
  columns also carry `<name>_cv` = `moe / 1.645 / estimate`: under 0.12
  reliable, 0.12–0.40 caution, over 0.40 unreliable.
  [place-people](place-people/AGENTS.md) has **no `_cv` columns at all** — use
  `_moe` there.
- **A `_cv` gate silently drops zero estimates.** The CV is undefined when the
  estimate is 0, so `WHERE pct_commute_transit_cv < 0.15` excludes all 22,895
  places whose transit share is exactly 0 (measured, in
  [place-connectivity](place-connectivity/AGENTS.md)). Write the zeros back in
  if you need them.
- **Never sum or average a median.** A region's median is not derivable from
  its parts'. To sum counts, add margins in quadrature (`sqrt(sum(moe*moe))`).
  A place's overall `median_hh_income` can sit below every race-specific
  median it contains — three universes, not a weighted average (measured, in
  [place-wellbeing](place-wellbeing/AGENTS.md)).
- **A place can have 0 households and thousands of residents.** Three places
  are 100.0% group quarters — Stony Brook University CDP (9,530 people),
  University CDP, Mississippi (5,315) and Binghamton University CDP (7,449) —
  and every household-denominated column on those rows is NULL because the
  universe is empty, not because anything was suppressed. A population floor
  does not exclude them.
- **`pct_vacant_units` is not an abandonment measure.** B25002 counts
  for-sale, for-rent, seasonal and migrant-worker units as vacant, so Ocean
  City town, Maryland reports 29,811 housing units, 6,903 residents and 87.16%
  vacant (measured).
- Jam values are already NULL. No jam filtering is needed, but NULLs reduce
  the row count of an aggregate and `avg()` skips them silently.
- Percentages are 0–100, not 0–1, and their margins are on the same scale. At
  this geography a percentage's margin can exceed 100 points — a flag to drop
  the row, not a value.
- `population` is the ACS 5-year estimate (B01003), not a 2020 Decennial
  count.
- **282 places carry geometry and NULL ACS values**: 279 in the island areas
  (MP 135, AS 77, GU 57, VI 10, measured), `3608026` Brentwood CDP and
  `3683294` Wyandanch CDP in re-delineated Suffolk County, New York, and
  `2148000` Louisville city. `ORDER BY … DESC` needs `NULLS LAST` or they sort
  first.
- Row count is the boundary file's own feature count, 32,612. For scale, the
  Census Bureau's
  [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html)
  give 19,734 incorporated places and 12,454 CDPs (32,188) for the 2020
  vintage; the 2024 vintage is four years of incorporations, dissolutions and
  CDP re-delineations later.
- Geometry is the 500k cartographic boundary files, shoreline-clipped,
  EPSG:4326 — good for mapping and point-in-polygon, not for area measurement.
- PMTiles z0–z5 are **counties**, not places — the Census Bureau's own county
  estimates under the same column names, so one style classifies every zoom —
  and z6–z12 are the places themselves. Places do not nest in counties, so the
  county band is national orientation and **not** a roll-up of these files. The
  tiles carry no `*_moe` columns; `*_cv` columns are kept. Statistics come from
  the GeoParquet, always.
- Spot-checked against data.census.gov: Los Angeles city population 3,857,263
  and median home value $921,200; New York city population 8,483,844.

## Where to look next

- Per-collection schemas, NULL stories and 4–5 tested recipes each:
  [place-income](place-income/AGENTS.md),
  [place-people](place-people/AGENTS.md),
  [place-housing](place-housing/AGENTS.md),
  [place-connectivity](place-connectivity/AGENTS.md),
  [place-wellbeing](place-wellbeing/AGENTS.md).
- All 112 columns in one table, with wall-clock timings against the mirror and
  the biggest-places and rent-burden rankings:
  [places](places/AGENTS.md).
- The population floor measured by size band, the margin-overlap test between
  two small places, and the state prefix join:
  [place-income](place-income/AGENTS.md).
- The 23 Springfields and what an ungated ranking returns:
  [place-people](place-people/AGENTS.md).
- Cross-geography showcases, and the most rent-burdened large cities with each
  city's state rate beside it: [catalog AGENTS.md](../AGENTS.md).

## License

CC0-1.0. Census Bureau data is a U.S. Government work in the public domain;
this mirror adds nothing proprietary. [data.census.gov](https://data.census.gov/)
is authoritative and nothing here is an official Census Bureau product — cite
the U.S. Census Bureau when you use the numbers.
