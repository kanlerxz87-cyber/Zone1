#!/usr/bin/env python3
"""One-shot patch: repair the annex nested anchor and add a guard against it.

Applied by session arena/88bb2db6 on 2026-11-15.

F6  site/index.html wrapped the whole "Main dashboard" card in <a class="card"> and
    then put a second <a href="flagged.html#F-16"> inside it. A nested anchor is
    invalid HTML: assistive technology and some crawlers resolve the inner link to
    the outer one. The cross-reference is moved out of the card, keeping both the
    whole-card click target and the F-16 citation.

G1  scripts/verify_site.py gains check_no_nested_anchors(), a new V13 assertion.
    The annex verifier previously passed with 382 assertions while this defect sat
    in the rendered HTML, because nothing looked for it. The new check parses each
    generated page and fails on any <a> nested inside another <a>.
"""
from pathlib import Path

# ------------------------------------------------------------------ F6
p = Path("scripts/build_site.py")
s = p.read_text(encoding="utf-8")

old_card = '''<a class="card" href="../index.html">
    <h3>Main dashboard</h3>
    <p>The repository's canonical site at the root URL, built by the other concurrent sessions.
    This annex does not modify it. See <a href="flagged.html#F-16">F-16</a>.</p>
  </a>'''
new_card = '''<a class="card" href="../index.html">
    <h3>Main dashboard</h3>
    <p>The repository's canonical site at the root URL, built by the other concurrent sessions.
    This annex does not modify it.</p>
  </a>'''
if s.count(old_card) != 1:
    raise SystemExit(f"F6 PATCH FAILED ({s.count(old_card)} matches)")
s = s.replace(old_card, new_card)

old_tail = '''  <a class="card" href="sources.html">
    <h3>Sources</h3>
    <p>The 16 official documents behind every value, with what each one was used to verify.</p>
  </a>
</div>'''
new_tail = '''  <a class="card" href="sources.html">
    <h3>Sources</h3>
    <p>The 16 official documents behind every value, with what each one was used to verify.</p>
  </a>
</div>
<p class="small">This annex does not modify the main dashboard above. The reason is recorded as
<a href="flagged.html#F-16">F-16</a>.</p>'''
if s.count(old_tail) != 1:
    raise SystemExit(f"F6 tail PATCH FAILED ({s.count(old_tail)} matches)")
s = s.replace(old_tail, new_tail)
p.write_text(s, encoding="utf-8")
print("F6 applied: nested anchor removed from scripts/build_site.py")

# ------------------------------------------------------------------ G1
v = Path("scripts/verify_site.py")
t = v.read_text(encoding="utf-8")

old_doc = '''  V12 no page contains a bare 'affiliate link' used as its only disclosure (C-02)
'''
new_doc = '''  V12 no page contains a bare 'affiliate link' used as its only disclosure (C-02)
  V13 no page nests an <a> inside another <a> (invalid HTML; found in site/index.html
      on 2026-11-15 and fixed in the same pass)
'''
if t.count(old_doc) != 1:
    raise SystemExit("G1 doc PATCH FAILED")
t = t.replace(old_doc, new_doc)

old_imports = '''import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
'''
new_imports = '''import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
'''
if t.count(old_imports) != 1:
    raise SystemExit("G1 imports PATCH FAILED")
t = t.replace(old_imports, new_imports)

# The new check, inserted immediately before main().
old_main = '''def main() -> int:
    check_expected_pages()'''
new_main = '''# ------------------------------------------------------------- V13 markup
class _NestedAnchorParser(HTMLParser):
    """Records any <a> that is opened while another <a> is still open."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.nested: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            if self.depth:
                href = dict(attrs).get("href", "")
                self.nested.append(href)
            self.depth += 1

    def handle_endtag(self, tag):
        if tag == "a" and self.depth:
            self.depth -= 1


def check_no_nested_anchors() -> None:
    """V13 - an <a> inside an <a> is invalid HTML.

    Added 2026-11-15 (arena/88bb2db6) after the repository-wide review found one in
    site/index.html. The annex verifier passed 382 assertions while that defect was
    present in the rendered page, because no check looked for it. A nested anchor
    makes the inner link ambiguous to assistive technology and to crawlers, which
    may resolve it to the outer link instead.
    """
    global checks_run
    for name in PAGES:
        path = OUT / name
        parser = _NestedAnchorParser()
        parser.feed(path.read_text(encoding="utf-8"))
        checks_run += 1
        for href in parser.nested:
            fail("V13", f"{name}: <a> nested inside another <a> (href={href!r})")


def main() -> int:
    check_expected_pages()'''
if t.count(old_main) != 1:
    raise SystemExit("G1 main PATCH FAILED")
t = t.replace(old_main, new_main)

old_call = '''    check_data_integrity()

    total_fields'''
new_call = '''    check_data_integrity()
    check_no_nested_anchors()

    total_fields'''
if t.count(old_call) != 1:
    raise SystemExit("G1 call PATCH FAILED")
t = t.replace(old_call, new_call)

v.write_text(t, encoding="utf-8")
print("G1 applied: check_no_nested_anchors() added to scripts/verify_site.py")
