# Agent guide — Commuting & Connectivity (Counties)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

How people get around and get online: households with no vehicle available, as a count and a share ([B25044](https://data.census.gov/table/ACSDT5Y2024.B25044)); commute mode shares for driving alone, public transportation, walking or cycling, and working from home ([B08301](https://data.census.gov/table/ACSDT5Y2024.B08301)); the share of commutes of 45 minutes or more ([B08303](https://data.census.gov/table/ACSDT5Y2024.B08303)); and the shares of households with no internet access and no computing device ([B28002](https://data.census.gov/table/ACSDT5Y2024.B28002), [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001)).

**3,235 rows**, one per county or county equivalent, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

One column here needs care even at this geography. `pct_commute_transit` publishes a coefficient of variation for only **2,417** of the 3,235 counties, and **69.9%** of those are above the 0.40 "unreliable" line (measured). Most American counties have too little transit commuting to estimate a share precisely — that is a finding about the country, not a defect in the file. Everything else in this chunk is tight: the median `pct_no_internet_cv` is 0.115 and `pct_hh_no_vehicle_cv` 0.172 (measured).

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.pmtiles`, layer `county-connectivity`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/collection.json` — carries a full description for every column

This is one themed cut of the county table. The same rows with all 112 columns — every theme at once, no join — are the sixth sibling in this group, [`counties/counties`](../counties/collection.json), whose data files sit one directory up at `https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet` (and `.pmtiles`).

## Source tables

| table | title | universe |
|---|---|---|
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B08301](https://data.census.gov/table/ACSDT5Y2024.B08301) | Means of Transportation to Work | Workers 16 years and over |
| [B08303](https://data.census.gov/table/ACSDT5Y2024.B08303) | Travel Time to Work | Workers 16 years and over who did not work from home |
| [B25044](https://data.census.gov/table/ACSDT5Y2024.B25044) | Tenure by Vehicles Available | Occupied housing units |
| [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001) | Types of Computers in Household | Households |
| [B28002](https://data.census.gov/table/ACSDT5Y2024.B28002) | Presence and Types of Internet Subscriptions in Household | Households |

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
| `hh_no_vehicle` | int64 | Occupied housing units with no vehicle available, owner- and renter-occupied combined. |
| `hh_no_vehicle_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `hh_no_vehicle`. |
| `pct_hh_no_vehicle` | double | Percent of occupied housing units with no vehicle available. |
| `pct_hh_no_vehicle_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_hh_no_vehicle`. |
| `pct_hh_no_vehicle_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_hh_no_vehicle`. |
| `pct_commute_drive_alone` | double | Percent of workers who drove alone to work in a car, truck or van. |
| `pct_commute_drive_alone_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_commute_drive_alone`. |
| `pct_commute_transit` | double | Percent of workers who commuted by public transportation. |
| `pct_commute_transit_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_commute_transit`. |
| `pct_commute_transit_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_commute_transit`. |
| `pct_commute_walk_bike` | double | Percent of workers who walked or bicycled to work. |
| `pct_commute_walk_bike_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_commute_walk_bike`. |
| `pct_work_from_home` | double | Percent of workers who worked from home. |
| `pct_work_from_home_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_work_from_home`. |
| `pct_commute_45min_plus` | double | Percent of commuters whose one-way travel time to work is 45 minutes or more. |
| `pct_commute_45min_plus_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_commute_45min_plus`. |
| `pct_no_internet` | double | Percent of households with no internet access of any kind. |
| `pct_no_internet_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_no_internet`. |
| `pct_no_internet_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_no_internet`. |
| `pct_no_computer` | double | Percent of households with no computing device — no desktop or laptop, no smartphone, no tablet, no other computer. |
| `pct_no_computer_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_no_computer`. |
| `geometry` | binary | Boundary polygon, WKB, EPSG:4326 / OGC:CRS84. |
| `bbox` | struct<xmin, ymin, xmax, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, with row-group statistics. |

## Field notes

- **`population_moe` is NULL on 3,103 of the 3,235 rows** (measured — only 132
  small rural counties carry one). Read `population` at this geography as a
  count to use rather than an estimate to put an interval on. Every other
  `*_moe` column in this chunk is populated on all 3,222 rows that carry ACS
  data (measured).
- **Every estimate has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. To compare two geographies, check
  whether their margins overlap before calling a difference real. To sum
  estimates across geographies, add the margins in quadrature
  (`sqrt(sum(moe*moe))`). **Never sum or average a median**: a median of a
  region is not derivable from the medians of its parts.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. Filtering or greying out by CV is the intended use, and in this
  chunk it is not optional: see `pct_commute_transit`, below.
- **`pct_commute_transit_cv` is NULL on 818 counties** (25.29%, measured) even
  though `pct_commute_transit` itself is published on 3,222. Measured: 13 of
  those are the island areas with no estimate at all, and the other **805 have
  an estimate of exactly 0.0** — a CV divides by the estimate, so there is none.
  `pct_commute_transit_cv IS NOT NULL` is therefore a filter on *having any
  measurable transit at all*, not a reliability filter — apply the 0.40
  threshold on top of it, and say which of the two you used.
- **`pct_commute_45min_plus` divides by workers who did not work from home**
  (B08303's own universe), while every other commute share divides by all
  workers 16+ (B08301). The two denominators differ, so the shares do not sum
  across tables, and `pct_work_from_home + pct_commute_45min_plus` is not a
  meaningful quantity.
- **The four B08301 shares do not sum to 100** either: driving in a carpool,
  taxi, motorcycle and "other means" are not carried as columns. Treat the
  remainder as "not broken out here".
- **`hh_no_vehicle` is a count of occupied housing units, not of people**, and
  `pct_hh_no_vehicle` is its share of occupied units (B25044, owner- and
  renter-occupied combined). The count and the share rank completely differently
  — recipe 4 shows both.
- **`pct_no_internet` and `pct_no_computer` are household shares** (B28002,
  B28001), not population shares, and this chunk carries no household count.
  Join `households` from
  [`county-housing`](../county-housing/collection.json) when a count is needed;
  `population` is not a household count.
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
- **Commuting at county level is residence-based.** These are shares of workers
  *living* in the county, by how they got to work, wherever the work was. A
  county with heavy inbound commuting looks like its residents, not like its
  daytime population.
- **Connecticut's county equivalents are the 9 planning regions**
  (`09110`–`09190`, measured) in the 2024 vintage, not the 8 historical
  counties. A 2020-vintage block or tract GEOID's 5-character prefix does not
  match these rows.

## Data quality

Columns with notable missingness at this geography, measured over this file:

| column | missingness |
|---|---|
| `population` | NULL on 0.40% of counties (13 rows) — the island-area county equivalents (AS 5, GU 1, MP 4, VI 3, measured), which have cartographic boundaries but no ACS 5-year estimates. |
| `population_moe` | NULL on 95.92% of counties (3,103 of 3,235). |
| every estimate column (`hh_no_vehicle`, `pct_hh_no_vehicle`, the four commute-mode shares, `pct_commute_45min_plus`, `pct_no_internet`, `pct_no_computer`) | NULL on 0.40% (13 rows) — the island areas only. Nothing in this chunk is suppressed for sample size. |
| `pct_commute_transit_cv` | **NULL on 25.29% of counties (818 rows)** — measured: 13 island areas plus 805 counties whose estimate is exactly 0.0, and a CV divides by the estimate. Of the 2,417 that do publish one, 69.9% are above 0.40. |
| `pct_hh_no_vehicle_cv` | NULL on 0.71% (23 rows): 13 island areas plus 10 counties whose estimate is exactly 0. |
| `pct_no_internet_cv` | NULL on 0.43% (14 rows). |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups.

So the estimates in this chunk are complete and the *reliability* of one of them is not. A national `pct_commute_transit` choropleth is drawn on 3,222 real values of which the large majority are statistically indistinguishable from each other and from zero; a national `pct_no_internet` choropleth is drawn on the same rows and is solid. Treat the two columns differently even though they live in the same file.

Margins of error at this geography are the narrowest in the catalog below state level, but they are not zero. Use the `*_cv` columns to flag or grey out unreliable values; never compare two counties without checking whether their margins overlap.

The PMTiles archive carries real county polygons at every zoom — the band is `0-10:geom`, there are few enough features to draw them all at a national zoom, so there is no coarser-geography band at coarse zooms the way the tract and block-group collections have one. `*_moe` columns are excluded from the tiles at every zoom; `*_cv` columns are kept, which is what lets a style grey out an unreliable transit share. Statistics come from the GeoParquet, always.

## Related collections

- [`counties/county-income`](../county-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`counties/county-people`](../county-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`counties/county-housing`](../county-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1. Its `households` is the denominator behind `pct_no_internet` and `pct_hh_no_vehicle`.
- [`counties/county-wellbeing`](../county-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`counties/counties`](../counties/collection.json) — the sixth sibling: all 112 columns in one wide table, same 3,235 rows, data files one directory up. Use it instead of a join when a question crosses three or more themes.
- The same theme at the other geographies: [`states/state-connectivity`](../../states/state-connectivity/collection.json), [`tracts/tract-connectivity`](../../tracts/tract-connectivity/collection.json), [`block-groups/bg-connectivity`](../../block-groups/bg-connectivity/collection.json), [`zctas/zcta-connectivity`](../../zctas/zcta-connectivity/collection.json), [`places/place-connectivity`](../../places/place-connectivity/collection.json), [`congressional-districts/cd-connectivity`](../../congressional-districts/cd-connectivity/collection.json).
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level. Different survey, different vintage, no margins of error, and no commuting or internet data at all.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

For cost: this file is 12.4 MB over 3,235 rows, most of it geometry. Nothing
here needs a filter to be affordable.

### 1. How rare is transit commuting? (the distribution first, always)

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(pct_commute_transit)                         AS published,
       round(avg(pct_commute_transit), 2)                 AS mean,
       quantile_cont(pct_commute_transit, 0.50)           AS p50,
       round(quantile_cont(pct_commute_transit, 0.99), 2) AS p99,
       max(pct_commute_transit)                           AS max,
       count(pct_commute_transit_cv)                      AS with_a_cv,
       round(100.0*count(*) FILTER (WHERE pct_commute_transit_cv > 0.40)
             / count(pct_commute_transit_cv), 1)          AS pct_cv_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet';
```

→ `3222 | 0.63 | 0.19 | 6.94 | 52.44 | 2417 | 69.9`.

The median county sends 0.19% of its commuters by transit; the 99th percentile
sends 6.94%; the maximum is 52.44%. A linear colour ramp on this column shows
one colour, which is why the `styles/` class breaks were measured from this
distribution rather than assumed. And the reliability column is the real
warning: 818 counties have no CV at all because their estimate is 0.0, and of
the 2,417 that have one, seven in ten are above 0.40.

### 2. Where transit commuting is real, gated on reliability

```sql
LOAD httpfs;
SELECT geoid, name, pct_commute_transit, round(pct_commute_transit_cv, 2) AS cv,
       pct_commute_drive_alone
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet'
WHERE pct_commute_transit_cv < 0.12
ORDER BY pct_commute_transit DESC LIMIT 6;
```

→ `36005 | Bronx County, New York | 52.44 | 0.01 | 23.53`, `36047 | Kings
County, New York | 46.5 | 0.01 | 17.6`, `36061 | New York County, New York |
43.75 | 0.01 | 5.64`, `36081 | Queens County, New York | 41.42 | 0.01 | 31.41`,
`34017 | Hudson County, New Jersey | 31.31 | 0.02 | 32.86`, `36085 | Richmond
County, New York | 23.3 | 0.02 | 51.61`.

Four New York City boroughs, then Hudson County, then Staten Island. Carrying
`pct_commute_drive_alone` alongside is a free sanity check: the two shares share
the B08301 denominator, so they must trade off, and they do — Manhattan's
transit share of 43.75% pairs with 5.64% driving alone, Staten Island's 23.3%
with 51.61%.

### 3. Connectivity against the income distribution (1:1 sibling join)

```sql
LOAD httpfs;
WITH j AS (
  SELECT ntile(5) OVER (ORDER BY i.median_hh_income) AS q,
         c.pct_work_from_home, c.pct_commute_45min_plus, c.pct_no_internet, c.pct_no_computer
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet' i
  JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet' c
    USING (geoid)
  WHERE i.median_hh_income IS NOT NULL)
SELECT q AS income_quintile, round(avg(pct_work_from_home), 1)     AS wfh,
       round(avg(pct_commute_45min_plus), 1)                       AS commute_45min_plus,
       round(avg(pct_no_internet), 1)                              AS no_internet,
       round(avg(pct_no_computer), 1)                              AS no_computer
FROM j GROUP BY 1 ORDER BY 1;
```

→

```
1 |  6.4 | 18.3 | 16.7 | 11.8
2 |  7.7 | 15.5 | 12.7 |  8.5
3 |  8.7 | 14.3 | 10.8 |  7.4
4 | 10.2 | 14.1 |  9.0 |  6.0
5 | 14.5 | 17.4 |  6.0 |  4.0
```

The join is 1:1 on `geoid` — all six county collections hold the same 3,235
rows. Working from home more than doubles across the income distribution while
households with no internet fall by nearly a factor of three: the same digital
gradient from two directions. Long commutes are **U-shaped**, highest in the
poorest quintile (18.3) and second-highest in the richest (17.4) — rural
distance at one end and metropolitan congestion at the other. Fitting a line
through that column would hide the shape.

The two commute columns have different denominators, as the field notes say, so
`wfh` and `commute_45min_plus` must not be added. And `avg()` here averages
*county* values, one county one vote, which is not a population-weighted
national figure.

### 4. Car-free households: the count and the share rank differently

```sql
LOAD httpfs;
SELECT geoid, name, hh_no_vehicle, pct_hh_no_vehicle, round(pct_hh_no_vehicle_cv, 3) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet'
ORDER BY hh_no_vehicle DESC LIMIT 5;
```

→ `36061 | New York County, New York | 607348 | 78.04 | 0.005`, `36047 | Kings
County, New York | 569113 | 56.35 | 0.005`, `17031 | Cook County, Illinois |
378260 | 18.01 | 0.009`, `36005 | Bronx County, New York | 326220 | 61.08 |
0.008`, `36081 | Queens County, New York | 314790 | 37.43 | 0.008`.

```sql
LOAD httpfs;
SELECT geoid, name, hh_no_vehicle, pct_hh_no_vehicle, round(pct_hh_no_vehicle_cv, 3) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet'
WHERE pct_hh_no_vehicle_cv < 0.15
ORDER BY pct_hh_no_vehicle DESC LIMIT 5;
```

→ `02158 | Kusilvak Census Area, Alaska | 1589 | 82.93 | 0.034`, `36061 | New
York County, New York | 607348 | 78.04 | 0.005`, `02188 | Northwest Arctic
Borough, Alaska | 1179 | 64.6 | 0.03`, `36005 | Bronx County, New York | 326220
| 61.08 | 0.008`, `02050 | Bethel Census Area, Alaska | 2784 | 57.66 | 0.035`.

Same column, two questions, two answers. By count it is Manhattan, Brooklyn and
Cook County — where car-free households are concentrated. By share the top row
is Kusilvak Census Area, Alaska, 1,589 households and 82.93% of them without a
vehicle: roadless villages, not transit-rich cities. Both are correct; neither
substitutes for the other, and "most car-free county in America" means
whichever one you say it means. The CVs are tight in both lists, so this is a
real difference in what the two columns measure rather than noise.

### 5. Which transit shares survive their own margins?

```sql
LOAD httpfs;
SELECT count(*)                                                                   AS estimate_over_5,
       count(*) FILTER (WHERE pct_commute_transit - pct_commute_transit_moe > 5)  AS significantly_over_5
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet'
WHERE pct_commute_transit > 5;
```

→ `54 | 41`.

54 counties estimate that more than one commuter in twenty takes transit; 41 of
them — 76% — hold that at the bottom of their 90% margin. `estimate - moe` is
the published interval's lower bound, so this is the Bureau's own arithmetic
rather than an added assumption. Run the identical test on
`tracts/tract-connectivity` and it returns `13118 | 6132` — only 47% of tracts
over the same threshold hold it (measured). Counties are where this kind of
threshold claim is safest in the catalog below states, and even here one in
four does not hold.

### Related recipes elsewhere

- The whole county table at once: [`counties/counties/AGENTS.md`](../counties/AGENTS.md).
- The same columns at tract scale, including the group-quarters trap where
  `population` is not a household count:
  [`tracts/tract-connectivity/AGENTS.md`](../../tracts/tract-connectivity/AGENTS.md).
- The household denominator these shares need:
  [`counties/county-housing/AGENTS.md`](../county-housing/AGENTS.md).
- Choosing between the six county collections, and stepping up or down a
  geography: [`counties/AGENTS.md`](../AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, so no test above that reads a margin of error can be reproduced from
tiles — even though, unlike the finer collections, every zoom of this archive
holds real county polygons.
