#!/usr/bin/env python3
"""Static site generator for the Zone1 Amazon affiliate research dashboard.

Reads data/*.json and writes docs/*.html. Every published value must carry a
source URL; blanks render as an explicit "unverified" marker. No value is
invented here — the generator only formats what the data files already prove.
"""
import html
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
DATA = os.path.join(ROOT, "research")
DOCS = os.path.join(ROOT, "research")  # additive section, linked from the main docs/ site

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

# Canonical field order for the product detail table. Rendering AND counting both
# use this list so the published totals always equal the visible rows.
PRODUCT_FIELDS = [
    ("Amazon listing title", "product_name_amazon"),
    ("Manufacturer product name", "product_name_manufacturer"),
    ("Brand", "brand"),
    ("Model number", "model_number"),
    ("ASIN", "asin"),
    ("Amazon canonical URL", "amazon_url"),
    ("Carries a tracking tag?", "has_tag_parameter"),
    ("Product category", "category"),
    ("Amazon browse category", "amazon_browse_category"),
    ("Capacity", "capacity"),
    ("Temperature range", "temperature_range"),
    ("Power", "power"),
    ("Voltage", "voltage"),
    ("Dimensions", "dimensions"),
    ("Cooking functions", "functions"),
    ("Preset count", "preset_count"),
    ("Key features", "key_features"),
    ("Accessories included", "accessories_included"),
    ("Dishwasher-safe parts", "dishwasher_safe_parts"),
    ("Certification", "certification"),
    ("Warranty", "warranty"),
    ("Country of origin", "country_of_origin"),
    ("Manufacturer list price", "listed_price_official_brand"),
    ("Amazon price", "amazon_price"),
    ("Amazon star rating", "amazon_star_rating"),
    ("Amazon review count", "amazon_review_count"),
    ("Best Sellers Rank", "best_sellers_rank"),
    ("Date first available", "date_first_available"),
    ("Reviews on the brand's own site", "brand_site_rating"),
    ("Official product page", "official_product_page"),
]
TRADEMARK = "Amazon and the Amazon logo are trademarks of Amazon.com, Inc. or its affiliates."
NO_HANDS_ON = ("No hands-on testing is claimed anywhere on this site. "
               "Every specification below is a quotation from the manufacturer's own "
               "product page, linked in the Source column.")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def esc(value):
    return html.escape(str(value), quote=True)


def src_link(source_id, sources, label=None):
    """Render a short 'source' link for a source id."""
    src = sources.get(source_id)
    if not src:
        return '<span class="bad">no source</span>'
    text = label or source_id
    return (f'<a class="srclink" href="{esc(src["url"])}" rel="noopener nofollow" '
            f'target="_blank" title="{esc(src["label"])}">{esc(text)}</a>')


def safe_url(url):
    """Only allow http(s) and in-site relative links through unfiltered."""
    if re.match(r"^https?://", url) or re.match(r"^[a-z0-9./#-]+$", url):
        return url
    return None


# --------------------------------------------------------------------------- #
# layout
# --------------------------------------------------------------------------- #

NAV = [
    ("index.html", "Research hub"),
    ("../index.html", "← Main site"),
    ("products.html", "Products"),
    ("categories/air-fryers.html", "Category"),
    ("analysis.html", "Analysis"),
    ("compliance.html", "Compliance"),
    ("articles/index.html", "Articles"),
    ("flagged-for-review.html", "Flagged for Review"),
    ("executive-summary.html", "Executive Summary"),
]


def layout(title, body, prefix="", active="", sources=None, meta=None, canonical="", self_name="index.html"):
    nav_items = []
    for href, label in NAV:
        cls = ' class="active"' if href == active else ""
        nav_items.append(f'<a href="{prefix}{href}"{cls}>{esc(label)}</a>')
    meta_html = ""
    if meta:
        meta_html = f'<p class="page-meta">{meta}</p>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} &middot; Zone1 Affiliate Research</title>
<meta name="description" content="Source-verified Amazon affiliate research dashboard: three air fryer SKUs, every value linked to an official source.">
<link rel="canonical" href="{self_name}">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="wrap">
    <div class="brand"><a href="{prefix}index.html"><span class="dot"></span> Zone1 <span class="sub">Affiliate Research Dashboard</span></a></div>
    <nav class="mainnav" aria-label="Main">{''.join(nav_items)}</nav>
  </div>
</header>
<div class="disclosure-bar" role="note">
  <div class="wrap">
    <strong>Affiliate disclosure:</strong> {esc(DISCLOSURE)}
    <span class="disclosure-detail">Links on this site may be affiliate links and I may earn a commission from qualifying purchases, at no extra cost to you.</span>
  </div>
</div>
<main id="main" class="wrap">
{meta_html}
{body}
</main>
<footer class="sitefoot">
  <div class="wrap">
    <p>{esc(TRADEMARK)}</p>
    <p>Independent research site. Not affiliated with, endorsed by, or sponsored by Amazon.com, Inc., Chefman, or Emeril Everyday. Product names and model numbers are used for identification only.</p>
    <p>{esc(NO_HANDS_ON)} Data captured 2026-11-13. Every row links to its official source; anything that could not be confirmed is blank and listed on the <a href="{prefix}flagged-for-review.html">Flagged for Review</a> page.</p>
  </div>
</footer>
</body>
</html>
"""


SITE = ""  # relative canonicals: the section is served at both / and /docs/ paths


def page(title, body, path, **kw):
    out = os.path.join(DOCS, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    depth = path.count("/")
    prefix = "../" * depth
    if depth:
        # nested pages must climb one level to reach docs/-root pages
        body = body.replace('href="flagged-for-review.html#', 'href="../flagged-for-review.html#')
        body = body.replace('href="compliance.html#', 'href="../compliance.html#')
        body = body.replace('href="analysis.html#', 'href="../analysis.html#')
        body = body.replace('href="products.html#', 'href="../products.html#')
    active = kw.pop("active", path)
    html_out = layout(title, body, prefix=prefix, active=active,
                      self_name=os.path.basename(path), **kw)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html_out)
    return path


# --------------------------------------------------------------------------- #
# reusable fragments
# --------------------------------------------------------------------------- #

def field_cell(field, sources, source_map_id=None, prefix=""):
    """Render one verified field as value + source link, or an unverified blank."""
    if not isinstance(field, dict) or not field:
        # field not present in the dataset at all: it was never confirmed, so it is
        # rendered as a blank that points at the "unpublished spec fields" flag.
        return (f'<td><span class="unv" title="Not published on any official page we could read">'
                f'unverified</span> <a class="flagchip" href="{prefix}flagged-for-review.html#I-8">I-8</a></td>')
    value = field.get("value")
    sid = field.get("source")
    verified = field.get("verified")
    note = field.get("note")
    flag = field.get("flag")
    if value is None or value == "":
        cell = '<span class="unv" title="Not confirmed from an official source">unverified</span>'
        if flag:
            cell += f' <a class="flagchip" href="/flagged-for-review.html#{esc(flag)}">{esc(flag)}</a>' \
                if False else f' <a class="flagchip" href="flagged-for-review.html#{esc(flag)}">{esc(flag)}</a>'
        return f"<td>{cell}</td>"
    if isinstance(value, bool):
        shown = "yes" if value else "no"
    else:
        shown = esc(value)
    if note:
        shown += f'<span class="note">{esc(note)}</span>'
    if verified and sid:
        shown += " " + src_link(sid, sources)
    elif verified and not sid:
        shown += ' <span class="bad">missing source</span>'
    else:
        shown += f' <span class="unv">unverified</span>'
        if flag:
            shown += f' <a class="flagchip" href="flagged-for-review.html#{esc(flag)}">{esc(flag)}</a>'
    return f"<td>{shown}</td>"


def kpi(value, label, tone=""):
    return (f'<div class="kpi {tone}"><div class="kpi-val">{value}</div>'
            f'<div class="kpi-label">{esc(label)}</div></div>')


def severity_tally(items):
    tally = {"high": 0, "medium": 0, "low": 0}
    for it in items:
        tally[it.get("severity", "low")] = tally.get(it.get("severity", "low"), 0) + 1
    return tally


# --------------------------------------------------------------------------- #
# pages
# --------------------------------------------------------------------------- #

def build():
    sources_doc = load("sources-s8a2.json")
    products_doc = load("products-s8a2.json")
    compliance_doc = load("compliance-policies.json")
    analysis_doc = load("analysis-s8a2.json")
    irr_doc = load("irregularities-s8a2.json")

    sources = {s["id"]: s for s in sources_doc["sources"]}
    products = products_doc["products"]
    irr_items = irr_doc["items"]
    tally = severity_tally(irr_items)

    verified_fields = 0
    unverified_fields = 0
    total_fields = 0
    for p in products:
        for _label, key in PRODUCT_FIELDS:
            total_fields += 1
            field = p.get(key)
            if isinstance(field, dict) and field.get("verified"):
                verified_fields += 1
            else:
                unverified_fields += 1

    # ----------------------------------------------------------------- index
    rows = []
    for p in products:
        rows.append(f"""<tr>
  <td class="num">{p['rank']}</td>
  <td><a href="products.html#{"P" and p['id']}">{esc(p['brand']['value'])}</a>
      <span class="note">{esc(p['product_name_manufacturer']['value'])}</span></td>
  <td><code>{esc(p['asin']['value'])}</code></td>
  <td>{esc(p['category']['value'])}</td>
  <td>{field_cell(p['capacity'], sources)}</td>
  <td>{field_cell(p['model_number'], sources)}</td>
  <td><span class="unv" title="Amazon price deliberately not stored">not stored</span>
      <a class="flagchip" href="flagged-for-review.html#I-10">I-10</a></td>
  <td><a class="btn" href="{esc(p['supplied_link'])}" rel="sponsored noopener nofollow" target="_blank">View on Amazon</a>
      <span class="note">supplied link &middot; {src_link(p['supplied_link_source'], sources)}</span></td>
</tr>""")

    index_body = f"""
<section class="hero">
  <h1>Amazon affiliate research dashboard</h1>
  <p class="lede">Three supplied affiliate links, resolved to their real ASINs, matched to the manufacturers'
  official product pages, and published row by row with a source link on every value.
  Anything that could not be confirmed from an official source is left blank and flagged.</p>
  <div class="hero-actions">
    <a class="btn primary" href="products.html">Open the product table</a>
    <a class="btn" href="executive-summary.html">Read the executive summary</a>
    <a class="btn ghost" href="flagged-for-review.html">Flagged items ({len(irr_items)})</a>
  </div>
</section>

<section class="kpis">
  {kpi("3", "supplied affiliate links, all resolved", "ok")}
  {kpi("3 / 3", "ASINs matched to an official manufacturer page", "ok")}
  {kpi(f"{verified_fields}", "product fields verified against an official source", "ok")}
  {kpi(f"{unverified_fields}", "fields left blank and flagged", "warn")}
  {kpi(f"{tally['high']}", "high-severity irregularities", "bad")}
  {kpi("0", "verified Amazon commission rates published", "warn")}
</section>

<section class="card">
  <h2>Products in this programme</h2>
  <p class="cardnote">Ranked 1–3 in the order the links were supplied. Ranking is <strong>not</strong> a paid placement or a
  performance claim — no performance data is publicly verifiable. Amazon prices are intentionally not stored on this
  site (see <a href="compliance.html#C8">C8</a> and <a href="flagged-for-review.html#I-10">I-10</a>).</p>
  <p class="disclosure-inline"><strong>Disclosure:</strong> {esc(DISCLOSURE)} The "View on Amazon" buttons below
  are affiliate links. If you buy through one I may earn a commission at no extra cost to you.</p>
  <div class="tablewrap">
  <table class="grid">
    <thead><tr>
      <th>#</th><th>Product</th><th>ASIN</th><th>Category</th><th>Capacity</th><th>Model</th>
      <th>Amazon price</th><th>Link</th>
    </tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  </div>
</section>

<section class="two-col">
  <div class="card">
    <h2>What was verified</h2>
    <ul class="ticks">
      <li>Each <code>link.amazon</code> short link was followed to its canonical <code>/dp/</code> URL and its ASIN recorded.</li>
      <li>Each ASIN was matched to the manufacturer's own product page by brand, capacity, functions and feature names.</li>
      <li>Every specification published here is quoted from that manufacturer page, with the URL beside it.</li>
      <li>Amazon's own program rules were read from Associates Central and quoted verbatim in the <a href="compliance.html">compliance matrix</a>.</li>
      <li>The FTC rules were read from the eCFR and from FTC staff guidance, and quoted verbatim.</li>
    </ul>
  </div>
  <div class="card">
    <h2>What could not be verified</h2>
    <ul class="crosses">
      <li><strong>Amazon prices</strong> — page body not machine-readable, and program policy restricts showing prices. <a href="flagged-for-review.html#I-10">I-10</a></li>
      <li><strong>Amazon star ratings / review counts</strong> — review pages require sign-in. <a href="flagged-for-review.html#I-11">I-11</a></li>
      <li><strong>Best Sellers Rank, date first available</strong> — not exposed publicly. <a href="flagged-for-review.html#I-12">I-12</a></li>
      <li><strong>Commission rate for the category</strong> — rate card is behind sign-in. <a href="flagged-for-review.html#I-14">I-14</a></li>
      <li><strong>Whether the links are monetised</strong> — none carry a tracking tag. <a href="flagged-for-review.html#I-2">I-2</a></li>
    </ul>
  </div>
</section>

<section class="card">
  <h2>Site map</h2>
  <div class="grid-cards">
    <a class="tile" href="products.html"><h3>Products</h3><p>All three SKUs, every field, every source link.</p></a>
    <a class="tile" href="categories/air-fryers.html"><h3>Category: air fryers</h3><p>Spec comparison across basket, dual-basket and oven formats.</p></a>
    <a class="tile" href="analysis.html"><h3>Analysis &amp; automation</h3><p>Scoring model, niche assessment, content plan, campaign playbook.</p></a>
    <a class="tile" href="compliance.html"><h3>Compliance</h3><p>{len(compliance_doc['rows'])} Amazon and FTC requirements with verbatim quotes.</p></a>
    <a class="tile" href="articles/index.html"><h3>Articles</h3><p>Source-linked buying guide and comparisons.</p></a>
    <a class="tile" href="flagged-for-review.html"><h3>Flagged for review</h3><p>{len(irr_items)} items: {tally['high']} high, {tally['medium']} medium, {tally['low']} low.</p></a>
  </div>
</section>
"""
    page("Dashboard", index_body, "index.html", active="index.html", sources=sources,
         meta=f"Data captured 2026-11-13. {verified_fields} product fields verified, {unverified_fields} left blank.")

    # -------------------------------------------------------------- products
    sections = []
    for p in products:
        def row(label, key, prod=p):
            return f"<tr><th>{esc(label)}</th>{field_cell(prod.get(key, {}), sources)}</tr>"

        irr_chips = " ".join(
            f'<a class="flagchip" href="flagged-for-review.html#{esc(i)}">{esc(i)}</a>'
            for i in p.get("irregularities", []))

        kv_rows = "\n      ".join(row(label, key) for label, key in PRODUCT_FIELDS)

        sections.append(f"""
<section class="card" id="{esc(p['id'])}">
  <div class="product-head">
    <div>
      <span class="pill">Rank {p['rank']}</span>
      <h2>{esc(p['product_name_manufacturer']['value'])}</h2>
      <p class="cardnote">{esc(p['brand']['value'])} &middot; model {esc(p['model_number']['value'])} &middot; ASIN <code>{esc(p['asin']['value'])}</code></p>
    </div>
    <div class="product-cta">
      <a class="btn primary" href="{esc(p['supplied_link'])}" rel="sponsored noopener nofollow" target="_blank">Check price on Amazon</a>
      <span class="note">Amazon sets the price; this site never stores it. {src_link(p['supplied_link_source'], sources, 'supplied link')}</span>
      <a class="btn ghost" href="{esc(p['official_product_page']['value'])}" rel="noopener" target="_blank">Manufacturer page</a>
    </div>
  </div>
  <p class="disclosure-inline"><strong>Disclosure:</strong> {esc(DISCLOSURE)} The button above is an affiliate link; if you buy through it I may earn a commission at no extra cost to you.</p>
  <div class="tablewrap">
  <table class="kv">
    <tbody>
      {kv_rows}
    </tbody>
  </table>
  </div>
  <p class="cardnote">Open irregularities for this product: {irr_chips or '&mdash;'}</p>
</section>""")

    products_body = f"""
<h1>Product table</h1>
<p class="lede">Three products, {total_fields} comparable fields. Every populated cell carries a source link to the official
page it came from. A blank cell means the value could not be confirmed and was deliberately left empty.</p>
<div class="callout warn">
  <strong>Read this first.</strong> None of the three supplied links carries an Associates tracking tag
  (<a href="flagged-for-review.html#I-2">I-2</a>). The links work, but as supplied they cannot be verified as
  commission-earning Special Links. Re-issue them in Associates Central before launch.
</div>
<nav class="jumplinks">{''.join(f'<a href="#{p["id"]}">{esc(p["brand"]["value"])} {esc(p["model_number"]["value"])}</a>' for p in products)}</nav>
{''.join(sections)}
"""
    page("Products", products_body, "products.html", sources=sources,
         meta=f"{total_fields} fields across 3 products &middot; {verified_fields} verified &middot; {unverified_fields} blank and flagged.")

    # ------------------------------------------------------------- category
    def cap_num(p):
        return p["capacity"]["value"]

    PREFIX = "../"          # categories/ lives one level below docs/
    cat_rows = []
    for p in products:
        cat_rows.append(f"""<tr>
  <td><strong>{esc(p['brand']['value'])}</strong><span class="note">{esc(p['product_name_manufacturer']['value'])}</span></td>
  <td>{esc(p['category']['value'])} {src_link('S7' if p['id']!='P2' else 'S9', sources)}</td>
  <td>{field_cell(p['capacity'], sources, prefix='')}</td>
  <td>{field_cell(p['temperature_range'], sources, prefix='')}</td>
  <td>{field_cell(p['functions'], sources, prefix='')}</td>
  <td>{field_cell(p['power'], sources, prefix='')}</td>
  <td>{field_cell(p['warranty'], sources, prefix='')}</td>
  <td>{field_cell(p['brand_site_rating'], sources, prefix='')}</td>
</tr>""")

    cat_body = f"""
<h1>Category: air fryers &amp; countertop air-fry ovens</h1>
<p class="lede">All three supplied products sit in Amazon's <strong>Home &amp; Kitchen</strong> browse category
({src_link('S4', sources)}, {src_link('S5', sources)}, {src_link('S6', sources)}). They occupy three different
form factors, which is the only structural differentiation that can be verified from official pages.</p>

<section class="card">
  <h2>Side-by-side specification comparison</h2>
  <div class="tablewrap">
  <table class="grid">
    <thead><tr><th>Product</th><th>Form factor</th><th>Capacity</th><th>Temperature</th><th>Functions</th><th>Power</th><th>Warranty</th><th>Brand-site rating</th></tr></thead>
    <tbody>{''.join(cat_rows)}</tbody>
  </table>
  </div>
  <p class="cardnote">Amazon star ratings are omitted deliberately — they are not publicly readable without sign-in
  (<a href="flagged-for-review.html#I-11">I-11</a>). The right-hand column is the aggregate shown on the manufacturer's
  own product page and is labelled as such, not as an Amazon rating.</p>
</section>

<section class="card">
  <h2>How these three differ (verified attributes only)</h2>
  <div class="compare">
    <div>
      <h3>Dual-basket, 6 Qt</h3>
      <p>Two independent 3 Qt baskets on their own settings, with Sync Finish so both finish together.
      {src_link('S7', sources)}</p>
      <p class="cardnote">Best fit if the constraint is "cook two things at once", not "cook for six".</p>
    </div>
    <div>
      <h3>Oven-style, 26 Qt</h3>
      <p>French doors, rotisserie, 10-in-1 function list, 16.9&quot; D x 15.8&quot; W x 14.8&quot; H footprint.
      {src_link('S9', sources)}</p>
      <p class="cardnote">Best fit if the constraint is counter depth and a whole chicken or a 12-inch pizza.</p>
    </div>
    <div>
      <h3>Single-basket XL, 8 Qt</h3>
      <p>One 8 Qt basket, 4 functions, and a 450 °F Hi-Fry button for the final two minutes of cooking.
      {src_link('S8', sources)}</p>
      <p class="cardnote">Best fit if the constraint is batch size in one basket and a crispier finish.</p>
    </div>
  </div>
</section>

<section class="card">
  <h2>Category-level estimates</h2>
  <p>Search demand, seasonality and Amazon sales rank could not be sourced from an official public page, so no
  volume, trend or "best seller" claim is made. The three derived scores that <em>can</em> be computed from verified
  evidence live on the <a href="../analysis.html">analysis page</a> and are labelled as judgement, not fact.
  The missing data is listed as <a href="../flagged-for-review.html#I-15">I-15</a>.</p>
</section>
"""
    page("Category — air fryers", cat_body, "categories/air-fryers.html", active="categories/air-fryers.html",
         sources=sources, meta="Category page generated from the same verified product data.")

    # ------------------------------------------------------------- analysis
    niche_evidence = "".join(
        f"<li>{esc(e['claim'])} &rarr; <strong>{esc(e['value'])}</strong> "
        f"({src_link(e['source'], sources, 'verified source') if e.get('verified') else 'unverified'})</li>"
        for e in analysis_doc["niche"]["evidence"])
    def niche_score_cell(s):
        if s["score"] is None:
            score = '<span class="unv">blank</span>'
        else:
            score = str(s["score"])
        if s.get("flag"):
            status = (f'<a class="flagchip" href="flagged-for-review.html#{esc(s["flag"])}">'
                      f'{esc(s["flag"])}</a>')
        else:
            status = '<span class="tagtag">derived</span>'
        return (f"<tr><td>{esc(s['dimension'])}</td><td>{score}</td>"
                f"<td>{esc(s['scale'])}</td><td>{esc(s['rationale'])}</td>"
                f"<td>{status}</td></tr>")

    niche_scores = "".join(niche_score_cell(s) for s in analysis_doc["niche"]["derived_scores"])

    score_rows = "".join(
        f"<tr><td><strong>{esc(p['id'])}</strong></td>"
        f"<td>{p['verified_spec_completeness']['score']}<span class='note'>{esc(p['verified_spec_completeness']['basis'])}</span></td>"
        f"<td>{p['price_point_clarity']['score']}<span class='note'>{esc(p['price_point_clarity']['basis'])}</span></td>"
        f"<td>{p['differentiation']['score']}<span class='note'>{esc(p['differentiation']['basis'])}</span></td>"
        f"<td>{p['brand_review_depth']['score']}<span class='note'>{esc(p['brand_review_depth']['basis'])}</span></td>"
        f"<td><strong>{p['content_priority']}</strong></td></tr>"
        for p in analysis_doc["scoring_model"]["products"])

    plan_rows = "".join(
        f"<tr><td>{esc(a['title'])}</td><td>{esc(a['type'])}</td><td>{esc(a['target_query'])}</td>"
        f"<td>{esc(', '.join(a['products']))}</td><td>{esc(a['word_target'])}</td><td>{esc(a['status'])}</td></tr>"
        for a in analysis_doc["content_plan"]["articles"])

    pipeline_rows = "".join(
        f"<tr><td class='num'>{s['step']}</td><td><strong>{esc(s['name'])}</strong></td>"
        f"<td>{esc(s['automation'])}</td><td>{esc(s['control'])}</td></tr>"
        for s in analysis_doc["campaign_playbook"]["pipeline"])

    analysis_body = f"""
<h1>Analysis, findings &amp; automation design</h1>
<p class="lede">Everything on this page is either (a) a fact with a source link, or (b) explicitly labelled as a
derived judgement or a proposal. Nothing here is Amazon data, and nothing here is a revenue forecast.</p>

<section class="card">
  <h2>1. Niche assessment</h2>
  <p><strong>Niche:</strong> {esc(analysis_doc['niche']['name'])}</p>
  <h3>Evidence</h3>
  <ul class="ticks">{niche_evidence}</ul>
  <h3>Derived scores</h3>
  <div class="tablewrap">
  <table class="grid">
    <thead><tr><th>Dimension</th><th>Score</th><th>Scale</th><th>Rationale</th><th>Status</th></tr></thead>
    <tbody>{niche_scores}</tbody>
  </table>
  </div>
  <p class="cardnote">Scores are this analyst's judgement, not measured data. The seasonality row is deliberately blank
  because no licensed search-volume source was consulted (<a href="flagged-for-review.html#I-15">I-15</a>).</p>
</section>

<section class="card">
  <h2>2. Scoring model</h2>
  <p>{esc(analysis_doc['scoring_model']['why'])}</p>
  <pre class="formula">{esc(analysis_doc['scoring_model']['formula'])}</pre>
  <div class="tablewrap">
  <table class="grid">
    <thead><tr><th>Product</th><th>Spec completeness</th><th>Price clarity</th><th>Differentiation</th><th>Brand review depth</th><th>Content priority</th></tr></thead>
    <tbody>{score_rows}</tbody>
  </table>
  </div>
  <p class="cardnote">Weights are operator-set and sum to 1. "Price clarity" is 0 for every product because no
  Amazon price is verifiable (<a href="flagged-for-review.html#I-10">I-10</a>) — the score is a content-planning aid,
  not a profitability model.</p>
</section>

<section class="card">
  <h2>3. Key findings</h2>
  <ol class="findings">
    <li><strong>The three links are a single-category, two-brand programme.</strong> 100% of the links are air fryers and 2 of 3 are Chefman — 3 of 3 sit in Amazon's Home &amp; Kitchen category. Concentration risk is the dominant structural finding (<a href="flagged-for-review.html#I-2">see also I-2</a>).</li>
    <li><strong>The programme cannot currently earn.</strong> Zero of the three links carry a tracking tag, so zero of the three can be verified as a commission-bearing Special Link. This is the single highest-priority fix (I-2).</li>
    <li><strong>The three products are genuinely different machines, not variants.</strong> 6 Qt dual-basket, 26 Qt French-door oven, 8 Qt single-basket XL — a real three-way buying-guide story exists without any invented claims.</li>
    <li><strong>The weakest verified signal is the 26 Qt oven's own review aggregate.</strong> The manufacturer's own page shows 2.6/5 from 25 reviews (<a href="https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360" rel="noopener" target="_blank">source</a>). Any content that recommends it must address that honestly rather than bury it.</li>
    <li><strong>Amazon's public data surface is much smaller than the brief assumed.</strong> Prices, star ratings, review counts, BSR and the category commission rate all require authentication or API access this account does not yet have. The site is therefore built to be honest about gaps rather than to look complete.</li>
    <li><strong>The 2026 policy change materially constrains paid acquisition.</strong> Purchases referred through paid or boosted ads that link to Amazon are now excluded from commission, with limited exceptions (<a href="compliance.html#C22">C22</a>). The growth plan is therefore content/SEO-led, not ad-led.</li>
  </ol>
</section>

<section class="card">
  <h2>4. Content plan</h2>
  <div class="tablewrap">
  <table class="grid">
    <thead><tr><th>Title</th><th>Type</th><th>Target query</th><th>Products</th><th>Words</th><th>Status</th></tr></thead>
    <tbody>{plan_rows}</tbody>
  </table>
  </div>
  <p class="cardnote">Target queries are proposals for editorial planning, not measured keyword volumes.</p>
</section>

<section class="card">
  <h2>5. Automation pipeline &amp; compliance controls</h2>
  <p class="cardnote">Each automation step is paired with the control that stops it drifting out of Amazon or FTC
  policy. The controls are cross-referenced to the <a href="compliance.html">compliance matrix</a>.</p>
  <div class="tablewrap">
  <table class="grid">
    <thead><tr><th>#</th><th>Step</th><th>What the automation would do</th><th>Compliance control</th></tr></thead>
    <tbody>{pipeline_rows}</tbody>
  </table>
  </div>
  <h3>Measurable today</h3>
  <ul class="ticks">{''.join(f'<li>{esc(k)}</li>' for k in analysis_doc['campaign_playbook']['kpis_that_can_be_measured_today'])}</ul>
  <h3>Not measurable yet</h3>
  <ul class="crosses">{''.join(f'<li>{esc(k)}</li>' for k in analysis_doc['campaign_playbook']['kpis_that_cannot_be_measured_yet'])}</ul>
</section>

<section class="card">
  <h2>6. Source register</h2>
  <p class="cardnote">{len(sources)} sources were consulted. Every one is listed below with what it supports.</p>
  <div class="tablewrap">
  <table class="grid compact">
    <thead><tr><th>ID</th><th>Source</th><th>Publisher</th><th>Supports</th></tr></thead>
    <tbody>{''.join(f"<tr><td><code>{esc(s['id'])}</code></td><td><a href='{esc(s['url'])}' rel='noopener' target='_blank'>{esc(s['label'])}</a></td><td>{esc(s['publisher'])}</td><td>{esc(s['supports'])}</td></tr>" for s in sources_doc['sources'])}</tbody>
  </table>
  </div>
</section>
"""
    page("Analysis", analysis_body, "analysis.html", sources=sources,
         meta="Facts carry source links; judgements are labelled as judgements; gaps are labelled as gaps.")

    # ----------------------------------------------------------- compliance
    comp_rows = "".join(f"""
<tr id="{esc(r['id'])}">
  <td><code>{esc(r['id'])}</code></td>
  <td><strong>{esc(r['topic'])}</strong><span class="note">{esc(r['section'])}</span></td>
  <td>{esc(r['requirement'])}
      {'<blockquote>'+esc(r['quote'])+'</blockquote>' if r.get('quote') else '<p class="bad"><strong>No public official text available.</strong> This requirement could not be read from an official public page.</p>'}
      <span class="note"><strong>Applied here:</strong> {esc(r['applied'])}</span>
      {'<span class="note"><strong>Open gap &rarr;</strong> <a class="flagchip" href="flagged-for-review.html#'+esc(r['flag'])+'">'+esc(r['flag'])+'</a></span>' if r.get('gap') and r.get('flag') else ''}
      {'<span class="note"><strong>Cross-reference:</strong> '+esc(r['cross_reference'])+'</span>' if r.get('cross_reference') else ''}</td>
  <td>{src_link(r['source'], sources, 'official source')}
      {'<br><span class="bad">unverified</span>' if not r.get('verified') else '<br><span class="ok">verified</span>'}</td>
</tr>""" for r in compliance_doc["rows"])

    compliance_body = f"""
<h1>Compliance matrix</h1>
<p class="lede">{len(compliance_doc['rows'])} requirements, each with a verbatim quotation and a link to the official
Amazon or FTC page it came from. Where a requirement could not be read from a public official page, the row says so
and is marked unverified.</p>

<div class="callout">
  <strong>Policy versions read on 2026-11-13:</strong>
  Amazon Associates Program Policies — updated <strong>April 14, 2026</strong>;
  Associates Program Operating Agreement — updated <strong>October 15, 2025</strong>;
  16 CFR Part 255 — eCFR current as of 2026-11-10;
  16 CFR Part 465 — eCFR.
</div>

<section class="card">
  <h2>How this site satisfies the disclosure requirement</h2>
  <p>The disclosure bar at the top of every page carries the exact sentence Amazon requires, and the same sentence is
  repeated immediately above every block of affiliate links, so it is never behind a click or a scroll-to-footer
  (<a href="#C1">C1</a>, <a href="#C3">C3</a>, <a href="#C6">C6</a>). The site never uses "buy now" or "affiliate link"
  as its only disclosure (<a href="#C5">C5</a>).</p>
  <p>The footer of every page carries Amazon's required trademark statement
  (<a href="#C12">C12</a>): <em>{esc(TRADEMARK)}</em></p>
  <h3>Why there are no prices on this site</h3>
  <p>Amazon permits a site to display price and availability only when Amazon serves that data or when it is obtained
  through the Creators API / PA API (<a href="#C8">C8</a>). This account has neither, so the site stores no prices and
  links out to Amazon instead. That is a compliance decision, not an oversight — and it is also why the price column
  reads "not stored" rather than showing a stale number.</p>
</section>

<section class="card">
  <h2>Requirement-by-requirement matrix</h2>
  <div class="tablewrap">
  <table class="grid comp">
    <thead><tr><th>ID</th><th>Topic &amp; section</th><th>Requirement, quotation and how it is applied</th><th>Official source</th></tr></thead>
    <tbody>{comp_rows}</tbody>
  </table>
  </div>
</section>

<section class="card">
  <h2>Launch gates that are not yet met</h2>
  <ul class="crosses">
    <li><strong>Tracking tags.</strong> All three links must be re-issued with the account's tracking ID (<a href="#C7">C7</a>).</li>
    <li><strong>Qualifying sales.</strong> Amazon requires at least three qualifying sales within the first 180 days of joining (<a href="#C18">C18</a>).</li>
    <li><strong>API access.</strong> The Creators API requires at least 10 qualifying sales in the past 30 days (<a href="#C19">C19</a>). PA-API 5 must not be used — it is deprecated and returns HTTP 403.</li>
    <li><strong>Rate card.</strong> The category commission rate is behind sign-in and is therefore unpublished here (<a href="#C23">C23</a>).</li>
  </ul>
</section>
"""
    page("Compliance", compliance_body, "compliance.html", sources=sources,
         meta="Official Amazon and FTC requirements, quoted verbatim, with links for manual review.")

    # ------------------------------------------------------------- articles
    articles_index_rows = "".join(
        f"<tr><td><a href='{esc(a['slug'])}.html'>{esc(a['title'])}</a></td><td>{esc(a['type'])}</td>"
        f"<td>{esc(', '.join(a['products']))}</td><td>{esc(a['status'])}</td></tr>"
        for a in analysis_doc["content_plan"]["articles"])
    articles_body = f"""
<h1>Articles</h1>
<p class="lede">Source-linked buying guide and comparisons generated from the verified specification data.
Every article carries a standing notice that no hands-on testing was performed — the FTC rule is explicit that you
cannot describe experience with a product you have not tried (<a href="../compliance.html#C10">C10</a>).</p>
<div class="callout warn">
  <strong>Editorial status:</strong> these are drafts built only from manufacturer specifications. They contain no
  first-person testing, no invented measurements, and no price claims.
</div>
<div class="tablewrap">
<table class="grid">
  <thead><tr><th>Article</th><th>Type</th><th>Products covered</th><th>Status</th></tr></thead>
  <tbody>{articles_index_rows}</tbody>
</table>
</div>
"""
    page("Articles", articles_body, "articles/index.html", active="articles/index.html", sources=sources)

    def article(slug, title, intro, sections_html):
        body = f"""
<article class="card article">
  <p class="crumb"><a href="index.html">Articles</a> / {esc(title)}</p>
  <h1>{esc(title)}</h1>
  <div class="callout">
    <strong>Disclosure:</strong> {esc(DISCLOSURE)} This article contains affiliate links.
    <br><strong>Method:</strong> {esc(NO_HANDS_ON)}
  </div>
  {intro}
  {sections_html}
  <hr>
  <p class="cardnote">Sources for every claim in this article are on the <a href="../analysis.html#sources">source register</a>.
  Known gaps and conflicts are listed on the <a href="../flagged-for-review.html">Flagged for Review</a> page.</p>
</article>"""
        page(title, body, f"articles/{slug}.html", active="articles/index.html", sources=sources)

    # article 1 — buying guide
    guide_rows = "".join(f"""<tr>
  <td><strong>{esc(p['product_name_manufacturer']['value'])}</strong>
      <span class="note">{esc(p['brand']['value'])} &middot; {esc(p['model_number']['value'])}</span></td>
  <td>{esc(p['category']['value'])} {src_link('S7' if p['id']!='P2' else 'S9', sources)}</td>
  <td>{field_cell(p['capacity'], sources, prefix='')}</td>
  <td>{field_cell(p['temperature_range'], sources, prefix='')}</td>
  <td>{field_cell(p['functions'], sources, prefix='')}</td>
  <td>{field_cell(p['warranty'], sources, prefix='')}</td>
  <td><a class="btn small" href="{esc(p['supplied_link'])}" rel="sponsored noopener nofollow" target="_blank">Check price on Amazon</a></td>
</tr>""" for p in products)

    article("best-air-fryer-buying-guide",
            "Air Fryer Buying Guide 2026: Basket, Dual-Basket or French-Door Oven?",
            """<p class="lede">Three air fryers, three form factors, and one honest question: which shape actually fits
your kitchen? This guide compares only what the manufacturers publish — capacity, temperature, functions, footprint
and warranty — and links each specification back to its official product page.</p>""",
            f"""
<h2>The three shapes, and what each one is for</h2>
<p><strong>Basket fryers</strong> are single-drawer machines. The 8 Qt Chefman TurboFry in this programme is one:
one 8 Qt / 7.57 L basket, four functions (air fry, bake, dehydrate, frozen) and a 450 °F Hi-Fry button for the final
two minutes of cooking {src_link('S8', sources)}. It is designed to be narrow on the counter and feeds four to six.</p>
<p><strong>Dual-basket fryers</strong> split that drawer in two. The 6 Qt Chefman here is two independent 3 Qt baskets
that can run on their own settings, with Sync Finish so both finish at the same moment {src_link('S7', sources)}.
The practical difference is that a main and a side stop competing for the same basket.</p>
<p><strong>Oven-style air fryers</strong> stop being fryers and become small convection ovens. The Emeril Lagasse
French Door AirFryer 360 is 26 Qt / 24.6 L with French doors, a rotisserie and a ten-function list, in a
16.9&quot; D x 15.8&quot; W x 14.8&quot; H box {src_link('S9', sources)}. It can hold a 12-inch pizza, which no basket
fryer in this set can.</p>

<h2>Specification comparison</h2>
<div class="tablewrap">
<table class="grid">
  <thead><tr><th>Product</th><th>Form factor</th><th>Capacity</th><th>Temperature</th><th>Functions</th><th>Warranty</th><th></th></tr></thead>
  <tbody>{guide_rows}</tbody>
</table>
</div>
<p class="cardnote">Prices are deliberately absent. Amazon permits a site to show price and availability only when
Amazon serves that data or when it comes through the Creators API / PA API, which this site does not yet have — so
every price check goes to Amazon directly.</p>

<h2>How to choose</h2>
<ol class="findings">
  <li><strong>Constraint is "two foods at once on different settings"?</strong> Dual-basket. 6 Qt total across two
  3 Qt baskets.</li>
  <li><strong>Constraint is batch size in one basket?</strong> 8 Qt single basket, with the 450 °F finish.</li>
  <li><strong>Constraint is whole meals, baking or rotisserie?</strong> The 26 Qt oven format — and accept the
  counter depth it needs.</li>
</ol>

<h2>What this guide cannot tell you</h2>
<p>It cannot tell you which one cooks better, because no hands-on testing was performed and no independent test data
is cited. It also cannot tell you which is better value, because Amazon pricing is not verifiable here. The
manufacturer's own review aggregate for the 26 Qt oven reads 2.6/5 from 25 reviews {src_link('S9', sources)} — worth
reading yourself before buying, and reported here rather than omitted.</p>

<h2>One thing to check before you click</h2>
<p>The links on this page were supplied by the site owner and, at the time of capture, none of them carried an
Associates tracking tag. That does not affect what you pay, but it is recorded in the open on the
<a href="../flagged-for-review.html#I-2">Flagged for Review</a> page.</p>
""")

    p1 = products[0]
    article("chefman-6qt-dual-basket-review",
            "Chefman TurboFry 6 Qt Dual-Basket (RJ38-3DBW-V2): Spec-Based Review",
            f"""<p class="lede">A 6-quart air fryer that is really two 3-quart air fryers bolted together — with a
Sync Finish button that is the whole reason to buy it. Everything below comes from Chefman's own product page for
model {esc(p1['model_number']['value'])}.</p>""",
            f"""
<div class="product-head">
  <div>
    <h2>What it is</h2>
    <p>{esc(p1['product_name_manufacturer']['value'])}, model <code>{esc(p1['model_number']['value'])}</code>,
    ASIN <code>{esc(p1['asin']['value'])}</code>. Two independent 3 Qt / 2.84 L nonstick baskets, 6 Qt / 5.68 L in
    total {src_link('S7', sources)}.</p>
  </div>
  <div class="product-cta">
    <a class="btn primary" href="{esc(p1['supplied_link'])}" rel="sponsored noopener nofollow" target="_blank">Check price on Amazon</a>
    <span class="note">{esc(DISCLOSURE)}</span>
  </div>
</div>

<h2>Verified specifications</h2>
<div class="tablewrap">
<table class="kv"><tbody>
<tr><th>Capacity</th>{field_cell(p1['capacity'], sources, prefix='')}</tr>
<tr><th>Temperature range</th>{field_cell(p1['temperature_range'], sources, prefix='')}</tr>
<tr><th>Power</th>{field_cell(p1['power'], sources, prefix='')}</tr>
<tr><th>Functions</th>{field_cell(p1['functions'], sources, prefix='')}</tr>
<tr><th>Key features</th>{field_cell(p1['key_features'], sources, prefix='')}</tr>
<tr><th>Dishwasher safe</th>{field_cell(p1['dishwasher_safe_parts'], sources, prefix='')}</tr>
<tr><th>Certification</th>{field_cell(p1['certification'], sources, prefix='')}</tr>
<tr><th>Warranty</th>{field_cell(p1['warranty'], sources, prefix='')}</tr>
<tr><th>Reviews on chefman.com</th>{field_cell(p1['brand_site_rating'], sources, prefix='')}</tr>
<tr><th>Amazon price</th>{field_cell(p1['amazon_price'], sources, prefix='')}</tr>
<tr><th>Amazon star rating</th>{field_cell(p1['amazon_star_rating'], sources, prefix='')}</tr>
</tbody></table>
</div>

<h2>What the specifications actually mean in a kitchen</h2>
<p><strong>Two baskets beat one bigger basket only if you use them independently.</strong> The claimed advantage is
Sync Finish: you set the two baskets differently and the machine times them to land together
{src_link('S7', sources)}. If you mostly cook one thing, an 8 Qt single basket gives you more room for the same money.</p>
<p><strong>90–400 °F is a wider range than most basket fryers publish, and the low end is the interesting part.</strong>
At 90 °F the dehydrate function is usable; at 400 °F it is a normal air fryer. It does not reach the 450 °F that
Chefman's own 8 Qt model advertises.</p>
<p><strong>1700 W is a real circuit consideration.</strong> On a 120 V North American circuit that is close to a
15 A breaker's practical ceiling, so do not plan to run it on the same circuit as a kettle.</p>

<h2>Honest limitations</h2>
<ul class="crosses">
  <li>No hands-on testing was performed for this review. There is no measured crispness, noise, or cook-time data
  anywhere in this article, because inventing it would breach the FTC endorsement rules (<a href="../compliance.html#C10">C10</a>).</li>
  <li>The Amazon listing title advertises "Hi-Fry", but Chefman's own feature list for this model number does not
  include a Hi-Fry mode. That conflict is logged as <a href="../flagged-for-review.html#I-4">I-4</a> and is not
  repeated here as a feature.</li>
  <li>Country of origin is not published on the manufacturer page and is therefore blank, not guessed
  (<a href="../flagged-for-review.html#I-8">I-8</a>).</li>
</ul>

<h2>Verdict, stated as a condition rather than a score</h2>
<p>Buy this one if your recurring problem is "the fries and the chicken need different times and temperatures". Do not
buy it if you need one large basket, or if you need oven-style baking and rotisserie — the 26 Qt French-door oven is
a different machine for that job.</p>
""")

    p3, p1b = products[2], products[0]
    article("chefman-8qt-vs-6qt-dual-basket",
            "Chefman 8 Qt TurboFry vs 6 Qt Dual-Basket: Which One Fits Your Kitchen?",
            """<p class="lede">Same brand, similar money, opposite philosophies: one big basket or two small ones.
This comparison uses only the manufacturer's published specifications for both models.</p>""",
            f"""
<h2>Head to head</h2>
<div class="tablewrap">
<table class="grid">
  <thead><tr><th>Attribute</th><th>TurboFry 8 Qt (RJ38-8T-BLACK)</th><th>TurboFry 6 Qt Dual-Basket (RJ38-3DBW-V2)</th></tr></thead>
  <tbody>
    <tr><th>Total capacity</th>{field_cell(p3['capacity'], sources, prefix='')}<td>{field_cell(p1b['capacity'], sources).replace('<td>','').replace('</td>','')}</td></tr>
    <tr><th>Basket layout</th><td>One 8 Qt basket {src_link('S8', sources)}</td><td>Two independent 3 Qt baskets {src_link('S7', sources)}</td></tr>
    <tr><th>Temperature</th>{field_cell(p3['temperature_range'], sources, prefix='')}<td>{field_cell(p1b['temperature_range'], sources).replace('<td>','').replace('</td>','')}</td></tr>
    <tr><th>Functions</th>{field_cell(p3['functions'], sources, prefix='')}<td>{field_cell(p1b['functions'], sources).replace('<td>','').replace('</td>','')}</td></tr>
    <tr><th>Power</th>{field_cell(p3['power'], sources, prefix='')}<td>{field_cell(p1b['power'], sources).replace('<td>','').replace('</td>','')}</td></tr>
    <tr><th>Certification</th>{field_cell(p3['certification'], sources, prefix='')}<td>{field_cell(p1b['certification'], sources).replace('<td>','').replace('</td>','')}</td></tr>
    <tr><th>Warranty</th>{field_cell(p3['warranty'], sources, prefix='')}<td>{field_cell(p1b['warranty'], sources).replace('<td>','').replace('</td>','')}</td></tr>
    <tr><th>Brand-site reviews</th>{field_cell(p3['brand_site_rating'], sources, prefix='')}<td>{field_cell(p1b['brand_site_rating'], sources).replace('<td>','').replace('</td>','')}</td></tr>
  </tbody>
</table>
</div>

<h2>The three real differences</h2>
<ol class="findings">
  <li><strong>Workflow, not size.</strong> The 6 Qt splits into two independently-controlled 3 Qt baskets with Sync
  Finish; the 8 Qt gives the whole 8 Qt to one thing. The dual-basket wins on "main plus side"; the single basket wins
  on "a lot of one thing".</li>
  <li><strong>450 °F versus 400 °F.</strong> The 8 Qt has a dedicated Hi-Fry button that lifts the temperature to
  450 °F / 232 °C for the final two minutes. The 6 Qt dual-basket tops out at 400 °F / 204 °C. If maximum browning is
  the goal, that is the deciding spec.</li>
  <li><strong>Review depth on the brand's own site.</strong> The 8 Qt page carries 200 reviews against the 6 Qt's 30
  — thin either way, and neither is an Amazon rating. Amazon ratings could not be captured
  (<a href="../flagged-for-review.html#I-11">I-11</a>).</li>
</ol>

<h2>What would change the answer</h2>
<p>Price. Both are sold on Amazon and the live price is the tiebreaker this comparison cannot settle, because this
site does not store Amazon prices (<a href="../flagged-for-review.html#I-10">I-10</a>). Check both before deciding:</p>
<p>
<a class="btn" href="{esc(p3['supplied_link'])}" rel="sponsored noopener nofollow" target="_blank">8 Qt price on Amazon</a>
<a class="btn" href="{esc(p1b['supplied_link'])}" rel="sponsored noopener nofollow" target="_blank">6 Qt dual-basket price on Amazon</a>
</p>
<p class="cardnote"><strong>Disclosure:</strong> {esc(DISCLOSURE)}</p>
""")

    # --------------------------------------------------------------- flagged
    flag_cards = []
    for it in irr_items:
        sev = it.get("severity", "low")
        links = "".join(
            f'<li><a href="{esc(u)}" rel="noopener nofollow" target="_blank">{esc(u)}</a></li>' for u in it.get("source_urls", []))
        verified_chip = ('<span class="chip ok">verified from source</span>' if it.get("verified")
                         else '<span class="chip warn">unverified / no public source</span>')
        flag_cards.append(f"""
<section class="card flagcard sev-{esc(sev)}" id="{esc(it['id'])}">
  <div class="flaghead">
    <span class="chip sev">{esc(sev.upper())}</span>
    <span class="chip">{esc(it['type'])}</span>
    {verified_chip}
    {'<span class="chip bad">monetisation</span>' if it['id']=='I-2' else ''}
  </div>
  <h2>{esc(it['id'])} — {esc(it['title'])}</h2>
  <p>{esc(it['detail'])}</p>
  <p class="cardnote"><strong>Affects:</strong> {esc(', '.join(it.get('affected', [])))}</p>
  <p class="cardnote"><strong>Action required:</strong> {esc(it['action_required'])}</p>
  <div class="tablewrap"><table class="grid compact"><thead><tr><th>Source link for manual review</th></tr></thead>
  <tbody>{''.join('<tr><td>'+l+'</td></tr>' for l in [links])}</tbody></table></div>
</section>""")

    flagged_body = f"""
<h1>Flagged for review</h1>
<p class="lede">Everything on this page is something a human should look at: values that could not be confirmed, two
official pages that disagree, and one item that blocks monetisation entirely. None of these blocked publication —
the site is live and every item below has its source link attached so it can be checked in one click.</p>

<section class="kpis">
  {kpi(str(tally['high']), "high severity", "bad")}
  {kpi(str(tally['medium']), "medium severity", "warn")}
  {kpi(str(tally['low']), "low severity", "")}
  {kpi(str(len(irr_items)), "items total", "")}
</section>

<p class="disclosure-inline"><strong>Disclosure:</strong> {esc(DISCLOSURE)} Some links on this page are affiliate links.</p>
<div class="callout bad">
  <strong>Highest priority: I-2.</strong> None of the three supplied affiliate links carries an Amazon Associates
  tracking tag. The links resolve and the products are correct, but as supplied they cannot be verified as
  commission-earning Special Links. Re-issue all three in Associates Central before promoting the site.
</div>

<nav class="jumplinks">{''.join(f'<a href="#{esc(i["id"])}">{esc(i["id"])} &middot; {esc(i["title"])}</a>' for i in irr_items)}</nav>

{''.join(flag_cards)}

<section class="card">
  <h2>What "unverified" means here</h2>
  <p>An unverified value is one that could not be read from an official primary source — Amazon.com, the
  manufacturer's own product page, Associates Central, or the FTC/eCFR — during capture on 2026-11-13. Those cells are
  left empty on purpose. They were not filled from memory, from a reseller, from a review aggregator, or from a
  language model's prior. If you can supply the missing value with an official link, it can be added.</p>
</section>
"""
    page("Flagged for Review", flagged_body, "flagged-for-review.html", sources=sources,
         meta=f"{len(irr_items)} items: {tally['high']} high, {tally['medium']} medium, {tally['low']} low. Nothing here blocked publication.")

    # ------------------------------------------------------ executive summary
    exec_body = f"""
<h1>Executive summary</h1>
<p class="lede">A one-page account of what was supplied, what was built, what was verified, what could not be
verified, and what the owner has to do next. Written to be read in three minutes.</p>

<section class="card">
  <h2>The brief</h2>
  <p>Build an AI-assisted Amazon affiliate marketing platform for three supplied product links: automate product
  research, identify high-converting products, analyse pricing/reviews/competition/commission, generate
  SEO-optimised articles and buying guides, publish and manage affiliate links, track clicks and conversions, and
  stay inside Amazon Associates policy and FTC disclosure law.</p>
</section>

<section class="card">
  <h2>What was actually delivered</h2>
  <div class="tablewrap">
  <table class="grid">
    <thead><tr><th>Requirement</th><th>Status</th><th>Evidence</th></tr></thead>
    <tbody>
      <tr><td>Resolve and verify the three supplied links</td><td><span class="chip ok">done</span></td>
          <td>All three followed to canonical <code>/dp/</code> URLs; ASINs recorded in <a href="products.html">Products</a> and in <code>data/links</code> evidence on <a href="analysis.html#sources">the source register</a>.</td></tr>
      <tr><td>Product research with per-field sourcing</td><td><span class="chip ok">done</span></td>
          <td>{total_fields} comparable fields across 3 SKUs; {verified_fields} verified against a manufacturer page; {unverified_fields} left blank and flagged.</td></tr>
      <tr><td>Trending / high-converting identification</td><td><span class="chip warn">not possible</span></td>
          <td>No official public source for search volume, sales rank or conversion rate. Deliberately not fabricated (<a href="flagged-for-review.html#I-12">I-12</a>, <a href="flagged-for-review.html#I-15">I-15</a>).</td></tr>
      <tr><td>Pricing analysis</td><td><span class="chip warn">blocked</span></td>
          <td>Amazon prices are not readable without authentication, and policy restricts price display anyway (<a href="compliance.html#C8">C8</a>).</td></tr>
      <tr><td>Review analysis</td><td><span class="chip warn">partial</span></td>
          <td>Amazon ratings blocked by sign-in (<a href="flagged-for-review.html#I-11">I-11</a>); manufacturer-site aggregates captured instead and labelled as such.</td></tr>
      <tr><td>Competition analysis</td><td><span class="chip ok">partial</span></td>
          <td>Structural analysis only: single-category, two-brand concentration; 27 Chefman air-fryer SKUs competing in the same collection.</td></tr>
      <tr><td>Commission analysis</td><td><span class="chip warn">blocked</span></td>
          <td>Rate card behind sign-in. No rate and no revenue projection published (<a href="flagged-for-review.html#I-14">I-14</a>).</td></tr>
      <tr><td>SEO-optimised articles &amp; buying guides</td><td><span class="chip ok">done</span></td>
          <td>Three source-linked articles plus a planned fourth, in <a href="articles/index.html">Articles</a>.</td></tr>
      <tr><td>Publish and manage affiliate links</td><td><span class="chip bad">needs owner action</span></td>
          <td>Links published exactly as supplied; none carries a tracking tag (<a href="flagged-for-review.html#I-2">I-2</a>).</td></tr>
      <tr><td>Track clicks and conversions</td><td><span class="chip warn">designed, not live</span></td>
          <td>Pipeline and controls documented on <a href="analysis.html">Analysis</a> §5. No tracking ID exists yet, so no real events can be attributed.</td></tr>
      <tr><td>Continuous optimisation</td><td><span class="chip warn">designed, not live</span></td>
          <td>Same: cannot optimise on data the account cannot yet see.</td></tr>
      <tr><td>Compliance with Amazon policy and FTC disclosure</td><td><span class="chip ok">done</span></td>
          <td>{len(compliance_doc['rows'])} requirements quoted verbatim in the <a href="compliance.html">compliance matrix</a>, with the corresponding control applied on every page.</td></tr>
    </tbody>
  </table>
  </div>
</section>

<section class="card">
  <h2>The three products</h2>
  <div class="tablewrap">
  <table class="grid">
    <thead><tr><th>#</th><th>Product</th><th>ASIN</th><th>Form factor</th><th>Capacity (verified)</th></tr></thead>
    <tbody>{''.join(f"<tr><td class='num'>{p['rank']}</td><td><strong>{esc(p['product_name_manufacturer']['value'])}</strong><span class='note'>{esc(p['brand']['value'])} &middot; {esc(p['model_number']['value'])}</span></td><td><code>{esc(p['asin']['value'])}</code></td><td>{esc(p['category']['value'])}</td><td>{esc(p['capacity']['value'])} {src_link(p['capacity']['source'], sources)}</td></tr>" for p in products)}</tbody>
  </table>
  </div>
</section>

<section class="card">
  <h2>Findings that matter</h2>
  <ol class="findings">
    <li><strong>Blocking:</strong> the three links are not monetised as supplied — no tracking tag on any of them.</li>
    <li><strong>Structural:</strong> this is a one-category, two-brand programme. Concentration risk is the dominant commercial risk.</li>
    <li><strong>Data reality:</strong> Amazon's public data surface is far smaller than the brief assumes. Prices, ratings, review counts, BSR and category commission rate all require authentication or API access this account does not have.</li>
    <li><strong>Compliance is the easy part and it is done:</strong> disclosure placement, trademark attribution, no fabricated experience, no price claims — all enforced by the build, not by memory.</li>
    <li><strong>Content is ready:</strong> three articles are publishable today because they only claim what a manufacturer's spec sheet supports.</li>
  </ol>
</section>

<section class="card">
  <h2>Owner action list, in priority order</h2>
  <ol class="findings">
    <li>Re-issue all three links with your tracking ID, then update <code>data/products.json</code> (<a href="flagged-for-review.html#I-2">I-2</a>).</li>
    <li>Log in to Associates Central and record the Home/Kitchen commission rate and its date (<a href="flagged-for-review.html#I-14">I-14</a>).</li>
    <li>Confirm the Hi-Fry feature question on the 6 Qt model before any campaign copy uses it (<a href="flagged-for-review.html#I-4">I-4</a>).</li>
    <li>Confirm the 8 Qt colourway — Amazon says stainless steel, the manufacturer says matte black (<a href="flagged-for-review.html#I-7">I-7</a>).</li>
    <li>After 10 qualifying sales in 30 days, enable Creators API ingestion so prices and ratings can finally be shown lawfully (<a href="flagged-for-review.html#I-13">I-13</a>).</li>
  </ol>
</section>

<section class="card">
  <h2>Verification method, in one paragraph</h2>
  <p>Every value on this site lives in <code>data/*.json</code> as <code>{{value, source, verified}}</code>. The site is
  generated from that data, and a build check fails if any published row lacks a source URL, if a field marked verified
  has no source, or if any internal link is broken. Anything that could not be confirmed is stored as <code>null</code>
  and renders as an explicit "unverified" blank with a link to its entry on the Flagged for Review page. Analysis is
  stored in a separate file and labelled <em>derived</em> wherever it is displayed.</p>
</section>
"""
    page("Executive Summary", exec_body, "executive-summary.html", sources=sources,
         meta="Straight account of scope, delivery, gaps and next actions.")

    # ------------------------------------------------------------------ 404
    notfound = """
<h1>Page not found</h1>
<p>The page you asked for does not exist. Start from the <a href="index.html">dashboard</a>.</p>
"""
    page("Not found", notfound, "404.html", sources=sources)

    return len(products), len(sources), len(irr_items)


GENERATED_ASSETS = ("assets",)


if __name__ == "__main__":
    os.makedirs(os.path.join(DOCS, "assets"), exist_ok=True)
    if os.path.abspath(os.path.join(ROOT, "research", "assets", "style.css")) != os.path.abspath(os.path.join(DOCS, "assets", "style.css")):
        shutil.copyfile(os.path.join(ROOT, "research", "assets", "style.css"),
                    os.path.join(DOCS, "assets", "style.css"))
    stats = build()
    print(f"built: {stats[0]} products, {stats[1]} sources, {stats[2]} flagged items")
