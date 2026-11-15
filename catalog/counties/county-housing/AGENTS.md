# Agent guide — Housing & Rent (Counties)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

The housing stock and what it costs: total units and the vacancy rate ([B25002](https://data.census.gov/table/ACSDT5Y2024.B25002)), households and the owner-occupied share ([B25003](https://data.census.gov/table/ACSDT5Y2024.B25003)), median gross rent ([B25064](https://data.census.gov/table/ACSDT5Y2024.B25064)) and median owner-occupied home value ([B25077](https://data.census.gov/table/ACSDT5Y2024.B25077)), the share of renter households paying 30% and 50% or more of income on rent ([B25070](https://data.census.gov/table/ACSDT5Y2024.B25070)), the pre-1940 share ([B25034](https://data.census.gov/table/ACSDT5Y2024.B25034)) and the single-family share ([B25024](https://data.census.gov/table/ACSDT5Y2024.B25024)).

**3,235 rows**, one per county or county equivalent, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

This is the geography where the rent and value medians stop disappearing. `median_gross_rent` is NULL on **0.62%** of counties and `median_home_value` on **0.56%** — against 5.92% and 3.55% at tract level and 29.68% and 10.03% at block group (measured, below). A national rent map drawn here has essentially no holes.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.pmtiles`, layer `county-housing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/collection.json` — carries a full description for every column

This is one themed cut of the county table. The same rows with all 112 columns — every theme at once, no join — are the sixth sibling in this group, [`counties/counties`](../counties/collection.json), whose data files sit one directory up at `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet` (and `.pmtiles`).

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

`geoid` is 5 characters and is the join key: `substr(geoid, 1, 2)` → state FIPS; tracts and block groups join back on their own first 5 characters.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 5-character county GEOID: state 2 + county 3. |
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

- **`population_moe` is NULL on 3,103 of the 3,235 rows** (measured — only 132
  small rural counties carry one). Read `population` at this geography as a
  count to use rather than an estimate to put an interval on. Every
  *housing* margin in this chunk is populated on every row where the estimate
  is — `housing_units_moe`, `households_moe`, `pct_vacant_units_moe`,
  `pct_owner_occupied_moe`, `median_gross_rent_moe`, `pct_rent_burdened_moe`,
  `pct_severely_rent_burdened_moe`, `median_home_value_moe`,
  `pct_built_pre_1940_moe` and `pct_single_family_moe` all match their
  estimate's non-NULL count exactly (measured).
- **Every estimate has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. To compare two geographies, check
  whether their margins overlap before calling a difference real. To sum
  estimates across geographies, add the margins in quadrature
  (`sqrt(sum(moe*moe))`). **Never sum or average a median**: a median of a
  region is not derivable from the medians of its parts.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. At this geography the medians are tight: the median
  `median_gross_rent_cv` is **0.039** and `median_home_value_cv` **0.035**
  (measured) — but `pct_rent_burdened_cv` runs at 0.103, so the burden shares
  are the looser half of this chunk.
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **`median_gross_rent` is gross rent** — contract rent plus the estimated
  average monthly cost of utilities and fuels — and its universe is
  renter-occupied units **paying cash rent** (B25064), so units occupied rent
  free are outside it.
- **`median_home_value` is the owner's own estimate** of what the property
  would sell for (B25077), not an assessment, not a sale price, and not a
  market index. Its universe is owner-occupied units only.
- **The rent-burden columns divide by renter households *excluding* those whose
  rent-to-income ratio the Bureau could not compute** (B25070 line 1 minus line
  11, "Not computed"). Including them would understate the burden.
  `pct_severely_rent_burdened` (50%+) is a subset of `pct_rent_burdened`
  (30%+), not a separate category — do not add them.
- **`housing_units` includes vacant units; `households` does not.**
  `households` is occupied housing units (B25003), and it is the right
  denominator for every household-based rate in the catalog — including the
  internet and vehicle shares over in
  [`county-connectivity`](../county-connectivity/collection.json), which have
  no household count of their own.
- **`pct_owner_occupied` divides by occupied units** (B25003), so it and the
  renter share sum to 100 of *occupied* units, not of `housing_units`.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area, and neither number is wrong.
- **Connecticut's county equivalents are the 9 planning regions**
  (`09110`–`09190`, measured) in the 2024 vintage, not the 8 historical
  counties. A 2020-vintage block or tract GEOID's 5-character prefix does not
  match these rows.

## Data quality

Columns with notable missingness at this geography, measured over this file:

| column | missingness |
|---|---|
| `population` | NULL on 0.40% of counties (13 rows) — the island-area county equivalents (AS 5, GU 1, MP 4, VI 3, measured), which have cartographic boundaries but no ACS 5-year estimates. |
| `population_moe` | NULL on 95.92% of counties (3,103 of 3,235). |
| `housing_units`, `households`, `pct_vacant_units`, `pct_owner_occupied`, `pct_rent_burdened`, `pct_severely_rent_burdened`, `pct_built_pre_1940`, `pct_single_family` | NULL on 0.40% (13 rows) — the island areas only. |
| `median_gross_rent` | NULL on 0.62% of counties (20 rows): the 13 island areas plus 7 counties with ACS data and too few cash-rent households for a median. Against 5.92% of tracts and 29.68% of block groups. |
| `median_home_value` | NULL on 0.56% of counties (18 rows). Against 3.55% of tracts and 10.03% of block groups. |
| `pct_rent_burdened_cv` | NULL on 0.71% (23 rows) — 10 more than the estimate. Measured: in all 10 the estimate is exactly 0, and a CV divides by the estimate. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

The seven counties with ACS data and no rent median are tiny and nameable, which is the point: at this geography the suppression list is short enough to print (recipe 1 prints it). At block-group level the same list is 71,923 rows long (measured).

Margins of error at this geography are the narrowest in the catalog below state level, but they are not zero. Use the `*_cv` columns to flag or grey out unreliable values; never compare two counties without checking whether their margins overlap, and never aggregate a median.

The PMTiles archive carries real county polygons at every zoom — the band is `0-10:geom`, there are few enough features to draw them all at a national zoom, so there is no coarser-geography band at coarse zooms the way the tract and block-group collections have one. `*_moe` columns are excluded from the tiles at every zoom; `*_cv` columns are kept. Statistics come from the GeoParquet, always.

## Related collections

- [`counties/county-income`](../county-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1. The denominator for any affordability ratio.
- [`counties/county-people`](../county-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`counties/county-connectivity`](../county-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1. Its household-denominated shares have no household count; this chunk's `households` is it.
- [`counties/county-wellbeing`](../county-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`counties/counties`](../counties/collection.json) — the sixth sibling: all 112 columns in one wide table, same 3,235 rows, data files one directory up. Use it instead of a join when a question crosses three or more themes.
- The same theme at the other geographies: [`states/state-housing`](../../states/state-housing/collection.json), [`tracts/tract-housing`](../../tracts/tract-housing/collection.json), [`block-groups/bg-housing`](../../block-groups/bg-housing/collection.json), [`zctas/zcta-housing`](../../zctas/zcta-housing/collection.json), [`places/place-housing`](../../places/place-housing/collection.json), [`congressional-districts/cd-housing`](../../congressional-districts/cd-housing/collection.json).
- [`blocks`](../../blocks/collection.json) — 2020 Decennial housing-unit and occupancy counts at block level. Different survey, different vintage, no margins of error, and no rent or value at all.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

For cost: this file is 12.4 MB over 3,235 rows, most of it geometry. Nothing
here needs a filter to be affordable.

### 1. How complete are the medians, and which counties lack one?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*) AS counties,
       count(median_gross_rent)                                     AS rent_published,
       round(100.0*(count(*)-count(median_gross_rent))/count(*), 2) AS pct_rent_null,
       count(median_home_value)                                     AS value_published,
       round(100.0*(count(*)-count(median_home_value))/count(*), 2) AS pct_value_null,
       quantile_cont(median_gross_rent, 0.5)::int                   AS rent_p50,
       quantile_cont(median_home_value, 0.5)::int                   AS value_p50
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet';
```

→ `3235 | 3215 | 0.62 | 3217 | 0.56 | 870 | 182300`.

The median county's median gross rent is $870/month and its median home value
$182,300. Now the holes, which are short enough to name:

```sql
LOAD httpfs;
SELECT geoid, name, population, households
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet'
WHERE median_gross_rent IS NULL AND population IS NOT NULL
ORDER BY population DESC;
```

→ `06091 | Sierra County, California | 2746 | 1219`, `06003 | Alpine County,
California | 1616 | 435`, `48443 | Terrell County, Texas | 835 | 451`, `48033 |
Borden County, Texas | 713 | 243`, `48269 | King County, Texas | 211 | 111`,
`48261 | Kenedy County, Texas | 145 | 55`, `48301 | Loving County, Texas | 33 |
27`.

Seven rows, the largest with 1,219 households. Every other county with ACS data
has a rent median; the remaining 13 NULLs are the island areas, which have no
ACS tabulation at all. This is the whole suppression story at this geography —
print it rather than describing it.

### 2. Most expensive rents in one state, reliability-gated

```sql
LOAD httpfs;
SELECT geoid, name, median_gross_rent::int AS rent, round(median_gross_rent_cv, 3) AS cv,
       pct_rent_burdened
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet'
WHERE state = 'CO' AND median_gross_rent_cv < 0.10
ORDER BY median_gross_rent DESC LIMIT 5;
```

→ `08035 | Douglas County, Colorado | 2193 | 0.009 | 51.28`, `08093 | Park
County, Colorado | 2161 | 0.04 | 35.08`, `08014 | Broomfield County, Colorado |
2126 | 0.011 | 44.17`, `08037 | Eagle County, Colorado | 2019 | 0.041 | 64.66`,
`08013 | Boulder County, Colorado | 1966 | 0.009 | 59.89`.

Carrying `pct_rent_burdened` beside the rent is the useful move: Park County's
$2,161 rent comes with a 35% burden rate and Eagle County's lower $2,019 with
65%, because burden is rent *relative to local income*. High rent and
unaffordable rent are different columns and sometimes different counties.

### 3. Rent as a share of income (1:1 sibling join)

```sql
LOAD httpfs;
SELECT h.geoid, h.name, h.median_gross_rent::int AS rent, i.median_hh_income::int AS income,
       round(100.0*12*h.median_gross_rent/i.median_hh_income, 1) AS rent_pct_of_income,
       h.pct_rent_burdened AS burdened
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet' h
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet' i
  USING (geoid)
WHERE h.population > 100000
  AND h.median_gross_rent_cv < 0.10 AND i.median_hh_income_cv < 0.10
ORDER BY rent_pct_of_income DESC LIMIT 5;
```

→ `36005 | Bronx County, New York | 1458 | 48676 | 35.9 | 60.1`, `72113 | Ponce
Municipio, Puerto Rico | 536 | 19877 | 32.4 | 55.33`, `12086 | Miami-Dade
County, Florida | 1829 | 71753 | 30.6 | 64.43`, `12011 | Broward County,
Florida | 1907 | 77633 | 29.5 | 65.16`, `12097 | Osceola County, Florida | 1746
| 72637 | 28.8 | 65.36`.

The join is 1:1 on `geoid` — all six county collections hold the same 3,235
rows. `rent_pct_of_income` here is a ratio of two medians from two different
universes (cash-rent renter units vs all households), so it is a screening
index and not a household-level burden rate; `pct_rent_burdened` is the
household-level one, and the two disagree in rank order, which is the point of
showing them together. Ponce's 32.4% index pairs with a 55% burden rate while
Osceola's 28.8% pairs with 65%, because the median renter and the median
household are different populations.

### 4. Summing across counties: margins add in quadrature

```sql
LOAD httpfs;
SELECT (SELECT sum(households) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet' WHERE state='CO') AS county_sum,
       (SELECT round(sqrt(sum(households_moe*households_moe))) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet' WHERE state='CO') AS quadrature_moe,
       (SELECT households     FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet' WHERE state='CO') AS state_row,
       (SELECT households_moe FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet' WHERE state='CO') AS state_moe;
```

→ `2374218 | 3574.0 | 2374218 | 4232.0`.

Two things worth keeping. First, the counties **sum exactly** to the state row,
2,374,218 either way: counts are additive and counties nest in states, so this
is a usable consistency check on any rollup you write. Second, the quadrature
margin (±3,574) is *not* the state's published margin (±4,232) — the Bureau
estimates the state directly rather than by adding counties, so its margin is
its own. `sqrt(sum(moe*moe))` is the right way to put a margin on *your* sum;
it does not reproduce the Bureau's.

**Never do this with `median_gross_rent` or `median_home_value`.** `sum()` and
quadrature apply to counts and to estimates of counts. A region's median rent
is not derivable from its counties' median rents at all, with or without
margins.

### 5. Which geography should a rent question be asked at? (three files)

```sql
LOAD httpfs;
SELECT 'county' AS geography,
       round(100.0*(count(*)-count(median_gross_rent))/count(*), 2) AS pct_rent_null,
       round(100.0*(count(*)-count(median_home_value))/count(*), 2) AS pct_value_null,
       round(quantile_cont(median_gross_rent_cv, 0.5), 3)           AS rent_median_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet'
UNION ALL SELECT 'tract',
       round(100.0*(count(*)-count(median_gross_rent))/count(*), 2),
       round(100.0*(count(*)-count(median_home_value))/count(*), 2),
       round(quantile_cont(median_gross_rent_cv, 0.5), 3)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet'
UNION ALL SELECT 'block group',
       round(100.0*(count(*)-count(median_gross_rent))/count(*), 2),
       round(100.0*(count(*)-count(median_home_value))/count(*), 2),
       round(quantile_cont(median_gross_rent_cv, 0.5), 3)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet';
```

→ `county | 0.62 | 0.56 | 0.039`, `tract | 5.92 | 3.55 | 0.083`, `block group |
29.68 | 10.03 | 0.107`.

Rent is the column that punishes going fine: nearly three block groups in ten
have no rent median at all, against six counties in a thousand. If the answer
is a ranking, a rate for a named county, or anything that will be quoted as a
number, ask it here. Step down only when the question is genuinely
intra-county, and when you do, grey out by `_cv` and say what share of rows is
blank.

### Related recipes elsewhere

- The whole county table at once, including the same quadrature check on the
  wide file: [`counties/counties/AGENTS.md`](../counties/AGENTS.md).
- Rent and value inside a county, where the medians start disappearing:
  [`tracts/tract-housing/AGENTS.md`](../../tracts/tract-housing/AGENTS.md) and
  [`block-groups/bg-housing/AGENTS.md`](../../block-groups/bg-housing/AGENTS.md).
- The income side of any affordability question:
  [`counties/county-income/AGENTS.md`](../county-income/AGENTS.md).
- Choosing between the six county collections, and stepping up or down a
  geography: [`counties/AGENTS.md`](../AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, so no test above that reads a margin of error can be reproduced from
tiles — even though, unlike the finer collections, every zoom of this archive
holds real county polygons.
