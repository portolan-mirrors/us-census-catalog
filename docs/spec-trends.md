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
