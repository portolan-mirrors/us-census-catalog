// Copyable query snippets for a collection. Pure; tested by snippets.test.mjs.

/**
 * DuckDB snippet for a collection's GeoParquet.
 * Hive-partitioned globs need the anonymous S3 endpoint: the HTTPS gateway
 * has no listing, so a glob over data.source.coop returns 404.
 */
export function duckdbSnippet(entry, base) {
  const d = entry.data?.[0];
  if (!d) return null;
  if (d.glob) {
    const s3 = "s3://us-west-2.opendata.source.coop/portolan-mirrors/us-census-catalog/" + d.href;
    return [
      "INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;",
      "SET s3_region='us-west-2';",
      `SELECT * FROM read_parquet('${s3}', hive_partitioning=true) LIMIT 10;`,
    ].join("\n");
  }
  return [
    "INSTALL spatial; LOAD spatial;",
    `SELECT * FROM read_parquet('${base}/${d.href}') LIMIT 10;`,
  ].join("\n");
}

/** Python snippet using GeoPandas. */
export function pythonSnippet(entry, base) {
  const d = entry.data?.[0];
  if (!d || d.glob) return null;
  return [
    "import geopandas as gpd",
    `gdf = gpd.read_parquet("${base}/${d.href}")`,
  ].join("\n");
}
