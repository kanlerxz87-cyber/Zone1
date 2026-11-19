"""Browser-style contracts for the canonical output (not independent archives)."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from analytics.collector import allowed_page_ids, validate_payload

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://kanlerxz87-cyber.github.io/Zone1/"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."


def publication_pages():
    paths = list(ROOT.glob("*.html"))
    for directory in ("products", "categories", "guides", "articles"):
        paths.extend((ROOT / directory).glob("*.html"))
    return {str(path.relative_to(ROOT)): path.read_text(encoding="utf-8") for path in paths
            if 'data-page-id=' in path.read_text(encoding="utf-8")}


class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.items = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.items.append((tag, dict(attrs)))


class PublicationOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = publication_pages()

    def test_disclosure_sits_under_masthead_before_content_and_repeats_in_footer(self):
        for page, text in self.pages.items():
            with self.subTest(page=page):
                masthead = text.index('</header>')
                band = text.index('class="disclosure-bar"')
                main = text.index('<main id="main-content">')
                self.assertLess(masthead, band)
                self.assertLess(band, main)
                self.assertIn(DISCLOSURE, text[band:main])
                self.assertIn(DISCLOSURE, text[text.index('<footer class="site">'):])
                self.assertNotIn('class="sidebar"', text)

    def test_browser_url_resolution_never_escapes_subpath_or_names_missing_file(self):
        for page, text in self.pages.items():
            for tag, attrs in Elements(text).items:
                for attr in ("href", "src"):
                    ref = attrs.get(attr, "")
                    if not ref or ref.startswith(("data:", "mailto:")):
                        continue
                    url = urlsplit(urljoin(BASE + page, ref))
                    if url.netloc != "kanlerxz87-cyber.github.io":
                        continue
                    # Other repositories may be cited as external evidence, not local navigation.
                    if urlsplit(ref).netloc and not url.path.startswith('/Zone1/'):
                        continue
                    with self.subTest(page=page, reference=ref):
                        self.assertTrue(url.path.startswith('/Zone1/'), ref)
                        rel = unquote(url.path[len('/Zone1/'):])
                        target = ROOT / (rel or 'index.html')
                        if target.is_dir():
                            target /= 'index.html'
                        self.assertTrue(target.is_file(), ref)

    def test_every_outbound_product_anchor_is_commercially_qualified(self):
        for page, text in self.pages.items():
            for tag, attrs in Elements(text).items:
                if tag != 'a':
                    continue
                url = urlsplit(attrs.get('href', ''))
                is_product = (url.hostname == 'link.amazon' and 'ZZZ9ZZZZZ' not in url.path) or (
                    url.hostname in {'amazon.com', 'www.amazon.com'} and
                    url.path.startswith(('/dp/', '/gp/product/')))
                if is_product:
                    with self.subTest(page=page, href=attrs['href']):
                        self.assertTrue({'sponsored', 'nofollow', 'noopener'}.issubset(set(attrs.get('rel', '').split())))

    def test_collector_page_allowlist_matches_every_eligible_rendered_page(self):
        eligible = set()
        for page, text in self.pages.items():
            body = next(attrs for tag, attrs in Elements(text).items if tag == 'body')
            if body.get('data-analytics-eligible') == 'true':
                page_id = body['data-page-id']
                eligible.add(page_id)
                validate_payload({'event': 'page_view', 'page_id': page_id})
            self.assertNotRegex(text, r'<script[^>]+src="[^"]*assets/analytics\.js"')
        self.assertEqual(allowed_page_ids(), eligible)

    def test_homepage_has_three_real_filter_choices_and_sourced_8qt_dimensions(self):
        home = self.pages['index.html']
        for choice in ('all', 'dual', 'single', 'oven'):
            self.assertIn(f'data-format-filter="{choice}"', home)
        self.assertEqual(3, sum(1 for tag, attrs in Elements(home).items if 'publication-product' in attrs.get('class', '').split()))
        self.assertIn('15.4 × 12.6 × 13.5 in', home)
        self.assertIn('AI-generated editorial scene', home)
        self.assertIn('not a product image or test kitchen.', home)
        self.assertNotIn('kitchen-counter.webp', home)
        self.assertFalse((ROOT / 'assets/editorial/kitchen-counter.webp').exists())

    def test_owner_and_unconfirmed_notes_stay_out_of_sitemap(self):
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        for path in ('product-intent.html', 'measurement.html', 'suggestions.html', 'decision-log.html',
                     'categories/cooking-thermometers.html'):
            self.assertIn('content="noindex,follow"', self.pages[path])
            self.assertNotIn(BASE + path, sitemap)
        self.assertIn(BASE + 'about.html', sitemap)
        self.assertEqual(25, len(json.loads((ROOT / 'data/articles.json').read_text())['articles']))

    def test_robots_gives_search_engines_one_site_to_index(self):
        # SG-44 option A / the brief's "make it findable" ask: the seven parallel
        # annex builds stay publicly readable evidence but are not for indexing, and
        # workspace pages stay crawlable so their noindex meta can be read.
        robots = (ROOT / 'robots.txt').read_text(encoding='utf-8')
        for tree in ('research/', 'site/', 's2/', 'dashboard/', 'docs/',
                     'annex-88769516/', 'session-3740f69d/'):
            self.assertIn(f'Disallow: /{tree}\n', robots)
        self.assertIn(f'Sitemap: {BASE}sitemap.xml\n', robots)
        self.assertNotIn('Disallow: /\n', robots)
        self.assertNotIn('Disallow: /executive-summary.html', robots)

    def test_compare_page_opens_with_the_three_question_chooser(self):
        compare = self.pages['compare.html']
        self.assertIn('Which one is for you?', compare)
        chooser = compare.index('Which one is for you?')
        table = compare.index('comparison-table')
        self.assertLess(chooser, table)
        for slug in ('chefman-6qt-dual-basket', 'chefman-8qt-turbofry', 'emeril-26qt-french-door'):
            self.assertIn(f'href="products/{slug}.html"', compare)

    def test_authored_assets_are_published_verbatim_and_fonts_are_local(self):
        for source, output in (('publication/theme.css', 'assets/style.css'),
                               ('publication/site.js', 'assets/app.js'),
                               ('analytics/client.js', 'assets/analytics.js')):
            self.assertEqual((ROOT / source).read_bytes(), (ROOT / output).read_bytes())
        css = (ROOT / 'assets/style.css').read_text()
        self.assertNotIn('https://', css)
        fonts = re.findall(r'url\(["\']([^"\']+\.woff2)["\']\)', css)
        self.assertGreaterEqual(len(fonts), 2)
        for font in fonts:
            self.assertTrue((ROOT / 'assets' / font).is_file())
        for name in ('DM-Sans-LICENSE.txt', 'DM-Serif-Display-LICENSE.txt'):
            self.assertIn('SIL OPEN FONT LICENSE', (ROOT / 'assets/fonts' / name).read_text())


if __name__ == '__main__':
    unittest.main()
