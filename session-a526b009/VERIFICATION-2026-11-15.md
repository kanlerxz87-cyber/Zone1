# Verification round 9 — session `arena-a526b009` (2026-11-15 UTC)

**Branch:** `arena/a526b009-zone1` (base `cacdb85`, rebased onto `73f8d79` = merge of PR #69).
**Method:** every source below was fetched live by this session on 2026-11-15 through the page-fetch
tool (shell `curl` in this sandbox cannot leave GitHub/npm/PyPI — a constraint already recorded by
session 22f43836). Values were compared character-for-character against the stored JSON. Nothing was
inferred; a mismatch would have been blanked and flagged, not reconciled by guesswork.

## 1. Sources re-read live (all official)

| # | Source | What was checked | Result |
|---|--------|------------------|--------|
| 1 | https://link.amazon/B04G1MEwY | redirect destination + served `<title>` | → `amazon.com/dp/B0CDY277D3?…lv=shuf…plpRedirect=mhFallback`, fresh `srctok-6c31d96765b8adfb`; title "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black" — **matches `data/products.json` exactly** (round 9, consistent with F10/F15/F36) |
| 2 | https://link.amazon/B02NbDxp3 | same | → `/dp/B09B7SB46R`, `srctok-4796bf563b804868`; title "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included" — **matches the 2026-11-15 stored value exactly** |
| 3 | https://link.amazon/B00hJ57DV | same | → `/dp/B08DKYBTPH`, `srctok-33a7001c2f183379`; title "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel" — **matches exactly** |
| 4 | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | Table 1 + Bounty table, read without login | **all 11 rows match `data/compliance.json` `commission_table`** (10.00 / 5.00 / **4.50 Kitchen** / 4.00 / 3.00 / 2.50 / 2.00 / 1.00 / 0.00 / 0.00 Coach / 4.00 All Other), long category labels verbatim. Bounties: Prime Free Trial **$12.00**, Prime Paid Membership $12.00, Prime Video Free Trial **$2.00**, Prime Video First Stream **$5.00**, Prime Video Stream **$0.25** — all match `bounty_examples` |
| 5 | https://affiliate-program.amazon.com/help/operating/agreement | version stamp + §1 | "**Updated:** October 15, 2025" ✓; §1 "The links must properly use the special '**tagged**' link formats we provide… (Special Links)" ✓ |
| 6 | https://affiliate-program.amazon.com/help/operating/policies | version stamp + the sections this site quotes | "**Updated:** April 14, 2026" ✓. Verbatim re-read today: **§2(b)** Associates ID `XXXXX-##` in every link URL; price/availability only if Amazon serves the link or via Creators/PA API; comparison-format lowest-new/lowest-used rule; no per-user sub-tags · **§3(e)** cookie/pixel disclosure · **§6(g)** no incentives for using Special Links · **§6(t)** no customer reviews/star ratings unless obtained via Creators/PA API · **§6(u)** no self-purchase · **§6(v)** no cloaking · **§6(w)** no link shortening that obscures linking to Amazon · **§6(y)** "your Site must not have price tracking and/or price alerting functionality" |
| 7 | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | disclosure rules | "Place it so it's **hard to miss**" ✓; "You can't talk about your experience with a product you haven't tried" ✓; dated November 2019 ✓ |
| 8 | https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255/section-255.5 | rule text + currency | §255.5(a) first sentence matches the `data/compliance.json` C4 `quote` **verbatim**; "up to date as of 11/12/2026", source 88 FR 48102 (July 26, 2023) ✓ |
| 9 | https://chefman.com/products/turbofry-touch-dual-window-air-fryer (S10) | **every stored 6 Qt spec row** against the live spec table | Capacity 6 Qt / 5.67 L ✓ · 200–450°F / 95–235°C ✓ · Max temp 450ºF with Hi-Fry ✓ · dims 13.38 × 11.81 × 10.63 in ✓ · 13.3 lbs / 6.03 kg ✓ · 1700W/120V ✓ · model RJ38-SQPF-3TDB-2W ✓ · cETL + 1-year assurance ✓ · matte-black ✓ · interior light ✓ · dual windows ✓ · nonstick dishwasher-safe ✓ · 4.6 ★ / **1305** reviews ✓ · $119.99 list on the price ladder ✓ · preset count still **not stated** (stored blank stays correct) |
| 10 | https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1 (S12) | **every stored 8 Qt spec row** | Max temp 400ºF ✓ · 4 cooking presets ✓ · 200–400°F ✓ · 8 Qt 7.57 L ✓ · dims 15.4 × 12.6 × 13.5 in ✓ · 12.8 lbs / 5.8 kg ✓ · model RJ38-SQSS-8T ✓ · 1700W/120V ✓ · cETL + 1-year ✓ · 4.6 ★ / **716** reviews ✓ · auto-shutoff ✓ · **Hi-Fry/450 °F row correctly still blank** (page documents 400 °F max — F3/F33 conflict preserved, no value asserted) |
| 11 | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 (S14) | **every stored Emeril spec row on the page** | $199.99 ✓ · model 4-00675-02A-VN ✓ · 2.6 ★ / 25 reviews ✓ · "25 Cooking Pre-sets" spec block ✓ · "24 one-touch cooking presets" description ✓ · "10-In-1" heading ✓ · `11-in-1_convection_oven_in_action.png` carousel asset still present (F29 evidence live) ✓ · 16.9″D × 15.8″W × 14.8″H ✓ · 24.6 L ✓ · 120 volts ✓ · dual-speed fan ✓ · 26-Qt / 4–6 people ✓ · "1-Years Warranty" ✓ · "7 premium accessories" ✓ · FAFO-001 manual link ✓ · placeholder "KeyFeatures"/FAQ copy still on the page (known I-16, not re-asserted) |

**Result: no stored value was found wrong. No data file was changed by this pass.**

## 2. Line-by-line structural review of the published root build (X2)

| Check | Method | Result |
|---|---|---|
| Disclosure on every page | exact OA §5 sentence searched in all 28 root-build pages | **28/28 present** |
| Internal links + fragments | every `href` resolved against disk, `#fragments` checked against target `id=` | **0 broken** (a first run reported 28 false positives from `data:image/svg+xml` logo URIs — checker corrected, not the site) |
| Orphan pages | linkers-of-record across all 28 pages, paths normalized | **0 orphans** (404.html intentionally unlinked); `decision-gate.html` and `marketing-directions.html` each linked from `questions.html` and `suggestions.html` |
| Count consistency | landing vs flagged vs executive summary | **45 open irregularities / 45 Open items / 45 Open flag rows** — all agree; landing also states "48 recorded … 45 distinct rows" ✓; 41 verified spec values + 2 unconfirmed = 43 ✓; 31 sources ✓ |
| Flag IDs | distinct IDs parsed from `flagged.html` | F1–F45, no duplicates (the `F08` string on the page is a cross-reference to the **s2 annex** register, correctly attributed, not a duplicate) |
| Sitemap/robots | 27 `<loc>` entries, all files exist; robots.txt points at the sitemap | ✓ |
| Conflict markers | repo-wide scan | **0** |
| Working tree | after `python3 build.py` | clean — build reproducible, CI gate will pass |

## 3. Brief-coverage review (what the brief asked for, and where it lives)

| Brief requirement | Where it is | State |
|---|---|---|
| Polished marketing landing page | `index.html` (editorial buyer guide, T19/W5 pass) | live |
| Subpages organized by category | `categories/kitchen-appliances.html` + 3 product pages | live |
| Dashboard-style tables, findings | `data.html`, `compare.html`, `flagged.html`, `reverification.html` | live, 0 unsourced rows |
| Catchy/trendy articles, organic traffic | `articles/` — 8 SEO-targeted pieces + hub, `sitemap.xml`, `robots.txt`, canonical URLs + `rel="sponsored"` (PR #69) | live |
| Not "AI slop" | editorial rules table in the articles hub; anti-slop rules in suggestions SG register; buyer-first landing copy | live |
| Suggestions section to review before implementing | `suggestions.html` — SG-01…SG-17, options + "Your choice" column, nothing implemented | live |
| Questions/information gaps before decisions | `questions.html` (Q-01…Q-14) + `decision-gate.html` | live |
| Executive summary | `executive-summary.html` (decision-ready, current counts) + `EXECUTIVE-SUMMARY.md` (dated audit trail) + `EXECUTIVE-SUMMARY-PASS9.md` | live |
| Line-by-line repo review, irregularities flagged | `flagged.html` (45 open items, each with source/evidence links), `REVIEW.md`, this file | live |
| Every table row sourced; blank + flagged if not | `scripts/source_rows.py --check` → **0 unsourced**; `verify.py` → **0 errors** | enforced by CI |
| Coordination with parallel sessions | `COORDINATION.md` claim X1–X4 pushed before any other edit | done |

## 4. Gates re-run on the rebased branch (all green)

```
python3 build.py                 → 28 pages, exit 0, second run byte-identical
python3 verify.py                → 0 errors (pre-existing s2 external-host WARNs only)
bash scripts/ci-check.sh         → OK · 33 tests · data audit clean · S2 current · 5,384 links / 0 broken
python3 research/check_research.py → OK
python3 scripts/verify_site.py   → ALL CHECKS PASSED (382 assertions)
python3 scripts/build_s2_site.py --check → current
python3 scripts/source_rows.py --check   → 0 rows unsourced
repo-wide conflict-marker scan   → 0
```

## 5. Irregularities found by this pass

**None new.** Every observation maps to an existing published flag (F1–F45): identity/tag
unconfirmed (F14–F16/F21/F6), Chefman 8 Qt 450 °F official-vs-official conflict (F3/F33), Emeril
five-way preset count (F29), s2 external-host warnings, the legacy `EXECUTIVE_SUMMARY.md`
contradictions (F34). This pass **changed no value and added no flag**, because nothing it
re-read contradicted the site.

Overlap note (not a conflict): session `22f43836` (W7, PR #69) ran its own round 9 today on the
short links, commission table, Program Policies and Google link-qualification policies, and fixed
canonical URLs / `rel="sponsored"`. This session's round independently agrees with all of its
results and adds the full manufacturer spec-table sweep, the OA/FTC/eCFR reads, and the
structural audit above. Both records are kept in `COORDINATION.md`.
