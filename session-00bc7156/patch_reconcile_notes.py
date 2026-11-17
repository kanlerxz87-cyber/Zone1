"""Pass 13 post-merge reconciliation notes (2026-11-17).

`main` moved twice while this branch was open: #132 (session 5b17c077) landed the tracking-ID gate, the
canonical `data/product-intent.json` + `product-intent.html`, and flags F76–F82; #134 (session 4618f77b)
landed a disposition record. This pass rebased onto that and reconciled rather than re-asserting:
the sources merged by id, the ledger append was moved off the file F80 had retired, and the cluster's
reader link was aligned to the policy #132 adopted. These edits put those decisions in the prose record.
"""

RPT = "reports/verification-2026-11-17-00bc7156.md"
EXEC = "EXECUTIVE-SUMMARY.md"

r = open(RPT, encoding="utf-8").read()

a = """**The finding is not the ASINs, it is the category.** Links 4 and 5 are meat thermometers. They share a
browse path with the air fryers (`Home & Kitchen › Kitchen & Dining`) and nothing else. A five-product
brief was being served by a three-product site, and no pass noticed because every pass asked "do the
recorded links still match?" rather than "are these all the links?"."""
assert a in r
r = r.replace(a, a + """

**Three sessions reached that discovery on the same day, and `main` merged two of them first.** #132
(session `5b17c077`) registered the same two destinations as `PI-04`/`PI-05` in a new canonical
`data/product-intent.json`, published them as `product-intent.html`, and opened flags F76–F82 — including
F81, which states the five-versus-three gap. So this pass renumbered nothing it did not have to: its six
sources became four (`S36`/`S37` already existed for the same two listing URLs, and their metadata is
main's with this pass's read caveat appended), its flags start at F83, and the two rows it found stale are
named in F83 rather than rewritten in someone else's voice.""", 1)

b = """`python3 build.py` → 53 pages built, 52 sitemap URLs (404 excluded), feed 23 items, all guards green (including the new
`check_adjacent_rows`), rebuild byte-identical · `python3 verify.py` → **131 pages, 77 spec rows
(75 verified, 2 blank+flagged), 41 sources, 0 errors, 0 external warnings** · `bash scripts/ci-check.sh` →
33 unit tests OK, data audit clean, **8,958 links, 0 broken**"""
if b not in r:
    import re
    m = re.search(r"`python3 build\.py` → .*?0 broken\*\*", r, re.S)
    assert m
    b = m.group(0)
r = r.replace(b, """`python3 build.py` → 55 pages built, **54 sitemap URLs**, feed 23 items, all guards green (including the new
`check_adjacent_rows` and #132's `check_associate_tagging`), rebuild byte-identical · `python3 verify.py` →
**133 pages, 77 spec rows (75 verified, 2 blank+flagged), 41 sources, 0 errors, 0 external warnings** ·
`bash scripts/ci-check.sh` → 33 unit tests OK, data audit clean, **9,239 links, 0 broken**""", 1)

c = """## 5. Conflicts published rather than resolved"""
assert c in r
r = r.replace(c, """## 4b. Two conventions main had already adopted, adopted here too

* **Reader links.** #132 set the policy that this site sends readers to the tagged `/dp/<ASIN>?tag=…`
  listing rather than through the supplied `link.amazon` short links. The cluster page follows it: each card
  carries one tagged, `rel="sponsored"` button, and the submitted token is printed as `<code>` evidence with
  its source badges. One nuance recorded rather than swallowed: #132's stated reason is that a tag "cannot
  travel" through a `link.amazon` redirect, which is plausible from §2(b)'s wording but is not a fact
  anyone here tested. The cluster does not depend on the answer either way — the tagged listing is the better
  path regardless — but the register should not adopt an untested mechanism as established. If someone wants
  it settled, it is a two-minute test of `link.amazon/<token>?tag=<id>` in a browser, and it belongs on
  `measurement.html`'s open list rather than in prose.
* **Orphan data.** The rule this repository enforces hardest — appended data must be reachable from a
  generated page or the build fails — was turned on this pass's own record: the control test is rendered as a
  table on `product-intent.html`, where the redirect observations live, with each row citing the source ids
  or the raw fetch log that produced it.

## 5. Conflicts published rather than resolved""", 1)
open(RPT, "w", encoding="utf-8").write(r)

t = open(EXEC, encoding="utf-8").read()
d = """**State at the end of this pass:** `build.py` exit 0 (53 pages built, 52 sitemap URLs, feed 23 items,
every guard green including the new one, rebuild byte-identical) · `verify.py` **131 pages, 41 sources,
0 errors, 0 external warnings** · `ci-check.sh` 33 tests OK, audit clean, **8,958 links, 0 broken** ·"""
if d not in t:
    import re
    m = re.search(r"\*\*State at the end of this pass:\*\* `build\.py` exit 0 .*?0 broken\*\* ·", t, re.S)
    assert m
    d = m.group(0)
t = t.replace(d, """**Rebased onto a moving `main` twice in one pass.** #132 landed the tracking-ID gate, the canonical
`data/product-intent.json` and flags F76–F82 while this branch was open, including F80's retirement of the
ledger this pass had first appended to. The reconciliation: six intended new sources became four (main's
`S36`/`S37` already covered the same two listing URLs, so this pass's read caveat was appended to main's
records instead of replacing them), flag ids stayed at F83+, the retired file was restored to main's state
and the observations moved to the canonical record, and the cluster's reader link was switched to main's
tagged-`/dp/` policy with the submitted short link shown as `<code>` evidence. The control test is rendered
on `product-intent.html` rather than left as an orphan block.

**State at the end of this pass:** `build.py` exit 0 (55 pages built, 54 sitemap URLs, feed 23 items, every
guard green including the new one plus #132's tag gate, rebuild byte-identical) · `verify.py` **133 pages,
41 sources, 0 errors, 0 external warnings** · `ci-check.sh` 33 tests OK, audit clean, **9,239 links,
0 broken** ·""", 1)
open(EXEC, "w", encoding="utf-8").write(t)
print("prose reconciled")
