# Agent guide — Income & Poverty (Congressional Districts, 119th Congress)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections, and the [group guide](../AGENTS.md) covers what the six congressional-district collections share; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Income, poverty and employment: median household income and per capita income ([B19013](https://data.census.gov/table/ACSDT5Y2024.B19013), [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301)), the share of people below the poverty line and below twice it ([C17002](https://data.census.gov/table/ACSDT5Y2024.C17002)), the share of households receiving SNAP ([B22010](https://data.census.gov/table/ACSDT5Y2024.B22010)), and the unemployment rate as a share of the civilian labor force ([B23025](https://data.census.gov/table/ACSDT5Y2024.B23025)), plus total population ([B01003](https://data.census.gov/table/ACSDT5Y2024.B01003)) and population density for context.

**441 rows**, one per congressional district, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

**These are the districts of the 119th Congress**, the vintage this ACS release tabulates. Three independent confirmations, two of them re-measured for this file: the release's own summary-level prefix is `5001900US` (the `19`), the cartographic boundary file is `cb_2024_us_cd119_500k` and carries `CDSESSN = '119'` on all 441 features (counted: one group, 441 rows), and the Census Bureau's [ACS geography boundaries by year](https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year/2024.html) lists "Congressional District, Delegate District DC, Resident Commissioner District PR" with the vintage "119th Congress of the United States". **District numbers are not stable across congresses.** A `geoid` here is not the same ground as the same `geoid` in an earlier congress, these estimates must never be read as a time series, and a district-level table from another release must never be joined to this one on district number.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.pmtiles`, layer `cd-income`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/collection.json` — carries a full description for every column

This is a themed cut of the wide district table: the same 441 rows and the same geometry, with this theme's columns and class breaks measured on the district distribution. All 112 columns in one file are at `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.parquet` (that file's data stayed one directory up; its metadata is in [`congressional-districts/`](../congressional-districts/collection.json)). The cut is not a download saving — 99.5% of this file is `geometry`, 8,815,141 of 8,861,372 bytes of column data, measured with `parquet_metadata`; every file in this group is over 99% geometry — so choose by column set and styles, not by bytes, and note that a query that does not select `geometry` reads from the other 45 KB.

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

`geoid` is 4 characters — state FIPS (2) + district (2) — so `substr(geoid, 1, 2)` joins [`states`](../../states/states/collection.json) and the themed [`state-income`](../../states/state-income/collection.json). At-large states use district `00` (AK, DE, ND, SD, VT, WY) and the non-voting delegate districts use `98`: `1198` District of Columbia, `7298` Puerto Rico, `6098` American Samoa, `6698` Guam, `6998` Northern Mariana Islands, `7898` U.S. Virgin Islands. Nothing finer joins by prefix — district boundaries follow 2020 census blocks, not counties or tracts, so relating a district to the tracts or counties inside it is a spatial operation (worked example in the [wide table's guide](../congressional-districts/AGENTS.md)).

| column | type | what it is |
|---|---|---|
| `geoid` | string | 4-character congressional district GEOID: state FIPS 2 + district 2, e.g. `0612` for California's 12th. 119th Congress. |
| `name` | string | `NAMELSAD` from the 2024 cd119 cartographic boundary file plus the state name — "Congressional District 12, California", "Delegate District (at Large), District of Columbia". |
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

- **441 rows, not 435.** The 435 voting districts plus the District of Columbia delegate district (`1198`), Puerto Rico's Resident Commissioner district (`7298`) and the four island-area delegate districts (`6098`, `6698`, `6998`, `7898`), which carry geometry but no ACS estimates. Filter `state NOT IN ('DC','PR','AS','GU','MP','VI')` for the 435 voting districts, or `population IS NOT NULL` for the 437 rows with data. Recipe 1 below counts all three denominators.
- **Three ACS district rows have no polygon and so no row here**: `09ZZ`, `17ZZ` and `33ZZ`, the water-only pseudo-districts of Connecticut, Illinois and New Hampshire. The ACS release tabulates 440 district rows (counted in the downloaded B01003 summary file); 437 of them are here, those three are not, and the four island-area delegate districts are here with no ACS row — 437 + 4 = 441. Nothing is lost: the three ACS rows read `0|14`, `0|13` and `0|12`, population exactly 0.
- **Districts are equal-population by construction** — 546,488 to 1,021,191 across the 435 voting districts, 771,301 at the median (measured) — so every rate here has a far narrower spread than at any other geography, and the margins are the narrowest in the catalog. The median `median_hh_income_cv` is **0.010** and the worst is 0.021; a `WHERE median_hh_income_cv < 0.12` filter removes nothing. Class breaks measured at county or tract level collapse: recipe 3 shows the tract poverty breaks putting 290 of 437 districts in one class, which is why this collection ships its own.
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
- **A NULL margin can mean "controlled, no sampling error".** `population_moe` is NULL on 18 of the 441 rows: the four island-area districts with no data at all, plus 14 whose ACS margin is the jam value `-555555555`, which `tools/build_acs.py` documents as "controlled, no sampling error". Those 14 are the eight single-district jurisdictions (AK `0200`, DE `1000`, DC `1198`, ND `3800`, SD `4600`, VT `5000`, WY `5600`, PR `7298`) plus all four Iowa districts and both West Virginia districts; the ACS row for Alaska reads `5001900US0200|735706|-555555555`. Every other margin in this collection is published on all 437 rows with data. Read a missing margin as "not published", never as zero uncertainty.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area, and neither number is wrong — and the blocks are the 2020
  blocks these district lines were drawn from, which is a different thing
  again.
- **`pct_unemployed` divides by the civilian labor force** (B23025 line 3), not by the population 16 and over. That is what makes it an unemployment rate.
- **`pct_below_2x_poverty` and `pct_below_poverty` share C17002's universe** — the population for whom poverty status is determined, which excludes institutionalised people, people in military group quarters and unrelated children under 15 — so neither is a share of `population`.
- **`per_capita_income` divides aggregate income by total population**, children and people with no income included, so it is systematically far below `median_hh_income` and is not a household figure.

## Data quality

Columns with notable missingness at this geography (counted on this file, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.91% of districts (4 rows) — the four island-area delegate districts (American Samoa, Guam, the Northern Mariana Islands, the U.S. Virgin Islands), which have 2024 boundaries but no ACS 5-year estimates. |
| every other estimate and its `_moe`/`_cv` | NULL on exactly those same four rows (0.91%). There is no suppression anywhere else in this collection: `median_hh_income`, `per_capita_income`, `pct_below_poverty`, `pct_below_2x_poverty`, `pct_snap` and `pct_unemployed` each publish on all 437 districts with data. |
| `population_moe` | NULL on 4.08% of districts (18 rows): the four above plus the 14 "controlled, no sampling error" rows in the field notes. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 4 delegate districts.

The three water-only pseudo-districts the ACS tabulates — `09ZZ`, `17ZZ`, `33ZZ` — have no polygon in the cartographic boundary files and therefore no row here. Their population is exactly 0, so nothing is lost, but a pipeline that expects every ACS district GEOID to resolve to a polygon must handle them.

This is the most complete collection of its theme in the catalog. For comparison, `median_hh_income` is NULL on 0.43% of counties, 1.59% of tracts, 7.69% of block groups, 9.60% of ZCTAs and 12.71% of places; here it is NULL only on the four rows that have no data at all.

Margins of error are the narrowest in the catalog, which does not make them zero: recipe 4 shows 12 of the 25 adjacent pairs in New York's district income ranking overlapping at 90% confidence. Never compare two districts without checking whether their margins overlap, and never aggregate a median.

The PMTiles archive is real polygons at every zoom (band `0-10:geom`, from `tools/make_tiles.py`) — there are few enough districts to draw them all nationally, so there is no coarser-geography band at coarse zooms and one style classifies every zoom. `*_moe` columns are excluded from the tiles at every zoom; `*_cv` columns are kept. Statistics come from the GeoParquet, always.

## Related collections

- [`congressional-districts/cd-people`](../cd-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts/cd-housing`](../cd-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts/cd-connectivity`](../cd-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts/cd-wellbeing`](../cd-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts`](../congressional-districts/collection.json) — the sixth sibling: all 112 columns for the same 441 districts, in one table. Use it when a question crosses themes.
- The same theme at the other geographies: [`state-income`](../../states/state-income/collection.json) (56 rows, the level a district is compared against), [`county-income`](../../counties/county-income/collection.json), [`zcta-income`](../../zctas/zcta-income/collection.json), [`place-income`](../../places/place-income/collection.json), [`tract-income`](../../tracts/tract-income/collection.json) and [`bg-income`](../../block-groups/bg-income/collection.json). Only the state join is a prefix join; tracts and block groups relate to a district spatially.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, the geography these district lines were drawn from. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

For cost, the numbers that matter: 441 rows, 8,868,131 bytes on disk, of which
`geometry` is 8,815,141 and every other column together is 46,231. Filtering
is never a cost question in this collection; selecting `geometry` is.

### 1. Where does district median household income sit, and against what denominator?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*)                                                    AS districts,
       count(median_hh_income)                                     AS published,
       round(100.0*(count(*)-count(median_hh_income))/count(*), 2) AS pct_suppressed,
       quantile_cont(median_hh_income, 0.10)::int                  AS p10,
       quantile_cont(median_hh_income, 0.50)::int                  AS p50,
       quantile_cont(median_hh_income, 0.90)::int                  AS p90
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet';
```

→ `441 | 437 | 0.91 | 61139 | 78678 | 114005`.

437 of 441, and the four missing are the island-area delegate districts, not
suppression. Pick the denominator deliberately:

```sql
LOAD httpfs;
SELECT count(*)                                                             AS rows_in_file,
       count(*) FILTER (WHERE population IS NOT NULL)                       AS with_acs_data,
       count(*) FILTER (WHERE state NOT IN ('DC','PR','AS','GU','MP','VI')) AS voting_districts,
       count(*) FILTER (WHERE median_hh_income IS NULL)                     AS income_null
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet';
```

→ `441 | 437 | 435 | 4`.

Three honest denominators and they are not interchangeable. `441` is the
polygon count, `437` is what can be ranked, `435` is what votes. A `rank()`
over a `DESC` ordering without `WHERE population IS NOT NULL` puts the four
NULL rows first and shifts every rank by four.

### 2. One district against its own state, and the spread inside a state

`substr(geoid, 1, 2)` is the only prefix join a district has:

```sql
LOAD httpfs;
SELECT d.name, d.median_hh_income::int AS district_income,
       s.median_hh_income::int         AS state_income,
       (d.median_hh_income - s.median_hh_income)::int AS gap
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet' d
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-income/state-income.parquet' s
  ON substr(d.geoid, 1, 2) = s.geoid
WHERE d.state = 'NY'
ORDER BY gap DESC LIMIT 5;
```

→ `Congressional District 12, New York | 147775 | 85974 | 61801`,
`District 4 | 141082 | 85974 | 55108`, `District 3 | 139677 | 85974 | 53703`,
`District 1 | 134242 | 85974 | 48268`, `District 2 | 128330 | 85974 | 42356`.
NY-12's $147,775 matches the build's data.census.gov spot check.

Which state's districts disagree with each other most:

```sql
LOAD httpfs;
SELECT state, count(*) AS districts,
       min(median_hh_income)::int AS lowest, max(median_hh_income)::int AS highest,
       (max(median_hh_income) - min(median_hh_income))::int AS spread
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet'
WHERE median_hh_income IS NOT NULL
GROUP BY state HAVING count(*) >= 5
ORDER BY spread DESC LIMIT 5;
```

→

```
CA | 52 |  58828 | 182230 | 123402
VA | 11 |  58380 | 162359 | 103979
NY | 26 |  47075 | 147775 | 100700
MD |  8 |  63952 | 138349 |  74397
GA | 14 |  52535 | 126823 |  74288
```

Every one of those districts holds about 770,000 people, so the within-state
spread is not a population artefact: California's richest district has three
times the median income of its poorest. This is the shape to reach for at this
geography — a district against its state, and districts against each other
inside a state — because the national distribution is compressed by
construction.

### 3. Why this collection ships its own class breaks

The tract poverty style's breaks are `[5, 10, 20, 30, 40]`
(`tracts/tract-income/styles/poverty.json`); this collection's are
`[8, 10, 12, 15, 19]` (`styles/poverty.json`). Counting districts per class:

```sql
LOAD httpfs;
WITH d AS (
  SELECT pct_below_poverty AS v
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet'
  WHERE pct_below_poverty IS NOT NULL)
SELECT 'tract breaks 5/10/20/30/40' AS break_set,
       count(*) FILTER (WHERE v <  5)                AS c1,
       count(*) FILTER (WHERE v >=  5 AND v < 10)    AS c2,
       count(*) FILTER (WHERE v >= 10 AND v < 20)    AS c3,
       count(*) FILTER (WHERE v >= 20 AND v < 30)    AS c4,
       count(*) FILTER (WHERE v >= 30 AND v < 40)    AS c5,
       count(*) FILTER (WHERE v >= 40)               AS c6
FROM d
UNION ALL
SELECT 'district breaks 8/10/12/15/19',
       count(*) FILTER (WHERE v <  8),            count(*) FILTER (WHERE v >=  8 AND v < 10),
       count(*) FILTER (WHERE v >= 10 AND v < 12), count(*) FILTER (WHERE v >= 12 AND v < 15),
       count(*) FILTER (WHERE v >= 15 AND v < 19), count(*) FILTER (WHERE v >= 19)
FROM d;
```

→

```
tract breaks 5/10/20/30/40    |  2 | 119 | 290 | 25 |  0 |  1
district breaks 8/10/12/15/19 | 54 |  67 | 104 | 111 | 68 | 33
```

The tract breaks put **290 of 437 districts into one colour** and leave the
fifth class empty; the measured district breaks spread them 54/67/104/111/68/33.
The district poverty rate runs 4.83% to 40.53% with p10 7.39 / p50 11.89 /
p90 18.12 (measured), against 0–100 at tract level. Do the same before
borrowing any threshold — a "high poverty" cutoff calibrated on tracts labels
almost no district.

### 4. Is the ranking real? (margins, not estimates)

```sql
LOAD httpfs;
WITH r AS (
  SELECT name, median_hh_income AS v, median_hh_income_moe AS m,
         lead(name)                 OVER (ORDER BY median_hh_income DESC) AS next_name,
         lead(median_hh_income)     OVER (ORDER BY median_hh_income DESC) AS next_v,
         lead(median_hh_income_moe) OVER (ORDER BY median_hh_income DESC) AS next_m
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet'
  WHERE state = 'NY')
SELECT count(*)                                        AS adjacent_pairs,
       count(*) FILTER (WHERE v - m <= next_v + next_m) AS overlapping_pairs
FROM r WHERE next_v IS NOT NULL;
```

→ `25 | 12`.

Twelve of the twenty-five adjacent pairs in New York's district income ranking
have overlapping 90% intervals: NY-5 at $86,577 ± 1,168 and NY-20 at
$86,491 ± 1,157 are the same number as far as this survey can tell, and so are
NY-23 and NY-24 ($72,834 ± 891 against $72,690 ± 797). The narrowest margins
in the catalog still do not make a 26-row ranking an order. Report the
interval, or report the pairs that separate:

```sql
LOAD httpfs;
SELECT geoid, name, median_hh_income::int AS income, median_hh_income_moe::int AS moe,
       (median_hh_income - median_hh_income_moe)::int AS lo,
       (median_hh_income + median_hh_income_moe)::int AS hi
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet'
WHERE geoid IN ('3605', '3620', '3615')
ORDER BY income DESC;
```

→ `3605 | Congressional District 5, New York | 86577 | 1168 | 85409 | 87745`,
`3620 | Congressional District 20, New York | 86491 | 1157 | 85334 | 87648`,
`3615 | Congressional District 15, New York | 47075 | 1074 | 46001 | 48149`.

NY-5 and NY-20 overlap almost completely; NY-15 is a different district from
either beyond any doubt. And the GEOIDs are 4 characters, two of state FIPS and
two of district, zero-padded — `3605`, not `NY05` and not `365`.

### 5. Which geography should this question be asked at?

```sql
LOAD httpfs;
SELECT 'congressional district' AS geography,
       quantile_cont(median_hh_income, 0.10)::int AS p10,
       quantile_cont(median_hh_income, 0.50)::int AS p50,
       quantile_cont(median_hh_income, 0.90)::int AS p90,
       round(quantile_cont(median_hh_income, 0.90)
             / quantile_cont(median_hh_income, 0.10), 2) AS p90_over_p10,
       round(quantile_cont(median_hh_income_cv, 0.5), 3) AS median_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet'
UNION ALL
SELECT 'county', quantile_cont(median_hh_income, 0.10)::int,
       quantile_cont(median_hh_income, 0.50)::int, quantile_cont(median_hh_income, 0.90)::int,
       round(quantile_cont(median_hh_income, 0.90) / quantile_cont(median_hh_income, 0.10), 2),
       round(quantile_cont(median_hh_income_cv, 0.5), 3)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet'
UNION ALL
SELECT 'tract', quantile_cont(median_hh_income, 0.10)::int,
       quantile_cont(median_hh_income, 0.50)::int, quantile_cont(median_hh_income, 0.90)::int,
       round(quantile_cont(median_hh_income, 0.90) / quantile_cont(median_hh_income, 0.10), 2),
       round(quantile_cont(median_hh_income_cv, 0.5), 3)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet';
```

→

```
congressional district | 61139 | 78678 | 114005 | 1.86 | 0.01
county                 | 46875 | 65346 |  89168 | 1.9  | 0.042
tract                  | 42851 | 77004 | 140000 | 3.27 | 0.125
```

Districts are the most precise and the least differentiated: a p90/p10 ratio of
1.86 against 3.27 at tract level, with a median CV twelve times narrower. Ask
"how do the 435 districts compare on income" here; ask "where in this city is
income low" at tract level and accept the margins. And remember what the
compression is: ~770,000 people per district, averaging over neighbourhoods
that differ by a factor of three.

### Related recipes elsewhere

- All 112 columns on the same 441 districts, the national rank of one district,
  and the spatial recipe for what is inside it:
  [`congressional-districts`](../congressional-districts/AGENTS.md).
- Income by race beside these overall medians — published on 99% of districts
  against 38.57% of tracts: [`cd-wellbeing`](../cd-wellbeing/AGENTS.md).
- The state figures these districts are compared against, and the quadrature
  rule for summing: [`states/AGENTS.md`](../../states/AGENTS.md).
- The same theme inside a district, related spatially:
  [`tracts/tract-income/AGENTS.md`](../../tracts/tract-income/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive is real polygons at
every zoom (`0-10:geom`) and carries the `*_cv` columns, but no `*_moe`
columns — and it is a map artifact either way: query the GeoParquet for
numbers.
