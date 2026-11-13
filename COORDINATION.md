# COORDINATION.md — shared task board

Shared task board for all agent sessions working in this repository.

**Status values:** `unclaimed` · `in progress` · `done` · `needs review`
(`needs review` = published on the *Flagged for Review* page; it does not block other tasks.)

**Branch rule for this session:** each session works only on its assigned branch. This session's
branch is `arena/4ba9e055-zone1` (branched from `main` @ `42f4036`). The `session-<id>/<task>` naming
from the brief could not be used, because the platform fixes the session to one branch and the
branch name cannot be changed. See the log entry *2026-11-13 · Branch naming* below.

**Session ID:** `arena-4ba9e055` (branch `arena/4ba9e055-zone1`)

## Task board

| ID | Task | Status | Owner (session ID) | Files in scope |
|----|------|--------|--------------------|----------------|
| T1 | Repo review (line-by-line, irregularities flagged) | in progress | arena-4ba9e055 | `reports/repo-review.md` (read-only review of `README.md`, `.git`) |
| T2 | Product data verification — 3 Amazon products (ASIN, title, category, links) | in progress | arena-4ba9e055 | `data/products.json` |
| T3 | Amazon Associates compliance + disclosure research | in progress | arena-4ba9e055 | `data/compliance.json` |
| T4 | Static site build (landing, category, analysis, flagged, sources pages) | in progress | arena-4ba9e055 | `scripts/**`, `docs/**`, `package.json` |
| T5 | Executive summary | in progress | arena-4ba9e055 | `EXECUTIVE_SUMMARY.md` |
| T6 | Integration: merge, re-verify combined data, link/build check, PR to `main`, merge, Pages deploy | unclaimed (runs last) | — | shared outputs (`docs/`, Pages config) |

No other session has claimed a task on this branch. `main` contains no `COORDINATION.md` before this commit.

## Task sources, verification, and irregularities

_To be filled in as each task completes (sources, checks performed, irregularities)._

## Log

- **2026-11-13 · Claim** — `arena-4ba9e055` claimed T1–T5 and listed T6 for the final integration step. Claim pushed to `arena/4ba9e055-zone1` before any other change.
- **2026-11-13 · Branch naming** — The brief asks for `session-<id>/<task>` branches and PRs per task. This session's branch is fixed as `arena/4ba9e055-zone1`, so all work is committed to it. Tasks are tracked here instead of on separate branches. Flagged for review.
