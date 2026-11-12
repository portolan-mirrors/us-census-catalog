# Conformance waivers

Findings from `portolan check` that are accepted rather than fixed, with the
reasoning. Anything not listed here is a defect.

| Rule | Where | Why accepted | Tracking |
|---|---|---|---|
| PTL-AST-003 (`file:size`/`file:checksum` missing) | `blocks/collection.json` asset `partitioned_data` | The asset's href is a hive glob (`./state_fips=*/*.parquet`) naming 52 files; a single size or checksum is undefined for a set. Each partition's own item asset carries both. | — |
| PTL-CAT-001 (52 children, no subcatalog) | `blocks/collection.json` | The children are the 52 hive partitions of one national dataset, keyed by state FIPS — a deliberate, machine-meaningful layout (`partition:*` fields + glob). Grouping them into subcatalogs would break the hive convention consumers rely on. | — |
| "1 registered asset missing from disk" notice | `blocks/collection.json` asset `partitioned_data` | The metadata scan treats the hive glob `./state_fips=*/*.parquet` (which `check --fix` itself wrote for PTL-PRT-001) as a literal path. Upstream portolan-cli bug; issue text prepared in [upstream-issue-portolan-cli-hive-items.md](upstream-issue-portolan-cli-hive-items.md). Block items are named `NN.json` (data-file stem) as the workaround the scanner accepts. | file against portolan-sdi/portolan-cli |
