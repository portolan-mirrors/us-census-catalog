import { test } from "node:test";
import assert from "node:assert/strict";
import {
  absolutizeStyle, extractLegend, valueExpr,
  stepExpr, trendLayers, firstSymbolId, DIV_PALETTE,
} from "./styles.js";

const SHIPPED = {
  version: 8,
  metadata: {
    "portolan:column": "chg_pct_below_poverty",
    "portolan:breaks": [-6, -3, -1, 0, 1, 3, 6],
  },
  sources: { data: { type: "vector", url: "pmtiles://../county-trends.pmtiles" } },
  layers: [
    {
      id: "no-data", type: "fill", source: "data", "source-layer": "county-trends",
      filter: ["!", ["has", "chg_pct_below_poverty"]],
      paint: { "fill-color": "#cccccc", "fill-opacity": 0.35 },
    },
    {
      id: "fill", type: "fill", source: "data", "source-layer": "county-trends",
      filter: ["has", "chg_pct_below_poverty"],
      paint: {
        "fill-color": ["step", ["get", "chg_pct_below_poverty"],
          "#2166ac", -6, "#4393c3", -3, "#92c5de", -1, "#d1e5f0",
          0, "#fddbc7", 1, "#f4a582", 3, "#d6604d", 6, "#b2182b"],
        "fill-opacity": 0.8,
      },
    },
    { id: "outline", type: "line", source: "data", "source-layer": "county-trends",
      paint: { "line-color": "#4d4d4d" } },
  ],
};

test("absolutizeStyle resolves relative pmtiles URLs against the style URL", () => {
  const url = "https://ex.com/cat/trends/county-trends/styles/default.json";
  const out = absolutizeStyle(SHIPPED, url);
  assert.equal(out.sources.data.url,
    "pmtiles://https://ex.com/cat/trends/county-trends/county-trends.pmtiles");
  // The input is not mutated.
  assert.equal(SHIPPED.sources.data.url, "pmtiles://../county-trends.pmtiles");
});

test("absolutizeStyle leaves absolute pmtiles URLs alone", () => {
  const style = { sources: { d: { url: "pmtiles://https://a.com/x.pmtiles" } } };
  const out = absolutizeStyle(style, "https://b.com/s.json");
  assert.equal(out.sources.d.url, "pmtiles://https://a.com/x.pmtiles");
});

test("extractLegend reads a step legend plus the no-data swatch", () => {
  const leg = extractLegend(SHIPPED);
  assert.equal(leg.kind, "step");
  assert.equal(leg.column, "chg_pct_below_poverty");
  assert.deepEqual(leg.breaks, [-6, -3, -1, 0, 1, 3, 6]);
  assert.equal(leg.entries.length, 8);
  assert.equal(leg.entries[0].color, "#2166ac");
  assert.equal(leg.nodata, "#cccccc");
});

test("extractLegend handles match expressions", () => {
  const leg = extractLegend({
    layers: [{
      id: "f", type: "fill",
      paint: { "fill-color": ["match", ["get", "cat"], "a", "#111", "b", "#222", "#333"] },
    }],
  });
  assert.equal(leg.kind, "match");
  assert.equal(leg.column, "cat");
  assert.deepEqual(leg.entries, [
    { value: "a", color: "#111" }, { value: "b", color: "#222" },
  ]);
});

test("extractLegend unwraps zoom-banded step paint", () => {
  const leg = extractLegend({
    layers: [{
      id: "f", type: "fill",
      paint: { "fill-color": ["step", ["zoom"],
        ["step", ["get", "v"], "#a", 10, "#b"], 8,
        ["step", ["get", "v"], "#c", 20, "#d"]] },
    }],
  });
  assert.equal(leg.kind, "step");
  assert.deepEqual(leg.breaks, [10]);
});

test("valueExpr reads the column now, derives it for 2015-2019", () => {
  assert.deepEqual(valueExpr("median_hh_income", "2020-2024"),
    ["get", "median_hh_income"]);
  assert.deepEqual(valueExpr("median_hh_income", "2015-2019"),
    ["-", ["get", "median_hh_income"], ["get", "chg_median_hh_income"]]);
});

test("stepExpr interleaves breaks and palette", () => {
  assert.deepEqual(stepExpr("v", [1, 2], ["#a", "#b", "#c"]),
    ["step", ["get", "v"], "#a", 1, "#b", 2, "#c"]);
});

test("trendLayers chg mode uses the chg_ column", () => {
  const ls = trendLayers({
    id: "t", source: "s", sourceLayer: "sl", column: "pct_below_poverty",
    breaks: [-6, -3, 0, 3, 6], mode: "chg",
  });
  assert.equal(ls.length, 3);
  const fill = ls.find((l) => l.id === "t-fill");
  assert.deepEqual(fill.filter, ["has", "chg_pct_below_poverty"]);
  assert.equal(fill.paint["fill-color"][1][1], "chg_pct_below_poverty");
  assert.equal(fill.paint["fill-color"].length, 3 + 2 * 5);
  assert.equal(fill.paint["fill-color"][2], DIV_PALETTE[0]);
});

test("trendLayers 2020-2024 reads the column directly", () => {
  const ls = trendLayers({
    id: "t", source: "s", sourceLayer: "sl", column: "median_hh_income",
    breaks: [40000, 55000], mode: "seq", period: "2020-2024",
  });
  const fill = ls.find((l) => l.id === "t-fill");
  assert.deepEqual(fill.filter, ["has", "median_hh_income"]);
  assert.deepEqual(fill.paint["fill-color"][1], ["get", "median_hh_income"]);
});

test("trendLayers 2015-2019 derives value minus change and needs both", () => {
  const ls = trendLayers({
    id: "t", source: "s", sourceLayer: "sl", column: "median_hh_income",
    breaks: [40000, 55000], mode: "seq", period: "2015-2019",
  });
  const fill = ls.find((l) => l.id === "t-fill");
  assert.deepEqual(fill.filter,
    ["all", ["has", "median_hh_income"], ["has", "chg_median_hh_income"]]);
  assert.deepEqual(fill.paint["fill-color"][1],
    ["-", ["get", "median_hh_income"], ["get", "chg_median_hh_income"]]);
  const nodata = ls.find((l) => l.id === "t-nodata");
  assert.equal(nodata.filter[0], "any");
});

test("firstSymbolId finds the label layer", () => {
  assert.equal(firstSymbolId({ layers: [
    { id: "bg", type: "background" }, { id: "labels", type: "symbol" },
  ] }), "labels");
  assert.equal(firstSymbolId({ layers: [{ id: "bg", type: "background" }] }), null);
});
