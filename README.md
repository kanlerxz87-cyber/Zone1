# Zone1 — Amazon Affiliate Marketing Platform

An AI-powered Amazon affiliate marketing platform that automates product research,
identifies trending / high-converting products, analyzes pricing, reviews, competition
and commission potential, generates SEO-optimized product articles, comparisons and
buying guides, manages affiliate links, tracks clicks and conversions, and optimizes
campaigns — all while staying compliant with Amazon Associates policies and disclosure
requirements.

## Site

Static, dashboard-style website served via **GitHub Pages**. Open the deployed site, or
serve locally:

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

## Pages

| Page | Purpose |
|------|---------|
| `index.html` | Landing / dashboard overview |
| `executive-summary.html` | Executive summary of the project and findings |
| `products.html` | Supplied affiliate listings + verification table |
| `research.html` | Automated research & analysis methodology |
| `content.html` | SEO content generation framework |
| `tracking.html` | Click / conversion tracking & optimization |
| `compliance.html` | Official Amazon Associates rules & commission rates |
| `methodology.html` | How every value was verified |
| `flagged-for-review.html` | Flagged irregularities & unverified items |

## Data & verification policy

Every table row carries a source link to an **official** site. If a value could not be
confirmed from an official source, it is left **blank** and flagged **UNVERIFIED** —
never inferred or filled. See `COORDINATION.md` and the *Methodology* page for the full
verification log.

## Current status

The three supplied affiliate links (ASINs `B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`) could
not be verified against a live Amazon listing from this environment (Amazon blocks
automated access). All product attributes are therefore left blank and flagged. The
platform is otherwise complete and published for review. See the **Flagged for Review**
page.

## Coordination

`COORDINATION.md` is the shared task board (tasks, statuses, owning session, files,
sources, verification, irregularities, PR/merge/deploy record).
