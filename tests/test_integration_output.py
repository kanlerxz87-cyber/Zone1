import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublishedIntegrationOutputTests(unittest.TestCase):
    def test_homepage_starts_with_buyer_choices_and_groups_owner_tools(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="home-title">Less guesswork.', html)
        self.assertIn("Three formats. Different jobs.", html)
        self.assertNotIn('class="sidebar"', html)
        self.assertLess(html.index("publication-hero"), html.index("publication-product"))
        self.assertIn("<h4>Owner workspace</h4>", html)
        self.assertIn("<h5>Owner &amp; dashboard index</h5>", html)
        for page in ("product-intent.html", "measurement.html", "questions.html", "decision-log.html"):
            self.assertIn(f'href="{page}"', html)

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
