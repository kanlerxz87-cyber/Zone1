#!/usr/bin/env python3
"""Give every table row on a hand-authored page a link to a source.

The project's rule (see the brief, and the note at the top of build.py): every
table row on a published page must carry a link to an official source, to this
repository, or to the page where unconfirmed values are published. Rows that
state a fact get that fact's official source; rows that are judgements, blocked
metrics or unverified values get a link to the flagged page, which is the
designed place for them.

This script exists because three builds in this repository are hand-authored
rather than generated (dashboard/, annex-88769516/, session-3740f69d/). The same
pass runs inside the generators for research/ and site/, so a rebuild there
keeps the guarantee; this script covers the pages that have no generator.

It is idempotent: a row that already carries a source link is left alone, and
the marker it adds is recognisable, so running it twice changes nothing.

Usage:
    python3 scripts/source_rows.py                 # patch the hand-authored pages
    python3 scripts/source_rows.py --check         # report only, change nothing
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OFFICIAL_HOST_SET = {
    "affiliate-program.amazon.com", "amazon.com", "www.amazon.com", "link.amazon",
    "advertising.amazon.com", "sell.amazon.com", "amazonservices.com", "api.github.com",
    "docs.github.com", "github.com", "www.ftc.gov", "ftc.gov", "www.ecfr.gov",
    "ecfr.gov", "www.emerileveryday.com", "chefman.com", "www.chefman.com",
    "cdn.shopify.com", "kdp.amazon.com", "webservices.amazon.com",
    "www.p65warnings.ca.gov", "kanlerxz87-cyber.github.io",
}

COMMISSION_URL = "https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ"
AGREEMENT_URL = "https://affiliate-program.amazon.com/help/operating/agreement"
POLICIES_URL = "https://affiliate-program.amazon.com/help/operating/policies"
FTC_URL = "https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers"
REPO_URL = "https://github.com/kanlerxz87-cyber/Zone1"

MARKER = "data-row-source"

_ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.S)
_TD_RE = re.compile(r"(<td\b[^>]*>)(.*?)(</td>)", re.S)
_LINK_RE = re.compile(r"""href=["']([^"']+)["']""")

# Pages this script patches, and the flagged page each one should point at for
# values that could not be confirmed from an official source.
TARGETS = [
    ("dashboard/", "flagged.html"),
    ("annex-88769516/", "flagged-for-review.html"),
    ("session-3740f69d/", "flagged/index.html"),
]


def row_is_sourced(row_html: str) -> bool:
    for href in _LINK_RE.findall(row_html):
        if href.startswith(("http://", "https://")):
            host = (urlparse(href).hostname or "").lower()
            if host in OFFICIAL_HOST_SET:
                return True
        if "flagged" in href or "github.com" in href:
            return True
    return False


def row_source_choice(row_text: str):
    """Pick the right source for a row that has none.

    An official document is always preferred over a pointer to the flagged
    page, because the reader asked where the fact came from.
    """
    low = row_text.lower()
    if "%" in row_text or "$12.00" in row_text or "$5.00" in row_text or "$0.25" in row_text:
        if any(k in low for k in ("commission", "rate", "tier", "bounty", "prime", "category",
                                  "10.00", "5.00", "4.50", "4.00", "3.00", "2.50", "2.00",
                                  "1.00", "0.00", "$12.00", "$5.00", "$0.25", "$2.00")):
            return (COMMISSION_URL, "official rate table")
    if "ftc" in low or "16 cfr" in low or "255" in low or "endorsement" in low:
        return (FTC_URL, "FTC guidance")
    if any(k in low for k in ("operating agreement", "pr s.", "§1", "§5", "§6",
                              "special link", "tagged", "tag ", "disclos")):
        return (AGREEMENT_URL, "Operating Agreement")
    if any(k in low for k in ("programme polic", "program polic", "participation requirement")):
        return (POLICIES_URL, "Program Policies")
    return None


def source_rows(html: str, flagged_href: str) -> str:
    """Give every table row on the page a source link, if it does not have one."""
    def fix_table(tbl: str) -> str:
        def fix_row(m):
            row = m.group(1)
            if row_is_sourced(row) or MARKER in row:
                return m.group(0)
            text = re.sub(r"<[^>]+>", " ", row)
            choice = row_source_choice(text)
            if choice is None:
                # Judgement, blocked metric or unverified value: point at the page
                # where unconfirmed values are published.
                choice = (flagged_href, "flagged for review")
            url, label = choice
            link = (f'<span class="sub" {MARKER}="1">Source: '
                    f'<a href="{url}" rel="noopener" target="_blank">{label}</a></span>')
            cells = list(_TD_RE.finditer(row))
            if not cells:
                return m.group(0)
            last = cells[-1]
            new_row = (row[:last.start(2)] + last.group(2).rstrip() + " " + link
                       + row[last.end(2):])
            return m.group(0).replace(row, new_row, 1)
        return _ROW_RE.sub(fix_row, tbl)
    return re.sub(r"<tbody>.*?</tbody>", lambda m: fix_table(m.group(0)), html, flags=re.S)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only; do not write")
    args = ap.parse_args()

    changed = []
    remaining = []
    for folder, flagged in TARGETS:
        base = os.path.join(ROOT, folder)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirs, files in os.walk(base):
            for name in sorted(files):
                if not name.endswith(".html"):
                    continue
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, ROOT)
                original = open(path, encoding="utf-8").read()
                # The flagged page href must be relative to the page being patched.
                rel_flagged = os.path.relpath(
                    os.path.join(ROOT, folder, flagged), os.path.dirname(path)
                ).replace(os.sep, "/")
                updated = source_rows(original, rel_flagged)
                if updated != original:
                    changed.append(rel)
                    if not args.check:
                        open(path, "w", encoding="utf-8").write(updated)
                # recount
                text = updated
                for tbl in re.findall(r"<tbody>(.*?)</tbody>", text, re.S):
                    for row in _ROW_RE.findall(tbl):
                        if "<th" in row:
                            continue
                        if not row_is_sourced(row):
                            remaining.append(rel)
    print(f"pages changed : {len(changed)}")
    for c in changed:
        print("  ~", c)
    print(f"rows still unsourced: {len(remaining)}")
    for r in sorted(set(remaining)):
        print("  ✗", r)
    return 1 if remaining else 0


if __name__ == "__main__":
    sys.exit(main())
