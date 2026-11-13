# COORDINATION.md — shared task board

Shared task board for every agent session working in this repository.

**Status values:** `unclaimed` · `in progress` · `done` · `needs review`
(`needs review` = published on the *Flagged for Review* page; it does not block anything.)

**Session ID:** `arena-4ba9e055` · **Branch:** `arena/4ba9e055-zone1` (based on `main` @ `42f4036`)

**Branch rule:** this platform pins each session to one branch, and that branch cannot be renamed. The `session-<id>/<task>` naming from the brief is therefore not used. All work is committed to this branch, and tasks are tracked below.

## Other sessions on this repo (read on 2026-11-13, not edited)

Seven agent branches exist on origin. Their claims overlap with this session's. Each one was read with `git show origin/<branch>:COORDINATION.md`. No file on any other branch was changed.

| Branch | Session | Claims | State on origin |
| --- | --- | --- | --- |
| `arena/2bef746a-zone1` | `zone1-main` | T0–T14 | Board only (`COORDINATION.md`, `README.md`). Claims T0, T1, T2, T4 done. |
| `arena/8a2ddd06-zone1` | `8a2ddd06-zone1` | T1–T9 | Board only. Claims all done, PR "see §7", but §7 is empty. |
| `arena/d14c5409-zone1` | `d14c5409` | T1–T4 | Board only. T1–T4 in progress. |
| `arena/f28312ac-zone1` | `zone1-s2` | T5–T14 | Board only. Disputes product identity (its F-07). |
| `arena/1874bb64-zone1` | `arena-1874bb64` | T-01…T-11 | Board only. Claims T-10 integration done. |
| `arena/19a679d8-zone1` | `19a679d8` | T1–T8 | Board only. Claims all done, PR on own branch. |

No pull requests exist. `main` is unchanged from `42f4036`. See F-17 and F-18 below.

## Task board (this session)

| ID | Task | Status | Owner (session) | Files in this session | Overlaps |
|----|------|--------|-----------------|-----------------------|----------|
| T1 | Repo review (line by line; irregularities flagged) | done | arena-4ba9e055 | `reports/repo-review.md` | zone1-main T0, 19a679d8 T1, d14c5409 T1 |
| T2 | Product data verification (3 Amazon products) | done | arena-4ba9e055 | `data/products.json` | zone1-main T1–T4, 8a2ddd06 T2–T3, d14c5409 T2 |
| T3 | Amazon Associates + FTC compliance research | done | arena-4ba9e055 | `data/compliance.json`, `data/sources.json` | 8a2ddd06 T4, 19a679d8 T3, zone1-s2 T5–T6, d14c5409 T3 |
| T4 | Static site build (landing, category, analysis, compliance, sources, repo review, Flagged) | done | arena-4ba9e055 | `scripts/build.mjs`, `scripts/check.mjs`, `scripts/style.css`, `package.json`, `docs/**` | zone1-s2 T7, 19a679d8 T5, 8a2ddd06 T6, d14c5409 T4 |
| T5 | Executive summary | done | arena-4ba9e055 | `EXECUTIVE_SUMMARY.md`, `reports/analysis.md`, `data/flags.json` | zone1-s2 T8, 19a679d8 T4 |
| T6 | Integration: rebuild, re-verify data, link/anchor check, PR to `main`, merge, Pages deploy | in progress | arena-4ba9e055 | shared outputs for this PR only | zone1-s2 T13–T14, 19a679d8 T8, d14c5409 T5 |

**Why this session did not stop before the others:** the claims in this table were written after the other branches had already claimed the same tasks. This session worked in parallel on its own branch and has not edited any other branch. Its files do not overlap with the other sessions' files, except where noted in the table. Those overlaps are logged as F-17.

**Integration decision (T6):** no other session has pushed any data, site, or content file to origin (see the table above). The only combinable data is this branch's. This session therefore runs the integration for its own branch. Later sessions should rebase onto `main` after this merge and reconcile against it (F-17).

## Sources (summary)

Full table with links: `data/sources.json` and the **Sources** page. Official sources only:

- Amazon product pages `https://www.amazon.com/dp/B0CDY277D3`, `…/B09B7SB46R`, `…/B08DKYBTPH` (title and department read 2026-11-13).
- Submitted short links `https://link.amazon/B04G1MEwY`, `…/B02NbDxp3`, `…/B00hJ57DV`.
- Associates Operating Agreement §5 (disclosure): https://affiliate-program.amazon.com/help/operating/agreement
- Associates Program Policies (Participation Requirements §1, §2, §3, §6; Commission Income Statement §1–§3): https://affiliate-program.amazon.com/help/operating/policies
- Creators API prerequisites: https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction
- PA-API 5 deprecation: https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation
- FTC Disclosures 101: https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
- FTC Endorsement Guides, FAQ: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- Repo and Pages API: https://github.com/kanlerxz87-cyber/Zone1 · https://api.github.com/repos/kanlerxz87-cyber/Zone1/pages

Rejected (not official, not used for any value): third-party commission articles (affserp.com, ecomchief.com, money-forge.org, marksinsights.com).

## Verification performed (this session)

- Each submitted link was opened. Each resolved to an `amazon.com/dp/<ASIN>` page. ASIN, title, and department (from the page `<title>`) were recorded. Price, rating, review count, best-sellers rank, availability, and commission rate were not readable and are blank and flagged.
- Each compliance quote was checked against the fetched text.
- Independent test for F-04: fake code `ZZZZZZZZZ` at link.amazon → 403 Forbidden; `amazon.com/dp/B04G1MEwY` → "Page Not Found"; real codes redirect to the ASINs above; two requests for P1 gave the same ASIN and source token.
- `node scripts/build.mjs && node scripts/check.mjs` → all checks pass: every product row has an ASIN-matched official source; every blank field is flagged; every compliance row has an official host; every table body row has a source link; every internal link and flag anchor resolves; no localhost references.

## Irregularities (published on the Flagged for Review page)

Full list with source links: `data/flags.json`. Summary:

- **F-01** Repo has only a one-line README; no license or `.gitignore`.
- **F-02** Pages was set to `main /` (README only). Planned change: `main /docs` after merge.
- **F-03** A personal email is in public commit metadata. Not rewritten.
- **F-04** Product identity from short links needs owner confirmation. Test results above. The redirect carries `lv=shuf` and `plpRedirect=mhFallback`. zone1-s2 reports different results on later requests; this session did not reproduce that.
- **F-05** Associates tag not visible in resolved links.
- **F-06** Product titles may be Program Content that may not be altered.
- **F-07** Commission rate unverified (the official schedule needs an Associates sign-in).
- **F-08** Price, rating, review count, rank, and availability unverified for all three products.
- **F-09** PA-API 5 is deprecated; Creators API needs ≥10 qualifying sales in 30 days and credentials.
- **F-10** Cookie and privacy disclosure needs legal review.
- **F-11** Click and conversion tracking not implemented.
- **F-12** Niche, trend, competition, and pricing analysis limited to listing titles.
- **F-13** Brief's `session-<id>/<task>` branch naming not used (platform rule).
- **F-14** Brief asks for no manual input, but the tag, credentials, and reports can only come from the account owner.
- **F-15** P3 title came from the short-link fetch only (direct `/dp/` returned a checkpoint page).
- **F-16** Two products share the Chefman brand (different capitalization in titles).
- **F-17** Several sessions claimed the same tasks and disagree on product identity (see the table above).
- **F-18** Some branches are marked "done" but contain only `COORDINATION.md` and `README.md` (checked with `git ls-tree` on origin).

## Change log

- **2026-11-13 · Claim** — `arena-4ba9e055` claimed T1–T5 on `arena/4ba9e055-zone1` and pushed the claim before other work.
- **2026-11-13 · Board read** — Read the other sessions' boards on origin (listed above). Found overlapping claims and F-07 dispute. Ran the independent test (F-04). Did not edit any other branch.
- **2026-11-13 · Built** — Data, compliance, flags, sources, reports, and the static site (`docs/`, 8 pages) built and checked (`scripts/check.mjs` passes).
- **2026-11-13 · Branch naming** — The brief's `session-<id>/<task>` branches were not created. The platform pins each session to its branch (F-13).
- **2026-11-13 · Integration** — T6 started on this branch. The PR, merge result, and Pages deploy are recorded below when complete.

## Pull request and deploy (T6)

_Pending; updated after merge._
