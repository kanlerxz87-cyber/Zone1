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
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
SITE_NAME = "Zone1 Kitchen"
SITE_TAGLINE = "Verified Amazon affiliate product intelligence"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

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

SRC_BY_ID = {s["id"]: s for s in SOURCES["sources"]}
ACCESSED = SOURCES["accessed"]
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
    ("index.html", "Dashboard", "Overview of the product set and the data"),
    ("categories/kitchen-appliances.html", "Category: Kitchen", "All tracked products in one category"),
    ("compare.html", "Comparison", "Verified-only side-by-side matrix"),
    ("guides/buying-guide-air-fryers.html", "Buying guide", "How to choose a form factor"),
    ("data.html", "Full dataset", "Every field, value, source and gap"),
    ("platform.html", "Platform blueprint", "The automation and compliance design"),
    ("compliance.html", "Compliance", "Program rules, quoted, with sources"),
    ("flagged.html", "Flagged for review", "Unverified values and irregularities"),
    ("executive-summary.html", "Executive summary", "Decision-ready briefing"),
    # Additive section contributed by parallel session 8a2ddd06 (own data, own source register).
    ("research/index.html", "Deep-dive research ↗", "Independent 25-source verification pass"),
    # Additive section contributed by parallel session arena-3740f69d (own data, own source register).
    ("session-3740f69d/index.html", "Session 3740f69d build ↗", "Independent dashboard build — link analysis, tracking design, AI Agent-Terms compliance"),
]

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
footer.site h5{margin:0 0 .4rem; font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; color:#6b7280}
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
"""

JS = r"""
document.addEventListener('click', function (ev) {
  var t = ev.target.closest('.navtoggle');
  if (t) { document.querySelector('.sidebar').classList.toggle('open'); }
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


def layout(page_rel, title, body, active=None, description=""):
    prefix = depth_prefix(page_rel)
    nav_html = []
    for href, label, sub in NAV:
        cls = ' class="active"' if href == active else ""
        nav_html.append(
            f'<a href="{prefix}{href}"{cls}>{e(label)}<span class="sub">{e(sub)}</span></a>'
        )
    # product links under the category entry
    prod_nav = "".join(
        f'<a href="{prefix}products/{p["slug"]}.html">{e(p["short_name"])}'
        f'<span class="sub">ASIN {e(p["asin"]["v"])}</span></a>'
        for p in PRODUCT_LIST
    )
    desc = f'<meta name="description" content="{e(description)}">' if description else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · {e(SITE_NAME)}</title>
{desc}
<link rel="stylesheet" href="{prefix}assets/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' fill='%230f766e'/%3E%3Ctext x='16' y='22' font-family='sans-serif' font-size='15' font-weight='700' fill='%23fff' text-anchor='middle'%3EZ1%3C/text%3E%3C/svg%3E">
</head>
<body>
<div class="disclosure-bar">
  <strong>Affiliate disclosure:</strong> {e(DISCLOSURE)}
  <a href="{prefix}compliance.html" style="color:#9ff3ec">How this site stays compliant →</a>
</div>
<header class="topbar">
  <a class="brand" href="{prefix}index.html" style="color:inherit">
    <span class="mark">Z1</span>
    <span>{e(SITE_NAME)}<small>{e(SITE_TAGLINE)}</small></span>
  </a>
  <span class="spacer"></span>
  <span class="meta">data verified {e(ACCESSED)}</span>
  <button class="navtoggle" type="button" aria-label="Toggle navigation">Menu</button>
</header>
<div class="shell">
  <aside class="sidebar">
    <div class="group">
      <h4>Dashboard</h4>
      {nav_html[0]}
    </div>
    <div class="group">
      <h4>Products</h4>
      <a href="{prefix}categories/kitchen-appliances.html"{' class="active"' if active=='categories/kitchen-appliances.html' else ''}>Category: Kitchen<span class="sub">3 tracked products</span></a>
      {prod_nav}
      {nav_html[2]}
    </div>
    <div class="group">
      <h4>Research &amp; data</h4>
      {nav_html[3]}
      {nav_html[4]}
      {nav_html[5]}
      {nav_html[6]}
    </div>
    <div class="group">
      <h4>Report</h4>
      {nav_html[7]}
      {nav_html[8]}
    </div>
  </aside>
  <main>
    {body}
  </main>
</div>
<footer class="site">
  <div class="inner">
    <div>
      <h5>Disclosure</h5>
      <p><strong>{e(DISCLOSURE)}</strong></p>
      <p>Links marked <span class="paid-tag">Paid link</span> are Amazon Associates links. If you buy through one, this site may earn a commission at no extra cost to you. Amazon prices and availability are never published here — check the live price on Amazon.</p>
    </div>
    <div>
      <h5>Verification</h5>
      <p>Every asserted value on this site links to the official page it came from. Values that could not be confirmed from an official source are left blank and listed on the <a href="{prefix}flagged.html">Flagged for review</a> page.</p>
      <p class="tiny">Data verified {e(ACCESSED)}. Policies change: always re-check the source before relying on it.</p>
    </div>
    <div>
      <h5>Cookies &amp; privacy</h5>
      <p>This site sets no cookies itself, runs no analytics, and has no comment forms or accounts. Following an Amazon link takes you to Amazon, whose own privacy notice and cookie practices apply from that point. No data you enter here is collected, because there is nowhere to enter it.</p>
      <p class="tiny">Amazon's Program Policies §3(e) require an accurate statement of cookie and third-party technology use on Associate sites. This notice satisfies that requirement for the current build; it must be updated the moment any analytics, embeds or affiliate-network script is added.</p>
    </div>
    <div>
      <h5>Sources</h5>
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
  <a class="btn" href="{e(p['link'])}" target="_blank" rel="nofollow sponsored noopener">Check price on Amazon <span aria-hidden="true">↗</span></a>
  <span class="paid-tag">Paid link</span>
  <span class="small muted">No Amazon price is shown here — the live price lives on the listing.</span>
</div>
<p class="cta-note">Link-level disclosure: this is an affiliate link and we may earn a commission if you buy, at no extra cost to you. ASIN <code>{e(p['asin']['v'])}</code> {src_links(['S17'])}</p>
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
        rate_cell = (
            f'{e(rate)}' if rate else
            '<span class="blank">— not confirmed —</span>' + ' ' + flag_pill("unverified")
        )
        rows.append(
            f'<tr>'
            f'<td><a href="products/{p["slug"]}.html">{e(p["short_name"])}</a></td>'
            f'<td>{e(p["brand"])}</td>'
            f'<td>{e(p["pricing"]["brand_list_price"]["v"])} '
            f'<span class="tiny muted">brand list price</span> {src_links(p["pricing"]["brand_list_price"]["s"])}</td>'
            f'<td class="blank">not displayed</td>'
            f'<td>{rate_cell}</td>'
            f'<td>{e(p["reviews"]["brand_site_rating"]["v"])} {src_links(p["reviews"]["brand_site_rating"]["s"])}</td>'
            f'<td>{len([f for f in p["flags"]])} flagged</td>'
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
<p class="tiny muted">Commission rate is blank on every row on purpose: Amazon publishes rates by <em>category</em> (S3) but not the category assigned to a given ASIN, so any number here would be a guess. Amazon price is blank because Program Policies §2(b) only permits displaying it when Amazon serves the link or via the official API {src_links(['S2'])}. "Brand-site rating" is the manufacturer's own on-site review widget, not Amazon's.</p>
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

def page_index():
    n_flags = sum(len(p["flags"]) for p in PRODUCT_LIST)
    n_total_flags = n_flags + len(PROGRAMME_FLAGS)
    verified = sum(1 for p in PRODUCT_LIST for s in p["specs"] if s["value"] is not None)
    unverified = sum(1 for p in PRODUCT_LIST for s in p["specs"] if s["value"] is None)
    cards = "".join(
        f"""
<div class="card pcard">
  <div class="rank">Rank {p['rank']} · {e(p['category'])}</div>
  <h3><a href="products/{p['slug']}.html">{e(p['short_name'])}</a></h3>
  <p class="small muted" style="margin:.2rem 0">{e(p['name'])}</p>
  <div class="facts">
    <span class="chip">ASIN {e(p['asin']['v'])}</span>
    <span class="chip">{e(p['pricing']['brand_list_price']['v'])} brand list</span>
    <span class="chip">{len(p['flags'])} flag(s)</span>
  </div>
  {product_cta(p)}
  <p class="small" style="margin:0"><a href="products/{p['slug']}.html">Read the verified breakdown →</a></p>
</div>"""
        for p in PRODUCT_LIST
    )
    body = f"""
<p class="crumbs">Dashboard</p>
<h1>Three Amazon products, verified line by line</h1>
<p class="lede">This dashboard holds everything that could be confirmed about the three supplied Amazon listings from <strong>official sources only</strong> — Amazon's Associates documents, the US FTC's rule text, and each manufacturer's own product page and owner's manual. Where a fact could not be confirmed, the field is blank and the item appears on <a href="flagged.html">Flagged for review</a>. Nothing has been inferred, estimated or filled in.</p>

<div class="grid grid-4" style="margin:1rem 0 1.25rem">
  <div class="stat brand"><div class="n">3</div><div class="l">Products resolved</div><div class="h">All three short links followed to an ASIN</div></div>
  <div class="stat ok"><div class="n">{verified}</div><div class="l">Verified spec values</div><div class="h">Each with a link to the manufacturer page or manual</div></div>
  <div class="stat warn"><div class="n">{unverified}</div><div class="l">Unconfirmed values</div><div class="h">Left blank, listed on Flagged for review</div></div>
  <div class="stat bad"><div class="n">{n_total_flags}</div><div class="l">Irregularities</div><div class="h">Including one hard spec conflict between sources</div></div>
</div>

<div class="callout info">
  <strong>Read this before you use any number on this site</strong>
  <p class="small">No Amazon price, star rating or review count appears anywhere on this site. That is deliberate. Amazon's Program Policies §2(b) allow price and availability to be shown only when Amazon serves the link or when the data comes from Creators/PA API, and §3(t) restricts customer reviews and star ratings to API-served content {src_links(['S2'])}. Manufacturer list prices are shown instead, in their own column, with their own source links.</p>
</div>

<h2>The product set</h2>
<div class="grid grid-3">{cards}</div>

<h2>Commercial summary</h2>
{commercial_table()}

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
    <tr><td>{flag_pill('conflict')}</td><td>Two official sources state different things and neither can be preferred.</td><td>Both claims quoted side by side; no single value asserted.</td></tr>
  </tbody>
</table>
</div>
<p class="tiny muted">"Official" in this project means: Amazon.com for Amazon program facts and for which ASIN a link resolves to; a US government source for US law; the manufacturer for product specifications. Retailer listings, reseller marketplaces, review aggregators and affiliate blogs are not treated as sources — several of them contradicted each other and the official rate table on the day of verification.</p>
"""
    return layout("index.html", "Dashboard", body, active="index.html",
                  description="Verified Amazon affiliate product dashboard: three air fryers, every value sourced to an official page, every gap disclosed.")


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
<p class="crumbs"><a href="../index.html">Dashboard</a> / <a href="../categories/kitchen-appliances.html">Kitchen</a> / {e(p['short_name'])}</p>
<h1>{e(p['short_name'])}</h1>
<p class="lede">{e(p['name'])} — {e(p['brand'])}. Rank {p['rank']} of 3 in this set. Everything below was read from the manufacturer's own page or owner's manual on {e(ACCESSED)}; the Amazon listing itself was used only to confirm which ASIN the supplied link points to.</p>

<div class="grid grid-4" style="margin-bottom:1rem">
  <div class="stat"><div class="n" style="font-size:1.15rem">{e(p['asin']['v'])}</div><div class="l">ASIN</div></div>
  <div class="stat"><div class="n" style="font-size:1.15rem">{e(p['pricing']['brand_list_price']['v'])}</div><div class="l">Brand list price</div></div>
  <div class="stat"><div class="n" style="font-size:1.15rem">{e(p['reviews']['brand_site_rating']['v'].split(' from')[0])}</div><div class="l">Brand-site rating</div></div>
  <div class="stat warn"><div class="n" style="font-size:1.15rem">{len(p['flags'])}</div><div class="l">Open flags</div></div>
</div>

{product_cta(p)}

<div class="callout ok">
  <strong>How this review was produced</strong>
  <p class="small">This is a documentation-based review. No unit was tested, owned or handled. That matters legally as well as ethically: the FTC's disclosure guidance says an endorser cannot describe an experience with a product they have not tried {src_links(['S8'])}, so this page describes published specifications and what they imply — nothing else.</p>
</div>

<h2>What the link resolves to</h2>
<div class="card tight">
  <p class="small" style="margin:0"><strong>Supplied short link:</strong> <code>{e(p['link'])}</code> {src_links(['S17'])}<br>
  <strong>Resolves to:</strong> <code>https://www.amazon.com/dp/{e(p['asin']['v'])}</code> {src_links(['S16'])}</p>
  <p class="tiny muted" style="margin:.5rem 0 0">{e(p['asin_evidence'])}</p>
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
    <tr><td>Amazon price</td><td class="blank">— not displayed —</td><td>{flag_pill('unverified')} {e(p['pricing']['amazon_price_reason'])}</td></tr>
    <tr><td>MSRP confirmed</td><td class="blank">— not confirmed —</td><td>{flag_pill('unverified')} {e(p['pricing']['msrp_confirmed'])}</td></tr>
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
    return layout(f"products/{tag}.html", p["short_name"], body,
                  active=f"products/{tag}.html",
                  description=f"Documentation-based review of the {p['name']} — verified specifications with official source links.")


PROGRAMME_FLAGS = [
    ("F1", "ASIN → manufacturer model number is not published by Amazon.",
     "All three", "Each product's model number is recorded as a match by capacity/finish/brand wording, with an explicit caveat. Flagged rather than asserted.", ["S16"]),
    ("F6", "The Associates tag inside the three link.amazon short links is not observable.",
     "All three links", "The shortener hides the tag. Attribution cannot be verified from outside Associates Central, so 'associates_tag_confirmed' is false for all three links. Needs the account holder to open Manage Tracking IDs.", ["S2", "S17"]),
    ("F7", "Program Policies §2(w) prohibits link shortening that makes it unclear you are linking to an Amazon Site.",
     "All three links", "link.amazon keeps the Amazon name visible, so the risk is low, but the landing URL is generated and temporary. Recorded so the account holder can confirm current guidance before publishing.", ["S2"]),
    ("F8", "IP License §2(e) forbids aggregating, analysing or repurposing Program Content and training models on it.",
     "Platform design", "Any AI research or trend scoring therefore runs only on first-party data and public manufacturer data. Documented as guardrail G6 in the blueprint.", ["S2"]),
    ("F9", "No Amazon price, star rating or review count is available to this build.",
     "All three", "Left blank everywhere by policy rather than by omission. Becomes fillable only if the operator secures Creators/PA API credentials.", ["S2", "S19"]),
    ("F10", "The short links are generated redirects with fallback parameters, not plain product links.",
     "All three links", "Each resolves with lv=shuf and plpRedirect=mhFallback in the landing URL, and the srctok value stays constant across repeat requests (re-tested 2026-11-13). That pattern is Amazon's server-side redirect, not a guarantee of a stable destination. Open each link yourself before publishing and confirm the product is the one intended.", ["S17", "S16"]),
    ("F11", "The site does not disclose cookies, pixels and third-party technologies as Participation Requirements §3(e) requires.",
     "Whole site", "The site itself sets no cookies and runs no analytics, but §3(e) requires an accurate disclosure of cookie and third-party technology use, including that third parties may place or recognise cookies. Only a minimal notice is in the footer; a proper privacy/cookie statement is needed before launch. Legal review recommended.", ["S2"]),
    ("F12", "The automated platform functions in the brief are not running — by design, not by omission.",
     "Platform", "Automated trend detection, competition scoring and conversion optimisation need an Associates account, Creators/PA API credentials and sales reports. PA API access is registered through Associates Central and credentials are tied to the primary account holder, with request rate scaled to account sales performance. None of that exists in this repository, and inventing the data to fill the gap would defeat the point of the project.", ["S2", "S19", "S20"]),
    ("F13", "Product listing titles are reproduced from Amazon; §6(a) restricts altering Program Content.",
     "All three", "Titles are shown verbatim and unedited. §6(a) permits truncation only where meaning is not materially altered, and whether a listing title counts as Program Content is not stated. Recorded so the operator can confirm before adding any paraphrase.", ["S2"]),
]

VERDICTS = {
    "chefman-6qt-dual-basket":
        "The published specification set is the most complete of the three: capacity, temperature range, dimensions, weight, power draw, safety approval and warranty are all stated by the manufacturer. Two independently controlled baskets with a Sync Finish function and a 450 °F ceiling address the main real-world complaint about single-basket air fryers — that you cannot cook two things at different temperatures at once. The one number a shopper most wants, cost per quart, cannot be computed here because the Amazon price is not available to this site by policy; the brand list price of $119.99 for 6 quarts is the only comparable figure that can be stated.",
    "emeril-26qt-french-door":
        "The largest cavity in the set by a wide margin (26 qt against 6 qt and 8 qt) and the only unit that is an oven rather than a basket. The manufacturer documents the power draw (1700 W), the temperature range (75–500 °F) and the physical footprint, which is what actually decides whether it fits a kitchen. On preset count the manual is the controlling document: its chart names exactly 24 presets, which matches the description text and the Amazon title rather than the spec block's 25. The brand's own on-site rating is unusually low (2.6 from 25 reviews) and is reported here as displayed, not softened.",
    "chefman-8qt-turbofry":
        "A conventional single-basket 8-quart air fryer with a documented 200–400 °F range, four food-type presets and dishwasher-safe nonstick parts. The unresolved problem is that the Amazon listing title advertises a 450 °F Hi-Fry mode and bake/dehydrate/frozen functions that the brand page and the owner's manual do not document. Until that is resolved, the honest position is that the temperature ceiling of the unit shipping against this ASIN is unknown, and the buyer should read the manual that arrives with the unit.",
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
          <td class="blank">not displayed</td>
          <td>{len(p['flags'])}</td>
        </tr>"""
        for p in PRODUCT_LIST
    )
    body = f"""
<p class="crumbs"><a href="../index.html">Dashboard</a> / Kitchen appliances</p>
<h1>Category: kitchen appliances — air fryers</h1>
<p class="lede">All three supplied links resolve to air fryers or air fryer toaster ovens, so this is the category the product set defines. The table below lists every tracked product with its verified capacity, the manufacturer's list price and its open flags. Amazon price is blank on every row by policy, not by oversight.</p>

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
    return layout("categories/kitchen-appliances.html", "Category: Kitchen", body,
                  active="categories/kitchen-appliances.html",
                  description="Kitchen appliance category page: three tracked air fryers with verified capacity, manufacturer list price and open flags.")


def page_compare():
    fields = []
    seen = set()
    for p in PRODUCT_LIST:
        for s in p["specs"]:
            if s["label"] not in seen:
                seen.add(s["label"])
                fields.append(s["label"])

    head = "".join(
        f'<th><a href="../products/{p["slug"]}.html">{e(p["short_name"])}</a><div class="tiny muted" style="font-weight:400">ASIN {e(p["asin"]["v"])}</div></th>'
        for p in PRODUCT_LIST
    )
    rows = []
    for label in fields:
        cells = []
        for p in PRODUCT_LIST:
            match = next((s for s in p["specs"] if s["label"] == label), None)
            if match is None:
                cells.append('<td class="blank">— not documented —</td>')
            elif match["value"] is None:
                cells.append(f'<td class="blank">— not confirmed —</td>')
            else:
                cells.append(f'<td>{e(match["value"])}<div class="tiny">{src_links(match["source"])}</div></td>')
        rows.append(f'<tr><td><strong>{e(label)}</strong></td>{"".join(cells)}</tr>')

    body = f"""
<p class="crumbs"><a href="../index.html">Dashboard</a> / Comparison</p>
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
    return layout("compare.html", "Comparison", body, active="compare.html",
                  description="Verified-only comparison of three air fryers, with gaps left visible and every value linked to an official source.")


def page_guide():
    body = f"""
<p class="crumbs"><a href="../index.html">Dashboard</a> / Buying guide</p>
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
                  description="How to choose an air fryer: form factor, documented capacity, real temperature ceilings, cleaning and footprint.")


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
                f'<td>{e(p["short_name"])}<div class="tiny muted">ASIN {e(p["asin"]["v"])}</div></td>'
                f'<td>{e(s["label"])}</td>'
                f'<td>{value}{note}</td>'
                f'<td>{flag_pill(state)}</td>'
                f'<td>{src_links(s["source"])}</td>'
                f'</tr>'
            )
    total = len(rows)
    body = f"""
<p class="crumbs"><a href="../index.html">Dashboard</a> / Full dataset</p>
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

<h2>Source register</h2>
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
                  description="Complete specification register for three air fryers: every value, its verification status and the official source link.")


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
<p class="crumbs"><a href="../index.html">Dashboard</a> / Compliance</p>
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

<h2>Bounty events (US) — published, not recommended for this launch</h2>
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
    <p class="small" style="margin-bottom:0">The disclosure bar at the top of every page is the one Amazon requires word for word. The "Paid link" tag next to every outbound button is the FTC-style link-level disclosure. Neither can be switched off by a content update, because both are generated into the page layout.</p>
  </div>
  <div class="card">
    <h3 style="margin-top:0">If you are the operator</h3>
    <p class="small" style="margin-bottom:0">This is the audit surface. When Amazon changes a rule, the page changes here first, then the build enforces it. The <a href="../flagged.html">flagged page</a> is the backlog of facts that still need a human decision before any copy can assert them.</p>
  </div>
</div>
"""
    return layout("compliance.html", "Compliance", body, active="compliance.html",
                  description="Amazon Associates and FTC compliance requirements, quoted with official source links and mapped to implementation.")


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
        return (f'<tr><td class="num"><strong>{e(fid)}</strong></td><td>{e(issue)}<div class="tiny muted">Scope: {e(scope)}</div></td>'
                f'<td class="small">{e(action)}</td><td>{src_links(srcs)}</td></tr>')

    body = f"""
<p class="crumbs"><a href="../index.html">Dashboard</a> / Flagged for review</p>
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
  <p class="small">The Chefman 8 Qt listing advertises a <strong>450 °F Hi-Fry</strong> mode and bake/dehydrate/frozen functions. The brand's own product page and its RJ38-SQSS-8T owner's manual document a <strong>200–400 °F</strong> range with four food-type presets. One of those official sources is describing a different product, or one is stale. This site asserts neither, and the buying guide tells readers to read the manual that ships with the unit. {src_links(['S12', 'S13', 'S16'])}</p>
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
  <thead><tr><th>ID</th><th>Item</th><th>Resolution</th><th>Date</th></tr></thead>
  <tbody><tr><td colspan="4" class="blank">No items resolved yet — this build is the first verification pass.</td></tr></tbody>
</table>
</div>
"""
    return layout("flagged.html", "Flagged for review", body, active="flagged.html",
                  description="Unverified values, source conflicts and operational irregularities flagged for human review, each with its official source link.")


def page_platform():
    pipeline = "".join(
        f"""<tr>
          <td class="num">{s['stage']}</td>
          <td><strong>{e(s['name'])}</strong><div class="tiny muted">Automation: {e(s['automation'])}</div></td>
          <td class="small">{e(s['inputs'])}</td>
          <td class="small">{e(s['outputs'])}</td>
          <td class="num">{e(s['guardrail'])}</td>
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
    modes = "".join(
        f'<tr><td>{e(m["task"])}</td><td>{e(m["mode"])}</td><td class="num">{e(m["frequency"])}</td></tr>'
        for m in PLATFORM["automation_vs_human"]
    )
    kpis = "".join(
        f'<tr><td><strong>{e(k["kpi"])}</strong></td><td class="small">{e(k["definition"])}</td><td class="small">{e(k["target"])}</td></tr>'
        for k in PLATFORM["kpis"]
    )
    launch = "".join(
        f'<tr><td class="num">{s["step"]}</td><td class="small">{e(s["action"])}</td><td class="small muted">{e(s["why"])}</td></tr>'
        for s in PLATFORM["launch_sequence"]
    )
    oos = "".join(f'<li>{e(x)}</li>' for x in PLATFORM["explicitly_out_of_scope"])
    body = f"""
<p class="crumbs"><a href="../index.html">Dashboard</a> / Platform blueprint</p>
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
                  description="Automation blueprint for a compliant Amazon affiliate platform: pipeline, guardrails, KPIs and launch sequence.")


def page_exec():
    facts = [
        ("Product set", "Three Amazon listings, resolved from three short links to ASINs B0CDY277D3, B09B7SB46R and B08DKYBTPH.", ["S16", "S17"]),
        ("Category", "All three are air fryers or air fryer toaster ovens — the niche is set by the products, not chosen.", ["S16"]),
        ("Verification standard", "Official sources only; blank plus flagged wherever unconfirmed; no inference.", []),
        ("Verified spec values", "Published on the dashboard and in the full dataset, each with a source link.", []),
        ("Hard source conflicts", "One serious (Chefman 8 Qt 450 °F claim vs its own manual), plus preset-count and SKU ambiguity issues.", ["S12", "S13", "S14"]),
        ("Commission rate", "Deliberately blank per product. Amazon publishes rates by category and not by ASIN.", ["S3"]),
        ("Amazon price / rating", "Not displayed anywhere, by policy, not by omission.", ["S2"]),
        ("Disclosure", "Required statement on every page plus a link-level badge on every outbound link.", ["S1", "S5"]),
        ("Biggest constraint", "Program Content may not be aggregated, analysed or trained on — which rules out the obvious version of an AI research engine.", ["S2"]),
        ("Next decision", "Resolve the remaining flagged items, then publish, then apply.", ["S4"]),
    ]
    rows = "".join(
        f'<tr><td><strong>{e(k)}</strong></td><td>{e(v)}</td><td>{src_links(s)}</td></tr>' for k, v, s in facts
    )
    body = f"""
<p class="crumbs"><a href="../index.html">Dashboard</a> / Executive summary</p>
<h1>Executive summary</h1>
<p class="lede">A one-page briefing for someone who will not read the rest. The short version: the product data is good, the economics are provable only within narrow limits, and the compliance constraint is the design constraint.</p>

<div class="grid grid-4" style="margin-bottom:1rem">
  <div class="stat brand"><div class="n">3</div><div class="l">Products</div><div class="h">Resolved to ASINs</div></div>
  <div class="stat ok"><div class="n">12</div><div class="l">Sources</div><div class="h">All official, all linked</div></div>
  <div class="stat warn"><div class="n">9</div><div class="l">Flags raised</div><div class="h">None hidden, none blocking</div></div>
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
  <p class="small">Every specification asserted on the site was read from the manufacturer's own product page or owner's manual on {e(ACCESSED)}, and each one carries a clickable link to it. Twelve sources are used; none is a retailer, a review aggregator or an affiliate blog. Values that could not be confirmed are blank and listed, which is the only honest way to publish a comparison table.</p>
</div>
<div class="callout bad">
  <strong>2 · One official source contradicts another, and it is not cosmetic</strong>
  <p class="small">The Chefman 8 Qt listing advertises a 450 °F Hi-Fry mode; the brand page and the RJ38-SQSS-8T manual document 200–400 °F. A buyer relying on the listing could receive a unit that does not match it. The site states both claims, asserts neither, and tells the reader to check the manual. Resolving this needs someone to open the live listing.</p>
</div>
<div class="callout">
  <strong>3 · The commission numbers cannot be stated per product, and pretending otherwise would be fabrication</strong>
  <p class="small">Amazon's published rate table lists Kitchen at 4.50%, Home at 3.00% and a 4.00% fallback {src_links(['S3'])}. Amazon does not publish which category a given ASIN sits in, and air fryers are not named in the table. Every "commission rate" figure on a competitor site therefore rests on a guess. This site shows the candidate rows and leaves the rate blank.</p>
</div>
<div class="callout info">
  <strong>4 · The policy constraint is the architecture</strong>
  <p class="small">The brief asks for automated product research, trend detection and optimisation. The IP License forbids aggregating, analysing, extracting or repurposing Program Content and forbids training models on it {src_links(['S2'])}. So the automated research layer must run on manufacturer documentation and the operator's own click and conversion data. That is a harder, slower build — and the only one that survives review.</p>
</div>

<h2>Economics, stated with the precision the data allows</h2>
<div class="tablewrap">
<table>
  <caption>Illustrative commissions at published rates — arithmetic, not forecast</caption>
  <thead><tr><th>Product</th><th>Brand list price</th><th>At Kitchen 4.50%</th><th>At Home 3.00%</th><th>At fallback 4.00%</th></tr></thead>
  <tbody>
    <tr><td>Chefman 6 Qt Dual</td><td class="num">$119.99</td><td class="num">$5.40</td><td class="num">$3.60</td><td class="num">$4.80</td></tr>
    <tr><td>Emeril 26 QT</td><td class="num">$199.99</td><td class="num">$9.00</td><td class="num">$6.00</td><td class="num">$8.00</td></tr>
    <tr><td>Chefman 8 Qt</td><td class="num">$119.99</td><td class="num">$5.40</td><td class="num">$3.60</td><td class="num">$4.80</td></tr>
  </tbody>
</table>
</div>
<p class="tiny muted">Brand list prices from {src_link('S10')}, {src_link('S12')} and {src_link('S14')}; rates from {src_link('S3')}. Amazon computes commission on Qualifying Revenue after shipping, tax, returns and bad debt, so real payouts are lower. The Amazon selling price — the number that would actually drive commission — is unknown to this project by policy.</p>

<h2>Recommendation</h2>
<ol class="tight small">
  <li><strong>Publish this build.</strong> It satisfies the content substance a review looks for, and it is honest under inspection.</li>
  <li><strong>Clear the flags that change copy first</strong> — F3 (the 450 °F conflict), F4/F5 (preset counts), F1/F2 (model mapping). Those decide what the pages may assert.</li>
  <li><strong>Fix attribution before driving traffic</strong> — confirm the Associates tag and create sub-tags; F6 and F7.</li>
  <li><strong>Then apply, and work the 180-day window deliberately</strong> {src_links(['S4'])}.</li>
  <li><strong>Only pursue price and rating display if API access is granted.</strong> Until then, absence is the compliant state.</li>
</ol>

<p class="small" style="margin-top:1.5rem"><a class="btn btn-ghost" href="../EXECUTIVE-SUMMARY.md">Download the markdown version</a> <a class="btn btn-ghost" href="../flagged.html">See every open flag</a></p>
"""
    return layout("executive-summary.html", "Executive summary", body, active="executive-summary.html",
                  description="One-page executive summary: findings, source conflicts, economics and the recommended next decision.")


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
    return layout("404.html", "Page not found", body)


# --------------------------------------------------------------------------- #
# build
# --------------------------------------------------------------------------- #

def check_rows_have_sources():
    """Build-time guard: an asserted value with no source id is a hard failure."""
    problems = []
    for p in PRODUCT_LIST:
        for s in p["specs"]:
            if s["value"] is not None and not s["source"]:
                problems.append(f'{p["slug"]}: "{s["label"]}" has a value but no source')
    return problems


def check_disclosure(pages):
    missing = [p for p, html_text in pages if DISCLOSURE not in html_text]
    return missing


def main():
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "style.css").write_text(CSS, encoding="utf-8")
    (assets / "app.js").write_text(JS, encoding="utf-8")

    for d in ("products", "categories", "guides"):
        (ROOT / d).mkdir(exist_ok=True)

    pages = {}
    pages["index.html"] = page_index()
    for p in PRODUCT_LIST:
        pages[f"products/{p['slug']}.html"] = page_product(p)
    pages["categories/kitchen-appliances.html"] = page_category()
    pages["compare.html"] = page_compare()
    pages["guides/buying-guide-air-fryers.html"] = page_guide()
    pages["data.html"] = page_data()
    pages["compliance.html"] = page_compliance()
    pages["flagged.html"] = page_flagged()
    pages["platform.html"] = page_platform()
    pages["executive-summary.html"] = page_exec()
    pages["404.html"] = page_404()

    # build guards
    problems = check_rows_have_sources()
    if problems:
        raise SystemExit("BUILD FAILED — rows with values but no official source:\n  " + "\n  ".join(problems))
    missing = check_disclosure(list(pages.items()))
    if missing:
        raise SystemExit("BUILD FAILED — pages missing the required disclosure: " + ", ".join(missing))

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


if __name__ == "__main__":
    main()
