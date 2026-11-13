# Executive summary — Zone1 Amazon affiliate research & publishing platform

**As of:** 2026-11-13
**Live site:** https://kanlerxz87-cyber.github.io/Zone1/
**Repository:** https://github.com/kanlerxz87-cyber/Zone1
**Published site:** the thirteen-page static site at the repository root

---

## 1. What was asked, and what is delivered

| Request | Delivered | Where |
|---|---|---|
| AI-powered Amazon affiliate platform for three supplied products | The parts that do not need a third-party credential are built and published: product research, link resolution, pricing/review/demand/competition analysis, a commission model, niche discovery, SEO content generation, affiliate-link management, a campaign and tracking plan, a compliance register, and an automated build-and-verify pipeline. The parts that need an Amazon API credential or an analytics account are specified as executable automation rules and published as open items — **no traffic, conversion or commission figure is invented**. | [`pages/`](pages/), [`data/program.json`](data/program.json) |
| Executive summary | This document and the one-page site version | [`pages/executive-summary.html`](pages/executive-summary.html) |
| Clean, simple GitHub Pages site with a landing dashboard and category subpages | Thirteen static pages, no runtime dependency, responsive, keyboard-navigable | [`index.html`](index.html) |
| All entries and analysis in readable tables | Every attribute, finding, rule, source and flag is a table row with a source cell | all pages |
| Verified marketing content for the three links | SEO article, head-to-head comparison, buying guide — each with the disclosure directly above every monetised block | [`pages/marketing/`](pages/marketing/) |
| Repo review, line by line, with official-source links and irregularities flagged | 37 review rows across repository state, data, content, compliance and process, each with its source | [`REVIEW.md`](REVIEW.md) |
| A "Flagged for Review" page with unconfirmed values and irregularities, unconfirmed fields left blank | 24-item register plus a per-attribute table of every blank value and why it is blank | [`pages/flagged.html`](pages/flagged.html) |
| Full autonomous completion — build, test, PR, merge, verify deployment | Done; the PR URL, merge commit and deployment result are recorded in the board | [`COORDINATION.md`](COORDINATION.md) |

---

## 2. The three products, as verified

The supplied `link.amazon` URLs are **not** product identifiers. Each path segment looks like
an ASIN but resolves to a different product, so every link in this project was rebuilt from
the destination ASIN.

| # | Supplied link | Resolved ASIN | Product | Rating / ratings | Demand | Best Sellers Rank | Verified price snapshot |
|---|---|---|---|---|---|---|---|
| P1 | [`link.amazon/B04G1MEwY`](https://link.amazon/B04G1MEwY) | `B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven | 4.2 / 4,859 | 1K+ bought in past month | #5,644 Kitchen & Dining · #35 Air Fryers | New **$79.93** (list $99.99, −20%); separate **$57.45** offer tagged `USED` by Amazon |
| P2 | [`link.amazon/B02NbDxp3`](https://link.amazon/B02NbDxp3) | `B09B7SB46R` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | 4.3 / 18.3K | 4K+ bought in past month | not verified | Deal **$149.99** (list $209.99); alternate offer $92.99 |
| P3 | [`link.amazon/B00hJ57DV`](https://link.amazon/B00hJ57DV) | `B08DKYBTPH` | Chefman Air Fryer 8 Qt TurboFry 4-in-1 | 4.4 / 16,861 | 3K+ bought in past month | #537 Kitchen & Dining · #8 Air Fryers | New **$79.91** (list $119.99); used $51.94 |

Each cell above is a reading of an official Amazon page taken on 2026-11-13, and every row
in the site carries the exact URL it was read from. The full per-attribute record — including
the attributes that are blank and why — is on the [catalogue](pages/catalog.html) and
[research](pages/research.html) pages.

**Two irregularities in the data itself**, both published rather than smoothed over:

- **Amazon renders a used offer without saying so.** For P1, Amazon's own embedded buy-box
  payload lists exactly two offers — `$79.93` with `buyingOptionType: NEW` and `$57.45` with
  `buyingOptionType: USED` — but the rendered price block next to `$57.45` shows only
  "43 percent savings" and the same "$99.99" list price, with no condition word beside it.
  The site publishes `$57.45` as the **used-condition** offer and says so (flag F-02).
- **Amazon states two different capacities for P1.** The structured details render
  `Capacity: 6 liters` while the title and the manufacturer bullets state a 6-quart combined
  capacity. Both are published side by side (flag F-06).

---

## 3. What the analysis says

- **Demand signal.** All three listings carry a "bought in past month" badge and a
  Best Sellers Rank, and all three sit inside the Amazon.com Air Fryers category. That is
  the only demand evidence this project will publish: there is no official source for search
  volume, keyword difficulty, competitor traffic or category conversion rates, so the niche
  map is built from Amazon's own published signals and says so where a benchmark would
  normally appear (flag F-13).
- **Competition.** Amazon's own pages surface the competitive set for each product; the
  site publishes that set with each competitor's price read from the same page.
- **Commission.** The official rate card redirects to a sign-in wall, so **no rate is stated**
  and no third-party rate table is used. The research page ships the earnings-per-click
  *model* — commission rate × price × click-through × conversion — with every input labelled
  as a placeholder the publisher fills in from their own dashboard (flag F-04).
- **Niche.** The two Chefman listings compete against each other in the dual-basket and
  sub-9-quart segments; the Emeril Lagasse listing occupies a different format (26-quart
  French-door, 24 functions, rotisserie). Both brands were confirmed from their own Amazon
  brand pages, not assumed from the spelling.

---

## 4. Compliance position

Quoted from the [Associates Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement),
the [Program Policies](https://affiliate-program.amazon.com/help/operating/policies), the
[FTC's Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers),
the [FTC Endorsement Guides FAQ](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking)
and the [16 CFR Part 255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255):

- **Disclosure.** "As an Amazon Associate I earn from qualifying purchases." appears in the
  footer of every page, with the FTC's "qualifying purchases made through our links" wording
  immediately above every monetised block. Disclosures are never only at the foot of a page.
- **Links.** Every outbound link is a direct Special Link to the product detail page with
  the publisher's `tag`. No supplied short link is reused — a redirect hop would obscure the
  destination from the reader, breach the rule against link shortening, and disqualify the
  purchase.
- **No invented claims.** No commission rate, no product performance claim, no review
  sentiment that was not read from the product page, no delivery promise.
- **No scraping.** Amazon's `robots.txt` disallows a long list of AI agents and the Program
  licence prohibits data-mining and model-training on Program Content, so no build-time
  Amazon scraping exists in this project (flag F-10).
- **Non-US publisher.** The Program Policies' Participation Requirements section 1 clause
  for non-US publishers applies to this project's owner in Oslo, and all three listings are
  Amazon.com (United States) marketplace values. Both are published as open items
  (flag F-14).

**Two gates must be closed before the site takes live traffic**, and both are on the
compliance page with the exact policy wording: static price display (F-07) and static
star-rating and review display (F-08). Both have two documented compliant routes — source
the values through Creators API / PA API so each carries a compliant link, or remove those
columns from the published pages and keep them in the internal research record.

---

## 5. Open items needing an owner decision

The full register is 24 items on the [Flagged for Review](pages/flagged.html) page, each
with its observation, its official source and the action taken. The high-severity ones:

| ID | Item | What the owner has to decide |
|---|---|---|
| F-04 | The Associates rate card is not publicly readable | Supply the publisher's own rate from their dashboard, or leave the rate blank |
| F-07 | Prices may only be displayed if Amazon serves them or they come from PA API / Creators API | Pick route 1 (API-sourced prices) or route 2 (remove the price columns) |
| F-08 | Star ratings and reviews need an API-sourced link | Pick route 1 (API-sourced ratings) or route 2 (remove the rating columns) |
| F-10 | Amazon's robots policy disallows AI and research agents | Accept that no automated Amazon fetching is possible, or supply an approved data path |
| F-14 | Non-US publisher clause and United States marketplace values | Confirm the account's tax position and the delivery destination |
| F-19 | Associates enrolment is not confirmed | Supply the Associates ID and confirm the account, then make the required statement active |
| F-20 | Live click/conversion tracking needs an API credential and an analytics account | Supply the credential, or run the campaign unmeasured |

---

## 6. How the result was verified

- **Every published value** was read from an official Amazon, Amazon Associates, FTC, eCFR
  or GitHub page. The URL is attached to the row.
- **Every blank value** is blank on purpose, and the Flagged for Review page lists each one
  with the reason it could not be confirmed.
- **`tools/check_links.py`** runs offline over the committed site and the datasets and
  fails on any of: a dataset that does not parse or is missing a schema key; a verified
  field with no source, a non-official source or a blank value; an unverified field that
  carries a value; a dangling id reference; a source cell pointing off an official host; a
  broken internal link or anchor; a non-`https` or non-official external link; a table row
  with no source cell; a rendered anchor still carrying the placeholder Associates tag; a
  missing disclosure string; a page with no language, viewport, description or exactly one
  `<h1>`; a skipped heading level; an `<img>` without alt text; an anchor with no label; a
  table with no header row; or an `aria-*` reference with no target.

  Current result: **13 HTML files, 497 table rows, 635 external links, 3 datasets — all
  checks passed.**
- **Every route** returns HTTP 200 from a local server, and the site was published and
  re-fetched from its live URL after the merge.

---

## 7. Disclosure

Some links on this site are Amazon links and may earn the site owner a commission.
**As an Amazon Associate I earn from qualifying purchases.**

Amazon and the Amazon logo are trademarks of Amazon.com, Inc. or its affiliates. This site
is not affiliated with, endorsed by, or sponsored by Amazon.com, Inc. Prices, ratings,
review counts, demand badges and Best Sellers Ranks are point-in-time readings of official
Amazon pages taken on 2026-11-13 and are reproduced for research purposes; they change
without notice.
