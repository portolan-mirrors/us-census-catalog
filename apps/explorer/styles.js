// Pure MapLibre style manipulation: resolve catalog style JSONs, extract
// legends, inject trends period filters, synthesize trends styles.
// No DOM, no map. Tested by styles.test.mjs.

/** Resolve pmtiles:// relative source URLs against the style's own URL. */
export function absolutizeStyle(style, styleUrl) {
  const out = structuredClone(style);
  for (const src of Object.values(out.sources ?? {})) {
    if (src.url && src.url.startsWith("pmtiles://")) {
      const rel = src.url.slice("pmtiles://".length);
      if (!/^https?:\/\//.test(rel)) {
        src.url = "pmtiles://" + new URL(rel, styleUrl).href;
      }
    }
  }
  return out;
}

function flattenStep(expr) {
  // ["step", input, color0, b1, color1, ...] -> {breaks, colors}
  const colors = [expr[2]];
  const breaks = [];
  for (let i = 3; i < expr.length; i += 2) {
    breaks.push(expr[i]);
    colors.push(expr[i + 1]);
  }
  return { breaks, colors };
}

function columnOf(expr) {
  if (!Array.isArray(expr)) return null;
  if (expr[0] === "get") return expr[1];
  for (const e of expr) {
    const c = columnOf(e);
    if (c) return c;
  }
  return null;
}

/**
 * Extract a legend from a catalog style document.
 * Returns {column, kind, entries: [{color, label?, value?}], nodata}.
 * kind: "step" | "match" | "interpolate" | "single" | "none".
 */
export function extractLegend(style) {
  const meta = style.metadata ?? {};
  const column = meta["portolan:column"] ?? null;
  let nodata = null;
  let main = null;
  for (const layer of style.layers ?? []) {
    const f = layer.filter;
    const isNoData = Array.isArray(f) && f[0] === "!" &&
      Array.isArray(f[1]) && f[1][0] === "has";
    const paint = layer.paint ?? {};
    const color = paint["fill-color"] ?? paint["circle-color"] ?? paint["line-color"];
    if (isNoData && typeof color === "string") { nodata = color; continue; }
    if (!main && color !== undefined &&
        (layer.type === "fill" || layer.type === "circle")) {
      main = { layer, color };
    }
  }
  if (!main) return { column, kind: "none", entries: [], nodata };
  const { color } = main;
  if (typeof color === "string") {
    return { column, kind: "single", entries: [{ color }], nodata };
  }
  let expr = color;
  // Zoom-banded paint: take the first band.
  if (expr[0] === "step" && Array.isArray(expr[1]) && expr[1][0] === "zoom") {
    expr = expr[2];
  }
  if (expr[0] === "step") {
    const { breaks, colors } = flattenStep(expr);
    return {
      column: column ?? columnOf(expr[1]), kind: "step",
      breaks, entries: colors.map((c) => ({ color: c })), nodata,
    };
  }
  if (expr[0] === "match") {
    const entries = [];
    for (let i = 2; i + 1 < expr.length; i += 2) {
      entries.push({ value: String(expr[i]), color: expr[i + 1] });
    }
    return { column: column ?? columnOf(expr[1]), kind: "match", entries, nodata };
  }
  if (expr[0] === "interpolate") {
    const entries = [];
    for (let i = 3; i + 1 < expr.length; i += 2) {
      entries.push({ value: expr[i], color: expr[i + 1] });
    }
    return { column: column ?? columnOf(expr[2]), kind: "interpolate", entries, nodata };
  }
  return { column, kind: "none", entries: [], nodata };
}

/**
 * The trends tilesets carry one feature per geography: the 2020-2024 row,
 * with the chg_* columns on it. The 2015-2019 value is therefore derived
 * in the paint expression as value minus change.
 */
export function valueExpr(column, period) {
  return period === "2015-2019"
    ? ["-", ["get", column], ["get", "chg_" + column]]
    : ["get", column];
}

export const SEQ_PALETTE = [
  "#440154", "#46327e", "#365c8d", "#277f8e", "#1fa187", "#4ac16d", "#a0da39",
];
// Blue = decrease, red = increase; matches the shipped poverty-change style.
export const DIV_PALETTE = [
  "#2166ac", "#4393c3", "#92c5de", "#d1e5f0",
  "#fddbc7", "#f4a582", "#d6604d", "#b2182b",
];

export function stepExprOn(input, breaks, palette) {
  const expr = ["step", input, palette[0]];
  breaks.forEach((b, i) => expr.push(b, palette[i + 1]));
  return expr;
}

export function stepExpr(column, breaks, palette) {
  return stepExprOn(["get", column], breaks, palette);
}

/**
 * Synthesize layers for a trends indicator.
 * mode "chg": the chg_* column, diverging around zero.
 * mode "seq": one period's values, viridis, shared quantile breaks; the
 * 2015-2019 value is derived (see valueExpr), so geographies whose shape
 * changed between the releases (chg is NULL) draw as no-data there.
 * Returns MapLibre layers bound to `source`/`sourceLayer`, ids prefixed `id`.
 */
export function trendLayers({ id, source, sourceLayer, column, breaks, mode, period }) {
  const chgCol = "chg_" + column;
  const base = { source, "source-layer": sourceLayer };
  let have, miss, input, palette;
  if (mode === "chg") {
    have = ["has", chgCol];
    miss = ["!", ["has", chgCol]];
    input = ["get", chgCol];
    palette = DIV_PALETTE.slice(0, breaks.length + 1);
  } else {
    const derived = period === "2015-2019";
    have = derived
      ? ["all", ["has", column], ["has", chgCol]]
      : ["has", column];
    miss = derived
      ? ["any", ["!", ["has", column]], ["!", ["has", chgCol]]]
      : ["!", ["has", column]];
    input = valueExpr(column, period);
    palette = SEQ_PALETTE.slice(0, breaks.length + 1);
  }
  return [
    {
      id: id + "-nodata", type: "fill", ...base, filter: miss,
      paint: { "fill-color": "#9a9a9a", "fill-opacity": 0.25 },
    },
    {
      id: id + "-fill", type: "fill", ...base, filter: have,
      paint: {
        "fill-color": stepExprOn(input, breaks, palette),
        "fill-opacity": 0.8,
      },
    },
    {
      id: id + "-line", type: "line", ...base, minzoom: 4,
      paint: {
        "line-color": "#555",
        "line-width": ["interpolate", ["linear"], ["zoom"], 4, 0.2, 9, 0.8],
        "line-opacity": ["interpolate", ["linear"], ["zoom"], 4, 0, 6, 0.4],
      },
    },
  ];
}

/** First symbol layer id of a basemap style, for beforeId insertion. */
export function firstSymbolId(style) {
  return style.layers?.find((l) => l.type === "symbol")?.id ?? null;
}
