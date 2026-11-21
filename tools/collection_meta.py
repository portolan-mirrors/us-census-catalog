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
# The Census Atlas explorer app (apps/explorer/), deployed by
# .github/workflows/pages.yml. `#c=<COLL_REL id>` deep-links a collection.
ATLAS = "https://portolan-mirrors.github.io/us-census-catalog/"
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
TIGER = "https://www2.census.gov/geo/tiger/TIGER2024"
REL2020 = "https://www2.census.gov/geo/docs/maps-data/data/rel2020"
PL_DIR = ("https://www2.census.gov/programs-surveys/decennial/2020/data/"
          "01-Redistricting_File--PL_94-171/")
PL_IMPORT_SCRIPTS = (
    "https://www2.census.gov/programs-surveys/decennial/rdo/about/"
    "2020-census-program/Phase3/SupportMaterials/2020PL_R_import_scripts.zip")

DATA_CENSUS = "https://data.census.gov/"
ACS_PROGRAM = "https://www.census.gov/programs-surveys/acs.html"
# The geography program, which publishes TIGER/Line and the
# relationship files. It is not a survey, so it carries no estimates.
GEO_PROGRAM = "https://www.census.gov/programs-surveys/geography.html"
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

# Group (catalog subdirectory) -> its collections, derived from
# `specs.COLLECTIONS` so this module cannot drift from the build's contract.
# Every ACS geography is a group as of the 2026-11-15 restructure: five themed
# chunks in theme order, plus — at the five coarse-or-sparse levels — the wide
# all-indicator table last, sharing its id with the group directory.
GROUPS: dict[str, list[str]] = {}
for _c in specs.COLLECTIONS:
    if _c.group:
        GROUPS.setdefault(_c.group, []).append(_c.id)
GROUP_OF = {cid: g for g, ids in GROUPS.items() for cid in ids}

# The wide all-indicator tables (`specs.WIDE_IDS`): counties, states, zctas,
# places, congressional-districts. Their collection.json sits in
# catalog/<group>/<id>/ with the themed children, but their parquet and
# pmtiles stay one directory up at catalog/<group>/<id>.parquet, so every
# published data URL survives the restructure. `data_url()` is the only place
# that knows this.
WIDE_IDS = set(specs.WIDE_IDS)

# The five groups whose themed children are column-pruned from a wide table
# that already shipped, rather than built per theme from the .dat files.
PRUNED_GROUPS = [g for g, ids in GROUPS.items() if set(ids) & WIDE_IDS]

# Collection id -> directory, relative to catalog/. Every collection except
# `blocks` now lives two levels down, in its group's directory.
COLL_REL = dict(
    {cid: f"{g}/{cid}" for g, ids in GROUPS.items() for cid in ids},
    blocks="blocks")

# The three wave-3 levels: ZCTAs, places and congressional districts, added
# after counties and states. Named by their wide table's id, which is also
# their group directory.
WAVE3 = ["zctas", "places", "congressional-districts"]

# In `specs.COLLECTIONS` order, with blocks (a different survey) last.
ALL_COLLECTIONS = [c.id for c in specs.COLLECTIONS] + ["blocks"]

LEVEL_OF = dict(cd.LEVEL_OF)

# Feature counts as the build measured them (docs/acs-build-notes.md,
# docs/blocks-build-notes.md). One count per geography level: a themed chunk
# is the same rows as its level's wide table with fewer columns, so it cannot
# have a different count. `make_stac.py` overrides each with the count it
# reads out of the published file.
LEVEL_FEATURES = {
    "bg": 242298, "tract": 85184, "county": 3235, "state": 56,
    "zcta": 33791, "place": 32612, "cd": 441, "block": 8174955,
}
FEATURES = {c.id: LEVEL_FEATURES[c.level] for c in specs.COLLECTIONS}
FEATURES["blocks"] = LEVEL_FEATURES["block"]

ACS_INTERVAL = ["2020-01-01T00:00:00Z", "2024-12-31T23:59:59Z"]
BLOCKS_INTERVAL = ["2020-04-01T00:00:00Z", "2020-04-01T00:00:00Z"]

# --------------------------------------------------------------------------
# reference/ (2026-11-15): geography that carries no demographic numbers.
# Not built from specs.COLLECTIONS -- this group holds no ACS theme and no
# ACS geography level, so it is registered here by hand instead of being
# derived from the ACS build's own contract.
# --------------------------------------------------------------------------
REFERENCE_IDS = ["urban-areas", "landmarks-area", "landmarks-point",
                 "crosswalks"]
GROUPS["reference"] = REFERENCE_IDS
GROUP_OF.update({cid: "reference" for cid in REFERENCE_IDS})
COLL_REL.update({cid: f"reference/{cid}" for cid in REFERENCE_IDS})
ALL_COLLECTIONS += REFERENCE_IDS

# Row counts, measured off the published files (staging/tiles-logs/
# reference.qc.json). crosswalks sums all 29 relationship tables; a single
# scalar count does not really describe 29 tables of very different sizes,
# but `make_stac.py` overrides it with the live count the same way it does
# for `blocks`, so this is only ever the --write-time placeholder.
FEATURES.update({
    "urban-areas": 2644, "landmarks-area": 120734,
    "landmarks-point": 1088085, "crosswalks": 22429855,
})

# --------------------------------------------------------------------------
# DHC subset (2026-11-15): 2020 Census age/sex, household type and tenure,
# placed beside the ACS collections at the same geography rather than in a
# separate decennial group (docs/spec-dhc.md). Not built from
# specs.COLLECTIONS -- a different survey, vintage and privacy model (100%
# counts with injected noise, no margin of error) -- so, like reference/,
# this is registered by hand. Unlike reference/, these six collections live
# INSIDE the existing block-groups and tracts groups, so `_siblings_para`
# below is patched to exclude them from the ACS sibling list it builds for
# bg-income etc. rather than mixing DHC into that prose.
# --------------------------------------------------------------------------
DHC_THEMES = ["age", "household", "tenure"]
DHC_LEVEL_PREFIX = {"bg": "bg", "tract": "tract"}
DHC_GROUP_OF_LEVEL = {"bg": "block-groups", "tract": "tracts"}
DHC_IDS = [f"{DHC_LEVEL_PREFIX[lvl]}-{theme}-dec2020"
          for lvl in DHC_LEVEL_PREFIX for theme in DHC_THEMES]
DHC_LEVEL_OF = {f"{DHC_LEVEL_PREFIX[lvl]}-{theme}-dec2020": lvl
               for lvl in DHC_LEVEL_PREFIX for theme in DHC_THEMES}
DHC_THEME_OF = {f"{DHC_LEVEL_PREFIX[lvl]}-{theme}-dec2020": theme
               for lvl in DHC_LEVEL_PREFIX for theme in DHC_THEMES}
for _cid, _lvl in DHC_LEVEL_OF.items():
    _g = DHC_GROUP_OF_LEVEL[_lvl]
    GROUPS.setdefault(_g, []).append(_cid)
    GROUP_OF[_cid] = _g
    COLL_REL[_cid] = f"{_g}/{_cid}"
ALL_COLLECTIONS += DHC_IDS

# Row counts: the join is driven by the same cartographic boundary files the
# ACS bg/tract collections join to (staging/geo/cb_2024_us_{bg,tract}_
# 4326.parquet), so the row counts are identical to the ACS collections at
# the same geography -- measured, not assumed, by tools/build_dhc.py.
FEATURES.update({cid: LEVEL_FEATURES[lvl] for cid, lvl in DHC_LEVEL_OF.items()})

# 2020 Census disclosure avoidance: differential privacy, Title 13
# confidentiality. Linked from every DHC collection's known_issues.
DHC_PROGRAM = ("https://www.census.gov/programs-surveys/decennial-census/"
              "about/rdo/summary-files.html")
DHC_DAS = ("https://www.census.gov/programs-surveys/decennial-census/"
          "decade/2020/planning-management/process/disclosure-avoidance.html")
DHC_TECHDOC = ("https://www2.census.gov/programs-surveys/decennial/2020/"
              "technical-documentation/complete-tech-docs/demographic-and-"
              "housing-characteristics-file-and-demographic-profile/"
              "2020census-demographic-and-housing-characteristics-file-and-"
              "demographic-profile-techdoc.pdf")
DHC_INTERVAL = ["2020-04-01T00:00:00Z", "2020-04-01T00:00:00Z"]

# TIGER2024 (urban-areas, landmarks-*) carries a 2024-09 vintage date; the
# rel2020 relationship files are keyed to the 2020 Census. The interval
# spans both rather than picking one.
REFERENCE_INTERVAL = ["2020-04-01T00:00:00Z", "2024-12-31T23:59:59Z"]

# --------------------------------------------------------------------------
# trends/ (batch 4, 2026-11-16): a dozen headline indicators, long form,
# across the 2015-2019 and 2020-2024 ACS 5-year vintages (docs/spec-
# trends.md). Not built from specs.COLLECTIONS -- long form (one row per
# geoid PER PERIOD, not one row per geoid), a geo_change column, and a
# second vintage -- so registered by hand like reference/ and DHC above,
# and duplicated in tools/column_docs.py for the same circular-import
# reason as REFERENCE_IDS/DHC_IDS there.
# --------------------------------------------------------------------------
TRENDS_IDS = ["county-trends", "state-trends", "tract-trends"]
TRENDS_LEVEL_OF = {"county-trends": "county", "state-trends": "state",
                  "tract-trends": "tract"}
GROUPS["trends"] = TRENDS_IDS
GROUP_OF.update({cid: "trends" for cid in TRENDS_IDS})
COLL_REL.update({cid: f"trends/{cid}" for cid in TRENDS_IDS})
ALL_COLLECTIONS += TRENDS_IDS

# Row counts, measured off the published files 2026-11-16 (one row per
# geoid per period, so twice the geography's own feature count).
FEATURES.update({"county-trends": 6470, "state-trends": 112,
                 "tract-trends": 170368})

# The 2015-2019 vintage starts the interval; 2020-2024 ends it. The STAC
# temporal extent must cover both periods, not just the current one.
TRENDS_INTERVAL = ["2015-01-01T00:00:00Z", "2024-12-31T23:59:59Z"]

TRENDS_SHELLS_URL_2019 = (
    "https://www2.census.gov/programs-surveys/acs/summary_file/2019/"
    "prototype/ACS2019_Table_Shells.csv")
TRENDS_5YR_DATA_2019 = ("https://www2.census.gov/programs-surveys/acs/"
                        "summary_file/2019/prototype/5YRData/")
TRENDS_GEOS_2019 = ("https://www2.census.gov/programs-surveys/acs/"
                    "summary_file/2019/prototype/Geos20195YR.csv")
COMPARING_ACS = cd.COMPARING_ACS_URL

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

# `<theme> — <geography>` for every ACS collection, composed rather than
# listed so a new themed chunk cannot arrive with a hand-typed title that
# disagrees with its siblings. `_siblings_para` splits these on " — ", so
# neither half may contain one.
LEVEL_TITLE = {
    "bg": "Block Groups",
    "tract": "Census Tracts",
    "county": "Counties",
    "state": "States",
    "zcta": "ZIP Code Tabulation Areas",
    "place": "Places & CDPs",
    "cd": f"Congressional Districts ({CONGRESS}th Congress)",
}
THEME_TITLE = {
    "income": "Income & Poverty",
    "people": "People & Education",
    "housing": "Housing & Rent",
    "connectivity": "Commuting & Connectivity",
    "wellbeing": "Health, Disability & Income by Race",
    "all": "All Indicators",
}

# A group's title is its geography's, because a group holds one geography.
GROUP_TITLES = {
    "block-groups": LEVEL_TITLE["bg"],
    "tracts": LEVEL_TITLE["tract"],
    "counties": LEVEL_TITLE["county"],
    "states": LEVEL_TITLE["state"],
    "zctas": LEVEL_TITLE["zcta"],
    "places": LEVEL_TITLE["place"],
    "congressional-districts": LEVEL_TITLE["cd"],
    "reference": "Reference Geography",
    "trends": "Trends, 2015–2024",
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
    """The theme a collection carries. A wide table's theme is "all"."""
    if cid in WIDE_IDS:
        return "all"
    if cid == "blocks":
        return "blocks"
    if cid in REFERENCE_IDS:
        return "reference"
    if cid in DHC_IDS:
        return DHC_THEME_OF[cid]
    return cid.split("-", 1)[1]


TITLES = {c.id: f"{THEME_TITLE[theme_of(c.id)]} — {LEVEL_TITLE[c.level]}"
          for c in specs.COLLECTIONS}
TITLES["blocks"] = "2020 Census Counts — Blocks"
TITLES.update({
    "urban-areas": "2020 Urban Areas",
    "landmarks-area": "Landmarks — Area",
    "landmarks-point": "Landmarks — Point",
    "crosswalks": "2020 Geography Crosswalks",
})

DHC_THEME_TITLE = {"age": "Age & Sex (2020 Census)",
                   "household": "Household Type (2020 Census)",
                   "tenure": "Tenure (2020 Census)"}
DHC_LEVEL_TITLE = {"bg": LEVEL_TITLE["bg"], "tract": LEVEL_TITLE["tract"]}
TITLES.update({cid: f"{DHC_THEME_TITLE[DHC_THEME_OF[cid]]} — "
                   f"{DHC_LEVEL_TITLE[lvl]}"
              for cid, lvl in DHC_LEVEL_OF.items()})

TITLES.update({cid: f"Trends, 2015–2024 — {LEVEL_TITLE[lvl]}"
              for cid, lvl in TRENDS_LEVEL_OF.items()})


_KW_REFERENCE = {
    "urban-areas": ["urban area", "urban cluster", "UAC20", "TIGER",
                    "urbanized", "city", "metro"],
    "landmarks-area": ["landmarks", "AREALM", "MIL", "MTFCC",
                       "military installation", "cemetery", "park", "TIGER"],
    "landmarks-point": ["landmarks", "POINTLM", "MTFCC", "points of "
                        "interest", "cul-de-sac", "TIGER"],
    "crosswalks": ["crosswalk", "relationship file", "rel2020",
                   "2010 Census", "2020 Census", "geography conversion",
                   "tract relationship"],
}


_DHC_KW_THEME = {
    "age": ["age", "sex", "age pyramid", "P12"],
    "household": ["household type", "family households", "living alone",
                  "relationship to householder", "P16", "P17"],
    "tenure": ["tenure", "owner occupied", "renter occupied",
              "housing units", "H1", "H4"],
}


def keywords(cid: str) -> list[str]:
    if cid == "blocks":
        return ["census", "2020 Census", "decennial census",
                "P.L. 94-171", "redistricting", "population", "race",
                "ethnicity", "voting age population", "housing occupancy",
                "group quarters", "United States", "census blocks"]
    if cid in REFERENCE_IDS:
        return (["census", "TIGER/Line", "geography", "United States"]
                + _KW_REFERENCE[cid])
    if cid in DHC_IDS:
        kw = (["census", "2020 Census", "decennial census", "DHC",
              "Demographic and Housing Characteristics",
              "differential privacy", "disclosure avoidance",
              "United States"]
             + _DHC_KW_THEME[DHC_THEME_OF[cid]]
             + _KW_LEVEL[DHC_LEVEL_OF[cid]])
        return list(dict.fromkeys(kw))
    if cid in TRENDS_IDS:
        kw = (["census", "ACS", "American Community Survey", "demographics",
              "United States", "margins of error", "trends", "time series",
              "change over time", "2015-2019", "2020-2024",
              "Connecticut", "geo_change", "t10t20"]
             + _KW_LEVEL[TRENDS_LEVEL_OF[cid]])
        return list(dict.fromkeys(kw))
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
        f"({_t('B22010')}), the unemployment rate as a share of the "
        f"civilian labor force ({_t('B23025')}), the household income "
        "distribution collapsed to 7 shares from under $25,000 to $200,000 "
        f"or more ({_t('B19001')}), and median earnings for workers with "
        f"earnings ({_t('B20002')}) — plus, at every level but block "
        "groups, where the Census Bureau does not publish them, the Gini "
        f"index of income inequality ({_t('B19083')}) and the poverty rate "
        f"by age for children under 18 and adults 65 and over ({_t('B17001')})"
        ", plus total population "
        f"({_t('B01003')}) and population density for context."),
    "people": (
        "Who lives here: median age and the shares under 18 and 65 or over "
        f"({_t('B01002')}, {_t('B01001')}), the four mutually exclusive "
        "non-Hispanic race shares this catalog carries — White, Black or "
        "African American, American Indian and Alaska Native, Asian — plus "
        "Hispanic or Latino of any race and its complement, people of color "
        f"({_t('B03002')}), and the share "
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
        "by race and ethnicity. At this many features width costs little, so "
        "the whole 135-column table is published here as well as a theme at "
        "a time in the five themed chunks beside it — a cross-theme question "
        "needs no join."),
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
        f"Districts are equal-population by construction — 546,488 to "
        f"1,021,191 people across the 435 voting districts, 771,301 at the "
        f"median of all 437 rows with data (measured) — so the "
        f"distribution of every rate here is far tighter than at any other "
        f"geography, and the map styles' class breaks are measured "
        f"accordingly. These are the districts of the **{CONGRESS}th "
        f"Congress** ([the vintage this ACS release tabulates]"
        f"({ACS_BOUNDARY_VINTAGE})); district numbers are not stable across "
        f"congresses, so do not join these GEOIDs to an earlier congress's "
        f"districts of the same number."),
}

# The themed chunks at the five coarse-or-sparse levels (2026-11-15). A
# consumer may read exactly one of them and nothing else, so each carries its
# geography's defining edge as well as its own theme's measured suppression
# and reliability. Every number below was counted with DuckDB over the
# published wide table these chunks are pruned from, 2026-11-15.
_LEVEL_EDGE = {
    "county": (
        "Counties are the coarsest geography most questions are actually "
        "asked at, and the most reliable in this catalog below state level: "
        "the median coefficient of variation on `median_hh_income` is "
        "**0.042** here against 0.125 at tract level (measured). One context "
        "column breaks the catalog's own rule — `population_moe` is NULL on "
        "**3,103 of the 3,235 rows**, only 132 small rural counties carrying "
        "a margin on `population` — so read `population` here as a count to "
        "use rather than an estimate to put an interval on."),
    "state": (
        "Fifty-six rows: the 50 states, the District of Columbia, Puerto Rico "
        "and the four island areas. The island-area rows carry geometry and "
        "no ACS estimates, so every value column is NULL on 4 of 56 rows "
        "(**7.14%**), and the 52 rows that do carry data are the most "
        "reliable estimates in this catalog — no headline column has a median "
        "coefficient of variation above **0.037** (measured). "
        "`population_moe` is NULL on all 56 rows, so `population` here is a "
        "count to use rather than an estimate to put an interval on."),
    "zcta": (
        f"A ZIP Code Tabulation Area [is not a ZIP code]({ZCTA_ABOUT}) — it "
        f"is the Census Bureau's block-built approximation of a USPS 5-digit "
        f"delivery area — and it nests in nothing, so `state` is NULL on "
        f"every row and there is no prefix join to counties or tracts. "
        f"Relating ZCTAs to other geographies is a spatial operation."),
    "place": (
        f"Most of the 32,612 rows are small: the file holds every "
        f"incorporated place and every "
        f"[census designated place]({CDP_ABOUT}) the Census Bureau "
        f"delineates, from New York city to villages of 40 people, so filter "
        f"on `population` before reading a place-level distribution as if "
        f"every row were a city. A place is also not a partition of the "
        f"country: the land between places is not in this file at all, so "
        f"place rows do not sum to a county or a state."),
    "cd": (
        f"Districts are equal-population by construction — 546,488 to "
        f"1,021,191 people across the 435 voting districts, 771,301 at the "
        f"median of all 437 rows with data (measured) — so "
        f"the distribution of every rate here is far tighter than at any "
        f"other geography, and the map styles' class breaks are measured "
        f"accordingly. These are the districts of the **{CONGRESS}th "
        f"Congress** ([the vintage this ACS release tabulates]"
        f"({ACS_BOUNDARY_VINTAGE})); district numbers are not stable across "
        f"congresses, so do not join these GEOIDs to an earlier congress's "
        f"districts of the same number."),
}

_THEME_EDGE = {
    ("county", "income"): (
        "`median_hh_income` is published for 3,221 of the 3,235 rows — NULL "
        "on **0.43%**, against 1.59% of tracts and 7.69% of block groups."),
    ("county", "people"): (
        "Nothing in this chunk is suppressed beyond the island areas: every "
        "column is NULL on exactly the **0.40%** of rows (13 county "
        "equivalents) that have boundaries and no ACS tabulation."),
    ("county", "housing"): (
        "`median_gross_rent` is NULL on **0.62%** of counties and "
        "`median_home_value` on **0.56%** — against 5.92% and 3.55% at tract "
        "level and 29.68% and 10.03% at block group."),
    ("county", "connectivity"): (
        "`pct_commute_transit` is the column to handle with care: only 2,417 "
        "of the 3,235 counties publish a coefficient of variation for it at "
        "all, and **69.9%** of those are above 0.40 (measured). Most "
        "counties have too little transit commuting to estimate a share "
        "precisely, and that is a finding rather than a defect."),
    ("county", "wellbeing"): (
        "The four race-iteration medians are sparse wherever the group has "
        "few households: `median_hh_income_asian` is NULL on **53.63%** of "
        "counties, `median_hh_income_black` on **39.47%**, "
        "`median_hh_income_hispanic` on **19.60%** and "
        "`median_hh_income_white_nh` on **2.38%** — against 71.27% / 61.43% "
        "/ 44.43% / 10.04% at tract level, which is the reason to answer a "
        "race-and-income question here."),
    ("state", "income"): (
        "Nothing is suppressed beyond the island areas, and the margins are "
        "tiny: the median coefficient of variation is **0.004** on "
        "`median_hh_income` and **0.010** on `pct_below_poverty` (measured)."),
    ("state", "people"): (
        "Nothing is suppressed beyond the island areas, so a state ranking "
        "on any column here is a complete ranking of the 52 rows with data."),
    ("state", "housing"): (
        "Nothing is suppressed beyond the island areas: `median_gross_rent` "
        "and `median_home_value` are published for all 52 rows that carry "
        "ACS data, with median coefficients of variation of **0.004** and "
        "**0.003** (measured)."),
    ("state", "connectivity"): (
        "Nothing is suppressed beyond the island areas, and even "
        "`pct_commute_transit` — the noisiest column in this catalog at every "
        "finer geography — has a median coefficient of variation of **0.037** "
        "here and a maximum of **0.197** (measured)."),
    ("state", "wellbeing"): (
        "All four race-iteration medians are published for every one of the "
        "52 rows with ACS data, which is true at no other geography in this "
        "catalog: their median coefficients of variation run **0.005** "
        "(`median_hh_income_white_nh`) to **0.025** "
        "(`median_hh_income_asian`), measured."),
    ("zcta", "income"): (
        "The medians thin out: `median_hh_income` is NULL for **9.60%** of "
        "ZCTAs and `per_capita_income` for **3.26%**, because a ZCTA with few "
        "households has no publishable median."),
    ("zcta", "people"): (
        "Beyond the 19 polygons with no ACS row at all, suppression here is "
        "small: `median_age` is NULL on **2.87%** of ZCTAs and "
        "`pct_bachelors_plus` on **2.04%** (measured)."),
    ("zcta", "housing"): (
        "`median_gross_rent` is NULL for **23.79%** of ZCTAs, "
        "`median_home_value` for **10.45%** and `pct_rent_burdened` for "
        "**10.96%**: a ZCTA with few renter or owner households has no "
        "publishable median."),
    ("zcta", "connectivity"): (
        "These are the noisiest columns at this geography: "
        "`pct_commute_transit` publishes a coefficient of variation for only "
        "13,378 of the 33,791 rows and **69.4%** of those are above 0.40, "
        "while `pct_hh_no_vehicle` has a median coefficient of variation of "
        "**0.395** (measured). Carry the `*_cv` columns into any map of "
        "them."),
    ("zcta", "wellbeing"): (
        "The race-iteration medians are sparse by construction: "
        "`median_hh_income_asian` is NULL for **76.59%** of ZCTAs, "
        "`median_hh_income_black` for **69.25%**, "
        "`median_hh_income_hispanic` for **58.55%** and "
        "`median_hh_income_white_nh` for **12.08%** (measured). A map of one "
        "of these columns is as much a map of where the group lives as of "
        "its income."),
    ("place", "income"): (
        "`median_hh_income` is NULL for **12.71%** of places and "
        "`per_capita_income` for **4.28%**, and the median coefficient of "
        "variation on `median_hh_income` is **0.139** (measured) — **7.3%** "
        "of the places that publish one are above the 0.40 \"unreliable\" "
        "line."),
    ("place", "people"): (
        "The mildest suppression in this group: `median_age` is NULL on "
        "**3.77%** of places and `pct_bachelors_plus` on **2.50%** "
        "(measured)."),
    ("place", "housing"): (
        "`median_gross_rent` is NULL for **31.32%** of places, "
        "`median_home_value` for **12.78%** and `pct_rent_burdened` for "
        "**14.60%** — most rows are places too small to have a publishable "
        "rent median."),
    ("place", "connectivity"): (
        "These are the noisiest estimates in this group: "
        "`pct_hh_no_vehicle` has a median coefficient of variation of "
        "**0.526**, and `pct_commute_transit` **0.691** over the 8,538 "
        "places that publish one at all (measured)."),
    ("place", "wellbeing"): (
        "The race-iteration medians are the sparsest in the catalog: "
        "`median_hh_income_asian` is NULL for **85.80%** of places, "
        "`median_hh_income_black` for **79.24%**, "
        "`median_hh_income_hispanic` for **69.35%** and "
        "`median_hh_income_white_nh` for **17.62%** (measured)."),
    ("cd", "income"): (
        "Nothing is suppressed beyond the four island-area delegate "
        "districts: `median_hh_income` is published for 437 of the 441 rows, "
        "with a median coefficient of variation of **0.010** (measured)."),
    ("cd", "people"): (
        "Nothing is suppressed beyond the four island-area delegate "
        "districts, which are NULL on every column (**0.91%** of rows)."),
    ("cd", "housing"): (
        "Nothing is suppressed beyond the four island-area delegate "
        "districts, and `median_gross_rent` and `median_home_value` carry "
        "median coefficients of variation of **0.008** and **0.007** "
        "(measured)."),
    ("cd", "connectivity"): (
        "Nothing is suppressed beyond the four island-area delegate "
        "districts, and of this collection's three `*_cv` columns only "
        "`pct_commute_transit` has even one district above 0.30 — exactly "
        "one, at 0.304, against maxima of 0.080 for `pct_hh_no_vehicle` and "
        "0.089 for `pct_no_internet` (measured). Elsewhere in this geography "
        "`median_hh_income_black_cv` reaches 0.480 and "
        "`pct_below_poverty_black_cv` 0.305, both in "
        "[cd-wellbeing](../cd-wellbeing/collection.json)."),
    ("cd", "wellbeing"): (
        "All four race-iteration medians are published for 436 or 437 of the "
        "441 rows — only `median_hh_income_asian` loses a fifth district "
        "(**1.13%** NULL) — which makes this the finest geography in the "
        "catalog where a race-and-income comparison is close to complete. "
        "Three districts carry a `median_hh_income_black_cv` above 0.40 "
        "(maximum 0.480, measured)."),
}

for _g in PRUNED_GROUPS:
    for _cid in GROUPS[_g]:
        if _cid in WIDE_IDS:
            continue  # the wide table keeps its own hand-written caveat
        _lvl = LEVEL_OF[_cid]
        THEME_CAVEAT[_cid] = (f"{_LEVEL_EDGE[_lvl]} "
                              f"{_THEME_EDGE[(_lvl, theme_of(_cid))]}")

# The two wide tables that had no caveat of their own get their geography's.
THEME_CAVEAT.setdefault("counties", _LEVEL_EDGE["county"])
THEME_CAVEAT.setdefault("states", _LEVEL_EDGE["state"])

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

# The census-geography pyramid. Coarse zooms carry a COARSER CENSUS
# GEOGRAPHY, with that geography's own published values under the same column
# names — not an abstract cell grid, and not a client-side roll-up of this
# collection's features. The zoom bands below are exactly the ones
# tools/make_tiles.py hands `tylertoo pyramid`, as recorded in
# staging/tiles-logs/<id>.pyramid.log.
PYRAMID = {
    "bg": {
        "bands": "z0–z5 are county polygons and z6–z7 census tracts, each "
                 "carrying the Census Bureau's own published estimates for "
                 "that geography, and z8–z13 are the block groups themselves",
        "not": "below z8 you are looking at counties and tracts, not block "
               "groups",
        "coarse": "a real county or tract",
    },
    "tract": {
        "bands": "z0–z5 are county polygons carrying the Census Bureau's own "
                 "published county estimates, and z6–z12 are the census "
                 "tracts themselves",
        "not": "below z6 you are looking at counties, not tracts",
        "coarse": "a real county",
    },
    "zcta": {
        "bands": "z0–z5 are county polygons carrying the Census Bureau's own "
                 "published county estimates, and z6–z12 are the ZIP Code "
                 "Tabulation Areas themselves. ZCTAs do not nest inside "
                 "counties, so the county band is orientation at national "
                 "zooms — real county values — and not a roll-up of these "
                 "features",
        "not": "below z6 you are looking at counties, not ZIP Code "
               "Tabulation Areas",
        "coarse": "a real county",
    },
    "place": {
        "bands": "z0–z5 are county polygons carrying the Census Bureau's own "
                 "published county estimates, and z6–z12 are the places "
                 "themselves. Places do not nest inside counties — a place "
                 "can cross a county line — so the county band is "
                 "orientation at national zooms, not a roll-up of these "
                 "features",
        "not": "below z6 you are looking at counties, not places",
        "coarse": "a real county",
    },
}

BLOCKS_TILES_PARA = (
    f"The PMTiles archive is a census-geography pyramid built with "
    f"[tylertoo]({TYLERTOO}): z0–z5 are county polygons and z6–z9 census "
    f"tracts carrying exact sums of the 2020 block counts — decennial counts "
    f"aggregate exactly, and the rate columns are recomputed from the summed "
    f"counts rather than averaged — and z10–z14 are the blocks themselves. "
    f"Thinning 8.1 million polygons down to a national zoom would show a "
    f"biased subset (small urban blocks drop first) rather than less data, "
    f"so the coarse zooms step up to a coarser census geography instead. "
    f"Every band carries the same column names, so one style expression "
    f"classifies every zoom — but below z10 you are looking at counties and "
    f"tracts, not blocks, and clicking a coarse feature identifies a real "
    f"county or tract by `geoid` and `name`. Statistics come from the "
    f"GeoParquet, never from the tiles.")

# The collections whose PMTiles carry real polygons at every zoom, with no
# coarser-geography band at all: few enough features that nothing has to be
# aggregated (counties `--band 0-10:geom`, states `0-8:geom`, congressional
# districts `0-10:geom` — see staging/tiles-logs/ and tools/make_tiles.py).
# Saying "the coarse zooms are a coarser geography" of these would be false.
# Keyed by level, not by id: a themed chunk holds exactly the same features as
# its level's wide table, so it is tiled the same way. Only `zcta` and `place`
# among the coarse levels need a pyramid — 33,791 and 32,612 features are too
# many to draw at a national zoom, and `PYRAMID` has a band plan for each.
GEOM_ONLY_LEVELS = {"county", "state", "cd"}
GEOM_ONLY_TILES = {c.id for c in specs.COLLECTIONS
                   if c.level in GEOM_ONLY_LEVELS}

GEOM_TILES_PARA = (
    "The PMTiles archive carries the same columns as the GeoParquet, minus "
    "the `*_moe` columns, and at every zoom the tiles are the real census "
    "geographies — there are few enough features here to draw them all at a "
    "national zoom, so this archive needs none of the coarser-geography "
    "coarse-zoom bands the catalog's finer collections carry. Built with "
    f"[tylertoo]({TYLERTOO}). Statistics still come from the GeoParquet: "
    f"margins of error are not in the tiles.")


def tiles_para(cid: str) -> str:
    if cid in GEOM_ONLY_TILES:
        return GEOM_TILES_PARA
    if cid == "blocks":
        return BLOCKS_TILES_PARA
    p = PYRAMID[LEVEL_OF[cid]]
    return (
        f"The PMTiles archive is a census-geography pyramid built with "
        f"[tylertoo]({TYLERTOO}): {p['bands']}. Thinning this many polygons "
        f"down to a national zoom would show a biased subset (small urban "
        f"geographies drop first) rather than less data, so the coarse zooms "
        f"step up to a coarser census geography instead of a thinned sample "
        f"of this one. Every band carries the same column names, so one "
        f"style expression classifies every zoom — but {p['not']}, and the "
        f"values there are the Bureau's official estimates for those "
        f"geographies, with their own meaning, rather than a "
        f"visualization-only average: clicking a coarse feature identifies "
        f"{p['coarse']} by `geoid` and `name`. The `*_moe` columns are "
        f"excluded from the tiles at every zoom — a margin of error is "
        f"computed for one specific geography and cannot be carried across "
        f"bands — while the `*_cv` columns are kept. Statistics come from "
        f"the GeoParquet, never from the tiles.")


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


# How a geography's GEOID relates to the rest of the catalog. Repeated in
# every chunk at that geography, because a consumer may read exactly one.
NESTS = {
    "bg": "GEOIDs nest by prefix: `substr(geoid, 1, 11)` is the tract, "
          "`substr(geoid, 1, 5)` the county and `substr(geoid, 1, 2)` the "
          "state.",
    "tract": "GEOIDs nest by prefix: `substr(geoid, 1, 5)` is the county and "
             "`substr(geoid, 1, 2)` the state, and a tract's block groups are "
             "the 12-character GEOIDs whose first 11 characters match it.",
    "county": "GEOIDs nest by prefix: `substr(geoid, 1, 2)` is the state, and "
              "tracts and block groups join back on their own first 5 "
              "characters.",
    "state": "GEOIDs nest by prefix: the first 2 characters of every county, "
             "tract, block-group, place and district GEOID in this catalog "
             "are its state's `geoid`.",
    "zcta": "A ZCTA nests in nothing: it can cross county and state lines, so "
            "there is no prefix join from `geoid` to any other collection "
            "here, and `state` is NULL on every row. Relating ZCTAs to "
            "counties or tracts is a spatial operation (or a Census "
            "relationship file), not a string operation.",
    "place": "A place nests in a state but not in a county — a place can "
             "straddle a county line — so `substr(geoid, 1, 2)` reaches the "
             "state row and nothing else joins by prefix.",
    "cd": "A district nests in a state, so `substr(geoid, 1, 2)` reaches the "
          "state row; nothing finer joins by prefix, because district "
          "boundaries follow 2020 census blocks rather than counties or "
          "tracts.",
}

# Group -> the phrase that names it in prose, for the "every other geography"
# sentence. Lower case, because it appears mid-sentence.
GROUP_PHRASE = {
    "block-groups": "block groups",
    "tracts": "census tracts",
    "counties": "counties",
    "states": "states",
    "zctas": "ZCTAs",
    "places": "places and CDPs",
    "congressional-districts": "congressional districts",
}


_NUM = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
        7: "seven"}


def _other_groups_clause(group: str) -> str:
    """Links to every geography's sub-catalog except this one's.

    GROUP_PHRASE holds the geography groups. The reference group is not
    a geography, so it never appears in this clause.
    """
    others = [g for g in GROUPS if g != group and g in GROUP_PHRASE]
    links = [f"[{GROUP_PHRASE[g]}](../../{g}/catalog.json)" for g in others]
    return ", ".join(links[:-1]) + f" and {links[-1]}"


def _siblings_para(cid: str) -> str:
    level = LEVEL_OF[cid]
    group = GROUP_OF.get(cid)
    if group is None:  # blocks, which has no siblings and its own prose
        return ""
    # DHC_IDS excluded: those six collections share a group directory with
    # the ACS ones (docs/spec-dhc.md's placement rule) but are a different
    # survey with their own cross-reference prose (_dhc_description), not
    # an ACS themed chunk.
    themed = [c for c in GROUPS[group] if c not in WIDE_IDS
             and c not in DHC_IDS]
    wide = next((c for c in GROUPS[group] if c in WIDE_IDS), None)
    elsewhere = (
        f"Every other geography in this catalog is organized the same way — "
        f"{_other_groups_clause(group)} — and the "
        f"[blocks](../../blocks/collection.json) collection carries 2020 "
        f"Decennial counts, a different survey and vintage rather than a "
        f"finer version of these numbers.")

    if cid in WIDE_IDS:
        links = [f"[{THEME_TITLE[theme_of(c)]}](../{c}/collection.json)"
                 for c in themed]
        joined = ", ".join(links[:-1]) + f" and {links[-1]}"
        return (
            f"**This is the full table** — all 135 columns on every row, the "
            f"file to read when a question crosses themes or when you want "
            f"one row with everything on it. The same rows are also published "
            f"as {_NUM[len(themed)]} themed chunks of 29–46 columns each — "
            f"{joined} — for a consumer who wants one theme and not the rest; "
            f"each carries the same `geoid`, the same geometry and the same "
            f"seven context columns, so it joins 1:1 back to this table. This "
            f"collection's metadata sits beside those chunks, but its "
            f"GeoParquet and PMTiles stay one directory up at "
            f"`{group}/{cid}.parquet` and `{group}/{cid}.pmtiles`, which is "
            f"where they have always been. {NESTS[level]} {elsewhere}")

    others = [c for c in themed if c != cid]
    links = [f"[{THEME_TITLE[theme_of(c)]}](../{c}/collection.json)"
             for c in others]
    joined = ", ".join(links[:-1]) + f" and {links[-1]}"
    if wide:
        wide_clause = (
            f" A sixth collection, "
            f"[{THEME_TITLE['all']}](../{wide}/collection.json), carries all "
            f"135 columns on the same rows in one wide table — at this many "
            f"features width costs little, so take that one if a question "
            f"crosses themes.")
    elif level == "bg":
        wide_clause = (
            " The wellbeing tables — health insurance, disability, nativity "
            "and income by race — are not published at this geography at all; "
            "they start at [census tracts](../../tracts/catalog.json).")
    else:
        wide_clause = (
            " There is no wide all-indicator table at this geography: a "
            "135-column file over this many rows would make every consumer "
            "download all of it. A question that crosses themes either joins "
            "the chunks on `geoid` or steps up to "
            "[counties](../../counties/counties/collection.json).")
    return (
        f"This is one themed chunk of {_NUM[len(themed)]} at this "
        f"geography. "
        f"The other themes are {joined}, split that way so a consumer who "
        f"wants one theme reads one file. Chunks at the same geography hold "
        f"the same rows and the same geometry, so they join 1:1 on `geoid`."
        f"{wide_clause} {NESTS[level]} {elsewhere}")


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


DHC_TABLES = {"age": ["P12"], "household": ["P16", "P17"],
             "tenure": ["H1", "H4"]}

DHC_LEAD = {
    "age": (
        "Sex by age for 23 age bands (P12), the full 2020 Census age "
        "pyramid: a total, a male/female split, and both sexes carried "
        "through the same 23 bands from under 5 to 85 and over. "
        "`pct_under18` and `pct_65plus` are this build's own sums of the "
        "published bands (not published columns themselves), named "
        "without the ACS collections' underscores (`pct_under18`, not "
        "`pct_under_18`) on purpose, so a query against both files by "
        "column name cannot silently select one sense when it meant the "
        "other."),
    "household": (
        "Two household tables: household type (P16 — family/nonfamily, "
        "married-couple, single-parent, living-alone) and household type "
        "including living alone by relationship to householder (P17 — "
        "spouse, child, parent, sibling, roommate, and the "
        "institutionalized/noninstitutionalized group-quarters "
        "population). `pct_family_households` and `pct_living_alone` are "
        "this build's own shares of the P16 counts."),
    "tenure": (
        "Housing units (H1) and tenure of occupied housing units (H4 — "
        "owned with a mortgage or loan, owned free and clear, renter "
        "occupied). `pct_owned`, `pct_rented` and `pct_vacant_2020` are "
        "this build's own shares, named apart from the ACS housing "
        "collections' `pct_owner_occupied` and `pct_vacant_units` so the "
        "two are never selected as if they were one column."),
}

DHC_SPEC_NOTE = (
    "**Deviation from the original brief:** the spec named P16 and P18 "
    "for household type. P18 turned out to be GROUP QUARTERS POPULATION "
    "BY SEX BY AGE BY MAJOR GROUP QUARTERS TYPE — institutionalized and "
    "noninstitutionalized counts, not household composition. P17, "
    "HOUSEHOLD TYPE (INCLUDING LIVING ALONE) BY RELATIONSHIP, is the "
    "table that actually carries relationship-to-householder detail, so "
    "this collection reads P16 + P17, not P16 + P18. See "
    "docs/dhc-build-notes.md.")


def _dhc_cross_refs(cid: str) -> str:
    level = DHC_LEVEL_OF[cid]
    other_level = "tract" if level == "bg" else "bg"
    other_cid = cid.replace(f"{DHC_LEVEL_PREFIX[level]}-",
                            f"{DHC_LEVEL_PREFIX[other_level]}-")
    group = DHC_GROUP_OF_LEVEL[level]
    acs_siblings = [c for c in GROUPS[group]
                    if c not in DHC_IDS and c not in WIDE_IDS]
    acs_links = ", ".join(
        f"[{THEME_TITLE[theme_of(c)]}](../{c}/collection.json)"
        for c in acs_siblings)
    other_theme = DHC_THEME_OF[cid]
    return (
        f"This sits beside the American Community Survey collections at "
        f"the same geography, not in a separate decennial group: "
        f"{acs_links}. All of them share this collection's `geoid` and "
        f"geometry and join 1:1 on `geoid` — but **do not subtract one "
        f"from the other**. This is a different measurement: a 2020 "
        f"Census 100% count with injected noise, not a 2020–2024 ACS "
        f"5-year sample estimate with a margin of error. The same theme "
        f"at the other geography this batch covers is "
        f"[{DHC_THEME_TITLE[other_theme]} — {DHC_LEVEL_TITLE[other_level]}]"
        f"(../../{DHC_GROUP_OF_LEVEL[other_level]}/{other_cid}/"
        f"collection.json).")


DHC_TILES_PARA = (
    "The PMTiles archive is one band, the collection's own features at "
    "every zoom (`tylertoo tiles`, not the county/tract pyramid the ACS "
    "collections use) — bg and tract are the two finest geographies this "
    "batch covers and there is no coarser DHC band to step up to yet. "
    "There are no `*_moe` columns to exclude: this is a 100% count, not "
    "an estimate, so there is nothing to exclude.")


def _dhc_mirror_para() -> str:
    return (
        f"This is a mirror — [data.census.gov]({DATA_CENSUS}) is "
        f"authoritative, and nothing here is an official Census Bureau "
        f"product. The exact upstream files this collection was built "
        f"from are published as `source` assets, linked at their "
        f"original census.gov URLs, so the original is always one click "
        f"away; the Bureau's own documentation is linked alongside them.")


def _dhc_description(cid: str, n: int) -> str:
    level = DHC_LEVEL_OF[cid]
    theme = DHC_THEME_OF[cid]
    noun = LEVEL_PLURAL[level]
    tables = " and ".join(DHC_TABLES[theme])
    paras = [
        f"{DHC_LEAD[theme]}\n\n"
        f"All **{n:,}** {noun} in the 50 states, the District of Columbia "
        f"and Puerto Rico, from the U.S. Census Bureau's [2020 Census "
        f"Demographic and Housing Characteristics File]({DHC_PROGRAM}) "
        f"(DHC), table{'s' if len(DHC_TABLES[theme]) > 1 else ''} "
        f"{tables}. The DHC is a 100% count from every return, the same "
        f"survey family as the "
        f"[blocks](../../blocks/collection.json) collection's P.L. "
        f"94-171 redistricting counts, read with the same per-state zip, "
        f"Latin-1 geoheader and `LOGRECNO` join — but a different table "
        f"set: blocks carries race, Hispanic origin, voting-age "
        f"population and housing occupancy; this carries age, sex, "
        f"household type and tenure, at block-groups and tracts rather "
        f"than blocks.",
        "**No margin of error, no coefficient of variation.** A 100% "
        "count carries no sampling error, so there is nothing here to "
        "estimate the uncertainty of — every column is the Bureau's "
        "tabulated count, full stop.",
        f"**Differential privacy.** The 2020 Census protects "
        f"confidentiality with a disclosure avoidance system that injects "
        f"statistical noise calibrated to a privacy-loss budget, most at "
        f"block level and least at state level (state population totals "
        f"are held exact; smaller geographies and smaller counts carry "
        f"more). A block group or tract's individual cells can be off by "
        f"a few people even though the file shows no margin of error; see "
        f"the Census Bureau's [disclosure avoidance documentation]"
        f"({DHC_DAS}) and the [DHC technical documentation]({DHC_TECHDOC}) "
        f"(Chapter 4, \"Confidentiality of the Data\").",
    ]
    if theme == "household":
        paras.append(DHC_SPEC_NOTE)
    paras += [_dhc_cross_refs(cid), DHC_TILES_PARA, _dhc_mirror_para()]
    return "\n\n".join(paras)


# Measured 2026-11-16 off the published files: the geo_change distribution
# at each level, as (identical, absorbed, subdivided, mixed, no_acs_data)
# counts of GEOIDS (not rows -- each geoid is 2 rows, one per period).
TRENDS_GEO_CHANGE_COUNTS = {
    "state": (52, 0, 0, 0, 4),
    "county": (3211, 0, 4, 7, 13),
    "tract": (58409, 403, 23068, 3075, 229),
}

TRENDS_LEAD = (
    "A dozen headline indicators — population, median household income, "
    "per capita income, the poverty rate, the unemployment rate, median "
    "age, the bachelor's-degree-or-higher share, the share of people of "
    "color, households, the owner-occupied share, median home value and "
    "median gross rent — carried across two non-overlapping ACS 5-year "
    "releases: **2015-2019** (`acsdt5y2019`, the Census Bureau's "
    f"table-based [prototype summary file]({TRENDS_5YR_DATA_2019}), "
    "validated against the [Census API](https://api.census.gov/data/2019/"
    "acs/acs5) before this collection was built — 29 requests, ~4.66 "
    "million compared values across every summary level this catalog "
    "uses including block groups, 0 mismatches) and **2020-2024** "
    f"(`acsdt5y2024`, the same release every other ACS collection here "
    f"reads). **Long form**: one row per `geoid` per `period`, not one "
    f"row per geoid — a consumer who wants \"both years side by side\" "
    f"pivots on `period`, and the `chg_*` columns already carry the "
    f"2020-2024-minus-2015-2019 difference on the 2020-2024 row so a map "
    f"style can classify on it without a join."
)

TRENDS_OVERLAP_NOTE = (
    "**The two periods do not overlap, which is what makes them "
    "comparable.** 2015-2019 and 2020-2024 share no sample year, unlike "
    "two 5-year releases one year apart (2019-2023 and 2020-2024, say), "
    "which the Census Bureau's own guidance on "
    f"[Comparing ACS Data]({COMPARING_ACS}) says not to compare because "
    "their overlapping sample years make a measured difference partly an "
    "artifact of shared data. This collection's two periods are five "
    "years apart with no shared sample year, so a difference here is a "
    "measured change, not a sampling artifact of the comparison itself — "
    "though it is still a difference of two margin-of-error estimates, "
    "see `chg_*_moe` and the known issues before calling a small "
    "difference real."
)


def _trends_geo_change_para(cid: str) -> str:
    level = TRENDS_LEVEL_OF[cid]
    ident, absorbed, subdiv, mixed, gap = TRENDS_GEO_CHANGE_COUNTS[level]
    total = ident + absorbed + subdiv + mixed + gap
    pct = lambda n: f"{100 * n / total:.1f}%"
    parts = [f"`identical` ({pct(ident)}, {ident:,} of {total:,})"]
    if absorbed:
        parts.append(f"`absorbed` ({pct(absorbed)}, {absorbed:,})")
    if subdiv:
        parts.append(f"`subdivided` ({pct(subdiv)}, {subdiv:,})")
    if mixed:
        parts.append(f"`mixed` ({pct(mixed)}, {mixed:,})")
    parts.append(f"`no_acs_data` ({pct(gap)}, {gap:,})")
    measured = "; ".join(parts)
    return (
        f"**`geo_change` is measured per geoid, not assumed** — see the "
        f"column's own description for the full definition of each "
        f"value. At this geography: {measured}. Never apportioned: the "
        f"period a geoid's lineage does not support a legitimate figure "
        f"for carries NULL on the affected columns rather than a modelled "
        f"or carried-over number dressed up as a measurement."
    )


_TRENDS_SAME_GEO_GROUP = {"county-trends": "counties", "state-trends": "states",
                         "tract-trends": "tracts"}


def _trends_siblings_para(cid: str) -> str:
    others = [f"[{TITLES[c]}](../{c}/collection.json)"
             for c in TRENDS_IDS if c != cid]
    joined = ", ".join(others[:-1]) + f" and {others[-1]}"
    same_geo = _TRENDS_SAME_GEO_GROUP[cid]
    return (
        f"Three collections, one per geography: {joined}. All three carry "
        f"the same dozen indicators and the same `geo_change` taxonomy; "
        f"they do not join to each other on `geoid` (a tract is not a "
        f"county). This group sits beside the ACS themed chunks at the "
        f"same geographies, not inside them — a different shape (long "
        f"form, two periods, `geo_change`) from every themed collection "
        f"this catalog otherwise publishes, and it carries only 12 of "
        f"the catalog's ~135 indicators rather than a theme's full set. "
        f"For every other 2020-2024 indicator at this geography, or for "
        f"a 2020-2024-only question with no time dimension, see "
        f"[{GROUP_PHRASE[same_geo]}](../../{same_geo}/catalog.json).")


def _trends_tiles_para(cid: str) -> str:
    level = TRENDS_LEVEL_OF[cid]
    if level == "tract":
        p = PYRAMID["tract"]
        return (
            f"The PMTiles archive is a census-geography pyramid built "
            f"with [tylertoo]({TYLERTOO}): {p['bands']}, exactly as the "
            f"tract ACS collections tile. A pyramid, not real tract "
            f"polygons at every zoom, because this collection holds two "
            f"periods' worth of 85,184 tracts and thinning that down to "
            f"a national zoom would show a biased subset rather than "
            f"less data. {p['not'].capitalize()}. The tiles carry the "
            f"`2020-2024` period's features only (one geometry per "
            f"geoid, with its `chg_*` columns already on it) — tiling "
            f"both periods' identical geometries twice would double the "
            f"archive for no visual gain, since a map renders one period "
            f"at a time. `*_moe` columns are excluded; `chg_*_moe` and "
            f"`*_cv`-equivalent reliability columns are not — there are "
            f"none on this collection, so check `chg_*_moe` before "
            f"styling confidently on a small difference. Statistics come "
            f"from the GeoParquet, which keeps both periods.")
    return (
        "The PMTiles archive carries the same columns as the GeoParquet "
        "minus the `*_moe` columns, at every zoom, for the `2020-2024` "
        "period's features only (one geometry per geoid, with its "
        "`chg_*` columns already on it — tiling both periods' identical "
        "geometries twice would double the archive for no visual gain). "
        f"Built with [tylertoo]({TYLERTOO}). Statistics come from the "
        "GeoParquet, which keeps both periods.")


def _trends_description(cid: str, n: int) -> str:
    level = TRENDS_LEVEL_OF[cid]
    noun = LEVEL_PLURAL[level]
    paras = [
        f"{TRENDS_LEAD}\n\n"
        f"All **{n:,}** rows at this geography ({n // 2:,} {noun} × 2 "
        f"periods), in the United States, Puerto Rico and the island "
        f"areas.",
        TRENDS_OVERLAP_NOTE,
        _trends_geo_change_para(cid),
        STATS_PARA,
        _geom_para(level),
        _trends_siblings_para(cid),
        _trends_tiles_para(cid),
        _mirror_para(cid),
    ]
    return "\n\n".join(p for p in paras if p)


def description(cid: str, features: int | None = None) -> str:
    """Full STAC description for a collection, as markdown."""
    n = features if features is not None else FEATURES[cid]
    if cid == "blocks":
        return _blocks_description(n)
    if cid in REFERENCE_IDS:
        return _reference_description(cid, n)
    if cid in DHC_IDS:
        return _dhc_description(cid, n)
    if cid in TRENDS_IDS:
        return _trends_description(cid, n)
    level = LEVEL_OF[cid]

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
        "and row count. Pull one state and you download one file. To query "
        "all 52 as one table use the glob over the anonymous S3 endpoint "
        "(`SET s3_region='us-west-2'; SET s3_url_style='path'; ... "
        "read_parquet('s3://us-west-2."
        "opendata.source.coop/portolan-mirrors/us-census-catalog/blocks/"
        "state_fips=*/*.parquet', hive_partitioning=true)`) — an HTTPS glob "
        "cannot list a directory and returns 404; see the "
        "[agent guide](AGENTS.md) for the tested forms. The synthesized "
        "`state_fips` key carries the numeric FIPS code and sits alongside "
        "the `state` column's USPS code.",

        tiles_para("blocks"),
        _mirror_para("blocks"),
    ])


REFERENCE_TILES_PARA = (
    "The PMTiles archive is a single band at full resolution, built with "
    f"[tylertoo]({TYLERTOO}) `tiles` (not `pyramid` — there is no coarser "
    "geography to step up to below this collection, so every zoom draws "
    "this collection's own features, thinned to fit the tile-size cap "
    "where a zoom is too dense to draw in full). Statistics come from the "
    "GeoParquet; this collection has no `*_moe` columns to exclude.")


def _reference_description(cid: str, n: int) -> str:
    """Full STAC description for a reference/ collection.

    Every geography/row count here is a literal copy of what
    tools/build_reference.py measured and printed; nothing is carried over
    from the ACS prose helpers above, since none of them applies to a
    collection with no ACS theme, no ACS geography level and no margin of
    error.
    """
    if cid == "urban-areas":
        return "\n\n".join([
            f"The Census Bureau's 2020 urban area delineation: all "
            f"**{n:,}** urban areas in the United States and Puerto Rico, "
            f"from [TIGER/Line 2024 `UAC20`]({TIGER}/UAC20/) — one national "
            f"file. For the 2020 Census the Bureau replaced the 2010 "
            f"urbanized-area/urban-cluster split with a single urban area "
            f"definition: every feature here carries the same MTFCC, "
            f"`G3500` (\"Urban Area\"), decoded into `feature_type`. "
            f"**Deviation from the original brief:** this means there is "
            f"no urban/rural class column (`UATYPE20`, from the 2010 "
            f"product) to style on — it does not exist in `UAC20` — so the "
            f"default style classes on land area instead; see the "
            f"collection's processing notes.",
            "`aland_sqkm` and `awater_sqkm` are `ALAND20`/`AWATER20` "
            "converted from square meters. Geometry keeps the source CRS "
            "(NAD83, EPSG:4269) rather than being reprojected to WGS84.",
            REFERENCE_TILES_PARA,
            _mirror_para(cid),
        ])
    if cid == "landmarks-area":
        return "\n\n".join([
            f"Polygon landmarks from TIGER/Line 2024: all **{n:,}** "
            f"features combining [`AREALM`]({TIGER}/AREALM/) (civilian "
            f"landmarks, one file per state) and [`MIL`]({TIGER}/MIL/) "
            f"(military installations, one national file) into a single "
            f"table, with `landmark_kind` set to `landmark` or `military` "
            f"so the two sources stay distinguishable after the merge. "
            f"Measured: 119,876 `landmark` rows (all 56 states carry a "
            f"`state` column) and 858 `military` rows (none do — `MIL` is "
            f"a national file, not per-state, so there is no state to "
            f"carry, and `AREALM` carries no `aland_sqkm`/`awater_sqkm` so "
            f"those are NULL on every `landmark` row).",
            "`feature_type` decodes each row's `mtfcc` through the Census "
            "Bureau's MAF/TIGER Feature Class Code list; see the "
            "collection's processing notes for the exact source and which "
            "codes, if any, this build could not decode. Measured "
            "nationally, the five most common types are cemeteries, "
            "parks, local jails and detention centers, hospitals, and "
            "universities or colleges — the five the default style colors.",
            REFERENCE_TILES_PARA,
            _mirror_para(cid),
        ])
    if cid == "landmarks-point":
        return "\n\n".join([
            f"Point landmarks from [TIGER/Line 2024 `POINTLM`]({TIGER}"
            f"/POINTLM/): all **{n:,}** features, one file per state (56 "
            f"state and territory files), each carrying the `state` USPS "
            f"code its source file was read from.",
            "`feature_type` decodes each row's `mtfcc` the same way "
            "landmarks-area does. Measured nationally, most of these "
            "points are cul-de-sacs and locality points — address-system "
            "landmarks, not places a person would look for on a map — "
            "followed by cemeteries, mountain peaks and summits, and "
            "airports or airfields.",
            REFERENCE_TILES_PARA,
            _mirror_para(cid),
        ])
    # crosswalks
    return "\n\n".join([
        f"**{n:,}** rows across **29 tables**, each its own parquet file "
        f"in this collection's directory, from the Census Bureau's [2020 "
        f"relationship files]({REL2020}/) — every geography pair this "
        f"catalog carries a crosswalk for. Tabular: no geometry, no "
        f"`geoid`/`name`/`state` columns, because a relationship file's "
        f"job is converting between two geography vintages or two "
        f"geography types, not describing one feature.",
        "`t10t20-tract.parquet` is the one later trend work depends on: it "
        "maps 2010 tabulation blocks to 2020 tabulation blocks, with the "
        "land and water area each 2010 block split across. It is "
        "block-level, not tract-level, because 2010 and 2020 tracts do "
        "not nest — the Bureau's own crosswalk for that relationship is "
        "built from block-level overlap, and the state+county+tract "
        "columns already in that file are what a tract-to-tract join "
        "reads. The other 28 tables are every other rel2020 relationship, "
        "one file per relationship, read from each subdirectory's single "
        "national file (`*_natl.txt`) except `t10t20`, the one "
        "relationship rel2020 ships with no national file — those 28 "
        "come from `tract`, `blkgrp`, `place`, `cousub`, `cbsa` (3 "
        "relationships), `zcta520` (6), `ua` (8), `puma520` (4) and "
        "`aiannh` (3).",
        "No PMTiles for this collection — there is no geometry to tile.",
        _mirror_para(cid),
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
        f"authoritative. Three more collections sit beside these four: "
        f"[age & sex](./bg-age-dec2020/collection.json), "
        f"[household type](./bg-household-dec2020/collection.json) and "
        f"[tenure](./bg-tenure-dec2020/collection.json), 2020 Census "
        f"100% counts with no margin of error — a different measurement "
        f"from the ACS estimates beside them, not a finer version of the "
        f"same one."),
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
        f"groups). [data.census.gov]({DATA_CENSUS}) is authoritative. Three "
        f"more collections sit beside these five, mirroring the block-group "
        f"group: [age & sex](./tract-age-dec2020/collection.json), "
        f"[household type](./tract-household-dec2020/collection.json) and "
        f"[tenure](./tract-tenure-dec2020/collection.json), 2020 Census "
        f"100% counts with no margin of error."),
    "counties": (
        f"American Community Survey 2020–2024 5-year indicators for all "
        f"3,235 counties and county equivalents in the United States, Puerto "
        f"Rico and the island areas — the coarsest geography most questions "
        f"are actually asked at, and the most reliable in this catalog below "
        f"state level: the median coefficient of variation on median "
        f"household income is 0.042 here against 0.125 at tract level "
        f"(measured). Six collections share these rows. Five are the themed "
        f"chunks the finer geographies carry — "
        f"[income](./county-income/collection.json), "
        f"[people](./county-people/collection.json), "
        f"[housing](./county-housing/collection.json), "
        f"[connectivity](./county-connectivity/collection.json) and "
        f"[wellbeing](./county-wellbeing/collection.json), 29–46 columns each "
        f"— and the sixth, [all indicators](./counties/collection.json), is "
        f"the wide 135-column table, whose GeoParquet and PMTiles stay at "
        f"`counties/counties.parquet` and `counties/counties.pmtiles`. All "
        f"six hold the same `geoid` and the same geometry and join 1:1. One "
        f"quirk to carry: `population_moe` is NULL on 3,103 of the 3,235 "
        f"rows (measured). [data.census.gov]({DATA_CENSUS}) is "
        f"authoritative."),
    "states": (
        f"American Community Survey 2020–2024 5-year indicators for all 56 "
        f"states and state equivalents — the 50 states, the District of "
        f"Columbia, Puerto Rico and the four island areas, whose rows carry "
        f"geometry and no ACS estimates. The 52 rows that do carry data hold "
        f"the most reliable estimates in this catalog: no headline column has "
        f"a median coefficient of variation above 0.037 (measured). Six "
        f"collections share these rows — "
        f"[income](./state-income/collection.json), "
        f"[people](./state-people/collection.json), "
        f"[housing](./state-housing/collection.json), "
        f"[connectivity](./state-connectivity/collection.json), "
        f"[wellbeing](./state-wellbeing/collection.json) and the wide "
        f"135-column [all indicators](./states/collection.json) table, whose "
        f"GeoParquet and PMTiles stay at `states/states.parquet` and "
        f"`states/states.pmtiles`. All six hold the same `geoid` and the same "
        f"geometry and join 1:1; `population_moe` is NULL on all 56 rows "
        f"(measured). [data.census.gov]({DATA_CENSUS}) is authoritative."),
    "zctas": (
        f"American Community Survey 2020–2024 5-year indicators for all "
        f"33,791 ZIP Code Tabulation Areas. A ZCTA "
        f"[is not a ZIP code]({ZCTA_ABOUT}) — it is the Census Bureau's "
        f"block-built approximation of a USPS 5-digit delivery area — and it "
        f"nests in nothing, so `state` is NULL on every row and there is no "
        f"prefix join to counties or tracts. Six collections share these "
        f"rows: [income](./zcta-income/collection.json), "
        f"[people](./zcta-people/collection.json), "
        f"[housing](./zcta-housing/collection.json), "
        f"[connectivity](./zcta-connectivity/collection.json), "
        f"[wellbeing](./zcta-wellbeing/collection.json) and the wide "
        f"135-column [all indicators](./zctas/collection.json) table, whose "
        f"GeoParquet and PMTiles stay at `zctas/zctas.parquet` and "
        f"`zctas/zctas.pmtiles`. All six hold the same `geoid` and the same "
        f"geometry and join 1:1. The medians thin out at this geography — "
        f"`median_gross_rent` is NULL on 23.79% of ZCTAs and "
        f"`median_hh_income` on 9.60% (measured) — so read each collection's "
        f"`*_cv` columns and its AGENTS.md before mapping. "
        f"[data.census.gov]({DATA_CENSUS}) is authoritative."),
    "places": (
        f"American Community Survey 2020–2024 5-year indicators for all "
        f"32,612 incorporated places and "
        f"[census designated places]({CDP_ABOUT}) — every city, town, "
        f"village, borough and named unincorporated community the Census "
        f"Bureau delineates, from New York city to villages of 40 people. "
        f"Places do not tile the country: the land between them is not in "
        f"these files at all, so place rows never sum to a county or a state. "
        f"Six collections share these rows: "
        f"[income](./place-income/collection.json), "
        f"[people](./place-people/collection.json), "
        f"[housing](./place-housing/collection.json), "
        f"[connectivity](./place-connectivity/collection.json), "
        f"[wellbeing](./place-wellbeing/collection.json) and the wide "
        f"135-column [all indicators](./places/collection.json) table, whose "
        f"GeoParquet and PMTiles stay at `places/places.parquet` and "
        f"`places/places.pmtiles`. All six hold the same `geoid` and the same "
        f"geometry and join 1:1. Most rows are small, so the suppression "
        f"rates are high (`median_gross_rent` NULL on 31.32% of places, "
        f"`median_hh_income` on 12.71%, measured): filter on `population` "
        f"before reading a place-level distribution as if every row were a "
        f"city. [data.census.gov]({DATA_CENSUS}) is authoritative."),
    "congressional-districts": (
        f"American Community Survey 2020–2024 5-year indicators for all 441 "
        f"congressional districts of the **{CONGRESS}th Congress** — the 435 "
        f"voting districts, the District of Columbia delegate district, "
        f"Puerto Rico's Resident Commissioner district and the four "
        f"island-area delegate districts, which carry geometry and no ACS "
        f"estimates. This is "
        f"[the vintage the 2024 ACS release tabulates]"
        f"({ACS_BOUNDARY_VINTAGE}); district numbers are not stable across "
        f"congresses, so these GEOIDs must not be joined to an earlier "
        f"congress's districts of the same number. Six collections share "
        f"these rows: [income](./cd-income/collection.json), "
        f"[people](./cd-people/collection.json), "
        f"[housing](./cd-housing/collection.json), "
        f"[connectivity](./cd-connectivity/collection.json), "
        f"[wellbeing](./cd-wellbeing/collection.json) and the wide "
        f"135-column [all indicators]"
        f"(./congressional-districts/collection.json) table, whose "
        f"GeoParquet and PMTiles stay at "
        f"`congressional-districts/congressional-districts.parquet` and "
        f"`….pmtiles`. All six hold the same `geoid` and the same geometry "
        f"and join 1:1. Districts are equal-population by construction "
        f"(546,488–1,021,191 people across the 435 voting districts), so "
        f"every rate's distribution is "
        f"far tighter than at any other geography and the margins are the "
        f"narrowest in this catalog. [data.census.gov]({DATA_CENSUS}) is "
        f"authoritative."),
    "reference": (
        "Geography that carries no demographic statistic, so it stays out "
        "of the seven geography groups above. Four collections, all from "
        "TIGER/Line 2024 and the 2020 Census relationship files: "
        "[urban-areas](./urban-areas/collection.json) (2,644 features, the "
        "2020 urban area delineation), "
        "[landmarks-area](./landmarks-area/collection.json) (120,734 "
        "civilian and military area landmarks), "
        "[landmarks-point](./landmarks-point/collection.json) (1,088,085 "
        "point landmarks) and "
        "[crosswalks](./crosswalks/collection.json) (22,429,855 rows "
        "across 29 tabular relationship tables, no geometry). None of the "
        "four shares a geometry or a `geoid` with another, so there is no "
        "1:1 join across this group the way the ACS geographies join "
        "across their themed collections — each collection here stands "
        "on its own."),
    "trends": (
        "A dozen headline indicators across two non-overlapping ACS "
        "5-year releases, 2015-2019 and 2020-2024, long form — one row "
        "per `geoid` per `period`. Three collections, one per geography: "
        "[county-trends](./county-trends/collection.json) (3,235 "
        "counties), [state-trends](./state-trends/collection.json) (56 "
        "states) and [tract-trends](./tract-trends/collection.json) "
        "(85,184 tracts). Every row carries `geo_change` — `identical`, "
        "`absorbed`, `subdivided`, `mixed` or `no_acs_data` — measured "
        "per geoid against the real 2010-to-2020 tract crosswalk and the "
        "2022 Connecticut county realignment, never assumed, and the "
        "period a geoid's lineage cannot legitimately support carries "
        "NULL rather than an apportioned number. The `chg_*` columns "
        "carry the 2020-2024-minus-2015-2019 difference, already "
        "computed, on the 2020-2024 row. These three collections carry "
        "only 12 of the catalog's ~135 indicators; for everything else, "
        "or for a 2020-2024-only question, see the counties, states and "
        "tracts groups."),
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
    if cid in DHC_IDS:
        return DHC_TABLES[DHC_THEME_OF[cid]]
    if cid in TRENDS_IDS:
        import build_trends as bt
        return sorted(bt.TABLE_LINES)
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


def _dat_asset_2019(table: str) -> tuple[str, dict]:
    title, universe = cd.TABLE_UNIVERSE[table]
    key = f"source-2019-{table.lower()}"
    return key, {
        "href": f"{TRENDS_5YR_DATA_2019}acsdt5y2019-{table.lower()}.dat",
        "type": "text/plain",
        "title": f"ACS 2015–2019 prototype detailed table {table} — {title}",
        "description": (
            f"The 2015-2019 upstream file this collection's {table} "
            f"columns were read from, from the Census Bureau's "
            f"table-based prototype directory — the same layout as the "
            f"2020-2024 production file (`GEO_ID|{table}_E001|"
            f"{table}_M001|...`), validated against the Census API before "
            f"this collection was built (see processing_notes). Universe: "
            f"{universe}. Served by census.gov, not by this mirror."),
        "roles": ["source"],
    }


MTFCC_CODES_URL = ("https://www.census.gov/library/reference/code-lists/"
                   "mt-feature-class-codes.html")
MTFCC_PDF_2022 = "https://www2.census.gov/geo/pdfs/reference/mtfccs2022.pdf"


def _reference_source_assets(cid: str) -> dict:
    """`source_assets` for the four reference/ collections."""
    out: dict[str, dict] = {}
    mtfcc_doc = {
        "href": MTFCC_PDF_2022,
        "type": "application/pdf",
        "title": "2022 MAF/TIGER Feature Class Code Definitions",
        "description": (
            "The code -> name table `feature_type` was decoded from. "
            "TIGER2024 has no 2024 edition of this PDF; 2022 is the "
            "nearest published vintage, linked from the Bureau's own "
            f"index at {MTFCC_CODES_URL}. The code set is unchanged "
            "between the two: every code this build used also appears, "
            "worded the same, in the 2021 and 2025 editions."),
        "roles": ["metadata"],
    }
    if cid == "urban-areas":
        out["source-uac20"] = {
            "href": f"{TIGER}/UAC20/tl_2024_us_uac20.zip",
            "type": "application/zip",
            "title": "TIGER/Line 2024 UAC20 — 2020 urban areas, national file",
            "description": (
                "The one national shapefile this collection's 2,644 "
                "features were read from."),
            "roles": ["source"],
        }
        out["doc-mtfcc"] = mtfcc_doc
        return out
    if cid == "landmarks-area":
        out["source-arealm"] = {
            "href": f"{TIGER}/AREALM/",
            "type": "text/html",
            "title": "TIGER/Line 2024 AREALM — area landmarks, state directory",
            "description": (
                "56 state and territory shapefiles "
                "(`tl_2024_<FIPS>_arealm.zip`), this collection's "
                "`landmark_kind = 'landmark'` rows."),
            "roles": ["source"],
        }
        out["source-mil"] = {
            "href": f"{TIGER}/MIL/tl_2024_us_mil.zip",
            "type": "application/zip",
            "title": "TIGER/Line 2024 MIL — military installations, "
                     "national file",
            "description": (
                "The one national shapefile this collection's "
                "`landmark_kind = 'military'` rows were read from."),
            "roles": ["source"],
        }
        out["doc-mtfcc"] = mtfcc_doc
        return out
    if cid == "landmarks-point":
        out["source-pointlm"] = {
            "href": f"{TIGER}/POINTLM/",
            "type": "text/html",
            "title": "TIGER/Line 2024 POINTLM — point landmarks, state "
                     "directory",
            "description": (
                "56 state and territory shapefiles "
                "(`tl_2024_<FIPS>_pointlm.zip`), this collection's source."),
            "roles": ["source"],
        }
        out["doc-mtfcc"] = mtfcc_doc
        return out
    # crosswalks
    out["source-rel2020"] = {
        "href": f"{REL2020}/",
        "type": "text/html",
        "title": "2020 Census relationship files (rel2020) — subdirectory "
                 "index",
        "description": (
            "The ten subdirectories this collection's 29 tables were read "
            "from: t10t20, tract, blkgrp, place, cousub, cbsa, zcta520, "
            "ua, puma520, aiannh. Each is a pipe-delimited text file, "
            "read directly over HTTPS with no download step."),
        "roles": ["source"],
    }
    return out


DHC_FTP_DIR = ("https://www2.census.gov/programs-surveys/decennial/2020/"
              "data/demographic-and-housing-characteristics-file/")
DHC_TABLE_MATRIX = ("https://www2.census.gov/programs-surveys/decennial/"
                    "2020/technical-documentation/complete-tech-docs/"
                    "demographic-and-housing-characteristics-file-and-"
                    "demographic-profile/2020-dhc-table-matrix.xlsx")


def _dhc_source_assets(cid: str) -> dict:
    level = DHC_LEVEL_OF[cid]
    out: dict[str, dict] = {
        "source-dhc-states": {
            "href": DHC_FTP_DIR,
            "type": "text/html",
            "title": "2020 Census Demographic and Housing Characteristics "
                     "File (DHC) — state directories",
            "description": (
                "The 52 state archives (`{State_Name}/{ab}2020.dhc.zip`) "
                "this collection's counts were read from. Each archive "
                "holds a pipe-delimited Latin-1 geoheader plus 44 segment "
                "files joined on `LOGRECNO`; this collection reads "
                f"segments carrying {' and '.join(DHC_TABLES[DHC_THEME_OF[cid]])}"
                f" and filters the geoheader to `SUMLEV = "
                f"'{'150' if level == 'bg' else '140'}'`, "
                "`GEOCOMP = '00'`. Served by census.gov."),
            "roles": ["source"],
        },
        "doc-dhc-techdoc": {
            "href": DHC_TECHDOC,
            "type": "application/pdf",
            "title": "2020 Census DHC and Demographic Profile — "
                     "Technical Documentation",
            "description": (
                "Chapter 3 (Data Dictionary) gives the table shells; "
                "Chapter 4 (Confidentiality of the Data) is the source for "
                "this collection's differential-privacy known issue. "
                "Served by census.gov."),
            "roles": ["metadata"],
        },
        "doc-dhc-table-matrix": {
            "href": DHC_TABLE_MATRIX,
            "type": "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet",
            "title": "2020 Census DHC Table Matrix",
            "description": (
                "Table ID, segment number and field position for every "
                "DHC table — the spreadsheet this build's field positions "
                "(tools/build_dhc.py) were derived from and verified "
                "against the real per-state files' field counts. Served "
                "by census.gov."),
            "roles": ["metadata"],
        },
        "doc-disclosure-avoidance": {
            "href": DHC_DAS,
            "type": "text/html",
            "title": "2020 Census Disclosure Avoidance System",
            "description": (
                "The Census Bureau's own explanation of the differential-"
                "privacy system that injects noise into every 2020 Census "
                "data product, this one included. Served by census.gov."),
            "roles": ["metadata"],
        },
    }
    year = cd.CB_VINTAGE[level]
    out["source-cartographic-boundaries"] = {
        "href": CB_LEVEL_URL[level],
        "type": "application/zip",
        "title": f"{year} cartographic boundary file — "
                 f"{LEVEL_PLURAL[level]} (1:500,000, national)",
        "description": (
            "The same boundary file the ACS collections at this geography "
            "join to — reused, not re-downloaded, so a DHC row and an ACS "
            "row for the same `geoid` always share the same geometry."),
        "roles": ["source"],
    }
    return out


def _trends_source_assets(cid: str) -> dict:
    out: dict[str, dict] = {}
    for table in tables_for(cid):
        key, asset = _dat_asset(table)
        out[key] = asset
        key19, asset19 = _dat_asset_2019(table)
        out[key19] = asset19
    out["source-table-shells-2024"] = {
        "href": cd.SHELLS_URL,
        "type": "text/plain",
        "title": "ACS 2020–2024 5-year table shells",
        "description": (
            "Every 2020-2024 line number this collection reads is pinned "
            "against this file. Served by census.gov."),
        "roles": ["source"],
    }
    out["source-table-shells-2019"] = {
        "href": TRENDS_SHELLS_URL_2019,
        "type": "text/csv",
        "title": "ACS 2015–2019 prototype table shells",
        "description": (
            "Re-pinned against this file before the 2015-2019 side of "
            "this collection was built: all 55 shell pins and all 120 "
            "(table, line) pairs this catalog's specs use resolve to "
            "the SAME line with the SAME concept as the 2020-2024 "
            "shells. A different layout from the 2024 file (comma-"
            "delimited, no Indent column, the label column called "
            "\"Stub\"), handled by `tools/specs.py`'s `shells()`. "
            "Served by census.gov."),
        "roles": ["source"],
    }
    level = TRENDS_LEVEL_OF[cid]
    year = cd.CB_VINTAGE[level]
    out["source-cartographic-boundaries"] = {
        "href": CB_LEVEL_URL[level],
        "type": "application/zip",
        "title": f"{year} cartographic boundary file — "
                 f"{LEVEL_PLURAL[level]} (1:500,000, national)",
        "description": (
            "The geometry both periods' rows join to — the current "
            "(2020-2024) boundary, used for both periods: a 2015-2019 "
            "predecessor whose geoid no longer exists under this "
            "boundary (Connecticut's 8 old counties, Alaska's "
            "Valdez-Cordova Census Area, every pre-2020-vintage tract "
            "that split) is not published as a row of its own — see "
            "`geo_change`. Served by census.gov."),
        "roles": ["source"],
    }
    if level == "tract":
        out["source-t10t20-crosswalk"] = {
            "href": f"{PUBLIC_BASE}/reference/crosswalks/t10t20-tract.parquet",
            "type": "application/vnd.apache.parquet",
            "title": "2010-to-2020 tract relationship (this catalog's own "
                     "reference/crosswalks collection)",
            "description": (
                "The block-level 2010-tract-to-2020-tract relationship "
                "this collection's `geo_change` classification is "
                "measured from, population-weighted by `catalog/blocks`' "
                "2020 block population apportioned by each block pair's "
                "land-area overlap (`arealand_int`). A collection this "
                "catalog already publishes, not re-fetched."),
            "roles": ["source"],
        }
        out["source-blocks-population"] = {
            # The collection document, not a data glob: an https glob does
            # not expand, and v0.3 keeps globs out of asset hrefs.
            "href": f"{PUBLIC_BASE}/blocks/collection.json",
            "type": "application/json",
            "title": "2020 Census block population (this catalog's own "
                     "blocks collection)",
            "description": (
                "The population weights behind the t10t20 crosswalk's "
                "apportionment, and behind the exact Connecticut "
                "old-county-to-new-planning-region county-level mapping "
                "(matched on the preserved 6-digit tract number, same "
                "as `docs/runbook.md`'s Connecticut fix elsewhere in "
                "this catalog)."),
            "roles": ["source"],
        }
    out["doc-comparing-acs"] = {
        "href": COMPARING_ACS,
        "type": "text/html",
        "title": "Comparing ACS Data — Census Bureau guidance",
        "description": (
            "The Census Bureau's own guidance on which ACS period pairs "
            "can be compared: non-overlapping 5-year periods (this "
            "collection's 2015-2019 and 2020-2024) can be; overlapping "
            "ones cannot, because shared sample years make a measured "
            "difference partly an artifact of the comparison itself."),
        "roles": ["metadata"],
    }
    out["doc-acs-handbook"] = {
        "href": ACS_HANDBOOK, "type": "text/html",
        "title": "Understanding and Using American Community Survey Data "
                 "— Census Bureau handbooks",
        "description": (
            "The Bureau's own guidance on what ACS estimates can and "
            "cannot support, including comparing estimates across "
            "vintages."),
        "roles": ["metadata"],
    }
    out["doc-acs-accuracy"] = {
        "href": ACS_ACCURACY, "type": "application/pdf",
        "title": "ACS Accuracy of the Data (2024, multiyear estimates)",
        "description": (
            "The source of the quadrature formula `chg_*_moe` applies to "
            "the difference of two periods' margins, and of every other "
            "margin-of-error formula this build applies."),
        "roles": ["metadata"],
    }
    out["doc-geo-glossary"] = _glossary_asset()
    return out


def source_assets(cid: str) -> dict:
    """Upstream `source` assets plus `metadata` documentation assets.

    `source` and not `data`: a client filtering on `data` should land on this
    catalog's GeoParquet, and the role also says these bytes live on a server
    this mirror does not control.
    """
    out: dict[str, dict] = {}
    if cid in REFERENCE_IDS:
        return _reference_source_assets(cid)
    if cid in DHC_IDS:
        return _dhc_source_assets(cid)
    if cid in TRENDS_IDS:
        return _trends_source_assets(cid)
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
            "The geometry this collection joins onto, shoreline-clipped and "
            "generalized for mapping. Only the join key, the name parts and "
            "the land-area field are kept; reprojected from NAD83 to "
            "EPSG:4326 with ogr2ogr."
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
    "network. Tiled to PMTiles with tylertoo as a census-geography pyramid, "
    "so coarse zooms carry a coarser census geography — counties, then "
    "tracts — with that geography's own official values, instead of a "
    "thinned sample of this collection's features; the collections small "
    "enough to draw nationally (counties, states, congressional districts) "
    "are tiled as real polygons at every zoom.")


REFERENCE_EXTRACTED = "2026-11-15"  # the day the reference/ sources were read


def _reference_processing_notes(cid: str) -> str:
    common = (
        f"Downloaded {REFERENCE_EXTRACTED} over plain HTTPS, no API key. "
        "GeoParquet written with the same path as the rest of this "
        "catalog (pyarrow, ZSTD, sized row groups, bbox covering column — "
        "tools/build_wide_themes.py documents the convention, verified "
        "against catalog/counties/county-income/county-income.parquet): "
        "`gpio convert geoparquet` reads the shapefile, keeping the "
        "source CRS (NAD83, EPSG:4269 — not reprojected, unlike the ACS "
        "collections' cartographic boundaries), then "
        "`gpio sort hilbert --add-bbox` writes the Hilbert-ordered file "
        "with the bbox covering metadata."
    )
    mtfcc_note = (
        f"`feature_type` decodes `mtfcc` through a table copied from the "
        f"2022 MAF/TIGER Feature Class Code PDF ({MTFCC_PDF_2022}), the "
        f"nearest published vintage to TIGER2024 — see this collection's "
        f"`doc-mtfcc` source asset. A code this build met that is not in "
        f"that table is left NULL rather than guessed at; none were, for "
        f"this collection's data (see docs/spec-reference-layers.md's "
        f"build report)."
    )
    if cid == "urban-areas":
        return "\n\n".join([
            f"Built from the single national `UAC20` shapefile "
            f"({TIGER}/UAC20/tl_2024_us_uac20.zip, 70 MB). " + common,
            "Every one of the 2,644 features carries MTFCC `G3500` and "
            "LSAD `67` (measured) — the 2020 Census urban area product "
            "has no urban/urbanized split, unlike its 2010 predecessor, "
            "so there is no categorical column to style on. The default "
            "style classes on `aland_sqkm` instead; see the description "
            "for the full note on this deviation from the original spec.",
            mtfcc_note,
        ])
    if cid == "landmarks-area":
        return "\n\n".join([
            f"Built from 56 state `AREALM` shapefiles "
            f"({TIGER}/AREALM/, 68 MB total) plus the one national `MIL` "
            f"shapefile ({TIGER}/MIL/tl_2024_us_mil.zip, 3 MB), unioned "
            f"into one table after each is converted independently. " +
            common,
            "`state` is the USPS code for the AREALM file each row's "
            "state zip was read from; MIL rows carry `state = NULL`, "
            "since MIL is one national file, not 56 state files, and has "
            "no state column of its own to carry forward. "
            "`landmark_kind` is `'landmark'` for every AREALM row and "
            "`'military'` for every MIL row — not read off any source "
            "column, since neither file has one. AREALM carries no "
            "`ALAND`/`AWATER`, so `aland_sqkm`/`awater_sqkm` are NULL on "
            "every `landmark` row; MIL has both, so every `military` row "
            "has them.",
            mtfcc_note,
        ])
    if cid == "landmarks-point":
        return "\n\n".join([
            f"Built from 56 state `POINTLM` shapefiles "
            f"({TIGER}/POINTLM/, 28 MB total), concatenated after each is "
            f"converted independently. " + common,
            "`state` is the USPS code for the file each row was read "
            "from.",
            mtfcc_note,
        ])
    # crosswalks
    return "\n\n".join([
        f"Downloaded {REFERENCE_EXTRACTED} over plain HTTPS from "
        f"{REL2020}/. Every subdirectory but `t10t20` ships one national "
        f"file per relationship (`*_natl.txt`); that is the file this "
        f"build reads for `tract`, `blkgrp`, `place`, `cousub`, `cbsa`, "
        f"`zcta520`, `ua`, `puma520` and `aiannh` — the per-state files "
        f"those nine subdirectories also publish are the same "
        f"relationship split into smaller pieces, so reading the "
        f"national file once is complete and the per-state files are "
        f"not read. `t10t20` is the one subdirectory with no national "
        f"file: its 52 per-state zips (`TAB2010_TAB2020_ST##.zip`) are "
        f"concatenated into `t10t20-tract.parquet`.",
        "Every file is pipe-delimited with a header row and read "
        "directly with DuckDB (`read_csv(..., delim='|', header=true)`); "
        "column names are lowercased on write and otherwise kept exactly "
        "as published. No geometry, no gpio step, no Hilbert sort — "
        "written straight to ZSTD-compressed Parquet with "
        "`ROW_GROUP_SIZE 20000`, the same row-group size the spatial "
        "write path uses, for consistency rather than necessity.",
    ])


DHC_BUILD_DATE = "2026-11-15"


def _dhc_processing_notes(cid: str) -> str:
    level = DHC_LEVEL_OF[cid]
    theme = DHC_THEME_OF[cid]
    sumlev = "150" if level == "bg" else "140"
    return "\n\n".join([
        f"Built {DHC_BUILD_DATE} from the 2020 Census DHC per-state zips "
        f"({DHC_FTP_DIR}), downloaded one state at a time and deleted "
        f"(zip and extract both) immediately after that state's rows "
        f"were pulled — the national DHC source is roughly 15 GB "
        f"compressed and several times larger extracted, so the build "
        f"never holds more than one state on disk. tools/build_dhc.py.",

        f"Per state: the geoheader (97 fields, Latin-1, same layout "
        f"PL 94-171 uses) is filtered to `SUMLEV = '{sumlev}'`, "
        f"`GEOCOMP = '00'` (the whole-geography total; block groups and "
        f"tracts carry no other geographic component, but state and "
        f"county records also carry urban/rural and housing-unit-count "
        f"variants under other `GEOCOMP` values, which this filter "
        f"excludes) and joined on `LOGRECNO` to the segment files "
        f"carrying {' and '.join(DHC_TABLES[theme])}. Field positions "
        f"were derived from the Census Bureau's own DHC Table Matrix "
        f"(`TABLE_ID`, `SEGMENT_NUMBER`, `TOTAL_RECORDS`, "
        f"`TABLE_SORT_ORDER` — cumulative field offsets within a "
        f"segment, the same scheme tools/build_blocks.py documents for "
        f"P.L. 94-171) and verified against the real field counts in "
        f"every segment file this build reads, not assumed from the "
        f"spreadsheet alone.",

        f"`GEOCODE` is the field trusted for the GEOID, matching "
        f"tools/build_blocks.py. Geometry is the same {cd.CB_VINTAGE[level]} "
        f"cartographic boundary file the ACS collections at this "
        f"geography join to (`{Path(CB_LEVEL_URL[level]).name}`), so a "
        f"DHC row and an ACS row for the same `geoid` always share the "
        f"same polygon; the join is driven by geometry, so a geography "
        f"with boundaries but no DHC row (there are none at bg/tract — "
        f"measured) would keep its row with NULL values rather than "
        f"disappear.",

        "Validated: every state's P12 `total_population` sum equals the "
        "state's published 2020 apportionment population exactly (state "
        "totals are held invariant by the disclosure avoidance system — "
        "not noised); `occupied_total` (H4) equals `total_households` "
        "(P16) and `total_population_p17` (P17) equals `total_population` "
        "(P12) on every state, exactly; `male_total + female_total` "
        "equals `total_population` on every state; three values "
        "cross-checked against data.census.gov (see the build report in "
        "docs/dhc-build-notes.md).",
    ])


def _trends_processing_notes(cid: str) -> str:
    level = TRENDS_LEVEL_OF[cid]
    tables = ", ".join(tables_for(cid))
    common = [
        f"Built 2026-11-16 from `tools/build_trends.py`, reading "
        f"{tables} from both the ACS 2015-2019 prototype summary file "
        f"({TRENDS_5YR_DATA_2019}) and the 2020-2024 production summary "
        f"file ({ACS_5YR_DATA}), both over plain HTTPS, no API key for "
        f"the bulk files.",

        "**Re-pinned, not assumed.** Every line number this catalog's "
        "`tools/specs.py` uses was re-checked against the 2019 "
        "prototype's own table shells before any 2019 value was read: "
        "all 55 shell pins and all 120 (table, line) pairs resolve to "
        "the SAME line with the SAME concept in both vintages. Two "
        "label changes only, neither a line move: B05002 line 13 reads "
        "\"Foreign born:\" in 2019 versus \"Foreign-born:\" in 2024 "
        "(a hyphen, normalized away rather than hardcoded), and B08301 "
        "line 10 drops a parenthetical in 2024 that the pin's substring "
        "match already tolerated.",

        "**Proven before anything depended on it.** The 2019 source is "
        "labelled a prototype, so it was validated against the Census "
        "API (`api.census.gov/data/2019/acs/acs5`) before this "
        "collection was built: 29 requests, stratified across state, "
        "county, 10 sampled states' full tract and block-group "
        "coverage (including Connecticut, Alaska and Puerto Rico), "
        "place, congressional district and a full national ZCTA pull — "
        "~4.66 million raw cell values compared, 0 mismatches.",

        "`geo_change` is measured the same way at every geography: "
        "population-weighted correspondence between the 2015-2019-"
        "vintage predecessor geography and the 2020-2024-vintage "
        "geography this catalog otherwise publishes, classified "
        "`identical` / `absorbed` / `subdivided` / `mixed` at a 99% "
        "population-share threshold each way (see the `geo_change` "
        "column description for the full rule). At county and state "
        "this needed real crosswalking in exactly two places, both "
        "measured by diffing the full set of county geoids each "
        "vintage's B01003 file carries: Connecticut's 8 old counties "
        "(2015-2019) versus 9 planning regions (2020-2024, effective "
        "2022, mapped on the preserved 6-digit tract number against "
        "`catalog/blocks`' 2020 population — exact, not estimated, "
        "since whole tracts move together at this level) and Alaska's "
        "Valdez-Cordova Census Area splitting into Chugach and Copper "
        "River (population-weighted, via the tract crosswalk below, "
        "since this is a genuine 2010-to-2020 boundary change the "
        "Census Bureau's own TIGER vintages already carry).",
    ]
    if level == "tract":
        common.append(
            "At tract level the crosswalk is the real one: 2010-vintage "
            "tracts (2015-2019's geography) do not nest inside "
            "2020-vintage tracts (2020-2024's geography, and every "
            "other tract collection in this catalog), so every 2015-2019 "
            "value is read through "
            "`catalog/reference/crosswalks/t10t20-tract.parquet`, a "
            "2010-block-to-2020-block relationship. Each 2020 block's "
            "actual 2020 population (`catalog/blocks`) is apportioned "
            "across its 2010-block predecessors by land-area share "
            "(`arealand_int`), summed to a (2010 tract, 2020 tract, "
            "weight) table, and classified at a 99% threshold both "
            "ways. `absorbed` sums the predecessors' raw census cells "
            "(not population-weighted — a legitimate whole-tract "
            "aggregation) and recomputes rates from the summed "
            "numerator and denominator; `identical`/`subdivided` carry "
            "the single dominant predecessor's own computed values. "
            "Connecticut tract geoids need one more step: both sides of "
            "the crosswalk predate the 2022 planning-region switch, so "
            "a classified 2020-side geoid is relabeled onto its current "
            "(2024 cartographic file) tract geoid by the same preserved-"
            "tract-number match the county-level fix uses, before the "
            "final output is written.")
    common.append(
        "`chg_<indicator>` is the 2020-2024 value minus the 2015-2019 "
        "value, computed once both periods' rows exist and carried on "
        "the 2020-2024 row only; `chg_<indicator>_moe` is the "
        "quadrature sum of the two periods' margins (ACS Accuracy of "
        "the Data's formula for the margin of a difference of two "
        "independent estimates).")
    common.append(
        f"Geometry is the same {cd.CB_VINTAGE[level]} cartographic "
        f"boundary file ({Path(CB_LEVEL_URL[level]).name}) the "
        f"2020-2024 themed ACS collections at this geography join to, "
        f"reused rather than re-fetched, for both periods' rows.")
    common.append(PROCESSING_COMMON)
    return "\n\n".join(common)


def processing_notes(cid: str) -> str:
    if cid in REFERENCE_IDS:
        return _reference_processing_notes(cid)
    if cid in DHC_IDS:
        return _dhc_processing_notes(cid)
    if cid in TRENDS_IDS:
        return _trends_processing_notes(cid)
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
        _pruned_para(cid),

        f"Built {EXTRACTED} from the ACS 2020–2024 5-year table-based "
        f"Summary File ({ACS_5YR_DATA}), downloaded the same day over plain "
        f"HTTPS — the summary file needs no API key. Tables read for this "
        f"collection: {tables}. Each national `.dat` file is one row per "
        f"geography with estimate and margin of error side by side, and "
        f"every summary level is picked off `GEO_ID` by prefix in a single "
        f"pass per file — this collection's is `{specs.LEVELS[level]}`, read "
        f"off the files themselves rather than taken from a summary-level "
        f"table"
        + (" (the `19` is the congress number)" if level == "cd" else
           " (the `Z2` is the 2020 ZCTA vintage)" if level == "zcta" else "")
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


def _pruned_para(cid: str) -> str:
    """How a themed chunk at a coarse level came to exist (2026-11-15).

    These five levels shipped as wide tables first. The themed chunks are
    those files with columns removed — not a second pass over the `.dat`
    files — so every value in a chunk is byte-identical to the wide table's,
    and the paragraphs below about the ACS read, the MOE formulas and the
    validation describe the build they were cut from.
    """
    group = GROUP_OF.get(cid)
    if cid in WIDE_IDS or group not in PRUNED_GROUPS:
        return ""
    wide = next(c for c in GROUPS[group] if c in WIDE_IDS)
    n = len(cd.columns_for(cid))
    return (
        f"This collection is a themed cut of "
        f"[{TITLES[wide]}](../{wide}/collection.json), the wide 135-column "
        f"table at this geography: the same rows, the same geometry and the "
        f"same seven context columns, with {n} columns kept and the other "
        f"themes' dropped. Nothing is recomputed — every value here is the "
        f"value in the wide file — so the build notes below describe the "
        f"single ACS read both were made from.")


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
        # Keyed by group, so a themed chunk pruned from one of these wide
        # tables reports the same validation — it is the same build.
    }.get(GROUP_OF.get(cid, cid), "")


# The Census Bureau's own median suppressions, by level, as a share of the
# collection's rows. The block-group and tract rates are the build's
# validation-pass counts (docs/acs-build-notes.md); the five coarse levels
# were counted with DuckDB over the published wide tables on 2026-11-15, the
# day the themed chunks were cut from them. Insertion order is the order they
# are listed in, overall medians before race iterations.
SUPPRESSED_MEDIANS = {
    "bg": {"median_hh_income": "7.69%", "median_gross_rent": "29.68%",
           "median_home_value": "10.03%"},
    "tract": {"median_hh_income": "1.59%", "median_gross_rent": "5.92%",
              "median_home_value": "3.55%",
              "median_hh_income_white_nh": "10.04%",
              "median_hh_income_hispanic": "44.43%",
              "median_hh_income_black": "61.43%",
              "median_hh_income_asian": "71.27%"},
    "county": {"median_hh_income": "0.43%", "median_gross_rent": "0.62%",
               "median_home_value": "0.56%",
               "median_hh_income_white_nh": "2.38%",
               "median_hh_income_hispanic": "19.60%",
               "median_hh_income_black": "39.47%",
               "median_hh_income_asian": "53.63%"},
    # At state level every value column is NULL on exactly the four
    # island-area rows, so there is nothing level-specific to report here;
    # the description's caveat says it once.
    "state": {},
    "zcta": {"median_hh_income": "9.60%", "median_gross_rent": "23.79%",
             "median_home_value": "10.45%",
             "median_hh_income_white_nh": "12.08%",
             "median_hh_income_hispanic": "58.55%",
             "median_hh_income_black": "69.25%",
             "median_hh_income_asian": "76.59%"},
    "place": {"median_hh_income": "12.71%", "median_gross_rent": "31.32%",
              "median_home_value": "12.78%",
              "median_hh_income_white_nh": "17.62%",
              "median_hh_income_hispanic": "69.35%",
              "median_hh_income_black": "79.24%",
              "median_hh_income_asian": "85.80%"},
    # Districts are big enough that every median is published everywhere the
    # ACS tabulates one: the only non-island gap is a single district with no
    # `median_hh_income_asian`.
    "cd": {"median_hh_income_asian": "1.13%"},
}

# The columns whose margin of error is NULL at county, state and
# congressional-district level: the total-population tables behind them
# (B01001, B01003, B03002, B05002, and B26001 at state level) publish no
# margin at these geographies, and the build propagates the NULL rather than
# inventing one. Counted with DuckDB over the published wide tables,
# 2026-11-15; at ZCTA, place, tract and block-group level the same columns
# carry margins normally.
MOE_GAP_COLUMNS = [
    "population", "pct_under_18", "pct_65_plus", "pct_white_nh", "pct_black",
    "pct_native", "pct_asian", "pct_hispanic", "pct_people_of_color",
    "pct_foreign_born",
]
MOE_GAP_TABLE = {
    "population": "B01003", "pct_under_18": "B01001",
    "pct_65_plus": "B01001", "pct_white_nh": "B03002",
    "pct_black": "B03002", "pct_native": "B03002", "pct_asian": "B03002",
    "pct_hispanic": "B03002", "pct_people_of_color": "B03002",
    "pct_foreign_born": "B05002", "group_quarters_pop": "B26001",
}
MOE_GAP_CARRIED = {
    "county": "132 of the 3,235 rows",
    "state": "none of the 56 rows",
    "cd": "423 of the 441 rows",
}
# `group_quarters_pop_moe` joins the family at state level only: 0 of 56
# rows, against 3,221 of 3,235 counties and 429 of 441 districts.
MOE_GAP_EXTRA = {"state": ["group_quarters_pop"]}

# Which rows do and do not carry one. Measured: at county level every one of
# the 132 has a population under 7,000; at congressional-district level the
# 18 without are the four island-area delegate districts (no ACS data at
# all), the six at-large districts, the DC delegate and Puerto Rico
# districts, all four of Iowa's and both of West Virginia's.
MOE_GAP_WHICH = {
    "county": "The 132 that carry one are the smallest counties in the "
              "country: every one has a population under 7,000 (measured).",
    "state": "",
    "cd": "The 18 without one are the four island-area delegate districts, "
          "which carry no ACS data at all, plus the six at-large districts, "
          "the District of Columbia delegate and Puerto Rico districts, all "
          "four of Iowa's and both of West Virginia's (measured).",
}

# Outside that family, the columns whose margin is NULL on rows where the
# estimate is published. Counted with DuckDB over the published wide tables,
# 2026-11-15: at state and congressional-district level there are none at
# all, and at county level there are these four.
MOE_RAGGED = {
    "county": {"pct_bachelors_plus": 99, "median_hh_income_black": 22,
               "median_hh_income_asian": 42,
               "median_hh_income_hispanic": 10},
    "state": {},
    "cd": {},
}


def _moe_source_phrase(n: int) -> str:
    return ("each column in the list above comes" if n > 1
            else "the column comes")


def _moe_elsewhere(n: int) -> str:
    return ("the same columns carry margins" if n > 1
            else "the same column carries a margin")


def _moe_exceptions(level: str, here: set) -> str:
    """Whether every other `*_moe` here is populated where its estimate is."""
    ragged = [(c, n) for c, n in MOE_RAGGED[level].items() if c in here]
    if not ragged:
        return ("Every other `*_moe` column in this collection is populated "
                "on every row where its estimate is — measured, with no "
                "exceptions.")
    listed = ", ".join(f"`{c}` on {n} rows" for c, n in ragged)
    return (f"Every other `*_moe` column in this collection is populated on "
            f"every row where its estimate is, except {listed} (measured).")


MEDIAN_SUPPRESSION_LEAD = {
    "bg": "Block-group medians are sparse where the sample is thin:",
    "tract": "Medians are suppressed where the sample behind them is too "
             "thin, and the race iterations are sparse by construction:",
    "county": "Medians are published for nearly every county; the race "
              "iterations are the exception:",
    "state": "",
    "zcta": "Medians thin out at this geography, because a ZCTA with few "
            "households, renter households or owner households has no "
            "publishable median:",
    "place": "Most rows are places too small for a published median:",
    "cd": "One gap, and it is the only median suppression at this geography:",
}


def _reference_known_issues(cid: str) -> str:
    if cid == "urban-areas":
        return (
            "There is no urban/urbanized-area class to style on. The "
            "2020 Census urban area product carries a single MTFCC "
            "(`G3500`) and a single LSAD (`67`) on every one of its "
            "2,644 features — the 2010-era `UATYP10` urban/urban-cluster "
            "split this build was originally asked to carry forward does "
            "not exist in `UAC20`. The default style classes on land "
            "area instead; see the collection's AGENTS.md for the exact "
            "breaks.")
    if cid == "landmarks-area":
        return (
            "`state` and `aland_sqkm`/`awater_sqkm` are NULL on different "
            "rows for different reasons, not the same reason: `state` is "
            "NULL on the 858 `landmark_kind = 'military'` rows (MIL is a "
            "national file with no per-state source to read a state "
            "from), while `aland_sqkm`/`awater_sqkm` are NULL on the "
            "119,876 `landmark_kind = 'landmark'` rows (AREALM carries no "
            "area fields at all). Filter on `landmark_kind`, not on "
            "whether a column is NULL, if you need one kind cleanly.")
    if cid == "landmarks-point":
        return (
            "Most of these points are not places. Measured nationally, "
            "the single largest `feature_type` is `Cul-de-sac` (668,308 "
            "of 1,088,085 points) followed by `Locality Point` (208,547) "
            "— both are address-system landmarks TIGER uses to resolve "
            "street addresses, not landmarks a person would look for on "
            "a map. Filter `feature_type` before treating this collection "
            "as a point-of-interest dataset.")
    # crosswalks
    return (
        "`t10t20-tract.parquet` is block-level (12,689,707 rows, "
        "measured), not tract-level, even though its job is mapping 2010 "
        "tracts to 2020 tracts — see the processing notes for why. A "
        "join on this file needs the state+county+tract columns, not a "
        "direct tract-to-tract key; there is no row that just says "
        "\"2010 tract X became 2020 tract Y\" for a tract that split or "
        "merged.")


def _dhc_known_issues(cid: str) -> str:
    theme = DHC_THEME_OF[cid]
    items = [
        f"**The 2020 Census applied differential privacy.** Every count "
        f"in this collection — not just the small ones — passed through "
        f"the Census Bureau's disclosure avoidance system, which injects "
        f"statistical noise calibrated to a privacy-loss budget. State "
        f"population totals are held exact; housing unit counts and major "
        f"group-quarters counts per block are held exact; everything "
        f"else, including the counts in this collection, can carry "
        f"injected noise, proportionally larger for a small count in a "
        f"small geography than for a large one. There is no column here "
        f"that quantifies that noise — see the Census Bureau's "
        f"[disclosure avoidance documentation]({DHC_DAS}) — so treat a "
        f"single block group's count with more caution than a tract's, "
        f"and a tract's with more caution than a state's.",

        "**This is a different measurement from the ACS collections "
        "beside it, not a finer or coarser version of the same one.** "
        "The ACS `*_moe`/`*_cv` columns describe sampling error in a "
        "5-year rolling survey; this collection has no sampling error "
        "and no margin of error because it is not a sample. Joining the "
        "two on `geoid` is fine; subtracting one's count from the "
        "other's estimate, or averaging them, treats two different "
        "measurements of two different things as if they disagreed "
        "about one.",
    ]
    if theme == "household":
        items.append(DHC_SPEC_NOTE)
    if theme == "age":
        items.append(
            "`total_population` (P12) is the same universe as "
            "`total_population_p17` in the household collection at this "
            "geography — both are the DHC's total population count — "
            "but neither is published in this collection under the ACS "
            "`population` column name, to keep a column-name join from "
            "silently crossing collections.")
    return "\n\n".join(items)


def _trends_known_issues(cid: str) -> str:
    level = TRENDS_LEVEL_OF[cid]
    ident, absorbed, subdiv, mixed, gap = TRENDS_GEO_CHANGE_COUNTS[level]
    total = ident + absorbed + subdiv + mixed + gap
    items = [
        "**Never apportioned.** Where `geo_change` says a period has no "
        "legitimate figure for a geoid (`mixed` always; `subdivided` "
        "for `population`/`households`; `absorbed` for the five "
        "medians; `no_acs_data` always), that cell is NULL. No value "
        "here was ever modelled, interpolated or carried over from a "
        "different geography and published as if it were a direct "
        "measurement.",

        "**A median cannot be derived from medians.** `absorbed` rows "
        "(several 2015-2019 predecessors combine into one 2020-2024 "
        "geoid) NULL `median_hh_income`, `per_capita_income`, "
        "`median_age`, `median_home_value` and `median_gross_rent` for "
        "2015-2019 for exactly this reason — summing the predecessors' "
        "raw census cells and recomputing is legitimate for counts "
        "and rates, and this build does it, but there is no published "
        "2015-2019 median for a geography the Census Bureau never "
        "tabulated directly, so inventing one by averaging or "
        "reweighting predecessor medians would be a model wearing a "
        "measurement's clothes.",

        "**`subdivided` carries an explicit assumption.** A "
        "`subdivided` geoid's rates and medians are its single "
        "dominant 2015-2019 predecessor's own published values, "
        "copied over under a part-resembles-whole assumption — the "
        "predecessor's overall rate or median is assumed to hold for "
        "the fragment too, which is not measured and can be wrong for "
        "a fragment that differs from its parent's average. "
        "`population` and `households` are NULL there instead of "
        "carrying the whole predecessor's count, which would overstate "
        "a fragment.",

        "**Measured `geo_change` distribution at this geography:** "
        f"`identical` {ident:,} ({100*ident/total:.1f}%)"
        + (f", `absorbed` {absorbed:,} ({100*absorbed/total:.1f}%)"
           if absorbed else "")
        + (f", `subdivided` {subdiv:,} ({100*subdiv/total:.1f}%)"
           if subdiv else "")
        + (f", `mixed` {mixed:,} ({100*mixed/total:.1f}%)" if mixed else "")
        + f", `no_acs_data` {gap:,} ({100*gap/total:.1f}%) of {total:,} "
          f"geoids.",

        "**The four dollar medians are not on a common dollar basis "
        "across the two periods, and `chg_median_hh_income`, "
        "`chg_per_capita_income`, `chg_median_home_value` and "
        "`chg_median_gross_rent` inherit that.** Each ACS release "
        "reports its dollar medians in ITS OWN vintage's inflation-"
        "adjusted dollars — `B19013` is titled \"...in 2019 inflation-"
        "adjusted dollars\" in the 2015-2019 release and \"...in 2024 "
        "inflation-adjusted dollars\" in the 2020-2024 release, exactly "
        "as published, not re-based to a common dollar-year by this "
        "build. A positive `chg_median_hh_income` mixes real change "
        "with five years of inflation, and it shows: measured at state "
        "level, 52 of 52 states show a nominal increase and 0 show a "
        "decrease, which is implausible as a real-income statement over "
        "five years for every single state and is this build's own "
        "evidence that the comparison is partly a dollar-basis effect, "
        "not a finding that incomes rose everywhere. This is why the "
        "collection's diverging style classifies on "
        "`chg_pct_below_poverty` (a percentage-point difference, immune "
        "to this) rather than on a dollar column. Deflate "
        "`median_hh_income`/`per_capita_income`/`median_home_value`/"
        "`median_gross_rent` to a common dollar-year yourself (e.g. CPI-"
        "U-RS) before treating any `chg_<dollar column>` as a real-"
        "dollar change.",
    ]
    if level == "county":
        items.append(
            "Connecticut and Alaska are the only two county-level "
            "geography changes this catalog measured between the two "
            "vintages (diffed off the full set of county geoids each "
            "vintage's B01003 file carries — nothing else moved). "
            "Connecticut's 9 planning regions split 2 ways: Greater "
            "Bridgeport (`09120`) and South Central Connecticut "
            "(`09170`) are `subdivided` (each a clean fragment of "
            "old Fairfield and New Haven counties respectively); the "
            "other 7 are `mixed` — Connecticut's planning regions were "
            "not drawn along the old county lines, so most of them "
            "blend population from more than one old county with no "
            "single county contributing 99% of either side. Alaska's "
            "Chugach (`02063`) and Copper River (`02066`) Census Areas "
            "are both `subdivided` fragments of the old Valdez-Cordova "
            "Census Area.")
    if level == "tract":
        items.append(
            "Connecticut's tract **numbers** do not change in 2022 — "
            "only the county prefix does — so a Connecticut tract's "
            "`geo_change` category is measured the same way as any "
            "other state's; only its published `geoid` gets relabeled "
            "onto the current planning-region prefix after "
            "classification. A tract with no measured 2010 lineage at "
            "all (a handful of water-only or newly-platted 2020 tracts "
            "with zero population weight in the crosswalk) is "
            "classified `mixed` rather than guessed at.")
        items.append(
            "This is the one geography in the catalog where `mixed` is "
            "a meaningful share (3.6%) rather than a near-zero edge "
            "case: a fifth of 2020 tracts overlap more than one 2010 "
            "predecessor at all (absorbed + subdivided + mixed ≈ 31%), "
            "and most of those overlaps are clean enough to carry a "
            "legitimate figure forward. Filter on `geo_change` before "
            "computing a national or state-level 2015-2019 statistic "
            "from this file; the measured distribution above is the "
            "honest accounting of how much of this tier is a real "
            "measurement versus how much had to go NULL.")
    items.append(TRENDS_OVERLAP_NOTE)
    items.append(
        "This group carries 12 of the catalog's ~135 ACS indicators. "
        "For every other indicator, or for a 2020-2024-only question "
        "with no time dimension, use the current-vintage themed "
        "collections at this geography instead — they are not a finer "
        "or coarser version of these numbers, they are the same survey "
        "at the same geography with the rest of the columns.")
    return "\n\n".join(items)


def known_issues(cid: str) -> str:
    if cid in REFERENCE_IDS:
        return _reference_known_issues(cid)
    if cid in DHC_IDS:
        return _dhc_known_issues(cid)
    if cid in TRENDS_IDS:
        return _trends_known_issues(cid)
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

            "PMTiles coarse zooms are a different census geography from this "
            "collection's: below z10 you are looking at counties and tracts, "
            "not blocks. Those bands carry exact sums of the block counts "
            "(rates recomputed from the summed counts), so they are "
            "consistent with the data — but the geometry and the `geoid` "
            "belong to the county or tract. Statistics come from the "
            "GeoParquet.",

            "Connecticut needs a crosswalk in those coarse bands. The 2020 "
            "block GEOIDs carry Connecticut's old 8-county prefixes "
            "(09001–09015), while the 2024 boundaries used for the county "
            "and tract bands are the 9 planning regions (09110–09190) that "
            "replaced them as the county equivalent in 2022. The build "
            "matches blocks to current geographies on the 6-digit tract "
            "number, which is preserved across the change, so no Connecticut "
            "population is dropped: the aggregates still sum to the "
            "published national block total of 334,735,155 exactly. The "
            "block rows themselves are untouched — they keep the 2020 "
            "GEOIDs, so a 5-character prefix join from Connecticut blocks to "
            "the 2024-vintage counties collection finds no match.",
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
    if level == "zcta":
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
            "Two ZCTAs — 11717 and 11798, in Suffolk County, New York — have "
            "2020 boundaries but no row in this ACS tabulation and publish "
            "with NULL values; they are the same two communities (Brentwood "
            "and Wyandanch) that the re-delineated Suffolk County tracts and "
            "block groups show up in elsewhere in this catalog.")
    if level == "place":
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
            "Most rows are small places. Filter on `population` before "
            "reading a place-level distribution as if every row were a city, "
            "and expect the suppression rates below.")
        items.append(
            "Three non-island places carry geometry and no ACS row: "
            "Brentwood CDP (`3608026`) and Wyandanch CDP (`3683294`) in "
            "Suffolk County, New York, and Louisville city, Kentucky "
            "(`2148000`), whose ACS tabulation is the consolidated "
            "`2148006` Louisville/Jefferson County metro government "
            "(balance) — if you want Louisville, use `2148006`.")
    if level == "cd":
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
            "across the 435 voting districts, 771,301 at the median of all "
            "437 rows with data — Puerto Rico's single Resident Commissioner "
            "district is the outlier at 3,234,309), so the spread of every "
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
    here = set(cd.columns_for(cid))
    if level in MOE_GAP_CARRIED:
        gap = [c for c in MOE_GAP_COLUMNS + MOE_GAP_EXTRA.get(level, [])
               if c in here]
        tables = ", ".join(sorted({MOE_GAP_TABLE[c] for c in gap}))
        carried = MOE_GAP_CARRIED[level]
        if len(gap) == 1:
            how = ("every row" if level == "state"
                   else "almost every row" if level == "county"
                   else "4.08% of rows")
            head = (f"**`population_moe` is NULL on {how} at this "
                    f"geography.** Measured: carried on {carried}.")
        else:
            listed = ", ".join(f"`{c}_moe`" for c in gap[:-1])
            head = (f"**A family of margins is NULL at this geography, and "
                    f"`population_moe` is only the visible one.** Measured: "
                    f"{listed} and `{gap[-1]}_moe` are carried on "
                    f"{carried}.")
        items.append(
            f"{head} {MOE_GAP_WHICH[level]}"
            f"{' ' if MOE_GAP_WHICH[level] else ''}"
            f"`sqrt(sum(moe*moe))` over a "
            f"NULL-bearing column returns NULL, so check before putting one "
            f"in a quadrature sum, and read "
            f"{'these estimates' if len(gap) > 1 else 'this count'} as "
            f"something to use rather than as an estimate to put an interval "
            f"on. {_moe_exceptions(level, here)}")
        items.append(
            f"That NULL is upstream, and it is not suppression: "
            f"{_moe_source_phrase(len(gap))}"
            f" from a total-population table ({tables}), and in the "
            f"release's own `.dat` files those rows carry the estimate "
            f"beside `-555555555`, the **controlled-MOE** jam value a "
            f"controlled estimate gets in place of a sampling margin. The "
            f"build turns it into NULL rather than publishing it as a number "
            f"— `0500000US01001|59947|-555555555` in "
            f"`acsdt5y2024-b01003.dat`, read 2026-11-15. "
            f"{_moe_elsewhere(len(gap)).capitalize()} normally at the finer "
            f"geographies, where the estimates are not controlled this way: "
            f"`population_moe` is carried on 33,759 of 33,791 ZCTAs and on "
            f"all 241,854 populated block groups (measured).")
    if level == "bg" and "per_capita_income" in here:
        items.append(
            "`per_capita_income` is incomplete upstream: B19301 "
            "publishes 242,069 block-group rows against 242,297 for "
            "B01003, and the missing 228 come through as NULL.")
    if level == "bg" and cid == "bg-income":
        items.append(
            "**Three income-depth columns do not exist at block-group "
            "level, and that is a Census Bureau publication gap, not a "
            "build error.** B19083 (Gini index) and B17001 (poverty status "
            "by age) carry no `1500000US`-prefixed rows in this release's "
            "`.dat` files — every other summary level this catalog uses is "
            "present in both files, block groups are the one exception "
            "(measured 2026-11-15 against "
            "`staging/census-cache/acsdt5y2024-b19083.dat` and "
            "`-b17001.dat`). `gini_index`, `pct_below_poverty_under_18` and "
            "`pct_below_poverty_65_plus` are omitted from this collection's "
            "schema entirely rather than published as all-NULL columns; "
            "`tract-income` and every coarser income collection carries all "
            "three. Household income bands (`pct_income_*`, from B19001) "
            "and `median_earnings` (B20002) ARE published at block-group "
            "level and are carried here.")
    # Only the medians this collection actually carries: a known-issues list
    # that names a column the file does not have is noise at best.
    sparse = [(c, r) for c, r in SUPPRESSED_MEDIANS[level].items()
              if c in here]
    if sparse:
        listed = ", ".join(f"`{c}` on {r} of rows" for c, r in sparse)
        text = (f"{MEDIAN_SUPPRESSION_LEAD[level]} NULL for {listed} "
                f"(measured). These are the Census Bureau's own suppressions, "
                f"reported rather than patched.")
        if any(c.startswith("median_hh_income_") for c, _ in sparse):
            text += (" A map of a race-iteration median is as much a map of "
                     "where that group lives as of its income, and quoting a "
                     "racial income gap without its denominator overstates "
                     "the coverage.")
        items.append(text)
    if level == "cd":
        # Measured over this file: the highest median coefficient of
        # variation on any `*_cv` column at this geography is 0.101
        # (`pct_commute_transit`). Reusing the small-area warning here would
        # be false modesty about the most reliable file in the catalog — but
        # "no district above 0.30" holds only for the wide table's styled
        # columns (docs/style-breaks.json): `cd-connectivity` has one
        # district above it on `pct_commute_transit` and `cd-wellbeing`
        # three on `median_hh_income_black`.
        text = ("Margins of error are the narrowest in this catalog — a "
                "district is ~770,000 people — and every `*_cv` column at "
                "this geography has a median coefficient of variation below "
                "0.11 (measured).")
        if cid in WIDE_IDS:
            text += (" No styled column has a single district with a "
                     "coefficient of variation above 0.30.")
        items.append(
            text + " They are still margins: check whether two districts' "
            "margins overlap before calling a difference real, and never "
            "aggregate a median.")
    elif level == "state":
        # Measured: the widest median coefficient of variation on any column
        # here is 0.037 (`pct_commute_transit`) and the widest single value
        # 0.213 (`pct_below_poverty_black`). The small-area warning the finer
        # collections carry would be false on this file.
        items.append(
            "Margins of error are negligible at this geography — no column "
            "has a median coefficient of variation above 0.037, and no "
            "single value above 0.213 (measured), so nothing here needs a "
            "reliability filter. They are still margins: check whether two "
            "states' margins overlap before calling a difference real, and "
            "never aggregate a median. A state's value is estimated directly "
            "by the Census Bureau and is not the sum or the average of its "
            "counties.")
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
            "coarser-geography coarse-zoom band (the catalog's finer "
            "collections switch to counties and tracts at coarse zooms; this "
            "one has few enough features not to). `*_moe` columns are not in "
            "the tiles — statistics come from the GeoParquet.")
    else:
        p = PYRAMID[LEVEL_OF[cid]]
        items.append(
            f"PMTiles coarse zooms are a different census geography from "
            f"this collection's: {p['not']}. The values there are the "
            f"Census Bureau's own estimates for those geographies, not an "
            f"aggregation of this file, and `*_moe` columns are not in the "
            f"tiles. Statistics come from the GeoParquet.")
    return "\n\n".join(items)


REFERENCE_SOURCE_URL = {
    "urban-areas": f"{TIGER}/UAC20/",
    "landmarks-area": f"{TIGER}/AREALM/",
    "landmarks-point": f"{TIGER}/POINTLM/",
    "crosswalks": f"{REL2020}/",
}


def source_url(cid: str) -> str:
    if cid in REFERENCE_IDS:
        return REFERENCE_SOURCE_URL[cid]
    if cid in DHC_IDS:
        return DHC_FTP_DIR
    if cid in TRENDS_IDS:
        # The current (2020-2024) release, for the single-URL field every
        # other collection's metadata.yaml carries; the 2015-2019
        # prototype directory is the collection's `source-2019-*` assets
        # and processing_notes, not this field.
        return ACS_5YR_DATA
    return PL_DIR if cid == "blocks" else ACS_5YR_DATA


def _yq(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _block(key: str, text: str) -> str:
    lines = [f"{key}: |"]
    for line in text.split("\n"):
        lines.append(f"  {line}" if line else "")
    return "\n".join(lines)


def data_url(cid: str, ext: str = "parquet") -> str:
    """The published URL of a collection's data file.

    The one place that knows the wide tables' files did not move when their
    metadata did: `catalog/<group>/<id>/collection.json` describes bytes that
    sit at `catalog/<group>/<id>.parquet`, one directory up, so every data URL
    this catalog has ever published keeps working. Everything else — themed
    chunks at every geography — is `<group>/<id>/<id>.<ext>`.
    """
    if cid == "blocks":
        return f"{PUBLIC_BASE}/blocks/state_fips=*/*.parquet"
    if cid == "crosswalks":
        return f"{PUBLIC_BASE}/{COLL_REL[cid]}/*.parquet"
    if cid in WIDE_IDS:
        return f"{PUBLIC_BASE}/{GROUP_OF[cid]}/{cid}.{ext}"
    return f"{PUBLIC_BASE}/{COLL_REL[cid]}/{cid}.{ext}"


def metadata_yaml(cid: str) -> str:
    """`.portolan/metadata.yaml` for one collection."""
    data_href = data_url(cid)
    example = (
        "INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';\n"
        "SET s3_url_style='path';\n"
        "SELECT geoid, pop_total, housing_units FROM read_parquet("
        "'s3://us-west-2.opendata.source.coop/portolan-mirrors/"
        "us-census-catalog/blocks/state_fips=*/*.parquet', "
        "hive_partitioning=true) LIMIT 5;"
        if cid == "blocks" else
        f"INSTALL httpfs; LOAD httpfs;\nSELECT * FROM "
        f"'{PUBLIC_BASE}/{COLL_REL[cid]}/t10t20-tract.parquet' LIMIT 5; "
        f"-- one of 29 tables; see source_url for the rest"
        if cid == "crosswalks" else
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
  districts of the 119th Congress. Thirty-nine collections carry curated
  [American Community Survey]({ACS_PROGRAM})
  2020–2024 5-year indicators — income, poverty, age, race and ethnicity,
  education, housing cost and tenure, vehicles, commuting, internet access,
  health insurance, disability, nativity — every estimate with its margin of
  error at the 90% confidence level and the headline statistics with a
  coefficient of variation. Every geography is a sub-catalog of themed
  collections (income, people, housing, connectivity, wellbeing), and the
  five coarse-or-sparse geographies — counties, states, ZCTAs, places,
  congressional districts — add a sixth collection carrying all 135 columns
  in one wide table. One further collection carries 2020 Decennial Census
  P.L. 94-171 counts at block level, hive-partitioned by state. Six more,
  beside the block-group and tract ACS collections, carry curated 2020
  Census Demographic and Housing Characteristics (DHC) counts — age & sex,
  household type and tenure — 100% counts with no margin of error and no
  sampling error, protected instead by the Census Bureau's differential-
  privacy disclosure avoidance system.
  Explore it all interactively — change maps, 2015–2019 / 2020–2024
  comparison and place search — in the [Census Atlas]({ATLAS}), the
  catalog's own map explorer.
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
            # A collection whose data is still being built: write the
            # metadata anyway, so `portolan add` has it the moment the
            # parquet lands. Creating the directory is the whole cost.
            print(f"+ creating collection directory: {COLL_REL[cid]}")
            coll_dir.mkdir(parents=True)
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
