# session-58cbaaa2 — pass 13 working scripts (2026-11-17)

One-shot patch scripts, kept as evidence of how the merged edits were produced. **They have already
been applied and are not idempotent** — each anchors on an exact string in the file it edits and
aborts if that string does not match exactly once, so re-running them after the merge is a no-op
that exits non-zero, which is the intended behaviour rather than a bug.

| File | What it did |
|---|---|
| `apply_pass13.py` | The `build.py` patch: 21 anchored edits (module constants read from `data/product-intent-confirmations.json` and `data/measurement.json`, nav and sidebar entries, the footer disclosure and §3(e) privacy paragraph, the landing-page status note and product CTAs, F76–F80 programme flags with evidence paths, `page_links()` and `page_measurement()`, the local click counter in the emitted `assets/app.js`, the `.comparebar`/tap-target CSS, three new build guards and four new `req_counts()` tokens). Aborts without writing if any anchor is ambiguous. |
| `apply_pass13_registers.py` | The register updates: SG-36…SG-40 and path P6 in `data/suggestions.json`, Q-27…Q-31 in `data/questions.json`, TP-21/TP-22 in `data/topics.json`, requirements H-01…H-04 in `data/requirements.json`, and the two stale-count sentences in `data/decision.json`. |
| `apply_pass13_s39.py` | Recorded the two help nodes found while re-reading S6 — including the correction (S39: a landing URL without a visible `tag=` is a null observation, not evidence of failed attribution) — in the intent register, Q-28, SG-37, H-02 and the measurement register. Dated and additive; no historical row rewritten. |
| `patch_patch.py` | Post-edit pass over `apply_pass13.py` before it was run: scoped `check_submitted_link_count()` to the present-tense surfaces so it could not force an edit of dated history, removed a dead ternary the first draft had left in `page_links().rows()`, and gave two new tables the source pointers `check_row_sources()` requires. A first attempt at the same job done as a shell here-doc failed with a `SyntaxError` on nested quotes; this file is the repaired version, and the defect class is logged in the pass report. |

Nothing here is published. The published evidence record is
[`../reports/verification-2026-11-17-58cbaaa2.md`](../reports/verification-2026-11-17-58cbaaa2.md).
