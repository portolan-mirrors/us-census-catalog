#!/usr/bin/env python3
"""Titles, descriptions, keywords, source assets and metadata.yaml per collection.

The prose layer of the catalog. `tools/make_stac.py` reads this module for
everything a STAC collection carries that is not derivable from the data, and
`--write` here writes the `.portolan/metadata.yaml` files that `portolan add`
reads.

Run order (the whole pipeline is in README.md):

    python3 tools/collection_meta.py --write    # metadata.yaml, BEFORE add
    portolan add catalog/<group>/<id>/ …        # or `portolan add catalog/`
    python3 tools/make_stac.py                  # everything else

`portolan add` reads `.portolan/metadata.yaml`, so the write step has to come
first; `make_stac.py` then patches what the CLI does not emit.

What is asserted here, and from where:

- Row counts are the build's own (`docs/acs-build-notes.md`, measured on the
  output), and `make_stac.py` passes the live count in so the description
  cannot drift from the file it describes.
- Vintages: ACS 2020–2024 5-year (`acsdt5y2024`, table-based Summary File)
  for the fourteen ACS collections, 2020 Census P.L. 94-171 for blocks.
- Geometry: 2024 cartographic boundary files for the ACS collections — the
  ZCTA collection excepted, which uses GENZ2020, the only cartographic ZCTA
  edition and the vintage the ACS tabulates — and TIGER/Line 2024
  `TABBLOCK20` for blocks (`docs/blocks-build-notes.md`).
- Known issues are quoted from the two build-notes files, which report what
  the validation pass counted.
- Universes and table titles come from `tools/column_docs.py`, which quotes
  the release's own table shells.

Every URL in a description is a markdown link, because these descriptions are
rendered as markdown by the Portolan data browser and by `portolan readme`.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import column_docs as cd  # noqa: E402
import specs  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"

EXTRACTED = "2026-11-12"          # the day every source file here was read
PUBLIC_BASE = "https://data.source.coop/portolan-mirrors/us-census-catalog"
REPO = "https://github.com/portolan-mirrors/us-census-catalog"
CONTACT_NAME = "Chris Holmes"
CONTACT_EMAIL = "cholmes@9eo.org"

# --------------------------------------------------------------------------
# Upstream URLs — the exact locations tools/download_sources.sh reads
# --------------------------------------------------------------------------

ACS_SF = ("https://www2.census.gov/programs-surveys/acs/summary_file/2024/"
          "table-based-SF")
ACS_5YR_DATA = f"{ACS_SF}/data/5YRData/"
CB_SHP = "https://www2.census.gov/geo/tiger/GENZ2024/shp"
CB_SHP_2020 = "https://www2.census.gov/geo/tiger/GENZ2020/shp"
TIGER_TABBLOCK = "https://www2.census.gov/geo/tiger/TIGER2024/TABBLOCK20/"
PL_DIR = ("https://www2.census.gov/programs-surveys/decennial/2020/data/"
          "01-Redistricting_File--PL_94-171/")
PL_IMPORT_SCRIPTS = (
    "https://www2.census.gov/programs-surveys/decennial/rdo/about/"
    "2020-census-program/Phase3/SupportMaterials/2020PL_R_import_scripts.zip")

DATA_CENSUS = "https://data.census.gov/"
ACS_PROGRAM = "https://www.census.gov/programs-surveys/acs.html"
ACS_HANDBOOK = ("https://www.census.gov/programs-surveys/acs/library/"
                "handbooks/general.html")
ACS_ACCURACY = cd.ACCURACY_URL
ACS_SUBJECT_DEFS = ("https://www2.census.gov/programs-surveys/acs/tech_docs/"
                    "subject_definitions/2024_ACSSubjectDefinitions.pdf")
PL_TECHDOC = cd.PL_TECHDOC_URL
PL_PROGRAM = ("https://www.census.gov/programs-surveys/decennial-census/"
              "about/rdo/summary-files.html")
GEO_GLOSSARY = ("https://www.census.gov/programs-surveys/geography/about/"
                "glossary.html")
CB_ABOUT = ("https://www.census.gov/geographies/mapping-files/time-series/"
            "geo/cartographic-boundary.html")
OPEN_DATA_POLICY = ("https://www.census.gov/about/policies/open-gov/"
                    "open-data.html")
A5 = "https://a5geo.org/"
TYLERTOO = "https://github.com/geoparquet-io/tylertoo"

# Wave-3 geography documentation. Each one is cited where a claim needs it:
# the ZCTA page for "a ZCTA is not a ZIP code", the ACS boundary-vintage page
# for "the 2024 release tabulates the 119th Congress", the tallies file for
# the published entity counts this build's row counts are checked against.
ZCTA_ABOUT = ("https://www.census.gov/programs-surveys/geography/guidance/"
              "geo-areas/zctas.html")
CDP_ABOUT = "https://www.census.gov/programs-surveys/bas/information/cdp.html"
ACS_BOUNDARY_VINTAGE = ("https://www.census.gov/programs-surveys/acs/"
                        "geography-acs/geography-boundaries-by-year/2024.html")
ACS_AREAS_PUBLISHED = ("https://www.census.gov/programs-surveys/acs/"
                       "geography-acs/areas-published.html")
CD_119 = ("https://www.census.gov/programs-surveys/decennial-census/about/"
          "rdo/congressional-districts.119th_Congress.html")
GEO_TALLIES = ("https://www.census.gov/geographies/reference-files/"
               "time-series/geo/tallies.html")
GEO_TALLIES_FILE = ("https://www2.census.gov/geo/docs/maps-data/data/"
                    "geo_tallies2020/Natl_Geographic_Tallies_2020.txt")
CONGRESS = 119

LICENSE = "CC0-1.0"
ATTRIBUTION = "U.S. Census Bureau"

# --------------------------------------------------------------------------
# The catalog's shape
# --------------------------------------------------------------------------

GROUPS = {
    "block-groups": ["bg-income", "bg-people", "bg-housing",
                     "bg-connectivity"],
    "tracts": ["tract-income", "tract-people", "tract-housing",
               "tract-connectivity", "tract-wellbeing"],
}
GROUP_OF = {cid: g for g, ids in GROUPS.items() for cid in ids}

# Collection id -> directory, relative to catalog/. Ungrouped collections sit
# at the catalog root, which is also their STAC id.
COLL_REL = dict(
    {cid: f"{g}/{cid}" for g, ids in GROUPS.items() for cid in ids},
    counties="counties", states="states", blocks="blocks",
    zctas="zctas", places="places",
    **{"congressional-districts": "congressional-districts"})

# The three wave-3 collections: coarse-or-sparse levels the ACS publishes the
# whole column set for, each a single wide table like counties and states.
WAVE3 = ["zctas", "places", "congressional-districts"]

ALL_COLLECTIONS = (GROUPS["block-groups"] + GROUPS["tracts"]
                   + ["counties", "states"] + WAVE3 + ["blocks"])

LEVEL_OF = dict(cd.LEVEL_OF)

# Feature counts as the build measured them (docs/acs-build-notes.md,
# docs/blocks-build-notes.md). `make_stac.py` overrides each with the count it
# reads out of the published file.
FEATURES = {
    "bg-income": 242298, "bg-people": 242298, "bg-housing": 242298,
    "bg-connectivity": 242298,
    "tract-income": 85184, "tract-people": 85184, "tract-housing": 85184,
    "tract-connectivity": 85184, "tract-wellbeing": 85184,
    "counties": 3235, "states": 56, "blocks": 8174955,
    "zctas": 33791, "places": 32612, "congressional-districts": 441,
}

ACS_INTERVAL = ["2020-01-01T00:00:00Z", "2024-12-31T23:59:59Z"]
BLOCKS_INTERVAL = ["2020-04-01T00:00:00Z", "2020-04-01T00:00:00Z"]

LEVEL_PLURAL = {
    "bg": "census block groups", "tract": "census tracts",
    "county": "counties and county equivalents",
    "state": "states and state equivalents",
    "block": "2020 census blocks",
    "zcta": "ZIP Code Tabulation Areas",
    "place": "incorporated places and census designated places",
    "cd": f"congressional districts of the {CONGRESS}th Congress",
}

# --------------------------------------------------------------------------
# Titles
# --------------------------------------------------------------------------

TITLES = {
    "bg-income": "Income & Poverty — Block Groups",
    "bg-people": "People & Education — Block Groups",
    "bg-housing": "Housing & Rent — Block Groups",
    "bg-connectivity": "Commuting & Connectivity — Block Groups",
    "tract-income": "Income & Poverty — Census Tracts",
    "tract-people": "People & Education — Census Tracts",
    "tract-housing": "Housing & Rent — Census Tracts",
    "tract-connectivity": "Commuting & Connectivity — Census Tracts",
    "tract-wellbeing": "Health, Disability & Income by Race — Census Tracts",
    "counties": "All Indicators — Counties",
    "states": "All Indicators — States",
    "zctas": "All Indicators — ZIP Code Tabulation Areas",
    "places": "All Indicators — Places & CDPs",
    "congressional-districts":
        f"All Indicators — Congressional Districts ({CONGRESS}th Congress)",
    "blocks": "2020 Census Counts — Blocks",
}

GROUP_TITLES = {
    "block-groups": "Block Groups",
    "tracts": "Census Tracts",
}

# --------------------------------------------------------------------------
# Keywords
# --------------------------------------------------------------------------

_KW_COMMON = ["census", "ACS", "American Community Survey", "demographics",
              "United States", "margins of error"]
_KW_THEME = {
    "income": ["income", "poverty", "SNAP", "unemployment", "equity"],
    "people": ["age", "race", "ethnicity", "education", "equity"],
    "housing": ["housing", "rent", "home values", "tenure", "vacancy",
                "affordability"],
    "connectivity": ["commuting", "transit", "vehicles", "internet access",
                     "digital divide"],
    "wellbeing": ["health insurance", "disability", "foreign-born",
                  "income by race", "group quarters", "equity"],
    "all": ["income", "poverty", "housing", "commuting", "internet access",
            "health insurance", "race", "education"],
}
_KW_LEVEL = {
    "bg": ["block groups"], "tract": ["census tracts"],
    "county": ["counties"], "state": ["states"], "block": ["census blocks"],
    # "ZIP codes" is in the ZCTA keyword list because it is what people
    # search for; the description and the known issues both say a ZCTA is
    # not a ZIP code.
    "zcta": ["ZCTA", "ZIP Code Tabulation Areas", "ZIP codes", "zip"],
    "place": ["places", "cities", "towns", "census designated places",
              "CDP", "municipalities"],
    "cd": ["congressional districts", f"{CONGRESS}th Congress",
           "redistricting", "politics"],
}


def theme_of(cid: str) -> str:
    if cid in ("counties", "states") or cid in WAVE3:
        return "all"
    if cid == "blocks":
        return "blocks"
    return cid.split("-", 1)[1]


def keywords(cid: str) -> list[str]:
    if cid == "blocks":
        return ["census", "2020 Census", "decennial census",
                "P.L. 94-171", "redistricting", "population", "race",
                "ethnicity", "voting age population", "housing occupancy",
                "group quarters", "United States", "census blocks"]
    kw = _KW_COMMON + _KW_THEME[theme_of(cid)] + _KW_LEVEL[LEVEL_OF[cid]]
    return list(dict.fromkeys(kw))


# --------------------------------------------------------------------------
# Descriptions
# --------------------------------------------------------------------------

def _t(table: str) -> str:
    return cd.acs_table(table)


# The lead paragraph of each theme: what the collection actually holds, with
# every indicator traced to its table. Universes are in the per-column
# descriptions; this names the measures.
THEME_LEAD = {
    "income": (
        "Income, poverty and employment: median household income and per "
        f"capita income ({_t('B19013')}, {_t('B19301')}), the share of "
        "people below the poverty line and below twice it "
        f"({_t('C17002')}), the share of households receiving SNAP "
        f"({_t('B22010')}), and the unemployment rate as a share of the "
        f"civilian labor force ({_t('B23025')}), plus total population "
        f"({_t('B01003')}) and population density for context."),
    "people": (
        "Who lives here: median age and the shares under 18 and 65 or over "
        f"({_t('B01002')}, {_t('B01001')}), the five mutually exclusive "
        "non-Hispanic race shares plus Hispanic or Latino of any race and "
        f"their complement, people of color ({_t('B03002')}), and the share "
        "of adults 25 and over holding a bachelor's degree or higher "
        f"({_t('B15003')})."),
    "housing": (
        "The housing stock and what it costs: total units and the vacancy "
        f"rate ({_t('B25002')}), households and the owner-occupied share "
        f"({_t('B25003')}), median gross rent ({_t('B25064')}) and median "
        f"owner-occupied home value ({_t('B25077')}), the share of renter "
        "households paying 30% and 50% or more of income on rent "
        f"({_t('B25070')}), the pre-1940 share ({_t('B25034')}) and the "
        f"single-family share ({_t('B25024')})."),
    "connectivity": (
        "How people get around and get online: households with no vehicle "
        f"available, as a count and a share ({_t('B25044')}); commute mode "
        "shares for driving alone, public transportation, walking or "
        f"cycling, and working from home ({_t('B08301')}); the share of "
        f"commutes of 45 minutes or more ({_t('B08303')}); and the shares "
        "of households with no internet access and no computing device "
        f"({_t('B28002')}, {_t('B28001')})."),
    "wellbeing": (
        "Health coverage, disability, nativity and income by race — the "
        "tables the Census Bureau does not publish for block groups, which "
        "is why this chunk has no block-group twin. The uninsured share and "
        f"the share with a disability ({_t('B27001')}, {_t('B18101')}), the "
        f"foreign-born share ({_t('B05002')}), the group-quarters population "
        f"({_t('B26001')}), median household income for Black, "
        "non-Hispanic White, Asian and Hispanic householders "
        f"({_t('B19013B')}, {_t('B19013H')}, {_t('B19013D')}, "
        f"{_t('B19013I')}), and the poverty rate of the Black alone "
        f"population ({_t('B17020B')})."),
    "all": (
        "Every indicator in this catalog's ACS column set, in one table: "
        "income and poverty, age and race and education, housing cost and "
        "tenure, vehicles and commuting and internet access, health "
        "insurance and disability and nativity, and median household income "
        "by race and ethnicity. The block-group and tract levels split these "
        "into themed chunks because a national block-group file is large; at "
        "this size width costs nothing, so nothing is split."),
}

# A sentence or two per collection about its own sharpest edge, from the
# build notes' NULL-rate table and known issues.
THEME_CAVEAT = {
    "bg-housing": (
        "One number to know before mapping this at block-group scale: "
        "`median_gross_rent` is NULL for **29.68%** of block groups and "
        "`median_home_value` for **10.03%**, because a block group with few "
        "renter or owner households has no publishable median. The tract "
        "collection's rates are 5.92% and 3.55%."),
    "bg-income": (
        "`median_hh_income` is NULL for **7.69%** of block groups — the "
        "Census Bureau suppresses a median when the sample behind it is too "
        "thin, which at this scale is often. The tract rate is 1.59%."),
    "tract-wellbeing": (
        "The four race-iteration medians are sparse by construction: "
        "`median_hh_income_asian` is NULL for **71.27%** of tracts, "
        "`median_hh_income_black` for **61.43%**, "
        "`median_hh_income_hispanic` for **44.43%** and "
        "`median_hh_income_white_nh` for **10.04%**, wherever that group has "
        "too few households in the tract for a published median. A map of "
        "one of these columns is as much a map of where the group lives as "
        "of its income."),
    "zctas": (
        f"Two things to know before mapping this. A ZIP Code Tabulation Area "
        f"[is not a ZIP code]({ZCTA_ABOUT}) — it is the Census Bureau's "
        f"block-built approximation of a USPS 5-digit delivery area — and it "
        f"nests in nothing, so `state` is NULL on every row and there is no "
        f"prefix join to counties or tracts. And the medians thin out: "
        f"`median_gross_rent` is NULL for **23.79%** of ZCTAs, "
        f"`median_home_value` for **10.45%** and `median_hh_income` for "
        f"**9.60%**, because a ZCTA with few renter, owner or total "
        f"households has no publishable median."),
    "places": (
        f"Most of the 32,612 rows are small: the file holds every "
        f"incorporated place and every "
        f"[census designated place]({CDP_ABOUT}) the Census Bureau "
        f"delineates, from New York city to villages of 40 people, and the "
        f"suppression rates follow — `median_gross_rent` is NULL for "
        f"**31.32%** of places, `median_home_value` for **12.78%** and "
        f"`median_hh_income` for **12.71%**. Filter on `population` before "
        f"drawing conclusions from a place-level distribution. A place is "
        f"also not a partition of the country: the land between places is "
        f"not in this file at all, so place rows do not sum to a state."),
    "congressional-districts": (
        f"Districts are equal-population by construction — roughly 770,000 "
        f"people each, 546,488 to 1,021,191 in this file — so the "
        f"distribution of every rate here is far tighter than at any other "
        f"geography, and the map styles' class breaks are measured "
        f"accordingly. These are the districts of the **{CONGRESS}th "
        f"Congress** ([the vintage this ACS release tabulates]"
        f"({ACS_BOUNDARY_VINTAGE})); district numbers are not stable across "
        f"congresses, so do not join these GEOIDs to an earlier congress's "
        f"districts of the same number."),
}

STATS_PARA = (
    "Every estimate ships with its margin of error — `<column>_moe`, at the "
    "90% confidence level, the level the Census Bureau publishes — and the "
    "headline statistics also carry a coefficient of variation "
    "(`<column>_cv` = `moe / 1.645 / estimate`) so small-area noise can be "
    "flagged rather than mapped as if certain. Derived percentages propagate "
    "error with the Census Bureau's own formulas from "
    f"[ACS Accuracy of the Data]({ACS_ACCURACY}): sums add in quadrature, "
    "proportions use the subset formula with the ratio formula as fallback. "
    "ACS jam values for suppressed or unestimable cells are NULL here, never "
    "numbers, and medians are published as the Bureau publishes them — a "
    "median cannot be aggregated to a larger area. Each column's description "
    "names its ACS table, its exact universe, and the lines summed to make "
    "it.")

TILES_PARA = (
    "The PMTiles archive carries the same columns as the GeoParquet. At "
    f"feature zooms the tiles are the census geographies; at coarse zooms "
    f"they are [A5]({A5}) cell aggregations built by "
    f"[tylertoo]({TYLERTOO}) — counts summed, rates and medians averaged "
    "unweighted over the geographies in the cell — because thinning "
    "hundreds of thousands of polygons at a national zoom would show a "
    "biased subset (small urban geographies drop first) rather than less "
    "data. Cell and feature zooms share column names, so one style "
    "expression classifies both. The aggregation is a visualization aid: "
    "statistics come from the GeoParquet, never from the tiles.")

# The collections whose PMTiles carry real polygons at every zoom, with no A5
# aggregation at all: few enough features that nothing has to be aggregated
# (counties `--band 0-10:geom`, states `0-8:geom`, congressional districts
# `0-10:geom` — see staging/tiles-logs/ and tools/make_tiles.py). Saying "the
# coarse zooms are A5 cells" of these would be false.
GEOM_ONLY_TILES = {"counties", "states", "congressional-districts"}

GEOM_TILES_PARA = (
    "The PMTiles archive carries the same columns as the GeoParquet, minus "
    "the `*_moe` columns, and at every zoom the tiles are the real census "
    f"geographies — no [A5]({A5}) cell aggregation, unlike the catalog's "
    f"finer collections, because there are few enough features here to draw "
    f"them all at a national zoom. Built with [tylertoo]({TYLERTOO}). "
    f"Statistics still come from the GeoParquet: margins of error are not in "
    f"the tiles.")


def tiles_para(cid: str) -> str:
    return GEOM_TILES_PARA if cid in GEOM_ONLY_TILES else TILES_PARA


def _geom_para(level: str) -> str:
    noun = LEVEL_PLURAL[level]
    year = cd.CB_VINTAGE[level]
    text = (
        f"Geometries are the Census Bureau's "
        f"[{year} cartographic boundary files]({CB_ABOUT}) for {noun} "
        f"(GENZ{year}, 1:500,000), reprojected to EPSG:4326 and joined on "
        f"`GEOID`. Cartographic rather than TIGER/Line because TIGER extends "
        f"census geographies into open water while the cartographic files "
        f"clip to the shoreline, which is what a choropleth wants. ")
    if level == "zcta":
        text += (
            f"GENZ2020 and not GENZ2024 because no cartographic ZCTA file "
            f"has been published since: the 2020-based ZCTAs are the current "
            f"ones, and they are the vintage this release tabulates "
            f"([ACS geography boundaries by year]"
            f"({ACS_BOUNDARY_VINTAGE}) gives 5-digit ZCTA as \"2020 "
            f"Census\"). The ZCTA file is also the one boundary file in this "
            f"catalog with no state attribute, which is why `state` is NULL "
            f"here.")
    elif level == "cd":
        text += (
            f"The file is `cb_2024_us_cd{CONGRESS}_500k` — "
            f"`CDSESSN = '{CONGRESS}'` on all 441 features — matching the "
            f"congress this release tabulates.")
    else:
        text += "The boundary vintage matches the estimate vintage."
    return text


def _gap_para(level: str) -> str:
    """The rows with geometry but no data, counted by the build."""
    counts = {
        "bg": ("405 block groups", "39 block groups"),
        "tract": ("126 tracts", "14 tracts"),
        "county": ("13 county equivalents", None),
        "state": ("4 rows (American Samoa, Guam, the Northern Mariana "
                  "Islands, the U.S. Virgin Islands)", None),
        "zcta": ("17 ZCTAs", "Two more, 11717 and 11798,"),
        "place": ("279 places (MP 135, AS 77, GU 57, VI 10)",
                  "Two more, Brentwood CDP and Wyandanch CDP,"),
        "cd": ("4 delegate districts (American Samoa, Guam, the Northern "
               "Mariana Islands, the U.S. Virgin Islands)", None),
    }[level]
    text = (
        f"The join is driven by geometry, so a geography with "
        f"{cd.CB_VINTAGE[level]} boundaries but no ACS tabulation keeps its "
        f"row with NULL values instead of disappearing: {counts[0]} in the "
        f"island areas, which have cartographic boundaries but no ACS 5-year "
        f"estimates because the Island Areas run a separate decennial-only "
        f"program.")
    if counts[1] and level in ("bg", "tract"):
        text += (f" Suffolk County, New York was re-delineated in the 2024 "
                 f"vintage, which adds {counts[1]} with boundaries and no "
                 f"matching ACS row. ")
    elif counts[1]:
        # No causal claim here: what was measured is that these rows have a
        # polygon and no ACS row, and that they sit in Suffolk County, New
        # York (checked by intersecting them with the county file).
        text += (f" {counts[1]} have boundaries and no matching ACS row, "
                 f"both in Suffolk County, New York — the county "
                 f"whose 2024 re-delineation also leaves 14 tracts and 39 "
                 f"block groups without ACS rows elsewhere in this "
                 f"catalog. ")
    else:
        text += " "
    if level == "place":
        text += (
            "One more: `2148000` Louisville city, Kentucky, which the "
            "boundary file still carries and the ACS tabulates as the "
            "consolidated `2148006` Louisville/Jefferson County metro "
            "government (balance) instead — so the Louisville you want is "
            "`2148006`. ")
    if level == "cd":
        text += (
            "In the other direction, three ACS district rows have no polygon "
            "and so no row here: `09ZZ`, `17ZZ` and `33ZZ`, the water-only "
            "pseudo-districts Connecticut, Illinois and New Hampshire "
            "contribute to the tabulation, each with population 0. ")
    if level == "zcta":
        text += (
            "No ACS ZCTA row is dropped in the other direction: all 33,772 "
            "tabulated ZCTAs have a polygon. ")
    text += ("Keeping these rows means a national map has no holes and a "
             "consumer can see the absence; dropping them would make "
             "\"every US geography\" quietly mean something narrower.")
    return text


def _siblings_para(cid: str) -> str:
    level = LEVEL_OF[cid]
    group = GROUP_OF.get(cid)
    if group:
        others = [c for c in GROUPS[group] if c != cid]
        names = [f"[{TITLES[c].split(' — ')[0]}](../{c}/collection.json)"
                 for c in others]
        links = ", ".join(names[:-1]) + f" and {names[-1]}"
        return (
            f"This is one themed chunk of {len(GROUPS[group])} at this "
            f"geography — the others are {links} — split that way because a "
            f"single wide national table would make a consumer who wanted "
            f"one column download all of them. Collections at the same "
            f"geography join 1:1 on `geoid`. The same indicators are "
            f"published for "
            f"[counties](../../counties/collection.json) and "
            f"[states](../../states/collection.json) as single wide tables.")
    if cid in ("counties", "states"):
        return (
            "Finer geographies are published as themed chunks: "
            "[block groups](../block-groups/catalog.json) carry income, "
            "people, housing and connectivity, and "
            "[census tracts](../tracts/catalog.json) add a wellbeing chunk. "
            "GEOIDs nest by prefix, so `substr(geoid, 1, 5)` on a tract row "
            "is its county and `substr(geoid, 1, 2)` its state. The same "
            "wide column set is also published for "
            "[ZCTAs](../zctas/collection.json), "
            "[places](../places/collection.json) and "
            "[congressional districts]"
            "(../congressional-districts/collection.json).")
    if cid in WAVE3:
        nests = {
            "zctas": (
                "A ZCTA nests in nothing: it can cross county and state "
                "lines, so there is no prefix join from `geoid` to any other "
                "collection here, and `state` is NULL. Relating ZCTAs to "
                "counties or tracts is a spatial operation (or a Census "
                "relationship file), not a string operation."),
            "places": (
                "A place nests in a state but not in a county — a place can "
                "straddle a county line — so `substr(geoid, 1, 2)` joins "
                "[states](../states/collection.json) and nothing else joins "
                "by prefix."),
            "congressional-districts": (
                "A district nests in a state, so `substr(geoid, 1, 2)` joins "
                "[states](../states/collection.json); nothing finer joins by "
                "prefix, because district boundaries follow 2020 census "
                "blocks rather than counties or tracts."),
        }[cid]
        siblings = ", ".join(
            f"[{TITLES[c].split(' — ')[1]}](../{c}/collection.json)"
            for c in ("counties", "states") + tuple(
                w for w in WAVE3 if w != cid))
        return (
            f"{nests} The same 112-column wide table is published at the "
            f"catalog's other coarse geographies — {siblings} — and the finer "
            f"geographies split the indicators into themed chunks: "
            f"[block groups](../block-groups/catalog.json) and "
            f"[census tracts](../tracts/catalog.json).")
    return ""


def _mirror_para(cid: str) -> str:
    agents = "[AGENTS.md](AGENTS.md)"
    return (
        f"This is a mirror — [data.census.gov]({DATA_CENSUS}) is "
        f"authoritative, and nothing here is an official Census Bureau "
        f"product. The exact upstream files this collection was built from "
        f"are published as `source` assets, linked at their original "
        f"census.gov URLs, so the original is always one click away; the "
        f"Bureau's own documentation is linked alongside them. Read the "
        f"collection's {agents} before querying: it carries the schema, the "
        f"join keys, the NULL-rate story and tested queries against the "
        f"published URLs.")


def description(cid: str, features: int | None = None) -> str:
    """Full STAC description for a collection, as markdown."""
    n = features if features is not None else FEATURES[cid]
    level = LEVEL_OF[cid]
    if cid == "blocks":
        return _blocks_description(n)

    noun = LEVEL_PLURAL[level]
    # Island-area rows are published with NULL estimates at every level, so
    # they belong in the count at every level. _gap_para says how many.
    where = "the United States, Puerto Rico and the island areas"
    # Which ACS releases reach this geography, from the Bureau's own
    # "Areas Published" table.
    release = {
        "bg": "The 5-year file is the only ACS release published at this "
              "geography: 1-year estimates stop well above it.",
        "tract": "The 5-year file is the only ACS release published at this "
                 "geography: 1-year estimates stop well above it.",
        "zcta": f"The 5-year file is the only ACS release published for "
                f"ZCTAs at all — [areas published]"
                f"({ACS_AREAS_PUBLISHED}) lists the 5-digit ZCTA under the "
                f"5-year estimates and nowhere else.",
        "place": f"The Bureau publishes 1-year estimates only for places of "
                 f"65,000 people or more, so the 5-year release is the only "
                 f"one that covers all {n:,} of them ([areas published]"
                 f"({ACS_AREAS_PUBLISHED})).",
    }.get(level,
          "The Bureau also publishes 1-year estimates at this geography; "
          "the 5-year release is used throughout this catalog so every "
          "geography in it is the same vintage and directly comparable.")
    paras = [
        f"{THEME_LEAD[theme_of(cid)]}\n\n"
        f"Curated indicators for all **{n:,}** {noun} in {where}, from the "
        f"U.S. Census Bureau's [American Community Survey]({ACS_PROGRAM}) "
        f"**2020–2024 5-year estimates** (`acsdt5y2024`, the table-based "
        f"[Summary File]({ACS_5YR_DATA})). The Census Bureau calls the ACS "
        f"\"the premier source of detailed information about the nation's "
        f"people and housing\". " + release,
        STATS_PARA,
    ]
    if cid in THEME_CAVEAT:
        paras.append(THEME_CAVEAT[cid])
    paras += [
        _geom_para(level),
        _gap_para(level),
        _siblings_para(cid),
        tiles_para(cid),
        _mirror_para(cid),
    ]
    return "\n\n".join(p for p in paras if p)


def _blocks_description(n: int) -> str:
    return "\n\n".join([
        f"2020 Decennial Census counts for all **{n:,}** census blocks in "
        f"the 50 states, the District of Columbia and Puerto Rico — the "
        f"smallest geography the Census Bureau publishes anything for. From "
        f"the [2020 Census P.L. 94-171 Redistricting Data Summary Files]"
        f"({PL_PROGRAM}): total population and the seven race-alone counts "
        f"plus two or more races ({cd.pl_table('P1')}), Hispanic or Latino "
        f"and White-alone-not-Hispanic ({cd.pl_table('P2')}), the "
        f"voting-age population 18 and over ({cd.pl_table('P3')}), housing "
        f"units occupied and vacant ({cd.pl_table('H1')}), and the "
        f"group-quarters population ({cd.pl_table('P5')}), with derived "
        f"shares and population density.",

        "These are **complete counts, not survey estimates**, so there are "
        "no margins of error and no coefficients of variation — the `*_moe` "
        "and `*_cv` columns the ACS collections carry do not exist here. "
        "They are, however, protected by the 2020 disclosure-avoidance "
        "system, which injects noise at block level while holding state "
        "totals exact: block counts are reliable in aggregate and should be "
        "read with care one block at a time. The Census Bureau publishes no "
        "income, education or commuting data at block level — for that, "
        "move up to the "
        "[block-group collections](../block-groups/catalog.json).",

        "Roughly three in ten census blocks are unpopulated by design "
        "(28.97% have `pop_total = 0`, measured), so `pct_white_nh`, "
        "`pct_black` and `pct_hispanic` are NULL on that share of rows, and "
        "`pct_vacant` is NULL on the 27.64% with no housing units. That is a "
        "property of census blocks, not missing data: filter "
        "`pop_total > 0` before averaging a rate. Summed over the 50 states "
        "and DC, `pop_total` equals 331,449,281 — the published 2020 "
        "resident population, exactly; Puerto Rico equals 3,285,874.",

        f"Geometry is [TIGER/Line 2024 `TABBLOCK20`]({TIGER_TABBLOCK}), not "
        f"the cartographic boundary files the ACS collections use, because "
        f"no cartographic edition is published for blocks. TIGER is "
        f"unclipped, so a coastal block extends to the 3-mile limit rather "
        f"than the shoreline, and `aland_sqkm` comes from the file's own "
        f"`ALAND20` land-area field (water-only blocks have `ALAND20 = 0` "
        f"and so a NULL `pop_density`). Field positions in the P.L. 94-171 "
        f"files are pinned against the Census Bureau's own "
        f"[R import scripts]({PL_IMPORT_SCRIPTS}) rather than read off a "
        f"PDF — see the build notes in the repository for the field table "
        f"and the three independent checks behind it.",

        "The collection is **hive-partitioned by state**: 52 parquet files "
        "under `state_fips=<FIPS>/`, one STAC item each with its own bbox "
        "and row count, queryable as one table through the glob "
        "`state_fips=*/*.parquet` with `hive_partitioning=true`. The "
        "synthesized `state_fips` key carries the numeric FIPS code and sits "
        "alongside the `state` column's USPS code. Pull one state and you "
        "download one file.",

        tiles_para("blocks"),
        _mirror_para("blocks"),
    ])


# --------------------------------------------------------------------------
# Sub-catalog and root prose
# --------------------------------------------------------------------------

GROUP_DESCRIPTIONS = {
    "block-groups": (
        "American Community Survey 2020–2024 5-year indicators for all "
        "242,298 census block groups in the United States and Puerto Rico — "
        "the finest geography the Census Bureau publishes income, housing "
        "cost and commuting data for, typically 600–3,000 people. The "
        "indicators are split into four themed collections — "
        "[income](./bg-income/collection.json), "
        "[people](./bg-people/collection.json), "
        "[housing](./bg-housing/collection.json) and "
        "[connectivity](./bg-connectivity/collection.json) — because one "
        "wide national table would make a consumer who wanted median income "
        "download sixty columns and 242,298 rows. All four share the same "
        "geometry and `geoid`, so they join 1:1. Health insurance, "
        "disability, nativity and income by race are not published at this "
        f"geography; they are in [tracts](../tracts/catalog.json). Every "
        f"estimate carries its margin of error, and block-group margins are "
        f"wide — read each collection's `*_cv` columns and its AGENTS.md "
        f"before mapping. [data.census.gov]({DATA_CENSUS}) is "
        f"authoritative."),
    "tracts": (
        "American Community Survey 2020–2024 5-year indicators for all "
        "85,184 census tracts in the United States and Puerto Rico — "
        "typically 1,200–8,000 people, the geography most small-area social "
        "research is done at. The same four themed collections as block "
        "groups — [income](./tract-income/collection.json), "
        "[people](./tract-people/collection.json), "
        "[housing](./tract-housing/collection.json), "
        "[connectivity](./tract-connectivity/collection.json) — plus "
        "[wellbeing](./tract-wellbeing/collection.json), which carries the "
        "health-insurance, disability, nativity and income-by-race tables "
        "the Census Bureau does not publish for block groups. All five share "
        "the same geometry and `geoid` and join 1:1; tract margins of error "
        "are substantially narrower than block-group margins (median "
        "household income is NULL on 1.59% of tracts against 7.69% of block "
        f"groups). [data.census.gov]({DATA_CENSUS}) is authoritative."),
}

# --------------------------------------------------------------------------
# Source assets
# --------------------------------------------------------------------------

# level -> the cartographic boundary zip this build downloaded, as a full
# URL. ZCTAs come from GENZ2020 (the only edition) and congressional
# districts carry the congress number in the name.
CB_LEVEL_URL = {
    "bg": f"{CB_SHP}/cb_2024_us_bg_500k.zip",
    "tract": f"{CB_SHP}/cb_2024_us_tract_500k.zip",
    "county": f"{CB_SHP}/cb_2024_us_county_500k.zip",
    "state": f"{CB_SHP}/cb_2024_us_state_500k.zip",
    "zcta": f"{CB_SHP_2020}/cb_2020_us_zcta520_500k.zip",
    "place": f"{CB_SHP}/cb_2024_us_place_500k.zip",
    "cd": f"{CB_SHP}/cb_2024_us_cd{CONGRESS}_500k.zip",
}


def tables_for(cid: str) -> list[str]:
    """ACS tables a collection reads, in table-id order."""
    if cid == "blocks":
        return []
    coll = next(c for c in specs.COLLECTIONS if c.id == cid)
    return sorted({s.table for s in specs.CONTEXT_SPEC + list(coll.spec)})


def _dat_asset(table: str) -> tuple[str, dict]:
    title, universe = cd.TABLE_UNIVERSE[table]
    key = f"source-{table.lower()}"
    return key, {
        "href": f"{ACS_5YR_DATA}acsdt5y2024-{table.lower()}.dat",
        "type": "text/plain",
        "title": f"ACS 2020–2024 detailed table {table} — {title}",
        "description": (
            f"The upstream file this collection's {table} columns were read "
            f"from: one pipe-delimited row per geography, estimate "
            f"(`{table}_E###`) and margin of error (`{table}_M###`) side by "
            f"side, for every summary level in one national file. Universe: "
            f"{universe}. Served by census.gov, not by this mirror; see "
            f"{cd.acs_table(table)} for the same table rendered on "
            f"data.census.gov."),
        "roles": ["source"],
    }


def source_assets(cid: str) -> dict:
    """Upstream `source` assets plus `metadata` documentation assets.

    `source` and not `data`: a client filtering on `data` should land on this
    catalog's GeoParquet, and the role also says these bytes live on a server
    this mirror does not control.
    """
    out: dict[str, dict] = {}
    level = LEVEL_OF[cid]
    if cid == "blocks":
        out["source-pl94171"] = {
            "href": PL_DIR,
            "type": "text/html",
            "title": "2020 Census P.L. 94-171 Redistricting Data Summary "
                     "Files — state directories",
            "description": (
                "The 52 state archives (`{State_Name}/{ab}2020.pl.zip`) this "
                "collection's counts were read from, 2020 Census P.L. 94-171 "
                "redistricting data. Each archive holds a pipe-delimited "
                "geoheader plus three segment files joined on `LOGRECNO`; "
                "block records are `SUMLEV = '750'`. Served by census.gov."),
            "roles": ["source"],
        }
        out["source-tiger-tabblock20"] = {
            "href": TIGER_TABBLOCK,
            "type": "text/html",
            "title": "TIGER/Line 2024 TABBLOCK20 — 2020 census block "
                     "shapefiles by state",
            "description": (
                "The block geometry: `tl_2024_{fips}_tabblock20.zip` per "
                "state, from which only `GEOID20` and `ALAND20` are kept. "
                "Unclipped, EPSG:4269 upstream, reprojected to EPSG:4326 "
                "with ogr2ogr. Served by census.gov."),
            "roles": ["source"],
        }
        out["source-pl-import-scripts"] = {
            "href": PL_IMPORT_SCRIPTS,
            "type": "application/zip",
            "title": "2020 P.L. 94-171 R import scripts (field layout)",
            "description": (
                "The Census Bureau's own machine-readable field dictionary "
                "for the P.L. 94-171 files. Every field position this build "
                "reads is pinned against the `colnames()` assignments in "
                "`R Versions/pl_part{1,2,3}_2020_dar.r` and "
                "`pl_geohd_2020_dar.r` — the citable layout source, rather "
                f"than the technical-documentation PDF. Downloaded "
                f"{EXTRACTED}."),
            "roles": ["source"],
        }
        out["doc-pl94171-techdoc"] = {
            "href": PL_TECHDOC,
            "type": "application/pdf",
            "title": "2020 Census P.L. 94-171 Redistricting Data Summary "
                     "File — technical documentation",
            "description": "Table shells, universes, file layout and the "
                           "disclosure-avoidance description for the 2020 "
                           "redistricting files.",
            "roles": ["metadata"],
        }
        out["doc-geo-glossary"] = _glossary_asset()
        return out

    for table in tables_for(cid):
        key, asset = _dat_asset(table)
        out[key] = asset
    out["source-table-shells"] = {
        "href": cd.SHELLS_URL,
        "type": "text/plain",
        "title": "ACS 2020–2024 5-year table shells",
        "description": (
            "`Table ID|Line|Indent|Unique ID|Label|Title|Universe|Type` for "
            "every table in the release. Two jobs here: every line number "
            "the build reads is pinned against this file and a vintage that "
            "renumbers a line fails the build, and every universe quoted in "
            "the column descriptions is this file's own `Universe` field. "
            "Served by census.gov."),
        "roles": ["source"],
    }
    year = cd.CB_VINTAGE[level]
    out["source-cartographic-boundaries"] = {
        "href": CB_LEVEL_URL[level],
        "type": "application/zip",
        "title": f"{year} cartographic boundary file — "
                 f"{LEVEL_PLURAL[level]} (1:500,000, national)",
        "description": (
            f"The geometry this collection joins onto, shoreline-clipped and "
            f"generalized for mapping. Only the join key, the name parts and "
            f"the land-area field are kept; reprojected from NAD83 to "
            f"EPSG:4326 with ogr2ogr."
            + (" GENZ2020 is the only cartographic ZCTA edition the Census "
               "Bureau publishes, and the 2020-based ZCTAs are the vintage "
               "this ACS release tabulates; its fields are suffixed with the "
               "vintage (`GEOID20`, `ZCTA5CE20`, `ALAND20`) and carry no "
               "state, which is why `state` is NULL in this collection."
               if level == "zcta" else
               f" `CDSESSN = '{CONGRESS}'` on every feature, matching the "
               f"congress this ACS release tabulates."
               if level == "cd" else "")
            + " Served by census.gov."),
        "roles": ["source"],
    }
    if level in ("zcta", "place", "cd"):
        out["doc-geo-tallies"] = {
            "href": GEO_TALLIES_FILE,
            "type": "text/plain",
            "title": "2020 Census national geographic entity tallies",
            "description": (
                f"The published count of every geographic entity type, which "
                f"this collection's row count is checked against: 33,791 "
                f"ZCTAs (33,642 US + 132 Puerto Rico + 17 island areas), "
                f"19,734 incorporated places and 12,454 census designated "
                f"places, 441 congressional districts (436 US including the "
                f"DC delegate + 1 Puerto Rico + 4 island areas). Index page: "
                f"{GEO_TALLIES}."),
            "roles": ["metadata"],
        }
    if level == "zcta":
        out["doc-zcta-about"] = {
            "href": ZCTA_ABOUT,
            "type": "text/html",
            "title": "ZIP Code Tabulation Areas (ZCTAs) — Census Bureau",
            "description": (
                "What a ZCTA is and, more importantly, what it is not: the "
                "Bureau's own page on how ZCTAs are built from census blocks "
                "to approximate USPS 5-digit ZIP delivery areas, why they do "
                "not match ZIP codes, and why they do not nest in any other "
                "census geography."),
            "roles": ["metadata"],
        }
    if level == "place":
        out["doc-cdp-about"] = {
            "href": CDP_ABOUT,
            "type": "text/html",
            "title": "Census Designated Places (CDPs) — Census Bureau",
            "description": (
                "How the Bureau delineates the unincorporated communities "
                "that make up roughly two fifths of the rows here, and how a "
                "CDP differs from an incorporated place."),
            "roles": ["metadata"],
        }
    if level == "cd":
        out["doc-cd119"] = {
            "href": CD_119,
            "type": "text/html",
            "title": f"Congressional Districts of the {CONGRESS}th Congress "
                     f"— Census Bureau",
            "description": (
                f"The Bureau's page for the district plans this collection "
                f"maps. The vintage is confirmed by "
                f"{ACS_BOUNDARY_VINTAGE}, which lists \"Congressional "
                f"District, Delegate District DC, Resident Commissioner "
                f"District PR\" with a vintage of \"{CONGRESS}th Congress of "
                f"the United States\" for the 2024 ACS."),
            "roles": ["metadata"],
        }
    out["doc-acs-handbook"] = {
        "href": ACS_HANDBOOK,
        "type": "text/html",
        "title": "Understanding and Using American Community Survey Data — "
                 "Census Bureau handbooks",
        "description": (
            "The Bureau's own guidance on what ACS estimates can and cannot "
            "support: 1-year versus 5-year releases, margins of error, "
            "comparing across vintages, and small-area reliability. Read it "
            "before drawing a conclusion from a single block group."),
        "roles": ["metadata"],
    }
    out["doc-acs-accuracy"] = {
        "href": ACS_ACCURACY,
        "type": "application/pdf",
        "title": "ACS Accuracy of the Data (2024, multiyear estimates)",
        "description": (
            "The source of every margin-of-error formula this build applies: "
            "quadrature for sums, the proportion formula and its ratio "
            "fallback for percentages, and the definition of the published "
            "90% confidence level."),
        "roles": ["metadata"],
    }
    out["doc-acs-subject-definitions"] = {
        "href": ACS_SUBJECT_DEFS,
        "type": "application/pdf",
        "title": "ACS 2024 Subject Definitions",
        "description": (
            "The Census Bureau's definitions of the concepts behind these "
            "columns — household, householder, gross rent, poverty status "
            "determined, group quarters, means of transportation to work, "
            "disability. Where a column description here says what a "
            "universe is, this is the document it is saying it from."),
        "roles": ["metadata"],
    }
    out["doc-geo-glossary"] = _glossary_asset()
    return out


def _glossary_asset() -> dict:
    return {
        "href": GEO_GLOSSARY,
        "type": "text/html",
        "title": "Census Bureau geography program glossary",
        "description": (
            "Definitions of the geographies and the identifiers used here — "
            "block, block group, tract, county equivalent, GEOID, and what "
            "nests inside what."),
        "roles": ["metadata"],
    }


# --------------------------------------------------------------------------
# .portolan/metadata.yaml
# --------------------------------------------------------------------------

PROCESSING_COMMON = (
    "Converted to GeoParquet with geoparquet-io (gpio): ZSTD compression, "
    "Hilbert row order, and a covering `bbox` column with row-group "
    "statistics, so a spatial filter can skip most of the file over the "
    "network. Tiled to PMTiles with tylertoo, with A5 cell aggregation at "
    "coarse zooms (counts summed, rates averaged) — a visualization aid, not "
    "a statistical product.")


def processing_notes(cid: str) -> str:
    if cid == "blocks":
        return "\n\n".join([
            f"Built {EXTRACTED} from two sets of Census Bureau files, "
            f"downloaded the same day: the 2020 P.L. 94-171 redistricting "
            f"archives ({PL_DIR}) for the counts, and TIGER/Line 2024 "
            f"TABBLOCK20 shapefiles ({TIGER_TABBLOCK}) for the geometry. "
            f"52 states (50 + DC + PR), 104 archives, 7.4 GB.",

            "Per state: ogr2ogr converts the shapefile to EPSG:4326 parquet "
            "keeping only `GEOID20` and `ALAND20`; DuckDB joins the four "
            "pipe-delimited P.L. files on `LOGRECNO`, filters "
            "`SUMLEV = '750'`, joins to the geometry on "
            "`GEOID20 = GEOCODE`, and derives the shares and density; "
            "`gpio sort hilbert --add-bbox` writes the final partition. "
            "Field positions are pinned against the Census Bureau's own R "
            "import scripts, field counts are re-checked per state and abort "
            "on a mismatch, and the geoheader is read as Latin-1 (it carries "
            "ISO-8859-1 place names; a UTF-8 read fails on Arizona).",

            "Validated: `pop_total` over the 50 states + DC equals the "
            "published 331,449,281 exactly and Puerto Rico 3,285,874; "
            "`housing_occupied + housing_vacant == housing_units` on every "
            "block; GEOIDs unique across all 52 partitions; zero orphans in "
            "either direction between TIGER and the P.L. files; one schema "
            "across all partitions.",

            PROCESSING_COMMON,
        ])

    level = LEVEL_OF[cid]
    tables = ", ".join(tables_for(cid))
    return "\n\n".join([
        f"Built {EXTRACTED} from the ACS 2020–2024 5-year table-based "
        f"Summary File ({ACS_5YR_DATA}), downloaded the same day over plain "
        f"HTTPS — the summary file needs no API key. Tables read for this "
        f"collection: {tables}. Each national `.dat` file is one row per "
        f"geography with estimate and margin of error side by side, and "
        f"every summary level is picked off `GEO_ID` by prefix in a single "
        f"pass per file — this collection's is `{specs.LEVELS[level]}`, read "
        f"off the files themselves rather than taken from a summary-level "
        f"table"
        + (f" (the `19` is the congress number)" if level == "cd" else
           f" (the `Z2` is the 2020 ZCTA vintage)" if level == "zcta" else "")
        + ".",

        "Jam values (the sentinels the ACS publishes in place of "
        "unestimable values, e.g. -666666666 for an uncomputable median, and "
        "-555555555 for a controlled MOE) become NULL: any estimate or "
        "margin at or below -111111111 is dropped rather than published as a "
        "number. Counts are sums of the specified lines with margins added "
        "in quadrature; percentages use the Census Bureau's proportion "
        "formula with the ratio formula as fallback; medians are passed "
        "through untouched; coefficients of variation are "
        "`moe / 1.645 / estimate` on the headline columns. Every line number "
        "is pinned against the release's own table shells before the build "
        "starts (44 pins verified, 0 failures, plus 4 derived line groups "
        "resolved from the shells), so a vintage bump that moves a line "
        "fails loudly instead of publishing a mislabeled column.",

        f"Geometry is the {cd.CB_VINTAGE[level]} cartographic boundary file "
        f"({Path(CB_LEVEL_URL[level]).name}) for "
        f"{LEVEL_PLURAL[level]} (1:500,000), reprojected to EPSG:4326 with "
        f"ogr2ogr — not DuckDB's `ST_Transform`, which computes correct "
        f"coordinates but stamps the source CRS into the GeoParquet "
        f"metadata. Geometry drives the join, so a geography with boundaries "
        f"but no ACS tabulation keeps its row with NULL values.",

        "Cross-checked end to end against the published St. Louis census "
        "catalog, which runs the same formulas on the same vintage: 314 of "
        "314 block groups joined, 0 mismatches on median household income, "
        "its margin of error, the poverty rate and its margin of error — "
        "exact equality, not approximate.",

        _wave3_validation(cid),

        PROCESSING_COMMON,
    ])


def _wave3_validation(cid: str) -> str:
    """What the validation pass counted for a wave-3 collection."""
    return {
        "zctas": (
            f"Validated: 33,791 rows against the 33,791 ZCTAs in the Census "
            f"Bureau's own [2020 geographic entity tallies]({GEO_TALLIES}) "
            f"(33,642 US + 132 Puerto Rico + 17 island areas), 33,791 "
            f"distinct `geoid`, no percentage outside 0–100, every one of "
            f"the 33,772 tabulated ACS ZCTAs matched to a polygon, and 19 "
            f"polygons with no ACS row kept with NULL values. Spot-checked "
            f"against data.census.gov: 90210 median household income "
            f"$187,801, 00601 (Adjuntas, PR) $19,454, 60614 (Chicago) "
            f"$136,448."),
        "places": (
            f"Validated: 32,612 rows (the 2024 cartographic boundary file's "
            f"own feature count; the Bureau's [2020 tallies]({GEO_TALLIES}) "
            f"give 19,734 incorporated places + 12,454 CDPs = 32,188 for the "
            f"2020 vintage), 32,612 distinct `geoid`, no percentage outside "
            f"0–100, every one of the 32,330 tabulated ACS places matched to "
            f"a polygon, 282 polygons with no ACS row kept with NULL values. "
            f"Spot-checked: Los Angeles city population 3,857,263, New York "
            f"city 8,483,844."),
        "congressional-districts": (
            f"Validated: 441 rows against the 441 districts in the Census "
            f"Bureau's own [geographic entity tallies]({GEO_TALLIES}) (436 "
            f"US including the District of Columbia delegate + 1 Puerto Rico "
            f"+ 4 island areas), 441 distinct `geoid`, no percentage outside "
            f"0–100, population 546,488–1,021,191 across the 435 voting "
            f"districts. Spot-checked: CA-12 median household income "
            f"$108,648, NY-12 $147,775, AL-01 $66,291."),
    }.get(cid, "")


def known_issues(cid: str) -> str:
    if cid == "blocks":
        return "\n\n".join([
            "28.97% of blocks have `pop_total = 0` (measured), so "
            "`pct_white_nh`, `pct_black` and `pct_hispanic` are NULL on that "
            "share of rows, and `pct_vacant` is NULL on the 27.64% with no "
            "housing units. By design — most census blocks are unpopulated. "
            "Filter `pop_total > 0` before averaging a rate.",

            "2020 block counts are protected by the Census Bureau's "
            "disclosure-avoidance system, which injects noise at block level "
            "while holding state totals exact. Reliable in aggregate; read a "
            "single block's counts with care.",

            "Geometry is TIGER/Line, which is not shoreline-clipped: a "
            "coastal block extends to the 3-mile limit. Water-only blocks "
            "have `ALAND20 = 0` and so a NULL `pop_density`.",

            "The race columns are race-alone counts crossing Hispanic "
            "origin (P1), while `pop_white_nh` is the not-Hispanic branch of "
            "P2. The two are not interchangeable, and `pct_black` here is "
            "not the same measure as `pct_black` in the ACS collections, "
            "which is non-Hispanic Black alone.",

            "Blocks carry 2020 Decennial counts only. The Census Bureau "
            "publishes no income, education, commuting or internet data "
            "below block group, and this collection invents none.",
        ])

    level = LEVEL_OF[cid]
    items = [
        "Island areas carry geometry but no ACS data. American Samoa, Guam, "
        "the Northern Mariana Islands and the U.S. Virgin Islands have "
        "cartographic boundaries but no ACS 5-year estimates, so their rows "
        "publish with NULL values rather than being dropped: 4 states, 13 "
        "county equivalents, 126 tracts, 405 block groups, 17 ZCTAs, 279 "
        "places and 4 delegate districts.",
    ]
    if cid == "zctas":
        items.append(
            f"**A ZCTA is not a ZIP code.** ZIP Code Tabulation Areas are "
            f"the Census Bureau's approximation of USPS 5-digit ZIP "
            f"delivery areas, built by assigning each 2020 census block the "
            f"most common ZIP code of the addresses in it "
            f"([what a ZCTA is]({ZCTA_ABOUT})). Consequences that bite: a "
            f"ZCTA boundary is not a ZIP boundary, some ZIP codes have no "
            f"ZCTA (PO-box-only and point ZIPs), ZCTA codes can differ from "
            f"the ZIP code of an address inside them, and the Bureau "
            f"re-delineates them only with each decennial census. Joining "
            f"customer ZIP codes to this file is an approximation, and it is "
            f"the user's job to say so.")
        items.append(
            "`state` is NULL on every row and there is no prefix join. A "
            "ZCTA can cross state and county lines, the ACS tabulates ZCTAs "
            "at the nation level only, and the 2020 cartographic boundary "
            "ZCTA file carries no state attribute to fall back on. The "
            "column is kept so the schema matches the catalog's other "
            "collections. Assign ZCTAs to states spatially (and expect "
            "ties), or use a Census relationship file.")
        items.append(
            "Medians thin out at this geography: `median_gross_rent` is NULL "
            "on 23.79% of ZCTAs, `median_home_value` on 10.45%, "
            "`median_hh_income` on 9.60%, and the race-iteration medians on "
            "58–77% (measured). These are the Census Bureau's own "
            "suppressions, reported rather than patched.")
        items.append(
            "Two ZCTAs — 11717 and 11798, in Suffolk County, New York — have "
            "2020 boundaries but no row in this ACS tabulation and publish "
            "with NULL values; they are the same two communities (Brentwood "
            "and Wyandanch) that the re-delineated Suffolk County tracts and "
            "block groups show up in elsewhere in this catalog.")
    if cid == "places":
        items.append(
            f"Places do not tile the country. A place is a settlement — an "
            f"incorporated city, town, village or borough, or a "
            f"[census designated place]({CDP_ABOUT}) standing in for an "
            f"unincorporated community — so the land between places is "
            f"absent from this file and place rows do not sum to a county or "
            f"a state. Places nest in states but not in counties: a place "
            f"can straddle a county line, which is why there is no "
            f"county-prefix join.")
        items.append(
            "Most rows are small places, so the suppression rates are high: "
            "`median_gross_rent` is NULL on 31.32% of places, "
            "`median_home_value` on 12.78%, `median_hh_income` on 12.71%, "
            "and the race-iteration medians on 69–86% (measured). Filter on "
            "`population` before reading a place-level distribution as if "
            "every row were a city.")
        items.append(
            "Three non-island places carry geometry and no ACS row: "
            "Brentwood CDP (`3608026`) and Wyandanch CDP (`3683294`) in "
            "Suffolk County, New York, and Louisville city, Kentucky "
            "(`2148000`), whose ACS tabulation is the consolidated "
            "`2148006` Louisville/Jefferson County metro government "
            "(balance) — if you want Louisville, use `2148006`.")
    if cid == "congressional-districts":
        items.append(
            f"**These are the districts of the {CONGRESS}th Congress**, "
            f"which is the vintage the ACS 2020–2024 5-year release "
            f"tabulates: the release's `GEO_ID` prefix is `5001900US` (the "
            f"`19`) and the boundary file is "
            f"`cb_2024_us_cd{CONGRESS}_500k` with `CDSESSN = '{CONGRESS}'`. "
            f"Confirmed against the Census Bureau's "
            f"[ACS geography boundaries by year]({ACS_BOUNDARY_VINTAGE}), "
            f"which lists \"Congressional District, Delegate District DC, "
            f"Resident Commissioner District PR\" with the vintage "
            f"\"{CONGRESS}th Congress of the United States\". District "
            f"numbers are not stable between congresses — several states "
            f"re-drew their maps for the {CONGRESS}th — so a GEOID here does "
            f"not refer to the same ground as the same GEOID in an earlier "
            f"congress, and estimates must not be compared across congresses "
            f"as a time series.")
        items.append(
            "441 rows, not 435: the 435 voting districts plus the District "
            "of Columbia delegate district (`1198`), Puerto Rico's Resident "
            "Commissioner district (`7298`) and the four island-area "
            "delegate districts (`6098`, `6698`, `6998`, `7898`), which "
            "carry geometry but no ACS estimates. Every column in this "
            "collection is NULL on exactly those four rows (0.91%).")
        items.append(
            "Three districts the ACS tabulates are absent, by construction: "
            "`09ZZ`, `17ZZ` and `33ZZ` — water-only pseudo-districts in "
            "Connecticut, Illinois and New Hampshire, each with population "
            "0 — have no polygon in the cartographic boundary file and so no "
            "row here.")
        items.append(
            "Districts are equal-population by design (546,488–1,021,191 "
            "here, around 770,000 at the median), so the spread of every "
            "rate is much narrower than at any other geography in this "
            "catalog. Class breaks measured at county or tract level will "
            "put almost every district in one or two classes; the styles "
            "shipped with this collection are measured on its own "
            "distribution.")
    if level in ("bg", "tract"):
        items.append(
            "Suffolk County, New York (36103) was re-delineated in the 2024 "
            "vintage: 39 block groups and 14 tracts exist in the 2024 "
            "cartographic boundary files with no matching row in the "
            "2020-based ACS tabulation, and publish with NULL ACS values. "
            "These are the only non-territory rows in the catalog with "
            "geometry but no data.")
        items.append(
            "443 ACS block groups and 338 ACS tracts (the `9900xx`-style "
            "water geographies) have no polygon in the cartographic boundary "
            "files and therefore no row here. All of them have population 0, "
            "so the dropped population is exactly 0 — this is why the tract "
            "collections hold 85,184 rows against 85,382 in the ACS "
            "release.")
    if level == "bg":
        # Only the medians this collection actually carries: a known-issues
        # list that names a column the file does not have is noise at best.
        here = set(cd.columns_for(cid))
        sparse = [(c, r) for c, r in (("median_hh_income", "7.69%"),
                                      ("median_gross_rent", "29.68%"),
                                      ("median_home_value", "10.03%"))
                  if c in here]
        if sparse:
            listed = ", ".join(f"`{c}` on {r} of rows" for c, r in sparse)
            items.append(
                f"Block-group medians are sparse where the sample is thin: "
                f"NULL for {listed}. These are the Census Bureau's own "
                f"suppressions, reported rather than patched.")
        if "per_capita_income" in here:
            items.append(
                "`per_capita_income` is incomplete upstream: B19301 "
                "publishes 242,069 block-group rows against 242,297 for "
                "B01003, and the missing 228 come through as NULL.")
    if cid == "tract-wellbeing":
        items.append(
            "The race-iteration medians are NULL wherever that group has too "
            "few households in the tract for a published median: "
            "`median_hh_income_asian` 71.27% of tracts, "
            "`median_hh_income_black` 61.43%, `median_hh_income_hispanic` "
            "44.43%, `median_hh_income_white_nh` 10.04%. A map of one of "
            "these columns is partly a map of where the group lives.")
    if cid == "congressional-districts":
        # Measured: no styled column has a single district with a CV above
        # 0.30 (docs/style-breaks.json). Reusing the small-area warning here
        # would be false modesty about the most reliable file in the catalog.
        items.append(
            "Margins of error are the narrowest in this catalog — a district "
            "is ~770,000 people — and no styled column has a single district "
            "with a coefficient of variation above 0.30 (measured). They are "
            "still margins: check whether two districts' margins overlap "
            "before calling a difference real, and never aggregate a "
            "median.")
    else:
        items.append(
            "Margins of error at this geography can be large relative to "
            "the estimate. Use the `*_cv` columns to flag or grey out "
            "unreliable values; never compare two geographies without "
            "checking whether their margins overlap, and never aggregate a "
            "median.")
    if cid in GEOM_ONLY_TILES:
        items.append(
            "The PMTiles archive is real geographies at every zoom, with no "
            "A5 cell aggregation (the catalog's finer collections aggregate "
            "at coarse zooms; this one has few enough features not to). "
            "`*_moe` columns are not in the tiles — statistics come from the "
            "GeoParquet.")
    else:
        items.append(
            "PMTiles coarse zooms are A5 cell aggregations, not census "
            "geographies — counts summed, rates and medians averaged "
            "unweighted. Statistics come from the GeoParquet.")
    return "\n\n".join(items)


def source_url(cid: str) -> str:
    return PL_DIR if cid == "blocks" else ACS_5YR_DATA


def _yq(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _block(key: str, text: str) -> str:
    lines = [f"{key}: |"]
    for line in text.split("\n"):
        lines.append(f"  {line}" if line else "")
    return "\n".join(lines)


def metadata_yaml(cid: str) -> str:
    """`.portolan/metadata.yaml` for one collection."""
    rel = COLL_REL[cid]
    data_href = (f"{PUBLIC_BASE}/{rel}/state_fips=*/*.parquet"
                 if cid == "blocks" else
                 f"{PUBLIC_BASE}/{rel}/{cid}.parquet")
    example = (
        f"INSTALL httpfs; LOAD httpfs;\n"
        f"SELECT * FROM read_parquet('{data_href}', "
        f"hive_partitioning=true) LIMIT 5;"
        if cid == "blocks" else
        f"INSTALL httpfs; LOAD httpfs;\nSELECT * FROM '{data_href}' LIMIT 5;")
    lines = [
        f"title: {_yq(TITLES[cid])}",
        _block("description", description(cid)),
        f"contact:\n  name: {_yq(CONTACT_NAME)}\n  email: {_yq(CONTACT_EMAIL)}",
        f"license: {_yq(LICENSE)}",
        f"license_url: {_yq(OPEN_DATA_POLICY)}",
        f"attribution: {_yq(ATTRIBUTION)}",
        f"source_url: {_yq(source_url(cid))}",
        f"keywords: [{', '.join(_yq(k) for k in keywords(cid))}]",
        _block("processing_notes", processing_notes(cid)),
        _block("known_issues", known_issues(cid)),
        "examples:",
        "  - engine: duckdb",
        f"    description: {_yq('Preview the first rows, straight off the published file')}",
        "    code: |",
        *[f"      {ln}" for ln in example.split("\n")],
    ]
    return "\n".join(lines) + "\n"


ROOT_YAML = f"""\
title: "US Census Demographics — Cloud-Native Mirror"
description: |
  Nationwide United States census statistics as cloud-native GeoParquet and
  PMTiles with STAC metadata, at every census geography from states down to
  the 242,298 block groups and 8,174,955 blocks of the 2020 Census, plus the
  33,791 ZIP Code Tabulation Areas, 32,612 places and 441 congressional
  districts of the 119th Congress. Fourteen
  collections carry curated [American Community Survey]({ACS_PROGRAM})
  2020–2024 5-year indicators — income, poverty, age, race and ethnicity,
  education, housing cost and tenure, vehicles, commuting, internet access,
  health insurance, disability, nativity — every estimate with its margin of
  error at the 90% confidence level and the headline statistics with a
  coefficient of variation. One collection carries 2020 Decennial Census
  P.L. 94-171 counts at block level, hive-partitioned by state.
  [data.census.gov]({DATA_CENSUS}) is authoritative; this is a mirror, and
  every collection links the exact upstream census.gov files it was built
  from.
contact:
  name: {CONTACT_NAME!r}
  email: {CONTACT_EMAIL!r}
license: "{LICENSE}"
license_url: "{OPEN_DATA_POLICY}"
attribution: "{ATTRIBUTION}"
source_url: "{DATA_CENSUS}"
keywords: ["census", "ACS", "American Community Survey", "decennial census",
  "demographics", "United States", "GeoParquet", "PMTiles", "STAC",
  "cloud-native"]
processing_notes: |
  Built from the Census Bureau's own published files over plain HTTPS, with no
  API key: the ACS 2020–2024 5-year table-based Summary File, the 2024
  cartographic boundary files, the 2020 P.L. 94-171 redistricting archives,
  and TIGER/Line 2024 TABBLOCK20 blocks. Extracted {EXTRACTED}.

  Statistics follow the Census Bureau's own methods: margins of error at the
  90% confidence level on every ACS estimate, quadrature for sums and the
  proportion/ratio formulas for percentages, jam values converted to NULL,
  coefficients of variation on headline columns, and every ACS table line
  number pinned against the release's table shells so a vintage bump that
  moves a line fails the build instead of publishing a mislabeled column.

  Each collection's own processing notes name its upstream files, its
  derivations and its known issues. Not an official Census Bureau product.
"""


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def write_metadata(only: set[str] | None = None) -> None:
    """Write .portolan/metadata.yaml files.

    `only` writes some collections and leaves the root and the rest alone —
    what a wave of new collections needs while other work is in flight.
    """
    if not only:
        d = CATALOG / ".portolan"
        d.mkdir(parents=True, exist_ok=True)
        (d / "metadata.yaml").write_text(ROOT_YAML)
        print("✓ catalog/.portolan/metadata.yaml")
    for cid in ALL_COLLECTIONS:
        if only and cid not in only:
            continue
        coll_dir = CATALOG / COLL_REL[cid]
        if not coll_dir.exists():
            print(f"✗ missing collection directory: {COLL_REL[cid]}")
            continue
        (coll_dir / ".portolan").mkdir(exist_ok=True)
        (coll_dir / ".portolan" / "metadata.yaml").write_text(
            metadata_yaml(cid))
        print(f"✓ {COLL_REL[cid]}/.portolan/metadata.yaml")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run --write BEFORE `portolan add`, then tools/make_stac.py.")
    ap.add_argument("--write", action="store_true",
                    help="write .portolan/metadata.yaml for the catalog root "
                         "and every collection")
    ap.add_argument("--print", dest="show", metavar="COLLECTION",
                    help="print one collection's title, keywords, source "
                         "assets and description to stdout")
    ap.add_argument("collections", nargs="*",
                    help="with --write, the only collections to write (the "
                         "catalog root is left alone)")
    args = ap.parse_args()
    only = set(args.collections) or None
    if only and (unknown := only - set(ALL_COLLECTIONS)):
        raise SystemExit(f"unknown collections: {sorted(unknown)}")
    if args.show:
        cid = args.show
        print(f"# {TITLES[cid]}\n")
        print(f"keywords: {', '.join(keywords(cid))}\n")
        print(f"source assets: {', '.join(source_assets(cid))}\n")
        print(description(cid))
        return
    if args.write:
        write_metadata(only)
        return
    for cid in (sorted(only) if only else ALL_COLLECTIONS):
        print(f"{COLL_REL[cid]:34s} {TITLES[cid]:52s} "
              f"{len(description(cid)):5d} chars, "
              f"{len(source_assets(cid)):2d} source/doc assets")


if __name__ == "__main__":
    main()
