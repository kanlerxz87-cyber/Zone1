# COORDINATION — shared task board

Session ID: `d14c5409` (branch `arena/d14c5409-zone1`, based on `main` @ `42f4036`).

This session runs on a single branch (`arena/d14c5409-zone1`) as set by Arena. Other sessions, if any, must
claim tasks here and must not edit files in another session's claimed scope. Status values: `unclaimed`,
`in progress`, `done`, `needs review`. A `needs review` item is published on the **Flagged for Review** page
and does not block anything.

## Task board

| ID | Task | Status | Owner (session) | Files / scope |
|----|------|--------|-----------------|---------------|
| T1 | Repo review + irregularity log (line-by-line, official sources) | in progress | d14c5409 | `REVIEW.md`, `COORDINATION.md` |
| T2 | Product data collection + verification (3 Amazon products) | in progress | d14c5409 | `data/products.json`, `data/sources.json` |
| T3 | Compliance review (Amazon Associates policy + FTC disclosure) | in progress | d14c5409 | `data/compliance.json` |
| T4 | Static site build (landing + category subpages + tables + Flagged page) | in progress | d14c5409 | `scripts/build.mjs`, `docs/**` |
| T5 | Integration: rebuild, link check, PR to `main`, merge, Pages verify | unclaimed | — | `main` (merge only), `COORDINATION.md` log |

## Claims log

- 2026-11-13 — `d14c5409` claimed T1–T4 (single-session run). T5 reserved for final integration in this session.

## Handoff / conflict log

- _none yet_
