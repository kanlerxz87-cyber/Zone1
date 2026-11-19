# Zone1 Kitchen — publication and measurement integration

**Review date:** 19 November 2026 UTC  
**Working branch:** `arena/7d42af7c-zone1`  
**Canonical publication:** <https://kanlerxz87-cyber.github.io/Zone1/>

## What this pass is, and is not

This is a canonical-root publication rebuild and a targeted engineering/source review. It is
**not** a claim that a person has manually re-read every line in every historical annex, that
every volatile product value was checked today, or that an Associates account was accessed.
Historical verification dates remain historical. The separate `site/`, `s2/`, `research/`,
`docs/`, `dashboard/`, annex and session evidence is preserved, not silently restyled.

No production analytics endpoint, conversion result, customer report, verified tracking ID,
intended product identity, licensed product photograph or human hands-on test has been
invented. No new article is being added just to increase the article count. The existing
question-led collection is retained, with substantive corrections recorded separately below.

## Implemented engineering changes

1. **One analytics protocol.** The browser previously emitted legacy EV-ID/raw-event fields
   while the Python endpoint accepted named events. There were also different definitions of
   engagement and comparison. `analytics/client.js` is now published verbatim, the two data
   registers must agree, and real client fixture payloads pass the actual Python validator.
2. **Fail closed, consistently.** Both collection switches must agree. Same-origin route,
   runtime/deployment flags and privacy review are build gates. The client is not loaded while
   collection is disabled. No link is opened, delayed or rewritten by measurement.
3. **Retired incompatible storage.** `analytics/endpoint.php` and `analytics/worker.js` now
   return HTTP 410 without reading or storing event bodies. The only supported implementation
   is the Python UTC-day aggregate collector; the former Worker array update was not atomic.
4. **Accurate privacy boundaries.** The footer distinguishes site analytics, the local-only
   owner picker and GitHub's documented security IP logging. A private collector's disabled
   access log cannot certify a hosting proxy's logs. Production stays off.
5. **A reader-first publication.** Shared masthead, disclosure immediately beneath it, a
   format-led product shelf, product/category/comparison routes, question-led journal,
   seasonal model-check reading, editorial method and RSS. Owner/evidence pages remain in
   one workspace menu and the footer. No audit metric tiles lead the home page.
6. **Honest imagery.** Original schematic SVGs describe formats, not branded products.
   Clearly labelled AI-generated preparation/food scenes are generic editorial atmosphere,
   not product photographs or test results. An initially generated appliance scene was
   rejected and is not published. SG-42/Q-34's product-photography restriction remains.
7. **Local assets and progressive controls.** Fonts and their OFL licences are served from
   this repository. Format filters, native workspace disclosure, scrollable tables and the
   local decision picker remain separate from analytics. Without JavaScript all formats and
   all article text remain readable.
8. **Dimension lookup repaired.** The 8 Qt record uses “Dimensions / weight”, not “Dimensions”.
   The front-page card no longer mislabels the existing manufacturer dimensions as missing.
   Compact cards omit the weight portion; the full sourced field is preserved.
9. **Subpath navigation checked.** The root comparison template now uses root-page relative
   paths directly. Existing final-output normalisation already removed parent prefixes,
   and a strict browser-style `/Zone1/` check found no published root escape. This is
   template cleanup and added regression coverage, not a demonstrated live broken-link fix.

## Official sources re-read in this pass

These are scoped observations from fresh page/manual reads on **2026-11-19**, not a global
new `accessed` stamp for the whole dataset. A source page is not account evidence. Some long
pages were read in selected chunks; the table states the facts actually adopted.

| Source / scope | What the read supports | What it does not establish | Official source |
|---|---|---|---|
| Associates Operating Agreement, chunks 0–1 | Provided Special Link formats, the exact Associates statement and no income guarantee; update stamp 15 October 2025 | This site's acceptance, account ownership or attribution | [Agreement](https://affiliate-program.amazon.com/help/operating/agreement) |
| Program Policies, selected chunks 0, 4, 5, 7, 8, 9 | Privacy accuracy, link clarity, no artificial clicks/incentives, restricted Program Content/price/review/API uses; update stamp 14 April 2026 | A legal opinion or account-specific permission | [Policies](https://affiliate-program.amazon.com/help/operating/policies) |
| FTC disclosure guidance | Clear material-connection disclosure and no invented product experience | A human test or a legal-compliance certification for this site | [FTC](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) |
| Chefman dual-window product page and store record | RJ38-SQPF-3TDB-2W; 6 Qt; published 13.38 × 11.81 × 10.63 in dimensions | Intended listing identity or independently tested performance | [Brand page](https://chefman.com/products/turbofry-touch-dual-window-air-fryer), [store record](https://chefman.com/products/turbofry-touch-dual-window-air-fryer.js) |
| Dual-window owner manual, chunks 0 and 2 | Two 3-quart baskets; Hi-Fry is a two-minute 450 °F boost; removing a basket pauses both; sync exceptions; care instructions | A sustained 450 °F cooking-cycle claim or actual food results | [Manual](https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQPF-3TDB-2W-UG-US.pdf) |
| Chefman 8 Qt product page and store record | RJ38-SQSS-8T and distinct 5 Qt variant; 200–400 °F; published 8 Qt dimensions 15.4 × 12.6 × 13.5 in | Resolution of the Amazon-title 450 °F conflict | [Brand page](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1), [store record](https://chefman.com/products/turbofry-touch-air-fryer-1.js) |
| Chefman 8 Qt manual, chunks 0 and 2 | Model-specific care, do not overcrowd, check food/doneness rather than relying on time alone | Proof that a differently worded listing ships this exact machine | [Manual](https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQSS-8T-UG-US.pdf) |
| Emeril product page, chunks 0–1 | 26 Qt; 16.9 D × 15.8 W × 14.8 H in; SKU 4-00675-02A-VN; preset/accessory copy conflicts remain | Exact listing-SKU equivalence or a tested winner | [Brand page](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) |
| Emeril FAFO-001 manual, chunk 0 | FAFO-001, 26 Qt, 1700 W, 120 V, 75–500 °F; 5 in clearance; no under-cabinet operation/extension cord | Permission to operate under a cabinet just because exterior dimensions fit | [Manual](https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf) |
| Tracking-ID creation/report help | Create IDs in the enrolled account and inspect the Tracking ID Summary Report | That `shopnow047c-20` exists, is active, or is on these links | [Amazon help](https://affiliate-program.amazon.com/help/node/topic/GJDYPQZK6E37RLPU) |
| Missing-visible-tag help | An ID need not remain visible in the final URL; the session may still be tagged | Positive or negative attribution from URL inspection alone | [Amazon help](https://affiliate-program.amazon.com/help/node/topic/GF4RJEQNXSMR7SP3) |
| Standard Commission Income Statement | Current general Kitchen rate row is 4.5% | Product-specific category assignment, conversions or a revenue forecast | [Official rate table](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| CHEF iQ iQ Sense page | Several probe/colour variants; internal/ambient-sensor wording is not uniform | Exact specifications of the supplied three-probe listing | [Brand page](https://chefiq.com/products/iq-sense) |
| ThermoMaven home catalogue | Current F1 family context, not the precise “1 Sec” listing identity | A matched intended model or its claimed certification | [Brand site](https://www.thermomaven.com/) |
| Google paid-link guidance | Paid links use `sponsored`; multiple `rel` values are allowed | Any ranking, traffic or conversion gain | [Outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) |
| Google spam guidance, selected chunks 0, 2, 4 | Useful original affiliate value; no scaled low-value pages or unauthorised automated rank queries | Popularity, search demand, indexing or improved rankings for this site | [Spam policies](https://developers.google.com/search/docs/essentials/spam-policies) |
| GitHub Pages documentation | Static hosting, and security IP logging by GitHub | A running Python collector or a no-logs guarantee by the host | [Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) |

Chefman's two brand review widgets had moved from the saved counts (1,310 and 717) to 1,312
and 719 during the fresh reads. They are volatile vendor widgets, not independent tests or
Amazon ratings. No such rating/count is used as front-page or product-page social proof;
historical dataset observations keep their own dates rather than being silently presented as
live. No new Amazon price/review/image dataset has been extracted.

### Exact supplied-link observations — not intended identity

Each exact string below was followed in a fresh fetch. Each yielded a fallback-style
`/dp/…` destination with `plpRedirect=mhFallback` and no visible `tag=` in the returned URL.
That absence is a **null observation**, not evidence of failed attribution, as Amazon's
[official help](https://affiliate-program.amazon.com/help/node/topic/GF4RJEQNXSMR7SP3) explains.
No intended ASIN, official-listing confirmation or enrolled test is inferred from this table.

| Record | Exact submitted source | Observed destination | Scope / official context |
|---|---|---|---|
| PI-01 | [B04G1MEwY](https://link.amazon/B04G1MEwY) | `https://www.amazon.com/dp/B0CDY277D3` | Chefman dual-basket title observed; [Special Link rules](https://affiliate-program.amazon.com/help/operating/agreement) |
| PI-02 | [B02NbDxp3](https://link.amazon/B02NbDxp3) | `https://www.amazon.com/dp/B09B7SB46R` | Emeril 26QT title observed; [Special Link rules](https://affiliate-program.amazon.com/help/operating/agreement) |
| PI-03 | [B00hJ57DV](https://link.amazon/B00hJ57DV) | `https://www.amazon.com/dp/B08DKYBTPH` | Chefman 8 Qt/450 °F title observed; [Special Link rules](https://affiliate-program.amazon.com/help/operating/agreement) |
| PI-04 | [B0c8moW59](https://link.amazon/B0c8moW59) | `https://www.amazon.com/dp/B0DHZTCNR5` | ThermoMaven 1 Sec title observed; [Special Link rules](https://affiliate-program.amazon.com/help/operating/agreement) |
| PI-05 | [B0f3GKalj](https://link.amazon/B0f3GKalj) | `https://www.amazon.com/dp/B0DZFD6R9Z` | CHEF iQ Gen3 three-probe title observed; [Special Link rules](https://affiliate-program.amazon.com/help/operating/agreement) |

The exact short-link compliance question remains unresolved in the user-specified
[FLG-003 record](https://kanlerxz87-cyber.github.io/Zone3/flagged.html#FLG-003).
This report does **not** declare the submitted links invalid. The five intended ASIN/URL/date/
source fields remain empty; the selected ID remains user-provided, account-unconfirmed and
not newly applied by this pass. The campaign ledger remains empty.

## Review and verification record

Checkpoint already completed: **17 Python tests + 8 JavaScript contract tests**, the root
build and `verify.py` passed before the visual rebuild. This is not the final integration
result. Final all-gate, browser and deployment results will be recorded here after they run;
an incomplete check is not called a pass.

- Full root build / reproducibility: pending final run.
- Canonical HTML and strict `/Zone1/` subpath links: pending final run.
- Platform, annex and research gates: pending final run.
- Responsive Chromium, keyboard, no-JavaScript and privacy-network checks: pending final run.
- PR, merge commit, Pages run and live readback: pending final run.

## What remains outside repository authority

A durable same-origin analytics runtime and host/proxy privacy review; enrolled Associates
access and link/report tests; intended listing confirmation; Search Console account access;
original/licensed product photography; a human reviewer identity and an agreed ongoing
publishing owner/cadence. These are explicit gates, not missing numbers to estimate.
