import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublishedIntegrationOutputTests(unittest.TestCase):
    def test_homepage_starts_with_buyer_choices_and_groups_owner_tools(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("Choose the shape that fits your kitchen.", html)
        self.assertLess(html.index("publication-hero"), html.index("publication-product"))
        # Pass 14 (arena/9b3365c7-zone1): the brief asks for every dashboard surface to be
        # reachable "from the footer and a single navigation group". Both are asserted here.
        self.assertIn("<h4>Behind the site</h4>", html)
        self.assertIn("<h5>Behind the site</h5>", html)
        self.assertEqual(1, html.count("<h4>Behind the site</h4>"))
        self.assertNotIn("<h4>Owner workspace</h4>", html)
        self.assertNotIn("<h4>Trust &amp; evidence</h4>", html)
        nav = html[html.index('<nav id="site-nav"'):html.index("</nav>", html.index('<nav id="site-nav"'))]
        foot = html[html.index('<footer class="site">'):html.index("</footer>")]
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
        ctas = [m for m in main.split("<a ") if "link.amazon/" in m and 'class="src"' not in m]
        self.assertEqual(3, len(ctas))
        for tag in ctas:
            self.assertIn("sponsored", tag.split(">")[0])
            self.assertIn("Amazon", tag)            # Program Policies 6(w): clear it goes to Amazon
        self.assertEqual(3, main.count("Sponsored link — we may earn a commission"))

    def test_price_note_cites_the_clause_that_governs_prices(self):
        # F90: the note used to say 2(b) *and* 6(t) bar Amazon prices; 6(t) is about reviews.
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("§2(b) and §6(t) bar", html)
        self.assertIn("Associates Program Policies §2(b) allow", html)

    def test_category_count_reads_the_recorded_browse_path(self):
        # F91: the category lede published "0 of the five links" while three landed on air fryers.
        intent = json.loads((ROOT / "data/product-intent.json").read_text(encoding="utf-8"))
        n = sum(1 for r in intent["rows"]
                if r["observed_browse_path"].split("›")[-1].strip() == "Air Fryers")
        self.assertEqual(3, n)
        html = (ROOT / "categories/kitchen-appliances.html").read_text(encoding="utf-8")
        self.assertIn("Three of the five links submitted", html)
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
