# Line-by-line verification pass — session `arena/91d0552e-zone1`

**Date:** 2026-11-14 (UTC) · **Branch:** `arena/91d0552e-zone1` · **Base at start:** `29e4804`, rebased onto `6616ca9`
**Performed by:** sess-91d0552e (COORDINATION.md task T18)

## Method

Every fact re-checked below was fetched **live from its official URL on 2026-11-14** and compared
character-for-character against the value stored in `data/*.json`. Nothing was taken from a prior
session's transcript. Where a value could not be confirmed it is left blank rather than inferred.

Sources re-read this pass: the three supplied `link.amazon` tokens (S17), the Amazon detail pages
they land on (S16), the Associates Program Operating Agreement (S1), the Standard Commission Income
Statement (S3), and the three brand product pages (S10 Chefman 6 Qt, S12 Chefman 8 Qt, S14 Emeril 26 QT).

---

## 1. Short-link resolution — three tokens, re-fetched

Each link was followed once and the resolved URL and page `<title>` recorded.

| Supplied link | Resolved URL | Page `<title>` (verbatim) | Matches stored ASIN? |
|---|---|---|---|
| `https://link.amazon/B04G1MEwY` | `https://www.amazon.com/dp/B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black | ✅ `B0CDY277D3` |
| `https://link.amazon/B02NbDxp3` | `https://www.amazon.com/dp/B09B7SB46R` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals. | ✅ `B09B7SB46R` |
| `https://link.amazon/B00hJ57DV` | `https://www.amazon.com/dp/B08DKYBTPH` | Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel | ✅ `B08DKYBTPH` |

**Verdict: confirmed.** All three titles match the stored `amazon_listing_title` values exactly,
including the Emeril title's trailing full stop. This is the **fifth** independent observation round
across sessions on 2026-11-13/14 (previous: sess-105bc29e, sess-81495d2d, sess-cb2cfa7c, arena/1dcaaafc).

**What this does and does not establish.** The *destination* of each token is reproducible. It does
**not** establish that the destination is the product the operator intended, nor that an Associates tag
is attached — the tag is hidden by the shortener. Both remain unconfirmed (F6, F14–F16, F21).

The landing URLs again carried `lv=shuf`, `btn_ref=srctok-…` and `plpRedirect=mhFallback`. The two
readings of those markers are both published; see F21.

---

## 2. Operating Agreement (S1)

Fetched `https://affiliate-program.amazon.com/help/operating/agreement`.

* Page header reads: **"Updated: October 15, 2025 (Current Associates, see what's changed.)"**
  → matches the stored `page_version` for S1 exactly.
* §1 "Description of the Associates Program" present; *Special Links* and *Program Content* defined as quoted.
* §2 "Associates Program Compliance Requirements" present.
* §3 "Amazon Customers" present — including *"Our customers are not, by virtue of your participation in
  the Associates Program, your customers."*

**Verdict: confirmed.** The disclosure requirement quoted as C1 comes from §5, which is further down the
same document; it was verified by earlier passes on 2026-11-13/14 and is unchanged on this page version.

---

## 3. Standard Commission Income Statement (S3)

Fetched `https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ`. **Publicly readable
without any login.**

All **11 rows** of "Table 1 – Fixed Standard Commission Income Rates for Specific Product Categories"
match the stored `commission_table` exactly, in order:

| Category | Published rate | Stored |
|---|---|---|
| Luxury Beauty, Luxury Stores Beauty, Amazon Explore | 10.00% | ✅ |
| Digital Music, Physical Music, Handmade, Digital Videos | 5.00% | ✅ |
| Physical Books, **Kitchen**, Automotive | **4.50%** | ✅ |
| Amazon Fire Tablet Devices … Handbags & Accessories | 4.00% | ✅ |
| Toys, Furniture, **Home**, … Amazon Coins | **3.00%** | ✅ |
| PC, PC Components, DVD & Blu-Ray | 2.50% | ✅ |
| Televisions, Digital Video Games | 2.00% | ✅ |
| Amazon Fresh, … Health & Personal Care | 1.00% | ✅ |
| Gift Cards; Wireless; … Amazon Pay Places | 0.00% | ✅ |
| Coach | 0.00% | ✅ |
| All Other Categories | 4.00% | ✅ |

Bounty spot-checks also match: Prime Free Trial **$12.00**, Prime Paid Membership **$12.00**,
Prime Video Free Trial **$2.00**, Prime Video First Stream **$5.00**, Prime Video Stream **$0.25**.

**Verdict: confirmed, 11/11 rows.** Air fryers are still **not named anywhere** in the table, so the
per-product rate remains unconfirmed and the site continues to show candidate rows only — correct.

> **Correction to note.** The separate document `EXECUTIVE_SUMMARY.md` (a legacy build's summary, still
> served at the site root) states that "the official commission schedule redirected to a sign-in page."
> That is **not** the case today: this pass read the full rate table without any session. See F28.

---

## 4. Brand product pages — all three re-read

### 4.1 Chefman 6 Qt Dual-Window (S10) — `RJ38-SQPF-3TDB-2W`

`https://chefman.com/products/turbofry-touch-dual-window-air-fryer`

| Field | Observed 2026-11-14 | Stored | Verdict |
|---|---|---|---|
| Model number | `RJ38-SQPF-3TDB-2W` | same | ✅ |
| Capacity | 6-quart (two baskets) | 6 Qt / 5.67 L | ✅ |
| Max temp | "Max temp: 450ºF/ 235ºC with Hi-Fry function" | 200–450 °F / 95–235 °C | ✅ |
| List price | $119.99 (with promo variants $108/$90/$84/$102/$96/$72) | $119.99 | ✅ |
| Review widget | **1,305 Reviews** | 1,305 (dated) | ✅ (unchanged since 2026-11-14 morning; see F19 for drift) |

### 4.2 Chefman 8 Qt TurboFry Touch (S12) — `RJ38-SQSS-8T`

`https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1`

| Field | Observed 2026-11-14 | Stored | Verdict |
|---|---|---|---|
| Model number | `RJ38-SQSS-8T` | same | ✅ |
| Temperature range | "precise temperatures ranging from 200–400°F" | 200–400 °F | ✅ |
| Presets | "presets for fries, chicken, fish, and meat" | 4 food presets | ✅ |
| List price | $119.99 | $119.99 | ✅ |
| Review widget | **716 Reviews** | 716 (dated) | ✅ |

**F3 remains live.** The Amazon listing title (§1 above) advertises **"450°F Hi-Fry Option"** and
"Bake, Dehydrate, Frozen", while the brand's own page documents **200–400 °F** with four food-type
presets. Both are official; neither is asserted. The Chefman 8 Qt's *Hi-Fry / 450 °F mode* row is the
**single blank spec row** in the dataset.

### 4.3 Emeril Lagasse 26 QT French Door (S14) — `4-00675-02A-VN`

`https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360`

| Field | Observed 2026-11-14 | Stored | Verdict |
|---|---|---|---|
| Model number | `4-00675-02A-VN` | same | ✅ |
| Price | $199.99 | $199.99 | ✅ |
| Capacity | "26-Quart Capacity" / "24.6 Liters" | 26 qt / 24.6 L | ✅ |
| Dimensions | `16.9"D x 15.8"W x 14.8"H` | same | ✅ |
| Voltage | 120 volts | 120 V | ✅ |
| Rating widget | **2.6 (25)** | 2.6 / 25 | ✅ |
| Spec block | **"25 Cooking Pre-sets"** | recorded | ✅ |
| Description | "Equipped with **24 one-touch cooking presets**" | recorded | ✅ |
| Marketing label | **"10-in-1"** | recorded | ✅ |

**New detail this pass (strengthens F5, does not resolve it).** The page carries a
**"10-In-1 Versatility"** section that enumerates exactly ten named functions:
Air Fry, Bake, Broil, Defrost, Dehydrate, Grill, Proof, Reheat, Roast, Warm.

So the same product carries **four** different counts on official or near-official surfaces:

| Count | Stated where |
|---|---|
| **10** | brand page "10-in-1" label, corroborated by the ten named Versatility functions |
| **24** | brand page description ("24 one-touch cooking presets"); Amazon listing title ("24 cooking functions"); owner's manual preset chart (S15) |
| **25** | brand page Specifications block ("25 Cooking Pre-sets") |
| **11** | an image asset filename on the brand page (`11-in-1_convection_oven_in_action.png`) |

The site reports the **24 named presets from the owner's manual** and asserts none of the labels.
That remains the correct treatment and is unchanged by this pass.

---

## 5. Summary of this pass

| Check | Result |
|---|---|
| Short-link destinations (3) | ✅ confirmed — 5th observation round |
| Operating Agreement version | ✅ confirmed — "Updated: October 15, 2025" |
| Commission table (11 rows) | ✅ confirmed 11/11, publicly readable |
| Chefman 6 Qt page | ✅ confirmed |
| Chefman 8 Qt page | ✅ confirmed — F3 conflict still live |
| Emeril 26 QT page | ✅ confirmed — F4/F5 conflicts still live, plus new detail |

**No stored value was found to be wrong.** Two defects were found in *surrounding documents* rather than
in the dataset, and are published as **F28**:

1. `research/build_research.py` points readers to "the root site's Flagged page … id F19" (product titles
   / §6(a)) and "id F20" (cookie disclosure). Those IDs are correct **in `data/flags.json`**, but on the
   **root** Flagged page F19 is "brand-site review counts move" and F20 is "six parallel builds". The
   cross-reference is broken because the register is described as "shared" when the ID spaces do not align.
2. `EXECUTIVE_SUMMARY.md` (legacy, still served at the site root) asserts "Identity verified" and that
   "the official commission schedule redirected to a sign-in page". Both are contradicted by this pass:
   the site's current position is **0 verified product identities** (F14–F16, F21), and the commission
   schedule is publicly readable (§3 above).

## 6. Gates re-run after the rebase onto `6616ca9`

* `python3 build.py` → 14 pages, and a second run leaves `git status` clean (reproducible).
* `python3 verify.py` → 92 pages checked · 43 spec rows (42 verified, 1 blank+flagged) · 24 sources · **0 errors**.
* `python3 scripts/check_links.py` → 4,030 links · 0 broken in the 13 pages owned by this build
  (+79 inherited pages reported as advisory, not blocking).
* `python3 research/check_research.py` → OK (no broken links, no unsourced rows, disclosures present).
* `python3 scripts/build_s2_site.py --check` → build current, 16 files.

**After F28 was added,** the flag register moved from 25 to **28** rows (24 programme + 4 product). The flag was originally numbered F25 by this session; it was renumbered to **F28** during the rebase onto `fcc7f9b` because session `arena/6ecdb4e4-zone1` (I7, PR #34) had already published an unrelated issue as F25, and the two would otherwise have shared one ID on the same page.
`flagged.html` and `executive-summary.html` both compute that number from the register, so they updated
automatically; the hand-written line in `EXECUTIVE-SUMMARY.md` §10.6 was corrected to match. That line was a
merge of two independent corrections — this pass supplied the 42-verified/1-blank split and the 92-page count,
and I7 supplied its own flag-count correction — so both passes' numbers survive.
