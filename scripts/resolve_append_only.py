#!/usr/bin/env python3
"""Append-only conflict resolver for the shared COORDINATION.md board.

Every parallel session appends its own claim/completion block at the end of the
file, so a rebase on `main` conflicts there even when no text actually
contradicts. The rule this pass follows, recorded in COORDINATION.md, is: keep
the upstream side verbatim and re-append this session's block after it. Never
reorder, trim or rewrite another session's lines.

Usage: python3 scripts/resolve_append_only.py PATH [PATH ...]
"""

from __future__ import annotations

import sys
from pathlib import Path

OURS = ("<<<<<<< ", "<<<<<<<")
SEP = "======="
THEIRS = (">>>>>>> ", ">>>>>>>")


def resolve(text: str) -> tuple[str, int]:
    """Return (resolved_text, conflicts_fixed). Upstream block first, ours after."""
    lines = text.split("\n")
    out: list[str] = []
    fixed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(OURS):
            upstream: list[str] = []
            incoming: list[str] = []
            side = upstream
            i += 1
            while i < len(lines) and not lines[i].startswith(THEIRS):
                if lines[i].startswith(SEP) and side is upstream:
                    side = incoming
                    i += 1
                    continue
                side.append(lines[i])
                i += 1
            i += 1  # skip the closing marker
            out.extend(upstream)
            if upstream and incoming:
                out.append("")
            out.extend(incoming)
            fixed += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out), fixed


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    status = 0
    for raw in argv[1:]:
        path = Path(raw)
        text = path.read_text()
        resolved, fixed = resolve(text)
        if not fixed:
            print(f"{path}: no conflict markers found (already resolved?)")
            continue
        if any(
            l.startswith(OURS) or l.startswith(THEIRS) or l.startswith(SEP)
            for l in resolved.split("\n")
        ):
            print(f"{path}: nested/unparsed markers remain -- refusing to write", file=sys.stderr)
            status = 1
            continue
        path.write_text(resolved)
        print(f"{path}: {fixed} conflict block(s) resolved append-only")
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
