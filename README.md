# Zone1 — Amazon affiliate research & publishing platform

A source-linked research record and a publishable affiliate marketing site for three
Amazon.com air-fryer products. **Every value in every table was read from an official
first-party source and carries a link to it. Anything that could not be confirmed is left
blank and flagged — never inferred.**

Live site: **https://kanlerxz87-cyber.github.io/Zone1/**

---

## What is in the box

| Deliverable | Where |
|---|---|
| Executive summary (on site, one page) | [`pages/executive-summary.html`](pages/executive-summary.html) |
| Executive summary (document) | [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md) |
| Landing dashboard | [`index.html`](index.html) |
| Category subpages | [`pages/category/`](pages/category/) |
| Full verified catalogue | [`pages/catalog.html`](pages/catalog.html) |
| Research & analysis (pricing, reviews, competition, commission model, demand) | [`pages/research.html`](pages/research.html) |
| SEO content | [`pages/marketing/seo-article.html`](pages/marketing/seo-article.html) |
| Head-to-head comparison | [`pages/marketing/comparison.html`](pages/marketing/comparison.html) |
| Buying guide | [`pages/marketing/buying-guide.html`](pages/marketing/buying-guide.html) |
| Campaign, link management & tracking plan | [`pages/campaign.html`](pages/campaign.html) |
| Compliance register | [`pages/compliance.html`](pages/compliance.html) |
| Source register & verification trail | [`pages/sources.html`](pages/sources.html) |
| **Flagged for Review** (unconfirmed values & irregularities) | [`pages/flagged.html`](pages/flagged.html) |
| Line-by-line repo review | [`REVIEW.md`](REVIEW.md) |
| Shared task board & change log | [`COORDINATION.md`](COORDINATION.md) |
| First build iteration (document) | [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md) |

Thirteen pages in total, all static HTML with no runtime dependency and no build step on
the server.

---

## The three products

The three supplied `link.amazon` URLs are opaque redirect tokens, not product identifiers.
Each was followed to its canonical `amazon.com/dp/<ASIN>` destination and the product
confirmed from the destination page.

| Supplied link | Resolved ASIN | Product | Rating / ratings | Demand | Verified price snapshot |
|---|---|---|---|---|---|
| [`link.amazon/B04G1MEwY`](https://link.amazon/B04G1MEwY) | `B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven | 4.2 / 4,859 | 1K+ bought in past month | New **$79.93** against a $99.99 list price; a separate **$57.45** offer is tagged `USED` by Amazon |
| [`link.amazon/B02NbDxp3`](https://link.amazon/B02NbDxp3) | `B09B7SB46R` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | 4.3 / 18.3K | 4K+ bought in past month | Deal **$149.99** against a $209.99 list price; an alternate offer at $92.99 |
| [`link.amazon/B00hJ57DV`](https://link.amazon/B00hJ57DV) | `B08DKYBTPH` | Chefman Air Fryer 8 Qt TurboFry 4-in-1 | 4.4 / 16,861 | 3K+ bought in past month | New **$79.91** against a $119.99 list price; used $51.94 |

Product 2's detail page serves a reduced body, so its values are read from Amazon's own
search result for its ASIN and every row carries that URL. The full per-attribute record,
including the attributes that are blank, is on the catalogue and research pages.

---

## Verification rules — the standard this project holds itself to

1. **Official source or nothing.** A value is published only if it was read from an
   Amazon product or search page, an Amazon Associates policy page, the FTC, the eCFR, or
   the GitHub API. Every table row carries a link to the page it came from.
2. **Blank means blank.** Where an official source did not serve a readable value the
   field is empty and carries an "unverified" marker plus the flag that explains what was
   tried. Nothing is inferred from a sibling product, from the title, from a third-party
   site, or from memory.
3. **Official source, editorial analysis and unverified are three different things**, and
   the site labels which is which on every table.
4. **Snapshot, not live.** Prices, discount badges, "bought in past month" counts, Best
   Sellers Rank and review counts are point-in-time values captured on **2026-11-13**. They
   change. The campaign page carries the re-verification schedule.
5. **A flag is published, not hidden.** Open questions go on the
   [Flagged for Review](pages/flagged.html) page with their source and the action taken.
   They do not block the site going live, but they are visible.

---

## Compliance position

Quoted from [the Associates Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement)
and [the Program Policies](https://affiliate-program.amazon.com/help/operating/policies),
and from the [FTC's disclosure guidance](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers)
and the [Endorsement Guides FAQ](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking):

- The statement **"As an Amazon Associate I earn from qualifying purchases."** appears in
  the footer of every page, with the FTC wording *"qualifying purchases made through our
  links"* beside every monetised block.
- Disclosures sit **above** the recommendation and next to the link, not only at the end of
  a page and not only in the footer.
- Every outbound link is a **direct Special Link** to the product detail page carrying the
  publisher's `tag`. No supplied `link.amazon` short link is reused as an outbound link —
  a redirect hop would obscure the destination from the reader, breach the rule against
  link shortening, and disqualify the purchase.
- No commission rate is stated anywhere. The official rate card is behind a sign-in wall,
  so the commission **model** on the research page is built from the publisher's own rate
  once it is known, and the rate itself is left blank.
- No product claim is made that was not read from the manufacturer or from Amazon.
- Amazon's `robots.txt` disallows a long list of AI and research agents, and the Program
  licence prohibits data-mining and model-training on Program Content, so **no automated
  Amazon scraping is part of this build**.

Two gates remain open before the site takes live traffic, and both are on the compliance
page with the exact wording: static price display (F-07) and static star-rating and review
display (F-08).

---

## Repository layout

| Path | Purpose |
|---|---|
| `index.html` | Landing dashboard — the Pages entry point |
| `pages/**` | The other twelve pages |
| `assets/css/site.css` | The complete visual system — responsive, dependency-free |
| `assets/js/site.js` | Navigation, copy-link, table filters, active-link behaviour |
| `data/products.json` | Product records. Every field carries `status` and `source`. Unverified fields are `null`. |
| `data/program.json` | 30 Associates/FTC program clauses, 10 automation rules, and the official source register |
| `data/flags.json` | The irregularity register (F-01 – F-24) |
| `tools/build_site.py` | The generator. Reads the three datasets and writes all thirteen pages. |
| `tools/check_links.py` | The integrity checker — datasets, links, anchors, sources, disclosures, accessibility, responsive |
| `scripts/build.mjs` | The first build iteration's generator. Still reproducible; see below. |
| `data/session-d14c5409/` | The first iteration's datasets, preserved verbatim |
| `legacy/` | The first iteration's root redirect, preserved for provenance |
| `COORDINATION.md` | The shared task board: claims, verification, conflict log, change log |
| `REVIEW.md` | The line-by-line repository review |
| `EXECUTIVE_SUMMARY.md` | The executive summary document |

### Two build iterations, one published site

This repository was worked on by two sessions. The first (`d14c5409`) produced a seven-page
site with a smaller verified dataset; the second (`zone1-main`) re-retrieved the Amazon
pages, recovered the price, rating, review-count, demand and rank values that the first
pass could not read, and produced the thirteen-page site published at the repository root.

**Only the thirteen-page root site is published.** The first iteration is preserved as
source — `scripts/build.mjs` plus `data/session-d14c5409/` — and rebuilds byte for byte
with one command:

```bash
node scripts/build.mjs       # writes docs/ — gitignored, not published
```

Its datasets are kept unchanged so that its site stays reproducible and auditable. Every
finding it raised is carried forward into the live `data/flags.json`, and the `legacy_ids`
field on each flag records the id it had in the earlier register.

---

## Build and check

```bash
python3 tools/build_site.py     # regenerate the thirteen pages from the datasets
python3 tools/check_links.py    # verify the result
```

No dependencies. Python 3.9+ and Node 18+ only.

`tools/build_site.py` writes `index.html`, `pages/**` and `assets/**`. `tools/check_links.py`
runs offline and fails on any of the following:

- a dataset that does not parse or is missing a key its schema requires;
- a field marked `verified` with no source, a non-official source, or a blank value;
- a field marked `unverified` that carries a value;
- a flag, program term or product that references an id that does not exist;
- a source cell that links to a host that is not an official source;
- an internal link that does not resolve, or an anchor that has no matching id;
- an external link that is not `https://` or points at a non-official host;
- a table row with no source cell;
- a rendered anchor still carrying the placeholder Associates tag;
- a missing Amazon or FTC disclosure string;
- a page with no language, no viewport, no description, or more than one `<h1>`;
- a heading level that skips a level, an `<img>` without alt text, an anchor with no
  discernible label, a table with no header row, or an `aria-*` reference with no target.

Current result:

```
Checked 13 HTML files, 497 table rows, 635 external links, 3 datasets.
All checks passed.
```

`node scripts/build.mjs --check` validates the archived first-iteration datasets without
writing anything.

---

## Before publishing with real traffic

1. Replace the `YOUR-TAG-XX` placeholder in `tools/build_site.py` with the publisher's
   Associates ID and rebuild.
2. Confirm the Associates account is approved, then make the required statement active
   (flag F-19).
3. Choose a compliant route for price and star-rating display (flags F-07 and F-08) —
   SiteStripe/PA API, or remove those columns from the published pages.
4. Confirm the non-US publisher clause and the delivery destination (flag F-14).
5. Re-verify the price, rating, badge and rank snapshot (flag F-02, F-05).

---

## Disclosure

Some links on this site are Amazon links and may earn the site owner a commission.
**As an Amazon Associate I earn from qualifying purchases.**

Amazon and the Amazon logo are trademarks of Amazon.com, Inc. or its affiliates. This site
is not affiliated with, endorsed by, or sponsored by Amazon.com, Inc. Prices, ratings,
review counts, demand badges and Best Sellers Ranks are point-in-time readings of official
Amazon pages taken on 2026-11-13 and are reproduced for research purposes; they change
without notice.
