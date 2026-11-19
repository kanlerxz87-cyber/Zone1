#!/usr/bin/env python3
"""Historical-tree compliance rules and idempotent repair (F103/F104).

Written 2026-11-19 by arena/e01a0112 to close two open findings against the
owner's brief, which settles what earlier passes recorded as owner decisions:

  * "Keep every outbound product link marked as sponsored"
  * "Keep the disclosure above the fold on every page, including this one"
    (a strip under the masthead, repeated in the footer)
  * "Do not claim that the supplied short links are invalid; their exact
    compliance status is unresolved in FLG-003."

F103 (arena/1970a80b): the Pages artifact publishes the whole repository root,
so seven historical builds are live alongside the canonical shop. They carried
about 300 Amazon product anchors without rel="sponsored", and several pages
published the verdict that the supplied short links are "invalid".
F104 (arena/43667e90): the annex pages lacked the disclosure in one or both of
the two required placements.

This module is the single source of truth for the repair and for the rules that
keep it repaired:

  * ``is_product_href`` — which outbound anchors are product links. The rule is
    build.py's ``is_product_href`` (root guard) extended with the slug form of
    /dp/ URLs and product-listing paths the historical pages use; help and
    policy pages on Amazon-adjacent hosts are citations, never product links.
  * ``qualify_anchors`` — add rel="sponsored nofollow noopener" to product
    anchors that lack it. Never rewrites a destination href.
  * ``claim_violations`` — every occurrence of "invalid" in a published claim
    must sit inside one of the allow-listed attributed phrases (a third-party
    tracker's quoted wording, or a negation that explicitly refuses the
    verdict). Anything else is a published "invalid" claim and fails.
  * ``disclosure_violations`` — the required sentence must appear under the
    masthead (after </header> when the page has one, before the first <h1> or
    within 4000 characters of <body>) and again inside <footer>.
  * ``transform`` — the idempotent repair for trees with no generator in this
    repository (dashboard/, annex-88769516/, session-3740f69d/, docs/). Trees
    with generators (s2/, site/, research/) are repaired at the generator and
    re-emitted; this module's rules gate both kinds.

Usage:
  python3 scripts/historical_compliance.py           # repair the frozen trees
  python3 scripts/historical_compliance.py --check   # fail if anything drifted

verify.py check 4c imports the rules from here, so the gate and the repair can
never disagree.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

# Trees with no generator in this repository. scripts/add_annex_noindex.py is the
# precedent: a frozen tree is repaired by an idempotent normaliser that records
# what it changed, not by resurrecting a generator that does not exist.
FROZEN_TREES = ("dashboard", "annex-88769516", "session-3740f69d", "docs")

# Every published tree that the historical gates cover (F105's list).
ANNEX_TREES = ("site", "dashboard", "research", "s2",
               "annex-88769516", "session-3740f69d", "docs")

# File types whose text a reader sees as a claim. .py sources in the trees are
# code, not published claims; their error strings are not editorial verdicts.
CLAIM_SUFFIXES = (".html", ".js", ".json", ".md", ".css", ".txt")

_PRODUCT_PREFIXES = ("/gp/product", "/product-reviews", "/b",
                     "/Best-Sellers/", "/gp/bestsellers/", "/gp/new-releases")


def is_product_href(href: str) -> bool:
    """Submitted links and product/listing pages; policy and help URLs are not.

    Root build.py's is_product_href covers link.amazon tokens (minus the
    deliberate ZZZ9ZZZZZ control) and /dp/ + /gp/product/ on amazon.com. The
    historical trees also link slug-form product URLs (…/dp/<ASIN>) and product
    listings (/b?node=…, /Best-Sellers/, /gp/bestsellers/, /gp/new-releases,
    /product-reviews/), which the brief's "every outbound product link" covers.
    Help, policy and developer documentation on affiliate-program.amazon.com,
    kdp.amazon.com, webservices.amazon.com, sell.amazon.com and
    advertising.amazon.com are citations and must NOT be marked sponsored.
    """
    from urllib.parse import urlsplit
    parsed = urlsplit(href.replace("&amp;", "&"))
    host = parsed.hostname or ""
    if host == "link.amazon":
        return "ZZZ9ZZZZZ" not in parsed.path
    if host in ("amazon.com", "www.amazon.com"):
        return "/dp/" in parsed.path or parsed.path.startswith(_PRODUCT_PREFIXES)
    return False


_ANCHOR = re.compile(r"<a\b[^>]*?>", re.I)
_HREF = re.compile(r"""href\s*=\s*("([^"]*)"|'([^']*)')""", re.I)
_REL = re.compile(r"""\srel\s*=\s*("([^"]*)"|'([^']*)')""", re.I)
_QUAL = ("sponsored", "nofollow", "noopener")


def qualify_anchors(text: str) -> str:
    """Add rel="sponsored nofollow noopener" to product anchors missing it.

    Existing rel tokens are preserved; only the three required tokens are added.
    hrefs are never rewritten (Participation Requirements 6(v)/6(w): never
    obscure or replace where a link goes).
    """
    def fix(m: re.Match) -> str:
        tag = m.group(0)
        href_m = _HREF.search(tag)
        if not href_m:
            return tag
        href = href_m.group(2) if href_m.group(2) is not None else href_m.group(3)
        if not is_product_href(href):
            return tag
        rel_m = _REL.search(tag)
        have = (rel_m.group(2) if rel_m and rel_m.group(2) is not None
                else (rel_m.group(3) if rel_m else "")) or ""
        values = list(_QUAL) + [v for v in have.split() if v not in _QUAL]
        if have.split() == values:
            return tag
        rel_attr = ' rel="%s"' % " ".join(values)
        if rel_m:
            start, end = rel_m.span()
            return tag[:start] + rel_attr + tag[end:]
        return tag[:-1].rstrip() + rel_attr + ">"

    return _ANCHOR.sub(fix, text)


# ----------------------------------------------------- published-claim rules

# Attributed wording that legitimately contains "invalid":
#  * the third-party tracker sentence CamelCamelCamel/Keepa were quoted as
#    showing ("… you may have searched for an invalid product identifier"),
#    preserved as an observation of someone else's output, never as this site's
#    verdict;
#  * the generic validator description in dashboard/links.html ("invalid input
#    is rejected"), which describes the tool's behaviour, not the links;
#  * the negation in annex-88769516/COORDINATION.md that explicitly refuses the
#    verdict ("NOT proof the requested ASINs are invalid").
ALLOWED_INVALID_PHRASES = (
    "invalid product identifier",
    "invalid input is rejected",
    "not proof the requested asins are invalid",
)

_STRIP_EMPHASIS = re.compile(r"[*_`]")


def claim_violations(text: str) -> list[str]:
    """Return a problem for every published 'invalid' claim outside the allow list.

    Markdown emphasis is stripped first so **invalid product identifier** still
    matches its allow-listed phrase. The check is deliberately blunt on purpose:
    "invalid" is banned as a verdict word in published files, and every
    remaining use must name itself in ALLOWED_INVALID_PHRASES.
    """
    flat = _STRIP_EMPHASIS.sub("", text).lower()
    flat = re.sub(r"\s+", " ", flat)
    for phrase in ALLOWED_INVALID_PHRASES:
        flat = flat.replace(phrase, "")
    if "invalid" not in flat:
        return []
    problems = []
    for m in re.finditer(r"invalid", flat):
        ctx = flat[max(0, m.start() - 60):m.start() + 70]
        problems.append(f'published "invalid" claim outside the allow list: …{ctx}…')
    return problems


# ------------------------------------------------------- disclosure placement

_SCRIPT = re.compile(r"<script\b.*?</script>", re.S | re.I)
_STYLE = re.compile(r"<style\b.*?</style>", re.S | re.I)


def anchor_violations(text: str) -> list[str]:
    """Every product anchor must carry rel="sponsored" (brief; F103)."""
    problems = []
    for tag in _ANCHOR.findall(text):
        href_m = _HREF.search(tag)
        href = (href_m.group(2) if href_m and href_m.group(2) is not None
                else (href_m.group(3) if href_m else ""))
        if not is_product_href(href):
            continue
        rel_m = _REL.search(tag)
        vals = (rel_m.group(2) if rel_m and rel_m.group(2) is not None
                else (rel_m.group(3) if rel_m else "")) or ""
        if "sponsored" not in vals.split():
            problems.append(f"product link without rel=sponsored: {href}")
    return problems


def disclosure_violations(text: str) -> list[str]:
    """Strip under the masthead, sentence repeated in the footer (brief, SG-28).

    Script and style blocks are removed before the sentence is located: the
    dashboard articles page embeds the disclosure sentence inside its JSON-LD
    FAQ, and structured data is not a disclosure strip. The first *rendered*
    occurrence is the one the rule governs.
    """
    problems = []
    rendered = _STYLE.sub("", _SCRIPT.sub("", text))
    low = rendered.lower()
    body = low.find("<body")
    if body < 0:
        return problems
    first = rendered.find(DISCLOSURE)
    header_end = low.find("</header>")
    h1 = low.find("<h1", body)
    if first < 0:
        problems.append("disclosure sentence missing entirely")
    else:
        after_header = header_end < 0 or first > header_end
        if h1 >= 0:
            near_top = first < h1
        else:
            near_top = first < body + 4000
        if not (after_header and near_top):
            problems.append(
                "disclosure sentence is not under the masthead (must follow </header> "
                "when the page has one, and precede the first <h1>; a page with no <h1> "
                "must carry it within 4000 characters of <body>)")
    foot = low.find("<footer")
    foot_end = low.find("</footer>", foot)
    if foot < 0:
        problems.append("page has no footer; the disclosure must repeat in the footer")
    elif DISCLOSURE not in rendered[foot:foot_end if foot_end > 0 else len(rendered)]:
        problems.append("footer does not repeat the disclosure sentence")
    return problems


# ------------------------------------------------------------- the repair

# Exact, dated wording repairs. Each replacement removes a published verdict
# about the supplied links while keeping the underlying observation (9-character
# tokens, 10-character ASIN format per KDP G200652190, no visible tag). The
# strings are frozen-tree text as published before this repair; running
# transform twice is a no-op because none of the old strings survive the pass.
WORDING = [
    # dashboard: verdict badges
    ('<span class="badge bad">Invalid link</span>',
     '<span class="badge">Unresolved</span>'),
    ('<span class="badge bad">Unverified / invalid</span>',
     '<span class="badge">Unverified</span>'),
    ('<span class="badge bad">invalid</span>',
     '<span class="badge">format mismatch</span>'),
    # session-3740f69d: token badges and the data enum behind them
    ('<span class="badge bad">9 chars — invalid ASIN</span>',
     '<span class="badge">9 chars — ASIN format mismatch</span>'),
    ('"invalid_asin_9_chars"', '"unconfirmed_asin_9_chars"'),
    # dashboard: feature and status prose
    ('quarantine of invalid links', 'quarantine of unverified links'),
    ('quarantine of the invalid submitted links',
     'quarantine of the unverified submitted links'),
    ('Invalid links quarantined — users never sent to unverified product pages',
     'Unverified links quarantined — users never sent to unconfirmed product pages'),
    ('no tag, invalid target (flags F03, I-03)',
     'no tag, unconfirmed target (flags F03, I-03)'),
    ('the critical invalid-link finding', 'the unresolved link-status finding'),
    ('<strong>Invalid identifiers</strong>',
     '<strong>Identifier-format mismatch</strong>'),
    ('invalid links quarantined from live CTAs',
     'unverified links quarantined from live CTAs'),
    ('invalid ASIN format (I-01), invalid link',
     'ASIN-format mismatch (I-01), unconfirmed link'),
    # dashboard/flagged.html section heading
    ('A · Critical — supplied product links are invalid (integration session 19a679d8)',
     'A · Critical — supplied product links: status unresolved (integration session 19a679d8)'),
    # annex-88769516: the tracker-result column becomes attributed wording
    ('result: "No record / invalid identifier"',
     'result: "No record; tracker displayed \'invalid product identifier\'"'),
    # dashboard/assets/js/main.js: validator hint
    ('problems.push("ASIN must be exactly 10 letters/digits (the supplied IDs are 9 and invalid).")',
     'problems.push("ASIN must be exactly 10 letters/digits (the supplied IDs are '
     '9 characters; their status is unresolved).")'),
]

# Line-wrapping regexes for sentences that span a newline in the minified-ish
# dashboard markup.
WORDING_RE = [
    (re.compile(r"are demonstrably\s+invalid and quarantined"),
     "are unverified and quarantined"),
]

# An annotation inserted under the rewritten dashboard/flagged.html heading, so
# the historical record stays visible while the withdrawn verdict cannot be read
# as this site's position. Idempotent: skipped when already present.
FLAG_NOTE = (
    '<p class="note">Published 2026-11-19 (arena/e01a0112): this section first '
    'appeared with an adverse verdict on the supplied product links. That verdict '
    'is withdrawn as a published claim. The observations below stand — the '
    '9-character tokens differ from the 10-character ASIN format (KDP G200652190) '
    '— but token length does not determine whether a link works or complies, and '
    'the owner\u2019s brief forbids the claim. The compliance status of the supplied '
    'short links is unresolved: '
    '<a href="https://kanlerxz87-cyber.github.io/Zone3/flagged.html#FLG-003">'
    'Zone3 FLG-003</a>.</p>\n    '
)
FLAG_ANCHOR = ('<h2>A · Critical — supplied product links: status unresolved '
               '(integration session 19a679d8)</h2>\n    ')

FOOTER_P = ('<p class="disclosure-foot"><strong>%s</strong></p>\n' % DISCLOSURE)
DOCS_FOOTER = ('<footer class="mini"><p class="disclosure-foot"><strong>%s</strong>'
               '</p></footer>\n' % DISCLOSURE)


def _relocate_annex_strip(text: str) -> str:
    """Move the annex disclosure strip from above <header> to under the masthead.

    The strip (added 2026-11-14 by integration session sess-cb2cfa7c with its
    provenance comment) sat before <header>, so the page had no disclosure strip
    *under* the masthead as the brief requires. Cut the exact block and re-insert
    it after </header>, comment intact.
    """
    m = re.search(
        r"(<!-- Added by integration session sess-cb2cfa7c.*?</p>\s*)<header",
        text, re.S)
    if not m:
        return text
    block = m.group(1)
    text = text[:m.start()] + "<header" + text[m.end():]
    head_end = text.find("</header>")
    if head_end < 0:
        return text  # let disclosure_violations report it
    insert_at = head_end + len("</header>")
    return text[:insert_at] + "\n" + block.rstrip() + "\n" + text[insert_at:]


def transform(text: str, rel_path: str = "") -> str:
    """Idempotent repair for one frozen-tree file. Never rewrites hrefs."""
    for old, new in WORDING:
        text = text.replace(old, new)
    for rx, new in WORDING_RE:
        text = rx.sub(new, text)

    if "dashboard/flagged.html" in rel_path.replace("\\", "/") and FLAG_NOTE not in text:
        text = text.replace(FLAG_ANCHOR, FLAG_ANCHOR + FLAG_NOTE, 1)

    text = qualify_anchors(text)

    if rel_path.replace("\\", "/").startswith("annex-88769516/"):
        text = _relocate_annex_strip(text)

    if text.endswith((".html", ".htm")) or "<html" in text[:200].lower():
        low = text.lower()
        foot = low.find("<footer")
        foot_end = low.find("</footer>", foot)
        in_footer = foot >= 0 and DISCLOSURE in text[foot:foot_end if foot_end > 0 else len(text)]
        if foot < 0:
            # docs/: bare redirect stubs with no footer at all.
            close = low.rfind("</body>")
            if close >= 0:
                text = text[:close] + DOCS_FOOTER + text[close:]
        elif not in_footer:
            open_end = low.find(">", foot) + 1
            text = text[:open_end] + "\n    " + FOOTER_P + text[open_end:]

    return text


def iter_files(tree: str):
    for base, dirs, files in os.walk(os.path.join(ROOT, tree)):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in sorted(files):
            if name.endswith(CLAIM_SUFFIXES) or name.endswith(".html"):
                yield os.path.join(base, name)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="fail if any frozen file differs from the repaired form")
    args = ap.parse_args()
    changed, checked = [], 0
    for tree in FROZEN_TREES:
        for path in iter_files(tree):
            checked += 1
            with open(path, encoding="utf-8") as fh:
                old = fh.read()
            new = transform(old, os.path.relpath(path, ROOT))
            if new != old:
                if args.check:
                    changed.append(os.path.relpath(path, ROOT))
                else:
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write(new)
                    changed.append(os.path.relpath(path, ROOT))
    if args.check:
        if changed:
            print("historical compliance: %d file(s) differ from the repaired form:"
                  % len(changed))
            for c in changed:
                print("  " + c)
            return 1
        print("historical compliance: %d frozen files match the repaired form" % checked)
        return 0
    print("historical compliance: %d files scanned, %d repaired" % (checked, len(changed)))
    for c in changed:
        print("  repaired " + c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
