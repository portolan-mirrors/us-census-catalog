# Agent guide — Congressional Districts (119th Congress)

Guidance for AI agents and automated clients working with this geography.

**Every claim in this file is quoted from a source or measured from the data.**
The catalog-level [AGENTS.md](../AGENTS.md) covers what spans geographies, and
each collection's own `AGENTS.md` carries its columns, NULL rates and tested
queries. This file covers what the six collections share. If you cannot point
at where a fact came from, it does not belong here.

## What this geography is

A congressional district is the geography the ACS publishes that is **equal in
population by construction**. The 435 voting districts run from 546,488 to
1,021,191 people with a median of 771,301 (measured), because apportionment
and one-person-one-vote redistricting put roughly the same number of people in
each one. Nothing else in this catalog is built that way, and it changes how
every column behaves: the margins of error are the narrowest in the catalog —
all 15 `*_cv` columns have a median below 0.11 — and the spread of every rate
is far tighter than anywhere else, so class breaks measured at county or tract
level put almost every district in one class.

**441 rows** per collection, one per congressional district, ACS 2020–2024
5-year estimates, geometry from the 2024 cartographic boundary files.

**These are the districts of the 119th Congress**, the vintage this ACS release
tabulates. Three independent confirmations, two of them re-measured for this
restructure: the release's own summary-level prefix is `5001900US` (the `19`),
the cartographic boundary file is `cb_2024_us_cd119_500k` and carries
`CDSESSN = '119'` on all 441 features (counted: one group, 441 rows), and the
Census Bureau's
[ACS geography boundaries by year](https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year/2024.html)
lists "Congressional District, Delegate District DC, Resident Commissioner
District PR" with the vintage "119th Congress of the United States".

**District numbers are not stable across congresses.** A `geoid` here is not
the same ground as the same `geoid` in an earlier congress; these estimates are
a cross-section of the 119th Congress's lines and **must never be read as a
time series**. Any "change" computed against another release's district table
is a boundary change until proven otherwise, and a district-level table from
another congress must never be joined to these on district number.

Three more facts about the row count, all measured:

- **441, not 435.** The 435 voting districts plus the District of Columbia
  delegate district (`1198`), Puerto Rico's Resident Commissioner district
  (`7298`) and four island-area delegate districts (`6098` American Samoa,
  `6698` Guam, `6998` Northern Mariana Islands, `7898` U.S. Virgin Islands).
  The four island-area rows carry geometry and NULL ACS values. Filter
  `state NOT IN ('DC','PR','AS','GU','MP','VI')` for the 435 voting districts,
  or `population IS NOT NULL` for the 437 rows with data.
- **Three ACS rows have no polygon here**: `09ZZ`, `17ZZ` and `33ZZ`, the
  water-only pseudo-districts of Connecticut, Illinois and New Hampshire. The
  ACS release tabulates 440 district rows (counted in the downloaded B01003
  summary file); 437 are here, those three are not, and the four island-area
  districts are here with no ACS row — 437 + 4 = 441. Their ACS rows read
  `0|14`, `0|13` and `0|12`: population exactly 0, so nothing is lost. A
  pipeline that expects every ACS district GEOID to resolve to a polygon must
  still handle them.
- **`geoid` is 4 characters** — state FIPS (2) + district (2) — zero-padded:
  `0612`, not `CA12` and not `612`. At-large states use `00` (AK, DE, ND, SD,
  VT, WY); the non-voting delegate districts use `98`.

## Six collections, one geography

Five themed collections mirroring the [tract](../tracts/AGENTS.md) set, plus
the original wide table as a sixth child:

| collection | theme | headline columns |
|---|---|---|
| [cd-income](cd-income/collection.json) ([agent guide](cd-income/AGENTS.md)) | Income & Poverty | `median_hh_income`, `per_capita_income`, `pct_below_poverty`, `pct_snap`, `pct_unemployed` |
| [cd-people](cd-people/collection.json) ([agent guide](cd-people/AGENTS.md)) | People & Education | `median_age`, `pct_under_18`, `pct_65_plus`, the four non-Hispanic race shares, `pct_hispanic`, `pct_people_of_color`, `pct_bachelors_plus` |
| [cd-housing](cd-housing/collection.json) ([agent guide](cd-housing/AGENTS.md)) | Housing & Rent | `housing_units`, `households`, `pct_owner_occupied`, `median_gross_rent`, `median_home_value`, `pct_rent_burdened` |
| [cd-connectivity](cd-connectivity/collection.json) ([agent guide](cd-connectivity/AGENTS.md)) | Commuting & Connectivity | `hh_no_vehicle`, the B08301 commute-mode shares, `pct_commute_45min_plus`, `pct_no_internet`, `pct_no_computer` |
| [cd-wellbeing](cd-wellbeing/collection.json) ([agent guide](cd-wellbeing/AGENTS.md)) | Health, Disability & Income by Race | `pct_uninsured`, `pct_with_disability`, `pct_foreign_born`, `group_quarters_pop`, `median_hh_income_{black,white_nh,asian,hispanic}`, `pct_below_poverty_black` |
| [congressional-districts](congressional-districts/collection.json) ([agent guide](congressional-districts/AGENTS.md)) | All Indicators | all 112 columns in one table — every column above, no join needed |

Column counts: income 23, people 29, housing 32, connectivity 30, wellbeing
34, wide 112. Every themed chunk carries the same seven context columns —
`geoid`, `name`, `state`, `population`, `population_moe`, `aland_sqkm`,
`pop_density` — plus `geometry` and the `bbox` covering struct, so a
single-theme question never needs a join.

**The wide table's data files sit one directory up.** The 2026-11-15
restructure moved `collection.json`, `README.md` and `styles/` into
`congressional-districts/congressional-districts/`, and left the `.parquet` and
`.pmtiles` where they were:

```
congressional-districts/cd-income/cd-income.parquet                 <- themed child
congressional-districts/congressional-districts.parquet             <- wide table's DATA
congressional-districts/congressional-districts/collection.json     <- wide table's METADATA
congressional-districts/catalog.json                                <- this group
```

**The chunks are not a download saving.** Over 99% of each of these files is
`geometry` — 99.29% to 99.48% across the five, 8,815,141 of 8,861,372 bytes of
column data in `cd-income.parquet`, measured with `parquet_metadata` — so
every file in this group is about 8.9 MB and the wide one is 9.0 MB. Pick a
chunk for its column set and its styles; pick the wide table whenever a
question crosses themes.
Column pruning still works: a query that does not select `geometry` reads from
the other 45 KB.

## The chunks join 1:1 on `geoid`

All six hold the same 441 `geoid` values with the same geometry. Measured:

```sql
LOAD httpfs;
SELECT (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet')             AS income,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/cd-people.parquet')             AS people,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/cd-housing.parquet')           AS housing,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet') AS connectivity,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet')       AS wellbeing,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/congressional-districts.parquet')         AS wide;
```

→ `441 | 441 | 441 | 441 | 441 | 441`, and the six-way `INTERSECT` of their
`geoid` columns returns 441 as well. (Run with DuckDB 1.4.1 against the local
`catalog/` copies, because the five themed files had not yet been uploaded to
the mirror — so no wall-clock timing is quoted. The wide file is unchanged on
the mirror.)

So `JOIN … USING (geoid)` loses nothing, and a full profile of one district is
one query across all five themed chunks:

```sql
LOAD httpfs;
SELECT i.geoid, i.name, i.population, i.median_hh_income::int AS income,
       i.pct_below_poverty AS poverty, p.median_age, p.pct_bachelors_plus AS degree,
       h.median_gross_rent::int AS rent, c.pct_commute_transit AS transit,
       w.pct_uninsured AS uninsured
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-income/cd-income.parquet' i
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-people/cd-people.parquet'             p USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-housing/cd-housing.parquet'           h USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-connectivity/cd-connectivity.parquet' c USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/congressional-districts/cd-wellbeing/cd-wellbeing.parquet'       w USING (geoid)
WHERE i.geoid = '0612';
```

→ `0612 | Congressional District 12, California | 748393 | 108648 | 12.54 |
38.0 | 54.06 | 2133 | 11.67 | 4.54`.

Five files for one row is the expensive shape — and at this geography it is
also the unnecessary one. The same row is one file away in the
[wide table](congressional-districts/AGENTS.md), which holds all 112 columns
for 9.0 MB against the chunks' 8.9 MB each. Join chunks when you want two
themes' columns *and* a themed collection's styles; otherwise go wide. (The
$108,648 matches the build's data.census.gov spot check for CA-12.)

Only one GEOID prefix join exists: `substr(geoid, 1, 2)` is the state FIPS
code, which reaches [`states`](../states/states/collection.json) and the themed
[`state-income`](../states/state-income/collection.json) and friends. **Nothing
finer joins by prefix.** District boundaries follow 2020 census blocks, not
counties or tracts, so relating a district to the tracts, block groups or
counties inside it is a spatial operation — `bbox` prefilter plus
`ST_Intersects`, with an area share to tell the real overlaps from the slivers.
The worked example is recipe 5 in
[congressional-districts/AGENTS.md](congressional-districts/AGENTS.md): three
counties intersect CA-12 and one of them is 99.96% of it.

## When to step up or down a geography

Districts are the right level for "how do the 435 compare" and for any question
whose answer is addressed to a member of Congress. They are the wrong level for
anything sub-district, because a district averages ~770,000 people over
neighbourhoods that differ by a factor of three. Measured, across the four
levels a district question can move between:

| geography | rows | `median_hh_income` NULL | median `median_hh_income_cv` | `median_hh_income_black` NULL |
|---|---|---|---|---|
| state | 56 | 7.14% | 0.004 | 7.14% |
| **congressional district** | **441** | **0.91%** | **0.010** | **0.91%** |
| county | 3,235 | 0.43% | 0.042 | 39.47% |
| tract | 85,184 | 1.59% | 0.125 | 61.43% |

(The NULL shares at state and district level are the island areas with no ACS
data at all — 4 states and 4 delegate districts — not suppression.)

- **Step up to [states](../states/AGENTS.md)** when the answer will be quoted
  as one number per state, or when a district's figure needs its state as a
  baseline. Every collection guide here carries that prefix-join recipe.
- **Stay here** for comparative, ranked or mapped work across the country's
  districts, and for equity questions: `median_hh_income_black` is published on
  99.09% of districts against 60.53% of counties and 38.57% of tracts, so a
  racial income gap that cannot be computed at tract level usually can be
  computed here.
- **Step down to [tracts](../tracts/AGENTS.md) or
  [block groups](../block-groups/AGENTS.md)** for anything inside a district,
  and accept both the wider margins (median income CV 0.125 at tract against
  0.010 here) and the spatial join. There is no block-group twin for
  `cd-wellbeing`'s theme at all.
- **[Counties](../counties/AGENTS.md)** are the other ~3,000-row level, with a
  real advantage for administrative questions and a real cost on the
  race-iteration medians (39.47% NULL against 0.91%).
- **[Blocks](../blocks/AGENTS.md)** carry 2020 Decennial counts only — a
  different survey and vintage. They are the geography these district lines
  were *drawn from*, which makes them the right source for a redistricting
  question and the wrong source for these estimates.

## Shared quirks

- **These are 119th-Congress lines and not a time series.** Repeated once more
  because it is the trap that produces confident nonsense: district numbers are
  reused across congresses for different ground.
- Every estimate carries `<name>_moe` at the **90%** confidence level. Headline
  columns also carry `<name>_cv` = `moe / 1.645 / estimate`: under 0.12
  reliable, 0.12–0.40 caution, over 0.40 unreliable. `cd-people` has **no
  `_cv` columns at all** — use `_moe` there.
- **The margins are narrow, not absent.** All 15 `*_cv` columns have a median
  below 0.11, and a `median_hh_income_cv < 0.12` filter removes nothing
  (worst CV 0.021). Two columns still need the gate:
  `median_hh_income_black_cv` reaches 0.480 with 3 districts over 0.40, and
  `pct_commute_transit_cv` reaches 0.304 with 176 districts over 0.12. And
  narrow margins still do not order a ranking: 12 of the 25 adjacent pairs in
  New York's district income ranking overlap at 90% (measured in
  [cd-income](cd-income/AGENTS.md)).
- **A NULL margin can mean "controlled, no sampling error".**
  `population_moe` and every margin derived from the total-population
  denominator — `pct_under_18_moe`, `pct_65_plus_moe`, the four non-Hispanic
  race-share margins, `pct_hispanic_moe`, `pct_people_of_color_moe`,
  `pct_foreign_born_moe` — are carried on 423 of the 441 rows. The 18 missing
  are the four island-area rows with no data plus 14 whose ACS margin is the
  jam value `-555555555`, which `tools/build_acs.py` documents as "controlled,
  no sampling error": the eight single-district jurisdictions (AK, DE, DC, ND,
  SD, VT, WY, PR) plus all four Iowa districts and both West Virginia
  districts. `group_quarters_pop_moe` is the near miss at 429 of 441. The
  estimates are published; only the margins are missing.
- **Never sum or average a median.** A region's median is not derivable from
  its parts'. To sum counts, add margins in quadrature (`sqrt(sum(moe*moe))`).
  `avg(median_age)` over districts is an average of medians — a summary of
  districts, not of people.
- **Class breaks are measured on the district distribution, not borrowed.**
  `tools/make_styles.py` records why: districts are "the tightest distribution
  in the catalog by construction — every district holds ~770,000 people, so
  median income runs p10 61k / p50 79k / p90 114k and poverty p10 7% / p90 18%.
  Counties breaks here would leave three of six classes with a handful of
  districts." The one deliberate exception is `transit-commute`, which keeps
  the catalog-wide `[0.5, 2, 5, 10, 25]` scale so a transit map reads the same
  at every geography.
- **The spread lives inside states, not across the country.** Every collection
  guide here carries a within-state spread recipe, because that is where
  equal-population districts actually differ: New York's districts run 10.9% to
  90.8% people of color and 12.6% to 84.0% owner-occupied.
- Jam values are already NULL. No jam filtering is needed, but NULLs reduce the
  row count of an aggregate and `avg()` skips them silently.
- Percentages are 0–100, not 0–1, and their margins are on the same scale.
- `population` is the ACS 5-year estimate (B01003), not a 2020 Decennial count,
  and not the apportionment population the lines were drawn to.
- Four island-area delegate districts carry geometry and NULL ACS values; three
  water-only ACS rows (`09ZZ`, `17ZZ`, `33ZZ`) have no geometry and no row.
- Geometry is the 500k cartographic boundary files (GENZ2024,
  `cb_2024_us_cd119_500k`), shoreline-clipped, EPSG:4326 — good for mapping and
  point-in-polygon, not for area measurement.
- **PMTiles are real polygons at every zoom** (band `0-10:geom`, from
  `tools/make_tiles.py`): there are few enough districts to draw them all
  nationally, so unlike the ZCTA and place collections there is no
  coarser-geography band at coarse zooms, and one style classifies every zoom.
  The tiles carry `*_cv` columns and no `*_moe` columns. Statistics come from
  the GeoParquet, always.

## Where to look next

- Per-collection schemas, NULL stories and 4–5 tested recipes each:
  [cd-income](cd-income/AGENTS.md), [cd-people](cd-people/AGENTS.md),
  [cd-housing](cd-housing/AGENTS.md),
  [cd-connectivity](cd-connectivity/AGENTS.md),
  [cd-wellbeing](cd-wellbeing/AGENTS.md).
- All 112 columns in one table, one district's national rank, and the spatial
  recipe for what is inside a district:
  [congressional-districts](congressional-districts/AGENTS.md).
- Why these collections ship their own class breaks, measured against the tract
  breaks: [cd-income](cd-income/AGENTS.md).
- Income by householder race where it is actually published, and the three
  districts whose Black-householder median is unreliable anyway:
  [cd-wellbeing](cd-wellbeing/AGENTS.md).
- The state baseline every district is compared against:
  [states](../states/AGENTS.md). Looking inside a district:
  [tracts](../tracts/AGENTS.md) and [block groups](../block-groups/AGENTS.md),
  related spatially.
- Cross-geography showcases and the catalog-wide conventions:
  [catalog AGENTS.md](../AGENTS.md).

## License

CC0-1.0. Census Bureau data is a U.S. Government work in the public domain;
this mirror adds nothing proprietary. [data.census.gov](https://data.census.gov/)
is authoritative and nothing here is an official Census Bureau product — cite
the U.S. Census Bureau when you use the numbers.
