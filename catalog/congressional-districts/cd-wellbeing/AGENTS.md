# Agent guide — Health, Disability & Income by Race (Congressional Districts, 119th Congress)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections, and the [group guide](../AGENTS.md) covers what the six congressional-district collections share; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Health coverage, disability, nativity and income by race — the tables the Census Bureau does not publish for block groups, which is why this chunk has no block-group twin. The uninsured share and the share with a disability ([B27001](https://data.census.gov/table/ACSDT5Y2024.B27001), [B18101](https://data.census.gov/table/ACSDT5Y2024.B18101)), the foreign-born share ([B05002](https://data.census.gov/table/ACSDT5Y2024.B05002)), the group-quarters population ([B26001](https://data.census.gov/table/ACSDT5Y2024.B26001)), median household income for Black, non-Hispanic White, Asian and Hispanic householders ([B19013B](https://data.census.gov/table/ACSDT5Y2024.B19013B), [B19013H](https://data.census.gov/table/ACSDT5Y2024.B19013H), [B19013D](https://data.census.gov/table/ACSDT5Y2024.B19013D), [B19013I](https://data.census.gov/table/ACSDT5Y2024.B19013I)), and the poverty rate of the Black alone population ([B17020B](https://data.census.gov/table/ACSDT5Y2024.B17020B)).

**441 rows**, one per congressional district, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

**These are the districts of the 119th Congress**, the vintage this ACS release tabulates. Three independent confirmations, two of them re-measured for this file: the release's own summary-level prefix is `5001900US` (the `19`), the cartographic boundary file is `cb_2024_us_cd119_500k` and carries `CDSESSN = '119'` on all 441 features (counted: one group, 441 rows), and the Census Bureau's [ACS geography boundaries by year](https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year/2024.html) lists "Congressional District, Delegate District DC, Resident Commissioner District PR" with the vintage "119th Congress of the United States". **District numbers are not stable across congresses.** A `geoid` here is not the same ground as the same `geoid` in an earlier congress — and because these columns describe populations that redistricting moves deliberately, comparing a district's racial income gap or uninsured rate to the same-numbered district in an earlier congress is comparing two different sets of people. These estimates must never be read as a time series.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.pmtiles`, layer `cd-wellbeing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/collection.json` — carries a full description for every column

This is a themed cut of the wide district table: the same 441 rows and the same geometry, with this theme's columns and class breaks measured on the district distribution. All 112 columns in one file are at `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.parquet` (that file's data stayed one directory up; its metadata is in [`congressional-districts/`](../congressional-districts/collection.json)). The cut is not a download saving — over 99% of each of these files is `geometry` (99.29–99.48%, measured with `parquet_metadata`) — so choose by column set and styles, not by bytes.

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

`geoid` is 4 characters — state FIPS (2) + district (2) — so `substr(geoid, 1, 2)` joins [`states`](../../states/states/collection.json) and the themed [`state-wellbeing`](../../states/state-wellbeing/collection.json). At-large states use district `00` (AK, DE, ND, SD, VT, WY) and the non-voting delegate districts use `98`: `1198` District of Columbia, `7298` Puerto Rico, `6098` American Samoa, `6698` Guam, `6998` Northern Mariana Islands, `7898` U.S. Virgin Islands. Nothing finer joins by prefix — district boundaries follow 2020 census blocks, not counties or tracts, so relating a district to the tracts or counties inside it is a spatial operation (worked example in the [wide table's guide](../congressional-districts/AGENTS.md)).

| column | type | what it is |
|---|---|---|
| `geoid` | string | 4-character congressional district GEOID: state FIPS 2 + district 2, e.g. `0612` for California's 12th. 119th Congress. |
| `name` | string | `NAMELSAD` from the 2024 cd119 cartographic boundary file plus the state name — "Congressional District 12, California", "Delegate District (at Large), District of Columbia". |
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

- **At this geography the NULLs are not the subject — and that is the headline.** The four race-iteration medians are published on **99.09 / 99.09 / 99.09 / 98.87 percent** of districts (white_nh / black / hispanic / asian, measured), against 89.96 / 38.57 / 55.57 / 28.73 percent of tracts. `median_hh_income_black` is NULL on 0.91% of districts against 39.47% of counties and 61.43% of tracts. An equity question that cannot be asked at tract level because the column is blank can almost always be asked here.
- **Which does not make the estimates equally precise.** `median_hh_income_black_cv` is the one column in the whole district table that reaches the "unreliable" zone: median 0.043, maximum 0.480, 33 districts above 0.12 and **3 above 0.40** — MT-1 (0.480), OR-4 (0.414) and WI-7 (0.414), where the Black-householder sample is small even across ~770,000 people. `median_hh_income_asian_cv` reaches 0.229 with 33 districts above 0.12. Gate *those* on `_cv` as you would anywhere else; `median_hh_income_white_nh_cv` (max 0.099) and `pct_uninsured_cv` (max 0.051) need no gate at all.
- **441 rows, not 435.** The 435 voting districts plus the District of Columbia delegate district (`1198`), Puerto Rico's Resident Commissioner district (`7298`) and the four island-area delegate districts (`6098`, `6698`, `6998`, `7898`), which carry geometry but no ACS estimates. Filter `state NOT IN ('DC','PR','AS','GU','MP','VI')` for the 435 voting districts, or `population IS NOT NULL` for the 437 rows with data.
- **Three ACS district rows have no polygon and so no row here**: `09ZZ`, `17ZZ` and `33ZZ`, the water-only pseudo-districts of Connecticut, Illinois and New Hampshire. The ACS release tabulates 440 district rows (counted in the downloaded B01003 summary file); 437 of them are here, those three are not, and the four island-area delegate districts are here with no ACS row — 437 + 4 = 441. Their population is exactly 0, so nothing is lost.
- **Districts are equal-population by construction** — 546,488 to 1,021,191 across the 435 voting districts, 771,301 at the median (measured) — so every rate here has a far narrower spread than at any other geography: `pct_uninsured` runs 2.1% to 32.0% across all 437 districts with data, against 0–100 at tract level (measured, recipe 3). Class breaks measured at county or tract level put almost every district in one class, which is why this collection ships breaks measured on the district distribution.
- **`pct_uninsured` and `pct_with_disability` are shares of the civilian noninstitutionalized population**, not of everyone: people on active duty and people in institutions are outside the universe. Those two columns are the reason this theme has no block-group twin.
- **The race-iteration medians are classified by the householder's race**, not by every member's, and each has its own universe (households with a householder who is …). They are not shares of a common total, they cannot be averaged together, and a district's overall median from [`cd-income`](../cd-income/collection.json) is not a weighted average of them — it can sit below every one of them.
- **`pct_below_poverty_black` has a race-specific denominator** (the Black alone population for whom poverty status is determined), so it is not comparable to `pct_below_poverty`'s denominator in `cd-income`. Its median CV here is 0.080 with a maximum of 0.305 — the second-noisiest column in the collection.
- **`group_quarters_pop` is a count, not a share**, and group quarters are correctional facilities, nursing facilities, college and university housing, military quarters, group homes and shelters together — B26001 does not separate them. The highest district share is 7.2% (measured, recipe 5), nowhere near the dormitory-scale distortions that appear at tract level.
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
- **A NULL margin can mean "controlled, no sampling error".** `population_moe` is NULL on 18 of the 441 rows: the four island-area districts with no data at all, plus 14 whose ACS margin is the jam value `-555555555`, which `tools/build_acs.py` documents as "controlled, no sampling error". Those 14 are the eight single-district jurisdictions (AK `0200`, DE `1000`, DC `1198`, ND `3800`, SD `4600`, VT `5000`, WY `5600`, PR `7298`) plus all four Iowa districts and both West Virginia districts. In this collection the knock-on is `pct_foreign_born_moe`, NULL on those same 18 rows because its denominator is the controlled total, and `group_quarters_pop_moe`, NULL on 12 rows. The estimates themselves are published on all 437 rows with data. Read a missing margin as "not published", never as zero uncertainty.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count.

## Data quality

Columns with notable missingness at this geography (counted on this file, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.91% of districts (4 rows) — the four island-area delegate districts (American Samoa, Guam, the Northern Mariana Islands, the U.S. Virgin Islands), which have 2024 boundaries but no ACS 5-year estimates. |
| `pct_uninsured`, `pct_with_disability`, `pct_foreign_born`, `group_quarters_pop`, `pct_below_poverty_black` | NULL on exactly those same four rows (0.91%). Not published for block groups at all. |
| `median_hh_income_black`, `median_hh_income_white_nh`, `median_hh_income_hispanic` | NULL on 0.91% (4 rows) — the no-data rows only. For comparison: 39.47% / 2.38% / 19.60% of counties and 61.43% / 10.04% / 44.43% of tracts. |
| `median_hh_income_asian` | NULL on 1.13% of districts (5 rows): the four no-data rows plus one district with no published Asian-householder median. The sparsest column in the catalog at every other geography — 53.63% of counties, 71.27% of tracts — and effectively complete here. |
| `pct_foreign_born_moe` | NULL on 4.08% of districts (18 rows): the four above plus the 14 "controlled, no sampling error" rows in the field notes. The estimate is present on 437. |
| `group_quarters_pop_moe` | NULL on 2.72% of districts (12 rows). The estimate is present on 437. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 4 delegate districts.

The three water-only pseudo-districts the ACS tabulates — `09ZZ`, `17ZZ`, `33ZZ` — have no polygon in the cartographic boundary files and therefore no row here. A pipeline that expects every ACS district GEOID to resolve to a polygon must handle them; their population is 0.

This is the geography at which the race-iteration medians are most completely published anywhere in the catalog, and the completeness is a property of district size rather than of the population: ~770,000 people is enough for the Bureau to publish a median for almost every group almost everywhere. The reliability gates in the field notes are what remain of the problem — a published median with a CV of 0.48 is published and uncertain, which is a different failure from a blank.

Margins of error are the narrowest in the catalog, which is not the same as zero. Never compare two districts without checking whether their margins overlap, and never aggregate a median.

The PMTiles archive is real polygons at every zoom (band `0-10:geom`, from `tools/make_tiles.py`) — there are few enough districts to draw them all nationally, so there is no coarser-geography band at coarse zooms and one style classifies every zoom. `*_moe` columns are excluded from the tiles at every zoom; `*_cv` columns are kept, which matters here more than anywhere: a map of `median_hh_income_black` should grey out the three districts whose CV is over 0.40. Statistics come from the GeoParquet, always.

## Related collections

- [`congressional-districts/cd-income`](../cd-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1. The overall median these race-specific medians are read against lives there.
- [`congressional-districts/cd-people`](../cd-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1. The population race shares are there; the income-by-race medians are here.
- [`congressional-districts/cd-housing`](../cd-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts/cd-connectivity`](../cd-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts`](../congressional-districts/collection.json) — the sixth sibling: all 112 columns for the same 441 districts, in one table. Use it when a question crosses themes.
- The same theme at the other geographies: [`state-wellbeing`](../../states/state-wellbeing/collection.json), [`county-wellbeing`](../../counties/county-wellbeing/collection.json), [`zcta-wellbeing`](../../zctas/zcta-wellbeing/collection.json), [`place-wellbeing`](../../places/place-wellbeing/collection.json) and [`tract-wellbeing`](../../tracts/tract-wellbeing/collection.json). **No block-group twin**: the Census Bureau does not publish these tables at that geography. Only the state join is a prefix join.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, the geography these district lines were drawn from. Different survey, different vintage, no margins of error, and none of these columns.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

For cost: 441 rows, 8,887,888 bytes on disk, of which `geometry` is about
8.8 MB. Filtering is never a cost question here; selecting `geometry` is.

### 1. How often is each race-iteration median published at all?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT round(100.0*count(median_hh_income_white_nh)/count(*), 2) AS pct_published_white_nh,
       round(100.0*count(median_hh_income_black)/count(*), 2)    AS pct_published_black,
       round(100.0*count(median_hh_income_hispanic)/count(*), 2) AS pct_published_hispanic,
       round(100.0*count(median_hh_income_asian)/count(*), 2)    AS pct_published_asian
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet';
```

→ `99.09 | 99.09 | 99.09 | 98.87`.

The same query against
`tracts/tract-wellbeing/tract-wellbeing.parquet` returns
`89.96 | 38.57 | 55.57 | 28.73`. At tract level the blanks are the story — a
national map of `median_hh_income_asian` is drawn on 28.73% of tracts, and the
coverage is a map of where the population lives. Here the blanks are four
island-area rows and one district, so the map is drawn on effectively every
district. Run this first anyway: the number is the sentence you are allowed to
write about coverage.

### 2. Income by race against income overall (1:1 sibling join, `_cv`-gated)

```sql
LOAD httpfs;
SELECT w.name, i.median_hh_income::int           AS overall,
       w.median_hh_income_white_nh::int          AS white_nh,
       w.median_hh_income_black::int             AS black,
       round(w.median_hh_income_black / w.median_hh_income_white_nh, 2) AS black_to_white
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet' w
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet' i
  USING (geoid)
WHERE w.median_hh_income_black_cv    < 0.20
  AND w.median_hh_income_white_nh_cv < 0.20
ORDER BY black_to_white LIMIT 5;
```

→ `Congressional District 11, California | 143154 | 179017 | 52015 | 0.29`,
`District 10, New York | 117000 | 161816 | 55579 | 0.34`,
`District 7, Illinois | 83208 | 128895 | 44738 | 0.35`,
`District 12, New York | 147775 | 165137 | 57178 | 0.35`,
`Delegate District (at Large), District of Columbia | 109870 | 170201 | 60764 | 0.36`.

In CA-11 the Black-householder median is 29% of the non-Hispanic
White-householder median. Note that the overall median ($143,154) sits *above*
the Black-householder median and *below* the White one — possible because the
three medians have three different universes, and a median is not a weighted
average of sub-medians. Then quote the denominator the gate left you:

```sql
LOAD httpfs;
SELECT count(*) AS districts,
       count(*) FILTER (WHERE median_hh_income_black    IS NOT NULL
                          AND median_hh_income_white_nh IS NOT NULL) AS both_published,
       count(*) FILTER (WHERE median_hh_income_black_cv    < 0.20
                          AND median_hh_income_white_nh_cv < 0.20)   AS both_reliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet';
```

→ `441 | 437 | 429`.

429 of 441 districts support the comparison at a 0.20 gate. The same recipe in
one county at tract level ([Fulton County, Georgia](../../tracts/tract-wellbeing/AGENTS.md))
can compare only 164 of 327 tracts before any gate at all. "In 429 of the 441
districts, where both medians are published and reliable" is a true sentence;
at tract level the equivalent sentence has to be much more careful.

### 3. The health columns, and how narrow the district distribution is

```sql
LOAD httpfs;
SELECT 'congressional district' AS geography, count(pct_uninsured) AS n,
       round(min(pct_uninsured), 1)                      AS min,
       round(quantile_cont(pct_uninsured, 0.5), 1)       AS p50,
       round(max(pct_uninsured), 1)                      AS max,
       round(quantile_cont(pct_uninsured_moe, 0.5), 2)   AS median_moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet'
UNION ALL
SELECT 'county', count(pct_uninsured), round(min(pct_uninsured), 1), round(quantile_cont(pct_uninsured, 0.5), 1),
       round(max(pct_uninsured), 1), round(quantile_cont(pct_uninsured_moe, 0.5), 2)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet'
UNION ALL
SELECT 'tract', count(pct_uninsured), round(min(pct_uninsured), 1), round(quantile_cont(pct_uninsured, 0.5), 1),
       round(max(pct_uninsured), 1), round(quantile_cont(pct_uninsured_moe, 0.5), 2)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet';
```

→

```
congressional district |   437 | 2.1 | 7.4 |  32.0 | 0.28
county                 |  3222 | 0.0 | 7.7 |  44.6 | 1.27
tract                  | 84386 | 0.0 | 6.4 | 100.0 | 3.52
```

Same median, radically different tails and margins: ±0.28 percentage points at
district level against ±3.52 at tract. Where the uninsured are:

```sql
LOAD httpfs;
SELECT geoid, name, pct_uninsured, pct_uninsured_moe AS moe, pct_with_disability, pct_foreign_born
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet'
ORDER BY pct_uninsured DESC LIMIT 5;
```

→ `4829 | Congressional District 29, Texas | 32.01 | 0.55 | 12.3 | 32.69`,
`4833 | District 33, Texas | 29.15 | 0.51 | 10.38 | 33.64`,
`4834 | District 34, Texas | 26.08 | 0.48 | 12.91 | 21.99`,
`4815 | District 15, Texas | 25.41 | 0.5 | 13.68 | 22.34`,
`4818 | District 18, Texas | 24.0 | 0.55 | 12.06 | 24.67`.

All five are Texas districts, and no reliability gate was needed. The
disability column moves independently of the insurance column — 10.4% in TX-33
against 13.7% in TX-15 — so neither is a proxy for the other. Both are shares
of the **civilian noninstitutionalised** population, so active-duty personnel
and people in institutions are outside the denominator entirely.

### 4. One district against its own state, and the spread inside a state

```sql
LOAD httpfs;
SELECT d.name, d.pct_uninsured AS district_uninsured, s.pct_uninsured AS state_uninsured,
       round(d.pct_uninsured - s.pct_uninsured, 1) AS gap
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet' d
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-wellbeing/state-wellbeing.parquet' s
  ON substr(d.geoid, 1, 2) = s.geoid
WHERE d.state = 'TX'
ORDER BY gap DESC LIMIT 5;
```

→ `Congressional District 29, Texas | 32.01 | 17.13 | 14.9`,
`District 33 | 29.15 | 17.13 | 12.0`, `District 34 | 26.08 | 17.13 | 9.0`,
`District 15 | 25.41 | 17.13 | 8.3`, `District 18 | 24.0 | 17.13 | 6.9`.

`substr(geoid, 1, 2)` is the only prefix join a district has. Texas's statewide
uninsured rate is 17.13%, and TX-29 is nearly twice that. The spread inside
each state:

```sql
LOAD httpfs;
SELECT state, count(*) AS districts, min(pct_uninsured) AS lowest, max(pct_uninsured) AS highest,
       round(max(pct_uninsured) - min(pct_uninsured), 1) AS spread
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet'
WHERE pct_uninsured IS NOT NULL
GROUP BY state HAVING count(*) >= 5
ORDER BY spread DESC LIMIT 5;
```

→

```
TX | 38 | 9.76 | 32.01 | 22.3
AZ |  9 | 6.49 | 20.28 | 13.8
NJ | 12 | 3.74 | 16.45 | 12.7
CA | 52 | 3.04 | 14.11 | 11.1
GA | 14 | 8.03 | 17.31 |  9.3
```

Texas's districts run from 9.8% to 32.0% uninsured on the same ~770,000
population each. A single statewide number hides a factor of three.

### 5. Where `_cv` still matters, and the group-quarters check

```sql
LOAD httpfs;
SELECT 'median_hh_income_black' AS column,
       count(median_hh_income_black_cv)                          AS publishes_cv,
       round(quantile_cont(median_hh_income_black_cv, 0.5), 3)   AS median_cv,
       round(max(median_hh_income_black_cv), 3)                  AS max_cv,
       count(*) FILTER (WHERE median_hh_income_black_cv > 0.12)  AS over_0_12,
       count(*) FILTER (WHERE median_hh_income_black_cv > 0.40)  AS over_0_40
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet'
UNION ALL
SELECT 'median_hh_income_asian', count(median_hh_income_asian_cv),
       round(quantile_cont(median_hh_income_asian_cv, 0.5), 3), round(max(median_hh_income_asian_cv), 3),
       count(*) FILTER (WHERE median_hh_income_asian_cv > 0.12), count(*) FILTER (WHERE median_hh_income_asian_cv > 0.40)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet'
UNION ALL
SELECT 'median_hh_income_white_nh', count(median_hh_income_white_nh_cv),
       round(quantile_cont(median_hh_income_white_nh_cv, 0.5), 3), round(max(median_hh_income_white_nh_cv), 3),
       count(*) FILTER (WHERE median_hh_income_white_nh_cv > 0.12), count(*) FILTER (WHERE median_hh_income_white_nh_cv > 0.40)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet'
UNION ALL
SELECT 'pct_uninsured', count(pct_uninsured_cv), round(quantile_cont(pct_uninsured_cv, 0.5), 3),
       round(max(pct_uninsured_cv), 3), count(*) FILTER (WHERE pct_uninsured_cv > 0.12),
       count(*) FILTER (WHERE pct_uninsured_cv > 0.40)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet';
```

→

```
median_hh_income_black    | 437 | 0.043 | 0.48  | 33 | 3
median_hh_income_asian    | 436 | 0.056 | 0.229 | 33 | 0
median_hh_income_white_nh | 437 | 0.011 | 0.099 |  0 | 0
pct_uninsured             | 437 | 0.023 | 0.051 |  0 | 0
```

The three districts above 0.40 on the Black-householder median are MT-1
($61,406 ± 48,513, CV 0.480), OR-4 ($37,122 ± 25,300, CV 0.414) and WI-7
($49,250 ± 33,555, CV 0.414) — published, and worth nothing without their
margins. Everything in the first and second rows is why a `_cv` gate stays in
the recipe even at a geography where most columns do not need one.

The group-quarters check, for when an age or income profile looks odd:

```sql
LOAD httpfs;
SELECT geoid, name, population, group_quarters_pop,
       round(100.0*group_quarters_pop/population, 1) AS pct_group_quarters
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet'
WHERE population IS NOT NULL
ORDER BY pct_group_quarters DESC LIMIT 5;
```

→ `2507 | Congressional District 7, Massachusetts | 773502 | 55355 | 7.2`,
`1202 | Congressional District 2, Florida | 792630 | 55445 | 7.0`,
`3619 | Congressional District 19, New York | 774788 | 53758 | 6.9`,
`4215 | Congressional District 15, Pennsylvania | 758565 | 52031 | 6.9`,
`1203 | Congressional District 3, Florida | 798141 | 49735 | 6.2`.

7.2% is the national maximum. Equal-population districts dilute group quarters
to the point where they shift a median slightly rather than inverting it — the
opposite of tract level, where a single dormitory tract can be 99% group
quarters. B26001 does not separate dormitories from prisons from nursing homes,
so this column tells you to be careful, not what to be careful about.

### Related recipes elsewhere

- All 112 columns on the same 441 districts, the national rank of one district,
  and the spatial recipe for what is inside it:
  [`congressional-districts`](../congressional-districts/AGENTS.md).
- The overall income median these race-specific medians are read against, and
  the margin-overlap test on a state's ranking:
  [`cd-income`](../cd-income/AGENTS.md).
- The population race shares, which are a different thing from income by
  householder race: [`cd-people`](../cd-people/AGENTS.md).
- The same columns at tract level, where these four medians are published on a
  minority of rows and the NULLs are the subject:
  [`tracts/tract-wellbeing/AGENTS.md`](../../tracts/tract-wellbeing/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive is real polygons at
every zoom (`0-10:geom`) and carries the `*_cv` columns recipe 5 reads, but no
`*_moe` columns — and it is a map artifact either way: query the GeoParquet for
numbers.
