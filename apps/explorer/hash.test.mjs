import { test } from "node:test";
import assert from "node:assert/strict";
import { decodeHash, encodeHash } from "./hash.js";

test("round-trips full state", () => {
  const state = {
    c: "trends/county-trends", s: "styles/default", p: "2015-2019",
    view: "swipe", camera: { zoom: 4.25, lat: 38.5, lng: -98.5 },
  };
  const h = encodeHash(state);
  const back = decodeHash("#" + h);
  assert.equal(back.c, state.c);
  assert.equal(back.s, state.s);
  assert.equal(back.p, state.p);
  assert.equal(back.view, "swipe");
  assert.equal(back.camera.zoom, 4.25);
  assert.equal(back.camera.lng, -98.5);
});

test("omitted keys stay omitted", () => {
  assert.equal(encodeHash({ c: "blocks" }), "c=blocks");
  assert.deepEqual(decodeHash("#"), {});
  assert.deepEqual(decodeHash(""), {});
});

test("ignores junk", () => {
  const out = decodeHash("#c=blocks&m=bad/values/x&evil=1");
  assert.equal(out.c, "blocks");
  assert.equal(out.camera, undefined);
  assert.equal(out.evil, undefined);
});

test("slashes stay readable in collection ids", () => {
  assert.equal(encodeHash({ c: "tracts/tract-income" }), "c=tracts/tract-income");
});
