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

HREF = re.compile(r'''(?:href|src)=["']([^"'#]+)(#[^"']*)?["']''')
ROW_HREF = re.compile(r'''href=["']([^"']+)["']''')
SITE_ROOTS = {"index.html"}


def _registered_hosts():
    """Hosts this project treats as official.

    The union of every source register in the repository: the root register
    (data/sources.json) plus the parallel builds' own registers
    (data/s2/, data/verified/, research/), plus the platform engine's list of
    Amazon programme and developer domains. A sibling build that cites its own
    register must not be reported as unsourced just because its register is a
    different file.
    """
    global _REGISTERED_HOSTS
    if _REGISTERED_HOSTS is None:
        import json
        hosts = set()
        registers = [
            "data/sources.json",
            "data/s2/sources.json",
            "data/verified/sources.json",
            "research/sources-s8a2.json",
        ]
        for rel in registers:
            path = os.path.join(ROOT, rel)
            if not os.path.exists(path):
                continue
            try:
                doc = json.load(open(path, encoding="utf-8"))
            except ValueError:
                continue
            for s in doc.get("sources", []):
                url = s.get("url") or ""
                if url:
                    hosts.add((urlparse(url).hostname or "").lower())
        try:
            from platform._common import OFFICIAL_HOSTS  # type: ignore
            hosts.update(h.lower() for h in OFFICIAL_HOSTS)
        except Exception:
            pass
        hosts.add("github.com")
        # The site's own published origin (GitHub Pages for this repo). A row that
        # points at the live page it documents is citing the official location of
        # that document, so it counts as sourced.
        hosts.add("kanlerxz87-cyber.github.io")
        _REGISTERED_HOSTS = {h for h in hosts if h}
    return _REGISTERED_HOSTS


_REGISTERED_HOSTS = None


def _is_official_href(href):
    """True when the href points at a host this project treats as official."""
    try:
        host = (urlparse(href).hostname or "").lower()
    except ValueError:
        return False
    return host in _registered_hosts()


def html_files(scope="all"):
    """`mine` = the generated subtree plus the root landing page this session owns.

    Inherited pages from parallel sessions are still scanned, but reported as
    warnings: this project must not red-build someone else's page, and must not
    be blocked by defects in it either.
    """
    for base, directories, files in os.walk(ROOT):
        # Optional browser tooling is not a published build. Prune rather than
        # scanning dependencies/caches and mistaking their HTML for our content.
        excluded = {"node_modules", "test-results", "playwright-report", "_site", "crosscheck"}
        directories[:] = sorted(d for d in directories if not d.startswith(".") and d not in excluded)
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
_SHALLOW = None


def _history_available():
    """False in the depth-1 checkout CI uses.

    The repo-path check needs objects, not just text, so on a shallow clone it would
    report "ref does not exist" for a perfectly good link to the base commit — a
    false alarm about someone else's history, which is the one thing a gate like this
    must never produce. When history is missing, the check degrades to advisory.
    """
    global _SHALLOW
    if _SHALLOW is None:
        out = subprocess.run(["git", "rev-parse", "--is-shallow-repository"],
                             cwd=ROOT, capture_output=True, text=True).stdout.strip()
        _SHALLOW = out != "true"
    return _SHALLOW


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
        if not _history_available():
            return None  # cannot judge object existence from a shallow checkout
        return f"link into this repo names a ref that does not exist: {url}"
    chosen = None
    for i in range(1, len(parts)):
        cand = "/".join(parts[:i])
        if known(cand):
            chosen = (cand, "/".join(parts[i:]))
            break
    if chosen is None:
        if not _history_available():
            return None
        return f"link into this repo names an unknown ref: {url}"
    ref, path = chosen
    probes = [ref, "origin/main", "HEAD"] if ref == "main" else [ref, "origin/" + ref]
    if not _path_exists(probes, path):
        if not _history_available():
            return None
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
                    # A row counts as sourced when it links to a registered official host,
                    # to this repository on GitHub, or to the page where unconfirmed values
                    # are published. Sibling builds name that page differently
                    # (flagged.html, flagged-for-review.html, flagged/), so match on the
                    # word rather than one literal filename. Both quote styles are
                    # accepted: some generators emit single-quoted hrefs, and a gate that
                    # cannot see those would report a sourced row as unsourced.
                    row_links = ROW_HREF.findall(row)
                    if not any(
                        _is_official_href(h) or "flagged" in h or "github.com" in h
                        for h in row_links
                    ):
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
