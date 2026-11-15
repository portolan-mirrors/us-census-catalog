# AGENTS.md — Age & Sex (2020 Census) — Census Tracts

Guidance for AI agents and automated clients working with this collection. The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. Every claim below is quoted from a source or measured from the published file.

## Overview

Sex by age for 23 age bands (P12), the full 2020 Census age pyramid: a total, a male/female split, and both sexes carried through the same 23 bands from under 5 to 85 and over. `pct_under18` and `pct_65plus` are this build's own sums of the published bands (not published columns themselves), named without the ACS collections' underscores (`pct_under18`, not `pct_under_18`) on purpose, so a query against both files by column name cannot silently select one sense when it meant the other.

**85,184 rows**, one per tract, 2020 Census DHC 100% count (not an ACS estimate), table P12.

## Accessing the data

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-age-dec2020/tract-age-dec2020.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-age-dec2020/tract-age-dec2020.pmtiles`, layer `tract-age-dec2020`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-age-dec2020/collection.json` — carries a full description for every column

```sql
INSTALL httpfs; LOAD httpfs;
SELECT * FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-age-dec2020/tract-age-dec2020.parquet' LIMIT 5;
```

## Source tables

[P12](https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/), from the [2020 Census Demographic and Housing Characteristics File](https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html).

## Schema & field notes

`geoid` is 11 characters and is the join key: `substr(geoid, 1, 5)` is the county, `substr(geoid, 1, 2)` is the state FIPS code — the same GEOID a sibling ACS collection at this geography carries.

| column | type | what it is |
|---|---|---|
| `geoid` | VARCHAR | 11-character census tract GEOID — state (2) + county (3) + tract (6), e.g. `29510102200`. Joins the block-group collections on `substr(geoid, 1, 11)` and the block collection on `substr(geoid, 1, 11)`. Matches `GEOID` in the 2024 cartographic boundary tract file; the ACS `1400000US` prefix is stripped. |
| `name` | VARCHAR | Human-readable name from the cartographic boundary tract file: `NAMELSAD`, `NAMELSADCO`, `STATE_NAME` — "Census Tract 34.06, San Joaquin County, California". |
| `state` | VARCHAR | Two-letter USPS state code, carried from the DHC geoheader's own per-state build rather than read off the boundary files (tools/build_dhc.py's `STATES` list). |
| `aland_sqkm` | DOUBLE | Land area in square kilometres, rounded to 3 decimals. `ALAND / 1e6` from the cartographic boundary file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
| `total_population` | BIGINT | Total population (P12 cell `P0120001`, "Total:"), the DHC's 100% count — not the ACS people collections' `population` estimate beside it. |
| `male_total` | BIGINT | Male population (P12, "Male:"). |
| `male_under5` | BIGINT | Male population, Under 5 years (P12). |
| `male_age5_9` | BIGINT | Male population, 5 to 9 years (P12). |
| `male_age10_14` | BIGINT | Male population, 10 to 14 years (P12). |
| `male_age15_17` | BIGINT | Male population, 15 to 17 years (P12). |
| `male_age18_19` | BIGINT | Male population, 18 and 19 years (P12). |
| `male_age20` | BIGINT | Male population, 20 years (P12). |
| `male_age21` | BIGINT | Male population, 21 years (P12). |
| `male_age22_24` | BIGINT | Male population, 22 to 24 years (P12). |
| `male_age25_29` | BIGINT | Male population, 25 to 29 years (P12). |
| `male_age30_34` | BIGINT | Male population, 30 to 34 years (P12). |
| `male_age35_39` | BIGINT | Male population, 35 to 39 years (P12). |
| `male_age40_44` | BIGINT | Male population, 40 to 44 years (P12). |
| `male_age45_49` | BIGINT | Male population, 45 to 49 years (P12). |
| `male_age50_54` | BIGINT | Male population, 50 to 54 years (P12). |
| `male_age55_59` | BIGINT | Male population, 55 to 59 years (P12). |
| `male_age60_61` | BIGINT | Male population, 60 and 61 years (P12). |
| `male_age62_64` | BIGINT | Male population, 62 to 64 years (P12). |
| `male_age65_66` | BIGINT | Male population, 65 and 66 years (P12). |
| `male_age67_69` | BIGINT | Male population, 67 to 69 years (P12). |
| `male_age70_74` | BIGINT | Male population, 70 to 74 years (P12). |
| `male_age75_79` | BIGINT | Male population, 75 to 79 years (P12). |
| `male_age80_84` | BIGINT | Male population, 80 to 84 years (P12). |
| `male_age85_plus` | BIGINT | Male population, 85 years and over (P12). |
| `female_total` | BIGINT | Female population (P12, "Female:"). |
| `female_under5` | BIGINT | Female population, Under 5 years (P12). |
| `female_age5_9` | BIGINT | Female population, 5 to 9 years (P12). |
| `female_age10_14` | BIGINT | Female population, 10 to 14 years (P12). |
| `female_age15_17` | BIGINT | Female population, 15 to 17 years (P12). |
| `female_age18_19` | BIGINT | Female population, 18 and 19 years (P12). |
| `female_age20` | BIGINT | Female population, 20 years (P12). |
| `female_age21` | BIGINT | Female population, 21 years (P12). |
| `female_age22_24` | BIGINT | Female population, 22 to 24 years (P12). |
| `female_age25_29` | BIGINT | Female population, 25 to 29 years (P12). |
| `female_age30_34` | BIGINT | Female population, 30 to 34 years (P12). |
| `female_age35_39` | BIGINT | Female population, 35 to 39 years (P12). |
| `female_age40_44` | BIGINT | Female population, 40 to 44 years (P12). |
| `female_age45_49` | BIGINT | Female population, 45 to 49 years (P12). |
| `female_age50_54` | BIGINT | Female population, 50 to 54 years (P12). |
| `female_age55_59` | BIGINT | Female population, 55 to 59 years (P12). |
| `female_age60_61` | BIGINT | Female population, 60 and 61 years (P12). |
| `female_age62_64` | BIGINT | Female population, 62 to 64 years (P12). |
| `female_age65_66` | BIGINT | Female population, 65 and 66 years (P12). |
| `female_age67_69` | BIGINT | Female population, 67 to 69 years (P12). |
| `female_age70_74` | BIGINT | Female population, 70 to 74 years (P12). |
| `female_age75_79` | BIGINT | Female population, 75 to 79 years (P12). |
| `female_age80_84` | BIGINT | Female population, 80 to 84 years (P12). |
| `female_age85_plus` | BIGINT | Female population, 85 years and over (P12). |
| `pct_under18` | DOUBLE | Share of total population under 18 (`male_under5 + male_age5_9 + male_age10_14 + male_age15_17 +` the matching female bins, over `total_population`), this build's own sum of the published bands — not a column P12 itself publishes, and not the ACS people collections' `pct_under_18`. |
| `pct_65plus` | DOUBLE | Share of total population 65 and over (the six 65-and-over bands for both sexes, over `total_population`), this build's own sum — not the ACS people collections' `pct_65_plus`. |
| `geometry` | GEOMETRY('OGC:CRS84') | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary census tract file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the census tract into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| `bbox` | STRUCT(xmin DOUBLE, ymin DOUBLE, xmax DOUBLE, ymax DOUBLE) | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Data quality & usage notes

**The 2020 Census applied differential privacy.** Every count in this collection — not just the small ones — passed through the Census Bureau's disclosure avoidance system, which injects statistical noise calibrated to a privacy-loss budget. State population totals are held exact; housing unit counts and major group-quarters counts per block are held exact; everything else, including the counts in this collection, can carry injected noise, proportionally larger for a small count in a small geography than for a large one. There is no column here that quantifies that noise — see the Census Bureau's [disclosure avoidance documentation](https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/process/disclosure-avoidance.html) — so treat a single block group's count with more caution than a tract's, and a tract's with more caution than a state's.

**This is a different measurement from the ACS collections beside it, not a finer or coarser version of the same one.** The ACS `*_moe`/`*_cv` columns describe sampling error in a 5-year rolling survey; this collection has no sampling error and no margin of error because it is not a sample. Joining the two on `geoid` is fine; subtracting one's count from the other's estimate, or averaging them, treats two different measurements of two different things as if they disagreed about one.

`total_population` (P12) is the same universe as `total_population_p17` in the household collection at this geography — both are the DHC's total population count — but neither is published in this collection under the ACS `population` column name, to keep a column-name join from silently crossing collections.

## Example queries

```sql
-- Ten tracts by age & sex, descending
SELECT geoid, name, state, total_population
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-age-dec2020/tract-age-dec2020.parquet'
ORDER BY 4 DESC NULLS LAST
LIMIT 10;
```

## Related collections

This sits beside the American Community Survey collections at the same geography, not in a separate decennial group: [Income & Poverty](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/collection.json), [People & Education](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/collection.json), [Housing & Rent](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/collection.json), [Commuting & Connectivity](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/collection.json), [Health, Disability & Income by Race](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/collection.json). All of them share this collection's `geoid` and geometry and join 1:1 on `geoid` — but **do not subtract one from the other**: this is a 2020 Census 100% count with injected noise, not a 2020–2024 ACS 5-year sample estimate with a margin of error.

The same theme at the other geography this batch covers: [Age & Sex (2020 Census) — Block Groups](https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-age-dec2020/collection.json).
