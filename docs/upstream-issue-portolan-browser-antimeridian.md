### What happened?

Some collections hold data on both sides of the antimeridian. US-wide census data is one. The Aleutian Islands reach +172°..+180°E. The Pacific island areas sit near +144°E. The rest of the data sits at -179°..-64°W.

Such a collection gets a STAC spatial extent in one of two honest forms. The first form spans the whole globe. The second form uses the STAC/GeoJSON antimeridian convention, where west > east. The browser fits both forms naively. The map then opens on the Atlantic and Africa. The data sits at the edges of a world view. The browser does not recognize a west > east bbox as one that crosses the antimeridian.

### Why it matters

Every US-nationwide dataset opens on an empty ocean view. Every Pacific dataset does too. The catalog author's only workaround is a frame extent narrower than the data. That workaround conflicts with PTL-DAT-005.

### Priority

P2

### How to reproduce

1. Load https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/collection.json in the browser.
2. Set its extent bbox to [-179.15, -14.55, 179.78, 71.39]. This is the true data bbox.
3. Observe the view that opens.
4. Set the bbox to [144.6, -14.6, -64.5, 71.4]. This is the STAC antimeridian form.
5. Observe the view again.

### Implementation notes

MapLibre's fitBounds does not take a bbox that crosses the antimeridian. Detect west > east. Then fit [west, south, east + 360, north], or split the box and fit the larger piece. The STAC spec and GeoJSON RFC 7946 §5.2 define west > east as the antimeridian form.

### How to confirm the fix

Restore the true data bbox on the bg-income collection above. The map opens centered on the United States.

### Version

Portolan Browser 0.1.0 (browser.portolan-sdi.org), 2026-11-13.
