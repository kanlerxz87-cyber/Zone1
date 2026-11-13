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
