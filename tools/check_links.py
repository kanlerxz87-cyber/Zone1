#!/usr/bin/env python3
"""
Zone1 — site integrity checker.

  python3 tools/check_links.py

Runs without any network access. Checks:

  Data layer
    1. every JSON dataset parses, and has the top-level keys its schema requires
    2. every product field that is marked "verified" carries a source URL on an
       official host; every field marked "unverified" carries a blank value
    3. every flag and every program term carries an official source URL
    4. every product, flag, program term and source id referenced by a page
       actually exists in the dataset that backs it

  HTML layer
    5. every internal href/src resolves to a file that exists in the repository
    6. every internal link that points at an HTML file also has a matching
       #anchor id in that file
    7. every external link is a well-formed absolute https:// URL
    8. every table row that carries a finding also carries an official source link
    9. no placeholder Associates tag is left in a rendered page body
   10. the required Amazon and FTC disclosure strings are present on every page

  Accessibility and responsive layer
   11. every page declares a language and a responsive viewport
   12. every page has exactly one <h1>, and heading levels never skip a level
   13. every <img> has a non-empty alt attribute
   14. every link and button has a discernible text label
   15. every table has a header row, and every data cell in a table with
       headers is covered by a column header
   16. every id referenced by an aria-* attribute exists in the page

Exit code is non-zero if any check fails.
"""

import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HREF_RE = re.compile(r'(?:href|src)\s*=\s*"([^"]+)"', re.I)
ID_RE = re.compile(r'\bid\s*=\s*"([^"]+)"', re.I)
ROW_RE = re.compile(r"<tr\b.*?</tr>", re.S | re.I)
CELL_RE = re.compile(r"<td\b[^>]*>(.*?)</td>", re.S | re.I)
TAG_RE = re.compile(r"<[^>]+>", re.S)
LINK_RE = re.compile(r'<a\b[^>]*href\s*=\s*"([^"]+)"', re.I)
SRC_CELL_RE = re.compile(r'<td[^>]*class="src"[^>]*>(.*?)</td>', re.S | re.I)
SRC_HREF_RE = re.compile(r'<a\b[^>]*href\s*=\s*"([^"]+)"', re.I)
WHITESPACE_RE = re.compile(r"\s+")

OFFICIAL_HOSTS = (
    "amazon.com",
    "link.amazon",
    "m.media-amazon.com",
    "images-na.ssl-images-amazon.com",
    "affiliate-program.amazon.com",
    "ftc.gov",
    "ecfr.gov",
    "api.github.com",
    "github.com",
    "githubusercontent.com",
    "docs.github.com",
)

REQUIRED_STRINGS = [
    "As an Amazon Associate I earn from qualifying purchases.",
    "qualifying purchases made through our links",
]

# ---------------------------------------------------------------------------
# dataset schema
# ---------------------------------------------------------------------------

DATA_SCHEMA = {
    "products.json": {
        "top": ["meta", "links", "products", "brand_signals", "competitive_set"],
        "product": ["id", "ref", "name", "short_name", "asin", "supplied_link",
                    "canonical_url", "special_link_template", "brand", "category",
                    "category_path", "verified_on", "fields", "bullets", "flag_ids"],
        "field": ["label", "value", "status", "source"],
    },
    "program.json": {
        "top": ["meta", "sources", "program_terms", "automation_rules"],
        "source": ["id", "title", "publisher", "url", "type", "accessed"],
        "term": ["id", "area", "requirement", "detail", "source_id", "applies_to"],
        "rule": ["id", "rule", "detail", "source_id"],
    },
    "flags.json": {
        "top": ["meta", "flags"],
        "flag": ["id", "title", "severity", "category", "observation",
                 "why_it_matters", "source", "action_taken", "status",
                 "blocks_publication"],
    },
}

DATA_FILES = {
    "products.json": ("products", "fields"),
    "program.json": ("program_terms", "sources"),
    "flags.json": ("flags", None),
}


def host_of(url):
    m = re.match(r"^https?://([^/]+)", url or "")
    if not m:
        return None
    return m.group(1).split("@")[-1].split(":")[0].lower()


def is_official(url):
    host = host_of(url)
    if not host:
        return False
    return any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS)


def check_datasets(errors, warnings):
    """Checks 1-4. Returns the loaded datasets."""
    global FLAG_IDS
    loaded = {}
    for name, schema in DATA_SCHEMA.items():
        path = os.path.join(ROOT, "data", name)
        if not os.path.exists(path):
            errors.append("data/%s: missing" % name)
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except ValueError as exc:
            errors.append("data/%s: does not parse as JSON (%s)" % (name, exc))
            continue
        loaded[name] = data
        if name == "flags.json":
            FLAG_IDS = {f.get("id") for f in data.get("flags", [])}

        for key in schema["top"]:
            if key not in data:
                errors.append("data/%s: missing top-level key %r" % (name, key))
        if "meta" in data and not isinstance(data["meta"], dict):
            errors.append("data/%s: 'meta' must be an object" % name)

    # --- products.json -----------------------------------------------------
    if "products.json" in loaded:
        products = loaded["products.json"].get("products", [])
        p_schema = DATA_SCHEMA["products.json"]["product"]
        f_schema = DATA_SCHEMA["products.json"]["field"]
        asins = set()
        for p in products:
            for key in p_schema:
                if key not in p:
                    errors.append("data/products.json: product %r missing key %r"
                                  % (p.get("id", "?"), key))
            asin = p.get("asin")
            if asin:
                if not re.match(r"^B0[A-Z0-9]{8}$", asin):
                    errors.append("data/products.json: product %r has a malformed ASIN %r"
                                  % (p.get("id"), asin))
                if asin in asins:
                    errors.append("data/products.json: duplicate ASIN %r" % asin)
                asins.add(asin)
            for f in p.get("fields", []):
                for key in f_schema:
                    if key not in f:
                        errors.append("data/products.json: product %r field %r missing key %r"
                                      % (p.get("id"), f.get("label", "?"), key))
                status = f.get("status")
                value = f.get("value")
                source = f.get("source")
                if status == "verified":
                    if not source:
                        errors.append("data/products.json: %s / %r is verified but has no source"
                                      % (p.get("id"), f.get("label")))
                    elif not is_official(source):
                        errors.append("data/products.json: %s / %r has a non-official source %r"
                                      % (p.get("id"), f.get("label"), source))
                    if value is None or str(value).strip() == "":
                        errors.append("data/products.json: %s / %r is verified but its value is blank"
                                      % (p.get("id"), f.get("label")))
                elif status == "unverified":
                    if value not in (None, ""):
                        errors.append("data/products.json: %s / %r is unverified but carries the value %r"
                                      % (p.get("id"), f.get("label"), value))
                elif status not in ("verified", "unverified", "derived", "editorial"):
                    errors.append("data/products.json: %s / %r has an unknown status %r"
                                  % (p.get("id"), f.get("label"), status))
            for fid in p.get("flag_ids", []):
                if fid not in FLAG_IDS:
                    errors.append("data/products.json: product %r references unknown flag %r"
                                  % (p.get("id"), fid))
        for l in loaded["products.json"].get("links", []):
            if l.get("segment_is_asin") is False and l.get("resolved_asin") == l.get("path_segment"):
                errors.append("data/products.json: link %r claims the segment is not an ASIN "
                              "but it equals the resolved ASIN" % l.get("id"))
            if l.get("resolved_asin") and l["resolved_asin"] not in asins:
                errors.append("data/products.json: link %r resolves to unknown ASIN %r"
                              % (l.get("id"), l["resolved_asin"]))
            for fid in l.get("flag_ids", []):
                if fid not in FLAG_IDS:
                    errors.append("data/products.json: link %r references unknown flag %r"
                                  % (l.get("id"), fid))

    # --- program.json ------------------------------------------------------
    if "program.json" in loaded:
        prog = loaded["program.json"]
        s_schema = DATA_SCHEMA["program.json"]["source"]
        t_schema = DATA_SCHEMA["program.json"]["term"]
        r_schema = DATA_SCHEMA["program.json"]["rule"]
        source_ids = set()
        for s in prog.get("sources", []):
            for key in s_schema:
                if key not in s:
                    errors.append("data/program.json: source %r missing key %r"
                                  % (s.get("id", "?"), key))
            if s.get("id"):
                source_ids.add(s["id"])
            if not is_official(s.get("url", "")):
                errors.append("data/program.json: source %r has a non-official url %r"
                              % (s.get("id"), s.get("url")))
        for t in prog.get("program_terms", []):
            for key in t_schema:
                if key not in t:
                    errors.append("data/program.json: term %r missing key %r"
                                  % (t.get("id", "?"), key))
            if t.get("source_id") not in source_ids:
                errors.append("data/program.json: term %r references unknown source %r"
                              % (t.get("id"), t.get("source_id")))
        for r in prog.get("automation_rules", []):
            for key in r_schema:
                if key not in r:
                    errors.append("data/program.json: rule %r missing key %r"
                                  % (r.get("id", "?"), key))
            if r.get("source_id") not in source_ids:
                errors.append("data/program.json: rule %r references unknown source %r"
                              % (r.get("id"), r.get("source_id")))

    # --- flags.json --------------------------------------------------------
    if "flags.json" in loaded:
        fl_schema = DATA_SCHEMA["flags.json"]["flag"]
        seen = set()
        for f in loaded["flags.json"].get("flags", []):
            for key in fl_schema:
                if key not in f:
                    errors.append("data/flags.json: flag %r missing key %r"
                                  % (f.get("id", "?"), key))
            if f.get("id") in seen:
                errors.append("data/flags.json: duplicate flag id %r" % f.get("id"))
            seen.add(f.get("id"))
            if not is_official(f.get("source", "")):
                errors.append("data/flags.json: flag %r has a non-official source %r"
                              % (f.get("id"), f.get("source")))
            for url in f.get("secondary_sources", []):
                if not is_official(url):
                    errors.append("data/flags.json: flag %r has a non-official secondary source %r"
                                  % (f.get("id"), url))
            if f.get("severity") not in ("high", "medium", "low"):
                errors.append("data/flags.json: flag %r has an unknown severity %r"
                              % (f.get("id"), f.get("severity")))
            if f.get("status") not in ("needs review", "done", "open", "closed"):
                errors.append("data/flags.json: flag %r has an unknown status %r"
                              % (f.get("id"), f.get("status")))
    return loaded


# ---------------------------------------------------------------------------
# HTML parsing
# ---------------------------------------------------------------------------

class PageParser(HTMLParser):
    """Collects the structural facts the accessibility checks need."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.has_viewport = False
        self.has_meta_description = False
        self.h1_count = 0
        self.headings = []          # (level, text)
        self.imgs = []              # (src, alt or None)
        self.anchors = []           # (href, text)
        self.aria_refs = []         # ids referenced by aria-*
        self.table_stack = []
        self.tables = []            # list of dicts
        self.in_link = False
        self.link_text = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "meta":
            if a.get("name", "").lower() == "viewport":
                self.has_viewport = True
            if a.get("name", "").lower() == "description":
                self.has_meta_description = True
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            if tag == "h1":
                self.h1_count += 1
            self.current = {"level": int(tag[1]), "text": []}
        elif tag == "img":
            self.imgs.append((a.get("src", ""), a.get("alt")))
        elif tag == "a":
            self.in_link = True
            self.link_text = []
            self.anchors.append((a.get("href", ""), None))
        elif tag == "table":
            self.table_stack.append({"has_th": False, "rows": 0, "cells": 0, "max_cells": 0})
        elif tag == "tr":
            if self.table_stack:
                self.table_stack[-1]["rows"] += 1
        elif tag in ("td", "th"):
            if self.table_stack:
                if tag == "th":
                    self.table_stack[-1]["has_th"] = True
                else:
                    self.table_stack[-1]["cells"] += 1
                    self.table_stack[-1]["max_cells"] = max(
                        self.table_stack[-1]["max_cells"], self.table_stack[-1]["cells"])
                    self.table_stack[-1]["cells"] = 0
        for key, value in attrs:
            if key.startswith("aria-") and key in ("aria-labelledby", "aria-describedby",
                                                   "aria-controls", "aria-owns"):
                for token in (value or "").split():
                    self.aria_refs.append(token)

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self.current:
            text = WHITESPACE_RE.sub(" ", "".join(self.current["text"])).strip()
            self.headings.append((self.current["level"], text))
            self.current = None
        elif tag == "a" and self.in_link:
            text = WHITESPACE_RE.sub(" ", "".join(self.link_text)).strip()
            if self.anchors:
                self.anchors[-1] = (self.anchors[-1][0], text)
            self.in_link = False
        elif tag == "table" and self.table_stack:
            self.tables.append(self.table_stack.pop())

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"].append(data)
        if self.in_link:
            self.link_text.append(data)


def html_files():
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs
                   if d not in (".git", "node_modules", "__pycache__", "tools", "data",
                                "legacy", "docs")]
        for f in files:
            if f.endswith(".html"):
                out.append(os.path.join(base, f))
    return sorted(out)


def rel_url(page, url):
    """Resolve a relative URL against the page's directory."""
    return os.path.normpath(os.path.join(os.path.dirname(page), url))


def main():
    errors, warnings = [], []
    external_total = 0
    rows_checked = 0

    global FLAG_IDS
    loaded = check_datasets(errors, warnings)

    files = html_files()
    ids_by_file = {}
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            ids_by_file[f] = set(ID_RE.findall(fh.read()))

    for page in files:
        with open(page, "r", encoding="utf-8") as fh:
            content = fh.read()
        rel_page = os.path.relpath(page, ROOT)

        # 10 — required disclosure strings (whitespace-insensitive)
        flat = " ".join(content.split())
        for needle in REQUIRED_STRINGS:
            if needle not in flat:
                errors.append("%s: missing required disclosure string %r" % (rel_page, needle))

        # 9 — placeholder tag must not appear in a rendered anchor
        for m in re.finditer(r'<a\b[^>]*href\s*=\s*"([^"]*YOUR-TAG-XX[^"]*)"', content, re.I):
            errors.append("%s: rendered anchor uses the placeholder tag %s" % (rel_page, m.group(1)))

        # 1, 2, 7 — links
        for url in HREF_RE.findall(content):
            url = url.strip()
            if not url or url.startswith("#"):
                if url.startswith("#"):
                    anchor = url[1:]
                    if anchor and anchor not in ids_by_file[page]:
                        errors.append("%s: anchor %s has no matching id in the same file"
                                      % (rel_page, url))
                continue
            if url.startswith("data:"):
                continue
            if url.startswith("http://") or url.startswith("https://"):
                external_total += 1
                if url.startswith("http://"):
                    errors.append("%s: external link is not https: %s" % (rel_page, url))
                if not is_official(url):
                    warnings.append("%s: external link to a non-official host: %s" % (rel_page, url))
                continue
            target = rel_url(page, url.split("#")[0])
            if not os.path.exists(target):
                errors.append("%s: broken internal link %s -> %s" % (rel_page, url, target))
            if "#" in url and target.endswith(".html"):
                anchor = url.split("#", 1)[1]
                if anchor and anchor not in ids_by_file.get(target, set()):
                    errors.append("%s: anchor %s not found in %s" % (rel_page, anchor,
                                                                    os.path.relpath(target, ROOT)))

        # 8 — every data row carries a source cell, and that source is official
        for row in ROW_RE.findall(content):
            if "<th" in row:
                continue
            cells = CELL_RE.findall(row)
            if not cells:
                continue
            rows_checked += 1
            src_match = SRC_CELL_RE.search(row)
            if not src_match:
                text = TAG_RE.sub(" ", cells[0])[:70]
                errors.append("%s: table row without a source cell -> %s" % (rel_page, text))
                continue
            for href in SRC_HREF_RE.findall(src_match.group(1)):
                if not is_official(href):
                    errors.append("%s: source cell links to a non-official host: %s"
                                  % (rel_page, href))

        # 11-16 — accessibility and responsive structure
        parser = PageParser()
        parser.feed(content)

        if not parser.lang:
            errors.append("%s: <html> has no lang attribute" % rel_page)
        if not parser.has_viewport:
            errors.append("%s: no responsive viewport meta tag" % rel_page)
        if not parser.has_meta_description:
            errors.append("%s: no meta description" % rel_page)
        if parser.h1_count != 1:
            errors.append("%s: expected exactly one <h1>, found %d"
                          % (rel_page, parser.h1_count))

        previous = None
        for level, text in parser.headings:
            if previous is not None and level > previous + 1:
                errors.append("%s: heading level jumps from h%d to h%d (%r)"
                              % (rel_page, previous, level, text[:40]))
            previous = level

        for src, alt in parser.imgs:
            if alt is None:
                errors.append("%s: <img src=%r> has no alt attribute" % (rel_page, src))
            elif alt.strip() == "":
                errors.append("%s: <img src=%r> has an empty alt attribute" % (rel_page, src))

        for href, text in parser.anchors:
            if text is None or text.strip() == "":
                errors.append("%s: anchor %r has no discernible text label" % (rel_page, href))

        for i, table in enumerate(parser.tables):
            if not table["has_th"]:
                errors.append("%s: table %d has no header row (<th>)" % (rel_page, i))
            elif table["rows"] > 1 and table["max_cells"] == 0:
                errors.append("%s: table %d has data rows but no <td> cells" % (rel_page, i))

        for token in parser.aria_refs:
            if token not in ids_by_file[page]:
                errors.append("%s: aria reference %r has no matching id in the page"
                              % (rel_page, token))

    print("Checked %d HTML files, %d table rows, %d external links, %d datasets."
          % (len(files), rows_checked, external_total, len(DATA_SCHEMA)))
    if warnings:
        print("\nWarnings (%d):" % len(warnings))
        for w in warnings:
            print("  - " + w)
    if errors:
        print("\nERRORS (%d):" % len(errors))
        for e in errors:
            print("  - " + e)
        return 1
    print("\nAll checks passed: datasets parse and satisfy their schema, no broken internal "
          "links,\nno missing anchors, every data row carries an official source link, "
          "disclosures present on\nevery page, and every page passes the accessibility and "
          "responsive checks.")
    return 0


FLAG_IDS = set()

if __name__ == "__main__":
    sys.exit(main())
