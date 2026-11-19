# Verification pass — arena/e9e5ab06-zone1 — 2026-11-19 (UTC)

**Session:** arena/e9e5ab06-zone1 (session e9e5ab06)
**Base:** main @ `0bcc272` (merge of PR #175)
**Task:** X-e9e5ab06 — independent line-by-line repo review, live re-verification
of the official sources behind the published values, structural audit of the
generated site against the standing brief, defect repair, full gate suite, then
PR → merge → GitHub Pages confirm → record.

## Method

- Every URL below was fetched **live on 2026-11-19** through a server-side
  fetch (`fetch_page`) and the value was read from the response body in this
  session. Values were not copied from earlier sessions' records.
- Verdicts: **confirms** = the live read matches the registered value;
  **note** = the live read is consistent but carries a date-stamp, drift or
  wording nuance recorded below; **differs** = the live read did not match the
  stored observation, recorded without changing the stored record.
- The baseline gate suite was run on the clean checkout **before any edit**;
  the full suite was re-run **after** the edits.

## A. Baseline gates, clean tree (before any edit)

| Gate | Result |
|---|---|
| `python3 build.py` | exit 0 — 37 sitemap URLs, 25 feed items |
| `python3 verify.py` | 137 pages, 77 spec rows (75 verified, 2 blank+flagged), 47 sources, **0 errors**, 0 external warnings |
| `python3 -m unittest discover -s tests` | 68 tests OK |
| `bash scripts/ci-check.sh` | OK — data audit clean, build current, link check 11,804 links OK, 8 Node + 33 engine tests OK |
| `python3 research/check_research.py` | OK — no broken links, no unsourced rows, disclosures on every page |
| `python3 scripts/verify_site.py` | ALL CHECKS PASSED — 11 pages, 53 spec fields, 393 assertions |

## B. The five supplied links, re-opened live

| Supplied link | Final URL observed in this session | Verdict |
|---|---|---|
| https://link.amazon/B04G1MEwY (read twice) | `https://www.amazon.com/` (generic homepage) both reads | **differs** from PI-01's stored observation (`/dp/B0CDY277D3`) — see note 1 |
| https://link.amazon/B02NbDxp3 | `https://www.amazon.com/` (generic homepage) | **differs** from PI-02's stored observation (`/dp/B09B7SB46R`) — see note 1 |
| https://link.amazon/B00hJ57DV | `https://www.amazon.com/` (generic homepage) | **differs** from PI-03's stored observation (`/dp/B08DKYBTPH`) — see note 1 |
| https://link.amazon/B0c8moW59 | `https://www.amazon.com/dp/B0DHZTCNR5?…plpRedirect=mhFallback` — title "ThermoMaven 1 Sec Professional Digital Meat Thermometer…" | **confirms PI-04** exactly (target and title) |
| https://link.amazon/B0f3GKalj | `https://www.amazon.com/` (generic homepage) | **differs** from PI-05's stored observation (`/dp/B0DZFD6R9Z`) — see note 1 |

**Note 1 (fetch-path instability, not a link verdict).** A direct control fetch
of `https://www.amazon.com/dp/B0CDY277D3` in the same session succeeded and
returned the stored PI-01 title and the `Air Fryers` breadcrumb
(leaf node 17659096011), so the fetch path was reaching Amazon detail pages.
An earlier session's reads on the same date (2026-11-19, recorded in
`data/sources.json` → `reverified_2026_11_19_6ace936d`) reproduced all five
detail-page landings. In this session, four of the five short links landed on
the generic homepage instead. The honest reading: the short links' observed
landing through this fetch path is **unstable on this date** — sometimes a
specific detail page (carrying `plpRedirect=mhFallback`), sometimes the
homepage. This neither confirms nor denies link validity, product identity or
Associates attribution, and no stored observation in `data/product-intent.json`
was changed. The site's existing stance (a null observation is not read in
either direction; the short links' compliance status stays unresolved at
Zone3 FLG-003) remains correct.

## C. Policy and legal sources, re-read live

| Source | URL | What was read back today | Verdict |
|---|---|---|---|
| S1 Operating Agreement | https://affiliate-program.amazon.com/help/operating/agreement | Heading "Associates Program Operating Agreement", "**Updated:** October 15, 2025"; §1: links "must properly use the special 'tagged' link formats we provide" and are called **Special Links** | confirms |
| S2 Program Policies | https://affiliate-program.amazon.com/help/operating/policies | "**Updated:** April 14, 2026."; Commission Income Statement, Participation Requirements, Products Statement, Mobile Application Policy, Trademark Guidelines, IP License sections present; session ends on the first of 24 hours / order / non-qualifying click-through | confirms |
| S8 FTC Disclosures 101 | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | Page dated **November 2019**; "Place it so it's **hard to miss**"; "The disclosure should be placed with the endorsement message itself"; "You can't talk about your experience with a product you haven't tried." | confirms |

## D. Product and brand sources, re-read live

| Source | URL | What was read back today | Verdict |
|---|---|---|---|
| S10 Chefman 6 Qt Dual-Window | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | Specifications block verbatim: "Capacity 6 Qt / 5.67 L"; "200–450°F / 95º-235ºC temperature range"; "Dimensions 13.38 in x 11.81 in x 10.63 in"; "Weight 13.3 lbs / 6.03 kg"; "Power 1700W/120V"; "Model Number RJ38-SQPF-3TDB-2W". Widget counter **1,312 reviews** | confirms every published spec row; widget count matches the `as_of: 2026-11-19` snapshot already in `data/products.json` |
| S12 Chefman 8 Qt TurboFry | https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1 | Specifications block verbatim: "Capacity 5 Qt or 8 Qt / 4.73 L or 7.57 L"; "200–400°F"; "(8 Qt Model) 15.4 in x 12.6 in x 13.5 in"; "Weight (8 Qt Model) 12.8 lbs / 5.8 kg"; "Model Number RJ38-SQSS-8T"; "Max temp: 400ºF/ 205ºC". Widget counter **719 reviews** | confirms every published spec row; widget count matches the `as_of: 2026-11-19` snapshot; **F3 stays live** — the brand page's 400 °F ceiling still conflicts with the 450 °F listing title, and the site publishes neither as corrected |
| S14 Emeril 26 QT French Door | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | Spec icons verbatim: "26-Quart Capacity"; "25 Cooking Pre-sets"; "16.9\"D x 15.8\"W x 14.8\"H"; "24.6 Liters"; "120 volts"; price $199.99; SKU 4-00675-02A-VN; body copy "10-in-1" still present; carousel asset `11-in-1_convection_oven_in_action.png` still present. Widget reads **2.6 (26)** on two separate fetches | confirms every published spec row; **F4/F5 preset conflict still live**; widget count **differs** from the stored 25-review value — repaired, see section E |
| S16 Amazon detail page (control) | https://www.amazon.com/dp/B0CDY277D3 | `<title>` "Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen"; breadcrumb `… › Fryers › Air Fryers` | confirms the stored PI-01 observed title and browse path |

Not re-read in this pass (nothing about them is restated as current):
S3–S7, S9, S11, S13, S15, S18–S27, S28–S47 beyond the structural link check.

Deliberately not used: prices, star ratings and "customers also viewed" items
visible on the live Amazon pages were seen and not recorded, per S2
participation requirements. No Associates Central, enrolled-link-test,
Search Console or campaign data exists in this pass; none is claimed.

## E. Structural audit of the published site (37 sitemap pages)

| Check | Result |
|---|---|
| Disclosure strip between masthead and `<main>` | **37/37** — `<div class="disclosure-bar">` with the exact S5 sentence, directly after `</header>`, before `<main>` |
| Footer disclosure repeated | **37/37** |
| Every `www.amazon.com` / `link.amazon` product anchor `rel="sponsored"` | **0 unqualified** across all 37 pages |
| Unique `<title>` | **37 unique** |
| Unique meta description | **37 unique** |
| `rel="canonical"` present | **37/37** |
| Sitemap URLs resolve to local files | **37/37**, none missing |
| Live GitHub Pages | API `status: built`, source `main` / `/`; main-branch CI runs green on 2026-11-19 |

The landing page reads as a publication front page (format chooser, sourced
product cards, buying-question modules), not an audit dashboard; the workspace
pages (decisions, questions, suggestions, flags, requirements, data) are
reachable from one native menu and the footer index. Question-shaped guides,
the Suggestions page (choose before implement), the Questions & information
gaps page, the Flagged for Review page and the executive summary are all in
the sitemap and reachable.

## F. Defect found and repaired

**E-1 (fixed): Emeril brand-site rating drifted and was unstamped.**
`data/products.json` → `products[emeril-26qt-french-door].reviews.brand_site_rating`
read `2.6 / 5 from 25 reviews` with no `as_of` and no history, while the two
Chefman rows carry `as_of: 2026-11-19` snapshots. The live widget reads
**2.6 (26)** (two independent fetches today). Repaired by the house convention:
`v` → `"2.6 / 5 from 26 reviews"`, `as_of` → `"2026-11-19"`, note rewritten as
a dated snapshot, and the previous 25-review value preserved in `history`.
Recorded reads through 2026-11-17 showed 25; nothing else on the row changed.
The dated test record in `data/reverification.json` (`observed_2026_11_14`,
"confirmed") is historical evidence and was deliberately left untouched, as
were the dated `page_version` reads in `data/sources.json`.

**E-2 (recorded, not changed): short-link landing instability on 2026-11-19.**
See note 1 in section B. Stored observations kept as dated records; the new
behaviour is recorded in `data/sources.json` → `reverified_2026_11_19_e9e5ab06`.

**E-3 (observed, left for owner decision): dead table in `build.py`.**
`commercial_table()` (line ~846) builds a "Commercial summary — prices and
ratings, honestly labelled" table (brand list price, "not displayed S2" for
Amazon price, brand-site rating, source links, flagged count) but is **never
called** — the table renders on no page. It is compliant-looking content that
the brief's "tables with sources" ask would benefit from, but publishing it is
an owner decision (it shows brand list prices and brand ratings), so it was
left as-is and flagged here rather than switched on unilaterally.

## G. Full gate suite, after the edits

| Gate | Result |
|---|---|
| `python3 build.py` | exit 0 — 37 sitemap URLs, 25 feed items |
| Deterministic rebuild | second run produced no git diff |
| `python3 verify.py` | 137 pages, 77 spec rows (75 verified, 2 blank+flagged), 47 sources, **0 errors**, 0 external warnings |
| `python3 -m unittest discover -s tests` | 68 tests OK |
| `bash scripts/ci-check.sh` | OK — data audit clean, build current, link check 11,804 links OK |
| `python3 research/check_research.py` | OK |
| `python3 scripts/verify_site.py` | ALL CHECKS PASSED — 393 assertions |

## H. Boundaries re-stated (not re-earned)

- Tracking ID **shopnow047c-20** stays recorded, unvalidated, unapplied; the
  operational associate tag stays blank.
- Intended-ASIN / official-listing / confirmation fields stay **null** and
  separate from the observed redirect fields on all five PI rows; no enrolled
  per-product Associates test has passed.
- Production analytics stays off (five-event contract tested only); the
  authorised first-party campaign ledger stays empty.
- No Search Console action; no product photography; no price, rating or
  conversion figures published from Amazon.
- The five supplied short links' compliance status stays unresolved at
  Zone3 FLG-003 — this pass declares nothing either way.
- Existing flags re-confirmed live and left open: **F3** (450 °F vs 400 °F),
  **F4/F5** (Emeril preset/in-1 four-way conflict), **F65/F69** (dimension
  disagreements), **F96** (extension-cord instruction conflict).

## I. Irregularities for the Flagged for Review page

None new beyond E-1 (fixed) and E-2/E-3 (recorded above). Nothing blocks the
merge: every irregularity is either repaired by dated record or published with
its source links for owner review.
