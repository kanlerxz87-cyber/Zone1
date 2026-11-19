# Acceptance review verification — X-e3ac0e8d

**Date:** 2026-11-19 UTC
**Branch:** `arena/e3ac0e8d-zone1`
**Reviewed `main`:** `cb33d97e1fe7c17e1ab1d943af4349ace17a271e`
**Live Pages snapshot:** `main` at `cb33d97`
**Scope:** acceptance review of the canonical root site, five supplied-link records, source/data contracts, build gates, buyer-facing pages, disclosures and product-link qualification, measurement status, and repairs published on `main`.

## Verdict

**Build/source and canonical publishing gates pass. Overall acceptance is conditional.** This review does not validate intended product identity, Associates Central account state, tracking attribution, Search Console data, analytics collection, clicks, orders or conversions. Some published passages still contradict the current source records, so the project is not approved to make unqualified attribution or measurement claims. These copy/register repairs are recorded here rather than implemented: `COORDINATION.md` assigns this review read-only scope on shared build/data/generated files.

## Review boundary and evidence limits

- The local checkout was rebased onto `main` at `cb33d97`, which includes pass 14 (PR #157) and its deployment record (PR #158). The rebase encountered an append-only `COORDINATION.md` conflict; the pass-14 record and this review's task board/log were both retained.
- Public Pages reads were made against the deployed `main` snapshot. The build/deploy, Pages deployment, annex verification and CI runs for `cb33d97` succeeded: [44468415447](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44468415447), [44468414860](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44468414860), [44468415345](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44468415345), and [44468415388](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44468415388). This review branch's reports are not public until merged; GitHub Pages serves `main`.
- Amazon page/redirect reads establish only what was observed on a public request. No Associates Central login, account page, Tracking ID Summary Report or Earnings report was available. No Search Console property was accessed. No private or server-side analytics data was available.
- This review did not edit `build.py`, `data/*.json`, canonical generated HTML or parallel build output. The task changes are limited to these reports and the X-e3ac0e8d record in `COORDINATION.md`.

## Local build and verification gates

Commands were re-run after the rebase onto `cb33d97`; all exited successfully.

| Command | Result |
|---|---|
| `python3 build.py` | Built 56 canonical HTML pages (2,843 KB); generated `sitemap.xml` with 35 URLs and `feed.xml` with 24 items. |
| `python3 verify.py` | 134 pages checked; 77 spec rows (75 asserted, 2 blank+flagged); 43 sources; 0 errors; 0 external warnings. One caution-status note remains for `chefman-8qt-turbofry` / Basket divider. |
| `bash scripts/ci-check.sh` | 33 tests passed; data audit clean; 16-file annex current; link check passed 11,464 links (13 owned by this session, plus 121 inherited/advisory). |
| `python3 research/build_research.py` + `python3 research/check_research.py` | Research output rebuilt (12 pages); 834 checks passed; no broken links, unsourced rows or missing disclosures. |
| `python3 scripts/build_site.py` + `python3 scripts/verify_site.py` | Separate legacy `site/` build checked; 393 assertions passed. This is not the canonical root build. |
| `python3 platform/audit/report.py` | 0 errors, 0 warnings, 0 findings. |
| `python3 scripts/build_s2_site.py --check` | 16 generated annex files current. |
| `python3 -m unittest discover -s tests -p 'test_*.py' -v` | 21 tests passed, including tests that the unverified tracking ID remains unapplied, the new browse-path count is used, and CTAs keep disclosures beside sponsored links. |
| `node --check assets/app.js`; `node --check assets/analytics.js` | Both passed. |
| `git diff --check` | Passed after the rebase and regenerated-tree checks. |

### Source and rendered-output audit

- The product register contains **77** specification rows: 75 with values and 2 blank rows retained for uncertainty. Every asserted value references an existing source ID (75/75); all 43 registered source URLs are HTTPS.
- The two blank rows are the Chefman 6 Qt preset count and Chefman 8 Qt Hi-Fry/450 °F mode. `verify.py` reports them as blank+flagged; the caution-status Basket divider note is separate and is not a build error.
- A canonical-output scan found the exact Associate disclosure before `<main>` and again in the footer on **56/56** pages.
- A canonical-output scan found **351/351** real Amazon product destinations carrying `rel="sponsored"`; the non-product `ZZZ9ZZZZZ` negative-control URL is excluded as designed.
- A wider scan of all repository HTML found 676 real Amazon product destinations: 378 qualified and 298 unqualified. All 298 unqualified destinations are outside canonical root output. This is an inherited parallel/archive exposure, not a failure of the canonical-root result; do not generalize the root result to every older published copy.

## Canonical buyer-facing and owner pages read live

Public reads against the latest main deployment covered the [home page](https://kanlerxz87-cyber.github.io/Zone1/), [This week's picks](https://kanlerxz87-cyber.github.io/Zone1/picks.html), [comparison](https://kanlerxz87-cyber.github.io/Zone1/compare.html), [kitchen-appliances category](https://kanlerxz87-cyber.github.io/Zone1/categories/kitchen-appliances.html), [article index](https://kanlerxz87-cyber.github.io/Zone1/articles/index.html), [product-intent register](https://kanlerxz87-cyber.github.io/Zone1/product-intent.html) (both chunks), [Requirements](https://kanlerxz87-cyber.github.io/Zone1/requirements.html), [Flagged for review](https://kanlerxz87-cyber.github.io/Zone1/flagged.html), [Questions](https://kanlerxz87-cyber.github.io/Zone1/questions.html), [Measurement](https://kanlerxz87-cyber.github.io/Zone1/measurement.html), [Topics](https://kanlerxz87-cyber.github.io/Zone1/topics.html), [Design prompt](https://kanlerxz87-cyber.github.io/Zone1/design-prompt.html), [parallel decision gate](https://kanlerxz87-cyber.github.io/Zone1/decision-gate.html), [Suggestions](https://kanlerxz87-cyber.github.io/Zone1/suggestions.html), and all four chunks of the [live executive summary](https://kanlerxz87-cyber.github.io/Zone1/executive-summary.html).

Current buyer-facing position:

- The home page now opens with a reader-first buying-guide question and three documented air-fryer candidates. It shows manufacturer list prices separately from Amazon prices; the page states Amazon price is not displayed. CTAs say “See it on Amazon” and place the sponsored-link disclosure beside the link.
- `picks.html` presents three formats without an overall winner. `compare.html` compares the same three candidate ASINs, each still labelled unconfirmed; neither makes a thermometer a current product card.
- The category page now says **three of the five submitted links** were observed on air-fryer listings and that the other two land under a different Amazon browse path. It excludes the thermometer paths from this air-fryer category. The category label remains provisional because observed destinations do not prove owner intent.
- The 24-piece article index says no product was hands-on tested. No Amazon selling price, star rating or review count is used as a buyer-facing fact; manufacturer list prices are identified as such.
- Pass 14's reader-first layout, CTA wording, adjacent disclosure, corrected price-policy citation, corrected “0 of five” category count, flag-anchor guard and Suggestions decision desk are live. The new count is driven by recorded `observed_browse_path`, not fuzzy product-title text.

## Five submitted links: observations are not owner intent

Pass 14 re-read all five short-link redirects on 2026-11-19 and reported unchanged destination/title observations. The `observed_asin`/title fields in `data/product-intent.json` retain their earlier 2026-11-17 record date; the new browse-path fields are dated 2026-11-19. The browse-path observation is evidence of where the redirect landed, not owner intent and not a commission category.

| Row | Supplied short code | Observed destination | Observed title/category | Browse path read 2026-11-19 | Intended product confirmed? | Associates click test |
|---|---|---|---|---|---|---|
| PI-01 | `B04G1MEwY` | `B0CDY277D3` | Chefman 6 Qt dual-basket air fryer | Air Fryers (node 17659096011) | No; intended ASIN and confirmation fields are null | Not passed; no report evidence |
| PI-02 | `B02NbDxp3` | `B09B7SB46R` | Emeril 26 Qt French-door air-fryer oven | Air Fryers | No; intended ASIN and confirmation fields are null | Not passed; no report evidence |
| PI-03 | `B00hJ57DV` | `B08DKYBTPH` | Chefman 8 Qt air fryer | Air Fryers | No; intended ASIN and confirmation fields are null | Not passed; no report evidence |
| PI-04 | `B0c8moW59` | `B0DHZTCNR5` | ThermoMaven meat thermometer | Thermometers & Timers → Meat (node 289810) | No; intended ASIN and confirmation fields are null | Not passed; no report evidence |
| PI-05 | `B0f3GKalj` | `B0DZFD6R9Z` | CHEF iQ Sense meat thermometer | Thermometers & Timers → Meat | No; intended ASIN and confirmation fields are null | Not passed; no report evidence |

The redirect/title observations do not show what the owner intended, which product should be promoted, whether an account owns the tracking ID, whether a Special Link is valid, or whether Amazon attributed a click or order.

## Tracking ID: material published contradiction remains

Current local state:

- `data/config.json` records `selected_tracking_id: shopnow047c-20`, provenance as user-provided, `selected_tracking_id_associates_central_confirmed: false`, and an empty `associate_tag`.
- `data/product-intent.json` says `tracking_id_applied_to_links: false`; all five rows have `associates_link_test_passed: false` and no test dates/sources. It says the selected ID is not validated in Associates Central.
- Build-contract tests passed, including `test_current_unverified_id_is_recorded_but_not_applied` and `test_rejects_tag_before_account_confirmation_and_per_product_tests`.

Published contradiction:

- Q-04 and Q-28 say the tag is not applied/`associate_tag` is blank, and require account/report evidence.
- Q-37 claims the ID is attached to every `/dp/` link and that the build rejects untagged links. Its answer is null and the account test is still unknowable. `measurement.html` repeats that the tracking ID is already applied.
- Q-37 asks for a tag parameter visible in the URL. Amazon's [tracking-ID help](https://affiliate-program.amazon.com/help/node/topic/GF4RJEQNXSMR7SP3) says a tracking ID need not remain visible in the click-through URL for a sale to be attributed. Amazon's [tracking-ID reporting guidance](https://affiliate-program.amazon.com/help/node/topic/GJDYPQZK6E37RLPU) points to the Tracking ID Summary Report. Neither public help page validates this account or any specific submitted link.

**Finding:** the current claim that the ID is applied is contradicted by the current source data and passing build-contract tests. Do not report that tagging or attribution works. The owner must confirm the ID and intended products and read the relevant account report.

## Measurement: design present, collection absent

The local config has `analytics.enabled: false` and an empty endpoint. `data/measurement.json` describes the client as shipped but the endpoint not deployed. The campaign ledger has no rows, and requires an authorized first-party source for any future row. The live Measurement page says no endpoint is deployed, the counter is off and no count is observed; however, its prerequisite table repeats the incorrect assertion that the tracking ID is already applied. The five event definitions are a future/reference design, not active collection. No Associates report, traffic count, order count, conversion rate or revenue result has been verified. Search Console status and any query/impression/click metrics are also unverified.

## Topic/article count reconciliation

The normalized local comparison remains:

- `data/topics.json`: 26 rows — 21 `published`, 5 `proposed`.
- `data/articles.json`, generated article pages, live article index and feed: 24 published articles/items.
- Three article slugs have no corresponding published topic row: `chefman-8qt-two-models`, `energy-cost-of-an-air-fryer`, and `who-actually-pays-for-air-fryer-reviews`.
- No published topic row points to a slug absent from the article register.

The topic page's 21-published count and the article index's 24 count each match their own register. The unresolved issue is their coverage relationship, not a proven missing article page. Pass 14 did not alter either register.

## Stale guidance and executive-summary comparison

- `design-prompt.html` still says there are three tracked air fryers/supplied links. `decision-gate.html` and SG-02 still frame the attribution question as three supplied links. Main Q-01 and the product-intent register contain five links; the new Suggestions decision brief also identifies two thermometer links separately. Reconcile these versions without treating any of the five destinations as owner-confirmed products.
- The live `measurement.html` statement that the tracking ID is already on every outbound product link conflicts with config/product-intent state and Q-04/Q-28. The endpoint itself is correctly disabled; the tracking sentence is not.
- The live `executive-summary.html` still foregrounds Pass 9/10, includes a former 43-specification-row snapshot and three-candidate framing, and does not incorporate the five-link status. It is not a November 19 roll-up.
- Root [`EXECUTIVE-SUMMARY.md`](../EXECUTIVE-SUMMARY.md) now includes a Pass 14 addendum, but its opening still calls the briefing historical/superseded and its older body retains three-link/old-count material. The generated public executive-summary page does not show the Pass 14 update. This dated report and [`executive-summary-2026-11-19.md`](executive-summary-2026-11-19.md) are the current X-e3ac0e8d deliverables; the generated page was not edited.
- The older Search Console basics URL `https://developers.google.com/search/docs/fundamentals/search-console-basics` returned 404. Google's current [Search Console getting-started guide](https://developers.google.com/search/docs/monitor-debug/search-console-start) is the replacement reference. No property verification or metrics were checked.

## Repairs already published and verified

1. **Amazon product-link qualification — PR #152**, merged as `c758b8b` on 2026-11-19. The current canonical output audit found all 351 product destinations marked `rel="sponsored"`; the generator/build gate prevents regression. This is a qualification marker, not proof of attribution. [PR #152](https://github.com/kanlerxz87-cyber/Zone1/pull/152).
2. **Requirements local-file targets — PR #154**, merged as `2e3134c` on 2026-11-19. The live G-01 target is `platform/README.md`; G-04 points to `platform/tests/test_platform.py`. The build-path guard and regression tests passed. See [`verification-2026-11-19-62a6f797.md`](verification-2026-11-19-62a6f797.md) and [PR #154](https://github.com/kanlerxz87-cyber/Zone1/pull/154).
3. **Reader-first publishing and pass-14 corrections — PR #157**, merged as `0a860d9` on 2026-11-19. The front page now leads with three documented machines, provides CTA disclosure beside the sponsored link, fixes the price-policy citation, replaces the false “0 of five” category count with the 3-of-5 browse-path count, repairs two flag anchors and guards against regression. [PR #157](https://github.com/kanlerxz87-cyber/Zone1/pull/157).
4. **Pass-14 publication record — PR #158**, merged as `cb33d97`. The current Pages, CI and annex workflows succeeded for this snapshot; [PR #158](https://github.com/kanlerxz87-cyber/Zone1/pull/158).

These repairs are included in the reviewed live `main`. The open tracking, topic-register and summary-copy issues above are separate and were not changed by them.

## Repair requests recorded; no overlapping files edited

1. Reconcile Q-37 and the Measurement page with the actual unapplied/unverified tracking state. Correct the URL-visible-tag criterion using Amazon's help guidance; leave `associate_tag` blank until owner evidence satisfies the build contract.
2. Reconcile the 24 article records against the 21 published topic rows and document or fix the three unmapped slugs.
3. Update or explicitly retire the three-link wording in the design prompt, decision gate and SG-02, while preserving the distinction between observed destination and owner-confirmed product intent.
4. Refresh the generated executive-summary source/page so the public roll-up matches the current 77-spec/5-link/disabled-measurement state, and keep historical pass notes visibly dated.
5. Replace the 404 Search Console citation in the relevant registers.
6. Treat the 298 unqualified destinations in older parallel/archive output as separate owner/session scope; the canonical-root pass does not establish those copies as compliant.

## Reproduction commands

```sh
python3 build.py
python3 verify.py
bash scripts/ci-check.sh
python3 research/build_research.py
python3 research/check_research.py
python3 scripts/build_site.py
python3 scripts/verify_site.py
python3 platform/audit/report.py
python3 scripts/build_s2_site.py --check
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --check assets/app.js
node --check assets/analytics.js
git diff --check
```

No product, affiliate destination, account, tracking, analytics, traffic, click, order, conversion, price or review value was changed or asserted by this acceptance review.