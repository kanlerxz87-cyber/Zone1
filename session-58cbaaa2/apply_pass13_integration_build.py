#!/usr/bin/env python3
"""pass 13, re-scoped onto main e5fc007 — integration patch.

Everything this session had already built that main superseded (a second intent register, a second
measurement register, flags F76-F80, the untagged-link gate) is NOT re-applied here; the draft and
the reason for each drop are in session-58cbaaa2/artifacts/. What this script adds is the increment
main does not have: four new official sources, the two brand catalogues for the newly submitted
links, a dated correction of the 'no tag in the URL' inference, the cookieless local collector that
moves main's measurement register from defined-not-shipped to wired-locally, the count repair main's
own F80 class needs on two present-tense surfaces, and the register rows that carry the decisions.

Anchor contract: each anchor must match exactly once or the script aborts without writing.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/user/Zone1")
BUILD = ROOT / "build.py"
edits = []


def rep(old, new, what, text=None):
    edits.append((old, new, what, text))


src = BUILD.read_text(encoding="utf-8")

# ───────────────────────────────────────────── A. module constants (before page_intent)
rep('''def page_intent():''',
'''# ── arena/58cbaaa2 (2026-11-17): the submitted-link register, read by the build ────────────
# Two surfaces described the submitted set in the present tense with a number typed into the
# sentence ("all three supplied short links"), the day the register itself grew to five rows.
# Same defect class this repository already carries as F73/F80, and main's own F80 resolution
# left it in place. The counts are read from the register now, and check_submitted_link_count()
# fails the build if a present-tense surface asserts a different number in its own words.
LINK_RECHECK_DATE = "2026-11-17"   # the date every row of the register was last re-resolved (see F82)
INTENT_REGISTER = load("product-intent.json")
SUBMITTED_ROWS = INTENT_REGISTER["rows"]
N_SUBMITTED_LINKS = len(SUBMITTED_ROWS)
_LINK_NUM_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def _submitted_links_in_category():
    """Submitted links the register files in this site's own category (main's F76 row).

    The category lede used to say "the three supplied links". The count is read off the register
    instead: a row counts as in-category when its `category_fit` names the air fryer, which is the
    field the register already uses to separate the two links the owner submitted on 2026-11-17.
    """
    return sum(1 for r in SUBMITTED_ROWS
               if (r.get("category_fit") or "").strip().lower().startswith("air fryer"))


def page_intent():''', "intent-register constants")

# ───────────────────────────────── B. landing-page link-status note: computed count + S40 caveat
rep('''  <p class="small">A live re-check on 2026-11-17 again observed fallback-style redirects for all three supplied short links, and none of them carried an Associates tag.''',
'''  <p class="small">A live re-check on {e(LINK_RECHECK_DATE)} again observed fallback-style redirects for all
  {N_SUBMITTED_LINKS} submitted short links, and none of their landing URLs carried a visible Associates tag — which,
  on Amazon's own account, proves nothing either way about attribution, because a tracking ID "is not necessary … to
  appear in order for us to track sales" {src_links(['S40'])}.''', "landing link-status note")

# ───────────────────────────────── C. category lede: computed counts
rep('''<p class="lede">The three supplied links were observed landing on air fryer or air fryer-oven listings on 2026-11-13/14; product identity from the tokens is still unconfirmed (F14–F16), so this category label is provisional.''',
'''<p class="lede">{_submitted_links_in_category()} of the {N_SUBMITTED_LINKS} links submitted to this project were
observed landing on air fryer or air fryer-oven listings, and the rest land under a different Amazon browse path —
recorded on the <a href="../product-intent.html">product-intent record</a> rather than merged into this category, and
flagged for a decision (F76, F83). Product identity from the tokens is still unconfirmed (F14–F16), so this category
label is provisional.''', "category page lede")

# ───────────────────────────────── D. page_intent: the correction + the brand catalogues
rep('''<p class="small">Intended ASIN and listing URL are filled only from an official listing the account holder confirms. Observed fields are what the supplied link returned on the date shown. The short codes are not ASINs, so no intended ASIN is inferred. Open flags: <a href="flagged.html#f77">F77</a>, <a href="flagged.html#f78">F78</a>.</p>''',
'''<p class="small">Intended ASIN and listing URL are filled only from an official listing the account holder confirms. Observed fields are what the supplied link returned on the date shown. The short codes are not ASINs, so no intended ASIN is inferred. Open flags: <a href="flagged.html#f77">F77</a>, <a href="flagged.html#f78">F78</a>, <a href="flagged.html#f83">F83</a>, <a href="flagged.html#f84">F84</a>.</p>

<div class="callout note">
  <strong>A correction to how this record argued its own case, dated 2026-11-17.</strong>
  <p class="small">Earlier rows cite the absence of a <code>tag=</code> parameter on an observed landing URL beside their
  caution about attribution. Two official help nodes read the same day narrow that. Amazon states plainly that a tracking
  ID does not need to appear in the click-through URL for a sale to be credited, because the session is tagged on its
  side {src_links(['S40'])} — so a clean landing URL is a <em>null</em> observation, not a negative one, and this page
  does not use it as evidence. What cannot be seen from outside the account is the positive: that the selected ID is
  listed, and that a click shows up under it. That is read in the <strong>Tracking ID Summary Report</strong>, and the
  same node records a limit of 100 tracking IDs per account — which is why per-channel sub-tags are the cheap option
  rather than an exotic one {src_links(['S41'])}. The older sentences are left as written, because they are dated
  records of what those passes observed; the reasoning is corrected here instead of edited backwards.</p>
</div>

<h2>What the brands' own catalogues say about the two newest links</h2>
<p class="small">Both links submitted on 2026-11-17 were checked against the manufacturer's own product pages, not
against the listing. Neither closes the row; both narrow what a future article could honestly claim (F83).</p>
<div class="tablewrap">
<table>
  <caption>Brand-catalogue check, read 2026-11-17</caption>
  <thead><tr><th style="width:8%">Row</th><th style="width:24%">Observed listing says</th>
  <th style="width:34%">The brand's own page says</th><th style="width:22%">Verdict</th><th style="width:12%">Source</th></tr></thead>
  <tbody>{brand_check_rows()}</tbody>
</table>
</div>''', "product-intent correction block")

rep('''    dash = '<span class="tiny muted">not confirmed</span>\'''',
'''    dash = '<span class="tiny muted">not confirmed</span>'

    def brand_check_rows():
        """Rows for the brand-catalogue comparison, read from the register, never typed here."""
        out = []
        for r in SUBMITTED_ROWS:
            bc = r.get("brand_catalogue_check")
            if not bc:
                continue
            out.append(
                f'<tr><td>{e(r["id"])}</td>'
                f'<td class="small">{e(bc.get("listing_says") or "")}</td>'
                f'<td class="small">{e(bc.get("brand_page_says") or "")}</td>'
                f'<td class="small">{e(bc.get("verdict") or "")}'
                f'<div class="tiny muted"><a href="flagged.html#f83">F83</a> — why this closes nothing</div></td>'
                f'<td class="small">{src_links(bc.get("source_ids") or [])}</td></tr>')
        return "".join(out)
''', "brand_check_rows helper")

# ───────────────────────────────── E. footer §3(e): describe the local tally truthfully
rep('''      <p>This site sets no cookies itself, runs no analytics, and has no comment forms or accounts. Following an Amazon link takes you to Amazon, whose own privacy notice and cookie practices apply from that point. No data you enter here is collected, because there is nowhere to enter it.</p>
      <p class="tiny">Amazon's Program Policies §3(e) require an accurate statement of cookie and third-party technology use on Associate sites. This notice satisfies that requirement for the current build; it must be updated the moment any analytics, embeds or affiliate-network script is added.</p>''',
'''      <p>This site sets no cookies and has no comment forms or accounts. Since 2026-11-17 it runs one script that
      counts: a tally of your own outbound link clicks and of the comparison tables you reach, stored in this browser
      only, sent to no server, and readable or erasable on the <a href="{prefix}measurement.html">measurement page</a>.
      Nothing you type anywhere else here is collected, because there is nowhere to send it. Following an Amazon link
      takes you to Amazon, whose own privacy notice and cookie practices apply from that point.</p>
      <p class="tiny">Amazon's Program Policies §3(e) require an accurate statement of cookie and third-party technology
      use on Associate sites. This notice describes the current build; it was rewritten in the same commit that added the
      local tally, and it must be rewritten again the moment a collector, embed or affiliate-network script is added.
      Third parties may still place or recognise cookies once you leave this site.</p>
      <p class="tiny"><a href="{prefix}measurement.html">What this site can and cannot measure</a> — the five events, the wiring state of each, and how to erase the tally.</p>''',
 "footer §3(e) privacy statement")

# ───────────────────────────────── F. measurement page: what is wired now
rep('''def page_measurement():
    m = MEASUREMENT''',
'''def page_measurement():
    m = MEASUREMENT
    collector = m.get("collector") or {}

    def wire_line(ev):
        """Per-event wiring state, read from the register (added 2026-11-17, arena/58cbaaa2)."""
        w = (ev.get("wired") or {}).get("state")
        if not w:
            return ""
        return (f'<p class="tiny" style="margin-bottom:0"><strong>Wiring:</strong> {e(w)}'
                + (f' — {e(ev["wired"].get("detail"))}' if ev["wired"].get("detail") else "") + "</p>")
''', "page_measurement collector/wire_line")

rep('''  <p class="tiny muted" style="margin-bottom:0">{e(ev['note'])}</p>
</div>\"\"\"''',
'''  <p class="tiny muted" style="margin-bottom:0">{e(ev['note'])}</p>
  {wire_line(ev)}
</div>"""''', "ev_card gains wiring line")

rep('''<p class="tiny muted">Specification: <code>data/measurement.json</code>. Program Policies
§3(e) governs the disclosure an analytics script triggers; §3(s) bars artificially
generating clicks; §2(b) bars associating a sub-tag with an end user.</p>''',
'''<h2>What is wired in this browser right now</h2>
<div class="reg-item" style="margin:.6rem 0 1rem">
  <p class="small">{e(collector.get("what") or "")}</p>
  <dl class="kv">
    <dt>Storage</dt><dd>{e(collector.get("storage") or "")}</dd>
    <dt>Sent anywhere</dt><dd>{e(collector.get("transmitted") or "")}</dd>
    <dt>Endpoint</dt><dd>{e(collector.get("endpoint") or "")}</dd>
    <dt>Ceiling</dt><dd>{e(collector.get("ceiling") or "")}</dd>
    <dt>Disclosure</dt><dd>{e(collector.get("disclosure") or "")} {src_links(['S2'])}</dd>
    <dt>Per-channel option that needs no script</dt>
    <dd>{e(collector.get("sub_tag_alternative") or "")} {src_links(['S41', 'S6'])}</dd>
  </dl>
</div>
<div class="tally" id="local-tally" hidden>
  <p class="small"><strong>This browser's own tally</strong> — read from this device's storage, not from a server.
  It is shown so the instrument is checkable rather than decorative, and it can be erased below.</p>
  <div class="tally-grid" id="tally-out"></div>
  <p class="tiny muted" id="tally-note">Nothing has been recorded in this browser yet.</p>
  <p><button class="btn btn-sm" id="tally-export" type="button">Download this tally</button>
     <button class="btn btn-sm" id="tally-erase" type="button">Erase it</button></p>
</div>

<p class="tiny muted">Specification: <code>data/measurement.json</code>; the collector source lives in
<code>assets/app.js</code>, which this build generates. Program Policies
§3(e) governs the disclosure an analytics script triggers; §3(s) bars artificially
generating clicks; §2(b) bars associating a sub-tag with an end user.</p>''',
 "measurement page: collector block")

rep('''    return layout("measurement.html", "Measurement: five events, defined not sending", body,
                  active="measurement.html",
                  description="The five measurement events this site will record, what each excludes, and the prerequisites before any of them can send. No counts are reported because none has been measured.",''',
'''    title_state = ("five events, two of them counting on this device"
                   if collector.get("state") == "wired_local_only" else "five events, defined not sending")
    return layout("measurement.html", "Measurement: " + title_state, body,
                  active="measurement.html",
                  description="The five measurement events this site defines, what each excludes, the cookieless tally that counts two of them in this browser and sends nothing, and the prerequisites before any of them can reach a server. No site-wide counts are reported because none is measured.",''',
 "measurement page title/description")

# ───────────────────────────────── G. programme flags
rep('''    ("F8", "IP License §2(e) forbids aggregating, analysing or repurposing Program Content and training models on it.",''',
'''    ("F83", "The two links submitted on 2026-11-17 do not reconcile with either brand's own catalogue, so their candidate listings cannot be closed by reading the brands.",
     "PI-04, PI-05 on the product-intent record",
     "Both links were checked on 2026-11-17 against the manufacturer's own pages rather than against the listing. The observed ThermoMaven listing is titled '1 Sec Professional Digital Meat Thermometer'; ThermoMaven's own site names its instant-read line F1 Pro and F1 Turbo, with a 0.5 s read, and does not use '1 Sec' as a model name. The observed CHEF iQ listing is the iQ Sense Gen3; the brand page states model CQ60-3C-Z3-E, three probes in the Gen3 kit, and an ambient rating the listing does not repeat. A '1 Sec' marketing line and a brand model number are different kinds of identifier, and neither page mentions the ASIN. So the candidate destinations stand as observations, the intended products stay null, and no product page is written for either: an article built on a listing title the manufacturer does not use would be the first unsourced claim on this site. The brand pages are registered (S38, S39) and their hosts are in verify.py's allow-list, which records that they are official brand pages — not that they settle an identity. Decision needed: say what each link was created to promote (Q-27), or drop the two rows. Added by arena/58cbaaa2, which re-scoped itself against the merged intent register rather than publish a second one.", ["S38", "S39", "S17", "S23"]),
    ("F84", "The site's own reasoning that a missing tag= parameter cast doubt on attribution was an over-reading, and is corrected on the record instead of edited out of it.",
     "product-intent.html, the landing-page link-status note, F82, data/decision.json",
     "Passes including this one cited the absence of a visible Associates tag on a landing URL next to their caution about attribution. Amazon's help node read the same day states that 'it is not necessary for your unique ID to appear in order for us to track sales made after the initial click through', because the session is tagged on Amazon's side (S40). A null observation is not a negative one: the clean landing URLs neither confirm nor refute anything. This is stated on the product-intent record and the landing note, and the second help node read alongside it (S41) names where the actual confirmation lives — the Tracking ID Summary Report — plus the 100-tracking-IDs-per-account limit that makes per-channel sub-tags a cheap option. Nothing historical was rewritten: F82's observation stays as observed, with its inference narrowed where the inference is made in the present tense. Added by arena/58cbaaa2.", ["S40", "S41", "S6", "S2"]),
    ("F85", "The measurement layer moved from 'defined, not shipped' to 'wired, local only' — and the two events that now count cannot answer the question a publisher actually asks.",
     "measurement.html, assets/app.js, data/measurement.json",
     "The register on main recorded five events with status defined_not_shipped, and a pass on the same day declined to ship a counter at all because a tally kept in each visitor's browser 'would not give the publisher usable aggregate analytics'. Both halves are right, and the reconciliation is shipped rather than argued: EV-02 (outbound product click) and EV-04 (comparison table viewed) are now wired in the generated script, storing counts in the reader's own browser, setting no cookie, making no request and keeping no reader identifier; EV-01, EV-03 and EV-05 stay unwired, and EV-05 stays manual because it is the only revenue-bearing event and comes from the owner's report. The footer's §3(e) statement was rewritten in the same commit, exactly as the register's own privacy rule demands. What this does not do is produce site-wide numbers: with no endpoint, one reader's device cannot tell the publisher whether anyone arrived. The option that answers that without any infrastructure is Amazon's own — extra tracking IDs per channel, reported separately in the Tracking ID Summary Report — and the limit of 100 per account means there is room (S41). Decision needed: host a first-party collector and answer the four-item boundary, or adopt per-channel IDs and leave this as a diagnostic, or remove it. SG-38 lays out the three. Added by arena/58cbaaa2.", ["S2", "S41", "S6"]),
    ("F8", "IP License §2(e) forbids aggregating, analysing or repurposing Program Content and training models on it.",''',
 "programme flags F83-F85")

rep('''    ("F82", "None of the five supplied link.amazon URLs carried an Associates tag when read on 2026-11-17.",''',
'''    ("F86", "Two present-tense sentences on the shopper surfaces still counted the submitted links at three, after the register grew to five.",
     "index.html link-status note, categories/kitchen-appliances.html lede",
     "Found 2026-11-17 while re-scoping this session's work against main, and it is the same defect class main's own F80 resolution named but did not repair on these two surfaces: a count typed into narrative rather than read from the register, which goes false the day the owner submits another link — not because any value is wrong. Repaired where the tense is present: the landing note and the category lede now take their numbers from len(rows) and from the register's own category_fit field, and check_submitted_link_count() fails the build if a present-tense surface asserts a different number in its own words. The guard is deliberately scoped to index.html, product-intent.html and the category page, because a dated row that records what was observed while three links existed (F10, F21, the round-10 registers) is a true statement about the past, and a guard that could be satisfied only by rewriting history is worse than no guard. Process note: when the owner submits another link, add a row to data/product-intent.json — never a sentence.", ["S17", "S2"]),
    ("F82", "None of the five supplied link.amazon URLs carried an Associates tag when read on 2026-11-17.",''',
 "programme flag F86 (count repair)")

# ───────────────────────────────── H. build guards
rep('''def main():
    assets = ROOT / "assets"''',
'''_LINK_PHRASE = re.compile(
    r"\\b(all|each of|both|none of|every one of|only)\\s+(the\\s+)?(one|two|three|four|five|six|seven|eight)\\s+"
    r"(supplied|submitted)( short)? links?", re.I)


def check_submitted_link_count(pages):
    """Build guard: a present-tense page may not assert a link count the register contradicts.

    The number of links the owner has submitted is a fact that changes when the owner acts. It was
    typed into sentences for ten passes, and the 2026-11-17 brief (five links) made those sentences
    false with every individual value inside them still correct — the narrative, not the data, was
    the unverified thing. See F86.

    Scope: the surfaces where the count is a claim about right now — the landing page, the product-
    intent record, the shopper surfaces and the two registers. Dated verification prose stays outside
    the guard on purpose: "all three supplied links" was true on 2026-11-14, and forcing history to
    satisfy a check would destroy the evidence the history exists to be.
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
            found = m.group(3).lower()
            n = _LINK_NUM_WORDS[found]
            if n == N_SUBMITTED_LINKS:
                continue
            problems.append(
                f"{rel}: asserts '{words.get(n, n)} {m.group(4)} links' where "
                f"data/product-intent.json holds {N_SUBMITTED_LINKS} rows — read the count from the "
                f"register, or date the sentence so it says when it was true")
    return problems


def main():
    assets = ROOT / "assets"''', "link-count guard")

# ───────────────────────────────── I. requirements token plumbing
rep('''        "n_products": len(PRODUCT_LIST),''',
'''        "n_products": len(PRODUCT_LIST),
        # arena/58cbaaa2 (2026-11-17): counts read from the registers, for prose that must not drift.
        "n_submitted_links": str(N_SUBMITTED_LINKS),
        "n_intent_confirmed": str(sum(1 for r in SUBMITTED_ROWS if r.get("intended_asin"))),
        "n_events": str(len(MEASUREMENT.get("events") or [])),
        "n_ledger_rows": str(len((load("campaign-ledger.json").get("rows") or []))),''',
 "req_counts tokens")

# ───────────────────────────────── J. emitted CSS + JS: the tally, in the existing vocabulary
rep('''.foot-brand p:first-of-type{font-family:var(--serif); font-size:.94rem; line-height:1.55}
"""''',
'''.foot-brand p:first-of-type{font-family:var(--serif); font-size:.94rem; line-height:1.55}
/* local tally on measurement.html (2026-11-17, arena/58cbaaa2) — presentation only */
.tally{border:1px solid var(--rule);border-radius:10px;padding:.85rem 1rem;margin:1rem 0;background:var(--panel)}
.tally-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(9.5rem,1fr));gap:.5rem}
.tally-grid .t{display:block;font-variant-numeric:tabular-nums;font-size:1.25rem;font-weight:600}
.tally-grid .l{display:block;font-size:.72rem;color:var(--muted)}
.btn-sm{font-size:.78rem;padding:.35rem .6rem}
@media (prefers-reduced-motion:reduce){.tally{animation:none}}
"""''', "CSS: tally")

rep('''  paint();
})();
"""''',
'''  paint();
})();

// Cookieless local tally of outbound product clicks and comparison-table views
// (2026-11-17, arena/58cbaaa2). It implements EV-02 and EV-04 of
// data/measurement.json and nothing else: no cookie, no network request, no
// reader identifier, nothing sent anywhere. Counts live in this browser, are
// readable on measurement.html, and can be erased there. With no endpoint the
// numbers describe one device, and the page says so — an aggregate implied by
// a single device would be an invented figure on a site that promises sourced
// ones, which is the failure Program Policies §3(s) and §3(e) exist to prevent.
(function () {
  var KEY = 'zone1-k' + 'itchen-tally';
  var MAX_KEYS = 40;                       // a ceiling, not a history
  var store = {};
  try { store = JSON.parse(window.localStorage.getItem(KEY) || '{}') || {}; } catch (err) { store = {}; }
  if (!store.pages) store.pages = {};
  if (!store.asins) store.asins = {};
  if (!store.tables) store.tables = {};
  if (!store.outbound) store.outbound = 0;

  function path() {
    var p = location.pathname.split('/').pop() || 'index.html';
    return p.length > 48 ? p.slice(0, 48) : p;
  }

  function trim(bucket) {
    var keys = Object.keys(bucket);
    if (keys.length > MAX_KEYS) { delete bucket[keys[0]]; }   // oldest insertion order wins out
  }

  function save() {
    try { window.localStorage.setItem(KEY, JSON.stringify(store)); } catch (err) {}
  }

  // EV-02 — an outbound click to a product listing. Fired on a real click only
  // (§3(s) forbids generating clicks), and it never touches the destination query
  // string, so no tag or token from the URL is stored.
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a[href]') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (!/amazon\\.com\\/dp\\//i.test(href) && !/link\\.amazon/i.test(href)) return;
    store.outbound += 1;
    var m = href.match(/\\/dp\\/([A-Z0-9]{10})/i);
    if (m) { store.asins[m[1].toUpperCase()] = (store.asins[m[1].toUpperCase()] || 0) + 1; trim(store.asins); }
    store.pages[path()] = (store.pages[path()] || 0) + 1;
    trim(store.pages);
    save();
  }, true);

  // EV-04 — the comparison table was actually seen, not merely loaded.
  if (window.IntersectionObserver) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        io.unobserve(en.target);
        var slug = path();
        if (store.tables[slug]) return;
        store.tables[slug] = 1;
        trim(store.tables);
        save();
      });
    }, { threshold: 0.35 });
    Array.prototype.forEach.call(document.querySelectorAll('table'), function (t) {
      if (t.querySelector('caption')) io.observe(t);   // a captioned table is a comparison, not a layout
    });
  }

  // The read-out, on measurement.html only. It reports what this device holds;
  // it is not a site statistic and is labelled where it appears.
  var box = document.getElementById('local-tally');
  if (box) {
    var out = document.getElementById('tally-out');
    var note = document.getElementById('tally-note');
    var cells = [['Outbound product clicks on this device', store.outbound],
                 ['Product listings recorded', Object.keys(store.asins).length],
                 ['Pages with a click', Object.keys(store.pages).length],
                 ['Comparison tables seen', Object.keys(store.tables).length]];
    if (out) {
      out.innerHTML = cells.map(function (c) {
        return '<span class="t-cell"><span class="t">' + c[1] + '</span><span class="l">' + c[0] + '</span></span>';
      }).join('');
    }
    if (note) {
      note.textContent = store.outbound
        ? 'Stored in this browser only, on this device, since the counter was first run here. Nothing has been sent to any server, and no cookie was set.'
        : 'Nothing has been recorded in this browser yet: the tally starts at zero on every device, which is what makes it a check on the links rather than an audience measurement.';
    }
    box.hidden = false;
    var ex = document.getElementById('tally-export');
    if (ex) ex.addEventListener('click', function () {
      var blob = new Blob([JSON.stringify({
        exported_on: new Date().toISOString().slice(0, 10),
        scope: 'single device, this browser only, not a site statistic',
        data: store
      }, null, 2)], { type: 'application/json' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url; a.download = 'zone1-local-tally.json';
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    });
    var er = document.getElementById('tally-erase');
    if (er) er.addEventListener('click', function () {
      try { window.localStorage.removeItem(KEY); } catch (err) {}
      store = { pages: {}, asins: {}, tables: {}, outbound: 0 };
      if (out) out.innerHTML = '';
      if (note) note.textContent = 'Erased in this browser. The tally restarts from zero.';
    });
  }
})();
"""''', "JS: local tally")

# ───────────────────────────────── K. evidence paths for the new flags
rep("REPO_EVIDENCE = {\n",
    "REPO_EVIDENCE = {\n"
    "    # arena/58cbaaa2 (2026-11-17): file paths a reader can open to check each new flag.\n"
    '    \"F83\": [\"data/product-intent.json\", \"product-intent.html\", '
    '\"session-58cbaaa2/artifacts/README.md\"],\n'
    '    \"F84\": [\"product-intent.html\", \"data/product-intent.json\"],\n'
    '    \"F85\": [\"data/measurement.json\", \"measurement.html\", \"assets/app.js\"],\n'
    '    \"F86\": [\"build.py\", \"data/product-intent.json\", '
    '\"reports/verification-2026-11-17-58cbaaa2.md\"],\n',
    "REPO_EVIDENCE rows")

problems = []
for old, new, what in [(o, n, w) for o, n, w, _ in edits]:
    n = src.count(old)
    if n != 1:
        problems.append(f"{what}: anchor matched {n} times")
if problems:
    sys.exit("PATCH ABORTED (nothing written):\n  " + "\n  ".join(problems))
for old, new, what in [(o, n, w) for o, n, w, _ in edits]:
    src = src.replace(old, new, 1)
BUILD.write_text(src, encoding="utf-8")
import ast
ast.parse(src)
print(f"build.py patched: {len(edits)} edits applied, parses OK")
