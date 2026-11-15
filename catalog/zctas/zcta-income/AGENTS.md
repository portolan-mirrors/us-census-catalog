# Agent guide — Income & Poverty (ZIP Code Tabulation Areas)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

**Read this before anything else: a ZCTA is not a ZIP code, and it nests in nothing.** A ZIP Code Tabulation Area is the Census Bureau's approximation of a USPS 5-digit delivery area, built by giving each 2020 census block the most common ZIP code of the addresses in it ([what a ZCTA is](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html)). Three consequences, all measured below:

- `state` is **NULL on all 33,791 rows**, so `WHERE state = 'CA'` returns nothing — silently, with no error.
- The first two characters of a `geoid` are a **postal region, not a state FIPS code**. `substr(geoid, 1, 2) = '06'` returns 289 rows and **not one of them is in California** — 288 intersect Connecticut and one, `06390`, is wholly in New York. A prefix join returns *wrong* rows rather than no rows.
- Relating a ZCTA to a county, tract or state is a **spatial** operation. Recipe 3 below does it properly, with a `bbox` covering-struct prefilter.

## What this is

Income, poverty and employment: median household income and per capita income ([B19013](https://data.census.gov/table/ACSDT5Y2024.B19013), [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301)), the share of people below the poverty line and below twice it ([C17002](https://data.census.gov/table/ACSDT5Y2024.C17002)), the share of households receiving SNAP ([B22010](https://data.census.gov/table/ACSDT5Y2024.B22010)), and the unemployment rate as a share of the civilian labor force ([B23025](https://data.census.gov/table/ACSDT5Y2024.B23025)), plus total population ([B01003](https://data.census.gov/table/ACSDT5Y2024.B01003)) and population density for context.

**33,791 rows**, one per ZIP Code Tabulation Area, ACS 2020–2024 5-year estimates, geometry from the 2020 cartographic boundary files — GENZ2020 is the only cartographic ZCTA edition the Census Bureau publishes, and the 2020-based ZCTAs are the ones the ACS tabulates.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.pmtiles`, layer `zcta-income`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/collection.json` — carries a full description for every column

This is a themed cut of the wide ZCTA table: the same 33,791 rows and the same geometry, 23 columns instead of 112. The wide sixth sibling is [`zctas/zctas`](../zctas/collection.json), whose own data files stay one directory up at `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zctas.parquet` (and `.pmtiles`). Use it when you want income beside housing, health and commuting in one download; use this file when income is the question.

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

`geoid` is the 5-digit ZCTA code and **joins nothing else in this catalog by prefix or by string**. It joins 1:1 to the five sibling ZCTA collections, and to nothing else: a ZCTA can cross county and state lines, so there is no prefix join to counties, tracts or states, and `substr(geoid, 1, 2)` is a postal region rather than a state FIPS code. `state` is NULL on every row for the same reason. To relate ZCTAs to states or counties, do it spatially (and expect a ZCTA to hit more than one), or use a Census relationship file.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 5-digit ZIP Code Tabulation Area code, e.g. `90210`. Not a ZIP code; does not nest in any other census geography. |
| `name` | string | `ZCTA5 ` + the code — "ZCTA5 90210". A ZCTA has no containing geography to name it by. |
| `state` | string | **Always NULL.** ZCTAs cross state lines, the ACS publishes them at the nation level only, and the 2020 cartographic boundary ZCTA file carries no state attribute. The column exists so the schema matches the catalog's other collections. |
| `population` | NULL on 0.06% of ZCTAs — the 19 rows with a 2020 cartographic boundary and no ACS tabulation (17 island-area ZCTAs plus 11717 and 11798 in Suffolk County, New York). Every other column is NULL on at least those rows. |
| `population_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `population`. |
| `aland_sqkm` | double | Land area in km² (water excluded), 3 decimals. |
| `pop_density` | double | People per square kilometre of land area, rounded to 1 decimal: `population / aland_sqkm`. |
| `median_hh_income` | NULL on 9.60% of ZCTAs — the Census Bureau suppresses a median when the sample behind it is too thin. |
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

- **`state` is NULL on every row** and `geoid` joins nothing by prefix. See the schema note above; this is the single most common way to get a wrong answer out of this collection.
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
- **A ZCTA's size varies enormously**: `aland_sqkm` runs from 0.004 to
  35,426.845 and `population` from 0 to 140,157, with a median of 2,656
  (measured). A rural ZCTA can be larger than a state's smallest county and an
  urban one a single city block, so `pop_density` is the only fair way to
  compare two of them, and an unweighted mean over ZCTAs is not a national
  average.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area, and neither number is wrong.
- **`pct_unemployed` divides by the civilian labor force** (B23025 line 3), not by the population 16 and over. That is what makes it an unemployment rate.
- **`median_hh_income` is top-coded upstream at $250,001.** That is a published
  value, not a jam code, and the richest ZCTAs sit on it — so a ranking at the
  very top of the distribution is a ranking of rounding.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.06% of ZCTAs — the 19 rows with a 2020 cartographic boundary and no ACS tabulation. Every other column is NULL on at least those rows. |
| `median_hh_income` | NULL on 9.60% of ZCTAs — the Census Bureau suppresses a median when the sample behind it is too thin. For comparison: 1.59% of tracts, 7.69% of block groups, 0.43% of counties. |
| `per_capita_income` | NULL on 3.26% of ZCTAs. |
| `pct_snap` | NULL on 2.88% of ZCTAs. |
| `pct_unemployed` | NULL on 2.91% of ZCTAs. |

Those 19 rows are 17 island-area ZCTAs — `00802`, `00820`, `00830`, `00840`, `00850`, `00851` (U.S. Virgin Islands), `96799` (American Samoa), `96910`, `96913`, `96915`, `96916`, `96917`, `96928`, `96929` (Guam), `96950`, `96951`, `96952` (Northern Mariana Islands) — plus `11717` and `11798` in Suffolk County, New York, measured by listing every row where `population IS NULL`. The island areas have 2020 cartographic boundaries but no ACS 5-year estimates; they keep their geometry and publish NULL values rather than being dropped.

**598 ZCTAs (1.77%) have an ACS row with `population` exactly 0** (measured). They are rows, not holes, and they will drag any unweighted average toward nothing — gate on `population` or weight by it.

Row count checked against the Census Bureau's own [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html): 33,791 ZCTAs (33,642 United States + 132 Puerto Rico + 17 island areas), which is exactly the row count here. The ACS tabulates 33,772 of them, and every one of those 33,772 matched a polygon.

Spot-checked against data.census.gov: 90210 median household income $187,801, 00601 (Adjuntas, Puerto Rico) $19,454, 60614 (Chicago) $136,448.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: z0–z5 are **counties**, carrying the Census Bureau's own county estimates under the same column names, and z6–z12 are the ZCTAs themselves. ZCTAs do not nest in counties, so the county band is national orientation, not a roll-up of these features. `*_moe` columns are not in the tiles at any zoom; `*_cv` columns are. Statistics come from the GeoParquet.

## Related collections

- [`zctas/zcta-people`](../zcta-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`zctas/zcta-housing`](../zcta-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`zctas/zcta-connectivity`](../zcta-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`zctas/zcta-wellbeing`](../zcta-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`zctas/zctas`](../zctas/collection.json) ([agent guide](../zctas/AGENTS.md)) — the wide sixth sibling: all 112 columns, same 33,791 rows, data files one directory up.
- The same theme where GEOIDs *do* nest: [`counties/county-income`](../../counties/county-income/collection.json), [`states/state-income`](../../states/state-income/collection.json), [`tracts/tract-income`](../../tracts/tract-income/collection.json), [`block-groups/bg-income`](../../block-groups/bg-income/collection.json), [`places/place-income`](../../places/place-income/collection.json), [`congressional-districts/cd-income`](../../congressional-districts/cd-income/collection.json).
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, the geography ZCTAs are built from. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted. The
file is 69,418,807 bytes over 33,791 rows.

### 1. Income for a list of ZIP codes

```sql
INSTALL httpfs; LOAD httpfs;
SELECT geoid, population, median_hh_income::int AS income,
       round(median_hh_income_cv, 2) AS cv, pct_below_poverty AS poverty
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet'
WHERE geoid IN ('90210', '10001', '60614', '00601', '99501', '20500')
ORDER BY income DESC NULLS LAST;
```

→ `90210 | 19004 | 187801 | 0.06 | 9.16`, `60614 | 70693 | 136448 | 0.03 |
8.44`, `10001 | 30511 | 129852 | 0.12 | 15.08`, `99501 | 16175 | 70891 | 0.06 |
13.53`, `00601 | 16669 | 19454 | 0.05 | 59.9`.

**Six ZIP codes in, five rows out.** `20500` — the White House — has no ZCTA,
because it is a point ZIP serving a single delivery address rather than an area
of census blocks. That shortfall is not missing data, and an `IN` list of *n*
ZIP codes returning fewer than *n* rows is the normal case for any list that
includes PO-box-only or point ZIPs. Say so when you report coverage.

Two more obligations come with this shape. Carry the `_cv`: `10001`'s 0.12 sits
exactly on the "use with caution" line while `60614`'s 0.03 is solid, and a
table that prints both incomes without that column invites a comparison the
data does not support. And say what the geography is — these are ZIP Code
*Tabulation Areas*, re-delineated once a decade from 2020 blocks, so a 2026
customer ZIP list is being matched to 2020 approximations of postal areas.

### 2. The two traps, measured

```sql
LOAD httpfs;
SELECT count(*)                                            AS zctas,
       count(state)                                        AS rows_with_state,
       count(*) FILTER (WHERE state = 'CA')                AS where_state_ca,
       count(*) FILTER (WHERE substr(geoid, 1, 2) = '06')  AS prefix_06
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet';
```

→ `33791 | 0 | 0 | 289`.

`count(state) = 0`: the column exists so the schema matches the catalog's other
collections, and it is NULL on all 33,791 rows. `WHERE state = 'CA'` returns
nothing — silently, with no error, which is worse than failing.

`06` is California's state FIPS code, and the prefix filter returns 289 rows.
Here is what they are:

```sql
LOAD httpfs;
SELECT geoid, median_hh_income::int AS income
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet'
WHERE substr(geoid, 1, 2) = '06' ORDER BY geoid LIMIT 5;
```

→ `06001 | 153664`, `06002 | 98162`, `06010 | 79314`, `06013 | 165120`,
`06016 | 120399`.

A spatial check on all 289 (recipe 3's shape, against
[`states`](../../states/states/collection.json)) puts **not one of them in
California**: 288 intersect **Connecticut** and one, `06390` — population 72,
Fishers Island — is wholly in **New York** (measured). `06001` alone is 100%
inside Connecticut, while `90210`, a real California ZIP, is 100% inside
California. The `06` prefix is the Connecticut postal region; California's ZIP
codes start with `9`. So a prefix join to
[`states`](../../states/states/collection.json) or
[`counties`](../../counties/counties/collection.json) returns 289 confidently
wrong rows rather than zero rows, which no downstream check will catch.

(The 289 also touch Massachusetts, New York and Rhode Island polygons 17, 15
and 11 times respectively — border slivers between two independently
generalized boundary files, which is why recipe 3 gates on an area share
rather than on bare `ST_Intersects`.)

### 3. One state's ZCTAs — spatially, because prefixes cannot

```sql
LOAD spatial; LOAD httpfs;
WITH s AS (
  SELECT geometry, bbox
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet'
  WHERE state = 'MS'),
cand AS (
  SELECT z.geoid,
         ST_Area(ST_Intersection(z.geometry, s.geometry)) / ST_Area(z.geometry) AS frac
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet' z, s
  WHERE z.bbox.xmin <= s.bbox.xmax AND z.bbox.xmax >= s.bbox.xmin
    AND z.bbox.ymin <= s.bbox.ymax AND z.bbox.ymax >= s.bbox.ymin
    AND ST_Intersects(z.geometry, s.geometry))
SELECT count(*)                            AS intersecting,
       count(*) FILTER (WHERE frac > 0.5)  AS majority_in_ms,
       count(*) FILTER (WHERE frac < 0.01) AS slivers
FROM cand;
```

→ `497 | 427 | 69`.

497 ZCTAs touch Mississippi; only 427 have more than half their area in it, and
69 have less than 1% — border artefacts of two independently generalized
boundary files. `ST_Intersects` alone is the wrong membership test: the
unfiltered version of this query ranks `38017` top in Mississippi, and `38017`
is 100.0% in Tennessee and 0.0% in Mississippi (measured with the same
`ST_Area(ST_Intersection(...))` expression). With the area-share gate:

```sql
LOAD spatial; LOAD httpfs;
WITH s AS (
  SELECT geometry, bbox
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/states.parquet'
  WHERE state = 'MS')
SELECT z.geoid, z.median_hh_income::int AS income,
       round(z.median_hh_income_cv, 2) AS cv, z.population
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet' z, s
WHERE z.bbox.xmin <= s.bbox.xmax AND z.bbox.xmax >= s.bbox.xmin
  AND z.bbox.ymin <= s.bbox.ymax AND z.bbox.ymax >= s.bbox.ymin
  AND ST_Area(ST_Intersection(z.geometry, s.geometry)) / ST_Area(z.geometry) > 0.5
  AND z.median_hh_income_cv < 0.15
ORDER BY z.median_hh_income DESC LIMIT 5;
```

→ `39110 | 125506 | 0.04 | 50443`, `38672 | 116184 | 0.05 | 16436`, `38654 |
103092 | 0.04 | 57898`, `39047 | 100347 | 0.03 | 40808`, `38651 | 98760 | 0.09
| 8731`.

Three things carry this recipe. The `bbox`-overlap condition is a cheap
candidate filter using the GeoParquet 1.1 covering struct and its row-group
statistics, so `ST_Intersection` runs on a few hundred polygons instead of
33,791 — write it as an *intersection* test (`z.xmin <= s.xmax AND z.xmax >=
s.xmin AND …`), because containment would drop every ZCTA that only partly
covers the state. The area-share gate decides membership. And the `_cv` gate
keeps the ranking out of the tiny-ZCTA noise. For a population-weighted
allocation rather than a membership list, use the Census Bureau's own
[ZCTA relationship files](https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html)
and say which one.

### 4. Which geography should this question be asked at? (`*_cv`, three files)

```sql
LOAD httpfs;
SELECT 'zcta' AS geography, count(median_hh_income_cv) AS n,
       round(quantile_cont(median_hh_income_cv, 0.5), 3) AS median_cv,
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40)
             / count(median_hh_income_cv), 1) AS pct_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet'
UNION ALL
SELECT 'tract', count(median_hh_income_cv),
       round(quantile_cont(median_hh_income_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40)
             / count(median_hh_income_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet'
UNION ALL
SELECT 'county', count(median_hh_income_cv),
       round(quantile_cont(median_hh_income_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40)
             / count(median_hh_income_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet';
```

→ `zcta | 30414 | 0.095 | 4.9`, `tract | 83266 | 0.125 | 1.5`, `county | 3221 |
0.042 | 0.1`.

Read both columns. The *median* ZCTA income estimate is more reliable than the
median tract estimate (0.095 against 0.125) — many ZCTAs are suburban and
large. But the ZCTA tail is three times fatter: 4.9% of ZCTA medians are over
the 0.40 "unreliable" line against 1.5% of tract medians, because the same file
also holds thousands of ZCTAs with a few hundred people. ZCTAs are not a
uniformly coarser geography than tracts; they are a far more *variable* one, so
gate on `_cv` (and on `population`) rather than trusting the level.

### 5. Is the difference between two ZCTAs real? (margins, not estimates)

```sql
LOAD httpfs;
SELECT geoid, median_hh_income::int AS income, median_hh_income_moe::int AS moe,
       (median_hh_income - median_hh_income_moe)::int AS lo,
       (median_hh_income + median_hh_income_moe)::int AS hi
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet'
WHERE geoid IN ('10001', '10003', '60614', '60615');
```

→ `60614 | 136448 | 7632 | 128816 | 144080`, `60615 | 63876 | 3720 | 60156 |
67596`, `10001 | 129852 | 25244 | 104608 | 155096`, `10003 | 154262 | 10754 |
143508 | 165016`.

Two pairs, two answers. `60614` and `60615` are $72,572 apart and their 90%
intervals — [128,816–144,080] and [60,156–67,596] — are nowhere near each
other, so that difference is real. `10001` and `10003` look $24,410 apart, but
[104,608–155,096] and [143,508–165,016] **overlap**, so that difference is not
established at all: `10001`'s margin is ±$25,244, a fifth of its own estimate.
Run this check before reporting any pair of ZCTAs. Subtracting two medians and
ignoring the margins is the most common way a ZIP-level comparison goes wrong,
and the medians themselves must never be summed or averaged — a region's median
is not derivable from its parts'.

### Related recipes elsewhere

- All 112 columns at once, including the top-coded ceiling on the richest
  ZCTAs: [`zctas/zctas/AGENTS.md`](../zctas/AGENTS.md).
- How many ZCTAs genuinely straddle a state line, and the cross-theme join:
  [the ZCTA group guide](../AGENTS.md).
- Income by race beside these overall medians, NULL-aware:
  [`zctas/zcta-wellbeing/AGENTS.md`](../zcta-wellbeing/AGENTS.md).
- The same theme where a GEOID prefix *is* a join key:
  [`counties/county-income/AGENTS.md`](../../counties/county-income/AGENTS.md),
  [`tracts/tract-income/AGENTS.md`](../../tracts/tract-income/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and its z0–z5 features are counties rather than ZCTAs, so nothing
above can be reproduced from tiles.
