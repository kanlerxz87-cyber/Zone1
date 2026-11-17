# Independent verification & decision-support pass — 2026-11-17 (session arena/0cf55ef3-zone1)

Task **X-0cf55ef3** on the COORDINATION board. Scope: line-by-line review of the committed
tree, live re-verification of the five supplied `link.amazon` short links and the load-bearing
official sources, a defect hunt over the newest merged work (TP-21 / PR #135 shop pass), and a
review of the suggestions register and decision gate against the standing brief.

Declared read-only for this pass: `data/topics.json` and `EXECUTIVE-SUMMARY-SHOP-PASS.md`
(owned by the C55 session). No row of either was edited.

Verdict vocabulary: **confirmed** (the live page states the published value), **matches**
(the live page states the same thing in different words), **not re-read** (this pass did not
fetch it and therefore restates nothing about it).

---

## A. The five supplied short links — re-opened live, 2026-11-17

Every row was read from the live response body in this session. None is carried forward from
an earlier pass's notes.

| # | Requested URL | Resolved to | Page title (as served) | Register row | Verdict |
|---|---|---|---|---|---|
| 1 | `https://link.amazon/B04G1MEwY` | `amazon.com/dp/B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry… | S17 | **matches** — destination unchanged |
| 2 | `https://link.amazon/B02NbDxp3` | `amazon.com/dp/B09B7SB46R` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven… | S28 | **matches** — destination unchanged |
| 3 | `https://link.amazon/B00hJ57DV` | `amazon.com/dp/B08DKYBTPH` | Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 … Stainless Steel | S29 | **matches** — destination unchanged |
| 4 | `https://link.amazon/B0c8moW59` | `amazon.com/dp/B0DHZTCNR5` | ThermoMaven 1 Sec Professional Digital Meat Thermometer … Black | S36 | **matches** — destination unchanged |
| 5 | `https://link.amazon/B0f3GKalj` | `amazon.com/dp/B0DZFD6R9Z` | CHEF iQ Sense \| Smart Wireless Meat Thermometer … Gen3 | S37 | **matches** — destination unchanged |

**What this does and does not establish.** All five tokens still resolve to the same five
destination ASINs the register records, so no link has been re-pointed or retired. All five
still land through Amazon's own fallback-style parameters (`lv=shuf`, `plpRedirect=mhFallback`)
with **no visible `tag=` parameter**. That keeps **F6 / F82** (attribution not observable from
outside Associates Central) and **Q-04** open exactly as recorded — they are not restated as
resolved here, and this pass adds no new conclusion about the account holder's intent behind
the links (**F77**).

---

## B. Official sources re-read live

| Source | Published fact it bears on | What the live page says today | Verdict |
|---|---|---|---|
| S1 Operating Agreement | Disclosure wording and programme obligations | "Updated: October 15, 2025" | **confirmed** |
| S2 Program Policies | The no-price / no-rating rule the site enforces | "Updated: April 14, 2026" | **confirmed** |
| S3 Standard Commission Income Statement | Table 1 rates and bounty amounts | Kitchen 4.50%, All Other 4.00%; bounties $12.00 / $5.00 / $0.25 | **confirmed** |
| S4 Application Review criteria | Qualification thresholds (Q-03, SG-11) | 3 qualifying sales / 180 days, ~10 posts, 500+ followers | **confirmed** |
| S8 FTC Disclosures 101 | "Hard to miss", the tried-it rule | Dated November 2019; both phrases present | **confirmed** |
| S9 eCFR 16 CFR Part 255 | The endorsement-guide text the compliance rows cite | "up to date as of 11/13/2026"; last amended 10/30/2026 (88 FR 48102) | **confirmed**, with the one-day stamp roll noted below |
| S10 Chefman 6 Qt product page | 450 °F Hi-Fry, Sync Finish, review line | RJ38-SQPF-3TDB-2W, 450 °F Hi-Fry, Sync Finish, 1310 Reviews | **confirmed** |
| S12 Chefman 8 Qt product page | The 200–400 °F disagreement behind F3 | RJ38-SQSS-8T, 200–400 °F, 717 Reviews | **confirmed** |
| S14 Emeril product page | The 25/24/10-in-1 conflict behind F4/F5 | "25 Cooking Pre-sets" icon, $199.99, 2.6 (25 reviews), 10-in-1 | **confirmed** — the conflict is still live on the vendor's own page, so F4/F5 correctly stay open |

**The one benign delta.** The register carries S9's eCFR stamp as `11/12/2026`; the live page
now renders `up to date as of 11/13/2026`. eCFR re-stamps that line daily, the last-amended
date and the source note are unchanged, and no substantive regulatory text moved. Recorded in
`data/sources.json` under `reverified_2026_11_17_0cf55ef3` rather than "repaired", because
rewriting it would produce a claim that goes stale again tomorrow.

**Read and excluded, not published.** Prices, star ratings, review counts and rank values
appeared in the live responses. None was published. Review counts are cited only inside the
source register as date-stamped vendor-page readings; the no-price/no-rating rule (S2 §2(b),
§6(t)) continues to hold on every reader-facing page.

**Not re-read by this pass:** S5, S6, S7, S11, S13, S15, S16, S18–S27, S30–S35, and the two
owner's-manual PDFs. Nothing about them is restated as current here; their standing records
carry their own dates.

---

## C. Defects found and repaired

All four are the same class the register already names (**F52/F63**): *a number or an id
written as a snapshot and then read as a live fact.* Each was verified against the data before
being changed, and each repair is at the source of truth, not in the generated HTML.

### C1. Handover table pointed the owner at flag ids the Flagged page does not render

`data/decision.json` → `handover.items` listed the flags each owner action closes as
`F01`, `F02`, `F03`, `F06`, `F07`. Those ids exist in `data/flags.json` (the older annex
register, which runs `F01–F27`), so `check_register_cross_references()` accepted them — but the
page that prints them is `handover.html` / `decisions.html`, whose reader-facing counterpart is
`flagged.html`, and that page renders the **canonical** register (`F1`, `F6`, …). A reader who
followed "F01" landed on an unrelated row or on nothing.

`data/flags.json` F01–F07 and the canonical rows say different things:

| Legacy id | Legacy row says | Canonical row with that number says |
|---|---|---|
| F01 | price/rating/review/availability blank | F1 = ASIN → manufacturer model number |
| F02 | commission rates blank | F2 = two near-identical Chefman SKUs |
| F03 | supplied links carry no Associates tag | F3 = 450 °F spec conflict |
| F06 | Associates statement cannot show as active | F6 = Associates tag not observable (matches) |
| F07 | canonical page for product 3 returned an interstitial | F7 = §6(w) link-shortening rule |

**Repair.** `closes` now names rows that exist where the reader is sent, chosen by subject:

- H1 (read the model number off each listing) → `F1`, `F32`, `F33`
- H2 (read the tracking ID, rebuild the links) → `F6`, `F82`
- H3 (account status) → `Q-03`, labelled as a question, not a flag
- H4 (domain / measurement) → `M1-M4 (measurement rows…)`, labelled as such
- H5 (the decision layer) → `the owner decision log (owner-facing, not a flag)`

Both renderers (`page_decisions._closes`, `page_handover`) now emit a link only when the entry
matches `F\d{1,2}`, and plain text otherwise, so a non-flag can never again be dressed as one.

### C2. The handover's headline count was typed, not computed

`handover.html` said **"Five actions, about an hour, eighteen flags"**; the homepage repeated
"closes eighteen flags" twice. The register holds five items, and the three that close flags
close five flag rows between them. The number 18 matched neither.

**Repair.** The heading now reads "a handful of flags", and the homepage card and callout read
"three of the five actions close five flag rows between them" / "five flag rows closed".
`data/decision.json`'s `handover.summary` was rewritten to the same five-row statement.

### C3. The homepage article count was stale

`build.py` printed **"Eight reads written for this product set"** directly above a card grid
rendering `data/articles.json`, which now holds **21** articles. It is the fourth occurrence of
the class F63 records.

**Repair.** The sentence is now `{len(ARTICLES["articles"])} reads written for this product
set` — computed at build time, so it cannot drift again.

### C4. Two requirements rows typed counts that had already moved

`data/requirements.json`:

- **B-08** said "Twelve articles are published and three more are specified but unwritten";
  the site publishes 21 articles and 4 topics are specified-but-unwritten.
- **A-04** said "Twenty questions"; `questions.html` renders 26.

**Repair.** Both now use the register's existing computed-count tokens — `{n_articles}`,
`{n_questions}` — and a new token `{n_topics_minus_articles}` was added to `req_counts()`,
computed as `len(topics) − published`. An unknown token still fails the build
(`req_interp`), and this pass confirmed the page renders "21 articles" and "26 questions".

### C5. New build guard, and proof that it fires

The existing guard could not catch C1 because it deliberately accepts legacy ids (F47
documents that two registers exist). This pass added **`check_legacy_flag_pointers(pages)`**:
a zero-padded `F0N` id is allowed only where the surrounding sentence names the legacy
register (`data/flags.json`, "legacy", "annex register"); anywhere else — which is every bare
reader pointer — the build fails.

**Proven non-vacuous.** Injecting `<p>closes F01 today</p>` into `handover.html` produced:

```
BUILD FAILED — a page points a reader at a legacy-register flag id that the Flagged page
does not render:
  handover.html: bare legacy flag id F01 with no reference to the legacy register in the
  surrounding sentence (near: ...Five actions, about an hour, a handful of flags closes ...)
```

and the tree was restored and rebuilt clean afterwards.

---

## D. TP-21 and the shop pass (read-only scope)

**TP-21** ("Questions to ask before buying a multi-function kitchen appliance", PR #135) was
reviewed line by line against its record in `data/topics.json`:

- `status: "proposed"`, `published_as: null` — correct; nothing links a reader to a page that
  does not exist.
- `must_cite` holds three manufacturer URLs (Chefman 6 Qt, Chefman 8 Qt, Emeril), all three of
  which this pass re-read live in section B.
- The demand line is labelled judgement on the page, matching the page-level note that "demand
  is argued, not measured".
- **No change made** — the record is sound as committed.

One presentation defect was found in the shared plan table, not in TP-21's data: the table
truncated each row's citation list to two links with no indication that more were required, so
**TP-21's row showed 2 of its 3 must-cite sources**. Seven topic rows were affected
(TP-02, TP-03, TP-04, TP-15, TP-16, TP-17, TP-21). **Repaired** in `build.py`: when the brief
requires more than two, the row appends `+N more in the brief ↓` linking to its own detail
card, which lists every source. Verified rendering on all seven rows.

Also re-checked on the live Pages host (cache-busted): the deployed landing page is current
with `main`, the Associates disclosure sits above the fold, the "Before shopping" banner is
present, and the tiles read 3 products / 21 articles / 37 sources / 82 flags / 0 hands-on
tests.

---

## E. Decision-support review (suggestions register, questions, decision gate)

The brief asks for a reviewable list of suggestions with the paths a reviewer can choose
between, plus the questions that must be answered before a decision is reasonable.

- **`data/suggestions.json`** — 34 suggestions (SG-01…SG-35, no SG-31), grouped into five
  ordered paths (P1 "safe to publish", P2 "read like a shop", P3 "findable", P4 "machinery
  trustworthy", P5 "read like a publication"). Each path carries effort, prerequisites,
  what it delivers, what it does not fix, and a "pick this if" line. This satisfies the
  "review suggestions before implementing" brief; the queue is owner-facing and versioned.
- **`data/questions.json`** — 26 questions, each recording what is known, what is missing,
  and the step that would discover it. `requirements.html` now states that count correctly.
- **`data/flagged.json`** — 13 open rows, all published on Flagged for review. None blocks a
  merge, per the standing rule.
- **`decision-gate.html`** — renders a **frozen** 14-question parallel register, and its lede
  says 14 because that register holds 14. A prior pass scanned it and cleared it as internally
  consistent (F63's record). Re-checked here: still internally consistent, **no change**.
  The live register (26 questions) is `questions.html`; the two are deliberately different
  artefacts and the gate page does not claim to be current.
- **Seasonal / trend coverage** — SG-24 (ship seasonal content while the season is live) plus
  published TP-15 (gift guide) and TP-17 (Black Friday model-number check) already cover the
  brief's "catchy, trendy" request without inventing demand numbers. Nothing added, because a
  second seasonal row would duplicate SG-24 rather than open a new decision.

---

## F. Gates run after the repairs

| Gate | Result |
|---|---|
| `python3 build.py` | exit 0 — 52 pages, sitemap 51 URLs, feed 21 items, flag register 84 rows |
| `python3 research/build_research.py` + `check_research.py` | exit 0 — 393 assertions, ALL CHECKS PASSED |
| `python3 verify.py` | exit 0 — 130 pages, 77 spec rows (75 verified / 2 blank+flagged), 37 sources, 0 external warnings, 0 errors |
| `python3 scripts/build_site.py` + `verify_site.py` | exit 0 — no broken links, disclosures present |
| `python3 platform/audit/report.py` | exit 0 — AUDIT PASSED, 0 warnings |
| `bash scripts/ci-check.sh` | exit 0 — 33 unit tests OK, data audit clean, 8,788 links / 0 broken |
| Reproducibility | clean rebuild leaves only the intended edits; no generated drift |

---

## G. Irregularities flagged for the owner (not blocking)

These are recorded on the Flagged for review page and are **not** repaired here, because each
needs something this sandbox does not have.

| Ref | What is unresolved | Why it cannot be closed here |
|---|---|---|
| F6, F82, Q-04 | Whether the five supplied links carry the `associates` tag; none shows `tag=` | Requires Associates Central login |
| F1, F32, F33, F77 | Whether each destination ASIN is the product the owner intended to market | Requires the owner's intent, i.e. the one-link test |
| F4, F5, F45 | Emeril 25 vs 24 presets and 6 vs 7 accessories | Live vendor page still contradicts itself; the listing says six, the manual seven |
| F3, F33 | 450 °F on the 8 Qt listing vs 200–400 °F on the brand page | Both pages are official and still disagree |
| F15, F41 | Plain ASIN URLs answered with Amazon's fallback form | Server-side behaviour, not a repo fact |
| Q-03, SG-11 | Whether the account is past the 180-day qualifying-sale threshold | Owner's account dashboard |
| SG-16, Q-07 | Domain decision before SEO investment | Owner decision |
| SG-29 | Search Console / Bing Webmaster registration | Owner's verified property |
| SG-23, F46, Q-22 | Product photography rights | No rights-cleared source exists |
| SG-08 | Self-hosted analytics endpoint | Pages is static-only |

---

## H. Files changed by this pass

- `build.py` — computed article count; `+N more` citation indicator; `{n_topics_minus_articles}`
  token; handover/decisions `closes` renderers; `check_legacy_flag_pointers()` + wiring.
- `data/decision.json` — `handover.items[*].closes` re-pointed; `handover.summary` rewritten.
- `data/requirements.json` — B-08 and A-04 now use computed-count tokens.
- `data/sources.json` — `reverified_2026_11_17_0cf55ef3` block recording this pass's reads.
- `build.py` flag register — new rows **F83** (handover pointed at non-existent flag ids) and
  **F84** (three stale typed counts), both with their `REPO_EVIDENCE` entries so each row cites
  the files that prove it.
- Generated: `index.html`, `handover.html`, `decisions.html`, `requirements.html`, `topics.html`,
  `flagged.html`, `executive-summary.html`.

No change was made to `data/topics.json` or `EXECUTIVE-SUMMARY-SHOP-PASS.md` (C55 scope), and
no published value was found wrong.
