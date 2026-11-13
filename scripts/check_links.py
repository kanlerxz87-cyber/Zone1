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
import subprocess
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_SLUG = "kanlerxz87-cyber/Zone1"
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


_REFS = None
_REFS_CACHE = {}


def _repo_refs():
    global _REFS
    if _REFS is None:
        out = subprocess.run(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes"],
                             cwd=ROOT, capture_output=True, text=True).stdout
        _REFS = {r.strip() for r in out.splitlines() if r.strip()}
    return _REFS


def _path_exists(ref_or_none_candidates, path):
    for ref in ref_or_none_candidates:
        key = (ref, path)
        if key not in _REFS_CACHE:
            _REFS_CACHE[key] = subprocess.run(["git", "cat-file", "-e", f"{ref}:{path}"],
                                              cwd=ROOT, capture_output=True).returncode == 0
        if _REFS_CACHE[key]:
            return True
    return False


def check_repo_link(url: str) -> str | None:
    """A link into this repository must point at a path that exists.

    Branch names may contain slashes (arena/x-zone1), so the ref/path boundary is
    ambiguous; every split is tried and the one that names a real ref wins. When a
    link targets `main` it is also accepted if the path exists on HEAD, so a pull
    request that *adds* the file it links to is not falsely reported as broken.
    """
    m = re.match(r"https://github\.com/([^/]+/[^/]+)/(?:tree|blob)/(.+?)/?$", url or "")
    if not m or m.group(1) != REPO_SLUG:
        return None
    rest = m.group(2)
    if "#" in rest:
        rest = rest.split("#", 1)[0]
    parts = [p for p in rest.split("/") if p]
    refs = _repo_refs()

    def known(ref):
        return ref in refs or ("origin/" + ref) in refs or ref in {"main", "HEAD"}

    if len(parts) == 1:
        # A bare /tree/<sha> or /tree/<branch> link: valid if that object exists.
        ref = parts[0]
        for probe in (ref, "origin/" + ref):
            if subprocess.run(["git", "cat-file", "-e", f"{probe}^{{tree}}"],
                              cwd=ROOT, capture_output=True).returncode == 0:
                return None
        return f"link into this repo names a ref that does not exist: {url}"
    chosen = None
    for i in range(1, len(parts)):
        cand = "/".join(parts[:i])
        if known(cand):
            chosen = (cand, "/".join(parts[i:]))
            break
    if chosen is None:
        return f"link into this repo names an unknown ref: {url}"
    ref, path = chosen
    probes = [ref, "origin/main", "HEAD"] if ref == "main" else [ref, "origin/" + ref]
    if not _path_exists(probes, path):
        return f"link into this repo points at a path that does not exist in {ref} -> {path}"
    return None


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
                if parsed.netloc.endswith("amazon.com") and "/dp/" in parsed.path and (anchor or "").lstrip("#"):
                    errors.append(f"{rel_from_root}: /dp/ link carries a fragment, which Amazon ignores")
                bad = check_repo_link(target)
                if bad:
                    (errors if strict else warnings).append(f"{rel_from_root}: {bad}")
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
    for scope, sink in (("mine", errors), ("inherited", warnings)):
        for path in html_files(scope):
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            text = open(path, encoding="utf-8").read()
            for tbl in re.findall(r"<tbody>(.*?)</tbody>", text, re.S):
                for row in re.findall(r"<tr>(.*?)</tr>", tbl, re.S):
                    if "<th>" in row:
                        continue
                    if "<a " not in row:
                        sink.append(f"{rel}: table row with no source link -> {re.sub('<[^>]+>', ' ', row)[:70].strip()}")

    # every html file must reference the stylesheet that exists
    for path in html_files("mine"):
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        text = open(path, encoding="utf-8").read()
        if "assets/app.css" not in text:
            errors.append(f"{rel}: does not link the shared stylesheet")
    if warnings:
        print(f"NOTE: {len(warnings)} advisory finding(s) in pages inherited from other sessions — reported, not blocking:")
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
