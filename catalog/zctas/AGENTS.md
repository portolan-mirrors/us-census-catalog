# Agent guide — ZIP Code Tabulation Areas

Guidance for AI agents and automated clients working with this geography.

**Every claim in this file is quoted from a source or measured from the data.**
The catalog-level [AGENTS.md](../AGENTS.md) covers what spans geographies, and
each collection's own `AGENTS.md` carries its columns, NULL rates and tested
queries. This file covers what the six collections share. If you cannot point
at where a fact came from, it does not belong here.

## The two things that make this geography different

**A ZCTA is not a ZIP code.** It is the Census Bureau's approximation of a USPS
5-digit ZIP delivery area, built by giving each 2020 census block the most
common ZIP code of the addresses in it
([what a ZCTA is](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html)).
Boundaries are not ZIP boundaries, some ZIP codes have no ZCTA at all
(PO-box-only and point ZIPs — `20500`, the White House, is one: it returns no
row, measured), and the codes are re-delineated only once a decade. Matching a
customer, patient or member ZIP list to these files is an approximation. Say
so, and report how many of the input ZIPs found a row.

**A ZCTA nests in nothing.** Every other geography in this catalog sits inside
a state, and most sit inside a county. A ZCTA sits inside neither: it can cross
county and state lines. Three consequences, each of which turns into a wrong
answer rather than an error:

- **`state` is NULL on all 33,791 rows.** `WHERE state = 'CA'` returns nothing,
  silently. The column exists only so the schema matches the catalog's other
  collections.
- **The first two characters of a `geoid` are a postal region, not a state FIPS
  code.** `substr(geoid, 1, 2) = '06'` — California's FIPS — returns 289 rows,
  and a spatial check against [`states`](../states/states/collection.json) puts
  **none of them in California**: 288 intersect **Connecticut** and one,
  `06390` (population 72, Fishers Island), is wholly in **New York**
  (measured; `90210`, a real California ZIP, checks out 100% inside
  California). A prefix join to [`states`](../states/states/collection.json) or
  [`counties`](../counties/counties/collection.json) therefore returns
  confidently wrong rows, not zero rows.
- **Relating a ZCTA to a county, tract or state is a spatial operation.** The
  tested recipe, with a `bbox` covering-struct prefilter and an area-share
  membership gate, is in
  [zcta-income](zcta-income/AGENTS.md); every themed guide here carries a
  variant of it. For a population-weighted allocation rather than a membership
  list, use the Census Bureau's own
  [ZCTA relationship files](https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html)
  and say which one.

Measured, with the same area-share expression: **118 ZCTAs have more than 1% of
their area in two or more states**, and 3,572 touch a second state's polygon at
all — the difference being border slivers between two independently generalized
boundary files. One ZCTA, `63119`, splits 99.0% / 1.0% between St. Louis County
and St. Louis city. "Which state is this ZIP in" has no single answer for
hundreds of ZCTAs, and "which county" has no single answer for far more.

## What this geography is

**33,791 rows** per collection, one per ZIP Code Tabulation Area, ACS 2020–2024
5-year estimates, geometry from the **2020** cartographic boundary files
(GENZ2020 — the only cartographic ZCTA edition the Census Bureau publishes;
every other geography in this catalog uses GENZ2024). Row count checked against
the Census Bureau's own
[2020 geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html):
33,642 United States + 132 Puerto Rico + 17 island areas = 33,791, exactly the
row count here. The ACS tabulates 33,772 of them, and every one of those 33,772
matched a polygon.

A ZCTA is not a unit of anything in particular, and its variability is the
practical consequence: `aland_sqkm` runs from **0.004 to 35,426.845** and
`population` from **0 to 140,157**, with a median of 2,656 (measured). 598
ZCTAs (1.77%) have an ACS row with population exactly 0. So `pop_density` is
the only fair way to compare two of them, an unweighted mean over ZCTAs is not
a national average, and a `population` gate belongs in nearly every query.

## Six collections, one geography

Five themed collections mirroring the tract themes, plus the original wide
112-column table as a sixth:

| collection | theme | headline columns |
|---|---|---|
| [zcta-income](zcta-income/collection.json) ([agent guide](zcta-income/AGENTS.md)) | Income & Poverty | `median_hh_income`, `per_capita_income`, `pct_below_poverty`, `pct_snap`, `pct_unemployed` |
| [zcta-people](zcta-people/collection.json) ([agent guide](zcta-people/AGENTS.md)) | People & Education | `median_age`, `pct_under_18`, `pct_65_plus`, the four non-Hispanic race shares, `pct_hispanic`, `pct_bachelors_plus` |
| [zcta-housing](zcta-housing/collection.json) ([agent guide](zcta-housing/AGENTS.md)) | Housing & Rent | `housing_units`, `households`, `pct_owner_occupied`, `median_gross_rent`, `median_home_value`, `pct_rent_burdened` |
| [zcta-connectivity](zcta-connectivity/collection.json) ([agent guide](zcta-connectivity/AGENTS.md)) | Commuting & Connectivity | `hh_no_vehicle`, the B08301 commute-mode shares, `pct_commute_45min_plus`, `pct_no_internet`, `pct_no_computer` |
| [zcta-wellbeing](zcta-wellbeing/collection.json) ([agent guide](zcta-wellbeing/AGENTS.md)) | Health, Disability & Income by Race | `pct_uninsured`, `pct_with_disability`, `pct_foreign_born`, `group_quarters_pop`, `median_hh_income_{black,white_nh,asian,hispanic}`, `pct_below_poverty_black` |
| [zctas](zctas/collection.json) ([agent guide](zctas/AGENTS.md)) | All Indicators — the wide table | all 112 |

Column counts, measured: income 23, people 29, housing 32, connectivity 30,
wellbeing 34, wide 112.

**The wide collection's data files sit one directory up.** Its STAC metadata
moved into `zctas/zctas/` when the themed children were added, but the
GeoParquet and PMTiles stayed where they have always been:

- wide: `.../us-census-catalog/zctas/zctas.parquet`, `.../zctas/zctas.pmtiles`
- themed: `.../us-census-catalog/zctas/zcta-income/zcta-income.parquet`, and so on

Every chunk carries the same seven context columns — `geoid`, `name`, `state`,
`population`, `population_moe`, `aland_sqkm`, `pop_density` — plus `geometry`
and the `bbox` covering struct, so a single-theme question never needs a join.
`name` is just `ZCTA5 ` plus the code, because a ZCTA has no containing
geography to be named after — the same fact as `state` being NULL.

## The chunks join 1:1 on `geoid`

All six hold the same 33,791 `geoid` values with the same geometry. Measured —
this query and the next were run with DuckDB 1.4.1 against these files as built,
immediately before they were written down, and their real output is quoted
beside them. The URLs are the published ones; the runs swapped in the local
`catalog/` paths, because the five themed collections had not yet been uploaded
to the mirror when the queries were run, so no wall-clock timings are quoted.

```sql
LOAD httpfs;
SELECT (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet')             AS income,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/zcta-people.parquet')             AS people,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet')           AS housing,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.parquet') AS connectivity,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/zcta-wellbeing.parquet')       AS wellbeing,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zctas.parquet')                               AS all_indicators;
```

→ `33791 | 33791 | 33791 | 33791 | 33791 | 33791`.

The `geoid` sets are identical, not merely the same size: `SELECT geoid FROM
zcta-income EXCEPT SELECT geoid FROM zctas` returns 0 rows, and so does the
reverse against `zcta-wellbeing` (measured). So `JOIN … USING (geoid)` loses
nothing, and a full profile of one ZCTA is one query across all five themed
files:

```sql
LOAD httpfs;
SELECT i.geoid, i.name, i.median_hh_income::int AS income, i.pct_below_poverty AS poverty,
       p.median_age, p.pct_bachelors_plus AS degree, h.median_gross_rent::int AS rent,
       c.pct_commute_transit AS transit, w.pct_uninsured AS uninsured
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-income/zcta-income.parquet' i
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-people/zcta-people.parquet'             p USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-housing/zcta-housing.parquet'           h USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-connectivity/zcta-connectivity.parquet' c USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/zctas/zcta-wellbeing/zcta-wellbeing.parquet'       w USING (geoid)
WHERE i.geoid = '98109';
```

→ `98109 | ZCTA5 98109 | 133663 | 8.71 | 31.7 | 79.42 | 2343 | 11.16 | 3.65`.

Five files for one row is the expensive shape; join only the chunks you need,
or read the sixth sibling [`zctas`](zctas/collection.json) instead, which has
all 112 columns in one 75,213,440-byte file. (That ZCTA came from a
point-in-polygon lookup; the recipe is in
[zcta-people](zcta-people/AGENTS.md).)

What does **not** work: `substr(geoid, 1, 5)`, `substr(geoid, 1, 2)`, or any
other prefix. The only join key a ZCTA has is its own full 5-digit code,
against its five siblings. Everything else is geometry.

## When to step up or down a geography

ZCTAs are not a rung on the census hierarchy — there is nothing to step down
*to* and nothing they roll up *into*. The choice is between asking a question
at ZCTA level because the input is ZIP codes, and re-asking it at a geography
that nests. Here is the measured case for each.

Suppression, same columns at the geographies a ZCTA can be related to
spatially:

| column | NULL at block group | NULL at tract | **NULL at ZCTA** | NULL at county |
|---|---|---|---|---|
| `median_hh_income` | 7.69% | 1.59% | **9.60%** | 0.43% |
| `median_gross_rent` | 29.68% | 5.92% | **23.79%** | 0.62% |
| `median_home_value` | 10.03% | 3.55% | **10.45%** | 0.56% |
| `median_hh_income_black` | not published | 61.43% | **69.25%** | 39.47% |
| `median_hh_income_asian` | not published | 71.27% | **76.59%** | 53.63% |

Reliability (measured): the median `median_hh_income_cv` is **0.095** at ZCTA
against 0.125 at tract and 0.042 at county — but **4.9%** of ZCTA medians are
over the 0.40 "unreliable" line against 1.5% of tract medians and 0.1% of
county medians. Read both numbers together: the typical ZCTA estimate is more
reliable than the typical tract estimate, because many ZCTAs are large suburban
areas, while the ZCTA tail is three times fatter, because the same file holds
thousands of ZCTAs with a few hundred people. ZCTAs are not a coarser
geography than tracts; they are a far more *variable* one.

- **Stay here** when the input or the output is ZIP codes — a customer list, a
  service area, a mailing. Nothing else in the catalog answers that question,
  and approximating it with tracts introduces an allocation error you would
  have to defend.
- **Step sideways to [tracts](../tracts/AGENTS.md) or
  [block groups](../block-groups/AGENTS.md)** when the question is really about
  neighbourhoods rather than postal areas. Those GEOIDs nest, so a county or
  state cut is a string operation rather than a spatial one, and
  `tract-wellbeing` publishes the race-iteration medians on more rows than this
  geography does.
- **Step up to [counties](../counties/AGENTS.md) or
  [states](../states/AGENTS.md)** when the answer will be quoted as a single
  number, or when a race-iteration median or a noisy share is the subject:
  `pct_commute_transit_cv` is over 0.40 on 69.4% of the ZCTAs that publish one
  and on 0.0% of states (measured).
- **[Places](../places/AGENTS.md)** are the other non-nesting geography here —
  a place sits in a state but can straddle a county line — and are often what
  someone asking for "ZIP codes" actually wants when they mean towns.
- **[Blocks](../blocks/AGENTS.md)** carry 2020 Decennial counts only, and are
  the geography ZCTAs were *built* from — a different survey and vintage, not a
  finer version of these numbers.

## Shared quirks

- **`state` is NULL on all 33,791 rows, and no `geoid` prefix joins anything.**
  This is the single most common way to get a wrong answer out of this
  geography. See the top of this file.
- Every estimate carries `<name>_moe` at the **90%** confidence level. Headline
  columns also carry `<name>_cv` = `moe / 1.645 / estimate`: under 0.12
  reliable, 0.12–0.40 caution, over 0.40 unreliable. `zcta-people` has **no
  `_cv` columns at all** — use `_moe` there.
- **The margin family is complete here**, unlike at the coarse geographies:
  `population_moe` is populated on 33,759 of the 33,791 rows and
  `group_quarters_pop_moe` on 33,772, against **132 of 3,235 counties** and
  **0 of 56 states** for `population_moe` (measured). At county and state level
  `population` is a count to use; here it is an estimate with a usable
  interval.
- **`*_cv` filtering is mandatory before mapping the connectivity and wellbeing
  columns.** Share of the ZCTAs that publish a CV which are over 0.40
  (measured): `pct_commute_transit` 69.4%, `pct_below_poverty_black` 50.7%,
  `pct_hh_no_vehicle` 49.2%, `pct_no_internet` 34.9%, `pct_rent_burdened`
  35.3%. The median `pct_below_poverty_black_cv` is 0.406 — above the
  unreliable line.
- **A `_cv` filter is also a filter on "the estimate is non-zero",** because
  the CV is NULL wherever the estimate is 0. 32,798 ZCTAs publish
  `pct_commute_transit` and only 13,378 publish its CV (measured), so
  `WHERE pct_commute_transit_cv < 0.12` silently discards every zero-transit
  ZCTA.
- **Never sum or average a median.** A region's median is not derivable from
  its parts'. To sum counts, add margins in quadrature (`sqrt(sum(moe*moe))`).
- **The medians thin out at this geography, and the holes are small ZCTAs.**
  `median_gross_rent` is NULL on 73.6% of ZCTAs under 500 people and on 0.1% of
  those over 10,000 (measured, [zcta-housing](zcta-housing/AGENTS.md)). A
  national choropleth of a median is therefore a map with rural holes that
  carry no information about rent or income — gate on `population`, or draw the
  NULLs in a colour that is not on the ramp.
- **`median_hh_income` is top-coded at $250,001 and `median_home_value` at
  $2,000,001.** Published values, not jam codes; the richest ZCTAs sit on them,
  so a ranking at the very top is a ranking of rounding.
- **`population` is not a household count.** 133 ZCTAs have over 2,000 people
  and under 100 households (measured) — campuses and military bases, where
  `group_quarters_pop` in `zcta-wellbeing` is nearly all of `population`. One
  of them publishes a household share with a margin of ±257 percentage points.
  Gate household- and worker-denominated columns on `households` from
  [zcta-housing](zcta-housing/collection.json).
- **A margin of exactly 0.0 is a flag to inspect, not high precision** — and it
  makes the CV 0.0, so such rows pass every reliability filter.
- Jam values are already NULL. No jam filtering is needed, but NULLs reduce the
  row count of an aggregate and `avg()` skips them silently.
- Percentages are 0–100, not 0–1, and their margins are on the same scale.
- `population` is the ACS 5-year estimate (B01003), not a 2020 Decennial count.
- **19 ZCTAs carry geometry and no ACS data**: 17 in the island areas (`00802`,
  `00820`, `00830`, `00840`, `00850`, `00851`, `96799`, `96910`, `96913`,
  `96915`, `96916`, `96917`, `96928`, `96929`, `96950`, `96951`, `96952`) plus
  `11717` and `11798` in Suffolk County, New York. Every ACS column is NULL on
  those rows.
- Geometry is the 500k cartographic boundary files, shoreline-clipped,
  EPSG:4326 — good for mapping and point-in-polygon, not for area measurement.
  Two independently generalized files share border slivers, which is why a
  spatial membership test needs an area-share gate rather than bare
  `ST_Intersects`.
- **PMTiles z0–z5 are counties**, not ZCTAs — the Census Bureau's own county
  estimates under the same column names, so one style classifies every zoom —
  and z6–z12 are the ZCTAs themselves. ZCTAs do not nest in counties, so the
  county band is national orientation rather than a roll-up of these features.
  The tiles carry no `*_moe` columns; they do carry `*_cv`. Statistics come
  from the GeoParquet, always.

## Where to look next

- Per-collection schemas, NULL stories and 4–5 tested recipes each:
  [zcta-income](zcta-income/AGENTS.md), [zcta-people](zcta-people/AGENTS.md),
  [zcta-housing](zcta-housing/AGENTS.md),
  [zcta-connectivity](zcta-connectivity/AGENTS.md),
  [zcta-wellbeing](zcta-wellbeing/AGENTS.md), and the wide
  [zctas](zctas/AGENTS.md).
- "Income for a list of ZIP codes", the prefix trap measured, and the spatial
  state-membership test: [zcta-income](zcta-income/AGENTS.md).
- "Which ZCTA is this point in" with a `bbox` prefilter:
  [zcta-people](zcta-people/AGENTS.md).
- Where the rent and value medians are missing, and why a `households` gate is
  not enough: [zcta-housing](zcta-housing/AGENTS.md).
- The campus-and-base thin-denominator trap, and margins wider than the scale:
  [zcta-connectivity](zcta-connectivity/AGENTS.md).
- Income by race with its coverage denominator attached:
  [zcta-wellbeing](zcta-wellbeing/AGENTS.md).
- Cross-geography showcases and the catalog-wide conventions:
  [catalog AGENTS.md](../AGENTS.md).

## License

CC0-1.0. Census Bureau data is a U.S. Government work in the public domain;
this mirror adds nothing proprietary. [data.census.gov](https://data.census.gov/)
is authoritative and nothing here is an official Census Bureau product — cite
the U.S. Census Bureau when you use the numbers.
