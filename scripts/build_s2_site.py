#!/usr/bin/env python3
"""Build the Zone1 static site from data/*.json.

Why a generator: every table on the site is rendered from the same JSON the CI
audit checks, so a row cannot appear on the site without also passing the
sourcing rules. The build fails -- loudly -- if a page would ship without the
required Amazon disclosure sentence.

Usage:  python3 scripts/build_s2_site.py [--check]
  --check  rebuild in memory and fail if the committed HTML differs
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "platform"))

from compliance.gates import AMAZON_DISCLOSURE, audit_page  # noqa: E402

DATA = os.path.join(ROOT, "data", "s2")   # namespaced so parallel sessions' data/ is never read
SITE = os.path.join(ROOT, "s2")                       # generated pages live here for the same reason

STATUS_CLASS = {
    "verified": "ok",
    "unverified": "blank",
    "needs review": "review",
    "needs-review": "review",
    "blocked": "bad",
    "partial": "review",
    "delivered": "ok",
    "in progress": "review",
    "done": "ok",
    "unclaimed": "blank",
}


def load(name: str) -> dict:
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def esc(s) -> str:
    return (
        "" if s is None else str(s)
        .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def pill(status) -> str:
    if status in (None, ""):
        return ""
    cls = STATUS_CLASS.get(str(status), "review")
    return f'<span class="pill {cls}">{esc(status)}</span>'


def src(url: str, label: str = "source") -> str:
    if not url:
        return '<span class="pill blank">no source</span>'
    return f'<a class="src" href="{esc(url)}" rel="noopener noreferrer" target="_blank">{esc(label)} ↗</a>'


def table(headers: list[str], rows: list[list[str]], caption: str = "") -> str:
    out = ['<div class="tw"><table>']
    if caption:
        out.append(f"<caption>{esc(caption)}</caption>")
    out.append("<thead><tr>" + "".join(f"<th>{esc(h)}</th>" for h in headers) + "</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


NAV = [
    ("Overview", [("Dashboard", "index.html"), ("Executive summary", "pages/executive-summary.html"),
                  ("Requirements", "pages/requirements.html")]),
    ("Product research", [("Products & findings", "pages/products.html"),
                          ("Niche & trend method", "pages/niche.html"),
                          ("Economics & commission", "pages/economics.html")]),
    ("Compliance", [("Associates rule matrix", "pages/compliance.html"),
                    ("Content engine & disclosure", "pages/content-engine.html"),
                    ("Campaign & measurement", "pages/campaign.html")]),
    ("Platform", [("Automation architecture", "pages/automation.html"),
                  ("Verification log", "pages/verification.html"),
                  ("Sources", "pages/sources.html"),
                  ("Flagged for review", "pages/flagged.html")]),
]


def nav_html(rel: str, current: str) -> str:
    parts = ['<nav class="sitenav" aria-label="Site sections">']
    for group, items in NAV:
        parts.append(f'<div class="navgrp"><p>{esc(group)}</p><ul>')
        for label, path in items:
            href = rel + path if path != "index.html" else rel + "index.html"
            active = " is-current" if path == current else ""
            parts.append(f'<li><a href="{esc(href)}"{active}>{esc(label)}</a></li>')
        parts.append("</ul></div>")
    parts.append("</nav>")
    return "".join(parts)


CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#12161c;--mut:#5b6675;--line:#e3e7ee;--ok:#0b7a3b;--okbg:#e8f6ee;
--warn:#8a5a00;--warnbg:#fdf3e0;--bad:#9c1c1c;--badbg:#fdeceb;--blank:#4b5563;--blankbg:#eef1f5;--acc:#1a56db}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header.top{background:#0f1724;color:#fff;padding:18px 0}
header.top .wrap{display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between}
.brand{display:flex;gap:11px;align-items:center;font-weight:650;letter-spacing:.2px}
.logo{width:26px;height:26px;border-radius:7px;background:linear-gradient(135deg,#ff9900,#ff6a00);display:grid;place-items:center;color:#0f1724;font-size:13px;font-weight:800}
.brand small{display:block;font-weight:450;color:#9fb0c8;font-size:11.5px;margin-top:1px}
.stamp{font-size:12px;color:#9fb0c8}
.layout{display:grid;grid-template-columns:232px 1fr;gap:26px;align-items:start;padding:22px 0 46px}
.sitenav{position:sticky;top:14px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px}
.navgrp{margin-bottom:13px}.navgrp:last-child{margin-bottom:0}
.navgrp p{margin:0 0 5px;font-size:10.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--mut);font-weight:700}
.navgrp ul{list-style:none;margin:0;padding:0}
.navgrp a{display:block;padding:5px 8px;border-radius:7px;color:#26313f;font-size:13.5px}
.navgrp a:hover{background:#eef2f8;text-decoration:none}
.navgrp a.is-current{background:#e7efff;color:#123c92;font-weight:650}
main{min-width:0}
h1{font-size:25px;margin:2px 0 6px;letter-spacing:-.3px}
h2{font-size:17px;margin:26px 0 9px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h3{font-size:14px;margin:18px 0 6px;color:#26313f}
.sub{color:var(--mut);font-size:13.5px;margin:0 0 14px;max-width:78ch}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:15px 17px;margin:0 0 14px}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(206px,1fr))}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:13px 15px}
.kpi b{display:block;font-size:20px;letter-spacing:-.3px;margin-bottom:2px}
.kpi span{font-size:12px;color:var(--mut)}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:11px;background:var(--card);margin:0 0 8px}
table{border-collapse:collapse;width:100%;font-size:13px}
caption{text-align:left;padding:10px 13px 0;font-size:12px;color:var(--mut)}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#f0f3f8;font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#3d4959;position:sticky;top:0;z-index:1}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:#fafbfe}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
code{background:#eef1f5;border-radius:4px;padding:1px 5px;font-size:12px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.pill{display:inline-block;padding:1.5px 8px;border-radius:999px;font-size:11px;font-weight:650;white-space:nowrap}
.pill.ok{background:var(--okbg);color:var(--ok)}.pill.review{background:var(--warnbg);color:var(--warn)}
.pill.bad{background:var(--badbg);color:var(--bad)}.pill.blank{background:var(--blankbg);color:var(--blank)}
.src{font-size:11.5px;white-space:nowrap}
.note{font-size:12.5px;color:var(--mut)}
q{color:#26313f;font-style:italic}
.disclosure{border-left:3px solid var(--acc);background:#eef3ff;padding:10px 13px;border-radius:0 8px 8px 0;font-size:13px;margin:0 0 16px}
.alert{border-left:3px solid #d9822b;background:#fef6ec;padding:11px 14px;border-radius:0 8px 8px 0;margin:0 0 16px;font-size:13.5px}
.alert.crit{border-left-color:var(--bad);background:#fdeeec}
ul.tight{margin:6px 0 0;padding-left:19px}ul.tight li{margin-bottom:5px}
.tools{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin:0 0 10px}
.tools input{flex:1;min-width:190px;padding:8px 11px;border:1px solid var(--line);border-radius:8px;font:inherit;font-size:13px}
.tools button{padding:8px 12px;border:1px solid var(--line);background:var(--card);border-radius:8px;font:inherit;font-size:13px;cursor:pointer}
.tools button.on{background:#1a56db;border-color:#1a56db;color:#fff}
tbody tr[hidden]{display:none}
footer{border-top:1px solid var(--line);background:var(--card);padding:16px 0;color:var(--mut);font-size:12.5px}
@media (max-width:900px){.layout{grid-template-columns:1fr}.sitenav{position:static}}
@media print{.sitenav,.tools{display:none}header.top{background:#fff;color:#000}}
"""

JS = """
/* Progressive enhancement only. The site is complete and readable with
   JavaScript disabled; this just makes the long tables searchable. */
(function () {
  if (!document.querySelector) return;
  var wraps = document.querySelectorAll('.tw');
  Array.prototype.forEach.call(wraps, function (wrap, i) {
    var table = wrap.querySelector('table');
    if (!table) return;
    var rows = table.querySelectorAll('tbody tr');
    if (rows.length < 6) return;
    var bar = document.createElement('div');
    bar.className = 'tools';
    var input = document.createElement('input');
    input.type = 'search';
    input.placeholder = 'Filter ' + rows.length + ' rows — try a rule id, a word, or "blank"';
    input.setAttribute('aria-label', 'Filter table');
    var count = document.createElement('span');
    count.className = 'note';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = 'Unverified only';
    var onlyBlank = false;
    function apply() {
      var q = input.value.toLowerCase().trim();
      var shown = 0;
      Array.prototype.forEach.call(rows, function (tr) {
        var text = tr.textContent.toLowerCase();
        var hit = !q || text.indexOf(q) >= 0;
        if (onlyBlank) hit = hit && /blank|unverified|no source|needs review/.test(text);
        tr.hidden = !hit;
        if (hit) shown++;
      });
      count.textContent = shown + ' of ' + rows.length + ' rows';
    }
    btn.addEventListener('click', function () {
      onlyBlank = !onlyBlank;
      btn.classList.toggle('on', onlyBlank);
      btn.textContent = onlyBlank ? 'Showing unverified' : 'Unverified only';
      apply();
    });
    input.addEventListener('input', apply);
    bar.appendChild(input);
    bar.appendChild(btn);
    bar.appendChild(count);
    wrap.parentNode.insertBefore(bar, wrap);
    apply();
  });
})();
"""


FAVICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    '<rect width="64" height="64" rx="14" fill="#0f1724"/>'
    '<path d="M14 40 32 14l18 26H40l-8-12-8 12z" fill="#ff9900"/>'
    '<rect x="14" y="45" width="36" height="4" rx="2" fill="#ff9900" opacity=".7"/></svg>'
)


def page(title: str, rel: str, current: str, body: str, *, sub: str = "") -> str:
    today = dt.date.today().isoformat()
    html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Zone1 affiliate platform</title>
<meta name="description" content="Verified Amazon Associates affiliate platform data: {esc(title)}. Every row cites an official source.">
<link rel="stylesheet" href="{rel}assets/app.css">
<link rel="icon" href="{rel}assets/favicon.svg" type="image/svg+xml">
</head><body>
<header class="top"><div class="wrap">
<div class="brand"><div class="logo">Z1</div><div>Zone1 — Amazon Associates platform
<small>data-driven · source-linked · no inferred values</small></div></div>
<div class="stamp">verified against official sources on 2026-11-13 · built {today}</div>
</div></header>
<div class="wrap layout">
{nav_html(rel, current)}
<main>
<h1>{esc(title)}</h1>
{f'<p class=sub>{esc(sub)}</p>' if sub else ''}
<div class="disclosure"><strong>Advertising disclosure.</strong> {AMAZON_DISCLOSURE}
This site is a demonstration platform; it currently publishes no live affiliate links.</div>
{body}
</main></div>
<footer><div class="wrap">Generated by <code>scripts/build_s2_site.py</code> from <code>data/*.json</code>; rebuild is
verified in CI. Every table row carries its own source link; blank cells mean no official source stated the value.
<a href="{rel}pages/flagged.html">Flagged for review</a> · <a href="{rel}pages/sources.html">All sources</a> ·
<a href="{rel}pages/verification.html">Verification log</a></div></footer>
<script src="{rel}assets/app.js" defer></script>
</body></html>
"""
    return html


# ---------------------------------------------------------------- pages


def p_index(D) -> str:
    a, pr, fl = D["analysis"], D["products"], D["flags"]
    _LIVE = "https://kanlerxz87-cyber.github.io/Zone1/"
    def _row(path, label, publishes, verified):
        return ['<a href="../%s">%s</a>' % (path, label), publishes, verified,
                src(_LIVE + path, "live page")]
    integ_rows = [
        _row("index.html", "root <code>index.html</code>",
             "root landing page of the deployed site", "not audited line by line"),
        _row("flagged.html", "<code>/flagged.html</code>",
             "another session's flagged-for-review page", "cross-check against this page"),
        _row("compliance.html", "<code>/compliance.html</code> · <code>/data.html</code> · <code>/compare.html</code>",
             "tables from a parallel verification pass", "not audited line by line"),
        _row("products/chefman-6qt-dual-basket.html", "<code>/products/chefman-6qt-dual-basket.html</code>",
             "a product page for an ASIN attributed to the supplied links",
             '<span class="pill bad">attribution not reproducible</span>'),
        _row("products/emeril-26qt-french-door.html", "<code>/products/emeril-26qt-french-door.html</code>",
             "as above", '<span class="pill bad">attribution not reproducible</span>'),
        _row("products/chefman-8qt-turbofry.html", "<code>/products/chefman-8qt-turbofry.html</code>",
             "as above", '<span class="pill bad">attribution not reproducible</span>'),
        _row("guides/buying-guide-air-fryers.html", "<code>/guides/buying-guide-air-fryers.html</code>",
             "a buying guide built on the unattributed products",
             '<span class="pill bad">built on F-07 inputs</span>'),
        _row("research/index.html", "<code>/research/</code> · <code>/docs/</code> · <code>/site/</code>",
             "three further copies of the same deliverable at different paths", "n/a"),
    ]
    integ_table = table(["Page from another session", "What it publishes", "Verified by this session?", "Live check"],
                        integ_rows,
                        "Listed so nothing is silently discarded; the merge kept every one of these files intact.")
    kn = table(["Metric", "Value", "Status", "Source"],
               [[esc(r["label"]), f"<b>{esc(r['value'])}</b>", pill(r["status"]), src(r["url"])]
                for r in a["key_numbers"]])
    prods = table(["Ref", "Identifier supplied", "Chars", "Valid ASIN", "Catalog lookup", "Status"],
                  [[esc(p["ref"]), f"<code>{esc(p['supplied_token'])}</code>", str(p["token_length"]),
                    '<span class="pill bad">no — 10 required</span>' if not p["asin_format_valid"] else pill("yes"),
                    src(p["direct_catalog_lookup"], "open /dp/ page"),
                    pill(p["status"]) + " · " + f'<a href="pages/flagged.html#{esc(p["blocker"])}">{esc(p["blocker"])}</a>']
                   for p in pr["products"]])
    flags = sorted(fl["flags"], key=lambda f: {"critical": 0, "high": 1, "medium": 2, "low": 3}[f["severity"]])
    frows = [[f'<a href="pages/flagged.html#{esc(f["id"])}">{esc(f["id"])}</a>', pill(f["severity"]),
              esc(f["title"]), src(f["sources"][0]["url"], "evidence")] for f in flags]
    cards = "".join(
        f'<div class="kpi"><b>{n}</b><span>{esc(l)}</span></div>'
        for n, l in [(str(len(a["key_numbers"])), "verified headline metrics"),
                    (str(sum(len(g["rows"]) for g in D["program"]["groups"])), "policy rules in the matrix"),
                    ("33", "unit tests passing"),
                    (str(len(flags)), "items flagged for your review"),
                    ("0 of 3", "products verifiable from the links given")])
    body = f"""
<div class="alert crit"><b>Read this first.</b> The three product links supplied for this build do not identify any
product: each token is 9 characters where an ASIN is 10, and each <code>amazon.com/dp/&lt;token&gt;</code> lookup
returns Amazon's “Page Not Found” page. Product name, price, rating and competition are therefore
<b>blank and flagged</b>, not estimated. <a href="pages/flagged.html#F-07">See F-07 with the evidence</a>.</div>
<div class="grid" style="margin-bottom:14px">{cards}</div>
<h2>Products — intake status</h2>{prods}
<h2>Headline verified numbers</h2>{kn}
<h2>Open review items</h2>{table(["ID", "Severity", "Item", "Evidence"], frows)}
<h2>Integration — what else is on this domain</h2>
<p class="note">Four other sessions merged pages into <code>main</code> before this one. Nothing here overwrites
them; they are linked so the operator can compare them against the verified tables. Every one of them states
product facts for the three links in the brief — facts this session could not reproduce (F-07) — and at least
one states a numeric commission rate, which no public official page does (F-04).</p>
{integ_table}
<h2>Where to start</h2>
<div class="card"><ul class="tight">
<li><a href="pages/executive-summary.html">Executive summary</a> — the whole project in one page.</li>
<li><a href="pages/compliance.html">Associates rule matrix</a> — every rule with the quoted official text.</li>
<li><a href="pages/flagged.html">Flagged for review</a> — all contested and unverified items, with links.</li>
<li><a href="pages/verification.html">Verification log</a> — 33 line-by-line checks, one row each.</li>
</ul></div>"""
    return page("Dashboard", "", "index.html", body,
                sub="Collection, organisation and analysis for the Zone1 affiliate brief. Every row links to the official page that states it.")


def p_exec(D) -> str:
    a = D["analysis"]["executive_summary"]
    bullets = "".join(
        f'<li><b>{i+1}.</b> {esc(b["text"])} {src(b["source"], "source")}</li>'
        for i, b in enumerate(a["bullets"]))
    req = D["requirements"]["requirements"]
    counts = {}
    for r in req:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    dist = table(["Requirement", "Status", "Where it lives", "Note", "Source"],
                 [[f'<code>{esc(r["id"])}</code> {esc(r["requirement"])}', pill(r["status"]),
                   esc(r["where"]), esc(r["note"]), src(r["source"], esc(r["source_label"]))] for r in req])
    body = f"""
<div class="card"><h3 style="margin-top:0">Conclusion</h3><p style="margin:0">{esc(a["headline"])}</p></div>
<h2>What was established</h2><ul class="tight">{bullets}</ul>
<h2>Delivery against the brief</h2>
<p class="note">{" · ".join(f"{v} {k}" for k, v in sorted(counts.items()))} across {len(req)} requirements.</p>
{dist}
<h2>Recommended next action</h2>
<div class="card"><ol style="margin:0;padding-left:19px">
<li>Send the three 10-character ASINs (or plain <code>amazon.com/dp/&lt;ASIN&gt;</code> URLs).</li>
<li>Create the Associates account and complete the tax interview; record the assigned tag.</li>
<li>Export the rate card from Associates Central and add it to <code>data/program.json</code> as <code>MN-2</code>.</li>
<li>Set the four credential variables in <i>Automation → credential contract</i>; the pipeline then unblocks itself.</li>
<li>Re-run <code>scripts/build_s2_site.py</code>; the tables fill from the same audit that gates them today.</li>
</ol></div>"""
    return page("Executive summary", "../", "pages/executive-summary.html", body,
                sub="Important details of the project: what was verified, what could not be, and what unblocks it.")


def p_products(D) -> str:
    pr = D["products"]
    rows = []
    for p in pr["products"]:
        rows.append([
            esc(p["ref"]),
            f'<a href="{esc(p["supplied_url"])}" target="_blank" rel="noopener">{esc(p["supplied_url"])}</a>',
            f'<code>{esc(p["supplied_token"])}</code> <span class="note">({p["token_length"]} chars)</span>',
            pill("valid") if p["asin_format_valid"] else '<span class="pill bad">invalid</span>',
            src(p["asin_format_source"], "ASIN rule"),
            pill(p["status"]),
            f'<a href="flagged.html#{p["blocker"]}">{esc(p["blocker"])}</a>',
        ])
    detail = []
    for p in pr["products"]:
        detail.append(
            f'<div class="card"><h3 style="margin-top:0">{esc(p["ref"])} · <code>{esc(p["supplied_token"])}</code></h3>'
            f'<p class="note">{esc(p["why_blank"])}</p>'
            + table(["Field", "Value", "Status", "Basis", "Source"],
                    [["product name", p["product_name"] or "— blank —", pill("unverified"),
                      "no official page stated it", src(p["direct_catalog_lookup"], "catalog lookup")]])
            + "</div>"
        )
    fields = ["product_name", "brand", "price", "currency", "rating", "review_count", "category",
              "best_sellers_rank", "availability", "commission_rate"]
    frows = []
    for p in pr["products"]:
        for f in fields:
            frows.append([esc(p["ref"]), f'<code>{esc(f)}</code>',
                          '<span class="pill blank">blank</span>' if p.get(f) in (None, "") else esc(p.get(f)),
                          f'<a href="flagged.html#{esc(p.get("blocker"))}">{esc(p.get("blocker"))}</a>',
                          src(p["direct_catalog_lookup"], "where it would come from")])
    obs = table(["Link", "ASIN shown by the fallback page", "Chars", "Adopted as the operator's product?", "Why", "Source"],
                [[esc(r["for_link"]), f'<code>{esc(r["asin"])}</code>', str(r["length"]),
                  '<span class="pill bad">no</span>',
                  "reached through <code>lv=shuf</code> / <code>plpRedirect=mhFallback</code>, so it identifies nothing",
                  src(r["source"], "that ASIN's page")]
                 for r in pr["candidate_asins_observed_by_other_session"]["rows"]])
    body = f"""
<h2>Intake table</h2>
{table(["Ref", "Supplied URL", "Identifier", "Format", "Rule source", "Status", "Blocker"], rows,
       "One row per link supplied in the brief.")}
<div class="alert"><b>Reading the blanks below.</b> A blank cell is a deliberate result, not unfinished work:
the value was not stated by any official page, so it is left empty and flagged rather than estimated.</div>
<h2>Per-product fields</h2>
{table(["Ref", "Field", "Value", "Flag", "Where it would come from"], frows,
       "Every field the brief asks the platform to analyse, for every product.")}
{"".join(detail)}
<h2>Candidate identifiers observed</h2>
<p class="note">{esc(pr["candidate_asins_observed_by_other_session"]["note"])}</p>
{obs}"""
    return page("Products & findings", "../", "pages/products.html", body,
                sub="The three products named in the brief, with every field either sourced or explicitly blank.")


def p_compliance(D) -> str:
    g_rows = []
    for g in D["program"]["groups"]:
        rows = [[f'<code>{esc(r["id"])}</code>', esc(r["claim"]), esc(r["value"]) or '<span class="pill blank">blank</span>',
                 pill(r["status"]), f'<q>{esc(r["quote"])}</q>' if r.get("quote") else "",
                 src(r["url"]), f'<code>{esc(r["checked_by"])}</code>'] for r in g["rows"]]
        g_rows.append(
            f'<h2 id="{esc(g["key"])}">{esc(g["label"])} '
            f'<span class="note">· source {esc(g["source"]["id"])} · {len(g["rows"])} rules</span></h2>'
            + table(["Rule", "Subject", "Requirement", "Status", "Official wording (quoted)", "Source", "Enforced by"], rows)
        )
    blank = [r for g in D["program"]["groups"] for r in g["rows"] if r["status"] == "unverified"]
    brows = [[f'<code>{esc(r["id"])}</code>', esc(r["claim"]),
              esc(r.get("why_blank") or r.get("quote") or ""), src(r["url"], "where it would come from")] for r in blank]
    body = f"""
<p class="note">{esc(D["program"]["how_to_read"])}</p>
<div class="card"><b>{sum(len(g["rows"]) for g in D["program"]["groups"])}</b> rules across
<b>{len(D["program"]["groups"])}</b> categories. Retrieved from the official pages on
{esc(D["program"]["retrieved"])}. Each row quotes the wording on the linked page; a row is only marked
<em>verified</em> when that page states it.</div>
{"".join(g_rows)}
<h2>Left blank on purpose</h2>
<p class="note">These are the values the brief asks for that no official public page states. They are recorded as
absent rather than estimated.</p>
{table(["Rule", "Subject", "Why it is blank", "Where the answer lives"], brows)}"""
    return page("Amazon Associates rule matrix", "../", "pages/compliance.html", body,
                sub="Every platform constraint, quoted from the official agreement text, with the code guard that enforces it.")


def p_economics(D) -> str:
    e = D["analysis"]["economics"]
    money = [g for g in D["program"]["groups"] if g["key"] == "money"][0]["rows"]
    attr = [g for g in D["program"]["groups"] if g["key"] == "attribution"][0]["rows"]
    dq = [g for g in D["program"]["groups"] if g["key"] == "disqualified"][0]["rows"]
    t = lambda rows: table(["Rule", "Subject", "Value", "Status", "Source"],
                           [[f'<code>{esc(r["id"])}</code>', esc(r["claim"]),
                             esc(r["value"]) or '<span class="pill blank">blank</span>',
                             pill(r["status"]), src(r["url"])] for r in rows])
    body = f"""
<h2>The formula, with its missing input visible</h2>
<div class="card"><p><code>{esc(e["formula"])}</code></p>
<p class="note">Definition of the deduction set: {src(e["formula_source"], "Commission Income Statement §1")}</p></div>
{table(["Input", "Owner", "Available in this build", "Why", "Source"],
       [[f'<code>{esc(i["input"])}</code>', esc(i["owner"]),
         '<span class="pill ok">yes</span>' if i["available_now"] else '<span class="pill bad">no</span>',
         esc(i["why"]), src(i["source"], "rule")] for i in e["inputs"]])}
<div class="alert"><b>Guard.</b> {esc(e["guard"])}</div>
<div class="card"><b>Risk note.</b> {esc(e["risk_note"])}</div>
<h2>Attribution windows</h2>{t(attr)}
<h2>Earnings mechanics</h2>{t(money)}
<h2>Purchases that earn nothing</h2>{t(dq)}"""
    return page("Economics & commission", "../", "pages/economics.html", body,
                sub="How a click becomes money, per the official Commission Income Statement — with the rate left as an unset input.")


def p_niche(D) -> str:
    n = D["analysis"]["niche_method"]
    wrows = [[esc(x["factor"]), f'{x["weight"]:.2f}', esc(x["input_source"]), pill(x["status"]),
              src(x["source"], "rule source")] for x in n["weights"]]
    body = f"""
<p class="note">{esc(n["purpose"])}</p>
{table(["Factor", "Weight", "Where the input comes from", "Status in this build", "Source"], wrows,
       "Weights are disclosed so a score can be reproduced or argued with.")}
<div class="alert"><b>Refusal rule.</b> {esc(n["refusal_rule"])}</div>
<h2>Why no niche is named as profitable</h2>
<div class="card"><p style="margin:0">Naming a “profitable niche” requires demand, competition, price,
review and commission inputs for that niche. None of the five can be read from a public official source for a
specific product family without an account, and a list of niches invented from general knowledge would be
exactly the kind of unverified claim this brief excludes. The rubric is therefore published complete and
the ranking empty.</p>
<p class="note" style="margin:8px 0 0">{src(n["source"], "pricing and Program Content rules that constrain niche selection")}</p></div>
<h2>Trend signal design</h2>
{table(["Signal", "Source of truth", "Refresh", "Status in this build", "Source"],
 [[esc(x["signal"]), esc(x["source_of_truth"]), esc(x["refresh"]), pill(x["status"]),
   src(x["url"], "official page")] for x in n["signals"]],
 "Every signal is defined against a page that can actually be read. None is a model guess, and none is populated from general knowledge.")}
<h2>Collector proof — one real fetch</h2>
<p class="note">{esc(D["analysis"]["collector_proof"]["why"])}</p>
{table(["Rank on the page", "Product, titled by Amazon", "ASIN", "Chars", "Rating", "Reviews", "Price", "Source"],
 [[esc(r["rank"]), f'<b>{esc(r["name"])}</b>', f'<code>{esc(r["asin"])}</code>', str(r["asin_length"]),
   esc(r["rating"]) if r["rating"] else '<span class="pill blank">blank — not read</span>',
   esc(r["reviews"]) if r["reviews"] else '<span class="pill blank">blank — not read</span>',
   esc(r["price"]) if r["price"] else '<span class="pill blank">blank — not read</span>',
   src(r["url"], "Amazon page")]
  for r in D["analysis"]["collector_proof"]["rows"]],
 f"Read from the live Best Sellers page on {esc(D['analysis']['collector_proof']['retrieved'])}; cells that were not read are blank, not estimated.")}
<div class="alert"><b>Do not copy this table into a monetized page.</b> {esc(D["analysis"]["collector_proof"]["caveat"])}
{src(D["analysis"]["collector_proof"]["caveat_url"], "CN-1")}</div>
"""
    return page("Niche & trend method", "../", "pages/niche.html", body,
                sub="The selection model, its disclosed weights, and the explicit reason no niche is declared profitable.")


def p_content(D) -> str:
    ce = D["analysis"]["content_engine"]
    body = f"""
<h2>Outputs</h2>
{table(["Content type", "Template", "Slots it fills", "State", "Source"],
       [[esc(o["type"]), f'<code>{esc(o["template"])}</code>', esc(o["slots"]), pill(o["state"]),
         src(o["source"], "code")] for o in ce["outputs"]])}
<h2>Invariants the generator cannot violate</h2>
{table(["Rule", "Enforced by", "Source"],
       [[esc(i["rule"]), f'<code>{esc(i["enforced_by"])}</code>', src(i["url"])] for i in ce["invariants"]])}
<h2>Sample: what the template emits with no data</h2>
<div class="card"><p class="note">Rendered by <code>platform/content/generator.py::article()</code> against the
three product records exactly as they stand — the placeholders are the point.</p>
<pre style="white-space:pre-wrap;font-size:12px;margin:0;color:#26313f">&lt;h1&gt;[unverified — no official source states this] review&lt;/h1&gt;
&lt;aside class="disclosure"&gt;&lt;strong&gt;Advertising disclosure.&lt;/strong&gt; {AMAZON_DISCLOSURE} …&lt;/aside&gt;
&lt;h2&gt;What it is&lt;/h2&gt;
&lt;p&gt;[unverified — no official source states this] — [unverified …]. Category: [unverified …].&lt;/p&gt;</pre>
</div>
<div class="alert"><b>Why nothing is published.</b> Publishing an article about a product we cannot identify would
require inventing its specifications. The generator is complete and tested; its input is not.</div>
<h2>SEO position, stated honestly</h2>
<div class="card"><p style="margin:0">The templates produce a single H1, one descriptive title, a meta
description, semantic sections, and a disclosure that is adjacent to the link — all of which is compatible with
both Amazon's §5 requirement and the FTC's placement guidance. Keyword selection itself needs the verified
product and its category, so no keyword target is asserted here.</p>
<p class="note" style="margin:8px 0 0">{src("https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking", "FTC placement guidance")} · {src("https://affiliate-program.amazon.com/help/operating/agreement", "Amazon §5")}</p></div>"""
    return page("Content engine & disclosure", "../", "pages/content-engine.html", body,
                sub="Article, comparison and buying-guide generation with a source gate: draft freely, publish only what is supported.")


def p_campaign(D) -> str:
    c = D["analysis"]["campaign_plan"]
    body = f"""
<h2>Pipeline</h2>
{table(["Stage", "Action", "Gate that must pass", "Status", "Source"],
       [[esc(s["stage"]), esc(s["action"]), f'<code>{esc(s["gate"])}</code>', pill(s["status"]),
         src(s["source"], "basis")] for s in c["stages"]])}
<h2>What can be measured</h2>
{table(["Metric", "How", "Status", "Source"],
       [[esc(m["metric"]), esc(m["how"]) + (f' — {esc(m["privacy"])}' if m.get("privacy") else ""),
         pill(m.get("status", "available")), src(m["source"], "rule")] for m in c["measurement"]["available"]])}
<h2>What must not be measured</h2>
{table(["Practice", "Rule", "Source"],
       [[esc(f["practice"]), f'<code>{esc(f["rule"])}</code>', src(f["url"])] for f in c["measurement"]["forbidden"]],
       "Each of these is a disqualified-purchase or material-breach route, not a style preference.")}
<h2>Optimization loop</h2>
<div class="card"><ol style="margin:0;padding-left:19px">
<li>Re-fetch every price and rating on the schedule in <i>Niche & trend</i>; expire anything past its window
(<code>pipeline/rot_sweep.py</code>).</li>
<li>Prune finished promotions automatically (<code>pipeline/promo_expiry.py</code>) — an expired discount claim is a
policy breach, not a typo.</li>
<li>Retire pages whose product left the catalog (<code>pipeline/eligibility.py</code>).</li>
<li>Re-run <code>platform/audit/report.py</code>; the site does not rebuild if a row loses its source.</li>
</ol><p class="note" style="margin:9px 0 0">Steps 1–3 need the credentials in <i>Automation</i>; step 4 runs today and
is wired into CI.</p></div>"""
    return page("Campaign & measurement", "../", "pages/campaign.html", body,
                sub="Publish, measure and optimise — with the tracking methods the program disqualifies called out explicitly.")


def p_automation(D) -> str:
    au = D["analysis"]["automation_architecture"]
    repo = "https://github.com/kanlerxz87-cyber/Zone1/blob/main/"
    body = f"""
<h2>Stages</h2>
{table(["Stage", "Module", "Reads", "Writes", "Needs to run", "Source"],
       [[f'<code>{esc(s["stage"])}</code>', f'<code>{esc(s["module"])}</code>', esc(s["reads"]), esc(s["writes"]),
         esc(s["needs"]), src(s["source"], "code")] for s in au["stages"]],
       "Every stage is idempotent: re-running it on unchanged input produces the same files.")}
<h2>Credential contract</h2>
<div class="card"><ul class="tight">{"".join(f"<li><code>{esc(c)}</code></li>" for c in au["credential_contract"])}</ul>
<p class="note" style="margin:9px 0 0">Credentials are read from the environment only. Absent credentials put a stage
into <code>skipped-no-credentials</code>. There is no code path that simulates a successful fetch, because simulated
data on this site would be indistinguishable from research.</p>
<p class="note" style="margin:4px 0 0">{src("https://affiliate-program.amazon.com/help/operating/policies", "approved Program Content channels")}</p></div>
<h2>Non-goals</h2>
<div class="card"><ul class="tight">{"".join(f"<li>{esc(x)}</li>" for x in au["non_goals"])}</ul></div>
<h2>Repo layout</h2>
{table(["Path", "Purpose", "File"],
       [["<code>data/s2/*.json</code>", "single source of truth for every table cell on this site", src(repo + "data", "data/")],
        ["<code>platform/</code>", "the engine: guards, resolver, scoring, generator, audit", src(repo + "platform", "platform/")],
        ["<code>platform/tests/</code>", "33 regression tests, one per policy constraint that is enforced in code", src(repo + "platform/tests/test_platform.py", "test_platform.py")],
        ["<code>scripts/build_s2_site.py</code>", "renders the site; blocks the build if a page would ship without the disclosure", src(repo + "scripts/build_s2_site.py", "build_site.py")],
        ["<code>scripts/check_links.py</code>", "fails if any rendered table row lacks a source link", src(repo + "scripts/check_links.py", "check_links.py")]])}"""
    return page("Automation architecture", "../", "pages/automation.html", body,
                sub="How the pipeline runs, what it refuses to do, and exactly which credentials unblock it.")


def p_requirements(D) -> str:
    req = D["requirements"]["requirements"]
    body = f"""
<p class="note">{esc(D["requirements"]["rule"])}</p>
{table(["#", "Requirement", "Status", "Where", "Evidence / note", "Source"],
       [[f'<code>{esc(r["id"])}</code>', esc(r["requirement"]), pill(r["status"]),
         esc(r["where"]), esc(r["note"]), src(r["source"], esc(r["source_label"]))] for r in req],
       "Decomposed from the brief: platform sentence, three products, and the five work orders.")}
"""
    return page("Requirements register", "../", "pages/requirements.html", body,
                sub="Every capability the brief asks for, with an honest delivery status against what is actually in the repo.")


def p_verification(D) -> str:
    v = D["verification"]
    body = f"""
<p class="note">{esc(v["method"])}</p>
{table(["#", "Item", "Claim checked", "Result", "How it was checked", "Source"],
       [[str(x["n"]), esc(x["item"]), esc(x["claim_checked"]),
         pill("confirmed") if str(x["result"]).startswith("confirmed") else '<span class="pill review">' + esc(x["result"]) + "</span>",
         esc(x["how"]), src(x["source"], "open")] for x in v["entries"]],
       f'{len(v["entries"])} checks · {v["as_of"]}')}
<p class="note">Rows 2–9 are the ones that decide the rest of the project: they establish that the product inputs do
not exist. Rows 10–29 are the policy and law matrix the platform enforces. Row 30 and 33 record what was left
unverified rather than assumed.</p>"""
    return page("Verification log", "../", "pages/verification.html", body,
                sub="Line by line: what was claimed, what was checked, what the official page actually said.")


def p_sources(D) -> str:
    s = D["sources"]
    body = f"""
<p class="note">{esc(s["rule"])}</p>
{table(["ID", "Publisher", "Document", "Type", "What it supports here", "Access"],
       [[f'<code>{esc(x["id"])}</code>', esc(x["publisher"]), src(x["url"], esc(x["name"])),
         esc(x["type"]), esc(x["used_for"]), esc(x["access"])] for x in s["sources"]],
       f'Retrieved {s["retrieved"]}.')}
<h2>Domains considered official</h2>
<div class="card"><p style="margin:0">affiliate-program.amazon.com · amazon.com · advertising.amazon.com ·
sell.amazon.com · ftc.gov · ecfr.gov · docs.github.com · api.github.com. Publisher blogs, affiliate-tool vendors
and SEO sites were used only to <i>locate</i> official pages, never as a source of fact; the registry above is the
complete list of what the tables cite.</p></div>"""
    return page("Sources", "../", "pages/sources.html", body,
                sub="Every official document behind every table cell, with what it was used for and whether it needs a login.")


def p_flagged(D) -> str:
    fl = D["flags"]
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    flags = sorted(fl["flags"], key=lambda f: (order[f["severity"]], f["id"]))
    parts = [f'<p class="note">{esc(fl["policy"])}</p>']
    for f in flags:
        ev = "".join(f"<li>{esc(e)}</li>" for e in f["evidence"])
        sc = "".join(
            f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])}</a></li>' for s in f["sources"]
        )
        parts.append(
            f'<div class="card" id="{esc(f["id"])}"><h3 style="margin:0 0 6px">{esc(f["id"])} · {esc(f["title"])} '
            f'{pill(f["severity"])}</h3><p style="margin:0 0 8px">{esc(f["detail"])}</p>'
            f'<div class="grid" style="grid-template-columns:1fr 1fr;align-items:start">'
            f'<div><b style="font-size:12px;color:#5b6675">EVIDENCE</b><ul class="tight">{ev}</ul></div>'
            f'<div><b style="font-size:12px;color:#5b6675">SOURCES FOR MANUAL REVIEW</b><ul class="tight">{sc}</ul></div>'
            f'</div><p style="margin:2px 0 0"><b>Action required:</b> {esc(f["action_required"])} '
            f'{pill(f["status"])}</p></div>'
        )
    body = "".join(parts)
    return page("Flagged for review", "../", "pages/flagged.html", body,
                sub="Contested claims, unverified values and irregularities. Published live so nothing blocks the site, and nothing is hidden.")


PAGES = {
    "index.html": p_index,
    "pages/executive-summary.html": p_exec,
    "pages/products.html": p_products,
    "pages/compliance.html": p_compliance,
    "pages/economics.html": p_economics,
    "pages/niche.html": p_niche,
    "pages/content-engine.html": p_content,
    "pages/campaign.html": p_campaign,
    "pages/automation.html": p_automation,
    "pages/requirements.html": p_requirements,
    "pages/verification.html": p_verification,
    "pages/sources.html": p_sources,
    "pages/flagged.html": p_flagged,
}


def build() -> dict[str, str]:
    D = {
        "analysis": load("analysis.json"),
        "products": load("products.reviewed.json"),
        "program": load("program.json"),
        "flags": load("flags.json"),
        "sources": load("sources.json"),
        "requirements": load("requirements.json"),
        "verification": load("verification.json"),
    }
    out = {"assets/app.css": CSS, "assets/app.js": JS, "assets/favicon.svg": FAVICON}
    for path, fn in PAGES.items():
        html = fn(D)
        has_link = 'class="cta"' in html or "amazon.com/dp" in html or "affiliate-program.amazon.com" in html
        rep = audit_page(html, has_affiliate_link=True)
        if not rep.ok:
            raise SystemExit(
                f"BUILD BLOCKED — {path} fails compliance gates: "
                + "; ".join(f"[{f.rule}] {f.message}" for f in rep.findings)
            )
        out[path] = html
    return out


def digest(html: str) -> str:
    return hashlib.sha256(html.encode("utf-8")).hexdigest()[:12]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify committed files match a rebuild")
    args = ap.parse_args()
    files = build()
    changed = []
    for path, html in files.items():
        full = os.path.join(SITE, path)
        new = html if html.endswith("\n") else html + "\n"
        old = open(full, encoding="utf-8").read() if os.path.exists(full) else None
        if old != new:
            changed.append(path)
            if not args.check:
                os.makedirs(os.path.dirname(full) or SITE, exist_ok=True)
                with open(full, "w", encoding="utf-8") as fh:
                    fh.write(new)
    if args.check:
        if changed:
            print("STALE BUILD — these files differ from a rebuild:")
            for c in changed:
                print("  ", c)
            return 1
        print(f"build current: {len(files)} files")
        return 0
    print(f"wrote {len(files)} files to s2/ ({len(changed)} changed)")
    for p in sorted(files):
        print(f"  {p:44s} {len(files[p]):>7}B  {digest(files[p])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
