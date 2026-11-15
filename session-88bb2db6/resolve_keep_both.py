#!/usr/bin/env python3
"""Resolve COORDINATION.md rebase conflicts by keeping both sides.

The conflicts are all in the append region of the board: every session appends its
own record at the end of the file, so two sessions appending at once produce
"both sides appended" conflicts. Protocol section 6 requires resolving without
discarding the other session's work, so this keeps HEAD's block and then the
incoming block, in that order, with a short marker between them.

Nothing else in the file is touched.
"""
import re
import sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else "COORDINATION.md")
text = path.read_text(encoding="utf-8")

MARK = re.compile(
    r"^<<<<<<< [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n",
    re.S | re.M,
)


def resolve(m):
    ours, theirs = m.group(1), m.group(2)
    # Trim the trailing blank lines each side contributes so the seam is clean.
    ours = ours.rstrip("\n")
    theirs = theirs.rstrip("\n")
    return (
        ours
        + "\n\n<!-- keep-both: the block below was appended by the session being "
          "rebased on top; nothing from either side is discarded -->\n\n"
        + theirs
        + "\n"
    )


new, n = MARK.subn(resolve, text)
path.write_text(new, encoding="utf-8")
print(f"resolved {n} conflict hunk(s) in {path} (keep-both)")
if n == 0:
    print("no conflict markers matched - check the file")
    sys.exit(1)
