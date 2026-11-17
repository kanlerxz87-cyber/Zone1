# Verification pass 13 — 2026-11-17 (session 58cbaaa2)

**Branch:** `arena/58cbaaa2-zone1` · **Rebased onto:** `c6a143a` (merge of PR #126) · **Claim commit:** `590c727`
**Method:** server-side fetch of each official URL through the page-fetch tool. `curl` from this sandbox
returns `000` for every non-GitHub host, and pre-signed proxy URLs of the form
`routify-file-proxy-sg.oss-ap-southeast-1.aliyuncs.com/...` return `SignatureDoesNotMatch` — five
attempts across two sessions, so all reads below went directly to the host that publishes the fact.
That is the same constraint every earlier pass recorded.

## Why this pass exists

The 2026-11-17 brief supplied three things no earlier pass had:

1. **Two more `link.amazon` links** — `B0c8moW59` and `B0f3GKalj` — on top of the three submitted on
   2026-11-13.
2. **A selected tracking ID** — `shopnow047c-20`.
3. A measurement instruction: a privacy-preserving outbound-click counter, a self-hosted analytics
   endpoint, five defined events, and an empty but well-defined campaign ledger, with the explicit
   note that no conversion score or revenue forecast is to be presented.

It also repeated the standing instruction not to assert that the supplied short links are invalid.
Nothing on this page says they are.

## 1. The five submitted links, re-resolved live on 2026-11-17

| ID | Token as submitted | Observed destination | Title as served | Amazon browse path as served |
|---|---|---|---|---|
| PI-01 | `B04G1MEwY` (9 chars) | `amazon.com/dp/B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff … Black | Home & Kitchen › … › Fryers › Air Fryers |
| PI-02 | `B02NbDxp3` (9 chars) | `amazon.com/dp/B09B7SB46R` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven … 24 One-Touch Preset Options | Home & Kitchen › … › Air Fryers |
| PI-03 | `B00hJ57DV` (9 chars) | `amazon.com/dp/B08DKYBTPH` | Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option … Stainless Steel | Home & Kitchen › … › Air Fryers |
| PI-04 | `B0c8moW59` (9 chars) | `amazon.com/dp/B0DHZTCNR5` | ThermoMaven 1 Sec Professional Digital Meat Thermometer … Black | Kitchen Utensils & Gadgets › Thermometers & Timers › Meat |
| PI-05 | `B0f3GKalj` (9 chars) | `amazon.com/dp/B0DZFD6R9Z` | CHEF iQ Sense \| Smart Wireless Meat Thermometer \| 3 Ultra-Thin Probes \| Gen3 | Kitchen Utensils & Gadgets › Thermometers & Timers › Meat |

Every one of the five carried `lv=shuf` and `plpRedirect=mhFallback` in the landing URL, and none
carried an `asin=` parameter. PI-01/02/03 landed on the same three ASINs recorded on 2026-11-16 —
the fallback pattern is stable across a day, which is a fact about the redirect, not a confirmation
of intent. **Verdict on all five: intended product unconfirmed.** `intended_product` fields stay
null and are held in separate fields from the observed destination, per the brief's instruction that
the two must never be merged.

**Token rule, re-checked:** Amazon defines an ASIN as ten characters (S23); all five submitted tokens
are nine. They are therefore short-link handles, not ASINs, and cannot be read as product
identifiers. This is recorded as an observation about format, not as a claim that the links are
broken or non-compliant (FLG-003 / F78 remain the standing unresolved item).

## 2. What the brands' own pages do and do not confirm

| Check | Official page read 2026-11-17 | Result |
|---|---|---|
| CHEF iQ Sense model behind `/dp/B0DZFD6R9Z` | [chefiq.com/products/iq-sense](https://chefiq.com/products/iq-sense) (S36) | Brand page names model **CQ60-3C-Z3-E**, five sensors, 1,000 °F ambient rating, and lists air-fryer use among its heat environments. "Consistent with" the observed listing; the listing does not state the model, so this closes nothing. |
| ThermoMaven "1 Sec" behind `/dp/B0DHZTCNR5` | [thermomaven.com](https://www.thermomaven.com/) (S37) | The brand's instant-read line is named **F1 Pro / F1 Turbo** with a 0.5 s read; the brand does not use the label "1 Sec" that the observed listing carries. Flagged as F77 rather than reconciled by guesswork. |

Both new hosts were added to `verify.py`'s `OFFICIAL_HOSTS` with a comment stating that neither page
confirms a listing identity — the allow-list entry means "this is the brand's own site", not "this
settles the ASIN".

## 3. The selected tracking ID, and one correction this pass owed the record

`shopnow047c-20` was read against the only official page that describes what a tracking ID is
(S6, re-read verbatim on 2026-11-17): the help node's worked example is `storeid-20` with sub-tag IDs
of the form `storeid-1-20`. **The supplied value matches that shape.** The node states no validation
rule and publishes no per-account list, so a shape match is not an existence check.

While reading S6, two nodes linked from it were read as well, and one of them changes how this
project has been arguing its own case:

| Source | Verbatim finding | Consequence |
|---|---|---|
| S39 — "Why doesn't my tracking ID appear in your URL…" | *"it is not necessary for your unique ID to appear in order for us to track sales made after the initial click through. The individual shopping session will be tagged in a way that allows us to track the items purchased and credit you with the appropriate commission."* | The absence of `tag=` on an observed landing URL is a **null** observation, not a negative one. Earlier passes cited that absence alongside their caution. It is now recorded as a method correction on `links.html`, in F78, in Q-28, in SG-37 and in requirements row H-02 — dated and additive, not quietly edited out of the historical rows. |
| S40 — "How do I request multiple tracking IDs?" | *"visit your account and click on 'Manage your Tracking ID'"* … *"there is a limit of 100 Tracking IDs per associate account"* … per-ID data appears in the **Tracking ID Summary Report** | The confirmation the gate waits for is a report row, not a URL inspection; and the 100-ID limit is why the per-channel sub-tag plan is the cheap option. S40 is also the second official page naming `affiliate-program.amazon.com/home/account/tag/manage`, which is where that screen URL in the register comes from. |

**Gate state: closed.** `data/product-intent-confirmations.json → selected_tracking_id.tagging_gate.state`
is `closed`; `check_special_link_gate()` fails the build if a tagged anchor appears while it is
closed, or if it is opened without a confirmation date and a cited source. No published link carries
the tag, and none is described as invalid.

## 4. What was built

* `data/product-intent-confirmations.json` → **schema v2**: `submitted_token` (as supplied, with
  character count and the format check), `observation_2026_11_17`, top-level
  `observations_2026_11_17` / `submitted_token_rule`, `selected_tracking_id` with
  `provenance`/`format_check`/`owner_action`/`tagging_gate`, and `observation_method_correction`
  (S39/S40). Intended and observed fields remain disjoint by construction.
* `links.html` (generated, `page_links()`) — the register rendered for a human: intended-vs-observed
  table, per-link observation cards, the gate block, the "href after confirmation" shown **as escaped
  text only**, and the four ordered edits that close a row.
* `data/measurement.json` → `measurement.html` — **5** events (EV-01 `outbound_click`, EV-02
  `cta_impression`, EV-03 `page_arrival`, EV-04 `guide_reached_end`, EV-05 `first_party_report_row`),
  each with properties, prohibited contents, status and the decision it informs; `endpoint: null`
  recorded as a gap rather than invented; an eight-column ledger with a filling rule per column and
  **0** rows; four anti-patterns the register rules out; and the per-channel tracking-ID option
  sourced to S6/S40.
* A cookieless, request-free counter in the generated `assets/app.js`: `localStorage` only
  (`zone1k-counts`), per-page click tallies, `IntersectionObserver` at 0.55 for CTA impressions,
  a 40-key ceiling, export and erase. The footer's §3(e) statement was rewritten to describe exactly
  what now happens, and every surface that shows a number labels it as one device's count.
* Registers: **5** new suggestions (SG-36…SG-40) and decision path **P6**, **5** new questions
  (Q-27…Q-31), **2** queued topics (TP-21, TP-22), **4** new requirements rows (H-01…H-04), and
  programme flags **F76–F80** with evidence paths. `data/sources.json` is now **40** sources
  (S36, S37, S38 added this pass; S39 and S40 added the same day; S6 re-read).
* `S-20` mobile-first pass, presentation only: 44 px tap targets and a type floor below the mobile
  breakpoints, and a sticky comparison bar on `compare.html`.

## 5. Defects found in the line-by-line review

| Found | Defect | Repair |
|---|---|---|
| 2026-11-17, minutes after the brief arrived | **Counts typed into present-tense prose.** The footer and the landing-page status note still said "three supplied links" while the brief described five; the category lede said the same. Ten passes had written the number as narrative, so the day the owner acted, the site went false without a byte of its data being wrong (F80). | The present-tense surfaces now read `len(records)` from the register; `N_SUBMITTED_LINKS` feeds the footer, the landing note and the register page; `req_counts()` gained `n_submitted_links`, `n_intent_confirmed`, `n_events`, `n_ledger_rows`; the category lede counts in-category links with `_links_in_category()`. |
| same | No guard held the new count. | `check_submitted_link_count()` fails the build if a page asserts a different number in its own words. It is **scoped** to the surfaces where the count is a claim about now (`index.html`, `links.html`, `measurement.html`, `compare.html`, `picks.html`, `compliance.html`, `categories/`, `products/`, `guides/`) — a dated row that says "all three supplied links" is a true statement about 2026-11-14, and rewriting history to satisfy a check would destroy the evidence. The guard was deliberately not weakened; it was pointed. |
| same | Ambiguous internal link target on the category page (lede referenced "the submitted-links register" with no such page in `NAV`). | `links.html` added to `NAV` and to the sidebar; `check_no_orphan_pages()` and `check_links.py` both pass. |
| same | A new suggestion row (`SG-40`) had no external citation. The build's own `check_row_sources()` caught it, not this pass. | Row given the repo-side evidence link it actually rests on (`data/reverification.json`), rather than exempting the row. |
| same | `data/sources.json` briefly carried two stray keys (`count_note`, `notes`) from an editing script, and the new-register JSON files were re-serialised at the wrong indentation, inflating the diff. | Both removed/restored to each file's own style; the data diff is now additive (47–317 lines per file, 1–2 deletions). |
| process | Two attempts to patch a patch script from a `python3 - <<'PY'` heredoc failed with `SyntaxError` from nested quotes. | Recorded so the next session edits the file or makes the patch script the single source, instead of quoting strings inside strings inside a shell here-doc. |

## 6. Deliberately not done

* **No Amazon prices, star ratings, review counts or ranking data** anywhere (Program Policies §2(b),
  §6(t); no PA-API/Creators API credentials are held). Manufacturer list prices stay in their own
  sourced column.
* **No photography.** Real product photography requires assets this project may not generate and may
  not copy from Amazon Program Content; the owner's decision is still open and the pages ship with
  original line-art glyphs instead.
* **No analytics endpoint.** GitHub Pages serves static files; a collector URL written into a static
  site with nothing behind it would be a promise, not a feature. Recorded as `endpoint: null` with
  the four-item deployment boundary that must be answered first.
* **No campaign ledger rows, no conversion score, no revenue forecast** — as the brief specifies, and
  enforced by the schema (a row with no report date and named source cannot render).
* **No shared-output integration beyond this session's scope:** no other session's published output was
  edited, and the `site/`, `s2/`, `platform/`, `research/` annexes are untouched.

## 7. Gates, as run on the rebased tree

```
python3 build.py                    built 52 pages (2398 KB of HTML); sitemap 51 urls; feed 21 items
python3 build.py (twice more)       idempotent — md5 set of all tracked .html identical across runs
python3 verify.py                   130 pages · 77 spec rows (75 verified, 2 blank+flagged) ·
                                    40 sources · 0 warnings · 0 errors
                                    1 NOTE (pre-existing): caution-status row
                                    chefman-8qt-turbofry/Basket divider
bash scripts/ci-check.sh            33 platform unit tests OK · data audit clean ·
                                    build_s2_site.py --check "build current: 16 files" ·
                                    check_links.py 9044 links, 13 pages owned by this session
python3 scripts/verify_site.py      393 assertions — ALL CHECKS PASSED
python3 research/check_research.py  834 checks, 67 verified fields, 23 blank/flagged — OK
node --check assets/app.js          OK (counter included)
```

Internal-link, fragment, disclosure, `rel="sponsored"`, row-source, flag-id, SEO-metadata,
count-token and link-count guards are all in `build.py`'s `main()` and all pass; there are now 26
`check_*` guards.

## 8. For the next session

* Q-27…Q-31 are the open rows; **Q-28 is the only one that unblocks revenue**, and it is a five-minute
  check inside the account. Opening the gate is four edits, listed on `links.html`.
* If another link is submitted: **add a record to `data/product-intent-confirmations.json`, never
  prose.** The guards now hold the counts.
* `reports/verification-2026-11-17-58cbaaa2.md` is cited from the evidence arrays of F76–F80, S38 and
  the intent register — this file.
