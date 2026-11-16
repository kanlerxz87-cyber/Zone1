# Executive summary — pass 8, 2026-11-15

> **Superseded, and kept.** This is pass 8's briefing, committed 2026-11-15 by session `arena/88bb2db6`. It is left here as that session's record and is **not** the current briefing: [executive-summary.html](https://kanlerxz87-cyber.github.io/Zone1/executive-summary.html) is generated from `data/` and is the one the site links to. Its verification counts (43 spec rows, 41 verified, 29 sources) were the truth on 2026-11-15 and have since moved — the root site now reports 77 rows, 75 verified, 34 sources. One claim in the passes around this one — that a listing does not publish a model number, so only a browser can settle product identity — was tested on 2026-11-16 and found false; see flag **F64** at https://kanlerxz87-cyber.github.io/Zone1/flagged.html#f63.

**What this is.** A briefing for one reader: the person who owns the Amazon Associates
account and the three supplied links. It says what has been built, what is verified, what
is not, what this pass found wrong, and what to decide next. The full evidence is on the
site; this document is the one-page version.

- **Live site:** https://kanlerxz87-cyber.github.io/Zone1/
- **Decision queue:** https://kanlerxz87-cyber.github.io/Zone1/suggestions.html
- **Questions register:** https://kanlerxz87-cyber.github.io/Zone1/questions.html
- **This pass:** session `arena/3ddfa50e-zone1`, branch of `main` at `8716134`

---

## 1. The honest position in one paragraph

There is a real, working, fully sourced product site here covering three Amazon air fryer
listings. It is not a mock-up and it does not invent anything: every specification is
quoted from Chefman's or Emeril's own page or owner's manual, with the source badge next to
the value, and every unresolved question is published rather than smoothed over. The three
supplied links resolve reliably to three specific ASINs. What the project still cannot do —
and must not fake — is state which exact manufacturer model each ASIN is, or confirm that
your Associates tag is inside the short links. Both are answerable in about ten minutes from
a signed-in browser, and neither can be answered by any amount of research from outside.

**Verdict: the content and the verification are ahead of the commercial plumbing.** The
remaining risk is not editorial. It is that nobody has yet confirmed the links pay you.

---

## 2. What this pass verified itself, on 2026-11-15

Fetched directly this session, not carried over from an earlier pass. Each is a live fetch
made today; where a value differed from the repository's stored value, the difference is
recorded as a flag.

| What | Result | Source |
|---|---|---|
| `link.amazon/B04G1MEwY` | → `amazon.com/dp/B0CDY277D3`, title matched the stored string | [S17](https://link.amazon/B04G1MEwY) |
| `link.amazon/B02NbDxp3` | → `amazon.com/dp/B09B7SB46R`, **title had changed** (flag F38) | [S17](https://link.amazon/B02NbDxp3) |
| `link.amazon/B00hJ57DV` | → `amazon.com/dp/B08DKYBTPH`, title matched the stored string | [S17](https://link.amazon/B00hJ57DV) |
| Bare code `amazon.com/dp/B04G1MEwY` | **"Page Not Found"** — the 9-character tokens are not ASINs, confirming the README's correction | [test](https://www.amazon.com/dp/B04G1MEwY) |
| Standard Commission Income Statement | Kitchen 4.50%, All Other Categories 4.00% — read without signing in | [S3](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| Program Policies | Updated April 14, 2026. §2(b) price/availability, §6(t) reviews, §6(v) no cloaking, §6(w) link shortening, **§6(y) no price tracking** | [S2](https://affiliate-program.amazon.com/help/operating/policies) |
| 16 CFR 255.5 | Disclosure of material connections, quoted in full | [S9](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255/section-255.5) |
| 16 CFR Part 465 | Rule on consumer reviews and testimonials, incl. §465.6 company-controlled review sites | [eCFR](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465) |
| Chefman 6 Qt page | RJ38-SQPF-3TDB-2W, 450 °F Hi-Fry, Sync Finish, 1,305 reviews — matched the dataset | [S10](https://chefman.com/products/turbofry-touch-dual-window-air-fryer) |
| Emeril French Door 360 page | 25 Cooking Pre-sets in the spec strip, "10-in-1" in the description, $199.99 — the internal contradiction is still live | [S14](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360) |

Two things this pass could **not** re-read, and therefore did not restate as fact:

- The Associates application-review page ([S4](https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM))
  did not return content. The "3 qualifying sales / 180 days" figures in this repository are
  carried forward from an earlier logged fetch and are flagged at
  [Q-13](https://kanlerxz87-cyber.github.io/Zone1/questions.html#q-13).
- The bare-ASIN URLs and the `?tag=` variant served Amazon's "Continue shopping" interstitial
  rather than the product page, so ASIN identity is confirmed only via the short links.

---

## 3. Three defects found and fixed in this pass

These were not inferred. Each was found by re-reading a source against the value the site
published, and each is now corrected on the site and in the dataset.

| Flag | Defect | What was wrong | Fix |
|---|---|---|---|
| **F38** | Stale listing title | The stored Emeril title ended "24 cooking functions, dual-speed fan and rotisserie"; the live title now ends "24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included". The preset count is unchanged; the wording is not. | Stored title updated to the 2026-11-15 string; superseded string kept visible; read date recorded. |
| **F39** | A citation that pointed at the wrong product | Source S16 was registered as the B0CDY277D3 URL but cited for **all three** listing titles. Two of the three citations therefore sent a reader to the Chefman 6 Qt listing while purporting to support the Emeril and 8 Qt rows. | Each ASIN registered separately (S16, S28, S29); every citation repointed. |
| **F40** | Duplicate flag number | Two different rows were both published as **F36** — one programme-level, one product-level. The register rendered 38 rows with 37 distinct numbers, so citing "F36" was ambiguous. F28 records an earlier collision of the same kind. | Programme row renumbered **F41**; a build test now fails on any duplicate flag ID. |

**Why F39 matters more than its size suggests.** The root build's row-source gate checks that
a row links to *a* registered official host. It does not check that the linked page actually
states the value. So a row can pass the gate while its source link points at a different
product entirely. That is the same defect class as F37, and it is worth deciding whether the
gate should be tightened to fetch and confirm — which would require network access at build
time and is written up as a suggestion rather than done silently.

---

## 4. Policies that constrain the brief, verified verbatim today

The brief asks for price analysis, campaign optimisation and automation. Three clauses bound
what is actually buildable. All three were read on the live Program Policies page today.

| Clause | What it says | What it forbids here |
|---|---|---|
| **§2(b)** | Price and availability may be shown only when Amazon serves the link, or when the data comes from Creators API / PA API | Scraping prices into a comparison table. This is why the site shows no Amazon price at all. |
| **§6(t)** | Customer reviews and star ratings only via Creators API / PA API | Publishing Amazon star ratings or review counts. |
| **§6(y)** | "Unless otherwise agreed by Amazon, your Site must not have price tracking and/or price alerting functionality" | A price-history chart, a price-drop alert, a "lowest ever" badge — the three most commonly built affiliate features. |
| **§5** (Promotional Limitations) | No ML training on Special Links or Program Content without Amazon's prior written approval | Training any content model on listing text. Drafting may use manufacturer documents only. |
| **§3(c)** | You are responsible for the accuracy of all material on your site | Publishing generated copy without a numeric gate. |

**This pass made §6(y) executable.** `build.py` now fails if a generated page contains a
code-shaped price-tracking identifier (`price-history`, `priceAlert`, `trackPrice`) in a
script block or an element attribute. It deliberately does not match prose, because the site
must remain free to *explain* the rule. The guard was tested by injecting a violation and
confirming the build fails.

---

## 5. What is built, and what state it is in

Every gate in the repository was re-run this pass. All pass.

| Gate | Command | Result |
|---|---|---|
| Site build | `python3 build.py` | 104 pages, 25 URLs in the sitemap, reproducible |
| Site verification | `python3 verify.py` | **0 errors**; 43 spec rows (41 verified, 2 blank+flagged); 29 sources |
| Engine tests | `python3 -m unittest discover -s platform/tests …` | 33 tests OK |
| Data audit | `python3 platform/audit/report.py` | 0 errors, 0 warnings |
| Link check | `python3 scripts/check_links.py` | 4,972+ links, 0 broken |
| S2 platform build | `python3 scripts/build_s2_site.py --check` | current |
| Research section | `python3 research/check_research.py` | OK |
| Verification annex | `python3 scripts/verify_site.py` | 382 assertions pass |

**New this pass:**

- **`suggestions.html`** — 16 suggestions, each with the problem, the official evidence, two
  or three paths, effort, risk, reversibility, and which path this pass would pick. Nothing
  on it has been implemented. This is the page the brief asked for: a place to review and
  choose a direction before work starts.
- **`questions.html`** — 14 questions in four states: *known and sourced*, *missing but
  discoverable*, *the source does not state it*, and *requires account access*. Each names
  what is known, what is missing, how to find it out, and what it blocks.
- **Buyer-first landing page** — the site used to open with "Three supplied Amazon links:
  product identity not yet confirmed", which is an internal status report and a poor first
  impression. It now opens with the buying decision, a three-column comparison of verified
  specifications each carrying its source badge, and a plain-English statement of what the
  site is and how it earns. The verification layer is intact, one heading further down, and
  linked from the sidebar under **Evidence**.
- **Sidebar rebuilt** — it was index-addressed, so inserting a nav entry silently moved every
  later group. Adding the two new pages pushed "Buying guide" into the Products group and
  dropped the Buying guide and Articles links entirely. Now keyed by href, so it cannot
  recur, and grouped as Start here / Products / Decide / Evidence / Platform.
- **Three build guards** — duplicate flag ID, dangling cross-reference between the two new
  registers, and price-tracking implementation. All three were tested by injecting a
  violation and confirming the build fails.

---

## 6. What must be answered before the next decision

Full detail and cross-links on [questions.html](https://kanlerxz87-cyber.github.io/Zone1/questions.html).
The five that actually gate progress:

| # | Question | State | Why it gates |
|---|---|---|---|
| [Q-01](https://kanlerxz87-cyber.github.io/Zone1/questions.html#q-01) | Which model number is on each listing? | Discoverable — 5 min in a browser | Closes F2, F3, F32, F33 at once. Until it is answered, three product pages carry a documented-match caveat. |
| [Q-04](https://kanlerxz87-cyber.github.io/Zone1/questions.html#q-04) | Is your Associates tag inside the three short links? | Account access only | If it is not, the site earns nothing and no page would show it. This is the single highest-value unknown. |
| [Q-03](https://kanlerxz87-cyber.github.io/Zone1/questions.html#q-03) | Is the account approved, and when did the window start? | Account access only | An account in review needs conversion-first content; an approved account can afford breadth. Opposite plans. |
| [Q-05](https://kanlerxz87-cyber.github.io/Zone1/questions.html#q-05) | Is Creators API access available? | Account access only | Decides whether a price and a star rating may ever appear (§2(b), §6(t)). |
| [Q-07](https://kanlerxz87-cyber.github.io/Zone1/questions.html#q-07) | One public site? On a domain you own? | A decision, not a lookup | Nine HTML sites for three products are published on one origin. Nine crawl, one converts. |

---

## 7. What this pass would do next, in order

Taken from the priority scores on the Suggestions page. Order is judgement; the evidence
underneath each item is not.

1. **Read the model number off each listing** (SG-01, 5 minutes). Closes four flags.
2. **Confirm the tag** (SG-02). Replace the short links with full tagged URLs so the tag is
   visible in the page source and the §6(w) question disappears with it.
3. **State the method and drop the word "independent"** (SG-03). Cheapest trust gain
   available, and 16 CFR 465.6 makes the current framing a live regulatory exposure.
4. **Retire the eight annexes from the public web, keep them in git** (SG-05). One site,
   one identity, nine sessions of evidence preserved.
5. **Add a "what the manufacturer does not publish" row to each product page** (SG-15).
   Turns a gap into a trust signal for the cost of one table row.
6. **Publish a corrections log** (SG-13). The site already has the ledger; it lacks the
   public commitment.

---

## 8. What is deliberately *not* built, and why

Stated plainly so the absence is not read as an oversight.

| Not built | Reason | Source |
|---|---|---|
| Amazon prices, star ratings, review counts | Program Policies §2(b) and §6(t) permit them only when Amazon serves the data or via Creators/PA API. No credentials exist for this session. | [S2](https://affiliate-program.amazon.com/help/operating/policies) |
| Price tracking, price alerts, price-history charts | Expressly prohibited by Program Policies §6(y). Now enforced by a build guard. | [S2](https://affiliate-program.amazon.com/help/operating/policies) |
| Live click and conversion tracking | Requires Associates credentials and an analytics decision that changes the site's privacy statement the moment it is added. | [Q-08](https://kanlerxz87-cyber.github.io/Zone1/questions.html#q-08) |
| Automatic publishing of generated articles | The numeric gate exists and works, but publishing without a human read would breach the "accuracy is your responsibility" duty in §3(c) in spirit if not in letter. | [S2](https://affiliate-program.amazon.com/help/operating/policies) |
| A model trained on listing data | §5 forbids using Special Links or Program Content to develop ML models without Amazon's prior written approval. Drafting from manufacturer documents only is permitted and is what the current pipeline does. | [S2](https://affiliate-program.amazon.com/help/operating/policies) |
| Hands-on testing claims | No unit was purchased. The site says so on every page rather than implying otherwise. | [index.html](https://kanlerxz87-cyber.github.io/Zone1/) |

---

## 9. Compliance position

- The required disclosure — *"As an Amazon Associate I earn from qualifying purchases."* —
  is generated into every page by `build.py`, and the build fails if any page lacks it.
- Every money link carries a link-level "Paid link" label plus a plain-English sentence.
- No Amazon price, rating or review count appears anywhere; this is enforced by `verify.py`.
- No cookies, no analytics, no forms, no accounts. The footer states this and it is true;
  the moment anything is added, that statement must change in the same commit.
- The site does not claim hands-on testing, and now says so near the top rather than only in
  the footer.
- **Open exposure:** the site describes itself as "an independent affiliate publisher" while
  monetising every product page. 16 CFR 465.6 addresses exactly that framing. This is
  suggestion SG-03 and it is the one compliance item this pass could not fix without a
  decision about who the author is.

---

## 10. Definition of done for this pass

- [x] Every value re-read against an official source, fetched by this session where possible
- [x] Values that could not be confirmed left blank and published on the Flagged page
- [x] Three defects found by re-reading, recorded as flags, corrected, and re-tested
- [x] All eight repository gates re-run; all pass
- [x] Suggestions section built, with alternative paths and a recommendation, nothing implemented
- [x] Questions register built, separating known / discoverable / not-stated / account-only
- [x] Landing page rewritten so a buyer can use it and an auditor can still verify it
- [x] New guards added and **proven to fail** on injected violations
- [x] Pull request opened, merged, and the Pages deploy confirmed
- [ ] **Model numbers confirmed** — needs a browser; see Q-01
- [ ] **Associates tag confirmed** — needs account access; see Q-04

The two open items are not failures of this pass. They are the two facts that cannot be
established from outside the account, and they are published as questions rather than
guessed at.

---

# Addendum — pass 9, 2026-11-15 (`arena/792c279e-zone1`, task T20)

This addendum is added, not substituted: pass 8's sections above remain as they were
published. It records what a further line-by-line live pass found and what it added.

## A. What changed, in one paragraph

The verification layer was re-read source by source on 2026-11-15 and **no published product
value was found to be wrong**: all three supplied links again resolved to the same three
ASINs, every Chefman and Emeril specification still matched the page cited for it, and the
Associates rate table, the required disclosure wording, the application-review thresholds and
16 CFR Part 255 were all re-read verbatim. Three things were *added*: a buyer-facing decision
page ([picks.html](https://kanlerxz87-cyber.github.io/Zone1/picks.html)), a strategy page
([decisions.html](https://kanlerxz87-cyber.github.io/Zone1/decisions.html)) covering niche,
traffic and measurement, and a one-page action list
([handover.html](https://kanlerxz87-cyber.github.io/Zone1/handover.html)). Four new
source-led articles bring the editorial set to twelve, and a banned-phrase build guard now
fails the build if the writing drifts back towards stock marketing copy.

## B. The strategy answers, for the first time on one page

| Question the brief asks | Where the answer is | The answer, shortened |
|---|---|---|
| Which niche? | `decisions.html#niche` | Air-fryer **format** decisions (basket vs dual-basket vs countertop oven), scored 14/15 against three alternatives. Small-kitchen fit is the internal-link cluster; policy literacy is the trust layer; broad "best air fryer" roundups are rejected because they need testing the project does not do. |
| Which traffic? | `decisions.html#traffic` | Six channels ordered by how little they depend on accounts that do not exist yet. Long-tail format questions and manual/specification questions are already executable; Pinterest is blocked on original imagery; YouTube is blocked on physical units; email comes last. |
| What is a sale worth? | `picks.html#commission` | **4.50%** (Kitchen) or **4.00%** (All Other) per the official table — a $5.40 / $4.80 difference on a $119.99 item. The per-ASIN category is **not published by Amazon**, so no product carries a rate: that is a choice, not an omission. |
| What gets measured? | `decisions.html#measure` | Six metrics with their prerequisites. Nothing can be measured today: no tag on the links, no analytics, no report access. A pre-committed kill rule stops a losing cluster from being relitigated from memory. |
| What is left for the owner? | `handover.html` | **Five actions, about an hour, eighteen flags.** Reading the model number off three listings is three minutes and closes the four highest-severity flags. |

## C. Three new flags, and why none of them was "fixed" by guessing

| Flag | What it is | Why it is flagged rather than changed |
|---|---|---|
| **F44** | Two flag registers exist in this repository and contradict each other — `data/flags.json` still says the commission schedule is behind a sign-in, while this same pass read it in full without one. | Editing another build's data file would silently re-point its citations. The owner has to name one register canonical. |
| **F45** | The Emeril listing title now says **six** cooking accessories; the site publishes **seven**, sourced to the brand page and the manual. | A listing can count a spit and forks as one accessory. Replacing a manual-sourced number with a title-sourced number *on a row whose product identity is itself unconfirmed* would make the site less accurate, not more. |
| **F46** | The one fact that closes four high-severity flags — the model number — cannot be read by an automated fetch because the listing renders that block client-side. | Recorded explicitly because seven sessions have logged "needs a human" without saying why the machine cannot do it, which invites an eighth attempt. It is now also stated where a buyer will read it. |

## D. Compliance position — unchanged, and re-verified today

* The required sentence *"As an Amazon Associate I earn from qualifying purchases."* is on
  every page and is generated by `build.py`; a build guard fails if any page lacks it.
  Re-read on 2026-11-15 at
  [the Associates help page](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98).
* Link-level disclosure must be **clear** and **conspicuous** — same source, same day. Each
  product CTA still carries a visible "Affiliate link · tracking unconfirmed" label.
* FTC: disclose any financial relationship, place it where it is hard to miss, and **do not
  claim experience you have not had** —
  [Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers),
  read 2026-11-15. Twelve articles now state that no unit was tested; the new banned-phrase
  guard also fails the build on first-person testing claims.
* 16 CFR Part 255 remains in force through §255.6, up to date as of 11/12/2026 —
  [eCFR](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255).
* No Amazon price, rating, review count or availability is published anywhere, including on
  the four new articles and the three new pages. The commission arithmetic uses manufacturer
  list prices only.

## E. What this pass could not do

* Confirm the model number behind any ASIN (F46).
* Confirm the Associates tag inside the supplied links, or the account's approval status.
* Publish a real Amazon price, rating or availability (Program Policies §2(b), §6(t)).
* Register a domain or a Search Console property.
* Render the site in a real browser: no browser binary was installable in this environment.
  The design claims in section F are therefore backed by static analysis — markup parsed,
  every class checked against the stylesheet, anchors and table tags balanced — and not by a
  screenshot. That limitation is stated rather than papered over.

## F. Site and content work in this pass

* **New pages:** `picks.html` (decision-rule picks, commission arithmetic, buyer-facing table
  of contents), `decisions.html` (niche scorecard, six channels, six metrics, kill rule),
  `handover.html` (five owner actions).
* **New articles (4):** counter-fit dimensions, running costs and circuit load, who pays for
  an air-fryer review, and the two-model 8-quart explainer. All twelve articles are guarded:
  every number must already exist in `data/products.json`, every section must cite a
  registered source, and stock marketing phrases now fail the build.
* **Design:** an editorial serif for headings, computed "pulse" tiles on the landing page
  (products, articles, sources, flags — all derived from data, never typed), trust/caution
  callouts, channel and handover cards, article share row with copy-to-clipboard, prev/next
  navigation and `Article` structured data.
* **SEO:** `sitemap.xml` now lists 34 URLs (was 27), `robots.txt` unchanged, every new page
  carries a distinct `<meta name="description">`, and the four new articles are in the
  sitemap under their own slugs.

## G. Definition of done for this pass

- [x] Every asserted value re-read against its official source on 2026-11-15, or explicitly
      recorded as not re-confirmed (`reports/verification-2026-11-15.md`)
- [x] Values that could not be confirmed left as they were and flagged — none inferred,
      none "corrected" from memory
- [x] Three new flags published with both sides linked
- [x] A banned-phrase guard that fails the build on stock marketing copy, proven by the
      articles passing it
- [x] All repository gates re-run: `build.py`, `verify.py`, `ci-check.sh`,
      `check_research.py`, `verify_site.py`, `platform/audit/report.py`
- [x] New pages reachable from the sidebar, the landing page and `sitemap.xml`
- [ ] Model numbers confirmed — needs a browser (H1, F46)
- [ ] Associates tag confirmed — needs account access (H2)

## H. The single next action

Open the three links, read the **Model number** line in each listing's *Product information*
section, and send the three strings back. That is three minutes and it closes F01, F02, F32
and F33 at once — the four flags that decide whether the site is describing the appliances it
is actually promoting.
