#!/usr/bin/env python3
"""Build catalog/trends/: a dozen headline ACS indicators, long form, one
row per (geoid, period), across the 2015-2019 and 2020-2024 5-year
vintages. See docs/spec-trends.md.

State and county need no spatial crosswalk -- both geographies are stable
between the two vintages at every geoid except Connecticut's county
equivalents (8 counties -> 9 planning regions, effective 2022) and one
Alaska county equivalent (Valdez-Cordova Census Area split into Chugach
and Copper River). Tract needs the real one: 2010-vintage tracts (the
geography the 2015-2019 ACS tabulates) do not nest inside 2020-vintage
tracts (the geography the 2020-2024 ACS tabulates and this catalog
otherwise publishes), so the two periods are reconciled through
`catalog/reference/crosswalks/t10t20-tract.parquet`, weighted by the 2020
block population each 2010/2020 block pair's land-area overlap carries
(`catalog/blocks`) -- the only population series available at block
granularity for either vintage's geometry, used as a defensible proxy for
"how much of this tract's population is really the same population as
before."

Every row carries `geo_change`, measured per geoid rather than assumed,
with one of five values:

  identical   -- bidirectionally 1:1 (>=99% of the population each way).
                 All 12 indicators carry over from the single predecessor.
  absorbed    -- several clean predecessors (each sending >=99% of ITS
                 OWN population here) combine into this one. Counts SUM
                 across the predecessors' raw census cells (a legitimate
                 aggregation -- quadrature MOE applies) and rates
                 recompute from the summed numerator and denominator.
                 Medians are NULL: a median cannot be derived from
                 medians, so there is no legitimate 2015-2019 median for
                 a geography the Census Bureau never tabulated directly.
  subdivided  -- this geoid gets >=99% of its population from a single
                 predecessor, but that predecessor itself sends
                 population elsewhere too (it is not a clean 1:1 match).
                 Rates and medians carry over from that one predecessor
                 under an explicit part-resembles-whole assumption --
                 flagged, not hidden. Counts are NULL: carrying a whole
                 predecessor's population onto a fragment of it would
                 overstate the fragment.
  mixed       -- genuinely mixed sources, no dominant predecessor and no
                 clean set of feeders. Everything NULL.
  no_acs_data -- cartographic boundary exists, no ACS 5-year tabulation in
                 EITHER period (American Samoa, Guam, the Northern
                 Mariana Islands, the U.S. Virgin Islands). Not a
                 geography change; a program gap in both periods.

Never apportioned, never carried over as a measurement that looks more
certain than it is -- see docs/spec-trends.md.

Usage:
  python3 tools/build_trends.py state county tract
  python3 tools/build_trends.py --validate
"""
import argparse
import csv
import subprocess
import sys
from collections import defaultdict
from math import sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from specs import ACS_RELEASE, CACHE, JAM, LEVELS, STATE_USPS, TRENDS_RELEASE

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
BUILD = ROOT / "staging" / "acs-build"
GEO = ROOT / "staging" / "geo"
REL2020 = CATALOG / "reference" / "crosswalks" / "t10t20-tract.parquet"
BLOCKS_GLOB = str(CATALOG / "blocks" / "state_fips=*" / "*.parquet")

ALL_LEVELS = ["state", "county", "tract"]

# (period label, release, year-string for the acsdt5y{year}-<table>.dat
# filename convention).
PERIODS = [
    ("2015-2019", TRENDS_RELEASE, "2019"),
    ("2020-2024", ACS_RELEASE, "2024"),
]
OLD, NEW = "2015-2019", "2020-2024"

# table -> lines this builder reads from it. pct_people_of_color's table
# (B03002) carries no `lines` of its own (it is a `complement` Spec), so
# its lines are listed explicitly here rather than resolved from the Spec.
TABLE_LINES = {
    "B01003": [1], "B19013": [1], "B19301": [1], "C17002": [1, 2, 3],
    "B23025": [3, 5], "B01002": [1], "B15003": [1, 22, 23, 24, 25],
    "B03002": [1, 3], "B25003": [1, 2], "B25077": [1], "B25064": [1],
}

# (name, kind, table, numerator lines, denominator lines)
INDICATORS = [
    ("population", "count", "B01003", [1], None),
    ("median_hh_income", "median", "B19013", [1], None),
    ("per_capita_income", "median", "B19301", [1], None),
    ("pct_below_poverty", "pct", "C17002", [2, 3], [1]),
    ("pct_unemployed", "pct", "B23025", [5], [3]),
    ("median_age", "median", "B01002", [1], None),
    ("pct_bachelors_plus", "pct", "B15003", [22, 23, 24, 25], [1]),
    ("pct_people_of_color", "complement", "B03002", [3], [1]),
    ("households", "count", "B25003", [1], None),
    ("pct_owner_occupied", "pct", "B25003", [2], [1]),
    ("median_home_value", "median", "B25077", [1], None),
    ("median_gross_rent", "median", "B25064", [1], None),
]
COUNT_NAMES = {n for n, k, *_ in INDICATORS if k == "count"}
RATE_NAMES = {n for n, k, *_ in INDICATORS if k in ("pct", "complement")}
MEDIAN_NAMES = {n for n, k, *_ in INDICATORS if k == "median"}

GEO_PARQUET = {
    "county": GEO / "cb_2024_us_county_4326.parquet",
    "state": GEO / "cb_2024_us_state_4326.parquet",
    "tract": GEO / "cb_2024_us_tract_4326.parquet",
}

TH = 0.99   # "clean"/dominant population-share threshold
SIG = 0.01  # materiality floor for "a significant contributor"


def run(cmd, **kw):
    proc = subprocess.run([str(c) for c in cmd], capture_output=True,
                          text=True, **kw)
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(str(c) for c in cmd)}\n"
                           f"{proc.stdout[-500:]}\n{proc.stderr[-2000:]}")
    return proc


def connect():
    import duckdb
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    return con


# --------------------------------------------------------------------------
# ACS extraction (shared math with build_acs.py: quadrature sums, the
# Census proportion/ratio MOE formula)
# --------------------------------------------------------------------------

def moe_sum(moes):
    known = [m for m in moes if m is not None]
    if not known:
        return None
    return sqrt(sum(m * m for m in known))


def pct_moe(num, num_moe, den, den_moe):
    if num_moe is None or den_moe is None or den == 0:
        return None
    p = num / den
    radicand = num_moe ** 2 - p * p * den_moe ** 2
    if radicand < 0:
        radicand = num_moe ** 2 + p * p * den_moe ** 2
    return 100 * sqrt(radicand) / den


def dat_path(table: str, year: str) -> Path:
    return CACHE / f"acsdt5y{year}-{table.lower()}.dat"


def cellval(raw: str):
    if not raw or raw == ".":
        return None
    v = float(raw)
    return None if v <= JAM else v


def load_table(table: str, year: str, levels: dict) -> dict:
    """-> {level: {geoid_suffix: {line: (E, M)}}}."""
    path = dat_path(table, year)
    if not path.exists():
        raise RuntimeError(f"missing source: {path}")
    needed = TABLE_LINES[table]
    out = {lvl: {} for lvl in levels}
    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("|")
        idx = {}
        for i, name in enumerate(header):
            if name == "GEO_ID":
                continue
            idx[name.split("_", 1)[1]] = i
        prefixes = {p: lvl for lvl, p in levels.items()}
        for line in f:
            lvl = prefixes.get(line[:9])
            if lvl is None:
                continue
            row = line.rstrip("\n").split("|")
            geoid = row[0].split("US", 1)[1]
            vals = {}
            for ln in needed:
                vals[ln] = (cellval(row[idx[f"E{ln:03d}"]]),
                           cellval(row[idx[f"M{ln:03d}"]]))
            out[lvl][geoid] = vals
    return out


def compute_indicator(kind, lines, den_lines, table_data: dict):
    """table_data: {line: (E, M)} for one geoid in one table."""
    def get(ln):
        return table_data.get(ln, (None, None))

    if kind == "median":
        return get(lines[0])

    if kind == "count":
        es = [get(l)[0] for l in lines]
        if all(e is None for e in es):
            return (None, None)
        est = sum(e for e in es if e is not None)
        return (int(est), moe_sum([get(l)[1] for l in lines]))

    es = [get(l)[0] for l in lines]
    if any(e is None for e in es):
        return (None, None)
    num = sum(es)
    nmoe = moe_sum([get(l)[1] for l in lines])
    dvals = [get(l)[0] for l in den_lines]
    if any(v is None for v in dvals):
        return (None, None)
    den = sum(dvals)
    if den <= 0:
        return (None, None)
    dmoe = moe_sum([get(l)[1] for l in den_lines])
    m = pct_moe(num, nmoe, den, dmoe)
    pct = max(0.0, min(100.0, 100 * num / den))  # clamp float noise, no -0.0
    m = None if m is None else round(m, 2)
    if kind == "complement":
        return (round(100 - pct, 2), m)
    return (round(pct, 2), m)


def compute_all(table_data: dict) -> dict:
    """{indicator_name: (est, moe)} from a geoid's {table: {line: (E,M)}}."""
    out = {}
    for name, kind, table, lines, den_lines in INDICATORS:
        td = (table_data or {}).get(table, {})
        out[name] = compute_indicator(kind, lines, den_lines, td)
    return out


def merge_table_data(parts: list[dict]) -> dict:
    """Sum raw E cells (quadrature M) for one table across several whole
    predecessor geoids -- the legitimate "absorbed" aggregation. A missing
    contributor for one line drops out rather than nulling the sum, the
    same convention moe_sum and the count-kind indicator already use."""
    merged: dict = {}
    for table in TABLE_LINES:
        lines = TABLE_LINES[table]
        merged[table] = {}
        for ln in lines:
            es = [p.get(table, {}).get(ln, (None, None))[0] for p in parts]
            ms = [p.get(table, {}).get(ln, (None, None))[1] for p in parts]
            e = None if all(v is None for v in es) \
                else sum(v for v in es if v is not None)
            merged[table][ln] = (e, moe_sum(ms))
    return merged


def extract_period(year: str, levels: dict) -> dict:
    """-> {level: {geoid: {table: {line: (E,M)}}}}"""
    tables_needed = sorted(TABLE_LINES)
    by_table = {t: load_table(t, year, levels) for t in tables_needed}
    out = {lvl: {} for lvl in levels}
    for lvl in levels:
        geoids = set()
        for t in tables_needed:
            geoids |= set(by_table[t][lvl])
        for g in geoids:
            out[lvl][g] = {t: by_table[t][lvl].get(g, {}) for t in tables_needed}
    return out


# --------------------------------------------------------------------------
# geo_change classification: population-weighted, measured per geoid
# --------------------------------------------------------------------------

def classify_pairs(pairs) -> dict:
    """pairs: iterable of (src, dst, weight) -> {dst: (category, info)}.

    info is the single dominant 2010-vintage src for 'identical'/
    'subdivided', the list of clean-feeder srcs for 'absorbed', or None
    for 'mixed'.
    """
    by_dst, by_src = defaultdict(dict), defaultdict(dict)
    for src, dst, w in pairs:
        if w is None or w <= 0:
            continue
        by_dst[dst][src] = by_dst[dst].get(src, 0.0) + w
        by_src[src][dst] = by_src[src].get(dst, 0.0) + w

    def shares(d):
        tot = sum(d.values())
        return ({k: v / tot for k, v in d.items()}, tot) if tot else ({}, 0)

    out = {}
    for dst, srcmap in by_dst.items():
        sh, _ = shares(srcmap)
        dom_src, dom_share = max(sh.items(), key=lambda kv: kv[1])
        if dom_share >= TH:
            src_sh, _ = shares(by_src[dom_src])
            src_dom_dst, src_dom_share = max(src_sh.items(), key=lambda kv: kv[1])
            if src_dom_share >= TH and src_dom_dst == dst:
                out[dst] = ("identical", dom_src)
            else:
                out[dst] = ("subdivided", dom_src)
        else:
            sig = [s for s, v in sh.items() if v >= SIG]
            contributors, clean_all = [], True
            for s in sig:
                s_sh, _ = shares(by_src[s])
                if s_sh.get(dst, 0) >= TH:
                    contributors.append(s)
                else:
                    clean_all = False
            if clean_all and contributors:
                out[dst] = ("absorbed", contributors)
            else:
                out[dst] = ("mixed", None)
    return out


def tract_population_weights(con) -> list:
    """(2010-tract, 2020-tract, weight) nationally, apportioning each 2020
    BLOCK's actual 2020 population across its 2010-block predecessors by
    land-area share (both sides of t10t20-tract.parquet carry Connecticut's
    OLD 8-county coding -- see ct_tract_relabel -- so this step needs no
    Connecticut special case of its own)."""
    sql = f"""
      WITH rel AS (
        SELECT state_2010||county_2010||tract_2010 AS t10,
               state_2020||county_2020||tract_2020 AS t20,
               state_2020||county_2020||tract_2020||blk_2020 AS geoid_2020,
               arealand_int
        FROM read_parquet('{REL2020}')
        WHERE state_2010 IS NOT NULL AND state_2020 IS NOT NULL
      ),
      blk_totals AS (
        SELECT geoid_2020, sum(arealand_int) AS total_int
        FROM rel GROUP BY geoid_2020
      ),
      blocks AS (SELECT geoid, pop_total FROM read_parquet('{BLOCKS_GLOB}')),
      weighted AS (
        SELECT r.t10, r.t20,
               b.pop_total * (r.arealand_int::DOUBLE /
                             NULLIF(bt.total_int, 0)) AS w
        FROM rel r
        JOIN blk_totals bt ON bt.geoid_2020 = r.geoid_2020
        JOIN blocks b ON b.geoid = r.geoid_2020
      )
      SELECT t10, t20, sum(w) FROM weighted GROUP BY t10, t20 HAVING sum(w) > 0
    """
    return con.execute(sql).fetchall()


def ct_tract_relabel(con) -> dict:
    """old-CT-coded 2020 tract geoid -> the 2024 cartographic boundary
    file's tract geoid for the SAME tract number. Deterministic, not
    population-weighted: Connecticut's 2022 switch from 8 counties to 9
    planning regions renumbered the county prefix and left the 6-digit
    tract number untouched (docs/runbook.md, "Connecticut")."""
    sql = f"""
      SELECT '09' || b.old_county_part || tr.tractno AS old_geoid,
             '09' || tr.new_county || tr.tractno AS new_geoid
      FROM (SELECT DISTINCT state_2020||county_2020 AS old_prefix,
                   county_2020 AS old_county_part, tract_2020 AS tractno
            FROM read_parquet('{REL2020}') WHERE state_2020 = '09') b
      JOIN (SELECT substr(GEOID,3,3) AS new_county, substr(GEOID,6,6) AS tractno
            FROM read_parquet('{GEO_PARQUET["tract"]}')
            WHERE substr(GEOID,1,2)='09') tr
        ON tr.tractno = b.tractno
    """
    return {old: new for old, new in con.execute(sql).fetchall()}


def ct_county_pairs(con) -> list:
    """Exact (old county, new planning region, 2020 population) at county
    level -- not population-weighted estimation, a deterministic join on
    the preserved 6-digit tract number, since whole tracts move together
    at this level of aggregation."""
    sql = f"""
      WITH blk AS (
        SELECT substr(geoid,1,5) AS old_county, substr(geoid,6,6) AS tractno,
               pop_total
        FROM read_parquet('{CATALOG / "blocks" / "state_fips=09" / "09.parquet"}')
      ),
      tr2024 AS (
        SELECT substr(GEOID,1,5) AS new_county, substr(GEOID,6,6) AS tractno
        FROM read_parquet('{GEO_PARQUET["tract"]}') WHERE substr(GEOID,1,2)='09'
      )
      SELECT b.old_county, t.new_county, sum(b.pop_total)
      FROM blk b JOIN tr2024 t ON t.tractno = b.tractno GROUP BY 1, 2
    """
    return con.execute(sql).fetchall()


def ak_county_pairs(con) -> list:
    """Population-weighted (old county, new county) for the one Alaska
    split this batch measured: 02261 Valdez-Cordova -> 02063 Chugach +
    02066 Copper River. Restricted to those exact geoids so an unrelated
    neighboring county's land-area noise (confirmed negligible, <0.001
    person-equivalents) cannot leak into the classification."""
    sql = f"""
      WITH rel AS (
        SELECT state_2010||county_2010||tract_2010 AS t10,
               state_2020||county_2020||tract_2020 AS t20,
               state_2020||county_2020||tract_2020||blk_2020 AS geoid_2020,
               arealand_int
        FROM read_parquet('{REL2020}')
        WHERE state_2010 = '02' AND county_2010 = '261'
          AND state_2020 = '02' AND county_2020 IN ('063', '066')
      ),
      blk_totals AS (
        SELECT geoid_2020, sum(arealand_int) AS total_int FROM rel GROUP BY 1
      ),
      blocks AS (SELECT geoid, pop_total FROM read_parquet(
          '{CATALOG / "blocks" / "state_fips=02" / "02.parquet"}')),
      weighted AS (
        SELECT substr(r.t10,1,5) AS c10, substr(r.t20,1,5) AS c20,
               b.pop_total * (r.arealand_int::DOUBLE /
                             NULLIF(bt.total_int,0)) AS w
        FROM rel r JOIN blk_totals bt ON bt.geoid_2020 = r.geoid_2020
        JOIN blocks b ON b.geoid = r.geoid_2020
      )
      SELECT c10, c20, sum(w) FROM weighted GROUP BY 1, 2
    """
    return con.execute(sql).fetchall()


def geo_change_map(level: str, con, period_data: dict) -> dict:
    """{geoid: (category, info)} for every geoid the 2024 boundary file
    carries at this level. `info` means what classify_pairs says it does.
    """
    old_geoids = set(period_data[OLD].keys())
    new_geoids = set(period_data[NEW].keys())
    out = {}
    if level == "state":
        for g in new_geoids:
            out[g] = ("identical", g) if g in old_geoids else ("no_acs_data", None)
        return out

    if level == "county":
        for g in new_geoids:
            out[g] = ("identical", g) if g in old_geoids else ("no_acs_data", None)
        ct_class = classify_pairs(ct_county_pairs(con))
        for g, (cat, info) in ct_class.items():
            if g in new_geoids:
                out[g] = (cat, info)
        ak_class = classify_pairs(ak_county_pairs(con))
        for g, (cat, info) in ak_class.items():
            if g in new_geoids:
                out[g] = (cat, info)
        return out

    # tract
    relabel = ct_tract_relabel(con)
    pairs = tract_population_weights(con)
    tract_class = classify_pairs(pairs)
    for dst, (cat, info) in tract_class.items():
        pub_dst = relabel.get(dst, dst)
        if pub_dst in new_geoids:
            out[pub_dst] = (cat, info)
    for g in new_geoids:
        if out.get(g) is None:
            # 2024 boundary tract with no measured 2010 lineage at all
            # (new/water-only tract, or a 2020-side sliver with zero
            # population weight): no legitimate single predecessor, so
            # treated like any other unclassifiable case.
            out[g] = ("mixed", None) if g in old_geoids else \
                ("no_acs_data", None)
    return out


# --------------------------------------------------------------------------
# row assembly
# --------------------------------------------------------------------------

def row_for(geoid, period, cat, est_by_name):
    row = {"geoid": geoid, "period": period, "geo_change": cat}
    for name, *_ in INDICATORS:
        est, moe = est_by_name.get(name, (None, None))
        row[name] = est
        row[f"{name}_moe"] = moe
    return row


def boundary_geoids(level: str, con) -> set:
    """Every geoid the 2024 cartographic boundary file carries at this
    level, including the ones with no ACS tabulation in either period
    (the island areas) -- the join is driven by geometry, same rule
    build_acs.py's assemble() applies, so a geoid with a polygon never
    silently disappears for lack of data."""
    gp = GEO_PARQUET[level]
    rows = con.execute(f"SELECT DISTINCT GEOID FROM read_parquet('{gp}')") \
              .fetchall()
    return {r[0] for r in rows}


def build_rows(level: str, con) -> list[dict]:
    levels = {level: LEVELS[level]}
    period_data = {}
    for label, release, year in PERIODS:
        print(f"  extracting {level} / {label} (release {release}) ...")
        period_data[label] = extract_period(year, levels)[level]

    gmap = geo_change_map(level, con, period_data)
    # Geometry-driven rows with no ACS tabulation in EITHER period (the
    # island areas at county/state; a handful of water-only tracts) --
    # not covered above because `geo_change_map` only classifies geoids
    # that appear in at least one period's own raw extraction.
    for g in boundary_geoids(level, con):
        if g not in gmap:
            gmap[g] = ("no_acs_data", None)
    rows = []
    for geoid, (cat, info) in sorted(gmap.items()):
        new_vals = compute_all(period_data[NEW].get(geoid))
        rows.append(row_for(geoid, NEW, cat, new_vals))

        if cat == "identical":
            old_vals = compute_all(period_data[OLD].get(info))
        elif cat == "subdivided":
            old_vals = compute_all(period_data[OLD].get(info))
            for n in COUNT_NAMES:
                old_vals[n] = (None, None)
        elif cat == "absorbed":
            parts = [period_data[OLD].get(s, {}) for s in info]
            merged = merge_table_data(parts)
            old_vals = compute_all(merged)
            for n in MEDIAN_NAMES:
                old_vals[n] = (None, None)
        else:  # mixed, no_acs_data
            old_vals = {n: (None, None) for n, *_ in INDICATORS}
        rows.append(row_for(geoid, OLD, cat, old_vals))
    add_change_columns(rows)
    return rows


def add_change_columns(rows: list[dict]) -> None:
    """`chg_<indicator>` = the 2020-2024 value minus the 2015-2019 value,
    carried on the 2020-2024 row only -- change is a property of the
    endpoint, not of either period on its own, and styling "map CHANGE,
    not level" needs one feature per geoid with the delta already on it
    rather than a cross-row computation a map style cannot do. NULL
    whenever either side is NULL, which already encodes every geo_change
    case correctly: 'mixed' and 'no_acs_data' are NULL on both sides so
    the change is NULL too; 'subdivided' leaves counts NULL so chg_
    population/chg_households are NULL there but chg_<rate/median> are
    not; 'absorbed' is the mirror image. The change's own margin of
    error is the quadrature sum of the two periods' margins -- the same
    formula this build already uses for every other sum of independent
    estimates (ACS Accuracy of the Data)."""
    by_geoid: dict[str, dict] = {}
    for r in rows:
        by_geoid.setdefault(r["geoid"], {})[r["period"]] = r
    for geoid, by_period in by_geoid.items():
        new_row, old_row = by_period.get(NEW), by_period.get(OLD)
        for name, *_ in INDICATORS:
            chg, chg_moe = None, None
            if new_row and old_row:
                nv, ov = new_row.get(name), old_row.get(name)
                if nv is not None and ov is not None:
                    chg = round(nv - ov, 2)
                    nm, om = new_row.get(f"{name}_moe"), old_row.get(f"{name}_moe")
                    chg_moe = moe_sum([nm, om])
                    if chg_moe is not None:
                        chg_moe = round(chg_moe, 2)
            if new_row is not None:
                new_row[f"chg_{name}"] = chg
                new_row[f"chg_{name}_moe"] = chg_moe
            if old_row is not None:
                old_row[f"chg_{name}"] = None
                old_row[f"chg_{name}_moe"] = None


# --------------------------------------------------------------------------
# assembly: DuckDB join to geometry, gpio GeoParquet normalization
# --------------------------------------------------------------------------

def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["geoid", "period", "geo_change"]
    for name, *_ in INDICATORS:
        fields += [name, f"{name}_moe", f"chg_{name}", f"chg_{name}_moe"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k))
                       for k in fields})


def col_types() -> dict:
    types = {"geoid": "VARCHAR", "period": "VARCHAR", "geo_change": "VARCHAR"}
    for name, kind, *_ in INDICATORS:
        t = "BIGINT" if kind == "count" else "DOUBLE"
        types[name] = t
        types[f"{name}_moe"] = "DOUBLE"
        # chg_<count> is a difference of two counts, published as DOUBLE
        # even where the level is BIGINT: it is a change, not a count.
        types[f"chg_{name}"] = "DOUBLE"
        types[f"chg_{name}_moe"] = "DOUBLE"
    return types


def restore_stats(path: Path) -> None:
    import pyarrow.parquet as pq
    t = pq.read_table(path)
    pq.write_table(t, path, compression="zstd", row_group_size=20000,
                   write_statistics=True)


def name_expr(level: str) -> str:
    return {
        "county": "concat_ws(', ', g.NAMELSAD, g.STATE_NAME)",
        "state": "g.NAME",
        "tract": "concat_ws(', ', g.NAMELSAD, g.NAMELSADCO, g.STATE_NAME)",
    }[level]


def assemble(level: str, con) -> dict:
    cid = f"{level}-trends"
    out_dir = CATALOG / "trends" / cid
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{cid}.parquet"
    tmp = BUILD / f"{cid}.duckdb.parquet"
    csv_path = BUILD / f"trends-{level}.csv"
    types = str(col_types()).replace('"', "'")
    gp = GEO_PARQUET[level]
    name = name_expr(level)
    usps_csv = BUILD / "statefp_usps.csv"
    usps_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(usps_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["statefp", "usps"])
        w.writerows(sorted(STATE_USPS.items()))

    col_names = []
    for ind_name, *_ in INDICATORS:
        col_names += [f"d.{ind_name}", f"d.{ind_name}_moe",
                     f"d.chg_{ind_name}", f"d.chg_{ind_name}_moe"]
    cols = ", ".join(col_names)
    if level == "tract":
        extra_join = (f"LEFT JOIN read_parquet('{GEO_PARQUET['county']}') c "
                     f"ON c.GEOID = substr(g.GEOID, 1, 5) ")
    else:
        extra_join = ""
    sql = f"""
        COPY (
            SELECT g.GEOID AS geoid, {name} AS name, u.usps AS state,
                   d.period, d.geo_change,
                   {cols},
                   g.geometry
            FROM read_parquet('{gp}') g
            {extra_join}
            LEFT JOIN read_csv('{csv_path}', header=true, nullstr='',
                               types={types}) d ON d.geoid = g.GEOID
            LEFT JOIN read_csv('{usps_csv}', header=true) u
                   ON u.statefp = substr(g.GEOID, 1, 2)
        ) TO '{tmp}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 20000)
    """
    con.execute(sql)
    run(["gpio", "convert", "geoparquet", tmp, out])
    sorted_tmp = BUILD / f"{cid}.hilbert.parquet"
    run(["gpio", "sort", "hilbert", out, sorted_tmp])
    sorted_tmp.replace(out)
    restore_stats(out)
    tmp.unlink(missing_ok=True)

    n = con.execute(f"SELECT count(*) FROM read_parquet('{out}')").fetchone()[0]
    print(f"  {cid:20s} {n:>7,} rows  {out.stat().st_size/1e6:>7.2f} MB  "
         f"{out.relative_to(ROOT)}")
    return {"rows": n, "path": str(out.relative_to(ROOT))}


def build(levels: list[str]) -> dict:
    report = {}
    con = connect()
    try:
        for level in levels:
            print(f"== {level}-trends ==")
            rows = build_rows(level, con)
            write_csv(rows, BUILD / f"trends-{level}.csv")
            report[level] = assemble(level, con)
    finally:
        con.close()
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("levels", nargs="*", choices=ALL_LEVELS,
                    default=ALL_LEVELS)
    args = ap.parse_args()
    report = build(args.levels or ALL_LEVELS)
    print(report)


if __name__ == "__main__":
    raise SystemExit(main())
