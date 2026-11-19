import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublishedIntegrationOutputTests(unittest.TestCase):
    def test_homepage_starts_with_buyer_choices_and_groups_owner_tools(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("Choose the shape that fits your kitchen.", html)
        self.assertLess(html.index("publication-hero"), html.index("publication-product"))
        self.assertIn('<details class="workspace-menu">', html)
        self.assertEqual(1, html.count('class="workspace-menu"'))
        self.assertIn('<h5>Owner workspace</h5>', html)
        self.assertNotIn('class="sidebar"', html)
        self.assertLess(html.index('</header>'), html.index('class="disclosure-bar"'))
        self.assertLess(html.index('class="disclosure-bar"'), html.index('<main'))
        nav_start = html.index('<nav class="workspace-links"')
        nav = html[nav_start:html.index('</nav>', nav_start)]
        foot = html[html.index('<footer class="site">'):html.index('</footer>')]
        for page in ("product-intent.html", "measurement.html", "questions.html", "decision-log.html",
                     "suggestions.html", "executive-summary.html", "flagged.html", "compliance.html"):
            self.assertIn(f'href="{page}"', nav)
            self.assertIn(f'href="{page}"', foot)

    def test_homepage_leads_with_products_and_keeps_disclosure_beside_every_cta(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        main = html[html.index("<main"):html.index("</main>")]
        # Disclosure strip under the masthead, above the main content, and again in the footer.
        self.assertLess(html.index('class="disclosure-bar"'), html.index("<main"))
        self.assertGreater(html.index("As an Amazon Associate I earn from qualifying purchases.",
                                      html.index('<footer class="site">')), 0)
        # Homepage cards open useful local guides rather than adding unconfirmed
        # one-click product CTAs. All actual product routes retain conspicuous link notes.
        self.assertEqual(3, main.count('class="card pcard publication-product"'))
        for slug in ('chefman-6qt-dual-basket', 'emeril-26qt-french-door', 'chefman-8qt-turbofry'):
            self.assertIn(f'href="products/{slug}.html"', main)
            product = (ROOT / 'products' / (slug + '.html')).read_text(encoding='utf-8')
            self.assertIn('Affiliate link · intended listing and attribution unconfirmed.', product)
            self.assertIn('View on Amazon', product)
            self.assertIn('rel="sponsored nofollow noopener"', product)

    def test_price_note_cites_the_clause_that_governs_prices(self):
        # F90: the note used to say 2(b) *and* 6(t) bar Amazon prices; 6(t) is about reviews.
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("§2(b) and §6(t) bar", html)
        self.assertNotIn("§2(b) and §6(t) bar", (ROOT / "products/chefman-6qt-dual-basket.html").read_text())
        policy = json.loads((ROOT / "data/products.json").read_text())["amazon_price_policy"]
        self.assertIn("no authorised", policy)

    def test_category_count_reads_the_recorded_browse_path(self):
        # F91: the category lede published "0 of the five links" while three landed on air fryers.
        intent = json.loads((ROOT / "data/product-intent.json").read_text(encoding="utf-8"))
        n = sum(1 for r in intent["rows"]
                if r["observed_browse_path"].split("›")[-1].strip() == "Air Fryers")
        self.assertEqual(3, n)
        html = (ROOT / "categories/kitchen-appliances.html").read_text(encoding="utf-8")
        self.assertIn("Three returned air-fryer titles;", html)
        self.assertNotIn("0 of the five links", html)

    def test_link_intent_and_tracking_status_remain_unconfirmed(self):
        config = json.loads((ROOT / "data/config.json").read_text(encoding="utf-8"))
        intent = json.loads((ROOT / "data/product-intent.json").read_text(encoding="utf-8"))
        ledger = json.loads((ROOT / "data/campaign-ledger.json").read_text(encoding="utf-8"))
        self.assertEqual("", config["associate_tag"])
        self.assertEqual("shopnow047c-20", config["selected_tracking_id"])
        self.assertFalse(config["selected_tracking_id_associates_central_confirmed"])
        self.assertFalse(intent["tracking_id_applied_to_links"])
        self.assertEqual(5, len(intent["rows"]))
        for row in intent["rows"]:
            self.assertIsNone(row["intended_asin"])
            self.assertIsNone(row["official_listing_url"])
            self.assertIsNone(row["confirmation_date"])
            self.assertIsNone(row["confirmation_source"])
            self.assertFalse(row["associates_link_test_passed"])
        self.assertEqual([], ledger["rows"])

        html = (ROOT / "product-intent.html").read_text(encoding="utf-8")
        self.assertIn("user-provided", html)
        self.assertIn("not confirmed as active", html)
        self.assertIn("any supplied link", html)
        self.assertNotIn("?tag=shopnow047c-20", html)
        for row in intent["rows"]:
            self.assertIn(row["supplied_link"], html)

    def test_measurement_is_five_event_reference_only_and_explicit_about_pages(self):
        plan = json.loads((ROOT / "data/analytics-plan.json").read_text(encoding="utf-8"))
        html = (ROOT / "measurement.html").read_text(encoding="utf-8")
        names = {event["name"] for event in plan["events"]}
        self.assertEqual(
            {"page_view", "outbound_click", "article_engagement", "comparison_interaction", "affiliate_report_import"},
            names,
        )
        self.assertFalse(plan["collection"]["enabled"])
        self.assertFalse(plan["collection"]["endpoint_deployed"])
        self.assertFalse(plan["collection"]["privacy_notice_approved"])
        for phrase in ("GitHub Pages", "same-origin", "Host and proxy logs", "privacy", "Not active"):
            self.assertIn(phrase, html)
        self.assertNotIn('src="assets/analytics.js"', html)
        self.assertNotIn("data-analytics-event", html)


if __name__ == "__main__":
    unittest.main()
