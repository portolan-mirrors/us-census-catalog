# Agent guide — Counties

Guidance for AI agents and automated clients working with this geography.

**Every claim in this file is quoted from a source or measured from the data.**
The catalog-level [AGENTS.md](../AGENTS.md) covers what spans geographies, and
each collection's own `AGENTS.md` carries its columns, NULL rates and tested
queries. This file covers what the six collections share. If you cannot point
at where a fact came from, it does not belong here.

## What this geography is

A county is **the coarsest geography most questions are actually asked at** and
the most reliable level in this catalog below states. It is where a national
ranking survives its own margins of error — the median `median_hh_income_cv` is
**0.042** here against 0.125 at tract level and 0.202 at block group
(measured) — and where a race-and-income question becomes answerable at all,
because the race-iteration medians are published far more often here than
below: the Black-householder median covers 60.53% of counties against 38.57% of
tracts, and the Asian-householder median 46.37% against 28.73% (measured).

**3,235 rows** per collection, one per county or county equivalent in the
United States, Puerto Rico and the island areas, ACS 2020–2024 5-year
estimates, geometry from the 2024 cartographic boundary files.

Two sharp edges to carry into every query at this geography:

- **`population_moe` is NULL on 3,103 of the 3,235 rows** (measured). Only 132
  small rural counties carry a margin on `population` — 28 in Texas, 26 in
  Nebraska, 14 in South Dakota, 13 in Montana, … Nine more margins are NULL on
  exactly the same rows; see [Shared quirks](#shared-quirks).
- **13 county equivalents carry geometry and no ACS values at all** — the
  island areas (American Samoa 5, Guam 1, Northern Mariana Islands 4, U.S.
  Virgin Islands 3, measured). They have 2024 cartographic boundaries and no
  ACS 5-year estimates, so they publish with NULL values rather than being
  dropped. That is the 0.40% floor under every missingness rate in this group.

## Six collections, one geography

The same five themed collections as [tracts](../tracts/AGENTS.md), plus the
whole table as a sixth:

| collection | theme | headline columns |
|---|---|---|
| [county-income](county-income/collection.json) ([agent guide](county-income/AGENTS.md)) | Income & Poverty, 23 columns | `median_hh_income`, `per_capita_income`, `pct_below_poverty`, `pct_below_2x_poverty`, `pct_snap`, `pct_unemployed` |
| [county-people](county-people/collection.json) ([agent guide](county-people/AGENTS.md)) | People & Education, 29 columns | `median_age`, `pct_under_18`, `pct_65_plus`, `pct_white_nh`, `pct_black`, `pct_native`, `pct_asian`, `pct_hispanic`, `pct_people_of_color`, `pct_bachelors_plus` |
| [county-housing](county-housing/collection.json) ([agent guide](county-housing/AGENTS.md)) | Housing & Rent, 32 columns | `housing_units`, `households`, `pct_vacant_units`, `pct_owner_occupied`, `median_gross_rent`, `median_home_value`, `pct_rent_burdened`, `pct_single_family` |
| [county-connectivity](county-connectivity/collection.json) ([agent guide](county-connectivity/AGENTS.md)) | Commuting & Connectivity, 30 columns | `hh_no_vehicle`, the four B08301 commute-mode shares, `pct_commute_45min_plus`, `pct_no_internet`, `pct_no_computer` |
| [county-wellbeing](county-wellbeing/collection.json) ([agent guide](county-wellbeing/AGENTS.md)) | Health, Disability & Income by Race, 34 columns | `pct_uninsured`, `pct_with_disability`, `pct_foreign_born`, `group_quarters_pop`, `median_hh_income_{black,white_nh,asian,hispanic}`, `pct_below_poverty_black` |
| [counties](counties/collection.json) ([agent guide](counties/AGENTS.md)) | All Indicators, 112 columns | every column above, in one table |

Column counts measured against the files as built. Every chunk carries the same
seven context columns — `geoid`, `name`, `state`, `population`,
`population_moe`, `aland_sqkm`, `pop_density` — plus `geometry` and the `bbox`
covering struct, so a single-theme question never needs a join.

**The wide table's data files sit one directory up.** This is the one asymmetry
in the layout and it is worth getting right:

```
counties/counties/collection.json   <- the wide table's STAC document
counties/counties.parquet           <- the wide table's DATA, one level up
counties/counties.pmtiles
counties/county-income/county-income.parquet    <- a themed child: both together
counties/county-income/county-income.pmtiles
```

So the wide table is
`https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet`
— unchanged by the restructure — while each themed child is
`.../counties/<cid>/<cid>.parquet`. Every child's STAC document, the wide one
included, is at `.../counties/<cid>/collection.json`, and this group's
sub-catalog is `.../counties/catalog.json`.

Prefer a themed chunk when the question sits inside one theme: it is a third of
the columns over the same rows. Prefer `counties` when a question crosses three
or more themes, or when you do not yet know which columns you need — at this
many features width costs little, and a five-way join costs more than reading
one wider file.

## The chunks join 1:1 on `geoid`

All six hold the same 3,235 `geoid` values with the same geometry. Measured:

```sql
INSTALL httpfs; LOAD httpfs;
SELECT (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet')             AS income,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet')             AS people,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet')           AS housing,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet') AS connectivity,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet')       AS wellbeing,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet')                                AS all_indicators;
```

→ `3235 | 3235 | 3235 | 3235 | 3235 | 3235`.

Equal counts are necessary but not sufficient, so the GEOIDs themselves were
intersected:

```sql
LOAD httpfs;
SELECT count(*) AS geoids_present_in_all_six FROM (
  SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet'
  INTERSECT SELECT geoid FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/counties.parquet');
```

→ `3235` — all 3,235, so `JOIN … USING (geoid)` loses nothing in any direction.

Both queries were run with DuckDB 1.4.1 against these files as built,
immediately before this was written down, with the local `catalog/` paths
swapped in for the URLs above: the five themed collections had not yet been
uploaded to the mirror when the queries were run, so no wall-clock timings are
quoted here. Each themed file is 12.3–12.4 MB over 3,235 rows and the wide file
is 13.0 MB, most of it geometry.

A full profile of one county is one query across the five themed chunks:

```sql
LOAD httpfs;
SELECT i.geoid, i.name, i.median_hh_income::int AS income, i.pct_below_poverty AS poverty,
       p.median_age, p.pct_bachelors_plus AS degree, h.median_gross_rent::int AS rent,
       c.pct_commute_transit AS transit, w.pct_uninsured AS uninsured
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-income/county-income.parquet' i
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-people/county-people.parquet'             p USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-housing/county-housing.parquet'           h USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-connectivity/county-connectivity.parquet' c USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/counties/county-wellbeing/county-wellbeing.parquet'       w USING (geoid)
WHERE i.geoid = '26163';
```

→ `26163 | Wayne County, Michigan | 60539 | 20.8 | 37.9 | 27.58 | 1132 | 1.76 |
5.61`.

That is five files for one row. The same nine values come out of
[`counties`](counties/collection.json) in a single-file query with no join at
all — which is exactly what the sixth sibling is for.

GEOIDs nest by prefix: `substr(geoid, 1, 2)` is the state FIPS code, and `state`
is also a column with the USPS code. A county's tracts are the 11-character
GEOIDs whose first 5 characters match, and its block groups the 12-character
ones. **One trap:** Connecticut's county equivalents in the 2024 vintage are
the 9 planning regions (`09110`–`09190`, measured), not the 8 historical
counties, so a 2020-vintage Connecticut block or tract GEOID's 5-character
prefix does not match any row here.

## When to step up or down a geography

This is usually the right level. Here is the measured case for it.

Suppression, the same columns at the three steps below state:

| column | NULL at block group | NULL at tract | NULL at county |
|---|---|---|---|
| `median_hh_income` | 7.69% | 1.59% | 0.43% |
| `median_gross_rent` | 29.68% | 5.92% | 0.62% |
| `median_home_value` | 10.03% | 3.55% | 0.56% |
| `median_hh_income_white_nh` | not published | 10.04% | 2.38% |
| `median_hh_income_hispanic` | not published | 44.43% | 19.60% |
| `median_hh_income_black` | not published | 61.43% | 39.47% |
| `median_hh_income_asian` | not published | 71.27% | 53.63% |

Reliability, measured: the median `median_hh_income_cv` is **0.042** at county
against 0.125 at tract and 0.202 at block group, and **0.1%** of county income
medians are over the 0.40 "unreliable" line against 1.5% of tracts and 11.8% of
block groups. At county level exactly 2 of the 3,221 published medians are
above 0.40, maximum 0.53.

- **Step down to [tracts](../tracts/AGENTS.md)** when the question is about
  variation *inside* a county — which is most of what counties hide. 85,184
  rows against 3,235, at five times the rent-median suppression and three times
  the median CV. Tracts are also the finest geography the
  `county-wellbeing` columns exist at: health insurance, disability, nativity
  and income by race are published for tracts and not below.
- **Step down to [block groups](../block-groups/AGENTS.md)** only when the
  question is genuinely sub-tract, and accept that nearly three block groups in
  ten have no rent median and one income median in eight is unreliable. There
  are only four themed collections there — no block-group twin for
  `county-wellbeing` — so an equity or health question cannot step down that
  far at all.
- **Stay here** for national rankings, for anything that will be quoted as a
  single number for a named place, for a race-and-income comparison, and for
  any claim that has to survive a margin-overlap test. The
  [`county-income`](county-income/AGENTS.md) guide works through a national
  top-six ranking where the first four ranks hold and the fifth and sixth are a
  statistical tie — that test is only affordable at this geography and above.
- **Step up to [states](../states/AGENTS.md)** when even county margins are
  too wide for the question. 56 rows, 52 with ACS data, and the median
  `median_hh_income_cv` is **0.004** (measured). It is also the only geography
  where all four race-iteration medians are published for every row that has
  data — 52 of 52, measured — so a race-and-income comparison that needs
  complete coverage belongs there, not here. The price is that a state is not a
  place anyone lives in.
- **[Blocks](../blocks/AGENTS.md)** carry 2020 Decennial counts only — a
  different survey and vintage, not a finer version of these numbers.
- **Not a step up or down:** [ZCTAs](../zctas/AGENTS.md),
  [places](../places/AGENTS.md) and
  [congressional districts](../congressional-districts/AGENTS.md) are parallel
  geographies, not levels. ZCTAs nest in nothing, places nest in a state but
  not in a county, and relating a district to counties is a spatial operation.
  None of them joins to these rows by prefix.

## Shared quirks

- **`population_moe` is NULL on 3,103 of the 3,235 rows** (measured). Read
  `population` here as a count to use rather than an estimate to put an
  interval on.
- **Nine more margins are NULL on exactly those same rows.** Measured, and
  verified row by row — all 3,235 rows agree: `pct_under_18_moe`,
  `pct_65_plus_moe`, `pct_white_nh_moe`, `pct_black_moe`, `pct_native_moe`,
  `pct_asian_moe`, `pct_hispanic_moe`, `pct_people_of_color_moe` and
  `pct_foreign_born_moe` stand or fall with `population_moe`. Those are
  precisely the shares denominated on a total-population line (`B01001` line 1,
  `B03002` line 1, `B05002` line 1, as `tools/column_docs.py` records). The
  **estimates** are complete on all 3,222 rows with ACS data; it is the
  interval that is unavailable, so a significance test on an age share, a race
  share or the foreign-born share is not possible here for 96% of rows. Ask it
  at state level, or present point values and say so. Run
  `count(<col>_moe)` before writing any significance test against these files.
- **Never write `sqrt(sum(moe*moe))` over one of those columns** without a NULL
  check — quadrature over a NULL-bearing column returns NULL.
- Every other estimate carries `<name>_moe` at the **90%** confidence level.
  Headline columns also carry `<name>_cv` = `moe / 1.645 / estimate`: under 0.12
  reliable, 0.12–0.40 caution, over 0.40 unreliable. `county-people` has **no
  `_cv` columns at all** — use `median_age_moe` or `pct_bachelors_plus_moe`
  there, the only two of its margins that are populated.
- **Never sum or average a median.** A region's median is not derivable from
  its parts'. To sum counts, add margins in quadrature (`sqrt(sum(moe*moe))`) —
  and note that counties *do* sum exactly to their state row for counts, which
  makes it a usable consistency check on a rollup (measured, in
  [county-housing](county-housing/AGENTS.md)).
- **`pct_commute_transit` is the one column that still needs a reliability gate
  at this geography.** It publishes a `_cv` for only 2,417 of 3,235 counties —
  the other 818 are 13 island areas plus 805 whose estimate is exactly 0.0 —
  and 69.9% of those 2,417 are above 0.40 (measured). Most counties have too
  little transit commuting to estimate a share precisely, which is a finding
  rather than a defect.
- In `county-wellbeing` the NULLs are part of the subject: the four
  race-iteration medians are published on 97.62% / 80.40% / 60.53% / 46.37% of
  counties (white_nh / hispanic / black / asian, measured). A blank is "not
  published here", never "low income", and quoting a racial income gap without
  its denominator overstates the coverage — 1,910 counties publish both the
  Black and non-Hispanic White medians, 1,193 of them at a CV under 0.20
  (measured).
- Jam values are already NULL. No jam filtering is needed, but NULLs reduce the
  row count of an aggregate and `avg()` skips them silently. A `_cv` that is
  NULL where the estimate exists usually means the estimate is exactly 0.
- Percentages are 0–100, not 0–1, and their margins are on the same scale.
- `pct_people_of_color` is a complement (`100 − pct_white_nh`) and adds no
  information; the four non-Hispanic race shares plus `pct_hispanic` sum to a
  median of 96.09, not 100, because B03002's remaining non-Hispanic lines are
  not carried (measured).
- `population` is the ACS 5-year estimate (B01003), not a 2020 Decennial count,
  and it is not a household count — join `households` from
  [county-housing](county-housing/collection.json) for household-denominated
  work.
- 13 island-area county equivalents carry geometry and NULL ACS values (AS 5,
  GU 1, MP 4, VI 3, measured). `35011` De Baca County, New Mexico, population
  1,576, is the one county with ACS data and no publishable income median.
- Connecticut's county equivalents are the 9 planning regions `09110`–`09190`
  in the 2024 vintage (measured), so a 2020-vintage GEOID prefix will not
  match.
- Geometry is the 500k cartographic boundary files, shoreline-clipped,
  EPSG:4326 — good for mapping and point-in-polygon, not for area measurement.
  `aland_sqkm` comes from the boundary file's own `ALAND`, not from the
  polygon.
- **PMTiles here are real county polygons at every zoom** — the band is
  `0-10:geom`, there are few enough features to draw them all at a national
  zoom, so these archives need none of the coarser-geography coarse-zoom bands
  the tract, block-group, ZCTA and place collections carry. These are in fact
  the polygons those collections' coarse zooms are built from. `*_moe` columns
  are excluded from every tile at every zoom; `*_cv` columns are kept, so one
  style can grey out an unreliable value at any zoom. Statistics come from the
  GeoParquet, always.

## Where to look next

- Per-collection schemas, NULL stories and 4–5 tested recipes each:
  [county-income](county-income/AGENTS.md), [county-people](county-people/AGENTS.md),
  [county-housing](county-housing/AGENTS.md),
  [county-connectivity](county-connectivity/AGENTS.md),
  [county-wellbeing](county-wellbeing/AGENTS.md), and the wide
  [counties](counties/AGENTS.md).
- Whether a national ranking survives its margins of error, worked through on
  the top six counties by income: [county-income](county-income/AGENTS.md).
- Which margins actually exist at this geography, and the query to check:
  [county-people](county-people/AGENTS.md) and [counties](counties/AGENTS.md).
- Quoting a racial income gap with its denominator:
  [county-wellbeing](county-wellbeing/AGENTS.md).
- The counties-sum-to-the-state consistency check, and quadrature margins:
  [county-housing](county-housing/AGENTS.md) and [counties](counties/AGENTS.md).
- Looking inside a county: [tracts](../tracts/AGENTS.md) and
  [block groups](../block-groups/AGENTS.md). Stepping up:
  [states](../states/AGENTS.md).
- Cross-collection showcases spanning geographies:
  [catalog AGENTS.md](../AGENTS.md).

## License

CC0-1.0. Census Bureau data is a U.S. Government work in the public domain;
this mirror adds nothing proprietary. [data.census.gov](https://data.census.gov/)
is authoritative and nothing here is an official Census Bureau product — cite
the U.S. Census Bureau when you use the numbers.
