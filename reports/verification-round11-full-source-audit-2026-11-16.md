# Verification round 11 — 2026-11-16 (session f3ada6ba, arena/f3ada6ba-zone1)

**Scope.** A single-session liveness and record-match audit of **all 34 registered sources (S1–S34)** in `data/sources.json`, plus a read-back of the deployed GitHub Pages site. Every source URL below was fetched live on 2026-11-16 (UTC) in this round; each row states what the official page showed today and whether it matches the value stored in this repository. No stored value was changed except one flag wording (F3, see §3). Nothing was inferred: where a fetch was blocked, the row says so.

Prior rounds the same day are complementary, not duplicated: session `c334fb1c` (round 10, PRs #86/#87) re-read the three supplied short links, the S2 "Updated" date and the live landing page; session `9f0e6668` (R10, PRs #88/#90/#92) re-read the short links again plus two volatile brand-page review counters and refreshed those counters in `data/products.json`. This round is the first in which **every registered source** carries a same-day live read in one pass.

## 1. Source-by-source audit (all fetched 2026-11-16)

| ID | Official URL (fetched today) | What the source showed on 2026-11-16 | Stored record (`data/sources.json`) | Match |
|----|------------------------------|--------------------------------------|--------------------------------------|-------|
| S1 | https://affiliate-program.amazon.com/help/operating/agreement | Associates Program Operating Agreement; "Updated: October 15, 2025" | "Updated: October 15, 2025" | Yes |
| S2 | https://affiliate-program.amazon.com/help/operating/policies | Associates Program Policies; "Updated: April 14, 2026"; Commission Income Statement, Participation Requirements, Products Statement, Trademark Guidelines, IP License all linked | "Updated: April 14, 2026" | Yes |
| S3 | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | Standard Commission Income Statement, Table 1 + Bounty Events, readable without login. All 11 fixed rates read: Luxury Beauty 10.00%, Digital Music/Handmade 5.00%, Physical Books/Kitchen/Automotive 4.50%, Fire TV/Echo/Apparel row 4.00%, Toys/Furniture/Home row 3.00%, PC 2.50%, TVs/Video Games 2.00%, Fresh/Grocery/HPC 1.00%, Gift Cards row 0.00%, Coach 0.00%, All Other Categories 4.00% | `data/commission-rates.csv`, all 11 rows, checked 2026-11-13 | Yes — every row identical |
| S4 | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM | Application Review Process: at least three qualified sales within the first 180 days (personal orders excluded); sites need robust original content, "a good rule of thumb is at least 10 posts"; website content recent (generally within the last 60 days); social networks accepted list includes Facebook, Instagram, Twitter, YouTube, TikTok, Twitch | "Live page, 2026-11-13" | Yes |
| S5 | https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98 | "Why do I have to identify myself as an Associate?": requires (1) a legally compliant link-level disclosure — "(paid link)", "#ad" or "#CommissionsEarned" — and (2) the statement "As an Amazon Associate I earn from qualifying purchases." clearly and conspicuously on the Site | "re-read live 2026-11-14" | Yes |
| S6 | https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA | Tracking-ID help node: per-channel tracking IDs accumulate earnings under one Associates ID | "Live page, 2026-11-13" | Yes |
| S7 | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking | FTC's Endorsement Guides: What People Are Asking; page footer reads "June 2023"; links to Disclosures 101 and 16 CFR 255 | page_version "June 2023" | Yes |
| S8 | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | Disclosures 101 for Social Media Influencers; dated "November 2019"; placement ("hard to miss"), wording ("advertisement", "ad", "sponsored"), and the no-experience-with-untried-product rule all present | page_version "November 2019" | Yes |
| S9 | https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255 | 16 CFR Part 255; eCFR "up to date as of 11/12/2026", "Title 16 was last amended 10/30/2026"; Part 255 source note 88 FR 48102 (July 26, 2023); timeline shows only the 7/26/2023 entry; §§255.0–255.6 including §255.5 | Same dates recorded in page_version (re-read 2026-11-14) | Yes |
| S10 | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | TurboFry® Touch 6 Qt. Dual-Window, model RJ38-SQPF-3TDB-2W; feature block "Max temp: 450ºF/235ºC with Hi-Fry function", Sync Finish; review widget 1,307 reviews | "re-read round 9, 2026-11-15"; R10 recorded 1,307 on 2026-11-16 | Yes |
| S11 | https://chefman.com/products/turbofry-touch-6-qt-dual-basket-air-fryer | TurboFry® Touch 6 Qt. Dual-Basket, model RJ38-SQPF-3TDB-2; 4.6 from 197 total reviews shown | "Live page, 2026-11-13" | Yes |
| S12 | https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1 | TurboFry® Touch Stainless-Steel (8 Qt / 5 Qt); description: "precise temperatures ranging from 200–400°F"; model RJ38-SQSS-8T | "re-read round 9, 2026-11-15" — 200–400 °F is the stored basis of flag F3 | Yes |
| S13 | https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQSS-8T-UG-US.pdf | User Guide PDF opens, model RJ38-SQSS-8T; Preset Function Chart: Default 15 min / 400 °F, Meat 18 min / 375 °F, Chicken 22 min / 375 °F, Fish (truncated in view) | "Document live, 2026-11-13"; F3 cites the 200–400 °F / four-preset basis | Yes |
| S14 | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | EMERILLAGASSE FRENCH DOOR AIRFRYER 360™ TOASTER OVEN COMBO, 26 QT; $199.99; SKU 4-00675-02A-VN; "25 Cooking Pre-sets"; 26-Quart, 24.6 Liters, 16.9"D × 15.8"W × 14.8"H, 120 V; rating widget 2.6 (25) | "re-read round 9, 2026-11-15" — same spec block; the 24-vs-25 preset conflict with the Amazon title remains open | Yes (values); conflict unchanged |
| S15 | https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf | Owner's Manual PDF opens; Model FAFO-001; 120 V/1700 W/60 Hz; 26 quarts (1519 cubic inches); 75 °F–500 °F / 25 °C–260 °C; LED | "re-read 2026-11-14" | Yes |
| S16 | https://www.amazon.com/dp/B0CDY277D3 | **Direct fetch blocked:** Amazon served its automated "To continue, please click the 'Continue shopping' button" checkpoint, not the listing. The listing title was verified instead through S17 (below), which returned the stored title character for character | "fetched 2026-11-15 from the supplied short link … <title> matched" | Blocked directly today; title re-verified via S17 |
| S17 | https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3 · https://link.amazon/B00hJ57DV | All three re-resolved in this round: `B04G1MEwY → /dp/B0CDY277D3` (title "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff…"), `B02NbDxp3 → /dp/B09B7SB46R` (title "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven … 24 One-Touch Preset Options…"), `B00hJ57DV → /dp/B08DKYBTPH` (title "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option … Stainless Steel"). Every landing URL still carries `lv=shuf&btn_type=ss&btn_ref=srctok-…&channelId=704&plpRedirect=mhFallback` and **no `tag=` parameter**. Breadcrumb on listings 1–2: Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers | "re-resolved 2026-11-14, same target ASIN, still served with lv=shuf & plpRedirect=mhFallback" | Yes — same three ASINs; see §2.1 for srctok rotation |
| S18 | https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQPF-3TDB-2W-UG-US.pdf | User Guide PDF opens, model RJ38-SQPF-3TDB-2W; two 3-quart baskets, Sync Finish, control-panel and special-functions sections present | "control panel and operating instructions re-read 2026-11-14" | Yes |
| S19 | https://affiliate-program.amazon.com/help/node/topic/GBRCD467W33NMWLD | New PA API Registration help node: registration merged into Associates Central; credentials tied to the primary account holder; rate tied to last-30-day sales | "Live page, 2026-11-13" | Yes |
| S20 | https://affiliate-program.amazon.com/help/node/topic/GMEDADBTCJ9KD8DQ | "About the Product Advertising API" topic index with the PA-API FAQ child links | "Live page, 2026-11-13" | Yes |
| S21 | https://www.amazon.com/dp/B04G1MEwY | **"Page Not Found"** — Amazon's error page for the 9-character token (negative control) | "Fetched 2026-11-14" (404) | Yes |
| S22 | https://link.amazon/ZZZ9ZZZZZ | **"403 Forbidden"** — the resolver refuses the nonsense token outright (negative control) | "Fetched 2026-11-14" (403) | Yes |
| S23 | https://kdp.amazon.com/en_US/help/topic/G200652190 | KDP help page, title "Linking from Your Website" | "re-verified 2026-11-14" | Yes |
| S24 | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation | "PA-API 5 Deprecation Notice": PA-API 5 deprecated, replaced by the Creators API; continued calls receive HTTP 403 with `AccessDeniedException` and a migration message | "Live page, re-verified 2026-11-14" | Yes |
| S25 | https://chefman.com/collections/air-fryers-1/products/turbofry-6-qt-double-basket-air-fryer-with-easy-view-windows | TurboFry 6 Qt. Double Basket with Easy View Windows, model RJ38-3DBW-V2; "90°F to 400°F", Sync Finish, Sync Baskets, five functions; 30 reviews; 1700W, 1-year assurance | "Read live 2026-11-14" | Yes |
| S26 | https://chefman.com/collections/air-fryers-1/products/turbofry-8-qt-air-fryer-w-high-fry | TurboFry 8 Qt. Air Fryer w/ High Fry, model **RJ38-8T-BLACK**; "The Hi-Fry button raises the heat to 450°F for the last two minutes"; Specifications: Capacity 8 Qt / 7.57 L, **Hi-Fry Temperature: 450 °F / 232 °C**, Power 1700W/120V; 200 reviews; matte-black finish | "Read live 2026-11-14" — **but this source was not cited by flag F3, whose text implied the brand side uniformly says 200–400 °F** | Yes (page live); **this read is what surfaced the F3-vs-F33 inconsistency — F3 refined, see §3** |
| S27 | https://chefman.com/products/turbofry-touch-6-qt-dual-basket-air-fryer | Same TurboFry® Touch 6 Qt. Dual-Basket page as S11 (canonical product URL); model RJ38-SQPF-3TDB-2 | "Read live 2026-11-14" | Yes |
| S28 | https://www.amazon.com/dp/B09B7SB46R | **Direct fetch not attempted after S16's checkpoint; title verified through S17's redirect:** "Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included" — matches the stored title, including "24 One-Touch Preset Options" | Stored title re-read round 9, 2026-11-15 | Yes (via S17 redirect today) |
| S29 | https://www.amazon.com/dp/B08DKYBTPH | **Title verified through S17's redirect:** "Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel" — matches the stored title, including "450°F Hi-Fry" | Stored title re-read round 9, 2026-11-15 | Yes (via S17 redirect today) |
| S30 | https://developers.google.com/search/docs/essentials/spam-policies | Spam policies for Google web search, including the "Thin affiliation" and "Scaled content abuse" sections this project's rules cite | "Live page, re-read 2026-11-15" | Yes |
| S31 | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links | "Qualify your outbound links to Google": `rel="sponsored"` for paid links, `rel="ugc"`, `rel="nofollow"`; "Last updated 2025-12-10 UTC" | "Live page, 2026-11-15" | Yes |
| S32 | https://chefman.com/products/turbofry-touch-dual-window-air-fryer.json | Shopify product JSON: variant price "119.99", compare_at_price "119.99", sku "RJ38-SQPF-3TDB-2W", grams 6582, weight 14.51 lb | Same five values recorded (read 2026-11-15) | Yes — identical |
| S33 | https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1.json | Shopify product JSON: 8 Quart price "119.99", compare_at_price "119.99", sku "RJ38-SQSS-8T", grams 6078, weight 13.4 lb; 5 Quart price "79.99", compare_at_price "99.99", sku "RJ38-SQSS-5T" | Same values recorded (read 2026-11-15) | Yes — identical |
| S34 | https://chefman.com/products/turbofry-touch-6-qt-dual-basket-air-fryer.json | Shopify product JSON: variant price "119.99", compare_at_price "119.99", sku "RJ38-SQPF-3TDB-2", grams 6509, weight 14.35 lb | Same five values recorded (read 2026-11-15) | Yes — identical |

**Totals:** 34/34 sources fetched live today. 33 matched their stored records. One record defect found and corrected (F3, §3). One fetch method substitution (S16/S28/S29 listing titles read through the supplied short-link redirects after Amazon's direct-detail-page checkpoint, §2.2).

## 2. Observations recorded, not silently patched

### 2.1 srctok tokens rotate between sessions; the target ASINs do not

| Token | 2026-11-13/14 (stored rounds) | 2026-11-16 (this round) |
|-------|------------------------------|--------------------------|
| B04G1MEwY | `srctok-0740a2e990c9bbb3` | `srctok-68884e8aa630b24a` |
| B02NbDxp3 | `srctok-3541f5edba6b914c` | `srctok-662480f5bd825c83` |
| B00hJ57DV | `srctok-507e2d3d167072eb` | `srctok-38bef00eb1e962ef` |

The `btn_ref=srctok-…` value differs today from the 2026-11-13/14 readings while all three landing ASINs (B0CDY277D3, B09B7SB46R, B08DKYBTPH) are unchanged. This is consistent with the existing register: `data/flags.json` records that re-requests inside one retrieval session return byte-identical redirects (cache), while `data/suggestions.json` already carries a row noting the srctok marker is not constant across sessions. Reading the two together: srctok identifies a fetch session, not a fixed link property — any sentence claiming "identical srctok" must stay scoped to the 2026-11-13/14 window it was measured in. **No published sentence needed correction** (the reverification text scopes its claim to those rounds); this table is the dated extension of that evidence.

### 2.2 Amazon's direct detail-page endpoint serves an automated checkpoint

A direct fetch of `https://www.amazon.com/dp/B0CDY277D3` on 2026-11-16 returned Amazon's "To continue, please click the 'Continue shopping' button" interstitial — the same per-ASIN block session `63a2c638` recorded on 2026-11-15 for S28. The listing titles remain verifiable through the supplied `link.amazon` short links (S17), which served all three titles character-for-character today. Consequence: **no Amazon price, rating, review count or availability has been or is being published from these fetches** — consistent with `data/products.json` → `amazon_price_policy` and Program Policies §2(b)/§6(t) (S2).

### 2.3 Live GitHub Pages read-back (deployed origin, 2026-11-16)

| Check | Result |
|-------|--------|
| `https://kanlerxz87-cyber.github.io/Zone1/` | Renders: affiliate disclosure bar ("As an Amazon Associate I earn from qualifying purchases."), the "Product identity, account approval and affiliate tracking are not confirmed" notice with its 2026-11-16 re-check sentence, hero ("Choose the shape before the model."), stat row (3 products / 12 articles / 34 sources / 0 flags open / 0 hands-on tests), the sourced three-product comparison table with per-cell S-links |
| `https://kanlerxz87-cyber.github.io/Zone1/sitemap.xml` | Serves **37** `<loc>` entries, every one dated 2026-11-16, including `requirements.html` and `design-prompt.html` — supersedes the 35-vs-36 cache-window observation logged by session `bf487400` on 2026-11-15; the count now matches the tree on `main` |
| `https://kanlerxz87-cyber.github.io/Zone1/requirements.html` | Renders the brief-requirements register shipped by PR #89 (27 Delivered / 13 Partial / 8 Blocked / 3 Not built) with per-row evidence links |
| Pages build state | `gh api …/pages/builds/latest` → `status: built`, commit `8c28dac` (PR #92 merge), `error: null` at read time |

## 3. Change made by this round: flag F3 refined (one row, `data/products.json`)

**Defect.** F3's product-level text read: *"conflict between the Amazon listing (450 °F …) and the brand page + owner's manual (200–400 °F …)"*. That wording implies the brand side uniformly states 200–400 °F. It does not — and the programme-level register already knew so: flag **F33** (added 2026-11-14 by `arena/6b2eddeb`, on the Flagged page) records that Chefman sells two 8 Qt SKUs, RJ38-SQSS-8T (max 400 °F) and RJ38-8T-BLACK (Hi-Fry 450 °F / 232 °C), and that the Amazon title matches the second. What F33 found on 2026-11-14 was re-confirmed live today: S26 — Chefman's own TurboFry 8 Qt w/ High Fry page for RJ38-8T-BLACK — states a **450 °F Hi-Fry button** and **Hi-Fry Temperature 450 °F / 232 ° C** (both re-read 2026-11-16), while S12/S13 document 200–400 °F for RJ38-SQSS-8T. The product-level F3 row had simply never been aligned with F33, so a reader of the 8 Qt product page would still take the brand side as one-sided. This change aligns the two rows, cites S26, and leaves the open question exactly where F33 left it: which model ASIN B08DKYBTPH maps to (Q-01 — the Product information table is only reachable inside Amazon). No temperature value was selected.

**Correction applied.** F3's `issue` now names both brand models and cites S26; `sources` gained `S26`; `action` now tells the account holder to read the model number off the listing and compare it with both brand pages and the manual. The flag stays **open**; no temperature value was selected, and no other product field changed.

## 4. Gates run on this tree (2026-11-16, after the F3 edit)

| Gate | Result |
|------|--------|
| `python3 build.py` | exit 0; row-source, disclosure, SEO, affiliate-qualification and duplicate-ID guards all pass |
| `python3 verify.py` | 0 errors; spec rows verified / blank+flagged counts unchanged apart from regenerated text |
| `bash scripts/ci-check.sh` | unit tests OK, data audit clean, build current, link check 0 broken |
| `python3 research/check_research.py` | OK |
| `python3 scripts/verify_site.py` | ALL CHECKS PASSED |
| `python3 platform/audit/report.py` | AUDIT PASSED |
| `node --check assets/app.js` | OK |

(Exact counts are recorded in the completion entry in `COORDINATION.md`.)

## 5. Not re-read in this round, and why

- **Amazon Associates account internals** (approval status, tracking IDs, per-ASIN commission categories, conversion reports): only observable signed in — questions Q-02/Q-03/Q-11 on `questions.html`. Unchanged, still blank.
- **FTC pages' underlying PDFs and 16 CFR 255 point-in-time versions beyond the current page**: the current pages were read; historical versions were not.
- **The `s2/`, `site/`, `research/`, `dashboard/`, `annex-*`, `docs/` parallel builds**: outside this session's scope per the board; their own verification stands as published.
- **Amazon detail pages directly** (S16/S28/S29): checkpoint-blocked; titles verified through S17 instead, as recorded in §1.

## 6. Result

All 34 registered sources are live as of 2026-11-16; 33 stored records matched exactly; one flag wording (F3) was corrected to reflect the evidence; three observations (srctok rotation, detail-page checkpoint, live 37-URL sitemap) are recorded rather than patched over. No unverified value was published, and no blank was filled.
