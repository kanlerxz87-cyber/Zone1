# Zone1 — verified Amazon affiliate product intelligence

A working affiliate site and data layer for three Amazon air fryer listings. Every
factual value is traced to an official source; anything that could not be confirmed is left
blank and published on the **Flagged for review** page. The site opens with the buying
decision and keeps the verification layer one click behind it.

**Live site:** https://kanlerxz87-cyber.github.io/Zone1/
**Start here as a buyer:** [`picks.html`](https://kanlerxz87-cyber.github.io/Zone1/picks.html) — three products, three jobs, one decision rule, and what one sale actually pays
**Start here as the owner:** [`handover.html`](https://kanlerxz87-cyber.github.io/Zone1/handover.html) — five actions, about an hour, eighteen flags closed
**Strategy:** [`decisions.html`](https://kanlerxz87-cyber.github.io/Zone1/decisions.html) — niche scorecard, traffic plan, measurement plan, kill rule
**Decision queue:** [`suggestions.html`](https://kanlerxz87-cyber.github.io/Zone1/suggestions.html) — review and choose before anything is built
**Open questions:** [`questions.html`](https://kanlerxz87-cyber.github.io/Zone1/questions.html) — what must be answered first
**Briefing:** [`EXECUTIVE-SUMMARY-PASS8.md`](EXECUTIVE-SUMMARY-PASS8.md) (pass 9 addendum at the end) · [`EXECUTIVE-SUMMARY-PASS9.md`](EXECUTIVE-SUMMARY-PASS9.md) (search plumbing and duplicate builds) · [`EXECUTIVE-SUMMARY-PASS9-42CA97AD.md`](EXECUTIVE-SUMMARY-PASS9-42CA97AD.md) (verification pass 9) · [`EXECUTIVE-SUMMARY.md`](EXECUTIVE-SUMMARY.md) §19 (design-coherence pass 12) · §20 (seasonal content pass) · §21/§22 (verification round 11 + RSS syndication passes) · §23 (marketing & decision-support pass, session arena/19d92a81)
**Today's live re-verification:** [`reports/verification-2026-11-16-19d92a81.md`](reports/verification-2026-11-16-19d92a81.md) (marketing pass: short links, S15 manual, S26, line-by-line review) · [`reports/verification-2026-11-16-8874422b.md`](reports/verification-2026-11-16-8874422b.md) (second-reader spot re-read, this session) · [`reports/verification-2026-11-16-492acddc.md`](reports/verification-2026-11-16-492acddc.md) (pass 12: policies, commission table, FTC, brand pages + WCAG audit) · [`reports/verification-round11-2026-11-16.md`](reports/verification-round11-2026-11-16.md) (round 11, session 3dfe4b45) · [`reports/verification-2026-11-16-9fccce0c.md`](reports/verification-2026-11-16-9fccce0c.md) (full pass 10) · [`reports/verification-2026-11-15.md`](reports/verification-2026-11-15.md) (pass 9)
## What is in here

| Path | What it is |
|---|---|
| `index.html` | **Buying guide landing page** — the decision, a sourced three-column spec table, computed coverage tiles, and the verification layer below the fold |
| `picks.html` | **This week's picks** — a decision rule instead of a ranking, with the commission arithmetic and the table rows it came from |
| `decisions.html` | **Decisions** — four niches scored on five criteria, six traffic channels with their prerequisites, six metrics, and a pre-committed kill rule |
| `handover.html` | **Handover** — the five things only the account holder can do, each with the time it takes and the flags it closes |
| `articles/` | **Twenty-one sourced articles (counted 2026-11-16)** — comparisons, explainers, feature and care walkthroughs, a source-forensics piece and two policy explainers. Every highlighted value in them must appear verbatim in `data/products.json` or the build fails. The set also ships as an RSS feed (`feed.xml`). |
| `categories/` | Category pages (currently: kitchen appliances / air fryers) |
| `products/` | One documentation-based review per product |
| `compare.html` | Verified-only comparison matrix, gaps left visible |
| `guides/` | Buying guide |
| `previous-passes.html` | Catalogue of every older build in this repo, where each one disagrees with this one, and which is canonical |
| `data.html` | Full specification register + source register |
| `platform.html` | Automation blueprint, guardrails, KPIs, launch sequence |
| `compliance.html` | 18 program/legal requirements, quoted, each with a source link — including the two that govern an AI-agent platform (IP License §4 Agent Terms and Participation Requirements §5) |
| `flagged.html` | Every unverified value, source conflict and irregularity |
| `suggestions.html` | **Decision queue** — 30 evidence-backed suggestions, each with alternative paths, effort, risk and a recommendation. Rows SG-27–SG-30 (session `8874422b`) add the RSS feed decision, a nav-label review, the Search Console step and the reader-capture posture. |
| `questions.html` | **Open questions** — 21 questions split into known / discoverable / not-stated / account-only. The five that an official source already settles carry their **answer** on the row; the rest say so plainly and name the step that would produce one. |
| `requirements.html` | **Every requirement in the brief, and whether this repository meets it** — 51 rows, each with a live status, the path that implements it and a source link. Added 2026-11-16 by session `ad8105b3`. |
| `executive-summary.html` | One-page briefing |
| `reverification.html` | Line-by-line re-read of every published value (2026-11-14 pass), each row with its verdict and source link |
| `session-81495d2d/EVIDENCE-2026-11-14.md` | Raw evidence behind that ledger: exact requests, exact responses, and what was not re-read |
| `data/*.json` | The verified dataset the site is generated from |
| `build.py` | Static site generator (stdlib only — no dependencies) |
| `verify.py` | Build gate: broken links, missing disclosures, unsourced values |
| `COORDINATION.md` | Shared task board, claim log and verification record |

## Verification annex — `site/`

Several agent sessions worked this repository concurrently. The canonical site above is generated by
`build.py` and served at the root URL. A second, independent build by session `1874bb64` is published
as an annex at **[`site/`](site/index.html)** — https://kanlerxz87-cyber.github.io/Zone1/site/

It exists because the two builds verify different things, and neither overwrote the other. The annex
does not modify the root site, its data or its scripts: it reads `data/verified/` and writes only
inside `site/`.

| | Root site (`build.py`) | Annex (`site/`) |
|---|---|---|
| Generator | `build.py` | `scripts/build_site.py` |
| Verifier | `verify.py` | `scripts/verify_site.py` (382 assertions) |
| Data | `data/*.json` | `data/verified/*.json` |
| Spec fields verified | 18/30 | 40/53 |
| Compliance requirements | 16 | 20 |
| Review items | 13 | 17 |
| **Commission rate** | shown as two candidate rows, per-product mapping unverified | **Kitchen fixed 4.50%**, sourced to the published Table 1 |
| Per-product model numbers | unmapped, flagged | mapped to manufacturer SKUs from the brands' own pages |

```bash
python3 scripts/build_site.py    # regenerate site/ from data/verified/
python3 scripts/verify_site.py   # 382 assertions; exit 0 = all passed
```

Both verifiers run in CI (`.github/workflows/`). Earlier sessions reported the same three candidate ASINs from cache-busted fetches of the
opaque `link.amazon` short links. **Correction (2026-11-14, F14–F16):** product identity is **not confirmed** —
the bare 9-character codes return "Page Not Found", and both the short links and the plain ASIN URLs served
Amazon's fallback-parameter form on re-check. Evidence: `reports/link-check-2026-11-14.md`. That cross-check remains useful on the
project's most consequential fact — which listing each token points to — but it is an observation of a
redirect, not a confirmed identity mapping. See `COORDINATION.md` and annex flag **F-16** for the
relationship between the two sites.

## Build

```bash
python3 build.py     # regenerate every page from data/*.json
python3 verify.py    # exit 0 = no broken links, no unsourced values, disclosure on every page
```

The presentation layer (pass 12, 2026-11-16, session 492acddc) is one coherent stylesheet
emitted from `build.py`'s `CSS` block: warm paper palette anchored to the brand green
`#245746`, serif display type, superscript-style source chips, sidebar grouped into
Shop smart / Products / Trust & evidence / Owner workspace, compact primary nav in the
topbar, deep-green footer. All 23 foreground/background pairs measure ≥ 4.5:1 (WCAG AA);
the only imagery is three hand-drawn inline SVG format glyphs. The design directives and
their live statuses are kept in [`data/design-prompt.json`](data/design-prompt.json)
(rendered on `design-prompt.html`).

`build.py` refuses to emit a page if a specification row has a value but no official source, if a
fourth guard fires — the **banned-phrase** check that fails the build when editorial copy drifts
back to stock marketing language ("in today's fast-paced world", "elevate your", "game-changer")
or claims first-hand experience—, or if the commission arithmetic in `data/decision.json` no longer
matches the official rate table. It also refuses
if any page is missing the required Amazon Associates disclosure statement, or if an article states
a number that is not a value published in `data/products.json`, or cites a source id that is not in
`data/sources.json`. The article guard rejected 18 paraphrased values while the article set was being
written, which is the point of having it.

## The verification rule

A value is published only if an **official** source states it:

- Amazon.com for Amazon program facts and for which ASIN a short link resolves to
- A US government source (FTC, eCFR) for US law
- The manufacturer for product specifications — its own product page or its own owner's manual

Retailer listings, reseller marketplaces, review aggregators and affiliate blogs are **not**
sources. Several of them contradicted each other, and the official rate table, on the day of
verification.

Values that fail the rule are stored as `null` with a written reason, render as
"— not confirmed —", and are listed on `flagged.html`. Nothing is inferred.

## Compliance notes

No Amazon price, availability, star rating or customer review appears anywhere on the site.
Amazon's Program Policies §2(b) permit price/availability display only when Amazon serves the
link or when the data comes from Creators/PA API, and §6(t) restricts customer reviews and
star ratings to API-served content. The IP License §2(e) additionally forbids aggregating,
analysing or repurposing Program Content, and forbids using it to train models.

The disclosure statement required by Operating Agreement §5 — *"As an Amazon Associate I earn
from qualifying purchases."* — is generated into every page by `build.py`.

See `compliance.html` for all 16 requirements with quoted source text.

## Deploy

GitHub Pages, branch `main`, root directory. The workflow at
`.github/workflows/pages.yml` rebuilds the site, runs `verify.py`, and fails the deploy if
verification fails.

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
node scripts/build.mjs --check         # validator for the retired docs/ build — currently FAILS
                                       # against the shared data schema (see flag F23); no CI workflow uses it
```

Neither generator touches the other's files. The only cross-file dependency is the nav entry in
`scripts/build.mjs` and the output-existence check that keeps that nav entry from rotting.


---

## Third build — `session-3740f69d/`

An independent build by session `arena-3740f69d`, published at
**[`session-3740f69d/index.html`](session-3740f69d/index.html)** (URL path `/session-3740f69d/`). It contributes a
dashboard-style site with subpages by category (Products, Analysis, Niches, Content, Links, Tracking, Platform,
Compliance, Flagged, Sources), a marketing-content set (buying guide + comparison + per-product copy), and its own
machine-readable registry in `session-3740f69d/data/`. Like the other builds, every table row carries an official
source link or a policy-cited blank. Independent highlights: cache-busted double resolution of the three short links;
the 2026 IP License §4 **Agent Terms** analysis for AI automation; link-policy mapping (§6(v)(w)) for the supplied
`link.amazon` links; verified Commission Table 1 candidates (Kitchen 4.50% / All Other 4.00%) with the per-product
mapping left flagged. Full record: `COORDINATION.md` → *Integration pass 3*.


---

## Fifth pass — independent re-verification, 2026-11-14 (`sess-81495d2d`)

Every value the root site publishes was re-read against the official source the site cites for it — the
manufacturer's own product page, its own owner's manual PDF, Amazon Associates Central, and the eCFR — and the
result is published as a ledger: **`reverification.html`** (61 rows: claim, value as published, what the source said
on the day, verdict, source link). Raw evidence and the two control requests are in
`session-81495d2d/EVIDENCE-2026-11-14.md`.

What the pass changed:

* **The link-resolution dispute is closed on the evidence.** Four sessions over two days, each with a fresh Amazon
  session id, obtained the same three ASINs (`B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`), and a nonsense-token control
  returns **403** instead of a shuffled product. The "resolves to a different featured item on each request" clause
  raised by an earlier pass is retired. What remains open is narrower and is still flagged: the tokens are not ASINs
  (9 characters), every landing URL carries `plpRedirect=mhFallback`, and the Associates tag inside the link cannot
  be observed from outside Associates Central.
* **Two blank rows are now filled.** The Chefman 8 Qt `Wattage` and `Dimensions / weight` rows were blank with the
  reason "not stated on the brand product page". The manufacturer's own Specifications block states
  `Power: 1700W/120V`, `(8 Qt Model) 15.4 in x 12.6 in x 13.5 in` and `(8 Qt Model) 12.8 lbs / 5.8 kg`, so both rows
  now carry values sourced to that page (verified spec rows: 40 → 42 of 43).
* **Volatile figures are stamped.** Brand-hosted review counts moved in 24 hours (1,302 → 1,305 and 715 → 716)
  while the averages held at 4.6. New flag F14 records why every rating on this site must carry its read date.
* **The conflicts are still conflicts.** Chefman 8 Qt: Amazon title says "450°F Hi-Fry … Bake, Dehydrate, Frozen",
  brand page says "Max temp: 400ºF/ 205ºC / 200–400°F". Emeril 26QT: **10-in-1**, **11-in-1** (a carousel asset's own
  filename), **24 cooking functions** (Amazon title) and **25 Cooking Pre-sets** (brand spec block) all appear on
  official pages on the same day. The site asserts none of them.
* **Stale build artefacts corrected:** root navigation now reaches all six published builds (it previously exposed
  three); the executive summary's hand-typed "12 sources / 9 flags" and its hand-typed commission table are computed
  from `data/*.json`; the Flagged page's "this build is the first verification pass" line is replaced by a real
  resolved-items table.

```bash
python3 build.py                 # regenerate every page, including reverification.html
python3 verify.py                # 0 errors = no broken link, no unsourced value, disclosure everywhere
```


---

## Pass 7 — 2026-11-14 (`arena/6b2eddeb`)

An independent pass that re-fetched its own sources rather than trusting the recorded ones. Raw
evidence: [`session-6b2eddeb/EVIDENCE-2026-11-14.md`](session-6b2eddeb/EVIDENCE-2026-11-14.md).

**No published value was found to be wrong.** All three supplied short links resolved to the same
three ASINs with titles matching the stored strings character for character; the Associates Program
Policies section map, the full Standard Commission Income Statement and all three manufacturer
product pages were re-read live and matched the dataset.

Four new findings, all published on [`flagged.html`](flagged.html):

* **F32 — Chefman publishes three 6-quart dual-basket SKUs, not two.** `RJ38-3DBW-V2` (90–400 °F,
  five functions), `RJ38-SQPF-3TDB-2` and `RJ38-SQPF-3TDB-2W` (200–450 °F, Hi-Fry). The root site
  maps the 6 Qt ASIN to `-2W` on the `Hi-Fry` wording; two other builds in this repo map the same
  ASIN to `RJ38-3DBW-V2` with no caveat.
* **F33 — the 8 Qt "450 °F conflict" is probably two different SKUs.** Chefman's `RJ38-8T-BLACK`
  documents 450 °F Hi-Fry and exactly the four functions named in the Amazon listing title, while
  the currently mapped `RJ38-SQSS-8T` documents 200–400 °F. This narrows flag F3 sharply without
  resolving it.
* **F34** — the older `EXECUTIVE_SUMMARY.md` still asserts two things this pass disproved.
* **F35** — nine published sites for the same three products disagree. The sidebar was reduced from
  six parallel-build entries to one; `previous-passes.html` now catalogues every build and names
  each divergence.

The highest-value action for the account holder is unchanged and now more specific: open the three
listings, read the model number in each one's product-information block, and settle F32 and F33.

---

## Pass 10 — 2026-11-16 (`arena/9fccce0c-zone1`)

A tenth independent re-read of the same source register, run because the register is made of
values that move and because the last several passes each found something. It found three
things, and all three are fixed:

* **The clauses that govern the brief were missing from the canonical register.** The Program
  Policies page carries **IP License §4 ("Agents" / the Agent Terms)** and **Participation
  Requirements §5** — written for exactly the case this project is, an AI-powered affiliate
  platform that automates research. Read verbatim on 2026-11-16 and now published as compliance
  requirements **C17** and **C18** and platform guardrail **G11**. The scope question they raise
  (does an ordinary public listing page count as Program Content, and what must the agent call
  itself?) is published as **Q-21** and **SG-22** rather than answered by inference, and the
  limit of what could be read is published as **F62**. The two defects are published as
  **F61** and **F62**.
* **Three published pages pointed at a flag that exists in no register.** `data/questions.json`,
  `data/suggestions.json` and `data/sources.json` all sent readers to "flag F46"; there is no
  F46 in either register in this repository. The pointers now name **F56**, and a new build guard
  (`check_register_cross_references()`) fails the build if any generated page cites a flag,
  source, question or suggestion id that does not exist. The guard was proven to fire on an
  injected violation.
* **The carried-forward Application Review figures are now read from the source**, which closes
  **F56** and gives **Q-19** its answer, and the two volatile Chefman review counters had moved
  again (1,307 and 717) and were refreshed with all three read dates kept.

Two independent sessions verified sources on 2026-11-16 and both records are kept:
`reports/verification-2026-11-16.md` (session `c334fb1c`, the three short links, the policy
date and the live landing page) and `reports/verification-2026-11-16-9fccce0c.md` (this
session, the full register). Neither replaces the other; the site publishes both ledgers.

No published value was found wrong. Full evidence, row by row: **[`reports/verification-2026-11-16-9fccce0c.md`](reports/verification-2026-11-16-9fccce0c.md)**;
the same ledger rendered on the site at
[`reverification.html`](https://kanlerxz87-cyber.github.io/Zone1/reverification.html).

## Pass 12 (session `arena/8874422b-zone1`) — RSS syndication, article masthead, second-reader re-read (2026-11-16)

This session claimed the marketing-design polish pass; while it worked, the design-coherence pass
(session `492acddc`, §19 of the executive summary), the seasonal content pass (session
`a746a9f2`, §20), verification round 11 (session `b23f12f0`) and the pass-11 decision closure
(session `ba29c641`) merged their own reader strip, single-era stylesheet, nineteen-article set
and direct reads of all three listings' Product information blocks.
Rather than ship two competing design systems, this branch **rebased onto their result, adopted it
as the canonical design, and contributed the additive pieces the merged tree still lacked** — no
published value, register row or wording changed anywhere:

* **RSS feed.** `feed.xml` (19 items) is generated deterministically from `data/articles.json`
  (pubDate derives from the register's own accessed date, so the reproducibility gate holds) and
  linked from every page head, the articles index and the footer. Shipped as **SG-28**; the
  owner-only Search Console step is **SG-29**; the keep-the-no-cookie-posture decision is
  **SG-30**; a review of the shipped shopper-strip labels is **SG-27**.
* **Article masthead.** Articles open with a kicker/headline/standfirst block and a meta row
  (kind · reading time · sources-read date · "documentation-based — no hands-on testing" badge),
  styled in the shipped stylesheet's own vocabulary.
* **Footer brand column** naming the publisher and the feed; `theme-color` meta.
* **Second-reader spot re-read.** The three `link.amazon` short links (same three `/dp/`
  destinations through the same fallback-style redirects), both Chefman counters (1,307 / 717 —
  unchanged), the Emeril preset conflict (re-confirmed live on one page) and the Program Policies
  stamp (April 14, 2026 — unchanged). Evidence:
  **[`reports/verification-2026-11-16-8874422b.md`](reports/verification-2026-11-16-8874422b.md)**;
  ledger rendered at
  [`reverification.html`](https://kanlerxz87-cyber.github.io/Zone1/reverification.html).
  F1/F2/F3, F4/F5 and F46 stand as published.

Gates on the final rebased tree: `build.py` exit 0 (48 pages, 47 sitemap URLs + feed.xml, 19
items) · `verify.py` 127 pages, 77 spec rows (75 verified / 2 blank+flagged), 0 errors ·
`ci-check.sh` green (8,287 links / 0 broken) · `verify_site.py` 393 assertions PASSED ·
research checks OK · platform audit PASSED · two consecutive builds byte-identical.
