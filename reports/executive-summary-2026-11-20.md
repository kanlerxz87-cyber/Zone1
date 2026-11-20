# Executive summary — 20 November 2026

**Publication:** Zone1 Kitchen — https://kanlerxz87-cyber.github.io/Zone1/
**This pass:** `arena/761c3c2e-zone1` · base `1c7de82` · full verification + reader-path repair
**Owner action needed to unlock revenue:** two items, both listed in §4. Everything else is built.

---

## 1. The honest one-paragraph version

The site is live, source-disciplined and structurally sound: 64 pages, 24 buying guides in four
intent clusters, five product pages covering all five supplied links, every figure carrying a
link to the official document it came from, an affiliate disclosure under the masthead on every
page, and `rel="sponsored"` on every outbound Amazon link. What it does **not** have is a
validated affiliate link: the five `link.amazon/…` strings reach Amazon product pages, but
nobody has confirmed in Associates Central that those are the listings you intend to promote,
`shopnow047c-20` has never been validated, and the operational tag is deliberately blank. Until
those two account-only facts are recorded, the site can inform readers but cannot be said to
earn anything. That is a deliberately honest position, not an incomplete build.

## 2. What changed in this pass (all verified, nothing inferred)

| # | Change | Why it mattered |
|---|---|---|
| 1 | Reading badges are now computed per guide instead of a hard-coded "3 min read" | Every one of 26 guides printed the identical badge regardless of length. It was the only number on the page a reader could check in ten seconds, and it was wrong. |
| 2 | Every guide now ends with links to the model pages it discusses | A count over the generated files found **zero** product or Amazon links across all 27 reader articles. The guides described products a reader could not click through to. |
| 3 | New indexable page: **How this site is researched** (`how-we-research.html`) | The method, the dated source reads and the corrections were previously a sentence on the about page. Authorship is now a dated, citable page — which is also what E-E-A-T guidance rewards. |
| 4 | Metadata type raised from 9–11 px to 12 px | Byline, source dates and footer index were at the readability floor. |
| 5 | Two new flags published (**F107**, **F108**) and one new console gate | F107 records that the two thermometer links now serve a different colour variant / sale parameter than yesterday's record. |

**Measured, not asserted:** contrast was tested on 18 colour pairs — all passed (lowest 5.35:1).
No colour was changed, because changing it and calling it an accessibility fix would have been
false.

## 3. What the five products actually are (observed, not confirmed)

| Link | Observed destination | Product | Status of intent |
|---|---|---|---|
| `link.amazon/B04G1MEwY` | `/dp/B0CDY277D3` | Chefman 6 Qt Dual Basket / Dual-Window | **Unconfirmed** |
| `link.amazon/B02NbDxp3` | `/dp/B09B7SB46R` | Emeril Lagasse 26 QT French Door | **Unconfirmed** |
| `link.amazon/B00hJ57DV` | `/dp/B08DKYBTPH` | Chefman 8 Qt TurboFry | **Unconfirmed** |
| `link.amazon/B0c8moW59` | `/dp/B0DHZTCNR5` | ThermoMaven instant-read thermometer | **Unconfirmed** |
| `link.amazon/B0f3GKalj` | `/dp/B0DZFD6R9Z` | CHEF iQ Sense Gen3 wireless thermometer | **Unconfirmed** |

All five were re-read live today. All five reached a product page. **A resolved destination is
not a confirmation of intent** — that is why the intended-ASIN fields remain blank and why the
two fields are kept apart in `data/product-intent.json`.

## 4. The two decisions only you can make

**D1 · Confirm the five intended listings (about ten minutes, no engineering).**
For each product, state: "the listing I intend is ASIN X". That single answer converts five
product records from *observed* to *confirmed* and removes the largest caveat from every buyer
page. Nothing needs rewriting — the fields already exist.

**D2 · Validate `shopnow047c-20` and run one enrolled link test.**
In Associates Central → Manage your Tracking ID, confirm the ID exists on the account. Then take
**one** product, build its Special Link through the enrolled workflow, and confirm a click lands
in the Tracking ID Summary Report. Only then apply the tag site-wide. Doing it product-by-product
is what the brief asks for, and it is also the fastest way to discover a broken link before it
costs you a season.

## 5. What is built but switched off, and why

| Capability | State | Why it is off |
|---|---|---|
| Analytics (5 events, browser client + Python collector) | Built, contract-tested, **disabled** | GitHub Pages cannot run the collector; a same-origin runtime, log minimisation and a privacy decision are required first. No events are being recorded today. |
| Campaign ledger | Empty by design | It accepts only dated first-party reports. Inventing rows would destroy the only trustworthy measurement in the project. |
| Search Console | Token field blank | Needs a real property verification; no ownership is claimed. |
| Email capture | Not built | There is no list service and no consent mechanism, so the site offers RSS only. Offering a fake signup would be worse than none. |
| Amazon price / rating display | Not built | Requires an authorised API route; scraped values would breach the Program Policies. |
| Product photography | Not used | No licensed imagery; the AI editorial scene is labelled as such. |

## 6. What the brief asked for that this project does not do — and should not pretend to

The brief asks for an engine that "identifies trending and high-converting products, analyses
competition and commission potential, and continuously optimises campaigns to maximise
revenue". **No such analysis is published, because none of its inputs exist here:** there is no
keyword dataset, no click or order data, no ranking feed and no conversion signal. Publishing a
"conversion score" from those absences would be fabrication, and it is also the fastest route to
an Associates policy problem. What exists instead is the *machinery* for that analysis —
event definitions, an empty ledger with a provenance schema, a collector, and a review queue —
so the first real report can be dropped in without redesigning anything.

## 7. Where the money actually is, ranked by effort

1. **D1 + D2 above** — without them, no click is attributable. Highest value, lowest effort.
2. **Lengthen the guides.** They are 162–382 words of prose. They are accurate but short, and
   short pages rarely earn a commercial query. This is an editorial decision (ET-4), not a bug;
   the site now publishes the true length rather than a badge that hid it.
3. **Search Console + sitemap submission** — then choose the next topic from query data
   instead of instinct. The sitemap and RSS feed already work; nothing is submitted yet.
4. **Analytics deployment** — only worth doing once there is traffic to measure.
5. **Photography / imagery licensing** — the largest remaining visual gap, and the one that most
   affects whether the site reads as a publication rather than a document.

## 8. Review trail

* Full verification record: [`reports/verification-2026-11-20-761c3c2e.md`](verification-2026-11-20-761c3c2e.md)
* Open items for your review: https://kanlerxz87-cyber.github.io/Zone1/flagged.html (F107, F108 new)
* Machine-readable source reads: `data/sources.json → reverified_2026_11_20_761c3c2e`
* Editorial policy behind every change: https://kanlerxz87-cyber.github.io/Zone1/how-we-research.html

**Nothing in this summary is a forecast, a price, a ranking or a conversion figure. No hands-on
testing is claimed. No short link has been declared valid or invalid.**
