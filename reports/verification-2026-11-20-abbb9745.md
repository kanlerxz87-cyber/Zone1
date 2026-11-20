# Verification and change report — 2026-11-20 (UTC)

**Session:** `arena/abbb9745-zone1`
**Branch:** `arena/abbb9745-zone1`, based on `main` @ `1c7de82` (merge of PR #185)
**Scope:** reader-facing polish, search-result metadata, live re-read of the supplied links and the policy clauses that govern them
**Status:** site rebuilt, every gate green, three flag rows published, no product, account, tag, analytics or ledger value changed

---

## 1. What changed, and why

### 1.1 Reader surfaces now cite sources by name (not by register number)

Measured on the build this pass started from: the front page carried **22** tiny `S10`/`S18`-style badges
between the reader and the product facts, and an article carried **12** — the single strongest
"reads like an internal audit" signal on the two most-visited surfaces, and the exact thing the brief
asks to remove ("make it read like a shop, not an audit").

- `build.src_link()` / `build.src_links()` take `words=True`: the link text becomes the source's short
  human name (`Chefman RJ38-SQSS-8T guide`, `Operating Agreement`, `USDA temperature chart`) and the
  register id moves into a `data-src-id` attribute.
- Applied to: landing/category product cards (one "From the documents:" line per card instead of a
  badge after every value), every article section's "Sources for this section" line, and the prose
  facts on the five product pages.
- **The guarantee is not weakened.** `verify.py` check 2b now resolves both badge forms: a badge whose
  text is the id and a badge whose id sits in `data-src-id` are each required to link to the URL
  registered for that id. A negative test was run (a word badge pointing `S13` at the wrong URL, and a
  badge naming an unregistered `S999`) — both failed the gate as intended.
- 49 readable short names were authored into `data/sources.json` (`short`). No URL, organisation,
  title or read date in that file changed.

### 1.2 A search-result metadata budget, with a gate

Measured before the repair: **13** shipped pages had a `<title>` over 65 characters (longest: 133) and
**10** had a meta description over 160 (longest: 259). Nothing in the build or the gates had a budget,
so the first sentence a search engine shows was routinely the cut-off half of a longer one — the
"make it findable" half of the brief.

- `build.seo_title()` / `build.seo_description()` compose the `<head>` only: an authored override
  first, then the page title with the `· Zone1 Kitchen` suffix dropped when that alone fits, then a
  word-boundary cut that prints a warning naming the page. Reader headlines, H1s and card copy are
  unchanged.
- `verify.py` check **8** fails the build if any shipped publication page exceeds 65 / 160 characters,
  and `tests/test_publication.py` pins the same budget plus the fallback behaviour.
- Result: **0** pages over budget (was 23 rows across 13 + 10 pages).

### 1.3 Two registers the pass could not leave as it found them

- **F113** — the policy text and the supplied links, side by side for the first time (see §4).
- **C20** — the same finding as a cited row in the compliance register on
  [`compliance.html`](../compliance.html), so it is visible where a reader or reviewer looks for policy
  rather than only in the flag table. (This row was drafted as C19. While this branch was open, a concurrent
  session — `arena/69c1201a-zone1`, PR #190 — merged its own **C19** for the tag-as-URL-parameter clause.
  Their row is kept as C19 unchanged; this pass's redirect clause is published as C20 so two different
  records never share an id.)

---

## 2. Live re-reads performed in this session (2026-11-20 UTC)

Every value below was read from a live response in this session. Sources not listed here were **not**
re-read and keep the date of the pass that read them; the dated record is
`reverified_2026_11_20_abbb9745` in [`data/sources.json`](../data/sources.json).

| Source | What was read | Result |
|---|---|---|
| [link.amazon/B04G1MEwY](https://link.amazon/B04G1MEwY) (PI-01) | final URL and landing title | `/dp/B0CDY277D3`; title matches the stored observation character for character |
| [link.amazon/B02NbDxp3](https://link.amazon/B02NbDxp3) (PI-02) | final URL and landing title | `/dp/B09B7SB46R`; title matches the stored observation |
| [link.amazon/B00hJ57DV](https://link.amazon/B00hJ57DV) (PI-03) | final URL and landing title, twice (chunk 0 and the product-detail chunk) | `/dp/B08DKYBTPH`; title matches. **The 2026-11-19 homepage landing recorded as F106 did not reproduce** |
| [link.amazon/B0c8moW59](https://link.amazon/B0c8moW59) (PI-04) | final URL and landing title | `/dp/B0DHZTCNR5`; title matches |
| [link.amazon/B0f3GKalj](https://link.amazon/B0f3GKalj) (PI-05) | final URL and landing title | `/dp/B0DZFD6R9Z`; title matches |
| [S1 Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) | heading date and §1 | "Updated: October 15, 2025". §1 requires links to "properly use the special 'tagged' link formats" to be Special Links |
| [S2 Program Policies](https://affiliate-program.amazon.com/help/operating/policies) | Participation Requirements §2(a)-(b), Commission Income Statement §2(e), price rule | Quotes in §4 below. The price rule confirms why the site shows no Amazon price |
| [S8 FTC Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | disclosure placement and wording | "hard to miss", with the endorsement itself, simple language ("ad", "sponsored"), not only a platform tool. Page foot date: November 2019 |
| [S10 Chefman 6 Qt dual-window page](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) | full specification block | Capacity 6 Qt / 5.67 L; 200-450 °F; **Dimensions 13.38 × 11.81 × 10.63 in** (identical to the published value); 1700W/120V; model RJ38-SQPF-3TDB-2W; "Max temp: 450 ºF with Hi-Fry function". Review widget read 4.6 / 1313 (volatile) |
| [S48 USDA FSIS chart](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart) | minimum internal temperatures | 145 °F + 3-min rest (whole cuts), 160 °F (ground meat), 165 °F (all poultry, leftovers, casseroles) — matches the thermometer pages |

**Observation, not a publication:** every fetched Amazon page displayed a price ($74.99, $229.99,
$16.99, $139.99, $59.99 on a cross-sell). None of these were copied into the site: the price rule read
in S2 permits displaying prices only when Amazon serves the link or via Creators API/PA API. The empty
price column stays empty.

**Second observation:** the PI-03 landing page states both "1000 Watts/120 Volts – RJ38-SQSS-8T" (item
bullets) and "1700W/120V" (product description) in the same page. The site's 8 Qt wattage row stays
blank and flagged rather than choosing one of those numbers. No value was changed in this pass.

### Not re-read in this pass (and therefore not claimed)

S3–S7, S9, S11–S16, S18–S47, S49 — including the Emeril brand page and manual, both Chefman 8 Qt pages,
both thermometer brand sites, and the remaining Amazon help topics. Their published values keep their
existing dated provenance. This is a scoped re-read, not a re-verification of the whole register.

---

## 3. Checks run on the merged tree

| Check | Result |
|---|---|
| `python3 build.py` | 63 pages, 41 sitemap URLs, 26 RSS items; byte-identical on a second run |
| `python3 verify.py` | 141 pages, 77 spec rows (75 verified, 2 blank + flagged), 49 sources, **0 errors**, 0 external warnings |
| `python3 -m unittest discover -s tests` | **78** tests OK (75 before this pass, 3 added) |
| `node --test tests/*.test.cjs` | 14 tests pass |
| platform engine tests | 33 tests OK |
| data audit (`platform/audit/report.py`) | clean |
| `scripts/build_s2_site.py --check` | current (16 files) |
| `scripts/check_links.py` | **12,609** links OK |
| `bash scripts/ci-check.sh` | OK end to end |
| independent page audit (titles, descriptions, canonical, H1 count, disclosure order, JSON-LD parse, sitemap→file existence, og:image) | 63 pages: 0 duplicate titles, 0 duplicate descriptions, 0 JSON-LD parse failures, 0 disclosure-order failures, 41/41 sitemap URLs exist |
| sponsored coverage of outbound product anchors | 347 product anchors, **0** unqualified. The only 8 unqualified matches in the tree are `link.amazon/ZZZ9ZZZZZ`, a placeholder string, never a real destination |
| negative tests of the two new gates | failing title (170 chars) → verify fails; `S13` badge pointed at another URL → verify fails; `S999` badge → verify fails |

---

## 4. Irregularities as published (nothing here blocks deployment)

**F110 — search-result metadata over budget (recorded by another session, and this pass's draft of the
same finding is withdrawn).** This pass wrote the finding up as F107 before merging. While the branch was
open, the concurrent session `arena/b6891e75-zone1` (PR #188) merged **F110** for the same defect (27 of 63
pages at that point) and took **F107** for an unrelated source-register finding. Two ids for one defect is
the kind of duplication this repository's coordination protocol exists to stop, so this pass keeps F110 as
the record and dropped its own row; the repair it made is unchanged. 13 titles / 10 descriptions over the
display budget at the time it was measured, repaired and gated as described in §1.2. Source links on the row: Google page-experience (§4) and
sitemap documentation. Not claimed: any ranking effect, or that 65/160 are published specifications —
they are conventional display budgets, and the row says so.

**F112 — seven open pull requests from earlier sessions.** #139, #141, #144, #146, #150, #159, #168,
#173, each verified through the GitHub API today as `OPEN` with no merge commit, while `main` is at
`1c7de82`. Some of their content is superseded by work that did merge; some (the probe-in-an-air-fryer
guide, the de-index generators) is not on main at all. This pass neither merged nor closed any of them
and edited only its own branch. The row asks a later integration session to diff each against `main`,
keep what is new, and record the decision.

**F113 — the tag/redirect question, quoted rather than judged.** Read live today:

> "Special Links must use the Associates ID we have assigned to you." — S2, Participation Requirements §2(a)
>
> "All Special Links must be accessed directly from your Site. For example, you must include your
> Associates ID or 'tag' (appearing as XXXXX-## …) as a parameter in the URL of each link you place on
> your Site to an Amazon Site." — S2, Participation Requirements §2(b)
>
> "… any Product purchased by a customer who is referred to an Amazon Site by a link that sends users
> indirectly to an Amazon Site via an intermediate site, without requiring the customer to click on a
> link or take some other affirmative action on that intermediate site (a 'Redirecting Link')" — S2,
> Commission Income Statement §2(e)
>
> "The links must properly use the special 'tagged' link formats we provide and comply with this
> Agreement ('Special Links')." — S1, §1

What the live links did: all five resolved from the intermediate host `link.amazon` to an
`amazon.com/dp/` page automatically, and each final URL carried `btn_ref=srctok-<opaque token>` and
`plpRedirect=mhFallback` with **no visible `tag=` parameter**.

What that is not: a finding that the links are invalid or that the account is in breach. The token may
carry an Associates ID server-side; `link.amazon` is plausibly an Amazon-operated redirector; and §2(e)
turns on whether the customer is required to take an affirmative action, which a browser click may
satisfy differently from a server-side fetch. The compliance status of the supplied links stays
unresolved in both directions (Zone3 FLG-003).

What it is: a compliance risk worth surfacing on the money pages, with the fix that was already
recommended — generate one tagged Special Link per product inside Associates Central, run the
single-link test (SG-02/SG-37), and record destination plus Associates Central report in
`data/product-intent.json`.

**F106 (carried, not closed).** The 2026-11-19 observation that PI-03 twice landed on the Amazon
homepage did not reproduce today: both fetches reached `/dp/B08DKYBTPH`. The historical record is not
overwritten; today's observation is added beside it. Two readings of the same token on two days is the
kind of instability the intended-listing test exists to catch.

---

## 5. Boundaries this pass did not cross

- No product specification, ASIN, intended-listing, tag or commission value was changed. `intended_asin`
  remains blank on all five rows; `shopnow047c-20` remains recorded, unvalidated and applied to no link.
- No Amazon price, rating, ranking, traffic, conversion or revenue figure is published anywhere in this
  patch, including the prices that were on screen during the verification reads.
- Production analytics stays off, the campaign ledger stays empty, no Search Console action was taken.
- No annex tree (`site/`, `s2/`, `dashboard/`, `research/`, `docs/`, `annex-*`), no `session-*` directory
  and no workflow file was edited.
- No other session's branch was merged, closed or rewritten. Two sessions were live during this pass
  (`arena/8ab133ea-zone1` = PR #186 and `arena/1875c5bb-zone1`); both touch `COORDINATION.md` and the
  second also regenerates product pages, so this pass rebases before merging and resolves
  `COORDINATION.md` by keeping both sides.

---

## 6. Links for manual review

| What to check | Link |
|---|---|
| The five supplied links (unchanged in this repo, fetched today) | [B04G1MEwY](https://link.amazon/B04G1MEwY) · [B02NbDxp3](https://link.amazon/B02NbDxp3) · [B00hJ57DV](https://link.amazon/B00hJ57DV) · [B0c8moW59](https://link.amazon/B0c8moW59) · [B0f3GKalj](https://link.amazon/B0f3GKalj) |
| Special Link / tag / redirect clauses | [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement) · [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) |
| Disclosure rules | [FTC Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) · [FTC Endorsement Guides](https://www.ftc.gov/business-guidance/advertising-marketing/endorsements-influencers-reviews) |
| Temperature values on the thermometer pages | [USDA FSIS chart](https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart) |
| The 6 Qt dimensions and model number on the front page | [Chefman 6 Qt dual-window page](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) |
| What this pass changed on the live site | [Home](../index.html) · [Compliance C20](../compliance.html) · [Flagged F110 · F112 · F113](../flagged.html) |
| The open pull requests named in F112 | [#139](https://github.com/kanlerxz87-cyber/Zone1/pull/139) · [#141](https://github.com/kanlerxz87-cyber/Zone1/pull/141) · [#144](https://github.com/kanlerxz87-cyber/Zone1/pull/144) · [#146](https://github.com/kanlerxz87-cyber/Zone1/pull/146) · [#150](https://github.com/kanlerxz87-cyber/Zone1/pull/150) · [#159](https://github.com/kanlerxz87-cyber/Zone1/pull/159) · [#168](https://github.com/kanlerxz87-cyber/Zone1/pull/168) · [#173](https://github.com/kanlerxz87-cyber/Zone1/pull/173) |
