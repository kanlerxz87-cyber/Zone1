#!/usr/bin/env python3
"""pass-13 build patch (arena/58cbaaa2-zone1, 2026-11-17).

Every edit is an exact-string replacement, so a concurrent session's work cannot be
overwritten by a line-number slip: if an anchor is missing or ambiguous the script stops
before writing anything.
"""
import sys
from pathlib import Path

B = Path("/home/user/Zone1/build.py")
src = B.read_text(encoding="utf-8")
edits = []


def rep(old, new, label):
    edits.append((old, new, label))


# ---------------------------------------------------------------- A. data loads
ANCHOR_A = '''_p12 = ROOT / "session-8874422b" / "pass12.json"
PASS12 = json.loads(_p12.read_text(encoding="utf-8")) if _p12.exists() else None'''
NEW_A = ANCHOR_A + '''
# Additive pass-13 registers (2026-11-17, arena/58cbaaa2-zone1).
#
# `data/product-intent-confirmations.json` was created by arena/02b4e9c7 on the same day:
# one row per link the account holder has submitted, with the intended product and the
# observed redirect destination kept in separate objects on purpose. That pass wrote the
# ledger and its report but, by its own scope ("No canonical data/build/nav edits"),
# nothing rendered it — so the register existed in the repository and nowhere a human
# could read it. This pass adds the reader-facing half and the machine half: the page
# below, and the Special-Link gate that refuses to tag a link the owner has not confirmed.
#
# `data/measurement.json` is the event and ledger contract the same brief asked for
# ("a privacy-preserving outbound-click counter… record the five defined events… an empty
# but well-defined campaign ledger"). Both loads are optional: if a file is removed the
# page renders its "register unavailable" state instead of failing the build, which is the
# same pattern passes 6, 7, 10 and 12 use for their ledgers.
INTENT = load("product-intent-confirmations.json") \\
    if (DATA / "product-intent-confirmations.json").exists() else None
MEASUREMENT = load("measurement.json") if (DATA / "measurement.json").exists() else None'''
rep(ANCHOR_A, NEW_A, "data loads")

# -------------------------------------------------------------------- B. NAV
ANCHOR_B = '''    ("picks.html", "This week's picks", "Three products, three jobs, one decision rule"),'''
NEW_B = ANCHOR_B + '''
    # Added 2026-11-17 (arena/58cbaaa2): the account holder has now submitted five links,
    # not three, and a tracking ID has been selected. Both facts need a published page:
    # one that records what each link is and is not confirmed to point at, one that records
    # what the site can and cannot measure. Neither is reader shopping content, so both sit
    # in the evidence and owner groups rather than in the shop group.
    ("links.html", "Submitted links register", "What each link is, where it lands, what is confirmed"),
    ("measurement.html", "Clicks and conversions", "Five defined events, one empty ledger, no cookies"),'''
rep(ANCHOR_B, NEW_B, "NAV entries")

# ------------------------------------------------------------- C. sidebar groups
ANCHOR_C = '''      {N("data.html")}
      {N("reverification.html")}'''
NEW_C = '''      {N("data.html")}
      {N("links.html")}
      {N("reverification.html")}'''
rep(ANCHOR_C, NEW_C, "sidebar: Trust & evidence group")

ANCHOR_C2 = '''      {N("platform.html")}
      {more_nav}'''
NEW_C2 = '''      {N("platform.html")}
      {N("measurement.html")}
      {more_nav}'''
rep(ANCHOR_C2, NEW_C2, "sidebar: Owner workspace group")

# --------------------------------------------------------------- D. footer text
ANCHOR_D = '''      <p>We may earn a commission from a qualifying purchase made through an eligible link. The three supplied Amazon short links have not been confirmed to match the named models or carry this site's Associates tracking ID. Amazon prices, availability and ratings are not published here.</p>'''
NEW_D = '''      <p>We may earn a commission from a qualifying purchase made through an eligible link. {N_SUBMITTED_LINKS} Amazon short links have been submitted to this project; none of them is confirmed to match the named models, and none is confirmed to carry this site's Associates tracking ID. Amazon prices, availability and ratings are not published here. <a href="{prefix}links.html">Read the submitted-links register →</a></p>'''
rep(ANCHOR_D, NEW_D, "footer disclosure paragraph")

ANCHOR_D2 = '''      <p>This site sets no cookies itself, runs no analytics, and has no comment forms or accounts. Following an Amazon link takes you to Amazon, whose own privacy notice and cookie practices apply from that point. No data you enter here is collected, because there is nowhere to enter it.</p>
      <p class="tiny">Amazon's Program Policies §3(e) require an accurate statement of cookie and third-party technology use on Associate sites. This notice satisfies that requirement for the current build; it must be updated the moment any analytics, embeds or affiliate-network script is added.</p>'''
NEW_D2 = '''      <p>This site sets no cookies and loads no analytics script, and it has no comment forms or accounts. It counts one thing, and it counts it inside your own browser: when you follow a product link, a tally is written to this device's local storage so the measurement page can show you a number that belongs to your visit. Nothing is sent anywhere — the page runs no request to any collector, known or unknown — and the tally can be erased here or by clearing site data in your browser. Following an Amazon link takes you to Amazon, whose own privacy notice and cookie practices apply from that point.</p>
      <p class="tiny">Amazon's Program Policies §3(e) require an accurate statement of cookie and third-party technology use on Associate sites, which is why this paragraph names the local storage the click counter uses. No storage, script or embed was added to this site on or after 2026-11-17 without rewriting this statement; the counter's own page is <a href="{prefix}measurement.html">Clicks and conversions</a>.</p>
      <p class="tiny"><button type="button" class="btn btn-ghost counter-clear" data-clear="1">Erase the counts stored on this device</button></p>'''
rep(ANCHOR_D2, NEW_D2, "footer cookies & privacy paragraph")

# ------------------------------------------------------------------ E. hero note
ANCHOR_E = '''  <p class="small">A targeted live re-check on 2026-11-16 again observed fallback-style redirects for all three supplied short links. We cannot confirm that any link reaches the product the account holder intended, carries the correct Associates tag, or that the Associates account is approved. Verify the model and account status in Amazon before relying on a purchase link. {src_links(['S17', 'S2'])} <a href="reverification.html">Read the redirect evidence</a> · <a href="flagged.html">Flagged for review</a> · <a href="questions.html#q-01">Product-link question</a> · <a href="questions.html#q-03">Account-status question</a>.</p>'''
NEW_E = '''  <p class="small">A live re-check on {LINK_CHECK_DATE} again observed fallback-style redirects for every one of the {N_SUBMITTED_LINKS} submitted short links, and the register now holds {N_SUBMITTED_LINKS} links where this site publishes {len(PRODUCT_LIST)} products. We cannot confirm that any link reaches the product the account holder intended, carries the tracking ID selected on 2026-11-17, or that the Associates account is approved. Verify the model and account status in Amazon before relying on a purchase link. {src_links(['S17', 'S38', 'S6', 'S2'])} <a href="links.html">Submitted-links register</a> · <a href="flagged.html">Flagged for review</a> · <a href="questions.html#q-01">Product-link question</a> · <a href="questions.html#q-28">Tracking-ID question</a>.</p>'''
rep(ANCHOR_E, NEW_E, "landing link-status note")

# --------------------------------------------------------------- F. product CTA
ANCHOR_F = '''<p class="cta-note">Affiliate disclosure: we may earn a commission if Amazon credits a qualifying purchase to this site, but this short link's Associates tag has not been verified. The model identity is also unconfirmed; check the product title and model number on Amazon before buying. See <a href="{prefix}flagged.html">Flagged for review</a> and <a href="{prefix}questions.html#q-01">the open questions</a>. {src_links(['S17', 'S2'])}</p>'''
NEW_F = '''<p class="cta-note">Affiliate disclosure: we may earn a commission if Amazon credits a qualifying purchase to this site, but this short link's Associates tag has not been verified. The account holder selected a tracking ID on {TRACKING_SELECTED_DATE}; it is recorded on the register and has not been confirmed inside this link, so the link ships untagged rather than tagged with something unverified. The model identity is also unconfirmed; check the product title and model number on Amazon before buying. See <a href="{prefix}links.html">the submitted-links register</a>, <a href="{prefix}flagged.html">Flagged for review</a> and <a href="{prefix}questions.html#q-01">the open questions</a>. {src_links(['S17', 'S6', 'S2'])}</p>'''
rep(ANCHOR_F, NEW_F, "product CTA note")

# ------------------------------------------------- F2. CTA / article-nav hooks for EV-02, EV-04
ANCHOR_F2 = '''<div class="cta-row">'''
NEW_F2 = '''<div class="cta-row" data-product="{e(p['slug'])}">'''
rep(ANCHOR_F2, NEW_F2, "cta-row product hook")

ANCHOR_F3 = '''<div class="article-nav">'''
NEW_F3 = '''<div class="article-nav" data-article="{e(a['slug'])}">'''
rep(ANCHOR_F3, NEW_F3, "article-nav article hook")

# ------------------------------------------------------------- G. compare bar (S-20)
ANCHOR_G0 = '''<p class="small" style="margin-top:1.5rem"><a href="../guides/buying-guide-air-fryers.html">Read the buying guide →</a> · <a href="../flagged.html">See what is unresolved →</a></p>
"""'''
NEW_G0 = '''<nav class="comparebar" aria-label="Keep the comparison within reach">
  <span><strong>Still deciding?</strong> The guide answers the format question first.</span>
  <a class="btn" href="../guides/buying-guide-air-fryers.html">Buying guide</a>
  <a class="btn btn-ghost" href="../flagged.html">What is unresolved</a>
</nav>

<p class="small" style="margin-top:1.5rem"><a href="../guides/buying-guide-air-fryers.html">Read the buying guide →</a> · <a href="../flagged.html">See what is unresolved →</a></p>
"""'''
rep(ANCHOR_G0, NEW_G0, "compare page sticky bar")

# ---------------------------------------------------------------- H. CSS block
ANCHOR_G = '''.foot-brand p:first-of-type{font-family:var(--serif); font-size:.94rem; line-height:1.55}
"""'''
NEW_G = '''.foot-brand p:first-of-type{font-family:var(--serif); font-size:.94rem; line-height:1.55}

/* ===== additive: arena/58cbaaa2-zone1 (2026-11-17) — the submitted-links register and the
   measurement page, plus the mobile items the requirements register still lists as open
   (S-20: tap targets, a type floor for small screens, a sticky comparison bar).
   Presentation only: every rule reuses this stylesheet's own variables, and no rule changes
   the size or wording of a published value. */
.reg-grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:.75rem; margin:.9rem 0 1.2rem}
.reg-item{border:1px solid var(--line); border-radius:14px; background:var(--panel); padding:.8rem .9rem}
.reg-item h4{margin:0 0 .35rem; font-size:.95rem}
.reg-item .kv{display:grid; grid-template-columns:auto 1fr; gap:.15rem .6rem; font-size:.86rem}
.reg-item .kv dt{color:var(--muted)}
.reg-item .kv dd{margin:0}
code.link-token{font-size:.86rem; background:#f4f1e6; padding:.1rem .35rem; border-radius:6px; word-break:break-all}
.blankcell{color:var(--muted); font-style:italic}
.ledger-empty{border:1px dashed var(--line); border-radius:14px; padding:.85rem 1rem; background:#fffdf7; color:var(--muted); font-size:.9rem}
.device-panel{border:1px solid var(--line); border-radius:14px; padding:.9rem 1rem; background:var(--panel); margin:.9rem 0 1.2rem}
.device-panel textarea{width:100%; font-family:monospace; font-size:.78rem; margin-top:.5rem}
.counter-row{display:flex; flex-wrap:wrap; gap:.5rem 1.1rem; align-items:baseline; font-size:.9rem; margin:.3rem 0}
.counter-row b{font-family:var(--serif); font-size:1.15rem}
.gate{display:flex; flex-wrap:wrap; gap:.4rem .8rem; align-items:center; border:1px solid var(--line);
  border-left:4px solid var(--warn); border-radius:12px; padding:.6rem .8rem; background:#fffdf7; margin:.7rem 0 1rem}
.gate.open{border-left-color:var(--ok)}
.comparebar{position:sticky; bottom:.5rem; z-index:15; display:none; gap:.6rem; align-items:center;
  margin:1.1rem 0 0; padding:.55rem .7rem; border:1px solid var(--line); border-radius:14px;
  background:var(--panel); box-shadow:0 -2px 12px rgba(20,18,12,.09); font-size:.86rem}
.comparebar span{flex:1 1 auto; min-width:0}
@media (max-width:900px){
  .comparebar{display:flex}
  .comparebar .btn{min-height:40px; flex:0 0 auto; padding:.4rem .8rem}
}
/* S-20 mobile-first pass: tap targets on the controls a shopper actually taps, and a type
   floor so a table never becomes the reason a page needs pinching. */
@media (max-width:760px){
  .cta-row .btn, .hero-actions .btn, .counter-clear, .decision-actions button, .comparebar .btn{
    min-height:44px; display:inline-flex; align-items:center; justify-content:center; padding:.55rem 1rem}
  .topnav a{padding:.45rem .55rem; min-height:40px; display:inline-flex; align-items:center}
  .reg-grid{grid-template-columns:1fr}
}
@media (max-width:560px){
  h1{font-size:clamp(1.6rem,7.2vw,2.1rem)}
  h2{font-size:clamp(1.26rem,5.6vw,1.55rem)}
  .card, .reg-item{padding:.85rem}
  .tablewrap{font-size:.84rem}
}
@media print{.comparebar,.device-panel,.counter-clear{display:none}}
"""'''
rep(ANCHOR_G, NEW_G, "CSS additive block")

# ------------------------------------------------------------------- I. JS block
ANCHOR_H = """  paint();
})();
\"\"\""""
NEW_H = """  paint();
})();

/* ===== additive (2026-11-17, arena/58cbaaa2-zone1): the outbound-click counter the brief
   asked for, in the only form a static site can honestly ship.
   What it does: counts, in this browser's localStorage, how many times a product link was
                  followed from this site and which page it was followed from.
   What it never does: sets a cookie, sends a request, names a reader, stores a full
                  destination query string, or touches anything Amazon serves as Program
                  Content. There is nowhere to send it: data/measurement.json carries
                  endpoint null, and GitHub Pages runs no server code.
   That is the whole design. A counter with no endpoint is not analytics — the page that
   shows these numbers says so in its first line — and pretending otherwise is how an
   affiliate site ends up publishing a chart nobody can source. The footer's section 3(e)
   statement describes this storage, and check_measurement_claims() fails the build if any
   page still claims the site counts nothing.
   Progressive: with JavaScript off nothing is counted and every link works unchanged. */
(function () {
  var KEY = '***';
  var AFFILIATE_HOSTS = ['link.amazon', 'amazon.com', 'www.amazon.com'];
  var MAX_KEYS = 40;
  var store = {clicks: {}, pages: {}, impressions: {}, ends: {}, total: 0};
  try {
    var loaded = JSON.parse(window.localStorage.getItem(KEY) || 'null');
    if (loaded && typeof loaded === 'object') store = Object.assign(store, loaded);
  } catch (err) {}

  function save() {
    try { window.localStorage.setItem(KEY, JSON.stringify(store)); } catch (err) {}
  }
  function bump(group, key) {
    if (!store[group]) store[group] = {};
    store[group][key] = (store[group][key] || 0) + 1;
    var keys = Object.keys(store[group]);
    if (keys.length > MAX_KEYS) delete store[group][keys[0]];   // a ceiling, not a history
    save();
  }

  // EV-01 outbound_click — the one number this site can count without anyone's account.
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a[href]') : null;
    if (!a) return;
    var url;
    try { url = new URL(a.href, location.href); } catch (err) { return; }
    if (AFFILIATE_HOSTS.indexOf(url.hostname) < 0) return;
    if (a.classList.contains('src')) return;                     // a citation, not a call to action
    var dest = 'other';
    var m = url.pathname.match(/(?:link\\.amazon\\/|\\/dp\\/)([A-Za-z0-9]{6,20})/);
    if (m) dest = m[1];
    bump('clicks', dest);
    store.total = (store.total || 0) + 1;
    save();
  });

  // EV-03 page_arrival — path only. The referrer is never read, so no typed query can be stored.
  bump('pages', location.pathname);

  // EV-02 cta_impression / EV-04 guide_reached_end — one flag per element, no timing series.
  function observe(selector, group, attr) {
    var nodes = document.querySelectorAll(selector);
    if (!nodes.length || !window.IntersectionObserver) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        if (el.getAttribute('data-counted')) return;
        el.setAttribute('data-counted', '1');
        bump(group, el.getAttribute(attr) || location.pathname);
        io.unobserve(el);
      });
    }, {threshold: 0.55});
    Array.prototype.forEach.call(nodes, function (n) { io.observe(n); });
  }
  observe('.cta-row', 'impressions', 'data-product');
  observe('.article-nav', 'ends', 'data-article');

  // The device panel on the measurement page, and the erase control in the footer.
  function render() {
    var panel = document.getElementById('device-panel');
    if (!panel) return;
    var rows = [
      ['product link' + ((store.total || 0) === 1 ? '' : 's') + ' followed from this device', store.total || 0],
      ['page' + (Object.keys(store.pages || {}).length === 1 ? '' : 's') + ' opened here', Object.keys(store.pages || {}).length],
      ['product card' + (Object.keys(store.impressions || {}).length === 1 ? '' : 's') + ' seen', Object.keys(store.impressions || {}).length],
      ['guide' + (Object.keys(store.ends || {}).length === 1 ? '' : 's') + ' read to the end', Object.keys(store.ends || {}).length]
    ];
    var html = '';
    rows.forEach(function (r) {
      html += '<div class="counter-row"><b>' + r[1] + '</b><span>' + r[0] + '</span></div>';
    });
    var links = Object.keys(store.clicks || {});
    if (links.length) {
      html += '<p class="tiny muted">Per submitted link:</p><ul class="tight small">';
      links.forEach(function (k) {
        var safe = String(k).replace(/[^A-Za-z0-9_-]/g, '');
        html += '<li><code class="link-token">' + safe + '</code> — ' + store.clicks[k] + '</li>';
      });
      html += '</ul>';
    } else {
      html += '<p class="tiny muted">No product link has been followed in this browser yet, so there is ' +
              'nothing to show. That is a true zero, not a missing value.</p>';
    }
    panel.innerHTML = html;
  }
  render();

  document.addEventListener('click', function (ev) {
    var b = ev.target && ev.target.closest ? ev.target.closest('[data-clear],[data-export]') : null;
    if (!b) return;
    if (b.hasAttribute('data-export')) {
      var box = document.getElementById('export-box');
      if (box) {
        box.value = JSON.stringify(store, null, 2);
        box.hidden = false;
        b.textContent = 'Written below — copy it into the owner ticket, never into the ledger';
      }
      return;
    }
    try { window.localStorage.removeItem(KEY); } catch (err) {}
    store = {clicks: {}, pages: {}, impressions: {}, ends: {}, total: 0};
    render();
    b.textContent = 'Erased on this device';
  });
})();
\"\"\""""
rep(ANCHOR_H, NEW_H, "JS click counter")

# -------------------------------------------------------------- J. flags + evidence
ANCHOR_I = '''    ("F75", "The 404 page was published with relative links, but GitHub Pages serves it at any missing path — so every link on it broke under nested URLs.",'''
NEW_I = '''    ("F76", "The two links submitted on 2026-11-17 resolve to cooking thermometers, not air fryers: the submitted product set spans two categories while the site publishes one.",
     "PI-04 (B0c8moW59) and PI-05 (B0f3GKalj)",
     "Found by this pass while re-resolving all five submitted links on 2026-11-17 (observation_2026_11_17 on each record in data/product-intent-confirmations.json). The candidate destinations are a ThermoMaven instant-read thermometer and a CHEF iQ Sense Gen3 wireless thermometer, each filed by Amazon under Kitchen Utensils & Gadgets > Thermometers & Timers > Meat, whereas the first three links land under Small Appliances > Fryers > Air Fryers. Two consequences, and this pass acted on neither. (1) Scope: every product page, comparison row, buying guide and article on this site is about air fryers, and the masthead reads 'Air-fryer field guide'. Adding two thermometer pages is a publishing decision (SG-36), not a data-entry task — it changes what the site is, and a second category built from two unconfirmed candidate destinations is how one thin affiliate footprint becomes two. (2) Money: the commission-category question was argued from the Air Fryers breadcrumb (Q-11, SG-10), and a thermometer listing sits in a different browse path, so the Kitchen 4.50% working rate cannot be extended to it by analogy. What this pass did instead: recorded both links with their observation fields filled and their confirmation fields blank, cross-read the two brands' own pages so the owner has something to compare intent against, and generated links.html so the divergence is on a page rather than buried in JSON. Decision needed: confirm which product each of the five links was made for, then choose path A (air fryers only, the thermometers stay in the register) or path B (a second category, sourced from brand documents before any page is written).",
     ["S36", "S37", "S38", "S23"]),
    ("F77", "Neither newly submitted link's candidate product can be resolved to a manufacturer model number from the brand's own catalogue.",
     "PI-04 (ThermoMaven), PI-05 (CHEF iQ Sense)",
     "Recorded 2026-11-17 while checking whether the observed destinations could be promoted to product pages the way the three air fryers were. For the air fryers the mapping was closable: each listing's own Product information block states RJ38-SQPF-3TDB-2W and RJ38-SQSS-8T, which are the brand documents' strings (F68). For PI-04 no such match exists: the observed listing title reads '1 Sec Professional' while the brand's official site names its instant-read models F1 Pro and F1 Turbo and describes the F1 Turbo with a half-second read (S37), so the brand page neither confirms nor denies which model the listing is. PI-05 is closer — the brand's iQ Sense page states model CQ60-3C-Z3-E, five sensors and a 1,000 °F ambient rating, consistent with the 'Gen3' in the observed title (S36) — but 'consistent with' is an inference about a listing reached through a fallback redirect, and this project does not publish inferences about the destination it is paid on. No spec row, comparison cell or article was created from either candidate. Decision needed: the account holder states which product each link was created to point at; only then does the F68 route (read the listing's model line) become meaningful.",
     ["S36", "S37", "S16"]),
    ("F78", "The tracking ID selected by the account holder matches the shape Amazon documents, and cannot be confirmed to exist on the account — so no published link carries it.",
     "shopnow047c-20 — all five submitted links",
     "The 2026-11-17 brief supplied 'Selected Tracking ID: shopnow047c-20', which answers half of Q-04 (which ID is intended) and none of the other half (whether it exists, and whether it is attached to the links). Checked against the only official page that describes what a tracking ID is, read verbatim today (S6): the help node's worked example is 'storeid-20', with sub-tag IDs of the form 'storeid-1-20'; the supplied value matches that shape. The node states no validation rule and publishes no list of IDs per account, so a shape match is not an existence check — and existence is the only thing that earns. The build therefore keeps every outbound link exactly as supplied: a tag that does not exist on the account cannot attribute a sale, and a destination rewritten by the publisher would be worse than an ambiguous one, because it would look settled. The gate is now data rather than convention — selected_tracking_id.tagging_gate.state in data/product-intent-confirmations.json — enforced by check_special_link_gate(), which fails the build if a tagged anchor appears while the gate is closed, or if the gate is opened without a confirmation date and source. Decision needed: five minutes at Associates Central > Manage your Tracking ID, then either open the gate or write back that the ID is not listed.",
     ["S6", "S2"]),
    ("F79", "The shipped click counter counts one device, not an audience: with no collector deployed its numbers cannot be aggregated, and the campaign ledger stays empty by design.",
     "measurement.html, data/measurement.json, assets/app.js",
     "The 2026-11-17 brief asks for a privacy-preserving outbound-click counter, a self-hosted analytics endpoint, five defined events, and an empty but well-defined campaign ledger — and it puts that ahead of writing anything else. The pass that ran the same day read the same instruction and declined to ship a counter at all, on the ground that a browser counter storing counts on each visitor's device 'would not give the publisher usable aggregate analytics' and that inventing an endpoint would be misleading (arena/02b4e9c7's completion record). Both readings are partly right, and the reconciliation is published rather than hidden. What shipped: the five events defined in a machine-readable register; a collector that stores counts in the reader's own browser and sends nothing; and a ledger whose eight columns each carry the rule for what may fill them. What did not ship and cannot: the endpoint — GitHub Pages serves static files, there is no server here to accept a POST, and a collector URL written into code with nobody to run it is a promise, not a feature. So the counter is a per-device diagnostic and is labelled that way on every surface that shows a number: the instrument, wired, waiting for the day an endpoint exists. The option that needs no infrastructure at all is Amazon's own — extra tracking IDs per channel, which report clicks and orders separately with no script on this site (the sub-tag plan on the measurement page, sourced to S6). Decision needed: deploy a first-party collector and rewrite the privacy statement to match it; or adopt sub-tags and leave the counter as a diagnostic; or remove the counter. All three are one edit, and SG-38 lays them out.",
     ["S2", "S6"]),
    ("F80", "Ten passes typed 'the three supplied links' into present-tense prose, and the sentence went false the day a fourth and fifth link arrived.",
     "build.py (footer, landing note), data/decision.json, EXECUTIVE_SUMMARY.md",
     "Found 2026-11-17 in the line-by-line review, minutes after the brief itself demonstrated the defect by supplying two more links. The number of submitted links is a fact that changes when the owner acts, and it had been typed into sentences in several files rather than read from the register — so the footer and the landing page both still described a submission of three while the brief described five. Same defect class as F73 (counts typed into prose) and F14 (a headline that outlived its premise), one step up: those passes were checking numbers against data; nobody was checking the *narrative* against data, and every number inside each of those sentences was individually fine. Repaired where the sentence is present tense: the footer, the landing-page link-status note and the new register page take their counts from len(records) in data/product-intent-confirmations.json, and check_submitted_link_count() fails the build if a generated page asserts a different number in its own words. Not repaired, deliberately: the dated rows that record what an earlier pass observed while three links existed (F14, F21, F28, F32 and the historical prose in data/decision.json) are statements about a past state, and rewriting them would destroy the audit trail that makes them evidence. Process note for the next session: when the owner submits another link, add the record — never the prose.",
     []),
    ("F75", "The 404 page was published with relative links, but GitHub Pages serves it at any missing path — so every link on it broke under nested URLs.",'''
rep(ANCHOR_I, NEW_I, "programme flags F76-F80")

ANCHOR_I2 = '''REPO_EVIDENCE = {
    "F74": ["build.py", "data/articles.json", "data/topics.json",'''
NEW_I2 = '''REPO_EVIDENCE = {
    "F76": ["data/product-intent-confirmations.json", "links.html",
            "reports/verification-2026-11-17-58cbaaa2.md"],
    "F77": ["data/product-intent-confirmations.json", "links.html"],
    "F78": ["data/product-intent-confirmations.json", "links.html", "build.py"],
    "F79": ["data/measurement.json", "measurement.html", "assets/app.js"],
    "F80": ["build.py", "data/product-intent-confirmations.json"],
    "F74": ["build.py", "data/articles.json", "data/topics.json",'''
rep(ANCHOR_I2, NEW_I2, "REPO_EVIDENCE rows")

# F11 is the site's own cookie-disclosure row and its action text still describes the build as
# of 2026-11-13. The appended sentence is the honest update; the original wording is kept.
ANCHOR_F11 = '''     "Whole site", "The site itself sets no cookies and runs no analytics, but §3(e) requires an accurate disclosure of cookie and third-party technology use, including that third parties may place or recognise cookies. Only a minimal notice is in the footer; a proper privacy/cookie statement is needed before launch. Legal review recommended.", ["S2"]),'''
NEW_F11 = '''     "Whole site", "The site itself sets no cookies and runs no analytics, but §3(e) requires an accurate disclosure of cookie and third-party technology use, including that third parties may place or recognise cookies. Only a minimal notice is in the footer; a proper privacy/cookie statement is needed before launch. Legal review recommended. UPDATED 2026-11-17 (arena/58cbaaa2): the row's 2026-11-13 premise — nothing is stored — is no longer the whole truth, so the footer statement was rewritten to say exactly what happens instead of left to rot: no cookie, no script, no network call, and one tally in the reader's own localStorage written when a product link is followed, with an erase control in the same paragraph. The §3(e) obligation is now met by a statement that describes the technology rather than denying it exists; what remains open is the half this repository cannot close — whether the endpoint decision (F79) adds a third party, and whether a lawyer reads the sentence before a domain points here.", ["S2"]),'''
rep(ANCHOR_F11, NEW_F11, "F11 dated update")

# ------------------------------------------------------------ K. pages + guards
ANCHOR_J = '''def main():
    assets = ROOT / "assets"'''
NEW_J = '''# --------------------------------------------------------------------------- #
# pass 13 (arena/58cbaaa2-zone1, 2026-11-17): the submitted-links register, the
# measurement contract, and the Special-Link gate.
# --------------------------------------------------------------------------- #

def _intent_records():
    return list((INTENT or {}).get("records") or [])


SUBMITTED_LINKS = _intent_records()
N_SUBMITTED_LINKS = len(SUBMITTED_LINKS)
_LINK_NUM_WORDS = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
                   6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
TRACKING_ID = ((INTENT or {}).get("selected_tracking_id") or {})
TAGGING_GATE = TRACKING_ID.get("tagging_gate") or {}
GATE_OPEN = (TAGGING_GATE.get("state") == "open")
LINK_CHECK_DATE = ((INTENT or {}).get("observations_2026_11_17") or {}).get("observed_on") or "2026-11-17"
N_SUBMITTED_LINKS_WORD = _LINK_NUM_WORDS.get(N_SUBMITTED_LINKS, str(N_SUBMITTED_LINKS))
TRACKING_SELECTED_DATE = (INTENT or {}).get("prepared_on") or "2026-11-17"
BLANK_CELL = '<span class="blankcell">blank — not confirmed</span>'


def _confirmed_link(rec):
    """The canonical Special Link a confirmed record is allowed to earn — or None.

    Rendered as escaped code text on links.html while the gate is closed, so the owner can
    see exactly what to build without the site publishing a commercial destination assembled
    from an unconfirmed ASIN and an unconfirmed tag. If the gate opens, this becomes the CTA.
    """
    if not GATE_OPEN:
        return None
    intended = rec.get("intended_product") or {}
    asin = (intended.get("asin") or "").strip()
    tag = (TRACKING_ID.get("value") or "").strip()
    if not asin or not tag:
        return None
    return f"https://www.amazon.com/dp/{asin}?tag={tag}"


def special_link(rec):
    """Outbound href for a submitted link: the supplied short link, or the confirmed tagged
    /dp/ URL once both halves of the record are confirmed."""
    return _confirmed_link(rec) or rec.get("submitted_link")


def check_special_link_gate():
    """Build guard: the gate is the only thing between a supplied short link and a tagged
    canonical link, so it has to be enforced by the build rather than by memory.

    Written 2026-11-17 (arena/58cbaaa2) on the day the account holder selected a tracking ID.
    Two failure modes, both cheap to make and expensive to ship:

      1. a `?tag=` is added to a template while the register still says the gate is closed.
         The site would then publish a link carrying an ID never confirmed to exist, which is
         worse than an untagged link: it looks settled and attributes nothing.
      2. the gate is opened without evidence. `state: open` asserts that somebody read the ID
         in Associates Central, so it must carry a date and a source field, or it is a wish.

    While the gate is closed the guard also asserts the positive: every supplied link string
    still appears verbatim on a generated page, so the register and the site cannot drift.
    """
    problems = []
    if INTENT is None:
        return problems
    for r in SUBMITTED_LINKS:
        if r.get("submitted_link") and r["submitted_link"] not in "".join(PAGES_CACHE.values()):
            problems.append(
                f'{r["record_id"]}: the supplied link string appears on no generated page, so the '
                'register and the site have diverged')
    tagged = []
    for rel, html_text in PAGES_CACHE.items():
        for m in re.finditer(r'<a\\b[^>]*href="([^"]*tag=[^"]*)"[^>]*>', html_text, re.I):
            if "class=\\"src\\"" in m.group(0):
                continue
            tagged.append((rel, m.group(1)))
    if not GATE_OPEN:
        for rel, href in tagged:
            problems.append(
                f'{rel}: publishes a tagged Amazon link ({href[:90]}) while '
                'selected_tracking_id.tagging_gate.state is "closed" in data/product-intent-confirmations.json')
        return problems
    if not str(TRACKING_ID.get("associates_central_confirmation_date") or "").strip():
        problems.append("the tagging gate is open but associates_central_confirmation_date is blank")
    if not str(TRACKING_ID.get("source") or "").strip():
        problems.append("the tagging gate is open but the confirmation source field is blank")
    for r in SUBMITTED_LINKS:
        intended = r.get("intended_product") or {}
        want = _confirmed_link(r)
        if intended.get("status", "").lower() == "confirmed" and not want:
            problems.append(
                f'{r["record_id"]}: intent confirmed and the gate is open, but no tagged link could '
                'be built — check intended_product.asin and selected_tracking_id.value')
        if want:
            for rel, html_text in PAGES_CACHE.items():
                if f'href="{r["submitted_link"]}"' in html_text and rel.startswith("products/"):
                    problems.append(
                        f'{rel}: still links a confirmed record with the raw short link while the gate is open')
    return problems


def check_submitted_link_count():
    """Build guard: no generated page may state a submitted-link count that the register
    disagrees with (flag F80).

    'The three supplied short links' sat in several files until the owner submitted a fourth and
    a fifth, and no gate could see it because every number inside those sentences was correct —
    the count in the sentence's own wording was the fact that had expired. This compares the
    number a page writes in front of 'supplied/submitted short link(s)' with len(records).
    """
    problems = []
    if INTENT is None:
        return problems
    # Scope: the pages where a link count is a claim about right now — the shopper surfaces
    # plus the two registers this pass built. A dated verification row that says "all three
    # supplied links" is a true statement about 2026-11-14, and editing history to satisfy a
    # check would destroy the evidence, so dated registers stay outside this guard on purpose.
    PRESENT_TENSE_PAGES = {"index.html", "links.html", "measurement.html", "compare.html",
                           "picks.html", "compliance.html", "categories", "products", "guides"}
    words = {v: k for k, v in _LINK_NUM_WORDS.items() if k}
    pat = re.compile(r"\\b(one|two|three|four|five|six|seven|eight|nine|ten|\\d{1,2})\\s+"
                     r"(?:(?:Amazon|newly|previously|originally)\\s+)?(?:supplied|submitted)\\s+"
                     r"(?:Amazon\\s+)?(?:short\\s+links?|links?)\\b", re.I)
    for rel, html_text in PAGES_CACHE.items():
        if rel.split("/")[0] not in PRESENT_TENSE_PAGES:
            continue
        plain = re.sub(r"<[^>]+>", " ", html_text)
        for m in pat.finditer(plain):
            raw = m.group(1).lower()
            n = words.get(raw, int(raw) if raw.isdigit() else -1)
            if n != N_SUBMITTED_LINKS:
                problems.append(
                    f"{rel}: the page says '{m.group(0).strip()}' while "
                    f"data/product-intent-confirmations.json holds {N_SUBMITTED_LINKS} records")
    return problems


def check_measurement_claims():
    """Build guard: the privacy statement, the shipped collector and the ledger must describe
    the same site.

    Three assertions, checked against the data rather than against prose:
      * the footer's Program Policies section 3(e) sentence must still say what the collector
        does — the old wording denied that anything was counted, which the shipped script makes
        false, and a stale §3(e) statement is a policy defect, not a style one;
      * the endpoint state rendered on the measurement page must match data/measurement.json,
        so no future pass can light up a dashboard by editing a sentence;
      * the ledger may only carry rows with a report date and a named first-party source, and
        a column that says a figure came from a browser counter is rejected outright.
    """
    problems = []
    if MEASUREMENT is None:
        return problems
    stale_footer = "sets no cookies itself, runs no analytics"
    for rel, html_text in PAGES_CACHE.items():
        if stale_footer in html_text:
            problems.append(
                f"{rel}: still publishes the pre-2026-11-17 privacy sentence ({stale_footer!r}), "
                "which the shipped click counter makes false")
    meas = PAGES_CACHE.get("measurement.html", "")
    endpoint_on = bool(MEASUREMENT["posture"].get("endpoint"))
    if endpoint_on and ">on<" not in meas:
        problems.append("data/measurement.json declares an endpoint but measurement.html does not render it as on")
    if not endpoint_on and ">off<" not in meas:
        problems.append("data/measurement.json declares no endpoint but measurement.html does not render it as off")
    led = MEASUREMENT["ledger"]
    rows = led.get("rows") or []
    has_table = "<caption>Rows</caption>" in meas
    if rows and not has_table:
        problems.append("the campaign ledger has rows in data but measurement.html renders no rows table")
    if not rows and has_table:
        problems.append("the campaign ledger is empty in data but measurement.html renders a rows table")
    for i, row in enumerate(rows, 1):
        for key in ("as_of", "source"):
            if not str(row.get(key) or "").strip():
                problems.append(
                    f"campaign ledger row {i} has no {key}; a row is only valid with a report date "
                    "and a named first-party source")
        for key in ("clicks", "orders_reported"):
            if str(row.get(key) or "").strip().lower() in ("local", "device", "browser", "counter"):
                problems.append(
                    f"campaign ledger row {i} records {key} from a browser counter; only an "
                    "authorized first-party report may fill that column")
    return problems


def page_links():
    \"\"\"The product-intent register, rendered for a human to read and to act on.\"\"\"
    if not INTENT:
        return layout("links.html", "Submitted links register",
                      '<h1>Submitted links register</h1><p class="lede">The register file '
                      '<code>data/product-intent-confirmations.json</code> is not present, so there is '
                      'nothing to render. Nothing is inferred in its absence.</p>',
                      active="links.html",
                      description="The submitted-link register is not available in this build.")
    recs = SUBMITTED_LINKS
    tok = TRACKING_ID.get("value") or ""
    gate = TAGGING_GATE
    obs = INTENT.get("observations_2026_11_17") or {}
    rule = INTENT.get("submitted_token_rule") or {}
    n_conf = sum(1 for r in recs
                 if (r.get("intended_product") or {}).get("status", "").lower() == "confirmed")
    n_obs = sum(1 for r in recs if (r.get("observed_redirect_target") or {}).get("url"))

    def cell_link(url, label=None, rel="noopener"):
        if not url:
            return BLANK_CELL
        return f'<a href="{e(url)}" target="_blank" rel="{rel}">{e(label or url)}</a>'

    def rows():
        out = []
        for r in recs:
            ip = r.get("intended_product") or {}
            ob = r.get("observed_redirect_target") or {}
            st = r.get("submitted_token") or {}
            cand = ob.get("url") or ""
            cand_asin = cand.rsplit("/", 1)[-1] if cand else ""
            intended_asin = str(ip.get("asin") or "").strip()
            cells = [
                f'<td class="small"><a href="{e(r["submitted_link"])}" target="_blank" '
                f'rel="nofollow sponsored noopener">{e(r["submitted_link"])}</a>'
                f'<div class="tiny muted">Submitted as supplied; the site does not normalise or reinterpret it.</div></td>',
                f'<td class="small"><code class="link-token">{e(st.get("as_supplied") or "")}</code>'
                f'<div class="tiny muted">{st.get("characters", "?")} characters, so it '
                f'{"matches" if st.get("matches_amazon_asin_length") else "does not match"} the '
                f'10-character ASIN length Amazon defines {src_link("S23")}</div></td>',
                f'<td class="small">{e(intended_asin) if intended_asin else BLANK_CELL}'
                f'<div class="tiny muted">official listing: '
                f'{e(str(ip.get("official_listing_url") or "")) or BLANK_CELL}<br>'
                f'confirmed: {e(str(ip.get("confirmed_on") or "")) or BLANK_CELL} · '
                f'source: {e(str(ip.get("confirmation_source") or "")) or BLANK_CELL}</div></td>',
                f'<td class="small">{cell_link(cand, cand_asin) if cand else BLANK_CELL}'
                f'<div class="tiny muted">observed {e(ob.get("observed_on") or "—")}</div></td>',
                f'<td>{_intent_pill(ip)}<div class="tiny muted">{e(ob.get("observation_status") or "no observation recorded")}</div>'
                f'{flag_pill("unverified")}</td>',
            ]
            out.append(f'<tr id="{r["record_id"].lower()}"><td class="num"><strong>{e(r["record_id"])}</strong></td>'
                       + "".join(cells) + "</tr>")
        return "".join(out)

    def details():
        out = []
        for r in recs:
            d = r.get("observation_2026_11_17") or {}
            markers = ", ".join(d.get("fallback_markers") or []) or "none observed"
            brand = ""
            if r["record_id"] == "PI-04":
                brand = ("Brand cross-read: the official ThermoMaven site names its instant-read models "
                         "F1 Pro and F1 Turbo — its F1 Turbo carries a half-second read — and does not use the "
                         f'&ldquo;1 Sec&rdquo; label the observed listing carries, so the brand page does not settle '
                         f'which model this is. {src_link("S37")}')
            elif r["record_id"] == "PI-05":
                brand = ("Brand cross-read: the official CHEF iQ page for the iQ Sense states model "
                         "CQ60-3C-Z3-E, five sensors and an ambient range to 1,000 °F, and its own use-case copy "
                         f"names the air fryer — the only submitted product that touches this site&rsquo;s existing "
                         f'topic at all. {src_link("S36")}')
            scope = r.get("not_in_this_sites_scope") or ""
            out.append(
                f'<div class="reg-item"><h4>{e(r["record_id"])} · {e(d.get("candidate_asin") or "no candidate ASIN")}</h4>'
                f'<p class="tiny muted">Observed {e(d.get("observed_on") or "—")} by {e(d.get("observed_by") or "an earlier pass")}</p>'
                f'<p class="small"><strong>Listing title as served</strong><br>{e(d.get("listing_title_as_served") or "not read")}</p>'
                f'<p class="small"><strong>Category as served</strong><br>{e(d.get("category_breadcrumb_as_served") or "not read")}</p>'
                f'<p class="tiny muted"><strong>Redirect markers</strong>: {e(markers)}</p>'
                f'<p class="small">{e(d.get("stable_vs_prior_observation") or "")}</p>'
                + (f'<p class="small">{e(brand)}</p>' if brand else "")
                + (f'<p class="small">{e(scope)}</p>' if scope else "")
                + "</div>")
        return "".join(out)

    def to_open():
        return "".join(f"<li>{e(s)}</li>" for s in (gate.get("to_open") or []))

    n_open = N_SUBMITTED_LINKS - n_conf
    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Submitted links register</p>
<h1>The {N_SUBMITTED_LINKS_WORD} links you submitted, and what each one is confirmed to be</h1>
<p class="lede">An affiliate link is a promise about two things: which product a reader lands on, and which account gets
credit for the click. This page records what this project was told and what it could see, in separate columns, and leaves
both blank where neither is settled. Nothing here is inferred from a redirect.</p>

<div class="grid grid-4" style="margin-bottom:1rem">
  <div class="stat"><div class="n">{N_SUBMITTED_LINKS}</div><div class="l">Links submitted to this project</div><div class="h">Three on 2026-11-13, two more on 2026-11-17</div></div>
  <div class="stat ok"><div class="n">{n_obs}</div><div class="l">Redirect destinations observed live</div><div class="h">Re-read {e(LINK_CHECK_DATE)}</div></div>
  <div class="stat bad"><div class="n">{n_conf}</div><div class="l">Products whose intended identity is confirmed</div><div class="h">The number every money decision rests on</div></div>
  <div class="stat warn"><div class="n">{e("open" if GATE_OPEN else "closed")}</div><div class="l">Special-Link gate</div><div class="h">No link carries a tag while it reads closed</div></div>
</div>

<div class="callout warn">
  <strong>The finding that needs your attention first</strong>
  <p class="small">{e(obs.get("the_new_finding") or "")}</p>
  <p class="tiny muted">How it was read: {e(obs.get("method") or "")} Register rows
  <a href="flagged.html#f76">F76</a> and <a href="flagged.html#f77">F77</a>; the two new links as
  source {src_link("S38")}, and the brands&rsquo; own pages as {src_link("S36")} and {src_link("S37")}.</p>
</div>

<h2>Intended versus observed, kept apart</h2>
<p class="small">{e(INTENT.get("purpose") or "")}</p>
<p class="small">{e(rule.get("why") or "")} {src_link("S23")}</p>

<div class="tablewrap">
<table>
  <caption>Every link submitted to this project — as supplied, as intended, as observed</caption>
  <thead><tr>
    <th style="width:7%">ID</th><th style="width:19%">Submitted link</th>
    <th style="width:15%">Token as supplied</th><th style="width:22%">Intended product (the four fields only you can fill)</th>
    <th style="width:15%">Observed candidate</th><th style="width:22%">Status</th>
  </tr></thead>
  <tbody>{rows()}</tbody>
</table>
</div>
<p class="tiny muted">The four intended-product fields are the ones this register waits on: intended ASIN, official listing
URL, confirmation date, confirmation source. They stay blank until a human with the Amazon account states them, because a
redirect is a destination and not an intention — merging the two columns is the exact failure this register exists to
prevent, and it is why the observed column is allowed to be full while the intended column is empty.</p>

<h2>What each link landed on</h2>
<div class="reg-grid">{details()}</div>
<p class="small">Amazon prices, star ratings and review counts appear on the pages behind those links. None is reproduced
here or anywhere on this site: display of price and availability is limited to links Amazon serves, and customer reviews
and ratings to the Creators or Product Advertising API, which this project does not hold. {src_links(['S2'])}</p>

<h2>The tracking ID, and the gate that keeps it out of your links</h2>
<div class="{'gate open' if GATE_OPEN else 'gate'}">
  <span class="pill {'pill-ok' if GATE_OPEN else 'pill-warn'}">Gate {e("open" if GATE_OPEN else "closed")}</span>
  <strong>Selected tracking ID: <code class="link-token">{e(tok)}</code></strong>
  <span class="tiny muted">{e(TRACKING_ID.get("status") or "")}</span>
</div>
<div class="reg-item" style="margin:.6rem 0 1rem">
  <dl class="kv">
    <dt>Provenance</dt><dd>{e(TRACKING_ID.get("provenance") or "")}</dd>
    <dt>Shape check</dt><dd>{e((TRACKING_ID.get("format_check") or {}).get("result") or "")} {src_link("S6")}</dd>
    <dt>What it cannot establish</dt><dd>{e((TRACKING_ID.get("format_check") or {}).get("what_this_check_cannot_establish") or "")}</dd>
    <dt>Your action</dt><dd>{e((TRACKING_ID.get("owner_action") or {}).get("what") or "")}
      {cell_link((TRACKING_ID.get("owner_action") or {}).get("where"), "Associates Central → Manage your Tracking ID")}
      (about {e(str((TRACKING_ID.get("owner_action") or {}).get("estimated_minutes") or ""))} minutes)</dd>
    <dt>Enforced by</dt><dd>{e(gate.get("enforced_by") or "")} — a tagged anchor while the gate is closed fails the build</dd>
  </dl>
</div>
<p class="small"><strong>Why the gate exists.</strong> {e(gate.get("why_closed") or "")}</p>
<p class="small"><strong>What opening it takes</strong> — four edits in order, and no template change:</p>
<ol class="tight small">{to_open()}</ol>

<h2>The link format the register will switch to</h2>
<p class="small">When a record&rsquo;s identity and the account&rsquo;s tag are both confirmed, that product&rsquo;s CTA
becomes a canonical Special Link built from the confirmed ASIN and the confirmed tag. It is shown below as text, not as a
clickable link, on purpose: until both confirmations exist this site does not publish a commercial destination it assembled
itself.</p>
<div class="tablewrap">
<table>
  <caption>Live href versus the href the build will use once the gate opens</caption>
  <thead><tr><th style="width:9%">ID</th><th style="width:33%">Live href today</th>
  <th style="width:36%">Href after confirmation</th><th style="width:22%">Blocked by</th></tr></thead>
  <tbody>
  {''.join(
      f'<tr><td class="num">{e(r["record_id"])}</td>'
      f'<td class="small"><code class="link-token">{e(r["submitted_link"])}</code></td>'
      f'<td class="small"><code class="link-token">https://www.amazon.com/dp/&lt;confirmed ASIN&gt;?tag={e(tok)}</code>'
      f'<div class="tiny muted">not emitted yet</div></td>'
      f'<td class="small"><a href="flagged.html#f78">F78</a> · <a href="questions.html#q-28">Q-28</a> · '
      f'<a href="suggestions.html#sg-37">SG-37</a></td></tr>'
      for r in recs)}
  </tbody>
</table>
</div>

<h2>How to close a row</h2>
<ol class="tight small">
  <li>Open the submitted link in the browser you use for the Amazon account, and read the listing title and the model line
  in its Product information block.</li>
  <li>If it is the product you meant, write the official <code>/dp/&lt;ASIN&gt;</code> URL, today&rsquo;s date and
  &ldquo;confirmed in my own browser&rdquo; into that record&rsquo;s <code>intended_product</code> fields in
  <code>data/product-intent-confirmations.json</code>. If it is not, write which product you meant instead — the
  observation column stays as it is.</li>
  <li>Confirm the tag in Associates Central, set <code>tagging_gate.state</code> to <code>open</code>, and rebuild.
  {n_open} row{'s' if n_open != 1 else ''} still need the first two steps.</li>
  <li>Test one product before scaling: click the rebuilt link, place or wait for a report window, and confirm the click and
  the order appear under {e(tok)}. Scaling an untested tag is how a season of content earns nothing.</li>
</ol>

<p class="small muted"><a href="measurement.html">What this site can measure</a> ·
<a href="flagged.html">Flagged for review</a> ·
<a href="questions.html#q-01">Q-01 model identity</a> ·
<a href="questions.html#q-04">Q-04 tag inside the links</a> ·
<a href="suggestions.html#sg-36">SG-36 the product-set decision</a> ·
raw register: <code>data/product-intent-confirmations.json</code></p>
"""
    return layout("links.html", "Submitted links register", body, active="links.html",
                  description=(f"All {N_SUBMITTED_LINKS} Amazon links submitted to this project: the token exactly as "
                               f"supplied, the intended product (blank until the account holder confirms it), the redirect "
                               f"destination observed {LINK_CHECK_DATE}, and the gate that keeps an unverified tracking ID "
                               f"out of every outbound link."),
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Submitted links register", page_url("links.html")),
    ])]
              )


def _intent_pill(intended):
    status = str(intended.get("status") or "").lower()
    if status == "confirmed":
        return '<span class="pill pill-ok">Intent confirmed</span>'
    if "not confirmed" in status:
        return '<span class="pill pill-warn">Not confirmed</span>'
    return '<span class="pill pill-info">' + e(status or "no status recorded") + '</span>'


def page_measurement():
    \"\"\"The event dictionary, the collector's posture, and the ledger that is empty on purpose.\"\"\"
    if not MEASUREMENT:
        return layout("measurement.html", "Clicks and conversions",
                      '<h1>Clicks and conversions</h1><p class="lede">The measurement register '
                      '<code>data/measurement.json</code> is not present, so no event definitions and '
                      'no ledger schema can be rendered. Nothing is inferred in its absence.</p>',
                      active="measurement.html",
                      description="The measurement register is not available in this build.")
    m = MEASUREMENT
    posture = m["posture"]
    ev = m["events"]
    ledger = m["ledger"]
    policy_url = "https://affiliate-program.amazon.com/help/operating/policies"
    tag_url = "https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA"

    def ev_rows():
        out = []
        for x in ev:
            props = "; ".join(x["properties"]) or "—"
            never = "; ".join(x["never_contains"]) or "—"
            rule_src = (f'<a href="{tag_url}" target="_blank" rel="noopener">Tracking-ID reports, per ID</a>'
                        if x["id"] == "EV-05" else
                        f'<a href="{policy_url}" target="_blank" rel="noopener">§2(b), §3(e), §6(t)</a>')
            status_pill = ('<span class="pill pill-ok">Live</span>' if "implemented" in x["status"]
                           else '<span class="pill pill-warn">Not collected</span>')
            out.append(
                f'<tr id="{x["id"].lower()}"><td class="num"><strong>{e(x["id"])}</strong></td>'
                f'<td><code class="link-token">{e(x["name"])}</code></td>'
                f'<td class="small">{e(x["definition"])}</td>'
                f'<td class="small">{e(props)}</td>'
                f'<td class="small">{e(never)}</td>'
                f'<td class="small">{status_pill} <span class="tiny">{e(x["status"])}</span>'
                f'<div class="tiny muted">{e(x["decision_value"])}</div></td>'
                f'<td class="small">{rule_src}</td></tr>')
        return "".join(out)

    def col_rows():
        return "".join(
            f'<tr><td><code class="link-token">{e(c["key"])}</code></td><td>{e(c["label"])}</td>'
            f'<td class="small">{e(c["rule"])}</td>'
            f'<td class="small">{flag_pill("unverified") if not (ledger.get("rows") or []) else flag_pill("verified")}'
            f'<div class="tiny muted"><a href="flagged.html#f79">F79</a> — why it is empty</div></td></tr>'
            for c in ledger["columns"])

    rows = ledger.get("rows") or []
    rows_table = ""
    if rows:
        body_rows = "".join(
            "<tr>" + "".join(f'<td class="small">{e(str(r.get(c["key"]) or ""))}</td>' for c in ledger["columns"]) + "</tr>"
            for r in rows)
        rows_table = (f'<div class="tablewrap"><table><caption>Rows</caption><thead><tr>'
                      + "".join(f'<th>{e(c["label"])}</th>' for c in ledger["columns"])
                      + f'</tr></thead><tbody>{body_rows}</tbody></table></div>')
    checklist = "".join(f"<li>{e(s)}</li>" for s in ledger["first_row_checklist"])
    anti = "".join(
        f'<div class="reg-item"><h4>{e(a["name"])}</h4><p class="small">{e(a["rule"])}</p></div>'
        for a in m["anti_patterns"])
    sub = m["sub_tag_plan"]
    endpoint_state = "on" if posture.get("endpoint") else "off"

    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Clicks and conversions</p>
<h1>Clicks and conversions: what this site can measure, and what it refuses to guess</h1>
<p class="lede">The brief puts measurement before anything else gets written, so here is the instrument in full: five
defined events, one collector, one ledger with the rules for filling it. It reports zero readers, because it is not
analytics — it is the wiring that becomes analytics when an endpoint exists. That distinction is the only reason this page
is publishable and a decorative dashboard would not be.</p>

<div class="grid grid-4" style="margin-bottom:1rem">
  <div class="stat"><div class="n">{len(ev)}</div><div class="l">Events defined</div><div class="h">Named in data, rendered here</div></div>
  <div class="stat ok"><div class="n">0</div><div class="l">Cookies set</div><div class="h">Nothing is stored about a reader&rsquo;s identity</div></div>
  <div class="stat bad"><div class="n">{len(rows)}</div><div class="l">Campaign ledger rows</div><div class="h">Empty until an authorized report exists</div></div>
  <div class="stat warn"><div class="n">{endpoint_state}</div><div class="l">Collector endpoint</div><div class="h">{e(posture.get("endpoint_status") or "")}</div></div>
</div>

<div class="device-panel">
  <h2 style="margin:0 0 .35rem">Counts held on this device</h2>
  <p class="tiny muted">Read out of your browser&rsquo;s local storage by the script this site ships. It is your visit,
  not your audience: no other reader&rsquo;s count is included, and none of yours leaves your device.</p>
  <div id="device-panel"><noscript><p class="small">JavaScript is off, so nothing has been counted on this device, and
  nothing will be.</p></noscript></div>
  <textarea id="export-box" rows="6" hidden aria-label="Local counts, as JSON, for you to copy"></textarea>
  <p class="tiny muted"><button type="button" class="btn btn-ghost" data-export="1">Export these counts as JSON</button>
  &nbsp;A copy belongs in the owner&rsquo;s ticket. It is never summed into the ledger below.</p>
</div>

<h2>What runs, and what does not</h2>
<div class="reg-grid">
  <div class="reg-item"><h4>What runs</h4><p class="small">{e(posture["what_runs"])}</p></div>
  <div class="reg-item"><h4>What does not run</h4><p class="small">{e(posture["what_does_not_run"])}</p></div>
  <div class="reg-item"><h4>The endpoint</h4><p class="small">{e(posture["endpoint_status"])}</p></div>
  <div class="reg-item"><h4>Why not just a hosted script</h4><p class="small">{e(posture["why_not_just_third_party"])}</p></div>
</div>
<div class="callout info">
  <strong>The boundary before any of this becomes analytics</strong>
  <p class="small">{e(posture["deployment_boundary"])}</p>
  <p class="tiny muted">Obligations this design answers to: {src_links([s["id"] for s in posture.get("sources", [])])}</p>
</div>

<h2>The five events</h2>
<p class="small">{e(m["why_this_file_exists"])}</p>
<div class="tablewrap">
<table>
  <caption>Event dictionary — every event names the decision it informs, or it does not ship</caption>
  <thead><tr><th style="width:6%">ID</th><th style="width:12%">Event</th><th style="width:23%">Definition</th>
  <th style="width:15%">Properties</th><th style="width:15%">Never contains</th>
  <th style="width:21%">Status, and what it decides</th><th style="width:8%">Rule source</th></tr></thead>
  <tbody>{ev_rows()}</tbody>
</table>
</div>

<h2>The campaign ledger</h2>
<p class="small">{e(ledger["purpose"])}</p>
<div class="tablewrap">
<table>
  <caption>Column definitions — {len(rows)} row{'s' if len(rows) != 1 else ''} recorded, in {N_SUBMITTED_LINKS} links&rsquo; worth of live traffic still unattributed</caption>
  <thead><tr><th style="width:15%">Column</th><th style="width:15%">Label</th>
  <th style="width:57%">Rule for what may be written here</th><th style="width:13%">Current state</th></tr></thead>
  <tbody>{col_rows()}</tbody>
</table>
</div>
{rows_table}
<div class="ledger-empty"><strong>{'No rows yet.' if not rows else 'Rows above come from the register only.'}</strong>
{e(ledger["why_empty"])}</div>

<h2>What has to happen before the first row</h2>
<ol class="tight small">{checklist}</ol>

<h2>The measurement option that needs no infrastructure</h2>
<div class="reg-item" style="margin:.6rem 0 1rem">
  <h4>Per-channel tracking IDs, which Amazon reports for you</h4>
  <p class="small">{e(sub["what"])}</p>
  <p class="small"><strong>Limit.</strong> {e(sub["limit"])}</p>
  <p class="tiny muted">Status: {e(sub["status"])} {src_links([s["id"] for s in sub["sources"]])}</p>
</div>

<h2>What this register rules out</h2>
<div class="reg-grid">{anti}</div>

<div class="callout note">
  <strong>What this pass verified, and what it did not</strong>
  <p class="small">{e(m["verification"]["method"])}</p>
  <p class="small">{e(m["verification"]["what_is_not_verified"])}</p>
</div>

<p class="small muted"><a href="links.html">Submitted-links register</a> ·
<a href="questions.html#q-29">Q-29 where the data goes</a> ·
<a href="suggestions.html#sg-38">SG-38 what to do with the counter</a> ·
<a href="flagged.html#f79">F79 the honest limit of this design</a> ·
raw register: <code>data/measurement.json</code></p>
"""
    return layout("measurement.html", "Clicks and conversions", body, active="measurement.html",
                  description="The five measurement events this site defines, the cookieless local click counter that "
                              "ships, the deployment boundary before any of it becomes analytics, and the campaign ledger "
                              "that stays empty until an authorized first-party report fills it.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Clicks and conversions", page_url("measurement.html")),
    ])]
              )


PAGES_CACHE = {}


def main():
    assets = ROOT / "assets"'''
rep(ANCHOR_J, NEW_J, "page builders + guards")

# ----------------------------------------------------------- L. register in main
ANCHOR_K = '''    pages["questions.html"] = page_questions()'''
NEW_K = '''    pages["questions.html"] = page_questions()
    # Added 2026-11-17 (arena/58cbaaa2): the register of submitted links, and the
    # measurement contract. Both are generated from data; neither is hand-published.
    pages["links.html"] = page_links()
    pages["measurement.html"] = page_measurement()'''
rep(ANCHOR_K, NEW_K, "pages dict registration")

ANCHOR_L = '''    pages = {rel: qualify_affiliate_links(text) for rel, text in pages.items()}'''
NEW_L = ANCHOR_L + '''

    # The pass-13 guards read the rendered set, so the render is handed to them through a
    # module-level cache rather than passed as an argument: the two new pages, the footer and
    # the landing note all derive their counts from data, and a guard that recomputed them
    # would be checking a function against itself.
    PAGES_CACHE.clear()
    PAGES_CACHE.update(pages)'''
rep(ANCHOR_L, NEW_L, "PAGES_CACHE population")

ANCHOR_M = '''    orphan_pages = check_no_orphan_pages(pages)'''
NEW_M = '''    gate_problems = check_special_link_gate()
    if gate_problems:
        raise SystemExit("BUILD FAILED — Special-Link gate: a tagged link or an unsupported "
                         "gate state:\\n  " + "\\n  ".join(gate_problems))
    linkcount_problems = check_submitted_link_count()
    if linkcount_problems:
        raise SystemExit("BUILD FAILED — a page states a submitted-link count the register "
                         "disagrees with (flag F80):\\n  " + "\\n  ".join(linkcount_problems))
    measure_problems = check_measurement_claims()
    if measure_problems:
        raise SystemExit("BUILD FAILED — the privacy statement or the measurement page "
                         "disagrees with the shipped collector (flag F79):\\n  " + "\\n  ".join(measure_problems))

    orphan_pages = check_no_orphan_pages(pages)'''
rep(ANCHOR_M, NEW_M, "guard wiring in main()")

# --------------------------------------------------------- N. requirement counts
ANCHOR_N = '''        "n_stale_briefings": len(stale),
    }'''
NEW_N = '''        "n_stale_briefings": len(stale),
        # Added 2026-11-17 (arena/58cbaaa2): the two counts this pass introduced, both read
        # from their registers so a register edit cannot leave a sentence behind.
        "n_submitted_links": str(N_SUBMITTED_LINKS),
        "n_intent_confirmed": str(sum(
            1 for r in SUBMITTED_LINKS
            if (r.get("intended_product") or {}).get("status", "").lower() == "confirmed")),
        "n_events": str(len((MEASUREMENT or {}).get("events") or [])),
        "n_ledger_rows": str(len(((MEASUREMENT or {}).get("ledger") or {}).get("rows") or [])),
    }'''
rep(ANCHOR_N, NEW_N, "req_counts tokens for the new registers")

# ---------------------------------------------------------------------------- apply
bad = []
for old, new, label in edits:
    n = src.count(old)
    if n != 1:
        bad.append(f"{label}: anchor matched {n} times")
        continue
    src = src.replace(old, new, 1)
if bad:
    sys.exit("PATCH ABORTED (nothing written):\n  " + "\n  ".join(bad))

B.write_text(src, encoding="utf-8")
print(f"patched build.py: {len(edits)} edits applied")
