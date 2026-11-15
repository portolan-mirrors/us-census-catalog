# Agent guide — 2020 Census Counts (Blocks)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

2020 Decennial Census counts for all **8,174,955** census blocks in the 50 states, the District of Columbia and Puerto Rico — the smallest geography the Census Bureau publishes anything for. From the [2020 Census P.L. 94-171 Redistricting Data Summary Files](https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html): total population and the seven race-alone counts plus two or more races ([P1](https://data.census.gov/table/DECENNIALPL2020.P1)), Hispanic or Latino and White-alone-not-Hispanic ([P2](https://data.census.gov/table/DECENNIALPL2020.P2)), the voting-age population 18 and over ([P3](https://data.census.gov/table/DECENNIALPL2020.P3)), housing units occupied and vacant ([H1](https://data.census.gov/table/DECENNIALPL2020.H1)), and the group-quarters population ([P5](https://data.census.gov/table/DECENNIALPL2020.P5)), with derived shares and population density.

**8,174,955 rows**, one per census block, 2020 Decennial Census (P.L. 94-171), geometry from TIGER/Line 2024.

## Where it lives

- **GeoParquet, one state** (the normal case): `https://data.source.coop/portolan-mirrors/us-census-catalog/blocks/state_fips=<FIPS>/<FIPS>.parquet` — e.g. `.../state_fips=29/29.parquet`. One state is one file; pull one and you download one file.
- **GeoParquet, all 52 partitions as one table**: `s3://us-west-2.opendata.source.coop/portolan-mirrors/us-census-catalog/blocks/state_fips=*/*.parquet` with `hive_partitioning = true`. The glob needs object listing, so it works over the S3 endpoint (anonymously, with `SET s3_region='us-west-2'`) and **not** over `https://data.source.coop/…`, where a `state_fips=*/*.parquet` URL returns 404 — plain HTTPS cannot list a directory. Over HTTPS, pass an explicit list of partition URLs to `read_parquet([...], hive_partitioning = true)` instead. Both forms are shown under Example queries.
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/blocks/blocks.pmtiles`, layer `blocks`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/blocks/collection.json` — carries a full description for every column

## Source tables

| table | title | universe |
|---|---|---|
| [P1](https://data.census.gov/table/DECENNIALPL2020.P1) | Race | Total population |
| [P2](https://data.census.gov/table/DECENNIALPL2020.P2) | Hispanic or Latino, and Not Hispanic or Latino by Race | Total population |
| [P3](https://data.census.gov/table/DECENNIALPL2020.P3) | Race for the Population 18 Years and Over | Population 18 years and over |
| [H1](https://data.census.gov/table/DECENNIALPL2020.H1) | Occupancy Status | Housing units |
| [P5](https://data.census.gov/table/DECENNIALPL2020.P5) | Group Quarters Population by Major Group Quarters Type | Population in group quarters |

## Schema

`geoid` is 15 characters and is the join key: `substr(geoid, 1, 12)` → block group, `substr(geoid, 1, 11)` → tract, `substr(geoid, 1, 5)` → county.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 15-character 2020 block GEOID: state 2 + county 3 + tract 6 + block 4 (the geoheader's `GEOCODE`). |
| `state` | string | Two-letter USPS state or territory code. |
| `pop_total` | int32 | Total population of the block, from the 2020 Decennial Census. |
| `pop_white` | int32 | Population reporting White alone. |
| `pop_black` | int32 | Population reporting Black or African American alone. |
| `pop_aian` | int32 | Population reporting American Indian and Alaska Native alone. |
| `pop_asian` | int32 | Population reporting Asian alone. |
| `pop_nhpi` | int32 | Population reporting Native Hawaiian and Other Pacific Islander alone. |
| `pop_other` | int32 | Population reporting Some Other Race alone. |
| `pop_two_plus` | int32 | Population reporting two or more races. |
| `pop_hispanic` | int32 | Population of Hispanic or Latino origin, of any race. |
| `pop_white_nh` | int32 | Population reporting White alone and not Hispanic or Latino. |
| `vap_total` | int32 | Voting-age population: people 18 years and over. |
| `housing_units` | int32 | Total housing units in the block, occupied and vacant. |
| `housing_occupied` | int32 | Occupied housing units. |
| `housing_vacant` | int32 | Vacant housing units. |
| `group_quarters_pop` | int32 | Population living in group quarters — correctional facilities, juvenile facilities, nursing facilities, college/university housing, military quarters, other group quarters. |
| `pct_white_nh` | double | `pop_white_nh` as a percent of `pop_total`, 2 decimals. |
| `pct_black` | double | `pop_black` as a percent of `pop_total`, 2 decimals. |
| `pct_hispanic` | double | `pop_hispanic` as a percent of `pop_total`, 2 decimals. |
| `pct_vacant` | double | `housing_vacant` as a percent of `housing_units`, 2 decimals. |
| `pop_density` | double | People per square kilometre of land area, rounded to 1 decimal: `pop_total / aland_sqkm`. |
| `aland_sqkm` | double | Land area in km² (water excluded), 3 decimals. |
| `geometry` | binary | Boundary polygon, WKB, EPSG:4326 / OGC:CRS84. |
| `bbox` | struct<xmin, ymin, xmax, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, with row-group statistics. |
| `state_fips` | string (hive key) | Hive partition key: 2-digit state FIPS code, synthesized from the directory name when the glob is read. |

## Field notes

- **These are complete counts, not estimates.** There are no `_moe` or `_cv`
  columns, and asking for one is a sign of a query written against the ACS
  collections.
- **The 2020 disclosure-avoidance system injects noise at block level** while
  holding state totals exact. Aggregate freely; treat a single block's counts
  as approximate.
- **The seven race-alone columns plus `pop_two_plus` sum to `pop_total`.**
  `P0010002` ("Population of one race") is an intermediate subtotal and is
  deliberately not carried, which is why the sum closes.
- **`pop_white` and `pop_white_nh` are different measures.** `pop_white` is
  race-alone and crosses Hispanic origin (P1); `pop_white_nh` is the
  not-Hispanic branch of P2. Likewise `pct_black` here is race-alone, while
  `pct_black` in the ACS collections is non-Hispanic Black alone.
- **`pop_hispanic` crosses every race column** — Hispanic origin is asked
  separately from race, so it cannot be added to a race count.
- **`vap_total` is the population 18 and over**; `pop_total - vap_total` is
  the under-18 population.
- **Group-quarters residents are in `pop_total` but live in no housing
  unit**, which is how a block can hold hundreds of people and no units.
- **Hive partitioning:** with `hive_partitioning = true`, `state_fips` appears
  as a synthesized `BIGINT` column (from the directory name) alongside the
  USPS `state` column. Query one state by reading its single file — do not
  scan 52 files to filter one. The `state_fips=*/*.parquet` glob needs object
  listing and therefore the S3 endpoint; over plain HTTPS it 404s, and an
  explicit list of URLs is the substitute. See "Where it lives" above.

## Data quality

28.97% of blocks have `pop_total = 0` (measured), so `pct_white_nh`, `pct_black` and `pct_hispanic` are NULL on that share of rows, and `pct_vacant` is NULL on the 27.64% with no housing units. By design — most census blocks are unpopulated. Filter `pop_total > 0` before averaging a rate.

Geometry is TIGER/Line, which is not shoreline-clipped: a coastal block extends to the 3-mile limit. Water-only blocks have `ALAND20 = 0` and so a NULL `pop_density`.

Blocks carry 2020 Decennial counts only. The Census Bureau publishes no income, education, commuting or internet data below block group, and this collection invents none.

PMTiles coarse zooms are a different census geography from this collection's: below z10 you are looking at counties and tracts, not blocks. Those bands carry exact sums of the block counts (rates recomputed from the summed counts), so they are consistent with the data — but the geometry and the `geoid` belong to the county or tract. Statistics come from the GeoParquet.

Connecticut needs a crosswalk in those coarse bands. The 2020 block GEOIDs carry Connecticut's old 8-county prefixes (09001–09015), while the 2024 boundaries used for the county and tract bands are the 9 planning regions (09110–09190) that replaced them as the county equivalent in 2022. The build matches blocks to current geographies on the 6-digit tract number, which is preserved across the change, so no Connecticut population is dropped: the aggregates still sum to the published national block total of 334,735,155 exactly. The block rows themselves are untouched — they keep the 2020 GEOIDs, so a 5-character prefix join from Connecticut blocks to the 2024-vintage counties collection finds no match.

## Related collections

- [`block-groups/`](../block-groups/catalog.json) — ACS indicators at the finest geography the Bureau publishes income and housing data for. A block's block group is `substr(geoid, 1, 12)`.
- [`tracts/`](../tracts/catalog.json), [`counties/`](../counties/AGENTS.md), [`states/`](../states/AGENTS.md) — coarser ACS geographies, all joinable by GEOID prefix. Each coarse geography is a group of five themed collections plus a wide all-indicator table ([`counties`](../counties/counties/collection.json), [`states`](../states/states/collection.json)).

## Example queries

Every query here was run against the published URLs with DuckDB 1.4.1
immediately before it was written down, and its real output is quoted beside
it. Rhode Island (`state_fips=44`, a 12.8 MB file) is the example state because it
is small; every query works on any of the 52 partitions unchanged — Missouri's
`state_fips=29` is 163 MB, Ohio's `state_fips=39` is 126 MB.

### 1. One state, one file (the hive partition is the filter)

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*) AS blocks, sum(pop_total) AS population, sum(housing_units) AS housing_units,
       round(100.0*count(*) FILTER (WHERE pop_total = 0)/count(*), 2) AS pct_empty
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/blocks/state_fips=44/44.parquet';
```

→ `25649 | 1097379 | 483474 | 16.64`, in **2.1 s** against the 12.8 MB
partition. Rhode Island's 1,097,379 is
its published 2020 resident population, exactly — these are complete counts,
not estimates, and there are no `_moe` or `_cv` columns to ask for.

16.64% of Rhode Island's blocks hold nobody. Nationally the figure is 28.97%
(recipe 5 measures it). Always `WHERE pop_total > 0` before averaging a rate:
`pct_white_nh`, `pct_black` and `pct_hispanic` are NULL on every empty block,
and `avg()` skipping them is not the same as weighting them.

### 2. The densest inhabited blocks in a state

```sql
LOAD httpfs;
SELECT geoid, pop_total, housing_units, round(aland_sqkm, 4) AS sqkm,
       round(pop_density) AS per_sqkm
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/blocks/state_fips=44/44.parquet'
WHERE pop_total > 500
ORDER BY pop_density DESC LIMIT 5;
```

→ `440070036023015 | 1374 | 0 | 0.006 | 248778`, `440070008003011 | 544 | 4 |
0.005 | 99579`, `440070020002005 | 585 | 0 | 0.007 | 84403`,
`440070036021013 | 622 | 0 | 0.011 | 59081`, `440090514001030 | 795 | 0 | 0.02
| 39041`. 3.1 s.

Look at `housing_units`: zero, on four of the five. 1,374 people and no
housing units is a **group-quarters block** — a dormitory, a barracks, a
correctional facility. Group-quarters residents are counted in `pop_total` and
live in no housing unit, so a density ranking at block level returns
institutions before neighbourhoods. Join `group_quarters_pop` or gate on
`housing_units > 0` if you want where people live.

Also: a single block's counts are protected by the 2020 disclosure-avoidance
system, which injects noise at block level while holding state totals exact.
Aggregate freely; treat one block's numbers as approximate.

### 3. Blocks inside a bounding box (`bbox` row-group pruning)

```sql
LOAD httpfs;
SELECT count(*) AS blocks, sum(pop_total) AS people, sum(housing_units) AS units
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/blocks/state_fips=44/44.parquet'
WHERE bbox.xmin < -71.39 AND bbox.xmax > -71.42       -- downtown Providence
  AND bbox.ymin < 41.835 AND bbox.ymax > 41.815;
```

→ `590 | 27039 | 11638`, in **3.9 s**. The `bbox`
covering column has row-group statistics (unlike the string columns), so this
predicate is pushed into the parquet reader and most row groups are never
fetched. The four comparisons are an intersection test — `xmin < east AND xmax
> west AND ymin < north AND ymax > south` — not a containment test; writing it
the other way round silently drops every block straddling the edge of the box.

Note what this gives you that no ACS collection can: a population and housing
count for an arbitrary small area, with no margin of error.

### 4. Rolling blocks up to block groups, and joining the ACS

```sql
LOAD httpfs;
WITH bg AS (
  SELECT substr(geoid, 1, 12) AS bg_geoid,
         sum(pop_total)       AS decennial_2020,
         sum(housing_units)   AS units
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/blocks/state_fips=44/44.parquet'
  GROUP BY 1)
SELECT bg.bg_geoid, bg.decennial_2020, i.population AS acs_2020_2024, bg.units,
       i.median_hh_income::int AS income
FROM bg
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.parquet' i
  ON i.geoid = bg.bg_geoid
WHERE i.state = 'RI'
ORDER BY bg.decennial_2020 DESC LIMIT 5;
```

→ `440090514001 | 6495 | 5762 | 256 | 119444`, `440070036023 | 4359 | 2434 |
260 | 124324`, `440090501041 | 3942 | 3798 | 1583 | 144963`, `440070020002 |
3917 | 4727 | 1231 | NULL`, `440070126011 | 3540 | 3634 | 310 | 117143`.
4.5 s.

`substr(geoid, 1, 12)` is the rollup. A block GEOID is state 2 + county 3 +
tract 6 + block 4 = 15 characters; a block-group GEOID is state 2 + county 3 +
tract 6 + block group 1 = 12, and the block-group digit is the **first digit of
the 4-digit block number**. So characters 1–12 of a block GEOID are exactly its
block group, blocks nest perfectly inside block groups, and this `sum()` is
exact rather than apportioned.

**The two population columns are not comparable row by row, and neither is
wrong.** `decennial_2020` is an April 2020 complete count; `acs_2020_2024` is
a 2020–2024 five-year survey estimate of an average over five years. Row one
differs by 13%, row four by 21% — real change, survey error and different
reference periods, in unknown proportions. Use the decennial count when you
need a count, the ACS estimate when you need an ACS-consistent denominator,
and never present a difference between them as growth.

At state scale they agree closely:

```sql
LOAD httpfs;
SELECT count(*) AS block_groups, sum(decennial_2020) AS decennial_total,
       sum(acs) AS acs_total,
       round(100.0*(sum(acs)-sum(decennial_2020))/sum(decennial_2020), 2) AS pct_diff
FROM (
  SELECT substr(b.geoid, 1, 12) AS bg, sum(b.pop_total) AS decennial_2020,
         any_value(i.population) AS acs
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/blocks/state_fips=44/44.parquet' b
  JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.parquet' i
    ON i.geoid = substr(b.geoid, 1, 12)
  GROUP BY 1);
```

→ `789 | 1097379 | 1101801 | 0.4`. 3.7 s. All 789 Rhode Island block groups
matched (nothing fell out of the join), the blocks sum to the published 2020
count, and the ACS total is 0.4% higher — and equals the `RI` row in
[`states`](../states/states/collection.json) exactly, as it must.

### 5. All 52 partitions as one table

The glob needs object listing, which plain HTTPS cannot do, so this one uses
the S3 endpoint — anonymously, no credentials:

```sql
LOAD httpfs;
SET s3_region = 'us-west-2';
SELECT count(*) AS blocks, sum(pop_total) AS people,
       round(100.0*count(*) FILTER (WHERE pop_total = 0)/count(*), 2) AS pct_empty
FROM read_parquet('s3://us-west-2.opendata.source.coop/portolan-mirrors/us-census-catalog/blocks/state_fips=*/*.parquet',
                  hive_partitioning = true);
```

→ `8174955 | 334735155 | 28.97`, in **26.6 s** — a national sweep of 8.17
million blocks across 52 files, two columns, no download. 8,174,955 is the row
count this collection documents, 334,735,155 is the 2020 resident population
of the 50 states, DC and Puerto Rico (331,449,281 + 3,285,874), and 28.97% is
the empty-block rate quoted above. All three re-measured.

The same URL over `https://data.source.coop/…` returns **404 (Not Found)** —
DuckDB cannot list an HTTP directory. Over HTTPS, name the partitions:

```sql
LOAD httpfs;
SELECT state_fips, count(*) AS blocks, sum(pop_total) AS people
FROM read_parquet([
        'https://data.source.coop/portolan-mirrors/us-census-catalog/blocks/state_fips=44/44.parquet',
        'https://data.source.coop/portolan-mirrors/us-census-catalog/blocks/state_fips=50/50.parquet',
        'https://data.source.coop/portolan-mirrors/us-census-catalog/blocks/state_fips=33/33.parquet'],
      hive_partitioning = true)
GROUP BY 1 ORDER BY 1;
```

→ `33 | 31948 | 1377529`, `44 | 25649 | 1097379`, `50 | 24611 | 643077`. 3.0 s.
`state_fips` is synthesized from the directory name and comes back as a
`BIGINT` (so `33`, not `'33'`), alongside the USPS `state` column from inside
the files.

### Related recipes elsewhere

- ACS income, housing and commuting for these block groups:
  [`block-groups/AGENTS.md`](../block-groups/AGENTS.md) and the four chunk
  guides under it.
- The `bbox`-prefilter pattern with real geometry predicates:
  [`block-groups/bg-income/AGENTS.md`](../block-groups/bg-income/AGENTS.md),
  [`tracts/tract-people/AGENTS.md`](../tracts/tract-people/AGENTS.md).

Statistics come from the GeoParquet. The blocks PMTiles archive is for maps
only, and below z10 its features are counties and tracts rather than census
blocks — exact sums of these block counts, but carrying the county's or
tract's `geoid` and geometry.
