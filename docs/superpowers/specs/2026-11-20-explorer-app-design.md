# Census Atlas explorer app — design

Date: 2026-11-20. Status: built autonomously on the user's request for "a cool
viewer to explore the data … maplibre / deck.gl based … search and download …
nice cartography, particularly anything you can show over time."

## Intent

A zero-backend web app that shows off the published catalog at
`https://data.source.coop/portolan-mirrors/us-census-catalog`: browse the 52
mapped collections, switch between the 205 curated styles, inspect features,
compare the two ACS periods in the trends collections over time, search for a
place, and download the data.

## Goals

- Every pixel of cartography comes from the catalog's own style JSONs and
  their `portolan:column` / `portolan:breaks` metadata. The app renders what
  the catalog publishes; it does not invent new cartography for existing
  styles.
- Time is a first-class control for the trends collections: period toggle,
  A/B cross-fade animation, and a synced swipe comparison.
- Search covers collections/styles (client-side over a manifest) and places
  (states + counties from a baked gazetteer; all 32,612 places by
  range-reading the published GeoParquet with hyparquet).
- Download panel per collection: GeoParquet, PMTiles, README, upstream source
  files, and a copyable DuckDB snippet.
- Shareable URL hash (camera, collection, style, period, mode).

## Non-goals / anti-goals

- No build step, no framework, no npm. Plain ES modules from CDN pins, the
  firms-catalog pattern. deck.gl is deliberately not used: every layer is a
  2D vector-tile choropleth that MapLibre renders natively, and deck.gl would
  force a Vite build (luma.gl single-copy rule, measured in
  sentinel-2-catalog) for no visual gain.
- Nothing inside `catalog/` changes. The app lives in `apps/explorer/` and is
  deployed to GitHub Pages, never to the published bucket.
- No charts dashboard; the inspect popup shows both periods' values for
  trends features, which is the per-feature time story.

## Approaches considered

1. **Runtime STAC crawl** (firms pattern): fetch catalog.json → 10 groups →
   53 collections → 205 styles at startup. Rejected: ~270 requests before
   first paint.
2. **Build-time manifest** (chosen): `tools/make_viewer_manifest.py` reads the
   local `catalog/` tree (and the local parquet, via DuckDB, for trends
   indicator breaks and the gazetteer) and writes `apps/explorer/manifest.json`
   + `gazetteer.json`. One fetch at startup; the app still resolves all data
   hrefs against the live catalog base (`?base=` overrides for local trees).
3. **Vite + deck.gl app** (sentinel-2 pattern): rejected, see non-goals.

## Decided by the builder (my calls)

- Basemaps: Carto Positron (light) / Dark Matter (dark), keyless, fetched with
  a timeout and a flat-background fallback; data layers insert before the
  first symbol layer so place labels stay above choropleths.
- Synthesized trends styles: per-indicator sequential styles (shared quantile
  breaks across both periods, computed at manifest build) and diverging
  change styles for `chg_*` columns without shipped styles. Convention: blue =
  decrease, red = increase, matching the shipped poverty-change style; legend
  labels state direction explicitly. Dollar indicators carry the
  vintage-inflation caveat from the catalog docs.
- Look: "statistical atlas" — Fraunces display + Public Sans body (the U.S.
  government's open typeface), ink-navy chrome, light/dark themes.
- Pure helpers (legend extraction, hash codec, DuckDB snippet, trends filter
  injection) are separate modules with `node --test` suites, firms-style.

## What's left open

- GitHub Pages must be enabled in repo settings for the deploy workflow to
  take effect.
- Places deep-search depends on hyparquet reading the published
  places.parquet; the app degrades to states+counties search if it fails.
