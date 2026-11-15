# Agent guide — Landmarks — Area

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.**
The [group guide](../AGENTS.md) covers what spans the `reference/` group. If
you cannot point at where a fact came from, it does not belong here.

## What this is

Polygon landmarks from TIGER/Line 2024: **120,734 rows**, combining
[`AREALM`](https://www2.census.gov/geo/tiger/TIGER2024/AREALM/) (civilian
landmarks, 56 state files) and
[`MIL`](https://www2.census.gov/geo/tiger/TIGER2024/MIL/) (military
installations, 1 national file). `landmark_kind` tells the two apart after
the merge.

## Schema

| column | type | notes |
|---|---|---|
| `geoid` | string | `AREAID` |
| `name` | string | `FULLNAME` |
| `state` | string | USPS code; **NULL on every `military` row** (MIL is national, not per-state) |
| `landmark_kind` | string | `"landmark"` or `"military"` |
| `mtfcc`, `feature_type` | string | decoded through the MTFCC list (see `doc-mtfcc` source asset) |
| `aland_sqkm` / `awater_sqkm` | double | **NULL on every `landmark` row** — AREALM has no area fields |
| `geometry`, `bbox` | WKB / struct | NAD83, EPSG:4269 |

## Known issues

`state` and the area columns are NULL on opposite subsets, not the same
one — filter on `landmark_kind`, not on whether a column is NULL, to
isolate one source cleanly.

## Tested queries

Run against `catalog/reference/landmarks-area/landmarks-area.parquet`.

1. Row count and NULL pattern by kind:
   ```sql
   SELECT landmark_kind, count(*), count(state), count(aland_sqkm)
   FROM read_parquet('landmarks-area.parquet') GROUP BY 1;
   -- landmark | 119876 | 119876 | 0
   -- military |    858 |      0 | 858
   ```
2. The 5 most common landmark types nationally:
   ```sql
   SELECT feature_type, count(*) n FROM read_parquet('landmarks-area.parquet')
   GROUP BY 1 ORDER BY n DESC LIMIT 5;
   -- Cemetery                               | 65880
   -- Park                                   | 18686
   -- Local Jail or Detention Center         |  3556
   -- Hospital/Hospice/Urgent Care Facility  |  3397
   -- University or College                 |  3344
   ```
3. Cemeteries in one state (Delaware):
   ```sql
   SELECT count(*) FROM read_parquet('landmarks-area.parquet')
   WHERE state = 'DE' AND feature_type = 'Cemetery';
   -- 102
   ```
