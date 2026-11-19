import copy
import unittest
from unittest.mock import patch

import build


class IntentAndTrackingGateTests(unittest.TestCase):
    def test_current_unverified_id_is_recorded_but_not_applied(self):
        self.assertEqual([], build.check_intent_measurement_contract())
        self.assertEqual("", build.SITE_CONFIG.get("associate_tag"))
        self.assertFalse(build.PRODUCT_INTENT["tracking_id_applied_to_links"])
        self.assertTrue(all(row["intended_asin"] is None for row in build.PRODUCT_INTENT["rows"]))

    def test_rejects_tag_before_account_confirmation_and_per_product_tests(self):
        config = copy.deepcopy(build.SITE_CONFIG)
        intent = copy.deepcopy(build.PRODUCT_INTENT)
        config["associate_tag"] = config["selected_tracking_id"]
        config["selected_tracking_id_associates_central_confirmed"] = False
        intent["tracking_id_applied_to_links"] = True
        intent["tracking_id_associates_central_confirmed"] = False

        with patch.object(build, "SITE_CONFIG", config), patch.object(build, "PRODUCT_INTENT", intent):
            problems = build.check_intent_measurement_contract()

        self.assertTrue(any("confirmed in Associates Central" in issue for issue in problems))
        self.assertTrue(any("before intended listing confirmation" in issue for issue in problems))
        self.assertTrue(any("enrolled-Associates test is recorded" in issue for issue in problems))

    def test_accepts_tag_only_after_every_confirmed_product_test(self):
        config = copy.deepcopy(build.SITE_CONFIG)
        intent = copy.deepcopy(build.PRODUCT_INTENT)
        config["associate_tag"] = config["selected_tracking_id"]
        config["selected_tracking_id_associates_central_confirmed"] = True
        intent["tracking_id_applied_to_links"] = True
        intent["tracking_id_associates_central_confirmed"] = True
        for index, row in enumerate(intent["rows"], start=1):
            # Deliberately use synthetic values; the test never copies an observed target
            # into an intended field or represents a real Associates Central check.
            row["intended_asin"] = f"fixture-{index}"
            row["official_listing_url"] = f"https://example.invalid/listing-fixture-{index}"
            row["confirmation_date"] = "2026-11-17"
            row["confirmation_source"] = "unit-test fixture only"
            row["associates_link_test_passed"] = True
            row["associates_link_test_date"] = "2026-11-17"
            row["associates_link_test_source"] = "unit-test fixture only"

        with patch.object(build, "SITE_CONFIG", config), patch.object(build, "PRODUCT_INTENT", intent):
            self.assertEqual([], build.check_intent_measurement_contract())


class RequirementPathGateTests(unittest.TestCase):
    def test_rejects_directory_references_that_github_pages_cannot_serve(self):
        requirements = copy.deepcopy(build.REQUIREMENTS)
        requirements["requirements"][0]["where"] = ["platform/"]
        requirements["requirements"][0]["evidence"] = [
            {"label": "fixture", "url": "platform/tests/"}
        ]

        with patch.object(build, "REQUIREMENTS", requirements):
            problems = build.check_requirement_paths()

        self.assertTrue(any("implementation path must name a file" in issue for issue in problems))
        self.assertTrue(any("evidence link must name a file" in issue for issue in problems))


class RetainedIntegrationGuardTests(unittest.TestCase):
    def test_flag_label_must_match_its_actual_fragment(self):
        self.assertTrue(build.check_flag_anchor_labels({"fixture.html":
            '<a href="flagged.html#f84">Flag F86</a>'}))
        self.assertEqual([], build.check_flag_anchor_labels({"fixture.html":
            '<a href="flagged.html#f86">Flag F86</a>'}))

    def test_explicit_owner_inventory_cannot_drop_a_nav_route(self):
        with patch.object(build, "DESK_NAV", [path for path in build.DESK_NAV if path != "figures.html"]):
            problems = build.check_desk_nav({})
        self.assertTrue(any("figures.html" in issue for issue in problems))


if __name__ == "__main__":
    unittest.main()
