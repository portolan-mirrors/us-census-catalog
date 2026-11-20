// Place + dataset search combobox. Gazetteer (states, counties) loads on
// first focus; all 32,612 places load on demand by range-reading the
// published GeoParquet with hyparquet.

const HYPARQUET = "https://cdn.jsdelivr.net/npm/hyparquet@1.30.1/+esm";
const COMPRESSORS = "https://cdn.jsdelivr.net/npm/hyparquet-compressors@1.1.1/+esm";

function norm(s) {
  return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
}

export function rankPlaces(entries, query, limit = 8) {
  const q = norm(query);
  if (!q) return [];
  const scored = [];
  for (const e of entries) {
    const name = norm(e[1]);
    let score = -1;
    if (name.startsWith(q)) score = 0;
    else {
      const i = name.indexOf(q);
      if (i >= 0 && (i === 0 || " (".includes(name[i - 1]))) score = 1;
      else if (name.includes(q)) score = 2;
    }
    if (score >= 0) scored.push([score, e[1].length, e]);
  }
  scored.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  return scored.slice(0, limit).map((s) => s[2]);
}

export function rankCollections(manifest, query, limit = 5) {
  const q = norm(query);
  if (!q) return [];
  const out = [];
  for (const [cid, c] of Object.entries(manifest.collections)) {
    const title = norm(c.title);
    let hit = null;
    if (title.includes(q)) hit = { cid, label: c.title };
    else {
      const style = c.styles.find((s) =>
        norm(s.title).includes(q) || (s.column && norm(s.column).includes(q)));
      if (style) hit = { cid, label: c.title, style: style.id, styleTitle: style.title };
      else if (c.cols.some((n) => norm(n).includes(q))) hit = { cid, label: c.title };
    }
    if (hit) out.push(hit);
  }
  out.sort((a, b) => (a.style ? 1 : 0) - (b.style ? 1 : 0) || a.label.length - b.label.length);
  return out.slice(0, limit);
}

export function initSearch({ input, panel, manifest, gazetteerUrl, placesUrl, onPlace, onDataset }) {
  let gaz = null;
  let gazPromise = null;
  let placesLoaded = false;
  let placesLoading = false;
  let items = [];
  let active = -1;

  function loadGaz() {
    gazPromise ??= fetch(gazetteerUrl, { cache: "no-cache" })
      .then((r) => r.json()).then((rows) => { gaz = rows; })
      .catch(() => { gaz = []; });
    return gazPromise;
  }

  async function loadPlaces() {
    if (placesLoaded || placesLoading) return;
    placesLoading = true;
    render();
    try {
      const [{ parquetReadObjects, asyncBufferFromUrl }, { compressors }] =
        await Promise.all([import(HYPARQUET), import(COMPRESSORS)]);
      const file = await asyncBufferFromUrl({ url: placesUrl });
      const rows = await parquetReadObjects({
        file, compressors, columns: ["name", "state", "geoid", "bbox"],
      });
      for (const r of rows) {
        // The published name already carries the state, e.g. "Madison, Wisconsin".
        gaz.push(["place", r.name, r.state, r.geoid,
          [r.bbox.xmin, r.bbox.ymin, r.bbox.xmax, r.bbox.ymax]]);
      }
      placesLoaded = true;
    } catch (e) {
      console.warn("places index failed to load", e);
    } finally {
      placesLoading = false;
      render();
    }
  }

  function render() {
    const q = input.value.trim();
    items = [];
    panel.innerHTML = "";
    if (!q || !gaz) { panel.hidden = true; return; }
    const places = rankPlaces(gaz, q);
    const sets = rankCollections(manifest, q);
    const frag = document.createDocumentFragment();
    const addHeader = (t) => {
      const h = document.createElement("div");
      h.className = "search-h"; h.textContent = t;
      frag.appendChild(h);
    };
    if (places.length) {
      addHeader("Places");
      for (const p of places) {
        const el = document.createElement("button");
        el.type = "button"; el.className = "search-item"; el.role = "option";
        el.innerHTML = `<span class="badge">${p[0]}</span> ${p[1]}`;
        el.addEventListener("click", () => { close(); onPlace(p); });
        items.push(el); frag.appendChild(el);
      }
    }
    if (sets.length) {
      addHeader("Datasets");
      for (const d of sets) {
        const el = document.createElement("button");
        el.type = "button"; el.className = "search-item"; el.role = "option";
        el.innerHTML = d.styleTitle
          ? `<span class="badge">map</span> ${d.styleTitle} <span class="dim">· ${d.label}</span>`
          : `<span class="badge">data</span> ${d.label}`;
        el.addEventListener("click", () => { close(); onDataset(d); });
        items.push(el); frag.appendChild(el);
      }
    }
    if (!placesLoaded) {
      const el = document.createElement("button");
      el.type = "button"; el.className = "search-item search-more";
      el.textContent = placesLoading
        ? "Loading 32,612 places from GeoParquet…"
        : "Search all 32,612 places (reads the published GeoParquet)";
      el.disabled = placesLoading;
      el.addEventListener("click", () => loadPlaces());
      items.push(el); frag.appendChild(el);
    }
    if (!items.length) {
      const el = document.createElement("div");
      el.className = "search-h"; el.textContent = "No matches";
      frag.appendChild(el);
    }
    panel.appendChild(frag);
    panel.hidden = false;
    active = -1;
  }

  function close() { panel.hidden = true; input.blur(); }

  input.addEventListener("focus", () => { loadGaz().then(render); });
  input.addEventListener("input", render);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { close(); return; }
    if (!items.length) return;
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      active = (active + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
      items.forEach((el, i) => el.classList.toggle("active", i === active));
      items[active].scrollIntoView({ block: "nearest" });
    } else if (e.key === "Enter" && active >= 0) {
      e.preventDefault();
      items[active].click();
    }
  });
  document.addEventListener("click", (e) => {
    if (!panel.contains(e.target) && e.target !== input) panel.hidden = true;
  });
}
