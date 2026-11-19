# Executive summary — acceptance review X-e3ac0e8d

**Prepared:** 2026-11-19 UTC
**Branch:** `arena/e3ac0e8d-zone1`
**Reviewed `main`:** `cb33d97e1fe7c17e1ab1d943af4349ace17a271e`
**Live Pages snapshot reviewed:** `main` at `cb33d97`
**Full evidence and commands:** [`verification-2026-11-19-e3ac0e8d.md`](verification-2026-11-19-e3ac0e8d.md)

## Decision

**The reproducible build, source-data checks, disclosure placement and canonical sponsored-link qualification pass. Overall acceptance is conditional, not a clean commercial/measurement sign-off.** There is no evidence that the five supplied links match the owner's intent, that `shopnow047c-20` is active in Associates Central or applied to links, that any click was attributed, or that analytics or conversions were collected. These remain unverified/account-only facts.

The live Measurement page and Q-37 still claim that the tracking ID is already applied to every product link, while the current config and product-intent register say it is not applied. Older guidance and the generated executive-summary also retain stale three-link or 43-specification-row statements. These copy/register issues are recorded as repair requests, not edited: this review is read-only on shared build, data and generated-page files.

## What passed

- `python3 build.py` regenerated **56 canonical HTML pages**, a **35-URL sitemap** and a **24-item feed**.
- `python3 verify.py` checked 134 repository HTML pages and 77 specification rows (**75 sourced values; 2 blank and flagged**), with 43 registered HTTPS sources, **0 errors and 0 external warnings**. One caution-status note remains on the Chefman 8 Qt basket-divider row.
- All 75 asserted product-spec values refer to existing source IDs; all 43 source URLs use HTTPS.
- All **56/56** canonical pages place the Amazon Associate disclosure before `<main>` and repeat it in the footer. All **351/351** canonical Amazon product destinations carry `rel="sponsored"`.
- `scripts/ci-check.sh` passed 33 tests and the 11,464-link check; research checks passed 834; site verification passed 393 assertions; platform audit had 0 errors/warnings; the 16-file S2 annex was current; 21 root unit tests passed; JavaScript syntax and whitespace checks passed.
- The live home page is now reader-first: three documented air-fryer options, separately labelled manufacturer list prices, no Amazon price/rating/review data, and sponsored CTAs with nearby commission disclosures. Pass 14 also fixed the category's false “0 of five” count and added a guard based on recorded browse paths.
- Published repairs are present on the reviewed `main`: PR [#152](https://github.com/kanlerxz87-cyber/Zone1/pull/152) qualifies Amazon product destinations; PR [#154](https://github.com/kanlerxz87-cyber/Zone1/pull/154) repairs Requirements directory links; PR [#157](https://github.com/kanlerxz87-cyber/Zone1/pull/157) delivers the reader-first pages and F90/F91/F92/F94 fixes. PR [#158](https://github.com/kanlerxz87-cyber/Zone1/pull/158) records the merge/deployment. The latest Pages and CI workflows for `cb33d97` succeeded.

## Product intent and tracking: not confirmed

The five short-link reads remain **redirect/title observations**, not proof of intended product identity or Associates attribution. Pass 14 re-read the links on 2026-11-19 and recorded the Amazon browse-path breadcrumb for each; observed targets were unchanged. The destination/title observations in the product-intent rows retain their original 2026-11-17 date.

| Supplied short code | Destination observed | Listing observed | Browse path read 2026-11-19 |
|---|---|---|---|
| `B04G1MEwY` | `B0CDY277D3` | Chefman 6 Qt dual-basket air fryer | Air Fryers |
| `B02NbDxp3` | `B09B7SB46R` | Emeril French-door air-fryer oven | Air Fryers |
| `B00hJ57DV` | `B08DKYBTPH` | Chefman 8 Qt air fryer | Air Fryers |
| `B0c8moW59` | `B0DHZTCNR5` | ThermoMaven meat thermometer | Thermometers & Timers → Meat |
| `B0f3GKalj` | `B0DZFD6R9Z` | CHEF iQ Sense meat thermometer | Thermometers & Timers → Meat |

All five rows still have `intended_asin`, official listing URL and owner-confirmation fields unset; none has a passed Associates click test. The repository records `shopnow047c-20` as user-provided, but `data/config.json` has an empty `associate_tag`, account confirmation is false, and `tracking_id_applied_to_links` is false. `rel="sponsored"` is a link qualification marker, not an Associates tracking tag.

Q-04/Q-28 say the tag is unapplied/blank; Q-37 and `measurement.html` say it is already on every `/dp/` link. Q-37 also asks for the tag to be visible in the click-through URL. Amazon's [tracking-ID help](https://affiliate-program.amazon.com/help/node/topic/GF4RJEQNXSMR7SP3) says the ID need not remain visible in that URL for attribution; evidence of account setup and a click belongs in Associates Central's Tracking ID Summary Report. No account screen or report was verified here.

## Measurement: no collection or results verified

`analytics.enabled` is false, the endpoint is empty/not deployed, and the campaign ledger has zero rows. The measurement plan defines five future/reference events; the shipped browser client is inert in the current configuration. No analytics events, Search Console metrics, Associates report, clicks, orders, conversion rate or revenue have been verified. The ledger correctly distinguishes authorized reported orders from browser click counts.

## Remaining repair requests

1. **Correct the tracking claim consistently.** Reconcile Q-37 and the live Measurement sentence with `data/config.json`, `data/product-intent.json`, Q-04 and Q-28. Replace the URL-visible-tag test with an account/report-based test; leave `associate_tag` blank until the owner confirms intended products and completes the required account tests.
2. **Resolve the article/topic register gap.** There are 26 topic rows (21 published, 5 proposed) but 24 registered/published articles. After normalizing `published_as` paths, three articles have no published topic row: `chefman-8qt-two-models`, `energy-cost-of-an-air-fryer`, and `who-actually-pays-for-air-fryer-reviews`. No topic row points to a missing article. Add the rows or document why these articles are outside the topic register.
3. **Refresh older three-link copy.** `design-prompt.html`, `decision-gate.html` and Suggestions SG-02 still describe a three-link set. The current product-intent register and main Q-01 cover five supplied URLs; the current category page correctly records three air-fryer browse paths and two thermometer browse paths. Do not imply all five are owner-confirmed products.
4. **Refresh the generated executive summary.** The live `executive-summary.html` still foregrounds Pass 9/10, a former 43-specification-row snapshot and a three-candidate framing; it is not a November 19 roll-up. The root `EXECUTIVE-SUMMARY.md` has a new Pass 14 addendum but still opens with a historical/superseded banner and older three-link content. This dated review report is the current X-e3ac0e8d summary; the generated page was outside scope.
5. **Repair the stale Search Console citation.** The older `developers.google.com/search/docs/fundamentals/search-console-basics` URL in the question/suggestion registers returned 404. Google's current guide is [`Search Console: getting started`](https://developers.google.com/search/docs/monitor-debug/search-console-start). No Search Console property or metrics were checked.

## Owner actions

Before making any revenue or performance claim: confirm the intended listing for each supplied URL; confirm the selected tracking ID in Associates Central; use the account's prescribed test/report workflow and record results; then decide whether to enable or deploy measurement. Do not infer intent from redirects, attribution from URL appearance, or conversions from clicks.

These reports are on the review branch, not yet public. GitHub Pages serves `main`; the deliverables require the review branch to be merged before publication.