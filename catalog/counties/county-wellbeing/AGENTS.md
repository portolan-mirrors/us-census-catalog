# Agent guide — Health, Disability & Income by Race (Counties)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Health coverage, disability, nativity and income by race — the tables the Census Bureau does not publish for block groups, which is why this chunk has no block-group twin. The uninsured share and the share with a disability ([B27001](https://data.census.gov/table/ACSDT5Y2024.B27001), [B18101](https://data.census.gov/table/ACSDT5Y2024.B18101)), the foreign-born share ([B05002](https://data.census.gov/table/ACSDT5Y2024.B05002)), the group-quarters population ([B26001](https://data.census.gov/table/ACSDT5Y2024.B26001)), median household income for Black, non-Hispanic White, Asian and Hispanic householders ([B19013B](https://data.census.gov/table/ACSDT5Y2024.B19013B), [B19013H](https://data.census.gov/table/ACSDT5Y2024.B19013H), [B19013D](https://data.census.gov/table/ACSDT5Y2024.B19013D), [B19013I](https://data.census.gov/table/ACSDT5Y2024.B19013I)), and the poverty rate of the Black alone population ([B17020B](https://data.census.gov/table/ACSDT5Y2024.B17020B)).

**3,235 rows**, one per county or county equivalent, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

**This is the geography where a race-and-income question becomes answerable.** The four race-iteration medians are published on 97.62% / 80.40% / 60.53% / 46.37% of counties (white_nh / hispanic / black / asian, measured) against 89.96% / 55.57% / 38.57% / 28.73% of tracts. The Black-householder median exists for 1,958 counties and the Asian-householder median for 1,500, where at tract level they cover a minority of rows. Step up to here before quoting a racial income gap, and step up again to [states](../../states/state-wellbeing/collection.json) if even these rates are too thin — all four are published for every one of the 52 state rows with ACS data.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.pmtiles`, layer `county-wellbeing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/collection.json` — carries a full description for every column

This is one themed cut of the county table. The same rows with all 112 columns — every theme at once, no join — are the sixth sibling in this group, [`counties/counties`](../counties/collection.json), whose data files sit one directory up at `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet` (and `.pmtiles`).

## Source tables

| table | title | universe |
|---|---|---|
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B05002](https://data.census.gov/table/ACSDT5Y2024.B05002) | Place of Birth by Nativity and Citizenship Status | Total population |
| [B17020B](https://data.census.gov/table/ACSDT5Y2024.B17020B) | Poverty Status in the Past 12 Months by Age (Black or African American Alone) | Black or African American alone population for whom poverty status is determined |
| [B18101](https://data.census.gov/table/ACSDT5Y2024.B18101) | Sex by Age by Disability Status | Civilian noninstitutionalized population |
| [B19013B](https://data.census.gov/table/ACSDT5Y2024.B19013B) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (Black or African American Alone Householder) | Households with a householder who is Black or African American alone |
| [B19013D](https://data.census.gov/table/ACSDT5Y2024.B19013D) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (Asian Alone Householder) | Households with a householder who is Asian alone |
| [B19013H](https://data.census.gov/table/ACSDT5Y2024.B19013H) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (White Alone, Not Hispanic or Latino Householder) | Households with a householder who is White alone, not Hispanic or Latino |
| [B19013I](https://data.census.gov/table/ACSDT5Y2024.B19013I) | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars) (Hispanic or Latino Householder) | Households with a householder who is Hispanic or Latino |
| [B26001](https://data.census.gov/table/ACSDT5Y2024.B26001) | Group Quarters Population | Population in group quarters |
| [B27001](https://data.census.gov/table/ACSDT5Y2024.B27001) | Health Insurance Coverage Status by Sex by Age | Civilian noninstitutionalized population |

## Schema

`geoid` is 5 characters and is the join key: `substr(geoid, 1, 2)` → state FIPS; tracts and block groups join back on their own first 5 characters.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 5-character county GEOID: state 2 + county 3. |
| `name` | string | Human-readable name, assembled from the boundary files' name parts (block group, tract, county, state as applicable). |
| `state` | string | Two-letter USPS state or territory code. |
| `population` | int64 | Total population. |
| `population_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `population`. |
| `aland_sqkm` | double | Land area in km² (water excluded), 3 decimals. |
| `pop_density` | double | People per square kilometre of land area, rounded to 1 decimal: `population / aland_sqkm`. |
| `pct_uninsured` | double | Percent of the civilian noninstitutionalized population with no health insurance coverage. |
| `pct_uninsured_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_uninsured`. |
| `pct_uninsured_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_uninsured`. |
| `pct_with_disability` | double | Percent of the civilian noninstitutionalized population with a disability, as the ACS's six-question sequence defines it (hearing, vision, cognitive, ambulatory, self-care, independent living). |
| `pct_with_disability_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_with_disability`. |
| `pct_with_disability_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_with_disability`. |
| `pct_foreign_born` | double | Percent of the population that is foreign-born — anyone not a U.S. citizen at birth, naturalized citizens included. |
| `pct_foreign_born_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_foreign_born`. |
| `group_quarters_pop` | int64 | Population living in group quarters — correctional facilities, nursing facilities, college and university housing, military quarters, group homes, shelters. |
| `group_quarters_pop_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `group_quarters_pop`. |
| `median_hh_income_black` | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is Black or African American alone. |
| `median_hh_income_black_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_black`. |
| `median_hh_income_black_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_black`. |
| `median_hh_income_white_nh` | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is White alone, not Hispanic or Latino. |
| `median_hh_income_white_nh_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_white_nh`. |
| `median_hh_income_white_nh_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_white_nh`. |
| `median_hh_income_asian` | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is Asian alone. |
| `median_hh_income_asian_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_asian`. |
| `median_hh_income_asian_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_asian`. |
| `median_hh_income_hispanic` | double | Median household income in the past 12 months (2024 inflation-adjusted dollars) for households whose householder is Hispanic or Latino, of any race. |
| `median_hh_income_hispanic_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_hh_income_hispanic`. |
| `median_hh_income_hispanic_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_hh_income_hispanic`. |
| `pct_below_poverty_black` | double | Percent of the Black or African American alone population below the poverty level. |
| `pct_below_poverty_black_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_below_poverty_black`. |
| `pct_below_poverty_black_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_below_poverty_black`. |
| `geometry` | binary | Boundary polygon, WKB, EPSG:4326 / OGC:CRS84. |
| `bbox` | struct<xmin, ymin, xmax, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, with row-group statistics. |

## Field notes

- **`population_moe` is NULL on 3,103 of the 3,235 rows** (measured — only 132
  small rural counties carry one), and **`pct_foreign_born_moe` is NULL on
  exactly the same 3,103 rows**. Measured: all 3,235 rows agree on the two
  patterns. `pct_foreign_born` is denominated on B05002 line 1, a
  total-population line, which is the group of columns that lose their margin
  at this geography (the age and race shares in
  [`county-people`](../county-people/collection.json) behave identically). The
  estimate itself is published on all 3,222 rows with ACS data; it is the
  interval that is unavailable.
- **Every other estimate has a `<name>_moe`**, at the 90% confidence level —
  the level the Census Bureau publishes. To compare two geographies, check
  whether their margins overlap before calling a difference real. To sum
  estimates across geographies, add the margins in quadrature
  (`sqrt(sum(moe*moe))`). **Never sum or average a median**: a median of a
  region is not derivable from the medians of its parts.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. In this chunk the gate earns its keep: the median
  `median_hh_income_asian_cv` is 0.167 and `pct_below_poverty_black_cv` 0.275,
  with 34.8% of the latter above 0.40 (measured, recipe 5).
- **The race-iteration medians are classified by the householder's race**, not
  by every member's, and each has its own universe (households with a
  householder who is …). They are not shares of a common total, cannot be
  averaged together, and are not sub-medians of `median_hh_income` in
  [`county-income`](../county-income/collection.json) — a county's overall
  median can sit below every race-specific median it contains, because three
  medians over three universes are not a weighted average.
- **A NULL race-iteration median means "not published here", never "low
  income".** Where the group has too few households in the county for a
  publishable median, the cell is blank. Quote the denominator whenever you
  quote a gap — recipe 3 measures it.
- **`pct_below_poverty_black` has a race-specific denominator** (the Black
  alone population for whom poverty status is determined), so it is not
  comparable to `pct_below_poverty`'s denominator over in `county-income`.
- **`pct_uninsured` and `pct_with_disability` are shares of the civilian
  noninstitutionalized population**, not of everyone: people on active duty and
  people in institutions are outside the universe. That matters here more than
  elsewhere, because `group_quarters_pop` in this same chunk counts some of the
  people the other two exclude.
- **`pct_with_disability` is the ACS's six-question definition** (hearing,
  vision, cognitive, ambulatory, self-care, independent living), not a
  programme eligibility or a clinical one.
- **`group_quarters_pop` is a count of people, not households**, and is a
  subset of `population`. A county with a prison or a large university can
  have a group-quarters population large enough to distort every
  household-denominated rate in the catalog — check it before reading a county
  as a residential population.
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
- **Connecticut's county equivalents are the 9 planning regions**
  (`09110`–`09190`, measured) in the 2024 vintage, not the 8 historical
  counties. A 2020-vintage block or tract GEOID's 5-character prefix does not
  match these rows.

## Data quality

Columns with notable missingness at this geography, measured over this file:

| column | missingness |
|---|---|
| `population` | NULL on 0.40% of counties (13 rows) — the island-area county equivalents (AS 5, GU 1, MP 4, VI 3, measured), which have cartographic boundaries but no ACS 5-year estimates. |
| `population_moe`, `pct_foreign_born_moe` | NULL on 95.92% of counties (3,103 of 3,235) — the same rows for both. |
| `pct_uninsured`, `pct_with_disability`, `pct_foreign_born`, `group_quarters_pop` | NULL on 0.40% (13 rows) — the island areas only, not suppression. |
| `median_hh_income_white_nh` | NULL on 2.38% of counties (77 rows), against 10.04% of tracts. |
| `median_hh_income_hispanic` | NULL on 19.60% of counties (634 rows), against 44.43% of tracts. |
| `median_hh_income_black` | **NULL on 39.47% of counties** (1,277 rows), against 61.43% of tracts. Its `_moe` and `_cv` cover 1,936 rows, 22 fewer than the estimate. |
| `median_hh_income_asian` | **NULL on 53.63% of counties** (1,735 rows), against 71.27% of tracts — the sparsest column in this chunk. Its `_moe` and `_cv` cover 1,458 rows. |
| `pct_below_poverty_black` | NULL on 5.87% of counties (190 rows): no Black-alone population for whom poverty status is determined, so no rate. Its `_cv` covers only 2,738 rows (15.36% NULL). |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

In this collection the NULLs are the subject, not an inconvenience. A national map of `median_hh_income_asian` is drawn on 46.37% of counties, and the counties that are blank are overwhelmingly counties where few Asian-householder households live — so the map's *coverage* is a map of residential patterns and the map's *colour* is income only where the colour exists. That is still roughly 1.6 times the tract-level coverage, which is the reason this question is asked here.

Margins of error at this geography are the narrowest in the catalog below state level, but in this chunk they are not uniformly narrow: the four race medians rest on race-specific samples, and the `_cv` columns are the only honest filter. Never compare two counties without checking whether their margins overlap, and never aggregate a median.

The PMTiles archive carries real county polygons at every zoom — the band is `0-10:geom`, there are few enough features to draw them all at a national zoom, so there is no coarser-geography band at coarse zooms the way the tract collections have one. `*_moe` columns are excluded from the tiles at every zoom; `*_cv` columns are kept, which is what lets a style grey out an unreliable race median rather than drawing it as if certain. Statistics come from the GeoParquet, always.

## Related collections

- [`counties/county-income`](../county-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1. The overall `median_hh_income` these race medians sit beside lives there.
- [`counties/county-people`](../county-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1. The race *shares* are there; the race *incomes* are here.
- [`counties/county-housing`](../county-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`counties/county-connectivity`](../county-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`counties/counties`](../counties/collection.json) — the sixth sibling: all 112 columns in one wide table, same 3,235 rows, data files one directory up. Use it instead of a join when a question crosses three or more themes.
- The same theme at the other geographies: [`states/state-wellbeing`](../../states/state-wellbeing/collection.json) (all four race medians complete for every row with data), [`tracts/tract-wellbeing`](../../tracts/tract-wellbeing/collection.json), [`zctas/zcta-wellbeing`](../../zctas/zcta-wellbeing/collection.json), [`places/place-wellbeing`](../../places/place-wellbeing/collection.json), [`congressional-districts/cd-wellbeing`](../../congressional-districts/cd-wellbeing/collection.json).
- **No twin at block groups** for this theme: the Census Bureau does not publish these tables at that geography. Tracts are the finest level these columns exist at.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error, and none of these subjects.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

For cost: this file is 12.4 MB over 3,235 rows, most of it geometry. Nothing
here needs a filter to be affordable. What does need care is the NULLs: four of
these columns are published on a minority or near-minority of rows, and a query
that ignores that produces a confident answer about where a population *lives*
while claiming to be about its income.

### 1. How often is each race-iteration median published, here and one level down?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT 'county' AS geography, count(*) AS rows,
       round(100.0*count(median_hh_income_white_nh)/count(*), 2) AS white_nh,
       round(100.0*count(median_hh_income_hispanic)/count(*), 2) AS hispanic,
       round(100.0*count(median_hh_income_black)/count(*), 2)    AS black,
       round(100.0*count(median_hh_income_asian)/count(*), 2)    AS asian
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet'
UNION ALL
SELECT 'tract', count(*),
       round(100.0*count(median_hh_income_white_nh)/count(*), 2),
       round(100.0*count(median_hh_income_hispanic)/count(*), 2),
       round(100.0*count(median_hh_income_black)/count(*), 2),
       round(100.0*count(median_hh_income_asian)/count(*), 2)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet';
```

→ `county | 3235 | 97.62 | 80.4 | 60.53 | 46.37`, `tract | 85184 | 89.96 |
55.57 | 38.57 | 28.73`.

Read this before mapping or quoting any of those four columns. The
Hispanic-householder median covers four counties in five against barely half of
tracts; the Asian-householder median covers nearly half of counties against
under three in ten tracts. That gap is the whole argument for answering a
race-and-income question at this geography — and it is also a reminder that
"46.37% of counties" is still not "the United States". Say which denominator
you are on.

### 2. Where are the most people uninsured? (`*_cv`-gated top-N)

```sql
LOAD httpfs;
SELECT geoid, name, pct_uninsured, pct_uninsured_moe AS moe, round(pct_uninsured_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet'
WHERE population > 50000 AND pct_uninsured_cv < 0.12
ORDER BY pct_uninsured DESC LIMIT 5;
```

→ `48427 | Starr County, Texas | 28.9 | 1.6 | 0.03`, `48215 | Hidalgo County,
Texas | 28.25 | 0.5 | 0.01`, `48479 | Webb County, Texas | 27.33 | 0.84 |
0.02`, `48291 | Liberty County, Texas | 26.16 | 1.71 | 0.04`, `48061 | Cameron
County, Texas | 25.82 | 0.63 | 0.02`.

Five Texas counties, four of them on the Rio Grande. The margins are tight
enough that ranks one and two overlap — Starr's [27.30–30.50] against Hidalgo's
[27.75–28.75] — so call them a pair rather than first and second. Remember the
universe: `pct_uninsured` is a share of the **civilian noninstitutionalised**
population, so active-duty personnel and people in institutions are outside the
denominator entirely.

### 3. Income by race against income overall, NULL-aware (sibling join)

```sql
LOAD httpfs;
SELECT w.geoid, w.name, i.median_hh_income::int        AS overall,
       w.median_hh_income_white_nh::int                AS white_nh,
       w.median_hh_income_black::int                   AS black,
       round(w.median_hh_income_black / w.median_hh_income_white_nh, 2) AS black_to_white
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet' w
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet' i
  USING (geoid)
WHERE w.state = 'MI'
  AND w.median_hh_income_black_cv    < 0.20
  AND w.median_hh_income_white_nh_cv < 0.20
ORDER BY black_to_white LIMIT 5;
```

→ `26157 | Tuscola County, Michigan | 63811 | 64167 | 22692 | 0.35`, `26115 |
Monroe County, Michigan | 77335 | 78417 | 28298 | 0.36`, `26021 | Berrien
County, Michigan | 65425 | 71839 | 33213 | 0.46`, `26121 | Muskegon County,
Michigan | 65024 | 70345 | 34353 | 0.49`, `26075 | Jackson County, Michigan |
66073 | 69646 | 35190 | 0.51`.

The join is 1:1 on `geoid` — all six county collections hold the same 3,235
rows. Both `_cv` gates are load-bearing: these race-iteration medians rest on
race-specific samples, and without the filter the ratio column fills with
noise. Note that the overall median sits between the two race medians in every
row here, which it need not — three medians over three universes (all
households; non-Hispanic White householders; Black householders) are not a
weighted average of each other.

Now the part the ranking hides:

```sql
LOAD httpfs;
SELECT count(*) AS counties, count(median_hh_income_black) AS black_published,
       count(median_hh_income_white_nh)                    AS white_published,
       count(*) FILTER (WHERE median_hh_income_black    IS NOT NULL
                          AND median_hh_income_white_nh IS NOT NULL) AS both,
       count(*) FILTER (WHERE median_hh_income_black_cv    < 0.20
                          AND median_hh_income_white_nh_cv < 0.20)   AS both_reliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet';
```

→ `3235 | 1958 | 3158 | 1910 | 1193`.

Of 3,235 counties, **1,910** publish both medians and **1,193** publish both at
a CV under 0.20. "In the 1,193 counties where both medians are published
reliably" is a true sentence; "in the United States" is not. Quote the
denominator whenever you quote a gap. (At tract level the equivalent of that
first number is far smaller — see the Fulton County worked example in
[`tracts/tract-wellbeing`](../../tracts/tract-wellbeing/AGENTS.md).)

### 4. Disability and insurance together, reliability-gated

```sql
LOAD httpfs;
SELECT geoid, name, pct_with_disability, round(pct_with_disability_cv, 2) AS dis_cv,
       pct_uninsured, round(pct_uninsured_cv, 2) AS unins_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet'
WHERE population > 50000
  AND pct_with_disability_cv < 0.06 AND pct_uninsured_cv < 0.20
ORDER BY pct_with_disability DESC LIMIT 5;
```

→ `72137 | Toa Baja Municipio, Puerto Rico | 30.49 | 0.03 | 6.4 | 0.07`, `21195
| Pike County, Kentucky | 29.75 | 0.03 | 4.09 | 0.11`, `72113 | Ponce
Municipio, Puerto Rico | 26.42 | 0.02 | 4.48 | 0.07`, `32023 | Nye County,
Nevada | 25.77 | 0.04 | 8.81 | 0.08`, `72005 | Aguadilla Municipio, Puerto Rico
| 25.06 | 0.04 | 4.57 | 0.11`.

The two columns move independently: every county in this list pairs a high
disability share with a *low* uninsured share, the opposite of the pairing the
Texas border counties in recipe 2 show. Reading one as a proxy for the other
would be wrong in both directions. Note the two different `_cv` thresholds —
the columns have different precision, and forcing one threshold on both drops
rows for the wrong reason.

### 5. How reliable are the race-specific columns? (run before ranking any of them)

```sql
LOAD httpfs;
SELECT 'median_hh_income_white_nh' AS col, count(median_hh_income_white_nh_cv) AS n,
       round(quantile_cont(median_hh_income_white_nh_cv, 0.5), 3) AS median_cv,
       round(100.0*count(*) FILTER (WHERE median_hh_income_white_nh_cv > 0.40)
             / count(median_hh_income_white_nh_cv), 1) AS pct_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet'
UNION ALL SELECT 'median_hh_income_hispanic', count(median_hh_income_hispanic_cv),
       round(quantile_cont(median_hh_income_hispanic_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE median_hh_income_hispanic_cv > 0.40)
             / count(median_hh_income_hispanic_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet'
UNION ALL SELECT 'median_hh_income_black', count(median_hh_income_black_cv),
       round(quantile_cont(median_hh_income_black_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE median_hh_income_black_cv > 0.40)
             / count(median_hh_income_black_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet'
UNION ALL SELECT 'median_hh_income_asian', count(median_hh_income_asian_cv),
       round(quantile_cont(median_hh_income_asian_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE median_hh_income_asian_cv > 0.40)
             / count(median_hh_income_asian_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet'
UNION ALL SELECT 'pct_below_poverty_black', count(pct_below_poverty_black_cv),
       round(quantile_cont(pct_below_poverty_black_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE pct_below_poverty_black_cv > 0.40)
             / count(pct_below_poverty_black_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet';
```

→

```
median_hh_income_white_nh | 3158 | 0.045 |  0.5
median_hh_income_hispanic | 2591 | 0.146 | 10.8
median_hh_income_black    | 1936 | 0.141 | 12.6
median_hh_income_asian    | 1458 | 0.167 | 15.4
pct_below_poverty_black   | 2738 | 0.275 | 34.8
```

Two effects compound down this table. Coverage falls — 3,158 rows for the
non-Hispanic White median, 1,458 for the Asian one — and the surviving rows get
noisier, from a median CV of 0.045 to 0.167. `pct_below_poverty_black` is the
loosest column in the chunk: a third of the counties that publish a CV for it
are over 0.40. For comparison, the overall `median_hh_income_cv` over in
[`county-income`](../county-income/collection.json) has a median of 0.042 with
0.1% of rows unreliable. Any ranking on a race-specific column needs the `_cv`
gate; a ranking on the overall median barely does.

### Related recipes elsewhere

- The whole county table at once: [`counties/counties/AGENTS.md`](../counties/AGENTS.md).
- The same columns at tract level, where they are much sparser, with the
  Fulton County worked example of quoting a denominator:
  [`tracts/tract-wellbeing/AGENTS.md`](../../tracts/tract-wellbeing/AGENTS.md).
- The overall income median and the margin-overlap test on a national ranking:
  [`counties/county-income/AGENTS.md`](../county-income/AGENTS.md).
- The race *shares* that go with these race incomes:
  [`counties/county-people/AGENTS.md`](../county-people/AGENTS.md).
- Choosing between the six county collections, and stepping up or down a
  geography: [`counties/AGENTS.md`](../AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, so no test above that reads a margin of error can be reproduced from
tiles — even though, unlike the finer collections, every zoom of this archive
holds real county polygons.
