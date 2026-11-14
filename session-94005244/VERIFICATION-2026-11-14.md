# I9 — Independent line-by-line verification, 2026-11-14 (UTC)

**Session:** `sess-94005244` · **Branch:** `arena/94005244-zone1` (base `b990352`, merged through `f45374b`)
**Method:** every fact below was re-fetched live from its official URL by this session on 2026-11-14
and compared against the value the site publishes. Nothing was copied from another session's record.
Values that could not be confirmed remain blank + flagged on the Flagged for Review page; nothing was
inferred or back-filled.

---

## 1. Gates run on the integrated tree (all green)

| Gate | Command | Result |
|---|---|---|
| Root build + reproducibility | `python3 build.py` (twice) | 14 pages; second run byte-identical (no diff) |
| Root verify gate | `python3 verify.py` | 0 errors (pre-existing s2 allow-list WARNs only) |
| Engine tests | `python3 -m unittest discover -s platform/tests -t platform -p "test_*.py"` | 33/33 OK |
| Data audit | `python3 platform/audit/report.py` | AUDIT PASSED, 0 warnings |
| Research section | `python3 research/build_research.py` + `check_research.py` | OK — no broken links, no unsourced rows, disclosures present |
| Link + source coverage | `python3 scripts/check_links.py` | 4,103 links · 0 broken in the 13 owned pages (inherited-build advisory rows = F25) |
| s2 reproducibility | `python3 scripts/build_s2_site.py --check` | current (16 files) |
| Annex build + verify | `python3 scripts/build_site.py` + `verify_site.py` | 382 assertions, ALL CHECKS PASSED |
| Conflict-marker scan | repo-wide grep | none |

---

## 2. Official sources re-fetched live by this session (2026-11-14)

| # | Source (fetched) | What was re-read | Result vs. the site |
|---|---|---|---|
| 1 | https://link.amazon/B04G1MEwY | Redirect destination + `<title>` | Lands on `amazon.com/dp/B0CDY277D3?lv=shuf&…&plpRedirect=mhFallback`; title "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff…" — **matches** stored title. Fallback markers present (F10/F15). |
| 2 | https://link.amazon/B02NbDxp3 | Redirect destination + `<title>` | Lands on `/dp/B09B7SB46R?…&plpRedirect=mhFallback`; title "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| … 24 cooking functions …" — **matches** stored title; the "24 cooking functions" wording is additional live evidence for F29. |
| 3 | https://link.amazon/B00hJ57DV | Redirect destination + `<title>` | Lands on `/dp/B08DKYBTPH?…&plpRedirect=mhFallback`; title "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option … \| Stainless Steel" — **matches** stored title; the 450 °F claim is still live on Amazon, so the F3 conflict with the brand's 200–400 °F page is still open on both sides. |
| 4 | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | Standard Commission Income Statement, Table 1 + Bounty table | Public, no login. "Physical Books, Kitchen, Automotive — **4.50%**"; "All Other Categories — **4.00%**"; "Toys, Furniture, Home … — 3.00%"; Prime Free Trial **$12.00**, Prime Video First Stream **$5.00**, Prime Video Stream **$0.25** — **all match** the site's commission rows exactly (11/11 rows observed). |
| 5 | https://affiliate-program.amazon.com/help/operating/agreement | Page version + §1/§5 context | "**Updated:** October 15, 2025" — **matches** S1 as recorded. |
| 6 | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | Model, reviews, price block, max temp | `RJ38-SQPF-3TDB-2W`; "**1305 Reviews**"; price block `$108 $90 $84 $102 $96 $72 $119.99` with Save 10–40% badges (the page still does not label which figure is list — I6-2 stands); "**Max temp: 450ºF/ 235ºC with Hi-Fry function**" — **all match** the site's rows. |
| 7 | https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1 | Model, reviews, temp range, presets, power | `RJ38-SQSS-8T`; "**716 Reviews**"; "precise temperatures ranging from **200–400°F**"; presets "**fries, chicken, fish, and meat**"; "Designed for **4-6 people**"; "**98% less oil**"; same price ladder incl. `$119.99` — **all match** the site's rows. |
| 8 | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | Price, model, rating, capacity, dims, presets | **$199.99**; `4-00675-02A-VN`; **2.6 / (25)**; "26-Quart Capacity"; "25 Cooking Pre-sets" (spec block) vs "**10-in-1**" (description) vs an `11-in-1_convection_oven_in_action.png` carousel asset; **16.9"D × 15.8"W × 14.8"H**; **24.6 Liters**; **120 volts** — **all match** the site's rows; the preset-count conflict (F29) is still live on the official page, and image assets still reference `4-00675-02X` (I-6). |
| 9 | https://kanlerxz87-cyber.github.io/Zone1/ (cache-busted) | Deployed landing page | Disclosure bar present; headline "Three supplied Amazon links: product identity not yet confirmed"; KPIs 0 / 42 / 1 / 31; commercial-summary rows all carry source links; candidate ASINs labelled "(unconfirmed)". |
| 10 | …/flagged.html (cache-busted) | Deployed Flagged page | "31 Open items", "3 Hard source conflicts", "0 Values guessed", "100% Asserted values sourced"; every table row carries an official source link. |
| 11 | …/compliance.html (cache-busted) | Deployed compliance page | Requirement register C1–C8+ each with verbatim quote and official source link (OA §5 wording, §2(b) price rule, §6(t) review rule, §6(y) price-tracking ban, 16 CFR §255.5(a)). |
| 12 | …/products/chefman-8qt-turbofry.html (cache-busted) | Deployed product page | Candidate-ASIN labelling, "How this review was produced" (FTC no-untried-experience note), spec rows with S12/S13/S16 links, Hi-Fry row blank + Unverified with the conflict explained. |

---

## 3. Result

* **No stored value was found to be wrong** in any row this session re-read against its official
  source. Routine drift only (live review counters already covered by F19).
* **No new factual defect** was found in the repo or the deployed site; no `data/*.json` value was
  changed; no generated page needed regeneration beyond what `build.py` already reproduces.
* **Observation (non-blocking, not changed):** on the product cards, the S17 source badge for the
  Emeril and Chefman-8Qt links hrefs to `link.amazon/B04G1MEwY` because S17 is a single registered
  source covering all three short links (its title lists all three). Cosmetic; the registered-source
  model allows one URL per source id.
* **Open items remain open** exactly where the board left them: token→product identity unconfirmed
  (F14–F16/F21), Associates tag not observable (F6), Chefman 8 Qt 450 °F vs 400 °F official-vs-official
  conflict (F3), Emeril five-way preset count (F29), `link.amazon` provenance (F16), and the rest —
  all published on `flagged.html` with source links, none blocking.
* Parallel session `sess-840a25d3` (T22) verified the disclosure wording, §2(b) and 16 CFR 255.5 on
  the same day; this session verified the commission table, OA date, all three brand pages, all three
  short links and the deployed site. The two passes are complementary and do not overlap.

**Sources:** every URL in the table above, fetched by this session on 2026-11-14 (UTC), plus the
repo's registered source ids S1–S24 in `data/sources.json`.
