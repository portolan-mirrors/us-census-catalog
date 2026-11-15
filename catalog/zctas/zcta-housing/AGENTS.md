# Agent guide — Housing & Rent (ZIP Code Tabulation Areas)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

**Read this before anything else: a ZCTA is not a ZIP code, and it nests in nothing.** A ZIP Code Tabulation Area is the Census Bureau's approximation of a USPS 5-digit delivery area, built by giving each 2020 census block the most common ZIP code of the addresses in it ([what a ZCTA is](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html)). Three consequences:

- `state` is **NULL on all 33,791 rows**, so `WHERE state = 'CA'` returns nothing — silently, with no error.
- The first two characters of a `geoid` are a **postal region, not a state FIPS code**: `substr(geoid, 1, 2) = '06'` returns 289 rows and **not one of them is in California** — 288 intersect Connecticut and one, `06390`, is wholly in New York (measured in [`zcta-income`](../zcta-income/AGENTS.md)). A prefix join returns *wrong* rows rather than no rows.
- Relating a ZCTA to a county, tract or state is a **spatial** operation. Recipe 4 below does it, with a `bbox` covering-struct prefilter.

And the thing that bites hardest in *this* collection: **the medians thin out**. `median_gross_rent` is NULL on 23.79% of ZCTAs, `median_home_value` on 10.45% and `pct_rent_burdened` on 10.96%. Recipe 1 measures where those holes are, and they are not where an uninformed map would put them.

## What this is

The housing stock and what it costs: total units and the vacancy rate ([B25002](https://data.census.gov/table/ACSDT5Y2024.B25002)), households and the owner-occupied share ([B25003](https://data.census.gov/table/ACSDT5Y2024.B25003)), median gross rent ([B25064](https://data.census.gov/table/ACSDT5Y2024.B25064)) and median owner-occupied home value ([B25077](https://data.census.gov/table/ACSDT5Y2024.B25077)), the share of renter households paying 30% and 50% or more of income on rent ([B25070](https://data.census.gov/table/ACSDT5Y2024.B25070)), the pre-1940 share ([B25034](https://data.census.gov/table/ACSDT5Y2024.B25034)) and the single-family share ([B25024](https://data.census.gov/table/ACSDT5Y2024.B25024)).

**33,791 rows**, one per ZIP Code Tabulation Area, ACS 2020–2024 5-year estimates, geometry from the 2020 cartographic boundary files — GENZ2020 is the only cartographic ZCTA edition the Census Bureau publishes, and the 2020-based ZCTAs are the ones the ACS tabulates.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.pmtiles`, layer `zcta-housing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/collection.json` — carries a full description for every column

This is a themed cut of the wide ZCTA table: the same 33,791 rows and the same geometry, 32 columns instead of 112. The wide sixth sibling is [`zctas/zctas`](../zctas/collection.json), whose own data files stay one directory up at `https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zctas.parquet` (and `.pmtiles`).

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
| `housing_units` | int64 | Total housing units, occupied and vacant. |
| `housing_units_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `housing_units`. |
| `pct_vacant_units` | double | Percent of housing units that are vacant. |
| `pct_vacant_units_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_vacant_units`. |
| `households` | int64 | Households — occupied housing units. |
| `households_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `households`. |
| `pct_owner_occupied` | double | Percent of occupied housing units that are owner-occupied. |
| `pct_owner_occupied_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_owner_occupied`. |
| `median_gross_rent` | NULL on 23.79% of ZCTAs: few renter households paying cash rent, no publishable median. |
| `median_gross_rent_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_gross_rent`. |
| `median_gross_rent_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_gross_rent`. |
| `pct_rent_burdened` | NULL on 10.96% of ZCTAs, where the computable-ratio denominator came out at or below 0. |
| `pct_rent_burdened_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_rent_burdened`. |
| `pct_rent_burdened_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `pct_rent_burdened`. |
| `pct_severely_rent_burdened` | double | Percent of renter households paying 50% or more of household income on gross rent. |
| `pct_severely_rent_burdened_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_severely_rent_burdened`. |
| `median_home_value` | NULL on 10.45% of ZCTAs. |
| `median_home_value_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `median_home_value`. |
| `median_home_value_cv` | double | Coefficient of variation, `moe / 1.645 / estimate`: under 0.12 reliable, 0.12–0.40 caution, over 0.40 unreliable. For `median_home_value`. |
| `pct_built_pre_1940` | double | Percent of housing units built in 1939 or earlier. |
| `pct_built_pre_1940_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_built_pre_1940`. |
| `pct_single_family` | double | Percent of housing units in single-family structures. |
| `pct_single_family_moe` | double | Margin of error, 90% confidence (the level the Bureau publishes). For `pct_single_family`. |
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
  unreliable. Filtering or greying out by CV is the intended use, and at this
  geography it is not optional for `pct_rent_burdened`: its median CV is
  **0.242** and **35.3%** of the ZCTAs that publish one are over 0.40
  (measured, recipe 3).
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale.
- **`median_gross_rent`'s universe is renter-occupied units *paying cash
  rent***, so units occupied rent-free are outside it. A ZCTA of 2,000
  owner-occupied households and 60 renters has a rent median built on those
  60 — gating on `households` does **not** protect a renter-denominated
  column. Recipe 3 shows exactly that failure.
- **The rent-burden columns divide by renter households *excluding* those whose rent-to-income ratio the Bureau could not compute** (B25070 line 1 minus line 11, "Not computed"). Including them would understate the burden.
- **`pct_vacant_units` counts for-sale, for-rent, seasonal and migrant-worker
  units as vacant**, so it is not a measure of abandonment. In a resort or
  second-home ZCTA it is mostly seasonal.
- **`median_home_value` is the owner's own estimate** of what the property
  would sell for — not an assessment and not a sale price — and it is
  **top-coded upstream at $2,000,001**. `median_hh_income` in
  [`zcta-income`](../zcta-income/collection.json) is top-coded at $250,001.
  Those are published values, not jam codes; `90210` sits on the home-value
  ceiling (measured, recipe 2).
- **A ZCTA's size varies enormously**: `aland_sqkm` runs from 0.004 to
  35,426.845 and `population` from 0 to 140,157, with a median of 2,656
  (measured). An unweighted mean over ZCTAs is not a national average.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count, and it is not a household count.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population`, `housing_units`, `households` | NULL on 0.06% of ZCTAs — the 19 rows with a 2020 cartographic boundary and no ACS tabulation. Every other column is NULL on at least those rows. |
| `median_gross_rent` | **NULL on 23.79% of ZCTAs** — nearly a quarter. Few renter households paying cash rent, no publishable median. For comparison: 5.92% of tracts, 29.68% of block groups, 0.62% of counties. |
| `median_home_value` | NULL on 10.45% of ZCTAs (3.55% of tracts, 10.03% of block groups, 0.56% of counties). |
| `pct_rent_burdened` | NULL on 10.96% of ZCTAs, where the computable-ratio denominator came out at or below 0. |
| `pct_vacant_units` | NULL on 2.46% of ZCTAs. |

Those 19 rows are 17 island-area ZCTAs — `00802`, `00820`, `00830`, `00840`, `00850`, `00851` (U.S. Virgin Islands), `96799` (American Samoa), `96910`, `96913`, `96915`, `96916`, `96917`, `96928`, `96929` (Guam), `96950`, `96951`, `96952` (Northern Mariana Islands) — plus `11717` and `11798` in Suffolk County, New York, measured by listing every row where `population IS NULL`. The island areas have 2020 cartographic boundaries but no ACS 5-year estimates, so they keep their geometry and publish NULL values rather than being dropped.

**598 ZCTAs (1.77%) have an ACS row with `population` exactly 0** (measured), and every one of them is NULL for both medians.

Row count checked against the Census Bureau's own [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html): 33,791 ZCTAs (33,642 United States + 132 Puerto Rico + 17 island areas), which is exactly the row count here. The ACS tabulates 33,772 of them, and every one of those 33,772 matched a polygon.

Margins of error at this geography can be large relative to the estimate. Use the `*_cv` columns to flag or grey out unreliable values; never compare two geographies without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: z0–z5 are **counties**, carrying the Census Bureau's own county estimates under the same column names, and z6–z12 are the ZCTAs themselves. ZCTAs do not nest in counties, so the county band is national orientation, not a roll-up of these features. `*_moe` columns are not in the tiles at any zoom; `*_cv` columns are. Statistics come from the GeoParquet.

## Related collections

- [`zctas/zcta-income`](../zcta-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1.
- [`zctas/zcta-people`](../zcta-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`zctas/zcta-connectivity`](../zcta-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`zctas/zcta-wellbeing`](../zcta-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`zctas/zctas`](../zctas/collection.json) ([agent guide](../zctas/AGENTS.md)) — the wide sixth sibling: all 112 columns, same 33,791 rows, data files one directory up.
- The same theme where GEOIDs *do* nest: [`counties/county-housing`](../../counties/county-housing/collection.json), [`states/state-housing`](../../states/state-housing/collection.json), [`tracts/tract-housing`](../../tracts/tract-housing/collection.json), [`block-groups/bg-housing`](../../block-groups/bg-housing/collection.json), [`places/place-housing`](../../places/place-housing/collection.json), [`congressional-districts/cd-housing`](../../congressional-districts/cd-housing/collection.json).
- [`blocks`](../../blocks/collection.json) — 2020 Decennial counts at block level, the geography ZCTAs are built from. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted. The
file is 69,944,559 bytes over 33,791 rows.

### 1. Where are the missing rent medians? (do this before mapping rent)

```sql
INSTALL httpfs; LOAD httpfs;
SELECT CASE WHEN population IS NULL     THEN 'no ACS row'
            WHEN population = 0         THEN '0'
            WHEN population < 500       THEN '1-499'
            WHEN population < 2000      THEN '500-1,999'
            WHEN population < 10000     THEN '2,000-9,999'
            ELSE '10,000+' END AS pop_band,
       count(*) AS zctas,
       round(100.0*(count(*)-count(median_gross_rent))/count(*), 1) AS pct_rent_null,
       round(100.0*(count(*)-count(median_home_value))/count(*), 1) AS pct_value_null
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet'
GROUP BY 1 ORDER BY min(coalesce(population, -1));
```

→

```
no ACS row    |   19 | 100.0 | 100.0
0             |  598 | 100.0 | 100.0
1-499         | 6577 |  73.6 |  33.5
500-1,999     | 7941 |  26.7 |   5.9
2,000-9,999   | 8781 |   5.2 |   2.5
10,000+       | 9875 |   0.1 |   0.2
```

The headline 23.79% of ZCTAs with no rent median is almost entirely a story
about small ZCTAs: **73.6%** of ZCTAs under 500 people have no rent median
against **0.1%** of those over 10,000. A national choropleth of
`median_gross_rent` is therefore a map with rural holes, and those holes carry
no information about rent — they are a sample-size artefact. Either gate on
`population`, or draw the NULLs explicitly as "not published" in a colour that
is not on the rent ramp.

### 2. Housing cost for a list of ZIP codes

```sql
LOAD httpfs;
SELECT geoid, households, median_gross_rent::int AS rent,
       round(median_gross_rent_cv, 2) AS rent_cv,
       median_home_value::int AS value, pct_rent_burdened AS burdened
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet'
WHERE geoid IN ('90210', '10001', '60614', '00601', '99501')
ORDER BY rent DESC NULLS LAST;
```

→ `10001 | 15737 | 3361 | 0.05 | 561100 | 40.31`, `90210 | 8029 | 3251 | 0.04 |
2000001 | 61.76`, `60614 | 35386 | 2030 | 0.02 | 720400 | 38.81`, `99501 | 7610
| 1254 | 0.04 | 379100 | 42.49`, `00601 | 5768 | 427 | 0.03 | 94200 | 49.5`.

`90210`'s `median_home_value` of **2000001** is the upstream top code, not a
measurement: any ZCTA whose owner-occupied median exceeds $2,000,000 reports
exactly this number, so Beverly Hills cannot be ranked against another ZCTA at
the ceiling. Report it as "$2,000,001 (top-coded)". An `IN` list of *n* ZIP
codes can also return fewer than *n* rows: PO-box-only and point ZIPs have no
ZCTA, and that shortfall is not missing data.

### 3. Rent burden, and why a `households` gate is not enough (`*_cv`)

```sql
LOAD httpfs;
SELECT count(pct_rent_burdened_cv) AS publishes_cv,
       round(quantile_cont(pct_rent_burdened_cv, 0.5), 3) AS median_cv,
       round(100.0*count(*) FILTER (WHERE pct_rent_burdened_cv > 0.40)
             / count(pct_rent_burdened_cv), 1) AS pct_unreliable
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet';
```

→ `27544 | 0.242 | 35.3`.

The median ZCTA's rent-burden share has a coefficient of variation of 0.242 —
inside "use with caution" — and more than a third of them are outright
unreliable. So gate, hard:

```sql
LOAD httpfs;
SELECT geoid, households, pct_rent_burdened AS burdened,
       round(pct_rent_burdened_cv, 2) AS cv, median_gross_rent::int AS rent
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet'
WHERE households > 2000 AND pct_rent_burdened_cv < 0.10
ORDER BY pct_rent_burdened DESC LIMIT 5;
```

→ `21104 | 2097 | 100.0 | 0.1 | 1384`, `02814 | 2980 | 95.95 | 0.08 | 970`,
`23009 | 3099 | 92.23 | 0.05 | 1197`, `18324 | 3962 | 91.24 | 0.05 | 1873`,
`32603 | 2694 | 89.42 | 0.03 | 1235`.

The first row still fails, and the reason is the lesson. `21104` has 2,097
households — past the gate — but:

```sql
LOAD httpfs;
SELECT geoid, households, pct_owner_occupied,
       round(households*(100-pct_owner_occupied)/100)::int AS renter_hh_approx,
       pct_rent_burdened, pct_rent_burdened_moe, median_gross_rent, median_gross_rent_moe
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet'
WHERE geoid IN ('21104', '02814');
```

→ `21104 | 2097 | 97.04 | 62 | 100.0 | 15.55 | 1384.0 | 919.0`, `02814 | 2980 |
91.88 | 242 | 95.95 | 12.45 | 970.0 | 449.0`.

`21104` is 97.04% owner-occupied: roughly **62 renter households**, all of them
apparently cost-burdened, with a ±15.55-point margin and a rent median of
$1,384 ± $919. "100% of renters here are rent-burdened" is a sentence about
62 households. `households` is the wrong denominator for every column in this
collection whose universe is renters — gate on `pct_owner_occupied` too, or on
`median_gross_rent_cv`, and read a `_cv` of 0.1 on a share of 100.0 as
arithmetic rather than confirmation.

### 4. One county's ZCTAs — spatially, because prefixes cannot

```sql
LOAD spatial; LOAD httpfs;
WITH c AS (
  SELECT geometry, bbox
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet'
  WHERE geoid = '48453')                     -- Travis County, Texas (Austin)
SELECT z.geoid, z.households, z.median_gross_rent::int AS rent,
       round(z.median_gross_rent_cv, 2) AS cv, z.pct_rent_burdened AS burdened
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet' z, c
WHERE z.bbox.xmin <= c.bbox.xmax AND z.bbox.xmax >= c.bbox.xmin
  AND z.bbox.ymin <= c.bbox.ymax AND z.bbox.ymax >= c.bbox.ymin
  AND ST_Area(ST_Intersection(z.geometry, c.geometry)) / ST_Area(z.geometry) > 0.5
  AND z.median_gross_rent_cv < 0.15
ORDER BY z.median_gross_rent DESC LIMIT 5;
```

→ `78739 | 7090 | 3473 | 0.06 | 7.98`, `78701 | 7949 | 2759 | 0.03 | 30.27`,
`78652 | 1869 | 2666 | 0.02 | 46.69`, `78725 | 4349 | 2232 | 0.04 | 29.92`,
`78703 | 11375 | 2181 | 0.04 | 38.53`.

And the membership arithmetic behind it:

```sql
LOAD spatial; LOAD httpfs;
WITH c AS (
  SELECT geometry, bbox
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet'
  WHERE geoid = '48453'),
cand AS (
  SELECT z.geoid, z.median_gross_rent,
         ST_Area(ST_Intersection(z.geometry, c.geometry)) / ST_Area(z.geometry) AS frac
  FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet' z, c
  WHERE z.bbox.xmin <= c.bbox.xmax AND z.bbox.xmax >= c.bbox.xmin
    AND z.bbox.ymin <= c.bbox.ymax AND z.bbox.ymax >= c.bbox.ymin
    AND ST_Intersects(z.geometry, c.geometry))
SELECT count(*)                                              AS intersecting,
       count(*) FILTER (WHERE frac > 0.5)                    AS majority,
       count(*) FILTER (WHERE frac < 0.01)                   AS slivers,
       count(median_gross_rent) FILTER (WHERE frac > 0.5)    AS majority_with_rent
FROM cand;
```

→ `67 | 47 | 7 | 46`.

67 ZCTAs touch Travis County, 47 have more than half their area inside it, 7
have less than 1% — border artefacts between two independently generalized
boundary files — and 46 of the 47 publish a rent median. The `bbox`-overlap
condition is a GeoParquet 1.1 covering-struct prefilter with row-group
statistics behind it, so `ST_Intersection` runs on a handful of polygons rather
than 33,791; write it as an *intersection* test (`z.xmin <= c.xmax AND z.xmax
>= c.xmin AND …`), because containment would drop every ZCTA that only partly
covers the county. There is no string shortcut for this: `substr(geoid, 1, 5)`
means nothing at this geography. For a population-weighted allocation rather
than a membership list, use the Census Bureau's own
[ZCTA-to-county relationship files](https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html)
and say which one.

### 5. Rent against income (1:1 sibling join)

```sql
LOAD httpfs;
SELECT h.geoid, i.median_hh_income::int AS income, h.median_gross_rent::int AS rent,
       round(12.0 * h.median_gross_rent / i.median_hh_income * 100, 1) AS annual_rent_pct_of_income
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet' h
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet' i
  USING (geoid)
WHERE h.households > 5000
  AND h.median_gross_rent_cv < 0.10 AND i.median_hh_income_cv < 0.10
ORDER BY annual_rent_pct_of_income DESC LIMIT 5;
```

→ `90007 | 35378 | 1544 | 52.4`, `10453 | 33186 | 1420 | 51.3`, `15213 | 31069
| 1263 | 48.8`, `61820 | 27539 | 1108 | 48.3`, `44115 | 22056 | 869 | 47.3`.

The join is 1:1 on `geoid` — all six ZCTA collections hold the same 33,791
rows. Both `_cv` gates are load-bearing; without them this ranking fills with
ZCTAs whose rent median rests on a few dozen renters, as recipe 3 shows.

Read the derived column for what it is: a ratio of **two medians from two
different universes** (renter-occupied units paying cash rent, versus all
households). It is a useful screening index for rent pressure and it is not a
household-level rent-to-income ratio — `pct_rent_burdened` is the column that
actually measures that, household by household, inside the Census Bureau's own
tabulation. The difference shows in the result: an index built on two medians
puts the worst rent pressure in the country in large, dense, low-median-income
ZCTAs, and a cross-check against
[`zcta-people`](../zcta-people/collection.json)'s `median_age` (25.4, 35.3,
20.8, 21.9 and 27.0 for these five, measured) says what four of them have in
common. Where the household-income median is depressed by non-family
households, this index overstates the burden a typical resident feels; use
`pct_rent_burdened` for the claim and this index only to find candidates.

### Related recipes elsewhere

- All 112 columns at once, including both top codes:
  [`zctas/zctas/AGENTS.md`](../zctas/AGENTS.md).
- The `geoid`-prefix trap measured, and the state membership test:
  [`zctas/zcta-income/AGENTS.md`](../zcta-income/AGENTS.md).
- Campus and base ZCTAs with thousands of people and dozens of households —
  the same thin-denominator failure from the other side:
  [`zctas/zcta-connectivity/AGENTS.md`](../zcta-connectivity/AGENTS.md).
- The same theme at a geography whose GEOIDs nest:
  [`tracts/tract-housing/AGENTS.md`](../../tracts/tract-housing/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and its z0–z5 features are counties rather than ZCTAs, so nothing
above can be reproduced from tiles.
