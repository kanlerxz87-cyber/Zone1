# Verification pass — arena/6ace936d-zone1 — 2026-11-19 (UTC)

**Session:** arena/6ace936d-zone1 (session 6ace936d)
**Base:** main @ `2be3bea` (merge of PR #163)
**Scope:** independent line-by-line repo review and live re-verification of the
official sources behind the published values; structural checks of the generated
site against the standing brief; no product, account or campaign data changed.

## Method

- Every URL below was fetched **live on 2026-11-19** through a server-side
  fetch (`fetch_page`) and the value was read from the response body in this
  session. Values were not copied from earlier sessions' records.
- The sandbox shell itself has no direct egress to non-GitHub hosts
  (`curl` to `www.amazon.com` / `link.amazon` fails with `SSL_ERROR_SYSCALL`);
  all live reads in this pass were therefore performed with the server-side
  fetch tool. This is a transport note, not a finding about any source.
- Verdicts: **confirms** = the live read matches the registered value;
  **note** = the live read is consistent but carries a date-stamp or wording
  nuance recorded below.

## A. The five supplied links, re-opened live

| Supplied link | Final URL observed today | Title read back today | Verdict |
|---|---|---|---|
| https://link.amazon/B04G1MEwY | `https://www.amazon.com/dp/B0CDY277D3` (`plpRedirect=mhFallback`) | "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black" | confirms PI-01 |
| https://link.amazon/B02NbDxp3 | `https://www.amazon.com/dp/B09B7SB46R` (`plpRedirect=mhFallback`) | "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included" | confirms PI-02 |
| https://link.amazon/B00hJ57DV | `https://www.amazon.com/dp/B08DKYBTPH` (`plpRedirect=mhFallback`) | "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel" | confirms PI-03 |
| https://link.amazon/B0c8moW59 | `https://www.amazon.com/dp/B0DHZTCNR5` (`plpRedirect=mhFallback`) | "ThermoMaven 1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy \| NIST&NSF Certified Food Thermometer, Auto-Rotate Bright LED Screen, Highly Waterproof for Grill BBQ Camping, Black" | confirms PI-04 |
| https://link.amazon/B0f3GKalj | `https://www.amazon.com/dp/B0DZFD6R9Z` (`plpRedirect=mhFallback`) | "CHEF iQ Sense \| Smart Wireless Meat Thermometer \| 3 Ultra-Thin Probes \| WiFi Unlimited Range \| 1000°F Heat Safe \| 5 Sensors \| BBQ, Grill, Oven, Smoker, Air Fryer \| Gen3" | confirms PI-05 |

Breadcrumbs read on the landing pages: the three air fryers print
`Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers`
(leaf node 17659096011); the two thermometers print
`Home & Kitchen › Kitchen & Dining › Kitchen Utensils & Gadgets › Thermometers & Timers › Meat`
(leaf node 289810). These match the `observed_browse_path` values recorded on
PI-01..PI-05. No final URL carried a visible `tag=` parameter; per S41 (read
live below) that is a null observation, not evidence of failed attribution, and
it is not read in either direction.

## B. Policy and legal sources, re-read live

| Source | URL | What was read back today | Verdict |
|---|---|---|---|
| S1 Operating Agreement | https://affiliate-program.amazon.com/help/operating/agreement | Heading "Associates Program Operating Agreement", "Updated: October 15, 2025"; §1 defines Special Links as links that "must properly use the special 'tagged' link formats we provide" | confirms |
| S2 Program Policies | https://affiliate-program.amazon.com/help/operating/policies | "Updated: April 14, 2026"; Commission Income Statement, Participation Requirements, Products Statement sections present | confirms |
| S3 Commission Income Statement | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | Table 1 read in full without login: "Physical Books, Kitchen, Automotive — 4.50%"; "All Other Categories — 4.00%" | confirms |
| S4 Application Review Process | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM | "at least three [qualified sales] within the first 180 days"; "at least 10 posts"; content "recent (generally within the last 60 days)"; social pages "at least 500" followers; FAQ defines special "tagged" links as "identifiers (e.g. abcd-20) embedded in Amazon product links" | confirms |
| S5 Identify yourself as an Associate | https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98 | Required sentence quoted verbatim: "As an Amazon Associate I earn from qualifying purchases."; link-level disclosure must be clear and conspicuous, "placed near any affiliate link or product review" | confirms (matches the site's masthead + footer disclosure exactly) |
| S6 Tracking IDs | https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA | Tracking IDs analyse performance under a single Associates ID; created via "Manage your Tracking ID"; per-ID reports exist | confirms (supports the recorded handling of tracking ID `shopnow047c-20`: recorded, not validated, not applied) |
| S8 FTC Disclosures 101 | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | Disclose financial/material connections; disclosure placed "so it's hard to miss"; "You can't talk about your experience with a product you haven't tried" | confirms |
| S9 16 CFR Part 255 | https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255 | "up to date as of 11/17/2026"; §255.0–§255.6 present, including §255.5 "Disclosure of material connections" | confirms — **note:** eCFR freshness date advanced from 11/12/2026 (the value quoted in the 2026-11-15 record) to 11/17/2026; Part 255 content unchanged |
| S31 Google — qualify outbound links | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links | `rel="sponsored"` marks "links that are advertisements or paid placements (commonly called paid links)"; multiple space-separated values allowed; page "Last updated 2025-12-10 UTC" | confirms (matches the site's `rel="sponsored nofollow noopener"`) |
| S41 Why doesn't my tracking ID appear in the URL | https://affiliate-program.amazon.com/help/node/topic/GF4RJEQNXSMR7SP3 | Verbatim: "it is not necessary for your unique ID to appear in order for us to track sales made after the initial click through. The individual shopping session will be tagged…" | confirms the `observation_method_correction` on the product-intent record |

## C. Product and brand sources, re-read live

| Source | URL | What was read back today | Verdict |
|---|---|---|---|
| S10 Chefman 6 Qt Dual-Window | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | Model `RJ38-SQPF-3TDB-2W`; "TurboFry® Touch 6 Qt. Dual-Window Air Fryer"; "Max temp: 450ºF/ 235ºC with Hi-Fry function"; Sync function for both baskets | confirms published 6 Qt rows |
| S14 Emeril French Door 360 | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | Specifications block: "26-Quart Capacity", "25 Cooking Pre-sets", "16.9\"D x 15.8\"W x 14.8\"H", "24.6 Liters", "120 volts"; model 4-00675-02A-VN; body copy still says "10-in-1" | confirms capacity/dimensions/voltage; the preset count conflict (25 spec block vs 24 listing title vs 10-in-1 body) remains open exactly as flagged — no value changed |
| S39 CHEF iQ iQ Sense | https://chefiq.com/products/iq-sense | Current default selection is one-probe `CQ60-1C-Z1-E`, with 1–4 probe and two colour options; heat resistance "up to 1,000ºF (537ºC)"; "4 internal temperature sensors… 1 ambient temperature sensor"; air fryer named among compatible environments | confirms PI-05 brand-catalogue check ("consistent with, not confirmed by"); no intended-ASIN match established |
| S40 ThermoMaven | https://www.thermomaven.com/ | Catalogue leads with F1 Turbo ("0.5s Instant Read, ±0.5℉, IP67") and wireless lines (G2, P2, WT02 Lite); "1 Sec" is not used as a model name anywhere on the page | confirms PI-04 brand-catalogue check — **note:** the 2026-11-17 record's wording "names its instant-read line F1 Pro and F1 Turbo" stands as a record of that date; today's homepage leads F1 Turbo and no F1 Pro was seen. The verdict (not reconciled; intended product stays null) is unchanged |

## D. Structural checks of the generated site (root canonical build)

| Check | Method | Result |
|---|---|---|
| Every outbound `amazon.com` link qualified | Scanned every `<a href="https://www.amazon.com/…">` on index, categories, products, articles, compare, picks, guides | 0 unqualified; 310 links carry `rel="sponsored nofollow noopener"` |
| Disclosure above the fold on every page | Line position of the Associate sentence vs `<main>` on index, category, product, article, compare, picks | Disclosure at line 55, `<main>` at line 59, on every checked page type; repeated in the footer (2 occurrences per page) |
| Unique title + meta description per page | `<title>` and `name="description"` on 13 representative pages | All present and unique |
| Structured data | `application/ld+json` blocks | Present on 35 canonical pages |
| Sitemap / RSS | `sitemap.xml` (36 URLs), `feed.xml` (24 items) | Present; canonical reader pages listed |
| Five defined events | `measurement.html` | `page_view`, `outbound_click`, `article_engagement`, `comparison_interaction` (browser) + `affiliate_report_import` (operator-only); production analytics remains off |
| Campaign ledger | `data/campaign-ledger.json` | Empty by design; no conversion score or revenue forecast published |
| Product-intent record | `data/product-intent.json` | Intent fields (`intended_asin`, `official_listing_url`, `confirmation_date`, `confirmation_source`) blank for all five; observed redirect fields separate and populated; the two fields are never merged |
| Tracking ID `shopnow047c-20` | `data/product-intent.json` | Recorded, `applied_to_links: false`, `associates_central_confirmed: false` — unchanged |

## E. Gates run from this tree

- `python3 build.py` — clean; regeneration is byte-reproducible (`git status` empty after rebuild).
- `python3 verify.py` — 136 pages checked, 77 spec rows (75 verified, 2 blank + flagged), 45 sources, 0 errors, 0 external warnings.
- `bash scripts/ci-check.sh` — build, verify, Python publication tests, 8 Node client-contract tests, 33 engine unit tests, data audit clean, s2 build check, link check 11,297 links: **all pass**.

## F. Irregularities and non-claims

- **No new defects found** in this pass. The structural checks in §D all pass.
- **F95 (channelId variance)** — the landing URLs observed today carry varying
  `channelId` values per request; already recorded; not read as evidence.
- **eCFR freshness date** — advanced 11/12/2026 → 11/17/2026; content unchanged.
  Recorded here; the published value on the site is the regulation, not the
  freshness date.
- **ThermoMaven wording nuance** — see §C; no published value depends on it.
- **Explicitly not verified in this pass (and not claimed):** Associates
  Central account state; whether tracking ID `shopnow047c-20` exists on the
  account; enrolled per-product Special Link tests; production analytics
  runtime; Search Console ownership or query data; product-photography rights.
  No account, link-test or campaign report is fabricated to clear any gate.

*Evidence for this pass is also recorded in `data/sources.json` under
`reverified_2026_11_19_6ace936d` and in `COORDINATION.md`.*
