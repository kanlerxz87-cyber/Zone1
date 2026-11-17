# ASIN → model mapping: reading the listing's own Product information block

> **Correction (2026-11-17, F79):** Section 5 below cites S23 as a general ASIN-length and `/dp/`-format definition. The source register identifies S23 as KDP's “Linking from Your Website” help page and does not substantiate that general claim. Do not use the supplied short-link path tokens to infer intended products or ASINs. Current supplied URLs, observed destinations, and blank owner-confirmed intent fields are in [`data/product-intent.json`](../data/product-intent.json). This correction narrows the source claim; it does not alter the reported 2026-11-16 listing-page observations.

**Session:** `arena/ba29c641-zone1` (pass 11) · **Date:** 2026-11-16 (UTC) · **Task:** Z2 on the board
**Method:** server-side fetch of the live URL, then a line-by-line read of the returned page. Nothing
below is recalled, inferred or carried over from another file: every value is quoted from the response
this pass fetched, and every value the response did not contain is recorded as absent.

---

## 1. Why this file exists

Ten passes of this repository carried one sentence forward without re-testing it. In
`data/products.json`, the Chefman 6 Qt `model_number` object held the caveat:

> "Amazon itself does not publish the model number on the ASIN, so the ASIN→model step remains a
> documented match rather than an official statement."

and the canonical flag register's **F1** was titled *"ASIN → manufacturer model number is not published by
Amazon."* **F49** went further and explained why no session could fix it: *"the 'Product information' table
… is rendered client-side, so an automated read cannot see it; a human browser can, in about ten seconds per
listing"* — recorded 2026-11-15 by `arena/792c279e-zone1` after three fetches returned the buy box without
the table, and then restated on the landing page, on `handover.html` and in hand-over item H1. On that premise sat **SG-01** ("open each of the three Amazon links, scroll to
the Product information table, read the 'Model Number' row. Five minutes total"), and with it the
blocking chain **F2 / F3 / F32 / F33** and **Q-01 / Q-02** — four flags, two questions and the top
item of a 22-entry decision queue, all held open because a document was believed unreachable by a
fetch. Pass 10 recorded the belief again, at `EXECUTIVE-SUMMARY.md` §17.6: those flags are "not
answerable from outside the account holder's browser".

They were answerable. The premise was tested on 2026-11-16 and it is false: the same `/dp/` URLs were
fetched from the same kind of environment and each response body contained the Product information block,
model rows included. Whether the table appears in a render depends on the render path, not on the data
being unreachable — and F49's own note says three fetches had returned the buy box *without* the table,
which is an observation about one response, promoted into a rule about all of them.

## 2. The reads

| # | Request | Result | Verdict |
|---|---------|--------|---------|
| 1 | `https://www.amazon.com/dp/B0CDY277D3` | Page returned; `<title>` = "Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen"; the returned URL carries `?lv=shuf&channelId=500&plpRedirect=mhFallback` | The **Product information** block is present in the response body (chunk 8 of 18). Model number published. |
| 2 | `https://www.amazon.com/dp/B09B7SB46R` | Page returned; `<title>` = "Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included : Home & Kitchen" | **Product information** present (chunks 7–8 of 16). Model number published. This ASIN had **never** rendered for this repository before: the three fetches of 2026-11-15 each returned the "Continue shopping" checkpoint (that is why the `Amazon browse node` row was blank, per **F53**). |
| 3 | `https://www.amazon.com/dp/B08DKYBTPH` | Page returned; `<title>` = "Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel : Home & Kitchen" | **Product information** present (chunks 7–8 of 18). The model **code** is published — but in `Part Number`, not in `Model Number`. |

No request in this pass was answered with a checkpoint, a captcha interstitial or a 404.

## 3. What each page states

Quoted as the field reads. `S16` / `S28` / `S29` are the repository's registered source ids for these
three URLs (`data/sources.json`, stamped with this pass's read).

### B0CDY277D3 — the 6 Qt dual basket

| Field on the page | Value | Against what the site held |
|---|---|---|
| Model Number | `RJ38-SQPF-3TDB-2W` | **Agrees** with chefman.com (S10) and the owner's manual (S18) — now a second official document for a value the site published from one |
| Part Number | `RJ38-SQPF-3TDB-2W` | new |
| Model Name | `Turbo Fry® Touch` | new |
| Configuration | `Dual Basket` | corroborates "two independent baskets" |
| Item Type Name | `Dual-Basket Air-Fryer` | new |
| UPC | `810087845025` | new |
| Included Components | `User Guide` | new |
| Special Features | `+ 2Min Button, Automatic Shut-Off, Dual Zone Features, Hi-Fry, Mute` | corroborates Hi-Fry and Auto Shutoff, which the title had claimed |
| Recommended Uses | `Air Fry, Cook, Defrost, Reheat, Roast` | new |
| Wattage / Voltage | `1700 watts` / `120 volts` | **agrees** with S10 |
| Max / Min Temperature Setting | `450 °F` / `93 °C` | maximum agrees; the minimum conflicts with the brand page's 95 °C floor → **F72** |
| Item Dimensions | `13.38"D x 11.81"W x 10.63"H` | **agrees** with S10 digit for digit |
| Item Weight | `13.3 pounds` | **agrees** with S10 |
| Capacity | `6 liters` | **conflicts** with the same page's title/Size and with 6 qt = 5.67 L → **F69** |
| Software Update Supported to Date | `unknown` | recorded, not used |
| Warranty & Support | "Manufacturer's warranty can be requested from customer service." | weaker than S10's stated 1-year assurance; the site keeps S10's row and notes the difference |
| Preset count | **absent** — no preset row exists in this block | strengthens **F36**: the row stays blank because no official document states a count |
| Breadcrumb | `Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers` | **agrees** with the `Amazon browse node` row filled on 2026-11-15 |

### B09B7SB46R — the Emeril 26 QT french door

| Field on the page | Value | Against what the site held |
|---|---|---|
| Model Number | `4-00675-02X-VN` | brand page says `4-00675-02A-VN` (S14) — **one character apart**, manual says `FAFO-001` (S15) → **F70**, not reconciled |
| Part Number | `4-00675-02X-VN` | same string in both rows |
| Model Name | `Extra Large 26 QT French Door Air Fryer Oven` | new |
| Configuration | `Air Fryer Toaster Oven Combo with 24 Functions and 7 Accessories` | third document for **24** functions (the manual lists 24 by name; the brand page's spec block says 25) → **F4** addendum. "7 Accessories" contradicts the same page's own enumeration → **F71** |
| Included Components | `Rack, Bake Pan, Drip Tray, Crisper Basket, Rotisserie Spit, Fetch Tool` | six named parts; the title says "Six Cooking Accessories Included"; the site publishes 7 from S14 + S15 → **F71** |
| Item Highlight | `Countertop Convection Cooker, 24 One-Touch Preset Options, … Six Cooking Accessories Included` | new |
| Wattage / Voltage | `1700 watts` / `120 volts` | agrees with S15 (1700 W) and S14 (120 V) |
| Max / Min Temperature Setting | `500 °F` / `75 °F` | the brand page publishes **no** temperature range for this model; this is the repository's only official range, and it is a *listing* claim, labelled as such |
| Item Dimensions | `16.9"D x 15.8"W x 14.8"H` | **agrees** with S14 |
| Capacity | `24.6 liters` | agrees with the 26 QT / 24.6 L the site publishes |
| Size / Materials | `Extra Large` / `Stainless Steel` (outer and inner) | new |
| Recommended Uses | `Air Fry, Bake, Broil, Dehydrate, Roast` | new |
| UPC | `752356835682` | new |
| Item Weight | **absent** — the Measurements block has no weight row | the site's weight row for this product does not exist, and still cannot be filled from this document |
| Warranty | two linked documents: "User manual … [PDF]" and "Product Warranty … [PDF]" under *Warranty & Support*, plus a *Product guides and documents* User Manual PDF | documents exist on the page and are named; **not opened by this pass**, so no warranty term is taken from them. The site continues to publish the 1-year term from the brand page (S14) |
| Browse classification | `#… in Kitchen & Dining`, `#… in Air Fryers` (`/gp/bestsellers/kitchen/17659096011`) | filled the `Amazon browse node` row that three 2026-11-15 fetches left blank (**F53** addendum) |

### B08DKYBTPH — the 8 Qt TurboFry

| Field on the page | Value | Against what the site held |
|---|---|---|
| Part Number | `RJ38-SQSS-8T` | **agrees** with S12 and S13 — the ASIN-to-model step is now sourced from the listing |
| Model Number | `Large Air Fryer` | **not a model code.** The field a reader (or a scraper) would trust holds marketing copy, so a method that reads only `Model Number` returns garbage. Recorded in **F68** as a method warning |
| Model Name | `Square Air Fryer` | new |
| Max / Min Temperature Setting | `400 °F` / `94 °C` | the maximum **contradicts this same page's title** ("450°F Hi-Fry Option"), which is the F3/F33 conflict now living inside one document; the minimum does not convert to the brand page's 200 °F floor → **F72** |
| Item Dimensions | `12.75"D x 13.5"W x 10"H` | brand page gives `15.4 x 12.6 x 13.5 in` for the 8 Qt → **F69**; both published, neither corrected |
| Item Weight | `12.8 pounds` | **agrees** with S12 |
| Capacity / Size | `8 quarts` / `8 quarts` | agrees |
| Wattage / Voltage | `1700 watts` / `120 volts` | agrees with S12 |
| Special Features | `Automatic Shut-Off, LED Shake Reminder, Programmable` | corroborates the `Shake reminder` and `Auto shutoff` rows |
| Product Care Instructions | `Dishwasher Safe` | new, and vaguer than the brand page (which says which parts) — the site says so on the row |
| Warranty Description | `1-Year Limited Warranty` | third document for the term the manual states (S13) |
| Included Components | `User Guide` | new |
| UPC | `816458024518` | new |
| Recommended Uses | `Air Fry, Bake, Dehydrate, Reheat, Roast` | corroborates the "4-in-1" functions named in the title |
| Preset count | the block carries no preset row | the site's four presets stay sourced to S12/S13 |

## 4. What was deliberately not published

These values were in the same responses and are **not** on the site:

* **Prices, discounts and delivery dates.** Program Policies, Participation Requirements §2(b): an
  Associate site may display a price only where Amazon serves the link or where it comes from the
  Creators API / PA API. <https://affiliate-program.amazon.com/help/operating/policies>
* **Star ratings, review counts and the "Customers also viewed" figures.** Same page, §6(t): customer
  reviews and ratings may be used only when obtained through those APIs.
* **Best Sellers Rank positions.** The number was read and is recorded above as an observation with
  its date. It is not put in a table, because this repository's adopted reading of IP License §2(e)
  (no aggregating or analysing Program Content) is what the site has published all along, and the
  `competition` field's reason string now says so: a decision not to publish, not an absence of data.
  Changing that posture is an owner call (the s2 register's R-03 and the root register's C-05/C-07
  carry it), not something a pass should quietly reverse while adding rows.

## 5. What remains open, unchanged by this pass

1. **A concurrent pass had already re-read these listings.** Pass 10 (`arena/121929a5-zone1`) reached the
   Emeril page *through the supplied short link* on the same day and filled its browse-node row; pass 11
   (`arena/2e346d24-zone1`) re-read both brand pages and the listing titles, and re-established that Chefman
   publishes a second 8 Qt page — `RJ38-8T-BLACK` at 450 °F (S26). This file's first draft read those reads as
   narrowing F3/F33 toward "stale title". That was wrong and is corrected above: with a second SKU genuinely
   documenting 450 °F, the two-models explanation is not closed, and the listing's self-contradiction is
   evidence in the case rather than a verdict. What is new in this pass is the Product information block itself,
   which neither pass captured.
2. **The three supplied tokens are still not ASINs.** `B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV` are nine
   characters; an ASIN is ten (<https://kdp.amazon.com/en_US/help/topic/G200652190>, S23). Using them
   as `/dp/` identifiers returns Amazon's 404 page (S21). The `link.amazon` short links resolve to the
   three ASINs above through `plpRedirect=mhFallback`, and this repository has never established that
   a fallback destination is what the link was created to point at. **F6, F7, F10 stand.**
3. **The Associates tag inside those short links is still unobservable** (**F6**). Nothing on the site
   can show it, and no `tag=` parameter exists in any link this build emits (`data/config.json`
   `associate_tag` is empty, by design, with a visible warning).
4. **Which commission category Amazon applies to each ASIN** (**Q-11**). The listings classify
   themselves in Kitchen & Dining and Air Fryers; the Commission Income Statement pays by *commission*
   category. No public document maps one to the other, so the rate stays blank per product with both
   candidate rows shown.
5. **The 450 °F question is sharpened, not settled.** The listing for the 8 Qt carries a 450 °F claim
   in its title and a 400 °F maximum in its own spec table, and its Part Number identifies the 400 °F
   model. What the machine does is still not something this site asserts.
6. **Whether quoting a public listing page is "Program Content"** — the question **F62 / Q-21** record,
   which every row added by this pass cites in its own note, because adding rows widens what the
   answer would touch.

## 6. Links for manual review

| Claim | Official page to check by eye |
|---|---|
| 6 Qt model number and full spec block | <https://www.amazon.com/dp/B0CDY277D3> |
| 6 Qt brand page (for the corroboration and the two conflicts) | <https://chefman.com/products/turbofry-touch-dual-window-air-fryer> |
| 6 Qt owner's manual (Hi-Fry "2 minutes", "two 3-quart baskets") | <https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQPF-3TDB-2W-UG-US.pdf> |
| Emeril model string, 24 Functions / 7 Accessories, six enumerated parts, 75–500 °F | <https://www.amazon.com/dp/B09B7SB46R> |
| Emeril brand page (the `02A-VN` string, the "25 Cooking Pre-sets") | <https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360> |
| 8 Qt Part Number, 400 °F maximum, 1-Year Limited Warranty, dimensions | <https://www.amazon.com/dp/B08DKYBTPH> |
| 8 Qt brand page (the 15.4 × 12.6 × 13.5 in figures) | <https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1> |
| 8 Qt owner's manual (warranty terms, four presets) | <https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQSS-8T-UG-US.pdf> |
| ASIN length definition (10 characters) | <https://kdp.amazon.com/en_US/help/topic/G200652190> |
| Price / rating / aggregation rules | <https://affiliate-program.amazon.com/help/operating/policies> |
| The supplied short links, exactly as given | <https://link.amazon/B04G1MEwY> · <https://link.amazon/B02NbDxp3> · <https://link.amazon/B00hJ57DV> |

## 7. Irregularities flagged for review

| Flag | One line |
|---|---|
| **F68** | The "listings do not publish a model number" premise was false; four flags and two questions were open on it. Also: on one ASIN the code is in `Part Number` while `Model Number` holds marketing copy. |
| **F69** | 8 Qt footprint differs between the brand page and its own listing; 6 Qt Capacity field says litres where the page says quarts. |
| **F70** | Three official model strings for the Emeril, the newest two one character apart. |
| **F71** | The Emeril listing says 7 accessories in one field, enumerates six in the next, and says "Six" in its title. |
| **F72** | °C temperature floors that do not convert to the °F floors published beside them. |
| **F73** | The requirements register promised computed counts in its own preamble and typed eight of them, four of which had already drifted; now substituted at build time, with a guard on both ends. |
| *(gate defect, fixed in the same pass)* | `.github/workflows/ci.yml` and `scripts/ci-check.sh` ran the annex builder (which writes) and then `--check`, so the "prove the committed HTML is current" step could not fail; the stamp was also timezone-dependent. Repaired and proven to fire. |
