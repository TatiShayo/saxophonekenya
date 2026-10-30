#!/usr/bin/env python3
"""
extract_emails.py — Turn the outreach pack into ready-to-send drafts
==========================================================================
The outreach pack is a markdown document. That is the right format for
reading and reviewing, but the wrong format for actually sending: every
email has `**bold**` markers, `&bull;` entities, `&mdash;` entities and
`---` separators that have to be stripped by hand before it can go into a
mail client.

This script parses Section 6 of Hotel-Outreach-Pack.md and writes one
plain-text file per send into `emails-outbox/`:

    01-villa-rosa-kempinski.txt
    02-fairmont-kenya.txt
    ...

Each file contains exactly what you paste into the message body:
    Line 1: the subject line
    Line 2: blank
    Line 3+: the email body

Markdown emphasis is removed, HTML entities are decoded to real Unicode
characters (the same bytes the hotel will receive either way), and the
`---` separators and `####` headings are dropped.

Usage:
    python extract_emails.py
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACK = ROOT / "docs" / "Hotel-Outreach-Pack.md"
if not PACK.exists():
    PACK = ROOT / "Hotel-Outreach-Pack.md"
OUT_DIR = ROOT / "emails-outbox"

BOLD = re.compile(r"\*\*(.+?)\*\*")
ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
CODE = re.compile(r"`([^`]+)`")
BACKTICK_ARROW = re.compile(r"&rarr;")
HEADING_DIVIDER = re.compile(r"^\s*-{3,}\s*$")

def clean_inline(text: str) -> str:
    """Strip markdown emphasis and decode HTML entities."""
    text = CODE.sub(r"\1", text)
    text = BOLD.sub(r"\1", text)
    text = ITALIC.sub(r"\1", text)
    # Entities that survive into the body should render as real characters.
    text = html.unescape(text)
    text = BACKTICK_ARROW.sub("->", text)
    return text

def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return name.strip("-")[:60]

def main() -> int:
    if not PACK.exists():
        print(f"Could not find the outreach pack at {PACK}")
        return 1

    raw = PACK.read_text(encoding="utf-8")

    # Isolate Section 6.
    section = re.search(
        r"^## 6\..*?(?=^## 7\.)",
        raw,
        re.MULTILINE | re.DOTALL,
    )
    if not section:
        print("Could not find Section 6 in the pack.")
        return 1

    body = section.group(0)

    # Split on each SEND block.
    blocks = re.split(r"(?m)^#### SEND (\d+) of 29", body)
    # blocks[0] is the section preamble, then alternating (number, content).
    pairs = list(zip(blocks[1::2], blocks[2::2]))

    if not pairs:
        print("No SEND blocks found.")
        return 1

    OUT_DIR.mkdir(exist_ok=True)

    written = 0
    index_rows = []

    for number, content in pairs:
        # Subject line
        subject = re.search(r"\*\*Subject:\*\*\s*(.+)", content)
        if not subject:
            print(f"  SEND {number}: no subject line, skipped")
            continue
        subject_text = clean_inline(subject.group(1).strip())

        # Recipient (for the filename and the index)
        to = re.search(r"\*\*To:\*\*\s*`([^`]+)`", content)
        recipient = to.group(1) if to else "unknown"

        # Property name. The split consumed "#### SEND N of 29", so the
        # remainder of that heading is the first line of `content`.
        first_line = content.lstrip().splitlines()[0] if content.strip() else ""
        property_name = clean_inline(re.sub(r"^[^A-Za-z0-9]+\s*", "", first_line))
        property_name = clean_inline(title.group(1).strip()) if title else f"Send {number}"

        # Body: everything after the subject line, minus trailing divider
        body_text = content[subject.end():]
        body_text = HEADING_DIVIDER.sub("", body_text).strip()

        lines = [clean_inline(line) for line in body_text.splitlines()]
        # Collapse runs of blank lines introduced by divider removal.
        cleaned: list[str] = []
        for line in lines:
            if line.strip() == "" and (not cleaned or cleaned[-1].strip() == ""):
                continue
            cleaned.append(line)
        while cleaned and cleaned[-1].strip() == "":
            cleaned.pop()

        filename = f"{int(number):02d}-{slugify(property_name)}.txt"
        draft = f"Subject: {subject_text}\nTo: {recipient}\n\n" + "\n".join(cleaned) + "\n"

        (OUT_DIR / filename).write_text(draft, encoding="utf-8")
        index_rows.append((int(number), property_name, recipient, filename))
        written += 1

    # Write an index so the outbox is navigable.
    index = [
        "HOTEL & RESORT OUTREACH - SEND INDEX",
        "=" * 74,
        "",
        "One plain-text draft per file. Paste the body into your mail client.",
        "The Subject: and To: lines are there for reference - do not send them.",
        "",
        f"{'#':>3}  {'PROPERTY':<46}  {'RECIPIENT':<44}",
        "-" * 74,
    ]
    for number, prop, to, fname in index_rows:
        index.append(f"{number:>3}  {prop[:45]:<46}  {to[:43]:<44}")
        index.append(f"     -> {fname}")
    index += [
        "",
        "-" * 74,
        f"{len(index_rows)} drafts ready in emails-outbox/",
        "",
        "Before sending, read Section 4 (Deliverability Rules) and Section 9",
        "(Legal & Compliance) of the outreach pack.",
        "",
    ]
    (OUT_DIR / "_INDEX.txt").write_text("\n".join(index), encoding="utf-8")

    print(f"Wrote {written} drafts to {OUT_DIR}/")
    print(f"Wrote index to {OUT_DIR}/_INDEX.txt")

    sizes = sorted(p.stat().st_size for p in OUT_DIR.glob("*.txt"))
    print(f"Average draft: {sum(sizes)/len(sizes)/1024:.1f} KB")

    return 0

if __name__ == "__main__":
    sys.exit(main())
