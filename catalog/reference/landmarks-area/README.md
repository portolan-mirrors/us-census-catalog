# Landmarks — Area

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/reference/landmarks-area/collection.json)** · [🧭 Census Atlas](https://portolan-mirrors.github.io/us-census-catalog/#c=reference/landmarks-area) · [Download the GeoParquet](https://data.source.coop/portolan-mirrors/us-census-catalog/reference/landmarks-area/landmarks-area.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/reference/landmarks-area/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

Polygon landmarks from TIGER/Line 2024: all **120,734** features combining [`AREALM`](https://www2.census.gov/geo/tiger/TIGER2024/AREALM/) (civilian landmarks, one file per state) and [`MIL`](https://www2.census.gov/geo/tiger/TIGER2024/MIL/) (military installations, one national file) into a single table, with `landmark_kind` set to `landmark` or `military` so the two sources stay distinguishable after the merge. Measured: 119,876 `landmark` rows (all 56 states carry a `state` column) and 858 `military` rows (none do — `MIL` is a national file, not per-state, so there is no state to carry, and `AREALM` carries no `aland_sqkm`/`awater_sqkm` so those are NULL on every `landmark` row).

`feature_type` decodes each row's `mtfcc` through the Census Bureau's MAF/TIGER Feature Class Code list; see the collection's processing notes for the exact source and which codes, if any, this build could not decode. Measured nationally, the five most common types are cemeteries, parks, local jails and detention centers, hospitals, and universities or colleges — the five the default style colors.

The PMTiles archive is a single band at full resolution, built with [tylertoo](https://github.com/geoparquet-io/tylertoo) `tiles` (not `pyramid` — there is no coarser geography to step up to below this collection, so every zoom draws this collection's own features, thinned to fit the tile-size cap where a zoom is too dense to draw in full). Statistics come from the GeoParquet; this collection has no `*_moe` columns to exclude.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](https://source.coop/portolan-mirrors/us-census-catalog/reference/landmarks-area/AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![TIGER/Line](https://img.shields.io/badge/TIGER%2FLine-blue) ![geography](https://img.shields.io/badge/geography-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![landmarks](https://img.shields.io/badge/landmarks-blue) ![AREALM](https://img.shields.io/badge/AREALM-blue) ![MIL](https://img.shields.io/badge/MIL-blue) ![MTFCC](https://img.shields.io/badge/MTFCC-blue) ![military installation](https://img.shields.io/badge/military_installation-blue) ![cemetery](https://img.shields.io/badge/cemetery-blue) ![park](https://img.shields.io/badge/park-blue) ![TIGER](https://img.shields.io/badge/TIGER-blue)

## Spatial Coverage

- **Bounding Box**: [-179.147236, -14.548699, -64.605552, 71.359879]

## Temporal Coverage

- **Start**: 2020-04-01T00:00:00Z
- **End**: 2024-12-31T23:59:59Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| geoid | string | `AREAID`, from TIGER's internal address/area ID scheme -- not a census tabulation GEOID. |
| name | string | `FULLNAME`. |
| state | string | USPS code of the state file this row's `AREALM` zip was read from. NULL on every `landmark_kind = 'military'` row (measured, 858 of 120,734): `MIL` is one national file, not 56 state files, so there is no state to carry. |
| landmark_kind | string | `'landmark'` for a row from `AREALM` (civilian landmarks, 119,876 rows measured) or `'military'` for a row from `MIL` (858 rows measured). Not a source column -- set by tools/build_reference.py from which file the row came from. |
| mtfcc | string | `MTFCC`. |
| feature_type | string | `mtfcc` decoded through the 2022 MAF/TIGER Feature Class Code list. Most common nationally (measured): Cemetery, Park, Local Jail or Detention Center, Hospital/Hospice/Urgent Care Facility, University or College. |
| aland_sqkm | double | `ALAND / 1e6`. NULL on every `landmark_kind = 'landmark'` row (measured, 119,876 of 120,734) -- `AREALM` carries no area fields at all. |
| awater_sqkm | double | `AWATER / 1e6`. NULL on the same rows as `aland_sqkm`, for the same reason. |
| geometry | binary | Landmark boundary polygon, WKB-encoded. Written in the source CRS, NAD83 (EPSG:4269) -- unlike the ACS collections, this is kept rather than reprojected to WGS84/OGC:CRS84, so the GeoParquet `geo` metadata carries an explicit `crs` key. |
| bbox | struct<xmin: double, ymin: double, xmax: double, ymax: double> | GeoParquet 1.1 covering struct for the row's geometry, written by gpio, with row-group statistics. |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./landmarks-area.pmtiles | 149.0 MB | 1220de752979... |
| ./landmarks-area.parquet | 65.9 MB | 1220464c66f5... |
| ./thumbnail.png | 24.1 KB | 122033f6088b... |
| ./styles/default.json | 1.8 KB | 12203be46520... |
| ./styles/kind.json | 988 B | 12204c14ed09... |
| https://www2.census.gov/geo/tiger/TIGER2024/AREALM/ | - | - |
| https://www2.census.gov/geo/tiger/TIGER2024/MIL/tl_2024_us_mil.zip | - | - |
| https://www2.census.gov/geo/pdfs/reference/mtfccs2022.pdf | - | - |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./landmarks-area.pmtiles")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/geo/tiger/TIGER2024/AREALM/](https://www2.census.gov/geo/tiger/TIGER2024/AREALM/)

## Processing Notes

Built from 56 state `AREALM` shapefiles (https://www2.census.gov/geo/tiger/TIGER2024/AREALM/, 68 MB total) plus the one national `MIL` shapefile (https://www2.census.gov/geo/tiger/TIGER2024/MIL/tl_2024_us_mil.zip, 3 MB), unioned into one table after each is converted independently. Downloaded 2026-11-15 over plain HTTPS, no API key. GeoParquet written with the same path as the rest of this catalog (pyarrow, ZSTD, sized row groups, bbox covering column — tools/build_wide_themes.py documents the convention, verified against catalog/counties/county-income/county-income.parquet): `gpio convert geoparquet` reads the shapefile, keeping the source CRS (NAD83, EPSG:4269 — not reprojected, unlike the ACS collections' cartographic boundaries), then `gpio sort hilbert --add-bbox` writes the Hilbert-ordered file with the bbox covering metadata.

`state` is the USPS code for the AREALM file each row's state zip was read from; MIL rows carry `state = NULL`, since MIL is one national file, not 56 state files, and has no state column of its own to carry forward. `landmark_kind` is `'landmark'` for every AREALM row and `'military'` for every MIL row — not read off any source column, since neither file has one. AREALM carries no `ALAND`/`AWATER`, so `aland_sqkm`/`awater_sqkm` are NULL on every `landmark` row; MIL has both, so every `military` row has them.

`feature_type` decodes `mtfcc` through a table copied from the 2022 MAF/TIGER Feature Class Code PDF (https://www2.census.gov/geo/pdfs/reference/mtfccs2022.pdf), the nearest published vintage to TIGER2024 — see this collection's `doc-mtfcc` source asset. A code this build met that is not in that table is left NULL rather than guessed at; none were, for this collection's data (see docs/spec-reference-layers.md's build report).


## Attribution

U.S. Census Bureau

## License

[CC0-1.0](https://www.census.gov/about/policies/open-gov/open-data.html)

## Contact

Chris Holmes <cholmes@9eo.org>

## Known Issues

`state` and `aland_sqkm`/`awater_sqkm` are NULL on different rows for different reasons, not the same reason: `state` is NULL on the 858 `landmark_kind = 'military'` rows (MIL is a national file with no per-state source to read a state from), while `aland_sqkm`/`awater_sqkm` are NULL on the 119,876 `landmark_kind = 'landmark'` rows (AREALM carries no area fields at all). Filter on `landmark_kind`, not on whether a column is NULL, if you need one kind cleanly.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
