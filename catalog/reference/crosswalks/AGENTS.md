# Agent guide — 2020 Geography Crosswalks

Guidance for AI agents and automated clients working with this collection.

**Every claim in this file is quoted from a source or measured from the data.**
The [group guide](../AGENTS.md) covers what spans the `reference/` group. If
you cannot point at where a fact came from, it does not belong here.

## What this is

**22,429,855 rows across 29 tables**, each its own parquet file in this
directory, from the Census Bureau's
[2020 relationship files](https://www2.census.gov/geo/docs/maps-data/data/rel2020/).
Tabular — no geometry, no `geoid`/`name`/`state` columns, because a
relationship file converts between two geographies rather than describing
one feature. Column names are lowercased from the source files; otherwise
kept exactly as published.

`t10t20-tract.parquet` is the one later trend work depends on: 2010
tabulation blocks to 2020 tabulation blocks (block-level, because 2010 and
2020 tracts do not nest). The other 28 are one file per rel2020
relationship, named `<subdir>-<other-side>.parquet` (or just `<subdir>`
where the subdirectory holds only one relationship).

## Known issues

`t10t20-tract.parquet` has no single column that says "this 2010 tract
became this 2020 tract" — it is block-level, so a tract-to-tract join
needs `state_2010`+`county_2010`+`tract_2010` on one side and the `_2020`
equivalents on the other, grouped (see query 2 below); a 2010 tract can map
to more than one 2020 tract.

## Tested queries

Run from `catalog/reference/crosswalks/`.

1. Row count per table:
   ```python
   import duckdb, glob
   for f in sorted(glob.glob('*.parquet')):
       print(f, duckdb.sql(f"select count(*) from read_parquet('{f}')").fetchone()[0])
   # t10t20-tract.parquet 12689707
   # zcta520-tabblock20.parquet 8180866
   # blkgrp.parquet 337326
   # ... 29 tables, 22429855 rows total
   ```
2. How many 2020 tracts a 2010 tract split into, Autauga County AL:
   ```sql
   SELECT state_2010, county_2010, tract_2010, count(DISTINCT tract_2020) AS n_2020_tracts
   FROM read_parquet('t10t20-tract.parquet')
   WHERE state_2010='01' AND county_2010='001'
   GROUP BY 1,2,3 ORDER BY n_2020_tracts DESC LIMIT 3;
   -- 020802 -> 3 tracts, 020500 -> 3 tracts, 021100 -> 2 tracts
   ```
3. `tract.parquet`'s own schema (the 2010<->2020 tract relationship the
   Bureau publishes directly, distinct from `t10t20-tract.parquet`'s
   block-level version):
   ```sql
   DESCRIBE SELECT * FROM read_parquet('tract.parquet');
   -- oid_tract_20, geoid_tract_20, namelsad_tract_20, ... oid_tract_10, ...
   ```
