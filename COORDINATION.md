# COORDINATION — Zone1 (Amazon affiliate platform)

Shared task board for concurrent agent sessions. Read this before starting any work.

**Protocol**

1. Claim a task by adding your session ID + file scope below, then commit and push the claim immediately.
2. Never start a task another session has claimed. Keep scopes non‑overlapping.
3. Each session works on its own branch `session-<id>/<task>` and edits only files inside its claimed scope.
4. If you need a file owned by another session, log a request here — do not edit it.
5. Shared outputs (`data/*.json`, `index.html`, navigation in `build.py`) are changed **only** by the final integration session, after all other tasks are done.
6. Small, frequent commits. `git pull --rebase` before every push. If you hit a merge conflict: stop, resolve without discarding the other session's work, and log it here.
7. A claim more than 60 minutes old with no commits may be taken over by another session — note the handoff in the log.
8. Never mark anything verified without checking it against an official source, and link that source.

Column key: **status** = `unclaimed` | `in progress` | `done` | `needs review`.

---

## Task board

| # | Task | Status | Owner (session) | File scope |
|---|------|--------|-----------------|------------|
| T1 | Resolve the 3 `link.amazon` short links to ASINs and capture Amazon listing facts | done | sess-105bc29e | research only (no files) |
| T2 | Verify Amazon Associates policy facts (agreement, program policies, commission table, application review) | done | sess-105bc29e | `data/sources.json`, `data/compliance.json` |
| T3 | Verify FTC disclosure law (16 CFR 255, Endorsement Guides, Disclosures 101) | done | sess-105bc29e | `data/sources.json`, `data/compliance.json` |
| T4 | Verify product specs from brand‑official pages + owner's manuals | done | sess-105bc29e | `data/products.json` |
| T5 | Build the static dashboard site generator (no external deps) | done | sess-105bc29e | `build.py`, `assets/`, `templates/` |
| T6 | Category page + 3 product/review pages + buying guide + comparison | done | sess-105bc29e | `categories/`, `products/`, `guides/` |
| T7 | Marketing content: SEO copy, disclosure blocks, link inventory | done | sess-105bc29e | `guides/`, `data/marketing.json` |
| T8 | Platform blueprint (automation pipeline, ops model, compliance guardrails) | done | sess-105bc29e | `platform.html`, `data/platform.json` |
| T9 | "Flagged for Review" page with source links for every unverified item | done | sess-105bc29e | `flagged.html` |
| T10 | Executive summary | done | sess-105bc29e | `EXECUTIVE-SUMMARY.md`, `executive-summary.html` |
| T11 | Final integration: rebuild, crawl for broken internal links, re‑verify every row has an official source | done | sess-105bc29e | whole tree (integration) |
| T12 | Open PR → merge to `main` → confirm GitHub Pages deploy | in progress | sess-105bc29e | `.github/workflows/` |

---

## Claim log

| UTC time | Session | Action |
|----------|---------|--------|
| 2026-11-13T22:35Z | sess-105bc29e | Claimed T1–T11 (research, data, site, integration). No other claims present; repo was empty apart from `README.md`. |
| 2026-11-13T22:35Z | sess-105bc29e | Claimed T12 (PR + merge + Pages verification). |

---

## Verification record

**Session:** sess-105bc29e
**Branch:** `arena/105bc29e-zone1` (base `42f4036`)
**Verification date:** 2026-11-13 (UTC)
**Method:** every fact in `data/*.json` was fetched live from the official domain on the date above, quoted, and given a `source_id` that resolves in `data/sources.json`. Values that could not be confirmed from an official source are stored as `null` with `status: "unverified"` and appear on `flagged.html`. Nothing was inferred or back-filled.

### Sources used (all primary / official)

| ID | Source | What it verifies |
|----|--------|------------------|
| S1 | https://affiliate-program.amazon.com/help/operating/agreement | Operating Agreement: disclosure wording (§5), term/termination (§6), Schedules |
| S2 | https://affiliate-program.amazon.com/help/operating/policies | Program Policies: Participation Requirements, Products Statement, Trademark Guidelines, IP License (Creators/PA API) |
| S3 | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | Standard Commission Income Statement — the fixed rate table and Bounty Events |
| S4 | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM | Application Review Process — 3 qualifying sales / 180 days, 10 posts, 60-day recency, 500 followers |
| S5 | https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98 | How to identify yourself as an Associate; clear + conspicuous link-level disclosure |
| S6 | https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA | Tracking IDs / sub-tags |
| S7 | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking | FTC Endorsement Guides Q&A (material connection, clear & conspicuous) |
| S8 | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | FTC disclosure practice: placement, wording, don'ts |
| S9 | https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255 | 16 CFR Part 255 — binding rule text (§255.5) |
| S10 | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | Chefman 6 Qt Dual‑Window specs, freight weight, MSRP, brand rating |
| S11 | https://chefman.com/products/turbofry-touch-6-qt-dual-basket-air-fryer | Chefman 6 Qt Dual‑Basket specs (sister SKU) |
| S12 | https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1 | Chefman 8 Qt TurboFry Touch Stainless specs, MSRP, brand rating |
| S13 | https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQSS-8T-UG-US.pdf | Chefman RJ38‑SQSS‑8T owner's manual (presets, temps) |
| S14 | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | Emeril 26QT specs, MSRP, accessories, warranty |
| S15 | https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf | Emeril FAFO‑001 owner's manual (power, capacity, temp range) |

### Line-by-line results

* **Short links** — `https://link.amazon/B04G1MEwY` → `https://www.amazon.com/dp/B0CDY277D3`; `https://link.amazon/B02NbDxp3` → `/dp/B09B7SB46R`; `https://link.amazon/B00hJ57DV` → `/dp/B08DKYBTPH`. Confirmed by following each short link and reading the returned product page title on 2026‑11‑13.
* **Commission rates** — taken only from the S3 table. Air fryers are **not** listed by name; the ASIN→category mapping is not published by Amazon, so the per‑product rate is recorded as unverified and both candidate rows (Kitchen 4.50%, All Other Categories 4.00%) are shown.
* **Prices / star ratings** — deliberately **not** scraped or reproduced from Amazon. Program Policies §2(b) only permits showing price/availability when Amazon serves the link or via Creators/PA API, and §3(t) only permits review/star content obtained via the API. Amazon prices and ratings are therefore blank + flagged; manufacturer MSRP is shown separately and labelled.
* **Product specs** — every value comes from the brand's own page or its own manual PDF. Three genuine conflicts were found and are flagged rather than resolved by guesswork (see below).

### Irregularities flagged for review

1. **ASIN → exact model number unmapped (all three products).** Amazon does not publish which SKU an ASIN is; the brand sites publish model numbers. Recorded as unverified.
2. **Chefman 6 Qt:** two near-identical SKUs exist (`RJ38-SQPF-3TDB-2` and `RJ38-SQPF-3TDB-2W`). The Amazon listing says "Easy View Windows", which matches the `-2W` dual‑window page, but this is a match, not a confirmation. Flagged.
3. **Chefman 8 Qt brand conflict:** the Amazon listing title advertises "4-in-1 … Bake, Dehydrate, Frozen" with a 450 °F Hi‑Fry option, while the brand page/manual for `RJ38‑SQSS‑8T` documents 200–400 °F with fries/chicken/fish/meat presets. Either the ASIN is a different SKU or one side is stale. Flagged, no value asserted.
4. **Emeril preset count conflict:** the brand spec block says "25 Cooking Pre‑sets" while the same page's description says "24 one‑touch cooking presets" and lists 20 names; the manual documents model `FAFO‑001` while the page lists `4‑00675‑02A‑VN`. Flagged.
5. **Emeril "10-in-1" vs "24/25 functions":** marketing label vs spec count are inconsistent on the official page. Flagged.
6. **Affiliate tag not visible in the supplied short links.** `link.amazon` is Amazon's own shortener, so the Associates tag is hidden. Whether the tag is present, valid, and belongs to the account cannot be verified without Associates Central access. Flagged — attribution is unconfirmed.
7. **Program Policies §2(w)** prohibits link shortening that makes it unclear you are linking to an Amazon Site; `link.amazon/…` keeps the Amazon name, but the landing URL is temporary. Flagged for the account holder to confirm current Amazon guidance.
8. **IP License §2(e)** forbids using Creators/PA API or Data Feeds to aggregate, analyse, extract or repurpose Program Content, or to train/fine‑tune ML models. Any "AI product research" feature must therefore run on non‑Program‑Content inputs. This constrains the platform design and is documented in `platform.html` + `flagged.html`.
9. **No Amazon price, availability or star rating is displayed anywhere on the site**, by design (policy), not by omission.

---

## PR / deploy record

* PR: _(filled in after the merge)_
* Merge result: _(pending)_
* GitHub Pages: `https://kanlerxz87-cyber.github.io/Zone1/` — source `main` / root, build type `legacy` (confirmed via `gh api repos/kanlerxz87-cyber/Zone1/pages` before work started).
* Deploy verification: _(pending — checked after merge)_
