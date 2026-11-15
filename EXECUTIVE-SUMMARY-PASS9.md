# Executive summary — pass 9 (session `22f43836`, 2026-11-15)

This is the decision-ready briefing for the work done in this session. It states only what
was checked, and it names the constraint that limits what "checked" means here.

## The one-paragraph version

The site is live, its build and verification gates pass, and its product data was already
sound. This pass re-read the three supplied Amazon short links and Amazon's commission table
against the official pages and found no published value wrong. It found and fixed two defects
that were costing the site real money and real search visibility: not one of the 27 generated
pages declared a canonical URL or carried sharing or structured data, and 11 clickable
affiliate links were not marked `rel="sponsored"`. Both are now fixed in the generator, both
are enforced by new build guards that fail the build if either returns, and the search-engine
requirements behind them are quoted from Google's own published policy. The largest issue is
not technical and is not fixed, because it is not mine to fix: **nine near-identical copies of
this site are published from one repository**, and the decision about what to do with the eight
superseded ones is queued for the owner as **SG-17**.

## What was verified in this pass, against official sources

| # | Claim checked | Result | Official source |
|---|---|---|---|
| 1 | `link.amazon/B04G1MEwY` resolves to ASIN `B0CDY277D3`, title "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows…" | **confirmed**, identical to the recorded value | [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY) |
| 2 | `link.amazon/B02NbDxp3` resolves to ASIN `B09B7SB46R`, title "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven…" | **confirmed**, identical | [link.amazon/B02NbDxp3](https://link.amazon/B02NbDxp3) |
| 3 | `link.amazon/B00hJ57DV` resolves to ASIN `B08DKYBTPH`, title "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry…" | **confirmed**, identical | [link.amazon/B00hJ57DV](https://link.amazon/B00hJ57DV) |
| 4 | Commission Table 1: "Physical Books, Kitchen, Automotive \| 4.50%" and "All Other Categories \| 4.00%" | **confirmed verbatim**, all 11 rows match `data/commission-rates.csv` | [Standard Commission Income Statement](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| 5 | Program Policies §3(e) requires an accurate cookie/pixel disclosure; "Updated: April 14, 2026" | **confirmed verbatim** | [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) |
| 6 | Google states affiliate links are permitted "as long as they are qualified with a `rel="nofollow"` or `rel="sponsored"` attribute" | **confirmed verbatim** | [Google spam policies](https://developers.google.com/search/docs/essentials/spam-policies) |
| 7 | Google: mark paid links with `rel="sponsored"` | **confirmed verbatim** | [Qualify outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) |
| 8 | The site's own flag register: 45 rows, 45 distinct IDs, no duplicates | **confirmed by parsing the rendered page** | [flagged.html](https://kanlerxz87-cyber.github.io/Zone1/flagged.html) |

Still unconfirmed, and still not guessed: which manufacturer model each ASIN ships
(flag F1 and SG-01), and which Associates tag rides inside each short link (F6). Both need
someone logged into the owner's Amazon accounts. They are published as questions, not filled in.

## What was fixed

| Defect | Measured before | Fixed by | Guarded by |
|---|---|---|---|
| No canonical URL, Open Graph, Twitter card or structured data on any generated page | **0 of 27** pages | `layout()` in `build.py` | `check_seo_metadata()` |
| Clickable affiliate links without `rel="sponsored"` | **11** instances on 5 pages (raw supplied links in evidence tables) | `qualify_affiliate_links()` post-render pass | `check_affiliate_link_qualification()` — it failed the build on those 11 first |
| Stale "8 parallel builds" navigation string (counted the site's own article hub; the catalogue lists 7) | 1 string on every page | count derived from the catalogue | — |

Deliberately **not** added: schema.org `Product`/`Offer`/`AggregateRating`. The site publishes
no Amazon price or star rating, by policy (§2(b), §6(t)). Product markup would either be empty
or would assert a number this project has spent nine passes refusing to publish.

## Decisions waiting on you, in priority order

1. **SG-17 — what happens to the eight superseded published builds.** The owner's call, with
   three costed options. This is the biggest lever on organic traffic and on price-display
   compliance. Recommended: option B (noindex the annex builds, keep the evidence citable).
2. **SG-01 — read the model number off each of the three live listings.** Five minutes, and it
   closes four flags at once. This pass could not do it: Amazon serves its product-information
   block through client-side markup, and the fetched pages do not contain it.
3. **F6 — confirm the Associates tag** inside each short link, from Associates Central.

## The constraint behind "verified"

Direct outbound HTTP from this session's shell is restricted to GitHub, npm and PyPI hosts;
`amazon.com`, `chefman.com`, `ftc.gov` and `ecfr.gov` are all unreachable that way. The
page-fetch tool does reach them, so every re-read above was done through it. Anything that
could not be re-read is recorded as not re-checked, never as confirmed. This is written down
because a future session should know that "curl says 000" here is a sandbox artefact, not a
dead source.
