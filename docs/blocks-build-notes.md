# Census blocks build notes

How `catalog/blocks/` is built, where every field position came from, and what
was checked against published control totals. Written so the next person can
re-derive the field offsets instead of trusting this file.

Build script: [`tools/build_blocks.py`](../tools/build_blocks.py).
Download script: [`tools/download_blocks.sh`](../tools/download_blocks.sh).

## Sources

| What | URL | Vintage |
| --- | --- | --- |
| Block polygons | `https://www2.census.gov/geo/tiger/TIGER2024/TABBLOCK20/tl_2024_{fips}_tabblock20.zip` | TIGER/Line 2024 |
| Block counts | `https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/{State_Name}/{ab}2020.pl.zip` | 2020 P.L. 94-171 |

104 archives, 7.4 GB, 52 states (50 + DC + PR). Staged in
`staging/blocks-cache/`, which is gitignored and never published.

The block geometry is **TIGER/Line, not the cartographic boundary files** the
ACS collections use. TIGER is unclipped, so coastal blocks extend to the
3-mile limit rather than the shoreline. `ALAND20` is the land-area field and is
what `aland_sqkm` and `pop_density` are computed from; water-only blocks have
`ALAND20 = 0` and therefore a NULL `pop_density`.

## Field positions: where they came from

**The citable source is the Census Bureau's own machine-readable import
scripts**, not the technical-documentation PDF:

```
https://www2.census.gov/programs-surveys/decennial/rdo/about/2020-census-program/Phase3/SupportMaterials/2020PL_R_import_scripts.zip
```

downloaded 2026-11-12. The zip contains `R Versions/pl_geohd_2020_dar.r`,
`pl_part1_2020_dar.r`, `pl_part2_2020_dar.r`, `pl_part3_2020_dar.r`. Each
script carries a commented field dictionary and then the authoritative
`colnames()` assignment, in file order. Those `colnames()` calls are the
layout this build pins. The same directory also holds
`2020_PLSummaryFile_FieldNames.xlsx` and the SAS equivalents, which agree.

The `colnames()` calls, verbatim:

```r
# pl_part1_2020_dar.r
colnames(part1) <- c("FILEID", "STUSAB", "CHARITER", "CIFSN", "LOGRECNO",
                     paste0("P00", c(10001:10071, 20001:20073)))

# pl_part2_2020_dar.r
colnames(part2) <- c("FILEID", "STUSAB", "CHARITER", "CIFSN", "LOGRECNO",
                     paste0("P00", c(30001:30071, 40001:40073)),
                     paste0("H00", 10001:10003))

# pl_part3_2020_dar.r
colnames(part3) <- c("FILEID", "STUSAB", "CHARITER", "CIFSN", "LOGRECNO",
                     paste0("P00", 50001:50010))
```

So each segment is five key fields followed by its tables packed end to end:

| File | Fields | Layout |
| --- | --- | --- |
| `{ab}geo2020.pl` | 97 | geoheader, one row per geographic entity |
| `{ab}000012020.pl` | 149 | 5 key + P1 (71 cells) + P2 (73 cells) |
| `{ab}000022020.pl` | 152 | 5 key + P3 (71) + P4 (73) + H1 (3) |
| `{ab}000032020.pl` | 15 | 5 key + P5 (10) |

All four files are **pipe-delimited and unquoted** (the 2020 geoheader is
delimited, unlike the fixed-width 2010 one). They are joined on `LOGRECNO`,
and every file has one row per logical record, so the join is 1:1. Block
records are `SUMLEV == '750'`.

### 0-based field offsets this build reads

Within a segment, table cell *k* sits at `5 + (offset of the table) + (k - 1)`.

| Column produced | Table cell | File | 0-based index |
| --- | --- | --- | --- |
| `geoid` | `GEOCODE` | geoheader | 9 |
| — | `SUMLEV` | geoheader | 2 |
| — | `LOGRECNO` | geoheader | 7 |
| — | `STATE`, `COUNTY`, `TRACT`, `BLOCK` | geoheader | 12, 14, 32, 34 |
| — | `LOGRECNO` | seg 1/2/3 | 4 |
| `pop_total` | P1-1 `P0010001` | seg 1 | 5 |
| `pop_white` | P1-3 `P0010003` | seg 1 | 7 |
| `pop_black` | P1-4 `P0010004` | seg 1 | 8 |
| `pop_aian` | P1-5 `P0010005` | seg 1 | 9 |
| `pop_asian` | P1-6 `P0010006` | seg 1 | 10 |
| `pop_nhpi` | P1-7 `P0010007` | seg 1 | 11 |
| `pop_other` | P1-8 `P0010008` | seg 1 | 12 |
| `pop_two_plus` | P1-9 `P0010009` | seg 1 | 13 |
| `pop_hispanic` | P2-2 `P0020002` | seg 1 | 77 |
| `pop_white_nh` | P2-5 `P0020005` | seg 1 | 80 |
| `vap_total` | P3-1 `P0030001` | seg 2 | 5 |
| `housing_units` | H1-1 `H0010001` | seg 2 | 149 |
| `housing_occupied` | H1-2 `H0010002` | seg 2 | 150 |
| `housing_vacant` | H1-3 `H0010003` | seg 2 | 151 |
| `group_quarters_pop` | P5-1 `P0050001` | seg 3 | 5 |

P2 starts at `5 + 71 = 76`, so P2-*k* is at `75 + k`. H1 starts at
`5 + 71 + 73 = 149`.

### What the race columns actually mean

`pop_white` … `pop_other` are the **race-alone** counts (`P0010003`–
`P0010008`), and `pop_two_plus` is `P0010009`, "Population of two or more
races". `P0010002` ("Population of one race") is an intermediate subtotal and
is deliberately *not* carried, which is why the seven race columns sum to
`pop_total` and not to something larger:

```
pop_white + pop_black + pop_aian + pop_asian + pop_nhpi + pop_other
  + pop_two_plus == pop_total
```

`pop_white_nh` is P2-5, white alone **and** not Hispanic or Latino, so it is
not comparable to `pop_white`; `pop_hispanic` (P2-2) crosses every race.

### Verification, not memory

The offsets above were confirmed three ways before the build ran:

1. **Field counts.** Alaska's four files parse to exactly 97 / 149 / 152 / 15
   fields, matching the `colnames()` lengths. `build_blocks.py` re-checks this
   for every state (`NFIELDS`, `check_field_counts`) and aborts on a mismatch,
   so a changed layout cannot silently shift the counts into wrong columns.
2. **Redundant fields inside the geoheader.** The geoheader carries its own
   `POP100` (index 90) and `HU100` (index 91). For Alaska's state record both
   equal the P1-1 and H1-1 values read from the segments: 733,391 and 326,200.
   Two independently located fields agreeing is what pins index 5 of segment 1
   to P1-1.
3. **Published control totals.** See below.

`GEOID` (index 8) carries the summary-level prefix — `7500000US020130001001000`
for a block, `0400000US02` for a state — so the build uses `GEOCODE`
(index 9), which is the bare 15-character code. The build also asserts
`GEOCODE == STATE || COUNTY || TRACT || BLOCK` on every row
(`geoid_mismatch`, 0 everywhere).

## Pipeline

Per state, one at a time, scratch deleted immediately after:

1. **`ogr2ogr`** shapefile → EPSG:4326 Parquet, selecting only `GEOID20` and
   `ALAND20`. GDAL does the reprojection; TIGER ships in EPSG:4269 (NAD83).
   DuckDB's `ST_Transform` is deliberately not used — it moves the geometry
   correctly but stamps CRS metadata that does not round-trip.
2. **DuckDB** joins the four PL files on `LOGRECNO`, filters `SUMLEV = '750'`,
   joins to the geometry on `GEOID20 = GEOCODE`, and derives the rates and
   density. Output is scratch: DuckDB writes GeoParquet 1.0 with no bbox
   covering column.
3. **`gpio sort hilbert --add-bbox`** writes the partition — Hilbert row order
   (PTL-DAT-006), bbox covering column with row-group statistics
   (PTL-DAT-007), ZSTD, sized row groups — in a single pass, and normalizes
   WGS84 lon/lat to how the spec spells it, an omitted `crs` key.

DuckDB's positional column names are zero-padded to the width of the widest
index, so a 97-field file yields `column00` and a 149-field file `column000`.
The build sidesteps that by passing an explicit `columns={'f0': 'VARCHAR', …}`
spec, and reads with `quote='' escape=''` because the PL files are unquoted and
a stray `"` in a `NAME` field would otherwise swallow delimiters.

### The geoheader is Latin-1, not UTF-8

`read_csv` must be given `encoding='latin-1'`. The geoheader carries place
names in ISO-8859-1; the first record to break a UTF-8 read is Arizona's
Kayenta CCD (line 69 of `azgeo2020.pl`), and Colorado fails at line 130.
DuckDB validates the encoding of the whole line even though every field this
build reads is plain ASCII, so the failure looks like a parse error in a
numeric column and is not one.

Do **not** reach for `ignore_errors=true`, which DuckDB suggests in that error
message. It would skip the offending rows, and the rows are whole census
tracts and counties — the national total would come out quietly short rather
than failing loudly.

`verify_output()` reads each finished file back and asserts GeoParquet 1.1
metadata, the bbox covering, bbox statistics in *every* row group, an absent
`crs` key, and ZSTD on the geometry column. Each of those is something a writer
in this chain has been observed to drop, so they are asserted rather than
assumed.

### Two things worth knowing if you change the pipeline

- **`gpio convert geoparquet` already Hilbert-sorts**, so the earlier
  convert-then-sort pair was one redundant full pass. One `gpio sort hilbert`
  does the whole job.
- **Do not rewrite the finished file with pyarrow** to "restore" statistics.
  gpio already emits them, and a pyarrow rewrite at a fixed `row_group_size`
  re-chunks the file into an unbalanced split (20,000 + 198 rows for Delaware)
  that makes `gpio check` report "poor spatial ordering (overlap ratio: 1.00)"
  even though the row order is untouched. The reference catalog needs that
  rewrite because its layers contain null geometries, which makes GDAL drop
  bbox statistics; blocks always have geometry.

## Output layout

```
catalog/blocks/
├── state_fips=01/01.parquet
├── state_fips=02/02.parquet
…  52 directories …
└── state_fips=72/72.parquet
```

Gitignored (`*.parquet`) but inside `publish_dir`, so the bytes publish with
the metadata without ever entering git.

### Why hive directories and not 52 flat files

This was checked against the Portolan CLI v0.8.0 source
(`/Users/cholmes/repos/portolan-cli`) and the spec
(`portolan-spec/specs/portolan/{core,formats}.md`) rather than guessed, because
the three candidate layouts are not equivalent:

- **Hive `key=value/` directories are the only multi-file scheme Portolan
  recognizes.** `portolan_cli/partitioning.py` matches
  `^([a-zA-Z_][a-zA-Z0-9_]*)=.+$`, and `detect_partitioning` finds pre-existing
  hive data and writes `partition:scheme`, `partition:keys`, and
  `partition:file_count` onto the collection, plus a `partitioned_data` glob
  asset. There is no `parts/` convention and no `_metadata` file.
- **A flat directory of 52 files produces zero STAC items.**
  `_derive_item_id_and_asset_level` in `portolan_cli/preparation.py` treats a
  parquet sitting directly in the collection directory as a *collection-level
  asset*, so `blocks-01.parquet … blocks-56.parquet` would land as 52
  collection-level data assets with no items, no per-state bbox, and no glob
  for consumers to query. `core.md` says an ordinary collection with multiple
  distinct data files represents each as an item, so that layout also
  contradicts the spec.
- **`portolan add` derives one item per directory**, so the hive layout yields
  52 items with real per-state bounding boxes and row counts, and
  `formats.md` explicitly endorses items for partitions that are
  "user-meaningful units (countries, regions)" — which is what states are.

The partition key is **`state_fips`**, not `state`. A hive key is synthesized
as a column when the glob is read, and `state` is already a column here
carrying the USPS code; naming the key `state_fips` keeps the FIPS code and the
USPS code as two distinct columns instead of one shadowing the other.

The file inside each directory is named for the partition value (`01.parquet`),
which is both what geoparquet-io's own column partitioner emits and what
`portolan scan`'s naming heuristic expects (the stem must relate to the parent
directory name; `data.parquet` is flagged).

`kdtree_cell=` is deliberately **not** used — that key name is reserved for
`portolan partition`'s spatial KD-tree strategy and would imply spatial cells
rather than states.

### Registering the collection

```bash
portolan add catalog/blocks/ --datetime 2020-04-01   # 52 items + partition:* + glob asset
portolan check                                        # expect PTL-PRT-001
portolan check --fix                                  # writes partition:glob
```

`portolan add` writes `partition:scheme`, `partition:keys`, and
`partition:file_count` but not the collection-level `partition:glob` that
PTL-PRT-001 requires, so one auto-fixable finding on the first check is
expected rather than a defect. The glob is `./state_fips=*/*.parquet`; keeping
it relative is what lets PTL-DAT-014 (single schema across all partitions)
actually run locally, since that rule skips absolute and remote globs.

Relevant per-file rules, all satisfied by the `gpio sort hilbert` step:
PTL-DAT-006 (spatial row order), PTL-DAT-007 (row-group spatial statistics),
PTL-DAT-008 (row groups ≤ 150,000 rows — gpio writes 49,152), PTL-DAT-012
(GeoParquet 1.1). PTL-DAT-014 requires identical column names and types across
all 52 files; `validate()` checks that directly by comparing every file's
schema signature.

## Columns

| Column | Type | Source |
| --- | --- | --- |
| `geoid` | string(15) | geoheader `GEOCODE` |
| `state` | string(2) | USPS code |
| `pop_total` | int32 | P1-1 |
| `pop_white`, `pop_black`, `pop_aian`, `pop_asian`, `pop_nhpi`, `pop_other` | int32 | P1-3 … P1-8, race alone |
| `pop_two_plus` | int32 | P1-9 |
| `pop_hispanic` | int32 | P2-2 |
| `pop_white_nh` | int32 | P2-5, white alone not Hispanic |
| `vap_total` | int32 | P3-1, population 18+ |
| `housing_units`, `housing_occupied`, `housing_vacant` | int32 | H1-1, H1-2, H1-3 |
| `group_quarters_pop` | int32 | P5-1 |
| `pct_white_nh`, `pct_black`, `pct_hispanic` | double | % of `pop_total`, 2 dp, NULL when `pop_total = 0` |
| `pct_vacant` | double | % of `housing_units`, 2 dp, NULL when `housing_units = 0` |
| `pop_density` | double | people per km², 1 dp, NULL when `ALAND20 = 0` |
| `aland_sqkm` | double | `ALAND20 / 1e6`, 3 dp |
| `geometry` | WKB MultiPolygon/Polygon | TIGER, EPSG:4326 |
| `bbox` | struct | covering, per GeoParquet 1.1 |

Roughly a third of all blocks are unpopulated (`pop_total = 0`), so the three
`pct_*` population columns are NULL on a large share of rows by design. That is
a property of census blocks, not missing data.

## Validation

Run `python3 tools/build_blocks.py --validate-only` to re-check the saved
report at `staging/blocks-build-report.json`.

Checks, all enforced in `validate()`:

- **National total.** `pop_total` summed over the 50 states + DC must equal
  exactly **331,449,281**, the published 2020 resident population. Puerto Rico
  must equal **3,285,874**.
- **Housing identity.** `housing_occupied + housing_vacant == housing_units`
  on every block.
- **GEOID uniqueness** across all 52 partitions at once, and
  `GEOCODE == STATE||COUNTY||TRACT||BLOCK` on every row.
- **Orphans.** Every TIGER block must have a PL row and vice versa, counted in
  both directions per state.

Per-state spot checks against published 2020 counts are in the build report;
the ones verified by hand during development were Alaska 733,391, Delaware
989,948, and DC 689,545, each matching the published figure exactly.

Blocks tile a state exhaustively, so the block sum equals the state total: for
Alaska, summing P1-1 over all 28,568 blocks gives 733,391, the same number the
geoheader's own `SUMLEV = '040'` record carries.

## Results of the full run

Built 2026-11-12, 52 partitions, 4 parallel workers, ~6 minutes wall clock
(slowest state Texas at 94 s). Log: `staging/build_blocks.log`; machine-readable
report: `staging/blocks-build-report.json`.

| | |
| --- | --- |
| Partitions | 52 / 52, no failures |
| Blocks | **8,174,955** |
| 50 states + DC population | **331,449,281** — matches published exactly |
| Puerto Rico population | **3,285,874** — matches published exactly |
| Housing units | 142,096,895 |
| Total size | **5.23 GB** |
| Orphans (both directions) | 0 |
| Blocks where occupied + vacant ≠ units | 0 |
| Blocks where GEOCODE ≠ STATE‖COUNTY‖TRACT‖BLOCK | 0 |
| Duplicate GEOIDs across all 52 partitions | 0 |
| Distinct schemas across partitions | 1 |
| Max row-group rows | 49,152 (PTL-DAT-008 limit is 150,000) |

`gpio check` passes all 28 spec checks on every partition, reporting
GeoParquet 1.1.0, a bbox covering column, ZSTD on the geometry column, and
"data appears to be spatially ordered".

### Per-state spot checks against published 2020 counts

Ten states checked by hand against the published 2020 resident population;
all ten match exactly.

| State | Blocks | Built | Published |
| --- | --- | --- | --- |
| CA | 519,723 | 39,538,223 | 39,538,223 |
| TX | 668,757 | 29,145,505 | 29,145,505 |
| FL | 390,066 | 21,538,187 | 21,538,187 |
| NY | 288,819 | 20,201,249 | 20,201,249 |
| PA | 336,985 | 13,002,700 | 13,002,700 |
| IL | 369,978 | 12,812,508 | 12,812,508 |
| OH | 276,428 | 11,799,448 | 11,799,448 |
| GA | 232,717 | 10,711,908 | 10,711,908 |
| VT | 24,611 | 643,077 | 643,077 |
| WY | 53,769 | 576,851 | 576,851 |

### Reading the whole collection

The hive glob queries all 52 partitions as one table, and the synthesized
`state_fips` key sits alongside the `state` USPS column without shadowing it:

```sql
SELECT state_fips, state, count(*) AS blocks, sum(pop_total) AS pop
FROM read_parquet('catalog/blocks/state_fips=*/*.parquet', hive_partitioning=true)
GROUP BY 1, 2 ORDER BY 1;
-- 52 partitions, 8,174,955 blocks, 334,735,155 people
```

### Every partition

| FIPS | State | Blocks | Population | Housing units | Size |
| --- | --- | --- | --- | --- | --- |
| 01 | AL | 185,976 | 5,024,279 | 2,288,330 | 122.6 MB |
| 02 | AK | 28,568 | 733,391 | 326,200 | 70.6 MB |
| 04 | AZ | 155,444 | 7,151,502 | 3,082,000 | 101.0 MB |
| 05 | AR | 136,422 | 3,011,524 | 1,365,265 | 109.6 MB |
| 06 | CA | 519,723 | 39,538,223 | 14,392,140 | 321.7 MB |
| 08 | CO | 140,345 | 5,773,714 | 2,491,404 | 112.0 MB |
| 09 | CT | 49,926 | 3,605,944 | 1,530,197 | 28.8 MB |
| 10 | DE | 20,198 | 989,948 | 448,735 | 9.8 MB |
| 11 | DC | 6,012 | 689,545 | 350,364 | 2.0 MB |
| 12 | FL | 390,066 | 21,538,187 | 9,865,350 | 159.0 MB |
| 13 | GA | 232,717 | 10,711,908 | 4,410,956 | 140.2 MB |
| 15 | HI | 14,732 | 1,455,271 | 561,066 | 12.0 MB |
| 16 | ID | 81,879 | 1,839,106 | 751,859 | 104.5 MB |
| 17 | IL | 369,978 | 12,812,508 | 5,426,429 | 131.2 MB |
| 18 | IN | 204,568 | 6,785,528 | 2,923,175 | 87.9 MB |
| 19 | IA | 175,199 | 3,190,369 | 1,412,789 | 72.4 MB |
| 20 | KS | 172,529 | 2,937,880 | 1,275,689 | 71.5 MB |
| 21 | KY | 132,662 | 4,505,836 | 1,994,323 | 134.8 MB |
| 22 | LA | 142,874 | 4,657,757 | 2,073,200 | 96.9 MB |
| 23 | ME | 47,138 | 1,362,359 | 739,072 | 58.3 MB |
| 24 | MD | 83,827 | 6,177,224 | 2,530,844 | 52.6 MB |
| 25 | MA | 107,278 | 7,029,917 | 2,998,537 | 48.6 MB |
| 26 | MI | 254,730 | 10,077,331 | 4,570,173 | 100.1 MB |
| 27 | MN | 198,705 | 5,706,494 | 2,485,558 | 126.9 MB |
| 28 | MS | 112,241 | 2,961,279 | 1,319,945 | 99.8 MB |
| 29 | MO | 253,632 | 6,154,913 | 2,786,621 | 162.8 MB |
| 30 | MT | 88,417 | 1,084,225 | 514,803 | 129.6 MB |
| 31 | NE | 119,103 | 1,961,504 | 844,278 | 41.5 MB |
| 32 | NV | 57,409 | 3,104,614 | 1,281,018 | 66.6 MB |
| 33 | NH | 31,948 | 1,377,529 | 638,795 | 21.9 MB |
| 34 | NJ | 137,972 | 9,288,994 | 3,761,229 | 54.5 MB |
| 35 | NM | 107,215 | 2,117,522 | 940,859 | 87.0 MB |
| 36 | NY | 288,819 | 20,201,249 | 8,488,066 | 151.5 MB |
| 37 | NC | 236,638 | 10,439,388 | 4,708,710 | 171.0 MB |
| 38 | ND | 84,566 | 779,094 | 370,642 | 41.0 MB |
| 39 | OH | 276,428 | 11,799,448 | 5,242,524 | 126.4 MB |
| 40 | OK | 180,154 | 3,959,353 | 1,746,807 | 91.4 MB |
| 41 | OR | 130,807 | 4,237,256 | 1,813,747 | 160.7 MB |
| 42 | PA | 336,985 | 13,002,700 | 5,742,828 | 192.1 MB |
| 44 | RI | 25,649 | 1,097,379 | 483,474 | 12.8 MB |
| 45 | SC | 146,844 | 5,118,425 | 2,344,963 | 93.3 MB |
| 46 | SD | 71,383 | 886,667 | 393,375 | 48.3 MB |
| 47 | TN | 179,717 | 6,910,840 | 3,031,605 | 157.9 MB |
| 48 | TX | 668,757 | 29,145,505 | 11,589,324 | 350.8 MB |
| 49 | UT | 71,207 | 3,271,616 | 1,151,414 | 91.4 MB |
| 50 | VT | 24,611 | 643,077 | 334,318 | 28.9 MB |
| 51 | VA | 163,491 | 8,631,393 | 3,618,247 | 157.5 MB |
| 53 | WA | 158,093 | 7,705,281 | 3,202,241 | 99.3 MB |
| 54 | WV | 72,558 | 1,793,716 | 855,635 | 88.2 MB |
| 55 | WI | 203,059 | 5,893,718 | 2,727,726 | 139.0 MB |
| 56 | WY | 53,769 | 576,851 | 271,887 | 74.3 MB |
| 72 | PR | 41,987 | 3,285,874 | 1,598,159 | 19.6 MB |
| | **52** | **8,174,955** | **334,735,155** | **142,096,895** | **5.23 GB** |

## Tiles rebuilt as a census pyramid (2026-11-13)

`blocks.pmtiles` is now built with `tylertoo pyramid`: z0–z5 counties and
z6–z9 tracts, both exact sums of these block counts with the rate columns
recomputed from the summed counts (`tools/build_tile_staging.py`), and
z10–z14 the blocks themselves. Connecticut's 2020 block GEOIDs are
crosswalked onto the 2024 planning-region geographies on the preserved
6-digit tract number before grouping, so the aggregates still total
334,735,155 exactly.
