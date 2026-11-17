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

> **Refreshed 2026-11-16 by session `arena/ba29c641-zone1`** (this file's own numbering calls it pass 11;
> note a second session used the same pass label the same day, so trust the session id), because the numbers below
> had become the file's oldest claims: `data/products.json` now holds **77 specification rows — 75
> verified, 2 blank and flagged**, over **35** official sources. The 31 added rows are all values
> read from the three listings' own Product information blocks on 2026-11-16, each labelled
> "as listed by Amazon" so a listing claim never reads as a manufacturer specification; one blank
> row (the Emeril browse node) was filled from that same read. The bullets under this note are the
> running record of how the count moved, kept with their dates rather than rewritten.
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

- **27 sources** (S1–S27), all official; **43 spec rows** (**41 verified, 2 blank+flagged** —
  *corrected 2026-11-14 by pass 7 (sess-7111e2b6); that pass blanked the Chefman 6 Qt preset count,
  which its cited source does not state (F30), and re-sourced the Emeril interior light to the
  owner's manual (F37)*);
  **38 open flag rows** (34 programme + 4 product), all published on [`flagged.html`](flagged.html).
  *Counting note (corrected 2026-11-14; two independent passes converged on the spec-row split and this
  line is their merge).* The register holds 7 product-level flag instances, but three of them are the same
  cross-product item — **F6**, the unobservable Associates tag — raised once per product. `build.py`'s
  `page_flagged()` renders F6 once at programme level and suppresses the three per-product copies, so the
  page shows 34 + 4 = **38** distinct rows, not 41.
  *History of this line:* it originally read **40 verified / 3 blank** and **17 open flags (13 programme +
  4 product)**. Two rows were filled from the manufacturers' own owner's manuals, leaving the Chefman 8 Qt's
  *Hi-Fry / 450 °F mode* as the only blank (F3). The flag count then rose as F18–F27 were added by later
  passes,
  **F28** by sess-91d0552e (PR #36), **F29–F31** by pass 6 (sess-54c66535), **F32–F35** by
  `arena/6b2eddeb` (PR #46), **F36** by pass 7 (sess-ce4070ad) — F36 records that the short links'
  `srctok` marker changes between sessions and on cache-busted repeats, contradicting F10's "stays
  constant" wording (renumbered from F32 after PR #46 took that ID) — and **F37** by sess-7111e2b6
  (PR #51).
- `build.py` + `verify.py` gates pass: 105 pages checked, **0 errors**, 0 broken internal links,
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

### 11.7 PR, merge and deployment

**PR [kanlerxz87-cyber/Zone1#51](https://github.com/kanlerxz87-cyber/Zone1/pull/51)** — opened from
`arena/7111e2b6-zone1` to `main` with the change summary, the sources, the gate results and the flagged
irregularities. Checks on the head commit: `CI / verify` ✔ · `Verify verification annex (site/)` ✔ ·
merge state CLEAN. **Merged 2026-11-14T19:22:07Z** with `gh pr merge 51 --merge` (no approval wait),
merge commit **`b899e2a`**.

Post-merge workflows on `main`: `CI` ✔ · `Verify verification annex (site/)` ✔ · `Build, verify and deploy
to GitHub Pages` ✔ · `pages build and deployment` ✔. GitHub Pages reports `status: built`, source `main` /
`/`, build type `legacy`, latest build commit `b899e2a`, error `none`.

Live check (cache-busted): `/articles/index.html` serves "Eight pieces written for this product set" with
all eight articles; `/articles/air-fryer-capacity-guide.html` is live with every section's source badges;
`/flagged.html` serves 37 open items including **F36** and **F37**, with the two **CLOSED** markers for F17
and F25. Site: **https://kanlerxz87-cyber.github.io/Zone1/**

### 11.8 Open for the account holder — none of it blocks the merge

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

## 14. Session `3b99448e` — suggestions, decision gate and link re-review (2026-11-15)

Branch `arena/3b99448e-zone1`, claims T13–T18 logged in COORDINATION.md. All files added by this
session live under `session-3b99448e/` so they cannot overwrite another session's work.

### 14.1 T13 — link re-review (`session-3b99448e/link-review.md`)

Re-reviewed the three supplied `link.amazon` short links against the official evidence already
recorded in this repo (no live Amazon fetch was possible from this session):

- The tokens are 9 characters; an ASIN is 10 characters (S23 — Amazon KDP Help).
- `amazon.com/dp/<token>` returns "Page Not Found" (S21); an unrecognised short-link token returns
  403 (S22).
- The short links resolve through Amazon's `plpRedirect=mhFallback` handler to air-fryer listings
  (candidate ASINs B0CDY277D3, B09B7SB46R, B08DKYBTPH — S17/S16), but destination is not identity:
  **product identity remains unconfirmed**.

### 14.2 T14 — suggestions (`session-3b99448e/suggestions.md`)

- **Design (D-1…D-10):** dashboard layout kept; hero value proposition above the fold; disclosure
  bar on every page (already built); verified-specs-only cards with blank cells left blank and
  flagged; no Amazon photos hotlinked; comparison matrix without prices; category subpages under
  Kitchen → Air fryers; JSON-LD + meta tags; mobile-first; WCAG AA contrast audit quarterly.
- **Content (A-1…A-10):** ten article working titles in the air-fryer niche dictated by the product
  set — e.g. "What '450 °F Hi-Fry' actually means", "6 Qt vs 8 Qt vs 26 QT: how much capacity?",
  "Why this site doesn't show Amazon prices". Anti-AI-slop rules: no unverified superlatives, one
  topic per page with dates, human voice, vendor claims labelled, no invented testing, disclosure
  on every page.
- **Traffic (T-1…T-8):** long-tail keywords from verified data; programmatic category/comparison
  pages; sitemap.xml + robots.txt already ship; compete on transparency ("shows its gaps"); Pinterest/
  TikTok/YouTube Shorts for visuals; double-opt-in email; quarterly re-verification against official
  sources.
- **Compliance:** disclosure wording per OA §5 (S1) and FTC (S7/S8/S9); replace `link.amazon/` short
  links with canonical tagged `/dp/<ASIN>` URLs only after Q-1/Q-2 are answered; PA-API 5 is
  deprecated — Creators API only (S24); IP License §2(e) bars training models on Program Content.

### 14.3 T15 — decision gate (`session-3b99448e/decisions.md`)

Ten questions (Q-1…Q-10), each with: what is known with its official source, what is missing, a
suggested pending answer, and how to discover the missing fact (M-1…M-8). Blocking questions:
Q-1 Associates tag (currently blank), Q-2 product identity of the three links, Q-3 commission
category per product, Q-4 account approval status, Q-6 Japan-store eligibility for the owner in
Osaka. Nothing missing is estimated.

### 14.4 What is already live

The concurrent session `633b115f` (PR #58, merged) added `suggestions.html` (SG-01…SG-12, each with
options A/B/C and an unfilled "Your choice" column) and `questions.html` (Q-01…Q-14, known/missing/
how-to-find/unblocks), both rendered by `build.py` and listed in NAV and `sitemap.xml`. **Nothing on
those pages has been implemented yet.** This session's deeper docs remain under `session-3b99448e/`.

### 14.5 Next decision step

The owner reviews SG-01…SG-12 and Q-01…Q-14, records a choice (Approved / Rejected / Needs more
info) plus a date, and implementation proceeds only for Approved rows. The `verify.py` gate stays
blocking: no unsourced value, missing disclosure or broken link may ship.


---

## 15. Pass 9 — final integration, live re-verification and the SEO layer (2026-11-15, session `arena/88bb2db6`, branch `arena/88bb2db6-zone1`)

### 15.1 What this pass was

Every task on the shared board was already marked `done` when this session started, on `main` @ `cacdb85`, with all local gates green. So this pass did not rebuild delivered work. It did three things: it **re-read the load-bearing facts against the live official sources**, it **read the generator line by line for defects**, and it **finished the integration the brief asks for** (PR → merge → confirm the Pages deploy).

The full evidence, with verbatim quotations and the URL of every fetch, is in `session-88bb2db6/EVIDENCE-2026-11-15.md`. The machine-readable ledger is `session-88bb2db6/pass9.json` (20 rows) and it renders as its own section on `reverification.html`.

### 15.2 What was re-read and confirmed (2026-11-15)

| Fact | Source | Result |
|---|---|---|
| `link.amazon/B04G1MEwY` → B0CDY277D3 | amazon.com | confirmed; the served `<title>` matches the published title word for word |
| `link.amazon/B02NbDxp3` → B09B7SB46R | amazon.com | confirmed, same |
| `link.amazon/B00hJ57DV` → B08DKYBTPH | amazon.com | confirmed, same |
| Table 1 rate table | Standard Commission Income Statement | confirmed: `Physical Books, Kitchen, Automotive — 4.50%`; `All Other Categories — 4.00%`; "air fryer" is **not** a named category, so the per-product rate stays unverified |
| Application review | Application Review Process | confirmed: 3 qualifying sales / 180 days, 10 posts, 60-day recency, 500 followers, personal orders do not qualify |
| Program Policies version | Program Policies | confirmed: page header reads `Updated: April 14, 2026` |
| Chefman 6 Qt — all 15 spec rows | chefman.com + the `-2W` manual | confirmed word for word, including `HI-FRY Buttons — Raise temperature to 450°F/235°C for 2 minutes` |
| Chefman 8 Qt — all spec rows | chefman.com | confirmed; the 450 °F / 4-in-1 conflict with the Amazon listing is **still live** |
| Emeril 26 QT — capacity, power, temperature | the `FAFO-001` manual + emerileveryday.com | confirmed: `26 quarts (1519 cubic inches)`, `120 V/1700 W/60 Hz`, `75° F - 500° F` |

### 15.3 One new conflict, recorded rather than resolved

**F44 — how many accessories are in the box.** The Emeril brand page says *"Included are 7 premium accessories"*. The Amazon listing title for the supplied link says *"Six Cooking Accessories Included"*. The manual adds only *"Some accessories may not be included with purchase."* No earlier pass had recorded this. The site now publishes the manufacturer's own count with **both** documents linked, and files the discrepancy for the account holder to settle from the delivered box.

### 15.4 Two flags tightened to match their documents exactly

* **F4 (Emeril preset count).** The manual does not state the numeral 24 anywhere — it **lists** 24 presets by name, and it lists them twice: the *Preset Mode Chart* and the *Recommended Accessory Positions* table each carry the same 24 rows. The wording changed from "names exactly 24 presets" to "lists 24 presets by name". The verdict is unchanged: 24. This pass also confirmed that the Amazon listing title is a **third** document on this count, and that it says 24.
* **F3 (Chefman 8 Qt 450 °F)** re-read and still live; no value asserted.

### 15.5 Ten defects found in the site build itself, and fixed

None of these changed a sourced value. All ten are fixed on this branch.

1. `page_suggestions()` declared the **wrong file name** to the layout function, so the Suggestions page carried the parallel page's canonical URL, `og:url` and breadcrumb, and highlighted **no** navigation item.
2. `page_suggestions_alt()` had the mirror image: it claimed the canonical Suggestions URL and lit up the wrong nav entry.
3. The two pages therefore shared one `<title>`.
4. `questions.html` and `decision-gate.html` shared one `<h1>`.
5. `marketing-directions.html` stated **16** suggestions while rendering the parallel register's **12** — a wrong count on a published page.
6. `site/index.html` nested an `<a>` inside another `<a>` — invalid HTML.
7. The landing page and all three product pages linked "redirect evidence" to a **raw markdown file** whose conclusion had been superseded, instead of to the rendered in-site page.
8. The landing comparison table published the Emeril preset row as an open conflict while the product page resolved it — the same fact told two ways.
9. `verify.py` allow-listed neither `advertising.amazon.com`, `sell.amazon.com` nor `api.github.com`, producing **18 warnings** for links to official Amazon and GitHub pages. Noise that trains a reader to ignore the list.
10. The root build shipped **no canonical URL, no Open Graph or Twitter card tags and no JSON-LD** on any page. A shared link rendered as a bare URL, and no page could qualify for a rich result — the organic-traffic goal the brief sets out had no technical entry point.

### 15.6 What was added

* **Canonical URL, Open Graph and Twitter card tags on all 28 root pages**, and JSON-LD: `WebSite` and `Organization` on the landing page, `Article` + `BreadcrumbList` on the eight articles, `ItemList` on the comparison and category pages, `CollectionPage` on the hubs, `ItemPage` on the three product pages, and `FAQPage` on the questions register — 20 rows built only from text the page already prints.
* **A social card** at `assets/og-card.png` (1200×630), drawn from the site's own palette and copy by `session-88bb2db6/make_og_card.py`. It states only what the site states.
* **`<lastmod>` in `sitemap.xml`**, carrying the date the published values were last re-read.
* **Two new build guards**, each proven to fire on an injected violation: a repository-wide nested-anchor check in `verify.py` (exit 1 on injection, exit 0 clean) and the same check for the annex in `scripts/verify_site.py` (now 393 assertions).
* **A derived-count fix in this document's site page.** The executive summary had hard-typed "Twelve sources are used" and "61 rows" — both stale (the register holds 29 sources and 81 ledger rows). Both are now computed from the data files, so they cannot drift again.

### 15.7 What this pass did **not** establish

* The Associates tracking tag inside the three short links — unobservable from outside Associates Central. Flag F6 stands.
* Which model the operator *meant* for each link — the destinations are reproducible; the intended identity is not. Flag F1 stands.
* Which Amazon category each ASIN sits in — Table 1 names no air-fryer category, so the per-product rate stays blank with both candidate rows shown.
* Whether the unit or the box says 24 or 25 presets, and six or seven accessories — F4 and F44.

### 15.8 The recommendation is unchanged

Verify the three model numbers and the Associates tag in a logged-in browser, then replace the three `link.amazon` short links with canonical tagged `/dp/<ASIN>?tag=<tracking-id>` URLs built inside Associates Central, then re-run the re-verification pass. Until then the site publishes candidate mappings, leaves every unconfirmed value blank, and flags the rest. Nothing was invented to fill a gap.

---

## 16. Integration pass 9 — session `arena/63a2c638`, branch `arena/63a2c638-zone1` (2026-11-15)

**Base:** `cacdb85026e29cb7d124e15b0d660e2af112bbde` (main, after PR #66 / T19 merged).
**Scope claimed in `COORDINATION.md`:** Z1 line-by-line review + live re-verification round 9;
Z2 editorial/traffic plan; Z3 the suggestions decision queue; Z4 the questions register;
Z5 this summary; Z6 integration, PR, merge and Pages confirmation.

### 16.1 What this pass re-read, live, on 2026-11-15

Every source below was re-fetched on 2026-11-15 and read against the value it supports. Nothing
was taken from a previous session's note.

| Source | Result |
|---|---|
| S2 Associates Program Policies | Confirmed. Page still reads **"Updated: April 14, 2026."** The session definition re-read verbatim: 24 hours from the click, 89 days for a cart-added order, 180 days for shipment/payment. |
| S3 Standard Commission Income Statement | Confirmed. **"Physical Books, Kitchen, Automotive | 4.50%"** and **"All Other Categories | 4.00%"**, character for character. Bounty events unchanged ($12.00 Prime trial and paid membership). |
| S10 Chefman 6 Qt Dual-Window | Confirmed all published values: 6 Qt / 5.67 L; 200–450 °F; 13.38 × 11.81 × 10.63 in; 13.3 lb; 1700 W/120 V; RJ38-SQPF-3TDB-2W; cETL approved, 1-year assurance. Review widget: **4.6 from 1,305 reviews**. |
| S12 Chefman 8 Qt TurboFry | Confirmed: **Max temp 400 °F**, 4 cooking presets, 200–400 °F, 1700 W/120 V, 8 Qt dimensions 15.4 × 12.6 × 13.5 in, 12.8 lb, RJ38-SQSS-8T. Review widget: **4.6 from 716 reviews**. The 400 °F figure is the source of the conflict with the listing title's 450 °F claim (F3). |
| S14 Emeril 26 QT French Door | Confirmed: 26-quart, 24.6 L, 16.9″D × 15.8″W × 14.8″H, 120 V, **"25 Cooking Pre-sets"**, $199.99, SKU **4-00675-02A-VN**, and **2.6 from 25 reviews**. The description on the same page still says "10-in-1" — the conflict is live, not historical. |
| S16 / S29 (ASINs B0CDY277D3, B08DKYBTPH) | Confirmed. Both `<title>` values matched the stored strings character for character. Both pages also rendered an identical browse-node breadcrumb. |
| S28 (ASIN B09B7SB46R) | **Not re-read.** Three fetches were each answered with Amazon's automated *"To continue, please click the 'Continue shopping' button below"* checkpoint, not the product page. Recorded as such on the source record rather than reported as confirmed. |
| S32–S34 (new) | The brands' own commerce endpoints, read for the first time this pass. See 15.2. |

### 16.2 Three findings, none of them a value error

**F51 — the brand's own store reports a different weight than the brand's own spec block.**
Chefman's product pages print 13.3 lb (6 Qt) and 12.8 lb (8 Qt) in their Specifications blocks; those
are the figures this site publishes, cited to S10 and S12. The same brand's commerce endpoint, read
the same day, reports **14.51 lb / 6,582 g** for RJ38-SQPF-3TDB-2W (S30) and **13.4 lb / 6,078 g**
for RJ38-SQSS-8T (S31). The likeliest reading is product weight versus packaged weight, but neither
page says so, so the site did not choose. **No published value changed** — the specification block
remains the cited source, because that is the document the published row points at.

**F52 — the questions register overstated what is missing.** Q-06 asked for exterior dimensions,
weight and warranty for all three products and was filed as `not_stated`. Checking the nine cells
against the dataset: dimensions are published for all three, warranty for all three, and weight for
both Chefman models. **Eight of the nine cells were already answered.** One is genuinely open — the
Emeril product weight, which neither the brand page nor the manual states. Q-06 has been narrowed to
that one cell and cross-linked to F52. This is the third defect in this project's history with the
same shape as F14 and F38: a register row describing the data as it used to be. It is the reason
Q-15 was added.

**F53 — the browse node is now published, and it does not settle the commission rate.** Both Chefman
listings render the breadcrumb *Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air
Fryers*. It is tempting to read "Kitchen" there and apply the 4.50% Kitchen rate from S3. That would
be an inference: S3's categories are commission categories defined by the Associates programme,
browse nodes are a shopper-navigation taxonomy, and Amazon publishes no mapping. The same breadcrumb
begins "Home & Kitchen" while S3 carries both *Kitchen* at 4.50% and *Home* at 3.00%. The site
therefore continues to show the commission rate as unconfirmed (Q-11) and now shows the browse node
as a separate sourced fact, with the limit published alongside it.

### 16.3 What was built

* **`topics.html` — Content and traffic plan** (new page, in NAV under *Decide* and in `sitemap.xml`).
  Fourteen article topics: eight already published, six proposed. Every row carries the official
  source the finished article must cite. The page states plainly that **there is no keyword-volume
  data in this repository and none was invented** — the demand column is labelled judgement
  throughout. It also lists five distribution channels, including the two Amazon's policies close
  off: paid search on Amazon Marks (Commission Income Statement §2(c), disqualified purchases) and
  price tracking or alerts (§6(y)). Those are listed next to the real channels so the plan cannot be
  read as if they had never been considered.
* **Choose a path** (new section on `suggestions.html`). Sixteen independent suggestions are a
  backlog, not a decision. Four paths group them into ordered work with an explicit entry condition,
  a deliverable, and an honest "what it does not fix". Suggested order: P1 make it safe to publish,
  P3 make it findable, P2 make it read like a shop, P4 make the machinery trustworthy. A build guard
  fails the build if a path references a suggestion that does not exist.
* **Q-15** (new): is there any published statement a live official source contradicts today? Answers
  the standing-accuracy question that F14, F38 and F52 all raise.
* **SG-17** (new): the site has no visual layer — no product imagery anywhere — and a marketing site
  without one does not convert. Four options, with the licensing constraint named first.
* Sources **S32–S34** added (the brands' own commerce endpoints), and round-9 observation notes
  appended to S2, S3, S10, S12, S14, S16, S28 and S29.

### 16.4 What this pass did not do

It did not change a single published product value. It did not resolve the model number on any
listing (Q-01 remains open), confirm the Associates tag (Q-02/Q-04), or state a commission rate
(Q-11 remains open). It did not edit any file in `site/`, `s2/`, `data/s2/`, `research/`,
`platform/`, `docs/`, `dashboard/`, `crosscheck/` or `annex-88769516/` — those belong to other
sessions' builds.

### 16.5 Next decision step

Open `suggestions.html` and pick one of the four paths rather than one of the sixteen rows. Path 1
is unblocked and takes an afternoon; everything else assumes it.

---

## 17. Pass 10 — verification, and the two clauses the brief needed (2026-11-16, session `arena/9fccce0c-zone1`)

**Branch:** `arena/9fccce0c-zone1` · **Baseline:** `6dbfa7cb` (= `origin/main` at claim time)
**Full evidence:** [`reports/verification-2026-11-16-9fccce0c.md`](reports/verification-2026-11-16-9fccce0c.md) ·
**Ledger on the site:** [`reverification.html`](https://kanlerxz87-cyber.github.io/Zone1/reverification.html)

This is the tenth independent re-read of the same register. It was run because the register is made
of values that move — a manufacturer's review counter, an Amazon listing title, a policy page's
"Updated" line — and because the last several passes each found something. It found three things.

### 17.1 The clause the brief most needed, and the register did not have

The brief this project answers asks for **an AI-powered Amazon affiliate marketing platform**
that automates product research, identifies trending products, and continuously optimises.
Amazon's Program Policies page carries a section written for exactly that case, and it was in
neither the canonical compliance register nor the platform blueprint:

| Clause | What it says, read verbatim 2026-11-16 | Where it now lives |
|---|---|---|
| **IP License §4 — "Agents" (Agent Terms)** | "The terms in this section ("Agent Terms") apply if you use, allow, enable, or cause the deployment of an Agent to access, use, or interact with the Program Content. For the purposes of these Agent Terms, "Agent" means any software or service that takes autonomous or semi-autonomous action on behalf of, or at the instruction of, any person or entity." §4(c) requires every HTTP/HTTPS request to carry "Agent/[agent name]" in the User-Agent string, forbids concealing or obfuscating that an access is from an agent, forbids completing or circumventing CAPTCHAs, and requires the agent to "respond truthfully to any question or prompt seeking to determine if interactions are coming from a human or a computer." | Requirement **C17**, guardrail **G11** |
| **Participation Requirements §5** | "You will not, without express prior written approval, use, or allow any third party to use, any Special Links or Program Content to develop machine learning models or related technology." | Requirement **C18** |

Before this pass, `data/compliance.json` contained **0** occurrences of "Agent Terms" and
`data/platform.json` contained **0** occurrences of "Agent". The clause was known to this
repository — the parallel build in `session-3740f69d/` carries an Agent-Terms row — but it had
never been carried into the canonical register that the live site publishes.

**What it changes, and what it does not.** The published site consumes no Program Content, so no
Agent Term is triggered by anything it renders today; the clauses matter for the *proposed*
research agent, which is the part of the brief that does not exist yet. Two things the clause
leaves open are published rather than guessed: whether an ordinary public listing page counts as
"Program Content" (the IP License defines Program Content around Creators API, PA API and Data
Feeds, and the policies page does not extend the definition to ordinary pages), and what the
agent must call itself. Those are **question Q-21** and **suggestion SG-22**. A third point is
only partly legible — §4(a) refers to "the requirements in section 3 of these Agent Terms", and
that section was not visible in the render used for this pass, which is recorded as **flag F62**
rather than papered over.

### 17.2 Three published pages pointed at a flag that does not exist

`data/questions.json`, `data/suggestions.json` and `data/sources.json` each told the reader to
see the flag numbered 46 for the Application Review Process recency criterion. **No such flag
exists** — the canonical register runs F1–F45 and F47–F58, and the legacy `data/flags.json`
register runs F01–F27. A reader who followed the pointer landed on the Flagged page and found
nothing, on a site whose entire claim is that every number is traceable.

Fixed: the three pointers now name **F56**, the row that actually covers the point. A new build
guard, `check_register_cross_references()`, now fails the build if any generated page cites a
flag, source, question or suggestion id that is not in the register it points at. The guard was
proven to fire: with a dangling `F46` injected into `data/questions.json` the build exits 1 and
names the page and the id; with the data restored it exits 0.

### 17.3 The carried-forward figures are now read from the source, and two counters had moved again

**F56 closes.** The Application Review Process page had not been loaded since 2026-11-13; its
four figures — three qualifying sales within 180 days, roughly ten posts, content recent within
about sixty days, about 500 social followers — were carried forward. They were re-read live on
2026-11-16 and confirmed verbatim, so the row's carried-forward part is closed and **question
Q-19 moves from "missing" to "known and sourced" with the answer on the row**. Two further
sentences were read at the same time and are new to the record: "personal orders do not qualify"
and "we aren't able to reassess an application once it's been rejected".

**Two volatile counters moved.** Chefman's own review widget read **1,307** on the 6 Qt page and
**717** on the 8 Qt page on 2026-11-16, against the 1,305 and 716 published from the 2026-11-14
read. Both averages held at 4.6 for the third consecutive read. The two rows were refreshed to
the new reading and all three dates are kept in each row, which is what flag F19 requires.

### 17.4 What else was re-read, and what it confirmed

Every load-bearing source was fetched live on 2026-11-16 and compared against what the site
publishes. Nothing published was found wrong.

| Checked live on 2026-11-16 | Result |
|---|---|
| Standard Commission Income Statement (S3) | Table 1 read verbatim without a login: Kitchen 4.50%, All Other 4.00%, Home 3.00%, PC 2.50%. Still no air-fryer row and still no ASIN→category mapping, so the per-product rate stays blank. |
| Program Policies (S2) | "Updated: April 14, 2026" confirmed; section order unchanged; §3(e), §6(s), §6(t), §6(w), §6(y), §5 and IP License §1, §2(e), §4 all re-read verbatim. |
| 16 CFR Part 255 (S9) | "up to date as of 11/12/2026", "Title 16 was last amended 10/30/2026", source "88 FR 48102, July 26, 2023", §255.5 "Disclosure of material connections" — all confirmed. |
| The three supplied `link.amazon` short links (S17) | All three resolved to the same three ASINs; all three `<title>` strings matched the stored values character for character, including the Emeril wording that changed on 2026-11-15; all three rendered the same browse-node path. |
| Both Chefman product pages (S10, S12) | Every published specification row still stated in the manufacturer's own Specifications block, character for character. |
| The Emeril product page (S14) | Price, model and rating unchanged; the four-way preset and in-1 disagreement between official pages is still live and still unasserted. |
| The three Chefman store endpoints (S32–S34) | SKU, price, compare-at price, grams and weight all matched. |

**Not re-read in this pass, and said so on the page:** the two FTC guidance pages, the Operating
Agreement, the disclosure and tracking-ID help articles, Google's two policy pages, the PA-API
deprecation notice and the owner's manuals. Their published values are unchanged and are cited
from the passes that fetched them.

### 17.5 Gates

`build.py` → 36 pages, 0 errors · `verify.py` → 115 pages, 46 spec rows (43 verified, 3
blank+flagged), 34 sources, **0 errors, 0 external warnings** · `platform/tests` → 33/33 ·
`platform/audit/report.py` → clean · `scripts/check_links.py` → 6,413 links, 0 broken ·
`scripts/verify_site.py` → 393 assertions, all passed · `research/check_research.py` → OK ·
`scripts/build_s2_site.py --check` → current · `node --check assets/app.js` → OK · a clean
rebuild leaves `git diff` empty outside the files this pass edited.

### 17.6 What this pass did not do

It did not resolve F1/F2 (which manufacturer model each ASIN ships), F6 (the Associates tag
inside the short links), F3 (the 450 °F conflict) or F4/F5 (the Emeril preset count) — none of
those is answerable from outside the account holder's browser. It did not read IP License §4 end
to end, and said so (F62). It did not change any published value that a source did not
contradict, and it did not touch a single file in `site/`, `s2/`, `data/s2/`, `research/`,
`platform/`, `docs/`, `dashboard/`, `crosscheck/` or `annex-88769516/`.

---

## 18. Pass 10 content pass — session `arena/121929a5-zone1` (2026-11-16)

Complements §17: session 9fccce0c re-verified the register and repaired its cross-references; this
session re-read the wider registry live (short-link resolutions with titles matching stored records
character-for-character; two Amazon detail pages direct, one via the resolver after a bot checkpoint;
all three manufacturer pages; the Chefman 6 Qt manual; OA §5; Program Policies April 14, 2026;
FTC/eCFR), then wrote the five articles the topic queue had planned (TP-07 box contents, TP-08
rotisserie, TP-09 sync modes, TP-10 aerosol-oil care, A-9 disclosure explainer) — article set 12 → 17.
Corrected three stale status rows (TP-04, TP-11, A-11) that disagreed with the already-published
article set, and filled the one verifiable blank (Emeril browse node) from a live official page.
Recorded the same-day S3 finding (schedule now public; Kitchen 4.50% matches the candidate rows).
Full report: [`reports/verification-2026-11-16-121929a5.md`](reports/verification-2026-11-16-121929a5.md);
one-page briefing: [`EXECUTIVE-SUMMARY-PASS10-121929a5.md`](EXECUTIVE-SUMMARY-PASS10-121929a5.md).

## 19. Pass 12 — the design-coherence pass (2026-11-16, session `arena/492acddc-zone1`)

The owner's standing complaint through ten passes was not the copy (the anti-slop rules
have been enforced in the build since pass 9) but the **look**: the stylesheet was three
stacked eras — an admin-dashboard base, an editorial override layer, and commercial
components appended on top — and the sidebar put the owner's thirteen process pages at eye
level for shoppers. Pass 12 rebuilt the presentation layer without touching a single
verified value.

### 19.1 What shipped

| Change | Detail |
|---|---|
| One coherent design system | The 422-line stylesheet was rewritten end to end (one token palette anchored to the brand green `#245746` the favicon already used, warm paper background, serif display type from the Iowan/Palatino/Georgia stack, quiet superscript-style source chips, deep-green footer). Every one of the 116 classes the 29 canonical pages emit is covered. |
| Information architecture | Sidebar regrouped into **Shop smart / Products / Trust & evidence / Owner workspace**; the topbar gained a compact primary nav (Picks · Buying guide · Articles · Compare) plus the verified-data stamp, so shoppers see destinations before process pages. |
| Editorial artwork | Three hand-drawn stroke-only SVG glyphs (dual basket / french-door oven / single basket) on the landing page's format cards — the site's only imagery, drawn for this site so the no-hotlinked-photos rule (D-5) is untouched. |
| Stale count fixed | The landing page said "Compliance — **16** requirements"; the register carries **18** (C17/C18 since pass 10). The count is now read from `data/compliance.json` at build time and cannot drift. |
| Register sync | `data/design-prompt.json`: A-11 corrected `not-written → published` (the contradiction round 11 filed against that register); D-1/D-2 status notes record pass 12; D-10 → `implemented` on measured evidence; the paste-ready design prompt's palette/typography directives updated to the shipped tokens. |

### 19.2 Verification performed

Live reads on 2026-11-16 (evidence: `reports/verification-2026-11-16-492acddc.md`): the
Associates Program Policies page ("Updated: April 14, 2026"; 24-hour session rule verbatim),
the Standard Commission Income Statement ("Kitchen — 4.50%"), FTC Disclosures 101
("November 2019"), and the three brand pages. Both Chefman review counters read **1,307**
and **717** for the third consecutive day — unchanged, so nothing was rewritten. Both open
conflicts (F3 450/400 °F; F4/F5 preset counts) re-confirmed and still open. A WCAG AA
contrast audit measured all 23 foreground/background pairs in the new stylesheet; one
failure (label grey at 2.88:1) was found and fixed during the audit; all pairs now ≥ 4.5:1.

### 19.3 Gates

`build.py` → 41 pages, 0 errors · `verify.py` → 119 pages, 46 spec rows (43 verified /
3 blank+flagged), 34 sources, 0 errors, 0 external warnings · `ci-check.sh` → tests OK,
audit clean, s2 current, 7,135 links / 0 broken · `verify_site.py` → 393 assertions passed ·
`research/check_research.py` → OK · `platform/audit/report.py` → AUDIT PASSED ·
`node --check assets/app.js` → OK · two consecutive builds byte-identical.

### 19.4 What this pass did not do

It did not write or rewrite any article, specification value, compliance row or flag; it did
not touch `site/`, `s2/`, `data/s2/`, `research/`, `platform/`, `docs/`, `dashboard/`,
`crosscheck/`, `annex-*` or `session-*`. The unresolved account-holder questions (product
identity, Associates tag, account approval) are unchanged and still published as such.

## 20. Line-by-line review, live re-verification and the seasonal content pass — 2026-11-16 (session `arena/a746a9f2`, branch `arena/a746a9f2-zone1`)

Task **X-a746a9f2** on the coordination board. This pass answered the brief's three standing
demands — verify everything against official sources with links, keep the site a polished
marketing property rather than an audit report, and leave the owner with a decision layer
instead of more reading — in one integrated sweep. It merged at the same seams as concurrent
rounds 10–11 (sessions `c334fb1c`, `9f0e6668`, `ad8105b3`, `9fccce0c`, `dc3f8b5d`, `3dfe4b45`,
`695f03b7`, `121929a5`, `f3ada6ba` and others); every collision is listed in §19.3.

### 20.1 What was verified (14/14 sources read live on 2026-11-16)

Full evidence table: `reports/verification-2026-11-16-a746a9f2.md` (rows V1–V14: the exact string
read back per row, with the URL and the verdict). Summary:

* **The three supplied short links** re-resolved to the same candidate ASINs (B0CDY277D3,
  B09B7SB46R, B08DKYBTPH) with fallback-style parameters; all three listing titles matched the
  stored values character for character. The 2026-11-15 bot checkpoint on the Emeril listing
  **cleared**: S28 is now read twice over.
* **Four manufacturer pages** (Chefman 6 Qt, Chefman 8 Qt Touch, Chefman 8 Qt High-Fry, Emeril 26 QT):
  every published specification still matches. Every registered conflict is still **live** —
  the 8 Qt model/temperature conflict (F3), the Emeril 24-vs-25 presets (F4) and 10-in-1/11-in-1
  counting (F5), the six-vs-seven accessories (F50).
* **Five Associates pages + FTC + eCFR**: agreement version stamps unchanged (Oct 15 2025 / Apr 14
  2026); commission table read in full with no login (Kitchen 4.50%, All Other 4.00%); the required
  disclosure sentence verbatim; 3-sales/180-days, 10 posts, 60-day recency; "You can't talk about
  your experience with a product you haven't tried"; 16 CFR 255 current as of 11/12/2026.
* **The Emeril "Amazon browse node" cell** — blank behind the checkpoint in this pass's early
  reading — was filled from a live breadcrumb read in V2 of the report; concurrent session
  `121929a5` independently filled the same cell from the same page in pass 10 (convergent, both
  recorded). Spec rows stand at 46 total: 44 verified, 2 blank+flagged — and the two blanks are
  genuine (no preset count is documented for the 6 Qt; the 8 Qt Hi-Fry row is the F3 conflict and
  must stay blank).

### 20.2 What shipped (the marketing and decision layers)

* **One new article** — *Air fryer gift guide 2026: match the format to the person* — this pass's
  seasonal piece, written for the Q4 query window that is open now. Format-first, every value a
  `{{published value}}` splice with its source, and a closing section naming the four things a
  gift guide cannot tell you (price, taste, exact SKU, box contents). Published as **TP-15**.
* **Three new topic rows** (TP-15…TP-17): the gift guide (published), a holiday-hosting capacity
  piece and a deal-season "what a price-free site can still tell you" piece (both proposed, each
  with hooks, intent and must-cite lists). The topics lede count is now computed rather than
  hardcoded.
* **Three new suggestions** feeding the owner's decision queue and the design prompt:
  **SG-24** ship the seasonal cluster while the season is live (options A/B/C, blocked by Q-23);
  **SG-25** one policy-compliant CTA component designed now and wired when the tag exists (the
  component spec the design prompt lacked; blocked by Q-04); **SG-26** a computed "decide this
  first" triage at the top of the queue — the brief's request for decision-making support.
* **Q-23**: who decides the publishing calendar and what the deadlines are — the one missing owner
  statement the seasonal plan needs. "No seasonal content" is recorded as an acceptable answer.

### 20.3 Defects found and fixed, and the merge-seam collisions

* **Stale-count defect class, fourth occurrence** (after F14, F38, F52), published as **F63**:
  three register surfaces asserted "eight articles" while the index had long since outgrown the
  number — `data/questions.json` Q-10, `data/suggestions.json` SG-09, and `data/decision.json`'s
  niche rows. Fixed per the F52 precedent; because the count moved twice at the merge seams
  (concurrent passes published more articles while this one worked), the corrected wording is
  deliberately **count-proof** — "live count on the articles index" — instead of a fresh snapshot
  that would age the same way. The `decision.json` fix is a cross-scope integration edit with
  before/after strings logged in `COORDINATION.md`. `data/design-prompt.json`'s "12 articles"
  status note received the same treatment.
* **F53's stale sentence** (Emeril browse node "cannot be recorded") received a dated update
  recording the checkpoint clearance and the filled row.
* **SG-25 corrected mid-pass after an accuracy check of my own draft**: the first wording claimed
  no page states what a buyer should click; a grep of the rendered pages showed the product pages
  already carry one CTA button ("Open supplied Amazon link — verify model"). The row now states
  the true gap: one ad-hoc CTA on product pages only, none on comparison/guide/picks/article
  pages, and no component spec in the design prompt.
* **Merge-seam ID collisions with concurrent sessions** (kept their rows, renumbered mine — the
  convention every earlier seam used; this pass's rows were renumbered **twice**, once per seam):

  | This pass's draft ID | Final ID | Renumbered at |
  |---|---|---|
  | SG-22 (seasonal calendar) | **SG-24** | seam 1: main's SG-22 (agent terms) · seam 2: main's SG-23 (photography licensing) |
  | SG-23 (CTA component) | **SG-25** | seam 1 (order) · seam 2 (SG-23 taken) |
  | SG-24 (decision triage) | **SG-26** | seam 1 (order) · seam 2 (order) |
  | Q-21 (publishing calendar) | **Q-23** | seam 1: main's Q-21 (agent scope) · seam 2: main's Q-22 (image rights) |
  | flag F59 (stale counts) | **F63** | seam 1: main's F59–F62 |
  | this summary section (§17) | **§19** | seam 1: main's §17 (pass 10) · seam 2: main's §18 (pass 10 content) |
  | `reports/verification-2026-11-16.md` | **`reports/verification-2026-11-16-a746a9f2.md`** | seam 1: main's same-path file (session c334fb1c) |

* Cleared without action: `decision-gate.html` ("14 questions") and `marketing-directions.html`
  ("12 suggestions") are parallel registers whose ledes render their own frozen register length —
  internally consistent; the "16 suggestions" strings in `reverification.html`/
  `executive-summary.html` are historical recounts of already-fixed defects.

### 20.4 What is still open (unchanged, non-blocking)

Q-01/Q-02 (ASIN→model mapping — Amazon serves automated reads a reduced shell with no Product
information block), Q-03/Q-04 (account status; the tag inside the supplied short links), Q-11
(commission category per ASIN — only the Earnings report names it), the owner's country statement
(F42), and the flag-register unification decision (F44/F47). Every one of these remains blank,
flagged and linked on `flagged.html`. Merged-tree gates on 2026-11-16: `build.py` 46 URLs ·
`verify.py` 126 pages / 46 spec rows (44 verified, 2 blank+flagged) / 34 sources / 0 errors ·
`ci-check.sh` 7,587 links / 0 broken · research, site and platform audits clean.

---

<!-- appended by arena/b23f12f0, 2026-11-16 -->

## 21. Verification round 11 — session `arena/b23f12f0`, branch `arena/b23f12f0-zone1` (2026-11-16)

### 21.1 Why there is an eleventh round, and what it covered

Round 10 ran earlier the same day (session `c334fb1c`) and re-read the three short links, the
Program Policies date and the live landing page. It recorded the rest as *not re-read*: the FTC
pages, 16 CFR 255, the brand pages, the manuals and the commission table. This round re-read exactly
that set — **S1, S3, S4, S8, S9, S10, S12, S14, S16, S17, S28, S29, S32, S33** — and added **S35**.
It does not repeat round 10's reads, except that the three short links were re-resolved because the
Emeril destination is load-bearing for the value this round added.

Every value re-read matched its stored record. **No published product value changed.**

### 21.2 The one blank cell that closed

The Emeril "Amazon browse node" row had been blank since 2026-11-15, because three fetches of ASIN
`B09B7SB46R` that day were each answered by Amazon's automated "Continue shopping" checkpoint. Today
the same ASIN loaded on the first attempt and rendered its breadcrumb:
**Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers** — identical to both
Chefman paths. The cell is now filled and cited to S28 and S17, and the stale 'unverified' text that a
parallel fill had left behind - still reading 'Not read ... left blank' on a row that then
carried a value - was removed. Verified specification rows went from 43 to **44**. Session
`121929a5` (pass 10) filled the same cell independently on the same day by the same route and
reached the identical string, so the value now rests on two independent reads rather than one.

**This also corrected a recorded conclusion.** Round 9 had written that the block was "per-ASIN, not
site-wide", because the two Chefman ASINs loaded in the same window. Today the reverse happened:
`B0CDY277D3` — which loaded cleanly yesterday — was served the checkpoint on its first attempt and
returned the listing only on a retry, while the Emeril loaded immediately. The checkpoint is
**intermittent per request**, not a property of the ASIN. That matters beyond the one cell: a failed
fetch is not evidence about a listing, and no future pass should record "blocked" as a fact about an
ASIN. Published as **F65**.

### 21.3 Three defects found by reading the data, not the sources

The brief asks that the site not read like machine-generated filler. Line by line, three places were
publishing the same content more than once:

| Where | What was wrong | Effect on the published page |
|---|---|---|
| `questions.html`, row Q-11 | three "what we know" entries repeated seven times each — 18 entries collapsing to 6 | the sentence *"The same breadcrumb does NOT settle this question"* appeared **14 times** on one page |
| `data/articles.json`, the note field | the opening paragraph repeated verbatim, pipe-joined | the editorial discipline statement printed twice |
| Chefman 8 Qt, "Hi-Fry / 450 °F" row | source S29 cited three times in a row | one claim rendered three identical source badges |

None was a wrong fact — each was the same fact printed repeatedly, which is precisely what makes a
page read as machine-generated. All three were repaired with an order-preserving de-duplication that
changed no wording, and a build guard (`check_register_duplicates()`) now fails the build if any
register list repeats an entry or any register string repeats a sentence. The guard was proven to
fire on an injected duplicate before it was committed (exit 1 injected, exit 0 clean). Published as
**F64**.

### 21.4 New evidence on two conflicts that stay open

The Emeril brand page's own product description, updated **2026-11-16**, now states *"24 one-touch
cooking presets"* and *"Included are 7 premium accessories"* — while the specification block on the
same page still states *"25 Cooking Pre-sets"*, and the Amazon listing title for the same ASIN says
*"Six Cooking Accessories Included"*. So the brand now contradicts itself within one page, and
disagrees with its own listing on accessories.

The site continues to publish 24 presets and 7 accessories on the strength of the manual and the
description text, and **publishes both conflicts rather than reconciling them** — the brand has not
withdrawn the 25, and averaging two official numbers is not verification. Published as **F66**.

### 21.5 What this round refused to publish

The Emeril storefront endpoint reports a variant weight of **27.04 lb / 12,265 g**. It is recorded
as a *candidate* on Q-06 with its source, **not** published as the product weight, because the
endpoint does not say whether that field is the product or the packaged weight — and the same brand
family already shows the two figures diverging for both Chefman models (F51). Q-06's own instruction
is to leave a cell blank rather than convert a shipping weight.

### 21.6 Concurrency record

Two other sessions were active on this repository on the same day. `arena/9f0e6668` (R10) and
`arena/ad8105b3` (Y1–Y4) both touched `build.py`, `data/products.json` and `data/sources.json`.

* **Flag-number collision.** This session had reserved F59 and F60 for its findings; `ad8105b3` had
  already published different rows under those numbers in PR #89. This pass renumbered its three
  flags to **F64, F65, F66** and kept the other session's rows untouched. The duplicate-ID guard
  confirms no flag number now means two things.
* **Both sessions' source stamps were kept.** Each had stamped S10, S12 and S14 on 2026-11-16 with
  different, non-contradictory observations (they read the on-page review counters; this pass read
  the storefront endpoints). Both findings now sit on each source, theirs in `page_version` and
  this pass's in `verified`.
* **A fourth finding was withdrawn rather than duplicated.** This pass also found that
  `check_flag_ids_unique()` had gone blind — it matched zero flag rows and therefore reported
  success while two sessions published different rows under F61 and F62 on the same day. Before
  this pass landed its repair, session `arena/2e346d24` located and fixed the same defect on
  `main`, and added `check_flag_count_matches_page()` for the related fault where the front page
  was advertising zero open flags beside a 61-row register. Their repair is kept; this pass's
  identical fix was dropped, and the finding is recorded as **F67** with the credit stated.
* **Generated HTML conflicts were resolved by regenerating**, not by textual merge — every root HTML
  file is a deterministic product of `build.py`.

### 21.7 Gates and state

`python3 build.py` exit 0 · **46 sitemap URLs** · `python3 verify.py` **126 pages**, 46 specification
rows (**44 verified**, 2 blank+flagged), **35 sources**, 0 errors, 0 external warnings ·
`bash scripts/ci-check.sh` 33 unit tests OK, data audit clean, **7,699 links / 0 broken** ·
`python3 scripts/verify_site.py` **393 assertions, all passed** · `python3 platform/audit/report.py`
AUDIT PASSED, 0 warnings · `python3 research/check_research.py` OK · flag-ID uniqueness: **no
duplicates** · conflict-marker scan across `*.md/*.py/*.json/*.html`: clean.


### 21.8 What remains open

Q-01 (model number per listing — Amazon serves the reduced "Product summary" shell to automated
reads), Q-02/Q-04 (Associates tag — not observable outside Associates Central), Q-11 (commission
rate — only observable in the Associates reports after real sales), and the Emeril product weight.
None was filled by inference.

## 21. Pass 11 — the premise that cost ten passes, and a way to close the decision queue (2026-11-16, session `arena/ba29c641-zone1`)

### 21.1 The finding that matters

Pass 10 recorded at §17.6 that F1/F2 "are not answerable from outside the account holder's browser".
They were. This pass fetched `https://www.amazon.com/dp/B0CDY277D3`, `B09B7SB46R` and `B08DKYBTPH`
and each page's **Product information** block rendered, model rows included:

| ASIN | What the listing states | What the site had held |
|---|---|---|
| B0CDY277D3 | Model Number **RJ38-SQPF-3TDB-2W**, Part Number same, Model Name "Turbo Fry® Touch", 1700 W / 120 V, Max 450 °F · Min 93 °C, 13.38″ × 11.81″ × 10.63″, 13.3 lb, Capacity field "6 liters", UPC 810087845025 | Model from the brand page and the manual only, with the caveat "Amazon does not publish the model number on the ASIN" |
| B08DKYBTPH | Part Number **RJ38-SQSS-8T**, Model Number row holding the marketing string "Large Air Fryer", 1700 W / 120 V, Max 400 °F · Min 94 °C, 12.75″ × 13.5″ × 10″, 12.8 lb, Warranty "1-Year Limited Warranty", UPC 816458024518 | Model from the brand page and the manual; the 450 °F row blank because two sites disagreed |
| B09B7SB46R | Model Number and Part Number **4-00675-02X-VN**, Min 75 °F · Max 500 °F, 1700 W / 120 V, 16.9″ × 15.8″ × 14.8″, Configuration "…24 Functions and 7 Accessories", Included Components enumerating six named parts, UPC 752356835682 | Model FAFO-001 (manual) / 4-00675-02A-VN (brand page); browse node blank because three 2026-11-15 fetches hit a checkpoint page |

Read in full: **F68** (`flagged.html#f68`). The correction is narrower than it looks and worth
stating twice. What closed is the ASIN-to-model step, for all three products. What did **not** close
is the supplied-link-to-ASIN attribution: the three `link.amazon` tokens are still nine characters,
still not ASINs, and still arrive through `plpRedirect=mhFallback` (F6, F7, F10 stand). No sentence
on this site now says the listing hides its model number; the register's F1 was corrected rather
than deleted, so the wrong premise stays visible in the file that carried it.

### 21.2 Four conflicts this pass found, and did not resolve

* **F69** — the 8 Qt's footprint: brand page 15.4 × 12.6 × 13.5 in, its own listing 12.75 × 13.5 × 10
  (S12 vs S29); and the 6 Qt's listing Capacity field reading "6 liters" where its title, its Size
  field and the brand page all read 6 quarts.
* **F70** — three official model strings for the Emeril, the newest two one character apart
  (`02A-VN` on the brand page, `02X-VN` on the listing, `FAFO-001` in the manual).
* **F71** — the Emeril listing contradicts itself about the box: "7 Accessories" in its Configuration
  field, six parts enumerated in its Included Components row, "Six" in its title. The same fetch made
  the 24-presets side of F4 stronger, so one read moved two rows in opposite directions.
* **F72** — °C floors that do not convert to the °F floors on two products (93 °C vs 95 °C; 94 °C vs
  200 °F): rounding across documents, published as each source states it, never merged.

Prices, availability, star ratings, review counts and the Best Sellers Rank line were all visible in
these fetches and are **not** on the site: Program Policies §2(b) and §6(t) for the first three
(`data/products.json` `amazon_price_policy`), and this repository's own reading of IP License §2(e)
for rank data, which stays a decision not to publish rather than a claim that no such figure exists
(that wording was corrected in the s2 register, R-03).

### 21.3 Two gates repaired, one of which could not fail

`.github/workflows/ci.yml` and `scripts/ci-check.sh` both ran `build_s2_site.py` (which writes) and
then `--check` (which compares a rebuild with the files the previous line had just produced). The
step titled *"Prove the committed HTML is current"* therefore could not report staleness. It now runs
`--check` alone, tolerating only the header's build date, which is derived from git and unreadable
from a shallow checkout; the stamp itself was also converted in UTC, because `git log --format=%cs`
had been stamping one commit 2026-11-16 in UTC and 2026-11-17 in JST. Proof the repaired gate fires:
one changed word in `s2/pages/sources.html` → `STALE BUILD`, exit 1.

**F60 was repaired at source**: `data/s2/requirements.json` R-01 now names both registers and the
paths that exist, R-08 restates the blocker as the ASIN-to-commission-category mapping with the
public Commission Income Statement as its source, and R-03's "no public demand metric exists" was
corrected to the reason that is actually true here.

### 21.4 The decision queue now has a closing mechanism

`suggestions.html` held a growing reviewed queue (23 rows at the time of writing, 26 after the merge with the seasonal pass) and no way to finish one. `decision-log.html` is new:
one picker per suggestion, the register's own recommended path, and a computed *adopt-after-silence*
default — reversible, risk none-or-low, and no `unknowable` blocking question. **The split is computed on the
page, not typed here: today 16 rows carry a default a later pass may implement without asking, 8 wait for a
person, and 2 are recorded done.** The rule is read from `data/suggestions.json` and `data/questions.json` at
build time, so the page cannot promise a default its own data does not support, and the same computation
prints the ordered queue the next pass works through.
Silence never authorises spending, account actions, credential changes, a price or rating, a
compliance posture, or any flagged product fact — that limit is printed on the page. A choice is
exported as the body of `data/decision-log.json`, whose `choices` array is empty by design: a session
that filled it would be inventing an instruction. Q-01 and Q-02 moved from `missing` to `known`
because this pass answered them from the listing read, and SG-01's "five minutes in a browser" is
closed as unnecessary.

### 21.5 What pass 11 did not do

It did not touch `articles/`, `data/articles.json` or `data/topics.json` — the two open PRs on the
board (#94, #95) own that ground, and a third copy of the same source ledger was the last thing this
repository needs. It did not delete the five stale root briefings; it put a pointer on each (F59's
disposition). It did not fill the two remaining blanks, did not assert a commission rate per ASIN, and
did not state what either contradicting document "really" means. `python3 verify.py` reports
**127 pages, 77 spec rows (75 verified, 2 blank and flagged), 35 sources, 0 errors, 0 external warnings**;
`scripts/check_links.py` reports **8,096 links, 0 broken**; `scripts/ci-check.sh`, `scripts/verify_site.py`
and `research/check_research.py` all pass; a clean rebuild leaves `git status` empty.

### 21.6 One more instance of the defect this repository keeps finding

While updating the requirements register for this pass, its own preamble was checked against its own rows:
the file promises "counts are computed from the rows at build time rather than typed, so this page cannot
claim a total the register does not contain", and then types eight counts into prose — 46 spec rows, 21
suggestions, 20 questions, a 37-URL sitemap, 33 unit tests, 15 guards, 27 banned phrases, five stale
briefings. All eight had drifted or were one edit from drifting. They are now `{}`-tokens substituted by
`req_interp()` from the same objects the pages render from, an unknown token raises, and
`check_requirement_tokens()` fails the build if a token survives into a page (both directions tested).
Recorded as **F73**.

---

## 22. Pass 12 (session `arena/8874422b-zone1`) — RSS syndication, article masthead and the second-reader spot re-read (2026-11-16)

*(Numbered §22 because two earlier sessions had each already taken §21 — their duplicate is left
as published; this session did not renumber another session's section.)*

**Branch:** `arena/8874422b-zone1` · rebased three times onto a moving `origin/main`
(final base `d5f449d`) · **Full evidence:**
[`reports/verification-2026-11-16-8874422b.md`](reports/verification-2026-11-16-8874422b.md) ·
**Ledger on the site:** [`reverification.html`](https://kanlerxz87-cyber.github.io/Zone1/reverification.html)

This session claimed a marketing-design polish pass while three other design/content sessions
worked in parallel. Their passes (§19 design-coherence, §20 seasonal, §21 round 11 and pass 11)
merged a reader strip, a single-era stylesheet, SVG glyphs, a nineteen-article set and — via
session `ba29c641` — direct reads of all three listings' Product information blocks that closed
F1 for two of three products. **Shipping two competing design systems would have made the site
worse**, so this branch rebased onto their result each time, adopted it wholesale as canonical,
and re-scoped its contribution to the additive pieces the merged tree still lacked —
presentation-only throughout: **no published value, register row, flag or wording changed.**

### 22.1 What this session added to the merged tree

| Addition | Where | Status |
|---|---|---|
| **RSS feed** `feed.xml` (19 items), generated deterministically from `data/articles.json` — pubDate derives from the register's own accessed date, so CI's reproducibility gate holds; linked from every page head (`rel="alternate"`), the articles index and the footer | `build.py` `main()`; `feed.xml` | shipped; reviewable as **SG-28** |
| **Article masthead**: kicker, headline, standfirst and a meta row (kind · reading time · sources-read date · a "documentation-based — no hands-on testing" badge), styled with the shipped stylesheet's own variables | `page_article()`, additive CSS block | shipped |
| **Footer brand column** naming the publisher and the feed; RSS link in the sources column; `theme-color` meta | `layout()` | shipped |
| **Second-reader spot re-read** of the load-bearing rows (below), rendered as its own ledger section and wired into the executive summary's ledger-row count | `session-8874422b/pass12.json` | shipped, with a dated addendum noting that session `ba29c641`'s later direct reads moved the model-mapping rows (F1 closed 2/3; Emeril part-number conflict opened as **F70**) |
| **Suggestion rows SG-27–SG-30** (nav-label review, feed, Search Console submission, reader-capture decision — numbered after main's SG-23–26) | `data/suggestions.json` | published |

**SG-27** deliberately asks for a review of the shipped shopper-strip labels
(Picks · Buying guide · Articles · Compare) against a six-item alternative (add Products and The
data) rather than changing them — the design system is `492acddc`'s; this session reviews, it does
not re-litigate.

### 22.2 The spot re-read — a second reader on the same day

Earlier the same day, sessions `3dfe4b45`, `492acddc`, `b23f12f0` and `ba29c641` covered the
register. This pass adds what a second independent reader confirms fresh: the three supplied
`link.amazon` short links (all resolving to `/dp/B0CDY277D3`, `/dp/B09B7SB46R`, `/dp/B08DKYBTPH`
through `plpRedirect=mhFallback` fallback pages), the two volatile Chefman counters (**1,307** and
**717** — unchanged), the Emeril 24-vs-25 preset conflict (re-confirmed live on one page), and the
Program Policies stamp (**Updated: April 14, 2026** — unchanged). **All seven rows: confirmed.**
Still open, unchanged by this pass: the Associates tag inside the links (F6), the Emeril
part-number variant (F70), and the preset-count conflict (F4/F5 family).

### 22.3 Gates (on the final rebased tree)

`python3 build.py` → exit 0, **48 pages**, 47 sitemap URLs + **feed.xml (19 items)** ·
`python3 verify.py` → 127 pages, 77 spec rows (75 verified / 2 blank+flagged), 0 errors,
0 external warnings · `bash scripts/ci-check.sh` → 33 unit tests OK, data audit clean, s2 build
current, **8,287 links / 0 broken** · `python3 scripts/verify_site.py` → 393 assertions, ALL
PASSED · `python3 research/check_research.py` → OK · `python3 platform/audit/report.py` →
AUDIT PASSED · `node --check assets/app.js` → OK · two consecutive `build.py` runs produce
byte-identical HTML.

The merge record for this pass is appended to `COORDINATION.md` after the PR lands.

## 23. Marketing & decision-support pass — session `arena/19d92a81`, branch `arena/19d92a81-zone1` (2026-11-16)

*(Numbering note: two earlier sections both claim §21 and were left as written by their
sessions; this section is numbered 23 to stay unique.)*

**The brief this pass answered:** make the site read like a polished marketing affiliate
publication with catchy, trend-aware, product-related articles that can earn organic traffic —
"not AI slop" — while every claim stays inside the sourcing rules; and keep the decision-support
layers (suggestions, questions, design prompt) current so the owner chooses the path before
anything changes.

**Shipped (all source-led, all gates green):**

* **Two seasonal articles** in the article set (now 21 rows, 2026-11-16): *The Black Friday
  model-number switch, and the three-minute check that catches it* — a deal-safety investigation
  built entirely on this repository's own documented listing conflicts (fulfils the proposed
  TP-17), and *How to clean an air fryer, according to the people who made it* — the three
  manuals' cleaning sections quoted side by side (new TP-18). A third seasonal piece (gift guide)
  was drafted and **dropped at merge** in favour of the parallel pass's already-published
  `air-fryer-gift-guide-2026`; two gift guides would be the duplication this register exists to
  prevent.
* **Decision support:** five new reviewable suggestions (**SG-27..SG-31**: production-method
  authorship, brand consolidation, Creators-API re-planning, an owned zero-data channel, and a
  four-cluster map) grouped into decision path **P5 — "Make it read like a publication"**, which
  also carries the parallel pass's SG-23..SG-25; three new open questions (**Q-24..Q-26**:
  who signs off on the queue, the brand name, and which API the automation platform calls) each
  with its discovery step; and a **marketing & organic-traffic addendum** to the paste-ready
  design prompt (rows D-11/D-13, A-12/A-14/A-15, T-9..T-12, V-5..V-7, R-7/R-8) — the
  "suggestions that feed the prompt" the brief asked for. Nothing on the suggestion queue is
  implemented; the owner still picks.
* **Verification round 12** (`reports/verification-2026-11-16-19d92a81.md`): the three supplied
  `link.amazon` links re-read live and matched to their recorded candidate ASINs
  (B0CDY277D3 / B09B7SB46R / B08DKYBTPH — identity still *unconfirmed*, caveat unchanged);
  S26 and the full S15 manual (including the Cleaning & Storage section) re-read verbatim.
* **One new irregularity, flagged not guessed:** `articles/sync-finish-two-buttons.html` is
  published outside the data-driven article set (**F74**), with the register-or-delete decision
  left to the owner. README's stale article count fixed with a dated snapshot.

**Merge reconciliation (logged in COORDINATION.md):** this session's branch met four parallel
passes mid-flight. Their published work won where it landed first (gift guide, nav/style pass,
SG-23..26, Q-22/23, TP-15..17); this session's unique work was renumbered and its
cross-references rewritten; every dropped duplicate is named in the log. The session's own
rebase conflict briefly committed conflict markers into COORDINATION.md (`7c6806f`) — the F22
class — repaired within the session (`3e4859f`) and logged.

**State at the end of this pass:** `build.py` exit 0 (48 sitemap URLs, every guard green) ·
`verify.py` 128 pages, 46 spec rows (44 verified, 2 blank+flagged), 35 sources, 0 errors ·
`ci-check.sh` 7,958 links, 0 broken.


## 24. Monetisation and measurement pass — session `arena/3093e674-zone1` (2026-11-17)

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
