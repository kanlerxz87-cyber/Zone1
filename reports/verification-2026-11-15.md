# Verification record — 2026-11-15 (session arena/792c279e-zone1, task T20)

Every row below was fetched live on **2026-11-15 (UTC)** during this session. The source
column is the exact URL requested. "Read back" quotes the string that was found on the page
at that URL; where the string differs from what the site publishes, the row says so.

Discipline: nothing is inferred. A value that could not be re-confirmed is recorded as
**not re-confirmed**, and the published value is left unchanged with a flag rather than
"fixed" from memory or from a secondary source. This sandbox has no direct egress; pages were
read through a server-side fetch that returns the page's own text, so a "live" read below is
a read of the publisher's response on that date, not a screenshot of a logged-in browser.

## 1. Amazon Associates — program facts

| # | Fact checked | Source (official) | Read back on 2026-11-15 | Verdict |
|---|---|---|---|---|
| V1 | Disclosure sentence required on the Site | https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98 | "the Operating Agreement requires that the following statement clearly and conspicuously appears on your Site: 'As an Amazon Associate I earn from qualifying purchases.'" | **Confirmed** — matches the sentence in `build.py` (`DISCLOSURE`) and on every page |
| V2 | Link-level disclosure must be clear **and** conspicuous | same (S5) | "your link-level disclosure must be: 1. **Clear.** … '(paid link)', '#ad', or '#CommissionsEarned'. 2. **Conspicuous.** It should be placed near any affiliate link or product review…" | **Confirmed** — the site's `paid-tag`/`cta-note` sits with each product CTA |
| V3 | Contribution to the Associates Program does not require a purchase for disclosure purposes | — | not assessed | n/a this pass |
| V4 | Application review: qualifying sales threshold | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM | "we require at least three within the first 180 days" ; "personal orders do not qualify" | **Confirmed** |
| V5 | Application review: content recency for websites | same (S4) | "Content on your website must be recent (generally within the last 60 days). You must own your website." | **Confirmed** — new content dates in this pass are 2026-11-15 |
| V6 | Application review: minimum content volume | same (S4) | "All Sites must have robust original content (even when advertising is removed) – a good rule of thumb is at least 10 posts." | **Confirmed** |
| V7 | Application review: social follower threshold | same (S4) | "substantive number of organic followers/likes (in most cases, at least 500)" | **Confirmed** |
| V8 | Application rejection is final | same (S4) | "Unfortunately, we aren't able to reassess an application once it's been rejected." | **Confirmed** — this is why the hand-over page puts the tag/eligibility check before promotion |
| V9 | Kitchen category fixed commission rate | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | Table 1, row "Physical Books, Kitchen, Automotive" → "4.50%" | **Confirmed** |
| V10 | Catch-all category rate | same (S3) | Table 1, row "All Other Categories" → "4.00%" | **Confirmed** |
| V11 | Whether *these three ASINs* are in the Kitchen category | — | Amazon does not publish a category-to-ASIN mapping on any public page read in this pass, and no signed-in Associates report was available | **Unverified** — remains flagged (F02) |
| V12 | Associates Program Policies page version | https://affiliate-program.amazon.com/help/operating/policies | "**Updated:** April 14, 2026." | **Confirmed** — the site's earlier copy recorded an older version string; see flag F44 |
| V13 | Associates Operating Agreement page version | https://affiliate-program.amazon.com/help/operating/agreement | "**Updated:** October 15, 2025" | **Confirmed** — matches `data/sources.json` S1 `page_version` |
| V14 | Tracking IDs / sub-tags exist and are per-account | https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA | "With tracking IDs, Associates can analyse the performance of various Web sites … Each ID would generate earnings for his Associates account storeid-20." | **Confirmed** — supports the measurement plan's `?tag=` / sub-tag recommendation, and cannot confirm the tag inside the supplied short links |
| V15 | Commission is calculated on Qualifying Revenue, not gross price | https://affiliate-program.amazon.com/help/operating/policies (Commission Income Statement §1) | Session measured as "at least 24 hours" from the click, and purchase within "89 days" of the initial click-through | **Confirmed for the definitions quoted** — the site's calculator already states this |

## 2. US law — endorsement disclosure

| # | Fact checked | Source (official) | Read back on 2026-11-15 | Verdict |
|---|---|---|---|---|
| V16 | A financial relationship must be disclosed | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | "Disclose when you have any **financial, employment, personal, or family relationship** with a brand." | **Confirmed** |
| V17 | Placement rule | same (S8) | "Place it so it's **hard to miss**. The disclosure should be placed with the endorsement message itself." | **Confirmed** — the site's disclosure bar is sticky above the header on every page |
| V18 | Cannot claim experience you do not have | same (S8) | "You can't talk about your experience with a product you haven't tried." | **Confirmed** — the reason every page states no hands-on testing was performed |
| V19 | Binding rule text still 16 CFR Part 255 | https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255 | "Displaying title 16, up to date as of 11/12/2026." Table of contents lists §255.0–§255.6 including "§ 255.5 Disclosure of material connections." | **Confirmed** — the part has not been re-organised since the 2023 revision (source note: 88 FR 48102, July 26, 2023) |

## 3. The three supplied links and the three Amazon listings

| # | Fact checked | Source (official) | Read back on 2026-11-15 | Verdict |
|---|---|---|---|---|
| V20 | Where `https://link.amazon/B04G1MEwY` lands | https://link.amazon/B04G1MEwY | Redirect target `https://www.amazon.com/dp/B0CDY277D3?lv=shuf&…&plpRedirect=mhFallback`; page `<title>` "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black" | **Destination confirmed again** (seventh session over three days, same ASIN). **Identity of the model still unconfirmed** (F1/F2/F32) |
| V21 | Where `https://link.amazon/B02NbDxp3` lands | https://link.amazon/B02NbDxp3 | `https://www.amazon.com/dp/B09B7SB46R?…plpRedirect=mhFallback`; `<title>` "Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included" | **Destination confirmed again.** Two new observations: the title now says **"24 One-Touch Preset Options"** (F29 narrowed, still conflicting with the brand page's "25 Cooking Pre-sets"), and **"Six Cooking Accessories Included"** conflicts with the site's *Included accessories: 7* row — flag **F45** |
| V22 | Where `https://link.amazon/B00hJ57DV` lands | https://link.amazon/B00hJ57DV | `https://www.amazon.com/dp/B08DKYBTPH?…plpRedirect=mhFallback&th=1`; `<title>` "Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel" | **Destination confirmed again.** The title's "450°F Hi-Fry … Bake, Dehydrate, Frozen" matches **RJ38-8T-BLACK** exactly, while "Stainless Steel" matches RJ38-SQSS-8T — F33 unchanged and now the single most consequential open item |
| V23 | Associates tag on any supplied link | the three landing URLs above | No `tag=` parameter appears in any of the three landing URLs | **Still absent** — F3 stands. A tag can be visible in the landing URL in the normal case, so this is evidence, not proof; the account holder can settle it in one look at Associates Central |
| V24 | The Model number shown in each listing's "Product information" block | the three `/dp/` pages | The text returned for the three pages in this pass did not include a "Product information" table; it returned the buy-box, protection plans and "Customers who viewed this item also viewed" blocks | **Not retrievable this pass** — F1/F32/F33 stay open. The hand-over page gives the exact 3-step way for the owner to close them |
| V25 | Whether `link.amazon` is an Amazon-published short domain | — | No Amazon-owned page naming `link.amazon` as its shortener was found in this pass | **Unverified** — F16 stands |

> **Note on V24.** This is the one fact that would close three flags at once, and it is the one
> fact a headless fetch reliably cannot see. The site says so plainly rather than guessing.
> Nothing on this site depends on the answer: every product page shows the candidate ASIN, the
> manufacturer SKU the site *believes* it maps to, and the caveat.

## 4. Manufacturer specifications — Chefman

| # | Product | Field | Source (official) | Read back on 2026-11-15 | Verdict vs published value |
|---|---|---|---|---|---|
| V26 | Chefman 6 Qt Dual Window | Model number | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | "Model Number: RJ38-SQPF-3TDB-2W" | **Confirmed** |
| V27 | Chefman 6 Qt Dual Window | Capacity | same (S10) | "Capacity: 6 Qt / 5.67 L" | **Confirmed** — matches "6 Qt / 5.67 L" |
| V28 | Chefman 6 Qt Dual Window | Temperature range | same (S10) | "200–450°F / 95º-235ºC temperature range" and feature "Max temp: 450ºF/ 235ºC with Hi-Fry function" | **Confirmed** — matches "200–450 °F / 95–235 °C" |
| V29 | Chefman 6 Qt Dual Window | Dimensions | same (S10) | "Dimensions: 13.38 in x 11.81 in x 10.63 in / 33.98 cm x 30 cm x 27 cm" | **Confirmed** |
| V30 | Chefman 6 Qt Dual Window | Weight | same (S10) | "Weight: 13.3 lbs / 6.03 kg" | **Confirmed** |
| V31 | Chefman 6 Qt Dual Window | Power | same (S10) | "Power: 1700W/120V" | **Confirmed** |
| V32 | Chefman 6 Qt Dual Window | Safety approval / warranty | same (S10) | "cETL approved with a 1-year Chefman® assurance" | **Confirmed** |
| V33 | Chefman 6 Qt Dual Window | Number of presets | same (S10) | The page's Features block lists Hi-Fry, Sync, nonstick baskets, interior light, dual windows, matte black. No food-preset count is stated. | **Remains unverified** — published row is `None` + unverified, which is the correct shape; F30 narrowed |
| V34 | Chefman 6 Qt Dual Window | Brand-site rating snapshot | same (S10) | "1305 Reviews" / "4.6" / "1305 Total Reviews" | **Confirmed as a dated snapshot** — 1,305 on 2026-11-15, unchanged since 2026-11-14 (F19's volatility warning still applies) |
| V35 | Chefman 8 Qt (the SKU the site maps) | Model / capacity / temperature / dimensions / weight / power | https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1 | "Model Number: RJ38-SQSS-8T (8 Qt model)"; "Capacity: 5 Qt or 8 Qt / 4.73 L or 7.57 L"; "200–400°F / 95º-205ºC temperature range"; "Dimensions: (8 Qt Model) 15.4 in x 12.6 in x 13.5 in"; "Weight: (8 Qt Model) 12.8 lbs / 5.8 kg"; "Power: 1700W/120V" | **Confirmed** — every published 8 Qt row still matches its cited page |
| V36 | Chefman 8 Qt (the SKU the site maps) | Brand-site rating snapshot | same (S12) | "716 Total Reviews", "4.6" | **Confirmed as a dated snapshot** — unchanged since 2026-11-14 |
| V37 | Chefman 8 Qt **second SKU** | Model / Hi-Fry / functions / power | https://chefman.com/collections/air-fryers-1/products/turbofry-8-qt-air-fryer-w-high-fry | "Model Number: RJ38-8T-BLACK"; "Hi-Fry Temperature: 450°F / 232°C"; "4 Cooking Functions: Air fry, bake, dehydrate, and frozen"; "1700W/120V"; "cETL approved with a 1-year assurance from Chefman" | **Confirmed** — this is the SKU whose wording matches the supplied 8 Qt listing title. The site does **not** assert either mapping; F33 records the ambiguity |

## 5. Manufacturer specifications — Emeril Everyday

| # | Field | Source (official) | Read back on 2026-11-15 | Verdict vs published value |
|---|---|---|---|---|
| V38 | Model code on the brand page | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | "4-00675-02A-VN" appears under the price; the owner's manual is FAFO-001 | **Not the same string** the site publishes (FAFO-001). The site cites the manual for FAFO-001 and the brand page for the rest; recorded here so the difference is not read as a contradiction. No change made. |
| V39 | Capacity | same (S14) | "26-Quart Capacity / preparing food for 4–6 people" and "24.6 Liters / Capacity" | **Confirmed** — matches "26 qt / 24.6 L" |
| V40 | Dimensions | same (S14) | "16.9\"D x 15.8\"W x 14.8\"H / Product Dimensions" | **Confirmed** |
| V41 | Voltage | same (S14) | "120 volts / Product Voltage" | **Confirmed** |
| V42 | Preset / function count | same (S14) | Four different strings on the same page in the same fetch: specification block "25 Cooking Pre-sets"; description "This endlessly versatile **10-in-1** air fry convection oven"; a carousel image filename `11-in-1_convection_oven_in_action.png`; the Amazon title for the same product "24 One-Touch Preset Options" | **Conflict confirmed live** — no number is asserted anywhere on the site. F29 now has five official strings (10-in-1, 11-in-1 asset, 24, 25) |
| V43 | Interior light | same (S14) | The specification block lists Timer, 26-Quart Capacity, Dual-Speed Fan, 25 Cooking Pre-sets, Dimensions, 24.6 Liters, Temperature Control, 120 volts — **no interior-light row** | **Not re-confirmed** — F30 stands (published row retained and flagged rather than deleted) |
| V44 | Warranty | same (S14) | Not stated in the specification block returned in this pass | **Not re-confirmed** — published "1-year warranty" stays with its existing flag; not edited |
| V45 | Brand-site rating snapshot | same (S14) | "2.6" with "(25)" next to it | **Confirmed as a snapshot** — this is the manufacturer's own widget, not Amazon's; already labelled as such on the site |

## 6. Repository irregularities found in this pass

| # | What was found | Evidence | Action taken |
|---|---|---|---|
| R1 | Two flag registers are published and they disagree: `data/flags.json` (F01–F27, consumed by the s2/docs generators) still says the commission schedule "redirected to a sign-in page" and that identity was verified; the rendered Flagged page (programme flags + product flags) says the opposite. Both are readable from the live site. | `data/flags.json` vs `flagged.html` | **Not edited** — another session's data, and rewriting it would silently re-point that generator's citations. Published as **F44** with both links so the owner can decide which register is canonical (the decision is already listed as suggestion SG-* on `suggestions.html`). |
| R2 | The Associates Program Policies page now reads **"Updated: April 14, 2026."** The site's compliance page quotes the same section numbers and text, so the quotations still hold; the version stamp was older. | policies page, 2026-11-15 | Published as **F44** context; `data/sources.json` S2 gains a `page_version` field with the 2026-11-15 reading, and S1's already-correct version is left as is. |
| R3 | The Emerald/Emeril listing title says **"Six Cooking Accessories Included"** while the site publishes **Included accessories: 7** (sourced to the brand page/manual). | V21 vs `data/products.json` | Published as **F45**; the value is **not** changed because the site's number is traceable to the brand/manual and the listing may count differently (e.g. rotisserie parts separately). Both are shown. |
| R4 | `reports/link-check-2026-11-14.md` is cited by the site, but the 2026-11-15 re-check is a new document. | this file | Added as the linked evidence for today's pass. |
| R5 | The 8 Qt product page's title row and the site's "Hi-Fry / 450 °F mode: None" row are only consistent for RJ38-SQSS-8T. | V37 vs `data/products.json` | Already F33; this pass adds the confirmed brand strings for RJ38-8T-BLACK so a reader can see the whole comparison in one place. No value changed. |

## 7. What was deliberately not changed

* No Amazon price, availability, star rating or review count was added anywhere (Program Policies
  §2(b), §6(t)). Prices were visible in the fetched pages and were **not** republished.
* No ASIN → model mapping was asserted. The three listings' Product-information blocks were not
  retrievable (V24), so F1/F2/F32/F33 remain open.
* No preset count was asserted for either Chefman 6 Qt or Emeril (V33, V42).
* No commission rate was attached to a specific product (V11).
* No other session's data files were edited: `data/flags.json`, `data/flagged.json`,
  `data/verified/*`, `site/`, `s2/`, `research/`, `docs/`, `dashboard/`, `annex-*` and
  `session-*` are untouched by this pass.

## 8. Commands run in this pass (all exit 0 unless stated)

```bash
python3 build.py            # regenerates every page, runs 9 build guards
python3 verify.py           # links, sources, disclosure, no price/rating leakage
python3 platform/audit/report.py
python3 scripts/build_s2_site.py --check
python3 scripts/check_links.py
python3 research/check_research.py
python3 scripts/verify_site.py
```
