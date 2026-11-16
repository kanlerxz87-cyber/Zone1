#!/usr/bin/env python3
"""Resolve a conflicted file keep-both: this session's side AND main's side.

Used by this session's integration pass. COORDINATION.md and data/sources.json
are appended to by every session, so a rebase conflicts at the tail almost every
time. The protocol in COORDINATION.md says to resolve a conflict *without
discarding the other session's work*, which for these two files means: take
main's content, then keep this session's addition as well.

Usage: python3 session-e05e5316/resolve_keep_both.py <path-to-conflicted-file>
"""
from __future__ import annotations

import json
import os
import re
import sys

MARKER = re.compile(r"^<<<<<<< HEAD\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n",
                    re.S | re.M)


def resolve_text(text: str) -> str:
    """Keep both sides of every conflict region, main's first."""
    out = text
    while True:
        m = MARKER.search(out)
        if not m:
            break
        ours, theirs = m.group(1), m.group(2)
        merged = ours.rstrip() + "\n\n" + theirs.lstrip("\n")
        out = out[:m.start()] + merged + out[m.end():]
    return out


def resolve_json(text: str) -> str:
    """Merge two JSON documents key by key, keeping every key from both sides."""
    # Rebuild each side as a document by removing the other's hunks.
    ours_parts, theirs_parts = [], []
    pos = 0
    for m in MARKER.finditer(text):
        ours_parts.append(text[pos:m.start(1)])
        ours_parts.append(m.group(1))
        theirs_parts.append(m.group(2))
        pos = m.end(2)
    ours_parts.append(text[pos:])
    ours = json.loads("".join(ours_parts))
    theirs = json.loads("".join(theirs_parts))
    merged = dict(ours)
    for key, value in theirs.items():
        if key not in merged:
            merged[key] = value
        elif isinstance(merged[key], dict) and isinstance(value, dict):
            out = dict(merged[key])
            for k2, v2 in value.items():
                if k2 not in out:
                    out[k2] = v2
                elif isinstance(out[k2], list) and isinstance(v2, list):
                    merged_list = list(out[k2])
                    for item in v2:
                        if item not in merged_list:
                            merged_list.append(item)
                    out[k2] = merged_list
            merged[key] = out
        elif isinstance(merged[key], list) and isinstance(value, list):
            merged_list = list(merged[key])
            for item in value:
                if item not in merged_list:
                    merged_list.append(item)
            merged[key] = merged_list
    return json.dumps(merged, indent=1, ensure_ascii=False) + "\n"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    text = open(path, encoding="utf-8").read()
    if "<<<<<<< HEAD" not in text:
        print(f"{path}: no conflict markers")
        return 0
    if path.endswith(".json"):
        resolved = resolve_json(text)
    else:
        resolved = resolve_text(text)
    leftovers = [l for l in resolved.split("\n")
                 if l.startswith("<<<<<<< ") or l.startswith(">>>>>>> ")]
    if leftovers:
        print(f"{path}: {len(leftovers)} unresolved marker lines remain")
        return 1
    open(path, "w", encoding="utf-8").write(resolved)
    print(f"{path}: resolved keep-both ({os.path.getsize(path)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
