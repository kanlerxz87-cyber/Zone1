# Executive summary — buyer-questions guide and gap register (2026-11-17)

Branch `arena/66c32067-zone1`, base `e5fc007` on `main`. Tracking ID applied since PR #128 / #131: `shopnow047c-20` (on every `/dp/` link, `rel="sponsored"`).

## What this pass delivered

| Brief item | Status | Where |
|---|---|---|
| Question-shaped guide, fourth working title "Questions to ask before buying a multi-function kitchen appliance" | **Published.** Six questions, each answered only with values already in `data/products.json` (build guard checks every quoted value). Judgement is labelled as judgement. | `articles/multi-function-buying-questions.html`, `data/articles.json`, topic TP-21 in `data/topics.json` |
| Add each new guide to the sitemap and feed | Done automatically by the build: sitemap 52 URLs, feed 22 items | `sitemap.xml`, `feed.xml` |
| Three other working titles | Already covered by published articles: TP-05 (basket vs oven), TP-03 (capacity), TP-04 and TP-18 (counter space, cleaning). Their titles differ from the working titles; they were not renamed. | `topics.html` |
| Five-event outbound-click measurement | **Not shipped, deliberately.** The site is static GitHub Pages with no endpoint to receive events, and the footer says no analytics run. Shipping a beacon would make that statement false, and a counter with no endpoint would invent numbers. Still blocked on an endpoint you control. | `measurement.html`, `data/measurement.json` |
| Search Console, reader capture, nav/RSS pass (SG-27 to SG-30) | **Not done.** Search Console and any reader-capture form need your Google and hosting accounts. | `suggestions.html` |
| Publishing cadence | **Not set here.** A cadence is a decision for you. | `suggestions.html` |
| Product photography (S-18) | **Not done.** Needs a licensing decision first. | `suggestions.html` |
| Storefront landing page redesign | **Not done in this pass.** The current landing page already puts the three products and the sourced matrix ahead of the verification layer, and the disclosure bar sits above the fold. | `index.html` |

## Verification performed

- **Gates, green:** `build.py` (exit 0; 52 sitemap URLs, 22 feed items), `verify.py` (0 errors; 77 spec rows: 75 verified, 2 blank and flagged; 37 sources), `scripts/ci-check.sh` (8,856 links, 0 broken), `research/check_research.py`, `scripts/verify_site.py`.
- **Live re-read, 2026-11-17:**
  - Emeril product page (S14): 26-Quart capacity, 16.9"D × 15.8"W × 14.8"H, 24.6 Liters, 120 volts, and the sentence "Included are 7 premium accessories" — all match.
  - Chefman 8 Qt brand page (S12): product name, 200–400°F range, presets, and dishwasher-safe basket and rack — match.
  - Amazon listing B08DKYBTPH (the 8 Qt): page title matches the registered listing identity. Its dimensions field was **not** in the chunks read this pass, so the 12.75" × 13.5" × 10" figure in the new article rests on the earlier dated read (S29) and is not re-confirmed here.
- Amazon prices and ratings were seen on the live page and **deliberately not recorded**. Program Policies do not permit publishing them on this site.

## Decisions only you can make

1. **Click and conversion measurement.** Choose a host you control for a collector endpoint. Until then, no counts will be shown.
2. **Publishing cadence and Search Console.** Choose a cadence and confirm you will add the site property in Search Console.
3. **Photography rights (S-18).** Decide whether any product imagery may be used, and whose permission covers it.
4. **Tracking test (F76).** Still open: one Special Link tested in Associates Central, with the destination and the tracking report checked.

## Irregularities for review

- The 8 Qt listing dimensions (S29 vs S12) disagree; both are published, neither chosen (flagged in the new article and on `flagged.html`).
- Emeril page presents "24 one-touch cooking presets" in its description and "25 Pre-sets" in its spec block; this is already on the presets conflict register.
- Pre-existing open items unchanged: F3, F4/F5, F70, F71, F11, F76, F81, F82, Q-01/Q-02/Q-04.
