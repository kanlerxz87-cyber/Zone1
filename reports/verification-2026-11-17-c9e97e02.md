# Verification report — arena/c9e97e02, 2026-11-17 UTC

Session c9e97e02, task C9 (measurement shipped + question guides + mobile pass +
one-site indexing). This report is the pass's evidence table: what was read live,
what was proved locally, what changed, and what remains open. Nothing in this
repository is marked verified without a source read in this pass or named below
as read by an earlier pass on the same day.

## 1. Live source re-reads (server-side fetch, 2026-11-17 UTC)

| # | Source | What was read | Verdict |
|---|---|---|---|
| R1 | [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY) | Resolves to `amazon.com/dp/B0CDY277D3` with fallback-style parameters (`lv=shuf`, `btn_type=ss`, `plpRedirect=mhFallback`, `btn_ref=srctok-…`, and a `gaOptInStatus=true` parameter first observed 2026-11-17). Listing title: "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black" | Destination and title match `data/products.json` character-for-character. **No `tag=` parameter on the final URL** — F82 unchanged. Identity remains unconfirmed (F6/F7/F10 unchanged). |
| R2 | [link.amazon/B02NbDxp3](https://link.amazon/B02NbDxp3) | Resolves to `amazon.com/dp/B09B7SB46R`, same fallback parameter family. Title: "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included" | Matches the register. The "Six Cooking Accessories Included" title conflicts with the site's published 7 (F4/F5/F71) — conflict live, unchanged. |
| R3 | [link.amazon/B00hJ57DV](https://link.amazon/B00hJ57DV) | Resolves to `amazon.com/dp/B08DKYBTPH`. Title: "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel" | Matches the register. The 450 °F title claim vs the manual's 200–400 °F row (F3/F33) conflict live, unchanged. |
| R4 | [Associates Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | Heading reads "**Updated:** April 14, 2026." All eight policy sections present (Commission Income Statement, Participation Requirements, Products Statement, Mobile Application Policy, Trademark Guidelines, IP License, Influencer Program Policy, Creator Ads Boost Program Policy). | Confirms S2's version stamp. No change. |
| R5 | [Standard Commission Income Statement](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) | Table 1 read in full with no login: "Physical Books, Kitchen, Automotive — 4.50%", "All Other Categories — 4.00%"; bounty rows $12.00 / $5.00 / $0.25. | Confirms S3 and the decision layer's rate arithmetic. Per-product rate stays blank (no ASIN→category mapping, Q-11). |
| R6 | [RFC 9309 §2.3](https://www.rfc-editor.org/rfc/rfc9309.html) | "The rules MUST be accessible in a file named \"/robots.txt\" (all lowercase) in the top-level path of the service." URI form `scheme:[//authority]/robots.txt`. | New source **S43**; grounds flag **F85**. |
| R7 | [Google: Introduction to robots.txt](https://developers.google.com/search/docs/crawling-indexing/robots/intro) | "This is used mainly to avoid overloading your site with requests; **it is not a mechanism for keeping a web page out of Google**. To keep a web page out of Google, block indexing with `noindex` or password-protect the page." A blocked URL "can still appear in search results". | New source **S44**; grounds flag **F85** and suggestion **SG-41**. |

**Not re-read this pass** (re-read earlier the same day by session 4618f77b — see
[`reports/verification-2026-11-17-4618f77b.md`](verification-2026-11-17-4618f77b.md)):
S1 Operating Agreement ("Updated: October 15, 2025"), S4 Application Review, S5
Associate identification, S8 FTC Disclosures 101, S9 eCFR 16 CFR 255, and the
manufacturer pages S10/S12/S14/S15. No value published anywhere in this pass
depends on a fact from those pages that the named report does not already carry.

## 2. What this pass shipped, and what was proved about it

| Component | Claim | Proof |
|---|---|---|
| `assets/app.js` counter | Sends EV-01…EV-04 exactly as `data/measurement.json` defines them; cookie-free, identifier-free; inert while `data/config.json` has no endpoint | `node --check` passes; the emitted events' fields match the endpoint schema, which rejects anything else |
| `platform/analytics/server.py` | Accepts EV-01…EV-04; rejects EV-05 and unknown fields with 400; never reads client address / User-Agent / Referer; drops prefetch beacons unrecorded; serves per-day aggregates only | `python3 platform/analytics/test_server.py` — **21 assertions, all passed** (includes a log scan proving no address/UA/referrer key can exist in the event file). Wired into `scripts/ci-check.sh` and `.github/workflows/ci.yml` |
| footer §3(e) sentence | States the counter's real state, generated from the same config value as the counter's meta tag | New build guard `check_analytics_disclosure()` **proven to fire both ways**: with an empty endpoint, removing the "records nothing until" phrase fails the build naming the page; with an endpoint configured, a stale empty-state meta fails the build naming the mismatch. Both injections reverted; build green after |
| S-07 question guides | Four buyer questions, one page each; every number is a `{{placeholder}}` spliced from `data/products.json`; every section cites registered sources | Article guards reject paraphrased values (8 mid-sentence splice violations caught and fixed during writing) and banned phrases; build passes `check_articles`, `check_article_voice`, `check_article_splices`, `check_article_pages` |
| S-20 mobile pass | Fluid type scale, 44px tap targets on controls/wayfinding, sticky comparison bar | Rendered CSS shipped in `assets/style.css`; comparison headers gained real `#p-<slug>` anchors (the in-page fragment guard passes) |
| S-25 / one-site | robots.txt now asks the annex builds out of the index; sitemap lists only canonical URLs | Generated robots.txt diff in this commit; **F83 records the honest limit** (subpath robots.txt is not protocol-visible per RFC 9309; robots.txt is not an exclusion mechanism per Google) with S43/S44 quoted |
| Registers | Requirements statuses, suggestion rows, question rows updated line by line | `check_requirement_paths`, `check_requirement_tokens`, `check_question_block_refs`, `check_register_duplicates` all pass |

## 3. Gate results (final tree, 2026-11-17)

| Gate | Result |
|---|---|
| `python3 build.py` | 55 pages emitted; **55 sitemap URLs** (was 51), **25 feed items** (was 21); robots.txt written |
| `python3 verify.py` | 134 pages, 77 spec rows (75 verified / 2 blank+flagged), **39 sources**, 0 errors, 0 external warnings |
| `bash scripts/ci-check.sh` | unit tests + **analytics endpoint tests (21)** + data audit clean + annex build current + link check **0 broken** |
| `python3 platform/analytics/test_server.py` | 21 passed, 0 failed |
| `node --check assets/app.js` | OK |
| `python3 research/check_research.py` · `scripts/verify_site.py` · `platform/audit/report.py` | all pass (run at integration) |
| second `build.py` run | tree reproduced byte-for-byte |

## 4. Irregularities raised this pass (published, non-blocking)

* **F85** (new, on `flagged.html`): robots.txt on a GitHub project-pages subpath is
  not where RFC 9309 §2.3 places the file, and Google's guidance says robots.txt is
  not an exclusion mechanism anyway. The Disallow lines ship as documented intent;
  **meta robots noindex on the annex builds** is the mechanism that works — requests
  logged in `COORDINATION.md` for those builds' owners (SG-41). Nothing in the
  annexes was edited.

## 5. Open items unchanged by this pass (published on flagged.html)

F3 (8 Qt temperature ceiling), F4/F5/F71 (Emeril preset and accessory counts),
F6/F7/F10/F82 (short-link identity, tag observability), F11 (standalone privacy
page + legal review), F76 (attribution untested — SG-37 is the gate), F81 (two
supplied links are meat thermometers; intended products unknown), Q-01/Q-02/Q-04,
and the two blank+flagged spec rows. **Nothing was filled by inference.**
