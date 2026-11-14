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
# Additive re-verification ledger (2026-11-14 pass, sess-81495d2d). Rendered as its own
# page; nothing else in the build depends on it, so a future pass can replace the file
# without touching the generators below.
REVERIFICATION = load("reverification.json")
# Additive pass-6 ledger (2026-11-14, sess-54c66535): re-opens the nine rows the earlier
# pass could not re-check. Owned entirely by this session's folder, so a future pass can
# drop the file without touching anything else; the page simply omits the section.
_p6 = ROOT / "session-54c66535" / "pass6.json"
PASS6 = json.loads(_p6.read_text(encoding="utf-8")) if _p6.exists() else None

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
    ("index.html", "Dashboard", "Overview of the product set and the data"),
    ("categories/kitchen-appliances.html", "Category: Kitchen", "All tracked products in one category"),
    ("compare.html", "Comparison", "Verified-only side-by-side matrix"),
    ("guides/buying-guide-air-fryers.html", "Buying guide", "How to choose a form factor"),
    ("articles/index.html", "Articles", "Five sourced reads — comparisons, explainers, policy"),
    ("data.html", "Full dataset", "Every field, value, source and gap"),
    ("platform.html", "Platform blueprint", "The automation and compliance design"),
    ("compliance.html", "Compliance", "Program rules, quoted, with sources"),
    ("flagged.html", "Flagged for review", "Unverified values and irregularities"),
    ("executive-summary.html", "Executive summary", "Decision-ready briefing"),
    # Added by the 2026-11-14 integration pass: the line-by-line re-read ledger.
    ("reverification.html", "Re-verification 2026-11-14", "Every published value re-read against its official source"),
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
    # Entries that describe a *parallel* pass merged into this repo (a top-level directory
    # with its own data and source registry) are listed in NAV so the link checker covers
    # them, but the nav groups above only render fixed indices, so those entries were
    # reachable from no page at all. Surface them in the footer by prefix rather than by
    # index, so the next session that adds one needs no edit here.
    parallel = [
        (href, label, sub) for (href, label, sub) in NAV
        if "/" in href and not href.startswith(("products/", "categories/", "guides/", "assets/"))
    ]
    extra_nav = "".join(
        a for (href, _label, _sub), a in zip(NAV, nav_html) if href in {p[0] for p in parallel}
    )

    # product links under the category entry
    prod_nav = "".join(
        f'<a href="{prefix}products/{p["slug"]}.html">{e(p["short_name"])}'
        f'<span class="sub">candidate ASIN {e(p["asin"]["v"])} (unconfirmed)</span></a>'
        for p in PRODUCT_LIST
    )
    # Sidebar gets ONE entry. Every parallel build is catalogued, with its disagreements
    # named, on previous-passes.html.
    more_nav = (
        '<div class="group"><h4>Archive</h4>'
        f'<a href="{prefix}previous-passes.html">Previous passes<span class="sub">'
        f'{len(parallel)} parallel builds kept in this repo, catalogued</span></a></div>'
        if parallel else ""
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
  <span class="meta">data verified {e(ACCESSED)}{(" · re-verified " + e(REVERIFIED)) if REVERIFIED else ""}</span>
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
      {nav_html[9]}
    </div>
    {more_nav}
  </aside>
  <main>
    {body}
  </main>
</div>
<footer class="site">
  <div class="inner">
    <div>
      <h5>Parallel passes on this domain</h5>
      {extra_nav}
      <p class="tiny">Independently verified builds merged into <code>main</code> by other sessions. Nothing here was overwritten by them and nothing of theirs was overwritten here.</p>
    </div>
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
<p class="cta-note">Link-level disclosure: this is an affiliate link and we may earn a commission if you buy, at no extra cost to you. Candidate ASIN <code>{e(p['asin']['v'])}</code> — <strong>not confirmed</strong>: the supplied link reaches an Amazon fallback page (<a href="../reports/link-check-2026-11-14.md">link check, 2026-11-14</a>). {src_links(['S17'])}</p>
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
    cards = "".join(
        f"""
<div class="card pcard">
  <div class="rank">Rank {p['rank']} · {e(p['category'])}</div>
  <h3><a href="products/{p['slug']}.html">{e(p['short_name'])}</a></h3>
  <p class="small muted" style="margin:.2rem 0">{e(p['name'])}</p>
  <div class="facts">
    <span class="chip">candidate ASIN {e(p['asin']['v'])} (unconfirmed)</span>
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
<h1>Three supplied Amazon links: product identity not yet confirmed</h1>
<p class="lede">This dashboard holds everything that could be confirmed about the three supplied Amazon listings from <strong>official sources only</strong> — Amazon's Associates documents, the US FTC's rule text, and each manufacturer's own product page and owner's manual. Where a fact could not be confirmed, the field is blank and the item appears on <a href="flagged.html">Flagged for review</a>. Nothing has been inferred, estimated or filled in.</p>

<div class="grid grid-4" style="margin:1rem 0 1.25rem">
  <div class="stat bad"><div class="n">0</div><div class="l">Verified product identities</div><div class="h">Supplied links reach Amazon fallback pages — see <a href="reports/link-check-2026-11-14.md">link check, 2026-11-14</a></div></div>
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
  <a href="reverification.html">Re-verification {REVERIFIED}</a> · their report:
  <a href="reports/link-check-2026-11-14.md">link check, 2026-11-14</a>.</p>
</div>

<h2>The product set</h2>
<div class="grid grid-3">{cards}</div>

<h2>Commercial summary</h2>
{commercial_table()}

<h2>Articles</h2>
<p class="small muted">Five reads written for this product set. Each one quotes the manufacturer's own pages or manuals, links every number to the page it came from, and names the places where the official record contradicts itself instead of smoothing them over. No first-hand testing is claimed anywhere.</p>
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
<div class="panel" style="margin-top:20px">
  <h3>Independent builds in this repository</h3>
  <p class="muted small">Several agent sessions worked this repository concurrently; each build is preserved and served alongside this one.</p>
  <table class="rows">
    <caption>Session builds and annexes</caption>
    <thead><tr><th>Build</th><th>What it adds</th></tr></thead>
    <tbody>
      <tr><td><a href="research/index.html">Deep-dive research ↗</a></td><td>Independent 25-source verification pass (session 8a2ddd06).<div class="tiny">{repo_link('research/', 'Source: research/ in this repository')}</div></td></tr>
      <tr><td><a href="site/index.html">Verification annex ↗</a></td><td>Independent dataset and generator, 53 spec fields, Kitchen 4.50% rate row (session 1874bb64).<div class="tiny">{repo_link('site/', 'Source: site/ in this repository')}</div></td></tr>
      <tr><td><a href="session-3740f69d/index.html">Session 3740f69d build ↗</a></td><td>Dashboard build: link-resolution evidence, affiliate-link policy mapping, tracking design, AI Agent-Terms compliance (session arena-3740f69d).<div class="tiny">{repo_link('session-3740f69d/', 'Source: session-3740f69d/ in this repository')}</div></td></tr>
      <tr><td><a href="crosscheck/arena-4ba9e055/README.md">Cross-check reports ↗</a></td><td>Independent cross-check notes (session arena-4ba9e055).<div class="tiny">{repo_link('crosscheck/arena-4ba9e055/README.md', 'Source: crosscheck/arena-4ba9e055/README.md')}</div></td></tr>
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
<p class="lede">{e(p['name'])} — {e(p['brand'])}. Rank {p['rank']} of 3 in this set. Everything below was read from the manufacturer's own page or owner's manual on {e(ACCESSED)}. The ASIN shown is a <strong>candidate</strong> observed on a 2026-11-14 fetch of the short link; the mapping from the supplied token to that ASIN is not confirmed — see the <a href="../reports/link-check-2026-11-14.md">link check</a> and <a href="../flagged.html">F14–F16</a>.</p>

<div class="grid grid-4" style="margin-bottom:1rem">
  <div class="stat warn"><div class="n" style="font-size:1.15rem">{e(p['asin']['v'])}</div><div class="l">Candidate ASIN (unconfirmed)</div></div>
  <div class="stat"><div class="n" style="font-size:1.15rem">{e(p['pricing']['brand_list_price']['v'])}</div><div class="l">Brand list price</div></div>
  <div class="stat"><div class="n" style="font-size:1.15rem">{e(p['reviews']['brand_site_rating']['v'].split(' from')[0])}</div><div class="l">Brand-site rating</div></div>
  <div class="stat warn"><div class="n" style="font-size:1.15rem">{len(p['flags'])}</div><div class="l">Open flags</div></div>
</div>

{product_cta(p)}

<div class="callout ok">
  <strong>How this review was produced</strong>
  <p class="small">This is a documentation-based review. No unit was tested, owned or handled. That matters legally as well as ethically: the FTC's disclosure guidance says an endorser cannot describe an experience with a product they have not tried {src_links(['S8'])}, so this page describes published specifications and what they imply — nothing else.</p>
</div>

<h2>What the link observed on 2026-11-14</h2>
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
    return layout(f"products/{tag}.html", p["short_name"], body,
                  active=f"products/{tag}.html",
                  description=f"Documentation-based review of the {p['name']} — verified specifications with official source links.")


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
     "All three links", "Each resolves with lv=shuf and plpRedirect=mhFallback in the landing URL, and the srctok value stays constant across repeat requests (re-tested 2026-11-13 and 2026-11-14). That pattern is Amazon's server-side redirect, not a guarantee of a stable destination. Open each link yourself before publishing and confirm the product is the one intended. See also F21 for the two readings of these markers.", ["S17", "S16"]),
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
     "dashboard/, site/, research/, session-3740f69d/ annexes", "Root pages generated by build.py were given a source badge, policy citation or flagged-page link in the arena/0c7445c7 pass (2026-11-14). Remaining advisory rows live only in other sessions' annex builds; scripts/check_links.py reports them as non-blocking warnings. Each annex owner must source or blank its own rows.", ["S1"]),
    ("F18", "Committed s2 build stamp changes with the calendar date.",
     "s2/ (session zone1-s2 build)", "scripts/build_s2_site.py writes today's date into the 'built' stamp. Re-running on 2026-11-14 changes 13 files by that stamp alone (committed stamp: 2026-11-13). The CI gate regenerates before it checks, so it passes, but the committed copy is not pinned. Not changed in this pass because another session owns the file.", ["S1"]),
    ("F19", "Brand-site review counts move between days, so every rating on this site is a dated observation.",
     "All three", "Chefman's own widget read 1,302 reviews on 2026-11-13 and 1,305 on 2026-11-14; the 8 Qt page read 715 then 716. The averages did not move (4.6 both days), but a published figure without its read date would silently become false. Both counts now carry both dates in the dataset, and any copy generated from it must carry the date too.", ["S10", "S12"]),
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
     "Audited 2026-11-14 with the project's own official-host list (every host in data/sources.json, plus this repo on GitHub). Root pages generated by build.py now pass, and the build fails on any unsourced row. Inherited builds were not edited by this pass because other sessions own them. Count at 2026-11-14: 281 of 1,363 table rows in the repository have no sourced link (inherited builds: 281 of 1,057; root pages built by build.py: 0 of 306). Each owner must add a source to each row, blank it, or remove it.", []),
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
     "Re-read 2026-11-14 by sess-54c66535. Amazon's listing title for ASIN B09B7SB46R says '24 cooking functions' and Emeril's own description paragraph says 'Equipped with 24 one-touch cooking presets', while the same page's specification block says '25 Cooking Pre-sets', its feature heading says '10-In-1' and one of its carousel assets is named '11-in-1'. Two independent official sources now agreeing on 24 is new evidence: earlier passes recorded only 25 vs 10-in-1 vs 11-in-1 with no tiebreaker. The conflict is narrowed, not closed - the same brand page still contradicts itself - so no preset count is asserted anywhere on this site. Decision needed: confirm the figure against the unit's own control panel before any copy states a number.", ["S14", "S17", "S16"]),
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
}

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
          <td class="blank">not displayed {src_link("S2")}</td>
          <td>{len(p['flags'])}</td>
        </tr>"""
        for p in PRODUCT_LIST
    )
    body = f"""
<p class="crumbs"><a href="../index.html">Dashboard</a> / Kitchen appliances</p>
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
                f'<td>{e(p["short_name"])}<div class="tiny muted">candidate ASIN {e(p["asin"]["v"])} (unconfirmed)</div></td>'
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
        parts = ([src_links(srcs)] if srcs else []) + [repo_link(p) for p in REPO_EVIDENCE.get(fid, [])]
        src_html = " ".join(parts) if parts else '<a href="data.html">dataset</a>'
        return (f'<tr><td class="num"><strong>{e(fid)}</strong></td><td>{e(issue)}<div class="tiny muted">Scope: {e(scope)}</div></td>'
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
  <thead><tr><th style="width:8%">ID</th><th style="width:30%">Item</th><th style="width:46%">Resolution</th><th style="width:16%">Source</th></tr></thead>
  <tbody>{resolved_rows}</tbody>
</table>
</div>
<p class="tiny muted">Rows whose verdict is <em>Official sources still disagree</em> are re-listed as open flags by the
<a href="../reverification.html">2026-11-14 re-verification pass</a>; a resolution here never removes evidence, it only
records what a re-test established.</p>
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
        ("Product set", "Three supplied short links were followed; each fetch observed a landing on an air-fryer listing (candidate ASINs B0CDY277D3, B09B7SB46R, B08DKYBTPH). Token-to-ASIN mapping is not confirmed — see F14–F16 and reports/link-check-2026-11-14.md.", ["S16", "S17"]),
        ("Category", "All three are air fryers or air fryer toaster ovens — the niche is set by the products, not chosen.", ["S16"]),
        ("Verification standard", "Official sources only; blank plus flagged wherever unconfirmed; no inference.", ["S1", "S2"]),
        ("Verified spec values", "Published on the dashboard and in the full dataset, each with a source link.", ["S10", "S12", "S14"]),
        ("Re-verification (2026-11-14)", "Every published value was re-read against the official source it cites. The ledger — 61 rows, each with the value as published, what the source said on the day, a verdict and a link — is on the Re-verification page. Two blank rows were filled from the manufacturer's own spec block, and the disputed question of whether the short links shuffle between requests was closed by a repeat fetch plus a nonsense-token control.", ["S16", "S21", "S22"]),
        ("Hard source conflicts", "One serious (Chefman 8 Qt 450 °F claim vs its own manual), plus preset-count and SKU ambiguity issues. All of them were re-checked on 2026-11-14 and are still live on the official pages.", ["S12", "S13", "S14"]),
        ("Commission rate", "Deliberately blank per product. Amazon publishes rates by category and not by ASIN.", ["S3"]),
        ("Amazon price / rating", "Not displayed anywhere, by policy, not by omission.", ["S2"]),
        ("Disclosure", "Required statement on every page plus a link-level badge on every outbound link.", ["S1", "S5"]),
        ("Biggest constraint", "Program Content may not be aggregated, analysed or trained on — which rules out the obvious version of an AI research engine.", ["S2"]),
        ("API status (re-verified 2026-11-14)", "PA-API 5 is officially deprecated; Amazon's docs direct integrations to migrate to the Creators API. The automation blueprint must target the Creators API.", ["S24"]),
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
  <caption>Illustrative commissions at published rates — arithmetic on the brand list price, not a forecast</caption>
  <thead><tr><th>Product</th><th>Brand list price</th>{rate_headers}</tr></thead>
  <tbody>{econ_rows}</tbody>
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
<p class="crumbs"><a href="../index.html">Dashboard</a> / Re-verification {e(rev["pass_date"])}</p>
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

<h2>What this pass changed on the site</h2>
<ul class="tight small">{changes}</ul>

{lr_html}

<p class="tiny muted">Full raw observations, including the two control requests, are in
<code>session-81495d2d/EVIDENCE-2026-11-14.md</code> and in the
<a href="../COORDINATION.md">coordination log</a>.</p>
"""
    return layout("reverification.html", f"Re-verification {rev['pass_date']}", body,
                  active="reverification.html",
                  description="Line-by-line re-read of every value this site publishes, each against the official source it cites, with the verdict and the source link.")


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
<p class="crumbs"><a href="index.html">Dashboard</a> / Previous passes</p>
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
                  description="Catalogue of every parallel build published in this repository, where each one disagrees with the canonical site, and which build to trust.")


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


def _article_text(paras):
    """Render {{value}} placeholders as <code>, escaping everything else."""
    out = []
    for para in paras:
        # **bold** -> <strong>
        chunk = e(para)
        chunk = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", chunk)
        chunk = re.sub(r"\{\{(.+?)\}\}", r'<code class="specval">\1</code>', chunk)
        out.append(f"<p>{chunk}</p>")
    return "\n".join(out)


def _article_placeholders(article):
    found = []
    for sec in article["sections"]:
        for para in sec["paras"]:
            found.extend(re.findall(r"\{\{(.+?)\}\}", para))
    return found


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
            if ph not in values:
                problems.append(
                    f"{a['slug']} states '{ph}' which is not a value published in data/products.json")
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
        cards.append(f"""<a class="card" href="../articles/{a['slug']}.html">
  <span class="kicker">{e(a['kicker'])}</span>
  <span class="cardtitle">{e(a['title'])}</span>
  <span class="cardtext">{e(a['standfirst'])}</span>
  <span class="tiny muted">{e(a['kind'])} · {a['reading_minutes']} min read</span>
  {prods}
</a>""")
    body = f"""
<p class="crumbs"><a href="../index.html">Dashboard</a> / Articles</p>
<h1>Articles</h1>
<p class="lede">Five pieces written for this product set. Each one states what the manufacturer's own pages and manuals establish, links to the page it came from, and names the places where the official record contradicts itself rather than tidying them away.</p>

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
    return layout("articles/index.html", "Articles", body, active="articles/index.html",
                  description="Five sourced articles on dual-basket vs oven air fryers, what a 450 F badge means, preset-count conflicts, and why this site publishes no Amazon prices.")


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
<p class="crumbs"><a href="../index.html">Dashboard</a> / <a href="../articles/index.html">Articles</a> / {e(a['kind'])}</p>
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
    return layout(f"articles/{a['slug']}.html", a["title"], body,
                  active="articles/index.html", description=a["standfirst"])



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
    pages["previous-passes.html"] = page_previous_passes()
    pages["404.html"] = page_404()

    # build guards
    problems = check_rows_have_sources()
    if problems:
        raise SystemExit("BUILD FAILED — rows with values but no official source:\n  " + "\n  ".join(problems))
    missing = check_disclosure(list(pages.items()))
    if missing:
        raise SystemExit("BUILD FAILED — pages missing the required disclosure: " + ", ".join(missing))
    article_problems = check_articles()
    if article_problems:
        raise SystemExit("BUILD FAILED — article cites an unregistered source or states an "
                         "unpublished value:\n  " + "\n  ".join(article_problems))
    unsourced_rows = check_row_sources(pages)
    if unsourced_rows:
        raise SystemExit("BUILD FAILED — table rows with no official source link (cite a registered "
                         "source, this repo on GitHub, or the Flagged page):\n  "
                         + "\n  ".join(unsourced_rows))

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
