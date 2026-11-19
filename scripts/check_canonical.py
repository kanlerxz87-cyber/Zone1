#!/usr/bin/env python3
"""Prove committed/generated canonical output was current *before* rebuilding it.

No git-diff shortcut: compare content hashes before and after the build, including
new/deleted canonical pages. Two rebuilds of freshly overwritten output would not
be a stale-output check. This script uses no network or third-party dependencies.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def snapshot(root=ROOT):
    files = set(root.glob('*.html'))
    for folder in ('articles', 'products', 'categories', 'guides'):
        files.update((root / folder).glob('*.html'))
    files.update((root / 'assets' / 'figures').glob('*.svg'))
    files.update(root / name for name in ('assets/style.css', 'assets/app.js', 'assets/analytics.js', 'sitemap.xml', 'feed.xml', 'robots.txt'))
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files if path.is_file()}


def main():
    before = snapshot()
    result = subprocess.run([sys.executable, 'build.py'], cwd=ROOT)
    if result.returncode:
        return result.returncode
    after = snapshot()
    changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
    if changed:
        print('STALE canonical output (rebuild updated these files):', file=sys.stderr)
        print('\n'.join('  ' + name for name in changed), file=sys.stderr)
        return 1
    print(f'Canonical output current and reproducible: {len(after)} artifacts unchanged.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
