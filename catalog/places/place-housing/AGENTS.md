# Agent guide — Housing & Rent (Places & CDPs)

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.** The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. If you cannot point at where a fact came from, it does not belong here — an agent acting on an invented column name produces a confident wrong answer that nothing downstream catches.

## What this is

The housing stock and what it costs: total units and the vacancy rate ([B25002](https://data.census.gov/table/ACSDT5Y2024.B25002)), households and the owner-occupied share ([B25003](https://data.census.gov/table/ACSDT5Y2024.B25003)), median gross rent ([B25064](https://data.census.gov/table/ACSDT5Y2024.B25064)) and median owner-occupied home value ([B25077](https://data.census.gov/table/ACSDT5Y2024.B25077)), the share of renter households paying 30% and 50% or more of income on rent ([B25070](https://data.census.gov/table/ACSDT5Y2024.B25070)), the pre-1940 share ([B25034](https://data.census.gov/table/ACSDT5Y2024.B25034)) and the single-family share ([B25024](https://data.census.gov/table/ACSDT5Y2024.B25024)).

**32,612 rows**, one per place, ACS 2020–2024 5-year estimates, geometry from the 2024 cartographic boundary files.

This is the **holeyest** of the five themed place chunks. `median_gross_rent` is NULL on **31.32%** of places — nearly a third of the file — against 5.92% of tracts and 0.62% of counties, because a median gross rent needs renter households paying cash rent and thousands of these rows are villages and CDPs of a few hundred people. A `population` floor is not a refinement here; it is the difference between an answer and an artefact.

## Where it lives

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.pmtiles`, layer `place-housing`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/collection.json` — carries a full description for every column

This is a themed cut of the wide 112-column place table, which is published as the sixth sibling in this group: `https://data.source.coop/portolan-mirrors/us-census-catalog/places/places.parquet` ([agent guide](../places/AGENTS.md)). Same 32,612 rows, same geometry, every column below included — reach for it when a question crosses themes, and for this one when it does not.

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

`geoid` is 7 characters — state FIPS (2) + place FIPS (5) — and `substr(geoid, 1, 2)` is the only prefix join it supports, to [`states/state-housing`](../../states/state-housing/collection.json). Places nest in states but not in counties (a place can straddle a county line) and a place is not an aggregate of tracts or block groups, so there is no prefix path to the finer collections. The five themed siblings and the wide table all carry the same 32,612 `geoid` values, so `JOIN … USING (geoid)` is 1:1.

| column | type | what it is |
|---|---|---|
| `geoid` | string | 7-character place GEOID: state FIPS 2 + place FIPS 5, e.g. `0644000` for Los Angeles city. |
| `name` | string | `NAMELSAD`, `STATE_NAME` from the 2024 cartographic boundary place file — "Los Angeles city, California", "Brentwood CDP, New York". The descriptor in the name says whether the place is a city, town, village, borough or CDP. |
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

- **`median_gross_rent`'s universe is renter-occupied units *paying cash
  rent*** (B25064), so units occupied rent-free are outside it. This is the
  main reason the column is NULL on 31.32% of places: a village with a dozen
  cash-renting households supports no median. **53.3%** of places under 1,000
  people have no rent median against **0.0%** of places of 50,000 or more
  (measured, recipe 1).
- **The rent-burden columns divide by renter households *excluding* those
  whose rent-to-income ratio the Bureau could not compute** (B25070 line 1
  minus line 11, "Not computed" — no cash rent, or no income). Including them
  would understate the burden. `pct_rent_burdened` and
  `pct_severely_rent_burdened` are NULL on 14.60% of places each, where that
  denominator came out at or below 0.
- **`pct_vacant_units` is not a measure of abandonment.** The ACS counts
  for-sale, for-rent, seasonal and migrant-worker units as vacant (B25002 line
  3), so resort and second-home places read as near-empty: Ocean City town,
  Maryland reports 29,811 housing units, 6,903 residents and 87.16% vacant
  (measured, recipe 5). Read the share beside `housing_units` and `population`,
  never alone.
- **`median_home_value` is the owner's own estimate** of what the property
  would sell for — not an assessment, not a sale price, and not a market index.
- **`housing_units` and `households` are the only two columns here that are
  never suppressed** beyond the data-free rows (both NULL on 0.86%, measured).
  A place can have 0 households and a nonzero population: a campus CDP that is
  entirely group quarters does, and every household-denominated column on that
  row is NULL as a result, not low. See
  [`place-wellbeing`](../place-wellbeing/AGENTS.md) for the measured cases.
- **Places are not a partition of the country.** Do not sum `housing_units` or
  `households` across place rows to get a state or national stock — the land
  between places is absent from this file, not empty. For a total, use
  [`counties/county-housing`](../../counties/county-housing/collection.json) or
  [`states/state-housing`](../../states/state-housing/collection.json).
- **Most rows are small.** 16,463 places have under 1,000 people and 883 have
  50,000 or more (measured). The median place's `median_gross_rent` is **$975**
  and `median_home_value` **$190,100** across the whole file (measured, recipe
  1) — numbers about villages, not about cities. Filter on `population` first.
- **Louisville is `2148006`,** the consolidated Louisville/Jefferson County
  metro government (balance). `2148000` "Louisville city" is still in the
  boundary file and has no ACS row, so it publishes with NULL values. The
  worked case is in [`../AGENTS.md`](../AGENTS.md).
- **282 places carry geometry and no ACS data**: 279 in the island areas
  (MP 135, AS 77, GU 57, VI 10, measured), Brentwood CDP and Wyandanch CDP in
  Suffolk County, New York, and Louisville city. `ORDER BY … DESC` needs
  `NULLS LAST`.
- **Every estimate has a `<name>_moe`**, at the 90% confidence level — the
  level the Census Bureau publishes. To compare two places, check whether
  their margins overlap before calling a difference real. To sum estimates
  across geographies, add the margins in quadrature (`sqrt(sum(moe*moe))`).
  **Never sum or average a median**: a median of a region is not derivable
  from the medians of its parts.
- **Headline columns also have a `<name>_cv`** = `moe / 1.645 / estimate` —
  here `median_gross_rent_cv`, `pct_rent_burdened_cv` and
  `median_home_value_cv`. Rule of thumb: under 0.12 reliable, 0.12–0.40 use
  with caution, over 0.40 unreliable. At place level the measured medians are
  0.091 (`median_gross_rent`), 0.338 (`pct_rent_burdened`) and 0.088
  (`median_home_value`) — the rent-burden share is close to unusable without a
  gate, while the two dollar medians survive. `pct_vacant_units`,
  `pct_owner_occupied`, `pct_severely_rent_burdened`, `pct_built_pre_1940` and
  `pct_single_family` have **no `_cv`**; gate those on `_moe`.
- **Jam values are already NULL.** The ACS publishes sentinels (-666666666
  and friends) where an estimate cannot be computed; anything at or below
  -111111111 became NULL in the build, so no jam filtering is needed — but
  NULLs reduce the row count of an aggregate, and `avg()` silently skips
  them.
- **Percentages are 0–100, not 0–1**, rounded to 2 decimals. Their margins
  are on the same scale, and at this geography a percentage's margin can
  exceed 100 points — a flag to drop the row, not a value.
- **`population` is the ACS 5-year estimate** (B01003), not a 2020 Decennial
  count. It will not match the `blocks` collection's `pop_total` summed over
  the same area, and neither number is wrong.
- **`pct_single_family` is the share of *units in single-family structures***
  (B25024), occupied or not, and `pct_built_pre_1940` the share built in 1939
  or earlier (B25034). Both divide by all housing units, so they are
  comparable to `pct_vacant_units` and not to `pct_owner_occupied`, which
  divides by occupied units.

## Data quality

Columns with notable missingness at this geography (rates counted by the build's validation pass, not estimated):

| column | missingness |
|---|---|
| `population`, `housing_units`, `households` | NULL on 0.86% of places — the 282 rows with 2024 boundaries and no ACS tabulation. Every other column is NULL on at least those rows. |
| `median_gross_rent` | **NULL on 31.32% of places** (23.79% of ZCTAs, 5.92% of tracts, 0.62% of counties). Concentrated in small places: 53.3% below 1,000 people, 9.9% from 1,000–9,999, 0.2% from 10,000–49,999, 0.0% at 50,000+ (measured, recipe 1). |
| `median_home_value` | NULL on 12.78% of places (3.55% of tracts, 0.56% of counties). 22.3% below 1,000 people, 0.0% at 50,000+. |
| `pct_rent_burdened`, `pct_severely_rent_burdened` | NULL on 14.60% of places each, where the computable-ratio denominator came out at or below 0. 26.0% below 1,000 people, 0.0% at 50,000+. |
| `pct_owner_occupied` | NULL on 2.76% of places (measured) — places with no occupied housing units. |
| `pct_vacant_units`, `pct_built_pre_1940`, `pct_single_family` | NULL on 2.20% of places each (measured) — all share B25002 line 1's housing-unit denominator, so they fail together. |

Island areas carry geometry but no ACS data. American Samoa, Guam, the Northern Mariana Islands and the U.S. Virgin Islands have 2024 cartographic boundaries but no ACS 5-year estimates, so their rows publish with NULL values rather than being dropped: 279 places here, plus 4 states, 13 county equivalents, 126 tracts and 405 block groups elsewhere in the catalog.

Three more places have boundaries and no ACS row: `3608026` Brentwood CDP and `3683294` Wyandanch CDP, left without an ACS match by the 2024 re-delineation of Suffolk County, New York, and `2148000` Louisville city, whose ACS tabulation is the consolidated `2148006` metro government. Running the other way, every one of the 32,330 ACS-tabulated places matched a polygon.

Row count is the 2024 cartographic boundary place file's own feature count, 32,612. For scale, the Census Bureau's [2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html) give 19,734 incorporated places and 12,454 census designated places (32,188) for the 2020 vintage; the 2024 vintage is four years of incorporations, dissolutions and CDP re-delineations later.

Spot-checked against data.census.gov: Los Angeles city median home value $921,200.

Margins of error at this geography can be large relative to the estimate — larger than anywhere in the catalog except block groups. Use the `*_cv` columns to flag or grey out unreliable values; never compare two places without checking whether their margins overlap, and never aggregate a median.

PMTiles coarse zooms are a different census geography from this collection's: z0–z5 are **counties**, carrying the Census Bureau's own county estimates for these same columns, and z6–z12 are the places themselves. The county band is national orientation, not a roll-up of this file — places do not tile a county. `*_moe` columns are not in the tiles; `*_cv` columns are. A place-level choropleth of `median_gross_rent` is drawn on 68.68% of the rows, so style the NULLs as a visible "not published" class rather than letting them fall through to the background. Statistics come from the GeoParquet.

## Related collections

- [`places/place-income`](../place-income/collection.json) — Income & Poverty, same geography. Same `geoid`, joins 1:1 — the denominator for any affordability ratio.
- [`places/place-people`](../place-people/collection.json) — People & Education, same geography. Same `geoid`, joins 1:1.
- [`places/place-connectivity`](../place-connectivity/collection.json) — Commuting & Connectivity, same geography. Same `geoid`, joins 1:1.
- [`places/place-wellbeing`](../place-wellbeing/collection.json) — Health, Disability & Income by Race, same geography. Same `geoid`, joins 1:1.
- [`places/places`](../places/collection.json) — the wide 112-column place table, the sixth sibling: every column of all five themes in one file.
- [`counties/county-housing`](../../counties/county-housing/collection.json) and [`states/state-housing`](../../states/state-housing/collection.json) — the same theme at geographies that **do** tile the country, with the rent median NULL on 0.62% and 7.14% of rows instead of 31.32%.
- [`tracts/tract-housing`](../../tracts/tract-housing/collection.json) and [`block-groups/bg-housing`](../../block-groups/bg-housing/collection.json) — the same theme inside a city, at geographies that tile it.
- [`zctas/zcta-housing`](../../zctas/zcta-housing/collection.json) and [`congressional-districts/cd-housing`](../../congressional-districts/cd-housing/collection.json) — the same theme at the catalog's other non-nesting geographies.
- [`blocks`](../../blocks/collection.json) — 2020 Decennial housing-unit and occupancy counts at block level. Different survey, different vintage, no margins of error.

## Example queries

Every query here was run with DuckDB 1.4.1 against these files as built,
immediately before it was written down, and its real output is quoted beside
it. The URLs below are the published ones; the runs swapped in the local
`catalog/` paths, because this collection had not yet been uploaded to the
mirror when the queries were run — so no wall-clock timings are quoted. For
scale instead: the file is **28.2 MB** over **32,612 rows**.

### 1. How much of this file has a rent median at all?

```sql
INSTALL httpfs; LOAD httpfs;
SELECT count(*)                                                     AS places,
       count(median_gross_rent)                                     AS rent_published,
       round(100.0*(count(*)-count(median_gross_rent))/count(*), 2) AS pct_rent_null,
       quantile_cont(median_gross_rent, 0.50)::int                  AS rent_p50,
       quantile_cont(median_home_value, 0.50)::int                  AS value_p50
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.parquet';
```

→ `32612 | 22398 | 31.32 | 975 | 190100`.

Then the same holes by size:

```sql
LOAD httpfs;
SELECT CASE WHEN population < 1000  THEN 'under 1,000'
            WHEN population < 10000 THEN '1,000-9,999'
            WHEN population < 50000 THEN '10,000-49,999'
            ELSE '50,000+' END                                        AS size_band,
       count(*)                                                       AS places,
       round(100.0*count(*) FILTER (WHERE median_gross_rent  IS NULL)/count(*), 1) AS pct_rent_null,
       round(100.0*count(*) FILTER (WHERE median_home_value  IS NULL)/count(*), 1) AS pct_value_null,
       round(100.0*count(*) FILTER (WHERE pct_rent_burdened  IS NULL)/count(*), 1) AS pct_burden_null
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.parquet'
WHERE population IS NOT NULL
GROUP BY 1 ORDER BY min(population);
```

→ `under 1,000 | 16463 | 53.3 | 22.3 | 26.0`,
`1,000-9,999 | 11641 | 9.9 | 1.8 | 1.7`,
`10,000-49,999 | 3343 | 0.2 | 0.3 | 0.0`,
`50,000+ | 883 | 0.0 | 0.0 | 0.0`.

Every hole in this collection is a small-place hole. Above 10,000 people the
three suppressed columns are essentially complete; below 1,000 people more
than half the rows have no rent median. So the 31.32% headline is not a
quality problem to apologise for, it is a universe statement: this file
contains 16,463 places that are too small for the ACS to price. `WHERE
population IS NOT NULL` is needed because the 282 data-free rows would
otherwise form a band of their own.

### 2. The most expensive places to rent (`*_cv`-gated, population-floored)

```sql
LOAD httpfs;
SELECT geoid, name, population, median_gross_rent::int AS rent,
       round(median_gross_rent_cv, 3) AS cv
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.parquet'
WHERE population > 25000 AND median_gross_rent_cv < 0.05
ORDER BY median_gross_rent DESC LIMIT 5;
```

→ `0655282 | Palo Alto city, California | 67237 | 3484 | 0.027`, `0645400 |
Manhattan Beach city, California | 34210 | 3449 | 0.044`, `5148376 | McLean
CDP, Virginia | 49627 | 3422 | 0.044`, `0651182 | Newport Beach city,
California | 83845 | 3316 | 0.016`, `1506290 | East Honolulu CDP, Hawaii |
51360 | 3313 | 0.031`.

Two of the five are CDPs — McLean and East Honolulu are unincorporated, so a
query restricted to incorporated "cities" would miss them and silently
mis-rank the rest. Drop the `population > 25000` floor and this list fills with
tiny places whose rent median rests on a handful of households; drop the `_cv`
gate and it fills with large places whose median has a ±30% margin. Both gates
are the query.

### 3. Home value against income (sibling join)

```sql
LOAD httpfs;
SELECT h.geoid, h.name, h.population, i.median_hh_income::int AS income,
       h.median_home_value::int AS home_value,
       round(h.median_home_value / i.median_hh_income, 1) AS value_to_income
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.parquet' h
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-income/place-income.parquet' i
  USING (geoid)
WHERE h.population > 50000
  AND h.median_home_value_cv < 0.10 AND i.median_hh_income_cv < 0.10
ORDER BY value_to_income DESC LIMIT 5;
```

→ `0670000 | Santa Monica city, California | 91169 | 114885 | 1755500 | 15.3`,
`0669070 | Santa Barbara city, California | 87779 | 106182 | 1570800 | 14.8`,
`0606000 | Berkeley city, California | 120257 | 108092 | 1413900 | 13.1`,
`0602462 | Arcadia city, California | 55170 | 113516 | 1441800 | 12.7`,
`3438580 | Lakewood CDP, New Jersey | 69585 | 56968 | 715500 | 12.6`.

The join is 1:1 on `geoid` — all six place collections hold the same 32,612
rows. `value_to_income` is a ratio of two medians from two different universes
(owner-occupied units vs all households); it is a useful screening index and
**not** a household-level statistic, and no margin is propagated through the
division. The two `_cv` gates matter in opposite directions: without the
home-value gate the list fills with places whose median is ±50%, and without
the income gate the denominator is the unreliable half. The last row gets there
from the bottom — Lakewood's income is half Santa Monica's.

### 4. Every place against its own state's rent (GEOID prefix join)

```sql
LOAD httpfs;
SELECT p.name, p.population, p.median_gross_rent::int AS place_rent,
       s.median_gross_rent::int AS state_rent,
       round(p.median_gross_rent::double / s.median_gross_rent, 2) AS ratio
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.parquet' p
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/states/state-housing/state-housing.parquet' s
  ON substr(p.geoid, 1, 2) = s.geoid
WHERE p.population > 50000 AND p.median_gross_rent_cv < 0.05
ORDER BY ratio DESC LIMIT 5;
```

→ `Mount Pleasant town, South Carolina | 93993 | 2159 | 1180 | 1.83`, `Palo
Alto city, California | 67237 | 3484 | 2036 | 1.71`, `Hoboken city, New Jersey
| 58668 | 2938 | 1720 | 1.71`, `Weston city, Florida | 68837 | 2851 | 1669 |
1.71`, `East Honolulu CDP, Hawaii | 51360 | 3313 | 1971 | 1.68`.

A place GEOID is state FIPS (2) + place FIPS (5), so `substr(geoid, 1, 2)` is
the state's `geoid` — the only prefix join this collection supports. There is
no county component in the GEOID at all and therefore **no**
`substr(geoid, 1, 5)` route to
[`counties/county-housing`](../../counties/county-housing/collection.json):
that relationship is spatial, and it is one-to-many (Houston city, `4835000`,
intersects five counties — measured; the pattern is in
[`place-income`](../place-income/AGENTS.md)). Note that the most expensive
place relative to its state is not in an expensive state: Mount Pleasant's
rent is 1.83× South Carolina's, higher than Palo Alto's multiple of California.

### 5. The vacancy column is not an abandonment column

```sql
LOAD httpfs;
SELECT geoid, name, population, pct_vacant_units, housing_units
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/places/place-housing/place-housing.parquet'
WHERE population > 5000
ORDER BY pct_vacant_units DESC LIMIT 5;
```

→ `2458225 | Ocean City town, Maryland | 6903 | 87.16 | 29811`, `0606434 | Big
Bear Lake city, California | 5041 | 76.26 | 9722`, `0157144 | Orange Beach
city, Alabama | 8407 | 73.73 | 14887`, `3454360 | Ocean City city, New Jersey
| 11261 | 73.15 | 21191`, `1246000 | Miramar Beach CDP, Florida | 8902 | 72.16
| 15677`.

All five are resorts, and the tell is in the query's own output: Ocean City,
Maryland has **29,811 housing units for 6,903 residents**. B25002 counts
for-sale, for-rent, seasonal and migrant-worker units as vacant, so a place
built for visitors reports a vacancy rate near 90% while being full in August.
Read `pct_vacant_units` beside `housing_units` and `population` — a high share
with *fewer* units than residents' households would need is a different
phenomenon from a high share with four times as many. Neither reading is
available from the share alone.

### Related recipes elsewhere

- The 11 Louisvilles, the consolidated-city trap, and the one-row cross-theme
  profile: [`places/AGENTS.md`](../AGENTS.md).
- The most rent-burdened large cities, with wall-clock timings against the
  mirror: [`places/places/AGENTS.md`](../places/AGENTS.md).
- The population-floor argument measured by size band, the margin-overlap
  test, and the state prefix join on income:
  [`places/place-income/AGENTS.md`](../place-income/AGENTS.md).
- The same theme where the rent median is nearly complete:
  [`counties/county-housing/AGENTS.md`](../../counties/county-housing/AGENTS.md).
- Rent and home value inside a city, at geographies that tile it:
  [`tracts/tract-housing/AGENTS.md`](../../tracts/tract-housing/AGENTS.md),
  [`block-groups/bg-housing/AGENTS.md`](../../block-groups/bg-housing/AGENTS.md).

Statistics come from the GeoParquet. The PMTiles archive carries no `*_moe`
columns, and its z0–z5 features are counties carrying the Census Bureau's own
county estimates rather than these places', so nothing above can be reproduced
from tiles.
