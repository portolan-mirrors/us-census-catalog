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
# per .dat file extracts all four (the biggest file is 200 MB).
LEVELS = {
    "bg": "1500000US",
    "tract": "1400000US",
    "county": "0500000US",
    "state": "0400000US",
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
]

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
    Collection("block-groups", "bg-income", "bg", INCOME_SPEC),
    Collection("block-groups", "bg-people", "bg", PEOPLE_SPEC),
    Collection("block-groups", "bg-housing", "bg", HOUSING_SPEC),
    Collection("block-groups", "bg-connectivity", "bg", CONNECTIVITY_SPEC),
    Collection("tracts", "tract-income", "tract", INCOME_SPEC),
    Collection("tracts", "tract-people", "tract", PEOPLE_SPEC),
    Collection("tracts", "tract-housing", "tract", HOUSING_SPEC),
    Collection("tracts", "tract-connectivity", "tract", CONNECTIVITY_SPEC),
    Collection("tracts", "tract-wellbeing", "tract", WELLBEING_SPEC),
    Collection(None, "counties", "county", ALL_SPEC),
    Collection(None, "states", "state", ALL_SPEC),
]


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
