# Batch 3 spec: 2020 Decennial DHC (curated subset)

The blocks collection carries PL 94-171, which is redistricting counts
only. The Demographic and Housing Characteristics file adds age, sex,
household type and tenure as 100% counts with no sampling error.

## Source

Per-state zips, the same shape as the PL files `tools/build_blocks.py`
already parses:

`https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/<State>/<ss>2020.dhc.zip`

Sizes measured 2026-11-15: Alabama 203 MB, California 1,008 MB. The
national set is roughly 15 GB compressed. Download to `staging/`, one
state at a time, and delete each extract after parsing it.

Reuse the PL machinery: the geoheader is Latin-1, segments join on
LOGRECNO, and GEOCODE is the field to trust for the GEOID. See
`docs/runbook.md`.

Check `https://www2.census.gov/programs-surveys/decennial/2020/data/blockgroup/`
first. If it holds a prepared block-group extract, it may replace part of
this work. Report what you find.

## Curate, do not ingest everything

The DHC holds about 300 tables. Take only these themes:

| theme | tables | note |
|---|---|---|
| age and sex | P12 | 23 age bands by sex, the full age pyramid |
| household type | P16, P18 | household size and composition |
| tenure | H4 (and H1 for occupancy) | owner and renter counts |

Disclosure avoidance limits which tables reach which geography. Measure
the lowest available level for each table and report it. Do not write a
column of NULLs for a table that is not published at a level.

## Placement — a structural decision

Put these beside the ACS collections at the same geography, as
`block-groups/bg-age-dec2020`, `tracts/tract-age-dec2020` and so on, NOT
in a separate decennial group. The catalog's shape is geography first,
and a reader comparing age at tract level should find both sources in
one place.

Every description must state plainly that this is a 100% count from the
2020 Census, that it has no margin of error, and that it is a different
measurement from the ACS 5-year estimates beside it. Never let a reader
subtract one from the other by accident.

## Rules

- No MOE columns. No CV columns. Do not fabricate uncertainty for a
  complete count.
- Note that the 2020 Census applied differential privacy. Small counts
  carry injected noise. State this in `known_issues` for every
  collection, and link the Census disclosure-avoidance documentation.
- Tiles, styles and the regeneration chain as in `docs/runbook.md`.
- Cross-check at least three values against data.census.gov.

## Report

Rows and columns per collection, the table-by-geography availability
matrix, the three cross-checks, peak disk used, and the gate result.
