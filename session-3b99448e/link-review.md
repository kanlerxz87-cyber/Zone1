# Zone1 — T13 link re-review: the three `link.amazon` short links

Session: `3b99448e` | Branch: `arena/3b99448e-zone1` | Date: 2026-11-15 (UTC)

**Scope:** Re-review the three supplied short links against the official sources already recorded in this repo. **No live Amazon fetching was performed in this session** (outbound sandbox access does not include amazon.com); this pass relies on evidence previously fetched live and recorded in `data/sources.json`, `data/products.json`, `data/products.csv`, and `reports/link-check-2026-11-14.md`.

## Supplied links

| # | Supplied link | Token length | ASIN standard length | Valid ASIN format? |
|---|---------------|--------------|----------------------|--------------------|
| 1 | https://link.amazon/B04G1MEwY | 9 chars | 10 chars | No |
| 2 | https://link.amazon/B02NbDxp3 | 9 chars | 10 chars | No |
| 3 | https://link.amazon/B00hJ57DV | 9 chars | 10 chars | No |

## What the recorded official evidence shows

1. **The tokens are not ASINs.** Amazon's own definition (S23, KDP Help G200652190): "the ASIN is a 10-character Amazon Standard Identification Number" and the canonical product URL is `http://www.amazon.com/dp/ASIN`. All three tokens are 9 characters → format-invalid as ASINs.

2. **Opening a token as an ASIN fails.** `https://www.amazon.com/dp/B04G1MEwY` returned Amazon's "Page Not Found" error page on 2026-11-13 and again on 2026-11-14 (S21 — negative control). Same finding applies by analogy to B02NbDxp3 and B00hJ57DV (products.csv, canonical_check_result).

3. **The short links resolve through Amazon's fallback handler.** All three `link.amazon/` links redirect to `amazon.com/dp/<ASIN>` but carry `plpRedirect=mhFallback`, and the landing titles are unrelated/random listings (B0CDY277D3, B09B7SB46R, B08DKYBTPH) described in products.csv as "session shuffle, not the intended product" (S17).

4. **The resolver distinguishes recognised from unrecognised tokens.** A made-up 9-character token (`link.amazon/ZZZ9ZZZZZ`) returns 403 Forbidden rather than a shuffled product (S22 — negative control), which shows the resolver has a recognition step; the three supplied tokens are recognised but their destinations are not provably the intended products.

5. **Candidate ASINs vs. intended identity.** The observed destination listings are:
   - B0CDY277D3 — "CHEFMAN 6 Quart Dual Basket Air Fryer Oven … 2 Independent 3Qt …" (S16)
   - B09B7SB46R — Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven (S16)
   - B08DKYBTPH — "Chefman Air Fryer 8 Qt | TurboFry® 4-in-1 … Stainless Steel" (S16)
   
   All three are home-kitchen air fryers, which supports the **niche** but not the **identity**: whether any destination ASIN is the product the link was created for remains unconfirmed.

## Conclusion

| Question | Answer | Basis |
|----------|--------|-------|
| Are the tokens valid ASINs? | No (9 chars vs. 10) | S23 |
| Does `amazon.com/dp/<token>` work? | No — 404 | S21 |
| Where do the short links point? | To air-fryer listings via `plpRedirect=mhFallback` | S17 |
| Are those the intended products? | **Unconfirmed** | Destination ≠ identity; tag inside short link not observable (S2/S17) |

## What would confirm identity (requires account-holder action)

- Open each short link in a normal browser (signed out, then signed in) and compare the final listing title/model with the intended product.
- Replace short links with canonical tagged `/dp/<ASIN>` URLs once the Associates tag is confirmed (Q-1/Q-2 in `session-3b99448e/decisions.md`).
- Contact the brands (Chefman/Emeril) to confirm which model number each ASIN carries.

## Related flags

- F-01: short links resolve via a redirect handler carrying a fallback marker (`flagged.html`)
- F-06/F-10: Associates tag inside the short link not observable; attribution unconfirmed
- F-07: `link.amazon` shortening compliance under Amazon Program Policies §2(w) flagged for the account holder

## Sources (all official, recorded in `data/sources.json`)

- S16: Amazon detail pages for ASINs B0CDY277D3, B09B7SB46R, B08DKYBTPH — https://www.amazon.com/dp/B0CDY277D3
- S17: link.amazon short links supplied by the account holder — https://link.amazon/B04G1MEwY
- S21: Negative control — `amazon.com/dp/B04G1MEwY` returns "Page Not Found"
- S22: Negative control — `link.amazon/ZZZ9ZZZZZ` returns 403
- S23: Amazon KDP Help — ASIN is a 10-character identifier; canonical URL format `/dp/ASIN` — https://kdp.amazon.com/en_US/help/topic/G200652190
