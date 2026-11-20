# Verification and repair record — 2026-11-20 · arena/761c3c2e-zone1

**Scope.** One reader-facing pass on the canonical publication: re-read the five supplied
Amazon short links and the official sources the changed pages rely on, repair two published
defects that could be verified from the repository itself, add a dated editorial-policy page,
add two regression gates, rebuild, and run the full gate suite.

**Base commit:** `1c7de82` (`main` after PR #185). **Branch:** `arena/761c3c2e-zone1`.

---

## 1. What was read live in this session

Every URL below was fetched during this session. Nothing in this table is recalled from an
earlier pass. It is also recorded machine-readably as
`data/sources.json → reverified_2026_11_20_761c3c2e`.

| Ref | URL | What was observed |
|---|---|---|
| S17 | https://link.amazon/B04G1MEwY | Resolved to `/dp/B0CDY277D3`, title `CHEFMAN 6 Quart Dual Basket Air Fryer Oven … Sync Finish, Hi-Fry …`. Matches the stored PI-01 observation. |
| S28 | https://link.amazon/B02NbDxp3 | Resolved to `/dp/B09B7SB46R`, title `Emeril Lagasse 26QT French Door … 24 One-Touch Preset Options … Six Cooking Accessories Included`. Matches PI-02. |
| S29 | https://link.amazon/B00hJ57DV | Resolved to `/dp/B08DKYBTPH`, title `Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option …`. Matches PI-03. **F106's homepage fallback was not reproduced in this read**; F106 stays recorded as an observation of that pass, not as a present-tense claim. |
| S36 | https://link.amazon/B0c8moW59 | Resolved to `/dp/B0DHZTCNR5`, title ending `… Stocking Stuffers Gifts for Men, Black`, with a `$16.99` price block. The 2026-11-19 record did not name a colour. → **F112** |
| S37 | https://link.amazon/B0f3GKalj | Resolved to `/dp/B0DZFD6R9Z`, title `CHEF iQ Sense … 3 Ultra-Thin Probes … Gen3`; the served page URL carried an `sbo` sale parameter absent from the previous redirect. → **F112** |
| S16 / S28b / S29b | `/dp/B0CDY277D3`, `/dp/B09B7SB46R`, `/dp/B08DKYBTPH` | Product detail pages rendered; breadcrumb `Home & Kitchen › … › Fryers › Air Fryers` (leaf node 17659096011). |
| S36b | `/dp/B0DHZTCNR5` | Detail page rendered; breadcrumb `… › Thermometers & Timers › Meat` (node 289810). |
| S10 | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | `6 Qt / 5.67 L`; `200–450°F / 95º-235ºC`; `13.38 × 11.81 × 10.63 in`; `1700W/120V`; model `RJ38-SQPF-3TDB-2W`; "Max temp: 450ºF with Hi-Fry function". |
| S12 | https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1 | "Max temp: **400ºF**/205ºC"; range `200–400°F`; 8 Qt dimensions `15.4 × 12.6 × 13.5 in`; model `RJ38-SQSS-8T`. **The 450 °F figure appears only in the Amazon listing title, not on this page** — the published conflict is correct as written. |
| S14 | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | Specification block prints **`25 Cooking Pre-sets`** beside `26-Quart Capacity`, `16.9"D × 15.8"W × 14.8"H`, `120 volts`; the body copy says **`10-in-1`**; the Amazon title says **24 presets**. Three official artefacts, three numbers. Retained as published, not reconciled. |
| S31 | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links | "Mark links that are advertisements or paid placements (commonly called *paid links*) with the `sponsored` value"; multiple `rel` values allowed. |
| S8 | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | "Place it so it's **hard to miss**"; "The disclosure should be placed with the endorsement message itself"; "You can't talk about your experience with a product you haven't tried". |
| S9 | https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255 | 16 CFR Part 255 displayed "up to date as of 11/18/2026"; §§255.0–255.6 present including 255.5 *Disclosure of material connections*. |
| S3 | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | Table 1: `Physical Books, Kitchen, Automotive — 4.50%`; `All Other Categories — 4.00%`. |
| S23 | https://kdp.amazon.com/en_US/help/topic/G200652190 | Page title `Linking from Your Website`. **The "10-character Amazon Standard Identification Number" sentence was not in the fetched portion of this page in this session.** Recorded as not re-confirmed rather than re-asserted. |

**Deliberately not fetched in this pass, and therefore not re-asserted:** S1 (Operating
Agreement) and S2 (Program Policies). No policy claim was added or edited, and the disclosure
sentence already on every page was not rewritten, so the pass does not depend on a fresh read
of either. This is recorded so the next pass knows exactly which claims carry which date.

---

## 2. Defects found and repaired

### D-1 · The reading badge was a constant, not an estimate  → **F113 / ET-1 / ET-4**

*Before:* all 26 article pages printed `3 min read`. The value came from a single literal in
`data/articles.json`, not from the text. Measured prose (placeholders rendered, headings,
specifications and source lines excluded) runs **162–382 words** per guide.
*After:* each page prints its own count, computed at build time by `article_word_count()`,
with an assumed 200 wpm **labelled as an assumption** in the visible copy and in
`data/editorial-trust.json`.

The honest consequence is recorded rather than hidden: at 200 wpm these guides are a
one-to-two-minute read, i.e. shorter than the badge used to advertise. Padding them to match
an old number would have been the wrong repair, so the short length is published as ET-4 and
the question of lengthening a guide is left to the owner.

*Gate:* `test_reading_badge_is_computed_per_article_not_a_constant` — asserts the printed
number equals the computed number for every article, that at least six distinct counts exist
across the set (so a reinstated constant fails), and that no `min read` string survives.

### D-2 · No reader article linked to a product page  → **F113 / ET-2**

*Before:* a count over the generated files found **zero** occurrences of a product-page path
or an Amazon URL across all 27 reader articles. A reader who finished a comparison had no next
step on the page — while every product page already linked back to articles.
*After:* each guide closes with a quiet **"Model pages for what this guide discusses"** block
built from that guide's own `products` field, naming the product's short name, the first
specification field cited, and its source id, under the standing wording *"Documentation pages,
not a recommendation or a test. Intended Amazon listings are unconfirmed."*

Deliberately **not** used: a row of purchase buttons. The linked pages are documentation
surfaces; styling them as a recommendation would assert something this publication does not do.

*Gate:* `test_every_guide_links_to_the_models_it_discusses`.

### D-3 · Typography floor  → **ET-3**

The byline strip, footer link lists, source notes and card captions were set at 9–11 px. These
are exactly the lines that carry authorship, source dates and the footer index. Raised to 12 px
(`publication/theme.css`, 6 rules). No published value changed.

**Not done, and recorded as not done:** no colour token was touched. The palette was measured
against WCAG 2.x contrast in this pass and already passed on 18 of 18 tested pairs (lowest:
5.35:1, footer muted text; disclosure bar 6.64:1; body ink 11.86:1). Claiming a contrast
improvement would have been false.

### D-4 · New console error caught by the existing gate

Adding `how-we-research.html` to `PUBLIC_INDEX_PAGES` made it analytics-eligible, and
`test_collector_page_allowlist_matches_every_eligible_rendered_page` immediately failed:
`allowed_page_ids()` did not contain the new id, so the browser client would have emitted
`page_view` events the collector rejects. The two lists were moved together (`analytics/
collector.py`). This is a good example of the existing gates doing their job — it was caught
by CI, not by review.

---

## 3. New page

`how-we-research.html` — indexable, in `sitemap.xml`, linked from the masthead workspace
menu and the footer index. Generated from `data/editorial-trust.json`, so the date, the
method steps and the correction list are data. It states the method, the 2026-11-20 source
reads with their source chips, the four corrections (ET-1…ET-4), and an explicit
"what this edition did not change" list.

**Design note.** The method and correction blocks are rendered as **lists, not tables**, on
purpose: on this site a table means "a value with a primary source", and the build correctly
refuses a table row without one. Cramming a policy statement into a table shape to look like
data would have been the wrong call — and the build guard flagged it, which is the guard
working as designed.

---

## 4. Irregularities flagged for review

| Flag | Severity | Item |
|---|---|---|
| **F112** | Low | The two thermometer short links serve a colour variant (B0DHZTCNR5, Black, with a companion Orange listing B0GL7Z4KP4 in the same rail) and an `sbo` sale parameter that the 2026-11-19 record did not carry. No stored observation was overwritten; intended-ASIN fields stay blank. |
| **F106** | (existing) | Not reproduced in this session's read of B00hJ57DV. Left as the record of the pass that observed it. |
| **F113** | Medium, repaired | D-1 and D-2 above; kept on the public flag register because the *length* finding (ET-4) is an open editorial question for the owner. |
| S23 | note | The ASIN definition sentence was not present in the fetched text today. No new ASIN claim was made; the existing `product-intent.json` note rests on earlier passes. |

---

### Flag-numbering note (rebase of 2026-11-20)

These two rows were drafted as **F107/F108**. While this branch was open, PR #188
(`arena/b6891e75`) merged its own **F107** (the S17 scope sentence) and **F108** (orphaned
`picks.html`) to `main` first. A flag id is a citation target, so re-using a merged id would
point two findings at one anchor. The rows were renumbered to **F112/F113** on rebase, with no
change to their substance. `build.py` carries the same note in a comment above the rows, in the
form `arena/69c1201a` used for F110. Rebase conflicts were resolved keep-both: `main`'s
F111/F107/F108 rows, `data/product-intent.json` and `EXECUTIVE-SUMMARY.md` appendix were kept
verbatim, and `data/sources.json` was rebuilt from `main`'s file with only this session's dated
entry appended (+107 lines, one key added, nothing removed).

## 5. Gates run (this tree, after all changes)

| Gate | Result |
|---|---|
| `build.py` | 64 pages, **42** sitemap URLs, 26 feed items, deterministic |
| `verify.py` | 142 pages, 77 spec rows (75 verified, 2 blank+flagged), 49 sources, **0 errors**, 0 external warnings |
| `python3 -m unittest discover -s tests` | **78** tests (75 before; +3 new), OK |
| `node --test tests/*.test.cjs` | **14** pass, 0 fail |
| `platform/tests` | 33 tests OK |
| data audit | clean |
| `build_s2_site.py --check` | build current: 16 files |
| `check_links.py` | **13,088** links OK (was 12,674 — the new guide→model links and policy page) |
| `research/check_research.py` | OK — no broken links, no unsourced rows, disclosures on every page |
| `scripts/verify_site.py` | 393 assertions, ALL CHECKS PASSED |
| `historical_compliance.py --check` | 61 frozen files unchanged |

**Structural checks re-run on the canonical scope (74 → 76 pages):** no duplicate `<title>`,
no duplicate meta description, no duplicate canonical, exactly one `<h1>` per page, zero
`<img>` without `alt`.

---

## 6. Boundaries re-stated, not re-earned

`shopnow047c-20` stays recorded, unvalidated and unapplied. No intended ASIN, listing URL,
confirmation date or source was filled in. No short link is called valid or invalid. Production
analytics stays off. The campaign ledger stays empty. No price, star rating, review count, traffic
figure, conversion rate or revenue forecast was added. No hands-on testing is claimed anywhere.
