#!/usr/bin/env python3
"""Stage the public Pages artifact without rewriting independent-build source files.

Only files known to Git are copied. Noncanonical HTML remains reachable, but the
*deployment copy* receives noindex,follow, a clearly visible archive notice and the
required disclosure below its masthead (or at body start if it has no header).
This is not a change to an archived claim or source observation.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DIRS = {"articles", "products", "guides", "categories"}
PUBLIC_SUFFIXES = {".html", ".css", ".js", ".json", ".svg", ".webp", ".png", ".jpg", ".jpeg", ".ico", ".xml", ".txt", ".md", ".csv", ".pdf"}
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
CANONICAL_HOME = "https://kanlerxz87-cyber.github.io/Zone1/"
ROBOTS = re.compile(r'<meta\b(?=[^>]*\bname=[\"\'](?:robots|googlebot|bingbot)[\"\'])[^>]*>', re.I)


def qualify_product_links(text: str) -> str:
    """Even an archived product/citation anchor must disclose its paid-link status."""
    def anchor(match: re.Match) -> str:
        tag = match.group(0)
        href = re.search(r'\bhref=[\"\']([^\"\']+)[\"\']', tag, re.I)
        if not href:
            return tag
        try:
            url = urlsplit(href.group(1))
        except ValueError:
            return tag
        if url.hostname == "link.amazon" and url.path.rstrip('/') == '/ZZZ9ZZZZZ':
            return tag  # S22 is an explicitly documented resolver control, not a product.
        product_path = re.search(r'/(?:dp|gp/product|gp/aw/d|product-reviews)/', url.path)
        if url.scheme != "https" or not (url.hostname == "link.amazon" or
                url.hostname in {"www.amazon.com", "amazon.com"} and product_path):
            return tag
        rel = re.search(r'\srel=[\"\']([^\"\']*)[\"\']', tag, re.I)
        values = list(dict.fromkeys(["sponsored"] + (rel.group(1).split() if rel else [])))
        tag = re.sub(r'\srel=[\"\'][^\"\']*[\"\']', '', tag, count=1, flags=re.I)
        return tag[:-1].rstrip() + f' rel="{" ".join(values)}">'
    return re.sub(r'<a\b[^>]*>', anchor, text, flags=re.I)


def rewrite_repository_links(text: str, rel: Path, root: Path = ROOT) -> str:
    """Source-code citations belong on GitHub, not in a static execution endpoint.

    Also rehome repository directories without an index page; Pages does not serve
    directory listings. Public documents/assets retain their original relative URL.
    """
    root = root.resolve()
    def link(match: re.Match) -> str:
        raw = match.group(1)
        url = urlsplit(raw)
        if url.scheme or url.netloc or not url.path or raw.startswith('/'):
            return match.group(0)
        target = (root / rel.parent / unquote(url.path)).resolve()
        if not target.is_relative_to(root):
            return match.group(0)  # canonical link checks flag an escaping path
        path = target.relative_to(root)
        if target.is_dir():
            if (target / 'index.html').is_file():
                return match.group(0)
            kind = 'tree'
        elif target.suffix.lower() in PUBLIC_SUFFIXES and not any(p.startswith('.') for p in path.parts):
            return match.group(0)
        else:
            kind = 'blob'
        fragment = '#' + url.fragment if url.fragment else ''
        return 'href="https://github.com/kanlerxz87-cyber/Zone1/' + kind + '/main/' + quote(path.as_posix(), safe='/') + fragment + '"'
    return re.sub(r'href=[\"\']([^\"\']+)[\"\']', link, text, flags=re.I)


def is_canonical_path(rel: Path) -> bool:
    return len(rel.parts) == 1 or rel.parts[0] in CANONICAL_DIRS


def archive_html(text: str) -> str:
    """Idempotent deployment wrapper. Original claim/source text is left untouched."""
    if 'id="zone1-archive-notice"' in text:
        return text
    text = ROBOTS.sub('', text)
    notice_style = ('<meta name="robots" content="noindex,follow">\n'
        '<style>#zone1-archive-notice{box-sizing:border-box;display:block;position:relative;'
        'z-index:1;background:#fff2ce;color:#3b3424;border-block:1px solid #ccb96e;'
        'padding:14px 5%;font:14px/1.65 system-ui,sans-serif;text-align:left}'
        '#zone1-archive-notice p{margin:3px 0;color:inherit;font:inherit}'
        '#zone1-archive-notice a{color:#214a35;text-decoration:underline;font-weight:600}'
        '</style>\n')
    text = re.sub(r'</head\s*>', lambda m: notice_style + m.group(0), text, count=1, flags=re.I)
    notice = ('\n<aside id="zone1-archive-notice" aria-label="Historical build notice">'
        f'<p><strong>Historical research build — not the current publication.</strong> '
        f'<a href="{CANONICAL_HOME}">Visit Zone1 Kitchen →</a></p>'
        '<p>Preserved for evidence; dates and claims may be out of date. '
        'This copy is marked noindex for search crawlers. No analytics is enabled here.</p>'
        f'<p><strong>Affiliate disclosure:</strong> {DISCLOSURE}</p></aside>\n')
    # Independent builds use different header classes. Do not assume a sidebar layout.
    if re.search(r'</header\s*>', text, re.I):
        text = re.sub(r'</header\s*>', lambda m: m.group(0) + notice, text, count=1, flags=re.I)
    else:
        text = re.sub(r'<body\b[^>]*>', lambda m: m.group(0) + notice, text, count=1, flags=re.I)
    # A historical counter must never collect just because its old HTML loads a file.
    text = re.sub(r'<script\b[^>]*\bsrc=[\"\'][^\"\']*analytics\.js[^\"\']*[\"\'][^>]*>\s*</script>', '', text, flags=re.I)
    return text


def stage(destination: Path, *, root: Path = ROOT, files: list[str] | None = None) -> dict[str, int]:
    root = root.resolve()
    destination = destination.resolve()
    if destination == root or root.is_relative_to(destination):
        raise ValueError("destination must not be the checkout or one of its parents")
    if destination.exists():
        # Never recursively remove an existing directory. Reusing it might publish
        # stale files, so require a fresh staging path (CI always has one).
        raise ValueError("destination already exists; use a fresh empty staging path")
    if files is None:
        result = subprocess.run(["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True)
        files = result.stdout.decode('utf-8').split('\0')
    destination.mkdir(parents=True)
    counts = {"files": 0, "canonical_html": 0, "archived_html": 0, "indexable_html": 0}
    for name in sorted(set(files)):
        if not name:
            continue
        rel = Path(name)
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError("unsafe source path")
        if any(part.startswith('.') for part in rel.parts) and name != '.nojekyll':
            continue
        if rel.suffix.lower() not in PUBLIC_SUFFIXES and name != '.nojekyll':
            continue
        source = root / rel
        if source.is_symlink() or not source.is_file():
            continue
        output = destination / rel
        output.parent.mkdir(parents=True, exist_ok=True)
        if rel.suffix == '.html':
            text = source.read_text(encoding='utf-8')
            if is_canonical_path(rel):
                counts['canonical_html'] += 1
                if not ROBOTS.search(text):
                    raise ValueError(f"canonical HTML lacks robots directive: {name}")
            else:
                counts['archived_html'] += 1
                text = archive_html(text)
            text = rewrite_repository_links(qualify_product_links(text), rel, root)
            directives = ROBOTS.findall(text)
            if any('noindex' not in value.lower() for value in directives):
                if not is_canonical_path(rel):
                    raise ValueError(f"archive is indexable: {name}")
                counts['indexable_html'] += 1
            output.write_text(text, encoding='utf-8')
        else:
            shutil.copyfile(source, output)
        counts['files'] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    args = parser.parse_args()
    counts = stage(args.output)
    print('Pages artifact staged: ' + ', '.join(f'{key}={value}' for key, value in counts.items()))


if __name__ == '__main__':
    main()
