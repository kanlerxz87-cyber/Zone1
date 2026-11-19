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
| Program Policies, selected chunks 0, 3, 4, 5, 7, 8, 9 | Privacy accuracy, link clarity, no artificial clicks/incentives, restricted Program Content/price/review/API uses; update stamp 14 April 2026 | A legal opinion or account-specific permission | [Policies](https://affiliate-program.amazon.com/help/operating/policies) |
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

Local pre-integration gates passed on 19 November 2026:

- `python3 build.py`: 58 canonical pages, 36 sitemap URLs and 24 feed items.
- A second root build: 64 canonical artifacts hashed, **zero changed**.
- `python3 verify.py`: 136 pages, 77 specification rows (75 populated/sourced, two blank/flagged),
  43 registered sources, zero errors and zero external-host warnings. This is a structural check,
  not a fresh semantic verification of every specification.
- Canonical Python tests: **30 passed**; JavaScript client tests: **8 passed**.
- `scripts/ci-check.sh`: **33 platform tests**, clean data audit, 16 current s2 artifacts and
  11,917 links checked (13 owned pages plus 123 inherited/advisory).
- Independent `site/`: **393 assertions passed**. Research: **834 checks passed**. Rebuilding
  either section produced **no diff**; neither independent generator or dataset was rewritten.
- Browser acceptance: **70 combinations** (14 representative pages × 320/390/768/1024/1440 px),
  five interaction groups and three no-JS groups; local fonts/images loaded, disclosure above
  fold, no document overflow, external request or page error. The run caught a real 320 px
  owner-stat path overflow, now fixed. Filters, native-menu keyboard/outside-click behaviour,
  table keyboard scrolling, suggestion search/anchor recovery, honest denied clipboard feedback,
  and an isolated local-only choice/export/clear fixture were exercised. No Amazon link was
  activated. Screenshots remain ignored development evidence, not product/test photography.

A late fetch found additional main-branch work merged while this pass was running (PRs
#152–#158). Integration with `cb33d97` retained its source/redirect observations, all history,
SG-49/50, Q-41, F90–F95, sponsored-anchor fix, exact-file requirement targets and directory guard,
flag-label/anchor guard and explicit desk inventory. The sidebar-only UI assertions were updated
to the native Workspace, and its guard now verifies both the actual menu and footer. Tests for
price policy follow the explanation's new journal location; the policy distinction itself is
retained. Our new flags moved in one pass to **F96–F99**; no upstream ID was reassigned.

**Post-integration re-run:** root build/verify; **36 Python**, **8 JavaScript**, **33 platform**
tests; 393 annex assertions; 834 research checks; **11,987 links**; 64-artifact deterministic
rebuild; no independent output drift. The 70-combination browser suite passed again with all
49 suggestions / 41 questions retained. No local conflict marker remains in source or output.

### Released and read back — 19 November 2026

- [PR #160](https://github.com/kanlerxz87-cyber/Zone1/pull/160) passed both checks before merge:
  [canonical CI](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44473639156) and
  [independent annex](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44473639101).
- Merged with explicit `gh pr merge 160 --merge` at **06:39:46 UTC**, merge commit
  **`4baab6289b68b56d1e3f8ed0a5f2c53208d465d4`**. No auto-merge flag, unrelated PR merge,
  branch switch or forced push was used.
- [Build, verify and deploy](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44473800015)
  succeeded, including rebuild/reproducibility and deploy, completed **06:40:27 UTC**.
  Main-branch [CI](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44473799872),
  [annex](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44473799968), and
  [Pages build](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44473799059) also succeeded.
- The Pages API returned **`built`**, no error, and that exact merge commit, updated
  **06:40:08 UTC** (21,445 ms). The existing configuration remains **legacy / main / root**;
  it was not silently changed to another deployment source. The Actions deployment result is
  separately linked above.
- Actual public fetches after deployment returned the redesigned home (both canonical URL and
  a release-query read), new product guide, honest About method/imagery, revised extension-cord
  article, current suggestion desk (**11 implemented / 21 partial / 17 proposed**), named
  five-event measurement page marked **not active**, the five-link intent record with selected
  ID unconfirmed, the local-font/cream-forest stylesheet and the revised RSS text/date. These
  were **Pages reads**, not responses from the sandbox preview.
- Live readback is a scoped content/stylesheet retrieval, not an assertion that a remote browser
  was screen-reader tested or that the fetch service exposes every raw HTML attribute. Disclosure
  placement, all commercial `rel` tokens, disabled script emission, metadata, keyboard/no-JS and
  network behaviour were checked on the deterministic artifact in the local and GitHub CI
  browser suites. No synthetic Amazon activation was made.
- Informational CI annotation: inherited checkout/setup action versions target deprecated Node
  20 and GitHub currently runs them on Node 24. Checks passed; that warning is not hidden as
  “zero CI warnings” and does not mean an application dependency or production endpoint failed.

Public readback entry points:
[home](https://kanlerxz87-cyber.github.io/Zone1/) ·
[product guide](https://kanlerxz87-cyber.github.io/Zone1/products/chefman-6qt-dual-basket.html) ·
[corrected manual article](https://kanlerxz87-cyber.github.io/Zone1/articles/extension-cord-rules-in-the-manuals.html) ·
[About](https://kanlerxz87-cyber.github.io/Zone1/about.html) ·
[suggestions](https://kanlerxz87-cyber.github.io/Zone1/suggestions.html) ·
[measurement](https://kanlerxz87-cyber.github.io/Zone1/measurement.html) ·
[intent](https://kanlerxz87-cyber.github.io/Zone1/product-intent.html) ·
[stylesheet](https://kanlerxz87-cyber.github.io/Zone1/assets/style.css) ·
[RSS](https://kanlerxz87-cyber.github.io/Zone1/feed.xml).

The code publication is released. Production analytics and enrolled Associates confirmation
remain deliberately **unverified**, not retroactively passed because Pages deployed.

## What remains outside repository authority

A durable same-origin analytics runtime and host/proxy privacy review; enrolled Associates
access and link/report tests; intended listing confirmation; Search Console account access;
original/licensed product photography; a human reviewer identity and an agreed ongoing
publishing owner/cadence. These are explicit gates, not missing numbers to estimate.

## Existing-article review and substantive corrections

Read all 24 existing title/standfirst/body sets; rewrote them **in place**, without adding
another article. This does not retroactively certify every historical table or annex.
The fresh reads below explain why passing the older value/citation tests was insufficient.

- **S15 — extension-cord conflict (F96).** In the FAFO-001 manual, Important Safeguards item 9
  says “NEVER use with an extension cord.” The later **Attaching the Power Cord** section says
  “Longer extension cords are available and may be used if care is exercised in their use” and
  gives conditions. Both passages were returned by the official PDF on 19 November. The earlier
  article quoted one and called the rule absolute. The correction reports the conflict, does
  not select the permissive passage and refers the exact-unit question to the manufacturer.
  [Official manual](https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf)
- **S13 — aerosol warning really exists (F97).** Under Operating Instructions, the RJ38-SQSS-8T
  manual says “Never use aerosol spray on the air fryer's nonstick parts as it can cause the
  coating to chip” and permits oil from a mister. The aerosol, cleaning and percentage-claim
  articles had said this rule was absent. Their text is corrected; a short dataset care cell
  is not evidence that the source contains no additional instructions.
  [Official manual](https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQSS-8T-UG-US.pdf)
- **S15 — rotisserie facts were not absent (F97).** The accessory weight table lists the spit
  at **6 lb (2721 g)**. The preset table supplies default settings and the document contains an
  internal-temperature meat chart. Earlier claims that no maximum weight, suggested time or
  doneness temperature appeared were false. The revised guide names the limit and existence
  of those sections, without validating or republishing the food-temperature chart as current
  public-health advice. Exact Amazon SKU/bundle identity remains unconfirmed.
- **S13/S18 — oil and cleaning.** Both manuals contain practical oil guidance and suggested
  quantities; the dual manual's troubleshooting mentions a half-teaspoon example. Removed the
  false claim that no quantities are stated, the invented coating-lifespan outcomes and the
  implication that Emeril's recommended accessory hand-washing is a universal explicit
  dishwasher ban. Cooled Chefman baskets/racks are documented top-rack dishwasher-safe.
- **S18 — sync modes.** Corrected the idea that only Hi-Fry and +2 MIN can break Sync Finish:
  the manual also says adjusting a timer while both sides are actively cooking breaks sync.
  Timer coordination is not doneness or food-safety confirmation.
  [Official dual manual](https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQPF-3TDB-2W-UG-US.pdf)
- **S26 — distinct High Fry model.** Freshly read the exact registered page, not a guessed URL:
  RJ38-8T-BLACK, matte black, four functions and a two-minute 450 °F finish. This documents a
  different manufacturer model, **not** its identity behind the submitted link. Removed the
  articles' probability rankings and assertions about which seller/title error “most likely”
  occurred. A guessed `/products/turbofry-touch-high-fry-air-fryer` path returned a branded 404;
  no product fact was adopted from that failed request.
  [Registered official page](https://chefman.com/collections/air-fryers-1/products/turbofry-8-qt-air-fryer-w-high-fry)
- **Capacity, energy and seasonality.** Removed the “same nominal total” claim for six versus
  eight quarts, undocumented usable-volume/footprint and portion conclusions, full-cycle power
  presented as exact energy cost, unsupported electrical-code assumptions and the alleged
  November acceleration of seller/stock changes. A dated editorial model-check surface is not
  a live deal, a verified switch, a trend or proof of audience demand.
- **Policy accuracy.** Re-read the Operating Agreement sections 5/6, policy sections 2(b),
  3(e), 6(t)/(y), IP/API conditions and FTC disclosure guidance. Corrected the claim that the
  required disclosure has no allowed historical alternative; the site still uses the exact
  prescribed sentence. Removed broad legal/health classifications and guarantees unsupported
  by those sources. The site makes no certification of legal compliance.

## Date and decision-state repair

The earlier Article/RSS code derived publication from `articles.accessed=2026-11-14` and
constructed 09:00 UTC without publication evidence. All 24 `published_at` values remain null;
optional `datePublished`/RSS `pubDate` are omitted. Actual `modified_at` was recorded when the
articles were revised (19 November 2026), and per-article `source_checks` lists **selected**
documents read that day. The register's historical access dates are preserved. Sitemap
`lastmod` now describes actual content edits; running a build does not advance a timestamp.
Feed GUIDs are unchanged. Repository presence or a source read is not a first-publication
receipt. No missing date was guessed merely to obtain richer search metadata.

The suggestion desk now renders explicit `implemented`/`partial`/`proposed` states instead of
inferring completion from an “effort” string or any past execution entry. SG-01 is correctly
partial while intended listing fields remain null. Current states, alternatives, recommendations,
questions, missing facts and discovery steps are separately reviewable. The old numeric
impact/confidence opinions remain in historical source data, not as invented performance or a
current displayed priority ranking. Search is progressively enhanced; no-JS readers retain
all cards. Question/decision summaries render full citation arrays instead of hiding all but
the first source. The existing whole-row official-host gate is **not** misdescribed as semantic
or dedicated-citation-cell verification. Owner `choices[]` remains empty.
