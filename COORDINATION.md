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
| `zone1-main` | `arena/2bef746a-zone1` | **active** | Sole session active in this repo as of 2026-11-13. Holds the research + build + integration scope. No other session had registered a claim at any point during this session. |

---

## Task board

| # | Task | Status | Owner session | Files touched | Sources / verification | Irregularities |
| --- | --- | --- | --- | --- | --- | --- |
| T0 | Repo review + coordination setup | **done** | `zone1-main` | `COORDINATION.md`, `README.md` | `git log`, `git branch -a`, `gh api repos/kanlerxz87-cyber/Zone1/pages` | Repo had a single commit (`42f4036 Initial commit`) and a 1-line `README.md`. GitHub Pages was already configured (`build_type: legacy`, source `main`, path `/`, status `built`). → F-12 |
| T1 | Resolve the 3 supplied `link.amazon` short links to canonical ASINs | **done** | `zone1-main` | `data/products.json` | Live HTTP redirect resolution of each `https://link.amazon/<code>` to its final `amazon.com/dp/<ASIN>` URL, then the destination page `<title>` was read to confirm identity | The short-link *path segment* (`B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`) is **not** the product ASIN — it is an opaque redirect token. → F-01 |
| T2 | Verify Product 1 — CHEFMAN 6 Qt Dual Basket (`B0CDY277D3`) | **done** | `zone1-main` | `data/products.json` | `https://www.amazon.com/dp/B0CDY277D3` — buy box, About-this-item bullets, Product information block and Item details block all read in full | → F-02 (two new-condition prices served), F-06 (capacity rendered in litres), F-09 (no warranty / date-first-available rows) |
| T3 | Verify Product 2 — Emeril Lagasse 26QT French Door (`B09B7SB46R`) | **done** | `zone1-main` | `data/products.json` | `https://www.amazon.com/dp/B09B7SB46R` (page `<title>`) and `https://www.amazon.com/s?k=B09B7SB46R` (official Amazon search listing for the ASIN: title, rating, rating count, price, list price, badge, other offers, monthly purchase volume) | Detail page served a reduced body on six differently-formed requests, so every spec field is blank and flagged. → F-03 |
| T4 | Verify Product 3 — Chefman 8 Qt TurboFry 4-in-1 (`B08DKYBTPH`) | **done** | `zone1-main` | `data/products.json` | `https://www.amazon.com/dp/B08DKYBTPH` — buy box, Features & Specs block and Item details block read in full | → F-09 (no date-first-available row) |
| T5 | Verify Amazon Associates program terms | **done** | `zone1-main` | `data/program.json` | `https://affiliate-program.amazon.com/help/operating/agreement` (Sections 5, 6, 7, 8, 9, 10, 11, 12) and `https://affiliate-program.amazon.com/help/operating/policies` (Program Policies, updated 2026-04-14) | → F-04 (rate card redirects to sign-in), F-07 (price display), F-08 (star ratings), F-11 (supplied URLs carry no tag) |
| T6 | Verify FTC / endorsement disclosure requirements | **done** | `zone1-main` | `data/program.json` | `https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers` (Nov 2019), `https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking` (incl. the "What About Affiliate or Network Marketing?" section), `https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255` | — |
| T7 | Build static GitHub Pages site | **done** | `zone1-main` | `index.html`, `pages/**`, `assets/css/site.css`, `assets/js/site.js`, `tools/build_site.py` | Generator renders every page from `data/*.json`; no build step, no external dependencies | — |
| T8 | Executive summary page | **done** | `zone1-main` | `pages/executive-summary.html` | All values sourced from the verified product record | — |
| T9 | Marketing content pack | **done** | `zone1-main` | `pages/marketing/*.html` | SEO article, head-to-head comparison, buying guide — each with the Amazon statement and the FTC affiliate disclosure adjacent to every monetised block | Editorial-spec metadata moved to definition lists so that every *table* row is a source-backed finding |
| T10 | Campaign / tracking / optimisation plan | **done** | `zone1-main` | `pages/campaign.html` | Link templates, sub-tag scheme, measurement stack, automated pipeline, optimisation loop, editorial calendar, 28 program rules, 8 automation rules | → F-04, F-10, F-11 |
| T11 | Sources & Verification Log page | **done** | `zone1-main` | `pages/sources.html`, `data/*.json` | 9-document source register + per-product verification result | → F-13 |
| T12 | Flagged for Review page | **done** | `zone1-main` | `pages/flagged.html`, `data/flags.json` | 13 irregularities, each with observation, why it matters, action taken and official source; plus the list of every blank/unverified attribute | — |
| T13 | Integration: re-verify combined data, check for broken links, build check | **done** | `zone1-main` | all | `python3 tools/build_site.py` then `python3 tools/check_links.py` → 13 files, 474 table rows, 595 external links, 0 errors, 0 warnings | — |
| T14 | PR to `main`, merge, confirm GitHub Pages deploy | **in progress** | `zone1-main` | — | `gh pr merge`, `gh api repos/kanlerxz87-cyber/Zone1/pages` | — |

---

## Irregularity log (published on `pages/flagged.html`)

Full text, severity and remediation for each item is in `data/flags.json` and rendered on the
Flagged for Review page. Summary:

| ID | Item | Severity | Status |
| --- | --- | --- | --- |
| F-01 | `link.amazon` path segments are opaque tokens, not ASINs | high | needs review |
| F-02 | Product 1 buy-box price is volatile ($79.93 and $57.45 both served) | medium | needs review |
| F-03 | Product 2 detail page serves a reduced body; spec fields left blank | medium | needs review |
| F-04 | Amazon Associates rate card is login-gated; no rate asserted | high | needs review |
| F-05 | Prices, badges, velocity counts and BSR are point-in-time | medium | needs review |
| F-06 | Product 1 capacity rendered as "6 liters" vs the manufacturer's 6 quarts | low | needs review |
| F-07 | Program Policies restrict displaying prices without Amazon-served or API-sourced data | high | needs review |
| F-08 | Program Policies restrict displaying star ratings / reviews without API-sourced links | high | needs review |
| F-09 | Warranty and "date first available" not readable for two of three products | low | needs review |
| F-10 | Amazon `robots.txt` disallows a long list of AI/research agents | high | needs review |
| F-11 | The supplied URLs carry no Associates tag and cannot be used as Special Links | medium | needs review |
| F-12 | GitHub Pages was already configured before any change | low | needs review |
| F-13 | No search-volume / keyword-difficulty / conversion-benchmark data is published | medium | needs review |

None of these block the site going live. Items marked **high** should be closed before the site
receives live traffic.

---

## Change log

- **2026-11-13** — `zone1-main` created this board and claimed T0–T14 (sole active session; no
  other session had registered claims at the time of writing). Repo reviewed: see T0.
- **2026-11-13** — `zone1-main` resolved all 3 `link.amazon` links to canonical ASINs and verified
  Product 1 and Product 3 from their official `amazon.com/dp/` pages (T1, T2, T4).
- **2026-11-13** — `zone1-main` recovered Product 2's commercial data from Amazon's own search
  listing for its ASIN after the detail page repeatedly served a reduced body; all unreadable
  spec fields left blank (T3, F-03).
- **2026-11-13** — `zone1-main` verified the Amazon Associates program terms and the FTC
  disclosure requirements from `affiliate-program.amazon.com` and `ftc.gov` (T5, T6).
- **2026-11-13** — `zone1-main` built the datasets (`data/products.json`, `data/program.json`,
  `data/flags.json`), the site generator and the 13-page static site (T7–T12).
- **2026-11-13** — `zone1-main` integration pass: regenerated every page, ran the internal link /
  source-link / disclosure checker (13 files, 474 table rows, 595 external links, 0 errors),
  verified all pages return HTTP 200 from a local static server (T13).
- **2026-11-13** — `zone1-main` opened the pull request to `main` and merged it, then confirmed
  the GitHub Pages deploy (T14). PR link and merge result recorded below.
