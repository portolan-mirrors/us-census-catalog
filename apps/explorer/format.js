// Pure value/label formatting. No DOM, no map. Tested by format.test.mjs.

/** Infer a display unit from a catalog column name. */
export function unitFor(col) {
  if (!col) return "num";
  const base = col.replace(/_moe$/, "").replace(/^chg_/, "");
  if (/_cv$/.test(base)) return "cv";
  if (base === "gini") return "gini";
  if (/^pct_|_pct$|^share_/.test(base)) return "pct";
  if (/income|_value$|_rent$|home_value|earnings|_cost$/.test(base)) return "usd";
  if (/^median_age$|_age$/.test(base)) return "years";
  if (/density/.test(base)) return "density";
  if (/year_built|_year$/.test(base)) return "year";
  return "num";
}

const nf0 = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
const nf1 = new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 });
const nf2 = new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 });

/** Format one value in a unit from unitFor(). Returns "—" for null. */
export function fmt(v, unit = "num") {
  if (v === null || v === undefined || v === "" || Number.isNaN(v)) return "—";
  if (typeof v !== "number") return String(v);
  switch (unit) {
    case "pct": return nf1.format(v) + "%";
    case "usd": return "$" + nf0.format(Math.round(v));
    case "years": return nf1.format(v) + " yrs";
    case "cv": return nf2.format(v);
    case "gini": return nf2.format(v);
    case "density": return nf0.format(v) + "/km²";
    case "year": return String(Math.round(v));
    default:
      return Math.abs(v) >= 1000 || Number.isInteger(v)
        ? nf0.format(v) : nf1.format(v);
  }
}

/** Compact break label: $40k, 1.5M, 12%. */
export function compact(v, unit = "num") {
  if (v === null || v === undefined) return "—";
  const sign = v < 0 ? "−" : "";
  const a = Math.abs(v);
  let s;
  if (a >= 1e6) s = nf1.format(a / 1e6) + "M";
  else if (a >= 1e3) s = nf1.format(a / 1e3) + "k";
  else s = a >= 100 ? nf0.format(a) : nf1.format(a);
  if (unit === "usd") return sign + "$" + s;
  if (unit === "pct") return sign + s + (a >= 1e3 ? "" : "%");
  return sign + s;
}

/** Legend labels for N+1 classes split at N ascending breaks. */
export function breakLabels(breaks, unit) {
  const out = [];
  for (let i = 0; i <= breaks.length; i++) {
    if (i === 0) out.push("< " + compact(breaks[0], unit));
    else if (i === breaks.length) out.push("≥ " + compact(breaks[breaks.length - 1], unit));
    else out.push(compact(breaks[i - 1], unit) + " – " + compact(breaks[i], unit));
  }
  return out;
}

/** Human label for a snake_case column name. */
export function labelFor(col) {
  const special = {
    geoid: "GEOID", moe: "MOE", cv: "CV", pct: "%", hh: "household",
    acs: "ACS", snap: "SNAP", gini: "Gini",
  };
  const words = col.split("_").map((w) => special[w] ?? w);
  const s = words.join(" ");
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/** Bytes to a human string. */
export function fmtBytes(n) {
  if (n === null || n === undefined) return "";
  if (n >= 1e9) return nf1.format(n / 1e9) + " GB";
  if (n >= 1e6) return nf0.format(n / 1e6) + " MB";
  if (n >= 1e3) return nf0.format(n / 1e3) + " KB";
  return n + " B";
}
