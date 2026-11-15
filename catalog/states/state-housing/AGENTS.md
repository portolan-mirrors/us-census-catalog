# Agent guide — Housing & Rent (States)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

The housing stock and what it costs: total units and the vacancy rate ([B25002](https://data.census.gov/table/ACSDT5Y2024.B25002)), households and the owner-occupied share ([B25003](https://data.census.gov/table/ACSDT5Y2024.B25003)), median gross rent ([B25064](https://data.census.gov/table/ACSDT5Y2024.B25064)) and median owner-occupied home value ([B25077](https://data.census.gov/table/ACSDT5Y2024.B25077)), the share of renter households paying 30% and 50% or more of income on rent ([B25070](https://data.census.gov/table/ACSDT5Y2024.B25070)), the pre-1940 share ([B25034](https://data.census.gov/table/ACSDT5Y2024.B25034)) and the single-family share ([B25024](https://data.census.gov/table/ACSDT5Y2024.B25024)).

**56 rows** — the 50 states, the District of Columbia, Puerto Rico and the four
island areas — ACS 2020–2024 5-year estimates, geometry from the 2024
cartographic boundary files. **52 of the 56 carry ACS data**; the four island
areas carry geometry and NULLs.

Housing is where this geography's reliability shows up most sharply.
`median_gross_rent` is NULL on 29.68% of block groups and 5.92% of tracts; here
it is published for every one of the 52 rows that have ACS data, with a worst
coefficient of variation of **0.010** (all measured). This is also the
collection that holds the catalog's cleanest rollup check: county `households`
sums exactly to the state row for all 52 states, while the quadrature margin of
that sum is *not* the state's published margin. Recipe 2 measures both.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.pmtiles`, layer `state-housing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/collection.json` — carries a full description for every column

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
| [B25002](https://data.census.gov/table/ACSDT5Y2024.B25002) | Occupancy Status | Housing units |
| [B25003](https://data.census.gov/table/ACSDT5Y2024.B25003) | Tenure | Occupied housing units |
| [B25024](https://data.census.gov/table/ACSDT5Y2024.B25024) | Units in Structure | Housing units |
| [B25034](https://data.census.gov/table/ACSDT5Y2024.B25034) | Year Structure Built | Housing units |
| [B25064](https://data.census.gov/table/ACSDT5Y2024.B25064) | Median Gross Rent (Dollars) | Renter-occupied housing units paying cash rent |
| [B25070](https://data.census.gov/table/ACSDT5Y2024.B25070) | Gross Rent as a Percentage of Household Income in the Past 12 Months | Renter-occupied housing units |
| [B25077](https://data.census.gov/table/ACSDT5Y2024.B25077) | Median Value (Dollars) | Owner-occupied housing units |

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
| `housing_units` | int64 | Total housing units, occupied and vacant. |
| `housing_units_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `housing_units`. |
| `pct_vacant_units` | double | Percent of housing units that are vacant. |
| `pct_vacant_units_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_vacant_units`. |
| `households` | int64 | Households — occupied housing units. |
| `households_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `households`. |
| `pct_owner_occupied` | double | Percent of occupied housing units that are owner-occupied. |
| `pct_owner_occupied_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_owner_occupied`. |
| `median_gross_rent` | double | Median gross rent in dollars per month — contract rent plus the estimated average monthly cost of utilities and fuels. |
| `median_gross_rent_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_gross_rent`. |
| `median_gross_rent_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_gross_rent`. |
| `pct_rent_burdened` | double | Percent of renter households paying 30% or more of household income on gross rent — the standard affordability threshold. |
| `pct_rent_burdened_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_rent_burdened`. |
| `pct_rent_burdened_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_rent_burdened`. |
| `pct_severely_rent_burdened` | double | Percent of renter households paying 50% or more of household income on gross rent. |
| `pct_severely_rent_burdened_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_severely_rent_burdened`. |
| `median_home_value` | double | Median value of owner-occupied housing units, in dollars — the owner's estimate of what the property would sell for, not an assessment or a sale price. |
| `median_home_value_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_home_value`. |
| `median_home_value_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_home_value`. |
| `pct_built_pre_1940` | double | Percent of housing units built in 1939 or earlier. |
| `pct_built_pre_1940_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_built_pre_1940`. |
| `pct_single_family` | double | Percent of housing units in single-family structures. |
| `pct_single_family_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_single_family`. |
| `geometry` | binary | Boundary polygon, WKB, EPSG:4326 / OGC:CRS84. |
| `bbox` | struct<xmin, ymin, xmax, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, with row-group statistics. |

## Field notes

- **Every estimate here has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. The one exception in this collection is
  `population_moe`, which is **NULL on all 56 rows** (measured); it is carried
  as context, not as a usable margin, and
  `sqrt(sum(population_moe*population_moe))` over these rows returns NULL.
  `housing_units_moe` and `households_moe` are populated on all 52 rows with
  data.
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
- **To sum counts across geographies, add the margins in quadrature**
  (`sqrt(sum(moe*moe))`) — the Census Bureau's own rule for a derived sum. It
  applies to `housing_units` and `households`, never to a median. **Never sum
  or average a median**: a median of a region is not derivable from the medians
  of its parts.
- **A state's value is the Census Bureau's own estimate for the state.** Counts
  nest and add up — county `households` sums exactly to the state row for all
  52 states (measured, recipe 2) — but the state's published margin is its own,
  not the quadrature of its counties', and for all but one state the two
  differ. Rates and medians are not derivable from counties at all.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. At this geography the worst values are 0.010
  (`median_gross_rent_cv`), 0.009 (`median_home_value_cv`) and 0.027
  (`pct_rent_burdened_cv`), all measured — no filtering is needed here.
- **`median_gross_rent`'s universe is renter-occupied units *paying cash
  rent***, so units occupied rent-free are outside it, and gross rent is
  contract rent plus the estimated average monthly cost of utilities and fuels
  — not the rent on a lease.
- **`median_home_value` is the owner's estimate of what the property would sell
  for**, over owner-occupied units only. It is not an assessment, not a sale
  price, and not comparable to a transaction-based index.
- **The rent-burden columns divide by renter households *excluding* those whose
  rent-to-income ratio the Bureau could not compute** (B25070 line 1 minus line
  11, "Not computed" — no cash rent, or no income). Including them would
  understate the burden. `pct_severely_rent_burdened` (50%+) is a subset of
  `pct_rent_burdened` (30%+), not an addition to it.
- **`pct_vacant_units` counts for-sale, for-rent, seasonal and migrant-worker
  units as vacant**, so it is not a measure of abandonment. At state level the
  top of this column is a seasonal-housing ranking (recipe 4).
- **`pct_owner_occupied` is the homeownership rate of households, not of
  people**, and vacant units are outside its universe entirely.
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
| every other ACS column | NULL on exactly the same 4 rows. Nothing in this collection is suppressed: `median_gross_rent`, `median_home_value`, both rent-burden shares, `housing_units`, `households`, `pct_owner_occupied`, `pct_vacant_units`, `pct_built_pre_1940` and `pct_single_family` are each published on all 52 rows with data (measured). |
| `population_moe` | NULL on all 56 rows — see the field notes. |

The two medians are the clearest case for working here. Measured across the
catalog:

| column | NULL at block group | NULL at tract | NULL at county | NULL at state |
|---|---|---|---|---|
| `median_gross_rent` | 29.68% | 5.92% | 0.62% | 7.14% |
| `median_home_value` | 10.03% | 3.55% | 0.56% | 7.14% |

The 7.14% at state level is four island-area rows out of only 56, not
suppression: of the 52 rows that have ACS data, both medians are published on
every one. Coverage of *rows* is worst here; coverage of *data where there is
data* is perfect.

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern
Mariana Islands and the U.S. Virgin Islands have cartographic boundaries but no
ACS 5-year estimates, so their rows publish with NULL values rather than being
dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 17
ZCTAs, 279 places and 4 delegate districts.

Margins are small here but comparisons still need testing: check whether two
states' intervals overlap before calling a difference real, and never aggregate
a median.

The PMTiles archive is real state polygons at every zoom, band `0-8:geom`
(`tools/make_tiles.py`) — there is no coarser-geography band at coarse zooms,
because 56 features tile directly. `*_moe` columns are excluded from every tile
at every zoom; `*_cv` columns are kept. Statistics come from the GeoParquet,
always.

## Related collections

- [`states/state-income`](../state-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`states/state-people`](../state-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`states/state-connectivity`](../state-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`states/state-wellbeing`](../state-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`states/states`](../states/collection.json) ([agent guide](../states/AGENTS.md)) — the sixth sibling: all 112 columns in one table, same 56 rows, data files one directory up.
- [`counties/county-housing`](../../counties/county-housing/collection.json), [`tracts/tract-housing`](../../tracts/tract-housing/collection.json) and [`block-groups/bg-housing`](../../block-groups/bg-housing/collection.json) — the same theme at finer geographies, where the rent median starts to disappear.
- [`zctas/zcta-housing`](../../zctas/zcta-housing/collection.json), [`places/place-housing`](../../places/place-housing/collection.json), [`congressional-districts/cd-housing`](../../congressional-districts/cd-housing/collection.json) — the same theme at the other statistical geographies.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, including housing-unit and occupancy counts from a complete enumeration. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

Instead, the cost: 56 rows and 3.9 MB, of which 3.86 MB is geometry. No filter
is ever needed here for cost.

### 1. What housing costs, state by state

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*) AS states, count(median_gross_rent) AS rent_published,
       count(median_home_value) AS value_published,
       quantile_cont(median_gross_rent, 0.5)::int AS rent_p50,
       min(median_gross_rent)::int AS rent_min, max(median_gross_rent)::int AS rent_max,
       round(max(median_gross_rent_cv), 3) AS worst_rent_cv,
       round(max(median_home_value_cv), 3) AS worst_value_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet';
```

→ `56 | 52 | 52 | 1231 | 578 | 2036 | 0.01 | 0.009`.

Both medians published on all 52 rows with data, median state rent $1,231,
range $578 (Puerto Rico) to $2,036 (California), and the worst CV on either
column is 0.010. The ranking:

```sql
LOAD httpfs;
SELECT name, median_gross_rent::int AS rent, median_home_value::int AS home_value,
       round(median_home_value/median_gross_rent/12, 1) AS value_to_annual_rent,
       pct_owner_occupied, pct_rent_burdened
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet'
WHERE median_gross_rent IS NOT NULL
ORDER BY median_home_value DESC LIMIT 5;
```

→ `Hawaii | 1971 | 839100 | 35.5 | 63.0 | 56.67`,
`District of Columbia | 1954 | 737100 | 31.4 | 41.51 | 46.6`,
`California | 2036 | 734700 | 30.1 | 55.86 | 55.31`,
`Washington | 1760 | 564600 | 26.7 | 63.78 | 49.95`,
`Massachusetts | 1762 | 562100 | 26.6 | 62.52 | 51.76`.

`value_to_annual_rent` is a ratio of two medians from two different universes
(owner-occupied units vs renter-occupied units paying cash rent). It is a
useful screening index for how expensive buying is relative to renting, and it
is not a household-level statistic — no household appears in both numerator and
denominator.

### 2. Counties sum exactly to the state; their margins do not

```sql
LOAD httpfs;
SELECT (SELECT sum(households) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet' WHERE state='NY') AS county_sum,
       (SELECT round(sqrt(sum(households_moe*households_moe))) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet' WHERE state='NY') AS quadrature_moe,
       (SELECT households     FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet' WHERE state='NY') AS state_row,
       (SELECT households_moe FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet' WHERE state='NY') AS state_moe;
```

→ `7722646 | 8003 | 7722646 | 12717`.

Two things worth keeping. First, the counties **sum exactly** to the state row,
7,722,646 either way: counts are additive and the geographies nest, so this is
a usable consistency check on any rollup you write. Second, the quadrature
margin (±8,003) is *not* the state's published margin (±12,717) — the Bureau
estimates the state directly rather than by adding counties, so its margin is
its own. `sqrt(sum(moe*moe))` is the right way to put a margin on *your* sum;
it does not reproduce the Bureau's. It generalises:

```sql
LOAD httpfs;
WITH c AS (
  SELECT substr(geoid, 1, 2) AS st, sum(households) AS county_sum,
         round(sqrt(sum(households_moe*households_moe))) AS quad
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet'
  WHERE households IS NOT NULL GROUP BY 1)
SELECT count(*) AS states_checked,
       count(*) FILTER (WHERE c.county_sum = s.households) AS sums_match_exactly,
       count(*) FILTER (WHERE c.quad = s.households_moe)   AS margins_match,
       count(*) FILTER (WHERE c.quad < s.households_moe)   AS quadrature_narrower
FROM c JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet' s
  ON s.geoid = c.st
WHERE s.households IS NOT NULL;
```

→ `52 | 52 | 1 | 49`. All 52 sums match to the unit. One margin matches; 49 of
the quadrature margins are narrower than the published state margin and two are
wider. **Never do either of these with a median.** `sum()` and quadrature apply
to counts and to estimates of counts; a region's median rent is not derivable
from its counties' medians at all, with or without margins.

### 3. Every county against its own state's rent (GEOID prefix join)

```sql
LOAD httpfs;
SELECT c.name AS county, s.state,
       c.median_gross_rent::int AS county_rent, s.median_gross_rent::int AS state_rent,
       round(c.median_gross_rent / s.median_gross_rent, 2) AS vs_state
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet' c
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet' s
  ON s.geoid = substr(c.geoid, 1, 2)
WHERE c.median_gross_rent IS NOT NULL AND s.median_gross_rent IS NOT NULL
  AND c.households > 20000
ORDER BY vs_state DESC LIMIT 5;
```

→ `Williamson County, Tennessee | TN | 1969 | 1189 | 1.66`,
`Gallatin County, Montana | MT | 1694 | 1081 | 1.57`,
`Guaynabo Municipio, Puerto Rico | PR | 901 | 578 | 1.56`,
`DeSoto County, Mississippi | MS | 1451 | 954 | 1.52`,
`Loudoun County, Virginia | VA | 2386 | 1579 | 1.51`.

`s.geoid = substr(c.geoid, 1, 2)` is the whole join — a county GEOID begins
with its state's FIPS code. This is the shape the state files exist for: they
are the denominator every finer geography gets compared against, and the same
prefix reaches tracts and block groups. Note that a ratio of 1.56 in Puerto
Rico and 1.51 in Virginia describe very different absolute rents ($901 against
$2,386); carry both columns, never the ratio alone.

### 4. The vacancy rate is a seasonal-housing ranking

```sql
LOAD httpfs;
SELECT name, housing_units, pct_vacant_units, pct_single_family, pct_built_pre_1940
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet'
WHERE pct_vacant_units IS NOT NULL
ORDER BY pct_vacant_units DESC LIMIT 5;
```

→ `Puerto Rico | 1634357 | 21.02 | 80.08 | 1.8`,
`Maine | 751876 | 20.58 | 72.53 | 22.87`,
`Vermont | 339042 | 19.36 | 71.71 | 24.35`,
`Alaska | 328491 | 17.64 | 71.03 | 1.65`,
`West Virginia | 861325 | 15.4 | 73.59 | 14.86`.

Maine and Vermont are not one-fifth abandoned. The ACS counts for-sale,
for-rent, seasonal and migrant-worker units as vacant, so a state of holiday
cabins reads as high-vacancy, and so does a state of depopulating small towns —
this column cannot tell the two apart on its own. `pct_built_pre_1940` is the
column that distinguishes them here: 22.87% and 24.35% in Maine and Vermont
against 1.8% in Puerto Rico and 1.65% in Alaska.

### 5. Rent burden, and the 50% subset

```sql
LOAD httpfs;
SELECT name, pct_rent_burdened, pct_severely_rent_burdened,
       round(pct_severely_rent_burdened/pct_rent_burdened, 2) AS severe_share
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet'
WHERE pct_rent_burdened IS NOT NULL
ORDER BY pct_rent_burdened DESC LIMIT 5;
```

→ `Florida | 60.09 | 31.32 | 0.52`, `Hawaii | 56.67 | 28.59 | 0.5`,
`Nevada | 55.85 | 28.27 | 0.51`, `California | 55.31 | 28.75 | 0.52`,
`Louisiana | 54.77 | 30.04 | 0.55`.

`pct_severely_rent_burdened` is a **subset** of `pct_rent_burdened`, not an
addition to it — the 50%-or-more band is inside the 30%-or-more band — so
`severe_share` is a composition, not a sum, and the two columns must never be
added. Both divide by renter households *excluding* those whose ratio the
Bureau could not compute (B25070 line 1 minus line 11), which is why these
numbers run higher than a share of all renters would.

### Related recipes elsewhere

- The same columns where the rent median starts to disappear, and the
  value-to-income screen at tract scale:
  [`tracts/tract-housing/AGENTS.md`](../../tracts/tract-housing/AGENTS.md).
- Rent and value at county level, with every county against its state:
  [`counties/county-housing/AGENTS.md`](../../counties/county-housing/AGENTS.md).
- The income side of affordability, and why a state median describes nowhere in
  particular: [`states/state-income/AGENTS.md`](../state-income/AGENTS.md).
- All 112 state columns in one table, with a national households total and its
  quadrature margin timed against the published mirror:
  [`states/states/AGENTS.md`](../states/AGENTS.md).
- What this geography is for and when to step down from it:
  [`states/AGENTS.md`](../AGENTS.md).

Statistics come from the GeoParquet. The state PMTiles archive is real polygons
at every zoom — it needs no coarser-geography band — but carries no `*_moe`
columns, so none of the margin arithmetic above can be reproduced from tiles.
