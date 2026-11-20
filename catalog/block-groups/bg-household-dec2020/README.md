# Household Type (2020 Census) — Block Groups

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-household-dec2020/collection.json)** · [🧭 Census Atlas](https://portolan-mirrors.github.io/us-census-catalog/#c=block-groups/bg-household-dec2020) · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-household-dec2020/bg-household-dec2020.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-household-dec2020/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

Two household tables: household type (P16 — family/nonfamily, married-couple, single-parent, living-alone) and household type including living alone by relationship to householder (P17 — spouse, child, parent, sibling, roommate, and the institutionalized/noninstitutionalized group-quarters population). `pct_family_households` and `pct_living_alone` are this build's own shares of the P16 counts.

All **242,298** census block groups in the 50 states, the District of Columbia and Puerto Rico, from the U.S. Census Bureau's [2020 Census Demographic and Housing Characteristics File](https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html) (DHC), tables P16 and P17. The DHC is a 100% count from every return, the same survey family as the [blocks](https://source.coop/portolan-mirrors/us-census-catalog/blocks/collection.json) collection's P.L. 94-171 redistricting counts, read with the same per-state zip, Latin-1 geoheader and `LOGRECNO` join — but a different table set: blocks carries race, Hispanic origin, voting-age population and housing occupancy; this carries age, sex, household type and tenure, at block-groups and tracts rather than blocks.

**No margin of error, no coefficient of variation.** A 100% count carries no sampling error, so there is nothing here to estimate the uncertainty of — every column is the Bureau's tabulated count, full stop.

**Differential privacy.** The 2020 Census protects confidentiality with a disclosure avoidance system that injects statistical noise calibrated to a privacy-loss budget, most at block level and least at state level (state population totals are held exact; smaller geographies and smaller counts carry more). A block group or tract's individual cells can be off by a few people even though the file shows no margin of error; see the Census Bureau's [disclosure avoidance documentation](https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/process/disclosure-avoidance.html) and the [DHC technical documentation](https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/demographic-and-housing-characteristics-file-and-demographic-profile/2020census-demographic-and-housing-characteristics-file-and-demographic-profile-techdoc.pdf) (Chapter 4, "Confidentiality of the Data").

**Deviation from the original brief:** the spec named P16 and P18 for household type. P18 turned out to be GROUP QUARTERS POPULATION BY SEX BY AGE BY MAJOR GROUP QUARTERS TYPE — institutionalized and noninstitutionalized counts, not household composition. P17, HOUSEHOLD TYPE (INCLUDING LIVING ALONE) BY RELATIONSHIP, is the table that actually carries relationship-to-householder detail, so this collection reads P16 + P17, not P16 + P18. See docs/dhc-build-notes.md.

This sits beside the American Community Survey collections at the same geography, not in a separate decennial group: [Income & Poverty](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/collection.json), [People & Education](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-people/collection.json), [Housing & Rent](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-housing/collection.json), [Commuting & Connectivity](https://source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-connectivity/collection.json). All of them share this collection's `geoid` and geometry and join 1:1 on `geoid` — but **do not subtract one from the other**. This is a different measurement: a 2020 Census 100% count with injected noise, not a 2020–2024 ACS 5-year sample estimate with a margin of error. The same theme at the other geography this batch covers is [Household Type (2020 Census) — Census Tracts](https://source.coop/portolan-mirrors/us-census-catalog/tracts/tract-household-dec2020/collection.json).

The PMTiles archive is one band, the collection's own features at every zoom (`tylertoo tiles`, not the county/tract pyramid the ACS collections use) — bg and tract are the two finest geographies this batch covers and there is no coarser DHC band to step up to yet. There are no `*_moe` columns to exclude: this is a 100% count, not an estimate, so there is nothing to exclude.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them.

![census](https://img.shields.io/badge/census-blue) ![2020 Census](https://img.shields.io/badge/2020_Census-blue) ![decennial census](https://img.shields.io/badge/decennial_census-blue) ![DHC](https://img.shields.io/badge/DHC-blue) ![Demographic and Housing Characteristics](https://img.shields.io/badge/Demographic_and_Housing_Characteristics-blue) ![differential privacy](https://img.shields.io/badge/differential_privacy-blue) ![disclosure avoidance](https://img.shields.io/badge/disclosure_avoidance-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![household type](https://img.shields.io/badge/household_type-blue) ![family households](https://img.shields.io/badge/family_households-blue) ![living alone](https://img.shields.io/badge/living_alone-blue) ![relationship to householder](https://img.shields.io/badge/relationship_to_householder-blue)

## Spatial Coverage

- **Bounding Box**: [-179.146711, -14.548699, -64.565599, 71.387815]

## Temporal Coverage

- **Start**: 2020-04-01T00:00:00Z
- **End**: 2020-04-01T00:00:00Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | 12-character census block-group GEOID — state (2) + county (3) + tract (6) + block group (1), e.g. `295101022004`. The join key across the census family: `substr(geoid, 1, 11)` is the tract, `substr(geoid, 1, 5)` the county, `substr(geoid, 1, 2)` the state FIPS code. Matches `GEOID` in the Census Bureau's 2024 cartographic boundary block-group file; the summary-level prefix the ACS summary file carries on `GEO_ID` (`1500000US`) is stripped. |
| name | string | Human-readable name, assembled from the cartographic boundary files with `concat_ws(', ', …)`: the block group's own `NAMELSAD`, the tract's `NAMELSAD`, then the county's `NAMELSAD` and `STATE_NAME` — "Block Group 4, Census Tract 1022, St. Louis city, Missouri". The block-group file carries only "Block Group 4", so the tract and county files supply the rest. |
| state | string | Two-letter USPS state code, carried from the DHC geoheader's own per-state build rather than read off the boundary files (tools/build_dhc.py's `STATES` list). |
| aland_sqkm | double | Land area in square kilometres, rounded to 3 decimals. `ALAND / 1e6` from the cartographic boundary file. Land only: water area is excluded, which is what makes it the right denominator for population density. |
| total_households | int64 | Total households (P16 cell `P0160001`, "Total:"). Equals `occupied_total` in the tenure collection at this geography — a household and an occupied housing unit are the same count in the 2020 Census. |
| family_households | int64 | Family households (P16, "Family households:"). |
| married_couple_family | int64 | Married-couple family households (P16). |
| other_family | int64 | Family households other than married-couple — single householder with relatives present, no spouse (P16, "Other family:"). |
| other_family_male_no_spouse | int64 | Other-family households with a male householder and no spouse present (P16). |
| other_family_female_no_spouse | int64 | Other-family households with a female householder and no spouse present (P16). |
| nonfamily_households | int64 | Nonfamily households — a householder living alone or with only unrelated people (P16). |
| living_alone | int64 | Nonfamily households where the householder lives alone (P16, "Householder living alone"). |
| not_living_alone | int64 | Nonfamily households where the householder lives with at least one other, unrelated, person (P16). |
| total_population_p17 | int64 | Total population (P17 cell `P0170001`, "Total:") — the same DHC total population count as `total_population` in the age collection at this geography, kept under its own name here because P17's universe includes the group-quarters population (`in_group_quarters` below) that a household table would not otherwise carry. |
| in_households | int64 | Population living in households, as opposed to group quarters (P17). |
| householder_total | int64 | Householders — the person households tables key the household's characteristics to (P17). |
| householder_male | int64 | Male householders (P17). |
| male_living_alone | int64 | Male householders living alone (P17). |
| male_not_living_alone | int64 | Male householders not living alone (P17). |
| householder_female | int64 | Female householders (P17). |
| female_living_alone | int64 | Female householders living alone (P17). |
| female_not_living_alone | int64 | Female householders not living alone (P17). |
| spouse_opposite_sex | int64 | Opposite-sex spouses of the householder (P17). |
| spouse_same_sex | int64 | Same-sex spouses of the householder (P17). |
| partner_opposite_sex | int64 | Opposite-sex unmarried partners of the householder (P17). |
| partner_same_sex | int64 | Same-sex unmarried partners of the householder (P17). |
| biological_child | int64 | Biological children of the householder (P17). |
| biological_child_under18 | int64 | Biological children of the householder under 18 years (P17, a subset of `biological_child`). |
| adopted_child | int64 | Adopted children of the householder (P17). |
| adopted_child_under18 | int64 | Adopted children of the householder under 18 years (P17, a subset of `adopted_child`). |
| stepchild | int64 | Stepchildren of the householder (P17). |
| stepchild_under18 | int64 | Stepchildren of the householder under 18 years (P17, a subset of `stepchild`). |
| grandchild | int64 | Grandchildren of the householder (P17). |
| grandchild_under18 | int64 | Grandchildren of the householder under 18 years (P17, a subset of `grandchild`). |
| sibling | int64 | Brothers or sisters of the householder (P17). |
| parent | int64 | Parents of the householder (P17). |
| parent_in_law | int64 | Parents-in-law of the householder (P17). |
| child_in_law | int64 | Sons-in-law or daughters-in-law of the householder (P17). |
| other_relatives | int64 | Other relatives of the householder not covered by another P17 category (P17). |
| foster_child | int64 | Foster children of the householder (P17). |
| other_nonrelatives | int64 | People in the household unrelated to the householder and not an unmarried partner (P17). |
| in_group_quarters | int64 | Population living in group quarters rather than a household (P17) — institutionalized facilities (correctional, nursing, juvenile and other) plus noninstitutionalized facilities (college housing, military quarters and others). See the blocks collection's `group_quarters_pop` for the P.L. 94-171 count of the same population. |
| institutionalized | int64 | Group-quarters population in institutional facilities — correctional, juvenile, nursing/skilled-nursing and other institutional facilities (P17, a subset of `in_group_quarters`). |
| noninstitutionalized | int64 | Group-quarters population in noninstitutional facilities — college/university housing, military quarters and others (P17, a subset of `in_group_quarters`). |
| pct_family_households | double | Share of households that are family households (`family_households / total_households`), this build's own derived share. |
| pct_living_alone | double | Share of households whose householder lives alone (`living_alone / total_households`), this build's own derived share. |
| geometry | binary | Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an omitted `crs` key. From the Census Bureau's 2024 cartographic boundary block group file (GENZ2024, 1:500,000), which clips to the shoreline — TIGER/Line would extend the block group into open water. Generalized for mapping and point-in-polygon work, not for legal-boundary or precise-area work. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for the row's geometry, with row-group statistics, so a spatial filter can skip most of the file over the network. Written by geoparquet-io, not by the Census Bureau. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./bg-household-dec2020.pmtiles | 958.0 MB | 122063d40453... |
| ./bg-household-dec2020.parquet | 89.8 MB | 122007b4ce43... |
| ./thumbnail.png | 81.4 KB | 1220a8a04a9d... |
| ./styles/default.json | 1.9 KB | 1220e29dfe8e... |
| ./styles/living-alone.json | 1.8 KB | 122093a1f94f... |
| https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/ | - | - |
| https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/demographic-and-housing-characteristics-file-and-demographic-profile/2020census-demographic-and-housing-characteristics-file-and-demographic-profile-techdoc.pdf | - | - |
| https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/demographic-and-housing-characteristics-file-and-demographic-profile/2020-dhc-table-matrix.xlsx | - | - |
| https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/process/disclosure-avoidance.html | - | - |
| https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_bg_500k.zip | 92.6 MB | 12207c4da3ed... |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./bg-household-dec2020.pmtiles")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/](https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/)

## Processing Notes

Built 2026-11-15 from the 2020 Census DHC per-state zips (https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/), downloaded one state at a time and deleted (zip and extract both) immediately after that state's rows were pulled — the national DHC source is roughly 15 GB compressed and several times larger extracted, so the build never holds more than one state on disk. tools/build_dhc.py.

Per state: the geoheader (97 fields, Latin-1, same layout PL 94-171 uses) is filtered to `SUMLEV = '150'`, `GEOCOMP = '00'` (the whole-geography total; block groups and tracts carry no other geographic component, but state and county records also carry urban/rural and housing-unit-count variants under other `GEOCOMP` values, which this filter excludes) and joined on `LOGRECNO` to the segment files carrying P16 and P17. Field positions were derived from the Census Bureau's own DHC Table Matrix (`TABLE_ID`, `SEGMENT_NUMBER`, `TOTAL_RECORDS`, `TABLE_SORT_ORDER` — cumulative field offsets within a segment, the same scheme tools/build_blocks.py documents for P.L. 94-171) and verified against the real field counts in every segment file this build reads, not assumed from the spreadsheet alone.

`GEOCODE` is the field trusted for the GEOID, matching tools/build_blocks.py. Geometry is the same 2024 cartographic boundary file the ACS collections at this geography join to (`cb_2024_us_bg_500k.zip`), so a DHC row and an ACS row for the same `geoid` always share the same polygon; the join is driven by geometry, so a geography with boundaries but no DHC row (there are none at bg/tract — measured) would keep its row with NULL values rather than disappear.

Validated: every state's P12 `total_population` sum equals the state's published 2020 apportionment population exactly (state totals are held invariant by the disclosure avoidance system — not noised); `occupied_total` (H4) equals `total_households` (P16) and `total_population_p17` (P17) equals `total_population` (P12) on every state, exactly; `male_total + female_total` equals `total_population` on every state; three values cross-checked against data.census.gov (see the build report in docs/dhc-build-notes.md).


## Attribution

U.S. Census Bureau

## License

[CC0-1.0](https://www.census.gov/about/policies/open-gov/open-data.html)

## Contact

Chris Holmes <cholmes@9eo.org>

## Known Issues

**The 2020 Census applied differential privacy.** Every count in this collection — not just the small ones — passed through the Census Bureau's disclosure avoidance system, which injects statistical noise calibrated to a privacy-loss budget. State population totals are held exact; housing unit counts and major group-quarters counts per block are held exact; everything else, including the counts in this collection, can carry injected noise, proportionally larger for a small count in a small geography than for a large one. There is no column here that quantifies that noise — see the Census Bureau's [disclosure avoidance documentation](https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/process/disclosure-avoidance.html) — so treat a single block group's count with more caution than a tract's, and a tract's with more caution than a state's.

**This is a different measurement from the ACS collections beside it, not a finer or coarser version of the same one.** The ACS `*_moe`/`*_cv` columns describe sampling error in a 5-year rolling survey; this collection has no sampling error and no margin of error because it is not a sample. Joining the two on `geoid` is fine; subtracting one's count from the other's estimate, or averaging them, treats two different measurements of two different things as if they disagreed about one.

**Deviation from the original brief:** the spec named P16 and P18 for household type. P18 turned out to be GROUP QUARTERS POPULATION BY SEX BY AGE BY MAJOR GROUP QUARTERS TYPE — institutionalized and noninstitutionalized counts, not household composition. P17, HOUSEHOLD TYPE (INCLUDING LIVING ALONE) BY RELATIONSHIP, is the table that actually carries relationship-to-householder detail, so this collection reads P16 + P17, not P16 + P18. See docs/dhc-build-notes.md.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
