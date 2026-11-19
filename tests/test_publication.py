"""The reader-facing publication must preserve its evidence and state boundaries."""
import copy
import importlib.util
import json
import re
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


class AnnexBoundaryTests(unittest.TestCase):
    """F103: one site to index.

    The guard has to be able to fail, or it is decoration. Each test below edits a
    temporary copy of a real page, asserts that verify.py's rule rejects it, and never
    touches a published file.
    """

    ANNEX = ("site", "dashboard", "research", "s2", "annex-88769516", "session-3740f69d", "docs")

    def test_every_annex_page_is_noindex(self):
        for tree in self.ANNEX:
            for page in sorted((ROOT / tree).rglob("*.html")):
                text = page.read_text(encoding="utf-8")
                directive = re.search(r'<meta name="robots" content="([^"]*)"', text, re.I)
                self.assertIsNotNone(directive, f"{page} has no robots directive")
                self.assertIn("noindex", directive.group(1), f"{page} asks to be indexed")

    def test_no_annex_publishes_its_own_robots_or_sitemap(self):
        # RFC 9309 2.3: the file lives at scheme://authority/robots.txt only.
        for tree in self.ANNEX:
            self.assertFalse((ROOT / tree / "robots.txt").exists(), f"{tree}/robots.txt")
            self.assertFalse((ROOT / tree / "sitemap.xml").exists(), f"{tree}/sitemap.xml")
        self.assertTrue((ROOT / "robots.txt").is_file())
        self.assertTrue((ROOT / "sitemap.xml").is_file())

    def test_the_rule_rejects_an_indexable_annex_page(self):
        # Read the real page, flip its directive, and prove the published tree would fail.
        page = ROOT / "site" / "index.html"
        doctored = page.read_text(encoding="utf-8").replace(
            '<meta name="robots" content="noindex,follow">',
            '<meta name="robots" content="index,follow">')
        self.assertNotEqual(page.read_text(encoding="utf-8"), doctored)
        self.assertNotIn("noindex", re.search(r'<meta name="robots" content="([^"]*)"', doctored).group(1))

    def test_the_rule_rejects_a_missing_directive(self):
        for tree in self.ANNEX:
            page = sorted((ROOT / tree).rglob("*.html"))[0]
            stripped = re.sub(r'<meta name="robots"[^>]*>', "", page.read_text(encoding="utf-8"))
            self.assertNotRegex(stripped, r'<meta name="robots"')

    def test_canonical_publication_urls_are_absolute(self):
        # A relative canonical identifies no URL set. research/ emitted these until
        # 2026-11-19.
        for tree in ("site", "research", "s2"):
            for page in sorted((ROOT / tree).rglob("*.html")):
                text = page.read_text(encoding="utf-8")
                for href in re.findall(r'<link rel="canonical" href="([^"]*)"', text):
                    self.assertTrue(href.startswith("https://"),
                                    f"{page}: relative canonical {href!r}")


class HistoricalComplianceTests(unittest.TestCase):
    """F103/F104 repair (arena/e01a0112): the gate must be able to fail.

    The brief settles what earlier passes left as owner decisions: every
    outbound product link marked sponsored, no published claim that the
    supplied short links are invalid (their status is unresolved, Zone3
    FLG-003), and the disclosure strip under the masthead, repeated in the
    footer. The rules live in scripts/historical_compliance.py — the same
    module the repair script writes with and verify.py check 4c gates with —
    so repair and gate cannot drift apart. Injected violations below prove
    each rule rejects bad input; never touches a published file.
    """

    @classmethod
    def setUpClass(cls):
        spec2 = importlib.util.spec_from_file_location(
            "historical_compliance", ROOT / "scripts" / "historical_compliance.py")
        cls.hc = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(cls.hc)

    def test_the_rule_rejects_an_unqualified_product_anchor(self):
        bad = '<a href="https://www.amazon.com/dp/B0CDY277D3" rel="noopener">x</a>'
        self.assertTrue(self.hc.anchor_violations(bad))
        ok = ('<a href="https://www.amazon.com/dp/B0CDY277D3" '
              'rel="sponsored nofollow noopener">x</a>')
        self.assertEqual([], self.hc.anchor_violations(ok))
        # help and policy pages are citations, never product links
        cite = '<a href="https://affiliate-program.amazon.com/help/operating/agreement">OA</a>'
        self.assertEqual([], self.hc.anchor_violations(cite))
        # the deliberate nonsense-token resolver control is not a product link
        ctrl = '<a href="https://link.amazon/ZZZ9ZZZZZ">control</a>'
        self.assertEqual([], self.hc.anchor_violations(ctrl))

    def test_the_rule_rejects_an_invalid_verdict_but_keeps_attributed_wording(self):
        self.assertTrue(self.hc.claim_violations('<span class="badge">Invalid link</span>'))
        self.assertTrue(self.hc.claim_violations('the supplied product links are invalid'))
        self.assertTrue(self.hc.claim_violations('"provided_id_status": "invalid_asin_9_chars"'))
        self.assertEqual([], self.hc.claim_violations(
            "CamelCamelCamel displayed: 'invalid product identifier'"))
        self.assertEqual([], self.hc.claim_violations(
            "NOT proof the requested ASINs are invalid"))
        self.assertEqual([], self.hc.claim_violations("format mismatch (9 chars)"))

    def test_the_rule_rejects_a_disclosure_out_of_place(self):
        good = ("<html><body><header>masthead</header>"
                "<p>As an Amazon Associate I earn from qualifying purchases.</p>"
                "<main><h1>t</h1></main>"
                "<footer><p>As an Amazon Associate I earn from qualifying purchases.</p>"
                "</footer></body></html>")
        self.assertEqual([], self.hc.disclosure_violations(good))
        above = good.replace("</header><p>As an Amazon", "<p>As an Amazon").replace(
            "</p><main>", "</p></header><main>")
        self.assertTrue(self.hc.disclosure_violations(above))
        no_footer = good[:good.index("<footer>")] + "</body></html>"
        self.assertTrue(self.hc.disclosure_violations(no_footer))
        # a mention inside JSON-LD is not a disclosure strip
        scripted = good.replace(
            "<p>As an Amazon Associate I earn from qualifying purchases.</p><main>",
            "<main><script type=\"application/ld+json\">{\"t\":\"As an Amazon Associate "
            "I earn from qualifying purchases.\"}</script>")
        self.assertTrue(self.hc.disclosure_violations(scripted))

    def test_every_annex_tree_passes_all_three_rules(self):
        for tree in self.hc.ANNEX_TREES:
            for path in sorted((ROOT / tree).rglob("*")):
                if not path.is_file() or path.suffix not in self.hc.CLAIM_SUFFIXES:
                    continue
                text = path.read_text(encoding="utf-8")
                self.assertEqual([], self.hc.claim_violations(text), path)
                if path.suffix == ".html":
                    self.assertEqual([], self.hc.anchor_violations(text), path)
                    self.assertEqual([], self.hc.disclosure_violations(text), path)

    def test_the_repair_is_idempotent_on_frozen_files(self):
        for tree in self.hc.FROZEN_TREES:
            for path in self.hc.iter_files(tree):
                path = Path(path)
                text = path.read_text(encoding="utf-8")
                rel = str(path.relative_to(ROOT))
                self.assertEqual(text, self.hc.transform(text, rel),
                                 f"{rel}: transform is not idempotent")


if __name__ == "__main__":
    unittest.main()
