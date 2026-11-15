# Agent guide — Health, Disability & Income by Race (States)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Health coverage, disability, nativity and income by race — the tables the Census Bureau does not publish for block groups, which is why this chunk has no block-group twin. The uninsured share and the share with a disability ([B27001](https://data.census.gov/table/ACSDT5Y2024.B27001), [B18101](https://data.census.gov/table/ACSDT5Y2024.B18101)), the foreign-born share ([B05002](https://data.census.gov/table/ACSDT5Y2024.B05002)), the group-quarters population ([B26001](https://data.census.gov/table/ACSDT5Y2024.B26001)), median household income for Black, non-Hispanic White, Asian and Hispanic householders ([B19013B](https://data.census.gov/table/ACSDT5Y2024.B19013B), [B19013H](https://data.census.gov/table/ACSDT5Y2024.B19013H), [B19013D](https://data.census.gov/table/ACSDT5Y2024.B19013D), [B19013I](https://data.census.gov/table/ACSDT5Y2024.B19013I)), and the poverty rate of the Black alone population ([B17020B](https://data.census.gov/table/ACSDT5Y2024.B17020B)).

**56 rows** — the 50 states, the District of Columbia, Puerto Rico and the four
island areas — ACS 2020–2024 5-year estimates, geometry from the 2024
cartographic boundary files. **52 of the 56 carry ACS data**; the four island
areas carry geometry and NULLs.

This is the one geography where this theme is complete. **All four
race-iteration medians are published for every one of the 52 rows that have ACS
data** — 100% coverage, against 60.77% and 46.55% of counties and 38.63% and
28.78% of tracts for the Black- and Asian-householder medians (all measured,
recipe 1). At tract level the NULLs *are* the subject of this collection; here
there are none, and a racial income comparison can be made for every state
without quoting a coverage denominator. What the 52 rows cannot do is locate
anything: a state gap is an average over every neighbourhood in the state, and
the inequality inside a single county is routinely larger than the gap between
two states.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.pmtiles`, layer `state-wellbeing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/collection.json` — carries a full description for every column

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
| [B05002](https://data.census.gov/table/ACSDT5Y2024.B05002) | Place of Birth by Nativity and Citizenship Status | Total population |
| [B17020B](https://data.census.gov/table/ACSDT5Y2024.B17020B) | Poverty Status in the Past 12 Months by Age (Black or African American Alone) | Black or African American alone population for whom poverty status is determined |
| [B18101](https://data.census.gov/table/ACSDT5Y2024.B18101) | Sex by Age by Disability Status | Civilian noninstitutionalized population |
| [B19013B](https://data.census.gov/table/ACSDT5Y2024.B19013B) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (Black or African American Alone Householder) | Households with a householder who is Black or African American alone |
| [B19013D](https://data.census.gov/table/ACSDT5Y2024.B19013D) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (Asian Alone Householder) | Households with a householder who is Asian alone |
| [B19013H](https://data.census.gov/table/ACSDT5Y2024.B19013H) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (White Alone, Not Hispanic or Latino Householder) | Households with a householder who is White alone, not Hispanic or Latino |
| [B19013I](https://data.census.gov/table/ACSDT5Y2024.B19013I) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (Hispanic or Latino Householder) | Households with a householder who is Hispanic or Latino |
| [B26001](https://data.census.gov/table/ACSDT5Y2024.B26001) | Group Quarters Population | Population in group quarters |
| [B27001](https://data.census.gov/table/ACSDT5Y2024.B27001) | Health Insurance Coverage Status by Sex by Age | Civilian noninstitutionalized population |

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
| `pct_uninsured` | double | Percent of the civilian noninstitutionalized population with no health insurance coverage. |
| `pct_uninsured_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_uninsured`. |
| `pct_uninsured_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_uninsured`. |
| `pct_with_disability` | double | Percent of the civilian noninstitutionalized population with a disability, as the ACS's six-question sequence defines it (hearing, vision, cognitive, ambulatory, self-care, independent living). |
| `pct_with_disability_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_with_disability`. |
| `pct_with_disability_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_with_disability`. |
| `pct_foreign_born` | double | Percent of the population that is foreign-born — anyone not a U.S. citizen at birth, naturalized citizens included. |
| `pct_foreign_born_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_foreign_born`. |
| `group_quarters_pop` | int64 | Population living in group quarters — correctional facilities, nursing facilities, college and university housing, military quarters, group homes, shelters. |
| `group_quarters_pop_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `group_quarters_pop`. |
| `median_hh_income_black` | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is Black or African American alone. |
| `median_hh_income_black_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_black`. |
| `median_hh_income_black_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_black`. |
| `median_hh_income_white_nh` | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is White alone, not Hispanic or Latino. |
| `median_hh_income_white_nh_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_white_nh`. |
| `median_hh_income_white_nh_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_white_nh`. |
| `median_hh_income_asian` | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is Asian alone. |
| `median_hh_income_asian_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_asian`. |
| `median_hh_income_asian_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_asian`. |
| `median_hh_income_hispanic` | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is Hispanic or Latino, of any race. |
| `median_hh_income_hispanic_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_hispanic`. |
| `median_hh_income_hispanic_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_hispanic`. |
| `pct_below_poverty_black` | double | Percent of the Black or African American alone population below the poverty level. |
| `pct_below_poverty_black_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_below_poverty_black`. |
| `pct_below_poverty_black_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_below_poverty_black`. |
| `geometry` | binary | Boundary polygon, WKB, EPSG:4326 / OGC:CRS84. |
| `bbox` | struct<xmin, ymin, xmax, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, with row-group statistics. |

## Field notes

- **Three `*_moe` columns in this collection are NULL on all 56 rows**
  (measured): `population_moe`, `pct_foreign_born_moe` and
  `group_quarters_pop_moe`. The first two divide by, or count, the total
  population, whose own margin is absent at this geography, and the build
  writes NULL rather than a guess when an input margin is NULL
  (`tools/column_docs.py`). Practical consequence: `pct_foreign_born` and
  `group_quarters_pop` cannot be significance-tested or quadrature-summed from
  this file. Every other margin here is populated on all 52 rows with data.
- **That NULL is upstream, and it is not suppression.** Each of those columns
  comes from a total-population table (B01003, B05002, B26001), and in the release's own
  `.dat` files those rows carry the estimate beside `-555555555`, the
  **controlled-MOE** jam value a controlled estimate gets in place of a
  sampling margin — `0400000US06|39287377|-555555555` in
  `staging/census-cache/acsdt5y2024-b01003.dat`, read 2026-11-15. The build
  turns it into NULL rather than publishing it as a number
  (`tools/build_acs.py`). The same columns carry margins normally at the finer
  geographies, where the estimates are not controlled this way:
  `population_moe` is carried on 33,759 of 33,791 ZCTAs and on all 241,854
  populated block groups (measured).
- **Every other estimate has a `<name>_moe`**, at the 90% confidence level —
  the level the Census Bureau publishes. To compare two states, check whether
  their margins overlap before calling a difference real. **Never sum or
  average a median**: a median of a region is not derivable from the medians of
  its parts, and that applies to the four race-iteration medians above all.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. At this geography the worst values are 0.213
  (`pct_below_poverty_black_cv`), 0.198 (`median_hh_income_asian_cv`) and 0.185
  (`median_hh_income_black_cv`), all measured — nothing is above 0.40, so no
  filtering is needed, which is not true of this theme anywhere finer.
- **The race-iteration medians are classified by the householder's race**, not
  by every member's, and each has its own universe (households with a
  householder who is …). They are not shares of a common total, they cannot be
  averaged together, and the overall median in
  [`state-income`](../state-income/collection.json) is **not** a weighted
  average of them — in Hawaii the overall median sits *above* the non-Hispanic
  White median (measured, recipe 3).
- **`pct_below_poverty_black` has a race-specific denominator** (the Black
  alone population for whom poverty status is determined), so it is not
  comparable to `pct_below_poverty`'s denominator even though both are poverty
  rates. Recipe 5 contrasts them and says what the contrast does and does not
  mean.
- **`pct_uninsured` and `pct_with_disability` are shares of the civilian
  noninstitutionalized population**, not of everyone: people on active duty and
  people in institutions are outside the universe. They move independently —
  the correlation across the 52 rows is 0.121 (measured).
- **`pct_foreign_born` counts anyone not a U.S. citizen at birth**, naturalized
  citizens included. It is not a count of non-citizens.
- **`group_quarters_pop` is a count, not a share**, covering correctional and
  nursing facilities, college and university housing, military quarters, group
  homes and shelters. It has no margin at this geography.
- **A state's value is the Census Bureau's own estimate for the state**, not a
  sum or average of its counties. Counts nest and add up — county `households`
  sums exactly to the state row for all 52 states, measured in
  [`state-housing`](../state-housing/AGENTS.md) — but medians and rates do not.
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
| `median_hh_income_black`, `median_hh_income_white_nh`, `median_hh_income_asian`, `median_hh_income_hispanic` | NULL on exactly the same 4 rows and no others — **all four are published on all 52 rows with ACS data** (measured). This is true at no other geography in the catalog. |
| `pct_below_poverty_black` | NULL on the same 4 rows only; published on all 52. |
| `pct_uninsured`, `pct_with_disability`, `pct_foreign_born`, `group_quarters_pop` | NULL on the same 4 rows only. |
| `population_moe`, `pct_foreign_born_moe`, `group_quarters_pop_moe` | NULL on all 56 rows — see the field notes. |

How unusual that is, measured as a share of the rows that have ACS data:

| column | published at state | at county | at tract |
|---|---|---|---|
| `median_hh_income_black` | 100.0% | 60.77% | 38.63% |
| `median_hh_income_asian` | 100.0% | 46.55% | 28.78% |

At tract level a map of `median_hh_income_asian` is drawn on about a quarter of
tracts and its coverage is largely a map of where Asian-householder households
live. At state level that problem does not exist. The problem that replaces it
is resolution: 52 rows, and a single state gap averaging over everything inside
it.

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

- [`states/state-income`](../state-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1; the overall `median_hh_income` and `pct_below_poverty` live there.
- [`states/state-people`](../state-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1; the race *shares* live there, and have no margins at this geography.
- [`states/state-housing`](../state-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`states/state-connectivity`](../state-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`states/states`](../states/collection.json) ([agent guide](../states/AGENTS.md)) — the sixth sibling: all 112 columns in one table, same 56 rows, data files one directory up.
- [`counties/county-wellbeing`](../../counties/county-wellbeing/collection.json) and [`tracts/tract-wellbeing`](../../tracts/tract-wellbeing/collection.json) — the same theme at finer geographies, where the race-iteration medians are published on a minority of rows.
- No twin at block-groups for this theme: the Census Bureau does not publish these tables at that geography, so tract is as fine as this theme goes.
- [`zctas/zcta-wellbeing`](../../zctas/zcta-wellbeing/collection.json), [`places/place-wellbeing`](../../places/place-wellbeing/collection.json), [`congressional-districts/cd-wellbeing`](../../congressional-districts/cd-wellbeing/collection.json) — the same theme at the other statistical geographies.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no income or health variables.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

Instead, the cost: 56 rows and 3.9 MB, of which 3.86 MB is geometry. No filter
is ever needed here for cost.

### 1. Nothing is missing here — measure it before you rely on it

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*) AS rows, count(population) AS with_acs_data,
       count(median_hh_income_white_nh) AS white_nh, count(median_hh_income_black) AS black,
       count(median_hh_income_hispanic) AS hispanic, count(median_hh_income_asian) AS asian,
       count(pct_below_poverty_black) AS poverty_black
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet';
```

→ `56 | 52 | 52 | 52 | 52 | 52 | 52`.

Every one of the five race-specific columns is published on every row that has
ACS data. Compare the geographies below it:

```sql
LOAD httpfs;
SELECT 'state' AS geography, count(*) AS rows,
       round(100.0*count(median_hh_income_black)/count(population), 2) AS pct_black_published,
       round(100.0*count(median_hh_income_asian)/count(population), 2) AS pct_asian_published
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet'
UNION ALL
SELECT 'county', count(*), round(100.0*count(median_hh_income_black)/count(population), 2),
       round(100.0*count(median_hh_income_asian)/count(population), 2)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet'
UNION ALL
SELECT 'tract', count(*), round(100.0*count(median_hh_income_black)/count(population), 2),
       round(100.0*count(median_hh_income_asian)/count(population), 2)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet';
```

→

```
state  |    56 | 100.00 | 100.00
county |  3235 |  60.77 |  46.55
tract  | 85184 |  38.63 |  28.78
```

(The denominator is `count(population)`, the rows that have ACS data, not
`count(*)`.) This is the reason to answer a racial-income question here when a
single number is wanted: at tract level the same question is answered on a
quarter to a third of rows, and the blanks are where the group does not live,
not where its income is low. The reason *not* to answer it here is in recipes 2
and 3 — 52 rows locate nothing.

### 2. The Black-to-White income ratio, state by state

```sql
LOAD httpfs;
SELECT name, median_hh_income_white_nh::int AS white_nh, median_hh_income_black::int AS black,
       round(median_hh_income_black::double/median_hh_income_white_nh, 2) AS black_to_white,
       round(median_hh_income_black_cv, 3) AS black_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet'
WHERE median_hh_income_black IS NOT NULL
ORDER BY black_to_white LIMIT 5;
```

→ `District of Columbia | 170201 | 60764 | 0.36 | 0.031`,
`Louisiana | 74021 | 39169 | 0.53 | 0.012`,
`Wisconsin | 81064 | 43296 | 0.53 | 0.015`,
`Mississippi | 70133 | 39434 | 0.56 | 0.013`,
`Illinois | 91123 | 50704 | 0.56 | 0.01`.

```sql
LOAD httpfs;
SELECT round(min(median_hh_income_black::double/median_hh_income_white_nh), 2) AS min_ratio,
       round(max(median_hh_income_black::double/median_hh_income_white_nh), 2) AS max_ratio,
       count(*) FILTER (WHERE median_hh_income_black > median_hh_income_white_nh) AS black_above_white
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet'
WHERE median_hh_income_black IS NOT NULL;
```

→ `0.36 | 0.89 | 0`. The ratio runs from 0.36 to 0.89 and there is **no** row
among the 52 where the Black-householder median exceeds the non-Hispanic
White-householder median. The `_cv` column is quoted here out of habit rather
than necessity — the worst `median_hh_income_black_cv` in the file is 0.185
(measured) — but keep the habit: the identical query at tract level needs the
gate, and needs the coverage denominator too.

### 3. The overall median is not a weighted average of the race medians (sibling join)

```sql
LOAD httpfs;
SELECT w.name, i.median_hh_income::int AS overall,
       w.median_hh_income_white_nh::int AS white_nh,
       w.median_hh_income_black::int    AS black,
       w.median_hh_income_asian::int    AS asian,
       w.median_hh_income_hispanic::int AS hispanic
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet' w
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet' i
  USING (geoid)
WHERE w.state IN ('CA','NY','TX','HI')
ORDER BY overall DESC;
```

→ `Hawaii | 100389 | 98872 | 81548 | 107564 | 88708`,
`California | 99122 | 111251 | 69282 | 129046 | 81624`,
`New York | 85974 | 97182 | 62083 | 97126 | 65593`,
`Texas | 78476 | 93968 | 60084 | 117028 | 65194`.

The join is 1:1 on `geoid` — all six collections in this group hold the same 56
rows. Hawaii is the row to stare at: its overall median ($100,389) is *above*
its non-Hispanic White median ($98,872). That is not an error. The five medians
have five different universes — all households, and households with a
householder of each group — and a median is not a weighted average of
sub-medians. In California the Asian-householder median exceeds the overall by
$29,924 and the Black-householder median falls short of it by $29,840; neither
difference is derivable from the other.

### 4. Insurance and disability move independently

```sql
LOAD httpfs;
SELECT name, pct_uninsured, round(pct_uninsured_cv, 3) AS unins_cv,
       pct_with_disability, pct_foreign_born, group_quarters_pop
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet'
WHERE pct_uninsured IS NOT NULL
ORDER BY pct_uninsured DESC LIMIT 5;
```

→ `Texas | 17.13 | 0.003 | 12.3 | 17.56 | 616727`,
`Oklahoma | 12.87 | 0.006 | 17.22 | 6.36 | 117326`,
`Georgia | 12.37 | 0.005 | 13.12 | 11.18 | 249767`,
`Florida | 11.54 | 0.004 | 13.66 | 21.88 | 476767`,
`Nevada | 11.42 | 0.009 | 13.94 | 19.13 | 36352`.

```sql
LOAD httpfs;
SELECT round(corr(pct_uninsured, pct_with_disability), 3) AS r, count(*) AS n
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet'
WHERE pct_uninsured IS NOT NULL;
```

→ `0.121 | 52`. Texas leads on uninsured (17.13%) with a disability share of
12.3%, below the 52-row mean of 14.05 (measured); Oklahoma is second on
uninsured and first of these
five on disability (17.22%). Across all 52 rows the correlation is 0.121 —
effectively none. Reading one column as a proxy for the other is wrong in both
directions. Both are shares of the **civilian noninstitutionalized**
population, so active-duty personnel and people in institutions are outside
both denominators, which also means `group_quarters_pop` in the same row is
partly a count of people the two shares exclude.

### 5. Two poverty rates, two denominators

```sql
LOAD httpfs;
SELECT w.name, i.pct_below_poverty AS overall, w.pct_below_poverty_black AS black,
       round(w.pct_below_poverty_black - i.pct_below_poverty, 2) AS gap,
       round(w.pct_below_poverty_black_cv, 3) AS black_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet' w
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet' i
  USING (geoid)
WHERE w.pct_below_poverty_black IS NOT NULL
ORDER BY gap DESC LIMIT 5;
```

→ `Wyoming | 10.53 | 34.41 | 23.88 | 0.15`,
`Iowa | 11.08 | 29.57 | 18.49 | 0.047`,
`Wisconsin | 10.55 | 27.31 | 16.76 | 0.025`,
`Nebraska | 10.6 | 26.63 | 16.03 | 0.06`,
`Maine | 10.75 | 26.13 | 15.38 | 0.093`.

```sql
LOAD httpfs;
SELECT count(*) AS rows,
       count(*) FILTER (WHERE w.pct_below_poverty_black > i.pct_below_poverty) AS black_rate_higher
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet' w
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet' i
  USING (geoid)
WHERE w.pct_below_poverty_black IS NOT NULL;
```

→ `52 | 51`. The Black-alone poverty rate is higher than the overall rate in 51
of the 52 rows; the exception is Puerto Rico (39.42% against an overall 40.53%,
measured). Two cautions. The denominators are different — `pct_below_poverty`
divides by the population for whom poverty status is determined,
`pct_below_poverty_black` by the Black-alone part of that population — so
`gap` is a difference of two rates, not a decomposition of one. And Wyoming's
`black_cv` of 0.15 is the highest of the five: its Black-alone population is
small, the estimate is in the "use with caution" band even at state level, and
it tops the ranking partly because of that. Sorting by a gap sorts small
populations to the top.

### Related recipes elsewhere

- The same columns where the NULLs are the subject, with the Fulton County
  coverage denominator:
  [`tracts/tract-wellbeing/AGENTS.md`](../../tracts/tract-wellbeing/AGENTS.md).
- The same race-iteration medians at county level, published on 60.77% of
  counties:
  [`counties/county-wellbeing/AGENTS.md`](../../counties/county-wellbeing/AGENTS.md).
- The overall income median and the state-median trap:
  [`states/state-income/AGENTS.md`](../state-income/AGENTS.md).
- The race *shares*, which at this geography carry no margins at all:
  [`states/state-people/AGENTS.md`](../state-people/AGENTS.md).
- All 112 state columns in one table, with recipes timed against the published
  mirror: [`states/states/AGENTS.md`](../states/AGENTS.md).
- What this geography is for and when to step down from it:
  [`states/AGENTS.md`](../AGENTS.md).

Statistics come from the GeoParquet. The state PMTiles archive is real polygons
at every zoom — it needs no coarser-geography band — but carries no `*_moe`
columns, so none of the margin arithmetic above can be reproduced from tiles.
