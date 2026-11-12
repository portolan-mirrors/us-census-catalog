# Design notes — US Census mirror

Decisions made at catalog bootstrap (2026-11-12), so contributors know what is
deliberate.

## Themed chunks, not one wide table

Each collection is one geography × one theme (income, people, housing,
connectivity, wellbeing), with its own GeoParquet and PMTiles. A chunk's
PMTiles carries ~10–20 related statistics — small enough to browse nationally,
coherent enough that its map styles all belong to the theme. Counties and
states are small (3,144 / 56 rows), so they carry all indicators in one
collection each.

## Geography levels and what exists at each

Income and the other ACS indicators exist down to **block groups** (~242k;
ACS 2020–2024 5-year). **Blocks** (~8.1M) carry 2020 Decennial Census counts
only (P.L. 94-171: population, race/ethnicity, voting age, housing occupancy,
group quarters) — the Census Bureau publishes no income below block group.
GEOIDs nest by prefix (state 2 / county 5 / tract 11 / block group 12 /
block 15), which is the join path between levels.

## Tiles: tylertoo with A5 cell aggregation at coarse zooms

Tiles are built with [tylertoo](https://github.com/geoparquet-io/tylertoo)
(built from main), not tippecanoe. Thinning 242k–8.1M polygons at national
zooms would show a biased subset (small urban geographies drop first), so
coarse zooms instead aggregate into [A5](https://a5geo.org/) cells via
`--band LO-HI:a5 --band LO-HI:geom` with `--accumulate-attribute`: counts are
cell sums, rates and medians are unweighted means of the underlying
geographies (a visualization aid, documented as such — statistics come from
the GeoParquet, not tiles). Cell and feature zooms share column names, so one
style expression classifies both.

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
