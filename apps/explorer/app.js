// Census Atlas explorer. Composes the basemap with layers from the
// catalog's published style JSONs; trends collections get period controls,
// an A/B cross-fade and a synced swipe comparison.

import { decodeHash, encodeHash } from "./hash.js";
import { fmt, unitFor, compact, breakLabels, labelFor, fmtBytes } from "./format.js";
import {
  absolutizeStyle, extractLegend, trendLayers,
  firstSymbolId, SEQ_PALETTE, DIV_PALETTE,
} from "./styles.js";
import { duckdbSnippet, pythonSnippet } from "./snippets.js";
import { initSearch } from "./search.js";

const qs = new URLSearchParams(location.search);
const BASE = (qs.get("base") ??
  "https://data.source.coop/portolan-mirrors/us-census-catalog").replace(/\/$/, "");
const ATTRIB = '<a href="https://www.census.gov/">U.S. Census Bureau</a> · ' +
  '<a href="https://source.coop/portolan-mirrors/us-census-catalog">Source Cooperative</a>';
const CARTO = {
  light: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
  dark: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
};
const PERIODS = ["2015-2019", "2020-2024"];
const DOLLAR_NOTE = "Dollar medians are in each release's own inflation-" +
  "adjusted dollars (2019 vs 2024); part of any change is inflation.";

const $ = (id) => document.getElementById(id);
const el = (tag, cls, html) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html !== undefined) n.innerHTML = html;
  return n;
};

// ---------------------------------------------------------------- state
let manifest = null;
function storedTheme() {
  try { return localStorage.getItem("atlas-theme"); } catch { return null; }
}
const state = {
  c: null, s: null, i: "pct_below_poverty", mode: "chg",
  theme: storedTheme() ??
    (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"),
};
let map, mapB = null;
let activePopup = null;
let playTimer = null;
let currentPeriod = "2020-2024";
let legendInfo = null;
let syncing = false;

const isTrends = (cid) => manifest?.trends.collections.includes(cid);
const entryOf = (cid) => manifest?.collections[cid];
const indicator = () =>
  manifest.trends.indicators.find((x) => x.col === state.i) ??
  manifest.trends.indicators[0];

// ---------------------------------------------------------------- basemap
const basemapCache = {};
function getBasemap(theme) {
  basemapCache[theme] ??= (async () => {
    try {
      const r = await fetch(CARTO[theme], { signal: AbortSignal.timeout(6000) });
      if (!r.ok) throw new Error(String(r.status));
      return await r.json();
    } catch {
      return {
        version: 8, name: "fallback", sources: {},
        layers: [{ id: "bg", type: "background",
          paint: { "background-color": theme === "dark" ? "#10141c" : "#f3f0e9" } }],
      };
    }
  })();
  return basemapCache[theme];
}

// ------------------------------------------------- data layers per state
async function fetchStyleDoc(entry, styleId) {
  const st = entry.styles.find((s) => s.id === styleId) ?? entry.styles[0];
  if (!st) return null;
  const url = `${BASE}/${st.href}`;
  const doc = absolutizeStyle(await (await fetch(url)).json(), url);
  return { st, doc };
}

/** Rebind a catalog style's layers to the shared "census" source id. */
function adoptLayers(doc) {
  return doc.layers.map((l) => ({ ...l, id: "census-" + l.id, source: "census" }));
}

function sourceUrlOf(doc, entry) {
  const src = Object.values(doc?.sources ?? {})[0];
  return src?.url ?? "pmtiles://" + BASE + "/" + entry.tiles.href;
}

/**
 * Build {sourceUrl, layers, legend} for the current state. For trends level
 * modes both periods' fills are present; setPeriod() cross-fades them.
 */
async function buildData() {
  const entry = entryOf(state.c);
  if (!entry?.tiles) return null;
  const layerName = entry.tiles.layer;

  if (isTrends(state.c)) {
    const ind = indicator();
    const unit = ind.unit === "usd" ? "usd" : ind.unit === "pct" ? "pct" : "num";
    if (state.mode === "chg") {
      const shipped = entry.styles.find((s) => s.column === "chg_" + ind.col);
      if (shipped) {
        const got = await fetchStyleDoc(entry, shipped.id);
        const legend = extractLegend(got.doc);
        return {
          sourceUrl: sourceUrlOf(got.doc, entry),
          layers: adoptLayers(got.doc),
          legend: {
            title: shipped.title, kind: "step", unit,
            colors: legend.entries.map((e) => e.color),
            labels: breakLabels(legend.breaks ?? [], unit),
            nodata: legend.nodata, note: shipped.desc,
          },
        };
      }
      const breaks = ind.chgBreaks[state.c];
      return {
        sourceUrl: "pmtiles://" + BASE + "/" + entry.tiles.href,
        layers: trendLayers({
          id: "census-chg", source: "census", sourceLayer: layerName,
          column: ind.col, breaks, mode: "chg",
        }),
        legend: {
          title: ind.label + " — change, 2015-2019 → 2020-2024",
          kind: "step", unit,
          colors: DIV_PALETTE.slice(0, breaks.length + 1),
          labels: breakLabels(breaks, unit),
          nodata: "#9a9a9a",
          note: "Blue fell, red rose. Class breaks at the 50th/80th/95th " +
            "percentile of the absolute change." +
            (ind.unit === "usd" ? " " + DOLLAR_NOTE : ""),
        },
      };
    }
    // Level mode: one fill set per period, cross-faded by opacity.
    const breaks = ind.breaks[state.c];
    const layers = [];
    for (const p of PERIODS) {
      const set = trendLayers({
        id: "census-" + p, source: "census", sourceLayer: layerName,
        column: ind.col, breaks, mode: "seq", period: p,
      }).filter((l) => l.type === "fill");
      for (const l of set) {
        l.paint = { ...l.paint,
          "fill-opacity": p === currentPeriod ? l.paint["fill-opacity"] : 0,
          "fill-opacity-transition": { duration: 700 } };
      }
      layers.push(...set);
    }
    layers.push({
      id: "census-line", type: "line", source: "census",
      "source-layer": layerName, minzoom: 4,
      paint: {
        "line-color": "#555",
        "line-width": ["interpolate", ["linear"], ["zoom"], 4, 0.2, 9, 0.8],
        "line-opacity": ["interpolate", ["linear"], ["zoom"], 4, 0, 6, 0.4],
      },
    });
    return {
      sourceUrl: "pmtiles://" + BASE + "/" + entry.tiles.href,
      layers,
      legend: {
        title: ind.label, kind: "step", unit,
        colors: SEQ_PALETTE.slice(0, breaks.length + 1),
        labels: breakLabels(breaks, unit),
        nodata: "#9a9a9a",
        note: "Same class breaks for both periods (pooled national " +
          "septiles), so color changes mean value changes. 2015-2019 " +
          "values are the published change subtracted from 2020-2024; " +
          "geographies whose boundaries changed draw as no-data there." +
          (ind.unit === "usd" ? " " + DOLLAR_NOTE : ""),
      },
    };
  }

  const got = await fetchStyleDoc(entry, state.s);
  if (!got) return null;
  const legend = extractLegend(got.doc);
  const unit = unitFor(legend.column);
  let labels;
  if (legend.kind === "step") labels = breakLabels(legend.breaks ?? [], unit);
  else if (legend.kind === "match") labels = legend.entries.map((e) => e.value);
  else if (legend.kind === "interpolate") labels = legend.entries.map((e) => compact(e.value, unit));
  else labels = [got.st.title];
  return {
    sourceUrl: sourceUrlOf(got.doc, entry),
    layers: adoptLayers(got.doc),
    legend: {
      title: got.st.title, kind: legend.kind, unit,
      colors: legend.entries.map((e) => e.color),
      labels, nodata: legend.nodata, note: got.st.desc,
      column: legend.column ?? got.st.column,
    },
  };
}

// ---------------------------------------------------------------- render
async function composeStyle(data, theme, periodOverride) {
  const base = structuredClone(await getBasemap(theme));
  if (!data) return base;
  let layers = data.layers;
  if (periodOverride) {
    layers = layers.map((l) => {
      if (!l.id.includes(PERIODS[0]) && !l.id.includes(PERIODS[1])) return l;
      const mine = l.id.includes(periodOverride);
      return { ...l, paint: { ...l.paint, "fill-opacity": mine ? 0.8 : 0 } };
    });
  }
  base.sources = { ...base.sources,
    census: { type: "vector", url: data.sourceUrl, attribution: ATTRIB } };
  const before = firstSymbolId(base);
  const idx = before ? base.layers.findIndex((l) => l.id === before) : base.layers.length;
  base.layers = [...base.layers.slice(0, idx), ...layers, ...base.layers.slice(idx)];
  return base;
}

let renderSeq = 0;
async function renderMap() {
  const seq = ++renderSeq;
  let data = null;
  try {
    data = await buildData();
  } catch (e) {
    console.warn("layer build failed", e);
    note("Could not load this collection's style. " + e.message);
  }
  if (seq !== renderSeq) return;
  activePopup?.remove();
  activePopup = null;
  legendInfo = data?.legend ?? null;
  const style = await composeStyle(data, state.theme,
    inSwipe() ? PERIODS[0] : null);
  if (seq !== renderSeq) return;
  map.setStyle(style, { diff: false });
  if (mapB && inSwipe()) {
    mapB.setStyle(await composeStyle(data, state.theme, PERIODS[1]), { diff: false });
  }
  renderLegend();
  renderDock();
  writeHash();
}

function fillLayerIds(m) {
  return m.getStyle().layers
    .filter((l) => l.id.startsWith("census-") && l.type === "fill")
    .map((l) => l.id);
}

// ------------------------------------------------------------- period/play
function setPeriod(p, animate = true) {
  currentPeriod = p;
  if (!map.getLayer("census-" + p + "-fill")) { renderMap(); return; }
  for (const period of PERIODS) {
    const on = period === p;
    for (const suffix of ["-fill", "-nodata"]) {
      const id = "census-" + period + suffix;
      if (!map.getLayer(id)) continue;
      if (!animate) map.setPaintProperty(id, "fill-opacity-transition", { duration: 0 });
      map.setPaintProperty(id, "fill-opacity",
        on ? (suffix === "-fill" ? 0.8 : 0.25) : 0);
    }
  }
  renderDock();
  writeHash();
}

function stopPlay() {
  if (playTimer) { clearInterval(playTimer); playTimer = null; renderDock(); }
}

function togglePlay() {
  if (playTimer) { stopPlay(); return; }
  if (state.mode === "chg" || inSwipe()) { setMode(currentPeriod); }
  playTimer = setInterval(() => {
    setPeriod(currentPeriod === PERIODS[0] ? PERIODS[1] : PERIODS[0]);
  }, 1600);
  renderDock();
}

const inSwipe = () => state.mode === "swipe";

function setMode(mode) {
  stopPlay();
  const wasSwipe = inSwipe();
  state.mode = mode;
  if (PERIODS.includes(mode)) currentPeriod = mode;
  if (inSwipe() !== wasSwipe) toggleSwipe(inSwipe());
  if (PERIODS.includes(mode) && !wasSwipe &&
      map.getLayer("census-" + mode + "-fill")) {
    setPeriod(mode);
    renderLegend();
    return;
  }
  renderMap();
}

// ---------------------------------------------------------------- swipe
function toggleSwipe(on) {
  const wrap = $("maps");
  wrap.classList.toggle("swipe", on);
  $("swipebar").hidden = !on;
  if (on && !mapB) {
    mapB = new maplibregl.Map({
      container: "mapB", style: { version: 8, sources: {}, layers: [] },
      center: map.getCenter(), zoom: map.getZoom(), attributionControl: false,
    });
    const sync = (from, to) => () => {
      if (syncing) return;
      syncing = true;
      to.jumpTo({ center: from.getCenter(), zoom: from.getZoom(),
        bearing: from.getBearing(), pitch: from.getPitch() });
      syncing = false;
    };
    map.on("move", sync(map, mapB));
    mapB.on("move", sync(mapB, map));
  }
  if (mapB) {
    mapB.jumpTo({ center: map.getCenter(), zoom: map.getZoom() });
    requestAnimationFrame(() => { map.resize(); mapB.resize(); });
  } else {
    requestAnimationFrame(() => map.resize());
  }
}

function initSwipeBar() {
  const bar = $("swipebar");
  const wrap = $("maps");
  let frac = 0.5;
  const apply = () => {
    bar.style.left = frac * 100 + "%";
    $("mapB").style.clipPath = `inset(0 0 0 ${frac * 100}%)`;
  };
  apply();
  let dragging = false;
  bar.addEventListener("pointerdown", (e) => {
    dragging = true; bar.setPointerCapture(e.pointerId);
  });
  bar.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const r = wrap.getBoundingClientRect();
    frac = Math.min(0.95, Math.max(0.05, (e.clientX - r.left) / r.width));
    apply();
  });
  bar.addEventListener("pointerup", () => { dragging = false; });
}

// ---------------------------------------------------------------- legend
function renderLegend() {
  const box = $("legend");
  if (!legendInfo) { box.hidden = true; return; }
  box.hidden = false;
  const L = legendInfo;
  let title = L.title;
  if (isTrends(state.c) && state.mode !== "chg") {
    title += inSwipe() ? " — 2015-2019 ⇆ 2020-2024" : ` — ${currentPeriod}`;
  }
  box.innerHTML = "";
  box.appendChild(el("div", "legend-title", title));
  const rows = el("div", "legend-rows");
  L.colors.forEach((c, i) => {
    const r = el("div", "legend-row");
    r.appendChild(el("span", "swatch")).style.background = c;
    r.appendChild(el("span", "legend-label", L.labels[i] ?? ""));
    rows.appendChild(r);
  });
  if (L.nodata) {
    const r = el("div", "legend-row legend-nodata");
    r.appendChild(el("span", "swatch")).style.background = L.nodata;
    r.appendChild(el("span", "legend-label", "no data"));
    rows.appendChild(r);
  }
  box.appendChild(rows);
  if (L.note) {
    const d = el("details", "legend-note");
    d.appendChild(el("summary", null, "About this view"));
    d.appendChild(el("p", null, L.note));
    box.appendChild(d);
  }
}

// ---------------------------------------------------------------- dock
function renderDock() {
  const dock = $("dock");
  if (!isTrends(state.c)) { dock.hidden = true; return; }
  dock.hidden = false;
  const ind = indicator();
  $("dock-ind").value = ind.col;
  const active = inSwipe() ? "swipe"
    : state.mode === "chg" ? "chg" : currentPeriod;
  for (const b of dock.querySelectorAll("[data-mode]")) {
    b.classList.toggle("active", b.dataset.mode === active);
  }
  $("dock-play").classList.toggle("active", !!playTimer);
  $("dock-play").textContent = playTimer ? "❚❚" : "▶";
  $("dock-play").title = playTimer ? "Pause" : "Animate between periods";
}

function initDock() {
  const sel = $("dock-ind");
  for (const ind of manifest.trends.indicators) {
    const o = document.createElement("option");
    o.value = ind.col; o.textContent = ind.label;
    sel.appendChild(o);
  }
  sel.addEventListener("change", () => {
    stopPlay();
    state.i = sel.value;
    renderMap();
  });
  for (const b of $("dock").querySelectorAll("[data-mode]")) {
    b.addEventListener("click", () => setMode(b.dataset.mode));
  }
  $("dock-play").addEventListener("click", togglePlay);
}

// ---------------------------------------------------------------- popup
function popupHTML(feats) {
  const entry = entryOf(state.c);
  const p0 = feats[0].properties;
  const name = p0.name ?? p0.NAME ?? p0.geoid ?? "";
  let html = `<div class="pop-head"><strong>${name}</strong>`;
  if (p0.geoid) html += ` <code>${p0.geoid}</code>`;
  html += "</div>";
  if (isTrends(state.c)) {
    // The tiles carry the 2020-2024 row with chg_* columns; the 2015-2019
    // value is the published change subtracted back out.
    const b = p0;
    html += `<table class="pop-table"><tr><th></th><th>2015-19</th><th>2020-24</th><th>Δ</th></tr>`;
    for (const ind of manifest.trends.indicators) {
      const u = ind.unit === "usd" ? "usd" : ind.unit === "pct" ? "pct" : ind.unit === "years" ? "years" : "num";
      const now = b[ind.col];
      const chg = b["chg_" + ind.col];
      const then = (now !== undefined && chg !== undefined) ? now - chg : undefined;
      const cls = chg > 0 ? "up" : chg < 0 ? "down" : "";
      const hot = ind.col === state.i ? ' class="hot"' : "";
      html += `<tr${hot}><td>${ind.label}</td><td>${fmt(then, u)}</td>` +
        `<td>${fmt(now, u)}</td>` +
        `<td class="${cls}">${chg === undefined ? "—" : (chg > 0 ? "+" : "") + compact(chg, u)}</td></tr>`;
    }
    html += "</table>";
    const gc = b.geo_change;
    if (gc && gc !== "identical") {
      html += `<div class="pop-note">Geography ${gc} between the two periods.</div>`;
    }
    return html;
  }
  const col = legendInfo?.column ?? entry?.styles[0]?.column;
  const activeCol = col ?? null;
  html += `<table class="pop-table">`;
  if (activeCol && activeCol in p0) {
    const u = unitFor(activeCol);
    html += `<tr class="hot"><td>${labelFor(activeCol)}</td><td>${fmt(p0[activeCol], u)}</td></tr>`;
    const moe = p0[activeCol + "_moe"];
    if (moe !== undefined) {
      html += `<tr><td>± margin of error (90%)</td><td>${fmt(moe, u)}</td></tr>`;
    }
    const cv = p0[activeCol + "_cv"];
    if (cv !== undefined) {
      html += `<tr><td>Coefficient of variation</td><td>${fmt(cv, "cv")}</td></tr>`;
    }
  }
  html += "</table>";
  const rest = Object.entries(p0)
    .filter(([k]) => !["name", "geoid"].includes(k))
    .map(([k, v]) => `<tr><td>${k}</td><td>${fmt(v, unitFor(k))}</td></tr>`)
    .join("");
  html += `<details class="pop-all"><summary>All fields</summary><div class="pop-scroll"><table class="pop-table">${rest}</table></div></details>`;
  return html;
}

function initPopup() {
  map.on("click", (e) => {
    const ids = fillLayerIds(map).filter((id) => map.getLayer(id));
    if (!ids.length) return;
    const feats = map.queryRenderedFeatures(e.point, { layers: ids });
    if (!feats.length) return;
    // All features of the clicked geography (both periods for trends).
    const geoid = feats[0].properties.geoid;
    const mine = feats.filter((f) => f.properties.geoid === geoid);
    activePopup?.remove();
    activePopup = new maplibregl.Popup({ maxWidth: "340px" })
      .setLngLat(e.lngLat).setHTML(popupHTML(mine)).addTo(map);
  });
  map.on("mousemove", (e) => {
    const ids = fillLayerIds(map).filter((id) => map.getLayer(id));
    const feats = ids.length
      ? map.queryRenderedFeatures(e.point, { layers: ids }) : [];
    map.getCanvas().style.cursor = feats.length ? "pointer" : "";
  });
}

// ---------------------------------------------------------------- sidebar
function selectCollection(cid, styleId) {
  stopPlay();
  if (inSwipe()) setMode("chg");
  state.c = cid;
  state.s = styleId ?? entryOf(cid)?.styles.find((s) => s.default)?.id ?? null;
  if (isTrends(cid) && !styleId) state.mode = "chg";
  renderPanel();
  renderMap();
  const entry = entryOf(cid);
  if (entry?.bbox && entry.tiles) {
    const [w, s, e, n] = entry.bbox;
    const c = map.getCenter();
    const inside = c.lng > w && c.lng < e && c.lat > s && c.lat < n;
    if (!inside) {
      map.fitBounds([[Math.max(w, -179), s], [Math.min(e, 180), n]],
        { padding: 40, duration: 900, maxZoom: 9 });
    }
  }
}

function renderBrowse() {
  const root = $("panel");
  root.innerHTML = "";
  root.appendChild(el("p", "intro",
    `${Object.keys(manifest.collections).length} collections of American ` +
    `Community Survey and 2020 Census statistics, from states to blocks. ` +
    `Pick a dataset, or search above.`));
  for (const g of manifest.groups) {
    const d = el("details", "group");
    if (g.id === "trends") d.open = true;
    const sum = el("summary");
    sum.appendChild(el("span", "group-title", g.title));
    sum.appendChild(el("span", "group-n", String(g.collections.length)));
    d.appendChild(sum);
    const list = el("div", "cards");
    for (const cid of g.collections) {
      const c = entryOf(cid);
      const card = el("button", "card");
      card.type = "button";
      if (c.thumb) {
        const img = document.createElement("img");
        img.loading = "lazy";
        img.src = `${BASE}/${c.thumb}`;
        img.alt = "";
        card.appendChild(img);
      }
      const t = el("div", "card-body");
      t.appendChild(el("div", "card-title", c.title));
      t.appendChild(el("div", "card-meta",
        (c.rows ? c.rows.toLocaleString("en-US") + " features · " : "") +
        c.styles.length + (c.styles.length === 1 ? " view" : " views")));
      card.appendChild(t);
      if (!c.tiles) card.classList.add("nodata-card");
      card.addEventListener("click", () => selectCollection(cid));
      list.appendChild(card);
    }
    d.appendChild(list);
    root.appendChild(d);
  }
}

function renderPanel() {
  const root = $("panel");
  const entry = entryOf(state.c);
  if (!entry) { renderBrowse(); return; }
  root.innerHTML = "";
  const back = el("button", "back", "← All collections");
  back.type = "button";
  back.addEventListener("click", () => {
    state.c = null; state.s = null;
    legendInfo = null;
    stopPlay();
    if (inSwipe()) { state.mode = "chg"; toggleSwipe(false); }
    renderBrowse();
    renderMap();
  });
  root.appendChild(back);
  root.appendChild(el("h2", "coll-title", entry.title));
  const meta = [];
  if (entry.rows) meta.push(entry.rows.toLocaleString("en-US") + " features");
  const g = manifest.groups.find((x) => x.id === entry.group);
  if (g && g.id !== state.c) meta.push(g.title);
  root.appendChild(el("div", "coll-meta", meta.join(" · ")));
  root.appendChild(el("p", "coll-desc", entry.desc));

  if (entry.tiles) {
    const zoomBtn = el("button", "ghost", "Zoom to extent");
    zoomBtn.type = "button";
    zoomBtn.addEventListener("click", () => {
      const [w, s, e, n] = entry.bbox;
      map.fitBounds([[Math.max(w, -179), s], [Math.min(e, 180), n]], { padding: 40 });
    });
    root.appendChild(zoomBtn);
  }

  if (isTrends(state.c)) {
    root.appendChild(el("p", "hint",
      "Use the time dock at the bottom of the map: pick an indicator, " +
      "flip between the 2015-2019 and 2020-2024 releases, press ▶ to " +
      "animate, or Compare to swipe the two periods side by side."));
  } else if (entry.styles.length) {
    root.appendChild(el("h3", "sec", "Views"));
    const list = el("div", "style-list");
    for (const st of entry.styles) {
      const b = el("button", "style-btn" + (st.id === state.s ? " active" : ""));
      b.type = "button";
      b.appendChild(el("div", "style-title", st.title));
      b.addEventListener("click", () => {
        state.s = st.id;
        renderPanel(); renderMap();
      });
      list.appendChild(b);
    }
    root.appendChild(list);
    const active = entry.styles.find((s) => s.id === state.s);
    if (active?.desc) root.appendChild(el("p", "style-desc", active.desc));
  } else if (!entry.tiles) {
    root.appendChild(el("p", "hint",
      "This collection has no map layer; it is table data for download."));
  }

  // ------------------------------------------------ downloads
  root.appendChild(el("h3", "sec", "Get the data"));
  const dl = el("div", "dl-list");
  for (const d of entry.data) {
    const href = d.glob ? null : `${BASE}/${d.href}`;
    const row = el(href ? "a" : "div", "dl-row");
    if (href) { row.href = href; }
    row.appendChild(el("span", "dl-name",
      (d.glob ? "GeoParquet (hive-partitioned)" :
        entry.data.length > 1 ? d.href.split("/").pop() : "GeoParquet")));
    row.appendChild(el("span", "dl-size",
      d.size ? fmtBytes(d.size) : "52 partitions"));
    dl.appendChild(row);
    if (entry.data.length > 6 && dl.children.length >= 6) break;
  }
  if (entry.data.length > 6) {
    dl.appendChild(el("div", "dl-more",
      `+ ${entry.data.length - dl.children.length} more files — see the collection document`));
  }
  if (entry.tiles) {
    const row = el("a", "dl-row");
    row.href = `${BASE}/${entry.tiles.href}`;
    row.appendChild(el("span", "dl-name", "PMTiles"));
    row.appendChild(el("span", "dl-size", fmtBytes(entry.tiles.size)));
    dl.appendChild(row);
  }
  const cj = el("a", "dl-row");
  cj.href = `${BASE}/${entry.dir}/collection.json`;
  cj.target = "_blank";
  cj.appendChild(el("span", "dl-name", "STAC collection"));
  cj.appendChild(el("span", "dl-size", "JSON"));
  dl.appendChild(cj);
  if (entry.readme) {
    const rm = el("a", "dl-row");
    rm.href = `${BASE}/${entry.readme}`;
    rm.target = "_blank";
    rm.appendChild(el("span", "dl-name", "README"));
    rm.appendChild(el("span", "dl-size", "Markdown"));
    dl.appendChild(rm);
  }
  root.appendChild(dl);

  const srcDetails = el("details", "sources");
  srcDetails.appendChild(el("summary", null, "Upstream census.gov sources"));
  const srcBox = el("div", "src-box", "Loading…");
  srcDetails.appendChild(srcBox);
  let srcLoaded = false;
  srcDetails.addEventListener("toggle", async () => {
    if (!srcDetails.open || srcLoaded) return;
    srcLoaded = true;
    try {
      const coll = await (await fetch(`${BASE}/${entry.dir}/collection.json`)).json();
      srcBox.innerHTML = "";
      for (const [k, a] of Object.entries(coll.assets ?? {})) {
        if (!(a.roles ?? []).includes("source")) continue;
        const r = el("a", "src-row", a.title ?? k);
        r.href = a.href; r.target = "_blank";
        srcBox.appendChild(r);
      }
      if (!srcBox.children.length) srcBox.textContent = "None listed.";
    } catch {
      srcBox.textContent = "Could not load the collection document.";
    }
  });
  root.appendChild(srcDetails);

  const duck = duckdbSnippet(entry, BASE);
  if (duck) root.appendChild(snippetBox("Query it with DuckDB", duck));
  const py = pythonSnippet(entry, BASE);
  if (py) root.appendChild(snippetBox("Load it in Python", py));
}

function snippetBox(title, code) {
  const d = el("details", "snippet");
  d.appendChild(el("summary", null, title));
  const pre = el("pre");
  pre.textContent = code;
  const btn = el("button", "copy", "Copy");
  btn.type = "button";
  btn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(code);
      btn.textContent = "Copied";
      setTimeout(() => { btn.textContent = "Copy"; }, 1200);
    } catch { /* clipboard unavailable */ }
  });
  d.appendChild(btn);
  d.appendChild(pre);
  return d;
}

// ---------------------------------------------------------------- misc UI
function note(msg) {
  const n = $("note");
  n.textContent = msg;
  n.hidden = false;
  clearTimeout(note.t);
  note.t = setTimeout(() => { n.hidden = true; }, 6000);
}

function writeHash() {
  const c = map.getCenter();
  const h = encodeHash({
    c: state.c, s: isTrends(state.c) ? null : state.s,
    i: isTrends(state.c) ? state.i : null,
    mode: isTrends(state.c) ? (inSwipe() ? "swipe" : state.mode) : null,
    camera: { zoom: map.getZoom(), lat: c.lat, lng: c.lng },
  });
  history.replaceState(null, "", "#" + h);
}

function applyTheme() {
  document.documentElement.dataset.theme = state.theme;
  $("themebtn").textContent = state.theme === "dark" ? "☀" : "◐";
}

// ---------------------------------------------------------------- boot
async function boot() {
  const protocol = new pmtiles.Protocol();
  maplibregl.addProtocol("pmtiles", protocol.tile);

  const want = decodeHash(location.hash);
  if (want.i) state.i = want.i;
  if (want.mode) state.mode = want.mode;
  if (PERIODS.includes(want.mode)) currentPeriod = want.mode;

  applyTheme();
  window.ATLAS = { get map() { return map; }, get mapB() { return mapB; },
    state, get manifest() { return manifest; }, phase: "init" };
  map = new maplibregl.Map({
    container: "map",
    style: { version: 8, sources: {}, layers: [] },
    center: want.camera ? [want.camera.lng, want.camera.lat] : [-96.0, 38.8],
    zoom: want.camera?.zoom ?? 3.6,
    attributionControl: { compact: true },
  });
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
  map.on("error", (e) => console.warn("[atlas]", e.error?.message ?? e));
  map.on("moveend", writeHash);
  // Restyling before the constructor style finishes loading wedges the map.
  window.ATLAS.phase = "await-load";
  await new Promise((res) => (map.isStyleLoaded() ? res() : map.once("load", res)));
  window.ATLAS.phase = "loaded";
  initPopup();
  initSwipeBar();

  manifest = await (await fetch("manifest.json", { cache: "no-cache" })).json();
  initDock();
  initSearch({
    input: $("q"), panel: $("search-results"), manifest,
    gazetteerUrl: "gazetteer.json",
    placesUrl: `${BASE}/places/places.parquet`,
    onPlace: (p) => {
      const [w, s, e, n] = p[4];
      map.fitBounds([[w, s], [e, n]], { padding: 60, maxZoom: 12 });
      $("q").value = "";
    },
    onDataset: (d) => {
      selectCollection(d.cid, d.style);
      $("q").value = "";
    },
  });

  $("themebtn").addEventListener("click", () => {
    state.theme = state.theme === "dark" ? "light" : "dark";
    try { localStorage.setItem("atlas-theme", state.theme); } catch { /* fine */ }
    applyTheme();
    renderMap();
    if (mapB && inSwipe()) renderMap();
  });
  $("menubtn").addEventListener("click", () => {
    $("sidebar").classList.toggle("open");
  });

  const startC = want.c && entryOf(want.c) ? want.c : "trends/county-trends";
  state.c = startC;
  state.s = want.s ?? entryOf(startC)?.styles.find((s) => s.default)?.id ?? null;
  if (inSwipe()) toggleSwipe(true);
  renderPanel();
  renderMap();
}

boot().then(() => {
  window.ATLAS.phase = "ready";
}).catch((e) => {
  console.error(e);
  note("The explorer failed to start: " + e.message);
});
