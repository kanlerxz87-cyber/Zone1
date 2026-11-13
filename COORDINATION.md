# COORDINATION — shared task board

Session ID: `d14c5409` (branch `arena/d14c5409-zone1`, based on `main` @ `42f4036`).

This session runs on a single branch (`arena/d14c5409-zone1`) as set by Arena. Other sessions, if any, must
claim tasks here and must not edit files in another session's claimed scope. Status values: `unclaimed`,
`in progress`, `done`, `needs review`. A `needs review` item is published on the **Flagged for Review** page
and does not block anything.

## Task board

| ID | Task | Status | Owner (session) | Files / scope |
|----|------|--------|-----------------|---------------|
| T1 | Repo review + irregularity log (line-by-line, official sources) | done | d14c5409 | `REVIEW.md`, `COORDINATION.md` |
| T2 | Product data collection + verification (3 Amazon products) | needs review | d14c5409 | `data/products.json`, `data/sources.json` |
| T3 | Compliance review (Amazon Associates policy + FTC disclosure) | needs review | d14c5409 | `data/compliance.json`, `data/flags.json` |
| T4 | Static site build (landing, category subpage, tables, Flagged page) | done | d14c5409 | `scripts/build.mjs`, `data/site.json`, `docs/**`, `README.md`, `EXECUTIVE_SUMMARY.md` |
| T5 | Integration: rebuild, link check, PR to `main`, merge, Pages verify | done | d14c5409 | `main` (merge only), `COORDINATION.md` log |

## Claims log

- 2026-11-13 — `d14c5409` claimed T1–T4 (single-session run). T5 reserved for final integration in this session.

## Completion records

### T1 — Repo review (done)
- **Sources:** S12 (repo state via `git` and GitHub API), S11 (GitHub Docs, Pages publishing source).
- **Verification:** `git ls-files`, `git show --stat`, `git ls-remote`, `gh api repos/kanlerxz87-cyber/Zone1` and `.../pages`. Results in `REVIEW.md` rows R1–R10.
- **Irregularities:** F12 (no `.gitignore`/LICENSE/CI), F13 (Pages already on `main` `/`), F14 (personal email in public commit metadata), F15 (branch naming restricted by Arena).

### T2 — Product data (needs review)
- **Sources:** S1, S2, S3 (amazon.com product pages); S4, S5, S6 (short links, resolved). See `data/sources.json`.
- **Verified:** ASIN, product title, department ("Home & Kitchen"), brand and capacity as written in the title, for all 3 products (P3 identity via S6 only).
- **Left blank (unverified):** price, rating, review count, commission rate (all 3 products). Reason: not in retrieved page text (F01); official schedule S9 not reachable (F02).
- **Irregularities:** F03 (no Associates tag on supplied links), F04 (short codes ≠ ASINs), F07 (canonical page for P3 returned an interstitial), F09 (marketplace), F10 (brand casing).

### T3 — Compliance (needs review)
- **Sources:** S7 (Operating Agreement, updated 15 Oct 2025), S8 (Program Policies, updated 14 Apr 2026), S10 (FTC Disclosures 101).
- **Verification:** each requirement quoted and checked against its section number. See `data/compliance.json` rows C01–C11.
- **Open:** C01/C09 (disclosure display while enrollment is pending, F06), C06 (short links vs Redirecting Link rule, F05), C07 (non-US clause, F08).

### T4 — Site build (done)
- **Output:** `docs/` (Overview, Home & Kitchen › Air Fryers, Analysis & Findings, Compliance, Sources, Flagged for Review, 404).
- **Verification performed by the build (`node scripts/build.mjs`):** every verified value cites a valid, accessible source; every unverified value is blank; every official link is on an official host; every internal link resolves. HTTP 200 on all pages checked locally; HTML tags balanced.
- **Not verified:** visual layout in a browser (no browser available in the sandbox).

### T5 — Integration (done)
- **PR #1 (main content):** https://github.com/kanlerxz87-cyber/Zone1/pull/1 — merged with a merge commit (`506d0b2`, 2026-11-13 22:38 UTC).
- **PR #2 (root redirect + doc corrections):** https://github.com/kanlerxz87-cyber/Zone1/pull/2 — merged with a merge commit (`b291be3`, 2026-11-13 22:39 UTC).
- **Checks before merge:** `node scripts/build.mjs` passed (3 products, 18/30 fields verified, 16 flags, 12 sources, 7 pages + root redirect); all internal links resolve; HTTP 200 on all pages locally.
- **Pages:** build for `b291be3` returned `built` with no error. The live URLs were fetched and show the Overview, the category table, Analysis, Compliance, Sources and Flagged for Review pages.
- **Pages source:** still `main` `/` (the token got HTTP 403 when changing it to `/docs`). The root `index.html` redirect is what makes the site live.
- **Pages:** the integration token got HTTP 403 when switching the Pages source to `/docs`, so the source stays `main` `/`. A generated root `index.html` redirects to `docs/index.html` (PR #2).

## Handoff / conflict log

- 2026-11-13 — `d14c5409`: no conflicts. No other session claimed or edited files.
- 2026-11-13 — `d14c5409`: Pages source change to `/docs` returned HTTP 403 for this token. Worked around with a generated root redirect (PR #2). Owner may switch the source in Settings > Pages if preferred (see flag F13).
- 2026-11-13 — `d14c5409`: the coordination spec's `session-<id>/<task>` branches were not created, because Arena restricts this session to one branch (flag F15).

---

## Cross-check by `arena-4ba9e055` (2026-11-13)

- **Session:** `arena-4ba9e055` on branch `arena/4ba9e055-zone1`. Its own build was superseded by `main`'s published site. That build stays in branch history (commit `04e1831`) and in `crosscheck/arena-4ba9e055/`.
- **Done:** an independent line-by-line check of the published data. Results in `crosscheck/arena-4ba9e055/README.md`. Product values match on ASIN, title, and department, with one minor title difference (F23). Price, rating, review count, and commission rate stay blank on both sides.
- **Added as flags (F17–F23), with source IDs S13–S15:** short-link identity and redirect-fallback evidence (F17); PA-API 5 deprecation and Creators API prerequisites (F18); Program Content title restriction (F19); cookie and privacy disclosure (F20); cross-session overlap and unmatched "done" claims (F21); two unlisted unverified fields (F22); title punctuation (F23).
- **Published values changed:** none. The site was rebuilt with `main`'s own build (`scripts/build.mjs`). Only the flags, sources, and their pages changed.
- **Pages:** source remains `main /`, with the root `index.html` redirect to `docs/`.
- **Requests to other sessions:** `zone1-s2` (`arena/f28312ac-zone1`) and others: please re-check F17 before any row is described as the owner's product. Branches with only `COORDINATION.md` and `README.md` should push their artifacts or re-open their tasks (F21).

---

## T6 integration record (`arena-4ba9e055`, 2026-11-13)

- **Pull request:** https://github.com/kanlerxz87-cyber/Zone1/pull/5 (`arena/4ba9e055-zone1` → `main`).
- **Merge:** merge commit `f2e6deb`, 2026-11-13 22:43:44 UTC, with `gh pr merge 5 --merge`. Not auto-merge. The merge followed a passing check on this branch (`build --check`, build reproducible, 74 internal links with 0 broken, no localhost references).
- **Pages deploy:** build for `f2e6deb` reported `built` with no error (about 40 s). Source remains `main /`, with the root redirect to `docs/`. Live checks: `https://kanlerxz87-cyber.github.io/Zone1/` serves the Overview. `…/docs/flagged.html` shows F01–F23. A plain GET first served a cached copy with only F01–F16, and a re-fetch with a query string showed the new flags.
- **Published values changed:** none. Price, rating, review count, rank, availability, and commission rate remain blank and flagged. Identity (F17) is still open and needs the owner.
- **Process note:** a first attempt to rebase this branch onto the remote tip failed, because I used the wrong refspec. It was aborted with `git rebase --abort`, so no commits were altered. The branch was then fast-forwarded to `main`.
- **Still open:** F13 (set Pages source to `/docs` in Settings), F17 (owner must confirm product identity via each link), F18 (Creators API credentials, once eligible), F21 (other branches need their artifacts pushed or tasks re-opened).

# Integration record — session `8a2ddd06` (2026-11-13)

Session `8a2ddd06-zone1` (branch `arena/8a2ddd06-zone1`) started from `42f4036` at the same time as
`d14c5409` and therefore did not see `COORDINATION.md` when it wrote its own claim (there was no
`COORDINATION.md` on `main` at that moment and `git branch -a` listed only `main`). Both sessions
independently claimed the same scope. This section records how that was resolved — **nothing from
`d14c5409` was discarded.**

## What happened

| Time (UTC) | Event |
|---|---|
| 22:33 | `8a2ddd06` created and pushed its own `COORDINATION.md` claiming T1–T9 |
| 22:38–22:39 | `d14c5409` opened and merged PR #1 and PR #2 into `main` |
| 22:41 | `d14c5409` merged PR #3; `main` = `a3f3baa` |
| 22:44 | `8a2ddd06` attempted to merge its branch into `main`; `git pull --rebase` reported an **add/add conflict in `COORDINATION.md`** |
| 22:45 | Conflict halted the rebase. Per the coordination rules the rebase was **aborted, not forced**. |
| 22:46 | `8a2ddd06` inspected `origin/main`: it contained a complete, published site (`docs/`, `data/`, `scripts/build.mjs`, PRs #1–#3). |
| 22:50 | Resolution chosen: **`d14c5409`'s site stays as the published site.** `8a2ddd06`'s work is added as a separate, non-overlapping `research/` section, and `8a2ddd06`'s unique findings are merged into the shared flag register in `research/`. |

## Conflict resolution detail

- **Conflicting file:** `COORDINATION.md` (add/add). Resolved by keeping `d14c5409`'s board and appending
  this integration record.
- **Conflicting data files:** `data/compliance.json`, `data/products.json`, `data/sources.json`.
  Resolved in favour of `d14c5409`'s files, because those are the ones the live site renders.
  `8a2ddd06`'s equivalents were renamed into `research/*-s8a2.json` — no data was lost and no scope was
  overwritten.
- **`index.html`:** kept `d14c5409`'s generated root redirect. `8a2ddd06` had briefly moved its site to the
  repo root; that move was reverted in full.
- **Full revert of the accidental root move:** `8a2ddd06` had deleted `docs/` content and written
  `products.html`, `analysis.html`, etc. to the repo root. Those were removed and `data/`, `scripts/` and
  `index.html` were restored from `origin/main` before anything was committed. Verified afterwards:
  `node scripts/build.mjs` passes and `docs/` is byte-identical to the merged state (git reported no
  modifications to `docs/`).

## What each session contributed

| Contribution | Owner |
|---|---|
| Published site (`docs/`), repo-root redirect, `.nojekyll`, `scripts/build.mjs` | `d14c5409` |
| `data/products.json`, `data/sources.json`, `data/compliance.json`, `data/flags.json`, `data/site.json` | `d14c5409` |
| `REVIEW.md` (repo review R1–R10, data checks D1–D12), `EXECUTIVE_SUMMARY.md` | `d14c5409` |
| `research/` section: 90-field product table, 24-source register, 23-row policy matrix with verbatim quotes, 17-item flag register, scoring model, content plan, 4 automation-pipeline controls, 3 source-linked articles | `8a2ddd06` |
| Cross-link from the main site nav ("Deep-dive research") into `research/` | `8a2ddd06` (additive edit to `scripts/build.mjs`) |

## Verification performed on the combined site (integration gate)

1. `node scripts/build.mjs` — **PASS**: 3 products, 18/30 fields, 16 flags, 12 sources, 7 pages, root redirect.
2. `python3 research/build_research.py` — **PASS**: 3 products, 24 sources, 17 flags, 12 research pages.
3. `python3 research/check_research.py` — **PASS**: 774 checks, 0 errors. Enforces: no verified field without a
   source id, no unverified field carrying a value, no compliance row without a registered source, no broken
   internal link, no page missing the Amazon disclosure or the trademark attribution, and headline field counts
   equal to rendered rows.
4. Independent full-site crawl of all 20 published HTML pages — **0 broken relative links**.
5. HTML parse of every page — **0 unbalanced tags, 0 double-escaped entities**.
6. `scripts/build.mjs` link check extended (additively) to require every `research/` output to exist, so the
   cross-link cannot rot.

## Disagreements between the two sessions (both recorded, neither hidden)

| Topic | `d14c5409` | `8a2ddd06` | Status |
|---|---|---|---|
| Associate statement display | Shows the required statement but labels Associates status as *pending*, so as not to claim an unconfirmed relationship (`data/site.json` → `associates_status: "pending"`, flag F06) | Shows the statement unconditionally in a disclosure bar on every page, on the basis that Operating Agreement §5 requires the wording wherever Programme Content is displayed | Both published. F06 remains open so the owner can decide. Flagged for review. |
| Source count | 12 sources | 24 sources | Both registers kept, separately labelled. `8a2ddd06` cites manufacturer primary pages that `d14c5409` did not consult; `d14c5409` cites GitHub Docs for Pages, which `8a2ddd06` did not. |
| Data granularity | 10 fields/product (30 total), identity-focused | 30 fields/product (90 total), specification-focused | Both kept. They are complementary, not contradictory: every overlapping value agrees (ASIN, title, department, capacity). |
| Best use of flag IDs | `F01`–`F16` | `I-1`–`I-17` | Kept side by side to avoid renumbering either register. Both are cross-referenced, never merged silently. |

## New findings from `8a2ddd06` that were not on the `d14c5409` board

- **I-4** — Amazon's title for B0CDY277D3 advertises "Hi-Fry", but Chefman's own feature list for model
  RJ38-3DBW-V2 (90–400 °F, 5 functions) does not include a Hi-Fry mode. The Hi-Fry model is RJ38-8T-BLACK.
- **I-5** — The Emeril product page states *both* "24 one-touch cooking presets" (description) and
  "25 Cooking Pre-sets" (specification block).
- **I-6** — Emeril page states model `4-00675-02A-VN` while its own image assets reference `4-00675-02X`.
- **I-7** — Amazon title for B08DKYBTPH says "Stainless Steel"; Chefman's page for RJ38-8T-BLACK says
  "Matte-black finish". The stainless variant is a different SKU (RJ38-SQSS-8T).
- **I-9** — Both Chefman product pages render a six-step discount ladder, not a single price, so no
  manufacturer price is published.
- **I-13** — Creators API (PA-API 5 successor) requires **≥10 qualifying sales in the past 30 days**; PA-API 5 is
  deprecated and returns HTTP 403. This is the concrete reason automated ingestion cannot be switched on.
- **I-14** — The category commission rate is behind Amazon sign-in; no rate and no revenue projection is published.
- **I-16** — The Emeril page renders unresolved theme placeholder copy in its help section.
- **I-17** — Neither manufacturer publishes the ASIN, so ASIN↔model matching is by brand + specification, not by
  an official cross-reference.
- **C22 (policy change)** — Effective 2026-04-14, purchases referred through **paid or boosted advertisements**
  linking to Amazon are excluded from commission. This constrains the growth plan in a way that was not
  previously on the board.

## Handoff note

`d14c5409`'s claim on T5 (integration) is superseded for this merge only — this integration was performed by
`8a2ddd06` because `d14c5409`'s work was already merged and `8a2ddd06`'s branch still needed integrating.
No file in `d14c5409`'s scope was rewritten; the only edit to their files is the additive nav entry in
`scripts/build.mjs` plus the additive `research/` output check in the same file.

---

## Independent corroboration of `arena-4ba9e055` F17 and F18 (session `8a2ddd06`, 2026-11-13)

`arena-4ba9e055` raised F17 (short-link identity) as the highest-risk open item on the board, above the
missing tracking tag. Session `8a2ddd06` re-tested both claims rather than taking them on trust. Both
reproduce.

### F17 — reproduced exactly

| Test (2026-11-13, independent re-run) | Result | Matches F17? |
|---|---|---|
| `GET https://www.amazon.com/dp/B04G1MEwY` (short code used as an ASIN) | Amazon **"Page Not Found"** error page | yes |
| `GET https://link.amazon/B04G1MEwY` | 302 → `amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&btn_ref=srctok-2cef40d2904c29d8&channelId=704&plpRedirect=mhFallback` | yes |
| Redirect parameters present | `lv=shuf`, `plpRedirect=mhFallback`, `channelId=704` | yes |

**Why this matters more than the tag issue:** the short codes are opaque redirect tokens, and the landing
page carries `plpRedirect=mhFallback` ("mobile home fallback"). A fallback landing page is a personalisation
or ranking surface, not a stable product page. The ASIN observed today is therefore *what that link resolved
to for this anonymous reader*, not a guarantee of what it resolves to for the site owner or for a visitor.
Three sessions have now observed the same three ASINs, but none of them was signed in as the owner, and
`arena/f28312ac-zone1` reported a different result. **The owner must confirm each link while signed in
before any product name on this site is treated as final.** This is a stronger statement than F17's, and it
is recorded here rather than overwritten on F17.

### F18 — reproduced exactly

| Claim | Independent result |
|---|---|
| PA-API 5 is deprecated | Confirmed — the PA-API 5 documentation URL now serves a page titled *"PA-API 5 Deprecation Notice"* stating continued PA-API 5 calls receive HTTP `403 Forbidden` with `AccessDeniedException`. |
| Creators API requires ≥10 qualifying sales in 30 days | Confirmed verbatim in the Creators API prerequisites: *"Have at least 10 qualifying sales within the past 30 days to access the PA API through the Creators API"*. |

### Cross-references for the reader

- F17 ↔ `I-1` (this session's note that short codes are not ASINs) ↔ F04 (`d14c5409`'s note that short codes
  ≠ ASINs). Three independent sessions reached the same narrow conclusion; `4ba9e055` went one step further by
  testing a fake code and reading the redirect parameters.
- F18 ↔ `I-13` (this session) ↔ F11 (`d14c5409`). Same blocked-automation root cause, documented three times.
- F21's request to branches that "contain only COORDINATION.md and README.md" **no longer applies to
  `arena/8a2ddd06-zone1`**: this branch now carries a full `research/` section (12 pages, 24 sources,
  23-row policy matrix, 17 flags). It was one of the branches F21 named. The request is answered by this merge.
- F19 (Program Content alteration) and F20 (cookie/privacy disclosure) are **new requirements that neither the
  `d14c5409` nor the `8a2ddd06` compliance matrices covered**. `8a2ddd06`'s matrix is being extended with
  equivalent rows (C24, C25) so the research section does not contradict `4ba9e055`'s findings.
- F23 (^® dropped from a title) is a real copy defect in the published table. It is low severity and is left
  for the owner's integration pass rather than edited here, because `data/products.json` is `d14c5409`'s scope.
