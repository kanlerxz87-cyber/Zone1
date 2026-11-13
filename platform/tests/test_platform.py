"""Regression tests for every guard the site claims to enforce.

Run: python3 -m unittest discover -s platform/tests -t platform
Each test name references the rule id in data/program.json that it protects.
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _common import Status, is_official  # noqa: E402
from catalog.asin import parse_url, validate_asin  # noqa: E402
from compliance import gates  # noqa: E402
from content import lint  # noqa: E402
from content.claims_checker import audit_draft, no_income_promise  # noqa: E402
from model import economics  # noqa: E402
from model.attribution import Click, Order, qualifies  # noqa: E402
from pricing.source_guard import may_show_price  # noqa: E402
from research import intake, observe_redirect  # noqa: E402
from scoring import WEIGHTS, score  # noqa: E402
from templates.comparison import render as render_comparison  # noqa: E402
from training.gate import audit_dataset  # noqa: E402
from links.validator import validate as validate_link  # noqa: E402
import credentials  # noqa: E402
from audit.report import audit_data  # noqa: E402


class TestIdentifiers(unittest.TestCase):
    def test_CT1_asin_is_ten_characters(self):
        self.assertTrue(validate_asin("B0CDY277D3").usable)

    def test_CT1_nine_char_token_is_rejected(self):
        f = validate_asin("B04G1MEwY")
        self.assertFalse(f.usable)
        self.assertIs(f.status, Status.UNVERIFIED)
        self.assertIn("9 characters", f.note)

    def test_CT5_parse_dp_and_bare_token(self):
        self.assertEqual(parse_url("https://www.amazon.com/dp/B0CDY277D3?tag=z-20")["asin"], "B0CDY277D3")
        self.assertEqual(parse_url("https://link.amazon/B04G1MEwY")["candidate"], "B04G1MEWY")
        self.assertIsNone(parse_url("https://example.com/nothing")["asin"])

    def test_lookup_preserves_operator_casing(self):
        self.assertTrue(parse_url("https://link.amazon/B04G1MEwY")["lookup"].endswith("/dp/B04G1MEwY"))


class TestResolver(unittest.TestCase):
    def test_F07_fallback_redirect_is_not_attribution(self):
        rec = intake(["https://link.amazon/B04G1MEwY"])[0]
        rec = observe_redirect(
            rec,
            "https://www.amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&channelId=704&plpRedirect=mhFallback",
        )
        self.assertFalse(rec["attributable"])
        self.assertEqual(rec["fields"], {})
        self.assertIs(rec["record_status"], Status.UNVERIFIED)

    def test_genuine_resolution_is_accepted(self):
        from resolver.link import classify

        c = classify("https://www.amazon.com/dp/B0CDY277D3/ref=sr_1_1", wanted_asin="B0CDY277D3")
        self.assertTrue(c["attributable"])


class TestLinks(unittest.TestCase):
    def test_LK1_LK2_require_well_formed_tag(self):
        self.assertTrue(validate_link("https://www.amazon.com/dp/B000X?tag=zone1-20", expected_tag="zone1-20").ok)
        self.assertFalse(validate_link("https://www.amazon.com/dp/B000X", expected_tag="zone1-20").ok)
        self.assertFalse(validate_link("https://www.amazon.com/dp/B000X?tag=nofive").ok)

    def test_DQ3_shortener_is_a_redirector(self):
        rep = validate_link("https://bit.ly/abc")
        self.assertIn("DQ-3", [f.rule for f in rep.findings])

    def test_LK5_no_subtag_bound_to_a_person(self):
        from links.validator import no_per_user_tagging

        self.assertTrue(no_per_user_tagging("article-3", None))
        self.assertFalse(no_per_user_tagging("user-99123", "user-99123"))


class TestCompliance(unittest.TestCase):
    def test_FT8_requires_the_exact_sentence(self):
        self.assertTrue(gates.amazon_disclosure_exact(f"<p>{gates.AMAZON_DISCLOSURE}</p>"))
        self.assertFalse(gates.amazon_disclosure_exact("<p>We may earn commissions.</p>"))

    def test_FT6_buried_disclosure_fails(self):
        html = '<a href="/legal">DISCLOSURE</a><a href="https://www.amazon.com/dp/X?tag=a-20">buy</a>'
        rep = gates.audit_page(html, has_affiliate_link=True)
        self.assertFalse(rep.ok)

    def test_ID5_rejects_amazon_mark_in_tag(self):
        self.assertFalse(gates.no_amazon_mark_in_identity("amazon-deals-hub"))
        self.assertTrue(gates.no_amazon_mark_in_identity("kitchen-gear-lab"))

    def test_DQ1_reports_biddable_amazon_marks(self):
        self.assertEqual(gates.no_amazon_mark_bidding(["air fryer", "amazon deals"]), ["amazon deals"])

    def test_MB3_MB4_mobile_restrictions(self):
        self.assertFalse(gates.no_price_tracking(["price alert"]))
        self.assertFalse(gates.no_webview(["WebView"]))

    def test_MB5_paapi_needs_approval_for_mobile_first(self):
        self.assertFalse(gates.paapi_surface_ok(mobile_first=True))
        self.assertTrue(gates.paapi_surface_ok(mobile_first=True, written_approval=True))


class TestContent(unittest.TestCase):
    def test_RK6_income_promise_is_blocked(self):
        self.assertFalse(no_income_promise("You will earn up to 10% every month."))
        self.assertTrue(no_income_promise("Prices change on Amazon after publication."))

    def test_CN6_unsourced_number_is_blocked(self):
        rep = audit_draft("The unit holds 6 quarts and costs $79.93.", supported=[])
        self.assertIn("CN-6", [f.rule for f in rep.findings])

    def test_CN3_truncation_allowed_rewording_not(self):
        self.assertTrue(lint.no_altered_program_content("Chefman 6 Quart Dual Basket Air Fryer", "Chefman 6 Quart..."))
        self.assertFalse(lint.no_altered_program_content("Chefman 6 Quart Dual Basket Air Fryer", "Chefman 8 Quart Air Fryer"))

    def test_similarity_gate(self):
        from content.similarity import transformative_use_ok

        self.assertFalse(transformative_use_ok("great compact dual basket air fryer for families",
                                               "great compact dual basket air fryer for families"))
        self.assertTrue(transformative_use_ok("great compact dual basket air fryer",
                                               "two baskets let you cook a main and a side at once"))


class TestEconomics(unittest.TestCase):
    def test_AT6_qualifying_revenue_nets_deductions(self):
        m = economics.OrderMoney(99.99, {"taxes": 8.0, "shipping": 5.0})
        self.assertEqual(m.qualifying_revenue, 86.99)

    def test_unknown_deduction_raises(self):
        with self.assertRaises(ValueError):
            economics.OrderMoney(10.0, {"vibes": 1.0}).qualifying_revenue

    def test_MN2_refuses_to_invent_a_rate(self):
        with self.assertRaises(economics.RateNotAvailable):
            economics.commission(100.0, None)

    def test_MN5_MN7_payment_minimums(self):
        self.assertEqual(economics.payout_ready(9.99, "direct_deposit")[0], False)
        self.assertEqual(economics.payout_ready(10.0, "gift_card")[0], True)
        self.assertEqual(economics.payout_ready(99.0, "check")[0], False)

    def test_AT1_AT3_AT4_windows(self):
        self.assertFalse(qualifies(Click(0), Order(30, 40))[0])       # > 24h session
        self.assertTrue(qualifies(Click(0), Order(3, 20))[0])
        self.assertFalse(qualifies(Click(0), Order(3, 3, is_digital=True))[0])
        self.assertFalse(qualifies(Click(0), Order(3, 3, returned=True))[0])
        self.assertFalse(qualifies(Click(0, tag_is_own=False), Order(3, 4))[0])


class TestPricing(unittest.TestCase):
    def test_CN1_only_approved_sources_may_show_a_price(self):
        self.assertFalse(may_show_price("scrape", "scrape"))
        self.assertFalse(may_show_price("third_party_blog", "third_party_blog"))
        self.assertTrue(may_show_price("pa_api", "pa_api"))
        self.assertTrue(may_show_price("special_link_served_by_amazon", "special_link_served_by_amazon"))

    def test_CN2_comparison_requires_lowest_new(self):
        _html, rep = render_comparison([{"name": None, "price_new": None}])
        self.assertIn("CN-2", [f.rule for f in rep.findings])
        self.assertIn("not verified", _html)


class TestModel(unittest.TestCase):
    def test_R07_partial_input_refuses_to_score(self):
        res = score({"demand": 0.8})
        self.assertIsNone(res.score)
        self.assertIn("competition", res.missing)

    def test_R07_complete_input_scores_deterministically(self):
        rec = {"demand": 0.8, "competition": 0.6, "price_band": 0.5, "review_quality": 0.7, "commission": 0.4}
        self.assertAlmostEqual(score(rec).score, sum(rec[k] * WEIGHTS[k] for k in WEIGHTS), places=4)


class TestSafety(unittest.TestCase):
    def test_F08_missing_credentials_skip_rather_than_simulate(self):
        st = credentials.detect({})
        self.assertIs(st.status, Status.SKIPPED_NO_CREDENTIALS)
        self.assertFalse(st.can_publish_links)
        self.assertIn("AMAZON_ASSOCIATE_TAG", st.missing())

    def test_placeholder_credentials_are_not_credentials(self):
        st = credentials.detect({
            "AMAZON_ASSOCIATE_TAG": "your-tag-20",
            "AMAZON_PA_ACCESS_KEY": "<from dashboard>",
            "AMAZON_PA_SECRET_KEY": "changeme",
            "AMAZON_PA_PARTNER_TYPE": "Public",
        })
        self.assertFalse(st.can_publish_links)
        self.assertFalse(st.can_fetch_product_data)

    def test_CN7_training_on_program_content_is_refused(self):
        self.assertFalse(audit_dataset([{"origin": "pa_api_payload"}]).ok)
        self.assertTrue(audit_dataset([{"origin": "pa_api_payload"}], has_written_approval=True).ok)

    def test_only_official_hosts_count_as_sources(self):
        self.assertTrue(is_official("https://affiliate-program.amazon.com/help/operating/agreement"))
        self.assertFalse(is_official("https://some-blog.example.com/asin-guide"))


class TestDataIntegrity(unittest.TestCase):
    def test_A1_A5_published_data_passes_the_audit(self):
        rep = audit_data()
        self.assertTrue(rep.ok, "\n".join(f"{f.rule}: {f.message}" for f in rep.findings))


if __name__ == "__main__":
    unittest.main(verbosity=2)
