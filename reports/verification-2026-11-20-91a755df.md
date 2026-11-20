# R-91a755df — reader-voice and search-snippet pass

**Date:** 2026-11-20 (UTC) · **Session:** `arena/91a755df-zone1` · **Base:** `main` @ `1c7de82`
**Scope:** `build.py`, `verify.py`, `tests/test_publication.py`, `data/articles.json`,
`data/sources.json`, `data/suggestions.json`, `data/questions.json`, `data/publication.json`,
generated reader pages, `COORDINATION.md`, this report.

## What was measured before anything was changed

Baseline, re-run on the untouched tree: `python3 build.py` (63 pages / 41 sitemap URLs / 26 RSS
items) · `python3 verify.py` (141 pages, 77 spec rows — 75 verified, 2 blank and flagged — 49
sources, **0 errors**, 0 external warnings) · `bash scripts/ci-check.sh` (14 Node contract tests,
33 platform tests, data audit clean, 12,674 links).

Then a direct read of the built output, page by page:

| Finding | Count | Method |
|---|---|---|
| Canonical pages publishing a `<title>` longer than 65 characters | 27 of 63 | parse every built page, strip the 16-character brand suffix, measure |
| Canonical pages publishing a `<meta name="description">` longer than 165 characters | 11 | same parse |
| Longest `<title>` on the site | 120 characters | turkey-temperature guide |
| Longest description | 234 characters | design-prompt |

## What the official sources actually say

Read live on 2026-11-20 and registered as **S50** and **S51**:

- **S50** — [Influencing your title links in search results](https://developers.google.com/search/docs/appearance/title-link):
  a title link "is truncated in Google Search results as needed, typically to fit the device width";
  titles should be "descriptive and concise"; boilerplate titles that "vary by only a single piece of
  information" are listed among the common issues Google manages; including just the site name at the
  start or end of each `<title>` is explicitly acceptable.
- **S51** — [Control your snippets in search results](https://developers.google.com/search/docs/appearance/snippet):
  "There's no limit on how long a meta description can be, but the snippet is truncated in Google
  Search results as needed, typically to fit the device width"; each page should carry a unique
  description.

**Neither page publishes a character limit.** The 60-character title budget and 160-character
description budget are therefore stated everywhere as this publication's own convention chosen inside
that guidance — in `build.py`, in `verify.py` check 12 and in the source register — and not as a
number Google states. No ranking, click-through or indexing claim follows from the repair.

## The repair

1. `build.py`: `TITLE_BUDGET`, `DESC_BUDGET`, `seo_title()` and `fit_description()`. The brand suffix
   is appended only when the whole string fits; a page that already fills the budget keeps its own
   words instead of being cut mid-brand. `layout()` gained an optional `title_tag`; article records
   gained optional `seo_title` / `seo_description`, so the on-page headline and the search snippet can
   differ without either being truncated.
2. Eleven records patched in `data/articles.json` (eight search titles, four descriptions); nine
   page-level descriptions shortened in `build.py`; the product template now composes its description
   through `fit_description()`.
3. Reader voice, in the same pass and with no disclosure removed:
   - the product CTA note went from four sentences to two: the paid-link label, the exact
     "Affiliate link · intended listing and attribution unconfirmed." sentence and the
     match-the-model instruction are all retained, and the link to the dated observation record stays;
   - the article byline now reads "Updated 19 Nov 2026"; the "first-publication timestamp is not
     established" caveat moved into the single reading note instead of ending the byline as a run-on
     fragment. The `<time datetime>` value is unchanged.
4. `verify.py` check 12 fails the build on an over-budget `<title>`, an over-budget description, a
   duplicate `<title>`, or a missing one. **Proven to fire:** an injected 120-character title and
   235-character description on `index.html` produced exactly two `FAIL` lines; restoring the file
   returned `errors: 0`. Four tests in `SearchSnippetBudgetTests` cover the helper behaviour, the
   `title_tag` override and every built page.

## Gates after the repair

`build.py` 63 pages / 41 sitemap URLs / 26 RSS items · `verify.py` 141 pages, 77 spec rows (75
verified, 2 blank + flagged), **51 sources**, 0 errors, 0 external warnings · **79** publication tests
(75 inherited + 4 new) · 14 Node contract tests · 33 platform tests · data audit clean ·
`check_links.py` 12,678 links OK · `verify_site.py` 393 assertions · `check_research.py` OK ·
`build_s2_site.py --check` current.

## Live re-read of the supplied links (2026-11-20)

One day after the 2026-11-19 observation, three of the five resolvers were re-followed from an
ordinary fetch:

| Row | Supplied link | Observed destination | Compared with 2026-11-19 |
|---|---|---|---|
| PI-01 | `https://link.amazon/B04G1MEwY` | `https://www.amazon.com/dp/B0CDY277D3` | unchanged |
| PI-02 | `https://link.amazon/B02NbDxp3` | `https://www.amazon.com/dp/B09B7SB46R` | unchanged |
| PI-03 | `https://link.amazon/B00hJ57DV` | `https://www.amazon.com/dp/B08DKYBTPH` (450 °F title) | unchanged |

No `tag=` parameter appeared on any resolved URL. Under S41 that is a **null observation**, not
evidence that attribution failed: Amazon states a tracking ID need not appear in the URL to track a
sale. Nothing here validates or invalidates the tokens (the Zone3 FLG-003 position is unchanged),
confirms the intended listing, or moves `shopnow047c-20` from recorded → applied. PI-04 and PI-05
were not re-followed in this pass; their 2026-11-19 rows stand.

The Amazon detail pages fetched in the course of this check displayed prices and star ratings. None of
those values is published anywhere on this site, and none was written into any data file: S2 governs
what may be displayed and no authorised Program Content route is configured here.

## Irregularity recorded

**F110** — 27 over-long titles and 11 over-long descriptions, now repaired and gated. Published on
[flagged.html](../flagged.html#f110) with its two sources. Numbered F110 rather than F107 because the
open pull request `arena/0c5c10d0` has drafted F105–F109 and may merge first.

## Recorded, not decided

**SG-56** (suggestions) and **Q-44** (questions) put the remaining voice question on the review
desk: how much of the per-section sourcing apparatus should stay in the reader's line of sight. The
mechanical problems were fixed this pass; the rest is a taste decision with no reader evidence behind
it yet, so it is written as three reversible options rather than applied.

## Not claimed

No ranking, impression, click, conversion or revenue figure. No claim that a shorter snippet improves
click-through. No claim that the five supplied links are valid or invalid, or that `shopnow047c-20`
exists in the account. No claim that production analytics is running. No change to the campaign
ledger, which stays empty.

## Limits of this pass

- The 60/160 budgets are a convention, not a documented limit.
- The snippet measurements were taken from the fetched page markup; a search engine decides what it
  actually displays, and may substitute on-page text for the description.
- PI-04 and PI-05 were not re-followed.
- The `main` branch moved during the pass; the merge record in `COORDINATION.md` states the SHA that
  was actually merged.
