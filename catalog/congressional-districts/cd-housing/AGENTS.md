# Agent guide — Housing & Rent (Congressional Districts, 119th Congress)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections, and the [group guide](../AGENTS.md) covers what the six congressional-district collections share; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

The housing stock and what it costs: total units and the vacancy rate ([B25002](https://data.census.gov/table/ACSDT5Y2024.B25002)), households and the owner-occupied share ([B25003](https://data.census.gov/table/ACSDT5Y2024.B25003)), median gross rent ([B25064](https://data.census.gov/table/ACSDT5Y2024.B25064)) and median owner-occupied home value ([B25077](https://data.census.gov/table/ACSDT5Y2024.B25077)), the share of renter households paying 30% and 50% or more of income on rent ([B25070](https://data.census.gov/table/ACSDT5Y2024.B25070)), the pre-1940 share ([B25034](https://data.census.gov/table/ACSDT5Y2024.B25034)) and the single-family share ([B25024](https://data.census.gov/table/ACSDT5Y2024.B25024)).

**441 rows**, one per congressional district, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

**These are the districts of the 119th Congress**, the vintage this ACS release tabulates. Three independent confirmations, two of them re-measured for this file: the release's own summary-level prefix is `5001900US` (the `19`), the cartographic boundary file is `cb_2024_us_cd119_500k` and carries `CDSESSN = '119'` on all 441 features (counted: one group, 441 rows), and the Census Bureau's [ACS geography boundaries by year](https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year/2024.html) lists "Congressional District, Delegate District DC, Resident Commissioner District PR" with the vintage "119th Congress of the United States". **District numbers are not stable across congresses.** A `geoid` here is not the same ground as the same `geoid` in an earlier congress, and a rent or home-value "change" measured against an earlier congress's district of the same number is a boundary change, not a market movement. These estimates must never be read as a time series.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/cd-housing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/cd-housing.pmtiles`, layer `cd-housing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/collection.json` — carries a full description for every column

This is a themed cut of the wide district table: the same 441 rows and the same geometry, with this theme's columns and class breaks measured on the district distribution. All 112 columns in one file are at `https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.parquet` (that file's data stayed one directory up; its metadata is in [`congressional-districts/`](../congressional-districts/collection.json)). The cut is not a download saving — over 99% of each of these files is `geometry` (99.29–99.48%, measured with `parquet_metadata`) — so choose by column set and styles, not by bytes.

## Source tables

| table | title | universe |
|---|---|---|
| [B01003](https://data.census.gov/table/ACSDT5Y2024.B01003) | Total Population | Total population |
| [B25002](https://data.census.gov/table/ACSDT5Y2024.B25002) | Occupancy Status | Housing units |
| [B25003](https://data.census.gov/table/ACSDT5Y2024.B25003) | Tenure | Occupied housing units |
| [B25024](https://data.census.gov/table/ACSDT5Y2024.B25024) | Units in Structure | Housing units |
| [B25034](https://data.census.gov/table/ACSDT5Y2024.B25034) | Year Structure Built | Housing units |
| [B25064](https://data.census.gov/table/ACSDT5Y2024.B25064) | Median Gross Rent (Dollars) | Renter-occupied housing units paying cash rent |
| [B25070](https://data.census.gov/table/ACSDT5Y2024.B25070) | Gross Rent as a Percentage of Household Income in the Past 12 Months | Renter-occupied housing units |
| [B25077](https://data.census.gov/table/ACSDT5Y2024.B25077) | Median Value (Dollars) | Owner-occupied housing units |

## Schema

`geoid` is 4 characters — state FIPS (2) + district (2) — so `substr(geoid, 1, 2)` joins [`states`](../../states/states/collection.json) and the themed [`state-housing`](../../states/state-housing/collection.json). At-large states use district `00` (AK, DE, ND, SD, VT, WY) and the non-voting delegate districts use `98`: `1198` District of Columbia, `7298` Puerto Rico, `6098` American Samoa, `6698` Guam, `6998` Northern Mariana Islands, `7898` U.S. Virgin Islands. Nothing finer joins by prefix — district boundaries follow 2020 census blocks, not counties or tracts, so relating a district to the tracts or counties inside it is a spatial operation (worked example in the [wide table's guide](../congressional-districts/AGENTS.md)).

| column | type | what it is |
|---|---|---|
| `geoid` | string | 4-character congressional district GEOID: state FIPS 2 + district 2, e.g. `0612` for California's 12th. 119th Congress. |
| `name` | string | `NAMELSAD` from the 2024 cd119 cartographic boundary file plus the state name — "Congressional District 12, California", "Delegate District (at Large), District of Columbia". |
| `state` | string | Two-letter USPS state or territory code. |
| `population` | int64 | Total population. |
| `population_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `population`. |
| `aland_sqkm` | double | Land area in km² (water excluded), 3 decimals. |
| `pop_density` | double | People per square kilometre of land area, rounded to 1 decimal: `population / aland_sqkm`. |
| `housing_units` | int64 | Total housing units, occupied and vacant. |
| `housing_units_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `housing_units`. |
| `pct_vacant_units` | double | Percent of housing units that are vacant. |
| `pct_vacant_units_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_vacant_units`. |
| `households` | int64 | Households — occupied housing units. |
| `households_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `households`. |
| `pct_owner_occupied` | double | Percent of occupied housing units that are owner-occupied. |
| `pct_owner_occupied_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_owner_occupied`. |
| `median_gross_rent` | double | Median gross rent in dollars per month — contract rent plus the estimated average monthly cost of utilities and fuels. |
| `median_gross_rent_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_gross_rent`. |
| `median_gross_rent_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_gross_rent`. |
| `pct_rent_burdened` | double | Percent of renter households paying 30% or more of household income on gross rent — the standard affordability threshold. |
| `pct_rent_burdened_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_rent_burdened`. |
| `pct_rent_burdened_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_rent_burdened`. |
| `pct_severely_rent_burdened` | double | Percent of renter households paying 50% or more of household income on gross rent. |
| `pct_severely_rent_burdened_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_severely_rent_burdened`. |
| `median_home_value` | double | Median value of owner-occupied housing units, in dollars — the owner's estimate of what the property would sell for, not an assessment or a sale price. |
| `median_home_value_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_home_value`. |
| `median_home_value_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_home_value`. |
| `pct_built_pre_1940` | double | Percent of housing units built in 1939 or earlier. |
| `pct_built_pre_1940_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_built_pre_1940`. |
| `pct_single_family` | double | Percent of housing units in single-family structures. |
| `pct_single_family_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_single_family`. |
| `geometry` | binary | Boundary polygon, WKB, EPSG:4326 / OGC:CRS84. |
| `bbox` | struct<xmin, ymin, xmax, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, with row-group statistics. |

## Field notes

- **441 rows, not 435.** The 435 voting districts plus the District of Columbia delegate district (`1198`), Puerto Rico's Resident Commissioner district (`7298`) and the four island-area delegate districts (`6098`, `6698`, `6998`, `7898`), which carry geometry but no ACS estimates. Filter `state NOT IN ('DC','PR','AS','GU','MP','VI')` for the 435 voting districts, or `population IS NOT NULL` for the 437 rows with data.
- **Three ACS district rows have no polygon and so no row here**: `09ZZ`, `17ZZ` and `33ZZ`, the water-only pseudo-districts of Connecticut, Illinois and New Hampshire. The ACS release tabulates 440 district rows (counted in the downloaded B01003 summary file); 437 of them are here, those three are not, and the four island-area delegate districts are here with no ACS row — 437 + 4 = 441. Their population is exactly 0, so nothing is lost.
- **Districts are equal-population by construction** — 546,488 to 1,021,191 across the 435 voting districts, 771,301 at the median (measured) — so every rate here has a far narrower spread than at any other geography. `pct_rent_burdened` runs from **36.9% to 66.4%** across all 437 districts with data, against 0–100 at both county and tract level (measured, recipe 2). Class breaks measured at county or tract level put almost every district in one class, which is why this collection's `styles/rent-burden.json` uses `[45, 48, 50, 55, 58, 60]`.
- **This collection is complete apart from the four no-data rows.** `median_gross_rent` and `median_home_value` are published on all 437 districts with data; for comparison the rent median is NULL on 5.92% of tracts, 23.79% of ZCTAs and 31.32% of places, and the value median on 3.55% of tracts and 10.45% of ZCTAs. The reliability is the same story: the median `median_gross_rent_cv` is 0.008 and the worst is 0.016; the median `median_home_value_cv` is 0.007 and the worst 0.026 (measured). A `_cv` gate removes nothing on these two columns.
- **`median_gross_rent` is gross rent** — contract rent plus the estimated average monthly cost of utilities and fuels — over **renter-occupied units paying cash rent** (B25064's universe). Units occupied without payment of cash rent are outside it.
- **The rent-burden columns divide by renter households *excluding* those whose rent-to-income ratio the Bureau could not compute** (B25070 line 1 minus line 11, "Not computed"). Including them would understate the burden.
- **`pct_severely_rent_burdened` is a subset of `pct_rent_burdened`**, not a separate category: 50%-or-more is inside 30%-or-more. They must never be added.
- **`median_home_value` is the owner's estimate** of what the property would sell for — not an assessment, not a sale price, and over owner-occupied units only (B25077). A ratio of it to `median_hh_income` from [`cd-income`](../cd-income/collection.json) mixes two universes (owner-occupied units against all households) and is a screening index, not a household-level statistic.
- **`housing_units` includes vacant units; `households` does not.** `households` is occupied housing units (B25003), which is the denominator for `pct_owner_occupied` and the right gate for any household-denominated column.
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
- **A NULL margin can mean "controlled, no sampling error".** `population_moe` is NULL on 18 of the 441 rows: the four island-area districts with no data at all, plus 14 whose ACS margin is the jam value `-555555555`, which `tools/build_acs.py` documents as "controlled, no sampling error". Those 14 are the eight single-district jurisdictions (AK `0200`, DE `1000`, DC `1198`, ND `3800`, SD `4600`, VT `5000`, WY `5600`, PR `7298`) plus all four Iowa districts and both West Virginia districts. No housing column is affected — every margin in this collection is published on all 437 rows with data — but read a missing margin as "not published", never as zero uncertainty.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count, and it is a person count — not a household or housing-unit count.

## Data quality

Columns with notable missingness at this geography (counted on this file, not estimated):

| column | missingness |
|---|---|
| `population` | NULL on 0.91% of districts (4 rows) — the four island-area delegate districts (American Samoa, Guam, the Northern Mariana Islands, the U.S. Virgin Islands), which have 2024 boundaries but no ACS 5-year estimates. |
| every other column in this collection, estimate and `_moe`/`_cv` alike | NULL on exactly those same four rows (0.91%). `housing_units`, `households`, `pct_vacant_units`, `pct_owner_occupied`, `median_gross_rent`, `pct_rent_burdened`, `pct_severely_rent_burdened`, `median_home_value`, `pct_built_pre_1940` and `pct_single_family` all publish on the 437 districts with data. There is no suppression in this collection. |
| `population_moe` | NULL on 4.08% of districts (18 rows): the four above plus the 14 "controlled, no sampling error" rows in the field notes. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 4 states, 13 county equivalents, 126 tracts, 405 block groups, 4 delegate districts.

The three water-only pseudo-districts the ACS tabulates — `09ZZ`, `17ZZ`, `33ZZ` — have no polygon in the cartographic boundary files and therefore no row here. A pipeline that expects every ACS district GEOID to resolve to a polygon must handle them; their population is 0.

This is the geography at which the two housing medians are most completely published anywhere in the catalog. That completeness is a property of district size, not of the housing market: an area of ~770,000 people always has enough renters and enough owners to support a median, which is exactly why the number tells you less about any particular neighbourhood.

Margins of error are the narrowest in the catalog, which is not the same as zero: recipe 5 finds 226 districts estimated above a 50% rent-burden rate and 177 that hold it at the bottom of their margin. Never compare two districts without checking whether their margins overlap, and never aggregate a median.

The PMTiles archive is real polygons at every zoom (band `0-10:geom`, from `tools/make_tiles.py`) — there are few enough districts to draw them all nationally, so there is no coarser-geography band at coarse zooms and one style classifies every zoom. `*_moe` columns are excluded from the tiles at every zoom; `*_cv` columns are kept. Statistics come from the GeoParquet, always.

## Related collections

- [`congressional-districts/cd-income`](../cd-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1. The denominator for any affordability ratio lives there.
- [`congressional-districts/cd-people`](../cd-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts/cd-connectivity`](../cd-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts/cd-wellbeing`](../cd-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`congressional-districts`](../congressional-districts/collection.json) — the sixth sibling: all 112 columns for the same 441 districts, in one table. Use it when a question crosses themes.
- The same theme at the other geographies: [`state-housing`](../../states/state-housing/collection.json), [`county-housing`](../../counties/county-housing/collection.json), [`zcta-housing`](../../zctas/zcta-housing/collection.json), [`place-housing`](../../places/place-housing/collection.json), [`tract-housing`](../../tracts/tract-housing/collection.json) and [`bg-housing`](../../block-groups/bg-housing/collection.json). Only the state join is a prefix join.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial housing-unit and occupancy counts at block level, and the geography these district lines were drawn from. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted.

For cost: 441 rows, 8,882,514 bytes on disk, of which `geometry` is about
8.8 MB. Filtering is never a cost question here; selecting `geometry` is.

### 1. What do the two housing medians look like across districts?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*) AS districts, count(median_gross_rent) AS rent_published,
       count(median_home_value)                    AS value_published,
       quantile_cont(median_gross_rent, 0.10)::int AS rent_p10,
       quantile_cont(median_gross_rent, 0.50)::int AS rent_p50,
       quantile_cont(median_gross_rent, 0.90)::int AS rent_p90,
       quantile_cont(median_home_value, 0.10)::int AS value_p10,
       quantile_cont(median_home_value, 0.50)::int AS value_p50,
       quantile_cont(median_home_value, 0.90)::int AS value_p90
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/cd-housing.parquet';
```

→ `441 | 437 | 437 | 946 | 1365 | 2036 | 184600 | 334100 | 721660`.

Both medians publish on every district that has data at all; the four missing
rows are the island-area delegate districts, not suppression. Rent spans
$946–$2,036 between the 10th and 90th percentile, home value $184,600–$721,660
— the value column is the one with real national range, and it is the one to
map if you only map one.

### 2. Why this collection ships its own class breaks

```sql
LOAD httpfs;
SELECT 'congressional district' AS geography, count(pct_rent_burdened) AS n,
       round(min(pct_rent_burdened), 1)                       AS min,
       round(quantile_cont(pct_rent_burdened, 0.10), 1)       AS p10,
       round(quantile_cont(pct_rent_burdened, 0.50), 1)       AS p50,
       round(quantile_cont(pct_rent_burdened, 0.90), 1)       AS p90,
       round(max(pct_rent_burdened), 1)                       AS max
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/cd-housing.parquet'
UNION ALL
SELECT 'county', count(pct_rent_burdened), round(min(pct_rent_burdened), 1),
       round(quantile_cont(pct_rent_burdened, 0.10), 1), round(quantile_cont(pct_rent_burdened, 0.50), 1),
       round(quantile_cont(pct_rent_burdened, 0.90), 1), round(max(pct_rent_burdened), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet'
UNION ALL
SELECT 'tract', count(pct_rent_burdened), round(min(pct_rent_burdened), 1),
       round(quantile_cont(pct_rent_burdened, 0.10), 1), round(quantile_cont(pct_rent_burdened, 0.50), 1),
       round(quantile_cont(pct_rent_burdened, 0.90), 1), round(max(pct_rent_burdened), 1)
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet';
```

→

```
congressional district |   437 | 36.9 | 43.9 | 50.2 | 58.0 |  66.4
county                 |  3222 |  0.0 | 30.9 | 44.8 | 55.6 | 100.0
tract                  | 83901 |  0.0 | 23.7 | 49.4 | 73.1 | 100.0
```

Every district in the country has between 37% and 66% of its renters paying
30% or more of income on rent. At county and tract level the same column runs
the full 0–100. A legend built on the tract distribution would colour every
district the same, so `styles/rent-burden.json` here uses
`[45, 48, 50, 55, 58, 60]` — seven classes inside a 15-point band — where
`tracts/tract-housing/styles/rent-burden.json` uses
`[25, 35, 45, 55, 70, 85]`. Measure before borrowing a threshold.

### 3. Housing cost against income (1:1 sibling join)

```sql
LOAD httpfs;
SELECT h.name, i.median_hh_income::int AS income, h.median_home_value::int AS home_value,
       round(h.median_home_value / i.median_hh_income, 1) AS value_to_income
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/cd-housing.parquet' h
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet' i
  USING (geoid)
WHERE h.median_home_value IS NOT NULL
ORDER BY value_to_income DESC LIMIT 5;
```

→ `Congressional District 34, California | 63055 | 838100 | 13.3`,
`District 30, California | 91416 | 1138500 | 12.5`,
`District 13, New York | 53573 | 660600 | 12.3`,
`District 37, California | 70327 | 852100 | 12.1`,
`District 8, New York | 66089 | 787100 | 11.9`.

Reverse the sort for the other end — `ORDER BY value_to_income LIMIT 5` gives
`District 15, Illinois | 73993 | 155600 | 2.1`,
`District 12, Illinois | 68540 | 151200 | 2.2`,
`District 17, Illinois | 59364 | 132800 | 2.2`,
`District 24, New York | 72690 | 172200 | 2.4`,
`District 34, Texas | 53104 | 125100 | 2.4`.

A factor of six between the least and most affordable district. No `_cv` gate
is needed on either column at this geography (worst CVs 0.026 and 0.021), which
is unusual — at tract level this same recipe needs both gates or it fills with
noise. The ratio mixes two universes (owner-occupied units against all
households) and is a screening index, not a household statistic.

### 4. One district against its own state, and the spread inside a state

```sql
LOAD httpfs;
SELECT d.name, d.median_gross_rent::int AS district_rent, d.median_gross_rent_moe::int AS moe,
       s.median_gross_rent::int AS state_rent,
       (d.median_gross_rent - s.median_gross_rent)::int AS gap
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/cd-housing.parquet' d
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet' s
  ON substr(d.geoid, 1, 2) = s.geoid
WHERE d.state = 'CA'
ORDER BY gap DESC LIMIT 5;
```

→ `Congressional District 17, California | 3052 | 29 | 2036 | 1016`,
`District 15 | 2849 | 40 | 2036 | 813`,
`District 47 | 2811 | 26 | 2036 | 775`,
`District 16 | 2809 | 30 | 2036 | 773`,
`District 10 | 2658 | 45 | 2036 | 622`.

`substr(geoid, 1, 2)` is the only prefix join a district has. A ±$29 margin on
a $3,052 median rent is what this geography buys. The within-state view again:

```sql
LOAD httpfs;
SELECT state, count(*) AS districts,
       min(pct_owner_occupied) AS lowest_owner_share,
       max(pct_owner_occupied) AS highest_owner_share,
       round(max(pct_owner_occupied) - min(pct_owner_occupied), 1) AS spread
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/cd-housing.parquet'
WHERE pct_owner_occupied IS NOT NULL
GROUP BY state HAVING count(*) >= 5
ORDER BY spread DESC LIMIT 5;
```

→

```
NY | 26 | 12.63 | 83.99 | 71.4
CA | 52 | 22.1  | 74.67 | 52.6
NJ | 12 | 28.11 | 79.5  | 51.4
MA |  9 | 33.65 | 76.2  | 42.6
TX | 38 | 38.04 | 75.69 | 37.7
```

One New York district is 12.6% owner-occupied and another is 84.0%, on the same
~770,000 population. The national district distribution hides that; the
within-state spread is the shape that shows it.

### 5. Is "majority rent-burdened" real? (margins, not estimates)

```sql
LOAD httpfs;
SELECT count(*)                                                              AS estimate_over_50,
       count(*) FILTER (WHERE pct_rent_burdened - pct_rent_burdened_moe > 50) AS significantly_over_50,
       round(quantile_cont(pct_rent_burdened_moe, 0.5), 2)                    AS median_moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/cd-housing.parquet'
WHERE pct_rent_burdened > 50;
```

→ `226 | 177 | 1.75`.

226 districts estimate that more than half their renters are rent-burdened and
177 of them — 78% — hold that at the bottom of their 90% interval, with a
median margin of ±1.75 percentage points. The same query at tract level returns
`40777 | 7488 | 22.05`: only 18% of the apparently majority-burdened tracts
survive their own margin, and the median tract margin is ±22 points. Same
question, same arithmetic, two very different answers about what the data can
support. `estimate - moe` is the published interval's lower bound, so this is
the Bureau's own arithmetic rather than an added assumption.

### Related recipes elsewhere

- All 112 columns on the same 441 districts, the national rank of one district,
  and the spatial recipe for what is inside it:
  [`congressional-districts`](../congressional-districts/AGENTS.md).
- The income side of every affordability ratio, the margin-overlap test on a
  state's ranking, and the class-break measurement:
  [`cd-income`](../cd-income/AGENTS.md).
- Car ownership and commuting, which track the owner/renter split closely:
  [`cd-connectivity`](../cd-connectivity/AGENTS.md).
- The same columns at tract level, where the rent median is NULL on 5.92% of
  rows and the `_cv` gates are load-bearing:
  [`tracts/tract-housing/AGENTS.md`](../../tracts/tract-housing/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive is real polygons at
every zoom (`0-10:geom`) and carries the `*_cv` columns, but no `*_moe`
columns — and it is a map artifact either way: query the GeoParquet for
numbers.
