### What happened?

A collection whose data spans the antimeridian (US-wide census data: the Aleutian Islands reach +172°..+180°E, the Pacific island areas sit at +144°E, everything else is -179°..-64°W) gets a STAC spatial extent that either spans the whole globe or uses the STAC/GeoJSON antimeridian convention (west > east). In both cases the browser's map fits the bbox naively: the opening view centers on the Atlantic/Africa and the data sits at the edges of a world view. A west > east bbox is not recognized as antimeridian-crossing.

### Why it matters

Any US-nationwide dataset (and any Pacific dataset) opens on an empty ocean view. The catalog author's only workaround is to declare a framing extent narrower than the data, which conflicts with PTL-DAT-005.

### How to reproduce

Load https://data.source.coop/portolan-mirrors/us-census-catalog/block-groups/bg-income/collection.json in the browser, set its extent bbox to [-179.15, -14.55, 179.78, 71.39] (the true data bbox) or [144.6, -14.6, -64.5, 71.4] (STAC antimeridian form). Observe the opening view in both cases.

### Implementation notes

MapLibre's fitBounds does not take antimeridian-crossing boxes directly; detect west > east and either fit [west, south, east + 360, north] or split the box and fit the larger piece. STAC spec (and GeoJSON RFC 7946 §5.2) define west > east as antimeridian-crossing.

### How to confirm the fix

The bg-income collection above, with its true data bbox restored, opens centered on the United States.

### Version

Portolan Browser 0.1.0 (browser.portolan-sdi.org), 2026-11-13.
