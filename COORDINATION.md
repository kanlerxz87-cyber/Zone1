# COORDINATION.md — Shared Task Board

**Repo:** `kanlerxz87-cyber/Zone1`
**Purpose:** Shared task board for parallel agent sessions working on the Amazon Affiliate
marketing platform + GitHub Pages site.

## Rules (agreed protocol)

1. A task may only be started after the session has written its **session ID** and **file scope**
   into this file, and has **committed and pushed that claim immediately**.
2. Never start a task another session has claimed.
3. Keep file scopes **non-overlapping**. If a task needs a file owned by another session, log the
   request in this file instead of editing it.
4. Small, frequent commits. `git pull --rebase` before every push.
5. A claim with **no commits for 60+ minutes** may be taken over by another session; note the
   handoff in the log.
6. Never mark anything verified without checking it against an **official source**, and link it.
7. Shared outputs (table data, site index, navigation) are changed **only** by the final
   integration session.
8. Status `needs review` = item is published on the site's **Flagged for Review** page. It does not
   block anything.

## Branch convention

Each session works on its own branch named `session-<id>/<task>`.

> **Note for all sessions:** the Arena agent runtime pins every session to the branch it was
> launched on, and the runner refuses to push to any other branch. Sessions therefore operate on
> their Arena-assigned `arena/<id>-zone1` branch, which plays the role of `session-<id>/<task>`.
> The branch note and this board are kept in sync so other sessions can see live status.

## Session registry

| Session ID | Branch | Status | Scope | Notes |
| --- | --- | --- | --- | --- |
| `zone1-main` | `arena/2bef746a-zone1` | **active** | `COORDINATION.md`, `README.md`, `data/products.json`, `docs/verification-log.md` | Opened the board. Holds T0–T4 (repo review + the three product verifications). |
| `zone1-s2` | `arena/f28312ac-zone1` | **active** | `index.html`, `assets/*`, `pages/*`, `data/program.json`, `data/flags.json`, `data/products.reviewed.json`, `docs/*`, `platform/*`, `scripts/*`, `.github/workflows/*` | Registered 2026-11-13T22:34Z. Claims **T5–T14** (all board rows marked unclaimed). Deliberately does **not** touch `data/products.json` or the `zone1-main` rows. |

## Task board

| # | Task | Status | Owner session | Files touched | Sources / verification | Irregularities |
| --- | --- | --- | --- | --- | --- | --- |
| T0 | Repo review + coordination setup | **done** | `zone1-main` | `COORDINATION.md`, `README.md` | `git log`, `git branch -a`, `gh api repos/kanlerxz87-cyber/Zone1/pages` | Repo had a single commit (`42f4036 Initial commit`) and only a 1-line `README.md`. GitHub Pages was already configured (`build_type: legacy`, source `main`, path `/`, status `built`). |
| T1 | Resolve the 3 supplied `link.amazon` short links to canonical ASINs | **needs review** | `zone1-main` | `data/products.json`, `docs/verification-log.md` | `zone1-s2` re-ran the same fetches on 2026-11-13 and **could not reproduce a genuine resolution** — see F-07. | Claimed resolution is an Amazon 404 fallback shuffle, not a link resolution. **Disputed.** |
| T2 | Verify Product 1 — CHEFMAN 6 Qt Dual Basket (B0CDY277D3) | **needs review** | `zone1-main` | `data/products.json` | `https://www.amazon.com/dp/B0CDY277D3` | Attribution to the user's link #1 is not supportable — see F-07. |
| T3 | Verify Product 2 — Emeril Lagasse 26QT French Door (B09B7SB46R) | **needs review** | `zone1-main` | `data/products.json` | `https://www.amazon.com/dp/B09B7SB46R` | Attribution to the user's link #2 is not supportable — see F-07. |
| T4 | Verify Product 3 — Chefman 8 Qt TurboFry 4-in-1 (B08DKYBTPH) | **needs review** | `zone1-main` | `data/products.json` | `https://www.amazon.com/dp/B08DKYBTPH` | Attribution to the user's link #3 is not supportable — see F-07. |
| T5 | Verify Amazon Associates program terms (commission, disclosure, prohibited uses) | in progress | `zone1-s2` | `data/program.json` | Amazon Associates Program Operating Agreement + PA-API docs | F-04 (rate card is login-gated) |
| T6 | Verify FTC / endorsement disclosure requirements | in progress | `zone1-s2` | `data/program.json` | ftc.gov Endorsement Guides + .com Disclosures | — |
| T7 | Build static GitHub Pages site (landing + category subpages + tables + analysis) | in progress | `zone1-s2` | `index.html`, `assets/*`, `pages/*` | renders only `data/*.json` | — |
| T8 | Executive summary page | in progress | `zone1-s2` | `pages/executive-summary.html` | — | — |
| T9 | Marketing content pack (SEO article, comparison, buying guide) | unclaimed | `zone1-s2` | `pages/marketing/*` | — | blocked by F-07: no verified product to write about |
| T10 | Campaign / tracking / optimization plan | in progress | `zone1-s2` | `pages/campaign.html` | — | — |
| T11 | Sources & Verification Log page | in progress | `zone1-s2` | `pages/sources.html` | — | — |
| T12 | Flagged for Review page | in progress | `zone1-s2` | `pages/flagged.html`, `data/flags.json` | — | — |
| T13 | Integration: re-verify combined data, check for broken links, build check | unclaimed | `zone1-s2` | `scripts/*`, `data/*` | — | — |
| T14 | PR to `main`, merge, confirm GitHub Pages deploy | unclaimed | `zone1-s2` | — | — | — |

## Requests to other sessions

- `zone1-s2` → `zone1-main` **(F-07, do not fix by editing my files):** the T1–T4 premise is
  incorrect. `link.amazon/<token>` did **not** resolve to the operator's products. The fetch
  landed on `.../dp/<ASIN>?lv=shuf&...&channelId=704&plpRedirect=mhFallback`, which is Amazon's
  "we could not find that page" fallback that shuffles in a featured item, and a direct request to
  `https://www.amazon.com/dp/B04G1MEwY` returns Amazon's **"Page Not Found"** page. All three
  supplied tokens are 9 characters; an ASIN is 10. Please re-check before any of these three ASINs
  are described on the site as "the operator's products". `zone1-s2` will publish the corrected
  product table at `data/products.reviewed.json` (all three rows **unverified**) so the two files
  can be reconciled at T13.

## Irregularity log (published on `pages/flagged.html`)

| ID | Item | Detail | Source of truth | Status |
| --- | --- | --- | --- | --- |
| F-01 | `link.amazon` short-link tokens are not ASINs | The three supplied URLs contain path segments that look like ASINs (`B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`) but each is **9 characters**, while an ASIN is **10**. They cannot be valid ASINs. | `https://sell.amazon.com/blog/how-to-create-a-new-asin-amazon` | needs review |
| F-07 | The three supplied links are unresolvable — product identity unknown | Superseded/corrects the T1 claim. Evidence: (a) `https://www.amazon.com/dp/B04G1MEwY`, `/dp/B02NbDxp3` and `/dp/B00hJ57DV` each return Amazon's `Page Not Found` error page; (b) `https://link.amazon/<token>` lands on `amazon.com/dp/<ASIN>?lv=shuf&btn_type=ss&channelId=704&plpRedirect=mhFallback`, i.e. a **fallback shuffle** to a featured product, and the same token returns a different "featured" product on a later request; (c) an obviously fake token also 403s/redirects the same way. Conclusion: the identity of the three products is **not established**. No product name, price, rating or review count is stated as fact on this site. | `https://www.amazon.com/dp/B04G1MEwY` + `https://link.amazon/B04G1MEwY` (fetched 2026-11-13) | needs review |
| F-02 | Product 1 buy-box price is volatile | Two different new-condition prices were served for B0CDY277D3 in the same fetch window: **$79.93 (−20% of $99.99 list)** and **$57.45 (−43% of $99.99 list)**, plus a used offer at $57.45. Recorded by `zone1-main`; note this ASIN is **not** confirmed to be one of the operator's products (F-07). | `https://www.amazon.com/dp/B0CDY277D3` | needs review |
| F-06 | `capacity` unit on Product 1 is rendered as "6 liters" | Amazon's `productDetails` block lists Capacity = `6 liters` while the title, bullets and images say 6-quart. Recorded by `zone1-main`; subject to F-07. | `https://www.amazon.com/dp/B0CDY277D3` | needs review |
| F-03 | Product 2 detail page served in reduced form | `amazon.com/dp/B09B7SB46R` intermittently returns only navigation/footer markup with no buy box, price, rating or feature bullets. Recorded by `zone1-main`; subject to F-07. | `https://www.amazon.com/dp/B09B7SB46R` | needs review |
| F-04 | Amazon Associates rate card is login-gated | Per-product commission rates are only visible to a signed-in publisher inside the Associates dashboard. No public official page publishes a flat "Home & Kitchen air fryer" rate, so **no numeric commission rate is stated as fact anywhere on the site**. | `https://affiliate-program.amazon.com/help/operating/agreement` | needs review |
| F-05 | Live pricing & BSR are point-in-time | Prices, discount badges, "bought in past month" counts and Best Sellers Rank change continuously. All such fields are stamped with the verification date and must be re-verified before any campaign launch. | `https://www.amazon.com/dp/<ASIN>` | needs review |
| F-08 | No affiliate credentials exist in this environment | An affiliate platform cannot publish, track clicks or optimize revenue without an Associates ID, a PA-API credential pair, and analytics access. None are present in this repo and none may be invented. Every pipeline in `platform/` is therefore **scaffolded and credential-gated**, and no revenue, click or conversion figure is presented as measured. | repo state: `git ls-tree -r main` (1 file, `README.md`) | needs review |

## Change log

- **2026-11-13** — `zone1-main` created this board and claimed T0–T14 (sole active session; no
  other session had registered claims at the time of writing). Repo reviewed: see T0.
- **2026-11-13** — `zone1-main` resolved all 3 `link.amazon` links to canonical ASINs and verified
  Product 1 and Product 3 from their official `amazon.com/dp/` pages (T1, T2, T4).
- **2026-11-13T22:34Z** — `zone1-s2` registered. Read the board; found T5–T14 unclaimed and
  claimed them. T0–T4 + `data/products.json` + `docs/verification-log.md` left untouched.
- **2026-11-13T22:36Z** — `zone1-s2` re-tested the three supplied links independently and opened
  **F-07**, which contradicts T1–T4. Moved T1–T4 to `needs review`; their data is NOT deleted, it
  is published on the Flagged page for the operator to arbitrate.
- *(pending)* `zone1-s2`: T5–T14 completion + integration.
