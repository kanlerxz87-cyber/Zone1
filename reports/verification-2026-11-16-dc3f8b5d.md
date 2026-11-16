# Verification pass 11 (V11) — session dc3f8b5d — 2026-11-16 (UTC)

**Scope:** live re-read of the three Amazon short links the project is built on, compared
line by line with `data/products.json`; run of every build, verify and test gate; publication
of this record. **No product value, site page, source row or flag was changed.**

## 1. Short links — live read on 2026-11-16

Each short link was followed with a live HTTP request. The final page's `<title>` and the ASIN
in its canonical URL were compared with the recorded values.

| Short link (supplied) | Final ASIN (live) | Live listing title (page `<title>`) | Recorded ASIN in `data/products.json` | Recorded listing title | Result |
|---|---|---|---|---|---|
| https://link.amazon/B04G1MEwY | B0CDY277D3 | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black | B0CDY277D3 | identical | match |
| https://link.amazon/B02NbDxp3 | B09B7SB46R | Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included | B09B7SB46R | identical (the 2026-11-15 read; the older wording is kept as `v_previous`) | match — see flag F38 |
| https://link.amazon/B00hJ57DV | B08DKYBTPH | Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel | B08DKYBTPH | identical | match |

**Source links for manual review** (the pages as they resolved today; the canonical product pages are the `/dp/` URLs):
- https://www.amazon.com/dp/B0CDY277D3
- https://www.amazon.com/dp/B09B7SB46R
- https://www.amazon.com/dp/B08DKYBTPH

**Not re-read in this pass:** prices, star ratings and review counts. Amazon shows them as volatile
values; they are recorded with their read dates in `data/products.json` and were not refreshed here.

**Naming note (not an irregularity in the data):** the dataset's display name for the 6 qt
product is "TurboFry Touch 6 Qt. Dual-Basket / Dual-Window Air Fryer", while the live listing
reads "CHEFMAN 6 Quart Dual Basket Air Fryer Oven …". The dataset keeps the listing title in
`amazon_listing_title`, so the Amazon wording is still available for comparison.

## 2. Gates run on this branch (before and after any change)

| Gate | Command | Result |
|---|---|---|
| Site build | `python3 build.py` | exit 0; rebuild leaves the working tree byte-identical (`git status` clean) |
| Verification | `python3 verify.py` | 34 sources declared, 0 external warnings, 0 errors |
| Engine tests | `python3 -m unittest discover -s platform/tests -t platform -p "test_*.py"` | 33 tests OK |
| Data audit | `python3 platform/audit/report.py` | AUDIT PASSED, 0 warnings |
| Link and source coverage | `python3 scripts/check_links.py` | link check ok, 6,792 links (advisory, inherited pages included) |
| GitHub Pages | `gh api repos/kanlerxz87-cyber/Zone1/pages` | status `built`; `https://kanlerxz87-cyber.github.io/Zone1/` |
| Most recent deploy | `gh run list` on `main` | run 43931810929 "Build, verify and deploy to GitHub Pages": `success` (merge of PR #93) |

## 3. Irregularities and flags

- **No new irregularity was found** in this pass. The three short links still resolve to the
  ASINs recorded in the dataset, and the listing titles match.
- **Existing flags still open and unchanged** (none can be closed from outside the account
  holder's browser or from official Amazon pages alone): F1/F2 (which manufacturer model each ASIN
  ships under; Amazon does not publish model numbers on the ASIN), F6 (the Associates tag inside
  the short links), F3 (the 450 °F conflict on the 8 qt product), F4/F5 (the Emeril preset count),
  F38 (the Emeril title changed between the 2026-11-14 and 2026-11-15 reads, and this read is
  identical to the newer one).
- The full, canonical flag register is on `flagged.html` on the live site.

## 4. Branch and protocol

- Branch: `arena/dc3f8b5d-zone1` (fixed for this session). The brief's `session-<id>/<task>`
  naming was not used because the platform assigns this branch name.
- Board claim for V11 committed and pushed before the work (commit `c054b66`).
- Files touched by this pass: `reports/verification-2026-11-16-dc3f8b5d.md` (new) and
  `COORDINATION.md` (board row and claim log). No other file was edited.
