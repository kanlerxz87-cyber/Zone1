#!/usr/bin/env python3
"""Verify the actual Pages artifact: links, noindex/archive scope and safe file set.

This is an offline structural check. It does not claim search-engine deindexing,
source adequacy, account permission, production analytics or Amazon attribution.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.stage_pages import DISCLOSURE, is_canonical_path, qualify_product_links  # noqa: E402


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.robots = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get('id'):
            self.ids.add(data['id'])
        if tag == 'a' and data.get('name'):
            self.ids.add(data['name'])
        if tag == 'meta' and data.get('name', '').lower() in {'robots', 'googlebot', 'bingbot'}:
            self.robots.append(data.get('content', '').lower())
        for name in ('href', 'src'):
            if data.get(name):
                self.links.append(data[name])


def verify(root: Path):
    root = root.resolve()
    parsed = {}
    errors = []
    counts = {'html_pages': 0, 'canonical_html': 0, 'archived_html': 0,
              'indexable_html': 0, 'sitemap_urls': 0, 'internal_links': 0}
    for file in sorted(root.rglob('*')):
        if not file.is_file():
            continue
        rel = file.relative_to(root)
        if any(part.startswith('.') for part in rel.parts) and rel.as_posix() != '.nojekyll':
            errors.append(f'{rel}: hidden/private file in artifact')
        if file.suffix in {'.py', '.php', '.sqlite3', '.ndjson', '.key'}:
            errors.append(f'{rel}: runtime/private file in static artifact')
        if file.suffix != '.html':
            continue
        text = file.read_text(encoding='utf-8')
        page = Page(text)
        parsed[file] = page
        counts['html_pages'] += 1
        canonical = is_canonical_path(rel)
        counts['canonical_html' if canonical else 'archived_html'] += 1
        if DISCLOSURE not in text:
            errors.append(f'{rel}: missing disclosure')
        if not page.robots:
            errors.append(f'{rel}: missing robots directive')
        indexable = page.robots and all('noindex' not in value for value in page.robots)
        if indexable:
            counts['indexable_html'] += 1
        if not canonical and (indexable or 'zone1-archive-notice' not in page.ids):
            errors.append(f'{rel}: noncanonical HTML lacks archive/noindex wrapper')
        if qualify_product_links(text) != text:
            errors.append(f'{rel}: unqualified Amazon product anchor')
        if not canonical and re.search(r'<script\b[^>]*\bsrc=["\'][^"\']*analytics\.js', text, re.I):
            errors.append(f'{rel}: archive must not load measurement')
    for file, page in parsed.items():
        for raw in page.links:
            url = urlsplit(raw)
            if url.scheme or url.netloc:
                continue
            path = unquote(url.path)
            if path.startswith('/Zone1/'):
                target = root / path.removeprefix('/Zone1/')
            elif path.startswith('/'):
                target = root / path.lstrip('/')
            else:
                target = file.parent / path if path else file
            target = target.resolve()
            counts['internal_links'] += 1
            if not target.is_relative_to(root):
                errors.append(f'{file.relative_to(root)}: path escapes artifact: {raw}')
                continue
            if target.is_dir():
                target /= 'index.html'
            if not target.is_file():
                errors.append(f'{file.relative_to(root)}: missing deployed target: {raw}')
            elif url.fragment and target in parsed and unquote(url.fragment) not in parsed[target].ids:
                errors.append(f'{file.relative_to(root)}: missing deployed fragment: {raw}')
    sitemap = ET.parse(root / 'sitemap.xml')
    members = set()
    for element in sitemap.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc = element.findtext('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        url = urlsplit(loc or '')
        if url.scheme != 'https' or url.netloc != 'kanlerxz87-cyber.github.io' or not url.path.startswith('/Zone1/'):
            errors.append(f'sitemap: not a canonical public URL: {loc}')
            continue
        rel = unquote(url.path.removeprefix('/Zone1/')) or 'index.html'
        target = root / rel
        members.add(target)
        if target not in parsed or any('noindex' in value for value in parsed[target].robots):
            errors.append(f'sitemap: missing/noindex target: {rel}')
    counts['sitemap_urls'] = len(members)
    indexable_files = {file for file, page in parsed.items()
                       if page.robots and all('noindex' not in value for value in page.robots)}
    if members != indexable_files:
        errors.append('sitemap membership does not equal the indexable HTML set')
    return counts, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    counts, errors = verify(args.root)
    print(json.dumps(counts, sort_keys=True))
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print('Staged Pages artifact verified (offline structural checks).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
