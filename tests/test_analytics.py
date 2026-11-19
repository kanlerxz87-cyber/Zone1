from __future__ import annotations

import json
import sqlite3
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from analytics.collector import ENDPOINT_PATH, allowed_product_ids, make_handler, record_event, validate_payload
from analytics.report_import import append_report_row, normalize_row


class CollectorValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.product = sorted(allowed_product_ids())[0]

    def test_allowlisted_page_view_is_minimal(self) -> None:
        result = validate_payload({"event": "page_view", "page_id": "index"})
        self.assertEqual(result, {"event": "page_view", "page_id": "index", "target_id": "", "bucket": ""})

    def test_unrecognized_or_identifying_fields_are_rejected(self) -> None:
        for payload in (
            {"event": "page_view", "page_id": "index", "visitor_id": "abc"},
            {"event": "page_view", "page_id": "index", "referrer": "https://example.test/?email=x"},
            {"event": "page_view", "page_id": "../secret"},
            {"event": "affiliate_report_import", "page_id": "index"},
            {"event": [], "page_id": "index"},
            {"event": {"bad": True}, "page_id": "index"},
            {"event": "outbound_click", "page_id": "index"},
        ):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                validate_payload(payload)

    def test_engagement_is_a_fixed_bucket_and_only_for_published_reading_pages(self) -> None:
        self.assertEqual(
            validate_payload({"event": "article_engagement", "page_id": "articles/air-fryer-capacity-guide", "bucket": "60s"})["bucket"],
            "60s",
        )
        for payload in (
            {"event": "article_engagement", "page_id": "index", "bucket": "60s"},
            {"event": "article_engagement", "page_id": "articles/air-fryer-capacity-guide", "bucket": "61s"},
        ):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                validate_payload(payload)

    def test_comparison_event_requires_a_product_id(self) -> None:
        accepted = validate_payload({
            "event": "comparison_interaction", "page_id": "compare", "target_id": self.product
        })
        self.assertEqual(accepted["target_id"], self.product)
        with self.assertRaises(ValueError):
            validate_payload({"event": "comparison_interaction", "page_id": "compare", "target_id": "https://amazon.com"})

    def test_outbound_click_never_accepts_a_destination_url(self) -> None:
        with self.assertRaises(ValueError):
            validate_payload({"event": "outbound_click", "page_id": "index", "target_id": "https://amazon.com/?tag=x"})

    def test_storage_contains_only_daily_aggregates_and_no_raw_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "events.sqlite3"
            event = {"event": "page_view", "page_id": "index"}
            now = datetime(2026, 11, 17, 12, 30, tzinfo=timezone.utc)
            record_event(db_path, event, now=now)
            record_event(db_path, event, now=now)
            with sqlite3.connect(db_path) as db:
                columns = [row[1] for row in db.execute("PRAGMA table_info(daily_events)")]
                rows = db.execute("SELECT day,event,page_id,target_id,bucket,count FROM daily_events").fetchall()
            self.assertEqual(columns, ["day", "event", "page_id", "target_id", "bucket", "count"])
            self.assertEqual(rows, [("2026-11-17", "page_view", "index", "", "", 2)])

    def test_concurrent_increments_are_not_lost(self):
        from concurrent.futures import ThreadPoolExecutor
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "aggregate.sqlite3"
            event = {"event": "outbound_click", "page_id": "index", "target_id": self.product}
            with ThreadPoolExecutor(max_workers=8) as pool:
                list(pool.map(lambda _: record_event(path, event), range(40)))
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute("SELECT sum(count) FROM daily_events").fetchone()[0], 40)

    def test_engagement_listing_page_is_not_an_article(self):
        with self.assertRaises(ValueError):
            validate_payload({"event": "article_engagement", "page_id": "articles/index", "bucket": "60s"})

    def test_daily_retention_is_applied(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.sqlite3"
            event = {"event": "page_view", "page_id": "index"}
            record_event(path, event, now=datetime(2020, 1, 1, tzinfo=timezone.utc))
            record_event(path, event, now=datetime(2026, 11, 19, tzinfo=timezone.utc))
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute("SELECT day,count FROM daily_events").fetchall(), [("2026-11-19", 1)])

    def test_disabled_http_service_fails_closed(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler({}))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            request = Request(
                f"http://127.0.0.1:{server.server_port}{ENDPOINT_PATH}",
                data=b'{"event":"page_view","page_id":"index"}',
                headers={"Content-Type": "application/json", "Origin": "https://zone1.example"},
                method="POST",
            )
            with self.assertRaises(HTTPError) as caught:
                urlopen(request, timeout=3)
            self.assertEqual(caught.exception.code, 503)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_enabled_service_requires_exact_origin_and_accepts_aggregate_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "events.sqlite3"
            env = {
                "ZONE1_ANALYTICS_ENABLED": "1",
                "ZONE1_ANALYTICS_PRIVACY_NOTICE_APPROVED": "1",
                "ZONE1_ANALYTICS_PUBLIC_ORIGIN": "https://zone1.example",
                "ZONE1_ANALYTICS_DB_PATH": str(db_path),
            }
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(env))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_port}{ENDPOINT_PATH}"
                body = json.dumps({"event": "page_view", "page_id": "index"}).encode()
                bad = Request(url, data=body, headers={"Content-Type": "application/json", "Origin": "https://other.example"}, method="POST")
                with self.assertRaises(HTTPError) as caught:
                    urlopen(bad, timeout=3)
                self.assertEqual(caught.exception.code, 403)

                good = Request(url, data=body, headers={"Content-Type": "application/json", "Origin": "https://zone1.example"}, method="POST")
                with urlopen(good, timeout=3) as response:
                    self.assertEqual(response.status, 202)
                    self.assertEqual(json.loads(response.read()), {"accepted": True})
                with sqlite3.connect(db_path) as db:
                    count = db.execute("SELECT count FROM daily_events WHERE event='page_view'").fetchone()[0]
                self.assertEqual(count, 1)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)


class ReportImportTests(unittest.TestCase):
    def valid_row(self) -> dict[str, object]:
        return {
            "timestamp_utc": "2026-11-17T12:00:00Z",
            "source_report": "Associates Central report",
            "channel": "shopnow047c-20",
            "date_range": "2026-11-01/2026-11-15",
            "eligible_sessions": 14,
            "clicks": 8,
            "reported_orders": 2,
        }

    def test_normalize_preserves_only_reported_aggregate_fields(self) -> None:
        normalized = normalize_row(self.valid_row())
        self.assertEqual(normalized["timestamp_utc"], "2026-11-17T12:00:00Z")
        self.assertNotIn("order_id", normalized)

    def test_report_row_rejects_estimated_or_invalid_counts(self) -> None:
        for field, value in (("clicks", -1), ("reported_orders", 2.5), ("eligible_sessions", True)):
            row = self.valid_row()
            row[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                normalize_row(row)

    def test_ledger_import_is_atomic_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "campaign-ledger.json"
            ledger.write_text(json.dumps({"columns": ["timestamp_utc"], "rows": []}), encoding="utf-8")
            self.assertTrue(append_report_row(self.valid_row(), ledger))
            self.assertFalse(append_report_row(self.valid_row(), ledger))
            saved = json.loads(ledger.read_text(encoding="utf-8"))
            self.assertEqual(len(saved["rows"]), 1)
            self.assertEqual(saved["rows"][0]["reported_orders"], 2)

    def test_missing_report_fields_remain_blank_not_zero(self):
        row = self.valid_row()
        row["eligible_sessions"] = None
        normalized = normalize_row(row)
        self.assertIsNone(normalized["eligible_sessions"])

    def test_conflicting_reimport_is_flagged_not_silently_dropped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.json"
            path.write_text(json.dumps({"rows": []}))
            row = self.valid_row()
            append_report_row(row, path)
            row["clicks"] = 9
            with self.assertRaises(ValueError):
                append_report_row(row, path)


if __name__ == "__main__":
    unittest.main()
