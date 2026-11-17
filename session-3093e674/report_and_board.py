import pathlib, datetime

TODAY = "2026-11-17"
SESS = "arena/3093e674-zone1"

# ================================================================ EXECUTIVE SUMMARY §24
ES = f"""

## 24. Monetisation and measurement pass — session `{SESS}` (2026-11-17)

Sixteen passes published a shop that could not earn and said so politely. The blocker was recorded as
an owner absence — "tag pending" — and the owner's brief of 2026-11-17 answered it in four words:
**Selected Tracking ID:shopnow047c-20**. That exposed a second fact nobody had written down: `build.py`
never read `data/config.json`, so the tag had been supplied to a file no generator opened. The site was
not unmonetisable because the owner was slow; it was unmonetisable because the wiring did not exist.

**What this pass built.**

* **Tagged Special Links, generated and guarded.** One function composes
  `amazon.com/dp/<ASIN>?tag=<id>` for every buy CTA — product pages, the comparison matrix's new
  action row, the category table and the picks cards. `check_special_links()` fails the build if an
  anchor forgets the tag, points at the `link.amazon` redirector instead of a product, carries a tag the
  config never declared, or breaks Amazon's published `XXXXX-##` shape. The supplied short links stay
  visible on each product page as the artefact being checked. §2(a): "Special Links must use the
  Associates ID we have assigned to you."
* **A product-intent register that will not let two fields merge.** `data/link-intent.json` — five rows
  (LI-01…LI-05), each keeping *intended* (owner statement only) beside *observed* (fetch only), with
  `observed_on` dates. `check_link_intent()` fails if a row records the two as the same product without a
  confirmation that starts "confirmed by the account holder", and if any marketed product lacks a
  covering row. Published on `links.html`.
* **Measurement you can hold in one hand.** Five events specified in `data/measurement.json`, counted in
  the visitor's own browser, transmitted nowhere, with export and erase buttons. The footer's "runs no
  analytics and sets no cookies" survives because the code cannot contradict it:
  `check_measurement_contract()` greps `assets/app.js` for `fetch(`/`XMLHttpRequest`/`sendBeacon`/
  `document.cookie`/dynamic imports, and fails if any page still says the site runs no analytics while an
  endpoint is configured. Published on `measurement.html`.
* **A campaign ledger with a provenance gate.** `data/campaign-ledger.json` is the site's only home for a
  performance number: every row needs a period, a source whose host this repository already recognises,
  and a date obtained; `revenue`, `forecast`, `conversion_rate` and `expected_earnings` are rejected as
  fields outright. It ships with **zero rows**, because the honest count of observed campaigns is zero.
* **The fourth guide the brief listed and the article set lacked** — *Questions to ask before buying a
  multi-function kitchen appliance* (TP-21), plus a bridge article for the two products the brief added
  (*Can you put a wireless meat thermometer in an air fryer?*), and a front-page band that leads with the
  buyer's four questions instead of a product grid.
* **Seasonal pages that expire.** Both seasonal articles now carry a validity window in the register,
  rendered on the page, and `check_seasonal_expiry()` stops the build the day after a window closes —
  §2(b) requires references to limited-time promotions to come down when the promotion ends.
* **Handover counted, not typed.** The page's own heading said "Five actions, about an hour, eighteen
  flags" while the register held a different number; it is computed from the rows now.

**What the brief's two new links turned out to be.** `B0c8moW59` → `/dp/B0DHZTCNR5` (ThermoMaven F1
instant-read) and `B0f3GKalj` → `/dp/B0DZFD6R9Z` (CHEF iQ iQ Sense Gen 3) — thermometers, outside the
air-fryer set this site markets. They are recorded, sourced and disclosed as **candidates only**: no
specs published as product claims, no merge into the comparison, because the listing's title says "1
Sec" while the brand states 0.7 s for an F1 sold in three variants (**Q-29**). The scope question — three
products or five — is **Q-27** and belongs to the owner; this pass registered it rather than answer it
(**F76**). **F77** records the other half of the honesty: the root build tags its links while
`scripts/build_s2_site.py` still emits untagged ones, and both are served.

**Gates on the final tree.** `build.py` exit 0 (53 sitemap URLs, feed 23 items, every guard green,
rebuild idempotent) · `verify.py` 132 pages, 77 spec rows (75 verified / 2 blank+flagged), 40 sources,
0 errors, 0 external warnings · `ci-check.sh` 33 tests, audit clean, 9,191 links / 0 broken ·
`research/check_research.py` OK · `platform/audit/report.py` AUDIT PASSED.
`reports/verification-2026-11-17-3093e674.md` carries the live reads behind every new claim.
"""
es = pathlib.Path('EXECUTIVE-SUMMARY.md')
t = es.read_text()
assert '## 24. Monetisation and measurement pass' not in t
es.write_text(t.rstrip() + "\n" + ES)
print('EXECUTIVE-SUMMARY.md:', len(t), '->', len(es.read_text()))


print('COORDINATION append lives in board_append.py (needs the PR number)')
