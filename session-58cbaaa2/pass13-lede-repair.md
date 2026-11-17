# pass 13 follow-up — the F82 repair, repaired (2026-11-17, session 58cbaaa2)

**Trigger:** after PR #140 merged (`6c9d313`) and Pages deployed, the live
`categories/kitchen-appliances.html` lede read *"0 of the five links submitted to this project were
observed landing on air fryer or air fryer-oven listings."* Correct answer: three.

**Cause:** `_submitted_links_in_category()` treated `data/product-intent.json`'s
`observed_listing_category` as an Amazon browse path. The consolidation pass stores a prose judgement in
that field — *"Air-fryer product title on observed landing page; intended product unconfirmed"* — and the
classifier tested for `"air fryer"` with a space. Zero rows matched, `n` was 0, the f-string rendered it.

**Why nothing caught it:** `check_submitted_link_count()` matched only spelled-out `one`…`twelve`, so a
literal `0` parsed to `None` and was skipped; the sentence's tail was fixed prose, true only while some
link lands elsewhere.

**Applied in `build.py` (five edits, no data change):**
1. `_register_category_words()` added — returns the register's words as a **list** (a dict keyed by row id
   would silently deduplicate rows).
2. `_submitted_links_in_category()` normalises hyphens and whitespace, and **raises `SystemExit`** when no
   row classifies, quoting the field values it was given. A silent zero is a bug, not a finding.
3. `_submitted_link_clause()` composes the whole lede sentence — number, total **and** tail — so the
   in-category case reads "every link submitted so far resolves inside this category".
4. `check_submitted_link_count()` also matches `N of the M links submitted to this project`, digits or
   words, with `zero`/`no` mapped to 0, and names `_submitted_link_clause()` in the failure text.
5. **F82**'s detail carries the addendum verbatim, including the sentence "deriving a number from a field
   whose meaning was inferred from its name is guessing with extra steps".

**Proven both directions:** the tree builds silently as-is; injecting `Four of the five`, `0 of the five`
and `Zero of the five` into the lede each exits non-zero quoting `three of five` from the register; and
patching `SUBMITTED_ROWS` to wording that classifies nothing aborts the build with the field values named.

Docs updated in the same commit: `README.md` (pass-13 section), `EXECUTIVE-SUMMARY.md` §24.5,
`reports/verification-2026-11-17-58cbaaa2.md` §5b, `COORDINATION.md` X-58cbaaa2 row.
