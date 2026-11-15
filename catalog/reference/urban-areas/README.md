# 2020 Urban Areas

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/reference/urban-areas/collection.json)** · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/reference/urban-areas/urban-areas.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/reference/urban-areas/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

The Census Bureau's 2020 urban area delineation: all **2,644** urban areas in the United States and Puerto Rico, from [TIGER/Line 2024 `UAC20`](https://www2.census.gov/geo/tiger/TIGER2024/UAC20/) — one national file. For the 2020 Census the Bureau replaced the 2010 urbanized-area/urban-cluster split with a single urban area definition: every feature here carries the same MTFCC, `G3500` ("Urban Area"), decoded into `feature_type`. **Deviation from the original brief:** this means there is no urban/rural class column (`UATYPE20`, from the 2010 product) to style on — it does not exist in `UAC20` — so the default style classes on land area instead; see the collection's processing notes.

`aland_sqkm` and `awater_sqkm` are `ALAND20`/`AWATER20` converted from square meters. Geometry keeps the source CRS (NAD83, EPSG:4269) rather than being reprojected to WGS84.

The PMTiles archive is a single band at full resolution, built with [tylertoo](https://github.com/geoparquet-io/tylertoo) `tiles` (not `pyramid` — there is no coarser geography to step up to below this collection, so every zoom draws this collection's own features, thinned to fit the tile-size cap where a zoom is too dense to draw in full). Statistics come from the GeoParquet; this collection has no `*_moe` columns to exclude.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](https://source.coop/portolan-mirrors/us-census-catalog/reference/urban-areas/AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![TIGER/Line](https://img.shields.io/badge/TIGER%2FLine-blue) ![geography](https://img.shields.io/badge/geography-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![urban area](https://img.shields.io/badge/urban_area-blue) ![urban cluster](https://img.shields.io/badge/urban_cluster-blue) ![TIGER](https://img.shields.io/badge/TIGER-blue) ![urbanized](https://img.shields.io/badge/urbanized-blue) ![city](https://img.shields.io/badge/city-blue) ![metro](https://img.shields.io/badge/metro-blue)

## Spatial Coverage

- **Bounding Box**: [-170.78931, -14.365419, -64.585544, 64.928893]

## Temporal Coverage

- **Start**: 2020-04-01T00:00:00Z
- **End**: 2024-12-31T23:59:59Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | `UACE20`, the 5-digit urban area code. |
| name | string | `NAMELSAD20`, e.g. "Chicago, IL--IN Urban Area". |
| mtfcc | string | `MTFCC20`. Always `G3500` (measured over all 2,644 rows) -- the 2020 Census urban area product has no urban/urbanized split, unlike its 2010 predecessor. |
| feature_type | string | `mtfcc` decoded through the 2022 MAF/TIGER Feature Class Code list. Always "Urban Area". |
| aland_sqkm | double | `ALAND20 / 1e6`, land area in square kilometres. |
| awater_sqkm | double | `AWATER20 / 1e6`, water area in square kilometres. |
| geometry | binary | Urban area boundary polygon, WKB-encoded. Written in the source CRS, NAD83 (EPSG:4269) -- unlike the ACS collections, this is kept rather than reprojected to WGS84/OGC:CRS84, so the GeoParquet `geo` metadata carries an explicit `crs` key. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, written by gpio, with row-group statistics. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./urban-areas.pmtiles | 11.9 MB | 12200b483555... |
| ./urban-areas.parquet | 77.1 MB | 1220826addc0... |
| ./thumbnail.png | 29.0 KB | 1220ab0eff7b... |
| ./styles/default.json | 1.8 KB | 12200432de81... |
| https://www2.census.gov/geo/tiger/TIGER2024/UAC20/tl_2024_us_uac20.zip | - | - |
| https://www2.census.gov/geo/pdfs/reference/mtfccs2022.pdf | - | - |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./urban-areas.pmtiles")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/geo/tiger/TIGER2024/UAC20/](https://www2.census.gov/geo/tiger/TIGER2024/UAC20/)

## Processing Notes

Built from the single national `UAC20` shapefile (https://www2.census.gov/geo/tiger/TIGER2024/UAC20/tl_2024_us_uac20.zip, 70 MB). Downloaded 2026-11-15 over plain HTTPS, no API key. GeoParquet written with the same path as the rest of this catalog (pyarrow, ZSTD, sized row groups, bbox covering column — tools/build_wide_themes.py documents the convention, verified against catalog/counties/county-income/county-income.parquet): `gpio convert geoparquet` reads the shapefile, keeping the source CRS (NAD83, EPSG:4269 — not reprojected, unlike the ACS collections' cartographic boundaries), then `gpio sort hilbert --add-bbox` writes the Hilbert-ordered file with the bbox covering metadata.

Every one of the 2,644 features carries MTFCC `G3500` and LSAD `67` (measured) — the 2020 Census urban area product has no urban/urbanized split, unlike its 2010 predecessor, so there is no categorical column to style on. The default style classes on `aland_sqkm` instead; see the description for the full note on this deviation from the original spec.

`feature_type` decodes `mtfcc` through a table copied from the 2022 MAF/TIGER Feature Class Code PDF (https://www2.census.gov/geo/pdfs/reference/mtfccs2022.pdf), the nearest published vintage to TIGER2024 — see this collection's `doc-mtfcc` source asset. A code this build met that is not in that table is left NULL rather than guessed at; none were, for this collection's data (see docs/spec-reference-layers.md's build report).


## Attribution

U.S. Census Bureau

## License

[CC0-1.0](https://www.census.gov/about/policies/open-gov/open-data.html)

## Contact

Chris Holmes <cholmes@9eo.org>

## Known Issues

There is no urban/urbanized-area class to style on. The 2020 Census urban area product carries a single MTFCC (`G3500`) and a single LSAD (`67`) on every one of its 2,644 features — the 2010-era `UATYP10` urban/urban-cluster split this build was originally asked to carry forward does not exist in `UAC20`. The default style classes on land area instead; see the collection's AGENTS.md for the exact breaks.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
