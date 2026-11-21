// The about page makes claims about the data. These tests measure them
// against manifest.json, so a renamed or imagined column fails the build
// rather than teaching a reader a column that does not exist.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import { copyLabel } from "./about-copy.js";

const html = readFileSync(new URL("./about.html", import.meta.url), "utf8");
const manifest = JSON.parse(
  readFileSync(new URL("./manifest.json", import.meta.url), "utf8"),
);

/** Every <div class="q" …> example, with its declared collections and columns. */
function examples() {
  const out = [];
  const re = /<div class="q"([^>]*)>/g;
  for (const [, attrs] of html.matchAll(re)) {
    const coll = /data-collection="([^"]+)"/.exec(attrs);
    const cols = /data-cols="([^"]+)"/.exec(attrs);
    out.push({
      collections: coll ? coll[1].split(",").map((s) => s.trim()) : [],
      columns: cols ? cols[1].split(",").map((s) => s.trim()) : [],
      attrs,
    });
  }
  return out;
}

/** The text of every <pre> on the page. */
function preBlocks() {
  return [...html.matchAll(/<pre>([\s\S]*?)<\/pre>/g)].map((m) => m[1]);
}

test("the page carries query examples", () => {
  assert.ok(examples().length >= 5, "expected at least five examples");
});

test("every example declares its collections and columns", () => {
  for (const ex of examples()) {
    assert.ok(
      ex.collections.length > 0,
      `an example has no data-collection: ${ex.attrs}`,
    );
    assert.ok(
      ex.columns.length > 0,
      `an example has no data-cols: ${ex.attrs}`,
    );
  }
});

test("every declared collection exists in the manifest", () => {
  for (const ex of examples()) {
    for (const key of ex.collections) {
      assert.ok(
        manifest.collections[key],
        `about.html names a collection the catalog does not publish: ${key}`,
      );
    }
  }
});

test("every column an example names exists in one of its collections", () => {
  // bbox and geometry are GeoParquet structure, not indicator columns, and
  // the manifest lists them per collection like any other.
  for (const ex of examples()) {
    const known = new Set();
    for (const key of ex.collections) {
      for (const c of manifest.collections[key].cols) known.add(c);
    }
    // Hive partition keys are directory names, not columns in the file.
    known.add("state_fips");
    for (const col of ex.columns) {
      assert.ok(
        known.has(col),
        `about.html names "${col}", which is not a column of ` +
          `${ex.collections.join(" or ")}`,
      );
    }
  }
});

test("a declared column actually appears in its example's SQL", () => {
  // Guards the other direction: data-cols cannot drift away from the query
  // it describes, which would make the check above pass while the SQL rots.
  const blocks = preBlocks().join("\n");
  for (const ex of examples()) {
    for (const col of ex.columns) {
      assert.ok(
        new RegExp(`\\b${col}\\b`).test(blocks),
        `data-cols lists "${col}" but no snippet on the page uses it`,
      );
    }
  }
});

test("the stated row counts match the manifest", () => {
  // Each pair is a number printed on the page and the collection it describes.
  const claims = [
    ["3,235", "counties/counties"],
    ["441", "congressional-districts/congressional-districts"],
    ["33,791", "zctas/zctas"],
    ["32,612", "places/places"],
    ["85,184", "tracts/tract-income"],
    ["242,298", "block-groups/bg-income"],
    ["8,174,955", "blocks"],
    ["6,470", "trends/county-trends"],
    ["56", "states/states"],
  ];
  for (const [printed, key] of claims) {
    const rows = manifest.collections[key].rows;
    assert.equal(
      rows.toLocaleString("en-US"),
      printed,
      `the page prints ${printed} for ${key}, which now has ${rows} rows`,
    );
    assert.ok(
      html.includes(`>${printed}<`) || html.includes(`${printed} `),
      `the page no longer prints ${printed} for ${key}`,
    );
  }
});

test("the stated collection count matches the manifest", () => {
  const n = Object.keys(manifest.collections).length;
  assert.equal(n, 53, "the page says 53 collections in two places");
  assert.ok(html.includes("<dt>53</dt>"));
  assert.ok(html.includes("53 collections"));
});

test("the stated column count matches the manifest", () => {
  const cols = new Set();
  for (const c of Object.values(manifest.collections)) {
    for (const col of c.cols) {
      if (col !== "geometry" && col !== "bbox") cols.add(col);
    }
  }
  assert.equal(cols.size, 297, "the page prints 297 distinct columns");
  assert.ok(html.includes("<dt>297</dt>"));
});

test("the page links the live catalog root, not a local base", () => {
  assert.ok(
    html.includes(
      "https://data.source.coop/portolan-mirrors/us-census-catalog/catalog.json",
    ),
  );
  assert.ok(!/localhost|127\.0\.0\.1/.test(html), "a local URL leaked in");
});

test("the page sends people to the Portolan skills first", () => {
  assert.ok(
    html.includes("portolan-sdi/portolan-skills"),
    "step 1 should install the Portolan skills",
  );
  assert.ok(
    /Read the reading-portolan skill/.test(html),
    "the first prompt should tell the agent to read the reading-portolan skill",
  );
});

test("the question cards carry no mechanism copy", () => {
  // The mechanics belong in the section at the end, so a reader who does not
  // care how it works can read the questions straight through.
  assert.ok(
    !html.includes('class="qwhy"'),
    "a question card still explains the plumbing",
  );
  const cards = html.match(/<p class="qkind">/g) ?? [];
  assert.ok(cards.length >= 6, `expected at least six question cards, got ${cards.length}`);
});

test("the caveats live in the catalog guide, not only on the page", () => {
  // The page claims an agent is warned about these before it writes SQL.
  // That is only true if the guide actually says so.
  const guide = readFileSync(
    new URL("../../catalog/AGENTS.md", import.meta.url), "utf8",
  );
  for (const phrase of ["geo_change", "ecological fallacy", "90% confidence level"]) {
    assert.ok(
      guide.includes(phrase),
      `catalog/AGENTS.md no longer mentions "${phrase}", which about.html promises it does`,
    );
  }
});

test("every runnable snippet is marked for the query gate", () => {
  // tests/test_doc_queries.py runs what is marked. An unmarked SQL block is
  // a query nothing checks.
  const snips = [...html.matchAll(/<div class="snip[^"]*"([^>]*)>\s*<pre>([\s\S]*?)<\/pre>/g)];
  for (const [, attrs, body] of snips) {
    const looksLikeSql = /^(SELECT|WITH|LOAD|INSTALL|SET)\b/m.test(body.trim());
    if (looksLikeSql) {
      assert.ok(
        attrs.includes('data-run="duckdb"'),
        `an SQL snippet is not marked data-run: ${body.trim().slice(0, 60)}`,
      );
    }
  }
  const marked = (html.match(/data-run="duckdb"/g) ?? []).length;
  assert.ok(marked >= 8, `expected at least eight runnable queries, got ${marked}`);
});

test("the cross-catalog examples name catalogs in the registry", () => {
  assert.ok(html.includes("data.source.coop/cholmes/trimet"), "TriMet example missing");
  assert.ok(html.includes("parquetry.geomermaids.com/nfhl"), "FEMA example missing");
  assert.ok(html.includes("portolan-sdi/portolan-registry"), "registry link missing");
});

test("copyLabel covers its states and falls back to idle", () => {
  assert.equal(copyLabel("idle"), "Copy");
  assert.equal(copyLabel("done"), "Copied");
  assert.equal(copyLabel("fail"), "Press ⌘C");
  assert.equal(copyLabel("nonsense"), "Copy");
  assert.equal(copyLabel(undefined), "Copy");
});
