# Agent guide — Commuting & Connectivity (Block Groups)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

How people get around and get online: households with no vehicle available, as a count and a share ([B25044](https://data.census.gov/table/ACSDT5Y2024.B25044)); commute mode shares for driving alone, public transportation, walking or cycling, and working from home ([B08301](https://data.census.gov/table/ACSDT5Y2024.B08301)); the share of commutes of 45 minutes or more ([B08303](https://data.census.gov/table/ACSDT5Y2024.B08303)); and the shares of households with no internet access and no computing device ([B28002](https://data.census.gov/table/ACSDT5Y2024.B28002), [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001)).

**242,298 rows**, one per block group, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/bg-connectivity.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/bg-connectivity.pmtiles`, layer `bg-connectivity`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/collection.json` — carries a full description for every column

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
- **`pct_commute_45min_plus` divides by workers who did not work from home** (B08303's own universe), while every other commute share divides by all workers 16+ (B08301). The two denominators differ, so the shares do not sum across tables.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.18% of block groups — the island areas (405 block groups with 2024 boundaries but no ACS data) and the 39 Suffolk County, NY block groups re-delineated in this vintage. |
| `pct_no_internet` | NULL on 1.13% of block groups. |
| `pct_no_computer` | NULL on 1.13% of block groups. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

Suffolk County, New York (36103) was re-delineated in the 2024 vintage: 39 block groups and 14 tracts exist in the 2024 cartographic boundary files with no matching row in the 2020-based ACS tabulation, and publish with NULL ACS values. These are the only non-territory rows in the catalog with geometry but no data.

443 ACS block groups and 338 ACS tracts (the `9900xx`-style water geographies) have no polygon in the cartographic boundary files and therefore no row here. All of them have population 0, so the dropped population is exactly 0 — this is why the tract collections hold 85,184 rows against 85,382 in the ACS release.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: below z8 you are looking at counties and tracts, not block groups. The values there are the Census Bureau's own estimates for those geographies, not an aggregation of this file, and `*_moe` columns are not in the tiles. Statistics come from the GeoParquet.

## Related collections

- [`block-groups/bg-income`](../bg-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`block-groups/bg-people`](../bg-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`block-groups/bg-housing`](../bg-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-connectivity`](../../tracts/tract-connectivity/collection.json) — the same theme one geography up, with narrower margins of error.
- [`counties`](../../counties/counties/collection.json) and [`states`](../../states/states/collection.json) — every indicator in one wide table per geography; each is also a group of five themed chunks matching these ([counties/](../../counties/AGENTS.md), [states/](../../states/AGENTS.md)).
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run against the published URLs with DuckDB 1.4.1
immediately before it was written down, and its real output is quoted beside
it.

### 1. How car-free is the country, block group by block group?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(pct_hh_no_vehicle)                   AS published,
       quantile_cont(pct_hh_no_vehicle, 0.50)     AS p50,
       quantile_cont(pct_hh_no_vehicle, 0.90)     AS p90,
       round(quantile_cont(pct_hh_no_vehicle, 0.99), 2) AS p99
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/bg-connectivity.parquet';
```

→ `239548 | 3.61 | 23.01 | 70.75`, in 3.2 s. The distribution is extremely
skewed: the median block group is 96% motorised, and car-free living is a
property of the top percentile. Class breaks for this column cannot be
equal-interval.

### 2. Where are the most car-free households? (state filter, count not share)

```sql
LOAD httpfs;
SELECT geoid, hh_no_vehicle, pct_hh_no_vehicle, round(pct_hh_no_vehicle_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/bg-connectivity.parquet'
WHERE state = 'NY'
ORDER BY hh_no_vehicle DESC LIMIT 5;
```

→ `360470555001 | 2867 | 65.09 | 0.09`, `360810019021 | 2708 | 66.42 | 0.09`,
`360610129012 | 2647 | 90.22 | 0.05`, `360610117002 | 2420 | 95.46 | 0.06`,
`360470015021 | 2370 | 79.26 | 0.05`. 5.2 s.

Ordering on `hh_no_vehicle` (the count) rather than `pct_hh_no_vehicle` is
deliberate: the share saturates at 100.0 across hundreds of New York City
block groups, so a share ranking returns an arbitrary slice of ties, while the
count ranks by how many households are actually affected. The collection
carries both for exactly this reason.

### 3. The digital divide, as a gradient (1:1 join to a sibling chunk)

```sql
LOAD httpfs;
WITH j AS (
  SELECT ntile(5) OVER (ORDER BY i.median_hh_income) AS income_quintile,
         c.pct_no_internet, c.pct_hh_no_vehicle
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.parquet' i
  JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/bg-connectivity.parquet' c
    USING (geoid)
  WHERE i.median_hh_income IS NOT NULL AND c.pct_no_internet IS NOT NULL)
SELECT income_quintile, count(*) AS block_groups,
       round(avg(pct_no_internet), 1)  AS avg_pct_no_internet,
       round(avg(pct_hh_no_vehicle), 1) AS avg_pct_no_vehicle
FROM j GROUP BY 1 ORDER BY 1;
```

→

```
1 | 44732 | 13.1 | 15.7
2 | 44732 |  8.8 |  8.1
3 | 44732 |  6.5 |  6.3
4 | 44732 |  4.3 |  5.1
5 | 44731 |  2.2 |  4.7
```

8.1 s. A six-fold gradient in households with no internet across income
quintiles, and the no-vehicle gradient is steeper still at the bottom. These
are unweighted means over block groups, which is the right unit when the
question is "what is a low-income neighbourhood like"; they are **not**
national household shares, because block groups differ in size.

### 4. Where "no internet" is high *and* reliable (`*_cv`)

```sql
LOAD httpfs;
SELECT geoid, state, population, pct_no_internet,
       pct_no_internet_moe AS moe, round(pct_no_internet_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/bg-connectivity.parquet'
WHERE population > 1500 AND pct_no_internet_cv < 0.15
ORDER BY pct_no_internet DESC LIMIT 5;
```

→ `132150106061 | GA | 1764 | 100.0 | 0.0 | 0.0`, `420270121001 | PA | 7817 |
100.0 | 0.0 | 0.0`, `360870115063 | NY | 1805 | 98.09 | 6.01 | 0.04`,
`360710150071 | NY | 2176 | 97.64 | 4.33 | 0.03`, `360870115061 | NY | 2126 |
96.56 | 14.57 | 0.09`.  7.9 s.

The first two rows are the warning this recipe exists to give: a `*_cv` of
exactly 0.00 with a margin of exactly 0.0 is not a precise estimate, it is a
**degenerate universe**. `420270121001` sits in tract `42027012100`, which has
**8 households and 7,797 people in group quarters** (measured in
[`tract-housing`](../../tracts/tract-housing/collection.json) and
[`tract-wellbeing`](../../tracts/tract-wellbeing/collection.json)) — a
dormitory. Eight households, none with internet, gives 100.0% ± 0.0.
`population` is not a household count, so gate on households as well when the
column's denominator is households:

```sql
LOAD httpfs;
SELECT c.geoid, c.state, h.households, c.pct_no_internet,
       c.pct_no_internet_moe AS moe, round(c.pct_no_internet_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/bg-connectivity.parquet' c
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet' h
  USING (geoid)
WHERE h.households > 300 AND c.pct_no_internet_cv < 0.15
ORDER BY c.pct_no_internet DESC LIMIT 5;
```

→ `421010101004 | PA | 307 | 100.0 | 0.0 | 0.0`, `360870115063 | NY | 314 |
98.09 | 6.01 | 0.04`, `360710150071 | NY | 508 | 97.64 | 4.33 | 0.03`,
`360870115061 | NY | 320 | 96.56 | 14.57 | 0.09`, `360470529002 | NY | 384 |
90.89 | 16.82 | 0.11`. 10.4 s.

The dormitory and the Georgia row are gone, and the surviving top four are
large New York block groups with ordinary margins. But the first row still
reads 100.0 ± 0.0 on 307 households, so the honest rule is not "gate on
households and trust the rest": **treat `moe = 0.0` as a flag to inspect the
row, never as high precision.** A zero margin on a non-trivial universe means
the ACS tabulated every sampled household on one side of the line, which
happens and is worth knowing, but it is not the same kind of number as
`98.09 ± 6.01`.

### Related recipes elsewhere

- Density against car ownership, nationally:
  [`catalog/AGENTS.md`](../../AGENTS.md).
- Commuting and internet one geography up, with narrower margins:
  [`tracts/tract-connectivity/AGENTS.md`](../../tracts/tract-connectivity/AGENTS.md).
- The income side of the gradient above:
  [`block-groups/bg-income/AGENTS.md`](../bg-income/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and below z8 its features are counties and tracts rather than block
groups, so nothing above can be reproduced from tiles.
