# Zone1 — verified Amazon affiliate product intelligence

A static site and data layer for an Amazon Associates content operation, built around three
supplied affiliate links. Every factual value is traced to an official source; anything that
could not be confirmed is left blank and published on the **Flagged for review** page.

**Live site:** https://kanlerxz87-cyber.github.io/Zone1/

## What is in here

| Path | What it is |
|---|---|
| `index.html` | Dashboard — the three products, verification counts, commercial summary |
| `categories/` | Category pages (currently: kitchen appliances / air fryers) |
| `products/` | One documentation-based review per product |
| `compare.html` | Verified-only comparison matrix, gaps left visible |
| `guides/` | Buying guide |
| `data.html` | Full specification register + source register |
| `platform.html` | Automation blueprint, guardrails, KPIs, launch sequence |
| `compliance.html` | 16 program/legal requirements, quoted, each with a source link |
| `flagged.html` | Every unverified value, source conflict and irregularity |
| `executive-summary.html` | One-page briefing |
| `data/*.json` | The verified dataset the site is generated from |
| `build.py` | Static site generator (stdlib only — no dependencies) |
| `verify.py` | Build gate: broken links, missing disclosures, unsourced values |
| `COORDINATION.md` | Shared task board, claim log and verification record |

## Build

```bash
python3 build.py     # regenerate every page from data/*.json
python3 verify.py    # exit 0 = no broken links, no unsourced values, disclosure on every page
```

`build.py` refuses to emit a page if a specification row has a value but no official source,
or if any page is missing the required Amazon Associates disclosure statement.

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
link or when the data comes from Creators/PA API, and §3(t) restricts customer reviews and
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
node scripts/build.mjs                 # main site; also requires every research/ output to exist
```

Neither generator touches the other's files. The only cross-file dependency is the nav entry in
`scripts/build.mjs` and the output-existence check that keeps that nav entry from rotting.
