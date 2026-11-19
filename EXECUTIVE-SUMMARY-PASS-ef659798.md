# Executive summary — shop, findable, publication pass (X-ef659798)

**19 November 2026 (UTC)** · session `arena/ef659798-zone1`
**Canonical publication:** <https://kanlerxz87-cyber.github.io/Zone1/>

## Bottom line

The site already led with products; this pass finished the brief's remaining publication asks
that a repository can honestly finish. The brief's own specification table (S-04…S-25 plus the
Priority 4/5 blocks) is now a register with every row verified line by line against this
repository — 21 rows, each with an official-source link and a status judged here, not copied
from a parallel build. Search engines are now told to index **one** site. The fourth unanswered
buyer question in the brief's editorial hypotheses has a sourced canonical page. Two defects
and one divergence were found and are recorded below.

Nothing here establishes a working affiliate business: intended listings, enrolled-link
attribution, production analytics and measured results remain unconfirmed, exactly as before.

## Delivered

- **Brief spec rows, verified line by line** ([requirements.html](https://kanlerxz87-cyber.github.io/Zone1/requirements.html)):
  S-04…S-25, Priority 4 (evidence-based iteration) and Priority 5 (compliance gate), each
  quoting the brief's clause and recording the repo-judged status. Every row carries an
  official-site evidence link. Where this repository diverges from the brief's tracker
  (S-06, S-23), the divergence is the row's content, not a footnote.
- **Findable — one site to index.** The annex builds are kept out of the index by their own
  `noindex` directives behind one root-authoritative `robots.txt` (F105, the parallel
  findability pass's mechanism, merged and adopted during integration — a robots.txt
  `Disallow` draft from this pass was withdrawn because blocking hides the noindex it would
  stand in for). This pass kept workspace pages crawlable-noindex, extended the boundary's
  enforcement to the legacy `docs/` tree, and pinned the design in tests.
- **S-04 as a gate.** Every page's own title and meta description is now enforced as
  *distinct*, not merely present — the check_seo_metadata guard fails the build on duplicates.
- **One new question-shaped guide:** *How to assess cleanup and counter-space trade-offs* —
  the third of the brief's four editorial hypotheses, which the article set did not answer in
  one place. Sourced to the two Chefman manuals, the Emeril manual and the three product
  pages; no ranking, no timed cleanup, no measured capacity. Filed in the choose cluster,
  tracked as TP-27 with its "working title, not demand claim" provenance. Sitemap 37 URLs,
  feed 25 items, both generated from the same registers as before.
- **S-19 chooser:** compare.html now opens with three situation questions above the
  comparison table, each routing to a documented format page and labelled as not a verdict.
- **Decision records:** SG-44's implementation note records the indexing half; Q-42 records
  the S-23 ratio decision the owner still owes.

## Findings that matter

1. **A register row can exist and still be invisible.** H-01 and H-02 sat in
   `data/requirements.json` while the requirements page silently dropped them — no group
   entry, no table row, no gate. The header tiles counted 53 rows; the tables showed 51.
   Fixed, and the class of defect is now visible in the same place it hid.
2. **The brief's table and this repository disagree on one metric (S-23).** The brief records
   "capacity per centimetre of counter depth" as implemented; this repository prints a
   reasoned refusal — nominal volume over body footprint is not food capacity without the
   dimension order and usable food area, which no official source publishes. Both positions
   stay published (Q-42); the owner decides which this site stands behind.
3. **Four blank cells in the brief's table are now answered** (S-07, S-20, S-25 and the two
   priority blocks) instead of being silently inherited.

## Still gated — unchanged, not re-earned

| Gate | State | Who can move it |
|---|---|---|
| Intended listing per submitted link | Blank by rule; observed targets kept separate | Owner, in an enrolled workflow |
| `shopnow047c-20` | Selected, unvalidated, unapplied | Owner, with account reports |
| Production measurement | Five-event contract tested; collection disabled | Owner + approved same-origin host |
| Campaign ledger | Empty by rule | Authorised first-party reports only |
| Search Console / query data | Not verified (SG-29) | Owner, ten minutes |
| Product photography | Blocked on rights | Owner photographs |

## Verification

All published checks green from this branch: 63 root tests (2 new), 8 Node client tests,
33 platform tests, data audit, research rebuild/check (no drift), s2 `--check` (annex
untouched), link check (11,687 links), verify.py (137 pages, 0 errors, 0 external warnings)
and a deterministic rebuild with zero byte changes. Full record, including the line-by-line
table and the boundaries this pass did not cross:
[`reports/verification-2026-11-19-ef659798.md`](reports/verification-2026-11-19-ef659798.md).
