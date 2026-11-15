# AGENTS.md — Tenure (2020 Census) — Census Tracts

Guidance for AI agents and automated clients working with this collection. The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. Every claim below is quoted from a source or measured from the published file.

## Overview

Housing units (H1) and tenure of occupied housing units (H4 — owned with a mortgage or loan, owned free and clear, renter occupied). `pct_owned`, `pct_rented` and `pct_vacant_2020` are this build's own shares, named apart from the ACS housing collections' `pct_owner_occupied` and `pct_vacant_units` so the two are never selected as if they were one column.

**85,184 rows**, one per tract, 2020 Census DHC 100% count (not an ACS estimate), tables H1, H4.

## Accessing the data

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-tenure-dec2020/tract-tenure-dec2020.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-tenure-dec2020/tract-tenure-dec2020.pmtiles`, layer `tract-tenure-dec2020`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-tenure-dec2020/collection.json` — carries a full description for every column

```sql
INSTALL httpfs; LOAD httpfs;
SELECT * FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-tenure-dec2020/tract-tenure-dec2020.parquet' LIMIT 5;
```

## Source tables

[H1](https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/), [H4](https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/), from the [2020 Census Demographic and Housing Characteristics File](https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html).

## Schema & field notes

`geoid` is 11 characters and is the join key: `substr(geoid, 1, 5)` is the county, `substr(geoid, 1, 2)` is the state FIPS code — the same GEOID a sibling ACS collection at this geography carries.

| column | type | what it is |
|---|---|---|
| `geoid` | VARCHAR | 11-character census tract GEOID — state (2) + county (3) + tract (6), e.g. `29510102200`. Joins the block-group collections on `substr(geoid, 1, 11)` and the block collection on `substr(geoid, 1, 11)`. Matches `GEOID` in the 2024 cartographic boundary tract file; the ACS `1400000US` prefix is stripped. |
| `name` | VARCHAR | Human-readable name from the cartographic boundary tract file: `NAMELSAD`, `NAMELSADCO`, `STATE_NAME` — "Census Tract 34.06, San Joaquin County, California". |
| `state` | VARCHAR | Two-letter USPS state code, carried from the DHC geoheader's own per-state build rather than read off the boundary files (tools/build_dhc.py's `STATES` list). |
| `aland_sqkm` | DOUBLE | Land area in square kilometres, rounded to 3 decimals. `ALAND / 1e6` from the cartographic boundary file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
| `total_housing_units` | BIGINT | Total housing units (H1 cell `P0010001` per the geoheader's own count, table `H1`, "Total"). Not the ACS housing collections' `housing_units`. |
| `occupied_total` | BIGINT | Occupied housing units (H4 cell `H0040001`, "Total:" — the universe of H4 is occupied housing units). Equals `total_households` in the household collection at this geography. |
| `owned_with_mortgage` | BIGINT | Occupied housing units owned with a mortgage or a loan (H4). |
| `owned_free_clear` | BIGINT | Occupied housing units owned free and clear, with no mortgage or loan (H4). |
| `renter_occupied` | BIGINT | Renter-occupied housing units (H4). |
| `pct_owned` | DOUBLE | Share of occupied housing units that are owner-occupied, with or without a mortgage (`(owned_with_mortgage + owned_free_clear) / occupied_total`), this build's own derived share — not the ACS housing collections' `pct_owner_occupied`. |
| `pct_rented` | DOUBLE | Share of occupied housing units that are renter-occupied (`renter_occupied / occupied_total`), this build's own derived share. |
| `pct_vacant_2020` | DOUBLE | Share of all housing units that are vacant (`(total_housing_units - occupied_total) / total_housing_units`), this build's own derived share — named apart from the ACS housing collections' `pct_vacant_units` so the two are never selected as if they were one column. |
| `geometry` | GEOMETRY('OGC:CRS84') | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary census tract file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the census tract into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| `bbox` | STRUCT(xmin DOUBLE, ymin DOUBLE, xmax DOUBLE, ymax DOUBLE) | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Data quality & usage notes

**The 2020 Census applied differential privacy.** Every count in this collection — not just the small ones — passed through the Census Bureau's disclosure avoidance system, which injects statistical noise calibrated to a privacy-loss budget. State population totals are held exact; housing unit counts and major group-quarters counts per block are held exact; everything else, including the counts in this collection, can carry injected noise, proportionally larger for a small count in a small geography than for a large one. There is no column here that quantifies that noise — see the Census Bureau's [disclosure avoidance documentation](https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/process/disclosure-avoidance.html) — so treat a single block group's count with more caution than a tract's, and a tract's with more caution than a state's.

**This is a different measurement from the ACS collections beside it, not a finer or coarser version of the same one.** The ACS `*_moe`/`*_cv` columns describe sampling error in a 5-year rolling survey; this collection has no sampling error and no margin of error because it is not a sample. Joining the two on `geoid` is fine; subtracting one's count from the other's estimate, or averaging them, treats two different measurements of two different things as if they disagreed about one.

## Example queries

```sql
-- Ten tracts by tenure, descending
SELECT geoid, name, state, total_housing_units
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-tenure-dec2020/tract-tenure-dec2020.parquet'
ORDER BY 4 DESC NULLS LAST
LIMIT 10;
```

## Related collections

This sits beside the American Community Survey collections at the same geography, not in a separate decennial group: [Income & Poverty](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-income/collection.json), [People & Education](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-people/collection.json), [Housing & Rent](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-housing/collection.json), [Commuting & Connectivity](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-connectivity/collection.json), [Health, Disability & Income by Race](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-wellbeing/collection.json). All of them share this collection's `geoid` and geometry and join 1:1 on `geoid` — but **do not subtract one from the other**: this is a 2020 Census 100% count with injected noise, not a 2020–2024 ACS 5-year sample estimate with a margin of error.

The same theme at the other geography this batch covers: [Tenure (2020 Census) — Block Groups](https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-tenure-dec2020/collection.json).
