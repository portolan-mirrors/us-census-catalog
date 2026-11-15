# Agent guide — States

Guidance for AI agents and automated clients working with this geography.

**Every claim in this file is quoted from a source or measured from the data.**
The catalog-level [AGENTS.md](../AGENTS.md) covers what spans geographies, and
each collection's own `AGENTS.md` carries its columns, NULL rates and tested
queries. This file covers what the six collections share. If you cannot point
at where a fact came from, it does not belong here.

## What this geography is

A state is the coarsest geography in this catalog, and **these are the smallest
and most reliable files in it**. 56 rows: the 50 states, the District of
Columbia, Puerto Rico and the four island areas (American Samoa, Guam, the
Northern Mariana Islands, the U.S. Virgin Islands), ACS 2020–2024 5-year
estimates, geometry from the 2024 cartographic boundary files. **52 of the 56
carry ACS data**; the island areas run a separate decennial-only program, so
they publish boundaries and NULLs.

What that buys: no estimate here needs a reliability filter. Across all 15
`*_cv` columns the highest median is **0.037** (`pct_commute_transit`) and the
single worst value anywhere in the wide table is **0.213**
(`pct_below_poverty_black`) — both measured, against a 0.40 "unreliable" line.
Nothing is suppressed either: 95 of the wide table's 112 columns are published
on all 52 rows with data, and **all four race-iteration medians are published
for every one of those 52 rows**, which is true at no other geography (60.77%
of counties and 38.63% of tracts for the Black-householder median, measured).

What it does not buy: resolution. 52 rows answer "how do states compare" and
never "what is this neighbourhood like". A state median describes no particular
place inside the state — Kentucky's richest county has 5.5× the median income
of its poorest (measured in
[state-income](state-income/AGENTS.md)) — and even a comparison between two
states is weaker than the tiny CVs suggest: of the 51 adjacent pairs in a
ranking of the 52 states by `median_hh_income`, only 15 have non-overlapping
90% intervals (measured). There is also one gap the small margins do not
explain: **`population_moe` is NULL on all 56 rows**, along with ten other
margins (see Shared quirks).

**These files are the denominator every finer geography gets compared against.**
The recipe shape to reach for is the prefix join — each county, tract or block
group against its own state — and every collection guide here carries one.

## Six collections, one geography

The same five themed collections as [tracts](../tracts/AGENTS.md), plus the
whole 112-column table as a sixth:

| collection | columns | theme | headline columns |
|---|---|---|---|
| [state-income](state-income/collection.json) ([agent guide](state-income/AGENTS.md)) | 23 | Income & Poverty | `median_hh_income`, `per_capita_income`, `pct_below_poverty`, `pct_snap`, `pct_unemployed` |
| [state-people](state-people/collection.json) ([agent guide](state-people/AGENTS.md)) | 29 | People & Education | `median_age`, `pct_under_18`, `pct_65_plus`, the four non-Hispanic race shares, `pct_hispanic`, `pct_bachelors_plus` |
| [state-housing](state-housing/collection.json) ([agent guide](state-housing/AGENTS.md)) | 32 | Housing & Rent | `housing_units`, `households`, `pct_owner_occupied`, `median_gross_rent`, `median_home_value`, `pct_rent_burdened` |
| [state-connectivity](state-connectivity/collection.json) ([agent guide](state-connectivity/AGENTS.md)) | 30 | Commuting & Connectivity | `hh_no_vehicle`, the B08301 commute-mode shares, `pct_commute_45min_plus`, `pct_no_internet`, `pct_no_computer` |
| [state-wellbeing](state-wellbeing/collection.json) ([agent guide](state-wellbeing/AGENTS.md)) | 34 | Health, Disability & Income by Race | `pct_uninsured`, `pct_with_disability`, `pct_foreign_born`, `group_quarters_pop`, `median_hh_income_{black,white_nh,asian,hispanic}`, `pct_below_poverty_black` |
| [states](states/collection.json) ([agent guide](states/AGENTS.md)) | 112 | **all of the above**, one row per state | everything above, no join needed |

Every chunk carries the same seven context columns — `geoid`, `name`, `state`,
`population`, `population_moe`, `aland_sqkm`, `pop_density` — plus `geometry`
and the `bbox` covering struct, so a single-theme question never needs a join.

**Two things about the layout.** First, the five themed children keep their
`*.parquet` and `*.pmtiles` beside their metadata, at
`…/states/<cid>/<cid>.parquet`; the wide `states` collection's data files sit
one directory **up**, at `…/states/states.parquet` and
`…/states/states.pmtiles`, beside this group's `catalog.json`. Those two URLs
are unchanged from before the group was split. Every child's STAC collection,
the wide one included, is at `…/states/<cid>/collection.json`.

Second, at this geography chunking saves almost nothing. `geometry` is 3.86 MB
of a themed file's 3.88 MB (measured from the Parquet column metadata), and the
wide 112-column table is only about 49 KB larger than the narrowest chunk.
**Prefer [`states`](states/AGENTS.md) for anything cross-theme**; prefer a
themed chunk when a narrow schema, a single style, or one subject's tiles is
the point.

## The chunks join 1:1 on `geoid`

All six hold the same 56 `geoid` values with the same geometry. Measured:

```sql
LOAD httpfs;
SELECT (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet')             AS income,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet')             AS people,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet')           AS housing,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet') AS connectivity,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet')       AS wellbeing,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet')                                AS wide;
```

→ `56 | 56 | 56 | 56 | 56 | 56`. And the `geoid` sets are identical, not merely
the same size:

```sql
LOAD httpfs;
SELECT count(*) AS geoids_in_all_six FROM (
  SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet');
```

→ `56`. So `JOIN … USING (geoid)` loses nothing. A full cross-theme profile of
one state is one query across the five chunks:

```sql
LOAD httpfs;
SELECT i.geoid, i.name, i.median_hh_income::int AS income, i.pct_below_poverty AS poverty,
       p.median_age, p.pct_bachelors_plus AS degree, h.median_gross_rent::int AS rent,
       c.pct_commute_transit AS transit, w.pct_uninsured AS uninsured
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet' i
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet'             p USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet'           h USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet' c USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet'       w USING (geoid)
WHERE i.geoid = '53';
```

→ `53 | Washington | 98141 | 9.9 | 38.3 | 39.61 | 1760 | 3.45 | 6.34`.

Both queries were run with DuckDB 1.4.1 against these files as built,
immediately before they were written down, and their real output is quoted. The
URLs above are the published ones; the runs swapped in the local `catalog/`
paths, because the five themed collections had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted. (The
wide [`states`](states/AGENTS.md) guide does quote timings: its data files were
already on the mirror and the restructure did not move them.)

**At this geography, do not write that join.** The identical row is one
`SELECT` from [`states`](states/collection.json), which costs about 49 KB more
than any single chunk. The join above is shown because it is the shape that
matters at tract and block-group level, where the wide table does not exist.

GEOIDs nest by prefix, and this is the top of the chain: a state's `geoid` is
2 characters, and every finer geography's `substr(geoid, 1, 2)` is this column
— counties (5 characters), tracts (11), block groups (12), blocks (15),
congressional districts (4) and places (7) all begin with their state's FIPS
code. **ZCTAs do not**: they nest in nothing, their `state` column is NULL on
all 33,791 rows, and the first two characters of a ZCTA code are a postal
region, not a state FIPS code. `state` is also a column here, with the USPS
code.

## When to step up or down a geography

There is nothing to step up to — this catalog publishes no national row, and a
national figure cannot be built from these 52 (see Shared quirks). So the only
question is when to step down.

Suppression, measured over the same columns at the three coarsest levels:

| column | NULL at state | NULL at county | NULL at tract |
|---|---|---|---|
| `median_hh_income` | 7.14% | 0.43% | 1.59% |
| `median_gross_rent` | 7.14% | 0.62% | 5.92% |
| `median_home_value` | 7.14% | 0.56% | 3.55% |
| `median_hh_income_black` | 7.14% | 39.47% | 61.43% |

Read the first column carefully: the 7.14% is **4 island-area rows out of only
56**, identical for every ACS column, and not suppression. Of the 52 rows that
have ACS data, nothing is missing. Counties are the level with the best row
coverage; states are the level with no holes in the rows it covers.

Reliability, measured:

| `*_cv` column | median at state | at county | at tract |
|---|---|---|---|
| `median_hh_income_cv` | 0.004 (max 0.011) | 0.042 (max 0.530) | 0.125 (max 0.607) |
| `pct_commute_transit_cv` | 0.037 (max 0.197) | 0.608, 69.9% unreliable | 0.685, 79.2% unreliable |

- **Stay here** when the answer will be quoted as a single number, when the
  subject is a race-iteration median or a noisy share like
  `pct_commute_transit`, or when 50-odd comparable units are exactly the frame
  of the question.
- **Step down to [counties](../counties/AGENTS.md)** for the first real
  resolution: 3,235 rows, `median_hh_income_cv` still a median 0.042, and the
  race-iteration medians published on 60.77% of rows. This is usually the right
  next step, and county rows sum exactly to the state row for counts (measured
  in [state-housing](state-housing/AGENTS.md)).
- **Step down to [tracts](../tracts/AGENTS.md)** when the question is about
  neighbourhoods. 85,184 rows, wider margins, and the finest geography at which
  health insurance, disability, nativity and income by race are published at
  all.
- **[Block groups](../block-groups/AGENTS.md)** only when the question is
  genuinely sub-tract, and with no twin for the wellbeing theme.
- **Sideways** to [ZCTAs](../zctas/AGENTS.md),
  [places](../places/AGENTS.md) or
  [congressional districts](../congressional-districts/AGENTS.md) when the unit
  of the question is a postal area, a municipality or a district rather than a
  nesting statistical area.
- **[Blocks](../blocks/AGENTS.md)** carry 2020 Decennial counts only — a
  different survey and vintage, not a finer version of these numbers. They do
  sum to published state totals exactly, which these ACS estimates do not
  claim to.

## Shared quirks

- **Eleven margin columns are NULL on all 56 rows** (measured across the six
  collections): `population_moe`, `pct_under_18_moe`, `pct_65_plus_moe`,
  `pct_white_nh_moe`, `pct_black_moe`, `pct_native_moe`, `pct_asian_moe`,
  `pct_hispanic_moe`, `pct_people_of_color_moe`, `pct_foreign_born_moe` and
  `group_quarters_pop_moe`. Every one is a count of, or a share of, the total
  population. **That NULL is upstream and it is not suppression**: each of
  those columns comes from a total-population table (B01001, B01003, B03002,
  B05002, B26001), and in the release's own `.dat` files those rows carry the
  estimate beside `-555555555`, the **controlled-MOE** jam value a controlled
  estimate gets in place of a sampling margin —
  `0400000US06|39287377|-555555555` in
  `staging/census-cache/acsdt5y2024-b01003.dat`, read 2026-11-15 — and the
  build turns it into NULL rather than publishing it as a number
  (`tools/build_acs.py`). The same columns carry margins normally further down:
  `population_moe` is carried on 33,759 of 33,791 ZCTAs and on all 241,854
  populated block groups (measured). So at state level a significance test on
  an age share, a race share, the foreign-born share or the group-quarters
  count is not possible at all. Read `population` as a count to use rather than
  an estimate to put an interval on, and remember that
  `sqrt(sum(moe*moe))` over any of those columns returns NULL rather than a
  number. Every other margin is populated on all 52 rows with data.
- **`state-people` has no `_cv` columns at all** (measured), as at tract level
  — use `_moe` there. It is also the collection where most of the missing
  margins live: eight of its ten estimates have no margin at all here, leaving
  only `median_age` and `pct_bachelors_plus` testable.
- Every other estimate carries `<name>_moe` at the **90%** confidence level.
  Headline columns also carry `<name>_cv` = `moe / 1.645 / estimate`: under
  0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. **At this geography
  no `_cv` filter is needed** — the worst value in the catalog's widest state
  table is 0.213 — but the columns exist so one style or one query runs at
  every geography. Breaks measured here will be useless at tract level.
- **A state's value is estimated directly by the Census Bureau**; it is not the
  sum or the average of its counties. Counts do nest and add: county
  `households` sums exactly to the state row for all 52 states (measured). The
  *margins* do not — the quadrature margin of that county sum matches the
  state's published margin for exactly 1 of the 52 states and is narrower for
  49 (measured in [state-housing](state-housing/AGENTS.md)). `sqrt(sum(moe*moe))`
  puts a margin on *your* sum; it does not reproduce the Bureau's.
- **Never sum or average a median.** A region's median is not derivable from
  its parts', in either direction: a national median cannot be built from these
  52 rows (the quantity does not exist in this catalog), and a state median is
  not an average of its counties' — the mean of Texas's 254 county medians is
  $11,994 below the published state median (measured in
  [state-income](state-income/AGENTS.md)).
- **Small CVs are not significant differences.** Only 15 of the 51 adjacent
  pairs in the `median_hh_income` ranking have non-overlapping 90% intervals
  (measured). Test the pair you are about to report.
- Jam values are already NULL. No jam filtering is needed, but NULLs reduce the
  row count of an aggregate and `avg()` skips them silently — and with 52 rows
  one skipped row is 2% of the sample.
- Percentages are 0–100, not 0–1, and their margins are on the same scale.
- The four non-Hispanic race shares plus `pct_hispanic` are mutually exclusive
  but **not exhaustive**: they sum to between 69.12 and 99.78 across the 52
  rows (measured). `pct_people_of_color` is the exact complement of
  `pct_white_nh` and is the exhaustive split.
- `population` is the ACS 5-year estimate (B01003), not a 2020 Decennial count,
  and will not match `blocks`' `pop_total` summed over the same area.
- 4 island-area rows carry geometry and NULL ACS values. The same gap runs down
  the catalog: 13 county equivalents, 126 tracts, 405 block groups, 17 ZCTAs,
  279 places and 4 delegate districts.
- Geometry is the 500k cartographic boundary files (GENZ2024), shoreline-clipped,
  EPSG:4326 — good for mapping and point-in-polygon, not for area measurement.
  Use `aland_sqkm`, which comes from the boundary file's `ALAND`, as the
  density denominator.
- PMTiles are **real state polygons at every zoom**, band `0-8:geom`
  (`tools/make_tiles.py`) — 56 features tile directly, so unlike the catalog's
  finer collections there is no coarser-geography band at coarse zooms.
  `*_moe` columns are excluded from every tile at every zoom; `*_cv` columns
  are kept. Statistics come from the GeoParquet, always.

## Where to look next

- Per-collection schemas, NULL stories and 4–5 tested recipes each:
  [state-income](state-income/AGENTS.md), [state-people](state-people/AGENTS.md),
  [state-housing](state-housing/AGENTS.md),
  [state-connectivity](state-connectivity/AGENTS.md),
  [state-wellbeing](state-wellbeing/AGENTS.md).
- All 112 columns in one table, and the only recipes in this group with real
  network timings: [states](states/AGENTS.md).
- The prefix-join shape — each X against its own state — in each themed guide,
  and at the geography below:
  [counties](../counties/AGENTS.md).
- Income by race published for every row, which happens nowhere else:
  [state-wellbeing](state-wellbeing/AGENTS.md).
- Cross-collection showcases and what spans geographies:
  [catalog AGENTS.md](../AGENTS.md).

## License

CC0-1.0. Census Bureau data is a U.S. Government work in the public domain;
this mirror adds nothing proprietary. [data.census.gov](https://data.census.gov/)
is authoritative and nothing here is an official Census Bureau product — cite
the U.S. Census Bureau when you use the numbers.
