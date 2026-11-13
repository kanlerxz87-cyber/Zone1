# Zone1 — AI-Powered Amazon Affiliate Research & Marketing Platform

A source-verified affiliate marketing workspace: automated product research, niche analysis, pricing / reviews /
competition / commission analysis (compliance-aware), SEO content and buying guides, affiliate link management,
click & conversion tracking design, and continuous optimization — built around the Amazon Associates Program
Operating Agreement (updated 2025-10-15), Program Policies (updated 2026-04-14), and FTC disclosure guidance.

**Live site (GitHub Pages):** published from `main` — this build lives at `session-3740f69d/` (URL path `/session-3740f69d/`).

## Repository layout

| Path | Contents |
|------|----------|
| `EXECUTIVE_SUMMARY.md` | Executive summary of objectives, findings, flagged items, owner actions |
| `COORDINATION.md` | Shared task board for parallel agent sessions (claims, verification log, integration record) |
| `session-3740f69d/` | GitHub Pages site — dashboard + subpages: Products, Analysis, Niches, Content, Links, Tracking, Platform, Compliance, Flagged, Sources |
| `session-3740f69d/SOURCES.md` | Source register index |
| `session-3740f69d/data/products.json` | Machine-readable product registry (every value carries provenance; restricted values are null) |
| `session-3740f69d/data/sources.json` | Machine-readable source register |

## Data rules (no hallucinations)

1. Every value published links to an **official** source (amazon.com, affiliate-program.amazon.com,
   webservices.amazon.com, kdp.amazon.com, ftc.gov).
2. If a value cannot be confirmed from an official source, the cell is left **blank** and flagged on the
   **Flagged for Review** page — never inferred or estimated.
3. Volatile values (rankings, listings) are dated snapshots. Restricted values (prices, star ratings) are withheld
   per Associates Program Policies §2(b)/§6(t) until PA API access exists.

## Affiliate disclosure

As an Amazon Associate I earn from qualifying purchases.

Zone1 is an independent research workspace and is not affiliated with, endorsed by, or sponsored by Amazon.com, Inc.

## Status

Built and verified 2026-11-13 by session `session-arena-3740f69d`. See `COORDINATION.md` for the task board,
verification log, and the integration record (PR link, merge result, Pages deployment).
