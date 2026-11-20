# Verification report — 2026-11-20 · session `arena/915c51ea-zone1`

Scope: the shopfront conversion pass and the reader-facing design polish it required.
Base read before any edit: `main` @ `1c7de82` (merge of PR #185), tree clean,
`scripts/ci-check.sh` exit 0.

Every statement below was either **read live on 2026-11-20 in this session** or is a
**dated record this repository already published**, and each is labelled as one or the
other. Where a value could not be established from an official source it is not stated
anywhere on the site; the row that would have carried it is flagged instead.

---

## 1. Live reads performed on 2026-11-20

| # | Source read | What was seen | Used by this pass |
|---|---|---|---|
| 1 | [Chefman TurboFry Touch 8 Qt / 5 Qt product page (S12)](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) | Model strings `RJ38-SQSS-8T` (and `RJ38-SQSS-5T`); "Max temp: 400ºF/ 205ºC"; "4 cooking presets"; "5-quart or 8-quart nonstick basket"; "Top-rack dishwasher-safe basket"; "200–400°F / 95º-205ºC temperature range"; "Power: 1700W/120V"; "Dimensions: (8 Qt Model) 15.4 in x 12.6 in x 13.5 in / 39.11 cm x 32 cm x 34.29 cm"; "Weight: (8 Qt Model) 12.8 lbs / 5.8 kg"; description ends "Designed for 4-6 people, this family-sized air fryer…"; a Size selector offering 8 Quart and 5 Quart; brand review widget reading 4.6 with 719 total reviews | the new guide's §1–§3; the decision kit on the 8 Qt page; corroboration of the register's existing rows |
| 2 | [Chefman TurboFry Touch 6 Qt Dual-Window product page (S10)](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | Model `RJ38-SQPF-3TDB-2W`; "This 6-quart air fryer combines two powerful air fryers in one"; "a Sync Finish feature to ensure both baskets finish cooking simultaneously"; "Max temp: 450ºF/ 235ºC with Hi-Fry function"; "Sync Function so both baskets …" | the new guide's §1; the decision kit on the 6 Qt page |
| 3 | [Emeril Lagasse French Door AirFryer 360 product page (S14)](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | Specification block: "26-Quart Capacity" paired with "**preparing food for 4–6 people**"; "16.9"D x 15.8"W x 14.8"H Product Dimensions"; "24.6 Liters Capacity"; "120 volts"; "25 Cooking Pre-sets"; "Dual-Speed Fan"; 1-year warranty badge; description says "24 one-touch cooking presets", "26-quart capacity … fits a whole chicken, 12-inch pizzas, or a full tray of cookies", "Included are 7 premium accessories"; ten modes named (Air Fry, Bake, Broil, Defrost, Dehydrate, Grill, Proof, Reheat, Roast, Warm); manual link to the registered FAFO-001 PDF | **the one row added to `data/products.json`**; the new guide's §1–§3; the decision kit on the Emeril page |
| 4 | [CHEF iQ iQ Sense product page (S39)](https://chefiq.com/products/iq-sense) | Heading shows `CQ60-1C-Z1-E`; description: "Five internal sensors and heat resistance up to 1000°F"; feature list: "4 internal temperature sensors for accuracy within 1°F", "1 ambient temperature sensor", "Wi-Fi and Bluetooth® connectivity", "Heat resistant up to 1,000ºF (537ºC)", compatible with "air fryer" among others; Size selector offering **1, 2, 3 and 4 Probes**; two colours; "In stock, ready to ship" | **two new irregularities recorded** (§3, I-1 and I-2); no thermometer copy was written |
| 5 | [ThermoMaven official site (S40)](https://www.thermomaven.com/) | F1 Turbo tile: "0.5s Instant Read · ±0.5℉ Accuracy · IP67 Waterproof · Lifetime Warranty"; G2 tile: "6 Sensors · Sub1G Range 3000ft · IPX8 · 1.5-year Warranty"; brand review quotes describing auto-rotating display, magnet and bottle opener (customer wording, not brand spec) | corroboration only; nothing new asserted from it |
| 6 | [Supplied short link 3 — `https://link.amazon/B00hJ57DV`](https://link.amazon/B00hJ57DV) | Followed to `https://www.amazon.com/dp/B08DKYBTPH?…&plpRedirect=mhFallback&…`; page title "Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option …" | §2 — corroborates the register's observation and refines open flag **F106** |
| 7 | [Supplied short link 1 — `https://link.amazon/B04G1MEwY`](https://link.amazon/B04G1MEwY) | **Fetch failed twice** (retriever error, no page content) | **no conclusion drawn.** The 2026-11-19 dated record in `data/product-intent.json` stands untouched |

Not re-read today, and deliberately not re-stamped: the three Associates policy pages, the
FTC pages, the two owner's-manual PDFs (S13, S15, S18) and the two remaining supplied
tokens. Where this pass cites them it cites the repository's own dated reads, and the new
guide says so in its `source_checks` scope rather than implying a fresh fetch.

**Prices and review counts seen while reading brand pages were not published.** The
Chefman and ThermoMaven pages carried discount pricing and star widgets; Amazon's page
carried prices and ratings for other products. None of it entered the site, per the
display rule in Program Policies §2(b) (registered as S2) and the site's own answer to
Q-16.

---

## 2. What the supplied links did today

`link.amazon` is not reachable from this sandbox's shell (egress is limited to a short
allow list), so the redirect reads above were made with the retrieval tool, which is the
same route earlier passes used.

Link 3 reached **a product detail page for the ASIN the register already records**
(`B08DKYBTPH`), and the landing URL still carries `plpRedirect=mhFallback`. That is the
full observation: a destination was reached, and the shortener's own query string says the
routing used a fallback path.

Consequence for **F106** (opened 2026-11-19 by `arena/2ce347cb` after the same token twice
resolved to the Amazon homepage): today the token resolved to a product page, so the
instability is not reproduced — while the `mhFallback` marker explains how a token could
land on the homepage on one day and on the product page on another. **This pass did not
edit `data/flagged.json`** (another session's register) and does not withdraw F106. It
records the dated observation here and asks the flag owner to fold it into the row. The
position of this repository is unchanged: the five supplied strings are neither valid nor
invalid, and their exact compliance status remains unresolved in
[Zone3 FLG-003](https://kanlerxz87-cyber.github.io/Zone3/flagged.html#FLG-003).

The listing title read through that redirect again advertises "450°F Hi-Fry", while the
brand page for the model the register maps the ASIN to documents a 400 °F maximum. Flag F3
therefore still describes a live conflict; nothing here resolves it, and the site continues
to print both readings rather than an average.

---

## 3. Irregularities found and opened for review

| ID | Finding | Status |
|---|---|---|
| I-1 | **The CHEF iQ page contradicts itself on sensor count.** Same screen, 2026-11-20: the description says "Five internal sensors"; the feature list says "4 internal temperature sensors for accuracy within 1°F" plus "1 ambient temperature sensor". The register's `Sensors` row prints the feature-list reading only. | Raised as **SG-57** (a proposed correction to `data/thermometers.json`, owned by the pass that published the thermometer pages) and **Q-46** (what is missing, and how to settle it). Not silently rewritten. |
| I-2 | **The same page sells 1, 2, 3 and 4-probe variants.** The register's "In the box" row describes one probe, a hub and a cable, which matches the selected variant but not the page's whole offer. | Recorded in **Q-46**; no register row changed. |
| I-3 | **Two brands print the same household-size figure beside capacities roughly three times apart** — "Designed for 4-6 people" next to one 8-quart basket, "preparing food for 4–6 people" next to a 26-quart cavity. It is also not stated whether Chefman's sentence describes the 5 Qt variant as well, since one description serves both sizes. | Used as claim-literacy content in the new guide; the ambiguity is opened as **Q-45**; the proposal to surface the pair where the decision is made is **SG-61**. |
| I-4 | **Dash forms differ between the source and the register.** Chefman's page writes "4-6" with a hyphen; the register's published value is "Designed for 4–6 people" with an en dash. The row reproduces the brand's wording with typographic normalisation, not a wording change. | Recorded here for the reviewer; no value altered. |
| I-5 | **A test pinned the article count at 26.** `tests/test_publication_output.py::test_owner_and_unconfirmed_notes_stay_out_of_sitemap` asserted a literal count, so shipping a 27th guide failed the build with no explanation of what was actually at stake. | Repaired, not loosened: the test now asserts that every registered guide has **exactly one** sitemap URL, that no two guides share a slug, and that the guide index appears once — the structural property the number was standing in for. |

No other discrepancy was found between the site's published rows and the sources re-read
today: the Emeril dimensions, capacity, accessory count and 25-vs-24 preset conflict; the
Chefman 6 Qt and 8 Qt capacity, footprint, temperature and care rows; the 8 Qt brand-site
rating snapshot (4.6 / 719 reviews — the register already carried exactly this figure and
count); the ThermoMaven F1 Turbo read time, accuracy, waterproofing and warranty terms; and
the ASIN each supplied token reached.

---

## 4. What this pass changed in the reader build

* **SG-53 (options A and B) — implemented as far as evidence allows.** `product_cta()`'s
  three-sentence qualification is one line; a decision kit renders on **all five** product pages —
  *Good fit if* and *Look elsewhere if* on the air fryers, *Look elsewhere if* on the thermometers,
  each cell quoting a row the register already publishes with that row's own source ids, then the five
  questions that finish the decision with a link to the page that answers each, then the other
  documented machines and the side-by-side matrix. The third row this pass first shipped
  (*Confirm before you click*) was **dropped at merge, not deleted**: main's same-day reader-polish
  pass (PR #192, `arena/abbb9745`) moved "What it is for", "Check first" and a "From the documents"
  citation line into the hero, so repeating them under the buy button would have put the same sentence
  on the screen twice. The thermometer hero already printed both, which is why its kit carries only
  the row the hero cannot. `tests/test_integration_output.py`'s assertion of the affiliate sentence
  still holds verbatim.
* **SG-15 (option A) — implemented.** `not_published_note()` derives its sentence from the
  blank specification rows themselves, so it cannot drift from the table it describes. The
  Emeril row the brand page does publish was added; the Emeril page has no blank rows, and
  its page now says what that does and does not mean.
* **One row added to `data/products.json`** — Emeril `Stated household size`, value
  "preparing food for 4–6 people", cited to S14, with a note that it is the brand's wording
  read live on 2026-11-20 and that no one was cooked for. Spec rows go 77 → 78; verified rows
  75 → 76; blank-and-flagged stays 2.
* **New guide** `articles/hosting-week-air-fryer-math.html` (topic TP-16), filed in the
  `choose` cluster, in the sitemap, the feed and both topic registers (the
  `data/design-prompt.json` mirror gained row A-16, which is what flag F85 asked for).
* **Canonical capacity guide refreshed, not duplicated.** The queue's kill rule forbids a
  second article answering the same question, so TP-16 became a worksheet page and the
  capacity guide gained one short hosting-week section pointing at it, with its own dated
  `source_checks` entry naming exactly which pages were read for that section.
* **`publication/theme.css`** (the source of the generated `assets/style.css`): decision-kit
  styling, guide-index cluster numbering, card hover treatment, article prose size on wide
  screens, and a top rule on the buyer table of contents. All inside the existing token set;
  `prefers-reduced-motion` already neutralises transitions.
* **Suggestion and question registers**: SG-53 → `partial` (the counter that would say
  whether any of this is used is gated on Q-30), SG-15 → `complete`, and SG-57 … SG-61 plus
  Q-45 … Q-47 opened. `test_suggestions_have_current_evidenced_states…` passes, so every row
  carries an evidenced implementation state.

**No conversion, click, traffic or ranking claim is made by any of this.** SG-53's own note
records that rule, and the campaign ledger remains empty.

---

## 5. Gates run on this branch

| Gate | Result |
|---|---|
| `python3 build.py` | exit 0 · 142 pages · 42 sitemap URLs · 27 feed items · deterministic rebuild byte-identical |
| `python3 verify.py` | 142 pages · **78 spec rows (76 verified, 2 blank+flagged)** · 49 sources · **0 errors** · 0 external warnings |
| `python3 -m unittest discover -s tests` | **Ran 75 · OK** |
| `node --test tests/*.test.cjs` | **14 pass · 0 fail** |
| `platform` engine tests | Ran 33 · OK |
| data audit | clean |
| `scripts/build_s2_site.py --check` | build current: 16 files |
| `scripts/check_links.py` | **12,971 links · no broken link** |
| `scripts/ci-check.sh` | **exit 0** (all of the above in sequence) |

---

## 6. Deliberately not done

* TP-22 (a probe-in-an-air-fryer guide) is the subject of open PR #173 — publishing it here
  would duplicate another session's work. TP-19 and TP-23 stay blocked on Q-20 and Q-27 as
  the queue records them.
* No product photography and no generated product likeness. **SG-42 records generated
  imagery as a rejected option**; this pass stayed on the illustration-and-typography path and
  did not reopen it.
* No new outbound destination convention, no analytics activation, no ledger row, no Search
  Console action, no tracking-ID validation. `shopnow047c-20` stays recorded, unvalidated and
  unapplied; intended-ASIN fields stay blank and stay separate from observed redirects.
* The eight open pull requests (#139, #141, #144, #146, #150, #159, #168, #173) were not
  merged, closed or edited. Two of them fail the browser check on their own branch (#159,
  #173), which is a reason for the owner to sequence them, not a reason to delete them.
* `data/thermometers.json`, `data/flagged.json`, `data/product-intent.json` and every frozen
  annex tree are untouched; the findings that belong to them are listed in §3 with the row
  that should carry them.

---

## 7. A CI-only gate, an unreadable log, and what the failure actually was

The first three pushes of this branch passed the `verify` job and failed the workflow's `browser`
job. Nothing in that job can run here: Playwright needs a Chromium download from
`cdn.playwright.dev`, and both the run log and its `browser-gate-evidence` artifact are served from
hosts the session sandbox cannot reach. So the failure could not be reproduced or read.

What was done instead of guessing:

1. A **temporary** step was added to the browser job that re-emits the gate's own failure text as
   check-run *annotations*, which are reachable through the API (`scripts/tmp_gate_diagnostics.py`,
   plus one workflow step, both removed again in the next commit — nothing about the site changed).
2. The annotation returned the real assertion:
   `Error: questions.html: document horizontal overflow — expected <= 321, received 684`, from
   `tests/browser/publication.spec.cjs:47`, which sweeps every root, product, category, guide and
   article page at 320/390/768/1440px. The `check_publication_browser.mjs` gate passed
   (`PASS: 70 page/viewport combinations…`) because its own page list does not include
   `questions.html` — which is also why this class of defect can survive the second gate entirely.

**Cause.** Not the decision kit. My three new rows in `data/questions.json` put bare URLs inside
`what_we_know` prose — `(https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1)`,
86 unbreakable characters — and `.qcard` did not declare `overflow-wrap`, so one token widened the
whole document. Two fixes, one for this content and one for the class:

* the register text now says "the page linked below as this row's evidence" and the URL lives only in
  the row's `sources[]`, where it renders as a labelled link — the convention every other row uses;
* `publication/theme.css` gives `.sug`/`.qcard` and their paragraphs, list items and definition text
  `overflow-wrap:anywhere`, so a long token in *future* register copy cannot widen those pages either.
  `overflow-wrap` inherits, which is why one declaration covers the nested evidence links too.

A 61-page static sweep of the rendered output — every visible token over 44 characters outside tables,
`code`, `pre` and the blocks that already break — now returns **zero** risky tokens, and the same
sweep run without the new `.qcard` rule returns exactly the two tokens above. `tests/test_publication_output.py`
carries the headless half of both findings: the decision kit may not declare a non-shrinking grid column
or an unbreakable link, and the two register-card components must declare breakability.

Two things written earlier in this report, and in the branch's first commit message, attributed the
failure to the kit's fixed label column. That hypothesis was wrong and the wording is corrected here
rather than quietly rewritten. The kit's mobile collapse is **kept**: at 320px a 150px label column
leaves a ~60px text column, which is unreadable even though it did not trip the gate — a readability
fix found by reading the CSS, not a CI repair, and labelled as such in `publication/theme.css`.
