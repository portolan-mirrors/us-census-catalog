# Batch 4 spec: the 2015-2019 vintage and the trends group

This batch gives the catalog a time dimension. Read
`docs/spec-income-depth.md` first for how a vintage rebuild flows.

## Part 1: ingest the 2015-2019 vintage

The 2019 release ships a table-based prototype in the SAME format the
pipeline reads today. Verified 2026-11-15:

- Data: `https://www2.census.gov/programs-surveys/acs/summary_file/2019/prototype/5YRData/acsdt5y2019-<table>.dat`
- Header: `GEO_ID|B19013_E001|B19013_M001`, identical to 2024.
- Shells: `.../2019/prototype/ACS2019_Table_Shells.csv`
- Geos: `.../2019/prototype/Geos20195YR.csv`, 579,680 rows, including
  220,333 block groups and 74,001 tracts.

### Findings already measured (2026-11-16), do not re-derive

The re-pinning was done and verified. All 55 shell pins and all 120
(table, line) pairs across 32 tables resolve to the SAME line with the
SAME concept in 2019 as in 2024. The derived groups (UNDER18, OVER65,
NOINS, DISAB) and the four B17001 poverty-by-age lists are unchanged
too. Nothing moved.

Two label changes on unchanged lines:

- `B05002` line 13 is "Foreign born:" in 2019 and "Foreign-born:" in
  2024. The pin's substring carries the hyphen, so this check FAILS
  against 2019 unless the test normalizes the hyphen.
- `B08301` line 10 is "Public transportation (excluding taxicab):" in
  2019. The existing substring already matches. No change needed.

**`specs.LEVELS` prefixes are vintage-specific and two of them change.**
Measured against the real 2019 file, not assumed:

| level | 2019 | 2024 |
|---|---|---|
| congressional district | `5001600US` (437, 116th) | `5001900US` (441, 119th) |
| ZCTA | `8600000US` (33,120) | `860Z200US` (33,791) |
| block group | `1500000US` (220,333) | same |
| tract | `1400000US` (74,001) | same |
| county | `0500000US` (3,220) | same |
| state | `0400000US` (52) | same |

A 2019 run that reuses the 2024 prefixes extracts ZERO rows for
congressional districts and ZCTAs. It fails silently, because an empty
filter is not an error.

Geometry files confirmed present at
`https://www2.census.gov/geo/tiger/GENZ2019/shp/cb_2019_us_<level>_500k.zip`.

**Re-pin every Spec against ACS2019_Table_Shells.csv.** Do not assume the
2024 line numbers hold. Table definitions drift between vintages: lines
are added, split and redefined. This is the real work of this part, and
a wrong line number produces a wrong number silently.

**Then prove the prototype.** It is labelled a prototype, so do not trust
it on faith. Validate against the Census API, which serves ACS 5-year
for 2019:

- `https://api.census.gov/data/2019/acs/acs5?get=<vars>&for=<level>:*&in=<parents>`
- Sample, do not bulk pull. Take a stratified sample across every
  summary level the catalog uses, block groups included, large enough to
  be convincing — target a few thousand compared values in a few hundred
  requests.
- Report the match rate per indicator and per summary level. Any
  mismatch stops this batch. Then rebuild from the production
  sequence-based files under `.../2019/data/5_year_seq_by_state/`
  instead, and say so.

Geometry: 2015-2019 uses 2010-vintage tract and block-group boundaries.
Fetch the matching cartographic boundary files. Do NOT reuse the 2020
geometry.

## Part 2: the trends group

A new group, `catalog/trends/`, in long form: one row per (geoid,
period). Carry about a dozen headline indicators with their margins, not
all 112 columns.

Tier the work by how honest it can be:

1. **county and state first.** These are stable across both vintages, so
   no crosswalk is needed and the result is a published estimate at both
   ends. Connecticut is the exception the catalog already solves; apply
   the same crosswalk.
2. **tract and block group second**, normalized onto 2020 geography with
   the t10t20 relationship file from the `reference/crosswalks`
   collection.

**Measure before you normalize.** Report what share of 2010 tracts map
1:1 to a 2020 tract, what share aggregate many-to-one, and what share
split. Aggregation is legitimate and the existing quadrature MOE rule
applies to it. A split requires apportioning, which is a modelled
assumption and not a sampling estimate.

Carry a `geo_change` column on every row stating which case it is. Where
a split occurred, write NULL for the estimate rather than an apportioned
number, unless the user has approved apportioning. Never publish a
modelled value that looks like a measurement.

## Rules

- Every row records its period in a `period` column, for example
  `2015-2019`. The STAC temporal extent must cover both periods.
- Styles map CHANGE, not level. At least one diverging style, with
  measured breaks and a defensible midpoint at zero.
- Document in each description that the two periods do not overlap and
  are therefore comparable, and cite the Census guidance saying so.

## Report

The re-pinning diff (which Spec lines moved between 2019 and 2024), the
API validation match rate by indicator and level, the t10t20 1:1 /
many-to-1 / split shares, rows and columns per trends collection, and
the gate result.
