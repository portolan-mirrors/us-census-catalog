# US Census Demographics — Cloud-Native Mirror

Nationwide U.S. Census Bureau statistics as cloud-native **GeoParquet** and
**PMTiles**, from states down to the ~242,000 block groups and ~8.1 million
2020 census blocks. [data.census.gov](https://data.census.gov/) is the
authoritative source; this catalog is a mirror optimized for analysis and
mapping, and every collection links the exact upstream files it was built
from.

This README is regenerated as collections land; per-collection READMEs carry
the full documentation, including a description of every column.

## What's here

- **Block groups** (`block-groups/`) — ACS 2020–2024 5-year indicators in
  themed chunks: income, people, housing, connectivity. The finest geography
  with income data.
- **Tracts** (`tracts/`) — the same chunks plus a wellbeing chunk (health
  insurance, disability, foreign-born, income by race).
- **Counties and states** — all indicators in one collection per geography.
- **Blocks** (`blocks/`) — 2020 Decennial Census (P.L. 94-171) population,
  race and ethnicity, voting age, housing occupancy, and group quarters at
  the smallest census geography.

Every ACS estimate ships with its margin of error (`*_moe`, 90% confidence),
and headline statistics with a coefficient of variation (`*_cv`) so you can
grey out unreliable geographies. Start with the [agent guide](AGENTS.md) for
tested queries.

## License

U.S. Census Bureau data is a U.S. Government work in the public domain,
published here as CC0-1.0. Cite the U.S. Census Bureau.
