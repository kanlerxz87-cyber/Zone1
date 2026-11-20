# VER-2026-11-20 — independent review, live re-verification and integration

**Date:** 2026-11-20 UTC
**Session branch:** `arena/1875c5bb-zone1` (base `main` @ `1c7de825`, merge of PR #185)
**Status:** complete — every gate run from a clean tree passed before and after the one
data repair described below.

## Executive finding

The repository's published site is structurally sound and its stored facts survived an
independent live re-read. Nothing was found that required a product, price, rating,
commission, ledger or compliance change.

Three things were established by measurement rather than assumed:

1. **All five supplied `link.amazon` short links resolved today**, each to a product detail
   page whose ASIN matches the record already stored. The exact URLs read were
   `link.amazon/B04G1MEwY` → `/dp/B0CDY277D3`, `B02NbDxp3` → `/dp/B09B7SB46R`,
   `B00hJ57DV` → `/dp/B08DKYBTPH`, `B0c8moW59` → `/dp/B0DHZTCNR5`, and
   `B0f3GKalj` → `/dp/B0DZFD6R9Z`. Reaching a product page is **not** evidence of the
   account holder's intent, of Associates attribution, or of compliance status in either
   direction, and no such claim is made.
2. **One real register inconsistency was found and repaired.** The canonical record
   `data/product-intent.json` carried a PI-04 landing title that agreed with neither the
   2026-11-19 record in `data/sources.json` nor today's live read. The row now carries
   today's read; the superseded wording is preserved in its observation history. Unchanged
   are all intent fields (`intended_asin`, `official_listing_url`, `confirmation_date`,
   `confirmation_source` are still `null`), `associates_link_test_passed` (still `false`)
   and the tracking ID (still recorded, still unapplied).
3. **Two automated audit hits were investigated and found to be intentional.** The
   404 page has no canonical (correct for an error page; it carries `noindex`), and the
   eight unqualified `link.amazon/ZZZ9ZZZZZ` anchors are the negative-control probe
   (`S22`), which `build.py` deliberately excludes from product-link qualification with a
   written comment. Neither was "fixed", because changing them would have contradicted a
   documented decision rather than a defect.

A deliberate non-change is also recorded: the Chefman 6 Qt review widget displayed
**1,313 reviews** today, while the published figure is a stamped *2026-11-19* snapshot of
4.6 / 5 from 1,312. The average was not rendered in the text this session read, so the
stamped value was **not** updated — writing "4.6 from 1,313" would have inferred a number
that was not observed.

## Official primary evidence read in this session

Each URL below was fetched live during this pass; every quoted phrase is from the live
response body, not from memory or an earlier session's note.

| Source | Link | What was actually read | Consequence |
|---|---|---|---|
| S1 Operating Agreement | [affiliate-program.amazon.com/help/operating/agreement](https://affiliate-program.amazon.com/help/operating/agreement) | Heading "Updated: October 15, 2025"; §1 requires that links "properly use the special 'tagged' link formats we provide". | Version date unchanged. No tag applied to any link. |
| S2 Program Policies | [affiliate-program.amazon.com/help/operating/policies](https://affiliate-program.amazon.com/help/operating/policies) | Heading "Updated: April 14, 2026"; qualifying-purchase wording (24-hour session, 89-day cart window, 180-day ship/pay). | Version date unchanged; no commission or revenue figure published. |
| S5 Associate identification | [help/node/topic/GHQNZAU6669EZS98](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) | Requires the statement "As an Amazon Associate I earn from qualifying purchases." clearly and conspicuously; link-level disclosure must be clear and "placed near any affiliate link or product review". | Site strip below masthead, footer repeat and per-CTA "Paid link" note all satisfy the described placement. |
| S8 FTC Disclosures 101 | [ftc.gov/…/disclosures-101-social-media-influencers](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | Stamped "November 2019"; "Place it so it's hard to miss"; "You can't talk about your experience with a product you haven't tried"; "advertisement", "ad", "sponsored" acceptable. | Basis for the no-hands-on-testing position; unchanged. |
| S10 Chefman 6 Qt Dual-Window | [chefman.com/products/turbofry-touch-dual-window-air-fryer](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | Model `RJ38-SQPF-3TDB-2W`; "Max temp: 450ºF/ 235ºC with Hi-Fry function"; two baskets in one unit with Sync Finish. | Matches the published 200–450 °F range and 450 °F Hi-Fry maximum. Review count noted above. |
| S14 Emeril French Door 26 QT | [emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | Spec block: 26-Quart, "25 Cooking Pre-sets", 16.9"D × 15.8"W × 14.8"H, 24.6 liters, 120 V, model `4-00675-02A-VN`; description "10-in-1"; widget "2.6 (26)". | Published dimensions, capacity and the 25-vs-24 preset conflict all reconfirmed; 2.6 / 26 corroborated. |
| S17, S28, S29, S36, S37 | the five tokens and `/dp/B09B7SB46R`, `/dp/B08DKYBTPH`, `/dp/B0DHZTCNR5`, `/dp/B0DZFD6R9Z` | Landing ASIN and `<title>` for each of the five supplied links. | Recorded as dated observations; see item 1 above. |

**Not read this session:** S3, S4, S6, S7, S9, S11–S13, S15, S18–S27, S30–S35 and S38–S49.
No statement is made in this report about their current content. This is a scoped re-read
of 12 sources, not a claim to have re-read all 49.

## Repository review — measured, not asserted

Run from a clean tree with no uncommitted generated output:

| Check | Command | Result |
|---|---|---|
| Generator | `python3 build.py` | exit 0; 41 sitemap URLs; 26 feed items; second run byte-identical (reproducible) |
| Row/source coverage gate | `python3 verify.py` | 141 pages, 77 spec rows (75 verified, 2 blank + flagged), 49 sources, 0 external warnings, **0 errors** |
| Unit tests | `python3 -m unittest discover -s tests` | 75 tests, OK |
| Link + compliance CI | `bash scripts/ci-check.sh` | 12,674 links OK; data audit clean |
| Research tree | `python3 research/check_research.py` | OK — no broken links, no unsourced rows, disclosures on every page |
| Annex verifier | `python3 scripts/verify_site.py` | 393 assertions, all passed |
| Client/collector contract | `node --test tests/*.test.cjs` | 14 pass, 0 fail |

Structural audit executed independently of the generator's own tests, over all 63 root
HTML files:

- **Unique page titles:** every root page has a distinct `<title>`; zero duplicates.
- **Disclosure:** every root page carries the exact Associate statement; 0 pages without it.
- **Product-link qualification:** the only Amazon-hosted anchors without
  `rel="sponsored nofollow noopener"` are the eight negative-control citations explained
  above; **zero** actual product destinations are unqualified.
- **Sitemap hygiene:** 41 URLs, 0 duplicates, 0 `lastmod` dates in the future.
- **Feed hygiene:** 26 items, 0 publication dates in the future.
- **404 handling:** `noindex` present; no self-referential canonical (appropriate).
- **Robots/sitemap/feed regeneration:** deterministic across two consecutive builds.

## Irregularities and open items

| ID | Item | Status this pass |
|---|---|---|
| F106 | PI-03 (`B00hJ57DV`) landed on the Amazon site homepage on 2026-11-19 in another session's read. | **Not reproduced.** Today it reached `/dp/B08DKYBTPH` again. Recorded as a dated observation; the earlier observation is retained, not overwritten. Still open as an instability, not as a validity claim. |
| — | PI-04 landing title wording differs from the canonical row. | **Repaired** (see item 2). Superseded wording preserved. |
| — | 6 Qt review count moved 1,312 → 1,313; average unreadable. | **Recorded, deliberately not changed.** Stamped snapshot stands. |
| E-3 | `commercial_table()` in `build.py` is dead code (raised by an earlier pass). | **Still dead.** Left for the owner; not switched on. |
| DR-01…DR-03 | Intended ASIN per link; tracking-ID validation; 180-day qualifying-sales decision. | **Still blocked on the account holder.** No agent can complete these. |
| DR-04 | Enable the analytics collector. | **Still off.** No endpoint, runtime or privacy approval exists. |

## What this pass did not and cannot establish

- No Associates account, credential or authorised report was available, so **no click,
  order, conversion, revenue or commission figure** is published or implied here.
- No Search Console ownership, so **no impression, ranking or traffic** claim is made.
- No production runtime exists for the analytics collector, so it remains disabled.
- No browser binary could be downloaded in this environment, so **no rendered screenshot
  or visual-regression check** was performed; layout conclusions are from source only.
- Absence of a visible tracking parameter on a short link proves **neither** successful nor
  failed attribution. The compliance status of the five supplied short links remains
  unresolved, and this report does not declare them invalid.

## Artefacts changed

- `data/product-intent.json` — dated 2026-11-20 observation fields for the five rows, one
  superseded title preserved in history, new `observation_2026_11_20` block, `reviewed_on`.
- `data/sources.json` — new scoped record `reverified_2026_11_20_1875c5bb` (what was read,
  what was observed, what was **not** read).
- `reports/verification-2026-11-20-1875c5bb.md` — this report.
- `EXECUTIVE-SUMMARY.md` — dated appendix.
- `COORDINATION.md` — claim, completion record and release receipt.
- Regenerated root HTML (dates only; product, price and rating values unchanged).
