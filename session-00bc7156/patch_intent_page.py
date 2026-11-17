"""One-shot patch script for pass 13 (arena/00bc7156).

Extends build.py's page_intent() so the 2026-11-17 re-read block and the control test recorded in
data/product-intent.json are actually rendered — the repository's rule is that appended data must be
reachable from a page or it is orphaned, which is the defect F44/F45/F46/F57 exist to catch.
Also refines one clause of flag F83 so it does not overstate what it changed on a parallel pass's row.
"""

P = "build.py"
s = open(P, encoding="utf-8").read()

# --- F83 precision about F81 ---------------------------------------------------
a = ("F81's 'This site publishes no product page for either' is now false as of this merge, and the two stale "
     "statements are fixed together in this pass")
b = ("F81's 'This site publishes no product page for either' is still literally true — there are no per-product "
     "pages — but its companion clause 'makes no claim about them' is overtaken: this pass publishes sourced "
     "specification rows for both")
if a in s:
    s = s.replace(a, b, 1)
    print("F83 clause refined")
else:
    a2 = "F81's 'This site publishes no product page for either' is now false as of this merge"
    assert a2 in s, "F83 anchor not found"
    s = s.replace(a2, b, 1)
    print("F83 clause refined (short form)")

# --- page_intent(): render the re-read + control test -------------------------
head = '    ledger_cols = "".join(f"<th>{e(c)}</th>" for c in ledger["columns"])'
assert s.count(head) == 1, "ledger_cols anchor"

code = '''    # Pass 13 (2026-11-17, arena/00bc7156): the re-read block and the marker control test are rendered
    # from data/product-intent.json rather than summarised here, so this page shows whatever the ledger
    # holds and a later pass that rewrites the ledger rewrites the page with it.
    reads = intent.get("reads_2026_11_17_00bc7156") or {}
    ctl = reads.get("control_test") or {}
    reads_block = ""
    if reads:
        _links = " · ".join("<code>" + e(u) + "</code>" for u in reads.get("links_read", []))
        _skip = " · ".join("<code>" + e(u) + "</code>" for u in reads.get("links_not_re_read_in_this_pass", []))
        _rows = [
            ("Links followed by this pass", _links),
            ("Not re-read by this pass", _skip + '<div class="tiny muted">' + e(reads.get("reread_result", "")) + "</div>"),
            ("<strong>The question the control asks</strong>", e(ctl.get("question", ""))),
            ("How it was run", e(ctl.get("method", ""))),
            ("What came back", e(ctl.get("observed", ""))),
            ("What that implies", e(ctl.get("implication", ""))),
            ("What still justifies the caution", e(ctl.get("what_still_justifies_the_caveat", ""))),
            ("Status", e(ctl.get("status", "")) + ' <a href="flagged.html#f87">F87</a> · '
             '<a href="suggestions.html#sg-38">SG-38</a> · <a href="questions.html#q-29">Q-29</a>'),
        ]
        _body = "".join(f'<tr><td>{k}</td><td class="small">{v}</td></tr>' for k, v in _rows)
        reads_block = (
            '\\n<h2>The 2026-11-17 re-read, and a control test that weakens one long-standing reason</h2>\\n'
            '<p class="small">Recorded on this page because this is where the redirect observations live — and the '
            'marker those observations have been read as proving does not survive a control. Full fetch log: '
            '<a href="https://github.com/kanlerxz87-cyber/Zone1/blob/main/session-00bc7156/observations-2026-11-17.json">'
            '<code>session-00bc7156/observations-2026-11-17.json</code></a>.</p>\\n'
            '<div class="tablewrap"><table><caption>What the fifth and sixth reads established, and what they did not</caption>'
            '<thead><tr><th style="width:26%">Item</th><th>Record</th></tr></thead><tbody>' + _body + '</tbody></table></div>\\n'
            '<p class="small">Two of the five rows above (PI-04, PI-05) now have published specification rows of their '
            'own — <a href="categories/kitchen-tools.html">the kitchen-tools cluster</a> — with the fields no official '
            'document supports left blank on the page instead of dropped from the record.</p>\\n'
        )
'''
s = s.replace(head, code + head, 1)

a2 = "<h2>Campaign ledger</h2>"
assert s.count(a2) == 1
s = s.replace(a2, "{reads_block}\n<h2>Campaign ledger</h2>", 1)

open(P, "w", encoding="utf-8").write(s)

import ast

ast.parse(s)
print("page_intent extended; build.py parses")
