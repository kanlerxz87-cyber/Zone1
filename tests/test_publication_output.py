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
        for path in ('product-intent.html', 'measurement.html', 'suggestions.html', 'decision-log.html'):
            self.assertIn('content="noindex,follow"', self.pages[path])
            self.assertNotIn(BASE + path, sitemap)
        self.assertIn(BASE + 'about.html', sitemap)
        # The article count was pinned at 26 here. A pinned count only says "a number
        # changed"; it does not say whether the change is a defect. It now asserts the
        # structural property the pin was standing in for: every guide in the register
        # has exactly one sitemap URL, and the guide index has one too. (Raised to the
        # current 27 by arena/915c51ea on 2026-11-20 when the hosting-week guide shipped.)
        articles = json.loads((ROOT / 'data/articles.json').read_text())['articles']
        slugs = [a['slug'] for a in articles]
        self.assertEqual(len(slugs), len(set(slugs)), 'two articles share a slug')
        for slug in slugs:
            self.assertEqual(1, sitemap.count(BASE + 'articles/' + slug + '.html'), slug)
        self.assertEqual(1, sitemap.count(BASE + 'articles/index.html'))

    def test_thermometer_pillar_and_both_product_pages_are_indexable(self):
        # Changed 2026-11-19 (arena/d154e428). The shelf began as dated link notes and was
        # correctly noindexed then. Two of the five supplied products are thermometers, and a
        # product a reader cannot reach from a search result is not a product page. Both now
        # have manufacturer-documented buyer pages, so the pillar and its two children are
        # buyer-facing and belong in the sitemap. The intent record stays out of it: that is
        # the owner's evidence surface, not a buying page.
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        pillar = 'categories/cooking-thermometers.html'
        self.assertIn('content="index,follow', self.pages[pillar])
        self.assertIn(BASE + pillar, sitemap)
        for slug in ('thermomaven-f1-turbo', 'chef-iq-sense-gen3'):
            page = 'products/' + slug + '.html'
            self.assertIn('content="index,follow', self.pages[page])
            self.assertIn(BASE + page, sitemap)
            self.assertNotIn(BASE + page, sitemap.replace(BASE + page, '', 1))
        self.assertIn('content="noindex,follow"', self.pages['product-intent.html'])

    def test_root_robots_is_authoritative_and_hides_nothing_the_annex_boundary_needs(self):
        # SG-44 option A / the brief's "make it findable" ask, implemented as the annex
        # noindex boundary (F105): one root-authoritative robots.txt that keeps out of the
        # way. Deliberately NO Disallow rules — a robots.txt block hides the noindex
        # directive the annex trees rely on (RFC 9309; Google's robots documentation).
        robots = (ROOT / 'robots.txt').read_text(encoding='utf-8')
        self.assertIn('User-agent: *\nAllow: /\n', robots)
        self.assertIn(f'Sitemap: {BASE}sitemap.xml\n', robots)
        self.assertNotIn('Disallow:', robots)
        self.assertFalse((ROOT / 'site' / 'robots.txt').exists())
        self.assertFalse((ROOT / 'dashboard' / 'sitemap.xml').exists())

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


    def test_the_decision_kit_cannot_force_horizontal_overflow(self):
        """Headless half of the browser gate for the component added 2026-11-20 (SG-53).

        `scripts/check_publication_browser.mjs` loads every product page at 320px and asserts
        `documentElement.scrollWidth <= width + 1`; `tests/browser/publication.spec.cjs` repeats the
        check at every configured viewport. Neither can run where a browser binary cannot be
        downloaded, so the first push of this component failed CI with no locally reproducible
        signal: the wide layout paired a fixed 150px label column with `white-space:nowrap` row
        links, which at 320px leaves a 60px content column and an unshrinkable link inside it.

        The rule that was actually broken is expressible without a browser, so it is asserted here:
        a text column in this component must be `minmax(0,1fr)` (able to shrink below its content),
        no rule in it may forbid wrapping, and it must collapse to one column on narrow screens.
        """
        css = (ROOT / "publication" / "theme.css").read_text(encoding="utf-8")
        start = css.index(".decision-kit{")
        end = css.index("@media(max-width:620px){.decision-kit", start)
        # Prose in the file's own comments describes the defect; only declarations are under test.
        kit = re.sub(r"/\*.*?\*/", " ", css[start:end], flags=re.S)
        self.assertNotIn("white-space:nowrap", kit, "an unbreakable link inside the kit")
        columns = re.findall(r"grid-template-columns:([^;}]+)", kit)
        self.assertTrue(columns, "the kit lost its grid rules entirely")
        for decl in columns:
            self.assertIn("minmax(0,1fr)", decl, f"grid column cannot shrink: {decl.strip()}")
        self.assertRegex(css[end:end + 500], r"\.dk-rows\{grid-template-columns:minmax\(0,1fr\)",
                         "the kit must stack its label above the text on narrow screens")

    def test_register_cards_break_long_tokens_before_they_widen_the_page(self):
        """The 320px failure this branch actually had, made unreproducible (2026-11-20).

        `tests/browser/publication.spec.cjs` sweeps every published page at 320px and asserts the
        document does not scroll sideways; `scripts/check_publication_browser.mjs` asserts the same
        on a shorter list that omits `questions.html`. New question rows put two bare URLs in
        `what_we_know`, and `.qcard` had no break rule, so one 86-character token pushed the
        document to 684px. The register text was corrected (URLs belong in `sources[]`, where they
        render as labelled links) AND the component now breaks long tokens, because the next editor
        should not be able to reproduce the defect from ordinary prose. `overflow-wrap` inherits, so
        the nested evidence links are covered by the same declaration.
        """
        css = (ROOT / "publication" / "theme.css").read_text(encoding="utf-8")
        bodies = [m.group(1) for m in re.finditer(r"\.sug,\.qcard[^{]*\{([^}]*)\}", css)]
        self.assertTrue(bodies, "no rule targets the register cards at all")
        self.assertTrue(any("overflow-wrap:anywhere" in b.replace(" ", "") for b in bodies),
                        f"the register cards lost their break rule: {bodies}")
        questions = json.loads((ROOT / "data" / "questions.json").read_text(encoding="utf-8"))["questions"]
        for row in questions:
            for field in ("question", "why_it_matters", "what_is_missing", "how_to_discover", "answer"):
                text = row.get(field)
                if isinstance(text, str):
                    self.assertNotIn("http", text, f"{row['id']}.{field} carries a bare URL in prose")
            for known in row.get("what_we_know", []):
                self.assertNotIn("http", known, f"{row['id']}.what_we_know carries a bare URL in prose")

if __name__ == '__main__':
    unittest.main()
