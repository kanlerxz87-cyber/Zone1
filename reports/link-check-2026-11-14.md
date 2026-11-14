# Independent re-check of the three supplied Amazon links — 2026-11-14

**Session:** `arena/1dcaaafc` (branch `arena/1dcaaafc-zone1`, base `8915b43`)
**Task:** T15 on the shared board (`COORDINATION.md`, "Integration pass 4")
**Method:** each URL fetched directly on 2026-11-14 (UTC) with the page fetch tool. For each request the table records the *final* URL after redirects and the page title. Nothing was copied from earlier sessions. Values are quoted exactly as returned.

## 1. The three supplied links

| # | Supplied link | Final URL after redirects (observed 2026-11-14) | Page title returned | Result |
|---|---|---|---|---|
| 1 | https://link.amazon/B04G1MEwY | https://www.amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-1e229870efde5acf&channelId=704&plpRedirect=mhFallback | "Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows … : Home & Kitchen" | Redirected to an Amazon URL carrying `lv=shuf` and `plpRedirect=mhFallback` (fallback parameters) |
| 2 | https://link.amazon/B02NbDxp3 | https://www.amazon.com/dp/B09B7SB46R?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-534f5e7952f396b2&channelId=704&plpRedirect=mhFallback | "Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven … : Home & Kitchen" | Same fallback parameters |
| 3 | https://link.amazon/B00hJ57DV | https://www.amazon.com/dp/B08DKYBTPH?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-76c3adaeb8708b44&channelId=704&plpRedirect=mhFallback&th=1 | "Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 … : Home & Kitchen" | Same fallback parameters |

Every redirect ends on a `/dp/<ASIN>` URL that carries `plpRedirect=mhFallback`. Amazon's `plpRedirect=mhFallback` parameter is the marker of the fallback path; the "Customers who viewed this item also viewed" carousel on these pages lists other products. A short link that resolves to a product the owner chose should not need that fallback marker. This session therefore **does not treat the three ASINs as confirmed identities** of the supplied links.

## 2. The 9-character codes as ASIN URLs

| Request | Final URL | Title / content | Result |
|---|---|---|---|
| https://www.amazon.com/dp/B04G1MEwY | same | "Page Not Found" — "Sorry! We couldn't find that page. Try searching or go to Amazon's home page." | No product |

The 9-character codes are not 10-character ASINs. The previous sessions and the sources cited on the site record that ASINs are 10 characters (for example the Product Advertising API documentation). That is the basis for treating the codes as non-ASINs. This session did not re-fetch the documentation, so that rule stays **as cited by earlier sessions** and is not restated here as newly verified.

## 3. The three ASIN URLs requested without the short link

| Request | Final URL | Title | Note |
|---|---|---|---|
| https://www.amazon.com/dp/B0CDY277D3 | …/dp/B0CDY277D3?lv=shuf&channelId=500&plpRedirect=mhFallback | CHEFMAN 6 Quart Dual Basket … | The plain ASIN URL also resolved to a fallback-parameter URL |
| https://www.amazon.com/dp/B09B7SB46R | …/dp/B09B7SB46R?lv=shuf&channelId=500&plpRedirect=mhFallback | Emeril Lagasse 26QT French Door … | Same |
| https://www.amazon.com/dp/B08DKYBTPH | …/dp/B08DKYBTPH?lv=shuf&channelId=500&plpRedirect=mhFallback&th=1 | Chefman Air Fryer 8 Qt TurboFry® 4-in-1 … | Same |

Observed in this session: even the plain 10-character ASIN URLs were answered with the fallback-parameter form. This means that **today's fetches cannot confirm from Amazon alone that each ASIN is served as its own live product page**. Prices in the fetched output ($69.97, $229.99, $99.99 and others) vary between requests and between the "also viewed" items, so they are not used anywhere on this site.

## 4. What is established, and what is not

**Established (2026-11-14, official amazon.com responses):**
- `amazon.com/dp/B04G1MEwY` (and the other two 9-character codes, checked in earlier sessions) returns Amazon's "Page Not Found" page.
- Each supplied `link.amazon` short link redirects to an Amazon `/dp/<ASIN>` URL that carries Amazon's fallback parameters (`lv=shuf`, `plpRedirect=mhFallback`).

**Not established:**
- That `link.amazon` is an Amazon-documented short-link domain. A web search on 2026-11-14 returned only third-party blogs that name `amzn.to` and `a.co`. No official Amazon page was found in this session that lists `link.amazon`. **Open item for manual review.**
- That any supplied link is the product the owner intended. The owner must supply the intended product (a 10-character ASIN or a full `amazon.com/dp/…` URL) to confirm identity.
- Any price, rating, review count, dimension, or commission rate for any product. None is stated on the site.

## 5. Consequence for the site

- The root landing page previously stated, as a headline, "3 Products resolved — All three short links followed to an ASIN." That sentence overstated the evidence, and it contradicted the dashboard's own finding of 0 verified identities. It is corrected in `build.py` `page_index` (see the T16 entry in `COORDINATION.md`).
- The product cards keep the three ASINs as **candidate** mappings, labelled as such, and continue to link to the supplied short links.

## 6. Items for owner review

1. Confirm the intended product for each supplied link (provide a 10-character ASIN or full product-page URL).
2. Confirm whether `link.amazon` is an Amazon-provided short-link domain. Official source needed: the Associates help pages on short links.
3. Confirm that the three ASIN pages are live (not fallback) from a logged-in Associates browser session.

## Sources (fetched 2026-11-14)

- https://link.amazon/B04G1MEwY
- https://link.amazon/B02NbDxp3
- https://link.amazon/B00hJ57DV
- https://www.amazon.com/dp/B04G1MEwY (Page Not Found)
- https://www.amazon.com/dp/B0CDY277D3
- https://www.amazon.com/dp/B09B7SB46R
- https://www.amazon.com/dp/B08DKYBTPH
