# Zone1 Kitchen

A documentation-based, AI-assisted kitchen buying publication, with its evidence and owner
workspace kept accessible rather than placed in front of the reader.

**Canonical site:** <https://kanlerxz87-cyber.github.io/Zone1/>
**Current brief:** [19 November 2026](EXECUTIVE-SUMMARY-2026-11-19.md)
**Source, test and release record:** [publication review](reports/publication-2026-11-19.md)

## What is implemented

- Reader-led home with a sourced three-format shelf, progressively enhanced filters, comparison,
  category/product/buying guides, 24 existing question-led articles, four topic clusters and RSS.
- A shared cream/forest theme, local OFL-licensed fonts and honest editorial-method page. Generic
  AI food/preparation scenes are labelled illustrations, not product photography, tested recipes
  or hands-on experience. Product-photo permissions remain unresolved.
- Associate statement **under the masthead**, repeated in the footer. All outbound product
  anchors, including listing citations, carry `sponsored nofollow noopener`.
- One native keyboard-operable Workspace group plus the comprehensive dashboard/evidence footer.
  Suggestions show current implementation state separately from alternatives, recommendations,
  questions, missing facts and discovery steps. No owner answer is invented.
- A corrected five-event analytics contract and self-hosted Python daily-aggregate collector,
  with browser/HTTP/storage/import tests. **Production collection is disabled.** Static GitHub
  Pages cannot run that endpoint; see [analytics deployment gates](analytics/README.md).

No conversions, traffic trends, earnings, search rankings or measured conversion improvements
are claimed. Tests do not establish semantic source truth, legal compliance or accessibility
conformance. The article review corrected substantive errors that earlier source-presence tests
had missed; the evidence is in the dated report and canonical Flagged rows F96–F99.

## Links, account facts and reports

The five supplied `link.amazon` strings remain exactly as submitted. Observed destinations are
not intended-product confirmations. Their validity/compliance is **not declared either way**;
the unresolved external record is
<https://kanlerxz87-cyber.github.io/Zone3/flagged.html#FLG-003>.

`shopnow047c-20` is the selected user-provided tracking ID, not an account-verified active ID.
`data/config.json` leaves the applied tag blank. The intended ASIN, official listing URL,
confirmation date/source and enrolled-link result for each row remain unfilled in
[`data/product-intent.json`](data/product-intent.json). A final URL without a visible ID proves
neither successful nor failed attribution.

The seven-column [`data/campaign-ledger.json`](data/campaign-ledger.json) is empty. Populate it
only from authorised timestamped first-party aggregates with source/channel provenance.
Browser clicks and engagement never become Amazon orders by inference. No synthetic check
opens an Amazon link or generates an account click.

## Build and check

The publication and collector use the Python standard library; the static site needs no
runtime Node, package install, database or third-party service.

```sh
python3 build.py
python3 verify.py
python3 -m unittest discover -s tests -v
node --test tests/*.test.cjs
bash scripts/ci-check.sh

# Independent sections — preserve both their data and committed output
python3 scripts/build_site.py
python3 scripts/verify_site.py
python3 research/build_research.py
python3 research/check_research.py
```

A second root build must be byte-identical. CI rebuilds the canonical output and independent
sections, tests the actual analytics contract and rejects stale output before merging.
GitHub Pages deployment and actual live readback are separate evidence, recorded in the report.

The browser check uses disposable development dependencies (not shipped with the site):

```sh
npm install --prefix .cache/browser --no-save --no-package-lock \
  playwright-core@1.65.1 @sparticuz/chromium@153.0.0
node scripts/check_publication_browser.mjs
```

It serves a temporary strict `/Zone1/` fixture, tests desktop/mobile/keyboard/no-JS behaviour,
blocks external network requests and never activates an Amazon product link. Optional screenshots
are written under `.cache/`, which is ignored. They are not source data or a test result about a
product. See the script for the exact tested scope.

## Maintained sources and outputs

| Source | Purpose | Generated output |
|---|---|---|
| `build.py`, `data/*.json` | Canonical templates, registers and build guards | Root HTML and `products/`, `categories/`, `guides/`, `articles/`; sitemap/RSS |
| `assets/theme.css` | Responsive publication theme | `assets/style.css`, emitted verbatim |
| `assets/app.source.js` | Progressive UI, local-only owner picker | `assets/app.js`, emitted verbatim |
| `analytics/client.js` | Gated four-event browser emitter | `assets/analytics.js`, emitted verbatim, **not loaded while disabled** |
| `analytics/collector.py` | Same-origin aggregate collector | Separate server runtime; not a Pages function |
| `analytics/report_import.py` | Validated/idempotent operator report import | Authorised ledger rows only; no fake fixture data in the real ledger |
| `assets/editorial/README.md`, `assets/fonts/*LICENSE*` | Image-use record and local font licences | Visible image labels; no copied product photo |
| `COORDINATION.md` | Claimed scopes, checkpoints, merge/deploy receipts | Human-readable coordination record |

Article `modified_at` records an actual editorial edit; `source_checks` names selected documents
read on that date. Unknown first-publication timestamps remain null, with optional RSS/Article
publication fields omitted. A rebuild never advances a date, and a source-read date is not
substituted for a publication timestamp.

## Preserved independent builds

The canonical root is not a claim that every historical annex agrees with it. `site/`, `s2/`,
`research/`, `docs/`, `dashboard/`, `annex-88769516/` and session evidence have their own generators,
data and historical conclusions. They were not silently restyled or deleted. Their relationship,
known conflicts and indexability questions are described on [Previous passes](previous-passes.html)
and in the dated report. Never use an annex's identity assertion to fill the canonical intent blanks.

Earlier README prose, fixed counts and older executive summaries describe previous revisions,
not the current state. Their Git history and dated reports remain available; this current README
supersedes their present-tense deployment, styling, privacy and measurement descriptions.
