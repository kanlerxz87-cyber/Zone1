# Verification round 11 — 2026-11-16 (session 3dfe4b45, branch `arena/3dfe4b45-zone1`)

Scope: live re-read of every official source that round 10 (`reports/verification-2026-11-16.md`, session
c334fb1c) explicitly listed under **"Not re-read in this round"**, plus the editorial growth that the
topic register marked as pending (TP-04/07/08/09/10/11) — of which the three rows fully supported by
already-published values were written. No published product value was changed. Anything not re-read in
this round is listed under "Not re-read".

## 1. What was re-read, and the verdict on each row

Every fetch below was made on 2026-11-16 UTC as a direct page read. Verdicts are recorded per value.

| Source | Page | Read on 2026-11-16 | Verdict vs stored record |
|---|---|---|---|
| S10 | [chefman.com — TurboFry Touch 6 Qt Dual-Window](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | Model RJ38-SQPF-3TDB-2W; Features: "Max temp: 450ºF/ 235ºC with Hi-Fry function", Sync Function, nonstick dishwasher-safe baskets, interior light, dual viewing windows, matte-black finish; Specifications: 6 Qt / 5.67 L · 200–450°F / 95º-235ºC · 13.38 x 11.81 x 10.63 in / 33.98 x 30 x 27 cm · 13.3 lbs / 6.03 kg · 1700W/120V · cETL approved with a 1-year Chefman assurance | **Match** — every published 6 Qt row still states exactly this |
| S12 | [chefman.com — TurboFry Touch Stainless-Steel (8 Qt)](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) | Model RJ38-SQSS-8T; Features: "Max temp: 400ºF/ 205ºC", 4 cooking presets, touch screen, 5- or 8-quart nonstick basket, top-rack dishwasher-safe, auto-shutoff, stainless-steel finish; Specifications: 5 Qt or 8 Qt / 4.73 L or 7.57 L · 200–400°F / 95º-205ºC · 1700W/120V · (8 Qt) 15.4 x 12.6 x 13.5 in / 39.11 x 32 x 34.29 cm · (8 Qt) 12.8 lbs / 5.8 kg · models RJ38-SQSS-5T / RJ38-SQSS-8T · cETL + 1-year assurance; description: 98% less oil, presets fries/chicken/fish/meat, designed for 4-6 people, LED shake reminder | **Match** — every published 8 Qt row still states exactly this; the 450 °F conflict (F3) stands: the brand page still documents 400 ºF |
| S14 | [emerileveryday.com — French Door AirFryer 360, 26 QT](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | Spec icons: 26-Quart Capacity · preparing food for 4–6 people · Dual-Speed Fan · **"25 Cooking Pre-sets"** · 16.9"D x 15.8"W x 14.8"H Product Dimensions · 24.6 Liters Capacity · 120 volts Product Voltage · "1-Years Warranty"; Product Manual link → the FAFO-001 PDF (S15 URL); description: "24 one-touch cooking presets" and "Included are 7 premium accessories"; a "10-In-1 Versatility" heading listing ten functions; Rotisserie in key features; price shown $199.99 (not published here) | **Match** on every published row; **the preset-count conflict is re-confirmed on one page on one day**: 25 (icon) vs 24 (description) vs 10-in-1 (heading) — none asserted by this site; still **no weight row** anywhere (Q-06 stays open) |
| S15 | [Emeril FAFO-001 owner's manual (PDF)](https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf) | Appliance Specifications table: FAFO-001 · 120 V/1700 W/60 Hz · 1700 W · 26 quarts (1519 cubic inches) · 75° F - 500° F/25° C - 260° C · LED; Preset Information: the preset/accessory table names exactly **24 presets** (Airfry, Fries, Bacon, Grill, Eggs, Fish, Ribs, Defrost, Steak, Vegetables, Wings, Bake, Rotisserie, Toast, Chicken, Pizza, Pastry, Proof, Broil, Slow Cook, Roast, Dehydrate, Reheat, Warm); Rotisserie row: "Level 3 (Rotisserie Slot) / Rotisserie Spit and Forks"; Heating Element Chart: "Uses the 1700W top spiral heating element"; safeguard: "**NEVER use with an extension cord**" | **Match** — capacity, power, supply, temperature range and display all still state exactly what the dataset publishes; the manual's 24 named presets are what the dataset records |
| S13 | [Chefman RJ38-SQSS-8T user guide (PDF)](https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQSS-8T-UG-US.pdf) | Safety instructions, features, control panel and preset chart: RJ38-SQSS-8T; "extra-large 8-quart basket capacity"; one basket in the features list; presets Default 15 min/400°F, Meat 18/375°F, Chicken 22/375°F, Fish 10/350°F; extension-cord clause: rating "at least as great as the electrical rating of the appliance" | **Match** — preset defaults match the published row; the single-basket features list supports the new Sync Finish article's contrast |
| S18 | [Chefman RJ38-SQPF-3TDB-2W user guide (PDF)](https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQPF-3TDB-2W-UG-US.pdf) | Welcome: "With two 3-quart baskets"; control panel: SYNC FINISH "Programs baskets with different cooking times and/or temperatures to finish at the same time", SYNC BASKETS "Programs both baskets to cook at the same time and temperature", HI-FRY "Raise temperature to 450°F/235°C for 2 minutes for a little extra browning"; operating instructions: the sync delay behaviour, the HOLD display, the pause-when-removed behaviour; special functions: HI-FRY "will raise the cooking temperature to 450˚F (235˚C) for 2 minutes"; **CAUTION (verbatim): "Never spray the baskets or racks with cooking oil from an aerosol spray can, which includes harsh components that can cause chipping of the nonstick coating. However, you can oil the racks or spray them with oil from a non-aerosol mister."**; cleaning: "Baskets and racks are also top-rack dishwasher safe" | **Match** — the Sync Finish, Hi-Fry, per-basket and care rows all still state exactly this |
| S3 | [Standard Commission Income Statement, Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) | Read **with no login**: "Physical Books, Kitchen, Automotive | 4.50%" and "All Other Categories | 4.00%", plus the rest of Table 1 and the bounty table | **Match** — the stored commission table row matches row for row |
| S8 | [FTC — Disclosures 101 for Social Media Influencers](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | Page stamp "November 2019"; "You can't talk about your experience with a product you haven't tried."; "Place it so it's **hard to miss**"; material-connection definition; "The disclosure should be in the same language as the endorsement itself." | **Match** — unchanged from the stored record |
| S9 | [eCFR — 16 CFR Part 255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) | "Displaying title 16, up to date as of 11/12/2026. Title 16 was last amended 10/30/2026."; Part 255 sections §255.0–§255.6 incl. §255.5 "Disclosure of material connections"; source: 88 FR 48102, July 26, 2023 | **Match** — unchanged from the 2026-11-14 read |

## 2. Observations recorded today (no published value changed)

1. **Review counts moved again on the brand widgets.** 6 Qt: 1,305 → **1,307**; 8 Qt: 716 → **717**. Both
   averages still read **4.6**. This is the third consecutive round with a moved count (F14's pattern).
   This site publishes no review counts, so nothing to update — the observation is recorded here and in
   the S10/S12 page-version stamps.
2. **The Emeril preset conflict is now confirmed three ways on one page on one day:** "25 Cooking
   Pre-sets" (spec icon), "24 one-touch cooking presets" (description), "10-In-1 Versatility" (heading) —
   and the owner's manual names 24. The site asserts none of them.
3. **The Chefman 8 Qt temperature conflict stands:** Amazon's listing title advertises "450°F Hi-Fry"
   while the brand page documents "Max temp: 400ºF/ 205ºC" (F3, narrowed by F33 to a second-SKU question
   that only the listing's product-information block could settle — Q-01/Q-02).
4. **The Emeril weight cell stays blank** — no weight appears in the brand page's spec icons or in the
   manual's specification table (Q-06 remains open; nothing inferred).
5. **Brand list-price display changed shape, not value.** Both Chefman pages now render a tiered discount
   selector (Save 10%–40%) over the same $119.99 list. The dataset's `list_price_confirmation` rows are
   date-stamped observations and were left as they stand; this site publishes no prices either way.

## 3. What was written from these reads

Three topic-register rows whose every needed value was already published — and was re-confirmed live
today — were written as articles and marked published in `data/topics.json`:

| Register row | Article | Every number in it |
|---|---|---|
| TP-09 | `articles/sync-finish-explained.html` | Quoted from the re-read manual (S18) and the published feature row |
| TP-10 | `articles/aerosol-oil-warning.html` | The manual's caution sentence, read verbatim today (S18); the 8 Qt care row (S13/S12) |
| TP-11 | `articles/extension-cord-rules-in-the-manuals.html` | Only the wattage rows published in the dataset and the manuals' own cord/clearance instructions |

TP-11's register row carries a caveat: *"Do not write the electrical half without [a non-manufacturer
electrical reference]."* The article respects it by **not writing the electrical half**: it makes no
statement about circuits, breakers, amps or shared loads — it quotes only each manufacturer's own cord
and placement instructions. The register row's working title ("what that means on a kitchen circuit")
was deliberately not used as the article title.

TP-04 ("The counter-space test") was **not** written: its ground is already covered by the published
`articles/small-kitchen-air-fryer-dimensions.html` ("Will it actually fit?"), added by pass T20. TP-07
and TP-08 remain proposals: TP-07 hinges on the accessory-count conflict (F45) that only the listing's
own product-information block could settle, and TP-08 would need the rotisserie hardware rows that sit
in the manual's parts section, which this round did not re-read in full.

## 4. A register contradiction observed, not edited (logged per protocol)

`data/design-prompt.json` — session `bf487400`'s register — lists topic row **A-11** ("Will it fit?
Reading air-fryer dimensions before you buy") as `not-written`, while `articles/small-kitchen-air-fryer-dimensions.html`
has been published since pass T20 (session 792c279e, PRs #71/#73) and is linked from the topic register
(TP-12). Two registers currently disagree about the same article. Per protocol item 4 the file was **not
edited** (it is outside this session's claimed scope); this row is the request to its owning session, and
the finding is visible on this page so nobody treats A-11's status as current.

## 5. Not re-read in this round

- S1 (Operating Agreement) and S2 (Program Policies) — re-read 2026-11-15 (round 9) and 2026-11-16
  (round 10, S2 date) respectively; no change reported by either.
- The three `link.amazon` short links and the three Amazon `/dp/` pages — re-read today by round 10
  (`reports/verification-2026-11-16.md`); re-running the same fetches hours later would add no
  independent evidence.
- S32–S34 (Chefman commerce endpoints) — last read 2026-11-15 (round 9); the F51 weight discrepancy
  they produced is unchanged by anything in this round.
- The Emeril manual's parts-and-accessories pages (needed for TP-07) — not re-read in full.

## 6. Result

Every value re-read today matches the stored record; no published value changed. Three new articles
enter the build with citations the round confirmed. The gates run on this tree are recorded in
`COORDINATION.md` (X-3dfe4b45 completion record).
