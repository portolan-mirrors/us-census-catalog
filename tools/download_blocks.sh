#!/bin/bash
# Download 2020 block-level sources for all states + DC + PR:
#   - TIGER/Line 2024 TABBLOCK20 shapefiles (block geometry)
#   - 2020 P.L. 94-171 redistricting data (block-level counts)
# Idempotent; failures logged, not fatal per-file.
set -u
CACHE="$(dirname "$0")/../staging/blocks-cache"
mkdir -p "$CACHE"
cd "$CACHE"

TIGER="https://www2.census.gov/geo/tiger/TIGER2024/TABBLOCK20"
PL="https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171"

get () {
  local url="$1" name
  name="$(basename "$url")"
  if [ -f "$name" ]; then echo "have $name"; return 0; fi
  echo "GET $name"
  curl -fsSL --retry 3 --retry-delay 10 -C - -o "$name.part" "$url" \
    && mv "$name.part" "$name" || echo "FAILED $url" >> failures.log
}

# fips|abbrev|PL-directory-name
STATES="01|al|Alabama 02|ak|Alaska 04|az|Arizona 05|ar|Arkansas 06|ca|California
08|co|Colorado 09|ct|Connecticut 10|de|Delaware 11|dc|District_of_Columbia
12|fl|Florida 13|ga|Georgia 15|hi|Hawaii 16|id|Idaho 17|il|Illinois
18|in|Indiana 19|ia|Iowa 20|ks|Kansas 21|ky|Kentucky 22|la|Louisiana
23|me|Maine 24|md|Maryland 25|ma|Massachusetts 26|mi|Michigan 27|mn|Minnesota
28|ms|Mississippi 29|mo|Missouri 30|mt|Montana 31|ne|Nebraska 32|nv|Nevada
33|nh|New_Hampshire 34|nj|New_Jersey 35|nm|New_Mexico 36|ny|New_York
37|nc|North_Carolina 38|nd|North_Dakota 39|oh|Ohio 40|ok|Oklahoma 41|or|Oregon
42|pa|Pennsylvania 44|ri|Rhode_Island 45|sc|South_Carolina 46|sd|South_Dakota
47|tn|Tennessee 48|tx|Texas 49|ut|Utah 50|vt|Vermont 51|va|Virginia
53|wa|Washington 54|wv|West_Virginia 55|wi|Wisconsin 56|wy|Wyoming
72|pr|Puerto_Rico"

for entry in $STATES; do
  fips="${entry%%|*}"; rest="${entry#*|}"
  ab="${rest%%|*}"; dir="${rest#*|}"
  get "$TIGER/tl_2024_${fips}_tabblock20.zip"
  get "$PL/$dir/${ab}2020.pl.zip"
done

echo "DONE $(date)"
du -sh .
[ -f failures.log ] && { echo FAILURES:; cat failures.log; }
exit 0
