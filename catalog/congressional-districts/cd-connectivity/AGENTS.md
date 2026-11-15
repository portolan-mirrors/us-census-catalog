# Agent guide — Commuting & Connectivity (Congressional Districts, 119th Congress)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections, and the [group guide](../AGENTS.md) covers what the six congressional-district collections share; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

How people get around and get online: households with no vehicle available, as a count and a share ([B25044](https://data.census.gov/table/ACSDT5Y2024.B25044)); commute mode shares for driving alone, public transportation, walking or cycling, and working from home ([B08301](https://data.census.gov/table/ACSDT5Y2024.B08301)); the share of commutes of 45 minutes or more ([B08303](https://data.census.gov/table/ACSDT5Y2024.B08303)); and the shares of households with no internet access and no computing device ([B28002](https://data.census.gov/table/ACSDT5Y2024.B28002), [B28001](https://data.census.gov/table/ACSDT5Y2024.B28001)).

**441 rows**, one per congressional district, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

**These are the districts of the 119th Congress**, the vintage this ACS release tabulates. Three independent confirmations, two of them re-measured for this file: the release's own summary-level prefix is `5001900US` (the `19`), the cartographic boundary file is `cb_2024_us_cd119_500k` and carries `CDSESSN = '119'` on all 441 features (counted: one group, 441 rows), and the Census Bureau's [ACS geography boundaries by year](https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year/2024.html) lists "Congressional District, Delegate District DC, Resident Commissioner District PR" with the vintage "119th Congress of the United States". **District numbers are not stable across congresses.** A `geoid` here is not the same ground as the same `geoid` in an earlier congress, so a transit or work-from-home "trend" built from two congresses' district tables is a boundary change, not a behaviour change. These estimates must never be read as a time series.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.pmtiles`, layer `cd-connectivity`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/collection.json` — carries a full description for every column

This is a themed cut of the wide district table: the same 441 rows and the same geometry, with this theme's columns and class breaks measured on the district distribution. All 112 columns in one file are at `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.parquet` (that file's data stayed one directory up; its metadata is in [`congressional-districts/`](../congressional-districts/collection.json)). The cut is not a download saving — over 99% of each of these files is `geometry` (99.29–99.48%, measured with `parquet_metadata`) — so choose by column set and styles, not by bytes.

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

`geoid` is 4 characters — state FIPS (2) + district (2) — so `substr(geoid, 1, 2)` joins [`states`](../../states/states/collection.json) and the themed [`state-connectivity`](../../states/state-connectivity/collection.json). At-large states use district `00` (AK, DE, ND, SD, VT, WY) and the non-voting delegate districts use `98`: `1198` District of Columbia, `7298` Puerto Rico, `6098` American Samoa, `6698` Guam, `6998` Northern Mariana Islands, `7898` U.S. Virgin Islands. Nothing finer joins by prefix — district boundaries follow 2020 census blocks, not counties or tracts, so relating a district to the tracts or counties inside it is a spatial operation (worked example in the [wide table's guide](../congressional-districts/AGENTS.md)).

| column | type | what it is |
|---|---|---|
| `geoid` | string | 4-character congressional district GEOID: state FIPS 2 + district 2, e.g. `0612` for California's 12th. 119th Congress. |
| `name` | string | `NAMELSAD` from the 2024 cd119 cartographic boundary file plus the state name — "Congressional District 12, California", "Delegate District (at Large), District of Columbia". |
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

- **441 rows, not 435.** The 435 voting districts plus the District of Columbia delegate district (`1198`), Puerto Rico's Resident Commissioner district (`7298`) and the four island-area delegate districts (`6098`, `6698`, `6998`, `7898`), which carry geometry but no ACS estimates. Filter `state NOT IN ('DC','PR','AS','GU','MP','VI')` for the 435 voting districts, or `population IS NOT NULL` for the 437 rows with data.
- **Three ACS district rows have no polygon and so no row here**: `09ZZ`, `17ZZ` and `33ZZ`, the water-only pseudo-districts of Connecticut, Illinois and New Hampshire. The ACS release tabulates 440 district rows (counted in the downloaded B01003 summary file); 437 of them are here, those three are not, and the four island-area delegate districts are here with no ACS row — 437 + 4 = 441. Their population is exactly 0, so nothing is lost.
- **Districts are equal-population by construction** — 546,488 to 1,021,191 across the 435 voting districts, 771,301 at the median (measured) — so every share here has a far narrower spread than at any other geography, and class breaks borrowed from county or tract work will put almost every district in one class. `pct_no_internet` has breaks of `[4, 5.5, 7, 8.5, 10]` in this collection's `styles/default.json`, measured on the district distribution.
- **`pct_commute_transit` is the one column here where `_cv` still matters.** Its median CV is 0.101 and 176 of the 437 districts with data are above the 0.12 reliability line, though none is above 0.40 and the worst is 0.304 (measured, recipe 2). Every other `_cv` column in this collection — `pct_hh_no_vehicle_cv`, `pct_no_internet_cv` — is under 0.12 on every single district. At county level 69.9% of the transit CVs are over 0.40, so the habit is worth keeping even where it stops biting.
- **`transit-commute` is the one style deliberately *not* re-measured here.** `tools/make_styles.py` keeps "the catalog-wide [0.5, 2, 5, 10, 25] scale at every level where no class comes out empty, so a transit map reads the same from block groups to congressional districts". The other three styles in this collection use district-measured breaks.
- **`pct_commute_45min_plus` divides by workers who did not work from home** (B08303's own universe), while every other commute share divides by all workers 16+ (B08301). The two denominators differ, so the shares do not sum across tables.
- **The B08301 mode shares do not sum to 100** even among themselves: drive-alone, transit, walk-or-bike and work-from-home are four of the table's categories, and carpooling, taxis, motorcycles and "other means" are not published here.
- **`hh_no_vehicle` is a household count and `pct_hh_no_vehicle` its share of occupied housing units** (B25044) — not of people, and not of housing units including vacancies. `households` lives in [`cd-housing`](../cd-housing/collection.json) if you need the denominator explicitly.
- **`pct_no_internet` and `pct_no_computer` are household shares** (B28002, B28001). "No internet access of any kind" includes households with a computer and no subscription.
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
- **A NULL margin can mean "controlled, no sampling error".** `population_moe` is NULL on 18 of the 441 rows: the four island-area districts with no data at all, plus 14 whose ACS margin is the jam value `-555555555`, which `tools/build_acs.py` documents as "controlled, no sampling error". Those 14 are the eight single-district jurisdictions (AK `0200`, DE `1000`, DC `1198`, ND `3800`, SD `4600`, VT `5000`, WY `5600`, PR `7298`) plus all four Iowa districts and both West Virginia districts. No connectivity column is affected — every margin in this collection is published on all 437 rows with data — but read a missing margin as "not published", never as zero uncertainty.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count, and it is a person count — so it is not a safe gate for a
  household-denominated column.

## Data quality

Columns with notable missingness at this geography (counted on this file, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.91% of districts (4 rows) — the four island-area delegate districts (American Samoa, Guam, the Northern Mariana Islands, the U.S. Virgin Islands), which have 2024 boundaries but no ACS 5-year estimates. |
| every other column in this collection, estimate and `_moe`/`_cv` alike | NULL on exactly those same four rows (0.91%). `hh_no_vehicle`, all five commute-mode and travel-time shares, `pct_no_internet` and `pct_no_computer` publish on all 437 districts with data. There is no suppression in this collection. |
| `population_moe` | NULL on 4.08% of districts (18 rows): the four above plus the 14 "controlled, no sampling error" rows in the field notes. |

Note what that means for `pct_commute_transit` in particular: it publishes a value on all 437 districts and a CV on all 437, where at county level only 2,417 of 3,235 counties publish a transit CV at all and at tract level only 43,264 of 85,184 (measured in recipe 2) — a district always has enough transit commuters to estimate.

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 4 delegate districts.

The three water-only pseudo-districts the ACS tabulates — `09ZZ`, `17ZZ`, `33ZZ` — have no polygon in the cartographic boundary files and therefore no row here. A pipeline that expects every ACS district GEOID to resolve to a polygon must handle them; their population is 0.

Margins of error are the narrowest in the catalog, which is not the same as zero: `pct_commute_transit` is the column to watch, because a district with almost no transit has a small estimate and a relatively large margin. Never compare two districts without checking whether their margins overlap.

The PMTiles archive is real polygons at every zoom (band `0-10:geom`, from `tools/make_tiles.py`) — there are few enough districts to draw them all nationally, so there is no coarser-geography band at coarse zooms and one style classifies every zoom. `*_moe` columns are excluded from the tiles at every zoom; `*_cv` columns are kept. Statistics come from the GeoParquet, always.

## Related collections

- [`congressional-districts/cd-income`](../cd-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts/cd-people`](../cd-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts/cd-housing`](../cd-housing/collection.json) — Housing & Rent, same geography. Same `geoid`, joins 1:1. `households` is there, and it is the denominator behind the household shares here.
- [`congressional-districts/cd-wellbeing`](../cd-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts`](../congressional-districts/collection.json) — the sixth sibling: all 112 columns for the same 441 districts, in one table. Use it when a question crosses themes.
- The same theme at the other geographies: [`state-connectivity`](../../states/state-connectivity/collection.json), [`county-connectivity`](../../counties/county-connectivity/collection.json), [`zcta-connectivity`](../../zctas/zcta-connectivity/collection.json), [`place-connectivity`](../../places/place-connectivity/collection.json), [`tract-connectivity`](../../tracts/tract-connectivity/collection.json) and [`bg-connectivity`](../../block-groups/bg-connectivity/collection.json). Only the state join is a prefix join.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, the geography these district lines were drawn from. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

For cost: 441 rows, 8,880,200 bytes on disk, of which `geometry` is about
8.8 MB. Filtering is never a cost question here; selecting `geometry` is.

### 1. How rare is transit commuting? (the distribution first, always)

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(pct_commute_transit)                         AS published,
       round(avg(pct_commute_transit), 2)                 AS mean,
       round(quantile_cont(pct_commute_transit, 0.50), 2) AS p50,
       round(quantile_cont(pct_commute_transit, 0.90), 2) AS p90,
       round(quantile_cont(pct_commute_transit, 0.99), 2) AS p99,
       max(pct_commute_transit)                           AS max
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet';
```

→ `437 | 3.23 | 0.94 | 6.86 | 48.09 | 56.94`.

The median district sends under one commuter in a hundred by public transport,
the 99th percentile sends nearly half, and the maximum is 56.94%. Averaging
~770,000 people per district does **not** normalise this column — it is as
skewed here as anywhere, which is why the catalog's shared transit breaks
`[0.5, 2, 5, 10, 25]` still work at this geography. The top of the list:

```sql
LOAD httpfs;
SELECT geoid, name, pct_commute_transit, round(pct_commute_transit_cv, 3) AS cv,
       pct_commute_drive_alone, pct_hh_no_vehicle
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet'
ORDER BY pct_commute_transit DESC LIMIT 5;
```

→ `3613 | Congressional District 13, New York | 56.94 | 0.011 | 9.31 | 76.1`,
`3615 | District 15, New York | 53.71 | 0.012 | 21.7 | 64.29`,
`3614 | District 14, New York | 49.61 | 0.011 | 24.13 | 51.63`,
`3607 | District 7, New York | 48.65 | 0.011 | 14.63 | 60.73`,
`3609 | District 9, New York | 48.61 | 0.01 | 20.11 | 55.39`.

All five are New York City districts, and no reliability gate was needed to get
a clean list. Carrying `pct_commute_drive_alone` alongside is a free sanity
check: the two shares have the same B08301 denominator, so they must trade off,
and they do — 9.31% drive alone in NY-13, where 76.1% of households have no
car at all.

### 2. Where `_cv` still bites, and where it does not

```sql
LOAD httpfs;
SELECT 'congressional district' AS geography, count(pct_commute_transit_cv) AS publishes_cv,
       round(quantile_cont(pct_commute_transit_cv, 0.5), 3) AS median_cv,
       round(max(pct_commute_transit_cv), 3)                AS max_cv,
       round(100.0*count(*) FILTER (WHERE pct_commute_transit_cv > 0.40)
             / count(pct_commute_transit_cv), 1)            AS pct_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet'
UNION ALL
SELECT 'county', count(pct_commute_transit_cv), round(quantile_cont(pct_commute_transit_cv, 0.5), 3),
       round(max(pct_commute_transit_cv), 3),
       round(100.0*count(*) FILTER (WHERE pct_commute_transit_cv > 0.40) / count(pct_commute_transit_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet'
UNION ALL
SELECT 'tract', count(pct_commute_transit_cv), round(quantile_cont(pct_commute_transit_cv, 0.5), 3),
       round(max(pct_commute_transit_cv), 3),
       round(100.0*count(*) FILTER (WHERE pct_commute_transit_cv > 0.40) / count(pct_commute_transit_cv), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.parquet';
```

→

```
congressional district |   437 | 0.101 | 0.304  |  0.0
county                 |  2417 | 0.608 | 9.119  | 69.9
tract                  | 43264 | 0.685 | 18.997 | 79.2
```

Not one district's transit share is unreliable; seven counties in ten and four
tracts in five are. Note the `publishes_cv` column too: a CV needs a non-zero
estimate, so 2,417 of 3,235 counties and 43,264 of 85,184 tracts publish one at
all, against 437 of 437 districts. Inside this collection the same comparison
across columns:

```sql
LOAD httpfs;
SELECT 'pct_commute_transit' AS column, round(quantile_cont(pct_commute_transit_cv, 0.5), 3) AS median_cv,
       round(max(pct_commute_transit_cv), 3) AS max_cv,
       count(*) FILTER (WHERE pct_commute_transit_cv > 0.12) AS over_0_12
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet'
UNION ALL
SELECT 'pct_hh_no_vehicle', round(quantile_cont(pct_hh_no_vehicle_cv, 0.5), 3), round(max(pct_hh_no_vehicle_cv), 3),
       count(*) FILTER (WHERE pct_hh_no_vehicle_cv > 0.12)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet'
UNION ALL
SELECT 'pct_no_internet', round(quantile_cont(pct_no_internet_cv, 0.5), 3), round(max(pct_no_internet_cv), 3),
       count(*) FILTER (WHERE pct_no_internet_cv > 0.12)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet';
```

→

```
pct_commute_transit | 0.101 | 0.304 | 176
pct_hh_no_vehicle   | 0.039 | 0.08  |   0
pct_no_internet     | 0.039 | 0.089 |   0
```

176 districts carry a transit CV above 0.12 and none above 0.40; no district
exceeds 0.12 on either of the other two. So gate on `pct_commute_transit_cv`
when transit is the subject, and do not bother on the rest.

### 3. One district against its own state, and the spread inside a state

```sql
LOAD httpfs;
SELECT d.name, d.pct_hh_no_vehicle AS district_no_vehicle,
       d.hh_no_vehicle            AS households_no_vehicle,
       s.pct_hh_no_vehicle        AS state_no_vehicle,
       round(d.pct_hh_no_vehicle - s.pct_hh_no_vehicle, 1) AS gap
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet' d
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-connectivity/state-connectivity.parquet' s
  ON substr(d.geoid, 1, 2) = s.geoid
WHERE d.state = 'IL'
ORDER BY gap DESC LIMIT 5;
```

→ `Congressional District 7, Illinois | 29.2 | 97473 | 10.97 | 18.2`,
`District 5 | 19.74 | 66599 | 10.97 | 8.8`,
`District 1 | 18.24 | 53922 | 10.97 | 7.3`,
`District 9 | 17.71 | 54692 | 10.97 | 6.7`,
`District 2 | 13.16 | 38771 | 10.97 | 2.2`.

`substr(geoid, 1, 2)` is the only prefix join a district has. Carrying the
count beside the share is the point: IL-7 has 97,473 car-free households,
nearly three times the state rate, and the count is what a transit or service
question actually needs. Within-state spread of internet access:

```sql
LOAD httpfs;
SELECT state, count(*) AS districts, min(pct_no_internet) AS lowest,
       max(pct_no_internet) AS highest,
       round(max(pct_no_internet) - min(pct_no_internet), 1) AS spread
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet'
WHERE pct_no_internet IS NOT NULL
GROUP BY state HAVING count(*) >= 5
ORDER BY spread DESC LIMIT 5;
```

→

```
VA | 11 | 1.33 | 13.63 | 12.3
GA | 14 | 2.43 | 13.1  | 10.7
NC | 14 | 2.98 | 13.26 | 10.3
TX | 38 | 2.44 | 11.42 |  9.0
AZ |  9 | 2.75 | 11.32 |  8.6
```

One Virginia district has 1.33% of households offline and another 13.63% — a
tenfold difference between two equal-population districts in the same state.

### 4. Connectivity across the income distribution (1:1 sibling join)

```sql
LOAD httpfs;
WITH j AS (
  SELECT ntile(5) OVER (ORDER BY i.median_hh_income) AS q,
         c.pct_no_internet, c.pct_no_computer, c.pct_work_from_home, c.pct_commute_45min_plus
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet' i
  JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet' c
    USING (geoid)
  WHERE i.median_hh_income IS NOT NULL)
SELECT q AS income_quintile, round(avg(pct_no_internet), 1) AS no_internet,
       round(avg(pct_no_computer), 1) AS no_computer,
       round(avg(pct_work_from_home), 1) AS wfh,
       round(avg(pct_commute_45min_plus), 1) AS commute_45min_plus
FROM j GROUP BY 1 ORDER BY 1;
```

→

```
1 | 9.8 | 6.6 |  9.9 | 15.1
2 | 7.8 | 5.4 | 11.8 | 13.6
3 | 6.1 | 4.2 | 14.2 | 16.1
4 | 4.9 | 3.5 | 16.4 | 18.0
5 | 3.8 | 2.8 | 21.6 | 20.4
```

The join is 1:1 on `geoid` — all six district collections hold the same 441
rows. Working from home doubles across the income distribution while households
without internet fall by more than half: the same gradient from two directions.
Long commutes rise with income, which surprises people and is a real feature of
these estimates. One caveat the table hides: `pct_commute_45min_plus` divides by
workers who did **not** work from home (B08303's universe) while
`pct_work_from_home` divides by all workers 16+ (B08301), so those two columns
do not share a denominator and must not be added.

### 5. Which districts are genuinely transit-heavy? (margins, not estimates)

```sql
LOAD httpfs;
SELECT count(*)                                                                    AS estimate_over_25,
       count(*) FILTER (WHERE pct_commute_transit - pct_commute_transit_moe > 25)   AS significantly_over_25
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet'
WHERE pct_commute_transit > 25;
```

→ `12 | 12`.

Twelve districts estimate at least a quarter of commuters on public transport,
and all twelve hold that at the bottom of their 90% margin. The identical query
at tract level returns `2882 | 1716` — two in five of the apparent transit
strongholds there do not survive their own margin. This is what equal-population
geography buys: the ranking is short, and it is solid. `estimate - moe` is the
published interval's lower bound, so this is the Bureau's own arithmetic rather
than an added assumption.

### Related recipes elsewhere

- All 112 columns on the same 441 districts, the national rank of one district,
  and the spatial recipe for what is inside it:
  [`congressional-districts`](../congressional-districts/AGENTS.md).
- The income distribution these quintiles came from, and the margin-overlap test
  on a state's ranking: [`cd-income`](../cd-income/AGENTS.md).
- `households`, the denominator behind every household share here, and the
  owner/renter split that tracks car ownership:
  [`cd-housing`](../cd-housing/AGENTS.md).
- The same columns at tract level, where a dormitory tract can report 100% with
  a margin of 0.0 and the `households` gate is essential:
  [`tracts/tract-connectivity/AGENTS.md`](../../tracts/tract-connectivity/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive is real polygons at
every zoom (`0-10:geom`) and carries the `*_cv` columns recipe 2 reads, but no
`*_moe` columns — and it is a map artifact either way: query the GeoParquet for
numbers.
