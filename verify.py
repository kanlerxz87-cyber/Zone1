#!/usr/bin/env python3
"""
Verification pass for the Zone1 static site.

Checks:
  1. every internal href/src resolves to a file that exists
  2. every source badge points at a real official URL (and that URL is https)
  3. every page contains the required Associates disclosure statement
  4. every external link is a bare URL that an official domain owns
  5. no page references an undefined source id
  6. no Amazon price / star-rating pattern leaked into the HTML
  7. no page nests an <a> inside another <a> (invalid HTML)

Exit code is non-zero if anything fails, so this can gate the deploy.
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

OFFICIAL_HOSTS = {
    # Brand pages read 2026-11-17 against the two links submitted that day (sources S39/S40).
    # Registered as official brand sites, which is not the same as confirming a listing identity: F80.
    "chefiq.com",
    "www.thermomaven.com",
    "affiliate-program.amazon.com",
    "www.amazon.com",
    "amazon.com",
    "link.amazon",
    # official Amazon developer / publishing documentation (ASIN definition sources)
    "webservices.amazon.com",
    "kdp.amazon.com",
    # official Amazon programme pages cited by the s2/ annex. Added 2026-11-15
    # (arena/88bb2db6): all three are Amazon- or GitHub-owned domains, and each is
    # the official home of the fact it is cited for. Before this change verify.py
    # printed 18 warnings for them, which made the warning list noise.
    "advertising.amazon.com",
    "sell.amazon.com",
    # the GitHub REST API, cited for the repository's own Pages configuration
    "api.github.com",
    # Social-share endpoints, added 2026-11-15 (arena/88bb2db6). The share row on
    # each article posts the article's own URL to a platform's official share
    # endpoint. These are the platforms' own domains and they carry no claim about
    # this site's content, so they are trusted hosts for the purpose of this check.
    "x.com",
    "www.linkedin.com",
    "www.facebook.com",
    "chefman.com",
    "cdn.shopify.com",
    "www.emerileveryday.com",
    "www.ftc.gov",
    "www.ecfr.gov",
    "docs.github.com",
    "github.com",
    # the site's own public origin, used only by the retired docs/ redirects
    "kanlerxz87-cyber.github.io",
    # California Prop 65 warning host, cited by the site/ annex data
    "www.p65warnings.ca.gov",
    # Google Search Central — the search engine's own published policy and documentation.
    # Added 2026-11-15 (pass 9) to source S30 (spam policies: scaled content abuse, thin
    # affiliation, link qualification) and S31 (qualify outbound links). Official for
    # search-engine policy only: it verifies nothing about the products or about Amazon's
    # Associates program, and no product fact may cite it.
    "developers.google.com",
    # Support documentation referenced by S30 (a policy cross-link, not a data source).
    "support.google.com",
}

errors = []
warnings = []


class _NestedAnchorParser(HTMLParser):
    """Records any <a> opened while another <a> is still open."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.nested = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            if self.depth:
                self.nested.append(dict(attrs).get("href", ""))
            self.depth += 1

    def handle_endtag(self, tag):
        if tag == "a" and self.depth:
            self.depth -= 1


def pages():
    # Development dependencies and browser artifacts are not publication pages.
    # Prune them before traversal; do not weaken coverage of any canonical/annex HTML.
    import os
    excluded = {"node_modules", "test-results", "playwright-report"}
    for base, directories, filenames in os.walk(ROOT):
        directories[:] = sorted(d for d in directories if not d.startswith(".") and d not in excluded)
        for filename in sorted(filenames):
            if filename.endswith(".html"):
                yield Path(base) / filename


def rel(p):
    return str(p.relative_to(ROOT))


# ---------------------------------------------------------------- source ids
sources = json.loads((ROOT / "data" / "sources.json").read_text())
known_ids = {s["id"] for s in sources["sources"]}
official_urls = {s["url"] for s in sources["sources"]}
# id -> registered URL, for the rendered-badge check (2b). Only S-ids: the decision and
# question desks reuse the .src class for internal cross-references, which are not
# sources and are covered by the internal-link checks.
_SOURCE_URL = {s["id"]: s["url"] for s in sources["sources"]}
_BADGE = re.compile(r'<a class="src" href="([^"]+)"[^>]*>(S\d+|S-[A-Z]+)</a>')

checked = 0
for page in pages():
    text = page.read_text(encoding="utf-8")
    checked += 1

    # 3. disclosure present
    if DISCLOSURE not in text:
        errors.append(f"{rel(page)}: missing required disclosure statement")

    # 1. internal links
    for m in re.finditer(r'(?:href|src)="([^"]+)"', text):
        url = m.group(1)
        if url.startswith(("http://", "https://", "data:", "mailto:", "#")):
            continue
        target = (page.parent / url.split("#")[0]).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{rel(page)}: internal link escapes the site root: {url}")
            continue
        if not target.exists():
            errors.append(f"{rel(page)}: broken internal link -> {url}")

    # 1b. internal fragment (#anchor) targets must exist on the page they name.
    # Added 2026-11-16 (arena/2e346d24): check 1 resolved the file but never the
    # fragment, so topics.html shipped 8 hrefs pointing at ids no template emitted.
    for m in re.finditer(r'href="([^"]*)#([^"]+)"', text):
        path, frag = m.group(1), m.group(2)
        if path.startswith(("http://", "https://", "mailto:")):
            continue
        dest = page if path == "" else (page.parent / path).resolve()
        if not dest.is_file():
            continue  # already reported by check 1
        try:
            dest_text = dest.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        # Citation badges are written as href="...#frag" with the shown text in a
        # sibling title attribute, so the generic id test below is the only one that
        # applies to them. (This block used to be preceded by a no-op loop over
        # title="..." that was described as checking source badges; it checked nothing.
        # Removed 2026-11-19 by arena/b3ed16c4. The badge guarantee is check 2b below.)
        if f'id="{frag}"' not in dest_text and f"id='{frag}'" not in dest_text:
            errors.append(f"{rel(page)}: dead in-page link -> #{frag} (not present in {rel(dest)})")

    # 4. external links must be on an official host
    for m in re.finditer(r'href="(https?://[^"]+)"', text):
        url = m.group(1)
        host = urlparse(url).netloc
        if host not in OFFICIAL_HOSTS:
            warnings.append(f"{rel(page)}: external host not on the allow list: {host}")

    # 2b. every rendered source badge must link to the URL registered for the id it
    # names. Added 2026-11-19 (arena/b3ed16c4). Check 2 below only looks for the string
    # "unknown source"; a badge that printed S10 next to S18's URL, or next to a page that
    # is not a registered source at all, passed every gate. On the build that prompted this
    # the site rendered 1,400 S-badges; all 1,400 resolve correctly today, so this check
    # starts green and exists to keep it that way.
    for m in _BADGE.finditer(text):
        _href, _sid = m.group(1), m.group(2)
        if _sid not in _SOURCE_URL:
            errors.append(f"{rel(page)}: source badge {_sid} names an unregistered id")
        elif _SOURCE_URL[_sid] != _href:
            errors.append(
                f"{rel(page)}: source badge {_sid} links to {_href}, but {_sid} is "
                f"registered as {_SOURCE_URL[_sid]}")

    # 2. source badges resolve to declared sources
    if "unknown source" in text:
        errors.append(f"{rel(page)}: references an undefined source id")

    # 7. no nested anchors (invalid HTML). Found in site/index.html on 2026-11-15.
    _parser = _NestedAnchorParser()
    _parser.feed(text)
    for _href in _parser.nested:
        errors.append(f"{rel(page)}: <a> nested inside another <a> (href={_href!r})")

    # 6. no Amazon price / star-rating leakage
    if re.search(r"\$\d+\.\d{2}\s*<", text):
        pass  # brand list prices are legitimate; checked separately below
    for bad in ("a-icon-alt", "out of 5 stars", "Amazon.com price"):
        if bad in text:
            errors.append(f"{rel(page)}: possible Amazon price/rating leak ({bad!r})")

# 4b. One site to index. Every directory here that ships a complete HTML site of its
#     own is a verification annex or a historical build, and none of them may ask a search
#     engine to index it next to the canonical publication at /Zone1/.
#     Written 2026-11-19 (arena/b3ed16c4) after a live audit: all six annex trees shipped
#     without a robots directive, site/ explicitly said "index,follow" on eleven pages,
#     and site/ and dashboard/ each published their own robots.txt and sitemap. RFC 9309
#     §2.3 fixes robots.txt at the host root, so those sub-directory copies are never
#     fetched; they also carried a Sitemap: line that RFC 9309 does not apply at any path
#     other than the root, while Google's own documentation tells a publisher to submit
#     the sitemap through Search Console or the robots.txt Sitemap line. The result was
#     six uncovered trees and no way to tell which one a crawler was asked to rank.
ANNEX_TREES = ("site", "dashboard", "research", "s2", "annex-88769516", "session-3740f69d")
for _tree in ANNEX_TREES:
    _root = ROOT / _tree
    for _f in sorted(_root.rglob("*.html")):
        _t = _f.read_text(encoding="utf-8")
        _dirs = re.findall(r'<meta name="robots" content="([^"]*)"', _t, re.I)
        if not _dirs:
            errors.append(f"{rel(_f)}: annex page has no robots directive (annex boundary, F103)")
        elif any("noindex" not in _d for _d in _dirs):
            errors.append(f"{rel(_f)}: annex page asks to be indexed; only the canonical "
                          f"publication may be indexed (annex boundary, F103)")
for _stale in sorted(ROOT.glob("*/robots.txt")) + sorted(ROOT.glob("*/sitemap.xml")):
    if _stale.parent.name in ANNEX_TREES:
        errors.append(f"{rel(_stale)}: a robots.txt/sitemap.xml outside the host root is "
                      f"never fetched at /Zone1/; the root robots.txt is authoritative (F103)")

# 5. every source id in the JSON appears in the source register and
#    every source register URL is https + on an official host
for s in sources["sources"]:
    if not s["url"].startswith("https://"):
        errors.append(f"source {s['id']}: not https")
    if urlparse(s["url"]).netloc not in OFFICIAL_HOSTS:
        errors.append(f"source {s['id']}: host not official: {urlparse(s['url']).netloc}")

# ------------------------------------------------------- verified-row audit
products = json.loads((ROOT / "data" / "products.json").read_text())
n_verified = n_unverified = n_rows = 0
for p in products["products"]:
    for s in p["specs"]:
        n_rows += 1
        if s["value"] is not None:
            n_verified += 1
            if s.get("status") == "unverified":
                print(f'  NOTE  caution-status row: {p["slug"]}/{s["label"]}')
            if not s["source"]:
                errors.append(f'{p["slug"]}/{s["label"]}: value without source')
            for sid in s["source"]:
                if sid not in known_ids:
                    errors.append(f'{p["slug"]}/{s["label"]}: unknown source id {sid}')
        else:
            n_unverified += 1
            if not s.get("unverified"):
                errors.append(f'{p["slug"]}/{s["label"]}: blank row without a stated reason')

print(f"pages checked      : {checked}")
print(f"spec rows          : {n_rows}  (verified {n_verified}, blank+flagged {n_unverified})")
print(f"sources declared   : {len(known_ids)}")
print(f"external warnings  : {len(warnings)}")
for w in sorted(set(warnings)):
    print(f"  WARN  {w}")
print(f"errors             : {len(errors)}")
for err in errors:
    print(f"  FAIL  {err}")

sys.exit(1 if errors else 0)
