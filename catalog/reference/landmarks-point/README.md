# Landmarks — Point

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/reference/landmarks-point/collection.json)** · [🧭 Census Atlas](https://portolan-mirrors.github.io/us-census-catalog/#c=reference/landmarks-point) · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/reference/landmarks-point/landmarks-point.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/reference/landmarks-point/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

Point landmarks from [TIGER/Line 2024 `POINTLM`](https://www2.census.gov/geo/tiger/TIGER2024/POINTLM/): all **1,088,085** features, one file per state (56 state and territory files), each carrying the `state` USPS code its source file was read from.

`feature_type` decodes each row's `mtfcc` the same way landmarks-area does. Measured nationally, most of these points are cul-de-sacs and locality points — address-system landmarks, not places a person would look for on a map — followed by cemeteries, mountain peaks and summits, and airports or airfields.

The PMTiles archive is a single band at full resolution, built with [tylertoo](https://github.com/geoparquet-io/tylertoo) `tiles` (not `pyramid` — there is no coarser geography to step up to below this collection, so every zoom draws this collection's own features, thinned to fit the tile-size cap where a zoom is too dense to draw in full). Statistics come from the GeoParquet; this collection has no `*_moe` columns to exclude.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](https://source.coop/portolan-mirrors/us-census-catalog/reference/landmarks-point/AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![TIGER/Line](https://img.shields.io/badge/TIGER%2FLine-blue) ![geography](https://img.shields.io/badge/geography-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![landmarks](https://img.shields.io/badge/landmarks-blue) ![POINTLM](https://img.shields.io/badge/POINTLM-blue) ![MTFCC](https://img.shields.io/badge/MTFCC-blue) ![points of interest](https://img.shields.io/badge/points_of_interest-blue) ![cul-de-sac](https://img.shields.io/badge/cul--de--sac-blue) ![TIGER](https://img.shields.io/badge/TIGER-blue)

## Spatial Coverage

- **Bounding Box**: [-178.791666, -14.346304, -64.565687, 71.385555]

## Temporal Coverage

- **Start**: 2020-04-01T00:00:00Z
- **End**: 2024-12-31T23:59:59Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | `POINTID`, from TIGER's internal address/point ID scheme -- not a census tabulation GEOID. |
| name | string | `FULLNAME`. |
| state | string | USPS code of the state file this row was read from. |
| mtfcc | string | `MTFCC`. |
| feature_type | string | `mtfcc` decoded through the 2022 MAF/TIGER Feature Class Code list. The two largest categories nationally (measured, 1,088,085 rows total) are Cul-de-sac (668,308) and Locality Point (208,547) -- both address-system landmarks, not places. |
| geometry | binary | Landmark point, WKB-encoded. Written in the source CRS, NAD83 (EPSG:4269) -- unlike the ACS collections, this is kept rather than reprojected to WGS84/OGC:CRS84, so the GeoParquet `geo` metadata carries an explicit `crs` key. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry (a point's own coordinates, repeated), written by gpio. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./landmarks-point.pmtiles | 187.1 MB | 1220df3e75bf... |
| ./landmarks-point.parquet | 44.2 MB | 1220da3fbef9... |
| ./thumbnail.png | 78.8 KB | 122070bdfe56... |
| ./styles/default.json | 1.6 KB | 1220940e1b03... |
| https://www2.census.gov/geo/tiger/TIGER2024/POINTLM/ | - | - |
| https://www2.census.gov/geo/pdfs/reference/mtfccs2022.pdf | - | - |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./landmarks-point.pmtiles")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/geo/tiger/TIGER2024/POINTLM/](https://www2.census.gov/geo/tiger/TIGER2024/POINTLM/)

## Processing Notes

Built from 56 state `POINTLM` shapefiles (https://www2.census.gov/geo/tiger/TIGER2024/POINTLM/, 28 MB total), concatenated after each is converted independently. Downloaded 2026-11-15 over plain HTTPS, no API key. GeoParquet written with the same path as the rest of this catalog (pyarrow, ZSTD, sized row groups, bbox covering column — tools/build_wide_themes.py documents the convention, verified against catalog/counties/county-income/county-income.parquet): `gpio convert geoparquet` reads the shapefile, keeping the source CRS (NAD83, EPSG:4269 — not reprojected, unlike the ACS collections' cartographic boundaries), then `gpio sort hilbert --add-bbox` writes the Hilbert-ordered file with the bbox covering metadata.

`state` is the USPS code for the file each row was read from.

`feature_type` decodes `mtfcc` through a table copied from the 2022 MAF/TIGER Feature Class Code PDF (https://www2.census.gov/geo/pdfs/reference/mtfccs2022.pdf), the nearest published vintage to TIGER2024 — see this collection's `doc-mtfcc` source asset. A code this build met that is not in that table is left NULL rather than guessed at; none were, for this collection's data (see docs/spec-reference-layers.md's build report).


## Attribution

U.S. Census Bureau

## License

[CC0-1.0](https://www.census.gov/about/policies/open-gov/open-data.html)

## Contact

Chris Holmes <cholmes@9eo.org>

## Known Issues

Most of these points are not places. Measured nationally, the single largest `feature_type` is `Cul-de-sac` (668,308 of 1,088,085 points) followed by `Locality Point` (208,547) — both are address-system landmarks TIGER uses to resolve street addresses, not landmarks a person would look for on a map. Filter `feature_type` before treating this collection as a point-of-interest dataset.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
