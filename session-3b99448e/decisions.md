# Zone1 — decisions before implementation: questions, information, answers

Session: `3b99448e` | Branch: `arena/3b99448e-zone1` | Date: 2026-11-15 (UTC)

**Status: decision gate.** No implementation should proceed until each question below has an answer recorded in the Answer column (or an explicit "deferred" with a date). Questions marked **blocking** stop related build/link decisions until answered. Facts cited here come from the repo's official sources (`data/sources.json`); missing information is listed as "not available" and a discovery path is suggested — nothing is inferred.

## How to read this

| Column | Meaning |
|--------|---------|
| Q | Question id |
| Question | What must be known before a decision |
| Blocking? | Yes = related changes are on hold until answered |
| Information we have | What the official sources already confirm (with source link) |
| Information we do NOT have | The gap |
| Suggested answer (pending owner decision) | A proposed answer for the owner to accept or correct |
| How to discover the missing information | Concrete steps to official sources |

## The decision questions

### Q-1 — What is the real Amazon Associates tracking ID (tag)?

| | |
|---|---|
| **Blocking?** | Yes — every affiliate link on the site should carry the tag; links are currently untagged and attribution is unconfirmed. |
| **Information we have** | `data/config.json`: `associate_tag` is `""` (left blank on purpose — no tag was supplied). Amazon requires the tag as a URL parameter on every Special Link (S2 §2(b)). |
| **Information we do NOT have** | The actual tag (format `XXXXXX-20`), whether it is valid, and whether it belongs to this account. |
| **Suggested answer (pending)** | Owner supplies the tag from Associates Central; `build.py` injects it into every outbound Amazon link and the build re-runs. |
| **How to discover** | Log into Associates Central → Manage Tracking IDs (or SiteStripe on any Amazon page while signed in). Source: S6 — https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA. Flagged as F-06/F-10 on `flagged.html`. |

### Q-2 — Are the three supplied links the products the owner intends to market?

| | |
|---|---|
| **Blocking?** | Yes — product identity underpins niche, category, commission rate, and every article topic. |
| **Information we have** | Each short link was followed and landed on an air-fryer listing; candidate ASINs recorded: B0CDY277D3, B09B7SB46R, B08DKYBTPH (S16/S17). But the tokens are 9 characters; an ASIN is 10 characters (S23). `amazon.com/dp/<token>` returns "Page Not Found" (S21). The short links resolve through `plpRedirect=mhFallback`, i.e. Amazon's fallback handler, not a clean product redirect (S17/S22). |
| **Information we do NOT have** | Confirmation that the resolved ASIN is the intended product; the model number on each ASIN (Amazon does not publish it); the tag riding inside each short link. |
| **Suggested answer (pending)** | Treat all three identities as **unconfirmed**; keep the "not confirmed" badge on every product card until the owner confirms each intended product in a logged-in browser. |
| **How to discover** | Open each `link.amazon/...` URL in a normal browser (signed out, then signed in), note the final `amazon.com/dp/ASIN` and page title, and compare with the product the owner meant to promote. Alternatively replace the short links with canonical tagged `/dp/<ASIN>` URLs once Q-1 is answered. |

### Q-3 — What commission rate applies to each product?

| | |
|---|---|
| **Blocking?** | Yes — revenue projections and the "commission potential" analysis depend on it. |
| **Information we have** | Official Table 1 (S3): Kitchen 4.50%; All Other Categories 4.00%. Air fryers are not named in the table. Amazon does not publish which category a given ASIN is assigned to (S3). |
| **Information we do NOT have** | The browse-node category per ASIN, and the account's personalised/custom rate (behind sign-in). |
| **Suggested answer (pending)** | Model revenue at **4.50% Kitchen** as the likely rate, and **4.00% All Other** as the fallback; label both as unverified candidates. Do not present either as confirmed. |
| **How to discover** | Read the breadcrumb on each Amazon listing (Home & Kitchen › … › Air Fryers) or the Associates category report per ASIN. Custom rate card: account's signed-in dashboard (flagged F-05). Source: S3 — https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ |

### Q-4 — Is the Associates account approved and active?

| | |
|---|---|
| **Blocking?** | Partially — content can be built, but links cannot earn until approved. |
| **Information we have** | Application review requires ~3 qualifying sales within 180 days, ~10 posts, content recent within ~60 days, social follower floor ~500 (S4). |
| **Information we do NOT have** | The account's application status, sales-to-date, and 180-day window position. |
| **Suggested answer (pending)** | Unknown until the owner checks Associates Central. Plan content and links assuming approval is pending. |
| **How to discover** | Sign in to Associates Central and check the application status page. Source: S4 — https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM |

### Q-5 — What are current Amazon prices, availability, and star ratings?

| | |
|---|---|
| **Blocking?** | No for publishing (they are deliberately blank); yes for any revenue model that displays them. |
| **Information we have** | Amazon Program Policies §2(b): prices/availability may only be shown when Amazon serves the link or via Creators/PA API. §6(t): reviews/star ratings only via those APIs (S2). This project holds neither, so those fields are blank and flagged. |
| **Information we do NOT have** | Any Amazon price, availability, or rating for the three candidate ASINs. |
| **Suggested answer (pending)** | Continue showing **nothing** from Amazon on the site. Show brand list prices instead (where verified on brand pages, with source links). |
| **How to discover** | Once approved, use the Creators API (PA-API 5 is deprecated — see S24) or SiteStripe to serve Amazon-served pricing. Until then: not available; do not infer from third-party sites. |

### Q-6 — What are the exact model numbers for each candidate ASIN?

| | |
|---|---|
| **Blocking?** | No — but it strengthens every product claim. |
| **Information we have** | Brand pages document models RJ38-SQPF-3TDB-2W (S10/S18) and RJ38-SQSS-8T (S12/S13), matched by capacity/finish/branding — a match, not a confirmation. Amazon does not publish model numbers on ASINs. |
| **Information we do NOT have** | Official confirmation of which model each ASIN ships. |
| **Suggested answer (pending)** | Keep the documented matches, label them "match — not confirmed by Amazon", and flag them (F-2/F-3 area). |
| **How to discover** | Contact Chefman/Emeril support with the ASIN and ask which model number it carries; or read the rating label on the unit. |

### Q-7 — Which niche(s) should the site expand into, if any?

| | |
|---|---|
| **Blocking?** | No — the niche is currently dictated by the product set (air fryers / small kitchen appliances). |
| **Information we have** | All three supplied products are air fryers; observed listings are home-kitchen air frying (S16 titles). |
| **Information we do NOT have** | Owner's appetite for adjacent niches (toasters, pressure cookers, cookware) and data for them. |
| **Suggested answer (pending)** | Stay in air fryers until Q-1/Q-2/Q-3 are answered; expand only after new products are supplied and verified. |
| **How to discover** | Owner decision, informed by the commission table (S3) and available verified product data. |

### Q-8 — Who writes, publishes, and refreshes content, and on what cadence?

| | |
|---|---|
| **Blocking?** | No — but without an owner the suggestions cannot be implemented. |
| **Information we have** | The site is a static GitHub Pages build (`build.py`, `verify.py`); changes require a commit to `main` and a Pages deploy. |
| **Information we do NOT have** | Named owner, publishing calendar, refresh schedule. |
| **Suggested answer (pending)** | Repository owner (`kanlerxz87-cyber`) controls the repo; quarterly re-verification against official sources suggested (T-8 in suggestions.md). |
| **How to discover** | Internal team decision; not an official-source question. |

### Q-9 — How are clicks and conversions tracked without scraping Amazon?

| | |
|---|---|
| **Blocking?** | No — for the static site; yes for any dashboard that shows revenue. |
| **Information we have** | Tracking IDs / sub-IDs for reporting (S6). Program Content must not be fed into analytics aggregation beyond what the program allows (S2 IP License §2(e)). |
| **Information we do NOT have** | Whether the account uses sub-IDs, and what conversion data Associates Central reports. |
| **Suggested answer (pending)** | Use Associates Central reporting + distinct sub-IDs per placement; do not scrape Amazon pages for click data. |
| **How to discover** | Associates Central → reporting dashboard. Source: S6 — https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA |

### Q-10 — Compliance sign-off before publishing affiliate links

| | |
|---|---|
| **Blocking?** | Yes — no affiliate link should go live until disclosure placement and link format are confirmed compliant. |
| **Information we have** | Required disclosure wording (S1 §5; S5); FTC clear-and-conspicuous placement rules (S7/S8/S9); Amazon restricts link shortening that obscures the destination (S2 §2(w)) — `link.amazon/` is flagged (F-07). |
| **Information we do NOT have** | Owner's final disclosure placement per page; confirmed tagged link format. |
| **Suggested answer (pending)** | Disclosure bar above the fold on every page (already built); replace short links with canonical tagged URLs once Q-1/Q-2 are answered. |
| **How to discover** | Review compliance.html (quotes all 16 program/legal requirements with sources); owner signs off. |

## Suggestions for discovering missing information

| # | Action | What it resolves | Where (official source) |
|---|--------|------------------|-------------------------|
| M-1 | Sign in to Associates Central; copy the tracking ID/tag into `data/config.json`; re-run `build.py`. | Q-1, link attribution | S6 — https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA |
| M-2 | Open each `link.amazon/...` short link in a normal browser (signed out, then signed in); record the final `amazon.com/dp/ASIN` and page title. | Q-2 | S17 — the supplied short links themselves |
| M-3 | Read the breadcrumb on each resolved Amazon listing; compare with Table 1 categories. | Q-3 | S3 — rate table; S16 — listings |
| M-4 | Check Associates Central application status page. | Q-4 | S4 — https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM |
| M-5 | Ask Chefman/Emeril support which model number each ASIN carries; record the answer or the lack of one. | Q-6 | Brand sites S10/S12/S14 (support contact via brand pages) |
| M-6 | Once approved, generate tagged links via SiteStripe / Creators API (PA-API 5 deprecated — S24). | Q-5, Q-9 | S19/S20/S24 — Associates Central developer docs |
| M-7 | Set a calendar reminder for quarterly re-verification of brand list prices and the S3 rate table; record results in `reverification.html`. | Q-3 freshness | S3 — rate table; S10/S12/S14 — brand pages |
| M-8 | Draft the disclosure placement (above the fold, near every affiliate link) and have the owner sign off on compliance.html. | Q-10 | S1 §5, S5, S7, S8, S9 |

## Rule for this gate

A question is answered only when the answer is traceable to an official source, or when the owner makes an explicit recorded decision. "We think…", "probably", and third-party blog figures are not answers — they are gaps, and they belong on `flagged.html`, not in a decision.
