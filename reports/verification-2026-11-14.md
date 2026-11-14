# Verification record — 2026-11-14 (session `arena/6ec3c2da`)

**Scope:** a line-by-line re-check of the claims the Zone1 dashboard relies on, against official pages fetched on **2026-11-14 (UTC)**. Board entry: `COORDINATION.md` → "Session `arena/6ec3c2da`" (tasks H1–H5).

**Method.** Each official URL below was fetched with the sandbox page-fetch tool. Observations were recorded as found. Nothing was inferred. Where an official source was not reached, the row says so. Prices were **not** republished: Program Policies §2(b) limits price display to Amazon-served links or the Creators API (see `dashboard/compliance.html`).

**Status key:** **Confirmed** = the official page says it. **Observed** = the official page shows it, but its meaning is not established. **Contradicted** = the official page conflicts with an earlier claim. **Unconfirmed** = no official source reached. **Withdrawn** = an earlier statement this session found unsupported.

---

## 1 · The three supplied links

| # | Supplied link | Final URL after redirect (fetched 2026-11-14) | Product title on the landing page | Status |
|---|---|---|---|---|
| 1.1 | <https://link.amazon/B04G1MEwY> | `https://www.amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&…&plpRedirect=mhFallback` | “CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows…” | **Observed.** Mapping to the token is **Unconfirmed** (H-08). |
| 1.2 | <https://link.amazon/B02NbDxp3> | `https://www.amazon.com/dp/B09B7SB46R?lv=shuf&btn_type=ss&…&plpRedirect=mhFallback` | “Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven…” | **Observed.** Mapping **Unconfirmed**. |
| 1.3 | <https://link.amazon/B00hJ57DV> | `https://www.amazon.com/dp/B08DKYBTPH?lv=shuf&btn_type=ss&…&plpRedirect=mhFallback&th=1` | “Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option…” | **Observed.** Mapping **Unconfirmed**. |

**Note on `link.amazon`.** The domain is not named in the Associates Operating Agreement §1 “Special Links” definition, which says links “must properly use the special ‘tagged’ link formats we provide” ([Operating Agreement, updated 2025-10-15](https://affiliate-program.amazon.com/help/operating/agreement)). Its provenance is unconfirmed (H-03). The earlier dashboard sentence “link.amazon is not an official Amazon link format” went further than the evidence and was corrected.

## 2 · The three supplied codes as canonical `/dp/` URLs

| # | URL | Result (fetched 2026-11-14) | Status |
|---|---|---|---|
| 2.1 | <https://www.amazon.com/dp/B04G1MEwY> | “Sorry! We couldn't find that page.” / Page Not Found | **Confirmed** (no product at this 9-character path) |
| 2.2 | <https://www.amazon.com/dp/B02NbDxp3> | Page Not Found | **Confirmed** |
| 2.3 | <https://www.amazon.com/dp/B00hJ57DV> | Page Not Found | **Confirmed** |

**Format.** The supplied tokens are **9 characters** each (`B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`). The three ASINs the links land on are **10 characters** each (`B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`). This is a direct count. The rule that ASINs are 10 characters is **observed** on Amazon's own `/dp/` URLs (H-05). The official help page that states the rule was not re-read this session.

## 3 · The three landing ASINs as direct requests

| # | URL | Result | Status |
|---|---|---|---|
| 3.1 | <https://www.amazon.com/dp/B0CDY277D3> | An existing product page (product title; breadcrumb to Air Fryers). The URL carries `lv=shuf&channelId=500&plpRedirect=mhFallback`. | **Observed.** The same parameters appear on a real product page, so they do **not** show a missing product. This **withdraws** the earlier “random unrelated listing” wording (H-08). |
| 3.2 | <https://www.amazon.com/dp/B09B7SB46R> | Existing product page (Emeril Lagasse 26QT). | **Observed** (same as 3.1). |
| 3.3 | <https://www.amazon.com/dp/B08DKYBTPH> | Existing product page (Chefman 8 Qt TurboFry). | **Observed** (same as 3.1). |

**Prices and ratings on these pages were not republished.** The fetched pages show different prices for the same ASIN in different tiles (for example, a list price of $99.99 for B0CDY277D3 in one tile and $69.97 in another). These figures are volatile and are not used on the site (H-07; Program Policies §2(b)).

## 4 · Commission rates (Amazon Associates)

| # | Claim | Official source (fetched 2026-11-14) | Status |
|---|---|---|---|
| 4.1 | Table 1, Kitchen: **4.50%** | [Standard Commission Income Statement](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) — “Physical Books, Kitchen, Automotive — 4.50%” | **Confirmed** |
| 4.2 | Table 1, Home: **3.00%** | Same page — “Toys, Furniture, Home, Home Improvement, … — 3.00%” | **Confirmed** |
| 4.3 | Table 1, All Other Categories: **4.00%** | Same page — “All Other Categories — 4.00%” | **Confirmed** |
| 4.4 | Table 1 range 0.00%–10.00% | Same page — lowest 0.00% (Gift Cards, etc.); highest 10.00% (Luxury Beauty) | **Confirmed** |
| 4.5 | Category of each ASIN | Not published by Amazon in the sources reached. | **Unconfirmed** (MN-11) |

The page is public (no sign-in) when fetched directly. The earlier log that said the rate card was login-gated (F-04) was superseded before this session and remains superseded.

## 5 · Platform data access (PA-API 5 and Creators API)

| # | Claim | Official source (fetched 2026-11-14) | Status |
|---|---|---|---|
| 5.1 | **PA-API 5 is deprecated.** Calls get HTTP 403 `AccessDeniedException`. | [PA-API 5 Deprecation Notice](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation) | **Confirmed**. **Contradicts** earlier pages that planned on PA-API 5 (H-01). |
| 5.2 | Creators API is the successor. | [Creators API — Welcome](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction) | **Confirmed** |
| 5.3 | Prerequisites: enrolled in Associates; **at least 10 qualifying sales within the past 30 days**; register; generate credentials. | Same page, “Prerequisites” | **Confirmed**. Automated product data is therefore not available to this project today (H-06). |

## 6 · Chefman brand pages (manufacturer reference only)

| # | Claim | Official brand source (fetched 2026-11-14) | Status |
|---|---|---|---|
| 6.1 | TurboFry Touch 6 Qt Dual-Window, model RJ38-SQPF-3TDB-2W: a reference price of **$119.99** is printed beside sale tiers ($108.00, $90.00, $84.00, $102.00, $96.00, $72.00) with “Save 10%–40%”. 1,305 reviews. | <https://chefman.com/products/turbofry-touch-dual-window-air-fryer> | **Observed**. It is the brand’s reference price, not an Amazon price. Mapping to ASIN B0CDY277D3 **Unconfirmed** (H-07). |
| 6.2 | TurboFry Touch 8 Qt Stainless, model RJ38-SQSS-8T: the same $119.99 reference beside the same tiers. 716 reviews. | <https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1> | **Observed** (same as 6.1). Mapping to ASIN B08DKYBTPH **Unconfirmed** (H-07). |

## 7 · Associates disclosure text

| # | Claim | Source | Status |
|---|---|---|---|
| 7.1 | Required wording: “As an Amazon Associate I earn from qualifying purchases.” | Operating Agreement §5 (verified in an earlier session; **not re-read this session**) | **Carried over.** Re-check §5 before publication. |

## 8 · Changes made to the dashboard in this session

| Change | Reason | Flag |
|---|---|---|
| Removed citations to keywordseverywhere.com, barcode.graphics, aruljohn.com, u2l.ai and manuals.plus. Replaced them with official Amazon pages or the Operating Agreement. One row had labelled a keywordseverywhere.com link “official”. | Requirement: every row sourced to an official site. | H-02 |
| Reworded “link.amazon is not an official link format” to “not named in the Operating Agreement §1 Special Links definition; provenance unconfirmed”. | The stronger claim had no official source. | H-03 |
| Withdrew “random unrelated listing” / “shuffle” wording. Replaced it with “existing product page reached through fallback-parameter URLs; mapping unconfirmed”. | Direct request for B0CDY277D3 carries the same parameters (§3). | H-08 |
| “PA-API / PA-API 5” references replaced by Creators API, with a note on the deprecation. | Deprecation notice (§5). | H-01, H-06 |
| Added refresh card to the executive summary. Added flags H-01…H-08 to Flagged for Review §E. Updated the flagged count on the landing page (22 → 30). | Record of this session. | — |

## 9 · Not changed, and why

- **Root site** (`index.html`, `executive-summary.html`, `products/`, `categories/`, `build.py`): it states the three ASINs as “resolved from three short links” and shows derived commission amounts. The root site is generated by `build.py`, which CI checks for reproducibility, and it belongs to the integration owner. It is **flagged** (H-04), not edited.
- **Open PR #9** (`arena/88769516-zone1`) from another session: left untouched.
- **`compliance.html`** quotes Program Policies §2(b) verbatim, including “Creators API or PA API”. The quote is kept as written.

## 10 · Limits of this verification

- Pages were fetched by the sandbox's page-fetch tool, not in a logged-in browser. Amazon may serve different content to different clients. Each observation is dated.
- No Associates account was available, so account-gated data (rate card for a specific product, Creators API responses) could not be checked.
- The three short links were followed to their destinations. Their ownership and intended products were not confirmed. The owner must confirm them.
