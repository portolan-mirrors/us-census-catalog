# Agent guide — Housing & Rent (Census Tracts)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

The housing stock and what it costs: total units and the vacancy rate ([B25002](https://data.census.gov/table/ACSDT5Y2024.B25002)), households and the owner-occupied share ([B25003](https://data.census.gov/table/ACSDT5Y2024.B25003)), median gross rent ([B25064](https://data.census.gov/table/ACSDT5Y2024.B25064)) and median owner-occupied home value ([B25077](https://data.census.gov/table/ACSDT5Y2024.B25077)), the share of renter households paying 30% and 50% or more of income on rent ([B25070](https://data.census.gov/table/ACSDT5Y2024.B25070)), the pre-1940 share ([B25034](https://data.census.gov/table/ACSDT5Y2024.B25034)) and the single-family share ([B25024](https://data.census.gov/table/ACSDT5Y2024.B25024)).

**85,184 rows**, one per census tract, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.pmtiles`, layer `tract-housing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/collection.json` — carries a full description for every column

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

`geoid` is 11 characters and is the join key: `substr(geoid, 1, 5)` → county, `substr(geoid, 1, 2)` → state FIPS; block groups and blocks join back on their own first 11 characters.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 11-character tract GEOID: state 2 + county 3 + tract 6. |
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
| `population` | NULL on 0.16% of tracts: 126 island-area tracts plus 14 in Suffolk County, NY. |
| `median_gross_rent` | NULL on 5.92% of tracts (29.68% of block groups, for comparison). |
| `pct_rent_burdened` | NULL on 1.51% of tracts. |
| `median_home_value` | NULL on 3.55% of tracts. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

Suffolk County, New York (36103) was re-delineated in the 2024 vintage: 39 block groups and 14 tracts exist in the 2024 cartographic boundary files with no matching row in the 2020-based ACS tabulation, and publish with NULL ACS values. These are the only non-territory rows in the catalog with geometry but no data.

443 ACS block groups and 338 ACS tracts (the `9900xx`-style water geographies) have no polygon in the cartographic boundary files and therefore no row here. All of them have population 0, so the dropped population is exactly 0 — this is why the tract collections hold 85,184 rows against 85,382 in the ACS release.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: below z6 you are looking at counties, not tracts. The values there are the Census Bureau's own estimates for those geographies, not an aggregation of this file, and `*_moe` columns are not in the tiles. Statistics come from the GeoParquet.

## Related collections

- [`tracts/tract-income`](../tract-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-people`](../tract-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-connectivity`](../tract-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-wellbeing`](../tract-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`block-groups/bg-housing`](../../block-groups/bg-housing/collection.json) — the same theme one geography down, with wider margins of error.
- [`counties`](../../counties/collection.json) and [`states`](../../states/collection.json) — every indicator in one wide table per geography.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run against the published URLs with DuckDB 1.4.1
immediately before it was written down, and its real output is quoted beside
it.

### 1. What is a tract's housing worth, and where is the top code?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(median_home_value)                        AS published,
       quantile_cont(median_home_value, 0.10)::int     AS p10,
       quantile_cont(median_home_value, 0.50)::int     AS p50,
       quantile_cont(median_home_value, 0.90)::int     AS p90,
       count(*) FILTER (WHERE median_home_value = 2000001) AS top_coded
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet';
```

→ `82164 | 121000 | 305100 | 778000 | 576`, in **2.1 s**. 576 tracts sit on
the upstream top code of $2,000,001 — that is a published ceiling, not a jam
value, so it is not NULL and it is not a measurement either. Exclude it before
fitting anything, and never read it as "the median home is worth two million".

One state, reliability-gated:

```sql
LOAD httpfs;
SELECT geoid, name, median_home_value::int AS value, round(median_home_value_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet'
WHERE state = 'CO' AND median_home_value_cv < 0.12
ORDER BY median_home_value DESC LIMIT 5;
```

→ `08013012505 | Census Tract 125.05, Boulder County, Colorado | 1675500 |
0.04`, `08035014142 | … Douglas County … | 1643600 | 0.04`, `08005005622 | …
Arapahoe County … | 1632800 | 0.07`, `08107000500 | Census Tract 5, Routt
County, Colorado | 1630900 | 0.08`, `08013012401 | … Boulder County … |
1602200 | 0.04`. 5.0 s.

### 2. The most rent-burdened tracts, reliability-filtered (`*_cv`)

```sql
LOAD httpfs;
SELECT geoid, state, households, pct_rent_burdened,
       pct_rent_burdened_moe AS moe, round(pct_rent_burdened_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet'
WHERE households > 1000 AND pct_rent_burdened_cv < 0.10
ORDER BY pct_rent_burdened DESC LIMIT 5;
```

→ `12105011821 | FL | 1002 | 100.0 | 12.37 | 0.08`, `12085001108 | FL | 2625 |
100.0 | 15.71 | 0.1`, `12099005955 | FL | 2568 | 100.0 | 14.03 | 0.09`,
`12011110357 | FL | 2200 | 100.0 | 16.29 | 0.1`, `15003008415 | HI | 1130 |
100.0 | 9.12 | 0.06`. 4.7 s.

Four of the five are Florida and the fifth is Hawaii; `pct_rent_burdened =
100.0` on 1,000–2,600 households is a real finding, not a small-sample
artifact, and the `_cv` gate is what lets you say so. Remember the
denominator: renter households whose rent-to-income ratio the Bureau could
compute, which excludes B25070's "Not computed" line. It is not a share of all
households in the tract.

### 3. Rent burden across the income distribution (1:1 sibling join)

```sql
LOAD httpfs;
WITH j AS (
  SELECT ntile(5) OVER (ORDER BY i.median_hh_income) AS q,
         h.pct_rent_burdened, h.median_gross_rent
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet' i
  JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet' h
    USING (geoid)
  WHERE i.median_hh_income IS NOT NULL AND h.pct_rent_burdened IS NOT NULL)
SELECT q AS income_quintile, count(*) AS tracts,
       round(avg(pct_rent_burdened), 1) AS avg_rent_burdened,
       round(avg(median_gross_rent))    AS avg_of_tract_rent_medians
FROM j GROUP BY 1 ORDER BY 1;
```

→

```
1 | 16705 | 56.2 |  991
2 | 16705 | 49.4 | 1163
3 | 16704 | 47.2 | 1359
4 | 16704 | 46.7 | 1655
5 | 16704 | 44.8 | 2248
```

8.0 s. Rent more than doubles from the poorest to the richest quintile of
tracts while the burdened share falls only 11 points — the burden is a floor,
not a poverty phenomenon.

`avg_of_tract_rent_medians` is named awkwardly on purpose: it is the mean of
85,184 tract medians, which is **not** the median rent of the quintile and is
not a quantity the Census Bureau publishes. It is legitimate as "what the
typical tract in this band looks like" and illegitimate as "what renters pay".
A median of a region is not derivable from the medians of its parts.

### 4. When to step down a geography — and when not to

```sql
LOAD httpfs;
SELECT 'tract' AS geography,
       round(100.0*(count(*)-count(median_gross_rent))/count(*), 2) AS pct_rent_null,
       round(100.0*(count(*)-count(median_home_value))/count(*), 2) AS pct_value_null
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet'
UNION ALL
SELECT 'block group',
       round(100.0*(count(*)-count(median_gross_rent))/count(*), 2),
       round(100.0*(count(*)-count(median_home_value))/count(*), 2)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet';
```

→ `tract | 5.92 | 3.55`, `block group | 29.68 | 10.03`. 8.3 s for both files.

Going down to block groups multiplies missing rent medians by five and missing
home values by three. Go down anyway when the question is genuinely
sub-tract — a single neighbourhood, a service area — and accept the holes;
stay here when the question is comparative or mapped at scale.

### Related recipes elsewhere

- The same columns one geography down, and the rent-vs-income correlation:
  [`block-groups/bg-housing/AGENTS.md`](../../block-groups/bg-housing/AGENTS.md).
- Most rent-burdened large cities, with each city's state for context:
  [`places/AGENTS.md`](../../places/AGENTS.md).
- Housing units as 2020 complete counts, rolled up from blocks:
  [`blocks/AGENTS.md`](../../blocks/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and below z6 its features are counties carrying the Census Bureau's
own county medians rather than these tracts', so nothing above can be
reproduced from tiles.
