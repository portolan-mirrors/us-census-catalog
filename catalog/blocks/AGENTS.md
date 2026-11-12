# Agent guide — 2020 Census Counts (Blocks)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

2020 Decennial Census counts for all **8,174,955** census blocks in the 50 states, the District of Columbia and Puerto Rico — the smallest geography the Census Bureau publishes anything for. From the [2020 Census P.L. 94-171 Redistricting Data Summary Files](https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html): total population and the seven race-alone counts plus two or more races ([P1](https://data.census.gov/table/DECENNIALPL2020.P1)), Hispanic or Latino and White-alone-not-Hispanic ([P2](https://data.census.gov/table/DECENNIALPL2020.P2)), the voting-age population 18 and over ([P3](https://data.census.gov/table/DECENNIALPL2020.P3)), housing units occupied and vacant ([H1](https://data.census.gov/table/DECENNIALPL2020.H1)), and the group-quarters population ([P5](https://data.census.gov/table/DECENNIALPL2020.P5)), with derived shares and population density.

**8,174,955 rows**, one per census block, 2020 Decennial Census (P.L. 94-171), geometry from TIGER/Line 2024.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/blocks/state_fips=*/*.parquet` — 52 state partitions, read as one table with `hive_partitioning=true`; one state is one file
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
- **Hive partitioning:** read the glob with `hive_partitioning=true` and
  `state_fips` appears as a column alongside the USPS `state` column. Query
  one state by reading its single file — do not scan 52 files to filter one.

## Data quality

28.97% of blocks have `pop_total = 0` (measured), so `pct_white_nh`, `pct_black` and `pct_hispanic` are NULL on that share of rows, and `pct_vacant` is NULL on the 27.64% with no housing units. By design — most census blocks are unpopulated. Filter `pop_total > 0` before averaging a rate.

Geometry is TIGER/Line, which is not shoreline-clipped: a coastal block extends to the 3-mile limit. Water-only blocks have `ALAND20 = 0` and so a NULL `pop_density`.

Blocks carry 2020 Decennial counts only. The Census Bureau publishes no income, education, commuting or internet data below block group, and this collection invents none.

## Related collections

- [`block-groups/`](../block-groups/catalog.json) — ACS indicators at the finest geography the Bureau publishes income and housing data for. A block's block group is `substr(geoid, 1, 12)`.
- [`tracts/`](../tracts/catalog.json), [`counties`](../counties/collection.json), [`states`](../states/collection.json) — coarser ACS geographies, all joinable by GEOID prefix.

## Example queries

<!-- TODO-recipes: a later agent writes this section. Requirements:
     3-5 DuckDB recipes, each actually executed against the published URLs
     above (not localhost, not a local path) with its real output pasted in;
     `INSTALL httpfs; LOAD httpfs;` on the first one; at least one that
     reads a single state partition rather than the whole glob, and at least
     one that rolls blocks up to their block group (`substr(geoid, 1, 12)`)
     and joins a block-group collection. Do not write a query that has not
     been run. -->
