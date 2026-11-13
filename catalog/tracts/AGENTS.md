# Agent guide — Census Tracts

Guidance for AI agents and automated clients working with this geography.

**Every claim in this file is quoted from a source or measured from the data.**
The catalog-level [AGENTS.md](../AGENTS.md) covers what spans geographies, and
each collection's own `AGENTS.md` carries its columns, NULL rates and tested
queries. This file covers what the five collections share. If you cannot point
at where a fact came from, it does not belong here.

## What this geography is

A census tract holds typically 1,200–8,000 people and is **the geography most
small-area social research is done at** — fine enough to separate
neighbourhoods, coarse enough that the ACS margins are usable. It is also the
finest geography for health insurance, disability, nativity and income by
race, which the Census Bureau does not publish below tract at all.

**85,184 rows** per collection, one per census tract, ACS 2020–2024 5-year
estimates, geometry from the 2024 cartographic boundary files. The ACS release
has 85,382 tracts; the 338 water-only `9900xx`-style tracts have no polygon in
the cartographic boundary files and so no row here, and their population is
exactly 0, so nothing is lost.

## Five chunks, one geography

The same four themed collections as [block groups](../block-groups/AGENTS.md),
plus a fifth that has no block-group twin:

| collection | theme | headline columns |
|---|---|---|
| [tract-income](tract-income/collection.json) ([agent guide](tract-income/AGENTS.md)) | Income & Poverty | `median_hh_income`, `per_capita_income`, `pct_below_poverty`, `pct_snap`, `pct_unemployed` |
| [tract-people](tract-people/collection.json) ([agent guide](tract-people/AGENTS.md)) | People & Education | `median_age`, `pct_under_18`, `pct_65_plus`, the five non-Hispanic race shares, `pct_hispanic`, `pct_bachelors_plus` |
| [tract-housing](tract-housing/collection.json) ([agent guide](tract-housing/AGENTS.md)) | Housing & Rent | `housing_units`, `households`, `pct_owner_occupied`, `median_gross_rent`, `median_home_value`, `pct_rent_burdened` |
| [tract-connectivity](tract-connectivity/collection.json) ([agent guide](tract-connectivity/AGENTS.md)) | Commuting & Connectivity | `hh_no_vehicle`, the B08301 commute-mode shares, `pct_commute_45min_plus`, `pct_no_internet`, `pct_no_computer` |
| [tract-wellbeing](tract-wellbeing/collection.json) ([agent guide](tract-wellbeing/AGENTS.md)) | Health, Disability & Income by Race | `pct_uninsured`, `pct_with_disability`, `pct_foreign_born`, `group_quarters_pop`, `median_hh_income_{black,white_nh,asian,hispanic}`, `pct_below_poverty_black` |

`tract-wellbeing` is the reason an equity question belongs at this geography
and not at block group: [B27001](https://data.census.gov/table/ACSDT5Y2024.B27001),
[B18101](https://data.census.gov/table/ACSDT5Y2024.B18101) and the
`B19013B/D/H/I` race-iteration medians are published for tracts and not below.

Every chunk carries the same seven context columns — `geoid`, `name`, `state`,
`population`, `population_moe`, `aland_sqkm`, `pop_density` — plus `geometry`
and the `bbox` covering struct, so a single-theme question never needs a join.

## The chunks join 1:1 on `geoid`

All five hold the same 85,184 `geoid` values with the same geometry. Measured:

```sql
LOAD httpfs;
SELECT (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet')             AS income,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/tract-people.parquet')             AS people,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet')           AS housing,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.parquet') AS connectivity,
       (SELECT count(*) FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet')       AS wellbeing;
```

→ `85184 | 85184 | 85184 | 85184 | 85184`, in 7.8 s. Run against the published
URLs, 2026-11-13.

So `JOIN … USING (geoid)` loses nothing, and a full profile of one tract is one
query across all five:

```sql
LOAD httpfs;
SELECT i.geoid, i.name, i.median_hh_income::int AS income, i.pct_below_poverty AS poverty,
       p.median_age, p.pct_bachelors_plus AS degree, h.median_gross_rent::int AS rent,
       c.pct_commute_transit AS transit, w.pct_uninsured AS uninsured
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/tract-income.parquet' i
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/tract-people.parquet'             p USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/tract-housing.parquet'           h USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/tract-connectivity.parquet' c USING (geoid)
JOIN 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/tract-wellbeing.parquet'       w USING (geoid)
WHERE i.geoid = '53033007101';
```

→ `53033007101 | Census Tract 71.01, King County, Washington | 122365 | 8.31 |
30.6 | 74.27 | 2231 | 8.62 | 2.71`. **15.4 s** — five files, so this is the
expensive shape even for one row; join only the chunks you need. (That GEOID
came from a point-in-polygon lookup; the recipe is in
[tract-people](tract-people/AGENTS.md).)

GEOIDs nest by prefix: one county is `substr(geoid, 1, 5)`, one state
`substr(geoid, 1, 2)`. `state` is also a column, with the USPS code. A tract's
block groups are the 12-character GEOIDs whose first 11 characters match.

## When to step up or down a geography

This is usually the right level, and here is the measured case for it.

Suppression, same columns at the two finer-to-coarser steps:

| column | NULL at block group | NULL at tract |
|---|---|---|
| `median_hh_income` | 7.69% | 1.59% |
| `median_gross_rent` | 29.68% | 5.92% |
| `median_home_value` | 10.03% | 3.55% |

Reliability (measured): the median `median_hh_income_cv` is **0.125** at tract
against **0.202** at block group, and 1.5% of tract medians are over the 0.40
"unreliable" line against 11.8% of block-group medians.

- **Step down to [block groups](../block-groups/AGENTS.md)** only when the
  question is genuinely sub-tract, and accept five times the missing rent
  medians. There is no block-group twin for `tract-wellbeing`, so an equity or
  health question cannot step down at all.
- **Stay here** for comparative, ranked or mapped work at state or national
  scale.
- **Step up to [counties](../counties/AGENTS.md) or
  [states](../states/AGENTS.md)** when the answer will be quoted as a single
  number, or when a race-iteration median is the subject:
  `median_hh_income_black` is NULL on 61.43% of tracts against 39.47% of
  counties, and `median_hh_income_asian` on 71.27% against 53.63%. Those
  collections carry all 112 columns in one wide table, so no chunk join is
  needed.
- **[Blocks](../blocks/AGENTS.md)** carry 2020 Decennial counts only — a
  different survey and vintage, not a finer version of these numbers.

## Shared quirks

- Every estimate carries `<name>_moe` at the **90%** confidence level. Headline
  columns also carry `<name>_cv` = `moe / 1.645 / estimate`: under 0.12
  reliable, 0.12–0.40 caution, over 0.40 unreliable. `tract-people` has **no
  `_cv` columns at all** — use `_moe` there.
- **Never sum or average a median.** A region's median is not derivable from
  its parts'. To sum counts, add margins in quadrature (`sqrt(sum(moe*moe))`).
- In `tract-wellbeing` the NULLs are the subject: the four race-iteration
  medians are published on 89.96% / 55.57% / 38.57% / 28.73% of tracts
  (white_nh / hispanic / black / asian, measured). A blank is "not published
  here", never "low income", and quoting a racial income gap without its
  denominator overstates the coverage.
- Jam values are already NULL. No jam filtering is needed, but NULLs reduce the
  row count of an aggregate and `avg()` skips them silently.
- Percentages are 0–100, not 0–1, and their margins are on the same scale.
- A share whose margin is exactly 0.0 is a flag to inspect, not high precision
  — a tract can be almost entirely group quarters and have single-digit
  household counts. `population` is not a household count.
- `population` is the ACS 5-year estimate (B01003), not a 2020 Decennial count.
- 126 island-area tracts and 14 re-delineated Suffolk County, NY tracts carry
  geometry and NULL ACS values.
- Geometry is the 500k cartographic boundary files, shoreline-clipped,
  EPSG:4326 — good for mapping and point-in-polygon, not for area measurement.
- PMTiles z0–z5 are **counties**, not tracts — the Census Bureau's own county
  estimates under the same column names, so one style classifies every zoom —
  and z6–z12 are the tracts themselves. The tiles carry no `*_moe` columns.
  Statistics come from the GeoParquet, always.

## Where to look next

- Per-collection schemas, NULL stories and 4–5 tested recipes each:
  [tract-income](tract-income/AGENTS.md), [tract-people](tract-people/AGENTS.md),
  [tract-housing](tract-housing/AGENTS.md),
  [tract-connectivity](tract-connectivity/AGENTS.md),
  [tract-wellbeing](tract-wellbeing/AGENTS.md).
- "Which tract am I in" point-in-polygon with a `bbox` prefilter:
  [tract-people](tract-people/AGENTS.md).
- Income by race beside overall income, NULL-aware:
  [tract-wellbeing](tract-wellbeing/AGENTS.md).
- Density against car ownership and transit, and other cross-collection
  showcases: [catalog AGENTS.md](../AGENTS.md).

## License

CC0-1.0. Census Bureau data is a U.S. Government work in the public domain;
this mirror adds nothing proprietary. [data.census.gov](https://data.census.gov/)
is authoritative and nothing here is an official Census Bureau product — cite
the U.S. Census Bureau when you use the numbers.
