#!/usr/bin/env python3
"""One-shot patch: executive summary — derive the counts, add the pass-9 briefing.

Applied by session arena/88bb2db6 on 2026-11-15.

E1  "Twelve sources are used" was a hand-typed number. The register holds
    {n} now, and the number had already gone stale once before this pass. It is
    now computed from data/sources.json so it cannot drift again.
E2  "The ledger — 61 rows" was also hand-typed. The ledger now holds the 2026-11-14
    rows plus the pass-9 rows, so the count is computed from both.
E3  The "Product set" row pointed at reports/link-check-2026-11-14.md, a raw
    markdown file whose conclusion was later superseded. It now points at the
    rendered re-verification page, as the landing page does.
E4  A pass-9 briefing callout is added, so the executive summary reflects the
    latest state of the work rather than stopping at pass 8.
"""
from pathlib import Path

p = Path("build.py")
s = p.read_text(encoding="utf-8")

PATCHES = []


def sub(old, new, why):
    PATCHES.append((old, new, why))


# ---------------------------------------------------------------- E1 + E2 + E3
sub(
    '''        ("Product set", "Three supplied short links were followed; each fetch observed a landing on an air-fryer listing (candidate ASINs B0CDY277D3, B09B7SB46R, B08DKYBTPH). Token-to-ASIN mapping is not confirmed — see F14–F16 and reports/link-check-2026-11-14.md.", ["S16", "S17"]),''',
    '''        ("Product set", "Three supplied short links were followed; each fetch observed a landing on an air-fryer listing (candidate ASINs B0CDY277D3, B09B7SB46R, B08DKYBTPH). Token-to-ASIN mapping is not confirmed — see F14–F16 and the link checks on the <a href=\\"reverification.html\\">Re-verification</a> page.", ["S16", "S17"]),''',
    "E3: the Product set row points at the rendered re-verification page",
)

sub(
    '''        ("Re-verification (2026-11-14)", "Every published value was re-read against the official source it cites. The ledger — 61 rows, each with the value as published, what the source said on the day, a verdict and a link — is on the Re-verification page. Two blank rows were filled from the manufacturer's own spec block, and the disputed question of whether the short links shuffle between requests was closed by a repeat fetch plus a nonsense-token control.", ["S16", "S21", "S22"]),''',
    '''        (f"Re-verification ({REVERIFICATION['pass_date']} and 2026-11-15)", f"Every published value was re-read against the official source it cites. The ledger — {LEDGER_ROWS} rows in total, each with the value as published, what the source said on the day, a verdict and a link — is on the <a href=\\"reverification.html\\">Re-verification</a> page. Two blank rows were filled from the manufacturer's own spec block, and the disputed question of whether the short links shuffle between requests was closed by a repeat fetch plus a nonsense-token control.", ["S16", "S21", "S22"]),''',
    "E2: the ledger row count is computed from both passes",
)

sub(
    '''  <p class="small">Every specification asserted on the site was read from the manufacturer's own product page or owner's manual on {e(ACCESSED)}, and each one carries a clickable link to it. Twelve sources are used; none is a retailer, a review aggregator or an affiliate blog. Values that could not be confirmed are blank and listed, which is the only honest way to publish a comparison table.</p>''',
    '''  <p class="small">Every specification asserted on the site was read from the manufacturer's own product page or owner's manual on {e(ACCESSED)}, and each one carries a clickable link to it. {len(SOURCES["sources"])} sources are registered; none is a retailer, a review aggregator or an affiliate blog. Values that could not be confirmed are blank and listed, which is the only honest way to publish a comparison table.</p>''',
    "E1: the source count is computed from data/sources.json",
)

# ---------------------------------------------------------------- E4
sub(
    '''  did <em>not</em> return content, is in <code>EXECUTIVE-SUMMARY-PASS8.md</code> in the repository.</p>
</div>''',
    '''  did <em>not</em> return content, is in <code>EXECUTIVE-SUMMARY-PASS8.md</code> in the repository.</p>
</div>

<div class="callout note">
  <strong>Pass 9 — 2026-11-15 (final integration).</strong>
  <p class="small">A final-integration pass re-read the load-bearing facts against the live official
  sources and fixed what it found. <strong>One new conflict was recorded rather than resolved</strong>:
  the Emeril brand page says "Included are 7 premium accessories" while the supplied Amazon listing
  title says "Six Cooking Accessories Included" (<a href="flagged.html">F44</a>). The Emeril preset
  count was re-confirmed as 24 by reading the manual's two preset tables row by row, and the flag
  wording was tightened from "names exactly 24" to "lists 24 presets by name" because the manual
  never states the numeral. <strong>Ten defects in the site build itself were found and fixed</strong>,
  among them two decision pages that had each other's canonical URL and title, a page that stated
  16 suggestions while rendering 12, a buyer-facing link to a raw markdown file, and the complete
  absence of canonical URLs, social cards and structured data on every page. The site now ships a
  canonical URL, Open Graph and Twitter card tags and JSON-LD on all {len(PAGES_HTML)} root pages, and
  two new build guards fail the build on a nested anchor. The full evidence, including what this
  pass could <em>not</em> establish, is in
  <code>session-88bb2db6/EVIDENCE-2026-11-15.md</code> in the repository.</p>
</div>''',
    "E4: the pass-9 briefing is added to the executive summary",
)

for old, new, why in PATCHES:
    if s.count(old) != 1:
        raise SystemExit(f"PATCH FAILED ({s.count(old)} matches) - {why}\n{old[:160]}")
    s = s.replace(old, new)

# ---------------------------------------------------------------- the two derived numbers
old_anchor = '''def page_exec():
    # Economics are computed from the dataset'''
new_anchor = '''def page_exec():
    # The number of ledger rows the executive summary quotes. Derived from both ledgers
    # so it cannot drift: the 2026-11-14 pass and the pass-9 addendum.
    LEDGER_ROWS = len(REVERIFICATION["tests"]) + (len(PASS9["rows"]) if PASS9 else 0)
    PAGES_HTML = len(NAV)
    # Economics are computed from the dataset'''
if s.count(old_anchor) != 1:
    raise SystemExit("anchor PATCH FAILED")
s = s.replace(old_anchor, new_anchor)

p.write_text(s, encoding="utf-8")
print(f"applied {len(PATCHES)} patches + the derived-number anchor")
for _o, _n, why in PATCHES:
    print("  -", why)
