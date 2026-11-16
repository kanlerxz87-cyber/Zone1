# Verification round 11 — 2026-11-16 (session b23f12f0)

**Branch:** `arena/b23f12f0-zone1` · **Base:** `f3d2d4e` · **Method:** server-side fetch of each
official URL. (`curl` from this sandbox returns `000` for every non-GitHub host, so all reads below
went through the page-fetch tool — the same constraint earlier sessions recorded.)

## Why this round exists

Round 10 ran earlier the same day (session `c334fb1c`, PRs #86/#87) and re-read the three short
links, S2 and the live landing page. It explicitly recorded the following as **not re-read**:
S8 (FTC), S9 (16 CFR 255), the brand pages (S10, S12, S14) and the manuals (S13, S15, S18).

This round re-reads that set, plus S1, S3, S4, the three `/dp/` pages and the two storefront
endpoints. It does not repeat round 10's short-link and S2 reads except where a round-11 result
required it (the three tokens were re-resolved because the Emeril destination is load-bearing for
the value this round added).

## 1. Amazon Associates — programme rules

| Source | URL | What was read today | Stored record | Verdict |
|---|---|---|---|---|
| S1 Operating Agreement | [agreement](https://affiliate-program.amazon.com/help/operating/agreement) | "**Updated:** October 15, 2025" | same date | **confirmed** |
| S2 Program Policies | [policies](https://affiliate-program.amazon.com/help/operating/policies) | "**Updated:** April 14, 2026" | same date | **confirmed** (also read by round 10 today) |
| S3 Commission Income Statement | [Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) | Read in full **with no login**. "Physical Books, Kitchen, Automotive \| 4.50%"; "All Other Categories \| 4.00%" | Kitchen 4.50%, All Other 4.00% | **confirmed** |
| S4 Application Review Process | [review](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) | "at least three within the first 180 days"; "personal orders do not qualify"; "at least 10 posts"; "generally within the last 60 days"; "at least 500" followers; "we aren't able to reassess an application once it's been rejected" | same six figures | **confirmed** |

Table 1 was also read for the bounty table, which the site publishes on the compliance page.

## 2. FTC and eCFR

| Source | What was read today | Verdict |
|---|---|---|
| S8 [Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | "Place it so it's **hard to miss**"; "You can't talk about your experience with a product you haven't tried"; page dated November 2019 | **confirmed** |
| S9 [16 CFR Part 255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) | "Displaying title 16, up to date as of **11/12/2026**. Title 16 was last amended **10/30/2026**." Source note still 88 FR 48102, July 26 2023. TOC lists §255.0–§255.6 including §255.5 Disclosure of material connections | **confirmed** |

## 3. Brand sources

| Source | What was read today | Verdict |
|---|---|---|
| S10 / S32 Chefman 6 Qt Dual-Window | Storefront endpoint: price 119.99, compare-at 119.99, SKU `RJ38-SQPF-3TDB-2W`, 6,582 g / 14.51 lb. Record `updated_at` **2026-11-16T13:25:53-05:00** — i.e. the brand's own store touched this record today | every published 6 Qt value still matches |
| S12 / S33 Chefman 8 Qt TurboFry | Endpoint: 8 Quart price 119.99 / compare-at 119.99, SKU `RJ38-SQSS-8T`, 6,078 g / 13.4 lb; 5 Quart 79.99 / compare-at 99.99, SKU `RJ38-SQSS-5T`. Same `updated_at` | every published 8 Qt value still matches |
| S14 Emeril French Door 360 | Page live; price 199.99, SKU `4-00675-02A-VN`. **New:** the page's own description text (updated **2026-11-16T12:27:19-06:00**) states **"24 one-touch cooking presets"** and **"Included are 7 premium accessories"** — while the separate specification block on the same page still states **"25 Cooking Pre-sets"** | price/SKU confirmed; **new evidence on two open conflicts → F66** |
| S35 Emeril commerce endpoint *(new this round)* | Variant weight **27.04 lb / 12,265 g**; description as above | registered as a **candidate** for Q-06, not published as a product weight — see §6 |

## 4. Amazon listing pages

All three rendered the reduced "Product summary presents key product information" shell, which is
why the model number is unreachable (flag F46 / question Q-01). Titles and breadcrumbs read:

| ASIN | Source | `<title>` read today | Matches stored? | Browse-node breadcrumb |
|---|---|---|---|---|
| B0CDY277D3 | S16 | "Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen" | **yes, character for character** | Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers |
| B09B7SB46R | S28 | "Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, **24 One-Touch Preset Options**, Extra Large Interior, **Six Cooking Accessories Included** : Home & Kitchen" | **yes, character for character** | Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers |
| B08DKYBTPH | S29 | "Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel : Home & Kitchen" | **yes, character for character** | Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers |

**The Emeril page loaded.** Three attempts on 2026-11-15 had been answered by the automated
"Continue shopping" checkpoint, and round 9 recorded that as a per-ASIN block. Today it loaded on
the first attempt. In the same session, B0CDY277D3 — which had loaded cleanly yesterday — was
served the checkpoint on its first attempt and returned the listing only on a retry. **The
checkpoint is intermittent per request, not a property of the ASIN.** That is a correction to a
recorded conclusion and is published as flag **F65**.

## 5. Short links (re-resolved because §4 depends on it)

| Supplied | Resolved to | Tracking markers on the landing URL |
|---|---|---|
| `https://link.amazon/B04G1MEwY` | `/dp/B0CDY277D3` | `lv=shuf`, `btn_ref=srctok-…`, `channelId=704`, `plpRedirect=mhFallback` |
| `https://link.amazon/B02NbDxp3` | `/dp/B09B7SB46R` | same |
| `https://link.amazon/B00hJ57DV` | `/dp/B08DKYBTPH` | same |

Destinations unchanged. No landing URL carries a `tag=` parameter, so attribution still cannot be
confirmed from outside Associates Central (flag F6, question Q-04).

## 6. What this round changed, and what it refused to change

**Changed (3 repairs, 1 fill, 3 new flags):**

1. **Filled one blank cell.** The Emeril "Amazon browse node" row went from blank-and-flagged to
   `Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers`, cited to S28 and
   S17, with the F53 scope limit carried in the note. Verified spec rows: 43 → **44**.
2. **Repaired three duplication defects** (flag F64): Q-11's `what_we_know` carried three entries
   seven times each — 18 entries collapsing to 6, and the sentence "The same breadcrumb does NOT
   settle this question" appeared **14 times** in the rendered `questions.html`; the articles note
   repeated its opening paragraph; one Chefman 8 Qt row cited S29 three times. Order-preserving
   de-duplication, no wording changed. Guard `check_register_duplicates()` added and proven to fire.
3. **Registered S35** and stamped 14 sources with the round-11 read.
4. **Added F64, F65, F66** (renumbered twice: F59/F60/F61 → F61/F62/F63 → F64/F65/F66, because sessions `ad8105b3` and `9fccce0c` published different rows under those numbers in PRs #89 and #93).

**Refused to change:**

- **The Emeril product weight was not published.** S35 reports 27.04 lb / 12,265 g, but the
  endpoint does not say whether that field is the product or the packaged weight, and the same
  brand family already shows the two figures diverging for both Chefman models (F51). Q-06's own
  instruction is to leave the cell blank rather than convert a shipping weight. The figure is
  recorded there as a candidate with its source.
- **The Emeril preset count stayed at 24.** The brand now says 24 in its description and 25 in its
  spec block. 24 has the manual and the Amazon title behind it, but the brand has not withdrawn
  the 25, so the conflict is published as live (F66) rather than settled by majority.
- **No commission rate was asserted.** All three browse nodes being identical does not tell you
  which commission category Amazon applies (F53, Q-11).

## 7. Gates

| Gate | Result |
|---|---|
| `python3 build.py` | exit 0 |
| `python3 verify.py` | 115 pages · 46 spec rows (**44 verified**, 2 blank+flagged) · 35 sources · 0 errors · 0 external warnings |
| `bash scripts/ci-check.sh` | 33 unit tests OK · data audit clean · 6,386 links / 0 broken |
| guard proof | injected duplicate → exit 1; clean tree → exit 0 |

## 8. Not re-read in this round

The owner's manuals (S13, S15, S18) were not re-opened; their last read stands at 2026-11-14/15.
The parallel builds in `site/`, `s2/`, `research/`, `docs/`, `dashboard/` and `annex-88769516/`
keep their own verification records and were not touched.
