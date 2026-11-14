# Executive summary — Zone1 Amazon affiliate platform

**Prepared:** 2026-11-13 (UTC) · **Branch:** `arena/105bc29e-zone1` · **Live site:** https://kanlerxz87-cyber.github.io/Zone1/

---

## 1. What was asked for, and what this is

The brief asked for an AI-powered Amazon affiliate platform that automates product research, finds trending and high-converting products, analyses pricing, reviews, competition and commission potential, generates SEO content, publishes and manages affiliate links, tracks clicks and conversions, and optimises for revenue — all inside Amazon Associates policy.

It asked for that to be built around three supplied links, with no manual input, line-by-line verification against official sources, a GitHub Pages site, and a "Flagged for Review" page for anything unverified.

**What exists now:** a live, dependency-free static site of **23 pages** generated from a verified JSON dataset — the dashboard and verification set, plus a **7-article editorial layer** — with a platform blueprint, a compliance register, and a flagged list that every unresolved item is published on. Every asserted value carries a link to the official page it came from. Nothing is estimated. *(Page count corrected 2026-11-14 at integration pass 7: the long-standing "13 pages" figure was stale by several passes; the root build is now 23 pages and `verify.py` checks 101 HTML files across the repo.)*

## 2. The three products

**Product identity is not confirmed** (corrected 2026-11-14, F14–F16). Each supplied short link was followed;
each fetch observed a landing on an air-fryer listing, but the token-to-ASIN mapping is unverified: the bare
9-character codes return "Page Not Found" on `amazon.com/dp/`, and both the short links and the plain ASIN URLs
served Amazon's fallback-parameter form on 2026-11-14. Evidence: [`reports/link-check-2026-11-14.md`](reports/link-check-2026-11-14.md).

| Supplied link | Candidate ASIN (unconfirmed) | Observed listing title | Category (provisional) |
|---|---|---|---|
| https://link.amazon/B04G1MEwY | **B0CDY277D3** | CHEFMAN 6 Quart Dual Basket Air Fryer Oven, Sync Finish, 2 × 3 qt baskets | Air fryer |
| https://link.amazon/B02NbDxp3 | **B09B7SB46R** | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | Air fryer oven |
| https://link.amazon/B00hJ57DV | **B08DKYBTPH** | Chefman Air Fryer 8 Qt, TurboFry 4-in-1, stainless steel | Air fryer |

Sources: Amazon detail pages (S16) and the supplied short links (S17); link-check report 2026-11-14.
Confirm each intended product from a logged-in browser before treating any candidate ASIN as final.

The observed listings are all **home-kitchen air frying**, so that remains the working niche — dictated by
the product set rather than chosen — but the niche claim rests on the observed titles, not on a confirmed
identity mapping.

## 3. Verification result

- **43 specification rows** across the three products.
- **41 verified** — each read on the manufacturer's own product page or owner's manual, each with a
  clickable source link. *(Count corrected 2026-11-14 by two independent passes to match `verify.py`; then
  corrected again on 2026-11-14 by pass 7 (sess-7111e2b6) to **41 verified / 2 blank+flagged**, after one
  more published value was blanked because the official source cited for it does not state it — see §11.)*
- **2 blank and flagged**:
  - the Chefman 8 Qt's *Hi-Fry / 450 °F mode* row. Two official sources contradict
    each other (the Amazon listing advertises 450 °F Hi-Fry; the brand page and the RJ38-SQSS-8T manual
    document 200–400 °F), so no value is asserted.
  - the Chefman 6 Qt's *Number of presets* row, blanked by pass 7 on 2026-11-14: the value that was
    published cited the RJ38-SQPF-3TDB-2W owner's manual, and that guide was re-read end to end and
    **contains no preset chart and names no food presets**. The four presets published for the *8 Qt*
    model belong to a different appliance and were not carried across. Blanked and flagged as **F36**.
  Verified 41 / blank 2 against `data/products.json` on 2026-11-14.
- **24 sources**, all official: Amazon Associates documents, the US FTC and eCFR, three manufacturer owner's manuals, two manufacturer product pages, and the Amazon listings themselves. *(Correction 2026-11-14: the completed register in [`data/sources.json`](data/sources.json) now holds **24** official sources, S1–S24 — see §10.)*

Two rows were initially blank and were later **upgraded to verified** using the manufacturers' own owner's manuals rather than by guessing: the Chefman 6 Qt's per-basket capacity (the manual states "two 3-quart baskets") and the Emeril's preset count (the manual's preset chart names exactly 24). Two further rows, the 6 Qt's preset list and the 8 Qt's warranty, were added from the manuals. The blank that remains is blank because no official source resolves it — the 8 Qt's Hi-Fry/450 °F row, where official sources disagree. *(2026-11-14 pass 6: count corrected to the single remaining blank.)*
- **0 values inferred, estimated or back-filled.**

## 4. Findings

1. **The product data is verifiable — and was verified.** Every asserted specification traces to a manufacturer document, not a retailer listing or a review blog.
2. **One official source contradicts another, materially.** The Chefman 8 Qt listing advertises a **450 °F Hi-Fry** mode and bake/dehydrate/frozen functions; the brand page and the RJ38-SQSS-8T manual document **200–400 °F** with four food-type presets. Both are quoted; neither is asserted. Flagged as F3.
3. **The Emeril page contradicts itself on preset count — and the manual settles it.** The brand page says "25 Cooking Pre-sets" in its spec block and "24 one-touch cooking presets" in its description; the Amazon title says 24. The owner's manual's preset chart names exactly **24** presets, so 24 is the documented figure and the page's "25" is treated as a marketing error. Still flagged as F4/F5 so the discrepancy is on the record.
4. **ASIN → model number is not published by Amazon.** Each product's model is a capacity/finish match with a caveat, not a confirmation. Flagged as F1/F2.
5. **Commission rate per product cannot honestly be stated.** Amazon publishes rates by *category* (Kitchen 4.50%, Home 3.00%, fallback 4.00%) and does not publish which category an ASIN sits in. Competitor sites that quote a single per-product figure are guessing. Candidate rows are shown; the rate is blank.
6. **No Amazon price or star rating appears anywhere on the site — deliberately.** Program Policies §2(b) restrict price/availability display to Amazon-served links or the official API; §6(t) restricts customer reviews and star ratings the same way. This is the compliant state, not an omission.
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
| §2(b) prices, §6(t) reviews, §6(y) price-tracking, §3(e) cookies, §6(a) alteration, ML-training ban | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) (updated 2026-04-14) | All quotes verbatim |
| 3 qualifying sales / 180 days · 10 posts · 60-day recency · 500 followers | [Application Review Process](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) | Exact match |
| OA §5 disclosure wording + "Clear/Conspicuous" link rules | [Associate identification help](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) | Exact match |
| FTC placement rules | [Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | Exact match |
| Chefman 6 Qt: RJ38-SQPF-3TDB-2W, $119.99 list, 450 °F Hi-Fry | [chefman.com](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | Exact match |
| Chefman 8 Qt: RJ38-SQSS-8T, $119.99 list, 200–400 °F, 4 food presets | [chefman.com](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) | Exact match (conflict with Amazon listing confirmed real, still flagged) |
| Emeril: $199.99, 2.6★/25, SKU 4-00675-02A-VN, "25 Cooking Pre-sets", "10-in-1" | [emerileveryday.com](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | Exact match (internal brand-page conflict confirmed real, still flagged) |

Only routine drift was found: brand-widget review counts moved 1,302→1,305 and 715→716 since the 2026-11-13 capture. The published figures remain date-stamped quotes (flag **F17**).

### 10.2 New finding: PA-API 5 is officially deprecated (flag **F14**)

The official PA-API 5 documentation URL now serves a **deprecation notice**: PA-API 5 "has been deprecated and is being replaced by the **Creators API**"; PA-API 5 calls return `403 AccessDeniedException` with a migration message ([official notice](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation), verified live 2026-11-14; added to the register as **S24**).

This settles a disagreement between earlier sessions in favour of the cross-check's original F18 claim: the platform blueprint's automation features must target the **Creators API**. The compliance quotes (which read "Creators API or PA API") are unaffected.

### 10.3 Citation-quality fixes in the dashboard annex (flag **F15**)

Some rows in the separately-built `dashboard/` annex cited third-party sites (barcode.graphics, keywordseverywhere.com, manuals.plus, aruljohn.com, u2l.ai) instead of official sources. Where an official source exists it has been added — Amazon's own [KDP Help G200652190](https://kdp.amazon.com/en_US/help/topic/G200652190) ("your 10-character Amazon Standard Identification Number"; canonical `amazon.com/dp/ASIN` format), verified live and added as **S23**. Where no official source exists (the short-domain list), the row is now explicitly marked **unverified**. No original claim was deleted.

### 10.4 Preserved disagreements (flag **F16**)

The dashboard annex reads the `link.amazon` redirects as a missing-page fallback to random listings. Four independent observation rounds on 2026-11-13 and 2026-11-14 (two sessions, repeat fetches) instead returned the same three destinations every time, with listing titles matching the recorded products exactly. Both positions are published; the account holder can settle it by opening the three links while signed in.

### 10.5 Stale PR #9 disposition

Session `arena/88769516-zone1` (PR #9, idle since 2026-11-13T22:47Z) built an independent complete site. Merging it would overwrite the integrated root site, so — per the "never discard another session's work" rule — all 16 of its files are preserved verbatim at [`annex-88769516/`](annex-88769516/README.md) (plus the untouched branch), PR #9 is closed with a pointer to the annex, and its disagreements with the integrated dataset are recorded in §10.4 and on the Flagged page.

### 10.6 State after this pass

<<<<<<< HEAD
- **27 sources** (S1–S27), all official; **43 spec rows** (**41 verified, 2 blank+flagged** —
  *corrected 2026-11-14 by pass 7 (sess-7111e2b6); that pass blanked the Chefman 6 Qt preset count,
  which its cited source does not state (F30), and re-sourced the Emeril interior light to the
  owner's manual (F37)*);
  **38 open flag rows** (34 programme + 4 product), all published on [`flagged.html`](flagged.html).
=======
- **27 sources** (S1–S27), all official; **43 spec rows** (**42 verified, 1 blank+flagged**);
  **36 open flag rows** (32 programme + 4 product), all published on [`flagged.html`](flagged.html).
>>>>>>> 5b6309f (pass 7 (sess-ce4070ad): renumber flag F32->F36 after PR #46 took F32; rebase onto 9d7d64d (keeps articles layer, F32-F35, S25-S27); counts corrected to 36 open rows (32 programme + 4 product))
  *Counting note (corrected 2026-11-14; two independent passes converged on the spec-row split and this
  line is their merge).* The register holds 7 product-level flag instances, but three of them are the same
  cross-product item — **F6**, the unobservable Associates tag — raised once per product. `build.py`'s
  `page_flagged()` renders F6 once at programme level and suppresses the three per-product copies, so the
<<<<<<< HEAD
  page shows 34 + 4 = **38** distinct rows, not 41.
=======
  page shows 32 + 4 = **36** distinct rows, not 39.
>>>>>>> 5b6309f (pass 7 (sess-ce4070ad): renumber flag F32->F36 after PR #46 took F32; rebase onto 9d7d64d (keeps articles layer, F32-F35, S25-S27); counts corrected to 36 open rows (32 programme + 4 product))
  *History of this line:* it originally read **40 verified / 3 blank** and **17 open flags (13 programme +
  4 product)**. Two rows were filled from the manufacturers' own owner's manuals, leaving the Chefman 8 Qt's
  *Hi-Fry / 450 °F mode* as the only blank (F3). The flag count then rose as F18–F27 were added by later
  passes,
  **F28** by sess-91d0552e (PR #36), **F29–F31** by pass 6 (sess-54c66535), **F32–F35** by
<<<<<<< HEAD
  `arena/6b2eddeb` (PR #46), **F36** by pass 7 (sess-ce4070ad) — F36 records that the short links'
  `srctok` marker changes between sessions and on cache-busted repeats, contradicting F10's "stays
  constant" wording (renumbered from F32 after PR #46 took that ID) — and **F37** by sess-7111e2b6
  (PR #51).
- `build.py` + `verify.py` gates pass: PAGES pages checked, **0 errors**, 0 broken internal links,
=======
  `arena/6b2eddeb` (PR #46), and **F36** by pass 7 (sess-ce4070ad) — F36 records that the short links'
  `srctok` marker changes between sessions and on cache-busted repeats, contradicting F10's "stays
  constant" wording (see `flagged.html`; F36 was logged as F32 and renumbered because PR #46 took that ID
  first).
- `build.py` + `verify.py` gates pass: 92 pages checked, **0 errors**, 0 broken internal links,
>>>>>>> 5b6309f (pass 7 (sess-ce4070ad): renumber flag F32->F36 after PR #46 took F32; rebase onto 9d7d64d (keeps articles layer, F32-F35, S25-S27); counts corrected to 36 open rows (32 programme + 4 product))
  0 missing disclosures, 0 unsourced values, 0 leaked Amazon prices/ratings.
  *(92 pages before pass 7 added the Articles section on 2026-11-14.)*

### 10.7 Pass 6 (sess-54c66535, 2026-11-14) — the nine rows nobody had re-checked

The 2026-11-14 re-verification ledger published 61 rows and, honestly, left **9 marked
*not re-checked***. Pass 6 re-opened all nine against the official page or owner's manual the site
cites for each. Raw observations: [`session-54c66535/EVIDENCE-2026-11-14.md`](session-54c66535/EVIDENCE-2026-11-14.md);
machine-readable: [`session-54c66535/pass6.json`](session-54c66535/pass6.json).

**Seven confirmed verbatim**

| Claim | Value | Official source |
|---|---|---|
| Emeril rated power | 1700 W | FAFO-001 manual, *Appliance Specifications*: `Supply Power 120 V/1700 W/60 Hz \| Rated Power 1700 W` |
| Emeril temperature range | 75–500 °F / 25–260 °C | Same table |
| Emeril warranty | 1 year | Brand page: "1-Years Warranty" |
| Chefman 8 Qt preset defaults | All five rows | RJ38-SQSS-8T manual *PRESET FUNCTION CHART* — including the **Fries 20 min / 400 °F** row the earlier pass could not read |
| Chefman 8 Qt shake reminder | LED shake reminder | Brand page + manual ("the SHAKE light … will turn on") |
| Chefman 8 Qt household size / oil claim | 4–6 people; "98% less oil" | Brand page verbatim |

**Two not stated by their cited source — left blank, not guessed (flag F30)**

- *Chefman 6 Qt preset count.* The RJ38-SQPF-3TDB-2W guide was read end to end. It documents HI-FRY,
  +2 MIN, MUTE, SYNC BASKETS, SYNC FINISH, START/STOP, TIME/TEMP and SHAKE and refers to "a preset
  function", but it has **no preset chart** and never names four food presets; its control panel is
  artwork with no text layer. Contrast the 8 Qt guide, which does carry an explicit chart.
- *Emeril interior light.* The brand page's specification block lists Timer, 26-Quart Capacity,
  Dual-Speed Fan, 25 Cooking Pre-sets, dimensions, 24.6 Liters, Temperature Control and 120 volts —
  with no interior-light row.

**Two new pieces of evidence on existing flags**

- **F29 — the Emeril preset count is now stated five ways.** Amazon's listing title for B09B7SB46R
  says "**24 cooking functions**" and Emeril's own description says "Equipped with **24** one-touch
  cooking presets", while the same page's spec block says "25 Cooking Pre-sets", its heading says
  "10-In-1" and a carousel asset is named "11-in-1". Two independent official sources now agreeing
  on 24 is genuinely new — earlier passes had no tiebreaker. The conflict is **narrowed, not
  closed**, so no preset count is asserted anywhere on the site.
- **F31 — the Chefman 6 Qt sister SKUs diverge sharply.** On the brand's own site the dual-basket
  page (RJ38-SQPF-3TDB-2) shows 4.6 ★ from **194** reviews while the dual-window page
  (RJ38-SQPF-3TDB-2W) shows 4.6 ★ from **1,305**, on an identical price ladder. A useful signal for
  the open ASIN→model question (F2), but a signal, not an identification.

**Link resolution, fifth round.** All three supplied short links were re-fetched and returned the
same three destinations (B0CDY277D3, B09B7SB46R, B08DKYBTPH) with titles matching the stored values
character for character. Five sessions across two days now agree on the **destination**; the
**identity** of the intended product and the Associates tag remain unconfirmed (F10, F14–F16, F21).

---

## 11. Integration pass 7 — session `sess-7111e2b6` (2026-11-14)

**Branch:** `arena/7111e2b6-zone1` (base `main` @ `b990352`) · **Claim:** V1–V6, pushed before any file edit.
**Full record:** [`reports/verification-7111e2b6-2026-11-14.md`](reports/verification-7111e2b6-2026-11-14.md).

This pass did three things: it re-read the published facts against the official sources the site cites for
them, it applied the brief's verification rule to anything that failed, and it closed the two gaps the
board still had open against the brief — the row-source rule and the marketing-article requirement.

### 11.1 One published value did not survive the re-read

The brief's verification rule is explicit: *"If a value can't be confirmed from an official source, leave it
blank and flag it as unverified. Never infer or fill in values."* One published value did not survive.

The **Chefman 6 Qt's "Number of presets"** row read *"Four one-touch food presets: French fries, chicken,
meat, fish"*, cited to the model's own owner's manual
([RJ38-SQPF-3TDB-2W](https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQPF-3TDB-2W-UG-US.pdf)).
That guide was re-read end to end in this pass: it refers once to "a preset function", it has **no preset
chart**, and it **names no food preset**. The brand page's feature list does not mention presets either.

The four names published for the 6 Qt are exactly the four food presets in the **8 Qt** guide
([RJ38-SQSS-8T](https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQSS-8T-UG-US.pdf)), which *does*
carry a PRESET FUNCTION CHART. **The value appears to have been carried across from a different
appliance.** The row is now blank, the reason is written out on the page, and it is flagged as **F36**.
The 8 Qt's own preset row and its default times and temperatures were re-read and confirmed
character for character.

### 11.2 One value was true but mis-cited

The **Emeril's "Interior light"** row cited the brand product page. That page's specification strip lists
Timer, 26-Quart Capacity, Dual-Speed Fan, 25 Cooking Pre-sets, 16.9″D × 15.8″W × 14.8″H, 24.6 Liters,
Temperature Control and 120 volts — **and no interior light**. The value is nonetheless correct: the
owner's manual documents it in the control-panel section — *"F. LIGHT BUTTON: May be selected at any time
during the cooking process to light the appliance's interior."* The row has been re-sourced to the manual
and the manual's wording recorded in the row. Published as **F33**, because a citation that does not
support its value is as much a defect as an invented number.

### 11.3 The Articles section (new)

The brief asks for a *"polished marketing affiliate website"* with *"catchy trendy articles and topics"*.
The canonical build had a buying guide, a comparison and three product pages, but **no article section**;
the only articles in the repository lived in an annex build and were not reachable from the root
navigation. There are now **five articles** on the canonical site, at `/articles/`:

| Article | Target query | What it does |
|---|---|---|
| [Air fryer vs toaster oven](https://kanlerxz87-cyber.github.io/Zone1/articles/air-fryer-vs-toaster-oven.html) | air fryer vs toaster oven | Compares the three units on documented presets, ceilings and clearance |
| [450 °F "Hi-Fry" explained](https://kanlerxz87-cyber.github.io/Zone1/articles/450f-hi-fry-explained.html) | air fryer 450 degrees hi fry | Teaches the 60-second manual check, from the live conflict in this product set |
| [Dual-basket vs single-basket](https://kanlerxz87-cyber.github.io/Zone1/articles/dual-basket-vs-single-basket.html) | dual basket vs single basket air fryer | The one question that decides it, with Sync Finish as documented |
| [26 quarts, 1,519 cubic inches](https://kanlerxz87-cyber.github.io/Zone1/articles/air-fryer-capacity-guide.html) | 26 quart air fryer capacity | Capacity from published numbers only, including the arithmetic |
| [Why this site shows no Amazon prices](https://kanlerxz87-cyber.github.io/Zone1/articles/why-no-amazon-prices.html) | affiliate disclosure no prices trust | The rule in Amazon's own words, and what is shown instead |

Editorial rules, enforced by the build: article copy is **data**, not hand-written HTML, and every
factual sentence carries the source ids it was written from as inline `[[Sxx]]` tokens that expand into
links to the official page. A paragraph with no source is visibly unsourced rather than quietly
authoritative. Every article page carries the Operating Agreement §5 disclosure in the site-wide bar and a
**link-level disclosure beside every affiliate link**. No article claims a product was tested, and none
quotes an Amazon price, rating or review count.

### 11.4 The row-source rule is now met across the whole repository (F17, F25 closed)

The brief: *"Every table row must have a source link to an official site."* At the start of this pass the
audit said **281 rows** failed. Two thirds of that number was the gate's own fault:

* the link gate's regex only matched **double-quoted** `href` attributes, so 33 rows that did carry a
  source link were being reported as unsourced;
* it recognised only one filename for the flagged page, so a sibling build's `flagged-for-review.html`
  did not count;
* it did not know the source registers of the parallel builds, so rows citing `sell.amazon.com` or
  `advertising.amazon.com` — official Amazon domains — were reported as unsourced.

With the gate corrected, the true figure was **248 rows**. A row-source pass was then added **inside the
research/ and site/ generators** (so it survives a rebuild) and **scripts/source_rows.py** applies the same
pass to the three hand-authored builds. Rows that state a fact now link to that fact's official document;
rows that are judgements, blocked metrics or unverified values link to the flagged page, which is where
this project puts unconfirmed values.

**Result: 248 → 0.** The stricter gate then exposed a genuine defect — the research content plan linked to
an article that was never written — which is now rendered as plain text marked *not published*.

### 11.5 What this pass verified, in one line each

| Fact | Source | Result |
|---|---|---|
| Three short links → their three destinations | the three `link.amazon` URLs | confirmed, titles match character for character |
| A nonsense token | `link.amazon/ZZZ9ZZZZZ` | **403**, not a shuffled product |
| A 9-character token as an ASIN | `amazon.com/dp/B04G1MEwY` | **Page Not Found** |
| Commission Table 1 | Standard Commission Income Statement | all 11 rows + bounty amounts match |
| Disclosure wording and Clear/Conspicuous rule | Associates help topic | verbatim match |
| Price rule (§2(b)), reviews/star ratings (§6(t)), lowest-new/lowest-used comparison rule | Program Policies | re-read first-hand in this pass before being asserted in new copy |
| Chefman 6 Qt interior light, capacity, dimensions, Hi-Fry, Sync Finish | brand page + user guide | confirmed |
| Chefman 8 Qt presets and every default time/temperature | user guide | confirmed |
| Emeril spec table, 24 named presets, interior light | owner's manual | confirmed (preset chart ends at "Warm") |
| Emeril preset count across official sources | brand page + manual + Amazon title | **still inconsistent (F29)** — no count asserted |

### 11.6 State after this pass

* **20** root pages generated by `build.py` (was 13), **98** pages verified in total, **0 errors**.
* **43 spec rows: 41 verified, 2 blank+flagged** (was 42/1 — the sixth pass blanked one more row).
* **24 official sources**, all linked, none third-party.
* **4,883 links, 0 broken, 0 advisory**; **0 table rows without a source link** in the entire repository.
* Research 801 checks OK · annex 382 assertions OK · s2 build current · platform 33/33 · audit 0 warnings.
* Flags: **F36** (Chefman 6 Qt preset count) and **F33** (mis-cited value) added; **F17** and **F25** closed.

### 11.7 Open for the account holder — none of it blocks the merge

1. **Confirm the product identity for each supplied link.** The destination is reproducible; whether each
   token is the product you meant to market, and which Associates tag rides on the redirect, can only be
   settled from inside Associates Central (F10, F14–F16, F21).
2. **Set the Associates tag.** No page on this site can earn until the account holder confirms it (F6).
3. **Read F29 and F3.** The Emeril's preset count is stated five ways by official sources, and the Chefman
   8 Qt's 450 °F Hi-Fry claim contradicts the brand's own manual. Both are published, neither is resolved.
4. **Decide the canonical build.** Six parallel builds are published on one domain (F20). The root build is
   the canonical one and the one this summary describes; the others are preserved annexes.

> *Merge note (2026-11-14): the block above and the block below were written by two sessions concurrently; both are kept verbatim and nothing was discarded.*

## 11. Pass 7 — independent re-verification and the model-mapping finding, 2026-11-14

**Session:** `arena/6b2eddeb` · **Branch:** `arena/6b2eddeb-zone1` · **Base commit:** `b990352`
**Raw evidence:** [`session-6b2eddeb/EVIDENCE-2026-11-14.md`](session-6b2eddeb/EVIDENCE-2026-11-14.md)

This pass re-fetched the sources it relied on rather than trusting any earlier record. Everything
below is what a live read on 2026-11-14 actually returned.

### 11.1 What was re-read, and what held

| Re-read | Result |
|---|---|
| The three `link.amazon` tokens | All three resolved to `B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH` again, and all three landing `<title>` values matched the stored `amazon_listing_title` strings **character for character**. Still `plpRedirect=mhFallback` on each. |
| Associates Program Operating Agreement (S1) | `Updated: October 15, 2025`; §5 disclosure sentence present. |
| Associates Program Policies (S2) | Read the whole Participation Requirements section map. §2(b) holds special links, prices, sub-tags and misleading claims; **§6 "Content on your Site"** holds items (a)–(z) including (g) incentives, (n) framing, (t) reviews/ratings, (u) self-purchase, (v) cloaking, (w) link shortening, (y) price tracking. All quoted texts matched the stored quotes. This independently reproduces flag **F27**. |
| Standard Commission Income Statement (S3) | All 11 Table 1 rows matched `data/commission-rates.csv` **word for word and rate for rate** (Kitchen 4.50%, Home 3.00%, All Other 4.00%, Coach 0.00%). Bounty amounts matched. Read with no login. |
| Chefman RJ38-SQPF-3TDB-2W page (S10) | Every stored value for product 1 is stated on the page. No discrepancy. |
| Chefman RJ38-SQSS-8T page (S12) | Every stored value for product 3 is stated on the page. No discrepancy. |
| Emeril 26 QT page (S14) | All stored values still present, and the 25-vs-24-vs-10-in-1-vs-11-in-1 conflict is **still live on the brand's own page**. |

**No published value was found to be wrong.** Three new sources (S25–S27) were added, and four new
flags (F32–F35) were published.

### 11.2 The new finding: two Chefman model families, not one (F32, F33)

This is the substantive result of the pass.

**6-quart family (product 1, ASIN B0CDY277D3).** Chefman's own store currently publishes **three**
different 6-quart dual-basket SKUs, not the two the site records:

| Model | Temperature range | Functions | Rating on chefman.com |
|---|---|---|---|
| `RJ38-3DBW-V2` | 90–400 °F / 32–204 °C | 5: air fry, bake, reheat, dehydrate, frozen | 4.5 from 30 |
| `RJ38-SQPF-3TDB-2` | no spec block published | none published | 4.6 from 194 |
| `RJ38-SQPF-3TDB-2W` | 200–450 °F / 95–235 °C | Hi-Fry 450 °F, Sync Finish, Sync Baskets | 4.6 from 1,305 |

The site's mapping to `-2W` stands on the `Hi-Fry` wording in the Amazon title, which only the `-2W`
page documents. But "Easy View windows" appears on **all three**, so the title does not discriminate
by itself. More importantly, two other builds shipped in this repo (`site/`, `research/`) map the
same ASIN to `RJ38-3DBW-V2` **with no caveat** — so the repository currently publishes two confident,
contradictory answers for the same ASIN, two clicks apart.

**8-quart family (product 3, ASIN B08DKYBTPH) — this materially changes flag F3.**

| Model | Hi-Fry | Functions | Finish |
|---|---|---|---|
| `RJ38-SQSS-8T` (currently mapped) | none — max 400 °F / 205 °C | 4 food presets | stainless steel |
| `RJ38-8T-BLACK` | **450 °F / 232 °C for the final two minutes** | **air fry, bake, dehydrate, frozen** | **matte black** |

The Amazon title reads `…4-in-1 with 450°F Hi-Fry Option… | Bake, Dehydrate, Frozen | … Stainless
Steel`. The **function list and the 450 °F Hi-Fry match `RJ38-8T-BLACK` word for word**; the finish
matches `RJ38-SQSS-8T`. The site has been presenting this as "one of the two official sources is
stale". That is now the **less** likely explanation: the more likely one is that the listing
describes a unit whose documented features belong to `RJ38-8T-BLACK`. **No value was changed** — the
`Hi-Fry / 450 °F: None` row remains true of `RJ38-SQSS-8T`, which is what it is sourced to — and no
model is asserted.

**What the owner should do:** open each listing, read the model number in the product-information
block, and settle F32 and F33 in one sitting. It is the single highest-value action available and it
takes about two minutes. Everything downstream — copy, comparisons, the buying guide — is written to
be safe either way, but it cannot become *specific* until that is done.

### 11.3 The other new flags

| ID | Item |
|---|---|
| **F34** | `EXECUTIVE_SUMMARY.md` (the older second summary at the repo root) still asserts "Identity verified. All three short links resolve to Amazon.com product pages with different ASINs" and "the official commission schedule redirected to a sign-in page". Both are contradicted by this session's fresh reads. A warning banner sits above it, but the sentences remain and the file is still linked from the site. Not edited — rewriting another session's published sentence is a content decision. |
| **F35** | Nine separate HTML sites for the same three products are published in this repo and disagree (F32, F27). The root nav used to list six of them as peers. **This pass fixed the presentation**: the sidebar now carries one "Previous passes" entry, and the new `previous-passes.html` catalogues every build, states exactly where each diverges, and names which one is canonical. |

### 11.4 Editorial layer added

The brief asks for "catchy, trendy articles and topics related to the product". The site had one
buying guide and a comparison matrix but no article set, so this pass added **five articles** at
`articles/`:

1. *Dual-basket or countertop oven? The 8-quart question nobody answers* — comparison
2. *What "450 °F" actually means on an air fryer listing* — explainer
3. *25 presets, 24 presets, or 10-in-1? One brand page says all three* — source forensics
4. *Why this affiliate site shows no Amazon prices, ratings or review counts* — policy explainer
5. *Two 3-quart drawers or one 8-quart basket: which actually feeds four people?* — head-to-head

They are written to a build-enforced rule, not a style guide: a factual number in an article must
appear **verbatim** in `data/products.json` or the build fails, and every section must cite a source
id that resolves in `data/sources.json` or the build fails. During development that guard rejected
18 paraphrased values, which is why it exists. No article claims first-hand testing, and none states
an Amazon price, rating or review count.

### 11.5 Verification performed this pass

```
python3 build.py                 → 21 pages, all guards pass (rows sourced, disclosure, article values)
python3 verify.py                → 99 pages, 43 spec rows (42 verified / 1 blank+flagged),
                                   27 sources, 0 errors
platform/tests                   → 33 tests OK
platform/audit/report.py         → AUDIT PASSED, 0 warnings
scripts/build_s2_site.py --check → build current, 16 files
scripts/check_links.py           → 4,477 links, 0 broken owned
research/check_research.py       → OK
scripts/build_site.py + verify_site.py → ALL CHECKS PASSED (382 assertions)
Independent crawl of the canonical build → 21 pages, 0 broken internal links,
                                   disclosure on every page, no template residue
```

### 11.6 What this pass did not do

It did not re-read the three owner's-manual PDFs, the FTC pages or 16 CFR Part 255 — those were
re-read on 2026-11-14 by earlier sessions and are structurally covered by `verify.py`. It did not
edit `EXECUTIVE_SUMMARY.md`, any `data/verified/` file, or any other session's build. It did not
resolve F32 or F33, because resolving them requires opening a logged-in listing, which this session
cannot do. **No number on this site changed as a result of this pass.**


---

## 12. Integration pass 7 — the editorial layer, and two sessions converging on it (2026-11-14)

### 12.1 What was missing

The brief asked for a site that **looks like a polished marketing affiliate website** with **catchy,
trendy articles and topics related to the product set**. Before this pass the canonical build had no
editorial layer of its own at the root: the only articles in the repository lived inside a parallel
session's `research/` annex, unreachable from the main navigation.

### 12.2 What landed

Two sessions worked this gap **at the same time** and merged independently:

| Session | Contribution | Now on `main` as |
|---|---|---|
| `sess-6b2eddeb` (PR #42) | A data-driven article engine: `data/articles.json` → `articles/*.html`, five articles, with a build gate (`check_articles()`) that refuses any `{{value}}` not present verbatim in `data/products.json` and any `cite` id not in `data/sources.json`. | The canonical engine and five articles |
| `arena/38f82d32` (this pass, PR #43) | Two further articles (a documentation-based 6 Qt review and an eight-line spec-sheet guide), ported into the same `data/articles.json` schema rather than shipped as a second competing hub; plus a **new gate**, `check_article_pages()`, and this section. | Articles 6 and 7, and one new build guard |

**The merge decision, recorded honestly.** This pass originally generated four articles of its own in a
separate `editorial.py` module. When PR #42 landed first with five articles and a better-understood data
contract, shipping both would have produced two articles hubs, one of them orphaned, and duplicate
targets competing for the same queries. The resolution: **the other session's engine is canonical**;
this pass kept only the two articles that did not duplicate it (a product review and a spec-sheet
guide), rewrote them into `data/articles.json`, and dropped the module. No published value was lost, and
nothing the other session wrote was overwritten. The superseded module remains in this branch's history
(commit `f9daccb`) and in `backup-38f82d32-before-merge` for audit.

### 12.3 Two gates now protect the article layer

| Gate | Protects against |
|---|---|
| `check_articles()` (from PR #42) | An article citing an unregistered source id, or stating a number that is not present verbatim in the verified dataset. Its author reports it rejected 18 paraphrases while writing. |
| `check_article_pages()` (this pass) | An article page that ships **without the Associates sentence in its header**, without a statement that nothing was tested, or containing a prohibited Amazon price/rating pattern. Verified by negative test: fed a synthetic page, it correctly returns all three failures. |

### 12.4 Compliance position of the article layer

- **Operating Agreement §5** — the required sentence is injected by `layout()` on every page and is now
  also checked specifically on article pages.
- **FTC Disclosures 101** — "you can't talk about your experience with a product you haven't tried."
  Every article carries a no-testing statement; the new gate makes its absence a build failure.
- **Program Policies §2(b) and §6(t)** — no Amazon price, availability, star rating or review count
  appears in any article. The gate rejects the patterns.
- **Program Policies §6(a)** — Amazon listing titles are quoted, not rewritten.

### 12.5 State of the record after this pass

| Measure | Value |
|---|---|
| Root build pages | **23** |
| HTML files checked by `verify.py` | **101** |
| Specification rows | 43 (42 verified, 1 blank + flagged) |
| Registered official sources | **27** (S25–S27 added by PR #42: the three further Chefman SKU pages) |
| Open flagged items | **35** (F1–F35 — F32–F35 added by PR #42) |
| Values invented, estimated or back-filled | **0** |

### 12.6 New flags from the concurrent pass, carried and not re-litigated

F32 (Chefman publishes three 6-quart dual-basket SKUs, not two), F33 (Chefman's RJ38-8T-BLACK
documents the 450 °F Hi-Fry and the exact four functions in the Amazon title for B08DKYBTPH — which
sharply narrows F3 toward "two different SKUs" rather than "one stale page"), F34 (a legacy
`EXECUTIVE_SUMMARY.md` asserts two claims a later pass disproved) and F35 (nine competing builds in
one repository). All four are published on `flagged.html` with their sources. **F33 is the most
consequential finding of the day**: it does not resolve F3, but it changes which explanation is more
likely, and it is recorded as evidence rather than as a resolution.
## 13. Independent re-verification — pass 7 (2026-11-14, session `arena-052f2c9f`, branch `arena/052f2c9f-zone1`)

A session that wrote none of the stored values re-read the load-bearing facts against the live
official sources on 2026-11-14 (19:05–19:15 UTC), hours after pass 6. Full evidence:
[`session-052f2c9f/EVIDENCE-2026-11-14.md`](session-052f2c9f/EVIDENCE-2026-11-14.md), rendered on
[`reverification.html`](reverification.html) as "Pass 7".

**Result: no stored value changed and nothing was filled in. This pass added no flags of its own;
the register as merged is F1–F35 (the concurrent `arena-6b2eddeb` pass 7 added F32–F35), and every
published value still traces to an official source.**

Key observations:

- **Link resolution, seventh round.** All three supplied short links resolved again to B0CDY277D3,
  B09B7SB46R and B08DKYBTPH with titles matching the stored values character for character — and,
  new in this round, each returned the **same `srctok` token earlier passes recorded for that same
  link** (a rotating target cannot preserve a per-token constant across two days and seven rounds).
- **The F-07 "fallback shuffle" reading is dead.** The nonsense-token control
  (`link.amazon/ZZZ9ZZZZZ`) was re-run independently and again returned a hard **403 Forbidden** —
  the resolver refuses unknown tokens instead of serving a shuffled product. What remains open is
  only whether these are the products the account holder *intended* (F1/F6), which no external
  check can prove.
- **Policy facts confirmed verbatim:** OA §5 disclosure wording (OA updated 2025-10-15), Commission
  Table 1 (Kitchen 4.50% / All Other 4.00%; air fryers still unnamed), Program Policies updated
  2026-04-14, 16 CFR 255.5 (eCFR current as of 2026-11-12), and the PA-API 5 deprecation notice
  (F24 stands).
- **Both hard conflicts are still live on the official pages** and still asserted by neither: the
  Chefman 8 Qt (brand 200–400 °F vs Amazon title 450 °F Hi-Fry, F3) and the Emeril preset count
  (25 / 24 / 10-in-1 / 11-in-1, F4/F5/F29).
- **Deploy-cache note (third recorded instance):** the first live fetch of `flagged.html` after the
  pass-6 merges returned the pre-pass-6 copy ("28 Open items"); a cache-busting re-fetch returned
  the current deploy (31 Open items). A stale first read is a CDN artefact — re-fetch before
  concluding the deploy is wrong.
