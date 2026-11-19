# Canonical publication assets and editorial contract

The canonical reader site is the root `build.py` output, not one of the historical
parallel generators. The generator reads `publication/layout.html.tpl`,
`publication/theme.css`, `publication/site.js` and `data/publication.json`.
Generated `assets/style.css` and `assets/app.js` must be byte-identical to their
reviewed sources. No build-time network, font CDN, third-party script or framework
is required.

## Imagery

- `assets/images/kitchen-editorial.jpg` was AI-generated for this publication on
  2026-11-19. The brief was a warm sage/oak kitchen, a bowl of vegetables and a
  deliberately unbranded, out-of-focus background appliance. It is a conceptual
  editorial scene, not a real location, product photograph, test, endorsement,
  cooking result or evidence of ownership. The front-page caption says so.
- The two WebP files are resized derivatives of that scene: 540×362 and 900×604.
  The responsive image has an empty alt because it is decorative; the provenance
  caption remains visible. It is not used as a specific product's photograph.
- The three inline SVG format diagrams are original drawings, not exact brand
  renderings. Each is labelled “Format illustration · not to scale.”
- `assets/og-card.png` is an editorial sharing card for the publication. It carries
  the brand and a decorative scene, not an offer or a tested-performance claim.
- No Amazon/manufacturer product photography was copied. Actual product imagery
  remains gated on original photography, documented permission or a compliant
  authorised Program Content integration. Do not claim that generated imagery
  proves product identity or confers third-party intellectual-property rights.

## Fonts

DM Sans and DM Serif Display are self-hosted Latin WOFF2 subsets distributed by
`@fontsource/dm-sans@5.3.0` and `@fontsource/dm-serif-display@5.3.0`. Their SIL Open
Font License texts are included in `assets/fonts/*-LICENSE.txt`.
Package provenance: [DM Sans package](https://registry.npmjs.org/@fontsource/dm-sans/5.3.0),
[DM Serif Display package](https://registry.npmjs.org/@fontsource/dm-serif-display/5.3.0).
Only the needed styles/weights ship. Small navigation arrows are original inline
SVGs rather than depending on a reader having a symbol font installed.

## Reader experience

One masthead, a disclosure strip immediately below it, four reader navigation
links and one native Workspace menu. The menu works without JavaScript; Escape
and outside-click closing are progressive enhancements. Owner/evidence pages
are reachable from that group and footer but excluded from the canonical reader
sitemap with `noindex,follow`. Historical builds are catalogued, not presented as
additional active publications; their original source generators are preserved.

Product pages lead with use case, a documented capacity and the most consequential
caveat. Every numeric table row still has primary/repository evidence. No Amazon
price/rating, hands-on claim, fabricated author or performance ranking is added.
Thermometer pages are explicitly **submitted-link notes**, not a new confirmed
product dataset. Intended ASINs, listing confirmations and enrolled tests remain
blank until actually established.

The byline is the publication, with AI-assisted document research stated openly.
A named human editor is not invented. The November selection is seasonal editorial
judgement, not proof of search demand or discounts. RSS is a working reader loop;
there is no pretend email form. The cadence in `data/publication.json` is an
operating plan, not a deployed scheduler.

## Dates and verification

Source-access dates and content modification dates are separate. Six revised
articles explicitly record `modified_on` and scoped `sources_read` dates. The
sitemap uses per-article dates; other redesigned reader routes use the publication
modification date. Legacy source-access dates are not invented into publication
dates. RSS omits an item `pubDate` when no actual `published_at_utc` has been
recorded; channel freshness uses the fixed, real editorial-update timestamp in
`data/publication.json`. Adding a future guide must update the article/topic and
cluster registers and pass the build, which regenerates sitemap and feed.

Run `python3 build.py`, `python3 verify.py`, root and platform unit tests, the annex
reproducibility/link gates and the browser checks described in the dated review
report before publication. The measurements in browser tests are synthetic test
fixtures, not campaign traffic. See `analytics/README.md` for the separate
production deployment and privacy gates.
