# Verification round — 2026-11-17 (arena/16adefc5-zone1, session 16adefc5)

**Branch:** `arena/16adefc5-zone1`, based on `origin/main` = `6c9d313` (PR #140 merge).
**Window:** 2026-11-17 16:45–17:10 UTC.
**Method:** every official source below was re-read live in this pass (server-side fetch of the
public page, no login); every deployed page was read back from
`https://kanlerxz87-cyber.github.io/Zone1/`. No value in this report is inferred — a row that
could not be confirmed says so. No product or site content was edited by this pass; the one
defect found is logged as request **R-16adefc5-1** in `COORDINATION.md` because `build.py` and
`data/requirements.json` are owned by four open PRs (#139, #141, #142, #143) at the time of writing.

---

## 1. Load-bearing policy sources

| # | Source (manual-review link) | Register claim | Live read 2026-11-17 | Verdict |
|---|---|---|---|---|
| S1 | [Associates Program Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) | "Updated: October 15, 2025" | Heading reads **"Updated: October 15, 2025"** | confirmed |
| S2 | [Associates Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | "Updated: April 14, 2026"; §2(a) tag rule; §2(b) `XXXXX-##` parameter rule | Heading reads **"Updated: April 14, 2026"**; §2(a) verbatim "Special Links must use the Associates ID we have assigned to you"; §2(b) verbatim "you must include your Associates ID or 'tag' (appearing as XXXXX-## …) as a parameter in the URL of each link you place on your Site"; price/availability rule (Creators API or PA API) present as published | confirmed |
| S3 | [Standard Commission Income Statement](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) | Kitchen 4.50%; All Other 4.00%; bounties $12.00 / $5.00 / $0.25 | Table 1 verbatim: **"Physical Books, Kitchen, Automotive — 4.50%"**, **"All Other Categories — 4.00%"**; Bounty table: Prime Free Trial **$12.00**, Prime Video First Stream **$5.00**, Prime Video Stream **$0.25** | confirmed |
| S4 | [Application Review Process](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) | 3 sales/180 days; personal orders excluded; ≥10 posts; content within 60 days; ≥500 followers; rejection final | all five read verbatim: "at least three within the first 180 days"; "personal orders do not qualify"; "a good rule of thumb is at least 10 posts"; "generally within the last 60 days"; "in most cases, at least 500"; "we aren't able to reassess an application once it's been rejected" | confirmed |
| S5 | [Associate identification help node](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) | Required sentence verbatim; "Clear." / "Conspicuous." tests | **"As an Amazon Associate I earn from qualifying purchases."** verbatim; Clear / Conspicuous list present verbatim | confirmed |
| S8 | [FTC Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | "November 2019"; "hard to miss"; "can't talk about … you haven't tried" | all three verbatim; page dated **November 2019** | confirmed |
| S9 | [eCFR 16 CFR Part 255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) | latest recorded stamp "up to date as of 11/13/2026"; last amended 10/30/2026; §255.0–§255.6; source note 88 FR 48102 (Jul 26 2023) | "Displaying title 16, **up to date as of 11/13/2026**. Title 16 was last amended 10/30/2026."; §255.0–§255.6 incl. §255.5 "Disclosure of material connections"; source note **88 FR 48102, July 26, 2023** | confirmed |

## 2. Brand pages (spec values published on this site)

| # | Source (manual-review link) | Rows checked against the live page | Verdict |
|---|---|---|---|
| S10 | [Chefman 6 Qt Dual-Window product page](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | Capacity 6 Qt / 5.67 L · Temperature range **200–450 °F / 95–235 °C** · Hi-Fry max **450 °F / 235 °C** ("Max temp: 450ºF/ 235ºC with Hi-Fry function" in Features) · Dimensions 13.38 × 11.81 × 10.63 in · Weight 13.3 lbs / 6.03 kg · Power 1700W/120V · Model **RJ38-SQPF-3TDB-2W** · review widget **4.6, 1,310 Total Reviews** | all confirmed (1,310 matches the 2026-11-17 refresh; 4.6 unchanged) |
| S12 | [Chefman 8 Qt TurboFry product page](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) | Temperature range **200–400 °F** · Max temp **400ºF/205ºC** · **4 cooking presets** · Dimensions (8 Qt) 15.4 × 12.6 × 13.5 in · Weight 12.8 lbs / 5.8 kg · Model **RJ38-SQSS-8T** · Power 1700W/120V · review widget **4.6, 717 Total Reviews** · **no Hi-Fry listed anywhere on this page** | all confirmed; the "Hi-Fry / 450 °F mode = None" blank stays correct for S12 |
| S14 | [Emeril French Door AirFryer 360 product page](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | Dimensions **16.9"D × 15.8"W × 14.8"H** · Capacity **26-Quart / 24.6 Liters** · Voltage **120 volts** · Model **4-00675-02A-VN** · rating widget **2.6 (25)** · specification strip **"25 Cooking Pre-sets"** · description **"10-in-1"** · carousel asset **"11-in-1"** | all confirmed; the four-way preset conflict (25 / 24 / 10-in-1 / 11-in-1) remains live exactly as published — nothing inferred, no preset count asserted |

## 3. The five submitted `link.amazon` tokens (re-resolved, redirects followed)

| Supplied token | Served final URL | Served `<title>` (first words) | Matches register |
|---|---|---|---|
| `B04G1MEwY` | `/dp/B0CDY277D3?lv=shuf…&channelId=704&plpRedirect=mhFallback` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry… | yes (S17 → B0CDY277D3) |
| `B02NbDxp3` | `/dp/B09B7SB46R?lv=shuf…&channelId=704&plpRedirect=mhFallback` | Emeril Lagasse 26QT French Door… 24 One-Touch Preset Options… Six Cooking Accessories Included | yes (S17 → B09B7SB46R) |
| `B00hJ57DV` | `/dp/B08DKYBTPH?lv=shuf…&channelId=704&plpRedirect=mhFallback&th=1` | Chefman Air Fryer 8 Qt \| TurboFry 4-in-1 with 450°F Hi-Fry Option… | yes (S17 → B08DKYBTPH) |
| `B0c8moW59` | `/dp/B0DHZTCNR5?lv=shuf…&channelId=500&plpRedirect=mhFallback` | ThermoMaven 1 Sec Professional Digital Meat Thermometer… (breadcrumb Thermometers & Timers › Meat) | yes (S36; different category — F81 stands) |
| `B0f3GKalj` | `/dp/B0DZFD6R9Z?lv=shuf&sbo=…&channelId=500&plpRedirect=mhFallback&th=1` | CHEF iQ Sense \| Smart Wireless Meat Thermometer \| 3 Ultra-Thin Probes… (Thermometers & Timers › Meat) | yes (S37; different category — F81 stands) |

Observations, recorded not interpreted: every landing URL still carries `lv=shuf` and
`plpRedirect=mhFallback`; **none carries a `tag=` parameter** (F82 stands); `btn_ref=srctok-…`
values differ per request, as previously recorded (F41). Per the control test recorded in
PR #139's branch, the `mhFallback` marker alone is not evidence about a submitted link —
the identity caveat rests on the nine-character tokens and the unrecorded intent, both unchanged.

## 4. Deployed-site read-back (GitHub Pages)

| Check | Result |
|---|---|
| Pages build | `status: built`, commit `6c9d313`, updated 2026-11-17T16:53:56Z, `error: null` |
| Workflows on main | `CI`, `Build, verify and deploy to GitHub Pages`, `Verify verification annex (site/)`, `pages build and deployment` — all `completed/success` |
| `/` landing page | disclosure strip is the first content above `<main>`; hero → format tiles → articles → guides; no audit-process framing |
| `/products/chefman-6qt-dual-basket.html` | disclosure above fold; CTA labelled "Affiliate link · tracking unconfirmed"; every spec row carries an official source; spec values match §2 of this report |
| `/requirements.html` | **defect: three hrefs (`platform/`, `platform/tests/` ×2) serve the site's 404 page** — see §5 |

## 5. Defects and irregularities

| ID | Finding | Status |
|---|---|---|
| **R-16adefc5-1** | `requirements.html` ships three directory hrefs (`href="platform/"` once, `href="platform/tests/"` twice — rows G-01/G-04 of `data/requirements.json`). GitHub Pages returns the site's own 404 for a directory with no `index.html`; live-confirmed at `https://kanlerxz87-cyber.github.io/Zone1/platform/`. Local link gates pass because the directories exist on disk; no gate checks servability. Suggested repair recorded in `COORDINATION.md`. A repo-wide scan finds this defect on no other page. | **open, request logged** (build.py / data/requirements.json owned by open PRs #139/#141/#143) |
| **State-of-play: tracking ID** | The brief's selected tracking ID `shopnow047c-20` is **not applied to any outbound link on current main**. PR #128 (merged 16:12Z) wired and gated it; PR #137 (merged 16:38Z, commit `5fe5422`) blanked `associate_tag` with the note that the ID "has not been validated in Associates Central and the required enrolled-Associates test has not been completed", removed `check_associate_tagging()`, and pointed product CTAs back at the untagged `link.amazon/<token>` short links. The site is honest about this everywhere it speaks (F76 "not validated … applied to links, or confirmed by a test"; product-intent "User-provided value recorded only"; Q-01/Q-03-style rows; SG row "Confirm the ID, click one published link, read the report"). Open PR **#141** proposes re-wiring the tag. This is a recorded decision conflict between two passes, not a silent drift — resolving it is the owner's call (or #141's), not this pass's. | **open, decision conflict recorded, PR #141 in flight** |
| **Observation: `/dp/` evidence citations** | 20 bare `amazon.com/dp/…` anchors on `data.html`, `pass10.html`, `reverification.html`, `questions.html` ship `rel="noopener"` only. They are source-register and verification citations (the rendered form of rows like "Amazon detail page for ASIN B0CDY277D3"), not calls to action — the recorded D-05 rationale treats `/dp/` citations as source badges. All CTAs (`class="btn"` → `link.amazon`) and every clickable non-citation `link.amazon` anchor carry `rel="sponsored"`; `check_affiliate_link_qualification()` is green. Recorded so the next reviewer can decide whether citations should also carry `nofollow`. | observation, no change made |
| Carried forward unchanged | F3, F4/F5, F70, F71, F11, F76, F81, F82, Q-01/Q-02/Q-04, the 2 blank+flagged spec rows (8 Qt basket divider; one caution row) — all still published on `flagged.html`, none resolved by this pass, none filled by inference. | open (non-blocking) |

## 6. Local gates on the tree this report was written against

| Gate | Result |
|---|---|
| `python3 build.py` | exit 0 — 31 sitemap URLs, feed 21 items; tree byte-clean after rebuild |
| `python3 verify.py` | 130 pages, 77 spec rows (75 verified, 2 blank+flagged), 42 sources, **0 errors**, 0 external warnings |
| `bash scripts/ci-check.sh` | 33 unit tests OK, data audit clean, s2 annex current, **9,585 links / 0 broken** |
| `python3 research/check_research.py` | OK — no broken links, no unsourced rows, disclosures on every page |
| `python3 scripts/verify_site.py` | 393 assertions — ALL CHECKS PASSED |
| `python3 platform/audit/report.py` | AUDIT PASSED (0 warnings) |
| `node --check assets/app.js` | OK |
| `python3 -m unittest discover -s tests` | 17 tests OK |
| `git diff --check` | clean |
| Scripted defect scan (25 root pages) | dead in-page anchors 0 · broken internal links 3 (the directory hrefs above) · missing canonicals 0 (404.html correctly carries none) · duplicate titles 0 · missing meta descriptions 0 · disclosure above `<main>` **25/25** · conflict markers 0 · sitemap/feed targets all exist on disk · untagged or unsponsored product CTAs **0** |

## 7. What this pass did not do

No product or site content was changed (scope: read-only while four PRs own the shared files).
No value was inferred or filled — the two blank spec rows stay blank and flagged. The
directory-href defect was **not** patched by this pass; it is logged as R-16adefc5-1 for the
next owner of `build.py`, per COORDINATION protocol item 4. The tracking-ID decision conflict
was **not** resolved by this pass; both recorded positions and open PR #141 are named above.
