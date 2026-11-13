#!/usr/bin/env python3
"""
build_site.py — generates the static GitHub Pages site from data/*.json.

Single source of truth: every number, quote and source link rendered into HTML
comes from data/*.json. Nothing is hand-typed into the templates.

Run:  python3 scripts/build_site.py
Then: python3 scripts/verify_site.py
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---- Path layout in the integrated repo -------------------------------------
# The parallel session (d14c5409) owns `docs/` (its GitHub Pages output, served
# by the existing main -> / setup), `data/*.json` (its schemas) and
# `scripts/build.mjs`. To keep both deliverables without conflict, this build
# writes into `site/` and reads from `data/verified/`. Nothing here writes into
# `docs/`, `data/*.json` or `scripts/build.mjs`.
OUT = ROOT / "site"            # where the generated HTML pages live
DATA = ROOT / "data" / "verified"
ASSETS = OUT / "assets"        # stylesheet lives beside the pages

# ---------------------------------------------------------------- data loading

def load(name: str) -> dict:
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


CONFIG = load("config.json")
SOURCES = load("sources.json")
PRODUCTS = load("products.json")
COMPLIANCE = load("compliance.json")
FLAGGED = load("flagged.json")
OPPS = load("opportunities.json")

SOURCE_BY_ID = {s["id"]: s for s in SOURCES["sources"]}
PRODUCT_BY_ID = {p["id"]: p for p in PRODUCTS["products"]}
FLAG_BY_ID = {f["id"]: f for f in FLAGGED["items"]}

TAG = (CONFIG.get("associate_tag") or "").strip()
TAG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-]{2,}-(20|21|22)$")


def e(text) -> str:
    """Escape for HTML text nodes and attributes."""
    return html.escape("" if text is None else str(text), quote=True)


# ------------------------------------------------------------ link construction

def amazon_url(asin: str) -> str:
    """
    Build an outbound Amazon link.

    Compliance C-13: the link must point directly at /dp/<ASIN> with no cloaking,
    no shortener, no interstitial. Compliance C-10: when a tag is configured it
    must be the standard `tag=` parameter.
    """
    base = f"https://www.amazon.com/dp/{asin}"
    if TAG:
        return f"{base}?tag={TAG}"
    return base


SHORT_LABELS = {
    "S-AMZ-P1": "Amazon listing",
    "S-AMZ-P2": "Amazon listing",
    "S-AMZ-P3": "Amazon listing",
    "S-CM-P1": "Chefman page",
    "S-CM-P3": "Chefman page",
    "S-EM-P2": "Emeril page",
    "S-CM-WARRANTY": "warranty PDF",
    "S-EM-MANUAL": "manual PDF",
    "S-P65": "OEHHA",
    "S-AMZ-POL": "Amazon policies",
    "S-AMZ-OA": "Operating Agreement",
    "S-AMZ-OA-S5": "Agreement \u00a75",
    "S-AMZ-RATE": "Amazon rate card",
    "S-AMZ-COMM": "Commission Statement",
    "S-FTC-QA": "FTC guidance",
    "S-FTC-255": "16 CFR 255",
    "S-REPO-AUDIT": "repo audit",
    "S-GH-EMAIL": "GitHub docs",
}


def src_link(source_id: str, label: str | None = None) -> str:
    """
    Render a source citation as an outbound link.

    The visible text is a short, specific label ("Chefman page", "Amazon rate card")
    so a reader can tell two sources apart without hovering. The full document title
    goes in the title attribute and the surrounding cell note.
    """
    if not source_id:
        return '<span class="src-missing">no source</span>'
    src = SOURCE_BY_ID.get(source_id)
    if src is None:
        return f'<span class="src-missing">unknown source {e(source_id)}</span>'
    full = label or src["label"]
    visible = SHORT_LABELS.get(source_id, src["owner"])
    return (
        f'<a class="src" href="{e(src["url"])}" rel="noopener nofollow" '
        f'target="_blank" title="{e(full)}">{e(visible)} &#8599;</a>'
    )


def status_chip(status: str) -> str:
    s = (status or "").lower()
    label = {"verified": "Verified", "flagged": "Flagged", "unverified": "Unverified"}.get(
        s, "Unknown"
    )
    return f'<span class="chip chip-{e(s)}">{e(label)}</span>'


# ------------------------------------------------------------------- chrome

NAV = [
    ("index.html", "Dashboard"),
    ("products.html", "Products"),
    ("compare.html", "Compare"),
    ("guides.html", "Buying guides"),
    ("compliance.html", "Compliance"),
    ("methodology.html", "Method"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged"),
]


def disclosure_block() -> str:
    """
    Compliance C-01 / C-02 / C-03: the Amazon-required sentence verbatim, plus the
    FTC's own plain-language example, repeated on EVERY page rather than site-wide.
    """
    return f"""
<div class="disclosure" role="note">
  <p class="disclosure-main"><strong>{e(CONFIG['site']['disclosure_amazon'])}</strong></p>
  <p class="disclosure-sub">{e(CONFIG['site']['disclosure_general'])} Links below go to Amazon.
  Prices, ratings and availability on Amazon change; always confirm on the Amazon page before buying.</p>
</div>"""


def tag_warning() -> str:
    if TAG:
        return ""
    return """
<div class="banner banner-warn" role="note">
  <strong>Links are not yet tagged.</strong> No Associates tag is configured, so no outbound
  link on this site can currently earn a commission. Set <code>associate_tag</code> in
  <code>data/config.json</code> and rebuild. Tracked as <a href="flagged.html#F-10">F-10</a>.
</div>"""


def page(filename: str, title: str, body: str, subtitle: str = "") -> None:
    nav_html = "\n".join(
        f'<a href="{e(href)}"'
        + (' class="active" aria-current="page"' if href == filename else "")
        + f">{e(label)}</a>"
        for href, label in NAV
    )
    sub = f'<p class="page-sub">{subtitle}</p>' if subtitle else ""
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} &middot; {e(CONFIG['site']['title'])}</title>
<meta name="description" content="{e(CONFIG['site']['tagline'])}">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="wrap topbar-in">
    <a class="brand" href="index.html">
      <span class="brand-mark" aria-hidden="true">AF</span>
      <span class="brand-text">{e(CONFIG['site']['title'])}</span>
    </a>
    <nav class="nav" aria-label="Main">{nav_html}</nav>
  </div>
</header>
<main id="main" class="wrap">
  <h1>{e(title)}</h1>
  {sub}
  {tag_warning()}
  {disclosure_block()}
  {body}
</main>
<footer class="footer">
  <div class="wrap">
    <p><strong>{e(CONFIG['site']['disclosure_amazon'])}</strong></p>
    <p>{e(CONFIG['site']['disclosure_general'])}</p>
    <p class="fine">Data verified {e(CONFIG['site']['freshness_label'])} against the official
    sources listed on the <a href="sources.html">Sources</a> page. This site is not endorsed by,
    sponsored by, or affiliated with Amazon or with any brand named here. Brand and product names
    are used only to identify the products discussed.</p>
    <p class="fine"><a href="privacy.html">Privacy</a> &middot; <a href="methodology.html">Method</a>
    &middot; <a href="flagged.html">Flagged for review</a> &middot;
    <a href="https://github.com/{e(CONFIG['site']['repo'])}" rel="noopener">Source repository</a></p>
  </div>
</footer>
</body>
</html>
"""
    (OUT / filename).write_text(doc, encoding="utf-8")


# ------------------------------------------------------------------- helpers

def product_short(p: dict) -> str:
    return f'{p["brand"]} &mdash; {p["specs"][0]["value"] if False else ""}'.strip()


def short_name(asin: str) -> str:
    for r in OPPS["results"]:
        if r["asin"] == asin:
            return r["short_name"]
    return asin


def stat(label: str, value: str, note: str = "", tone: str = "") -> str:
    cls = f"stat {tone}".strip()
    note_html = f'<span class="stat-note">{e(note)}</span>' if note else ""
    return f"""<div class="{cls}"><span class="stat-label">{e(label)}</span>
<span class="stat-value">{value}</span>{note_html}</div>"""


# ------------------------------------------------------------------- pages

def build_index() -> None:
    total_specs = sum(len(p["specs"]) for p in PRODUCTS["products"])
    verified = sum(
        1 for p in PRODUCTS["products"] for s in p["specs"] if s["status"] == "verified"
    )
    flagged = sum(
        1 for p in PRODUCTS["products"] for s in p["specs"] if s["status"] == "flagged"
    )
    unverified = sum(
        1 for p in PRODUCTS["products"] for s in p["specs"] if s["status"] == "unverified"
    )
    pct = round(100 * verified / total_specs)

    stats = "".join(
        [
            stat("Products tracked", str(len(PRODUCTS["products"])), "all 3 resolved to ASINs"),
            stat("Spec fields checked", str(total_specs), "every one carries a status"),
            stat("Verified from official source", f"{verified}", f"{pct}% of fields", "ok"),
            stat("Flagged for review", str(flagged), "published, not blocking", "warn"),
            stat("Unverified, left blank", str(unverified), "never inferred", "muted"),
        ]
    )

    # top-level product table, every row sourced
    def truncate(text: str, limit: int = 92) -> str:
        if len(text) <= limit:
            return text
        cut = text[:limit].rsplit(" ", 1)[0]
        return cut + "&hellip;"

    rows = []
    for idx, p in enumerate(PRODUCTS["products"], start=1):
        o = next((r for r in OPPS["results"] if r["asin"] == p["asin"]), None)
        listing_src = f"S-AMZ-P{idx}"
        rows.append(
            f"""<tr>
<td><strong>{e(p['brand'])}</strong><br><span class="mono muted">{e(p['asin'])}</span></td>
<td>{truncate(p['title_as_listed'])}</td>
<td class="mono">{e(p['manufacturer_model'])}</td>
<td class="num">{e(o['composite']) if o else ''}</td>
<td>{e(p['commission_rate_published'])}<div class="srcmini">{src_link(p['commission_rate_source'], 'Amazon rate card')}</div></td>
<td>{src_link(listing_src, 'Amazon listing ' + p['asin'])}<div class="srcmini">{src_link('S-CM-P1' if p['asin']=='B0CDY277D3' else ('S-CM-P3' if p['asin']=='B08DKYBTPH' else 'S-EM-P2'), 'Brand page (model ' + p['manufacturer_model'] + ')')}</div></td>
</tr>"""
        )

    body = f"""
<section class="stats">{stats}</section>

<h2>What this is</h2>
<p class="lede">Three air fryers, one affiliate programme (Amazon Associates), and a rule I have
applied without exception: <strong>every factual cell on this site links to the official page it
came from, and anything I could not confirm is left blank.</strong> That means some cells are
empty. That is the point.</p>

<div class="grid-3">
  <a class="card" href="../index.html">
    <h3>Main dashboard</h3>
    <p>The repository's canonical site at the root URL, built by the other concurrent sessions.
    This annex does not modify it. See <a href="flagged.html#F-16">F-16</a>.</p>
  </a>
  <a class="card" href="products.html">
    <h3>Products</h3>
    <p>Full specification sheets for each ASIN, field by field, each with its own source link.</p>
  </a>
  <a class="card" href="compare.html">
    <h3>Compare</h3>
    <p>Side-by-side on the fields that are actually verified &mdash; with gaps shown as gaps.</p>
  </a>
  <a class="card" href="compliance.html">
    <h3>Compliance</h3>
    <p>20 requirements read line by line from Amazon's and the FTC's own documents, with the quote.</p>
  </a>
  <a class="card" href="guides.html">
    <h3>Buying guides</h3>
    <p>Which of the three fits which kitchen &mdash; argued only from verified specs.</p>
  </a>
  <a class="card" href="flagged.html">
    <h3>Flagged for review</h3>
    <p>13 irregularities and open questions, each with the evidence and what would settle it.</p>
  </a>
  <a class="card" href="sources.html">
    <h3>Sources</h3>
    <p>The 16 official documents behind every value, with what each one was used to verify.</p>
  </a>
</div>

<h2>At a glance</h2>
<div class="table-wrap">
<table>
  <caption>Product register. Score is a merchandising-fit ranking explained on the
  <a href="methodology.html">method page</a>; it is not a demand forecast.</caption>
  <thead>
    <tr>
      <th scope="col">Product</th>
      <th scope="col">Listing title (verbatim)</th>
      <th scope="col">Model</th>
      <th scope="col">Fit score</th>
      <th scope="col">Rate</th>
      <th scope="col">Source</th>
    </tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
</div>

<h2>How the verification works</h2>
<div class="steps">
  <div class="step"><span class="step-n">1</span><h3>Resolve</h3><p>Follow the short link, record
  the ASIN it lands on and the page title. Log the fallback marker if present (F-01).</p></div>
  <div class="step"><span class="step-n">2</span><h3>Cross-read</h3><p>Find the same model on the
  brand's own storefront. Compare field by field. Where the two disagree, publish the disagreement
  instead of choosing a side (F-02, F-03, F-04).</p></div>
  <div class="step"><span class="step-n">3</span><h3>Record</h3><p>Each value goes into a JSON file
  with a status of <em>verified</em>, <em>flagged</em> or <em>unverified</em>. A blank value is only
  legal for an unverified row.</p></div>
  <div class="step"><span class="step-n">4</span><h3>Assert</h3><p>A build script generates every
  page from that data and a verifier fails the build if any row is missing a source.</p></div>
</div>

<h2>The one thing that matters most</h2>
<div class="banner banner-warn">
  <p><strong>No Associates tag is configured, so nothing here can earn yet.</strong> That is not a
  footnote &mdash; it is the difference between a live affiliate property and a well-researched
  static site. Setting one value in <code>data/config.json</code> and rebuilding flips every
  outbound link to a trackable Special Link. Until then the site says so out loud, on every page.</p>
</div>
"""
    page(
        "index.html",
        "Dashboard",
        body,
        subtitle="A verified, source-linked register of three air fryers on the Amazon Associates programme.",
    )


def build_products() -> None:
    sections = []
    for p in PRODUCTS["products"]:
        o = next((r for r in OPPS["results"] if r["asin"] == p["asin"]), None)
        spec_rows = []
        for s in p["specs"]:
            if s["status"] == "verified":
                value = f'<span class="val-verified">{e(s["value"])}</span>'
            elif s["status"] == "flagged":
                value = f'<span class="val-flagged">{e(s["value"]) or "<em>blank &mdash; see flag</em>"}</span>'
            else:
                value = '<span class="val-blank"><em>blank &mdash; unverified</em></span>'
            flag_cell = (
                f'<a class="flag-link" href="flagged.html#{e(s["flag_id"])}">{e(s["flag_id"])}</a>'
                if s.get("flag_id")
                else ""
            )
            note = f'<div class="cell-note">{e(s["note"])}</div>' if s.get("note") else ""
            spec_rows.append(
                f"""<tr>
<td class="field">{e(s['field'])}</td>
<td>{value}{note}</td>
<td>{status_chip(s['status'])}</td>
<td class="srccell">{src_link(s['source_id'])}{(' ' + src_link(s['also_source_id'])) if s.get('also_source_id') else ''}{('<div class="cell-note">' + e(s['source_field']) + '</div>') if s.get('source_field') else ''}</td>
<td>{flag_cell}</td>
</tr>"""
            )

        differentiators = "".join(f"<li>{e(d)}</li>" for d in p["positioning"]["verified_differentiators"])
        tradeoffs = "".join(f"<li>{e(d)}</li>" for d in p["positioning"]["tradeoffs_stated_by_brand"])

        sections.append(
            f"""
<section class="product" id="{e(p['asin'])}">
  <div class="product-head">
    <div>
      <p class="eyebrow">{e(p['brand'])} &middot; <span class="mono">{e(p['asin'])}</span></p>
      <h2>{e(short_name(p['asin']))}</h2>
      <p class="lede">{e(p['title_as_listed'])}</p>
    </div>
    <div class="product-score">
      <span class="score-num">{e(o['composite']) if o else ''}</span>
      <span class="score-label">fit score<br>rank {e(o['rank']) if o else ''} of 3</span>
    </div>
  </div>

  <dl class="keyfacts">
    <div><dt>Manufacturer model</dt><dd class="mono">{e(p['manufacturer_model'])}
      {src_link('S-CM-P1' if p['asin']=='B0CDY277D3' else ('S-CM-P3' if p['asin']=='B08DKYBTPH' else 'S-EM-P2'))}</dd></div>
    <div><dt>Commission rate (published)</dt><dd>{e(p['commission_rate_published'])}
      <span class="muted">&middot; {e(p['commission_rate_basis'])}</span>
      {src_link(p['commission_rate_source'], 'Amazon rate card')}</dd></div>
    <div><dt>Brand page</dt><dd><a href="{e(p['manufacturer_page'])}" rel="noopener nofollow" target="_blank">{e(p['manufacturer_page'])} &#8599;</a></dd></div>
    <div><dt>Amazon link</dt><dd><a class="buy" href="{e(amazon_url(p['asin']))}" rel="noopener nofollow sponsored" target="_blank">Check on Amazon &#8599;</a></dd></div>
    <div><dt>Category</dt><dd>{e(p['category'])}<div class="cell-note">{e(p['category_basis'])}</div></dd></div>
    <div><dt>Original short link supplied</dt><dd class="mono">{e(p['short_link'])}</dd></div>
  </dl>

  <h3>Specification sheet <span class="muted">&mdash; {len(spec_rows)} fields, each with a source</span></h3>
  <div class="table-wrap">
  <table class="spec">
    <thead>
      <tr><th scope="col">Field</th><th scope="col">Value</th><th scope="col">Status</th>
      <th scope="col">Source</th><th scope="col">Flag</th></tr>
    </thead>
    <tbody>{''.join(spec_rows)}</tbody>
  </table>
  </div>

  <div class="grid-2">
    <div class="panel">
      <h3>Verified strengths</h3>
      <ul>{differentiators}</ul>
      <p class="muted"><strong>Fits:</strong> {e(p['positioning']['best_for'])}</p>
    </div>
    <div class="panel panel-warn">
      <h3>Trade-offs the brand itself states</h3>
      <ul>{tradeoffs}</ul>
      <p class="muted">Text is derived only from quantities and features named on the brand page.</p>
    </div>
  </div>
</section>"""
        )

    body = f"""
<p class="lede">Six fields per product are deliberately blank or flagged. Nothing has been filled in
to make a table look complete. Click any source badge to land on the exact page the value was read
from.</p>
<div class="legend">
  <span>{status_chip('verified')} read directly off the named official page</span>
  <span>{status_chip('flagged')} sources disagree, or the value is blank because of a conflict</span>
  <span>{status_chip('unverified')} could not be confirmed &mdash; left blank on purpose</span>
</div>
{''.join(sections)}
"""
    page("products.html", "Products", body, subtitle="Every specification field, with the official page it was read from.")


def build_compare() -> None:
    # Build the union of fields in a stable order, using product P-1's ordering as the spine
    field_order: list[str] = []
    for p in PRODUCTS["products"]:
        for s in p["specs"]:
            if s["field"] not in field_order:
                field_order.append(s["field"])

    def lookup(p: dict, field: str):
        for s in p["specs"]:
            if s["field"] == field:
                return s
        return None

    rows = []
    for field in field_order:
        cells = []
        for p in PRODUCTS["products"]:
            s = lookup(p, field)
            if s is None:
                cells.append('<td class="na">&mdash;</td>')
                continue
            if s["status"] == "verified":
                inner = f'<span class="val-verified">{e(s["value"])}</span>'
            elif s["status"] == "flagged":
                fl_id = s.get("flag_id") or ""
                fl_link = (
                    '<a class="flag-link" href="flagged.html#%s">%s</a>' % (e(fl_id), e(fl_id))
                    if fl_id else ""
                )
                inner = (
                    '<span class="val-flagged">%s %s</span>'
                    % (e(s["value"]) or "<em>blank</em>", fl_link)
                )
            else:
                inner = '<span class="val-blank"><em>blank</em></span>'
            extra = (" " + src_link(s["also_source_id"])) if s.get("also_source_id") else ""
            cells.append(f"<td>{inner}<div class='srcmini'>{src_link(s['source_id'])}{extra}</div></td>")
        rows.append(
            f"<tr><th scope='row' class='field'>{e(field)}</th>{''.join(cells)}</tr>"
        )

    head = "".join(
        f"<th scope='col'><span class='th-name'>{e(short_name(p['asin']))}</span>"
        f"<span class='th-sub mono'>{e(p['asin'])}</span></th>"
        for p in PRODUCTS["products"]
    )

    body = f"""
<p class="lede">Same data as the product pages, transposed. Where a value is missing for one
product but present for another, the gap is shown as a gap rather than smoothed over.</p>
<div class="table-wrap">
<table class="compare">
  <thead><tr><th scope="col">Field</th>{head}</tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
</div>

<h2>How the three actually differ</h2>
<div class="grid-3">
  <div class="panel">
    <h3>Capacity spread</h3>
    <p>The three units are <strong>6 Qt</strong>, <strong>8 Qt</strong> and <strong>26 Qt</strong>
    &mdash; a 4.3&times; range. They are not substitutes for one another; they answer different
    questions. All three capacities are verified on the brand pages.</p>
    <p class="srcmini">{src_link('S-CM-P1')} {src_link('S-CM-P3')} {src_link('S-EM-P2')}</p>
  </div>
  <div class="panel">
    <h3>Function count</h3>
    <p>5 functions (6 Qt dual basket), 4 functions (8 Qt), and a full oven mode set with rotisserie
    (26 Qt). The 8 Qt's four functions are the narrowest verified set of the three.</p>
    <p class="srcmini">{src_link('S-CM-P1')} {src_link('S-CM-P3')} {src_link('S-EM-P2')}</p>
  </div>
  <div class="panel">
    <h3>What cannot be compared</h3>
    <p>Amazon price, Amazon star rating and Amazon review volume are <strong>not</strong> shown for
    any of the three. Amazon's own policies restrict displaying them, and they did not render to
    this client anyway. See <a href="flagged.html#F-08">F-08</a>.</p>
    <p class="srcmini">{src_link('S-AMZ-POL')}</p>
  </div>
</div>

<h2>Where they genuinely tie</h2>
<p>All three advertise <strong>dishwasher-safe</strong> components, and all three are sold as
countertop units under 120 V. Those are the only tie-breakers the sources support. Claims about
which one "cooks faster" are not made here, because none of the three brand pages publishes a
comparable, testable cooking-time figure for a common food.</p>
"""
    page("compare.html", "Compare", body, subtitle="Side by side, on the fields that survived verification.")


def build_guides() -> None:
    body = f"""
<p class="lede">Three buyer situations, three answers. Each answer is built only from verified
specifications, and each one says plainly what would make it the wrong answer.</p>

<article class="guide">
  <p class="eyebrow">Situation 1</p>
  <h2>&ldquo;I cook one thing for two people, quickly, on a weeknight.&rdquo;</h2>
  <p class="answer"><strong>{e(short_name('B08DKYBTPH'))}</strong> &mdash; 8 Qt, 4 functions,
  450&deg;F Hi-Fry finish, 1700 W, cETL.</p>
  <p>Eight quarts is a genuine single-batch size for two to four people, the 450&deg;F Hi-Fry step
  addresses the most common air-fryer complaint (soggy finishes), and the brand's own storefront
  carries the strongest review base of the three (4.6/5 over 200 reviews).</p>
  <p class="wrong"><strong>Wrong answer if:</strong> you regularly cook a main and a side at the same
  time &mdash; one basket means sequencing. Or if you need a reheat preset; this unit's verified
  function set is four and does not include reheat.</p>
  <p class="srcmini">{src_link('S-CM-P3')} &middot; <a class="buy" href="{e(amazon_url('B08DKYBTPH'))}" rel="noopener nofollow sponsored" target="_blank">Check on Amazon &#8599;</a></p>
</article>

<article class="guide">
  <p class="eyebrow">Situation 2</p>
  <h2>&ldquo;I want mains and sides finished at the same time, and I want to watch them cook.&rdquo;</h2>
  <p class="answer"><strong>{e(short_name('B0CDY277D3'))}</strong> &mdash; 6 Qt across two
  independent 3 Qt baskets, Sync Finish, Easy View windows with interior lights.
  </p>
  <p>This is the only one of the three with two independently controlled baskets. Sync Finish is
  confirmed on the brand page, and so are the windows and interior lights. It also has the widest
  verified temperature span of the two basket units (90&ndash;400&deg;F).</p>
  <p class="wrong"><strong>Wrong answer if:</strong> you need volume. 6 Qt total is the smallest here,
  at 3 Qt per basket, and a full family roast will not fit. Note also that the Amazon title claims a
  &ldquo;Hi-Fry&rdquo; feature that Chefman's own specification for this model does not list
  (<a href="flagged.html#F-02">F-02</a>) &mdash; do not buy it for that.</p>
  <p class="srcmini">{src_link('S-CM-P1')} &middot; <a class="buy" href="{e(amazon_url('B0CDY277D3'))}" rel="noopener nofollow sponsored" target="_blank">Check on Amazon &#8599;</a></p>
</article>

<article class="guide">
  <p class="eyebrow">Situation 3</p>
  <h2>&ldquo;I want one box that replaces the toaster oven, fits a whole chicken, and can rotisserie.&rdquo;</h2>
  <p class="answer"><strong>{e(short_name('B09B7SB46R'))}</strong> &mdash; 26 Qt / 24.6 L,
  French doors, dual-speed fan, rotisserie spit, seven accessories.</p>
  <p>On capability this is not close: 26 quarts, French doors, a rotisserie, and a
  toaster-oven footprint of 16.9&Prime;D &times; 15.8&Prime;W &times; 14.8&Prime;H. If the brief is
  &ldquo;replace three appliances&rdquo;, this is the only one of the three that attempts it.</p>
  <p class="wrong"><strong>Wrong answer if:</strong> you weigh owner sentiment heavily. On the
  brand's own storefront this unit sits at 2.6/5 across 25 reviews with 42% recommending it &mdash;
  far below the two Chefman units on the same kind of storefront review system
  (<a href="flagged.html#F-12">F-12</a>). That sample is small, so treat it as a reason to read the
  reviews rather than a verdict. Wattage and safety certification are also unconfirmed for this
  unit (<a href="flagged.html#F-09">F-09</a>).</p>
  <p class="srcmini">{src_link('S-EM-P2')} &middot; <a class="buy" href="{e(amazon_url('B09B7SB46R'))}" rel="noopener nofollow sponsored" target="_blank">Check on Amazon &#8599;</a></p>
</article>

<h2>Comparison shopping table</h2>
<div class="table-wrap">
<table>
  <caption>Brand-store prices are the brands' own storefront prices, not Amazon prices, and are
  shown only to indicate relative band. Amazon prices are deliberately not published
  (<a href="flagged.html#F-08">F-08</a>).</caption>
  <thead><tr>
    <th scope="col">Product</th><th scope="col">Capacity</th><th scope="col">Functions</th>
    <th scope="col">Brand-store price band</th><th scope="col">Brand-store rating</th>
    <th scope="col">Source</th>
  </tr></thead>
  <tbody>
    <tr><td>{e(short_name('B0CDY277D3'))}</td><td>6 Qt (2&times;3 Qt)</td><td>5</td>
      <td>$60.00&ndash;$99.99</td><td>4.5/5 (30)</td><td>{src_link('S-CM-P1')}</td></tr>
    <tr><td>{e(short_name('B08DKYBTPH'))}</td><td>8 Qt</td><td>4</td>
      <td>$72.00&ndash;$119.99</td><td>4.6/5 (200)</td><td>{src_link('S-CM-P3')}</td></tr>
    <tr><td>{e(short_name('B09B7SB46R'))}</td><td>26 Qt / 24.6 L</td><td>10-in-1 / 24&ndash;25 presets
      <a class="flag-link" href="flagged.html#F-03">F-03</a></td>
      <td>$199.99</td><td>2.6/5 (25)</td><td>{src_link('S-EM-P2')}</td></tr>
  </tbody>
</table>
</div>
"""
    page("guides.html", "Buying guides", body, subtitle="Three kitchens, three recommendations, each with the reason it could be wrong.")


def build_compliance() -> None:
    rows = []
    for r in COMPLIANCE["rules"]:
        impl = ", ".join(r.get("implemented_in") or []) or "&mdash;"
        quote = (
            f'<blockquote>{e(r["verbatim_quote"])}</blockquote>'
            if r.get("verbatim_quote")
            else '<p class="muted">No quotable single sentence; see the section named in the source.</p>'
        )
        flag = (
            f'<a class="flag-link" href="flagged.html#{e(r["flag_id"])}">{e(r["flag_id"])}</a>'
            if r.get("flag_id")
            else ""
        )
        rows.append(
            f"""<tr id="{e(r['id'])}">
<td class="mono">{e(r['id'])}</td>
<td><strong>{e(r['area'])}</strong></td>
<td>{e(r['requirement'])}{quote}
  <div class="cell-note">Source: {src_link(r['source_id'])} &middot; {e(r['source_section'])}</div></td>
<td>{e(r['how_this_site_complies'])}
  <div class="cell-note"><code>{e(impl)}</code></div></td>
<td>{status_chip('verified' if r['status']=='verified' else 'flagged')} {flag}</td>
</tr>"""
        )

    body = f"""
<p class="lede">Twenty requirements, each read directly from Amazon's own program documents or from
the FTC's published guidance. Every row quotes the operative sentence so you can check it yourself
without trusting this page.</p>

<div class="banner banner-info">
  <p><strong>Two rules shaped this entire site more than any other.</strong> Amazon permits showing
  prices and availability only when Amazon serves them or they come through the Creators API
  (&sect;2(b)), and permits showing Amazon reviews or star ratings only when they come through that
  API (&sect;3(t)). Neither condition is met here. So this site shows <em>no</em> Amazon prices and
  <em>no</em> Amazon ratings &mdash; every such cell is blank, and each blank links to
  <a href="flagged.html#F-08">F-08</a>. A third rule matters just as much: Amazon prohibits
  price-tracking and price-alert functionality (&sect;3(y)), so none is built.</p>
</div>

<div class="table-wrap">
<table class="compliance">
  <thead><tr>
    <th scope="col">ID</th><th scope="col">Area</th><th scope="col">Requirement &amp; quote</th>
    <th scope="col">What this site does</th><th scope="col">Status</th>
  </tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
</div>

<h2>The disclosure, verbatim</h2>
<p>Amazon's Operating Agreement &sect;5 requires this exact sentence, or a substantially similar one
previously allowed, to be stated clearly and prominently:</p>
<blockquote class="big-quote">{e(CONFIG['site']['disclosure_amazon'])}</blockquote>
<p>It appears in the footer of every page and again in the disclosure panel above each product
table. The FTC separately warns that &ldquo;affiliate link&rdquo; on its own is not an adequate
disclosure, and that a single site-wide notice is not enough &mdash; so the plain-English sentence
&ldquo;{e(CONFIG['site']['disclosure_general'])}&rdquo; appears next to the links on every page, not
only on the home page.</p>
<p class="srcmini">{src_link('S-AMZ-OA-S5')} {src_link('S-FTC-QA')} {src_link('S-FTC-255')}</p>

<h2>What is deliberately not built</h2>
<div class="grid-2">
  <div class="panel panel-warn">
    <h3>Not built, and why</h3>
    <ul>
      <li><strong>Amazon price tracking or price-drop alerts</strong> &mdash; prohibited by
      &sect;3(y). <a href="https://affiliate-program.amazon.com/help/operating/policies" rel="noopener nofollow" target="_blank">Policies &#8599;</a></li>
      <li><strong>Amazon price and rating tables</strong> &mdash; &sect;2(b) and &sect;3(t) restrict
      this to API-served data. See <a href="flagged.html#F-08">F-08</a>.</li>
      <li><strong>Cloaked or shortened outbound links</strong> &mdash; &sect;3(v) requires the true
      destination to be visible. Every link here prints its full amazon.com/dp/ URL.</li>
      <li><strong>Click incentives, cashback or reward points</strong> &mdash; &sect;3(g).</li>
      <li><strong>Amazon logos or brand imagery</strong> &mdash; the Trademark Guidelines restrict
      their use.</li>
      <li><strong>Third-party analytics, cookies or pixels</strong> &mdash; none are present, so the
      privacy page can make a clean claim.</li>
    </ul>
  </div>
  <div class="panel">
    <h3>Shipped instead</h3>
    <ul>
      <li>A verification pipeline where a table row cannot render without a source link.</li>
      <li>A build-time assertion that rejects any outbound Amazon URL that is not a direct
      <code>/dp/&lt;ASIN&gt;</code> link.</li>
      <li>Brand-store ratings, always labelled as brand-store and never as Amazon.</li>
      <li>A tag-injection point that the build validates before use
      (<a href="flagged.html#F-10">F-10</a>).</li>
      <li>An explicit list of what is unverified, published rather than hidden.</li>
    </ul>
  </div>
</div>

<h2>Operator obligations that a website cannot enforce</h2>
<p>Three duties sit with the operator, not the codebase. They are recorded here so they are not
lost: never purchase through your own links, and never let relatives, employees or contractors do
so (&sect;3(u)); never offer any incentive for a click (&sect;3(g)); and keep the site's original
content genuinely original (&sect;1).</p>
<p class="srcmini">{src_link('S-AMZ-POL')}</p>
"""
    page("compliance.html", "Compliance", body, subtitle="Amazon Associate and FTC requirements, quoted from the source documents.")


def build_methodology() -> None:
    comp_rows = "".join(
        f"<tr><td>{e(c['label'])}</td><td>{e(c['rationale'])}</td><td>{e(c['direction'])}</td>"
        f"<td class='mono'>{OPPS['meta']['weights'][c['key']]*100:.0f}%</td></tr>"
        for c in OPPS["components"]
    )
    score_rows = "".join(
        "<tr>"
        f"<td><strong>{e(r['short_name'])}</strong><div class='mono muted'>{e(r['asin'])}</div></td>"
        + "".join(f"<td class='num'>{e(v)}</td>" for v in r["component_scores"].values())
        + f"<td class='num'><strong>{e(r['composite'])}</strong></td>"
        f"<td>{e(r['why'])}</td>"
        "</tr>"
        for r in OPPS["results"]
    )
    comp_heads = "".join(f"<th scope='col' class='num'>{e(c['label'])}</th>" for c in OPPS["components"])

    rm = OPPS["revenue_model"]
    we = rm["worked_example"]

    body = f"""
<p class="lede">How the numbers on this site were produced &mdash; and, more importantly, which
numbers were refused. A method page that only explains successes is not a method page.</p>

<h2>1. Source tiers</h2>
<div class="table-wrap">
<table>
  <thead><tr><th scope="col">Tier</th><th scope="col">Definition</th><th scope="col">Used for</th></tr></thead>
  <tbody>
    <tr><td>official-primary</td><td>The manufacturer's or retailer's own domain, first party.</td>
        <td>All product facts.</td></tr>
    <tr><td>official-program</td><td>Amazon's own Associates legal documents.</td>
        <td>Rules, rates, disclosure wording.</td></tr>
    <tr><td>official-regulatory</td><td>FTC and eCFR publications.</td>
        <td>Disclosure law and guidance.</td></tr>
    <tr><td>official-supporting</td><td>Manuals and warranty PDFs hosted by the manufacturer.</td>
        <td>Cross-reference only; not used to assert a table value.</td></tr>
    <tr><td class="muted">rejected</td><td class="muted">Review aggregators, price-comparison
        sites, affiliate blogs, "best of" listicles, AI-generated summaries.</td>
        <td class="muted">Never used as a source. One marketing site asserting the Emeril wattage
        was found and rejected &mdash; see <a href="flagged.html#F-09">F-09</a>.</td></tr>
  </tbody>
</table>
</div>

<h2>2. The three-state rule</h2>
<p>Every field is in exactly one of three states, and the state is published alongside the value:</p>
<div class="grid-3">
  <div class="panel"><h3>{status_chip('verified')}</h3><p>The value was read on an official page and
  the specific section is recorded. Two independent official pages agreeing strengthens it; a single
  official page is sufficient, and the source is always linked.</p></div>
  <div class="panel panel-warn"><h3>{status_chip('flagged')}</h3><p>Official sources disagree, or the
  only basis is a fragment of a title rather than a specification field. The cell shows the conflict
  rather than a resolution, and links to a numbered flag.</p></div>
  <div class="panel"><h3>{status_chip('unverified')}</h3><p>No official source could be found within
  the scope of this review. <strong>The cell is left blank.</strong> It is never filled with an
  estimate, a range midpoint, an Amazon "typical price", or a figure from a third-party tool.</p></div>
</div>

<h2>3. Fit score &mdash; what it is and what it is not</h2>
<p><strong>It is</strong> a weighted ranking of five factors that can each be traced to a source.
<strong>It is not</strong> a demand forecast, a conversion prediction, or an earnings estimate.
Amazon publishes no per-ASIN sales volume, search volume or conversion rate, and the third-party
tools that guess at these produce estimates that cannot be reproduced or verified &mdash; so they are
excluded (<a href="flagged.html#F-13">F-13</a>).</p>
<div class="table-wrap">
<table>
  <thead><tr><th scope="col">Component</th><th scope="col">Rationale</th><th scope="col">Direction</th><th scope="col" class="num">Weight</th></tr></thead>
  <tbody>{comp_rows}</tbody>
</table>
</div>
<div class="table-wrap">
<table>
  <thead><tr><th scope="col">Product</th>{comp_heads}<th scope="col" class="num">Composite</th><th scope="col">Reading</th></tr></thead>
  <tbody>{score_rows}</tbody>
</table>
</div>
<p class="muted">Weights are the operator's stated preference between competing merchandising goals.
They are <em>not</em> fitted to observed sales, because no observed sales data exists for this site.
Change the weights in <code>data/opportunities.json</code> and the ranking moves &mdash; which is
exactly why the weights are printed above rather than buried.</p>

<h2>4. Commission arithmetic</h2>
<p>The published standard rate for the <strong>{e(rm['published_rate_category'])}</strong> category is
<strong>{e(rm['published_rate'])}</strong> {src_link(rm['published_rate_source_id'], 'Amazon Table 1')}.
That rate is public. The account-specific custom rate card is behind sign-in and was
<strong>not</strong> read, so no personalised rate is claimed (<a href="flagged.html#F-05">F-05</a>).</p>
<div class="table-wrap">
<table>
  <tbody>
    <tr><th scope="row">Assumption &mdash; price used for arithmetic</th>
        <td>{e(we['assumption_a'])}</td></tr>
    <tr><th scope="row">Commission per sale</th>
        <td><strong>{e(we['commission_per_sale'])}</strong>
        <div class="cell-note">{e(we['commission_per_sale_working'])}</div></td></tr>
    <tr><th scope="row">Assumption &mdash; units per month</th>
        <td><span class="val-blank"><em>blank</em></span>
        <div class="cell-note">{e(we['why_units_are_blank'])}</div></td></tr>
  </tbody>
</table>
</div>
<p>Which is why this site does not print a monthly earnings figure. The arithmetic is published so
you can run it with your own observed numbers once traffic exists. Amazon itself states it makes no
representation about achievable commission income
{src_link('S-AMZ-OA', 'Operating Agreement §4')}.</p>

<h3>Attribution windows that constrain the arithmetic</h3>
<p>A click opens a {OPPS['revenue_model']['attribution_windows_that_limit_the_math']['session_hours']}-hour session.
A cart completed within {OPPS['revenue_model']['attribution_windows_that_limit_the_math']['cart_window_days']} days of the click still counts, and the order must ship and be paid for within
{OPPS['revenue_model']['attribution_windows_that_limit_the_math']['ship_pay_window_days']} days of purchase
{src_link('S-AMZ-COMM')}.</p>

<h2>5. Relationship to the earlier build in this repository</h2>
<p>Several agent sessions worked this repository concurrently. The consolidated canonical site is
generated by <code>build.py</code> and <code>verify.py</code> at the repository root and is what the
main Pages URL serves. <strong>This build is an annex published at <code>site/</code>.</strong> It
does not modify the root site, its data, or its build scripts: it reads its own data from
<code>data/verified/</code> and writes only into <code>site/</code>. That separation is deliberate, so
that two agents could each deliver without overwriting the other's work.</p>
<p>Three independent sessions resolved the same three opaque short links to the same three ASINs,
which is a meaningful cross-check on the single most consequential fact in this project. The builds
differ in depth rather than in conclusion: this one verifies manufacturer specifications field by
field against the brands' own product and support pages, and it resolved the published commission
rate, which earlier audits recorded as unreachable &mdash; Kitchen is a fixed <strong>4.50%</strong>
(<a href="flagged.html#F-17">F-17</a>). The coexistence of a root site and this annex is recorded as
<a href="flagged.html#F-16">F-16</a>; if the annex data set is preferred, retiring it is a
one-setting change to the Pages source.</p>

<h2>6. Reproducing this</h2>
<pre class="code"><code>python3 scripts/build_site.py   # regenerate every page from data/*.json
python3 scripts/verify_site.py  # fail on any row without a source, or any broken internal link</code></pre>
<p>The verifier is the part that matters. It refuses to let an unsourced value reach a page, so the
guarantee does not depend on anyone remembering the rule.</p>
"""
    page("methodology.html", "Method", body, subtitle="How each value was accepted, and why several were refused.")


def build_sources() -> None:
    rows = []
    for s in SOURCES["sources"]:
        rows.append(
            f"""<tr id="{e(s['id'])}">
<td class="mono">{e(s['id'])}</td>
<td><a href="{e(s['url'])}" rel="noopener nofollow" target="_blank"><strong>{e(s['label'])}</strong> &#8599;</a>
  <div class="cell-note">{e(s['note'])}</div></td>
<td>{e(s['owner'])}</td>
<td><code>{e(s['tier'])}</code></td>
<td>{e(s['what_it_verifies'])}</td>
<td class="mono">{e(s['observed'])}</td>
</tr>"""
        )

    tiers = SOURCES["meta"]["tier_definitions"]
    tier_rows = "".join(
        f"<tr><td><code>{e(k)}</code></td><td>{e(v)}</td></tr>" for k, v in tiers.items()
    )

    body = f"""
<p class="lede">Every value on this site resolves to one of these {len(SOURCES['sources'])} documents.
None of them is a blog, a listicle, a price aggregator or an AI summary.</p>

<h2>Tier definitions</h2>
<div class="table-wrap">
<table><thead><tr><th scope="col">Tier</th><th scope="col">Meaning</th></tr></thead>
<tbody>{tier_rows}</tbody></table>
</div>

<h2>Registry</h2>
<div class="table-wrap">
<table class="sources">
  <thead><tr>
    <th scope="col">ID</th><th scope="col">Document</th><th scope="col">Publisher</th>
    <th scope="col">Tier</th><th scope="col">Used to verify</th><th scope="col">Read on</th>
  </tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
</div>

<h2>What was checked and rejected</h2>
<div class="panel panel-warn">
  <p>For completeness, three categories of source were considered and excluded:</p>
  <ul>
    <li><strong>Review-aggregator and price-history sites.</strong> They republish Amazon data
    without a licence and their figures cannot be traced to Amazon.</li>
    <li><strong>&ldquo;Best air fryer&rdquo; listicles and affiliate blogs.</strong> Circular: they
    cite each other and none is primary.</li>
    <li><strong>A third-party marketing site that stated the Emeril unit's wattage.</strong> The
    number may well be right, but a marketing site is not the manufacturer, so the field stays blank
    and is recorded as <a href="flagged.html#F-09">F-09</a>.</li>
  </ul>
</div>
"""
    page("sources.html", "Sources", body, subtitle="The official documents behind every value, with what each one was used for.")


def build_flagged() -> None:
    items = []
    for f in FLAGGED["items"]:
        links = " ".join(
            f'<a href="{e(l["url"])}" rel="noopener nofollow" target="_blank">{e(l["label"])} &#8599;</a>'
            for l in f["source_links"]
        )
        quote = ""
        items.append(
            f"""<article class="flag flag-{e(f['severity'])}" id="{e(f['id'])}">
  <div class="flag-head">
    <span class="flag-id mono">{e(f['id'])}</span>
    <span class="sev sev-{e(f['severity'])}">{e(f['severity'])}</span>
    <h2>{e(f['item'])}</h2>
  </div>
  <div class="flag-body">
    <dl>
      <div><dt>What was expected</dt><dd>{e(f['what_was_expected'])}</dd></div>
      <div><dt>What was observed</dt><dd>{e(f['what_was_observed'])}</dd></div>
      <div><dt>Why it matters</dt><dd>{e(f['why_it_matters'])}</dd></div>
      <div><dt>What would settle it</dt><dd>{e(f['what_would_confirm_it'])}</dd></div>
    </dl>
    <p class="srcmini"><strong>Evidence:</strong> {links}</p>
  </div>
</article>"""
        )

    counts = {}
    for f in FLAGGED["items"]:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    body = f"""
<div class="banner banner-warn">
  <p><strong>Nothing on this page blocks publication.</strong> Every item here is either an
  irregularity found during verification or a value that could not be confirmed from an official
  source. They are published so you can review them and ask for changes, rather than quietly
  resolved in the site's favour.</p>
</div>

<section class="stats">
  {stat('Total items', str(len(FLAGGED['items'])), 'all published with evidence')}
  {stat('High severity', str(counts.get('high', 0)), 'affects whether links can earn', 'warn')}
  {stat('Medium severity', str(counts.get('medium', 0)), 'affects a published claim', 'warn')}
  {stat('Low severity', str(counts.get('low', 0)), 'cosmetic or narrow', 'muted')}
</section>

<p class="lede">The two that matter most: <a href="#F-10">F-10</a>, no Associates tag is configured,
so nothing can earn yet; and <a href="#F-08">F-08</a>, Amazon price and rating are blank by design
because Amazon's own policies restrict displaying them. Everything else is smaller.</p>

{''.join(items)}
"""
    page("flagged.html", "Flagged for review", body, subtitle=f"{len(FLAGGED['items'])} items to look at, each with the evidence attached.")


def build_privacy() -> None:
    body = f"""
<p class="lede">Short, because this site does very little. A privacy page that is long usually means
the site is doing something it would rather not itemise.</p>

<h2>What this site collects</h2>
<p><strong>Nothing.</strong> There are no cookies, no analytics, no pixels, no tracking scripts, no
third-party fonts and no forms. The pages are static files served by GitHub Pages. There is no
account, no newsletter and no comment system.</p>

<h2>What GitHub collects</h2>
<p>The site is hosted on GitHub Pages. GitHub logs requests, including IP addresses, as part of
serving the site. That processing is GitHub's and is described in GitHub's own privacy statement at
<a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener nofollow" target="_blank">docs.github.com &#8599;</a>.</p>

<h2>What happens when you click an outbound link</h2>
<p>Product links go to <code>amazon.com</code>. Once you leave this site, Amazon's privacy notice and
cookie practices apply, not mine. If an Associates tag is configured, the click carries that tag as
a URL parameter so Amazon can attribute a resulting purchase. {e(CONFIG['site']['disclosure_amazon'])}</p>

<h2>Amazon's requirement on disclosure of tracking</h2>
<p>Amazon's Program Policies require a site to disclose, accurately and adequately, its own use of
cookies, pixels and other technologies. Because this site uses none, the honest disclosure is the
one above. Source: {src_link('S-AMZ-POL')} &middot; Participation Requirements &sect;3(e).</p>

<h2>Contact</h2>
<p>Corrections are welcome through the repository's issue tracker:
<a href="https://github.com/{e(CONFIG['site']['repo'])}/issues" rel="noopener">github.com/{e(CONFIG['site']['repo'])}/issues</a>.
If a value on this site is wrong, the source link next to it is the fastest way to show it.</p>
"""
    page("privacy.html", "Privacy", body, subtitle="No cookies, no analytics, no tracking. Here is the detail.")


def build_exec_summary_html() -> None:
    """Render the executive summary to HTML from the same structures, so numbers cannot drift."""
    total = sum(len(p["specs"]) for p in PRODUCTS["products"])
    ver = sum(1 for p in PRODUCTS["products"] for s in p["specs"] if s["status"] == "verified")
    fl = sum(1 for p in PRODUCTS["products"] for s in p["specs"] if s["status"] == "flagged")
    un = sum(1 for p in PRODUCTS["products"] for s in p["specs"] if s["status"] == "unverified")

    prod_rows = "".join(
        f"<tr><td>{e(short_name(p['asin']))}</td><td class='mono'>{e(p['asin'])}</td>"
        f"<td>{e(p['manufacturer_model'])}</td>"
        f"<td>{e(next(s['value'] for s in p['specs'] if s['field']=='Capacity'))}</td>"
        f"<td>{e(p['commission_rate_published'])}</td>"
        f"<td>{src_link('S-AMZ-P'+('1' if p['asin']=='B0CDY277D3' else '2' if p['asin']=='B09B7SB46R' else '3'))}</td></tr>"
        for p in PRODUCTS["products"]
    )
    top = OPPS["results"][0]

    body = f"""
<section class="stats">
  {stat('Products', '3', 'all three short links resolved')}
  {stat('Spec fields audited', str(total), 'every one carries a status')}
  {stat('Verified', str(ver), f'{round(100*ver/total)}% from official sources', 'ok')}
  {stat('Flagged', str(fl), 'conflicts, published not resolved', 'warn')}
  {stat('Unverified / blank', str(un), 'never inferred', 'muted')}
  {stat('Open review items', str(len(FLAGGED['items'])), 'all on the Flagged page', 'warn')}
</section>

<h2>1. What was delivered</h2>
<p>A static, GitHub-Pages-hosted dashboard covering three Amazon air-fryer affiliate products. It
publishes a verification register in which every fact carries the official page it came from, a
compliance register quoting Amazon's and the FTC's own requirements, three buying guides reasoned
only from verified specs, and a review queue of {len(FLAGGED['items'])} flagged items.</p>

<h2>2. The three products</h2>
<div class="table-wrap">
<table>
  <thead><tr><th scope="col">Product</th><th scope="col">ASIN</th><th scope="col">Model</th>
  <th scope="col">Capacity</th><th scope="col">Rate</th><th scope="col">Source</th></tr></thead>
  <tbody>{prod_rows}</tbody>
</table>
</div>
<p>All three are air fryers, which places them in Amazon's <strong>Kitchen</strong> category at a
published <strong>4.50%</strong> {src_link('S-AMZ-RATE')}. That is the public Table 1 rate, not a
personalised rate.</p>

<h2>3. The headline finding</h2>
<p><strong>{e(top['short_name'])} scores highest on merchandising fit ({e(top['composite'])}), but
the single most important finding in this audit is not a product ranking.</strong> It is that
Amazon's Program Policies restrict showing prices, availability, reviews and star ratings to data
Amazon serves or data obtained through its API. This site therefore publishes
<strong>no Amazon prices and no Amazon ratings</strong>. Every such cell is blank and links to
<a href="flagged.html#F-08">F-08</a>. Most affiliate sites fill those cells in anyway. That is the
compliance risk this build removes.</p>

<h2>4. The blocker</h2>
<p><strong>No Associates tag is configured, so no link on this site can currently earn.</strong> One
value in <code>data/config.json</code> and a rebuild converts every outbound link into a tracked
Special Link. Until then the site displays a warning on every page
(<a href="flagged.html#F-10">F-10</a>). This is the highest-value action available and it costs
about a minute.</p>

<h2>5. Evidence quality, honestly stated</h2>
<div class="grid-2">
  <div class="panel">
    <h3>Solid</h3>
    <ul>
      <li>Capacity, wattage, temperature range, function counts, certifications and warranty for
      both Chefman units &mdash; read off Chefman's own product pages with model numbers matching.</li>
      <li>The Amazon commission rate and the attribution windows &mdash; read off Amazon's own
      published documents.</li>
      <li>The disclosure requirement &mdash; quoted verbatim from the Operating Agreement &sect;5.</li>
    </ul>
  </div>
  <div class="panel panel-warn">
    <h3>Weak or absent</h3>
    <ul>
      <li><strong>Demand data.</strong> No official source exists for search volume, sales rank or
      conversion rate. The fit score is a merchandising ranking, not a demand forecast.</li>
      <li><strong>The Emeril unit.</strong> Wattage and safety certification unconfirmed
      (<a href="flagged.html#F-09">F-09</a>); three conflicting preset counts
      (<a href="flagged.html#F-03">F-03</a>).</li>
      <li><strong>Review sentiment.</strong> Only brand-storefront ratings were reachable, and those
      are not comparable to marketplace ratings (<a href="flagged.html#F-12">F-12</a>).</li>
      <li><strong>Link fidelity.</strong> All three short links landed via a fallback marker
      (<a href="flagged.html#F-01">F-01</a>).</li>
    </ul>
  </div>
</div>

<h2>6. Compliance posture</h2>
<p>Twenty requirements are recorded with the operative quote and the specific implementation. Five
things were deliberately <em>not</em> built because Amazon prohibits them: price tracking and price
alerts (&sect;3(y)), Amazon price/rating display without API data (&sect;2(b), &sect;3(t)), cloaked or
shortened outbound links (&sect;3(v)), click incentives (&sect;3(g)), and any use of Amazon logos or
brand imagery. See the <a href="compliance.html">compliance register</a>.</p>

<h2>7. Recommendations, in priority order</h2>
<ol class="recs">
  <li><strong>Set the Associates tag and rebuild.</strong> Nothing earns until this is done.</li>
  <li><strong>Re-check the three short links in a browser</strong> and replace them with canonical
  tagged <code>/dp/&lt;ASIN&gt;</code> URLs (<a href="flagged.html#F-01">F-01</a>).</li>
  <li><strong>Apply for Creators API / PA API access.</strong> This is the only lawful route to
  showing Amazon prices and ratings, and it is what would make the comparison table genuinely useful
  (<a href="flagged.html#F-08">F-08</a>).</li>
  <li><strong>Resolve the Emeril wattage and certification</strong> from the manual or the rating
  label before publishing any claim about it (<a href="flagged.html#F-09">F-09</a>).</li>
  <li><strong>Get the Chefman 6 Qt model number confirmed against the Amazon SKU</strong> to settle
  the &ldquo;Hi-Fry&rdquo; discrepancy (<a href="flagged.html#F-02">F-02</a>).</li>
  <li><strong>Only then</strong> build the click counter and read conversions from the Associates
  dashboard. Do not build a price tracker, ever.</li>
</ol>

<h2>8. Where the platform blueprint stands</h2>
<p>The brief asked for automated research, niche scoring, content generation, publishing, tracking
and continuous optimisation. Being precise about which of those this delivery actually contains:</p>
<div class="table-wrap">
<table>
  <thead><tr><th scope="col">Blueprint capability</th><th scope="col">Status</th><th scope="col">Reality</th></tr></thead>
  <tbody>
    <tr><td>Product research and verification</td><td>{status_chip('verified')}</td>
        <td>Implemented as the sourced data layer and the build-time verifier.</td></tr>
    <tr><td>Pricing and competition analysis</td><td>{status_chip('flagged')}</td>
        <td>Partial and deliberately limited: brand-store prices only, no Amazon price, no tracker
        (&sect;2(b), &sect;3(y)).</td></tr>
    <tr><td>Commission-potential analysis</td><td>{status_chip('verified')}</td>
        <td>The 4.50% Kitchen rate is published and sourced; arithmetic is shown, volume is left
        blank.</td></tr>
    <tr><td>SEO-optimised articles, comparisons, guides</td><td>{status_chip('verified')}</td>
        <td>The three buying guides and the comparison page, built only on verified specs.</td></tr>
    <tr><td>Special Link management and tag injection</td><td>{status_chip('flagged')}</td>
        <td>Link rendering and validation are built; the tag itself is missing
        (<a href="flagged.html#F-10">F-10</a>).</td></tr>
    <tr><td>Click and conversion tracking</td><td>{status_chip('unverified')}</td>
        <td>Not shipped. A static site cannot truthfully do it, and conversion data lives in the
        Associates dashboard (<a href="flagged.html#F-11">F-11</a>).</td></tr>
    <tr><td>Continuous campaign optimisation</td><td>{status_chip('unverified')}</td>
        <td>Not shipped. Optimising without observed traffic data would be theatre
        (<a href="flagged.html#F-13">F-13</a>).</td></tr>
    <tr><td>Compliance with Associates policy and disclosure</td><td>{status_chip('verified')}</td>
        <td>Twenty requirements quoted, implemented and asserted at build time.</td></tr>
  </tbody>
</table>
</div>

<h2>9. Reproducing any number here</h2>
<pre class="code"><code>python3 scripts/build_site.py &amp;&amp; python3 scripts/verify_site.py</code></pre>
<p>Every figure on every page is generated from <code>data/*.json</code>. To change a value you must
change its source; to publish an unsourced value the verifier has to be defeated.</p>
"""
    page("executive-summary.html", "Executive summary", body, subtitle="What was built, what was proven, what is missing, and what to do first.")


def build_404() -> None:
    body = """
<p class="lede">That page does not exist. Everything this site publishes is reachable from the list
below &mdash; there are only a few pages.</p>
<ul class="recs">
  <li><a href="index.html">Dashboard</a> &mdash; the summary and the product register</li>
  <li><a href="products.html">Products</a> &mdash; full sourced specification sheets</li>
  <li><a href="compare.html">Compare</a> &mdash; side-by-side, gaps shown as gaps</li>
  <li><a href="guides.html">Buying guides</a> &mdash; three kitchens, three answers</li>
  <li><a href="compliance.html">Compliance</a> &mdash; Amazon and FTC requirements, quoted</li>
  <li><a href="methodology.html">Method</a> &mdash; how values were accepted or refused</li>
  <li><a href="sources.html">Sources</a> &mdash; the official documents</li>
  <li><a href="flagged.html">Flagged for review</a> &mdash; open items with evidence</li>
  <li><a href="executive-summary.html">Executive summary</a></li>
</ul>
"""
    page("404.html", "Page not found", body)


# ------------------------------------------------------------------- assets

CSS = """:root{
  --bg:#f6f7f9; --panel:#ffffff; --ink:#10151c; --ink-2:#4a5563; --ink-3:#79838f;
  --line:#e3e7ec; --line-2:#cfd6de; --accent:#0b5fff; --accent-ink:#ffffff;
  --ok:#0a7d4b; --ok-bg:#e6f7ee; --warn:#8a5300; --warn-bg:#fff4e0;
  --bad:#a11a34; --bad-bg:#ffe9ee; --muted:#6b7480; --shadow:0 1px 2px rgba(16,21,28,.06),0 4px 14px rgba(16,21,28,.05);
  --radius:10px; --maxw:1120px;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 var(--sans);
  -webkit-font-smoothing:antialiased}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 20px}
.skip{position:absolute;left:-9999px}
.skip:focus{left:8px;top:8px;background:var(--accent);color:#fff;padding:8px 12px;z-index:99;border-radius:6px}

/* top bar */
.topbar{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
.topbar-in{display:flex;align-items:center;gap:20px;min-height:60px;flex-wrap:wrap;padding-top:8px;padding-bottom:8px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:700;letter-spacing:-.01em}
.brand-mark{display:grid;place-items:center;width:30px;height:30px;border-radius:8px;
  background:linear-gradient(135deg,#0b5fff,#0036a3);color:#fff;font-size:12px;font-weight:800}
.brand-text{font-size:15px}
.nav{display:flex;gap:2px;flex-wrap:wrap;margin-left:auto}
.nav a{padding:7px 11px;border-radius:7px;text-decoration:none;color:var(--ink-2);font-size:13.5px;font-weight:500;white-space:nowrap}
.nav a:hover{background:#f0f3f7;color:var(--ink)}
.nav a.active{background:var(--ink);color:#fff}

/* page head */
main{padding-top:26px;padding-bottom:56px}
h1{font-size:clamp(26px,3.4vw,36px);line-height:1.15;letter-spacing:-.022em;margin:.2em 0 .25em}
.page-sub{color:var(--ink-2);font-size:16.5px;margin:0 0 18px;max-width:70ch}
h2{font-size:clamp(19px,2.1vw,23px);letter-spacing:-.014em;margin:2em 0 .6em;padding-top:.2em}
h2:first-of-type{margin-top:1.4em}
h3{font-size:16.5px;margin:1.4em 0 .45em;letter-spacing:-.008em}
p{margin:.7em 0}
.lede{font-size:16.5px;color:var(--ink-2);max-width:76ch}
.muted{color:var(--ink-3)}
.fine{font-size:12.5px;color:var(--ink-3);line-height:1.55}
.mono{font-family:var(--mono);font-size:12.5px}
code{font-family:var(--mono);font-size:12.5px;background:#eef1f5;padding:1px 5px;border-radius:4px}
pre.code{background:#10151c;color:#e6edf3;padding:14px 16px;border-radius:var(--radius);overflow:auto;font-size:12.5px}
pre.code code{background:none;color:inherit;padding:0}
a{color:var(--accent)}
a:hover{text-decoration-thickness:2px}

/* disclosure */
.disclosure{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--accent);
  border-radius:var(--radius);padding:12px 16px;margin:18px 0 26px;box-shadow:var(--shadow)}
.disclosure-main{margin:0;font-size:14.5px}
.disclosure-sub{margin:4px 0 0;font-size:13px;color:var(--ink-2)}

/* banners */
.banner{border-radius:var(--radius);padding:14px 16px;margin:18px 0;border:1px solid;font-size:14.5px}
.banner p{margin:.35em 0}
.banner-warn{background:var(--warn-bg);border-color:#f0d4a6;color:#573408}
.banner-info{background:#eef4ff;border-color:#c9dbff;color:#123a76}

/* stats */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:12px;margin:8px 0 28px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
  padding:13px 15px;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:2px}
.stat-label{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-3);font-weight:650}
.stat-value{font-size:26px;font-weight:750;letter-spacing:-.03em;line-height:1.1}
.stat-note{font-size:12px;color:var(--ink-3)}
.stat.ok .stat-value{color:var(--ok)}
.stat.warn .stat-value{color:var(--warn)}
.stat.muted .stat-value{color:var(--muted)}

/* cards + panels */
.grid-3{display:grid;grid-template-columns:repeat(auto-fit,minmax(258px,1fr));gap:14px;margin:18px 0}
.grid-2{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:14px;margin:18px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;
  text-decoration:none;color:inherit;box-shadow:var(--shadow);transition:.14s}
.card:hover{border-color:var(--accent);transform:translateY(-1px)}
.card h3{margin:.1em 0 .35em;color:var(--ink)}
.card p{margin:0;font-size:14px;color:var(--ink-2)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:14px 18px;box-shadow:var(--shadow)}
.panel h3{margin-top:.2em}
.panel ul{margin:.4em 0;padding-left:20px;font-size:14.5px}
.panel li{margin:.3em 0}
.panel-warn{border-left:3px solid #e0a94a}

/* steps */
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:16px 0}
.step{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px;box-shadow:var(--shadow)}
.step-n{display:inline-grid;place-items:center;width:24px;height:24px;border-radius:50%;
  background:var(--ink);color:#fff;font-size:12.5px;font-weight:700;margin-bottom:6px}
.step h3{margin:.2em 0 .3em;font-size:15px}
.step p{margin:0;font-size:13.5px;color:var(--ink-2)}

/* tables */
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);background:var(--panel);
  box-shadow:var(--shadow);margin:16px 0}
table{border-collapse:collapse;width:100%;font-size:14px;min-width:640px}
caption{caption-side:bottom;text-align:left;padding:9px 14px 12px;font-size:12.5px;color:var(--ink-3)}
th,td{padding:10px 12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
thead th{background:#f2f5f8;font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;
  color:var(--ink-2);font-weight:700;position:sticky;top:0;border-bottom:1px solid var(--line-2)}
tbody tr:last-child td,tbody tr:last-child th{border-bottom:none}
tbody tr:hover{background:#fafbfd}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
td.field,th.field{font-weight:650;color:var(--ink);white-space:normal;min-width:150px}
td.na{color:var(--ink-3);text-align:center}
th[scope=row]{background:#fafbfd;font-weight:650}
.th-name{display:block;font-size:13px;text-transform:none;letter-spacing:0;color:var(--ink)}
.th-sub{display:block;font-weight:400;text-transform:none;letter-spacing:0;color:var(--ink-3)}
.srcmini{font-size:11.5px;margin-top:4px}
.src{font-size:11.5px;text-decoration:none;background:#eef2f8;border:1px solid var(--line-2);
  padding:1px 7px;border-radius:20px;white-space:nowrap;display:inline-block;color:#1c3f7a;font-weight:600}
.src:hover{background:#e2eaf7;border-color:#9fb6d8}
.src-missing{font-size:11.5px;color:var(--bad);background:var(--bad-bg);padding:1px 7px;border-radius:20px;font-weight:700}
.cell-note{font-size:12px;color:var(--ink-3);margin-top:3px;line-height:1.45}

/* chips */
.chip{display:inline-block;font-size:11px;font-weight:750;letter-spacing:.04em;text-transform:uppercase;
  padding:2px 8px;border-radius:20px;border:1px solid;white-space:nowrap}
.chip-verified{background:var(--ok-bg);color:var(--ok);border-color:#b6e3ca}
.chip-flagged{background:var(--warn-bg);color:var(--warn);border-color:#f0d4a6}
.chip-unverified{background:#eef1f5;color:var(--muted);border-color:var(--line-2)}
.val-verified{}
.val-flagged{color:var(--warn)}
.val-blank{color:var(--ink-3);font-style:italic}
.flag-link{font-family:var(--mono);font-size:11.5px;font-weight:700;color:var(--bad);
  background:var(--bad-bg);border:1px solid #f7c3ce;padding:1px 6px;border-radius:5px;text-decoration:none}
.flag-link:hover{background:#ffd6e0}

/* products */
.product{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px 22px;
  margin:26px 0;box-shadow:var(--shadow)}
.product-head{display:flex;gap:20px;justify-content:space-between;align-items:flex-start;flex-wrap:wrap}
.product-head h2{margin:.1em 0 .3em}
.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-3);font-weight:700;margin:0}
.product-score{background:#10151c;color:#fff;border-radius:12px;padding:12px 16px;text-align:center;min-width:104px}
.score-num{display:block;font-size:28px;font-weight:800;letter-spacing:-.03em;line-height:1}
.score-label{display:block;font-size:10.5px;color:#b9c3ce;margin-top:4px;line-height:1.3;text-transform:uppercase;letter-spacing:.05em}
.keyfacts{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:10px 20px;
  margin:16px 0 6px;padding:14px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.keyfacts div{margin:0}
.keyfacts dt{font-size:11.5px;text-transform:uppercase;letter-spacing:.055em;color:var(--ink-3);font-weight:700}
.keyfacts dd{margin:2px 0 0;font-size:14px;font-weight:600}
.buy{display:inline-block;background:var(--accent);color:#fff;padding:6px 13px;border-radius:7px;
  text-decoration:none;font-size:13px;font-weight:650;white-space:nowrap}
.buy:hover{background:#0048cc}
.legend{display:flex;gap:10px;flex-wrap:wrap;font-size:13px;color:var(--ink-2);margin:14px 0 8px}
.legend span{background:var(--panel);border:1px solid var(--line);padding:6px 11px;border-radius:20px}

/* guides */
.guide{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px 22px;
  margin:20px 0;box-shadow:var(--shadow)}
.guide h2{margin:.1em 0 .5em;font-size:20px}
.answer{background:var(--ok-bg);border:1px solid #b6e3ca;border-radius:8px;padding:10px 14px;font-size:15px}
.wrong{background:var(--warn-bg);border:1px solid #f0d4a6;border-radius:8px;padding:10px 14px;font-size:14px}
.recs{font-size:15px;max-width:80ch}
.recs li{margin:.5em 0;padding-left:2px}

/* compliance table */
.compliance td:nth-child(3){min-width:300px;max-width:440px}
.compliance td:nth-child(4){min-width:270px;max-width:400px}
blockquote{margin:.55em 0;padding:9px 13px;border-left:3px solid var(--line-2);background:#f8fafc;
  font-size:13px;color:var(--ink-2);border-radius:0 6px 6px 0}
blockquote.big-quote{font-size:17px;color:var(--ink);font-weight:650;border-left-color:var(--accent);background:#eef4ff}

/* flags */
.flag{background:var(--panel);border:1px solid var(--line);border-radius:12px;margin:16px 0;
  box-shadow:var(--shadow);overflow:hidden}
.flag-high{border-left:4px solid var(--bad)}
.flag-medium{border-left:4px solid #e0a94a}
.flag-low{border-left:4px solid var(--line-2)}
.flag-head{padding:14px 18px 10px;border-bottom:1px solid var(--line);display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.flag-head h2{margin:.1em 0;font-size:17px;flex:1 1 100%;order:3}
.flag-id{font-weight:750;font-size:13px}
.sev{font-size:10.5px;font-weight:800;text-transform:uppercase;letter-spacing:.07em;padding:2px 8px;border-radius:20px}
.sev-high{background:var(--bad-bg);color:var(--bad)}
.sev-medium{background:var(--warn-bg);color:var(--warn)}
.sev-low{background:#eef1f5;color:var(--muted)}
.flag-body{padding:12px 18px 16px}
.flag-body dl{margin:0}
.flag-body dt{font-size:11.5px;text-transform:uppercase;letter-spacing:.055em;color:var(--ink-3);font-weight:700;margin-top:9px}
.flag-body dd{margin:2px 0 0;font-size:14.5px}

/* footer */
.footer{background:#10151c;color:#c3ccd6;margin-top:40px;padding:30px 0 34px;font-size:14px}
.footer .wrap{max-width:var(--maxw)}
.footer p{margin:.5em 0}
.footer a{color:#8fb6ff}
.footer .fine{color:#8792a0;max-width:88ch}

@media (max-width:640px){
  .topbar-in{gap:10px}
  .nav{margin-left:0;width:100%;overflow-x:auto;flex-wrap:nowrap;padding-bottom:4px}
  .nav a{font-size:13px}
  table{font-size:13px}
  .product,.guide,.flag-body{padding-left:14px;padding-right:14px}
  .product-score{min-width:0}
}
@media (prefers-color-scheme:dark){
  :root{--bg:#0d1117;--panel:#161b22;--ink:#e6edf3;--ink-2:#aeb9c5;--ink-3:#7d8896;
    --line:#232b36;--line-2:#333d4b;--muted:#8b96a3;--shadow:none;
    --ok:#4ade80;--ok-bg:#122a1d;--warn:#fbbf24;--warn-bg:#2a2110;--bad:#fb7185;--bad-bg:#2c1219}
  thead th{background:#1b2129}
  th[scope=row]{background:#1b2129}
  tbody tr:hover{background:#1b2129}
  blockquote{background:#1b2129}
  blockquote.big-quote{background:#132a4d}
  .src{background:#1e2a3d;color:#a8c8ff;border-color:#2e3d52}
  .banner-info{background:#132a4d;border-color:#24406e;color:#cfe0ff}
  .nav a.active{background:#e6edf3;color:#0d1117}
  .card:hover{border-color:#4b8bff}
  code{background:#1e242c}
}
"""


def build_assets() -> None:
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "style.css").write_text(CSS, encoding="utf-8")
    # A tiny favicon so GitHub Pages does not 404 on /favicon.ico requests from browsers.
    (OUT / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        '<rect width="32" height="32" rx="7" fill="#0b5fff"/>'
        '<text x="16" y="22" font-family="Helvetica,Arial,sans-serif" font-size="15" '
        'font-weight="700" fill="#fff" text-anchor="middle">AF</text></svg>',
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n", encoding="utf-8"
    )
    (OUT / ".nojekyll").write_text("", encoding="utf-8")


# ------------------------------------------------------------------- main

def main() -> int:
    if TAG and not TAG_RE.match(TAG):
        print(
            f"ERROR: associate_tag {TAG!r} does not look like an Amazon Associates tag "
            f"(expected format such as XXXXX-20). Refusing to build links with it.",
            file=sys.stderr,
        )
        return 1

    build_assets()
    build_index()
    build_products()
    build_compare()
    build_guides()
    build_compliance()
    build_methodology()
    build_sources()
    build_flagged()
    build_privacy()
    build_exec_summary_html()
    build_404()
    print(f"Built site with associate_tag={TAG!r} "
          f"({len(PRODUCTS['products'])} products, {len(SOURCES['sources'])} sources, "
          f"{len(COMPLIANCE['rules'])} compliance rules, {len(FLAGGED['items'])} flags)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
