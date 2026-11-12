#!/bin/bash
# Download all upstream census source files into staging/census-cache/.
# Everything here is plain HTTPS from census.gov — no API key.
# Idempotent: skips files that already exist and are complete (curl -C -).
set -u
CACHE="$(dirname "$0")/../staging/census-cache"
mkdir -p "$CACHE"
cd "$CACHE"

ACS_SF="https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF"
CB="https://www2.census.gov/geo/tiger/GENZ2024/shp"
CB2020="https://www2.census.gov/geo/tiger/GENZ2020/shp"

get () {
  local url="$1"
  local name="${2:-$(basename "$url")}"
  if [ -f "$name" ]; then echo "have $name"; return 0; fi
  echo "GET $name"
  curl -fsSL --retry 3 --retry-delay 5 -C - -o "$name.part" "$url" \
    && mv "$name.part" "$name" || echo "FAILED $url" >> failures.log
}

# --- Geometry: national cartographic boundary files (GENZ2024, 500k) ---
get "$CB/cb_2024_us_bg_500k.zip"
get "$CB/cb_2024_us_tract_500k.zip"
get "$CB/cb_2024_us_county_500k.zip"
get "$CB/cb_2024_us_state_500k.zip"
get "$CB/cb_2024_us_place_500k.zip"
# Congressional districts: the file name carries the congress number, and
# 119 is the congress the ACS 2024 5-year release tabulates (its GEO_ID
# prefix is 5001900US). See docs/acs-build-notes.md, "Wave 3".
get "$CB/cb_2024_us_cd119_500k.zip"
# ZCTAs: GENZ2020 is the ONLY cartographic ZCTA edition the Census Bureau
# publishes (GENZ2021-GENZ2024 carry no zcta file), and the 2020-based
# ZCTAs are the vintage the ACS tabulates (prefix 860Z200US).
get "$CB2020/cb_2020_us_zcta520_500k.zip"

# --- ACS 2020-2024 5-year table shells (pins line numbers) ---
get "$ACS_SF/documentation/ACS20245YR_Table_Shells.txt"

# --- ACS tables: block-group spec ---
for t in b01001 b01002 b01003 b03002 b15003 b19013 b19301 c17002 \
         b22010 b23025 b25002 b25003 b25024 b25034 b25044 b25064 \
         b25070 b25077 b08301 b08303 b28001 b28002; do
  get "$ACS_SF/data/5YRData/acsdt5y2024-$t.dat"
done

# --- ACS tables: tract-only additions (wellbeing + income by race) ---
for t in b27001 b18101 b05002 b26001 b19013b b17020b b19013h b19013i b19013d; do
  get "$ACS_SF/data/5YRData/acsdt5y2024-$t.dat"
done

echo "DONE $(date)"
ls -la | tail -3
[ -f failures.log ] && { echo "FAILURES:"; cat failures.log; exit 1; }
exit 0
