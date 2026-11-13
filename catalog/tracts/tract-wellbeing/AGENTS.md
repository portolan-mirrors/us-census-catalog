# Agent guide — Health, Disability & Income by Race (Census Tracts)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Health coverage, disability, nativity and income by race — the tables the Census Bureau does not publish for block groups, which is why this chunk has no block-group twin. The uninsured share and the share with a disability ([B27001](https://data.census.gov/table/ACSDT5Y2024.B27001), [B18101](https://data.census.gov/table/ACSDT5Y2024.B18101)), the foreign-born share ([B05002](https://data.census.gov/table/ACSDT5Y2024.B05002)), the group-quarters population ([B26001](https://data.census.gov/table/ACSDT5Y2024.B26001)), median household income for Black, non-Hispanic White, Asian and Hispanic householders ([B19013B](https://data.census.gov/table/ACSDT5Y2024.B19013B), [B19013H](https://data.census.gov/table/ACSDT5Y2024.B19013H), [B19013D](https://data.census.gov/table/ACSDT5Y2024.B19013D), [B19013I](https://data.census.gov/table/ACSDT5Y2024.B19013I)), and the poverty rate of the Black alone population ([B17020B](https://data.census.gov/table/ACSDT5Y2024.B17020B)).

**85,184 rows**, one per census tract, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.pmtiles`, layer `tract-wellbeing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/collection.json` — carries a full description for every column

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
- **`pct_uninsured` and `pct_with_disability` are shares of the civilian noninstitutionalized population**, not of everyone: people on active duty and people in institutions are outside the universe.
- **The race-iteration medians are classified by the householder's race**, not by every member's, and each has its own universe (households with a householder who is …). They are not shares of a common total and cannot be averaged together.
- **`pct_below_poverty_black` has a race-specific denominator** (the Black alone population for whom poverty status is determined), so it is not comparable to `pct_below_poverty`'s denominator.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.16% of tracts: 126 island-area tracts plus 14 in Suffolk County, NY. |
| `pct_uninsured` | NULL on 0.94% of tracts. Not published for block groups at all. |
| `pct_with_disability` | NULL on 0.94% of tracts. Not published for block groups at all. |
| `group_quarters_pop` | NULL on 0.16% of tracts — the island-area and re-delineated geographies, not suppression. |
| `median_hh_income_black` | **NULL on 61.43% of tracts** (39.47% of counties): wherever too few Black-householder households live in the tract for the Census Bureau to publish a median. A map of this column is as much a map of where the group lives as of its income — read the NULLs as "not published here", never as a value. |
| `median_hh_income_white_nh` | NULL on 10.04% of tracts (2.38% of counties) — the least sparse of the four race-iteration medians, which is itself a fact about the distribution of the population. |
| `median_hh_income_asian` | **NULL on 71.27% of tracts** (53.63% of counties) — the sparsest column in the catalog. Present only where the Asian-householder sample supports a median. |
| `median_hh_income_hispanic` | **NULL on 44.43% of tracts** (19.60% of counties). |
| `pct_below_poverty_black` | NULL on 12.84% of tracts (measured): no Black-alone population for whom poverty status is determined, so no rate. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

Suffolk County, New York (36103) was re-delineated in the 2024 vintage: 39 block groups and 14 tracts exist in the 2024 cartographic boundary files with no matching row in the 2020-based ACS tabulation, and publish with NULL ACS values. These are the only non-territory rows in the catalog with geometry but no data.

443 ACS block groups and 338 ACS tracts (the `9900xx`-style water geographies) have no polygon in the cartographic boundary files and therefore no row here. All of them have population 0, so the dropped population is exactly 0 — this is why the tract collections hold 85,184 rows against 85,382 in the ACS release.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are A5 cell aggregations, not census geographies — counts summed, rates and medians averaged unweighted. Statistics come from the GeoParquet.

## Related collections

- [`tracts/tract-income`](../tract-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-people`](../tract-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-housing`](../tract-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`tracts/tract-connectivity`](../tract-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- No twin at block-groups for this theme: the Census Bureau does not publish these tables at that geography.
- [`counties`](../../counties/collection.json) and [`states`](../../states/collection.json) — every indicator in one wide table per geography.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run against the published URLs with DuckDB 1.4.1
immediately before it was written down, and its real output is quoted beside
it. In this collection the NULLs are the subject, not an inconvenience: four
of the columns are published on a minority of tracts, and a query that ignores
that produces a confident answer about where a population *lives* while
claiming to be about its income.

### 1. Where are the most people uninsured? (`*_cv`-gated top-N)

```sql
INSTALL httpfs; LOAD httpfs;
SELECT geoid, name, pct_uninsured, pct_uninsured_moe AS moe,
       round(pct_uninsured_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet'
WHERE population > 2000 AND pct_uninsured_cv < 0.12
ORDER BY pct_uninsured DESC LIMIT 5;
```

→ `18087970401 | Census Tract 9704.01, LaGrange County, Indiana | 77.5 | 2.77
| 0.02`, `18039000902 | Census Tract 9.02, Elkhart County, Indiana | 74.66 |
2.79 | 0.02`, `48201433004 | … Harris County, Texas | 71.54 | 9.7 | 0.08`,
`48113009610 | … Dallas County, Texas | 69.53 | 9.45 | 0.08`, `48113019013 | …
Dallas County, Texas | 69.09 | 7.0 | 0.06`. 5.7 s.

77.5% ± 2.77 is an extraordinarily tight margin for a tract-level share, which
is what makes the top two credible. Remember the universe: `pct_uninsured` is
a share of the **civilian noninstitutionalised** population, so active-duty
personnel and people in institutions are outside the denominator entirely.

### 2. How often is each race-iteration median published at all?

```sql
LOAD httpfs;
SELECT round(100.0*count(median_hh_income_white_nh)/count(*), 2) AS pct_published_white_nh,
       round(100.0*count(median_hh_income_black)/count(*), 2)    AS pct_published_black,
       round(100.0*count(median_hh_income_hispanic)/count(*), 2) AS pct_published_hispanic,
       round(100.0*count(median_hh_income_asian)/count(*), 2)    AS pct_published_asian
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet';
```

→ `89.96 | 38.57 | 55.57 | 28.73`. **4.2 s**, and it re-measures the
data-quality table above exactly.

Read this before mapping any of those four columns. A national map of
`median_hh_income_asian` is drawn on 28.73% of tracts, and the 71% of tracts
that are blank are overwhelmingly tracts where few Asian-householder
households live — so the map's *coverage* is a map of residential patterns,
and the map's *colour* is income only where the colour exists. "No data" is
never "low income" here.

### 3. Income by race against income overall, NULL-aware (sibling join)

```sql
LOAD httpfs;
SELECT w.geoid, i.median_hh_income::int                AS overall,
       w.median_hh_income_white_nh::int                AS white_nh,
       w.median_hh_income_black::int                   AS black,
       round(w.median_hh_income_black::double / w.median_hh_income_white_nh, 2) AS black_to_white
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet' w
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet' i
  USING (geoid)
WHERE substr(w.geoid, 1, 5) = '13121'            -- Fulton County, Georgia
  AND w.median_hh_income_black_cv    < 0.20
  AND w.median_hh_income_white_nh_cv < 0.20
ORDER BY black_to_white LIMIT 5;
```

→ `13121011437 | 105188 | 109405 | 15688 | 0.14`, `13121001501 | 105640 |
120583 | 18907 | 0.16`, `13121006601 | 47237 | 143382 | 23163 | 0.16`,
`13121008000 | 52837 | 184700 | 53317 | 0.29`, `13121007100 | 36635 | 115742 |
34615 | 0.3`. 8.1 s.

Both `_cv` gates are load-bearing: these race-iteration medians rest on small
samples and without the filter the ratio column fills with noise. The third
row is worth staring at — the tract's overall median ($47,237) sits *below*
both of the race-specific medians it contains, which is possible because the
three medians have three different universes (all households; non-Hispanic
White householders; Black householders) and a median is not a weighted
average of sub-medians.

Now the part the ranking hides:

```sql
LOAD httpfs;
SELECT count(*) AS tracts,
       count(median_hh_income_black)    AS black_published,
       count(median_hh_income_white_nh) AS white_published,
       count(*) FILTER (WHERE median_hh_income_black    IS NOT NULL
                          AND median_hh_income_white_nh IS NOT NULL) AS both
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet'
WHERE substr(geoid, 1, 5) = '13121';
```

→ `327 | 245 | 238 | 164`. 3.3 s. Fulton County has 327 tracts; only **164**
can be compared at all, and that is before the `_cv` gates. Quote the
denominator whenever you quote a gap: "in the 164 of 327 Fulton County tracts
where both medians are published" is a true sentence, "in Fulton County" is
not.

### 4. Disability and insurance together, reliability-gated

```sql
LOAD httpfs;
SELECT geoid, name, pct_with_disability, round(pct_with_disability_cv, 2) AS dis_cv,
       pct_uninsured, round(pct_uninsured_cv, 2) AS unins_cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet'
WHERE population > 2000
  AND pct_with_disability_cv < 0.10 AND pct_uninsured_cv < 0.20
ORDER BY pct_with_disability DESC LIMIT 5;
```

→ `04013071505 | Census Tract 715.05, Maricopa County, Arizona | 39.31 | 0.09
| 7.04 | 0.1`, `40019892801 | … Carter County, Oklahoma | 38.5 | 0.07 | 23.05
| 0.12`, `04015950705 | … Mohave County, Arizona | 35.84 | 0.1 | 12.21 | 0.2`,
`40135030201 | … Sequoyah County, Oklahoma | 35.29 | 0.1 | 11.89 | 0.18`,
`48113021000 | Census Tract 210, Dallas County, Texas | 35.23 | 0.08 | 27.99 |
0.17`. 9.8 s.

The two columns move independently: Maricopa 715.05 pairs a 39% disability
share with 7% uninsured, Carter County pairs 38.5% with 23%. Reading one as a
proxy for the other would be wrong in both directions. Note the two different
`_cv` thresholds — the columns have different precision, and forcing one
threshold on both drops rows for the wrong reason.

### Related recipes elsewhere

- Overall income and the margin-overlap test:
  [`tracts/tract-income/AGENTS.md`](../tract-income/AGENTS.md).
- The same race-iteration medians at county scale, where they are published far
  more often (Black-householder median NULL on 39.47% of counties against
  61.43% of tracts): [`counties/AGENTS.md`](../../counties/AGENTS.md).
- There is no block-group twin for this theme — the Census Bureau does not
  publish these tables below tract.

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe` or
`*_cv` columns and its coarse zooms are A5 cell aggregations, so nothing above
can be reproduced from tiles.
