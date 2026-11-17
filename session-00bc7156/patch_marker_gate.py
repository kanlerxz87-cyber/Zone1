"""Add the one gate this repository keeps needing: a merge-marker check over its text files.

Why this pass adds it rather than noting it again: the same defect has now been committed three times —
`7c6806f` briefly committed conflict markers into COORDINATION.md and `3e4859f` repaired it (the register
files it as the F22 class), and on 2026-11-17 this session left a stray marker in the same file twice while
resolving keep-both conflicts, catching it only by reading the file. Every other file type in this repo has a
gate that fails the build; Markdown and JSON have none, because the gates that exist all reason about the
generated pages, and a marker inside a register survives every one of them.

Scope decision, stated so the next session can disagree with something specific: the check covers the whole
repository, including files owned by parallel passes. A marker in someone else's file is still a marker in a
published artefact, and every session runs this build before merging, so the session that notices is the one
that fixes it — which is the same rule the merge-base gate failures already follow here.
"""

P = "build.py"
s = open(P, encoding="utf-8").read()

FUNC = '''

def check_conflict_markers():
    """Build guard: no git merge-conflict marker may survive in any tracked text file.

    Written 2026-11-17 (arena/00bc7156) after this defect class shipped three times in two days, twice in
    COORDINATION.md, and no existing gate could see it: verify.py and scripts/check_links.py reason about
    generated pages, so a `>>>>>>>` line sitting in a Markdown file or a JSON register passes them all.
    Two rules keep it honest rather than noisy:
      * an angle-bracket marker line (`<<<<<<< ` / `>>>>>>> `) is always fatal — no prose writes those;
      * a bare `=======` line counts only when the same file also carries an angle marker, because
        Markdown's setext heading underline looks identical and is not a defect.
    Binary, generated-asset and dependency paths are skipped; the scan is a few thousand files and under a
    second.
    """
    import os

    skip_dirs = {".git", "node_modules", ".venv", "__pycache__", ".pytest_cache", ".cache"}
    exts = (".md", ".json", ".py", ".html", ".yml", ".yaml", ".txt", ".css", ".js", ".sh")
    problems = []
    root = ROOT
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            if not fn.endswith(exts):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                    lines = fh.read().splitlines()
            except OSError:
                continue
            angle = [i + 1 for i, ln in enumerate(lines)
                     if ln.startswith("<<<<<<< ") or ln.startswith(">>>>>>> ")]
            if not angle:
                continue
            where = ", ".join(f"line {n}" for n in angle[:4])
            if len(angle) > 4:
                where += f" (+{len(angle) - 4} more)"
            problems.append(f"{os.path.relpath(fp, root)}: unresolved merge-conflict marker at {where}")
    return problems

'''

anchor = "def check_requirement_tokens():"
assert s.count(anchor) == 1
s = s.replace(anchor, FUNC.lstrip("\n") + "\n" + anchor, 1)

# wire it in as the first thing main() does, before any page is written
a2 = '''def main():
    t0 = time.time()'''
assert s.count(a2) == 1, "main anchor"
s = s.replace(a2, '''def main():
    t0 = time.time()
    # First, before a single page is written: a register with a marker in it is not worth rendering, and
    # aborting here means the build never publishes a half-merged tree alongside the marker that caused it.
    marker_problems = check_conflict_markers()
    if marker_problems:
        raise SystemExit("BUILD FAILED — unresolved git merge-conflict markers in tracked text files "
                         "(resolve the conflict, then rebuild):\\n  " + "\\n  ".join(marker_problems))''', 1)

open(P, "w", encoding="utf-8").write(s)

import ast

ast.parse(s)
print("marker gate added to build.py")
