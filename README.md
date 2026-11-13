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
