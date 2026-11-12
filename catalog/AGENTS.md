# AGENTS.md — US Census Demographics Mirror

Guidance for AI agents and automated clients working with this catalog.

**One rule survives every edit to this file.** Every claim here is either quoted
from a source or measured from the data. If you cannot point at where a fact
came from, it does not belong in this file. An agent acting on an invented join
key or an invented column name produces a confident wrong answer, and nothing
downstream catches it.

## What this catalog holds

U.S. Census Bureau demographics as GeoParquet + PMTiles, rooted at
`https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json`.
ACS 2020–2024 5-year indicators at block group, tract, county, and state
level, grouped into themed collections (income, people, housing,
connectivity, wellbeing), plus 2020 Decennial counts at block level. Each
collection's own `AGENTS.md` documents its columns and carries tested
queries; this file covers what spans collections.

## Join keys

Every ACS collection has a `geoid` column (string): the full census GEOID.
Lengths by geography — state 2, county 5, tract 11, block group 12,
block 15. GEOIDs nest by prefix: a block group's county is
`substr(geoid, 1, 5)`, its tract `substr(geoid, 1, 11)`; a block's block
group is `substr(geoid, 1, 12)`. Collections at the same geography join 1:1
on `geoid`.

## Quirks that produce silently wrong answers

- ACS margins of error are published at the **90% confidence level**. To sum
  estimates across geographies, add MOEs in quadrature; never sum medians at
  all (a median of a region is not derivable from its parts).
- Jam values (e.g. `-666666666`) in Census files mean "no estimate"; they
  are already `NULL` here. A query that averages a column needs no jam
  filtering, but remember NULLs reduce the row count.
- Coarse zooms of each PMTiles archive are **A5 cell aggregations**, not
  census geographies: counts are sums, rates and medians are unweighted
  means of the underlying geographies' values. Use the GeoParquet, not
  tiles, for statistics.
- Geometries are the Census cartographic boundary files (500k, shoreline-
  clipped), in EPSG:4326 — good for mapping and point-in-polygon, not for
  legal-boundary or area-measurement work. Blocks use TIGER/Line (not
  shoreline-clipped).

## Structure

Assets and structural links resolve relative to the object that carries them.
STAC browsers and `pystac` both resolve them. The data browser at
[source.coop](https://source.coop/portolan-mirrors/us-census-catalog) renders
each collection with map previews, legends, schema, and download links.
