#!/usr/bin/env python3
"""Every published column, described: measure, universe, table, derivation.

One description per column name per collection, written for the `description`
field of STAC's table extension (`table:columns[].description`) and reused by
the published AGENTS.md files. `tools/make_stac.py` reads this module and
fails loudly on any column in a parquet file that has no entry here, so a
column cannot reach the catalog undocumented.

Three rules held while writing these:

1. **Universes are quoted, not guessed.** Every ACS universe below is the
   `Universe` field of that table's own row in this release's table shells
   (`staging/census-cache/ACS20245YR_Table_Shells.txt`, the file
   `tools/specs.py` pins line numbers against — published at
   <https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/documentation/ACS20245YR_Table_Shells.txt>).
   `TABLE_UNIVERSE` holds them verbatim, and the prose reuses them rather
   than paraphrasing: "occupied housing units" and "households" are the same
   population, but "renter-occupied housing units paying cash rent" is not
   "renter-occupied housing units", and B25064 means the former.
2. **Derivations come from `tools/specs.py`,** which is the only place that
   knows a line number. `kind`, `lines`, `den` and `cv` are read off the Spec
   tuples here, so the margin-of-error sentence a column gets is the formula
   the build actually applied to it.
3. **Quirk notes are measured,** from `docs/acs-build-notes.md` and
   `docs/blocks-build-notes.md` (both of which report what the build run
   measured) or from a query against the published parquet. Where a note
   gives a NULL rate, that rate is a count, not an estimate.

Block columns come from the 2020 P.L. 94-171 redistricting file, whose field
positions are pinned in `docs/blocks-build-notes.md` against the Census
Bureau's own R import scripts.

Public interface:

    docs_for(collection_id)        -> {column: description}
    describe(column, collection_id) -> description or None
    missing(columns, collection_id) -> columns with no description
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import specs  # noqa: E402

# --------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------

ACS_DATASET = "ACSDT5Y2024"       # data.census.gov table id for this release
PL_DATASET = "DECENNIALPL2020"    # ditto for the 2020 redistricting file

SHELLS_URL = (
    "https://www2.census.gov/programs-surveys/acs/summary_file/2024/"
    "table-based-SF/documentation/ACS20245YR_Table_Shells.txt"
)
ACCURACY_URL = (
    "https://www2.census.gov/programs-surveys/acs/tech_docs/accuracy/"
    "MultiyearACSAccuracyofData2024.pdf"
)
PL_TECHDOC_URL = (
    "https://www2.census.gov/programs-surveys/decennial/2020/"
    "technical-documentation/complete-tech-docs/summary-file/"
    "2020Census_PL94_171Redistricting_StatesTechDoc_English.pdf"
)


def acs_table(table: str) -> str:
    """Markdown link to an ACS table's page on data.census.gov."""
    return f"[{table}](https://data.census.gov/table/{ACS_DATASET}.{table})"


def pl_table(table: str) -> str:
    """Markdown link to a 2020 PL 94-171 table's page on data.census.gov."""
    return f"[{table}](https://data.census.gov/table/{PL_DATASET}.{table})"


# --------------------------------------------------------------------------
# Universes, verbatim from this release's table shells
# --------------------------------------------------------------------------

# table -> (Title, Universe), copied from the `Title` and `Universe` fields of
# ACS20245YR_Table_Shells.txt. Nothing in this dict is paraphrased.
TABLE_UNIVERSE = {
    "B01001": ("Sex by Age", "Total population"),
    "B01002": ("Median Age by Sex", "Total population"),
    "B01003": ("Total Population", "Total population"),
    "B03002": ("Hispanic or Latino Origin by Race", "Total population"),
    "B05002": ("Place of Birth by Nativity and Citizenship Status",
               "Total population"),
    "B08301": ("Means of Transportation to Work", "Workers 16 years and over"),
    "B08303": ("Travel Time to Work",
               "Workers 16 years and over who did not work from home"),
    "B15003": ("Educational Attainment for the Population 25 Years and Over",
               "Population 25 years and over"),
    "B17020B": ("Poverty Status in the Past 12 Months by Age (Black or "
                "African American Alone)",
                "Black or African American alone population for whom "
                "poverty status is determined"),
    "B18101": ("Sex by Age by Disability Status",
               "Civilian noninstitutionalized population"),
    "B19013": ("Median Household Income in the Past 12 Months (in 2024 "
               "Inflation-Adjusted Dollars)", "Households"),
    "B19013B": ("Median Household Income in the Past 12 Months (in 2024 "
                "Inflation-Adjusted Dollars) (Black or African American "
                "Alone Householder)",
                "Households with a householder who is Black or African "
                "American alone"),
    "B19013D": ("Median Household Income in the Past 12 Months (in 2024 "
                "Inflation-Adjusted Dollars) (Asian Alone Householder)",
                "Households with a householder who is Asian alone"),
    "B19013H": ("Median Household Income in the Past 12 Months (in 2024 "
                "Inflation-Adjusted Dollars) (White Alone, Not Hispanic or "
                "Latino Householder)",
                "Households with a householder who is White alone, not "
                "Hispanic or Latino"),
    "B19013I": ("Median Household Income in the Past 12 Months (in 2024 "
                "Inflation-Adjusted Dollars) (Hispanic or Latino "
                "Householder)",
                "Households with a householder who is Hispanic or Latino"),
    "B19301": ("Per Capita Income in the Past 12 Months (in 2024 "
               "Inflation-Adjusted Dollars)", "Total population"),
    "B22010": ("Receipt of Food Stamps/SNAP in the Past 12 Months by "
               "Disability Status for Households", "Households"),
    "B23025": ("Employment Status for the Population 16 Years and Over",
               "Population 16 years and over"),
    "B25002": ("Occupancy Status", "Housing units"),
    "B25003": ("Tenure", "Occupied housing units"),
    "B25024": ("Units in Structure", "Housing units"),
    "B25034": ("Year Structure Built", "Housing units"),
    "B25044": ("Tenure by Vehicles Available", "Occupied housing units"),
    "B25064": ("Median Gross Rent (Dollars)",
               "Renter-occupied housing units paying cash rent"),
    "B25070": ("Gross Rent as a Percentage of Household Income in the Past "
               "12 Months", "Renter-occupied housing units"),
    "B25077": ("Median Value (Dollars)", "Owner-occupied housing units"),
    "B26001": ("Group Quarters Population", "Population in group quarters"),
    "B27001": ("Health Insurance Coverage Status by Sex by Age",
               "Civilian noninstitutionalized population"),
    "B28001": ("Types of Computers in Household", "Households"),
    "B28002": ("Presence and Types of Internet Subscriptions in Household",
               "Households"),
    "C17002": ("Ratio of Income to Poverty Level in the Past 12 Months",
               "Population for whom poverty status is determined"),
}

# 2020 P.L. 94-171 tables, from the file's own table titles (see
# docs/blocks-build-notes.md for the field layout and
# PL_TECHDOC_URL for the published universes).
PL_UNIVERSE = {
    "P1": ("Race", "Total population"),
    "P2": ("Hispanic or Latino, and Not Hispanic or Latino by Race",
           "Total population"),
    "P3": ("Race for the Population 18 Years and Over",
           "Population 18 years and over"),
    "H1": ("Occupancy Status", "Housing units"),
    "P5": ("Group Quarters Population by Major Group Quarters Type",
           "Population in group quarters"),
}

# --------------------------------------------------------------------------
# Geography / context columns
# --------------------------------------------------------------------------

LEVEL_OF = {c.id: c.level for c in specs.COLLECTIONS}
LEVEL_OF["blocks"] = "block"

LEVEL_NOUN = {
    "bg": "block group", "tract": "census tract", "county": "county",
    "state": "state", "block": "census block",
    "zcta": "ZIP Code Tabulation Area", "place": "place",
    "cd": "congressional district",
}

# The cartographic boundary vintage behind each level's geometry. ZCTAs are
# the exception: the 2020-based ZCTAs are the current ones and the Census
# Bureau has published no cartographic ZCTA file since GENZ2020, which is
# also the vintage the ACS tabulates (summary level 860Z2).
CB_VINTAGE = {"bg": 2024, "tract": 2024, "county": 2024, "state": 2024,
              "zcta": 2020, "place": 2024, "cd": 2024}

CONGRESS = 119  # the Congress the ACS 2020-2024 5-year release tabulates

GEOID_DOC = {
    "bg": "12-character census block-group GEOID — state (2) + county (3) + "
          "tract (6) + block group (1), e.g. `295101022004`. The join key "
          "across the census family: `substr(geoid, 1, 11)` is the tract, "
          "`substr(geoid, 1, 5)` the county, `substr(geoid, 1, 2)` the state "
          "FIPS code. Matches `GEOID` in the Census Bureau's 2024 "
          "cartographic boundary block-group file; the summary-level prefix "
          "the ACS summary file carries on `GEO_ID` (`1500000US`) is "
          "stripped.",
    "tract": "11-character census tract GEOID — state (2) + county (3) + "
             "tract (6), e.g. `29510102200`. Joins the block-group "
             "collections on `substr(geoid, 1, 11)` and the block collection "
             "on `substr(geoid, 1, 11)`. Matches `GEOID` in the 2024 "
             "cartographic boundary tract file; the ACS `1400000US` prefix "
             "is stripped.",
    "county": "5-character county (or county-equivalent) GEOID — state (2) + "
              "county (3), e.g. `29510` for St. Louis city. Includes Puerto "
              "Rico municipios and the island-area county equivalents. "
              "Matches `GEOID` in the 2024 cartographic boundary county "
              "file; the ACS `0500000US` prefix is stripped.",
    "state": "2-character state FIPS code, e.g. `29` for Missouri. Covers "
             "the 50 states, the District of Columbia, Puerto Rico and the "
             "four island areas. Matches `GEOID` in the 2024 cartographic "
             "boundary state file; the ACS `0400000US` prefix is stripped.",
    "zcta": "5-digit ZIP Code Tabulation Area code, e.g. `90210`. **Not a "
            "ZIP code**: a ZCTA is the Census Bureau's approximation of the "
            "area a USPS 5-digit ZIP delivery area covers, built from 2020 "
            "census blocks, and the two are not interchangeable (see the "
            "collection's known issues). ZCTAs do not nest in any other "
            "census geography — a ZCTA can cross county and state lines — so "
            "there is no prefix join to counties, tracts or states, and the "
            "first two characters are a postal region, not a state FIPS "
            "code. Matches `GEOID20`/`ZCTA5CE20` in the Census Bureau's 2020 "
            "cartographic boundary ZCTA file; the ACS `860Z200US` prefix is "
            "stripped.",
    "place": "7-character place GEOID — state FIPS (2) + place FIPS (5), "
             "e.g. `0644000` for Los Angeles city. `substr(geoid, 1, 2)` is "
             "the state FIPS code, which is the only prefix join a place "
             "supports: places nest in states but not in counties (a place "
             "can straddle a county line) and a place is not a census-tract "
             "aggregate. Matches `GEOID` in the 2024 cartographic boundary "
             "place file; the ACS `1600000US` prefix is stripped.",
    "cd": f"4-character congressional district GEOID — state FIPS (2) + "
          f"district (2), e.g. `0612` for California's 12th. "
          f"`substr(geoid, 1, 2)` is the state FIPS code. At-large states "
          f"use district `00` (AK, DE, ND, SD, VT, WY) and the non-voting "
          f"delegate districts use `98` (`1198` District of Columbia, `7298` "
          f"Puerto Rico, plus the four island areas). Districts of the "
          f"**{CONGRESS}th Congress**, which is the vintage the ACS "
          f"2020–2024 5-year release tabulates: matches `GEOID` in the "
          f"`cb_2024_us_cd{CONGRESS}_500k` cartographic boundary file "
          f"(`CDSESSN = '{CONGRESS}'` on every feature) and the ACS "
          f"`5001900US` prefix, whose `19` is the congress number, is "
          f"stripped. District numbers are not stable across congresses, so "
          f"a `geoid` here does not join to a 118th-Congress district of the "
          f"same number.",
    "block": "15-character 2020 census block GEOID — state (2) + county (3) "
             "+ tract (6) + block (4), e.g. `020130001001000`. The "
             "geoheader's `GEOCODE` field, not its `GEOID` (which carries a "
             "`7500000US` summary-level prefix); the build asserts "
             "`GEOCODE == STATE || COUNTY || TRACT || BLOCK` on every row. "
             "`substr(geoid, 1, 12)` is the block group, so blocks join the "
             "ACS block-group collections by prefix.",
}

CONTEXT_DOC = {
    "name": lambda level: {
        "bg": "Human-readable name, assembled from the cartographic boundary "
              "files with `concat_ws(', ', …)`: the block group's own "
              "`NAMELSAD`, the tract's `NAMELSAD`, then the county's "
              "`NAMELSAD` and `STATE_NAME` — \"Block Group 4, Census Tract "
              "1022, St. Louis city, Missouri\". The block-group file carries "
              "only \"Block Group 4\", so the tract and county files supply "
              "the rest.",
        "tract": "Human-readable name from the cartographic boundary tract "
                 "file: `NAMELSAD`, `NAMELSADCO`, `STATE_NAME` — \"Census "
                 "Tract 34.06, San Joaquin County, California\".",
        "county": "Human-readable name from the cartographic boundary county "
                  "file: `NAMELSAD`, `STATE_NAME` — \"St. Louis city, "
                  "Missouri\".",
        "state": "State name from the cartographic boundary state file's "
                 "`NAME` field — \"Missouri\".",
        "zcta": "`'ZCTA5 ' || ZCTA5CE20` from the 2020 cartographic "
                "boundary ZCTA file — \"ZCTA5 90210\". A ZCTA has no "
                "containing geography to name it by, because it crosses "
                "county and state lines, and the Census Bureau publishes no "
                "other name for one; this is the label data.census.gov uses.",
        "place": "Human-readable name from the cartographic boundary place "
                 "file: `NAMELSAD`, `STATE_NAME` — \"Los Angeles city, "
                 "California\", \"Brentwood CDP, New York\". `NAMELSAD` "
                 "carries the legal/statistical descriptor, so the name "
                 "itself says whether a place is a city, town, village, "
                 "borough or CDP.",
        "cd": "`NAMELSAD` from the cartographic boundary congressional "
              "district file plus the state name from the state file — "
              "\"Congressional District 12, California\", \"Delegate "
              "District (at Large), District of Columbia\".",
    }[level],
    "state": lambda level: (
        "Always NULL in this collection. A ZIP Code Tabulation Area is not "
        "inside any state: it approximates a USPS ZIP delivery area, which "
        "can cross state lines, the ACS publishes ZCTAs at the nation level "
        "only, and the 2020 cartographic boundary ZCTA file carries no state "
        "attribute (its fields are `ZCTA5CE20`, `AFFGEOID20`, `GEOID20`, "
        "`NAME20`, `LSAD20`, `ALAND20`, `AWATER20`). The column is kept so "
        "the schema matches the other collections; deriving a value from the "
        "first digits of the code would be wrong, because those are a postal "
        "region. To assign ZCTAs to states, do it spatially, and expect "
        "ties."
        if level == "zcta" else
        "Two-letter USPS state or territory code (`MO`, `PR`, `GU`). Carried "
        "on every collection from the `STATEFP → USPS` lookup embedded in "
        "`tools/specs.py` rather than read off the boundary files, because "
        "the 2024 cartographic boundary block-group file has no `STUSPS` "
        "column while the tract, county and state files do."
        + ("" if level != "block" else
           " In the block collection this sits alongside the hive partition "
           "key `state_fips`, which carries the numeric FIPS code.")),
    "aland_sqkm": lambda level: (
        "Land area in square kilometres, rounded to 3 decimals. "
        + ("`ALAND20 / 1e6` from the TIGER/Line 2024 block file."
           if level == "block" else
           "`ALAND20 / 1e6` from the 2020 cartographic boundary ZCTA file."
           if level == "zcta" else
           "`ALAND / 1e6` from the cartographic boundary file.")
        + " Land only: water area is excluded, which is what makes it the "
          "right denominator for population density."),
    "pop_density": lambda level: (
        "People per square kilometre of land area, rounded to 1 decimal: "
        + ("`pop_total / aland_sqkm`. NULL where `ALAND20` is 0 — a "
           "water-only block has no land to divide by; 2.92% of the "
           "8,174,955 blocks are NULL on this column (measured)."
           if level == "block" else
           "`population / aland_sqkm`. NULL where `ALAND` is 0 or "
           "`population` is NULL.")
        + ("" if level != "bg" else
           " 646 of 242,298 block groups are NULL: 444 with no ACS "
           "population plus 202 that are entirely water.")),
    "geometry": lambda level: (
        "Boundary polygon (Polygon or MultiPolygon), WKB-encoded, in "
        "EPSG:4326 / OGC:CRS84 — the GeoParquet default CRS, written as an "
        "omitted `crs` key. "
        + ("TIGER/Line 2024 `TABBLOCK20`, which is **not** shoreline-clipped: "
           "a coastal block extends to the 3-mile limit."
           if level == "block" else
           f"From the Census Bureau's {CB_VINTAGE[level]} cartographic "
           f"boundary {LEVEL_NOUN[level]} file (GENZ{CB_VINTAGE[level]}, "
           f"1:500,000), which clips to the shoreline — TIGER/Line would "
           f"extend the {LEVEL_NOUN[level]} into open water."
           + (" GENZ2020 because the Census Bureau has published no "
              "cartographic ZCTA file since: the 2020-based ZCTAs are the "
              "current ones, and they are the vintage the ACS tabulates."
              if level == "zcta" else ""))
        + " Generalized for mapping and point-in-polygon work, not for "
          "legal-boundary or precise-area work."),
    "bbox": lambda level: (
        "GeoParquet 1.1 covering struct (`xmin`, `ymin`, `xmax`, `ymax`) for "
        "the row's geometry, with row-group statistics, so a spatial filter "
        "can skip most of the file over the network. Written by "
        "geoparquet-io, not by the Census Bureau."),
    "state_fips": lambda level: (
        "Hive partition key, synthesized from the directory name when the "
        "`state_fips=*/*.parquet` glob is read — the 2-digit state FIPS code "
        "of the partition. Not a column in the parquet files themselves. "
        "Named `state_fips` rather than `state` so it does not shadow the "
        "USPS `state` column."),
}

# --------------------------------------------------------------------------
# ACS value columns
# --------------------------------------------------------------------------

_U = {t: u for t, (_, u) in TABLE_UNIVERSE.items()}

# Each entry: what it measures, the universe (quoted from the shells), the
# table as a link, and how it was derived. Line numbers match
# docs/acs-build-notes.md, which the build pins against the shells.
ACS_DOC = {
    # --- context ----------------------------------------------------------
    "population": (
        "Total population. Universe: total population. The single line of "
        f"{acs_table('B01003')} ({TABLE_UNIVERSE['B01003'][0]}), published "
        "as an integer. Carried on every ACS collection so a rate can be "
        "weighted or sanity-checked without a second download."),

    # --- income -----------------------------------------------------------
    "median_hh_income": (
        "Median household income in the past 12 months, in 2024 "
        "inflation-adjusted dollars. Universe: households. Line 1 of "
        f"{acs_table('B19013')}, published as the Census Bureau publishes "
        "it. A median cannot be aggregated: there is no way to combine the "
        "medians of two block groups into the median of their union."),
    "per_capita_income": (
        "Per capita income in the past 12 months, in 2024 inflation-adjusted "
        "dollars — aggregate income divided by total population, so children "
        "and people with no income are in the denominator. Universe: total "
        f"population. Line 1 of {acs_table('B19301')}."),
    "pct_below_poverty": (
        "Percent of the population below the federal poverty level — an "
        "income-to-poverty ratio under 1.00. Universe: population for whom "
        "poverty status is determined, which excludes institutionalized "
        "people, people in military group quarters and in college dormitories, "
        "and unrelated individuals under 15. Lines 2 (\"Under .50\") + 3 "
        f"(\".50 to .99\") of {acs_table('C17002')} over line 1."),
    "pct_below_2x_poverty": (
        "Percent of the population with an income-to-poverty ratio under "
        "2.00 — a common proxy for low income rather than deep poverty. "
        "Universe: population for whom poverty status is determined. Lines "
        f"2–7 of {acs_table('C17002')} over line 1 (equivalently, everyone "
        "not in line 8, \"2.00 and over\")."),
    "pct_snap": (
        "Percent of households that received Food Stamps/SNAP benefits at "
        "any time in the past 12 months. Universe: households. Line 2 of "
        f"{acs_table('B22010')} over line 1. Receipt by the household, not "
        "by individuals, and not a measure of current enrollment."),
    "pct_unemployed": (
        "Unemployment rate: unemployed people as a percent of the civilian "
        "labor force. Universe for the table is the population 16 years and "
        "over, but the denominator here is line 3, \"Civilian labor force\" "
        "— the labor force, not the whole population 16+, because that is "
        "what an unemployment rate divides by. Line 5 (\"Unemployed\") over "
        f"line 3 of {acs_table('B23025')}. Members of the Armed Forces and "
        "people not in the labor force are excluded from both parts."),

    # --- people -----------------------------------------------------------
    "median_age": (
        "Median age in years. Universe: total population. Line 1 of "
        f"{acs_table('B01002')} (Median Age by Sex); the male and female "
        "medians on lines 2 and 3 are not published here. Like every median, "
        "not aggregable."),
    "pct_under_18": (
        "Percent of the population under 18 years old. Universe: total "
        f"population. The under-18 lines of {acs_table('B01001')} (Sex by "
        "Age) over line 1. The components are resolved from the table shells "
        "by label — \"Under 5 years\", \"5 to 9 years\", \"10 to 14 years\", "
        "\"15 to 17 years\", once per sex, 8 lines for this vintage — so a "
        "renumbered line fails the build instead of silently shifting."),
    "pct_65_plus": (
        "Percent of the population 65 years and over. Universe: total "
        f"population. The 65-and-over lines of {acs_table('B01001')} over "
        "line 1, resolved from the shells by label (\"65 and 66 years\" "
        "through \"85 years and over\", once per sex, 12 lines for this "
        "vintage)."),
    "pct_white_nh": (
        "Percent of the population that is White alone and not Hispanic or "
        "Latino. Universe: total population. Line 3 of "
        f"{acs_table('B03002')} over line 1 — line 3 sits under line 2, "
        "\"Not Hispanic or Latino\", so this is the non-Hispanic branch."),
    "pct_black": (
        "Percent of the population that is Black or African American alone "
        "and not Hispanic or Latino. Universe: total population. Line 4 of "
        f"{acs_table('B03002')} over line 1 (the \"Not Hispanic or Latino\" "
        "branch, so this share and `pct_hispanic` do not overlap)."),
    "pct_native": (
        "Percent of the population that is American Indian and Alaska Native "
        "alone and not Hispanic or Latino. Universe: total population. Line "
        f"5 of {acs_table('B03002')} over line 1. Small everywhere outside "
        "Indian Country and reservations, and at block-group scale usually "
        "within its own margin of error."),
    "pct_asian": (
        "Percent of the population that is Asian alone and not Hispanic or "
        "Latino. Universe: total population. Line 6 of "
        f"{acs_table('B03002')} over line 1."),
    "pct_hispanic": (
        "Percent of the population that is Hispanic or Latino, of any race. "
        "Universe: total population. Line 12 of "
        f"{acs_table('B03002')} over line 1. Hispanic origin is asked "
        "separately from race, which is why this crosses every race "
        "category; here it is disjoint from the five race shares because "
        "those are all drawn from the non-Hispanic branch."),
    "pct_people_of_color": (
        "Percent of the population that is **not** White-alone "
        "non-Hispanic: `100 − pct_white_nh`. Universe: total population. "
        f"Derived from {acs_table('B03002')}. A complement, so it carries "
        "`pct_white_nh`'s own margin of error unchanged — a share and its "
        "complement have the same sampling error."),
    "pct_bachelors_plus": (
        "Percent of adults 25 and over whose highest attainment is a "
        "bachelor's degree or more. Universe: population 25 years and over. "
        f"Lines 22–25 of {acs_table('B15003')} (Bachelor's, Master's, "
        "Professional school, Doctorate) over line 1. Associate's degrees "
        "(line 21) are deliberately excluded."),

    # --- housing ----------------------------------------------------------
    "housing_units": (
        "Total housing units, occupied and vacant. Universe: housing units. "
        f"Line 1 of {acs_table('B25002')} (Occupancy Status), published as "
        "an integer."),
    "pct_vacant_units": (
        "Percent of housing units that are vacant. Universe: housing units. "
        f"Line 3 (\"Vacant\") over line 1 of {acs_table('B25002')}. The ACS "
        "counts for-sale, for-rent, seasonal and migrant-worker units as "
        "vacant, so this is not a measure of abandonment."),
    "households": (
        "Households — occupied housing units. One household per occupied "
        "unit, by definition. Universe: occupied housing units. Line 1 of "
        f"{acs_table('B25003')} (Tenure), published as an integer."),
    "pct_owner_occupied": (
        "Percent of occupied housing units that are owner-occupied. "
        "Universe: occupied housing units. Line 2 (\"Owner occupied\") over "
        f"line 1 of {acs_table('B25003')}. The homeownership rate of "
        "households, not of people, and vacant units are outside the "
        "universe entirely."),
    "median_gross_rent": (
        "Median gross rent in dollars per month — contract rent plus the "
        "estimated average monthly cost of utilities and fuels. Universe: "
        "renter-occupied housing units **paying cash rent**, so units "
        "occupied rent-free are excluded. Line 1 of "
        f"{acs_table('B25064')}."),
    "pct_rent_burdened": (
        "Percent of renter households paying 30% or more of household income "
        "on gross rent — the standard affordability threshold. Universe: "
        "renter-occupied housing units, less those whose ratio the Census "
        "could not compute. Lines 7–10 (30.0–34.9, 35.0–39.9, 40.0–49.9, "
        f"50.0 percent or more) of {acs_table('B25070')} over line 1 minus "
        "line 11 (\"Not computed\" — no cash rent, or no income). Including "
        "the not-computed units in the denominator would understate the "
        "burden."),
    "pct_severely_rent_burdened": (
        "Percent of renter households paying 50% or more of household income "
        "on gross rent. Universe: renter-occupied housing units, less those "
        "whose ratio could not be computed. Line 10 of "
        f"{acs_table('B25070')} over line 1 minus line 11. A subset of "
        "`pct_rent_burdened`."),
    "median_home_value": (
        "Median value of owner-occupied housing units, in dollars — the "
        "owner's estimate of what the property would sell for, not an "
        "assessment or a sale price. Universe: owner-occupied housing units. "
        f"Line 1 of {acs_table('B25077')}."),
    "pct_built_pre_1940": (
        "Percent of housing units built in 1939 or earlier. Universe: "
        f"housing units. Line 11 of {acs_table('B25034')} (Year Structure "
        "Built) over line 1. The oldest bucket the table publishes, and a "
        "standard screening proxy for lead-paint risk."),
    "pct_single_family": (
        "Percent of housing units in single-family structures. Universe: "
        "housing units. Lines 2 (\"1, detached\") + 3 (\"1, attached\") over "
        f"line 1 of {acs_table('B25024')} (Units in Structure). Attached "
        "single-family — rowhouses, townhouses — is included; a duplex "
        "(line 4) is not."),

    # --- connectivity -----------------------------------------------------
    "hh_no_vehicle": (
        "Occupied housing units with no vehicle available, owner- and "
        "renter-occupied combined. Universe: occupied housing units. Lines 3 "
        f"+ 10 of {acs_table('B25044')} (Tenure by Vehicles Available) — the "
        "\"No vehicle available\" line under each tenure — which is what "
        "makes this a tenure-blind count. Published as an integer; the two "
        "margins of error add in quadrature."),
    "pct_hh_no_vehicle": (
        "Percent of occupied housing units with no vehicle available. "
        "Universe: occupied housing units. Lines 3 + 10 over line 1 of "
        f"{acs_table('B25044')}. Households, not people: a car-free "
        "household of four counts once."),
    "pct_commute_drive_alone": (
        "Percent of workers who drove alone to work in a car, truck or van. "
        "Universe: workers 16 years and over. Line 3 (\"Drove alone\", under "
        f"\"Car, truck, or van\") over line 1 of {acs_table('B08301')} "
        "(Means of Transportation to Work). The ACS asks about the usual "
        "means of transportation in the reference week, so a hybrid "
        "commuter reports one mode."),
    "pct_commute_transit": (
        "Percent of workers who commuted by public transportation. Universe: "
        "workers 16 years and over. Line 10 (\"Public transportation\") over "
        f"line 1 of {acs_table('B08301')}, which covers bus, subway and "
        "elevated rail, light rail, commuter rail and ferryboat. Taxi and "
        "ride-hailing (line 16) are a separate category in this vintage and "
        "are **not** included."),
    "pct_commute_walk_bike": (
        "Percent of workers who walked or bicycled to work. Universe: "
        "workers 16 years and over. Lines 18 (\"Bicycle\") + 19 "
        f"(\"Walked\") over line 1 of {acs_table('B08301')}."),
    "pct_work_from_home": (
        "Percent of workers who worked from home. Universe: workers 16 years "
        f"and over. Line 21 (\"Worked from home\") over line 1 of "
        f"{acs_table('B08301')}. In a 2020–2024 5-year estimate this "
        "averages over the pandemic shift and its partial reversal, so it is "
        "not a reading of any single year."),
    "pct_commute_45min_plus": (
        "Percent of commuters whose one-way travel time to work is 45 "
        "minutes or more. Universe: workers 16 years and over **who did not "
        "work from home** — the table's own universe, which is why "
        "work-from-home does not deflate this share. Lines 11 + 12 + 13 (45 "
        "to 59 minutes, 60 to 89, 90 or more) over line 1 of "
        f"{acs_table('B08303')} (Travel Time to Work)."),
    "pct_no_internet": (
        "Percent of households with no internet access of any kind. "
        "Universe: households. Line 13 (\"No Internet access\") over line 1 "
        f"of {acs_table('B28002')}. Households that use the internet without "
        "paying for a subscription (line 12) are counted as having access, "
        "so this is the floor of the digital divide, not its full extent."),
    "pct_no_computer": (
        "Percent of households with no computing device — no desktop or "
        "laptop, no smartphone, no tablet, no other computer. Universe: "
        f"households. Line 11 (\"No Computer\") over line 1 of "
        f"{acs_table('B28001')} (Types of Computers in Household)."),

    # --- wellbeing --------------------------------------------------------
    "pct_uninsured": (
        "Percent of the civilian noninstitutionalized population with no "
        "health insurance coverage. Universe: civilian noninstitutionalized "
        "population — people on active duty and people in institutions are "
        "outside it. The \"No health insurance coverage\" lines of "
        f"{acs_table('B27001')} over line 1, resolved from the table shells "
        "by label (9 age groups × 2 sexes = 18 lines for this vintage) "
        "rather than hardcoded. Not published for block groups, which is why "
        "there is no block-group twin of this collection."),
    "pct_with_disability": (
        "Percent of the civilian noninstitutionalized population with a "
        "disability, as the ACS's six-question sequence defines it (hearing, "
        "vision, cognitive, ambulatory, self-care, independent living). "
        "Universe: civilian noninstitutionalized population. The \"With a "
        f"disability\" lines of {acs_table('B18101')} over line 1, resolved "
        "from the shells by label (6 age groups × 2 sexes = 12 lines for "
        "this vintage)."),
    "pct_foreign_born": (
        "Percent of the population that is foreign-born — anyone not a U.S. "
        "citizen at birth, naturalized citizens included. Universe: total "
        f"population. Line 13 (\"Foreign-born\") over line 1 of "
        f"{acs_table('B05002')} (Place of Birth by Nativity and Citizenship "
        "Status). People born abroad to American parents (line 12) are "
        "native-born and are not in this share."),
    "group_quarters_pop": (
        "Population living in group quarters — correctional facilities, "
        "nursing facilities, college and university housing, military "
        "quarters, group homes, shelters. Universe: population in group "
        f"quarters. Line 1 of {acs_table('B26001')}, published as an "
        "integer. A large value next to a small household population "
        "usually explains an odd median: a prison or a dorm dominates the "
        "geography."),
    "median_hh_income_black": (
        "Median household income in the past 12 months (2024 "
        "inflation-adjusted dollars) for households whose householder is "
        "Black or African American alone. Universe: households with a "
        "householder who is Black or African American alone. Line 1 of "
        f"{acs_table('B19013B')}, the B race iteration of "
        f"{acs_table('B19013')}. Classified by the householder's race, not "
        "by every member's."),
    "median_hh_income_white_nh": (
        "Median household income in the past 12 months (2024 "
        "inflation-adjusted dollars) for households whose householder is "
        "White alone, not Hispanic or Latino. Universe: households with a "
        "householder who is White alone, not Hispanic or Latino. Line 1 of "
        f"{acs_table('B19013H')} (the H iteration)."),
    "median_hh_income_asian": (
        "Median household income in the past 12 months (2024 "
        "inflation-adjusted dollars) for households whose householder is "
        "Asian alone. Universe: households with a householder who is Asian "
        f"alone. Line 1 of {acs_table('B19013D')} (the D iteration)."),
    "median_hh_income_hispanic": (
        "Median household income in the past 12 months (2024 "
        "inflation-adjusted dollars) for households whose householder is "
        "Hispanic or Latino, of any race. Universe: households with a "
        "householder who is Hispanic or Latino. Line 1 of "
        f"{acs_table('B19013I')} (the I iteration)."),
    "pct_below_poverty_black": (
        "Percent of the Black or African American alone population below the "
        "poverty level. Universe: Black or African American alone population "
        "for whom poverty status is determined — a race-specific universe, "
        "so this is not comparable to `pct_below_poverty`'s denominator. "
        "Line 2 (\"Income in the past 12 months below poverty level\") over "
        f"line 1 of {acs_table('B17020B')}."),
}

# --------------------------------------------------------------------------
# Block columns (2020 P.L. 94-171)
# --------------------------------------------------------------------------

_PL_SRC = (
    f"Read from the 2020 P.L. 94-171 redistricting file at the field "
    f"position pinned in `docs/blocks-build-notes.md` against the Census "
    f"Bureau's own R import scripts")

BLOCK_DOC = {
    "pop_total": (
        "Total population of the block, from the 2020 Decennial Census. "
        f"Universe: total population. Table P1, cell 1 (`P0010001`) of "
        f"{pl_table('P1')}. {_PL_SRC}. A complete count, not a survey "
        "estimate, so there is no margin of error — but it is protected by "
        "the 2020 disclosure-avoidance system, which injects noise at the "
        "block level and exact-counts states. Blocks tile their state "
        "exhaustively: summed over the 50 states and DC this column equals "
        "331,449,281, the published 2020 resident population, exactly. "
        "28.97% of all 8,174,955 blocks have a population of 0 (measured)."),
    "pop_white": (
        "Population reporting White alone. Universe: total population. Table "
        f"P1, cell 3 (`P0010003`) of {pl_table('P1')} — a race-alone count, "
        "crossing Hispanic origin, so it is not comparable to "
        "`pop_white_nh`."),
    "pop_black": (
        "Population reporting Black or African American alone. Universe: "
        f"total population. Table P1, cell 4 (`P0010004`) of "
        f"{pl_table('P1')}. Race alone, crossing Hispanic origin."),
    "pop_aian": (
        "Population reporting American Indian and Alaska Native alone. "
        "Universe: total population. Table P1, cell 5 (`P0010005`) of "
        f"{pl_table('P1')}."),
    "pop_asian": (
        "Population reporting Asian alone. Universe: total population. Table "
        f"P1, cell 6 (`P0010006`) of {pl_table('P1')}."),
    "pop_nhpi": (
        "Population reporting Native Hawaiian and Other Pacific Islander "
        "alone. Universe: total population. Table P1, cell 7 (`P0010007`) of "
        f"{pl_table('P1')}."),
    "pop_other": (
        "Population reporting Some Other Race alone. Universe: total "
        f"population. Table P1, cell 8 (`P0010008`) of {pl_table('P1')}."),
    "pop_two_plus": (
        "Population reporting two or more races. Universe: total population. "
        f"Table P1, cell 9 (`P0010009`) of {pl_table('P1')}. The seven "
        "race-alone columns plus this one sum exactly to `pop_total`; P1's "
        "cell 2 (\"Population of one race\") is an intermediate subtotal and "
        "is deliberately not carried, which is why the sum closes."),
    "pop_hispanic": (
        "Population of Hispanic or Latino origin, of any race. Universe: "
        f"total population. Table P2, cell 2 (`P0020002`) of "
        f"{pl_table('P2')}. Hispanic origin is asked separately from race, "
        "so this crosses all seven race columns."),
    "pop_white_nh": (
        "Population reporting White alone and not Hispanic or Latino. "
        "Universe: total population. Table P2, cell 5 (`P0020005`) of "
        f"{pl_table('P2')} — the not-Hispanic branch, so this is a subset "
        "of `pop_white` and the two are not interchangeable."),
    "vap_total": (
        "Voting-age population: people 18 years and over. Universe: "
        "population 18 years and over. Table P3, cell 1 (`P0030001`) of "
        f"{pl_table('P3')}. The table this column comes from is the one "
        "P.L. 94-171 exists to publish — the race detail behind redistricting "
        "— and `pop_total − vap_total` is the under-18 population."),
    "housing_units": (
        "Total housing units in the block, occupied and vacant. Universe: "
        f"housing units. Table H1, cell 1 (`H0010001`) of {pl_table('H1')}. "
        "A complete count of units, not of households."),
    "housing_occupied": (
        "Occupied housing units. Universe: housing units. Table H1, cell 2 "
        f"(`H0010002`) of {pl_table('H1')}. `housing_occupied + "
        "housing_vacant == housing_units` holds on every block in this "
        "collection; the build checks it (0 violations)."),
    "housing_vacant": (
        "Vacant housing units. Universe: housing units. Table H1, cell 3 "
        f"(`H0010003`) of {pl_table('H1')}. Includes seasonal, for-rent and "
        "for-sale units, so it is not a measure of abandonment."),
    "group_quarters_pop": (
        "Population living in group quarters — correctional facilities, "
        "juvenile facilities, nursing facilities, college/university "
        "housing, military quarters, other group quarters. Universe: "
        "population in group quarters. Table P5, cell 1 (`P0050001`) of "
        f"{pl_table('P5')}. Group-quarters residents are included in "
        "`pop_total` but live in no housing unit, which is how a block can "
        "hold hundreds of people and few or no units."),
    "pct_white_nh": (
        "`pop_white_nh` as a percent of `pop_total`, 2 decimals. Universe: "
        "total population. NULL where `pop_total` is 0 — 28.97% of blocks "
        "(measured), because roughly three in ten census blocks are "
        "unpopulated by design. That is a property of census blocks, not "
        "missing data: filter `pop_total > 0` before averaging."),
    "pct_black": (
        "`pop_black` as a percent of `pop_total`, 2 decimals. Universe: "
        "total population — and note the numerator is race-alone, crossing "
        "Hispanic origin, unlike the ACS collections' `pct_black`. NULL "
        "where `pop_total` is 0 (28.97% of blocks, measured)."),
    "pct_hispanic": (
        "`pop_hispanic` as a percent of `pop_total`, 2 decimals. Universe: "
        "total population. NULL where `pop_total` is 0 (28.97% of blocks, "
        "measured)."),
    "pct_vacant": (
        "`housing_vacant` as a percent of `housing_units`, 2 decimals. "
        "Universe: housing units. NULL where the block has no housing units "
        "— 27.64% of blocks (measured)."),
}

# --------------------------------------------------------------------------
# Margin of error, coefficient of variation
# --------------------------------------------------------------------------

MOE_BASE = ("Margin of error for `{col}` at the 90% confidence level, the "
            "level the Census Bureau publishes.")

# One sentence per `kind`, naming the arithmetic the build applied. Formulas
# are the Census Bureau's own, from ACS Accuracy of the Data
# (see ACCURACY_URL); the implementation is in tools/build_acs.py.
MOE_BY_KIND = {
    "count": (" Component margins add in quadrature — `sqrt(Σ moe²)` — "
              "which is the Census Bureau's formula for the margin of a sum. "
              "NULL when every component is a jam value."),
    "median": (" Published as the Census Bureau publishes it for this line. "
               "A median's margin cannot be recomputed from a distribution, "
               "so it is passed through untouched."),
    "pct": (" Propagated with the Census Bureau's proportion formula, "
            "`sqrt(moe_num² − p²·moe_den²) / den`, falling back to the ratio "
            "formula (`+` instead of `−`) when the radicand goes negative "
            "because the numerator is not a true subset of the denominator. "
            "Multiplied by 100 to match the percentage, rounded to 2 "
            "decimals, and NULL rather than guessed when an input margin is "
            "NULL or the denominator is 0."),
    "complement": (" A complement carries the margin of error of the share "
                   "it was taken from, unchanged — `100 − p` has the same "
                   "sampling error as `p`."),
}

CV_DOC = (
    "Coefficient of variation for `{col}`: `moe / 1.645 / estimate`, rounded "
    "to 3 decimals — the standard error as a fraction of the estimate, with "
    "1.645 converting the published 90% margin back to a standard error. A "
    "rule of thumb: under 0.12 reliable, 0.12–0.40 use with caution, over "
    "0.40 unreliable. NULL when the estimate is NULL or 0, or the margin of "
    "error is NULL. Published on the headline statistics so a map can grey "
    "out the geographies whose value is swamped by its own error instead of "
    "drawing them as if certain.")

# --------------------------------------------------------------------------
# Per-column, per-level quirk notes
# --------------------------------------------------------------------------

# (column, level) -> sentence appended to the column's description. Every
# rate below is from docs/acs-build-notes.md's validation pass (counted, not
# estimated) or measured here against the published parquet.
NULL_NOTES = {
    ("population", "bg"):
        "NULL on 0.18% of block groups — the island areas (405 block groups "
        "with 2024 boundaries but no ACS data) and the 39 Suffolk County, NY "
        "block groups re-delineated in this vintage.",
    ("population", "tract"):
        "NULL on 0.16% of tracts: 126 island-area tracts plus 14 in Suffolk "
        "County, NY.",
    ("population", "county"):
        "NULL on 0.40% of counties — the 13 island-area county equivalents "
        "(AS 5, GU 1, MP 4, VI 3), which have cartographic boundaries but no "
        "ACS 5-year estimates.",
    ("population", "state"):
        "NULL on 4 of 56 rows: American Samoa, Guam, the Northern Mariana "
        "Islands and the U.S. Virgin Islands have boundaries here but no ACS "
        "5-year data, because the island areas run a separate "
        "decennial-only program. 52 rows carry data.",
    ("median_hh_income", "bg"):
        "**NULL on 7.69% of block groups.** The Census Bureau suppresses "
        "(jams) a median when the sample behind it is too thin, which at "
        "block-group scale is often; the comparable tract rate is 1.59%. "
        "Where it is present the margin can still be wide — check "
        "`median_hh_income_cv`.",
    ("median_hh_income", "tract"):
        "NULL on 1.59% of tracts (7.69% of block groups, for comparison).",
    ("per_capita_income", "bg"):
        "NULL on 0.99% of block groups. Part of that is an upstream coverage "
        f"gap rather than suppression: {acs_table('B19301')} publishes "
        "242,069 block-group rows against 242,297 for "
        f"{acs_table('B01003')}, and the missing 228 come through as NULL.",
    ("median_gross_rent", "bg"):
        "**NULL on 29.68% of block groups** — nearly a third. A block group "
        "with few renter households paying cash rent has no publishable rent "
        "median; the tract rate is 5.92%. Map this at block-group scale only "
        "if the holes are acceptable, or move up to tracts.",
    ("median_gross_rent", "tract"):
        "NULL on 5.92% of tracts (29.68% of block groups, for comparison).",
    ("median_home_value", "bg"):
        "**NULL on 10.03% of block groups** — a block group with few "
        "owner-occupied units has no publishable value median. The tract "
        "rate is 3.55%.",
    ("median_home_value", "tract"):
        "NULL on 3.55% of tracts.",
    ("pct_rent_burdened", "bg"):
        "NULL on 7.91% of block groups, where the denominator (renter "
        "households whose ratio could be computed) came out at or below 0.",
    ("pct_rent_burdened", "tract"):
        "NULL on 1.51% of tracts.",
    ("median_hh_income_black", "tract"):
        "**NULL on 61.43% of tracts** (39.47% of counties): wherever too few "
        "Black-householder households live in the tract for the Census "
        "Bureau to publish a median. A map of this column is as much a map "
        "of where the group lives as of its income — read the NULLs as "
        "\"not published here\", never as a value.",
    ("median_hh_income_black", "county"):
        "NULL on 39.47% of counties, wherever the group has too few "
        "households for a published median.",
    ("median_hh_income_asian", "tract"):
        "**NULL on 71.27% of tracts** (53.63% of counties) — the sparsest "
        "column in the catalog. Present only where the Asian-householder "
        "sample supports a median.",
    ("median_hh_income_asian", "county"):
        "NULL on 53.63% of counties.",
    ("median_hh_income_hispanic", "tract"):
        "**NULL on 44.43% of tracts** (19.60% of counties).",
    ("median_hh_income_hispanic", "county"):
        "NULL on 19.60% of counties.",
    ("median_hh_income_white_nh", "tract"):
        "NULL on 10.04% of tracts (2.38% of counties) — the least sparse of "
        "the four race-iteration medians, which is itself a fact about the "
        "distribution of the population.",
    ("median_hh_income_white_nh", "county"):
        "NULL on 2.38% of counties.",
    ("pct_below_poverty_black", "tract"):
        "NULL on 12.84% of tracts (measured): no Black-alone population for "
        "whom poverty status is determined, so no rate.",
    ("pct_below_poverty_black", "county"):
        "NULL on 5.87% of counties (measured).",
    ("group_quarters_pop", "tract"):
        "NULL on 0.16% of tracts — the island-area and re-delineated "
        "geographies, not suppression.",
    ("pct_uninsured", "tract"):
        "NULL on 0.94% of tracts. Not published for block groups at all.",
    ("pct_with_disability", "tract"):
        "NULL on 0.94% of tracts. Not published for block groups at all.",
    ("pct_no_internet", "bg"):
        "NULL on 1.13% of block groups.",
    ("pct_no_computer", "bg"):
        "NULL on 1.13% of block groups.",

    # --- wave 3: ZCTAs, places, congressional districts -------------------
    # Every rate below was counted by tools/build_acs.py --validate on the
    # published file (docs/acs-build-notes.md, "Wave 3").
    ("population", "zcta"):
        "NULL on 0.06% of ZCTAs — the 19 ZCTAs that have a 2020 "
        "cartographic boundary but no row in the ACS tabulation (17 in the "
        "island areas, plus 11717 and 11798 in Suffolk County, New York).",
    ("population", "place"):
        "NULL on 0.86% of places — the 282 places with 2024 boundaries but "
        "no ACS row: 279 in the island areas (MP 135, AS 77, GU 57, VI 10), "
        "Brentwood CDP and Wyandanch CDP in Suffolk County, New York, and "
        "Louisville city, Kentucky, whose ACS tabulation is the consolidated "
        "`2148006` Louisville/Jefferson County metro government (balance).",
    ("population", "cd"):
        "NULL on 0.91% of districts — the four island-area delegate "
        "districts (American Samoa, Guam, the Northern Mariana Islands, the "
        "U.S. Virgin Islands), which have 2024 boundaries but no ACS 5-year "
        "estimates. Every other column in this collection is NULL on the "
        "same four rows and nowhere else.",
    ("median_hh_income", "zcta"):
        "**NULL on 9.60% of ZCTAs.** A ZCTA with few households has no "
        "publishable median — the rate sits between the tract (1.59%) and "
        "block-group (7.69%) rates because a rural ZCTA is large but a "
        "single-building urban one is tiny.",
    ("median_hh_income", "place"):
        "**NULL on 12.71% of places.** Thousands of places in the file are "
        "villages and CDPs of a few hundred people, which is where the "
        "Census Bureau's suppression bites; the population-weighted "
        "coverage is far better than the row-weighted rate suggests.",
    ("median_gross_rent", "zcta"):
        "**NULL on 23.79% of ZCTAs** — nearly a quarter. A ZCTA with few "
        "renter households paying cash rent has no publishable rent median.",
    ("median_gross_rent", "place"):
        "**NULL on 31.32% of places** — a third of them, mostly small "
        "places with few cash-renting households.",
    ("median_home_value", "zcta"):
        "NULL on 10.45% of ZCTAs.",
    ("median_home_value", "place"):
        "NULL on 12.78% of places.",
    ("pct_rent_burdened", "zcta"):
        "NULL on 10.96% of ZCTAs, where the denominator (renter households "
        "whose rent-to-income ratio could be computed) came out at or below "
        "0.",
    ("pct_rent_burdened", "place"):
        "NULL on 14.60% of places, where the denominator (renter households "
        "whose rent-to-income ratio could be computed) came out at or below "
        "0.",
    ("median_hh_income_black", "zcta"):
        "**NULL on 69.25% of ZCTAs** (79.24% of places), wherever too few "
        "Black-householder households live there for a published median. A "
        "map of this column is as much a map of where the group lives as of "
        "its income.",
    ("median_hh_income_black", "place"):
        "**NULL on 79.24% of places.**",
    ("median_hh_income_asian", "zcta"):
        "**NULL on 76.59% of ZCTAs** (85.80% of places) — the sparsest "
        "column at this geography.",
    ("median_hh_income_asian", "place"):
        "**NULL on 85.80% of places** — the sparsest column in the catalog.",
    ("median_hh_income_asian", "cd"):
        "NULL on 1.13% of districts: the four island-area delegate "
        "districts plus one district with no published "
        "Asian-householder median.",
    ("median_hh_income_hispanic", "zcta"):
        "**NULL on 58.55% of ZCTAs** (69.35% of places).",
    ("median_hh_income_hispanic", "place"):
        "**NULL on 69.35% of places.**",
    ("median_hh_income_white_nh", "zcta"):
        "NULL on 12.08% of ZCTAs (17.62% of places).",
    ("median_hh_income_white_nh", "place"):
        "NULL on 17.62% of places.",
    ("pct_below_poverty_black", "zcta"):
        "NULL on 36.59% of ZCTAs: no Black-alone population for whom "
        "poverty status is determined, so no rate.",
    ("pct_below_poverty_black", "place"):
        "NULL on 46.72% of places: no Black-alone population for whom "
        "poverty status is determined, so no rate.",
}

# Levels where every ACS column inherits the same floor of missingness. Added
# to the first column of each collection would be noise; instead it is stated
# once in the collection description and once here, on `population`.
SPEC_BY_NAME = {s.name: s for s in specs.CONTEXT_SPEC + specs.ALL_SPEC}


def moe_doc(base: str) -> str:
    """Description for `<base>_moe`, keyed off the base column's kind."""
    spec = SPEC_BY_NAME.get(base)
    text = MOE_BASE.format(col=base)
    if spec is not None:
        text += MOE_BY_KIND.get(spec.kind, "")
    return text


def cv_doc(base: str) -> str:
    """Description for `<base>_cv`."""
    return CV_DOC.format(col=base)


def _acs_value_doc(column: str, level: str) -> str | None:
    base = ACS_DOC.get(column)
    if base is None:
        return None
    note = NULL_NOTES.get((column, level))
    return f"{base} {note}" if note else base


def describe(column: str, collection_id: str) -> str | None:
    """The description for one column of one collection, or None.

    None means "undocumented", and `tools/make_stac.py` treats that as a
    build failure rather than writing a column with no description.
    """
    level = LEVEL_OF.get(collection_id)
    if level is None:
        raise KeyError(f"unknown collection id: {collection_id!r}")

    if column == "geoid":
        return GEOID_DOC[level]
    if column in CONTEXT_DOC:
        return CONTEXT_DOC[column](level)

    if level == "block":
        return BLOCK_DOC.get(column)

    doc = _acs_value_doc(column, level)
    if doc:
        return doc
    for suffix, fn in (("_moe", moe_doc), ("_cv", cv_doc)):
        if column.endswith(suffix):
            base = column[: -len(suffix)]
            if base in ACS_DOC:
                return fn(base)
    return None


def columns_for(collection_id: str) -> list[str]:
    """Published column names for a collection, in file order.

    Mirrors what `tools/build_acs.py` writes, so a drift between this module
    and the build shows up as a missing description rather than as silence.
    """
    if collection_id == "blocks":
        return (["geoid", "state"] + list(BLOCK_DOC) +
                ["pop_density", "aland_sqkm", "geometry", "bbox"])
    coll = next(c for c in specs.COLLECTIONS if c.id == collection_id)
    head = ["geoid", "name", "state", "population", "population_moe",
            "aland_sqkm", "pop_density"]
    return head + specs.out_columns(coll.spec) + ["geometry", "bbox"]


def docs_for(collection_id: str) -> dict[str, str]:
    """{column: description} for every column this module can describe."""
    out = {}
    for col in columns_for(collection_id):
        doc = describe(col, collection_id)
        if doc:
            out[col] = doc
    return out


def missing(columns, collection_id: str) -> list[str]:
    """Columns with no description — what make_stac fails on."""
    return [c for c in columns if not describe(c, collection_id)]


def main() -> None:
    """Self-check: every column of every collection has a description."""
    bad = []
    for coll in [c.id for c in specs.COLLECTIONS] + ["blocks"]:
        cols = columns_for(coll)
        gaps = missing(cols, coll)
        print(f"{coll:20s} {len(cols):3d} columns, "
              f"{len(cols) - len(gaps):3d} documented"
              + (f" — MISSING: {', '.join(gaps)}" if gaps else ""))
        bad += [(coll, g) for g in gaps]
    if bad:
        raise SystemExit(f"{len(bad)} undocumented columns")
    print("every column documented")


if __name__ == "__main__":
    main()
