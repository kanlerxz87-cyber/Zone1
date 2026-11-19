# Verification report — arena/2ce347cb-zone1

**Date:** 19 November 2026 (UTC, session window ≈ 19:38–20:10Z)
**Base:** `main` @ `0bcc272` (merge of PR #175)
**Scope:** live re-verification of the five supplied links and three policy sources; one new flag (F106, PI-03 destination instability); the decision worksheet (SG-54); the hosting-week temperature guide (SG-55, TP-28); one new open question (Q-43); one new registered source (S48). No product, account or campaign data changed.

This pass answered the brief's standing asks in the order the brief names them: a dedicated review surface for suggestions (the worksheet), a clear list of what must be answered before a decision is reasonable (the new question row), and a genuinely timely, catchy-but-honest article shipped while its season is live. Everything else in the pass is re-verification.

---

## 1. What was read live, and when

Every item below was fetched in this session. Nothing is quoted from memory or from an earlier pass's notes.

| Source | URL | What it was read for | Result |
|---|---|---|---|
| **PI-01** supplied link | <https://link.amazon/B04G1MEwY> | Final URL and title | → `https://www.amazon.com/dp/B0CDY277D3` — "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black". Matches the record. |
| **PI-02** supplied link | <https://link.amazon/B02NbDxp3> | Final URL and title | → `/dp/B09B7SB46R` — "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included". Matches the record. |
| **PI-03** supplied link | <https://link.amazon/B00hJ57DV> | Final URL and title | **→ `https://www.amazon.com/` (site homepage, title "Amazon.com. Spend less. Smile more.") on two fetches about two minutes apart.** This differs from the `/dp/B08DKYBTPH` target recorded earlier the same day (6ace936d) and in every pass since 2026-11-15. See §2 (F106). |
| **PI-04** supplied link | <https://link.amazon/B0c8moW59> | Final URL and title | → `/dp/B0DHZTCNR5` — "ThermoMaven 1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy | NIST&NSF Certified, Auto-Rotate Bright LED Screen, IP67 Waterproof for Grill BBQ, Stocking Stuffers Gifts for Men, Black". Matches the record. |
| **PI-05** supplied link | <https://link.amazon/B0f3GKalj> | Final URL and title | → `/dp/B0DZFD6R9Z` — "CHEF iQ Sense | Smart Wireless Meat Thermometer | 3 Ultra-Thin Probes | WiFi Unlimited Range | 1000°F Heat Safe | 5 Sensors | BBQ, Grill, Oven, Smoker, Air Fryer | Gen3". Matches the record. |
| **S2** Associates Program Policies | <https://affiliate-program.amazon.com/help/operating/policies> | "Updated" heading; qualifying-purchase wording | Heading still reads "Updated: April 14, 2026" (no drift). Re-read verbatim: click through a Special Link; 24-hour session; 89-day cart window; shipped and paid within 180 days. |
| **S8** FTC Disclosures 101 | <https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers> | Placement and experience rules | "November 2019" stamp present; "Place it so it's **hard to miss**" and "You can't talk about your experience with a product you haven't tried" re-read verbatim. |
| **S48** (new) USDA FSIS chart | <https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart> | Minimum internal temperatures for the new guide | "Last Updated: Apr 14, 2025" visible. Read verbatim: all poultry 165 °F (73.9 °C); beef/pork/veal/lamb steaks, chops, roasts 145 °F + 3-minute rest; ground meats 160 °F; leftovers and casseroles 165 °F; "Cook all food to these minimum internal temperatures, **as measured with a food thermometer**, before removing food from the heat source. For reasons of personal preference, consumers may choose to cook food to higher temperatures." |

**Not verified, and not claimed:** whether any of the five destinations is the *intended* listing; whether `shopnow047c-20` is the tag on any link; whether the Associates account exists or is approved; anything about traffic, clicks, orders or revenue. All landing URLs still carry `plpRedirect=mhFallback` and no visible tag — a null observation, not read in either direction.

---

## 2. New flag — F106: the PI-03 redirect did not reproduce its recorded target

Two fetches of `https://link.amazon/B00hJ57DV` in this session both resolved to the Amazon **homepage** rather than `/dp/B08DKYBTPH`. The same token resolved to the product page for session 6ace936d earlier on 2026-11-19 and in every recorded pass back to 2026-11-15.

What makes this more than a curiosity: the live money pages use the supplied short links as their primary CTAs, and the 8 Qt product page's button is `href="https://link.amazon/B00hJ57DV"`. A redirect that sometimes lands on the storefront homepage instead of the listing is exactly the failure mode the intended-ASIN and one-link-test gates (Q-01, Q-27, SG-37, F80, F101) exist for.

What this pass deliberately does **not** claim:

- It does **not** say the link is broken or invalid. A datacentre fetch without cookies can be treated differently from a browser click; the record says what was observed, not what a shopper will see.
- It does **not** overwrite the historical PI-03 record, which keeps its earlier dated observations.
- It does **not** touch the unresolved compliance question at Zone3 FLG-003.

Action recorded on the flag: re-read this token from a normal browser before any release that carries it; run the enrolled-account one-link test (SG-37); keep the "check model" caveat on the button. No site change was made in response, because the site already routes attribution through the gated path and states the caveat.

---

## 3. What shipped in this pass

| Change | Where | Nature |
|---|---|---|
| **SG-54 — decision worksheet** | `data/suggestions.json`, `build.py` → `suggestions.html#decision-worksheet` | One table under the decision brief listing every register row whose current state is not complete: its current note (what remains), state chip, blocking-question link, evidence link, and a link to draft a choice on the decision log. Derived mechanically from the same JSON the cards render; adds no facts, changes no state. Implemented under the standing adopt-after-silence rule (reversible, low-risk, no account-only fact). |
| **SG-55 / TP-28 — hosting-week guide** | `data/articles.json`, `data/topics.json`, `data/clusters.json` → `articles/turkey-temperature-usda-chart-and-air-fryer-manuals.html` | "What temperature is turkey safe? The USDA chart for hosting week, and what an air-fryer preset can and cannot promise." Answers from the USDA chart (S48, read live before use) plus values already published in `data/products.json` (spliced through the value-placeholder system, which rejects unpublished numbers). Names the preset-vs-measured gap, keeps the 8 Qt's unresolved 450 °F-title/400 °F-spec conflict visible, states plainly that nothing was cooked, probed or timed, and labels the seasonal framing so a December read does not mistake itself for fresh news. **Deliberately no thermometer content** — Q-27/SG-36 keep those links out of the catalogue. |
| **Q-43 — success criteria / stop rule** | `data/questions.json` | The one decision-critical fact no earlier row asks: what outcome, by when, would make this project a success, and what evidence would make it a stop. State: missing — only the account holder can answer. Linked from the worksheet so the queue can be re-sorted against it once answered. |
| **S48** | `data/sources.json` | USDA FSIS Safe Minimum Internal Temperature Chart registered as a primary source, with the verbatim read recorded on the row and in the dated re-verification record. |
| **F106** | `build.py` FLAGS + REPO_EVIDENCE | The PI-03 destination instability (§2). |
| **verify.py allow list** | `verify.py` | `www.fsis.usda.gov` added with the same justification as `www.ftc.gov`: the party that owns the fact publishes the page. |

---

## 4. Gates run on the final tree

| Gate | Result |
|---|---|
| `python3 build.py` | 38 sitemap URLs (was 37), 26 RSS items (was 25), exit 0; value-splice guard, cluster-map guard, row-source guard all exercised |
| `python3 verify.py` | 138 pages (was 137), 77 spec rows (75 verified, 2 blank+flagged), **48 sources** (was 47), 0 errors, 0 external warnings |
| `python3 -m unittest discover -s tests` | 68 tests, OK |
| `node --test tests/*.test.cjs` | 0 fail |
| `research/build_research.py` + `research/check_research.py` | OK, no drift |
| `python3 -m unittest discover -s platform/tests -t platform` | 33 tests, OK |
| `python3 platform/audit/report.py` | AUDIT PASSED (0 warnings) |
| `python3 scripts/build_s2_site.py --check` | build current (16 files) |
| `python3 scripts/check_links.py` | link check ok · 12,100 links |
| Deterministic rebuild | second `build.py` run reproduces byte-identical output (verified by clean `git status` after commit + rebuild) |

Two build guards fired during development and were fixed the way they are designed to be fixed: the splice guard rejected a capitalised published value spliced mid-sentence (rewritten to introduce the value with a dash), and the cluster-map guard rejected an article whose cluster membership was not yet in `data/clusters.json` (map updated). Neither guard was weakened.

---

## 5. Boundaries unchanged, restated

- `shopnow047c-20` stays **selected / unvalidated / unapplied**; `data/config.json` keeps `associate_tag` blank.
- Intended-ASIN/listing fields stay **blank and separate** from observed redirect targets (`data/product-intent.json`).
- Production analytics stays **off**; the five-event contract remains tested but not deployed; the campaign ledger stays empty.
- No Search Console action; no product photography; the supplied short links' compliance status stays unresolved at Zone3 FLG-003 and is not declared either way.
- The two thermometer links stay out of the canonical catalogue (Q-27, SG-36); they appear only as dated link notes.

---

## 6. Merge reconciliation with arena/d154e428-zone1 (recorded per protocol item 6)

While this branch was open, main advanced by PR #178 (arena/d154e428-zone1: two sourced thermometer buyer pages, an indexable thermometer pillar, a 14-row decision-review queue, collector and gate updates). `git pull --rebase origin main` was run before pushing; the rebase conflicts were resolved without discarding either side's work:

- `COORDINATION.md` — merged append-only; both sessions' claim and completion records stand.
- `data/sources.json` — both sessions independently registered the **same** USDA FSIS chart on the same day. Main's row (S48, with its own verbatim read and its companion S49) was kept as the single registered row; this pass's independent verbatim read was appended to the S48 row as corroboration, and this pass's dated re-verification record was kept with its "S48 added" wording corrected to "S48 re-read and corroborated". No duplicate source row exists.
- `verify.py` — both sessions added `www.fsis.usda.gov` (main also added `www.foodsafety.gov`); the duplicate entry was removed, keeping one entry covering both justifications.
- Generated pages (`data.html`, `executive-summary.html`, `flagged.html`) — regenerated from the merged data by `build.py` rather than hand-merged.
- **Wording reconciled, not relitigated:** the merged catalogue now carries thermometer link-note buyer pages from the parallel pass while Q-27 stays `unknowable`. This pass's rows were edited so every statement about the catalogue state is true of the merged tree: the guide (TP-28) contains no thermometer content and cites none of those pages; SG-55's problem/current notes now say the guide deliberately leaves the thermometer pages out rather than that the catalogue excludes them. The parallel pass's records and states were not altered.

Gates were re-run on the rebased tree (results in §4 reflect the post-rebase numbers).
