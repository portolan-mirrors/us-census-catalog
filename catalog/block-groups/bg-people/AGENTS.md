# Agent guide — People & Education (Block Groups)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Who lives here: median age and the shares under 18 and 65 or over ([B01002](https://data.census.gov/table/ACSDT5Y2024.B01002), [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001)), the five mutually exclusive non-Hispanic race shares plus Hispanic or Latino of any race and their complement, people of color ([B03002](https://data.census.gov/table/ACSDT5Y2024.B03002)), and the share of adults 25 and over holding a bachelor's degree or higher ([B15003](https://data.census.gov/table/ACSDT5Y2024.B15003)).

**242,298 rows**, one per block group, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/bg-people.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/bg-people.pmtiles`, layer `bg-people`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/collection.json` — carries a full description for every column

## Source tables

| table | title | universe |
|---|---|---|
| [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001) | Sex by Age | Total population |
| [B01002](https://data.census.gov/table/ACSDT5Y2024.B01002) | Median Age by Sex | Total population |
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) | Hispanic or Latino Origin by Race | Total population |
| [B15003](https://data.census.gov/table/ACSDT5Y2024.B15003) | Educational Attainment for the Population 25 Years and Over | Population 25 years and over |

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
| `median_age` | double | Median age in years. |
| `median_age_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_age`. |
| `pct_under_18` | double | Percent of the population under 18 years old. |
| `pct_under_18_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_under_18`. |
| `pct_65_plus` | double | Percent of the population 65 years and over. |
| `pct_65_plus_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_65_plus`. |
| `pct_white_nh` | double | Percent of the population that is White alone and not Hispanic or Latino. |
| `pct_white_nh_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_white_nh`. |
| `pct_black` | double | Percent of the population that is Black or African American alone and not Hispanic or Latino. |
| `pct_black_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_black`. |
| `pct_native` | double | Percent of the population that is American Indian and Alaska Native alone and not Hispanic or Latino. |
| `pct_native_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_native`. |
| `pct_asian` | double | Percent of the population that is Asian alone and not Hispanic or Latino. |
| `pct_asian_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_asian`. |
| `pct_hispanic` | double | Percent of the population that is Hispanic or Latino, of any race. |
| `pct_hispanic_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_hispanic`. |
| `pct_people_of_color` | double | Percent of the population that is not White-alone non-Hispanic: `100 − pct_white_nh`. |
| `pct_people_of_color_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_people_of_color`. |
| `pct_bachelors_plus` | double | Percent of adults 25 and over whose highest attainment is a bachelor's degree or more. |
| `pct_bachelors_plus_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_bachelors_plus`. |
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
- **`pct_people_of_color` is a complement** (`100 − pct_white_nh`) and carries `pct_white_nh`'s margin of error unchanged.
- **The five race shares are all non-Hispanic**, drawn from B03002's "Not Hispanic or Latino" branch, so they and `pct_hispanic` are mutually exclusive and do not double-count.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.18% of block groups — the island areas (405 block groups with 2024 boundaries but no ACS data) and the 39 Suffolk County, NY block groups re-delineated in this vintage. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

Suffolk County, New York (36103) was re-delineated in the 2024 vintage: 39 block groups and 14 tracts exist in the 2024 cartographic boundary files with no matching row in the 2020-based ACS tabulation, and publish with NULL ACS values. These are the only non-territory rows in the catalog with geometry but no data.

443 ACS block groups and 338 ACS tracts (the `9900xx`-style water geographies) have no polygon in the cartographic boundary files and therefore no row here. All of them have population 0, so the dropped population is exactly 0 — this is why the tract collections hold 85,184 rows against 85,382 in the ACS release.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: below z8 you are looking at counties and tracts, not block groups. The values there are the Census Bureau's own estimates for those geographies, not an aggregation of this file, and `*_moe` columns are not in the tiles. Statistics come from the GeoParquet.

## Related collections

- [`block-groups/bg-income`](../bg-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`block-groups/bg-housing`](../bg-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`block-groups/bg-connectivity`](../bg-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-people`](../../tracts/tract-people/collection.json) — the same theme one geography up, with narrower margins of error.
- [`counties`](../../counties/collection.json) and [`states`](../../states/collection.json) — every indicator in one wide table per geography.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run against the published URLs with DuckDB 1.4.1
immediately before it was written down, and its real output is quoted beside
it. **This collection has no `*_cv` columns** — every reliability test below
therefore works from `<name>_moe` directly, which is the only honest option
here.

### 1. How much does educational attainment vary between block groups?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(pct_bachelors_plus)                  AS published,
       quantile_cont(pct_bachelors_plus, 0.10)    AS p10,
       quantile_cont(pct_bachelors_plus, 0.50)    AS p50,
       quantile_cont(pct_bachelors_plus, 0.90)    AS p90
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/bg-people.parquet';
```

→ `240099 | 8.94 | 29.47 | 67.11`, in 3.6 s. A factor of seven between the
tenth and ninetieth percentile block group — the spread this geography exists
to show.

One state is the same query plus `WHERE state = 'XX'`; DuckDB fetches only the
columns named, so a state slice costs about what the national sweep costs.

### 2. The trap: top-N on a share without its margin

```sql
LOAD httpfs;
SELECT geoid, population, pct_bachelors_plus, pct_bachelors_plus_moe AS moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/bg-people.parquet'
WHERE state = 'NC' AND population > 1000
ORDER BY pct_bachelors_plus DESC LIMIT 5;
```

→ `370630015011 | 3333 | 100.0 | 37.31`, `371830516001 | 1083 | 100.0 | 8.97`,
`371190064032 | 1813 | 100.0 | 35.43`, `371830516002 | 1025 | 97.49 | 50.26`,
`371190028001 | 1023 | 96.62 | 7.71`. 4.1 s.

Three ties at 100.0, and the margins run from ±7.71 to ±50.26 points. The
fourth row's estimate of 97.49 ± 50.26 is consistent with anything from 47% to
100%. A ranking built on the estimate alone is a ranking of noise; rank on
`estimate - moe` instead, which is what recipe 3 does.

### 3. Significance, not estimates: where is the 65+ share really over half?

```sql
LOAD httpfs;
SELECT count(*)                                                     AS estimate_over_50,
       count(*) FILTER (WHERE pct_65_plus - pct_65_plus_moe > 50)   AS significantly_over_50
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/bg-people.parquet'
WHERE pct_65_plus > 50;
```

→ `5004 | 1663`, 4.4 s. 5,004 block groups estimate a majority over 65; only
1,663 of them — a third — stay above 50% at the bottom of their 90% margin.
The other 3,341 are candidates, not findings. `estimate - moe` is the lower
bound of the published interval, so this is the Bureau's own arithmetic, not an
added assumption.

### 4. Educated *and* well-paid, both tests passed (1:1 join to a sibling chunk)

```sql
LOAD httpfs;
SELECT p.geoid, p.population, p.pct_bachelors_plus, p.pct_bachelors_plus_moe AS moe,
       i.median_hh_income::int AS income, round(i.median_hh_income_cv, 2) AS income_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/bg-people.parquet' p
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.parquet' i
  USING (geoid)
WHERE p.state = 'NC' AND p.population > 1000
  AND p.pct_bachelors_plus - p.pct_bachelors_plus_moe > 80
  AND i.median_hh_income_cv < 0.12
ORDER BY p.pct_bachelors_plus DESC;
```

→ four rows: `371830518002 | 1723 | 96.58 | 8.65 | 242963 | 0.08`,
`370630020332 | 1859 | 96.48 | 6.44 | 173732 | 0.11`,
`370630020201 | 3190 | 95.11 | 12.51 | 196364 | 0.07`,
`371350107061 | 1904 | 88.67 | 4.92 | 209099 | 0.03`. 8.5 s.

Four survivors out of the dozens the naive query in recipe 2 would have
offered. The join is 1:1 on `geoid`: both chunks hold all 242,298 block
groups, same geometry, same vintage.

### 5. The very youngest block groups — and what they turn out to be

```sql
LOAD httpfs;
SELECT geoid, state, population, median_age, median_age_moe AS moe, pct_under_18
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/bg-people.parquet'
WHERE population > 2000 AND median_age + median_age_moe < 22
ORDER BY median_age LIMIT 5;
```

→ `360470509002 | NY | 2614 | 9.8 | 4.9 | 63.85`, `515500201004 | VA | 2080 |
10.5 | 7.1 | 71.3`, `360470238002 | NY | 2947 | 10.6 | 2.0 | 60.26`,
`482013314001 | TX | 2428 | 10.7 | 3.1 | 68.49`, `340297170021 | NJ | 2194 |
10.9 | 2.1 | 61.8`. 8.4 s.

Note what came back: the `pct_under_18` column, 60–71% on every row, says
these are *family* neighbourhoods with very many children, not dormitories.
A median age of 9.8 cannot be a student population. Reading one column without
its neighbours is how a geography gets mislabelled — the `median_age + moe <
22` test is doing real work here (it is an upper bound), but the
interpretation came from the second column.

### Related recipes elsewhere

- Income inequality inside a single county, and the lat/lon axis trap in
  DuckDB's spheroid functions:
  [`block-groups/bg-income/AGENTS.md`](../bg-income/AGENTS.md).
- Point-in-polygon "which geography am I in":
  [`tracts/tract-people/AGENTS.md`](../../tracts/tract-people/AGENTS.md).
- Race and ethnicity by decennial complete count rather than ACS estimate:
  [`blocks/AGENTS.md`](../../blocks/AGENTS.md) — different universe definitions,
  read its field notes first.

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and below z8 its features are counties and tracts rather than block
groups, so no significance test above can be reproduced from tiles.
