# Acceptance review verification — X-e3ac0e8d

**Date:** 2026-11-19 UTC
**Branch:** `arena/e3ac0e8d-zone1`
**Reviewed local base:** `f0226ef289bfba6304481a081a89c29868409a72`, rebased onto `origin/main` `bc5f0b103143ef626cf3d5d060031808d03c3a5c`
**Live Pages snapshot:** `main` at `bc5f0b1`
**Scope:** acceptance review of the canonical root site, five supplied-link records, source/data contracts, build gates, buyer-facing pages, disclosure and link qualification, measurement status, and repairs already published on `main`.

## Verdict

**Build/source and canonical publishing gates pass. Overall acceptance is conditional.** The review does not validate intended product identity, Associates Central account state, tracking attribution, Search Console data, analytics collection, clicks, orders or conversions. Several published passages contradict the current records, so the project is not approved to make unqualified attribution or measurement claims. Those copy/register repairs were documented here rather than implemented: `COORDINATION.md` assigned this review read-only scope on shared build/data/generated files.

## Review boundary and evidence limits

- Local evidence was gathered from the rebased repository. The regenerated root site is deterministic and no generated files changed in the verification run.
- Public Pages reads were made against the deployed site. The most recent recorded main deployment was for `bc5f0b1`; successful workflow runs are [44467120332](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44467120332) and [44467119638](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44467119638). This task branch's new reports are not public until the branch is merged; GitHub Pages serves `main`.
- Amazon page reads are destination/title observations only. No Associates Central login, account page, Tracking ID Summary Report or Earnings report was available. No Search Console property was accessed. No private or server-side analytics data was available.
- This review did not edit `build.py`, `data/*.json`, canonical generated HTML, or parallel build output. The only files intended to change for this task are these reports and the X-e3ac0e8d entry in `COORDINATION.md`.

## Local build and verification gates

Commands were run after the rebase and before report creation. All exited successfully.

| Command | Result |
|---|---|
| `python3 build.py` | Built 56 canonical HTML pages (2,798 KB); generated `sitemap.xml` with 35 URLs and `feed.xml` with 24 items. |
| `python3 verify.py` | 134 pages checked; 77 spec rows (75 asserted, 2 blank+flagged); 43 sources; 0 errors; 0 external warnings. One informational caution-status note remains for `chefman-8qt-turbofry` / Basket divider. |
| `bash scripts/ci-check.sh` | 33 tests passed; data audit clean; 16-file annex current; link check passed 10,688 links (13 owned by this session, plus 121 inherited/advisory). |
| `python3 research/build_research.py` + `python3 research/check_research.py` | Research output rebuilt (12 pages); 834 checks passed; no broken links, unsourced rows or missing disclosures. |
| `python3 scripts/build_site.py` + `python3 scripts/verify_site.py` | Separate legacy `site/` build checked; 393 assertions passed. This is not the canonical root build. |
| `python3 platform/audit/report.py` | 0 errors, 0 warnings, 0 findings. |
| `python3 scripts/build_s2_site.py --check` | 16 generated annex files current. |
| `python3 -m unittest discover -s tests -p 'test_*.py' -v` | 18 tests passed, including tests proving the unconfirmed tracking ID remains unapplied and cannot be enabled before account/product tests. |
| `node --check assets/app.js`; `node --check assets/analytics.js` | Both passed. |
| `git diff --check` | Passed on the regenerated tree. |

### Source and rendered-output audit

- The product register contains **77** specification rows: 75 with values and 2 blank rows retained for uncertainty. Every asserted value references an existing source ID (75/75); all 43 registered source URLs are HTTPS.
- The two blank rows are the Chefman 6 Qt preset count and Chefman 8 Qt Hi-Fry/450 °F mode. `verify.py` reports them as blank+flagged; the caution-status Basket divider note is separate and is not a build error.
- A canonical-output scan found the exact Associate disclosure before `<main>` and again in the footer on **56/56** pages.
- A canonical-output scan found **346/346** real Amazon product destinations carrying `rel="sponsored"`; the non-product `ZZZ9ZZZZZ` negative-control URL is excluded as designed.
- A wider scan of canonical plus archive/parallel HTML found 678 real product destinations: 373 qualified and 305 unqualified. All 305 unqualified destinations are outside canonical root output. This is an inherited parallel/archive exposure, not a failure of the 346-link canonical-root result; do not generalize the root result to every old published copy.

## Canonical buyer-facing and owner pages read live

The public reads covered the [home page](https://kanlerxz87-cyber.github.io/Zone1/), [This week's picks](https://kanlerxz87-cyber.github.io/Zone1/picks.html), [comparison](https://kanlerxz87-cyber.github.io/Zone1/compare.html), [kitchen-appliances category](https://kanlerxz87-cyber.github.io/Zone1/categories/kitchen-appliances.html), [article index](https://kanlerxz87-cyber.github.io/Zone1/articles/index.html), [product-intent register](https://kanlerxz87-cyber.github.io/Zone1/product-intent.html), [Requirements](https://kanlerxz87-cyber.github.io/Zone1/requirements.html) (including lower-page G-01/G-04 entries), [Flagged for review](https://kanlerxz87-cyber.github.io/Zone1/flagged.html), [Questions](https://kanlerxz87-cyber.github.io/Zone1/questions.html), [Measurement](https://kanlerxz87-cyber.github.io/Zone1/measurement.html), [Topics](https://kanlerxz87-cyber.github.io/Zone1/topics.html), [Design prompt](https://kanlerxz87-cyber.github.io/Zone1/design-prompt.html), [parallel decision gate](https://kanlerxz87-cyber.github.io/Zone1/decision-gate.html), [Suggestions](https://kanlerxz87-cyber.github.io/Zone1/suggestions.html), and all four chunks of the [live executive summary](https://kanlerxz87-cyber.github.io/Zone1/executive-summary.html).

Observed buyer-facing position: the home/picks/comparison set presents three unconfirmed air-fryer candidates. The category page distinguishes three air-fryer observations from two meat-thermometer observations across the five supplied links; it does not treat those five redirect destinations as five owner-confirmed products. Product price, ratings, review counts and hands-on performance are not established by this review. The disclosure and `rel="sponsored"` checks above establish placement/qualification, not Associates acceptance or commission.

## Five submitted links: observations are not owner intent

The five current Amazon destination reads again produced the following landing observations on 2026-11-19. The source register's `observed_on` fields still show its previous recorded date (2026-11-17); this review did not edit the register.

| Register row | Supplied short code | Observed destination | Observed title/category | Intended product confirmed? | Associates click test |
|---|---|---|---|---|---|
| PI-01 | `B04G1MEwY` | `B0CDY277D3` | Chefman 6 Qt dual-basket air fryer | No; `intended_asin` and confirmation fields are null | Not passed; no report evidence |
| PI-02 | `B02NbDxp3` | `B09B7SB46R` | Emeril 26 Qt French-door air-fryer oven | No; `intended_asin` and confirmation fields are null | Not passed; no report evidence |
| PI-03 | `B00hJ57DV` | `B08DKYBTPH` | Chefman 8 Qt air fryer | No; `intended_asin` and confirmation fields are null | Not passed; no report evidence |
| PI-04 | `B0c8moW59` | `B0DHZTCNR5` | ThermoMaven meat thermometer | No; `intended_asin` and confirmation fields are null | Not passed; no report evidence |
| PI-05 | `B0f3GKalj` | `B0DZFD6R9Z` | CHEF iQ Sense meat thermometer | No; `intended_asin` and confirmation fields are null | Not passed; no report evidence |

These readings show what a public redirect returned on the day read. They do not show what the owner intended, which listing should be promoted, whether the account owns the tracking ID, whether a Special Link is valid, or whether Amazon attributed a click or order.

## Tracking ID: material published contradiction

Current local state:

- `data/config.json` records `selected_tracking_id: shopnow047c-20`, provenance as user-provided, `selected_tracking_id_associates_central_confirmed: false`, and an empty `associate_tag`.
- `data/product-intent.json` says `tracking_id_applied_to_links: false`; all five rows have `associates_link_test_passed: false` and no test dates/sources. It also says the selected ID is not validated in Associates Central.
- Build-contract tests passed, including `test_current_unverified_id_is_recorded_but_not_applied` and `test_rejects_tag_before_account_confirmation_and_per_product_tests`.

Published contradiction:

- Q-04 and Q-28 say the tag is not applied/`associate_tag` is blank, and require account/report evidence.
- Q-37 claims the ID is already attached to every `/dp/` link and that the build rejects untagged links. Its answer is null and the account test is still unknowable. `measurement.html` repeats that the tracking ID is already applied.
- Q-37's test asks for a tag parameter visible in the URL. Amazon's [tracking-ID help](https://affiliate-program.amazon.com/help/node/topic/GF4RJEQNXSMR7SP3) says that a tracking ID need not remain visible in the click-through URL for a sale to be attributed. Amazon's [tracking-ID reporting guidance](https://affiliate-program.amazon.com/help/node/topic/GJDYPQZK6E37RLPU) points to the Tracking ID Summary Report. Neither public help page validates this account or any specific submitted link.

**Finding:** the current published claim that the ID is applied is contradicted by the current source data and passing build-contract tests. Do not report that tagging or attribution works. The review cannot resolve account-only questions; the owner must confirm the ID and intended products and read the relevant account report.

## Measurement: design present, collection absent

The local config has `analytics.enabled: false` and an empty endpoint. `data/measurement.json` describes the client as shipped but the endpoint not deployed. The campaign ledger has no rows, and explicitly requires an authorized first-party source for any future row. The Measurement page distinguishes browser click interest from Amazon-reported orders; no counter, endpoint or live event was observed. No Associates report, traffic count, order count, conversion rate or revenue result has been verified.

The page defines four browser event types and one manually reported-order event as a future plan. That design must not be described as active collection. Search Console status and any query/impression/click data are likewise unverified.

## Topic/article count reconciliation

The normalized local comparison is exact:

- `data/topics.json`: 26 rows — 21 `published`, 5 `proposed`.
- `data/articles.json`, generated article pages, live article index and feed: 24 published articles/items.
- Three article slugs have no corresponding published topic row: `chefman-8qt-two-models`, `energy-cost-of-an-air-fryer`, `who-actually-pays-for-air-fryer-reviews`.
- No published topic row points to a slug absent from the article register.

The topic page's computed 21-published count and the article index's 24 count each match their own register. The unresolved issue is their coverage relationship, not a proven missing article page. This review did not add topic rows or reclassify articles.

## Stale guidance and executive-summary comparison

- `design-prompt.html` still says there are three tracked air fryers/supplied links. `decision-gate.html` and SG-02 also describe a three-link set, while the current product-intent register and Q-01 cover five supplied links. The three-versus-two category split on the live category page is appropriately qualified; the stale copies need reconciliation.
- `measurement.html`'s statement that the tracking ID is already on every outbound product link conflicts with config/product-intent state and Q-04/Q-28. This is a published copy defect even though the endpoint itself is correctly disabled.
- The live `executive-summary.html` foregrounds older Pass 9/10 material, includes a former 43-specification-row snapshot and three-candidate framing, and recommends attribution actions without incorporating the current five-link status. It is not a November 19 roll-up.
- The root [`EXECUTIVE-SUMMARY.md`](../EXECUTIVE-SUMMARY.md) opens by marking itself historical and superseded for post-2026-11-17 link-intent/measurement status. `reports/brief-reconciliation-2026-11-17.md` is the earlier reconciliation, not this review's current summary. This report and [`executive-summary-2026-11-19.md`](executive-summary-2026-11-19.md) are the dated X-e3ac0e8d deliverables; the generated public page was not edited.
- The older Search Console basics URL `https://developers.google.com/search/docs/fundamentals/search-console-basics` returned 404. Google's current [Search Console getting-started guide](https://developers.google.com/search/docs/monitor-debug/search-console-start) is the replacement reference. No property verification or metrics were checked.

## Repairs already published and verified

1. **Amazon product-link qualification — PR #152**, merged as `c758b8b` on 2026-11-19. The canonical output audit found all 346 current product destinations marked `rel="sponsored"`; the generator/build gate prevents regression. This is a qualification marker, not proof of attribution. See [PR #152](https://github.com/kanlerxz87-cyber/Zone1/pull/152).
2. **Requirements local-file targets — PR #154**, merged as `2e3134c` on 2026-11-19. The live G-01 target is `platform/README.md`; G-04 points to `platform/tests/test_platform.py`. The build-path guard and regression tests passed. The repair record is [`verification-2026-11-19-62a6f797.md`](verification-2026-11-19-62a6f797.md), and the PR is [#154](https://github.com/kanlerxz87-cyber/Zone1/pull/154).

Both merged changes are included in the reviewed `main` snapshot. The open copy/register discrepancies above are separate and were not changed by those repairs.

## Repair requests recorded; no overlapping files edited

1. Reconcile Q-37 and the Measurement page with the actual unapplied/unverified tracking state. Correct the URL-visible-tag criterion using Amazon's help guidance; leave `associate_tag` blank until owner evidence satisfies the build contract.
2. Reconcile the 24 article records against the 21 published topic rows and document or fix the three unmapped slugs.
3. Update or explicitly retire the three-link wording in the design prompt, decision gate and SG-02 while preserving the difference between observed destination and owner-confirmed product intent.
4. Refresh the generated executive-summary source/page so its current summary matches the 77-spec/5-link/disabled-measurement state, and keep historical pass notes visibly dated.
5. Replace the 404 Search Console citation in the relevant registers.
6. Treat the 305 unqualified destinations in older parallel/archive output as separate owner/session scope; the canonical-root pass does not establish that those copies are compliant.

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
