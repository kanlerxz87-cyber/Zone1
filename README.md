# Zone1 Kitchen

A buyer-first, **AI-assisted, documentation-based** kitchen publication. The canonical
site compares documented air-fryer formats and answers practical buying/care questions.
It does not claim hands-on tests, human expertise, search demand or sales results.

**Publication:** https://kanlerxz87-cyber.github.io/Zone1/\
**Owner overview:** [workspace.html](https://kanlerxz87-cyber.github.io/Zone1/workspace.html)\
**Dated briefing:** [Executive summary — 19 November 2026](EXECUTIVE-SUMMARY-2026-11-19.md)\
**Evidence, limitations & release receipts:** [19 November verification](reports/verification-2026-11-19-53d18637.md)

## Read or operate it

| Surface | Purpose |
|---|---|
| `index.html` | Editorial front page: product formats, existing question-led articles, seasonal edit and RSS. |
| `categories/kitchen-appliances.html`, `products/`, `compare.html` | Source-linked documented product guides and comparison; conflicts and blank values remain visible. |
| `guides/`, `articles/`, `clusters.html`, `feed.xml` | Buying guide, existing sourced articles, reader-intent filing and RSS. |
| `about.html` | Production method, affiliate relationship, imagery, no-testing rule and corrections route. |
| `workspace.html` | Concise known / missing / next discovery-step brief. All dashboards are also in one Workspace menu and the complete footer index. |
| `product-intent.html` | Five exact submitted links; intended listings separate from dated redirect observations; selected ID and campaign ledger. |
| `measurement.html`, `analytics/README.md` | One five-event contract and explicit code-versus-deployment boundary. |
| `suggestions.html`, `questions.html`, `decision-log.html` | Alternatives, unknowns and recorded actions. Agent implementation is not an invented owner choice. |
| `data.html`, `flagged.html`, `requirements.html` | Evidence register, unresolved findings and scoped requirement status. A source-presence check is not semantic or legal certification. |
| `executive-summary.html` | Current executive briefing, distinct from dated historical pass reports. |
| `previous-passes.html` | Historical independent builds and their evidence role. |

### Money path: deliberately unresolved

`shopnow047c-20` is the **selected**, user-provided ID. It is not confirmed in Associates
Central and is not applied by this build. Intended ASIN, official listing URL, confirmation
date/source and the per-product enrolled-Associates test results are unconfirmed.

All five submitted URLs are preserved exactly in `data/product-intent.json`. Observed
redirects are not intended identity or attribution. A missing tag in a landing URL is
not failed-attribution proof. Purchase CTAs remain gated; no replacement Special Link
is guessed from a candidate ASIN. The exact short-link compliance status is unresolved:
https://kanlerxz87-cyber.github.io/Zone3/flagged.html#FLG-003

### Measurement: implemented and tested, **not deployed**

- `page_view`: once when a canonical reader document becomes visible, not a unique session.
- `outbound_click`: trusted activation of a tagged allowed Amazon destination; site product ID.
- `article_engagement`: one fixed 60-second visible/focused threshold, not completion.
- `comparison_interaction`: internal product-guide activation from Compare, not table visibility.
- `affiliate_report_import`: authorized first-party aggregate import, **never a browser order pixel**.

The maintained client and Python collector share this contract. PHP/Worker v1 adapters
are retired with HTTP 410; they are not interchangeable deployment choices.

Production switches/gates are off and the endpoint is blank. GitHub Pages is static
hosting, not a persistent collector runtime. App storage contains only daily aggregates;
provider/proxy connection logs still require review. Browser counts can be forged or
undercounted and are not orders or commission attribution. The campaign ledger is empty;
that means no authorized rows, **not** a claim of zero real orders.

See [analytics/README.md](analytics/README.md) for runtime/privacy/logging/receipt gates,
retention, the optional untested container recipe and authorized nullable-report import.
No account credentials belong in this repository or frontend.

## Build & verify

The generator and collector use the Python standard library; Python 3.11+ is supported.
Node 22.17+ runs the client tests and optional real-browser tooling.

```sh
python3 build.py                        # regenerate canonical output
bash scripts/ci-check.sh                # canonical, client, engine, annex and staged-artifact gates

# Real Chromium + axe, using pinned npm test-only dependencies:
npm ci --prefix tests/browser-tools --no-audit --no-fund
node tests/browser_check.cjs

# Local static preview, not a production analytics deployment:
python3 -m http.server 8080 --bind 0.0.0.0
```

`scripts/check_canonical.py` hashes the existing canonical output **before** regeneration.
It fails if rebuilding changes it; it does not compare a fresh write against itself.
`verify.py` checks rendered structure/links/source IDs and spec traceability, not account
facts or the substantive adequacy of every historical citation. The full test script also
keeps independent platform/annex regression gates.

The browser fixture is local HTTPS with an ephemeral database outside the checkout.
External requests, including Amazon, are blocked. Enabled-path emission is injected only
into fixture responses; real config, generated HTML and the campaign ledger stay unchanged.
No-JavaScript navigation, keyboard focus, print disclosures, narrow layouts and scoped
accessibility checks are included. Automated axe checks are not full WCAG certification.

### Maintained inputs versus generated output

- `build.py`, `data/*.json`: canonical publication/content and evidence inputs.
- `publication/style.css`, `publication/app.js`: maintained presentation sources.
- `analytics/client.js`: sole browser measurement source.
- `assets/style.css`, `assets/app.js`, `assets/analytics.js`, root/category/product/guide/article
  HTML, sitemap, robots and RSS: generated; rebuild and commit when an input changes.
- `assets/editorial/kitchen-counter.webp`: labeled generic generated editorial atmosphere,
  not product photography, a customer image or test evidence. Format diagrams are not to scale.

No Amazon price, availability, customer rating or review corpus is displayed. Program
Policies contain specified authorized price-display routes; this project has no feed.
Brand prices/ratings, when shown, are explicitly dated source snapshots, not Amazon offers.
Unconfirmed values remain blank and conflicts are published. The extension-cord guide
carries a dated correction for the internally contradictory Emeril manual (F97).

## Deployment and canonical scope

`.github/workflows/ci.yml` runs canonical and inherited checks **on pull requests**, including
local HTTPS browser fixtures. `.github/workflows/pages.yml` checks again on `main`, stages
public files, verifies the artifact and uploads **`_site`**, not the checkout.

```sh
python3 scripts/stage_pages.py --output _site   # requires a fresh destination
python3 scripts/verify_staged.py _site
```

Staging copies only Git-tracked public files. Runtime/private files, `.git`, dependencies
and scratch are excluded. Repository-code citations point to GitHub. Owner/research pages
are noindex; historical HTML deployment copies receive a visible archive/disclosure notice
and `noindex,follow`. This requests crawler treatment, not instant search-result removal.
Their original source files/generators are not rewritten. No robots disallow prevents a
crawler from reading the HTML noindex directive.

Independent `s2/`, `site/`, `docs/`, `research/`, `dashboard/`, `annex-88769516/` and `session-*/`
retain their own data and generators. Do not hand-edit them to match the canonical design.
Their dated claims are evidence history, not current product/account conclusions. Historical
pass reports remain in `reports/` and the coordination log.

A push is not a deployment receipt. Check Actions and live read-back; the dated verification
report records the actual PR, merge SHA and deployment result after completion.

## Operating plan and unresolved access

Review one buyer question each Tuesday from **24 November 2026**, at most one source-approved
guide. New writing is paused pending production measurement/access. Monthly query-led review
needs real Search Console data and authorized reports. This is a project plan, not proof
of a scheduler, trend, indexing, traffic, conversion or profit.

Account approval, intended products, enrolled tests, a persistent same-origin runtime,
privacy/logging approval, human-editor identity and model-photography rights remain open.
The aspirational automation platform needs authorized data/use permissions; it is not
permission for scraping, restricted-content model training or autonomous spending.

Read and update [COORDINATION.md](COORDINATION.md) before editing shared scope. Changes are
made on the current Arena branch; actions and evidence must not be recorded as owner choices.
