#!/usr/bin/env python3
"""One-shot patch: verify.py — allowlist the official Amazon hosts, add V13 repo-wide.

Applied by session arena/88bb2db6 on 2026-11-15.

V14  OFFICIAL_HOSTS is extended with three official Amazon / GitHub hosts that the
     s2/ annex cites: advertising.amazon.com (Amazon Ads / Associates advertising
     policy), sell.amazon.com (Amazon Selling partner pages), and api.github.com
     (the GitHub REST API, used to record the Pages configuration). All three are
     owned by the organisation they document. Before this change verify.py printed
     18 warnings for them, which trained the reader to ignore the warning list.

V13  A repository-wide nested-anchor check. The root site and the annex each
     gained one in this pass; this check makes the whole tree safe, whichever
     generator produces a page in future.
"""
from pathlib import Path

p = Path("verify.py")
s = p.read_text(encoding="utf-8")

old_hosts = '''    # official Amazon developer / publishing documentation (ASIN definition sources)
    "webservices.amazon.com",
    "kdp.amazon.com",'''
new_hosts = '''    # official Amazon developer / publishing documentation (ASIN definition sources)
    "webservices.amazon.com",
    "kdp.amazon.com",
    # official Amazon programme pages cited by the s2/ annex. Added 2026-11-15
    # (arena/88bb2db6): all three are Amazon- or GitHub-owned domains, and each is
    # the official home of the fact it is cited for. Before this change verify.py
    # printed 18 warnings for them, which made the warning list noise.
    "advertising.amazon.com",
    "sell.amazon.com",
    # the GitHub REST API, cited for the repository's own Pages configuration
    "api.github.com",'''
if s.count(old_hosts) != 1:
    raise SystemExit(f"V14 PATCH FAILED ({s.count(old_hosts)} matches)")
s = s.replace(old_hosts, new_hosts)

old_doc = '''  6. no Amazon price / star-rating pattern leaked into the HTML
'''
new_doc = '''  6. no Amazon price / star-rating pattern leaked into the HTML
  7. no page nests an <a> inside another <a> (invalid HTML)
'''
if s.count(old_doc) != 1:
    raise SystemExit("doc PATCH FAILED")
s = s.replace(old_doc, new_doc)

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
if s.count(old_imports) != 1:
    raise SystemExit("imports PATCH FAILED")
s = s.replace(old_imports, new_imports)

old_loop = '''    # 6. no Amazon price / star-rating leakage'''
new_loop = '''    # 7. no nested anchors (invalid HTML). Found in site/index.html on 2026-11-15.
    _parser = _NestedAnchorParser()
    _parser.feed(text)
    for _href in _parser.nested:
        errors.append(f"{rel(page)}: <a> nested inside another <a> (href={_href!r})")

    # 6. no Amazon price / star-rating leakage'''
if s.count(old_loop) != 1:
    raise SystemExit("loop PATCH FAILED")
s = s.replace(old_loop, new_loop)

old_errors = '''errors = []
warnings = []
'''
new_errors = '''errors = []
warnings = []


class _NestedAnchorParser(HTMLParser):
    """Records any <a> opened while another <a> is still open."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.nested = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            if self.depth:
                self.nested.append(dict(attrs).get("href", ""))
            self.depth += 1

    def handle_endtag(self, tag):
        if tag == "a" and self.depth:
            self.depth -= 1
'''
if s.count(old_errors) != 1:
    raise SystemExit("errors PATCH FAILED")
s = s.replace(old_errors, new_errors)

p.write_text(s, encoding="utf-8")
print("verify.py patched: V14 allowlist + V13 nested-anchor check")
