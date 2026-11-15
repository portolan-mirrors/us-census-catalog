# Agent guide — Commuting & Connectivity (States)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

How people get around and get online: households with no vehicle available, as a count and a share ([B25044](https://data.census.gov/table/ACSDT5Y2024.B25044)); commute mode shares for driving alone, public transportation, walking or cycling, and working from home ([B08301](https://data.census.gov/table/ACSDT5Y2024.B08301)); the share of commutes of 45 minutes or more ([B08303](https://data.census.gov/table/ACSDT5Y2024.B08303)); and the shares of households with no internet access and no computing device ([B28002](https://data.census.gov/table/ACSDT5Y2024.B28002), [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001)).

**56 rows** — the 50 states, the District of Columbia, Puerto Rico and the four
island areas — ACS 2020–2024 5-year estimates, geometry from the 2024
cartographic boundary files. **52 of the 56 carry ACS data**; the four island
areas carry geometry and NULLs.

This is the collection where state-level reliability matters most.
`pct_commute_transit` is the noisiest column in the catalog: at county level its
median coefficient of variation is 0.608 and 69.9% of the counties that publish
one are above the 0.40 "unreliable" line; at tract level the median is 0.685 and
79.2% are unreliable. At state level the median is **0.037**, the maximum is
**0.197**, and nothing is above 0.40 — all measured in recipe 1. If a transit
question has to produce a defensible number, this is the file that can.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.pmtiles`, layer `state-connectivity`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/collection.json` — carries a full description for every column

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
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B08301](https://data.census.gov/table/ACSDT5Y2024.B08301) | Means of Transportation to Work | Workers 16 years and over |
| [B08303](https://data.census.gov/table/ACSDT5Y2024.B08303) | Travel Time to Work | Workers 16 years and over who did not work from home |
| [B25044](https://data.census.gov/table/ACSDT5Y2024.B25044) | Tenure by Vehicles Available | Occupied housing units |
| [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001) | Types of Computers in Household | Households |
| [B28002](https://data.census.gov/table/ACSDT5Y2024.B28002) | Presence and Types of Internet Subscriptions in Household | Households |

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

- **Every estimate here has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. The one exception in this collection is
  `population_moe`, which is **NULL on all 56 rows** (measured); it is carried
  as context, not as a usable margin, and
  `sqrt(sum(population_moe*population_moe))` over these rows returns NULL.
  `hh_no_vehicle_moe` and every commute and internet margin are populated on
  all 52 rows with data.
- **That NULL is upstream, and it is not suppression.** `population` comes
  from a total-population table (B01003), and in the release's own
  `.dat` files those rows carry the estimate beside `-555555555`, the
  **controlled-MOE** jam value a controlled estimate gets in place of a
  sampling margin — `0400000US06|39287377|-555555555` in
  `staging/census-cache/acsdt5y2024-b01003.dat`, read 2026-11-15. The build
  turns it into NULL rather than publishing it as a number
  (`tools/build_acs.py`). The same column carries a margin normally at the
  finer geographies, where the estimates are not controlled this way:
  `population_moe` is carried on 33,759 of 33,791 ZCTAs and on all 241,854
  populated block groups (measured).
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. At this geography the worst values are 0.197
  (`pct_commute_transit_cv`), 0.049 (`pct_hh_no_vehicle_cv`) and 0.048
  (`pct_no_internet_cv`), all measured — no filtering is needed here, which is
  not true of this theme at any finer geography.
- **`pct_commute_45min_plus` divides by workers who did not work from home**
  (B08303's own universe), while every other commute share divides by all
  workers 16+ (B08301). The two denominators differ, so the shares do not sum
  across tables, and working from home does not deflate the long-commute share.
- **The four published B08301 shares are not exhaustive.**
  `pct_commute_drive_alone` + `pct_commute_transit` + `pct_commute_walk_bike` +
  `pct_work_from_home` sums to between 83.71 and 93.39 across the 52 rows with
  data (measured). The remainder is the B08301 categories this collection does
  not publish: carpooling (the rest of "Car, truck, or van" below the
  drove-alone line), taxicab and ride-hailing, motorcycle, and other means.
  Never normalise the four to 100.
- **`pct_commute_transit` excludes taxi and ride-hailing.** It is B08301's
  "Public transportation" line — bus, subway and elevated rail, light rail,
  commuter rail, ferryboat — and taxi/ride-hailing is a separate line in this
  vintage.
- **`hh_no_vehicle` is a count of households, `pct_hh_no_vehicle` a share of
  occupied housing units.** They rank differently and answer different
  questions (recipe 5): a car-free household of four counts once.
- **`pct_no_internet` counts households with no access of any kind**;
  households that use the internet without paying for a subscription are
  counted as *having* access, so this is not a measure of unaffordable
  broadband.
- **A state's value is the Census Bureau's own estimate for the state**, not a
  sum or average of its counties. Counts nest and add up — county `households`
  sums exactly to the state row for all 52 states, measured in
  [`state-housing`](../state-housing/AGENTS.md) — but shares and medians do
  not, and the Bureau's state margin is its own.
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.

## Data quality

Columns with notable missingness at this geography (measured over the file as
built, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 4 of 56 rows (7.14%): American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have boundaries here but no ACS 5-year data, because the island areas run a separate decennial-only program. 52 rows carry data. |
| every other ACS column | NULL on exactly the same 4 rows. Nothing in this collection is suppressed: `hh_no_vehicle`, all four commute-mode shares, `pct_commute_45min_plus`, `pct_no_internet` and `pct_no_computer` are each published on all 52 rows with data (measured). |
| `population_moe` | NULL on all 56 rows — see the field notes. |

`pct_commute_transit_cv` is published on all 52 rows here. At finer geographies
it is not: 2,417 of 3,235 counties and 43,264 of 85,184 tracts publish one at
all (measured), because a CV needs a non-zero estimate and in most of the
country nobody commutes by transit. A national transit map drawn from tracts is
drawn on half the tracts; a national transit comparison drawn from this file
uses every row.

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern
Mariana Islands and the U.S. Virgin Islands have cartographic boundaries but no
ACS 5-year estimates, so their rows publish with NULL values rather than being
dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 17
ZCTAs, 279 places and 4 delegate districts.

The PMTiles archive is real state polygons at every zoom, band `0-8:geom`
(`tools/make_tiles.py`) — there is no coarser-geography band at coarse zooms,
because 56 features tile directly. `*_moe` columns are excluded from every tile
at every zoom; `*_cv` columns are kept. Statistics come from the GeoParquet,
always.

## Related collections

- [`states/state-income`](../state-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`states/state-people`](../state-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`states/state-housing`](../state-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`states/state-wellbeing`](../state-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`states/states`](../states/collection.json) ([agent guide](../states/AGENTS.md)) — the sixth sibling: all 112 columns in one table, same 56 rows, data files one directory up.
- [`counties/county-connectivity`](../../counties/county-connectivity/collection.json), [`tracts/tract-connectivity`](../../tracts/tract-connectivity/collection.json) and [`block-groups/bg-connectivity`](../../block-groups/bg-connectivity/collection.json) — the same theme at finer geographies, where `pct_commute_transit` becomes unreliable for most rows.
- [`zctas/zcta-connectivity`](../../zctas/zcta-connectivity/collection.json), [`places/place-connectivity`](../../places/place-connectivity/collection.json), [`congressional-districts/cd-connectivity`](../../congressional-districts/cd-connectivity/collection.json) — the same theme at the other statistical geographies.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no commuting or internet variables.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

Instead, the cost: 56 rows and 3.9 MB, of which 3.86 MB is geometry. No filter
is ever needed here for cost.

### 1. Where a transit question can actually be answered (`*_cv`, three files)

```sql
INSTALL httpfs; LOAD httpfs;
SELECT 'state' AS geography, count(pct_commute_transit_cv) AS n,
       round(quantile_cont(pct_commute_transit_cv, 0.5), 3) AS median_cv,
       round(max(pct_commute_transit_cv), 3) AS max_cv,
       round(100.0*count(*) FILTER (WHERE pct_commute_transit_cv > 0.40)
             / count(pct_commute_transit_cv), 1) AS pct_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet'
UNION ALL
SELECT 'county', count(pct_commute_transit_cv),
       round(quantile_cont(pct_commute_transit_cv, 0.5), 3), round(max(pct_commute_transit_cv), 3),
       round(100.0*count(*) FILTER (WHERE pct_commute_transit_cv > 0.40) / count(pct_commute_transit_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet'
UNION ALL
SELECT 'tract', count(pct_commute_transit_cv),
       round(quantile_cont(pct_commute_transit_cv, 0.5), 3), round(max(pct_commute_transit_cv), 3),
       round(100.0*count(*) FILTER (WHERE pct_commute_transit_cv > 0.40) / count(pct_commute_transit_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.parquet';
```

→

```
state  |    52 | 0.037 | 0.197 |  0.0
county |  2417 | 0.608 | 9.119 | 69.9
tract  | 43264 | 0.685 |18.997 | 79.2
```

Three facts in one result. The state median CV is 0.037 against 0.608 and
0.685; nothing at state level is unreliable while seven counties in ten and
four tracts in five are; and `n` falls from every row to 2,417 of 3,235
counties and 43,264 of 85,184 tracts, because a CV needs a non-zero estimate.
Transit is the column that most rewards stepping up a geography. The ranking it
supports:

```sql
LOAD httpfs;
SELECT name, pct_commute_transit, round(pct_commute_transit_cv, 3) AS cv,
       pct_commute_drive_alone, pct_work_from_home, pct_commute_45min_plus
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet'
WHERE pct_commute_transit IS NOT NULL
ORDER BY pct_commute_transit DESC LIMIT 5;
```

→ `New York | 21.6 | 0.003 | 48.77 | 14.93 | 27.42`,
`District of Columbia | 20.28 | 0.02 | 27.38 | 33.0 | 19.01`,
`New Jersey | 8.12 | 0.009 | 62.22 | 16.83 | 23.39`,
`Massachusetts | 6.51 | 0.011 | 61.19 | 18.64 | 21.51`,
`Illinois | 5.83 | 0.009 | 65.85 | 15.86 | 19.73`.

New York and DC are in a class of their own and then it falls off a cliff — a
linear colour ramp on this column will show two states. Carrying
`pct_commute_drive_alone` alongside is a free sanity check: the two shares
share the B08301 denominator, so they must trade off, and they do.

### 2. The four commute shares do not sum to 100

```sql
LOAD httpfs;
SELECT name,
       round(pct_commute_drive_alone + pct_commute_transit + pct_commute_walk_bike
             + pct_work_from_home, 2) AS four_b08301_shares,
       pct_commute_45min_plus
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet'
WHERE pct_commute_transit IS NOT NULL
ORDER BY four_b08301_shares DESC LIMIT 3;
```

→ `District of Columbia | 93.39 | 19.01`, `Puerto Rico | 92.05 | 18.73`,
`New Hampshire | 91.8 | 17.21`.

```sql
LOAD httpfs;
SELECT min(pct_commute_drive_alone + pct_commute_transit + pct_commute_walk_bike + pct_work_from_home) AS min_sum,
       max(pct_commute_drive_alone + pct_commute_transit + pct_commute_walk_bike + pct_work_from_home) AS max_sum
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet';
```

→ `83.71 | 93.39`. The best-covered state accounts for 93% of its workers and
the worst for 84%. The missing share is the B08301 categories this collection
does not publish — carpooling above all, plus taxicab and ride-hailing,
motorcycle and other means. So: never normalise these four to 100, and never
infer carpooling by subtraction without saying that the residual also contains
three other modes. `pct_commute_45min_plus` is in the same result for contrast
and must **not** be added to any of them: it divides by workers who did not
work from home (B08303's universe), a different denominator entirely.

### 3. Who is offline, and by how much (`*_cv`-gated ranking)

```sql
LOAD httpfs;
SELECT name, pct_no_internet, round(pct_no_internet_cv, 3) AS cv, pct_no_computer,
       hh_no_vehicle, pct_hh_no_vehicle
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet'
WHERE pct_no_internet IS NOT NULL
ORDER BY pct_no_internet DESC LIMIT 5;
```

→ `Puerto Rico | 16.92 | 0.009 | 15.02 | 167247 | 12.96`,
`Mississippi | 12.3 | 0.014 | 7.31 | 72244 | 6.31`,
`West Virginia | 10.89 | 0.017 | 8.82 | 58654 | 8.05`,
`Louisiana | 10.74 | 0.011 | 6.67 | 152488 | 8.45`,
`Arkansas | 10.47 | 0.013 | 6.36 | 70570 | 5.85`.

`pct_no_internet` and `pct_no_computer` are close in Puerto Rico (16.92 against
15.02) and far apart in Mississippi (12.3 against 7.31): households with a
device and no connection are a different population from households with
neither, and the gap between the two columns is the interesting quantity.
Remember that households using the internet without paying for a subscription
count as having access, so neither column measures affordability.

### 4. Every county against its own state (GEOID prefix join)

```sql
LOAD httpfs;
SELECT c.name AS county, s.name AS state, c.pct_no_internet AS county_pct,
       s.pct_no_internet AS state_pct,
       round(c.pct_no_internet - s.pct_no_internet, 2) AS points_above_state
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet' c
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet' s
  ON s.geoid = substr(c.geoid, 1, 2)
WHERE c.pct_no_internet IS NOT NULL AND s.pct_no_internet IS NOT NULL
ORDER BY points_above_state DESC LIMIT 5;
```

→ `Maricao Municipio, Puerto Rico | Puerto Rico | 60.51 | 16.92 | 43.59`,
`Las Marías Municipio, Puerto Rico | Puerto Rico | 58.8 | 16.92 | 41.88`,
`Claiborne Parish, Louisiana | Louisiana | 45.37 | 10.74 | 34.63`,
`Apache County, Arizona | Arizona | 36.41 | 6.03 | 30.38`,
`Lunenburg County, Virginia | Virginia | 36.85 | 6.71 | 30.14`.

`s.geoid = substr(c.geoid, 1, 2)` is the whole join — a county GEOID begins
with its state's FIPS code. This "each X against its own state" shape is what
the state files are for: they are the denominator every finer geography gets
compared against, and the same prefix reaches tracts and block groups. Note
what the state figure hides: Arizona's 6.03% contains a county at 36.41%.

### 5. The car-free count and the car-free share rank differently

```sql
LOAD httpfs;
SELECT name, hh_no_vehicle, pct_hh_no_vehicle, round(pct_hh_no_vehicle_cv, 3) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet'
WHERE hh_no_vehicle IS NOT NULL
ORDER BY hh_no_vehicle DESC LIMIT 5;
```

→ `New York | 2256981 | 29.23 | 0.003`, `California | 959291 | 7.08 | 0.005`,
`Texas | 598470 | 5.44 | 0.008`, `Illinois | 552555 | 10.97 | 0.007`,
`Pennsylvania | 549478 | 10.42 | 0.008`.

Now the same file by share, `ORDER BY pct_hh_no_vehicle DESC`:

→ `District of Columbia | 116851 | 36.01`, `New York | 2256981 | 29.23`,
`Puerto Rico | 167247 | 12.96`, `Massachusetts | 326673 | 11.73`,
`New Jersey | 389559 | 11.11`.

California has the second-largest car-free *population* and does not appear in
the top five by *share*; the District of Columbia leads by share with 116,851
car-free households against California's 959,291. "Where should transit
investment go" and "where is car-free
living normal" are different questions with different columns, and the count is
the one that sizes a programme. The share's denominator is occupied housing
units, not people — a car-free household of four counts once.

### Related recipes elsewhere

- The same columns at tract level, including the dormitory trap where
  `pct_no_internet` is 100.0 with a margin of exactly 0.0:
  [`tracts/tract-connectivity/AGENTS.md`](../../tracts/tract-connectivity/AGENTS.md).
- Transit and car ownership at county level, with every county against its
  state:
  [`counties/county-connectivity/AGENTS.md`](../../counties/county-connectivity/AGENTS.md).
- Density against car ownership and transit, nationally:
  [`catalog/AGENTS.md`](../../AGENTS.md).
- All 112 state columns in one table, with recipes timed against the published
  mirror: [`states/states/AGENTS.md`](../states/AGENTS.md).
- What this geography is for and when to step down from it:
  [`states/AGENTS.md`](../AGENTS.md).

Statistics come from the GeoParquet. The state PMTiles archive is real polygons
at every zoom — it needs no coarser-geography band — but carries no `*_moe`
columns, so none of the margin arithmetic above can be reproduced from tiles.
