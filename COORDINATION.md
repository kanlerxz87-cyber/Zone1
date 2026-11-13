# COORDINATION — shared task board

**Repository:** https://github.com/kanlerxz87-cyber/Zone1
**Live site:** https://kanlerxz87-cyber.github.io/Zone1/
**Board last updated:** 2026-11-13

Two sessions worked on this repository. This board is the shared task register: every task
names its owner session and the files it touched, so no two sessions ever worked on the same
file at the same time. Every claim was committed and pushed before the work started, and
every completion record states the source that was checked.

| Session | Branch | Role | Outcome |
|---|---|---|---|
| `d14c5409` | `arena/d14c5409-zone1` | Repository review, first data pass, first site build, first PR and merge | Merged to `main` via PRs #1, #2 and #3. Its generator and datasets are preserved in `scripts/build.mjs` and `data/session-d14c5409/`. |
| `zone1-main` | `arena/2bef746a-zone1` | Re-retrieval and verification, the full data model, the thirteen-page site, integration, final PR and merge | This board's second half and the published site. |

**Status values:** `unclaimed` · `in progress` · `done` · `needs review` · `blocked`.
A `needs review` item is published on the site's **Flagged for Review** page and does not
block the site going live.

---

## Task board

| ID | Task | Status | Owner (session) | Files / scope |
|----|------|--------|-----------------|---------------|
| T0 | Claim board and open the session | done | d14c5409 | `COORDINATION.md` |
| T1 | Repo review, line by line, against official sources; irregularity log | done | d14c5409 | `REVIEW.md` (part 1–2), `COORDINATION.md` |
| T2 | Product data collection and verification for the three supplied links | done | zone1-main | `data/products.json` |
| T3 | Compliance review — Associates program terms, FTC disclosure rules | done | zone1-main | `data/program.json` |
| T4 | Static site build — landing, category subpages, tables, flagged page | done | d14c5409 | `scripts/build.mjs`, `data/session-d14c5409/`, `docs/` (now unbuilt) |
| T5 | Integration — rebuild, link check, PR to `main`, merge, verify Pages | done | d14c5409 | `main` (merge only), `COORDINATION.md` log |
| T6 | Re-retrieve the Amazon pages and recover the values the first pass could not read | done | zone1-main | `data/products.json` |
| T7 | Build the full data model — products, program terms, automation rules, flag register | done | zone1-main | `data/products.json`, `data/program.json`, `data/flags.json` |
| T8 | Build the thirteen-page site generator, stylesheet and script | done | zone1-main | `tools/build_site.py`, `assets/css/site.css`, `assets/js/site.js` |
| T9 | Research, analysis, SEO content, comparison, buying guide, campaign and tracking pages | done | zone1-main | `pages/**`, `index.html` |
| T10 | Build the offline integrity checker | done | zone1-main | `tools/check_links.py` |
| T11 | Strengthen the checker — dataset schema, official-host source cells, accessibility and responsive checks | done | zone1-main | `tools/check_links.py` |
| T12 | Reconcile the two sessions' work without discarding either side | done | zone1-main | `COORDINATION.md`, `README.md`, `REVIEW.md`, `EXECUTIVE_SUMMARY.md`, `data/**`, `scripts/build.mjs` |
| T13 | Correct the Product 1 condition wording — the `$57.45` offer is tagged `USED` | done | zone1-main | `data/products.json`, `data/flags.json` |
| T14 | Repository hygiene — `.gitignore`, CI workflow, archive the first iteration | done | zone1-main | `.gitignore`, `.github/workflows/site-check.yml`, `legacy/` |
| T15 | Final integration — rebuild, check, PR to `main`, merge, verify Pages, record the result | in progress | zone1-main | `main` (merge only), `COORDINATION.md` log |

**Scope rule that was followed:** shared outputs — the combined table data, the site index
and the navigation — were changed only by the integration session, and only after the other
session's work had finished and been merged.

---

## Claims log

| Date | Session | Claim | Files |
|---|---|---|---|
| 2026-11-13 | `d14c5409` | T0 — created the board and claimed T1–T4 | `COORDINATION.md` |
| 2026-11-13 | `d14c5409` | T5 reserved for final integration in that session | `main` (merge only) |
| 2026-11-13 | `zone1-main` | T6–T11 — re-retrieval, data model, site build, checker | `data/**`, `tools/**`, `assets/**`, `index.html`, `pages/**` |
| 2026-11-13 | `zone1-main` | T12–T15 — integration, correction, hygiene, final PR and merge | `COORDINATION.md`, `README.md`, `REVIEW.md`, `EXECUTIVE_SUMMARY.md`, `.gitignore`, `.github/**`, `legacy/**`, `scripts/build.mjs` |

---

## Completion records

### T1 — Repo review, line by line (done · `d14c5409`)

- **Sources:** the first session's register, preserved at `data/session-d14c5409/sources.json`
  (S1–S12).
- **Verification:** `git ls-files`, `git show --stat`, `git ls-remote`, and the GitHub API for
  the repository, the branch list and the Pages configuration.
- **Result:** 10 repository-state rows and 12 data-and-claims rows. Findings: the repository
  held only a 7-byte README; Pages was already configured for `main` `/`; no `.gitignore`,
  `LICENSE` or CI existed; a personal email address is visible in the public commit metadata;
  no link carried an Associates tag; the commission rate was unreachable; the brand spelling
  differed between two titles.
- **Irregularities:** F-12, F-13, F-14, F-15, F-16 in that session's numbering — all carried
  forward into the live register.

### T2 — Product data (done · `zone1-main`)

- **Sources:** S10 (Product 1), S11 (Product 3), S12 (Product 2), S13–S15 (the three supplied
  short links), S16 (Chefman storefront), S17 (Product 1 User Guide).
- **Verified:** ASIN, title, brand, manufacturer, model, UPC, item type, rating, rating count,
  new and used offer prices, list price, discount, price per count, "bought in past month",
  Amazon's Choice, Best Sellers Rank in two categories, dimensions, material, colour, special
  features, recommended uses, configuration, included components, electrical rating,
  temperature range, safety certification, warranty and the manufacturer feature bullets.
- **Left blank and flagged:** Product 2's dimensions, item weight, wattage, material, model
  number, UPC, Best Sellers Rank, temperature range, warranty and date first available (its
  detail page serves a reduced body — F-03); and Product 1's warranty and date first
  available (F-09).
- **Correction made:** the `$57.45` offer on Product 1 is tagged `buyingOptionType: USED` in
  Amazon's own embedded buy-box payload, so it is published as the used-condition offer and
  not as a second new-condition price (F-02).

### T3 — Compliance (done · `zone1-main`)

- **Sources:** S1 (Operating Agreement), S2 (Program Policies), S3 (rate card), S4–S6 (FTC
  Disclosures 101, the Endorsement Guides FAQ and 16 CFR Part 255), S7 (robots.txt), S9
  (Amazon trademark table).
- **Verification:** 30 program clauses and 10 automation rules, each with the section it comes
  from and a link to the source. Where a source is behind a sign-in wall the clause says so
  instead of reproducing a value.
- **Rules that shaped the build:** the required Associates statement on every page; the FTC
  disclosure immediately above every monetised block; direct Special Links only, never the
  supplied short links; no static price or star rating without an API-sourced link; no
  build-time Amazon fetching; and the non-US publisher clause.

### T4 — First site build (done · `d14c5409`)

- **Output:** a seven-page site — Overview, Home & Kitchen › Air Fryers, Analysis & Findings,
  Compliance, Sources, Flagged for Review, 404 — plus a root redirect.
- **Generator:** `scripts/build.mjs`, which still runs and still reproduces that site byte for
  byte from the preserved datasets in `data/session-d14c5409/`.
- **Not published:** the root site is now the thirteen-page site, and `docs/` is gitignored
  build output. Publishing both would have put a second, weaker copy of the project on the
  same domain under `/docs/`.

### T6 — Re-retrieval (done · `zone1-main`)

- **Method:** the first session's default retrieval path returned Amazon's footer boilerplate
  instead of the product-detail blocks. Requesting the detail page with its canonical query
  parameters — for example `https://www.amazon.com/dp/B0CDY277D3?psc=1&language=en_US` —
  returned the full buy box, feature bullets, Item details block and Best Sellers Rank.
- **Result:** the price, rating, rating count, demand badge and Best Sellers Rank for all
  three products were recovered and are published with the exact URL each was read from.
  Product 2 still serves a reduced body, so its values are read from Amazon's own search
  result for its ASIN (F-03).
- **Flag closed:** F-23.

### T7 — Data model (done · `zone1-main`)

- `data/products.json` — three product records, three link-resolution records, brand signals
  and the competitive set.
- `data/program.json` — 18 official sources, 30 program clauses, 10 automation rules.
- `data/flags.json` — 24 irregularities, F-01 to F-24, each with an observation, why it
  matters, the official source, the action taken, a status and whether it blocks publication.

### T8 — Site build (done · `zone1-main`)

- **Output:** thirteen pages at the repository root — landing dashboard, executive summary,
  catalogue, two category subpages, research and analysis, SEO article, comparison, buying
  guide, campaign and tracking, compliance, sources, flagged for review.
- **Generator:** `tools/build_site.py`, standard library only, writes `index.html`,
  `pages/**` and `assets/**`.
- **Presentation:** every finding, attribute, rule, source and flag is a table row, and every
  row carries a source cell linking to the page the value was read from.

### T10, T11 — Integrity checker (done · `zone1-main`)

- `tools/check_links.py` runs offline and fails on: a dataset that does not parse or is
  missing a schema key; a field marked `verified` with no source, a non-official source or a
  blank value; an `unverified` field that carries a value; a dangling id reference; a source
  cell pointing off an official host; a broken internal link or anchor; a non-`https` or
  non-official external link; a table row with no source cell; a rendered anchor still
  carrying the placeholder Associates tag; a missing disclosure string; a page with no
  language, viewport or description, or with more than one `<h1>`; a skipped heading level;
  an `<img>` without alt text; an anchor with no discernible label; a table with no header
  row; or an `aria-*` reference with no target.
- **Result at the time of writing:** 13 HTML files, 497 table rows, 635 external links,
  3 datasets — all checks passed.

### T12 — Integration (done · `zone1-main`)

- The first session's PRs #1, #2 and #3 were already merged into `main`. This session's
  branch was behind `main` and its `git pull --rebase` stopped on an add/add conflict in
  `COORDINATION.md` — both sessions had created the file from scratch.
- **Resolution:** the rebase was aborted, the first session's work was merged forward with
  `git merge origin/main`, and each conflicting file was resolved by hand. Neither side was
  discarded. The first session's datasets are preserved verbatim under
  `data/session-d14c5409/`, its generator still reproduces its site byte for byte, its root
  redirect is preserved in `legacy/`, and all 16 of its flags are carried into the live
  register with `legacy_ids` cross-references.
- Flag ids were kept in one sequence across both sessions so the live site has a single
  register: F-01 to F-13 are this session's, F-14 to F-24 are the carry-forward.

### T13 — Product 1 condition correction (done · `zone1-main`)

- Amazon's embedded buy-box payload for `B0CDY277D3` was re-read directly. It lists exactly
  two offers: `$79.93` with `buyingOptionType: NEW` and `$57.45` with `buyingOptionType: USED`.
- The dataset row that described `$57.45` as a second new-condition price was removed. The
  catalogue now publishes `$79.93` as the new price and `$57.45` as the used-condition
  offer, with the condition tag Amazon itself applies, the `-43%` savings line and the
  `$28.73` per-count figure. Flag F-02 was rewritten to describe what was actually observed.

### T14 — Repository hygiene (done · `zone1-main`)

- `.gitignore` added: `docs/`, `__pycache__/`, `node_modules/`, `.env`, `*.log`, OS cruft.
- `.github/workflows/site-check.yml` added: it rebuilds the site, fails if the committed
  pages differ from the generator output, runs the full integrity checker, and re-runs the
  archived build.
- `legacy/root-redirect-to-docs.html` preserves the first iteration's root redirect for
  provenance.
- A `LICENSE` was **not** added — it is a legal decision for the copyright holder, and it is
  recorded as an open item (F-17) rather than chosen on the owner's behalf.

### T15 — Final integration (in progress · `zone1-main`)

Recorded below once the PR is opened, merged and the deployment is verified.

---

## Flag summary

24 items in the live register (`data/flags.json`), all rendered on the site's
**Flagged for Review** page. 18 are open and 6 are resolved; resolved items stay published
so the audit trail is complete.

| ID | Severity | Status | Item |
|---|---|---|---|
| F-01 | high | open | The supplied `link.amazon` path segments are not ASINs |
| F-02 | medium | open | Amazon renders the used-condition offer without labelling its condition inline |
| F-03 | medium | open | Product 2's detail page serves a reduced body |
| F-04 | high | open | The Amazon Associates rate card is not publicly readable |
| F-05 | medium | open | Prices, badges, purchase-volume counts and ranks are point-in-time |
| F-06 | low | open | Product 1's capacity is rendered in litres on Amazon and in quarts by the manufacturer |
| F-07 | high | open | Program Policies restrict displaying prices without Amazon-sourced or API-sourced data |
| F-08 | high | open | Program Policies restrict displaying star ratings and reviews without API-sourced links |
| F-09 | low | open | Warranty and "date first available" were not readable for two of the three products |
| F-10 | high | open | Amazon's `robots.txt` disallows a large set of AI and research agents |
| F-11 | medium | open | The supplied `link.amazon` URLs cannot be reused as affiliate Special Links |
| F-12 | low | open | GitHub Pages was already configured for this repository before any change |
| F-13 | medium | open | No search-volume, keyword-difficulty or conversion-benchmark data is published |
| F-14 | high | open | Non-US publisher clause, and every price is a United States marketplace value |
| F-15 | low | **resolved** | The two Chefman listings are the same brand — confirmed from two official pages |
| F-16 | low | open | A personal email address is visible in the public commit metadata |
| F-17 | low | open | No `LICENSE`; `.gitignore` and CI added in this session |
| F-18 | medium | **resolved** | The supplied short links behave like a redirect wrapper and are never reused |
| F-19 | high | open | Associates enrolment is not confirmed and no supplied link carries a tag |
| F-20 | high | open | The live-data half of the platform needs an Amazon API credential that does not exist here |
| F-21 | low | open | Retrieval was done with an anonymous text fetch, not a logged-in browser session |
| F-22 | medium | open | The coordination spec's per-task branch convention could not be followed |
| F-23 | medium | **resolved** | The first iteration could not read price, rating or review count |
| F-24 | low | **resolved** | Product 3's canonical page served an interstitial in the first iteration |

---

## Conflict log

| Date | Session | Conflict | Resolution |
|---|---|---|---|
| 2026-11-13 | `zone1-main` | `git pull --rebase` stopped with `CONFLICT (add/add): Merge conflict in COORDINATION.md` while applying the first session's board commit `a1c2b7c`. Both sessions had created `COORDINATION.md` from scratch. | The rebase was aborted with `git rebase --abort` — no work was lost — and the first session's `main` was merged forward instead with `git merge origin/main`. `COORDINATION.md`, `README.md`, `data/flags.json`, `data/products.json` and `index.html` were resolved by hand: the first session's board, flags, datasets, generator and root redirect were preserved, and the richer second-session data was layered on top with explicit cross-references. Recorded as F-22. |
| 2026-11-13 | `zone1-main` | `data/flags.json`, `data/products.json` and `index.html` conflicted on the same merge (add/add). | The first session's versions were preserved verbatim under `data/session-d14c5409/`, its generator was left working against that directory, and its root redirect was preserved in `legacy/`. The live files carry the second session's richer data. Its `scripts/build.mjs` was patched to read the archived datasets and to stop overwriting the repository-root `index.html`. |
| 2026-11-13 | `zone1-main` | The first session's site was published from `docs/`, which collided with the second session's root-level site. | Only the thirteen-page root site is published. `docs/` is now gitignored build output, reproducible with `node scripts/build.mjs`. |

---

## Change log

| Date | Session | Change | Commit |
|---|---|---|---|
| 2026-11-13 | `d14c5409` | Claimed T1–T4 and created the board | `f4f0354` |
| 2026-11-13 | `d14c5409` | Verified product rows, sources, compliance, flags, site config, build and validate script | `4c75099` |
| 2026-11-13 | `d14c5409` | Generated the first static site | `1b7fbbb` |
| 2026-11-13 | `d14c5409` | Executive summary, repo review log, README, completion records | `9949ca2` |
| 2026-11-13 | `d14c5409` | Recorded PR #1 for integration | `7fdac07` |
| 2026-11-13 | `d14c5409` | Root `index.html` redirect to `docs/`; F13 updated | `984aa9c` |
| 2026-11-13 | `d14c5409` | T5 merge results, brand-label casing, F13 wording | `85ba3ef` |
| 2026-11-13 | `zone1-main` | Claimed T0–T14 and created the board | `a1c2b7c` |
| 2026-11-13 | `zone1-main` | Verified datasets, static site generator and the thirteen-page site | `ae0c4ed` |
| 2026-11-13 | `zone1-main` | Merged the first session's work forward without discarding it; unified the flag register across both sessions; corrected the Product 1 condition wording; strengthened the checker with dataset-schema, official-source, accessibility and responsive checks; added `.gitignore`, the CI workflow and the `legacy/` provenance archive; rewrote `README.md`, `EXECUTIVE_SUMMARY.md` and `REVIEW.md` | _see the PR below_ |
| 2026-11-13 | `zone1-main` | Final PR to `main`, merge and Pages verification | _see the PR below_ |

---

## Final integration record

_Filled in once the PR is opened, merged and the deployment is verified._

- **PR:** _pending_
- **Merge commit:** _pending_
- **GitHub Pages:** _pending_
- **Live check:** _pending_
