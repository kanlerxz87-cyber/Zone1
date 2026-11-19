# PUB-1 — scoped source review and publication integration

**Date:** 2026-11-19 UTC  
**Session branch:** `arena/1f9e7d52-zone1`  
**Status:** complete — PR #162 merged, all combined local/PR/main gates passed, Pages built the exact merge and actual public content was read back. The earlier checkpoints below retain their original timing/limits.

## Executive finding

The repository contained substantial sourced research, but the canonical reader
experience repeated its audit machinery and its isolated measurement tests missed
a real interoperability defect. The old browser emitted EV-number events with
fields the Python collector did not accept, and its `/dp/` matching missed actual
supplied short links. The replacement client and collector now share one contract,
with the actual client payloads exercised through the real HTTP handler into an
isolated aggregate database. **Production analytics remains disabled.**

The reader redesign leads with buying decisions and concise product cards. Source
registers, decisions, requirements and the full audit remain public under one
Workspace navigation group and the footer, rather than a permanent sidebar.

## Scope and honesty limits

This is a **scoped** primary-source re-read, not a claim that every line of all 45
registered sources or every page of each manual was read again. Historical broad
`accessed`/`reverified` stamps are retained. Specific reviewed sections are appended
to `data/sources.json`; all 24 revised articles have their own source
read and modification dates. Other guides retain their previous source dates.

No account credentials, authorised Associates report, Search Console ownership,
production runtime or test appliance was available. No conversion, revenue,
traffic, ranking improvement, product ownership or named human editor is invented.

## Official primary evidence read this session

| Evidence | Sections read / observation | Consequence |
|---|---|---|
| [Amazon Operating Agreement, S1](https://affiliate-program.amazon.com/help/operating/agreement) | Version October 15, 2025; identification/disclosure and no earnings warranty sections. | Exact Associate sentence in every below-masthead strip and footer; no earnings promise. |
| [Amazon Program Policies, S2](https://affiliate-program.amazon.com/help/operating/policies) | Version April 14, 2026; Special Link accuracy/tag rules, permitted price-display routes and technology disclosure. This was not a complete re-read of every clause. | No tag application without validation; no price integration invented; correct the false blanket claim that all Associates price display is prohibited. |
| [Amazon disclosure help, S5](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) | Exact Associate sentence, conspicuous disclosure near links. | Visible strip under masthead and repeated footer. |
| [FTC disclosure guidance, S8](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | Clear disclosures and no claims of experience with an untried product. | Honest publication byline, no hands-on or imaginary expert claim. |
| [Chefman dual-window brand page, S10](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | Model RJ38-SQPF-3TDB-2W; 6 Qt/5.67 L; 200–450 °F; 13.38×11.81×10.63 in; 1700W/120V. Brand widget observed at 4.6 with 1,312 reviews. | Key format/specification evidence retained. Refresh dated brand-widget snapshot only; no Amazon review data. |
| [Chefman 8 Qt brand page, S12](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) | RJ38-SQSS-8T; 8 Qt option; 200–400 °F; 15.4×12.6×13.5 in; 12.8 lb; 1700W/120V; four presets. Widget observed at 4.6 with 719 reviews. | Keep 450 °F listing-title conflict visible; restore known dimensions to buyer guidance; date widget snapshot. |
| [Emeril brand page, S14](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | 26 qt/24.6 L; 16.9D×15.8W×14.8H in; 120V; 25-preset icon vs 24-preset description and 10-in-1 heading. | No invented reconciliation of counts or SKU strings. |
| [Chefman dual-window manual, S18](https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQPF-3TDB-2W-UG-US.pdf) | Model/safety, two 3-qt baskets, Sync Finish/Sync Baskets, two-minute Hi-Fry and cleaning sections. | Split capacity and finish-mode limits explained. Removable baskets/racks may go on dishwasher top rack; main unit may not. |
| [Chefman single-basket manual, S13](https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQSS-8T-UG-US.pdf) | Model/safety, setup and care sections. Setup calls for 6 inches on top and back; basket/rack top-rack dishwasher safe; main unit not immersed/dishwashed. | Model-specific clearance and care, not a general rule for every air fryer. |
| [Emeril FAFO-001 manual, S15](https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf) | Electrical/capacity table, English safeguards and power-cord section, parts, cleaning/storage and FAQ. Safeguard 9 prohibits extension cords; the later cord section conditionally permits them. | **Open F96:** seek manufacturer clarification, do not select the convenient instruction. Correct the old guide that quoted only one section. Accessories are recommended hand-wash; main appliance never soaked/dishwashed. |
| [CHEF iQ catalogue, S39](https://chefiq.com/products/iq-sense) | Current default CQ60-1C-Z1-E, selectable 1/2/3/4 probe configurations; both page chunks read. | A default catalogue variant cannot confirm the submitted three-probe observed listing; no specs promoted to an intended record. |
| [ThermoMaven catalogue, S40](https://www.thermomaven.com/) | F1 Turbo among multiple instant-read and wireless lines. | A catalogue title is not proof of exact model intent. No accuracy/certification claim adopted. |
| [Amazon invisible-ID help, S41](https://affiliate-program.amazon.com/help/node/topic/GF4RJEQNXSMR7SP3) | Tracking ID need not remain visible in the landing URL. | Missing visible `tag=` is neither success nor failure evidence. |
| [Amazon multiple-ID/report help, S42](https://affiliate-program.amazon.com/help/node/topic/GJDYPQZK6E37RLPU) | Manage Tracking ID, Summary Report, account limit. | Positive attribution evidence must come from the enrolled account workflow, not a URL inspection. |
| [GitHub Pages documentation, S38](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) | Static hosting and GitHub’s separate visitor-IP security logging. | No production collector on Pages; distinguish application data from host logs. |
| [Google sponsored-link guidance, S31](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) | Paid links use `sponsored`; multiple rel values allowed. | Preserve main’s strict qualification of every real Amazon product destination, including source citations. |
| [Google page-experience guidance, S43](https://developers.google.com/search/docs/appearance/page-experience) | Mobile content, secure serving, main-content distinction, no distracting ads/interstitials, no ranking guarantee. | Responsive source-led presentation is a design change, not a promise of traffic. |
| [Search Console verification, S44](https://support.google.com/webmasters/answer/9008080) | Ownership and verification methods. | Empty guarded token field and exact URL-prefix instructions; no fabricated property verification. |
| [Google sitemap documentation, S45](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) | Absolute canonical URLs, accurate lastmod, optional RSS, submission. | Per-page modification dates and no invented article publication dates from source-access dates. |

## Exact submitted-link observations — not intended-product confirmation

All five supplied URL strings were fetched on 2026-11-19. Returned Amazon landing
content used the fallback-parameter form (`plpRedirect=mhFallback`). Titles and
normalized `/dp/` destinations below are observations only. No retail price or
review data is republished from them. No enrolled-link test was performed.

| Supplied official resolver | Observed ASIN/title family | Intended ASIN / confirmed listing |
|---|---|---|
| [B04G1MEwY](https://link.amazon/B04G1MEwY) | B0CDY277D3; Chefman 6 Qt dual basket/windows | Blank, unconfirmed |
| [B02NbDxp3](https://link.amazon/B02NbDxp3) | B09B7SB46R; Emeril 26 Qt French door | Blank, unconfirmed |
| [B00hJ57DV](https://link.amazon/B00hJ57DV) | B08DKYBTPH; Chefman 8 Qt, 450 °F Hi-Fry in title | Blank, unconfirmed |
| [B0c8moW59](https://link.amazon/B0c8moW59) | B0DHZTCNR5; **ThermoMaven** thermometer title | Blank, unconfirmed |
| [B0f3GKalj](https://link.amazon/B0f3GKalj) | B0DZFD6R9Z; **CHEF iQ Sense** Gen3 three-probe title | Blank, unconfirmed |

`shopnow047c-20` remains selected but unvalidated and unapplied. The operational
`associate_tag` remains empty. Intended ASIN, official listing URL, confirmation
date/source, and enrolled per-product test fields remain empty/false. The campaign
ledger is empty. Uncertainty is **not** a finding that short links are invalid.

## Corrections and implementation boundaries

- **F96 open:** contradictory cord instructions inside the same Emeril manual.
- **F99 repaired, production hosting open:** incompatible browser/collector
  contracts; old PHP/Worker endpoints retired without accepting/storing bodies.
- **F100 repaired, infrastructure approval open:** privacy wording now includes
  host IP logs and local decision drafts, and the enabled notice describes all
  browser events rather than clicks alone.
- **F97 repaired:** old guide’s all-appliance dishwasher claim, omitted known
  8 Qt dimensions, capacity article’s incorrect same-total comparison of 6 and
  8 quarts, and unsupported “most common avoidable return” sentence.
- **F101 account/runtime boundary:** no invented first-party reports, link tests,
  Search Console data, approved infrastructure or conversion result.
- One canonical brand and reader sitemap; prior source generators stay read-only.
- Conceptual AI scene is visibly labelled; no generated branded-product likeness
  is offered as evidence. Product photography remains a separate rights gate.
- All 24 existing canonical guides revised after a full prose read; no duplicate query pages added. RSS is the
  actual reader-subscription mechanism, not a nonfunctional email form.

## Verification log

Baseline canonical build: 56 pages, 35 sitemap URLs and 24 RSS items. Baseline
verification: 134 HTML pages, 77 spec rows (75 populated / 2 blank+flagged), 43
registered sources, 0 errors. The original 17 isolated tests passed despite the
client/collector incompatibility; they were insufficient evidence.

Measurement repair: the expanded 29-test root suite passed after main’s exact-file
requirements guard was preserved during rebase. Synthetic HTTP integration writes
only to a temporary database outside the checkout and leaves the ledger empty.

First redesigned front-page browser pass: Chromium desktop 1440 px and mobile
390 px; no document horizontal overflow, disclosure below masthead and fully
visible (desktop bottom 129 px; mobile bottom 170 px). The full visual review and
all-pages regression gates are still pending at this report revision.

Final build, unit, source/link, reproducibility, browser, CI and deployment results
will be appended after execution, not anticipated here.

## Coordination / integration

The claim was committed and pushed before implementation. `main` advanced during
the first pull-before-push. Both append-only board records were preserved; main’s
sponsored-link and exact-file requirements guards were retained. That rebase
required a lease-protected update of this same session branch, not another branch.
No stale parallel PR was merged or closed and no historical generator was edited.

**PR, merge and production deployment:** pending at this report revision.


### Current-state reconciliation and deeper editorial audit

Main advanced to `cb33d97` (completed pass 14, PRs #157–#158) during
pull-before-push. Both coordination/source records were retained. Its flags
F90–F95, SG-49/SG-50/Q-41, breadcrumb counts, flag-anchor consistency guard,
sponsored destinations and exact-file requirement guard remain present. PUB-1
findings were renumbered F96–F101; F102 is a later distinct source-gate repair.
The overlapping presentation was replaced by the canonical publication template,
not by deleting main's evidence or historical source generators.

The original Suggestions effort/status fields and historical `implemented[]`
were not a reliable current-state partition. Each current row now has a dated
state and note; complete, superseded, partial, gated and open sum to the actual
register size. This does not turn an old disabled client into deployed analytics
or an old “done” label into confirmed product intent. Prior Q&A/prompt snapshots
are preserved in data history, owner choices remain empty, and agent execution
updates are labelled separately.

All 24 existing guides were then read as prose and substantially rewritten using
the named official-source scopes. Additional unsupported inferences were found:
proportional food load from quart capacity, a low-temperature proofing claim for
the Chefman dual basket, cooking/durability assertions, a 15-amp circuit assumption,
exact energy cost from rated watts, a definite “hybrid listing” explanation, and a
nutrition-regulatory classification. Those were removed, not assigned a citation
they did not have. The 8 Qt aerosol caution was corrected from its own manual.
Disclosure placement and conditional Amazon-content permission wording were also
reconciled. The S12 product description was re-opened and its “98% less oil” phrase
confirmed; it is treated only as a brand statement with no test method supplied
alongside it, not as nutrition, health or measured performance evidence.

A direct rendered-table audit found **27 rows** with no direct primary/repository
source, despite the old gate passing. A generic Flagged link counted as a source,
and a data row containing a `<th>` was skipped entirely. **F102:** the replacement
requires a registered primary URL, an exact submitted resolver, or an existing
exact-file record in this repository. It rejects arbitrary URLs on an official
host, unrelated repositories and a generic flag/summary. Editorial/implementation
rows now link their authoritative code/data record; they are not presented as
Amazon facts. Link identity/coverage does not prove arbitrary prose true, so scoped
reading remains necessary.

At this checkpoint, build and verifier pass (58 canonical pages / 37 sitemap URLs /
24 RSS items; 136 HTML pages / 77 spec rows / 45 sources / 0 errors). The expanded
**43-test root suite passes**, including explicit source-gate/header bypass,
state-partition, disclosure-order, asset-drift, unknown-date and known-correction
regressions. Full browser/annex/CI/deployment results still follow.


## Local final acceptance — executed, before PR CI/merge

- `bash scripts/ci-check.sh`: canonical build/source/link/privacy gates, root
  contract tests, **33 platform tests**, clean data audit, 16-file annex current
  check and **11,230 links** passed at the browser-ready checkpoint.
- `research/check_research.py`: **834 checks** passed, with its original source
  generator/data unchanged.
- `scripts/verify_site.py`: **393 assertions** passed; historical annex unchanged.
- `verify.py`: **136 published HTML pages**, 77 spec rows (75 populated / 2
  blank+flagged), 45 registered sources, **0 errors / 0 external warnings**.
  Optional `node_modules` and browser artifacts are pruned, not mistaken for
  publication HTML; every canonical/historical page remains in scope.
- JavaScript syntax checks and `git diff --check` passed.
- **10 Playwright tests passed** in Chromium (3.4 minutes): all **58 canonical
  pages × 320/390/768/1440 px**, disclosure immediately below masthead and fully
  above fold, no document overflow, decoded local images/fonts, no publisher
  analytics/cookies/storage writes on reader visits, one Workspace group, and
  no unexpected external runtime dependency. The absolute canonical asset URLs
  on the production 404 are mapped to the local checkout for this offline test.
- Separate no-JavaScript navigation, native Workspace, expanded product evidence,
  keyboard table scrolling, menu Escape/focus return, outside closing and local
  decision export/reload/clear passed. Malformed/denied storage does not break the
  workspace or claim a saved draft when storage is unavailable.
- Scoped axe checks on **12 representative reader/critical workspace routes at
  390 and 1440 px** reported **0 violations** for the selected WCAG A/AA tags.
  The audit found and repaired a visible-label/accessibility-name mismatch in
  the wordmark. This is not full WCAG certification or a user-assistive-tech study.
- Actual trusted primary, keyboard and middle activations reached the real Python
  HTTP handler over same-origin test HTTPS with **202** responses. Synthetic
  dispatch/right-click did not inflate counts. Cookie and Referer headers were
  absent from event requests even with a synthetic cookie installed; query/tag/
  ASIN/full-URL strings were absent from payloads. DNT/GPC suppression passed.
  A comparison view alone did not become an interaction.
- The browser reading bucket used a **virtual clock and explicitly controlled
  focus/visibility inputs**. It verified 59 active ticks, exclusion of hidden or
  unfocused ticks, then one fixed 60s bucket, with no repeat. Headless Playwright
  normally emulates focused tabs; no native OS-focus/real reading-time claim is
  made from this fixture. The Node VM tests separately cover the same state cases.
- All browser metrics live in a TemporaryDirectory database outside Git. The
  production switches stay false, active tag blank, per-product tests false and
  campaign ledger empty. No synthetic values were imported as campaign evidence.

### Final browser findings and bounded test-harness repairs

Visual inspection shortened product pages: a concise essentials table now leads,
with full dated listing/specification evidence in a native expandable section.
The mobile comparison row-label width was fixed so labels do not wrap one letter
per line. The redesigned sharing card uses the same local fonts and clearly
labelled conceptual scene. Current desktop/mobile screenshots were inspected.

The first headless run used a serverless single-process flag that prevented a
second browser context; ordinary sandboxed-test process settings fixed the harness.
A `networkidle` wait was inappropriate for the enabled keepalive event fixture:
requests were already accepted, while the wait did not finish. The tests now
assert actual collector/HTTP outcomes rather than idle timing. No acceptance
criterion was replaced by a delay or a fabricated successful response. A no-JS
text selector also intentionally ignored NOSCRIPT; the test checks the actual
visible notice element and DOM text instead.

The full browser run exposed a genuine privacy hardening issue in the stdlib
server’s fallback error path: an interrupted TLS request printed the client
address despite disabled request access logs. **F100 update:** the production
`AggregateHTTPServer` now suppresses expected disconnect diagnostics and emits
only a fixed nonidentifying message for unexpected errors—never request/exception
text or a traceback. Two negative log tests were added; the **45-test root suite**
passes and the five actual-browser measurement tests were re-run successfully on
that server. Proxy/host logs still require their own real deployment review.

Compliance implementation notes were also reconciled: no assigned sub-tags,
running paid-acquisition workflow, human sign-off, account-review clock or blanket
Agent-Term exemption is invented. Original notes remain dated history. The policy
quotes were not silently edited or blanket-stamped newly verified.

**PR CI, merge and actual Pages read-back remain pending at this checkpoint.**


## Integration with the completed parallel Z14 release

The next pull-before-push found `main` at `4ae97f0`, including PRs #160/#161.
That release independently addressed much of the same publication/evidence seam.
The stopped six-commit rebase was aborted intact, then one explicit main merge was
reconciled on the Arena-fixed current branch. Both histories, both complete board
records, the published Z14 report/receipt and its image/font/source assets remain.
No other session branch or historical generator was edited or discarded.

- Keep the already-public thermometer-note route
  **categories/cooking-thermometers.html**. The unmerged draft pathname was removed,
  not published as a duplicate. The unconfirmed shelf stays noindex and outside
  analytics eligibility, matching upstream's existing boundary.
- Upstream **F96 cord conflict, F97 article corrections, F98 date provenance and
  F99 protocol repair retain their published IDs**. Independent duplicate findings
  are consolidated into those rows with both reports/evidence. New distinct PUB-1
  findings are **F100 privacy/server-error logging**, **F101 external runtime/account
  boundary**, and **F102 direct-source/row-header bypass**. This is not a renumbering
  of an already-published upstream flag.
- Preserve explicit published_at=null, real modified_at, scoped source_checks and
  source-check history; preserve both suggestion/decision histories. Current-state
  and implementation compatibility views agree without inventing owner choices.
- Preserve bot/prerender/lifecycle opt-outs alongside the explicit enable switch,
  same-origin route and target-ID allowlists. Preserve stricter all-product-anchor
  sponsored/nofollow/noopener qualification, including `/gp/product/` destinations.
- Preserve the real progressive format filter, suggestion search/empty state/anchor
  recovery, clipboard-denial feedback and native no-JS alternatives in the selected
  theme. The source-linked 8 Qt dimensions remain available on the product cards.
- Preserve upstream's complete Q&A summary citations, the native Workspace **and**
  footer inventory guard, source/date/metadata tests and strict /Zone1/ subpath browser
  acceptance. Shape-specific tests were updated for the selected semantic header,
  `publication/` source paths and native details structure—not dropped or reduced.
- The original Z14 6 lb (2721 g) rotisserie-spit limit observation is retained with
  that session's date/source provenance. Two final attempts to reopen the official
  PDF returned a fetch failure; this integration does **not** claim those were a
  successful fresh load-limit read. It does not resurrect the false absence claim,
  infer load from quarts or provide a doneness recommendation. F96 still requires
  manufacturer clarification on the independent cord contradiction.

Post-integration checkpoint: canonical build **58 pages / 36 sitemap URLs / 24 RSS
items**, verifier **136 pages / 77 spec rows / 45 sources / 0 errors and warnings**;
**60 Python root tests and 8 retained JavaScript tests pass**. The preserved strict
subpath browser script passes **70 page/viewport combinations, 5 interaction groups
and 3 no-JS groups**, with no external request or page error. The broader native
HTTP/axe suite will be rerun on the combined tree before merge.


## Final publication receipt — completed

**Functional integration:** [PR #162](https://github.com/kanlerxz87-cyber/Zone1/pull/162)
merged with `gh pr merge 162 --merge` at **2026-11-19T07:19:38Z** as
**c8b9b61a4187bd511582bb054ee764f8a9feec5c**. No approval or manual review was
invented. The current Arena branch was never switched or renamed.

### Final combined gates

- **60 canonical Python tests + 8 Node client tests + 33 platform tests:** pass.
- **11 native Playwright tests:** pass on the integrated tree, including actual
  HTTP/HTTPS collector transport, trusted primary/keyboard/middle activations,
  DNT/GPC/automated-browser exclusion, controlled reading-state inputs, all 58
  canonical pages at four widths, no-JS flows, keyboard and local draft/export
  behaviour, and the scoped 12-route × 2-width axe checks with zero selected-tag
  violations.
- **Retained strict-subpath suite:** 70 page/viewport combinations, 5 interaction
  groups, 3 no-JS groups, no external request or page error.
- **136 HTML pages / 77 specification rows / 45 registered sources:** 0 verifier
  errors or external warnings. This is traceability/build validation, not a
  blanket fresh source or legal certification.
- **11,297 links**, clean platform data audit, **834 research checks**, **393 annex
  assertions** and the 16-file annex current-output gate: pass.
- Deterministic canonical rebuild: **64 artifacts, zero byte changes**. JavaScript
  syntax checks and Git whitespace/diff gates: pass. Historical generators/data
  were not silently edited.

PR [CI 44477886498](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44477886498)
passed both `verify` and `browser`; independent annex
[44477886612](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44477886612)
also passed. On the actual main merge, canonical
[CI 44478744857](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44478744857)
passed (including the full browser job), as did annex
[44478744750](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44478744750).

### Deployment proof and actual read-back

The build/reproducibility/deploy workflow
[44478744908](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44478744908)
succeeded through both jobs at **07:20:09Z**. The separate legacy Pages run
[44478743774](https://github.com/kanlerxz87-cyber/Zone1/actions/runs/44478743774)
also succeeded. The official Pages API reported **built**, **error.message=null**,
exact commit **c8b9b61**, updated **07:20:04Z**, duration **24,905 ms**. Source remains
**legacy / main / root**, HTTPS enforced. No Pages-configuration migration is
claimed.

Actual public fetches, after that deployment, returned the integrated content at:

- [Home](https://kanlerxz87-cyber.github.io/Zone1/): the current buying-question
  headline, three format choices/cards with source-linked dimensions, conceptual
  image caption, November notebook and RSS reader loop.
- [6 Qt model guide](https://kanlerxz87-cyber.github.io/Zone1/products/chefman-6qt-dual-basket.html):
  the original submitted Amazon URL, explicit paid-link/unknown-attribution note,
  concise essentials, two-minute Hi-Fry qualification and correct part-specific care.
- [Thermometer notes](https://kanlerxz87-cyber.github.io/Zone1/categories/cooking-thermometers.html):
  correct PI-04 ThermoMaven / PI-05 CHEF iQ mapping as observations only, original
  supplied URLs, no invented model or accuracy/certification claim.
- [Cord guide](https://kanlerxz87-cyber.github.io/Zone1/articles/extension-cord-rules-in-the-manuals.html):
  both incompatible manual directions, F96, and no permissive electrical recommendation.
- [About](https://kanlerxz87-cyber.github.io/Zone1/about.html): honest AI-assisted
  publication authorship, no tests/persona invented, imagery provenance, no live
  analytics and GitHub's separate IP security logs.
- [Measurement](https://kanlerxz87-cyber.github.io/Zone1/measurement.html) and
  [link-intent record](https://kanlerxz87-cyber.github.io/Zone1/product-intent.html):
  all five events inactive, selected ID unvalidated/unapplied, all five original
  submitted strings, separate observed/intended fields and no campaign report rows.
- [Live stylesheet](https://kanlerxz87-cyber.github.io/Zone1/assets/style.css): the
  selected publication tokens and local DM fonts, not the superseded theme.
- [RSS](https://kanlerxz87-cyber.github.io/Zone1/feed.xml): current rewritten guide
  titles and stable canonical links; no invented original item publication times.

These are actual public-content retrievals. They are distinct from local/CI
Chromium rendering; no remote browser/a11y certification or raw-byte equality with
the public proxy is claimed. All synthetic metrics remain outside Git and outside
the authorised campaign ledger.

### Process and remaining boundaries

A plain post-integration `git pull --rebase origin main` tried to flatten the
already-reconciled merge and stopped at the earlier claim. It was aborted intact.
The actual merge had both **929a411** and **4ae97f0** as parents. A fresh
`git pull --rebase --ff-only origin arena/1f9e7d52-zone1` then reported up to date,
followed by a normal fast-forward push. No other session branch was modified and
neither integration history was dropped. This is logged rather than masking a
failed command's exit status.

Active overlapping PR #159 was reviewed only for coordination/disposition. A
[scope/hold request](https://github.com/kanlerxz87-cyber/Zone1/pull/159#issuecomment-7002437543)
was posted; it was **not** merged, closed, imported or claimed as tested. Earlier
stale-PR dispositions remain preserved. The root publication is canonical while
historical annexes remain labelled public evidence; full archive-only deployment
wrapping is not claimed.

A nonblocking GitHub runner annotation says older action versions target Node 20
and are forced to Node 24. All jobs succeeded; an action-version maintenance
refresh is not represented as performed here.

**Still unverified, deliberately:** enrolled account/selected-ID ownership and
per-intended-product attribution; intended ASIN/listing confirmations; authorised
campaign/query reports; controlled production collector runtime and infrastructure
privacy/log approval; actual product-photography rights; and the Emeril cord
clarification. The cadence is a recorded plan, not a deployed scheduler. No revenue,
conversion, traffic or ranking promise was added to close any of these gates.

**PUB-1 repository/publication scope is complete and released.**

Receipt recorded at 2026-11-19T07:25:56Z. The follow-up publishes this already-observed release record and the narrowly scoped Flagged-introduction correction described below; it does not anticipate unperformed account or production actions.


### Last live-read finding — Flagged introduction corrected in the receipt follow-up

The final actual public Flagged read exposed a present-tense introduction left
outside the earlier article/register reconciliation: it labelled every historical
finding “Open items”, typed “3 Hard source conflicts”, and repeated a “most likely
two models” explanation above the dated evidence. Those claims were not supported
by the current-state register. The receipt follow-up therefore also corrects this
small generated surface: **recorded findings/history included**, computed source
and blank/populated-specification counts, and a source-linked model conflict with
no selected explanation. The cord safety conflict is explicitly highlighted.
Historical flag bodies/IDs remain untouched. A targeted negative regression raises
the root suite to **61 tests**; all current gates are rerun on the follow-up head.
This is a bounded content correction, not new source verification or a change to
account, link, analytics or campaign data. The prior functional release proof above
remains the already-observed PR #162 result.
