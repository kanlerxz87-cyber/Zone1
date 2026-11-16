# Targeted source verification — 2026-11-16

**Scope:** targeted follow-up during integration. This is not a full line-by-line re-read of every repository claim, product specification, policy quotation, or parallel build. It re-reads the three supplied short links, the two volatile manufacturer review counters that were stale on the root site, the current Emeril conflict, and official program/disclosure sources. No price, Amazon review count, star rating, stock status, or inferred commission rate was copied into the product data.

## Findings

| Claim checked | Official source observation on 2026-11-16 | Outcome | Official source |
|---|---|---|---|
| `https://link.amazon/B04G1MEwY` destination | Amazon's title identifies the CHEFMAN 6 Quart Dual Basket Air Fryer; fetched URL contains `/dp/B0CDY277D3` and `plpRedirect=mhFallback`. | Same candidate destination observed. This does not confirm the owner's intended product or the Associates tag. | [Amazon supplied short link](https://link.amazon/B04G1MEwY) |
| `https://link.amazon/B02NbDxp3` destination | Amazon's title identifies the Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven; fetched URL contains `/dp/B09B7SB46R` and `plpRedirect=mhFallback`. The title says 24 one-touch preset options and six accessories. | Same candidate destination observed. This does not confirm the owner's intended product or the Associates tag. | [Amazon supplied short link](https://link.amazon/B02NbDxp3) |
| `https://link.amazon/B00hJ57DV` destination | Amazon's title identifies the Chefman 8 Qt TurboFry with a 450°F Hi-Fry option; fetched URL contains `/dp/B08DKYBTPH` and `plpRedirect=mhFallback`. | Same candidate destination observed. This does not confirm the owner's intended product or the Associates tag. | [Amazon supplied short link](https://link.amazon/B00hJ57DV) |
| Chefman 6 Qt on-site review counter | Product page displayed **1,307 Reviews**. The current fetch did not establish the current average; the previously recorded 4.6/5 remains explicitly dated to 2026-11-15. | Count changed from 1,305 on 2026-11-15 to 1,307 on 2026-11-16. Product data now separates the dated average from the current count. | [Chefman 6 Qt product page](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) |
| Chefman 8 Qt on-site review counter | Product page displayed **717 Reviews**. The current fetch did not establish the current average; the previously recorded 4.6/5 remains explicitly dated to 2026-11-15. | Count changed from 716 on 2026-11-15 to 717 on 2026-11-16. Product data now separates the dated average from the current count. | [Chefman 8 Qt product page](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) |
| Emeril official product-page figures | Page displayed 2.6 (25), “25 Cooking Pre-sets,” “10-in-1,” and an image described as “11-in-1”; the linked Amazon title above says 24 one-touch preset options. | Conflict remains open; no preset count was selected or inferred. Rating unchanged. | [Emeril Everyday product page](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) |
| Amazon Associates policies | Policies page still says “Updated: April 14, 2026.” | No version change observed. | [Amazon Associates Program Policies](https://affiliate-program.amazon.com/help/operating/policies) |
| Amazon commission table | Table 1 still lists Kitchen at 4.50%, Home within the 3.00% row, and All Other Categories at 4.00%. It does not name air fryers or publish the ASIN-to-category mapping used for settlement. | Category rate per product remains blank/unverified. | [Amazon Associates Standard Commission Income Statement](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| FTC disclosure guidance | FTC guidance still instructs that disclosures be hard to miss and cautions against describing experience with a product that was not tried. | The site's non-hands-on framing remains consistent with this guidance. | [FTC — Disclosures 101 for Social Media Influencers](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) |
| Current eCFR status | eCFR reports Title 16 up to date as of 2026-11-12 and lists 16 CFR Part 255, including §255.5. | Current official status recorded; no compliance text changed. | [eCFR — 16 CFR Part 255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) |

## Limitations and irregularities retained

1. The Amazon redirects still expose the fallback marker `plpRedirect=mhFallback`. These are observations of current destinations only—not proof of the account holder's intended products, link ownership, a tracking tag, attribution, or an approved Associates account.
2. The Emeril product materials still disagree about functional count. The current manufacturer page says 25 pre-sets and 10-in-1, one image is identified as 11-in-1, and the linked Amazon title says 24 preset options. The comparison remains conservative and the existing flag remains open.
3. Manufacturer-hosted review counters moved in one day. They are point-in-time brand-page counters, not Amazon review data, product testing, sales, conversion rates, or evidence of trend demand.
4. This follow-up does not validate every stored product specification, every parallel site build, or account-only data (tracking IDs, Associates application approval, actual commission report, or conversions). Those limits remain documented in the site's decision and flagged registers.

## Changes made from this evidence

- Updated only the two Chefman brand-site review counts in `data/products.json`, preserving the last-seen rating average with its date and explicitly stating that the latest fetch confirmed the count only.
- Added the 2026-11-16 reads to the relevant manufacturer source records in `data/sources.json`.
- Published this scoped follow-up table on the site's Re-verification page with a separate official source link in every row.
- No short-link identity, Amazon price/review metric, commission mapping, or conflicting Emeril preset value was filled in.
