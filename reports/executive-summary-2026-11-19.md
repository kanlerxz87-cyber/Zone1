# Executive summary — acceptance review X-e3ac0e8d

**Prepared:** 2026-11-19 UTC
**Branch:** `arena/e3ac0e8d-zone1`
**Reviewed snapshot:** rebased on `origin/main` at `bc5f0b103143ef626cf3d5d060031808d03c3a5c`
**Live Pages snapshot reviewed:** `main` at `bc5f0b1`
**Full evidence and commands:** [`verification-2026-11-19-e3ac0e8d.md`](verification-2026-11-19-e3ac0e8d.md)

## Decision

**The reproducible build, source-data checks, disclosure placement and sponsored-link qualification pass. Overall acceptance is conditional, not a clean commercial/measurement sign-off.** There is no evidence here that the five supplied links match the owner's intent, that `shopnow047c-20` is active in Associates Central or is applied to the links, that any click was attributed, or that analytics or conversions have been collected. Those remain unverified/account-only facts.

A published contradiction says the tracking ID is already on every product link, while the current config and product-intent register explicitly say it is not applied. The live executive-summary, measurement and older parallel guidance also retain stale three-link or 43-specification-row statements. These copy/register issues were recorded as repair requests rather than edited: this acceptance review was scoped read-only on shared build, data and generated-page files.

## What passed

- `python3 build.py` regenerated **56 canonical HTML pages**, a **35-URL sitemap** and a **24-item feed**.
- `python3 verify.py` checked 134 repository HTML pages and 77 specification rows (**75 sourced values; 2 blank and flagged**), with 43 registered HTTPS sources, **0 errors and 0 external warnings**. One caution-status note remains on the Chefman 8 Qt basket-divider row.
- The 75 asserted product-spec values all point to existing source IDs; all 43 registered source URLs use HTTPS.
- All **56/56** canonical pages put the Amazon Associate disclosure before `<main>` and repeat it in the footer. All **346/346** canonical Amazon product destinations carry `rel="sponsored"`.
- The integration, research, site, platform, annex and JavaScript checks passed. The detailed command/result table is in the verification report.
- The merged repairs are present on the reviewed live `main`: PR [#152](https://github.com/kanlerxz87-cyber/Zone1/pull/152) qualifies Amazon product destinations; PR [#154](https://github.com/kanlerxz87-cyber/Zone1/pull/154) replaces the dead Requirements directory targets with files and adds a regression guard. The live Requirements page reflects the repaired G-01/G-04 targets.

## Product intent and tracking: not confirmed

The five short-link reads are **redirect/title observations only**, not proof of intended product identity or Associates attribution:

| Supplied short code | Destination observed on 2026-11-19 | Listing observed |
|---|---|---|
| `B04G1MEwY` | `B0CDY277D3` | Chefman 6 Qt dual-basket air fryer |
| `B02NbDxp3` | `B09B7SB46R` | Emeril French-door air-fryer oven |
| `B00hJ57DV` | `B08DKYBTPH` | Chefman 8 Qt air fryer |
| `B0c8moW59` | `B0DHZTCNR5` | ThermoMaven meat thermometer |
| `B0f3GKalj` | `B0DZFD6R9Z` | CHEF iQ Sense meat thermometer |

All five rows in `data/product-intent.json` still have `intended_asin`, official listing URL and owner-confirmation fields unset; none has a passed Associates link test. The repository records `shopnow047c-20` as user-provided, but `data/config.json` has an empty `associate_tag`, the selected ID is not confirmed in Associates Central, and `tracking_id_applied_to_links` is false. `rel="sponsored"` is a link qualification marker; it is not an Associates tracking tag.

The published guidance conflicts: Q-04/Q-28 describe the tag as unapplied/blank, while Q-37 and a sentence on `measurement.html` claim it is already applied to every `/dp/` link. Q-37 also asks for the tag to be visible in the click-through URL. Amazon's tracking-ID help says that the tag need not remain visible in that URL for attribution; the relevant proof is the account's Tracking ID Summary Report. No account screen or report was available or verified in this review.

## Measurement: no collection or results verified

`analytics.enabled` is false, the endpoint is empty/not deployed, and the campaign ledger has zero rows. The measurement plan defines five events, but describes a future/reference design; the shipped browser client is inert in the current configuration. No analytics events, Search Console metrics, Associates report, clicks, orders, conversion rate or revenue have been verified. The ledger correctly distinguishes authorized reported orders from browser click counts.

## Repairs required before an unqualified acceptance

1. **Correct the tracking claim consistently.** Reconcile Q-37 and the live Measurement sentence with `data/config.json`, `data/product-intent.json`, Q-04 and Q-28. Replace the URL-visible-tag test with an account/report-based test; do not populate `associate_tag` until the owner has confirmed intended products and completed the required account tests.
2. **Resolve the article/topic register gap.** There are 26 topic rows (21 published, 5 proposed) but 24 registered/published articles. After normalizing `published_as` paths, three articles have no published topic row: `chefman-8qt-two-models`, `energy-cost-of-an-air-fryer`, and `who-actually-pays-for-air-fryer-reviews`. No topic row points to a missing article. Decide whether to add the three rows or explicitly document why those articles are outside the topic register.
3. **Refresh stale three-link copy.** `design-prompt.html`, `decision-gate.html`, and Suggestions SG-02 still frame the project as a three-link set. The current product-intent register and Q-01 contain five links. Retain the distinction between the three air-fryer candidates and two thermometer destinations; do not imply all five are intended products.
4. **Refresh the public executive summary.** The live `executive-summary.html` remains a chronological, older-pass briefing with a former three-product/43-specification-row snapshot and an attribution recommendation that is not aligned with the current link-intent record. `EXECUTIVE-SUMMARY.md` itself labels its contents historical and superseded for the 2026-11-17 link-intent/measurement status. This dated report is the current review summary; the generated page was outside this pass's edit scope.
5. **Repair the stale Search Console citation.** The older `developers.google.com/search/docs/fundamentals/search-console-basics` URL cited by the question/suggestion registers returned 404. The current guide is [`Search Console: getting started`](https://developers.google.com/search/docs/monitor-debug/search-console-start). No Search Console property or metrics were checked.

## Owner actions

Before any revenue or performance claim: confirm the intended listing for each supplied URL; confirm the selected tracking ID in Associates Central; use the account's prescribed test/report workflow and record results; and only then decide whether to enable or deploy measurement. Do not infer intent from redirects, attribution from URL appearance, or conversions from clicks.

The reports on this branch are not yet published by GitHub Pages. Pages serves `main`; these deliverables require the review branch to be merged before they become public.
