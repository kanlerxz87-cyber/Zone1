# SOURCES.md — Source Register (repository index)

The full, row-by-row source register with "what was verified" per source is published on the site:

- **Live register:** [`docs/sources/index.html`](sources/index.html) (rendered on the GitHub Pages site)
- **Machine-readable:** [`../data/sources.json`](../data/sources.json)

## Rules applied

1. Only official domains carry value-bearing claims: `amazon.com`, `affiliate-program.amazon.com`,
   `webservices.amazon.com`, `kdp.amazon.com`, `ftc.gov`.
2. Every table row on the site links to one of these sources.
3. Anything unverifiable from an official source is left blank and flagged (see
   [`docs/flagged/index.html`](flagged/index.html)).
4. All sources accessed **2026-11-13**.

## Register at a glance

| # | Source | Verified from it |
|---|--------|------------------|
| 1 | [Associates Program Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) | Required disclosure text (§5); Special Links (§1) |
| 2 | [Associates Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | Commission rules; display restrictions (§2(b), §6(t), §2(y)); Agent Terms (IP License §4); ML limits (§5) |
| 3 | [Commission rate card](https://affiliate-program.amazon.com/help/operating/schedule) | Login-gated — rates unverified (F4) |
| 4–6 | Product pages [B0CDY277D3](https://www.amazon.com/dp/B0CDY277D3) · [B09B7SB46R](https://www.amazon.com/dp/B09B7SB46R) · [B08DKYBTPH](https://www.amazon.com/dp/B08DKYBTPH) | Listing titles, ASINs, category |
| 7 | [Best Sellers — Air Fryers](https://www.amazon.com/gp/bestsellers/kitchen/17659096011) | Category taxonomy; dated ranking snapshot |
| 8 | [PA API 5.0 GetItems](https://webservices.amazon.com/paapi5/documentation/get-items.html) | ASIN = 10-character identifier |
| 9 | [KDP Help G200652190](https://kdp.amazon.com/en_US/help/topic/G200652190) | ASIN = 10-character identifier (corroboration) |
| 10 | [FTC Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | Disclosure duty and placement rules |
| 11 | [404 evidence](https://www.amazon.com/dp/B04G1MEwY) | Provided IDs are not ASINs |
| 12 | [link.amazon observations](https://link.amazon/B04G1MEwY) | Stable redirect mapping (provenance flagged) |
