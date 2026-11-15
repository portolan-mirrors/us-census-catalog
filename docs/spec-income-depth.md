# Batch 2 spec: depth for the income theme

The catalog was built for fine-grained income analysis, but the income
theme carries only medians and poverty rates. It has no distribution and
no poverty by age. This batch adds them.

## Indicators to add

Add these to `INCOME_SPEC` in `tools/specs.py`. The existing Spec tuple
and shell-pinning machinery covers all of them.

| indicator | table | note |
|---|---|---|
| household income bands | B19001 | collapse the 16 published brackets into 7 shares: under 25k, 25-50k, 50-75k, 75-100k, 100-150k, 150-200k, 200k plus |
| `gini_index` | B19083 | single value, income inequality |
| `median_earnings` | B20002 | earnings, which is not the same as household income |
| `pct_below_poverty_under_18` | B17001 | child poverty |
| `pct_below_poverty_65_plus` | B17001 | senior poverty |

## Verify availability BEFORE you build

The Census Bureau does not publish every table at every summary level.
Block groups carry a restricted set. B19083 and B17001 may be absent
there.

Measure it. Check each table against the downloaded `.dat` files for each
summary level the catalog uses. Report which indicator is unavailable at
which level. Omit an unavailable column at that level rather than writing
a column of NULLs, and record the omission in the collection's
`known_issues`. Never invent a value.

## Build order

The themed children are pruned from the wide tables, so order matters.

1. `tools/download_sources.sh` for any table not yet staged.
2. `python3 tools/build_acs.py` — rebuilds bg-income, tract-income and
   the five wide tables, which carry `ALL_SPEC`.
3. `python3 tools/build_wide_themes.py --all` — re-prunes the 25 themed
   children from the rebuilt wide tables.
4. Tiles for the 12 affected collections: bg-income, tract-income,
   county-income, state-income, zcta-income, place-income, cd-income and
   the five wide tables.
5. Styles. Add at least one new style that uses the new columns. The
   Gini index and the child poverty rate are both good choices. Measure
   every class break. No class may be empty.
6. The rest of the regeneration chain in `docs/runbook.md`.

## Rules

- Pin every new table line against the table shells, as the existing
  specs do. A wrong line number silently produces a wrong number.
- Apply the Census margin-of-error formulas already in the codebase.
  Derived shares use the proportion formula. Do not invent a margin.
- Column descriptions go in `tools/column_docs.py`. Every new column
  needs one. `make_stac.py` fails the build if a column has no
  description, which is the intended behavior.
- Cross-check at least three new values against data.census.gov and
  record the check in the build notes.
- Do not hand-write long guides. Extend the generators.

## Boundaries

- Do not touch catalog/blocks or the connectivity, housing, people or
  wellbeing themes.
- Do not publish or upload. Do not render thumbnails. Report when the
  gates pass and stop.

## Report

Row and column counts per rebuilt collection, the availability matrix
(indicator by summary level), the three data.census.gov cross-checks with
their values, and the test-gate result.
