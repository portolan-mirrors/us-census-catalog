# Agent guide — Commuting & Connectivity (Census Tracts)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

How people get around and get online: households with no vehicle available, as a count and a share ([B25044](https://data.census.gov/table/ACSDT5Y2024.B25044)); commute mode shares for driving alone, public transportation, walking or cycling, and working from home ([B08301](https://data.census.gov/table/ACSDT5Y2024.B08301)); the share of commutes of 45 minutes or more ([B08303](https://data.census.gov/table/ACSDT5Y2024.B08303)); and the shares of households with no internet access and no computing device ([B28002](https://data.census.gov/table/ACSDT5Y2024.B28002), [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001)).

**85,184 rows**, one per census tract, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.pmtiles`, layer `tract-connectivity`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/collection.json` — carries a full description for every column

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
| `population` | NULL on 0.16% of tracts: 126 island-area tracts plus 14 in Suffolk County, NY. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

Suffolk County, New York (36103) was re-delineated in the 2024 vintage: 39 block groups and 14 tracts exist in the 2024 cartographic boundary files with no matching row in the 2020-based ACS tabulation, and publish with NULL ACS values. These are the only non-territory rows in the catalog with geometry but no data.

443 ACS block groups and 338 ACS tracts (the `9900xx`-style water geographies) have no polygon in the cartographic boundary files and therefore no row here. All of them have population 0, so the dropped population is exactly 0 — this is why the tract collections hold 85,184 rows against 85,382 in the ACS release.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: below z6 you are looking at counties, not tracts. The values there are the Census Bureau's own estimates for those geographies, not an aggregation of this file, and `*_moe` columns are not in the tiles. Statistics come from the GeoParquet.

## Related collections

- [`tracts/tract-income`](../tract-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-people`](../tract-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-housing`](../tract-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-wellbeing`](../tract-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`block-groups/bg-connectivity`](../../block-groups/bg-connectivity/collection.json) — the same theme one geography down, with wider margins of error.
- [`counties`](../../counties/counties/collection.json) and [`states`](../../states/states/collection.json) — every indicator in one wide table per geography; each is also a group of five themed chunks matching these ([counties/](../../counties/AGENTS.md), [states/](../../states/AGENTS.md)).
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run against the published URLs with DuckDB 1.4.1
immediately before it was written down, and its real output is quoted beside
it.

### 1. How rare is transit commuting? (the distribution first, always)

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(pct_commute_transit)                           AS published,
       round(avg(pct_commute_transit), 2)                   AS mean,
       quantile_cont(pct_commute_transit, 0.50)             AS p50,
       round(quantile_cont(pct_commute_transit, 0.99), 2)   AS p99,
       max(pct_commute_transit)                             AS max
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.parquet';
```

→ `84378 | 3.37 | 0.1 | 49.67 | 100.0`, in **2.7 s**. The median tract sends
one commuter in a thousand by transit, the 99th percentile sends half, and the
maximum is 100. A linear colour ramp on this column shows one colour; this is
the distribution that `styles/` class breaks were measured from.

One state, reliability-gated:

```sql
LOAD httpfs;
SELECT geoid, name, pct_commute_transit, round(pct_commute_transit_cv, 2) AS cv,
       pct_commute_drive_alone
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.parquet'
WHERE state = 'MA' AND pct_commute_transit_cv < 0.12
ORDER BY pct_commute_transit DESC LIMIT 5;
```

→ `25025050700 | Census Tract 507, Suffolk County, Massachusetts | 58.7 | 0.11
| 13.51`, `25025050600 | … | 54.08 | 0.05 | 14.1`, `25025050500 | … | 53.39 |
0.12 | 17.82`, `25025050200 | … | 47.56 | 0.06 | 21.9`, `25025081200 | … |
34.57 | 0.12 | 32.99`. 6.4 s. All five are Suffolk County — Boston. Carrying
`pct_commute_drive_alone` alongside is a free sanity check: the two shares
share the B08301 denominator, so they must trade off, and they do.

### 2. The commute and the income distribution (1:1 sibling join)

```sql
LOAD httpfs;
WITH j AS (
  SELECT ntile(5) OVER (ORDER BY i.median_hh_income) AS q,
         c.pct_work_from_home, c.pct_commute_45min_plus, c.pct_no_internet
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet' i
  JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.parquet' c
    USING (geoid)
  WHERE i.median_hh_income IS NOT NULL AND c.pct_work_from_home IS NOT NULL)
SELECT q AS income_quintile,
       round(avg(pct_work_from_home), 1)     AS wfh,
       round(avg(pct_commute_45min_plus), 1) AS commute_45min_plus,
       round(avg(pct_no_internet), 1)        AS no_internet
FROM j GROUP BY 1 ORDER BY 1;
```

→

```
1 |  8.2 | 14.7 | 13.1
2 |  9.9 | 15.3 |  9.2
3 | 12.3 | 16.1 |  6.8
4 | 16.1 | 17.4 |  4.6
5 | 24.0 | 19.0 |  2.4
```

7.0 s. Working from home triples across the income distribution while
households without internet fall by a factor of five — the same gradient from
two directions. Long commutes rise slightly with income, which surprises
people and is a real feature of these estimates.

One caveat the numbers hide: `pct_commute_45min_plus` divides by workers who
did **not** work from home (B08303's universe) while `pct_work_from_home`
divides by all workers 16+ (B08301). The two columns in this table do not
share a denominator and must not be added.

### 3. Where "no internet" is highest, and the degenerate-universe trap (`*_cv`)

```sql
LOAD httpfs;
SELECT geoid, state, population, pct_no_internet,
       pct_no_internet_moe AS moe, round(pct_no_internet_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.parquet'
WHERE population > 2000 AND pct_no_internet_cv < 0.12
ORDER BY pct_no_internet DESC LIMIT 5;
```

→ `42027012100 | PA | 7817 | 100.0 | 0.0 | 0.0`, `36071015008 | NY | 4994 |
88.16 | 11.13 | 0.08`, `36071015007 | NY | 5740 | 86.56 | 9.36 | 0.07`,
`36087011505 | NY | 3764 | 79.69 | 7.02 | 0.05`, `36087011506 | NY | 6601 |
79.53 | 7.73 | 0.06`. 4.5 s.

The first row is the lesson. 7,817 residents, 100.0% of households without
internet, margin exactly 0.0 — because the tract has **8 households and 7,797
people in group quarters** (measured, below). It is a dormitory. `population`
is not a household count, so a population gate does not protect a
household-denominated column:

```sql
LOAD httpfs;
SELECT w.geoid, w.population, w.group_quarters_pop, h.households, c.pct_no_internet
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet' w
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet' h USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.parquet' c USING (geoid)
WHERE w.geoid = '42027012100';
```

→ `42027012100 | 7817 | 7797 | 8 | 100.0`. 9.5 s (three files, one row).
Gate on `households` from
[`tract-housing`](../tract-housing/collection.json), and read `moe = 0.0` as a
flag to inspect the row rather than as high precision.

### 4. Which tracts are genuinely majority-transit? (margins, not estimates)

```sql
LOAD httpfs;
SELECT count(*)                                                                  AS estimate_over_25,
       count(*) FILTER (WHERE pct_commute_transit - pct_commute_transit_moe > 25) AS significantly_over_25
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.parquet'
WHERE pct_commute_transit > 25;
```

→ `2882 | 1716`. 4.1 s. 2,882 tracts estimate at least a quarter of commuters
on transit; 1,716 of them — 60% — hold that at the bottom of their 90% margin.
Two in five of the apparent transit strongholds do not survive their own
margin.
`estimate - moe` is the published interval's lower bound, so this is the
Bureau's own arithmetic rather than an added assumption.

### Related recipes elsewhere

- The same columns one geography down, with the car-free count vs share
  distinction:
  [`block-groups/bg-connectivity/AGENTS.md`](../../block-groups/bg-connectivity/AGENTS.md).
- Population density against car ownership and transit, nationally:
  [`catalog/AGENTS.md`](../../AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and below z6 its features are counties rather than tracts, so nothing
above can be reproduced from tiles.
