"""Evidence/date and decision-state regressions; not semantic source verification."""
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import build

ROOT = Path(__file__).resolve().parents[1]


class EditorialMetadataTests(unittest.TestCase):
    def test_publication_date_is_never_filled_from_source_access(self):
        sample = dict(build.ARTICLES['articles'][0])
        sample['published_at'] = None
        sample['modified_at'] = '2026-11-19T06:15:51Z'
        node = build.article_jsonld(sample, 'https://example.invalid/article')
        self.assertNotIn('datePublished', node)
        self.assertEqual(sample['modified_at'], node['dateModified'])
        sample['published_at'] = '2026-11-16T10:15:00Z'  # synthetic fixture only
        self.assertEqual(sample['published_at'], build.article_jsonld(sample, 'https://example.invalid/article')['datePublished'])

    def test_rendered_articles_match_their_own_explicit_metadata(self):
        for article in build.ARTICLES['articles']:
            with self.subTest(slug=article['slug']):
                text = (ROOT / 'articles' / (article['slug'] + '.html')).read_text()
                graph = json.loads(text.split('<script type="application/ld+json">')[1].split('</script>')[0])['@graph']
                node = next(x for x in graph if x.get('@type') == 'Article')
                self.assertEqual(article['modified_at'], node['dateModified'])
                self.assertIsNone(article['published_at'])
                self.assertNotIn('datePublished', node)
                self.assertIn('first-publication timestamp is not established', text)
                self.assertIn('AI-assisted, document-based writing', text)
                self.assertNotIn('sources read 2026-11-14', text)
                for section in article['sections']:
                    self.assertTrue(section['cite'])
                for check in article['source_checks']:
                    self.assertTrue(check['ids'])
                    self.assertTrue(set(check['ids']).issubset(build.SRC_BY_ID))

    def test_rss_has_stable_guids_and_does_not_invent_original_publication_time(self):
        feed = ET.parse(ROOT / 'feed.xml').getroot().find('channel')
        self.assertTrue(feed.findtext('lastBuildDate'))
        items = feed.findall('item')
        self.assertEqual(len(build.ARTICLES['articles']), len(items))
        for item in items:
            self.assertIsNone(item.find('pubDate'))
            self.assertEqual(item.findtext('link'), item.findtext('guid'))
            self.assertEqual('true', item.find('guid').get('isPermaLink'))

    def test_current_guide_corrections_cannot_silently_regress(self):
        cord = json.dumps(build.ARTICLE_BY_SLUG['extension-cord-rules-in-the-manuals'], ensure_ascii=False)
        self.assertIn('contradicts itself', cord)
        self.assertIn('Do not rely on this article as permission', cord)
        oil = json.dumps(build.ARTICLE_BY_SLUG['aerosol-oil-warning'], ensure_ascii=False)
        self.assertIn('both Chefman manuals', oil)
        self.assertNotIn('No aerosol rule is recorded', oil)
        spit = json.dumps(build.ARTICLE_BY_SLUG['rotisserie-at-home'], ensure_ascii=False)
        self.assertIn('6 lb (2721 g)', spit)
        self.assertNotIn('a maximum rotisserie weight', spit)

    def test_suggestions_have_current_evidenced_states_not_effort_based_completion(self):
        suggestions = build.SUGGESTIONS['suggestions']
        for suggestion in suggestions:
            self.assertIn(suggestion['implementation']['state'], {'implemented', 'partial', 'proposed'})
            self.assertTrue(suggestion['implementation']['evidence'])
            self.assertGreaterEqual(len(suggestion['options']), 2)
        sg1 = next(x for x in suggestions if x['id'] == 'SG-01')
        self.assertEqual('partial', sg1['implementation']['state'])
        self.assertEqual([], build.DECISION_LOG['choices'])
        text = (ROOT / 'suggestions.html').read_text()
        self.assertEqual(len(suggestions), text.count(' data-suggestion>'))
        self.assertIn('data-suggestion-toolbar hidden', text)
        self.assertNotIn('Nothing on this page has been implemented', text)
        self.assertNotIn('class="score"', text)
        self.assertNotIn('score 25', text)

    def test_questions_summary_renders_every_citation_not_first_source_only(self):
        text = (ROOT / 'questions.html').read_text()
        summary = text.split('<tbody>')[1].split('</tbody>')[0]
        for question in build.QUESTIONS['questions']:
            row = next(row for row in summary.split('</tr>') if f'>{question["id"]}</a>' in row)
            for source in question['sources']:
                from html import escape
                self.assertIn(f'href="{escape(source["url"], quote=True)}"', row)


if __name__ == '__main__':
    unittest.main()
