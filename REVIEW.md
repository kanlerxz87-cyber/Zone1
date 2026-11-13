# REVIEW — line-by-line repository review log (2026-11-13)

Scope: the repository `kanlerxz87-cyber/Zone1` as it stood when each session reviewed it.
Every row records what was checked, what was found, the official source used, and the flag
it produced. Flag IDs refer to the live register in `data/flags.json`; the `legacy_ids`
field on each flag records the id it carried in the first session's register.

**Two sessions worked on this repository.**

| Session | Branch | Scope | Outcome |
|---|---|---|---|
| `d14c5409` | `arena/d14c5409-zone1` | Repository review, first data pass, first site build, first PR and merge | Merged to `main` via PRs #1, #2 and #3. Its generator and datasets are preserved in `scripts/build.mjs` and `data/session-d14c5409/`. |
| `zone1-main` | `arena/2bef746a-zone1` | Re-retrieval and verification, the full data model, the thirteen-page site, integration, PR and merge | This review's second half and the live site. |

---

## Part 1 — Repository state (session `d14c5409`, at `main` @ `42f4036`)

| # | Item checked | Result | Source | Flag |
|---|---|---|---|---|
| R1 | Tracked files on `main` @ `42f4036` | Only `README.md` (7 bytes, `# Zone1`, no trailing newline). No code, data, CI or docs. | S12 (`git ls-files`, `git show --stat`) | F-17 |
| R2 | Remote `origin` | `https://github.com/kanlerxz87-cyber/Zone1.git`. `git ls-remote` shows `main` at `42f4036` and no other branches at the start. | S12 | — |
| R3 | Repository visibility and default branch | Public. Default branch `main`. | S12 (GitHub API `repos/kanlerxz87-cyber/Zone1`) | — |
| R4 | GitHub Pages configuration | Already enabled: source `main` `/` (legacy), status `built`, URL `https://kanlerxz87-cyber.github.io/Zone1/`. Served content was the README only. | S12 (GitHub API `repos/.../pages`) | F-12 |
| R5 | Publishing folder option | A branch folder of `/docs` is a supported publishing source. | S11 (GitHub Docs) | — |
| R6 | `.gitignore`, `LICENSE`, CI workflows | None present at the time of review. | S12 | F-17 |
| R7 | Commit author metadata | `kanlerxz87-cyber <kanlerxz87@gmail.com>` on `42f4036`. A personal address is visible in public history. | S12 (`git log`) | F-16 |
| R8 | Git config (`.git/config`) | Holds only the remote URL, refspecs and a noreply committer email. No token or credential is stored in the file. | S12 | — |
| R9 | Branch rules | Session restricted to `arena/d14c5409-zone1`. The coordination spec's `session-<id>/<task>` naming was therefore not used. | Arena branch note | F-22 |
| R10 | Existing coordination board | `COORDINATION.md` did not exist. It was created and claimed (T1–T4) before any other work. | S12 | F-17 |

## Part 2 — Data and claims (session `d14c5409`)

| # | Item checked | Result | Source | Flag |
|---|---|---|---|---|
| D1 | Short link `B04G1MEwY` | Resolves to `amazon.com/dp/B0CDY277D3`. Title and department read from the page. | S4, S1 | F-01 |
| D2 | Short link `B02NbDxp3` | Resolves to `amazon.com/dp/B09B7SB46R`. Title and department read. | S5, S2 | F-01 |
| D3 | Short link `B00hJ57DV` | Resolves to `amazon.com/dp/B08DKYBTPH`. Title and department read from the resolved page. Canonical URL returned an interstitial. | S6, S3 | F-24 (resolved) |
| D4 | Associates tag on resolved links | None of the three resolved URLs has a `tag=` parameter. | S4, S5, S6 | F-19 |
| D5 | Price, rating, reviews, availability | Not present in the retrieved page text. Left blank. | S1, S2, S3 | F-23 (resolved) |
| D6 | Commission rate (Home & Kitchen) | Official schedule redirected to a sign-in page. Third-party sites conflict. Left blank. | S9 | F-04 |
| D7 | Associates disclosure wording | `As an Amazon Associate I earn from qualifying purchases.` (Operating Agreement s.5). | S7 | F-19 |
| D8 | Price display rule | Prices and availability may be shown only if the Amazon link serves them, or via Creators API / PA-API (Participation Requirements s.2(b)). | S8 | F-07 |
| D9 | Non-US account clause | A non-US person agrees to perform services outside the US unless the tax information says otherwise (Participation Requirements s.1). Site owner location: Oslo, Norway. | S8 | F-14 |
| D10 | FTC disclosure guidance | Disclose a material connection where it is hard to miss, near the endorsement. | S10 | F-19 |
| D11 | Brand spelling in titles | `CHEFMAN` (P1) and `Chefman` (P3). Same brand likely but not confirmed. | S1, S6 | F-15 (resolved) |
| D12 | Marketplace | All three resolve to amazon.com (US). Shipping to Norway not verified. | S1, S2, S3 | F-14 |

---

## Part 3 — Repository state after integration (session `zone1-main`)

*Source ids in Parts 3–5 refer to the live register in `data/program.json` (S1–S18). Parts 1–2 use the
first session's register, preserved at `data/session-d14c5409/sources.json` (S1–S12).*

Every line below was checked against the live repository after the first session's PRs had
merged, and again after this session's own commit.

| # | Item checked | Result | Source | Flag |
|---|---|---|---|---|
| R11 | Branches and remotes after PRs #1–#3 | `main` had advanced to `a3f3baa` with three merges; `arena/d14c5409-zone1` was left in place. This session's branch was behind and could not be pushed until the merge was reconciled. | S18 (`git branch -r -v`, `git log --oneline origin/main`) | F-22 |
| R12 | Merge conflict in `COORDINATION.md` | The two sessions both created `COORDINATION.md` from scratch, so the rebase produced an add/add conflict. Neither side was discarded: the first session's claims, sources and completion records were carried into the merged board, and its flags were carried into the live register with `legacy_ids` cross-references. | S18 (`git ls-files -u`, conflict stages 2 and 3) | F-22 |
| R13 | Duplicate file trees | `data/flags.json`, `data/products.json`, `data/program.json`, `README.md`, `index.html` and `COORDINATION.md` existed on both sides with different content. Resolved in favour of the richer datasets, with the first session's versions preserved under `data/session-d14c5409/` and in `legacy/`. | S18 (`git diff --stat origin/main`) | — |
| R14 | `index.html` at the repository root | The first session wrote a redirect to `docs/`; this session writes the landing dashboard itself. The redirect is preserved at `legacy/root-redirect-to-docs.html` and is not published. | S18 | — |
| R15 | Publishing folder `/docs` | The first session's site was published from `docs/`. It is no longer published: the root site is the live one, and `docs/` is now gitignored build output from the archived generator. Publishing two sites would have put a second, weaker copy on the same domain under `/docs/`. | S18 | — |
| R16 | `.gitignore` | Added. `docs/`, `__pycache__/`, `node_modules/`, `.env`, `*.log` and OS cruft are excluded. | S18 | F-17 (action taken) |
| R17 | CI workflow | Added at `.github/workflows/site-check.yml`. It rebuilds the site and fails the build if the committed pages differ from the generator output, then runs the full integrity checker and re-runs the archived build. | S18 | F-17 (action taken) |
| R18 | `LICENSE` | Still absent. A licence was not chosen on the owner's behalf, because it is a legal decision for the copyright holder. | S18 | F-17 |
| R19 | Secret material | No credential, token or key is present in any committed file, and `.git/config` holds no token. | S18 | — |
| R20 | Dependency risk | Neither generator has a third-party dependency. `tools/build_site.py` uses only the Python standard library; `scripts/build.mjs` uses only Node built-ins. | S18 | — |
| R21 | Data-directory discovery | The checker walks the whole tree. It was pointed at `data/` and `legacy/` explicitly so that archived material is not mistaken for published pages. | S18 | — |
| R22 | Unverified values | Every field marked `unverified` is `null` and no sibling product's value was copied into it. Confirmed mechanically by `tools/check_links.py`. | S12 (`data/products.json`) | — |
| R23 | Published figures | No traffic, click, conversion, commission or search-volume figure appears anywhere in the published site. The commission model is published as a model with labelled placeholder inputs. | S18 | F-13, F-20 |
| R24 | Page count and routes | Thirteen published pages; every route returns HTTP 200 from a local static server and every internal link and anchor resolves. | S12 (`tools/check_links.py`, local HTTP check) | — |
| R25 | Accessibility and responsive structure | Every page declares a language, a viewport and a description, has exactly one `<h1>`, no skipped heading level, alt text on every image, a discernible label on every link, a header row on every table, and no dangling `aria-*` reference. | S12 (`tools/check_links.py`) | — |
| R26 | Placeholder Associates tag | The tag placeholder appears only inside copyable template boxes; no rendered anchor carries it. | S12 (`tools/check_links.py`) | F-19 |
| R27 | Disclosure coverage | Both required disclosure strings are present on all thirteen pages. | S12 (`tools/check_links.py`) | F-19 |
| R28 | Page weight | Every page is plain HTML plus one stylesheet and one script. No web fonts, no trackers, no third-party requests. | S18 | — |

---

## Part 4 — Product data, re-verified line by line (session `zone1-main`)

| # | Item checked | Result | Source | Flag |
|---|---|---|---|---|
| D13 | P1 rating and rating count | `4.2` stars from `4,859` ratings. | S10 | — |
| D14 | P1 demand and rank | `1K+ bought in past month`; Best Sellers Rank `#5,644` in Kitchen & Dining and `#35` in Air Fryers. | S10 | F-05 |
| D15 | P1 price block | New `$79.93` with `-20%` against a `$99.99` list price, `$39.97` per count. | S10 | F-07 |
| D16 | P1 second offer | `$57.45`, `-43%`, `$28.73` per count. Amazon's embedded buy-box payload tags it `buyingOptionType: USED`, so it is published as the used-condition offer, not as a second new-condition price. The rendered block shows no condition word next to it. | S10 | F-02 |
| D17 | P1 capacity | Amazon's structured details render `6 liters`; the title and the manufacturer bullets state a 6-quart combined capacity with 3-quart baskets. Both are published. | S10 | F-06 |
| D18 | P1 specifications | `13.38"D x 11.81"W x 10.63"H`; Metal, Plastic; Black, Gray; 120 V / 1700 W; 200–450 °F; dishwasher-safe nonstick baskets; cETL approved; one-year assurance; model `RJ38-SQPF-3TDB-2W`; UPC `810087845025`. | S10 | — |
| D19 | P1 warranty and date first available | The Item details block was read in full and exposed neither row. Both are blank and flagged. | S10 | F-09 |
| D20 | P1 User Guide | The manufacturer's PDF linked from Amazon is published as the product document. | S17 | — |
| D21 | P2 identity | `Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven`, Home & Kitchen. Read from Amazon's own search result for the ASIN, because the detail page serves a reduced body. | S12 | F-03 |
| D22 | P2 rating and demand | `4.3` stars from `18.3K` ratings; `4K+ bought in past month`. | S12 | — |
| D23 | P2 price | Early Black Friday Deal `$149.99` against a `$209.99` list price, with an alternate offer at `$92.99`. | S12 | F-07, F-05 |
| D24 | P2 specifications | Not readable — the detail page serves a reduced body. Dimensions, weight, wattage, material, model number, UPC, Best Sellers Rank, temperature range, warranty and date first available are all blank and flagged. | S12 | F-03 |
| D25 | P3 identity | `Chefman Air Fryer 8 Qt | TurboFry® 4-in-1`, Home & Kitchen. | S11 | F-24 (resolved) |
| D26 | P3 rating and demand | `4.4` stars from `16,861` ratings; `3K+ bought in past month`; Best Sellers Rank `#537` in Kitchen & Dining and `#8` in Air Fryers. | S11 | — |
| D27 | P3 price | New `$79.91` against a `$119.99` list price; used `$51.94`. | S11 | F-07 |
| D28 | P3 specifications | 450 °F Hi-Fry; Bake, Dehydrate, Frozen; XL nonstick dishwasher-safe basket; 1700 W / 120 V; 94 °C–400 °F; `12.75"D x 13.5"W x 10"`; 12.8 lb; one-year limited warranty; model `RJ38-SQSS-8T`; UPC `816458024518`. | S11 | — |
| D29 | Brand identity across P1 and P3 | Both product pages resolve to the same Chefman storefront, and both Item details blocks list `Brand Name: Chefman` and `Manufacturer: Chefman`. The two listings are the same brand — confirmed, not assumed. | S10, S11, S16 | F-15 (resolved) |
| D30 | Competitive set | Each product page surfaces sibling listings from the same category; each competitor's price is read from the same official page and published with it. | S10, S12, S11 | F-05 |
| D31 | Demand and trend evidence | Built only from Amazon's own published signals — Best Sellers Rank, "bought in past month", rating depth, the brand panel's trend labels and Amazon's own competitive set. No search volume, keyword difficulty, competitor traffic or category conversion benchmark was available from an official source, so none is published. | S10, S12, S11 | F-13 |
| D32 | Commission model | The rate card redirects to a sign-in wall, so no rate is stated. The earnings-per-click model on the research page carries the publisher's own rate as a labelled placeholder input. | S3 | F-04 |
| D33 | Marketplace and destination | All three resolve to amazon.com, the United States marketplace. No delivery date, shipping cost or non-US price is asserted anywhere. | S10, S12, S11 | F-14 |

---

## Part 5 — Compliance and content, checked line by line

| # | Item checked | Result | Source | Flag |
|---|---|---|---|---|
| C1 | Required Associates statement | "As an Amazon Associate I earn from qualifying purchases." (Operating Agreement s.5) appears in the footer of all thirteen pages. | S1 | F-19 |
| C2 | FTC affiliate wording | "qualifying purchases made through our links" appears above every monetised block and in the footer of all thirteen pages. | S4 | — |
| C3 | Disclosure placement | Disclosures sit directly above the recommendation and beside the link, never only at the end of an article or only in the footer. | S4, S5 | — |
| C4 | Vague disclosure wording | "Sponsored by", `#ad` and "affiliate link" are used. `#sp`, `#spon`, `#collab`, "ambassador" and "partner" as a bare endorsement are not used. | S5 | — |
| C5 | Trademark and image use | No Amazon logo, seller logo or third-party trademark is used as a site asset. Brand names are used nominatively and linked to the official product page. | S2 | — |
| C6 | Original content | Every marketing page is written for this project; no Amazon editorial content is reproduced. Manufacturer bullets are quoted verbatim and attributed, with the source linked. | S2 | — |
| C7 | Price display rule | Static prices are published as dated research snapshots with the caveat printed on the same page, and the two compliant routes are recorded before live use. | S2 | F-07 |
| C8 | Rating and review display rule | Static star ratings and review counts carry the same dated-snapshot treatment, with the two compliant routes recorded. | S2 | F-08 |
| C9 | Redirecting links | No supplied `link.amazon` URL is used as an outbound link. Every outbound link is a direct `/dp/<ASIN>` URL carrying the publisher's tag. | S2 | F-11, F-18 |
| C10 | Data mining and model training | No build step fetches Amazon. The Program Content licence's data-mining and model-training restrictions are recorded in `data/program.json` and no scraping exists in the repository. | S2, S7 | F-10 |
| C11 | Robots policy | Amazon's `robots.txt` was read directly and its disallow list is recorded verbatim in `data/program.json`. | S7 | F-10 |
| C12 | Endorsement truthfulness | No performance claim is made that was not read from the manufacturer or from Amazon. The used-versus-new condition distinction for P1 is stated explicitly. | S5, S10 | F-02 |
| C13 | Prohibited content | The site carries no incentives to purchase, no claims about the availability of a discount, and no framing of an affiliate relationship as an endorsement by Amazon. | S2 | F-19 |
| C14 | Non-US publisher clause | Quoted verbatim in `data/program.json` (term C-29) and published on the compliance page. | S2 | F-14 |
| C15 | Market and delivery | Every price row is a United States marketplace value; no delivery promise is made. | S2 | F-14 |

---

## Method and limits

- Retrieval used a page fetch that returns the text an anonymous visitor sees. Amazon serves
  product-detail blocks inconsistently to that client, which is why two of the three products
  needed a second retrieval path before their price, rating and review count became
  readable, and why Product 2's detail page still serves a reduced body.
- **No build step in this repository fetches Amazon.** Amazon's `robots.txt` disallows a long
  list of AI and research agents, and the Program Content licence prohibits data-mining and
  model-training on Program Content (flag F-10). Every value was read by hand during
  verification and recorded in the datasets with its URL.
- No value was taken from a third-party retailer, a price-comparison site, a review site or a
  keyword tool. Where those would normally be the source, the field is blank and flagged.
- No browser screenshot was taken; the sandbox has no browser. Layout was verified
  structurally — HTTP 200 on every route, balanced tags, heading order, alt text, table
  headers, and a mobile breakpoint in the stylesheet.
- The live pages were re-fetched from their published URL after the merge to confirm that
  what GitHub Pages serves is what the checker verified.

## Manual review links

**Products**

- https://www.amazon.com/dp/B0CDY277D3?psc=1&language=en_US
- https://www.amazon.com/s?k=B09B7SB46R
- https://www.amazon.com/dp/B08DKYBTPH?psc=1&language=en_US&th=1
- https://m.media-amazon.com/images/I/91jAOUF-OyL.pdf (Product 1 User Guide)

**Short links as supplied**

- https://link.amazon/B04G1MEwY
- https://link.amazon/B02NbDxp3
- https://link.amazon/B00hJ57DV

**Programme and policy**

- https://affiliate-program.amazon.com/help/operating/agreement
- https://affiliate-program.amazon.com/help/operating/policies
- https://affiliate-program.amazon.com/help/operating/schedule (not reachable — sign-in)
- https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
- https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255
- https://www.amazon.com/robots.txt

**Repository and deployment**

- https://github.com/kanlerxz87-cyber/Zone1
- https://api.github.com/repos/kanlerxz87-cyber/Zone1
- https://api.github.com/repos/kanlerxz87-cyber/Zone1/pages
- https://kanlerxz87-cyber.github.io/Zone1/

**Source register**

- The live register is [`data/program.json`](data/program.json) (`sources` S1–S9) and the
  rendered version is [`pages/sources.html`](pages/sources.html).
- The first session's register is preserved at
  [`data/session-d14c5409/sources.json`](data/session-d14c5409/sources.json) (S1–S12).
