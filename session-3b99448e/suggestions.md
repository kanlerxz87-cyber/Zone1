# Zone1 — marketing & content suggestions

Session: `3b99448e` | Branch: `arena/3b99448e-zone1` | Date: 2026-11-15 (UTC)

**Status: suggestions only.** Nothing here changes the site, the data, or any published value. Every suggestion below is a recommendation for the site owner to review and decide on (see the decision register at the end). Facts about the current site and data cite the repo's official sources; everything else is a suggestion, not a claim.

## 1. What the site is today (verified baseline)

- **Live site:** https://kanlerxz87-cyber.github.io/Zone1/ (GitHub Pages, root build from `build.py`)
- **Generator:** `build.py` — stdlib-only static site generator reading `data/*.json`
- **Verifier:** `verify.py` — broken-link, disclosure, source-ID, and price/rating-leak gates
- **Products tracked:** 3 air fryers supplied as `link.amazon/` short links:
  - `https://link.amazon/B04G1MEwY` → candidate ASIN `B0CDY277D3` (Chefman 6 Qt dual-basket, **identity unconfirmed**)
  - `https://link.amazon/B02NbDxp3` → candidate ASIN `B09B7SB46R` (Emeril 26 QT French Door, **identity unconfirmed**)
  - `https://link.amazon/B00hJ57DV` → candidate ASIN `B08DKYBTPH` (Chefman 8 Qt TurboFry, **identity unconfirmed**)
- **What is NOT shown:** Amazon prices, availability, star ratings, review counts — deliberately blank, per Amazon Program Policies §2(b) and §6(t) (source S2) and the FTC's endorsement rules (S7/S8/S9).
- **Commission rates (official, S3):** Kitchen 4.50%; All Other Categories 4.00%. Per-product rate is unverified because Amazon does not publish which category a given ASIN is assigned to.
- **Open irregularities:** published on `flagged.html` — product identity, model-number mapping, commission category, Associates tag visibility, `link.amazon` shortening compliance.

## 2. Design suggestions — polished marketing affiliate website

These are aimed at making the site look and feel like a professional marketing affiliate site rather than a data dump, while keeping the verification discipline.

| # | Suggestion | Why it matters | Recommended path | Decision |
|---|------------|----------------|------------------|----------|
| D-1 | Keep the layout a simple dashboard: sticky sidebar nav, top bar with disclosure, stat tiles, then tables. | Familiar, scannable, loads fast on mobile. | Keep the current `build.py` chrome; tighten spacing and add one accent colour. | Pending |
| D-2 | Lead the landing page with a one-line value proposition, not a data table. | Visitors decide in seconds whether to stay. | Hero band: "Air fryer buying data, verified line by line against manufacturer pages and Amazon's own program rules." | Pending |
| D-3 | Put the Amazon Associates + FTC disclosure above the fold on every page (already done via `build.py` disclosure bar). | Required by Amazon (§5 Operating Agreement, S1) and the FTC (S7/S8/S9); builds trust. | Keep the disclosure bar; add a one-line "why you see this" link to compliance.html. | Pending |
| D-4 | Product cards: verified specs only; blank cells stay blank with a "flagged" pill; each row links to its official source. | Transparency is the differentiator vs. AI slop sites that invent specs. | Reuse the existing table pattern; never fill a blank with a guess. | Pending |
| D-5 | No product photos hotlinked from Amazon; use no photos or only brand-supplied assets with permission. | Amazon's trademark/IP license (S2) restricts how Program Content (images, links) may be used. | Spec-based cards instead of photo-led cards; link to the brand page instead of embedding. | Pending |
| D-6 | Comparison matrix: verified specs side by side, gaps visible, no price column. | Amazon §2(b) restricts price display; showing gaps is honest and defensible. | Keep `compare.html` as-is (verified-only matrix). | Pending |
| D-7 | Category subpages: Kitchen → Air fryers → one page per product, plus the category index. | Gives Google clear topical sections and internal-link paths. | Keep `categories/kitchen-appliances.html`; add one page per category as new products are added. | Pending |
| D-8 | Add JSON-LD (Organization, BreadcrumbList, Product where verified) and meta descriptions to every page. | Helps search engines understand the site; improves click-through from results. | Add to `build.py` page templates; keep it static (no JS). | Pending |
| D-9 | Mobile-first: single-column stack below ~640px, readable touch targets, no horizontal scroll. | Most affiliate traffic is mobile. | Verify with Chrome DevTools device emulation before each release. | Pending |
| D-10 | Accessibility: colour contrast ≥ 4.5:1, focus-visible outlines, alt text on images, semantic headings. | Legal good practice; excludes no readers. | Audit the CSS variables against WCAG AA once per quarter. | Pending |

## 3. Content suggestions — catchy, trendy articles and topics

All topics are in the air fryer / small kitchen appliance niche dictated by the supplied products (the niche comes from the product set; it was not chosen independently). Titles are working titles. None of these articles may claim the writer tested a product (Amazon §6(t) and FTC §255.5 prohibit experience claims without substantiation — see source S8) and none may state a price or rating that Amazon hasn't served.

| # | Working title | Format | Hook / angle | Verified facts available to cite |
|---|---------------|--------|--------------|----------------------------------|
| A-1 | "Air fryer vs. toaster oven: which one actually earns its counter space?" | Comparison explainer | Form-factor choice, not brand praise. | Capacity, temperature ranges, presets from brand pages/manuals (S10/S12/S13/S14/S15). |
| A-2 | "Dual-basket air fryers: cook two dinners at once — and the sync problem nobody mentions" | Product explainer | Chefman 6 Qt dual-basket/Sync Finish mechanics. | "Two 3-quart baskets", Sync Finish, Sync Baskets, HI-FRY 450 °F 2 minutes (S10/S18). |
| A-3 | "What '450 °F Hi-Fry' actually means (and what it doesn't)" | Myth-busting explainer | A marketing term explained precisely. | HI-FRY definition from the RJ38-SQPF-3TDB-2W manual: 450 °F/235 °C for 2 minutes, a finish mode (S18); conflict with brand page for a different model flagged (F-02/F36). |
| A-4 | "6 Qt vs 8 Qt vs 26 QT: how much air fryer capacity do you actually need?" | Buying guide | Capacity by household size. | 6 Qt / 5.67 L (S10), 8 Qt for 4–6 people (S12), 26 QT / 1519 cu in (S14/S15). |
| A-5 | "How to read an air fryer spec sheet without the marketing fluff" | Editorial | Teaches readers to verify claims themselves — trust content. | Preset-count conflicts (F-03/F-04), "10-in-1" vs 24 presets (F-5), temperature-range conflict between Amazon title and brand page (F-3). |
| A-6 | "24 vs 25 presets: does preset count even matter?" | Explainer | Turns a brand-page conflict into reader value. | Emeril spec strip says 25, description says 24, manual names 24 (F-3/F-4/F-5). |
| A-7 | "Why this site doesn't show Amazon prices" | Compliance explainer | Explains blank price cells; builds credibility. | Amazon Program Policies §2(b)/§6(t) (S2); FTC disclosure guidance (S7/S8). |
| A-8 | "Chefman vs. Emeril: stainless steel vs. glass door, 8 Qt vs. 26 QT" | Brand comparison | Two real products, verified specs only, gaps shown. | Chefman 8 Qt (S12/S13); Emeril 26 QT (S14/S15); both brand-site ratings (not Amazon's). |
| A-9 | "Amazon Associates disclosure: what 'As an Amazon Associate I earn from qualifying purchases' actually means" | Policy explainer | Disclosure explained for readers; signals compliance. | Amazon Operating Agreement §5 (S1); FTC Endorsement Guides (S7/S8/S9). |
| A-10 | "Air fryer cooking without oil: what '98% less oil' really says" | Claim check | Reproduces a brand claim as a claim, not a fact. | Chefman "98% less oil" marketing claim, labelled as vendor claim (S12). |

Editorial rules to avoid reading like AI slop:

- **No unverified superlatives:** never "best", "top-rated", "revolutionary", "must-have", "game-changing". If it isn't sourced, don't say it.
- **One topic per page; dates on every page:** "Last verified 2026-11-15" keeps content honest and helps Google's freshness signals.
- **Human voice:** contractions, questions, short sentences mixed with longer ones, specific numbers instead of vague intensifiers ("very", "really", "incredible").
- **Show the gaps:** blank cells, flagged conflicts, "unconfirmed" identity badges are content, not bugs. A site that admits what it doesn't know is trusted more than one that invents.
- **Label vendor claims:** anything the manufacturer says about its own product is marked "brand claim — not independently tested".
- **No invented testing:** never say "we tested", "we cooked", "our pick". The site does not test products.
- **Disclosure on every page:** the Amazon Associates statement + FTC-style wording must appear on every article (already enforced by `build.py`).

## 4. Organic traffic suggestions

| # | Suggestion | How to execute | Policy guardrail |
|---|------------|----------------|------------------|
| T-1 | Target long-tail informational + commercial-intent keywords from the verified data (e.g. "dual basket air fryer sync finish", "air fryer capacity for 4 people", "Hi-Fry 450 °F meaning"). | One article per keyword cluster (A-1…A-10), internal links between them. | None (editorial content). |
| T-2 | Build programmatic category/comparison pages from the verified data tables (one page per category, one per product pair). | `categories/kitchen-appliances.html` is the template; `compare.html` is the comparison template. | No prices/ratings from Amazon unless Amazon serves them (S2 §2(b)/§6(t)). |
| T-3 | Ship `sitemap.xml` and `robots.txt` (already present in root). | Keep them regenerated by the build; submit sitemap via Google Search Console once the site is owned by the account holder. | None. |
| T-4 | Internal linking hub: Dashboard → Category → Product → Guide → Article → Flagged page. | Every product page links to its category, its guide, its specs' sources, and the flagged items affecting it. | None. |
| T-5 | Compete on transparency, not price data. Tagline idea: "The affiliate site that shows its gaps." | Publish `flagged.html` prominently in nav; explain blanks in a callout on every product page. | Reinforces compliance positioning. |
| T-6 | Social: Pinterest + TikTok + YouTube Shorts for air fryer visuals (capacity demos, basket comparisons). | Short vertical video; link in bio to the relevant category page; no Amazon price claims in captions. | No price/availability claims unless sourced from Amazon-served data (S2). |
| T-7 | Email capture: "Air fryer recipe + capacity guide of the week." | Simple static capture form handled by a third-party newsletter provider; double opt-in. | FTC: clear disclosure that sign-up is marketing; no affiliate content in email unless disclosed. |
| T-8 | Refresh cadence: re-verify brand list prices, ratings and commission-category assumptions quarterly against official sources. | Re-read chefman.com / emerileveryday.com product pages and the S3 rate table; record in `reverification.html`. | Brand prices change; always stamp the access date and keep the old value in the ledger. |

## 5. Compliance framing for all of the above

- Amazon disclosure wording (§5 Operating Agreement, S1): **"As an Amazon Associate I earn from qualifying purchases."** — must appear on every page with affiliate links.
- FTC-style wording (S7/S8): **"I get commissions for purchases made through links on this page."** — clear and conspicuous, near the links, not buried in a footer.
- Link shortening: `link.amazon/` is flagged (F-07/F-10 area). Amazon Program Policies §2(w) concerns link shortening that obscures the destination. Recommendation: replace short links with canonical tagged `/dp/<ASIN>` URLs once the Associates tag is confirmed (see Q-1/Q-2 in decisions.md).
- IP License (S2 §2(e)): do not use Creators/PA API or Data Feeds to aggregate, analyse, extract or repurpose Program Content, or to train/fine-tune ML models. Any "AI product research" feature must run on non-Program-Content inputs.

## 6. Decision register — review before implementing

Each row is a suggestion the owner can approve, reject, or modify before any code or content change.

| # | Suggestion | Options considered | Recommended path | Decision | Notes |
|---|------------|-------------------|------------------|----------|-------|
| R-1 | Adopt the dashboard layout with hero band (D-1/D-2) | Keep as-is / redesign / hero band | Hero band + existing dashboard | Pending | Low risk; additive to index.html |
| R-2 | Publish suggestions + decisions pages on the site | Not published / PDF only / HTML pages | HTML pages linked from nav | Pending | This document pair |
| R-3 | Article series A-1…A-10 | Publish all / pilot 3 / none | Pilot A-1, A-3, A-7 first | Pending | Pilot tests the voice rules |
| R-4 | Traffic plan T-1…T-8 | All channels / search first / social first | Search (T-1/T-2/T-3) first | Pending | Social needs content inventory first |
| R-5 | Replace `link.amazon/` short links with canonical tagged URLs | Keep short links / replace once tag confirmed / remove | Replace once Associates tag confirmed | Pending | Depends on Q-1/Q-2 (decisions.md) |
| R-6 | Quarterly re-verification cadence (T-8) | Quarterly / annually / never | Quarterly | Pending | Requires owner calendar reminder |

**How to use this register:** read each row, choose Approved / Rejected / Needs more info, record the choice and date in the Decision column, then implement only Approved rows. Rejected rows stay on the register so they are not re-proposed. Needs-more-info rows link to the open questions in `decisions.md`.

## Sources

- S1: Amazon Associates Program Operating Agreement — https://affiliate-program.amazon.com/help/operating/agreement
- S2: Amazon Associates Program Policies — https://affiliate-program.amazon.com/help/operating/policies
- S3: Standard Commission Income Statement — https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ
- S4: Application Review Process — https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM
- S5: Associate identification / disclosure — https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98
- S6: Tracking IDs — https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA
- S7: FTC Endorsement Guides Q&A — https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- S8: FTC Disclosures 101 — https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
- S9: 16 CFR Part 255 — https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255
- S10–S27: brand and Amazon official pages listed in `data/sources.json`
