# Verification record — pass 13, shopfront polish + decision desk

**Session:** `arena/fd9778a1-zone1` · **Date:** 2026-11-17 (UTC) · **Repo:** `kanlerxz87-cyber/Zone1`
**Branch base:** `e5fc007` → rebased onto `913d0ab` (main) before any edit.

This file is the evidence report for the pass. It is cited from `data/requirements.json`,
`data/decision-log.json`, `data/suggestions.json` and `COORDINATION.md`, which is why the
build fails if a register points here and this file does not exist.

---

## 1. Executive summary of this pass

**What was asked.** Make the site read like a shop rather than an audit; give the owner a
dedicated suggestions section for choosing a path before changes are implemented; and produce
a clear list of the questions and missing information that must be answered before a design
or traffic decision is reasonable. Plus: line-by-line verification against official sources,
no inferred values, and a live GitHub Pages deploy.

**What was done, in one line each.**

1. **Shopfront implementation** on the canonical build — front page now leads with the three
   machines; each product card and product page carries a `Best for` / `Check first` decision
   block generated from the rows already on the page; the brand's own list price appears with
   the policy reason no Amazon price does; mobile got a fluid type scale, a 44 px minimum hit
   area, a bottom-anchored comparison bar and a hint under any clipped table.
2. **Three question-shaped guides published** (24 articles now), each added to the topic
   register so the sitemap (54 URLs) and RSS feed (24 items) regenerated from data.
3. **Decision desk extended**: nine suggestions (SG-36…SG-44), a sixth path (P6), eleven
   questions (Q-27…Q-37), five design rows, three traffic tactics, two voice rules and four
   decision rows, plus the paste-ready design prompt extended with what the build now does and
   what still needs a human.
4. **Registers repaired where they were stale** and three new irregularities published on the
   flagged register rather than quietly fixed (F83, F84, F85, F86 — §4).
5. **All gates green** on the merged tree: build, verify, CI suite, research annex, site annex,
   platform audit, byte-for-byte rebuild reproducibility.

**What was deliberately not done.** No conversion, traffic, popularity or revenue figure was
added anywhere; no click counter was shipped (there is no host for one, and a browser-only
counter would publish a number that is not a count); no photography was copied or generated;
the supplied Associates tracking ID remains untested against a real click, which only the
account holder can check.

---

## 2. Line-by-line re-read of every source the new copy relies on

All four reads are live server-side fetches performed during this pass on 2026-11-17. "Match"
means the value on the official page equals the value published in `data/products.json` and on
the rendered pages, character for character where the page states it in a block.

| Source | Official page (opened above) | What was read on 2026-11-17 | Verdict |
|---|---|---|---|
| S10 | `chefman.com/products/turbofry-touch-dual-window-air-fryer` | Capacity `6 Qt / 5.67 L`; `200–450°F / 95º-235ºC`; Dimensions `13.38 in x 11.81 in x 10.63 in / 33.98 x 30 x 27 cm`; Weight `13.3 lbs / 6.03 kg`; Power `1700W/120V`; Model Number `RJ38-SQPF-3TDB-2W`; `cETL approved with a 1-year Chefman® assurance`; features `Max temp: 450ºF/ 235ºC with Hi-Fry function`, `Sync Function so both baskets finish cooking at the same time`, `Nonstick, dishwasher-safe baskets`, `Interior light`, `Dual viewing windows`, `Matte-black finish`; price block displays `$119.99` list with promotional prices alongside; brand widget `4.6`, `1310 Total Reviews` (5★ 930 · 4★ 259 · 3★ 85 · 2★ 12 · 1★ 24) | **Match** on every field, including the volatile review count (1,310, unchanged since the earlier read the same day) |
| S12 | `chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1` | `Max temp: 400ºF/ 205ºC`; `4 cooking presets`; `200–400°F / 95º-205ºC`; `Power: 1700W/120V`; `(8 Qt Model) 15.4 in x 12.6 in x 13.5 in / 39.11 x 32 x 34.29 cm`; `Weight: (8 Qt Model) 12.8 lbs / 5.8 kg`; `Model Number: RJ38-SQSS-8T`; widget `4.6`, `717 Total Reviews`; a 5 Qt variant is published on the same page | **Match**; no Hi-Fry and no 450 °F figure appears anywhere on this page — the brand-controlled half of F3 stands unchanged |
| S14 | `emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360` | Spec icons `26-Quart Capacity`, `24.6 Liters`, `16.9"D x 15.8"W x 14.8"H`, `120 volts`, `Dual-Speed Fan`, `25 Cooking Pre-sets`; product code `4-00675-02A-VN`; price `$199.99`; widget rating `2.6` from `25`; description says `10-in-1` and `26-quart extra-large capacity`; a marketing image asset is labelled `11-in-1` | **Match**; the 25-vs-24 preset conflict (F4) and the 10-in-1 / 11-in-1 counting conflict (F5) are still live on the page |
| S33 | `chefman.com/…/turbofry-touch-air-fryer-1.json` | `updated_at 2026-11-17T11:41:54-05:00`; 8 Quart variant `price 119.99`, `compare_at_price 119.99`, `sku RJ38-SQSS-8T`, `barcode 816458024518`, `weight 13.4 lb`; 5 Quart variant `price 79.99`, `compare_at_price 99.99`; body copy carries `extra-crispy meals with 98% less oil` | **Price and SKU match**; **new irregularity**: variant weight 13.4 lb vs the page's own 12.8 lbs, same day → **F84** |

Prior passes' observations of the three Amazon listing pages and of the two thermometer
listings (S16, S28, S29, S36, S37) and of the policy pages (S1, S2, S3, S5, S8, S9) were
**not** re-fetched in this pass; they are quoted from the dated records in
`data/sources.json`, and this file makes no claim that they were re-read today. The one
newly registered source, **S38** (Google Search Central, *Understanding page experience in
Google Search results*), was fetched live on 2026-11-17 and its self-assessment list is
quoted verbatim on the source row.

---

## 3. What the three new articles assert, and where each assertion comes from

The build enforces the first rule mechanically: a value spliced into an article (`{{…}}`) must
already be a published value in `data/products.json`, a prose form may only re-case it, and a
section may only cite a registered source id. An unregistered citation or an unpublished value
fails the build — which is exactly how the drafting of these three pieces was caught twice and
corrected (a re-worded "prose form" and three capitalised product names spliced mid-sentence).

| Article | Loaded with | Held back from |
|---|---|---|
| `articles/chefman-vs-emeril-air-fryer.html` | Published capacity, temperature range and ceiling, footprints, weights, door type, accessory count and preset counts, each spliced from the register; both brands' self-contradictions, cited to the pages that contain them | Any statement about evenness of cooking, noise, real preheat time, coating durability or rotisserie result — "not published by these brands", stated as such |
| `articles/ninety-eight-percent-less-oil-claim.html` | The brand's sentence quoted verbatim (`extra-crispy meals with 98% less oil…`), the register's labelled claim row, the 8 Qt temperature range, the dual-window manual's aerosol caution | Any health or diet position; any statement that the claim is true or false; extending the 6 Qt manual's caution to the 8 Qt, which has no such row |
| `articles/questions-before-buying-a-multifunction-appliance.html` | The eight questions, each answered or marked unanswerable from the same published rows; the model-number check, tied to F2/F3/F4/F70 | Ranking of any product; any price claim; any "expert recommends" framing |

No article names an author, because no author identity exists in this repository (Q-29). Each
page carries the site-level statement that the analysis is documentation-based.

---

## 4. Irregularities found by this pass and published for review

These are added to `flagged.html` with their sources. None blocks publication; each names the
decision a human has to make.

| Flag | What was found | Why it is a flag rather than a fix |
|---|---|---|
| **F83** | The topic queue (`data/topics.json`) and the design-prompt topic register (`data/design-prompt.json`) are two hand-maintained lists of the same article set. The pass-13 read found both wrong in opposite directions: A-9 was marked `not-written` for two days after its article shipped, and `articles/associates-disclosure-explained.html` had **no** row in the canonical queue at all. | The two data rows are now corrected (A-9 → published; queue row TP-24 added), but the duplication that produced them is still in the build. Decide: generate the design-prompt topic list from `data/topics.json`, or retire the duplicate. |
| **F84** | For `RJ38-SQSS-8T`, chefman.com published `Weight: (8 Qt Model) 12.8 lbs / 5.8 kg` in its specification block and `weight: 13.4` (lb) in the store variant record **on the same day**. Nothing on either document says which is the appliance and which is the package. | Averaging or choosing silently would turn a documented disagreement into an invented fact. The site publishes the specification block and states the gap. Settled by a statement from Chefman or a scale reading (Q-35). |
| **F85** | The shopfront pass lands in the canonical root build only. `s2/`, `site/`, `research/`, `docs/`, `dashboard/` and `annex-88769516/` each carry their own stylesheet and their own copy of the navigation, so a reader arriving at a parallel build still sees the pre-2026-11-17 look — and those builds' own reproducibility gates (`scripts/build_s2_site.py --check`, `scripts/verify_site.py`, `research/check_research.py`) fail if anyone hand-edits their HTML. | Hand-editing five other sessions' generated output is the one action this repository's protocol forbids. The request is logged for their generator owners; SG-41 / Q-30 is the owner-level decision that ends it. |
| **F86** | The mobile pass widened tap targets to a 44 px minimum and the stylesheet says so in a code comment. No page on this site may state that as conformance to a standard, because `verify.py`'s official-host list contains no accessibility body — a WCAG citation could not be added to a source register without editing the verifier. | The claim and the citation have to arrive in the same commit, and registering a new source host is a policy change, not a style change. Q-37 puts that decision in front of the owner instead of letting a later pass quietly add `w3.org` to the allow list. |

Carried, unchanged, still open from earlier passes: **F3** (8 Qt temperature), **F4/F5**
(Emeril preset counting), **F6/F7/F10** (short-link attribution), **F11** (cookie notice to be
updated the moment analytics exists), **F15** (fallback-parameter redirects), **F70/F71**,
**F76/F82** (tag attached and gated, attribution untested), and the two blank+flagged
specification rows (6 Qt preset count, 8 Qt basket divider). Nothing was filled by inference.

---

## 5. Gates run on the final tree

| Gate | Result |
|---|---|
| `python3 build.py` | exit 0 — 133 pages, 54 sitemap URLs, 24 feed items |
| `python3 verify.py` | 133 pages · 77 spec rows (75 verified / 2 blank+flagged) · 38 sources · 0 errors · 0 external warnings |
| `bash scripts/ci-check.sh` | 33 unit tests OK · data audit clean · annex build current (16 files) · link check OK, 0 broken |
| `python3 research/check_research.py` | OK |
| `python3 scripts/verify_site.py` | ALL CHECKS PASSED |
| `python3 platform/audit/report.py` | AUDIT PASSED |
| `node --check assets/app.js` | OK |
| rebuild twice, `git diff --exit-code` | clean — the committed HTML is what the generator produces |
| disclosure sentence present on every page; every outbound Amazon link `?tag=shopnow047c-20` + `rel="sponsored nofollow noopener"` | enforced by `check_disclosure`, `check_associate_tagging` and `check_affiliate_link_qualification` in the build, all passing |

---

## 6. How the brief's own numbered rows map onto this repository

The brief's `S-nn` rows (with `D-nn` decision links) belong to the sibling repository
`kanlerxz87-cyber/Zone4`; this repository tracks the same work in its own registers, so the
mapping is recorded here rather than inventing `S-nn` ids inside this build.

| Brief row | Status in this repository after pass 13 | Where it is published here |
|---|---|---|
| Lead with the products, not the verification process | Implemented — product rail first, metrics below the table | `index.html`, SG-36, D-13 |
| S-20 mobile-first pass: type scale, tap targets, sticky comparison bar | Implemented | CSS `shopfront pass` block, D-16, SG-38 |
| S-07 one page per question, then measure whether anyone arrives | Articles: implemented (24 live, 3 this pass). Measurement: **not** implemented — no host for an endpoint, five events defined and none sending | `articles/index.html`, `topics.html`, `measurement.html`, Q-27/Q-28 |
| S-06 "what the appliance is like to live with" | Still not adopted, and unchanged by this pass: it needs handling the product, which nobody here has done | SG-37 option B, Q-29, Q-31 |
| S-18 real product photography, never generated or copied | Still blocked on the rights decision; generated likenesses recorded as rejected in writing | SG-39, Q-31, D-22 precedent in the decision log |
| S-05 sponsored marking without breaking disclosure | Unchanged and still gated; the new front-page CTA carries it too | `check_affiliate_link_qualification` |
| Keep the disclosure above the fold on every page | Unchanged; the sticky bar additionally repeats the paid-link fact where a reader is about to act | header band in `layout()`, footer, `compliance.html` |
| Priority 4 — measure before automating optimisation | Ledger still empty by design, now with a dated implementation record for the three rows this pass was allowed to ship | `data/campaign-ledger.json`, `data/decision-log.json` |
| Priority 5 — compliance gate in the publishing workflow | Unchanged: disclosure, tag, price/rating silence and banned-phrase voice checks all run at build time | `.github/workflows/pages.yml`, `build.py` guards |
