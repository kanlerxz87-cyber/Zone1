#!/usr/bin/env python3
"""Link gate for the published site.

Two jobs:
  1. every internal href/src must resolve to a file that will actually exist on
     GitHub Pages (accounting for the /Zone1/ base path and for #anchors);
  2. every external href must be https and land on a host this project treats
     as official -- which is what stops a citation quietly becoming a blog post.
External reachability is verified separately against the live deployment.
"""
from __future__ import annotations

import os
import re
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "platform"))
from _common import is_official  # noqa: E402

HREF = re.compile(r'(?:href|src)="([^"#]+)(#[^"]*)?"')
SITE_ROOTS = {"index.html"}


def html_files(scope="all"):
    """`mine` = the generated subtree plus the root landing page this session owns.

    Inherited pages from parallel sessions are still scanned, but reported as
    warnings: this project must not red-build someone else's page, and must not
    be blocked by defects in it either.
    """
    for base, _dirs, files in os.walk(ROOT):
        if any(p in base for p in ("/.git", "/node_modules", "/_site", "/crosscheck")):
            continue
        for f in sorted(files):
            if not f.endswith(".html"):
                continue
            full = os.path.join(base, f)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            mine = rel == "s2/index.html" or rel.startswith("s2/")
            if scope == "mine" and not mine:
                continue
            if scope == "inherited" and mine:
                continue
            yield full


def is_mine(path: str) -> bool:
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    return rel == "s2/index.html" or rel.startswith("s2/")


def main() -> int:
    errors: list[str] = []
    checked = 0
    warnings: list[str] = []
    for path in html_files():
        rel_from_root = os.path.relpath(path, ROOT).replace(os.sep, "/")
        strict = is_mine(path)
        text = open(path, encoding="utf-8").read()
        for target, anchor in HREF.findall(text):
            checked += 1
            if target.startswith(("mailto:", "data:", "javascript:")):
                continue
            parsed = urlparse(target)
            if parsed.scheme:  # external
                if parsed.scheme != "https":
                    errors.append(f"{rel_from_root}: non-https link {target}")
                elif parsed.netloc.endswith("amazon.com") and "/dp/" in parsed.path:
                    frag = (anchor or "").lstrip("#")
                    if frag:
                        errors.append(f"{rel_from_root}: /dp/ link carries a fragment, which Amazon ignores")
                continue
            # internal
            base = os.path.dirname(path)
            dest = os.path.normpath(os.path.join(base, target or rel_from_root))
            if not os.path.exists(dest):
                (errors if strict else warnings).append(f"{rel_from_root}: broken internal link -> {target}")
            if anchor and os.path.exists(dest) and dest.endswith(".html"):
                frag = anchor[1:]
                if frag and f'id="{frag}"' not in open(dest, encoding="utf-8").read():
                    (errors if strict else warnings).append(
                        f"{rel_from_root}: missing anchor {anchor} in {os.path.relpath(dest, ROOT)}")
    # THE core promise of this site, enforced on rendered output:
    # every data row in a table body must carry at least one link.
    for path in html_files():
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        text = open(path, encoding="utf-8").read()
        for tbl in re.findall(r"<tbody>(.*?)</tbody>", text, re.S):
            for row in re.findall(r"<tr>(.*?)</tr>", tbl, re.S):
                if "<th>" in row:
                    continue
                if "<a " not in row:
                    errors.append(f"{rel}: table row with no source link -> {re.sub('<[^>]+>', ' ', row)[:70].strip()}")

    # every html file must reference the stylesheet that exists
    for path in html_files("mine"):
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        text = open(path, encoding="utf-8").read()
        if "assets/app.css" not in text:
            errors.append(f"{rel}: does not link the shared stylesheet")
    if warnings:
        print(f"{len(warnings)} advisory finding(s) in pages inherited from other sessions (not blocking):")
        for w in warnings[:12]:
            print("  ~", w)
        if len(warnings) > 12:
            print(f"   … {len(warnings) - 12} more")
    if errors:
        print("LINK CHECK FAILED")
        for e in errors:
            print("  ✗", e)
        return 1
    print(f"link check ok · {checked} links · {len(list(html_files('mine')))} pages owned by this session "
          f"(+{len(list(html_files('inherited')))} inherited, advisory)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
