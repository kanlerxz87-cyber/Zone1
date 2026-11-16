# Verification pass 10 — live re-read of the source register

**Date:** 2026-11-16 (UTC) · **Session:** `arena/9fccce0c-zone1` (session `9fccce0c`)
**Branch:** `arena/9fccce0c-zone1` · **Baseline:** `6dbfa7cb` (= `origin/main` at claim time)
**Scope:** the canonical root build — `build.py`, `data/*.json`, the generated root HTML, and the
`platform/` engine. The parallel published builds (`site/`, `s2/`, `research/`, `docs/`,
`dashboard/`, `annex-88769516/`, `session-*/`, `crosscheck/`) are **not** edited by this pass.

This is the **tenth** independent re-read of the same register. It was run because the register is
made of values that move — a manufacturer's review counter, an Amazon listing title, a policy
page's "Updated" line — and because the last several passes each found something. It found
three things.

## Method, and what "verified" means here

Every row below was fetched **in this session, on 2026-11-16**, through the page-fetch tool. This
sandbox has no direct egress to non-GitHub hosts from a shell (`curl` returns `000` for
`amazon.com`, `affiliate-program.amazon.com`, `chefman.com`, `ftc.gov`, `ecfr.gov` and
`github.io`), so every live check below was made through that tool and read back from the
response body. Nothing was carried over from a previous pass and nothing was inferred.

| Verdict | Meaning |
|---|---|
| **confirmed** | The live page states the value, in the wording recorded in the dataset. |
| **moved** | The live page states a *different* value than the one published — the value was updated and the movement recorded, with both read dates kept. |
| **not-stated** | The official page was read and does not state the fact. Nothing was filled in. |
| **new-evidence** | A clause that was read live for the first time in this pass and was not previously in the register. |

## A · Amazon Associates program documents

| # | Source | What was read back, verbatim, on 2026-11-16 | Verdict |
|---|---|---|---|
| V1 | [S3 — Standard Commission Income Statement](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) | Table 1 read without a login. "Physical Books, Kitchen, Automotive \| 4.50%"; "Toys, Furniture, Home, Home Improvement, Lawn & Garden, Pets Products, Headphones, Beauty, Musical Instruments, Business & Industrial Supplies, Outdoors, Tools, Sports, Baby Products, Amazon Coins \| 3.00%"; "PC, PC Components, DVD & Blu-Ray \| 2.50%"; "All Other Categories \| 4.00%"; "Television, Digital Video Games \| 2.00%"; "Amazon Fresh, Physical Video Games & Video Game Consoles, Grocery, Health & Personal Care \| 1.00%"; "Luxury Beauty, Luxury Stores Beauty, Amazon Explore \| 10.00%". Bounty Events read: Prime Free Trial $12.00, Prime Paid Membership $12.00, Prime Video Stream $0.25, Prime Video First Stream $5.00. | confirmed |
| V2 | [S3](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) | Still **no air-fryer row** and still no published ASIN→category mapping. The per-product rate therefore stays blank on the site. | not-stated |
| V3 | [S4 — Application Review Process](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM) | "our Associates team will check your application once you've driven qualified sales (we require at least three within the first 180 days). Please note that personal orders do not qualify." · "All Sites must have robust original content (even when advertising is removed) – a good rule of thumb is at least 10 posts." · "Content on your website must be recent (generally within the last 60 days). You must own your website." · "Your social network page or group must be established, with a substantive number of organic followers/likes (in most cases, at least 500)." · "Unfortunately, we aren't able to reassess an application once it's been rejected." | confirmed — **closes flag F56** |
| V4 | [S2 — Associates Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | Page heading reads "**Updated:** April 14, 2026. (Current Associates, see what's changed.)" — matches the registered value. Section order unchanged: Commission Income Statement, Participation Requirements, Products Statement, Mobile Application Policy, Trademark Guidelines, IP License, Influencer Program Policy, Creator Ads Boost. | confirmed |
| V5 | [S2](https://affiliate-program.amazon.com/help/operating/policies) | Commission Income Statement §1(d): session "beginning when a customer clicks through that Special Link and ending upon the first to occur of the following: (x) 24 hours elapse from that click…" · §1(d)(i) "no later than 89 days after their initial click-through of the Special Link" · §1(d)(iii) "within 180 days of the purchase, the Product is shipped to, streamed or downloaded by, and paid for by the customer". | confirmed — 24 h / 89 d / 180 d windows |
| V6 | [S2](https://affiliate-program.amazon.com/help/operating/policies) | Participation Requirements §3(e): "disclosing on your Site accurately and adequately and otherwise satisfying applicable legal requirements, either through a privacy policy or otherwise, the use of cookies, pixels, and other technologies by you and third parties and how you collect, use, store, and disclose data collected from visitors…" | confirmed |
| V7 | [S2](https://affiliate-program.amazon.com/help/operating/policies) | §6(t): "You will not display or otherwise use any of our customer reviews or star ratings, in part or in whole, on your Site unless you have obtained a link to that customer review or star rating through Creators API or PA API…" · §6(w): "You will not use a link shortening service, button, hyperlink or other ad placement in a manner that makes it unclear that you are linking to an Amazon Site." · §6(y): "Unless otherwise agreed by Amazon, your Site must not have price tracking and/or price alerting functionality." · §6(s): "You will not artificially generate clicks or impressions on your Site or create Sessions on an Amazon Site, whether by way of a robot or software program or otherwise." | confirmed |
| V8 | [S2](https://affiliate-program.amazon.com/help/operating/policies) | IP License §2(e): "You will not, without our express prior written approval, access or use Creators API, PA API or Data Feeds for the purpose of aggregating, analyzing, extracting, or repurposing any Product Advertising Content or in connection with any software or other application intended for use by persons or entities that offer products on an Amazon Site, or in the direct training or fine-tuning of a machine learning and/or foundational model." — matches the quote already published as requirement **C9**, character for character. | confirmed |
| V9 | [S2](https://affiliate-program.amazon.com/help/operating/policies) | IP License §1, final paragraph: "We will not allow any third party to, use Program Content to, directly or indirectly, develop or improve large language or multimodal models, machine learning models or related technology." | confirmed — **not previously in the register** |
| V10 | [S2](https://affiliate-program.amazon.com/help/operating/policies) | IP License §4 "Agents" (Agent Terms): "The terms in this section ("Agent Terms") apply if you use, allow, enable, or cause the deployment of an Agent to access, use, or interact with the Program Content. For the purposes of these Agent Terms, "Agent" means any software or service that takes autonomous or semi-autonomous action on behalf of, or at the instruction of, any person or entity." · (a) "No Agent may access, use, or interact with Program Content unless, at all times, it identifies itself and operates in strict accordance with the requirements in section 3 of these Agent Terms." · (b) "At our sole discretion, we may limit, including by technical measures, whether and how any Agent accesses, uses, and interacts with Program Content." · (c) "In all HTTP/HTTPS requests, identify that the request is from an Agent and disclose the name of the Agent by including the following in the request's user agent string: "Agent/[agent name]" (e.g., Agent/AmazonAgent)"; "Not conceal or obfuscate that any access, use, or interactions are from an Agent…"; "Respond truthfully to any question or prompt seeking to determine if interactions are coming from a human or a computer." | **new-evidence** — **not previously in the register** |
| V11 | [S2](https://affiliate-program.amazon.com/help/operating/policies) | Participation Requirements §5 (Distribution of Special Links Through Software and Devices), final sentence: "You will not, without express prior written approval, use, or allow any third party to use, any Special Links or Program Content to develop machine learning models or related technology." | **new-evidence** — **not previously in the register** |

**Limit stated honestly:** the Amazon policies page renders its IP License as one long markdown
table, and the fetch tool's markdown conversion collapsed some of it. Everything quoted in V8–V11
was read directly in the response body. **Section 4 of the Agent Terms was not read end to end** —
the row shown names sub-parts (a), (b) and (c), and sub-part (a) refers to "the requirements in
section 3 of these Agent Terms", whose text was not visible in the rendered chunk. A human
reviewer should read §4 in a browser before this is relied on as a launch checklist. That gap is
published as part of **flag F62**, not closed by inference.

## B · The three supplied links and the listings behind them

All three short links were requested on 2026-11-16. All three landed on the same ASINs this site
publishes, and all three rendered the same browse-node path.

| # | Source | What was read back | Verdict |
|---|---|---|---|
| V12 | [S17 — `link.amazon/B04G1MEwY`](https://link.amazon/B04G1MEwY) | Redirected to `https://www.amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-68884e8aa630b24a&channelId=704&plpRedirect=mhFallback`. `<title>`: "Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen" — matches the stored title exactly. Breadcrumb: Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers. | confirmed |
| V13 | [S17 — `link.amazon/B02NbDxp3`](https://link.amazon/B02NbDxp3) | Redirected to `https://www.amazon.com/dp/B09B7SB46R?…&plpRedirect=mhFallback`. `<title>`: "Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included : Home & Kitchen" — matches the stored title exactly, including the wording that changed on 2026-11-15 (flag F38). Same breadcrumb. | confirmed |
| V14 | [S17 — `link.amazon/B00hJ57DV`](https://link.amazon/B00hJ57DV) | Redirected to `https://www.amazon.com/dp/B08DKYBTPH?…&plpRedirect=mhFallback`. `<title>`: "Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel : Home & Kitchen" — matches the stored title exactly. Same breadcrumb. | confirmed |
| V15 | [S16](https://www.amazon.com/dp/B0CDY277D3) / [S28](https://www.amazon.com/dp/B09B7SB46R) / [S29](https://www.amazon.com/dp/B08DKYBTPH) | The three ASIN URLs served directly to an automated request returned Amazon's bot checkpoint ("To continue, please click the "Continue shopping" button below") on this date; the listings were therefore read through the short links, which served the full pages. This is the same limitation recorded on 2026-11-15 for S28. | not-stated (titles still read via V12–V14) |
| V16 | [S22 — control token `link.amazon/ZZZ9ZZZZZ`](https://link.amazon/ZZZ9ZZZZZ) | The nonsense-token control was **not** re-run this pass. The 2026-11-14 result (403 Forbidden, so the resolver refuses an unknown token rather than serving a featured product) stands as recorded and is cited from the earlier pass. | not re-read — recorded, not re-asserted |

## C · Manufacturer pages — the volatile rows

| # | Source | What was read back | Verdict |
|---|---|---|---|
| V17 | [S10 — Chefman 6 Qt Dual-Window product page](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | Specifications block, verbatim: "Capacity: 6 Qt / 5.67 L" · "200–450°F / 95º-235ºC temperature range" · "Dimensions: 13.38 in x 11.81 in x 10.63 in / 33.98 cm x 30 cm x 27 cm" · "Weight: 13.3 lbs / 6.03 kg" · "Power: 1700W/120V" · "Model Number: RJ38-SQPF-3TDB-2W" · "cETL approved with a 1-year Chefman® assurance". Features: "Max temp: 450ºF/ 235ºC with Hi-Fry function". | confirmed |
| V18 | [S10](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | Brand-hosted review widget read: **4.6, 1307 Total Reviews** (5★ 928 · 4★ 258 · 3★ 85 · 2★ 12 · 1★ 24). The site published "4.6 / 5 from 1,305 reviews" (5★ 927 · 4★ 257 · …) from the 2026-11-14 read. **The count moved +2; the average held at 4.6.** | **moved** — row refreshed, both dates kept |
| V19 | [S12 — Chefman 8 Qt TurboFry product page](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) | Specifications block, verbatim: "Capacity: 5 Qt or 8 Qt / 4.73 L or 7.57 L" · "200–400°F / 95º-205ºC temperature range" · "Power: 1700W/120V" · "Dimensions: (8 Qt Model) 15.4 in x 12.6 in x 13.5 in / 39.11 cm x 32 cm x 34.29 cm" · "Weight: (8 Qt Model) 12.8 lbs / 5.8 kg" · "Model Number: RJ38-SQSS-8T (8 Qt model)". Features: "Max temp: 400ºF/ 205ºC" · "4 cooking presets". | confirmed |
| V20 | [S12](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1) | Brand-hosted review widget read: **4.6, 717 Total Reviews** (5★ 523 · 4★ 131 · 3★ 42 · 2★ 10 · 1★ 11). The site published "4.6 / 5 from 716 reviews" (5★ 522 · …) from the 2026-11-14 read. **The count moved +1; the average held at 4.6.** | **moved** — row refreshed, both dates kept |
| V21 | [S14 — Emeril 26 QT French Door product page](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) | Price "$199.99"; model "4-00675-02A-VN"; brand-hosted rating "2.6 (25)". Specification icons: "26-Quart Capacity — preparing food for 4–6 people" · "Dual-Speed Fan" · "25 Cooking Pre-sets" · "16.9"D x 15.8"W x 14.8"H Product Dimensions" · "24.6 Liters Capacity" · "120 volts Product Voltage". Body copy: "This endlessly versatile 10-in-1 air fry convection oven…". | confirmed — the four-way preset/in-1 conflict (F4/F5/F29) is **still live**, and the site still asserts none of the four figures |
| V22 | [S32 — Chefman 6 Qt store endpoint](https://chefman.com/products/turbofry-touch-dual-window-air-fryer.json) | `sku RJ38-SQPF-3TDB-2W`, `price 119.99`, `compare_at_price 119.99`, `grams 6582`, `weight 14.51 lb`, `barcode 810087845025`, `updated_at 2026-11-16T13:25:53-05:00`. | confirmed |
| V23 | [S33 — Chefman 8 Qt store endpoint](https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1.json) | 8 Quart: `sku RJ38-SQSS-8T`, `price 119.99`, `compare_at_price 119.99`, `grams 6078`, `weight 13.4 lb`, `barcode 816458024518`. 5 Quart: `sku RJ38-SQSS-5T`, `price 79.99`, `compare_at_price 99.99`, `grams 4999`, `weight 11.02 lb`. | confirmed |
| V24 | [S34 — Chefman 6 Qt dual-basket sister SKU endpoint](https://chefman.com/products/turbofry-touch-6-qt-dual-basket-air-fryer.json) | `sku RJ38-SQPF-3TDB-2`, `price 119.99`, `compare_at_price 119.99`, `grams 6509`, `weight 14.35 lb`, `barcode 810087842956`. Identical list price to the -2W SKU, which is why price cannot separate them (flag F2). | confirmed |

## D · US government sources

| # | Source | What was read back | Verdict |
|---|---|---|---|
| V25 | [S9 — eCFR, 16 CFR Part 255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) | "Displaying title 16, up to date as of 11/12/2026. Title 16 was last amended 10/30/2026." Source note: "88 FR 48102, July 26, 2023, unless otherwise noted." §255.5 is titled "Disclosure of material connections." | confirmed |
| V26 | [S7 — FTC Endorsement Guides](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) · [S8 — Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | Not re-fetched in this pass. Both pages were read live on 2026-11-14 and 2026-11-15 and their wording is published unchanged; this pass makes no new claim about them. | not re-read — carried forward unchanged |
| V27 | [S1 — Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) · [S5](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) · [S6](https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA) | Not re-fetched in this pass. §5 disclosure wording, the disclosure help article and the tracking-ID article were read live on 2026-11-13 and 2026-11-14 and their wording is published unchanged. | not re-read — carried forward unchanged |

## E · The three defects this pass found

### E1 — The canonical register did not carry the clauses that govern the AI-agent platform (new-evidence, fixed)

The brief this project answers asks for "an AI-powered Amazon affiliate marketing platform"
that automates product research. The Program Policies page carries two clauses written for exactly
that case, and **neither was anywhere in the canonical build**:

* **IP License §4 "Agents" (Agent Terms)** — V10. Defines an Agent as "any software or service
  that takes autonomous or semi-autonomous action on behalf of, or at the instruction of, any
  person or entity", and requires it to identify itself in the `User-Agent` string as
  `Agent/[agent name]`, not to obfuscate that it is an agent, not to complete or circumvent
  CAPTCHAs, and to "respond truthfully to any question or prompt seeking to determine if
  interactions are coming from a human or a computer".
* **Participation Requirements §5** — V11. "You will not, without express prior written approval,
  use, or allow any third party to use, any Special Links or Program Content to develop machine
  learning models or related technology."

Before this pass, `data/compliance.json` contained **0** occurrences of "Agent Terms" and
`data/platform.json` contained **0** occurrences of "Agent" — while the root site ships a
platform blueprint (`platform.html`) that proposes automated research against manufacturer and
Amazon pages. The parallel build in `session-3740f69d/` does carry an Agent-Terms row, which is
why the clause was known to this repository; it was simply never carried into the canonical
register.

**Fixed:** new requirement **C17** (Agent Terms) and **C18** (the §5 model-development clause)
in `data/compliance.json`, and new platform guardrail **G11** in `data/platform.json`, each with
the verbatim quote and the S2 source link. The open scope question the clause creates is
published as **question Q-21** and the design decision as **suggestion SG-22** — neither is
resolved by inference.

### E2 — Three published pages pointed at a flag that does not exist (fixed)

`data/questions.json`, `data/suggestions.json` and `data/sources.json` each told the reader to
see **"flag F46"** for the Application Review Process recency criterion. No F46 exists in the
register: the canonical register runs F1–F45 and F47–F62, and the legacy `data/flags.json`
register runs F01–F27. The reader following the pointer landed on the Flagged page and found
nothing.

**Fixed:** the three pointers now name **F56**, which is the row that actually covers it
("The Application Review Process page was not re-read this pass; its figures are carried forward
from an earlier fetch"). A new build guard, `check_register_cross_references()`, now fails the
build if any generated page cites a flag id, source id, question id or suggestion id that is not
in the register it is pointing at — so the class of defect cannot recur silently.

The two defects are also recorded as two rows in the published register so a reader can see
them rather than only the repair: **F61** states that the canonical compliance register and
platform blueprint had never carried the two agent clauses and that three published pages
pointed at a flag number that does not exist, and **F62** states that IP License §4 was not
read end to end.

### E3 — The two volatile review counts moved again (fixed)

See V18 and V20. The site published the 2026-11-14 reading of both Chefman review widgets; the
live 2026-11-16 reading is 1,307 and 717. The rows were refreshed to the new reading and both
dates are kept in the row note, exactly as flag F19 requires. The averages did not move.

## F · What this pass did not do

* It did not re-read the two FTC pages (S7, S8), the Operating Agreement (S1), the disclosure
  help article (S5), the tracking-ID article (S6), Google's two policy pages (S30, S31), the
  PA-API deprecation notice (S24), the two owner's-manual PDFs (S13, S15) or the Chefman
  sister-SKU product page (S11). Their published values are unchanged and are cited from the
  passes that fetched them. Re-reading them would not change a published value; it would only
  repeat a date.
* It did not read IP License §4 end to end — see the limit stated under A.
* It did not attempt to resolve F1/F2 (which manufacturer model each ASIN ships), F6 (the
  Associates tag inside the short links), F3 (the 450 °F conflict) or F4/F5 (the Emeril preset
  count). None of those is answerable from outside the account holder's browser.
* It did not change any published value that a source did not contradict.

## F2 · The new guard was proved to fire, not just to exist

A guard that has never been seen to fail is a comment. `check_register_cross_references()` was
tested by injecting a violation into the real data and running the real build:

| Test | Injection | Build result |
|---|---|---|
| Positive | `F46` (a flag id that exists in no register), plus `SG-99` and `Q-99`, inserted into a question row in `data/questions.json` | **exit 1** — the build named the offending page, the register and the id, and did not write the site |
| Negative | the data restored byte for byte | **exit 0** — the site rebuilt normally |

The check is now part of the build pipeline, so a dangling pointer cannot reach the published
site again through any of the four registers (flags, sources, questions, suggestions).

## G · Gates run after these changes

Every gate below was run on the working tree that produced this commit, and all of them were
run **after** the last edit, not before it.

| Gate | Result |
|---|---|
| `python3 build.py` | **pass** — 36 pages written, `robots.txt` + `sitemap.xml` (36 URLs), 0 errors |
| `python3 verify.py` | **pass** — 115 pages checked · 46 specification rows (43 verified, 3 blank+flagged) · 34 sources declared · **0 errors, 0 external warnings** |
| `python3 -m unittest discover -s platform/tests -t platform` | **pass** — 33 tests, 0 failures |
| `python3 platform/audit/report.py` | **pass** — `AUDIT PASSED (0 warning(s))`, 0 findings |
| `python3 scripts/check_links.py` | **pass** — 6,425 links, 0 broken |
| `python3 scripts/verify_site.py` | **pass** — 393 assertions, `ALL CHECKS PASSED` |
| `python3 research/check_research.py` | **pass** — `OK — no broken links, no unsourced rows, disclosures present on every page.` |
| `python3 scripts/build_s2_site.py --check` | **pass** — `build current: 16 files` |
| `node --check assets/app.js` | **pass** |
| reproducibility | a second `python3 build.py` leaves `git diff` empty — the generator is deterministic |

The pass-10 ledger itself is `session-9fccce0c/pass10.json` (17 re-read rows, 4 new-evidence
entries) and is rendered on the site's
[`reverification.html`](https://kanlerxz87-cyber.github.io/Zone1/reverification.html) page
under **"Pass 10 — independent re-read"**. The build loads it if the file is present and
omits the section if it is not, so the generator never depends on a session folder existing.

## H · Where the record of this pass lives

| Artefact | Path |
|---|---|
| This report | `reports/verification-2026-11-16-9fccce0c.md` |
| Pass-10 ledger (17 rows) | `session-9fccce0c/pass10.json` |
| Briefing for the owner | `EXECUTIVE-SUMMARY.md` §17 |
| Repository overview | `README.md` → *Pass 10 — 2026-11-16* |
| Claim, plan and outcome | `COORDINATION.md` → *Task board — arena/9fccce0c-zone1* |
| Live ledger | https://kanlerxz87-cyber.github.io/Zone1/reverification.html |
