# 2020 Geography Crosswalks

**[🗺️ Open in the data browser](https://browser.portolan-sdi.org/?catalog=https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json#/external/data.source.coop/portolan-mirrors/us-census-catalog/reference/crosswalks/collection.json)** · [Download one table's GeoParquet (t10t20-tract)](https://data.source.coop/portolan-mirrors/us-census-catalog/reference/crosswalks/t10t20-tract.parquet) · [Agent guide](https://source.coop/portolan-mirrors/us-census-catalog/reference/crosswalks/AGENTS.md) · [Source repository](https://github.com/portolan-mirrors/us-census-catalog)

**22,429,855** rows across **29 tables**, each its own parquet file in this collection's directory, from the Census Bureau's [2020 relationship files](https://www2.census.gov/geo/docs/maps-data/data/rel2020/) — every geography pair this catalog carries a crosswalk for. Tabular: no geometry, no `geoid`/`name`/`state` columns, because a relationship file's job is converting between two geography vintages or two geography types, not describing one feature.

`t10t20-tract.parquet` is the one later trend work depends on: it maps 2010 tabulation blocks to 2020 tabulation blocks, with the land and water area each 2010 block split across. It is block-level, not tract-level, because 2010 and 2020 tracts do not nest — the Bureau's own crosswalk for that relationship is built from block-level overlap, and the state+county+tract columns already in that file are what a tract-to-tract join reads. The other 28 tables are every other rel2020 relationship, one file per relationship, read from each subdirectory's single national file (`*_natl.txt`) except `t10t20`, the one relationship rel2020 ships with no national file — those 28 come from `tract`, `blkgrp`, `place`, `cousub`, `cbsa` (3 relationships), `zcta520` (6), `ua` (8), `puma520` (4) and `aiannh` (3).

No PMTiles for this collection — there is no geometry to tile.

This is a mirror — [data.census.gov](https://data.census.gov/) is authoritative, and nothing here is an official Census Bureau product. The exact upstream files this collection was built from are published as `source` assets, linked at their original census.gov URLs, so the original is always one click away; the Bureau's own documentation is linked alongside them. Read the collection's [AGENTS.md](https://source.coop/portolan-mirrors/us-census-catalog/reference/crosswalks/AGENTS.md) before querying: it carries the schema, the join keys, the NULL-rate story and tested queries against the published URLs.

![census](https://img.shields.io/badge/census-blue) ![TIGER/Line](https://img.shields.io/badge/TIGER%2FLine-blue) ![geography](https://img.shields.io/badge/geography-blue) ![United States](https://img.shields.io/badge/United_States-blue) ![crosswalk](https://img.shields.io/badge/crosswalk-blue) ![relationship file](https://img.shields.io/badge/relationship_file-blue) ![2010 Census](https://img.shields.io/badge/2010_Census-blue) ![2020 Census](https://img.shields.io/badge/2020_Census-blue) ![geography conversion](https://img.shields.io/badge/geography_conversion-blue) ![tract relationship](https://img.shields.io/badge/tract_relationship-blue)

## Spatial Coverage

- **Bounding Box**: [-179.231086, 17.831519, -65.168508, 71.439786]

## Temporal Coverage

- **Start**: 2020-04-01T00:00:00Z
- **End**: 2024-12-31T23:59:59Z

## Schema

| Column | Type | Description |
|--------|------|-------------|
| oid_aiannh_20 | int64 |  |
| geoid_aiannh_20 | string |  |
| namelsad_aiannh_20 | string |  |
| arealand_aiannh_20 | int64 |  |
| areawater_aiannh_20 | int64 |  |
| mtfcc_aiannh_20 | string |  |
| classfp_aiannh_20 | string |  |
| funcstat_aiannh_20 | string |  |
| oid_county_20 | int64 |  |
| geoid_county_20 | string |  |
| namelsad_county_20 | string |  |
| arealand_county_20 | int64 |  |
| areawater_county_20 | int64 |  |
| mtfcc_county_20 | string |  |
| classfp_county_20 | string |  |
| funcstat_county_20 | string |  |
| arealand_part | int64 |  |
| areawater_part | int64 |  |

## Files

| File | Size | Checksum |
|------|------|----------|
| ./aiannh-county20.parquet | 139.6 KB | 12202465c977... |
| ./aiannh-cousub20.parquet | 1.0 MB | 1220902f3bc5... |
| ./aiannh-tract20.parquet | 1.7 MB | 1220fab0891e... |
| ./blkgrp.parquet | 7.3 MB | 122033947304... |
| ./cbsa-cbsa23.parquet | 59.6 KB | 12201509ff05... |
| ./cbsa-necta23.parquet | 34.9 KB | 12201103eddf... |
| ./cbsa-ua23.parquet | 145.2 KB | 1220707cd11f... |
| ./cousub.parquet | 2.1 MB | 1220929661f4... |
| ./place.parquet | 2.0 MB | 12206988ffbf... |
| ./puma520-cousub20.parquet | 1.1 MB | 12201f2651e9... |
| ./puma520-puma510.parquet | 249.7 KB | 1220a1f387ac... |
| ./puma520-ua20.parquet | 224.8 KB | 12208439c28a... |
| ./puma520-zcta520.parquet | 1.1 MB | 12203d0f337b... |
| ./t10t20-tract.parquet | 158.1 MB | 1220333194c8... |
| ./tract.parquet | 3.3 MB | 122063479a13... |
| ./ua-cd118.parquet | 121.3 KB | 12202caa269d... |
| ./ua-county20.parquet | 232.0 KB | 1220141d1466... |
| ./ua-cousub20.parquet | 1.4 MB | 122094463652... |
| ./ua-place20.parquet | 1.2 MB | 12207030906f... |
| ./ua-sldl2022.parquet | 268.9 KB | 12207986ddf2... |
| ./ua-sldu2022.parquet | 167.9 KB | 12209a6263b3... |
| ./ua-ua10.parquet | 233.0 KB | 12200b6a0d58... |
| ./ua-zcta520.parquet | 1.0 MB | 1220cbd3496b... |
| ./zcta520-county20.parquet | 1.2 MB | 12205fd8c196... |
| ./zcta520-cousub20.parquet | 2.8 MB | 1220659a7ee4... |
| ./zcta520-place20.parquet | 1.9 MB | 12205111014b... |
| ./zcta520-tabblock20.parquet | 95.5 MB | 1220c7814c70... |
| ./zcta520-tract20.parquet | 3.9 MB | 122050f502fc... |
| ./zcta520-zcta510.parquet | 2.6 MB | 122026b569f3... |
| https://www2.census.gov/geo/docs/maps-data/data/rel2020/ | - | - |

## Quick Start

```python
import geopandas as gpd

gdf = gpd.read_parquet("./aiannh-county20.parquet")
print(gdf.head())
```

## STAC Metadata

- **root**: `../../catalog.json`
- **parent**: `../catalog.json`

## Source

[https://www2.census.gov/geo/docs/maps-data/data/rel2020/](https://www2.census.gov/geo/docs/maps-data/data/rel2020/)

## Processing Notes

Downloaded 2026-11-15 over plain HTTPS from https://www2.census.gov/geo/docs/maps-data/data/rel2020/. Every subdirectory but `t10t20` ships one national file per relationship (`*_natl.txt`); that is the file this build reads for `tract`, `blkgrp`, `place`, `cousub`, `cbsa`, `zcta520`, `ua`, `puma520` and `aiannh` — the per-state files those nine subdirectories also publish are the same relationship split into smaller pieces, so reading the national file once is complete and the per-state files are not read. `t10t20` is the one subdirectory with no national file: its 52 per-state zips (`TAB2010_TAB2020_ST##.zip`) are concatenated into `t10t20-tract.parquet`.

Every file is pipe-delimited with a header row and read directly with DuckDB (`read_csv(..., delim='|', header=true)`); column names are lowercased on write and otherwise kept exactly as published. No geometry, no gpio step, no Hilbert sort — written straight to ZSTD-compressed Parquet with `ROW_GROUP_SIZE 20000`, the same row-group size the spatial write path uses, for consistency rather than necessity.


## Attribution

U.S. Census Bureau

## License

[CC0-1.0](https://www.census.gov/about/policies/open-gov/open-data.html)

## Contact

Chris Holmes <cholmes@9eo.org>

## Known Issues

`t10t20-tract.parquet` is block-level (12,689,707 rows, measured), not tract-level, even though its job is mapping 2010 tracts to 2020 tracts — see the processing notes for why. A join on this file needs the state+county+tract columns, not a direct tract-to-tract key; there is no row that just says "2010 tract X became 2020 tract Y" for a tract that split or merged.


---

*Generated by [Portolan](https://github.com/portolan-sdi/portolan-cli) from STAC metadata and .portolan/metadata.yaml*
