# Executive summary — verification pass 9 (session `42ca97ad`), 2026-11-15

**What this is.** A briefing for one reader: the person who owns the Amazon Associates
account and the three supplied links. It says what this pass verified, what it found that
the eight earlier passes had not, and what to decide next. The full evidence is on the
site; this document is the one-page version.

- **Live site:** https://kanlerxz87-cyber.github.io/Zone1/
- **Decision queue:** https://kanlerxz87-cyber.github.io/Zone1/suggestions.html
- **Questions register:** https://kanlerxz87-cyber.github.io/Zone1/questions.html
- **This pass:** session `arena/42ca97ad-zone1`, branch of `main` at `cacdb85`
- **A second pass-9 briefing exists** — [`EXECUTIVE-SUMMARY-PASS9.md`](EXECUTIVE-SUMMARY-PASS9.md), written by session `22f43836` (PR #69/#70), covering canonical/structured data and the duplicate-build problem. Both are preserved; neither supersedes the other.
- **Raw evidence:** [`session-42ca97ad/EVIDENCE-2026-11-15.md`](session-42ca97ad/EVIDENCE-2026-11-15.md)

---

## 1. The honest position in one paragraph

There is a real, working, fully sourced product site here covering three Amazon air fryer
listings. It does not invent anything: every specification is quoted from Chefman's or
Emeril's own page or owner's manual, with the source badge next to the value, and every
unresolved question is published rather than smoothed over. What the project still cannot
do — and must not fake — is state which exact manufacturer model each ASIN is, or confirm
that your Associates tag is inside the short links. Both are answerable in about ten
minutes from a signed-in browser, and neither can be answered from outside the account.

**Verdict: unchanged, and better evidenced.** This pass found nothing wrong with any
published value. What it found was that the *presentation* had a defect the verification
layer could not see, and that one piece of missing evidence was closer to hand than the
register said.

---

## 2. What this pass verified, independently

Every source below was fetched by this session on 2026-11-15. Nothing was carried over
from an earlier pass without being re-read. All 43 specification rows were checked against
the page each one cites.

| Source | What was re-read | Result |
|---|---|---|
| Amazon Program Policies (S2) | §2(b) prices/availability, §2(b) sub-tags, §6(t) reviews/ratings, §6(v) cloaking, §6(w) link shortening, §6(y) price tracking, IP License §1 and §2(e) | **All confirmed verbatim.** Page still dated *Updated: April 14, 2026*. |
| Standard Commission Income Statement (S3) | Table 1 in full | **Confirmed.** Kitchen 4.50%, All Other 4.00%, Home 3.00%. |
| Chefman 6 Qt product page (S10) | Every specification row | **All 13 rows confirmed verbatim**, including `Power: 1700W/120V` and `Model Number: RJ38-SQPF-3TDB-2W`. |
| Chefman 8 Qt product page (S12) | Every specification row | **All confirmed.** Max 400 ºF, 4 cooking presets, 200–400 °F, 1700 W, 8 Qt dimensions and weight. |
| Emeril product page (S14) | Every specification row | **All confirmed.** 26 qt / 24.6 L, 16.9″ × 15.8″ × 14.8″, 120 V, 7 accessories. |
| Chefman RJ38-SQPF-3TDB-2W manual (S18) | "two 3-quart baskets", HI-FRY 450 °F for 2 minutes, Sync Finish, no preset chart, warranty terms | **All confirmed.** |
| Chefman RJ38-SQSS-8T manual (S13) | Preset function chart | **Confirmed exactly:** Default 400 °F/15 min, Meat 375 °F/18 min, Chicken 375 °F/22 min, Fish 350 °F/10 min, Fries 400 °F/20 min. |
| Emeril FAFO-001 manual (S15) | Preset mode chart, temperature range, rated power, LED, interior light | **Confirmed.** The chart names exactly 24 presets; 75 °F (Proof) and 500 °F (Grill/Steak) bracket the range; "1700W top spiral heating element". |
| 16 CFR Part 255 (S9) | §255.5(a), §255.5(c) | **Confirmed verbatim.** eCFR current to 11/12/2026. |
| 16 CFR Part 465 | §465.1(c), §465.6 | **Confirmed verbatim.** 89 FR 68077, Aug 22, 2024. |
| The three `link.amazon` short links (S17) | Redirect target, page title, department breadcrumb | **All three reach the recorded ASINs with the recorded titles.** See §3. |

**Published values changed: none. Values found wrong: none.**

---

## 3. Two findings the earlier passes did not have

### 3.1 The browse-node path is now read on all three listings (F54)

The annex register's row F-06 said the path
`Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers`
*"was read directly on B09B7SB46R. The other two listings' breadcrumbs did not render to
this client"* — and named reading the other two as the confirmation step.

This session fetched all three supplied short links and read the identical path on
**B0CDY277D3 and B08DKYBTPH as well**. The evidence is now three-for-three.

What it still does **not** establish is the category Amazon applies when it settles a
commission: that name appears only on a shipped line in the Associates Earnings report. So
the per-product rate stays blank and both candidate rows stay on the page — but the
"working rate" is no longer a guess. Answer to **Q-15**, and the evidence behind **SG-10
path A**.

### 3.2 The prose read as machine output, and no verifier could see it (F55)

Eleven sentences in the articles spliced a published display label into a mid-sentence
position where its capital is wrong:

> "The dual-basket unit is 6 Qt / 5.67 L **as Two 3-quart baskets**."
> "The Chefman 6 Qt splits a 6 Qt / 5.67 L cavity **into Two 3-quart baskets**."

Every value involved is genuinely published and correct in a table. Eight earlier passes
checked the data and found nothing wrong — correctly. The defect only exists in the
sentence, so only reading the page the way a shopper reads it could find it.

**Fixed.** (The defect survived PR #71's full rewrite of `data/articles.json`, which re-introduced the same ten sentences and added an eleventh in a new article; it was re-found and re-fixed at the merge seam.) The article format now supports `{{value::prose form}}`, where the prose form may
differ from the published value in letter case and in nothing else — so the fix cannot
smuggle in a number. A new build guard, `check_article_splices()`, fails the build if a
capitalised value is spliced into a mid-sentence position again. Both guards were proven
to fire: the build failed on exactly these defects before the fix and passes after it.

---

## 4. The register changes

| Register | Before | After | What changed |
|---|---|---|---|
| Flags (root) | F1–F43 | **F1–F57** | F54 breadcrumb evidence · F55 the prose defect · F56 S4 not re-read this pass · F57 three orphaned files under `data/` |
| Flags (annex `data/verified/`) | 17 rows | 17 rows | F-06 rewritten with the 2026-11-15 read; `site/` regenerated; 382 assertions pass |
| Suggestions | 16 | **21** | SG-18 what the AI agent may read · SG-19 value freshness · SG-20 the product set · SG-21 moving the unconfirmed markers onto the money pages |
| Questions | 14 | **20** | Q-15 to Q-18 are **known and sourced and now carry an explicit answer**; Q-19 and Q-20 are new gaps |

**The questions register now answers what can be answered.** Four of its twenty rows state
an answer, each with the official source that settles it:

- **Q-15 — the commission rate.** Kitchen 4.50%; all three listings render the Kitchen &
  Dining path; the settlement-time category still comes from the Earnings report.
- **Q-16 — may prices and ratings be shown?** No, without Creators/PA API access.
  §2(b) and §6(t) quoted verbatim.
- **Q-17 — what is the coverage based on?** Manufacturer documentation only. Nothing was
  bought, unboxed, cooked in or photographed.
- **Q-18 — can the brief's AI agent read Amazon's data?** Not under the standard licence.
  IP License §1 and §2(e) quoted verbatim.

---

## 5. What is still open — and it is the same three things

| # | What is open | Who can close it | How long |
|---|---|---|---|
| **Q-01 / Q-02** | Which exact manufacturer model each of the three ASINs is. Chefman publishes three 6-quart dual-basket SKUs with different documented temperature ranges. | You, in a signed-in browser | ~5 minutes: open each listing, read the *Model Number* row in Product information |
| **Q-04 / SG-02** | Which Associates tag is inside the three short links, and whether it is yours. | You, in Associates Central | ~5 minutes, but the tag may not be visible even there |
| **Q-05 / Q-03** | Whether the account is approved, and whether it can hold Creators API access. | You, in Associates Central | ~5 minutes to look; the answer decides whether prices and ratings can ever be shown |

**None of the three can be answered from outside the account.** No amount of further
research will close them, which is why this pass spent its effort on the things that *can*
be checked.

---

## 6. The four decisions this pass puts in front of you

Full detail, with paths, effort, risk and a recommendation, is on the
[Suggestions page](https://kanlerxz87-cyber.github.io/Zone1/suggestions.html).

1. **SG-18 — what the AI agent in the brief is allowed to read.** *(Highest priority on
   the page.)* The IP License forbids using Amazon's Program Content to build or improve
   models and forbids aggregating or analysing it without written approval. The version of
   the brief that is lawful runs on manufacturers' own pages — which is the version this
   repository already implements. **Decide this before writing the research pipeline, not
   after.**
2. **SG-20 — the product set.** Two of the three products share a brand and a form factor,
   so the comparison cannot answer the two questions the site's own articles say are most
   common. The competing listings are named on the Amazon pages the site's own links
   already open.
3. **SG-21 — move the "we could not confirm this" markers onto the money pages.** The
   site's best differentiator is currently three clicks away from the reader who needs it.
4. **SG-19 — value freshness.** Every published value carries its read date, but nothing
   reports which values have gone stale. A brand's own review counter moved 1,302 → 1,305
   within a day.

---

## 7. The recommendation, unchanged and now better evidenced

1. **Publish this build.** It satisfies the content substance a review looks for and it is
   honest under inspection.
2. **Clear the flags that change copy first** — the 8-quart 450 °F conflict, the preset
   counts, the model mapping. Those decide what the pages may assert.
3. **Fix attribution before driving traffic** — confirm the Associates tag, create
   sub-tags.
4. **Then apply, and work the 180-day window deliberately.**
5. **Only pursue price and rating display if API access is granted.** Until then, absence
   is the compliant state.
6. **Decide SG-18 before building the automation.** It is the one decision that becomes
   expensive to reverse.

---

## 8. Irregularities and limitations of this pass

Recorded in full on the [Flagged for review page](https://kanlerxz87-cyber.github.io/Zone1/flagged.html).

| ID | What it is | Severity |
|---|---|---|
| **F54** | The commission category is evidenced three-for-three now, but the settlement-time category is still only knowable from the Earnings report. | Medium |
| **F55** | The prose defect — found, fixed, and guarded. | Low (fixed) |
| **F56** | The Application Review Process page was **not** re-read this pass. Its criteria are carried forward from earlier logged fetches and must not be restated as current fact. | Medium |
| **F57** | `data/flagged.json`, `data/commission-rates.csv` and `data/products.csv` are read by no build. The first is a stale copy of a register that *is* published. | Low |
| **F42** | Carried forward: the operator's location is stated two different ways on this domain, and neither statement came from the owner. | Medium |

**What this pass did not fetch**, listed item by item in
[`session-42ca97ad/EVIDENCE-2026-11-15.md`](session-42ca97ad/EVIDENCE-2026-11-15.md)
section 6, so that no reader mistakes silence for confirmation.
