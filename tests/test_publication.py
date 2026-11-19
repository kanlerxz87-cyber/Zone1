"""The reader-facing publication must preserve its evidence and state boundaries."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("publication_build", ROOT / "build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class PublicationDataTests(unittest.TestCase):
    def test_current_publication_and_state_partition_pass(self):
        self.assertEqual([], build.check_publication_data())
        rows = build.SUGGESTIONS["suggestions"]
        states = {"complete", "partial", "gated", "superseded", "open"}
        self.assertEqual(len(rows), sum(sum(r["current_state"] == s for r in rows) for s in states))
        self.assertEqual([], build.DECISION_LOG["choices"])
        self.assertEqual([], build.CAMPAIGN_LEDGER["rows"])

    def test_a_stale_or_missing_current_state_is_a_build_error(self):
        suggestions = copy.deepcopy(build.SUGGESTIONS)
        del suggestions["suggestions"][0]["current_state"]
        self.assertTrue(build.check_publication_data(suggestions=suggestions))
        suggestions["suggestions"][0]["current_state"] = "deployed-probably"
        self.assertTrue(build.check_publication_data(suggestions=suggestions))

    def test_display_copy_cannot_orphan_a_product_guide_or_source(self):
        publication = copy.deepcopy(build.PUBLICATION)
        publication["products"][0]["slug"] = "unregistered-model"
        self.assertTrue(build.check_publication_data(publication=publication))
        publication = copy.deepcopy(build.PUBLICATION)
        publication["featured_guides"][0]["slug"] = "imaginary-guide"
        self.assertTrue(build.check_publication_data(publication=publication))
        publication = copy.deepcopy(build.PUBLICATION)
        publication["thermometer_links"][0]["sources"] = ["S000000"]
        self.assertTrue(build.check_publication_data(publication=publication))


class DirectEvidenceGateTests(unittest.TestCase):
    def test_flag_summary_and_arbitrary_official_host_are_not_row_sources(self):
        for href in ("flagged.html", "flagged.html#f96", "https://chefman.com/not-a-registered-source",
                     "https://github.com/somebody/another-repo/blob/main/file.txt",
                     build.REPO_BLOB + "file-that-does-not-exist.md"):
            with self.subTest(href=href):
                self.assertFalse(build.row_is_sourced(f'<a href="{href}">source</a>'))

    def test_registered_primary_and_existing_repository_records_pass(self):
        for href in (build.SRC_BY_ID["S15"]["url"], build.REPO_BLOB + "data/publication.json",
                     build.PRODUCT_INTENT["rows"][1]["supplied_link"]):
            self.assertTrue(build.row_is_sourced(f'<a href="{href}">evidence</a>'))

    def test_row_header_is_not_a_source_gate_bypass(self):
        invalid = '<table><tbody><tr><th scope="row">Capacity</th><td>26 qt</td></tr></tbody></table>'
        self.assertTrue(build.check_row_sources({"compare.html": invalid}))
        valid = invalid.replace("26 qt", '26 qt ' + build.src_link("S15"))
        self.assertEqual([], build.check_row_sources({"compare.html": valid}))


class PublishedReaderBoundaryTests(unittest.TestCase):
    def test_all_reader_routes_have_honest_method_no_projection_and_one_workspace(self):
        reader = [ROOT / "index.html", ROOT / "compare.html", ROOT / "picks.html", ROOT / "about.html"]
        for folder in ("articles", "products", "categories", "guides"):
            reader.extend((ROOT / folder).glob("*.html"))
        for path in reader:
            content = path.read_text()
            with self.subTest(page=str(path.relative_to(ROOT))):
                self.assertEqual(1, content.count('class="workspace-menu"'))
                self.assertIn("AI-assisted", content)
                self.assertIn("no hands-on", content.lower())
                self.assertNotIn("Revenue scenarios", content)
                self.assertNotIn('id="rev-calc"', content)
                self.assertNotIn('class="sidebar"', content)
                self.assertEqual([], build.check_disclosure([(str(path), content)]))

    def test_sources_and_generated_presentation_assets_do_not_drift(self):
        for source, output in (("publication/theme.css", "assets/style.css"),
                               ("publication/site.js", "assets/app.js"),
                               ("analytics/client.js", "assets/analytics.js")):
            self.assertEqual((ROOT / source).read_bytes(), (ROOT / output).read_bytes())

    def test_article_publication_dates_are_not_fabricated_from_access_dates(self):
        items = ET.parse(ROOT / "feed.xml").findall("./channel/item")
        self.assertEqual(len(build.ARTICLES["articles"]), len(items))
        for article, item in zip(build.ARTICLES["articles"], items):
            if not article.get("published_at_utc"):
                self.assertIsNone(item.find("pubDate"))
            ld = build.article_jsonld(article, "https://example.invalid/article")
            if not article.get("published_on"):
                self.assertNotIn("datePublished", ld)
            self.assertEqual(article.get("modified_at"), ld.get("dateModified"))

    def test_disclosure_both_placements_and_order_are_enforced(self):
        correct = (ROOT / "index.html").read_text()
        self.assertEqual([], build.check_disclosure([("index.html", correct)]))
        no_footer = correct[:correct.index('<footer class="site">')] + "<footer>Footer</footer>"
        self.assertTrue(build.check_disclosure([("index.html", no_footer)]))
        reordered = correct.replace('</header>', '').replace('<main', '</header><main', 1)
        self.assertTrue(build.check_disclosure([("index.html", reordered)]))

    def test_flagged_intro_does_not_call_all_historical_findings_open_or_guess_a_model(self):
        text = build.page_flagged().split('<h2>Programme-level flags')[0]
        self.assertIn('Recorded findings', text)
        self.assertIn('not a count of currently open work', text)
        self.assertNotIn('>Open items<', text)
        self.assertNotIn('>Hard source conflicts<', text)
        self.assertNotIn('So this is most likely', text)
        self.assertIn('no “most likely” model explanation is selected', text)
        self.assertIn('F96', text)

    def test_known_content_corrections_remain_visible(self):
        extension = (ROOT / "articles/extension-cord-rules-in-the-manuals.html").read_text()
        self.assertIn("F96", extension)
        self.assertIn("incompatible", extension)
        care = (ROOT / "articles/aerosol-oil-warning.html").read_text()
        self.assertIn("single-basket manual also contains", care)
        energy = (ROOT / "articles/energy-cost-of-an-air-fryer.html").read_text()
        self.assertIn("not measured kilowatt-hours", energy)
        model = (ROOT / "articles/what-450f-actually-means.html").read_text()
        self.assertNotIn("which it is on all three listings", model)
        self.assertIn("conflict unresolved", model)


if __name__ == "__main__":
    unittest.main()
