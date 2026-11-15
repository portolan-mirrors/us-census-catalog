# AGENTS.md — Household Type (2020 Census) — Block Groups

Guidance for AI agents and automated clients working with this collection. The catalog-level [AGENTS.md](../../AGENTS.md) covers what spans collections; this file covers this collection. Every claim below is quoted from a source or measured from the published file.

## Overview

Two household tables: household type (P16 — family/nonfamily, married-couple, single-parent, living-alone) and household type including living alone by relationship to householder (P17 — spouse, child, parent, sibling, roommate, and the institutionalized/noninstitutionalized group-quarters population). `pct_family_households` and `pct_living_alone` are this build's own shares of the P16 counts.

**242,298 rows**, one per block group, 2020 Census DHC 100% count (not an ACS estimate), tables P16, P17.

## Accessing the data

- **GeoParquet** (use this for statistics): `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-household-dec2020/bg-household-dec2020.parquet`
- **PMTiles** (use this for maps): `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-household-dec2020/bg-household-dec2020.pmtiles`, layer `bg-household-dec2020`
- **STAC collection**: `https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-household-dec2020/collection.json` — carries a full description for every column

```sql
INSTALL httpfs; LOAD httpfs;
SELECT * FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-household-dec2020/bg-household-dec2020.parquet' LIMIT 5;
```

## Source tables

[P16](https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/), [P17](https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/), from the [2020 Census Demographic and Housing Characteristics File](https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html).

## Schema & field notes

`geoid` is 12 characters and is the join key: `substr(geoid, 1, 11)` is the tract, `substr(geoid, 1, 5)` is the county, `substr(geoid, 1, 2)` is the state FIPS code — the same GEOID a sibling ACS collection at this geography carries.

| column | type | what it is |
|---|---|---|
| `geoid` | VARCHAR | 12-character census block-group GEOID — state (2) + county (3) + tract (6) + block group (1), e.g. `295101022004`. The join key across the census family: `substr(geoid, 1, 11)` is the tract, `substr(geoid, 1, 5)` the county, `substr(geoid, 1, 2)` the state FIPS code. Matches `GEOID` in the Census Bureau's 2024 cartographic boundary block-group file; the summary-level prefix the ACS summary file carries on `GEO_ID` (`1500000US`) is stripped. |
| `name` | VARCHAR | Human-readable name, assembled from the cartographic boundary files with `concat_ws(', ', …)`: the block group's own `NAMELSAD`, the tract's `NAMELSAD`, then the county's `NAMELSAD` and `STATE_NAME` — "Block Group 4, Census Tract 1022, St. Louis city, Missouri". The block-group file carries only "Block Group 4", so the tract and county files supply the rest. |
| `state` | VARCHAR | Two-letter USPS state code, carried from the DHC geoheader's own per-state build rather than read off the boundary files (tools/build_dhc.py's `STATES` list). |
| `aland_sqkm` | DOUBLE | Land area in square kilometres, rounded to 3 decimals. `ALAND / 1e6` from the cartographic boundary file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
| `total_households` | BIGINT | Total households (P16 cell `P0160001`, "Total:"). Equals `occupied_total` in the tenure collection at this geography — a household and an occupied housing unit are the same count in the 2020 Census. |
| `family_households` | BIGINT | Family households (P16, "Family households:"). |
| `married_couple_family` | BIGINT | Married-couple family households (P16). |
| `other_family` | BIGINT | Family households other than married-couple — single householder with relatives present, no spouse (P16, "Other family:"). |
| `other_family_male_no_spouse` | BIGINT | Other-family households with a male householder and no spouse present (P16). |
| `other_family_female_no_spouse` | BIGINT | Other-family households with a female householder and no spouse present (P16). |
| `nonfamily_households` | BIGINT | Nonfamily households — a householder living alone or with only unrelated people (P16). |
| `living_alone` | BIGINT | Nonfamily households where the householder lives alone (P16, "Householder living alone"). |
| `not_living_alone` | BIGINT | Nonfamily households where the householder lives with at least one other, unrelated, person (P16). |
| `total_population_p17` | BIGINT | Total population (P17 cell `P0170001`, "Total:") — the same DHC total population count as `total_population` in the age collection at this geography, kept under its own name here because P17's universe includes the group-quarters population (`in_group_quarters` below) that a household table would not otherwise carry. |
| `in_households` | BIGINT | Population living in households, as opposed to group quarters (P17). |
| `householder_total` | BIGINT | Householders — the person households tables key the household's characteristics to (P17). |
| `householder_male` | BIGINT | Male householders (P17). |
| `male_living_alone` | BIGINT | Male householders living alone (P17). |
| `male_not_living_alone` | BIGINT | Male householders not living alone (P17). |
| `householder_female` | BIGINT | Female householders (P17). |
| `female_living_alone` | BIGINT | Female householders living alone (P17). |
| `female_not_living_alone` | BIGINT | Female householders not living alone (P17). |
| `spouse_opposite_sex` | BIGINT | Opposite-sex spouses of the householder (P17). |
| `spouse_same_sex` | BIGINT | Same-sex spouses of the householder (P17). |
| `partner_opposite_sex` | BIGINT | Opposite-sex unmarried partners of the householder (P17). |
| `partner_same_sex` | BIGINT | Same-sex unmarried partners of the householder (P17). |
| `biological_child` | BIGINT | Biological children of the householder (P17). |
| `biological_child_under18` | BIGINT | Biological children of the householder under 18 years (P17, a subset of `biological_child`). |
| `adopted_child` | BIGINT | Adopted children of the householder (P17). |
| `adopted_child_under18` | BIGINT | Adopted children of the householder under 18 years (P17, a subset of `adopted_child`). |
| `stepchild` | BIGINT | Stepchildren of the householder (P17). |
| `stepchild_under18` | BIGINT | Stepchildren of the householder under 18 years (P17, a subset of `stepchild`). |
| `grandchild` | BIGINT | Grandchildren of the householder (P17). |
| `grandchild_under18` | BIGINT | Grandchildren of the householder under 18 years (P17, a subset of `grandchild`). |
| `sibling` | BIGINT | Brothers or sisters of the householder (P17). |
| `parent` | BIGINT | Parents of the householder (P17). |
| `parent_in_law` | BIGINT | Parents-in-law of the householder (P17). |
| `child_in_law` | BIGINT | Sons-in-law or daughters-in-law of the householder (P17). |
| `other_relatives` | BIGINT | Other relatives of the householder not covered by another P17 category (P17). |
| `foster_child` | BIGINT | Foster children of the householder (P17). |
| `other_nonrelatives` | BIGINT | People in the household unrelated to the householder and not an unmarried partner (P17). |
| `in_group_quarters` | BIGINT | Population living in group quarters rather than a household (P17) — institutionalized facilities (correctional, nursing, juvenile and other) plus noninstitutionalized facilities (college housing, military quarters and others). See the blocks collection's `group_quarters_pop` for the P.L. 94-171 count of the same population. |
| `institutionalized` | BIGINT | Group-quarters population in institutional facilities — correctional, juvenile, nursing/skilled-nursing and other institutional facilities (P17, a subset of `in_group_quarters`). |
| `noninstitutionalized` | BIGINT | Group-quarters population in noninstitutional facilities — college/university housing, military quarters and others (P17, a subset of `in_group_quarters`). |
| `pct_family_households` | DOUBLE | Share of households that are family households (`family_households / total_households`), this build's own derived share. |
| `pct_living_alone` | DOUBLE | Share of households whose householder lives alone (`living_alone / total_households`), this build's own derived share. |
| `geometry` | GEOMETRY('OGC:CRS84') | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary block group file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the block group into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| `bbox` | STRUCT(xmin DOUBLE, ymin DOUBLE, xmax DOUBLE, ymax DOUBLE) | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Data quality & usage notes

**The 2020 Census applied differential privacy.** Every count in this collection — not just the small ones — passed through the Census Bureau's disclosure avoidance system, which injects statistical noise calibrated to a privacy-loss budget. State population totals are held exact; housing unit counts and major group-quarters counts per block are held exact; everything else, including the counts in this collection, can carry injected noise, proportionally larger for a small count in a small geography than for a large one. There is no column here that quantifies that noise — see the Census Bureau's [disclosure avoidance documentation](https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/process/disclosure-avoidance.html) — so treat a single block group's count with more caution than a tract's, and a tract's with more caution than a state's.

**This is a different measurement from the ACS collections beside it, not a finer or coarser version of the same one.** The ACS `*_moe`/`*_cv` columns describe sampling error in a 5-year rolling survey; this collection has no sampling error and no margin of error because it is not a sample. Joining the two on `geoid` is fine; subtracting one's count from the other's estimate, or averaging them, treats two different measurements of two different things as if they disagreed about one.

**Deviation from the original brief:** the spec named P16 and P18 for household type. P18 turned out to be GROUP QUARTERS POPULATION BY SEX BY AGE BY MAJOR GROUP QUARTERS TYPE — institutionalized and noninstitutionalized counts, not household composition. P17, HOUSEHOLD TYPE (INCLUDING LIVING ALONE) BY RELATIONSHIP, is the table that actually carries relationship-to-householder detail, so this collection reads P16 + P17, not P16 + P18. See docs/dhc-build-notes.md.

## Example queries

```sql
-- Ten block groups by household type, descending
SELECT geoid, name, state, total_households
FROM 'https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-household-dec2020/bg-household-dec2020.parquet'
ORDER BY 4 DESC NULLS LAST
LIMIT 10;
```

## Related collections

This sits beside the American Community Survey collections at the same geography, not in a separate decennial group: [Income & Poverty](https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/collection.json), [People & Education](https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/collection.json), [Housing & Rent](https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/collection.json), [Commuting & Connectivity](https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/collection.json). All of them share this collection's `geoid` and geometry and join 1:1 on `geoid` — but **do not subtract one from the other**: this is a 2020 Census 100% count with injected noise, not a 2020–2024 ACS 5-year sample estimate with a margin of error.

The same theme at the other geography this batch covers: [Household Type (2020 Census) — Census Tracts](https://data.source.coop/portolan-mirrors/us-census-catalog/tracts/tract-household-dec2020/collection.json).
