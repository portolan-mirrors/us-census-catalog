#!/usr/bin/env python3
"""Column specs and shell pinning for the national ACS build.

Ported from the St. Louis catalog's tools/fetch_census.py (BG_SPEC /
TRACT_SPEC, check_shell, the MOE machinery) and widened to the whole
country. The St. Louis catalog publishes one block-group table and one
tract table; a national catalog of the same width would be a 60-column,
242,000-row file for every consumer who only wanted median income, so the
columns are split into themed collections instead (income, people,
housing, connectivity, wellbeing) and the two coarse levels — counties and
states — carry every column in one wide table, because at 3,235 and 56
rows width costs nothing.

Everything about a column lives in one Spec tuple: which table it reads,
which lines, which denominator, the (table, line, label) pin that fails
the build if a vintage moves a line, and whether it gets a coefficient of
variation. Nothing else in the build knows a line number.

Line numbers are pinned against the release's own table-shells file, so a
vintage bump that renumbers a line fails loudly instead of publishing a
mislabeled column. The age, insurance and disability line groups are
resolved FROM the shells (they appear once per sex, and per age band)
rather than hardcoded.
"""

import csv
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "staging" / "census-cache"
BUILD = ROOT / "staging" / "acs-build"

ACS_RELEASE = "20245YR"  # ACS 2020-2024 5-year estimates
SHELLS = CACHE / f"ACS{ACS_RELEASE}_Table_Shells.txt"

Z90 = 1.645       # ACS margins of error are published at 90% confidence
JAM = -111111111  # any value at or below this is an ACS jam code, not data

# Summary-level prefixes on GEO_ID in the table-based Summary File. One pass
# per .dat file extracts every level asked for (the biggest file is 200 MB).
#
# Every prefix below was read OFF the cached .dat files rather than from a
# summary-level table: `python3 -c` over acsdt5y2024-b19013.dat, counting
# GEO_ID prefixes, gives 1500000US 242,297 / 1400000US 85,382 / 0500000US
# 3,222 / 0400000US 52 / 860Z200US 33,772 / 1600000US 32,330 / 5001900US 440.
# The three wave-3 prefixes carry a component that is not zero-padding:
#   860Z200US  ZCTA5, "Z2" = the 2020-based ZCTA vintage (summary level 860)
#   1600000US  place — incorporated places and census designated places
#   5001900US  congressional district, "19" = the 119th Congress
# See docs/acs-build-notes.md, "Wave 3".
LEVELS = {
    "bg": "1500000US",
    "tract": "1400000US",
    "county": "0500000US",
    "state": "0400000US",
    "zcta": "860Z200US",
    "place": "1600000US",
    "cd": "5001900US",
}

# STATEFP -> USPS. Embedded rather than read off the boundary files because
# the 2024 block-group shapefile carries no STUSPS column (the tract, county
# and state files do), and every collection publishes the same `state` code.
STATE_USPS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
    # Territories. Puerto Rico is in the ACS 5-year release; the other four
    # have cartographic boundaries but no ACS 5-year data (Island Areas run
    # their own decennial-only program), so their rows publish with NULL
    # estimates. See docs/acs-build-notes.md.
    "60": "AS", "66": "GU", "69": "MP", "72": "PR", "78": "VI",
}


class Spec(NamedTuple):
    """One published column (plus its _moe, and _cv when cv is set).

    kind:
      count      — sum of `lines`; MOE adds in quadrature; published as int
      median     — one line published as-is (medians never aggregate)
      pct        — 100 * sum(lines) / den; Census proportion/ratio MOE
      complement — 100 - `source`, carrying the source's own MOE
    den is (table, plus_lines, minus_lines); minus covers denominators like
    B25070's "excluding rent not computed". check is the (table, line, label)
    pin verified against this vintage's table shells.
    """
    name: str
    kind: str
    table: str
    lines: object = None
    den: tuple | None = None
    check: tuple | None = None
    cv: bool = False
    source: str | None = None


# --------------------------------------------------------------------------
# Themed column specs
# --------------------------------------------------------------------------

CONTEXT_SPEC = [
    Spec("population", "count", "B01003", [1], None, ("B01003", 1, "Total")),
]

#   B17001 (Poverty Status in the Past 12 Months by Sex by Age) bins ages in
# a non-standard scheme: Under 5, 5, 6 to 11, 12 to 14, 15, 16 and 17, 18 to
# 24, 25 to 34, 35 to 44, 45 to 54, 55 to 64, 65 to 74, 75 and over — each
# label occurring four times (below-poverty male, below-poverty female,
# at-or-above male, at-or-above female), ascending in that order. The two
# "below poverty" occurrences of a label are its numerator lines; all four
# are the "for whom poverty status is determined" denominator for that age
# band. `poverty_lines` resolves both from the shells rather than trusting
# four hand-counted integers per label, and `check_all_shells` recomputes
# the literal line lists below against it so a vintage that renumbers one
# fails the build instead of silently shifting a child- or senior-poverty
# rate.
POV_CHILD_LABELS = ["Under 5 years", "5 years", "6 to 11 years",
                    "12 to 14 years", "15 years", "16 and 17 years"]
POV_SENIOR_LABELS = ["65 to 74 years", "75 years and over"]

# Literal line numbers for this vintage (ACS20245YR), derived once by the
# same exact-label logic `poverty_lines` applies at build time — see
# check_all_shells, which recomputes and compares. Only `check_all_shells`
# needs to call `poverty_lines`; Spec.den is a plain tuple at import time
# everywhere else in this module, and these stay consistent with that.
POV_CHILD_BELOW = [4, 5, 6, 7, 8, 9, 18, 19, 20, 21, 22, 23]
POV_CHILD_TOTAL = [4, 5, 6, 7, 8, 9, 18, 19, 20, 21, 22, 23,
                   33, 34, 35, 36, 37, 38, 47, 48, 49, 50, 51, 52]
POV_SENIOR_BELOW = [15, 16, 29, 30]
POV_SENIOR_TOTAL = [15, 16, 29, 30, 44, 45, 58, 59]

INCOME_SPEC = [
    Spec("median_hh_income", "median", "B19013", [1], None,
         ("B19013", 1, "Median household income"), cv=True),
    Spec("per_capita_income", "median", "B19301", [1], None,
         ("B19301", 1, "Per capita income")),
    Spec("pct_below_poverty", "pct", "C17002", [2, 3], ("C17002", [1], []),
         ("C17002", 2, "Under .50"), cv=True),
    Spec("pct_below_2x_poverty", "pct", "C17002", [2, 3, 4, 5, 6, 7],
         ("C17002", [1], []), ("C17002", 8, "2.00 and over")),
    Spec("pct_snap", "pct", "B22010", [2], ("B22010", [1], []),
         ("B22010", 2, "Household received Food Stamps/SNAP")),
    Spec("pct_unemployed", "pct", "B23025", [5], ("B23025", [3], []),
         ("B23025", 5, "Unemployed")),
    # Household income distribution: B19001's 16 published brackets,
    # collapsed to 7 shares. Published at every summary level this catalog
    # uses, block groups included (measured against the cached .dat file).
    Spec("pct_income_under_25k", "pct", "B19001", [2, 3, 4, 5],
         ("B19001", [1], []), ("B19001", 2, "Less than $10,000")),
    Spec("pct_income_25_50k", "pct", "B19001", [6, 7, 8, 9, 10],
         ("B19001", [1], []), ("B19001", 6, "$25,000 to $29,999")),
    Spec("pct_income_50_75k", "pct", "B19001", [11, 12],
         ("B19001", [1], []), ("B19001", 11, "$50,000 to $59,999")),
    Spec("pct_income_75_100k", "pct", "B19001", [13],
         ("B19001", [1], []), ("B19001", 13, "$75,000 to $99,999")),
    Spec("pct_income_100_150k", "pct", "B19001", [14, 15],
         ("B19001", [1], []), ("B19001", 14, "$100,000 to $124,999")),
    Spec("pct_income_150_200k", "pct", "B19001", [16],
         ("B19001", [1], []), ("B19001", 16, "$150,000 to $199,999")),
    Spec("pct_income_200k_plus", "pct", "B19001", [17],
         ("B19001", [1], []), ("B19001", 17, "$200,000 or more")),
    Spec("median_earnings", "median", "B20002", [1], None,
         ("B20002", 1, "Total:"), cv=True),
    # Gini index of income inequality. Not published for block groups —
    # measured against the cached .dat file, see INCOME_SPEC_BG below — so
    # this Spec is in the full INCOME_SPEC only.
    Spec("gini_index", "median", "B19083", [1], None,
         ("B19083", 1, "Gini Index")),
    # Poverty by age. Also not published for block groups; see
    # INCOME_SPEC_BG.
    Spec("pct_below_poverty_under_18", "pct", "B17001", POV_CHILD_BELOW,
         ("B17001", POV_CHILD_TOTAL, []), ("B17001", 4, "Under 5 years")),
    Spec("pct_below_poverty_65_plus", "pct", "B17001", POV_SENIOR_BELOW,
         ("B17001", POV_SENIOR_TOTAL, []), ("B17001", 15, "65 to 74 years")),
]

# Block groups carry a restricted ACS table set: B19083 (Gini index) and
# B17001 (poverty by age) are not published at block-group level (measured
# against staging/census-cache/acsdt5y2024-b19083.dat and -b17001.dat: both
# files carry every summary-level prefix this catalog uses EXCEPT
# 1500000US, the block-group prefix — checked 2026-11-15). Household income
# bands (B19001) and median earnings (B20002) ARE published at block-group
# level, so only the three columns below are held back. See the bg-income
# collection's known_issues for this.
_BG_OMIT = {"gini_index", "pct_below_poverty_under_18",
           "pct_below_poverty_65_plus"}
INCOME_SPEC_BG = [s for s in INCOME_SPEC if s.name not in _BG_OMIT]

PEOPLE_SPEC = [
    Spec("median_age", "median", "B01002", [1], None,
         ("B01002", 1, "Total")),
    Spec("pct_under_18", "pct", "B01001", "UNDER18", ("B01001", [1], []),
         ("B01001", 1, "Total")),
    Spec("pct_65_plus", "pct", "B01001", "OVER65", ("B01001", [1], []),
         ("B01001", 1, "Total")),
    Spec("pct_white_nh", "pct", "B03002", [3], ("B03002", [1], []),
         ("B03002", 3, "White alone")),
    Spec("pct_black", "pct", "B03002", [4], ("B03002", [1], []),
         ("B03002", 4, "Black or African American alone")),
    Spec("pct_native", "pct", "B03002", [5], ("B03002", [1], []),
         ("B03002", 5, "American Indian")),
    Spec("pct_asian", "pct", "B03002", [6], ("B03002", [1], []),
         ("B03002", 6, "Asian alone")),
    Spec("pct_hispanic", "pct", "B03002", [12], ("B03002", [1], []),
         ("B03002", 12, "Hispanic or Latino")),
    # The complement of non-Hispanic white alone. A complement carries the
    # same margin of error as the share it is taken from.
    Spec("pct_people_of_color", "complement", "B03002",
         source="pct_white_nh"),
    Spec("pct_bachelors_plus", "pct", "B15003", [22, 23, 24, 25],
         ("B15003", [1], []), ("B15003", 22, "Bachelor's degree")),
]

HOUSING_SPEC = [
    Spec("housing_units", "count", "B25002", [1], None,
         ("B25002", 1, "Total")),
    Spec("pct_vacant_units", "pct", "B25002", [3], ("B25002", [1], []),
         ("B25002", 3, "Vacant")),
    Spec("households", "count", "B25003", [1], None,
         ("B25003", 1, "Total")),
    Spec("pct_owner_occupied", "pct", "B25003", [2], ("B25003", [1], []),
         ("B25003", 2, "Owner occupied")),
    Spec("median_gross_rent", "median", "B25064", [1], None,
         ("B25064", 1, "Median gross rent"), cv=True),
    Spec("pct_rent_burdened", "pct", "B25070", [7, 8, 9, 10],
         ("B25070", [1], [11]), ("B25070", 7, "30.0 to 34.9 percent"),
         cv=True),
    Spec("pct_severely_rent_burdened", "pct", "B25070", [10],
         ("B25070", [1], [11]), ("B25070", 10, "50.0 percent or more")),
    Spec("median_home_value", "median", "B25077", [1], None,
         ("B25077", 1, "Median value"), cv=True),
    Spec("pct_built_pre_1940", "pct", "B25034", [11], ("B25034", [1], []),
         ("B25034", 11, "Built 1939 or earlier")),
    Spec("pct_single_family", "pct", "B25024", [2, 3], ("B25024", [1], []),
         ("B25024", 2, "1, detached")),
]

CONNECTIVITY_SPEC = [
    Spec("hh_no_vehicle", "count", "B25044", [3, 10], None,
         ("B25044", 3, "No vehicle available")),
    Spec("pct_hh_no_vehicle", "pct", "B25044", [3, 10],
         ("B25044", [1], []), ("B25044", 10, "No vehicle available"),
         cv=True),
    Spec("pct_commute_drive_alone", "pct", "B08301", [3],
         ("B08301", [1], []), ("B08301", 3, "Drove alone")),
    Spec("pct_commute_transit", "pct", "B08301", [10], ("B08301", [1], []),
         ("B08301", 10, "Public transportation"), cv=True),
    Spec("pct_commute_walk_bike", "pct", "B08301", [18, 19],
         ("B08301", [1], []), ("B08301", 19, "Walked")),
    Spec("pct_work_from_home", "pct", "B08301", [21], ("B08301", [1], []),
         ("B08301", 21, "Worked from home")),
    Spec("pct_commute_45min_plus", "pct", "B08303", [11, 12, 13],
         ("B08303", [1], []), ("B08303", 11, "45 to 59 minutes")),
    Spec("pct_no_internet", "pct", "B28002", [13], ("B28002", [1], []),
         ("B28002", 13, "No Internet access"), cv=True),
    Spec("pct_no_computer", "pct", "B28001", [11], ("B28001", [1], []),
         ("B28001", 11, "No Computer")),
]

# Tract and coarser only: the detailed-race median-income tables and the
# insurance/disability tables are not published for block groups.
WELLBEING_SPEC = [
    Spec("pct_uninsured", "pct", "B27001", "NOINS", ("B27001", [1], []),
         ("B27001", 1, "Total"), cv=True),
    Spec("pct_with_disability", "pct", "B18101", "DISAB",
         ("B18101", [1], []), ("B18101", 1, "Total"), cv=True),
    Spec("pct_foreign_born", "pct", "B05002", [13], ("B05002", [1], []),
         ("B05002", 13, "Foreign-born")),
    Spec("group_quarters_pop", "count", "B26001", [1], None,
         ("B26001", 1, "Total")),
    Spec("median_hh_income_black", "median", "B19013B", [1], None,
         ("B19013B", 1, "Median household income"), cv=True),
    Spec("median_hh_income_white_nh", "median", "B19013H", [1], None,
         ("B19013H", 1, "Median household income"), cv=True),
    Spec("median_hh_income_asian", "median", "B19013D", [1], None,
         ("B19013D", 1, "Median household income"), cv=True),
    Spec("median_hh_income_hispanic", "median", "B19013I", [1], None,
         ("B19013I", 1, "Median household income"), cv=True),
    Spec("pct_below_poverty_black", "pct", "B17020B", [2],
         ("B17020B", [1], []),
         ("B17020B", 2, "below poverty level"), cv=True),
]

ALL_SPEC = (INCOME_SPEC + PEOPLE_SPEC + HOUSING_SPEC + CONNECTIVITY_SPEC
            + WELLBEING_SPEC)


class Collection(NamedTuple):
    group: str | None  # catalog subdirectory, None for the coarse levels
    id: str
    level: str
    spec: list


COLLECTIONS = [
    Collection("block-groups", "bg-income", "bg", INCOME_SPEC_BG),
    Collection("block-groups", "bg-people", "bg", PEOPLE_SPEC),
    Collection("block-groups", "bg-housing", "bg", HOUSING_SPEC),
    Collection("block-groups", "bg-connectivity", "bg", CONNECTIVITY_SPEC),
    Collection("tracts", "tract-income", "tract", INCOME_SPEC),
    Collection("tracts", "tract-people", "tract", PEOPLE_SPEC),
    Collection("tracts", "tract-housing", "tract", HOUSING_SPEC),
    Collection("tracts", "tract-connectivity", "tract", CONNECTIVITY_SPEC),
    Collection("tracts", "tract-wellbeing", "tract", WELLBEING_SPEC),
    # Every coarse-or-sparse level is a group too (2026-11-15): the five
    # themed chunks mirror the tract set so the whole catalog reads
    # uniformly, and the original wide table stays as a sixth child. The
    # wide table keeps its id and its data files: the parquet and pmtiles
    # stay one directory up (catalog/<group>/<id>.parquet), referenced
    # from the moved collection.json with ../ hrefs, so every published
    # data URL keeps working.
    Collection("counties", "county-income", "county", INCOME_SPEC),
    Collection("counties", "county-people", "county", PEOPLE_SPEC),
    Collection("counties", "county-housing", "county", HOUSING_SPEC),
    Collection("counties", "county-connectivity", "county", CONNECTIVITY_SPEC),
    Collection("counties", "county-wellbeing", "county", WELLBEING_SPEC),
    Collection("counties", "counties", "county", ALL_SPEC),
    Collection("states", "state-income", "state", INCOME_SPEC),
    Collection("states", "state-people", "state", PEOPLE_SPEC),
    Collection("states", "state-housing", "state", HOUSING_SPEC),
    Collection("states", "state-connectivity", "state", CONNECTIVITY_SPEC),
    Collection("states", "state-wellbeing", "state", WELLBEING_SPEC),
    Collection("states", "states", "state", ALL_SPEC),
    Collection("zctas", "zcta-income", "zcta", INCOME_SPEC),
    Collection("zctas", "zcta-people", "zcta", PEOPLE_SPEC),
    Collection("zctas", "zcta-housing", "zcta", HOUSING_SPEC),
    Collection("zctas", "zcta-connectivity", "zcta", CONNECTIVITY_SPEC),
    Collection("zctas", "zcta-wellbeing", "zcta", WELLBEING_SPEC),
    Collection("zctas", "zctas", "zcta", ALL_SPEC),
    Collection("places", "place-income", "place", INCOME_SPEC),
    Collection("places", "place-people", "place", PEOPLE_SPEC),
    Collection("places", "place-housing", "place", HOUSING_SPEC),
    Collection("places", "place-connectivity", "place", CONNECTIVITY_SPEC),
    Collection("places", "place-wellbeing", "place", WELLBEING_SPEC),
    Collection("places", "places", "place", ALL_SPEC),
    Collection("congressional-districts", "cd-income", "cd", INCOME_SPEC),
    Collection("congressional-districts", "cd-people", "cd", PEOPLE_SPEC),
    Collection("congressional-districts", "cd-housing", "cd", HOUSING_SPEC),
    Collection("congressional-districts", "cd-connectivity", "cd",
               CONNECTIVITY_SPEC),
    Collection("congressional-districts", "cd-wellbeing", "cd",
               WELLBEING_SPEC),
    Collection("congressional-districts", "congressional-districts", "cd",
               ALL_SPEC),
]

# The wide all-indicator tables: one per coarse level, same id as its group
# directory. Their collection.json lives in catalog/<group>/<id>/ but their
# parquet and pmtiles stay in catalog/<group>/, so published data URLs
# survive the 2026-11-15 restructure.
WIDE_IDS = {c.id for c in COLLECTIONS if c.group == c.id}


# --------------------------------------------------------------------------
# Table shells: line-number pinning and derived line groups
# --------------------------------------------------------------------------

_shells: list[tuple[str, int, str]] | None = None


def shells() -> list[tuple[str, int, str]]:
    """(table, line, label) from this vintage's table-shells file."""
    global _shells
    if _shells is None:
        rows = []
        with open(SHELLS, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="|")
            next(reader)
            for row in reader:
                if len(row) >= 5 and row[1]:
                    rows.append((row[0], int(float(row[1])), row[4]))
        _shells = rows
    return _shells


def shell_lines(table: str, label_substr: str) -> list[int]:
    """Line numbers in `table` whose shell label contains `label_substr`."""
    return [line for t, line, label in shells()
            if t == table and label_substr in label]


def check_shell(table: str, line: int, label_substr: str) -> None:
    """Fail loudly if a pinned line's label moved in this vintage."""
    if line not in shell_lines(table, label_substr):
        raise RuntimeError(
            f"{table} line {line} no longer matches {label_substr!r} in the "
            f"ACS {ACS_RELEASE} table shells — the vintage moved a line")


# Age components appear once per sex, so each label resolves to two lines;
# derive them from the shells rather than hardcoding twenty numbers.
UNDER_18_LABELS = ["Under 5 years", "5 to 9 years", "10 to 14 years",
                   "15 to 17 years"]
OVER_65_LABELS = ["65 and 66 years", "67 to 69 years", "70 to 74 years",
                  "75 to 79 years", "80 to 84 years", "85 years and over"]


def age_lines(labels: list[str]) -> list[int]:
    out = []
    for lab in labels:
        found = shell_lines("B01001", lab)
        if len(found) != 2:  # one male line + one female line
            raise RuntimeError(f"B01001 {lab!r}: expected 2 lines, got "
                               f"{found}")
        out += found
    return out


def poverty_lines(labels: list[str]) -> tuple[list[int], list[int]]:
    """(below-poverty lines, total/denominator lines) for B17001 age labels.

    B17001's labels are not unique substrings of each other ("5 years" is a
    substring of "75 years and over"), so this matches on exact label text
    against `shells()` directly rather than `shell_lines`'s substring
    search. Each label occurs 4 times — below-poverty male, below-poverty
    female, at-or-above male, at-or-above female, in ascending line order —
    so the first two are the numerator and all four are the denominator.
    """
    below, total = [], []
    for lab in labels:
        found = sorted(line for t, line, label in shells()
                       if t == "B17001" and label == lab)
        if len(found) != 4:
            raise RuntimeError(f"B17001 {lab!r}: expected 4 lines, got "
                               f"{found}")
        below += found[:2]
        total += found
    return sorted(below), sorted(total)


def resolve_lines(spec_lines, table: str) -> list[int]:
    """Expand the named line groups that are derived from the shells."""
    if spec_lines == "UNDER18":
        return age_lines(UNDER_18_LABELS)
    if spec_lines == "OVER65":
        return age_lines(OVER_65_LABELS)
    if spec_lines == "NOINS":
        lines = shell_lines(table, "No health insurance coverage")
        if len(lines) != 18:  # 9 age groups x 2 sexes
            raise RuntimeError(f"B27001: expected 18 no-coverage lines, "
                               f"got {len(lines)}")
        return lines
    if spec_lines == "DISAB":
        lines = shell_lines(table, "With a disability")
        if len(lines) != 12:  # 6 age groups x 2 sexes
            raise RuntimeError(f"B18101: expected 12 disability lines, "
                               f"got {len(lines)}")
        return lines
    return spec_lines


def check_all_shells() -> list[tuple[str, int, str]]:
    """Verify every pinned line in every spec. Returns what was checked."""
    pins = []
    for spec in [CONTEXT_SPEC, ALL_SPEC]:
        for s in spec:
            if s.check:
                check_shell(*s.check)
                pins.append(s.check)
    # The derived groups self-check their cardinality.
    for group, table in (("UNDER18", "B01001"), ("OVER65", "B01001"),
                         ("NOINS", "B27001"), ("DISAB", "B18101")):
        resolve_lines(group, table)
    # The B17001 poverty-by-age line lists are literals (Spec.den must be a
    # plain tuple at import time), so re-derive them from the live shells
    # and fail loudly if a vintage renumbered a line instead of silently
    # publishing a wrong child- or senior-poverty rate.
    child_below, child_total = poverty_lines(POV_CHILD_LABELS)
    if (child_below, child_total) != (POV_CHILD_BELOW, POV_CHILD_TOTAL):
        raise RuntimeError(
            f"B17001 child-poverty lines moved: shells give "
            f"below={child_below} total={child_total}, specs.py has "
            f"below={POV_CHILD_BELOW} total={POV_CHILD_TOTAL}")
    senior_below, senior_total = poverty_lines(POV_SENIOR_LABELS)
    if (senior_below, senior_total) != (POV_SENIOR_BELOW, POV_SENIOR_TOTAL):
        raise RuntimeError(
            f"B17001 senior-poverty lines moved: shells give "
            f"below={senior_below} total={senior_total}, specs.py has "
            f"below={POV_SENIOR_BELOW} total={POV_SENIOR_TOTAL}")
    return pins


def tables() -> dict[str, list[Spec]]:
    """table -> the unique columns derived from it, in publication order.

    Every column reads its numerator and its denominator from the same
    table, so one table is one independent unit of work: read the .dat
    once, emit that table's columns for all four geography levels.
    """
    out: dict[str, list[Spec]] = {}
    seen: set[str] = set()
    for s in CONTEXT_SPEC + ALL_SPEC:
        if s.name in seen:
            continue
        seen.add(s.name)
        if s.den and s.den[0] != s.table:
            raise RuntimeError(f"{s.name}: denominator table {s.den[0]} is "
                               f"not the numerator table {s.table}")
        out.setdefault(s.table, []).append(s)
    return out


def out_columns(spec: list[Spec]) -> list[str]:
    """Published column names for a spec, in order (value, moe, cv)."""
    cols = []
    for s in spec:
        cols.append(s.name)
        cols.append(f"{s.name}_moe")
        if s.cv:
            cols.append(f"{s.name}_cv")
    return cols
