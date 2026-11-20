import { test } from "node:test";
import assert from "node:assert/strict";
import { unitFor, fmt, compact, breakLabels, labelFor, fmtBytes } from "./format.js";

test("unitFor infers units from column names", () => {
  assert.equal(unitFor("pct_below_poverty"), "pct");
  assert.equal(unitFor("chg_pct_below_poverty"), "pct");
  assert.equal(unitFor("median_hh_income"), "usd");
  assert.equal(unitFor("median_hh_income_moe"), "usd");
  assert.equal(unitFor("median_home_value"), "usd");
  assert.equal(unitFor("median_gross_rent"), "usd");
  assert.equal(unitFor("median_age"), "years");
  assert.equal(unitFor("population"), "num");
  assert.equal(unitFor("pop_density"), "density");
  assert.equal(unitFor("gini"), "gini");
  assert.equal(unitFor("median_hh_income_cv"), "cv");
});

test("fmt renders values per unit, em-dash for null", () => {
  assert.equal(fmt(null), "—");
  assert.equal(fmt(12.34, "pct"), "12.3%");
  assert.equal(fmt(56160, "usd"), "$56,160");
  assert.equal(fmt(38.5, "years"), "38.5 yrs");
  assert.equal(fmt(0.42, "gini"), "0.42");
  assert.equal(fmt(1234567), "1,234,567");
  assert.equal(fmt("identical"), "identical");
});

test("compact renders break-point labels", () => {
  assert.equal(compact(40000, "usd"), "$40k");
  assert.equal(compact(1500000), "1.5M");
  assert.equal(compact(-6, "pct"), "−6%");
  assert.equal(compact(0.9, "pct"), "0.9%");
});

test("breakLabels covers N+1 classes", () => {
  const labels = breakLabels([40000, 55000], "usd");
  assert.deepEqual(labels, ["< $40k", "$40k – $55k", "≥ $55k"]);
});

test("labelFor prettifies column names", () => {
  assert.equal(labelFor("median_hh_income"), "Median household income");
  assert.equal(labelFor("geoid"), "GEOID");
  assert.equal(labelFor("pct_below_poverty"), "% below poverty");
});

test("fmtBytes", () => {
  assert.equal(fmtBytes(323229152), "323 MB");
  assert.equal(fmtBytes(7067134582), "7.1 GB");
  assert.equal(fmtBytes(2126), "2 KB");
});
