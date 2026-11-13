#!/usr/bin/env python3
"""
Zone1 — site integrity checker.

  python3 tools/check_links.py

Checks, without any network access:
  1. every internal href/src resolves to a file that exists in the repository
  2. every internal link that points at an HTML file also has a matching
     #anchor id in that file
  3. every external link is a well-formed absolute https:// URL
  4. every table row that carries a finding also carries an official source link
  5. no placeholder Associates tag is left in a rendered page body
  6. the required Amazon and FTC disclosure strings are present on every page

Exit code is non-zero if any check fails.
"""

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
)

REQUIRED_STRINGS = [
    "As an Amazon Associate I earn from qualifying purchases.",
    "qualifying purchases made through our links",
]


def html_files():
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__", "tools")]
        for f in files:
            if f.endswith(".html"):
                out.append(os.path.join(base, f))
    return sorted(out)


def rel_url(page, url):
    """Resolve a relative URL against the page's directory."""
    return os.path.normpath(os.path.join(os.path.dirname(page), url))


def main():
    files = html_files()
    errors, warnings = [], []
    external_total = 0
    rows_checked = 0

    ids_by_file = {}
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            ids_by_file[f] = set(ID_RE.findall(fh.read()))

    for page in files:
        with open(page, "r", encoding="utf-8") as fh:
            content = fh.read()
        rel_page = os.path.relpath(page, ROOT)

        # 6 — required disclosure strings (whitespace-insensitive)
        flat = " ".join(content.split())
        for needle in REQUIRED_STRINGS:
            if needle not in flat:
                errors.append("%s: missing required disclosure string %r" % (rel_page, needle))

        # 5 — placeholder tag must not appear in a rendered link
        for m in LINK_RE.finditer(content):
            if "YOUR-TAG-XX" in m.group(1) and 'class="linkbox"' not in content[m.start() - 200:m.start()]:
                # allowed only inside the documented template boxes
                pass
        for m in re.finditer(r'<a\b[^>]*href\s*=\s*"([^"]*YOUR-TAG-XX[^"]*)"', content, re.I):
            errors.append("%s: rendered anchor uses the placeholder tag %s" % (rel_page, m.group(1)))

        # 1, 2, 3 — links
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
                host = re.sub(r"^https?://([^/]+).*$", r"\1", url)
                host = host.split("@")[-1].split(":")[0]
                if not any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS):
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

        # 4 — every data row carries a source link
        for row in ROW_RE.findall(content):
            if "<th" in row:
                continue
            cells = CELL_RE.findall(row)
            if not cells:
                continue
            rows_checked += 1
            has_source = bool(re.search(r'<td[^>]*class="src"', row))
            if not has_source:
                text = TAG_RE.sub(" ", cells[0])[:70]
                # rows that are layout-only (e.g. the T of a two-column matrix) are flagged
                errors.append("%s: table row without a source cell -> %s" % (rel_page, text))

    print("Checked %d HTML files, %d table rows, %d external links." % (len(files), rows_checked, external_total))
    if warnings:
        print("\nWarnings (%d):" % len(warnings))
        for w in warnings:
            print("  - " + w)
    if errors:
        print("\nERRORS (%d):" % len(errors))
        for e in errors:
            print("  - " + e)
        return 1
    print("\nAll checks passed: no broken internal links, no missing anchors, "
          "every data row carries a source link, disclosures present on every page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
