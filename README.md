# Zone1 — Amazon affiliate product research (verified, source-linked)

Live site (after the owner merges and Pages deploys): https://kanlerxz87-cyber.github.io/Zone1/

A simple dashboard for three Amazon.com products submitted for affiliate marketing. Every value on the site is either
read from a cited official source on 2026-11-13 or left **blank and marked unverified**. Nothing is estimated or invented.

- **Overview** — executive summary, KPI tiles, category index
- **Home & Kitchen › Air Fryers** — product table with official source links on every row
- **Analysis & Findings** — verified findings, what is blocked and why, official commission method
- **Compliance** — Amazon Associates and FTC requirements, each with its source and site status
- **Sources** — every source with retrieval status
- **Flagged for Review** — irregularities and open decisions, with source links

Full executive summary: [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md).
Repo review log: [REVIEW.md](REVIEW.md). Shared task board: [COORDINATION.md](COORDINATION.md).

## Repository layout

| Path | Purpose |
|------|---------|
| `data/products.json` | Product rows. Each value carries `status` (verified / derived / unverified) and `source`. Unverified values must be `null`. |
| `data/sources.json` | Every source with its URL, access date and retrieval status. |
| `data/compliance.json` | Associates and FTC requirements with sources and site status. |
| `data/flags.json` | Flagged-for-review items with severity, sources and the action needed. |
| `data/site.json` | Site-level settings, including the Associates status shown in the disclosure banner. |
| `scripts/build.mjs` | Validates all data, then writes the static site to `docs/`. No dependencies. |
| `docs/` | Generated site. Opened through the root `index.html` redirect (Pages source is `main` `/`). |
| `index.html` (root) | Generated redirect to `docs/index.html`, so the Pages URL opens the site. |

## Build and check

```bash
node scripts/build.mjs --check   # validate only (exit 1 on any error)
node scripts/build.mjs           # validate, then write docs/
```

The build fails if:
- a verified or derived value has no valid source,
- an unverified value is filled in,
- a row's official link is not on an official host,
- an internal link points to a file that will not be built.

External links were checked manually with the fetch tool. Build-time checks do not reach the network.

## Verification rules

1. A value is shown only if it was read from an official source (Amazon product page, Amazon Associates Central, FTC, GitHub Docs).
2. A value that cannot be confirmed is left blank and flagged as unverified (see `flags.json`).
3. Prices, ratings, review counts and commission rates are **not** estimated. Price display is restricted by Associates Program Policies s.2(b).
4. Category names derived from title words are marked "derived", not "verified".

## Not built (and why)

The full AI platform in the brief needs Amazon Creators API / PA-API credentials, Associates account data and an analytics account.
None are available to this session, and building those features without them would mean inventing data. See flag F11.

## `research/` — deep-dive research section (session `8a2ddd06`)

Two sessions worked this repository in parallel from the same base commit and both claimed the same scope;
see the integration record at the bottom of [COORDINATION.md](COORDINATION.md). The published dashboard in
`docs/` is session `d14c5409`'s build. Session `8a2ddd06`'s independent work is published as an additive
section at **`/research/`** and is linked from the main navigation as "Deep-dive research ↗".

What the research section adds:

- a 90-field product table (30 fields per SKU) where every field is `{value, source, verified}`
- a 24-source register including the manufacturers' own product pages (chefman.com, emerileveryday.com),
  Associates Central policy documents with their *Updated* dates, 16 CFR Part 255, 16 CFR Part 465 and the
  FTC Endorsement Guides
- a 23-row compliance matrix with **verbatim quotations** and the section number for each requirement
- a 17-item flag register (`I-1`–`I-17`) with root-cause detail for each item
- a transparent scoring model, a content plan, and a 10-step automation pipeline with a compliance control
  attached to every step
- three source-linked articles (a buying guide and two comparisons) that claim no hands-on testing

Build and verify it independently:

```bash
python3 research/build_research.py     # regenerate research/*.html
python3 research/check_research.py     # 774 checks; exits non-zero on any failure
node scripts/build.mjs                 # main site; also requires every research/ output to exist
```

Neither generator touches the other's files. The only cross-file dependency is the nav entry in
`scripts/build.mjs` and the output-existence check that keeps that nav entry from rotting.
