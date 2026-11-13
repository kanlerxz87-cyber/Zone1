# Zone1 — Amazon Affiliate Marketing Platform

An AI-assisted affiliate research and publishing platform for three Amazon.com air-fryer
products, delivered as a static site published with GitHub Pages.

**Live site:** <https://kanlerxz87-cyber.github.io/Zone1/>

---

## What this is

The brief was to build an affiliate marketing platform that automates product research,
identifies trending and high-converting products, analyses pricing, reviews, competition and
commission potential, generates SEO-optimised content, publishes and manages affiliate links,
tracks clicks and conversions, and continuously optimises campaigns — with compliance with
Amazon Associates policies and FTC disclosure requirements built in.

What exists in this repository:

| Deliverable | Where |
| --- | --- |
| Verified product research dataset | `data/products.json` |
| Amazon Associates + FTC compliance map | `data/program.json` |
| Irregularity register | `data/flags.json` |
| Static site (13 pages) | `index.html`, `pages/**` |
| Site generator | `tools/build_site.py` |
| Link / disclosure / source checker | `tools/check_links.py` |
| Parallel-session task board | `COORDINATION.md` |

## The three products

The brief supplied three `link.amazon` short URLs. Each was resolved over HTTP to its
canonical `amazon.com/dp/<ASIN>` destination and the identity confirmed from the destination
page title.

| # | Supplied URL | Resolved ASIN | Product | Verified price | Rating | Ratings |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | `link.amazon/B04G1MEwY` | `B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven | $79.93 | 4.2 | 4,859 |
| P2 | `link.amazon/B02NbDxp3` | `B09B7SB46R` | Emeril Lagasse 26QT French Door Air Fryer Toaster Oven | $149.99 | 4.3 | 18.3K |
| P3 | `link.amazon/B00hJ57DV` | `B08DKYBTPH` | Chefman Air Fryer 8 Qt TurboFry 4-in-1 | $79.91 | 4.4 | 16,861 |

> The path segment in each supplied URL is an **opaque redirect token, not the ASIN**. Rebuilding
> links from the segment would point at the wrong product. See flag **F-01**.

## Verification standard

Every value in every table was read directly from an official first-party source
(`amazon.com`, `affiliate-program.amazon.com`, `ftc.gov`, `ecfr.gov`) and carries a link to it.
**Where an official source did not serve a readable value, the field is left blank and flagged
as unverified. Nothing is inferred, estimated or filled in from memory.**

This is enforced mechanically. `tools/check_links.py` fails the build if:

1. any internal link or `#anchor` does not resolve;
2. any table row carrying a finding does not carry an official source link;
3. a rendered anchor still contains the placeholder Associates tag;
4. either required disclosure string is missing from a page;
5. any external link is not `https://` or points at a non-official host.

## Two open compliance gates

These are published for review rather than silently resolved — see the
**Flagged for Review** page.

* **F-07 — price display.** Amazon's Program Policies allow a Site to show prices only where
  Amazon serves them with the link, or where the data comes from Creators API / PA API. This is
  a static build with dated research snapshots, so it is neither. Compliant routes: swap the
  price column for SiteStripe / PA API, or drop prices from published pages.
* **F-08 — star ratings.** Participation Requirements 5(t) forbids displaying Amazon customer
  reviews or star ratings unless obtained through Creators API / PA API.

Also relevant: **F-10** — Amazon's `robots.txt` disallows a long list of AI and research agents
outright, and the Program Content licence prohibits using Program Content to develop or improve
language or machine-learning models. The automation design therefore routes product data through
the official APIs rather than scraping.

## Running the build

```bash
python3 tools/build_site.py     # regenerate every page from data/
python3 tools/check_links.py    # integrity, source-link and disclosure checks
```

No dependencies. The output is plain static HTML, CSS and JavaScript committed to the
repository root, which is what the existing GitHub Pages legacy build publishes.

## Site map

```
index.html                                   Dashboard
pages/executive-summary.html                 Executive summary
pages/catalog.html                           All products — full verified record
pages/category/dual-basket-air-fryers.html   Category: dual-basket air fryers
pages/category/multi-function-air-fryer-ovens.html  Category: air fryer ovens
pages/research.html                          Pricing, reviews, competition, commission model
pages/marketing/seo-article.html             SEO article
pages/marketing/comparison.html              Head-to-head comparison
pages/marketing/buying-guide.html            Buying guide
pages/campaign.html                          Link management, tracking, automation, optimisation
pages/compliance.html                        Amazon Associates + FTC compliance map
pages/sources.html                           Sources & verification audit trail
pages/flagged.html                           Flagged for Review
```

## Working on this repo in parallel

Read `COORDINATION.md` before starting. It is the shared task board: claim a task by writing
your session ID and file scope there, commit and push the claim immediately, keep file scopes
non-overlapping, and make small frequent commits. Shared outputs (the datasets, the site index
and navigation) are changed only by the final integration session.

## Disclosure

> As an Amazon Associate I earn from qualifying purchases.

We are a participant in the Amazon Services LLC Associates Programme, an affiliate advertising
programme designed to provide a means for sites to earn advertising fees by advertising Amazon
products. In our content we earn money from qualifying purchases made through our links, at no
extra cost to you. The price you pay is unchanged.

Not affiliated with, endorsed by, or sponsored by Amazon.com, Inc., Chefman or Emeril Lagasse.
