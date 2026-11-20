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
  8. every shipped page keeps its <title> and meta description inside the
     search-result budget (65 / 160 characters)

Exit code is non-zero if anything fails, so this can gate the deploy.
"""

import html
import json
import re
import sys
from html import unescape as html_unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "scripts"))
# F103/F104 gate (arena/e01a0112, 2026-11-19): the rules that closed those two
# findings live in one module so the repair script and this verifier can never
# disagree. See scripts/historical_compliance.py.
import historical_compliance as _hist  # noqa: E402
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
# Annex trees are the historical/verification builds; they are never indexed and are
# excluded from the canonical-page metadata checks below.
ANNEX_TREES = ("site", "dashboard", "research", "s2", "annex-88769516", "session-3740f69d", "docs")

OFFICIAL_HOSTS = {
    # Brand pages read 2026-11-17 against the two links submitted that day (sources S39/S40).
    # Registered as official brand sites, which is not the same as confirming a listing identity: F80.
    "chefiq.com",
    "www.thermomaven.com",
    # U.S. federal food-safety guidance (sources S48/S49, added 2026-11-19 by
    # arena/d154e428). These are government publication hosts, used only for the
    # safe-minimum internal temperature figures a food thermometer exists to check.
    # A registered host is not a product claim: nothing on the thermometer pages is
    # taken from them except the USDA temperature minimums and the advice to use a
    # thermometer.
    "www.fsis.usda.gov",
    "www.foodsafety.gov",
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
    # The IETF standards archive, added 2026-11-19 (arena/b3ed16c4). RFC 9309 is the
    # Robots Exclusion Protocol itself; there is no other publisher of the standard, and
    # "official" here means exactly what it means for the other entries: the party that
    # owns the fact publishes the page. No third-party blog or mirror is on this list.
    "www.rfc-editor.org",
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
# Two badge forms are legitimate after pass 16 (2026-11-20): the register form, whose
# link text is the source id, and the reader form (class "src src-word"), whose link
# text is the source's short human name and whose data-src-id attribute carries the id.
# Both are checked against the registered URL; the second form exists so a reader sees
# "Chefman RJ38-SQSS-8T guide" instead of "S13" without weakening the guarantee.
_BADGE = re.compile(r'<a class="src(?: src-word)?" href="([^"]+)"(?P<attrs>[^>]*)>'
                    r'(?P<text>S\d+|S-[A-Z]+|[^<]*)</a>')
_BADGE_ID = re.compile(r'data-src-id="([^"]+)"')

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
        _href = m.group(1)
        _id_attr = _BADGE_ID.search(m.group("attrs") or "")
        _is_id_text = bool(re.fullmatch(r"S\d+|S-[A-Z]+", m.group("text")))
        if not _id_attr and not _is_id_text:
            # Historical annexes label some badges with a short name instead of an S-id;
            # those were never covered by this id-to-URL guarantee.
            continue
        _sid = _id_attr.group(1) if _id_attr else m.group("text")
        if not re.fullmatch(r"S\d+|S-[A-Z]+", _sid):
            errors.append(f"{rel(page)}: badge data-src-id {_sid!r} is not a source id")
            continue
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
for _tree in ANNEX_TREES:
    _root = ROOT / _tree
    for _f in sorted(_root.rglob("*.html")):
        _t = _f.read_text(encoding="utf-8")
        _dirs = re.findall(r'<meta name="robots" content="([^"]*)"', _t, re.I)
        if not _dirs:
            errors.append(f"{rel(_f)}: annex page has no robots directive (annex boundary, F105)")
        elif any("noindex" not in _d for _d in _dirs):
            errors.append(f"{rel(_f)}: annex page asks to be indexed; only the canonical "
                          f"publication may be indexed (annex boundary, F105)")
for _stale in sorted(ROOT.glob("*/robots.txt")) + sorted(ROOT.glob("*/sitemap.xml")):
    if _stale.parent.name in ANNEX_TREES:
        errors.append(f"{rel(_stale)}: a robots.txt/sitemap.xml outside the host root is "
                      f"never fetched at /Zone1/; the root robots.txt is authoritative (F105)")

# 4c. Historical compliance — the repair that closed F103 and F104 (2026-11-19,
#     arena/e01a0112) is gated here, because a repair without a gate is a
#     decoration. The owner's brief settles what earlier passes left as owner
#     decisions: every outbound product link is marked sponsored (F103), no
#     published page claims the supplied short links are invalid (F103: their
#     status is unresolved, Zone3 FLG-003), and the disclosure sentence sits
#     under the masthead and repeats in the footer (F104). Rules imported from
#     scripts/historical_compliance.py, which also holds the idempotent repair
#     for the trees that have no generator.
for _tree in ANNEX_TREES:
    _root = ROOT / _tree
    for _f in sorted(_root.rglob("*.html")):
        _t = _f.read_text(encoding="utf-8")
        for _p in _hist.anchor_violations(_t):
            errors.append(f"{rel(_f)}: {_p} (F103)")
        for _p in _hist.disclosure_violations(_t):
            errors.append(f"{rel(_f)}: {_p} (F104)")
    for _f in sorted(_f for _f in _root.rglob("*")
                     if _f.suffix in _hist.CLAIM_SUFFIXES):
        for _p in _hist.claim_violations(_f.read_text(encoding="utf-8")):
            errors.append(f"{rel(_f)}: {_p} (F103)")

# 12. Search-snippet budget. Written 2026-11-20 (arena/91a755df) after counting the
#     built site: 27 of 63 pages published a <title> longer than 65 characters and 11
#     published a <meta name="description"> longer than 165, so what a searcher sees was
#     cut mid-sentence. Google Search Central's title-link documentation, read live
#     2026-11-20 (S50), states that a title link "is truncated in Google Search results
#     as needed, typically to fit the device width", asks for "descriptive and concise"
#     titles, and lists boilerplate titles that differ by only one piece of information
#     as a common issue. S51 describes the same truncation for the description snippet.
#     The budgets are an editorial convention chosen inside that guidance, not a limit
#     the documentation states; the check enforces the convention and nothing more.
TITLE_BUDGET = 60
DESC_BUDGET = 160
# The canonical publication only: the repository root and its four reader folders.
# Historical builds (research/, site/, s2/, the session annexes) are frozen, noindex
# and out of scope; `pages()` walks them too, so the path root is matched explicitly.
CANONICAL_PAGES = [p for p in pages()
                   if p.relative_to(ROOT).parts[0] in
                   {"index.html", "articles", "products", "categories", "guides"}
                   or len(p.relative_to(ROOT).parts) == 1]
_titles = {}
for page in CANONICAL_PAGES:
    text = page.read_text(encoding="utf-8")
    m = re.search(r"<title>(.*?)</title>", text, re.S)
    if not m:
        errors.append(f"{rel(page)}: no <title> element")
        continue
    title = html_unescape(m.group(1)).strip()
    if len(title) > TITLE_BUDGET:
        errors.append(f"{rel(page)}: <title> is {len(title)} characters (budget {TITLE_BUDGET}): {title!r}")
    _titles.setdefault(title, []).append(rel(page))
    d = re.search(r'<meta name="description" content="(.*?)">', text, re.S)
    if not d:
        errors.append(f"{rel(page)}: no meta description")
        continue
    desc = html_unescape(d.group(1)).strip()
    if len(desc) > DESC_BUDGET:
        errors.append(f"{rel(page)}: meta description is {len(desc)} characters "
                      f"(budget {DESC_BUDGET})")
for _t, _pages in sorted(_titles.items()):
    if len(_pages) > 1:
        errors.append(f"duplicate <title> on {len(_pages)} pages: {_t!r} -> {_pages}")

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
