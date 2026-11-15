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
SITE_TAGLINE = "Air-fryer decisions, backed by sources"
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
# Additive pass-7 ledger (2026-11-14, arena-052f2c9f): independent re-verification round 7.
# Owned entirely by this session's folder; the page omits the section if the file is absent.
_p7 = ROOT / "session-052f2c9f" / "pass7.json"
PASS7 = json.loads(_p7.read_text(encoding="utf-8")) if _p7.exists() else None

# Decision layer (added 2026-11-15, arena/3ddfa50e). Two registers that exist to be reviewed
# rather than acted on: the suggestions queue and the open-questions register. Both are
# generated from JSON so a reviewer edits data, never a template.
SUGGESTIONS = load("suggestions.json")
QUESTIONS = load("questions.json")
SUG_BY_ID = {s["id"]: s for s in SUGGESTIONS["suggestions"]}

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
    ("index.html", "Home", "A clear guide to three air-fryer formats"),
    ("categories/kitchen-appliances.html", "Category: Kitchen", "All tracked products in one category"),
    ("compare.html", "Comparison", "Verified-only side-by-side matrix"),
    ("guides/buying-guide-air-fryers.html", "Buying guide", "How to choose a form factor"),
    ("articles/index.html", "Articles", "Sourced reads — comparisons, explainers, policy"),
    ("data.html", "Full dataset", "Every field, value, source and gap"),
    ("platform.html", "Platform blueprint", "The automation and compliance design"),
    ("compliance.html", "Compliance", "Program rules, quoted, with sources"),
    ("flagged.html", "Flagged for review", "Unverified values and irregularities"),
    ("suggestions.html", "Suggestions", "Review site improvements before implementation"),
    ("questions.html", "Questions and gaps", "Known facts, missing answers and discovery steps"),
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
footer.site h5{color:#405548}
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

"""

JS = r"""
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


def layout(page_rel, title, body, active=None, description=""):
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
      {N("suggestions.html")}
      {N("questions.html")}
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
      <h5>Research archive</h5>
      <p>Older verification builds and supporting reports are kept separate from the main buying guide.</p>
      <p><a href="{prefix}previous-passes.html">Browse prior passes and annexes →</a></p>
    </div>
    <div>
      <h5>Disclosure</h5>
      <p><strong>{e(DISCLOSURE)}</strong></p>
      <p>We may earn a commission from a qualifying purchase made through an eligible link. The three supplied Amazon short links have not been confirmed to match the named models or carry this site's Associates tracking ID. Amazon prices, availability and ratings are not published here.</p>
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

<div class="callout bad link-status" id="link-status">
  <div class="link-status-heading"><span class="pill pill-warn">Before shopping</span><strong>Product identity, account approval and affiliate tracking are not confirmed.</strong></div>
  <p class="small">Recorded checks through 2026-11-15 observed fallback-style redirects for the three supplied short links. We cannot confirm that each link reaches the named manufacturer model, carries the correct Associates tag, or that the Associates account is approved. Verify the model and account status in Amazon before relying on a purchase link. {src_links(['S17', 'S2'])} <a href="reports/link-check-2026-11-14.md">Read the redirect evidence</a> · <a href="flagged.html">Flagged for review</a> · <a href="questions.html#q-01">Product-link question</a> · <a href="questions.html#q-03">Account-status question</a>.</p>
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
      <p class="small">The Emeril is described as a 26 QT French-door toaster-oven combo, and the manual documents a rotisserie. Its preset-count claims differ across official pages; see the flag before treating the count as settled. {src_links(['S14', 'S15'])}</p>
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
      <td class="small"><span class="pill pill-warn">Conflicting claims</span><div class="tiny">Owner's manual names 24; product page states 25. Neither count is selected as definitive.</div><div class="tiny">{src_links(['S15', 'S14'])} <a href="flagged.html">Flagged</a></div></td>
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

<h2>Commercial summary</h2>
{commercial_table()}

<h2 id="evidence">Under the hood: how much of this is actually confirmed</h2>
<p class="small muted">Everything from here down is the verification layer — useful if you want to know how
much to trust a number, not required reading before buying. The same material, in full, is on
<a href="data.html">the dataset</a>, <a href="reverification.html">the re-verification ledger</a> and
<a href="flagged.html">Flagged for review</a>.</p>

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
    return layout("index.html", "Air fryer buying guide", body, active="index.html",
                  description="A source-led comparison of three air-fryer formats, with manufacturer specifications, visible gaps and the status of the supplied Amazon links.")


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
<p class="lede">{e(p['name'])} — {e(p['brand'])}. These are document-based product notes, not a ranking or hands-on review. Specifications below come from the manufacturer's product page or owner's manual, accessed {e(ACCESSED)}. The candidate ASIN comes from recorded link checks, but the supplied short-link-to-model mapping is not confirmed; see the <a href="../reports/link-check-2026-11-14.md">redirect evidence</a> and <a href="../flagged.html">Flagged for review</a>.</p>

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
     "dashboard/, site/, research/, session-3740f69d/ annexes", "Root pages generated by build.py were given a source badge, policy citation or flagged-page link in the arena/0c7445c7 pass (2026-11-14). Remaining advisory rows lived only in other sessions' annex builds; scripts/check_links.py reported them as non-blocking warnings. **CLOSED 2026-11-14 by sess-7111e2b6** along with F25: a row-source pass now runs inside the research/ and site/ generators, and scripts/source_rows.py applies it to the hand-authored annex builds. The advisory list is empty, and the gate's own definition was corrected first, so that it can see single-quoted hrefs and every flagged-page filename.", ["S1"]),
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
    # sess-ce4070ad, pass 7, 2026-11-14. NOTE (2026-11-15, arena/3ddfa50e): this row was published as F36
    # while a product-level row in data/products.json was also published as F36. Two rows, one number. The
    # product row is re-sourced from S16 to S28 by this pass and keeps F36 because three session evidence
    # files cite it by that number; this programme-level row moves to F41. Flag F40 records the collision.
    ("F41", "Published flag F10 says the short links' srctok marker \u201cstays constant across repeat requests\u201d; the repository's own published evidence shows the marker changes and only the destination is stable.",
     "All three links",
     "Recorded 2026-11-14 by sess-ce4070ad (observation round 6). Stable across every reading, including today's two independent fetches: each link.amazon token resolves to the same ASIN with the same listing title \u2014 B04G1MEwY \u2192 B0CDY277D3, B02NbDxp3 \u2192 B09B7SB46R, B00hJ57DV \u2192 B08DKYBTPH, now re-confirmed by six sessions over two days. Not stable: the btn_ref/srctok marker in the landing URL \u2014 srctok-2cef40d2904c29d8 on 2026-11-13; srctok-1e229870efde5acf changing to srctok-397b5ba66db39bbf on a cache-busted repeat minutes later (sess-81495d2d's published evidence, row 4); srctok-704dc575b940a94c (sess-54c66535); srctok-0740a2e990c9bbb3, the same value in two independent fetches by sess-840a25d3 and sess-ce4070ad later the same day. F10's constancy wording therefore overstates what the evidence supports: it is the ASIN + title destination that is constant, not the marker. Decision needed: reword F10 to claim destination stability only. F10 is another session's register row and is left verbatim.", ["S17", "S16"]),

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
    ("F43", "Two wording advisories on the Suggestions and Questions pages (reader-facing precision, no data value affected).",
     "suggestions.html and questions.html (PR #58, X-633b115f)",
     "Recorded 2026-11-15 by arena-b1e7b4bc. (a) The Suggestions lede says 'None of them has been implemented', but for SG-03, SG-04, SG-05 and SG-11 option A is the current, already-implemented state ('Keep...', 'Keep blank and link to the live Amazon page (current, compliant)'), so those rows read more accurately as 'confirm the current state' than as pending work. (b) Q-01's 'How to find out' says to check the owner's Associates account for which tag the short links carry - the tag is not observable from the account's tracking-ID page either (flag F6); only whoever created the short links knows the mapping. Decision needed: reword the lede and the Q-01 cell, or accept the current phrasing. Both rows' facts and sources check out; this flag is about wording only.",
     []),

    # ------------------------------------------------------------------ #
    # Verification pass 9 - session 42ca97ad, 2026-11-15.
    # Raw evidence: session-42ca97ad/EVIDENCE-2026-11-15.md
    # ------------------------------------------------------------------ #
    ("F44", "The Amazon department category is now read directly on all three listings; the rate itself still needs the Earnings report.",
     "All three products \u2014 commission rate",
     "Recorded 2026-11-15 by session 42ca97ad. The annex register\u2019s row F-06 recorded that the browse-node path \u2018Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers\u2019 had been read directly on B09B7SB46R only, and named reading the other two listings as the confirmation step. This session fetched all three supplied link.amazon short links and read the identical breadcrumb on B0CDY277D3 and B08DKYBTPH as well, so the evidence is now three for three rather than one for three. It still does not establish the category Amazon applies when a commission is settled: only the Associates Earnings report names the category on a shipped line, so the two candidate rows (Kitchen 4.50%, All Other 4.00%) remain the honest presentation until a sale exists. Decision needed: publish Kitchen 4.50% as the working rate with the breadcrumb cited (SG-10 path A), or keep both rows until the first Earnings report lands.",
     ["S3", "S16", "S28", "S29"]),
    ("F45", "Ten article sentences spliced a published display label into a mid-sentence position. Found, fixed and guarded.",
     "articles/ prose, and the build\u2019s article gate",
     "Recorded 2026-11-15 by session 42ca97ad. The article prose in data/articles.json interpolates published values into sentences. Ten of those interpolations put a display label \u2014 \u2018Two 3-quart baskets\u2019, \u2018Designed for 4-6 people\u2019, \u2018Fries, Chicken, Fish, Meat (one-touch)\u2019, \u2018Limited 1-year warranty \u2026\u2019 \u2014 into a position where its capital is wrong, so the sentences read as machine output: \u2018The dual-basket unit is 6 Qt / 5.67 L as Two 3-quart baskets\u2019, \u2018splits a 6 Qt / 5.67 L cavity into Two 3-quart baskets\u2019. The defect was invisible to every earlier verification pass, because each value is genuinely published and correct in a table; it only appears when the page is read as prose, which is what a shopper does. Fixed by adding a {{value::prose form}} syntax whose prose form may differ from the published value in letter case and nothing else, enforced by check_articles(), and by adding check_article_splices(), which fails the build when a capitalised value is spliced into a mid-sentence position. Both guards were proven to fire: the build failed on exactly these ten defects before the fix and passes after it. No published value changed and no source changed.",
     ["S1"]),
    ("F46", "The Application Review Process page was not re-read this pass; its figures are carried forward from an earlier fetch.",
     "S4 \u2014 the Associates application criteria",
     "Recorded 2026-11-15 by session 42ca97ad. This pass re-fetched the Program Policies, the Standard Commission Income Statement, both Chefman product pages, the Emeril product page, all three owner\u2019s manuals, all three supplied short links, 16 CFR Part 255 and 16 CFR Part 465. It did not load the Application Review Process page (S4). The figures the repository carries for it \u2014 three qualifying sales within 180 days, roughly ten posts, content recent within about sixty days, a social follower floor of about five hundred \u2014 are carried forward from earlier logged fetches and are NOT re-confirmed by this pass. The sixty-day recency requirement is load-bearing for any content-refresh schedule the owner adopts, so it must be re-read before it is used as a scheduling rule rather than quoted from this repository. What was and was not fetched is listed item by item in session-42ca97ad/EVIDENCE-2026-11-15.md section 6.",
     ["S4"]),
    ("F47", "Three files under data/ are read by no build, and one of them is a stale copy of a register that is published.",
     "data/flagged.json, data/commission-rates.csv, data/products.csv",
     "Recorded 2026-11-15 by session 42ca97ad. A reference scan of every loader in the repository shows that scripts/build_site.py and scripts/verify_site.py read data/verified/, not data/. The root-level data/flagged.json is therefore an orphan: it holds a 13-row register whose live counterpart is data/verified/flagged.json (17 rows), and the two disagree across 85 lines \u2014 including the browse-node observation this pass has just updated, which would otherwise leave two registers saying different things about the same fact. data/commission-rates.csv and data/products.csv are read by nothing in the repository; the first is a CSV transcription of the Standard Commission Income Statement, the second the 2026-11-13 link-check ledger that records the bare-token 404 and the fallback redirect, and both are evidence worth keeping if they are labelled as evidence. Nothing published depends on any of the three, so this is a maintenance risk rather than a correctness bug, but a reader who opens data/flagged.json sees a register that no longer matches the site. Decision needed: delete the three orphans, or keep them explicitly as dated evidence with a header that says so.",
     ["S1"]),
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
    "F42": ["suggestions.html", "questions.html", "data/flags.json", "s2/"],
    "F43": ["suggestions.html", "questions.html"],
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
    return layout("compare.html", "Comparison", body, active="compare.html",
                  description="Verified-only comparison of three air fryers, with gaps left visible and every value linked to an official source.")


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
        ("Re-verification (2026-11-15)", "A ninth pass re-fetched every source itself rather than trusting the recorded ones: the Program Policies, the Commission Income Statement, both Chefman product pages, the Emeril product page, all three owner's manuals, all three supplied short links, 16 CFR Part 255 and 16 CFR Part 465. All 43 specification rows were checked against the page each one cites; none was found wrong and no published value changed. The raw evidence, including the sources deliberately not fetched, is in the repository.", ["S2", "S3", "S10", "S12", "S14", "S18"]),
        ("Hard source conflicts", "One serious (Chefman 8 Qt 450 °F claim vs its own manual), plus preset-count and SKU ambiguity issues. All of them were re-checked on 2026-11-14 and are still live on the official pages.", ["S12", "S13", "S14"]),
        ("Commission rate", "Still blank per product, but on firmer ground. Amazon publishes rates by category and not by ASIN. All three listings were re-read on 2026-11-15 and all three render the browse-node path Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers, so Kitchen at 4.50% is the well-evidenced working rate. The settlement-time category still has to come from the Associates Earnings report, so both candidate rows are shown.", ["S3", "S16", "S28", "S29"]),
        ("Amazon price / rating", "Not displayed anywhere, by policy, not by omission.", ["S2"]),
        ("Disclosure", "Required statement on every page plus a link-level badge on every outbound link.", ["S1", "S5"]),
        ("Biggest constraint", "Program Content may not be aggregated, analysed or trained on — which rules out the obvious version of an AI research engine.", ["S2"]),
        ("API status (re-verified 2026-11-14)", "PA-API 5 is officially deprecated; Amazon's docs direct integrations to migrate to the Creators API. The automation blueprint must target the Creators API.", ["S24"]),
        ("Editorial defect found and fixed", "Ten article sentences spliced a published display label into a mid-sentence position, so the prose read as machine output — 'splits a cavity into Two 3-quart baskets'. Every value was genuinely published and correct in a table, which is why eight earlier verification passes missed it. Fixed, and the build now fails if it recurs. This is the clearest evidence on the site that reading the page as a reader, not as a database, is a separate job from verifying it.", ["S1"]),
        ("Next decision", "Resolve the remaining flagged items, then publish, then apply. The decision queue is on the Suggestions page; the information gaps are on the Questions page.", ["S4"]),
    ]
    rows = "".join(
        f'<tr><td><strong>{e(k)}</strong></td><td>{e(v)}</td><td>{src_links(s)}</td></tr>' for k, v, s in facts
    )
    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Executive summary</p>
<h1>Executive summary</h1>
<p class="lede">A one-page briefing for someone who will not read the rest. The short version: the product data is good, the economics are provable only within narrow limits, and the compliance constraint is the design constraint.</p>

<div class="callout note">
  <strong>Pass 9 — 2026-11-15 (most recent).</strong>
  <p class="small">This pass re-fetched every official source itself instead of trusting the recorded ones,
  and checked all 43 specification rows against the page each one cites. Nothing was found wrong and no
  published value changed. Three things did change. First, the Amazon browse-node path
  <em>Home &amp; Kitchen &gt; Kitchen &amp; Dining &gt; Small Appliances &gt; Fryers &gt; Air Fryers</em> was read
  directly on all three listings, where an earlier pass had read it on one; the commission evidence is now
  three-for-three (<a href="flagged.html">F44</a>). Second, ten article sentences were found to splice a
  published label into mid-sentence position, so the prose read as machine output; they are fixed and the build
  now fails if it recurs (<a href="flagged.html">F45</a>). Third, the questions register gained four rows that
  are <em>known and sourced</em> and therefore carry an explicit answer, and four new suggestions were added.
  One source, the Application Review Process page, was <em>not</em> re-read this pass and is flagged as
  carried-forward rather than confirmed (<a href="flagged.html">F46</a>). Raw evidence:
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
  <p class="small">Every specification asserted on the site was read from the manufacturer's own product page or owner's manual on {e(ACCESSED)}, and each one carries a clickable link to it. {len(SOURCES["sources"])} sources are used; none is a retailer, a review aggregator or an affiliate blog. Values that could not be confirmed are blank and listed, which is the only honest way to publish a comparison table.</p>
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
  <p class="small">Eight earlier passes checked every value against its source and found nothing wrong — correctly.
  But a value that is right in a table can still be wrong in a sentence, and ten of them were: a published
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

<h2>Recommendation</h2>
<ol class="tight small">
  <li><strong>Publish this build.</strong> It satisfies the content substance a review looks for, and it is honest under inspection.</li>
  <li><strong>Clear the flags that change copy first</strong> — F3 (the 450 °F conflict), F4/F5 (preset counts), F1/F2 (model mapping). Those decide what the pages may assert.</li>
  <li><strong>Fix attribution before driving traffic</strong> — confirm the Associates tag and create sub-tags; F6 and F7.</li>
  <li><strong>Then apply, and work the 180-day window deliberately</strong> {src_links(['S4'])}.</li>
  <li><strong>Only pursue price and rating display if API access is granted.</strong> Until then, absence is the compliant state.</li>
  <li><strong>Decide what the AI agent is allowed to read before writing the research pipeline.</strong> The IP License forbids using Amazon's Program Content to build or improve models, and forbids aggregating or analysing it without written approval {src_links(['S2'])}. The version of the brief that is lawful runs on manufacturers' own pages — which is the version this repository already implements. See <a href="suggestions.html#sg-17">SG-17</a>.</li>
  <li><strong>Decide the product set before the next content push.</strong> Two of the three products share a brand and a form factor, which caps what the comparison can answer. See <a href="suggestions.html#sg-19">SG-19</a>.</li>
</ol>

<p class="small" style="margin-top:1.5rem"><a class="btn btn-ghost" href="../EXECUTIVE-SUMMARY-PASS9.md">Download this pass's markdown briefing</a> <a class="btn btn-ghost" href="../EXECUTIVE-SUMMARY.md">Earlier briefing</a> <a class="btn btn-ghost" href="../flagged.html">See every open flag</a></p>
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
                  description="Catalogue of every parallel build published in this repository, where each one disagrees with the canonical site, and which build to trust.")


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

    # summary table - every row links to its own evidence so the row-source gate is satisfied
    rows = []
    for x in items:
        ev_links = " ".join(
            f'<a href="{e(y["url"])}" target="_blank" rel="noopener">{e(y["label"].split(" - ")[0][:38])} ↗</a>'
            for y in x["evidence"]
        )
        rows.append(
            f'<tr><td class="num"><a href="#{e(x["id"].lower())}">{e(x["id"])}</a></td>'
            f'<td>{e(x["title"])}</td><td class="small">{e(x["area"])}</td>'
            f'<td class="num">{x["impact"]*x["confidence"]}</td>'
            f'<td class="small">{_effort_chip(x["effort"])} {e(x["risk_of_not_doing"].split(".")[0])}</td>'
            f'<td class="small">{ev_links}</td></tr>'
        )

    body = f"""
<p class="crumbs"><a href="../index.html">Home</a> / Suggestions</p>
<h1>Suggestions, and a place to choose between them</h1>
<p class="lede">{len(items)} things this project believes would materially improve this site, in priority order.
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

<h2>At a glance</h2>
<table>
  <thead><tr><th>#</th><th>Suggestion</th><th>Area</th><th>Priority</th><th>Effort · cost of waiting</th><th>Evidence</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
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
  <a href="questions.html">This pass's open questions</a>
</div>
"""
    return layout("marketing-directions.html", "Suggestions", body, active="marketing-directions.html",
                  description="Reviewed, evidence-backed suggestions for the site, each with alternative paths and a recommendation, for the owner to choose before anything is implemented.")


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
<table>
  <thead><tr><th>#</th><th>Question</th><th>Group</th><th>State</th><th>Source</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>

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
    return layout("questions.html", "Open questions", body, active="questions.html",
                  description="The questions, information and answers that must be settled before a decision on this site is reasonable, separated into known, discoverable, not-stated and account-only.")


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
<p class="crumbs"><a href="index.html">Home</a> / Suggestions</p>
<h1>Suggestions: choose the path before anything changes</h1>
<p class="lede">{len(SUGGESTIONS)} suggestions to improve the site's design, trust, content and measurement. <strong>None of them has been implemented.</strong> Each one lists the options. Pick an option for each ID you want, and only then will the change be made.</p>

<div class="callout warn"><strong>How to decide.</strong> Each row has a basis. Where the basis is an official Amazon or FTC source, the link goes to that source. Where the row is a design opinion, it says so and points to <a href="flagged.html">Flagged for review</a>. The options run from the current state (A) to the recommended path.</div>

<div class="tablewrap">
<table>
  <caption>Suggestions and the options for each</caption>
  <thead><tr><th>ID</th><th>Suggestion</th><th>Basis and source</th><th>Options</th><th>Effort</th><th>Your choice</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>
</div>

<h2>Information needed before some of these can be decided</h2>
<p class="small">Several suggestions depend on a fact not yet known. Those facts are listed, with the way to find each one, on the <a href="questions.html">Questions and information gaps</a> page.</p>
"""
    return layout("suggestions.html", "Suggestions", body, active="suggestions.html",
                  description="Site, design, trust, content and measurement suggestions, with options for the owner to choose before any change is made.")


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
<p class="crumbs"><a href="index.html">Home</a> / Questions and information gaps</p>
<h1>What must be answered before a decision is reasonable</h1>
<p class="lede">{len(QUESTIONS_ALT)} questions. For each one: what the repository already holds (with its official source), what is still missing, how to find the missing fact, and which decision it unblocks. Nothing in the <em>missing</em> column has been filled in with an estimate.</p>

<div class="callout warn"><strong>Read this first.</strong> Q-01 and Q-06 decide most of the other choices: which products the links really point to, and which Amazon store the site can promote. Answer those two before the product pages are extended.</div>

<div class="tablewrap">
<table>
  <caption>Questions, known facts, gaps and how to close each gap</caption>
  <thead><tr><th>ID</th><th>Question</th><th>Known (sourced)</th><th>Missing</th><th>How to find out</th><th>Unblocks</th></tr></thead>
  <tbody>{"".join(rows)}</tbody>
</table>
</div>

<p class="small" style="margin-top:1.5rem">Related: <a href="suggestions.html">Suggestions</a> · <a href="flagged.html">Flagged for review</a> · <a href="executive-summary.html">Executive summary</a></p>
"""
    return layout("decision-gate.html", "Questions and information gaps", body, active="decision-gate.html",
                  description="Questions that must be answered before decisions, what is known with sources, what is missing, and how to find it.")


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

    This is the guard behind flag F45. A display label such as "Two 3-quart
    baskets" is a correct answer to "what is the capacity?" and a broken
    sentence inside "divided into Two 3-quart baskets". The defect is not
    visible in a data table, which is why it survived eight earlier passes:
    it only shows up when the page is read as prose.
    """
    problems = []
    for sec in article["sections"]:
        for para in sec["paras"]:
            pos = 0
            for m in PLACEHOLDER_RE.finditer(para):
                before = para[:m.start()]
                raw = m.group(1)
                pub, prose = _split_placeholder(raw)
                shown = prose if prose is not None else pub
                if not shown[:1].isupper():
                    pos = m.end()
                    continue
                if _is_identifier(shown):
                    pos = m.end()
                    continue
                # First non-space token of the paragraph: a capital is correct.
                if before.strip() == "":
                    pos = m.end()
                    continue
                # A colon, quote, bracket or dash introduces the value, so a
                # capital is correct there too.
                stripped = before.rstrip()
                if stripped and stripped[-1] in _CAP_OK_BEFORE:
                    pos = m.end()
                    continue
                problems.append(
                    f"{article['slug']} §'{sec['h']}': the value {pub!r} is spliced into "
                    f"mid-sentence in a position where its capital is wrong "
                    f"(rendered as {shown!r}). Use a prose form "
                    f"({{{{{pub}::lower-case}}}}) or rewrite the sentence."
                )
                pos = m.end()
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
        cards.append(f"""<article class="card article-card">
  <span class="kicker">{e(a['kicker'])}</span>
  <a class="cardtitle" href="../articles/{a['slug']}.html">{e(a['title'])}</a>
  <span class="cardtext">{e(a['standfirst'])}</span>
  <span class="tiny muted">{e(a['kind'])} · {a['reading_minutes']} min read</span>
  {prods}
</article>""")
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
    return layout("articles/index.html", "Articles", body, active="articles/index.html",
                  description="Eight sourced articles on dual-basket vs oven air fryers, what a 450 F badge means, preset-count conflicts, capacity from published numbers, and why this site publishes no Amazon prices.")


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
    return layout(f"articles/{a['slug']}.html", a["title"], body,
                  active="articles/index.html", description=a["standfirst"])



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
    ids = re.findall(r'<tr><td class="num"><strong>(F\d+)</strong>', page)
    dupes = sorted(k for k, v in Counter(ids).items() if v > 1)
    if dupes:
        return [f"flag id(s) rendered more than once on flagged.html: {', '.join(dupes)}"]
    return []


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
    pages["suggestions.html"] = page_suggestions()
    pages["questions.html"] = page_questions()
    pages["decision-gate.html"] = page_questions_alt()
    pages["marketing-directions.html"] = page_suggestions_alt()
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
    article_page_problems = check_article_pages(pages)
    if article_page_problems:
        raise SystemExit("BUILD FAILED — article page violated a disclosure/claims rule:\n  "
                         + "\n  ".join(article_page_problems))
    flag_id_problems = check_flag_ids_unique()
    if flag_id_problems:
        raise SystemExit("BUILD FAILED — flag register integrity:\n  " + "\n  ".join(flag_id_problems))
    ref_problems = check_question_block_refs()
    if ref_problems:
        raise SystemExit("BUILD FAILED — decision-layer cross-reference:\n  " + "\n  ".join(ref_problems))
    price_problems = check_no_price_tracking(pages)
    if price_problems:
        raise SystemExit("BUILD FAILED — Prohibited feature (Program Policies 6(y)):\n  "
                         + "\n  ".join(price_problems))
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
    locs = "".join(
        f"  <url><loc>{base}{'' if rel == 'index.html' else rel}</loc></url>\n"
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
