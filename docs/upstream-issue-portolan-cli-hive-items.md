### What happened?

Three layout conventions disagree on a hive-partitioned collection such as `blocks/state_fips=NN/NN.parquet` (52 partitions).

First, `portolan add blocks/` derives each item id from the parent directory. It writes `state_fips=01/state_fips=01.json`.

Second, `metadata/detection.py::get_stored_metadata` only recognizes an item named after the data file stem, `state_fips=01/01.json`. Every partition therefore scans as `MetadataStatus.MISSING` with "Missing STAC metadata for file". The check summary then reports "52 registered asset(s) are missing from disk". The files are on disk.

Third, `portolan check --fix` acts on those false MISSING results. It writes a second item per partition. The new `01.json` carries a creation-timestamp datetime, next to `state_fips=01.json` with the real `--datetime`. The collection's item links double from 52 to 104. `stac-geoparquet` then indexes the duplicates.

There is one more case. `check --fix` writes a `partitioned_data` glob asset, `./state_fips=*/*.parquet`, for PTL-PRT-001. The metadata scan treats that glob as a literal path. It reports the glob as a missing file.

### Why it matters

The CLI's own recommended hive layout cannot pass the CLI's own metadata scan. The `add` then `check --fix` sequence corrupts the collection with duplicate items that carry wrong datetimes. The false "missing from disk" warning also hides real losses.

### Priority

P1

### How to reproduce

Reproduced 2026-11-12 with portolan 0.8.0 while building `portolan-mirrors/us-census-catalog`.

1. Lay out one collection as 52 hive partitions: `blocks/state_fips=NN/NN.parquet`.
2. Run `portolan add blocks/ --datetime 2020-04-01`.
3. Run `portolan check --fix`.
4. Observe 104 item links, stray `NN.thumb.jpg` files, and duplicate items per partition.
<!-- ste-ok: LONG_SENTENCE this list step is five short sentences, not one long one -->
5. Delete the `NN.json` duplicates. Keep the `state_fips=NN.json` set. Run `portolan check`. It reports 53 false missing assets. That is 52 partitions plus the glob.
6. Rename the items to `NN.json` with id `NN`. The count drops to 1. The glob warning remains.

### Implementation notes

Code paths: `metadata/scan.py::_scan_collection` accepts any STAC Item name in the item directory. `metadata/detection.py::get_stored_metadata` requires `{stem}.json`. `validation/runner.py::_notice_message` writes the summary text.

Two options. Teach `get_stored_metadata` the scanner's rule. It would accept any STAC Item in the directory whose asset href resolves to the file. Or make `add` name hive items after the data stem. In either case, skip glob-href assets in the registration sweep. The summary wording should also distinguish "file absent" from "no stored metadata found". This is the same family as #709, but the trigger is the hive layout that `partitioning.py` itself canonicalizes.

### How to confirm the fix

Run `add` then `check --fix` on a hive-partitioned collection. The sequence is idempotent. There are no duplicate items and no false MISSING results. Glob assets are exempt from the on-disk sweep.

### Version

portolan 0.8.0, macOS (Apple Silicon), Python 3.
