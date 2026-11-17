import re
from pathlib import Path

f = Path('/home/user/Zone1/session-58cbaaa2/apply_pass13.py')
t = f.read_text()
subs = []

# (a) scope the link-count guard to pages where the count is a present-tense claim
subs.append((
"""    words = {v: k for k, v in _LINK_NUM_WORDS.items() if k}""",
"""    # Scope: the pages where a link count is a claim about right now — the shopper surfaces
    # plus the two registers this pass built. A dated verification row that says "all three
    # supplied links" is a true statement about 2026-11-14, and editing history to satisfy a
    # check would destroy the evidence, so dated registers stay outside this guard on purpose.
    PRESENT_TENSE_PAGES = {"index.html", "links.html", "measurement.html", "compare.html",
                           "picks.html", "compliance.html", "categories", "products", "guides"}
    words = {v: k for k, v in _LINK_NUM_WORDS.items() if k}""",
))
subs.append((
"""    for rel, html_text in PAGES_CACHE.items():
        plain = re.sub(r"<[^>]+>", " ", html_text)
        for m in pat.finditer(plain):""",
"""    for rel, html_text in PAGES_CACHE.items():
        if rel.split("/")[0] not in PRESENT_TENSE_PAGES:
            continue
        plain = re.sub(r"<[^>]+>", " ", html_text)
        for m in pat.finditer(plain):""",
))

# (b) drop the dead ternary left in rows()
subs.append((
"""            cells = [
                f'<td class="small">{e(r["submitted_link"])}</td>' if False else
                f'<td class="small"><a href=""",
"""            cells = [
                f'<td class="small"><a href=""",
))

# (c) every row of the format table must carry a source pointer (check_row_sources)
subs.append((
"""      f'<td class="small"><a href="questions.html#q-28">Q-28</a> · <a href="suggestions.html#sg-37">SG-37</a></td></tr>'""",
"""      f'<td class="small"><a href="flagged.html#f78">F78</a> · <a href="questions.html#q-28">Q-28</a> · '
      f'<a href="suggestions.html#sg-37">SG-37</a></td></tr>'""",
))

# (d) same for the ledger column-definition rows
subs.append((
"""            f'<td class="small">{flag_pill("unverified") if not (ledger.get("rows") or []) else flag_pill("verified")}</td></tr>'""",
"""            f'<td class="small">{flag_pill("unverified") if not (ledger.get("rows") or []) else flag_pill("verified")}'
            f'<div class="tiny muted"><a href="flagged.html#f79">F79</a> — why it is empty</div></td></tr>'""",
))

for old, new in subs:
    n = t.count(old)
    if n != 1:
        raise SystemExit(f"anchor matched {n} times: {old[:70]!r}")
    t = t.replace(old, new, 1)

f.write_text(t)
print("apply_pass13.py updated (4 groups)")
