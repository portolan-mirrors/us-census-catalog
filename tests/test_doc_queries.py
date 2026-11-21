#!/usr/bin/env python3
"""Every query printed in the documentation still runs against the catalog.

The guides and the explainer page teach people to paste a query and get an
answer. A column that gets renamed, a file that moves or a collection that is
rewritten turns one of those into a confident failure in somebody else's
terminal. This gate runs them.

Sources:
  - catalog/**/AGENTS.md   -- every ```sql fence
  - apps/explorer/about.html -- every snippet marked data-run="duckdb"

The queries read the published files over HTTPS, so this gate needs the
network and the published catalog. It is slower than the other gates and it
runs in its own workflow, not in the fast CI job.

Run:   python3 tests/test_doc_queries.py
       python3 tests/test_doc_queries.py --only tracts     # paths matching
       python3 tests/test_doc_queries.py --workers 4
       python3 tests/test_doc_queries.py --list
"""
import argparse
import importlib.util
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "tools"))
from collection_meta import PUBLIC_BASE  # noqa: E402

# Some guides say "run from this directory" and name a file beside them. That
# is true for a reader with the bytes on disk, and the same file is published
# at the collection's own URL. Resolving the name against that URL keeps the
# guide honest as written and proves the published file is really there.
# A structural rule, so no document needs an entry on an exclusion list.
# A quoted path with no scheme: 'tract.parquet' or 'urban-areas/x.parquet'.
BARE_PARQUET = re.compile(r"'(?!\w+://)([A-Za-z0-9][A-Za-z0-9._/-]*\.parquet)'")

SQL_FENCE = re.compile(r"```sql\n(.*?)```", re.S)
# A snippet div that opts in, then its <pre> body.
HTML_SNIPPET = re.compile(
    r'<div class="snip[^"]*"[^>]*data-run="duckdb"[^>]*>\s*<pre>(.*?)</pre>', re.S)
HTML_PYTHON = re.compile(
    r'<div class="snip[^"]*"[^>]*data-run="python"[^>]*>\s*<pre>(.*?)</pre>', re.S)

HTML_ENTITIES = {
    "&lt;": "<", "&gt;": ">", "&amp;": "&", "&quot;": '"', "&#39;": "'",
    "&mdash;": "—", "&ndash;": "–", "&nbsp;": " ",
}


def unescape(text: str) -> str:
    for entity, char in HTML_ENTITIES.items():
        text = text.replace(entity, char)
    return text


def line_of(haystack: str, index: int) -> int:
    return haystack.count("\n", 0, index) + 1


def resolve(sql: str, doc: str) -> str:
    """Point a bare file name at the published file beside its guide."""
    directory = str(Path(doc).parent)
    if not directory.startswith("catalog"):
        return sql
    rel = directory[len("catalog"):].strip("/")
    base = f"{PUBLIC_BASE}/{rel}" if rel else PUBLIC_BASE
    return BARE_PARQUET.sub(lambda m: f"'{base}/{m.group(1)}'", sql)


def collect() -> list[dict]:
    """Every documented query, with where it came from."""
    found = []

    for path in sorted(ROOT.glob("catalog/**/AGENTS.md")):
        text = path.read_text()
        rel = str(path.relative_to(ROOT))
        for match in SQL_FENCE.finditer(text):
            found.append({
                "doc": rel,
                "line": line_of(text, match.start()),
                "lang": "duckdb",
                "sql": resolve(match.group(1).strip(), rel),
            })

    page = ROOT / "apps/explorer/about.html"
    if page.exists():
        text = page.read_text()
        rel = str(page.relative_to(ROOT))
        for lang, pattern in (("duckdb", HTML_SNIPPET), ("python", HTML_PYTHON)):
            for match in pattern.finditer(text):
                found.append({
                    "doc": rel,
                    "line": line_of(text, match.start()),
                    "lang": lang,
                    "sql": unescape(match.group(1)).strip(),
                })
    return found


def run_sql(sql: str) -> None:
    import duckdb

    con = duckdb.connect()
    try:
        con.execute("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs;")
        con.execute(sql).fetchall()
    finally:
        con.close()


def run_python(source: str) -> None:
    """Execute a documented Python snippet in its own namespace."""
    exec(compile(source, "<doc snippet>", "exec"), {"__name__": "__doc__"})


def run_one(item: dict, lock: threading.Lock) -> dict:
    started = time.monotonic()
    try:
        if item["lang"] == "python":
            run_python(item["sql"])
        else:
            run_sql(item["sql"])
        item["ok"] = True
        item["error"] = None
    except Exception as exc:  # noqa: BLE001 - any failure is a failing doc
        item["ok"] = False
        item["error"] = f"{type(exc).__name__}: {exc}".strip().split("\n")[0][:300]
    item["seconds"] = round(time.monotonic() - started, 1)

    with lock:
        mark = "ok  " if item["ok"] else "FAIL"
        print(f"  {mark} {item['doc']}:{item['line']}  {item['seconds']}s",
              flush=True)
        if not item["ok"]:
            print(f"       {item['error']}", flush=True)
    return item


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="",
                        help="run queries whose doc path contains this text")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--list", action="store_true",
                        help="print what would run and exit")
    args = parser.parse_args()

    items = collect()
    if args.only:
        items = [i for i in items if args.only in i["doc"]]

    runnable = items

    if args.list:
        for item in runnable:
            print(f"{item['lang']:7s} {item['doc']}:{item['line']}")
        langs = {}
        for item in runnable:
            langs[item["lang"]] = langs.get(item["lang"], 0) + 1
        print(f"\n{len(runnable)} snippet(s): " +
              ", ".join(f"{n} {lang}" for lang, n in sorted(langs.items())))
        return 0

    if not runnable:
        print("no documented queries found; the extractors are out of date")
        return 1

    # pyflakes does not honour noqa, so probe the module without importing.
    if importlib.util.find_spec("duckdb") is None:
        print("duckdb is not installed: python -m pip install duckdb")
        return 1
    if (any(i["lang"] == "python" for i in runnable)
            and importlib.util.find_spec("geopandas") is None):
        print("geopandas is not installed: python -m pip install geopandas")
        return 1

    docs = len({i["doc"] for i in runnable})
    print(f"running {len(runnable)} documented query(s) from {docs} file(s) "
          f"with {args.workers} worker(s)")
    started = time.monotonic()
    lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda i: run_one(i, lock), runnable))
    elapsed = round(time.monotonic() - started, 1)

    failures = [r for r in results if not r["ok"]]

    if failures:
        print(f"\nFAILED: {len(failures)} of {len(results)} documented "
              f"query(s) no longer run")
        for item in failures:
            print(f"  {item['doc']}:{item['line']}")
            print(f"    {item['error']}")
            first = item["sql"].split("\n")[0][:100]
            print(f"    starts: {first}")
        return 1

    slowest = max(results, key=lambda r: r["seconds"])
    print(f"\nOK: {len(results)} documented query(s) run, {elapsed}s total, "
          f"slowest {slowest['seconds']}s ({slowest['doc']}:{slowest['line']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
