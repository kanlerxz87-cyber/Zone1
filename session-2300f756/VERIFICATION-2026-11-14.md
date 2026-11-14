# Verification record — `arena-2300f756` (T23, integration pass 8, 2026-11-14 UTC)

Record-only pass. Branch `arena/2300f756-zone1`, base `f45374b` (rebased onto current `main`
before the PR — see the conflict log). **No `data/*.json`, no `build.py`, and no other
session's file was changed by this pass.** Evidence below was collected by this session
on 2026-11-14; nothing was copied from another session's record on trust.

---

## 1. Local gates (all run by this session)

| Gate | Command | Result |
|---|---|---|
| Root build reproducible | `python3 build.py` | 21 pages regenerated; working tree byte-identical afterwards (`git status`/`git diff` empty) |
| Root verifier | `python3 verify.py` | `errors: 0` (99 pages). Advisory allow-list WARNs only, all on `s2/pages/*` (external hosts `advertising.amazon.com`, `api.github.com`, `sell.amazon.com`) — informational, not errors; identical advisory class recorded by earlier passes |
| Platform regression tests | `python3 -m unittest discover -s platform/tests -t platform` | `Ran 33 tests ... OK` |
| Data-integrity audit | `platform/audit/report.py → audit_data()` | `warnings: 0` |
| S2 build current | `python3 scripts/build_s2_site.py --check` | `build current: 16 files` |
| Research checker | `python3 research/check_research.py` | `OK — no broken links, no unsourced rows, disclosures present on every page` (12 published pages) |
| Link check | `python3 scripts/check_links.py` | `link check ok · 4477 links · 13 pages owned by this session (+86 inherited, advisory)` |
| Annex rebuild + verify | `python3 scripts/build_site.py` then `python3 scripts/verify_site.py` | `382` assertions, `ALL CHECKS PASSED`; rebuilt `site/` byte-identical (no diff) |
| Repo-wide conflict-marker scan | `grep -rln '^<<<<<<< \|^>>>>>>> '` over html/md/py/json/js | clean |

## 2. Live official-source re-verification (fetched 2026-11-14 by this session)

### Round 7 — the three `link.amazon` short links

Each URL was fetched fresh; the destination page title as served is quoted below.

| Token | Landed on | Page title as served (verbatim) | Matches stored value? | Fallback markers |
|---|---|---|---|---|
| `B04G1MEwY` | `amazon.com/dp/B0CDY277D3` | "Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen" | **Yes** — ASIN and title match `data/products.json` (S16/S17) | `lv=shuf`, `plpRedirect=mhFallback`, `srctok-…`, `channelId=704` all present |
| `B02NbDxp3` | `amazon.com/dp/B09B7SB46R` | "Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals. : Home & Kitchen" | **Yes** | same markers present |
| `B00hJ57DV` | `amazon.com/dp/B08DKYBTPH` | "Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel : Home & Kitchen" | **Yes** | same markers present |

Observations (all consistent with open flags — nothing new to flag):

* The **450 °F Hi-Fry / 4-in-1** wording is still live on the B08DKYBTPH listing, while the
  brand page/manual for `RJ38-SQSS-8T` documents 200–400 °F — the F3/F33 conflict is still open,
  and this pass asserts neither value.
* The Emeril listing title still says **"24 cooking functions"** — additional round-7 evidence
  for F29 (the preset-count inconsistency across official sources). No count is asserted anywhere.
* Each fallback landing also serves a shuffle carousel ("Customers who viewed this item also
  viewed" with different products), consistent with the `lv=shuf` marker — the behaviour the
  `platform/resolver/link.py` guard refuses to attribute.
* No `tag=` parameter is observable from outside Associates Central (F6/F21 unchanged).

### eCFR (US Government Publishing Office / Office of the Federal Register)

| Source | What was read | Verdict |
|---|---|---|
| [16 CFR 255.5 — Disclosure of material connections](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255/section-255.5) | eCFR content "up to date as of 11/12/2026", Title 16 last amended 10/30/2026; Part 255 = "Guides Concerning Use of Endorsements and Testimonials in Advertising"; authority 15 U.S.C. 41-58; source 88 FR 48102 (July 26, 2023) | Page live and current; matches the site's registered source for 16 CFR 255.5 |
| [16 CFR Part 465 — Rule on the Use of Consumer Reviews and Testimonials](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465) | Full TOC read: §465.1 definitions, §465.2 fake/false reviews, §465.4 buying positive/negative reviews, §465.5 insider reviews, §465.6 company-controlled review sites, §465.7 review suppression, §465.8 misuse of fake social-media-influence indicators, §465.9 severability; authority 15 U.S.C. 57a; source 89 FR 68077 (Aug. 22, 2024) | Page live and current — **first live re-read of the Part 465 citation by a recent pass**; confirms the `research/` source register |

## 3. Live GitHub Pages audit

| Check | Result |
|---|---|
| Pages configuration (`gh api repos/…/pages`) | `status: built`, `html_url: https://kanlerxz87-cyber.github.io/Zone1/`, source `main` / `/` (legacy), HTTPS enforced |
| Latest Pages build (`…/pages/builds/latest`) | `status: built`, commit `99b6fb584b4c297cc563f9d05bccbe2fb2725538` (= origin/main tip at check time), created 2026-11-14T19:14:34Z, `error: null` |
| Workflows on `origin/main` at that commit | `CI` ✓ · `Build, verify and deploy to GitHub Pages` ✓ · `Verify verification annex (site/)` ✓ · `pages build and deployment` ✓ (PR #45 push run) |
| Live `/flagged.html` | Serves the current register: **35 Open items**, 3 hard source conflicts, 0 values guessed, 100% of asserted values sourced; OA §5 disclosure bar ("As an Amazon Associate I earn from qualifying purchases.") present; F1–F13 rows render with per-row source links |
| Live `/articles/index.html` | 5 articles rendered with breadcrumbs and disclosure; editorial-rules table cites S1, S2, S8, S9, S14 with live links |

## 4. New findings / irregularities (advisory, no data changed)

1. `verify.py` advisory WARN class on `s2/pages/*` for external hosts outside the allow list —
   pre-existing, informational, unchanged from earlier passes.
2. `check_links.py` prints ~172 advisory `Blocked/same` note rows for `dashboard/analysis.html`
   table cells — advisory only; the gate itself reports `link check ok`.
3. Deploy-cache behaviour: the Pages `builds/latest` commit matched `origin/main` at check time,
   and both live pages fetched returned the current content (35 items). No stale-CDN artefact
   was observed in this pass.

No stored value was found to be wrong. No new flag was required.

## 5. Sources used by this pass (all fetched live 2026-11-14)

| URL | Verified |
|---|---|
| https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3 · https://link.amazon/B00hJ57DV | Round-7 destinations, served titles, fallback markers |
| https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255/section-255.5 | 16 CFR 255.5 citation, currency, authority |
| https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465 | 16 CFR Part 465 structure, citation, currency |
| https://kanlerxz87-cyber.github.io/Zone1/flagged.html | Live deploy: flag register + disclosure |
| https://kanlerxz87-cyber.github.io/Zone1/articles/index.html | Live deploy: articles layer |
| `gh api repos/kanlerxz87-cyber/Zone1/pages` + `/pages/builds/latest` | Deploy state (status, commit, error) |
| `gh run list --branch main` | CI/Pages/annex workflow results on main |
