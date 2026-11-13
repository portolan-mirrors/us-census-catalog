# Agent guide — Block Groups

Guidance for AI agents and automated clients working with this geography.

**Every claim in this file is quoted from a source or measured from the data.**
The catalog-level [AGENTS.md](../AGENTS.md) covers what spans geographies, and
each collection's own `AGENTS.md` carries its columns, NULL rates and tested
queries. This file covers what the four collections share. If you cannot point
at where a fact came from, it does not belong here.

## What this geography is

A census block group is the **finest geography the Census Bureau publishes
income, housing cost, education and commuting data for** — typically 600–3,000
people. Below it there are blocks, and blocks carry 2020 Decennial counts only.
Above it there are tracts, with the same indicators and much narrower margins.

**242,298 rows** per collection, one per block group, ACS 2020–2024 5-year
estimates, geometry from the 2024 cartographic boundary files.

## Four chunks, one geography

The indicators are split into four themed collections rather than published as
one wide table, because a consumer who wants median income should not download
sixty columns and 242,298 rows:

| collection | theme | headline columns |
|---|---|---|
| [bg-income](bg-income/collection.json) ([agent guide](bg-income/AGENTS.md)) | Income & Poverty | `median_hh_income`, `per_capita_income`, `pct_below_poverty`, `pct_snap`, `pct_unemployed` |
| [bg-people](bg-people/collection.json) ([agent guide](bg-people/AGENTS.md)) | People & Education | `median_age`, `pct_under_18`, `pct_65_plus`, the five non-Hispanic race shares, `pct_hispanic`, `pct_bachelors_plus` |
| [bg-housing](bg-housing/collection.json) ([agent guide](bg-housing/AGENTS.md)) | Housing & Rent | `housing_units`, `households`, `pct_owner_occupied`, `median_gross_rent`, `median_home_value`, `pct_rent_burdened` |
| [bg-connectivity](bg-connectivity/collection.json) ([agent guide](bg-connectivity/AGENTS.md)) | Commuting & Connectivity | `hh_no_vehicle`, the B08301 commute-mode shares, `pct_commute_45min_plus`, `pct_no_internet`, `pct_no_computer` |

There is **no fifth chunk here**. Health insurance, disability, nativity and
income by race are not published by the Census Bureau at block-group level;
they are in [tracts/tract-wellbeing](../tracts/tract-wellbeing/collection.json).
Asking this geography for an uninsured rate is asking for a number that does
not exist.

Every chunk carries the same seven context columns — `geoid`, `name`, `state`,
`population`, `population_moe`, `aland_sqkm`, `pop_density` — plus `geometry`
and the `bbox` covering struct. That is deliberate: a single-theme question
never needs a join.

## The chunks join 1:1 on `geoid`

All four hold the same 242,298 `geoid` values, in the same order, with the same
geometry. Measured:

```sql
LOAD httpfs;
SELECT (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.parquet')             AS income,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/bg-people.parquet')             AS people,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet')           AS housing,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/bg-connectivity.parquet') AS connectivity;
```

→ `242298 | 242298 | 242298 | 242298`, in 6.5 s. Run against the published
URLs, 2026-11-13.

So `JOIN … USING (geoid)` is an inner join that loses nothing, and all four
chunks at once is one query:

```sql
LOAD httpfs;
SELECT i.geoid, i.median_hh_income::int AS income, pe.pct_bachelors_plus AS degree,
       h.median_gross_rent::int AS rent, c.pct_hh_no_vehicle AS no_vehicle
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/bg-income.parquet' i
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/bg-people.parquet'             pe USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/bg-housing.parquet'           h  USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/bg-connectivity.parquet' c  USING (geoid)
WHERE substr(i.geoid, 1, 5) = '11001'      -- the District of Columbia
  AND i.median_hh_income IS NOT NULL
ORDER BY i.median_hh_income DESC LIMIT 5;
```

→ `110010052021 | 250001 | 96.14 | 3501 | 46.11`, `110010055012 | 250001 |
90.27 | 3501 | 40.4`, `110010104003 | 250001 | 22.82 | 1641 | 58.63`,
`110010081002 | 250001 | 94.08 | 2498 | 8.24`, `110010083021 | 250001 | 95.1 |
2247 | 15.93`. **15.2 s** — four 60–95 MB files, so this is the expensive
shape; join only the chunks you need. Note every income reads 250,001: that is
the ACS top code, not a measurement, and the third row shows why the other
columns matter (a top-coded income with a 22.82% degree share is a different
kind of place from its neighbours).

GEOIDs nest by prefix, so one county is `substr(geoid, 1, 5)`, one tract
`substr(geoid, 1, 11)`, one state `substr(geoid, 1, 2)`. `state` is also a
column, with the USPS code.

## When to step up a geography

Block-group margins of error are wide, and suppression is common. Measured, for
the same columns at the two geographies:

| column | NULL at block group | NULL at tract |
|---|---|---|
| `median_hh_income` | 7.69% | 1.59% |
| `median_gross_rent` | 29.68% | 5.92% |
| `median_home_value` | 10.03% | 3.55% |

And on reliability (measured): the median `median_hh_income_cv` is **0.202** at
block group against **0.125** at tract, and 11.8% of block-group medians are
over the 0.40 "unreliable" line against 1.5% of tract medians.

So:

- **Stay here** when the question is genuinely sub-tract — one neighbourhood,
  a service area, a catchment — and accept the holes, greying out by `*_cv`
  rather than pretending they are not there.
- **Step up to [tracts](../tracts/AGENTS.md)** when the question is
  comparative, ranked, or mapped at state or national scale. The query is the
  same with one URL changed.
- **Step down to [blocks](../blocks/AGENTS.md)** only for counts — population,
  housing units, race and voting-age population from the 2020 Decennial. There
  is no income, education or commuting data below this geography, and a block
  rollup is a different survey and vintage, not a finer version of these
  numbers.

## Shared quirks

- Every estimate carries `<name>_moe` at the **90%** confidence level. Headline
  columns also carry `<name>_cv` = `moe / 1.645 / estimate`: under 0.12
  reliable, 0.12–0.40 caution, over 0.40 unreliable. `bg-people` has **no
  `_cv` columns at all** — use `_moe` there.
- **Never sum or average a median.** A region's median is not derivable from
  its parts'. To sum counts, add margins in quadrature (`sqrt(sum(moe*moe))`).
- `median_hh_income` is bottom-coded at 2,499 and top-coded at 250,001, and
  those 3,458 rows carry no margin of error at all (measured).
- Jam values are already NULL. No jam filtering is needed, but NULLs reduce the
  row count of an aggregate and `avg()` skips them silently.
- Percentages are 0–100, not 0–1, and their margins are on the same scale.
- `population` is the ACS 5-year estimate (B01003), not a 2020 Decennial count.
- 405 island-area block groups and 39 re-delineated Suffolk County, NY block
  groups carry geometry and NULL ACS values. 443 water-only ACS block groups
  have no polygon and so no row; their population is exactly 0.
- Geometry is the 500k cartographic boundary files, shoreline-clipped,
  EPSG:4326 — good for mapping and point-in-polygon, not for area measurement.
- PMTiles z0–z5 are **counties** and z6–z7 **tracts**, not block groups — the
  Census Bureau's own estimates for those geographies, under the same column
  names, so one style classifies every zoom — and z8–z13 are the block groups
  themselves. The tiles carry no `*_moe` columns. Statistics come from the
  GeoParquet, always.

## Where to look next

- Per-collection schemas, NULL stories and 4–5 tested recipes each:
  [bg-income](bg-income/AGENTS.md), [bg-people](bg-people/AGENTS.md),
  [bg-housing](bg-housing/AGENTS.md),
  [bg-connectivity](bg-connectivity/AGENTS.md).
- Income inequality inside one county, the `bbox` + `ST_DWithin` spatial
  pattern, and DuckDB's lat/lon axis trap: [bg-income](bg-income/AGENTS.md).
- The digital divide by income quintile:
  [bg-connectivity](bg-connectivity/AGENTS.md).
- One geography up: [tracts](../tracts/AGENTS.md). One down:
  [blocks](../blocks/AGENTS.md). Whole-country tables:
  [counties](../counties/AGENTS.md), [states](../states/AGENTS.md).
- Cross-collection showcase queries: [catalog AGENTS.md](../AGENTS.md).

## License

CC0-1.0. Census Bureau data is a U.S. Government work in the public domain;
this mirror adds nothing proprietary. [data.census.gov](https://data.census.gov/)
is authoritative and nothing here is an official Census Bureau product — cite
the U.S. Census Bureau when you use the numbers.
