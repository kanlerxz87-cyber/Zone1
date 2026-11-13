# Executive Summary

**Project:** Amazon Associates property covering three air fryers, with a verification and
compliance layer.
**Audit date:** 13 November 2026 (UTC)
**Live site:** https://kanlerxz87-cyber.github.io/Zone1/
**Repo:** https://github.com/kanlerxz87-cyber/Zone1

> As an Amazon Associate I earn from qualifying purchases.
> I get commissions for purchases made through links on this site.

---

## 0. Two builds, one repository

This brief was worked by two agent sessions independently. Neither overwrote the other. Both are
published:

| | Build A | Build B (this document's primary subject) |
| --- | --- | --- |
| Session | `d14c5409` | `1874bb64` |
| Live at | `docs/` — the **root** Pages URL | `site/` |
| Fields verified | 18/30 (60%) | 40/53 (75%) |
| Compliance rows | 11 | 20 |
| Open review items | 16 | 17 |
| Commission rate | recorded unreachable (F02) | **published: Kitchen 4.50%** |

Both sessions independently resolved the same three short links to the same three ASINs. Build B
closed the one substantive gap build A left open — the commission rate — and added manufacturer
specification verification against the brands' own product pages. Build B did **not** edit build A's
data files, so build A's own records still show that gap honestly. The coexistence of two live sites
is recorded as **F-16** and needs one decision from the owner: keep `docs/` canonical at the root
(recommended, since it already is), or repoint Pages to `site/` and retire `docs/`.

Full reconciliation: [`COORDINATION.md`](COORDINATION.md).

---

## 1. What was delivered

A static, GitHub-Pages-hosted dashboard covering the three supplied Amazon products. It publishes:

| Deliverable | Count | Where |
| --- | --- | --- |
| Products with full sourced specification sheets | 3 | `/products.html` |
| Specification fields audited, each with a status and a source | 53 | `/products.html` |
| Official source documents in the registry | 16 | `/sources.html` |
| Amazon / FTC compliance requirements, quoted and implemented | 20 | `/compliance.html` |
| Irregularities and open items published for review | 17 | `/flagged.html` |
| Buying guides argued only from verified specs | 3 | `/guides.html` |
| Automated assertions run on every build | 381 | `scripts/verify_site.py` |

Every figure on every page is generated from `data/*.json`. There is no hand-typed number in any
template, and the verifier fails the build if an unsourced value reaches a page.

## 2. The three products

| Product | ASIN | Model | Capacity | Published rate |
| --- | --- | --- | --- | --- |
| CHEFMAN 6 Quart Dual Basket Air Fryer Oven | `B0CDY277D3` | `RJ38-3DBW-V2` | 6 Qt (2 × 3 Qt) | 4.50% |
| Emeril Lagasse 26QT French Door Air Fryer Toaster Oven | `B09B7SB46R` | `4-00675-02A-VN` | 26 Qt / 24.6 L | 4.50% |
| Chefman Air Fryer 8 Qt TurboFry 4-in-1 | `B08DKYBTPH` | `RJ38-8T-BLACK` | 8 Qt / 7.57 L | 4.50% |

All three are air fryers, placing them in Amazon's **Kitchen** category at a published standard
rate of **4.50%**
([Amazon Standard Commission Income Statement, Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ)).
That is the public table rate. The account-specific custom rate card sits behind sign-in and was
not read, so no personalised rate is claimed (**F-05**).

**The three are not substitutes.** Capacities span 6 Qt, 8 Qt and 26 Qt — a 4.3× range. They
answer three different buying questions, which is why the guides route by situation rather than
declaring one winner.

## 3. The headline finding

**The most consequential finding is not a product ranking — it is a compliance constraint that
changes what the site is allowed to show.**

Amazon's Associates Program Policies permit publishing prices and availability only if Amazon
serves the data or it is obtained through the Creators API / PA API (§2(b)), and permit displaying
Amazon reviews and star ratings only from those same APIs (§3(t)). Neither condition is met here.
The same policies also prohibit price-tracking and price-alert functionality outright (§3(y)).

So this site publishes **no Amazon prices, no Amazon availability, and no Amazon star ratings**.
Every one of those cells is blank and links to the flag **F-08** explaining why. Most affiliate
sites fill those cells in from a scrape and hope. That shortcut is the single largest compliance
exposure in this category, and this build removes it rather than documenting it as a risk.

The practical cost is honest: the comparison table is less useful than one with prices in it. The
practical fix is also known — Creators API access — and it is recommendation 3 below.

## 4. The blocker that matters most

**No Amazon Associates tag is configured, so no link on this site can currently earn commission.**

Amazon requires the Associate tag as a URL parameter on every Special Link
([Program Policies §2(b)](https://affiliate-program.amazon.com/help/operating/policies)). Without
it, an outbound link is just a link. The site is architected for this: one value in
`data/config.json` plus a rebuild converts every product link into a tagged Special Link, and the
build validates the tag format before using it.

Until that is done, every page displays a visible warning, and **F-10** is marked high severity.
This is a sub-two-minute fix and it is the highest-value action available.

## 5. Fit ranking, and exactly what it does and does not mean

| Rank | Product | Composite | Basis |
| --- | --- | --- | --- |
| 1 | Chefman TurboFry 8 Qt | 82.8 | Strongest brand-store sentiment (4.6/5, 200 reviews), most complete verified spec sheet, 8 Qt in the target band |
| 2 | CHEFMAN 6 Qt Dual Basket | 81.0 | Cheapest brand-store entry, richest confirmed feature set, but 6 Qt total and a 30-review base |
| 3 | Emeril Lagasse 26 QT | 59.5 | Broadest capability by far, but weakest brand-store sentiment (2.6/5, 25 reviews), highest price, least complete verified spec sheet |

**This is a merchandising-fit score, not a demand forecast.** It combines five factors that can each
be traced to a source, using weights that are published on the method page. Amazon publishes no
per-ASIN sales volume, search volume or conversion rate, and third-party tools that estimate them
produce figures that cannot be verified or reproduced — so they are excluded (**F-13**). Any site
that shows you a confident "conversion rate" for an ASIN is showing you a number it invented.

The ranking is also genuinely close between first and second (82.8 vs 81.0) and would flip if the
weights changed. That is stated rather than hidden, because a score whose sensitivity is concealed
is worse than no score.

## 6. Evidence quality, stated plainly

**Solid — read directly off first-party pages:**

- Capacity, wattage, temperature range, function counts, certifications, warranty and model numbers
  for both Chefman units, from Chefman's own product pages, with model numbers matching exactly.
- All physical specifications for the Emeril unit except wattage and certification.
- The Amazon commission rate, the attribution windows (24-hour session, 89-day cart, 180-day
  ship-and-pay), and the required disclosure sentence — all quoted from Amazon's own documents.
- The FTC's affiliate-disclosure guidance, quoted from ftc.gov and 16 CFR §255.

**Weak, conflicting or absent:**

- **Demand data.** No official source exists. The fit score is not a demand forecast (**F-13**).
- **The Emeril unit.** Wattage and safety certification unconfirmed (**F-09**); three different
  preset counts appear on the same brand page — 25, 24 and "10-in-1" (**F-03**).
- **Review sentiment.** Only brand-storefront ratings were reachable, and a 25-review brand sample
  is not comparable to a marketplace rating (**F-12**).
- **Link fidelity.** All three supplied short links landed through a `plpRedirect=mhFallback`
  redirect marker. The ASIN mapping rests on the redirect target, not on the link text (**F-01**).
- **The "Hi-Fry" claim** on the 6 Qt unit's Amazon title does not appear in Chefman's specification
  for the matching model (**F-02**).
- **Finish conflict** on the 8 Qt unit: Amazon says "Stainless Steel", Chefman says "matte-black"
  (**F-04**).
- **Category evidence** was read directly for one ASIN only; the other two are inferred from title
  and brand page (**F-06**).

## 7. Compliance posture

Twenty requirements are recorded in `/compliance.html`, each with the operative sentence quoted and
the specific implementation named. The five prohibitions that shaped the build most:

| Prohibited by Amazon | Policy | What this site does instead |
| --- | --- | --- |
| Price tracking / price alerts | §3(y) | Not built, and stated as a permanent non-feature |
| Amazon prices & availability without API data | §2(b) | Blank cells, labelled unverified |
| Amazon reviews & star ratings without API data | §3(t) | Brand-store ratings only, always labelled as such |
| Cloaked or indirect outbound links | §3(v) | Full `amazon.com/dp/<ASIN>` printed; build rejects anything else |
| Click incentives / rebates / points | §3(g) | None exist anywhere in the build |

The Amazon-required disclosure sentence — *"As an Amazon Associate I earn from qualifying
purchases."* — appears verbatim in the footer of every page, plus the FTC's own suggested
plain-language wording beside the links. The FTC warns that "affiliate link" alone is inadequate
and that a single site-wide notice is insufficient, so the disclosure is a repeatable component on
every page, and the verifier fails if any page lacks it.

## 8. Recommendations, in priority order

1. **Set the Associates tag in `data/config.json` and rebuild.** Nothing earns until this is done.
   **F-10.**
2. **Re-check the three short links in a normal browser** and replace them with canonical tagged
   `/dp/<ASIN>` URLs. **F-01.**
3. **Apply for Creators API / PA API access.** This is the only lawful route to showing Amazon
   prices and ratings, and it is what would make the comparison table genuinely useful. **F-08.**
4. **Resolve the Emeril wattage and certification** from the manual or the unit's rating label
   before publishing any claim about it. **F-09.**
5. **Confirm the Chefman 6 Qt model number against the Amazon SKU** to settle the "Hi-Fry"
   discrepancy. **F-02.**
6. **Only then** build click accounting server-side and read conversions from the Associates
   dashboard. **Never** build a price tracker. **F-11, F-13.**

## 9. Where the platform blueprint stands

The brief asked for automated research, niche scoring, content generation, publishing, click and
conversion tracking, and continuous optimisation. Being precise about what this delivery actually
contains:

| Blueprint capability | Status | Reality |
| --- | --- | --- |
| Product research and verification | Implemented | The sourced data layer plus build-time assertions |
| Commission-potential analysis | Implemented | 4.50% Kitchen rate sourced; arithmetic shown, volume deliberately blank |
| SEO-oriented guides and comparisons | Implemented | Three situation-based guides and a comparison page, verified specs only |
| Pricing and competition analysis | Partial, deliberately limited | Brand-store prices only; no Amazon price; no tracker (§2(b), §3(y)) |
| Affiliate link management | Partial | Rendering and validation built; the tag itself is missing (**F-10**) |
| Click and conversion tracking | Not shipped | A static site cannot truthfully do it; data lives in the Associates dashboard (**F-11**) |
| Continuous campaign optimisation | Not shipped | Optimising without observed traffic would be theatre (**F-13**) |
| Policy and disclosure compliance | Implemented and enforced | 20 requirements quoted and implemented; verifier asserts them |

Nothing in the "not shipped" rows was skipped for convenience. Each is either prohibited by policy,
impossible on a static host without inventing data, or genuinely dependent on traffic that does not
exist yet. Publishing a convincing dashboard full of estimated conversions would have been easy and
would have been false.

## 10. Reproducing any number on the site

```bash
python3 scripts/build_site.py    # regenerate every page from data/*.json
python3 scripts/verify_site.py   # 381 assertions; exit 0 = all passed
```

To change a published value you must change its source. To publish an unsourced value, the verifier
has to be defeated first. That is the whole design.

---

*Data verified 13 November 2026 against the official sources listed on the Sources page. This site
is not endorsed by, sponsored by, or affiliated with Amazon or with any brand named here.*
=======
# Executive summary — Amazon affiliate product research (as of 2026-11-13)

**Live site:** https://kanlerxz87-cyber.github.io/Zone1/ (served from `main` at `/`; a root redirect opens `docs/`)
**Repository:** https://github.com/kanlerxz87-cyber/Zone1
**Branch:** `arena/d14c5409-zone1` (based on `main` @ `42f4036`)

## What was requested vs. what was delivered

| Request | Delivered | Status |
|---|---|---|
| Review the repo line by line against official sources, flag irregularities | `REVIEW.md`, `data/flags.json` (16 flags), Flagged for Review page | Done |
| Live GitHub Pages site: clean landing page, category subpages, simple tables with analysis | Overview, Home & Kitchen › Air Fryers, Analysis, Compliance, Sources, Flagged for Review | Done (pending deploy check) |
| Every table row linked to an official source; unverified values blank and flagged | Every product row links to its amazon.com product page; 40% of fields are blank, all flagged | Done |
| Coordinate through COORDINATION.md | Claims, handoffs and task status recorded | Done |
| Full AI affiliate platform (product discovery, trend/niche detection, price and competition analysis, article generation, click and conversion tracking, optimization) | **Not built.** Requires Amazon Creators API / PA-API credentials, an Associates account and analytics access, none of which are available here. No data was invented to stand in for them. | Blocked — see F11 |
| Executive summary | This document, and the Overview page | Done |

## The three products

| # | Submitted link | ASIN (resolved) | Title as shown (brand / capacity / type) | Official source |
|---|---|---|---|---|
| P1 | https://link.amazon/B04G1MEwY | B0CDY277D3 | CHEFMAN 6 Quart Dual Basket Air Fryer Oven · Home & Kitchen | [amazon.com/dp/B0CDY277D3](https://www.amazon.com/dp/B0CDY277D3) |
| P2 | https://link.amazon/B02NbDxp3 | B09B7SB46R | Emeril Lagasse 26QT French Door Air Fryer Toaster Oven · Home & Kitchen | [amazon.com/dp/B09B7SB46R](https://www.amazon.com/dp/B09B7SB46R) |
| P3 | https://link.amazon/B00hJ57DV | B08DKYBTPH | Chefman Air Fryer 8 Qt TurboFry · Home & Kitchen | [amazon.com/dp/B08DKYBTPH](https://www.amazon.com/dp/B08DKYBTPH) (interstitial on retrieval; identity confirmed through the short link) |

## Key findings

1. **Identity verified.** All three short links resolve to Amazon.com product pages with different ASINs, all listed under Home & Kitchen (page titles).
2. **Coverage.** 18 of 30 product fields (60%) are verified or derived. The 12 blank fields are price, rating, review count and commission rate for each product.
3. **No price, review or commission analysis is possible** from the sources reachable here. Amazon product-detail text did not render, and the official commission schedule redirected to a sign-in page. Third-party rate tables conflict with each other, so none were used.
4. **Brand overlap.** Two of three titles name Chefman (casing differs: “CHEFMAN”, “Chefman”). Whether they are the same brand listing is not confirmed.
5. **Compliance gaps.** None of the links carries an Associates tag. Associates Program Policies require one (Participation Requirements s.2(b)). The required disclosure statement is shown with an "enrollment pending" status, because the account is not confirmed.

## Top items needing an owner decision (High severity)

- **F01** Price, rating, review count and availability are blank. Provide Creators API / PA-API access, or review the pages manually.
- **F02** The Home & Kitchen commission rate is unverified. Check it on Associates Central while signed in.
- **F03** The links carry no Associates tag. Provide the Associates ID for tagging. No ID has been invented.
- **F06** The disclosure cannot be shown as active until enrollment is confirmed. Then set `associates_status` to `"active"` in `data/site.json` and rebuild.
- **F11** The full AI platform is not built, because the required API and account data are not available.

Medium and low items (short-link codes, redirect-link rule, non-US account clause, marketplace, repo hygiene, commit-author visibility, process notes) are listed with sources on the Flagged for Review page.

## Sources used

- Amazon.com product pages: S1 [amazon.com/dp/B0CDY277D3](https://www.amazon.com/dp/B0CDY277D3), S2 [amazon.com/dp/B09B7SB46R](https://www.amazon.com/dp/B09B7SB46R), S3 [amazon.com/dp/B08DKYBTPH](https://www.amazon.com/dp/B08DKYBTPH) (interstitial)
- Short-link resolution: S4 [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY), S5 [link.amazon/B02NbDxp3](https://link.amazon/B02NbDxp3), S6 [link.amazon/B00hJ57DV](https://link.amazon/B00hJ57DV)
- Associates Operating Agreement (updated 15 Oct 2025): [affiliate-program.amazon.com/help/operating/agreement](https://affiliate-program.amazon.com/help/operating/agreement) — S7
- Associates Program Policies (updated 14 Apr 2026): [affiliate-program.amazon.com/help/operating/policies](https://affiliate-program.amazon.com/help/operating/policies) — S8
- Commission schedule, not reachable: [affiliate-program.amazon.com/help/operating/schedule](https://affiliate-program.amazon.com/help/operating/schedule) — S9
- FTC, Disclosures 101 for Social Media Influencers (Nov 2019): [ftc.gov](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) — S10
- GitHub Docs, publishing from a branch folder: [docs.github.com](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) — S11
- This repository: [github.com/kanlerxz87-cyber/Zone1](https://github.com/kanlerxz87-cyber/Zone1) — S12

## Verification performed

- Each short link was resolved and each product title, ASIN and department was read from the resolved page.
- Each policy quote was read from the official page and checked against its section number.
- The build validates that every verified value has a source, every unverified value is blank, every official link is on an official host, and every internal link resolves.
- Limitation: a visual check in a browser was not possible in this sandbox. Layout was checked structurally (HTTP 200 on every page, balanced HTML tags, table rows present).
>>>>>>> origin/main
