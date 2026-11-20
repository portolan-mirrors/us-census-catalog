// Shareable URL hash codec. Omitted keys mean "the default".
// `#c=trends/county-trends&s=styles/default&m=4.2/38.5/-98.5&p=2020-2024`
// Pure; tested by hash.test.mjs.

export function decodeHash(hash) {
  const out = {};
  const body = (hash ?? "").replace(/^#/, "");
  if (!body) return out;
  for (const pair of body.split("&")) {
    const i = pair.indexOf("=");
    if (i < 1) continue;
    const k = pair.slice(0, i);
    const v = decodeURIComponent(pair.slice(i + 1));
    if (k === "m") {
      const parts = v.split("/").map(Number);
      if (parts.length === 3 && parts.every(Number.isFinite)) {
        out.camera = { zoom: parts[0], lat: parts[1], lng: parts[2] };
      }
    } else if (["c", "s", "p", "i", "view", "mode"].includes(k)) {
      out[k] = v;
    }
  }
  return out;
}

export function encodeHash(state) {
  const parts = [];
  const put = (k, v) => {
    if (v !== null && v !== undefined && v !== "") {
      parts.push(k + "=" + encodeURIComponent(v).replaceAll("%2F", "/"));
    }
  };
  put("c", state.c);
  put("s", state.s);
  put("i", state.i);
  put("mode", state.mode);
  put("p", state.p);
  put("view", state.view);
  if (state.camera) {
    const { zoom, lat, lng } = state.camera;
    parts.push(`m=${zoom.toFixed(2)}/${lat.toFixed(4)}/${lng.toFixed(4)}`);
  }
  return parts.join("&");
}
