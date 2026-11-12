# ACS build notes

How the fourteen ACS collections in this catalog are derived, line by line,
and what the build measured when it ran. Every number below came out of the
build or out of a query against its output; nothing here is estimated.

Build date: 2026-11-12, both the first eleven collections and the three
wave-3 ones (ZCTAs, places, congressional districts), whose own section is
at the end of this file. Source release: **ACS 2020–2024
5-year estimates** (`acsdt5y2024`, table-based Summary File). Boundaries:
**2024 cartographic boundary files** (GENZ2024, 500k), which match the ACS
vintage — with one documented exception, the ZCTA file, which only exists
as GENZ2020.

Code: [`tools/specs.py`](../tools/specs.py) (column specs, shell pinning)
and [`tools/build_acs.py`](../tools/build_acs.py) (the three build stages
and the validation pass).

## Collections

| collection | file | rows | size |
|---|---|---|---|
| bg-income | `catalog/block-groups/bg-income/bg-income.parquet` | 242,298 | 93.5 MB |
| bg-people | `catalog/block-groups/bg-people/bg-people.parquet` | 242,298 | 94.3 MB |
| bg-housing | `catalog/block-groups/bg-housing/bg-housing.parquet` | 242,298 | 96.2 MB |
| bg-connectivity | `catalog/block-groups/bg-connectivity/bg-connectivity.parquet` | 242,298 | 93.8 MB |
| tract-income | `catalog/tracts/tract-income/tract-income.parquet` | 85,184 | 55.6 MB |
| tract-people | `catalog/tracts/tract-people/tract-people.parquet` | 85,184 | 55.8 MB |
| tract-housing | `catalog/tracts/tract-housing/tract-housing.parquet` | 85,184 | 56.7 MB |
| tract-connectivity | `catalog/tracts/tract-connectivity/tract-connectivity.parquet` | 85,184 | 55.9 MB |
| tract-wellbeing | `catalog/tracts/tract-wellbeing/tract-wellbeing.parquet` | 85,184 | 55.9 MB |
| counties | `catalog/counties/counties.parquet` | 3,235 | 13.6 MB |
| states | `catalog/states/states.parquet` | 56 | 4.1 MB |
| zctas | `catalog/zctas/zctas.parquet` | 33,791 | 75.2 MB |
| places | `catalog/places/places.parquet` | 32,612 | 34.5 MB |
| congressional-districts | `catalog/congressional-districts/congressional-districts.parquet` | 441 | 9.0 MB |

Why themed chunks rather than one wide table per level: the St. Louis
catalog this build is ported from publishes one 60-column block-group
table, which is fine for 314 rows. Nationally that is a 60-column,
242,298-row download for a consumer who wanted median income. Block groups
and tracts are therefore split into themed collections, and the coarse or
non-nesting levels — 3,235 counties, 56 states, 33,791 ZCTAs, 32,612 places
and 441 congressional districts — carry every column in one wide table,
because at that size width costs nothing and nobody wants a themed chunk of
ZIP code areas.

## Source files

Already staged under `staging/census-cache/` by `tools/download_sources.sh`
(the build never downloads):

- `acsdt5y2024-<table>.dat` — 31 tables, pipe-delimited, one row per
  geography, `GEO_ID` plus `<table>_E###` (estimate) and `<table>_M###`
  (margin of error) per line. Largest is `acsdt5y2024-b01001.dat` at
  200 MB.
- `ACS20245YR_Table_Shells.txt` — `Table ID|Line|Indent|Unique ID|Label|…`,
  the file the line-number pins are checked against.
- `cb_2024_us_{bg,tract,county,state,place,cd119}_500k.zip` and
  `cb_2020_us_zcta520_500k.zip` — national cartographic boundary
  shapefiles, NAD83. The ZCTA one is GENZ2020 because that is the only
  cartographic ZCTA edition published; see Wave 3 below.

Tables read: B01001 B01002 B01003 B03002 B05002 B08301 B08303 B15003 B18101
B19013 B19013B B19013D B19013H B19013I B19301 B22010 B23025 B25002 B25003
B25024 B25034 B25044 B25064 B25070 B25077 B26001 B27001 B28001 B28002
B17020B C17002 (31 tables). B17020B (line 2 over line 1, with CV) feeds
`pct_below_poverty_black`, added to tract-wellbeing, counties, and states
after the first build (orchestrator edit to `specs.py`, full rebuild
re-validated 2026-11-12 22:28; tract-wellbeing has 34 columns,
counties/states 112). Measured NULL rates for it: 12.84% tract /
5.87% county / 7.14% state.

Cartographic boundary files, not TIGER/Line: TIGER extends block groups
into open water, the CB files clip to the shoreline, which is what a
choropleth wants.

## Commands

```sh
python3 tools/build_acs.py --stage extract     # ~83 s, 31 tables
python3 tools/build_acs.py --stage geometry    # ~37 s, 7 shapefiles
python3 tools/build_acs.py --stage assemble    # ~86 s, 14 collections
python3 tools/build_acs.py --validate          # the checks below
```

`python3 tools/build_acs.py` runs all three stages; a trailing list of
collection ids restricts assembly (and restricts extraction to the tables
those collections need, and extraction and geometry to their summary
levels). `--level` restricts the levels explicitly — how the wave-3
collections were extracted without rewriting the four levels' CSVs:

```sh
python3 tools/build_acs.py zctas places congressional-districts   # 29 s all-in
```

### Stage 1 — extract

One pass per `.dat` file, writing `staging/acs-build/<table>.<level>.csv`.

Every column reads its numerator *and* its denominator from one table, so a
table is an independent unit of work: one read emits finished columns for
all four summary levels at once. The four levels are picked off `GEO_ID` by
prefix, in that single pass — the 200 MB B01001 file is read once, not four
times, which is the main change from the St. Louis code.

| level | GEO_ID prefix | rows in the ACS release |
|---|---|---|
| block group | `1500000US` | 242,297 |
| tract | `1400000US` | 85,382 |
| county | `0500000US` | 3,222 |
| state | `0400000US` | 52 |

B27001, B18101, B05002, B26001 and B19013B/D/H/I return 0 block-group rows:
the Census does not publish them below tract level. That is why
`tract-wellbeing` has no block-group twin. Those same tables *are* published
at all three wave-3 levels, which is why those collections carry the full
column set.

Three more levels were added in wave 3 (`860Z200US` ZCTA, `1600000US`
place, `5001900US` congressional district) — their prefixes, counts and the
`--level` flag that extracts them without rewriting the four CSVs above are
in the Wave 3 section at the end of this file.

### Stage 2 — geometry

`unzip` then `ogr2ogr -f Parquet -t_srs EPSG:4326` per level into
`staging/geo/cb_2024_us_<level>_4326.parquet`, keeping only the join key,
the name parts and `ALAND`. **ogr2ogr, not DuckDB `ST_Transform`**: DuckDB
computes correct coordinates but stamps the source CRS into the GeoParquet
metadata — a known trap, hit before in the TriMet catalog.

Feature counts: bg 242,298 · tract 85,184 · county 3,235 · state 56.

### Stage 3 — assemble

DuckDB joins the per-table CSVs onto the geometry parquet. **Geometry drives
the join** (`FROM geometry LEFT JOIN attributes`), so a geography with
boundaries but no ACS data keeps its row with NULL values rather than
disappearing — see *Known issues*.

Per-table CSVs are read with explicit column types. A column that is
all-NULL in DuckDB's sample (`median_hh_income_asian` at tract level, for
instance) would otherwise be sniffed as VARCHAR.

The DuckDB output is then normalized by gpio (geoparquet.io 1.6.0) — the
same conversion the St. Louis catalog passes Portolan validation with:

```sh
gpio convert geoparquet <duckdb out> <collection>.parquet   # covering bbox, zstd
gpio sort hilbert <collection>.parquet <tmp>                # PTL-DAT-006
# then pyarrow rewrite: row_group_size=20000, write_statistics=True
```

The pyarrow rewrite is there because GDAL and gpio can drop row-group
min/max statistics on the bbox covering column (PTL-DAT-007 wants them);
the rewrite preserves the `geo` schema metadata and the Hilbert row order.

Verified on the output: GeoParquet 1.1.0, `covering.bbox` present, no `crs`
key (the spec's way of writing the OGC:CRS84 default — byte-identical in
shape to the published St. Louis file), ZSTD, 5 row groups of 20,000 for
tract-income with statistics on all four `bbox.*` columns, and row order
that starts in American Samoa rather than at GEOID `01…` (Hilbert, not
lexical).

## Column derivations

`kind` determines the arithmetic:

- **count** — sum of the numerator lines, published as an integer.
- **median** — one published line, passed through. Medians never aggregate.
- **pct** — `100 × Σnumerator / denominator`, rounded to 2 decimals.
- **complement** — `100 − <other column>`.

Every column also publishes `<name>_moe`, and the columns marked `cv`
publish `<name>_cv`.

`shell pin` is the `(table, line, label)` triple checked against
`ACS20245YR_Table_Shells.txt` at the start of every build. **43 pins
verified, 0 failures.** A vintage that renumbers a line fails the build
instead of publishing a mislabeled column.

#### Income (bg-income, tract-income)

| column | kind | table | numerator lines | denominator | cv | shell pin |
|---|---|---|---|---|---|---|
| median_hh_income | median | B19013 | 1 | — | yes | B19013 line 1 = "Median household income" |
| per_capita_income | median | B19301 | 1 | — | no | B19301 line 1 = "Per capita income" |
| pct_below_poverty | pct | C17002 | 2+3 | 1 | yes | C17002 line 2 = "Under .50" |
| pct_below_2x_poverty | pct | C17002 | 2+3+4+5+6+7 | 1 | no | C17002 line 8 = "2.00 and over" |
| pct_snap | pct | B22010 | 2 | 1 | no | B22010 line 2 = "Household received Food Stamps/SNAP" |
| pct_unemployed | pct | B23025 | 5 | 3 | no | B23025 line 5 = "Unemployed" |

`pct_unemployed` divides by line 3 (civilian labor force), not line 1
(population 16+): the unemployment rate's denominator is the labor force.

#### People (bg-people, tract-people)

| column | kind | table | numerator lines | denominator | cv | shell pin |
|---|---|---|---|---|---|---|
| median_age | median | B01002 | 1 | — | no | B01002 line 1 = "Total" |
| pct_under_18 | pct | B01001 | UNDER18 | 1 | no | B01001 line 1 = "Total" |
| pct_65_plus | pct | B01001 | OVER65 | 1 | no | B01001 line 1 = "Total" |
| pct_white_nh | pct | B03002 | 3 | 1 | no | B03002 line 3 = "White alone" |
| pct_black | pct | B03002 | 4 | 1 | no | B03002 line 4 = "Black or African American alone" |
| pct_native | pct | B03002 | 5 | 1 | no | B03002 line 5 = "American Indian" |
| pct_asian | pct | B03002 | 6 | 1 | no | B03002 line 6 = "Asian alone" |
| pct_hispanic | pct | B03002 | 12 | 1 | no | B03002 line 12 = "Hispanic or Latino" |
| pct_people_of_color | complement | — | 100 − pct_white_nh | — | no | (inherits pct_white_nh) |
| pct_bachelors_plus | pct | B15003 | 22+23+24+25 | 1 | no | B15003 line 22 = "Bachelor's degree" |

B03002 lines 3–6 are the *not Hispanic or Latino* branch, so `pct_black`,
`pct_native` and `pct_asian` are single-race non-Hispanic shares and the
five race shares plus `pct_hispanic` are mutually exclusive.
`pct_people_of_color` carries `pct_white_nh`'s own margin of error: a
complement has the same sampling error as the share it is taken from.

#### Housing (bg-housing, tract-housing)

| column | kind | table | numerator lines | denominator | cv | shell pin |
|---|---|---|---|---|---|---|
| housing_units | count | B25002 | 1 | — | no | B25002 line 1 = "Total" |
| pct_vacant_units | pct | B25002 | 3 | 1 | no | B25002 line 3 = "Vacant" |
| households | count | B25003 | 1 | — | no | B25003 line 1 = "Total" |
| pct_owner_occupied | pct | B25003 | 2 | 1 | no | B25003 line 2 = "Owner occupied" |
| median_gross_rent | median | B25064 | 1 | — | yes | B25064 line 1 = "Median gross rent" |
| pct_rent_burdened | pct | B25070 | 7+8+9+10 | 1 − 11 | yes | B25070 line 7 = "30.0 to 34.9 percent" |
| pct_severely_rent_burdened | pct | B25070 | 10 | 1 − 11 | no | B25070 line 10 = "50.0 percent or more" |
| median_home_value | median | B25077 | 1 | — | yes | B25077 line 1 = "Median value" |
| pct_built_pre_1940 | pct | B25034 | 11 | 1 | no | B25034 line 11 = "Built 1939 or earlier" |
| pct_single_family | pct | B25024 | 2+3 | 1 | no | B25024 line 2 = "1, detached" |

The rent-burden denominator subtracts B25070 line 11, "Not computed" —
renter households whose rent-to-income ratio the Census could not compute
(no cash rent, or no income). Including them would understate the burden.

#### Connectivity (bg-connectivity, tract-connectivity)

| column | kind | table | numerator lines | denominator | cv | shell pin |
|---|---|---|---|---|---|---|
| hh_no_vehicle | count | B25044 | 3+10 | — | no | B25044 line 3 = "No vehicle available" |
| pct_hh_no_vehicle | pct | B25044 | 3+10 | 1 | yes | B25044 line 10 = "No vehicle available" |
| pct_commute_drive_alone | pct | B08301 | 3 | 1 | no | B08301 line 3 = "Drove alone" |
| pct_commute_transit | pct | B08301 | 10 | 1 | yes | B08301 line 10 = "Public transportation" |
| pct_commute_walk_bike | pct | B08301 | 18+19 | 1 | no | B08301 line 19 = "Walked" |
| pct_work_from_home | pct | B08301 | 21 | 1 | no | B08301 line 21 = "Worked from home" |
| pct_commute_45min_plus | pct | B08303 | 11+12+13 | 1 | no | B08303 line 11 = "45 to 59 minutes" |
| pct_no_internet | pct | B28002 | 13 | 1 | yes | B28002 line 13 = "No Internet access" |
| pct_no_computer | pct | B28001 | 11 | 1 | no | B28001 line 11 = "No Computer" |

B25044 lines 3 and 10 are owner-occupied and renter-occupied households
with no vehicle; summing them is what makes `hh_no_vehicle` a tenure-blind
count, and the two margins of error add in quadrature.

#### Wellbeing (tract-wellbeing)

| column | kind | table | numerator lines | denominator | cv | shell pin |
|---|---|---|---|---|---|---|
| pct_uninsured | pct | B27001 | NOINS | 1 | yes | B27001 line 1 = "Total" |
| pct_with_disability | pct | B18101 | DISAB | 1 | yes | B18101 line 1 = "Total" |
| pct_foreign_born | pct | B05002 | 13 | 1 | no | B05002 line 13 = "Foreign-born" |
| group_quarters_pop | count | B26001 | 1 | — | no | B26001 line 1 = "Total" |
| median_hh_income_black | median | B19013B | 1 | — | yes | B19013B line 1 = "Median household income" |
| median_hh_income_white_nh | median | B19013H | 1 | — | yes | B19013H line 1 = "Median household income" |
| median_hh_income_asian | median | B19013D | 1 | — | yes | B19013D line 1 = "Median household income" |
| median_hh_income_hispanic | median | B19013I | 1 | — | yes | B19013I line 1 = "Median household income" |

The B19013 race iterations are B = Black or African American alone, D =
Asian alone, H = White alone not Hispanic or Latino, I = Hispanic or Latino
householder.

#### Context (every collection)

| column | kind | table | numerator lines | denominator | cv | shell pin |
|---|---|---|---|---|---|---|
| population | count | B01003 | 1 | — | no | B01003 line 1 = "Total" |

Plus, on every collection:

- `geoid` — string, no summary-level prefix (the 12-, 11-, 5- or 2-digit
  GEOID), matching the cartographic boundary files' `GEOID`.
- `state` — 2-letter USPS code, from the `STATEFP → USPS` lookup embedded in
  `tools/specs.py`. Embedded rather than read off the boundary files
  because the 2024 block-group shapefile carries no `STUSPS` column (the
  tract, county and state files do) and every collection should publish the
  same code.
- `name` — built from boundary attributes with `concat_ws(', ', …)`, which
  drops a missing part instead of leaving a dangling comma:
  - state → `NAME` ("Missouri")
  - county → `NAMELSAD, STATE_NAME` ("St. Louis city, Missouri")
  - tract → `NAMELSAD, NAMELSADCO, STATE_NAME` ("Census Tract 34.06, San
    Joaquin County, California")
  - block group → `NAMELSAD` + the tract's `NAMELSAD` (joined on the first
    11 characters of the GEOID) + the county's `NAMELSAD` and `STATE_NAME`
    (joined on the first 5): "Block Group 4, Census Tract 1022, St. Louis
    city, Missouri". The block-group file carries only "Block Group 4", so
    the tract and county files supply the rest.
- `aland_sqkm` — `ALAND / 1e6`, 3 decimals.
- `pop_density` — `population / aland_sqkm`, 1 decimal; NULL when `ALAND`
  is 0 (202 block groups are entirely water) or population is NULL. 646 of
  242,298 block groups are NULL on this column: 444 with no ACS population
  plus those 202.

### Derived line groups

Four groups are resolved *from the shells* rather than hardcoded, because
they span one line per sex and per age band. The build fails if a group's
cardinality changes. Resolved for this vintage:

| group | table | lines | resolves by |
|---|---|---|---|
| UNDER18 | B01001 | 3, 4, 5, 6, 27, 28, 29, 30 | labels "Under 5 years", "5 to 9 years", "10 to 14 years", "15 to 17 years" × 2 sexes = 8 lines |
| OVER65 | B01001 | 20–25, 44–49 | "65 and 66 years", "67 to 69", "70 to 74", "75 to 79", "80 to 84", "85 years and over" × 2 = 12 lines |
| NOINS | B27001 | 5, 8, 11, 14, 17, 20, 23, 26, 29, 33, 36, 39, 42, 45, 48, 51, 54, 57 | label "No health insurance coverage", 9 age groups × 2 sexes = 18 lines |
| DISAB | B18101 | 4, 7, 10, 13, 16, 19, 23, 26, 29, 32, 35, 38 | label "With a disability", 6 age groups × 2 sexes = 12 lines |

## Statistics

### Jam values

ACS publishes jam codes in place of unestimable values. Any estimate or MOE
**at or below −111111111** becomes NULL, never a number. That single
threshold also catches the MOE jam −555555555 ("controlled, no sampling
error"), which would otherwise publish as a nonsense negative margin.

### Margins of error

All MOEs are at the 90% confidence level, as published. Formulas are the
Census's own, from *ACS Accuracy of the Data*:

**Sums** add in quadrature. For a count or a numerator over lines *i*:

```
MOE(Σxᵢ) = √( Σ MOE(xᵢ)² )
```

Jammed components are NULL and drop out of the sum; a sum of entirely
jammed lines is NULL, not 0.

**Proportions** use the subset (proportion) formula, with the ratio formula
as the fallback when the radicand goes negative — which happens when the
numerator is not a true subset of the denominator, or when sampling error
makes it look that way:

```
p = num / den
MOE(p) = √( MOE(num)² − p²·MOE(den)² ) / den        (proportion)
MOE(p) = √( MOE(num)² + p²·MOE(den)² ) / den        (ratio, if radicand < 0)
```

Published `*_moe` for a percentage is `100 ×` that, rounded to 2 decimals.
If either input MOE is NULL, or the denominator is 0, the MOE is NULL
rather than guessed.

**Medians** are published with the Census's own MOE for that line. A median
is never summed or averaged across lines or geographies.

**Complements** (`pct_people_of_color`) carry the source share's MOE
unchanged.

A percentage whose denominator is ≤ 0 after the "Not computed" subtraction
is NULL, as is a percentage whose numerator is entirely jammed.

### Coefficients of variation

Columns marked `cv` publish `<name>_cv`:

```
cv = (moe / 1.645) / estimate
```

rounded to 3 decimals; NULL when the estimate is NULL or 0, or the MOE is
NULL. The convention lets a consumer grey out unreliable geographies —
cv > 0.3 is usually the cutoff. Applied to the headline medians and the
rates where block-group sampling error is largest.

## Validation results

All from `python3 tools/build_acs.py --validate`, which ends in
`all checks passed`.

### Row counts and uniqueness

Every collection: `count(*) == count(DISTINCT geoid)`, and no `pct_*` value
outside 0–100.

| level | rows | expected |
|---|---|---|
| block groups | 242,298 | ~242,000 ✓ |
| tracts | 85,184 | ~85,000 ✓ |
| counties | 3,235 | 3,144 for the 50 states + DC, + 78 Puerto Rico municipios, + 13 territory county-equivalents ✓ |
| states | 56 | 50 + DC + PR + 4 island areas; **52 carry ACS data** ✓ |

Counted directly: `counties.parquet` has exactly 3,144 rows outside PR and
the island areas, and `states.parquet` has 52 rows with non-NULL ACS values.

### Cross-check against the published St. Louis catalog

The St. Louis catalog publishes the same ACS vintage through the same
formulas, so it is an end-to-end check on the whole statistics pipeline —
parser, jam handling, line pins, MOE arithmetic, rounding.

```sql
WITH mine AS (
  SELECT geoid, median_hh_income, median_hh_income_moe,
         pct_below_poverty, pct_below_poverty_moe
  FROM 'catalog/block-groups/bg-income/bg-income.parquet'
  WHERE substr(geoid, 1, 5) = '29510'
), theirs AS (
  SELECT geoid, median_hh_income, median_hh_income_moe,
         pct_below_poverty, pct_below_poverty_moe
  FROM 'https://data.source.coop/tge-labs/st-louis-open-data-mirror/demographics/acs-block-groups/acs-block-groups.parquet'
)
SELECT count(*) FILTER (WHERE m.median_hh_income IS DISTINCT FROM t.median_hh_income), …
FROM mine m JOIN theirs t USING (geoid);
```

**314 block groups here, 314 published, 314 joined, 0 mismatches** on
`median_hh_income`, `median_hh_income_moe`, `pct_below_poverty` and
`pct_below_poverty_moe`. Exact equality, not approximate.

### Sanity checks

- `median_hh_income` across the 50 states + DC: **56,447 (MS) – 109,870
  (DC)**, 0 NULL — inside the 55k–120k band. Puerto Rico is a state
  equivalent in the ACS but at 26,297 sits well below the band, so it is
  reported separately rather than widening the band to meaninglessness.
- Population summed over the 50 states + DC: **334,922,499**.
- Spot checks against published ACS 2020–2024 figures: California median
  household income 99,122 and median home value 734,700; New York 21.6%
  commuting by transit; San Francisco County 11.15% below poverty; St.
  Louis city 56,160 median household income and 20.64% below poverty.
- Highest block-group `pop_density`: 216,805/km², a 1.1-hectare Lower East
  Side block group with 2,348 residents. Real, not an artifact.
- `state` and `name` are non-NULL on every row of every collection.

### NULL rates

Block-group medians have genuinely high NULL rates: the Census suppresses
(jams) a median when the sample is too thin, which at block-group level is
often. These are reported, not patched.

| column | bg | tract | county | state |
|---|---|---|---|---|
| population | 0.18% | 0.16% | 0.40% | 7.14% |
| pop_density | 0.27% | 0.19% | 0.40% | 7.14% |
| median_hh_income | **7.69%** | 1.59% | 0.43% | 7.14% |
| per_capita_income | 0.99% | 0.84% | 0.40% | 7.14% |
| pct_below_poverty | 1.08% | 0.99% | 0.40% | 7.14% |
| median_age | 0.95% | 0.82% | 0.40% | 7.14% |
| pct_white_nh / black / native / asian / hispanic / people_of_color | 0.88% | 0.77% | 0.40% | 7.14% |
| pct_bachelors_plus | 0.91% | 0.79% | 0.40% | 7.14% |
| housing_units / households / hh_no_vehicle | 0.18% | 0.16% | 0.40% | 7.14% |
| median_gross_rent | **29.68%** | 5.92% | 0.62% | 7.14% |
| median_home_value | **10.03%** | 3.55% | 0.56% | 7.14% |
| pct_rent_burdened | 7.91% | 1.51% | 0.40% | 7.14% |
| pct_no_internet / pct_no_computer | 1.13% | 1.06% | 0.40% | 7.14% |
| pct_uninsured / pct_with_disability | — | 0.94% | 0.40% | 7.14% |
| group_quarters_pop | — | 0.16% | 0.40% | 7.14% |
| median_hh_income_black | — | **61.43%** | 39.47% | 7.14% |
| median_hh_income_white_nh | — | 10.04% | 2.38% | 7.14% |
| median_hh_income_asian | — | **71.27%** | 53.63% | 7.14% |
| median_hh_income_hispanic | — | **44.43%** | 19.60% | 7.14% |

Reading these:

- The 7.14% floor on `states` is 4 of 56 rows: the four island areas with
  boundaries but no ACS data.
- The 0.40% floor on `counties` is 13 of 3,235 rows, the same island-area
  county-equivalents (AS 5, GU 1, MP 4, VI 3).
- `median_gross_rent` is NULL for nearly a third of block groups because a
  block group with few renter households has no publishable rent median.
- The race-specific medians are NULL wherever that group has too few
  households in the tract — `median_hh_income_asian` for 71% of tracts.
  That is the published data, and a map of it is a map of where the group
  lives as much as of its income.
- `--validate` prints the full per-collection table; the above is a
  transposed digest of it.

### Format

`portolan info` on the outputs:

```
→ Format: GeoParquet
→ CRS: Unknown
→ Bbox: [-179.146711, -14.548699, 179.77847011250077, 71.387815]
→ Features: 85,184
```

"CRS: Unknown" is expected and correct: gpio normalizes the GeoParquet
default CRS to an *omitted* `crs` key, which the spec defines as OGC:CRS84.
The published St. Louis file — which passes Portolan validation — has the
identically shaped `geo` block:

```json
{"version": "1.1.0", "primary_column": "geometry", "columns": {"geometry":
 {"encoding": "WKB", "bbox": [...], "geometry_types": ["MultiPolygon", "Polygon"],
  "covering": {"bbox": {"xmin": ["bbox", "xmin"], ...}}}}}
```

A DuckDB read confirms a `GEOMETRY` column plus the `bbox` covering struct,
and `pyarrow` confirms ZSTD and row-group statistics on all four `bbox.*`
columns.

## Known issues

**Island areas carry geometry but no ACS data.** American Samoa, Guam, the
Northern Mariana Islands and the US Virgin Islands have 2024 cartographic
boundaries but no ACS 5-year estimates (the Island Areas run a separate
decennial-only program). Because geometry drives the join, their rows are
published with NULL values rather than dropped: 4 states, 13 county
equivalents, 405 block groups, 126 tracts. Keeping them means a national
map has no holes and a consumer can see the absence; dropping them would
make "every US state" quietly mean 52.

**Suffolk County, New York (36103) was re-delineated in the 2024 vintage.**
39 block groups and 14 tracts exist in the 2024 cartographic boundary files
with no matching row in the 2020-based ACS tabulation. They publish with
NULL ACS values, same as the island areas. These are the only non-territory
rows in the catalog with geometry but no data.

**Water block groups and tracts have no cartographic geometry.** 443 ACS
block groups and 338 ACS tracts (the `9900xx`-style water geographies) have
no polygon in the CB files and so no row here. All of them have population
0, and total dropped population is **0**. This is why the tract collections
hold 85,184 rows against 85,382 in the ACS release.

**Block-group coverage of `per_capita_income` is incomplete upstream.**
B19301 has 242,069 block-group rows against 242,297 for B01003; the missing
228 come through as NULL.

**Rounding.** Percentages and their MOEs are rounded to 2 decimals, CVs to
3, `aland_sqkm` to 3, `pop_density` to 1. Estimates and MOEs for counts and
medians are published unrounded, as the Census publishes them. One block
group (360610086012, population 0) has an `ALAND` of 118 m², so its
`aland_sqkm` rounds to 0.0 while `pop_density` is a computed 0.0 rather
than NULL — `pop_density` keys off raw `ALAND = 0`, not the rounded column.

**`staging/` is never published and never committed.** The extract CSVs
(273 MB) and geometry parquets (566 MB) are intermediate; re-running a
stage regenerates them. `staging/geo/*.parquet` is cached — delete it to
force a re-conversion from the shapefiles.

---

# Wave 3 — ZCTAs, places and congressional districts

Added 2026-11-12, after the eleven collections above. Three more
collections, each **one wide table with the full `ALL_SPEC` column set** —
the same 112 columns as `counties` and `states`:

| collection | level key | rows | parquet | pmtiles |
|---|---|---|---|---|
| zctas | `zcta` | 33,791 | 75.2 MB | 477.6 MB |
| places | `place` | 32,612 | 34.5 MB | 206.2 MB |
| congressional-districts | `cd` | 441 | 9.0 MB | 23.3 MB |

Nothing in the machinery was reinvented: `tools/specs.py` gained three
`LEVELS` prefixes and three `Collection`s, `tools/build_acs.py` gained the
new boundary files and a `--level` filter so the extract stage could run for
the new levels only, and `tools/make_tiles.py`, `tools/make_styles.py`,
`tools/column_docs.py` and `tools/collection_meta.py` each gained three
entries.

## Summary-level prefixes, verified empirically

The prefixes were read **off the cached `.dat` files**, not from a
summary-level table. Counting every distinct `GEO_ID` prefix in
`staging/census-cache/acsdt5y2024-b19013.dat` (the cached files hold *every*
summary level the release publishes — 118 of them in that one file) gives,
for the levels this catalog publishes:

| level | GEO_ID prefix | rows in the ACS release | example GEO_ID |
|---|---|---|---|
| block group | `1500000US` | 242,297 | `1500000US010010201001` |
| tract | `1400000US` | 85,382 | `1400000US01001020100` |
| county | `0500000US` | 3,222 | `0500000US01001` |
| state | `0400000US` | 52 | `0400000US01` |
| **ZCTA5** | **`860Z200US`** | **33,772** | `860Z200US00601` |
| **place** | **`1600000US`** | **32,330** | `1600000US0100100` |
| **congressional district** | **`5001900US`** | **440** | `5001900US0101` |

Two of the three wave-3 prefixes carry a component that is *not*
zero-padding, which is exactly why they were measured rather than recalled:

- `860Z200US` — summary level 860 (5-digit ZCTA) with **`Z2`** for the
  2020-based ZCTA vintage. A guessed `8600000US` matches nothing.
- `5001900US` — summary level 500 (congressional district) with **`19`**
  for the **119th Congress**.

All three prefixes are present with identical counts in all 31 cached
`.dat` files, with one upstream gap: `acsdt5y2024-b19301.dat`
(`per_capita_income`) publishes 33,303 ZCTAs and 31,741 places rather than
33,772 and 32,330, so that column is NULL on the difference.

Reproduce:

```sh
python3 - <<'PY'
import collections
c = collections.Counter(); ex = {}
with open('staging/census-cache/acsdt5y2024-b19013.dat') as f:
    f.readline()
    for line in f:
        g = line.split('|', 1)[0]
        p = g.split('US', 1)[0] + 'US'
        c[p] += 1; ex.setdefault(p, g)
for p, n in sorted(c.items(), key=lambda kv: -kv[1])[:12]:
    print(f'{p:12s} {n:>8d}  {ex[p]}')
PY
```

## Which Congress the ACS 2024 5-year release tabulates: the 119th

Three independent confirmations, all from the Census Bureau:

1. The release's own `GEO_ID` prefix is `5001900US` (above) — the `19` is
   the congress number.
2. The cartographic boundary file for the vintage is
   `cb_2024_us_cd119_500k.zip`, and `CDSESSN = '119'` on all 441 features
   (`ogrinfo`).
3. [ACS geography boundaries by year — 2024](https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year/2024.html)
   lists "Congressional District, Delegate District DC, Resident
   Commissioner District PR" with a vintage of "119th Congress of the
   United States", and 5-digit ZCTA with a vintage of "2020 Census".

The Bureau's [119th Congress district page](https://www.census.gov/programs-surveys/decennial-census/about/rdo/congressional-districts.119th_Congress.html)
is linked from the collection as a `metadata` asset. **District numbers are
not stable between congresses**, so these GEOIDs are not a time series with
any earlier release's districts.

## Stage 2 — geometry: the new boundary files

| level | file | features | source |
|---|---|---|---|
| zcta | `cb_2020_us_zcta520_500k.zip` | 33,791 | `GENZ2020/shp/` |
| place | `cb_2024_us_place_500k.zip` | 32,612 | `GENZ2024/shp/` |
| cd | `cb_2024_us_cd119_500k.zip` | 441 | `GENZ2024/shp/` |

Availability was checked against the directory listings, not assumed:

- **There is no `cb_2024_us_zcta520_500k.zip`.** `GENZ2021` through
  `GENZ2024` carry no ZCTA file at all; `GENZ2020` is the only cartographic
  ZCTA edition, and the 2020-based ZCTAs are both the current ones and the
  ones the ACS tabulates (see the boundary-vintage page above). This is the
  one place in the catalog where the boundary vintage and the estimate
  vintage differ, and it is the Bureau's own alignment.
- **A national place file does exist** (`cb_2024_us_place_500k.zip`), so no
  per-state loop was needed — the per-state `cb_2024_<ss>_place_500k.zip`
  files exist too but are redundant.

The ZCTA file is the only boundary file in the catalog whose fields are
suffixed with its vintage (`GEOID20`, `ZCTA5CE20`, `NAME20`, `LSAD20`,
`ALAND20`, `AWATER20`), so it is read through an `ogr2ogr -sql` rename
(`GEOID20 AS GEOID`, `ZCTA5CE20 AS NAMELSAD`, `ALAND20 AS ALAND`) and
nothing downstream learns the difference. Output names follow the zip:
`staging/geo/cb_2020_us_zcta520_4326.parquet`,
`cb_2024_us_place_4326.parquet`, `cb_2024_us_cd119_4326.parquet`.

## Context columns at the new levels

**ZCTAs have no state and no parent.** A ZCTA approximates a USPS ZIP
delivery area, which can cross state lines; the ACS publishes ZCTAs at the
nation level only; and the 2020 CB ZCTA file carries **no state attribute**
(checked with `ogrinfo` — the field list is above). So:

- `state` is `CAST(NULL AS VARCHAR)` on every row. The catalog's usual
  `substr(GEOID, 1, 2) → USPS` join would be actively wrong here: the first
  two digits of a ZIP code are a postal region, so `06010` would come out
  as California.
- `name` is `'ZCTA5 ' || ZCTA5CE20` — "ZCTA5 90210" — the label the Census
  Bureau itself uses, since there is no containing geography to name a ZCTA
  by.
- There is no prefix join from a ZCTA to anything. Relating ZCTAs to states
  or counties is a spatial operation or a Census relationship file.

Places and congressional districts both nest in states, so both keep the
standard `substr(GEOID, 1, 2) → USPS` join. `name` is
`NAMELSAD, STATE_NAME` for places ("Los Angeles city, California",
"Brentwood CDP, New York") and `NAMELSAD` plus the state file's `NAME` for
districts ("Congressional District 12, California") — the cd119 file carries
no state name, so the state boundary parquet is joined in for it.

## Validation results

```sh
python3 tools/build_acs.py zctas places congressional-districts --validate
```

### Row counts against published Census tallies

Checked against the Census Bureau's own
[2020 national geographic entity tallies](https://www.census.gov/geographies/reference-files/time-series/geo/tallies.html)
([`Natl_Geographic_Tallies_2020.txt`](https://www2.census.gov/geo/docs/maps-data/data/geo_tallies2020/Natl_Geographic_Tallies_2020.txt),
downloaded 2026-11-12):

| entity | tallies file | here | note |
|---|---|---|---|
| ZIP Code Tabulation Areas | 33,642 US + 132 PR + 17 island = **33,791** | **33,791** | exact |
| Incorporated places | 19,519 + 215 island = 19,734 | — | 2020 vintage |
| Census designated places | 12,098 + 292 PR + 64 island = 12,454 | — | 2020 vintage |
| places, both kinds | **32,188** (2020) | **32,612** (2024 CB file) | +424 over four vintages of incorporations, dissolutions and CDP re-delineations |
| Congressional districts | 436 US (incl. the DC delegate) + 1 PR + 4 island = **441** | **441** | exact |

### Uniqueness, ranges, orphans

```
  zctas                 33,791 rows   33,791 distinct geoid  0 out-of-range pct  [ok]
  places                32,612 rows   32,612 distinct geoid  0 out-of-range pct  [ok]
  congressional-districts  441 rows      441 distinct geoid  0 out-of-range pct  [ok]

  zctas                        0 ACS rows with no polygon     19 polygons with no ACS row
  places                       0 ACS rows with no polygon    282 polygons with no ACS row
  congressional-districts      3 ACS rows with no polygon      4 polygons with no ACS row
```

Geometry drives the join, as everywhere else in the catalog, so the rows
with a polygon and no ACS tabulation are **kept with NULL values**:

- **ZCTAs, 19 kept**: the 17 island-area ZCTAs (USVI 00802/00820/00830/
  00840/00850/00851, American Samoa 96799, Guam 96910/96913/96915/96916/
  96917/96928/96929, Northern Mariana Islands 96950/96951/96952 — which is
  exactly the tallies file's "17 island areas"), plus **11717 and 11798**,
  both in Suffolk County, New York (located by intersecting them with the
  county boundary file). Puerto Rico's 132 ZCTAs all have data. Nothing is
  dropped in the other direction: all 33,772 tabulated ZCTAs have a polygon.
- **places, 282 kept**: 279 island-area places (MP 135, AS 77, GU 57,
  VI 10), Brentwood CDP (`3608026`) and Wyandanch CDP (`3683294`) in
  Suffolk County NY — the same two communities as the two orphan ZCTAs, and
  the same county whose re-delineation leaves 14 tracts and 39 block groups
  without ACS rows — and **Louisville city, Kentucky (`2148000`)**, which
  the boundary file still carries while the ACS tabulates the consolidated
  `2148006` Louisville/Jefferson County metro government (balance). If you
  want Louisville, use `2148006`.
- **districts, 4 kept**: the island-area delegate districts `6098` (AS),
  `6698` (GU), `6998` (MP), `7898` (VI).
- **districts, 3 dropped**: `09ZZ`, `17ZZ`, `33ZZ` — water-only
  pseudo-districts in Connecticut, Illinois and New Hampshire, each with
  **population 0** in the ACS, which have no polygon in the CB file.
  Dropped population is exactly 0, the same situation as the `9900xx` water
  tracts.

### Spot checks against data.census.gov

| geography | column | value here |
|---|---|---|
| ZCTA 90210 (Beverly Hills) | `median_hh_income` | 187,801 (MOE 18,411), `median_home_value` 2,000,001 |
| ZCTA 00601 (Adjuntas, PR) | `median_hh_income` | 19,454 (MOE 1,546) |
| ZCTA 60614 (Chicago) | `median_hh_income` | 136,448, `pct_bachelors_plus` 87.21 |
| ZCTA 33109 (Fisher Island, FL) | `median_hh_income` | 250,001 — the ACS top code, not a jam value |
| place 0644000 Los Angeles city | `population` | 3,857,263, `median_home_value` 921,200 |
| place 3651000 New York city | `population` | 8,483,844, `median_hh_income` 80,483 |
| place 1150000 Washington city, DC | `population` | 681,294 — equals the DC row in `states` |
| CD 0612 (CA-12) | `median_hh_income` | 108,648 |
| CD 3612 (NY-12) | `median_hh_income` | 147,775, `pct_bachelors_plus` 80.31 |
| CD 0101 (AL-01) | `median_hh_income` | 66,291 |

District population across the 435 voting districts: **546,488 –
1,021,191** (Delaware's at-large district is the maximum, and equals
Delaware's population in `states`). Equal-population by construction, which
is why this collection's style breaks are much tighter than any other's.

Top codes are published values, not jams: `median_home_value` tops out at
$2,000,001 and `median_hh_income` at $250,001 upstream, and the richest
ZCTAs sit on those values.

### NULL rates

Congressional districts are the most complete collection in the catalog:
**every column is NULL on exactly the four island-area delegate districts
(0.91%)**, with one exception — `median_hh_income_asian` is NULL on 1.13%
(those four plus one district with no published Asian-householder median).

ZCTAs and places, notable columns only (full table from
`--validate`):

| column | zctas | places |
|---|---|---|
| `population` (and the other counts) | 0.06% | 0.86% |
| `median_hh_income` | 9.60% | 12.71% |
| `per_capita_income` | 3.26% | 4.28% |
| `median_gross_rent` | 23.79% | 31.32% |
| `median_home_value` | 10.45% | 12.78% |
| `pct_rent_burdened` | 10.96% | 14.60% |
| `median_hh_income_black` | 69.25% | 79.24% |
| `median_hh_income_white_nh` | 12.08% | 17.62% |
| `median_hh_income_asian` | 76.59% | 85.80% |
| `median_hh_income_hispanic` | 58.55% | 69.35% |
| `pct_below_poverty_black` | 36.59% | 46.72% |
| most `pct_*` columns | 1.8–3.1% | 2.2–3.8% |

For reference: `median_hh_income` is NULL on 1.59% of tracts and 7.69% of
block groups, so ZCTA coverage sits just below block-group coverage and
place coverage below that — both files are dominated by small geographies
(a single-building urban ZCTA, a village of forty people), not by the
cities and ZIP codes a reader pictures.

## Tiles

`python3 tools/make_tiles.py zctas places congressional-districts`, built
with tylertoo from `/Users/cholmes/repos/tylertoo`; logs in
`staging/tiles-logs/{zctas,places,congressional-districts}.log` carry the
exact command lines.

- **zctas, places** — `--band 0-5:a5 --band 6-12:geom`, the tract recipe,
  with the same accumulate/exclude logic (`classify()` in
  `tools/make_tiles.py`): the five count columns summed
  (`population`, `housing_units`, `households`, `hh_no_vehicle`,
  `group_quarters_pop`), every rate, median and `*_cv` averaged unweighted,
  and all 45 `*_moe` columns excluded from the tiles — an averaged margin of
  error is not a margin of error. 65 of 110 property columns kept.
- **congressional-districts** — `--band 0-10:geom
  --max-compressed-tile-size 2M`, the counties recipe: few enough features
  to carry real polygons at every zoom, and wide enough (110 columns) that
  the z0 tile needs the raised cap, exactly as counties did.

### Per-zoom maximum tile size (`tylertoo stats`)

| zoom | zctas | places | congressional-districts |
|---|---|---|---|
| 0 | 29,899 | 29,645 | 107,238 |
| 1 | 77,966 | 77,966 | 126,041 |
| 2 | 161,496 | 161,317 | 87,881 |
| 3 | 274,286 | 266,194 | 82,531 |
| 4 | 518,859 | 503,904 | 81,253 |
| 5 | **746,904** | **684,100** | 51,332 |
| 6 | 483,927 | 484,324 | 34,451 |
| 7 | 398,788 | 368,037 | 22,165 |
| 8 | 207,257 | 172,714 | 17,102 |
| 9 | 143,332 | 82,648 | 15,324 |
| 10 | 83,774 | 43,955 | 11,690 |
| 11 | 43,795 | 23,577 | — |
| 12 | 23,182 | 16,395 | — |
| total tiles | 227,025 (z0–12) | 89,679 (z0–12) | 21,323 (z0–10) |

QC finding, recorded rather than patched: the largest zctas and places
tiles sit at **z5**, the last A5 zoom, at 747 KB and 684 KB — above
tylertoo's default 500 KB compressed cap, which the size valve merges
toward but cannot reach when each A5 cell carries 65 attribute columns
(4,087 features merged for zctas, 1,952 for places). This is the same
best-effort behaviour the tract archives show at z6 (485 KB max) and is
documented in `docs/design.md`; raising the cap to 2M would stop the valve
merging cells it cannot shrink below the cap, at the cost of ~1 MB tiles.
Served tiles remain well under a megabyte either way.

### Decode spot checks

`tylertoo decode --zoom 12` (10 for districts) over each archive:

- **No `*_moe` column in any archive** (69, 70 and 70 tile columns, 0
  matching `_moe`), and the layer name equals the collection id in all
  three — which is what every generated style's `source-layer` expects.
- Full coverage at the feature zooms: 33,791 / 32,612 / 441 distinct
  `geoid`, matching the parquet exactly.
- Tile values equal parquet values at feature zooms (checked for ZCTAs
  90210/00601/60614, places 0644000/3651000, districts 0612/1198/0101 on
  `population`, `median_hh_income`, `median_home_value`,
  `pct_bachelors_plus`).
- A5 aggregation is exact: deduplicating the z4 zctas decode on `cell`
  gives 3,867 cells whose `population` sums to **338,071,860** — the same
  total as the GeoParquet's `sum(population)`.

## Styles

`python3 tools/make_styles.py --measure zctas places congressional-districts`
— four styles each, the counties tier (income default, density, poverty,
home value), measured on each collection's own national distribution and
appended to `docs/style-breaks.json` without touching the twelve
collections already in it. `--measure` and style writing now take an
optional collection filter for exactly that reason.

The breaks are measured, not copied: the three distributions differ from
counties and from each other.

| column | zctas | places | congressional-districts |
|---|---|---|---|
| `median_hh_income` (default) | 45k/60k/72k/87k/120k/160k | 40k/55k/67k/84k/115k/150k | 60k/70k/79k/91k/110k/130k |
| percentiles | 9/29/50/70/90/97 | 10/30/50/70/88/95 | 8/29/51/70/88/95 |
| `pop_density` | 5/20/60/200/600/2000 | 50/125/250/500/1000/2000 | 25/75/200/600/1500/4000 |
| percentiles | 20/43/60/72/82/94 | 15/30/47/70/87/96 | 14/38/57/72/86/95 |
| `pct_below_poverty` | 5/9/13/19/28 | 5/9/14/20/30 | 8/10/12/15/19 |
| percentiles | 19/42/61/80/92 | 23/42/61/76/90 | 12/28/51/77/92 |
| `median_home_value` | 100k/160k/225k/325k/500k/800k | 85k/130k/190k/290k/450k/750k | 185k/250k/335k/450k/650k/900k |
| percentiles | 10/30/51/70/87/95 | 11/30/50/70/85/95 | 10/33/50/71/86/96 |

Every class is non-empty nationally (the generator fails the run otherwise)
and the fullest class holds 25.4% of features at worst. Two consequences of
the measured numbers, applied by the existing logic rather than by hand:

- `median_hh_income` (9.60% / 12.71% NULL) and `median_home_value`
  (10.45% / 12.78%) get the neutral-gray "no data" underlay on zctas and
  places; nothing on districts does (0.91% NULL, under the 5% threshold).
- `pct_below_poverty` has a CV above 0.30 on **40.53%** of ZCTAs and
  **56.69%** of places — past the 35% fade ceiling — so those two styles
  say so in their description instead of fading most of the map. On
  districts no styled column has a single feature with a CV above 0.30.

## Files changed for wave 3

- `tools/specs.py` — three `LEVELS` prefixes, three `Collection`s.
- `tools/build_acs.py` — `GEO_ZIP`/`GEO_RENAME`/`GEO_FIELDS` for the new
  boundary files, `state_expr()` (NULL for ZCTAs), three `name_expr()`
  cases, the cd→state join, `--level` filtering on the extract and geometry
  stages, and an orphan report in `--validate`.
- `tools/make_tiles.py` — restructured into one filterable driver (the
  previous version re-ran every archive on import); the counties, states,
  tract-income and blocks recipes it emits are byte-identical to the
  command lines in the existing logs, and `zctas`, `places` and
  `congressional-districts` are added.
- `tools/make_styles.py` — three `SOURCES`/`UNIT` entries, twelve styles,
  an optional collection filter on `--measure` and on writing.
- `tools/column_docs.py` — `LEVEL_NOUN`, `CB_VINTAGE`, `GEOID_DOC`,
  `CONTEXT_DOC` (`name`, `state`, `aland_sqkm`, `geometry`) and the
  measured `NULL_NOTES` for the three levels.
- `tools/collection_meta.py` — titles, descriptions, keywords, source and
  documentation assets (the `.dat` tables, the three CB zips at their
  census.gov URLs, the tallies file, the ZCTA/CDP/CD119 pages), processing
  notes, known issues, and `--write` filtering. Two corrections that fall
  out of adding a geometry-only collection: the tiles paragraph and the
  tiles known-issue now say "real geographies at every zoom, no A5" for the
  collections whose archives have no `a5` band at all — which has always
  been true of `counties` (`0-10:geom`) and `states` (`0-8:geom`) as well,
  and the generated text claimed A5 coarse zooms for them; and the pin
  count in the processing notes now reads 44, which is what
  `check_all_shells()` actually returns (43 missed the `B01003`
  context pin).
- `tools/make_stac.py` — the root catalog's ungrouped children are derived
  from `ALL_COLLECTIONS` instead of a hardcoded
  `("counties", "states", "blocks")`, so the three new collections get
  `child` links.
- `tools/download_sources.sh` — the three new boundary zips, with the
  GENZ2020-only ZCTA case and the congress number commented in place.
- `catalog/{zctas,places,congressional-districts}/` — `*.parquet`,
  `*.pmtiles`, `styles/*.json`, `.portolan/metadata.yaml`, `AGENTS.md`
  (schema tables and quality notes written, `TODO-recipes` marker left for
  the recipes agent).
- `docs/style-breaks.json` — three collections appended.
- `staging/census-cache/` — `cb_2020_us_zcta520_500k.zip`,
  `cb_2024_us_place_500k.zip`, `cb_2024_us_cd119_500k.zip` downloaded
  (2026-11-12).
