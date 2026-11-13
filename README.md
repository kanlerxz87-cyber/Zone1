# Zone1 — Amazon affiliate research dashboard

A source-verified research site for three supplied Amazon affiliate links. Every product
value is quoted from the manufacturer's official product page and carries a link to it.
Anything that could not be confirmed from an official source is **left blank and flagged**,
not filled in.

**Live site:** https://kanlerxz87-cyber.github.io/Zone1/

## What is here

| Path | What it is |
|---|---|
| `*.html`, `articles/`, `categories/`, `assets/` | The published site (GitHub Pages serves `main` → `/`) |
| `data/products.json` | The three products, every field as `{value, source, verified}` |
| `data/sources.json` | The source register — 24 official URLs and what each supports |
| `data/compliance.json` | 23 Amazon/FTC requirements, each with a verbatim quote and a link |
| `data/analysis.json` | Niche scoring, content plan, automation pipeline (labelled as derived) |
| `data/irregularities.json` | 17 flagged items, including the monetisation blocker |
| `scripts/build.py` | Static generator — renders the HTML from `data/` |
| `scripts/check.py` | Verification gate — fails on broken links, unsourced rows, missing disclosures |
| `COORDINATION.md` | Shared task board for parallel agent sessions |

## Build

```bash
./build.sh            # build + verify
python3 scripts/build.py
python3 scripts/check.py
```

The check fails the build if a row renders without a source link and without an explicit
"unverified" marker, if any internal link is broken, if any page is missing the required
Amazon disclosure or trademark attribution, or if the headline field counts stop matching
the rendered rows.

## The three supplied links

| # | Supplied link | Resolves to | Product |
|---|---|---|---|
| 1 | https://link.amazon/B04G1MEwY | ASIN B0CDY277D3 | Chefman TurboFry 6 Qt Dual-Basket Air Fryer (RJ38-3DBW-V2) |
| 2 | https://link.amazon/B02NbDxp3 | ASIN B09B7SB46R | Emeril Lagasse 26 Qt French Door AirFryer 360 (4-00675-02A-VN) |
| 3 | https://link.amazon/B00hJ57DV | ASIN B08DKYBTPH | Chefman TurboFry 8 Qt Air Fryer w/ High Fry (RJ38-8T-BLACK) |

> **Action required:** as supplied, none of the three resolves with an Amazon Associates
> `tag=` parameter, so none can be verified as a commission-earning Special Link. See
> `data/irregularities.json` item **I-2** and the site's Flagged for Review page.

## Honesty rules this repo follows

1. No Amazon price, star rating, review count or Best Sellers Rank is published unless it
   was captured from an official Amazon surface. All of them were blocked, so all are blank.
2. No category commission rate is published — the rate card is behind Amazon sign-in.
3. No search-volume, trend or revenue figure is asserted anywhere.
4. No hands-on testing is claimed. Articles are spec-based desk research and say so.
5. Analysis and scoring are labelled `derived`, never presented as fact.

## Licence / attribution

Amazon and the Amazon logo are trademarks of Amazon.com, Inc. or its affiliates.
This is an independent research site; it is not endorsed by or affiliated with Amazon,
Chefman or Emeril Everyday. Product names and model numbers are used for identification.
