# Agent guide — Income & Poverty (Block Groups)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Income, poverty and employment: median household income and per capita income ([B19013](https://data.census.gov/table/ACSDT5Y2024.B19013), [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301)), the share of people below the poverty line and below twice it ([C17002](https://data.census.gov/table/ACSDT5Y2024.C17002)), the share of households receiving SNAP ([B22010](https://data.census.gov/table/ACSDT5Y2024.B22010)), and the unemployment rate as a share of the civilian labor force ([B23025](https://data.census.gov/table/ACSDT5Y2024.B23025)), plus total population ([B01003](https://data.census.gov/table/ACSDT5Y2024.B01003)) and population density for context.

**242,298 rows**, one per block group, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.pmtiles`, layer `bg-income`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/collection.json` — carries a full description for every column

## Source tables

| table | title | universe |
|---|---|---|
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B19013](https://data.census.gov/table/ACSDT5Y2024.B19013) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) | Households |
| [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301) | Per Capita Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) | Total population |
| [B22010](https://data.census.gov/table/ACSDT5Y2024.B22010) | Receipt of Food Stamps/SNAP in the Past 12 Months by Disability Status for Households | Households |
| [B23025](https://data.census.gov/table/ACSDT5Y2024.B23025) | Employment Status for the Population 16 Years and Over | Population 16 years and over |
| [C17002](https://data.census.gov/table/ACSDT5Y2024.C17002) | Ratio of Income to Poverty Level in the Past 12 Months | Population for whom poverty status is determined |

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
| `median_hh_income` | double | Median household income in the past 12 months, in 2024 inflation-adjusted dollars. |
| `median_hh_income_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income`. |
| `median_hh_income_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income`. |
| `per_capita_income` | double | Per capita income in the past 12 months, in 2024 inflation-adjusted dollars — aggregate income divided by total population, so children and people with no income are in the denominator. |
| `per_capita_income_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `per_capita_income`. |
| `pct_below_poverty` | double | Percent of the population below the federal poverty level — an income-to-poverty ratio under 1.00. |
| `pct_below_poverty_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_below_poverty`. |
| `pct_below_poverty_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_below_poverty`. |
| `pct_below_2x_poverty` | double | Percent of the population with an income-to-poverty ratio under 2.00 — a common proxy for low income rather than deep poverty. |
| `pct_below_2x_poverty_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_below_2x_poverty`. |
| `pct_snap` | double | Percent of households that received Food Stamps/SNAP benefits at any time in the past 12 months. |
| `pct_snap_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_snap`. |
| `pct_unemployed` | double | Unemployment rate: unemployed people as a percent of the civilian labor force. |
| `pct_unemployed_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_unemployed`. |
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
- **`pct_unemployed` divides by the civilian labor force** (B23025 line 3), not by the population 16 and over. That is what makes it an unemployment rate.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.18% of block groups — the island areas (405 block groups with 2024 boundaries but no ACS data) and the 39 Suffolk County, NY block groups re-delineated in this vintage. |
| `median_hh_income` | **NULL on 7.69% of block groups.** The Census Bureau suppresses (jams) a median when the sample behind it is too thin, which at block-group scale is often; the comparable tract rate is 1.59%. Where it is present the margin can still be wide — check `median_hh_income_cv`. |
| `per_capita_income` | NULL on 0.99% of block groups. Part of that is an upstream coverage gap rather than suppression: B19301 publishes 242,069 block-group rows against 242,297 for B01003, and the missing 228 come through as NULL. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

Suffolk County, New York (36103) was re-delineated in the 2024 vintage: 39 block groups and 14 tracts exist in the 2024 cartographic boundary files with no matching row in the 2020-based ACS tabulation, and publish with NULL ACS values. These are the only non-territory rows in the catalog with geometry but no data.

443 ACS block groups and 338 ACS tracts (the `9900xx`-style water geographies) have no polygon in the cartographic boundary files and therefore no row here. All of them have population 0, so the dropped population is exactly 0 — this is why the tract collections hold 85,184 rows against 85,382 in the ACS release.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are A5 cell aggregations, not census geographies — counts summed, rates and medians averaged unweighted. Statistics come from the GeoParquet.

## Related collections

- [`block-groups/bg-people`](../bg-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`block-groups/bg-housing`](../bg-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`block-groups/bg-connectivity`](../bg-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-income`](../../tracts/tract-income/collection.json) — the same theme one geography up, with narrower margins of error.
- [`counties`](../../counties/collection.json) and [`states`](../../states/collection.json) — every indicator in one wide table per geography.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query below was run against the published URLs with DuckDB 1.4.1 and its
real output is quoted beside it. `BG_INCOME` stands for
`https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.parquet`
throughout; substitute it literally.

### 1. Where does block-group median household income sit, nationally?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*)                                                     AS block_groups,
       count(median_hh_income)                                      AS published,
       round(100.0*(count(*)-count(median_hh_income))/count(*), 2)  AS pct_suppressed,
       quantile_cont(median_hh_income, 0.10)::int                   AS p10,
       quantile_cont(median_hh_income, 0.50)::int                   AS p50,
       quantile_cont(median_hh_income, 0.90)::int                   AS p90
FROM 'BG_INCOME';
```

→ `242298 | 223659 | 7.69 | 40977 | 79643 | 154327`. The 7.69% suppression rate
is the one in the table above; a national decile sweep over 242k rows is one
column's worth of bytes and ran in **2.9 s**.

Add `WHERE state = 'NM'` for one state — `1614 | 1444 | 32725 | 62982 | 115441`,
same cost. `state` has no row-group statistics in this file (it is a string
column), so the filter does not skip row groups; what makes both queries cheap
is that DuckDB fetches only the columns named. The predicate that *does* prune
row groups is on `bbox` — see recipe 5.

### 2. How unequal is one county? (GEOID prefix, no join needed)

```sql
LOAD httpfs;
SELECT count(*) AS block_groups, count(median_hh_income) AS published,
       min(median_hh_income)::int                 AS poorest_bg,
       quantile_cont(median_hh_income, 0.5)::int  AS median_bg,
       max(median_hh_income)::int                 AS richest_bg
FROM 'BG_INCOME'
WHERE substr(geoid, 1, 5) = '17031';   -- Cook County, Illinois
```

→ `4001 | 3528 | 2499 | 85773 | 250001`. Read that carefully: **2,499 and
250,001 are the ACS bottom- and top-codes**, not measurements, and they carry
no margin of error at all (`median_hh_income_moe IS NULL` on all 3,458 such
rows nationally — 120 at 2,499 and 3,338 at 250,001, measured). A "100× spread"
from those two numbers is an artifact of coding. For a defensible spread, drop
to coded-free, reliable rows:

```sql
LOAD httpfs;
SELECT geoid, median_hh_income::int AS income, round(median_hh_income_cv, 2) AS cv
FROM 'BG_INCOME'
WHERE substr(geoid,1,5) = '17031' AND median_hh_income IS NOT NULL
  AND median_hh_income_cv < 0.20
ORDER BY median_hh_income DESC LIMIT 3;
```

→ `170318011004 | 248798 | 0.1`, `170318067002 | 246053 | 0.16`,
`170318089002 | 244300 | 0.14`. 2.9 s.

### 3. Does income track education at this scale? (1:1 join to a sibling chunk)

```sql
LOAD httpfs;
SELECT count(*) AS pairs,
       round(corr(i.median_hh_income, p.pct_bachelors_plus), 3) AS r_income_vs_degree,
       round(corr(i.median_hh_income, p.pct_people_of_color), 3) AS r_income_vs_poc
FROM 'BG_INCOME' i
JOIN '…/block-groups/bg-people/bg-people.parquet' p USING (geoid)
WHERE i.median_hh_income IS NOT NULL;
```

→ `223659 | 0.674 | -0.183`. The join is 1:1 on `geoid` and loses nothing: all
223,659 block groups with a published median matched. 8.7 s for two full-file
column scans.

### 4. The poorest block groups — and why the naive answer is wrong (`*_cv`)

```sql
LOAD httpfs;
SELECT geoid, median_hh_income::int AS income, median_hh_income_moe::int AS moe,
       round(median_hh_income_cv, 2) AS cv
FROM 'BG_INCOME'
WHERE median_hh_income IS NOT NULL ORDER BY median_hh_income LIMIT 5;
```

→ five rows all reading `2499 | NULL | NULL` (`240054906051`, `484410109005`,
`280119503001`, `051190027001`, `471570101203`). Bottom-coded, no margin, not
rankable. Now ask for reliable estimates only:

```sql
LOAD httpfs;
SELECT geoid, state, median_hh_income::int AS income, median_hh_income_moe::int AS moe,
       round(median_hh_income_cv, 2) AS cv
FROM 'BG_INCOME'
WHERE median_hh_income_cv < 0.12 ORDER BY median_hh_income LIMIT 5;
```

→ `121270820002 | FL | 3996 | 182 | 0.03`, `421010188022 | PA | 6250 | 830 |
0.08`, `120860007191 | FL | 9375 | 470 | 0.03`, `261635350001 | MI | 9583 |
1573 | 0.1`, `295101101002 | MO | 9583 | 1430 | 0.09`. 5.1 s.

How much of the file survives that filter:

```sql
LOAD httpfs;
SELECT CASE WHEN median_hh_income_cv IS NULL THEN 'no CV (top/bottom-coded)'
            WHEN median_hh_income_cv < 0.12 THEN 'reliable (<0.12)'
            WHEN median_hh_income_cv < 0.40 THEN 'caution (0.12-0.40)'
            ELSE 'unreliable (>0.40)' END AS band,
       count(*) AS n, round(100.0*count(*)/sum(count(*)) OVER (), 1) AS pct
FROM 'BG_INCOME' WHERE median_hh_income IS NOT NULL GROUP BY 1 ORDER BY 2 DESC;
```

→ `caution 147002 (65.7%)`, `reliable 47063 (21.0%)`, `unreliable 26136
(11.7%)`, `no CV 3458 (1.5%)`. One block group in five is reliable on its own.
Note the `IS NULL` arm: without it the coded rows fall into the `ELSE` and get
mislabelled "unreliable".

### 5. Lowest-income block groups within 3 km of a point (`bbox` + spatial)

```sql
LOAD spatial; LOAD httpfs;
SELECT geoid, median_hh_income::int AS income, round(median_hh_income_cv, 2) AS cv,
       round(ST_Distance(
         ST_Transform(geometry, 'EPSG:4326', 'EPSG:32616', always_xy := true),
         ST_Transform(ST_Point(-87.6298, 41.8781), 'EPSG:4326', 'EPSG:32616', always_xy := true))) AS metres
FROM 'BG_INCOME'
WHERE bbox.xmin < -87.59 AND bbox.xmax > -87.67      -- bbox of the 3 km disc:
  AND bbox.ymin < 41.906 AND bbox.ymax > 41.851      -- prunes row groups first
  AND ST_DWithin(
        ST_Transform(geometry, 'EPSG:4326', 'EPSG:32616', always_xy := true),
        ST_Transform(ST_Point(-87.6298, 41.8781), 'EPSG:4326', 'EPSG:32616', always_xy := true),
        3000)
  AND median_hh_income_cv < 0.40
ORDER BY median_hh_income LIMIT 5;
```

→ `170318429001 | 29363 | 0.39 | 2549`, `170312838001 | 46346 | 0.39 | 2146`,
`170313105001 | 63070 | 0.24 | 2969`, `170310811003 | 64750 | 0.39 | 2638`,
`170312832001 | 66404 | 0.18 | 2337`. 3.7 s against a 93 MB file; only 142 rows
survive the `bbox` predicate (measured), which is what makes the geometry
decode cheap. The `bbox` box must *contain* the disc, and the four comparisons
are an intersection test (`xmin < east AND xmax > west AND …`), not a
containment test — write it the other way round and you silently drop every
polygon that straddles the edge.

Two things that will otherwise bite:

- With `LOAD spatial`, `geometry` reads back as a `GEOMETRY`, so `ST_GeomFromWKB`
  is unnecessary and in fact errors. Without the extension it is a `BLOB`.
- **`ST_Distance_Spheroid` and `ST_DWithin_Spheroid` take `POINT(latitude,
  longitude)`** — the opposite of this catalog's `(lon, lat)` geometries, and
  they only accept points. Checked: Chicago→New York comes out 1147.2 km with
  `(lat, lon)` and 1521.3 km with `(lon, lat)`; the true distance is ~1145 km.
  The `ST_Transform` form above avoids the trap and measures to the polygon
  rather than its centroid.

Statistics come from the GeoParquet. The PMTiles archive has no `*_moe` or
`*_cv` columns and its coarse zooms are A5 cell aggregations, so no number
above can be reproduced from tiles.
