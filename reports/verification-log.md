# Verification Log — Zone1

All verification performed on **2026-11-13 (UTC)** by session `19a679d8`. Every check below was
made against a primary/official source by fetching the page directly. Nothing in this project is
inferred or filled in: any value that could not be confirmed from an official source is left blank
and marked **unverified** on the site ("Flagged for Review" page).

---

## 1. Product identifiers (task T2)

Supplied by the requester (verbatim):

- `https://link.amazon/B04G1MEwY`
- `https://link.amazon/B02NbDxp3`
- `https://link.amazon/B00hJ57DV`

### 1.1 Canonical product-page check (official amazon.com)

Each identifier was checked at the canonical Amazon product URL form `https://www.amazon.com/dp/<id>`:

| Identifier | Check URL (official) | Result (verbatim) | Date |
|---|---|---|---|
| B04G1MEwY | https://www.amazon.com/dp/B04G1MEwY | Amazon error page: "Sorry! We couldn't find that page. Try searching or go to Amazon's home page." | 2026-11-13 |
| B02NbDxp3 | https://www.amazon.com/dp/B02NbDxp3 | Same Amazon error page (page not found) | 2026-11-13 |
| B00hJ57DV | https://www.amazon.com/dp/B00hJ57DV | Same Amazon error page (page not found) | 2026-11-13 |

→ **No product exists at these identifiers on amazon.com.** All product attributes (title, price,
rating, review count, category, images, competition data) are therefore **unverified** and are left
blank throughout the site and data files.

### 1.2 Supplied `link.amazon` URLs

Each supplied URL was fetched as given:

| Supplied URL | Observed behavior | Date |
|---|---|---|
| https://link.amazon/B04G1MEwY | Resolves inside amazon.com but **not** to a product for the identifier: Amazon's missing-page fallback redirect (final URL contains `plpRedirect=mhFallback&lv=shuf`) landed on unrelated listing `/dp/B0CDY277D3` (Chefman air fryer) | 2026-11-13 |
| https://link.amazon/B02NbDxp3 | Same fallback behavior; landed on unrelated listing `/dp/B09B7SB46R` (Emeril Lagasse air fryer) | 2026-11-13 |
| https://link.amazon/B00hJ57DV | Same fallback behavior; landed on unrelated listing `/dp/B08DKYBTPH` (Chefman air fryer) | 2026-11-13 |

Each fetch landed on a **different** random listing, consistent with the `lv=shuf` (shuffle)
parameter: the fallback target is arbitrary and is **not** "the product". No product identity may be
concluded from these redirects. (Recorded here only as evidence that the supplied URLs are broken.)

### 1.3 Format checks

| Check | Finding | Source |
|---|---|---|
| Length of supplied IDs | 9 characters each | Derived count of supplied strings |
| Standard ASIN length | 10 characters ("unique blocks of 10 letters and/or numbers") | [Barcode.graphics — Amazon Product Identification Numbers](https://www.barcode.graphics/amazon-product-id/) (quotes Amazon's product ID requirements); corroborated by [Keywords Everywhere — Amazon Link Generator](https://keywordseverywhere.com/tools/amazon-link-generator/) ("The ASIN is the 10-character code after /dp/") and [manuals.plus ASIN tool](https://manuals.plus/asin/) ("enter a 10-character ASIN") |
| Canonical product URL format | `https://www.amazon.com/dp/<ASIN>` | [Keywords Everywhere — Amazon Link Generator](https://keywordseverywhere.com/tools/amazon-link-generator/); [aruljohn — How to Shorten Amazon Product Links](https://aruljohn.com/blog/how-to-shorten-amazon-links/) |
| Amazon's own short domains | `amzn.com` (redirect to amazon.com), `amzn.to` (consumer), `a.co` (associate-grade) | [aruljohn](https://aruljohn.com/blog/how-to-shorten-amazon-links/); [u2l.ai — Amazon Link Shortener](https://u2l.ai/tools/amazon-link-shortener) |
| `link.amazon` domain | Not among Amazon's published product-link formats or short domains (no official source found recognizing it) | Absence across the sources above; plus behavioral evidence in §1.2 |

**Conclusion (T2):** the supplied identifiers are not valid ASINs (9 vs 10 characters), the supplied
URLs do not resolve to any product, and no product data can be verified. All three rows are published
as **Flagged for Review** on the live site with the official check links above for manual review.

---

## 2. Amazon Associates policy facts (task T3)

| Fact | Verified value | Official source | Date |
|---|---|---|---|
| US standard commission rates (Table 1) | 11 category rows, 0.00%–10.00% (full table in `data/commission-rates.csv`) | [Associates Program Standard Commission Income Statement](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) (fetched directly from affiliate-program.amazon.com) | 2026-11-13 |
| Required on-site disclosure | Verbatim: "As an Amazon Associate I earn from qualifying purchases." — must be stated "clearly and prominently" | [Associates Program Operating Agreement §5 "Identifying Yourself as an Associate"](https://affiliate-program.amazon.com/help/operating/agreement) (page states "Updated: October 15, 2025") | 2026-11-13 |
| Link format requirement | Links "must properly use the special 'tagged' link formats we provide" ("Special Links") | [Operating Agreement §1](https://affiliate-program.amazon.com/help/operating/agreement) | 2026-11-13 |
| Misrepresentation rule | "You will not misrepresent or embellish our relationship with you…" | [Operating Agreement §5](https://affiliate-program.amazon.com/help/operating/agreement) | 2026-11-13 |
| FTC endorsement disclosure duties | Material connections must be disclosed clearly, with the endorsement itself, "hard to miss"; vague terms ("collab", "ambassador" alone) are insufficient | [FTC — Disclosures 101 for Social Media Influencers](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) (fetched directly from ftc.gov) | 2026-11-13 |
| Bounty events (special commissions) | e.g., Prime Free Trial / Paid Membership $12.00 (US) | [Standard Commission Income Statement — Special Commission Income](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) | 2026-11-13 |

---

## 3. Repo review (task T1)

- Baseline commit `42f4036` ("Initial commit") contained exactly one file: `README.md` ("# Zone1").
  No code, data, or content existed to audit line by line.
- GitHub Pages was already enabled for the repository on `main` (source: GitHub REST API
  `GET /repos/kanlerxz87-cyber/Zone1/pages` → `"status": "built"`,
  `"html_url": "https://kanlerxz87-cyber.github.io/Zone1/"`).

---

## 4. Site build checks (task T8)

| Check | Method | Result |
|---|---|---|
| Internal link integrity | Automated crawl of every `href`/`src` in all 15 HTML pages + `sitemap.xml`; every internal target must exist in the repo | Passing (see PR checks log) |
| Page smoke test | `python3 -m http.server` + HTTP status check for every page | All pages HTTP 200 |
| Source-link coverage | Every data table row either links an official source or displays the "unverified" badge with the official check URL | Passing |
| Disclosure presence | Required disclosure sentence present in the footer of every page | Passing |
| No-inference audit | Manual re-read of every table cell: values are either (a) verbatim from an official fetch above, or (b) blank + flagged | Passing |

## 5. Irregularities summary (all published on the site's Flagged for Review page)

1. **I-01** — Supplied IDs `B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV` are 9 characters; ASINs are 10
   (official definition sources in §1.3). → Not valid ASINs.
2. **I-02** — Supplied link domain `link.amazon` is not an official Amazon product-link or short-link
   domain (§1.3). → Links are non-compliant as affiliate links.
3. **I-03** — All three supplied URLs land on Amazon's missing-page fallback (random unrelated
   listing), verified individually (§1.2). → Links are broken/unusable for affiliate monetization.
4. **I-04** — Consequently, **all product-level data is unverified**: title, price, rating, review
   count, category, competition, commission rate, and niche are left blank everywhere.
5. **I-05** — No Associates tracking tag (`tag=` parameter) was supplied. Site links are built in
   canonical `https://www.amazon.com/dp/<ASIN>?tag=<YOUR_TAG>-20` form with the tag left as an
   explicit placeholder; they must not be published until a real Associate ID and valid ASINs exist.
