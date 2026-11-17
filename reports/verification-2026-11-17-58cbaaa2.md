# Verification pass 13 — 2026-11-17 (session 58cbaaa2)

**Branch:** `arena/58cbaaa2-zone1` · **Built on:** `9c6e3f0` · **Landed on:** `4609ff3` (main, after PRs
#125, #127, #128, #130, #131, #134, #135, #136, #137 and #138 merged underneath it) · **Method:**
server-side fetch of each official URL with the page-fetch tool. `curl` from this sandbox returns `000`
for every non-GitHub host, and pre-signed proxy URLs (`routify-file-proxy-sg.oss-ap-southeast-1…`)
return `SignatureDoesNotMatch` — five attempts across two sessions. All reads below went directly to the
publishing host, the constraint every earlier pass recorded.

## 0. Read this first: this pass deleted its own work twice

The session spent a day building a product-intent register of its own (`data/product-intent-confirmations.json`
at schema v2, a new `links.html`, programme flags F76–F80, a `check_special_link_gate()` that refused to
emit a tagged link, a second `data/measurement.json` with its own five events, its own measurement page and
a cookieless browser counter). Then it fetched.

- **First rebase target (`e5fc007`)**: `arena/5b17c077` had consolidated *three* parallel intent records
  into `data/product-intent.json` → `product-intent.html`, retired the file this pass was editing, published
  its own five-event `data/measurement.json` → `measurement.html`, taken flags F76–F82, and wired the
  owner's tracking ID into every link. The duplicates were dropped and the increment re-applied.
- **Second (what merged, `4609ff3`)**: `arena/c55fa0d8` had meanwhile **reversed** the tag-wiring decision —
  `associate_tag` is blank by contract, `analytics/collector.py` is a fail-closed service GitHub Pages does
  not run, `tests/test_build_contract.py` enforces that browser collection stays off, and the footer says so.
  main also took F76–F79 with its own numbering, added a `TP-21`, and registered S36–S38.

So the second re-scope dropped the browser counter as well: shipping it would have made main's footer
sentence false and overrode a merged, tested decision, which is not what an integration pass does. It
survives as **SG-38**, an option set with all three paths and the reason path C was withdrawn.
The superseded draft, its complete diff and a row-by-row drop list are published at
[`../session-58cbaaa2/artifacts/`](../session-58cbaaa2/artifacts/README.md). Everything below is what
actually merged, and every item in it is something `main` did not already have.

## 1. The five submitted links, re-resolved live on 2026-11-17

| Row | Token as submitted | Observed destination | Title as served | Browse path as served |
|---|---|---|---|---|
| PI-01 | `B04G1MEwY` (9 chars) | `/dp/B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff … Black | Home & Kitchen › … › Fryers › Air Fryers |
| PI-02 | `B02NbDxp3` (9 chars) | `/dp/B09B7SB46R` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven … 24 One-Touch Preset Options | Home & Kitchen › … › Air Fryers |
| PI-03 | `B00hJ57DV` (9 chars) | `/dp/B08DKYBTPH` | Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option … Stainless Steel | Home & Kitchen › … › Air Fryers |
| PI-04 | `B0c8moW59` (9 chars) | `/dp/B0DHZTCNR5` | ThermoMaven 1 Sec Professional Digital Meat Thermometer … Black | Kitchen Utensils & Gadgets › Thermometers & Timers › Meat |
| PI-05 | `B0f3GKalj` (9 chars) | `/dp/B0DZFD6R9Z` | CHEF iQ Sense \| Smart Wireless Meat Thermometer \| 3 Ultra-Thin Probes \| Gen3 | Kitchen Utensils & Gadgets › Thermometers & Timers › Meat |

All five carried `lv=shuf` and `plpRedirect=mhFallback`; none carried an `asin=` parameter; PI-01/02/03
resolved to the same three ASINs recorded on 2026-11-16, so the fallback pattern is stable across a day —
an observation about the redirect, not about intent. **Verdict: intended product unconfirmed on all five
rows.** `intended_asin`, `official_listing_url`, `confirmation_date` and `confirmation_source` stay null;
observations live only in the `observed_*` fields; the two fields are never merged, per the brief. Each
token is nine characters against Amazon's ten-character ASIN definition (S23), so they are short-link
handles, not product identifiers — recorded as a format observation, never as a claim that a link is
broken, invalid or non-compliant.

## 2. What the brands' own catalogues do and do not settle — new to this record (**F80**)

| Row | Listing says | Brand page says | Registered |
|---|---|---|---|
| PI-04 | "1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy \| NIST&NSF Certified …" | ThermoMaven's instant-read line is **F1 Pro / F1 Turbo**, sub-second read; "1 Sec" is not used there as a model name | S40 |
| PI-05 | "iQ Sense \| Smart Wireless Meat Thermometer \| 3 Ultra-Thin Probes \| Gen3" | CHEF iQ states model **CQ60-3C-Z3-E**, the Gen3 probe configuration, an ambient rating the listing omits, and names air-fryer use among the heat environments | S39 |

A listing's marketing phrase and a manufacturer's model designation are different kinds of identifier and
neither names the ASIN, so the rows cannot be closed by reading harder and no product page is written for
either. Both brand hosts went into `verify.py`'s `OFFICIAL_HOSTS` with a comment stating that registration
means "official brand site", not "identity confirmed".

## 3. The tracking ID — and the correction this project owed its own record (**F81**)

`shopnow047c-20` was checked against S6, re-read verbatim: the worked example is `storeid-20` with
sub-tag `storeid-1-20`; the supplied value **matches the shape**; the node publishes no validation rule
and no per-account list, so shape is not existence. Two nodes linked from it, read the same day, change
the argument:

* **S41** — *"it is not necessary for your unique ID to appear in order for us to track sales made after
  the initial click through. The individual shopping session will be tagged in a way that allows us to
  track the items purchased and credit you with the appropriate commission."* A landing URL with no
  visible `tag=` is therefore a **null** observation, not evidence of failed attribution — in either
  direction. Passes including this one had cited that absence beside their caution; the inference is now
  narrowed **where it is drawn in the present tense** (a dated callout on `product-intent.html`, next to
  the per-row `associates_link_test_*` fields, plus a bracketed annotation on the two `decision.json`
  rows that made it), and the dated rows themselves are left exactly as written.
* **S42** — names the screen that creates IDs (*Manage your Tracking ID*), the **Tracking ID Summary
  Report** where each ID's data is read, and the **100 tracking IDs per account** limit. That report row,
  not a URL inspection, is what the per-row link-test fields and Q-28 wait for; the limit is why a
  per-channel sub-tag scheme is cheap enough to recommend (recorded in the register's `sub_tag_plan`).

## 4. What shipped

| Layer | Delivered |
|---|---|
| Sources | **S39–S42** registered (42 total, all official, all linked): the two brand catalogues and the two tracking-ID help nodes; `S6`'s `page_version` gained the verbatim 2026-11-17 re-read. |
| `data/product-intent.json` | `brand_catalogue_check` on PI-04/PI-05 (listing says / brand page says / verdict / sources), their `observed_source_ids` extended, and top-level `observation_method_correction` + `sub_tag_plan`. |
| `product-intent.html` | A brand-catalogue table rendered **from the register** (a new row needs no template edit) and the dated correction callout, both with source badges; verdict cells link to F80 so nothing reads as a closed item. |
| `build.py` | Constants read from the canonical register (`SUBMITTED_ROWS`, `N_SUBMITTED_LINKS`, `_num_word`, `_submitted_links_in_category`, `LINK_RECHECK_DATE`); **F80/F81/F82** programme flags with `REPO_EVIDENCE` paths; `check_submitted_link_count()`; three new `req_counts()` tokens (`n_submitted_links`, `n_intent_confirmed`, `n_link_tests_passed`). |
| The count repair (**F82**) | main's category lede still opened "The three supplied links were observed landing…" in the present tense, two days after the register grew to five — every value inside the sentence correct, the sentence false. It now reads `len(rows)` and the register's own `observed_listing_category`, spelled as words. |
| Registers | Suggestions **SG-36** (the two-links decision with paths A/B/C), **SG-37** (close attribution with one click read in the report, plus per-channel IDs), **SG-38** (what measurement may become, including why the counter was withdrawn) and path **P6**; questions **Q-27**, **Q-28**; topics **TP-22**, **TP-23** queued and deliberately unwritten; requirements **H-01** (partial, by arithmetic) and **H-02** (delivered, guard-backed); `data/decision.json` annotated in dated brackets. |

## 5. The guard, proven in both directions

`check_submitted_link_count()` scans only the surfaces where a count is a claim about now (`index.html`,
`product-intent.html`, `measurement.html`, `compare.html`, `picks.html`, `compliance.html`, `categories/`,
`products/`, `guides/`). Current tree: builds silently. Inject the old phrase back into the lede and the
build exits non-zero naming the register's row count and telling the author to read the number or date the
sentence. The scope is the point: a dated row that says "all three supplied links" is a true statement
about 2026-11-14, and a check satisfiable only by rewriting history is worse than no check.

A process note in the same category: the first version of the pattern required a lead-in word
(`all`, `none of`, …) and therefore matched nothing at all — a guard that cannot fail. The negative test
is what caught it, and it is recorded in F82 rather than tidied away.

## 5b. Addendum, written after this merged — the fix was wrong too

PR #140 merged as `6c9d313` and deployed with the lede reading **"0 of the five links submitted to this
project were observed landing on air fryer or air fryer-oven listings."** The repair had moved the number
out of the sentence and into the code, and the code read `observed_listing_category` as an Amazon browse
path. It is not one: the consolidation pass stores a *prose judgement* in that field — "Air-fryer product
title on observed landing page; intended product unconfirmed" — hyphenated, and the classifier tested for
`"air fryer"` with a space. No row matched, the count returned 0, the sentence rendered confidently, and
**every gate stayed green**. Recorded here rather than quietly amended, because the failure is the point:

* **A derived number is only as verified as the field it reads.** "Computed from the register" is not a
  synonym for "true"; it moved the guess from the prose into the code, where no reader could see it.
* **A guard with a parsing hole is a guard that passes.** The original check could only read spelled
  numbers 1–12, so a literal `0` was unparseable and skipped — the one value the defect actually
  produced. Digit and `zero`/`no` forms now parse, and the classifier **refuses to build** when it
  matches nothing, so a register-wording change fails loudly instead of silently publishing a zero.
* **Fixed prose inside a computed sentence is the same defect in slower clothing.** The tail ("and the
  rest land under a different browse path") is derived now too — it becomes false the day every submitted
  link lands in-category.
* **Re-proved in both directions.** Current tree builds silently; injecting `Four of the five`,
  `0 of the five` and `Zero of the five` each exits non-zero naming the register's own numbers and
  pointing at `_submitted_link_clause()`. Follow-up: PR #141.

## 6. Refused, and why

No Amazon prices, star ratings, review counts or rankings (Policies §2(b)/§6(t); no PA-API/Creators
credentials held) · no photography, generated or copied · no analytics endpoint, and no browser
collection while main's contract keeps it disabled (the withdrawn work is offered as SG-38 instead) · no
campaign-ledger row, conversion score or revenue forecast · no claim that the supplied short links are
invalid · no unilateral edit to a merged decision, and none to another session's annex.

## 7. Gates, on the landed tree

```
python3 build.py                  built 52 pages (2368 KB HTML); sitemap 31 urls; feed 21 items
                                  re-run twice: byte-identical (md5 over every tracked .html)
python3 verify.py                 130 pages · 77 spec rows (75 verified, 2 blank+flagged) · 42 sources ·
                                  0 warnings · 0 errors · 1 pre-existing NOTE
                                  (caution-status row chefman-8qt-turbofry/Basket divider)
bash scripts/ci-check.sh          33 platform unit tests · data audit clean · s2 annex "build current:
                                  16 files" · 9,585 links / 0 broken
python3 -m unittest discover -s tests   17 tests OK — includes the intent/analytics build contract
python3 scripts/verify_site.py    393 assertions — ALL CHECKS PASSED
python3 research/check_research.py 834 checks · 67 verified fields · 23 blank/flagged — OK
```

Every `<tbody>` row on every generated page still carries a registered source link or a flagged-page
pointer; every outbound Amazon anchor keeps `rel="sponsored"`; the disclosure stays above the fold.

## 8. For the next session

* **Q-28 is the only row that unblocks revenue** and it is five minutes inside the account: confirm the ID
  is listed, click one published link, read the Tracking ID Summary Report. Then fill the per-row
  `associates_link_test_*` and `associates_central_confirmation_*` fields; `tests/test_build_contract.py`
  decides when `associate_tag` may stop being blank. Do not substitute a URL inspection (S41).
* **Q-27** decides SG-36's path, and whether TP-22/TP-23 are written or the two rows are parked or dropped.
* When the owner submits another link: **add a row to `data/product-intent.json`, never a sentence.**
* Before building on a claim of what main does or does not have, `git fetch origin main`. This session's
  work was cut in half twice by not doing that first; the second cut was the one that mattered.
