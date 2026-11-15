# Agent guide — People & Education (Congressional Districts, 119th Congress)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections, and the [group guide](../AGENTS.md) covers what the six congressional-district collections share; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

Who lives here: median age and the shares under 18 and 65 or over ([B01002](https://data.census.gov/table/ACSDT5Y2024.B01002), [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001)), the four mutually exclusive non-Hispanic race shares this catalog carries — White, Black or African American, American Indian and Alaska Native, Asian — plus Hispanic or Latino of any race and its complement, people of color ([B03002](https://data.census.gov/table/ACSDT5Y2024.B03002)), and the share of adults 25 and over holding a bachelor's degree or higher ([B15003](https://data.census.gov/table/ACSDT5Y2024.B15003)).

**441 rows**, one per congressional district, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

**These are the districts of the 119th Congress**, the vintage this ACS release tabulates. Three independent confirmations, two of them re-measured for this file: the release's own summary-level prefix is `5001900US` (the `19`), the cartographic boundary file is `cb_2024_us_cd119_500k` and carries `CDSESSN = '119'` on all 441 features (counted: one group, 441 rows), and the Census Bureau's [ACS geography boundaries by year](https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year/2024.html) lists "Congressional District, Delegate District DC, Resident Commissioner District PR" with the vintage "119th Congress of the United States". **District numbers are not stable across congresses.** A `geoid` here is not the same ground as the same `geoid` in an earlier congress, these estimates must never be read as a time series, and a demographic shift between two congresses' district tables is a boundary change, not a population change.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/cd-people.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/cd-people.pmtiles`, layer `cd-people`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/collection.json` — carries a full description for every column

This is a themed cut of the wide district table: the same 441 rows and the same geometry, with this theme's columns and class breaks measured on the district distribution. All 112 columns in one file are at `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.parquet` (that file's data stayed one directory up; its metadata is in [`congressional-districts/`](../congressional-districts/collection.json)). The cut is not a download saving — over 99% of each of these files is `geometry` (99.29–99.48%, measured with `parquet_metadata`) — so choose by column set and styles, not by bytes.

## Source tables

| table | title | universe |
|---|---|---|
| [B01001](https://data.census.gov/table/ACSDT5Y2024.B01001) | Sex by Age | Total population |
| [B01002](https://data.census.gov/table/ACSDT5Y2024.B01002) | Median Age by Sex | Total population |
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B03002](https://data.census.gov/table/ACSDT5Y2024.B03002) | Hispanic or Latino Origin by Race | Total population |
| [B15003](https://data.census.gov/table/ACSDT5Y2024.B15003) | Educational Attainment for the Population 25 Years and Over | Population 25 years and over |

## Schema

`geoid` is 4 characters — state FIPS (2) + district (2) — so `substr(geoid, 1, 2)` joins [`states`](../../states/states/collection.json) and the themed [`state-people`](../../states/state-people/collection.json). At-large states use district `00` (AK, DE, ND, SD, VT, WY) and the non-voting delegate districts use `98`: `1198` District of Columbia, `7298` Puerto Rico, `6098` American Samoa, `6698` Guam, `6998` Northern Mariana Islands, `7898` U.S. Virgin Islands. Nothing finer joins by prefix — district boundaries follow 2020 census blocks, not counties or tracts, so relating a district to the tracts or counties inside it is a spatial operation (worked example in the [wide table's guide](../congressional-districts/AGENTS.md)).

| column | type | what it is |
|---|---|---|
| `geoid` | string | 4-character congressional district GEOID: state FIPS 2 + district 2, e.g. `0612` for California's 12th. 119th Congress. |
| `name` | string | `NAMELSAD` from the 2024 cd119 cartographic boundary file plus the state name — "Congressional District 12, California", "Delegate District (at Large), District of Columbia". |
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

- **This collection has no `_cv` columns at all** — use `_moe`. That is the same shape as [`tract-people`](../../tracts/tract-people/AGENTS.md), and at this geography it costs little: the median `pct_bachelors_plus_moe` is **0.63 percentage points** against 2.24 at county level and 6.67 at tract level (measured).
- **441 rows, not 435.** The 435 voting districts plus the District of Columbia delegate district (`1198`), Puerto Rico's Resident Commissioner district (`7298`) and the four island-area delegate districts (`6098`, `6698`, `6998`, `7898`), which carry geometry but no ACS estimates. Filter `state NOT IN ('DC','PR','AS','GU','MP','VI')` for the 435 voting districts, or `population IS NOT NULL` for the 437 rows with data.
- **Three ACS district rows have no polygon and so no row here**: `09ZZ`, `17ZZ` and `33ZZ`, the water-only pseudo-districts of Connecticut, Illinois and New Hampshire. The ACS release tabulates 440 district rows (counted in the downloaded B01003 summary file); 437 of them are here, those three are not, and the four island-area delegate districts are here with no ACS row — 437 + 4 = 441. Their population is exactly 0, so nothing is lost.
- **Districts are equal-population by construction** — 546,488 to 1,021,191 across the 435 voting districts, 771,301 at the median (measured) — so every share here has a far narrower spread than at any other geography. `pct_bachelors_plus` runs p10 23.4 / p50 33.3 / p90 50.3, against 11.9 / 29.7 / 64.4 at tract level (measured, recipe 1). Class breaks borrowed from county or tract work will put almost every district in one class, which is why this collection ships breaks measured on the district distribution.
- **The four non-Hispanic race shares** — `pct_white_nh`, `pct_black`, `pct_native`, `pct_asian` — are all drawn from B03002's "Not Hispanic or Latino" branch, so they and `pct_hispanic` are mutually exclusive and do not double-count. They do not sum to 100: B03002's "Native Hawaiian and Other Pacific Islander", "Some other race" and "Two or more races" branches are not published here, so the five shares together run 64.23 to 99.78 with a median of 95.43 across districts (measured). `pct_people_of_color` is the complement of `pct_white_nh` and does cover the remainder.
- **`pct_people_of_color` is a complement** (`100 − pct_white_nh`) and carries `pct_white_nh`'s margin of error unchanged. It is not an independent estimate and must not be treated as one.
- **`pct_bachelors_plus` divides by the population 25 and over** (B15003's universe), not by everyone — a district with a large student population has many adults under 25 outside the denominator.
- **Every estimate has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. To compare two geographies, check
  whether their margins overlap before calling a difference real. To sum
  estimates across geographies, add the margins in quadrature
  (`sqrt(sum(moe*moe))`). **Never sum or average a median**: a median of a
  region is not derivable from the medians of its parts — `median_age`
  included.
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **A NULL margin can mean "controlled, no sampling error".** `population_moe` is NULL on 18 of the 441 rows: the four island-area districts with no data at all, plus 14 whose ACS margin is the jam value `-555555555`, which `tools/build_acs.py` documents as "controlled, no sampling error". Those 14 are the eight single-district jurisdictions (AK `0200`, DE `1000`, DC `1198`, ND `3800`, SD `4600`, VT `5000`, WY `5600`, PR `7298`) plus all four Iowa districts and both West Virginia districts; the ACS row for Alaska reads `5001900US0200|735706|-555555555`. Because a derived share's margin needs its denominator's margin, **every column in this collection whose denominator is total population is NULL on those same 18 rows**: `pct_under_18_moe`, `pct_65_plus_moe`, the four non-Hispanic race-share margins, `pct_hispanic_moe` and `pct_people_of_color_moe` — each carried on 423 of the 441 rows. The estimates themselves are published; only the margins are missing. Read a missing margin as "not published", never as zero uncertainty.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area — and those 2020 blocks are the geography these district lines
  were drawn from, which is a different thing again.

## Data quality

Columns with notable missingness at this geography (counted on this file, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.91% of districts (4 rows) — the four island-area delegate districts (American Samoa, Guam, the Northern Mariana Islands, the U.S. Virgin Islands), which have 2024 boundaries but no ACS 5-year estimates. |
| every estimate in this collection | NULL on exactly those same four rows (0.91%). No suppression anywhere else: `median_age`, the age shares, all six race/ethnicity shares, `pct_people_of_color` and `pct_bachelors_plus` publish on all 437 districts with data. |
| `population_moe`, `pct_under_18_moe`, `pct_65_plus_moe`, `pct_white_nh_moe`, `pct_black_moe`, `pct_native_moe`, `pct_asian_moe`, `pct_hispanic_moe`, `pct_people_of_color_moe` | NULL on 4.08% of districts (18 rows): the four above plus the 14 "controlled, no sampling error" rows in the field notes. The estimates are present on 437. |
| `median_age_moe`, `pct_bachelors_plus_moe` | NULL on 0.91% only — their denominators are not the controlled total. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 4 delegate districts.

The three water-only pseudo-districts the ACS tabulates — `09ZZ`, `17ZZ`, `33ZZ` — have no polygon in the cartographic boundary files and therefore no row here. A pipeline that expects every ACS district GEOID to resolve to a polygon must handle them; their population is 0.

Margins of error are the narrowest in the catalog, which is not the same as zero: recipe 4 finds 142 districts estimated to be majority people of color and 136 that hold that at the bottom of their own margin. Never compare two districts without checking whether their margins overlap, and never average `median_age` across districts.

The PMTiles archive is real polygons at every zoom (band `0-10:geom`, from `tools/make_tiles.py`) — there are few enough districts to draw them all nationally, so there is no coarser-geography band at coarse zooms and one style classifies every zoom. `*_moe` columns are excluded from the tiles at every zoom, and this collection has no `*_cv` columns to carry. Statistics come from the GeoParquet, always.

## Related collections

- [`congressional-districts/cd-income`](../cd-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts/cd-housing`](../cd-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts/cd-connectivity`](../cd-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts/cd-wellbeing`](../cd-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1. The race-iteration income medians live there, not here.
- [`congressional-districts`](../congressional-districts/collection.json) — the sixth sibling: all 112 columns for the same 441 districts, in one table. Use it when a question crosses themes.
- The same theme at the other geographies: [`state-people`](../../states/state-people/collection.json), [`county-people`](../../counties/county-people/collection.json), [`zcta-people`](../../zctas/zcta-people/collection.json), [`place-people`](../../places/place-people/collection.json), [`tract-people`](../../tracts/tract-people/collection.json) and [`bg-people`](../../block-groups/bg-people/collection.json). Only the state join is a prefix join.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, including race and Hispanic origin counted rather than estimated, and the geography these district lines were drawn from. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

For cost: 441 rows, 8,875,880 bytes on disk, of which `geometry` is about
8.8 MB. Filtering is never a cost question here; selecting `geometry` is.

### 1. How much narrower is a district than a tract? (the distribution first)

```sql
INSTALL httpfs; LOAD httpfs;
SELECT 'congressional district' AS geography, count(pct_bachelors_plus) AS n,
       round(quantile_cont(pct_bachelors_plus, 0.10), 1)     AS p10,
       round(quantile_cont(pct_bachelors_plus, 0.50), 1)     AS p50,
       round(quantile_cont(pct_bachelors_plus, 0.90), 1)     AS p90,
       round(quantile_cont(pct_bachelors_plus_moe, 0.50), 2) AS median_moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/cd-people.parquet'
UNION ALL
SELECT 'county', count(pct_bachelors_plus), round(quantile_cont(pct_bachelors_plus, 0.10), 1),
       round(quantile_cont(pct_bachelors_plus, 0.50), 1), round(quantile_cont(pct_bachelors_plus, 0.90), 1),
       round(quantile_cont(pct_bachelors_plus_moe, 0.50), 2)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet'
UNION ALL
SELECT 'tract', count(pct_bachelors_plus), round(quantile_cont(pct_bachelors_plus, 0.10), 1),
       round(quantile_cont(pct_bachelors_plus, 0.50), 1), round(quantile_cont(pct_bachelors_plus, 0.90), 1),
       round(quantile_cont(pct_bachelors_plus_moe, 0.50), 2)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/tract-people.parquet';
```

→

```
congressional district |   437 | 23.4 | 33.3 | 50.3 | 0.63
county                 |  3222 | 14.4 | 22.3 | 38.7 | 2.24
tract                  | 84514 | 11.9 | 29.7 | 64.4 | 6.67
```

Read both halves. The district band (23–50) is a third the width of the tract
band (12–64) because every district averages ~770,000 people; the district
margin (±0.63pp at the median) is **ten times** narrower than the tract margin
(±6.67pp). That trade is the whole reason to work at this geography — and the
reason a "high education" threshold calibrated on tracts is useless here.

### 2. One district against its own state, and the spread inside a state

```sql
LOAD httpfs;
SELECT d.name, d.pct_people_of_color AS district_poc, d.pct_people_of_color_moe AS moe,
       s.pct_people_of_color AS state_poc,
       round(d.pct_people_of_color - s.pct_people_of_color, 1) AS gap
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/cd-people.parquet' d
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-people/state-people.parquet' s
  ON substr(d.geoid, 1, 2) = s.geoid
WHERE d.state = 'TX'
ORDER BY d.pct_people_of_color DESC LIMIT 5;
```

→ `Congressional District 34, Texas | 92.41 | 0.14 | 60.88 | 31.5`,
`District 29 | 92.28 | 0.38 | 60.88 | 31.4`,
`District 16 | 88.58 | 0.13 | 60.88 | 27.7`,
`District 33 | 87.22 | 0.55 | 60.88 | 26.3`,
`District 9 | 86.98 | 0.5 | 60.88 | 26.1`.

`substr(geoid, 1, 2)` is the only prefix join a district has. Note the margins:
±0.14 on a 92% share. Now the within-state spread, which is where the real
variation at this geography lives:

```sql
LOAD httpfs;
SELECT state, count(*) AS districts,
       min(pct_people_of_color) AS lowest, max(pct_people_of_color) AS highest,
       round(max(pct_people_of_color) - min(pct_people_of_color), 1) AS spread
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/cd-people.parquet'
WHERE pct_people_of_color IS NOT NULL
GROUP BY state HAVING count(*) >= 5
ORDER BY spread DESC LIMIT 5;
```

→

```
NY | 26 | 10.92 | 90.78 | 79.9
IL | 17 | 10.25 | 76.76 | 66.5
TN |  9 | 11.51 | 76.22 | 64.7
MD |  8 | 28.46 | 89.99 | 61.5
NJ | 12 | 20.34 | 81.59 | 61.3
```

New York's districts run from 10.9% to 90.8% people of color while each holds
roughly the same number of people. A national map of this column at district
level is mostly a map of which states are diverse; the inside-a-state view is
the one that separates districts.

### 3. Who lives in the rich districts and the poor ones? (1:1 sibling join)

```sql
LOAD httpfs;
WITH j AS (
  SELECT ntile(5) OVER (ORDER BY i.median_hh_income) AS q,
         p.pct_bachelors_plus, p.median_age, p.pct_under_18, p.pct_people_of_color
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet' i
  JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/cd-people.parquet' p
    USING (geoid)
  WHERE i.median_hh_income IS NOT NULL)
SELECT q AS income_quintile, round(avg(pct_bachelors_plus), 1) AS degree,
       round(avg(median_age), 1) AS median_age, round(avg(pct_under_18), 1) AS under_18,
       round(avg(pct_people_of_color), 1) AS people_of_color
FROM j GROUP BY 1 ORDER BY 1;
```

→

```
1 | 25.9 | 38.4 | 22.5 | 48.4
2 | 29.5 | 39.3 | 21.9 | 35.6
3 | 34.1 | 39.3 | 22.0 | 39.8
4 | 38.3 | 38.7 | 21.7 | 45.1
5 | 50.0 | 39.8 | 21.4 | 44.7
```

The join is 1:1 on `geoid` — all six district collections hold the same 441
rows. Education doubles across the income distribution; age and the under-18
share barely move, because equal-population districts average age structures
out. `people_of_color` is **not** monotonic (48.4, 35.6, 39.8, 45.1, 44.7): the
poorest and the richest quintiles are both more diverse than the second, which
is a real feature of these estimates and the reason to look at the column
rather than assume a gradient. `avg()` of `median_age` here is an average of
medians over districts — a summary of the districts, not of people, and it must
not be quoted as the median age of anything.

### 4. Which districts are genuinely majority people of color? (margins, not estimates)

```sql
LOAD httpfs;
SELECT count(*)                                                                   AS estimate_over_50,
       count(*) FILTER (WHERE pct_people_of_color - pct_people_of_color_moe > 50)  AS significantly_over_50,
       count(*) FILTER (WHERE pct_people_of_color + pct_people_of_color_moe <= 50) AS ruled_out
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/cd-people.parquet'
WHERE pct_people_of_color > 50;
```

→ `142 | 136 | 0`.

142 districts estimate a majority of residents who are not White-alone
non-Hispanic; 136 of them clear 50% at the bottom of their 90% interval, 6 sit
inside their own margin, and none is ruled out. `estimate - moe` is the
published interval's lower bound, so this is the Bureau's own arithmetic rather
than an added assumption. Remember whose margin it is: `pct_people_of_color`
carries `pct_white_nh`'s margin unchanged, because it is `100 − pct_white_nh`.

### 5. The age columns, and the group-quarters trap

```sql
LOAD httpfs;
SELECT geoid, name, median_age, median_age_moe AS moe, pct_under_18, pct_65_plus
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/cd-people.parquet'
WHERE population IS NOT NULL
ORDER BY median_age LIMIT 5;
```

→ `4903 | Congressional District 3, Utah | 30.6 | 0.2 | 26.55 | 12.27`,
`0622 | Congressional District 22, California | 30.6 | 0.3 | 30.15 | 9.76`,
`4904 | Congressional District 4, Utah | 30.9 | 0.3 | 31.43 | 9.32`,
`0403 | Congressional District 3, Arizona | 31.2 | 0.3 | 26.79 | 8.67`,
`4834 | Congressional District 34, Texas | 31.3 | 0.3 | 29.8 | 13.13`.

±0.2–0.3 years on a median age is the kind of precision this geography buys —
and it is still not enough to order the top of the list, because UT-3 and CA-22
are both 30.6. The two reach that median by different routes: 26.55% under 18
in UT-3 against 30.15% in CA-22, with UT-3 carrying more people 65 and over
(12.27% against 9.76%). `median_age`, `pct_under_18` and `pct_65_plus` are
three different facts about an age structure, not substitutes. If a district's age
structure looks strange, check `group_quarters_pop` in
[`cd-wellbeing`](../cd-wellbeing/collection.json): the highest group-quarters
shares here are 7.2% (MA-7) and 7.0% (FL-2), measured, which is enough to move
a median age but nowhere near the dormitory-scale distortions that appear at
tract level.

### Related recipes elsewhere

- All 112 columns on the same 441 districts, the national rank of one district,
  and the spatial recipe for what is inside it:
  [`congressional-districts`](../congressional-districts/AGENTS.md).
- Median household income by householder race and ethnicity, published on 99%
  of districts against 38.57% of tracts:
  [`cd-wellbeing`](../cd-wellbeing/AGENTS.md).
- The income distribution these quintiles came from, and the class-break
  measurement: [`cd-income`](../cd-income/AGENTS.md).
- The same columns at tract level, where a "which tract am I in"
  point-in-polygon recipe lives:
  [`tracts/tract-people/AGENTS.md`](../../tracts/tract-people/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive is real polygons at
every zoom (`0-10:geom`) and carries no `*_moe` columns — and since this
collection has no `*_cv` columns either, the tiles carry estimates only.
Query the GeoParquet for numbers.
