import { test } from "node:test";
import assert from "node:assert/strict";
import { duckdbSnippet, pythonSnippet } from "./snippets.js";

const BASE = "https://data.source.coop/portolan-mirrors/us-census-catalog";

test("single-file collections query over HTTPS", () => {
  const s = duckdbSnippet(
    { data: [{ href: "tracts/tract-income/tract-income.parquet", glob: false }] },
    BASE,
  );
  assert.match(s, /read_parquet\('https:\/\/data\.source\.coop\/portolan-mirrors\/us-census-catalog\/tracts\/tract-income\/tract-income\.parquet'\)/);
  assert.doesNotMatch(s, /s3:/);
});

test("hive globs query the anonymous S3 endpoint", () => {
  const s = duckdbSnippet(
    { data: [{ href: "blocks/state_fips=*/*.parquet", glob: true }] },
    BASE,
  );
  assert.match(s, /s3:\/\/us-west-2\.opendata\.source\.coop/);
  assert.match(s, /hive_partitioning=true/);
  assert.match(s, /s3_region='us-west-2'/);
});

test("no data asset means no snippet", () => {
  assert.equal(duckdbSnippet({ data: [] }, BASE), null);
});

test("python snippet for single files only", () => {
  assert.match(pythonSnippet(
    { data: [{ href: "states/states.parquet", glob: false }] }, BASE),
    /gpd\.read_parquet/);
  assert.equal(pythonSnippet(
    { data: [{ href: "blocks/x=*/*.parquet", glob: true }] }, BASE), null);
});
