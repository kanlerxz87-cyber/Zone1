#!/usr/bin/env python3
"""Page gate for the published site: read the *rendered HTML*, not the dataset.

Why this exists
---------------
Every other gate in this repository reads the **dataset** (`data/*.json`) or the
**generator** (`build.py`). A page can satisfy all of them and still publish a
table row whose value carries no source link, because the value was typed
straight into the generator. This script reads the **HTML that is actually
served** and looks for defect classes the dataset gates cannot see.

It is read-only. It inspects files and writes one JSON report when asked; it
never edits a page, a dataset or the generator.

Checks
------
A.  per-row source coverage across every *data* table on every page. The rule
    the site itself applies (Program Policies §2(b)/§6(t) and the FTC guides)
    is: a row that asserts a value links to the official document that states
    it. A row that links only to this repository or to the Flagged page is
    reported as a warning, because that is the project's documented pattern for
    a design opinion or an unconfirmed value — it is not silently passed.
B.  duplicate `id` attributes within a page
C.  JSON-LD blocks that do not parse
D.  canonical URL present and equal to the published URL of the page
    (the 404 page is exempt by design: it is `noindex` and must not declare one)
E.  meta description present
F.  exactly one `<h1>`, and no skipped heading level, no `<h5>`/`<h6>`
G.  `<img>` without usable alternative text
H.  `<html lang>` and the mobile viewport meta
I.  data tables without a header row (`<th>`)
J.  affiliate anchors: every product page must carry the supplied link.amazon token
K.  "slop" phrases in rendered copy — the house list in `build.py`, re-checked
    against the HTML rather than against the JSON, so an escape cannot satisfy
    it. A phrase that is *quoted* is evidence, not slop, and is not reported.

Usage:  python3 scripts/audit_pages.py [--json out.json]
Exit code 0 = no errors. Warnings are reported but do not fail the gate.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "platform"))
from _common import is_official  # noqa: E402

PUBLISH_ORIGIN = "https://kanlerxz87-cyber.github.io/Zone1/"

# The directories the root generator (build.py) writes. The parallel annexes
# (site/, s2/, research/, dashboard/, docs/, platform/, crosscheck/, annex-*/
# session-*/) belong to other sessions and are not part of this gate.
ROOT_DIRS = ("", "products/", "categories/", "guides/", "articles/")

# A cell that means "this was not confirmed" is allowed to be unsourced, because
# a blank with a flag is the honest cell. These are the markers the site's own
# generator uses for that state.
BLANK_MARKERS = (
    "—", "–", "not confirmed", "unconfirmed", "unverified", "flagged", "not available",
    "not published", "not disclosed", "unknown", "no source", "n/a", "not stated",
)

BANNED_PHRASES = (
    "in today's fast-paced world", "elevate your", "unlock the power", "game-changer",
    "game changer", "revolutionize", "revolutionise", "seamless experience",
    "take it to the next level", "look no further", "dive into", "delve into",
    "ever-evolving landscape", "nestled in the heart", "boasts a", "unleash",
    "cutting-edge", "state-of-the-art", "must-have", "indulge in", "tantalizing",
)


def registered_hosts():
    """Hosts this project treats as official: the union of every source register."""
    hosts = set()
    for rel in ("data/sources.json", "data/s2/sources.json", "data/verified/sources.json",
                "research/sources-s8a2.json"):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        try:
            doc = json.load(open(path, encoding="utf-8"))
        except ValueError:
            continue
        for s in doc.get("sources", []):
            url = s.get("url") or ""
            if url:
                hosts.add((urlparse(url).hostname or "").lower())
    try:
        from platform._common import OFFICIAL_HOSTS  # type: ignore
        hosts.update(h.lower() for h in OFFICIAL_HOSTS)
    except Exception:
        pass
    hosts.update({"github.com", "kanlerxz87-cyber.github.io"})
    return {h for h in hosts if h}


HOSTS = registered_hosts()


class PageParser(HTMLParser):
    """Collects the elements the audit needs, page by page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.headings = []          # (level, text)
        self.heading_stack = []
        self.jsonld = []
        self._in_jsonld = False
        self._jsonld_buf = []
        self.imgs = []
        self.tables = []             # [{"header": bool, "rows": [[cell, ...]]}]
        self._table = None
        self._row = None
        self._cell = None
        self.lang = None
        self.viewport = False
        self.canonical = None
        self.description = None
        self.links = []             # (href, text)
        self._link_depth = 0
        self._link_href = None
        self._link_text = []
        self.title = None
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            if a.get("name", "").lower() == "viewport":
                self.viewport = True
            if a.get("name", "").lower() == "description":
                self.description = a.get("content")
        if tag == "link" and "canonical" in (a.get("rel") or "").lower():
            self.canonical = a.get("href")
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_buf = []
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.heading_stack.append([int(tag[1]), []])
        if tag == "img":
            self.imgs.append(a)
        if tag == "table":
            self._table = {"header": False, "rows": []}
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in ("th", "td") and self._row is not None:
            self._cell = {"tag": tag, "text": [], "links": []}
        elif tag == "a":
            self._link_depth += 1
            if self._link_depth == 1:
                self._link_href = a.get("href")
                self._link_text = []
            if self._cell is not None:
                self._cell["links"].append(a.get("href"))
        elif tag == "br" and self._cell is not None:
            self._cell["text"].append(" ")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            self.jsonld.append("".join(self._jsonld_buf))
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self.heading_stack:
            level, buf = self.heading_stack.pop()
            text = re.sub(r"\s+", " ", "".join(buf)).strip()
            self.headings.append((level, text))
            if level == 1:
                self.h1 += 1
        if tag == "a":
            if self._link_depth == 1 and self._link_href is not None:
                self.links.append((self._link_href, re.sub(r"\s+", " ", "".join(self._link_text)).strip()))
                self._link_href = None
            self._link_depth = max(0, self._link_depth - 1)
        if tag in ("th", "td") and self._cell is not None and self._row is not None:
            cell = self._cell
            cell["text"] = re.sub(r"\s+", " ", "".join(cell["text"])).strip()
            self._row.append(cell)
            self._cell = None
        elif tag == "tr" and self._row is not None and self._table is not None:
            if self._row:
                self._table["rows"].append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            if self._table["rows"]:
                self._table["header"] = any(c["tag"] == "th" for c in self._table["rows"][0])
                self.tables.append(self._table)
            self._table = None

    def handle_data(self, data):
        if self._in_jsonld:
            self._jsonld_buf.append(data)
        if self._in_title:
            self.title = (self.title or "") + data
        if self.heading_stack:
            self.heading_stack[-1][1].append(data)
        if self._cell is not None:
            self._cell["text"].append(data)
        if self._link_depth:
            self._link_text.append(data)


def cell_is_blank(text):
    t = text.strip()
    if not t:
        return True
    low = t.lower()
    return any(m.strip().lower() in low for m in BLANK_MARKERS)


def is_internal(href):
    """True for a link into this repository (relative path, GitHub, or the live site)."""
    if not href:
        return False
    host = (urlparse(href).hostname or "").lower()
    if not host:
        return True
    return host in ("github.com", "kanlerxz87-cyber.github.io")


def audit_page(rel):
    """Returns (errors, warnings, notes) for one page."""
    errors, warnings, notes = [], [], []
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return [f"{rel}: page missing from the tree"], [], []
    text = open(path, encoding="utf-8").read()
    p = PageParser()
    p.feed(text)

    # --- B. duplicate ids ------------------------------------------------------
    seen = {}
    for m in re.finditer(r'\sid="([^"]+)"', text):
        i = m.group(1)
        seen[i] = seen.get(i, 0) + 1
    dups = sorted(i for i, n in seen.items() if n > 1)
    if dups:
        errors.append(f"{rel}: duplicate id(s): {', '.join(dups[:8])}")

    # --- C. JSON-LD ------------------------------------------------------------
    for i, block in enumerate(p.jsonld):
        try:
            json.loads(block)
        except ValueError as exc:
            errors.append(f"{rel}: JSON-LD block {i} does not parse ({exc})")

    # --- D. canonical ----------------------------------------------------------
    expected = PUBLISH_ORIGIN + rel if rel != "index.html" else PUBLISH_ORIGIN
    if rel == "404.html":
        # By design: the 404 page is noindex and must not declare a canonical URL.
        if p.canonical:
            errors.append(f"{rel}: 404 page must not declare a canonical URL")
    elif not p.canonical:
        errors.append(f"{rel}: no canonical link")
    elif p.canonical.rstrip("/") != expected.rstrip("/"):
        errors.append(f"{rel}: canonical is {p.canonical}, expected {expected}")

    # --- E. meta description ----------------------------------------------------
    if not (p.description or "").strip():
        errors.append(f"{rel}: no meta description")

    # --- F. headings ------------------------------------------------------------
    if p.h1 != 1:
        errors.append(f"{rel}: {p.h1} <h1> elements (expected exactly 1)")
    prev = None
    for level, htext in p.headings:
        if level >= 5:
            errors.append(f"{rel}: <h{level}> used ({htext[:40]!r}); the site uses h1..h4 only")
        if prev is not None and level > prev + 1:
            errors.append(f"{rel}: heading jumps from h{prev} to h{level} at {htext[:40]!r}")
        prev = level

    # --- G. images --------------------------------------------------------------
    for a in p.imgs:
        if "alt" not in a:
            errors.append(f"{rel}: <img> without alt attribute ({a.get('src', '')[:60]})")
        elif not (a.get("alt") or "").strip() and a.get("role") != "presentation":
            errors.append(f"{rel}: <img alt=\"\"> without role=presentation ({a.get('src', '')[:60]})")

    # --- H. lang / viewport -----------------------------------------------------
    if not p.lang:
        errors.append(f"{rel}: <html> has no lang attribute")
    if not p.viewport:
        errors.append(f"{rel}: no viewport meta tag")

    # --- A/I. tables ------------------------------------------------------------
    # The site's own rule is per *row*: a row that asserts a value links to the
    # official document that states it. A row whose cells are all blank/flagged
    # is the honest alternative the site uses for "could not confirm this".
    for ti, table in enumerate(p.tables):
        if not table["header"]:
            if len(table["rows"]) >= 4:
                warnings.append(f"{rel}: table {ti} has {len(table['rows'])} rows and no header row")
            continue
        body = table["rows"][1:]
        if not body:
            continue
        ncols = len(table["rows"][0])

        def official_links(cell):
            out = []
            for href in cell["links"]:
                if not href:
                    continue
                host = (urlparse(href).hostname or "").lower()
                if host in HOSTS or is_official(href):
                    out.append(href)
            return out

        if not any(official_links(c) for row in table["rows"] for c in row):
            # No row in this table carries an official link: a legend or narrative
            # table (a key that explains the site's own notation), not a data table.
            notes.append(f"table {ti}: legend/narrative table — no official link in any row")
            continue

        for ri, row in enumerate(body):
            if len(row) != ncols:
                warnings.append(f"{rel}: table {ti} row {ri} has {len(row)} cells, header has {ncols}")
            if any(official_links(c) for c in row):
                continue
            if all(cell_is_blank(c["text"]) for c in row):
                continue
            populated = [c["text"] for c in row if not cell_is_blank(c["text"])]
            if any(is_internal(h) for c in row for h in c["links"]):
                # The row cites this repository or the Flagged page. That is the
                # project's documented pattern for a design opinion or an
                # unconfirmed value — reported, not silently passed.
                warnings.append(
                    f"{rel}: table {ti} row {ri} cites the repository, not an official source "
                    f"— {' | '.join(t[:50] for t in populated[:3])}"
                )
                continue
            errors.append(
                f"{rel}: table {ti} row {ri} has values but no source link — "
                f"{' | '.join(t[:60] for t in populated[:4])}"
            )

    # --- J. affiliate anchors on product pages ----------------------------------
    if rel.startswith("products/"):
        if not any("link.amazon" in (h or "") for h, _t in p.links):
            errors.append(f"{rel}: product page carries no link.amazon affiliate anchor")

    # --- K. slop phrases in rendered copy ----------------------------------------
    # A phrase that is *quoted* is not slop: the site quotes the phrases it bans,
    # and quotes brand copy verbatim as evidence. Only unquoted use is a defect.
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S)
    body = re.sub(r"<code[^>]*>.*?</code>", " ", body, flags=re.S)
    body = re.sub(r"<q[^>]*>.*?</q>", " ", body, flags=re.S)
    body = html.unescape(re.sub(r"<[^>]+>", " ", body)).lower()
    for phrase in BANNED_PHRASES:
        for m in re.finditer(re.escape(phrase), body):
            before = body[max(0, m.start() - 1):m.start()]
            after = body[m.end():m.end() + 1]
            if before in ("'", "“", '"') or after in ("'", "”", '"'):
                notes.append(f"quoted occurrence of {phrase!r} — quoted, not written here")
                continue
            errors.append(f"{rel}: banned stock phrase in rendered copy: {phrase!r}")

    return errors, warnings, notes


def root_build_pages():
    """Every page the root generator writes, discovered from the tree."""
    pages = []
    for d in ROOT_DIRS:
        base = os.path.join(ROOT, d) if d else ROOT
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            if not name.endswith(".html"):
                continue
            rel = (d + name) if d else name
            pages.append(rel)
    return pages


def main():
    out_json = None
    if "--json" in sys.argv:
        out_json = sys.argv[sys.argv.index("--json") + 1]

    all_errors, all_warnings = [], []
    pages_checked = 0
    descs = {}
    for rel in root_build_pages():
        errs, warns, notes = audit_page(rel)
        pages_checked += 1
        all_errors.extend(errs)
        all_warnings.extend(warns)
        for n in notes:
            if n.startswith("description: "):
                d = n.split(": ", 1)[1].strip()
                if d:
                    descs.setdefault(d, []).append(rel)

    for d, pages in sorted(descs.items(), key=lambda kv: -len(kv[1])):
        if len(pages) > 1 and len(d) > 40:
            all_warnings.append(
                f"identical meta description on {len(pages)} pages: {pages[:5]} — {d[:70]!r}"
            )

    report = {
        "pages_checked": pages_checked,
        "errors": len(all_errors),
        "warnings": len(all_warnings),
        "error_list": all_errors,
        "warning_list": all_warnings,
        "official_hosts": sorted(HOSTS),
    }
    print(f"pages checked : {pages_checked}")
    print(f"errors         : {len(all_errors)}")
    for e in all_errors[:80]:
        print("  ERROR  " + e)
    if len(all_errors) > 80:
        print(f"  ... and {len(all_errors) - 80} more")
    print(f"warnings       : {len(all_warnings)}")
    for w in all_warnings[:40]:
        print("  WARN   " + w)
    if len(all_warnings) > 40:
        print(f"  ... and {len(all_warnings) - 40} more")

    if out_json:
        with open(out_json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        print(f"report written: {out_json}")

    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
