# Agent guide — Landmarks — Point

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.**
The [group guide](../AGENTS.md) covers what spans the `reference/` group. If
you cannot point at where a fact came from, it does not belong here.

## What this is

Point landmarks from
[TIGER/Line 2024 `POINTLM`](https://www2.census.gov/geo/tiger/TIGER2024/POINTLM/):
**1,088,085 rows**, one file per state and territory (56 files).

## Schema

| column | type | notes |
|---|---|---|
| `geoid` | string | `POINTID` |
| `name` | string | `FULLNAME` |
| `state` | string | USPS code of the source file |
| `mtfcc`, `feature_type` | string | decoded through the MTFCC list (see `doc-mtfcc` source asset) |
| `geometry`, `bbox` | WKB / struct | NAD83, EPSG:4269 |

## Known issues

Most of these points are not places. The single largest `feature_type` is
`Cul-de-sac` and the second is `Locality Point` — both are address-system
landmarks TIGER uses to resolve street addresses, not landmarks a person
would look for on a map. Filter `feature_type` before treating this
collection as a point-of-interest dataset.

## Tested queries

Run against `catalog/reference/landmarks-point/landmarks-point.parquet`.

1. The 5 most common feature types nationally:
   ```sql
   SELECT feature_type, count(*) n FROM read_parquet('landmarks-point.parquet')
   GROUP BY 1 ORDER BY n DESC LIMIT 5;
   -- Cul-de-sac               | 668308
   -- Locality Point           | 208547
   -- Cemetery                 | 103934
   -- Mountain Peak or Summit  |  63097
   -- Airport or Airfield      |  13146
   ```
2. The 5 states with the most point landmarks:
   ```sql
   SELECT state, count(*) n FROM read_parquet('landmarks-point.parquet')
   GROUP BY 1 ORDER BY n DESC LIMIT 5;
   -- CA | 96909, TX | 79766, GA | 50313, FL | 50095, VA | 42996
   ```
3. Excluding the two address-system types to get places someone would
   actually look for:
   ```sql
   SELECT count(*) FROM read_parquet('landmarks-point.parquet')
   WHERE feature_type NOT IN ('Cul-de-sac', 'Locality Point');
   -- 211230
   ```
