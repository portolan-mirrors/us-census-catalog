# Agent guide — Commuting & Connectivity (ZIP Code Tabulation Areas)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

**Read this before anything else: a ZCTA is not a ZIP code, and it nests in nothing.** A ZIP Code Tabulation Area is the Census Bureau's approximation of a USPS 5-digit delivery area, built by giving each 2020 census block the most common ZIP code of the addresses in it ([what a ZCTA is](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html)). Three consequences:

- `state` is **NULL on all 33,791 rows**, so `WHERE state = 'CA'` returns nothing — silently, with no error.
- The first two characters of a `geoid` are a **postal region, not a state FIPS code**: `substr(geoid, 1, 2) = '06'` returns 289 rows and **not one of them is in California** — 288 intersect Connecticut and one, `06390`, is wholly in New York (measured in [`zcta-income`](../zcta-income/AGENTS.md)). A prefix join returns *wrong* rows rather than no rows.
- Relating a ZCTA to a county, tract or state is a **spatial** operation. Recipe 5 below does it, with a `bbox` covering-struct prefilter.

And the thing that bites hardest in *this* collection: **these columns are the noisiest in the catalog at this geography.** 69.4% of the ZCTAs that publish a `pct_commute_transit_cv` are over the 0.40 "unreliable" line, 49.2% for `pct_hh_no_vehicle_cv` and 34.9% for `pct_no_internet_cv` (measured, recipe 1). `*_cv` filtering is not optional before mapping or ranking anything here.

## What this is

How people get around and get online: households with no vehicle available, as a count and a share ([B25044](https://data.census.gov/table/ACSDT5Y2024.B25044)); commute mode shares for driving alone, public transportation, walking or cycling, and working from home ([B08301](https://data.census.gov/table/ACSDT5Y2024.B08301)); the share of commutes of 45 minutes or more ([B08303](https://data.census.gov/table/ACSDT5Y2024.B08303)); and the shares of households with no internet access and no computing device ([B28002](https://data.census.gov/table/ACSDT5Y2024.B28002), [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001)).

**33,791 rows**, one per ZIP Code Tabulation Area, ACS 2020–2024 5-year estimates, geometry from the 2020 cartographic boundary files — GENZ2020 is the only cartographic ZCTA edition the Census Bureau publishes, and the 2020-based ZCTAs are the ones the ACS tabulates.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.pmtiles`, layer `zcta-connectivity`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/collection.json` — carries a full description for every column

This is a themed cut of the wide ZCTA table: the same 33,791 rows and the same geometry, 30 columns instead of 112. The wide sixth sibling is [`zctas/zctas`](../zctas/collection.json), whose own data files stay one directory up at `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zctas.parquet` (and `.pmtiles`).

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

- **`state` is NULL on every row** and `geoid` joins nothing by prefix. See the schema note above; this is the single most common way to get a wrong answer out of this collection.
- **Every estimate has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. To compare two geographies, check
  whether their margins overlap before calling a difference real. To sum
  estimates across geographies, add the margins in quadrature
  (`sqrt(sum(moe*moe))`). **Never sum or average a median**: a median of a
  region is not derivable from the medians of its parts.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate`.
  Rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over 0.40
  unreliable. At this geography these three columns are the catalog's worst:
  median CV 0.608 (`pct_commute_transit`), 0.395 (`pct_hh_no_vehicle`) and
  0.319 (`pct_no_internet`), measured. Filter or grey out by `_cv`.
- **`pct_commute_transit_cv` is NULL far more often than the estimate is.**
  32,798 ZCTAs publish the share and only 13,378 publish a CV (measured),
  because a CV is NULL wherever the estimate is 0 — and the median ZCTA's
  transit share *is* 0.0. `WHERE pct_commute_transit_cv < 0.12` therefore
  silently discards every zero-transit ZCTA; add `OR pct_commute_transit = 0`
  if you need them in the denominator.
- **A margin of exactly 0.0 is a flag to inspect, not high precision.** Five
  ZCTAs publish a non-zero `pct_commute_transit` with
  `pct_commute_transit_moe = 0.0` (measured), and the CV on those rows is 0.0,
  so they sail through any CV gate. Recipe 5 has one: 100.0% transit, 0.0%
  driving alone, margin 0.0, in a ZCTA of 195 people.
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **`pct_commute_45min_plus` divides by workers who did not work from home** (B08303's own universe), while every other commute share divides by all workers 16+ (B08301). The two denominators differ, so the shares do not sum across tables.
- **`pct_commute_transit` excludes taxi and ride-hailing** (B08301 line 16 is a separate category in this vintage), and covers bus, subway and elevated rail, light rail, commuter rail and ferryboat.
- **`pct_no_internet` counts a household that uses the internet without a
  subscription as having access** (B28002 line 12), so it is the floor of the
  digital divide rather than its full extent.
- **`hh_no_vehicle` is a count of households and `pct_hh_no_vehicle` a share
  of them.** A car-free household of four counts once. `population` is **not**
  a household count — recipe 3 is what happens when it is used as one.
- **A ZCTA's size varies enormously**: `aland_sqkm` runs from 0.004 to
  35,426.845 and `population` from 0 to 140,157, with a median of 2,656
  (measured). An unweighted mean over ZCTAs is not a national average.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population`, `hh_no_vehicle` | NULL on 0.06% of ZCTAs — the 19 rows with a 2020 cartographic boundary and no ACS tabulation. Every other column is NULL on at least those rows. |
| `pct_commute_transit` | NULL on 2.94% of ZCTAs. Published on 32,798 rows, but only 13,378 of those also publish a `_cv` (measured) — the rest estimate exactly 0. |
| `pct_no_internet` | NULL on 2.88% of ZCTAs: no households, so no denominator. |
| `pct_commute_45min_plus` | NULL on 3.14% of ZCTAs — a slightly higher rate than the other commute shares, because its universe excludes people who worked from home. |

Those 19 rows are 17 island-area ZCTAs — `00802`, `00820`, `00830`, `00840`, `00850`, `00851` (U.S. Virgin Islands), `96799` (American Samoa), `96910`, `96913`, `96915`, `96916`, `96917`, `96928`, `96929` (Guam), `96950`, `96951`, `96952` (Northern Mariana Islands) — plus `11717` and `11798` in Suffolk County, New York, measured by listing every row where `population IS NULL`. The island areas have 2020 cartographic boundaries but no ACS 5-year estimates, so they keep their geometry and publish NULL values rather than being dropped.

**598 ZCTAs (1.77%) have an ACS row with `population` exactly 0**, and **133 ZCTAs have more than 2,000 people and fewer than 100 households** (both measured). The second group is the dangerous one: it is campuses and military bases, where every household-denominated column in this collection rests on a handful of households. Recipe 3 works one of them.

Row count checked against the Census Bureau's own [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html): 33,791 ZCTAs (33,642 United States + 132 Puerto Rico + 17 island areas), which is exactly the row count here. The ACS tabulates 33,772 of them, and every one of those 33,772 matched a polygon.

Margins of error at this geography can be large relative to the estimate — larger here than in any other ZCTA theme. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap.

PMTiles coarse zooms are a different census geography from this collection's: z0–z5 are **counties**, carrying the Census Bureau's own county estimates under the same column names, and z6–z12 are the ZCTAs themselves. ZCTAs do not nest in counties, so the county band is national orientation, not a roll-up of these features. `*_moe` columns are not in the tiles at any zoom; `*_cv` columns are. Statistics come from the GeoParquet.

## Related collections

- [`zctas/zcta-income`](../zcta-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`zctas/zcta-people`](../zcta-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`zctas/zcta-housing`](../zcta-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1. **Gate household-denominated columns on its `households`.**
- [`zctas/zcta-wellbeing`](../zcta-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1. Carries `group_quarters_pop`.
- [`zctas/zctas`](../zctas/collection.json) ([agent guide](../zctas/AGENTS.md)) — the wide sixth sibling: all 112 columns, same 33,791 rows, data files one directory up.
- The same theme where GEOIDs *do* nest: [`counties/county-connectivity`](../../counties/county-connectivity/collection.json), [`states/state-connectivity`](../../states/state-connectivity/collection.json), [`tracts/tract-connectivity`](../../tracts/tract-connectivity/collection.json), [`block-groups/bg-connectivity`](../../block-groups/bg-connectivity/collection.json), [`places/place-connectivity`](../../places/place-connectivity/collection.json), [`congressional-districts/cd-connectivity`](../../congressional-districts/cd-connectivity/collection.json).
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, the geography ZCTAs are built from. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted. The
file is 69,643,472 bytes over 33,791 rows.

### 1. The distribution first, and how unreliable these columns are

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(pct_commute_transit)                         AS published,
       round(avg(pct_commute_transit), 2)                 AS mean,
       quantile_cont(pct_commute_transit, 0.50)           AS p50,
       round(quantile_cont(pct_commute_transit, 0.99), 2) AS p99,
       max(pct_commute_transit)                           AS max
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.parquet';
```

→ `32798 | 1.28 | 0.0 | 21.47 | 100.0`.

**The median ZCTA sends nobody to work by transit.** The 99th percentile sends
one commuter in five and the maximum is 100. A linear colour ramp on this
column shows one colour; this is the distribution the `styles/` class breaks
were measured from.

Now the reliability of the three `_cv` columns, side by side:

```sql
LOAD httpfs;
SELECT 'pct_commute_transit' AS col, count(pct_commute_transit_cv) AS n,
       round(quantile_cont(pct_commute_transit_cv, 0.5), 3) AS median_cv,
       round(100.0*count(*) FILTER (WHERE pct_commute_transit_cv > 0.40)
             / count(pct_commute_transit_cv), 1) AS pct_over_040
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.parquet'
UNION ALL SELECT 'pct_hh_no_vehicle', count(pct_hh_no_vehicle_cv),
       round(quantile_cont(pct_hh_no_vehicle_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE pct_hh_no_vehicle_cv > 0.40)
             / count(pct_hh_no_vehicle_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.parquet'
UNION ALL SELECT 'pct_no_internet', count(pct_no_internet_cv),
       round(quantile_cont(pct_no_internet_cv, 0.5), 3),
       round(100.0*count(*) FILTER (WHERE pct_no_internet_cv > 0.40)
             / count(pct_no_internet_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.parquet';
```

→

```
pct_commute_transit | 13378 | 0.608 | 69.4
pct_hh_no_vehicle   | 27369 | 0.395 | 49.2
pct_no_internet     | 30194 | 0.319 | 34.9
```

Read the `n` column as carefully as the rest. Only 13,378 of the 32,798 ZCTAs
with a transit share publish a CV at all, because the CV is NULL wherever the
estimate is 0 — so `WHERE pct_commute_transit_cv < 0.12` is also a filter on
"has any transit commuters". And of the ones that do publish a CV, **seven in
ten are over 0.40**. At county level the same share is 69.9% and at state level
0.0% (per the catalog's measurements): this is a column that wants a coarser
geography unless the question is specifically about a dense urban ZCTA.

### 2. Where households have no internet, reliability-gated (`*_cv`)

```sql
LOAD httpfs;
SELECT geoid, population, pct_no_internet, pct_no_internet_moe AS moe,
       round(pct_no_internet_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.parquet'
WHERE population > 2000 AND pct_no_internet_cv < 0.12
ORDER BY pct_no_internet DESC LIMIT 5;
```

→ `16256 | 2162 | 59.35 | 8.7 | 0.09`, `00670 | 8512 | 58.67 | 4.4 | 0.05`,
`00606 | 5163 | 58.49 | 6.49 | 0.07`, `44627 | 7086 | 53.35 | 6.26 | 0.07`,
`84534 | 2473 | 53.22 | 5.82 | 0.07`.

Three different kinds of place, which is the point: a spatial check against
[`states`](../../states/states/collection.json) puts `00606` and `00670` wholly
in Puerto Rico, `16256` in Pennsylvania, `44627` in Ohio and `84534` in Utah —
and `44627` is the same Ohio ZCTA that appears in the uninsured top five in
[`zcta-wellbeing`](../zcta-wellbeing/AGENTS.md). Remember what the column
measures: a household with no *subscription* that still uses the internet
counts as having access, so 59.35% is a floor.

### 3. `population` is not a household count — the campus-and-base trap

```sql
LOAD httpfs;
SELECT c.geoid, c.population, h.households, w.group_quarters_pop,
       c.pct_no_internet, c.pct_no_internet_moe AS moe, round(c.pct_no_internet_cv, 2) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.parquet' c
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet' h USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/zcta-wellbeing.parquet' w USING (geoid)
WHERE c.population > 2000 AND h.households < 100
ORDER BY c.population DESC LIMIT 8;
```

→

```
16802 | 14793 | 63 | 14718 | 12.7 |  22.77 | 1.09
01003 | 13510 | 44 | 13425 |  0.0 |  47.73 | NULL
32816 | 12624 |  0 | 12624 | NULL |   NULL | NULL
43210 | 12164 | 26 | 12115 |  0.0 |  76.92 | NULL
48825 | 11295 |  7 | 11284 |  0.0 | 257.14 | NULL
92055 | 10831 |  0 | 10831 | NULL |   NULL | NULL
13244 |  9683 | 13 |  9659 |  0.0 | 146.15 | NULL
28310 |  9583 |  0 |  9583 | NULL |   NULL | NULL
```

**133 ZCTAs nationally have over 2,000 people and under 100 households**
(measured). Every row above is a ZCTA whose population is almost entirely
`group_quarters_pop` — a university campus or a military post. `48825`
publishes `pct_no_internet = 0.0` with a margin of **±257.14 percentage
points**, which is the data telling you, in the only way it can, that seven
households is not a sample. Two of these ZCTAs have zero households, so the
share is NULL rather than misleading.

A `population` gate does not protect a household-denominated column. Gate on
`households` from [`zcta-housing`](../zcta-housing/collection.json), and treat
a margin wider than the 0–100 range as a hard reject rather than a wide
interval.

### 4. Which ZCTAs are genuinely transit-heavy? (margins, not estimates)

```sql
LOAD httpfs;
SELECT count(*)                                                                  AS estimate_over_25,
       count(*) FILTER (WHERE pct_commute_transit - pct_commute_transit_moe > 25) AS significantly_over_25
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.parquet'
WHERE pct_commute_transit > 25;
```

→ `252 | 175`.

Only 252 ZCTAs in the country estimate that a quarter of their commuters use
transit, and 175 of them — 69% — hold that at the bottom of their own 90%
margin. Three in ten of the apparent transit strongholds do not survive their
margin. `estimate - moe` is the published interval's lower bound, so this is
the Census Bureau's own arithmetic rather than an added assumption, and it is
the right screen before any "top transit ZIP codes" list.

### 5. One county's ZCTAs — spatially, and the margin-zero flag

```sql
LOAD spatial; LOAD httpfs;
WITH c AS (
  SELECT geometry, bbox
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet'
  WHERE geoid = '17031')                     -- Cook County, Illinois (Chicago)
SELECT z.geoid, z.population, z.pct_commute_transit AS transit,
       round(z.pct_commute_transit_cv, 2) AS cv, z.pct_commute_drive_alone AS drive_alone
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.parquet' z, c
WHERE z.bbox.xmin <= c.bbox.xmax AND z.bbox.xmax >= c.bbox.xmin
  AND z.bbox.ymin <= c.bbox.ymax AND z.bbox.ymax >= c.bbox.ymin
  AND ST_Area(ST_Intersection(z.geometry, c.geometry)) / ST_Area(z.geometry) > 0.5
  AND z.pct_commute_transit_cv < 0.12
ORDER BY z.pct_commute_transit DESC LIMIT 5;
```

→ `60141 | 195 | 100.0 | 0.0 | 0.0`, `60657 | 71904 | 30.38 | 0.03 | 20.86`,
`60640 | 65445 | 27.1 | 0.05 | 29.87`, `60660 | 42724 | 26.67 | 0.05 | 33.8`,
`60614 | 70693 | 26.62 | 0.04 | 26.2`.

The spatial machinery first. The `bbox`-overlap condition is a GeoParquet 1.1
covering-struct prefilter with row-group statistics behind it, so
`ST_Intersection` runs on a few hundred polygons instead of 33,791; write it as
an *intersection* test (`z.xmin <= c.xmax AND z.xmax >= c.xmin AND …`), because
containment would drop every ZCTA that only partly covers the county. The
area-share gate (`> 0.5`) is what turns "touches Cook County" into "is in Cook
County" — two generalized boundary files share border slivers, and
`ST_Intersects` alone picks them up. `substr(geoid, 1, 5)` cannot do any of
this: a ZCTA code contains no county.

Then the first row, which passed a `_cv < 0.12` gate with flying colours:

```sql
LOAD httpfs;
SELECT c.geoid, c.population, h.households, w.group_quarters_pop,
       c.pct_commute_transit, c.pct_commute_transit_moe AS moe,
       c.pct_commute_transit_cv AS cv, c.pct_commute_drive_alone, c.pct_work_from_home
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.parquet' c
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet' h USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/zcta-wellbeing.parquet' w USING (geoid)
WHERE c.geoid = '60141';
```

→ `60141 | 195 | 127 | 68 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0`.

195 people, 127 households, 68 of them in group quarters; 100.0% of commuters
on transit, 0.0% driving alone, and a margin of exactly **0.0**, which makes
the CV 0.0 and lets the row through every reliability filter. A margin of 0.0
on a 100.0% share is the ACS saying the worker universe is too small to vary,
not that it measured perfectly — and only five ZCTAs in the country publish a
non-zero transit share with a zero margin (measured). Treat `moe = 0.0` as a
flag to inspect the row, and add a worker- or household-size gate to any
ranking.

### Related recipes elsewhere

- All 112 columns at once, one row per ZCTA:
  [`zctas/zctas/AGENTS.md`](../zctas/AGENTS.md).
- The `geoid`-prefix trap measured, and the spatial state membership test:
  [`zctas/zcta-income/AGENTS.md`](../zcta-income/AGENTS.md).
- The same thin-denominator failure on the renter side:
  [`zctas/zcta-housing/AGENTS.md`](../zcta-housing/AGENTS.md).
- The same columns at a geography whose GEOIDs nest, with the car-free count
  vs share distinction:
  [`tracts/tract-connectivity/AGENTS.md`](../../tracts/tract-connectivity/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and its z0–z5 features are counties rather than ZCTAs, so nothing
above can be reproduced from tiles.
