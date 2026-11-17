"""Pass 13, patch 2: the product-link register, the measurement page, the
navigation restructure, the privacy-preserving counter, and three build guards.
"""
import re
import sys

P = "build.py"
s = open(P, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f"expected {count} occurrence(s), found {n} of:\n{old[:300]}")
    s = s.replace(old, new)


# ============================================================ flags F76+ ====
FLAG_ANCHOR = """     []),
"""
last_flag = s.rindex('("F75"')
insert_at = s.index(FLAG_ANCHOR, last_flag) + len(FLAG_ANCHOR)

NEW_FLAGS = '''    ("F76", "The intended ASIN is blank for all five supplied links. Only the account holder can fill it in.",
     "All five supplied links", "A reproducible redirect destination is not an intention. Every recorded read since 2026-11-13 has observed where these links go; nothing observed anywhere states which product they were created to promote. The product-link register therefore keeps two separate blocks per link: 'intent' (intended ASIN, official listing URL, confirmation date, source) and 'observation' (what the link actually did). Both blocks are published, the intent block is empty, and copying an observed ASIN into it is a build failure - see check_link_intent(). This pass deliberately does not assert that the supplied short links are invalid; their compliance status is unresolved.", ["S17", "S40", "S36"]),
    ("F79", "A Selected Tracking ID was supplied; its format matches Amazon's documented convention but its ownership is unconfirmed.",
     "All five supplied links", "The account holder supplied a Selected Tracking ID on 2026-11-17 and it is recorded in data/config.json and on the product-link register. Amazon's own help states that its software 'automatically adds \\"-20\\" to the end of all Associate IDs', so the string has the documented shape of a US Associates Store/Tracking ID (S36). That is a statement about format only: it is not evidence that the ID belongs to this account, that the account is approved, or that the ID is attached to these five links. No resolved URL observed across eight rounds has carried a visible tag= parameter (F6). Confirm in Manage your Tracking IDs, then validate one link per product (SG-38).", ["S36", "S2"]),
'''
s = s[:insert_at] + NEW_FLAGS + s[insert_at:]

# ============================================================= NAV entries ===
sub(
    '    ("compliance.html", "Compliance", "Program rules, quoted, with sources"),\n',
    '    ("compliance.html", "Compliance", "Program rules, quoted, with sources"),\n'
    '    # Added 2026-11-17 (arena/9fe0b6b3): every supplied link, with what it was meant to\n'
    '    # point at kept separate from what it does when followed.\n'
    '    ("links.html", "Product link register", "Five supplied links, intent and observation kept apart"),\n'
    '    # Added 2026-11-17 (arena/9fe0b6b3): measurement is turned on before the next guide\n'
    '    # is written, so the counter, the endpoint contract and the empty ledger ship first.\n'
    '    ("measurement.html", "Measurement", "Five events, the endpoint contract, an empty ledger"),\n',
)

# =============================================================== sidebar ====
sub(
    '''    <div class="group">
      <h4>Trust &amp; evidence</h4>
      {N("compliance.html")}
      {N("flagged.html")}
      {N("data.html")}
      {N("reverification.html")}
    </div>
    <div class="group">
      <h4>Owner workspace</h4>
      {N("decisions.html")}
      {N("suggestions.html")}
      {N("design-prompt.html")}
      {N("questions.html")}
      {N("requirements.html")}
      {N("topics.html")}
      {N("executive-summary.html")}
      {N("platform.html")}
      {more_nav}
    </div>''',
    '''    <div class="group">
      <h4>Data &amp; verification</h4>
      {N("links.html")}
      {N("measurement.html")}
      {N("data.html")}
      {N("compliance.html")}
      {N("flagged.html")}
      {N("reverification.html")}
      {N("pass10.html")}
      {N("figures.html")}
      {N("platform.html")}
      {N("requirements.html")}
      {more_nav}
    </div>
    <div class="group">
      <h4>Owner workspace</h4>
      {N("decisions.html")}
      {N("suggestions.html")}
      {N("decision-log.html")}
      {N("design-prompt.html")}
      {N("questions.html")}
      {N("topics.html")}
      {N("executive-summary.html")}
    </div>''',
)

# Product count in the sidebar is now generated, not typed.
sub(
    """>Category: Kitchen<span class="sub">3 tracked products</span></a>""",
    """>Category: Kitchen<span class="sub">{len(PRODUCT_LIST)} tracked products</span></a>""",
)

# ========================================================= footer nav list ===
sub(
    '    <div>\n      <h5>Sources</h5>\n',
    '''    <div>
      <h5>Every dashboard</h5>
      <p>Every data and verification surface on this site, including the ones the sidebar leaves out:</p>
      <ul class="foot-nav">
        {foot_nav}
      </ul>
    </div>
    <div>
      <h5>Sources</h5>
''',
)

# Build the footer index from NAV, so a page added to NAV cannot be missing from it.
sub(
    '    social_alt = og_image_alt or f"{SITE_NAME} — {SITE_TAGLINE}"\n',
    '    social_alt = og_image_alt or f"{SITE_NAME} — {SITE_TAGLINE}"\n'
    '\n'
    '    # Every dashboard surface stays reachable from the footer even when the sidebar\n'
    '    # collapses it into one group: the brief asks for the front page to read like a\n'
    '    # publication while the verification machinery stays one click away, and a link\n'
    '    # that only exists in a collapsed group is a link nobody finds.\n'
    '    foot_nav = "".join(\n'
    '        f\'<li><a href="{prefix}{href}">{e(label)}</a></li>\'\n'
    '        for href, label, _sub in NAV\n'
    '    )\n',
)

# ============================================================= measure.js ====
MEASURE_JS = r'''/* Zone1 - privacy-preserving event counter.  Generated by build.py; do not edit.
 *
 * Counts events, not people. No cookie, no localStorage, no sessionStorage, no
 * fingerprinting surface and no per-reader identifier of any kind. Two visits are
 * indistinguishable to this script.
 *
 * If no endpoint is configured, events are counted in memory for the current visit
 * and nothing leaves the browser. The site says so in its footer rather than
 * implying measurement that does not exist - see data/analytics.json.
 */
(function () {
  "use strict";

  var CFG = window.__Z1_MEASURE__ || { endpoint: "" };

  function path() {
    var p = location.pathname || "/";
    var i = p.indexOf("/Zone1/");
    return i === -1 ? p : p.slice(i + 6) || "/";
  }

  // Coarse referrer: the registrable domain only. Never the full URL, never the
  // query string - a search query can carry personal terms.
  function referrer() {
    try {
      var host = document.referrer ? new URL(document.referrer).hostname : "";
      if (!host) { return ""; }
      var parts = host.split(".");
      return parts.slice(Math.max(0, parts.length - 2)).join(".");
    } catch (err) { return ""; }
  }

  function send(payload) {
    counts[payload.e] = (counts[payload.e] || 0) + 1;
    if (!CFG.endpoint) { return; }          // nothing leaves the browser
    var body = JSON.stringify(payload);
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(CFG.endpoint, new Blob([body], { type: "application/json" }));
        return;
      }
      fetch(CFG.endpoint, {
        method: "POST", keepalive: true,
        headers: { "Content-Type": "application/json" }, body: body
      });
    } catch (err) { /* a blocked endpoint must never change what the reader sees */ }
  }

  var counts = {};

  function ev(name, extra) {
    var payload = { e: name, p: path(), r: referrer(), v: null };
    if (extra) {
      for (var k in extra) {
        if (Object.prototype.hasOwnProperty.call(extra, k)) { payload[k] = extra[k]; }
      }
    }
    send(payload);
    return payload;
  }

  function closestAnchor(node) {
    while (node && node !== document) {
      if (node.tagName === "A") { return node; }
      node = node.parentNode;
    }
    return null;
  }

  // 1. page_view
  ev("page_view");

  // 2. outbound_click - any sponsored product link. Counted before navigation and
  //    never intercepted: the href stays exactly what the build produced.
  document.addEventListener("click", function (e) {
    var a = closestAnchor(e.target);
    if (!a) { return; }
    if (a.getAttribute("href") && a.getAttribute("href").indexOf("feed.xml") !== -1) {
      ev("subscribe", { v: 1 });                                   // 5. subscribe
      return;
    }
    var asin = a.getAttribute("data-z1-asin");
    if (!asin) { return; }
    ev("outbound_click", { a: asin, l: a.getAttribute("data-z1-link") || "" });
  }, true);

  // 3. chooser_complete - dispatched by the chooser, or by any control marked for it.
  document.addEventListener("z1:chooser-complete", function (e) {
    ev("chooser_complete", { a: (e.detail && e.detail.slug) || "", v: (e.detail && e.detail.steps) || null });
  });

  // 4. guide_read - fires once when the end of a guide enters the viewport.
  var endMarker = document.querySelector("[data-z1-guide-end]");
  if (endMarker && "IntersectionObserver" in window) {
    var fired = false;
    new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting && !fired) {
          fired = true;
          ev("guide_read", { v: 100 });
        }
      });
    }, { threshold: 0.25 }).observe(endMarker);
  }

  // Exposed for debugging and for the build's own smoke test. Deliberately small:
  // in-memory totals for this visit only, and an empty object when nothing fired.
  window.Z1 = { counts: counts, event: ev };
})();
'''

sub(
    'def main():\n    assets = ROOT / "assets"\n',
    'MEASURE_JS = r"""' + MEASURE_JS + '"""\n'
    '\n'
    '\n'
    'def measure_js():\n'
    '    """Bake the endpoint URL into the counter so the client ships no configuration file."""\n'
    '    cfg = {\n'
    '        "endpoint": ANALYTICS_ENDPOINT,\n'
    '        "events": [x["id"] for x in ANALYTICS_EVENTS],\n'
    '    }\n'
    '    return MEASURE_JS.replace("__Z1_CONFIG__", json.dumps(cfg))\n'
    '\n'
    '\n'
    'def main():\n'
    '    assets = ROOT / "assets"\n',
)

sub(
    '    (assets / "app.js").write_text(JS, encoding="utf-8")\n',
    '    (assets / "app.js").write_text(JS, encoding="utf-8")\n'
    '    (assets / "measure.js").write_text(measure_js(), encoding="utf-8")\n',
)

open(P, "w", encoding="utf-8").write(s)
print("patch 2 applied")
