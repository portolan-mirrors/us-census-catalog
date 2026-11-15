#!/usr/bin/env python3
"""Post-process the READMEs `portolan readme` generates. Run after it.

Two problems this fixes, both verified against the live pages:

1. The generator writes child links with a doubled group prefix
   (`tracts/README.md` linking `tracts/tract-income/`), and source.coop
   renders every README at a no-trailing-slash URL, so even a correct
   relative link resolves one directory too high (clicking "blocks/" on
   source.coop/portolan-mirrors/us-census-catalog lands on
   /portolan-mirrors/blocks). Every relative link is therefore rewritten
   to an absolute source.coop URL, which also works from GitHub and from
   raw data.source.coop fetches.

2. People land on these READMEs from three places (source.coop, GitHub,
   the data browser) with no way across, so a nav line is injected under
   each title: data browser deep link, GeoParquet download, repo.

The wrong prefixes are filed upstream as portolan-cli#1114; the
no-trailing-slash resolution is source.coop rendering behavior.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"

SC = "https://source.coop/portolan-mirrors/us-census-catalog"
DATA = "https://data.source.coop/portolan-mirrors/us-census-catalog"
GH = "https://github.com/portolan-mirrors/us-census-catalog"
BROWSER = ("https://browser.portolan-sdi.org/?catalog="
           f"{DATA}/catalog.json#/external/"
           "data.source.coop/portolan-mirrors/us-census-catalog")

LINK = re.compile(r"\]\(([^)]+)\)")


def absolutize(text: str, readme_dir_rel: str) -> str:
    """Rewrite every relative markdown link target to a source.coop URL."""
    def fix(m: re.Match) -> str:
        target = m.group(1)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            return m.group(0)
        # normalize against the README's directory
        base = [p for p in readme_dir_rel.split("/") if p]
        parts = base + target.split("/")
        out: list[str] = []
        for part in parts:
            if part in ("", "."):
                continue
            if part == "..":
                if out:
                    out.pop()
                continue
            out.append(part)
        path = "/".join(out).rstrip("/")
        return f"]({SC}/{path})" if path else f"]({SC})"
    return LINK.sub(fix, text)


def nav_line(rel: str, cid: str | None) -> str:
    """The cross-location line injected under the title."""
    if cid is None:  # root or group catalog README
        target = f"{BROWSER}/{rel}/catalog.json" if rel else \
                 f"{BROWSER}/catalog.json"
        return (f"**[🗺️ Open in the data browser]({target})** · "
                f"[Source repository]({GH}) · "
                f"[Agent guide]({SC}{'/' + rel if rel else ''}/AGENTS.md) · "
                f"[STAC root]({DATA}/catalog.json)\n")
    if cid == "blocks":
        parquet = f"{DATA}/{rel}/state_fips=01/01.parquet"
        parquet_label = "Download one state's GeoParquet (AL)"
    elif cid == "crosswalks":
        # 29 separate tables, no single `<cid>.parquet` -- same shape of
        # problem as blocks' per-state partitions, so the nav line points
        # at one representative table instead of a file that does not
        # exist.
        parquet = f"{DATA}/{rel}/t10t20-tract.parquet"
        parquet_label = "Download one table's GeoParquet (t10t20-tract)"
    else:
        # A wide all-indicators table's parquet lives one level above its
        # collection.json (the group restructure kept data URLs stable).
        data_rel = rel if (CATALOG / rel / f"{cid}.parquet").exists() \
            else rel.rsplit("/", 1)[0]
        parquet = f"{DATA}/{data_rel}/{cid}.parquet"
        parquet_label = "Download the GeoParquet"
    return (f"**[🗺️ Open in the data browser]({BROWSER}/{rel}/"
            f"collection.json)** · [{parquet_label}]({parquet}) · "
            f"[Agent guide]({SC}/{rel}/AGENTS.md) · "
            f"[Source repository]({GH})\n")


def inject_nav(text: str, line: str) -> str:
    """Put the nav line after the badges (or the H1 if no badges)."""
    if line.split("·")[0] in text:  # already injected (idempotence)
        return text
    lines = text.split("\n")
    # after the first blank line following the H1/badge block
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            j = i + 1
            while j < len(lines) and lines[j].strip():
                j += 1
            lines.insert(j, "\n" + line.rstrip())
            return "\n".join(lines)
    return line + "\n" + text


def main() -> None:
    for readme in sorted(CATALOG.rglob("README.md")):
        rel = str(readme.parent.relative_to(CATALOG)).replace("\\", "/")
        rel = "" if rel == "." else rel
        text = readme.read_text()

        # The generator writes child links with wrong leading prefixes
        # (`catalog/` on the root README, the group's own directory on a
        # group README — doubled since the wide tables moved into
        # same-named subdirectories). Blind prefix-stripping over-strips
        # the wide child (`counties/counties/` must become `counties/`,
        # not ``), so instead drop leading path segments until the target
        # actually exists relative to the README's own directory.
        def localize(m: re.Match) -> str:
            target = m.group(1)
            if target.startswith(("http://", "https://", "#", "mailto:")):
                return m.group(0)
            if (readme.parent / target.split("#")[0].rstrip("/")).exists():
                return m.group(0)
            parts = target.split("/")
            for i in range(1, len(parts)):
                cand = "/".join(parts[i:])
                p = cand.split("#")[0].rstrip("/")
                if p and (readme.parent / p).exists():
                    return f"]({cand})"
            return m.group(0)
        text = LINK.sub(localize, text)
        text = re.sub(r"### \[(?:[a-z-]+/)+([a-z-]+)\]", r"### [\1]", text)

        cid = None
        if (readme.parent / "collection.json").exists():
            cid = readme.parent.name
        text = absolutize(text, rel)
        text = inject_nav(text, nav_line(rel, cid))
        readme.write_text(text)
        print(f"fixed {readme.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
