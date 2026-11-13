# Agent guide — Housing & Rent (Block Groups)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

The housing stock and what it costs: total units and the vacancy rate ([B25002](https://data.census.gov/table/ACSDT5Y2024.B25002)), households and the owner-occupied share ([B25003](https://data.census.gov/table/ACSDT5Y2024.B25003)), median gross rent ([B25064](https://data.census.gov/table/ACSDT5Y2024.B25064)) and median owner-occupied home value ([B25077](https://data.census.gov/table/ACSDT5Y2024.B25077)), the share of renter households paying 30% and 50% or more of income on rent ([B25070](https://data.census.gov/table/ACSDT5Y2024.B25070)), the pre-1940 share ([B25034](https://data.census.gov/table/ACSDT5Y2024.B25034)) and the single-family share ([B25024](https://data.census.gov/table/ACSDT5Y2024.B25024)).

**242,298 rows**, one per block group, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.pmtiles`, layer `bg-housing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/collection.json` — carries a full description for every column

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

`geoid` is 12 characters and is the join key: `substr(geoid, 1, 11)` → tract, `substr(geoid, 1, 5)` → county, `substr(geoid, 1, 2)` → state FIPS.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 12-character block-group GEOID: state 2 + county 3 + tract 6 + block group 1. |
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

- **Every estimate has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. To compare two geographies, check
  whether their margins overlap before calling a difference real. To sum
  estimates across geographies, add the margins in quadrature
  (`sqrt(sum(moe*moe))`). **Never sum or average a median**: a median of a
  region is not derivable from the medians of its parts.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. Filtering or greying out by CV is the intended use.
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area, and neither number is wrong.
- **The rent-burden columns divide by renter households *excluding* those whose rent-to-income ratio the Bureau could not compute** (B25070 line 1 minus line 11, "Not computed"). Including them would understate the burden.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.18% of block groups — the island areas (405 block groups with 2024 boundaries but no ACS data) and the 39 Suffolk County, NY block groups re-delineated in this vintage. |
| `median_gross_rent` | **NULL on 29.68% of block groups** — nearly a third. A block group with few renter households paying cash rent has no publishable rent median; the tract rate is 5.92%. Map this at block-group scale only if the holes are acceptable, or move up to tracts. |
| `pct_rent_burdened` | NULL on 7.91% of block groups, where the denominator (renter households whose ratio could be computed) came out at or below 0. |
| `median_home_value` | **NULL on 10.03% of block groups** — a block group with few owner-occupied units has no publishable value median. The tract rate is 3.55%. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

Suffolk County, New York (36103) was re-delineated in the 2024 vintage: 39 block groups and 14 tracts exist in the 2024 cartographic boundary files with no matching row in the 2020-based ACS tabulation, and publish with NULL ACS values. These are the only non-territory rows in the catalog with geometry but no data.

443 ACS block groups and 338 ACS tracts (the `9900xx`-style water geographies) have no polygon in the cartographic boundary files and therefore no row here. All of them have population 0, so the dropped population is exactly 0 — this is why the tract collections hold 85,184 rows against 85,382 in the ACS release.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are A5 cell aggregations, not census geographies — counts summed, rates and medians averaged unweighted. Statistics come from the GeoParquet.

## Related collections

- [`block-groups/bg-income`](../bg-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`block-groups/bg-people`](../bg-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`block-groups/bg-connectivity`](../bg-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-housing`](../../tracts/tract-housing/collection.json) — the same theme one geography up, with narrower margins of error.
- [`counties`](../../counties/collection.json) and [`states`](../../states/collection.json) — every indicator in one wide table per geography.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run against the published URLs with DuckDB 1.4.1
immediately before it was written down, and its real output is quoted beside
it.

### 1. What does a block group's rent look like, and how often is it missing?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*)                                                     AS block_groups,
       count(median_gross_rent)                                     AS published,
       round(100.0*(count(*)-count(median_gross_rent))/count(*), 2) AS pct_no_rent_median,
       quantile_cont(median_gross_rent, 0.5)::int                   AS p50_rent
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet';
```

→ `242298 | 170375 | 29.68 | 1327`, in **2.0 s**. Nearly a third of block
groups have no publishable rent median, which re-measures the rate in the
data-quality table above. Any choropleth of this column at this geography is
30% holes.

One state, same query plus `WHERE state = 'WV'`:

```sql
LOAD httpfs;
SELECT count(*) AS block_groups, count(median_gross_rent) AS published,
       quantile_cont(median_gross_rent, 0.5)::int AS p50_rent
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet'
WHERE state = 'WV';
```

→ `1639 | 959 | 862`, 2.5 s. West Virginia is worse than the national average:
41% of its block groups have no rent median.

### 2. When to step up a geography (the same column at tract level)

```sql
LOAD httpfs;
SELECT 'block group' AS geography,
       round(100.0*(count(*)-count(median_gross_rent))/count(*), 2) AS pct_null
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet'
UNION ALL
SELECT 'tract',
       round(100.0*(count(*)-count(median_gross_rent))/count(*), 2)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet';
```

→ `block group | 29.68`, `tract | 5.92`. 4.7 s for both files.

That is a five-fold reduction in missingness for one step up in geography, and
the same comparison holds for `median_home_value` (10.03% against 3.55%). If
the question is about rent rather than about block groups, ask it of
[`tracts/tract-housing`](../../tracts/tract-housing/collection.json) and keep
the coverage.

### 3. The most rent-burdened block groups, reliability-filtered (`*_cv`)

```sql
LOAD httpfs;
SELECT geoid, state, households, pct_rent_burdened,
       pct_rent_burdened_moe AS moe, round(pct_rent_burdened_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet'
WHERE households > 500 AND pct_rent_burdened_cv < 0.10
ORDER BY pct_rent_burdened DESC LIMIT 5;
```

→ `061110052042 | CA | 545 | 100.0 | 16.14 | 0.1`, `061110010024 | CA | 556 |
100.0 | 14.14 | 0.09`, `060290017003 | CA | 515 | 100.0 | 1.37 | 0.01`,
`060450106022 | CA | 752 | 100.0 | 11.76 | 0.07`, `410390031031 | OR | 574 |
100.0 | 5.74 | 0.04`. 5.6 s.

`pct_rent_burdened = 100.0` is real and reachable: the denominator is renter
households whose rent-to-income ratio the Bureau could compute, which in a
small block group can be a few dozen households all paying 30% or more. The
`households > 500` gate is about the *block group*, not that denominator — the
third row's ±1.37 margin is what tells you its 100.0 is solid. Without the
`_cv` filter this query returns block groups whose margin is wider than the
estimate.

### 4. Rent burden against income (1:1 join to a sibling chunk)

```sql
LOAD httpfs;
SELECT round(corr(h.pct_rent_burdened, i.median_hh_income), 3) AS r_burden_vs_income,
       round(corr(h.median_gross_rent, i.median_hh_income), 3) AS r_rent_vs_income,
       count(*) AS block_groups
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet' h
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.parquet' i
  USING (geoid)
WHERE h.pct_rent_burdened IS NOT NULL AND i.median_hh_income IS NOT NULL
  AND h.median_gross_rent IS NOT NULL;
```

→ `-0.222 | 0.666 | 160374`, 7.9 s. Rent rises steeply with income (+0.67)
while the share of renters burdened by it falls only weakly (−0.22) — rent
burden is much less a function of neighbourhood income than rent is. Do not
divide the two medians into each other to make a "rent-to-income ratio": they
come from different universes (all households vs renter households paying cash
rent), and a ratio of two medians is not the median of the ratio.

Note the row count: 160,374 of 242,298 block groups clear all three NOT NULL
tests — two thirds. That is the real sample for any rent analysis at this
geography.

### Related recipes elsewhere

- Income inequality inside one county, and the top/bottom-coded income values
  that carry no margin: [`block-groups/bg-income/AGENTS.md`](../bg-income/AGENTS.md).
- Housing *units* as a 2020 complete count rather than an ACS estimate:
  [`blocks/AGENTS.md`](../../blocks/AGENTS.md).
- Most rent-burdened large cities:
  [`places/AGENTS.md`](../../places/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe` or
`*_cv` columns and its coarse zooms are A5 cell aggregations — which average
medians unweighted — so nothing above can be reproduced from tiles.
