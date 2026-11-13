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

> **Note for this session:** the Arena agent runtime pins every session to the branch it was
> launched on, and the runner refuses to push to any other branch. This session is therefore
> operating on the Arena-assigned branch `arena/2bef746a-zone1`, which plays the role of
> `session-<id>/<task>` for this session. The branch note and this board are kept in sync so other
> sessions can see live status.

## Session registry

| Session ID | Branch | Status | Notes |
| --- | --- | --- | --- |
| `zone1-main` | `arena/2bef746a-zone1` | **active** | Sole session active in this repo as of 2026-11-13. Holds the research + build + integration scope. |

---

## Task board

| # | Task | Status | Owner session | Files touched | Sources / verification | Irregularities |
| --- | --- | --- | --- | --- | --- | --- |
| T0 | Repo review + coordination setup | **done** | `zone1-main` | `COORDINATION.md`, `README.md` | `git log`, `git branch -a`, `gh api repos/kanlerxz87-cyber/Zone1/pages` | Repo had a single commit (`42f4036 Initial commit`) and only a 1-line `README.md`. GitHub Pages was already configured (`build_type: legacy`, source `main`, path `/`, status `built`). |
| T1 | Resolve the 3 supplied `link.amazon` short links to canonical ASINs | **done** | `zone1-main` | `data/products.json`, `docs/verification-log.md` | Live HTTP redirect resolution via `https://link.amazon/<code>` → final `amazon.com/dp/<ASIN>` URL + official `<title>` on each `/dp/` page | All 3 short links resolve to `/dp/` pages. The short-link *path segment* (e.g. `B04G1MEwY`) is **not** the product ASIN — it is an opaque redirect token. Flagged as an irregularity (F-01). |
| T2 | Verify Product 1 — CHEFMAN 6 Qt Dual Basket (B0CDY277D3) | **done** | `zone1-main` | `data/products.json` | `https://www.amazon.com/dp/B0CDY277D3` | see F-02 (variant/price volatility), F-06 (capacity unit) |
| T3 | Verify Product 2 — Emeril Lagasse 26QT French Door (B09B7SB46R) | **in progress** | `zone1-main` | `data/products.json` | `https://www.amazon.com/dp/B09B7SB46R` | Amazon is serving a reduced page for this ASIN — see F-03 |
| T4 | Verify Product 3 — Chefman 8 Qt TurboFry 4-in-1 (B08DKYBTPH) | **done** | `zone1-main` | `data/products.json` | `https://www.amazon.com/dp/B08DKYBTPH` | — |
| T5 | Verify Amazon Associates program terms (commission, disclosure, prohibited uses) | unclaimed | — | `data/program.json`, `docs/verification-log.md` | — | — |
| T6 | Verify FTC / endorsement disclosure requirements | unclaimed | — | `data/program.json` | — | — |
| T7 | Build static GitHub Pages site (landing + category subpages + tables + analysis) | unclaimed | — | `index.html`, `assets/*`, `pages/*` | — | — |
| T8 | Executive summary page | unclaimed | — | `pages/executive-summary.html` | — | — |
| T9 | Marketing content pack (SEO article, comparison, buying guide) | unclaimed | — | `pages/marketing/*` | — | — |
| T10 | Campaign / tracking / optimization plan | unclaimed | — | `pages/campaign.html` | — | — |
| T11 | Sources & Verification Log page | unclaimed | — | `pages/sources.html`, `docs/verification-log.md` | — | — |
| T12 | Flagged for Review page | unclaimed | — | `pages/flagged.html`, `data/flags.json` | — | — |
| T13 | Integration: re-verify combined data, check for broken links, build check | unclaimed | — | all | — | — |
| T14 | PR to `main`, merge, confirm GitHub Pages deploy | unclaimed | — | — | — | — |

---

## Irregularity log (published on `pages/flagged.html`)

| ID | Item | Detail | Source of truth | Status |
| --- | --- | --- | --- | --- |
| F-01 | `link.amazon` short-link tokens are not ASINs | The three supplied URLs contain path segments that look like ASINs (`B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`) but resolve to different, unrelated ASINs (`B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`). The segment is an opaque redirect token. Anyone rebuilding links from the ASIN-looking segment would link to the wrong product. | `https://link.amazon/<code>` redirect target | needs review |
| F-02 | Product 1 buy-box price is volatile | Two different new-condition prices were served for B0CDY277D3 in the same fetch window: **$79.93 (−20% of $99.99 list)** and **$57.45 (−43% of $99.99 list)**, plus a used offer at $57.45. Both are recorded; the page must be re-checked before publishing any price claim. | `https://www.amazon.com/dp/B0CDY277D3` | needs review |
| F-06 | `capacity` unit on Product 1 is rendered as "6 liters" | Amazon's `productDetails` block lists Capacity = `6 liters` while the title, bullets and images say 6-quart. Both are recorded verbatim; the quart figure is used in prose because it is what the manufacturer states on the page. | `https://www.amazon.com/dp/B0CDY277D3` | needs review |
| F-03 | Product 2 detail page served in reduced form | `amazon.com/dp/B09B7SB46R` intermittently returns only navigation/footer markup with no buy box, price, rating or feature bullets. Title + category were confirmed from the page `<title>`; price/rating/reviews could not be read from the page body at fetch time. Those fields are left **blank** and flagged, per the verification rule. | `https://www.amazon.com/dp/B09B7SB46R` | needs review |
| F-04 | Amazon Associates rate card is login-gated | Per-product commission rates are only visible to a signed-in publisher inside the Associates dashboard. No public official page publishes a flat "Home & Kitchen air fryer" rate, so no numeric commission rate is stated as fact anywhere on the site. | `https://affiliate-program.amazon.com/help/operating/agreement` | needs review |
| F-05 | Live pricing & BSR are point-in-time | Prices, discount badges, "bought in past month" counts and Best Sellers Rank change continuously. All such fields are stamped with the verification date and must be re-verified before any campaign launch. | `https://www.amazon.com/dp/<ASIN>` | needs review |

---

## Change log

- **2026-11-13** — `zone1-main` created this board and claimed T0–T14 (sole active session; no
  other session had registered claims at the time of writing). Repo reviewed: see T0.
- **2026-11-13** — `zone1-main` resolved all 3 `link.amazon` links to canonical ASINs and verified
  Product 1 and Product 3 from their official `amazon.com/dp/` pages (T1, T2, T4).
