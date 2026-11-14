## Record-only follow-up to PR #36

PR #36 could not contain its own merge result, so this record is published by a follow-up, exactly as
`arena/6ecdb4e4` did for I8.

### PR #36 — merged

* **PR:** https://github.com/kanlerxz87-cyber/Zone1/pull/36 — "Integration pass 6 (sess-91d0552e): live
  re-verification, flag-register collision F28, exec-summary count corrections".
* **Checks on head `00df880`:** `CI` pass · `Verify verification annex (site/)` pass (both jobs:
  `verify` and `Rebuild site/ from data/verified and assert every guarantee`).
* **Merged:** 2026-11-14T18:54:06Z without waiting for approval, per the brief.
  **Merge commit on `main`: `fa417c9f0725707d240435e25441c8bf7f112298`.**
* **Post-merge workflows on `main`, all green:** `CI` · `Verify verification annex (site/)` ·
  `Build, verify and deploy to GitHub Pages` · `pages build and deployment`.
* **GitHub Pages:** status `built`, latest build commit `fa417c9`, `error: null`.
* **Live check:** `flagged.html` serves **28 open items** including **F28** with both source links;
  `executive-summary.html` serves **28 open flag rows**, 24 sources, 0 verified product identities,
  0 numbers invented; the OA section 5 disclosure bar is on every page.
* **Deploy-cache note:** the first fetch after the merge returned the previous deploy (27 items) from
  the Pages CDN; a later fetch returned the new copy. Re-fetch before concluding a deploy is wrong.

### Content of PR #36 (summary)

1. `session-91d0552e/VERIFICATION-2026-11-14.md` — independent live re-verification of the three
   `link.amazon` tokens (5th observation round), the Operating Agreement page version, the Standard
   Commission Income Statement (**11/11 rate rows, read without any login**) and all three brand
   product pages. **No stored value was found to be wrong.**
2. Flag **F28** — three flag registers share overlapping ID spaces but index different issues, and two
   published documents cite the wrong one. Renumbered from F25 during the rebase because
   `arena/6ecdb4e4` (I7) had already published a different finding as F25.
3. `EXECUTIVE-SUMMARY.md` — stale counts corrected (42 verified / 1 blank spec rows; 28 open flag rows;
   92 pages), merged with `arena/6ecdb4e4`'s independent correction of the same line.
4. `EXECUTIVE_SUMMARY.md` — additive reconciliation banner for the two competing executive summaries at
   the repo root. No other session's text was deleted.
5. Rebase conflict resolutions against PR #34 and PR #37, both recorded in `COORDINATION.md`.
