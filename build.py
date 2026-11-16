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
from urllib.parse import quote_plus
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
SITE_NAME = "Zone1 Kitchen"
SITE_TAGLINE = "Air-fryer decisions, backed by sources"
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
        "An independent, documentation-based air-fryer buying guide. Every specification "
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

# Decision layer (added 2026-11-15, arena/3ddfa50e). Two registers that exist to be reviewed
# rather than acted on: the suggestions queue and the open-questions register. Both are
# generated from JSON so a reviewer edits data, never a template.
DECISION = load("decision.json")
SUGGESTIONS = load("suggestions.json")
QUESTIONS = load("questions.json")
SUG_BY_ID = {s["id"]: s for s in SUGGESTIONS["suggestions"]}
# Design/content/traffic suggestion layer (added 2026-11-15, arena/bf487400-zone1).
# The paste-ready design prompt plus the D/A/T/V/R registers, generated from JSON so the
# owner reviews data, never a template. Statuses describe the repository as built.
DESIGN_PROMPT = load("design-prompt.json")

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
    return {
        "@type": "Article",
        "@id": url + "#article",
        "headline": a["title"],
        "description": a["standfirst"],
        "articleSection": a["kind"],
        "wordCount": None,
        "inLanguage": "en-US",
        "datePublished": ARTICLES.get("accessed", ""),
        "dateModified": ARTICLES.get("updated", ""),
        "author": {"@id": SITE_URL + "/#organization"},
        "publisher": {"@id": SITE_URL + "/#organization"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "image": OG_IMAGE,
        "url": url,
        "isAccessibleForFree": True,
    }


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
    ("picks.html", "This week's picks", "Three products, three jobs, one decision rule"),
    ("decisions.html", "Decisions & handover", "Niche, traffic, measurement, and the five things only you can do"),
    ("categories/kitchen-appliances.html", "Category: Kitchen", "All tracked products in one category"),
    ("compare.html", "Comparison", "Verified-only side-by-side matrix"),
    ("guides/buying-guide-air-fryers.html", "Buying guide", "How to choose a form factor"),
    ("articles/index.html", "Articles", "Sourced reads — comparisons, explainers, policy"),
    ("data.html", "Full dataset", "Every field, value, source and gap"),
    ("platform.html", "Platform blueprint", "The automation and compliance design"),
    ("compliance.html", "Compliance", "Program rules, quoted, with sources"),
    ("flagged.html", "Flagged for review", "Unverified values and irregularities"),
    ("suggestions.html", "Suggestions", "Review site improvements before implementation"),
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

CSS = r"""
:root{
  --bg:#f6f7f9; --panel:#ffffff; --ink:#111827; --muted:#6b7280; --line:#e5e7eb;
  --brand:#0f766e; --brand-soft:#ccfbf1; --warn:#b45309; --warn-soft:#fef3c7;
  --bad:#b91c1c; --bad-soft:#fee2e2; --ok:#15803d; --ok-soft:#dcfce7;
  --shadow:0 1px 2px rgba(16,24,40,.06),0 1px 3px rgba(16,24,40,.10);
  --radius:12px; --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,monospace;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
a{color:var(--brand); text-decoration:none}
a:hover{text-decoration:underline}
code{font-family:var(--mono); font-size:.9em; background:#eef2f4; padding:.1em .35em; border-radius:4px}

/* disclosure bar — required on every page */
.disclosure-bar{
  background:#0b3b36; color:#d7fffb; font-size:.82rem;
  padding:.5rem 1.25rem; text-align:center; letter-spacing:.01em;
}
.disclosure-bar strong{color:#fff}

/* top bar */
.topbar{
  position:sticky; top:0; z-index:20; display:flex; align-items:center; gap:1rem;
  background:var(--panel); border-bottom:1px solid var(--line);
  padding:.7rem 1.25rem; box-shadow:var(--shadow);
}
.brand{display:flex; align-items:center; gap:.6rem; font-weight:700; letter-spacing:-.01em}
.brand .mark{
  width:30px; height:30px; border-radius:9px; display:grid; place-items:center;
  background:linear-gradient(135deg,#0f766e,#0ea5a4); color:#fff; font-size:.9rem; font-weight:800;
}
.brand small{display:block; font-weight:500; color:var(--muted); font-size:.72rem; letter-spacing:.02em}
.topbar .spacer{flex:1}
.topbar .meta{color:var(--muted); font-size:.78rem; font-family:var(--mono)}
.navtoggle{display:none; border:1px solid var(--line); background:#fff; border-radius:8px; padding:.4rem .6rem; font:inherit; cursor:pointer}

/* shell */
.shell{display:grid; grid-template-columns:250px minmax(0,1fr); gap:1.25rem; max-width:1400px; margin:0 auto; padding:1.25rem}
.sidebar{position:sticky; top:74px; align-self:start}
.sidebar .group{margin-bottom:1.1rem}
.sidebar .group h4{
  margin:0 0 .4rem .6rem; font-size:.7rem; text-transform:uppercase;
  letter-spacing:.09em; color:#9ca3af; font-weight:700;
}
.sidebar a{
  display:block; padding:.45rem .6rem; border-radius:8px; color:#374151;
  font-size:.9rem; border:1px solid transparent;
}
.sidebar a:hover{background:#eef2f4; text-decoration:none}
.sidebar a.active{background:var(--brand-soft); border-color:#99f6e4; color:#0b3b36; font-weight:600}
.sidebar a .sub{display:block; font-size:.74rem; color:var(--muted); font-weight:400}
.sidebar a.active .sub{color:#0f766e}

main{min-width:0; padding-bottom:3rem}
.crumbs{font-size:.8rem; color:var(--muted); margin:0 0 .5rem}
.crumbs a{color:var(--muted)}
h1{font-size:clamp(1.5rem,2.6vw,2.05rem); line-height:1.2; margin:.1rem 0 .5rem; letter-spacing:-.02em}
h2{font-size:1.18rem; margin:2rem 0 .6rem; letter-spacing:-.01em}
h3{font-size:1rem; margin:1.4rem 0 .4rem}
.lede{font-size:1.02rem; color:#374151; max-width:74ch; margin:0 0 1rem}
.muted{color:var(--muted)}
.small{font-size:.85rem}
.tiny{font-size:.78rem}

/* cards */
.card{background:var(--panel); border:1px solid var(--line); border-radius:var(--radius); padding:1.1rem 1.2rem; box-shadow:var(--shadow); margin:0 0 1rem}
/* article layer */
.cardgrid{display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:1rem; margin:1.2rem 0}
.cardgrid .card{margin:0; display:flex; flex-direction:column; gap:.4rem; transition:border-color .15s, transform .15s}
.cardgrid .card:hover{border-color:var(--brand); transform:translateY(-1px); text-decoration:none}
.kicker{display:inline-block; font-size:.7rem; letter-spacing:.09em; text-transform:uppercase; font-weight:700; color:var(--brand); margin:0 0 .2rem}
.cardtitle{font-size:1.06rem; font-weight:700; line-height:1.3; color:var(--ink)}
.cardtext{font-size:.9rem; color:#4b5563; line-height:1.5}
code.specval{background:var(--brand-soft); color:#0b3b36; border:1px solid #99f6e4; padding:.05em .4em; border-radius:5px; font-size:.86em; white-space:normal}
.card.tight{padding:.85rem 1rem}
.grid{display:grid; gap:1rem}
.grid-3{grid-template-columns:repeat(auto-fit,minmax(250px,1fr))}
.grid-2{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.grid-4{grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}

/* stat tiles */
.stat{background:var(--panel); border:1px solid var(--line); border-radius:var(--radius); padding:.9rem 1rem; box-shadow:var(--shadow)}
.stat .n{font-size:1.75rem; font-weight:800; letter-spacing:-.03em; line-height:1.1}
.stat .l{font-size:.76rem; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); font-weight:700; margin-top:.15rem}
.stat .h{font-size:.78rem; color:var(--muted); margin-top:.35rem}
.stat.warn .n{color:var(--warn)}
.stat.ok .n{color:var(--ok)}
.stat.bad .n{color:var(--bad)}
.stat.brand .n{color:var(--brand)}

/* tables */
.tablewrap{overflow-x:auto; border:1px solid var(--line); border-radius:var(--radius); background:var(--panel); box-shadow:var(--shadow)}
table{border-collapse:collapse; width:100%; font-size:.875rem}
caption{caption-side:top; text-align:left; padding:.75rem 1rem .25rem; font-weight:700; font-size:.9rem}
th,td{padding:.6rem .8rem; text-align:left; vertical-align:top; border-bottom:1px solid var(--line)}
thead th{
  background:#f3f5f7; font-size:.72rem; text-transform:uppercase; letter-spacing:.06em;
  color:#4b5563; font-weight:700; white-space:nowrap; position:sticky; top:0;
}
tbody tr:nth-child(even){background:#fbfcfd}
tbody tr:hover{background:#f0fdfa}
td.num{font-variant-numeric:tabular-nums; white-space:nowrap}
.blank{color:#9ca3af; font-style:italic}

/* pills + badges */
.pill{display:inline-block; padding:.12rem .5rem; border-radius:999px; font-size:.72rem; font-weight:700; letter-spacing:.02em; white-space:nowrap}
.pill-ok{background:var(--ok-soft); color:#14532d}
.pill-warn{background:var(--warn-soft); color:#78350f}
.pill-bad{background:var(--bad-soft); color:#7f1d1d}
.pill-info{background:#e0f2fe; color:#075985}
.src{
  display:inline-block; font-family:var(--mono); font-size:.7rem; font-weight:700;
  background:#eef7f6; color:#0b5a54; border:1px solid #cbe8e5; border-radius:5px;
  padding:.05rem .35rem; margin-right:.15rem;
}
.src:hover{background:#d9f2ef; text-decoration:none}
.src-none{background:#fef3c7; color:#78350f; border-color:#fde68a}
.src-bad{background:#fee2e2; color:#7f1d1d; border-color:#fecaca}

/* CTA */
.cta-row{display:flex; flex-wrap:wrap; align-items:center; gap:.6rem; margin:.8rem 0 .4rem}
.btn{
  display:inline-flex; align-items:center; gap:.45rem; background:var(--brand); color:#fff;
  padding:.6rem 1rem; border-radius:9px; font-weight:650; font-size:.9rem; border:1px solid #0b5f59;
}
.btn:hover{background:#0b5f59; text-decoration:none; color:#fff}
.btn-ghost{background:#fff; color:#0b3b36; border:1px solid var(--line)}
.btn-ghost:hover{background:#f3f5f7; color:#0b3b36}
.paid-tag{
  font-size:.68rem; font-weight:800; letter-spacing:.06em; text-transform:uppercase;
  background:var(--warn-soft); color:#78350f; border:1px solid #fde68a; border-radius:5px; padding:.12rem .4rem;
}
.cta-note{font-size:.78rem; color:var(--muted); margin:0 0 .8rem; max-width:70ch}

/* callouts */
.callout{border-left:4px solid var(--warn); background:var(--warn-soft); padding:.8rem 1rem; border-radius:0 10px 10px 0; margin:1rem 0}
.callout.bad{border-color:var(--bad); background:var(--bad-soft)}
.callout.ok{border-color:var(--ok); background:var(--ok-soft)}
.callout.info{border-color:var(--brand); background:#ecfdfa}
.callout p:last-child{margin-bottom:0}
.callout strong{display:block; margin-bottom:.2rem}

blockquote{margin:.8rem 0; padding:.7rem 1rem; border-left:3px solid #cbd5e1; background:#f8fafc; color:#334155; font-size:.92rem}
blockquote cite{display:block; margin-top:.4rem; font-size:.78rem; color:var(--muted); font-style:normal}

ul.tight,ol.tight{margin:.4rem 0 .8rem; padding-left:1.2rem}
ul.tight li,ol.tight li{margin:.25rem 0}

/* product cards */
.pcard{display:flex; flex-direction:column; gap:.5rem}
.pcard .rank{font-size:.7rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--brand)}
.pcard h3{margin:0; font-size:1.02rem}
.pcard .facts{display:flex; flex-wrap:wrap; gap:.35rem}
.chip{font-size:.74rem; background:#f1f5f9; border:1px solid var(--line); border-radius:6px; padding:.1rem .45rem; color:#334155}

/* calculator */
.calc{display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:.75rem; align-items:end}
.calc label{display:block; font-size:.78rem; font-weight:700; color:#374151; margin-bottom:.25rem}
.calc input,.calc select{
  width:100%; padding:.5rem .6rem; border:1px solid #cbd5e1; border-radius:8px;
  font:inherit; font-size:.9rem; background:#fff;
}
.calc .out{background:#0b3b36; color:#d7fffb; border-radius:10px; padding:.8rem 1rem; text-align:center}
.calc .out b{display:block; font-size:1.5rem; color:#fff; letter-spacing:-.02em}
.calc .out span{font-size:.74rem; text-transform:uppercase; letter-spacing:.07em}

footer.site{border-top:1px solid var(--line); background:var(--panel); padding:2rem 1.25rem; margin-top:2rem}
footer.site .inner{max-width:1400px; margin:0 auto; display:grid; gap:1.25rem; grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
footer.site h2{margin:0 0 .4rem; font-size:.78rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#6b7280}
footer.site p,footer.site li{font-size:.82rem; color:#4b5563}
footer.site ul{list-style:none; margin:0; padding:0}
footer.site li{margin:.2rem 0}
.legal{max-width:1400px; margin:1.25rem auto 0; padding-top:1rem; border-top:1px solid var(--line); font-size:.76rem; color:var(--muted)}

@media (max-width:960px){
  .shell{grid-template-columns:1fr; padding:.9rem}
  .sidebar{position:static; display:none}
  .sidebar.open{display:block}
  .navtoggle{display:inline-block}
  .topbar .meta{display:none}
  th,td{padding:.5rem .6rem}
}
@media print{
  .topbar,.sidebar,.navtoggle,.cta-row{display:none}
  body{background:#fff}
  .card,.tablewrap,.stat{box-shadow:none}
}
/* ---- decision layer: suggestions + open questions (2026-11-15) ---- */
.chip{display:inline-block; padding:.05rem .4rem; border:1px solid var(--line); border-radius:999px;
  font-size:.7rem; font-weight:700; color:var(--muted); background:#f9fafb; font-family:var(--mono)}
.sug,.qcard{background:var(--panel); border:1px solid var(--line); border-radius:var(--radius);
  padding:1rem 1.15rem; margin:0 0 1rem; box-shadow:var(--shadow)}
.sug-head{display:flex; gap:1rem; align-items:flex-start; justify-content:space-between; margin-bottom:.4rem}
.sug-head h3{margin:.1rem 0 0; font-size:1.02rem; line-height:1.35}
.score{flex:0 0 auto; display:grid; place-items:center; min-width:56px; padding:.35rem .5rem;
  border-radius:10px; background:var(--brand-soft); border:1px solid #99f6e4; color:#0b3b36}
.score strong{font-size:1.15rem; line-height:1}
.score span{font-size:.62rem; text-transform:uppercase; letter-spacing:.06em; font-weight:700}
.sug p,.qcard p{margin:.45rem 0}
.evidence{background:#f9fafb; border:1px dashed var(--line); border-radius:9px;
  padding:.5rem .65rem; margin:.6rem 0; font-size:.82rem}
.src-link{display:inline-block; margin:.12rem .55rem .12rem 0; color:var(--brand); font-size:.82rem}
/* paste-ready design prompt block (design-prompt.html) */
.prompt-block{
  display:block; white-space:pre-wrap; word-break:break-word; overflow-wrap:anywhere;
  background:#0b3b36; color:#e7f7f2; padding:1.15rem 1.3rem; margin:0 0 .8rem;
  border-radius:12px; box-shadow:var(--shadow);
  font:0.79rem/1.6 var(--mono); tab-size:2;
}
.label{margin:.7rem 0 .3rem; font-size:.7rem; text-transform:uppercase; letter-spacing:.08em;
  color:#9ca3af; font-weight:700}
.paths{margin:.2rem 0 .6rem; padding-left:1.3rem}
.paths li{margin:0 0 .6rem}
.paths li strong{font-size:.9rem}
.rec{margin:.6rem 0; padding:.55rem .7rem; background:var(--ok-soft);
  border:1px solid #bbf7d0; border-radius:9px; font-size:.88rem}
.twocol{display:grid; grid-template-columns:1fr 1fr; gap:1rem}
ul.tight{margin:.2rem 0 .6rem; padding-left:1.15rem}
ul.tight li{margin:.25rem 0; font-size:.86rem}
@media (max-width:820px){.twocol{grid-template-columns:1fr}}

/* Editorial refresh: warm, quiet typography instead of a generic admin dashboard. */
:root{
  --bg:#f4f2eb; --panel:#fffefa; --ink:#202820; --muted:#626b62; --line:#deded2;
  --brand:#245746; --brand-soft:#e5eee6; --warn:#92531e; --warn-soft:#fff1d8;
  --bad:#9c4437; --bad-soft:#f8e8e3; --ok:#2f6745; --ok-soft:#e4f0e6;
  --shadow:0 7px 24px rgba(32,40,32,.055); --radius:15px;
  --accent:#b75d3c; --serif:Georgia,"Times New Roman",serif;
}
body{background:var(--bg); color:var(--ink); line-height:1.65}
.skip-link{position:absolute; z-index:100; top:-5rem; left:1rem; padding:.55rem .85rem; background:#fffefa; color:#173f32; border:2px solid #245746; border-radius:8px; font-weight:700}
.skip-link:focus{top:1rem}
a{color:var(--brand); text-underline-offset:.18em}
a:hover{color:#173f32}
:focus-visible{outline:3px solid #ca784d; outline-offset:3px; border-radius:4px}
.disclosure-bar{background:#173f34; color:#f2f4ec; padding:.58rem 1.25rem; font-size:.8rem}
.topbar{background:#fffefa; border-bottom-color:#deded2; box-shadow:none; padding:.8rem 1.4rem}
.brand .mark{background:#245746; border-radius:50%; width:34px; height:34px}
.brand small{font-size:.68rem; letter-spacing:.045em; text-transform:uppercase; color:#677168}
.shell{max-width:1500px; grid-template-columns:230px minmax(0,1fr); gap:1.65rem; padding:1.5rem}
.sidebar .group h4{color:#8a8d82; letter-spacing:.12em}
.sidebar a{color:#39453b; padding:.48rem .7rem}
.sidebar a.active{background:#e4eee5; border-color:#c9d9ca; color:#1d4a39}
main{padding-bottom:4rem}
h1,h2,h3{font-family:var(--serif)}
h1{font-size:clamp(2rem,3.3vw,2.7rem); font-weight:500; letter-spacing:-.035em; line-height:1.08}
h2{font-size:clamp(1.4rem,2.25vw,1.9rem); font-weight:500; letter-spacing:-.025em; margin-top:2.35rem}
h3{font-size:1.12rem; font-weight:600}
.lede{font-size:1.08rem; color:#465348}
.card,.stat,.sug,.qcard{background:var(--panel); border-color:var(--line); box-shadow:var(--shadow); border-radius:var(--radius)}
.card{padding:1.25rem 1.35rem}
.tablewrap{box-shadow:none; border-color:#d8d9ce; border-radius:13px}
table{font-size:.86rem}
thead th{background:#e9ece4; color:#435044}
tbody tr:nth-child(even){background:#faf9f4}
tbody tr:hover{background:#f1f4ed}
.btn{background:#245746; border-color:#194635; border-radius:999px; padding:.7rem 1.2rem; font-weight:700}
.btn:hover{background:#173f32}
.btn-ghost{background:transparent; color:#245746; border-color:#aab8aa}
.btn-ghost:hover{background:#e8eee7; color:#173f32}
.paid-tag{border-radius:999px; letter-spacing:.035em}
.callout{border-radius:0 12px 12px 0}
.callout.info{background:#e8efe7}
.cta-note{max-width:78ch}

.editorial-hero{
  position:relative; isolation:isolate; overflow:hidden; display:grid;
  grid-template-columns:minmax(0,1.15fr) minmax(310px,.85fr); gap:clamp(1.5rem,3.5vw,3rem);
  align-items:stretch; margin:.1rem 0 1.25rem; padding:clamp(1.5rem,4vw,3.5rem);
  border:1px solid #d8ddcf; border-radius:26px; background:#eceee2;
}
.editorial-hero:before{content:""; position:absolute; z-index:-1; width:28rem; height:28rem; right:20%; top:-22rem; border:1px solid rgba(36,87,70,.14); border-radius:50%; box-shadow:0 0 0 35px rgba(36,87,70,.035),0 0 0 70px rgba(36,87,70,.025)}
.hero-copy{align-self:center; max-width:650px}
.hero-eyebrow,.section-eyebrow{margin:0 0 .75rem; color:var(--accent); font-size:.7rem; font-weight:800; letter-spacing:.15em; text-transform:uppercase}
.hero-eyebrow span{color:#929487; padding:0 .35rem}
.hero-title{max-width:11ch; margin:.2rem 0 1rem; color:#1d3025; font:500 clamp(3rem,5.7vw,5.25rem)/.96 var(--serif); letter-spacing:-.065em}
.hero-copy .lede{max-width:58ch; margin:0; font-size:1.08rem}
.hero-actions{display:flex; flex-wrap:wrap; gap:.7rem; margin:1.5rem 0 .5rem}
.hero-footnote{margin:.65rem 0 0; color:#606b5f; font-size:.75rem; letter-spacing:.035em}
.hero-panel{display:flex; flex-direction:column; justify-content:center; min-width:0; padding:1.35rem 1.45rem; color:#f6f4eb; background:#214a3c; border-radius:19px; box-shadow:0 12px 30px rgba(27,61,49,.12)}
.hero-panel-kicker{display:flex; justify-content:space-between; gap:1rem; margin:0; color:#e5b580; font-size:.68rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase}
.hero-panel-kicker span{color:#d0dace; letter-spacing:.08em}
.hero-panel h2{margin:.45rem 0 .9rem; color:#fffdf6; font-size:1.8rem; line-height:1.1}
.hero-choice{display:grid; grid-template-columns:30px minmax(0,1fr) 18px; gap:.55rem; align-items:center; padding:.85rem 0; color:#f6f4eb; border-top:1px solid rgba(239,244,231,.19)}
.hero-choice:hover{border-color:rgba(239,244,231,.55)}
.hero-index{color:#e5b580; font-family:var(--mono); font-size:.76rem}
.hero-choice-copy{display:flex; flex-direction:column; min-width:0}
.hero-choice-copy>a{color:#fffdf6; text-decoration:none}
.hero-choice-copy>a:hover{text-decoration:underline; text-underline-offset:.2em}
.hero-choice-copy strong{color:#fffdf6; font-size:.91rem; line-height:1.3}
.hero-choice-copy small{margin-top:.18rem; color:#d4dfd3; font-size:.72rem}
.hero-panel .src{margin:.05rem .1rem; background:#e4efe5; border-color:#d0e3d2; color:#204a39}
.hero-arrow{color:#e5b580; text-align:right}
.link-status{margin:1.15rem 0 1.5rem; background:#fff2dd; border-left-color:#c87539; border-color:#efd6b2; border-left-width:5px; padding:1rem 1.15rem}
.link-status-heading{display:flex; align-items:center; flex-wrap:wrap; gap:.65rem; margin:0 0 .3rem}
.link-status-heading strong{display:inline; margin:0; color:#48331f}
.link-status p{margin:.35rem 0 0}
.method-strip{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; padding:1.15rem 0; border-top:1px solid #deded2; border-bottom:1px solid #deded2}
.method-strip>div{display:grid; grid-template-columns:30px 1fr; column-gap:.55rem; align-items:start}
.method-number{grid-row:span 2; color:var(--accent); font:700 .75rem/1.6 var(--mono)}
.method-strip strong{font-size:.86rem; line-height:1.35}
.method-strip p{margin:.2rem 0 0; color:var(--muted); font-size:.78rem; line-height:1.45}
.section-heading{max-width:700px; margin:2.4rem 0 1rem}
.section-heading .section-eyebrow{margin-bottom:.25rem}
.section-heading h2{margin:.1rem 0 .4rem}
.section-heading p:last-child{margin:.2rem 0}
.decision-grid{align-items:stretch}
.decision-card{display:flex; flex-direction:column; min-height:235px; padding:1.25rem 1.35rem}
.decision-label,.product-type{margin:0; color:var(--accent); font-size:.68rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase}
.decision-card h3{margin:.25rem 0 .45rem; font-size:1.23rem; line-height:1.2}
.decision-card p.small{margin:.1rem 0 .85rem; color:#515c52}
.decision-card>a{margin-top:auto; font-size:.87rem; font-weight:700}
.pcard{gap:.55rem; min-height:270px}
.pcard h3{margin:.05rem 0; font-size:1.3rem; line-height:1.2}
.pcard .product-name{margin:0; line-height:1.45}
.product-fact{display:grid; gap:.1rem; padding:.7rem 0; border-top:1px solid var(--line); border-bottom:1px solid var(--line)}
.product-fact>span:first-child{color:var(--muted); font-size:.7rem; letter-spacing:.06em; text-transform:uppercase}
.product-fact>strong{font-family:var(--serif); font-size:1.22rem; font-weight:500}
.product-match{display:flex; align-items:center; flex-wrap:wrap; gap:.4rem; margin:.1rem 0}
.product-match .pill{white-space:normal}
.archive-panel{margin-top:1.5rem; padding:1.2rem 1.4rem; background:#ebece2; border:1px solid #d8ddcf; border-radius:16px}
.archive-panel .section-eyebrow{margin:0 0 .2rem}
.archive-panel h3{margin:.15rem 0 .35rem; font-size:1.35rem}
.archive-panel p{margin:.3rem 0}
.comparison-table td .tiny{margin-top:.3rem; line-height:1.4}
.comparison-table .src{margin:.05rem .1rem .05rem 0}
footer.site{background:#ebece5; border-top-color:#d8d9ce; margin-top:2.5rem}
footer.site .inner{max-width:1500px}
footer.site h2{color:#405548}
footer.site p,footer.site li{color:#59645a}
.legal{border-top-color:#d4d7cc}

@media (max-width:960px){
  .shell{grid-template-columns:1fr; padding:1rem}
  .sidebar{background:#fffefa; border:1px solid var(--line); border-radius:14px; padding:.6rem}
  .editorial-hero{grid-template-columns:minmax(0,1fr) minmax(290px,.8fr); padding:1.5rem}
  .hero-title{font-size:clamp(2.8rem,6vw,4rem)}
}
@media (max-width:760px){
  .editorial-hero{grid-template-columns:1fr; gap:1.25rem; border-radius:20px}
  .hero-title{max-width:12ch; font-size:clamp(3rem,12vw,4.4rem)}
  .hero-panel{padding:1.1rem 1.2rem}
  .method-strip{grid-template-columns:1fr; gap:.8rem}
}
@media (max-width:560px){
  .topbar{padding:.65rem .85rem}
  .brand small{max-width:180px; font-size:.62rem}
  .shell{padding:.75rem}
  .editorial-hero{padding:1.2rem}
  .hero-actions{align-items:stretch}
  .hero-actions .btn{justify-content:center; flex:1 1 100%}
  .link-status-heading{align-items:flex-start; flex-direction:column}
  .decision-card{min-height:0}
  table{font-size:.8rem}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important; transition:none!important}}

/* ===== 2026-11-15 (arena/792c279e): commercial + decision components ===== */
:root{ --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
       --accent:#245746; --accent-soft:#e3ece4; }

.picks-hero{position:relative}
.pick .pick-cta{margin-top:auto; display:inline-block; font-weight:700; font-size:.88rem}
.pick h3{font-family:var(--serif); font-weight:500; font-size:1.32rem; line-height:1.22; letter-spacing:-.01em}
.card.pick{border-color:#cfdacf}
.card.pick:hover{border-color:var(--accent)}

.callout{background:var(--panel); border:1px solid var(--line); border-left:4px solid var(--accent);
  border-radius:10px; padding:.9rem 1.1rem; margin:1.1rem 0; box-shadow:var(--shadow); font-size:.94rem}
.callout.trust{border-left-color:#0f766e; background:#f4fbf8}
/* Added 2026-11-16 (arena/2e346d24): `.note` (13 uses) and `.warn` (33 uses) had no rule at
   all, so 46 callouts on the generated pages rendered as uncoloured boxes with no visual
   difference between "for your information" and "this could be wrong". */
.callout.note{border-left-color:var(--brand); background:var(--brand-soft)}
.callout.warn{border-left-color:var(--warn); background:var(--warn-soft)}
/* Same pass: the four register pages (topics, suggestions, questions, requirements) put wide
   tables directly in the flow. `.tablewrap` scrolls horizontally; without it those tables
   forced the whole page to scroll sideways at phone widths. */
.tablewrap table{margin:0; border:0}
.callout.bad{border-left-color:var(--bad); background:#fff6f6}
.callout.ok{border-left-color:var(--ok); background:#f5fbf6}

.channel{padding:1rem 1.15rem}
.channel-head{display:flex; align-items:center; gap:.55rem; flex-wrap:wrap; margin-bottom:.35rem}
.channel-head h3{margin:0; font-size:1.02rem; font-family:var(--serif); font-weight:600}
.channel ul{margin:.2rem 0 .5rem 1.1rem; padding:0}
.channel li{margin:.12rem 0}

.handover-item{border-left:4px solid var(--accent)}
.handover-head{display:flex; align-items:baseline; gap:.6rem; flex-wrap:wrap}
.handover-head h2{margin:0; font-family:var(--serif); font-weight:600; font-size:1.08rem; line-height:1.3; flex:1 1 60%}
.handover-num{font:800 .8rem/1 var(--mono); color:#fff; background:var(--accent); border-radius:6px; padding:.32rem .45rem}
.handover-meta{display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:.8rem; margin-top:.7rem;
  padding-top:.7rem; border-top:1px solid var(--line)}
.handover-meta .tiny{display:block; text-transform:uppercase; letter-spacing:.08em}

.article-head{max-width:74ch}
.article-body{max-width:74ch}
.article-body h2{font-family:var(--serif); font-weight:600; font-size:1.3rem; letter-spacing:-.01em; margin-top:2.1rem}
.article-body p:first-of-type{font-size:1.05rem}
.share{display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; margin:1.6rem 0 .5rem; padding-top:1rem; border-top:1px solid var(--line)}
.share a,.share button{display:inline-flex; align-items:center; gap:.35rem; border:1px solid var(--line);
  background:#fff; color:var(--ink); border-radius:999px; padding:.32rem .8rem; font:inherit; font-size:.8rem;
  cursor:pointer; text-decoration:none}
.share a:hover,.share button:hover{border-color:var(--accent); background:var(--accent-soft); text-decoration:none}
.share .label{font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); margin-right:.2rem}
.article-nav{display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:.8rem; margin:1.2rem 0}
.article-nav .card{display:block; margin:0}
.article-nav strong{font-size:.92rem; line-height:1.3}

.pulse{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:.7rem; margin:1.1rem 0}
.pulse .tile{background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:.75rem .85rem; box-shadow:var(--shadow)}
.pulse .tile b{display:block; font:800 1.35rem/1.1 var(--serif); letter-spacing:-.02em}
.pulse .tile span{display:block; font-size:.72rem; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); margin-top:.25rem}
.pulse .tile a{font-size:.78rem}
details.card summary{cursor:pointer; font-size:.9rem}

/* section rhythm on the buyer-facing pages */
.quick-guide{margin:1.8rem 0 .5rem}
.buyer-toc{display:flex; flex-wrap:wrap; gap:.45rem; margin:.9rem 0 1.4rem}
.buyer-toc a{font-size:.8rem; border:1px solid var(--line); background:#fff; border-radius:999px;
  padding:.28rem .7rem; color:#374151}
.buyer-toc a:hover{border-color:var(--accent); background:var(--accent-soft); text-decoration:none}
.article-card .cardtitle{font-family:var(--serif); font-weight:600}
@media (max-width:560px){ .handover-head h2{font-size:1rem} }

"""

JS = r"""
// copy-to-clipboard for article share rows (2026-11-15, arena/792c279e).
// Progressive: without JS the button does nothing and the URL is still in the address bar,
// so no functionality depends on it.
document.addEventListener('click', function (ev) {
  var c = ev.target.closest('.copylink');
  if (!c) return;
  var link = c.getAttribute('data-link') || location.href;
  var done = function () {
    var old = c.textContent;
    c.textContent = 'Copied';
    setTimeout(function () { c.textContent = old; }, 1600);
  };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(link).then(done, done);
  } else {
    var ta = document.createElement('textarea');
    ta.value = link; document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta); done();
  }
});

document.addEventListener('click', function (ev) {
  var t = ev.target.closest('.navtoggle');
  if (!t) return;
  var nav = document.getElementById(t.getAttribute('aria-controls'));
  if (!nav) return;
  var open = nav.classList.toggle('open');
  t.setAttribute('aria-expanded', open ? 'true' : 'false');
});

// revenue scenario calculator — arithmetic on two published inputs only
(function () {
  var form = document.getElementById('calc');
  if (!form) return;
  var fields = ['profit', 'price', 'rate', 'conv'];
  function num(id, d) { var v = parseFloat(document.getElementById(id).value); return isFinite(v) ? v : d; }
  function run() {
    var price = num('price', 0), rate = num('rate', 0) / 100,
        conv = num('conv', 0) / 100, clicks = num('clicks', 0);
    var commission = price * rate;
    var sales = clicks * conv;
    var revenue = sales * commission;
    document.getElementById('out-commission').textContent = '$' + commission.toFixed(2);
    document.getElementById('out-sales').textContent = sales.toFixed(1);
    document.getElementById('out-revenue').textContent = '$' + revenue.toFixed(2);
    document.getElementById('out-epc').textContent = '$' + (clicks > 0 ? revenue / clicks : 0).toFixed(3);
  }
  form.addEventListener('input', run);
  form.addEventListener('submit', function (e) { e.preventDefault(); run(); });
  run();
})();
"""


def layout(page_rel, title, body, active=None, description="", og_type="website",
           jsonld_blocks=None, og_image_alt=None):
    prefix = depth_prefix(page_rel)
    # Keyed by href, not by position: the sidebar used to index this list, so inserting a nav
    # entry silently moved every later group (caught 2026-11-15 when Suggestions and Open
    # questions were added and the Products group began rendering the Buying guide).
    nav_hrefs = [href for href, _label, _sub in NAV]
    if len(nav_hrefs) != len(set(nav_hrefs)):
        raise SystemExit("BUILD FAILED — duplicate navigation href")
    nav_html = {}
    for href, label, sub in NAV:
        cls = ' class="active"' if href == active else ""
        nav_html[href] = (
            f'<a href="{prefix}{href}"{cls}>{e(label)}<span class="sub">{e(sub)}</span></a>'
        )

    def N(href):
        return nav_html[href]
    # Entries that describe a *parallel* pass merged into this repo (a top-level directory
    # with its own data and source registry) are listed in NAV so the link checker covers
    # them, but the nav groups above only render fixed indices, so those entries were
    # reachable from no page at all. Surface them in the footer by prefix rather than by
    # index, so the next session that adds one needs no edit here.
    parallel = [
        (href, label, sub) for (href, label, sub) in NAV
        if "/" in href and not href.startswith(("products/", "categories/", "guides/", "assets/"))
    ]

    # product links under the category entry
    prod_nav = "".join(
        f'<a href="{prefix}products/{p["slug"]}.html">{e(p["short_name"])}'
        f'<span class="sub">candidate ASIN {e(p["asin"]["v"])} (unconfirmed)</span></a>'
        for p in PRODUCT_LIST
    )
    # Sidebar gets ONE entry. Every parallel build is catalogued, with its disagreements
    # named, on previous-passes.html.
    # The count used to be len(parallel), i.e. every NAV entry containing a "/" that was not
    # a product/category/guide/asset path. That set includes this site's own articles/index.html
    # hub, so the sidebar advertised "8 parallel builds" while the catalogue below it listed 7.
    # Caught 2026-11-15 (pass 9) by comparing the string with PARALLEL_BUILDS. Both numbers now
    # come from the catalogue, which is the thing the reader is being sent to read.
    more_nav = (
        '<div class="group"><h4>Archive</h4>'
        f'<a href="{prefix}previous-passes.html">Previous passes<span class="sub">'
        f'{len(PARALLEL_BUILDS)} parallel builds kept in this repo, catalogued</span></a></div>'
        if parallel else ""
    )
    desc = f'<meta name="description" content="{e(description)}">' if description else ""

    # Absolute URL of this page. The landing page canonicalises to the directory form
    # so that https://…/Zone1/ and https://…/Zone1/index.html are one URL, not two.
    canonical = SITE_URL + "/" if page_rel == "index.html" else page_url(page_rel)
    full_title = f"{title} · {SITE_NAME}"
    # Fall back to the page's own description for the social card; a link shared with
    # no text still gets a readable preview rather than an empty one.
    social_desc = description or f"{SITE_NAME} — {SITE_TAGLINE}."
    social_alt = og_image_alt or f"{SITE_NAME} — {SITE_TAGLINE}"
    ld = jsonld(jsonld_blocks)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
{desc}

{"" if page_rel == "404.html" else f'<link rel="canonical" href="{e(canonical)}">'}
<meta name="robots" content="{e("noindex" if page_rel == "404.html" else "index,follow,max-image-preview:large")}">
<meta property="og:type" content="{e(og_type)}">
<meta property="og:site_name" content="{e(SITE_NAME)}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(social_desc)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(OG_IMAGE)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(social_alt)}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(full_title)}">
<meta name="twitter:description" content="{e(social_desc)}">
<meta name="twitter:image" content="{e(OG_IMAGE)}">
<meta name="twitter:image:alt" content="{e(social_alt)}">
{ld}
<link rel="stylesheet" href="{prefix}assets/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' fill='%23245746'/%3E%3Ctext x='16' y='22' font-family='sans-serif' font-size='15' font-weight='700' fill='%23fff' text-anchor='middle'%3EZ1%3C/text%3E%3C/svg%3E">
</head>
<body>
<a class="skip-link" href="#main-content">Skip to main content</a>
<div class="disclosure-bar">
  <strong>Affiliate disclosure:</strong> {e(DISCLOSURE)}
  <a href="{prefix}compliance.html" style="color:#d8e7d5">How this site stays compliant →</a>
</div>
<header class="topbar">
  <a class="brand" href="{prefix}index.html" style="color:inherit">
    <span class="mark">Z1</span>
    <span>{e(SITE_NAME)}<small>{e(SITE_TAGLINE)}</small></span>
  </a>
  <span class="spacer"></span>
  <span class="meta">data verified {e(ACCESSED)}{(" · re-verified " + e(REVERIFIED)) if REVERIFIED else ""}</span>
  <button class="navtoggle" type="button" aria-controls="site-nav" aria-expanded="false">Menu</button>
</header>
<div class="shell">
  <nav id="site-nav" class="sidebar" aria-label="Primary navigation">
    <div class="group">
      <h4>Start here</h4>
      {N("index.html")}
      {N("picks.html")}
      {N("guides/buying-guide-air-fryers.html")}
      {N("articles/index.html")}
    </div>
    <div class="group">
      <h4>Products</h4>
      <a href="{prefix}categories/kitchen-appliances.html"{' class="active"' if active=='categories/kitchen-appliances.html' else ''}>Category: Kitchen<span class="sub">3 tracked products</span></a>
      {prod_nav}
      {N("compare.html")}
    </div>
    <div class="group">
      <h4>Decide</h4>
      {N("decisions.html")}
      {N("suggestions.html")}
      {N("design-prompt.html")}
      {N("questions.html")}
      {N("requirements.html")}
      {N("topics.html")}
      {N("executive-summary.html")}
    </div>
    <div class="group">
      <h4>Evidence</h4>
      {N("data.html")}
      {N("reverification.html")}
      {N("compliance.html")}
      {N("flagged.html")}
    </div>
    <div class="group">
      <h4>Platform</h4>
      {N("platform.html")}
    </div>
    {more_nav}
  </nav>
  <main id="main-content">
    {body}
  </main>
</div>
<footer class="site">
  <div class="inner">
    <div>
      <h2>Research archive</h2>
      <p>Older verification builds and supporting reports are kept separate from the main buying guide.</p>
      <p><a href="{prefix}previous-passes.html">Browse prior passes and annexes →</a></p>
    </div>
    <div>
      <h2>Disclosure</h2>
      <p><strong>{e(DISCLOSURE)}</strong></p>
      <p>We may earn a commission from a qualifying purchase made through an eligible link. The three supplied Amazon short links have not been confirmed to match the named models or carry this site's Associates tracking ID. Amazon prices, availability and ratings are not published here.</p>
    </div>
    <div>
      <h2>Verification</h2>
      <p>Every asserted value on this site links to the official page it came from. Values that could not be confirmed from an official source are left blank and listed on the <a href="{prefix}flagged.html">Flagged for review</a> page.</p>
      <p class="tiny">Data verified {e(ACCESSED)}. Policies change: always re-check the source before relying on it.</p>
    </div>
    <div>
      <h2>Cookies &amp; privacy</h2>
      <p>This site sets no cookies itself, runs no analytics, and has no comment forms or accounts. Following an Amazon link takes you to Amazon, whose own privacy notice and cookie practices apply from that point. No data you enter here is collected, because there is nowhere to enter it.</p>
      <p class="tiny">Amazon's Program Policies §3(e) require an accurate statement of cookie and third-party technology use on Associate sites. This notice satisfies that requirement for the current build; it must be updated the moment any analytics, embeds or affiliate-network script is added.</p>
    </div>
    <div>
      <h2>Sources</h2>
      <ul>
        <li><a href="https://affiliate-program.amazon.com/help/operating/agreement" target="_blank" rel="noopener">Associates Operating Agreement</a></li>
        <li><a href="https://affiliate-program.amazon.com/help/operating/policies" target="_blank" rel="noopener">Associates Program Policies</a></li>
        <li><a href="https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ" target="_blank" rel="noopener">Standard Commission Income Statement</a></li>
        <li><a href="https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255" target="_blank" rel="noopener">16 CFR Part 255 (FTC)</a></li>
      </ul>
    </div>
  </div>
  <div class="legal">
    {e(SITE_NAME)} is an independent affiliate publisher. It is not owned by, endorsed by, or sponsored by Amazon.com, Inc. or by any brand named on this site. Product names and brand names are the property of their respective owners and are used for identification only. No hands-on testing is claimed anywhere on this site; all analysis is documentation-based and sourced.
  </div>
</footer>
<script src="{prefix}assets/app.js"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# reusable fragments
# --------------------------------------------------------------------------- #

def product_cta(p, prefix=""):
    return f"""
<div class="cta-row">
  <a class="btn" href="{e(p['link'])}" target="_blank" rel="nofollow sponsored noopener">Open supplied Amazon link — verify model <span aria-hidden="true">↗</span></a>
  <span class="paid-tag">Affiliate link · tracking unconfirmed</span>
</div>
<p class="cta-note">Affiliate disclosure: we may earn a commission if Amazon credits a qualifying purchase to this site, but this short link's Associates tag has not been verified. The model identity is also unconfirmed; check the product title and model number on Amazon before buying. See <a href="{prefix}flagged.html">Flagged for review</a> and <a href="{prefix}questions.html#q-01">the open questions</a>. {src_links(['S17', 'S2'])}</p>
"""


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
    return f"""
<div class="card">
  <h3 style="margin-top:0">Revenue scenario calculator</h3>
  <p class="small muted" style="margin-top:0">Pure arithmetic on inputs <em>you</em> supply, plus a rate you pick <strong>from the official table</strong>. Nothing here is a forecast, and no number below is an Amazon quote for these products. Change a field and the outputs recompute.</p>
  <form id="calc" class="calc">
    <div><label for="price">Brand list price (USD)</label><input id="price" type="number" min="0" step="0.01" value="199.99"></div>
    <div><label for="rate">Commission rate</label>
      <select id="rate">
        <option value="4.50">4.50% — Kitchen (S3)</option>
        <option value="4.00">4.00% — All Other Categories (S3)</option>
        <option value="3.00">3.00% — Home (S3)</option>
        <option value="2.50">2.50% — PC / components (S3)</option>
      </select>
    </div>
    <div><label for="clicks">Monthly outbound clicks</label><input id="clicks" type="number" min="0" step="1" value="1000"></div>
    <div><label for="conv">Conversion rate (%)</label><input id="conv" type="number" min="0" step="0.1" value="3"></div>
  </form>
  <div class="calc" style="margin-top:.75rem">
    <div class="out"><span>Commission / sale</span><b id="out-commission">—</b></div>
    <div class="out"><span>Orders / month</span><b id="out-sales">—</b></div>
    <div class="out"><span>Revenue / month</span><b id="out-revenue">—</b></div>
    <div class="out"><span>Earnings per click</span><b id="out-epc">—</b></div>
  </div>
  <p class="tiny muted" style="margin-bottom:0">Commission is computed on <em>Qualifying Revenue</em>, which Amazon defines as what it actually receives less shipping, gift wrap, handling, taxes, service charges, credits, rebates, card fees and bad debt — so a real payout is lower than the figure above {src_links(['S2'])}. Conversion rate is the single biggest unknown and is yours to measure.</p>
</div>
"""


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


def page_index():
    _article_cards = _dashboard_article_cards()
    rev = REVERIFICATION["tests"]
    rev_total = len(rev)
    def _v(*keys):
        return sum(1 for t in rev if any(t["verdict"].startswith(k) for k in keys))
    rev_conf = _v("confirmed")
    rev_part = _v("partially-confirmed")
    rev_moved = _v("moved")
    rev_conflict = _v("conflict-live")
    rev_new = _v("not-rechecked")
    n_flags = sum(len(p["flags"]) for p in PRODUCT_LIST)
    n_total_flags = n_flags + len(PROGRAMME_FLAGS)
    # The Flagged page collapses each product's F1/F6 rows into the programme-level rows, so the
    # number of rows a reader actually finds there is smaller than the number recorded per product.
    n_open_flags = len(PROGRAMME_FLAGS) + sum(
        1 for p in PRODUCT_LIST for f in p["flags"] if f["id"] not in ("F1", "F6"))
    verified = sum(1 for p in PRODUCT_LIST for s in p["specs"] if s["value"] is not None)
    unverified = sum(1 for p in PRODUCT_LIST for s in p["specs"] if s["value"] is None)
    format_labels = {
        "chefman-6qt-dual-basket": "Two-basket air fryer",
        "emeril-26qt-french-door": "French-door countertop oven",
        "chefman-8qt-turbofry": "Single-basket air fryer",
    }
    cards = "".join(
        f"""
<article class="card pcard">
  <p class="product-type">{e(format_labels.get(p['slug'], 'Air fryer'))}</p>
  <h3><a href="products/{p['slug']}.html">{e(p['short_name'])}</a></h3>
  <p class="small muted product-name">{e(p['name'])}</p>
  <div class="product-fact">
    <span>Manufacturer-stated capacity</span>
    <strong>{e(next((s['value'] for s in p['specs'] if s['label'] == 'Capacity' and s['value']), '— not confirmed —'))}</strong>
    <span class="tiny">{src_links(next((s['source'] for s in p['specs'] if s['label'] == 'Capacity'), []))}</span>
  </div>
  <p class="product-match"><span class="pill pill-warn">Amazon model match unconfirmed</span>
    <a class="tiny" href="flagged.html">Review link status</a></p>
  <p class="small" style="margin:.2rem 0 0"><a href="products/{p['slug']}.html">Read the sourced product notes →</a></p>
</article>"""
        for p in PRODUCT_LIST
    )
    body = f"""
<div class="editorial-hero">
  <div class="hero-copy">
    <p class="hero-eyebrow">Zone1 Kitchen <span aria-hidden="true">/</span> Air-fryer field guide</p>
    <h1 class="hero-title">Choose the shape before the model.</h1>
    <p class="lede">Two baskets, one 8 Qt basket, or a countertop oven? Compare three formats using manufacturer pages and owner's manuals—without pretending we tested them.</p>
    <div class="hero-actions">
      <a class="btn" href="#quick-guide">Find your fit <span aria-hidden="true">↓</span></a>
      <a class="btn btn-ghost" href="articles/index.html">Read the guides <span aria-hidden="true">→</span></a>
    </div>
    <p class="hero-footnote">Sourced specifications · visible gaps · no hands-on testing claimed</p>
  </div>
  <aside class="hero-panel" aria-label="Three air-fryer formats">
    <p class="hero-panel-kicker">The format guide <span>03 products</span></p>
    <h2>Start with how you cook.</h2>
    <div class="hero-choice">
      <span class="hero-index">01</span><span class="hero-choice-copy"><a href="products/chefman-6qt-dual-basket.html"><strong>Two independent baskets</strong></a><small>Chefman · 6 Qt {src_link('S10')} {src_link('S18')}</small></span><span class="hero-arrow" aria-hidden="true">↗</span>
    </div>
    <div class="hero-choice">
      <span class="hero-index">02</span><span class="hero-choice-copy"><a href="products/emeril-26qt-french-door.html"><strong>French-door countertop oven</strong></a><small>Emeril · 26 QT {src_link('S14')}</small></span><span class="hero-arrow" aria-hidden="true">↗</span>
    </div>
    <div class="hero-choice">
      <span class="hero-index">03</span><span class="hero-choice-copy"><a href="products/chefman-8qt-turbofry.html"><strong>One large basket</strong></a><small>Chefman · 8 Qt {src_link('S12')}</small></span><span class="hero-arrow" aria-hidden="true">↗</span>
    </div>
  </aside>
</div>

{pulse_strip()}

<div class="callout bad link-status" id="link-status">
  <div class="link-status-heading"><span class="pill pill-warn">Before shopping</span><strong>Product identity, account approval and affiliate tracking are not confirmed.</strong></div>
  <p class="small">A targeted live re-check on 2026-11-16 again observed fallback-style redirects for all three supplied short links. We cannot confirm that any link reaches the product the account holder intended, carries the correct Associates tag, or that the Associates account is approved. Verify the model and account status in Amazon before relying on a purchase link. {src_links(['S17', 'S2'])} <a href="reverification.html">Read the redirect evidence</a> · <a href="flagged.html">Flagged for review</a> · <a href="questions.html#q-01">Product-link question</a> · <a href="questions.html#q-03">Account-status question</a>.</p>
</div>

<div class="method-strip" id="how-we-work" aria-label="How this guide is made">
  <div><span class="method-number">01</span><strong>Manufacturer sources</strong><p>Specs link to brand product pages or owner's manuals.</p></div>
  <div><span class="method-number">02</span><strong>Unknowns stay visible</strong><p>Unconfirmed values are left blank and sent to the review register.</p></div>
  <div><span class="method-number">03</span><strong>No test claims</strong><p>This is a document-based comparison, not a hands-on review. {src_links(['S8'])}</p></div>
</div>

<section id="quick-guide" class="quick-guide">
  <div class="section-heading">
    <p class="section-eyebrow">A practical starting point</p>
    <h2>Start with the shape that suits your kitchen.</h2>
    <p class="small muted">These are product formats—not a ranked top-three list. Follow a link for the full sourced breakdown.</p>
  </div>
  <div class="grid grid-3 decision-grid">
    <article class="card decision-card">
      <p class="decision-label">Two baskets</p>
      <h3>Two foods, separate settings</h3>
      <p class="small">The 6 Qt Chefman manual documents two 3-quart baskets and a Sync Finish function. That is the documented difference; we have not tested the cooking result. {src_links(['S18'])}</p>
      <a href="articles/dual-basket-vs-single-basket.html">Two baskets or one? →</a>
    </article>
    <article class="card decision-card">
      <p class="decision-label">Oven-style</p>
      <h3>More than a basket</h3>
      <p class="small">The Emeril is described as a 26 QT French-door toaster-oven combo, and the manual documents a rotisserie. Its owner's manual lists 24 presets and the supplied listing title agrees; the brand page's specification block says 25, so the flag stays open. {src_links(['S14', 'S15'])}</p>
      <a href="articles/dual-basket-vs-oven-air-fryer.html">Basket or countertop oven? →</a>
    </article>
    <article class="card decision-card">
      <p class="decision-label">Single basket</p>
      <h3>One 8 Qt cooking space</h3>
      <p class="small">Chefman's product page lists an 8 Qt basket and four named presets. The supplied listing title and the manufacturer's specification set contain a temperature discrepancy, so the exact model mapping remains open. {src_links(['S12', 'S13', 'S29'])}</p>
      <a href="articles/what-450f-actually-means.html">What the temperature label means →</a>
    </article>
  </div>
</section>

<h2>The three, side by side</h2>
<p class="small muted">Every populated fact has its own official source link. A dash means we could not confirm it; conflicts are shown as conflicts rather than resolved by guesswork.</p>
<div class="tablewrap comparison-table">
<table>
  <caption>Quick comparison — manufacturer-backed specifications and open gaps</caption>
  <thead><tr><th>What to compare</th><th>Chefman 6 Qt Dual Basket</th><th>Emeril 26 QT French Door</th><th>Chefman 8 Qt TurboFry</th></tr></thead>
  <tbody>
    <tr><td class="small"><strong>Format</strong></td>
      <td class="small">Dual-basket air fryer<div class="tiny">{src_links(['S10'])}</div></td>
      <td class="small">French-door countertop oven<div class="tiny">{src_links(['S14'])}</div></td>
      <td class="small">Single-basket air fryer<div class="tiny">{src_links(['S12'])}</div></td></tr>
    <tr><td class="small"><strong>Capacity</strong></td>
      <td class="small">6 Qt / 5.67 L; two 3-qt baskets<div class="tiny">{src_links(['S10', 'S18'])}</div></td>
      <td class="small">26 qt / 24.6 L<div class="tiny">{src_links(['S14', 'S15'])}</div></td>
      <td class="small">8 qt<div class="tiny">{src_links(['S12', 'S13'])}</div></td></tr>
    <tr><td class="small"><strong>Temperature</strong></td>
      <td class="small">200–450 °F; Hi-Fry holds 450 °F for 2 minutes<div class="tiny">{src_links(['S10', 'S18'])}</div></td>
      <td class="small">75–500 °F<div class="tiny">{src_links(['S15'])}</div></td>
      <td class="small"><span class="pill pill-warn">Conflicting claims</span><div class="tiny">Brand page: 200–400 °F; supplied listing title advertises 450 °F. Model match is unconfirmed.</div><div class="tiny">{src_links(['S12', 'S29'])} <a href="flagged.html">Flagged</a></div></td></tr>
    <tr><td class="small"><strong>Preset information</strong></td>
      <td class="small blank">— not confirmed —<div class="tiny">{src_links(['S18'])} <a href="flagged.html">Flagged</a></div></td>
      <td class="small">24 presets named in the owner's manual<div class="tiny">Airfry, Fries, Bacon, Grill, Eggs, Fish, Ribs, Defrost, Steak, Vegetables, Wings, Bake, Rotisserie, Toast, Chicken, Pizza, Pastry, Proof, Broil, Slow Cook, Roast, Dehydrate, Reheat, Warm.</div><div class="tiny"><span class="pill pill-warn">One page disagrees</span> The brand page's specification block says "25 Cooking Pre-sets"; its own description and the Amazon listing title both say 24.</div><div class="tiny">{src_links(['S15', 'S14', 'S28'])} <a href="flagged.html">Flagged</a></div></td>
      <td class="small">Fries, Chicken, Fish, Meat<div class="tiny">{src_links(['S12', 'S13'])}</div></td></tr>
    <tr><td class="small"><strong>Rotisserie</strong></td>
      <td class="small blank">— not confirmed —<div class="tiny">{src_links(['S10', 'S18'])} <a href="flagged.html">Flagged</a></div></td>
      <td class="small">Yes<div class="tiny">{src_links(['S14', 'S15'])}</div></td>
      <td class="small blank">— not confirmed —<div class="tiny">{src_links(['S12', 'S13'])} <a href="flagged.html">Flagged</a></div></td></tr>
    <tr><td class="small"><strong>Outer dimensions</strong></td>
      <td class="small">13.38 × 11.81 × 10.63 in<div class="tiny">{src_links(['S10'])}</div></td>
      <td class="small">16.9 D × 15.8 W × 14.8 H in<div class="tiny">{src_links(['S14'])}</div></td>
      <td class="small">15.4 × 12.6 × 13.5 in<div class="tiny">{src_links(['S12'])}</div></td></tr>
    <tr><td class="small"><strong>Rated power</strong></td>
      <td class="small">1700 W / 120 V<div class="tiny">{src_links(['S10'])}</div></td>
      <td class="small">1700 W / 120 V<div class="tiny">{src_links(['S15'])}</div></td>
      <td class="small">1700 W / 120 V<div class="tiny">{src_links(['S12'])}</div></td></tr>
    <tr><td class="small"><strong>Warranty</strong></td>
      <td class="small">1 year<div class="tiny">{src_links(['S10'])}</div></td>
      <td class="small">1 year<div class="tiny">{src_links(['S14'])}</div></td>
      <td class="small">Limited 1 year<div class="tiny">{src_links(['S13'])}</div></td></tr>
    <tr><td class="small"><strong>Full product record</strong></td>
      <td class="small"><a href="products/chefman-6qt-dual-basket.html">Read the sourced product notes →</a> {src_links(['S10', 'S18'])}</td>
      <td class="small"><a href="products/emeril-26qt-french-door.html">Read the sourced product notes →</a> {src_links(['S14', 'S15'])}</td>
      <td class="small"><a href="products/chefman-8qt-turbofry.html">Read the sourced product notes →</a> {src_links(['S12', 'S13'])}</td></tr>
  </tbody>
</table>
</div>
<p class="small muted">Measure your counter and cabinet clearance against the dimensions above. Noise level and real-world preheat time are not confirmed in the cited manufacturer materials. <a href="questions.html#q-06">See the open information gaps →</a></p>

<h2>Product notes, not rankings</h2>
<p class="small muted">The Amazon model match remains unconfirmed for every item. These pages separate manufacturer specifications from what is known about the supplied links.</p>
<div class="grid grid-3">{cards}</div>

<h2>This week's picks &mdash; and what one sale is worth</h2>
<p class="small muted">A picks page is usually a ranking. The one on this site is a decision rule: each product wins a different job, and the job you have decides the product. It also shows what Amazon actually pays per sale at each candidate rate, with the table row it came from.</p>
<div class="grid grid-2">
  <a class="card" href="picks.html"><span class="kicker">Commercial front door</span><span class="cardtitle">Three air fryers, three jobs &#8594;</span><span class="cardtext">The honest version of a picks page: a rule, the specification behind each match, and the commission arithmetic in the open.</span></a>
  <a class="card" href="decisions.html"><span class="kicker">Strategy</span><span class="cardtitle">Niche, traffic and measurement &#8594;</span><span class="cardtext">Three decisions with scored options, six channels ordered by what they depend on, and a pre-committed kill rule.</span></a>
</div>

<div class="grid grid-3" style="margin:1.1rem 0">
  <a class="card" href="picks.html"><span class="kicker">Buyer</span><span class="cardtitle">This week's picks &#8594;</span><span class="cardtext">A decision rule, not a ranking, plus what one sale pays at each official rate.</span></a>
  <a class="card" href="decisions.html"><span class="kicker">Owner</span><span class="cardtitle">Niche, traffic, measurement &#8594;</span><span class="cardtext">Scored options, six channels with their prerequisites, and a kill rule.</span></a>
  <a class="card" href="handover.html"><span class="kicker">Owner</span><span class="cardtitle">Handover: five actions &#8594;</span><span class="cardtext">About an hour of owner time closes eighteen flags. Start with three minutes.</span></a>
</div>

<h2>Commercial summary</h2>
{commercial_table()}

<div class="callout bad">
  <strong>Five actions, about an hour, eighteen flags.</strong>
  <p class="small" style="margin:.35rem 0 0">Everything in this repository is done as far as it can be done without your accounts. Reading the model number off three Amazon listings takes about three minutes and closes the four highest-severity flags. The full list, with exact steps and time estimates, is on <a href="handover.html">the handover sheet</a>.</p>
</div>

<h2 id="evidence">Under the hood: how much of this is actually confirmed</h2>
<p class="small muted">Everything from here down is the verification layer — useful if you want to know how
much to trust a number, not required reading before buying. The same material, in full, is on
<a href="data.html">the dataset</a>, <a href="reverification.html">the re-verification ledger</a> and
<a href="flagged.html">Flagged for review</a>.</p>

<div class="grid grid-4" style="margin:1rem 0 1.25rem">
  <div class="stat bad"><div class="n">0</div><div class="l">Verified product identities</div><div class="h">Supplied links reach Amazon fallback pages — see <a href="reverification.html">link checks through 2026-11-16</a></div></div>
  <div class="stat ok"><div class="n">{verified}</div><div class="l">Verified spec values</div><div class="h">Each with a link to the manufacturer page or manual</div></div>
  <div class="stat warn"><div class="n">{unverified}</div><div class="l">Unconfirmed values</div><div class="h">Left blank, listed on Flagged for review</div></div>
  <div class="stat bad"><div class="n">{n_open_flags}</div><div class="l">Open irregularities</div><div class="h">{n_total_flags} recorded across the three products and the programme; the Flagged page lists them as {n_open_flags} distinct rows</div></div>
</div>

<div class="callout info">
  <strong>Read this before you use any number on this site</strong>
  <p class="small">No Amazon price, star rating or review count appears anywhere on this site. That is deliberate. Amazon's Program Policies §2(b) allow price and availability to be shown only when Amazon serves the link or when the data comes from Creators/PA API, and §6(t) restricts customer reviews and star ratings to API-served content {src_links(['S2'])}. Manufacturer list prices are shown instead, in their own column, with their own source links.</p>
</div>

<div class="callout ok">
  <strong>Re-verified {REVERIFIED} — line by line</strong>
  <p class="small">Every value below was re-read on {REVERIFIED} against the official source the site cites for it: the
  manufacturer's own product page, its owner's manual, Amazon's Associates Central documents and the FTC's rule text.
  Of the {rev_total} rows in that ledger, {rev_conf} matched, {rev_part} matched in part, {rev_moved} moved because they
  are live counters, {rev_conflict} are still contradicted between official pages, and {rev_new} rows could not be re-opened
  in that pass. Two rows that were blank are now filled from the manufacturer's own specification block, and the open
  question of where the supplied links point has been tested twice more, with a control: four sessions over two days
  reached the same three destination ASINs, and an unrecognised token is refused (403) rather than shuffled. That
  settles the <em>destination</em>, not the <em>identity</em> — whether these are the products you meant to market,
  and which Associates tag rides on the link, still cannot be confirmed from outside Associates Central, and a
  parallel pass reads the same fallback marker as grounds for withholding the "resolved" label entirely. Both
  readings are published side by side (flag F21). Full ledger:
  <a href="reverification.html">Full line-by-line re-read: {REVERIFIED}</a>. A targeted follow-up on 2026-11-16 rechecked all three link destinations and refreshed two dated manufacturer review counters; it was not a full re-read. See the <a href="reverification.html">combined verification ledger</a>.</p>
</div>

<h2>Articles</h2>
<p class="small muted">Eight reads written for this product set. Each one quotes the manufacturer's own pages or manuals, links every number to the page it came from, and names the places where the official record contradicts itself instead of smoothing them over. No first-hand testing is claimed anywhere.</p>
<div class="cardgrid">
{_article_cards}
</div>
<p class="small"><a class="btn btn-ghost" href="articles/index.html">All articles →</a></p>

<h2>Where to go next</h2>
<div class="grid grid-2">
  <div class="card">
    <h3 style="margin-top:0">Judge the products</h3>
    <ul class="tight small">
      <li><a href="compare.html">Comparison matrix</a> — verified fields only, blanks kept visible.</li>
      <li><a href="guides/buying-guide-air-fryers.html">Buying guide</a> — dual-basket vs single-basket vs oven-style.</li>
      <li><a href="data.html">Full dataset</a> — every field, value, source and gap in one table.</li>
    </ul>
  </div>
  <div class="card">
    <h3 style="margin-top:0">Judge the operation</h3>
    <ul class="tight small">
      <li><a href="platform.html">Platform blueprint</a> — the automation, the data model, the guardrails.</li>
      <li><a href="compliance.html">Compliance</a> — 16 requirements, each quoted with a source link.</li>
      <li><a href="flagged.html">Flagged for review</a> — everything that still needs a human decision.</li>
      <li><a href="executive-summary.html">Executive summary</a> — the one-page version.</li>
    </ul>
  </div>
</div>

<h2>How a value earns its place on this site</h2>
<div class="tablewrap">
<table>
  <caption>Verification standard applied to every row</caption>
  <thead><tr><th>State</th><th>Meaning</th><th>How it renders</th></tr></thead>
  <tbody>
    <tr><td>{flag_pill('verified')}</td><td>The value was read on an official page — the party that owns the fact published it — on {e(ACCESSED)}.</td><td>Value shown, with a clickable source badge (e.g. {src_link('S10')}).</td></tr>
    <tr><td>{flag_pill('unverified')}</td><td>No official source states the value, or official sources disagree.</td><td>Value left blank, reason written out, and the item repeated on <a href="flagged.html">Flagged for review</a>.</td></tr>
    <tr><td>{flag_pill('conflict')}</td><td>Two official sources state different things and neither can be preferred.</td><td>Both claims quoted side by side; no single value asserted. Examples listed on <a href="flagged.html">Flagged for review</a> (F3, F4, F5).</td></tr>
  </tbody>
</table>
</div>
<div class="archive-panel">
  <p class="section-eyebrow">For the detail-minded</p>
  <h3>Want the full evidence trail?</h3>
  <p class="small">The complete dataset, source register, open flags and previous research builds are available for review.</p>
  <p class="small"><a href="data.html">Full dataset →</a> · <a href="flagged.html">Flagged for review →</a> · <a href="previous-passes.html">Research archive →</a></p>
</div>
<p class="tiny muted">Evidence standard: Amazon sources support Amazon program and listing facts; manufacturers support product specifications; US government sources support legal requirements. The <a href="data.html">source register</a> lists each reference and what it can verify.</p>
"""
    ld = [
        PUBLISHER,
        {
            "@type": "WebSite",
            "@id": SITE_URL + "/#website",
            "url": SITE_URL + "/",
            "name": SITE_NAME,
            "description": SITE_TAGLINE,
            "inLanguage": "en-US",
            "publisher": {"@id": SITE_URL + "/#organization"},
        },
        breadcrumbs_jsonld([("Home", SITE_URL + "/")]),
        {
            "@type": "ItemList",
            "@id": SITE_URL + "/#formats",
            "name": "Three air-fryer formats compared",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "name": pr["short_name"],
                    "url": page_url(f"products/{pr['slug']}.html"),
                }
                for i, pr in enumerate(PRODUCT_LIST, start=1)
            ],
        },
    ]
    return layout("index.html", "Air fryer buying guide", body, active="index.html",
                  description="A source-led comparison of three air-fryer formats, with manufacturer specifications, visible gaps and the status of the supplied Amazon links.",
                  jsonld_blocks=ld)


def page_product(p):
    tag = p["slug"]
    facts = "".join(
        f'<tr><td>{e(s["label"])}</td><td>'
        + (e(s["value"]) if s["value"] else '<span class="blank">— not confirmed —</span>')
        + f'</td><td>{src_links(s["source"])}</td></tr>'
        for s in p["specs"][:6]
    )
    flag_rows = "".join(
        f'<tr><td class="num">{e(f["id"])}</td><td>{e(f["issue"])}</td>'
        f'<td class="small">{e(f["action"])}</td><td>{src_links(f.get("sources", []))}</td></tr>'
        for f in p["flags"]
    )
    cand = "".join(
        f'<tr><td>{e(c["category"])}</td><td class="num">{e(c["rate"])}</td><td>{src_links(c["source"])}</td></tr>'
        for c in p["commission"]["candidate_rows"]
    )
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / <a href="../categories/kitchen-appliances.html">Kitchen</a> / {e(p['short_name'])}</p>
<h1>{e(p['short_name'])}</h1>
<p class="lede">{e(p['name'])} — {e(p['brand'])}. These are document-based product notes, not a ranking or hands-on review. Specifications below come from the manufacturer's product page or owner's manual, accessed {e(ACCESSED)}. The candidate ASIN comes from recorded link checks, but the supplied short-link-to-model mapping is not confirmed; see the <a href="../reverification.html">redirect evidence</a> and <a href="../flagged.html">Flagged for review</a>.</p>

<div class="grid grid-4" style="margin-bottom:1rem">
  <div class="stat warn"><div class="n" style="font-size:1.15rem">{e(p['asin']['v'])}</div><div class="l">Candidate ASIN · unconfirmed</div><div class="h">{src_links(p['asin']['s'])}</div></div>
  <div class="stat"><div class="n" style="font-size:1.15rem">{e(p['pricing']['brand_list_price']['v'])}</div><div class="l">Brand list price</div><div class="h">{src_links(p['pricing']['brand_list_price']['s'])}</div></div>
  <div class="stat"><div class="n" style="font-size:1.15rem">{e(p['reviews']['brand_site_rating']['v'].split(' from')[0])}</div><div class="l">Brand-site rating · not Amazon</div><div class="h">{src_links(p['reviews']['brand_site_rating']['s'])}</div></div>
  <div class="stat warn"><div class="n" style="font-size:1.15rem">{len(p['flags'])}</div><div class="l">Open flags</div><div class="h"><a href="../flagged.html">Review all flags →</a></div></div>
</div>

{product_cta(p, prefix="../")}

<div class="callout ok">
  <strong>How this review was produced</strong>
  <p class="small">This is a documentation-based review. No unit was tested, owned or handled. That matters legally as well as ethically: the FTC's disclosure guidance says an endorser cannot describe an experience with a product they have not tried {src_links(['S8'])}, so this page describes published specifications and what they imply — nothing else.</p>
</div>

<h2>What recorded link checks observed</h2>
<div class="card tight">
  <p class="small" style="margin:0"><strong>Supplied short link:</strong> <code>{e(p['link'])}</code> {src_links(['S17'])}<br>
  <strong>Observed landing URL (identity not confirmed):</strong> <code>https://www.amazon.com/dp/{e(p['asin']['v'])}</code> {src_links(['S16'])}</p>
  <p class="tiny muted" style="margin:.5rem 0 0">{e(p['asin_evidence'])} The plain <code>/dp/{e(p['asin']['v'])}</code> URL also returned Amazon's fallback-parameter form on 2026-11-14 (F15), so a fetch alone does not prove this is the live product page. Confirm from a logged-in browser before treating the ASIN as the supplied product.</p>
</div>

<h2>Verified specifications</h2>
{spec_table(p)}

<h2>Pricing — what is shown and what is not</h2>
<div class="tablewrap">
<table>
  <caption>Pricing transparency for {e(p['short_name'])}</caption>
  <thead><tr><th>Figure</th><th>Value</th><th>Source / status</th></tr></thead>
  <tbody>
    <tr><td>Manufacturer list price</td><td>{e(p['pricing']['brand_list_price']['v'])}</td><td>{src_links(p['pricing']['brand_list_price']['s'])} {flag_pill('verified')}</td></tr>
    <tr><td>Amazon price</td><td class="blank">— not displayed —</td><td>{flag_pill('unverified')} {e(p['pricing']['amazon_price_reason'])} {src_links(['S2'])}</td></tr>
    <tr><td>MSRP confirmed</td><td class="blank">— not confirmed —</td><td>{flag_pill('unverified')} {e(p['pricing']['msrp_confirmed'])} {src_links(p['pricing']['brand_list_price']['s'])}</td></tr>
  </tbody>
</table>
</div>
<p class="tiny muted">{e(p['pricing']['brand_list_price'].get('note',''))}</p>

<h2>Commission potential — the honest version</h2>
<p class="small">The site cannot state this product's commission rate, because Amazon publishes rates by category and does not publish which category an ASIN belongs to. The candidate rows from the official table are:</p>
<div class="tablewrap">
<table>
  <caption>Candidate official rate rows for {e(p['short_name'])}</caption>
  <thead><tr><th>Rate-table category</th><th>Rate</th><th>Source</th></tr></thead>
  <tbody>{cand}</tbody>
</table>
</div>
<div class="callout bad">
  <strong>Why the rate is left blank</strong>
  <p class="small">{e(p['commission']['why_unverified'])} {src_links(['S3'])}</p>
  <p class="tiny" style="margin-bottom:0">{e(p['commission']['rate_source_note'])}</p>
</div>

<h2>Competition data</h2>
<div class="card tight">
  <p class="small" style="margin:0">{flag_pill('unverified')} Amazon result counts and Best Sellers Rank are not published by Amazon as a stable, quotable fact, and building an aggregated dataset from Amazon pages is explicitly restricted by the IP License §2(e) {src_links(['S2'])}. This field stays empty rather than being scraped.</p>
</div>

<h2>Open irregularities on this product</h2>
<div class="tablewrap">
<table>
  <caption>Flags recorded against {e(p['short_name'])}</caption>
  <thead><tr><th style="width:6%">ID</th><th style="width:44%">Issue</th><th style="width:32%">Action taken</th><th style="width:18%">Source checked</th></tr></thead>
  <tbody>{flag_rows}</tbody>
</table>
</div>
<p class="small">See also the <a href="../flagged.html">Flagged for review</a> page for the cross-product flags.</p>

<h2>Verdict, limited to what is verified</h2>
<div class="card">
  <p class="small" style="margin-top:0">{e(VERDICTS.get(p['slug'], ''))}</p>
  <p class="tiny muted" style="margin-bottom:0">No star rating is given by this site, because a rating would imply a comparative judgement this dataset cannot support: the Amazon price and rating for these ASINs are unknown to us by policy, and no unit was tested.</p>
</div>

<p class="small" style="margin-top:1.5rem"><a href="../compare.html">← Back to the comparison</a> · <a href="../data.html">See every field in the dataset</a></p>
"""
    purl = page_url(f"products/{tag}.html")
    ld = [
        {
            "@type": "ItemPage",
            "@id": purl + "#webpage",
            "url": purl,
            "name": p["name"],
            "description": f"Documentation-based review of the {p['name']} — verified specifications with official source links.",
            "isPartOf": {"@id": SITE_URL + "/#website"},
            "about": {"@id": SITE_URL + "/#organization"},
            "inLanguage": "en-US",
        },
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Kitchen appliances", page_url("categories/kitchen-appliances.html")),
            (p["short_name"], purl),
        ]),
    ]
    return layout(f"products/{tag}.html", p["short_name"], body,
                  active=f"products/{tag}.html",
                  description=f"Documentation-based review of the {p['name']} — verified specifications with official source links.",
                  jsonld_blocks=ld)


PROGRAMME_FLAGS = [
    ("F1", "ASIN → manufacturer model number is not published by Amazon.",
     "All three", "Each product's model number is recorded as a match by capacity/finish/brand wording, with an explicit caveat. Flagged rather than asserted.", ["S16"]),
    ("F6", "The Associates tag inside the three link.amazon short links is not observable.",
     "All three links", "The shortener hides the tag. Attribution cannot be verified from outside Associates Central, so 'associates_tag_confirmed' is false for all three links. Needs the account holder to open Manage Tracking IDs.", ["S2", "S17"]),
    ("F7", "Program Policies §6(w) (Content on your Site) prohibits link shortening that makes it unclear you are linking to an Amazon Site.",
     "All three links", "link.amazon keeps the Amazon name visible, so the risk is low, but the landing URL is generated and temporary. Recorded so the account holder can confirm current guidance before publishing.", ["S2"]),
    ("F8", "IP License §2(e) forbids aggregating, analysing or repurposing Program Content and training models on it.",
     "Platform design", "Any AI research or trend scoring therefore runs only on first-party data and public manufacturer data. Documented as guardrail G6 in the blueprint.", ["S2"]),
    ("F9", "No Amazon price, star rating or review count is available to this build.",
     "All three", "Left blank everywhere by policy rather than by omission. Becomes fillable only if the operator secures Creators/PA API credentials.", ["S2", "S19"]),
    ("F10", "The short links are generated redirects with fallback parameters, not plain product links.",
     "All three links", "Logged redirect observations carried lv=shuf and plpRedirect=mhFallback. The candidate ASIN/title destinations were consistent across the recorded checks, but the btn_ref/srctok value changed between repeat or cache-busted requests (see F41 and the linked session evidence). These are observations of redirect responses, not confirmation that the candidate ASINs are the products intended by the account holder or that the links carry an Associates tag. Confirm both before publishing.", ["S17", "S16"]),
    ("F11", "The site does not disclose cookies, pixels and third-party technologies as Participation Requirements §3(e) requires.",
     "Whole site", "The site itself sets no cookies and runs no analytics, but §3(e) requires an accurate disclosure of cookie and third-party technology use, including that third parties may place or recognise cookies. Only a minimal notice is in the footer; a proper privacy/cookie statement is needed before launch. Legal review recommended.", ["S2"]),
    ("F12", "The automated platform functions in the brief are not running — by design, not by omission.",
     "Platform", "Automated trend detection, competition scoring and conversion optimisation need an Associates account, Creators/PA API credentials and sales reports. PA API access is registered through Associates Central and credentials are tied to the primary account holder, with request rate scaled to account sales performance. None of that exists in this repository, and inventing the data to fill the gap would defeat the point of the project.", ["S2", "S19", "S20"]),
    ("F13", "Product listing titles are reproduced from Amazon; §6(a) restricts altering Program Content.",
     "All three", "Titles are shown verbatim and unedited. §6(a) permits truncation only where meaning is not materially altered, and whether a listing title counts as Program Content is not stated. Recorded so the operator can confirm before adding any paraphrase.", ["S2"]),
    ("F14", "The landing page overstated product resolution (corrected 2026-11-14).",
     "Root landing page", "The headline read '3 products resolved — all three short links followed to an ASIN'. The 2026-11-14 check found the short links reach Amazon fallback pages and the bare 9-character codes return 'Page Not Found'. The headline now reads '0 verified product identities' and the ASINs are labelled as unconfirmed candidates. Evidence: reports/link-check-2026-11-14.md.", ["S16", "S17"]),
    ("F15", "Plain ASIN URLs were also answered with Amazon's fallback form on 2026-11-14.",
     "All three ASINs", "amazon.com/dp/B0CDY277D3, /dp/B09B7SB46R and /dp/B08DKYBTPH each returned a URL carrying lv=shuf and plpRedirect=mhFallback, so a fetch cannot show that the ASIN is the live product page. Confirm from a logged-in browser before any ASIN is treated as the supplied product.", ["S16"]),
    ("F16", "link.amazon is not confirmed as an Amazon-documented short-link domain.",
     "All three links", "A web search on 2026-11-14 returned only third-party blogs naming amzn.to and a.co. No official Amazon page listing link.amazon was found. An official Associates help page is needed before the domain is described as Amazon's.", ["S2", "S17"]),
    ("F17", "Advisory link gate: table rows with no source link on inherited annex pages.",
     "dashboard/, site/, research/, session-3740f69d/ annexes", "Root pages generated by build.py were given a source badge, policy citation or flagged-page link in the arena/0c7445c7 pass (2026-11-14). Remaining advisory rows lived only in other sessions' annex builds; scripts/check_links.py reported them as non-blocking warnings. **CLOSED 2026-11-14 by sess-7111e2b6** along with F25: a row-source pass now runs inside the research/ and site/ generators, and scripts/source_rows.py applies it to the hand-authored annex builds. The advisory list is empty, and the gate's own definition was corrected first, so that it can see single-quoted hrefs and every flagged-page filename.", ["S1"]),
    ("F18", "Committed s2 build stamp changes with the calendar date.",
     "s2/ (session zone1-s2 build)", "scripts/build_s2_site.py writes today's date into the 'built' stamp. Re-running on 2026-11-14 changes 13 files by that stamp alone (committed stamp: 2026-11-13). The CI gate regenerates before it checks, so it passes, but the committed copy is not pinned. Not changed in this pass because another session owns the file.", ["S1"]),
    ("F19", "Brand-site review counts move between days, so every rating on this site is a dated observation.",
     "All three", "Chefman's own widget read 1,302 reviews on 2026-11-13 and 1,305 on 2026-11-14; the 8 Qt page read 715 then 716. A third read on 2026-11-16 moved them again — 1,307 and 717 — while both averages held at 4.6 for the third consecutive time. The averages did not move (4.6 on every read), but a published figure without its read date would silently become false. All three counts now carry all three dates in the dataset, and any copy generated from it must carry the date too.", ["S10", "S12"]),
    ("F20", "The repository carries six parallel builds, and two of them were unreachable from the landing page until the 2026-11-14 integration pass.",
     "Whole repo", "s2/, site/, dashboard/, research/, session-3740f69d/ and docs/ are independent session outputs with their own data, their own verifiers and their own verdicts; they disagree in places (for example on whether the commission rate can be stated, and on how to read the plpRedirect=mhFallback marker). The pass linked the two orphaned builds into the navigation and changed none of their content. The owner should decide which build is canonical before this points at a real domain — a live site with six home pages is a maintenance and trust problem, not a data problem.", []),
    ("F23", "One documented build command in the README no longer runs against the shared data — it is a pre-existing break, not a regression from this pass.",
     "scripts/build.mjs → docs/", "The Node builder that generated the retired docs/ build validates a schema (products with official_url / values, sources with a status field, compliance.rows, flags) that data/products.json, data/sources.json, data/compliance.json and data/flags.json no longer use, so 'node scripts/build.mjs --check' throws ERR_INVALID_URL on undefined. Verified identical on the pre-change baseline, and no CI workflow calls it — pages.yml, ci.yml and verify.yml are Python-only. docs/ therefore stays frozen as committed and cannot be regenerated from current data. Not repaired here: re-authoring another session's generator to a new schema would silently change what its published pages assert. Either retire docs/ and its README line, or point the builder at data/verified/. This pass added no dependency on it.", []),
    ("F22", "A committed merge-conflict marker was found in a published document and repaired by this pass.",
     "EXECUTIVE_SUMMARY.md", "The file carried a bare '=======' line and a '>>>>>>> origin/main' line on main, i.e. a previous integration resolved a conflict by leaving the markers in. Both sides are real work by different sessions, so this pass removed only the markers and kept both documents as separate sections. Any other file carrying markers should be treated the same way — delete the marker, never the work.", []),
    ("F21", "Two verification passes on the same links reached different conclusions, and both are published.",
     "The three supplied links", "arena/1dcaaafc (reports/link-check-2026-11-14.md) reads the fallback marker plus the 9-character-token 404 as 'product identity not confirmed' and removed the 'products resolved' headline. sess-81495d2d (reverification.html) re-tested with a repeat request and a nonsense-token control: the target was identical across four sessions on two days, while an unrecognised token returns 403 instead of a product page, which is not what a pure not-found fallback would do. The reconciled position on this site: the *destination* of the links is reproducible and is documented; the *identity* of the product the operator meant, and the Associates tag attached to the link, are not confirmed and are not asserted. Confirm both in a logged-in browser and in Associates Central before publishing.", ["S16", "S17", "S21", "S22"]),
    ("F24", "PA-API 5 is officially deprecated (confirmed live 2026-11-14); the successor is Amazon's Creators API.",
     "Platform design", "The official docs URL now serves a deprecation notice: PA-API 5 calls return 403 AccessDeniedException and integrations are told to migrate to the Creators API. This supersedes the earlier board retraction of the cross-check's F18 claim and means every automated feature in the blueprint must target the Creators API, not PA-API 5. The Program Policies phrase their data-use rules as 'Creators API or PA API', so the compliance quotes remain accurate. Independently noted in the dashboard annex as H-01.", ["S24", "S20"]),
    ("F25", "Table rows on inherited builds have no link to a registered official source.",
     "dashboard/, research/, site/, s2/, session-3740f69d/, annex-88769516/",
     "Audited 2026-11-14 with the project's own official-host list (every host in data/sources.json, plus this repo on GitHub). Root pages generated by build.py now pass, and the build fails on any unsourced row. Inherited builds were not edited by that pass because other sessions own them. Count at 2026-11-14: 281 of 1,363 table rows in the repository have no sourced link (inherited builds: 281 of 1,057; root pages built by build.py: 0 of 306). **CLOSED 2026-11-14 by sess-7111e2b6.** The residue is now 0. Two things were wrong with the count itself: the link gate could not see single-quoted hrefs, and it recognised only one filename for the flagged page, so 33 rows that did carry a source link were being reported as unsourced. With the gate corrected, the true figure was 248 rows. A row-source pass was then added inside the research/ and site/ generators, and scripts/source_rows.py applies the same pass to the three hand-authored builds (dashboard/, annex-88769516/, session-3740f69d/). Rows that state a fact now link to that fact's official document; rows that are judgements, blocked metrics or unverified values link to the flagged page, which is where the project puts unconfirmed values. The gate also now rejects rows that link only to a relative internal page.", []),

    ("F26", "Two platform KPIs are internal design targets; no official source states them.",
     "platform.html, KPI table: Verified-row coverage, Flag resolution time",
     "Shown with this flag, not with an invented source. They are operating targets for this project, not facts about Amazon, the FTC or any product, and they feed no published product value. The owner should decide whether to keep them as targets.", []),
    ("F27", "Policy citations for the Participation Requirements 'Content on your Site' items used section numbers that do not match the live page.",
     "Root-site content (corrected in this pass); site/ annex pages still carry the old labels",
     "Live reads of affiliate-program.amazon.com/help/operating/policies on 2026-11-14 (two independent renders; version dated April 14, 2026) place the customer-review/star-rating rule at Participation Requirements '6. Content on your Site' item (t), and items (g) incentives, (n) framing, (u) self-purchase, (v) cloaking, (w) link shortening and (y) price tracking in the same section. Repo content had cited these as \u00a73(t), \u00a73(g), \u00a73(n), \u00a73(u), \u00a73(v), \u00a72(w) and \u00a73(y). Every quoted rule text was verified verbatim against the live page, so no published behaviour changes \u2014 only the citation labels were aligned to the live structure in build.py, data/compliance.json, data/products.json, data/sources.json, data/platform.json, data/marketing.json, README.md, EXECUTIVE-SUMMARY.md and EXECUTIVE_SUMMARY.md. Spot-checked labels that were already correct: \u00a72(b) prices/availability, \u00a73(e) cookies, \u00a76(a) alteration, IP License \u00a72(e) aggregation/ML-training, Operating Agreement \u00a75 disclosure. The site/ annex (session 1874bb64) still renders \u00a73(t) from data/verified/; its owner session should align it (request logged in COORDINATION.md). Historical session records in COORDINATION.md were left as written.", ["S2"]),
    ("F28", "Three flag registers share overlapping ID spaces but index different issues, and two published documents cite the wrong one.",
     "Cross-build consistency",
     "Confirmed 2026-11-14 by sess-91d0552e (renumbered F25 -> F28 to avoid a collision with arena/6ecdb4e4's F25). (a) research/build_research.py tells the reader to see 'the root site's Flagged page (shared register data/flags.json id F19)' for the product-titles/§6(a) issue and 'id F20' for the cookie-disclosure issue. Those IDs ARE correct inside data/flags.json, but the root Flagged page is generated from build.py's own PROGRAMME_FLAGS, where F19 is 'brand-site review counts move between days' and F20 is 'the repository carries six parallel builds'. A reader following that pointer lands on an unrelated row. (b) EXECUTIVE_SUMMARY.md, still served at the site root, asserts 'Identity verified. All three short links resolve to Amazon.com product pages with different ASINs' and that 'the official commission schedule redirected to a sign-in page'. Both are contradicted by this pass: the reconciled position published on this site is 0 verified product identities (F14-F16, F21), and the Standard Commission Income Statement was read in full, without any login, on 2026-11-14. Not repaired in this pass: data/flags.json is consumed by the s2 and docs generators and research/ is another session's build, so re-keying either register would silently re-point another build's citations. Decision needed: adopt one register as canonical and re-key the others, or relabel the pointers. Evidence: session-91d0552e/VERIFICATION-2026-11-14.md §5.", ["S1", "S3"]),

    ("F29", "The Emeril preset count is stated five different ways across official sources, and two of them now say 24.",
     "Emeril 26 QT French Door",
     "Re-read 2026-11-14 by sess-54c66535. Amazon's listing title for ASIN B09B7SB46R says '24 cooking functions' and Emeril's own description paragraph says 'Equipped with 24 one-touch cooking presets', while the same page's specification block says '25 Cooking Pre-sets', its feature heading says '10-In-1' and one of its carousel assets is named '11-in-1'. Two independent official sources now agreeing on 24 is new evidence: earlier passes recorded only 25 vs 10-in-1 vs 11-in-1 with no tiebreaker. The conflict is narrowed, not closed - the same brand page still contradicts itself - so no preset count is asserted anywhere on this site. Decision needed: confirm the figure against the unit's own control panel before any copy states a number. <strong>Re-read 2026-11-15 by arena/88bb2db6, which changes that last sentence.</strong> The owner's manual for FAFO-001 was read row by row: its Preset Mode Chart and its Recommended Accessory Positions table each list exactly 24 presets by name, and the manual never states the numeral. The Amazon listing title independently says '24 One-Touch Preset Options'. The site now states 24 on the strength of the manual, names the one official line that disagrees (the brand page's specification block, '25 Cooking Pre-sets'), and flags it. This row and F4 both stay open, but the site no longer asserts nothing. The 10-in-1 and 11-in-1 labels remain marketing wording and are not presented as specifications. Decision still needed: confirm the figure against the unit's own control panel.", ["S14", "S17", "S16"]),
    ("F30", "Two published specification values are not stated by the official source the site cites for them.",
     "Chefman 6 Qt Dual Basket (preset count); Emeril 26 QT French Door (interior light)",
     "Re-read 2026-11-14 by sess-54c66535. The Chefman dual-window user guide RJ38-SQPF-3TDB-2W was read end to end and documents HI-FRY, +2 MIN, MUTE, SYNC BASKETS, SYNC FINISH, START/STOP, TIME/TEMP and SHAKE, but has no preset chart and never names the four food presets the site publishes; its control panel is artwork with no text layer. The Emeril brand page's specification block lists Timer, 26-Quart Capacity, Dual-Speed Fan, 25 Cooking Pre-sets, dimensions, 24.6 Liters, Temperature Control and 120 volts, with no interior-light row. Both values were left as published rather than deleted, because deleting another session's sourced row is not this pass's call, but neither is currently traceable to an official statement. Decision needed: re-source both to the brand product pages, or blank them and let them appear here as unverified.", ["S18", "S14"]),
    ("F31", "The two Chefman 6 Qt sister SKUs carry very different review counts on the brand's own site.",
     "Chefman 6 Qt Dual Basket",
     "Re-read 2026-11-14 by sess-54c66535. The dual-basket page RJ38-SQPF-3TDB-2 reports 4.6 stars from 194 reviews; the dual-window page RJ38-SQPF-3TDB-2W reports 4.6 stars from 1,305 reviews, on an identical list price and promo ladder. The 6.7x gap is a usable signal for deciding which SKU the supplied ASIN maps to, which is open flag F2. It is not an identification: Amazon does not publish the model number behind an ASIN, and a review count is not a product identifier. No SKU is asserted.", ["S11", "S10"]),
    ("F32", "Chefman sells three different 6-quart dual-basket SKUs; the site names two of them.",
     "Chefman 6 Qt Dual Basket",
     "Found live 2026-11-14 by arena/6b2eddeb. Chefman's own store currently publishes RJ38-3DBW-V2 ('TurboFry 6 Qt. Double Basket Air Fryer with Easy View Windows': 6 Qt / 5.68 L as two 3 Qt / 2.84 L baskets, 90–400 °F / 32–204 °C, 1700 W, five functions — air fry, bake, reheat, dehydrate, frozen — easy-view windows, interior lights, shake notifications, 4.5 stars from 30 reviews, $99.99 list), RJ38-SQPF-3TDB-2 (dual-basket, 4.6 from 194, no specification block published) and RJ38-SQPF-3TDB-2W (dual-window, 200–450 °F, Hi-Fry, 4.6 from 1,305). The site records the -2W mapping because the Amazon title says 'Hi-Fry' and 'Easy View Windows', and Hi-Fry is documented only on the -2W page — but Easy View windows appear on all three, so the title does not discriminate on its own. This is an identification risk, not an identification. Two other builds shipped in this repo (site/, research/) map the same ASIN to RJ38-3DBW-V2 with no caveat, so a reader can reach two different official-looking answers two clicks apart. Decision needed: open the listing, read the model plate or the 'Product information' model number, and settle it once.", ["S25", "S27", "S10"]),
    ("F33", "The 'Hi-Fry / 450 °F: None' row for the 8 Qt product is only true of the stainless SKU, and a second official SKU matches the Amazon title exactly.",
     "Chefman 8 Qt TurboFry",
     "Found live 2026-11-14 by arena/6b2eddeb — narrows F3, does not resolve it. Chefman sells RJ38-SQSS-8T (TurboFry Touch Stainless-Steel, max 400 °F / 205 °C, four food presets, stainless finish — the SKU the site currently maps) and RJ38-8T-BLACK (TurboFry 8 Qt Air Fryer w/ High Fry: Hi-Fry 450 °F / 232 °C for the final two minutes, and exactly four functions — air fry, bake, dehydrate, frozen — in a matte-black finish). The Amazon listing title for B08DKYBTPH reads '…4-in-1 with 450°F Hi-Fry Option… | Bake, Dehydrate, Frozen | … Stainless Steel'. The function list and the 450 °F Hi-Fry match RJ38-8T-BLACK word for word; the finish matches RJ38-SQSS-8T. So the title may describe a third variant, or may carry a finish that does not match the unit. The previous framing — 'one of the two official sources is stale' — is now the less likely explanation. No value is changed and neither model is asserted; a human should read the model number printed in the listing's Product information section.", ["S12", "S26", "S16"]),
    ("F34", "The second executive summary at the repo root still asserts two things that are now known to be wrong.",
     "EXECUTIVE_SUMMARY.md",
     "Found 2026-11-14 by arena/6b2eddeb. EXECUTIVE_SUMMARY.md (the older of the two root summaries) states in its Key findings: 'Identity verified. All three short links resolve to Amazon.com product pages with different ASINs' and 'the official commission schedule redirected to a sign-in page'. This session re-fetched both on 2026-11-14: the Associates Program Standard Commission Income Statement (Table 1 and Bounty Events) was read in full with no login, and product identity is explicitly NOT verified anywhere on this site (F14–F16, F21, F32, F33). A dated correction banner was placed above that document by an earlier pass, but the contradicting sentences remain in the body and the file is still served from the site root by direct link. Decision needed: retire the duplicate document, or rewrite the two sentences. This pass did not edit it — the sentence is another session's published work and rewriting it is a content decision, not a verification one.", ["S1", "S3"]),
    ("F35", "Nine separate HTML sites for the same three products are published in this repository, and they disagree with each other.",
     "Whole repository",
     "Found 2026-11-14 by arena/6b2eddeb. Alongside the canonical root build there are research/ (12 pages), session-3740f69d/ (11), s2/ (13), site/ (11), dashboard/ (14), docs/ (7) and annex-88769516/ (10), plus data-only trees in crosscheck/ and platform/. The root navigation links to six of them. They disagree on facts a reader would take as settled: the Chefman 6 Qt model (RJ38-SQPF-3TDB-2W on the root site, RJ38-3DBW-V2 in site/ and research/ — F32), and the policy section numbers for the review/star-rating and link-shortening rules (§6(t)/§6(w) on the root site after F27, §3(t)/§2(w) in site/ and session-3740f69d/). Each build is internally consistent and individually verified; the problem is that nothing tells a reader which one is canonical when they arrive from a search engine. Decision needed: keep one site and archive the rest behind a clearly labelled 'previous verification passes' page, or make every non-canonical page carry a fixed banner naming the canonical build.", ["S1", "S2"]),
    # sess-ce4070ad, pass 7, 2026-11-14. NOTE (2026-11-15, arena/3ddfa50e): this row was published as F36
    # while a product-level row in data/products.json was also published as F36. Two rows, one number. The
    # product row is re-sourced from S16 to S28 by this pass and keeps F36 because three session evidence
    # files cite it by that number; this programme-level row moves to F41. Flag F40 records the collision.
    ("F41", "F10's earlier wording incorrectly said the short links' srctok marker stays constant across repeat requests.",
     "All three links — historical wording correction",
     "Closed 2026-11-15 by arena/94a562a1-zone1: F10 now states that the recorded candidate ASIN/title destinations were consistent while btn_ref/srctok values changed across some repeat or cache-busted requests. The underlying records include srctok-2cef40d2904c29d8 on 2026-11-13; srctok-1e229870efde5acf changing to srctok-397b5ba66db39bbf on a cache-busted repeat (session-81495d2d evidence, row 4); srctok-704dc575b940a94c (session-54c66535); and srctok-0740a2e990c9bbb3 in two observations later that day. This closes only the wording mismatch. It does not prove that any candidate listing is the product intended by the account holder or confirm affiliate attribution; see F1, F6, F14-F16 and F21.", ["S17", "S16"]),

    ("F37", "A published value was cited to a source that does not state it.",
     "Emeril 26 QT French Door — the \"Interior light: Yes\" row",
     "Found and fixed 2026-11-14 by sess-7111e2b6. The row cited the brand product page (S14), whose specification strip lists Timer, 26-Quart Capacity, Dual-Speed Fan, 25 Cooking Pre-sets, 16.9\"D x 15.8\"W x 14.8\"H, 24.6 Liters, Temperature Control and 120 volts — and no interior light. The value is nonetheless correct: the owner\'s manual (S15) documents it in the control-panel section, \"F. LIGHT BUTTON: May be selected at any time during the cooking process to light the appliance\'s interior.\" The row has been re-sourced from S14 to S15 and the manual\'s wording recorded in the row note. The lesson is published rather than quietly fixed: a value can be true and still be mis-cited, and a citation that does not support its value is as much a defect as an invented number.",
     ["S14", "S15"]),

    # ---- arena/3ddfa50e, integration pass 8, 2026-11-15 ------------------------------ #
    # Three defects found by re-fetching the official sources rather than trusting the
    # recorded reads. All three are fixed in this pass; none was inferred.
    ("F38", "An Amazon listing title changed between the 2026-11-14 read and 2026-11-15, so a published value was stale.",
     "Emeril 26 QT French Door \u2014 the listing-title row",
     "Found and fixed 2026-11-15 by arena/3ddfa50e. The stored title ended '| 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals.' and the live title on the same ASIN (B09B7SB46R, reached through https://link.amazon/B02NbDxp3) now ends '| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included'. The preset count is unchanged at 24; the wording around it is not. The row now carries the 2026-11-15 string, keeps the superseded string in a visible field, and states the date of the read. This is the same class of volatility as F14 (brand-hosted review counts that moved in 24 hours) and the reason every volatile value on this site must carry its read date.",
     ["S28"]),

    ("F39", "A source record was cited for a value it does not support: one registered URL stood in for three different product pages.",
     "All three products \u2014 the listing-title and ASIN rows",
     "Found and fixed 2026-11-15 by arena/3ddfa50e. Source S16 was registered with a single URL (https://www.amazon.com/dp/B0CDY277D3) but its title claimed to cover 'ASINs B0CDY277D3, B09B7SB46R, B08DKYBTPH', and it was cited as the source for all three products' listing titles and ASIN rows. For the Emeril and 8 Qt rows, the source link therefore took a reader to the Chefman 6 Qt listing. A citation that does not resolve to the page stating the value is the same defect class as F37. Fixed by registering each ASIN separately: S16 = B0CDY277D3, S28 = B09B7SB46R, S29 = B08DKYBTPH, and repointing every citation. The root build's row-source gate did not catch this because it checks that a row links to *a* registered official host, not that the host page actually states the value.",
     ["S16", "S28", "S29"]),

    ("F40", "Two different rows were published under the same flag number.",
     "Register integrity \u2014 F36",
     "Found and fixed 2026-11-15 by arena/3ddfa50e. The programme-level row recording the srctok-marker finding (added by sess-ce4070ad, itself renumbered from F32) was published as F36, and a product-level row in data/products.json recording the Chefman 6 Qt preset-count mis-citation was also published as F36. Both rendered on the Flagged page, so the register showed 38 rows with 37 distinct numbers and any citation of 'F36' was ambiguous. F28 records an earlier ID collision of the same kind, which means the rule was not enforceable. The programme-level row is renumbered F41; the product row keeps F36 because three session evidence files cite it by that number. A duplicate-ID build test now fails the build if this recurs.",
     ["S1"]),

    # arena-b1e7b4bc, verification round 2026-11-15 (additive): findings from the
    # line-by-line review of the new suggestions.html / questions.html layer (PR #58).
    # RENUMBERED at the merge seam 2026-11-15: authored as F38/F39, but PR #62
    # (arena/3ddfa50e) had already taken F38-F40 on main, so this session's rows
    # become F42/F43. Same precedent as the F32 -> F36 renumber; nothing else
    # about the rows changed.
    ("F42", "The operator's location is stated two different ways on the same domain, and neither statement comes from an official source.",
     "questions.html (Q-06) and suggestions.html (SG-10) vs the s2/ annex register (its F08)",
     "Recorded 2026-11-15 by arena-b1e7b4bc. The 2026-11-15 pages say the owner is in Osaka, Japan; the s2 annex register (data/flags.json, row F08) records a Norway residence. Both were written from agent-session environment context, not from anything the owner supplied in the repository and not from any official page, so neither can be verified from here and at most one can be right. The Japan wording matters because Q-06 and SG-10 build a store-targeting decision on it. Decision needed: the owner states their actual country once, one register row cites it, and the other wording is corrected to match; until then no eligibility conclusion (Q-06, SG-10, or the s2 register's F08) should be treated as settled.",
     []),
    # ---- pass 9, session 22f43836, 2026-11-15 ------------------------------- #
    # Both rows are about the repository as a published web property, not about a product
    # fact. Neither changes a published value. Each was measured, not assumed.
    ("F44", "The same site is published nine times from one repository, and eight of those copies are reachable at public URLs.",
     "Whole repository \u2014 GitHub Pages deployment",
     "Measured 2026-11-15 by this pass: 106 HTML files are published from the repository root. The maintained site is the 27 sitemap URLs generated by build.py; the remaining pages are seven earlier or parallel builds (dashboard/, annex-88769516/, session-3740f69d/, research/, s2/, site/, docs/), each with its own homepage, its own near-duplicate comparison of the same three products, and in two cases a visible Amazon price. Amazon's Program Policies \u00a72(b) permit price display only when Amazon serves the link or the data comes from Creators/PA API, so a published copy that shows a price is a compliance exposure this project has otherwise been careful to avoid. Google's own guidance (S30) states that the presumption is that individual pages match the overall quality of the domain, that a site reputation review weighs whether 'the same identical or near-identical content appears on multiple other sites', and that scaled content generated without added value for users should be excluded from search. Decision needed, and it is the owner's: keep the older builds published for auditability and accept the duplicate-content and compliance risk, or remove the duplicate pages and keep only their evidence files. This pass did not delete or edit another session's published output \u2014 that is not a unilateral decision to take. Full option set: SG-17 on the Suggestions page.",
     ["S30", "S2"]),

    ("F45", "The site's search-engine plumbing was incomplete: no page declared a canonical URL, and no page carried Open Graph or structured data.",
     "Whole root site \u2014 every generated page",
     "Found and fixed 2026-11-15 by this pass, and measured before the fix: 0 of 27 generated pages had rel=canonical, 0 had og:* tags, 0 had a Twitter card, 0 had JSON-LD (a repository-wide count that also included the annex builds was 33 canonicals of 106 pages, from other sessions' templates). Two consequences: with nine copies of the same content on one origin, nothing told a search engine which copy is maintained; and a shared link rendered as a bare URL. Fixed in build.py's layout() so every generated page now carries canonical, og:*, twitter:card and schema.org WebSite/Organization/BreadcrumbList/Article markup, and 404.html carries noindex and no canonical. Enforced by a new build guard (check_seo_metadata) so a later template edit cannot drop it. schema.org Product/Offer/AggregateRating is deliberately NOT emitted: the site publishes no Amazon price or star rating (\u00a72(b), \u00a76(t)), so product markup would either be empty or would assert a number this project refuses to publish.",
     ["S30", "S31", "S2"]),

    ("F43", "Two wording advisories on the Suggestions and Questions pages (reader-facing precision, no data value affected).",
     "suggestions.html and questions.html (PR #58, X-633b115f)",
     "Recorded 2026-11-15 by arena-b1e7b4bc. (a) The Suggestions lede says 'None of them has been implemented', but for SG-03, SG-04, SG-05 and SG-11 option A is the current, already-implemented state ('Keep...', 'Keep blank and link to the live Amazon page (current, compliant)'), so those rows read more accurately as 'confirm the current state' than as pending work. (b) Q-01's 'How to find out' says to check the owner's Associates account for which tag the short links carry - the tag is not observable from the account's tracking-ID page either (flag F6); only whoever created the short links knows the mapping. Decision needed: reword the lede and the Q-01 cell, or accept the current phrasing. Both rows' facts and sources check out; this flag is about wording only.",
     []),

    # ---- arena/792c279e-zone1, task T20, 2026-11-15 -------------------------------- #
    # Findings from the live line-by-line re-verification performed in this pass. Full
    # evidence, including the exact strings read back from each official page, is in
    # reports/verification-2026-11-15.md. No published product value was changed by this
    # pass; each row below either records a source-liveness change or a conflict that a
    # human has to settle.
    ("F47", "There are two flag registers in this repository, they contradict each other, and both are readable from the live site.",
     "data/flags.json (F01-F27) vs flagged.html (F1-F43)",
     "Found 2026-11-15 by arena/792c279e-zone1. data/flags.json still records F02 'The official Standard Commission Income schedule redirected to a sign-in page' and F01-F04 language asserting that the short links resolve 'with different ASINs'. The re-verification performed in this same pass read the Standard Commission Income Statement in full without any login (Table 1: Kitchen 4.50%, All Other 4.00%) and re-confirmed all three destinations, so the older register's two statements are contradicted by a live read. The rendered Flagged page says the opposite of data/flags.json on the commission question, so a reader who follows two links reaches two different answers. This pass did not edit data/flags.json: it is consumed by scripts/build_s2_site.py and scripts/build.mjs, and re-keying it would silently re-point another build's citations. Decision needed: name one register canonical, then either re-key the other or replace its contradicting sentences with a dated pointer to this page. Evidence: the two files themselves, and reports/verification-2026-11-15.md section 1.",
     ["S3", "S16", "S28", "S29"]),

    ("F48", "The Amazon listing for the Emeril 26 QT says six cooking accessories; the site publishes seven.",
     "Emeril 26 QT French Door — the Included accessories row",
     "Found 2026-11-15 by arena/792c279e-zone1 while re-reading the live listing title. ASIN B09B7SB46R's title now ends '... Extra Large Interior, Six Cooking Accessories Included', while the site's own row publishes 7, sourced to the brand product page and the owner's manual. This is not necessarily a contradiction: a listing can count a rotisserie spit and its forks as one accessory, or bundle differently from the retail box, and the brand page and manual are the sources this site chose. The value was therefore NOT changed — altering it would mean replacing a manual-sourced number with a listing-title number on a row whose product identity is itself unconfirmed (F1, F2). Decision needed: count the accessories in the box against the manual's accessory list, then publish one number with that source. Evidence: reports/verification-2026-11-15.md section 3 row V21.",
     ["S28", "S14", "S15"]),

    ("F49", "The 2026-11-15 live pass could not retrieve the one fact that closes four high-severity flags, and the site now says why in the place a buyer will look.",
     "All three products — the model-number mapping",
     "Recorded 2026-11-15 by arena/792c279e-zone1. The three Amazon detail pages were fetched again and returned the buy box, the protection plans and the 'Customers who viewed this item also viewed' blocks, but not the 'Product information' table that carries the model number. That block is rendered client-side, so an automated read cannot see it; a human browser can, in about ten seconds per listing. This is recorded as its own row because seven sessions have now listed F1/F2/F32/F33 as 'needs a human' without saying why the machine cannot do it, which invites an eighth session to try again. It is now also stated on picks.html, handover.html and hand-over item H1 rather than only in the register. Evidence: reports/verification-2026-11-15.md section 3 row V24.",
     ["S16", "S28", "S29"]),

    # ------------------------------------------------------------------ #
    # Verification pass 9 - session 42ca97ad, 2026-11-15.
    # Raw evidence: session-42ca97ad/EVIDENCE-2026-11-15.md
    # Renumbered at the merge seam: F44/F45/F47 were taken by PR #69/#70/#71
    # (duplicate builds, canonical/structured data, two flag registers), so
    # these four rows start at F50.
    # ------------------------------------------------------------------ #
    ("F54", "The Amazon department category is now read directly on all three listings; the rate itself still needs the Earnings report.",
     "All three products \u2014 commission rate",
     "Recorded 2026-11-15 by session 42ca97ad. The annex register\u2019s row F-06 recorded that the browse-node path \u2018Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers\u2019 had been read directly on B09B7SB46R only, and named reading the other two listings as the confirmation step. This session fetched all three supplied link.amazon short links and read the identical path on B0CDY277D3 and B08DKYBTPH as well, so the evidence is now three for three rather than one for three. It still does not establish the category Amazon applies when a commission is settled: only the Associates Earnings report names the category on a shipped line, so the two candidate rows (Kitchen 4.50%, All Other 4.00%) remain the honest presentation until a sale exists. Decision needed: publish Kitchen 4.50% as the working rate with the breadcrumb cited (SG-10 path A), or keep both rows until the first Earnings report lands.",
     ["S3", "S16", "S28", "S29"]),
    ("F55", "Eleven article sentences spliced a published display label into a mid-sentence position. Found, fixed and guarded.",
     "articles/ prose, and the build\u2019s article gate",
     "Recorded 2026-11-15 by session 42ca97ad. The article prose in data/articles.json interpolates published values into sentences. Eleven of those interpolations put a display label \u2014 \u2018Two 3-quart baskets\u2019, \u2018Designed for 4-6 people\u2019, \u2018Fries, Chicken, Fish, Meat (one-touch)\u2019, \u2018Limited 1-year warranty \u2026\u2019 \u2014 into a position where its capital is wrong, so the sentences read as machine output: \u2018The dual-basket unit is 6 Qt / 5.67 L as Two 3-quart baskets\u2019, \u2018splits a 6 Qt / 5.67 L cavity into Two 3-quart baskets\u2019. The defect was invisible to every earlier verification pass, because each value is genuinely published and correct in a table; it only appears when the page is read as prose, which is what a shopper does. It survived PR #71\u2019s full rewrite of data/articles.json, which re-introduced the same ten sentences and added an eleventh in a new article. Fixed by adding a {{value::prose form}} syntax whose prose form may differ from the published value in letter case and nothing else, enforced by check_articles(), and by adding check_article_splices(), which fails the build when a capitalised value is spliced into a mid-sentence position. Both guards were proven to fire: the build failed on exactly these defects before the fix and passes after it. No published value changed and no source changed.",
     ["S1"]),
    ("F56", "The Application Review Process page was not re-read this pass; its figures are carried forward from an earlier fetch.",
     "S4 \u2014 the Associates application criteria",
     "Recorded 2026-11-15 by session 42ca97ad. This pass re-fetched the Program Policies, the Standard Commission Income Statement, both Chefman product pages, the Emeril product page, all three owner\u2019s manuals, all three supplied short links, 16 CFR Part 255 and 16 CFR Part 465. It did not load the Application Review Process page (S4). The figures the repository carries for it \u2014 three qualifying sales within 180 days, roughly ten posts, content recent within about sixty days, a social follower floor of about five hundred \u2014 are carried forward from earlier logged fetches and are NOT re-confirmed by this pass. The sixty-day recency requirement is load-bearing for any content-refresh schedule the owner adopts, so it must be re-read before it is used as a scheduling rule rather than quoted from this repository. Note that a sibling pass on the same day did re-read this page and reported the same four figures, which corroborates them but does not change what this session itself fetched. What was and was not fetched is listed item by item in session-42ca97ad/EVIDENCE-2026-11-15.md section 6. **Re-read 2026-11-16 by arena/9fccce0c-zone1: all four figures are confirmed verbatim from the live page** \u2014 \u201cwe require at least three within the first 180 days\u201d, \u201ca good rule of thumb is at least 10 posts\u201d, \u201cContent on your website must be recent (generally within the last 60 days)\u201d and \u201cin most cases, at least 500\u201d organic followers/likes \u2014 so the carried-forward part of this row is closed, and question Q-19 moves from *missing* to *known and sourced* with its answer on the row. Evidence: reports/verification-2026-11-16-9fccce0c.md row V3.",
     ["S4"]),
    ("F57", "Three files under data/ are read by no build, and one of them is a stale copy of a register that is published.",
     "data/flagged.json, data/commission-rates.csv, data/products.csv",
     "Recorded 2026-11-15 by session 42ca97ad. A reference scan of every loader in the repository shows that scripts/build_site.py and scripts/verify_site.py read data/verified/, not data/. The root-level data/flagged.json is therefore an orphan: it holds a 13-row register whose live counterpart is data/verified/flagged.json (17 rows), and the two disagree across 85 lines \u2014 including the browse-node observation this pass has just updated, which would otherwise leave two registers saying different things about the same fact. data/commission-rates.csv and data/products.csv are read by nothing in the repository; the first is a CSV transcription of the Standard Commission Income Statement, the second the 2026-11-13 link-check ledger that records the bare-token 404 and the fallback redirect, and both are evidence worth keeping if they are labelled as evidence. Nothing published depends on any of the three, so this is a maintenance risk rather than a correctness bug, but a reader who opens data/flagged.json sees a register that no longer matches the site. This row is narrower than F47, which covers the same class of problem for data/flags.json; the two are kept separate because the files and the contradictions are different. Decision needed: delete the three orphans, or keep them explicitly as dated evidence with a header that says so.",
     ["S1"]),

    ("F58", "A register preamble repeated a sentence on the published page. Found on the deployed site, fixed, and guarded.",
     "questions.html \u2014 the preamble above the register",
     "Found 2026-11-15 by session 42ca97ad, after PR #78 merged: the sentence \u2018Questions in the \u2018known and sourced\u2019 state carry their answer on the row \u2026\u2019 appeared twice in the preamble above the questions register. The cause was the one-shot editor that adds the register rows (session-42ca97ad/apply_pass9_edits.py): it appended the sentence to the preamble unconditionally, so running it a second time appended it again. The build did not catch it, because the duplicate-ID guard sees IDs, the published-value guard sees numbers, and a repeated sentence is neither. Fixed by making the editor idempotent, by removing the duplicate from data/questions.json, and by adding check_register_preambles(), which fails the build if any register preamble repeats a sentence. The guard was proven to fire on an injected duplicate. The same edit also corrected the preamble's own claim that the page \u2018separates three things\u2019 - it has always described four states, which is what the legend on the page lists.",
     ["S1"]),


    # ---- arena/ad8105b3, 2026-11-16 ------------------------------------------------- #
    # Both found by reading the repository's own registers rather than the live sources.
    # Neither changes a published value; both are records a reader can act on.
    ("F59", "The repository serves six separate executive summaries, five of them stale and none labelled stale.",
     "EXECUTIVE-SUMMARY.md, EXECUTIVE_SUMMARY.md, EXECUTIVE-SUMMARY-PASS8.md, EXECUTIVE-SUMMARY-PASS9.md, EXECUTIVE-SUMMARY-PASS9-42CA97AD.md, executive-summary.html",
     "Recorded 2026-11-16 by arena/ad8105b3. A read of the repository root finds six files whose names all claim to be the executive summary: the generated executive-summary.html (current, built from data), EXECUTIVE-SUMMARY.md, and four earlier or parallel-session Markdown files (EXECUTIVE_SUMMARY.md, EXECUTIVE-SUMMARY-PASS8.md, EXECUTIVE-SUMMARY-PASS9.md, EXECUTIVE-SUMMARY-PASS9-42CA97AD.md). GitHub Pages publishes the repository root, so all six are reachable by URL. At least one, EXECUTIVE_SUMMARY.md, is already recorded in this register (F28) as asserting 'Identity verified. All three short links resolve to Amazon.com product pages with different ASINs', which this site's reconciled position contradicts. This pass did not delete or rewrite any of them: they are other sessions' committed records, and deleting another session's evidence is not a repair. The live site links only executive-summary.html. Decision needed: keep one Markdown briefing and move the rest under an archive directory with a one-line header saying what superseded them, or add a banner to each. Evidence: the six files themselves, and the root README.",
     ["S1"]),

    ("F60", "The s2 annex's requirements register cites two paths that do not exist, and its commission row rests on a premise the annex itself has since corrected.",
     "data/s2/requirements.json rows R-01 and R-08",
     "Recorded 2026-11-16 by arena/ad8105b3 while building the root requirements register (requirements.html). Two defects in the annex register. (1) R-01 'Collect and organise a full list of requirements' gives its implementation path as 'data/requirements.json rendered on Requirements page'. There is no data/requirements.json: the file is data/s2/requirements.json, and it renders at s2/pages/requirements.html. So the repository's only requirements register pointed the reader at a different, non-existent file. This is the third occurrence of the same defect class (after F14 and F38 in this register), which is why the new root register has check_requirement_paths() failing the build on any cited path that does not exist, and that guard was proven to fire on an injected bad path. (2) R-08 'Analyse commission potential' is marked blocked with the reason 'login-gated rate card (F-04)'. data/s2/flags.json row F-04 is itself titled 'CORRECTED — a public commission table does exist' and records that the Standard Commission Income Statement is readable without a login, which this pass re-confirmed live on 2026-11-16: Table 1 renders 'Physical Books, Kitchen, Automotive 4.50%'. The genuine remaining gap is narrower — Table 1 is keyed to categories, not ASINs — and the root register states it that way. Neither row was edited in the annex: data/s2/requirements.json is another session's published output. Decision needed: re-point R-01 at the real path, and restate R-08's blocking reason as the ASIN-to-category mapping rather than a login. Evidence: the two annex files and the commission page.",
     ["S3"]),

    # ---- arena/63a2c638, integration pass 9, 2026-11-15 ----------------------------- #
    # Three findings from re-reading the official sources rather than trusting recorded
    # reads. F51 and F52 were found by reading a source the site had never used; F53 is a
    # scope limit on a value this pass added, published so it cannot be misread.
    ("F51", "The brand's own store reports a different product weight than the brand's own specification block, and this site publishes the specification-block figure.",
     "Chefman 6 Qt Dual-Window (RJ38-SQPF-3TDB-2W) and Chefman 8 Qt TurboFry (RJ38-SQSS-8T)",
     "Recorded 2026-11-15 by arena/63a2c638, round 9. The Chefman product pages print a Specifications block: the 6 Qt page says 'Weight: 13.3 lbs / 6.03 kg' and the 8 Qt page says 'Weight: (8 Qt Model) 12.8 lbs / 5.8 kg'. Those are the figures this site publishes, cited to S10 and S12. The same brand's own commerce endpoint, read the same day, reports the variant weight as 14.51 lb / 6,582 g for RJ38-SQPF-3TDB-2W (S32) and 13.4 lb / 6,078 g for RJ38-SQSS-8T (S33). The endpoint figure is the weight Shopify carries for shipping, so the most likely reading is product weight versus packaged weight - but neither page says so, and the site must not choose between them by inference. No published value was changed: the specification block remains the cited source because that is the document the published row points at. Decision needed: state in each weight row whether the figure is the product or the packaged weight, or publish both.",
     ["S10", "S12", "S32", "S33"]),

    ("F52", "The open-questions register states that dimensions, weight and warranty are missing for all three products; the product dataset already publishes eight of those nine values from official sources.",
     "questions.html row Q-06 vs data/products.json",
     "Recorded 2026-11-15 by arena/63a2c638, round 9. Q-06 asks 'What are the exterior dimensions, weight and warranty terms for each of the three products?' and is filed as 'not_stated'. Checking the nine cells against the dataset this pass: exterior dimensions are published for all three (6 Qt from S10, Emeril from S14, 8 Qt from S12); warranty is published for all three (S10, S14, S13); weight is published for both Chefman models (S10, S12). One cell - the Emeril 26 QT product weight - is genuinely absent, because neither the brand page nor the owner's manual states one. So the register overstates the gap by eight cells. This matters in both directions: a reader using Q-06 to decide what to research would redo work already done, and a reader trusting the product pages would think the register is stale. Q-06 was narrowed this pass to the single cell that is actually open, and is cross-linked to this row. No data value moved.",
     ["S10", "S12", "S13", "S14"]),

    ("F61", "The canonical compliance register and platform blueprint had never carried the two clauses that govern an AI-agent affiliate platform, and three published pages pointed at a flag number that does not exist.",
     "Whole site \u2014 compliance.html, platform.html, questions.html, suggestions.html, data.html",
     "Found 2026-11-16 by arena/9fccce0c-zone1 during verification pass 10, and fixed in the same pass. Two independent defects. "
     "(a) Missing clauses. The Associates Program Policies page (S2, \u201cUpdated: April 14, 2026\u201d) carries IP License \u00a74 "
     "\u201cAgents\u201d (the Agent Terms) and Participation Requirements \u00a75, both read verbatim live on 2026-11-16. Neither appeared "
     "anywhere in the canonical build: data/compliance.json held 0 occurrences of \u201cAgent Terms\u201d and data/platform.json held 0 occurrences of "
     "\u201cAgent\u201d, although the brief this project answers is explicitly an AI-powered affiliate platform and the root site ships a "
     "platform blueprint that proposes automated research. They are now requirements C17 and C18, with platform guardrail G11; the scope "
     "question they raise is published as Q-21 and the design decision as SG-22, and neither is answered by inference. "
     "(b) Dangling pointer. data/questions.json, data/suggestions.json and data/sources.json each told the reader to see the flag numbered 46 "
     "for the Application Review Process recency criterion. No such flag exists in the canonical register, which runs F1\u2013F45 and F47\u2013F58, "
     "and none exists in the legacy data/flags.json register either, which runs F01\u2013F27. The three pointers now name F56, the row that actually "
     "covers it. A new build guard, check_register_cross_references(), fails the build if any generated page cites a flag id, source id, question id "
     "or suggestion id that is not in the register it points at, so the class of defect cannot recur silently. Evidence: "
     "reports/verification-2026-11-16-9fccce0c.md section E.",
     ["S2", "S4"]),
    ("F62", "IP License \u00a74 (the Agent Terms) was not read end to end, so the full list of agent-identification requirements is not yet on the record.",
     "S2 \u2014 the IP License section of the Program Policies page",
     "Recorded 2026-11-16 by arena/9fccce0c-zone1. The Associates Program Policies page renders its IP License as one long table, and the "
     "markdown conversion used for that pass collapsed part of it. Everything quoted in requirement C17 was read directly in the response body, "
     "but the section was not read to its end: sub-part (a) refers to \u201cthe requirements in section 3 of these Agent Terms\u201d, and the text of "
     "that section was not visible in the render. The Agent Terms are therefore published as the rules this pass could read, with the limit stated "
     "on the row, rather than as a complete checklist. Decision needed: read IP License \u00a74 in a browser, in full, and extend requirement C17 "
     "if it adds anything \u2014 before the research agent is built (SG-22). Evidence: reports/verification-2026-11-16-9fccce0c.md, the limit stated under "
     "section A.",
     ["S2"]),
    ("F53", "The Amazon browse-node breadcrumb is now published for two ASINs, and it does not settle which commission rate applies.",
     "All three products - the 'Amazon browse node' row and open question Q-11",
     "Recorded 2026-11-15 by arena/63a2c638, round 9, at the same time as the value itself was added, so the limit travels with the value. Both Chefman listings render the breadcrumb 'Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers' (S16, S29). It is tempting to read 'Kitchen' there and apply the 4.50% Kitchen rate from the Commission Income Statement (S3). That would be an inference, not a source: S3's categories are commission categories defined by the Associates programme, Amazon's browse nodes are a shopper-navigation taxonomy, and Amazon publishes no mapping between the two. The same breadcrumb begins 'Home & Kitchen', and S3 also carries 'Home' at 3.00%, so the breadcrumb alone cannot even tell you which of the two it resembles. The site therefore continues to show the commission rate as unconfirmed (Q-11) and now shows the browse node as a separate, sourced fact. The Emeril browse node is blank: three fetches of that ASIN on 2026-11-15 returned Amazon's automated 'Continue shopping' checkpoint instead of the listing page, and a value that was never rendered cannot be recorded.",
     ["S3", "S16", "S29", "S28"]),
]

# Repository files that evidence a programme-level flag. Used where the irregularity is a
# fact about this repository, so the repository itself (on GitHub) is the source.
REPO_EVIDENCE = {
    "F20": ["s2/", "site/", "dashboard/", "research/", "session-3740f69d/", "docs/"],
    "F22": ["EXECUTIVE_SUMMARY.md"],
    "F23": ["scripts/build.mjs"],
    "F25": ["scripts/check_links.py", "dashboard/", "research/", "site/", "s2/",
            "session-3740f69d/", "annex-88769516/"],
    "F26": ["data/platform.json"],
    "F29": ["session-54c66535/EVIDENCE-2026-11-14.md", "data/products.json"],
    "F30": ["session-54c66535/EVIDENCE-2026-11-14.md", "session-54c66535/pass6.json"],
    "F31": ["session-54c66535/EVIDENCE-2026-11-14.md"],
    "F32": ["session-6b2eddeb/EVIDENCE-2026-11-14.md", "data/products.json", "site/", "research/"],
    "F33": ["session-6b2eddeb/EVIDENCE-2026-11-14.md"],
    "F34": ["EXECUTIVE_SUMMARY.md"],
    "F35": ["build.py", "site/", "session-3740f69d/"],
    "F41": ["session-81495d2d/EVIDENCE-2026-11-14.md", "session-ce4070ad/EVIDENCE-2026-11-14.md"],
    "F47": ["data/flags.json", "data/sources.json"],
    "F48": ["data/products.json"],
    "F49": ["reports/verification-2026-11-15.md"],
    "F42": ["suggestions.html", "questions.html", "data/flags.json", "s2/"],
    "F43": ["suggestions.html", "questions.html"],
    "F44": ["dashboard/", "annex-88769516/", "session-3740f69d/", "research/", "s2/", "site/", "docs/", "sitemap.xml"],
    "F45": ["build.py", "sitemap.xml"],
}

VERDICTS = {
    "chefman-6qt-dual-basket":
        "The published specification set is the most complete of the three: capacity, temperature range, dimensions, weight, power draw, safety approval and warranty are all stated by the manufacturer. Two independently controlled baskets with a Sync Finish function and a 450 °F ceiling address the main real-world complaint about single-basket air fryers — that you cannot cook two things at different temperatures at once. The one number a shopper most wants, cost per quart, cannot be computed here because the Amazon price is not available to this site by policy; the brand list price of $119.99 for 6 quarts is the only comparable figure that can be stated.",
    "emeril-26qt-french-door":
        "The largest cavity in the set by a wide margin (26 qt against 6 qt and 8 qt) and the only unit that is an oven rather than a basket. The manufacturer documents the power draw (1700 W), the temperature range (75–500 °F) and the physical footprint, which is what actually decides whether it fits a kitchen. On preset count the manual is the controlling document: its chart names exactly 24 presets, which matches the description text and the Amazon title rather than the spec block's 25. The brand's own on-site rating is unusually low (2.6 from 25 reviews) and is reported here as displayed, not softened.",
    "chefman-8qt-turbofry":
        "A conventional single-basket 8-quart air fryer with a documented 200–400 °F range, four food-type presets and dishwasher-safe nonstick parts. The unresolved problem is that the Amazon listing title advertises a 450 °F Hi-Fry mode and bake/dehydrate/frozen functions that the RJ38-SQSS-8T page and manual do not document. A 2026-11-14 read found that Chefman sells a second 8-quart SKU, RJ38-8T-BLACK, whose page states exactly that Hi-Fry mode and exactly those four functions — so the listing probably describes a different unit rather than a stale page (flag F33). Until someone opens the listing and reads the model number, the honest position is that the temperature ceiling of the unit shipping against this ASIN is unknown, and the buyer should read the manual that arrives with the unit.",
}


def page_category():
    rows = "".join(
        f"""<tr>
          <td class="num">{p['rank']}</td>
          <td><a href="../products/{p['slug']}.html">{e(p['short_name'])}</a><div class="tiny muted">{e(p['name'])}</div></td>
          <td>{e(p['brand'])}</td>
          <td class="num">{e(p['asin']['v'])}</td>
          <td>{e(p['specs'][0]['value'])} {src_links(p['specs'][0]['source'])}</td>
          <td>{e(p['pricing']['brand_list_price']['v'])} {src_links(p['pricing']['brand_list_price']['s'])}</td>
          <td class="blank">not displayed {src_link("S2")}</td>
          <td>{len(p['flags'])}</td>
        </tr>"""
        for p in PRODUCT_LIST
    )
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Kitchen appliances</p>
<h1>Category: kitchen appliances — air fryers</h1>
<p class="lede">The three supplied links were observed landing on air fryer or air fryer-oven listings on 2026-11-13/14; product identity from the tokens is still unconfirmed (F14–F16), so this category label is provisional. The table below lists every tracked product with its verified capacity, the manufacturer's list price and its open flags. Amazon price is blank on every row by policy, not by oversight.</p>

<div class="tablewrap">
<table>
  <caption>Tracked products in this category</caption>
  <thead><tr>
    <th>#</th><th>Product</th><th>Brand</th><th>ASIN</th><th>Capacity (verified)</th>
    <th>Brand list price</th><th>Amazon price</th><th>Flags</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>
</div>

<h2>Why the category matters commercially</h2>
<p class="small">Amazon's published rate table (reproduced in full on <a href="../compliance.html">Compliance</a>) puts <strong>Kitchen at 4.50%</strong>, <strong>Home at 3.00%</strong> and the fallback row, <strong>All Other Categories, at 4.00%</strong> {src_links(['S3'])}. A countertop cooking appliance could plausibly fall in any of those, and Amazon does not publish the assignment. That 1.5-point spread between the best and worst case is why the platform blueprint scores products on scenarios rather than a single number.</p>

<h2>Rules that shape every page in this category</h2>
<div class="tablewrap">
<table>
  <caption>Category-level constraints, each with a source</caption>
  <thead><tr><th>Constraint</th><th>Effect on this category's pages</th><th>Source</th></tr></thead>
  <tbody>
    <tr><td>Prices only from Amazon-served content or the API</td><td>No Amazon price appears; manufacturer list price shown separately and labelled.</td><td>{src_links(['S2'])}</td></tr>
    <tr><td>No Amazon star ratings or customer reviews without the API</td><td>Ratings column removed; brand-hosted ratings shown only as vendor-published social proof.</td><td>{src_links(['S2'])}</td></tr>
    <tr><td>No price tracking or alerts</td><td>No price-history widget can be built for appliances like these.</td><td>{src_links(['S2'])}</td></tr>
    <tr><td>No misleading product claims</td><td>Where the listing and the manual disagree — the 8 Qt 450 °F case — neither is asserted.</td><td>{src_links(['S2', 'S8'])}</td></tr>
  </tbody>
</table>
</div>
"""
    curl = page_url("categories/kitchen-appliances.html")
    ld = [
        {
            "@type": "CollectionPage",
            "@id": curl + "#webpage",
            "url": curl,
            "name": "Category: Kitchen",
            "description": "Kitchen appliance category page: three tracked air fryers with verified capacity, manufacturer list price and open flags.",
            "isPartOf": {"@id": SITE_URL + "/#website"},
            "about": {"@id": SITE_URL + "/#organization"},
            "inLanguage": "en-US",
        },
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Kitchen appliances", curl),
        ]),
        {
            "@type": "ItemList",
            "@id": curl + "#products",
            "name": "Tracked air fryers",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "name": pr["short_name"],
                    "url": page_url(f"products/{pr['slug']}.html"),
                }
                for i, pr in enumerate(PRODUCT_LIST, start=1)
            ],
        },
    ]
    return layout("categories/kitchen-appliances.html", "Category: Kitchen", body,
                  active="categories/kitchen-appliances.html",
                  description="Kitchen appliance category page: three tracked air fryers with verified capacity, manufacturer list price and open flags.",
                  jsonld_blocks=ld)


def page_compare():
    fields = []
    seen = set()
    for p in PRODUCT_LIST:
        for s in p["specs"]:
            if s["label"] not in seen:
                seen.add(s["label"])
                fields.append(s["label"])

    head = "".join(
        f'<th><a href="../products/{p["slug"]}.html">{e(p["short_name"])}</a><div class="tiny muted" style="font-weight:400">candidate ASIN {e(p["asin"]["v"])} (unconfirmed)</div></th>'
        for p in PRODUCT_LIST
    )
    rows = []
    for label in fields:
        cells = []
        for p in PRODUCT_LIST:
            match = next((s for s in p["specs"] if s["label"] == label), None)
            if match is None:
                # Field absent from this product's verified dataset — point at the
                # full dataset / blank-field register rather than inventing a source.
                cells.append('<td class="blank">— not documented — <div class="tiny"><a href="flagged.html">see blanks</a></div></td>')
            elif match["value"] is None:
                cells.append(f'<td class="blank">— not confirmed — <div class="tiny">{src_links(match["source"])}</div></td>')
            else:
                cells.append(f'<td>{e(match["value"])}<div class="tiny">{src_links(match["source"])}</div></td>')
        rows.append(f'<tr><td><strong>{e(label)}</strong></td>{"".join(cells)}</tr>')

    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Comparison</p>
<h1>Side-by-side, blanks included</h1>
<p class="lede">Most comparison tables hide gaps by quietly dropping the row. This one keeps every row and marks the gaps, because "we don't know" is a different statement from "it doesn't have it". Every filled cell links to the official page it came from.</p>

<div class="tablewrap">
<table>
  <caption>Verified-only comparison matrix</caption>
  <thead><tr><th style="min-width:170px">Field</th>{head}</tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
</div>

<h2>The three real differences</h2>
<div class="grid grid-3">
  <div class="card">
    <h3 style="margin-top:0">Form factor</h3>
    <p class="small">Two 3 qt-class drawers, one 8 qt basket, or a 26 qt oven cavity. This decides what you can cook simultaneously far more than raw litres do.</p>
  </div>
  <div class="card">
    <h3 style="margin-top:0">Documented ceiling</h3>
    <p class="small">450 °F (Chefman 6 Qt, per {src_link('S10')}), 400 °F (Chefman 8 Qt, per {src_link('S12')}), 500 °F (Emeril, per {src_link('S15')}). The 8 Qt's listing claims 450 °F — see the conflict note.</p>
  </div>
  <div class="card">
    <h3 style="margin-top:0">Information quality</h3>
    <p class="small">The Chefman 6 Qt publishes the most complete spec sheet, and its owner manual settles the questions the product page left open. The Chefman 8 Qt still has one unresolved contradiction between the listing and its own manual, logged on the flagged page.</p>
  </div>
</div>

<h2>Decision rules</h2>
<ol class="tight small">
  <li><strong>Cooking two different things at once, on a normal counter?</strong> The dual-basket unit is the only one designed for that.</li>
  <li><strong>Feeding four to six people from one basket?</strong> The 8 qt single basket is the documented "4–6 people" unit {src_links(['S12'])}.</li>
  <li><strong>Replacing a toaster oven as well?</strong> Only the 26 qt oven-style unit does rotisserie and toast, and it is the one whose footprint you should measure first (16.9 × 15.8 × 14.8 in {src_links(['S14'])}).</li>
  <li><strong>Worried about the 450 °F claim on the 8 qt?</strong> Read the manual that ships with the unit. This site will not resolve that conflict for you by guessing.</li>
</ol>

<h2>Revenue scenarios, not forecasts</h2>
{calc_widget()}

<p class="small" style="margin-top:1.5rem"><a href="../guides/buying-guide-air-fryers.html">Read the buying guide →</a> · <a href="../flagged.html">See what is unresolved →</a></p>
"""
    curl = page_url("compare.html")
    ld = [
        {
            "@type": "ItemList",
            "@id": curl + "#products",
            "name": "Three air fryers compared",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "name": pr["short_name"],
                    "url": page_url(f"products/{pr['slug']}.html"),
                }
                for i, pr in enumerate(PRODUCT_LIST, start=1)
            ],
        },
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Comparison", curl),
        ]),
    ]
    return layout("compare.html", "Comparison", body, active="compare.html",
                  description="Verified-only comparison of three air fryers, with gaps left visible and every value linked to an official source.",
                  jsonld_blocks=ld)


def page_guide():
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Buying guide</p>
<h1>How to choose an air fryer without being sold to</h1>
<p class="lede">A form-factor decision dressed up as a shopping decision. Work down these five questions in order and most of the market falls away before you look at a single price.</p>

<p class="small muted">Written for this product set. Every factual number links to the manufacturer's own page or manual; no product is claimed to have been tested.</p>

<h2>1. Which form factor do you actually need?</h2>
<div class="tablewrap">
<table>
  <caption>Form factor, described by what is documented</caption>
  <thead><tr><th>Form factor</th><th>What it is good at</th><th>In this set</th></tr></thead>
  <tbody>
    <tr><td>Dual-basket</td><td>Two foods, two temperatures, one finish time. The Sync Finish feature exists precisely so both drawers land together {src_links(['S10'])}.</td><td><a href="../products/chefman-6qt-dual-basket.html">Chefman 6 Qt</a></td></tr>
    <tr><td>Single large basket</td><td>One big batch. Documented as sized for 4–6 people {src_links(['S12'])}.</td><td><a href="../products/chefman-8qt-turbofry.html">Chefman 8 Qt</a></td></tr>
    <tr><td>Countertop oven</td><td>Toast, bake, rotisserie and air fry in a 26 qt cavity — replaces appliances rather than adding one {src_links(['S14', 'S15'])}.</td><td><a href="../products/emeril-26qt-french-door.html">Emeril 26 QT</a></td></tr>
  </tbody>
</table>
</div>

<h2>2. Match capacity to the household, using published numbers</h2>
<p class="small">Quart figures are nominal cavity volume, not usable food volume, and no manufacturer in this set publishes a usable-volume figure. The only official household-size statement in the set is Chefman's "designed for 4–6 people" for the 8 qt {src_links(['S12'])}. Treat every other capacity-to-people mapping you read online, including your own, as an estimate.</p>

<h2>3. Check what the top temperature setting really does</h2>
<div class="callout">
  <strong>The single most useful thing you can do before buying</strong>
  <p class="small">Find the owner's manual and read the temperature range, not the box. A "450 °F" badge can mean a full-cycle setting, a two-minute finish mode, or nothing at all. In this product set the Chefman 8 Qt's Amazon listing advertises 450 °F Hi-Fry while its own manual documents 200–400 °F {src_links(['S12', 'S13', 'S16'])}. That contradiction is unresolved and is <a href="../flagged.html">flagged</a> rather than smoothed over.</p>
</div>

<h2>4. Check cleaning before you check features</h2>
<p class="small">All three units in this set document nonstick, dishwasher-safe baskets or racks {src_links(['S10', 'S12', 'S14'])}. Where they differ is documented cleaning caveats: Chefman's manual warns specifically against aerosol spray on the nonstick coating {src_links(['S13'])}. That is the kind of line that decides whether a coating survives a year.</p>

<h2>5. Check the footprint against your counter</h2>
<div class="tablewrap">
<table>
  <caption>Published dimensions — measure your counter, not your shelf</caption>
  <thead><tr><th>Product</th><th>Dimensions</th><th>Weight</th><th>Source</th></tr></thead>
  <tbody>
    <tr><td>Chefman 6 Qt Dual</td><td>13.38 × 11.81 × 10.63 in</td><td>13.3 lb</td><td>{src_links(['S10'])}</td></tr>
    <tr><td>Chefman 8 Qt TurboFry</td><td class="blank">— not published —</td><td class="blank">— not published —</td><td>{src_links(['S12', 'S13'])}</td></tr>
    <tr><td>Emeril 26 QT</td><td>16.9 × 15.8 × 14.8 in</td><td class="blank">— not published —</td><td>{src_links(['S14'])}</td></tr>
  </tbody>
</table>
</div>
<p class="tiny muted">The Emeril manual also specifies clearance: at least 5 inches of free space on top, back and sides, and never under a hanging cabinet {src_links(['S15'])}. An oven-style unit that is 14.8 in tall needs roughly 20 in of vertical clearance to be used as documented.</p>

<h2>What this guide will not do</h2>
<ul class="tight small">
  <li><strong>Rank them.</strong> There is no honest ranking without testing, and no testing was done.</li>
  <li><strong>Quote an Amazon price.</strong> Prices change and may only be shown when Amazon serves them or via the official API {src_links(['S2'])}.</li>
  <li><strong>Show Amazon star ratings.</strong> Same restriction {src_links(['S2'])}.</li>
  <li><strong>Promise a result.</strong> No claim is made about cooking performance, because none was observed.</li>
</ul>

<h2>Ready to compare</h2>
<p class="small"><a class="btn btn-ghost" href="../compare.html">Open the comparison matrix</a></p>
"""
    return layout("guides/buying-guide-air-fryers.html", "Buying guide", body,
                  active="guides/buying-guide-air-fryers.html",
                  description="How to choose an air fryer: form factor, documented capacity, real temperature ceilings, cleaning and footprint.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Buying guide", page_url("guides/buying-guide-air-fryers.html")),
    ])]
              )


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
<h1>Compliance, quoted rather than summarised</h1>
<p class="lede">{len(COMPLIANCE['requirements'])} requirements that govern this site, each with the source text, a link to the official document, and a plain statement of how the build satisfies it. Where a rule is inconvenient, the rule wins and the feature is dropped.</p>

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
    prog_flags = PROGRAMME_FLAGS
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
<p class="lede">Everything this project could not confirm, could not reconcile, or found contradicted between official sources. These items are published rather than hidden, they do not block the site, and each one names the decision a human needs to make.</p>

<div class="grid grid-4" style="margin-bottom:1rem">
  <div class="stat bad"><div class="n">{len(prog_flags) + len(prod_flags)}</div><div class="l">Open items</div></div>
  <div class="stat warn"><div class="n">3</div><div class="l">Hard source conflicts</div><div class="h">Official pages disagreeing with official pages</div></div>
  <div class="stat"><div class="n">0</div><div class="l">Values guessed</div><div class="h">Everything unconfirmed is blank</div></div>
  <div class="stat ok"><div class="n">100%</div><div class="l">Asserted values sourced</div></div>
</div>

<div class="callout bad">
  <strong>The one that matters most</strong>
  <p class="small">The Chefman 8 Qt listing advertises a <strong>450 °F Hi-Fry</strong> mode and bake/dehydrate/frozen functions. The brand's page and owner's manual for <code>RJ38-SQSS-8T</code> — the model this site maps to that listing — document a <strong>200–400 °F</strong> range with four food-type presets. <strong>Read 2026-11-14:</strong> Chefman also sells <code>RJ38-8T-BLACK</code>, whose page states a <strong>450 °F Hi-Fry</strong> and exactly those four functions, in a matte-black finish. So this is most likely <em>two different units</em> rather than one stale page — which narrows the problem without settling which unit the ASIN ships. This site asserts neither, and the buying guide tells readers to read the manual that ships with the unit. {src_links(['S12', 'S13', 'S26', 'S16'])}</p>
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
        return 'Internal design target — no official source states it (<a href="flagged.html">F26</a>)'

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
<p class="lede">The brief asks for automation, scale, data-driven optimisation and Amazon policy compliance. Those four pull in different directions, and the design below resolves the tension in one place: <strong>automate everything except the claims</strong>. Machines move data, check links, compute and report. A human signs off on what gets asserted about a product.</p>

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
    # The number of re-verification rows the executive summary quotes. Derived from
    # every rendered register so it cannot drift as a targeted addendum is added.
    LEDGER_ROWS = (len(REVERIFICATION["tests"]) + (len(PASS9["rows"]) if PASS9 else 0)
                   + (len(PASS10["rows"]) if PASS10 else 0)
                   + (len(PASS10_U2["rows"]) if PASS10_U2 else 0))
    # How many pages the root build publishes. Counted from the directories this
    # generator writes to, so the number in the prose cannot drift away from the
    # number of pages actually shipped.
    _written = set()
    for _d in (ROOT, ROOT / "articles", ROOT / "products", ROOT / "categories", ROOT / "guides"):
        for _f in _d.glob("*.html"):
            _written.add(_f)
    PAGES_HTML = len(_written)
    # Economics are computed from the dataset, never transcribed by hand: the price comes from
    # each product's brand-page list price and the rates come from the published Table 1 held
    # in data/compliance.json, so this table cannot drift away from the sources it cites.
    def _price(p):
        m = re.search(r"\$\s*([\d,]+\.\d{2})", p["pricing"]["brand_list_price"]["v"])
        return float(m.group(1).replace(",", "")) if m else None

    def _rate(*needles):
        for row in COMPLIANCE["commission_table"]:
            if all(n.lower() in row["category"].lower() for n in needles):
                return float(row["rate"].rstrip("%")), row["category"]
        return None, None

    rate_sets = [(r, c, lbl) for (r, c), lbl in
                 zip([_rate("kitchen"), _rate("home", "furniture"), _rate("all other categories")],
                     ["Kitchen", "Home", "fallback"])]
    econ_rows = []
    for p in PRODUCT_LIST:
        price = _price(p)
        cells = "".join(
            f'<td class="num">{("$%.2f" % (price * r / 100)) if (price and r) else "—"}</td>'
            for r, _c, _lbl in rate_sets
        )
        econ_rows.append(
            f'<tr><td><a href="products/{p["slug"]}.html">{e(p["short_name"])}</a></td>'
            f'<td class="num">{e(p["pricing"]["brand_list_price"]["v"])} {src_links(p["pricing"]["brand_list_price"]["s"])}</td>'
            f'{cells}</tr>'
        )
    econ_rows = "".join(econ_rows)
    rate_headers = "".join(f"<th>At {lbl} {r:.2f}%</th>" for r, _c, lbl in rate_sets)

    facts = [
        ("Product set", "Three supplied short links were followed; each fetch observed a landing on an air-fryer listing (candidate ASINs B0CDY277D3, B09B7SB46R, B08DKYBTPH). Token-to-ASIN mapping is not confirmed — see F14–F16 and the link checks on the <a href=\"reverification.html\">Re-verification</a> page.", ["S16", "S17"]),
        ("Category", "All three are air fryers or air fryer toaster ovens — the niche is set by the products, not chosen.", ["S16"]),
        ("Verification standard", "Official sources only; blank plus flagged wherever unconfirmed; no inference.", ["S1", "S2"]),
        ("Verified spec values", "Published on the dashboard and in the full dataset, each with a source link.", ["S10", "S12", "S14"]),
        (f"Re-verification ({REVERIFICATION['pass_date']}, 2026-11-15 and 2026-11-16)", f"Every published value was re-read against the official source it cites. The ledger — {LEDGER_ROWS} rows in total, each with the value as published, what the source said on the day, a verdict and a link — is on the <a href=\"reverification.html\">Re-verification</a> page. Two blank rows were filled from the manufacturer's own spec block, and the disputed question of whether the short links shuffle between requests was closed by a repeat fetch plus a nonsense-token control.", ["S16", "S21", "S22"]),
        ("Re-verification (2026-11-15, pass 9)", "Every official source was re-fetched by that session rather than trusted from the recorded ones: the Program Policies, the Commission Income Statement, both Chefman product pages, the Emeril product page, all three owner's manuals, all three supplied short links, 16 CFR Part 255 and 16 CFR Part 465. All 43 specification rows were checked against the page each one cites; none was found wrong and no published value changed. The raw evidence, including the sources deliberately not fetched, is in the repository.", ["S2", "S3", "S10", "S12", "S14", "S18"]),
        ("Re-verification (2026-11-16, pass 10)", "A tenth independent re-read fetched the load-bearing sources live and found three things. The Application Review criteria had been carried forward since 2026-11-13 and are now read from the source (which closes F56 and moves Q-19 from missing to answered). The two clauses that govern an AI-agent affiliate platform \u2014 IP License \u00a74 and Participation Requirements \u00a75 \u2014 were in neither the compliance register nor the platform blueprint, and are now C17, C18 and guardrail G11. And three pages pointed at a flag number that exists in no register, which is fixed and now fails the build. Two volatile review counters had moved again and were refreshed. No published value was found wrong.", ["S2", "S3", "S4", "S10", "S12", "S14"]),
        ("Hard source conflicts", "One serious and still live (Chefman 8 Qt 450 °F claim vs its own manual), plus SKU ambiguity. The Emeril preset count was narrowed on 2026-11-15: the owner's manual lists 24 presets by name in two separate tables and the Amazon listing title says 24, while the brand page's specification block still says 25 - the site states 24 and flags the 25.", ["S12", "S13", "S14"]),
        ("Commission rate", "Still blank per product, but on firmer ground. Amazon publishes rates by category and not by ASIN. All three listings were re-read on 2026-11-15 and all three render the browse-node path Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers, so Kitchen at 4.50% is the well-evidenced working rate. The settlement-time category still has to come from the Associates Earnings report, so both candidate rows are shown.", ["S3", "S16", "S28", "S29"]),
        ("Amazon price / rating", "Not displayed anywhere, by policy, not by omission.", ["S2"]),
        ("Disclosure", "Required statement on every page plus a link-level badge on every outbound link.", ["S1", "S5"]),
        ("Biggest constraint", "Program Content may not be aggregated, analysed or trained on — which rules out the obvious version of an AI research engine.", ["S2"]),
        ("API status (re-verified 2026-11-14)", "PA-API 5 is officially deprecated; Amazon's docs direct integrations to migrate to the Creators API. The automation blueprint must target the Creators API.", ["S24"]),
("Editorial defect found and fixed", "Eleven article sentences spliced a published display label into a mid-sentence position, so the prose read as machine output — 'splits a cavity into Two 3-quart baskets'. Every value was genuinely published and correct in a table, which is why nine earlier verification passes missed it. Fixed, and the build now fails if it recurs. This is the clearest evidence on the site that reading the page as a reader, not as a database, is a separate job from verifying it.", ["S1"]),
        ("Next decision", "Resolve the remaining flagged items, then publish, then apply. The decision queue is on the Suggestions page; the information gaps are on the Questions page.", ["S4"]),
    ]
    rows = "".join(
        f'<tr><td><strong>{e(k)}</strong></td><td>{e(v)}</td><td>{src_links(s)}</td></tr>' for k, v, s in facts
    )
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Executive summary</p>
<h1>Executive summary</h1>
<p class="lede">A one-page briefing for someone who will not read the rest. The short version: the product data is good, the economics are provable only within narrow limits, and the compliance constraint is the design constraint.</p>
<div class="grid grid-3" style="margin:1rem 0">
  <a class="card tight" href="picks.html"><span class="kicker">Buyer-facing</span><strong>This week's picks</strong><br><span class="tiny muted">Decision rule, not a ranking</span></a>
  <a class="card tight" href="decisions.html"><span class="kicker">Strategy</span><strong>Niche, traffic, measurement</strong><br><span class="tiny muted">Scored options and a kill rule</span></a>
  <a class="card tight" href="handover.html"><span class="kicker">Action</span><strong>Handover: five actions</strong><br><span class="tiny muted">About an hour of owner time</span></a>
</div>

<div class="callout note">
  <strong>Pass 9 — 2026-11-15 (verification, session 42ca97ad).</strong>
  <p class="small">This pass re-fetched every official source itself instead of trusting the recorded ones,
  and checked all 43 specification rows against the page each one cites. Nothing was found wrong and no
  published value changed. Four things did change. First, the Amazon browse-node path
  <em>Home &amp; Kitchen &gt; Kitchen &amp; Dining &gt; Small Appliances &gt; Fryers &gt; Air Fryers</em> was read
  directly on all three listings, where an earlier pass had read it on one; the commission evidence is now
  three-for-three (<a href="flagged.html">F50</a>). Second, eleven article sentences were found to splice a
  published label into mid-sentence position, so the prose read as machine output; they are fixed and the build
  now fails if it recurs (<a href="flagged.html">F51</a>). Third, the questions register gained four rows that
  are <em>known and sourced</em> and therefore carry an explicit answer, and four new suggestions were added.
  Fourth, the Application Review Process page was <em>not</em> re-read this pass and is flagged as
  carried-forward rather than confirmed (<a href="flagged.html">F52</a>). Raw evidence:
  <code>session-42ca97ad/EVIDENCE-2026-11-15.md</code>.</p>
</div>

<div class="callout note">
  <strong>Pass 8 — 2026-11-15.</strong>
  <p class="small">This pass re-fetched the three supplied links, the Standard Commission Income
  Statement, the Program Policies page, 16 CFR 255.5, 16 CFR Part 465 and both manufacturers' pages.
  Three defects were found by re-reading and are fixed: a stale listing title (<a href="flagged.html">F38</a>),
  a source record cited for a value it does not support (F39), and two rows published under the same
  flag number (F40). Two new registers were added: a <a href="suggestions.html">decision queue</a> of
  16 evidence-backed improvements with alternative paths, and a register of
  <a href="questions.html">14 open questions</a> separating what is known, what is discoverable, what
  the official source does not state, and what can only be answered from inside the account.
  Nothing on either register has been implemented. The full briefing, including the fetches that
  did <em>not</em> return content, is in <code>EXECUTIVE-SUMMARY-PASS8.md</code> in the repository.</p>
</div>

<div class="callout note">
  <strong>Pass 9 — 2026-11-15 (final integration).</strong>
  <p class="small">A final-integration pass re-read the load-bearing facts against the live official
  sources and fixed what it found. <strong>One new conflict was recorded rather than resolved</strong>:
  the Emeril brand page says "Included are 7 premium accessories" and the owner's manual enumerates
  seven removable accessories, while the supplied Amazon listing title says "Six Cooking Accessories
  Included" (<a href="flagged.html">F48</a> and <a href="flagged.html">F50</a>). The Emeril preset
  count was re-confirmed as 24 by reading the manual's two preset tables row by row, and the flag
  wording was tightened from "names exactly 24" to "lists 24 presets by name" because the manual
  never states the numeral. <strong>Ten defects in the site build itself were found and fixed</strong>,
  among them two decision pages that had each other's canonical URL and title, a page that stated
  16 suggestions while rendering 12, a buyer-facing link to a raw markdown file, and the complete
  absence of canonical URLs, social cards and structured data on every page. The site now ships a
  canonical URL, Open Graph and Twitter card tags and JSON-LD on all {PAGES_HTML} root pages, and
  two new build guards fail the build on a nested anchor. The full evidence, including what this
  pass could <em>not</em> establish, is in
  <code>session-88bb2db6/EVIDENCE-2026-11-15.md</code> in the repository.</p>
</div>

<div class="callout note">
  <strong>Pass 10 \u2014 2026-11-16 (verification, session 9fccce0c).</strong>
  <p class="small">The tenth independent re-read of the same register, run because the register is made of
  values that move. <strong>It found the clause the brief most needed and the register had never carried</strong>:
  Amazon's Program Policies contain <strong>IP License \u00a74, the Agent Terms</strong>, and
  <strong>Participation Requirements \u00a75</strong>, both written for exactly the case this project is
  \u2014 an AI-powered affiliate platform that automates product research. They are now compliance requirements
  <a href="compliance.html">C17 and C18</a> and platform guardrail G11, quoted verbatim. What they leave open is
  published rather than guessed: whether an ordinary public listing page counts as Program Content, and what the
  agent must call itself (<a href="questions.html">Q-21</a>, <a href="suggestions.html">SG-22</a>). It also found
  that three published pages pointed readers at a flag number which exists in no register in this repository; that
  is fixed and a new build guard now fails the build if any page cites an id that does not exist. The
  Application Review criteria had been carried forward rather than read since 2026-11-13 and are now confirmed
  verbatim from the live page, which closes <a href="flagged.html">F56</a> and gives
  <a href="questions.html">Q-19</a> its answer. The full evidence is in
  <code>reports/verification-2026-11-16-9fccce0c.md</code> in the repository, and on the
  <a href="reverification.html">Re-verification</a> page.</p>
</div>


<div class="grid grid-4" style="margin-bottom:1rem">
  <div class="stat bad"><div class="n">0</div><div class="l">Verified product identities</div><div class="h">3 candidate ASINs, mapping unconfirmed (F14–F16)</div></div>
  <div class="stat ok"><div class="n">{len(SOURCES["sources"])}</div><div class="l">Sources</div><div class="h">All official, all linked</div></div>
  <div class="stat warn"><div class="n">{len(PROGRAMME_FLAGS) + sum(1 for p in PRODUCT_LIST for f in p["flags"] if f["id"] not in ("F1", "F6"))}</div><div class="l">Open flag rows</div><div class="h">Counted the way the Flagged page lists them — none hidden, none blocking</div></div>
  <div class="stat"><div class="n">0</div><div class="l">Numbers invented</div></div>
</div>

<div class="tablewrap">
<table>
  <caption>What was done, what was found, what it means</caption>
  <thead><tr><th style="width:20%">Item</th><th style="width:64%">Finding</th><th style="width:16%">Source</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
</div>

<h2>Findings</h2>
<div class="callout ok">
  <strong>1 · The product side is verifiable, and was verified</strong>
  <p class="small">Every specification asserted on the site was read from the manufacturer's own product page or owner's manual on {e(ACCESSED)}, and each one carries a clickable link to it. {len(SOURCES["sources"])} sources are registered; none is a retailer, a review aggregator or an affiliate blog. Values that could not be confirmed are blank and listed, which is the only honest way to publish a comparison table.</p>
</div>
<div class="callout bad">
  <strong>2 · One official source contradicts another, and it is not cosmetic</strong>
  <p class="small">The Chefman 8 Qt listing advertises a 450 °F Hi-Fry mode; the brand page and the RJ38-SQSS-8T manual document 200–400 °F. A buyer relying on the listing could receive a unit that does not match it. The site states both claims, asserts neither, and tells the reader to check the manual. Resolving this needs someone to open the live listing.</p>
</div>
<div class="callout">
  <strong>3 · The commission numbers cannot be stated per product, and pretending otherwise would be fabrication</strong>
  <p class="small">Amazon's published rate table lists Kitchen at 4.50%, Home at 3.00% and a 4.00% fallback {src_links(['S3'])}. Amazon does not publish which category a given ASIN sits in, and air fryers are not named in the table. Every "commission rate" figure on a competitor site therefore rests on a guess. What this site adds is evidence rather than a guess: on 2026-11-15 all three listings were re-read and all three render the Kitchen &amp; Dining browse-node path, which makes 4.50% the well-evidenced working rate. The settlement-time category still comes only from the Earnings report, so both candidate rows stay on the page and the rate stays blank per product.</p>
</div>
<div class="callout info">
  <strong>4 · The policy constraint is the architecture</strong>
  <p class="small">The brief asks for automated product research, trend detection and optimisation. The IP License forbids aggregating, analysing, extracting or repurposing Program Content and forbids training models on it {src_links(['S2'])}. So the automated research layer must run on manufacturer documentation and the operator's own click and conversion data. That is a harder, slower build — and the only one that survives review.</p>
</div>
<div class="callout">
  <strong>5 · Verifying the data and reading the page are different jobs, and only one of them was automated</strong>
  <p class="small">Nine earlier passes checked every value against its source and found nothing wrong — correctly.
  But a value that is right in a table can still be wrong in a sentence, and eleven of them were: a published
  display label such as "Two 3-quart baskets" had been spliced into mid-sentence position, so the articles read
  as machine output ("splits a cavity into Two 3-quart baskets"). No verifier catches that, because the value is
  genuinely published. It took reading the rendered pages as a shopper would. The defect is fixed and the build
  now fails if a capitalised value is spliced into a mid-sentence position again {src_links(['S1'])}.</p>
</div>

<h2>Economics, stated with the precision the data allows</h2>
<div class="tablewrap">
<table>
  <caption>Illustrative commissions at published rates — arithmetic on the brand list price, not a forecast</caption>
  <thead><tr><th>Product</th><th>Brand list price</th>{rate_headers}</tr></thead>
  <tbody>{econ_rows}</tbody>
</table>
</div>
<p class="tiny muted">Brand list prices from {src_link('S10')}, {src_link('S12')} and {src_link('S14')}; rates from {src_link('S3')}. Amazon computes commission on Qualifying Revenue after shipping, tax, returns and bad debt, so real payouts are lower. The Amazon selling price — the number that would actually drive commission — is unknown to this project by policy.</p>

<h2>Coverage against the brief</h2>
<div class="callout note">
  <strong>Every requirement in the brief, and what is actually done about it</strong>
  <p class="small" style="margin-bottom:0">{_req_counts_html()} The <a href="requirements.html">Requirements and
  status</a> page lists all {len(REQUIREMENTS['requirements'])} rows individually, each with the path that
  implements it and the official source that settles it. A row is marked <em>blocked</em> only where the input
  exists solely inside Amazon's own systems — the Associate tag, the account's approval status, per-ASIN
  commission categories, customer reviews, conversion reports — and never to mean "not done yet".</p>
</div>

<h2>Recommendation</h2>
<ol class="tight small">
  <li><strong>Publish this build.</strong> It satisfies the content substance a review looks for, and it is honest under inspection.</li>
  <li><strong>Clear the flags that change copy first</strong> — F3 (the 450 °F conflict), F4/F5 (preset counts), F1/F2 (model mapping). Those decide what the pages may assert.</li>
  <li><strong>Fix attribution before driving traffic</strong> — confirm the Associates tag and create sub-tags; F6 and F7.</li>
  <li><strong>Then apply, and work the 180-day window deliberately</strong> {src_links(['S4'])}.</li>
  <li><strong>Only pursue price and rating display if API access is granted.</strong> Until then, absence is the compliant state.</li>
  <li><strong>Decide what the AI agent is allowed to read before writing the research pipeline.</strong> The IP License forbids using Amazon's Program Content to build or improve models, and forbids aggregating or analysing it without written approval {src_links(['S2'])}. The version of the brief that is lawful runs on manufacturers' own pages — which is the version this repository already implements. See <a href="suggestions.html#sg-18">SG-18</a>.</li>
  <li><strong>Decide the product set before the next content push.</strong> Two of the three products share a brand and a form factor, which caps what the comparison can answer. See <a href="suggestions.html#sg-20">SG-20</a>.</li>
</ol>

<p class="small" style="margin-top:1.5rem"><a class="btn btn-ghost" href="requirements.html">Requirement-by-requirement status</a> <a class="btn btn-ghost" href="flagged.html">See every open flag</a></p>
<p class="tiny muted">The Markdown briefings this page used to link are undated records from earlier passes; five of
them sit at the repository root and at least one contradicts the position published here. They are not endorsed by
this page. See <a href="flagged.html#f59">F59</a>.</p>
"""
    return layout("executive-summary.html", "Executive summary", body, active="executive-summary.html",
                  description="One-page executive summary: findings, source conflicts, economics and the recommended next decision.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Executive summary", page_url("executive-summary.html")),
    ])]
              )


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
            f'<div class="tiny">{repo_link(path, "Source: " + path)}</div></td>'
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
<p class="small">Merging them would mean picking a winner for each disagreement on evidence that does not exist yet. For the model number, only the account holder can settle it by reading the model plate on a unit or the listing's product-information block. For the policy labels, the live page settles it and the canonical build already matches the live page — but rewriting another session's published pages to match would destroy the record of what that pass actually verified against.</p>

<h2>What "canonical" means here, precisely</h2>
<div class="tablewrap">
<table>
  <caption>How each build is gated</caption>
  <thead><tr><th>Build</th><th>Generator</th><th>Gate that runs on every push</th></tr></thead>
  <tbody>
    <tr><td>Root site (canonical)</td><td><code>build.py</code>{repo_link('build.py', '')}</td><td><code>verify.py</code> — no broken internal links, no specification row with a value but no official source, the required disclosure on every page, and no article number that is not in the verified dataset. {repo_link('verify.py', 'verify.py on GitHub')}</td></tr>
    <tr><td><code>site/</code></td><td><code>scripts/build_site.py</code>{repo_link('scripts/build_site.py', '')}</td><td><code>scripts/verify_site.py</code> — 382 assertions over <code>data/verified/</code>. {repo_link('scripts/verify_site.py', 'verify_site.py on GitHub')}</td></tr>
    <tr><td><code>s2/</code></td><td><code>scripts/build_s2_site.py</code>{repo_link('scripts/build_s2_site.py', '')}</td><td><code>--check</code> byte-comparison against a fresh rebuild. {repo_link('scripts/build_s2_site.py', 'build_s2_site.py on GitHub')}</td></tr>
    <tr><td>Others</td><td>their own scripts</td><td>No CI gate. They are preserved evidence, not a maintained product. {repo_link('.github/workflows/', 'The only workflows that run')}</td></tr>
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
<h1>Design prompt pack: review before anything changes</h1>
<p class="lede">The design and content-production suggestion layer: a paste-ready design prompt, ten design suggestions with live status, the article topic queue, organic-traffic tactics, editorial voice rules and a decision register. Every row is a suggestion for you to approve, reject or modify — the status column records which of them the repository already satisfies today.</p>

<div class="callout info">
  <strong>How this page fits the other registers.</strong>
  <p class="small"><a href="suggestions.html">Suggestions</a> is the governance queue (SG-01…): what to decide and what it costs. <a href="questions.html">Questions</a> is what is not known yet (Q-01…). <a href="decisions.html">Decisions &amp; handover</a> settles strategy — which niche, which channels, what to measure. <a href="topics.html">Content and traffic plan</a> is the proposal view of the article queue — intent, angle and citations per topic. <strong>This page</strong> is the design and content-production layer: how the site should look and read, whether each proposed article has shipped yet, and the tactics that turn the strategy into published pages. Product facts are not here — they live in <a href="data.html">the full dataset</a>, each with its official source.</p>
</div>

<h2 id="the-prompt">The design prompt</h2>
<p class="small">Paste the block below into any designer or AI assistant used to restyle the site. It describes the site exactly as it is today, names the components and rules that must survive a redesign, and ends with the acceptance criteria every change has to pass. Nothing in it asks for a claim the site cannot source.</p>
<pre class="prompt-block">{e(d["design_prompt"])}</pre>
<p class="tiny muted">Compiled {e(d["compiled"])} by {e(d["session"])}. If a request built from this prompt contradicts the verification rules inside it — a filled blank cell, a price, a rating, a testing claim — the prompt is wrong and the rules win.</p>

<h2>Design suggestions</h2>
<p class="small muted">{e(d["how_to_read"])}</p>
<div class="tablewrap">
<table>
  <caption>Design suggestions D-1…D-10 with the status of each in the repository today</caption>
  <thead><tr><th>#</th><th>Suggestion · why · path</th><th>Status</th><th>Evidence</th></tr></thead>
  <tbody>{design_rows}</tbody>
</table>
</div>

<h2>Article topic queue</h2>
<p class="small">Catchy, reader-shaped topics for this product set, in the order they were proposed. Titles are working titles; each one names the format and the hook it leads with. Published rows link to the article they became. Nothing here may claim hands-on testing or state an Amazon price — those rules are inside the prompt above. <strong>Relationship to <a href="topics.html">topics.html</a>:</strong> that page is the proposal view (intent, serving product, citation each topic must carry); this table is the status view — which of the original working titles actually became articles, and which are still open.</p>
<div class="tablewrap">
<table>
  <caption>Topic queue A-1…A-11 — published versus not written</caption>
  <thead><tr><th>#</th><th>Working title · format · hook</th><th>Status</th><th>Sources it would cite</th></tr></thead>
  <tbody>{''.join(topic_rows)}</tbody>
</table>
</div>

<h2>Organic-traffic tactics</h2>
<p class="small">Channel strategy — which niche to build, which channels to run, what to measure — is decided on <a href="decisions.html">decisions.html</a>, with the per-topic promotion channels listed on <a href="topics.html">topics.html</a>. This table is the operational checklist behind them: what has already shipped, what is half-done and what has not started.</p>
<div class="tablewrap">
<table>
  <caption>Organic-traffic tactics T-1…T-8 with implementation status</caption>
  <thead><tr><th>#</th><th>Tactic · how · status note</th><th>Status</th><th>Evidence</th></tr></thead>
  <tbody>{tactic_rows}</tbody>
</table>
</div>

<h2>Editorial voice rules</h2>
<p class="small">The voice half of the anti-slop rules. The enforcement half — the banned openers, the arithmetic guard, the claim checks — lives on <a href="decisions.html">decisions.html</a> and in <code>build.py</code>, where the build fails if a rule is broken.</p>
<div class="tablewrap">
<table>
  <caption>Voice rules V-1…V-4</caption>
  <thead><tr><th>#</th><th>Rule</th><th>Why</th><th>Evidence</th></tr></thead>
  <tbody>{voice_rows}</tbody>
</table>
</div>

<h2>Decision register</h2>
<p class="small">How to use this register: for each row choose <strong>Approved</strong>, <strong>Rejected</strong> or <strong>Needs more info</strong>, write the choice and the date in the last column, then implement only approved rows. Rejected rows stay on the register so they are not proposed again. Rows that are blocked name the question that unblocks them.</p>
<div class="tablewrap">
<table>
  <caption>Decision register R-1…R-6 — the choice column is deliberately empty</caption>
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
                  description="Design, content and traffic suggestions for this site: a paste-ready design prompt, ten design suggestions with live status, the article topic queue, organic-traffic tactics, voice rules and a decision register to review before anything changes.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Design prompt pack", page_url("design-prompt.html")),
    ])])


def page_suggestions():
    s = SUGGESTIONS
    items = sorted(s["suggestions"], key=lambda x: -(x["impact"] * x["confidence"]))

    def card(sg):
        score = sg["impact"] * sg["confidence"]
        opts = "".join(
            f'<li><strong>{e(o["label"])}</strong>'
            f'<div class="tiny" style="margin:.15rem 0 .35rem">Effort {e(o["effort"])} · risk {e(o["risk"])}'
            f'{" · reversible" if o.get("reversible") else ""}</div>'
            f'<div class="small">{e(o["what"])}</div></li>'
            for o in sg["options"]
        )
        ev = " ".join(
            f'<a class="src-link" href="{e(x["url"])}" target="_blank" rel="noopener">{e(x["label"])} ↗</a>'
            for x in sg["evidence"]
        )
        blocked = sg.get("blocked_by") or []
        blocked_html = (
            " ".join(f'<a href="questions.html#{e(q.lower())}" class="src">{e(q)}</a>' for q in blocked)
            if blocked else '<span class="tiny muted">Nothing blocks this.</span>'
        )
        return f"""
<article class="sug" id="{e(sg['id'].lower())}">
  <div class="sug-head">
    <div>
      <div class="tiny muted">{e(sg['id'])} · {e(sg['area'])}</div>
      <h3>{e(sg['title'])}</h3>
    </div>
    <div class="score" title="impact {sg['impact']} x confidence {sg['confidence']} - this pass's judgement, not a measurement">
      <strong>{score}</strong><span>priority</span>
    </div>
  </div>
  <p><strong>The problem.</strong> {e(sg['problem'])}</p>
  <div class="evidence"><strong>Evidence.</strong> {ev}</div>
  <p class="label">Paths you could take</p>
  <ol class="paths">{opts}</ol>
  <p class="rec"><strong>This pass would pick:</strong> {e(sg['recommendation'])}</p>
  <p class="small"><strong>Why.</strong> {e(sg['why'])}</p>
  <p class="small"><strong>Cost of not doing it.</strong> {e(sg['risk_of_not_doing'])}</p>
  <p class="small"><strong>Blocked by:</strong> {blocked_html}</p>
</article>"""

    cards = "".join(card(x) for x in items)

    # ---- Choose a path (added 2026-11-15, arena/63a2c638) -------------------------- #
    # A long decision queue is a backlog, not a decision. The paths group the rows into
    # ordered pieces of work with an explicit entry condition, so the owner can pick one
    # and finish it. Built from data/suggestions.json -> "paths"; a path's member ids are
    # validated against the suggestion register so a stale id fails the build rather than
    # silently dropping a row.
    known_sg = {x["id"]: x for x in s["suggestions"]}
    path_rows = []
    path_articles = []
    for path in (s.get("paths") or []):
        unknown = [m for m in path["contains"] if m not in known_sg]
        if unknown:
            raise SystemExit(
                "BUILD FAILED — path %s references unknown suggestion(s): %s"
                % (path["id"], ", ".join(unknown)))
        # Evidence links for the row-source gate: the official sources behind the members.
        seen_urls = []
        for m in path["contains"]:
            for ev in known_sg[m]["evidence"]:
                if ev["url"] not in seen_urls:
                    seen_urls.append(ev["url"])
        ev_links = " ".join(
            f'<a href="{e(u)}" target="_blank" rel="noopener">{e(u.split("//")[-1][:34])} ↗</a>'
            for u in seen_urls[:4]
        )
        # Flagged page is always a valid target, and every path links to it for its caveats.
        ev_links += ' <a href="flagged.html">Flagged ↗</a>'
        chips = " ".join(
            f'<a class="src" href="#{e(m.lower())}">{e(m)}</a>' for m in path["contains"]
        )
        path_rows.append(
            f'<tr><td class="num"><a href="#{e(path["id"].lower())}">{e(path["id"])}</a></td>'
            f'<td><strong>{e(path["name"])}</strong><div class="small muted">{e(path["promise"])}</div></td>'
            f'<td class="small">{chips}</td>'
            f'<td class="small">{e(path["effort"])}</td>'
            f'<td class="small">{ev_links}</td></tr>'
        )
        path_articles.append(f"""
<article class="sug" id="{e(path['id'].lower())}">
  <div class="sug-head">
    <div>
      <div class="tiny muted">{e(path['id'])} · a path through the queue</div>
      <h3>{e(path['name'])}</h3>
    </div>
  </div>
  <p>{e(path['promise'])}</p>
  <p class="small"><strong>Contains.</strong> {chips}</p>
  <p class="small"><strong>Effort.</strong> {e(path['effort'])}</p>
  <p class="small"><strong>Must be true first.</strong> {e(path['must_be_true_first'])}</p>
  <p class="small"><strong>What you get.</strong> {e(path['delivers'])}</p>
  <p class="small"><strong>What it does not fix.</strong> {e(path['does_not_fix'])}</p>
  <p class="small"><strong>Why it sits here in the order.</strong> {e(path['why_first'])}</p>
  <p class="rec"><strong>Pick this if.</strong> {e(path['pick_this_if'])}</p>
</article>""")

    paths_html = ""
    if path_rows:
        paths_html = f"""
<h2>Choose a path before you choose a suggestion</h2>
<p class="lede">{e(s.get('paths_intro',''))}</p>
<div class="tablewrap"><table>
  <thead><tr><th>#</th><th>Path</th><th>Suggestions it contains</th><th>Effort</th><th>Evidence behind its rows</th></tr></thead>
  <tbody>{''.join(path_rows)}</tbody>
</table></div>
<p class="tiny muted">{e(s.get('paths_note',''))}</p>
{''.join(path_articles)}
"""

    # summary table - every row links to its own evidence so the row-source gate is satisfied
    rows = []
    for x in items:
        ev_links = " ".join(
            f'<a href="{e(y["url"])}" target="_blank" rel="noopener">{e(y["label"].split(" - ")[0][:38])} ↗</a>'
            for y in x["evidence"]
        )
        # The choice set, at a glance, so a reviewer can decide from this table alone
        # and record it. The row already carries its evidence links, which is what the
        # row-source gate requires of every table row on the site.
        choice = " ".join(
            f'<span class="tiny muted">{e(o["label"].split(".")[0])}</span>'
            for o in x["options"]
        )
        rows.append(
            f'<tr><td class="num"><a href="#{e(x["id"].lower())}">{e(x["id"])}</a></td>'
            f'<td>{e(x["title"])}</td><td class="small">{e(x["area"])}</td>'
            f'<td class="num">{x["impact"]*x["confidence"]}</td>'
            f'<td class="small">{_effort_chip(x["effort"])} {e(x["risk_of_not_doing"].split(".")[0])}</td>'
            f'<td class="small">{choice}</td>'
            f'<td class="small">{ev_links}</td></tr>'
        )

    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Suggestions</p>
<h1>Suggestions, and a place to choose between them</h1>
<p class="lede">{len(items)} reviewed, evidence-backed suggestions, in priority order. Each one would materially change something on this site.
Nothing on this page has been implemented. Each entry names the problem it fixes, the official
document or repository evidence behind it, two or three paths you could take, and the path this
pass would pick if it were your call. Read the one you care about, choose a path, and the work is
a short story rather than an open-ended project.</p>

<div class="callout note">
  <strong>How to use this page.</strong> {e(s["how_to_read"][0])}
  The score is <em>{e(s["scoring_note"])}</em>
  Suggestions blocked by something only you can supply link to the exact row on the
  <a href="questions.html">Open questions</a> page.
</div>

{paths_html}
<h2>At a glance</h2>
<p class="small muted">Read the table, then take one row and read the full entry for it. The <em>Your call</em> column lists the paths that are on the table for that suggestion &mdash; write the letter you choose next to it, with the date. Nothing on this page has been implemented, and implementing anything starts by choosing a path here.</p>
<div class="tablewrap"><table>
  <thead><tr><th>#</th><th>Suggestion</th><th>Area</th><th>Priority</th><th>Effort · cost of waiting</th><th>Your call</th><th>Evidence</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table></div>
<p class="tiny muted">Priority is impact x confidence, both scored by this pass out of 5. It is judgement. The evidence column is the fact.</p>

<h2>The queue</h2>
{cards}

<div class="callout note" style="margin-top:1.5rem">
  <strong>Related registers.</strong>
  A second, independently written set of questions and directions was produced by a parallel
  session on the same day and is published rather than merged away, because it asks things this
  register does not — including which Amazon marketplace a Japan-based Associate may promote.
  <a href="decision-gate.html">Questions and information gaps (parallel pass)</a> ·
  <a href="marketing-directions.html">Marketing directions (parallel pass)</a> ·
  <a href="questions.html">This pass's open questions</a> ·
  <a href="design-prompt.html">Design prompt pack — design, topics and tactics</a>
</div>
"""
    return layout("suggestions.html", "Suggestions", body, active="suggestions.html",
                  description="Reviewed, evidence-backed suggestions for the site, each with alternative paths and a recommendation, for the owner to choose before anything is implemented.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Suggestions", page_url("suggestions.html")),
    ])]
              )

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
        extra = (" " + " ".join(f'<a href="{e(y["url"])}" target="_blank" rel="noopener">repo ↗</a>'
                                for y in item["sources"][1:] if "github.com" in y["url"]))
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
  <span class="pill ok">Known and sourced</span> verified this pass against an official page, link on the row.
  <span class="pill warn">Missing - discoverable</span> not established here, but a browser and ten minutes would settle it.
  <span class="pill bad">Needs account access</span> outside the account it cannot be known at all.
  <span class="pill warn">The source does not state it</span> we read the official page and the fact is not on it.
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
     "The owner's manual matches the listing wording (dual baskets, easy-view windows, Hi-Fry, Sync Finish). Amazon does not publish the model number on the product page.",
     "A model number printed on the product, or on the listing's product-information block, is not confirmed.",
     "Read the model plate on a unit, or the 'Product information' block on the listing page. Record what you find with the source.",
     "Product page spec rows", ["S10", "S16"]),
    ("Q-08", "Which model is sold under ASIN B09B7SB46R (Emeril Lagasse 26QT)?",
     "The owner's manual FAFO-001 and the brand product page describe the Emeril 26QT French Door air fryer.",
     "The model number printed on the Amazon listing is not confirmed.",
     "Read the 'Product information' block on the listing page and compare it with the manual's model number.",
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


def page_suggestions_alt():
    rows = []
    for sid, area, text, basis, basis_src, options, effort in SUGGESTIONS_ALT:
        basis_html = (src_links(basis_src) + " " if basis_src else "") + (
            "" if basis_src else '<a href="flagged.html">Flagged for review</a> ')
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
          <td class="small">{e(known)}<div class="tiny">{src_links(srcs) if srcs else '<a href="flagged.html">Flagged for review</a>'}</div></td>
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
        cites = " ".join(
            f'<a href="{e(c["url"])}" target="_blank" rel="noopener">{e(c["label"][:40])} ↗</a>'
            for c in it["must_cite"][:2]
        )
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
  {caveat}
  <div class="evidence"><strong>Must cite.</strong> {cites}</div>
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
            f'{e(ch["source"]["label"])} ↗</a></td></tr>'
        )

    disclaimer = "".join(f"<li>{e(x)}</li>" for x in t["disclaimer"])
    n_new = sum(1 for x in items if x["status"] == "proposed")
    n_pub = sum(1 for x in items if x["status"] == "published")

    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Content and traffic plan</p>
<h1>What to write next, and how it is allowed to be promoted</h1>
<p class="lede">Fourteen topics for this product set — {n_pub} already published and {n_new} not yet
written — and five distribution channels, two of which Amazon's policies close off entirely. The
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


def check_requirement_paths(generated=()):
    """Build guard: every path a requirement row claims must exist in this repository.

    This guard exists because the defect it prevents was live. The s2 annex's own
    register row R-01 cited `data/requirements.json` and a "Requirements page"; neither
    existed at those locations, and no gate noticed because a register is prose. A
    status table that points at files which are not there is worse than no table: it
    reads as verification and is none. Failing the build makes the claim checkable.
    """
    generated = set(generated)

    def exists(rel):
        # A path is real if it is on disk, or if this same build is generating it.
        return rel in generated or (ROOT / rel).exists()

    problems = []
    for req in REQUIREMENTS["requirements"]:
        for path in req.get("where") or []:
            if path.endswith("/"):
                if not exists(path) and not (ROOT / path).is_dir():
                    problems.append(f"{req['id']}: directory does not exist: {path}")
            elif not exists(path):
                problems.append(f"{req['id']}: file does not exist: {path}")
        for ev in req.get("evidence") or []:
            url = ev["url"]
            if url.startswith("http") or url.startswith("#"):
                continue
            if not exists(url):
                problems.append(f"{req['id']}: evidence link does not exist: {url}")
        for sid in req.get("sources") or []:
            if sid not in SRC_BY_ID:
                problems.append(f"{req['id']}: cites unregistered source {sid}")
        if not (req.get("where") or req.get("evidence") or req.get("sources")) and not req.get("why"):
            problems.append(f"{req['id']}: no implementation path, no evidence and no stated gap")
    return problems


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
            f'{e(x["label"])} ↗</a>'
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
            f'<td class="small"><strong>{e(r["requirement"])}</strong>'
            f'<div class="tiny muted" style="margin-top:.35rem">{e(r["clause"])}</div></td>'
            f'<td><span class="pill {cls}">{e(label)}</span></td>'
            f'<td class="small">{e(r["why"])}</td>'
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
  yet. There are {counts.get('not_delivered',0)} of them, and the largest is organic traffic — see
  <a href="topics.html">the content and traffic plan</a> for the channels Amazon's policies leave open.</p>
</div>

{''.join(sections)}

<h2>What this register does not claim</h2>
<p class="small">A status here is a statement about this repository, not about the affiliate business.
This site has three products, one category, no traffic and no confirmed affiliate tag, so no row on this
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
  <div class="card"><h2 style="margin-top:0;font-size:1.02rem">Products</h2>
    <ul class="tight small">
      <li><a href="products/chefman-6qt-dual-basket.html">Chefman 6 Qt Dual Basket</a></li>
      <li><a href="products/emeril-26qt-french-door.html">Emeril 26 QT French Door</a></li>
      <li><a href="products/chefman-8qt-turbofry.html">Chefman 8 Qt TurboFry</a></li>
      <li><a href="compare.html">Comparison matrix</a></li>
    </ul>
  </div>
  <div class="card"><h2 style="margin-top:0;font-size:1.02rem">Research</h2>
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
        for sec in a["sections"]:
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
        if DISCLOSURE not in text.split("</header>")[0]:
            problems.append(f"{rel}: the Associates sentence is not in the page header")
        low = text.lower()
        if "tested" not in low and "hands-on" not in low:
            problems.append(f"{rel}: no statement that nothing was tested")
        for bad in ("out of 5 stars", "a-icon-alt", "Amazon price:"):
            if bad in text:
                problems.append(f"{rel}: prohibited Amazon price/rating pattern {bad!r}")
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
    for sec in article["sections"]:
        parts.append(f"<h2>{e(sec['h'])}</h2>")
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


def page_articles_index():
    cards = []
    for a in ARTICLES["articles"]:
        prods = ""
        if a["products"]:
            links = []
            for slug in a["products"]:
                p = next((x for x in PRODUCT_LIST if x["slug"] == slug), None)
                if p:
                    links.append(f'<a href="../products/{slug}.html">{e(p["short_name"])}</a>')
            if links:
                prods = ('<p class="tiny muted" style="margin:.4rem 0 0">About: '
                         + " · ".join(links) + "</p>")
        # An article that serves no single product (site-level pieces) leaves prods
        # empty; emitting the slot anyway would publish a trailing-whitespace line.
        prods_html = (prods + "\n") if prods else ""
        cards.append(f"""<article class="card article-card">
  <span class="kicker">{e(a['kicker'])}</span>
  <a class="cardtitle" href="../articles/{a['slug']}.html">{e(a['title'])}</a>
  <span class="cardtext">{e(a['standfirst'])}</span>
  <span class="tiny muted">{e(a['kind'])} · {a['reading_minutes']} min read</span>
{prods_html}</article>""")
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Articles</p>
<h1>Articles</h1>
<p class="lede">{_n_words(len(ARTICLES["articles"]))} written for this product set. Each one states what the manufacturer's own pages and manuals establish, links to the page it came from, and names the places where the official record contradicts itself rather than tidying them away.</p>

<div class="callout info">
  <strong>How to read these articles</strong>
  <p class="small">A <code class="specval">highlighted number</code> is a value published in this site's verified dataset and is a quotation from a manufacturer page or owner's manual. An ordinary number in prose is a date or a page reference. Anything marked <em>judgement</em> or written as a decision rule is the site's opinion, not a sourced fact. <strong>No product in this set was tested by anyone here</strong>, so no article claims a cooking result, a measured time or a hands-on comparison.</p>
</div>

<div class="cardgrid">
{chr(10).join(cards)}
</div>

<h2>What these articles deliberately do not contain</h2>
<div class="tablewrap">
<table>
  <caption>Editorial rules this section is built to</caption>
  <thead><tr><th>Rule</th><th>Why</th><th>Source</th></tr></thead>
  <tbody>
    <tr><td>No hands-on testing is claimed</td><td>A first-person testing claim that never happened is a deceptive endorsement, not a style choice.</td><td>{src_links(['S8', 'S2'])}</td></tr>
    <tr><td>No Amazon price, star rating or review count</td><td>Both may only be displayed when Amazon serves the link or the data comes from Creators/PA API.</td><td>{src_links(['S2'])}</td></tr>
    <tr><td>No superlative asserted as fact</td><td>"Best", "quietest" and "fastest" are measurements. None were taken.</td><td>{src_links(['S2'])}</td></tr>
    <tr><td>A conflict is published, not resolved</td><td>Picking a winner between two official sources without evidence would be a fabrication with a citation attached.</td><td>{src_links(['S14', 'S12'])}</td></tr>
    <tr><td>Disclosure on every page</td><td>Operating Agreement §5 and 16 CFR §255.5(a) both require it, in a place a reader will actually see.</td><td>{src_links(['S1', 'S9'])}</td></tr>
  </tbody>
</table>
</div>

<p class="small" style="margin-top:1.5rem"><a class="btn btn-ghost" href="../guides/buying-guide-air-fryers.html">Buying guide →</a> <a class="btn btn-ghost" href="../compare.html">Comparison matrix →</a> <a class="btn btn-ghost" href="../flagged.html">Flagged for review →</a></p>
"""
    aurl = page_url("articles/index.html")
    ld = [
        {
            "@type": "CollectionPage",
            "@id": aurl + "#webpage",
            "url": aurl,
            "name": "Articles",
            "isPartOf": {"@id": SITE_URL + "/#website"},
            "about": {"@id": SITE_URL + "/#organization"},
            "inLanguage": "en-US",
        },
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Articles", aurl),
        ]),
        {
            "@type": "ItemList",
            "@id": aurl + "#articles",
            "name": "Sourced air-fryer articles",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "name": art["title"],
                    "url": page_url(f"articles/{art['slug']}.html"),
                }
                for i, art in enumerate(ARTICLES["articles"], start=1)
            ],
        },
    ]
    return layout("articles/index.html", "Articles", body, active="articles/index.html",
                  description="Eight sourced articles on dual-basket vs oven air fryers, what a 450 F badge means, preset-count conflicts, capacity from published numbers, and why this site publishes no Amazon prices.",
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
    related = [x for x in ARTICLES["articles"] if x["slug"] != a["slug"]][:3]
    rel_html = "".join(
        f'<li><a href="../articles/{x["slug"]}.html">{e(x["title"])}</a> '
        f'<span class="tiny muted">— {e(x["kind"])}</span></li>' for x in related)
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / <a href="../articles/index.html">Articles</a> / {e(a['kind'])}</p>
<p class="kicker">{e(a['kicker'])}</p>
<h1>{e(a['title'])}</h1>
<p class="lede">{e(a['standfirst'])}</p>
<p class="tiny muted">{e(a['kind'])} · {a['reading_minutes']} min read · sources read {ARTICLES['accessed']} · no first-hand testing</p>

<div class="callout warn">
  <strong>No hands-on testing, and no Amazon numbers</strong>
  <p class="small">Nobody here cooked with these appliances. Every specification below is quoted from the manufacturer's own product page or owner's manual and links to it. No Amazon price, star rating or review count appears, because Amazon's Program Policies only permit those when Amazon serves the link or via Creators/PA API {src_links(['S2'])}.</p>
</div>

{prods}

{article_body(a)}

<p class="small" style="margin-top:1.5rem"><em>{e(a['closing_note'])}</em></p>

<h2>Read next</h2>
<ul class="tight small">{rel_html}</ul>

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
  <button type="button" class="copylink" data-link="{e(_url)}">Copy link</button>
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
    """Commercial front door: the honest version of a 'top picks' page."""
    d = DECISION
    cards = []
    jobs = [
        ("chefman-6qt-dual-basket", "Cook two different things at once",
         "Two independent 3-quart baskets and a Sync Finish function that delays the shorter cook to land with the longer one."),
        ("emeril-26qt-french-door", "Replace a toaster oven as well as a fryer",
         "One 26-quart cavity with French doors, a dual-speed fan and a rotisserie documented in the owner's manual."),
        ("chefman-8qt-turbofry", "Feed four to six people from one basket",
         "A single large basket with a documented 4\u20136 person household size and a shake reminder."),
    ]
    by_slug = {p["slug"]: p for p in PRODUCT_LIST}
    for slug, job, why in jobs:
        p = by_slug[slug]
        cap = next(s for s in p["specs"] if s["label"] in ("Capacity",))
        model = p.get("model_number") or {}
        cards.append(f"""
<article class="card pcard pick">
  <p class="product-type">Pick if you want to</p>
  <h3>{e(job)}</h3>
  <p class="small muted product-name">{e(p['short_name'])} \u2014 {e(p['name'])}</p>
  <div class="product-fact">
    <span>Manufacturer-stated capacity</span>
    <strong>{e(cap['value'])}</strong>
    <span class="tiny">{src_links(cap['source'])}</span>
  </div>
  <p class="small">{e(why)}</p>
  <p class="product-match"><span class="pill pill-warn">Model match unconfirmed</span>
    <a class="tiny" href="flagged.html">Why</a></p>
  <a class="pick-cta" href="products/{e(p['slug'])}.html">Read the sourced breakdown \u2192</a>
</article>""")

    rate_rows = "".join(
        f'<tr><td>{e(r["label"])}</td><td class="num">{e(r["rate"])}</td>'
        f'<td class="small">{e(r["row_quoted"])} {src_links(r["source"])}</td></tr>'
        for r in _decision_rows())

    examples = "".join(
        f'<tr><td>{e(x["product"])}</td><td class="num">{e(x["list_price"])}</td>'
        f'<td class="num">{e(x["at_4_5"])}</td><td class="num">{e(x["at_4_0"])}</td>'
        f'<td>{src_links(x["source"])}</td></tr>'
        for x in d["commission"]["per_sale_examples"])

    caveats = "".join(f"<li>{e(c)}</li>" for c in d["commission"]["caveats"])

    body = f"""
<div class="editorial-hero picks-hero">
  <div class="hero-copy">
    <p class="hero-eyebrow">This week's picks <span aria-hidden="true">/</span> updated {e(d['compiled'])}</p>
    <h1 class="hero-title">Three air fryers, three different jobs.</h1>
    <p class="lede">A picks page is usually a ranking. This one is a decision rule: each of the three products wins a different job, and the job you have decides the product. Every claim below is a manufacturer specification you can check in one click.</p>
    <div class="hero-actions">
      <a class="btn" href="#pick-rule">See the rule <span aria-hidden="true">\u2193</span></a>
      <a class="btn btn-ghost" href="decisions.html">How the money works <span aria-hidden="true">\u2192</span></a>
    </div>
    <p class="hero-footnote">No hands-on testing claimed \u00b7 no Amazon price or rating published \u00b7 model identity still open</p>
  </div>
  <aside class="hero-panel" aria-label="What this page is">
    <p class="hero-panel-kicker">Before you click <span>read this</span></p>
    <h2>The link is not the product.</h2>
    <p class="small">Each product below links to a supplied Amazon short link. All three land on a listing, but Amazon does not publish a model number a fetch can read, so this site cannot confirm which manufacturer SKU each listing is. Check the model number on the listing before you buy. <a href="flagged.html">Flagged for review</a>.</p>
  </aside>
</div>

<nav class="buyer-toc" aria-label="On this page">
  <a href="#pick-rule">The rule</a>
  <a href="#the-picks">The three picks</a>
  <a href="#commission">What one sale is worth</a>
  <a href="#not-a-top-ten">Why not a top ten</a>
  <a href="#read-next">Read next</a>
</nav>

<div class="callout trust" id="pick-rule">
  <strong>The rule.</strong> Buy the format, not the brand: two baskets if you cook two different things at once, a French-door oven if you also want to replace a toaster oven, one big basket if you are cooking for four to six people from a single batch. Everything else on this page is a consequence of that rule.
</div>

<section class="quick-guide" id="the-picks">
  <div class="section-heading">
    <p class="section-eyebrow">The three picks</p>
    <h2>Each one wins a different job</h2>
    <p class="small muted">Capacity is quoted from each manufacturer's own product page. The links to Amazon are the supplied affiliate links.</p>
  </div>
  <div class="grid grid-3 decision-grid">{''.join(cards)}</div>
</section>

<h2 id="commission">What one sale is actually worth</h2>
<p class="lede">Amazon pays a fixed percentage by category, not by product. Two rows of its published table are plausible for these appliances, and it does not publish which row a given ASIN falls into, so the honest answer is a range.</p>
<div class="tablewrap">
<table>
  <caption>Official Standard Commission Income rates that could apply</caption>
  <thead><tr><th>Category as published</th><th>Fixed rate</th><th>Row quoted from the official table</th></tr></thead>
  <tbody>{rate_rows}</tbody>
</table>
</div>
<div class="tablewrap" style="margin-top:1rem">
<table>
  <caption>What that is worth per sale, at each candidate rate (arithmetic on manufacturer list prices)</caption>
  <thead><tr><th>Product</th><th>Brand list price</th><th>At 4.50%</th><th>At 4.00%</th><th>Sources</th></tr></thead>
  <tbody>{examples}</tbody>
</table>
</div>
<ul class="tight small" style="margin-top:.8rem">{caveats}</ul>
<p class="small muted">Per-product mapping is deliberately not asserted: see <a href="flagged.html">Flagged for review</a> and the measurement section of <a href="decisions.html">Decisions &amp; handover</a>.</p>

<h2 id="not-a-top-ten">Why this page is not a top-ten list</h2>
<div class="grid grid-2">
  <div class="card">
    <h3 style="margin-top:0">Because "best" needs evidence this site does not have</h3>
    <p class="small">A ranking implies comparison testing. The FTC's own guidance says you cannot talk about experience with a product you have not tried, and Amazon's policies restrict republishing customer reviews and star ratings. So this page ranks <em>jobs</em>, not products, and shows the specification that supports each match.</p>
    <p class="small">{src_links(['S8', 'S2'])}</p>
  </div>
  <div class="card">
    <h3 style="margin-top:0">Because the reader can check every line</h3>
    <p class="small">Every capacity, dimension and temperature on the product pages links to the manufacturer's page or the owner's manual PDF. If a value is missing from the source, the row stays blank and appears on the flagged page instead of being filled in.</p>
    <p class="small"><a href="compare.html">See the verified-only comparison matrix \u2192</a></p>
  </div>
</div>

<h2 id="read-next">Read next</h2>
<div class="cardgrid">
  <a class="card" href="articles/small-kitchen-air-fryer-dimensions.html">
    <span class="kicker">Fit check</span>
    <span class="cardtitle">Will it actually fit? Three air fryers, measured against your counter</span>
    <span class="cardtext">Depth, height and weight, from the manufacturers' own figures.</span>
  </a>
  <a class="card" href="articles/chefman-8qt-two-models.html">
    <span class="kicker">Model watch</span>
    <span class="cardtitle">The 8-quart Chefman is sold as two different machines</span>
    <span class="cardtext">One tops out at 400\u00b0F, one reaches 450\u00b0F. The listing describes both.</span>
  </a>
  <a class="card" href="articles/energy-cost-of-an-air-fryer.html">
    <span class="kicker">Running costs</span>
    <span class="cardtitle">The 1,700-watt question</span>
    <span class="cardtext">All three units draw the same load. What that means for a kitchen circuit.</span>
  </a>
  <a class="card" href="articles/who-actually-pays-for-air-fryer-reviews.html">
    <span class="kicker">How the money works</span>
    <span class="cardtitle">Who pays for the air-fryer review you are reading?</span>
    <span class="cardtext">The disclosure rule, the law behind it, and the three claims an affiliate may not make.</span>
  </a>
</div>
"""
    purl = page_url("picks.html")
    ld = [
        {
            "@type": "ItemList",
            "@id": purl + "#picks",
            "name": "This week's picks - three air fryers, three jobs",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "name": pr["short_name"],
                    "url": page_url(f"products/{pr['slug']}.html"),
                }
                for i, pr in enumerate(PRODUCT_LIST, start=1)
            ],
        },
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("This week's picks", purl),
        ]),
    ]
    return layout("picks.html", "This week's picks \u2014 three air fryers, three jobs", body,
                  active="picks.html",
                  description="A decision-rule picks page: which of three sourced air fryers wins which job, what one sale pays at each official commission rate, and what remains unconfirmed.",
                  jsonld_blocks=ld)


def page_decisions():
    d = DECISION
    def crit_table():
        crit = d["niche"]["criteria"]
        head = "".join(f'<th title="{e(c["why"])}">{e(c["id"])}</th>' for c in crit)
        rows = ""
        for c in d["niche"]["candidates"]:
            cells = "".join(f'<td class="num">{c["score"][k["id"]]}</td>' for k in crit)
            rows += (f'<tr><td><strong>{e(c["id"])} {e(c["name"])}</strong>'
                     f'<div class="tiny muted">{e(c["basis"])}</div></td>{cells}'
                     f'<td class="num"><strong>{c["total"]}</strong></td>'
                     f'<td class="small">{e(c["recommendation"])}'
                     f'<div class="tiny">{src_links(c["source"])}</div></td></tr>')
        return (f'<div class="tablewrap"><table><caption>Niche options scored 0\u20133 '
                f'(higher is better; the scores are judgements, shown with their basis)</caption>'
                f'<thead><tr><th>Candidate niche</th>{head}<th>Total</th><th>Verdict / evidence</th></tr></thead>'
                f'<tbody>{rows}</tbody></table></div>')

    def crit_legend():
        return "".join(
            f'<li><strong>{e(c["id"])}</strong> {e(c["name"])} \u2014 {e(c["why"])}</li>'
            for c in d["niche"]["criteria"])

    def channels():
        out = ""
        for c in d["traffic"]["channels"]:
            reqs = "".join(f"<li>{e(r)}</li>" for r in c["requirements"])
            out += f"""
<div class="card channel">
  <div class="channel-head">
    <span class="pill pill-info">{e(c['id'])}</span>
    <h3>{e(c['name'])}</h3>
    <span class="pill {'pill-ok' if 'Ready' in c['status'] or 'exist' in c['status'] else 'pill-warn'}">{e(c['status'])}</span>
  </div>
  <p class="small">{e(c['works_because'])}</p>
  <p class="tiny muted" style="margin-bottom:.2rem">Requires</p>
  <ul class="tight small">{reqs}</ul>
  <p class="tiny muted"><strong>Effort:</strong> {e(c['effort'])} \u00b7 <strong>Cost:</strong> {e(c['cost'])} \u00b7 <strong>Risk:</strong> {e(c['risk'])}</p>
</div>"""
        return out

    def _msrc(m):
        if m.get("source"):
            return src_links(m["source"])
        return repo_link("reports/verification-2026-11-15.md", "this pass")
    metrics = "".join(
        f'<tr><td>{e(m["id"])}</td><td><strong>{e(m["metric"])}</strong></td>'
        f'<td class="small">{e(m["how"])}</td><td class="small">{e(m["status"])}</td>'
        f'<td class="small">{_msrc(m)}</td></tr>'
        for m in d["measurement"]["metrics"])

    rules = "".join(f"<li>{e(r)}</li>" for r in d["traffic"]["anti_slop_rules"])

    def _closes(h):
        return e(", ".join(h["closes"])) if h["closes"] else "not a flag \u2014 unblocks measurement"
    def _hsrc(h):
        if h.get("source"):
            return src_links(h["source"])
        return repo_link("COORDINATION.md", "claim record")
    handoff_rows = "".join(
        f'<tr><td><span class="pill pill-info">{e(h["id"])}</span></td>'
        f'<td>{_md(h["owner_action"])}</td><td class="num">{e(h["time"])}</td>'
        f'<td class="small">{_closes(h)}</td><td class="small">{_hsrc(h)}</td></tr>'
        for h in d["handover"]["items"])

    body = f"""
<p class="section-eyebrow">Decisions &amp; handover</p>
<h1>What has to be decided before more is built</h1>
<p class="lede">Three decisions, one measurement plan, and the short list of things only the account holder can do. Nothing on this page is implemented: it exists so the paths can be compared before anyone spends time on one.</p>
<div class="callout trust"><strong>How to read this.</strong> A number is either quoted from a registered official source or labelled an assumption. Scores in the niche table are judgements and are shown with their basis so you can disagree with them. Nothing here is a forecast of traffic or revenue.</div>

<div class="grid grid-3" style="margin:1.2rem 0">
  <a class="card" href="#niche"><span class="kicker">Decision 1</span><span class="cardtitle">Which niche</span><span class="cardtext">Four candidates, scored on five criteria, with the honest verdict.</span></a>
  <a class="card" href="#traffic"><span class="kicker">Decision 2</span><span class="cardtitle">Which traffic</span><span class="cardtext">Six channels ordered by how little they depend on things we do not have.</span></a>
  <a class="card" href="#measure"><span class="kicker">Decision 3</span><span class="cardtitle">What to measure</span><span class="cardtext">Six metrics, what each needs, and a pre-committed kill rule.</span></a>
</div>

<h2 id="niche">Decision 1 \u2014 which niche to build around</h2>
<p class="small muted">{_md(d['niche']['summary'])}</p>
{crit_table()}
<p class="tiny muted">{e(d['niche']['scoring_note'])}</p>
<details class="card tight">
  <summary><strong>What each criterion means</strong></summary>
  <ul class="tight small" style="margin-top:.6rem">{crit_legend()}</ul>
</details>
<div class="callout ok">
  <strong>Recommendation:</strong> {e(d['niche']['decision']['recommendation'])}
  <p class="small" style="margin:.4rem 0 0">{e(d['niche']['decision']['why'])}</p>
  <p class="small" style="margin:.3rem 0 0"><strong>Alternative:</strong> {e(d['niche']['decision']['alternative'])}</p>
</div>
<div class="tablewrap">
<table>
  <caption>What would have to be true for each candidate</caption>
  <thead><tr><th>Candidate</th><th>Condition</th><th>Evidence</th></tr></thead>
  <tbody>{''.join(f'<tr><td>{e(c["id"])} {e(c["name"])}</td><td class="small">{e(c["what_must_be_true"])}</td><td>{src_links(c["source"])}</td></tr>' for c in d['niche']['candidates'])}</tbody>
</table>
</div>

<h2 id="traffic">Decision 2 \u2014 how traffic would actually arrive</h2>
<p class="small muted">{e(d['traffic']['summary'])}</p>
{channels()}

<h3>Rules that keep the writing from reading like machine output</h3>
<ol class="tight small">{rules}</ol>

<h2 id="measure">Decision 3 \u2014 what to measure</h2>
<p class="small muted">{e(d['measurement']['summary'])}</p>
<div class="tablewrap">
<table>
  <caption>Six metrics and what each one needs before it can exist</caption>
  <thead><tr><th>#</th><th>Metric</th><th>How</th><th>Status</th><th>Source of the rule</th></tr></thead>
  <tbody>{metrics}</tbody>
</table>
</div>
<div class="callout">
  <strong>{e(d['measurement']['decision_rule']['heading'])}</strong>
  <p class="small" style="margin:.4rem 0 0">{e(d['measurement']['decision_rule']['rule'])}</p>
  <p class="small" style="margin:.3rem 0 0 muted">{e(d['measurement']['decision_rule']['why'])}</p>
</div>
<p class="small muted">{e(d['measurement']['untrackable_note'])}</p>

<h2 id="handover">What only you can do</h2>
<p class="small muted">{e(d['handover']['summary'])}</p>
<div class="tablewrap">
<table>
  <caption>Owner actions, time required, and the flags each one closes</caption>
  <thead><tr><th>#</th><th>Action</th><th>Time</th><th>Closes</th><th>Grounded in</th></tr></thead>
  <tbody>{handoff_rows}</tbody>
</table>
</div>
<p class="small"><a href="handover.html">Open the full handover sheet \u2014 with the exact steps and what to paste back \u2192</a></p>
<p class="small muted">Nothing on this page has been implemented. The suggestions queue, with alternative paths, effort, risk and reversibility for each item, is on <a href="suggestions.html">Suggestions</a>; the outstanding facts are on <a href="questions.html">Questions and gaps</a>.</p>
"""
    durl = page_url("decisions.html")
    ld = [breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Decisions", durl),
    ])]
    return layout("decisions.html", "Decisions \u2014 niche, traffic, measurement and handover", body,
                  active="decisions.html",
                  description="Three decisions with scored options, a six-channel traffic plan, six metrics with their prerequisites, a pre-committed kill rule, and the five actions only the account holder can take.",
                  jsonld_blocks=ld)


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
    d = DECISION["handover"]
    items = ""
    for h in d["items"]:
        closes = ", ".join(h["closes"]) if h["closes"] else "no flag \u2014 unblocks measurement"
        src = src_links(h["source"]) if h["source"] else ""
        items += f"""
<article class="card handover-item">
  <div class="handover-head">
    <span class="handover-num">{e(h['id'])}</span>
    <h2>{_md(h['owner_action'])}</h2>
    <span class="pill pill-info">{e(h['time'])}</span>
  </div>
  <p class="small">{_md(h['why_now'])}</p>
  <div class="handover-meta">
    <div><span class="tiny muted">Closes</span><div class="small">{e(closes)}</div></div>
    <div><span class="tiny muted">Paste back</span><div class="small">{_md(h['what_to_paste_back'])} {src}</div></div>
  </div>
</article>"""

    not_possible = "".join(f"<li>{e(x)}</li>" for x in d["not_possible_here"])
    body = f"""
<p class="section-eyebrow">Handover</p>
<h1>Five actions, about an hour, eighteen flags</h1>
<p class="lede">Everything in this repository is done as far as it can be done without the account holder's own logins. These five actions are the shortest path from "unverified" to "confirmed". Each shows the time it takes and the flags it closes.</p>
<div class="callout bad">
  <strong>Start with H1.</strong> Reading the model number off three Amazon listings takes about three minutes and closes the four highest-severity flags in the register. It is the only fact in the project that a headless fetch cannot read.
</div>
{items}

<h2>What cannot be done from here</h2>
<div class="card">
  <ul class="tight small">{not_possible}</ul>
</div>
<p class="small muted">When the answers come back, they are recorded in <a href="flagged.html">the flag register</a> with their source and the date read, not inferred from an earlier pass. Every published value on this site carries that same discipline.</p>
"""
    hurl = page_url("handover.html")
    ld = [breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Decisions", page_url("decisions.html")),
        ("Handover", hurl),
    ])]
    return layout("handover.html", "Handover \u2014 the five things only the account holder can do", body,
                  active="decisions.html",
                  description="Five owner actions totalling about an hour, each with the exact steps, the time required, the flags it closes and what to paste back.",
                  jsonld_blocks=ld)


# --------------------------------------------------------------------------- #
# build
# --------------------------------------------------------------------------- #

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
    """Build guard: the landing page's "Flags open" tile must equal the register it links to.

    The defect this prevents was live on main at 9c6deab: `_flag_count()` matched
    `<tr><td class="num">` while `page_flagged()` had emitted `<tr id="fNN">` since the
    per-row anchors landed, so the front page advertised "0 Flags open" beside a 61-row
    register. A typed total is what passes 9 and 10 both caught themselves getting wrong;
    a computed total is only better if something checks the computation. This does.
    """
    rendered = len(re.findall(r'<tr id="f\d+"><td class="num"><strong>F\d+</strong>',
                              page_flagged()))
    computed = _flag_count()
    if rendered == 0:
        return ["flagged.html renders no flag rows, so the landing-page count cannot be trusted"]
    if rendered != computed:
        return [f"landing-page flag count ({computed}) disagrees with the rendered "
                f"register ({rendered} rows)"]
    # The tile on index.html must publish that same number, not a literal of its own.
    idx = page_index()
    m = re.search(r'<div class="tile"><b>(\d+)</b><span>Flags open', idx)
    if not m:
        return ["index.html no longer renders the Flags open tile"]
    if int(m.group(1)) != rendered:
        return [f"index.html publishes {m.group(1)} flags, register holds {rendered}"]
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
    missing = [p for p, html_text in pages if DISCLOSURE not in html_text]
    return missing


# Hosts a table row may cite: every registered source in data/sources.json, plus this
# repository on GitHub. A row that links to none of them fails the build.
def _registered_hosts():
    from urllib.parse import urlparse
    hosts = {(urlparse(s["url"]).hostname or "").lower() for s in SOURCES["sources"]}
    hosts.add("github.com")
    return {h for h in hosts if h}


REGISTERED_HOSTS = _registered_hosts()


def row_is_sourced(row_html):
    """Row passes if it links to a registered official host, to this repo on GitHub,
    or to the Flagged-for-review page (the designed place for an unconfirmed value)."""
    from urllib.parse import urlparse
    for href in re.findall(r'href="([^"]+)"', row_html):
        u = urlparse(href)
        if u.scheme == "https" and (u.hostname or "").lower() in REGISTERED_HOSTS:
            return True
        if href.endswith("flagged.html") or "flagged.html#" in href:
            return True
    return False


def check_row_sources(pages):
    """Every table data row on every generated page must be sourced (see row_is_sourced)."""
    problems = []
    for rel, html_text in pages.items():
        for tbl in re.findall(r"<tbody>(.*?)</tbody>", html_text, re.S):
            for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", tbl, re.S):
                if "<th" in row:
                    continue
                if not row_is_sourced(row):
                    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", row)).strip()[:90]
                    problems.append(f"{rel}: {text}")
    return problems


# --------------------------------------------------------------------------- #
# pass 9 guards (session 22f43836)
# --------------------------------------------------------------------------- #

def qualify_affiliate_links(html_text):
    """Add rel="sponsored" to every clickable affiliate anchor in a rendered page.

    One post-render pass rather than fifteen template edits, so a future page that prints a
    supplied link cannot reintroduce the defect the guard now blocks. Rules match the guard:
    anchors on the affiliate host, excluding citation badges (class="src") and the
    nonsense-token control request (S22). Existing rel values are preserved and de-duplicated
    so rel="nofollow sponsored noopener" never becomes contradictory or repeated.
    """
    def fix(match):
        tag = match.group(0)
        if 'class="src"' in tag or "ZZZ9ZZZZZ" in tag:
            return tag
        rel_attr = re.search(r'rel="([^"]*)"', tag, re.I)
        if rel_attr:
            values = [v for v in rel_attr.group(1).split() if v]
        else:
            values = []
        if "sponsored" not in values:
            # sponsored must lead: it is the value that states the commercial relationship.
            values = ["sponsored"] + values
        new_tag = re.sub(r'\srel="[^"]*"', "", tag, count=1, flags=re.I)
        return new_tag[:-1].rstrip() + f' rel="{" ".join(values)}">'
    return re.sub(r'<a\b[^>]*' + AFFILIATE_HOST + r'[^>]*>', fix, html_text, flags=re.I)


AFFILIATE_HOST = "link.amazon"


def check_affiliate_link_qualification(pages):
    """Build guard: every clickable affiliate link must be qualified.

    Read verbatim 2026-11-15 from Google Search Central, "Spam policies for Google web
    search" (S30): "It's not a violation of our policies to have such links as long as
    they are qualified with a rel="nofollow" or rel="sponsored" attribute value to the
    <a> tag", and from "Qualify your outbound links to Google" (S31): "Mark links that are
    advertisements or paid placements (commonly called paid links) with the sponsored
    value."

    Scope: only anchors a reader can actually click through to Amazon, i.e. hrefs on the
    affiliate short-link host. Excluded on purpose:
      * citation badges (class="src") — these evidence a fact, they are not calls to action;
      * the nonsense-token control request (data/sources.json S22), which exists to prove
        the resolver refuses unknown tokens and must stay clickable for a human to re-test.
    Every product CTA already carried rel="nofollow sponsored"; the anchors this guard was
    written to catch are the raw supplied links printed in the evidence tables, which had
    rel="noopener" only. Refusing to qualify a link that is the site's entire commercial
    purpose is a silent revenue and compliance defect, so it is a build failure now.
    """
    anchor = re.compile(r'<a\b[^>]*' + AFFILIATE_HOST + r'[^>]*>', re.I)
    problems = []
    for rel, html_text in pages.items():
        for tag in anchor.findall(html_text):
            if 'class="src"' in tag:
                continue
            if "ZZZ9ZZZZZ" in tag:
                continue
            rel_attr = re.search(r'rel="([^"]*)"', tag, re.I)
            values = (rel_attr.group(1) if rel_attr else "").split()
            if "sponsored" not in values:
                href = re.search(r'href="([^"]+)"', tag)
                problems.append(
                    f'{rel}: affiliate link without rel="sponsored": '
                    f'{(href.group(1) if href else tag)[:90]}')
    return problems


def check_heading_order(pages):
    """Build guard: the heading outline of every generated page must be walkable.

    Written because the defect was live on 2026-11-16: the footer labelled its
    five columns with ``<h5>``, so every generated page skipped a heading level
    (h2 or h3 -> h5), and two pages skipped one inside ``<main>`` (h1 -> h3).
    A skipped level breaks the outline that a screen-reader user and the
    heading parsers behind structured data both build from the page, and it
    is invisible in a visual review — which is exactly the kind of defect
    that comes back with the next template edit.

    House rule enforced here:
      * exactly one ``<h1>`` per page;
      * no heading may sit more than one level deeper than the one before it;
      * no ``<h5>`` or ``<h6>`` anywhere — the site uses h1..h4 only.
    """
    problems = []
    heading_re = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.S | re.I)
    for rel, html_text in sorted(pages.items()):
        if not rel.endswith(".html"):
            continue
        body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html_text, flags=re.S)
        headings = []
        for m in heading_re.finditer(body):
            level = int(m.group(1))
            text = re.sub(r"<[^>]+>", "", m.group(2))
            text = re.sub(r"\s+", " ", text).strip()
            headings.append((level, text))
        if not headings:
            problems.append(f"{rel}: page has no headings at all")
            continue
        h1s = [h for h in headings if h[0] == 1]
        if len(h1s) != 1:
            problems.append(f"{rel}: {len(h1s)} <h1> elements (expected exactly 1)")
        prev = None
        for level, text in headings:
            if level >= 5:
                problems.append(f"{rel}: <h{level}> used ({text[:40]!r}); the site uses h1..h4 only")
            if prev is not None and level > prev + 1:
                problems.append(f"{rel}: heading jumps from h{prev} to h{level} at {text[:40]!r}")
            prev = level
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
        if rel == "404.html":
            if not re.search(r'<meta name="robots" content="noindex"', html_text):
                problems.append(f"{rel}: 404 page must carry a noindex robots meta")
            if 'rel="canonical"' in html_text:
                problems.append(f"{rel}: 404 page must not declare a canonical URL")
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


def main():
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "style.css").write_text(CSS, encoding="utf-8")
    (assets / "app.js").write_text(JS, encoding="utf-8")

    for d in ("products", "categories", "guides", "articles"):
        (ROOT / d).mkdir(exist_ok=True)

    pages = {}
    pages["index.html"] = page_index()
    for p in PRODUCT_LIST:
        pages[f"products/{p['slug']}.html"] = page_product(p)
    pages["categories/kitchen-appliances.html"] = page_category()
    pages["compare.html"] = page_compare()
    pages["guides/buying-guide-air-fryers.html"] = page_guide()
    pages["articles/index.html"] = page_articles_index()
    for _a in ARTICLES["articles"]:
        pages[f"articles/{_a['slug']}.html"] = page_article(_a)
    pages["data.html"] = page_data()
    pages["compliance.html"] = page_compliance()
    pages["flagged.html"] = page_flagged()
    pages["platform.html"] = page_platform()
    pages["executive-summary.html"] = page_exec()
    pages["reverification.html"] = page_reverification()
    pages["picks.html"] = page_picks()
    pages["decisions.html"] = page_decisions()
    pages["handover.html"] = page_handover()
    pages["suggestions.html"] = page_suggestions()
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
    price_problems = check_no_price_tracking(pages)
    if price_problems:
        raise SystemExit("BUILD FAILED — Prohibited feature (Program Policies 6(y)):\n  "
                         + "\n  ".join(price_problems))
    seo_problems = check_seo_metadata(pages)
    if seo_problems:
        raise SystemExit("BUILD FAILED - SEO/sharing metadata:\n  " + "\n  ".join(seo_problems))
    heading_problems = check_heading_order(pages)
    if heading_problems:
        raise SystemExit("BUILD FAILED - heading outline:\n  " + "\n  ".join(heading_problems))
    affiliate_problems = check_affiliate_link_qualification(pages)
    if affiliate_problems:
        raise SystemExit("BUILD FAILED - unqualified affiliate links (Google spam policies, "
                         "S30/S31):\n  " + "\n  ".join(affiliate_problems))
    req_path_problems = check_requirement_paths(generated=pages.keys())
    if req_path_problems:
        raise SystemExit("BUILD FAILED - requirements register cites paths that do not exist:\n  "
                         + "\n  ".join(req_path_problems))
    unsourced_rows = check_row_sources(pages)
    if unsourced_rows:
        raise SystemExit("BUILD FAILED — table rows with no official source link (cite a registered "
                         "source, this repo on GitHub, or the Flagged page):\n  "
                         + "\n  ".join(unsourced_rows))

    dangling_ids = check_register_cross_references(pages)
    if dangling_ids:
        raise SystemExit("BUILD FAILED — a published page points at an id that does not exist in any "
                         "register:\n  " + "\n  ".join(dangling_ids))

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

    # ---- pass 7 additive (sess-ce4070ad, T25): SEO plumbing -----------------
    # The brief calls for an SEO-optimized site; until this pass the root build
    # shipped neither robots.txt nor a sitemap. Both are generated here from the
    # same page list the HTML is generated from, so they cannot drift from it.
    # 404.html is excluded (not an indexable page). The annex builds (docs/,
    # research/, s2/, site/, dashboard/, session-*/) are separate sub-sites owned
    # by other sessions and deliberately stay out of the root sitemap.
    base = "https://kanlerxz87-cyber.github.io/Zone1/"
    indexable = sorted(
        rel for rel in pages
        if rel.endswith(".html") and rel != "404.html"
    )
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + base + "sitemap.xml\n",
        encoding="utf-8")
    # <lastmod> carries the date the published values were last re-read against their
    # official sources (REVERIFIED), not the date the file was written. Added
    # 2026-11-15 (arena/88bb2db6) so crawlers get a real content-change signal.
    lastmod = REVERIFIED or ACCESSED
    locs = "".join(
        f"  <url><loc>{base}{'' if rel == 'index.html' else rel}</loc>"
        f"<lastmod>{lastmod}</lastmod></url>\n"
        for rel in indexable
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + locs + "</urlset>\n",
        encoding="utf-8")
    print(f"wrote robots.txt + sitemap.xml ({len(indexable)} urls)")


if __name__ == "__main__":
    main()
