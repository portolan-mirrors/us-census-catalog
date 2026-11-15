# Agent guide — People & Education (ZIP Code Tabulation Areas)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

**Read this before anything else: a ZCTA is not a ZIP code, and it nests in nothing.** A ZIP Code Tabulation Area is the Census Bureau's approximation of a USPS 5-digit delivery area, built by giving each 2020 census block the most common ZIP code of the addresses in it ([what a ZCTA is](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html)). Three consequences:

- `state` is **NULL on all 33,791 rows**, so `WHERE state = 'CA'` returns nothing — silently, with no error.
- The first two characters of a `geoid` are a **postal region, not a state FIPS code**: `substr(geoid, 1, 2) = '06'` returns 289 rows and **not one of them is in California** — 288 intersect Connecticut and one, `06390`, is wholly in New York (measured in [`zcta-income`](../zcta-income/AGENTS.md)). A prefix join returns *wrong* rows rather than no rows.
- Relating a ZCTA to a county, tract or state is a **spatial** operation. Recipes 2 and 4 below do it, with a `bbox` covering-struct prefilter.

## What this is

Who lives here: median age and the shares under 18 and 65 or over ([B01002](https://data.census.gov/table/ACSDT5Y2024.B01002), [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001)), the four mutually exclusive non-Hispanic race shares this catalog carries — White, Black or African American, American Indian and Alaska Native, Asian — plus Hispanic or Latino of any race and its complement, people of color ([B03002](https://data.census.gov/table/ACSDT5Y2024.B03002)), and the share of adults 25 and over holding a bachelor's degree or higher ([B15003](https://data.census.gov/table/ACSDT5Y2024.B15003)).

**33,791 rows**, one per ZIP Code Tabulation Area, ACS 2020–2024 5-year estimates, geometry from the 2020 cartographic boundary files — GENZ2020 is the only cartographic ZCTA edition the Census Bureau publishes, and the 2020-based ZCTAs are the ones the ACS tabulates.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/zcta-people.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/zcta-people.pmtiles`, layer `zcta-people`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/collection.json` — carries a full description for every column

This is a themed cut of the wide ZCTA table: the same 33,791 rows and the same geometry, 29 columns instead of 112. The wide sixth sibling is [`zctas/zctas`](../zctas/collection.json), whose own data files stay one directory up at `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zctas.parquet` (and `.pmtiles`).

## Source tables

| table | title | universe |
|---|---|---|
| [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001) | Sex by Age | Total population |
| [B01002](https://data.census.gov/table/ACSDT5Y2024.B01002) | Median Age by Sex | Total population |
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) | Hispanic or Latino Origin by Race | Total population |
| [B15003](https://data.census.gov/table/ACSDT5Y2024.B15003) | Educational Attainment for the Population 25 Years and Over | Population 25 years and over |

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

- **`state` is NULL on every row** and `geoid` joins nothing by prefix. See the schema note above; this is the single most common way to get a wrong answer out of this collection.
- **This collection has no `_cv` columns at all.** Every estimate carries its
  `<name>_moe`, at the 90% confidence level — the level the Census Bureau
  publishes — and reliability filtering here has to be done on the margin
  directly (`pct_bachelors_plus_moe < 5`, say) rather than on a coefficient of
  variation. The four other ZCTA themes do carry `_cv` columns.
- **The margins are actually there at this geography**, which is not true
  everywhere in the catalog: `population_moe` is populated on 33,759 of the
  33,791 rows and `pct_under_18_moe` / `pct_white_nh_moe` on 33,161, against
  **132 of 3,235 counties** and **0 of 56 states** for `population_moe`
  (measured). At county and state level `population` is a count to use; here it
  is an estimate you can and should put an interval on.
- To compare two geographies, check whether their margins overlap before
  calling a difference real. To sum estimates across geographies, add the
  margins in quadrature (`sqrt(sum(moe*moe))`). **Never sum or average a
  median**: a median of a region is not derivable from the medians of its
  parts, and `median_age` is a median.
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **The four race shares are all non-Hispanic**, drawn from B03002's "Not Hispanic or Latino" branch, so they and `pct_hispanic` are mutually exclusive and do not double-count.
- **`pct_people_of_color` is a complement** (`100 − pct_white_nh`) and carries `pct_white_nh`'s margin of error unchanged.
- **`pct_bachelors_plus` divides by the population 25 and over** (B15003's own universe), not by everyone, and associate's degrees are deliberately excluded.
- **A ZCTA's size varies enormously**: `aland_sqkm` runs from 0.004 to
  35,426.845 and `population` from 0 to 140,157, with a median of 2,656
  (measured). A rural ZCTA can be larger than a state's smallest county and an
  urban one a single city block, so `pop_density` is the only fair way to
  compare two of them, and an unweighted mean over ZCTAs is not a national
  average.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area, and neither number is wrong.
- **A share whose margin is 0.0 is a flag to inspect, not high precision.**
  66 ZCTAs publish `pct_hispanic_moe = 0.0` (measured), and a ZCTA can be
  almost entirely group quarters — a campus or a base — with a handful of
  households. `population` is not a household count.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.06% of ZCTAs — the 19 rows with a 2020 cartographic boundary and no ACS tabulation. Every other column is NULL on at least those rows. |
| `median_age` | NULL on 2.87% of ZCTAs — 971 rows, of which 598 are ZCTAs whose ACS population is exactly 0 (measured). |
| `pct_bachelors_plus` | NULL on 2.04% of ZCTAs: no population 25 and over, so no denominator. |

Those 19 rows are 17 island-area ZCTAs — `00802`, `00820`, `00830`, `00840`, `00850`, `00851` (U.S. Virgin Islands), `96799` (American Samoa), `96910`, `96913`, `96915`, `96916`, `96917`, `96928`, `96929` (Guam), `96950`, `96951`, `96952` (Northern Mariana Islands) — plus `11717` and `11798` in Suffolk County, New York, measured by listing every row where `population IS NULL`. The island areas have 2020 cartographic boundaries but no ACS 5-year estimates, so they keep their geometry and publish NULL values rather than being dropped.

**598 ZCTAs (1.77%) have an ACS row with `population` exactly 0**, and `median_age` is NULL on every one of them (measured). They are rows, not holes: they will drag an unweighted average toward nothing and they sort to the top or bottom of any ascending ranking.

Row count checked against the Census Bureau's own [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html): 33,791 ZCTAs (33,642 United States + 132 Puerto Rico + 17 island areas), which is exactly the row count here. The ACS tabulates 33,772 of them, and every one of those 33,772 matched a polygon.

Spot-checked against data.census.gov: Los Angeles city population 3,857,263 and New York city 8,483,844 at the [`places`](../../places/places/collection.json) level, which is the same B01003 estimate this column carries.

Margins of error at this geography can be large relative to the estimate, and this collection has no `_cv` column to lean on — read `<name>_moe` beside every value you report, and never compare two geographies without checking whether their margins overlap.

PMTiles coarse zooms are a different census geography from this collection's: z0–z5 are **counties**, carrying the Census Bureau's own county estimates under the same column names, and z6–z12 are the ZCTAs themselves. ZCTAs do not nest in counties, so the county band is national orientation, not a roll-up of these features. `*_moe` columns are not in the tiles at any zoom. Statistics come from the GeoParquet.

## Related collections

- [`zctas/zcta-income`](../zcta-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`zctas/zcta-housing`](../zcta-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`zctas/zcta-connectivity`](../zcta-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`zctas/zcta-wellbeing`](../zcta-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`zctas/zctas`](../zctas/collection.json) ([agent guide](../zctas/AGENTS.md)) — the wide sixth sibling: all 112 columns, same 33,791 rows, data files one directory up.
- The same theme where GEOIDs *do* nest: [`counties/county-people`](../../counties/county-people/collection.json), [`states/state-people`](../../states/state-people/collection.json), [`tracts/tract-people`](../../tracts/tract-people/collection.json), [`block-groups/bg-people`](../../block-groups/bg-people/collection.json), [`places/place-people`](../../places/place-people/collection.json), [`congressional-districts/cd-people`](../../congressional-districts/cd-people/collection.json).
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, the geography ZCTAs are built from. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted. The
file is 69,568,044 bytes over 33,791 rows.

### 1. A demographic profile for a list of ZIP codes

```sql
INSTALL httpfs; LOAD httpfs;
SELECT geoid, population, median_age, pct_under_18, pct_65_plus,
       pct_bachelors_plus AS degree, pct_hispanic
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/zcta-people.parquet'
WHERE geoid IN ('90210', '10001', '60614', '00601', '99501')
ORDER BY median_age DESC;
```

→ `90210 | 19004 | 51.9 | 15.24 | 30.94 | 68.05 | 5.99`, `00601 | 16669 | 45.3
| 17.43 | 22.96 | 18.19 | 99.31`, `99501 | 16175 | 38.2 | 16.01 | 17.29 | 39.37
| 12.05`, `10001 | 30511 | 35.8 | 10.97 | 13.41 | 72.63 | 16.95`, `60614 |
70693 | 31.1 | 14.11 | 9.43 | 87.21 | 7.47`.

This is the shape to use for a customer or patient ZIP list: an `IN` list on
`geoid`, no join, nothing clever. An `IN` list of *n* ZIP codes can return
fewer than *n* rows — PO-box-only and point ZIPs have no ZCTA at all — and that
shortfall is not missing data. Report it rather than silently dropping it.

### 2. Which ZCTA is this point in? (`bbox` prefilter, then the polygon)

```sql
LOAD spatial; LOAD httpfs;
SELECT geoid, name, population, median_age, pct_bachelors_plus
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/zcta-people.parquet'
WHERE bbox.xmin <= -122.3493 AND bbox.xmax >= -122.3493
  AND bbox.ymin <=   47.6205 AND bbox.ymax >=   47.6205
  AND ST_Within(ST_Point(-122.3493, 47.6205), geometry);
```

→ `98109 | ZCTA5 98109 | 34328 | 31.7 | 79.42`.

This is the correct way to turn a coordinate into a ZCTA, and the only
correct way to turn a ZCTA into any other census geography. The four `bbox`
comparisons are a GeoParquet 1.1 covering-struct filter: they carry row-group
statistics, so the reader skips most of the file before a single polygon is
decoded, and `ST_Within` then runs on a handful of candidates. Note that
`name` is just `ZCTA5 ` plus the code — a ZCTA has no containing geography to
be named after, which is the same fact as `state` being NULL.

### 3. The education distribution, and filtering on the margin instead of a CV

```sql
LOAD httpfs;
SELECT count(*) AS zctas, count(median_age) AS age_published,
       quantile_cont(median_age, 0.10) AS age_p10,
       quantile_cont(median_age, 0.50) AS age_p50,
       quantile_cont(median_age, 0.90) AS age_p90,
       max(median_age)                 AS age_max
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/zcta-people.parquet';
```

→ `33791 | 32820 | 32.8 | 42.1 | 56.4 | 93.3`.

Then the top of the education distribution, gated on the margin — this
collection has **no `_cv` columns**, so the margin is the only reliability
handle:

```sql
LOAD httpfs;
SELECT geoid, population, pct_bachelors_plus AS degree, pct_bachelors_plus_moe AS moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/zcta-people.parquet'
WHERE population > 10000 AND pct_bachelors_plus_moe < 5
ORDER BY pct_bachelors_plus DESC LIMIT 5;
```

→ `07078 | 14613 | 92.73 | 4.46`, `60654 | 25755 | 91.51 | 3.57`, `20008 |
29434 | 90.43 | 2.72`, `07310 | 16015 | 90.4 | 4.61`, `20037 | 13156 | 89.63 |
4.35`.

Both gates are load-bearing. Without `population > 10000` the top of this list
fills with ZCTAs of a few hundred people whose margins are tens of points wide;
without `pct_bachelors_plus_moe < 5` it fills with estimates that cannot be
distinguished from each other. And the `93.3` in the first query is the
inspection trigger for the next recipe.

### 4. The outlier at the top of a median — inspect, do not report

```sql
LOAD httpfs;
SELECT geoid, population, population_moe, median_age, median_age_moe, aland_sqkm
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/zcta-people.parquet'
ORDER BY median_age DESC LIMIT 5;
```

→ `11042 | 141 | 4.0 | 93.3 | 20.1 | 1.552`, `98558 | 61 | 4.0 | 91.7 | 25.1 |
0.168`, `17606 | 404 | 148.0 | 91.1 | 3.0 | 0.112`, `17943 | 42 | 51.0 | 89.4 |
22.4 | 0.345`, `77431 | 250 | 237.0 | 88.4 | 8.5 | 33.39`.

"The oldest ZIP code in America is 11042, median age 93.3" is the wrong
sentence. The ZCTA holds 141 people and the margin on that median is **±20.1
years** — the 90% interval runs from 73 to 113. `17606` has a population
estimate of 404 ± 148, and `77431` 250 ± 237. Every row at the top of a
ZCTA-level median ranking is a small-sample artefact, and with no `_cv` column
in this collection the margin is what tells you so. Gate on `population` and on
`<name>_moe` before ranking, and when a single ZCTA has to be reported, report
its interval.

### 5. Education against income (1:1 sibling join)

```sql
LOAD httpfs;
WITH j AS (
  SELECT ntile(5) OVER (ORDER BY i.median_hh_income) AS q,
         p.pct_bachelors_plus, p.median_age, p.pct_65_plus
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet' i
  JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/zcta-people.parquet' p
    USING (geoid)
  WHERE i.median_hh_income IS NOT NULL AND p.pct_bachelors_plus IS NOT NULL)
SELECT q AS income_quintile,
       round(avg(pct_bachelors_plus), 1) AS degree,
       round(avg(median_age), 1)         AS median_age,
       round(avg(pct_65_plus), 1)        AS age_65_plus
FROM j GROUP BY 1 ORDER BY 1;
```

→

```
1 | 16.4 | 43.7 | 22.9
2 | 20.6 | 43.3 | 21.9
3 | 24.5 | 42.9 | 21.1
4 | 30.2 | 42.9 | 20.3
5 | 47.8 | 43.2 | 19.4
```

The join is 1:1 on `geoid` — all six ZCTA collections hold the same 33,791
rows. The degree share nearly triples across the income distribution while
median age barely moves, which is the useful shape of this comparison: the
quintiles are quintiles *of ZCTAs*, not of people, so each row averages
thousands of areas of wildly different size. To say anything about people,
weight by `population`.

### Related recipes elsewhere

- All 112 columns at once, one row per ZCTA:
  [`zctas/zctas/AGENTS.md`](../zctas/AGENTS.md).
- The `geoid`-prefix trap measured, and the spatial state membership test:
  [`zctas/zcta-income/AGENTS.md`](../zcta-income/AGENTS.md).
- Group-quarters ZCTAs — campuses and bases with thousands of people and
  dozens of households: [`zctas/zcta-connectivity/AGENTS.md`](../zcta-connectivity/AGENTS.md).
- The same theme at a geography whose GEOIDs nest:
  [`tracts/tract-people/AGENTS.md`](../../tracts/tract-people/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and its z0–z5 features are counties rather than ZCTAs, so nothing
above can be reproduced from tiles.
