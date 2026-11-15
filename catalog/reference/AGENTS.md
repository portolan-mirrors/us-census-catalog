# Agent guide — Reference Geography

Guidance for AI agents and automated clients working with this group.

**Every claim in this file is quoted from a source or measured from the data.**
The [catalog-level AGENTS.md](../AGENTS.md) covers what spans groups; each
collection's own `AGENTS.md` carries its schema and tested queries. If you
cannot point at where a fact came from, it does not belong here.

## What this group is

Geography that carries no demographic statistic, so it stays out of the
seven geography groups (block-groups, tracts, counties, states, zctas,
places, congressional-districts, blocks). Four collections, all from
TIGER/Line 2024 and the 2020 Census relationship files:

| collection | rows | geometry |
|---|---|---|
| [urban-areas](./urban-areas/AGENTS.md) | 2,644 | polygon |
| [landmarks-area](./landmarks-area/AGENTS.md) | 120,734 | polygon |
| [landmarks-point](./landmarks-point/AGENTS.md) | 1,088,085 | point |
| [crosswalks](./crosswalks/AGENTS.md) | 22,429,855 (29 tables) | none |

None of the four shares a geometry or a `geoid` with another, and none
joins to an ACS collection on `geoid` either — a `geoid` here is a TIGER
area, point or landmark ID, not a census tabulation geography. Join through
`crosswalks` or a spatial join, not a `geoid` string match.

## Shared quirks

- Every spatial collection keeps the **source CRS (NAD83, EPSG:4269)**,
  unlike the ACS collections' cartographic boundaries — do not assume
  WGS84 lon/lat without checking the GeoParquet `geo` metadata.
- `feature_type` on all three spatial collections is decoded from `mtfcc`
  through the 2022 MAF/TIGER Feature Class Code list (the nearest published
  vintage to TIGER2024); see each collection's `doc-mtfcc` source asset.
- `crosswalks` has no PMTiles — there is no geometry to tile.

## Tested queries

1. Confirm no two spatial collections share a `geoid` namespace (sampled):
   ```sql
   SELECT geoid FROM read_parquet('urban-areas/urban-areas.parquet') LIMIT 3;
   -- 5-digit UACE20 codes, e.g. 00037
   SELECT geoid FROM read_parquet('landmarks-area/landmarks-area.parquet') LIMIT 3;
   -- long numeric AREAID strings, 13+ digits
   ```
2. Count rows across the whole group in one pass:
   ```sql
   SELECT 'urban-areas', count(*) FROM read_parquet('urban-areas/urban-areas.parquet')
   UNION ALL
   SELECT 'landmarks-area', count(*) FROM read_parquet('landmarks-area/landmarks-area.parquet')
   UNION ALL
   SELECT 'landmarks-point', count(*) FROM read_parquet('landmarks-point/landmarks-point.parquet');
   -- urban-areas 2644, landmarks-area 120734, landmarks-point 1088085
   ```
