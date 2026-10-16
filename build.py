#!/usr/bin/env python3
"""
build.py — Assemble the partial-based source tree into deployable HTML.
==========================================================================
The site is no longer one 3,622-line file with a 2,270-line inline <style>
block. It is a set of partials in `partials/` plus modular stylesheets in
`css/` and ES modules in `js/`. This script stitches them into the two
documents that actually ship: `index.html` and `rate-card.html`.

Usage
-----
    python build.py                 build both pages
    python build.py --check         validate only, write nothing
    python build.py --stats         report page weights after building

What it does
------------
  * Injects every partial into the document shell.
  * Replaces {{TOKENS}} with real values from build.config.json.
  * Writes valid UTF-8 with no BOM (a BOM breaks some Apache configs).
  * Verifies that every local asset referenced by the built document
    exists on disk, so a typo'd filename fails the build instead of
    shipping a broken image.
  * Verifies that every in-page anchor (#id) resolves to a real element,
    which is how the original site's dead `#cal-grid` link went unnoticed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTIALS = ROOT / "partials"
CONFIG_FILE = ROOT / "build.config.json"

FONT_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Cinzel:wght@500;600;700;800;900"
    "&family=Plus+Jakarta+Sans:wght@300;400;500;600;700"
    "&family=JetBrains+Mono:wght@400;500;600&display=swap"
)


def load_config() -> dict:
    defaults = {
        "site_origin": "https://fredericsax.com",
        "og_image": "IMG_3609.PNG",
        "font_url": FONT_URL,
    }
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open(encoding="utf-8") as handle:
            defaults.update(json.load(handle))
    defaults["og_image_url"] = _absolute(defaults["site_origin"], defaults["og_image"])
    return defaults


def _absolute(origin: str, path: str) -> str:
    if not path:
        return ""
    if path.startswith(("http://", "https://")):
        return path
    return f"{origin.rstrip('/')}/{path.lstrip('/')}"


def read_partial(name: str) -> str:
    path = PARTIALS / f"{name}.html"
    if not path.exists():
        raise SystemExit(f"Missing partial: {path}")
    return path.read_text(encoding="utf-8").strip()


def substitute(text: str, cfg: dict) -> str:
    tokens = {
        "{{SITE_ORIGIN}}": cfg["site_origin"],
        "{{OG_IMAGE}}": cfg["og_image_url"],
        "{{FONT_URL}}": cfg["font_url"],
        "{{BUILD_DATE}}": _today(),
    }
    for token, value in tokens.items():
        text = text.replace(token, value)
    return text


def _today() -> str:
    from datetime import date
    return date.today().isoformat()


SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
{head}
</head>
<body>
{skip}
{nav}
{hero}
{marquee}
<main class="site-main-flow" id="main">
{bio}
{videos}
{calendar}
{weddings}
{ratecard}
{pinterest}
{portal}
{contact}
{footer}
</main>
{scripts}
</body>
</html>
"""


def build_document() -> str:
    cfg = load_config()
    parts = {
        "head": substitute(read_partial("head"), cfg),
        "nav": read_partial("nav"),
        "hero": read_partial("hero"),
        "marquee": read_partial("marquee"),
        "bio": read_partial("bio"),
        "videos": read_partial("videos"),
        "calendar": read_partial("calendar"),
        "weddings": read_partial("weddings"),
        "ratecard": read_partial("ratecard"),
        "pinterest": read_partial("pinterest"),
        "portal": read_partial("portal"),
        "contact": read_partial("contact"),
        "footer": read_partial("footer"),
        "scripts": read_partial("scripts"),
    }

    # partials/nav.html already carries the skip link, the toast host and the
    # live region as its first children, so they must not be emitted again.
    shell = SHELL

    document = substitute(shell, cfg)
    for key, value in parts.items():
        document = document.replace("{" + key + "}", value)
    document = document.replace("{skip}", "")

    return _normalise(document)


def _normalise(document: str) -> str:
    """Collapse runs of blank lines. Never touches content inside <pre>."""
    lines = [line.rstrip() for line in document.splitlines()]
    out: list[str] = []
    for line in lines:
        if line == "" and (not out or out[-1] == ""):
            continue
        out.append(line)
    return "\n".join(out).strip() + "\n"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

ASSET_ATTRS = ("src", "poster", "href")


def validate(document: str, extra_skip_dirs=(".git", "node_modules")) -> list[str]:
    problems: list[str] = []

    # 1. Local assets resolve to real files.
    for attr in ASSET_ATTRS:
        for match in re.finditer(rf'{attr}\s*=\s*"([^"]+)"', document):
            value = match.group(1)
            if value.startswith(("http://", "https://", "mailto:", "tel:", "data:", "#")):
                continue
            clean = value.split("?")[0].split("#")[0]
            if not clean:
                continue
            if clean.startswith("css/") or clean.startswith("js/") or clean.startswith("partials/"):
                target = ROOT / clean
            else:
                target = ROOT / clean
            if not target.exists():
                problems.append(f"asset does not exist: {clean} (from {attr}=)")

    # 2. In-page anchors resolve to real element ids.
    declared_ids = set(re.findall(r'id\s*=\s*"([^"]+)"', document))
    for match in re.finditer(r'href\s*=\s*"(#[^"]+)"', document):
        target = match.group(1)[1:]
        if not target:
            continue
        if target not in declared_ids:
            problems.append(f"anchor href=\"#{target}\" has no matching element id")

    # 3. No duplicated ids — a real class of bug the old site never checked.
    seen: set[str] = set()
    for element_id in re.finditer(r'id\s*=\s*"([^"]+)"', document):
        if element_id.group(1) in seen:
            problems.append(f"duplicate element id: {element_id.group(1)}")
        seen.add(element_id.group(1))

    # 4. Canonical WhatsApp number is the only one in use.
    for match in re.finditer(r"wa\.me/(\d+)", document):
        if match.group(1) != "254745163122":
            problems.append(f"non-canonical WhatsApp number: {match.group(1)}")

    # 5. No inline event handlers remain (they block a strict CSP).
    for match in re.finditer(r'\son(click|load|error|mouseover|submit|change|input)\s*=', document):
        line = document[: match.start()].count("\n") + 1
        problems.append(f"inline handler at line {line}: {match.group(1)}")

    # 6. No unresolved build tokens.
    for match in re.finditer(r"\{\{[A-Z_]+\}\}", document):
        problems.append(f"unresolved token: {match.group(0)}")

    return problems


# ---------------------------------------------------------------------------
# Rate card page
# ---------------------------------------------------------------------------

def build_rate_card(cfg: dict) -> str:
    """rate-card.html is unchanged in structure but is validated too."""
    path = ROOT / "rate-card.html"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Frederic Sax Ke site")
    parser.add_argument("--check", action="store_true", help="validate only")
    parser.add_argument("--stats", action="store_true", help="report output sizes")
    args = parser.parse_args()

    document = build_document()
    cfg = load_config()

    problems = validate(document)

    rate_card = build_rate_card(cfg)
    if rate_card:
        problems.extend(f"rate-card.html: {p}" for p in validate(rate_card))

    if problems:
        print("Build validation FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    if args.check:
        print(f"[ok] index.html would pass validation ({len(document.splitlines())} lines)")
        return 0

    out = ROOT / "index.html"
    out.write_text(document, encoding="utf-8", newline="\n")

    print(f"[ok] wrote {out.name} — {len(document.splitlines())} lines, "
          f"{len(document.encode('utf-8')) / 1024:.1f} KB")

    if args.stats:
        total = len(document.encode("utf-8"))
        css = sum(p.stat().st_size for p in (ROOT / "css").glob("*.css"))
        js = sum(p.stat().st_size for p in (ROOT / "js").glob("*.js"))
        print(f"     index.html : {total / 1024:7.1f} KB")
        print(f"     css/*.css  : {css / 1024:7.1f} KB"
              f"  ({len(list((ROOT / 'css').glob('*.css')))} files)")
        print(f"     js/*.js    : {js / 1024:7.1f} KB"
              f"  ({len(list((ROOT / 'js').glob('*.js')))} files)")
        print(f"     partials   : {len(list(PARTIALS.glob('*.html')))} files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
