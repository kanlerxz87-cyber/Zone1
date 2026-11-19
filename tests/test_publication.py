import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build
from analytics.collector import allowed_page_ids
from scripts.stage_pages import archive_html, qualify_product_links, stage

ROOT = Path(__file__).resolve().parents[1]


class PublicationGateTests(unittest.TestCase):
    def test_disclosure_is_below_masthead_before_content_and_repeated(self):
        page = build.page_index()
        self.assertEqual([], build.check_disclosure([('index.html', page)]))
        band = '<div class="disclosure-bar">'
        self.assertLess(page.index('</header>'), page.index(band))
        self.assertLess(page.index(band), page.index('<main'))
        self.assertTrue(build.check_disclosure([('bad.html', page.replace(band, '<div>'))]))
        self.assertTrue(build.check_disclosure([('bad.html', page.replace('<footer', '<div').replace('</footer>', '</div>'))]))

    def test_owner_links_are_in_one_menu_and_complete_footer_index(self):
        page = build.page_index()
        menu = page.split('<nav class="workspace-dropdown"', 1)[1].split('</nav>', 1)[0]
        footer = page.split('<nav aria-label="Footer workspace index">', 1)[1].split('</nav>', 1)[0]
        for href, _label in build.OWNER_LINKS:
            self.assertIn(f'href="{href}"', menu)
            self.assertIn(f'href="{href}"', footer)

    def test_unconfirmed_intent_never_becomes_purchase_cta(self):
        for product in build.PRODUCT_LIST:
            cta = build.product_cta(product)
            self.assertIn('cta-gated', cta)
            self.assertNotIn(f'href="{product["link"]}"', cta)
            intent = copy.deepcopy(build.PRODUCT_INTENT)
            record = next(row for row in intent['rows'] if row['supplied_link'] == product['link'])
            for key in ('confirmation_date', 'confirmation_source', 'associates_link_test_date', 'associates_link_test_source'):
                record[key] = 'TEST FIXTURE ONLY'
            # Matching a documented candidate is a conditional test, not an intent
            # assertion. The mock never writes into production records.
            record['intended_asin'] = product['asin']['v']
            record['official_listing_url'] = 'https://www.amazon.com/dp/' + record['intended_asin']
            record['associates_link_test_passed'] = True
            intent['tracking_id_associates_central_confirmed'] = True
            with patch.object(build, 'PRODUCT_INTENT', intent):
                confirmed = build.product_cta(product)
                self.assertIn('rel="sponsored nofollow noopener"', confirmed)
                self.assertIn('data-analytics-target-id', confirmed)
                # A future implementation still uses the original link unless separately changed;
                # the fixture never writes a guessed destination into production data.
                self.assertIn(f'href="{product["link"]}"', confirmed)
                record['intended_asin'] = 'DIFFERENT-INTENDED-MODEL'
                self.assertIn('cta-gated', build.product_cta(product), 'intent must match the guide, not just exist')

    def test_scrolling_tables_have_a_caption_named_keyboard_focus_target(self):
        table = '<div class="tablewrap"><table><caption>Specifications &amp; gaps</caption><tr><td>Fixture</td></tr></table></div>'
        result = build.accessible_tables(table)
        self.assertIn('tabindex="0"', result)
        self.assertIn('role="region"', result)
        self.assertIn('aria-label="Specifications &amp; gaps"', result)
        self.assertEqual(result, build.accessible_tables(result))

    def test_published_main_guards_reject_flag_mismatches_and_orphaned_dashboards(self):
        self.assertTrue(build.check_flag_anchor_labels({'fixture.html': '<a href="flagged.html#f84">Flag F86</a>'}))
        html = build.page_index()
        self.assertEqual([], build.check_desk_nav({'index.html': html}))
        self.assertTrue(build.check_desk_nav({'index.html': html.replace('href="figures.html"', 'href="missing-fixture.html"')}))

    def test_editorial_art_is_labeled_and_no_rating_schema_is_invented(self):
        html = build.page_index()
        self.assertIn('AI-generated editorial illustration', html)
        self.assertIn('not to scale', html)
        self.assertNotIn('"aggregateRating"', html)
        self.assertNotIn('"@type":"Review"', html)
        self.assertTrue((ROOT / 'assets/editorial/kitchen-counter.webp').is_file())

    def test_correction_is_dated_and_does_not_erase_the_source_conflict(self):
        article = next(a for a in build.ARTICLES['articles'] if a['slug'] == 'extension-cord-rules-in-the-manuals')
        self.assertEqual('2026-11-19', article['updated'])
        self.assertIn('Correction, 19 November 2026', json.dumps(article))
        self.assertIn('Attaching the Power Cord', json.dumps(article))
        self.assertNotIn('the rule is absolute', json.dumps(article))


class EnabledBuildGateTests(unittest.TestCase):
    def patches(self, endpoint='/api/analytics/events', ready=True, config_enabled=True, plan_enabled=True):
        plan = copy.deepcopy(build.ANALYTICS_PLAN)
        collection = plan['collection']
        collection['enabled'] = plan_enabled
        for key in ('runtime_selected', 'endpoint_deployed', 'privacy_notice_approved', 'host_logging_reviewed', 'end_to_end_verified'):
            collection[key] = ready
        return patch.multiple(build, ANALYTICS_PLAN=plan, ANALYTICS_ENABLED=config_enabled,
                              ANALYTICS_ENDPOINT=endpoint, ANALYTICS_ON=config_enabled and bool(endpoint))

    def test_switches_runtime_privacy_logging_and_receipt_are_required(self):
        with self.patches(ready=False):
            self.assertTrue(any('deployment gates' in x for x in build.check_analytics_consistency({})))
        with self.patches(config_enabled=False, plan_enabled=True):
            self.assertTrue(any('switches disagree' in x for x in build.check_analytics_consistency({})))
        with self.patches():
            self.assertEqual([], build.check_analytics_consistency({}))

    def test_endpoint_must_be_the_fixed_same_origin_https_route(self):
        for endpoint in ('//foreign.test/api/analytics/events', 'https://foreign.test/api/analytics/events',
                         '/api/analytics/events?x=1', '/api/analytics/events#x', '/other',
                         'http://kanlerxz87-cyber.github.io/api/analytics/events',
                         'https://user@kanlerxz87-cyber.github.io/api/analytics/events', 'relative/events'):
            with self.subTest(endpoint=endpoint), self.patches(endpoint=endpoint):
                self.assertTrue(build.check_analytics_consistency({}))
        for endpoint in ('/api/analytics/events', 'https://kanlerxz87-cyber.github.io/api/analytics/events'):
            with self.subTest(endpoint=endpoint), self.patches(endpoint=endpoint):
                self.assertEqual([], build.check_analytics_consistency({}))

    def test_enabled_emission_covers_reader_pages_only_and_collector_accepts_ids(self):
        paths = ['index.html', 'about.html', 'articles/index.html', 'compare.html',
                 'articles/air-fryer-capacity-guide.html', 'guides/buying-guide-air-fryers.html',
                 'products/chefman-8qt-turbofry.html', 'workspace.html', 'measurement.html',
                 '404.html', 'categories/meat-thermometers.html']
        with self.patches():
            pages = {rel: build.layout(rel, 'Fixture', '<h1>Isolated deployment fixture</h1>') for rel in paths}
            self.assertEqual([], build.check_analytics_consistency(pages))
            for rel, html in pages.items():
                emitted = 'data-collection="enabled"' in html
                self.assertEqual(build.is_indexable_page(rel), emitted)
                if emitted:
                    self.assertIn(rel[:-5], allowed_page_ids())
        self.assertFalse(build.ANALYTICS_ON)  # mock state is restored, production remains off

    def test_definition_drift_fails_before_deployment(self):
        data = copy.deepcopy(build.MEASUREMENT)
        data['events'][2]['fires_when'] = 'A different trigger'
        with patch.object(build, 'MEASUREMENT', data):
            self.assertTrue(any('disagree' in x for x in build.check_analytics_consistency({})))


class StagingTests(unittest.TestCase):
    def test_product_anchors_include_citations_but_not_policy_help_or_spoofed_hosts(self):
        for href in ('https://link.amazon/B04G1MEwY', 'https://www.amazon.com/dp/EXAMPLE',
                     'https://amazon.com/gp/product/EXAMPLE', 'https://www.amazon.com/model-name/dp/EXAMPLE',
                     'https://www.amazon.com/product-reviews/EXAMPLE'):
            original = f'<a class="src" href="{href}" rel="noopener">Official product source</a>'
            output = qualify_product_links(original)
            self.assertIn('sponsored', output)
            self.assertEqual(output, qualify_product_links(output))
        for href in ('https://amazon.com.evil.test/dp/EXAMPLE', 'https://link.amazon/ZZZ9ZZZZZ',
                     'https://affiliate-program.amazon.com/help/operating/policies'):
            original = f'<a href="{href}">Official source</a>'
            self.assertEqual(original, qualify_product_links(original))

    def test_archive_transform_preserves_body_and_source_date_without_collecting(self):
        original = ('<html><head><meta name="robots" content="index,follow"></head>'
                    '<body><header>Old title</header><main>Historical claim, 2026-11-13.</main>'
                    '<script src="../assets/analytics.js" data-endpoint="/api/analytics/events"></script></body></html>')
        transformed = archive_html(original)
        self.assertIn('content="noindex,follow"', transformed)
        self.assertIn('<main>Historical claim, 2026-11-13.</main>', transformed)
        self.assertLess(transformed.index('</header>'), transformed.index('<aside'))
        self.assertIn(build.DISCLOSURE, transformed)
        self.assertNotIn('src="../assets/analytics.js"', transformed)
        self.assertEqual(transformed, archive_html(transformed))

    def test_staging_does_not_change_archival_sources_or_copy_private_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'repo'
            root.mkdir()
            for path, text in {
                'index.html': '<head><meta name="robots" content="index,follow"></head><body><header>Current</header></body>',
                'research/index.html': '<head></head><body><header>Archived</header>Old claims</body>',
                '.private/credentials.json': '{"not":"public"}',
                'analytics/collector.py': '# runtime, not a public asset',
            }.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text)
            files = [str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()]
            original = (root / 'research/index.html').read_bytes()
            output = Path(temp) / 'public'
            counts = stage(output, root=root, files=files)
            self.assertEqual(1, counts['archived_html'])
            self.assertEqual(1, counts['indexable_html'])
            self.assertEqual(original, (root / 'research/index.html').read_bytes())
            self.assertIn('noindex', (output / 'research/index.html').read_text())
            self.assertFalse((output / '.private/credentials.json').exists())
            self.assertFalse((output / 'analytics/collector.py').exists())
            with self.assertRaises(ValueError):
                stage(root, root=root, files=[])
            with self.assertRaises(ValueError):
                stage(output, root=root, files=[])


if __name__ == '__main__':
    unittest.main()
