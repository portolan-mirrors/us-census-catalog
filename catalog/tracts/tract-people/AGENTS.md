# Agent guide — People & Education (Census Tracts)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Who lives here: median age and the shares under 18 and 65 or over ([B01002](https://data.census.gov/table/ACSDT5Y2024.B01002), [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001)), the five mutually exclusive non-Hispanic race shares plus Hispanic or Latino of any race and their complement, people of color ([B03002](https://data.census.gov/table/ACSDT5Y2024.B03002)), and the share of adults 25 and over holding a bachelor's degree or higher ([B15003](https://data.census.gov/table/ACSDT5Y2024.B15003)).

**85,184 rows**, one per census tract, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/tract-people.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/tract-people.pmtiles`, layer `tract-people`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/collection.json` — carries a full description for every column

## Source tables

| table | title | universe |
|---|---|---|
| [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001) | Sex by Age | Total population |
| [B01002](https://data.census.gov/table/ACSDT5Y2024.B01002) | Median Age by Sex | Total population |
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) | Hispanic or Latino Origin by Race | Total population |
| [B15003](https://data.census.gov/table/ACSDT5Y2024.B15003) | Educational Attainment for the Population 25 Years and Over | Population 25 years and over |

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
| `population` | NULL on 0.16% of tracts: 126 island-area tracts plus 14 in Suffolk County, NY. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

Suffolk County, New York (36103) was re-delineated in the 2024 vintage: 39 block groups and 14 tracts exist in the 2024 cartographic boundary files with no matching row in the 2020-based ACS tabulation, and publish with NULL ACS values. These are the only non-territory rows in the catalog with geometry but no data.

443 ACS block groups and 338 ACS tracts (the `9900xx`-style water geographies) have no polygon in the cartographic boundary files and therefore no row here. All of them have population 0, so the dropped population is exactly 0 — this is why the tract collections hold 85,184 rows against 85,382 in the ACS release.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are A5 cell aggregations, not census geographies — counts summed, rates and medians averaged unweighted. Statistics come from the GeoParquet.

## Related collections

- [`tracts/tract-income`](../tract-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-housing`](../tract-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-connectivity`](../tract-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-wellbeing`](../tract-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`block-groups/bg-people`](../../block-groups/bg-people/collection.json) — the same theme one geography down, with wider margins of error.
- [`counties`](../../counties/collection.json) and [`states`](../../states/collection.json) — every indicator in one wide table per geography.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run against the published URLs with DuckDB 1.4.1
immediately before it was written down, and its real output is quoted beside
it. **This collection has no `*_cv` columns** — reliability work here uses
`<name>_moe` directly.

### 1. How old is the country, tract by tract?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(median_age)               AS published,
       quantile_cont(median_age, 0.10) AS p10,
       quantile_cont(median_age, 0.50) AS p50,
       quantile_cont(median_age, 0.90) AS p90
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/tract-people.parquet';
```

→ `84483 | 31.0 | 39.9 | 50.6`, in **2.1 s**. 84,483 of 85,184 tracts carry a
median age. Grouping the 701 that do not (measured) gives 515 tracts with
`population = 0`, 140 with no ACS row at all (`population IS NULL` — the
island areas and the re-delineated Suffolk County tracts), and 46 with a
population but no publishable median. Almost all of the missingness is
"nobody lives here", not suppression.

One state, with the margin alongside:

```sql
LOAD httpfs;
SELECT geoid, name, population, median_age, median_age_moe AS moe, pct_65_plus
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/tract-people.parquet'
WHERE state = 'FL' AND population > 2000
ORDER BY median_age DESC LIMIT 5;
```

→ `12071001915 | Census Tract 19.15, Lee County, Florida | 3044 | 81.5 | 1.4 |
91.92`, `12103027330 | … Pinellas County … | 2437 | 80.0 | 4.7 | 73.37`,
`12099005944 | … Palm Beach County … | 2342 | 78.0 | 3.5 | 85.23`,
`12099005947 | … Palm Beach County … | 4220 | 77.6 | 2.5 | 86.97`,
`12021011003 | … Collier County … | 3779 | 77.1 | 3.0 | 80.82`. 4.3 s.

A median age of 81.5 ± 1.4 with 91.92% of residents over 65 is a retirement
community, and the margin is narrow enough to say so. The `population > 2000`
gate keeps out tiny tracts whose median age swings on a handful of people.

### 2. Which tract am I in? (point-in-polygon, `bbox` prefilter)

```sql
LOAD spatial; LOAD httpfs;
SELECT geoid, name, population, median_age, pct_bachelors_plus
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/tract-people.parquet'
WHERE bbox.xmin <= -122.3493 AND bbox.xmax >= -122.3493
  AND bbox.ymin <=   47.6205 AND bbox.ymax >=   47.6205
  AND ST_Contains(geometry, ST_Point(-122.3493, 47.6205));
```

→ one row: `53033007101 | Census Tract 71.01, King County, Washington | 3104 |
30.6 | 74.27`. **6.5 s** against a 56 MB file, because the four `bbox`
comparisons prune row groups by the parquet's own statistics before any
geometry is decoded. Drop them and DuckDB decodes 85,184 polygons instead.

The pattern generalises to any lookup: `bbox.xmin <= lon AND bbox.xmax >= lon
AND bbox.ymin <= lat AND bbox.ymax >= lat` is the exact bbox-contains-point
test, and `ST_Contains` then resolves the handful of candidates. Geometry is
`(lon, lat)` in EPSG:4326, so `ST_Point` takes longitude first. With
`LOAD spatial`, `geometry` reads back as a `GEOMETRY` — `ST_GeomFromWKB` is
unnecessary and raises a binder error.

These are shoreline-clipped cartographic boundaries, which is what you want
for a point-in-polygon lookup on land and not what you want for a point
offshore.

### 3. Education and income at tract scale (1:1 join to a sibling chunk)

```sql
LOAD httpfs;
SELECT count(*) AS tracts,
       round(corr(p.pct_bachelors_plus, i.median_hh_income), 3) AS r_degree_income,
       round(corr(p.median_age, i.median_hh_income), 3)         AS r_age_income
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/tract-people.parquet' p
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet' i
  USING (geoid)
WHERE i.median_hh_income IS NOT NULL AND p.pct_bachelors_plus IS NOT NULL;
```

→ `83827 | 0.715 | 0.165`. 8.1 s. The degree–income correlation is 0.715 at
tract level against 0.674 at block-group level (measured in
[`bg-income`](../../block-groups/bg-income/AGENTS.md)) — tightening as the
margins narrow, which is what you would expect if the block-group figure is
attenuated by noise rather than describing a different world.

### 4. Significance before ranking (`*_moe`)

```sql
LOAD httpfs;
SELECT count(*)                                                        AS estimate_over_50,
       count(*) FILTER (WHERE pct_hispanic - pct_hispanic_moe > 50)    AS significantly_over_50
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/tract-people.parquet'
WHERE pct_hispanic > 50;
```

→ `9621 | 6793`. 3.9 s. Of the 9,621 tracts estimated to be majority-Hispanic,
6,793 — 71% — stay above 50% at the bottom of their 90% margin. Compare the
same shape of test on `pct_65_plus` at block-group level, where only a third
survive (5,004 → 1,663, measured in
[`bg-people`](../../block-groups/bg-people/AGENTS.md)). Narrower margins are
the whole argument for working at this geography; they are not a licence to
skip the test.

### Related recipes elsewhere

- The same indicators one geography down, with wider margins:
  [`block-groups/bg-people/AGENTS.md`](../../block-groups/bg-people/AGENTS.md).
- Race and ethnicity as 2020 complete counts (different universe definitions —
  read the field notes): [`blocks/AGENTS.md`](../../blocks/AGENTS.md).
- Income by race for these same tracts:
  [`tracts/tract-wellbeing/AGENTS.md`](../tract-wellbeing/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns and its coarse zooms are A5 cell aggregations, so no significance test
above can be reproduced from tiles.
