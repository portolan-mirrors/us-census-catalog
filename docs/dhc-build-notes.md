# DHC subset build notes

How `catalog/<group>/{bg,tract}-{age,household,tenure}-dec2020/` is built,
where the field positions came from, and what was checked against the
Census Bureau's own published control totals. See `docs/spec-dhc.md` for
the brief and `docs/runbook.md` for the shared build traps.

Build script: [`tools/build_dhc.py`](../tools/build_dhc.py).

## Sources

| What | URL | Vintage |
| --- | --- | --- |
| Per-state counts | `https://www2.census.gov/programs-surveys/decennial/2020/data/demographic-and-housing-characteristics-file/{State_Name}/{ab}2020.dhc.zip` | 2020 Census DHC |
| Table matrix (field positions) | `.../complete-tech-docs/.../2020-dhc-table-matrix.xlsx` | same release |
| Geoheader layout | `.../complete-tech-docs/.../geoheader-2020-dhc-state.xlsx` | same release |
| Geometry | `staging/geo/cb_2024_us_{bg,tract}_4326.parquet` — reused from the ACS build, not re-downloaded | GENZ2024 |

52 state archives (50 + DC + PR), ~15 GB compressed. Downloaded, extracted,
read and deleted one state at a time — `staging/dhc-cache/` and
`staging/dhc-scratch/` never hold more than one state's bytes. Only the
small per-state extract (a few hundred KB, bg+tract rows for the 5 target
tables) persists between states, in `staging/dhc-build/`.

## Field positions: where they came from

The DHC Table Matrix spreadsheet's `DHC Table_Segments` sheet gives
`TABLE_ID`, `SEGMENT_NUMBER`, `TOTAL_RECORDS` and `TABLE_SORT_ORDER` for
every table. Within a segment, a table's first field sits at
`5 + sum(TOTAL_RECORDS of every table with a lower TABLE_SORT_ORDER)`
(0-based; the first 5 fields of every segment file are the link fields
FILEID, STUSAB, CHARITER, CIFSN, LOGRECNO) — the same cumulative-offset
scheme `tools/build_blocks.py` documents for P.L. 94-171. Derived
positions:

| table | segment | 0-based start | cells |
| --- | --- | --- | --- |
| H1 (total housing units) | 1 | 5 | 1 |
| H4 (tenure) | 1 | 13 | 4 |
| P12 (sex by age) | 6 | 149 | 49 |
| P16 (household type) | 13 | 228 | 9 |
| P17 (household type incl. living alone, by relationship) | 14 | 185 | 31 |

Every position was verified against the real field count of the
corresponding segment file in Delaware's zip (`NFIELDS` in
`tools/build_dhc.py`: 239/247/255/216 fields for segments 1/6/13/14),
not trusted from the spreadsheet alone.

Geoheader fields (97, same layout as P.L. 94-171): `SUMLEV`=2, `GEOCOMP`=4,
`LOGRECNO`=7, `GEOCODE`=9, `STATE`=12, `COUNTY`=14, `PLACE`=29, `TRACT`=32,
`BLKGRP`=33 (0-based). `GEOCODE` is the field trusted for the GEOID.
Block groups and tracts are `SUMLEV` `150`/`140`, `GEOCOMP` `'00'` (the
whole-geography total; `GEOCOMP` only varies at state/county level in this
file — urban/rural and housing-unit-count subsets — and both are excluded
by the `'00'` filter).

## Spec correction: P16 + P17, not P16 + P18

`docs/spec-dhc.md` names P16 and P18 for "household type". Measured
against the table matrix and the real Delaware segment 15 file: **P18 is
GROUP QUARTERS POPULATION BY SEX BY AGE BY MAJOR GROUP QUARTERS TYPE** —
institutionalized/noninstitutionalized counts, not household composition.
**P17, HOUSEHOLD TYPE (INCLUDING LIVING ALONE) BY RELATIONSHIP**, is the
table that actually carries relationship-to-householder detail (spouse,
child, parent, sibling, roommate) plus the household-size signal
("living alone" / "not living alone") the spec's "household size and
composition" note was describing. This build reads P16 + P17.

## Checked: `https://www2.census.gov/programs-surveys/decennial/2020/data/blockgroup/`

Per the spec, checked before building. It holds only `SRR_<fips>_1014.csv`
/ `SRR_<fips>_1028.csv` files — Block Group **Self-Response Rates**
(2020 Census mail-back response rates, rounded to the nearest 10, one
CSV per state, defined in `SRR_Definitions.pdf`) — not a prepared
demographic extract. It does not overlap or replace any part of this
batch.

## Geography and table availability

P12, P16, P17, H1 and H4 are all base ("PH") tables, published at every
summary level the DHC carries, block through state — confirmed by the
`sl-sequence-list-dhc-state-ph.xlsx` summary-level list, which carries no
per-table restriction. This batch builds **block groups and tracts only**
(`docs/spec-dhc.md`'s two named examples): every one of the five tables is
present, non-null and internally consistent at both geographies for every
one of the 242,298 block groups and 85,184 tracts the 2024 cartographic
boundary files carry (minus the island-area rows below). County, state,
place and ZCTA are not a disclosure-avoidance gap — the same per-state
files carry those SUMLEVs too — they are simply out of scope for this
batch; the per-state harvester (`build_state` in `tools/build_dhc.py`)
would need one more SUMLEV branch and an assembly pass per level to add
them.

**Congressional districts are excluded, not deferred.** The DHC geoheader
carries `CD116`, `CD118` and `CD119` columns; measured against Delaware's
one at-large district record, `CD116` is populated and `CD118`/`CD119`
are both NULL. The 2020 Census tabulates congressional districts to the
116th Congress (the districts in effect on Census Day, April 1, 2020),
while this catalog's `congressional-districts` collection is built from
`cb_2024_us_cd119_500k` (119th Congress). Most states redistricted between
the 116th and 119th Congresses, so joining DHC data to the 119th-Congress
polygons by GEOID would attach the wrong district's population to the
wrong current boundary in most states — a correctness bug, not a cosmetic
gap, so this batch does not build it.

## Connecticut

The 2020 Census (DHC included, same as blocks' P.L. 94-171) carries
Connecticut's old 8-county GEOID prefixes. The 2024 cartographic boundary
files this build joins to carry the 9 planning regions that replaced them
in 2022. The tract's 6-digit number (tracts) or its trailing 7 digits
(tract + block group, for block groups) is preserved across the change,
so `tools/build_dhc.py`'s `theme_select()` crosswalks on that before the
join — the same fix `tools/build_tile_staging.py` applies to blocks.
Caught by the population cross-check below, which was short by exactly
Connecticut's population (3,605,944) before the fix.

## Validated

- **Every state's total population** (`sum(total_population)` in the age
  collection, grouped by `state`) matches the Census Bureau's own
  [2020 apportionment population file]
  (https://www2.census.gov/programs-surveys/decennial/2020/data/apportionment/apportionment.csv)
  exactly, for all 52 states/DC/PR — 0 mismatches.
- **National total housing units**, 50 states + DC:
  `sum(total_housing_units)` in the tenure collection, excluding Puerto
  Rico = **140,498,736**, the figure the Census Bureau published with the
  August 2021 redistricting data release.
- `occupied_total` (H4) = `total_households` (P16) exactly, every row.
- `total_population_p17` (P17) = `total_population` (P12) exactly, every
  row.
- `male_total + female_total` = `total_population`, and the 23 age bins
  per sex sum to that sex's total, exactly, every row.
- National total population, tract level: **334,735,155** — the same
  figure `tools/build_blocks.py` pins for the blocks collection (50
  states + DC + PR).
- 405 block groups / 126 tracts carry geometry (2024 cartographic
  boundary) but no DHC row: the same island-area gap the ACS collections
  at this geography already document (American Samoa, Guam, the Northern
  Mariana Islands and the U.S. Virgin Islands have no DHC data because
  the Island Areas run a separate decennial-only program) — not a new
  gap this build introduced.
