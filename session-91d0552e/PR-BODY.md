## What this PR does

Integration pass 6 for session `arena/91d0552e-zone1`, rebased onto `fcc7f9b` (main after PR #34).

### 1. Independent line-by-line re-verification, 2026-11-14 — new file `session-91d0552e/VERIFICATION-2026-11-14.md`

Every fact below was fetched live from its official URL and compared character-for-character against `data/*.json`. **No stored value was found to be wrong.**

| Check | Result |
|---|---|
| 3 `link.amazon` tokens | All three destinations + verbatim page titles match the stored values. 5th independent observation round. |
| Operating Agreement (S1) | Page reads "Updated: October 15, 2025" — matches stored `page_version`. |
| Commission Income Statement (S3) | **11/11 rate rows exact** (Kitchen 4.50%, Home 3.00%, fallback 4.00%) + bounty amounts. **Read without any login.** |
| Chefman 6 Qt (S10) | RJ38-SQPF-3TDB-2W, $119.99, 450 F Hi-Fry, 1,305 reviews |
| Chefman 8 Qt (S12) | RJ38-SQSS-8T, $119.99, 200-400 F, 716 reviews. **F3 conflict still live** (listing says 450 F). |
| Emeril 26 QT (S14) | 4-00675-02A-VN, $199.99, 26 qt / 24.6 L, 2.6 stars (25). **F4/F5 still live.** |

New detail recorded (strengthens F5, does not resolve it): the Emeril page's "10-In-1 Versatility" section enumerates exactly ten named functions, so the product carries four different counts across official surfaces — 10 (label + ten named functions), 24 (description, Amazon title, owner's manual), 25 (spec block), 11 (an image filename). The site reports the 24 named presets from the manual and asserts none of the labels — unchanged and still correct.

### 2. New flag F28 — flag-register ID collision (published on the Flagged page)

1. `research/build_research.py` points readers to "the root site's Flagged page (shared register `data/flags.json` id **F19**)" for the product-titles issue and "id **F20**" for the cookie-disclosure issue. Those IDs are correct *inside* `data/flags.json`, but the root Flagged page is generated from `build.py`'s own `PROGRAMME_FLAGS`, where **F19 = "brand-site review counts move"** and **F20 = "six parallel builds"**. The register is described as "shared" when the ID spaces do not align, so the pointer lands a reader on an unrelated row.
2. `EXECUTIVE_SUMMARY.md` (legacy, still served at the site root) asserts **"Identity verified"** and that **"the official commission schedule redirected to a sign-in page"**. Both are contradicted by this pass: the reconciled position is **0 verified product identities** (F14-F16, F21), and the commission schedule was read in full with **no login** on 2026-11-14.

Not re-keyed, because `data/flags.json` feeds the s2 and docs generators and `research/` is another session's build — re-keying would silently re-point another build's citations. Flagged for the owner to decide.

**ID note:** this was numbered F25 by this session and **renumbered to F28** during the rebase, because `arena/6ecdb4e4-zone1` (I7, PR #34) had already published a different finding as F25.

### 3. Corrected stale counts in `EXECUTIVE-SUMMARY.md`

| Was | Now | Basis |
|---|---|---|
| 40 verified / 3 blank spec rows | **42 verified / 1 blank** | counted against `data/products.json`; two rows were filled from owner's manuals, the only remaining blank is the Chefman 8 Qt Hi-Fry row (F3) |
| 17 open flags (13 programme + 4 product) | **28 open flag rows** (24 programme + 4 product) | counted against `build.py` |
| 91 pages checked | 92 pages | `verify.py` output |

The 10.6 line is a **merge of two independent corrections** — I7 fixed the flag count, this pass fixed the spec-row split and page count — so both survive.

### 4. `EXECUTIVE_SUMMARY.md` reconciliation banner (additive)

The repo root carries two executive summaries with materially different figures. A banner now points to `EXECUTIVE-SUMMARY.md` as the one the site links to, and marks the two superseded statements. **No other session's text was deleted.**

## Sources used (all official, all re-read 2026-11-14)

- https://link.amazon/B04G1MEwY · /B02NbDxp3 · /B00hJ57DV → https://www.amazon.com/dp/B0CDY277D3 · /B09B7SB46R · /B08DKYBTPH
- https://affiliate-program.amazon.com/help/operating/agreement
- https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ (Standard Commission Income Statement)
- https://chefman.com/products/turbofry-touch-dual-window-air-fryer
- https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1
- https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360

## Flagged irregularities (non-blocking, published on the Flagged page)

F28 (above) joins the existing open items. Register moves 25 to **28** rows; both `flagged.html` and `executive-summary.html` compute that number from the register.

## Merge-conflict resolution (protocol 6)

Rebase onto `fcc7f9b` conflicted on 6 files because I7 (PR #34) merged concurrently. **Nothing discarded:**

- `build.py`: I7's F25/F26/F27 kept; this session's flag appended as **F28**.
- `build.py` source cell: **I7's `REPO_EVIDENCE`/`repo_link()` implementation kept**, superseding this session's generic repo link (it maps each repo-observation flag to the specific files evidencing it).
- `EXECUTIVE-SUMMARY.md` section 10.6: both passes' corrections merged.
- `COORDINATION.md`: both boards kept verbatim, marker lines removed, handoff noted.
- Generated HTML regenerated after the data/build merge.

One item needed a force-push of this branch: the rebase rewrote this session's own two commits (`4b65a22`, `33bee64` to `5d596df`, `fd26366`). The remote contained **only** those superseded commits of this session and nothing from any other session, verified with `git log HEAD..origin/<branch>` before pushing with `--force-with-lease`.

## Verification performed

- `build.py` → 14 pages, **byte-identical on re-run** (reproducibility gate).
- `verify.py` → 92 pages · 43 spec rows (42 verified, 1 blank+flagged) · 24 sources · **0 errors**.
- `check_links.py` → 4,079 links · 0 broken in the 13 owned pages (+79 inherited, advisory).
- `research/check_research.py` OK · `build_s2_site.py --check` current · `verify_site.py` 382 assertions ALL PASSED · `ci-check.sh` OK.
- Platform: 33/33 tests · `platform/audit/report.py` AUDIT PASSED (0 warnings).
- Row-source audit: **283/283** data-table rows on the owned root pages carry a link to an official source.
- Every row in `data/*.json` machine-checked for a `source` key: 0 missing, 0 unknown IDs.
- No merge-conflict markers remain anywhere in the tree.
