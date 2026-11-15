# Agent guide — 2020 Urban Areas

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.**
The [group guide](../AGENTS.md) covers what spans the `reference/` group. If
you cannot point at where a fact came from, it does not belong here.

## What this is

The Census Bureau's 2020 urban area delineation: **2,644 rows**, one per
urban area in the United States and Puerto Rico, from
[TIGER/Line 2024 `UAC20`](https://www2.census.gov/geo/tiger/TIGER2024/UAC20/).
No demographic data — join to an ACS geography for that.

## Schema

| column | type | notes |
|---|---|---|
| `geoid` | string | `UACE20`, the urban area code |
| `name` | string | `NAMELSAD20`, e.g. "Chicago, IL--IN Urban Area" |
| `mtfcc` | string | always `G3500` (measured — see Known issues) |
| `feature_type` | string | always `"Urban Area"`, decoded from `mtfcc` |
| `aland_sqkm` / `awater_sqkm` | double | land/water area, km² |
| `geometry`, `bbox` | WKB / struct | NAD83, EPSG:4269 (not WGS84) |

## Known issues

There is no urban/urbanized-area split to filter on. Every row carries the
same `mtfcc` (`G3500`) and the same `feature_type` (measured: `SELECT
feature_type, count(*) FROM urban-areas.parquet GROUP BY 1` returns one row,
`("Urban Area", 2644)`). The 2010-era `UATYP10` class this build was asked
to style on does not exist in this file.

## Tested queries

Run against `catalog/reference/urban-areas/urban-areas.parquet`.

1. Total count and total land area:
   ```sql
   SELECT count(*) AS n, round(sum(aland_sqkm), 0) AS total_sqkm
   FROM read_parquet('urban-areas.parquet');
   -- 2644, 273229.0
   ```
2. The 5 largest urban areas by land area:
   ```sql
   SELECT name, aland_sqkm FROM read_parquet('urban-areas.parquet')
   ORDER BY aland_sqkm DESC LIMIT 5;
   -- New York--Jersey City--Newark, NY--NJ Urban Area | 8412.246
   -- Atlanta, GA Urban Area                            | 6612.668
   ```
3. `geoid`/`name` completeness and the land-area range, both checked rather
   than assumed:
   ```sql
   SELECT count(*) FILTER (WHERE name IS NULL OR geoid IS NULL) AS missing,
          min(aland_sqkm) AS smallest, max(aland_sqkm) AS largest
   FROM read_parquet('urban-areas.parquet');
   -- 0, 1.622, 8412.246
   ```
