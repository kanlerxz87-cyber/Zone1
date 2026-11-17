# Executive summary — product-intent and tracking pass (2026-11-17)

Branch `arena/1c97a25f-zone1`, base `9c6e3f0` on `main`. Session `1c97a25f`.
Page: [`product-intent.html`](https://kanlerxz87-cyber.github.io/Zone1/product-intent.html) (in the sidebar under *Products*).

## What the owner asked for, and what this pass delivered

| Ask | Status this pass | Where |
|---|---|---|
| Selected tracking ID `shopnow047c-20` | **Recorded, not applied.** Your brief requires one Special Link to be tested in the Associates workflow before scaling. That test needs an Associates Central login, which this build cannot use. | `data/config.json` (`selected_tracking_id`), `data/product-intent.json`, flag F76 |
| Product-intent confirmation record (intended ASIN, official listing URL, confirmation date and source, kept apart from observed redirects) | **Built for all 5 links.** No intended ASIN or listing is confirmed. The submitted URLs and observed destinations stay in separate fields; no validity conclusion is made from the path tokens. | `product-intent.html`, flag F77 |
| Five supplied links | Three observed page titles describe air fryers; two observed page titles describe meat thermometers. These are destination observations, not proof of intended products or a scope change. | flag F78 |
| Empty campaign ledger (no invented numbers) | **Built, empty.** No authorised first-party report has been added. | `data/campaign-ledger.json`, `product-intent.html` |
| Correct the S23 discrepancy | **Corrected and retained as F79.** S23 is registered as KDP's “Linking from Your Website” page; the product-intent page no longer cites it for a general ASIN definition or `/dp/` format. | flag F79 |
| Disclosure, rel="sponsored", unique titles and descriptions | Already present on every page; re-checked by `verify.py` (0 errors) and `build.py` guards. | existing |

## The five supplied links

| # | Short link | Observed on 2026-11-17 | Air-fryer scope? | Register |
|---|---|---|---|---|
| PI-01 | link.amazon/B04G1MEwY | amazon.com/dp/B0CDY277D3 (Chefman 6 Qt Dual Basket) | Yes | matches S16 / S17 |
| PI-02 | link.amazon/B02NbDxp3 | amazon.com/dp/B09B7SB46R (Emeril 26 Qt French Door) | Yes | matches S28 / S17; accessory count still open (F48) |
| PI-03 | link.amazon/B00hJ57DV | amazon.com/dp/B08DKYBTPH (Chefman 8 Qt TurboFry) | Yes | matches S29 / S17 |
| PI-04 | link.amazon/B0c8moW59 | amazon.com/dp/B0DHZTCNR5 (ThermoMaven 1 Sec thermometer) | **No** | new: S36 |
| PI-05 | link.amazon/B0f3GKalj | amazon.com/dp/B0DZFD6R9Z (CHEF iQ Sense thermometer) | **No** | new: S37 |

Sources: [S17 link.amazon short links](https://link.amazon/B04G1MEwY) · [S16](https://www.amazon.com/dp/B0CDY277D3) · [S28](https://www.amazon.com/dp/B09B7SB46R) · [S29](https://www.amazon.com/dp/B08DKYBTPH) · [S36](https://www.amazon.com/dp/B0DHZTCNR5) · [S37](https://www.amazon.com/dp/B0DZFD6R9Z) · [S6 tracking IDs](https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA) · [S5 identify as an Associate](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) · [S2 Program Policies](https://affiliate-program.amazon.com/help/operating/policies)

## Decisions only the owner can make

1. **Test the tracking ID** (F76). Create one Special Link for one product in Associates Central, follow it, and confirm the destination and the tracking report. Then say so, and the ID can be applied.
2. **Confirm the intended listing for each short link** (F77), so intended ASIN and official URL can be filled.
3. **Keep or drop the two thermometer links** (F78). Keeping them means sourced specification rows for each product before any page is published.
4. **F79 disposition:** the claim was dropped from the owner-facing intent page pending verification of a suitable official source; the source mismatch remains documented for audit.

## Not done in this pass (honest list)

The brief is much wider than this pass. These items are **not** built here and remain open:

- A product-led storefront landing page and a reader-facing redesign (the current landing page is unchanged).
- The outbound-click counter and a self-hosted analytics endpoint. These need a hosting decision; GitHub Pages can't run an endpoint.
- Search Console, a feed-submission step, and reader capture (SG-27 to SG-30).
- New question-shaped guides and a publishing calendar.
- Real product photography (needs a licensing decision, S-18).

## Verification performed

- Each Amazon link was fetched on 2026-11-17 and its final URL and `<title>` recorded (fetch tool; the build host cannot reach Amazon directly).
- Gates, all green on the final tree: `build.py` (50 pages, sitemap 50 URLs), `research/check_research.py`, `verify.py` (0 errors, 37 sources, 0 external warnings), `scripts/check_links.py` (8,595 links, 0 broken), `scripts/build_s2_site.py --check`, `platform/audit/report.py`, platform unit tests, `node --check assets/app.js`, `git diff --check`.
- The build guards caught two real defects while this pass was written (broken in-page flag anchors; an unsourced placeholder row). Both were fixed before commit.

## Irregularities for review

- **F76–F79** on `flagged.html`, each with its source links.
- Two flag registers still disagree (existing F44/F47): unchanged in this pass.
