# Agent guide — Income & Poverty (Census Tracts)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Income, poverty and employment: median household income and per capita income ([B19013](https://data.census.gov/table/ACSDT5Y2024.B19013), [B19301](https://data.census.gov/table/ACSDT5Y2024.B19301)), the share of people below the poverty line and below twice it ([C17002](https://data.census.gov/table/ACSDT5Y2024.C17002)), the share of households receiving SNAP ([B22010](https://data.census.gov/table/ACSDT5Y2024.B22010)), and the unemployment rate as a share of the civilian labor force ([B23025](https://data.census.gov/table/ACSDT5Y2024.B23025)), plus total population ([B01003](https://data.census.gov/table/ACSDT5Y2024.B01003)) and population density for context.

**85,184 rows**, one per census tract, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.pmtiles`, layer `tract-income`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/collection.json` — carries a full description for every column

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
| `population` | NULL on 0.16% of tracts: 126 island-area tracts plus 14 in Suffolk County, NY. |
| `median_hh_income` | NULL on 1.59% of tracts (7.69% of block groups, for comparison). |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

Suffolk County, New York (36103) was re-delineated in the 2024 vintage: 39 block groups and 14 tracts exist in the 2024 cartographic boundary files with no matching row in the 2020-based ACS tabulation, and publish with NULL ACS values. These are the only non-territory rows in the catalog with geometry but no data.

443 ACS block groups and 338 ACS tracts (the `9900xx`-style water geographies) have no polygon in the cartographic boundary files and therefore no row here. All of them have population 0, so the dropped population is exactly 0 — this is why the tract collections hold 85,184 rows against 85,382 in the ACS release.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are A5 cell aggregations, not census geographies — counts summed, rates and medians averaged unweighted. Statistics come from the GeoParquet.

## Related collections

- [`tracts/tract-people`](../tract-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-housing`](../tract-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-connectivity`](../tract-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-wellbeing`](../tract-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`block-groups/bg-income`](../../block-groups/bg-income/collection.json) — the same theme one geography down, with wider margins of error.
- [`counties`](../../counties/collection.json) and [`states`](../../states/collection.json) — every indicator in one wide table per geography.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run against the published URLs with DuckDB 1.4.1
immediately before it was written down, and its real output is quoted beside
it.

### 1. Where does tract median household income sit, nationally?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*)                                                    AS tracts,
       count(median_hh_income)                                     AS published,
       round(100.0*(count(*)-count(median_hh_income))/count(*), 2) AS pct_suppressed,
       quantile_cont(median_hh_income, 0.10)::int                  AS p10,
       quantile_cont(median_hh_income, 0.50)::int                  AS p50,
       quantile_cont(median_hh_income, 0.90)::int                  AS p90
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet';
```

→ `85184 | 83828 | 1.59 | 42851 | 77004 | 140000`, in **2.3 s**. 1.59%
suppressed against 7.69% at block-group level: the reason to work here.

One state is the same query with `WHERE state = 'XX'`:

```sql
LOAD httpfs;
SELECT geoid, name, median_hh_income::int AS income, round(median_hh_income_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet'
WHERE state = 'MS' AND median_hh_income_cv < 0.15
ORDER BY median_hh_income DESC LIMIT 5;
```

→ `28089030301 | Census Tract 303.01, Madison County, Mississippi | 155357 |
0.08`, `28033070722 | … DeSoto County … | 154518 | 0.04`, `28033070631 | …
DeSoto County … | 148081 | 0.03`, `28089030204 | … Madison County … | 134943 |
0.09`, `28033070634 | … DeSoto County … | 131007 | 0.14`. 6.5 s. Note the
`name` column already carries county and state, so a state's top tracts need
no join to be readable.

### 2. Which geography should this question be asked at? (`*_cv`, two files)

```sql
LOAD httpfs;
SELECT 'tract' AS geography, count(median_hh_income_cv) AS n,
       round(quantile_cont(median_hh_income_cv, 0.5), 3) AS median_cv,
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40)
             / count(median_hh_income_cv), 1) AS pct_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet'
UNION ALL
SELECT 'block group', count(median_hh_income_cv),
       round(quantile_cont(median_hh_income_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE median_hh_income_cv > 0.40)
             / count(median_hh_income_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.parquet';
```

→ `tract | 83266 | 0.125 | 1.5`, `block group | 220201 | 0.202 | 11.8`. 4.1 s
for both files.

The median tract CV is 0.125, right on the "use with caution" line; the median
block group is 0.202, and one block group in eight is outright unreliable
against one tract in 67. Run this before deciding which geography a question
belongs at — and if a block-group answer must be mapped, grey out by `_cv`
rather than pretending the holes are not there.

### 3. One county's tracts, cheapest to most expensive housing (sibling join)

```sql
LOAD httpfs;
SELECT i.geoid, i.median_hh_income::int AS income, h.median_home_value::int AS home_value,
       round(h.median_home_value / i.median_hh_income, 1) AS value_to_income
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet' i
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet' h
  USING (geoid)
WHERE substr(i.geoid, 1, 5) = '48201'          -- Harris County, Texas
  AND i.median_hh_income_cv < 0.15 AND h.median_home_value_cv < 0.15
ORDER BY value_to_income DESC LIMIT 5;
```

→ `48201521000 | 47985 | 610400 | 12.7`, `48201530701 | 20516 | 225000 |
11.0`, `48201430700 | 88870 | 972900 | 10.9`, `48201411002 | 101875 | 1067400
| 10.5`, `48201430200 | 82434 | 821800 | 10.0`. 9.6 s.

The join is 1:1 on `geoid` — all five tract chunks hold the same 85,184 rows.
`value_to_income` is a ratio of two medians from two different universes
(owner-occupied units vs all households); it is a useful screening index and
not a household-level statistic. Both `_cv` gates matter: without them this
ranking fills with tracts whose home-value median is ±50%.

### 4. Is the difference between two tracts real? (margins, not estimates)

```sql
LOAD httpfs;
SELECT geoid, median_hh_income::int AS income, median_hh_income_moe::int AS moe,
       (median_hh_income - median_hh_income_moe)::int AS lo,
       (median_hh_income + median_hh_income_moe)::int AS hi
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet'
WHERE geoid IN ('48201521000', '48201430200');
```

→ `48201430200 | 82434 | 16096 | 66338 | 98530`, `48201521000 | 47985 | 5337 |
42648 | 53322`. 5.0 s.

The two 90% intervals, [42,648–53,322] and [66,338–98,530], do not overlap,
so these two Harris County tracts really do differ in income. Run the same
check before reporting any pair: at tract level the margins are narrow enough
that many comparisons survive, and wide enough that plenty do not. Never do
this by subtracting medians and ignoring the margins, and never sum or average
the medians themselves — a region's median is not derivable from its parts'.

### Related recipes elsewhere

- Income inequality inside a county at the finest geography available, and the
  top/bottom-coded values that carry no margin:
  [`block-groups/bg-income/AGENTS.md`](../../block-groups/bg-income/AGENTS.md).
- Income by race alongside these overall medians, NULL-aware:
  [`tracts/tract-wellbeing/AGENTS.md`](../tract-wellbeing/AGENTS.md).
- Top counties by income, and the poorest tracts inside the richest county:
  [`catalog/AGENTS.md`](../../AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe` or
`*_cv` columns and its coarse zooms are A5 cell aggregations that average
medians unweighted, so nothing above can be reproduced from tiles.
