"""Exercise the actual browser source and Python endpoint together, using fixtures only."""
import copy
import json
import shutil
import sqlite3
import subprocess
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import build
from analytics.collector import BROWSER_EVENTS, ENDPOINT_PATH, make_handler, validate_payload

ROOT = Path(__file__).resolve().parents[1]


def client(**config):
    result = subprocess.run(
        ["node", "tests/analytics_harness.cjs", json.dumps(config)],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    return json.loads(result.stdout)


@unittest.skipUnless(shutil.which("node"), "Node is required for actual-client contract tests")
class BrowserCollectorContractTests(unittest.TestCase):
    def test_client_payloads_are_accepted_by_real_http_collector(self):
        requests = client(actions=[{"kind": "click"}, {"kind": "click", "target": "PI-04"}])
        requests += client(page="compare", actions=[{"kind": "click", "event": "comparison_interaction"}])
        requests += client(page="articles/sync-finish-explained", type="article", actions=[{"kind": "ticks", "count": 62}])
        self.assertEqual({r["body"]["event"] for r in requests}, BROWSER_EVENTS)
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "synthetic-only.sqlite3"
            env = {
                "ZONE1_ANALYTICS_ENABLED": "1",
                "ZONE1_ANALYTICS_PRIVACY_NOTICE_APPROVED": "1",
                "ZONE1_ANALYTICS_PUBLIC_ORIGIN": "https://contract-test.invalid",
                "ZONE1_ANALYTICS_DB_PATH": str(db),
            }
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(env))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                for emitted in requests:
                    self.assertEqual(emitted["route"], ENDPOINT_PATH)
                    self.assertEqual(emitted["options"]["credentials"], "omit")
                    self.assertEqual(emitted["options"]["referrerPolicy"], "no-referrer")
                    self.assertEqual(emitted["options"]["mode"], "same-origin")
                    request = Request(
                        f"http://127.0.0.1:{server.server_port}{emitted['route']}",
                        data=emitted["options"]["body"].encode(),
                        headers={"Content-Type": emitted["options"]["headers"]["Content-Type"], "Origin": "https://contract-test.invalid"},
                        method="POST",
                    )
                    with urlopen(request, timeout=3) as response:
                        self.assertEqual(202, response.status)
                with sqlite3.connect(db) as connection:
                    counts = connection.execute("SELECT event,SUM(count) FROM daily_events GROUP BY event").fetchall()
                    self.assertEqual(dict(counts), {"page_view": 3, "outbound_click": 2, "comparison_interaction": 1, "article_engagement": 1})
                    self.assertEqual(connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(), [("daily_events",)])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)

    def test_disabled_and_privacy_opt_outs_send_nothing(self):
        for config in ({"disabled": True}, {"dnt": True}, {"gpc": True}, {"endpoint": "https://tracker.invalid/collect"}):
            with self.subTest(config=config):
                self.assertEqual(client(**config, actions=[{"kind": "click"}]), [])

    def test_only_trusted_marked_primary_and_middle_activations_count(self):
        emitted = client(actions=[
            {"kind": "click", "trusted": False},
            {"kind": "click", "target": "unregistered-target"},
            {"kind": "click", "button": 2},
            {"kind": "click", "eventType": "auxclick", "button": 1, "target": "PI-05"},
        ])
        self.assertEqual([r["body"] for r in emitted], [
            {"event": "page_view", "page_id": "index"},
            {"event": "outbound_click", "page_id": "index", "target_id": "PI-05"},
        ])

    def test_engagement_excludes_hidden_and_unfocused_intervals(self):
        emitted = client(page="articles/sync-finish-explained", type="article", actions=[
            {"kind": "ticks", "count": 30},
            {"kind": "visible", "value": False}, {"kind": "ticks", "count": 90},
            {"kind": "visible", "value": True}, {"kind": "focus", "value": False}, {"kind": "ticks", "count": 90},
            {"kind": "focus", "value": True}, {"kind": "ticks", "count": 31},
            {"kind": "ticks", "count": 90},
        ])
        self.assertEqual([r["body"]["event"] for r in emitted], ["page_view", "article_engagement"])
        for row in emitted:
            validate_payload(row["body"])

    def test_hidden_initial_page_view_fires_once_when_visible(self):
        emitted = client(hidden=True, actions=[{"kind": "visible", "value": True}, {"kind": "visible", "value": True}])
        self.assertEqual(len(emitted), 1)

    def test_invalid_shapes_are_validation_errors_not_type_errors(self):
        for event in ([], {}, None, True, 2):
            with self.subTest(event=event), self.assertRaises(ValueError):
                validate_payload({"event": event, "page_id": "index"})
        with self.assertRaises(ValueError):
            validate_payload({"event": "article_engagement", "page_id": "articles/index", "bucket": "60s"})
        with self.assertRaises(ValueError):
            validate_payload({"event": "outbound_click", "page_id": "index"})


class BuildMeasurementContractTests(unittest.TestCase):
    def test_actual_disabled_configuration_passes(self):
        self.assertEqual([], build.check_analytics_consistency({}))

    def test_dual_switch_drift_is_rejected(self):
        plan = copy.deepcopy(build.ANALYTICS_PLAN)
        plan["collection"]["enabled"] = True
        with patch.object(build, "ANALYTICS_PLAN", plan):
            self.assertTrue(any("switches disagree" in issue for issue in build.check_analytics_consistency({})))

    def test_unsafe_or_missing_endpoint_and_privacy_gate_fail(self):
        plan = copy.deepcopy(build.ANALYTICS_PLAN)
        plan["collection"]["enabled"] = True
        with patch.object(build, "ANALYTICS_PLAN", plan), patch.object(build, "ANALYTICS_ENABLED", True), patch.object(build, "ANALYTICS_ENDPOINT", "https://external.invalid/collect"):
            issues = build.check_analytics_consistency({})
        self.assertTrue(any("same-origin" in issue for issue in issues))
        self.assertTrue(any("privacy_notice_approved" in issue for issue in issues))

    def test_enabled_reader_loads_client_but_workspace_does_not(self):
        plan = copy.deepcopy(build.ANALYTICS_PLAN)
        plan["collection"].update(enabled=True, endpoint_deployed=True, runtime_selected=True, privacy_notice_approved=True)
        notice = "It loads one small script of its own"
        pages = {"index.html": notice + '<script src="assets/analytics.js"></script>', "measurement.html": notice}
        with patch.object(build, "ANALYTICS_PLAN", plan), patch.object(build, "ANALYTICS_ENABLED", True), patch.object(build, "ANALYTICS_ON", True), patch.object(build, "ANALYTICS_ENDPOINT", ENDPOINT_PATH):
            self.assertEqual([], build.check_analytics_consistency(pages))
            pages["measurement.html"] += '<script src="assets/analytics.js"></script>'
            self.assertTrue(build.check_analytics_consistency(pages))

    def test_event_name_drift_fails_the_build(self):
        with patch.object(build, "ANALYTICS_EVENTS", ["EV-01", "EV-02", "EV-03", "EV-04"]):
            self.assertTrue(any("event names differ" in issue for issue in build.check_analytics_consistency({})))


if __name__ == "__main__":
    unittest.main()
