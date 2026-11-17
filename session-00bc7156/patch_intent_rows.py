"""Fix the page_intent re-read block so it satisfies the site's own row rule.

The gate that failed is not an inconvenience to argue with: on this site every table row must carry a link
to a registered source, to the repository on GitHub, or to the Flagged page. A table of *provenance* is the
worst possible place to break that rule, because provenance is the one thing the row is for. Each row now
names the source ids that recorded it and links the raw fetch log.
"""

P = "build.py"
s = open(P, encoding="utf-8").read()

old_rows = '''        _rows = [
            ("Links followed by this pass", _links),
            ("Not re-read by this pass", _skip + \'<div class="tiny muted">\' + e(reads.get("reread_result", "")) + "</div>"),
            ("<strong>The question the control asks</strong>", e(ctl.get("question", ""))),
            ("How it was run", e(ctl.get("method", ""))),
            ("What came back", e(ctl.get("observed", ""))),
            ("What that implies", e(ctl.get("implication", ""))),
            ("What still justifies the caution", e(ctl.get("what_still_justifies_the_caveat", ""))),
            ("Status", e(ctl.get("status", "")) + \' <a href="flagged.html#f87">F87</a> · \'
             \'<a href="suggestions.html#sg-38">SG-38</a> · <a href="questions.html#q-29">Q-29</a>\'),
        ]
        _body = "".join(f\'<tr><td>{k}</td><td class="small">{v}</td></tr>\' for k, v in _rows)'''
assert s.count(old_rows) == 1, "rows anchor"

new_rows = '''        _blob = ("https://github.com/kanlerxz87-cyber/Zone1/blob/main/"
                 + reads.get("evidence_log", "session-00bc7156/observations-2026-11-17.json"))
        _rows = [
            ("Links followed by this pass", _links, ["S40", "S41"]),
            ("Not re-read by this pass",
             _skip + \'<div class="tiny muted">\' + e(reads.get("reread_result", "")) + "</div>", ["S16", "S17"]),
            ("<strong>The question the control asks</strong>", e(ctl.get("question", "")), []),
            ("How it was run", e(ctl.get("method", "")), []),
            ("What came back", e(ctl.get("observed", "")), ["S16"]),
            ("What that implies", e(ctl.get("implication", "")), []),
            ("What still justifies the caution", e(ctl.get("what_still_justifies_the_caveat", "")), ["S2"]),
            ("Status", e(ctl.get("status", "")) + \' <a href="flagged.html#f87">F87</a> · \'
             \'<a href="suggestions.html#sg-38">SG-38</a> · <a href="questions.html#q-29">Q-29</a>\', []),
        ]
        # Rows with no external document behind them are facts about this repository's own fetch, so
        # they cite the fetch log - which is what makes them checkable at all.
        _log = f\'<a href="{_blob}">raw fetch log</a>\'
        _body = "".join(
            f\'<tr><td>{k}</td><td class="small">{v} {" " + src_links(ids) if ids else " " + _log}</td></tr>\'
            for k, v, ids in _rows
        )'''
s = s.replace(old_rows, new_rows, 1)
open(P, "w", encoding="utf-8").write(s)

import ast

ast.parse(s)
print("rows now carry their sources")
