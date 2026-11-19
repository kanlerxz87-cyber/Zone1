#!/usr/bin/env python3
"""
Zone1 — static site generator.

No third-party dependencies. Reads data/*.json (the verified dataset) and writes
a flat set of HTML pages. The layout function injects the required Amazon
Associates disclosure into every page, so no page can ship without it.

Run:  python3 build.py
Out:  index.html, products/*.html, categories/*.html, guides/*.html,
      data.html, compare.html, platform.html, compliance.html,
      flagged.html, executive-summary.html, 404.html, assets/style.css
"""

import html
import json
import os
import posixpath
import re
import shutil
from email.utils import format_datetime
from urllib.parse import quote_plus
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
SITE_NAME = "Zone1 Kitchen"
SITE_TAGLINE = "A little clarity for your countertop."
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

# Public origin of the canonical site (GitHub Pages, branch main, root). The sitemap and
# robots.txt generators below already hard-code this; it is named here so canonical URLs,
# Open Graph URLs and structured-data ids cannot drift from the sitemap.
SITE_BASE = "https://kanlerxz87-cyber.github.io/Zone1/"

# --------------------------------------------------------------------------- #
# canonical origin, social card, publisher identity
# --------------------------------------------------------------------------- #
# The published origin is the GitHub Pages site for this repository. data/site.json
# records the same URL; it is repeated here so the generator can build absolute URLs
# (canonical, og:url, JSON-LD) without a network call at build time.
SITE_URL = "https://kanlerxz87-cyber.github.io/Zone1"
# Repository blob root: the evidence link that proves a cited path exists in the tree.
REPO_BLOB = "https://github.com/kanlerxz87-cyber/Zone1/blob/main/"
OG_IMAGE = SITE_URL + "/assets/og-card.png"
# The publisher is the site itself. There is no named individual author on this site,
# so the structured data names the organisation rather than inventing a person.
PUBLISHER = {
    "@type": "Organization",
    "@id": SITE_URL + "/#organization",
    "name": SITE_NAME,
    "url": SITE_URL + "/",
    "logo": OG_IMAGE,
    "description": (
        "An affiliate-funded, documentation-based kitchen buying guide. Every specification "
        "links to the manufacturer's own page or owner's manual; nothing is inferred and "
        "no hands-on testing is claimed."
    ),
    # The disclosure and the non-affiliation statement travel inside the structured
    # data, not only in the page body, so a consumer that reads the data alone still
    # sees them. Adopted from arena/792c279e's implementation.
    "disambiguatingDescription": (
        "Not owned by, endorsed by or sponsored by Amazon.com, Inc. or any brand named "
        "on the site. " + DISCLOSURE
    ),
}

# --------------------------------------------------------------------------- #
# data loading
# --------------------------------------------------------------------------- #

def load(name):
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


SOURCES = load("sources.json")
PRODUCTS = load("products.json")
COMPLIANCE = load("compliance.json")
MARKETING = load("marketing.json")
PLATFORM = load("platform.json")
ANALYTICS_PLAN = load("analytics-plan.json")
CAMPAIGN_LEDGER = load("campaign-ledger.json")
MEASUREMENT = load("measurement.json")
PRODUCT_INTENT = load("product-intent.json")
SITE_CONFIG = load("config.json")

# Outbound-click counter switch (added 2026-11-17, session 79743fd2). The switch lives in
# data/config.json so that the footer's cookie/third-party statement and the
# behaviour the page actually ships are generated from one source and cannot
# drift apart. Program Policies section 3(e) requires that statement to be
# accurate; a hand-typed sentence is how it goes stale.
ANALYTICS = SITE_CONFIG.get("analytics") or {}
ANALYTICS_ENABLED = bool(ANALYTICS.get("enabled"))
ANALYTICS_ENDPOINT = (ANALYTICS.get("endpoint") or "").strip()
ANALYTICS_EVENTS = [x.strip() for x in (ANALYTICS.get("events") or []) if x.strip()]
# The counter only runs when it has somewhere to send to. An enabled flag with
# no endpoint is a configuration error, not a mode: the build guard refuses it.
ANALYTICS_ON = ANALYTICS_ENABLED and bool(ANALYTICS_ENDPOINT)
# Additive re-verification ledger (2026-11-14 pass, sess-81495d2d). Rendered as its own
# page; nothing else in the build depends on it, so a future pass can replace the file
# without touching the generators below.
REVERIFICATION = load("reverification.json")
# Additive pass-6 ledger (2026-11-14, sess-54c66535): re-opens the nine rows the earlier
# pass could not re-check. Owned entirely by this session's folder, so a future pass can
# drop the file without touching anything else; the page simply omits the section.
_p6 = ROOT / "session-54c66535" / "pass6.json"
PASS6 = json.loads(_p6.read_text(encoding="utf-8")) if _p6.exists() else None
# Additive pass-7 ledger (2026-11-14, arena-052f2c9f): independent re-verification round 7.
# Owned entirely by this session's folder; the page omits the section if the file is absent.
_p7 = ROOT / "session-052f2c9f" / "pass7.json"
PASS7 = json.loads(_p7.read_text(encoding="utf-8")) if _p7.exists() else None
# Additive pass-9 ledger (2026-11-15, arena/88bb2db6): the final-integration re-read.
# Same additive pattern as passes 6 and 7 - owned entirely by this session's folder,
# so a later session can drop the file without touching anything else.
_p9 = ROOT / "session-88bb2db6" / "pass9.json"
PASS9 = json.loads(_p9.read_text(encoding="utf-8")) if _p9.exists() else None
# Additive round-10 targeted live-source follow-up (2026-11-16, arena/9f0e6668).
# This is deliberately scoped: it refreshes dated volatile brand counters and records
# current link/policy observations without claiming a full re-read of every product row.
_p10 = ROOT / "session-9f0e6668" / "pass10.json"
PASS10 = json.loads(_p10.read_text(encoding="utf-8")) if _p10.exists() else None
# Additive pass-10 ledger (2026-11-16, arena/9fccce0c-zone1): the tenth independent
# re-read. Same additive pattern - the file is owned by this session's folder and the
# page simply omits the section if the file is absent. Named _p10u2/PASS10_U2 because
# arena/9f0e6668 already owns the round-10 follow-up ledger above.
_p10u2 = ROOT / "session-9fccce0c" / "pass10.json"
PASS10_U2 = json.loads(_p10u2.read_text(encoding="utf-8")) if _p10u2.exists() else None
# Additive pass-10 full source ledger (2026-11-16, arena/695f03b7-zone1): every
# registered source in data/sources.json re-read live, one row per source, rendered
# as its own page by page_pass10(). Owned by this session; if the file is ever
# removed the page renders nothing rather than failing the build.
_p10full = ROOT / "data" / "pass10.json"
PASS10_FULL = json.loads(_p10full.read_text(encoding="utf-8")) if _p10full.exists() else None
# Additive spot ledger (2026-11-16, arena/8874422b-zone1): a second independent reader's
# targeted re-read of the load-bearing rows the same day — the three supplied short links,
# the two volatile Chefman counters, the Emeril preset conflict and the Program Policies
# stamp. Round 11 and pass 12 (492acddc) re-read the wider register earlier that day; this
# file deliberately covers only the subset a second reader should confirm fresh. Owned by
# this session's folder; the re-verification page omits the section if the file is absent.
_p12 = ROOT / "session-8874422b" / "pass12.json"
PASS12 = json.loads(_p12.read_text(encoding="utf-8")) if _p12.exists() else None

# Decision layer (added 2026-11-15, arena/3ddfa50e). Two registers that exist to be reviewed
# rather than acted on: the suggestions queue and the open-questions register. Both are
# generated from JSON so a reviewer edits data, never a template.
DECISION = load("decision.json")
SUGGESTIONS = load("suggestions.json")
QUESTIONS = load("questions.json")
# Owner decision record (added 2026-11-16, arena/ba29c641): the write-side of the suggestions
# review. choices[] is empty until an owner actually decides something, and no session may fill
# it on their behalf - a default is not an instruction.
DECISION_LOG = load("decision-log.json")
SUG_BY_ID = {s["id"]: s for s in SUGGESTIONS["suggestions"]}
# Design/content/traffic suggestion layer (added 2026-11-15, arena/bf487400-zone1).
# The paste-ready design prompt plus the D/A/T/V/R registers, generated from JSON so the
# owner reviews data, never a template. Statuses describe the repository as built.
DESIGN_PROMPT = load("design-prompt.json")
PUBLICATION = load("publication.json")
BUYING_BY_SLUG = {row["slug"]: row for row in PUBLICATION["products"]}


SRC_BY_ID = {s["id"]: s for s in SOURCES["sources"]}
ACCESSED = SOURCES["accessed"]
# Date of the most recent line-by-line re-read of the published values (see reverification.html).
REVERIFIED = SOURCES.get("reverified") or ""
PRODUCT_LIST = PRODUCTS["products"]


def e(text):
    """Escape for HTML text nodes and attributes."""
    return html.escape(str(text), quote=True)


def src_link(sid):
    """A single inline source badge linking to the official page."""
    s = SRC_BY_ID.get(sid)
    if not s:
        return f'<span class="src src-bad">unknown source {e(sid)}</span>'
    return (
        f'<a class="src" href="{e(s["url"])}" title="{e(s["org"])} — {e(s["title"])}" '
        f'rel="noopener" target="_blank">{e(sid)}</a>'
    )


def src_links(ids):
    if not ids:
        return '<span class="src src-none">no official source</span>'
    return " ".join(src_link(i) for i in ids)


def format_glyph(kind):
    """Hand-drawn stroke-only SVG glyphs for the three air-fryer formats.

    Added by pass 12 (2026-11-16, session 492acddc) as the landing page's only
    artwork. Original line art drawn for this site — no external image, no brand
    asset, no photograph — so the no-first-party-imagery stance is preserved and
    verify.py's host allow-list is untouched. Purely decorative (aria-hidden).
    """
    head = ('<svg class="glyph" viewBox="0 0 76 46" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            'aria-hidden="true" focusable="false">')
    dot = ('<circle cx="{cx}" cy="9" r="1.6" fill="currentColor" stroke="none"/>')
    body = {
        # Two independent baskets: one housing, centre divider, two drawer fronts.
        "dual": (
            '<rect x="4" y="14" width="68" height="26" rx="6"/>'
            '<line x1="38" y1="14" x2="38" y2="40"/>'
            '<rect x="10" y="21" width="22" height="12" rx="3"/>'
            '<rect x="44" y="21" width="22" height="12" rx="3"/>'
            '<line x1="17" y1="27" x2="25" y2="27"/>'
            '<line x1="51" y1="27" x2="59" y2="27"/>'
        ),
        # French-door oven: wide body, control strip, two door panes with bars.
        "oven": (
            '<rect x="4" y="10" width="68" height="30" rx="4"/>'
            '<line x1="10" y1="17" x2="66" y2="17"/>'
            '<line x1="38" y1="17" x2="38" y2="40"/>'
            '<line x1="33" y1="24" x2="33" y2="33"/>'
            '<line x1="43" y1="24" x2="43" y2="33"/>'
            '<line x1="11" y1="40" x2="11" y2="44"/>'
            '<line x1="65" y1="40" x2="65" y2="44"/>'
        ),
        # Single large basket: tall body, one drawer, side handle.
        "single": (
            '<rect x="12" y="6" width="52" height="34" rx="6"/>'
            '<rect x="21" y="21" width="26" height="12" rx="3"/>'
            '<line x1="47" y1="27" x2="58" y2="27"/>'
            '<line x1="19" y1="40" x2="19" y2="44"/>'
            '<line x1="57" y1="40" x2="57" y2="44"/>'
        ),
    }
    dots = "".join(dot.format(cx=cx) for cx in (28, 36, 44, 52))
    return head + dots + body[kind] + "</svg>"


# --------------------------------------------------------------------------- #
# structured data (JSON-LD) and social cards
# --------------------------------------------------------------------------- #
# Added 2026-11-15 (arena/88bb2db6). The site previously shipped no canonical URL, no
# Open Graph / Twitter card tags and no JSON-LD at all, so a shared link rendered as a
# bare URL and no page could qualify for a rich result. These helpers build that layer
# from the same verified data the pages already display.
#
# Two rules govern what may go in the structured data:
#   1. No price, priceCurrency, availability or aggregateRating. Program Policies
#      section 2(b) and 6(t) restrict those to an Amazon-served link or the
#      Creators/PA API, and this site holds neither. check_no_price_tracking()
#      below fails the build if a price-tracking identifier appears in any script
#      body, which now includes every JSON-LD block.
#   2. No rating. The brand-site review widget rating is not Amazon's rating and is
#      not a schema.org aggregateRating for the product.

def jsonld(blocks):
    """Render JSON-LD blocks for the <head>.

    The blocks are emitted as one @graph inside an object carrying an explicit
    "@context". Both parts matter:

      * @context tells a consumer that the node types are schema.org types. Without
        it, a bare array of nodes is ambiguous.
      * @graph lets the blocks reference each other by @id, so an Article can point
        at the publisher node instead of duplicating the publisher's details.

    `</` is escaped so a string containing it can never close the script element.
    """
    if not blocks:
        return ""
    payload = json.dumps({"@context": "https://schema.org", "@graph": blocks},
                         ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    return f'<script type="application/ld+json">{payload}</script>'


def page_url(page_rel):
    """Absolute URL of a generated page, for canonical and og:url."""
    return f"{SITE_URL}/{page_rel}"


def breadcrumbs_jsonld(trail):
    """BreadcrumbList for the trail of (name, url) pairs, Home first."""
    items = []
    for i, (name, url) in enumerate(trail, start=1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "name": name,
            "item": url,
        })
    return {
        "@type": "BreadcrumbList",
        "@id": SITE_URL + "/#breadcrumb",
        "itemListElement": items,
    }


def article_jsonld(a, url):
    """Article schema for one article in data/articles.json.

    Only facts the site already publishes are used. The article's own record is the
    source of the headline, the standfirst and the reading time; the dates are the
    dates recorded in data/articles.json, not invented ones.
    """
    node = {
        "@type": "Article",
        "@id": url + "#article",
        "headline": a["title"],
        "description": a["standfirst"],
        "articleSection": a["kind"],
        "inLanguage": "en-US",
        "author": {"@id": SITE_URL + "/#organization"},
        "publisher": {"@id": SITE_URL + "/#organization"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "image": OG_IMAGE,
        "url": url,
        "isAccessibleForFree": True,
    }
    if a.get("published_at"):
        node["datePublished"] = a["published_at"]
    if a.get("modified_at"):
        node["dateModified"] = a["modified_at"]
    return node


def uniq(seq):
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


REPO_URL = "https://github.com/kanlerxz87-cyber/Zone1"


def repo_link(path, label=None):
    """Link to a file or folder in this repository on GitHub.

    Used only for facts about the repository itself (its own irregularities and
    builds). GitHub is the official host for those files, so they count as a source.
    """
    kind = "tree" if path.endswith("/") else "blob"
    url = f"{REPO_URL}/{kind}/main/{path.rstrip('/')}"
    return (f'<a href="{e(url)}" target="_blank" rel="noopener">'
            f'{e(label or path)} ↗</a>')


def governed_by(guardrail_ids):
    """Source badges for the registered sources a platform guardrail cites."""
    ids = []
    for g in PLATFORM["guardrails"]:
        if g["id"] in guardrail_ids:
            ids.extend(g["source"])
    return src_links(uniq(ids))


# Which guardrail governs each human/automated operating policy on platform.html.
AUTOMATION_GOVERNANCE = {
    "Broken link detection": "G5",          # link placement and integrity (S2, S6)
    "Fact-table verification": "G2",        # no published claim without an official source (S2, S8)
    "Content drafting": "G7",               # no experience claims, no invented testing (S8)
    "Click/conversion reporting": "G6",     # Program Content is never an analytics input (S2)
    "Publication decision": "G9",           # disclosure is unremovable (S1, S5)
}


def flag_pill(state):
    return {
        "verified": '<span class="pill pill-ok">Verified</span>',
        "unverified": '<span class="pill pill-warn">Unverified</span>',
        "conflict": '<span class="pill pill-bad">Conflict</span>',
    }[state]


def depth_prefix(page_path):
    """Relative prefix so nested pages resolve assets and links correctly."""
    parts = Path(page_path).parts
    return "../" * (len(parts) - 1)


# --------------------------------------------------------------------------- #
# page inventory (used for nav + link checking)
# --------------------------------------------------------------------------- #

NAV = [
    ("index.html", "Home", "A clear guide to three air-fryer formats"),
    ("picks.html", "Format guide", "Three documented formats, with their trade-offs"),
    ("product-intent.html", "Product intent & ledger", "Intended listings kept apart from observed redirects; empty campaign ledger"),
    ("measurement.html", "Measurement plan", "Five event definitions, reporting cadence, and deployment gate"),
    ("decisions.html", "Decisions & handover", "Niche, traffic, measurement, and the five things only you can do"),
    ("handover.html", "Account-holder handover", "Account-only actions, with exact discovery steps"),
    ("categories/kitchen-appliances.html", "Category: Kitchen", "All tracked products in one category"),
    ("compare.html", "Comparison", "Verified-only side-by-side matrix"),
    ("guides/buying-guide-air-fryers.html", "Buying guide", "How to choose a form factor"),
    ("articles/index.html", "Articles", "Sourced reads — comparisons, explainers, policy"),
    ("clusters.html", "Article clusters", "The four questions the set is filed under"),
    ("data.html", "Full dataset", "Every field, value, source and gap"),
    ("platform.html", "Platform blueprint", "The automation and compliance design"),
    ("compliance.html", "Compliance", "Program rules, quoted, with sources"),
    ("flagged.html", "Flagged for review", "Unverified values and irregularities"),
    ("suggestions.html", "Suggestions", "Review site improvements before implementation"),
    # Added 2026-11-16 (arena/ba29c641): the queue had 21 rows and no way to close one.
    ("decision-log.html", "Owner decision log", "Pick a path per suggestion, or let the stated default stand"),
    ("design-prompt.html", "Design prompt pack", "Design, topics and tactics — review before changes"),
    ("questions.html", "Questions and gaps", "Known facts, missing answers and discovery steps"),
    ("requirements.html", "Requirements and status", "Every requirement in the brief, and whether this repo meets it"),
    # Added 2026-11-15 by arena/63a2c638: the editorial and traffic plan. It sits with the
    # decision pages because nothing on it has been written yet - it is a proposal queue,
    # the same way suggestions.html is an implementation queue.
    ("topics.html", "Content and traffic plan", "Article topics and the channels allowed to promote them"),
    ("executive-summary.html", "Executive summary", "Decision-ready briefing"),
    # Added by the 2026-11-14 integration pass: the line-by-line re-read ledger.
    ("reverification.html", "Re-verification", "Published values re-read against their official sources"),
    # Added 2026-11-16 by arena/695f03b7-zone1: the full source-by-source re-read ledger,
    # one row per registered source with its official link and the 2026-11-16 observation.
    ("pass10.html", "Verification pass 10", "All 34 official sources re-read on 2026-11-16"),
    # Added 2026-11-16 by arena/695f03b7-zone1: data-driven diagrams generated from
    # data/products.json at build time; diagrams only, because photography rights are open.
    ("figures.html", "Figures and diagrams", "Four diagrams generated from the published dataset"),
    # All parallel-session builds are now reached through one page rather than six sidebar
    # entries (2026-11-14, arena/6b2eddeb). Six entries in the main nav made a reader choose
    # between six answers to the same question; flag F35 records why that was a problem.
    # NAV still lists them so the link checker keeps covering every published page.
    ("previous-passes.html", "Previous passes", "Every parallel build in this repo, and which one is canonical"),
    ("research/index.html", "Deep-dive research", "Independent 25-source verification pass (research/)"),
    ("session-3740f69d/index.html", "Session 3740f69d build", "Independent dashboard build (session-3740f69d/)"),
    ("s2/index.html", "Verified platform pass", "Compliance matrix and verification log (s2/)"),
    ("site/index.html", "Verification annex", "382-assertion verifier over data/verified/ (site/)"),
    ("dashboard/index.html", "Campaign dashboard", "Niches, commissions, links and tracking views (dashboard/)"),
    ("docs/index.html", "Legacy docs build", "Retired build kept for its evidence (docs/)"),
    ("annex-88769516/index.html", "Annex 88769516", "Independent annex build (annex-88769516/)"),
]

NAV_LABEL = {}  # filled from NAV below DESK_NAV


# Every owner / verification surface, in the order the "Behind the site" group and the
# footer list them. check_desk_nav() fails the build if a NAV page that is neither a reader
# page nor a parallel build is missing from here, so a new dashboard cannot be orphaned.
DESK_NAV = [
    "executive-summary.html",
    "suggestions.html",
    "questions.html",
    "decision-log.html",
    "decisions.html",
    "handover.html",
    "product-intent.html",
    "measurement.html",
    "topics.html",
    "design-prompt.html",
    "requirements.html",
    "compliance.html",
    "flagged.html",
    "data.html",
    "reverification.html",
    "pass10.html",
    "figures.html",
    "clusters.html",
    "platform.html",
]
NAV_LABEL.update({href: label for href, label, _sub in NAV})


def json_ld(page_rel, title, description):
    """Structured data for a generated page — and a deliberate omission.

    Emitted: WebSite + publisher on the home page, Article on article pages, and a
    BreadcrumbList tying every subpage to the home page. That is metadata this build can
    state truthfully from data it already holds.

    NOT emitted: schema.org Product / Offer / AggregateRating. Amazon prices, availability
    and star ratings are deliberately absent from this site (Program Policies §2(b) and
    §6(t), see data/products.json → amazon_price_policy). Structured data is read by search
    engines and rich-result systems as a factual assertion, so a Product block without a
    price, or with an invented one, would either be useless or would assert a number this
    project has explicitly refused to publish. Manufacturer list prices are real but are not
    Amazon offers, so they are not marked up as offers either.
    """
    canonical = SITE_BASE + ("" if page_rel == "index.html" else page_rel)
    graph = []
    if page_rel == "index.html":
        graph.append({
            "@type": "WebSite",
            "@id": SITE_BASE + "#website",
            "url": SITE_BASE,
            "name": SITE_NAME,
            "description": description or SITE_TAGLINE,
            "inLanguage": "en-US",
            "publisher": {"@id": SITE_BASE + "#publisher"},
        })
    graph.append({
        "@id": canonical + "#publisher",
        "@type": "Organization",
        "name": SITE_NAME,
        "url": SITE_BASE,
        "description": ("Independent Amazon Associates publisher. Documentation-based "
                        "product comparison; no hands-on testing is claimed."),
        "disambiguatingDescription": (
            "Not owned by, endorsed by or sponsored by Amazon.com, Inc. or any brand named "
            "on the site. " + DISCLOSURE),
    })
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Home",
               "item": SITE_BASE}]
    parts = page_rel.split("/")[:-1]
    for i, part in enumerate(parts, start=2):
        crumbs.append({"@type": "ListItem", "position": i,
                       "name": part.replace("-", " ").title(),
                       "item": SITE_BASE + "/".join(parts[:i - 1]) + "/"})
    if len(crumbs) > 1:
        graph.append({"@type": "BreadcrumbList", "itemListElement": crumbs})
    if page_rel.startswith("articles/"):
        graph.append({
            "@type": "Article",
            "headline": title,
            "description": description or "",
            "mainEntityOfPage": {"@id": canonical},
            "isPartOf": {"@id": SITE_BASE + "#website"},
            "publisher": {"@id": canonical + "#publisher"},
            "inLanguage": "en-US",
        })
    payload = {"@context": "https://schema.org", "@graph": graph}
    return ('<script type="application/ld+json">'
            + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
            + "</script>\n")


# --------------------------------------------------------------------------- #
# layout
# --------------------------------------------------------------------------- #

CSS = (ROOT / "publication" / "theme.css").read_text(encoding="utf-8")

JS = (ROOT / "publication" / "site.js").read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# The outbound-click counter (2026-11-17, session 79743fd2).
#
# The brief asks for click and conversion measurement "before writing anything
# else", and requirement E-03 was still `not_delivered`: data/measurement.json
# defined five events precisely and shipped no code at all. This file is that
# code. It is deliberately small, dependency-free and inert unless the build
# writes a script tag carrying a data-endpoint attribute.
#
# What it must never do, and how each rule is enforced:
#   - Set a cookie or a persistent identifier  -> it never writes to
#     document.cookie, localStorage, sessionStorage or indexedDB. The build
#     guard check_analytics_consistency() greps this file for those tokens and
#     fails the build if one appears.
#   - Record an IP address, a user agent or a referrer -> the payload is built
#     from four or five named fields and nothing else. The guard greps for
#     navigator.userAgent and document.referrer for the same reason.
#   - Manufacture a click (Program Policies 3(s)) -> an event is sent only
#     inside a `click` listener that requires event.isTrusted, a primary
#     button, and a target that is an Amazon product link. Nothing fires on
#     load, on scroll alone, or from a synthetic dispatchEvent.
#   - Get in the way of the reader -> the handler never calls
#     preventDefault(), never stops propagation and never rewrites the href.
#     The click goes to Amazon whether or not the beacon was accepted.
#
# Why it is disabled by default: a counter with no sink behind it would report
# a number this site cannot source. data/config.json -> analytics holds the
# switch, and the footer's cookie sentence is generated from the same block, so
# the sentence can never describe a behaviour the page does not have (Program
# Policies 3(e)).
# --------------------------------------------------------------------------- #

# One reviewed source for the browser client; the generated asset is byte-identical.
ANALYTICS_JS = (ROOT / "analytics" / "client.js").read_text(encoding="utf-8")



def privacy_html():
    """State actual collection behaviour, including the host's separate security logs."""
    if ANALYTICS_ON:
        state = (
            "It loads one small script of its own on reader pages. It sends page views, "
            "reader-initiated product clicks, a coarse active-reading bucket and comparison "
            "interactions to a same-origin collector. Payloads contain only allow-listed page "
            "and product IDs or the fixed reading bucket; the application stores daily totals, "
            "not visitor-level records. Cookies, persistent IDs, referrers and query strings "
            "are not read or sent by this script. Do Not Track and Global Privacy Control "
            "are respected. Orders are imported only from authorised first-party reports."
        )
    else:
        state = (
            "This site sets no cookies itself, runs no analytics, and sends no measurement "
            "events. The self-hosted collector is implemented and tested, but is not deployed "
            "on this GitHub Pages site. Browser collection is disabled."
        )
    return (
        '<p>' + state + '</p>'
        '<p>GitHub Pages separately logs visitor IP addresses for security. This publisher '
        'does not control those host logs. '
        '<a href="https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection" '
        'target="_blank" rel="noopener">GitHub’s hosting notice</a>. '
        'Following an Amazon link takes you to Amazon, where its own privacy and cookie '
        'practices apply. Workspace decision drafts, if used, stay in your browser’s local '
        'storage until cleared; they are not sent to a server.</p>'
    )



PUBLIC_INDEX_PAGES = {
    "index.html",
    "picks.html",
    "compare.html",
    "categories/kitchen-appliances.html",
    "guides/buying-guide-air-fryers.html",
    "articles/index.html",
    "compliance.html",
    "clusters.html",
    "about.html",
}


def is_indexable_page(page_rel):
    """Only buyer-facing canonical publication pages enter the root sitemap."""
    if page_rel in {"404.html", "categories/cooking-thermometers.html"}:
        return False
    return (
        page_rel in PUBLIC_INDEX_PAGES
        or page_rel.startswith("products/") and page_rel.endswith(".html")
        or page_rel.startswith("articles/") and page_rel.endswith(".html")
        or page_rel.startswith("guides/") and page_rel.endswith(".html")
        or page_rel.startswith("categories/") and page_rel.endswith(".html")
    )


def analytics_page_type(page_rel):
    if page_rel == "articles/index.html":
        return "listing"
    if page_rel.startswith("articles/"):
        return "article"
    if page_rel.startswith("guides/"):
        return "guide"
    if page_rel.startswith("products/"):
        return "product"
    return "page"


def layout(page_rel, title, body, active=None, description="", og_type="website",
           jsonld_blocks=None, og_image_alt=None):
    """One publication masthead, below-masthead disclosure and native workspace menu."""
    from string import Template
    prefix = depth_prefix(page_rel)
    body = body.replace('<div class="tablewrap">', '<div class="tablewrap" tabindex="0" role="region" aria-label="Scrollable data table">')
    canonical = SITE_BASE if page_rel == "index.html" else page_url(page_rel)
    def navlink(href, label):
        current = ' class="active" aria-current="page"' if active == href else ""
        return f'<a href="{prefix}{href}"{current}>{e(label)}</a>'
    topnav = "".join(navlink(href, label) for href, label in (
        ("categories/kitchen-appliances.html", "Air fryers"),
        ("categories/cooking-thermometers.html", "Thermometers"),
        ("articles/index.html", "Buying guides"),
        ("compare.html", "Compare"),
    ))
    workspace_items = (
        ("executive-summary.html", "Executive summary & index"),
        ("suggestions.html", "Suggestions decision queue"),
        ("questions.html", "Questions, known facts & gaps"),
        ("decision-log.html", "Decision drafts & export"),
        ("product-intent.html", "Product intent & campaign ledger"),
        ("measurement.html", "Measurement contract"),
        ("design-prompt.html", "Design & editorial brief"),
        ("topics.html", "Publishing & search plan"),
        ("requirements.html", "Requirements & status"),
        ("platform.html", "Automation blueprint"),
        ("handover.html", "Account-only handover"),
        ("decisions.html", "Strategy background"),
        ("flagged.html", "Flagged for review"),
        ("data.html", "Dataset & official sources"),
        ("compliance.html", "Disclosure & link policy"),
        ("pass10.html", "Prior source-read ledger"),
        ("figures.html", "Diagrams & image notes"),
        ("clusters.html", "Article cluster map"),
        ("reverification.html", "Verification history"),
        ("previous-passes.html", "Historical builds & annexes"),
    )
    analytics_tag = ""
    if ANALYTICS_ON and is_indexable_page(page_rel):
        targets = [p["slug"] for p in PRODUCT_LIST] + [r["id"] for r in PRODUCT_INTENT["rows"]]
        analytics_tag = (
            f'<script src="{prefix}assets/analytics.js" data-enabled="true" '
            f'data-endpoint="{e(ANALYTICS_ENDPOINT)}" '
            f'data-events="{e(",".join(ANALYTICS_EVENTS))}" '
            f'data-target-ids="{e(",".join(targets))}" defer></script>')
    indexable = is_indexable_page(page_rel)
    page_kind = ("home" if page_rel == "index.html" else
                 "article" if page_rel.startswith("articles/") and page_rel != "articles/index.html" else
                 "reader" if indexable or page_rel == "404.html" else "workspace")
    search_token = (SITE_CONFIG.get("search_console_verification") or "").strip()
    search_tag = f'<meta name="google-site-verification" content="{e(search_token)}">' if search_token else ""
    result = Template((ROOT / "publication" / "layout.html.tpl").read_text(encoding="utf-8")).substitute(
        prefix=prefix, full_title=e(f"{title} · {SITE_NAME}"), site_name=e(SITE_NAME),
        description=e(description or SITE_TAGLINE), canonical=e(canonical),
        canonical_tag=(f'<link rel="canonical" href="{e(canonical)}">' if page_rel != "404.html" else ""),
        robots="index,follow,max-image-preview:large" if indexable else "noindex,follow",
        og_type=e(og_type), og_image=e(OG_IMAGE),
        og_alt=e(og_image_alt or "Zone1 Kitchen — thoughtful kitchen buying guides; decorative kitchen scene"),
        jsonld=jsonld(jsonld_blocks), body_class="page-" + page_kind,
        page_id=e(page_rel.removesuffix(".html")), page_type=e(analytics_page_type(page_rel)),
        topnav=topnav, workspace_links="".join(navlink(*item) for item in workspace_items),
        footer_workspace="".join(f'<li>{navlink(*item)}</li>' for item in workspace_items),
        analytics_eligible=str(indexable).lower(), disclosure=e(DISCLOSURE), privacy=privacy_html(), analytics_tag=analytics_tag,
        workspace_status=('<div class="workspace-status">OWNER WORKSPACE <span aria-hidden="true">/</span> '
                          'Public evidence and decisions · not a reader buying guide</div>' if page_kind == "workspace" else ""),
        search_console_tag=search_tag, body=body.strip(),
    )
    def arrow_icon(match):
        rotate = {"→": "", "↗": ' style="transform:rotate(-45deg)"', "↓": ' style="transform:rotate(90deg)"'}[match.group(1)]
        return ('<svg class="icon-arrow" width="15" height="15" viewBox="0 0 20 20" fill="none" '
                f'aria-hidden="true"{rotate}><path d="M3 10h13m-5-5 5 5-5 5" '
                'stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    result = re.sub(r'<span aria-hidden="true">([→↗↓])</span>', arrow_icon, result)
    if page_rel == "404.html":
        def absolute(match):
            attr, url = match.group(1), match.group(2)
            if url.startswith(("#", "http://", "https://", "data:", "mailto:", "//")):
                return match.group(0)
            return f'{attr}="{SITE_URL}/{url.lstrip("/")}"'
        result = re.sub(r'(href|src)="([^"]+)"', absolute, result)
    return "\n".join(line.rstrip() for line in result.splitlines()) + "\n"


# --------------------------------------------------------------------------- #
# reusable fragments
# --------------------------------------------------------------------------- #

def product_cta(p, prefix=""):
    return f"""<div class="cta-row"><a class="btn" href="{e(p['link'])}" target="_blank" rel="sponsored nofollow noopener" data-analytics-event="outbound_click" data-analytics-target-id="{e(p['slug'])}">View on Amazon — check model <span aria-hidden="true">↗</span></a></div>
<p class="cta-note"><strong>Paid link — we may earn a commission.</strong> Affiliate link · intended listing and attribution unconfirmed. The submitted link has an observed destination, not a verified model match. Check the exact listing before buying. <a href="{prefix}product-intent.html">Link notes</a>. {src_links(['S2','S41'])}</p>"""



# --------------------------------------------------------------------------- #
# shopfront merchandising (added 2026-11-17, arena/fd9778a1-zone1)
# --------------------------------------------------------------------------- #
# Two cells per product, and both are quotations of rows this site already
# publishes about that product: "Best for" names a feature the manufacturer's
# own document states, "Check first" names the open conflict on the same page.
# No performance, comfort, durability or taste claim appears here — not because
# copywriting forbids it, but because no such fact exists in the register: a
# hands-on claim would need a test, and no test was run (S8).
MERCH = {
    "chefman-6qt-dual-basket": {
        "best_for": ("Cooking two dishes at two settings on one appliance. The manual documents two "
                     "independent 3-quart baskets, each with its own time and temperature, and a "
                     "Sync Finish function that starts the shorter cook late so both baskets land together.",
                     ["S10", "S18"], "articles/sync-finish-explained.html", "How Sync Finish works →"),
        "check_first": ("Chefman sells more than one 6-quart dual-basket SKU with near-identical "
                        "specifications, and the model this page describes is the dual-window one. "
                        "Read the model number on the appliance before treating any figure here as yours.",
                        ["S10", "S11", "S27"], "flagged.html#f2", "Flag F2 →"),
    },
    "emeril-26qt-french-door": {
        "best_for": ("A whole chicken, a 26-quart cavity and a mode list that reaches below 200 °F. "
                     "The manual documents a 75–500 °F range, a rotisserie spit set and seven "
                     "accessories, which is what separates it from a basket unit with a bigger box.",
                     ["S14", "S15"], "articles/rotisserie-at-home.html", "What the rotisserie claim covers →"),
        "check_first": ("The brand's own page disagrees with itself on the preset count (25 in its "
                        "specification block, 24 in its description and in the Amazon listing title), "
                        "and the listing's model code differs from the brand page by one character.",
                        ["S14", "S15", "S28"], "flagged.html#f4", "Flags F4 and F5 →"),
    },
    "chefman-8qt-turbofry": {
        "best_for": ("One large single basket for everyday batches. The brand page lists an 8 qt "
                     "basket, four one-touch presets, an LED shake reminder and a top-rack "
                     "dishwasher-safe basket and rack.",
                     ["S12", "S13"], "articles/air-fryer-capacity-guide.html", "Is 8 qt the right size? →"),
        "check_first": ("The Amazon listing title advertises a 450 °F Hi-Fry mode; the brand page for "
                        "the model this site maps it to documents 200–400 °F. Those are probably two "
                        "machines, and which one the ASIN ships is unresolved.",
                        ["S12", "S29", "S26"], "flagged.html#f3", "Flag F3 →"),
    },
}


def merch_pair(p, prefix="", mode="card"):
    """The two merchandising cells for one product, built from MERCH + the register.

    mode="card" renders one definition list with two rows (the front-page product card);
    mode="strip" renders two separate boxes (the product page, which has the room).
    """
    m = MERCH.get(p["slug"])
    if not m:
        return ""
    cells = []
    for key, label in (("best_for", "Best for"), ("check_first", "Check first")):
        text, srcs, link, link_label = m[key]
        inner = (f'{e(text)}<span class="tiny"> {src_links(srcs)} '
                 f'<a href="{prefix}{link}">{e(link_label)}</a></span>')
        if mode == "strip":
            cells.append(f'<dl class="vs"><dt>{label}</dt><dd>{inner}</dd></dl>')
        else:
            cells.append(f'<div><dt>{label}</dt><dd>{inner}</dd></div>')
    if mode == "strip":
        return "".join(cells)
    return f'<dl class="merch">{"".join(cells)}</dl>'


def price_line(p, prefix=""):
    snapshot = p["pricing"]["brand_list_price"]
    return (f'<p class="price-line"><b>{e(snapshot["v"])}</b> · brand list-price snapshot '
            f'{src_links(snapshot["s"])}<span class="pl-note">Not an Amazon price or a current retailer quote. '
            f'This site has no authorised live price integration; check the listing for today’s terms. '
            f'<a href="{prefix}compliance.html">Our content policy</a>.</span></p>')
def spec_table(p, prefix=""):
    rows = []
    for s in p["specs"]:
        if s["value"] is None:
            rows.append(
                f'<tr><td>{e(s["label"])}</td>'
                f'<td class="blank">— not confirmed —</td>'
                f'<td>{flag_pill("unverified")}<div class="tiny muted" style="margin-top:.3rem">{e(s["unverified"])}</div>{src_links(s["source"])}</td></tr>'
            )
        else:
            rows.append(
                f'<tr><td>{e(s["label"])}</td>'
                f'<td>{e(s["value"])}'
                + (f'<div class="tiny muted" style="margin-top:.25rem">{e(s["note"])}</div>' if s.get("note") else "")
                + f'</td>'
                f'<td>{flag_pill(s.get("status", "verified"))} {src_links(s["source"])}</td></tr>'
            )
    return f"""
<div class="tablewrap">
<table>
  <caption>Verified specifications — {e(p['short_name'])}</caption>
  <thead><tr><th style="width:26%">Field</th><th style="width:40%">Value</th><th style="width:34%">Official source / status</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
</div>
<p class="tablewrap-hint">The table is wider than the screen — scroll it sideways to reach the source column.</p>
"""


def commercial_table():
    rows = []
    for p in PRODUCT_LIST:
        rate = p["commission"]["rate_confirmed"]
        rate_value = (
            e(rate) if rate else
            '<span class="blank">— not confirmed —</span> ' + flag_pill("unverified")
        )
        rate_cell = f'{rate_value} {src_link("S3")}'
        rows.append(
            f'<tr>'
            f'<td><a href="products/{p["slug"]}.html">{e(p["short_name"])}</a></td>'
            f'<td>{e(p["brand"])}</td>'
            f'<td>{e(p["pricing"]["brand_list_price"]["v"])} '
            f'<span class="tiny muted">brand list price</span> {src_links(p["pricing"]["brand_list_price"]["s"])}</td>'
            f'<td class="blank">not displayed {src_link("S2")}</td>'
            f'<td>{rate_cell}</td>'
            f'<td>{e(p["reviews"]["brand_site_rating"]["v"])} {src_links(p["reviews"]["brand_site_rating"]["s"])}</td>'
            f'<td><a href="flagged.html">{len([f for f in p["flags"]])} flagged</a></td>'
            f'</tr>'
        )
    return f"""
<div class="tablewrap">
<table>
  <caption>Commercial summary — prices and ratings, honestly labelled</caption>
  <thead><tr>
    <th>Product</th><th>Brand</th><th>Manufacturer list price</th><th>Amazon price</th>
    <th>Commission rate</th><th>Brand-site rating</th><th>Open flags</th>
  </tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
</div>
<p class="tiny muted">Commission rate is blank on every row on purpose: Amazon publishes rates by <em>category</em> (S3) but not the category assigned to a given ASIN, so any number here would be a guess. Amazon price is blank because Program Policies §2(b) only permits displaying it when Amazon serves the link or via the official API {src_links(['S2'])}. Brand-site ratings are dated snapshots from each manufacturer's own review widget, not Amazon ratings; see the product-page notes for the recorded counts and access dates.</p>
"""


def rate_table():
    rows = "".join(
        f'<tr><td>{e(r["category"])}</td><td class="num">{e(r["rate"])}</td><td>{src_links(r["source"])}</td></tr>'
        for r in COMPLIANCE["commission_table"]
    )
    return f"""
<div class="tablewrap">
<table>
  <caption>Amazon Associates standard commission income rates (US) — official table, reproduced verbatim</caption>
  <thead><tr><th>Product category</th><th>Fixed rate</th><th>Source</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
</div>
<p class="tiny muted">Reproduced from the Standard Commission Income Statement {src_links(['S3'])} on {e(ACCESSED)}. This is the only official rate source; third-party blogs circulating different numbers were excluded from this project.</p>
"""


def calc_widget():
    """No hypothetical traffic/order/revenue estimator is published."""
    return '<p class="small">No order or revenue projection is published. The campaign ledger remains empty until authorised first-party reports exist. <a href="measurement.html">Measurement status and definitions →</a></p>'


# --------------------------------------------------------------------------- #
# pages
# --------------------------------------------------------------------------- #

def _dashboard_article_cards():
    """Three headline articles, rendered as cards on the dashboard."""
    picks = ARTICLES["articles"][:3]
    out = []
    for a in picks:
        out.append(f"""<a class="card" href="articles/{a['slug']}.html">
  <span class="kicker">{e(a['kicker'])}</span>
  <span class="cardtitle">{e(a['title'])}</span>
  <span class="cardtext">{e(a['standfirst'])}</span>
  <span class="tiny muted">{e(a['kind'])} · {a['reading_minutes']} min read</span>
</a>""")
    return chr(10).join(out)


def _flag_count():
    """Rows on the Flagged page.

    Counted from the same markup `page_flagged()` emits, which has been
    `<tr id="fNN"><td class="num"><strong>FNN</strong>` since pass 10 added per-row
    anchors. The previous pattern (`<tr><td class="num">...`, with no id attribute)
    silently stopped matching at that commit and the landing page published
    "0 Flags open" next to a 61-row register. `check_flag_count_matches_page()`
    now asserts the two agree, so this cannot regress unnoticed again.
    """
    return len(re.findall(r'<tr id="f\d+"><td class="num"><strong>F\d+</strong>',
                          page_flagged()))


def pulse_strip():
    """Landing-page tiles. Every number is computed from the data, never typed."""
    return f"""
<div class="pulse" aria-label="What this site covers, computed from the dataset">
  <div class="tile"><b>{len(PRODUCT_LIST)}</b><span>Products compared</span><a href="compare.html">Sourced matrix \u2192</a></div>
  <div class="tile"><b>{len(ARTICLES["articles"])}</b><span>Sourced articles</span><a href="articles/index.html">Read the guides \u2192</a></div>
  <div class="tile"><b>{len(SOURCES["sources"])}</b><span>Official sources</span><a href="data.html#sources">The register \u2192</a></div>
  <div class="tile"><b>{_flag_count()}</b><span>Flags open</span><a href="flagged.html">Review them \u2192</a></div>
  <div class="tile"><b>0</b><span>Hands-on tests</span><a href="articles/who-actually-pays-for-air-fryer-reviews.html">Why \u2192</a></div>
</div>
"""



def publication_byline(prefix="", checked=None):
    date_text = f' · Sources checked {e(checked)}' if checked else ""
    return (f'<p class="reading-note">By <a href="{prefix}about.html">Zone1 Kitchen</a> '
            f'· AI-assisted document research · no hands-on testing{date_text}</p>')


def format_art(row):
    return (f'<div class="format-art {e(row["kind"])}" aria-hidden="true">'
            f'<span class="art-index">{e(row["index"])}</span>{format_glyph(row["kind"])}'
            '<span class="art-note">Format illustration · not to scale</span></div>')


def product_card(p, prefix=""):
    row = BUYING_BY_SLUG[p["slug"]]
    return f"""<article class="card pcard publication-product" data-format="{e(row['kind'])}">
{format_art(row)}
<div class="pcard-body">
 <p class="product-type">{e(row['eyebrow'])}</p>
 <h3><a href="{prefix}products/{e(p['slug'])}.html">{e(row['title'])}</a></h3>
 <p class="cardtext">{e(row['dek'])} {src_links(row['sources'])}</p>
 <dl class="publication-facts"><div><dt>Capacity</dt><dd>{e(row['capacity'])} {src_links(row['sources'])}</dd></div><div><dt>Published size</dt><dd>{e(row["size"])} {src_links(row["size_sources"])}</dd></div></dl>
 <p class="product-caution"><strong>Check first:</strong> {e(row['check'])} {src_links(row['check_sources'])}</p>
 <a class="pick-cta" href="{prefix}products/{e(p['slug'])}.html">Explore the product guide <span aria-hidden="true">→</span></a>
</div>
</article>"""


def article_teaser(slug, prefix="", short=True):
    a = ARTICLE_BY_SLUG[slug]
    editorial = next((x for x in PUBLICATION["featured_guides"] if x["slug"] == slug), {}) if short else {}
    return (f'<a class="card article-card" href="{prefix}articles/{e(slug)}.html">'
            f'<span class="kicker">{e(editorial.get("label", a["kicker"]))}</span>'
            f'<span class="cardtitle">{e(editorial.get("title", a["title"]))}</span>'
            f'<span class="cardtext">{e(editorial.get("dek", a["standfirst"]))}</span>'
            f'<span class="article-card-foot">{a["reading_minutes"]} min read <span aria-hidden="true">↗</span></span></a>')


def reader_capture(prefix=""):
    return (f'<section class="rss-band" aria-label="Follow new guides"><div><p class="section-eyebrow">A quieter way to keep up</p>'
            '<h2>Good questions. New guides.</h2><p>Add our RSS feed to your reader. No email address, account or inbox clutter.</p></div>'
            f'<a class="btn btn-ghost" href="{prefix}feed.xml">Get the RSS feed <span aria-hidden="true">↗</span></a></section>')


def page_thermometers():
    cards = []
    for note in PUBLICATION["thermometer_links"]:
        record = next(x for x in PRODUCT_INTENT["rows"] if x["id"] == note["id"])
        cards.append(f"""<article class="card">
<p class="kicker">{e(note['eyebrow'])}</p><h2 style="font-size:30px;margin-top:5px">{e(note['title'])}</h2>
<p class="small">{e(note['note'])} {src_links(note['sources'])}</p>
<p class="tiny muted">Observed {e(record['observed_on'])}: <code>{e(record['observed_asin'])}</code>. Intended ASIN, official listing confirmation and enrolled-link test remain blank in the separate record.</p>
<a class="btn" href="{e(record['supplied_link'])}" rel="sponsored nofollow noopener" target="_blank" data-analytics-event="outbound_click" data-analytics-target-id="{e(record['id'])}">View supplied Amazon link <span aria-hidden="true">↗</span></a>
<p class="tiny muted" style="margin:12px 0 0">Affiliate link · model, intended listing and attribution unconfirmed.</p>
</article>""")
    body = f"""<p class="crumbs"><a href="../index.html">Home</a> / Thermometers</p>
<p class="section-eyebrow">Beyond the air fryer</p><h1>Two thermometer links. A few checks first.</h1>
<p class="lede">The other kitchen tools submitted for this publication currently open thermometer listings. These are transparent link notes—not tested recommendations, and not confirmation of what their sender intended.</p>
{publication_byline('../')}
<div class="grid grid-2">{''.join(cards)}</div>
<h2>Before choosing a thermometer</h2>
<p>Check the exact model and probe configuration, its instructions for use and cleaning, and whether any app or hub is required. The CHEF iQ brand page has selectable probe configurations; the ThermoMaven catalogue includes different instant-read and wireless lines. Do not copy a specification from one variant to another. {src_links(['S39','S40'])}</p>
<p class="small">The observed Amazon titles are retained as dated evidence. No claim about accuracy, certifications, wireless range, heat resistance or food safety is adopted from those titles. A landing URL alone does not prove attribution, and a missing visible tracking ID does not disprove it. {src_links(['S36','S37','S41'])}</p>
<p class="small"><a href="../product-intent.html">Read all five separate link records →</a> · <a href="../flagged.html#f80">Unresolved model matching →</a></p>
{reader_capture('../')}"""
    return layout('categories/cooking-thermometers.html','Meat thermometer link notes',body,active='categories/cooking-thermometers.html',
                  description='Dated notes on the two submitted thermometer links, keeping observed listings separate from intended products and unverified specifications.',
                  jsonld_blocks=[breadcrumbs_jsonld([('Home',SITE_BASE),('Thermometer link notes',page_url('categories/cooking-thermometers.html'))])])


def page_about():
    body = f"""<p class="crumbs"><a href="index.html">Home</a> / Our approach</p>
<p class="section-eyebrow">About Zone1 Kitchen</p><h1>Useful buying guides. Clear limits.</h1>
<p class="lede">This publication starts with the questions a kitchen purchase leaves you with: will it fit, what will it hold, and what will it ask of you after dinner?</p>
<h2>Who writes this?</h2>
<p>Zone1 Kitchen is the publication byline. The research, drafting and site build are AI-assisted. No named human editor has been established, so there is no invented expert biography, cook, test team or personal recommendation here. The <a href="data.html#sources">source register</a> makes the primary documents available for your own review.</p>
<h2>Documents, not a test kitchen</h2>
<p>No hands-on testing is claimed. No appliance was bought, handled or tested for these guides. Published dimensions, capacities and care rules come from the manufacturer or its manual. A label such as “worth comparing” is editorial guidance about those documents, not a claim about taste, noise, reliability or cooking speed. The FTC says you cannot talk about an experience with a product you have not tried. {src_link('S8')}</p>
<p>When official documents disagree, the difference stays visible. An unconfirmed value stays blank; “not documented” is not the same as “not included.” See <a href="flagged.html">Flagged for review</a> for the evidence and discovery steps.</p>
<h2>How the links work</h2>
<p><strong>{e(DISCLOSURE)}</strong> Eligible links may earn a commission. The selected ID is recorded, but account ownership and attribution have not been verified. The five submitted links have separate fields for their observed redirect and their intended listing; none has a completed enrolled-Associates test. Short-link uncertainty is not a finding that the link is invalid. {src_links(['S1','S5','S41'])}</p>
<p>We do not display Amazon prices, availability, star ratings or review counts. This site has no authorised live Program Content integration. That is a limitation of this implementation—not a claim that Amazon prohibits every permitted price display. <a href="compliance.html">Read the link and content policy</a>. {src_link('S2')}</p>
<h2>About the illustrations and imagery</h2>
<p>The line drawings are original format diagrams, not photographs or exact depictions of a branded model. The front-page kitchen scene is AI-generated decorative imagery. It is not a real test kitchen, an appliance demonstration, proof of a cooking result or an image of the submitted products. No Amazon or manufacturer product photograph has been copied. Image provenance and the self-hosted fonts’ open licences are recorded in <a href="{REPO_BLOB}publication/README.md">the publication asset notes</a>.</p>
<h2>Updates and corrections</h2>
<p>Sources are dated on individual guides. A fresh layout does not refresh every product fact. The <a href="{REPO_BLOB}reports/verification-2026-11-19-1f9e7d52.md">19 November 2026 review report</a> names exactly which official pages and sections were read, what changed, and what remains unverified. Reports from earlier passes remain available, not silently rewritten.</p>
<p>The operating plan is a weekly source review and at most one new or substantially refreshed guide every two weeks, subject to evidence and checks. This is not an already-running scheduler. <a href="topics.html">The publishing plan</a> distinguishes topics worth investigating from measured demand; no traffic, ranking or revenue outcome is promised.</p>
<h2>Privacy and reader capture</h2>
{privacy_html()}
<p>RSS is the only reader-subscription mechanism currently offered. There is no working newsletter signup and no subscriber list.</p>
{reader_capture()}"""
    return layout('about.html','Our approach & authorship',body,active='about.html',description='Who publishes Zone1 Kitchen, how AI-assisted documentation research is made, what was not tested, and how affiliate links, imagery and privacy are handled.',jsonld_blocks=[breadcrumbs_jsonld([('Home',SITE_BASE),('Our approach',page_url('about.html'))])])


def page_index():
    products = {p["slug"]: p for p in PRODUCT_LIST}
    cards = "".join(product_card(products[r["slug"]]) for r in PUBLICATION["products"])
    guides = "".join(article_teaser(r["slug"]) for r in PUBLICATION["featured_guides"])
    body = f"""<section class="publication-hero">
 <div class="hero-copy">
  <p class="hero-eyebrow">The considered kitchen <span aria-hidden="true">/</span> November 2026</p>
  <h1 class="hero-title">Choose the shape that fits your kitchen.</h1>
  <p class="lede">Basket or oven? One big batch or two dishes at once? Make the space—and the trade-offs—clear before you buy.</p>
  <div class="hero-actions"><a class="btn" href="#choose-a-format">Find your fit <span aria-hidden="true">→</span></a><a class="text-link" href="compare.html">Compare the details <span aria-hidden="true">↗</span></a></div>
  <p class="hero-footnote">Source-led buying guides. No hands-on tests. <a href="about.html">Our approach</a></p>
 </div>
 <figure class="hero-image"><img src="assets/images/kitchen-editorial-900.webp" srcset="assets/images/kitchen-editorial-540.webp 540w, assets/images/kitchen-editorial-900.webp 900w" sizes="(max-width:620px) calc(100vw - 40px), 48vw" width="900" height="604" alt="" fetchpriority="high"><span class="image-label">Room for good food</span><figcaption>AI-generated editorial scene · not a product image or test kitchen.</figcaption></figure>
</section>
<nav class="browse-strip" aria-label="Browse by question"><span>Start with a question</span><a href="articles/dual-basket-vs-oven-air-fryer.html">Basket or oven?</a><a href="articles/air-fryer-capacity-guide.html">How much capacity?</a><a href="articles/small-kitchen-air-fryer-dimensions.html">Will it fit?</a></nav>
<section class="quick-guide" id="choose-a-format" aria-labelledby="formats-title">
 <div class="section-heading"><div><p class="section-eyebrow">Different kitchens. Different trade-offs.</p><h2 id="formats-title">Find your kind of air fryer.</h2></div><a class="text-link" href="categories/kitchen-appliances.html">Explore air fryers <span aria-hidden="true">↗</span></a></div>
 <div class="format-controls" data-format-controls hidden role="group" aria-label="Filter by appliance format"><button type="button" data-format-filter="all" aria-pressed="true">All formats</button><button type="button" data-format-filter="dual" aria-pressed="false">Two baskets</button><button type="button" data-format-filter="single" aria-pressed="false">One basket</button><button type="button" data-format-filter="oven" aria-pressed="false">Oven-style</button><span class="tiny muted" data-format-status aria-live="polite">3 formats shown.</span></div>
 <div class="grid grid-3">{cards}</div>
 <p class="section-note">These are documented product options, not a ranking. Supplied-link destinations and intended listings are not yet confirmed as a match; check the exact model before buying. <a href="product-intent.html">The separate link record</a>.</p>
</section>
<div class="publication-compare-cta"><div><h2>Prefer everything side by side?</h2><p>Capacity, counter space and care. Official sources beside the details.</p></div><a class="btn btn-ghost" href="compare.html">Compare the three <span aria-hidden="true">→</span></a></div>
<section class="quick-guide" aria-labelledby="guides-heading"><div class="section-heading"><div><p class="section-eyebrow">A little homework, a better fit</p><h2 id="guides-heading">Read before you make room.</h2></div><a class="text-link" href="articles/index.html">All buying guides <span aria-hidden="true">↗</span></a></div><div class="grid grid-2">{guides}</div></section>
<section class="season-feature" aria-labelledby="season-heading"><div><p class="section-eyebrow">The November notebook · 2026</p><h2 id="season-heading">Giving an air fryer? Ask about the counter first.</h2><p>A useful gift starts with the way someone cooks—not the biggest number on the box. These seasonal guides help with the questions, without claiming a deal or a bestseller.</p></div><div class="season-links"><a href="articles/air-fryer-gift-guide-2026.html">The thoughtful air-fryer gift guide <span aria-hidden="true">↗</span></a><a href="articles/black-friday-model-number-switch.html">A model-number check before a sale <span aria-hidden="true">↗</span></a><a href="articles/questions-before-buying-a-multifunction-appliance.html">Questions before buying multifunction <span aria-hidden="true">↗</span></a></div></section>
<section class="reader-note" aria-label="How these guides are made"><span class="note-symbol" aria-hidden="true">“</span><div><h3>The manual is a good place to start.</h3><p>We link the specifications to the manufacturer. When official documents disagree, you’ll see the difference—not a guess. <a href="about.html">How we research</a>.</p></div><div><h3>More kitchen tools, kept in perspective.</h3><p>The other submitted links open thermometer titles. Read the <a href="categories/cooking-thermometers.html">ThermoMaven and CHEF iQ link notes</a>; intended models and specifications remain unconfirmed.</p></div></section>
{reader_capture()}"""
    ld = [breadcrumbs_jsonld([("Home", SITE_BASE)]), {"@type":"ItemList","name":"Documented air-fryer formats","itemListElement":[{"@type":"ListItem","position":i,"name":r["title"],"url":page_url('products/'+r['slug']+'.html')} for i,r in enumerate(PUBLICATION['products'],1)]}]
    return layout("index.html","Kitchen buying guides for the way you cook",body,active="index.html",description="Find the air-fryer format that fits your kitchen. Compare documented capacity, counter space and care, with useful buying guides and clear affiliate disclosures.",jsonld_blocks=ld)

def page_product(p):
    row = BUYING_BY_SLUG[p["slug"]]
    record = next(r for r in PRODUCT_INTENT["rows"] if r["supplied_link"] == p["link"])
    flag_rows = "".join(f'<tr><td>{e(f["id"])}</td><td>{e(f["issue"])}</td><td>{e(f["action"])}</td><td>{src_links(f.get("sources",[]))}</td></tr>' for f in p["flags"])
    related = ARTICLE_BY_SLUG[row["related_guide"]]
    labels = {"Capacity", "Dimensions", "Dimensions / weight", "Temperature range", "Power", "Rated power", "Wattage"}
    brief = spec_table({**p, "specs": [r for r in p["specs"] if r["label"] in labels]})
    brief = brief.replace("Verified specifications", "Documented essentials")
    care_source = {"chefman-6qt-dual-basket":"S18", "chefman-8qt-turbofry":"S13", "emeril-26qt-french-door":"S15"}[p['slug']]
    care = {
        'emeril-26qt-french-door': 'Hand-washing accessories is recommended. Never soak or dishwash the main appliance.',
        'chefman-6qt-dual-basket': 'The removable baskets and racks may go on the dishwasher top rack. Never immerse or dishwash the main unit.',
        'chefman-8qt-turbofry': 'The removable basket and rack may go on the dishwasher top rack. Never immerse or dishwash the main unit.',
    }[p['slug']]
    temperature_note = ('<p class="small"><strong>Temperature note:</strong> the manual describes 450 °F as a two-minute Hi-Fry boost, not an unrestricted full-cycle setting. ' + src_link('S18') + '</p>'
                        if p['slug'] == 'chefman-6qt-dual-basket' else '')
    body = f"""<p class="crumbs"><a href="../index.html">Home</a> / <a href="../categories/kitchen-appliances.html">Air fryers</a> / {e(row['title'])}</p>
<section class="product-hero">{format_art(row)}<div><p class="section-eyebrow">{e(row['eyebrow'])} · a document-based guide</p><h1>{e(row['title'])}</h1><p class="lede">{e(row['dek'])} {src_links(row['sources'])}</p><p class="small"><strong>Capacity:</strong> {e(row['capacity'])} {src_links(row['sources'])}</p><p class="small"><strong>Check first:</strong> {e(row['check'])} {src_links(row['check_sources'])}</p>{product_cta(p,'../')}</div></section>
{publication_byline('../')}
<div class="product-verdict"><p class="section-eyebrow">The short version · editorial guidance</p><p>{e(row['verdict'])} {src_links(row['sources']+row['check_sources'])}</p></div>
<nav class="buyer-toc" aria-label="On this product page"><a href="#specifications">Specifications</a><a href="#before-buying">Before buying</a><a href="#source-record">Sources &amp; listing record</a></nav>
<h2 id="specifications">What the documents say.</h2><p class="small muted">The essentials for the documented model—not a serving or performance test. A refreshed layout does not re-verify every field; individual dates and conflicts stay in the <a href="../data.html">full record</a>.</p>
{brief}
{temperature_note}
<p class="small"><strong>Care:</strong> {e(care)} {src_link(care_source)} <a href="../articles/how-to-clean-an-air-fryer.html">Read the care guide →</a></p>
<h2 id="before-buying">What to check before buying.</h2><p>{e(row['check'])} {src_links(row['check_sources'])}</p><p class="small">The model string in this record is <code>{e(p['model_number']['v'])}</code>. {src_links(p['model_number']['s'])} Compare it with the listing and the documentation for the unit you would receive. No opinion here establishes cooking performance, noise, durability or how many portions your meal will make.</p>
<div class="grid grid-2">{article_teaser(related["slug"],"../")}{article_teaser("how-to-clean-an-air-fryer","../")}</div><p class="small"><a href="../compare.html">Compare all three formats →</a></p>
<details class="source-detail" id="source-record"><summary>Official sources, listing observations &amp; open questions</summary>
<p class="small">Observed {e(record['observed_on'])}: <code>{e(record['observed_asin'])}</code>. This is a dated redirect observation, not the intended ASIN. Intended ASIN, official listing confirmation and per-product enrolled Associates test remain blank. The selected tracking ID is recorded but not applied. {src_links(record['observed_source_ids'])}</p>
<p class="small">{e(p['model_number']['caveat'])}</p><h3>The full specification record</h3><p class="small muted">Manufacturer statements and dated Amazon listing observations are labelled separately; neither confirms this account holder’s intended listing. Older field-specific notes remain dated evidence, not a fresh claim about every value.</p>{spec_table(p)}
<div class="tablewrap"><table><caption>Recorded product questions</caption><thead><tr><th>ID</th><th>Issue</th><th>Next step</th><th>Official evidence</th></tr></thead><tbody>{flag_rows}</tbody></table></div>
<p class="small"><a href="../flagged.html">Full public review register</a> · <a href="../product-intent.html">Separate intent and attribution fields</a></p>
</details>
<p class="small muted">No Amazon price, rating or review count is displayed. No authorised live Program Content integration is configured. The brand’s dated commercial snapshots, if useful for a source check, remain in the <a href="../data.html">full dataset</a>, not as today’s shopping price. {src_link('S2')}</p>
{reader_capture('../')}"""
    return layout('products/'+p['slug']+'.html',row['title']+' product guide',body,active='categories/kitchen-appliances.html',description=row['dek']+' Documentation-based product notes; no hands-on testing.',jsonld_blocks=[breadcrumbs_jsonld([('Home',SITE_BASE),('Air fryers',page_url('categories/kitchen-appliances.html')),(row['title'],page_url('products/'+p['slug']+'.html'))])])


PROGRAMME_FLAGS = [('F1',
  'ASIN → manufacturer model number: recorded for ten passes as not published by Amazon. Closed on 2026-11-16 '
  'for two of three products — see F49 and F68.',
  'All three',
  'HISTORY KEPT, BECAUSE THE PREMISE WAS THE DEFECT: this row said the model number could not be read from the '
  "listing, so each product's model was published as a documented match with a caveat, and F49 recorded that a "
  'machine could not read it at all. On 2026-11-16 session arena/ba29c641 fetched all three /dp/ pages and '
  'each Product information block rendered. B0CDY277D3 states Model Number and Part Number RJ38-SQPF-3TDB-2W — '
  "the brand page's and manual's string, so that mapping is now sourced twice. B08DKYBTPH states Part Number "
  "RJ38-SQSS-8T (its Model Number row holds the marketing string 'Large Air Fryer'). B09B7SB46R states "
  "4-00675-02X-VN, one character away from the brand page's 4-00675-02A-VN, and that conflict stays open "
  '(F70). Still open, unchanged by this pass: whether the supplied short links point where the account holder '
  'intended (F6, F7, F10), which is why the caveat on the *link* half of the mapping is not removed.',
  ['S16', 'S28', 'S29']),
 ('F6',
  'The Associates tag inside the three link.amazon short links is not observable.',
  'All three links',
  'The shortener hides the tag. Attribution cannot be verified from outside Associates Central, so '
  "'associates_tag_confirmed' is false for all three links. Needs the account holder to open Manage Tracking "
  'IDs.',
  ['S2', 'S17']),
 ('F7',
  'Program Policies §6(w) (Content on your Site) prohibits link shortening that makes it unclear you are '
  'linking to an Amazon Site.',
  'All three links',
  'link.amazon keeps the Amazon name visible, so the risk is low, but the landing URL is generated and '
  'temporary. Recorded so the account holder can confirm current guidance before publishing.',
  ['S2']),
 ('F83',
  'The owner handover told a reader to see F01, F02, F03, F06 and F07, and the Flagged page renders no such '
  'rows.',
  'data/decision.json handover.items, handover.html, decisions.html',
  'Found and repaired 2026-11-17 by arena/0cf55ef3 (X-0cf55ef3). The handover register names the flags each '
  'owner action closes. Five of those entries were zero-padded ids (F01, F02, F03, F06, F07) belonging to the '
  'older annex register data/flags.json, which runs F01-F27. The page that prints them is rendered next to '
  'flagged.html, and that page renders the canonical register (F1, F6, ...), where the same numbers mean '
  "different things: legacy F01 is 'price, rating and review count are blank', canonical F1 is 'ASIN to "
  "manufacturer model number'. A reader who followed one landed on the wrong row or on nothing, which is the "
  'F46/F59 defect class that check_register_cross_references() was written to stop - but that guard accepts '
  'legacy ids on purpose because F47 documents two registers, so these slipped through. Repaired at source: H1 '
  'now closes F1, F32 and F33; H2 closes F6 and F76; H3 cites Q-03 as a question; H4 and H5 are labelled as '
  'measurement rows and a decision log rather than dressed up as flags. Both renderers link an id only when it '
  'matches F plus one or two digits. New guard check_legacy_flag_pointers() now fails the build when a '
  'zero-padded id is printed without the surrounding sentence naming the legacy register, and it was proven to '
  "fire on an injected 'closes F01' before being committed.",
  []),
 ('F84',
  'Three published counts were typed into prose and had already gone stale, including the headline on the '
  'handover page.',
  'build.py (homepage callout, handover heading), data/decision.json handover.summary, data/requirements.json '
  'rows A-04 and B-08',
  'Found and repaired 2026-11-17 by arena/0cf55ef3 (X-0cf55ef3), fifth occurrence of the class F14, F38, F52 '
  "and F63 record. (1) handover.html's headline read 'Five actions, about an hour, eighteen flags' and the "
  "homepage repeated 'closes eighteen flags' twice, while data/decision.json holds five handover items and the "
  'three that close flags close five flag rows between them - 18 matched neither the item count nor the flag '
  "count. (2) index.html said 'Eight reads written for this product set' directly above a grid rendering 21 "
  "articles. (3) data/requirements.json row B-08 said 'Twelve articles are published and three more are "
  "specified but unwritten' (now 21 and 4) and row A-04 said 'Twenty questions' (now 26). Repaired at source: "
  'the article count is now computed from data/articles.json at build time, both requirements rows now use the '
  "register's existing computed-count tokens (n_articles, n_questions) and a new n_topics_minus_articles token "
  'derived from data/topics.json, and the handover headline and summary state the five-row figure that the '
  'register actually supports. An unknown token still fails the build. Re-rendered and re-checked: '
  "requirements.html reads '21 articles' and '26 questions', index.html reads '21 reads' and 'five flag rows "
  "closed'.",
  []),
 ('F85',
  'The article set is tracked in two hand-maintained registers, and both were wrong in opposite directions on '
  '2026-11-17.',
  'data/topics.json vs data/design-prompt.json (topics)',
  "Found by the pass-13 read. The design-prompt register still marked A-9 'not-written' two days after its "
  'article shipped (articles/associates-disclosure-explained.html, published 2026-11-16 in the pass-10 set), '
  'while the canonical topic queue carried no row for that published article at all — the orphan defect of F74 '
  'in reverse: a page every reader could reach, absent from the list that says what the site covers. Both data '
  'rows are corrected in place by this pass (A-9 status fixed; queue row TP-26 added) and the new rows '
  'TP-21/TP-24/TP-25 keep the two lists aligned for now. The machinery gap is what stays open: nothing in the '
  'build compares the two registers, so the next article that touches one and not the other reproduces this. '
  'Decision needed: generate the design-prompt topic list from data/topics.json, or retire the duplicate list.',
  ['S30']),
 ('F86',
  'chefman.com publishes two different weights for the 8 Qt TurboFry Touch (RJ38-SQSS-8T) on the same product, '
  'read on the same day.',
  'Chefman 8 Qt TurboFry — product weight',
  "Read 2026-11-17: the product page's specification block states 'Weight: (8 Qt Model) 12.8 lbs / 5.8 kg'; "
  'the store product record behind the same page (…/turbofry-touch-air-fryer-1.json, updated_at '
  '2026-11-17T11:41:54-05:00) carries variant weight 13.4 lb. 0.6 lb apart, and neither document says which '
  "figure is the appliance and which is the carton — which matters because this site's small-kitchen article "
  "and the new buyer's checklist both tell readers to check a shelf or cupboard load. Nothing was averaged and "
  'no weight figure was invented: the published row stays the specification block, and no weight claim is made '
  'in advice. Settled by a statement from Chefman or a scale reading (Q-38).',
  ['S12', 'S33']),
 ('F87',
  'The shopfront polish of pass 13 lands in the canonical root build only; six parallel builds on the same '
  'origin keep their own stylesheets and their own look.',
  's2/, site/, research/, docs/, dashboard/, annex-88769516/',
  'Found while implementing SG-44. Every design change in this pass (front-page order, merchandising rows, '
  'mobile type scale, the sticky comparison bar) is generated by build.py for the root site. The parallel '
  'builds are separate generators with their own reproducibility gates — scripts/build_s2_site.py --check, '
  'scripts/verify_site.py, research/check_research.py — so hand-editing their HTML or CSS would break the gate '
  'that proves their output matches their data, which is the reason earlier passes logged requests instead of '
  "edits and this pass does the same. A reader who reaches a parallel build from the footer's archive links "
  'sees a pre-2026-11-17 page and a second brand voice. Decision needed (SG-44): declare the root build '
  'canonical and label the annexes archives, port the tokens into each generator, or stop serving the annexes '
  'from the published site.',
  ['S31']),
 ('F88',
  'No accessibility standard can currently be cited on this site, so the mobile pass states a 44 px tap-target '
  'minimum as a usability choice and claims no conformance.',
  'verify.py OFFICIAL_HOSTS vs the design rows in data/design-prompt.json',
  'The pass-13 stylesheet widens interactive chrome to a 44 px minimum and the code comment names WCAG 2.2 SC '
  "2.5.8 — but verify.py's official-host allow list contains no accessibility body, so no published row could "
  'link the standard it satisfies and the site must not print a conformance claim without a registered source. '
  'Recorded rather than silently fixed: adding a host to the verifier is a policy change to the checking '
  'machinery, and the two must arrive in the same commit with the decision attached (Q-40). Note also that 44 '
  'px is larger than the 24 CSS px minimum in that success criterion; the figure chosen here comes from '
  'platform interface guidance, not from the standard, and is described that way on D-16.',
  ['S43']),
 ('F89',
  'The suggestions queue asserted in its own lede that nothing on the page had been implemented, while the '
  'decision log already recorded a shipped row — a typed claim that outlived the fact.',
  'data/suggestions.json (lede and how_to_read) vs data/decision-log.json (implemented)',
  "Found 2026-11-17 by the pass-13 read while adding rows to that register: the page's first sentence and its "
  "how_to_read[0] both stated 'Nothing on this page has been implemented', which had been untrue since "
  "2026-11-16, when data/decision-log.json recorded SG-26 path A as implemented under the queue's own "
  'pre-authorisation rule. Same class as F52, F63 and F14 — a register cell written as a snapshot and rendered '
  "as a live fact. Repaired in the generator: the lede and the new decision desk now count the log's rows at "
  'build time (so the sentence moves when the log does), and how_to_read[0] was rewritten to describe the '
  'mechanism instead of asserting a status. What remains open is the general fix: check_register_preambles() '
  'compares repeated sentences, not claims about other registers, so no guard stops the next typed status '
  'sentence from going stale the same way. Decision needed: extend the register-preamble guard to reject '
  "declarative status claims ('nothing has been implemented', 'N rows are done') in prose that has a computed "
  'equivalent. The pass-13 scan found the same class in a place no guard looks at — evidence-link labels: '
  "'A-02: 21 suggestions', 'A-04: 20 questions' and 'B-08: 12 articles' were printed as link text beside a "
  'register that had grown to 44, 37 and 24. All three were rewritten to point at the page that computes its '
  "own count, and B-08's typed count became a build-time computed count instead. A label is prose, and prose "
  'about a row count is exactly what drifts.',
  ['S30']),
 ('F90',
  'The price note on every front-page product card cited the wrong policy clause: it said Program Policies '
  "§2(b) and §6(t) bar an Associate site from displaying Amazon's price.",
  'Front page (price_line in build.py) — all three products',
  "Re-read live 2026-11-19: Participation Requirements §2(b) says a site 'may only show prices and "
  'availability if: (a) we serve the link … or (b) you obtain Product pricing and availability data via '
  "Creators API or PA API' — a conditional permission, not a bar — and §6(t) is about customer reviews and "
  'star ratings, not prices. Fixed in the same pass: the note now cites §2(b) alone and says what it allows. '
  "Other pages that pair 'prices and star ratings' with '§2(b) and §6(t)' are correct and were left alone.",
  ['S2']),
 ('F91',
  "categories/kitchen-appliances.html published '0 of the five links submitted to this project were observed "
  "landing on air fryer or air fryer-oven listings' while three of them did.",
  'Category page lede — PI-01…PI-05',
  "The count tested 'air fryer' against a prose field that spells it 'Air-fryer', so nothing matched. Live "
  "re-read 2026-11-19: B04G1MEwY, B02NbDxp3 and B00hJ57DV land on pages whose breadcrumb ends 'Fryers › Air "
  "Fryers'; B0c8moW59 and B0f3GKalj land under 'Thermometers & Timers › Meat'. The breadcrumb is now recorded "
  'per row as observed_browse_path (an observation, kept apart from intent), the count reads it, and a row '
  'without one fails the build. The defect was first reported in open PR #144 on 2026-11-17 and stayed live '
  'for two days because that PR could not merge.',
  ['S17', 'S16', 'S28', 'S29', 'S36', 'S37']),
 ('F92',
  "Two rows on the questions page linked their flag citations to the wrong anchor: 'Flag F86' pointed to #f84 "
  "and 'Flag F88' pointed to #f86.",
  'data/questions.json — Q-38 and Q-40',
  'Left over from the pass-13 renumbering (F84→F86, F86→F88): the labels were rewritten, the URL fragments '
  'were not, and check_register_cross_references() reads labels, not fragments. Both anchors repaired '
  "2026-11-19; a repository-wide scan of every data file for a 'Flag Fnn' label whose URL fragment names a "
  'different flag found no other case. The guard gap is closed in the same pass: check_flag_anchor_labels() '
  "now fails the build when a link's text names one flag and its fragment opens another (proven by reverting "
  "Q-38's anchor).",
  []),
 ('F93',
  'Five pull requests from 2026-11-17 are still open and unmergeable (#139, #141, #144, #146, #150); at least '
  'one carried content no merged pass has published.',
  'Repository process',
  "Reviewed 2026-11-19. #144's fix is superseded by F91. #150 is a COORDINATION record only. #146's "
  'self-hosted endpoint overlaps analytics/ already on main. #141 applies the selected tracking ID to links, '
  'which main deliberately does not do until the account test passes (Q-01, SG-47) — a decision, not a merge. '
  '#139 carries a sourced dataset and page for the two thermometer links (PI-04, PI-05) that main has never '
  'published; porting it needs a fresh live re-read of every row, and the choice is SG-50. Disposition is in '
  'COORDINATION.md; none of the five was merged or closed by this pass.',
  []),
 ('F94',
  'The suggestions page contradicted itself: the decision desk said 47 rows, 42 still asking for a path and 7 '
  "implemented (49), and the 'At a glance' note under it still said 'Nothing on this page has been "
  "implemented'.",
  "suggestions.html — decision desk and 'At a glance' note",
  "Found 2026-11-19 while adding rows. The desk's 'still ask you for a path' figure excluded only rows whose "
  "effort said 'done', not rows the decision log records as shipped, so implemented rows were counted twice. "
  "The 'At a glance' sentence is the same typed-status class as F89, in a second place that F89's repair did "
  "not reach. Both fixed in the generator: shipped rows leave the open count and the 'blocked on a question' "
  'count, and the note now points at the desk instead of asserting a status.',
  []),
 ('F95',
  "The channelId parameter on Amazon's landing URL is not a property of a link: the same ASIN came back with "
  'channelId=704 through its short link and channelId=500 through a direct /dp/ request on the same day.',
  'PI-01…PI-05 observed redirect targets',
  'Observed 2026-11-19. Through the short links, the three air-fryer ASINs landed with channelId=704 and the '
  'two thermometer ASINs with channelId=500 plus extra parameters; the same day, direct requests for all five '
  '/dp/ pages each landed with channelId=500. The 704 value matches the 2026-11-14 record in '
  'data/reverification.json. Amazon documents none of these parameters in any source this project holds, so '
  'they are recorded and nothing is read into them — not attribution, not link type, not who made the links. '
  'Amazon says even an absent tag parameter on the landing URL is not evidence about attribution (S41). This '
  'row exists so a future pass does not treat the 704/500 split as a difference between the two batches of '
  'links.',
  ['S17', 'S41']),
 ('F8',
  'IP License §2(e) forbids aggregating, analysing or repurposing Program Content and training models on it.',
  'Platform design',
  'Any AI research or trend scoring therefore runs only on first-party data and public manufacturer data. '
  'Documented as guardrail G6 in the blueprint.',
  ['S2']),
 ('F9',
  'No Amazon price, star rating or review count is available to this build.',
  'All three',
  'Left blank everywhere by policy rather than by omission. Becomes fillable only if the operator secures '
  'Creators/PA API credentials.',
  ['S2', 'S19']),
 ('F10',
  'The short links are generated redirects with fallback parameters, not plain product links.',
  'All three links',
  'Logged redirect observations carried lv=shuf and plpRedirect=mhFallback. The candidate ASIN/title '
  'destinations were consistent across the recorded checks, but the btn_ref/srctok value changed between '
  'repeat or cache-busted requests (see F41 and the linked session evidence). These are observations of '
  'redirect responses, not confirmation that the candidate ASINs are the products intended by the account '
  'holder or that the links carry an Associates tag. Confirm both before publishing.',
  ['S17', 'S16']),
 ('F11',
  'The site does not disclose cookies, pixels and third-party technologies as Participation Requirements §3(e) '
  'requires.',
  'Whole site',
  'The site itself sets no cookies and runs no analytics, but §3(e) requires an accurate disclosure of cookie '
  'and third-party technology use, including that third parties may place or recognise cookies. Only a minimal '
  'notice is in the footer; a proper privacy/cookie statement is needed before launch. Legal review '
  'recommended.',
  ['S2']),
 ('F12',
  'The automated platform functions in the brief are not running — by design, not by omission.',
  'Platform',
  'Automated trend detection, competition scoring and conversion optimisation need an Associates account, '
  'Creators/PA API credentials and sales reports. PA API access is registered through Associates Central and '
  'credentials are tied to the primary account holder, with request rate scaled to account sales performance. '
  'None of that exists in this repository, and inventing the data to fill the gap would defeat the point of '
  'the project.',
  ['S2', 'S19', 'S20']),
 ('F13',
  'Product listing titles are reproduced from Amazon; §6(a) restricts altering Program Content.',
  'All three',
  'Titles are shown verbatim and unedited. §6(a) permits truncation only where meaning is not materially '
  'altered, and whether a listing title counts as Program Content is not stated. Recorded so the operator can '
  'confirm before adding any paraphrase.',
  ['S2']),
 ('F14',
  'The landing page overstated product resolution (corrected 2026-11-14).',
  'Root landing page',
  "The headline read '3 products resolved — all three short links followed to an ASIN'. The 2026-11-14 check "
  "found the short links reach Amazon fallback pages and the bare 9-character codes return 'Page Not Found'. "
  "The headline now reads '0 verified product identities' and the ASINs are labelled as unconfirmed "
  'candidates. Evidence: reports/link-check-2026-11-14.md.',
  ['S16', 'S17']),
 ('F15',
  "Plain ASIN URLs were also answered with Amazon's fallback form on 2026-11-14.",
  'All three ASINs',
  'amazon.com/dp/B0CDY277D3, /dp/B09B7SB46R and /dp/B08DKYBTPH each returned a URL carrying lv=shuf and '
  'plpRedirect=mhFallback, so a fetch cannot show that the ASIN is the live product page. Confirm from a '
  'logged-in browser before any ASIN is treated as the supplied product.',
  ['S16']),
 ('F16',
  'link.amazon is not confirmed as an Amazon-documented short-link domain.',
  'All three links',
  'A web search on 2026-11-14 returned only third-party blogs naming amzn.to and a.co. No official Amazon page '
  'listing link.amazon was found. An official Associates help page is needed before the domain is described as '
  "Amazon's.",
  ['S2', 'S17']),
 ('F17',
  'Advisory link gate: table rows with no source link on inherited annex pages.',
  'dashboard/, site/, research/, session-3740f69d/ annexes',
  'Root pages generated by build.py were given a source badge, policy citation or flagged-page link in the '
  "arena/0c7445c7 pass (2026-11-14). Remaining advisory rows lived only in other sessions' annex builds; "
  'scripts/check_links.py reported them as non-blocking warnings. **CLOSED 2026-11-14 by sess-7111e2b6** along '
  'with F25: a row-source pass now runs inside the research/ and site/ generators, and scripts/source_rows.py '
  "applies it to the hand-authored annex builds. The advisory list is empty, and the gate's own definition was "
  'corrected first, so that it can see single-quoted hrefs and every flagged-page filename.',
  ['S1']),
 ('F18',
  'Committed s2 build stamp changes with the calendar date.',
  's2/ (session zone1-s2 build)',
  "scripts/build_s2_site.py writes today's date into the 'built' stamp. Re-running on 2026-11-14 changes 13 "
  'files by that stamp alone (committed stamp: 2026-11-13). The CI gate regenerates before it checks, so it '
  'passes, but the committed copy is not pinned. Not changed in this pass because another session owns the '
  'file.',
  ['S1']),
 ('F19',
  'Brand-site review counts move between days, so every rating on this site is a dated observation.',
  'All three',
  "Chefman's own widget read 1,302 reviews on 2026-11-13 and 1,305 on 2026-11-14; the 8 Qt page read 715 then "
  '716. A third read on 2026-11-16 moved them again — 1,307 and 717 — while both averages held at 4.6 for the '
  'third consecutive time. The averages did not move (4.6 on every read), but a published figure without its '
  'read date would silently become false. All three counts now carry all three dates in the dataset, and any '
  'copy generated from it must carry the date too.',
  ['S10', 'S12']),
 ('F20',
  'The repository carries six parallel builds, and two of them were unreachable from the landing page until '
  'the 2026-11-14 integration pass.',
  'Whole repo',
  's2/, site/, dashboard/, research/, session-3740f69d/ and docs/ are independent session outputs with their '
  'own data, their own verifiers and their own verdicts; they disagree in places (for example on whether the '
  'commission rate can be stated, and on how to read the plpRedirect=mhFallback marker). The pass linked the '
  'two orphaned builds into the navigation and changed none of their content. The owner should decide which '
  'build is canonical before this points at a real domain — a live site with six home pages is a maintenance '
  'and trust problem, not a data problem.',
  []),
 ('F23',
  'One documented build command in the README no longer runs against the shared data — it is a pre-existing '
  'break, not a regression from this pass.',
  'scripts/build.mjs → docs/',
  'The Node builder that generated the retired docs/ build validates a schema (products with official_url / '
  'values, sources with a status field, compliance.rows, flags) that data/products.json, data/sources.json, '
  "data/compliance.json and data/flags.json no longer use, so 'node scripts/build.mjs --check' throws "
  'ERR_INVALID_URL on undefined. Verified identical on the pre-change baseline, and no CI workflow calls it — '
  'pages.yml, ci.yml and verify.yml are Python-only. docs/ therefore stays frozen as committed and cannot be '
  "regenerated from current data. Not repaired here: re-authoring another session's generator to a new schema "
  'would silently change what its published pages assert. Either retire docs/ and its README line, or point '
  'the builder at data/verified/. This pass added no dependency on it.',
  []),
 ('F22',
  'A committed merge-conflict marker was found in a published document and repaired by this pass.',
  'EXECUTIVE_SUMMARY.md',
  "The file carried a bare '=======' line and a '>>>>>>> origin/main' line on main, i.e. a previous "
  'integration resolved a conflict by leaving the markers in. Both sides are real work by different sessions, '
  'so this pass removed only the markers and kept both documents as separate sections. Any other file carrying '
  'markers should be treated the same way — delete the marker, never the work.',
  []),
 ('F21',
  'Two verification passes on the same links reached different conclusions, and both are published.',
  'The three supplied links',
  'arena/1dcaaafc (reports/link-check-2026-11-14.md) reads the fallback marker plus the 9-character-token 404 '
  "as 'product identity not confirmed' and removed the 'products resolved' headline. sess-81495d2d "
  '(reverification.html) re-tested with a repeat request and a nonsense-token control: the target was '
  'identical across four sessions on two days, while an unrecognised token returns 403 instead of a product '
  'page, which is not what a pure not-found fallback would do. The reconciled position on this site: the '
  '*destination* of the links is reproducible and is documented; the *identity* of the product the operator '
  'meant, and the Associates tag attached to the link, are not confirmed and are not asserted. Confirm both in '
  'a logged-in browser and in Associates Central before publishing.',
  ['S16', 'S17', 'S21', 'S22']),
 ('F24',
  "PA-API 5 is officially deprecated (confirmed live 2026-11-14); the successor is Amazon's Creators API.",
  'Platform design',
  'The official docs URL now serves a deprecation notice: PA-API 5 calls return 403 AccessDeniedException and '
  'integrations are told to migrate to the Creators API. This supersedes the earlier board retraction of the '
  "cross-check's F18 claim and means every automated feature in the blueprint must target the Creators API, "
  "not PA-API 5. The Program Policies phrase their data-use rules as 'Creators API or PA API', so the "
  'compliance quotes remain accurate. Independently noted in the dashboard annex as H-01.',
  ['S24', 'S20']),
 ('F25',
  'Table rows on inherited builds have no link to a registered official source.',
  'dashboard/, research/, site/, s2/, session-3740f69d/, annex-88769516/',
  "Audited 2026-11-14 with the project's own official-host list (every host in data/sources.json, plus this "
  'repo on GitHub). Root pages generated by build.py now pass, and the build fails on any unsourced row. '
  'Inherited builds were not edited by that pass because other sessions own them. Count at 2026-11-14: 281 of '
  '1,363 table rows in the repository have no sourced link (inherited builds: 281 of 1,057; root pages built '
  'by build.py: 0 of 306). **CLOSED 2026-11-14 by sess-7111e2b6.** The residue is now 0. Two things were wrong '
  'with the count itself: the link gate could not see single-quoted hrefs, and it recognised only one filename '
  'for the flagged page, so 33 rows that did carry a source link were being reported as unsourced. With the '
  'gate corrected, the true figure was 248 rows. A row-source pass was then added inside the research/ and '
  'site/ generators, and scripts/source_rows.py applies the same pass to the three hand-authored builds '
  "(dashboard/, annex-88769516/, session-3740f69d/). Rows that state a fact now link to that fact's official "
  'document; rows that are judgements, blocked metrics or unverified values link to the flagged page, which is '
  'where the project puts unconfirmed values. The gate also now rejects rows that link only to a relative '
  'internal page.',
  []),
 ('F26',
  'Two platform KPIs are internal design targets; no official source states them.',
  'platform.html, KPI table: Verified-row coverage, Flag resolution time',
  'Shown with this flag, not with an invented source. They are operating targets for this project, not facts '
  'about Amazon, the FTC or any product, and they feed no published product value. The owner should decide '
  'whether to keep them as targets.',
  []),
 ('F27',
  "Policy citations for the Participation Requirements 'Content on your Site' items used section numbers that "
  'do not match the live page.',
  'Root-site content (corrected in this pass); site/ annex pages still carry the old labels',
  'Live reads of affiliate-program.amazon.com/help/operating/policies on 2026-11-14 (two independent renders; '
  "version dated April 14, 2026) place the customer-review/star-rating rule at Participation Requirements '6. "
  "Content on your Site' item (t), and items (g) incentives, (n) framing, (u) self-purchase, (v) cloaking, (w) "
  'link shortening and (y) price tracking in the same section. Repo content had cited these as §3(t), §3(g), '
  '§3(n), §3(u), §3(v), §2(w) and §3(y). Every quoted rule text was verified verbatim against the live page, '
  'so no published behaviour changes — only the citation labels were aligned to the live structure in '
  'build.py, data/compliance.json, data/products.json, data/sources.json, data/platform.json, '
  'data/marketing.json, README.md, EXECUTIVE-SUMMARY.md and EXECUTIVE_SUMMARY.md. Spot-checked labels that '
  'were already correct: §2(b) prices/availability, §3(e) cookies, §6(a) alteration, IP License §2(e) '
  'aggregation/ML-training, Operating Agreement §5 disclosure. The site/ annex (session 1874bb64) still '
  'renders §3(t) from data/verified/; its owner session should align it (request logged in COORDINATION.md). '
  'Historical session records in COORDINATION.md were left as written.',
  ['S2']),
 ('F28',
  'Three flag registers share overlapping ID spaces but index different issues, and two published documents '
  'cite the wrong one.',
  'Cross-build consistency',
  "Confirmed 2026-11-14 by sess-91d0552e (renumbered F25 -> F28 to avoid a collision with arena/6ecdb4e4's "
  "F25). (a) research/build_research.py tells the reader to see 'the root site's Flagged page (shared register "
  "data/flags.json id F19)' for the product-titles/§6(a) issue and 'id F20' for the cookie-disclosure issue. "
  "Those IDs ARE correct inside data/flags.json, but the root Flagged page is generated from build.py's own "
  "PROGRAMME_FLAGS, where F19 is 'brand-site review counts move between days' and F20 is 'the repository "
  "carries six parallel builds'. A reader following that pointer lands on an unrelated row. (b) "
  "EXECUTIVE_SUMMARY.md, still served at the site root, asserts 'Identity verified. All three short links "
  "resolve to Amazon.com product pages with different ASINs' and that 'the official commission schedule "
  "redirected to a sign-in page'. Both are contradicted by this pass: the reconciled position published on "
  'this site is 0 verified product identities (F14-F16, F21), and the Standard Commission Income Statement was '
  'read in full, without any login, on 2026-11-14. Not repaired in this pass: data/flags.json is consumed by '
  "the s2 and docs generators and research/ is another session's build, so re-keying either register would "
  "silently re-point another build's citations. Decision needed: adopt one register as canonical and re-key "
  'the others, or relabel the pointers. Evidence: session-91d0552e/VERIFICATION-2026-11-14.md §5.',
  ['S1', 'S3']),
 ('F29',
  'The Emeril preset count is stated five different ways across official sources, and two of them now say 24.',
  'Emeril 26 QT French Door',
  "Re-read 2026-11-14 by sess-54c66535. Amazon's listing title for ASIN B09B7SB46R says '24 cooking functions' "
  "and Emeril's own description paragraph says 'Equipped with 24 one-touch cooking presets', while the same "
  "page's specification block says '25 Cooking Pre-sets', its feature heading says '10-In-1' and one of its "
  "carousel assets is named '11-in-1'. Two independent official sources now agreeing on 24 is new evidence: "
  'earlier passes recorded only 25 vs 10-in-1 vs 11-in-1 with no tiebreaker. The conflict is narrowed, not '
  'closed - the same brand page still contradicts itself - so no preset count is asserted anywhere on this '
  "site. Decision needed: confirm the figure against the unit's own control panel before any copy states a "
  'number. <strong>Re-read 2026-11-15 by arena/88bb2db6, which changes that last sentence.</strong> The '
  "owner's manual for FAFO-001 was read row by row: its Preset Mode Chart and its Recommended Accessory "
  'Positions table each list exactly 24 presets by name, and the manual never states the numeral. The Amazon '
  "listing title independently says '24 One-Touch Preset Options'. The site now states 24 on the strength of "
  "the manual, names the one official line that disagrees (the brand page's specification block, '25 Cooking "
  "Pre-sets'), and flags it. This row and F4 both stay open, but the site no longer asserts nothing. The "
  '10-in-1 and 11-in-1 labels remain marketing wording and are not presented as specifications. Decision still '
  "needed: confirm the figure against the unit's own control panel.",
  ['S14', 'S17', 'S16']),
 ('F30',
  'Two published specification values are not stated by the official source the site cites for them.',
  'Chefman 6 Qt Dual Basket (preset count); Emeril 26 QT French Door (interior light)',
  'Re-read 2026-11-14 by sess-54c66535. The Chefman dual-window user guide RJ38-SQPF-3TDB-2W was read end to '
  'end and documents HI-FRY, +2 MIN, MUTE, SYNC BASKETS, SYNC FINISH, START/STOP, TIME/TEMP and SHAKE, but has '
  'no preset chart and never names the four food presets the site publishes; its control panel is artwork with '
  "no text layer. The Emeril brand page's specification block lists Timer, 26-Quart Capacity, Dual-Speed Fan, "
  '25 Cooking Pre-sets, dimensions, 24.6 Liters, Temperature Control and 120 volts, with no interior-light '
  "row. Both values were left as published rather than deleted, because deleting another session's sourced row "
  "is not this pass's call, but neither is currently traceable to an official statement. Decision needed: "
  're-source both to the brand product pages, or blank them and let them appear here as unverified.',
  ['S18', 'S14']),
 ('F31',
  "The two Chefman 6 Qt sister SKUs carry very different review counts on the brand's own site.",
  'Chefman 6 Qt Dual Basket',
  'Re-read 2026-11-14 by sess-54c66535. The dual-basket page RJ38-SQPF-3TDB-2 reports 4.6 stars from 194 '
  'reviews; the dual-window page RJ38-SQPF-3TDB-2W reports 4.6 stars from 1,305 reviews, on an identical list '
  'price and promo ladder. The 6.7x gap is a usable signal for deciding which SKU the supplied ASIN maps to, '
  'which is open flag F2. It is not an identification: a review count is not a product identifier. No SKU is '
  "asserted. Correction 2026-11-16 (session arena/ba29c641): this row also stated that 'Amazon does not "
  "publish the model number behind an ASIN', which is false — the listing's Product information block "
  'publishes it (F49, F68) — so a review-count comparison is no longer the nearest thing to a route: the model '
  'number itself has been read, and it matches the -2W page this site maps to.',
  ['S11', 'S10', 'S16']),
 ('F32',
  'Chefman sells three different 6-quart dual-basket SKUs; the site names two of them.',
  'Chefman 6 Qt Dual Basket',
  "Found live 2026-11-14 by arena/6b2eddeb. Chefman's own store currently publishes RJ38-3DBW-V2 ('TurboFry 6 "
  "Qt. Double Basket Air Fryer with Easy View Windows': 6 Qt / 5.68 L as two 3 Qt / 2.84 L baskets, 90–400 °F "
  '/ 32–204 °C, 1700 W, five functions — air fry, bake, reheat, dehydrate, frozen — easy-view windows, '
  'interior lights, shake notifications, 4.5 stars from 30 reviews, $99.99 list), RJ38-SQPF-3TDB-2 '
  '(dual-basket, 4.6 from 194, no specification block published) and RJ38-SQPF-3TDB-2W (dual-window, 200–450 '
  "°F, Hi-Fry, 4.6 from 1,305). The site records the -2W mapping because the Amazon title says 'Hi-Fry' and "
  "'Easy View Windows', and Hi-Fry is documented only on the -2W page — but Easy View windows appear on all "
  'three, so the title does not discriminate on its own. This is an identification risk, not an '
  'identification. Two other builds shipped in this repo (site/, research/) map the same ASIN to RJ38-3DBW-V2 '
  'with no caveat, so a reader can reach two different official-looking answers two clicks apart. Decision '
  "needed: open the listing, read the model plate or the 'Product information' model number, and settle it "
  "once. **Addendum 2026-11-16 (session arena/ba29c641): the read was done, by fetch.** The listing's Product "
  "information block states Model Number and Part Number RJ38-SQPF-3TDB-2W — the root site's mapping, not the "
  'site/ and research/ mapping to RJ38-3DBW-V2. Those two builds now disagree with a document each of them can '
  'read; they are not edited here because those trees belong to other sessions, and the divergence is another '
  'reason to retire or re-key them (F44). See F68.',
  ['S25', 'S27', 'S10', 'S16']),
 ('F33',
  "The 'Hi-Fry / 450 °F: None' row for the 8 Qt product is only true of the stainless SKU, and a second "
  'official SKU matches the Amazon title exactly.',
  'Chefman 8 Qt TurboFry',
  'Found live 2026-11-14 by arena/6b2eddeb — narrows F3, does not resolve it. Chefman sells RJ38-SQSS-8T '
  '(TurboFry Touch Stainless-Steel, max 400 °F / 205 °C, four food presets, stainless finish — the SKU the '
  'site currently maps) and RJ38-8T-BLACK (TurboFry 8 Qt Air Fryer w/ High Fry: Hi-Fry 450 °F / 232 °C for the '
  'final two minutes, and exactly four functions — air fry, bake, dehydrate, frozen — in a matte-black '
  "finish). The Amazon listing title for B08DKYBTPH reads '…4-in-1 with 450°F Hi-Fry Option… | Bake, "
  "Dehydrate, Frozen | … Stainless Steel'. The function list and the 450 °F Hi-Fry match RJ38-8T-BLACK word "
  'for word; the finish matches RJ38-SQSS-8T. So the title may describe a third variant, or may carry a finish '
  "that does not match the unit. The previous framing — 'one of the two official sources is stale' — is now "
  'the less likely explanation. No value is changed and neither model is asserted; a human should read the '
  "model number printed in the listing's Product information section. **Read 2026-11-16 by session "
  'arena/ba29c641, by fetch:** the listing states Part Number RJ38-SQSS-8T *and* Max Temperature Setting 400 '
  "°F — its identifier field points at the 400 °F model while its title describes the -BLACK's Hi-Fry "
  'capability. That is a listing carrying a title from somewhere else, which is not the same as proof of which '
  'machine ships: because RJ38-8T-BLACK genuinely documents 450 °F (S26), the two-models explanation this row '
  'opened stays live and both readings are published.',
  ['S12', 'S26', 'S16', 'S29']),
 ('F34',
  'The second executive summary at the repo root still asserts two things that are now known to be wrong.',
  'EXECUTIVE_SUMMARY.md',
  'Found 2026-11-14 by arena/6b2eddeb. EXECUTIVE_SUMMARY.md (the older of the two root summaries) states in '
  "its Key findings: 'Identity verified. All three short links resolve to Amazon.com product pages with "
  "different ASINs' and 'the official commission schedule redirected to a sign-in page'. This session "
  're-fetched both on 2026-11-14: the Associates Program Standard Commission Income Statement (Table 1 and '
  'Bounty Events) was read in full with no login, and product identity is explicitly NOT verified anywhere on '
  'this site (F14–F16, F21, F32, F33). A dated correction banner was placed above that document by an earlier '
  'pass, but the contradicting sentences remain in the body and the file is still served from the site root by '
  'direct link. Decision needed: retire the duplicate document, or rewrite the two sentences. This pass did '
  "not edit it — the sentence is another session's published work and rewriting it is a content decision, not "
  'a verification one.',
  ['S1', 'S3']),
 ('F35',
  'Nine separate HTML sites for the same three products are published in this repository, and they disagree '
  'with each other.',
  'Whole repository',
  'Found 2026-11-14 by arena/6b2eddeb. Alongside the canonical root build there are research/ (12 pages), '
  'session-3740f69d/ (11), s2/ (13), site/ (11), dashboard/ (14), docs/ (7) and annex-88769516/ (10), plus '
  'data-only trees in crosscheck/ and platform/. The root navigation links to six of them. They disagree on '
  'facts a reader would take as settled: the Chefman 6 Qt model (RJ38-SQPF-3TDB-2W on the root site, '
  'RJ38-3DBW-V2 in site/ and research/ — F32), and the policy section numbers for the review/star-rating and '
  'link-shortening rules (§6(t)/§6(w) on the root site after F27, §3(t)/§2(w) in site/ and session-3740f69d/). '
  'Each build is internally consistent and individually verified; the problem is that nothing tells a reader '
  'which one is canonical when they arrive from a search engine. Decision needed: keep one site and archive '
  "the rest behind a clearly labelled 'previous verification passes' page, or make every non-canonical page "
  'carry a fixed banner naming the canonical build.',
  ['S1', 'S2']),
 ('F41',
  "F10's earlier wording incorrectly said the short links' srctok marker stays constant across repeat "
  'requests.',
  'All three links — historical wording correction',
  'Closed 2026-11-15 by arena/94a562a1-zone1: F10 now states that the recorded candidate ASIN/title '
  'destinations were consistent while btn_ref/srctok values changed across some repeat or cache-busted '
  'requests. The underlying records include srctok-2cef40d2904c29d8 on 2026-11-13; srctok-1e229870efde5acf '
  'changing to srctok-397b5ba66db39bbf on a cache-busted repeat (session-81495d2d evidence, row 4); '
  'srctok-704dc575b940a94c (session-54c66535); and srctok-0740a2e990c9bbb3 in two observations later that day. '
  'This closes only the wording mismatch. It does not prove that any candidate listing is the product intended '
  'by the account holder or confirm affiliate attribution; see F1, F6, F14-F16 and F21.',
  ['S17', 'S16']),
 ('F37',
  'A published value was cited to a source that does not state it.',
  'Emeril 26 QT French Door — the "Interior light: Yes" row',
  'Found and fixed 2026-11-14 by sess-7111e2b6. The row cited the brand product page (S14), whose '
  'specification strip lists Timer, 26-Quart Capacity, Dual-Speed Fan, 25 Cooking Pre-sets, 16.9"D x 15.8"W x '
  '14.8"H, 24.6 Liters, Temperature Control and 120 volts — and no interior light. The value is nonetheless '
  'correct: the owner\'s manual (S15) documents it in the control-panel section, "F. LIGHT BUTTON: May be '
  'selected at any time during the cooking process to light the appliance\'s interior." The row has been '
  "re-sourced from S14 to S15 and the manual's wording recorded in the row note. The lesson is published "
  'rather than quietly fixed: a value can be true and still be mis-cited, and a citation that does not support '
  'its value is as much a defect as an invented number.',
  ['S14', 'S15']),
 ('F38',
  'An Amazon listing title changed between the 2026-11-14 read and 2026-11-15, so a published value was stale.',
  'Emeril 26 QT French Door — the listing-title row',
  "Found and fixed 2026-11-15 by arena/3ddfa50e. The stored title ended '| 26QT air fryer oven with French "
  "doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals.' and the live title on "
  "the same ASIN (B09B7SB46R, reached through https://link.amazon/B02NbDxp3) now ends '| Countertop Convection "
  "Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included'. The preset "
  'count is unchanged at 24; the wording around it is not. The row now carries the 2026-11-15 string, keeps '
  'the superseded string in a visible field, and states the date of the read. This is the same class of '
  'volatility as F14 (brand-hosted review counts that moved in 24 hours) and the reason every volatile value '
  'on this site must carry its read date.',
  ['S28']),
 ('F39',
  'A source record was cited for a value it does not support: one registered URL stood in for three different '
  'product pages.',
  'All three products — the listing-title and ASIN rows',
  'Found and fixed 2026-11-15 by arena/3ddfa50e. Source S16 was registered with a single URL '
  "(https://www.amazon.com/dp/B0CDY277D3) but its title claimed to cover 'ASINs B0CDY277D3, B09B7SB46R, "
  "B08DKYBTPH', and it was cited as the source for all three products' listing titles and ASIN rows. For the "
  'Emeril and 8 Qt rows, the source link therefore took a reader to the Chefman 6 Qt listing. A citation that '
  'does not resolve to the page stating the value is the same defect class as F37. Fixed by registering each '
  'ASIN separately: S16 = B0CDY277D3, S28 = B09B7SB46R, S29 = B08DKYBTPH, and repointing every citation. The '
  "root build's row-source gate did not catch this because it checks that a row links to *a* registered "
  'official host, not that the host page actually states the value.',
  ['S16', 'S28', 'S29']),
 ('F40',
  'Two different rows were published under the same flag number.',
  'Register integrity — F36',
  'Found and fixed 2026-11-15 by arena/3ddfa50e. The programme-level row recording the srctok-marker finding '
  '(added by sess-ce4070ad, itself renumbered from F32) was published as F36, and a product-level row in '
  'data/products.json recording the Chefman 6 Qt preset-count mis-citation was also published as F36. Both '
  'rendered on the Flagged page, so the register showed 38 rows with 37 distinct numbers and any citation of '
  "'F36' was ambiguous. F28 records an earlier ID collision of the same kind, which means the rule was not "
  'enforceable. The programme-level row is renumbered F41; the product row keeps F36 because three session '
  'evidence files cite it by that number. A duplicate-ID build test now fails the build if this recurs.',
  ['S1']),
 ('F42',
  "The operator's location is stated two different ways on the same domain, and neither statement comes from "
  'an official source.',
  'questions.html (Q-06) and suggestions.html (SG-10) vs the s2/ annex register (its F08)',
  'Recorded 2026-11-15 by arena-b1e7b4bc. The 2026-11-15 pages say the owner is in Osaka, Japan; the s2 annex '
  'register (data/flags.json, row F08) records a Norway residence. Both were written from agent-session '
  'environment context, not from anything the owner supplied in the repository and not from any official page, '
  'so neither can be verified from here and at most one can be right. The Japan wording matters because Q-06 '
  'and SG-10 build a store-targeting decision on it. Decision needed: the owner states their actual country '
  'once, one register row cites it, and the other wording is corrected to match; until then no eligibility '
  "conclusion (Q-06, SG-10, or the s2 register's F08) should be treated as settled.",
  []),
 ('F44',
  'The same site is published nine times from one repository, and eight of those copies are reachable at '
  'public URLs.',
  'Whole repository — GitHub Pages deployment',
  'Measured 2026-11-15 by this pass: 106 HTML files are published from the repository root. The maintained '
  'site is the 27 sitemap URLs generated by build.py; the remaining pages are seven earlier or parallel builds '
  '(dashboard/, annex-88769516/, session-3740f69d/, research/, s2/, site/, docs/), each with its own homepage, '
  'its own near-duplicate comparison of the same three products, and in two cases a visible Amazon price. '
  "Amazon's Program Policies §2(b) permit price display only when Amazon serves the link or the data comes "
  'from Creators/PA API, so a published copy that shows a price is a compliance exposure this project has '
  "otherwise been careful to avoid. Google's own guidance (S30) states that the presumption is that individual "
  "pages match the overall quality of the domain, that a site reputation review weighs whether 'the same "
  "identical or near-identical content appears on multiple other sites', and that scaled content generated "
  "without added value for users should be excluded from search. Decision needed, and it is the owner's: keep "
  'the older builds published for auditability and accept the duplicate-content and compliance risk, or remove '
  "the duplicate pages and keep only their evidence files. This pass did not delete or edit another session's "
  'published output — that is not a unilateral decision to take. Full option set: SG-17 on the Suggestions '
  'page.',
  ['S30', 'S2']),
 ('F45',
  "The site's search-engine plumbing was incomplete: no page declared a canonical URL, and no page carried "
  'Open Graph or structured data.',
  'Whole root site — every generated page',
  'Found and fixed 2026-11-15 by this pass, and measured before the fix: 0 of 27 generated pages had '
  'rel=canonical, 0 had og:* tags, 0 had a Twitter card, 0 had JSON-LD (a repository-wide count that also '
  "included the annex builds was 33 canonicals of 106 pages, from other sessions' templates). Two "
  'consequences: with nine copies of the same content on one origin, nothing told a search engine which copy '
  "is maintained; and a shared link rendered as a bare URL. Fixed in build.py's layout() so every generated "
  'page now carries canonical, og:*, twitter:card and schema.org WebSite/Organization/BreadcrumbList/Article '
  'markup, and 404.html carries noindex and no canonical. Enforced by a new build guard (check_seo_metadata) '
  'so a later template edit cannot drop it. schema.org Product/Offer/AggregateRating is deliberately NOT '
  'emitted: the site publishes no Amazon price or star rating (§2(b), §6(t)), so product markup would either '
  'be empty or would assert a number this project refuses to publish.',
  ['S30', 'S31', 'S2']),
 ('F43',
  'Two wording advisories on the Suggestions and Questions pages (reader-facing precision, no data value '
  'affected).',
  'suggestions.html and questions.html (PR #58, X-633b115f)',
  "Recorded 2026-11-15 by arena-b1e7b4bc. (a) The Suggestions lede says 'None of them has been implemented', "
  "but for SG-03, SG-04, SG-05 and SG-11 option A is the current, already-implemented state ('Keep...', 'Keep "
  "blank and link to the live Amazon page (current, compliant)'), so those rows read more accurately as "
  "'confirm the current state' than as pending work. (b) Q-01's 'How to find out' says to check the owner's "
  "Associates account for which tag the short links carry - the tag is not observable from the account's "
  'tracking-ID page either (flag F6); only whoever created the short links knows the mapping. Decision needed: '
  "reword the lede and the Q-01 cell, or accept the current phrasing. Both rows' facts and sources check out; "
  'this flag is about wording only.',
  []),
 ('F47',
  'There are two flag registers in this repository, they contradict each other, and both are readable from the '
  'live site.',
  'data/flags.json (F01-F27) vs flagged.html (F1-F43)',
  "Found 2026-11-15 by arena/792c279e-zone1. data/flags.json still records F02 'The official Standard "
  "Commission Income schedule redirected to a sign-in page' and F01-F04 language asserting that the short "
  "links resolve 'with different ASINs'. The re-verification performed in this same pass read the Standard "
  'Commission Income Statement in full without any login (Table 1: Kitchen 4.50%, All Other 4.00%) and '
  "re-confirmed all three destinations, so the older register's two statements are contradicted by a live "
  'read. The rendered Flagged page says the opposite of data/flags.json on the commission question, so a '
  'reader who follows two links reaches two different answers. This pass did not edit data/flags.json: it is '
  'consumed by scripts/build_s2_site.py and scripts/build.mjs, and re-keying it would silently re-point '
  "another build's citations. Decision needed: name one register canonical, then either re-key the other or "
  'replace its contradicting sentences with a dated pointer to this page. Evidence: the two files themselves, '
  'and reports/verification-2026-11-15.md section 1.',
  ['S3', 'S16', 'S28', 'S29']),
 ('F48',
  'The Amazon listing for the Emeril 26 QT says six cooking accessories; the site publishes seven.',
  'Emeril 26 QT French Door — the Included accessories row',
  "Found 2026-11-15 by arena/792c279e-zone1 while re-reading the live listing title. ASIN B09B7SB46R's title "
  "now ends '... Extra Large Interior, Six Cooking Accessories Included', while the site's own row publishes "
  "7, sourced to the brand product page and the owner's manual. This is not necessarily a contradiction: a "
  'listing can count a rotisserie spit and its forks as one accessory, or bundle differently from the retail '
  'box, and the brand page and manual are the sources this site chose. The value was therefore NOT changed — '
  'altering it would mean replacing a manual-sourced number with a listing-title number on a row whose product '
  'identity is itself unconfirmed (F1, F2). Decision needed: count the accessories in the box against the '
  "manual's accessory list, then publish one number with that source. Evidence: "
  'reports/verification-2026-11-15.md section 3 row V21.',
  ['S28', 'S14', 'S15']),
 ('F49',
  'The 2026-11-15 live pass could not retrieve the one fact that closes four high-severity flags, and the site '
  'now says why in the place a buyer will look.',
  'All three products — the model-number mapping',
  'Recorded 2026-11-15 by arena/792c279e-zone1. The three Amazon detail pages were fetched again and returned '
  "the buy box, the protection plans and the 'Customers who viewed this item also viewed' blocks, but not the "
  "'Product information' table that carries the model number. That block is rendered client-side, so an "
  'automated read cannot see it; a human browser can, in about ten seconds per listing. This is recorded as '
  "its own row because seven sessions have now listed F1/F2/F32/F33 as 'needs a human' without saying why the "
  'machine cannot do it, which invites an eighth session to try again. It is now also stated on picks.html, '
  'handover.html and hand-over item H1 rather than only in the register. Evidence: '
  'reports/verification-2026-11-15.md section 3 row V24. **TESTED AND FALSIFIED 2026-11-16 by session '
  'arena/ba29c641-zone1.** The same /dp/ URLs were fetched from the same kind of environment and the Product '
  'information block was present in the response body for all three ASINs, model rows included, so the block '
  'is not unreachable to an automated read; whether it renders depends on the render path, not on the '
  'existence of the data. The row is kept rather than deleted because the failure it documents is real and '
  "worth reading: a negative observation about a fetch was promoted to a rule ('only a human can do this'), "
  'that rule was copied forward by six later passes, and it then gated four flags, two questions and the top '
  "item of the decision queue. A 'needs a human' claim is a claim about what a tool can reach, and it should "
  'be re-tested on the same schedule as any other checkable value. See F68.',
  ['S16', 'S28', 'S29']),
 ('F54',
  'The Amazon department category is now read directly on all three listings; the rate itself still needs the '
  'Earnings report.',
  'All three products — commission rate',
  'Recorded 2026-11-15 by session 42ca97ad. The annex register’s row F-06 recorded that the browse-node path '
  '‘Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers’ had been read directly on '
  'B09B7SB46R only, and named reading the other two listings as the confirmation step. This session fetched '
  'all three supplied link.amazon short links and read the identical path on B0CDY277D3 and B08DKYBTPH as '
  'well, so the evidence is now three for three rather than one for three. It still does not establish the '
  'category Amazon applies when a commission is settled: only the Associates Earnings report names the '
  'category on a shipped line, so the two candidate rows (Kitchen 4.50%, All Other 4.00%) remain the honest '
  'presentation until a sale exists. Decision needed: publish Kitchen 4.50% as the working rate with the '
  'breadcrumb cited (SG-10 path A), or keep both rows until the first Earnings report lands.',
  ['S3', 'S16', 'S28', 'S29']),
 ('F55',
  'Eleven article sentences spliced a published display label into a mid-sentence position. Found, fixed and '
  'guarded.',
  'articles/ prose, and the build’s article gate',
  'Recorded 2026-11-15 by session 42ca97ad. The article prose in data/articles.json interpolates published '
  'values into sentences. Eleven of those interpolations put a display label — ‘Two 3-quart baskets’, '
  '‘Designed for 4-6 people’, ‘Fries, Chicken, Fish, Meat (one-touch)’, ‘Limited 1-year warranty …’ — into a '
  'position where its capital is wrong, so the sentences read as machine output: ‘The dual-basket unit is 6 Qt '
  '/ 5.67 L as Two 3-quart baskets’, ‘splits a 6 Qt / 5.67 L cavity into Two 3-quart baskets’. The defect was '
  'invisible to every earlier verification pass, because each value is genuinely published and correct in a '
  'table; it only appears when the page is read as prose, which is what a shopper does. It survived PR #71’s '
  'full rewrite of data/articles.json, which re-introduced the same ten sentences and added an eleventh in a '
  'new article. Fixed by adding a {{value::prose form}} syntax whose prose form may differ from the published '
  'value in letter case and nothing else, enforced by check_articles(), and by adding check_article_splices(), '
  'which fails the build when a capitalised value is spliced into a mid-sentence position. Both guards were '
  'proven to fire: the build failed on exactly these defects before the fix and passes after it. No published '
  'value changed and no source changed.',
  ['S1']),
 ('F56',
  'The Application Review Process page was not re-read this pass; its figures are carried forward from an '
  'earlier fetch.',
  'S4 — the Associates application criteria',
  'Recorded 2026-11-15 by session 42ca97ad. This pass re-fetched the Program Policies, the Standard Commission '
  'Income Statement, both Chefman product pages, the Emeril product page, all three owner’s manuals, all three '
  'supplied short links, 16 CFR Part 255 and 16 CFR Part 465. It did not load the Application Review Process '
  'page (S4). The figures the repository carries for it — three qualifying sales within 180 days, roughly ten '
  'posts, content recent within about sixty days, a social follower floor of about five hundred — are carried '
  'forward from earlier logged fetches and are NOT re-confirmed by this pass. The sixty-day recency '
  'requirement is load-bearing for any content-refresh schedule the owner adopts, so it must be re-read before '
  'it is used as a scheduling rule rather than quoted from this repository. Note that a sibling pass on the '
  'same day did re-read this page and reported the same four figures, which corroborates them but does not '
  'change what this session itself fetched. What was and was not fetched is listed item by item in '
  'session-42ca97ad/EVIDENCE-2026-11-15.md section 6. **Re-read 2026-11-16 by arena/9fccce0c-zone1: all four '
  'figures are confirmed verbatim from the live page** — “we require at least three within the first 180 '
  'days”, “a good rule of thumb is at least 10 posts”, “Content on your website must be recent (generally '
  'within the last 60 days)” and “in most cases, at least 500” organic followers/likes — so the '
  'carried-forward part of this row is closed, and question Q-19 moves from *missing* to *known and sourced* '
  'with its answer on the row. Evidence: reports/verification-2026-11-16-9fccce0c.md row V3.',
  ['S4']),
 ('F57',
  'Three files under data/ are read by no build, and one of them is a stale copy of a register that is '
  'published.',
  'data/flagged.json, data/commission-rates.csv, data/products.csv',
  'Recorded 2026-11-15 by session 42ca97ad. A reference scan of every loader in the repository shows that '
  'scripts/build_site.py and scripts/verify_site.py read data/verified/, not data/. The root-level '
  'data/flagged.json is therefore an orphan: it holds a 13-row register whose live counterpart is '
  'data/verified/flagged.json (17 rows), and the two disagree across 85 lines — including the browse-node '
  'observation this pass has just updated, which would otherwise leave two registers saying different things '
  'about the same fact. data/commission-rates.csv and data/products.csv are read by nothing in the repository; '
  'the first is a CSV transcription of the Standard Commission Income Statement, the second the 2026-11-13 '
  'link-check ledger that records the bare-token 404 and the fallback redirect, and both are evidence worth '
  'keeping if they are labelled as evidence. Nothing published depends on any of the three, so this is a '
  'maintenance risk rather than a correctness bug, but a reader who opens data/flagged.json sees a register '
  'that no longer matches the site. This row is narrower than F47, which covers the same class of problem for '
  'data/flags.json; the two are kept separate because the files and the contradictions are different. Decision '
  'needed: delete the three orphans, or keep them explicitly as dated evidence with a header that says so.',
  ['S1']),
 ('F58',
  'A register preamble repeated a sentence on the published page. Found on the deployed site, fixed, and '
  'guarded.',
  'questions.html — the preamble above the register',
  'Found 2026-11-15 by session 42ca97ad, after PR #78 merged: the sentence ‘Questions in the ‘known and '
  'sourced’ state carry their answer on the row …’ appeared twice in the preamble above the questions '
  'register. The cause was the one-shot editor that adds the register rows '
  '(session-42ca97ad/apply_pass9_edits.py): it appended the sentence to the preamble unconditionally, so '
  'running it a second time appended it again. The build did not catch it, because the duplicate-ID guard sees '
  'IDs, the published-value guard sees numbers, and a repeated sentence is neither. Fixed by making the editor '
  'idempotent, by removing the duplicate from data/questions.json, and by adding check_register_preambles(), '
  'which fails the build if any register preamble repeats a sentence. The guard was proven to fire on an '
  "injected duplicate. The same edit also corrected the preamble's own claim that the page ‘separates three "
  'things’ - it has always described four states, which is what the legend on the page lists.',
  ['S1']),
 ('F59',
  'The repository serves six separate executive summaries, five of them stale and none labelled stale.',
  'EXECUTIVE-SUMMARY.md, EXECUTIVE_SUMMARY.md, EXECUTIVE-SUMMARY-PASS8.md, EXECUTIVE-SUMMARY-PASS9.md, '
  'EXECUTIVE-SUMMARY-PASS9-42CA97AD.md, executive-summary.html',
  'Recorded 2026-11-16 by arena/ad8105b3. A read of the repository root finds six files whose names all claim '
  'to be the executive summary: the generated executive-summary.html (current, built from data), '
  'EXECUTIVE-SUMMARY.md, and four earlier or parallel-session Markdown files (EXECUTIVE_SUMMARY.md, '
  'EXECUTIVE-SUMMARY-PASS8.md, EXECUTIVE-SUMMARY-PASS9.md, EXECUTIVE-SUMMARY-PASS9-42CA97AD.md). GitHub Pages '
  'publishes the repository root, so all six are reachable by URL. At least one, EXECUTIVE_SUMMARY.md, is '
  "already recorded in this register (F28) as asserting 'Identity verified. All three short links resolve to "
  "Amazon.com product pages with different ASINs', which this site's reconciled position contradicts. This "
  "pass did not delete or rewrite any of them: they are other sessions' committed records, and deleting "
  "another session's evidence is not a repair. The live site links only executive-summary.html. Decision "
  'needed: keep one Markdown briefing and move the rest under an archive directory with a one-line header '
  'saying what superseded them, or add a banner to each. Evidence: the six files themselves, and the root '
  'README. **Disposition recorded 2026-11-16 (session arena/ba29c641): the banner option was taken,** because '
  "deleting another session's committed evidence is not a repair. Each non-canonical briefing now opens with a "
  "'Superseded, and kept' line naming its session and date, pointing at executive-summary.html, and stating "
  'the specific claim inside it that the repository has since reversed. Covered: EXECUTIVE_SUMMARY.md (whose '
  '2026-11-14 banner also carried a stale count, refreshed here), EXECUTIVE-SUMMARY-PASS8.md, '
  'EXECUTIVE-SUMMARY-PASS9.md, EXECUTIVE-SUMMARY-PASS9-42CA97AD.md and EXECUTIVE-SUMMARY-PASS10-121929a5.md — '
  'six Markdown briefings beside the generated page. Nothing was deleted and no historical sentence was '
  'rewritten.',
  ['S1']),
 ('F60',
  "The s2 annex's requirements register cites two paths that do not exist, and its commission row rests on a "
  'premise the annex itself has since corrected.',
  'data/s2/requirements.json rows R-01 and R-08',
  'Recorded 2026-11-16 by arena/ad8105b3 while building the root requirements register (requirements.html). '
  "Two defects in the annex register. (1) R-01 'Collect and organise a full list of requirements' gives its "
  "implementation path as 'data/requirements.json rendered on Requirements page'. There is no "
  'data/requirements.json: the file is data/s2/requirements.json, and it renders at '
  "s2/pages/requirements.html. So the repository's only requirements register pointed the reader at a "
  'different, non-existent file. This is the third occurrence of the same defect class (after F14 and F38 in '
  'this register), which is why the new root register has check_requirement_paths() failing the build on any '
  'cited path that does not exist, and that guard was proven to fire on an injected bad path. (2) R-08 '
  "'Analyse commission potential' is marked blocked with the reason 'login-gated rate card (F-04)'. "
  "data/s2/flags.json row F-04 is itself titled 'CORRECTED — a public commission table does exist' and records "
  'that the Standard Commission Income Statement is readable without a login, which this pass re-confirmed '
  "live on 2026-11-16: Table 1 renders 'Physical Books, Kitchen, Automotive 4.50%'. The genuine remaining gap "
  'is narrower — Table 1 is keyed to categories, not ASINs — and the root register states it that way. Neither '
  "row was edited in the annex: data/s2/requirements.json is another session's published output. Decision "
  "needed: re-point R-01 at the real path, and restate R-08's blocking reason as the ASIN-to-category mapping "
  'rather than a login. Evidence: the two annex files and the commission page. **Repaired at source 2026-11-16 '
  '(session arena/ba29c641), with the correction shown as a dated line inside the annex row rather than '
  'applied silently:** R-01 names both registers and the paths that exist, R-08 states the ASIN-to-category '
  "mapping as the blocker and cites the public Standard Commission Income Statement, and R-03's 'no public "
  "demand metric exists' was corrected to what is actually true (a listing does carry a rank line; this "
  'repository declines to publish it under IP License §2(e), F8). The annex was regenerated with its own '
  'generator, the only supported way to change s2/**.',
  ['S3']),
 ('F51',
  "The brand's own store reports a different product weight than the brand's own specification block, and this "
  'site publishes the specification-block figure.',
  'Chefman 6 Qt Dual-Window (RJ38-SQPF-3TDB-2W) and Chefman 8 Qt TurboFry (RJ38-SQSS-8T)',
  'Recorded 2026-11-15 by arena/63a2c638, round 9. The Chefman product pages print a Specifications block: the '
  "6 Qt page says 'Weight: 13.3 lbs / 6.03 kg' and the 8 Qt page says 'Weight: (8 Qt Model) 12.8 lbs / 5.8 "
  "kg'. Those are the figures this site publishes, cited to S10 and S12. The same brand's own commerce "
  'endpoint, read the same day, reports the variant weight as 14.51 lb / 6,582 g for RJ38-SQPF-3TDB-2W (S32) '
  'and 13.4 lb / 6,078 g for RJ38-SQSS-8T (S33). The endpoint figure is the weight Shopify carries for '
  'shipping, so the most likely reading is product weight versus packaged weight - but neither page says so, '
  'and the site must not choose between them by inference. No published value was changed: the specification '
  'block remains the cited source because that is the document the published row points at. Decision needed: '
  'state in each weight row whether the figure is the product or the packaged weight, or publish both.',
  ['S10', 'S12', 'S32', 'S33']),
 ('F52',
  'The open-questions register states that dimensions, weight and warranty are missing for all three products; '
  'the product dataset already publishes eight of those nine values from official sources.',
  'questions.html row Q-06 vs data/products.json',
  "Recorded 2026-11-15 by arena/63a2c638, round 9. Q-06 asks 'What are the exterior dimensions, weight and "
  "warranty terms for each of the three products?' and is filed as 'not_stated'. Checking the nine cells "
  'against the dataset this pass: exterior dimensions are published for all three (6 Qt from S10, Emeril from '
  'S14, 8 Qt from S12); warranty is published for all three (S10, S14, S13); weight is published for both '
  'Chefman models (S10, S12). One cell - the Emeril 26 QT product weight - is genuinely absent, because '
  "neither the brand page nor the owner's manual states one. So the register overstates the gap by eight "
  'cells. This matters in both directions: a reader using Q-06 to decide what to research would redo work '
  'already done, and a reader trusting the product pages would think the register is stale. Q-06 was narrowed '
  'this pass to the single cell that is actually open, and is cross-linked to this row. No data value moved.',
  ['S10', 'S12', 'S13', 'S14']),
 ('F61',
  'The canonical compliance register and platform blueprint had never carried the two clauses that govern an '
  'AI-agent affiliate platform, and three published pages pointed at a flag number that does not exist.',
  'Whole site — compliance.html, platform.html, questions.html, suggestions.html, data.html',
  'Found 2026-11-16 by arena/9fccce0c-zone1 during verification pass 10, and fixed in the same pass. Two '
  'independent defects. (a) Missing clauses. The Associates Program Policies page (S2, “Updated: April 14, '
  '2026”) carries IP License §4 “Agents” (the Agent Terms) and Participation Requirements §5, both read '
  'verbatim live on 2026-11-16. Neither appeared anywhere in the canonical build: data/compliance.json held 0 '
  'occurrences of “Agent Terms” and data/platform.json held 0 occurrences of “Agent”, although the brief this '
  'project answers is explicitly an AI-powered affiliate platform and the root site ships a platform blueprint '
  'that proposes automated research. They are now requirements C17 and C18, with platform guardrail G11; the '
  'scope question they raise is published as Q-21 and the design decision as SG-22, and neither is answered by '
  'inference. (b) Dangling pointer. data/questions.json, data/suggestions.json and data/sources.json each told '
  'the reader to see the flag numbered 46 for the Application Review Process recency criterion. No such flag '
  'exists in the canonical register, which runs F1–F45 and F47–F58, and none exists in the legacy '
  'data/flags.json register either, which runs F01–F27. The three pointers now name F56, the row that actually '
  'covers it. A new build guard, check_register_cross_references(), fails the build if any generated page '
  'cites a flag id, source id, question id or suggestion id that is not in the register it points at, so the '
  'class of defect cannot recur silently. Evidence: reports/verification-2026-11-16-9fccce0c.md section E.',
  ['S2', 'S4']),
 ('F62',
  'IP License §4 (the Agent Terms) was not read end to end, so the full list of agent-identification '
  'requirements is not yet on the record.',
  'S2 — the IP License section of the Program Policies page',
  'Recorded 2026-11-16 by arena/9fccce0c-zone1. The Associates Program Policies page renders its IP License as '
  'one long table, and the markdown conversion used for that pass collapsed part of it. Everything quoted in '
  'requirement C17 was read directly in the response body, but the section was not read to its end: sub-part '
  '(a) refers to “the requirements in section 3 of these Agent Terms”, and the text of that section was not '
  'visible in the render. The Agent Terms are therefore published as the rules this pass could read, with the '
  'limit stated on the row, rather than as a complete checklist. Decision needed: read IP License §4 in a '
  'browser, in full, and extend requirement C17 if it adds anything — before the research agent is built '
  '(SG-22). Evidence: reports/verification-2026-11-16-9fccce0c.md, the limit stated under section A.',
  ['S2']),
 ('F53',
  'The Amazon browse-node breadcrumb is now published for two ASINs, and it does not settle which commission '
  'rate applies.',
  "All three products - the 'Amazon browse node' row and open question Q-11",
  'Recorded 2026-11-15 by arena/63a2c638, round 9, at the same time as the value itself was added, so the '
  "limit travels with the value. Both Chefman listings render the breadcrumb 'Home & Kitchen > Kitchen & "
  "Dining > Small Appliances > Fryers > Air Fryers' (S16, S29). It is tempting to read 'Kitchen' there and "
  'apply the 4.50% Kitchen rate from the Commission Income Statement (S3). That would be an inference, not a '
  "source: S3's categories are commission categories defined by the Associates programme, Amazon's browse "
  'nodes are a shopper-navigation taxonomy, and Amazon publishes no mapping between the two. The same '
  "breadcrumb begins 'Home & Kitchen', and S3 also carries 'Home' at 3.00%, so the breadcrumb alone cannot "
  'even tell you which of the two it resembles. The site therefore continues to show the commission rate as '
  'unconfirmed (Q-11) and now shows the browse node as a separate, sourced fact. The Emeril browse node is '
  "blank: three fetches of that ASIN on 2026-11-15 returned Amazon's automated 'Continue shopping' checkpoint "
  'instead of the listing page, and a value that was never rendered cannot be recorded. **Update 2026-11-16, '
  'from three reads on one day:** pass 10 (arena/121929a5) filled the Emeril row by reaching the listing '
  'through the supplied short link; arena/a746a9f2 re-read the breadcrumb directly and recorded that the '
  'checkpoint had cleared; session arena/ba29c641 fetched the /dp/ URL independently and found the same '
  "classification in the page's Best Sellers Rank line (Kitchen & Dining; Air Fryers node 17659096011). Three "
  'of three ASINs now carry a browse classification from three routes, and none of the three carries a '
  'commission category: the inference this row forbids is still forbidden, as arena/a746a9f2 put it.',
  ['S3', 'S16', 'S29', 'S28']),
 ('F46',
  'Product photography rights are undecided: no row records which images, if any, the site publishes, whose '
  'permission covers them, or how Amazon Program Content image rights apply to these specific products. '
  "Amazon's Operating Agreement and Program Policies govern Program Content imagery; the FTC treats imagery as "
  'part of an endorsement requiring clear disclosure of material connections. No product photography is '
  'published and Q-22 asks what may be published and whose permission covers it.',
  'SG-23, Q-22 and all three product pages',
  'Recorded 2026-11-16 by arena/695f03b7-zone1. The design layer offers owner photos, licensed imagery and '
  'Amazon Program Content as image options, but none is decided; until Q-22 is answered, the site stays '
  'text-and-diagrams-only and the figures on figures.html are generated diagrams, not photographs. Evidence: '
  'data/suggestions.json (SG-23), data/questions.json (Q-22), build.py flags register.',
  ['S1', 'S2']),
 ('F63',
  "Fourth occurrence of the stale-count defect class: three registers asserted 'eight articles' after the set "
  'grew to thirteen. Found and fixed.',
  'data/questions.json Q-10, data/suggestions.json SG-09, data/decision.json niche rows',
  "Recorded 2026-11-16 by arena/a746a9f2 (X-a746a9f2). The brief's line-by-line review grepped every generated "
  'page for register counts and found live assertions that had gone stale as the article set grew: '
  "questions.html (Q-10's 'what we know' cell and the page's JSON-LD) and suggestions.html (SG-09's title, "
  "problem, evidence label and recommendation) both said 'eight articles', and decisions.html carried 'the "
  "site's existing eight articles' plus a pill reading 'Eight articles already exist in this shape' - while "
  'the articles index publishes thirteen. This is the same defect class as F14, F38 and F52: a register cell '
  'written as a snapshot and read as a live fact. Fixed per the F52 precedent: the two rows inside this '
  "session's claimed scope were corrected in place, and the third (data/decision.json, created by a completed "
  'session) was corrected as an integration-scope wording fix, with before/after strings logged in '
  'COORDINATION.md. All three now carry a dated count (13, 2026-11-16) plus a pointer to the live articles '
  "index, so they read as dated snapshots rather than live claims. The same scan cleared the 'parallel "
  "register' pages (decision-gate.html's fourteen questions, marketing-directions.html's twelve suggestions) "
  "as internally consistent — their ledes render their own frozen register's length — and cleared the "
  'historical recounts in reverification.html and executive-summary.html, which describe already-fixed '
  'defects. No build guard can police free-prose counts without a whitelist of claim sentences; '
  'check_register_preambles covers repeated sentences only. Decision needed: adopt computed counts in register '
  'prose (SG-26 option A machinery) or accept dated snapshots as the house standard.',
  []),
 ('F64',
  'Three registers carried duplicated content onto the published site. Found by line-by-line review, repaired, '
  'and guarded.',
  'questions.html row Q-11, the articles note, and one Chefman 8 Qt specification row',
  'Recorded 2026-11-16 by arena/b23f12f0, round 11. A line-by-line read of data/ found three places where the '
  'same text was stored more than once and then published more than once: (1) the Q-11 row of the '
  "open-questions register carried three of its 'what we know' entries seven times each - 18 entries "
  "collapsing to 6 - so the sentence 'The same breadcrumb does NOT settle this question' appeared 14 times in "
  'the rendered questions.html; (2) the note field in data/articles.json repeated its first paragraph '
  "verbatim, joined by a pipe, so the editorial discipline statement was printed twice; (3) the 'Hi-Fry / 450 "
  "F mode' row of the Chefman 8 Qt product cited source S29 three times in a row, which a reader sees as three "
  'source badges for one claim. None of the three is a wrong fact - each is the same fact printed repeatedly, '
  'which is precisely the pattern that makes a page read as machine-generated. All three were repaired with an '
  'order-preserving de-duplication that changed no wording. A build guard, check_register_duplicates(), now '
  'fails the build if any register list repeats an entry or any register string repeats a sentence, and the '
  'guard was proven to fire on an injected duplicate before it was committed.',
  ['S3', 'S29']),
 ('F65',
  'A recorded conclusion about Amazon’s bot checkpoint was wrong: the block is intermittent per request, not a '
  'property of the ASIN.',
  "data/sources.json source S28, data/products.json, and the 'Amazon browse node' row of the Emeril 26 QT "
  'product',
  'Recorded 2026-11-16 by arena/b23f12f0, round 11, because an earlier pass recorded a conclusion that this '
  'pass contradicts. On 2026-11-15 three fetches of ASIN B09B7SB46R were each answered by Amazon’s automated '
  "'Continue shopping' checkpoint, while the two Chefman ASINs fetched cleanly in the same window. The "
  "recorded conclusion was 'this is a per-ASIN block, not a site-wide one'. Round 11 re-tested it: the Emeril "
  'ASIN loaded on the first attempt, and in the same session B0CDY277D3 - which had loaded cleanly the '
  'previous day - was served the checkpoint on its first attempt and returned the listing only on a retry. So '
  'the block is intermittent per request. The 2026-11-15 evidence could not have distinguished the two '
  'readings, because a per-ASIN pattern and an intermittent pattern look identical across three failures, but '
  'the distinction matters: a failed fetch is not evidence about the ASIN, and no future pass should record '
  "'blocked' as a property of a listing. Separately, this pass filled the Emeril browse-node cell and then "
  'found that session 121929a5 (pass 10) had filled the same cell independently on the same day, by the same '
  'route - the detail page and the supplied short link - reaching the identical string. Two independent reads '
  'agreeing is worth more than one, so both are recorded on the row and both sources cited (S28, S17). This '
  "pass also removed a stale 'unverified' field that the earlier fill had left behind, which still read 'Not "
  "read ... left blank' on a row that now carried a value; it did not render, but it would have contradicted "
  'the value if the render rule ever changed.',
  ['S28', 'S17', 'S16', 'S29']),
 ('F66',
  'The Emeril brand page now documents 24 presets and 25 presets on the same page, and states a different '
  'accessory count from its own Amazon listing title.',
  'Emeril 26 QT French Door - the preset count and the included-accessories count',
  'Recorded 2026-11-16 by arena/b23f12f0, round 11, from a source this project had not previously read: the '
  'brand storefront’s own machine-readable product record (S35), whose description text carries an updated_at '
  "stamp of 2026-11-16. It states 'Equipped with 24 one-touch cooking presets' and 'Included are 7 premium "
  "accessories'. Two consequences. On presets: the brand’s specification block still says '25 Cooking "
  "Pre-sets', so the brand now contradicts itself within a single page rather than across two documents. The "
  'owner’s manual’s chart names 24 and the Amazon listing title says 24, so 24 now has three statements behind '
  'it and the site continues to publish 24 - but the conflict is recorded as live and unresolved, because the '
  'brand has not withdrawn the 25. On accessories: the site publishes 7 on the strength of the brand page, '
  "while the current Amazon listing title for the same ASIN reads 'Six Cooking Accessories Included'. Both "
  'figures are quoted, neither was reconciled by inference, and the discrepancy is published rather than '
  'averaged. Neither published value changed in this pass.',
  ['S35', 'S14', 'S15', 'S28']),
 ('F67',
  'The flag duplicate-ID guard had gone blind: it matched zero rows and reported success, so it could not '
  'catch a same-day collision between two sessions.',
  'build.py - check_flag_ids_unique(), and the Flagged page it reads',
  'Found independently by two sessions on 2026-11-16 and repaired by the first of them. This pass '
  '(arena/b23f12f0, round 11) found the defect while renumbering its own flags and checking whether the guard '
  'would object; session arena/2e346d24 located and repaired it on main first, and additionally added '
  'check_flag_count_matches_page() for the related defect where the landing page was advertising zero open '
  'flags beside a 61-row register. The defect: check_flag_ids_unique() counted flag rows with a pattern that '
  'began with a bare opening table-row tag followed immediately by the number cell, while page_flagged() has '
  'emitted a row id attribute since the per-row anchors landed. The pattern therefore matched nothing, and a '
  'Counter over an empty list reports no duplicates - so the guard returned success on every run while two '
  'sessions published different rows under F61 and F62 on the same day. This repository has been bitten by '
  'flag-ID collisions at least three times before (F28, F40 and the preamble case F58), which is why the guard '
  "exists. It is recorded here rather than in the repairing session's own words because the finding belongs on "
  'the register even though the repair predates this pass landing. Nothing in this row is a claim by this pass '
  'to have made the fix.',
  ['S1']),
 ('F68',
  "The 'only a human in a browser can read this' rule was untested for ten passes, and testing it took one "
  'fetch. Also: on one ASIN the model code is not in the field named Model Number.',
  'F1, F2, F32, F33, F49, SG-01, Q-01, Q-02, hand-over item H1, and every product page',
  "Found 2026-11-16 by arena/ba29c641-zone1, as the consequence of F49. The register's own explanation for why "
  'four flags needed a human was that the Product information table is rendered client-side and cannot be '
  'retrieved by a fetch. Three /dp/ URLs were fetched on 2026-11-16 and the block was present in each '
  'response, model rows included. Two lessons, both kept on the record. (1) A negative claim about tooling is '
  "an empirical claim and decays: 'the fetch did not return it' became 'a fetch cannot return it' without "
  'anyone re-testing, and six later passes copied the sentence forward, one of them into a hand-over sheet and '
  "a 'three minutes of your time' callout on the landing page. (2) The method matters as much as the read: on "
  "B08DKYBTPH the field called Model Number holds the marketing string 'Large Air Fryer' and the code sits in "
  "Part Number, so any procedure that reads 'the Model Number row' — the exact procedure SG-01 told the owner "
  'to follow — returns a non-code for one of the three products. Both fields must be read, and the two are '
  'compared. What this pass did NOT do is convert a listing claim into a manufacturer specification: the 31 '
  "rows added to data/products.json are each labelled 'as listed by Amazon' and sourced to S16/S28/S29, and "
  'product identity from the link side stays open (F6, F7, F10). The mechanism behind the earlier failed read '
  'is recorded separately and correctly by arena/b23f12f0 as F65 — the “Continue shopping” checkpoint is '
  'intermittent per request, not a property of the ASIN — so the 2026-11-15 observation that the table was '
  'missing was a real observation about three particular responses, and the error was generalising from them '
  'to a rule about all fetches. Both rows stand on their own reads.',
  ['S16', 'S28', 'S29', 'S10', 'S12', 'S13', 'S18', 'S26']),
 ('F69',
  "Two official documents disagree on the 8 Qt's footprint, and one listing disagrees with itself about the 6 "
  "Qt's capacity units.",
  'chefman-8qt-turbofry dimensions rows; chefman-6qt-dual-basket capacity rows',
  'Found 2026-11-16 by arena/ba29c641-zone1, in the same read that closed F1. chefman.com publishes the 8 Qt '
  '(RJ38-SQSS-8T) as 15.4 in x 12.6 in x 13.5 in and separates the 5 Qt figures on the same page (S12); the '
  'listing for B08DKYBTPH publishes 12.75"D x 13.5"W x 10"H (S29). Those are not two ways of writing one '
  'measurement: the depth differs by 2.65 in and the height by 3.5 in, so a buyer checking a cabinet clearance '
  'gets a different answer from each official source, and the weight agrees on both (12.8 lb) — which is what '
  'makes it a documentation problem rather than a transcription of a different product. Nothing was averaged: '
  "the brand figures stay the published row, the listing's figures sit on their own dated row. The same class "
  "on the 6 Qt: its listing's Capacity field reads '6 liters' while the same page's title, its Size field and "
  'the brand page all read 6 quarts (5.67 L) — a unit label that moved. Any copy that turns a capacity or a '
  'footprint into advice (the capacity guide, the small-kitchen article) must carry the caveat until Chefman '
  'states which figures are the appliance and which are the carton. Decision needed: ask Chefman which number '
  'is the appliance footprint, or drop cabinet-clearance advice.',
  ['S12', 'S29', 'S10', 'S16']),
 ('F70',
  'Three official documents give three different model strings for the Emeril 26 QT, and the two newest differ '
  'by one character.',
  'emeril-26qt-french-door model_number and its listing rows',
  "Found 2026-11-16 by arena/ba29c641-zone1. The owner's manual is headed FAFO-001 (S15), the brand product "
  'page lists 4-00675-02A-VN (S14), and the listing for B09B7SB46R states 4-00675-02X-VN in both its Model '
  "Number and Part Number rows (S28). An 'A' against an 'X' in the tenth position is the whole difference, and "
  'it is the kind of difference that means either a variant suffix or a transcription error in one of three '
  'documents — no document in this repository says which. This is the one product where the live read did not '
  'settle the mapping the way it did for the two Chefman listings, so all three strings are quoted and none is '
  'asserted. The commercial reason it matters: a comparison page that prints the wrong SKU string is a page '
  'that can be accused of reviewing a different machine, on a site whose entire claim is traceability. '
  'Decision needed: Emeril Everyday support can state the SKU behind the ASIN in one reply; until then the '
  'product page shows three strings and the character in dispute.',
  ['S14', 'S15', 'S28']),
 ('F71',
  'The Emeril listing contradicts itself inside one table: 7 accessories in Configuration, six parts '
  "enumerated in Included Components, 'Six' in the title. F48 records the six-vs-seven question; this row is "
  'about the self-contradiction.',
  "emeril-26qt-french-door 'Included accessories', 'Configuration' and 'Included components' rows",
  'Found 2026-11-16 by arena/ba29c641-zone1, and it complicates F48 rather than repeating it. F48 was recorded '
  "2026-11-15 from the listing *title* alone ('Six Cooking Accessories Included' against the site's "
  'manual-sourced 7), and left open with the sensible observation that a listing may count a spit and its '
  'forks as one item. Reading the whole Product information block shows the page does not agree with itself: '
  "its Configuration field says '…with 24 Functions and 7 Accessories', its Included Components row then "
  'enumerates six named parts (Rack, Bake Pan, Drip Tray, Crisper Basket, Rotisserie Spit, Fetch Tool), and '
  "its title says Six. So 'the listing says six' is not a single fact to weigh against the manual — the "
  "listing says both, on one screen. The site's published value stays 7 because the brand page and the manual "
  'state it (S14, S15); the Configuration field is a fourth document that agrees, and the enumeration is a '
  'second that does not. No averaging, no quiet correction. Decision needed: the packing list settles it. Note '
  "the same fetch also strengthened the other half of that row: '24 Functions' in the Configuration field is a "
  "third document agreeing with the manual's 24 named presets against the brand page's '25 Cooking Pre-sets' "
  "(F4). Distinct from F66, which records the brand page's own 24/25 split and the title-vs-manual accessory "
  'disagreement: this row is the narrower observation that the two counts sit next to each other in one table '
  'on the listing.',
  ['S14', 'S15', 'S28']),
 ('F72',
  'Temperature floors published in degrees Celsius do not convert to the floors published in degrees '
  'Fahrenheit, on two of the three products.',
  'chefman-6qt-dual-basket and chefman-8qt-turbofry temperature rows; any copy quoting a low end',
  'Found 2026-11-16 by arena/ba29c641-zone1. The 6 Qt brand page gives 200-450 °F / 95-235 °C (S10); the same '
  "product's listing states 'Min Temperature Setting: 93 °C' (S16), and 93 °C is 199.4 °F, not 95 °C's 203 °F. "
  "The 8 Qt listing states 'Min 94 °C' (S29) against the brand page's 200 °F floor (S12), i.e. 201.2 °F. Two "
  'degrees, in both cases, in the same direction: 200 °F is 93.33 °C, so someone rounded the Celsius figure up '
  'in one document and left the Fahrenheit figure alone in the other. This is a rounding inconsistency, not a '
  'second specification, and it is recorded rather than repaired because the site does not get to rewrite a '
  "manufacturer's numbers. What it forbids is specific: an article that says 'the 6 Qt goes down to 95 °C' is "
  'quoting one page and contradicting another, so low-end claims must show both units with the source that '
  'uses them, or stay out of the copy.',
  ['S10', 'S16', 'S12', 'S29']),
 ('F73',
  'The requirements register promised computed counts in its own preamble and then typed eight of them into '
  'prose; four had already gone stale.',
  'data/requirements.json (rows A-02, A-04, A-06, B-01, B-05, B-06, B-08, C-02, D-05, G-01)',
  "Found 2026-11-16 by arena/ba29c641-zone1 while updating the register for this pass's rows. The file's "
  "`counts_note` says: 'Counts are computed from the rows at build time rather than typed, so this page cannot "
  "claim a total the register does not contain.' The status counts at the top of the page are indeed computed "
  '— every number inside the prose of individual rows was typed, and four had drifted within two days: '
  "'Forty-six spec rows' and '43 of 46 carry a value' (the dataset had moved to 46 and then to 77 as passes "
  "added sourced rows), 'Twenty-one numbered suggestions (SG-01…SG-21)' against a register of 23, 'Twenty "
  "questions' against 22, and 'a generated sitemap of 37 URLs' against 46. None of these is a wrong fact about "
  'the world; each is a right fact about an older build, published as present tense, which is how a '
  'verification register quietly becomes a historical document. The fix is structural, not editorial: those '
  'rows now write named count tokens — n_spec_rows, n_verified_rows, n_blank_rows, n_suggestions, n_sg_last, '
  'n_questions, n_articles, n_topics, n_products, n_sources, n_banned, n_banned_distinct, n_tests, n_guards, '
  'n_stale_briefings — each wrapped in braces in the data and substituted by req_interp() from the same '
  'objects the pages render from. An unknown token raises at build time, and check_requirement_tokens() fails '
  'the build if a brace-delimited token survives into any generated page, so a row cannot ship '
  'half-interpolated. Both directions were proven: an injected bad token and an injected unresolved token each '
  "exited non-zero. The same class is why this register's sibling in the s2 annex carries F60, and why the "
  "sitemap row's number was removed rather than retyped: a count is only true at the moment it is written — "
  "including the counts typed into this register's own log lines, one of which this pass had to correct in its "
  'own commit message two minutes after writing it (7,815 links became 7,826 when the guard rows were added). '
  "Process note for the next session: this pass's rows were renumbered twice in one day to avoid same-day id "
  'collisions — first off F63 (arena/a746a9f2), then off F64-F67 (arena/b23f12f0, whose F67 is the '
  'duplicate-ID guard that has now caught both collisions). Renumbering is cheap while a PR is open and '
  'expensive after it merges.',
  []),
 ('F74',
  'An article page existed on disk and on the live site that no data file or generator referenced: '
  'articles/sync-finish-two-buttons.html. Found independently twice on 2026-11-16; repaired the same day.',
  'articles/sync-finish-two-buttons.html vs data/articles.json (no matching slug); file removed 2026-11-16',
  'Found 2026-11-16 by session arena/19d92a81 during the line-by-line repo review, after the file arrived with '
  "a parallel pass's merge. data/articles.json carries no 'sync-finish-two-buttons' slug and no build step "
  'generates the page, so nothing will ever refresh or retire it - yet it is served publicly next to the '
  'generated articles and looks exactly like them, disclosure bar included, so a reader cannot tell it is '
  'unmanaged. A grep of data/ and build.py finds zero references. It is the same defect class as F57 (orphan '
  'registers), one layer up: a page outside the data-driven set. Independent discovery the same day by '
  'arena/5ac82b1d during the final integration pass: articles/ held 20 HTML files against 19 registered slugs; '
  'the orphan carried the same TP-09 subject as the registered article sync-finish-explained.html and appeared '
  'in no sitemap entry, no articles index and no internal link - an orphan a crawler could still reach by '
  "direct URL, publishing a second unregistered answer to the same question. Its own passing session's "
  "completion record (X-121929a5) states this draft was discarded as a duplicate of round 11's TP-09 article; "
  'the register entry was dropped but the HTML file survived the merge, and no gate compared the articles/ '
  'directory against the page set the build emits (verify.py checks links from files that exist, so it cannot '
  'see a file nothing links to). DECISION EXECUTED 2026-11-16 by arena/5ac82b1d: deleted rather than '
  'registered - the canonical TP-09 article (articles/sync-finish-explained.html, data/topics.json '
  'published_as) already covers the subject, so registering the duplicate would publish the same question '
  'twice. check_no_orphan_pages() now fails the build if any .html file in articles/, products/, guides/, '
  'categories/ or the repo root is not generated by this build, and the guard was proven to fire on an '
  'injected file before it was committed.',
  []),
 ('F75',
  'The 404 page was published with relative links, but GitHub Pages serves it at any missing path — so every '
  'link on it broke under nested URLs.',
  '404.html (all href/src values)',
  "Found 2026-11-16 by arena/5ac82b1d while reading back the deleted orphan article's URL on the live site: "
  '/articles/sync-finish-two-buttons.html correctly served the 404 page, but its nav, card and stylesheet '
  'links resolved against /articles/ (e.g. products/chefman-6qt-dual-basket.html became '
  '/articles/products/...), so the error page it served was itself unstyled and full of dead links — the one '
  'page whose whole job is to recover a lost reader. Root-relative links (/Zone1/...) were rejected as a fix '
  'because verify.py and scripts/check_links.py resolve internal hrefs against the file on disk, where they do '
  'not exist. Fixed instead by rewriting every relative href/src on 404.html to its absolute SITE_URL form in '
  'layout(), leaving fragment-only links (#anchor) alone since they address the displayed document. '
  'check_seo_metadata() now fails the build if any non-absolute, non-fragment URL survives on the 404 page. '
  'Note for later: this defect can only be observed by fetching a missing nested URL from the deployed site — '
  'no local gate sees the serving path.',
  []),
 ('F76',
  'The tracking ID shopnow047c-20 is user-provided but is not validated in Associates Central, applied to '
  'links, or confirmed by a test.',
  'data/config.json (selected_tracking_id); data/product-intent.json (tracking_id_status); associate_tag left '
  'blank',
  'For each product the account holder confirms as intended, verify that the ID is active in Associates '
  'Central, create or select one enrolled Special Link, follow it, and verify that the click appears under '
  "that ID in the report. Apply no tag broadly until every intended product's test passes. No account login "
  'was available in this pass.',
  ['S5', 'S6', 'S2']),
 ('F77',
  'No intended ASIN or official listing URL is confirmed for any of the five supplied short links; each '
  'intended-product field remains blank.',
  'data/product-intent.json rows PI-01 to PI-05 (intended_asin, official_listing_url)',
  'The submitted URL strings, observed destinations and owner-confirmed intent are kept separate. No claim is '
  "made here about a short link's validity, compliance or intended product. Confirm the official listing "
  'separately for each link before filling intended fields.',
  ['S16', 'S28', 'S29', 'S36', 'S37']),
 ('F78',
  'Two new short-link fetches returned fallback-style Amazon pages whose titles identify meat thermometers, '
  'outside the current air-fryer publication scope.',
  'PI-04 and PI-05 in data/product-intent.json; observed targets B0DHZTCNR5 and B0DZFD6R9Z',
  "These are observed redirect destinations only; they do not establish the operator's intended products, "
  'invalidate the links, or establish compliance. Keep them unmapped and do not publish thermometer '
  'specifications unless product intent and scope are confirmed.',
  ['S36', 'S37']),
 ('F79',
  "S23 is registered as KDP's 'Linking from Your Website' help page, but earlier notes cited it as a general "
  'Amazon ASIN definition.',
  'data/sources.json S23; prior ASIN-format claims; data/product-intent.json',
  'Corrected in the final integration: the current product-intent page no longer cites S23 for ASIN length or '
  '/dp/ format. Do not use the supplied short-link tokens or observed redirects to infer intent. Verify a '
  'suitable first-party source before restoring an identifier-format claim.',
  ['S23']),
 ('F80',
  "Neither newly submitted link reconciles with its manufacturer's own catalogue, so the two candidate "
  'listings cannot be closed by reading harder.',
  'PI-04, PI-05 on the link-intent record',
  "Both links submitted on 2026-11-17 were read the same day against the brands' own product pages rather than "
  "against the Amazon listings they resolved to. The observed ThermoMaven listing is titled '1 Sec "
  "Professional Digital Meat Thermometer, ±0.5℉ Accuracy | NIST&NSF Certified …'; ThermoMaven's site names its "
  "instant-read line F1 Pro and F1 Turbo with a sub-second read and does not use '1 Sec' as a model name. The "
  'observed CHEF iQ listing is the iQ Sense Gen3 with three probes; the brand page states model CQ60-3C-Z3-E '
  "and an ambient rating the listing omits, and names air-fryer use among the product's heat environments. A "
  'marketing phrase in a listing title and a brand model designation are different kinds of identifier, and '
  'neither page mentions an ASIN — so the observed destinations stand as observations, the intended fields '
  'stay null, and no product page is written for either. The two brand pages are registered as S39 and S40, '
  "and their hosts are in verify.py's allow-list, which records that they are official brand sites, not that "
  'they settle an identity. Decision needed: say what each link was created to promote (Q-27), or drop the two '
  'rows — SG-36 lays out the paths. Recorded by arena/58cbaaa2, which re-scoped twice against the merged '
  'registers rather than publish a parallel one.',
  ['S39', 'S40', 'S36', 'S37', 'S23']),
 ('F81',
  'The inference that a landing URL without a visible tag casts doubt on attribution was an over-reading, and '
  'it is corrected on the record instead of edited out of it.',
  'product-intent.html, data/product-intent.json, data/decision.json, F76',
  'Passes including this one cited the absence of a tag= parameter on an observed landing URL next to their '
  "caution about attribution. Amazon's help node read on 2026-11-17 (S41) states that 'it is not necessary for "
  "your unique ID to appear in order for us to track sales made after the initial click through', because the "
  "shopping session is tagged on Amazon's side. A null observation is not a negative one: the clean landing "
  'URLs neither support nor undermine attribution. The correction is applied where the inference is drawn in '
  'the present tense — the link-intent page now says so in those words next to the per-row test fields — and '
  'the dated rows are untouched, because they are records of what those passes saw. The sibling node (S42) '
  'names where the real confirmation is read, the Tracking ID Summary Report, plus the screen that creates IDs '
  'and the limit of 100 per account; that is what the per-row associates_link_test_* fields are waiting for, '
  "and Q-28/SG-37 are the owner's five minutes.",
  ['S41', 'S42', 'S6', 'S2']),
 ('F82',
  'A present-tense sentence still counted the submitted links at three, two days after the register grew to '
  'five.',
  'categories/kitchen-appliances.html lede',
  "Found 2026-11-17 while re-scoping this session against main, in the same class main's F77/F79 lineage "
  "describes but with the narrative rather than a value out of date: the category lede opened 'The three "
  "supplied links were observed landing on air fryer or air fryer-oven listings on 2026-11-13/14', which was "
  'true at the time and is now a partial description of a five-row register whose two newest rows sit under '
  'Thermometers & Timers. The sentence is repaired where the tense is present — the lede reads its counts from '
  "len(rows) and from the register's own observed_listing_category field — and check_submitted_link_count() "
  'fails the build if a present-tense surface asserts a different count in its own words — both directions '
  'proven on 2026-11-17: the current tree builds silently, and injecting the old phrase back into the lede '
  "exited non-zero with the register's own row count named in the message. (A first version of the pattern "
  "required a lead-in word like 'all' and matched nothing, which is how a guard that cannot fail gets shipped: "
  'the negative test is the guard.) The scope is narrowed to the shopper surfaces and the two registers: a '
  "dated verification row that says 'all three supplied links' is a true statement about 2026-11-14, and a "
  'check that could only be satisfied by rewriting history is worse than no check. Process note for whoever '
  'next receives a link: add a row to data/product-intent.json — never a sentence.',
  ['S17', 'S2']),
 ('F96',
  'The FAFO-001 manual contradicts itself about extension cords; the conflict remains unresolved.',
  'Emeril manual Important Safeguards item 9 vs Attaching the Power Cord; re-read 2026-11-19',
  'Item 9 says NEVER use with an extension cord, while the later power-cord section permits longer cords with '
  'conditions. The previous article quoted one passage and called it an absolute difference between manuals. '
  'That account is corrected. Do not infer permission from the later paragraph: seek manufacturer '
  'clarification for the exact unit and appropriate electrical advice. The site supplies no cord '
  'recommendation. Independent PUB-1 scoped review and regression/HTTP/browser evidence are retained in '
  'reports/verification-2026-11-19-1f9e7d52.md. Read 2026-11-19. Safeguards item 9 says never use an extension '
  'cord; the later power-cord section conditionally permits longer cords. The prior guide quoted only the '
  'prohibition. Both statements are now recorded, not selected between. This is not permission to use an '
  'extension cord. Obtain current manufacturer clarification for the exact unit before relying on a setup '
  'affected by the conflict.',
  ['S15']),
 ('F97',
  'Several articles made false absence claims or unsupported inferences despite passing source-presence tests; '
  'corrected in place on 2026-11-19.',
  'All 24 existing article bodies; reports/publication-2026-11-19.md',
  'The 8 Qt manual explicitly warns against aerosol spray. The Emeril manual includes a 6 lb (2721 g) '
  'rotisserie spit limit, preset times and an internal-temperature chart. Both Chefman manuals contain '
  'practical oil advice. Removed unsupported probability rankings for model matches, serving/footprint and '
  'energy assumptions, and seasonal stock-switch/trend claims. A citation or valid value placeholder does not '
  'verify the sentence containing it. No human product test or current public-health validation is claimed. '
  'Independent PUB-1 scoped review and regression/HTTP/browser evidence are retained in '
  'reports/verification-2026-11-19-1f9e7d52.md. The previous buying guide called all three appliances '
  'dishwasher-safe and left the 8 Qt dimensions blank after they were sourced. The capacity article also '
  'called 6 qt and 8 qt the same nominal total. The revised guides distinguish removable parts from the main '
  "unit, Emeril's hand-wash recommendation, model-specific dimensions and divided vs undivided capacity. An "
  'unsupported most-common-return assertion was removed. The full prose review also removed unsupported '
  'serving-load ratios, cooking/durability claims, electrical-circuit assumptions, exact-energy-cost '
  'implications, guessed model explanations and a nutrition-regulatory classification. It corrected the 8 Qt '
  'aerosol caution and the disclosure placement. All 24 existing guides were revised without adding duplicate '
  'slugs. These are content corrections, not evidence of better conversion.',
  ['S13', 'S15', 'S18', 'S8', 'S10', 'S12', 'S14']),
 ('F98',
  'Article datePublished and RSS pubDate inherited a global source-access date and invented a 09:00 '
  'publication time; repaired.',
  'build.py article_jsonld/RSS/sitemap; data/articles.json',
  'First-publication timestamps are not established, so published_at stays null and those optional output '
  'fields are omitted. Actual authored modified_at and scoped source_checks are separate, stable data. The '
  'sitemap describes real publication-content edits rather than pretending the entire source register was '
  're-read. A successful build is not historical publication evidence.',
  []),
 ('F99',
  'The old browser, event registers and example endpoints did not share one analytics protocol; corrected '
  'without enabling production collection.',
  'analytics/client.js, analytics/collector.py, data/measurement.json, data/analytics-plan.json',
  'The four browser events and operator-only affiliate_report_import now share one tested named schema. The '
  'canonical client is emitted verbatim, incompatible PHP/Worker examples return 410, and both switches stay '
  'off. Local tests are not a deployed same-origin runtime, approved privacy notice or authorised Associates '
  'report. No order or attribution was invented. Independent PUB-1 scoped review and regression/HTTP/browser '
  'evidence are retained in reports/verification-2026-11-19-1f9e7d52.md. One named-event contract now covers '
  'the actual browser source, collector, deployment gates and privacy notice. Synthetic client payloads are '
  'posted to the real HTTP handler in an isolated database. The old raw-event PHP/Worker endpoints return 410. '
  'No production endpoint or traffic is claimed; hosting and privacy approval remain open.',
  ['S2', 'S38']),
 ('F100',
  'Repaired 2026-11-19: blanket no-data privacy wording omitted hosting IP logs and local decision drafts.',
  'Canonical footer, about page, measurement notices',
  'The site-specific notice now distinguishes no publisher analytics from GitHub Pages security IP logs and '
  'browser-only localStorage decision drafts. Enabled notices describe page views and engagement as well as '
  'clicks. The browser run also exposed socketserver’s fallback transport-error traceback, which can print a '
  'client address even with request access logs disabled. The production server now suppresses expected '
  'disconnects and emits only a fixed nonidentifying diagnostic for unexpected errors, with negative log '
  'tests. Proxy/hosting infrastructure logging and the production notice still require a separate deployment '
  'review.',
  ['S38', 'S2']),
 ('F101',
  'Open boundary: production analytics, Search Console ownership and enrolled Associates validation are not '
  'deployed/account-verified.',
  'Recorded tracking ID shopnow047c-20, all five submitted links, empty campaign ledger',
  'Code, primary-source research and static publication work are complete within repository authority. No '
  'account ownership, intended listing, tracking-ID application, click/order report, live collector or search '
  'performance is invented. Confirm one intended listing and permitted enrolled Special Link workflow per '
  'product, then record dated first-party evidence before applying the ID broadly. A missing visible tag is '
  'not evidence of link failure.',
  ['S2', 'S41', 'S42', 'S44']),
 ('F109',
  'Amazon revised the Program Policies on 14 April 2026 and this register carried on quoting clause text without recording the revision until today.',
  'data/compliance.json C8 and C10, the Commission Income Statement and Original Content rows, and any future paid-promotion plan',
  "Found 2026-11-19 by arena/0c5c10d0-zone1. The live Program Policies page has read “Updated: April 14, 2026” on every pass since 2026-11-15, and the register recorded that stamp; what it never recorded is what changed. Amazon's linked change notice lists four items: a 180-day shipping-and-payment condition on qualifying purchases, a broadened disqualifier for products referred through any paid or boosted advertisement, an onsite-commission scope narrowed to Direct Qualifying Purchases of the same ASIN variant as the linked product page, and a new definition of original content requiring commentary, analysis or transformation. Only the first was confirmed from a direct read of the live policy text today, and it is now quoted as C19. The other three are NOT quoted anywhere on this site as verified policy text: two direct fetches of the change notice (S46) failed this pass, so they are recorded as a re-read task, not as rules with citations. C8 keeps its own dated quote and remains accurate about what it quoted; whether the surrounding clause has since been broadened is unresolved and C8 should be re-read against the live text before anyone plans a paid promotion.",
  ['S2', 'S46']),
 ('F105',
  'A queued editorial premise said an air fryer is built to run unattended. The manual for the machine in question says the opposite, so the premise was dropped before the page was written.',
  'data/topics.json TP-22 hook, and any copy that frames these appliances as set-and-forget',
  'Found 2026-11-19 by arena/0c5c10d0-zone1 while preparing articles/probe-in-an-air-fryer.html. The queued hook read “The appliance is built to run unattended”. The RJ38-SQPF-3TDB-2W safety list states “Do not leave the air fryer unattended during use” (S18, read live this session), and the Emeril FAFO-001 manual never grants it either: it describes a 3-minute idle auto-off, a 20-second fan run-on after the cycle and a cool-down of at least 30 minutes before cleaning or storing (S15). The published article answers what each document states instead of repeating the premise, and the hook text stays in Git history rather than being silently rewritten. The standing rule this reinforces: a topic card is a hypothesis, not a source.',
  ['S18', 'S15']),
 ('F106',
  'The Emeril extension-cord conflict is not a translation artefact: the French safeguard list and the French wiring note contradict each other the same way the English ones do.',
  'Emeril FAFO-001 manual (S15) — a second observation for F96, which stays open',
  'Read 2026-11-19 by arena/0c5c10d0-zone1. English safeguard 9 states “NEVER use with an extension cord”. French safeguard 9 states “NE JAMAIS utiliser avec une rallonge”. The French “MISE EN GARDE : Branchement du Cordon D’Alimentation” block then says longer extension cords are available and may be used with care, with rating and routing conditions — the same pair of instructions F96 records in the English text. That narrows the remedy: a reader cannot resolve the conflict by switching language, and current manufacturer clarification for the exact unit is still the only way out. This row adds an observation; it closes nothing.',
  ['S15']),
 ('F107',
  'The CHEF iQ iQ Sense page describes its own sensors two ways on one page: five internal sensors in the prose, four internal plus one ambient in the feature list.',
  'S39 (brand page) read against the observed Amazon listing title (S37)',
  'Read 2026-11-19 by arena/0c5c10d0-zone1. The product description states “Five internal sensors and heat resistance up to 1000°F”, while the feature list below it states “4 internal temperature sensors for accuracy within 1°F” and “1 ambient temperature sensor”. The observed listing title says “5 Sensors”. All three are consistent with four internal plus one ambient, and no official document read here defines what the word “internal” counts, so the article cites the feature list and warns against the prose sentence. No probe count, accuracy figure or heat rating is published here as a verified specification, and none of it confirms an intended ASIN for PI-05.',
  ['S39', 'S37']),
 ('F108',
  '“Before first use” is not the same procedure in the three manuals, and the clearance figure differs too, so one generic first-week paragraph would have been wrong for at least one product.',
  'S15, S18, S13 (owner’s manuals) — the separation a future TP-19 guide must keep',
  'Read 2026-11-19 by arena/0c5c10d0-zone1. The Emeril manual ends Before First Use with a burn-in: “preheat the appliance for a few minutes to allow the manufacturer’s protective coating of oil to burn off. Wipe the appliance with warm, soapy water and a dishcloth after this burn-in cycle”, and its French note warns of smoke or a burnt smell on first use caused by those coating oils. Both Chefman manuals stop at unpack, wipe and wash, and state only that on first use “the unit may emit a slight odor, which is normal and will dissipate with use”; neither instructs a burn-in. Clearance: Emeril asks for at least 5 inches of free space on the top, back and sides; the 8 Qt Chefman asks for at least 6 inches on top and back. A combined setup guide therefore has to publish three procedures, not one — one reason TP-19 was held this pass.',
  ['S15', 'S18', 'S13']),
 ('F102',
  'Repaired 2026-11-19: the row-source gate accepted a generic flag link and skipped data rows containing a '
  'row header.',
  'row_is_sourced / check_row_sources and canonical implementation/evidence tables',
  'A direct audit found 27 rows with no registered primary-source or repository evidence link. The gate now '
  'requires an actual registered primary URL, an exact supplied resolver URL, or an existing exact-file record '
  'in this repository. It checks data rows with th scope=row as well as td-only rows, and rejects generic '
  'Flagged links, unrelated GitHub repos and unregistered URLs on an otherwise official host. '
  'Editorial/implementation rows now link their authoritative repository record. Coverage and link identity '
  'are machine-checked; whether a source supports arbitrary prose still requires an actual scoped read. SG-48 '
  'records that boundary.',
  ['S2']),
 ('F103',
  'Found 2026-11-19: public historical builds in the Pages artifact publish Amazon product links without '
  'rel="sponsored" and describe the supplied short-link tokens as "invalid".',
  'Pages artifact (.github/workflows/pages.yml uploads the whole repository root); s2/pages/products.html; '
  'dashboard/, research/, site/, annex-88769516/, session-3740f69d/',
  'Checked 2026-11-19. The Pages workflow uploads the repository root, and a live read of '
  'https://kanlerxz87-cyber.github.io/Zone1/s2/pages/products.html returned the historical page. That page '
  'labels each supplied token "invalid" because it has 9 characters. This site does not draw that conclusion: '
  'token length does not establish that a link is invalid, and the brief forbids the claim. A static scan of the '
  'published HTML found product-type Amazon anchors without a sponsored token in s2 (68 of 68), '
  'session-3740f69d (118 of 118), annex-88769516 (9 of 9), dashboard (47 of 56), research (43 of 55) and site '
  '(20 of 26). The canonical root has 8 such anchors, all the deliberate nonsense-token resolver control '
  'ZZZ9ZZZZZ, which build.py does not classify as a product link; its other 235 product anchors are qualified. '
  'No change was made in this pass: the historical generators are declared read-only, and their own '
  'reproducibility gates compare committed HTML.',
  ['S1', 'S2', 'S31', 'S38']),
 ]

REPO_EVIDENCE = {'F80': ['data/product-intent.json', 'product-intent.html', 'session-58cbaaa2/artifacts/README.md'],
 'F81': ['product-intent.html', 'data/product-intent.json', 'reports/verification-2026-11-17-58cbaaa2.md'],
 'F82': ['build.py', 'data/product-intent.json', 'reports/verification-2026-11-17-58cbaaa2.md'],
 'F83': ['data/decision.json', 'data/flags.json', 'handover.html', 'decisions.html', 'build.py'],
 'F84': ['build.py', 'data/decision.json', 'data/requirements.json', 'data/articles.json'],
 'F85': ['data/topics.json',
         'data/design-prompt.json',
         'build.py',
         'reports/verification-2026-11-17-fd9778a1.md'],
 'F86': ['data/products.json', 'data/sources.json', 'reports/verification-2026-11-17-fd9778a1.md'],
 'F87': ['data/suggestions.json', 'data/questions.json', 'reports/verification-2026-11-17-fd9778a1.md'],
 'F88': ['verify.py', 'data/design-prompt.json', 'assets/style.css'],
 'F89': ['data/suggestions.json',
         'data/decision-log.json',
         'build.py',
         'reports/verification-2026-11-17-fd9778a1.md'],
 'F90': ['build.py', 'reports/verification-2026-11-19-9b3365c7.md'],
 'F91': ['data/product-intent.json',
         'build.py',
         'tests/test_integration_output.py',
         'reports/verification-2026-11-19-9b3365c7.md'],
 'F92': ['data/questions.json', 'reports/verification-2026-11-19-9b3365c7.md'],
 'F93': ['COORDINATION.md', 'reports/verification-2026-11-19-9b3365c7.md'],
 'F94': ['build.py', 'data/decision-log.json'],
 'F95': ['data/product-intent.json', 'data/reverification.json', 'reports/verification-2026-11-19-9b3365c7.md'],
 'F74': ['build.py', 'data/articles.json', 'data/topics.json', 'reports/verification-2026-11-16-19d92a81.md'],
 'F75': ['build.py', '404.html'],
 'F76': ['data/config.json', 'data/product-intent.json'],
 'F77': ['data/product-intent.json'],
 'F78': ['data/product-intent.json'],
 'F79': ['data/sources.json', 'build.py'],
 'F63': ['data/questions.json', 'data/suggestions.json', 'data/decision.json'],
 'F20': ['s2/index.html',
         'site/index.html',
         'dashboard/index.html',
         'research/index.html',
         'session-3740f69d/index.html',
         'docs/index.html'],
 'F22': ['EXECUTIVE_SUMMARY.md'],
 'F23': ['scripts/build.mjs'],
 'F25': ['scripts/check_links.py',
         'dashboard/',
         'research/',
         'site/',
         's2/',
         'session-3740f69d/',
         'annex-88769516/'],
 'F26': ['data/platform.json'],
 'F29': ['session-54c66535/EVIDENCE-2026-11-14.md', 'data/products.json'],
 'F30': ['session-54c66535/EVIDENCE-2026-11-14.md', 'session-54c66535/pass6.json'],
 'F31': ['session-54c66535/EVIDENCE-2026-11-14.md'],
 'F32': ['session-6b2eddeb/EVIDENCE-2026-11-14.md', 'data/products.json', 'site/', 'research/'],
 'F33': ['session-6b2eddeb/EVIDENCE-2026-11-14.md'],
 'F34': ['EXECUTIVE_SUMMARY.md'],
 'F35': ['build.py', 'site/', 'session-3740f69d/'],
 'F41': ['session-81495d2d/EVIDENCE-2026-11-14.md', 'session-ce4070ad/EVIDENCE-2026-11-14.md'],
 'F47': ['data/flags.json', 'data/sources.json'],
 'F48': ['data/products.json'],
 'F49': ['reports/verification-2026-11-15.md'],
 'F42': ['suggestions.html', 'questions.html', 'data/flags.json', 's2/'],
 'F43': ['suggestions.html', 'questions.html'],
 'F44': ['dashboard/',
         'annex-88769516/',
         'session-3740f69d/',
         'research/',
         's2/',
         'site/',
         'docs/',
         'sitemap.xml'],
 'F45': ['build.py', 'sitemap.xml'],
 'F64': ['data/questions.json', 'data/articles.json', 'data/products.json', 'build.py'],
 'F65': ['data/sources.json', 'data/products.json'],
 'F66': ['data/sources.json', 'data/products.json'],
 'F67': ['build.py', 'flagged.html'],
 'F68': ['reports/asin-model-mapping-2026-11-16.md', 'data/products.json', 'build.py'],
 'F69': ['data/products.json'],
 'F70': ['data/products.json'],
 'F71': ['data/products.json'],
 'F72': ['data/products.json'],
 'F73': ['data/requirements.json', 'build.py'],
 'F96': ['reports/publication-2026-11-19.md',
         'data/articles.json',
         'reports/verification-2026-11-19-1f9e7d52.md',
         'build.py'],
 'F97': ['reports/publication-2026-11-19.md',
         'data/articles.json',
         'reports/verification-2026-11-19-1f9e7d52.md',
         'build.py'],
 'F98': ['build.py',
         'data/articles.json',
         'tests/test_editorial_metadata.py',
         'reports/verification-2026-11-19-1f9e7d52.md'],
 'F99': ['analytics/README.md',
         'analytics/client.js',
         'analytics/collector.py',
         'tests/analytics-client.test.cjs',
         'reports/verification-2026-11-19-1f9e7d52.md',
         'build.py',
         'tests/test_analytics_contract.py',
         'tests/browser/measurement.spec.cjs'],
 'F100': ['reports/verification-2026-11-19-1f9e7d52.md',
          'build.py',
          'analytics/collector.py',
          'tests/test_analytics.py'],
 'F101': ['reports/verification-2026-11-19-1f9e7d52.md', 'build.py'],
 'F102': ['reports/verification-2026-11-19-1f9e7d52.md', 'build.py', 'tests/test_publication.py'],
 'F103': ['reports/verification-2026-11-19-1970a80b.md', 'build.py', '.github/workflows/pages.yml'],
 'F105': ['data/topics.json', 'articles/probe-in-an-air-fryer.html', 'reports/verification-2026-11-19-0c5c10d0.md'],
 'F106': ['reports/verification-2026-11-19-0c5c10d0.md', 'articles/extension-cord-rules-in-the-manuals.html'],
 'F107': ['articles/probe-in-an-air-fryer.html', 'reports/verification-2026-11-19-0c5c10d0.md'],
 'F108': ['reports/verification-2026-11-19-0c5c10d0.md', 'data/topics.json'],
 'F109': ['data/compliance.json', 'reports/verification-2026-11-19-0c5c10d0.md', 'data/sources.json']}
VERDICTS = {
    "chefman-6qt-dual-basket":
        "The published specification set is the most complete of the three: capacity, temperature range, dimensions, weight, power draw, safety approval and warranty are all stated by the manufacturer. Two independently controlled baskets with a Sync Finish function and a 450 °F ceiling address the main real-world complaint about single-basket air fryers — that you cannot cook two things at different temperatures at once. The one number a shopper most wants, cost per quart, cannot be computed here because the Amazon price is not available to this site by policy; the brand list price of $119.99 for 6 quarts is the only comparable figure that can be stated.",
    "emeril-26qt-french-door":
        "The largest cavity in the set by a wide margin (26 qt against 6 qt and 8 qt) and the only unit that is an oven rather than a basket. The manufacturer documents the power draw (1700 W), the temperature range (75–500 °F) and the physical footprint, which is what actually decides whether it fits a kitchen. On preset count the manual is the controlling document: its chart names exactly 24 presets, which matches the description text and the Amazon title rather than the spec block's 25. The brand's own on-site rating is unusually low (2.6 from 25 reviews) and is reported here as displayed, not softened.",
    "chefman-8qt-turbofry":
        "A conventional single-basket 8-quart air fryer with a documented 200–400 °F range, four food-type presets and dishwasher-safe nonstick parts. The unresolved problem is that the Amazon listing title advertises a 450 °F Hi-Fry mode and bake/dehydrate/frozen functions that the RJ38-SQSS-8T page and manual do not document. A 2026-11-14 read found that Chefman sells a second 8-quart SKU, RJ38-8T-BLACK, whose page states exactly that Hi-Fry mode and exactly those four functions — so the listing probably describes a different unit rather than a stale page (flag F33). The listing has since been read: its own Part Number row identifies RJ38-SQSS-8T and its own spec table states a 400 °F maximum (S29, read 2026-11-16). So the 450 °F wording in the title is contradicted by the page that carries it — but because a second Chefman 8 Qt page documents exactly that 450 °F Hi-Fry (S26), the honest position is unchanged in kind: the temperature ceiling of the machine that ships against this ASIN is not something this site will assert, and a buyer should read the manual in the box. See F3, F33 and F68.",
}


def page_category():
    products = {p["slug"]:p for p in PRODUCT_LIST}
    body = f"""<p class="crumbs"><a href="../index.html">Home</a> / Air fryers &amp; countertop ovens</p><p class="section-eyebrow">Find your fit</p><h1>A basket, two baskets, or an oven?</h1><p class="lede">Start with the layout that suits your meals. These three documented options have different capacities and care rules; none is an overall winner without a test.</p>
{publication_byline('../')}
<div class="grid grid-3">{''.join(product_card(products[r['slug']],'../') for r in PUBLICATION['products'])}</div>
<p class="section-note">The {_num_word(N_SUBMITTED_LINKS)} submitted links are kept in a <a href="../product-intent.html">separate intent register</a>. {_num_word(_submitted_links_in_category()).capitalize()} returned air-fryer titles; the others returned thermometer titles. Observed destinations are not confirmation of the intended listing or Associates attribution.</p>
<div class="publication-compare-cta"><div><h2>Measure first. Compare second.</h2><p>Published dimensions are only the starting point; read the model’s clearance and care instructions too.</p></div><a class="btn" href="../compare.html">Open the comparison →</a></div>
<div class="grid grid-2">{article_teaser('air-fryer-capacity-guide','../')}{article_teaser('small-kitchen-air-fryer-dimensions','../')}</div>
{reader_capture('../')}"""
    return layout('categories/kitchen-appliances.html','Air fryers & countertop ovens',body,active='categories/kitchen-appliances.html',description='Choose between a dual-basket air fryer, a single basket and a countertop oven using documented capacity, dimensions and care requirements.',jsonld_blocks=[breadcrumbs_jsonld([('Home',SITE_BASE),('Air fryers & ovens',page_url('categories/kitchen-appliances.html'))])])


def page_compare():
    products = {p["slug"]:p for p in PRODUCT_LIST}
    ordered = [products[r["slug"]] for r in PUBLICATION["products"]]
    def spec(product, labels):
        row = next((r for r in product["specs"] if r["label"] in labels), None)
        if row and row["value"] is not None:
            return e(row["value"]) + '<div class="tiny">'+src_links(row["source"])+"</div>"
        return '<span class="blank">— not confirmed —</span> '+src_links(row["source"] if row else BUYING_BY_SLUG[product['slug']]['sources'])
    head = ''.join(f'<th scope="col"><a href="products/{p["slug"]}.html" data-analytics-event="comparison_interaction" data-analytics-target-id="{e(p["slug"])}">{e(BUYING_BY_SLUG[p["slug"]]["title"])}</a></th>' for p in ordered)
    rows=[]
    for label, labels in [('Published capacity', ['Capacity']),('Exterior dimensions', ['Dimensions','Dimensions / weight']),('Documented temperature range',['Temperature range']),('Power',['Power','Rated power','Wattage'])]:
        rows.append('<tr><th scope="row">'+label+'</th>'+''.join('<td>'+spec(p,labels)+'</td>' for p in ordered)+'</tr>')
    care=[('Removable baskets and racks: top-rack dishwasher safe. Main unit: never immerse or dishwash.',['S18']),('Hand-washing accessories recommended. Main unit: never soak or dishwash.',['S15']),('Removable basket and rack: top-rack dishwasher safe. Main unit: never immerse or dishwash.',['S13'])]
    rows.append('<tr><th scope="row">Care instructions</th>'+''.join('<td>'+e(text)+'<div class="tiny">'+src_links(ids)+'</div></td>' for text,ids in care)+'</tr>')
    rows.append('<tr><th scope="row">Check before buying</th>'+''.join('<td>'+e(BUYING_BY_SLUG[p['slug']]['check'])+'<div class="tiny">'+src_links(BUYING_BY_SLUG[p['slug']]['check_sources'])+'</div></td>' for p in ordered)+'</tr>')
    body=f"""<p class="crumbs"><a href="index.html">Home</a> / Compare</p><p class="section-eyebrow">The useful details, together</p><h1>Three formats. Side by side.</h1><p class="lede">Compare the space, capacity and care each documented model asks of you. No winner, no invented performance score—and no assumption that a submitted link is the intended listing.</p>{publication_byline()}
<div class="tablewrap" tabindex="0" role="region" aria-label="Air-fryer comparison, scroll horizontally on a small screen"><table class="comparison-table"><caption>Documented model comparison — not a test or a ranking</caption><thead><tr><th scope="col">What to compare</th>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div><p class="tablewrap-hint">Scroll sideways for every model and its official sources.</p>
<p class="small muted">The dual-basket 450 °F maximum is a two-minute Hi-Fry boost, not an unrestricted cook setting. {src_link('S18')} The 8 Qt brand-model range conflicts with the listing title’s 450 °F claim. {src_links(['S12','S29'])} Read the manual for the exact unit you would receive.</p>
<h2>What matters for your meals?</h2><div class="grid grid-3">{''.join(product_card(p) for p in ordered)}</div>
<p class="section-note">Use the <a href="data.html">full dataset</a> for every recorded field, dated listing observation and blank. Manufacturer and listing values are not silently combined. Official sources disagree on some temperatures, dimensions and counts; see <a href="flagged.html">the public review register</a>.</p>
{reader_capture()}"""
    return layout('compare.html','Compare air fryers & countertop ovens',body,active='compare.html',description='Compare documented air-fryer capacity, dimensions, temperature, power and care with a source in each populated cell. No performance ranking or revenue estimates.',jsonld_blocks=[breadcrumbs_jsonld([('Home',SITE_BASE),('Compare',page_url('compare.html'))])])


def page_guide():
    cards = ''.join(article_teaser(row['slug'],'../') for row in PUBLICATION['featured_guides'])
    body = f"""<p class="crumbs"><a href="../index.html">Home</a> / Buying guide</p><p class="section-eyebrow">Start here</p><h1>Make room for the right air fryer.</h1><p class="lede">Before comparing presets, answer four questions: what you cook, how you divide it, where the machine will live, and how you’ll clean it.</p>{publication_byline('../','2026-11-19')}
<h2>Choose the layout before the model.</h2><p>The Chefman dual-basket manual describes two 3-quart baskets with separate settings and Sync Finish. The 8-quart model uses a single basket. The Emeril is a 26-quart oven-style cavity with a documented rotisserie. Those layouts—not a universal capacity-to-people rule—are the useful starting point. {src_links(['S18','S12','S15'])}</p>
<h2>Give the counter a proper check.</h2><p>The published size does not include the space you need to open the appliance and operate it as instructed. The 8-quart Chefman manual calls for at least 6 inches above and behind it. The Emeril manual calls for at least 5 inches above, behind and at the sides, and says not to operate under hanging cabinets. Check the manual for your exact model rather than applying either rule to another unit. {src_links(['S13','S15'])}</p>
<h2>Read the care rules before the feature list.</h2><p>The two Chefman manuals permit their removable baskets and racks on the top rack of a dishwasher. That does not include the main unit. The Emeril manual recommends hand-washing accessories and says not to soak or dishwash the appliance. There is no basis here for calling all three equally easy to clean. {src_links(['S18','S13','S15'])}</p>
<h2>Check the claims that need a second look.</h2><p>The 8-quart listing title advertises a 450 °F Hi-Fry option, while Chefman’s page for RJ38-SQSS-8T documents a 200–400 °F range. The Emeril brand page uses 25 presets in an icon and 24 in its description. Do not turn these into extra features by combining the larger claims. {src_links(['S12','S29','S14'])}</p>
<div class="grid grid-2">{cards}</div><p class="small"><a class="btn" href="../compare.html">Compare the documented details →</a></p><p class="small muted">No cooking results, portion counts or energy savings were measured here. These guides are document research, not a substitute for the full safety instructions for the unit you receive.</p>"""
    return layout('guides/buying-guide-air-fryers.html','How to choose an air fryer',body,active='articles/index.html',description='A practical air-fryer buying route through format, capacity, counter clearance, cleaning and exact-model checks.',jsonld_blocks=[breadcrumbs_jsonld([('Home',SITE_BASE),('Buying guide',page_url('guides/buying-guide-air-fryers.html'))])])


def page_data():
    rows = []
    for p in PRODUCT_LIST:
        for s in p["specs"]:
            state = "verified" if s["value"] is not None else "unverified"
            value = e(s["value"]) if s["value"] is not None else '<span class="blank">— blank —</span>'
            note = ""
            if s["value"] is None:
                note = f'<div class="tiny muted" style="margin-top:.3rem">{e(s["unverified"])}</div>'
            elif s.get("note"):
                note = f'<div class="tiny muted" style="margin-top:.3rem">{e(s["note"])}</div>'
            rows.append(
                f'<tr>'
                f'<td>{e(p["short_name"])}<div class="tiny muted">candidate ASIN {e(p["asin"]["v"])} (unconfirmed)</div></td>'
                f'<td>{e(s["label"])}</td>'
                f'<td>{value}{note}</td>'
                f'<td>{flag_pill(state)}</td>'
                f'<td>{src_links(s["source"])}</td>'
                f'</tr>'
            )
    total = len(rows)
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Full dataset</p>
<h1>Full dataset — every field, every source, every gap</h1>
<p class="lede">This is the machine-readable table the site is generated from, rendered for humans. {total} specification rows across three products. Each row shows the value, whether it is verified, and a clickable link to the official page it came from. Rows with no official source are blank on purpose.</p>

<div class="callout info">
  <strong>Every row carries a source link, by design</strong>
  <p class="small">The generator refuses to render a value without a source id, and the build reports any row that has a value but no source. That is why the "Official source" column is never empty — it either holds a link to an official page or says, explicitly, that there is none.</p>
</div>

<div class="tablewrap">
<table>
  <caption>Specification register</caption>
  <thead><tr><th style="width:18%">Product</th><th style="width:18%">Field</th><th style="width:36%">Value</th><th style="width:10%">Status</th><th style="width:18%">Official source</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
</div>

<h2>Program facts register</h2>
<p class="small">The compliance facts used throughout the site, with their sources, live on the <a href="../compliance.html">Compliance</a> page. The rate table, payment minimums and attribution windows are reproduced there verbatim from the official documents.</p>

<h2 id="sources">Source register</h2>
<div class="tablewrap">
<table>
  <caption>All {len(SOURCES['sources'])} sources used, with what each one verifies</caption>
  <thead><tr><th>ID</th><th>Publisher</th><th>Document</th><th>Covers</th><th>Directness</th></tr></thead>
  <tbody>
  {''.join(f'<tr><td>{src_link(s["id"])}</td><td>{e(s["org"])}</td><td><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["title"])}</a><div class="tiny muted">{e(s.get("page_version",""))}</div></td><td class="small">{e(s["covers"])}</td><td class="small">{e(s["directness"])}</td></tr>' for s in SOURCES['sources'])}
  </tbody>
</table>
</div>
"""
    return layout("data.html", "Full dataset", body, active="data.html",
                  description="Complete specification register for three air fryers: every value, its verification status and the official source link.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Full dataset", page_url("data.html")),
    ])]
              )


def page_compliance():
    rows = "".join(
        f"""<tr>
          <td><strong>{e(r['id'])}</strong><div class="tiny muted">{e(r['topic'])}</div></td>
          <td>{e(r['requirement'])}
            <blockquote>{e(r['quote'])}<cite>{e(r['clause'])}</cite></blockquote>
          </td>
          <td>{src_links(r['source'])}</td>
          <td class="small">{e(r['how_implemented'])}</td>
        </tr>"""
        for r in COMPLIANCE["requirements"]
    )
    windows = "".join(
        f'<tr><td>{e(w["fact"])}</td><td>{e(w["value"])}</td><td>{src_links(w["source"])}</td></tr>'
        for w in COMPLIANCE["attribution_windows"]
    )
    pays = "".join(
        f'<tr><td>{e(x["method"])}</td><td class="num">${x["minimum_usd"]}</td>'
        f'<td class="num">{("$" + str(x["maximum_usd"])) if x["maximum_usd"] else "—"}</td>'
        f'<td class="small">{e(x.get("extra",""))}</td><td>{src_links(x["source"])}</td></tr>'
        for x in COMPLIANCE["payment_minimums"]
    )
    bounties = "".join(
        f'<tr><td>{e(b["program"])}</td><td class="num">${b["bounty_usd"]:.2f}</td><td>{src_links(b["source"])}</td></tr>'
        for b in COMPLIANCE["bounty_examples"]
    )
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Compliance</p>
<h1>Policy text and implementation boundaries</h1><p class="small muted">This is a cited policy register, not Amazon approval or legal certification. Implementation notes were reconciled on 19 November; quotes retain their recorded source dates. Only the named sections in the scoped report were freshly re-read.</p>
<p class="lede">{len(COMPLIANCE['requirements'])} requirements that govern this site, each with the source text, a link to the official document, and a bounded statement of what this repository does about it. Where a rule is inconvenient, the rule wins and the feature is dropped.</p>

<div class="callout">
  <strong>The three rules that shape everything else</strong>
  <p class="small"><strong>Prices</strong> may only be shown when Amazon serves the link or via the official API. <strong>Reviews and star ratings</strong> may only be shown when obtained through that API. <strong>Program Content</strong> may not be aggregated, analysed, repurposed or used to train a model. Those three are why this site has no Amazon prices, no Amazon ratings, and no Amazon scraping pipeline — even though all three would have been easier to build. {src_links(['S2'])}</p>
</div>

<h2>Requirement register</h2>
<div class="tablewrap">
<table>
  <caption>Program and legal requirements mapped to implementation</caption>
  <thead><tr><th style="width:18%">Requirement</th><th style="width:40%">What the rule says</th><th style="width:10%">Source</th><th style="width:32%">How this build complies</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
</div>

<h2>Attribution windows</h2>
<div class="tablewrap">
<table>
  <caption>How long a click keeps earning — official definitions</caption>
  <thead><tr><th>Fact</th><th>Value</th><th>Source</th></tr></thead>
  <tbody>{windows}</tbody>
</table>
</div>

<h2>Payment minimums (US)</h2>
<div class="tablewrap">
<table>
  <caption>Payment minimum chart, reproduced from the Commission Income Statement</caption>
  <thead><tr><th>Method</th><th>Minimum</th><th>Maximum</th><th>Notes</th><th>Source</th></tr></thead>
  <tbody>{pays}</tbody>
</table>
</div>

<h2>Standard commission income rates</h2>
{rate_table()}

<h2>Bounty events (US) — published programme amounts</h2>
<div class="tablewrap">
<table>
  <caption>Special Commission Income: bounty programmes and amounts</caption>
  <thead><tr><th>Bounty-eligible programme</th><th>Bounty (USD)</th><th>Source</th></tr></thead>
  <tbody>{bounties}</tbody>
</table>
</div>
<p class="tiny muted">{e(COMPLIANCE['bounty_note'])}</p>

<h2>What a visitor should take from this page</h2>
<div class="grid grid-2">
  <div class="card">
    <h3 style="margin-top:0">If you are the buyer</h3>
    <p class="small" style="margin-bottom:0">The exact Amazon Associate disclosure appears at the top of every page. Product buttons also state that the supplied link's model identity and tracking tag are unconfirmed, followed by a link-level explanation. The disclosure is generated into the layout and cannot be removed by a content update.</p>
  </div>
  <div class="card">
    <h3 style="margin-top:0">If you are the operator</h3>
    <p class="small" style="margin-bottom:0">This is the audit surface. When Amazon changes a rule, the page changes here first, then the build enforces it. The <a href="../flagged.html">flagged page</a> is the backlog of facts that still need a human decision before any copy can assert them.</p>
  </div>
</div>
"""
    return layout("compliance.html", "Compliance", body, active="compliance.html",
                  description="Amazon Associates and FTC compliance requirements, quoted with official source links and mapped to implementation.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Compliance", page_url("compliance.html")),
    ])]
              )


def page_flagged():
    # cross-product flags from products.json plus programme-level flags
    #
    # Sorted by numeric id on render. PROGRAMME_FLAGS is appended to by whichever pass raises a
    # flag first, and on 2026-11-19 two sessions added rows at once: the register order became
    # F101, F108, F104…F107, F102, F103. Renumbering the rows after the fact is the wrong fix —
    # ids are cited from articles, topics and the question registers, so a renumber would chase
    # references forever. Sorting at render keeps the published ids stable and the table readable.
    # (2026-11-19, arena/0c5c10d0-zone1.)
    def _flag_sort_key(row):
        fid = str(row[0] or "")
        return (0, int(fid[1:])) if re.fullmatch(r"F\d+", fid) else (1, 0)

    prog_flags = sorted(PROGRAMME_FLAGS, key=_flag_sort_key)
    prod_flags = []
    for p in PRODUCT_LIST:
        for f in p["flags"]:
            if f["id"] in ("F1", "F6"):
                continue
            prod_flags.append((f["id"], f["issue"], p["short_name"], f["action"], f.get("sources", [])))

    def row(fid, issue, scope, action, srcs):
        parts = ([src_links(srcs)] if srcs else []) + [repo_link(p) for p in REPO_EVIDENCE.get(fid, [])]
        src_html = " ".join(parts) if parts else '<a href="data.html">dataset</a>'
        return (f'<tr id="{(fid or "").lower()}"><td class="num"><strong>{e(fid)}</strong></td>'
                f'<td>{e(issue)}<div class="tiny muted">Scope: {e(scope)}</div></td>'
                f'<td class="small">{e(action)}</td><td>{src_html}</td></tr>')

    # Resolved items are generated from the re-verification ledger so a future pass updates the
    # table by editing data/reverification.json rather than by editing this template.
    res = [t for t in REVERIFICATION["tests"] if t["verdict"] in ("conflict-resolved", "new-evidence")]
    resolved_rows = "".join(
        f'<tr><td class="num"><strong>{e(REVERIFICATION["pass_date"])}</strong></td>'
        f'<td>{e(t["claim"])}</td><td class="small">{e(t["observed_2026_11_14"])}'
        f'<div class="tiny muted">{e(t["note"])}</div></td>'
        f'<td class="small"><a href="{e(t["source_url"])}" target="_blank" rel="noopener">{e(t["source_label"])}</a></td></tr>'
        for t in res
    )
    # Pass 10 (2026-11-16) closed items too. They are rendered from the pass-10 ledger so
    # the table keeps its own source of truth rather than a hand-maintained list.
    if PASS10:
        for _t in PASS10["rows"]:
            if _t["verdict"] not in ("conflict-resolved", "new-evidence"):
                continue
            resolved_rows += (
                f'<tr><td class="num"><strong>{e(PASS10["pass_date"])}</strong></td>'
                f'<td>{e(_t["claim"])}</td>'
                f'<td class="small">{e(_t["observed"])}</td>'
                f'<td class="small"><a href="{e(_t["source_url"])}" target="_blank" rel="noopener">'
                f'{e(_t["source_label"])}</a></td></tr>'
            )
    resolved_rows += (
        '<tr><td class="num"><strong>2026-11-14</strong></td>'
        '<td>Chefman 8 Qt — blank Wattage and Dimensions rows</td>'
        '<td class="small">Both rows were blank because the 2026-11-13 pass had not read the brand page down to its '
        'Specifications block. Re-reading that page today produced "Power: 1700W/120V", "Dimensions: (8 Qt Model) '
        '15.4 in x 12.6 in x 13.5 in" and "Weight: (8 Qt Model) 12.8 lbs / 5.8 kg", so both rows are now filled and '
        'sourced to the manufacturer\'s own page.</td>'
        f'<td>{src_links(["S12"])}</td></tr>'
    )

    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Flagged for review</p>
<h1>Flagged for review</h1>
<p class="lede">Source conflicts, missing facts and dated repairs are kept in public. This register includes historical and already-repaired findings—not a count of currently open work. Read each row’s date and action; current implementation states are on the Suggestions page. Unconfirmed facts stay explicit and do not block the honest publication.</p>

<div class="grid grid-4" style="margin-bottom:1rem">
  <div class="stat"><div class="n">{len(prog_flags) + len(prod_flags)}</div><div class="l">Recorded findings</div><div class="h">History included; not all open</div></div>
  <div class="stat"><div class="n">{len(SOURCES['sources'])}</div><div class="l">Registered sources</div><div class="h">Read dates and scopes stay separate</div></div>
  <div class="stat warn"><div class="n">{sum(r['value'] is None for p in PRODUCT_LIST for r in p['specs'])}</div><div class="l">Blank specification fields</div><div class="h">Unknown values are not back-filled</div></div>
  <div class="stat"><div class="n">{sum(r['value'] is not None for p in PRODUCT_LIST for r in p['specs'])}</div><div class="l">Populated specification rows</div><div class="h">With declared primary-source evidence</div></div>
</div>

<div class="callout warn">
  <strong>A model conflict—not a guessed explanation.</strong>
  <p class="small">The observed Chefman 8 Qt listing title advertises 450 °F Hi-Fry, while the RJ38-SQSS-8T brand page gives a 200–400 °F range. Both claims are recorded. This does not establish why the sources disagree or which unit will ship; no “most likely” model explanation is selected. Match the exact current listing/model documents and seek clarification before relying on the disputed feature. {src_links(['S12','S13','S29'])}</p>
  <p class="small">A separate electrical-safety conflict remains unresolved in the Emeril manual: incompatible extension-cord instructions. Do not select the permissive passage as permission; seek current manufacturer clarification for the exact unit. <a href="#f96">F96</a>. {src_link('S15')}</p>
</div>

<h2>Programme-level flags</h2>
<div class="tablewrap">
<table>
  <caption>Cross-product and operational irregularities</caption>
  <thead><tr><th style="width:6%">ID</th><th style="width:40%">Issue</th><th style="width:38%">Action taken / decision needed</th><th style="width:16%">Source</th></tr></thead>
  <tbody>{''.join(row(*f) for f in prog_flags)}</tbody>
</table>
</div>

<h2>Product-level flags</h2>
<div class="tablewrap">
<table>
  <caption>Conflicts and gaps per product</caption>
  <thead><tr><th style="width:6%">ID</th><th style="width:40%">Issue</th><th style="width:38%">Action taken / decision needed</th><th style="width:16%">Source</th></tr></thead>
  <tbody>{''.join(row(*f) for f in prod_flags)}</tbody>
</table>
</div>

<h2>Every blank field, with the reason</h2>
<div class="tablewrap">
<table>
  <caption>Unconfirmed values — nothing here has been filled in</caption>
  <thead><tr><th>Product</th><th>Field</th><th>Why it is blank</th><th>Source checked</th></tr></thead>
  <tbody>
  {''.join(f'<tr><td>{e(p["short_name"])}</td><td>{e(s["label"])}</td><td class="small">{e(s["unverified"])}</td><td>{src_links(s["source"])}</td></tr>' for p in PRODUCT_LIST for s in p["specs"] if s["value"] is None)}
  </tbody>
</table>
</div>

<h2>How to close an item</h2>
<ol class="tight small">
  <li>Open the source link in the row. If an official page now states the value, update <code>data/products.json</code> with the value and the source id, then rebuild.</li>
  <li>If two official sources still conflict, do not pick one. Record both and keep the row blank — that is the correct output, not a failure.</li>
  <li>For F6 and F7, the fix happens in Associates Central, not in this repository.</li>
  <li>Move the resolved item into the resolved table below, so the audit trail survives.</li>
</ol>

<div class="tablewrap">
<table>
  <caption>Resolved items</caption>
  <thead><tr><th style="width:8%">ID</th><th style="width:30%">Item</th><th style="width:46%">Resolution</th><th style="width:16%">Source</th></tr></thead>
  <tbody>{resolved_rows}</tbody>
</table>
</div>
<p class="tiny muted">Rows whose verdict is <em>Official sources still disagree</em> are re-listed as open flags by the
<a href="../reverification.html">2026-11-14 re-verification pass</a>; a resolution here never removes evidence, it only
records what a re-test established.</p>
"""
    return layout("flagged.html", "Flagged for review", body, active="flagged.html",
                  description="Unverified values, source conflicts and operational irregularities flagged for human review, each with its official source link.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Flagged for review", page_url("flagged.html")),
    ])]
              )


def page_platform():
    pipeline = "".join(
        f"""<tr>
          <td class="num">{s['stage']}</td>
          <td><strong>{e(s['name'])}</strong><div class="tiny muted">Automation: {e(s['automation'])}</div></td>
          <td class="small">{e(s['inputs'])}</td>
          <td class="small">{e(s['outputs'])}</td>
          <td class="num"><a href="compliance.html">{e(s['guardrail'])}</a><div class="tiny">{governed_by([c.strip() for c in s['guardrail'].split(',')])}</div></td>
        </tr>"""
        for s in PLATFORM["pipeline"]
    )
    guard = "".join(
        f"""<tr>
          <td class="num"><strong>{e(g['id'])}</strong></td>
          <td>{e(g['rule'])}</td>
          <td class="small">{e(g['clause'])}</td>
          <td>{src_links(g['source'])}</td>
          <td class="small">{e(g['enforcement'])}</td>
        </tr>"""
        for g in PLATFORM["guardrails"]
    )
    principles = "".join(
        f'<div class="card"><h3 style="margin-top:0">{e(p["id"]).replace("P","Principle ")}</h3><p class="small" style="margin:0"><strong>{e(p["principle"])}</strong> {e(p["detail"])}</p></div>'
        for p in PLATFORM["design_principles"]
    )
    def _mode_task(task):
        if "Rate-table" in task:
            return e(task) + " " + src_link("S3")
        if "Compliance" in task:
            return e(task) + " " + src_link("S2")
        # Operating policies map to the guardrail that governs them (see the guardrail table).
        code = AUTOMATION_GOVERNANCE.get(task)
        if code:
            return e(task) + f' <a href="compliance.html">policy {e(code)}</a> ' + governed_by([code])
        return e(task) + ' <a href="compliance.html">policy</a>'

    modes = "".join(
        f'<tr><td>{_mode_task(m["task"])}</td><td>{e(m["mode"])}</td><td class="num">{e(m["frequency"])}</td></tr>'
        for m in PLATFORM["automation_vs_human"]
    )
    # Official source that governs each KPI's definition. Where none exists the row says so
    # and links to flag F26 — a design target is not a fact, and no official source states it.
    kpi_sources = {
        "Clicks per page": ["S6"],
        "Earnings per click (EPC)": ["S3"],
        "Disclosure coverage": ["S1", "S5"],
        "Policy incidents": ["S1"],
    }

    def _kpi_source(name):
        ids = kpi_sources.get(name)
        if ids:
            return src_links(ids)
        return f'Internal operating target, not an Amazon fact. <a href="{REPO_BLOB}data/platform.json">Recorded target</a> · <a href="flagged.html#f26">F26</a>'

    kpis = "".join(
        f'<tr><td><strong>{e(k["kpi"])}</strong></td><td class="small">{e(k["definition"])}</td>'
        f'<td class="small">{e(k["target"])} <a href="flagged.html">open items</a>'
        f'<div class="tiny">{_kpi_source(k["kpi"])}</div></td></tr>'
        for k in PLATFORM["kpis"]
    )
    launch = "".join(
        f'<tr><td class="num">{s["step"]}</td><td class="small">{e(s["action"])}</td><td class="small muted">{e(s["why"])} {src_links(["S2", "S4"])}</td></tr>'
        for s in PLATFORM["launch_sequence"]
    )
    oos = "".join(f'<li>{e(x)}</li>' for x in PLATFORM["explicitly_out_of_scope"])
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Platform blueprint</p>
<h1>An automated affiliate engine that survives an audit</h1>
<p class="lede">The brief asks for automation, scale, data-driven optimisation and Amazon policy compliance. Those four pull in different directions, and the design below resolves the tension in one place: <strong>automate everything except the claims</strong>. Machines move data, check links, compute and report. Claims require primary-source evidence and the publication checks before shipping. No named human sign-off is established for this AI-assisted publication; this is a gated blueprint, not a running research/optimisation service.</p>

<h2>Design principles</h2>
<div class="grid grid-2">{principles}</div>

<h2>The pipeline</h2>
<div class="tablewrap">
<table>
  <caption>Nine stages, each with the guardrail that constrains it</caption>
  <thead><tr><th style="width:5%">#</th><th style="width:20%">Stage</th><th style="width:26%">Inputs</th><th style="width:26%">Outputs</th><th style="width:8%">Guard</th></tr></thead>
  <tbody>{pipeline}</tbody>
</table>
</div>

<h2>Guardrails</h2>
<div class="tablewrap">
<table>
  <caption>Hard rules with source clause and enforcement mechanism</caption>
  <thead><tr><th style="width:6%">ID</th><th style="width:26%">Rule</th><th style="width:16%">Clause</th><th style="width:8%">Source</th><th style="width:44%">Enforcement</th></tr></thead>
  <tbody>{guard}</tbody>
</table>
</div>

<h2>Automated versus human</h2>
<div class="tablewrap">
<table>
  <caption>Who owns which decision</caption>
  <thead><tr><th>Task</th><th>Mode</th><th>Frequency</th></tr></thead>
  <tbody>{modes}</tbody>
</table>
</div>

<h2>Revenue model</h2>
<p class="small">{e(PLATFORM['revenue_model_note'])}</p>
{calc_widget()}
<div class="callout info">
  <strong>Reading the numbers honestly</strong>
  <p class="small">At the Kitchen rate of 4.50% {src_links(['S3'])}, a $199.99 list-priced unit yields about $9.00 of commission before Amazon's deductions for returns, shipping, tax and bad debt. That is the ceiling, not the expectation. The variables that actually decide the outcome — conversion rate, return rate, mix of products in the cart — are unknowable from any official source and must be measured. Any projection that shows more precision than that is selling something.</p>
</div>

<h2>KPIs</h2>
<div class="tablewrap">
<table>
  <caption>What gets measured, and the target</caption>
  <thead><tr><th>KPI</th><th>Definition</th><th>Target</th></tr></thead>
  <tbody>{kpis}</tbody>
</table>
</div>

<h2>Launch sequence — and the 180-day clock</h2>
<div class="tablewrap">
<table>
  <caption>The order matters, because application review is conditional on sales</caption>
  <thead><tr><th style="width:6%">#</th><th style="width:52%">Action</th><th style="width:42%">Why this order</th></tr></thead>
  <tbody>{launch}</tbody>
</table>
</div>
<p class="small">Amazon requires at least three qualifying sales within the first 180 days and states that personal orders do not qualify {src_links(['S4'])}. Applying before the site has traffic and content is the most common way this fails, so the sequence above puts publication first.</p>

<h2>Explicitly out of scope</h2>
<div class="card">
  <p class="small" style="margin-top:0">These are the features a generic "AI affiliate platform" pitch would include. They are excluded here because each one breaches a specific rule:</p>
  <ul class="tight small" style="margin-bottom:0">{oos}</ul>
</div>

<h2>What this build deliberately does not do</h2>
<div class="grid grid-2">
  <div class="card">
    <h3 style="margin-top:0">No scraped Amazon dataset</h3>
    <p class="small" style="margin-bottom:0">A product-research engine built on Amazon page scraping would violate the IP License's restriction on aggregation and extraction {src_links(['S2'])}. The research layer here works on manufacturer documentation and the operator's own performance data.</p>
  </div>
  <div class="card">
    <h3 style="margin-top:0">No autopilot publishing</h3>
    <p class="small" style="margin-bottom:0">Content is drafted automatically and published by a human. The failure mode of full autopublish is a confident, well-formatted, policy-breaking claim — which is precisely what this project exists to prevent.</p>
  </div>
</div>
"""
    return layout("platform.html", "Platform blueprint", body, active="platform.html",
                  description="Automation blueprint for a compliant Amazon affiliate platform: pipeline, guardrails, KPIs and launch sequence.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Platform blueprint", page_url("platform.html")),
    ])]
              )


def _req_counts_html():
    """Live counts from the requirements register, so the briefing cannot disagree with it."""
    counts = {}
    for r in REQUIREMENTS["requirements"]:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    parts = " · ".join(
        f"<strong>{counts.get(k, 0)}</strong> {REQ_STATUS[k][1].lower()}"
        for k in ("delivered", "partial", "blocked", "not_delivered")
    )
    return parts + "."


def page_exec():
    counts = {state:sum(r.get("current_state") == state for r in SUGGESTIONS["suggestions"]) for state in ("complete","partial","gated","superseded","open")}
    rows = [
        ("Publication", 'Buyer-first home, category, comparison and model guides; both thermometer links are acknowledged as unconfirmed link notes. One native Workspace group and footer index hold owner/evidence work.', ['S10','S12','S14'], 'publication/README.md'),
        ("Authorship & assets", 'AI-assisted document research is disclosed. No invented human editor, hands-on test or copied/generated branded-product photograph. The conceptual kitchen scene is visibly labelled.', ['S8','S2'], 'publication/README.md'),
        ("Sources & corrections", 'Scoped 19 November reads, not a blanket refresh. F96 flags contradictory Emeril cord instructions; F97 records corrected care, capacity and dimension guidance. Source conflicts stay public.', ['S13','S15','S18'], 'reports/verification-2026-11-19-1f9e7d52.md'),
        ("Five submitted links", 'Original URL strings, dated redirect/title observations and intended listings remain separate. Every intended ASIN/listing confirmation and enrolled test is still unconfirmed.', ['S41','S42'], 'data/product-intent.json'),
        ("Selected tracking ID", 'shopnow047c-20 is recorded but unvalidated and unapplied. The operational tag is blank. Confirm one intended listing and a permitted enrolled Special Link workflow per product before scaling.', ['S2','S42'], 'data/config.json'),
        ("Measurement", 'Actual named-event browser client and aggregate Python collector interoperate in synthetic HTTP tests. Production collection is disabled; no runtime/privacy approval or eligible campaign dataset exists.', ['S2','S38'], 'analytics/README.md'),
        ("Search & reader loop", 'One canonical reader sitemap, feed and metadata are generated automatically. RSS works. Search Console ownership/submission/query data and email capture are not invented.', ['S44','S45'], 'data/publication.json'),
        ("Cadence", 'Weekly source review and at most one useful new/substantial guide update per fortnight, only after evidence/build checks. Refresh an existing answer rather than duplicate it. This is a plan, not a running scheduler.', ['S43'], 'data/publication.json'),
    ]
    table = ''.join(f'<tr><th scope="row">{e(title)}</th><td>{e(note)}</td><td>{src_links(ids)} <a href="{e(path)}">Repository evidence</a></td></tr>' for title,note,ids,path in rows)
    links = ''.join(f'<a class="card tight" href="{e(href)}"><span class="kicker">Workspace</span><strong>{e(label)}</strong></a>' for href,label in (("suggestions.html","Current decisions & alternatives"),("questions.html","Known facts, gaps & discovery"),("product-intent.html","Five links & empty campaign ledger"),("measurement.html","Measurement & deployment contract"),("design-prompt.html","Current design/editorial brief"),("requirements.html","Brief coverage & explicit gaps")))
    body = f"""<p class="crumbs"><a href="index.html">Home</a> / Executive summary</p><p class="section-eyebrow">Current integration · {e(PUBLICATION['updated'])}</p><h1>A publication, with its limits in view.</h1><p class="lede">The reader site is built. Account-only validation, production analytics and measured campaign results are not. This is the current brief—not a revenue forecast or a legal-compliance certificate.</p>
<div class="grid grid-3"><div class="stat"><div class="n">{len(ARTICLES['articles'])}</div><div class="l">Question-led guides</div><div class="h">{len(CLUSTERS['clusters'])} intent clusters; editorial hypotheses, not measured demand</div></div><div class="stat"><div class="n">{len(PRODUCT_INTENT['rows'])}</div><div class="l">Exact submitted links retained</div><div class="h">Intended listings and enrolled tests remain unconfirmed</div></div><div class="stat"><div class="n">{len(CAMPAIGN_LEDGER['rows'])}</div><div class="l">Authorised campaign rows</div><div class="h">No conversions, revenue forecast or optimisation score</div></div></div>
<h2>What is implemented—and what is not</h2><div class="tablewrap"><table><caption>Current evidence boundaries</caption><thead><tr><th>Area</th><th>Current state</th><th>Primary / implementation evidence</th></tr></thead><tbody>{table}</tbody></table></div>
<div class="callout warn"><strong>Safety discrepancy, not a choice of instructions.</strong>The Emeril manual prohibits extension cords in its safeguards but conditionally permits them in a later section. Do not treat the latter as permission; seek current manufacturer clarification for the exact unit. <a href="flagged.html#f96">F96 and the source</a>.</div>
<h2>A short route through the workspace</h2><div class="grid grid-3">{links}</div><p class="small">The Suggestions register contains {len(SUGGESTIONS['suggestions'])} rows: {counts['complete']} complete repository features/plans, {counts['superseded']} superseded, {counts['partial']} partial and {counts['gated']} gated. These current states form one partition; they do not add historical action logs to a current open count. Owner choices remain separate from agent execution records.</p>
<h2>Evidence before optimisation</h2><ol class="tight"><li>Keep the original links and complete intended-listing/enrolled validation only with authorised account evidence.</li><li>Use the repaired collector only after a real controlled same-origin runtime, infrastructure-log minimisation and privacy review exist.</li><li>Import only dated authorised first-party reports with source/channel/date-range/eligible sessions/clicks/orders/provenance. Leave missing values blank.</li><li>Use actual comparable data before changing placement or calling a topic popular. No present design change is claimed to improve conversion.</li></ol>
<p class="section-note"><a href="reports/verification-2026-11-19-1f9e7d52.md">Scoped verification, test results and deployment record</a> · <a href="EXECUTIVE-SUMMARY.md">Current written summary with historical appendices</a> · <a href="previous-passes.html">Historical builds</a>.</p>"""
    return layout('executive-summary.html','Executive summary & workspace index',body,active='executive-summary.html',description='Current publication delivery, source corrections and honest remaining account/deployment boundaries. No fabricated traffic, conversions or approvals.',jsonld_blocks=[breadcrumbs_jsonld([('Home',SITE_BASE),('Executive summary',page_url('executive-summary.html'))])])


REV_VERDICT = {
    "confirmed": ("pill-ok", "Confirmed"),
    "partially-confirmed": ("pill-info", "Partly confirmed"),
    "moved": ("pill-warn", "Moved since last pass"),
    "conflict-live": ("pill-bad", "Official sources still disagree"),
    "conflict-resolved": ("pill-ok", "Earlier conflict resolved"),
    "new-evidence": ("pill-info", "New evidence"),
    "not-rechecked": ("pill-warn", "Not re-checked in this pass"),
    # Added by pass 6 (sess-54c66535): the row was re-opened and the official source read,
    # but the source does not state the value. Distinct from "not re-checked", which means
    # nobody looked. Nothing is filled in on this verdict.
    "source-silent": ("pill-warn", "Re-read — source does not state it"),
}


def page_reverification():
    rev = REVERIFICATION
    groups = []
    seen = []
    for t in rev["tests"]:
        if t["group"] not in seen:
            seen.append(t["group"])
    tally = {}
    for t in rev["tests"]:
        tally[t["verdict"]] = tally.get(t["verdict"], 0) + 1

    def row(t):
        cls, label = REV_VERDICT[t["verdict"]]
        return (
            f'<tr><td><strong>{e(t["claim"])}</strong></td>'
            f'<td class="small">{e(t["published_value"])}</td>'
            f'<td class="small">{e(t["observed_2026_11_14"])}</td>'
            f'<td><span class="pill {cls}">{e(label)}</span></td>'
            f'<td class="small"><a href="{e(t["source_url"])}" target="_blank" rel="noopener">'
            f'{e(t["source_label"])}</a></td></tr>'
        )

    for g in seen:
        rows = "".join(row(t) for t in rev["tests"] if t["group"] == g)
        groups.append(f"""
<h2>{e(g)}</h2>
<div class="tablewrap">
<table>
  <thead><tr><th style="width:19%">Claim</th><th style="width:19%">Published value</th>
  <th style="width:38%">What the official source said on {e(rev["pass_date"])}</th>
  <th style="width:13%">Verdict</th><th style="width:11%">Source</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
</div>
""")

    changes = "".join(f"<li>{e(c)}</li>" for c in rev["changes_made"])

    # ---- pass-6 addendum (sess-54c66535): the nine rows this page left unre-checked ----
    p6_html = ""
    if PASS6:
        p6 = PASS6
        def p6row(t):
            cls, label = REV_VERDICT[t["verdict"]]
            return (
                f'<tr><td><strong>{e(t["claim"])}</strong></td>'
                f'<td class="small">{e(t["published_value"])}</td>'
                f'<td class="small">{e(t["observed"])}</td>'
                f'<td><span class="pill {cls}">{e(label)}</span></td>'
                f'<td class="small"><a href="{e(t["source_url"])}" target="_blank" rel="noopener">'
                f'{e(t["source_label"])}</a></td></tr>'
            )

        p6rows = "".join(p6row(t) for t in p6["rows"])
        p6conf = sum(1 for t in p6["rows"] if t["verdict"] == "confirmed")
        p6silent = sum(1 for t in p6["rows"] if t["verdict"] == "source-silent")
        p6ev = "".join(
            f'<div class="callout info" style="margin:.6rem 0">'
            f'<strong>{e(x["title"])}</strong>'
            f'<p class="small">{e(x["detail"])}</p>'
            f'<p class="tiny muted">Flag {e(x["flag"])} · '
            f'<a href="{e(x["source_url"])}" target="_blank" rel="noopener">{e(x["source_label"])}</a>'
            f'</p></div>'
            for x in p6["new_evidence"]
        )
        p6_html = f"""
<h2>Pass 6 — the nine rows earlier passes could not re-check ({e(p6['pass_date'])}, sess-54c66535)</h2>
<p class="small">This page's ledger re-read 61 values on 2026-11-14 and left 9 marked
<em>not re-checked</em>. Pass 6 re-opened all nine against the official page or manual the site cites
for each. <strong>{p6conf} are now confirmed verbatim</strong> and <strong>{p6silent} are not stated
by their official source at all</strong>. Neither group was filled by inference: a value the
manufacturer does not publish stays blank.</p>
<div class="tablewrap">
<table>
  <caption>All nine previously unre-checked rows, re-read on {e(p6['pass_date'])}</caption>
  <thead><tr><th style="width:17%">Claim</th><th style="width:17%">Published value</th>
  <th style="width:42%">What the official source says</th><th style="width:12%">Verdict</th>
  <th style="width:12%">Source</th></tr></thead>
  <tbody>{p6rows}</tbody>
</table>
</div>

<h3>What pass 6 added beyond the nine rows</h3>
{p6ev}
<p class="tiny muted">{e(p6['scope_note'])}</p>
<p class="tiny muted">Raw observations for this pass are in
<code>session-54c66535/EVIDENCE-2026-11-14.md</code>.</p>
"""
    # ---- pass-7 addendum (arena-052f2c9f): independent re-verification round 7 ----
    p7_html = ""
    if PASS7:
        p7 = PASS7
        def p7row(t):
            cls, label = REV_VERDICT[t["verdict"]]
            return (
                f'<tr><td><strong>{e(t["claim"])}</strong></td>'
                f'<td class="small">{e(t["published_value"])}</td>'
                f'<td class="small">{e(t["observed"])}</td>'
                f'<td><span class="pill {cls}">{e(label)}</span></td>'
                f'<td class="small"><a href="{e(t["source_url"])}" target="_blank" rel="noopener">'
                f'{e(t["source_label"])}</a></td></tr>'
            )

        p7rows = "".join(p7row(t) for t in p7["rows"])
        p7ev = "".join(
            f'<div class="callout info" style="margin:.6rem 0">'
            f'<strong>{e(x["title"])}</strong>'
            f'<p class="small">{e(x["detail"])}</p>'
            f'<p class="tiny muted">Flag {e(x["flag"])} · '
            f'<a href="{e(x["source_url"])}" target="_blank" rel="noopener">{e(x["source_label"])}</a>'
            f'</p></div>'
            for x in p7["new_evidence"]
        )
        p7_html = f"""
<h2>Pass 7 — independent re-verification round 7 ({e(p7['pass_date'])}, arena-052f2c9f)</h2>
<p class="small">A session that wrote none of the stored values re-read the load-bearing facts
against the live official sources on {e(p7['pass_date'])}, hours after pass 6. The three supplied
short links resolved to the same three ASINs for the <strong>seventh consecutive observation
round</strong>, the nonsense-token control was re-run and again refused with 403, and every policy
and brand fact checked below matched what the site publishes. No stored value changed and no new
value was filled in.</p>
<div class="tablewrap">
<table>
  <caption>Round-7 re-reads, {e(p7['pass_date'])} (UTC 19:05–19:15)</caption>
  <thead><tr><th style="width:17%">Claim</th><th style="width:17%">Published value</th>
  <th style="width:42%">What the official source says</th><th style="width:12%">Verdict</th>
  <th style="width:12%">Source</th></tr></thead>
  <tbody>{p7rows}</tbody>
</table>
</div>

<h3>What pass 7 added beyond the re-reads</h3>
{p7ev}
<p class="tiny muted">{e(p7['scope_note'])}</p>
<p class="tiny muted">Raw observations for this pass are in
<code>session-052f2c9f/EVIDENCE-2026-11-14.md</code>.</p>
"""
    # ---- pass-9 addendum (arena/88bb2db6): final-integration re-read, 2026-11-15 ----
    p9_html = ""
    if PASS9:
        p9 = PASS9

        def p9row(t):
            cls, label = REV_VERDICT[t["verdict"]]
            return (
                f'<tr><td><strong>{e(t["claim"])}</strong></td>'
                f'<td class="small">{e(t["published_value"])}</td>'
                f'<td class="small">{e(t["observed"])}</td>'
                f'<td><span class="pill {cls}">{e(label)}</span></td>'
                f'<td class="small"><a href="{e(t["source_url"])}" target="_blank" rel="noopener">'
                f'{e(t["source_label"])}</a></td></tr>'
            )

        p9rows = "".join(p9row(t) for t in p9["rows"])
        p9ev = "".join(
            f'<div class="callout info" style="margin:.6rem 0">'
            f'<strong>{e(x["title"])}</strong>'
            f'<p class="small">{e(x["detail"])}</p>'
            f'<p class="tiny muted">Flag {e(x["flag"])} · '
            f'<a href="{e(x["source_url"])}" target="_blank" rel="noopener">{e(x["source_label"])}</a>'
            f'</p></div>'
            for x in p9["new_evidence"]
        )
        p9_conf = sum(1 for t in p9["rows"] if t["verdict"] == "confirmed")
        p9_confl = sum(1 for t in p9["rows"] if t["verdict"] in ("conflict-live", "conflict-resolved"))
        p9_html = f"""
<h2>Pass 9 — final-integration re-read ({e(p9['pass_date'])}, arena/88bb2db6)</h2>
<p class="small">{e(p9['lede'])}</p>
<p class="tiny muted"><strong>{p9_conf}</strong> of the {len(p9['rows'])} rows below were confirmed
against the live official source on {e(p9['pass_date'])};
<strong>{p9_confl}</strong> record a disagreement between official documents that is still open.
One new conflict was found and filed rather than resolved by guesswork.</p>
<div class="tablewrap">
<table>
  <caption>Pass-9 re-reads, {e(p9['pass_date'])}</caption>
  <thead><tr><th style="width:17%">Claim</th><th style="width:17%">Published value</th>
  <th style="width:42%">What the official source says</th><th style="width:12%">Verdict</th>
  <th style="width:12%">Source</th></tr></thead>
  <tbody>{p9rows}</tbody>
</table>
</div>

<h3>What pass 9 added beyond the re-reads</h3>
{p9ev}
<p class="tiny muted">{e(p9['scope_note'])}</p>
<p class="tiny muted">Raw observations for this pass are in
<code>session-88bb2db6/EVIDENCE-2026-11-15.md</code>.</p>
"""

    p10_html = ""
    if PASS10:
        p10 = PASS10
        def p10_source_links(t):
            links = [{"label": t["source_label"], "url": t["source_url"]}]
            links.extend(t.get("additional_sources", []))
            return "<br>".join(
                f'<a href="{e(source["url"])}" target="_blank" rel="noopener">{e(source["label"])}</a>'
                for source in links
            )

        p10rows = "".join(
            f'<tr><td><strong>{e(t["claim"])}</strong></td>'
            f'<td class="small">{e(t["previous"])}</td>'
            f'<td class="small">{e(t["observed"])}</td>'
            f'<td class="small">{e(t["verdict"])}</td>'
            f'<td class="small">{p10_source_links(t)}</td></tr>'
            for t in p10["rows"]
        )
        p10flags = "".join(f"<li>{e(item)}</li>" for item in p10["irregularities"])
        p10_html = f"""
<h2>{e(p10['title'])}</h2>
<p class="small">{e(p10['lede'])}</p>
<div class="callout info"><strong>Scope and caution</strong><p class="small">{e(p10['scope_note'])}</p></div>
<div class="tablewrap">
<table>
  <caption>Targeted official-source re-reads, {e(p10['pass_date'])}</caption>
  <thead><tr><th style="width:18%">Claim</th><th style="width:17%">Previously recorded</th>
  <th style="width:35%">Current observation</th><th style="width:17%">Verdict</th>
  <th style="width:13%">Official source(s)</th></tr></thead>
  <tbody>{p10rows}</tbody>
</table>
</div>
<h3>Open irregularities — not resolved by this pass</h3>
<ul class="tight small">{p10flags}</ul>
<p class="tiny muted">Full evidence notes: <a href="session-9f0e6668/VERIFICATION-2026-11-16.md">round-10 verification record</a>.</p>
"""

    # ---- pass-10 addendum (arena/9fccce0c-zone1): independent re-read, 2026-11-16 ----
    p10u2_html = ""
    if PASS10_U2:
        p10u2 = PASS10_U2

        def p10u2row(t):
            cls, label = REV_VERDICT[t["verdict"]]
            return (
                f'<tr><td><strong>{e(t["claim"])}</strong></td>'
                f'<td class="small">{e(t["published_value"])}</td>'
                f'<td class="small">{e(t["observed"])}</td>'
                f'<td><span class="pill {cls}">{e(label)}</span></td>'
                f'<td class="small"><a href="{e(t["source_url"])}" target="_blank" rel="noopener">'
                f'{e(t["source_label"])}</a></td></tr>'
            )

        p10u2rows = "".join(p10u2row(t) for t in p10u2["rows"])
        p10u2ev = "".join(
            f'<div class="callout info" style="margin:.6rem 0">'
            f'<strong>{e(x["title"])}</strong>'
            f'<p class="small">{e(x["detail"])}</p>'
            f'<p class="tiny muted">Flag {e(x["flag"])} \u00b7 '
            f'<a href="{e(x["source_url"])}" target="_blank" rel="noopener">{e(x["source_label"])}</a>'
            f'</p></div>'
            for x in p10u2["new_evidence"]
        )
        p10u2_conf = sum(1 for t in p10u2["rows"] if t["verdict"] == "confirmed")
        p10u2_moved = sum(1 for t in p10u2["rows"] if t["verdict"] == "moved")
        p10u2_new = sum(1 for t in p10u2["rows"] if t["verdict"] == "new-evidence")
        p10u2_html = f"""
<h2>Pass 10 \u2014 independent re-read ({e(p10u2['pass_date'])}, arena/9fccce0c-zone1)</h2>
<p class="small">{e(p10u2['lede'])}</p>
<p class="tiny muted"><strong>{p10u2_conf}</strong> of the {len(p10u2['rows'])} rows below were confirmed
against the live official source on {e(p10u2['pass_date'])};
<strong>{p10u2_moved}</strong> record a value that had moved since the last read,
<strong>{p10u2_new}</strong> record a clause that had never been read into this register before,
and <strong>1</strong> records an official disagreement that is still open and still unasserted.
No value was filled in that a source did not state.</p>
<div class="tablewrap">
<table>
  <caption>Pass-10 re-reads, {e(p10u2['pass_date'])}</caption>
  <thead><tr><th style="width:17%">Claim</th><th style="width:17%">Published value</th>
  <th style="width:42%">What the official source says</th><th style="width:12%">Verdict</th>
  <th style="width:12%">Source</th></tr></thead>
  <tbody>{p10u2rows}</tbody>
</table>
</div>

<h3>What pass 10 added beyond the re-reads</h3>
{p10u2ev}
<p class="tiny muted">{e(p10u2['scope_note'])}</p>
<p class="tiny muted">The full evidence for this pass \u2014 every URL requested, the exact string read
back, and the verdict \u2014 is in <code>reports/verification-2026-11-16-9fccce0c.md</code>.</p>
"""

    # ---- spot ledger (arena/8874422b-zone1): the second reader's cross-check, 2026-11-16 ----
    p12_html = ""
    if PASS12:
        p12 = PASS12

        def p12row(t):
            cls, label = REV_VERDICT[t["verdict"]]
            return (
                f'<tr><td><strong>{e(t["claim"])}</strong></td>'
                f'<td class="small">{e(t["published_value"])}</td>'
                f'<td class="small">{e(t["observed"])}</td>'
                f'<td><span class="pill {cls}">{e(label)}</span></td>'
                f'<td class="small"><a href="{e(t["source_url"])}" target="_blank" rel="noopener">'
                f'{e(t["source_label"])}</a></td></tr>'
            )

        p12rows = "".join(p12row(t) for t in p12["rows"])
        p12_conf = sum(1 for t in p12["rows"] if t["verdict"] == "confirmed")
        p12_moved = sum(1 for t in p12["rows"] if t["verdict"] == "moved")
        p12_html = f"""
<h2>Second-reader spot re-read ({e(p12['pass_date'])}, arena/8874422b-zone1)</h2>
<p class="small">{e(p12['lede'])}</p>
<div class="callout info"><strong>Scope</strong><p class="small">{e(p12['scope_note'])}</p></div>
<div class="tablewrap">
<table>
  <caption>Spot re-reads by a second reader, {e(p12['pass_date'])}</caption>
  <thead><tr><th style="width:19%">Claim</th><th style="width:17%">Published value</th>
  <th style="width:38%">What the official source shows</th><th style="width:12%">Verdict</th>
  <th style="width:14%">Source</th></tr></thead>
  <tbody>{p12rows}</tbody>
</table>
</div>
<p class="tiny muted"><strong>{p12_conf}</strong> of {len(p12['rows'])} rows confirmed against the
live official source on {e(p12['pass_date'])}; <strong>{p12_moved}</strong> had moved (and were
left as published or refreshed per the flag rules). The full URL-by-URL evidence, including the
exact strings read back, is in <code>reports/verification-2026-11-16-8874422b.md</code>.</p>
"""

    lr = rev.get("link_resolution") or {}
    lr_html = ""
    if lr:
        lr_html = (
            '<div class="callout ok"><strong>' + e(lr.get("question", "")) + "</strong>"
            + '<p class="small">' + e(lr.get("answer", "")) + "</p>"
            + '<p class="tiny muted">' + e(lr.get("evidence_note", "")) + "</p></div>"
        )
    stats = [
        ("ok", tally.get("confirmed", 0), "Confirmed against the live official source"),
        ("brand", tally.get("partially-confirmed", 0), "Partly confirmed (document read in part)"),
        ("warn", tally.get("not-rechecked", 0), "Not re-checked in this pass — earlier record stands"),
        ("bad", tally.get("conflict-live", 0), "Official sources still disagree — nothing asserted"),
    ]
    stat_html = "".join(
        f'<div class="stat {cls}"><div class="n">{n}</div><div class="l">{e(lbl)}</div></div>'
        for cls, n, lbl in stats
    )
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Re-verification {e(rev["pass_date"])}</p>
<h1>{e(rev["title"])}</h1>
<p class="lede">{e(rev["lede"])}</p>

<div class="grid grid-4" style="margin:1rem 0 1.25rem">{stat_html}</div>

<div class="callout info">
  <strong>Method</strong>
  <p class="small">{e(rev["method"])}</p>
</div>
<p class="tiny muted">{e(rev["scope_note"])}</p>

{"".join(groups)}

{p6_html}

{p7_html}
{p9_html}
{p10_html}
{p10u2_html}
{p12_html}

<h2>What this pass changed on the site</h2>
<ul class="tight small">{changes}</ul>

{lr_html}

<p class="tiny muted">Full raw observations, including the two control requests, are in
<code>session-81495d2d/EVIDENCE-2026-11-14.md</code> and in the
<a href="../COORDINATION.md">coordination log</a>.</p>
"""
    return layout("reverification.html", f"Re-verification {rev['pass_date']}", body,
                  active="reverification.html",
                  description="Line-by-line re-read of every value this site publishes, each against the official source it cites, with the verdict and the source link.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Re-verification", page_url("reverification.html")),
    ])]
              )


# --------------------------------------------------------------------------- #
# figure layer (pass 10, arena/695f03b7-zone1)
# Four data-driven SVG diagrams generated from data/products.json at build time,
# so no number in a figure can drift from the dataset. Sources travel with each
# figure; nothing is inferred. They are diagrams, not photographs, because
# product-photography rights are undecided (Q-22 / SG-23 / flag F46).
# --------------------------------------------------------------------------- #
FIGURES_DIR = ROOT / "assets" / "figures"
FIG_W, FIG_H = 900, 520


def _svg_frame(title, note, src_lines):
    src_html = "".join(f'<text x="22" y="{y}" class="src">{e(s)}</text>' for y, s in src_lines)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {FIG_W} {FIG_H}" '
        f'role="img" aria-labelledby="t"><title id="t">{e(title)}</title>'
        f'<style>.t{{font:700 17px/1.25 system-ui,sans-serif;fill:#111827;}}'
        f'.s{{font:600 12.5px/1.4 system-ui,sans-serif;fill:#374151;}}'
        f'.m{{font:400 12px/1.45 system-ui,sans-serif;fill:#4b5563;}}'
        f'.b{{font:700 13px/1.3 system-ui,sans-serif;fill:#ffffff;}}'
        f'.x{{font:600 11.5px/1.3 system-ui,sans-serif;fill:#6b7280;}}'
        f'.l{{font:600 12px/1.3 system-ui,sans-serif;fill:#111827;}}'
        f'</style>'
        f'<rect width="{FIG_W}" height="{FIG_H}" fill="#ffffff"/>'
        f'<text x="22" y="34" class="t">{e(title)}</text>'
        f'<text x="22" y="52" class="m">{e(note)}</text>{src_html}'
    )


def _svg_close():
    return "</svg>"


def fig_footprint():
    cfg = PRODUCTS["figures"]
    scale = cfg["scale_px_per_inch"]
    products = cfg["footprint"]
    y0, band = 150, 118
    axis_y = y0 + band * len(products) + 26
    ticks = "".join(
        f'<line x1="{22 + t * scale}" y1="{axis_y}" x2="{22 + t * scale}" y2="{axis_y + 4}" stroke="#9ca3af" stroke-width="1"/>'
        f'<text x="{22 + t * scale - 7}" y="{axis_y + 18}" class="x" text-anchor="middle">{t}</text>'
        for t in range(0, 57, 10)
    )
    axis = (
        f'<line x1="22" y1="{axis_y}" x2="{22 + 56 * scale}" y2="{axis_y}" stroke="#9ca3af" stroke-width="1.5"/>'
        f'<text x="22" y="{axis_y + 36}" class="x">Inches — true scale, {scale} px per inch</text>'
        + ticks
    )
    panels = ""
    for i, p in enumerate(products):
        y = y0 + i * band
        wpx = p["w"] * scale
        panels += (
            f'<rect x="22" y="{y}" width="{wpx}" height="{p["d"] * scale}" fill="#2563eb" rx="4"/>'
            f'<text x="{22 + wpx / 2}" y="{y + p["d"] * scale / 2 + 5}" class="b" text-anchor="middle">{e(p["label"])}</text>'
            f'<text x="22" y="{y + p["d"] * scale + 18}" class="m">{e(p["w"])}" W × {e(p["d"])}" D × {e(p["h"])}" H</text>'
            f'<text x="22" y="{y - 8}" class="l">{e(p["label"])}</text>'
        )
    src_lines = [(axis_y + 48, "Sources: " + ", ".join(f'{e(p["label"])} — {e(p["source"])}' for p in products))]
    return _svg_frame("Footprint at true scale — width × depth × height",
                      "Rectangles are drawn at true scale (16 px per inch) from the dimensions the manufacturers publish.",
                      src_lines) + panels + axis + _svg_close()


def fig_temperature():
    cfg = PRODUCTS["figures"]
    products = cfg["temperature"]
    lo = min(p["min"] for p in products)
    hi = max(p["max"] for p in products)
    x0, x1 = 90, 850
    span = (hi + 60) - (lo - 20)

    def xof(v):
        return x0 + (v - (lo - 20)) * (x1 - x0) / span

    axis_y = 330
    bars = ""
    y = 150
    colors = ["#2563eb", "#16a34a", "#b45309"]
    for i, p in enumerate(products):
        bars += (
            f'<rect x="{xof(p["min"])}" y="{y}" width="{xof(p["max"]) - xof(p["min"])}" height="34" '
            f'fill="{colors[i]}" opacity=".9" rx="3"/>'
            f'<text x="{xof(p["min"]) - 10}" y="{y + 22}" class="x" text-anchor="end">{p["min"]}</text>'
            f'<text x="{xof(p["max"]) + 10}" y="{y + 22}" class="b">{p["max"]}</text>'
            f'<text x="{x0}" y="{y - 12}" class="l">{e(p["label"])}</text>'
            f'<text x="{x0}" y="{y + 56}" class="m">{e(p.get("note", ""))}</text>'
            f'<text x="{x0}" y="{y + 74}" class="src">Source {e(p["source"])}' + (f' · conflict: {e(p["conflict_source"])}' if p.get("conflict_source") else "") + "</text>"
        )
        y += 98
    ticks = "".join(
        f'<text x="{xof(v)}" y="{axis_y + 18}" class="x" text-anchor="middle">{v}</text>'
        for v in range(100, 551, 100)
    )
    axis = f'<line x1="{x0}" y1="{axis_y}" x2="{x1}" y2="{axis_y}" stroke="#9ca3af" stroke-width="1.5"/>{ticks}'
    src_lines = [(axis_y + 46, "Sources: " + ", ".join(f'{e(p["label"])} — {e(p["source"])}' for p in products))]
    return (_svg_frame("Documented temperature ranges",
                       "Each bar runs from the documented minimum to the documented maximum. The Chefman 8 Qt bar ends at 400 °F because the brand page and manual document 200–400 °F; the 450 °F the Amazon listing title advertises is a live conflict (F3) and is not asserted here.",
                       src_lines) + bars + axis + _svg_close())


def fig_presets():
    cfg = PRODUCTS["figures"]
    rows_src = cfg["presets"]
    maxc = max(p["count"] for p in rows_src if p["count"] is not None)
    x0, x1 = 90, 760

    def xof(c):
        return x0 + c * (x1 - x0) / maxc

    rows = ""
    y = 150
    for p in rows_src:
        if p["count"] is not None:
            fill = "#dc2626" if p.get("conflict") else "#2563eb"
            rows += (
                f'<rect x="{x0}" y="{y}" width="{xof(p["count"]) - x0}" height="30" '
                f'fill="{fill}" opacity=".9" rx="3"/>'
                f'<text x="{xof(p["count"]) + 8}" y="{y + 21}" class="b">{p["count"]}</text>'
            )
        else:
            rows += f'<text x="{x0 + 10}" y="{y + 21}" class="m">— not documented</text>'
        rows += (
            f'<text x="22" y="{y - 8}" class="l">{e(p["document"])}</text>'
            f'<text x="{x1 + 10}" y="{y + 22}" class="m">{e(p["note"])}</text>'
            f'<text x="22" y="{y + 44}" class="src">Source {e(p["source"])}' + (f' · conflicts with {e(p.get("conflict_source", ""))}' if p.get("conflict_source") else "") + "</text>"
        )
        y += 92
    src_lines = [(y + 10, "Reading: bar length = preset count stated by that document. Red = one official document disagrees with another for the same product; no count is asserted until the conflict is settled.")]
    return (_svg_frame("Preset-count conflict — what each official document states",
                       "The site states 24 presets for the Emeril 26 QT on the strength of the owner's manual (S15); the brand page's own specification block says 25 (S14), so the conflict stays open (F29). The Chefman 8 Qt documents four presets in both page and manual (S12, S13). For the Chefman 6 Qt dual-basket no official source publishes a preset count, so the row is blank (F36).",
                       src_lines) + rows + _svg_close())


def fig_decision_tree():
    nodes = [
        ("q1", "Cooking two different foods at once, on separate settings?", "start"),
        ("q2", "Replacing a toaster oven too — toast, bake, rotisserie?", "q1"),
        ("q3", "Cooking for 4–6 people from one basket?", "q2"),
        ("a1", "Chefman 6 Qt Dual Basket — Sync Finish, two 3-qt baskets", "q1"),
        ("a2", "Emeril 26 QT French Door — rotisserie, 75–500 °F, 24 presets", "q2"),
        ("a3", "Chefman 8 Qt TurboFry — one 8-qt basket, 200–400 °F", "q3"),
        ("a4", "Reconsider capacity before choosing a model", "q3"),
    ]
    xq, xa = 250, 660
    yq, ya = 170, 170
    step = 90
    drawn = {}
    drawn["q1"] = (xq, yq)
    drawn["q2"] = (xq, yq + step)
    drawn["q3"] = (xq, yq + 2 * step)
    drawn["a1"] = (xa, yq)
    drawn["a2"] = (xa, yq + step)
    drawn["a3"] = (xa, yq + 2 * step)
    drawn["a4"] = (xa, yq + 2 * step)
    edges = [
        ("q1", "a1", "yes"), ("q1", "q2", "no"),
        ("q2", "a2", "yes"), ("q2", "q3", "no"),
        ("q3", "a3", "yes"), ("q3", "a4", "no"),
    ]
    lines = ""
    for a, b, tag in edges:
        x1_, y1_ = drawn[a]; x2_, y2_ = drawn[b]
        lines += f'<line x1="{x1_ + 145 if a.startswith("q") else x1_}" y1="{y1_ + 26}" x2="{x2_ - 150 if b.startswith("a") else x2_}" y2="{y2_ + 26}" stroke="#9ca3af" stroke-width="2" stroke-dasharray="6,4"/>'
        mx = (x1_ + x2_) / 2
        lines += f'<text x="{mx}" y="{y2_ + 14}" class="m" text-anchor="middle">{tag}</text>'
    boxes = ""
    for nid, label, _ in nodes:
        cx, cy = drawn[nid]
        w = 320
        fill = "#2563eb" if nid.startswith("q") else ("#16a34a" if nid.startswith("a") and nid != "a4" else "#9ca3af")
        parts = label.split("\n")
        boxes += (
            f'<rect x="{cx - w / 2}" y="{cy}" width="{w}" height="56" fill="{fill}" rx="8"/>'
            f'<text x="{cx}" y="{cy + 19}" class="b" text-anchor="middle">{e(parts[0])}</text>'
        )
        if len(parts) > 1:
            boxes += f'<text x="{cx}" y="{cy + 37}" class="b" text-anchor="middle">{e(parts[1])}</text>'
    return (_svg_frame("Format decision tree — choose by job, not by brand",
                       "Generated from data/products.json. Each answer names the product whose documented capability fits; the tree is decision support, not a recommendation.",
                       [(yq + 2 * step + 90, "Sources: Chefman 6 Qt — S10 · Emeril 26 QT — S15/S14 · Chefman 8 Qt — S12/S13")]) + lines + boxes + _svg_close())


def build_figures():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in (("footprint", fig_footprint), ("temperature", fig_temperature),
                     ("presets", fig_presets), ("decision-tree", fig_decision_tree)):
        (FIGURES_DIR / f"{name}.svg").write_text(fn(), encoding="utf-8")


def page_pass10():
    """Pass-10 ledger: every registered source re-read live on 2026-11-16, one row per
    source, each row carrying its official source link and the observed verdict.

    Additive only: no published value changes here; irregularities are flagged, never
    inferred. Renders at pass10.html and is linked from the Evidence nav group.
    """
    p10 = PASS10_FULL
    if not p10:
        return ""
    tally = p10["tally"]

    def verdict_html(v):
        cls, label = REV_VERDICT[v]
        return f'<span class="pill {cls}">{e(label)}</span>'

    def row(r):
        return (
            f'<tr><td class="num">{e(r["id"])}</td>'
            f'<td class="small"><strong>{e(r["source"])}</strong><br><span class="tiny muted">{e(r["source_label"])}</span></td>'
            f'<td class="small">{e(r["claim"])}</td>'
            f'<td class="small">{e(r["published_value"])}</td>'
            f'<td class="small">{e(r["observed_2026_11_16"])}</td>'
            f'<td class="small">{verdict_html(r["verdict"])}</td>'
            f'<td class="small"><a href="{e(r["source_url"])}" target="_blank" rel="noopener">'
            f'{e(r["source"])} — official page</a></td></tr>'
        )

    rows = "".join(row(r) for r in p10["rows"])
    conf = tally["confirmed"]
    part = tally["partially-confirmed"]
    confl = tally["conflict-live"]
    nrc = tally["not-rechecked"]

    stats = [
        ("ok", conf, "Confirmed against the live official source"),
        ("brand", part, "Partly confirmed (document read in part)"),
        ("warn", nrc, "Not re-checked in this pass — earlier record stands"),
        ("bad", confl, "Official sources still disagree — nothing asserted"),
    ]
    stat_html = "".join(
        f'<div class="stat {cls}"><div class="n">{n}</div><div class="l">{e(lbl)}</div></div>'
        for cls, n, lbl in stats
    )

    irr = "".join(
        f'<div class="callout info" style="margin:.6rem 0">'
        f'<strong class="small">Flag {e(x["id"])}</strong> {e(x["summary"])}'
        f'<p class="tiny muted">Sources: {e(", ".join(x["sources"]))}</p>'
        f'</div>'
        for x in p10["irregularities"]
    )

    carried = "".join(f"<li>{e(c)}</li>" for c in p10["carried_forward"])

    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Verification pass 10</p>
<h1>Pass {e(p10['pass'])} verification ledger · {e(p10['pass_date'])}</h1>
<p class="lede">{e(p10['scope'])}</p>

<div class="callout info">
  <strong>Method</strong>
  <p class="small">{e(p10['method'])}</p>
</div>

<div class="grid grid-4" style="margin:1rem 0 1.25rem">{stat_html}</div>

<p class="small"><strong>{conf} confirmed</strong> · <strong>{part} partly confirmed</strong> ·
<strong>{confl} conflict live</strong> · <strong>{nrc} not re-checked</strong> — no published
value changed and no new product-value correction is justified. Every irregularity below is
already flagged; none is inferred.</p>

<div class="tablewrap">
<table>
  <caption>All {len(p10['rows'])} registered sources, re-read on {e(p10['pass_date'])}</caption>
  <thead><tr><th style="width:8%">Pass-10 ID</th><th style="width:16%">Official source</th>
  <th style="width:22%">Claim checked against the source</th>
  <th style="width:20%">Value this site publishes from it</th>
  <th style="width:20%">What the source said on {e(p10['pass_date'])}</th>
  <th style="width:7%">Verdict</th><th style="width:7%">Source link</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
</div>

<h2>Irregularities carried in the flag register</h2>
{irr}

<h2>Round 10 (previously reported)</h2>
<ul class="tight small">{carried}</ul>
<p class="tiny muted">The three supplied short links, S2 and the live homepage were re-read by round 10
(session c334fb1c); see
<a href="../reports/verification-2026-11-16.md">reports/verification-2026-11-16.md</a>.
That record is not duplicated in this ledger.</p>

<p class="tiny muted">{e(p10['conclusion'])}</p>
<p class="tiny muted">Raw observations: <code>data/pass10.json</code> — one row per registered source,
each row linking to its official source.</p>
"""
    return layout("pass10.html", f"Verification pass 10 · {p10['pass_date']}", body,
                  active="pass10.html",
                  description=f"Pass {p10['pass']} ledger: every official source (S1-S34) re-read on {p10['pass_date']} against the value this site publishes from it, with verdicts and source links.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Verification pass 10", page_url("pass10.html")),
    ])])


def page_figures():
    captions = {
        "footprint": ("How much counter each model needs", "True-scale footprint drawn from the manufacturer-published dimensions."),
        "temperature": ("Documented cooking temperature ranges", "Min–max from each official source; conflicts are shown, not hidden."),
        "presets": ("Preset-count conflict, document by document", "Why the site states 24 for the Emeril and four for the Chefman 8 Qt — and why the Chefman 6 Qt row stays blank."),
        "decision-tree": ("Choose by the job, not by the brand", "Decision support generated from the published dataset; not a recommendation."),
    }
    panels = ""
    for name in ("footprint", "temperature", "presets", "decision-tree"):
        svg = (FIGURES_DIR / f"{name}.svg").read_text(encoding="utf-8")
        cap, lede = captions[name]
        panels += (
            f'<div class="figure">'
            f'<h4 class="fighead">{e(cap)}</h4>'
            f'{svg}'
            f'<p class="figcap">{e(lede)}</p>'
            f'</div>'
        )
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Figures</p>
<h1>Figures and diagrams</h1>
<p class="lede">Four diagrams, all generated at build time from data/products.json. None of them contains a number
that this dataset does not hold, and each one carries the official sources of its own figures. They are diagrams,
not photographs: product-photography rights are undecided (Q-22, SG-23, flag F46), so the site stays
text-and-diagrams-only until a decision is recorded.</p>
{panels}
<p class="tiny muted">Regenerate: <code>python3 build.py</code>. Sources are cited per figure and the raw data is in
<code>data/products.json</code> → <code>figures</code>.</p>
"""
    return layout("figures.html", "Figures and diagrams", body,
                  active="figures.html",
                  description="Data-driven diagrams generated from the published dataset: footprint at true scale, temperature ranges, preset-count conflict, format decision tree.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Figures", page_url("figures.html")),
    ])])


PARALLEL_BUILDS = [
    ("research/index.html", "research/", "Deep-dive research",
     "Independent 25-source pass: a 90-field product table, a 23-row compliance matrix with verbatim quotations, a 17-item flag register (I-1 to I-17), a content plan and a 10-step automation pipeline.",
     "Maps the Chefman 6 Qt ASIN to **RJ38-3DBW-V2** with no caveat; the canonical site maps it to **RJ38-SQPF-3TDB-2W**. Both are real Chefman SKUs — see F32."),
    ("site/index.html", "site/", "Verification annex",
     "A second dataset and generator over the same three products: 53 spec fields, its own 382-assertion verifier, and a Kitchen 4.50% commission row.",
     "Also maps the 6 Qt ASIN to **RJ38-3DBW-V2** (F32), and still prints the old policy labels **§3(t)** and **§2(w)** where the live page says **§6(t)** and **§6(w)** (F27)."),
    ("session-3740f69d/index.html", "session-3740f69d/", "Session 3740f69d build",
     "Dashboard-style build: link-resolution evidence, a link-policy map for the supplied link.amazon URLs, tracking design and an analysis of Amazon's 2026 IP License Agent Terms.",
     "Prints the pre-F27 policy labels (Participant Requirements §2(t), §2(v)(w), §2(y)). Its link-policy reading agrees with the canonical site."),
    ("s2/index.html", "s2/", "Verified platform pass",
     "A compliance matrix, a verification log and its own flag register, generated from data/s2/ by scripts/build_s2_site.py with a build-date stamp.",
     "None found against the canonical site at the time of this pass; its citations were spot-checked and matched."),
    ("dashboard/index.html", "dashboard/", "Campaign dashboard",
     "Niches, commissions, links and tracking views for the same three products, built by a separate session.",
     "Maps the 6 Qt ASIN without the F32 caveat."),
    ("docs/index.html", "docs/", "Legacy docs build",
     "The earliest dashboard build. Retired; kept because its evidence files are cited by later passes.",
     "Its build command is already documented as broken against the shared data schema (F23)."),
    ("annex-88769516/index.html", "annex-88769516/", "Annex 88769516",
     "An independent annex build with its own content, tracking and flagged pages.",
     "Inherited advisory only; not re-verified by this pass."),
]


def page_previous_passes():
    rows = []
    for href, path, name, what, conflict in PARALLEL_BUILDS:
        rows.append(
            f'<tr><td><a href="{href}">{e(name)} ↗</a>'
            f'<div class="tiny">{repo_link(path + "index.html", "Source: " + path + "index.html")}</div></td>'
            f'<td class="small">{e(what)}</td>'
            f'<td class="small">{conflict.replace("**", "")}</td></tr>')
    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Previous passes</p>
<h1>Every parallel build in this repository, and which one is canonical</h1>
<p class="lede">Several agent sessions worked this repository at the same time. Nothing was thrown away, so {len(PARALLEL_BUILDS)} older builds are still published next to this one. That is a record of the work, but it is a bad thing to hand a reader cold: two of them answer the same question differently. This page says so, names the differences, and tells you which build to trust.</p>

<div class="callout warn">
  <strong>The canonical build is the root site you are on now</strong>
  <p class="small">It is the only build generated by <code>build.py</code>, verified by <code>verify.py</code> on every push, and the only one that reconciles the flags below. If you arrived here from a search result and landed on one of the older pages instead, everything on this page applies to what you are reading.</p>
</div>

<h2>Where the older builds disagree with this one</h2>
<div class="tablewrap">
<table>
  <caption>Parallel builds, what each adds, and where it diverges</caption>
  <thead><tr><th>Build</th><th>What it adds</th><th>Where it disagrees with the canonical site</th></tr></thead>
  <tbody>
  {chr(10).join(rows)}
  </tbody>
</table>
</div>
<p class="small muted">Every disagreement above is published, with its source links, on <a href="flagged.html">Flagged for review</a>: the model-number question is <strong>F32</strong>, the policy-label question is <strong>F27</strong>, the number of parallel builds is <strong>F35</strong>.</p>

<h2>Why the builds were not merged into one</h2>
<p class="small">Merging them would mean picking a winner for each disagreement on evidence that does not exist yet. For the model number the listing's product-information block was read on 2026-11-16 and published (F68), which settled the ASIN-to-model step for the two Chefman listings; only the model plate on a physical unit can say what ships against an ASIN, and that is still the account holder's to check. For the policy labels, the live page settles it and the canonical build already matches the live page — but rewriting another session's published pages to match would destroy the record of what that pass actually verified against.</p>

<h2>What "canonical" means here, precisely</h2>
<div class="tablewrap">
<table>
  <caption>How each build is gated</caption>
  <thead><tr><th>Build</th><th>Generator</th><th>Gate that runs on every push</th></tr></thead>
  <tbody>
    <tr><td>Root site (canonical)</td><td><code>build.py</code>{repo_link('build.py', '')}</td><td><code>verify.py</code> — no broken internal links, no specification row with a value but no official source, the required disclosure on every page, and no article number that is not in the verified dataset. {repo_link('verify.py', 'verify.py on GitHub')}</td></tr>
    <tr><td><code>site/</code></td><td><code>scripts/build_site.py</code>{repo_link('scripts/build_site.py', '')}</td><td><code>scripts/verify_site.py</code> — 382 assertions over <code>data/verified/</code>. {repo_link('scripts/verify_site.py', 'verify_site.py on GitHub')}</td></tr>
    <tr><td><code>s2/</code></td><td><code>scripts/build_s2_site.py</code>{repo_link('scripts/build_s2_site.py', '')}</td><td><code>--check</code> byte-comparison against a fresh rebuild. {repo_link('scripts/build_s2_site.py', 'build_s2_site.py on GitHub')}</td></tr>
    <tr><td>Others</td><td>their own scripts</td><td>No CI gate. They are preserved evidence, not a maintained product. {repo_link('.github/workflows/ci.yml', 'Canonical CI workflow')}</td></tr>
  </tbody>
</table>
</div>

<p class="small" style="margin-top:1.5rem"><a class="btn btn-ghost" href="flagged.html">See every open irregularity →</a> <a class="btn btn-ghost" href="reverification.html">The 2026-11-14 line-by-line re-read →</a></p>
"""
    return layout("previous-passes.html", "Previous passes", body,
                  active="previous-passes.html",
                  description="Catalogue of every parallel build published in this repository, where each one disagrees with the canonical site, and which build to trust.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Previous passes", page_url("previous-passes.html")),
    ])]
              )


# --------------------------------------------------------------------------- #
# Decision layer — Suggestions and Open questions (added 2026-11-15, arena/3ddfa50e)
#
# These two pages exist because the brief asks for a place to review improvements and
# choose a path *before* anything is implemented, and for a register of what must be
# known before a decision is reasonable. Both are generated from data/*.json, so a
# reviewer edits data and never a template. Every evidence link is an official source
# or a repository path; the row-source gate applies to both pages like any other.
# --------------------------------------------------------------------------- #

_STATE_LABEL = {
    "known": ("ok", "Known and sourced"),
    "missing": ("warn", "Missing - discoverable"),
    "unknowable": ("bad", "Needs account access"),
    "not_stated": ("warn", "The source does not state it"),
}


def _effort_chip(effort):
    return f'<span class="chip">{e(effort)}</span>'


def page_design_prompt():
    """Design/content/traffic suggestion layer — the paste-ready design prompt plus the
    D/A/T/V/R registers (arena/bf487400-zone1, compiled 2026-11-15).

    Published rather than left in session-3b99448e/suggestions.md because the brief asks
    for suggestions that feed a design prompt, a catchy-topic queue and an organic-traffic
    plan the owner can review before anything is implemented. Statuses describe the
    repository as built, not a plan; every row carries a source or repository link so the
    row-source guard covers these tables like any other.
    """
    d = DESIGN_PROMPT

    def chip(status):
        return {
            "implemented": '<span class="pill pill-ok">Implemented</span>',
            "partial": '<span class="pill pill-warn">Partial</span>',
            "pending": '<span class="pill pill-info">Pending</span>',
            "published": '<span class="pill pill-ok">Published</span>',
            "not-written": '<span class="pill pill-warn">Not written</span>',
        }.get(status, f'<span class="pill pill-info">{e(status)}</span>')

    def ev(item):
        """Evidence cell: registered source badges plus any repository links.

        Topic rows name their citations `cites`; every other register uses `sources`.
        """
        bits = []
        cites = item.get("sources") or item.get("cites")
        if cites:
            bits.append(src_links(cites))
        for ln in item.get("links") or []:
            url = ln["url"]
            if url.startswith("http"):
                bits.append(f'<a class="src-link" href="{e(url)}" target="_blank" '
                            f'rel="noopener">{e(ln["label"])} ↗</a>')
            else:
                bits.append(f'<a class="src-link" href="{e(url)}">{e(ln["label"])}</a>')
        return " ".join(bits) if bits else '<span class="tiny muted">see row note</span>'

    design_rows = "".join(
        f'<tr id="{e(x["id"].lower())}">'
        f'<td class="num">{e(x["id"])}</td>'
        f'<td><strong>{e(x["suggestion"])}</strong>'
        f'<div class="tiny muted">{e(x["why"])}</div>'
        f'<div class="tiny">Path: {e(x["path"])}</div>'
        f'<div class="tiny muted">{e(x["status_note"])}</div></td>'
        f'<td>{chip(x["status"])}</td>'
        f'<td class="small">{ev(x)}</td></tr>'
        for x in d["design"])

    topic_rows = []
    for x in d["topics"]:
        pub = (
            f'<div class="tiny">Published as <a href="{e(x["published_as"])}">'
            f'{e(x["published_as"].rsplit("/", 1)[-1])}</a></div>'
        ) if x.get("published_as") else ""
        topic_rows.append(
            f'<tr id="{e(x["id"].lower())}">'
            f'<td class="num">{e(x["id"])}</td>'
            f'<td><strong>{e(x["title"])}</strong>'
            f'<div class="tiny muted">{e(x["format"])} — {e(x["hook"])}</div>{pub}'
            f'<div class="tiny muted">{e(x["status_note"])}</div></td>'
            f'<td>{chip(x["status"])}</td>'
            f'<td class="small">{ev(x)}</td></tr>')

    tactic_rows = "".join(
        f'<tr id="{e(x["id"].lower())}">'
        f'<td class="num">{e(x["id"])}</td>'
        f'<td><strong>{e(x["tactic"])}</strong>'
        f'<div class="tiny muted">{e(x["how"])}</div>'
        f'<div class="tiny muted">{e(x["status_note"])}</div></td>'
        f'<td>{chip(x["status"])}</td>'
        f'<td class="small">{ev(x)}</td></tr>'
        for x in d["tactics"])

    voice_rows = "".join(
        f'<tr id="{e(x["id"].lower())}">'
        f'<td class="num">{e(x["id"])}</td>'
        f'<td>{e(x["rule"])}</td>'
        f'<td class="small">{e(x["why"])}</td>'
        f'<td class="small">{ev(x)}</td></tr>'
        for x in d["voice_rules"])

    decision_rows = "".join(
        f'<tr id="{e(x["id"].lower())}">'
        f'<td class="num">{e(x["id"])}</td>'
        f'<td>{e(x["suggestion"])}</td>'
        f'<td class="small">{e(x["options"])}</td>'
        f'<td class="small">{e(x["recommended"])}</td>'
        f'<td>{chip(x["status"])}<div class="tiny muted">{e(x["status_note"])}</div></td>'
        f'<td class="small">{ev(x)}</td>'
        f'<td class="small"><span class="blank">— your decision —</span></td></tr>'
        for x in d["decisions"])

    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Design prompt pack</p>
<h1>The design and editorial contract</h1>
<p class="lede">The design and content-production suggestion layer: a paste-ready design prompt, design suggestions with current implementation states, the article topic queue, organic-traffic tactics, editorial voice rules and a decision register. Every row is a suggestion for you to approve, reject or modify — the status column records which of them the repository already satisfies today.</p>

<div class="callout info">
  <strong>How this page fits the other registers.</strong>
  <p class="small"><a href="suggestions.html">Suggestions</a> is the governance queue (SG-01…): what to decide and what it costs. <a href="questions.html">Questions</a> is what is not known yet (Q-01…). <a href="decisions.html">Decisions &amp; handover</a> settles strategy — which niche, which channels, what to measure. <a href="topics.html">Content and traffic plan</a> is the proposal view of the article queue — intent, angle and citations per topic. <strong>This page</strong> is the design and content-production layer: how the site should look and read, whether each proposed article has shipped yet, and the tactics that turn the strategy into published pages. Product facts are not here — they live in <a href="data.html">the full dataset</a>, each with its official source.</p>
</div>

<h2 id="the-prompt">The design prompt</h2>
<p class="small">Paste the block below into any designer or AI assistant used to restyle the site. It describes the site exactly as it is today, names the components and rules that must survive a redesign, and ends with the acceptance criteria every change has to pass. Nothing in it asks for a claim the site cannot source.</p>
<pre class="prompt-block">{e(d["design_prompt"])}</pre>
<p class="tiny muted">Compiled {e(d["compiled"])} by {e(d["session"])}. If a request built from this prompt contradicts the verification rules inside it — an invented fact, unauthorised Program Content, a fake author or testing claim — the prompt is wrong and the rules win.</p>

<h2>Design suggestions</h2>
<p class="small muted">{e(d["how_to_read"])}</p>
<div class="tablewrap">
<table>
  <caption>Design suggestions — current canonical implementation</caption>
  <thead><tr><th>#</th><th>Suggestion · why · path</th><th>Status</th><th>Evidence</th></tr></thead>
  <tbody>{design_rows}</tbody>
</table>
</div>

<h2>Article topic queue</h2>
<p class="small">Catchy, reader-shaped topics for this product set, in the order they were proposed. Titles are working titles; each one names the format and the hook it leads with. Published rows link to the article they became. Nothing here may claim hands-on testing or state an Amazon price — those rules are inside the prompt above. <strong>Relationship to <a href="topics.html">topics.html</a>:</strong> that page is the proposal view (intent, serving product, citation each topic must carry); this table is the status view — which of the original working titles actually became articles, and which are still open.</p>
<div class="tablewrap">
<table>
  <caption>Topic queue — publication state derived from the article register</caption>
  <thead><tr><th>#</th><th>Working title · format · hook</th><th>Status</th><th>Sources it would cite</th></tr></thead>
  <tbody>{''.join(topic_rows)}</tbody>
</table>
</div>

<h2>Organic-traffic tactics</h2>
<p class="small">Channel strategy — which niche to build, which channels to run, what to measure — is decided on <a href="decisions.html">decisions.html</a>, with the per-topic promotion channels listed on <a href="topics.html">topics.html</a>. This table is the operational checklist behind them: what has already shipped, what is half-done and what has not started.</p>
<div class="tablewrap">
<table>
  <caption>Organic-traffic tactics — implemented versus planned</caption>
  <thead><tr><th>#</th><th>Tactic · how · status note</th><th>Status</th><th>Evidence</th></tr></thead>
  <tbody>{tactic_rows}</tbody>
</table>
</div>

<h2>Editorial voice rules</h2>
<p class="small">The voice half of the anti-slop rules. The enforcement half — the banned openers, the arithmetic guard, the claim checks — lives on <a href="decisions.html">decisions.html</a> and in <code>build.py</code>, where the build fails if a rule is broken.</p>
<div class="tablewrap">
<table>
  <caption>Current editorial voice rules</caption>
  <thead><tr><th>#</th><th>Rule</th><th>Why</th><th>Evidence</th></tr></thead>
  <tbody>{voice_rows}</tbody>
</table>
</div>

<h2>Decision register</h2>
<p class="small">How to use this register: for each row choose <strong>Approved</strong>, <strong>Rejected</strong> or <strong>Needs more info</strong>, write the choice and the date in the last column, then implement only approved rows. Rejected rows stay on the register so they are not proposed again. Rows that are blocked name the question that unblocks them.</p>
<div class="tablewrap">
<table>
  <caption>Design choices — implementation state is not an owner approval</caption>
  <thead><tr><th>#</th><th>Suggestion</th><th>Options considered</th><th>Recommended path</th><th>Status today</th><th>Evidence</th><th>Decision</th></tr></thead>
  <tbody>{decision_rows}</tbody>
</table>
</div>

<div class="callout note" style="margin-top:1.5rem">
  <strong>Related registers.</strong>
  <a href="suggestions.html">Governance suggestions (SG-01…)</a> ·
  <a href="questions.html">Open questions (Q-01…)</a> ·
  <a href="decisions.html">Niche, traffic and measurement decisions</a> ·
  <a href="topics.html">Content and traffic plan (topic proposals)</a> ·
  <a href="flagged.html">Flagged for review</a>
</div>
"""
    return layout("design-prompt.html", "Design prompt pack", body,
                  active="design-prompt.html",
                  description="Design, content and traffic suggestions for this site: a paste-ready design prompt, design suggestions with current implementation states, the article topic queue, organic-traffic tactics, voice rules and a decision register to review before anything changes.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Design prompt pack", page_url("design-prompt.html")),
    ])])


def page_suggestions():
    data = SUGGESTIONS
    items = data['suggestions']
    lookup = {row['id']:row for row in items}
    states = {'complete':('pill-ok','Complete'), 'partial':('pill-warn','Partial'), 'gated':('pill-warn','Gated'), 'superseded':('pill-info','Superseded'), 'open':('pill-info','Open')}
    def chip(row):
        cls,label=states[row['current_state']]
        return f'<span class="pill {cls}">{label}</span>'
    def evidence(row):
        official=' '.join(f'<a href="{e(v["url"])}" target="_blank" rel="noopener">{e(v["label"])}</a>' for v in row['evidence'][:2])
        return official + f' <a href="{REPO_BLOB}data/suggestions.json">Current state record</a>'
    counts={key:sum(r['current_state']==key for r in items) for key in states}
    brief=data.get('decision_brief') or {}
    for row in brief.get('items',[]):
        if row['id'] not in lookup:
            raise SystemExit('BUILD FAILED — unknown suggestion in decision brief: '+row['id'])
    briefs=''.join(f'<li><strong><a href="#{e(r["id"].lower())}">{e(r["id"])}</a> — {e(r["ask"])}</strong><p class="small muted">{e(r["why"])}</p></li>' for r in brief.get('items',[]))
    rows=''.join(f'<tr><td><a href="#{e(r["id"].lower())}">{e(r["id"])}</a></td><td>{e(r["title"])}<div class="small muted">{e(r["current_note"])}</div></td><td>{chip(r)}</td><td>{evidence(r)}</td></tr>' for r in items)
    cards=[]
    for row in items:
        opts=''.join(f'<li><strong>{e(o["label"])}</strong><p>{e(o["what"])}</p><p class="tiny muted">Original effort: {e(o["effort"])} · original risk: {e(o["risk"])} · reversible: {"yes" if o.get("reversible") else "no"}</p></li>' for o in row['options'])
        blocks=' '.join(f'<a href="questions.html#{e(q.lower())}">{e(q)}</a>' for q in (row.get('blocked_by') or [])) or 'None recorded in the original proposal.'
        cards.append(f"""<details class="sug" id="{e(row['id'].lower())}" data-suggestion><summary>{e(row['id'])} · {e(row['title'])} {chip(row)}</summary><p><strong>Current review — {e(row['current_reviewed_on'])}.</strong> {e(row['current_note'])}</p><div class="evidence">{evidence(row)}</div><h3>Original proposal and alternatives</h3><p class="small muted">Historical recommendation, not a fresh factual claim or a request to repeat shipped work. Previous problem wording is preserved so a reviewer can understand the options. Current states and account/evidence gates above take precedence.</p><p class="small"><strong>Original problem.</strong> {e(row['problem'])}</p><ol class="paths">{opts}</ol><p class="small"><strong>Original recommendation.</strong> {e(row['recommendation'])} {e(row['why'])}</p><p class="small"><strong>Linked questions.</strong> {blocks}</p><p class="small"><a href="decision-log.html#{e(row['id'].lower())}">Draft or export a different choice →</a></p></details>""")
    paths=[]
    for path in data.get('paths',[]):
        if any(i not in lookup for i in path['contains']):
            raise SystemExit('BUILD FAILED — unknown suggestion in path '+path['id'])
        members=' '.join(f'<a href="#{e(i.lower())}">{e(i)}</a>' for i in path['contains'])
        paths.append(f'<section id="{e(path["id"].lower())}"><h3>{e(path["id"])} · {e(path["name"])}</h3><p class="small">{e(path["promise"])}</p><p>{members}</p></section>')
    body=f"""<p class="crumbs"><a href="index.html">Home</a> / Suggestions</p><p class="section-eyebrow">Reviewable decisions · current states</p><h1>What changed. What still needs evidence.</h1><p class="lede">Repository work proceeds autonomously. This queue records what actually shipped, the boundaries that remain, and the alternatives a reviewer can choose. It never turns an agent action into a person’s approval.</p>
<section class="desk" id="decision-desk" aria-label="Current suggestion counts"><p class="small">{len(items)} total = {counts['complete']} complete + {counts['superseded']} superseded + {counts['partial']} partial + {counts['gated']} gated + {counts['open']} open.</p><p class="tiny muted">Complete can mean an implemented repository feature or a recorded plan. Partial never means a deployed collector or confirmed account. Historical action records are not added to these counts.</p></section>
<section class="card decision-brief" id="decision-brief"><h2 style="margin-top:0">The remaining boundaries, in brief</h2><p class="small">{e(brief.get('intro',''))}</p><ol class="tight">{briefs}</ol><p class="tiny">Order is editorial judgement. {src_links(['S2','S42','S44'])}</p></section>
<h2>Current register</h2><div class="tablewrap"><table><caption>Every suggestion has exactly one current implementation state</caption><thead><tr><th>ID</th><th>Suggestion / current answer</th><th>State</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Review a row and its alternatives</h2><div class="suggestion-toolbar" data-suggestion-toolbar hidden><label for="suggestion-query">Find a suggestion</label><input id="suggestion-query" type="search" placeholder="Search the decisions and alternatives"><output aria-live="polite"></output></div><p class="small">Open any row. A different choice can be drafted locally on <a href="decision-log.html">the decision log</a>; nothing is submitted from that page. The earlier proposals are labelled history rather than published as today’s facts.</p>{''.join(cards)}
<details><summary>Original grouped paths (historical planning)</summary><p class="small muted">These earlier bundles are preserved for review; current per-row states supersede old claims about what remains unbuilt.</p>{''.join(paths)}</details><p class="section-note"><a href="questions.html">Known facts and missing evidence</a> · <a href="design-prompt.html">Current design/editorial brief</a> · <a href="executive-summary.html">Executive summary</a>.</p>"""
    return layout('suggestions.html','Suggestions & current decisions',body,active='suggestions.html',description='A current, reviewable decision queue: implemented publication work, partial delivery, explicit evidence gates and preserved alternatives.',jsonld_blocks=[breadcrumbs_jsonld([('Home',SITE_BASE),('Suggestions',page_url('suggestions.html'))])])

def page_questions():
    q = QUESTIONS
    groups = []
    for item in q["questions"]:
        if item["group"] not in groups:
            groups.append(item["group"])

    # summary table first: every row carries a source link
    rows = []
    for item in q["questions"]:
        cls, label = _STATE_LABEL[item["state"]]
        first = item["sources"][0]
        extra = (" " + " ".join(f'<a href="{e(y["url"])}" target="_blank" rel="noopener">evidence ↗</a>'
                                for y in item["sources"][1:]))
        rows.append(
            f'<tr><td class="num"><a href="#{e(item["id"].lower())}">{e(item["id"])}</a></td>'
            f'<td>{e(item["question"])}</td><td class="small">{e(item["group"])}</td>'
            f'<td><span class="pill {cls}">{e(label)}</span></td>'
            f'<td class="small"><a href="{e(first["url"])}" target="_blank" rel="noopener">source ↗</a>{extra}</td></tr>'
        )

    def block(item):
        cls, label = _STATE_LABEL[item["state"]]
        known = "".join(f'<li>{e(k)}</li>' for k in item["what_we_know"])
        srcs = " ".join(
            f'<a class="src-link" href="{e(x["url"])}" target="_blank" rel="noopener">{e(x["label"])} ↗</a>'
            for x in item["sources"]
        )
        blocks = item.get("blocks") or []
        block_html = " ".join(
            f'<a class="src" href="suggestions.html#{e(x.lower())}">{e(x)}</a>' for x in blocks
        ) or '<span class="tiny muted">Does not block anything on its own.</span>'
        # A question that can be answered carries its answer. This is the column
        # the brief asked for: not only what is missing, but what the answer is
        # where an official source already settles it.
        answer = item.get("answer")
        answer_html = (
            f'<div class="callout ok"><strong>Answer.</strong> {e(answer)}</div>'
            if answer else
            '<div class="callout warn"><strong>Answer.</strong> '
            'No answer is published here. The official sources listed below were read '
            'and do not settle it, or it cannot be settled from outside the account. '
            'The "How to find it out" line names the step that would.</div>'
        )
        return f"""
<article class="qcard" id="{e(item['id'].lower())}">
  <div class="sug-head">
    <div>
      <div class="tiny muted">{e(item['id'])} · {e(item['group'])}</div>
      <h3>{e(item['question'])}</h3>
    </div>
    <span class="pill {cls}">{e(label)}</span>
  </div>
  <p><strong>Why it matters.</strong> {e(item['why_it_matters'])}</p>
  {answer_html}
  <div class="twocol">
    <div><p class="label">What we know, and can prove</p><ul class="tight">{known}</ul></div>
    <div>
      <p class="label">What is missing</p>
      <p class="small">{e(item['what_is_missing'])}</p>
      <p class="label">How to find it out</p>
      <p class="small">{e(item['how_to_discover'])}</p>
    </div>
  </div>
  <div class="evidence"><strong>Official sources.</strong> {srcs}</div>
  <p class="small"><strong>Blocks:</strong> {block_html}</p>
</article>"""

    sections = []
    for g in groups:
        items = [x for x in q["questions"] if x["group"] == g]
        sections.append(f'<h2>{e(g)}</h2>' + "".join(block(x) for x in items))

    counts = {k: sum(1 for x in q["questions"] if x["state"] == k) for k in _STATE_LABEL}

    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Open questions</p>
<h1>What must be answered before a decision is reasonable</h1>
<p class="lede">A decision is only as good as the information behind it. This page separates what we
know and can prove from what we do not know but could look up, and from what cannot be established
at all without information that only the account holder holds. Every suggestion that cannot be
settled without you links to the row that blocks it.</p>

<div class="callout warn">
  <strong>Read the four states before the questions.</strong>
  <span class="pill ok">Known and sourced</span> sourced fact or recorded repository decision; the row gives its evidence/date.
  <span class="pill warn">Missing - discoverable</span> not established here; the row names the required lookup or deployment step.
  <span class="pill bad">Needs account access</span> outside the account it cannot be known at all.
  <span class="pill warn">The source does not state it</span> the cited source or recorded permissions do not establish the fact.
</div>

<p class="small muted">{e(q['preamble'])}</p>

<h2>Register</h2>
<p class="small">{counts['known']} known and sourced · {counts['missing']} missing but discoverable ·
{counts['not_stated']} not stated by the official source · {counts['unknowable']} requiring account access ·
{len(q['questions'])} total.</p>
<div class="tablewrap"><table>
  <thead><tr><th>#</th><th>Question</th><th>Group</th><th>State</th><th>Source</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table></div>

<h2>The questions in full</h2>
{''.join(sections)}

<div class="callout note" style="margin-top:1.5rem">
  <strong>Related registers.</strong>
  A parallel session published its own question set the same day; it is kept alongside this one
  because it covers ground this register does not. <a href="decision-gate.html">Questions and
  information gaps (parallel pass)</a> · <a href="marketing-directions.html">Marketing directions
  (parallel pass)</a> · <a href="suggestions.html">This pass's suggestions</a>
</div>
"""
    qurl = page_url("questions.html")
    # FAQPage. Every answer below is assembled only from fields that the page above
    # already prints in full — what_we_know, what_is_missing and how_to_discover —
    # so the structured data restates visible content and adds nothing.
    faq = []
    for item in q["questions"]:
        answer = []
        if item.get("what_we_know"):
            answer.append("What we know: " + " ".join(item["what_we_know"]))
        if item.get("what_is_missing"):
            answer.append("What is missing: " + item["what_is_missing"])
        if item.get("how_to_discover"):
            answer.append("How to find it out: " + item["how_to_discover"])
        if not answer:
            continue
        faq.append({
            "@type": "Question",
            "name": item["question"],
            "acceptedAnswer": {"@type": "Answer", "text": " ".join(answer)},
        })
    ld = [
        {
            "@type": "FAQPage",
            "@id": qurl + "#faq",
            "url": qurl,
            "mainEntity": faq,
        },
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Questions and gaps", qurl),
        ]),
    ]
    return layout("questions.html", "Open questions", body, active="questions.html",
                  description="The questions, information and answers that must be settled before a decision on this site is reasonable, separated into known, discoverable, not-stated and account-only.",
                  jsonld_blocks=ld)


# --------------------------------------------------------------------------- #
# 2026-11-15 (arena/633b115f, X-633b115f): decision pages.
# Suggestions are NOT implemented. Each one is a choice for the owner to make
# before any change is made. Questions are the facts still missing before a
# decision can be made reasonably. Opinions carry no official source; they are
# labelled as opinions and point to the Flagged page instead of inventing one.
# --------------------------------------------------------------------------- #

# Literal registers belonging to the arena/633b115f decision pages below. Renamed on merge
# (2026-11-15) because they collided with the JSON-backed SUGGESTIONS/QUESTIONS above.
SUGGESTIONS_ALT = [
    # id, area, suggestion, basis text, basis source ids, options, effort
    ("SG-01", "Design",
     "Make the home page a product finder: one question at the top (\"Which air fryer fits how you cook?\") and the three products as rows of comparable facts, not three identical cards.",
     "Opinion, not a fact. The current dashboard repeats the same card for each product. Flagged so you can decide.",
     [], "A) Keep the dashboard. B) Finder-first home page (recommended for a buyer audience). C) Editorial home page led by one article.",
     "Medium"),
    ("SG-02", "Design",
     "Use photographs the owner takes, or licensed images, instead of generic stock or generated imagery. Generic imagery is the main reason a site reads as machine-made.",
     "Amazon provides Program Content (images, text, linking tools) to Associates. Image rights for anything else are not covered. Confirm before use.",
     ["S1"], "A) Owner photos (recommended). B) Amazon Program Content images, used as the Agreement allows. C) Text-only pages.",
     "Low to medium"),
    ("SG-03", "Trust and disclosure",
     "Keep the disclosure next to every Amazon link as well as in the top bar. Confirm every product card, table row and article has it.",
     "The Operating Agreement requires an identification of the Associate relationship, and FTC guidance says disclosures must be hard to miss and placed with the endorsement itself.",
     ["S1", "S5", "S8"], "A) Top bar plus link-level text (recommended). B) Top bar only (not recommended).",
     "Low"),
    ("SG-04", "Pricing and reviews",
     "Do not display Amazon prices, availability, star ratings or review counts until they come through an approved Amazon API. Keep those cells blank and flagged.",
     "Program Policies restrict price and review display (§2(b) and §6(t) as quoted in data/products.json). PA-API eligibility is described in Amazon's Associates help.",
     ["S2", "S19", "S24"], "A) Keep blank and link to the live Amazon page (current, compliant). B) Apply for API access once eligible (requires the Question Q-05 answer first).",
     "Low now, medium later"),
    ("SG-05", "Content",
     "Write only from facts you can source, and state any first-hand experience only if the owner actually uses the product. Do not write reviews for products that have not been tried.",
     "FTC Disclosures 101: you cannot talk about your experience with a product you have not tried; a paid recommendation cannot say a product is great if you thought it was terrible.",
     ["S8", "S7"], "A) Spec-and-policy articles only (current, compliant). B) Add first-hand reviews after the owner tests each product, with the test recorded.",
     "Medium"),
    ("SG-06", "Content and SEO",
     "Pick article topics from real search demand, not from guesses. Candidate clusters: air fryer capacity for household size, air fryer vs toaster oven, and how to read a manufacturer's temperature range.",
     "No official source publishes search demand for these topics. Demand data must come from a tool the owner chooses and must be saved to the repository before any topic is treated as trending.",
     [], "A) Choose a keyword tool and export its data first (recommended). B) Publish the current topics without demand data (not recommended).",
     "Medium"),
    ("SG-07", "Tracking",
     "Measure clicks with Associates tracking IDs (sub-tags), one per page or article, so the owner can see which content drives sales.",
     "Amazon defines tracking IDs and sub-tags in the Associates help topic. Click and order reporting is available only after the account is live.",
     ["S6", "S3"], "A) One tracking ID per page (recommended). B) One ID for the whole site (simpler, less detail).",
     "Low"),
    ("SG-08", "Links",
     "Use the full canonical product link format for outbound Amazon links, with the Associates tag, instead of the three short links, once the owner confirms which product each short link should send people to.",
     "Each short link resolves today to a product page (S17, S16). Who owns the short links is not confirmed (flag F2). The Operating Agreement requires the tagged link formats Amazon provides (§1).",
     ["S17", "S16", "S1"], "A) Keep the short links until the owner confirms them. B) Switch to tagged product-page links after Q-01 and Q-02 are answered (recommended).",
     "Low"),
    ("SG-09", "Eligibility",
     "Confirm the Associates account passes the Application Review before publishing money pages, or publish content without outbound links until it does.",
     "Amazon's Application Review topic lists qualifying-sales and content requirements. The owner must check their own account status.",
     ["S4"], "A) Check status now, publish after approval (recommended). B) Publish content with no purchase links until approved. C) Use a different affiliate program for now (new research required).",
     "Low"),
    ("SG-10", "Market",
     "Decide which Amazon store the site targets. The three supplied links point to amazon.com (US). The owner is in Osaka, Japan.",
     "The Operating Agreement names the Amazon sites in Schedule 1, and Japan appears in the Associates country list. Whether a Japan-based Associate may promote US listings is not confirmed.",
     ["S1"], "A) Stay on amazon.com and confirm eligibility (current links). B) Research amazon.co.jp products and build a separate Japan site.",
     "High (changes the product set)"),
    ("SG-11", "Automation",
     "Require the build gate to pass before any article or page is published. A failed gate blocks publication.",
     "The repository's verify.py gate checks broken links, unsourced values and missing disclosures, and the Pages workflow runs it on every push.",
     [], "A) Keep the gate blocking (recommended). B) Warn only (not recommended; allows unsourced values to ship).",
     "Low"),
    ("SG-12", "Freshness",
     "Set a re-verification interval for every price-free fact on the site (specs, policy quotes, links), and show the date on each page.",
     "Official pages change. The site already records the verification date. The interval itself is a choice; no official source sets it.",
     [], "A) Every 30 days. B) Every 90 days (recommended for spec data). C) Only when the owner asks.",
     "Low"),
]

QUESTIONS_ALT = [
    # id, question, known (sourced), missing, how to find out, unblocks, source ids
    ("Q-01", "Who owns the three link.amazon short links, and are these the products the owner intends to promote?",
     "Re-read on 2026-11-15: each short link resolves to a product page. B04G1MEwY → B0CDY277D3 (CHEFMAN 6 Qt Dual Basket); B02NbDxp3 → B09B7SB46R (Emeril Lagasse 26QT); B00hJ57DV → B08DKYBTPH (CHEFMAN 8 Qt TurboFry).",
     "Who created the short links, and whether they were meant for these products. The short-link owner is not published.",
     "Open the owner's Associates account and check which tag the short links carry. Amazon's tracking-ID help explains the tag format.",
     "SG-08, every product page", ["S17", "S16", "S6"]),
    ("Q-02", "Which Associates account and tracking ID will the site use?",
     "Amazon defines tracking IDs and sub-tags in its help topic.",
     "The account name, tracking ID and sub-tag plan are not in the repository.",
     "Associates Central → tracking IDs (see the help topic). Record the chosen ID in data/config.json.",
     "SG-07, SG-08", ["S6"]),
    ("Q-03", "Is the Associates account approved and active, and does it meet the Application Review requirements?",
     "Application Review lists qualifying-sales and content requirements, including a time window for the sales.",
     "Account status and sales history are not known to this repository.",
     "Read the Application Review topic and the account's status page. Record the result.",
     "SG-09", ["S4"]),
    ("Q-04", "Which commission rate applies to each of the three products?",
     "The Standard Commission Income Statement publishes a rate table. Rows have not yet been matched to these three products' categories by a verified read on 2026-11-15.",
     "The category-to-rate mapping for each product is not confirmed.",
     "Read the rate table on the Commission Income Statement page and match each product's category. Do not estimate.",
     "Commission-potential figures on every product page", ["S3"]),
    ("Q-05", "What are the current price, availability, star rating and review count for each product?",
     "Program Policies restrict displaying Amazon prices and reviews unless they come from an approved Amazon API. The site does not hold that access.",
     "No price, availability, rating or review count is published by this site, by design.",
     "Check API eligibility on the PA-API pages, and read Amazon's PA-API 5 deprecation notice for the dates before choosing an API.",
     "SG-04", ["S2", "S19", "S24"]),
    ("Q-06", "Which Amazon store should the site target, given the owner is in Osaka, Japan?",
     "The Operating Agreement defines the Amazon sites in Schedule 1. The country selector on the Operating Agreement page lists Japan.",
     "Whether a Japan-based Associate may promote amazon.com listings is not confirmed.",
     "Read Schedule 1 and the Japan Associates pages. Ask Associates support if the answer is unclear.",
     "SG-10", ["S1"]),
    ("Q-07", "Is RJ38-SQPF-3TDB-2W the exact model sold under ASIN B0CDY277D3?",
     "The owner's manual matches the listing wording (dual baskets, easy-view windows, Hi-Fry, Sync Finish), and since 2026-11-16 the listing's own Product information block states Model Number and Part Number RJ38-SQPF-3TDB-2W (S16).",
     "Nothing for the listing read. A model plate on a physical unit is still the only way to check what ships against the ASIN.",
     "Done 2026-11-16 by session arena/ba29c641 — see F68 and reports/asin-model-mapping-2026-11-16.md. To go further: read the plate on an owned unit, or ask Chefman which SKU is behind the ASIN.",
     "Product page spec rows", ["S10", "S16"]),
    ("Q-08", "Which model is sold under ASIN B09B7SB46R (Emeril Lagasse 26QT)?",
     "The owner's manual FAFO-001 and the brand product page (4-00675-02A-VN) describe the Emeril 26QT French Door air fryer, and the listing read on 2026-11-16 states 4-00675-02X-VN in both its Model Number and Part Number rows (S28) — one character from the brand page's string.",
     "Which of the three strings is the model printed on the unit. The listing is now confirmed; the reconciliation is not.",
     "Done: the block was read on 2026-11-16 (F68). Remaining step: ask Emeril Everyday support which SKU sits behind ASIN B09B7SB46R (F70).",
     "Product page spec rows", ["S15", "S14", "S16"]),
    ("Q-09", "Which Chefman 8 Qt model is sold under ASIN B08DKYBTPH: RJ38-SQSS-8T or RJ38-8T-BLACK?",
     "The brand's owner's manual names RJ38-SQSS-8T. A different brand page lists RJ38-8T-BLACK. The two model names conflict in the sources.",
     "The model behind the ASIN is not confirmed.",
     "Read the 'Product information' block on the listing and compare the model number with each brand page.",
     "Product page spec rows", ["S13", "S26", "S12"]),
    ("Q-10", "What warranty and return terms apply to each product on Amazon?",
     "Brand pages may describe warranty for units the brand sells; the Amazon listing's seller terms may differ.",
     "The terms for the Amazon listing are not confirmed by this repository.",
     "Read the 'Returns and warranty' section on each listing page, and record the seller shown.",
     "Product pages, buying guide", ["S16", "S14"]),
    ("Q-11", "What tax and payment information must the payee provide, and what is the minimum payment threshold?",
     "The Operating Agreement is the governing document. Payment and tax terms are not in the pages this repository has read.",
     "This repository has not read the payment or tax pages on 2026-11-15, so no tax or threshold figure is published here.",
     "Read the payment and tax help pages in Associates Central. Record the figures with their source and date before publishing any of them.",
     "Any earnings or payout statement on the site", ["S1"]),
    ("Q-12", "What is the search demand for the air-fryer topics the site wants to cover?",
     "No official source publishes search demand. The site's article topics are a proposal.",
     "Search volume, trend and competition data for each topic are not held in the repository.",
     "Choose a keyword tool, export the data for the candidate topics, and save the export under data/ with the date.",
     "SG-06", []),
    ("Q-13", "Which product experiences has the owner personally tested?",
     "FTC guidance: you cannot talk about your experience with a product you have not tried.",
     "No first-hand test is recorded for any of the three products.",
     "Test the products, or do not describe them as tested. Record each test (date, what was tested) in the repository.",
     "SG-05", ["S8"]),
    ("Q-14", "Is the owner's use of brand names and logos in headlines allowed under Amazon's Trademark Guidelines?",
     "Program Policies incorporate the Associates Trademark Guidelines by reference (Operating Agreement preamble).",
     "The site has not checked its headlines and images against the Trademark Guidelines.",
     "Read the Trademark Guidelines linked from the Program Policies, then review each headline and image.",
     "SG-02, article headlines", ["S2", "S1"]),
]



def page_decision_log():
    """Owner decision log (2026-11-16, arena/ba29c641).

    The brief asks for two things that pull against each other: a section where a human reviews
    suggestions and chooses a path *before* anything changes, and no manual input required of the
    owner to keep the project moving. They meet in one rule, computed here from the same registers
    rather than asserted in prose: a suggestion whose recommended path is reversible, low-risk and
    unblocked by an account-only fact carries that path as a default; everything else waits. A
    picker records a real choice over any default, and the page exports the file a later pass reads.
    """
    s = SUGGESTIONS
    log = DECISION_LOG
    qinfo = {q["id"]: q for q in QUESTIONS["questions"]}
    recorded = {c["id"]: c for c in (log.get("choices") or [])}
    safe_risk = ("none", "low")

    def letter_of(label):
        """The path letter an option label names.

        The register is not uniform: most labels read 'A. Rebuild the landing page', a row added by
        another pass reads just 'A', and another would read 'B)'. Matching only on '<letter>.' would
        have silently dropped a suggestion out of the default rule — and a suggestion that drops out
        stops being reviewable, which is the failure mode this page exists to avoid. Any leading
        letter, punctuated or not, is accepted. (2026-11-16, arena/ba29c641.)
        """
        m = re.match(r"\s*([A-Za-z])\s*[\.\):]?", label or "")
        return m.group(1).upper() if m else ""

    def default_for(sg):
        """Return (letter, label, kind, reason) for one suggestion's stand-if-silent outcome."""
        current = sg.get("current_state")
        if current in ("complete", "superseded"):
            return ("", "Current implementation", "done", sg["current_note"])
        if current in ("partial", "gated"):
            return ("", "Current evidence/deployment boundary", "hold", sg["current_note"])
        rec = (sg.get("recommendation") or "").strip()
        letter = rec[:1].upper() if rec else ""
        opts = sg.get("options") or []

        chosen = next((o for o in opts if letter_of(o.get("label")) == letter), None) if len(letter) == 1 else None
        if (sg.get("effort") or "").strip().lower() in ("done", "shipped", "complete", "complete."):
            return (letter, (chosen or {}).get("label", ""), "done",
                    "Recorded as done in the register: the outcome is on the row, so no path is waiting.")
        if chosen is None:
            return ("", "", "hold", "The recommendation does not name a lettered path this register "
                    "can match, so there is nothing to default to.")
        blocked = sg.get("blocked_by") or []
        hard = [b for b in blocked if qinfo.get(b, {}).get("state") == "unknowable"]
        if hard:
            return (letter, chosen.get("label", ""), "hold",
                    "It depends on a fact only the account holder can supply ("
                    + ", ".join(hard) + "), so silence is not consent here.")
        if chosen.get("reversible") is False:
            return (letter, chosen.get("label", ""), "hold",
                    "Marked not reversible: an irreversible change waits for a person.")
        if (chosen.get("risk") or "").strip().lower() not in safe_risk:
            return (letter, chosen.get("label", ""), "hold",
                    "Risk is " + str(chosen.get("risk")) + ", above the low bar this register sets "
                    "for acting without an answer.")
        return (letter, chosen.get("label", ""), "auto",
                "Reversible, risk " + str(chosen.get("risk")) + ", no account-only blocker, so the "
                "default stands until a picker overrules it.")

    order = sorted(s["suggestions"], key=lambda x: -(x["impact"] * x["confidence"]))
    computed = {sg["id"]: default_for(sg) for sg in order}
    # 'done' rows are neither auto nor hold: count them separately so the three stats add up.
    n_auto = sum(1 for v in computed.values() if v[2] == "auto")
    n_hold = sum(1 for v in computed.values() if v[2] == "hold")
    n_done = sum(1 for v in computed.values() if v[2] == "done")
    assert n_auto + n_hold + n_done == len(order), "decision-log: a suggestion fell out of the default rule"

    rows = []
    for sg in order:
        letter, label, kind, reason = computed[sg["id"]]
        blocked = sg.get("blocked_by") or []
        blist = " ".join(
            f'<a class="src" href="questions.html#{e(q.lower())}">{e(q)}</a>'
            for q in blocked) or '<span class="tiny muted">nothing blocked</span>'
        ev = [x["url"] for x in sg["evidence"] if x["url"].startswith("https://")]
        ev_links = " ".join(
            f'<a class="src-link" href="{e(u)}" target="_blank" rel="noopener">'
            f'{e(u.split("//")[-1][:30])} ↗</a>' for u in ev[:2])
        ev_links += f' <a class="src-link" href="{REPO_BLOB}data/suggestions.json">Current state record</a>'
        rec = recorded.get(sg["id"])
        if rec:
            state = (f'<span class="pill pill-ok">recorded</span>'
                     f'<div class="tiny">{e(str(rec.get("chosen_path", "")))} · '
                     f'{e(str(rec.get("recorded_at", "")))}</div>')
        elif kind == "auto":
            state = f'<span class="pill pill-ok">default {e(letter)}</span>'
        elif kind == "done":
            state = '<span class="pill pill-info">done</span>'
        else:
            state = '<span class="pill pill-warn">open</span>'
        rows.append(
            f'<tr id="{e(sg["id"].lower())}">'
            f'<td class="num">{e(sg["id"])}</td>'
            f'<td><a href="suggestions.html#{e(sg["id"].lower())}">{e(sg["title"])}</a>'
            f'<div class="tiny muted">{e(sg["area"])} · priority {sg["impact"] * sg["confidence"]}</div></td>'
            f'<td class="small">{e((label or sg.get("recommendation", "")).strip())}</td>'
            f'<td class="small">{e(reason)}<div class="tiny muted">Blocked by: {blist}</div></td>'
            f'<td>{state}</td>'
            f'<td class="small">{ev_links} <a class="src" href="flagged.html">Flagged ↗</a></td>'
            f'</tr>')

    fields = []
    for sg in order:
        letter, label, kind, reason = computed[sg["id"]]
        opts_html = "".join(
            f'<label class="dec-opt"><input type="radio" name="dec-{e(sg["id"])}" '
            f'value="{e((o.get("label") or "").strip()[0])}" data-sg="{e(sg["id"])}">'
            f'<span>{e(o.get("label"))}</span>'
            f'<em class="tiny muted">effort {e(str(o.get("effort")))} · risk {e(str(o.get("risk")))}</em>'
            + ('<b class="tag-default">default</b>'
               if kind == "auto" and letter_of(o.get("label")) == letter else "")
            + '</label>'
            for o in (sg.get("options") or []))
        fields.append(
            f'<fieldset class="dec-row" data-sg="{e(sg["id"])}" '
            f'data-title="{e(sg["title"])}" data-default="{e(letter if kind == "auto" else "")}">'
            f'<legend><a href="suggestions.html#{e(sg["id"].lower())}">{e(sg["id"])}</a> '
            f'{e(sg["title"])} '
            + (f'<span class="pill pill-ok">default {e(letter)}</span>' if kind == "auto"
               else '<span class="pill pill-info">already recorded as done</span>' if kind == "done"
               else '<span class="pill pill-warn">evidence / deployment gate</span>')
            + '</legend>'
            f'<p class="tiny muted">{e(sg.get("current_note", ""))[:220]}'
            f'{"…" if len(sg.get("problem", "")) > 220 else ""}</p>'
            f'{opts_html}'
            f'<label class="hold-row"><input type="radio" name="dec-{e(sg["id"])}" value="HOLD" '
            f'data-sg="{e(sg["id"])}"><span>Hold this one — change nothing</span></label>'
            f'<textarea class="dec-note" rows="2" aria-label="Optional note for {e(sg["id"])}" data-sg="{e(sg["id"])}" '
            f'placeholder="Optional: a condition, a date, or why. This travels with your choice."></textarea>'
            f'</fieldset>')

    if recorded:
        rec_tbl = ('<div class="tablewrap"><table><thead><tr><th>Suggestion</th><th>Chosen path</th>'
                   '<th>Recorded</th><th>Note</th></tr></thead><tbody>' + "".join(
                       f'<tr><td class="num"><a href="#{e(c["id"].lower())}">{e(c["id"])}</a></td>'
                       f'<td>{e(str(c.get("chosen_path", "")))}</td>'
                       f'<td>{e(str(c.get("recorded_at", "")))}</td>'
                       f'<td class="small">{e(str(c.get("note", "") or "—"))} '
                       f'<a class="src" href="flagged.html">context ↗</a></td></tr>'
                       for c in (log.get("choices") or [])) + "</tbody></table></div>")
    else:
        rec_tbl = (
          '<div class="callout note"><p class="small" style="margin:0">No owner decision is recorded '
          'in the repository yet, so every row below stands on its default. That is the designed state, '
          'not a gap: <code>choices</code> stays empty until a person chooses, because a session that '
          'filled it would be inventing an instruction. ' + str(n_auto) + ' suggestions carry a default '
          'a later pass may implement without asking; ' + str(n_hold) + ' hold for an answer'
          + (f'; {n_done} are recorded as done.' if n_done else '.') + '</p></div>')

    # ---- "start here" triage, computed (SG-26 path A, implemented 2026-11-16 by arena/ba29c641) ----
    # The register already carries the order: every suggestion lists what it unblocks in `blocks`, and
    # every question lists the suggestions it gates. Downstream size = transitive closure of those two
    # arrays, so a row that frees four others outranks one that frees none, and the ranking regenerates
    # when a row is edited instead of being retyped by the next pass (the class F63 and F73 document).
    blocks_sg = {x["id"]: list(x.get("blocks") or []) for x in s["suggestions"]}
    blocks_q = {q["id"]: list(q.get("blocks") or []) for q in QUESTIONS["questions"]}

    def downstream(root, seen=None):
        seen = seen or set()
        total = set()
        frontier = [root]
        while frontier:
            cur = frontier.pop()
            for nxt in blocks_sg.get(cur, []) + blocks_q.get(cur, []):
                if nxt not in total:
                    total.add(nxt)
                    if nxt not in seen and nxt != root:
                        seen.add(nxt)
                        frontier.append(nxt)
        return total

    # Rows already answered are excluded, with the exclusion counted on the page: a "start here"
    # list that still shows a closed question is worse than no list, because it re-asks the owner
    # for something the repository now holds (this pass answered Q-01 and Q-02 the same way).
    answered_q = {k for k, v in qinfo.items() if v.get("state") in ("known", "answered")}
    done_sg = {x["id"] for x in s["suggestions"]
               if x.get("current_state") in ("complete", "superseded")}
    set_aside = len(answered_q) + len(done_sg)
    triage = []
    for sid, lst in blocks_q.items():
        if lst and sid not in answered_q:
            free = downstream(sid)
            qrow = qinfo.get(sid, {})
            triage.append((len(free), sid, qrow.get("question", ""), "questions.html#" + sid.lower(),
                           ", ".join(lst)))
    for sg in order:
        if blocks_sg.get(sg["id"]) and sg["id"] not in done_sg:
            free = downstream(sg["id"])
            triage.append((len(free), sg["id"], sg["title"], "suggestions.html#" + sg["id"].lower(),
                           ", ".join(sorted(set(blocks_sg[sg["id"]]) - {sg["id"]}))))
    triage.sort(key=lambda x: (-x[0], x[1]))
    triage_rows = "".join(
        f'<tr><td class="num"><a href="{href}">{e(nid)}</a></td>'
        f'<td>{e(txt)}</td><td class="num">{n}</td>'
        f'<td class="small">{e(frees)} <a class="src" href="{REPO_BLOB}data/suggestions.json" '
        f'target="_blank" rel="noopener" title="the register carrying these blocker edges">data ↗</a> '
        f'<a class="src" href="flagged.html">caveats ↗</a></td></tr>'
        for n, nid, txt, href, frees in triage[:6])

    implemented = log.get("implemented") or []
    if implemented:
        implemented_html = ('<div class="tablewrap"><table><caption>Executed under the standing rule — '
            'not owner decisions</caption><thead><tr><th>Date</th><th>Row</th><th>Path</th>'
            '<th>What was done</th><th>Why the rule allowed it</th></tr></thead><tbody>' + "".join(
              f'<tr><td>{e(str(x.get("date", "")))}</td>'
              f'<td class="num"><a href="suggestions.html#{e(str(x.get("id", "")).lower())}">{e(x.get("id", ""))}</a></td>'
              f'<td class="num">{e(str(x.get("path", "")))}</td>'
              f'<td class="small">{e(str(x.get("what", "")))} <a class="src" href="{REPO_BLOB}data/decision-log.json">Dated action record ↗</a></td>'
              f'<td class="small">{e(str(x.get("why_allowed", "")))}</td></tr>'
              for x in implemented) + '</tbody></table></div>'
            + f'<p class="tiny muted">{e(str(log.get("implemented_note", "")).strip())}</p>')
    else:
        implemented_html = ('<p class="small muted">Nothing yet. A default that a pass executes must be '
                            'recorded here on the same commit, or the rule is unverifiable.</p>')
    updates = log.get("execution_updates") or []
    updates_html = "".join(f'<div class="callout note"><strong>{e(u["date"])} · {e(u["session"])}</strong><p>{e(u["what"])}</p><p class="tiny">'+ ' '.join(f'<a href="{e(path)}">Evidence</a>' for path in u['evidence'])+'</p></div>' for u in updates)
    implemented_html = updates_html + '<details><summary>Dated historical execution records</summary><p class="small muted">Past-tense records from earlier builds. The current Suggestions state takes precedence; this history is not a production-deployment or account-approval claim.</p>' + implemented_html + '</details>'
    steps = "".join(f"<li>{e(x)}</li>" for x in log.get("how_to_return_a_choice", []))
    auto_in_order = [sg for sg in order if computed[sg["id"]][2] == "auto"]
    queue = "".join(
        f'<li><a href="suggestions.html#{e(sg["id"].lower())}">{e(sg["id"])}</a> — '
        f'path {e(computed[sg["id"]][0])} · {e(sg["title"])}'
        f'<div class="tiny muted">priority {sg["impact"] * sg["confidence"]} · effort '
        f'{e(str(sg.get("effort", "")))} · touches: {e(sg.get("area", ""))}</div></li>'
        for sg in auto_in_order)
    policy = log.get("policy") or {}

    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Owner decision log</p>
<h1>Decision drafts, current states and action history</h1>
<p class="lede">The suggestion queue runs to {len(order)} entries, and a queue nobody closes is a
backlog. This page is the closing mechanism: one picker per suggestion, the default that applies if
nobody answers, and an export that turns picks into the file the next agent pass reads. The rule is
computed from the same registers the suggestions live in, so the page cannot promise a default its
own data does not support.</p>

<div class="callout info">
  <strong>The standing rule.</strong>
  <p class="small">{e(policy.get("text", ""))}</p>
  <p class="small"><strong>What silence never authorises.</strong> {e(policy.get("scope_limit", ""))}</p>
  <p class="tiny muted" style="margin-bottom:0">{e(policy.get("rule_applied", ""))}</p>
</div>

<div class="grid grid-4">
  <div class="stat"><div class="n">{len(order)}</div><div class="l">Suggestions on the queue</div><div class="h"><a href="suggestions.html">Read them →</a></div></div>
  <div class="stat ok"><div class="n">{n_auto}</div><div class="l">Carry a default a pass may implement</div><div class="h">reversible · low risk · unblocked</div></div>
  <div class="stat warn"><div class="n">{n_hold}</div><div class="l">Evidence / deployment gate</div><div class="h"><a href="questions.html">Open questions →</a></div></div>
  <div class="stat brand"><div class="n">{len(recorded)}</div><div class="l">Owner decisions in the register</div><div class="h">data/decision-log.json</div></div>
</div>

<h2>Start here — computed from the registers&rsquo; own blocker fields</h2>
<p class="small muted">Not a curated list: each row&rsquo;s score is the transitive size of the
<code>blocks</code> arrays in <code>data/suggestions.json</code> and <code>data/questions.json</code>,
so it moves when the registers move. This is SG-26 path A, implemented under the standing rule and
recorded in <code>implemented</code> below.</p>
<p class="tiny muted">{set_aside} row(s) are excluded because they are closed in the registers — a
question already answered or a suggestion marked done. The answer, not just the removal, is on the
linked page; if a row below disappears next pass it is because someone settled it, not because the
list was retyped.</p>
<div class="tablewrap">
<table>
  <caption>The rows that free the most other rows</caption>
  <thead><tr><th>Row</th><th>What is being asked</th><th>Rows it frees</th><th>Directly unblocks</th></tr></thead>
  <tbody>{triage_rows}</tbody>
</table>
</div>

<h2>How a choice becomes work</h2>
<ol class="small">{steps}</ol>

<h2>The register</h2>
<p class="small muted">Read the default column before the picker: it is what happens if you do
nothing. Priority is the scoring this register carries — judgement, not measurement. The evidence
column is the fact.</p>
<div class="tablewrap">
<table>
  <caption>Every suggestion, its default, and what it waits on</caption>
  <thead><tr><th>#</th><th>Suggestion</th><th>Path it recommends</th><th>If nobody answers</th>
  <th>State</th><th>Evidence</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>
</div>

<h2>Pick a path</h2>
<p class="small muted">Choices are stored in this browser (localStorage) so the page remembers
between visits, and nothing leaves the page until you press copy or download. The <em>default</em>
tag marks the path this register would take if you said nothing — picking it explicitly still matters,
because a recorded choice outranks a default and carries a reason.</p>
<noscript><p class="callout note">Decision drafting/export needs JavaScript. The full current-state table and the source JSON remain readable; nothing is submitted from this page.</p></noscript><div class="decision-actions" data-js-required hidden>
  <span id="decision-counter" class="tiny muted">0 of {len(order)} picked in this browser</span>
  <button type="button" class="btn" data-decision-action="download">Download decision-log.json</button>
  <button type="button" class="btn btn-ghost" data-decision-action="copy">Copy decision record</button>
  <button type="button" class="btn btn-ghost" data-decision-action="clear">Clear this browser&rsquo;s picks</button>
</div>
<div class="decision-picker" id="decision-picker" data-js-required hidden>
{"".join(fields)}
</div>
<pre class="decision-out" id="decision-output" hidden></pre>

<h2>What is recorded in the repository</h2>
{rec_tbl}
<p class="tiny muted">{e((log.get("choices_note") or "").strip())}</p>
<p class="tiny muted">{e(str(policy.get("recording", "")).strip())}</p>

<h2>What a pass already implemented under this rule</h2>
{implemented_html}

<h2>For the next agent pass</h2>
<p class="small muted">In this order, one commit per row, each with the evidence that justifies it.
{n_auto} defaults is a queue, not a big-bang release: a pass that lands a dozen page changes in one
commit cannot say which one broke a page, and this site&rsquo;s own rule is that a change has to be
checkable on its own.</p>
<ol class="small">{queue}</ol>
<p class="small">Read <code>data/decision-log.json</code> first: a recorded choice outranks the
default in this table, and a row with neither is still open. Implementing a default means the change
and its evidence in one commit, then a row appended to <code>choices</code> naming the session, the
path and the date, so the next reader sees that the default was executed rather than merely
available. Nothing here authorises spending, credential changes, account actions, a price or star
rating, a compliance posture, or any product fact the flag register holds open.</p>
<p class="small"><a href="suggestions.html">Suggestions queue</a> ·
<a href="questions.html">Open questions</a> ·
<a href="requirements.html">Requirements and status</a> ·
<a href="flagged.html">Flagged for review</a></p>
"""
    return layout("decision-log.html", "Owner decision log", body, active="decision-log.html",
                  description="Every suggestion on the queue with the path it recommends, the default that stands if the owner says nothing, and a picker that records a chosen path as a file the next agent pass can implement.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Owner decision log", page_url("decision-log.html")),
    ])]
              )


def page_suggestions_alt():
    rows = []
    for sid, area, text, basis, basis_src, options, effort in SUGGESTIONS_ALT:
        basis_html = (src_links(basis_src) + " " if basis_src else "") + (
            "" if basis_src else f'<a href="{REPO_BLOB}build.py">Original editorial proposal</a> ')
        rows.append(
            f"""<tr>
          <td><strong>{e(sid)}</strong><div class="tiny muted">{e(area)}</div></td>
          <td>{e(text)}</td>
          <td class="small">{e(basis)}<div class="tiny">{basis_html}</div></td>
          <td class="small">{e(options)}</td>
          <td class="small">{e(effort)}</td>
          <td class="small">☐ A &nbsp; ☐ B &nbsp; ☐ C<div class="tiny muted">Reply with the ID and letter</div></td>
        </tr>""")
    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Marketing directions (parallel pass)</p>
<h1>Suggestions: choose the path before anything changes</h1>
<p class="lede">{len(SUGGESTIONS_ALT)} suggestions to improve the site's design, trust, content and measurement. <strong>None of them has been implemented.</strong> Each one lists the options. Pick an option for each ID you want, and only then will the change be made.</p>

<div class="callout warn"><strong>How to decide.</strong> Each row has a basis. Where the basis is an official Amazon or FTC source, the link goes to that source. Where the row is a design opinion, it says so and points to <a href="flagged.html">Flagged for review</a>. The options run from the current state (A) to the recommended path.</div>

<div class="tablewrap">
<table>
  <caption>Suggestions and the options for each</caption>
  <thead><tr><th>ID</th><th>Suggestion</th><th>Basis and source</th><th>Options</th><th>Effort</th><th>Your choice</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>
</div>

<h2>Information needed before some of these can be decided</h2>
<p class="small">Several suggestions depend on a fact not yet known. Those facts are listed, with the way to find each one, on the <a href="decision-gate.html">Questions and information gaps</a> page.</p>
"""
    body = '<div class="callout warn"><strong>Historical parallel proposal — 15 November 2026.</strong> The text below is preserved history, not today’s account facts, location assumptions, current states or policy interpretation. IDs belong to that original proposal. Use <a href="questions.html">current questions/answers</a> and <a href="suggestions.html">current suggestion states</a> instead.</div>' + '<details><summary>Read the original parallel proposal</summary>' + body + '</details>'
    return layout("marketing-directions.html", "Marketing directions (parallel pass)", body,
                  active="marketing-directions.html",
                  description="Site, design, trust, content and measurement suggestions, with options for the owner to choose before any change is made.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Marketing directions (parallel pass)", page_url("marketing-directions.html")),
    ])]
              )


def page_questions_alt():
    rows = []
    for qid, q, known, missing, how, unblocks, srcs in QUESTIONS_ALT:
        rows.append(
            f"""<tr>
          <td><strong>{e(qid)}</strong></td>
          <td>{e(q)}</td>
          <td class="small">{e(known)}<div class="tiny">{src_links(srcs) if srcs else f'<a href="{REPO_BLOB}build.py">Original editorial question</a>'}</div></td>
          <td class="small">{e(missing)}</td>
          <td class="small">{e(how)}</td>
          <td class="small">{e(unblocks)}</td>
        </tr>""")
    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Questions and information gaps (parallel pass)</p>
<h1>The parallel register: fourteen questions with their known facts, gaps and next steps</h1>
<p class="lede">{len(QUESTIONS_ALT)} questions. For each one: what the repository already holds (with its official source), what is still missing, how to find the missing fact, and which decision it unblocks. Nothing in the <em>missing</em> column has been filled in with an estimate.</p>

<div class="callout warn"><strong>Read this first.</strong> Q-01 and Q-06 decide most of the other choices: which products the links really point to, and which Amazon store the site can promote. Answer those two before the product pages are extended.</div>

<div class="tablewrap">
<table>
  <caption>Questions, known facts, gaps and how to close each gap</caption>
  <thead><tr><th>ID</th><th>Question</th><th>Known (sourced)</th><th>Missing</th><th>How to find out</th><th>Unblocks</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>
</div>

<p class="small" style="margin-top:1.5rem">Related: <a href="marketing-directions.html">Marketing directions (parallel pass)</a> · <a href="questions.html">Questions and gaps (this register's main pass)</a> · <a href="flagged.html">Flagged for review</a> · <a href="executive-summary.html">Executive summary</a></p>
"""
    body = '<div class="callout warn"><strong>Historical parallel proposal — 15 November 2026.</strong> The text below is preserved history, not today’s account facts, location assumptions, current states or policy interpretation. IDs belong to that original proposal. Use <a href="questions.html">current questions/answers</a> and <a href="suggestions.html">current suggestion states</a> instead.</div>' + '<details><summary>Read the original parallel proposal</summary>' + body + '</details>'
    return layout("decision-gate.html", "Questions and information gaps", body, active="decision-gate.html",
                  description="Questions that must be answered before decisions, what is known with sources, what is missing, and how to find it.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Questions and gaps (parallel pass)", page_url("decision-gate.html")),
    ])]
              )


# --------------------------------------------------------------------------- #
# Content and traffic plan (added 2026-11-15, arena/63a2c638)
#
# The brief asks for the article and traffic thinking that would make this a real
# marketing site. This page is where that lives, and the discipline applied to the
# data is applied to the plan: a proposal is labelled as a proposal, no search volume
# is invented, and every row names the official source the finished article must cite.
# The two channels that Amazon's policies forbid are listed next to the real ones so
# the plan cannot be read as if they had not been considered.
# --------------------------------------------------------------------------- #

TOPICS = load("topics.json")
# Added 2026-11-16 by arena/ad8105b3: the brief's first requirement was the only one
# with no first-class page. The 19-row register existed only inside the s2/ annex.
REQUIREMENTS = load("requirements.json")

_TOPIC_STATUS = {
    "published": ("ok", "Published"),
    "proposed": ("warn", "Proposed — not written"),
}


def page_topics():
    t = TOPICS
    items = t["topics"]
    prod_by_slug = {p["slug"]: p for p in PRODUCT_LIST}

    # Guard: a topic may not cite a product that does not exist, and may not point at a
    # question that is not in the register. A plan with a dangling reference is a plan
    # nobody can execute.
    _qids = {q["id"] for q in QUESTIONS["questions"]}
    for it in items:
        for slug in it.get("serves") or []:
            if slug not in prod_by_slug:
                raise SystemExit(f"BUILD FAILED — topic {it['id']} serves unknown product {slug}")
        for qid in it.get("blocked_by") or []:
            if qid not in _qids:
                raise SystemExit(f"BUILD FAILED — topic {it['id']} blocked by unknown question {qid}")

    rows = []
    for it in items:
        cls, label = _TOPIC_STATUS.get(it["status"], ("warn", it["status"]))
        serves = ", ".join(prod_by_slug[s]["short_name"] for s in (it.get("serves") or [])) \
            or '<span class="muted">Site-level — serves no single product</span>'
        # The plan table keeps two citation links per row for compactness. When the brief
        # requires more, an explicit "+N more in the brief" link points at the row's detail
        # card, so a reader can never mistake two links for the full citation set (found
        # 2026-11-17 by arena/0cf55ef3: TP-21's row showed 2 of its 3 required sources).
        cites = " ".join(
            f'<a href="{e(c["url"])}" target="_blank" rel="noopener">{e(c["label"][:40])} ↗</a>'
            for c in it["must_cite"][:2]
        )
        _more = len(it["must_cite"]) - 2
        if _more > 0:
            cites += f' <a class="tiny muted" href="#{e(it["id"].lower())}">+{_more} more in the brief ↓</a>'
        cites += f' <a href="{REPO_BLOB}data/topics.json">Editorial topic record</a>'
        title_html = e(it["title"])
        if it["status"] == "published" and it.get("published_as"):
            title_html = f'<a href="../{e(it["published_as"])}">{title_html}</a>'
        rows.append(
            f'<tr><td class="num"><a href="#{e(it["id"].lower())}">{e(it["id"])}</a></td>'
            f'<td><strong>{title_html}</strong>'
            f'<div class="small muted">{e(it["hook"])}</div></td>'
            f'<td class="small">{e(it["intent"])}</td>'
            f'<td class="small">{serves}</td>'
            f'<td><span class="pill {cls}">{e(label)}</span></td>'
            f'<td class="small">{cites}</td></tr>'
        )

    # Detail cards. The plan table links every row to #tp-NN, so every row must have a
    # target: before this pass the block below was skipped for published topics, which
    # left 8 of 14 in-page links on this page pointing at nothing. Published topics get
    # a short card that links the article; unwritten ones get the full brief.
    cards = []
    for it in items:
        if it["status"] == "published":
            cites = " ".join(
                f'<a class="src-link" href="{e(c["url"])}" target="_blank" rel="noopener">{e(c["label"])} ↗</a>'
                for c in it["must_cite"]
            )
            cards.append(f"""
<article class="sug" id="{e(it['id'].lower())}">
  <div class="sug-head">
    <div>
      <div class="tiny muted">{e(it['id'])} · {e(it['intent'])} · published</div>
      <h3><a href="../{e(it['published_as'])}">{e(it['title'])}</a></h3>
    </div>
  </div>
  <p><strong>The angle.</strong> {e(it['angle'])}</p>
  <p class="small"><a href="../{e(it['published_as'])}">Read the article →</a></p>
  <div class="evidence"><strong>Must cite.</strong> {cites}</div>
</article>""")
            continue
        cites = " ".join(
            f'<a class="src-link" href="{e(c["url"])}" target="_blank" rel="noopener">{e(c["label"])} ↗</a>'
            for c in it["must_cite"]
        )
        blocked = it.get("blocked_by") or []
        blocked_html = " ".join(
            f'<a class="src" href="questions.html#{e(q.lower())}">{e(q)}</a>' for q in blocked
        ) or '<span class="tiny muted">Nothing blocks this one.</span>'
        caveat = (f'<p class="small"><strong>Caution.</strong> {e(it["caveat"])}</p>'
                  if it.get("caveat") else "")
        cards.append(f"""
<article class="sug" id="{e(it['id'].lower())}">
  <div class="sug-head">
    <div>
      <div class="tiny muted">{e(it['id'])} · {e(it['intent'])} · not yet written</div>
      <h3>{e(it['title'])}</h3>
    </div>
  </div>
  <p><strong>The angle.</strong> {e(it['angle'])}</p>
  <p class="small"><strong>Why it could earn traffic.</strong> {e(it['why_it_could_earn_traffic'])}</p>
{('  ' + caveat) if caveat else ''}  <div class="evidence"><strong>Must cite.</strong> {cites}</div>
  <p class="small"><strong>Blocked by:</strong> {blocked_html}</p>
</article>""")

    ch_rows = []
    for ch in t["channels"]:
        forbidden = ch["id"] in ("CH-2", "CH-5")
        verdict_cls = "bad" if forbidden else "ok"
        ch_rows.append(
            f'<tr><td class="num">{e(ch["id"])}</td>'
            f'<td><strong>{e(ch["channel"])}</strong></td>'
            f'<td><span class="pill {verdict_cls}">{e("Forbidden by policy" if forbidden else "Available")}</span></td>'
            f'<td class="small">{e(ch["verdict"])}</td>'
            f'<td class="small">{e(ch["constraint"])}</td>'
            f'<td class="small"><a href="{e(ch["source"]["url"])}" target="_blank" rel="noopener">'
            f'{e(ch["source"]["label"])} ↗</a> <a href="{REPO_BLOB}data/topics.json">Channel proposal</a></td></tr>'
        )

    disclaimer = "".join(f"<li>{e(x)}</li>" for x in t["disclaimer"])
    n_new = sum(1 for x in items if x["status"] == "proposed")
    n_pub = sum(1 for x in items if x["status"] == "published")

    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Content and traffic plan</p>
<h1>What to write next, and how it is allowed to be promoted</h1><div class="callout note"><strong>Current operating plan, not an unattended publisher.</strong><p>{e(PUBLICATION["cadence"]["rhythm"])}</p><p>{e(PUBLICATION["cadence"]["kill_rule"])}</p></div>
<p class="lede">{n_pub + n_new} topics for this product set — {n_pub} already published and {n_new} not yet
written — and {len(TOPICS.get('channels', []))} distribution channels, two of which Amazon's policies close off entirely. The
topics are chosen for one reason: each one is answerable from an official manufacturer page or an
owner's manual, so none of them requires a claim this site cannot support.</p>

<div class="callout note">
  <strong>Read this before treating anything below as a fact.</strong>
  <ul class="tight">{disclaimer}</ul>
</div>

<h2>The plan</h2>
<div class="tablewrap"><table>
  <thead><tr><th>#</th><th>Topic</th><th>Intent</th><th>Serves</th><th>State</th><th>Must cite</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table></div>
<p class="tiny muted">{e(t['demand_note'])}</p>

<h2>The brief behind each topic</h2>
<p class="small muted">Every row in the plan table links here. Published topics link straight to the
article; unwritten ones carry the angle, the reason it could earn traffic, the sources any finished
version must cite, and what blocks it.</p>
<p class="small">{''.join(cards) if cards else '<span class="muted">No topics are on the plan yet.</span>'}</p>

<h2>How any of it may be promoted</h2>
<div class="tablewrap"><table>
  <thead><tr><th>#</th><th>Channel</th><th>Status</th><th>Verdict</th><th>The constraint</th><th>Source</th></tr></thead>
  <tbody>{''.join(ch_rows)}</tbody>
</table></div>
<p class="tiny muted">{e(t['channels_note'])}</p>

<div class="callout note" style="margin-top:1.5rem">
  <strong>Where this fits.</strong>
  The topics above are the editorial half of <a href="suggestions.html#sg-09">SG-09</a> and
  <a href="suggestions.html#sg-04">SG-04</a>; the channel constraints are the same clauses recorded on the
  <a href="compliance.html">Compliance</a> page. Choosing a path through the work starts on the
  <a href="suggestions.html">Suggestions</a> page, under <em>Choose a path</em>.
</div>
"""
    return layout("topics.html", "Content and traffic plan", body, active="topics.html",
                  description="Article topics for three air fryers, each tied to an official source, and the "
                              "distribution channels Amazon's policies permit or forbid.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Content and traffic plan", page_url("topics.html")),
    ])]
                  )



# --------------------------------------------------------------------------- #
# requirements register (arena/ad8105b3, 2026-11-16)
# --------------------------------------------------------------------------- #

REQ_STATUS = {
    "delivered":     ("ok",   "Delivered"),
    "partial":       ("warn", "Partial"),
    "blocked":       ("bad",  "Blocked"),
    "not_delivered": ("warn", "Not built"),
}

REQ_GROUPS = [
    ("A", "What the brief asked for"),
    ("B", "The site, its design and its traffic"),
    ("C", "Product research and analysis"),
    ("D", "Content generation and editorial voice"),
    ("E", "Publishing, affiliate links and measurement"),
    ("F", "Compliance and disclosure"),
    ("G", "The automation platform"),
]


def check_requirement_tokens(pages):
    """Build guard: no count token may survive into a published page.

    Companion to req_interp(): the register may type {n_spec_rows} instead of a number, and if a
    token is misspelled or a row is rendered by a path that forgot to interpolate, the page would
    otherwise ship with braces in the prose. Added 2026-11-16 (arena/ba29c641).
    """
    problems = []
    for rel, html_text in pages.items():
        if not rel.endswith(".html"):
            continue
        for m in re.finditer(r"\{(n_[a-z_]+|sg_[a-z_]+)\}", html_text):
            problems.append(f"{rel}: unresolved count token {m.group(0)}")
    return problems


def check_requirement_paths(generated=()):
    """Build guard: every path a requirement row claims must exist in this repository.

    This guard exists because the defect it prevents was live. The s2 annex's own
    register row R-01 cited `data/requirements.json` and a "Requirements page"; neither
    existed at those locations, and no gate noticed because a register is prose. A
    status table that points at files which are not there is worse than no table: it
    reads as verification and is none. Requirement paths must also be files, not
    repository directories: the canonical GitHub Pages output has no directory index,
    so a root-relative `platform/` or `platform/tests/` reader link is a published 404.
    Failing the build makes both kinds of claim checkable.
    """
    generated = set(generated)

    def exists(rel):
        # A path is real if it is on disk, or if this same build is generating it.
        return rel in generated or (ROOT / rel).exists()

    problems = []
    for req in REQUIREMENTS["requirements"]:
        for path in req.get("where") or []:
            if path.endswith("/") or (ROOT / path).is_dir():
                problems.append(f"{req['id']}: implementation path must name a file, not a directory: {path}")
            elif not exists(path):
                problems.append(f"{req['id']}: file does not exist: {path}")
        for ev in req.get("evidence") or []:
            url = ev["url"]
            if url.startswith("http") or url.startswith("#"):
                continue
            if url.endswith("/") or (ROOT / url).is_dir():
                problems.append(f"{req['id']}: evidence link must name a file, not a directory: {url}")
            elif not exists(url):
                problems.append(f"{req['id']}: evidence link does not exist: {url}")
        for sid in req.get("sources") or []:
            if sid not in SRC_BY_ID:
                problems.append(f"{req['id']}: cites unregistered source {sid}")
        if not (req.get("where") or req.get("evidence") or req.get("sources")) and not req.get("why"):
            problems.append(f"{req['id']}: no implementation path, no evidence and no stated gap")
    return problems


def req_counts():
    """Counts for the requirements register, computed from the data at build time.

    Written 2026-11-16 (arena/ba29c641) because the register's own rule promises exactly this —
    'counts are computed from the rows at build time rather than typed, so this page cannot claim
    a total the register does not contain' — while eight of its rows typed their numbers into
    prose. Four of those had already gone stale (46 spec rows, 21 suggestions, 20 questions, a
    37-URL sitemap) in the two days between the register being written and this pass, which is the
    drift the rule exists to prevent. A row may now write {n_spec_rows}; an unknown token fails the
    build, and a token left unresolved fails it too (check_requirement_tokens).
    """
    tests = 0
    tp = ROOT / "platform" / "tests" / "test_platform.py"
    if tp.exists():
        tests = len(re.findall(r"^\s+def test_", tp.read_text(encoding="utf-8"), re.M))
    briefings = sorted(p.name for p in ROOT.glob("EXECUTIVE*SUMMARY*.md"))
    stale = [n for n in briefings if n != "EXECUTIVE-SUMMARY.md"]
    return {
        "n_req_rows": len(REQUIREMENTS["requirements"]),
        "n_spec_rows": sum(len(p["specs"]) for p in PRODUCT_LIST),
        "n_verified_rows": sum(1 for p in PRODUCT_LIST for s in p["specs"] if s["value"] is not None),
        "n_blank_rows": sum(1 for p in PRODUCT_LIST for s in p["specs"] if s["value"] is None),
        "n_products": len(PRODUCT_LIST),
        # arena/58cbaaa2 (2026-11-17): counts read from the registers, for prose that must not drift.
        "n_submitted_links": str(N_SUBMITTED_LINKS),
        "n_intent_confirmed": str(sum(1 for r in SUBMITTED_ROWS if r.get("intended_asin"))),
        "n_link_tests_passed": str(sum(1 for r in SUBMITTED_ROWS if r.get("associates_link_test_passed"))),
        "n_sources": len(SOURCES["sources"]),
        "n_suggestions": len(SUGGESTIONS["suggestions"]),
        "n_sg_last": max(int(x["id"].split("-")[1]) for x in SUGGESTIONS["suggestions"]),
        "n_questions": len(QUESTIONS["questions"]),
        "n_articles": len(ARTICLES["articles"]),
        "n_topics": len(TOPICS["topics"]),
        # topics that are specified but not yet written (status "proposed")
        "n_topics_minus_articles": sum(1 for t in TOPICS["topics"] if t.get("status") != "published"),
        "n_banned": len(BANNED_PHRASES),
        "n_banned_distinct": len({p.lower() for p in BANNED_PHRASES}),
        "n_guards": len(re.findall(r"^def check_", open(__file__).read(), re.M)),
        "n_tests": tests,
        "n_stale_briefings": len(stale),
    }


def req_interp(text):
    """Substitute the computed counts into a register string; unknown tokens are a build failure."""
    counts = req_counts()
    for tok, val in counts.items():
        if "{" + tok + "}" in text:
            text = text.replace("{" + tok + "}", str(val))
    left = re.findall(r"\{[a-z_]+\}", text)
    if left:
        raise SystemExit(f"BUILD FAILED — unknown count token(s) in the requirements register: {left}")
    return text


def page_requirements():
    reqs = REQUIREMENTS["requirements"]
    legend = REQUIREMENTS["status_legend"]
    counts = {}
    for r in reqs:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    stat_html = "".join(
        f'<div class="stat {"ok" if REQ_STATUS[k][0]=="ok" else ("bad" if REQ_STATUS[k][0]=="bad" else "warn")}">'
        f'<div class="n">{counts.get(k,0)}</div>'
        f'<div class="l">{e(REQ_STATUS[k][1])}</div></div>'
        for k in ("delivered", "partial", "blocked", "not_delivered")
    )

    def row(r):
        cls, label = REQ_STATUS[r["status"]]
        where = "<br>".join(
            f'<a class="src-link" href="{e(pth)}" target="_blank" rel="noopener">'
            f'<code>{e(pth)}</code> ↗</a>'
            f'<a class="src" href="{REPO_BLOB}{e(pth)}" target="_blank" rel="noopener" '
            f'title="repository file — this is the evidence that the path exists">repo</a>'
            for pth in (r.get("where") or [])
        ) or '<span class="muted">—</span>'
        ev = " ".join(
            f'<a class="src-link" href="{e(x["url"])}" target="_blank" rel="noopener">'
            f'{e(req_interp(x["label"]))} ↗</a>'
            for x in (r.get("evidence") or [])
        )
        srcs = src_links(r.get("sources") or []) if (r.get("sources") or []) else ""
        evidence_cell = (ev + ((" " + srcs) if srcs else "")) or '<span class="muted">—</span>'
        if not (r.get("where") or []):
            # No implementation path: cite the register row itself, which is where the
            # gap is recorded, so the row still carries a checkable link.
            evidence_cell = (evidence_cell + " " if ev or srcs else "") + (
                f'<a class="src" href="{REPO_BLOB}data/requirements.json" target="_blank" '
                f'rel="noopener" title="the register row that records this gap">repo</a>')
        return (
            f'<tr id="{e(r["id"].lower())}"><td class="num">' 
            f'<a href="#{e(r["id"].lower())}">{e(r["id"])}</a></td>'
            f'<td class="small"><strong>{e(req_interp(r["requirement"]))}</strong>'
            f'<div class="tiny muted" style="margin-top:.35rem">{e(req_interp(r["clause"]))}</div></td>'
            f'<td><span class="pill {cls}">{e(label)}</span></td>'
            f'<td class="small">{e(req_interp(r["why"]))}</td>'
            f'<td class="small">{where}</td>'
            f'<td class="small">{evidence_cell}</td></tr>'
        )

    sections = []
    for gid, gname in REQ_GROUPS:
        rows = [r for r in reqs if r["id"].startswith(gid + "-")]
        if not rows:
            continue
        sub = {}
        for r in rows:
            sub[r["status"]] = sub.get(r["status"], 0) + 1
        summary = " · ".join(f"{REQ_STATUS[k][1]} {sub.get(k,0)}" for k in
                             ("delivered", "partial", "blocked", "not_delivered") if sub.get(k))
        sections.append(
            f'<h2 id="group-{gid.lower()}">{gid}. {e(gname)}</h2>'
            f'<p class="tiny muted">{len(rows)} requirements · {e(summary)}</p>'
            '<div class="tablewrap"><table><thead><tr><th>#</th><th>Requirement</th><th>Status</th>'
            '<th>What that status means here</th><th>Where it lives</th><th>Evidence</th>'
            f'</tr></thead><tbody>{"".join(row(r) for r in rows)}</tbody></table></div>'
        )

    legend_html = "".join(
        f'<li><span class="pill {REQ_STATUS[k][0]}">{e(REQ_STATUS[k][1])}</span> {e(legend[k])}</li>'
        for k in ("delivered", "partial", "blocked", "not_delivered")
    )

    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Requirements and status</p>
<h1>Every requirement in the brief, and what this repository actually does about it</h1>
<p class="lede">{e(REQUIREMENTS['purpose'])}</p>

<div class="grid grid-4" style="margin:1.25rem 0 1.75rem">{stat_html}</div>

<div class="callout note">
  <strong>How to read a status.</strong>
  <ul class="tight">{legend_html}</ul>
  <p class="tiny" style="margin-bottom:0">{e(REQUIREMENTS['rule'])}</p>
</div>

<div class="callout warn">
  <strong>The three counts that matter, and why they are not zero.</strong>
  <p><strong>Blocked</strong> rows are not unfinished work. Each one depends on a fact that exists only
  inside Amazon's own systems — the Associate tag, the approval status of the account, per-ASIN commission
  categories, customer reviews, conversion reports. No amount of work in this repository closes them, and
  the alternative to leaving them open is inventing a number, which is the one thing the brief forbids
  more plainly than any other.</p>
  <p style="margin-bottom:0"><strong>Not built</strong> rows are the opposite: buildable today, not built
  yet. There are {counts.get('not_delivered',0)} of them, and traffic outcomes remain unproven — see
  <a href="topics.html">the content and traffic plan</a> for the channels Amazon's policies leave open.</p>
</div>

{''.join(sections)}

<h2>What this register does not claim</h2>
<p class="small">A status here is a statement about this repository, not about the affiliate business.
This site has three documented appliance guides, two unconfirmed thermometer notes, no verified campaign data and no confirmed active affiliate tag, so no row on this
page should be read as evidence of revenue potential. The rows that would answer that —
<a href="requirements.html#c-07">C-07</a>, <a href="requirements.html#c-08">C-08</a>,
<a href="requirements.html#e-04">E-04</a> — are exactly the ones blocked.</p>
<p class="small">Where a requirement could not be met, the row names the missing input and the clause that
makes it missing rather than softening the status. Unverified values and unresolved conflicts are collected
on <a href="flagged.html">Flagged for review</a>, and the questions that a decision would have to answer
first are on <a href="questions.html">Questions and gaps</a>.</p>

<div class="callout note">
  <strong>Where this fits.</strong>
  This page is the coverage view. <a href="suggestions.html">Suggestions</a> is the queue of changes with
  options and a recommended path; <a href="design-prompt.html">Design prompt pack</a> is the status view of
  what has already shipped; <a href="questions.html">Questions and gaps</a> is what must be answered before
  a decision. The s2 annex carries its own, earlier, 19-row register at
  <a href="s2/pages/requirements.html">s2/pages/requirements.html</a> — it is not edited by this page, and
  the two disagreements between them are recorded as flags <a href="flagged.html#f59">F59</a> and
  <a href="flagged.html#f60">F60</a>.
</div>
"""
    return layout("requirements.html", "Requirements and status", body, active="requirements.html",
                  description="Every requirement in the brief, one row each, with the status judged against what "
                              "this repository and this site actually do, the path that implements it and the "
                              "official source that settles it.",
                  jsonld_blocks=[breadcrumbs_jsonld([
                      ("Home", SITE_URL + "/"),
                      ("Requirements and status", page_url("requirements.html")),
                  ])])


def page_404():
    body = """
<p class="crumbs">Not found</p>
<h1>That page is not here</h1>
<p class="lede">The link may be stale, or the page may not exist. Everything published is reachable from the dashboard.</p>
<div class="grid grid-2">
  <div class="card"><h3 style="margin-top:0">Products</h3>
    <ul class="tight small">
      <li><a href="products/chefman-6qt-dual-basket.html">Chefman 6 Qt Dual Basket</a></li>
      <li><a href="products/emeril-26qt-french-door.html">Emeril 26 QT French Door</a></li>
      <li><a href="products/chefman-8qt-turbofry.html">Chefman 8 Qt TurboFry</a></li>
      <li><a href="compare.html">Comparison matrix</a></li>
    </ul>
  </div>
  <div class="card"><h3 style="margin-top:0">Research</h3>
    <ul class="tight small">
      <li><a href="data.html">Full dataset</a></li>
      <li><a href="compliance.html">Compliance</a></li>
      <li><a href="flagged.html">Flagged for review</a></li>
      <li><a href="executive-summary.html">Executive summary</a></li>
    </ul>
  </div>
</div>
"""
    return layout("404.html", "Page not found", body,
                  description="That page does not exist on this site. Start from the air-fryer buying guide, the articles, or the flagged-for-review register.",
                  jsonld_blocks=[breadcrumbs_jsonld([
                      ("Home", SITE_URL + "/"),
                      ("Page not found", page_url("404.html")),
                  ])])


# --------------------------------------------------------------------------- #
# Articles — the editorial layer asked for in the brief ("catchy, trendy articles
# and topics related to the product we are promoting").
#
# Discipline: data/articles.json holds prose whose factual numbers are written as
# {{value}} placeholders and a per-section list of source ids. A section may not be
# rendered unless every one of its source ids resolves in data/sources.json; the
# article may not be rendered unless every placeholder in it appears verbatim in a
# value published in data/products.json. That makes "the article invented a number"
# a build failure rather than a proofreading task.
# --------------------------------------------------------------------------- #

ARTICLES = load("articles.json")
# The article cluster map (added 2026-11-17, session 79743fd2). The article set
# had no map: "Read next" on every page showed the same three articles because
# it was the first three rows of the file, and internal linking was whatever a
# reader happened to click. A small site earns a commercial query by owning one
# cluster completely rather than by publishing one page per idea, so the
# articles are grouped by the question a reader actually arrives with, each
# group has a named hub, and the build draws the links.
CLUSTERS = load("clusters.json")
CLUSTER_BY_ID = {c["id"]: c for c in CLUSTERS["clusters"]}
ARTICLE_BY_SLUG = {a["slug"]: a for a in ARTICLES["articles"]}

_PRODUCT_VALUES = None


def _published_values():
    """Every value string this build publishes for a product, for placeholder checks."""
    global _PRODUCT_VALUES
    if _PRODUCT_VALUES is not None:
        return _PRODUCT_VALUES
    vals = set()
    for p in PRODUCT_LIST:
        for spec in p["specs"]:
            vals.add(spec["value"])
            vals.add(spec["label"])
        for k in ("name", "short_name", "brand", "category"):
            if p.get(k):
                vals.add(p[k])
        for k in ("asin", "model_number", "sibling_sku"):
            f = p.get(k)
            if isinstance(f, dict) and f.get("v"):
                vals.add(f["v"])
            elif isinstance(f, str):
                vals.add(f)
    # Values the dataset states inside an evidence/note string are still published;
    # scan those too so a quoted dimension can be cited without re-typing it.
    for p in PRODUCT_LIST:
        for k, v in p.items():
            if isinstance(v, str):
                vals.add(v)
        for spec in p["specs"]:
            if spec.get("note"):
                vals.add(spec["note"])
    _PRODUCT_VALUES = vals
    return vals


PLACEHOLDER_RE = re.compile(r"\{\{(.+?)\}\}")


def _split_placeholder(raw):
    """Split a placeholder into (published value, prose form or None).

    Two forms are accepted:

        {{Two 3-quart baskets}}            the published value, verbatim
        {{Two 3-quart baskets::two 3-quart baskets}}
                                            the published value with a prose form

    The prose form exists because the published values are display labels
    ("Two 3-quart baskets"), and a display label spliced into the middle of a
    sentence reads like machine output: "splits a cavity into Two 3-quart
    baskets". The prose form may differ from the published value ONLY in
    letter case - check_articles() enforces that, so a prose form can never
    introduce a number, a unit or a fact that the dataset does not publish.
    """
    if "::" in raw:
        pub, prose = raw.split("::", 1)
        return pub.strip(), prose.strip()
    return raw.strip(), None


def _render_placeholder(raw):
    pub, prose = _split_placeholder(raw)
    if prose is None:
        return f'<code class="specval">{pub}</code>'
    # The prose form is what the reader sees; the published value stays
    # recoverable on hover, so nothing is lost by rendering the lower-case form.
    return f'<code class="specval" title="Published value: {pub}">{prose}</code>'


def _article_text(paras):
    """Render {{value}} placeholders as <code>, escaping everything else."""
    out = []
    for para in paras:
        # **bold** -> <strong>
        chunk = e(para)
        chunk = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", chunk)
        chunk = PLACEHOLDER_RE.sub(lambda m: _render_placeholder(m.group(1)), chunk)
        out.append(f"<p>{chunk}</p>")
    return "\n".join(out)


def _article_placeholders(article):
    found = []
    for sec in article["sections"]:
        for para in sec["paras"]:
            found.extend(PLACEHOLDER_RE.findall(para))
    return found


# A value that opens with a capital letter is correct in some positions and
# wrong in others. "Sync Finish" is right at the start of a sentence and wrong
# after "as". A published value may therefore be written in mid-sentence only
# when it is an identifier (a model number or an ASIN) or when it carries an
# explicit prose form. These are the positions where a capital is right.
_CAP_OK_BEFORE = set(':"\'(—–')
_IDENTIFIER_RE = re.compile(r"^[A-Z0-9][A-Z0-9\-/]*(\s|$)")


def _is_identifier(value):
    """True for model numbers and ASINs: the first token has no lower-case letter."""
    first = value.split()[0] if value.split() else value
    return not any(ch.islower() for ch in first)


def check_article_splices(article):
    """Reject a published value spliced into a sentence where its capital is wrong.

    This is the guard behind flag F55. A display label such as "Two 3-quart
    baskets" is a correct answer to "what is the capacity?" and a broken
    sentence inside "divided into Two 3-quart baskets". The defect is not
    visible in a data table, which is why it survived nine earlier passes:
    it only shows up when the page is read as prose.
    """
    problems = []
    for sec in article["sections"]:
        for para in sec["paras"]:
            for m in PLACEHOLDER_RE.finditer(para):
                before = para[:m.start()]
                raw = m.group(1)
                pub, prose = _split_placeholder(raw)
                shown = prose if prose is not None else pub
                if not shown[:1].isupper():
                    continue
                if _is_identifier(shown):
                    continue
                # First non-space token of the paragraph: a capital is correct.
                if before.strip() == "":
                    continue
                # A colon, quote, bracket or dash introduces the value, so a
                # capital is correct there too.
                stripped = before.rstrip()
                if stripped and stripped[-1] in _CAP_OK_BEFORE:
                    continue
                problems.append(
                    f"{article['slug']} §'{sec['h']}': the value {pub!r} is spliced into "
                    f"mid-sentence in a position where its capital is wrong "
                    f"(rendered as {shown!r}). Use a prose form "
                    f"({{{{{pub}::lower-case}}}}) or rewrite the sentence."
                )
    return problems


def check_articles():
    """Fail the build if an article cites an unregistered source or invents a number."""
    problems = []
    values = _published_values()
    for a in ARTICLES["articles"]:
        if not a.get("modified_at"):
            problems.append(f"{a['slug']}: missing evidence-backed editorial modification date")
        for check in a.get("source_checks", []):
            if not check.get("on") or not check.get("ids"):
                problems.append(f"{a['slug']}: incomplete scoped source-check record")
            for sid in check.get("ids", []):
                if sid not in SRC_BY_ID:
                    problems.append(f"{a['slug']}: source check cites unknown {sid}")
        for sec in a["sections"]:
            if not sec.get("cite"):
                problems.append(f"{a['slug']} §'{sec['h']}' has no source citation")
            for sid in sec.get("cite", []):
                if sid not in SRC_BY_ID:
                    problems.append(f"{a['slug']} §'{sec['h']}' cites unregistered source {sid}")
        for ph in _article_placeholders(a):
            pub, prose = _split_placeholder(ph)
            if pub not in values:
                problems.append(
                    f"{a['slug']} states '{pub}' which is not a value published in data/products.json")
            if prose is None:
                continue
            if prose.lower() != pub.lower():
                problems.append(
                    f"{a['slug']} prose form '{prose}' differs from the published value '{pub}' "
                    f"by more than letter case. A prose form may only re-case the published value; "
                    f"it may not add or change a number, a unit or a fact.")
        problems.extend(check_article_splices(a))
    return problems


def check_article_pages(rendered):
    """Every rendered article must carry the Associates sentence, say that nothing was tested, and
    contain no Amazon price or star-rating pattern (Program Policies 2(b) and 6(t))."""
    problems = []
    for rel, text in rendered.items():
        if not rel.startswith("articles/") or not rel.endswith(".html"):
            continue
        if DISCLOSURE not in text.split('<main')[0]:
            problems.append(f"{rel}: disclosure must appear below the masthead and before the main content")
        low = text.lower()
        if "tested" not in low and "hands-on" not in low:
            problems.append(f"{rel}: no statement that nothing was tested")
        for bad in ("out of 5 stars", "a-icon-alt", "Amazon price:"):
            if bad in text:
                problems.append(f"{rel}: prohibited Amazon price/rating pattern {bad!r}")
    return problems


def check_no_orphan_pages(pages):
    """Build guard: every HTML file the root build owns must be one it generates (F74).

    Found 2026-11-16 (arena/5ac82b1d): `articles/sync-finish-two-buttons.html` was
    live on Pages and on disk while absent from data/articles.json, the sitemap and
    every index — a second, unregistered version of topic TP-09. It arrived in a
    merge whose register entry was dropped as a duplicate while its HTML file was
    not, and no existing check compared the directories on disk against the page
    set the build actually emits (verify.py checks links *from* files that exist;
    it cannot see a file nothing links to). The guard fails the build if any .html
    file in the root build's owned directories is not in `pages`, so a stale or
    unregistered page cannot ship again. Annex directories (s2/, site/, research/,
    docs/, dashboard/, session-*/, annex-*/) are other sessions' builds and are
    deliberately not scanned.
    """
    owned_dirs = ("articles", "products", "guides", "categories")
    expected = set(pages)
    problems = []
    for d in owned_dirs:
        p = ROOT / d
        if not p.is_dir():
            continue
        for f in sorted(p.glob("*.html")):
            rel = f"{d}/{f.name}"
            if rel not in expected:
                problems.append(
                    f"{rel}: exists on disk but this build does not generate it "
                    "(not registered in data/ — stale or unregistered page)")
    for f in sorted(ROOT.glob("*.html")):
        if f.name not in expected:
            problems.append(
                f"{f.name}: exists on disk but this build does not generate it "
                "(not registered in data/ — stale or unregistered page)")
    return problems


# Banned-phrase guard for the editorial layer (2026-11-15, arena/792c279e).
# The brief's complaint is that the site read "like AI slop". A house style rule that
# nobody can enforce is a wish, so it is a build failure. The list is deliberately
# short and specific: phrases that appear in machine-written marketing copy far more
# often than in writing a person would publish, plus the hype verbs that make a
# statement unfalsifiable. It is checked against the article sources in
# data/articles.json, not against the rendered HTML, so the guard cannot be satisfied
# by escaping.
BANNED_PHRASES = [
    "in today's fast-paced world", "in today\u2019s fast-paced world", "elevate your",
    "unlock the power", "game-changer", "game changer", "revolutionize", "revolutionise",
    "seamless experience", "take it to the next level", "look no further",
    "dive into", "delve into", "in the ever-evolving", "ever-evolving landscape",
    "whether you're a", "whether you\u2019re a", "nestled in the heart",
    "boasts a", "unleash", "cutting-edge", "state-of-the-art", "must-have",
    "indulge in", "tantalizing", "cullinary", "culinary journey",
]


def check_decision_data():
    """Build guard for data/decision.json (2026-11-15, arena/792c279e).

    The decision pages publish arithmetic on official rates, so the rates must still be the
    ones on the official table and every per-sale figure must be the arithmetic it claims to
    be. A stale example is worse than no example: it looks authoritative and is wrong.
    """
    problems = []
    official = {r["rate"]: r for r in COMPLIANCE.get("commission_table", [])}
    for row in DECISION["commission"]["rows"]:
        rate = row["rate"]
        cat = row["label"].split(" (")[0].strip()
        # The table groups categories in one row, e.g. "Physical Books, Kitchen,
        # Automotive" -> 4.50%. Match the category *inside* a grouped row, not the whole
        # row string, so a rename on either side fails loudly instead of passing silently.
        match = [r for r in COMPLIANCE.get("commission_table", [])
                 if r["category"].strip() == cat
                 or cat in [x.strip() for x in r["category"].split(",")]]
        if not match:
            problems.append(f"decision.json rate row {cat!r} is not a row on the official table")
            continue
        if match[0]["rate"].strip() != rate:
            problems.append(f"decision.json says {cat} is {rate}, the table says {match[0]['rate']}")
    for ex in DECISION["commission"]["per_sale_examples"]:
        try:
            price = float(ex["list_price"].replace("$", "").replace(",", ""))
        except ValueError:
            problems.append(f"unparseable list price {ex['list_price']!r}")
            continue
        for pct_key, rate in (("at_4_5", 0.045), ("at_4_0", 0.040)):
            expect = round(price * rate + 1e-9, 2)
            got = float(ex[pct_key].replace("$", ""))
            if abs(expect - got) > 0.005:
                problems.append(f"{ex['product']}: {pct_key} is {ex[pct_key]}, "
                                f"{price} x {rate:.2%} = ${expect:.2f}")
    # every channel and metric must name its prerequisites rather than imply readiness
    for c in DECISION["traffic"]["channels"]:
        if not c.get("requirements"):
            problems.append(f"traffic channel {c['id']} lists no requirements")
        if not c.get("status"):
            problems.append(f"traffic channel {c['id']} has no status")
    return problems


def check_article_voice():
    problems = []
    for a in ARTICLES["articles"]:
        blob = " ".join(
            [a.get("title", ""), a.get("standfirst", "")]
            + [p for sec in a["sections"] for p in sec["paras"]]
        ).lower()
        for phrase in BANNED_PHRASES:
            if phrase in blob:
                problems.append(f"{a['slug']}: banned stock phrase {phrase!r}")
        # A first-person plural claim of experience is the same failure as a test claim.
        for claim in ("we tested", "we tried", "we used it", "after weeks of use",
                      "we've been using", "our testers"):
            if claim in blob:
                problems.append(f"{a['slug']}: experience claim {claim!r} with no testing")
    return problems


def article_body(article, prefix="../"):
    parts = []
    last = len(article["sections"]) - 1
    for i, sec in enumerate(article["sections"]):
        # EV-03 (guide_completed) is measured at the last heading, not at the
        # footer: reaching the end of the article is the event, and the footer
        # is visible on a page the reader scrolled past without reading.
        mark = ""
        parts.append(f"<h2{mark}>{e(sec['h'])}</h2>")
        parts.append(_article_text(sec["paras"]))
        if sec.get("cite"):
            parts.append(
                f'<p class="tiny muted">Sources for this section: {src_links(sec["cite"])}</p>')
    body = "\n".join(parts)
    return body


_NUM_WORDS = {1: "One piece", 2: "Two pieces", 3: "Three pieces", 4: "Four pieces", 5: "Five pieces",
              6: "Six pieces", 7: "Seven pieces", 8: "Eight pieces", 9: "Nine pieces", 10: "Ten pieces"}


def _n_words(n):
    """Spell a small count so the hub's lede cannot go stale when an article is added."""
    return _NUM_WORDS.get(n, f"{n} pieces")


def cluster_of(article):
    """The cluster an article belongs to, or None when it has none."""
    cid = article.get("cluster")
    return CLUSTER_BY_ID.get(cid)


def cluster_href(hub, prefix="../"):
    """A link to a cluster's hub page, relative to wherever the reader is."""
    return prefix + hub


def cluster_siblings(article):
    """The other articles in the same cluster, in the order the map lists them."""
    c = cluster_of(article)
    if not c:
        return []
    return [ARTICLE_BY_SLUG[s] for s in c["members"]
            if s in ARTICLE_BY_SLUG and s != article["slug"]]


def _article_card(a, prefix="../"):
    """One article card. Shared by the articles index and the cluster map, so a
    card looks the same wherever a reader meets it."""
    prods = ""
    if a["products"]:
        links = []
        for slug in a["products"]:
            p = next((x for x in PRODUCT_LIST if x["slug"] == slug), None)
            if p:
                links.append(f'<a href="{prefix}products/{slug}.html">{e(p["short_name"])}</a>')
        if links:
            prods = ('<p class="tiny muted" style="margin:.4rem 0 0">About: '
                     + " \u00b7 ".join(links) + "</p>")
    # An article that serves no single product (site-level pieces) leaves prods
    # empty; emitting the slot anyway would publish a trailing-whitespace line.
    prods_html = (prods + "\n") if prods else ""
    cluster = cluster_of(a)
    badge = ""
    if cluster:
        badge = (f'<p class="tiny muted" style="margin:.5rem 0 0">In the cluster: '
                 f'<a href="{prefix}clusters.html#{e(cluster["id"])}">{e(cluster["label"])}</a></p>\n')
    return f"""<article class="card article-card">
  <span class="kicker">{e(a["kicker"])}</span>
  <a class="cardtitle" href="{prefix}articles/{a["slug"]}.html">{e(a["title"])}</a>
  <span class="cardtext">{e(a["standfirst"])}</span>
  <span class="tiny muted">{e(a["kind"])} \u00b7 {a["reading_minutes"]} min read</span>
{badge}{prods_html}</article>"""


def page_articles_index():
    groups=[]
    names={'choose':'Choose an appliance','spec':'Understand the specifications','live':'Life after dinner','trust':'How this publication works'}
    for cluster in CLUSTERS['clusters']:
        members=[slug for slug in cluster['members'] if slug in ARTICLE_BY_SLUG]
        groups.append(f'<section class="cluster-group" id="{e(cluster["id"])}"><div class="cluster-head"><h2>{e(names.get(cluster["id"],cluster["label"]))}</h2><p>{e(cluster["summary"])}</p></div><div class="grid grid-2">'+''.join(article_teaser(slug,'../') for slug in members)+'</div></section>')
    body=f"""<p class="crumbs"><a href="../index.html">Home</a> / Buying guides</p><p class="section-eyebrow">Read before you make room</p><h1>A better question before you buy.</h1><p class="lede">Practical guides to formats, capacity, counter space and care. Written from official product pages and manuals, with the limits left in—not tested recommendations.</p>{publication_byline('../')}
<nav class="buyer-toc" aria-label="Guide topics">{''.join(f'<a href="#{e(c["id"])}">{e(names.get(c["id"],c["label"]))}</a>' for c in CLUSTERS['clusters'])}</nav>
<p class="small"><a href="../guides/buying-guide-air-fryers.html">Not sure where to start? Take the short buying route →</a></p>
{''.join(groups)}
<p class="section-note">These topics are editorial choices, not a search-volume or popularity ranking. Source dates stay on each guide. <a href="../clusters.html">See the cluster map</a> · <a href="../about.html">Our research and authorship</a>.</p>{reader_capture('../')}"""
    return layout('articles/index.html','Kitchen buying guides',body,active='articles/index.html',description='Useful questions before buying an air fryer: formats, capacity, counter space, care and model checks. Source-led guides without hands-on claims.',jsonld_blocks=[breadcrumbs_jsonld([('Home',SITE_BASE),('Buying guides',page_url('articles/index.html'))])])


def page_clusters():
    """The cluster map: one page that shows how the article set fits together.

    Added 2026-11-17 (session 79743fd2). Twenty-one articles with no map is
    twenty-one pages a search engine has to work out the relationship between,
    and a reader who wants a second answer to the question they just read has
    to go back to a flat list. The map gives both of them the shape.
    """
    sections = []
    for c in CLUSTERS["clusters"]:
        members = [ARTICLE_BY_SLUG[s] for s in c["members"] if s in ARTICLE_BY_SLUG]
        rows = ""
        for a in members:
            # The official documents this article rests on, so the row states
            # where its facts came from rather than only what it says.
            cites = []
            for sec in a.get("sections") or []:
                for sid in sec.get("cite") or []:
                    if sid not in cites:
                        cites.append(sid)
            cite_cell = src_links(cites) if cites else (
                '<span class="tiny muted">site-level piece: no product specification is quoted</span>')
            rows += (
                f'<tr><td class="small"><a href="articles/{e(a["slug"])}.html">{e(a["title"])}</a>'
                f'<div class="tiny muted">{e(a["kind"])} \u00b7 {a["reading_minutes"]} min read</div></td>'
                f'<td class="small">{e(a["standfirst"])}</td>'
                f'<td class="small muted">{e(a["target_query"])}</td>'
                f'<td class="small">{cite_cell}</td></tr>')
        sections.append(f"""
<section id="{e(c["id"])}" class="cluster-group">
  <div class="cluster-head">
    <p class="kicker">{e(c["intent"])}</p>
    <h2>{e(c["label"])}</h2>
    <p class="small muted">{e(c["summary"])}</p>
    <p class="tiny">Hub: <a href="{e(c["hub"])}">{e(c["hub_label"])}</a></p>
  </div>
  <div class="tablewrap">
  <table>
    <caption>Articles in this cluster, with the query each one targets</caption>
    <thead><tr><th style="width:26%">Article</th><th style="width:36%">What it answers</th><th style="width:18%">Query it targets</th><th style="width:20%">Official sources it rests on</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  </div>
</section>""")

    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Article clusters</p>
<h1>Four clusters, {len(ARTICLES["articles"])} articles</h1>
<p class="lede">A small site earns a query by answering it completely rather than by publishing
one page per idea. This is the shape of the set: the four questions a shopper brings here, the
hub that answers each one, and the articles underneath it. Every link on this page is generated
from <code>data/clusters.json</code>, so the map and the articles cannot drift apart.</p>

<div class="callout info">
  <strong>Why this is not a taxonomy exercise</strong>
  <p class="small">The clusters are not tags. Each one is a question a reader arrives with, and
  each article is filed under the question it actually answers. A piece about cleaning sits with
  ownership questions, not with the format comparisons, even when it mentions the same three
  products.</p>
</div>

{"".join(sections)}

<div class="callout warn">
  <strong>What a cluster is not</strong>
  <p class="small">It is not a claim that these pages rank, or will rank, or that the search terms
  in the last column have any volume behind them. The query each article targets is the
  question it is written to answer, recorded so the set can be judged for overlap. No traffic
  figure appears here because none has been measured.</p>
</div>

<p class="small" style="margin-top:1.5rem"><a class="btn btn-ghost" href="articles/index.html">All articles →</a> <a class="btn btn-ghost" href="guides/buying-guide-air-fryers.html">Buying guide →</a> <a class="btn btn-ghost" href="compare.html">Comparison matrix →</a></p>
"""
    url = page_url("clusters.html")
    ld = [
        {
            "@type": "CollectionPage",
            "@id": url + "#webpage",
            "url": url,
            "name": "Article clusters",
            "isPartOf": {"@id": SITE_URL + "/#website"},
            "about": {"@id": SITE_URL + "/#organization"},
            "inLanguage": "en-US",
        },
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Article clusters", url),
        ]),
    ]
    return layout("clusters.html", "Article clusters", body, active="articles/index.html",
                  description="The article set filed under the four questions a shopper actually arrives with: which machine to buy, what the numbers mean, what it is like to live with, and whether the page can be trusted.",
                  jsonld_blocks=ld)


def page_article(a):
    prods = ""
    if a["products"]:
        items = []
        for slug in a["products"]:
            p = next((x for x in PRODUCT_LIST if x["slug"] == slug), None)
            if p:
                items.append(
                    f'<li><a href="../products/{slug}.html">{e(p["name"])}</a> '
                    f'<span class="tiny muted">— {e(p["category"])}</span></li>')
        if items:
            prods = ('<div class="callout"><strong>Products covered</strong>'
                     f'<ul class="tight small" style="margin:.4rem 0 0">{"".join(items)}</ul></div>')
    # "Read next" used to be the first three rows of data/articles.json minus
    # this article, so every article on the site pointed at the same three
    # articles. It is now the rest of this article's own cluster - the group
    # that answers the same question - with the cluster hub above it.
    _cluster = cluster_of(a)
    _sibs = cluster_siblings(a)
    rel_html = ""
    if _sibs:
        rel_html = "".join(
            f'<li><a href="../articles/{x["slug"]}.html">{e(x["title"])}</a> '
            f'<span class="tiny muted">— {e(x["kind"])}</span></li>' for x in _sibs)
    cluster_badge = ""
    if _cluster:
        cluster_badge = (
            f'<span class="pill pill-info">Cluster: <a href="../clusters.html#'
            f'{e(_cluster["id"])}">{e(_cluster["label"])}</a></span>')
    cluster_hub_html = ""
    if _cluster:
        cluster_hub_html = (
            f'<p class="small" style="margin:.6rem 0 0">Hub for this cluster: '
            f'<a href="../{e(_cluster["hub"])}">{e(_cluster["hub_label"])}</a></p>')
    if rel_html:
        read_next_html = (
            "<h2>More in this cluster</h2>" + cluster_hub_html + "\n"
            + '<ul class="tight small">' + rel_html + "</ul>")
    elif _cluster:
        read_next_html = (
            "<h2>More in this cluster</h2>" + cluster_hub_html + "\n"
            + '<p class="small">This is the only article filed under this cluster so far.</p>')
    else:
        read_next_html = (
            "<h2>Read next</h2>"
            + '<ul class="tight small">'
            + "".join(
                f'<li><a href="../articles/{x["slug"]}.html">{e(x["title"])}</a> '
                f'<span class="tiny muted">— {e(x["kind"])}</span></li>'
                for x in ARTICLES["articles"][:3] if x["slug"] != a["slug"])
            + "</ul>")
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / <a href="../articles/index.html">Articles</a> / {e(a['kind'])}</p>
<header class="article-head">
  <p class="kicker">{e(a['kicker'])}</p>
  <h1>{e(a['title'])}</h1>
  <p class="lede">{e(a['standfirst'])}</p>
  <div class="article-meta">
    <span>By <a href="../about.html">Zone1 Kitchen</a> · AI-assisted, document-based writing</span><span aria-hidden="true">·</span>
    <span>{a['reading_minutes']} min read</span><span aria-hidden="true">·</span>
    <span>Sources checked {e(a.get('sources_read') or ARTICLES['accessed'])}</span><span aria-hidden="true">·</span>
    <span>Edited <time datetime="{e(a['modified_at'])}">{e(a['modified_at'][:10])}</time>; first-publication timestamp is not established.</span>
    <span class="pill pill-info">Documentation-based — no hands-on testing</span>
    {cluster_badge}
  </div>
</header>

<p class="reading-note">No appliance was tested for this guide. Specifications are attributed to their documents; editorial guidance is not a cooking result. <a href="../about.html">How we research</a>.</p>
<div class="article-prose">
{article_body(a)}
</div>

<p class="small" style="margin-top:1.5rem"><em>{e(a['closing_note'])}</em></p>

{read_next_html}

<p class="small" style="margin-top:1.5rem"><a class="btn btn-ghost" href="../articles/index.html">← All articles</a> <a class="btn btn-ghost" href="../flagged.html">What is unresolved →</a></p>
"""
    # --- 2026-11-15 (arena/792c279e): reader-facing polish on the editorial layer.
    # A share row that works with no third-party script, prev/next navigation so a reader
    # who lands deep can keep reading, and Article structured data assembled only from
    # fields already in data/articles.json. No author identity is invented; the publisher
    # is the site.
    _arts = ARTICLES["articles"]
    _idx = [x["slug"] for x in _arts].index(a["slug"])
    _prev = _arts[_idx - 1] if _idx > 0 else _arts[-1]
    _next = _arts[(_idx + 1) % len(_arts)]
    _site = "https://kanlerxz87-cyber.github.io/Zone1/"
    _url = f"{_site}articles/{a['slug']}.html"
    share = f"""
<div class="share">
  <span class="label">Share</span>
  <a href="https://x.com/intent/post?text={quote_plus(a['title'])}&amp;url={quote_plus(_url)}" target="_blank" rel="noopener">X / Twitter</a>
  <a href="https://www.linkedin.com/sharing/share-offsite/?url={quote_plus(_url)}" target="_blank" rel="noopener">LinkedIn</a>
  <a href="https://www.facebook.com/sharer/sharer.php?u={quote_plus(_url)}" target="_blank" rel="noopener">Facebook</a>
  <a href="mailto:?subject={quote_plus(a['title'])}&amp;body={quote_plus(_url)}">Email</a>
  <button type="button" class="copylink" data-js-required hidden data-link="{e(_url)}">Copy link</button>
</div>
<div class="article-nav">
  <a class="card tight" href="{e(_prev['slug'])}.html"><span class="tiny muted">Previous</span><br><strong>{e(_prev['title'])}</strong></a>
  <a class="card tight" href="{e(_next['slug'])}.html"><span class="tiny muted">Next</span><br><strong>{e(_next['title'])}</strong></a>
</div>"""
    body = body + share
    # Structured data for this article is emitted once, in <head>, by layout(), with
    # the same @context and @graph wrapper as every other block. (arena/792c279e
    # appended a second, body-level Article block; merged here into one so a crawler
    # never sees two conflicting Article nodes for the same URL.)
    aurl = page_url(f"articles/{a['slug']}.html")
    ld = [
        article_jsonld(a, aurl),
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Articles", page_url("articles/index.html")),
            (a["title"], aurl),
        ]),
    ]
    return layout(f"articles/{a['slug']}.html", a["title"], body,
                  active="articles/index.html", description=a["standfirst"],
                  og_type="article", jsonld_blocks=ld,
                  og_image_alt=f"{a['title']} — {SITE_NAME}")



# --------------------------------------------------------------------------- #
# 2026-11-15 (arena/792c279e-zone1, T20): the decision-facing pages.
#
# picks.html      — the commercial front door: three products, three jobs, one
#                   decision rule, and the caveat that governs every link.
# decisions.html  — niche, traffic and measurement: the strategy material the
#                   brief asks for, with assumptions labelled and quantities
#                   either sourced or left as owner inputs.
# handover.html   — the five things only the account holder can do, each with a
#                   time estimate and the flags it closes.
#
# Every number on these pages comes from data/decision.json, which follows the
# same rule as the rest of the dataset: a value is either quoted from a
# registered official source or labelled as an assumption.
# --------------------------------------------------------------------------- #

FLAG_BY_ID = {}


def _decision_rows():
    return DECISION["commission"]["rows"]


def page_picks():
    products = {p["slug"]:p for p in PRODUCT_LIST}
    body = f"""<p class="crumbs"><a href="index.html">Home</a> / Format finder</p><p class="section-eyebrow">A practical starting point</p><h1>Match the format to the way you cook.</h1><p class="lede">No price leaderboard or claimed bestseller. Compare the three formats, then check the exact model and the space it needs.</p>{publication_byline()}
<div class="grid grid-3" id="format-guides">{''.join(product_card(products[r['slug']]) for r in PUBLICATION['products'])}</div><p class="section-note">Candidate product records; the intended listing behind each submitted link is still unconfirmed. <a href="product-intent.html">See the separate record</a>.</p>
<div class="publication-compare-cta"><div><h2>Still choosing?</h2><p>Take the capacity and countertop checklist with you.</p></div><a class="btn" href="guides/buying-guide-air-fryers.html">Read the buying guide →</a></div>"""
    return layout('picks.html','Air-fryer format finder',body,active='categories/kitchen-appliances.html',description='Three documented air-fryer formats and the practical trade-offs to check, with no overall ranking or invented test result.',jsonld_blocks=[breadcrumbs_jsonld([('Home',SITE_BASE),('Format finder',page_url('picks.html'))])])

# ── arena/58cbaaa2 (2026-11-17): the submitted-link register, read by the build ──────────────
# main's own F79/F77 class of defect, one step up: a count typed into narrative rather than read from
# the register. The register holds five rows; the category lede still said "the three supplied links"
# in the present tense. Read the number, do not retype it, and let the build check the sentence.
LINK_RECHECK_DATE = "2026-11-17"
SUBMITTED_ROWS = PRODUCT_INTENT["rows"]
N_SUBMITTED_LINKS = len(SUBMITTED_ROWS)
_LINK_NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                   "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


def _num_word(n):
    """A count as a word, for prose. The data stays numeric; the sentence reads like English.

    check_submitted_link_count() matches both spellings, so this can never become a way to hide a
    number from the guard.
    """
    return {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
            8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}.get(n, str(n))


def _submitted_links_in_category():
    """Submitted links the register files in this site's own category.

    "In category" is read off the register's own `observed_listing_category`, the field the
    consolidation pass added for exactly this purpose — not from a guess about the product.
    """
    # Pass 14 (arena/9b3365c7-zone1, 2026-11-19): this used to test
    # `"air fryer" in observed_listing_category.lower()`. That field holds a prose judgement
    # ("Air-fryer product title on observed landing page; …"), the hyphen never matched, and
    # categories/kitchen-appliances.html published "0 of the five links … landed on air fryer
    # listings" while three of them did (first reported by the still-open PR #144). The count
    # now reads `observed_browse_path` — the breadcrumb Amazon itself printed on the landing
    # page, recorded with its read date — and a row without one fails the build instead of
    # being silently counted as "not in category".
    n = 0
    for r in SUBMITTED_ROWS:
        crumb = r.get("observed_browse_path")
        if not crumb:
            raise SystemExit(f"BUILD FAILED — {r.get('id')} has no observed_browse_path; "
                             "the category count cannot be computed from a guess")
        leaf = crumb.split("›")[-1].strip().lower()
        if leaf == "air fryers":
            n += 1
    return n


def page_intent():
    """Operator-only link-intent record and campaign ledger."""
    intent = PRODUCT_INTENT
    ledger = CAMPAIGN_LEDGER
    dash = '<span class="tiny muted">Not confirmed</span>'

    def brand_check_rows():
        """Rows for the brand-catalogue comparison, read from the register so a new row needs no template edit."""
        out = []
        for row in SUBMITTED_ROWS:
            current = row.get("latest_catalogue_observation")
            if current:
                out.append(f'<tr><td>{e(row["id"])}</td><td class="small">{e(row.get("observed_title", ""))}</td>'
                           f'<td class="small">{e(current["observation"])}</td><td>Intended model/ASIN unconfirmed; no performance/certification specification adopted.</td>'
                           f'<td>{src_link(current["source"])} {src_links(row["observed_source_ids"])}</td></tr>')
                continue
            bc = row.get("brand_catalogue_check")
            if not bc:
                continue
            out.append(
                f'<tr><td>{e(row["id"])}</td>'
                f'<td class="small">{e(bc.get("listing_says") or "")}</td>'
                f'<td class="small">{e(bc.get("brand_page_says") or "")}</td>'
                f'<td class="small">{e(bc.get("verdict") or "")}'
                f'<div class="tiny muted"><a href="flagged.html#f80">F80</a> — why this closes nothing</div></td>'
                f'<td class="small">{src_links(bc.get("source_ids") or [])}</td></tr>')
        return "".join(out)

    body_rows = []
    for row in intent["rows"]:
        intended = e(row["intended_asin"]) if row["intended_asin"] else dash
        official = e(row["official_listing_url"]) if row["official_listing_url"] else dash
        confirmed = (f'{e(row["confirmation_date"])} {src_links([row["confirmation_source"]])}'
                     if row["confirmation_date"] and row["confirmation_source"] else dash)
        target = e(row["observed_redirect_target"]) if row.get("observed_redirect_target") else "No observation recorded"
        observed_date = e(row["observed_on"]) if row.get("observed_on") else "—"
        sources = src_links(row.get("observed_source_ids") or []) or dash
        body_rows.append(
            f'<tr><td>{e(row["id"])}</td>'
            f'<td><code>{e(row["supplied_link"])}</code></td>'
            f'<td>{e(row["observed_listing_category"])}</td>'
            f'<td>{intended}</td><td>{official}</td><td>{confirmed}</td>'
            f'<td><code>{target}</code><br><span class="tiny muted">observed {observed_date}; destination only</span></td>'
            f'<td>{e(row.get("observed_title") or "No title observation recorded")}</td>'
            f'<td>{sources}<br><span class="tiny muted">{e(row["note"])}</span></td></tr>'
        )
    ledger_cols = "".join(f"<th>{e(column)}</th>" for column in ledger["columns"])
    ledger_rows = "".join(
        "<tr>" + "".join(f"<td>{e(row.get(column, ''))}</td>" for column in ledger["columns"]) + "</tr>"
        for row in ledger["rows"]
    )
    ledger_empty = "" if ledger["rows"] else '<p class="small blank">No authorized report rows recorded.</p>'
    tag = intent["tracking_id_selected"]
    body = f"""
<section class="hero-lite">
  <p class="kicker">Owner workspace · product links and measurement</p>
  <h1>Link intent and campaign ledger</h1>
  <p class="lede">Observed redirect destinations and intended products are separate records. No intended ASIN or listing is filled in until the account holder confirms it. The campaign ledger stays empty until an authorized first-party report supplies real numbers.</p>
</section>

<div class="callout warn">
  <strong>Account and link status are not verified.</strong>
  The tracking ID below is user-provided, not confirmed as active or as the tag on any supplied link. No tracking test or order report has been run. Do not read an observed fallback page as the product the account holder meant to promote.
</div>

<div class="card">
  <h2 style="margin-top:0">Selected tracking ID</h2>
  <p><strong><code>{e(tag)}</code></strong> — {e(intent["tracking_id_status"])}</p>
  <p class="small">The brief calls for one enrolled-Associates link test <strong>per confirmed intended product</strong> before scaling. Once each intended listing is confirmed, test its Special Link and verify the click in Associates Central. Keep <code>associate_tag</code> blank until those account-only checks pass. Sources: {src_links(['S5', 'S6', 'S2'])}. Open flag: <a href="flagged.html#f76">F76</a>.</p>
</div>

<h2>Five supplied links: intended identity is unconfirmed</h2>
<p class="small">The five submitted URL strings, the observed destination/title for each, and any owner-confirmed intended listing are separate records. The observed pages are not evidence of intent. No conclusion is made here about whether a supplied short link is valid or compliant, or what its path token denotes. Intended fields stay blank until the account holder confirms each listing. Open flags: <a href="flagged.html#f77">F77</a>, <a href="flagged.html#f78">F78</a>, and <a href="flagged.html#f79">F79</a> (source-record correction).</p>
<div class="tablewrap">
<table>
  <caption>Five link records — each observation is dated separately; intended products not confirmed</caption>
  <thead><tr><th>Record</th><th>Supplied link</th><th>Observed page title suggests (not intended identity)</th><th>Intended ASIN</th><th>Official listing URL confirmed by operator</th><th>Confirmation date / source</th><th>Observed redirect target</th><th>Observed listing title</th><th>Evidence / note</th></tr></thead>
  <tbody>{"".join(body_rows)}</tbody>
</table>
</div>

<h2 id="campaign-ledger">Campaign ledger</h2>
<p class="small">No rows have been added. The ledger accepts timestamp, source report, channel, date range, eligible sessions, clicks and <em>reported</em> orders. It does not estimate conversion or revenue from click counts. The required fields and import gate are recorded in <a href="measurement.html">the measurement plan</a>. Sources for the program/reporting rules: {src_links(['S1', 'S2', 'S6'])}.</p>
<div class="tablewrap">
<table>
  <caption>Authorized report totals only ({len(ledger['rows'])} rows recorded)</caption>
  <thead><tr>{ledger_cols}</tr></thead>
  <tbody>{ledger_rows}</tbody>
</table>
</div>
{ledger_empty}
<h2>What the brands' own catalogues say about the two newest links</h2>
<p class="small">The two thermometer links were checked against official manufacturer catalogues on 19 November. Current catalogue selections do not confirm the intended Amazon listing. The <a href="categories/cooking-thermometers.html">reader shelf</a> therefore publishes link notes only, not a verified product specification or certification claim. Earlier catalogue snapshots remain in the data history (F80).</p>
<div class="tablewrap">
<table>
  <caption>Scoped catalogue observations, read 2026-11-19</caption>
  <thead><tr><th style="width:8%">Row</th><th style="width:24%">The listing says</th>
  <th style="width:34%">The brand's own page says</th><th style="width:22%">Verdict</th>
  <th style="width:12%">Source</th></tr></thead>
  <tbody>{brand_check_rows()}</tbody>
</table>
</div>

<div class="callout note">
  <strong>A correction to how this record argued its own case, dated 2026-11-17.</strong>
  <p class="small">Rows above and flags around them cite the absence of a visible <code>tag=</code> parameter on an
  observed landing URL beside their caution about attribution. Two official help nodes read on this date narrow what
  that can carry. Amazon states plainly that a tracking ID does not need to appear in the click-through URL for a
  sale to be credited, because the session is tagged on its side {src_links(['S41'])} — so a clean landing URL is a
  <em>null</em> observation, not a negative one, and it cannot be used as evidence about attribution in either
  direction. What stays unprovable from outside the account is the positive: that the selected ID is listed, and that
  a click through a published link appears under it. S41's sibling node names where that is read — the
  <strong>Tracking ID Summary Report</strong> — together with the screen that creates IDs and the limit of 100
  tracking IDs per account {src_links(['S42'])}, which is also what makes a per-channel sub-tag scheme a cheap option
  rather than an exotic one. The per-row <code>associates_link_test_*</code> fields are the right place for that
  result, and nothing on this page will accept a URL inspection as a substitute for it. Historical rows are left as
  written: they are dated records of what those passes observed, and the reasoning is corrected here instead of
  edited backwards.</p>
</div>

<p class="small"><a href="measurement.html">See the five event definitions, cadence and deployment gate →</a></p>
"""
    return layout("product-intent.html", "Product-link records and campaign ledger", body,
                  active="product-intent.html",
                  description="Owner record keeping supplied-link observations separate from intended listings, plus an empty campaign ledger for authorized report data.",
                  jsonld_blocks=[breadcrumbs_jsonld([
                      ("Home", SITE_BASE),
                      ("Product-link records and campaign ledger", page_url("product-intent.html")),
                  ])])


def page_measurement():
    plan = ANALYTICS_PLAN
    project_schema = repo_link("data/analytics-plan.json", "Project event schema")
    event_rows = []
    for event in plan["events"]:
        evidence = (src_links(["S6", "S2"]) if event["name"] == "affiliate_report_import" else project_schema)
        event_rows.append(
            f'<tr><td><code>{e(event["name"])}</code></td>'
            f'<td>{e(event["origin"])}</td>'
            f'<td class="small">{e(event["when"])}</td>'
            f'<td class="small">{e(", ".join(event["properties"]))}</td>'
            f'<td class="small">{e("Not active" if not plan["collection"]["enabled"] else "Enabled only after deployment gates")}</td>'
            f'<td>{evidence}</td></tr>'
        )
    cadence_rows = "".join(
        f'<tr><td><strong>{e(item["frequency"])}</strong></td>'
        f'<td class="small">{e(item["action"])}</td>'
        f'<td>{repo_link("data/analytics-plan.json", "Project cadence")}</td></tr>'
        for item in plan["cadence"]
    )
    gate_rows = [
        ("Runtime and route", "Not configured or verified. The repository's canonical origin is a GitHub Pages URL; no same-origin /api/analytics/events runtime is configured in this checkout. GitHub’s official documentation was read on 2026-11-19 and confirms Pages is static hosting.", src_links(["S38"])),
        ("Privacy and retention notice", "Not approved. Keep the client disabled until the actual deployment and visitor-facing notice are reviewed together.", src_links(["S2"])),
        ("Host and proxy logs", "Not reviewed. Before collection, verify whether the hosting platform, CDN or reverse proxy retains IP addresses, user agents, request URLs or access logs; set an approved retention policy.", repo_link("data/analytics-plan.json", "Privacy and deployment gate")),
        ("Event collector", "Reference implementation and tests are in analytics/collector.py and tests/test_analytics.py; not deployed or reachable from the published site.", repo_link("analytics/collector.py", "Reference collector")),
        ("Associates attribution", "Not tested. The selected tracking ID is user-provided and the Associates Central account is not accessible here.", src_links(["S5", "S6"])),
        ("Conversion reporting", "Blocked on an authorized Associates Central report. No conversion, order or revenue estimate is generated.", src_links(["S2", "S6"])),
    ]
    gates_html = "".join(
        f'<tr><td><strong>{e(name)}</strong></td><td class="small">{e(status)}</td><td>{sources}</td></tr>'
        for name, status, sources in gate_rows
    )
    # -- Sections from data/measurement.json (session 79743fd2): what actually ships
    # in this repository, the client-side event cards, the empty campaign ledger and
    # the prerequisites. The two event registers above and below were written by
    # different sessions; both are published and the mapping note keeps them honest.
    m = MEASUREMENT

    def ev_card(ev):
        nots = "".join(f'<li>{e(x)}</li>' for x in ev["explicitly_not_recorded"])
        recs = "".join(f'<li>{e(x)}</li>' for x in ev["records"])
        return f"""
<div class="card" style="margin:.7rem 0">
  <p class="section-eyebrow">{e(ev['id'])} \u00b7 <code>{e(ev['name'])}</code></p>
  <p class="small"><strong>Fires when:</strong> {e(ev['fires_when'])}</p>
  <div class="grid" style="grid-template-columns:1fr 1fr;gap:1rem">
    <div><p class="tiny muted" style="margin:0">Records</p><ul class="tight small">{recs}</ul></div>
    <div><p class="tiny muted" style="margin:0">Never records</p><ul class="tight small">{nots}</ul></div>
  </div>
  <p class="tiny muted" style="margin-bottom:0">{e(ev['note'])}</p>
</div>"""

    events = "".join(ev_card(ev) for ev in m["events"])
    why = "".join(f"<li>{e(x)}</li>" for x in m["why_nothing_is_sending"])
    priv = "".join(f"<li>{e(x)}</li>" for x in m["privacy_rules"])
    SRC_S2 = src_links(['S2'])
    pre = "".join(
        f'<tr><td class="num">{e(x["step"])}</td><td class="small">{e(x["owner_action"])}</td>'
        f'<td class="small">{e(x["blocks"])}</td><td class="small">{e(x["why"])} {SRC_S2}</td></tr>'
        for x in m["prerequisites"]
    )
    led = m["campaign_ledger"]
    impl = m.get("implementation") or {}
    REPO_BLOB = "https://github.com/kanlerxz87-cyber/Zone1/blob/main/"
    impl_where = {
        "client": REPO_BLOB + "assets/analytics.js",
        "switch": REPO_BLOB + "data/config.json",
        "endpoint_source": REPO_BLOB + "analytics/README.md",
        "guard": REPO_BLOB + "build.py",
        "verification": REPO_BLOB + "tests/test_analytics_contract.py",
        "what_is_not_shipped": REPO_BLOB + "data/measurement.json",
    }
    impl_rows = ""
    for k, v in impl.items():
        where = impl_where.get(k, REPO_BLOB)
        impl_rows += (
            f'<tr><td class="small"><strong>{e(k.replace("_", " "))}</strong></td>'
            f'<td class="small">{e(v)}</td>'
            f'<td class="small"><a href="{e(where)}" target="_blank" rel="noopener">'
            f'in this repository \u2197</a></td></tr>')
    body = f"""
<section class="hero-lite">
  <p class="kicker">Owner workspace · measurement</p>
  <h1>Measure only what the system can verify.</h1>
  <p class="lede">Five event definitions and a reporting cadence are ready for review. Collection is deliberately disabled: the current GitHub Pages publication has no server endpoint, no verified account connection and no approved analytics privacy notice.</p>
</section>

<div class="callout warn">
  <strong>Prepared, not live.</strong>
  The source-controlled collector is a deployment reference, not a live service. This publication currently sends no analytics events. No click totals, conversions, traffic sources or revenue are claimed.
</div>

<h2>Event definitions</h2>
<p class="small">In the reference design, browser payloads contain only allow-listed page/product IDs or a fixed engagement bucket, and the application stores daily aggregates rather than raw event rows. The client reads no cookies, persistent IDs, referrers, query strings or destination URLs. The collector disables its own HTTP access log; host and proxy logging must also be reviewed before deployment. <code>affiliate_report_import</code> is an operator-only aggregate from an authorized report, not a browser event.</p>
<div class="tablewrap">
<table>
  <caption>Five event types in the project-owned measurement schema</caption>
  <thead><tr><th>Event</th><th>Origin</th><th>When it is recorded</th><th>Allowed data</th><th>Current state</th><th>Source / definition</th></tr></thead>
  <tbody>{"".join(event_rows)}</tbody>
</table>
</div>

<h2>Cadence</h2>
<p class="small">These are operating rules for the project, not evidence that any event or search query has been recorded.</p>
<div class="tablewrap">
<table>
  <caption>Measurement and publication cadence</caption>
  <thead><tr><th>When</th><th>Action</th><th>Definition</th></tr></thead>
  <tbody>{cadence_rows}</tbody>
</table>
</div>

<h2>Deployment and access gates</h2>
<div class="tablewrap">
<table>
  <caption>What must be verified before measurement is enabled</caption>
  <thead><tr><th>Gate</th><th>Current evidence and missing step</th><th>Source</th></tr></thead>
  <tbody>{gates_html}</tbody>
</table>
</div>

<h2>What actually ships in this repository</h2>
<p class="small">One canonical wire contract is defined in <code>data/analytics-plan.json</code>.
The EV-01…EV-05 labels below refer to those exact event names, not a separate protocol.
The browser client and supported Python collector are integration-tested together;
a synthetic test is not live traffic. No production endpoint is deployed.</p>
<div class="tablewrap">
<table>
  <caption>What ships, and what does not</caption>
  <thead><tr><th style="width:18%">Part</th><th style="width:62%">State</th><th style="width:20%">Where to look</th></tr></thead>
  <tbody>{impl_rows}</tbody>
</table>
</div>

<h2>The client-side events, in detail</h2>
{events}

<div class="callout info">
  <strong>Privacy rules the counter must keep</strong>
  <ul class="tight small" style="margin-bottom:0">{priv}</ul>
</div>

<h2>Why nothing is sending yet</h2>
<ul class="tight small">{why}</ul>

<h2 id="campaign-ledger">Campaign ledger</h2>
<p class="small">{e(led['note'])}</p>
<div class="tablewrap">
<table>
  <caption>Empty on purpose. Columns: {e(', '.join(led['columns']))}</caption>
  <thead><tr>{''.join(f'<th>{e(c)}</th>' for c in led['columns'])}</tr></thead>
  <tbody><tr><td colspan="{len(led['columns'])}" class="small muted">No rows. {e(led['why_empty'])} {SRC_S2}</td></tr></tbody>
</table>
</div>

<h2>What has to be true before a single event sends</h2>
<div class="tablewrap">
<table>
  <caption>Prerequisites, in order</caption>
  <thead><tr><th style="width:6%">Step</th><th style="width:34%">Owner action</th>
  <th style="width:16%">Blocks</th><th style="width:44%">Why</th></tr></thead>
  <tbody>{pre}</tbody>
</table>
</div>

<h2>Choose future topics from measured queries</h2>
<p class="small">The topic register contains editorial hypotheses, not demand estimates. Verify the site's Search Console property, submit the generated sitemap, and wait for real query/page data before describing a topic as popular or trending. The build regenerates the sitemap from indexable publication pages and the feed from registered articles; include a guide in the appropriate register before publishing so those outputs update together.</p>
<p class="small">References: <a href="topics.html">Content and traffic plan</a> · <a href="questions.html">Questions and discovery steps</a> · <a href="product-intent.html">Product-link records and campaign ledger</a> · {src_links(["S30", "S31", "S38"])}</p>
"""
    return layout("measurement.html", "Measurement plan and deployment gate", body,
                  active="measurement.html",
                  description="Five privacy-minimizing event definitions, a publication/report cadence, and explicit unverified hosting and account blockers. Collection remains disabled.",
                  jsonld_blocks=[breadcrumbs_jsonld([
                      ("Home", SITE_BASE),
                      ("Measurement plan", page_url("measurement.html")),
                  ])])

def page_decisions():
    body=f"""<p class="crumbs"><a href="index.html">Home</a> / Publishing strategy</p><p class="section-eyebrow">The operating choices</p><h1>Publish the useful answer. Measure the real result.</h1><p class="lede">A source-led buying publication is implemented. Profitability, popularity and conversion performance are not established by a well-designed page or a weighted score.</p>
<h2>The scope</h2><p>{e(PUBLICATION['positioning'])}</p><p class="small">Three documented appliance guides and two unconfirmed thermometer link notes reflect the submitted set, not a claim to cover a whole market. Brand/listing/model conflicts remain on <a href="flagged.html">the public review register</a>. {src_links(['S10','S12','S14','S36','S37'])}</p>
<h2>The editorial rhythm</h2><p>{e(PUBLICATION['cadence']['rhythm'])}</p><p>{e(PUBLICATION['cadence']['kill_rule'])}</p><p class="small muted">{e(PUBLICATION['cadence']['status'])}. {e(PUBLICATION['cadence']['seasonal'])}</p>
<h2>The reader loop</h2><p>Answer practical kitchen buying questions, connect the existing intent clusters, and offer the real <a href="feed.xml">RSS feed</a>. No social account, email service, paid campaign, popularity badge or lead total is fabricated. Search work is canonical metadata, a maintained sitemap and useful internal links—not a traffic guarantee. {src_links(['S43','S44','S45'])}</p>
<h2>The measurement boundary</h2><p>The four allowed browser events are page_view, outbound_click, article_engagement and comparison_interaction. affiliate_report_import is operator-only. The tested first-party collector stays disabled until real hosting/privacy gates pass. The <a href="product-intent.html#campaign-ledger">campaign ledger</a> remains empty. {src_links(['S2','S38'])}</p>
<p>No revenue scenario, forecast or conversion score is used to justify current design. Do not turn brand list prices, candidate rates or synthetic browser tests into actual earnings. Actual orders and commission facts come only from authorised dated first-party reports. {src_links(['S1','S42'])}</p>
<h2>What remains a plan</h2><p>Automated source monitoring, licensed content integrations, production measurement and campaign optimisation require the access, permissions, runtime and data described on <a href="platform.html">the platform blueprint</a>. The static generator does not create those prerequisites.</p><p class="section-note"><a href="suggestions.html">Review current choices and alternatives</a> · <a href="questions.html">Known facts, missing data and discovery steps</a> · <a href="handover.html">Deployment/account boundaries</a> · <a href="design-prompt.html">House design and voice brief</a>.</p>"""
    return layout('decisions.html','Publishing strategy & measurement boundary',body,active='decisions.html',description='The current publication scope, cadence plan, reader loop and evidence-first measurement rules. No revenue or conversion forecasts.',jsonld_blocks=[breadcrumbs_jsonld([('Home',SITE_BASE),('Strategy',page_url('decisions.html'))])])


def _md(text):
    """Escape, then honour **bold** and `code` from the JSON prose.

    data/decision.json stores prose with light markdown so it stays readable as data. This is
    the only place that turns it into HTML, so a stray asterisk or backtick cannot reach a
    page. Added 2026-11-15 after handover.html was published showing literal ``**`` around
    two words of an action title.
    """
    out = e(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"`(.+?)`", r"<code>\1</code>", out)
    return out


def page_handover():
    body=f"""<p class="crumbs"><a href="index.html">Home</a> / Deployment & account boundaries</p><h1>What code cannot confirm on its own.</h1><p class="lede">No manual review is needed to publish this repository change. These are the separate account, permission and runtime gates that an autonomous static-site build cannot truthfully fill in.</p>
<section class="card"><h2 style="margin-top:0">1. Intended listings and enrolled link validation</h2><p>For each of the five exact submitted URLs, confirm the intended official listing, its ASIN, date and source separately from the observed redirect. Use the enrolled account’s permitted Special Link workflow and authorised reporting evidence before scaling. Do not self-purchase, manufacture traffic or assume that a missing visible tracking parameter proves failure. {src_links(['S2','S41','S42'])}</p><p class="small">Until that evidence exists, shopnow047c-20 stays selected but unapplied, and every per-product test stays false. <a href="product-intent.html">Exact fields and all submitted links</a>.</p></section>
<section class="card"><h2 style="margin-top:0">2. Production measurement</h2><p>The Python/SQLite collector is tested, not deployed. Pages is a static host; a controlled runtime must sit behind the same public origin. Review proxy/security logs, HTTPS, database location/retention and the actual privacy/consent posture before enabling the two switches. {src_links(['S38','S2'])}</p><p class="small"><a href="analytics/README.md">Deployment contract</a> · <a href="measurement.html">Five events and current state</a>. Workspace tests never become campaign traffic.</p></section>
<section class="card"><h2 style="margin-top:0">3. Search ownership</h2><p>Use the configured /Zone1/ URL-prefix property. Only a real verification token or another authorised method can establish access. No token, property approval, sitemap submission or query performance is invented. {src_links(['S44','S45'])}</p><p class="small">The generator supports a blank optional search_console_verification field. Record actual submission/ownership evidence before changing its state.</p></section>
<section class="card"><h2 style="margin-top:0">4. Actual product images and licensed Amazon content</h2><p>The current AI scene is decorative and labelled; it is not a photograph of a model or evidence of a test. Actual product photography requires original work or suitable documented rights. API price/rating/review content requires the applicable authorised route and terms. {src_links(['S2','S8'])}</p><p class="small"><a href="publication/README.md">Current asset provenance</a>.</p></section>
<section class="card"><h2 style="margin-top:0">5. Safety clarification</h2><p>The Emeril FAFO-001 manual contains incompatible extension-cord instructions. Seek current manufacturer clarification for the exact unit before relying on an affected setup; this publication does not select the permissive instruction. {src_links(['S15'])} <a href="flagged.html#f96">F96</a>.</p></section>
<p class="section-note">These gates do not block the honest source-led publication. They block claims of validated attribution, deployed collection, approved content integration or measured results. <a href="executive-summary.html">Current executive summary</a> · <a href="questions.html">Full known/missing/answer/discovery register</a>.</p>"""
    return layout('handover.html','Deployment & account boundaries',body,active='handover.html',description='What remains unconfirmed beyond repository authority: intended listings, enrolled link tests, production measurement, search ownership and content permissions.',jsonld_blocks=[breadcrumbs_jsonld([('Home',SITE_BASE),('Deployment boundaries',page_url('handover.html'))])])


# --------------------------------------------------------------------------- #
# build
# --------------------------------------------------------------------------- #

def check_legacy_flag_pointers(pages):
    """Build guard: a zero-padded flag id (F01, F06, ...) must sit in a block that names the
    legacy register, never in a bare pointer a reader is expected to follow.

    Found 2026-11-17 (arena/0cf55ef3-zone1). decisions.html and handover.html said the owner's
    actions close "F01", "F02", "F03", "F06" and "F07". Those ids exist in data/flags.json, the
    older annex register, so check_register_cross_references() accepted them; but the page they
    are printed on is the root Flagged page, which renders the canonical register (F1, F6, ...).
    A reader who followed one landed on the wrong row or on nothing. The entries were re-pointed
    at canonical rows in data/decision.json.

    This guard keeps the distinction executable. It works block by block - a table row, an
    article card or a paragraph - rather than on a character window, because a register row may
    legitimately list the legacy ids first and explain them in the next sentence (F83 does).
    A block that mentions data/flags.json, "legacy" or the annex register may print them; any
    other block may not.
    """
    problems = []
    legacy_tell = re.compile(r"data/flags\.json|legacy|annex register", re.I)
    block_split = re.compile(r"</tr>|</article>|</li>|</p>", re.I)
    for rel, html_text in pages.items():
        for block in block_split.split(html_text):
            plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", block))
            hits = re.findall(r"\bF0\d\b", plain)
            if not hits or legacy_tell.search(plain):
                continue
            for hit in sorted(set(hits)):
                at = plain.find(hit)
                problems.append(
                    f"{rel}: bare legacy flag id {hit} in a block that never names the legacy "
                    f"register (near: ...{plain[max(0, at - 90):at + 90].strip()}...)"
                )
    return problems


def check_flag_ids_unique():
    """Build guard: a flag number must mean exactly one thing.

    Flag F40 (2026-11-15) records two different rows being published as F36 on the same
    page. F28 records an earlier collision of the same kind, which is why a written rule
    was not enough and this check exists. Runs on the rendered Flagged page, so it sees
    programme rows and product rows together rather than trusting either list alone.
    """
    from collections import Counter
    page = page_flagged()
    # The row markup carries an id attribute since pass 10 (<tr id="fNN">); matching on
    # `<tr><td class="num">` made this guard find zero rows and pass vacuously. Located
    # by the fixed flag-count guard below, 2026-11-16 (arena/2e346d24).
    ids = re.findall(r'<tr id="f\d+"><td class="num"><strong>(F\d+)</strong>', page)
    dupes = sorted(k for k, v in Counter(ids).items() if v > 1)
    if dupes:
        return [f"flag id(s) rendered more than once on flagged.html: {', '.join(dupes)}"]
    return []


def check_flag_count_matches_page():
    """Build guard: the review register's rendered rows must match its computed count.

    The buyer-first front page intentionally no longer carries an audit-count tile; the
    detailed count belongs on flagged.html, not in the shopping decision path. Keep checking
    that the register's own rows and count agree so the redesign cannot hide a drift.
    """
    rendered = len(re.findall(r'<tr id="f\d+"><td class="num"><strong>F\d+</strong>',
                              page_flagged()))
    computed = _flag_count()
    if rendered == 0:
        return ["flagged.html renders no flag rows, so the landing-page count cannot be trusted"]
    if rendered != computed:
        return [f"landing-page flag count ({computed}) disagrees with the rendered "
                f"register ({rendered} rows)"]
    return []


def check_callout_states_and_table_wraps(pages):
    """Build guard: every CSS state a page uses must be defined, and wide tables must scroll.

    Two visual defects were live on main at 9c6deab and neither had a gate:
    `.callout.note` (13 uses) and `.callout.warn` (33 uses) had no rule in the stylesheet, so
    46 callouts rendered with no colour distinction between "for information" and "this could
    be wrong"; and four register pages emitted `<table>` outside `.tablewrap`, so those
    tables forced the whole page to scroll sideways at phone width. Both are cheap to check
    and expensive to notice by eye on a page nobody proof-reads twice.
    """
    problems = []
    defined = set(re.findall(r'\.callout\.([a-z]+)', CSS))
    for rel, text in pages.items():
        if not rel.endswith(".html"):
            continue
        used = set(re.findall(r'class="callout ([a-z]+)"', text))
        for state in sorted(used - defined):
            problems.append(f"{rel}: .callout.{state} is used but has no CSS rule")
        for m in re.finditer(r"<table[ >]", text):
            before = text[max(0, m.start() - 220):m.start()]
            if "tablewrap" not in before:
                problems.append(f"{rel}: a <table> is not inside .tablewrap and will "
                                f"overflow the viewport on a narrow screen")
                break
    return problems


def check_internal_fragments(pages):
    """Build guard: every href="#id" must resolve to an element on the page it names.

    `verify.py` checks that a link's *file* exists; it has never checked the fragment.
    A plan table that links each row to a detail block the template no longer emits is
    therefore invisible to every existing gate - which is exactly what topics.html was
    doing for 8 of its 14 rows when this guard was written (2026-11-16, arena/2e346d24).
    """
    ids = {rel: set(re.findall(r'\sid="([^"]+)"', text)) for rel, text in pages.items()}
    problems = []
    for rel, text in pages.items():
        if not rel.endswith(".html"):
            continue
        for target, frag in re.findall(r'href="([^"#]*)#([^"]+)"', text):
            if frag in ("", "top"):
                continue
            dest = rel if target == "" else posixpath.normpath(
                posixpath.join(posixpath.dirname(rel), target))
            if dest not in ids:
                continue  # an external or generated-at-another-step target; verify.py owns it
            if frag not in ids[dest]:
                problems.append(f"{rel}: href=\"{target}#{frag}\" has no target in {dest}")
    return problems


def _canonical_flag_ids():
    """Every flag id the Flagged page actually publishes."""
    ids = {f[0] for f in PROGRAMME_FLAGS}
    for p in PRODUCT_LIST:
        for f in p.get("flags", []):
            ids.add(f["id"])
    return ids


def _legacy_flag_ids():
    """Ids of the second, older register (data/flags.json, F01-F27).

    Flag F47 documents that two registers exist in this repository and disagree. Pages
    that point at the older register name its ids explicitly, and those pointers are
    correct - the rows are in that file. They are therefore accepted here, and only
    ids that are in neither register are treated as dangling.
    """
    path = ROOT / "data" / "flags.json"
    if not path.exists():
        return set()
    try:
        legacy = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return set()
    return {f.get("id") for f in legacy.get("flags", []) if f.get("id")}


def check_register_cross_references(pages):
    """Build guard: every id a published page points at must exist in the register it
    points at.

    Written 2026-11-16 (arena/9fccce0c-zone1) after the live site was found to tell the
    reader to see "flag F46" on three pages - a flag number that exists in no register
    in this repository. The pointer was live on questions.html, suggestions.html and
    data.html, and it was invisible to every earlier gate: the duplicate-id guard sees
    ids that are rendered twice, not ids that are rendered and do not exist.

    A reader who followed it landed on the Flagged page and found nothing, which is the
    worst possible outcome for a page whose entire claim is that every number is
    traceable. The check is therefore executable, not editorial.
    """
    problems = []
    known_flags = _canonical_flag_ids() | _legacy_flag_ids()
    known_sources = set(SRC_BY_ID)
    known_questions = {q["id"] for q in QUESTIONS.get("questions", [])}
    known_suggestions = set(SUG_BY_ID)

    patterns = (
        ("flag", re.compile(r"\bF(\d{1,2})\b"), "F"),
        ("source", re.compile(r"\bS(\d{1,2})\b"), "S"),
        ("question", re.compile(r"\bQ-(\d{2})\b"), "Q-"),
        ("suggestion", re.compile(r"\bSG-(\d{2})\b"), "SG-"),
    )
    known_by_kind = {
        "flag": known_flags,
        "source": known_sources,
        "question": known_questions,
        "suggestion": known_suggestions,
    }

    for rel, html_text in pages.items():
        for kind, pattern, prefix in patterns:
            known = known_by_kind[kind]
            for match in sorted(set(pattern.findall(html_text))):
                value = prefix + match
                if value not in known:
                    plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html_text))
                    at = plain.find(value)
                    context = plain[max(0, at - 70):at + 70] if at >= 0 else ""
                    problems.append(
                        f"{rel}: {kind} id {value} does not exist in any register"
                        + (f" (near: ...{context.strip()}...)" if context else "")
                    )
    return problems


def check_register_preambles():
    """Build guard: a register preamble must not repeat itself.

    A sentence appended to a register's preamble by a one-shot editor will be
    appended a second time if the editor is run twice. The result reads as a
    copy-paste slip on a published page, and nothing else catches it: the
    duplicate-ID guard sees IDs, the value guard sees numbers, and a repeated
    sentence is neither. This is the guard behind flag F58.
    """
    import collections as _c
    problems = []
    for name, raw in (("questions.json", QUESTIONS.get("preamble", "")),
                      ("suggestions.json", SUGGESTIONS.get("how_to_read", "")),
                      ("suggestions.json (scoring_note)", SUGGESTIONS.get("scoring_note", ""))):
        if isinstance(raw, list):
            text = " ".join(str(x) for x in raw)
        else:
            text = str(raw or "")
        sentences = [s.strip() for s in re.split(r"(?<=\.)\s+", text) if len(s.strip()) > 40]
        for sentence, n in _c.Counter(sentences).items():
            if n > 1:
                problems.append(
                    f"{name}: the sentence {sentence[:70]!r} appears {n} times in the preamble")
    return problems


def check_register_duplicates():
    """Build guard: a register must not carry the same content twice.

    Three separate places shipped duplicated prose to the published site and no gate
    caught them (flag F64): a questions register whose 'what we know' list repeated
    three entries seven times each, so one sentence rendered 14 times on
    questions.html; an articles note that repeated its opening paragraph; and a
    specification row that cited the same source three times in a row. None was a
    wrong fact - each was the same fact printed repeatedly, which is exactly the
    pattern that makes a page read as machine-generated.

    check_register_preambles() covers preamble text only. This guard covers every
    other register field, in both forms the defect took: a repeated entry in a list,
    and a repeated sentence inside one string.
    """
    import collections as _c
    problems = []

    def sentences(text):
        return [s.strip() for s in re.split(r"(?<=\.)\s+", text) if len(s.strip()) > 40]

    def walk(node, path, label):
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}/{key}", label)
        elif isinstance(node, list):
            counts = _c.Counter(x for x in node if isinstance(x, str) and x.strip())
            for text, n in counts.items():
                if n > 1:
                    problems.append(
                        f"{label} {path}: the list entry {text[:70]!r} appears {n} times")
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]", label)
        elif isinstance(node, str):
            for text, n in _c.Counter(sentences(node)).items():
                if n > 1:
                    problems.append(
                        f"{label} {path}: the sentence {text[:70]!r} appears {n} times")

    registers = [
        ("questions.json", QUESTIONS),
        ("suggestions.json", SUGGESTIONS),
        ("articles.json", ARTICLES),
        ("products.json", PRODUCTS),
    ]
    if "DECISION" in globals():
        registers.append(("decision.json", DECISION))
    if "TOPICS" in globals():
        registers.append(("topics.json", TOPICS))
    if "DESIGN_PROMPT" in globals():
        registers.append(("design-prompt.json", DESIGN_PROMPT))
    for label, data in registers:
        if data:
            walk(data, "", label)
    return problems


def check_question_block_refs():
    """Build guard: a suggestion must not point at a question that does not exist, and a
    question must not point at a suggestion that does not exist. A dangling cross-reference
    in a decision queue is worse than no cross-reference."""
    problems = []
    qids = {q["id"] for q in QUESTIONS["questions"]}
    for sg in SUGGESTIONS["suggestions"]:
        for qid in sg.get("blocked_by") or []:
            if qid not in qids:
                problems.append(f'{sg["id"]} blocked_by unknown question {qid}')
    for q in QUESTIONS["questions"]:
        for sid in q.get("blocks") or []:
            if sid not in SUG_BY_ID:
                problems.append(f'{q["id"]} blocks unknown suggestion {sid}')
    if not QUESTIONS["questions"] or not SUGGESTIONS["suggestions"]:
        problems.append("decision-layer register is empty")
    return problems


def check_no_price_tracking(pages):
    """Build guard: Program Policies section 6(y) forbids price tracking and/or price
    alerting functionality on an Associate site unless Amazon agrees otherwise.

    Scope is deliberately narrow so the guard tests implementation rather than vocabulary.
    The site must be free to *explain* the rule - an entire article on policy quotes it, and
    suggestions.html proposes writing this very guard - so prose is never scanned. What is
    scanned:

      1. the body of every <script> block (a tracker has to live in JavaScript);
      2. attribute values only - id, class, data-* - where a real component would declare
         itself (id="price-history", data-price-alert, class="price-tracker").

    Both patterns require a code-shaped token (an identifier with - or _ joining the words,
    or camelCase), which ordinary sentences do not produce. Verified verbatim against the
    Program Policies page on 2026-11-15.
    """
    ident = re.compile(
        r"price[-_](history|tracker|tracking|alert|alerts|watch)\b"
        r"|priceHistory|priceAlert|priceTrack|trackPrice|track_amazon_price",
        re.I)
    attr = re.compile(r"\b(?:id|class|data-[a-z-]+)\s*=\s*\"([^\"]*)\"", re.I)
    problems = []
    for rel, html_text in pages.items():
        for script in re.findall(r"<script\b[^>]*>(.*?)</script>", html_text, re.S):
            for m in ident.finditer(script):
                around = re.sub(r"\s+", " ", script[max(0, m.start()-50):m.end()+50])
                problems.append(f"{rel}: price-tracking identifier in script (6(y)): ...{around}...")
        for value in attr.findall(html_text):
            if ident.search(value):
                problems.append(f"{rel}: price-tracking class/id/attribute (6(y)): {value!r}")
    return problems

# --------------------------------------------------------------------------- #
# The measurement guard (2026-11-17, session 79743fd2).
# --------------------------------------------------------------------------- #

# Tokens the counter must never contain. The counter is allowed to know the
# page it is on, the ASIN the reader clicked and the date; it is not allowed to
# know who the reader is. Each token below is a way of doing that, so the file
# is checked for them rather than trusted to have avoided them.
BANNED_IN_COUNTER = [
    "document.cookie", "localStorage", "sessionStorage", "indexedDB",
    "navigator.userAgent", "document.referrer", "window.name",
    "navigator.geolocation", "navigator.credentials",
]

# Third-party hosts that would need their own disclosure and their own review.
# The counter must point at an endpoint the owner controls, not at a hosted
# analytics product that quietly sets its own cookies.
BANNED_ANALYTICS_HOSTS = [
    "google-analytics.com", "googletagmanager.com", "analytics.google.com",
    "segment.io", "segment.com", "hotjar.com", "mixpanel.com", "plausible.io",
    "amplitude.com", "matomo.cloud", "statcounter.com",
]


def check_analytics_consistency(pages):
    """The real client, collector schema, deployment gate and privacy notice must agree."""
    from analytics.collector import BROWSER_EVENTS, ENDPOINT_PATH
    problems = []
    collection = ANALYTICS_PLAN.get("collection", {})
    if ANALYTICS_ENABLED != bool(collection.get("enabled")):
        problems.append("analytics switches disagree between config.json and analytics-plan.json")
    if ANALYTICS_ENABLED:
        for key in ("endpoint_deployed", "runtime_selected", "privacy_notice_approved"):
            if not collection.get(key):
                problems.append(f"analytics cannot run before {key} is verified")
        if ANALYTICS_ENDPOINT != ENDPOINT_PATH:
            problems.append("analytics.endpoint must be the verified same-origin /api/analytics/events route")
    elif ANALYTICS_ENDPOINT and ANALYTICS_ENDPOINT != ENDPOINT_PATH:
        problems.append("analytics.endpoint must be empty or the same-origin collector route")
    if set(ANALYTICS_EVENTS) != BROWSER_EVENTS or len(ANALYTICS_EVENTS) != len(BROWSER_EVENTS):
        problems.append("browser event names differ from the collector's allow-list")
    details = MEASUREMENT.get("events", [])
    plan_events = ANALYTICS_PLAN.get("events", [])
    if [(x.get("id"), x.get("name")) for x in details] != [(x.get("id"), x.get("name")) for x in plan_events]:
        problems.append("measurement event IDs/names drifted from analytics-plan.json")
    for event in BROWSER_EVENTS:
        if '"' + event + '"' not in ANALYTICS_JS:
            problems.append(f"browser client does not implement {event}")
    if "affiliate_report_import" in ANALYTICS_JS:
        problems.append("the browser must never emit an order/report event")
    for token in BANNED_IN_COUNTER:
        if token in ANALYTICS_JS:
            problems.append(f"analytics client contains forbidden reader-identifying API {token!r}")
    if "preventDefault" in ANALYTICS_JS or "sendBeacon" in re.sub(r"//[^\n]*", "", ANALYTICS_JS):
        problems.append("client must not block navigation or send credentialed beacons")
    if "isTrusted" not in ANALYTICS_JS or 'credentials: "omit"' not in ANALYTICS_JS:
        problems.append("client must check trusted activation and omit credentials")
    for rel, text in pages.items():
        has_script = re.search(r'<script[^>]+src="[^"]*assets/analytics\.js"', text) is not None
        expected = bool(ANALYTICS_ON and is_indexable_page(rel))
        if has_script != expected:
            problems.append(f"{rel}: analytics script does not match the collection/publication gate")
        if ANALYTICS_ON:
            if "It loads one small script of its own" not in text:
                problems.append(f"{rel}: enabled analytics notice is missing")
            if re.search(r"\bruns no analytics\b", text, re.I):
                problems.append(f"{rel}: published no-analytics claim would become false")
        elif "This site sets no cookies itself, runs no analytics" not in text:
            problems.append(f"{rel}: disabled analytics notice is missing")
    return problems


def check_clusters(generated=()):
    """Build guard: the cluster map and the article set must agree.

    The map is a second copy of a fact - which article belongs to which group -
    and a second copy of a fact is where the two drift apart. When a new
    article is added and nobody files it, it becomes invisible in the cluster
    navigation and reachable only from the flat list; when an article is
    renamed, the map points at a page that no longer exists. Both are the kind
    of defect no link checker sees, because every link in the map is a valid
    link to *something*.

    This guard fails the build if an article is unfiled, if an article is filed
    twice, if a cluster names an article that does not exist, if a cluster is
    empty, or if a cluster's hub is not a page this build actually generates.
    """
    problems = []
    ids = [c["id"] for c in CLUSTERS["clusters"]]
    if len(ids) != len(set(ids)):
        problems.append("two clusters share an id")
    slugs = {a["slug"] for a in ARTICLES["articles"]}
    filed = {}
    for c in CLUSTERS["clusters"]:
        if not c.get("members"):
            problems.append(f'cluster {c["id"]} has no members')
        for slug in c.get("members") or []:
            if slug not in slugs:
                problems.append(f'cluster {c["id"]} lists "{slug}", which is not an article')
            if slug in filed:
                problems.append(
                    f'"{slug}" is in both cluster {filed[slug]} and cluster {c["id"]}')
            filed[slug] = c["id"]
    for a in ARTICLES["articles"]:
        cid = a.get("cluster")
        if not cid:
            problems.append(f'article "{a["slug"]}" is not filed in a cluster')
        elif cid not in CLUSTER_BY_ID:
            problems.append(f'article "{a["slug"]}" names cluster "{cid}", which does not exist')
        elif filed.get(a["slug"]) != cid:
            problems.append(
                f'article "{a["slug"]}" says cluster "{cid}" but the map files it under '
                f'{filed.get(a["slug"])}')
    known = set(generated) if generated else set()
    for c in CLUSTERS["clusters"]:
        hub = c.get("hub") or ""
        if not hub:
            problems.append(f'cluster {c["id"]} has no hub')
        elif known and hub not in known:
            problems.append(
                f'cluster {c["id"]} points its hub at "{hub}", which this build does not '
                "generate")
    return problems


def check_rows_have_sources():
    """Build-time guard: an asserted value with no source id is a hard failure."""
    problems = []
    for p in PRODUCT_LIST:
        for s in p["specs"]:
            if s["value"] is not None and not s["source"]:
                problems.append(f'{p["slug"]}: "{s["label"]}" has a value but no source')
    return problems


def check_spec_source_conflicts():
    """Build guard: a row must not cite a document that contradicts its own value.

    Written 2026-11-15 (arena/88bb2db6) after this session cited the Amazon listing
    title on the Emeril "Included accessories" row. That listing says "Six Cooking
    Accessories Included" while the row's value is 7, so listing it as a source
    asserted something false about where the value came from.

    The check is driven by an explicit register in data/products.json
    (source_conflicts.entries), not by inference: there is no way for a build to
    tell that an arbitrary document contradicts a value. A reviewer who has read
    both documents records the conflict once, and from then on the contradiction
    can live in the flag register but never in the row's evidence.
    """
    problems = []
    register = (PRODUCTS.get("source_conflicts") or {}).get("entries") or []
    for entry in register:
        slug = entry.get("slug")
        label = entry.get("label")
        bad = entry.get("conflicting_source")
        product = next((p for p in PRODUCT_LIST if p["slug"] == slug), None)
        if product is None:
            problems.append(f"source_conflicts: unknown product slug {slug!r}")
            continue
        row = next((s for s in product["specs"] if s["label"] == label), None)
        if row is None:
            problems.append(f"source_conflicts: {slug} has no row labelled {label!r}")
            continue
        if bad in (row.get("source") or []):
            problems.append(
                f'{slug} / "{label}": cites {bad}, which contradicts the published value '
                f'{row.get("value")!r}. The contradicting document belongs in the flag '
                f'register, not in the row\'s source list.'
            )
    return problems


def check_disclosure(pages):
    """Disclosure is after the masthead, before the content, and repeated in the footer."""
    problems = []
    for rel, text in pages:
        header_end = text.find("</header>")
        bar = text.find('class="disclosure-bar"')
        main = text.find('<main')
        footer = text.find('<footer')
        if not (header_end >= 0 and header_end < bar < main < footer):
            problems.append(f"{rel}: disclosure strip must be under the masthead and before the main content")
        if DISCLOSURE not in text[bar:main] or DISCLOSURE not in text[footer:]:
            problems.append(f"{rel}: exact disclosure is required in the strip and footer")
    return problems


# Hosts a table row may cite: every registered source in data/sources.json, plus this
# repository on GitHub. A row that links to none of them fails the build.
def _registered_hosts():
    from urllib.parse import urlparse
    hosts = {(urlparse(s["url"]).hostname or "").lower() for s in SOURCES["sources"]}
    hosts.add("github.com")
    return {h for h in hosts if h}


REGISTERED_HOSTS = _registered_hosts()


def row_is_sourced(row_html):
    """Require an actual registered primary-source URL or this repository's own
    exact-file evidence. A generic flag/summary link is context, not the source.
    This checks link identity/coverage, not whether arbitrary prose is true.
    """
    from urllib.parse import urldefrag, urlparse
    registered = {urldefrag(r['url'])[0].rstrip('/') for r in SOURCES['sources']}
    registered.update(row['supplied_link'] for row in PRODUCT_INTENT['rows'])
    for href in re.findall(r'href="([^"]+)"', row_html):
        href = html.unescape(href)
        url = urlparse(href)
        if url.scheme != 'https':
            continue
        if urldefrag(href)[0].rstrip('/') in registered:
            return True
        if href.startswith(REPO_BLOB) and (ROOT / href[len(REPO_BLOB):].split('#')[0]).is_file():
            return True
    return False



def check_row_sources(pages):
    """Every table data row on every generated page must be sourced (see row_is_sourced)."""
    problems = []
    for rel, html_text in pages.items():
        for tbl in re.findall(r"<tbody>(.*?)</tbody>", html_text, re.S):
            for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", tbl, re.S):
                if "<td" not in row:
                    continue
                if not row_is_sourced(row):
                    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", row)).strip()[:90]
                    problems.append(f"{rel}: {text}")
    return problems


# --------------------------------------------------------------------------- #
# pass 9 guards (session 22f43836)
# --------------------------------------------------------------------------- #

# The local standard is intentionally stricter than a CTA-only check: every click from
# this publisher to an Amazon product detail page or supplied Amazon resolver is qualified,
# whether it is rendered as a button, an inline source citation or a table link. That makes
# the machine-readable treatment of an outbound product link unambiguous and implements the
# brief's “every outbound product link marked as sponsored” rule in one place. It does *not*
# turn Amazon policy, help, or developer-documentation links into sponsored links.
AFFILIATE_HOST = "link.amazon"
_AMAZON_PRODUCT_ANCHOR_RE = re.compile(
    r'<a\b(?=[^>]*\bhref="https://(?:link\.amazon/|(?:www\.)?amazon\.com/dp/))[^>]*>',
    re.I,
)


def is_product_href(href):
    """Submitted links and ordinary product listings; policy/help URLs are not products."""
    from urllib.parse import urlsplit
    parsed = urlsplit(html.unescape(href))
    return ((parsed.hostname == "link.amazon" and "ZZZ9ZZZZZ" not in parsed.path) or
            (parsed.hostname in {"amazon.com", "www.amazon.com"} and
             parsed.path.startswith(("/dp/", "/gp/product/"))))

def qualify_affiliate_links(html_text):
    """Qualify every outbound product anchor, including listing citation badges.

    Preserve other rel values, add sponsored/nofollow/noopener, never rewrite a
    destination. The nonsense-token control is not a product; it remains a citation.
    """
    def fix(match):
        tag = match.group(0)
        href = re.search(r'href="([^\"]+)"', tag, re.I)
        if not href or not is_product_href(href.group(1)):
            return tag
        existing = re.search(r'rel="([^\"]*)"', tag, re.I)
        values = uniq(["sponsored", "nofollow", "noopener"] +
                      (existing.group(1).split() if existing else []))
        tag = re.sub(r'\srel="[^\"]*"', "", tag, count=1, flags=re.I)
        return tag[:-1].rstrip() + f' rel="{" ".join(values)}">'
    return re.sub(r'<a\b[^>]*>', fix, html_text, flags=re.I)


def check_affiliate_link_qualification(pages):
    """All outbound product anchors must retain sponsored, nofollow and noopener."""
    problems = []
    for rel, text in pages.items():
        for tag in re.findall(r'<a\b[^>]*>', text, re.I):
            href = re.search(r'href="([^\"]+)"', tag, re.I)
            if not href or not is_product_href(href.group(1)):
                continue
            values = re.search(r'rel="([^\"]*)"', tag, re.I)
            if not {"sponsored", "nofollow", "noopener"}.issubset(set(values.group(1).split() if values else [])):
                problems.append(f"{rel}: product link must be sponsored/nofollow/noopener: {href.group(1)}")
    return problems


def check_seo_metadata(pages):
    """Build guard: the SEO/sharing metadata must exist on every generated page.

    Written because the defect it prevents was live: before pass 9 no generated page had a
    canonical URL, an Open Graph title or structured data, measured as 0/27 pages on
    2026-11-15. A metadata block that is added by hand once and then dropped by the next
    template edit is not a fix, so the requirement is executable.
    """
    problems = []
    for rel, html_text in pages.items():
        if not rel.endswith(".html"):
            continue
        expected_robots = ("index,follow,max-image-preview:large" if is_indexable_page(rel)
                           else "noindex,follow")
        if f'<meta name="robots" content="{expected_robots}">' not in html_text:
            problems.append(f"{rel}: robots directive must be {expected_robots!r}")
        if rel == "404.html":
            if '<meta name="robots" content="noindex,follow">' not in html_text:
                problems.append(f"{rel}: 404 page must carry a noindex robots meta")
            if 'rel="canonical"' in html_text:
                problems.append(f"{rel}: 404 page must not declare a canonical URL")
            # GitHub Pages serves this file at any missing path, so a relative
            # href resolves against that path and breaks (flag F75).
            for m in re.finditer(r'(?:href|src)="([^"]+)"', html_text):
                u = m.group(1)
                if u.startswith(("#", "http://", "https://", "data:", "mailto:", "//")):
                    continue
                problems.append(
                    f"{rel}: relative URL {u!r} — 404.html is served at arbitrary "
                    "paths, so every href/src must be absolute")
            continue
        for needle, what in (
            ('rel="canonical"', "canonical URL"),
            ('property="og:title"', "Open Graph title"),
            ('name="twitter:card"', "Twitter card"),
            ('application/ld+json', "structured data"),
        ):
            if needle not in html_text:
                problems.append(f"{rel}: missing {what}")
        m = re.search(r'<script type="application/ld\+json">(.*?)</script>',
                      html_text, re.S)
        if m:
            try:
                json.loads(m.group(1))
            except Exception as exc:  # noqa: BLE001 - any parse failure is a build failure
                problems.append(f"{rel}: structured data is not valid JSON ({exc})")
        if 'name="description"' not in html_text:
            problems.append(f"{rel}: missing meta description")
    return problems


_LINK_PHRASE = re.compile(
    r"\b(?:all\s+|each of\s+|both\s+|none of\s+|every one of\s+|only\s+|just\s+)?"
    r"(?:the\s+)?(one|two|three|four|five|six|seven|eight)\s+"
    r"(supplied|submitted)(?: short)? links?\b", re.I)


def check_submitted_link_count(pages):
    """Build guard: a present-tense page may not assert a link count the register contradicts.

    Why this exists (main's F77/F79 lineage, extended 2026-11-17): the number of links the owner has
    submitted changes when the owner acts, and for ten passes it was typed into prose. Every individual
    value in those sentences stayed correct while the sentence went false — the narrative was the
    unverified thing, and no gate read it.

    Scope: the surfaces where the count is a claim about right now. Dated verification prose is outside
    it on purpose. "All three supplied links" was true on 2026-11-14; forcing history to agree with a
    check would destroy the evidence history is here to be.
    """
    present_tense = {"index.html", "product-intent.html", "measurement.html", "compare.html",
                     "picks.html", "compliance.html", "categories", "products", "guides"}
    words = {v: k for k, v in _LINK_NUM_WORDS.items()}
    problems = []
    for rel, html_text in pages.items():
        if rel.split("/")[0] not in present_tense:
            continue
        plain = re.sub(r"<[^>]+>", " ", html_text)
        for m in _LINK_PHRASE.finditer(plain):
            n = _LINK_NUM_WORDS[m.group(1).lower()]
            if n == N_SUBMITTED_LINKS:
                continue
            kind = m.group(2) or "supplied"
            problems.append(
                f"{rel}: asserts '{words.get(n, n)} {kind} links' where data/product-intent.json holds "
                f"{N_SUBMITTED_LINKS} rows — read the count from the register, or date the sentence so it "
                f"says when it was true")
    return problems


def check_intent_measurement_contract(pages=None):
    """Guard the five link records and the disabled-by-default analytics gate."""
    problems = []
    expected_links = {
        "https://link.amazon/B04G1MEwY",
        "https://link.amazon/B02NbDxp3",
        "https://link.amazon/B00hJ57DV",
        "https://link.amazon/B0c8moW59",
        "https://link.amazon/B0f3GKalj",
    }
    rows = PRODUCT_INTENT.get("rows", [])
    if len(rows) != 5 or {row.get("supplied_link") for row in rows} != expected_links:
        problems.append("product-intent register must preserve the five supplied link strings exactly")
    for row in rows:
        confirmed = all(row.get(field) for field in (
            "intended_asin", "official_listing_url", "confirmation_date", "confirmation_source"))
        if any(row.get(field) for field in (
            "intended_asin", "official_listing_url", "confirmation_date", "confirmation_source")) and not confirmed:
            problems.append(f"{row.get('id')}: intended listing fields must be confirmed together or remain blank")
    selected = SITE_CONFIG.get("selected_tracking_id")
    if selected != PRODUCT_INTENT.get("tracking_id_selected"):
        problems.append("selected tracking ID differs between config.json and product-intent.json")
    associate_tag = (SITE_CONFIG.get("associate_tag") or "").strip()
    applied = bool(PRODUCT_INTENT.get("tracking_id_applied_to_links"))
    if bool(associate_tag) != applied:
        problems.append("associate_tag and tracking_id_applied_to_links must agree")
    if associate_tag or applied:
        if associate_tag != selected:
            problems.append("configured associate_tag must match the separately recorded tracking ID")
        if not SITE_CONFIG.get("selected_tracking_id_associates_central_confirmed") or not PRODUCT_INTENT.get("tracking_id_associates_central_confirmed"):
            problems.append("associate_tag cannot be applied before the tracking ID is confirmed in Associates Central")
        for row in rows:
            intended_fields = ("intended_asin", "official_listing_url", "confirmation_date", "confirmation_source")
            if not all(row.get(field) for field in intended_fields):
                problems.append(f"{row.get('id')}: associate_tag cannot be applied before intended listing confirmation")
            if not (row.get("associates_link_test_passed") and row.get("associates_link_test_date") and row.get("associates_link_test_source")):
                problems.append(f"{row.get('id')}: associate_tag cannot be applied before its enrolled-Associates test is recorded")

    names = [event.get("name") for event in ANALYTICS_PLAN.get("events", [])]
    required_events = {
        "page_view", "outbound_click", "article_engagement",
        "comparison_interaction", "affiliate_report_import",
    }
    if len(names) != 5 or set(names) != required_events:
        problems.append("analytics plan must define the five agreed event types exactly once")
    collection = ANALYTICS_PLAN.get("collection", {})
    if collection.get("enabled") and not all(collection.get(key) for key in (
        "endpoint_deployed", "runtime_selected", "privacy_notice_approved")):
        problems.append("analytics cannot be enabled before runtime, endpoint and privacy gates pass")
    if pages is not None and not collection.get("enabled"):
        for rel, text in pages.items():
            if re.search(r'<script\b[^>]+src="[^"]*assets/analytics\.js"', text):
                problems.append(f"{rel}: analytics client must not load while collection is disabled")
    ledger_required = {
        "timestamp_utc", "source_report", "channel", "date_range",
        "eligible_sessions", "clicks", "reported_orders",
    }
    if not ledger_required.issubset(set(CAMPAIGN_LEDGER.get("columns", []))):
        problems.append("campaign ledger is missing one or more required report fields")
    return problems


_FLAG_ANCHOR_RE = re.compile(r'<a\b[^>]*href="[^"]*flagged\.html#f(\d+)"[^>]*>(.*?)</a>', re.S | re.I)


def check_flag_anchor_labels(pages):
    """F92 / SG-50: a link whose text names one flag must land on that flag's row.

    Pass 13 renumbered F84->F86 and F86->F88; the labels on Q-38 and Q-40 were rewritten and
    the URL fragments were not, so 'Flag F86' opened F84. check_register_cross_references()
    reads labels only, so nothing caught it. This compares the label with the fragment on
    every published page."""
    problems = []
    for name, content in pages.items():
        if not name.endswith(".html"):
            continue
        for m in _FLAG_ANCHOR_RE.finditer(content):
            frag = m.group(1)
            text = re.sub(r"<[^>]+>", " ", m.group(2))
            named = set(re.findall(r"\bF(\d+)\b", text))
            if len(named) == 1 and frag not in named:
                problems.append(f"{name}: link text names F{next(iter(named))} but opens #f{frag}")
    return problems


def check_desk_nav(pages):
    """Retain P14's explicit owner inventory and test both actual rendered routes.

    The root redesign replaces the old sidebar with one native Workspace menu; it
    must not make any desk route disappear from that group or from the footer.
    Buyer cluster/About routes may sit in reader navigation instead of the menu.
    """
    problems = []
    reader = {"index.html", "picks.html", "compare.html", "categories/kitchen-appliances.html",
              "guides/buying-guide-air-fryers.html", "articles/index.html", "clusters.html", "about.html"}
    for href, _label, _sub in NAV:
        if "/" in href and href not in reader:
            continue
        if href not in reader and href not in DESK_NAV and href != "previous-passes.html":
            problems.append(f"{href}: in NAV but neither a reader route nor DESK_NAV")
    for rel, content in pages.items():
        if rel == "404.html":
            continue  # its separate guard requires absolute canonical routes
        foot = content[content.find('<footer class="site">'):]
        match = re.search(r'<nav class="workspace-links"[^>]*>(.*?)</nav>', content, re.S)
        workspace = match.group(1) if match else ""
        prefix = depth_prefix(rel)
        for href in DESK_NAV:
            target = f'href="{prefix}{href}"'
            if target not in foot:
                problems.append(f"{rel}: footer does not link {href}")
            if href not in reader and target not in workspace:
                problems.append(f"{rel}: Workspace does not link {href}")
    return problems


def check_sitemap_membership(pages):
    """The buyer-facing publication set must exist; admin pages are a separate surface."""
    required = set(PUBLIC_INDEX_PAGES)
    missing = sorted(required - set(pages))
    return [f"missing canonical buyer page: {rel}" for rel in missing]


def page_modified_date(rel):
    if rel.startswith("articles/") and rel != "articles/index.html":
        slug = Path(rel).stem
        article = ARTICLE_BY_SLUG.get(slug, {})
        return (article.get("modified_at") or article.get("modified_on") or article.get("sources_read") or ACCESSED)[:10]
    return PUBLICATION["updated"]


def check_publication_data(publication=None, suggestions=None):
    """Display copy, current states and reader routes share the same reviewed registers."""
    publication = PUBLICATION if publication is None else publication
    suggestions = SUGGESTIONS if suggestions is None else suggestions
    problems = []
    expected = {p['slug'] for p in PRODUCT_LIST}
    rows = publication.get('products') or []
    if len(rows) != len(expected) or {r.get('slug') for r in rows} != expected:
        problems.append('publication product cards must match the documented product routes exactly')
    for row in rows + (publication.get('thermometer_links') or []):
        for key in ('sources', 'check_sources', 'size_sources'):
            for sid in row.get(key) or []:
                if sid not in SRC_BY_ID:
                    problems.append('publication copy references unknown source '+str(sid))
    for row in publication.get('featured_guides') or []:
        if row.get('slug') not in ARTICLE_BY_SLUG:
            problems.append('featured guide is not in the canonical article register')
    if {r.get('id') for r in publication.get('thermometer_links') or []} != {'PI-04','PI-05'}:
        problems.append('thermometer shelf must retain both submitted link-note IDs')
    for row in suggestions.get('suggestions') or []:
        if row.get('current_state') not in {'complete','partial','gated','superseded','open'}:
            problems.append(str(row.get('id'))+': missing/invalid current implementation state')
        if not row.get('current_note') or not row.get('current_reviewed_on'):
            problems.append(str(row.get('id'))+': current state needs a note and a dated review')
    return problems


def main():
    publication_problems = check_publication_data()
    if publication_problems:
        raise SystemExit('BUILD FAILED — publication state/route drift:\n  ' + '\n  '.join(publication_problems))
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "style.css").write_text(CSS, encoding="utf-8")
    (assets / "app.js").write_text(JS, encoding="utf-8")
    # The counter is always written to disk, so the code that would run is
    # reviewable in the repository. It is only *referenced* by a page when
    # data/config.json gives it an endpoint to send to.
    (assets / "analytics.js").write_text(ANALYTICS_JS, encoding="utf-8")
    build_figures()

    for d in ("products", "categories", "guides", "articles"):
        (ROOT / d).mkdir(exist_ok=True)

    pages = {}
    pages["index.html"] = page_index()
    for p in PRODUCT_LIST:
        pages[f"products/{p['slug']}.html"] = page_product(p)
    pages["categories/kitchen-appliances.html"] = page_category()
    pages["categories/cooking-thermometers.html"] = page_thermometers()
    pages["about.html"] = page_about()
    pages["compare.html"] = page_compare()
    pages["guides/buying-guide-air-fryers.html"] = page_guide()
    pages["articles/index.html"] = page_articles_index()
    pages["clusters.html"] = page_clusters()
    for _a in ARTICLES["articles"]:
        pages[f"articles/{_a['slug']}.html"] = page_article(_a)
    pages["data.html"] = page_data()
    pages["compliance.html"] = page_compliance()
    pages["flagged.html"] = page_flagged()
    pages["platform.html"] = page_platform()
    pages["executive-summary.html"] = page_exec()
    pages["reverification.html"] = page_reverification()
    pages["pass10.html"] = page_pass10()
    pages["figures.html"] = page_figures()
    pages["picks.html"] = page_picks()
    pages["decisions.html"] = page_decisions()
    pages["handover.html"] = page_handover()
    pages["product-intent.html"] = page_intent()
    pages["measurement.html"] = page_measurement()
    pages["suggestions.html"] = page_suggestions()
    pages["decision-log.html"] = page_decision_log()
    pages["design-prompt.html"] = page_design_prompt()
    pages["questions.html"] = page_questions()
    pages["requirements.html"] = page_requirements()
    pages["topics.html"] = page_topics()
    pages["decision-gate.html"] = page_questions_alt()
    pages["marketing-directions.html"] = page_suggestions_alt()
    pages["previous-passes.html"] = page_previous_passes()
    pages["404.html"] = page_404()

    # Qualify affiliate anchors before the guards see them, and before anything is written.
    pages = {rel: qualify_affiliate_links(text) for rel, text in pages.items()}

    # build guards
    problems = check_rows_have_sources()
    if problems:
        raise SystemExit("BUILD FAILED — rows with values but no official source:\n  " + "\n  ".join(problems))
    conflict_problems = check_spec_source_conflicts()
    if conflict_problems:
        raise SystemExit("BUILD FAILED — a row cites a document that contradicts its own value:\n  "
                         + "\n  ".join(conflict_problems))
    missing = check_disclosure(list(pages.items()))
    if missing:
        raise SystemExit("BUILD FAILED — pages missing the required disclosure: " + ", ".join(missing))
    article_problems = check_articles()
    if article_problems:
        raise SystemExit("BUILD FAILED — article cites an unregistered source or states an "
                         "unpublished value:\n  " + "\n  ".join(article_problems))
    decision_problems = check_decision_data()
    if decision_problems:
        raise SystemExit("BUILD FAILED — decision data no longer matches the official table:\n  "
                         + "\n  ".join(decision_problems))
    voice_problems = check_article_voice()
    if voice_problems:
        raise SystemExit("BUILD FAILED — article violates the house voice rule:\n  "
                         + "\n  ".join(voice_problems))
    article_page_problems = check_article_pages(pages)
    if article_page_problems:
        raise SystemExit("BUILD FAILED — article page violated a disclosure/claims rule:\n  "
                         + "\n  ".join(article_page_problems))
    legacy_pointer_problems = check_legacy_flag_pointers(pages)
    if legacy_pointer_problems:
        raise SystemExit("BUILD FAILED — a page points a reader at a legacy-register flag id "
                         "that the Flagged page does not render:\n  "
                         + "\n  ".join(legacy_pointer_problems))
    flag_id_problems = check_flag_ids_unique()
    if flag_id_problems:
        raise SystemExit("BUILD FAILED — flag register integrity:\n  " + "\n  ".join(flag_id_problems))
    flag_count_problems = check_flag_count_matches_page()
    if flag_count_problems:
        raise SystemExit("BUILD FAILED — landing-page total disagrees with the published "
                         "register:\n  " + "\n  ".join(flag_count_problems))
    visual_problems = check_callout_states_and_table_wraps(pages)
    if visual_problems:
        raise SystemExit("BUILD FAILED — rendered page would not display as designed:\n  "
                         + "\n  ".join(visual_problems))
    fragment_problems = check_internal_fragments(pages)
    if fragment_problems:
        raise SystemExit("BUILD FAILED — an in-page link points at an element that is not "
                         "rendered:\n  " + "\n  ".join(fragment_problems))
    ref_problems = check_question_block_refs()
    if ref_problems:
        raise SystemExit("BUILD FAILED — decision-layer cross-reference:\n  " + "\n  ".join(ref_problems))
    preamble_problems = check_register_preambles()
    if preamble_problems:
        raise SystemExit("BUILD FAILED — register preamble repeats itself:\n  " + "\n  ".join(preamble_problems))
    duplicate_problems = check_register_duplicates()
    if duplicate_problems:
        raise SystemExit("BUILD FAILED — register carries duplicated content (flag F64):\n  "
                         + "\n  ".join(duplicate_problems))
    cluster_problems = check_clusters(generated=pages.keys())
    if cluster_problems:
        raise SystemExit("BUILD FAILED - the cluster map and the article set disagree:\n  " + "\n  ".join(cluster_problems))
    analytics_problems = check_analytics_consistency(pages)
    if analytics_problems:
        raise SystemExit("BUILD FAILED - measurement/privacy consistency:\n  " + "\n  ".join(analytics_problems))
    price_problems = check_no_price_tracking(pages)
    if price_problems:
        raise SystemExit("BUILD FAILED — Prohibited feature (Program Policies 6(y)):\n  "
                         + "\n  ".join(price_problems))
    seo_problems = check_seo_metadata(pages)
    if seo_problems:
        raise SystemExit("BUILD FAILED - SEO/sharing metadata:\n  " + "\n  ".join(seo_problems))
    affiliate_problems = check_affiliate_link_qualification(pages)
    if affiliate_problems:
        raise SystemExit("BUILD FAILED - unqualified affiliate links (Google spam policies, "
                         "S30/S31):\n  " + "\n  ".join(affiliate_problems))
    linkcount_problems = check_submitted_link_count(pages)
    if linkcount_problems:
        raise SystemExit("BUILD FAILED — a present-tense page asserts a link count the register "
                         "contradicts (F82):\n  " + "\n  ".join(linkcount_problems))
    contract_problems = check_intent_measurement_contract(pages)
    if contract_problems:
        raise SystemExit("BUILD FAILED - product-intent or analytics contract:\n  "
                         + "\n  ".join(contract_problems))
    anchor_problems = check_flag_anchor_labels(pages)
    if anchor_problems:
        raise SystemExit("BUILD FAILED — a flag link opens a different flag (F92):\n  "
                         + "\n  ".join(anchor_problems[:20]))
    desk_problems = check_desk_nav(pages)
    if desk_problems:
        raise SystemExit("BUILD FAILED — a dashboard surface is unreachable:\n  "
                         + "\n  ".join(desk_problems[:20]))
    sitemap_problems = check_sitemap_membership(pages)
    if sitemap_problems:
        raise SystemExit("BUILD FAILED - canonical sitemap membership:\n  "
                         + "\n  ".join(sitemap_problems))
    req_path_problems = check_requirement_paths(generated=pages.keys())
    if req_path_problems:
        raise SystemExit("BUILD FAILED - requirements register cites paths that do not exist:\n  "
                         + "\n  ".join(req_path_problems))
    token_problems = check_requirement_tokens(pages)
    if token_problems:
        raise SystemExit("BUILD FAILED — an unresolved count token reached a published page:\n  "
                         + "\n  ".join(token_problems))
    unsourced_rows = check_row_sources(pages)
    if unsourced_rows:
        raise SystemExit("BUILD FAILED — table rows with no official source link (cite a registered "
                         "source or an existing exact-file record in this repo on GitHub):\n  "
                         + "\n  ".join(unsourced_rows))

    dangling_ids = check_register_cross_references(pages)
    if dangling_ids:
        raise SystemExit("BUILD FAILED — a published page points at an id that does not exist in any "
                         "register:\n  " + "\n  ".join(dangling_ids))

    orphan_pages = check_no_orphan_pages(pages)
    if orphan_pages:
        raise SystemExit("BUILD FAILED — HTML on disk that this build does not generate "
                         "(flag F74):\n  " + "\n  ".join(orphan_pages))

    for rel, text in pages.items():
        # Page bodies are authored with ../ prefixes so they can be reused at any
        # depth. Root-level pages must not carry that prefix.
        if "/" not in rel:
            text = text.replace('href="../', 'href="').replace('src="../', 'src="')
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")

    total_bytes = sum(len(t) for t in pages.values())
    print(f"built {len(pages)} pages ({total_bytes/1024:.0f} KB of HTML)")
    for rel in sorted(pages):
        print(f"  {rel}")

    # ---- SEO plumbing: one canonical buyer publication ---------------------
    # The root sitemap contains only buyer-facing publication pages. Owner workspaces,
    # verification registers, dashboards and the 404 page remain reachable by direct
    # navigation but are noindex and excluded. The separate historical annexes are not
    # generated into this sitemap.
    base = "https://kanlerxz87-cyber.github.io/Zone1/"
    indexable = sorted(rel for rel in pages if is_indexable_page(rel))
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + base + "sitemap.xml\n",
        encoding="utf-8")
    # <lastmod> carries the date the published values were last re-read against their
    # official sources (REVERIFIED), not the date the file was written. Added
    # 2026-11-15 (arena/88bb2db6) so crawlers get a real content-change signal.
    lastmod = REVERIFIED or ACCESSED
    locs = "".join(
        f"  <url><loc>{base}{'' if rel == 'index.html' else rel}</loc>"
        f"<lastmod>{page_modified_date(rel)}</lastmod></url>\n"
        for rel in indexable
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + locs + "</urlset>\n",
        encoding="utf-8")
    print(f"wrote robots.txt + sitemap.xml ({len(indexable)} urls)")

    # ---- additive (arena/8874422b-zone1, 2026-11-16): RSS feed of the article set --
    # The brief asks the site to earn organic traffic; a static site with a growing
    # article set should give readers (and aggregators) a way to follow it without an
    # account, a script or a cookie — the same no-data posture the footer declares under
    # Program Policies §3(e). The feed is generated from data/articles.json, the same
    # register that renders articles/index.html, so the two cannot drift. The fixed
    # editorial-update stamp sets channel freshness; unknown publication dates are omitted
    # rather than invented from a source-access date. The CI gate asserts reproducibility.
    import datetime as _feed_dt
    _feed_link = base + "articles/index.html"
    _feed_stamp = _feed_dt.datetime.fromisoformat(PUBLICATION["updated_at_utc"].replace("Z", "+00:00"))
    _feed_date = format_datetime(_feed_stamp)
    _items = []
    for _a in ARTICLES["articles"]:
        _a_url = base + f"articles/{_a['slug']}.html"
        _items.append(
            "    <item>\n"
            f"      <title>{e(_a['title'])}</title>\n"
            f"      <link>{e(_a_url)}</link>\n"
            f"      <guid isPermaLink=\"true\">{e(_a_url)}</guid>\n"
            f"      <description>{e(_a['standfirst'])}</description>\n"
            f"      <category>{e(_a['kind'])}</category>\n" +
            (f"      <pubDate>{format_datetime(_feed_dt.datetime.fromisoformat(_a['published_at_utc'].replace('Z', '+00:00')))}</pubDate>\n" if _a.get("published_at_utc") else "") +
            "    </item>\n")
    (ROOT / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{e(SITE_NAME)} — sourced air-fryer articles</title>\n"
        f"    <link>{e(_feed_link)}</link>\n"
        "    <description>Documentation-based air-fryer buying guides. Every factual "
        "sentence cites the manufacturer page or owner's manual it came from; no "
        "hands-on testing is claimed and no Amazon price or rating is published.</description>\n"
        "    <language>en-us</language>\n"
        f"    <lastBuildDate>{_feed_date}</lastBuildDate>\n"
        f"    <atom:link href=\"{e(base)}feed.xml\" rel=\"self\" type=\"application/rss+xml\" />\n"
        + "".join(_items)
        + "  </channel>\n</rss>\n",
        encoding="utf-8")
    print(f"wrote feed.xml ({len(ARTICLES['articles'])} items)")


if __name__ == "__main__":
    main()
