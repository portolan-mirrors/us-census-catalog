#!/usr/bin/env python3
"""Generate MapLibre styles for every collection, with breaks measured
from the NATIONAL distribution of each column.

Three to five styles per collection: one default (the headline indicator for
that theme) plus the variants worth their own card. Every style is a choropleth
`step` on one published column — never a computed expression, because every
band of the PMTiles pyramid carries the same column names (counties at the
national zooms, tracts in the middle, the collection's own features below
that), so one expression classifies every zoom, and a column that exists in
the GeoParquet is the only thing guaranteed to exist in the tiles.

Breaks
------
`--measure` profiles every styled column over its GeoParquet with DuckDB
(row count, null share, min/max, 13 quantiles) and counts how many features
land in each class of the chosen breaks, writing all of it to
docs/style-breaks.json. The generator then reads that file, so a style's
class breaks are reproducible and auditable, and the run fails if

  * a styled column is missing from the parquet schema,
  * breaks are not strictly increasing, or
  * any class is empty nationally (an empty legend swatch is a lie).

Break values are human numbers ($10k steps, whole percents, round densities)
chosen to sit near measured quantiles rather than at exact quantiles, and the
ends are winsorized: the top class starts around the 90th percentile instead
of chasing a $2,000,001 cap or a 3,000,000/km² Manhattan block. Each style's
metadata.description states where its breaks fall in the national distribution,
computed from the measured class counts.

Legend mechanism
----------------
portolan-browser's `extractLegend` (src/utils/portolanStyles.js) walks the
fill and circle layers in order and returns the first whose color is a `step`
or `match` expression with literal colors; `interpolate` and `case` yield
nothing. Here the visible layer IS a fill with a step expression, so it carries
the legend itself — no inert zero-opacity layer needed. Two consequences the
layer order respects:

  * the "no data" underlay is a CONSTANT color, so the legend walk skips it and
    reaches the step layer behind it;
  * noisy-estimate fading lives in `fill-opacity` as a `case`, never in
    `fill-color`, which would destroy the legend.

NULLs
-----
A null must never reach the step expression. "MapLibre evaluates null as the
step's first stop" is NOT true, and it was checked rather than assumed: `step`
parses its input as NumberType (maplibre-gl 5.x, `Step.parse`), so a missing
attribute makes the implicit number assertion throw at evaluate time; the
throw is caught in `StyleExpression.evaluate`, which returns the paint
property's spec default — and the spec default for `fill-color` is `#000000`.
An unfiltered style would paint every null feature solid black, not pale.

So every data layer is filtered to `["has", col]` (tiles omit null attributes
entirely, so `has` is false for them). Where more than 5% of features have no
value — a third of 2020 blocks are unpopulated, 61% of tracts have no
published median income for Black households, four territories have no ACS
estimates at all — a neutral-gray "no data" layer draws underneath with the
inverse filter, so absence reads as absence instead of as the lowest class.

Margins of error
----------------
`*_moe` columns are not in the tiles; `*_cv` columns are. Where a styled column
has a CV, features whose coefficient of variation exceeds 0.30 draw at reduced
opacity: the estimate is published, but its margin of error swamps it. This is
the same stance as the rest of the pipeline (docs/design.md, "Statistical
integrity").

Usage: python3 tools/make_styles.py [--measure]
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import specs  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
BREAKS_JSON = ROOT / "docs" / "style-breaks.json"

# ---------------------------------------------------------------------------
# Where each collection's data and styles live
# ---------------------------------------------------------------------------
# dir is relative to catalog/; the PMTiles sits beside it as <id>.pmtiles and
# its single vector layer is named for the collection id, so every style's
# source-layer is the collection id.
SOURCES = {
    "bg-income": ("block-groups/bg-income", "bg-income.parquet"),
    "bg-people": ("block-groups/bg-people", "bg-people.parquet"),
    "bg-housing": ("block-groups/bg-housing", "bg-housing.parquet"),
    "bg-connectivity": ("block-groups/bg-connectivity",
                        "bg-connectivity.parquet"),
    "tract-income": ("tracts/tract-income", "tract-income.parquet"),
    "tract-people": ("tracts/tract-people", "tract-people.parquet"),
    "tract-housing": ("tracts/tract-housing", "tract-housing.parquet"),
    "tract-connectivity": ("tracts/tract-connectivity",
                           "tract-connectivity.parquet"),
    "tract-wellbeing": ("tracts/tract-wellbeing", "tract-wellbeing.parquet"),
    "counties": ("counties", "counties.parquet"),
    "states": ("states", "states.parquet"),
    "zctas": ("zctas", "zctas.parquet"),
    "places": ("places", "places.parquet"),
    "congressional-districts": ("congressional-districts",
                                "congressional-districts.parquet"),
    "blocks": ("blocks", "state_fips=*/*.parquet"),
    # reference/ (2026-11-15): geography with no demographic columns.
    "urban-areas": ("reference/urban-areas", "urban-areas.parquet"),
    "landmarks-area": ("reference/landmarks-area", "landmarks-area.parquet"),
    "landmarks-point": ("reference/landmarks-point",
                        "landmarks-point.parquet"),
    # DHC subset (2026-11-15): 2020 Census age/sex, household type and
    # tenure, beside the ACS collections at the same geography.
    "bg-age-dec2020": ("block-groups/bg-age-dec2020",
                       "bg-age-dec2020.parquet"),
    "bg-household-dec2020": ("block-groups/bg-household-dec2020",
                             "bg-household-dec2020.parquet"),
    "bg-tenure-dec2020": ("block-groups/bg-tenure-dec2020",
                         "bg-tenure-dec2020.parquet"),
    "tract-age-dec2020": ("tracts/tract-age-dec2020",
                         "tract-age-dec2020.parquet"),
    "tract-household-dec2020": ("tracts/tract-household-dec2020",
                                "tract-household-dec2020.parquet"),
    "tract-tenure-dec2020": ("tracts/tract-tenure-dec2020",
                            "tract-tenure-dec2020.parquet"),
}

# Point collections need a `circle` layer, not the `fill`/`line` pair every
# polygon collection gets. landmarks-point is the only one in this catalog.
POINT_COLLECTIONS = {"landmarks-point"}

# What one feature is, for prose: (singular, plural). The states collection
# holds 50 states plus DC, Puerto Rico and four Island Areas, so its plural
# says so rather than claiming 56 states.
UNIT = {
    "bg-income": ("block group", "block groups"),
    "bg-people": ("block group", "block groups"),
    "bg-housing": ("block group", "block groups"),
    "bg-connectivity": ("block group", "block groups"),
    "tract-income": ("tract", "tracts"),
    "tract-people": ("tract", "tracts"),
    "tract-housing": ("tract", "tracts"),
    "tract-connectivity": ("tract", "tracts"),
    "tract-wellbeing": ("tract", "tracts"),
    "counties": ("county", "counties"),
    "states": ("state", "states and state equivalents"),
    # A ZCTA is not a ZIP code, so the noun never says "ZIP code"; places are
    # incorporated places and census designated places together; the
    # congressional-districts collection holds the 435 voting districts plus
    # the DC and PR delegate districts and the four island-area delegate
    # districts, so its plural says districts, not "congressional districts".
    "zctas": ("ZCTA", "ZIP Code Tabulation Areas"),
    "places": ("place", "places"),
    "congressional-districts": ("district", "districts"),
    "blocks": ("block", "blocks"),
    "urban-areas": ("urban area", "urban areas"),
    "landmarks-area": ("landmark", "landmarks"),
    "landmarks-point": ("landmark", "landmarks"),
    "bg-age-dec2020": ("block group", "block groups"),
    "bg-household-dec2020": ("block group", "block groups"),
    "bg-tenure-dec2020": ("block group", "block groups"),
    "tract-age-dec2020": ("tract", "tracts"),
    "tract-household-dec2020": ("tract", "tracts"),
    "tract-tenure-dec2020": ("tract", "tracts"),
}

# ---------------------------------------------------------------------------
# Ramps
# ---------------------------------------------------------------------------
# One ramp per style, picked so that sibling collections' default styles —
# the cards in the browser — read apart at a glance: income is viridis,
# people is magma, housing is amber-brown, connectivity is blue, wellbeing is
# yellow-red. Within a theme the secondary styles take neighbouring hues.
# All ramps are perceptually ordered light-to-dark or dark-to-light, and none
# ends at pure white or pure black, so they survive a dark basemap.
RAMPS = {
    # viridis, dark purple (low) to yellow (high) — perceptually uniform and
    # colour-vision-deficiency safe; the money ramp, used at every geography
    # so an income map reads the same from blocks groups to states.
    "viridis7": ["#440154", "#443983", "#31688e", "#21918c", "#35b779",
                 "#90d743", "#fde725"],
    "viridis6": ["#440154", "#414487", "#2a788e", "#22a884", "#7ad151",
                 "#fde725"],
    # magma reversed, pale cream (empty) to deep plum (dense) — population
    # density at every geography.
    "magma7": ["#fcfdbf", "#fec488", "#fe9f6d", "#f1605d", "#b63679",
               "#721f81", "#2d1160"],
    # amber to burnt brown — housing value.
    "amber7": ["#fff3c0", "#fee391", "#fec44f", "#fe9929", "#ec7014",
               "#cc4c02", "#8c2d04"],
    # pale to deep blue — the connectivity theme.
    "pubu6": ["#ebf4fb", "#d0d1e6", "#a6bddb", "#74a9cf", "#2b8cbe",
              "#045a8d"],
    "ylgnbu6": ["#f7f8c8", "#c7e9b4", "#7fcdbb", "#41b6c4", "#2c7fb8",
                "#253494"],
    "ylgn6": ["#f2f7b0", "#d9f0a3", "#addd8e", "#78c679", "#31a354",
              "#006837"],
    "purples6": ["#f2f0f7", "#dadaeb", "#bcbddc", "#9e9ac8", "#756bb1",
                 "#54278f"],
    # yellow to deep red — the wellbeing theme and poverty everywhere.
    "ylorrd6": ["#fff2b0", "#fed976", "#feb24c", "#fd8d3c", "#f03b20",
                "#bd0026"],
    "orrd6": ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33",
              "#b30000"],
    "purd7": ["#f1eef6", "#d4b9da", "#c994c7", "#df65b0", "#e7298a",
              "#ce1256", "#91003f"],
    "rdpu6": ["#feebe2", "#fcc5c0", "#fa9fb5", "#f768a1", "#dd3497",
              "#7a0177"],
    "gnbu6": ["#f0f9e8", "#ccebc5", "#a8ddb5", "#7bccc4", "#43a2ca",
              "#0868ac"],
    "bupu7": ["#e8eff6", "#bfd3e6", "#9ebcda", "#8c96c6", "#8c6bb1",
              "#88419d", "#6e016b"],
    "bugn7": ["#e5f5f9", "#ccece6", "#99d8c9", "#66c2a4", "#41ae76",
              "#238b45", "#005824"],
    "greens7": ["#edf8e9", "#c7e9c0", "#a1d99b", "#74c476", "#41ab5d",
                "#238b45", "#005a32"],
    "greens6": ["#edf8e9", "#c7e9c0", "#a1d99b", "#74c476", "#31a354",
                "#006d2c"],
    "oranges6": ["#feedde", "#fdd0a2", "#fdae6b", "#fd8d3c", "#e6550d",
                 "#a63603"],
    "blues7": ["#eff3ff", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6",
               "#2171b5", "#084594"],
    # sepia — the age of the housing stock.
    "sepia6": ["#f4ecdf", "#e2d0a8", "#c8a97a", "#a67c52", "#7d5636",
               "#4e3220"],
    # cividis, navy to gold — also CVD-safe, and deliberately NOT viridis:
    # the race-specific median incomes are a different statistic from
    # median household income and should not be mistaken for it.
    "cividis6": ["#00224e", "#35456c", "#666970", "#958f5f", "#cab969",
                 "#fee838"],
}

NODATA = "#d9d6d2"   # warm neutral gray: "no published value", not "zero"
OUTLINE = "#4d4d4d"  # dark gray hairline, legible over light and dark fills
OPACITY = 0.8        # fills
OPACITY_NOISY = 0.35  # fills whose CV exceeds CV_LIMIT
CV_LIMIT = 0.30
# Fading noisy estimates only informs the reader while it stays a minority
# report. A block-group poverty rate has a CV above 0.30 in 84% of block
# groups and a tract's no-internet share in 79% of tracts — fade those and the
# map is a wash with no signal left, so above this share the style says so in
# its description instead of dimming almost every feature.
NOISY_FADE_MAX = 35.0


# ---------------------------------------------------------------------------
# Style definitions
# ---------------------------------------------------------------------------
class S:
    """One style: a column, its breaks, its ramp, and reader-facing prose."""

    def __init__(self, file, name, col, breaks, ramp, blurb, fmt="pct",
                 default=False, note=None, fade=True):
        assert len(RAMPS[ramp]) == len(breaks) + 1, (
            f"{file}: {len(breaks) + 1} classes need {len(breaks) + 1} "
            f"colors, ramp {ramp} has {len(RAMPS[ramp])}")
        self.file, self.name, self.col = file, name, col
        self.breaks, self.ramp, self.blurb = breaks, ramp, blurb
        self.fmt, self.default, self.note = fmt, default, note
        self.fade = fade  # False keeps a pair of styles visually comparable


class M:
    """One categorical style: a `match` on a label column, not a `step` on
    a number. Used for reference/ -- feature_type and landmark_kind are
    text, not a measured quantity, so there is no break to choose.

    `categories` is every value drawn its own color, in legend order; any
    other value (including a value this build could not decode) draws
    `other_color`. `--measure` counts every category named here, and the
    generator refuses to publish a style with a zero-count category -- see
    the module docstring's "any class is empty" rule, which this extends
    from step classes to match branches.
    """

    def __init__(self, file, name, col, categories, colors, blurb,
                 other_color=NODATA, default=False):
        assert len(categories) == len(colors), (
            f"{file}: {len(categories)} categories need {len(categories)} "
            f"colors, got {len(colors)}")
        self.file, self.name, self.col = file, name, col
        self.categories, self.colors = categories, colors
        self.blurb, self.default = blurb, default
        self.other_color = other_color
        self.breaks = None  # marks this style as categorical, not numeric


# -- income: ACS 2020-2024, block groups and tracts -------------------------
# Same breaks at both geographies on purpose: tract values are block-group
# values pooled, so a shared scale lets the two maps be compared directly.
#
# `breaks` overrides a style's class breaks by file name, and nothing else
# about it. The five themed children of each wide level (county-*, state-*,
# zcta-*, place-*, cd-*) are these same style sets on their own measured
# breaks: averaging over a whole county or state collapses the national
# spread, so block-group breaks there would leave the top classes with a
# handful of features. The numbers are in WIDE_THEME_BREAKS below, and the
# quantiles behind each one are in docs/style-breaks.json.
def _b(breaks, file, default):
    return (breaks or {}).get(file, default)


def income_styles(breaks=None, extended=True):
    """`extended=False` for bg-income: block groups carry neither
    `gini_index` nor `pct_below_poverty_under_18` (B19083 and B17001 are
    not published at block-group level — see tools/specs.py
    INCOME_SPEC_BG), so the two styles below would reference a column that
    does not exist in that collection's GeoParquet."""
    styles = [
        S("default", "Median household income", "median_hh_income",
          _b(breaks, "default", [40000, 55000, 70000, 90000, 120000, 160000]),
          "viridis7",
          "Median household income, viridis dark purple (low) through teal "
          "and green to yellow (high)", fmt="usd", default=True),
        S("poverty", "People below the poverty line", "pct_below_poverty",
          _b(breaks, "poverty", [5, 10, 20, 30, 40]), "ylorrd6",
          "Share of residents with income below the federal poverty line, "
          "pale yellow to deep red"),
        S("snap", "Households receiving SNAP", "pct_snap",
          _b(breaks, "snap", [3, 8, 15, 25, 40]), "orrd6",
          "Share of households that received SNAP (food stamps) in the past "
          "12 months, cream to dark red"),
        S("unemployment", "Unemployment rate", "pct_unemployed",
          _b(breaks, "unemployment", [2, 4, 6, 9, 14]), "purples6",
          "Unemployed share of the civilian labor force, pale lilac to deep "
          "purple"),
    ]
    if extended:
        styles.append(
            S("gini", "Income inequality (Gini index)", "gini_index",
              _b(breaks, "gini", [0.37, 0.40, 0.43, 0.47, 0.51]), "cividis6",
              "Gini index of household income inequality, 0 (perfect "
              "equality) to 1 (perfect inequality), navy (low) to gold "
              "(high) — not published for block groups", fmt="num"))
        styles.append(
            S("child-poverty", "Children below the poverty line",
              "pct_below_poverty_under_18",
              _b(breaks, "child-poverty", [2, 7, 16, 30, 43]), "rdpu6",
              "Share of residents under 18 with income below the federal "
              "poverty line, pale pink to deep magenta — not published for "
              "block groups"))
    return styles


# -- people -----------------------------------------------------------------
def people_styles(breaks=None):
    return [
        S("default", "Population density", "pop_density",
          _b(breaks, "default", [25, 100, 400, 1000, 2500, 6000]), "magma7",
          "People per square kilometre of land area on roughly logarithmic "
          "steps, pale cream (empty) to deep plum (dense)",
          fmt="dens", default=True),
        S("people-of-color", "People of color", "pct_people_of_color",
          _b(breaks, "people-of-color", [10, 20, 35, 55, 75, 90]), "bupu7",
          "Share of residents who are not non-Hispanic white alone, pale "
          "blue through violet to deep purple"),
        S("seniors", "Residents 65 and over", "pct_65_plus",
          _b(breaks, "seniors", [8, 13, 18, 24, 32]), "oranges6",
          "Share of residents aged 65 or older, pale apricot to burnt "
          "orange"),
        S("education", "Bachelor's degree or higher",
          "pct_bachelors_plus",
          _b(breaks, "education", [10, 18, 28, 40, 55, 70]), "bugn7",
          "Share of adults 25 and over holding a bachelor's degree or more, "
          "pale aqua to deep teal"),
    ]


# -- housing ----------------------------------------------------------------
def housing_styles(breaks=None):
    return [
        S("default", "Median home value", "median_home_value",
          _b(breaks, "default",
             [125000, 200000, 275000, 375000, 550000, 850000]), "amber7",
          "Median value of owner-occupied homes, pale amber to burnt brown",
          fmt="usd", default=True),
        S("rent-burden", "Renters paying 30%+ of income",
          "pct_rent_burdened",
          _b(breaks, "rent-burden", [25, 35, 45, 55, 70, 85]), "purd7",
          "Share of renter households spending 30% or more of income on "
          "gross rent — the federal definition of rent-burdened — pale mauve "
          "to deep magenta"),
        S("vacancy", "Vacant housing units", "pct_vacant_units",
          _b(breaks, "vacancy", [3, 7, 12, 18, 30]), "orrd6",
          "Share of housing units vacant, cream to dark red; seasonal and "
          "recreational housing drives the high end as much as abandonment "
          "does"),
        S("pre-1940", "Homes built before 1940", "pct_built_pre_1940",
          _b(breaks, "pre-1940", [2, 8, 20, 35, 55]), "sepia6",
          "Share of housing units built in 1939 or earlier, pale parchment "
          "to dark sepia"),
        S("ownership", "Owner-occupied homes", "pct_owner_occupied",
          _b(breaks, "ownership", [25, 45, 60, 75, 88, 95]), "greens7",
          "Share of occupied housing units lived in by their owner, pale to "
          "deep green"),
    ]


# -- connectivity -----------------------------------------------------------
def connectivity_styles(breaks=None):
    return [
        S("default", "No home internet", "pct_no_internet",
          _b(breaks, "default", [2, 5, 9, 14, 22]), "pubu6",
          "Share of households with no internet subscription of any kind, "
          "pale to deep blue", default=True),
        S("no-vehicle", "Households without a vehicle",
          "pct_hh_no_vehicle",
          _b(breaks, "no-vehicle", [2, 5, 10, 20, 35]), "ylgnbu6",
          "Share of households with no vehicle available, pale yellow "
          "through teal to navy"),
        S("transit-commute", "Commute by public transit",
          "pct_commute_transit",
          _b(breaks, "transit-commute", [0.5, 2, 5, 10, 25]), "ylgn6",
          "Share of workers commuting by public transportation, pale yellow "
          "to dark green; the first class is deliberately narrow because "
          "most of the country has effectively none"),
        S("work-from-home", "Work from home", "pct_work_from_home",
          _b(breaks, "work-from-home", [4, 8, 13, 20, 30]), "purples6",
          "Share of workers whose usual commute is none — they worked from "
          "home — pale lilac to deep purple"),
    ]


BG_TRACT = {
    "income": income_styles, "people": people_styles,
    "housing": housing_styles, "connectivity": connectivity_styles,
}

STYLES = {}
for _theme, _fn in BG_TRACT.items():
    STYLES[f"bg-{_theme}"] = (income_styles(extended=False) if _theme == "income"
                              else _fn())
    STYLES[f"tract-{_theme}"] = _fn()

# -- tract-wellbeing --------------------------------------------------------
# The two race-specific medians share one break set and one ramp on purpose:
# switching between the styles reads as the income gap, with no derived
# column invented to hold it. Black-household medians are published for only
# a minority of tracts, so that style leans on the no-data layer.
WELLBEING_INCOME = [30000, 45000, 60000, 85000, 120000]


def wellbeing_styles(breaks=None, unit="tract"):
    shared = _b(breaks, "income-pair", WELLBEING_INCOME)
    return [
        S("default", "People without health insurance", "pct_uninsured",
          _b(breaks, "default", [2, 4, 7, 11, 18]), "ylorrd6",
          "Share of the civilian non-institutionalized population with no "
          "health insurance coverage, pale yellow to deep red", default=True),
        S("disability", "People with a disability", "pct_with_disability",
          _b(breaks, "disability", [8, 11, 14, 17, 22]), "rdpu6",
          "Share of the civilian non-institutionalized population reporting "
          "a disability, pale pink to deep magenta"),
        S("foreign-born", "Foreign-born residents", "pct_foreign_born",
          _b(breaks, "foreign-born", [2, 5, 10, 18, 30]), "gnbu6",
          "Share of residents born outside the United States, pale green to "
          "deep blue"),
        S("income-black-households", "Median income, Black households",
          "median_hh_income_black", shared, "cividis6",
          "Median household income for Black or African American "
          "householders (ACS table B19013B), cividis navy (low) to gold "
          "(high)", fmt="usd", fade=False,
          note="Shares its breaks and ramp with the white non-Hispanic "
               "style, so switching between the two shows the gap directly; "
               f"the Census publishes this estimate only where the {unit}'s "
               "Black household count supports one"),
        S("income-white-households", "Median income, white non-Hispanic "
          "households", "median_hh_income_white_nh", shared, "cividis6",
          "Median household income for white, non-Hispanic householders (ACS "
          "table B19013H), on the same scale as the Black-household style",
          fmt="usd", fade=False,
          note="Same breaks, ramp and opacity rule as the Black-household "
               "style — neither fades its noisy estimates, because fading "
               "only one of the pair would make the gap look like a "
               "difference in confidence"),
    ]


STYLES["tract-wellbeing"] = wellbeing_styles()

# -- DHC subset (2026-11-15): 2020 Census age/sex, household type, tenure --
# Same breaks at bg and tract, same reasoning as income_styles: tract values
# pool block-group values, so a shared scale lets the two maps compare
# directly. No style here has a `_cv` column to fade on -- these are 100%
# counts, not estimates -- so `fades()` is a no-op for every one of them,
# which is the point: nothing here fabricates an uncertainty indicator.
def age_styles():
    return [
        S("default", "Population 65 and over", "pct_65plus",
          [8, 12, 16, 20, 25], "ylgn6",
          "Share of the 2020 Census population age 65 and over, pale "
          "yellow-green (low) to deep green (high) -- a 100% count, not "
          "the ACS people collections' pct_65_plus estimate", default=True),
        S("under18", "Population under 18", "pct_under18",
          [18, 22, 26, 30, 35], "oranges6",
          "Share of the 2020 Census population under 18, pale to deep "
          "orange -- a 100% count, not the ACS people collections' "
          "pct_under_18 estimate"),
    ]


def household_styles():
    return [
        S("default", "Family households", "pct_family_households",
          [50, 60, 68, 76, 84], "cividis6",
          "Share of households that are family households (P16), dark "
          "blue through tan to yellow. The connectivity collections own "
          "the blue ramp and the reference group owns the purple ramp, "
          "so either would read as the same dataset in a card grid",
          default=True),
        S("living-alone", "Householders living alone", "pct_living_alone",
          [18, 24, 30, 36, 44], "greens6",
          "Share of households whose householder lives alone (P16), "
          "pale to deep green"),
    ]


def tenure_styles():
    return [
        S("default", "Owner-occupied housing", "pct_owned",
          [40, 55, 65, 75, 85], "rdpu6",
          "Share of occupied housing units that are owner-occupied (H4), "
          "pale pink to deep magenta -- a 100% count, not the ACS "
          "housing collections' pct_owner_occupied estimate. Neither "
          "blue nor green: connectivity owns the blue ramp and age the "
          "green one, and a blue-green tested too close to connectivity "
          "at card size. Pink is the one hue path no other default "
          "style in this catalog uses", default=True),
        S("vacant", "Vacant housing units", "pct_vacant_2020",
          [3, 6, 10, 15, 25], "orrd6",
          "Vacant share of all housing units (H1 minus H4's occupied "
          "total), cream to deep red -- a 100% count, not the ACS "
          "housing collections' pct_vacant_units estimate"),
    ]


DHC_BG_TRACT = {"age": age_styles, "household": household_styles,
               "tenure": tenure_styles}
for _dhc_theme, _dhc_fn in DHC_BG_TRACT.items():
    STYLES[f"bg-{_dhc_theme}-dec2020"] = _dhc_fn()
    STYLES[f"tract-{_dhc_theme}-dec2020"] = _dhc_fn()

# -- counties and states ----------------------------------------------------
# Averaging over a whole county or state collapses the national spread, so
# these get their own, tighter breaks: block-group breaks would leave the top
# classes with a handful of features and the middle class with a third of the
# country.
STYLES["counties"] = [
    S("default", "Median household income", "median_hh_income",
      [45000, 55000, 65000, 75000, 90000, 110000], "viridis7",
      "Median household income by county, viridis dark purple (low) to "
      "yellow (high)", fmt="usd", default=True),
    S("density", "Population density", "pop_density",
      [2, 8, 20, 50, 150, 600], "magma7",
      "People per square kilometre on roughly logarithmic steps, pale cream "
      "to deep plum", fmt="dens"),
    S("poverty", "People below the poverty line", "pct_below_poverty",
      [8, 11, 14, 18, 25], "ylorrd6",
      "Share of residents with income below the federal poverty line, pale "
      "yellow to deep red"),
    S("home-value", "Median home value", "median_home_value",
      [110000, 150000, 200000, 275000, 400000, 650000], "amber7",
      "Median value of owner-occupied homes, pale amber to burnt brown",
      fmt="usd"),
]

STYLES["states"] = [
    S("default", "Median household income", "median_hh_income",
      [55000, 65000, 75000, 85000, 100000], "viridis6",
      "Median household income by state, viridis dark purple (low) to "
      "yellow (high)", fmt="usd", default=True),
    S("density", "Population density", "pop_density",
      [5, 15, 40, 80, 150, 400], "magma7",
      "People per square kilometre on roughly logarithmic steps, pale cream "
      "to deep plum", fmt="dens"),
    S("poverty", "People below the poverty line", "pct_below_poverty",
      [10, 12, 14, 17, 22], "ylorrd6",
      "Share of residents with income below the federal poverty line, pale "
      "yellow to deep red"),
    S("home-value", "Median home value", "median_home_value",
      [175000, 225000, 275000, 350000, 450000, 600000], "amber7",
      "Median value of owner-occupied homes, pale amber to burnt brown",
      fmt="usd"),
]

# -- wave 3: ZCTAs, places, congressional districts -------------------------
# Measured, not copied. The three distributions sit in different places from
# the counties one and from each other (docs/style-breaks.json has the
# quantiles behind every number below):
#   ZCTAs      spread almost as wide as tracts — median income p10 46k /
#              p50 72k / p90 119k, density p50 31/km² — because a rural ZCTA
#              is a county-sized polygon and an urban one is a few blocks.
#   places     poorer and denser than ZCTAs at the median (income p50 67k,
#              density p50 274/km²): a place is a settlement, so the empty
#              half of the country is simply absent from the file.
#   districts  the tightest distribution in the catalog by construction —
#              every district holds ~770,000 people, so median income runs
#              p10 61k / p50 79k / p90 114k and poverty p10 7% / p90 18%.
#              Counties breaks here would leave three of six classes with a
#              handful of districts.
def _wave3_styles(income, density, poverty, home_value, unit):
    return [
        S("default", "Median household income", "median_hh_income",
          income, "viridis7",
          f"Median household income by {unit}, viridis dark purple (low) to "
          f"yellow (high)", fmt="usd", default=True),
        S("density", "Population density", "pop_density", density, "magma7",
          "People per square kilometre on roughly logarithmic steps, pale "
          "cream to deep plum", fmt="dens"),
        S("poverty", "People below the poverty line", "pct_below_poverty",
          poverty, "ylorrd6",
          "Share of residents with income below the federal poverty line, "
          "pale yellow to deep red"),
        S("home-value", "Median home value", "median_home_value",
          home_value, "amber7",
          "Median value of owner-occupied homes, pale amber to burnt brown",
          fmt="usd"),
    ]


STYLES["zctas"] = _wave3_styles(
    [45000, 60000, 72000, 87000, 120000, 160000],
    [5, 20, 60, 200, 600, 2000],
    [5, 9, 13, 19, 28],
    [100000, 160000, 225000, 325000, 500000, 800000],
    "ZIP Code Tabulation Area")
STYLES["places"] = _wave3_styles(
    [40000, 55000, 67000, 84000, 115000, 150000],
    [50, 125, 250, 500, 1000, 2000],
    [5, 9, 14, 20, 30],
    [85000, 130000, 190000, 290000, 450000, 750000],
    "place")
STYLES["congressional-districts"] = _wave3_styles(
    [60000, 70000, 79000, 91000, 110000, 130000],
    [25, 75, 200, 600, 1500, 4000],
    [8, 10, 12, 15, 19],
    [185000, 250000, 335000, 450000, 650000, 900000],
    "congressional district")

# -- the themed children of the five wide levels (2026-11-15) ---------------
# Each wide level is now a group with five themed children mirroring the
# tract set, so each child carries its theme's style set — county-income gets
# the tract-income styles, county-people the tract-people styles, and so on,
# same files, same columns, same ramps, same prose.
#
# Only the class breaks differ, and every number below was measured on that
# child's own parquet (quantiles, class counts and null shares in
# docs/style-breaks.json): a county is a pooled average of its tracts, so
# tract breaks here would pile three quarters of the country into the middle
# class and leave the ends with a handful of features.
#
# Breaks were snapped to human numbers near the p10/p30/p50/p70/p88/p95
# quantiles for a six-break ramp and p20/p40/p60/p78/p91 for a five-break
# one — the same percentile shape the wave-3 collections' breaks sit on —
# then checked class by class, because the generator refuses an empty legend
# swatch. Two deliberate reuses:
#
#   * median_hh_income, pop_density, pct_below_poverty and median_home_value
#     take their level's EXISTING wide-table breaks wherever the ramp width
#     matches, so the child and its wide parent draw the same map of the same
#     column. (state-income's default is the exception: the wide states style
#     has five breaks and this ramp wants six.)
#   * transit-commute keeps the catalog-wide [0.5, 2, 5, 10, 25] scale at
#     every level where no class comes out empty, so a transit map reads the
#     same from block groups to congressional districts. Only states needs
#     its own ([0.5, 1, 3, 8, 20]): no state reaches the 25% top class, New
#     York's 21.6% being the national maximum.
WIDE_THEME_BREAKS = {
    "county": {
        "income": {
            "default": [45000, 55000, 65000, 75000, 90000, 110000],
            "poverty": [8, 11, 14, 18, 25],
            "snap": [7, 10, 14, 17, 24],
            "unemployment": [3, 4, 5, 6, 8],
            "gini": [0.42, 0.44, 0.46, 0.48, 0.50],
            "child-poverty": [10, 15, 19, 26, 32],
        },
        "people": {
            "default": [2, 8, 20, 50, 150, 600],
            "people-of-color": [7, 12, 20, 36, 58, 75],
            "seniors": [17, 19, 21, 24, 27],
            "education": [14, 19, 22, 27, 36, 45],
        },
        "housing": {
            "default": [110000, 150000, 200000, 275000, 400000, 650000],
            "rent-burden": [30, 40, 45, 50, 55, 58],
            "vacancy": [8, 12, 16, 22, 30],
            "pre-1940": [4, 7.5, 14, 23, 32],
            "ownership": [62, 70, 75, 78, 82, 85],
        },
        "connectivity": {
            "default": [6.5, 9, 11, 14, 18],
            "no-vehicle": [3.5, 5, 6, 7.5, 10],
            "work-from-home": [5.5, 7.5, 9.5, 12, 17],
        },
        "wellbeing": {
            "default": [5, 6.5, 9, 12, 16],
            "disability": [13, 15, 17, 20, 23],
            "foreign-born": [1.25, 2, 4, 6.5, 12],
            "income-pair": [45000, 60000, 70000, 80000, 95000],
        },
    },
    "state": {
        "income": {
            "default": [55000, 65000, 75000, 85000, 95000, 105000],
            "poverty": [10, 12, 14, 17, 22],
            "snap": [8.5, 11, 12, 14, 16],
            "unemployment": [3.5, 4.5, 5, 6, 6.5],
            "gini": [0.45, 0.46, 0.47, 0.48, 0.49],
            "child-poverty": [10, 13, 16, 19, 22],
        },
        "people": {
            "default": [5, 15, 40, 80, 150, 400],
            "people-of-color": [18, 25, 35, 42, 55, 65],
            "seniors": [17, 18, 19, 20, 21],
            "education": [28, 32, 35, 38, 42, 45],
        },
        "housing": {
            "default": [175000, 225000, 275000, 350000, 450000, 600000],
            "rent-burden": [45, 48, 50, 52, 55, 58],
            "vacancy": [8, 9.5, 12, 13, 15],
            "pre-1940": [4, 8, 15, 19, 25],
            "ownership": [60, 64, 67, 70, 72, 74],
        },
        "connectivity": {
            "default": [5.5, 6, 7, 8, 10],
            "no-vehicle": [5.5, 6, 7, 8.5, 11],
            # No state reaches 25% transit (NY, 21.6%, is the maximum), so
            # this is the one level that cannot carry the shared scale.
            "transit-commute": [0.5, 1, 3, 8, 20],
            "work-from-home": [9.5, 13, 16, 17, 19],
        },
        "wellbeing": {
            "default": [5.5, 6.5, 8.5, 9.5, 11],
            "disability": [12, 13, 14, 15, 18],
            "foreign-born": [4.5, 6, 9.5, 15, 19],
            # The two state distributions barely overlap — Black-household
            # medians run 26k-84k, white non-Hispanic 44k-170k — and these
            # five breaks are the set that leaves no class empty on either
            # column while still being one shared scale.
            "income-pair": [45000, 62500, 70000, 75000, 80000],
        },
    },
    "zcta": {
        "income": {
            "default": [45000, 60000, 72000, 87000, 120000, 160000],
            "poverty": [5, 9, 13, 19, 28],
            "snap": [3, 7, 12, 17, 26],
            "unemployment": [1, 3, 4.5, 6.5, 10],
            "gini": [0.37, 0.40, 0.43, 0.47, 0.50],
            "child-poverty": [2, 8, 15, 27, 38],
        },
        "people": {
            "default": [5, 20, 60, 200, 600, 2000],
            "people-of-color": [2.5, 8, 17, 32, 62, 85],
            "seniors": [14, 18, 21, 26, 35],
            "education": [9, 17, 23, 32, 50, 65],
        },
        "housing": {
            "default": [100000, 160000, 225000, 325000, 500000, 800000],
            "rent-burden": [8.5, 34, 45, 55, 68, 88],
            "vacancy": [4.5, 8.5, 14, 23, 38],
            "pre-1940": [2, 7.5, 17, 29, 42],
            "ownership": [52, 70, 78, 85, 92, 99],
        },
        "connectivity": {
            "default": [3, 6, 9.5, 14, 22],
            "no-vehicle": [0.75, 3, 5, 8, 13],
            "work-from-home": [4, 8, 12, 17, 25],
        },
        "wellbeing": {
            "default": [2.5, 4.5, 7.5, 11, 18],
            "disability": [10, 13, 16, 20, 26],
            "foreign-born": [0.25, 1.5, 4, 9.5, 20],
            "income-pair": [50000, 65000, 80000, 100000, 130000],
        },
    },
    "place": {
        "income": {
            "default": [40000, 55000, 67000, 84000, 115000, 150000],
            "poverty": [5, 9, 14, 20, 30],
            "snap": [2.5, 7.5, 13, 21, 32],
            "unemployment": [0.5, 2.5, 4.5, 7.5, 12],
            "gini": [0.34, 0.39, 0.42, 0.46, 0.50],
            "child-poverty": [3, 10, 20, 32, 48],
        },
        "people": {
            "default": [50, 125, 250, 500, 1000, 2000],
            "people-of-color": [1.5, 8.5, 17, 34, 68, 92],
            "seniors": [13, 17, 21, 27, 38],
            "education": [5, 14, 21, 30, 50, 65],
        },
        "housing": {
            "default": [85000, 130000, 190000, 290000, 450000, 750000],
            "rent-burden": [1, 32, 45, 55, 72, 99],
            "vacancy": [3, 7.5, 13, 21, 36],
            "pre-1940": [1, 7, 18, 32, 50],
            "ownership": [50, 65, 75, 85, 97, 99],
        },
        "connectivity": {
            "default": [2, 5.5, 9.5, 15, 24],
            "no-vehicle": [0.5, 2.5, 5, 8.5, 14],
            "work-from-home": [1.5, 5.5, 10, 16, 25],
        },
        "wellbeing": {
            "default": [2, 4.5, 7.5, 12, 19],
            "disability": [9.5, 13, 17, 22, 29],
            "foreign-born": [0.25, 1, 3.5, 8.5, 19],
            "income-pair": [50000, 60000, 75000, 100000, 130000],
        },
    },
    "cd": {
        "income": {
            "default": [60000, 70000, 79000, 91000, 110000, 130000],
            "poverty": [8, 10, 12, 15, 19],
            "snap": [7.5, 10, 13, 15, 20],
            "unemployment": [4, 5, 5.5, 6, 7],
            "gini": [0.44, 0.45, 0.47, 0.48, 0.50],
            "child-poverty": [10, 14, 17, 21, 25],
        },
        "people": {
            "default": [25, 75, 200, 600, 1500, 4000],
            "people-of-color": [15, 29, 40, 52, 75, 85],
            "seniors": [14, 16, 18, 20, 21],
            "education": [23, 29, 34, 40, 50, 55],
        },
        "housing": {
            "default": [185000, 250000, 335000, 450000, 650000, 900000],
            "rent-burden": [45, 48, 50, 55, 58, 60],
            "vacancy": [5.5, 8, 10, 13, 17],
            "pre-1940": [3, 5.5, 11, 19, 29],
            "ownership": [50, 62, 68, 72, 75, 78],
        },
        "connectivity": {
            "default": [4, 5.5, 7, 8.5, 10],
            "no-vehicle": [4.5, 5.5, 6.5, 8.5, 13],
            "work-from-home": [10, 12, 15, 19, 23],
        },
        "wellbeing": {
            "default": [5, 6.5, 8.5, 11, 14],
            "disability": [11, 12, 14, 15, 17],
            "foreign-born": [5, 8, 14, 22, 32],
            "income-pair": [55000, 70000, 80000, 95000, 115000],
        },
    },
}

# (collection-id prefix, catalog group, the noun for one feature)
WIDE_THEME_LEVELS = [
    ("county", "counties", ("county", "counties")),
    ("state", "states", ("state", "states and state equivalents")),
    ("zcta", "zctas", ("ZCTA", "ZIP Code Tabulation Areas")),
    ("place", "places", ("place", "places")),
    ("cd", "congressional-districts", ("district", "districts")),
]
THEME_FNS = dict(BG_TRACT, wellbeing=wellbeing_styles)

for _prefix, _group, _unit in WIDE_THEME_LEVELS:
    for _theme, _fn in THEME_FNS.items():
        _cid = f"{_prefix}-{_theme}"
        _breaks = WIDE_THEME_BREAKS[_prefix][_theme]
        STYLES[_cid] = (_fn(_breaks, unit=_unit[0]) if _theme == "wellbeing"
                        else _fn(_breaks))
        SOURCES[_cid] = (f"{_group}/{_cid}", f"{_cid}.parquet")
        UNIT[_cid] = _unit

# Outlines appear as soon as they can be seen, which is a property of the
# geography, not of the collection: the coarse levels and their themed
# children carry a few hundred to a few thousand polygons, so z4.
COARSE_OUTLINES = {"states", "counties", "congressional-districts"} | {
    f"{p}-{t}" for p, _, _ in WIDE_THEME_LEVELS
    for t in THEME_FNS if p != "zcta" and p != "place"}


# -- blocks: 2020 Decennial counts, 8.17M features --------------------------
# Decennial counts are a complete enumeration, so there is no CV to fade.
# Roughly a third of blocks have no residents and a quarter no housing units,
# which is why every share style here carries the no-data underlay.
STYLES["blocks"] = [
    S("default", "Population density", "pop_density",
      [1, 10, 50, 200, 800, 2500], "magma7",
      "People per square kilometre of land area on roughly logarithmic "
      "steps, pale cream to deep plum; the lowest class is almost entirely "
      "the blocks with no residents at all", fmt="dens", default=True),
    S("white-share", "White, non-Hispanic share", "pct_white_nh",
      [10, 30, 50, 70, 85, 95], "blues7",
      "Share of residents who are white alone and not Hispanic or Latino, "
      "pale to deep blue"),
    S("black-share", "Black share", "pct_black",
      [1, 5, 15, 35, 65], "greens6",
      "Share of residents who are Black or African American alone, pale to "
      "deep green"),
    S("hispanic-share", "Hispanic or Latino share", "pct_hispanic",
      [2, 6, 15, 30, 60], "oranges6",
      "Share of residents who are Hispanic or Latino of any race, pale "
      "apricot to burnt orange"),
    S("vacancy", "Vacant housing units", "pct_vacant",
      [5, 15, 30, 50, 75], "orrd6",
      "Share of housing units vacant on Census Day 2020, cream to dark red; "
      "blocks with no housing units draw as no data, not as zero"),
]


# -- reference/ (2026-11-15): geography with no demographic columns --------
# No ACS or decennial statistic touches these four collections, so there is
# no income or density to class on. urban-areas has no urban/urbanized
# split to style on either: TIGER2024's UAC20 carries a single MTFCC
# (G3500, "Urban Area") and a single LSAD for every one of its 2,644
# features -- the 2010-era UATYP10 class this spec asked to style on does
# not exist in the 2020 urban area product, so the default style classes
# on land area instead, which the docstring's "class breaks measured from
# the data" rule already covers. landmarks-area and landmarks-point style
# on feature_type, the column this build decoded from MTFCC.
STYLES["urban-areas"] = [
    S("default", "Land area", "aland_sqkm",
      [10, 25, 75, 250, 750], "purples6",
      "Land area in square kilometres, pale to deep purple, roughly "
      "logarithmic so a small city's urban area and a metro area's both "
      "get their own class", fmt="km2", default=True, fade=False),
]

# Top feature_type categories, measured (see the report this build wrote):
# landmarks-area's are dominated by cemeteries and parks; landmarks-point's
# by cul-de-sacs and locality points, which are address-system landmarks,
# not places you would look for on a map. Every category below has a
# nonzero national count; `--measure` fails the run if that stops being
# true.
# landmarks-area classes on the types that COVER AREA, not the types
# that are most numerous. Cemeteries are 54.6% of features but 0.1% of
# land area, so a count-ranked legend paints a national map almost
# entirely in the "other" color. These six cover 97.9% of land area
# (measured 2026-11-15).
LANDMARK_AREA_TYPES = [
    "National Park Service Land", "National Forest or Other Federal Land",
    "Military Installation", "Island",
    "State Park, Forest, or Recreation Area", "Park",
]
LANDMARK_AREA_COLORS = ["#00441b", "#238b45", "#b30000", "#8c6bb1",
                        "#66c2a4", "#b8e186", NODATA]

LANDMARK_POINT_TYPES = [
    "Cul-de-sac", "Locality Point", "Cemetery", "Mountain Peak or Summit",
    "Airport or Airfield",
]
LANDMARK_POINT_COLORS = ["#969696", "#6baed6", "#54278f", "#a67c52",
                         "#e6550d", NODATA]

STYLES["landmarks-area"] = [
    M("default", "Landmark type", "feature_type",
      LANDMARK_AREA_TYPES, LANDMARK_AREA_COLORS[:-1],
      "The six landmark types that cover the most land nationally -- "
      "National Park Service land, national forest and other federal "
      "land, military installations, islands, state parks and forests, "
      "and local parks -- each its own color; every other type draws "
      "neutral gray. These six hold 97.9% of the collection's land area "
      "(measured), which is why they are ranked by area and not by "
      "count: cemeteries are 54.6% of the features and 0.1% of the land",
      other_color=LANDMARK_AREA_COLORS[-1], default=True),
    M("kind", "Landmark kind", "landmark_kind",
      ["landmark", "military"], ["#238b45", "#b30000"],
      "Civilian landmarks (AREALM) in green against military installations "
      "(MIL) in red -- the two source files this collection combines",
      other_color=NODATA),
]

STYLES["landmarks-point"] = [
    M("default", "Landmark type", "feature_type",
      LANDMARK_POINT_TYPES, LANDMARK_POINT_COLORS[:-1],
      "The five most common point-landmark types nationally -- most of "
      "them cul-de-sacs and locality points, address-system landmarks "
      "rather than places -- each its own color; every other type draws "
      "neutral gray",
      other_color=LANDMARK_POINT_COLORS[-1], default=True),
]


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------
QUANTILES = [0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95,
             0.98]


def parquet_glob(coll_id):
    d, pat = SOURCES[coll_id]
    return str(CATALOG / d / pat)


def measure(only=None):
    """Profile every styled column nationally; write docs/style-breaks.json.

    `only` measures some collections and merges them into whatever the file
    already holds, so adding a collection does not re-profile 8.2 million
    blocks to learn nothing new about them.
    """
    import duckdb

    out = {
        "measured": date.today().isoformat(),
        "method": (
            "DuckDB over each collection's GeoParquet (the whole national "
            "file, not a sample). quantile_cont on non-null values; class "
            "counts are exact counts of features falling in each step class "
            "of the published style. Regenerate with "
            "python3 tools/make_styles.py --measure."),
        "collections": {},
    }
    if only and BREAKS_JSON.exists():
        prev = json.loads(BREAKS_JSON.read_text())
        out["collections"] = prev["collections"]
        out["measured_previously"] = prev.get("measured")
    for coll_id, styles in STYLES.items():
        if only and coll_id not in only:
            continue
        src = parquet_glob(coll_id)
        schema = [r[0] for r in
                  duckdb.sql(f"describe select * from read_parquet('{src}')")
                  .fetchall()]
        cols, cat_cols = {}, {}
        for s in styles:
            if s.col not in schema:
                sys.exit(f"✗ {coll_id}: column {s.col!r} is not in the "
                         f"parquet schema")
            if isinstance(s, M):
                merged = cat_cols.setdefault(s.col, [])
                for c in s.categories:
                    if c not in merged:
                        merged.append(c)
            else:
                cols.setdefault(s.col, s.breaks)

        sel = ["count(*) as rows"]
        for col, cats in cat_cols.items():
            sel.append(f"count({col}) as n_{col}")
            for i, cat in enumerate(cats):
                lit = cat.replace("'", "''")
                sel.append(f"count_if({col} = '{lit}') as m{i}_{col}")
        for col, breaks in cols.items():
            sel += [f"count({col}) as n_{col}",
                    f"min({col}) as min_{col}",
                    f"max({col}) as max_{col}"]
            for q in QUANTILES:
                sel.append(f"quantile_cont({col}, {q}) as q{_qn(q)}_{col}")
            edges = [None] + list(breaks) + [None]
            for i in range(len(breaks) + 1):
                lo, hi = edges[i], edges[i + 1]
                conds = [f"{col} is not null"]
                if lo is not None:
                    conds.append(f"{col} >= {lo}")
                if hi is not None:
                    conds.append(f"{col} < {hi}")
                sel.append(f"count_if({' and '.join(conds)}) as c{i}_{col}")
            if f"{col}_cv" in schema:
                sel.append(f"count_if({col}_cv > {CV_LIMIT}) as cv_{col}")
        row = duckdb.sql(
            f"select {', '.join(sel)} from read_parquet('{src}')").fetchone()
        names = [d.strip().split(" as ")[-1] for d in sel]
        v = dict(zip(names, row))

        rec = {"source": str(Path(src).relative_to(ROOT)),
               "rows": int(v["rows"]), "schema": schema, "stats": {}}
        for col, breaks in cols.items():
            n = int(v[f"n_{col}"])
            counts = [int(v[f"c{i}_{col}"]) for i in range(len(breaks) + 1)]
            rec["stats"][col] = {
                "n_non_null": n,
                "null_pct": round(100 * (rec["rows"] - n) / rec["rows"], 2),
                "min": v[f"min_{col}"], "max": v[f"max_{col}"],
                "quantiles": {f"p{_qn(q)}": v[f"q{_qn(q)}_{col}"]
                              for q in QUANTILES},
                "breaks": list(breaks),
                "class_counts": counts,
                "class_pct": [round(100 * c / n, 2) if n else 0.0
                              for c in counts],
                "noisy_cv_pct": (
                    round(100 * int(v[f"cv_{col}"]) / n, 2)
                    if f"cv_{col}" in v and n else None),
            }
        for col, cats in cat_cols.items():
            n = int(v[f"n_{col}"])
            cat_counts = {cat: int(v[f"m{i}_{col}"])
                         for i, cat in enumerate(cats)}
            rec["stats"][col] = {
                "kind": "match",
                "n_non_null": n,
                "null_pct": round(100 * (rec["rows"] - n) / rec["rows"], 2),
                "categories": list(cats),
                "category_counts": cat_counts,
                "other_count": n - sum(cat_counts.values()),
            }
        out["collections"][coll_id] = rec
        print(f"✓ measured {coll_id}: {len(cols) + len(cat_cols)} columns over "
              f"{rec['rows']:,} rows")

    BREAKS_JSON.parent.mkdir(exist_ok=True)
    BREAKS_JSON.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(f"✓ wrote {BREAKS_JSON.relative_to(ROOT)}")


def _qn(q):
    return str(int(round(q * 100)))


# ---------------------------------------------------------------------------
# Style assembly
# ---------------------------------------------------------------------------
def step_expr(col, breaks, ramp):
    expr = ["step", ["get", col], RAMPS[ramp][0]]
    for i, b in enumerate(breaks):
        expr += [b, RAMPS[ramp][i + 1]]
    return expr


def fmt_value(x, fmt):
    if fmt == "usd":
        return f"${x / 1000:g}k" if x >= 1000 else f"${x:g}"
    if fmt in ("dens", "km2"):
        return f"{x:,g}"
    if fmt == "num":
        return f"{x:g}"
    return f"{x:g}%"


SUFFIX = {"dens": " people per km²", "km2": " km²"}


ORDINAL = {1: "st", 2: "nd", 3: "rd"}


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else ORDINAL.get(n % 10, 'th')}"


def break_basis(stat, s):
    """'breaks at A/B/C sit at the Nth/Mth ... national percentile'.

    The percentile of each break is read straight off the measured class
    counts, so the prose cannot drift from the numbers in
    docs/style-breaks.json.
    """
    cum, pcts = 0, []
    for c in stat["class_counts"][:-1]:
        cum += c
        pcts.append(round(100 * cum / stat["n_non_null"]))
    vals = ("/".join(fmt_value(b, s.fmt) for b in s.breaks)
            + SUFFIX.get(s.fmt, ""))
    return (f"{len(s.breaks) + 1} classes with breaks at {vals}, which fall "
            f"at the {'/'.join(ordinal(p) for p in pcts)} percentile of the "
            f"national distribution")


def fades(s, stat):
    noisy = stat.get("noisy_cv_pct")
    return bool(s.fade and noisy and noisy <= NOISY_FADE_MAX)


def description_match(coll_id, s, stat):
    """Prose for an M (categorical) style: counts, not percentile breaks."""
    unit, units = UNIT[coll_id]
    parts = [f"{cat} ({stat['category_counts'][cat]:,})"
             for cat in s.categories]
    bits = [f"{s.blurb}. Measured over all {stat['n_non_null']:,} {units} "
            f"with a value: {', '.join(parts)}, and "
            f"{stat['other_count']:,} other types in neutral gray."]
    if stat["null_pct"] >= 5:
        bits.append(f"{stat['null_pct']:g}% have no {s.col} value and draw "
                    f"in neutral gray too.")
    return " ".join(bits)


def description(coll_id, s, stat):
    if isinstance(s, M):
        return description_match(coll_id, s, stat)
    unit, units = UNIT[coll_id]
    bits = [f"{s.blurb}. Measured over all "
            f"{stat['n_non_null']:,} {units} with a published value: "
            f"{break_basis(stat, s)}."]
    if s.note:
        bits.append(s.note + ".")
    if stat["null_pct"] >= 5:
        bits.append(f"{stat['null_pct']:g}% have no published value and draw "
                    f"in neutral gray rather than as a low value.")
    noisy = stat.get("noisy_cv_pct")
    if fades(s, stat):
        bits.append(f"{noisy:g}% have a coefficient of variation above "
                    f"{CV_LIMIT:g} and render faded — the estimate is real "
                    f"but its margin of error swamps it.")
    elif noisy and noisy > NOISY_FADE_MAX:
        bits.append(f"{noisy:g}% of {units} have a coefficient of variation "
                    f"above {CV_LIMIT:g} at this geography, too many to fade "
                    f"without washing the map out, so read {s.col}_moe in the "
                    f"GeoParquet before drawing a conclusion from any single "
                    f"{unit}.")
    elif noisy:
        bits.append(f"{noisy:g}% of {units} have a coefficient of variation "
                    f"above {CV_LIMIT:g}; this style does not fade them, so "
                    f"read {s.col}_moe in the GeoParquet before drawing a "
                    f"conclusion from any single {unit}.")
    return " ".join(bits)


def match_expr(col, categories, colors, other_color):
    expr = ["match", ["get", col]]
    for cat, color in zip(categories, colors):
        expr += [cat, color]
    expr.append(other_color)
    return expr


def build_style(coll_id, s, stat):
    point = coll_id in POINT_COLLECTIONS
    paint_prop = "circle-color" if point else "fill-color"
    opacity_prop = "circle-opacity" if point else "fill-opacity"
    layer_type = "circle" if point else "fill"
    layers = []
    if isinstance(s, M):
        # The `other_color` branch of the match expression already covers
        # a missing value (a null `get` matches no literal case), so there
        # is no separate no-data layer -- one `match` layer carries both.
        expr = match_expr(s.col, s.categories, s.colors, s.other_color)
        paint = {paint_prop: expr, opacity_prop: OPACITY}
        if point:
            paint["circle-radius"] = ["interpolate", ["linear"], ["zoom"],
                                      4, 1.5, 14, 5]
            paint["circle-stroke-width"] = 0
        layers.append({"id": layer_type, "type": layer_type, "source": "data",
                       "source-layer": coll_id, "paint": paint})
        return {
            "version": 8,
            "name": s.name,
            "metadata": {"description": description(coll_id, s, stat),
                        "portolan:column": s.col,
                        "portolan:categories": list(s.categories)},
            "sources": {"data": {"type": "vector",
                                 "url": f"pmtiles://../{coll_id}.pmtiles"}},
            "layers": layers,
        }

    if stat["null_pct"] >= 5:
        # Constant colour, so portolan-browser's legend walk steps over it and
        # finds the step expression on the layer above.
        layers.append({
            "id": "no-data", "type": layer_type, "source": "data",
            "source-layer": coll_id,
            "filter": ["!", ["has", s.col]],
            "paint": {paint_prop: NODATA, opacity_prop: 0.55},
        })
    expr = step_expr(s.col, s.breaks, s.ramp)
    opacity = OPACITY
    if fades(s, stat):
        opacity = ["case",
                   [">", ["coalesce", ["get", f"{s.col}_cv"], 0], CV_LIMIT],
                   OPACITY_NOISY, OPACITY]
    fill_paint = {paint_prop: expr, opacity_prop: opacity}
    if point:
        fill_paint["circle-radius"] = ["interpolate", ["linear"], ["zoom"],
                                       4, 1.5, 14, 5]
        fill_paint["circle-stroke-width"] = 0
    layers.append({
        "id": layer_type, "type": layer_type, "source": "data",
        "source-layer": coll_id,
        # Tiles omit null attributes; an unfiltered step would get a
        # non-numeric input and fall back to the paint default (black).
        "filter": ["has", s.col],
        "paint": fill_paint,
    })
    if not point:
        # Boundaries only once they can be seen: at national zoom 242k
        # block-group outlines are noise, and 8.2M block outlines a gray
        # sheet. Points have no outline layer at all.
        zmin = 11 if coll_id == "blocks" else (
            4 if coll_id in COARSE_OUTLINES else 8)
        layers.append({
            "id": "outline", "type": "line", "source": "data",
            "source-layer": coll_id, "minzoom": zmin,
            "paint": {
                "line-color": OUTLINE,
                "line-width": ["interpolate", ["linear"], ["zoom"],
                               zmin, 0.2, zmin + 5, 0.8],
                "line-opacity": ["interpolate", ["linear"], ["zoom"],
                                 zmin, 0.0, zmin + 2, 0.45],
            },
        })
    return {
        "version": 8,
        "name": s.name,
        "metadata": {"description": description(coll_id, s, stat),
                     "portolan:column": s.col,
                     "portolan:breaks": list(s.breaks)},
        "sources": {"data": {"type": "vector",
                             "url": f"pmtiles://../{coll_id}.pmtiles"}},
        "layers": layers,
    }


def validate(coll_id, s, stat):
    if isinstance(s, M):
        empty = [cat for cat in s.categories
                if stat["category_counts"].get(cat, 0) == 0]
        if empty:
            sys.exit(f"✗ {coll_id}/{s.file}: match branches {empty} are "
                     f"empty nationally — no empty legend swatches")
        return
    if list(s.breaks) != sorted(set(s.breaks)):
        sys.exit(f"✗ {coll_id}/{s.file}: breaks are not strictly increasing: "
                 f"{s.breaks}")
    if stat["breaks"] != list(s.breaks):
        sys.exit(f"✗ {coll_id}/{s.file}: docs/style-breaks.json was measured "
                 f"against {stat['breaks']}, style now uses {s.breaks} — "
                 f"rerun with --measure")
    empty = [i for i, c in enumerate(stat["class_counts"]) if c == 0]
    if empty:
        sys.exit(f"✗ {coll_id}/{s.file}: classes {empty} are empty "
                 f"nationally ({stat['class_counts']}) — no empty legend "
                 f"swatches")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measure", action="store_true",
                    help="re-profile the parquet and rewrite "
                         "docs/style-breaks.json")
    ap.add_argument("collections", nargs="*",
                    help="collection ids to measure and write styles for "
                         "(default: all of them)")
    args = ap.parse_args()
    only = set(args.collections) or None
    if only and (unknown := only - set(STYLES)):
        sys.exit(f"✗ unknown collections: {sorted(unknown)}")
    if args.measure or not BREAKS_JSON.exists():
        measure(only)

    m = json.loads(BREAKS_JSON.read_text())["collections"]
    total = 0
    for coll_id, styles in STYLES.items():
        if only and coll_id not in only:
            continue
        if coll_id not in m:
            sys.exit(f"✗ {coll_id}: not in docs/style-breaks.json — rerun "
                     f"with --measure")
        rec = m[coll_id]
        # SOURCES names the directory holding the DATA. A wide
        # all-indicators table's collection.json (and styles/) moved into
        # catalog/<group>/<group>/ in the 2026-11-15 restructure while its
        # parquet and pmtiles stayed put, so its styles go one level down.
        src_dir = SOURCES[coll_id][0]
        if coll_id in specs.WIDE_IDS:
            src_dir = f"{src_dir}/{coll_id}"
        d = CATALOG / src_dir / "styles"
        if not d.parent.exists():
            sys.exit(f"✗ no collection dir: {d.parent}")
        d.mkdir(exist_ok=True)
        defaults = [s.file for s in styles if s.default]
        assert defaults == ["default"], (
            f"{coll_id}: exactly one style must be the default and it must be "
            f"named default.json (finalize_stac keys the default role off the "
            f"filename); got {defaults}")
        thin = []
        for s in styles:
            if s.col not in rec["schema"]:
                sys.exit(f"✗ {coll_id}/{s.file}: column {s.col!r} is not in "
                         f"the parquet schema")
            if f"{s.col}_cv" in rec["schema"] and \
                    rec["stats"][s.col].get("noisy_cv_pct") is None:
                sys.exit(f"✗ {coll_id}/{s.file}: {s.col}_cv exists but was "
                         f"not measured — rerun with --measure")
            stat = rec["stats"][s.col]
            validate(coll_id, s, stat)
            obj = build_style(coll_id, s, stat)
            json.loads(json.dumps(obj))  # round-trips as JSON
            (d / f"{s.file}.json").write_text(json.dumps(obj, indent=2) + "\n")
            total += 1
            if "class_pct" in stat:
                worst = max(stat["class_pct"])
                if worst >= 50:
                    thin.append(
                        f"{s.file} ({s.col}: {worst:g}% in one class)")
        print(f"✓ {coll_id}: {len(styles)} styles → "
              f"{d.relative_to(CATALOG)} (default: {styles[0].name})")
        for t in thin:
            print(f"  ! {coll_id}/{t} — concentrated, by design; see "
                  f"docs/style-breaks.json")
    print(f"{total} styles written")


if __name__ == "__main__":
    main()
