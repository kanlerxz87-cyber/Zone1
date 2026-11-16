# Live source re-verification — 2026-11-16 (arena/a746a9f2, X-a746a9f2)

> Filed under the session-suffixed name at the 2026-11-16 merge seam: the unsuffixed
> `reports/verification-2026-11-16.md` belongs to session c334fb1c's round-10 record.

Independent line-by-line re-verification pass. Every row below was read **live on 2026-11-16 UTC**
through a server-side fetch (this sandbox has no direct egress to non-GitHub hosts). Each row names
the URL, the exact string read back today, and the verdict against what the site publishes. Nothing
was inferred; where a value could not be read it is left as published and flagged.

## 1. The three supplied `link.amazon` short links (S17)

| # | URL | Read back today (2026-11-16) | Verdict |
|---|-----|------------------------------|---------|
| V1 | https://link.amazon/B04G1MEwY | Resolved to `https://www.amazon.com/dp/B0CDY277D3?…&plpRedirect=mhFallback`. Page title: "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black". Breadcrumb: Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers | Destination unchanged since 2026-11-15 (S16/S17). Title matches the published `amazon_listing_title` for `chefman-6qt-dual-basket` verbatim. Token remains 9 characters and the redirect still carries fallback-style parameters (F17/F24 unchanged). **Product identity still unconfirmed** (Q-01): the reduced "Product summary" shell returned to automated reads contains no Product-information block. |
| V2 | https://link.amazon/B02NbDxp3 | Resolved to `https://www.amazon.com/dp/B09B7SB46R?…&plpRedirect=mhFallback`. Page title: "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included". Same browse-node breadcrumb | **S28 re-read after the 2026-11-15 bot checkpoint.** The listing title confirms, verbatim: "24 One-Touch Preset Options" and "Six Cooking Accessories Included". Re-confirms the F4/F50 conflict (brand spec block says 25 presets; site publishes 24 from the manual; brand page says 7 accessories, listing says six). No published value changed. |
| V3 | https://link.amazon/B00hJ57DV | Resolved to `https://www.amazon.com/dp/B08DKYBTPH?…&plpRedirect=mhFallback&th=1`. Page title: "Chefman Air Fryer 8 Qt | TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results | Bake, Dehydrate, Frozen | XL Nonstick Dishwasher-Safe Basket | Stainless Steel". Same browse-node breadcrumb | Destination and title unchanged (S29). Re-confirms the F3/Q-02 conflict: the title's 450 °F Hi-Fry + "Bake, Dehydrate, Frozen" match RJ38-8T-BLACK (S26), the "Stainless Steel" finish matches RJ38-SQSS-8T (S12). No model asserted. |

Notes on all three (not published as values): the reduced pages returned a "Customers who viewed
this item also viewed" carousel carrying other products' prices and star ratings. Per Program
Policies §2(b)/§6(t) this site publishes none of those numbers, and none were copied anywhere.

## 2. Manufacturer sources

| # | Source | Read back today | Verdict |
|---|--------|-----------------|---------|
| V4 | [S10 — Chefman TurboFry Touch 6 Qt Dual-Window](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | Model string "RJ38-SQPF-3TDB-2W" shown on page; "Max temp: 450ºF/ 235ºC with Hi-Fry function"; "Sync Function so both baskets finish cook…"; review widget "1307 Reviews" | Every published 6 Qt spec row still matches. Review count moved 1,305 → 1,307 since 2026-11-15 — exactly the drift F19 documents; the site publishes no review count. |
| V5 | [S12 — Chefman 8 Qt TurboFry Touch](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) | Model "RJ38-SQSS-8T"; sizes "8 Quart / 5 Quart"; "precise temperatures ranging from 200–400°F"; "Designed for 4-6 people"; presets "fries, chicken, fish, and meat"; "98% less oil" (brand claim); review widget "717 Reviews" | Every published 8 Qt row matches. Max temp 400 °F confirmed again — the F3 conflict with the listing title is live. Review drift 716 → 717 (F19 class). |
| V6 | [S26 — Chefman TurboFry 8 Qt w/ High Fry](https://chefman.com/collections/air-fryers-1/products/turbofry-8-qt-air-fryer-w-high-fry) | Model "RJ38-8T-BLACK"; "Capacity: 8 Qt / 7.57 L"; "Hi-Fry Temperature: 450°F / 232°C"; "4 Cooking Functions: Air fry, bake, dehydrate, and frozen"; "Power: 1700W/120V"; "cETL approved with a 1-year assurance from Chefman"; "Matte-black finish" | Confirms the second 8 Qt SKU the site names in F3/Q-02 and in the article `chefman-8qt-two-models`. The listing title's function list ("Bake, Dehydrate, Frozen") and 450 °F Hi-Fry match this model exactly; its finish does not. Conflict stands; nothing inferred. |
| V7 | [S14 — Emeril French Door AirFryer 360](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | SKU "4-00675-02A-VN"; spec widget: "26-Quart Capacity / preparing food for 4–6 people", "25 Cooking Pre-sets", "16.9\"D x 15.8\"W x 14.8\"H", "24.6 Liters", "120 volts"; description "10-in-1"; an image asset named "11-in-1_convection_oven_in_action.png"; rating widget "2.6 (25)" | Capacity, dimensions and voltage rows match. The 24-vs-25 preset conflict (F4), the "10-in-1"/"11-in-1" counting conflict (F5) and the low brand-widget rating are all live exactly as registered. SKU string matches what `data/products.json` publishes for `model_number`. |

## 3. Amazon Associates programme sources

| # | Source | Read back today | Verdict |
|---|--------|-----------------|---------|
| V8 | [S1 — Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) | "**Updated:** October 15, 2025" | Version stamp unchanged vs S1. |
| V9 | [S2 — Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | "**Updated:** April 14, 2026"; session rules verbatim: "24 hours elapse from that click" / "no later than 89 days after their initial click-through" / "within 180 days of the purchase, the Product is shipped to, streamed or downloaded by, and paid for by the customer" | Version stamp and the 24h / 89-day / 180-day rules match what the compliance page quotes. |
| V10 | [S3 — Standard Commission Income Statement](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) | Table 1 read **in full, with no login**: "Physical Books, Kitchen, Automotive \| 4.50%"; "All Other Categories \| 4.00%"; plus the full bounty table | Matches the published commission rows and `data/compliance.json`. Re-confirms that the legacy register's F02 claim ("redirected to a sign-in page") is contradicted by live reads since 2026-11-14 (F44/F47 unchanged). |
| V11 | [S4 — Application Review Process](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) | "we require at least three within the first 180 days"; "a good rule of thumb is at least 10 posts"; "Content on your website must be recent (generally within the last 60 days)"; "at least 500" followers for social; "we aren't able to reassess an application once it's been rejected" | Matches the published decision/Q-13 rows verbatim. |
| V12 | [S5 — Identify yourself as an Associate](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) | Required sentence verbatim: "As an Amazon Associate I earn from qualifying purchases."; link-level disclosure "Clear… Conspicuous" with examples "(paid link)", "#ad", "#CommissionsEarned" | Matches the site's disclosure bar and the compliance page. The sentence appears in every page header (build guard `check_disclosure`). |

## 4. Legal sources

| # | Source | Read back today | Verdict |
|---|--------|-----------------|---------|
| V13 | [S8 — FTC Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | "You can't talk about your experience with a product you haven't tried."; "Place it so it's hard to miss."; "Don't mix your disclosure into a group of hashtags or links." | Matches the site's voice rules and the "no hands-on testing" policy. |
| V14 | [S9 — 16 CFR Part 255 (eCFR)](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) | "Displaying title 16, up to date as of 11/12/2026. Title 16 was last amended 10/30/2026."; ToC carries §255.0–§255.6 incl. §255.5 | Matches the compliance page's citation. |

## 5. Verdict summary

* **14/14 source reads succeeded today**, including S28 which was blocked by a bot checkpoint in the
  2026-11-15 round. That checkpoint is cleared and the listing title is now read twice over.
* **No published value changed.** Every value the site publishes still matches its official source.
* **Every open conflict is still open and still live**: F3 (8 Qt model/temperature), F4/F5 (Emeril
  preset and function counting), F50 (accessory count), F2/F33-class model-match caveats (Q-01/Q-02).
  None was closed, none was softened.
* **Still unverifiable from here, left blank/flagged**: the ASIN→model mapping (Amazon serves the
  reduced "Product summary" shell with no Product-information block — F46), the Associates tag inside
  the supplied short links (Q-04), account status (Q-03), and every Amazon price/rating/availability
  by policy (S2 §2(b), §6(t)).
* **New irregularities found today: none.** Brand review-count drift (1,305→1,307, 716→717) is the
  already-registered F19 behaviour and affects no published value.

## 6. Gates run at the end of this pass (2026-11-16)

See the completion record in `COORDINATION.md` for the final gate table after the content additions.
Baseline before this pass's edits: `python3 build.py` 29 pages + robots/sitemap (36 URLs) ·
`python3 verify.py` 115 pages, 46 spec rows (43 verified, 3 blank+flagged), 34 sources, 0 errors ·
`bash scripts/ci-check.sh` 33 tests, 6,372 links / 0 broken.
