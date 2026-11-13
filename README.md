# Zone1 — AI-Powered Amazon Affiliate Marketing Platform

**Live site (GitHub Pages):** https://kanlerxz87-cyber.github.io/Zone1/

An automated Amazon affiliate marketing platform: product research and verification against
official sources, commission/niche analysis from the official Amazon Associates rate tables,
SEO-optimized marketing content (articles, comparisons, buying guides), affiliate link management
with click/conversion tracking, and Amazon Associates + FTC compliance enforcement.

> **Verification policy:** every value is checked against an official source. Anything that cannot
> be confirmed is left **blank** and flagged on the site's
> [Flagged for Review](https://kanlerxz87-cyber.github.io/Zone1/flagged.html) page. Nothing is
> inferred or filled in.

## Key finding (2026-11-13)

The three supplied product links (`link.amazon/B04G1MEwY`, `link.amazon/B02NbDxp3`,
`link.amazon/B00hJ57DV`) are **not valid**: the identifiers are 9 characters (ASINs are 10),
`link.amazon` is not an official Amazon link domain, and all three URLs land on Amazon's
missing-page fallback (random unrelated listings, `plpRedirect=mhFallback`). All product-level
data is therefore blank + flagged. See [reports/verification-log.md](reports/verification-log.md)
for the line-by-line evidence and [COORDINATION.md](COORDINATION.md) for the two-session record.

## Site map (published at the site root — integrated dashboard)

| Page | Contents |
|---|---|
| `index.html` | Dashboard landing page (KPIs, summary tables) |
| `products.html` | Product research & verification tables |
| `analysis.html` | Pricing / reviews / competition / commission analysis |
| `commissions.html` | Official Amazon Associates commission rate tables (verified) |
| `niches.html` | Niche identification framework (official rate-driven) |
| `content.html` | SEO content library + strategy |
| `articles.html` | Product article templates (3), data-safe |
| `comparison.html` | 3-way comparison article (data-safe) |
| `buying-guide.html` | Buying guide (data-safe) |
| `links.html` | Affiliate link manager + builder |
| `analytics.html` | Click/conversion tracking dashboard |
| `compliance.html` | Amazon Associates + FTC compliance (verbatim quotes) |
| `flagged.html` | Flagged for Review (all irregularities + sources) |
| `executive-summary.html` | Executive summary (site copy) |

## Session `d14c5409` build (preserved, published under `/docs/`)

A parallel session produced a second, schema-validated static site and data pipeline, preserved
unchanged in structure at [`docs/`](https://kanlerxz87-cyber.github.io/Zone1/docs/):

| Path | Purpose |
|------|---------|
| `data/products.json` | Product rows (JSON). Each value carries `status` (verified / derived / unverified) and `source`. Unverified values must be `null`. *(Identity fields corrected to `unverified` at integration — see COORDINATION.md "Disputed findings".)* |
| `data/sources.json` | Every source with its URL, access date and retrieval status. |
| `data/compliance.json` | Associates and FTC requirements with sources and site status. |
| `data/flags.json` | Flagged-for-review items with severity, sources and the action needed. |
| `data/site.json` | Site-level settings, including the Associates status shown in the disclosure banner. |
| `scripts/build.mjs` | Validates all data, then writes the static site to `docs/`. No dependencies. |
| `docs/` | Generated site (Overview, category, analysis, compliance, sources, flagged, 404). |
| `EXECUTIVE_SUMMARY.md` / `REVIEW.md` | That session's executive summary and repo review log. |

### Build and check

```bash
node scripts/build.mjs --check   # validate only (exit 1 on any error)
node scripts/build.mjs           # validate, then write docs/
```

The build fails if a verified value has no valid source, an unverified value is filled in, a row's
official link is not on an official host, or an internal link points to a file that will not be built.

## Integrated data (CSV)

| Path | Contents |
|---|---|
| `data/products.csv` | The three supplied links with per-row official checks (all unverified/blank) |
| `data/commission-rates.csv` | Full official US commission Table 1 (fetched from affiliate-program.amazon.com) |
| `reports/executive-summary.md` | Executive summary (integrated) |
| `reports/verification-log.md` | Line-by-line verification log with official source links |

## Verification rules (both sessions)

1. A value is shown only if it was read from an official source (Amazon product page, Amazon Associates Central, FTC, GitHub Docs).
2. A value that cannot be confirmed is left blank and flagged as unverified. Nothing is estimated or invented.
3. Prices, ratings, review counts and commission rates are **not** estimated.
4. Category names derived from title words are marked "derived", not "verified".

## Disclosure

This site contains affiliate links. **As an Amazon Associate I earn from qualifying purchases.**
See [compliance.html](compliance.html) for the full policy basis (Associates Program Operating
Agreement §5; FTC Disclosures 101).
