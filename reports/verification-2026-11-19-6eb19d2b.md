# Verification report — arena/6eb19d2b-zone1 (2026-11-19 UTC)

Scope: Z16-1 (independent live re-read of the five supplied `link.amazon` short links) and Z16-2 (overlap audit of open PRs touching the same pass work). No table data, no `data/*.json` value and no published flag was changed by this pass.

## Method

* Each supplied short link was opened with a live page fetch on 2026-11-19 (UTC). The final landing URL and the `<title>` of the landing page were recorded as returned by the fetch.
* Each landing page was compared with (a) the ASIN recorded for that supplied link in `data/product-intent.json` and (b) the title stored in `data/sources.json` on the earlier read.
* Prices, ratings and availability shown on the pages were **not** recorded or published, in line with the project's rule on Amazon price and rating data.
* This is an observation of what Amazon returned to a fetch. It is not confirmation of the Associates tag, of the account's enrolment or of the intended listing. Those remain open (see Z16-1 limits below).

## Observations

| # | Supplied link | Final URL (observed 2026-11-19) | ASIN | Landing `<title>` (observed 2026-11-19) | Matches register ASIN? | Matches stored title (2026-11-17 read)? |
|---|---|---|---|---|---|---|
| 1 | https://link.amazon/B04G1MEwY | https://www.amazon.com/dp/B0CDY277D3 | B0CDY277D3 | Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen | Yes | Yes, character for character (`data/sources.json`) |
| 2 | https://link.amazon/B02NbDxp3 | https://www.amazon.com/dp/B09B7SB46R | B09B7SB46R | Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included : Home & Kitchen | Yes | Yes (title as stored). Standing flag **F45**: the listing says "Six Cooking Accessories", the site publishes seven. Not changed here. |
| 3 | https://link.amazon/B00hJ57DV | https://www.amazon.com/dp/B08DKYBTPH | B08DKYBTPH | Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel : Home & Kitchen | Yes | Yes, character for character |
| 4 | https://link.amazon/B0c8moW59 | https://www.amazon.com/dp/B0DHZTCNR5 | B0DHZTCNR5 | Amazon.com: ThermoMaven 1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy \| NIST&NSF Certified, Auto-Rotate Bright LED Screen, **IP67 Waterproof for Grill BBQ, Stocking Stuffers Gifts for Men**, Black : Home & Kitchen | Yes | **No. Title wording has changed.** Stored (2026-11-17): "…NIST&NSF Certified Food Thermometer, Auto-Rotate Bright LED Screen, **Highly Waterproof for Grill BBQ Camping**, Black : Home & Kitchen". The ASIN and product type are unchanged. See irregularity **I-1** below. |
| 5 | https://link.amazon/B0f3GKalj | https://www.amazon.com/dp/B0DZFD6R9Z | B0DZFD6R9Z | Amazon.com: CHEF iQ Sense \| Smart Wireless Meat Thermometer \| 3 Ultra-Thin Probes \| WiFi Unlimited Range \| 1000°F Heat Safe \| 5 Sensors \| BBQ, Grill, Oven, Smoker, Air Fryer \| Gen3: Home & Kitchen | Yes | Yes, character for character |

Every landing URL still carries Amazon's own redirect and merchandising parameters (`lv=shuf`, `btn_type=ss`, `plpRedirect=mhFallback`, `btn_ref=srctok-…`). None of the five landing URLs shows a visible `tag=` parameter. That is the same null observation recorded in the register (F17 / F24). It does not prove that the tag is absent from the supplied short link, and it does not show that the tag is correct.

## Irregularities for review (non-blocking, not published as values)

* **I-1 — Listing title wording changed for ASIN B0DHZTCNR5 (supplied link 4).** Same ASIN and same product type on both reads (2026-11-17 and 2026-11-19). The title text differs in the phrases "Highly Waterproof for Grill BBQ Camping" and "IP67 Waterproof for Grill BBQ, Stocking Stuffers Gifts for Men", and the title also drops "Food Thermometer". The site does not publish a value from the title, so no page changes. The stored title in `data/sources.json` is left as recorded and is flagged here so the owner can decide whether to re-stamp it. Source to review: https://www.amazon.com/dp/B0DHZTCNR5 (final URL of https://link.amazon/B0c8moW59).
* **I-2 — Carried forward, unchanged:** F45 (Emeril accessory count, supplied link 2), F17/F24 (no visible `tag=` on any landing URL), and the unresolved compliance status of the supplied short links at Zone3 FLG-003 (https://kanlerxz87-cyber.github.io/Zone3/flagged.html#FLG-003). This pass does not declare that status either way.

## What this pass cannot confirm (left blank, not inferred)

* The Associates tag inside each supplied short link. This needs the account's own link-builder or reporting view, which this sandbox cannot reach.
* Whether `shopnow047c-20` is active on the account and attributed to these five products. This needs first-party reporting.
* Whether the supplied short links are the Special Link format described in Associates Program Policies §2(a). This needs a test in the enrolled account.
* Intended ASIN, official listing confirmation and the enrolled-link test. These remain blank in `data/product-intent.json` by design.

## Z16-2 — overlap audit of open PRs (recorded, not merged or closed)

All six open PRs below are from other sessions. Their titles were read from `gh pr list`. Their content was not reviewed line by line in this pass, and none of them was merged, closed or edited.

| PR | Title (as on GitHub) | Branch | Opened (UTC) |
|---|---|---|---|
| #173 | Pass 15: a probe-in-an-air-fryer guide, dated policy re-read, flags F105-F109 | arena/0c5c10d0-zone1 | 2026-11-19 11:15 |
| #168 | One site to index: de-index eight competing builds, repair the boundary at each generator, publish F104 | arena/95af246d-zone1 | 2026-11-19 10:56 |
| #159 | Publish Zone1 Kitchen and reconcile gated first-party measurement | arena/53d18637-zone1 | 2026-11-19 06:33 |
| #150 | COORDINATION: record X-16adefc5 (PR #149 merged, Pages confirmed, open items) | arena/16adefc5-zone1 | 2026-11-17 17:15 |
| #146 | C9: turn on click measurement (counter + self-hosted endpoint), publish question guides, mobile pass, and the one-site finding (F83) | arena/c9e97e02-zone1 | 2026-11-17 17:05 |
| #144 | pass 13 follow-up: the F82 repair shipped a false lede — classify the register as text, fail loud, guard the computed shape | arena/58cbaaa2-zone1 | 2026-11-17 16:59 |

Also open and older (not re-checked here): #141 (Pass 13: the Associates tag wired into the build) and #139 (Publish the two supplied links no earlier pass recorded). Two observations for the owner:

* #168 and #173 both change how the site is indexed and built, and #159 changes the analytics and first-party measurement path. Merging any one of them without the others risks a conflict in `build.py` and in the root HTML. Their order should be decided by the owner, not by this session.
* The pass-14 and pass-15 claims on `COORDINATION.md` already record a live re-read of the same five links. This report is an independent read on 2026-11-19 and does not replace those records.

## Gates on this branch

Run after the edits in this pass (see the completion record in `COORDINATION.md` for the exact results).
