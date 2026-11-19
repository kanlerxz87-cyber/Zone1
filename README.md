# Zone1 Kitchen

A source-led, buyer-first kitchen publication, generated without a runtime
framework. The front page leads with formats, product questions and practical
buying guides—not an audit dashboard.

**Canonical site:** https://kanlerxz87-cyber.github.io/Zone1/
**Current implementation / source review:** [PUB-1 report](reports/verification-2026-11-19-1f9e7d52.md)
**Owner index:** [Executive summary](https://kanlerxz87-cyber.github.io/Zone1/executive-summary.html)

## Read the publication

- [Home](https://kanlerxz87-cyber.github.io/Zone1/): concise format/product cards,
  useful buying questions and a November 2026 editorial notebook.
- [Air fryers and ovens](https://kanlerxz87-cyber.github.io/Zone1/categories/kitchen-appliances.html),
  [comparison](https://kanlerxz87-cyber.github.io/Zone1/compare.html) and three
  documentation-based model guides.
- [Thermometers](https://kanlerxz87-cyber.github.io/Zone1/categories/cooking-thermometers.html):
  a buyer-facing category with a documented guide for each of the two supplied
  thermometer products — [ThermoMaven F1 Turbo](https://kanlerxz87-cyber.github.io/Zone1/products/thermomaven-f1-turbo.html)
  and [CHEF iQ Sense Gen3](https://kanlerxz87-cyber.github.io/Zone1/products/chef-iq-sense-gen3.html).
  Every fabricated-sounding figure is the manufacturer's own, cited; where the brand
  page contradicts the observed Amazon title (read time, sensor count) both readings
  are printed rather than reconciled. Intended listings remain unconfirmed.
- [Buying guides](https://kanlerxz87-cyber.github.io/Zone1/articles/), arranged in
  four reader-intent clusters. Existing canonical questions are refreshed rather
  than duplicated. [RSS](https://kanlerxz87-cyber.github.io/Zone1/feed.xml) is the
  working reader-subscription mechanism; there is no pretend email signup.
- [Our approach](https://kanlerxz87-cyber.github.io/Zone1/about.html): honest
  AI-assisted publication authorship, no invented human editor or hands-on tests,
  imagery provenance, affiliate funding and current privacy boundaries.

**Start decisions on the [Decision review queue](https://kanlerxz87-cyber.github.io/Zone1/decision-review.html)** —
fourteen forward-looking choices (priority-ordered, each with its official evidence and
options) plus a dated written brief at [`reports/suggestions-2026-11-19-d154e428.md`](reports/suggestions-2026-11-19-d154e428.md).

One native **Workspace** menu and a footer index contain the decisions, questions,
source register, flags, requirements and technical blueprint. There is no audit
sidebar on reader pages. The exact Associate disclosure sits **below the masthead,
before main content**, and repeats in the footer. Every actual outbound Amazon
product destination, including source citations, is qualified `sponsored`.

## Important boundaries

The five original submitted URL strings are preserved in
[`data/product-intent.json`](data/product-intent.json). Intended ASIN, official
listing, confirmation date/source, observed redirect/title/date, and enrolled
per-product test evidence are separate fields. The selected ID **shopnow047c-20**
is recorded but **unvalidated and unapplied**. The operational tag stays blank.
Uncertainty is not a conclusion that a short link is invalid; absence of a
visible URL parameter proves neither successful nor failed attribution.

No authorised Amazon price/rating integration is configured. This is an
implementation boundary, not a blanket claim that Amazon forbids every permitted
Amazon-served/API display route. No price tracking, fabricated social proof,
performance ranking, conversion score or revenue forecast is published.

**Production analytics is off.** The actual browser client and Python/SQLite
collector share a tested named-event contract. The four browser events are
`page_view`, `outbound_click`, `article_engagement` and `comparison_interaction`;
`affiliate_report_import` is operator-only. Tests use temporary synthetic data,
never campaign traffic. Pages cannot execute this collector. A controlled
same-origin runtime, infrastructure-log minimisation and privacy approval are
required before enabling it. See [analytics/README.md](analytics/README.md).
The authorised first-party campaign ledger remains empty.

Source review is scoped and dated. A layout refresh is not a fresh verification
of every historical value. **F96** records conflicting extension-cord instructions
inside the Emeril manual; this site does not choose the permissive instruction.
**F97** records content corrections; **F102** records the stricter direct-evidence
row gate. The [public flag register](https://kanlerxz87-cyber.github.io/Zone1/flagged.html)
links the primary sources and implementation evidence.

## Build and test

The canonical build uses only Python's standard library. Node 22 is needed for
the actual-client integration tests; browser tooling is an optional development
installation, not shipped to readers.

```sh
python3 build.py
python3 verify.py
python3 -m unittest discover -s tests -v
bash scripts/ci-check.sh
python3 research/check_research.py
python3 scripts/verify_site.py
```

The optional development-only browser suite is also a separate PR CI job:

```sh
npm ci --ignore-scripts
npx playwright install --with-deps chromium
npm run test:browser
# Optional after changing the reviewed share-card source/assets:
npm run render:social
```

It serves the committed pages locally over temporary HTTPS and uses an isolated,
explicitly synthetic collector fixture outside Git. Real primary/keyboard/middle
activations, privacy transport, opt-outs and the client/collector connection are
exercised. The reading-bucket test uses a virtual clock with controlled
focus/visibility inputs; it is not an OS-focus study or measured reading time.
All static pages are checked at 320, 390, 768 and 1440 px, with separate no-JS,
keyboard and scoped axe checks. This is not full WCAG certification or production
measurement. Development dependencies/artifacts are excluded from publication
crawls, not from any canonical or historical-build checks.

The generator reads:

- `data/products.json`, `data/articles.json`, `data/sources.json` and related
  evidence/intent/decision registers;
- `data/publication.json` for concise reader copy and the explicit operating plan;
- `publication/layout.html.tpl`, `publication/theme.css` and `publication/site.js`;
- `analytics/client.js` for the separately gated measurement asset.

It writes the canonical HTML, local style/scripts, `robots.txt`, `sitemap.xml` and
`feed.xml`. Committed generated output must be byte-reproducible. Every data table
row—including rows with a row header—needs an actual registered primary-source
URL, an exact submitted resolver, or an existing exact-file record in this
repository. A generic flag link is context, not a source. That gate verifies
coverage/link identity; scoped primary-source reading still establishes what a
document actually supports.

Source-access dates are not article publication timestamps. Unknown RSS item
publication dates are omitted; channel freshness uses a fixed real editorial
update timestamp. The optional Search Console token remains blank without real
ownership evidence. Neither sitemap submission nor rankings are assumed.

For assets, licences, responsive/no-JavaScript behaviour and editorial limits see
[publication/README.md](publication/README.md). For the current reviewable choices
see [Suggestions](https://kanlerxz87-cyber.github.io/Zone1/suggestions.html) and
[known/missing/answer/discovery questions](https://kanlerxz87-cyber.github.io/Zone1/questions.html).
Agent execution history is separate from actual owner choices.

## Historical builds and coordination

`site/`, `s2/`, `research/`, `dashboard/`, `docs/`, `annex-*` and `session-*` contain
independent earlier work. Their source generators remain read-only during this
integration. The root publication is canonical; the
[historical catalogue](https://kanlerxz87-cyber.github.io/Zone1/previous-passes.html)
explains disagreements instead of presenting multiple current shops. Their
reproducibility/audit gates still run.

Read [COORDINATION.md](COORDINATION.md) before working. It records claims,
keep-both integration incidents, exact checks, PR/merge/deployment evidence and
completion. The previous README and historical briefings remain in Git history;
the dated appendices in [EXECUTIVE-SUMMARY.md](EXECUTIVE-SUMMARY.md) are not current
account or campaign evidence.

The [parallel Z14 release report](reports/publication-2026-11-19.md) and its dated
[receipt](EXECUTIVE-SUMMARY-2026-11-19.md) remain preserved. Shared source/metadata,
bot/prerender and filter improvements were integrated; current canonical sources
are the `publication/` files, not the preserved earlier `assets/theme.css` or
`assets/app.source.js` drafts.
