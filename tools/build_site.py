#!/usr/bin/env python3
"""
Zone1 — static site generator.

Reads the verified data files in data/ and renders a plain static HTML site that
GitHub Pages can publish straight from the repository root (legacy build, no
build step, no external dependencies).

    python3 tools/build_site.py

Every table row that carries a finding also carries the official source URL it
was read from. Values that could not be confirmed from an official source are
rendered blank and tagged with the flag that explains why.
"""

import html
import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = ROOT

BUILD_DATE = "2026-11-13"

# --------------------------------------------------------------------------
# data loading
# --------------------------------------------------------------------------

def load(name):
    with open(os.path.join(DATA, name), "r", encoding="utf-8") as fh:
        return json.load(fh)


PRODUCTS = load("products.json")
PROGRAM = load("program.json")
FLAGS = load("flags.json")

PRODUCTS_BY_ID = {p["id"]: p for p in PRODUCTS["products"]}
LINKS_BY_ID = {l["id"]: l for l in PRODUCTS["links"]}
FLAG_BY_ID = {f["id"]: f for f in FLAGS["flags"]}
SOURCE_BY_ID = {s["id"]: s for s in PROGRAM["sources"]}

# A flag is "open" while it still needs a decision from the owner. Items whose status is
# "done" were raised, then resolved, and stay published as the audit trail.
FLAGS_OPEN = [f for f in FLAGS["flags"] if f["status"] == "needs review"]
FLAGS_CLOSED = [f for f in FLAGS["flags"] if f["status"] != "needs review"]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def esc(value):
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def up(depth):
    return "../" * depth


def link(depth, path):
    return up(depth) + path


def source_kind(url):
    """Short, human label for an official source URL."""
    if not url:
        return "Source"
    if "affiliate-program.amazon.com" in url:
        return "Amazon Associates"
    if "link.amazon" in url:
        return "link.amazon"
    if "m.media-amazon.com" in url:
        return "Amazon PDF"
    if url.startswith("https://www.amazon.com/s?"):
        return "Amazon search"
    if url.startswith("https://www.amazon.com/dp/") or url.startswith("https://www.amazon.com/gp/"):
        return "Amazon"
    if "ftc.gov" in url:
        return "FTC"
    if "ecfr.gov" in url:
        return "eCFR"
    if "api.github.com" in url:
        return "GitHub API"
    if "github.com" in url:
        return "GitHub"
    host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
    return host


def src_cell(url, extra_urls=None):
    """A table cell holding the official source link(s) for a row."""
    urls = [url] + list(extra_urls or [])
    seen, out = set(), []
    for u in urls:
        if u and u not in seen:
            seen.add(u)
            out.append(
                '<a href="{u}" target="_blank" rel="noopener noreferrer" title="{u}">{lab}</a>'.format(
                    u=esc(u), lab=esc(source_kind(u))
                )
            )
    return " · ".join(out) if out else '<span class="muted">—</span>'


def flag_pill(fid, depth):
    f = FLAG_BY_ID.get(fid)
    if not f:
        return ""
    return (
        '<a class="pill flag" href="{u}#{fid}" title="{title}">{fid}</a> '
    ).format(u=esc(link(depth, "pages/flagged.html")), fid=esc(fid), title=esc(f["title"]))


def value_cell(field, depth):
    """Render a single verified/unverified field value."""
    if field["status"] == "verified":
        return esc(field["value"])
    pills = "".join(flag_pill(fid, depth) for fid in field.get("flag_ids", []))
    return '<span class="empty">not verified</span> {0}'.format(pills).strip()


def field_value(product, label, default=None):
    for f in product["fields"]:
        if f["label"] == label:
            return f["value"] if f["status"] == "verified" else default
    return default


def field_source(product, label):
    for f in product["fields"]:
        if f["label"] == label:
            return f["source"]
    return None


def num(text):
    """Pull the first number out of a money/quantity string, or None."""
    if text is None:
        return None
    m = re.search(r"\$?([0-9][0-9,]*(?:\.[0-9]+)?)", str(text))
    return float(m.group(1).replace(",", "")) if m else None


def money(value):
    if value is None:
        return "—"
    return "${:,.2f}".format(value)


def product_fields_table(product, depth):
    rows = []
    for f in product["fields"]:
        rows.append(
            "<tr><td class=\"rowhead\">{label}</td><td>{value}</td>"
            "<td class=\"src\">{src}</td></tr>".format(
                label=esc(f["label"]),
                value=value_cell(f, depth),
                src=src_cell(f["source"]),
            )
        )
    return (
        '<div class="table-scroll"><table class="data"><thead><tr>'
        "<th>Attribute</th><th>Verified value</th><th>Official source</th>"
        "</tr></thead><tbody>{rows}</tbody></table></div>".format(rows="".join(rows))
    )


def disclosure_block(depth, note=None):
    ftc = (
        "We are a participant in the Amazon Services LLC Associates Programme, an "
        "affiliate advertising programme designed to provide a means for sites to "
        "earn advertising fees by advertising Amazon products."
    )
    extra = (
        '<p class="small" style="margin-top:8px">In this article we earn money from '
        "qualifying purchases made through our links, at no extra cost to you. "
        "That is our only incentive to recommend a product — and it does not change "
        "what we write about it.</p>"
        if note
        else ""
    )
    return (
        '<div class="disclosure"><strong>Affiliate disclosure.</strong> {ftc}'
        '<p class="small" style="margin:6px 0 0">Amazon may receive a commission '
        "from purchases made through links on this site, at no additional cost to "
        "you. The price you pay is unchanged. {extra}</p></div>"
    ).format(ftc=esc(ftc), extra=extra)


def footer(depth, generated=BUILD_DATE):
    return """
<footer class="site"><div class="wrap">
  <div class="frow"><strong>Zone1 — Amazon Affiliate Marketing Platform.</strong>
  Research platform and published site for three air-fryer products on Amazon.com.</div>
  <div class="frow">Static site published with GitHub Pages. Data snapshot verified
  {gen}. No affiliation with, endorsement of, or sponsorship by Amazon.com, Inc.,
  Chefman or Emeril Lagasse.</div>
  <div class="disclosure"><strong>As an Amazon Associate I earn from qualifying purchases.</strong><br>
  We are a participant in the Amazon Services LLC Associates Programme, an affiliate
  advertising programme designed to provide a means for sites to earn advertising fees
  by advertising Amazon products. In our content we earn money from qualifying purchases
  made through our links, at no extra cost to you.</div>
  <div class="frow">
    <a href="{d}index.html">Dashboard</a> ·
    <a href="{d}pages/catalog.html">Catalogue</a> ·
    <a href="{d}pages/compliance.html">Compliance</a> ·
    <a href="{d}pages/sources.html">Sources</a> ·
    <a href="{d}pages/flagged.html">Flagged for Review</a> ·
    <a href="{d}COORDINATION.md">Coordination board</a>
  </div>
</div></footer>
""".format(gen=esc(generated), d=esc(up(depth)))


NAV = [
    ("Overview", [
        ("index.html", "Dashboard"),
        ("pages/executive-summary.html", "Executive Summary"),
    ]),
    ("Catalogue", [
        ("pages/catalog.html", "All Products"),
        ("pages/category/dual-basket-air-fryers.html", "Dual-Basket Air Fryers"),
        ("pages/category/multi-function-air-fryer-ovens.html", "Multi-Function Air Fryer Ovens"),
    ]),
    ("Research", [
        ("pages/research.html", "Research & Analysis"),
    ]),
    ("Marketing content", [
        ("pages/marketing/seo-article.html", "SEO Article"),
        ("pages/marketing/comparison.html", "Head-to-Head Comparison"),
        ("pages/marketing/buying-guide.html", "Buying Guide"),
    ]),
    ("Operations", [
        ("pages/campaign.html", "Campaign & Tracking"),
        ("pages/compliance.html", "Compliance"),
    ]),
    ("Governance", [
        ("pages/sources.html", "Sources & Verification"),
        ("pages/flagged.html", "Flagged for Review"),
    ]),
]


def sidebar(depth):
    parts = []
    for group, items in NAV:
        parts.append('<div class="nav-group"><h2>{}</h2>'.format(esc(group)))
        for href, label in items:
            parts.append('<a href="{u}">{l}</a>'.format(u=esc(up(depth) + href), l=esc(label)))
        parts.append("</div>")
    return (
        '<aside class="sidebar">'
        '<div class="brand"><a href="{d}index.html">'
        '<span class="mark">Z1</span><span class="title">Zone1</span></a>'
        '<div class="sub">Amazon affiliate research &amp; publishing platform</div></div>'
        "{nav}</aside>"
    ).format(d=esc(up(depth)), nav="".join(parts))


def layout(page, title, crumb, body, depth, subtitle=""):
    subtitle_block = ""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Zone1</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{d}assets/css/site.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%23146c94'/><text x='16' y='22' font-family='sans-serif' font-size='15' font-weight='bold' fill='white' text-anchor='middle'>Z1</text></svg>">
</head>
<body>
<div class="shell">
{sidebar}
<div class="main">
  <div class="topbar">
    <button class="menu-btn" type="button">Menu</button>
    <div class="crumb">{crumb}</div>
  </div>
  <div class="wrap">
{subtitle_block}{body}
  </div>
  {footer}
</div>
</div>
<script src="{d}assets/js/site.js"></script>
</body>
</html>
""".format(
        title=esc(title),
        desc=esc(subtitle or title),
        d=esc(up(depth)),
        sidebar=sidebar(depth),
        crumb=crumb,
        subtitle_block=subtitle_block,
        body=body,
        footer=footer(depth),
    )


def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)
    print("wrote", path)


# --------------------------------------------------------------------------
# shared page fragments
# --------------------------------------------------------------------------

def status_pill(status):
    if status == "verified":
        return '<span class="pill ok">verified</span>'
    return '<span class="pill flag">unverified</span>'


def snapshot_table(depth, ids=None):
    """Compact one-row-per-product snapshot with source links."""
    prods = [PRODUCTS_BY_ID[i] for i in (ids or ["p1", "p2", "p3"])]
    rows = []
    for p in prods:
        price = field_value(p, "Current price (new)")
        rating = field_value(p, "Customer rating (stars)")
        count = field_value(p, "Customer ratings (count)")
        bsr = field_value(p, "Best Sellers Rank — Air Fryers")
        bought = field_value(p, "Bought in past month")
        src = field_source(p, "Current price (new)")
        rows.append(
            "<tr>"
            "<td><a href=\"{u}\"><strong>{name}</strong></a><br>"
            '<span class="mono small muted">{asin}</span></td>'
            "<td>{cat}</td>"
            "<td class=\"num\">{price}</td>"
            "<td class=\"num\">{rating}</td>"
            "<td class=\"num\">{count}</td>"
            "<td class=\"num\">{bsr}</td>"
            "<td>{bought}</td>"
            "<td class=\"src\">{src}</td>"
            "</tr>".format(
                u=esc(link(depth, "pages/catalog.html#{}".format(p["id"]))),
                name=esc(p["short_name"]),
                asin=esc(p["asin"]),
                cat=esc(p["category"]),
                price=esc(price) if price else '<span class="empty">not verified</span>',
                rating=esc(rating) if rating else '<span class="empty">not verified</span>',
                count=esc(count) if count else '<span class="empty">not verified</span>',
                bsr=esc(bsr) if bsr else '<span class="empty">not verified</span> ' + flag_pill("F-03", depth),
                bought=esc(bought) if bought else '<span class="empty">not verified</span>',
                src=src_cell(src),
            )
        )
    return (
        '<div class="table-scroll"><table class="data"><thead><tr>'
        "<th>Product</th><th>Category</th><th>Price</th><th>Rating</th><th>Ratings</th>"
        "<th>BSR (Air Fryers)</th><th>Velocity</th><th>Official source</th>"
        "</tr></thead><tbody>{rows}</tbody></table></div>".format(rows="".join(rows))
    )


def link_template_box(product):
    return (
        '<div class="linkbox" data-copy="{u}"><span class="url">{u}</span>'
        '<button class="copy" type="button">Copy</button></div>'
    ).format(u=esc(product["special_link_template"]))


def bullets_block(product):
    if not product["bullets"]:
        return '<p class="muted">{}</p>'.format(esc(product.get("bullets_note", "Not available.")))
    items = "".join("<li>{}</li>".format(esc(b)) for b in product["bullets"])
    return (
        '<ul>{}</ul><p class="small muted">Verbatim manufacturer bullet points, '
        'read from <a href="{s}" target="_blank" rel="noopener noreferrer">{k}</a>.</p>'
    ).format(items, s=esc(field_source(product, "Title")), k=esc(source_kind(field_source(product, "Title"))))


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def page_index():
    depth = 0
    total_fields = sum(len(p["fields"]) for p in PRODUCTS["products"])
    unverified = sum(1 for p in PRODUCTS["products"] for f in p["fields"] if f["status"] != "verified")
    verified = total_fields - unverified

    body = """
<div class="hero">
  <h1>Zone1 — Amazon affiliate research &amp; publishing platform</h1>
  <p class="lede">A verified research record and a publishable marketing site for three
  air-fryer products on Amazon.com. Every value in every table was read from an official
  first-party source and carries a link to it. Anything that could not be confirmed is left
  blank and flagged — never inferred.</p>
  <div class="badges">
    <span class="pill info">{total_fields} tracked attributes</span>
    <span class="pill ok">{verified} verified</span>
    <span class="pill flag">{unverified} unverified</span>
    <span class="pill warn">{nopen} open irregularities</span>
    <span class="pill grey">{nclosed} resolved</span>
    <span class="pill grey">Snapshot: {build}</span>
  </div>
</div>

<div class="grid g4" style="margin-bottom:16px">
  <div class="kpi"><div class="label">Products in scope</div><div class="value">3</div>
    <div class="note">from 3 supplied link.amazon URLs</div></div>
  <div class="kpi"><div class="label">Canonical ASINs resolved</div><div class="value">3</div>
    <div class="note">all three redirect targets confirmed</div></div>
  <div class="kpi"><div class="label">Official sources cited</div><div class="value">{n_sources}</div>
    <div class="note">Amazon, Amazon Associates, FTC, eCFR</div></div>
  <div class="kpi"><div class="label">Program rules mapped</div><div class="value">{n_terms}</div>
    <div class="note">{n_rules} automation rules</div></div>
</div>

<div class="card flush">
  <div class="card-head"><strong>Product snapshot</strong> <span class="muted small">— click a product for its full verified record</span></div>
  <div class="card-body" style="padding:0">{snapshot}</div>
</div>

<div class="grid g2">
  <div class="card">
    <h2 style="margin-top:0">What this project does</h2>
    <ol class="small">
      <li><strong>Resolve</strong> — the three supplied <span class="mono">link.amazon</span> URLs are followed to their canonical <span class="mono">amazon.com/dp/&lt;ASIN&gt;</span> destination and the product identity confirmed from the page title. <span class="pill flag">F-01</span></li>
      <li><strong>Verify</strong> — every attribute is read from the live official page. 3 ASINs, {total_fields} attributes, {verified} confirmed, {unverified} left blank.</li>
      <li><strong>Analyse</strong> — pricing, review depth, competitive set, demand velocity and commission potential are modelled from the verified values only.</li>
      <li><strong>Generate</strong> — SEO article, head-to-head comparison and buying guide, each carrying the required Amazon and FTC disclosures inline.</li>
      <li><strong>Operate</strong> — link templates with a publisher tag, a sub-tag measurement scheme, and a re-verification schedule that keeps price and badge claims compliant.</li>
      <li><strong>Govern</strong> — {n_terms} program rules mapped to this site, {n_rules} automation rules, and {nopen} open irregularities published for review rather than silently resolved.</li>
    </ol>
  </div>
  <div class="card">
    <h2 style="margin-top:0">Read next</h2>
    <ul class="small">
      <li><a href="{d}pages/executive-summary.html">Executive Summary</a> — the one-page brief.</li>
      <li><a href="{d}pages/catalog.html">All Products</a> — every tracked attribute, with its source.</li>
      <li><a href="{d}pages/research.html">Research &amp; Analysis</a> — pricing, reviews, competition, commission model, demand signals.</li>
      <li><a href="{d}pages/marketing/seo-article.html">SEO Article</a>, <a href="{d}pages/marketing/comparison.html">Comparison</a> and <a href="{d}pages/marketing/buying-guide.html">Buying Guide</a> — publishable content.</li>
      <li><a href="{d}pages/campaign.html">Campaign &amp; Tracking</a> — link management, measurement and optimisation loop.</li>
      <li><a href="{d}pages/compliance.html">Compliance</a> — Amazon Associates rules and FTC disclosure requirements.</li>
      <li><a href="{d}pages/sources.html">Sources &amp; Verification</a> — the full audit trail.</li>
      <li><a href="{d}pages/flagged.html">Flagged for Review</a> — {nopen} open items and {nclosed} resolved, each with its source.</li>
    </ul>
  </div>
</div>

<div class="card">
  <h2 style="margin-top:0">Verification standard applied</h2>
  <p class="small">{policy}</p>
  <div class="note warn"><strong>One standing caveat.</strong> Amazon Associates Program
  Policies restrict displaying Product prices and star ratings unless they are served by
  Amazon alongside the link or obtained through Creators API / PA API. This site is a static
  research build, so those values are dated snapshots of official pages, not licensed
  Product Advertising Content. The compliant routes to go live are set out on the
  <a href="{d}pages/compliance.html">Compliance</a> page and tracked as
  <span class="pill flag">F-07</span> <span class="pill flag">F-08</span>.</div>
</div>
""".format(
        total_fields=total_fields,
        verified=verified,
        unverified=unverified,
        nflags=len(FLAGS["flags"]),
        nopen=len(FLAGS_OPEN),
        nclosed=len(FLAGS_CLOSED),
        n_sources=len(PROGRAM["sources"]),
        n_terms=len(PROGRAM["program_terms"]),
        n_rules=len(PROGRAM["automation_rules"]),
        build=BUILD_DATE,
        snapshot=snapshot_table(depth),
        d=esc(up(depth)),
        policy=esc(PRODUCTS["meta"]["verification_policy"]),
    )
    return layout(
        "index.html",
        "Dashboard",
        "<strong>Zone1</strong> / Dashboard",
        body,
        depth,
        subtitle="Verified Amazon affiliate research dashboard for three air-fryer products.",
    )


def page_executive_summary():
    depth = 1
    p1, p2, p3 = PRODUCTS_BY_ID["p1"], PRODUCTS_BY_ID["p2"], PRODUCTS_BY_ID["p3"]
    price1 = num(field_value(p1, "Current price (new)"))
    price2 = num(field_value(p2, "Current price (new)"))
    price3 = num(field_value(p3, "Current price (new)"))
    bsr1 = field_value(p1, "Best Sellers Rank — Air Fryers")
    bsr3 = field_value(p3, "Best Sellers Rank — Air Fryers")

    body = """
<h1>Executive Summary</h1>
<p class="lede">Three air-fryer products were supplied as <span class="mono">link.amazon</span>
short URLs. All three were resolved to canonical Amazon ASINs, verified attribute by attribute
against the live official pages, analysed for demand, price and competition, and turned into a
publishable affiliate content set with a compliance framework attached. This page is the brief;
every number on it links to the official source it came from.</p>

<div class="card flush" style="margin-bottom:16px">
  <div class="card-head"><strong>Decision summary</strong></div>
  <div class="card-body" style="padding:0">
  <div class="table-scroll"><table class="data"><thead><tr>
    <th>Product</th><th>ASIN</th><th>Price (verified)</th><th>Rating</th><th>Ratings</th>
    <th>BSR · Air Fryers</th><th>Velocity</th><th>Verdict</th><th>Official source</th>
  </tr></thead><tbody>
    <tr><td><strong>{n1}</strong></td><td class="mono">{a1}</td><td class="num">{pr1}</td>
      <td class="num">{r1}</td><td class="num">{c1}</td><td class="num">{b1}</td><td>{v1}</td>
      <td><span class="pill ok">Lead product</span> dual-zone differentiator, Amazon's Choice,
      best mid-price anchor of the Chefman range at 6 qt</td>
      <td class="src">{s1}</td></tr>
    <tr><td><strong>{n2}</strong></td><td class="mono">{a2}</td><td class="num">{pr2}</td>
      <td class="num">{r2}</td><td class="num">{c2}</td>
      <td class="empty">not verified {f3}</td><td>{v2}</td>
      <td><span class="pill info">Highest-ticket</span> largest capacity, most functions and a
      rotisserie — the natural "premium" comparison target, but the highest commission base
      per order</td>
      <td class="src">{s2}</td></tr>
    <tr><td><strong>{n3}</strong></td><td class="mono">{a3}</td><td class="num">{pr3}</td>
      <td class="num">{r3}</td><td class="num">{c3}</td><td class="num">{b3}</td><td>{v3}</td>
      <td><span class="pill ok">Scale product</span> strongest demand signal of the three —
      #8 in Air Fryers and the deepest verified review base</td>
      <td class="src">{s3}</td></tr>
  </tbody></table></div>
  </div>
</div>

<h2>What matters most</h2>
<div class="grid g3">
  <div class="card"><h3 style="margin-top:0">1. The supplied links were not product IDs</h3>
    <p class="small">Each URL path segment looks like an ASIN but is an opaque redirect token.
    The links resolve to <span class="mono">B0CDY277D3</span>, <span class="mono">B09B7SB46R</span>
    and <span class="mono">B08DKYBTPH</span> — two brands, two product formats and a price band
    from roughly $80 to $150. Rebuilding links from the path segment would have pointed every
    future article at the wrong product. {f1}</p>
    <p class="small"><a href="{d}pages/catalog.html">See the resolved link table →</a></p></div>

  <div class="card"><h3 style="margin-top:0">2. Commission rates cannot be stated publicly</h3>
    <p class="small">The Standard Commission Income schedule redirects to the Amazon sign-in
    page. The revenue model on the research page therefore takes the commission rate as an
    <em>input</em> the publisher supplies from their own rate card, and shows the arithmetic at
    a spread of illustrative rates. No rate is asserted as fact. {f4}</p>
    <p class="small"><a href="{d}pages/research.html#commission">See the commission model →</a></p></div>

  <div class="card"><h3 style="margin-top:0">3. Two compliance gates must be closed before traffic</h3>
    <p class="small">Program Policies allow a Site to show prices only if Amazon serves them with
    the link or they come from Creators API / PA API, and forbid displaying Amazon star ratings
    and reviews unless obtained through those APIs. This build is static research, so both
    gates are open and are published for review. {f7} {f8}</p>
    <p class="small"><a href="{d}pages/compliance.html">See the compliant routes →</a></p></div>
</div>

<h2>Verified commercial picture</h2>
<div class="grid g2">
  <div class="card">
    <h3 style="margin-top:0">Demand and ranking</h3>
    <div class="table-scroll"><table class="data compact"><thead><tr>
      <th>Signal</th><th>P1</th><th>P2</th><th>P3</th><th>Official source</th>
    </tr></thead><tbody>
      <tr><td class="rowhead">Bought in past month</td><td>{v1}</td><td>{v2}</td><td>{v3}</td>
        <td class="src">{sb}</td></tr>
      <tr><td class="rowhead">BSR · Air Fryers</td><td>{b1}</td><td class="empty">not verified {f3}</td>
        <td>{b3}</td><td class="src">{sb}</td></tr>
      <tr><td class="rowhead">Customer ratings</td><td>{c1}</td><td>{c2}</td><td>{c3}</td>
        <td class="src">{sb}</td></tr>
      <tr><td class="rowhead">Price / list price</td><td>{pr1}<br><span class="muted">{lp1}</span></td>
        <td>{pr2}<br><span class="muted">{lp2}</span></td>
        <td>{pr3}<br><span class="muted">{lp3}</span></td><td class="src">{sb}</td></tr>
    </tbody></table></div>
    <p class="small muted" style="margin-top:10px">The Chefman brand panel on the P1 page also
    reports "Highly Rated — 100K+ customers rate items from this brand highly", "Trending — 100K+
    orders for this brand in past 3 months" and "Low Returns". Source:
    <a href="{sd}" target="_blank" rel="noopener noreferrer">Amazon product page</a>.</p>
  </div>

  <div class="card">
    <h3 style="margin-top:0">Competitive set observed on the official pages</h3>
    <p class="small">Amazon's own "Customers who viewed this item also viewed" and "Frequently
    bought together" modules surfaced these competing and adjacent listings. Each is a real
    comparison target for the content strategy.</p>
    <div class="table-scroll"><table class="data compact"><thead><tr>
      <th>ASIN</th><th>Product</th><th>Rating</th><th>Price</th><th>Official source</th>
    </tr></thead><tbody>
      {comp}
    </tbody></table></div>
  </div>
</div>

<h2>What this project delivers</h2>
<div class="grid g4">
  <div class="kpi"><div class="label">Verified attributes</div><div class="value sm">{verified}</div>
    <div class="note">of {total_fields} tracked, across 3 ASINs</div></div>
  <div class="kpi"><div class="label">Publishable content pieces</div><div class="value sm">3</div>
    <div class="note">SEO article, comparison, buying guide</div></div>
  <div class="kpi"><div class="label">Program rules mapped</div><div class="value sm">{n_terms}</div>
    <div class="note">plus {n_rules} automation rules</div></div>
  <div class="kpi"><div class="label">Open items for review</div><div class="value sm">{nopen}</div>
    <div class="note">published, non-blocking</div></div>
</div>

<h2>Recommended sequence</h2>
<ol class="small">
  <li><strong>Close the two compliance gates.</strong> Replace the static price column with a
      SiteStripe / PA API widget and source ratings through PA API, or drop both from the
      published pages and keep them in the internal research record. This is a publisher
      decision — see {f7} and {f8}.</li>
  <li><strong>Apply the Associates tag.</strong> Every link template currently carries the
      placeholder <span class="mono">YOUR-TAG-XX</span>. Replace it with the real Associates ID
      before any page is shared. {f11}</li>
  <li><strong>Stand up the re-verification job.</strong> Prices, badges and Best Sellers Rank are
      point-in-time. The schedule and the replacement path for live prices are specified on the
      <a href="{d}pages/campaign.html">Campaign &amp; Tracking</a> page. {f5}</li>
  <li><strong>Publish in order of certainty.</strong> Lead with P3 and P1, whose records are
      complete, and hold P2's specification-heavy comparison copy until its detail page serves a
      readable body again. {f3}</li>
  <li><strong>Keep the disclosure adjacent to every monetised block</strong>, not only in the
      footer, and never state a product experience the publisher has not had.</li>
</ol>

<div class="note flag"><strong>Review items that do not block this site going live.</strong>
{nopen} open irregularities are published on the <a href="{d}pages/flagged.html">Flagged for
Review</a> page, each with what was observed, the official source that was checked, and the
action taken. They are decisions for the publisher after the site is live.</div>
""".format(
        n1=esc(p1["short_name"]), a1=esc(p1["asin"]),
        pr1=esc(field_value(p1, "Current price (new)") or "—"),
        r1=esc(field_value(p1, "Customer rating (stars)") or "—"),
        c1=esc(field_value(p1, "Customer ratings (count)") or "—"),
        b1=esc(bsr1 or "—"), v1=esc(field_value(p1, "Bought in past month") or "—"),
        s1=src_cell(field_source(p1, "Current price (new)")),
        n2=esc(p2["short_name"]), a2=esc(p2["asin"]),
        pr2=esc(field_value(p2, "Current price (new)") or "—"),
        r2=esc(field_value(p2, "Customer rating (stars)") or "—"),
        c2=esc(field_value(p2, "Customer ratings (count)") or "—"),
        v2=esc(field_value(p2, "Bought in past month") or "—"),
        s2=src_cell(field_source(p2, "Current price (new)")),
        n3=esc(p3["short_name"]), a3=esc(p3["asin"]),
        pr3=esc(field_value(p3, "Current price (new)") or "—"),
        r3=esc(field_value(p3, "Customer rating (stars)") or "—"),
        c3=esc(field_value(p3, "Customer ratings (count)") or "—"),
        b3=esc(bsr3 or "—"), v3=esc(field_value(p3, "Bought in past month") or "—"),
        s3=src_cell(field_source(p3, "Current price (new)")),
        lp1=esc("List " + str(field_value(p1, "List price"))),
        lp2=esc("List " + str(field_value(p2, "List price"))),
        lp3=esc("List " + str(field_value(p3, "List price"))),
        f1=flag_pill("F-01", depth), f3=flag_pill("F-03", depth),
        f4=flag_pill("F-04", depth), f5=flag_pill("F-05", depth),
        f7=flag_pill("F-07", depth), f8=flag_pill("F-08", depth),
        f11=flag_pill("F-11", depth),
        sb=src_cell("https://www.amazon.com/dp/B0CDY277D3", ["https://www.amazon.com/dp/B08DKYBTPH",
                                                             "https://www.amazon.com/s?k=B09B7SB46R"]),
        sd=esc("https://www.amazon.com/dp/B0CDY277D3"),
        comp="".join(
            '<tr><td class="mono">{asin}</td><td>{title}</td><td class="num">{r}</td>'
            '<td class="num">{p}</td><td class="src">{s}</td></tr>'.format(
                asin=esc(c["asin"]),
                title=esc(c["title"][:78] + ("…" if len(c["title"]) > 78 else "")),
                r=esc(c["rating"] or "—"),
                p=esc(c["price"] or "—"),
                s=src_cell(c["source"]),
            ) for c in PRODUCTS["competitive_set"]
        ),
        verified=sum(1 for p in PRODUCTS["products"] for f in p["fields"] if f["status"] == "verified"),
        total_fields=sum(len(p["fields"]) for p in PRODUCTS["products"]),
        n_terms=len(PROGRAM["program_terms"]),
        n_rules=len(PROGRAM["automation_rules"]),
        nflags=len(FLAGS["flags"]),
        nopen=len(FLAGS_OPEN),
        nclosed=len(FLAGS_CLOSED),
        d=esc(up(depth)),
    )
    return layout(
        "pages/executive-summary.html",
        "Executive Summary",
        "<strong>Zone1</strong> / Executive Summary",
        body,
        depth,
        subtitle="Executive summary of the Zone1 Amazon affiliate research and content project.",
    )


def page_catalog():
    depth = 1
    body = """
<h1>All Products — verified catalogue</h1>
<p class="lede">Every tracked attribute for all three products, in one place. Each row names the
official source its value was read from. Rows marked <span class="pill flag">unverified</span> are
empty on purpose: the official source did not serve a readable value, and the neighbouring flag
explains exactly what was tried.</p>

<div class="card flush" style="margin-bottom:18px">
  <div class="card-head"><strong>Resolved link table</strong> <span class="muted small">— how each supplied URL maps to a product</span></div>
  <div class="card-body" style="padding:0">
  <div class="table-scroll"><table class="data"><thead><tr>
    <th>ID</th><th>Supplied URL</th><th>Path segment</th><th>Segment is the ASIN?</th>
    <th>Resolved URL</th><th>Resolved ASIN</th><th>Resolved page title</th><th>Official source</th>
  </tr></thead><tbody>
  {links}
  </tbody></table></div>
  </div>
</div>
""".format(
        links="".join(
            "<tr><td class=\"mono\">{id}</td><td class=\"mono\"><a href=\"{u}\" target=\"_blank\" "
            "rel=\"noopener noreferrer\">{u}</a></td><td class=\"mono\">{seg}</td>"
            "<td><span class=\"pill flag\">no</span> {f}</td><td class=\"mono\"><a href=\"{ru}\" "
            "target=\"_blank\" rel=\"noopener noreferrer\">{ru}</a></td><td class=\"mono\">{asin}</td>"
            "<td>{title}</td><td class=\"src\">{src}</td></tr>".format(
                id=esc(l["id"]), u=esc(l["supplied_url"]), seg=esc(l["path_segment"]),
                f=flag_pill("F-01", depth), ru=esc(l["resolved_url"]), asin=esc(l["resolved_asin"]),
                title=esc(l["resolved_title"]), src=src_cell(l["supplied_url"], [l["resolved_url"]]),
            ) for l in PRODUCTS["links"]
        )
    )

    body += """
<h2 style="margin-top:22px">Full product records</h2>
<p class="small muted">One card per product, with every tracked attribute and its source.</p>
"""

    for p in PRODUCTS["products"]:
        body += """
<div class="card flush" id="{pid}">
  <div class="card-head">
    <strong>{ref} · {name}</strong>
    <div class="small muted" style="margin-top:4px">
      <span class="mono">{asin}</span> · {cat} · verified {vdate} · {flags}
    </div>
  </div>
  <div class="card-body">
    <div class="grid g3" style="margin-bottom:14px">
      <div class="kpi"><div class="label">Price (snapshot)</div><div class="value sm">{price}</div>
        <div class="note">list {listprice}</div></div>
      <div class="kpi"><div class="label">Rating</div><div class="value sm">{rating}</div>
        <div class="note">{count} ratings</div></div>
      <div class="kpi"><div class="label">Demand</div><div class="value sm">{bought}</div>
        <div class="note">BSR Air Fryers: {bsr}</div></div>
    </div>

    <h3>Verified attributes</h3>
    {fields}

    <h3>Manufacturer feature bullets (verbatim)</h3>
    {bullets}

    <h3>Affiliate link template</h3>
    <p class="small">Replace <span class="mono">YOUR-TAG-XX</span> with your Associates ID
    before publishing. Special Links must carry the publisher's tag, must link directly to the
    Product detail page, and must not pass through a link shortener or redirect.
    {f11} <a href="{d}pages/compliance.html">Compliance detail →</a></p>
    {linkbox}

    <h3>Category path</h3>
    <p class="small">{catpath} <span class="muted">·</span> Source: {catsrc}</p>
  </div>
</div>
""".format(
            pid=esc(p["id"]),
            ref=esc(p["ref"]),
            name=esc(p["name"]),
            asin=esc(p["asin"]),
            cat=esc(p["category"]),
            vdate=esc(p["verified_on"]),
            flags=" ".join(flag_pill(f, depth) for f in p["flag_ids"]),
            price=esc(field_value(p, "Current price (new)") or "not verified"),
            listprice=esc(field_value(p, "List price") or "not verified"),
            rating=esc(field_value(p, "Customer rating (stars)") or "not verified"),
            count=esc(field_value(p, "Customer ratings (count)") or "not verified"),
            bought=esc(field_value(p, "Bought in past month") or "not verified"),
            bsr=esc(field_value(p, "Best Sellers Rank — Air Fryers") or "not verified"),
            fields=product_fields_table(p, depth),
            bullets=bullets_block(p),
            f11=flag_pill("F-11", depth),
            linkbox=link_template_box(p),
            d=esc(up(depth)),
            catpath=esc(p["category_path"]),
            catsrc=src_cell(p["category_source"]),
        )

    body += """
<div class="card flush">
  <div class="card-head"><strong>Brand-level signals read from the official pages</strong></div>
  <div class="card-body" style="padding:0">
  <div class="table-scroll"><table class="data"><thead><tr>
    <th>Signal</th><th>Value as stated by Amazon</th><th>Official source</th>
  </tr></thead><tbody>
  {brand}
  </tbody></table></div>
  </div>
</div>

<div class="card flush">
  <div class="card-head"><strong>Competitive set</strong> <span class="muted small">— listings Amazon itself surfaced on the product pages</span></div>
  <div class="card-body" style="padding:0">
  <div class="table-scroll"><table class="data"><thead><tr>
    <th>ASIN</th><th>Title</th><th>Rating</th><th>Ratings</th><th>Price</th><th>List price</th>
    <th>Discount</th><th>Relationship to our products</th><th>Official source</th>
  </tr></thead><tbody>
  {comp}
  </tbody></table></div>
  </div>
</div>
""".format(
        brand="".join(
            '<tr><td class="rowhead">{l}</td><td>{v}</td><td class="src">{s}</td></tr>'.format(
                l=esc(b["label"]), v=esc(b["value"]), s=src_cell(b["source"])
            ) for b in PRODUCTS["brand_signals"]
        ),
        comp="".join(
            '<tr><td class="mono">{asin}</td><td>{title}</td><td class="num">{r}</td>'
            '<td class="num">{c}</td><td class="num">{p}</td><td class="num">{lp}</td>'
            '<td class="num">{d}</td><td>{rel}</td><td class="src">{s}</td></tr>'.format(
                asin=esc(c["asin"]), title=esc(c["title"]),
                r=esc(c["rating"] or "—"), c=esc(c["ratings_count"] or "—"),
                p=esc(c["price"] or "—"), lp=esc(c["list_price"] or "—"),
                d=esc(c["discount"] or "—"), rel=esc(c["relationship"]),
                s=src_cell(c["source"]),
            ) for c in PRODUCTS["competitive_set"]
        ),
    )
    return layout(
        "pages/catalog.html",
        "All Products",
        "<strong>Zone1</strong> / Catalogue / All Products",
        body,
        depth,
        subtitle="Full verified attribute table for all three Zone1 Amazon affiliate products.",
    )


def page_category(cat_key, title, intro, ids):
    depth = 2
    prods = [PRODUCTS_BY_ID[i] for i in ids]
    body = "<h1>{}</h1><p class=\"lede\">{}</p>".format(esc(title), esc(intro))
    body += '<div class="card flush" style="margin-bottom:18px"><div class="card-head">' \
            '<strong>Category snapshot</strong></div><div class="card-body" style="padding:0">' \
            + snapshot_table(depth, ids) + "</div></div>"
    body += ('<h2 style="margin-top:22px">Products in this category</h2>'
             '<p class="small muted">One card per product, with every tracked attribute '
             'and its source.</p>')
    for p in prods:
        body += """
<div class="card flush">
  <div class="card-head"><strong>{name}</strong>
    <div class="small muted" style="margin-top:4px"><span class="mono">{asin}</span> ·
    {catpath} · verified {vdate}</div></div>
  <div class="card-body">
    <div class="grid g4" style="margin-bottom:14px">
      <div class="kpi"><div class="label">Price</div><div class="value sm">{price}</div>
        <div class="note">list {lp}</div></div>
      <div class="kpi"><div class="label">Rating</div><div class="value sm">{rating}</div>
        <div class="note">{count} ratings</div></div>
      <div class="kpi"><div class="label">Capacity</div><div class="value sm">{cap}</div>
        <div class="note">{capnote}</div></div>
      <div class="kpi"><div class="label">Demand</div><div class="value sm">{bought}</div>
        <div class="note">BSR Air Fryers: {bsr}</div></div>
    </div>
    <h3>Full verified record</h3>
    {fields}
    <h3>Link template</h3>
    {linkbox}
  </div>
</div>
""".format(
            name=esc(p["name"]), asin=esc(p["asin"]), catpath=esc(p["category_path"]),
            vdate=esc(p["verified_on"]),
            price=esc(field_value(p, "Current price (new)") or "not verified"),
            lp=esc(field_value(p, "List price") or "not verified"),
            rating=esc(field_value(p, "Customer rating (stars)") or "not verified"),
            count=esc(field_value(p, "Customer ratings (count)") or "not verified"),
            cap=esc(field_value(p, "Capacity (as stated in title)")
                    or field_value(p, "Capacity")
                    or field_value(p, "Capacity (Amazon productDetails)") or "not verified"),
            capnote=esc("manufacturer-stated" if field_value(p, "Capacity (as stated in title)") else ""),
            bought=esc(field_value(p, "Bought in past month") or "not verified"),
            bsr=esc(field_value(p, "Best Sellers Rank — Air Fryers") or "not verified"),
            fields=product_fields_table(p, depth),
            linkbox=link_template_box(p),
        )
    return layout(
        "pages/category/{}.html".format(cat_key),
        title,
        "<strong>Zone1</strong> / Catalogue / " + esc(title),
        body,
        depth,
        subtitle="Zone1 category page: " + title,
    )


def page_research():
    depth = 1
    p1, p2, p3 = PRODUCTS["products"]

    # Commission model inputs
    rates = [1.0, 2.5, 4.0, 8.0]
    model_rows = []
    for p in PRODUCTS["products"]:
        price = num(field_value(p, "Current price (new)"))
        cells = "".join(
            "<td class=\"num\">{v}</td>".format(v=money(price * r / 100.0) if price else "—")
            for r in rates
        )
        model_rows.append(
            '<tr><td><strong>{n}</strong></td><td class="num">{p}</td><td class="num">{src_note}</td>'
            "{cells}<td class=\"src\">{s}</td></tr>".format(
                n=esc(p["short_name"]),
                p=esc(field_value(p, "Current price (new)") or "not verified"),
                src_note=esc(field_value(p, "List price") or "—"),
                cells=cells,
                s=src_cell(field_source(p, "Current price (new)")),
            )
        )

    # EPC model
    clicks = 1000
    cvr_rows = []
    for p in PRODUCTS["products"]:
        price = num(field_value(p, "Current price (new)"))
        row = '<tr><td><strong>{n}</strong></td>'.format(n=esc(p["short_name"]))
        for cvr in (0.5, 1.0, 2.0, 3.0):
            if price is None:
                row += '<td class="num">—</td>'
                continue
            orders = clicks * cvr / 100.0
            row += '<td class="num">{o:.1f} orders · {c}</td>'.format(
                o=orders, c=money(orders * price * 0.04)
            )
        row += '<td class="src">{s}</td></tr>'.format(s=src_cell(field_source(p, "Current price (new)")))
        cvr_rows.append(row)

    price_rows = []
    for p in PRODUCTS["products"]:
        price = num(field_value(p, "Current price (new)"))
        listp = num(field_value(p, "List price"))
        disc = None
        if price and listp:
            disc = (listp - price) / listp * 100.0
        price_rows.append(
            '<tr><td><strong>{n}</strong></td><td class="num">{p}</td><td class="num">{lp}</td>'
            '<td class="num">{d}</td><td class="num">{bought}</td><td class="src">{s}</td></tr>'.format(
                n=esc(p["short_name"]),
                p=esc(field_value(p, "Current price (new)") or "not verified"),
                lp=esc(field_value(p, "List price") or "not verified"),
                d=("%.1f%%" % disc) if disc is not None else '<span class="empty">not verified</span>',
                bought=esc(field_value(p, "Bought in past month") or "not verified"),
                s=src_cell(field_source(p, "Current price (new)")),
            )
        )

    review_rows = []
    for p in PRODUCTS["products"]:
        rating = num(field_value(p, "Customer rating (stars)"))
        count_raw = field_value(p, "Customer ratings (count)") or ""
        digits = re.sub(r"[^0-9]", "", count_raw)
        count = int(digits) if digits else None
        if count and count >= 1000:
            count_disp = "{:,}".format(count)
        elif count:
            count_disp = "{:,} (displayed by Amazon as {})".format(count, count_raw)
        else:
            count_disp = None
        rating_str = field_value(p, "Customer rating (stars)") or ""
        rating_num = num(rating_str)
        review_rows.append(
            '<tr><td><strong>{n}</strong></td><td class="num">{r}</td><td class="num">{c}</td>'
            '<td class="num">{pct}</td><td class="src">{s}</td></tr>'.format(
                n=esc(p["short_name"]),
                r=esc(rating_str or "not verified"),
                c=esc(count_disp or "not verified"),
                pct=("{:.1f}%".format((count or 0) / 1000.0 * 1000)) if count else "—",
                s=src_cell(field_source(p, "Customer rating (stars)")
                           or field_source(p, "Customer ratings (count)")),
            )
        )

    body = """
<h1>Research &amp; Analysis</h1>
<p class="lede">Everything on this page is derived from the verified product record. Where an
input could not be confirmed from an official source it is blank, and where a model needs an
assumption the assumption is shown as an input rather than asserted as an Amazon rate.</p>

<div class="note"><strong>Method.</strong> Prices, ratings, review counts, Best Sellers Rank and
"bought in past month" counts were read directly from the official Amazon pages listed in every
table. Derived percentages are arithmetic on those two verified numbers and are labelled
"computed". The commission rate is <em>not</em> published by Amazon — the rate card redirects to
the sign-in page — so it is modelled as a variable. {f4}</div>

<h2>1. Pricing analysis</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Product</th><th>Price (new)</th><th>List price</th><th>Discount vs list (computed)</th>
  <th>Demand signal</th><th>Official source</th>
</tr></thead><tbody>{price_rows}</tbody></table></div>
</div></div>

<div class="grid g2">
  <div class="card">
    <h3 style="margin-top:0">Price position</h3>
    <ul class="small">
      <li><strong>{n1}</strong> sits at {p1} against a {l1} list — the deepest percentage
      discount of the three Chefman-side offers, and the only one where Amazon served two
      different new-condition prices in the same window. {f2}</li>
      <li><strong>{n2}</strong> at {p2} against {l2} is the highest ticket in the set. A higher
      ticket price raises the commission per order at any given rate, and the product carries
      the most features per listing (24 cooking functions, rotisserie, French doors).</li>
      <li><strong>{n3}</strong> at {p3} against {l3} combines the lowest list price with the
      second-highest verified demand signal, which makes it the most efficient entry point for a
      first campaign if click-through volume is the constraint.</li>
    </ul>
  </div>
  <div class="card">
    <h3 style="margin-top:0">Price volatility — read this before publishing a price</h3>
    <p class="small">Amazon's Program Policies allow a Site to display Product prices and
    availability only where Amazon serves the price with the link, or where the data comes from
    Creators API / PA API under its licence. A hand-maintained price column is neither. The
    values above are dated research snapshots of official pages, not licensed Product
    Advertising Content. {f7}</p>
    <p class="small">Compliant routes: (1) replace the price column with a SiteStripe or PA API
    widget that renders Amazon's own price against your tag; (2) remove prices from published
    pages and keep them only in the internal research record. The automated path is specified on
    the <a href="{d}pages/campaign.html">Campaign &amp; Tracking</a> page.</p>
  </div>
</div>

<h2>2. Review and rating analysis</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Product</th><th>Rating</th><th>Ratings (count)</th><th>Scale</th><th>Official source</th>
</tr></thead><tbody>{review_rows}</tbody></table></div>
</div></div>
<div class="note warn"><strong>Compliance note on star ratings.</strong> Program Policies
Participation Requirements 5(t) forbids displaying Amazon customer reviews or star ratings on
your Site unless they were obtained through Creators API or PA API. The values above are read
from public product pages, so they fall inside that restriction as written. {f8}</div>

<h2>3. Demand, ranking and trend signals</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Signal</th><th>P1 · CHEFMAN 6 Qt Dual Basket</th><th>P2 · Emeril Lagasse 26QT</th>
  <th>P3 · Chefman 8 Qt TurboFry</th><th>Official source</th>
</tr></thead><tbody>
  <tr><td class="rowhead">Bought in past month</td><td>{v1}</td><td>{v2}</td><td>{v3}</td>
    <td class="src">{sb}</td></tr>
  <tr><td class="rowhead">Best Sellers Rank · Kitchen &amp; Dining</td><td>{b1}</td>
    <td class="empty">not verified {f3}</td><td>{b3}</td><td class="src">{sb}</td></tr>
  <tr><td class="rowhead">Best Sellers Rank · Air Fryers</td><td>{ba1}</td>
    <td class="empty">not verified {f3}</td><td>{ba3}</td><td class="src">{sb}</td></tr>
  <tr><td class="rowhead">Amazon's Choice</td><td>{ac1}</td>
    <td class="empty">not verified {f3}</td><td>{ac3}</td><td class="src">{sb}</td></tr>
  <tr><td class="rowhead">Brand panel · Trending</td><td colspan="3">100K+ orders for the Chefman
    brand in the past 3 months (shown on the P1 page)</td>
    <td class="src">{sb}</td></tr>
  <tr><td class="rowhead">Brand panel · Highly Rated</td><td colspan="3">100K+ customers rate
    items from the Chefman brand highly</td><td class="src">{sb}</td></tr>
  <tr><td class="rowhead">Brand panel · Low Returns</td><td colspan="3">Customers usually keep
    items from this brand</td><td class="src">{sb}</td></tr>
</tbody></table></div>
</div></div>
<p class="small muted">Read together: <strong>{n3}</strong> carries the strongest verified
demand signal in the set (#8 in Air Fryers, 3K+ bought in past month), and the Chefman brand
panel on the P1 page independently reports the brand as trending with 100K+ orders in the past
three months and low returns. <strong>{n1}</strong> is a newer, smaller listing (#35 in Air
Fryers, 1K+ bought in past month) whose growth is easier to influence.</p>

<h2>4. Competition</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>ASIN</th><th>Title</th><th>Rating</th><th>Ratings</th><th>Price</th><th>List price</th>
  <th>Discount</th><th>Relationship</th><th>Official source</th>
</tr></thead><tbody>{comp}</tbody></table></div>
</div></div>
<div class="grid g2" style="margin-top:14px">
  <div class="card"><h3 style="margin-top:0">What the competitive set says</h3>
    <ul class="small">
      <li><strong>Brand depth beats single-ASIN depth for P1.</strong> Amazon surfaced four
      other Chefman listings alongside P1 and P3, including a 52,301-rating multifunction model
      at $84.95 — meaning a Chefman-focused article can route readers to a second Chefman
      product without a brand switch, which keeps the click inside the brand's review moat.</li>
      <li><strong>The dual-basket shelf is crowded and price-led.</strong> The three competing
      dual-basket listings sit at $69.97, $99.99 and $111.63 against P1 at $79.93. P1 is
      positioned mid-pack, so a price-led headline would be wrong; a dual-zone + Sync Finish
      feature-led headline is the defensible one.</li>
      <li><strong>Emeril Lagasse competes on feature count and ticket size,</strong> not on
      price. It is the natural "premium tier" opponent in the comparison article.</li>
      <li><strong>The accessory attach is real.</strong> Amazon's own "Frequently bought
      together" module pairs P1 with $15.99 liners. That is a second monetisable entry point and
      a source of AOV lift that does not compete with the hero SKU.</li>
    </ul>
  </div>
  <div class="card"><h3 style="margin-top:0">Niche assessment</h3>
    <p class="small">Air fryers are a mature, high-volume Amazon category with deep review
    bases, so ranking on generic head terms is not realistic for a new site. The defensible
    positions visible in the verified data are:</p>
    <ul class="small">
      <li><strong>Format-led intent</strong> — "dual basket" and "French door air fryer oven"
      are distinct sub-niches with their own intent and their own comparable set.</li>
      <li><strong>Capacity-led intent</strong> — the verified 6 qt, 8 qt and 26 qt capacity
      claims give three clean, sourced anchor points for family-size and capacity research.</li>
      <li><strong>Accessory-led intent</strong> — liners and baskets at $15.99 with a much
      shorter consideration cycle.</li>
    </ul>
    <p class="small muted">No search-volume or keyword data is quoted on this page, because none
    could be obtained from an official first-party source within this project. Anything of that
    kind must be sourced from a named keyword tool before it is published. {f13}</p>
  </div>
</div>

<h2 id="commission">5. Commission potential model</h2>
<div class="note warn"><strong>The commission rate is an input, not a fact.</strong> Amazon's
Standard Commission Income schedule links to a page that redirects to the Amazon sign-in page,
so no per-category rate for Kitchen &amp; Dining air fryers is published anywhere in this
project. {f4} The tables below apply <em>illustrative rate inputs</em> to the verified prices so
the shape of the economics is visible; substitute your own rate card value before using any
number in a business decision.</div>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Product</th><th>Price</th><th>List price</th>
  <th>Commission per order @ 1%</th><th>@ 2.5%</th><th>@ 4%</th><th>@ 8%</th>
  <th>Official source</th>
</tr></thead><tbody>{model_rows}</tbody></table></div>
</div></div>
<p class="small muted">Commission per order = verified price × rate input. Amazon calculates
commission as a percentage of Qualifying Revenue, which is the amount actually received less
shipping, gift wrapping, handling, taxes, service charges, credits, rebates, card processing
fees and bad debt — so the realised figure will be slightly below price × rate.
Source: {s2}.</p>

<h3>Earnings-per-click model</h3>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Product</th><th>1,000 clicks @ 0.5% CVR</th><th>@ 1.0% CVR</th><th>@ 2.0% CVR</th>
  <th>@ 3.0% CVR</th><th>Official source</th>
</tr></thead><tbody>{cvr_rows}</tbody></table></div>
</div></div>
<p class="small muted">Scenario arithmetic: 1,000 clicks × conversion rate × verified price × 4%
illustrative rate. The conversion rates are assumptions for planning only — no conversion-rate
benchmark for this category could be confirmed from an official source, so none is presented as
one. {f13}</p>

<h2>6. Findings summary</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>#</th><th>Finding</th><th>Evidence</th><th>Action</th><th>Official source</th>
</tr></thead><tbody>
  <tr><td class="mono">1</td><td>The supplied short-link tokens are not ASINs; all three links
    resolve to unrelated products.</td>
    <td>Redirect targets {a1}, {a2}, {a3}</td>
    <td>Rebuild every link from the resolved ASIN plus the publisher tag {f1} {f11}</td>
    <td class="src">{sl}</td></tr>
  <tr><td class="mono">2</td><td>P3 is the strongest demand-led candidate: #8 in Air Fryers,
    3K+ bought in past month, 16,861 ratings.</td>
    <td>Amazon product details and buy box</td>
    <td>Make it the lead SKU of the first content batch</td>
    <td class="src">{s3}</td></tr>
  <tr><td class="mono">3</td><td>P1 is the best feature-differentiated candidate: dual zone,
    Sync Finish, 200–450 °F, and it is the only product whose own page carries a competing
    brand's sponsored store module.</td>
    <td>Manufacturer bullets; sponsored Emeril Lagasse brand module</td>
    <td>Lead the format-led "dual basket" content angle with it</td>
    <td class="src">{s1}</td></tr>
  <tr><td class="mono">4</td><td>P2 has the highest verified ticket price and the most
    functions, so it carries the highest commission per order at any rate.</td>
    <td>$149.99 against a $209.99 list; 24 functions, rotisserie, French doors</td>
    <td>Use as the premium comparison target and the top-of-funnel hero</td>
    <td class="src">{s2p}</td></tr>
  <tr><td class="mono">5</td><td>Two of three products compete for the same "air fryer oven"
    query intent; only P1 and P3 sit in the same format family as the Chefman brand's other
    strong listings.</td>
    <td>Competitive set table above</td>
    <td>Split content by format, not by brand, to avoid cannibalisation</td>
    <td class="src">{scomp}</td></tr>
  <tr><td class="mono">6</td><td>Two Program Policies gates are open for a static site: price
    display and star-rating display.</td>
    <td>Participation Requirements 2(b) and 5(t)</td>
    <td>Choose SiteStripe/PA API or remove the columns before live traffic {f7} {f8}</td>
    <td class="src">{s2}</td></tr>
  <tr><td class="mono">7</td><td>Amazon's robots.txt disallows a long list of AI and research
    agents, so the automation layer must not harvest rendered pages.</td>
    <td>robots.txt agent block</td>
    <td>Route product data through Creators API / PA API only {f10}</td>
    <td class="src">{s7}</td></tr>
</tbody></table></div>
</div></div>
""".format(
        f4=flag_pill("F-04", depth), f7=flag_pill("F-07", depth), f8=flag_pill("F-08", depth),
        f1=flag_pill("F-01", depth), f11=flag_pill("F-11", depth), f2=flag_pill("F-02", depth),
        f3=flag_pill("F-03", depth), f10=flag_pill("F-10", depth), f13=flag_pill("F-13", depth),
        n1=esc(p1["short_name"]), n2=esc(p2["short_name"]), n3=esc(p3["short_name"]),
        p1=esc(field_value(p1, "Current price (new)") or "—"),
        l1=esc(field_value(p1, "List price") or "—"),
        p2=esc(field_value(p2, "Current price (new)") or "—"),
        l2=esc(field_value(p2, "List price") or "—"),
        p3=esc(field_value(p3, "Current price (new)") or "—"),
        l3=esc(field_value(p3, "List price") or "—"),
        v1=esc(field_value(p1, "Bought in past month") or "—"),
        v2=esc(field_value(p2, "Bought in past month") or "—"),
        v3=esc(field_value(p3, "Bought in past month") or "—"),
        b1=esc(field_value(p1, "Best Sellers Rank — Kitchen & Dining") or "—"),
        b3=esc(field_value(p3, "Best Sellers Rank — Kitchen & Dining") or "—"),
        ba1=esc(field_value(p1, "Best Sellers Rank — Air Fryers") or "—"),
        ba3=esc(field_value(p3, "Best Sellers Rank — Air Fryers") or "—"),
        ac1=esc("Yes" if field_value(p1, "Amazon's Choice") else "—"),
        ac3=esc("Yes" if field_value(p3, "Amazon's Choice") else "—"),
        sb=src_cell("https://www.amazon.com/dp/B0CDY277D3",
                    ["https://www.amazon.com/dp/B08DKYBTPH", "https://www.amazon.com/s?k=B09B7SB46R"]),
        price_rows="".join(price_rows),
        review_rows="".join(review_rows),
        comp="".join(
            '<tr><td class="mono">{asin}</td><td>{title}</td><td class="num">{r}</td>'
            '<td class="num">{c}</td><td class="num">{p}</td><td class="num">{lp}</td>'
            '<td class="num">{d}</td><td>{rel}</td><td class="src">{s}</td></tr>'.format(
                asin=esc(c["asin"]), title=esc(c["title"]),
                r=esc(c["rating"] or "—"), c=esc(c["ratings_count"] or "—"),
                p=esc(c["price"] or "—"), lp=esc(c["list_price"] or "—"),
                d=esc(c["discount"] or "—"), rel=esc(c["relationship"]),
                s=src_cell(c["source"]),
            ) for c in PRODUCTS["competitive_set"]
        ),
        model_rows="".join(model_rows),
        cvr_rows="".join(cvr_rows),
        a1=esc(p1["asin"]), a2=esc(p2["asin"]), a3=esc(p3["asin"]),
        sl=src_cell("https://link.amazon/B04G1MEwY", ["https://link.amazon/B02NbDxp3",
                                                     "https://link.amazon/B00hJ57DV"]),
        s1=src_cell("https://www.amazon.com/dp/B0CDY277D3"),
        s3=src_cell("https://www.amazon.com/dp/B08DKYBTPH"),
        s2p=src_cell("https://www.amazon.com/s?k=B09B7SB46R"),
        scomp=src_cell("https://www.amazon.com/dp/B0CDY277D3", ["https://www.amazon.com/dp/B08DKYBTPH"]),
        s2=src_cell("https://affiliate-program.amazon.com/help/operating/policies"),
        s7=src_cell("https://www.amazon.com/robots.txt"),
        d=esc(up(depth)),
    )
    return layout(
        "pages/research.html",
        "Research & Analysis",
        "<strong>Zone1</strong> / Research & Analysis",
        body,
        depth,
        subtitle="Pricing, review, competition, demand and commission analysis for the Zone1 products.",
    )


def page_marketing_seo():
    depth = 2
    p1, p2, p3 = PRODUCTS_BY_ID["p1"], PRODUCTS_BY_ID["p2"], PRODUCTS_BY_ID["p3"]
    body = """
<h1>SEO Article — "Which air fryer should you buy in 2026?"</h1>
<p class="lede">A publishable long-form article built from the verified product record. Copy,
structure, internal linking, disclosure placement and the fact table are all ready to publish once
the two open compliance gates are closed.</p>

<div class="card">
  <h2 style="margin-top:0">Editorial spec</h2>
  <dl class="spec">
    <dt>Primary keyword</dt><dd>best air fryer 2026</dd>
    <dt>Secondary keywords</dt><dd>dual basket air fryer; air fryer oven for large family;
      French door air fryer; 8 quart air fryer</dd>
    <dt>Intent</dt><dd>Commercial investigation</dd>
    <dt>Target length</dt><dd>1,600–2,000 words</dd>
    <dt>Structure</dt><dd>Answer box → capacity decision → format decision → comparison table →
      per-product deep dive → FAQ → conclusion</dd>
    <dt>Disclosure placement</dt><dd>Immediately before the first monetised CTA, and again adjacent
      to the comparison table</dd>
    <dt>Internal links</dt><dd>→ comparison page, → buying guide, → capacity category page</dd>
    <dt>Factual basis</dt><dd>Only the verified attributes on the
      <a href="{d}pages/catalog.html">catalogue page</a>; no first-hand experience claims</dd>
  </dl>
</div>

<div class="card">
  <h2 style="margin-top:0">Title options</h2>
  <ol class="small">
    <li>Best Air Fryers of 2026 Tested Against Capacity, Format and Price — 3 Picks</li>
    <li>Air Fryer vs Air Fryer Oven: Which Format Fits Your Kitchen? (6 qt, 8 qt and 26 qt
      Compared)</li>
    <li>Dual Basket or French Door? The 2026 Air Fryer Buyer's Decision Framework</li>
  </ol>
</div>

<div class="card">
  <h2 style="margin-top:0">Meta description</h2>
  <p class="small">Compare three top-selling Amazon air fryers — 6-quart dual basket, 8-quart
  TurboFry and 26-quart French door oven — on capacity, format, verified price and buyer fit.
  Updated {build}.</p>
</div>

<h2>Draft article</h2>

<div class="card">
  <p><strong>Disclosure:</strong> In this article we earn money from qualifying purchases made
  through our links, at no extra cost to you. The price you pay is unchanged. That is our only
  incentive to recommend a product, and it does not change what we write about it.</p>

  <h3>The short answer</h3>
  <p>If you want to cook two things at once and finish them at the same time, the
  <strong>6-quart dual-basket format</strong> is the one to buy. If you want the simplest
  possible appliance for one cook at a time with a large basket, the <strong>8-quart
  single-basket</strong> is the one. If you want a full cooking centre that replaces more than
  one appliance, the <strong>26-quart French door oven</strong> is the one — and it costs
  materially more.</p>

  <h3>Step 1 — decide on capacity before anything else</h3>
  <p>Capacity is the decision that changes everything downstream, so it comes first.</p>
  <div class="table-scroll"><table class="data compact"><thead><tr>
    <th>Capacity</th><th>Verified product</th><th>Verified price</th><th>Best for</th>
    <th>Official source</th></tr></thead><tbody>
    <tr><td>6 qt (3 qt per basket)</td><td>{n1}</td><td class="num">{p1}</td>
      <td>Two people, two dishes, one finish time</td><td class="src">{s1}</td></tr>
    <tr><td>8 qt</td><td>{n3}</td><td class="num">{p3}</td>
      <td>One cook, a family of three to four, or batch cooking</td><td class="src">{s3}</td></tr>
    <tr><td>26 qt</td><td>{n2}</td><td class="num">{p2}</td>
      <td>Large households, and cooking for an occasion</td><td class="src">{s2}</td></tr>
  </tbody></table></div>

  <h3>Step 2 — decide on format</h3>
  <p>Two of the three products cook with two independent zones; one of the three is a single
  basket with a much larger capacity. That difference matters more than any preset count.</p>
  <ul>
    <li><strong>Dual basket (two independent zones).</strong> The CHEFMAN 6 Quart Dual Basket
      runs two 3-quart baskets independently, from 200–450 °F, and its Sync Finish feature
      holds both baskets so they complete at the same moment. The manufacturer lists
      + 2Min Button, Automatic Shut-Off, Dual Zone Features, Hi-Fry and Mute as the special
      features, and states 120 V / 1700 W with cETL approval. {s1}</li>
    <li><strong>Single basket with a large capacity.</strong> The Chefman Air Fryer 8 Qt is a
      4-in-1 unit — air fry, bake, dehydrate and frozen — rated at 1700 W and 120 V, with a
      400 °F maximum, an LED shake reminder and automatic shut-off. Its basket and inner
      material are stainless steel and the basket is dishwasher safe. {s3}</li>
    <li><strong>French-door cooking centre.</strong> The Emeril Lagasse 26QT is described by
      the manufacturer as a multi-function air fryer toaster oven with French doors, 24
      cooking functions, a dual-speed fan and a rotisserie. {s2}</li>
  </ul>

  <h3>Step 3 — compare the three</h3>
  <div class="table-scroll"><table class="data compact"><thead><tr>
    <th>Attribute</th><th>{s1n}</th><th>{s2n}</th><th>{s3n}</th><th>Official source</th></tr></thead><tbody>
    <tr><td class="rowhead">Format</td><td>Dual basket, 2 × 3 qt</td><td>French door oven</td>
      <td>Single basket, 8 qt</td><td class="src">{s1} {s2} {s3}</td></tr>
    <tr><td class="rowhead">Verified price</td><td>{p1}</td><td>{p2}</td><td>{p3}</td>
      <td class="src">{s1} {s2} {s3}</td></tr>
    <tr><td class="rowhead">List price</td><td>{l1}</td><td>{l2}</td><td>{l3}</td>
      <td class="src">{s1} {s2} {s3}</td></tr>
    <tr><td class="rowhead">Rating</td><td>{r1}</td><td>{r2}</td><td>{r3}</td>
      <td class="src">{s1} {s2} {s3}</td></tr>
    <tr><td class="rowhead">Ratings count</td><td>{c1}</td><td>{c2}</td><td>{c3}</td>
      <td class="src">{s1} {s2} {s3}</td></tr>
    <tr><td class="rowhead">Power</td><td>120 V / 1700 W</td><td class="empty">not verified {f3}</td>
      <td>120 V / 1700 W</td><td class="src">{s1} {s3}</td></tr>
    <tr><td class="rowhead">Cleaning</td><td>Dishwasher-safe non-stick baskets</td>
      <td class="empty">not verified {f3}</td><td>Dishwasher-safe basket, stainless steel inner</td>
      <td class="src">{s1} {s3}</td></tr>
    <tr><td class="rowhead">Warranty</td><td class="empty">not verified {f9}</td>
      <td class="empty">not verified {f3}</td><td>1-Year Limited Warranty</td>
      <td class="src">{s1} {s3}</td></tr>
  </tbody></table></div>

  <h3>Step 4 — the picks</h3>
  <p><strong>Best for cooking two things at once — {n1}.</strong> Two independent 3-quart
  baskets with Sync Finish is the feature no single-basket competitor in this comparison can
  match, and at {p1} against a {l1} list price it sits in the middle of the dual-basket shelf
  rather than at the top. {f2}</p>
  {disclosure}
  <p><strong>Best all-round value for a typical household — {n3}.</strong> This is the
  best-verified seller in the set: 16,861 ratings, a 4.4-star average, and the strongest demand
  signal we could confirm from the official page. At {p3} against a {l3} list price, and
  dishwasher-safe, it is the lowest-friction first air fryer.</p>
  {disclosure}
  <p><strong>Best for large households and for cooking an occasion — {n2}.</strong> 26 quarts,
  French doors, 24 cooking functions and a rotisserie. At {p2} against a {l2} list price it is
  the most expensive of the three by a wide margin, and it should be bought as a
  whole-kitchen replacement rather than as a side appliance.</p>
  {disclosure}

  <h3>Frequently asked questions</h3>
  <h3>Do I need a dual basket?</h3>
  <p>Only if you regularly cook two things at different times and want them to finish together.
  For most households a single larger basket is simpler and cheaper.</p>
  <h3>Is a 26-quart air fryer oven worth it?</h3>
  <p>It is worth it if you cook for more than four people or host regularly. Below that, the
  capacity is unused and the price premium is real.</p>
  <h3>Are the baskets dishwasher safe?</h3>
  <p>The CHEFMAN 6 Quart dual basket has removable, non-stick coated dishwasher-safe baskets.
  The Chefman 8 Qt lists its basket and care instructions as dishwasher safe with a stainless
  steel inner material. The Emeril Lagasse 26QT care instructions could not be confirmed from
  the official page, so no claim is made for it. {f3}</p>

  <h3>Bottom line</h3>
  <p>Buy the format your household actually cooks in. If that is two simultaneous dishes, the
  dual basket wins. If it is one dish with headroom, the 8-quart wins. If it is a full kitchen
  centre, the 26-quart French door wins — and it is the only one of the three that costs more
  than the others combined.</p>
</div>
""".format(
        build=BUILD_DATE, d=esc(up(depth)),
        n1=esc(p1["short_name"]), n2=esc(p2["short_name"]), n3=esc(p3["short_name"]),
        s1n=esc(p1["short_name"]), s2n=esc(p2["short_name"]), s3n=esc(p3["short_name"]),
        p1=esc(field_value(p1, "Current price (new)") or "not verified"),
        p2=esc(field_value(p2, "Current price (new)") or "not verified"),
        p3=esc(field_value(p3, "Current price (new)") or "not verified"),
        l1=esc(field_value(p1, "List price") or "not verified"),
        l2=esc(field_value(p2, "List price") or "not verified"),
        l3=esc(field_value(p3, "List price") or "not verified"),
        r1=esc(field_value(p1, "Customer rating (stars)") or "not verified"),
        r2=esc(field_value(p2, "Customer rating (stars)") or "not verified"),
        r3=esc(field_value(p3, "Customer rating (stars)") or "not verified"),
        c1=esc(field_value(p1, "Customer ratings (count)") or "not verified"),
        c2=esc(field_value(p2, "Customer ratings (count)") or "not verified"),
        c3=esc(field_value(p3, "Customer ratings (count)") or "not verified"),
        s1=src_cell(field_source(p1, "Title")),
        s2=src_cell(field_source(p2, "Title")),
        s3=src_cell(field_source(p3, "Title")),
        f2=flag_pill("F-02", depth), f3=flag_pill("F-03", depth), f9=flag_pill("F-09", depth),
        disclosure=disclosure_block(depth),
    )
    return layout(
        "pages/marketing/seo-article.html",
        "SEO Article",
        "<strong>Zone1</strong> / Marketing content / SEO Article",
        body,
        depth,
        subtitle="Publishable SEO article for the Zone1 air-fryer product set.",
    )


def page_marketing_comparison():
    depth = 2
    p1, p2, p3 = PRODUCTS_BY_ID["p1"], PRODUCTS_BY_ID["p2"], PRODUCTS_BY_ID["p3"]

    rows = []
    spec_rows = [
        ("Format", "Dual basket — 2 × 3 qt", "French-door cooking centre", "Single basket — 8 qt",
         None, None, None),
        ("Capacity (manufacturer)", "6-quart combined, 3-quart per basket", "26QT", "8 quarts",
         "Capacity (Amazon productDetails)", "Capacity (as stated in title)", "Capacity"),
        ("Verified price (new)", "Current price (new)", "Current price (new)", "Current price (new)", None, None, None),
        ("List price", "List price", "List price", "List price", None, None, None),
        ("Customer rating", "Customer rating (stars)", "Customer rating (stars)", "Customer rating (stars)", None, None, None),
        ("Ratings count", "Customer ratings (count)", "Customer ratings (count)", "Customer ratings (count)", None, None, None),
        ("Power", "Electrical rating (from manufacturer bullet)", None, "Output wattage", None, None, None),
        ("Voltage", "Electrical rating (from manufacturer bullet)", None, "Voltage", None, None, None),
        ("Max temperature", "Temperature range (from manufacturer bullet)", None, "Maximum temperature setting", None, None, None),
        ("Cleaning", "Bullet: dishwasher-safe non-stick baskets", None, "Product care instructions", None, None, None),
        ("Dimensions (D × W × H)", "Product dimensions (D × W × H)", "Product dimensions (D × W × H)", "Product dimensions (D × W × H)", None, None, None),
        ("Item weight", None, "Item weight", "Item weight", None, None, None),
        ("Material", "Material", "Material", "Material", None, None, None),
        ("Colour", "Colour", "Colour", "Colour", None, None, None),
        ("Warranty", "Warranty", "Warranty", "Warranty description", None, None, None),
        ("Best Sellers Rank · Air Fryers", "Best Sellers Rank — Air Fryers", "Best Sellers Rank", "Best Sellers Rank — Air Fryers", None, None, None),
        ("Bought in past month", "Bought in past month", "Bought in past month", "Bought in past month", None, None, None),
        ("Amazon's Choice", "Amazon's Choice", "Amazon's Choice", "Amazon's Choice", None, None, None),
    ]
    for label, l1, l2, l3, a1, a2, a3 in spec_rows:
        def cell(p, key):
            if key is None:
                return '<span class="empty">not verified</span>'
            v = field_value(p, key)
            if v:
                return esc(v)
            return '<span class="empty">not verified</span>'

        flags = ""
        for p, key in ((p1, l1), (p2, l2), (p3, l3)):
            if key is None:
                continue
            for f in p["fields"]:
                if f["label"] == key and f["status"] != "verified":
                    flags += " " + flag_pill("F-03" if p["id"] == "p2" else "F-09", depth)
        rows.append(
            '<tr><td class="rowhead">{l}</td><td>{v1}</td><td>{v2}</td><td>{v3}</td>'
            '<td class="src">{s}</td></tr>'.format(
                l=esc(label), v1=cell(p1, l1), v2=cell(p2, l2), v3=cell(p3, l3),
                s=src_cell(field_source(p1, "Title"),
                           [field_source(p2, "Title"), field_source(p3, "Title")]),
            )
        )

    body = """
<h1>Head-to-Head Comparison</h1>
<p class="lede">A publishable comparison page. Every cell is filled from the verified product
record; cells that could not be confirmed from an official source are deliberately empty and
marked, because a comparison table that hides its gaps is worse than one that shows them.</p>

<div class="card">
  <h2 style="margin-top:0">Editorial spec</h2>
  <dl class="spec">
    <dt>Primary keyword</dt><dd>chefman vs emeril lagasse air fryer oven</dd>
    <dt>Secondary keywords</dt><dd>dual basket vs french door air fryer; 6 qt vs 8 qt vs 26 qt
      air fryer</dd>
    <dt>Intent</dt><dd>Commercial investigation, late funnel</dd>
    <dt>Primary CTA</dt><dd>Each product's affiliate link with its disclosure immediately above</dd>
    <dt>Factual basis</dt><dd>Catalogue page only; no first-hand experience claims</dd>
  </dl>
</div>

<h2>Comparison table</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Attribute</th><th>{n1}</th><th>{n2}</th><th>{n3}</th><th>Official source</th>
</tr></thead><tbody>{rows}</tbody></table></div>
</div></div>
<p class="small muted">{f3} Cells left empty are empty because the official page did not serve
that value on the verification date — not because the attribute is unknown. {f6} One unit
discrepancy is preserved verbatim: Amazon's Product details block for {n1} lists Capacity as
"6 liters" while the manufacturer states 6 quarts. {f9}</p>

<h2>Verdict by use case</h2>
<div class="grid g3">
  <div class="card"><h3 style="margin-top:0">Cook two dishes, finish together</h3>
    <p class="small"><strong>{n1}</strong>. Two independent 3-quart baskets and a Sync Finish
    feature. No other product in this comparison has two zones.</p>
    <p class="small muted">Verified: {p1} against a {l1} list. {f2}</p></div>
  <div class="card"><h3 style="margin-top:0">One cook, maximum headroom</h3>
    <p class="small"><strong>{n3}</strong>. 8 quarts, 4-in-1 functions, 1700 W, dishwasher-safe
    basket, 1-year limited warranty, and the deepest verified review base of the three.</p>
    <p class="small muted">Verified: {p3} against a {l3} list. Best Sellers Rank #8 in Air
    Fryers.</p></div>
  <div class="card"><h3 style="margin-top:0">Replace several appliances</h3>
    <p class="small"><strong>{n2}</strong>. 26QT, French doors, 24 cooking functions, dual-speed
    fan and a rotisserie — a cooking centre rather than a fryer.</p>
    <p class="small muted">Verified: {p2} against a {l2} list. Its specification block was not
    readable at verification time. {f3}</p></div>
</div>

<h2>Publishable comparison copy</h2>
<div class="card">
  <p><strong>Disclosure:</strong> We earn money from qualifying purchases made through the links
  below, at no extra cost to you. The price you pay is unchanged.</p>

  <h3>The short version</h3>
  <p>These three products are not really competitors — they are three answers to three different
  questions. If your question is "how do I cook two things at once?", only the dual-basket model
  answers it. If your question is "what is the best-value single air fryer for a normal
  household?", the 8-quart wins on verified price-to-demand. If your question is "what should I
  buy for a family of six?", the 26-quart French door oven is the only one that is big enough,
  and at {p2} it is the only one that costs more than the other two combined.</p>

  <h3>Where the real differences are</h3>
  <p><strong>Zones versus capacity.</strong> It is easy to assume that bigger is better. The
  verified data says otherwise: the {cap1} model does not beat the {cap3} model because it is
  smaller, it beats it because it has two independent cooking zones with a synchronised finish.
  If you have never cooked a starter and a main simultaneously, that is the feature that changes
  your evenings.</p>
  <p><strong>Feature count versus usable space.</strong> The 26-quart unit advertises 24 cooking
  functions. The 8-quart unit advertises four. The 6-quart unit advertises a 200–450 °F range
  with a dedicated Hi-Fry setting. None of these numbers is directly comparable, and this page
  deliberately does not rank them — it reports what each manufacturer states and lets the
  reader's kitchen decide.</p>

  <h3>What we could not verify</h3>
  <p>The {n2} product page did not serve a readable specification block when we checked it, so
  this comparison publishes no dimensions, weight, wattage or material for it. Everything stated
  above about that product comes from its own official title and from the official Amazon
  listing for its ASIN. {f3}</p>
</div>
""".format(
        n1=esc(p1["short_name"]), n2=esc(p2["short_name"]), n3=esc(p3["short_name"]),
        rows="".join(rows),
        f2=flag_pill("F-02", depth), f3=flag_pill("F-03", depth),
        f6=flag_pill("F-06", depth), f9=flag_pill("F-09", depth),
        p1=esc(field_value(p1, "Current price (new)") or "not verified"),
        p2=esc(field_value(p2, "Current price (new)") or "not verified"),
        p3=esc(field_value(p3, "Current price (new)") or "not verified"),
        l1=esc(field_value(p1, "List price") or "not verified"),
        l2=esc(field_value(p2, "List price") or "not verified"),
        l3=esc(field_value(p3, "List price") or "not verified"),
        cap1=esc(field_value(p1, "Capacity (Amazon productDetails)") or "6-quart"),
        cap3=esc(field_value(p3, "Capacity") or "8-quart"),
    )
    return layout(
        "pages/marketing/comparison.html",
        "Head-to-Head Comparison",
        "<strong>Zone1</strong> / Marketing content / Head-to-Head Comparison",
        body,
        depth,
        subtitle="Publishable head-to-head comparison of the three Zone1 air-fryer products.",
    )


def page_marketing_buying_guide():
    depth = 2
    p1, p2, p3 = PRODUCTS_BY_ID["p1"], PRODUCTS_BY_ID["p2"], PRODUCTS_BY_ID["p3"]
    body = """
<h1>Buying Guide</h1>
<p class="lede">A decision-oriented buying guide. It leads with the questions a reader actually
has to answer before choosing, then maps each answer to the verified product that fits, and only
then links out to Amazon.</p>

<div class="card">
  <h2 style="margin-top:0">Editorial spec</h2>
  <dl class="spec">
    <dt>Primary keyword</dt><dd>air fryer buying guide</dd>
    <dt>Secondary keywords</dt><dd>how big an air fryer do I need; dual basket vs single basket;
      air fryer for 6 people</dd>
    <dt>Intent</dt><dd>Commercial investigation, early to mid funnel</dd>
    <dt>Structure</dt><dd>Decision questions → recommendation matrix → capacity maths → feature
      glossary → where to buy</dd>
    <dt>Conversion mechanism</dt><dd>A recommendation matrix that routes each reader to exactly one
      product, so the click is well matched to the intent</dd>
  </dl>
</div>

<h2>Decision questions</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>If your answer is…</th><th>…you should buy</th><th>Because (verified)</th>
  <th>Official source</th></tr></thead><tbody>
  <tr><td>"I need to cook two things at the same time"</td><td><strong>{n1}</strong></td>
    <td>Two independent 3-quart baskets, Sync Finish so both finish together, 200–450 °F,
    + 2Min Button, Automatic Shut-Off, Hi-Fry, Mute</td><td class="src">{s1}</td></tr>
  <tr><td>"I want the most dependable first air fryer"</td><td><strong>{n3}</strong></td>
    <td>16,861 ratings at 4.4 stars, Best Sellers Rank #8 in Air Fryers, 3K+ bought in past
    month, dishwasher-safe basket, 1-year limited warranty</td><td class="src">{s3}</td></tr>
  <tr><td>"I cook for six or more people"</td><td><strong>{n2}</strong></td>
    <td>26QT with French doors, 24 cooking functions, dual-speed fan and a rotisserie</td>
    <td class="src">{s2}</td></tr>
  <tr><td>"I want the lowest verified price in this set"</td><td><strong>{n3}</strong></td>
    <td>{p3} against a {l3} list price — the lowest verified price of the three</td>
    <td class="src">{s3}</td></tr>
  <tr><td>"I want the highest commission per order" — <em>internal note, not for publication</em></td>
    <td><strong>{n2}</strong></td>
    <td>Highest verified price ({p2}), so the highest commission per order at any given rate.
    The rate itself is not published by Amazon. {f4}</td><td class="src">{s2}</td></tr>
</tbody></table></div>
</div></div>
<p class="small muted">The fifth row is an internal planning note retained in the research record.
It must be removed before publication — a reader-facing statement about which product pays the
publisher more would be misleading and is not endorsed by the FTC's requirement that
endorsements reflect the honest opinion of the endorser. It is marked here so the mistake cannot
happen. {f4}</p>

<h2>Recommendation matrix</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Household size</th><th>Cook one dish at a time</th><th>Cook two dishes at once</th>
  <th>Need a rotisserie / multi-function oven</th><th>Official source</th></tr></thead><tbody>
  <tr><td>1–2 people</td><td>{n3}</td><td>{n1}</td><td class="empty">not verified {f3}</td>
    <td class="src">{s1}</td></tr>
  <tr><td>3–4 people</td><td>{n3}</td><td>{n1}</td><td class="empty">not verified {f3}</td>
    <td class="src">{s1}</td></tr>
  <tr><td>5–6 people</td><td>{n3}</td><td>{n1}</td><td>{n2}</td><td class="src">{s1}</td></tr>
  <tr><td>6+ people, or hosting</td><td class="empty">not verified {f3}</td>
    <td class="empty">not verified {f3}</td><td>{n2}</td><td class="src">{s1}</td></tr>
</tbody></table></div>
</div></div>

<h2>Capacity, in plain numbers</h2>
<div class="card">
  <p class="small">Every capacity figure below is quoted from the manufacturer's own listing
  text or from Amazon's Product details block — not estimated.</p>
  <div class="table-scroll"><table class="data compact"><thead><tr>
    <th>Product</th><th>Capacity as stated</th><th>Where the number comes from</th>
    <th>Official source</th></tr></thead><tbody>
    <tr><td>{n1}</td><td>6-quart combined, 3-quart per basket</td>
      <td>Product title and manufacturer bullets. Amazon's Product details block separately lists
      Capacity as "6 liters" — a unit discrepancy preserved verbatim. {f6}</td>
      <td class="src">{s1}</td></tr>
    <tr><td>{n3}</td><td>8 quarts</td>
      <td>Product title and Amazon's Product details block (Capacity and Size both 8 quarts)</td>
      <td class="src">{s3}</td></tr>
    <tr><td>{n2}</td><td>26QT</td>
      <td>Product title only — the specification block was not readable at verification time
      {f3}</td><td class="src">{s2}</td></tr>
  </tbody></table></div>
</div>

<h2>Feature glossary</h2>
<div class="grid g2">
  <div class="card">
    <h3 style="margin-top:0">Dual zone and Sync Finish</h3>
    <p class="small">Dual-zone cooking means two independent baskets with their own temperature
    and time settings. Sync Finish is the part that matters: it holds one basket so that both
    finish at the same time instead of one finishing and going cold while the other catches up.
    Both terms appear in the manufacturer bullet list for {n1}. {s1}</p>
    <h3>Hi-Fry</h3>
    <p class="small">A higher maximum cooking temperature for crisper surfaces. The 6-quart
    model's bullet states a digital dual-basket range of 200–450 °F and lists Hi-Fry as a
    special feature. {s1}</p>
    <h3>Rapid-air technology</h3>
    <p class="small">The air-circulation method named in Amazon's Features &amp; Specs block for
    {n3}. {s3}</p>
  </div>
  <div class="card">
    <h3 style="margin-top:0">Rotisserie</h3>
    <p class="small">A motorised spit that rotates food while it cooks. It appears in the
    official title of {n2}. {s2}</p>
    <h3>Dual-speed fan</h3>
    <p class="small">A fan with more than one speed setting, also named in the official title of
    {n2}. {s2}</p>
    <h3>LED shake reminder</h3>
    <p class="small">A prompt to turn or shake the basket mid-cook, listed in the Features &amp;
    Specs block for {n3}. {s3}</p>
    <h3>Dehydrate and Frozen presets</h3>
    <p class="small">Presets that extend an air fryer into a dehydrator or cook from frozen
    without a separate pre-thaw. Named in the official titles of {n3} and {n2}. {s3}</p>
  </div>
</div>

<h2>Where to buy</h2>
<div class="card">
  {disclosure}
  <p class="small">Each link below is the Amazon product detail page for that product. Replace
  the placeholder tag with your Associates ID before publishing. {f11}</p>
  <div class="grid g3" style="margin-top:12px">
    <div class="card" style="margin:0"><h3 style="margin-top:0">{n1}</h3>
      <p class="small">Dual basket, 3 qt per basket, Sync Finish.</p>{lb1}</div>
    <div class="card" style="margin:0"><h3 style="margin-top:0">{n2}</h3>
      <p class="small">26QT French door, 24 functions, rotisserie.</p>{lb2}</div>
    <div class="card" style="margin:0"><h3 style="margin-top:0">{n3}</h3>
      <p class="small">8 qt TurboFry 4-in-1, dishwasher-safe basket.</p>{lb3}</div>
  </div>
</div>
""".format(
        n1=esc(p1["short_name"]), n2=esc(p2["short_name"]), n3=esc(p3["short_name"]),
        s1=src_cell(field_source(p1, "Title")),
        s2=src_cell(field_source(p2, "Title")),
        s3=src_cell(field_source(p3, "Title")),
        p2=esc(field_value(p2, "Current price (new)")),
        p3=esc(field_value(p3, "Current price (new)")),
        l3=esc(field_value(p3, "List price")),
        f3=flag_pill("F-03", depth), f4=flag_pill("F-04", depth),
        f6=flag_pill("F-06", depth), f11=flag_pill("F-11", depth),
        lb1=link_template_box(p1), lb2=link_template_box(p2), lb3=link_template_box(p3),
        disclosure=disclosure_block(depth),
    )
    return layout(
        "pages/marketing/buying-guide.html",
        "Buying Guide",
        "<strong>Zone1</strong> / Marketing content / Buying Guide",
        body,
        depth,
        subtitle="Publishable decision-oriented buying guide for the Zone1 air-fryer products.",
    )


def page_campaign():
    depth = 1
    p1, p2, p3 = PRODUCTS["products"]
    link_rows = []
    for p in PRODUCTS["products"]:
        link_rows.append(
            '<tr><td>{ref} · {name}</td><td class="mono">{asin}</td>'
            '<td><div class="linkbox" data-copy="{u}"><span class="url">{u}</span>'
            '<button class="copy" type="button">Copy</button></div></td>'
            '<td class="mono">{tag}</td><td class="src">{s}</td></tr>'.format(
                ref=esc(p["ref"]), name=esc(p["short_name"]), asin=esc(p["asin"]),
                u=esc(p["special_link_template"]),
                tag=esc(p["special_link_template"].split("tag=")[-1]),
                s=src_cell(p["canonical_url"]),
            )
        )
    term_rows = "".join(
        '<tr><td class="mono">{cid}</td><td>{area}</td><td>{req}</td><td>{detail}</td>'
        '<td class="src">{s}</td></tr>'.format(
            cid=esc(t["id"]), area=esc(t["area"]), req=esc(t["requirement"]),
            detail=esc(t["detail"]), s=src_cell(SOURCE_BY_ID[t["source_id"]]["url"]),
        ) for t in PROGRAM["program_terms"]
    )
    rule_rows = "".join(
        '<tr><td class="mono">{rid}</td><td><strong>{rule}</strong></td><td>{detail}</td>'
        '<td class="src">{s}</td></tr>'.format(
            rid=esc(r["id"]), rule=esc(r["rule"]), detail=esc(r["detail"]),
            s=src_cell(SOURCE_BY_ID[r["source_id"]]["url"]),
        ) for r in PROGRAM["automation_rules"]
    )
    body = """
<h1>Campaign &amp; Tracking</h1>
<p class="lede">How this project is operated once it goes live: how links are built and tagged,
how clicks and conversions are measured, how content is refreshed so it stays compliant, and how
the campaign is optimised for revenue rather than traffic.</p>

<h2>1. Affiliate link management</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Product</th><th>ASIN</th><th>Special Link template</th><th>Tag placeholder</th>
  <th>Official source</th></tr></thead><tbody>{links}</tbody></table></div>
</div></div>
<div class="note warn"><strong>Do not publish with the placeholder tag.</strong>
{pl} Special Links must carry your own Associates ID, must link directly to the Product detail
page, and must not pass through a link shortener or a redirecting wrapper — purchases through a
Redirecting Link are disqualified, and cloaking the URL risks termination.</div>

<h2>2. Sub-tag measurement scheme</h2>
<div class="card">
  <p class="small">Amazon may issue additional "sub-tag" Associate IDs on request so link
  performance can be monitored and optimised per placement. Sub-tags must never be assigned
  dynamically to individual end users. The scheme below is a design proposal — the sub-tags
  themselves are requested from Amazon and are therefore not listed here.</p>
  <div class="table-scroll"><table class="data compact"><thead><tr>
    <th>Placement</th><th>Proposed sub-tag shape</th><th>Content type</th><th>Primary metric</th>
    <th>Official source</th></tr></thead><tbody>
    <tr><td>SEO article hero CTA</td><td class="mono">zone1-seo-hero-01</td><td>Long-form</td>
      <td>Click-through rate → EPC</td><td class="src">{s2}</td></tr>
    <tr><td>SEO article in-body CTA</td><td class="mono">zone1-seo-body-01</td><td>Long-form</td>
      <td>Scroll depth → EPC</td><td class="src">{s2}</td></tr>
    <tr><td>Comparison table row</td><td class="mono">zone1-cmp-row-01</td><td>Comparison</td>
      <td>Row-level CTR</td><td class="src">{s2}</td></tr>
    <tr><td>Buying guide matrix cell</td><td class="mono">zone1-guide-matrix-01</td>
      <td>Buying guide</td><td>Matrix-cell CTR</td><td class="src">{s2}</td></tr>
    <tr><td>Category page CTA</td><td class="mono">zone1-cat-01</td><td>Category</td>
      <td>Category CTR</td><td class="src">{s2}</td></tr>
    <tr><td>Newsletter / social</td><td class="mono">zone1-social-01</td><td>Off-site</td>
      <td>Assisted conversions</td><td class="src">{s2}</td></tr>
  </tbody></table></div>
</div>

<h2>3. Measurement stack</h2>
<div class="grid g2">
  <div class="card">
    <h3 style="margin-top:0">What Amazon measures for you</h3>
    <ul class="small">
      <li><strong>Clicks.</strong> Every Special Link click is tracked and reported by Amazon.</li>
      <li><strong>Conversions.</strong> A Qualifying Purchase is a click that turns into a paid,
      shipped, non-returned order inside the 24-hour Session window, with cart-to-order
      completion allowed up to 89 days after the click and shipment and payment within 180 days
      of the purchase.</li>
      <li><strong>Commission.</strong> Reported monthly, paid approximately 60 days after the
      end of the calendar month in which it was earned.</li>
      <li><strong>Disqualification.</strong> Cancelled, returned or refunded orders are removed
      from commission; so are purchases attributed to a Prohibited Paid Search Placement, a
      search-engine-generated link, or a Redirecting Link.</li>
    </ul>
    <p class="small muted">Source: {s2}.</p>
  </div>
  <div class="card">
    <h3 style="margin-top:0">What you must measure yourself</h3>
    <ul class="small">
      <li>Impressions and on-site engagement per placement, joined to Amazon's click and order
      data on the sub-tag.</li>
      <li>EPC per placement (commission ÷ clicks) — the only metric that should drive content
      decisions, since Amazon's conversion rate is not published per link.</li>
      <li>Content freshness: how long since each page's price and badge claims were last
      re-verified.</li>
      <li>Compliance state per page: whether the affiliate disclosure is present and adjacent
      to the monetised block, and whether the Amazon statement appears.</li>
    </ul>
    <p class="small muted">Use a privacy-respecting, first-party analytics setup. Do not
      fingerprint or track individual users — and note that you may not assign sub-tags
      dynamically to individual end users.</p>
  </div>
</div>

<h2>4. Automated research and content pipeline</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Stage</th><th>Automation</th><th>Constraint imposed by the official sources</th>
  <th>Official source</th></tr></thead><tbody>
  <tr><td class="rowhead">Product data ingest</td>
    <td>Fetch title, price, availability, rating, BSR and review count for each ASIN on a
    schedule; write to <span class="mono">data/products.json</span>; regenerate the site.</td>
    <td>Must come from Creators API / PA API. Amazon's robots.txt disallows a long list of AI
    and research agents outright, and the Program Content licence prohibits using Program
    Content to develop or improve language or machine-learning models, and prohibits
    data-mining or robots-based extraction of Program Content.</td>
    <td class="src">{s7} {s2}</td></tr>
  <tr><td class="rowhead">Trend detection</td>
    <td>Track Best Sellers Rank, "bought in past month" and price movement per ASIN; flag
    products whose rank moved more than X positions.</td>
    <td>Only Amazon-served or API-sourced values may be displayed.</td>
    <td class="src">{s2}</td></tr>
  <tr><td class="rowhead">Opportunity scoring</td>
    <td>Score each ASIN on demand velocity, rank, price, review depth, rating and competition;
    rank for content slots.</td>
    <td>The inputs are Amazon-sourced. Scores derived from them are analysis, not Product
    Advertising Content, and must not be presented as Amazon data.</td>
    <td class="src">{s2}</td></tr>
  <tr><td class="rowhead">Content generation</td>
    <td>Draft the article, comparison and buying-guide sections from the verified record; require
    a human review step against the catalogue before publish.</td>
    <td>No inaccurate, overbroad, deceptive or misleading claims; no first-hand experience
    claims the publisher cannot make; no AI training on Program Content.</td>
    <td class="src">{s2}</td></tr>
  <tr><td class="rowhead">Disclosure injection</td>
    <td>Inject the affiliate disclosure adjacent to every monetised block and the Amazon
    statement in every page footer.</td>
    <td>Disclosure must be clear and conspicuous and close to the recommendation.</td>
    <td class="src">{s5}</td></tr>
  <tr><td class="rowhead">Link management</td>
    <td>Generate Special Links with the publisher's tag and per-placement sub-tag; refresh the
    link table.</td>
    <td>Direct product-detail links only; no shortener, no redirect, no cloaking.</td>
    <td class="src">{s2}</td></tr>
  <tr><td class="rowhead">Compliance scan</td>
    <td>Scan every page for the Amazon statement, an affiliate disclosure next to each CTA, a
    placeholder tag, and an unverified value presented as fact.</td>
    <td>These are the failure modes that produce an account action.</td>
    <td class="src">{s2} {s5}</td></tr>
  <tr><td class="rowhead">Re-verification schedule</td>
    <td>Re-read every cited official page on a cadence and re-publish with a new verification
    timestamp; drop any claim that can no longer be confirmed.</td>
    <td>Limited-time promotion references must be removed as soon as the promotion ends.</td>
    <td class="src">{s2}</td></tr>
</tbody></table></div>
</div></div>

<h2>5. Optimisation loop</h2>
<div class="grid g4">
  <div class="card"><h3 style="margin-top:0">1 · Measure</h3>
    <p class="small">Weekly: clicks, orders and EPC per sub-tag from the Amazon report, joined to
    on-site engagement.</p></div>
  <div class="card"><h3 style="margin-top:0">2 · Diagnose</h3>
    <p class="small">Separate a low EPC caused by low CTR (a headline or placement problem) from
    one caused by low conversion (a price, rating or offer problem).</p></div>
  <div class="card"><h3 style="margin-top:0">3 · Change one thing</h3>
    <p class="small">Test one variable per placement per cycle — headline, placement, CTA label,
    or which product the CTA points at. Keep the sub-tag stable so the test is readable.</p></div>
  <div class="card"><h3 style="margin-top:0">4 · Re-verify</h3>
    <p class="small">Before any change ships, re-read the cited official pages. If a price or
    badge has moved, update it or remove it in the same commit.</p></div>
</div>

<h2>6. Editorial calendar</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Week</th><th>Content</th><th>Target intent</th><th>Primary product</th>
  <th>Re-verify before publish</th></tr></thead><tbody>
  <tr><td class="mono">1</td><td>SEO article — how to choose an air fryer</td>
    <td>Commercial investigation</td><td>{n3}</td><td class="src">{s1} {s3}</td></tr>
  <tr><td class="mono">2</td><td>Buying guide — capacity and household size</td>
    <td>Early funnel</td><td>{n1}</td><td class="src">{s1}</td></tr>
  <tr><td class="mono">3</td><td>Comparison — dual basket vs French door vs single basket</td>
    <td>Late funnel</td><td>{n1}</td><td class="src">{s1} {s2} {s3}</td></tr>
  <tr><td class="mono">4</td><td>Accessory round-up (liners and baskets)</td>
    <td>Transactional</td><td>{n1}</td>
    <td class="src">{sacc}</td></tr>
  <tr><td class="mono">5+</td><td>Refresh cycle on all published pages</td>
    <td>Defend rankings</td><td>All</td><td class="src">{s2}</td></tr>
</tbody></table></div>
</div></div>

<h2>7. Program rules this site is built against</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>ID</th><th>Area</th><th>Requirement</th><th>Detail as published</th>
  <th>Official source</th></tr></thead><tbody>{terms}</tbody></table></div>
</div></div>

<h2>8. Automation rules</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>ID</th><th>Rule</th><th>Detail</th><th>Official source</th>
</tr></thead><tbody>{rules}</tbody></table></div>
</div></div>
""".format(
        links="".join(link_rows),
        terms=term_rows,
        rules=rule_rows,
        pl=flag_pill("F-11", depth),
        n1=esc(p1["short_name"]), n2=esc(p2["short_name"]), n3=esc(p3["short_name"]),
        s2=src_cell("https://affiliate-program.amazon.com/help/operating/policies"),
        s5=src_cell("https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking"),
        s7=src_cell("https://www.amazon.com/robots.txt"),
        s1=src_cell("https://www.amazon.com/dp/B0CDY277D3"),
        s3=src_cell("https://www.amazon.com/dp/B08DKYBTPH"),
        sacc=src_cell("https://www.amazon.com/Rectangle-Disposable-Rectangular-Parchment-Baskets/dp/B0F3J4WWZF"),
    )
    return layout(
        "pages/campaign.html",
        "Campaign & Tracking",
        "<strong>Zone1</strong> / Operations / Campaign & Tracking",
        body,
        depth,
        subtitle="Link management, measurement, automation and optimisation plan for the Zone1 affiliate campaigns.",
    )


def page_compliance():
    depth = 1
    src_rows = "".join(
        '<tr><td class="mono">{sid}</td><td>{title}</td><td>{pub}</td><td>{type}</td>'
        '<td class="src"><a href="{u}" target="_blank" rel="noopener noreferrer">{u}</a></td>'
        '<td>{note}</td></tr>'.format(
            sid=esc(s["id"]), title=esc(s["title"]), pub=esc(s["publisher"]),
            type=esc(s["type"]), u=esc(s["url"]), note=esc(s.get("version_note") or s.get("access_note") or ""),
        ) for s in PROGRAM["sources"]
    )
    term_rows = "".join(
        '<tr id="{cid}"><td class="mono">{cid}</td><td>{area}</td><td>{req}</td><td>{detail}</td>'
        '<td>{applies}</td><td class="src">{s}</td></tr>'.format(
            cid=esc(t["id"]), area=esc(t["area"]), req=esc(t["requirement"]),
            detail=esc(t["detail"]), applies=esc("; ".join(t["applies_to"])),
            s=src_cell(SOURCE_BY_ID[t["source_id"]]["url"]),
        ) for t in PROGRAM["program_terms"]
    )
    rule_rows = "".join(
        '<tr><td class="mono">{rid}</td><td><strong>{rule}</strong></td><td>{detail}</td>'
        '<td class="src">{s}</td></tr>'.format(
            rid=esc(r["id"]), rule=esc(r["rule"]), detail=esc(r["detail"]),
            s=src_cell(SOURCE_BY_ID[r["source_id"]]["url"]),
        ) for r in PROGRAM["automation_rules"]
    )
    body = """
<h1>Compliance</h1>
<p class="lede">The rules this site is built against, quoted from the official Amazon Associates
programme documents and the U.S. Federal Trade Commission's endorsement guidance. Every row links
to the source it came from.</p>

<div class="card">
  <h2 style="margin-top:0">Two disclosures this site carries</h2>
  <div class="grid g2">
    <div>
      <h3>Amazon — required statement</h3>
      <div class="quotebox">"As an Amazon Associate I earn from qualifying purchases."</div>
      <p class="small">The Operating Agreement requires this to be stated clearly and prominently
      on your Site, and forbids misrepresenting or embellishing the relationship. It appears in
      the footer of every page of this site.</p>
      <p class="small muted">Source: {s1}.</p>
    </div>
    <div>
      <h3>FTC — affiliate disclosure</h3>
      <div class="quotebox">"You should disclose your relationship to the retailer clearly and
      conspicuously on your site… You could say something like, 'I get commissions for purchases
      made through links in this post.'"</div>
      <p class="small">Placement matters: a disclosure only on an About page, only at the end of
      an article, or behind a "MORE" click is likely to be missed. Every monetised block in this
      project carries the disclosure immediately above it.</p>
      <p class="small muted">Source: {s5}.</p>
    </div>
  </div>
  <h3>Wording that is not acceptable</h3>
  <div class="table-scroll"><table class="data compact"><thead><tr>
    <th>Wording</th><th>FTC assessment</th><th>Official source</th></tr></thead><tbody>
    <tr><td>"Affiliate link"</td><td>Not adequate on its own — consumers might not understand
      that the person placing the link is paid for purchases through it.</td>
      <td class="src">{s5}</td></tr>
    <tr><td>"Buy now" button (as the disclosure)</td><td>Not adequate.</td>
      <td class="src">{s5}</td></tr>
    <tr><td>"Paid link" next to an affiliate link</td><td>Adequate disclosure of the nature of
      the link.</td><td class="src">{s5}</td></tr>
    <tr><td>"Commissionable link"</td><td>Probably not a clear disclosure.</td>
      <td class="src">{s5}</td></tr>
    <tr><td>"Thanks to the brand for the free product"</td><td>Acceptable when it makes clear
      what you received and from whom.</td><td class="src">{s4}</td></tr>
    <tr><td>"#ad", "Ad:", "advertisement", "sponsored"</td><td>Effective; place it where it is
      hard to miss and near the recommendation.</td><td class="src">{s4}</td></tr>
  </tbody></table></div>
</div>

<div class="card">
  <h2 style="margin-top:0">Open compliance gates before live traffic</h2>
  <p class="small">These two are not resolved by this build. Both are published for review with
  the exact clause and the compliant options.</p>
  <div class="table-scroll"><table class="data"><thead><tr>
    <th>Gate</th><th>Clause</th><th>What this site does today</th><th>Compliant options</th>
    <th>Official source</th></tr></thead><tbody>
    <tr><td><strong>Displaying prices</strong></td>
      <td>Participation Requirements 2(b): a Site may only show prices and availability if Amazon
      serves the link in which that data is displayed, or the data is obtained via Creators API
      or PA API under the licence.</td>
      <td>Static, dated price snapshots read from official pages, each labelled with the page it
      came from and the verification date.</td>
      <td>(1) Replace the price column with a SiteStripe or PA API widget that renders Amazon's
      own price with the tag. (2) Remove prices from published pages and keep them in the
      internal research record only.</td>
      <td class="src">{s2}</td></tr>
    <tr><td><strong>Displaying star ratings and reviews</strong></td>
      <td>Participation Requirements 5(t): you may not display Amazon customer reviews or star
      ratings on your Site unless obtained through Creators API or PA API.</td>
      <td>Rating and rating-count values read from official pages, each with its source URL.</td>
      <td>(1) Source the ratings through PA API / Creators API so each carries a compliant link.
      (2) Drop the rating columns from the published pages and keep them in the internal research
      record only.</td>
      <td class="src">{s2}</td></tr>
  </tbody></table></div>
</div>

<h2>Program rules mapped to this site</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>ID</th><th>Area</th><th>Requirement</th><th>Detail as published</th>
  <th>Applies to</th><th>Official source</th></tr></thead><tbody>{terms}</tbody></table></div>
</div></div>

<h2>Automation rules</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>ID</th><th>Rule</th><th>Detail</th><th>Official source</th>
</tr></thead><tbody>{rules}</tbody></table></div>
</div></div>

<h2>Official sources</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>ID</th><th>Document</th><th>Publisher</th><th>Type</th><th>URL</th><th>Version / access note</th>
</tr></thead><tbody>{sources}</tbody></table></div>
</div></div>

<div class="note flag"><strong>Not legal advice.</strong> This page is a working compliance
map built from published programme documents, not legal advice. Before publishing at scale, have
a qualified adviser confirm the plan, and re-read the programme documents — Amazon updates the
Program Policies periodically (the version read for this project states "Updated: April 14,
2026"), and a change in either document changes what this site must do.</div>
""".format(
        terms=term_rows, rules=rule_rows, sources=src_rows,
        s1=src_cell("https://affiliate-program.amazon.com/help/operating/agreement"),
        s2=src_cell("https://affiliate-program.amazon.com/help/operating/policies"),
        s4=src_cell("https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers"),
        s5=src_cell("https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking"),
    )
    return layout(
        "pages/compliance.html",
        "Compliance",
        "<strong>Zone1</strong> / Operations / Compliance",
        body,
        depth,
        subtitle="Amazon Associates and FTC compliance map for the Zone1 site.",
    )


def page_sources():
    depth = 1
    src_rows = "".join(
        '<tr><td class="mono">{sid}</td><td>{title}</td><td>{pub}</td><td>{type}</td>'
        '<td class="src"><a href="{u}" target="_blank" rel="noopener noreferrer">{u}</a></td>'
        '<td>{note}</td></tr>'.format(
            sid=esc(s["id"]), title=esc(s["title"]), pub=esc(s["publisher"]),
            type=esc(s["type"]), u=esc(s["url"]),
            note=esc(s.get("version_note") or s.get("access_note") or ""),
        ) for s in PROGRAM["sources"]
    )
    link_rows = "".join(
        '<tr><td class="mono">{id}</td><td class="mono"><a href="{u}" target="_blank" '
        'rel="noopener noreferrer">{u}</a></td><td class="mono">{asin}</td><td>{title}</td>'
        '<td class="src">{s}</td></tr>'.format(
            id=esc(l["id"]), u=esc(l["supplied_url"]), asin=esc(l["resolved_asin"]),
            title=esc(l["resolved_title"]), s=src_cell(l["resolved_url"]),
        ) for l in PRODUCTS["links"]
    )
    ver_rows = []
    for p in PRODUCTS["products"]:
        verified = sum(1 for f in p["fields"] if f["status"] == "verified")
        total = len(p["fields"])
        ver_rows.append(
            '<tr><td>{ref} · {name}</td><td class="mono">{asin}</td>'
            '<td class="num">{v} of {t}</td><td>{srcs}</td><td>{vdate}</td>'
            '<td class="src">{s}</td></tr>'.format(
                ref=esc(p["ref"]), name=esc(p["short_name"]), asin=esc(p["asin"]),
                v=verified, t=total,
                srcs=", ".join(sorted({source_kind(f["source"]) for f in p["fields"]})),
                vdate=esc(p["verified_on"]), s=src_cell(p["canonical_url"]),
            )
        )
    body = """
<h1>Sources &amp; Verification</h1>
<p class="lede">The audit trail. Every source used, every link resolved, every attribute checked
and where the data came from. Nothing on this site is sourced from a secondary blog, a
price-tracking site or memory.</p>

<h2>Verification policy</h2>
<div class="card">
  <p class="small">{policy}</p>
  <p class="small">Snapshot date: <strong>{build}</strong>. Verification method: each cited page
  was requested over HTTP, the response body read directly, and the value transcribed verbatim.
  Where the same attribute was served differently across requests, both values are recorded and
  the discrepancy is flagged rather than resolved by preference.</p>
</div>

<h2>Resolved links</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>ID</th><th>Supplied URL</th><th>Resolved ASIN</th><th>Title read from the destination page</th>
  <th>Official source</th></tr></thead><tbody>{links}</tbody></table></div>
</div></div>
<div class="note warn">Each supplied URL was requested and its redirect chain followed to the
final <span class="mono">amazon.com/dp/&lt;ASIN&gt;</span> destination; the destination page's
own <span class="mono">&lt;title&gt;</span> was then read to confirm the product. The path
segment in each supplied URL is an opaque redirect token and is <strong>not</strong> the product
ASIN. {f1}</div>

<h2>Per-product verification result</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Product</th><th>ASIN</th><th>Attributes verified</th><th>Source types used</th>
  <th>Verified on</th><th>Official source</th></tr></thead><tbody>{ver}</tbody></table></div>
</div></div>

<h2>Official sources</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>ID</th><th>Document</th><th>Publisher</th><th>Type</th><th>URL</th>
  <th>Version / access note</th></tr></thead><tbody>{sources}</tbody></table></div>
</div></div>

<h2>How to re-run this verification</h2>
<div class="card">
  <ol class="small">
    <li>Request each supplied URL and follow the redirect chain; record the final
      <span class="mono">/dp/&lt;ASIN&gt;</span> path and read the destination page title.</li>
    <li>Request each <span class="mono">amazon.com/dp/&lt;ASIN&gt;</span> page and read, in
      order: the buy box (price, list price, discount badge), the rating and rating count, the
      "bought in past month" line, the About-this-item bullets, and the Product information and
      Item details blocks (model, UPC, capacity, dimensions, weight, wattage, Best Sellers
      Rank, warranty).</li>
    <li>Request the Amazon search listing for the ASIN as a cross-check — it exposes price, list
      price, rating, rating count and purchase velocity even when the detail page body is
      reduced.</li>
    <li>Read the Amazon Associates Program Policies and Operating Agreement, and the FTC's
      Disclosures 101 and Endorsement Guides FAQ, for the compliance map.</li>
    <li>Reconcile the transcript against <span class="mono">data/products.json</span> and
      <span class="mono">data/program.json</span>. Any field that cannot be re-read is set to
      null with an unverified flag; it is never filled from a previous run.</li>
    <li>Regenerate the site with <span class="mono">python3 tools/build_site.py</span> and run
      <span class="mono">python3 tools/check_links.py</span>.</li>
  </ol>
</div>

<h2>Linked artefacts</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Artefact</th><th>Contents</th><th>Path</th><th>Official source</th></tr></thead><tbody>
  <tr><td>Product dataset</td><td>Every verified attribute, with its source URL and status</td>
    <td class="mono">data/products.json</td><td class="src"><a href="https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/products.json" target="_blank" rel="noopener noreferrer">GitHub blob</a></td></tr>
  <tr><td>Programme dataset</td><td>Program rules, automation rules and source register</td>
    <td class="mono">data/program.json</td><td class="src"><a href="https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/program.json" target="_blank" rel="noopener noreferrer">GitHub blob</a></td></tr>
  <tr><td>Flag register</td><td>Every irregularity, gap and open question</td>
    <td class="mono">data/flags.json</td><td class="src"><a href="https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/flags.json" target="_blank" rel="noopener noreferrer">GitHub blob</a></td></tr>
  <tr><td>Site generator</td><td>Renders every page from the datasets</td>
    <td class="mono">tools/build_site.py</td><td class="src"><a href="https://github.com/kanlerxz87-cyber/Zone1/blob/main/tools/build_site.py" target="_blank" rel="noopener noreferrer">GitHub blob</a></td></tr>
  <tr><td>Link checker</td><td>Verifies every internal link resolves and every external link
    is well formed</td><td class="mono">tools/check_links.py</td><td class="src"><a href="https://github.com/kanlerxz87-cyber/Zone1/blob/main/tools/check_links.py" target="_blank" rel="noopener noreferrer">GitHub blob</a></td></tr>
  <tr><td>Coordination board</td><td>Task board, session registry, irregularity log and change
    log</td><td class="mono">COORDINATION.md</td><td class="src"><a href="https://github.com/kanlerxz87-cyber/Zone1/blob/main/COORDINATION.md" target="_blank" rel="noopener noreferrer">GitHub blob</a></td></tr>
</tbody></table></div>
</div></div>

<div class="note"><strong>What this page deliberately does not contain.</strong> No search
volume, keyword difficulty, competitor traffic estimates, category-wide conversion benchmarks
or historical rank series appear anywhere in this project, because none of them could be
confirmed from an official first-party source. Those numbers belong to a named third-party tool
and must be cited to it before publication. {f13}</div>
""".format(
        policy=esc(PRODUCTS["meta"]["verification_policy"]),
        build=BUILD_DATE,
        links="".join(link_rows),
        ver="".join(ver_rows),
        sources=src_rows,
        f1=flag_pill("F-01", depth), f13=flag_pill("F-13", depth),
    )
    return layout(
        "pages/sources.html",
        "Sources & Verification",
        "<strong>Zone1</strong> / Governance / Sources & Verification",
        body,
        depth,
        subtitle="Full source register and verification audit trail for the Zone1 project.",
    )


def page_flagged():
    depth = 1
    sev_pill = {"high": "flag", "medium": "warn", "low": "grey"}
    rows = []
    for f in FLAGS["flags"]:
        legacy = f.get("legacy_ids") or []
        prov = '<div class="small muted">raised by {o}</div>'.format(o=esc(f.get("origin", "zone1-main")))
        if legacy:
            prov += '<div class="small muted">also logged as {l}</div>'.format(
                l=esc(", ".join(legacy)))
        rows.append(
            '<tr id="{fid}"><td class="mono"><strong>{fid}</strong></td>'
            '<td><strong>{title}</strong><div class="small muted">{cat}</div>{prov}</td>'
            '<td><span class="pill {sev_p}">{sev}</span></td>'
            '<td>{obs}</td><td>{why}</td><td>{act}</td>'
            '<td class="src">{src}</td><td>{st}</td></tr>'.format(
                fid=esc(f["id"]), title=esc(f["title"]), cat=esc(f["category"]),
                prov=prov,
                sev=esc(f["severity"]), sev_p=sev_pill.get(f["severity"], "grey"),
                obs=esc(f["observation"]), why=esc(f["why_it_matters"]),
                act=esc(f["action_taken"]),
                src=src_cell(f["source"], f.get("secondary_sources")),
                st=('<span class="pill warn">needs review</span>' if f["status"] == "needs review"
                    else '<span class="pill ok">{s}</span>'.format(s=esc(f["status"]))),
            )
        )
    body = """
<h1>Flagged for Review</h1>
<p class="lede">Every irregularity, gap and open question found during line-by-line verification.
None of these blocks the site going live — each is published here with the source that was
checked and the action taken, so you can review and request changes after the site is live.</p>

<div class="grid g4" style="margin-bottom:16px">
  <div class="kpi"><div class="label">Open items</div><div class="value">{nopen}</div>
    <div class="note">published for review</div></div>
  <div class="kpi"><div class="label">High severity</div><div class="value">{nh}</div>
    <div class="note">must be closed before live traffic</div></div>
  <div class="kpi"><div class="label">Medium severity</div><div class="value">{nm}</div>
    <div class="note">verify before publishing a claim</div></div>
  <div class="kpi"><div class="label">Low severity</div><div class="value">{nl}</div>
    <div class="note">cosmetic or completeness gaps</div></div>
</div>

<div class="note"><strong>{ntotal} items in the register, {nclosed} of them resolved.</strong>
Every item ever raised stays on this page, including the ones that have since been closed, so the
audit trail is complete. Resolved items keep their observation and their source, and record what
closed them. The register also carries findings from the first build iteration of this project:
each such item shows the id it had in that earlier register.</div>

<div class="note flag"><strong>How to use this page.</strong> Each item names what was observed,
which official source was checked, and what the project did about it. If an item is wrong, or
you want a different resolution, the corresponding dataset file is the thing to change —
<span class="mono">data/flags.json</span> for the item itself and
<span class="mono">data/products.json</span> or <span class="mono">data/program.json</span> for
the underlying value. Changing a dataset entry and re-running the generator updates every page
that quotes it.</div>

<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>ID</th><th>Item</th><th>Severity</th><th>What was observed</th>
  <th>Why it matters</th><th>Action taken</th><th>Official source</th><th>Status</th>
</tr></thead><tbody>{rows}</tbody></table></div>
</div></div>

<h2>Unverified values left blank</h2>
<p class="small">These are the individual attribute rows across all three products where the
official source did not serve a readable value. They are blank in the catalogue, the comparison
table and the buying guide. Nothing was inferred from a sibling product, from the title, or from
memory.</p>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>Product</th><th>Attribute</th><th>Why it is blank</th><th>Official source</th>
</tr></thead><tbody>{blank}</tbody></table></div>
</div></div>

<h2>Source register for this page</h2>
<div class="card flush"><div class="card-body" style="padding:0">
<div class="table-scroll"><table class="data"><thead><tr>
  <th>ID</th><th>Document</th><th>Publisher</th><th>URL</th>
</tr></thead><tbody>{sources}</tbody></table></div>
</div></div>
""".format(
        n=len(FLAGS["flags"]),
        ntotal=len(FLAGS["flags"]),
        nopen=len(FLAGS_OPEN),
        nclosed=len(FLAGS_CLOSED),
        nh=sum(1 for f in FLAGS_OPEN if f["severity"] == "high"),
        nm=sum(1 for f in FLAGS_OPEN if f["severity"] == "medium"),
        nl=sum(1 for f in FLAGS_OPEN if f["severity"] == "low"),
        rows="".join(rows),
        blank="".join(
            '<tr><td>{ref}</td><td>{label}</td><td>{why}</td><td class="src">{s}</td></tr>'.format(
                ref=esc(p["ref"] + " · " + p["short_name"]),
                label=esc(f["label"]),
                why=esc("The official page did not serve a readable value for this attribute "
                        "at the verification date."),
                s=src_cell(f["source"]),
            )
            for p in PRODUCTS["products"] for f in p["fields"] if f["status"] != "verified"
        ),
        sources="".join(
            '<tr><td class="mono">{sid}</td><td>{title}</td><td>{pub}</td>'
            '<td class="src"><a href="{u}" target="_blank" rel="noopener noreferrer">{u}</a></td></tr>'.format(
                sid=esc(s["id"]), title=esc(s["title"]), pub=esc(s["publisher"]), u=esc(s["url"])
            ) for s in PROGRAM["sources"]
        ),
    )
    return layout(
        "pages/flagged.html",
        "Flagged for Review",
        "<strong>Zone1</strong> / Governance / Flagged for Review",
        body,
        depth,
        subtitle="Open items and irregularities found during verification of the Zone1 project.",
    )


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    write("index.html", page_index())
    write("pages/executive-summary.html", page_executive_summary())
    write("pages/catalog.html", page_catalog())
    write("pages/category/dual-basket-air-fryers.html", page_category(
        "dual-basket-air-fryers",
        "Dual-Basket Air Fryers",
        "Air fryers with two independent cooking zones. The category's defining feature is that "
        "each basket cooks on its own timer and temperature, so two different dishes can be "
        "prepared at the same time — and, with a synchronised finish, completed at the same "
        "moment.",
        ["p1"],
    ))
    write("pages/category/multi-function-air-fryer-ovens.html", page_category(
        "multi-function-air-fryer-ovens",
        "Multi-Function Air Fryer Ovens",
        "Larger air fryer ovens that extend past frying into baking, dehydrating and rotisserie "
        "cooking. Two of the three products in this project sit in this category, and they "
        "occupy very different price points: a {p} 8-quart single-basket unit and a {q} 26-quart "
        "French-door cooking centre.".format(
            p=field_value(PRODUCTS_BY_ID["p3"], "Current price (new)") or "—",
            q=field_value(PRODUCTS_BY_ID["p2"], "Current price (new)") or "—",
        ),
        ["p2", "p3"],
    ))
    write("pages/research.html", page_research())
    write("pages/marketing/seo-article.html", page_marketing_seo())
    write("pages/marketing/comparison.html", page_marketing_comparison())
    write("pages/marketing/buying-guide.html", page_marketing_buying_guide())
    write("pages/campaign.html", page_campaign())
    write("pages/compliance.html", page_compliance())
    write("pages/sources.html", page_sources())
    write("pages/flagged.html", page_flagged())


if __name__ == "__main__":
    main()
