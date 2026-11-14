# Executive summary — Zone1 Amazon affiliate platform

**Prepared:** 2026-11-13 (UTC) · **Branch:** `arena/105bc29e-zone1` · **Live site:** https://kanlerxz87-cyber.github.io/Zone1/

---

## 1. What was asked for, and what this is

The brief asked for an AI-powered Amazon affiliate platform that automates product research, finds trending and high-converting products, analyses pricing, reviews, competition and commission potential, generates SEO content, publishes and manages affiliate links, tracks clicks and conversions, and optimises for revenue — all inside Amazon Associates policy.

It asked for that to be built around three supplied links, with no manual input, line-by-line verification against official sources, a GitHub Pages site, and a "Flagged for Review" page for anything unverified.

**What exists now:** a live, dependency-free static site of 13 pages generated from a verified JSON dataset, plus a platform blueprint, a compliance register of 16 quoted requirements, and a flagged list that every unresolved item is published on. Every asserted value carries a link to the official page it came from. Nothing is estimated.

## 2. The three products

All three short links were followed and each resolved to an Amazon ASIN.

| Supplied link | ASIN | Product (from the listing title) | Category |
|---|---|---|---|
| https://link.amazon/B04G1MEwY | **B0CDY277D3** | CHEFMAN 6 Quart Dual Basket Air Fryer Oven, Sync Finish, 2 × 3 qt baskets | Air fryer |
| https://link.amazon/B02NbDxp3 | **B09B7SB46R** | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | Air fryer oven |
| https://link.amazon/B00hJ57DV | **B08DKYBTPH** | Chefman Air Fryer 8 Qt, TurboFry 4-in-1, stainless steel | Air fryer |

Source: the Amazon detail pages themselves (S16) reached via the short links (S17).

The niche is therefore **home-kitchen air frying**, dictated by the product set rather than chosen.

## 3. Verification result

- **43 specification rows** across the three products.
- **40 verified** — each read on the manufacturer's own product page or owner's manual, each with a clickable source link.
- **3 blank and flagged** — no official source states the value, or official sources disagree.
- **18 sources**, all official: Amazon Associates documents, the US FTC and eCFR, three manufacturer owner's manuals, two manufacturer product pages, and the Amazon listings themselves. *(Correction 2026-11-14: the completed register in [`data/sources.json`](data/sources.json) now holds **22** official sources, S1–S22 — see §10.)*

Two rows were initially blank and were later **upgraded to verified** using the manufacturers' own owner's manuals rather than by guessing: the Chefman 6 Qt's per-basket capacity (the manual states "two 3-quart baskets") and the Emeril's preset count (the manual's preset chart names exactly 24). Two further rows, the 6 Qt's preset list and the 8 Qt's warranty, were added from the manuals. The blanks that remain are blanks because no official document answers them.
- **0 values inferred, estimated or back-filled.**

## 4. Findings

1. **The product data is verifiable — and was verified.** Every asserted specification traces to a manufacturer document, not a retailer listing or a review blog.
2. **One official source contradicts another, materially.** The Chefman 8 Qt listing advertises a **450 °F Hi-Fry** mode and bake/dehydrate/frozen functions; the brand page and the RJ38-SQSS-8T manual document **200–400 °F** with four food-type presets. Both are quoted; neither is asserted. Flagged as F3.
3. **The Emeril page contradicts itself on preset count — and the manual settles it.** The brand page says "25 Cooking Pre-sets" in its spec block and "24 one-touch cooking presets" in its description; the Amazon title says 24. The owner's manual's preset chart names exactly **24** presets, so 24 is the documented figure and the page's "25" is treated as a marketing error. Still flagged as F4/F5 so the discrepancy is on the record.
4. **ASIN → model number is not published by Amazon.** Each product's model is a capacity/finish match with a caveat, not a confirmation. Flagged as F1/F2.
5. **Commission rate per product cannot honestly be stated.** Amazon publishes rates by *category* (Kitchen 4.50%, Home 3.00%, fallback 4.00%) and does not publish which category an ASIN sits in. Competitor sites that quote a single per-product figure are guessing. Candidate rows are shown; the rate is blank.
6. **No Amazon price or star rating appears anywhere on the site — deliberately.** Program Policies §2(b) restrict price/availability display to Amazon-served links or the official API; §3(t) restricts customer reviews and star ratings the same way. This is the compliant state, not an omission.
7. **The policy constraint is the architecture.** The IP License §2(e) forbids aggregating, analysing, extracting or repurposing Program Content and forbids training models on it. An "AI product research" engine therefore has to run on manufacturer documentation and first-party click/conversion data — which is how the blueprint is designed.

## 5. Economics, with the precision the data allows

Arithmetic on two published inputs only — brand list price and an official rate row. Not a forecast.

| Product | Brand list price | @ Kitchen 4.50% | @ Home 3.00% | @ fallback 4.00% |
|---|---|---|---|---|
| Chefman 6 Qt Dual | $119.99 | $5.40 | $3.60 | $4.80 |
| Emeril 26 QT | $199.99 | $9.00 | $6.00 | $8.00 |
| Chefman 8 Qt | $119.99 | $5.40 | $3.60 | $4.80 |

Amazon computes commission on *Qualifying Revenue* — after shipping, gift wrap, handling, tax, service charges, credits, rebates, card fees and bad debt — so real payouts are lower. The variable that decides the outcome, conversion rate, is measurable only by the operator.

## 6. Recommendation

1. **Publish this build** — it carries the substance (buying guide, comparison, three reviews, dataset, platform and compliance documentation) that a manual review looks for.
2. **Clear the flags that change copy first:** F3 (450 °F conflict), F4/F5 (preset counts), F1/F2 (model mapping).
3. **Fix attribution before driving traffic:** confirm the Associates tag inside the short links and create per-placement sub-tags (F6, F7).
4. **Then apply**, and work the **180-day / three qualifying sales** window deliberately — publication first, application second.
5. **Pursue price and rating display only if Creators/PA API access is granted.**

## 7. Compliance posture

| Requirement | Status |
|---|---|
| "As an Amazon Associate I earn from qualifying purchases." on every page | Generated into the layout; a build fails without it |
| Clear + conspicuous link-level disclosure | "Paid link" badge on every outbound button |
| No Amazon price / availability without API | Enforced by absence — no template slot exists |
| No Amazon reviews or star ratings without API | Enforced by absence |
| No price tracking or alerts | Feature excluded by design |
| No Amazon Marks in paid search | Guardrail G1 with a negative-keyword list |
| No Program Content in analytics or model training | Guardrail G6, enforced at the data contract |
| Sub-tags never per-user | Guardrail G5, static per-page map |
| No experience claims | No testing is claimed anywhere; copy says so explicitly |

## 8. Sources

All sources are listed with what each one verifies in [`data/sources.json`](data/sources.json) and rendered with links on the live **Full dataset** and **Compliance** pages.

Primary documents:

- Amazon Associates Operating Agreement — https://affiliate-program.amazon.com/help/operating/agreement
- Amazon Associates Program Policies — https://affiliate-program.amazon.com/help/operating/policies
- Standard Commission Income Statement (rate table) — https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ
- Application Review Process — https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM
- Associate identification / disclosure — https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98
- Tracking IDs — https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA
- FTC Endorsement Guides Q&A — https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- FTC Disclosures 101 — https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
- 16 CFR Part 255 — https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255
- Chefman 6 Qt Dual-Window — https://chefman.com/products/turbofry-touch-dual-window-air-fryer
- Chefman 6 Qt Dual-Basket (sister SKU) — https://chefman.com/products/turbofry-touch-6-qt-dual-basket-air-fryer
- Chefman 8 Qt TurboFry Touch — https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1
- Chefman RJ38-SQSS-8T owner's manual (PDF) — https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQSS-8T-UG-US.pdf
- Emeril French Door AirFryer 360 26 QT — https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360
- Emeril FAFO-001 owner's manual (PDF) — https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf

## 9. Limitations, stated plainly

- No unit was tested, handled or owned. Nothing on the site claims otherwise.
- Amazon prices, star ratings and review counts are unavailable to this project and are not displayed.
- Category assignment per ASIN is unknown, so per-product commission rates are blank.
- Competition metrics (result counts, Best Sellers Rank) are not published as stable quotable facts and were not scraped, because aggregation of Program Content is prohibited.
- Every unresolved item needs a human decision; they are all listed at [`flagged.html`](flagged.html) and in [`COORDINATION.md`](COORDINATION.md).

---

## 10. Integration update — 2026-11-14 (session `sess-cb2cfa7c`, branch `arena/cb2cfa7c-zone1`)

A fifth agent session performed an independent line-by-line review of the merged repository and re-verified the critical published facts against the live official pages on **2026-11-14**. Summary of results:

### 10.1 Re-verification — everything critical re-checked live, everything holds

| Claim re-checked | Official source re-fetched 2026-11-14 | Result |
|---|---|---|
| All 11 commission-table rows (10% → 0%) | [Standard Commission Income Statement](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) | Exact match |
| Short link #1 → ASIN **B0CDY277D3**, Chefman 6 Qt title | [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY) | Exact match |
| Short link #2 → ASIN **B09B7SB46R**, Emeril 26QT title | [link.amazon/B02NbDxp3](https://link.amazon/B02NbDxp3) | Exact match |
| Short link #3 → ASIN **B08DKYBTPH**, Chefman 8 Qt title | [link.amazon/B00hJ57DV](https://link.amazon/B00hJ57DV) | Exact match |
| §2(b) prices, §3(t) reviews, §3(y) price-tracking, §3(e) cookies, §6(a) alteration, ML-training ban | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) (updated 2026-04-14) | All quotes verbatim |
| 3 qualifying sales / 180 days · 10 posts · 60-day recency · 500 followers | [Application Review Process](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) | Exact match |
| OA §5 disclosure wording + "Clear/Conspicuous" link rules | [Associate identification help](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) | Exact match |
| FTC placement rules | [Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | Exact match |
| Chefman 6 Qt: RJ38-SQPF-3TDB-2W, $119.99 list, 450 °F Hi-Fry | [chefman.com](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | Exact match |
| Chefman 8 Qt: RJ38-SQSS-8T, $119.99 list, 200–400 °F, 4 food presets | [chefman.com](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) | Exact match (conflict with Amazon listing confirmed real, still flagged) |
| Emeril: $199.99, 2.6★/25, SKU 4-00675-02A-VN, "25 Cooking Pre-sets", "10-in-1" | [emerileveryday.com](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | Exact match (internal brand-page conflict confirmed real, still flagged) |

Only routine drift was found: brand-widget review counts moved 1,302→1,305 and 715→716 since the 2026-11-13 capture. The published figures remain date-stamped quotes (flag **F17**).

### 10.2 New finding: PA-API 5 is officially deprecated (flag **F14**)

The official PA-API 5 documentation URL now serves a **deprecation notice**: PA-API 5 "has been deprecated and is being replaced by the **Creators API**"; PA-API 5 calls return `403 AccessDeniedException` with a migration message ([official notice](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation), verified live 2026-11-14; added to the register as **S22**).

This settles a disagreement between earlier sessions in favour of the cross-check's original F18 claim: the platform blueprint's automation features must target the **Creators API**. The compliance quotes (which read "Creators API or PA API") are unaffected.

### 10.3 Citation-quality fixes in the dashboard annex (flag **F15**)

Some rows in the separately-built `dashboard/` annex cited third-party sites (barcode.graphics, keywordseverywhere.com, manuals.plus, aruljohn.com, u2l.ai) instead of official sources. Where an official source exists it has been added — Amazon's own [KDP Help G200652190](https://kdp.amazon.com/en_US/help/topic/G200652190) ("your 10-character Amazon Standard Identification Number"; canonical `amazon.com/dp/ASIN` format), verified live and added as **S21**. Where no official source exists (the short-domain list), the row is now explicitly marked **unverified**. No original claim was deleted.

### 10.4 Preserved disagreements (flag **F16**)

The dashboard annex reads the `link.amazon` redirects as a missing-page fallback to random listings. Four independent observation rounds on 2026-11-13 and 2026-11-14 (two sessions, repeat fetches) instead returned the same three destinations every time, with listing titles matching the recorded products exactly. Both positions are published; the account holder can settle it by opening the three links while signed in.

### 10.5 Stale PR #9 disposition

Session `arena/88769516-zone1` (PR #9, idle since 2026-11-13T22:47Z) built an independent complete site. Merging it would overwrite the integrated root site, so — per the "never discard another session's work" rule — all 16 of its files are preserved verbatim at [`annex-88769516/`](annex-88769516/README.md) (plus the untouched branch), PR #9 is closed with a pointer to the annex, and its disagreements with the integrated dataset are recorded in §10.4 and on the Flagged page.

### 10.6 State after this pass

- **22 sources** (S1–S22), all official; **43 spec rows** (40 verified, 3 blank+flagged); **17 open flags** (13 programme + 4 product), all published on [`flagged.html`](flagged.html).
- `build.py` + `verify.py` gates pass: 91 pages checked, **0 errors**, 0 broken internal links, 0 missing disclosures, 0 unsourced values, 0 leaked Amazon prices/ratings.
