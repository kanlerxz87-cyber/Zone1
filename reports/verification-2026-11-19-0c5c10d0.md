# Verification and status record — arena/0c5c10d0-zone1 (2026-11-19 UTC)

**Branch:** `arena/0c5c10d0-zone1` (fixed for this session; not renamed)
**Base:** `main` at `2be3bea` (merge of PR #163, the PUB-1 receipt) — recorded in `COORDINATION.md` at 10:47 UTC with the file scope below.
**Scope of this pass:** spend the fortnightly editorial cadence on one guide a shopper actually reads; re-read live the sources that copy depends on; register what those reads changed as flags and compliance rows; add the decision-desk rows that follow from them; correct one test that asserted a frozen article count.
**Result in one line:** one new canonical guide is published (`articles/probe-in-an-air-fryer.html`), four dated findings and one policy-revision finding are registered as **F104–F108**, three compliance rows now quote the live Program Policies text read today (**C19–C21**), four suggestions and three questions were added to the desk, and every gate is green. Account-only facts remain unconfirmed and are labelled as such; nothing was marked verified without a read made in this session.

---

## 1. Starting state (read, not assumed)

- `git status` clean; branch equal to `origin/main` at `2be3bea`; 444 tracked files.
- Baseline before any edit: `python3 build.py` exit 0 → `python3 verify.py` **136 pages, 77 spec rows (75 verified, 2 blank and flagged), 45 sources, 0 external warnings, 0 errors**; sitemap **36 URLs**, feed **24 items**; rebuild byte-identical.
- Open pull requests at claim time: #139, #141, #144, #146, #150 (all 2026-11-17) and **#159** (2026-11-19T07:13Z). None was merged or closed by this pass; #159's state is recorded in §7.
- No other session held a live claim when this pass started. Two other sessions (`arena/1970a80b-zone1`, `arena/6ace936d-zone1`) merged into `main` while this pass was in flight; their work was integrated, not overwritten — see §5.

## 2. What this pass published

| Surface | Change |
|---|---|
| `articles/probe-in-an-air-fryer.html` | New canonical guide, kind *Guide*, cluster `live`, kicker *Manual walkthrough*, 4 minutes, seven sections. Every factual sentence cites a document read live today: S15, S18, S13, S12, S29, S37, S39. |
| `data/articles.json` | 24 → 25 rows. `published_at` stays `null` because no first-publication timestamp is established for this publication (F98); `modified_at 2026-11-19T11:05:00Z`; `sources_read` / `sources_check` dated 2026-11-19. |
| `data/topics.json` | TP-22 → `published`, with `published_as` and a status note naming the premise that was dropped and the flag that records it (F104). TP-19 recorded as considered and **held**, with both reasons (cadence limit; its Q-20 gate). |
| `data/clusters.json` | New article filed in the `live` cluster in the same commit (4 → 5 members), `compiled 2026-11-19`. |
| Counts after integration | **137** pages, **37** sitemap URLs, **25** feed items, **77** spec rows (75 verified / 2 blank and flagged), **46** sources, **102** programme flags. |

The guide states plainly that no document read here clears leaving a probe in a running unit, and quotes what the documents do say: “Do not leave the air fryer unattended during use”, “at least 6 inches of clearance on top and back”, “Leave at least 5 inches … top, back, and sides”, the door-linked system and idle auto-off, and the manual's own “Use this chart and a food thermometer” USDA internal-temperature table.

## 3. Dated reads made in this session (2026-11-19, 10:47–11:05 UTC)

| Source read | What it settled |
|---|---|
| `https://link.amazon/B04G1MEwY` → `/dp/B0CDY277D3` | Title unchanged; still served with `plpRedirect=mhFallback`, no visible `tag=`. Matches PI-01. No intent field filled. |
| `https://link.amazon/B02NbDxp3` → `/dp/B09B7SB46R` | Title still says 24 one-touch presets and six accessories; the 6-vs-7 accessory and 24-vs-25 preset conflicts stand as published register rows. |
| `https://link.amazon/B00hJ57DV` → `/dp/B08DKYBTPH` | Title still advertises a 450 °F Hi-Fry option against the RJ38-SQSS-8T brand page and manual. Unchanged conflict. |
| `https://link.amazon/B0c8moW59` → `/dp/B0DHZTCNR5` | ThermoMaven 1 Sec, Black, in the *Meat* node; still no model number readable. `channelId=500` here against `704` on the air-fryer pair — recorded as request noise (F95), not evidence. |
| `https://link.amazon/B0f3GKalj` → `/dp/B0DZFD6R9Z` | CHEF iQ Sense Gen3 3-probe title; the observed title lists “Air Fryer” among the environments. Matches PI-05; intent fields still blank. |
| S15 — Emeril FAFO-001 manual PDF | Clearance “at least 5 inches … top, back, and sides”; “NEVER use with an extension cord”; 3-minute idle auto-off; 20-second fan run-on; 30-minute cool-down before cleaning; accessory weight limits; the internal-temperature meat chart with “Use this chart and a food thermometer”; Before-First-Use burn-in; French equivalents. |
| S18 — Chefman RJ38-SQPF-3TDB-2W guide | “Do not leave the air fryer unattended during use”; HI-FRY 450 °F / 235 °C for two minutes; SYNC FINISH and its break conditions; “Never fill the baskets with oil”; the non-aerosol-mister exception; first-use odour wording; E1/E2; warranty terms. |
| S13 — Chefman RJ38-SQSS-8T guide | “at least 6 inches of clearance on top and back”; five-minute preheat recommendation; the per-food chart; “Follow food-safety guidelines for doneness”; no burn-in instruction. |
| S39 — CHEF iQ iQ Sense product page | CQ60-1C-Z1-E shown as the default selection; “oven, stovetop, gas and charcoal grills, smoker, air fryer, deep fryer, and sous vide”; “heat resistant up to 1,000ºF (537ºC)”; feature list “4 internal temperature sensors … within 1°F” plus “1 ambient temperature sensor”, against prose claiming “Five internal sensors”. |
| S2 — Associates Program Policies | Header still reads **“Updated: April 14, 2026.”** Read directly, not from cache. §1(c)(iii) 180-day shipping/payment condition quoted; §2(b) read in full: Special-Link formatting, product-list original-content rule, limited-time-promotion removal rule, price-display conditions. |
| S46 — Amazon's “what's changed” notice | **Not read directly:** two fetch attempts this pass failed. Registered as a source with that limitation on the row. No sentence on the site quotes it as verified policy text. |

Prices visible in “customers who viewed” rails were deliberately not reused: price tracking and price display are restricted by the Program Policies, and `check_no_price_tracking` enforces it here.

## 4. Findings registered

| Flag | One-line summary | Status |
|---|---|---|
| **F104** | The queued TP-22 hook “the appliance is built to run unattended” is contradicted by S18 and unsupported by S15. Premise dropped before writing; hook text left in Git history rather than silently rewritten. | Recorded; rule adopted: a topic card is a hypothesis, not a source |
| **F105** | The Emeril cord conflict is not a translation artefact — the French safeguard and the French wiring note contradict each other the same way. | Second dated observation for **F96**, which stays open |
| **F106** | CHEF iQ's page describes its own sensors two ways (“Five internal sensors” vs “4 internal … + 1 ambient”); the observed listing title says “5 Sensors”. | No probe count published as a verified spec |
| **F107** | “Before first use” differs by brand (burn-in vs odour-only), as does clearance (5 in vs 6 in). | Reason TP-19 must keep three procedures; raised as SG-53 |
| **F108** | Amazon revised the Program Policies on 14 April 2026; the register recorded the stamp for days but not the content. One item confirmed from a direct read and quoted (C19); three remain unquoted because the notice could not be fetched. | Open until S46 is read directly |

**Renumbering note.** These five rows were drafted as F103–F107. While this pass was in flight, `arena/1970a80b-zone1` merged its own F103 (historical-build sponsored-link and short-link wording). Rather than renumber the published ids of another session, this pass renumbered its own rows to F104–F108 and made `page_flagged()` sort the register by numeric id on render, so the table stays readable whatever order sessions land in.

## 5. Integration with two parallel merges

`origin/main` advanced by three merges during this pass (#165, #169, #170). Integrating them produced conflicts in `build.py`, `flagged.html` and `COORDINATION.md`:

- **`build.py`** — both sides appended to `PROGRAMME_FLAGS` and `REPO_EVIDENCE`. Resolution keeps main's F103 row and evidence entry and this pass's F104–F108, with the duplicate `F102` evidence key removed. `ast.literal_eval` equality on the whole `PROGRAMME_FLAGS` list was asserted before writing: 102 rows, ids unique, no row content changed by the merge.
- **`COORDINATION.md`** — both sides appended dated sections at end of file. Both kept; no session history rewritten.
- **`flagged.html`** and every other generated surface were regenerated by `python3 build.py` rather than hand-merged.

## 6. Registers, compliance and decision desk

- **C19, C20, C21** added to `data/compliance.json` with verbatim quotes and today's read date: the 180-day shipping-and-payment condition; the rule that links to product-list pages need additional relevant original content; the obligation to remove a limited-time promotion mention as soon as the promotion ends. `C21` is the rule the seasonal guides are written to, and why they name no discount, deal or bestseller.
- **S46** registered as a source, with its limitation stated on the row and echoed in `data/sources.json → reverified_2026_11-19_0c5c10d0`, which lists what was read directly and what was **not** read this pass (S46, the S1 header, every Associates Central screen, listing spec blocks beyond the served title).
- **Q-42, Q-43, Q-44** added: the paid/boosted-advertisement disqualifier (missing, and what would settle it), the narrowed onsite-commission scope (missing), and the re-read cadence question (recorded as `known`: the rule was adopted this pass; the automatic window check is proposed, not built).
- **SG-51…SG-54** added with paths, evidence links, effort/risk and the blocking questions: read the April revision in full (SG-51, blocked by Q-42/Q-43), a dated “rules changed” line on the compliance page (SG-52), per-product before-first-use blocks from each unit's own manual (SG-53), and one-sentence answers at the top of every guide (SG-54). All four are recorded as `partial`/`open`, not delivered — none is represented as implemented.
- **B-07** (“Actually generate organic traffic”) stays the single `not_delivered` row. Its note now records that the site is at 25 articles / 37 indexable URLs, still with no verified search property, no query data, no inbound link and no analytics: findability metadata is not the gap. **F-02**'s note records today's policy re-read and the F108 finding.
- **`tests/test_publication_output.py`** asserted `24 == len(articles)` inside a sitemap test, so it failed for the wrong reason the moment a cadence guide was published. It now asserts the invariant — the sitemap carries exactly one entry per registered article and no entry the register does not know — with the shipped count recorded as a floor (`>= 24`).
- `data/suggestions.json` uses `implementation.state ∈ {proposed, partial, implemented}`; the three new proposals were first written as `not_started`, which the test suite rejected. Recorded here because a rejected value is a fact about the contract.

## 7. Gates

| Gate | Command | Result |
|---|---|---|
| Build | `python3 build.py` | exit 0 — 137 pages, sitemap 37 URLs, feed 25 items |
| Verifier | `python3 verify.py` | 137 pages; 77 spec rows (75 verified, 2 blank+flagged); 46 sources; **0 errors, 0 external warnings**; one NOTE (pre-existing caution row: `chefman-8qt-turbofry/Basket divider`) |
| Canonical unit tests | `python3 -m unittest discover -s tests` | **61 tests, OK** |
| Client contract tests | `node --test tests/*.test.cjs` | **8 tests, 8 pass, 0 fail** |
| Engine tests | `python3 -m unittest discover -s platform/tests -t platform` | **33 tests, OK** |
| Data audit | `python3 platform/audit/report.py` | **AUDIT PASSED (0 warnings)** |
| Research layer | `python3 research/check_research.py` | OK — no broken links, no unsourced rows, disclosures present on every page |
| Legacy build currency | `python3 scripts/build_s2_site.py --check` | build current, 16 files |
| Link check | `python3 scripts/check_links.py` | **ok · 11,527 links · 13 pages owned by this session (+124 inherited, advisory)**. One advisory: `dashboard/flagged.html` links a blob ref `arena/6ec3c2da-zone1` the checker cannot resolve. Checked against the remote: that branch **does** exist (`gh api repos/…/branches/arena/6ec3c2da-zone1` returned it), so this is a checker limitation against a shallow local clone, not a dead link. No change made in the read-only legacy tree. |
| Annex verifier | `python3 scripts/verify_site.py` | **ALL CHECKS PASSED**, 393 assertions |
| Reproducibility | rebuild, then `git status` | only the intended changes differ |

Not run locally: the Playwright browser suite (needs a Chromium download outside the allowed hosts). CI runs it on the pull request; this pass does not claim its result.

**PR #159 review (no action taken).** Its head is reachable and its four commits are the same work already in `main` — `analytics/*`, the measurement client and the coordination records — but `git merge-base origin/main tmp159` reports **no merge base**, because `main` in this sandbox is a shallow clone (`git rev-parse --is-shallow-repository` → `true`) and `origin/main` currently reads as a single-commit history locally while the API reports 616 commits. GitHub reports `mergeable: UNKNOWN`, `mergeStateStatus: UNKNOWN`. So: **not** mergeable-by-inspection from this clone, contents appear superseded by later merges, and no evidence was found that would justify closing it. Disposition left to the owner, consistent with Q-41 / SG-50. Nothing was merged or closed by this pass.

## 8. Not verified, and not claimed

- `config.json` `associate_tag` blank; `shopnow047c-20` **selected, not applied**, `selected_tracking_id_associates_central_confirmed: false`.
- Every PI row's `intended_asin`, `official_listing_url`, `confirmation_date` null and `associates_link_test_passed: false`. Observed redirect targets were re-read today; intended products remain unconfirmed and are kept in separate fields.
- No Special Links validated; no Amazon-served price or rating anywhere; no popularity or “trending” claim; no conversion score or revenue forecast.
- Search Console ownership and query data; production analytics host, runtime and privacy/log approval (`enabled: false`); the campaign ledger stays at zero rows; photography rights; a named human editor; the F96 manufacturer clarification.
- This pass did not re-read every file in the repository, and does not certify legal compliance, accessibility, rankings or conversions.

## 9. Release

Recorded here after `gh pr merge` and a confirmed Pages deployment, in the same style as the pass-14 receipt: PR number, merge commit, Pages API status read back after the merge, and the actual public URL content that was retrieved.
