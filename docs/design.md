# Design notes — US Census mirror

Decisions made at catalog bootstrap (2026-11-12), so contributors know what is
deliberate.

## Themed chunks, not one wide table

Each collection is one geography × one theme (income, people, housing,
connectivity, wellbeing), with its own GeoParquet and PMTiles. A chunk's
PMTiles carries ~10–20 related statistics — small enough to browse nationally,
coherent enough that its map styles all belong to the theme.

The five coarse-or-sparse levels — counties, states, ZCTAs, places,
congressional districts — shipped first as a single wide 112-column table
each, on the reasoning that at 3,235 / 56 / 33,791 / 32,612 / 441 rows width
costs nothing. **Revised 2026-11-15:** every one of them became a group with
the same five themed children as tracts, plus the original wide table as a
sixth child. Two reasons. The catalog now reads uniformly — the same five
theme ids under every geography, so an agent that has learned one geography
has learned them all — and a themed chunk is 23–34 columns against 112, which
is what a consumer who wants median income should have to read even when the
file is small. The wide table stays because a cross-theme profile of one row
is a real question and at this size it needs no join.

The wide table keeps its id and its data files: its `collection.json`,
`README.md` and `styles/` moved into `catalog/<group>/<id>/` beside the themed
children, while its parquet and pmtiles stayed at
`catalog/<group>/<id>.parquet`, referenced from the moved `collection.json`
with `../` hrefs. Every data URL this catalog has published keeps working;
`tools/collection_meta.py`'s `data_url()` is the one place that knows.

The themed children are **column-pruned from the wide table**
(`tools/build_wide_themes.py`), not a second pass over the ACS `.dat` files,
so every value in a chunk is identical to the wide table's — verified by an
`EXCEPT` over every column of all 25 chunks: 0 rows differing.

## Geography levels and what exists at each

Income and the other ACS indicators exist down to **block groups** (~242k;
ACS 2020–2024 5-year). **Blocks** (~8.1M) carry 2020 Decennial Census counts
only (P.L. 94-171: population, race/ethnicity, voting age, housing occupancy,
group quarters) — the Census Bureau publishes no income below block group.
GEOIDs nest by prefix (state 2 / county 5 / tract 11 / block group 12 /
block 15), which is the join path between levels.

## Tiles: tylertoo pyramid, census geography at coarse zooms

Tiles are built with [tylertoo](https://github.com/geoparquet-io/tylertoo)
(built from main), not tippecanoe. Thinning 242k–8.1M polygons at national
zooms would show a biased subset (small urban geographies drop first), so
coarse zooms step up to a **coarser census geography** instead, via
`tylertoo pyramid --band LO-HI:<parquet>:<layer> … --generalize`
(`tools/make_tiles.py` holds the exact recipes):

| archive | z0–z5 | mid | finest |
| --- | --- | --- | --- |
| `bg-income`, `-people`, `-housing`, `-connectivity` | counties | z6–z7 tracts | z8–z13 block groups |
| `tract-*` | counties | — | z6–z12 tracts |
| `zctas`, `zcta-*`, `places`, `place-*` | counties | — | z6–z12 own features |
| `blocks` | counties | z6–z9 tracts | z10–z14 blocks |
| `counties`, `county-*`, `states`, `state-*`, `congressional-districts`, `cd-*` | real polygons at every zoom | | |

A themed child carries its parent's geometry exactly, so it reuses its
level's recipe with the themed parquet and the themed layer name swapped in —
nothing about the band plan is new. The one difference: the wide `zctas` and
`places` archives point their county band at `counties.parquet` itself, which
they can because its 112 columns are exactly their own, while a themed child
bands on `staging/agg/<theme>-county.parquet`, the same pruned staging file
every `bg-*` and `tract-*` archive already uses.

For the ACS archives the county and tract bands are **the Census Bureau's own
county and tract estimates** — `staging/agg/<theme>-county.parquet` is
`counties.parquet` column-pruned to the theme's exact schema, and the `bg-*`
archives' tract band is the matching `tract-<theme>` table — not a
client-side roll-up. That makes the coarse zooms official published values
with their own meaning, identifiable by `geoid` and `name` on click. It also
means that below the finest band **you are looking at a different census
geography than the collection's own** (below z8 in a `bg-*` archive you are
looking at counties and tracts, not block groups), which each affected
collection's known-issues says plainly. ZCTAs and places do not nest in counties, so their county band is
national-zoom orientation rather than a roll-up of those units.

`blocks` is the one archive whose coarse bands are aggregated here: 2020
decennial counts are complete counts and sum exactly, so
`tools/build_tile_staging.py` sums them by GEOID prefix and recomputes the
rates from the summed counts (never averaging per-block rates). Connecticut's
2020 block GEOIDs carry the old 8-county prefixes while the 2024 boundaries
use the 9 planning regions that replaced them, so the aggregation crosswalks
on the preserved 6-digit tract number; the national total stays exact at
334,735,155.

Every band carries the same layer name (the collection id) and the same
column names, so one style expression classifies every zoom. `*_moe` columns
are excluded from every tile — a margin of error is computed for one specific
geography and cannot be carried across bands — while `*_cv` columns are kept.
Statistics come from the GeoParquet, not tiles.

This replaced an earlier design in which coarse zooms were
[A5](https://a5geo.org/) cell aggregations (`--band LO-HI:a5` with
`--accumulate-attribute`, counts summed and rates averaged unweighted): the
cells tiled cleanly but were a visualization-only artifact, and recognizable
census geographies carrying official values proved more useful than an
abstract cell grid.

## Map styles: national breaks, measured

Each collection carries 3–5 MapLibre styles in `styles/`, generated by
`tools/make_styles.py`; `styles/default.json` is the default (the role
`finalize_stac`-style tooling keys off). Every style is a `step` choropleth on
one published column — never a computed expression — because every band of the
PMTiles pyramid carries the same column names, so one expression classifies
the county, tract and feature zooms alike. Class breaks are chosen from the **national** distribution of
that column, measured over the whole GeoParquet with DuckDB and recorded in
[`docs/style-breaks.json`](style-breaks.json) (quantiles, null share, and the
exact count of features in each class). The generator fails if a styled column
is missing from the schema, if breaks are not strictly increasing, or if any
class is empty nationally — an empty legend swatch would be a lie. Breaks are
rounded to human numbers near measured quantiles, and the ends are winsorized
rather than stretched to a $2,000,001 cap.

Three things the styles do deliberately:

- **NULL is not zero.** `step` parses its input as a number, so a missing
  attribute throws at evaluate time and MapLibre falls back to the *paint
  property default* — `#000000` for `fill-color`. Every data layer is therefore
  filtered to `["has", col]`, and where more than 5% of features have no value
  (a third of 2020 blocks are unpopulated; 61% of tracts have no published
  median income for Black households) a neutral-gray "no data" layer draws
  underneath with the inverse filter.
- **The legend comes from the first fill layer whose `fill-color` is a
  `step`/`match`** (portolan-browser `extractLegend`). The no-data layer is a
  constant color, so the legend walk steps over it; noisy-estimate fading lives
  in `fill-opacity`, never in `fill-color`, which would destroy the legend.
- **Noisy estimates fade, but only while they are a minority.** Features whose
  `*_cv` exceeds 0.30 draw at 0.35 opacity instead of 0.8 — unless more than
  35% of the collection is that noisy (a block-group poverty rate has CV > 0.30
  in 84% of block groups), in which case the style says so in its description
  instead of dimming nearly every feature.

## Mirror stance

[data.census.gov](https://data.census.gov/) is authoritative. Every
collection links the exact upstream files it was built from (ACS `.dat`
tables, cartographic-boundary and TIGER zips, PL 94-171 zips) as `source`
assets, plus the relevant data.census.gov table pages. License CC0-1.0
(U.S. Government work, public domain).

## Statistical integrity

Ported from the St. Louis census pipeline: margins of error at the 90%
confidence level on every estimate, Census's own MOE propagation formulas
(quadrature for sums, proportion/ratio formulas for percentages), CV columns
on headline stats, jam values → NULL, and ACS table-shell pinning so a
vintage bump that moves a line fails loudly instead of publishing a mislabeled
column. The published St. Louis catalog (same vintage) is used as an exact
cross-check of this pipeline's output.
