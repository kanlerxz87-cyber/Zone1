# P15 — what the annex repairs leave open: the contradicting conclusion (F106)

**Date:** 2026-11-19 UTC
**Session branch:** `arena/95af246d-zone1` (based on `71fb8b1`)
**Status:** complete — one new flag, one suggestion and one question published; all gates green.

## Scope, stated up front because three other sessions touched this ground today

This pass set out to establish **one site to index** and found the same defects that three other
sessions found in parallel. Their repairs are already on `main` and are **better than this pass's
first draft**, so this pass dropped its duplicate implementation instead of re-landing it:

| Finding | Owner on `main` | What it covers |
|---|---|---|
| F103 | `arena/1970a80b-zone1` | Product anchors in the historical builds without `rel="sponsored"` |
| F104 | `arena/43667e90-zone1` | Ten inherited annex pages with no disclosure strip; `session-3740f69d/index.html` with no footer disclosure |
| F105 | `arena/b3ed16c4-zone1` | Indexation of all six annex trees, sub-directory `robots.txt`/`sitemap.xml`, absolute canonicals, enforced by `verify.py` check 4b and `scripts/add_annex_noindex.py` |

This pass's original branch independently built the F105 repair — `HISTORICAL_BUILD_DIRS`, a build
guard, generator edits and an idempotent normaliser for the three static trees. When the rebase exposed
that F105 already existed and was enforced in `verify.py` **and** addressed the sub-directory
`robots.txt`/`sitemap.xml` problem this pass had not, the duplicate was dropped. Re-landing it would
have produced two competing implementations of one boundary, which is the exact failure mode this pass
was written to remove.

**So this document reports only the finding that none of the four covers.**

## The finding — F106

**The annex repairs remove the pages from the index. They do not reconcile what the pages say.**

`dashboard/index.html` reports **"0 verified product identities"** and labels all five supplied links
**"Invalid link"**; `dashboard/products.html` repeats the badge; `dashboard/compliance.html` states that
visitors are *"never sent to unverified product pages"*. That data is dated 2026-11-13.

The conclusion rests on two counts, and both are true **about the token**:

1. Each supplied token is 9 characters, while Amazon documents ASINs as **10 characters**
   ([KDP G200652190](https://kdp.amazon.com/en_US/help/topic/G200652190), read 2026-11-19: *"add your
   10-character Amazon Standard Identification Number to the end of the URLs below"*).
2. `/dp/<token>` returns a missing-page response ([S21](https://www.amazon.com/dp/B04G1MEwY)).

Neither settles the link, and the canonical register says so explicitly: each **exact supplied URL** was
fetched and observed resolving to a stable 10-character ASIN through a `plpRedirect=mhFallback`
parameter; the intended-ASIN fields stay blank because intent is unconfirmed; and the published
position is that compliance status is **unresolved, not invalid**. Amazon's own help page supports the
weaker reading — *"it is not necessary for your unique ID to appear in order for us to track sales"*
([S41](https://affiliate-program.amazon.com/help/node/topic/GF4RJEQNXSMR7SP3), read 2026-11-19).

The project brief states the same rule the register follows: *"Do not claim that the supplied short
links are invalid; their exact compliance status is unresolved."*

**Why this is not F103, F104 or F105.** F103 is about link qualification (a `rel` token), F104 about
whether a disclosure is present, F105 about whether a crawler is asked to index the page. None of them
is about which conclusion a page asserts. A reader who follows the `previous-passes.html` link to
`dashboard/` — a link this publication deliberately keeps, because it is the evidence trail — still
meets an answer this publication rejects.

**What this pass changed, and what it deliberately did not.**

- Changed: `previous-passes.html` now names the disagreement in the same row that links the build. It
  previously described `dashboard/` as differing only over the F32 model number.
- Changed: F106 records the conflict with its official basis and both sides of the argument.
- Changed: SG-54 and Q-42 put the choice in front of the owner with the enrolled-link test named as the
  only route that produces an answer rather than a position.
- **Not** changed: the dashboard's prose. It is evidence of what that pass actually found; rewriting it
  would destroy the record, and choosing the published position is the owner's call.

## Sources read in this pass (2026-11-19)

A **scoped** re-read of the pages this pass's own claims depend on. This is not a re-verification of all
47 registered sources; historical stamps are untouched.

| # | Source | Exact observation | Verdict |
|---|--------|-------------------|---------|
| V1 | [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) | "**Updated:** October 15, 2025"; §1 Special Links must use "the special 'tagged' link formats we provide" | matches S1 |
| V2 | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | "**Updated:** April 14, 2026"; Participation Requirements §2(a) "Special Links must use the Associates ID we have assigned to you"; §2(b) "you must include your Associates ID or 'tag' … as a parameter in the URL of each link" | matches S2 |
| V3 | [Standard Commission Income Statement](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) | Table 1 read without login: "Physical Books, **Kitchen**, Automotive — **4.50%**"; "All Other Categories — 4.00%" | matches S3 |
| V4 | [Application Review Process](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) | "at least three within the first 180 days"; "at least 10 posts"; "generally within the last 60 days"; "at least 500"; "we aren't able to reassess an application once it's been rejected" | matches S4 |
| V5 | [Why doesn't my tracking ID appear in your URL…](https://affiliate-program.amazon.com/help/node/topic/GF4RJEQNXSMR7SP3) | "it is **not necessary for your unique ID to appear** in order for us to track sales made after the initial click through" | matches S41 — the basis for "a missing visible `tag=` proves neither success nor failure" |
| V6 | [KDP G200652190](https://kdp.amazon.com/en_US/help/topic/G200652190) | "add your **10-character** Amazon Standard Identification Number to the end of the URLs below" | matches the ASIN-length observation |

Every observation matched the register. **No source value changed, so no `accessed`/`reverified` stamp
was rewritten** — a stamp means the value was re-read, not that the page was opened.

## Gates

| Gate | Result |
|------|--------|
| `python3 build.py` | 58 canonical pages, 36 sitemap URLs, 24 RSS items, exit 0 |
| `python3 verify.py` | 136 pages, 77 spec rows (75 verified / 2 blank+flagged), 47 sources, **0 errors**, 0 external warnings |
| `python3 -m unittest discover -s tests` | 68 tests OK |
| `node --test tests/*.test.cjs` | 8 client-contract tests OK |
| `platform/tests` | 33 engine tests OK |
| data audit | clean |
| `scripts/build_s2_site.py --check` | current, 16 files |
| `scripts/check_links.py` | 11,345 links OK |
| `research/check_research.py` | 0 broken links, 0 unsourced rows |
| `scripts/verify_site.py` | 393 assertions, all passed |
| full rebuild (all four generators) | byte-identical, `git status` clean |

## Irregularities and remaining gates

- **F106 (new, open).** The owner must choose the published position on the five supplied links, or run
  one enrolled-link test that answers it. Until then the site publishes "unresolved" and the historical
  page publishes "invalid", with the disagreement named.
- **F103, F104 and F105 remain open on their own rows** and are not repaired by this pass. In particular,
  de-indexing does **not** make an unsponsored anchor compliant for a reader who reaches the page
  directly, and does not supply a missing disclosure.
- **Search Console remains unverified.** Not being in the index is a boundary, not a ranking. No
  ownership token, property approval, sitemap submission or query data is claimed.
- **The affiliate business is not operational.** `shopnow047c-20` stays selected, unvalidated and
  **unapplied**; intended listings are unconfirmed; the `associates_link_test_*` triple is blank on all
  five rows; the campaign ledger is empty; production analytics is **off**.
- **A browser read-back after merge** is required for deployment confirmation, because GitHub Pages only
  deploys `main`.
- **Two rebase collisions** with concurrently merged sessions occurred in this pass (F103, then F104/F105
  claimed by others). Both are recorded in `COORDINATION.md`; nothing was discarded.

## What was not done, deliberately

- No duplicate of F103/F104/F105 was re-landed after it was found on `main`.
- No historical prose was rewritten.
- No article was published to manufacture freshness: a new guide needs a sourced fact the register does
  not already carry, and none was established here.
- No stamp was refreshed on a partial read.
