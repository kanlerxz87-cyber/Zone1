#!/usr/bin/env python3
"""A minimal, self-hosted Zone1 aggregate-event collector.

This service is intentionally fail-closed. It will not accept events unless an operator
sets ZONE1_ANALYTICS_ENABLED=1, ZONE1_ANALYTICS_PRIVACY_NOTICE_APPROVED=1,
ZONE1_ANALYTICS_PUBLIC_ORIGIN to the exact HTTPS origin, and a database path outside this
checkout. GitHub Pages does not run this service; no production endpoint is configured.

Only daily aggregate counts are stored. Request bodies are allow-listed and bounded. The
handler never reads or persists cookies, IP addresses, user agents, referers, or full URLs,
and it disables the built-in HTTP access log (which otherwise includes client addresses).
A reverse proxy must also be configured not to retain identifying access logs.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ENDPOINT_PATH = "/api/analytics/events"
MAX_BODY_BYTES = 1024
BROWSER_EVENTS = {"page_view", "outbound_click", "article_engagement", "comparison_interaction"}


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def allowed_page_ids() -> set[str]:
    """Canonical publication IDs only; dashboard/annex and owner pages are excluded."""
    ids = {
        "index",
        "picks",
        "compare",
        "compliance",
        "categories/kitchen-appliances",
        "guides/buying-guide-air-fryers",
        "articles/index",
    }
    products = _json(DATA / "products.json").get("products", [])
    articles = _json(DATA / "articles.json").get("articles", [])
    ids.update(f"products/{item['slug']}" for item in products)
    ids.update(f"articles/{item['slug']}" for item in articles)
    return ids


def allowed_product_ids() -> set[str]:
    return {item["slug"] for item in _json(DATA / "products.json").get("products", [])}


def validate_payload(payload: Any) -> dict[str, str]:
    """Validate and return only the fields the aggregate store is allowed to receive."""
    if not isinstance(payload, dict):
        raise ValueError("event body must be an object")
    event = payload.get("event")
    page_id = payload.get("page_id")
    if event not in BROWSER_EVENTS:
        raise ValueError("event is not allowed from a browser")
    if not isinstance(page_id, str) or page_id not in allowed_page_ids():
        raise ValueError("unknown canonical page ID")

    allowed_keys = {"event", "page_id"}
    result = {"event": event, "page_id": page_id, "target_id": "", "bucket": ""}
    if event == "outbound_click":
        allowed_keys.add("target_id")
        target_id = payload.get("target_id", "")
        if not isinstance(target_id, str) or (target_id and target_id not in allowed_product_ids()):
            raise ValueError("outbound link ID is not allow-listed")
        result["target_id"] = target_id
    elif event == "article_engagement":
        if not (page_id.startswith("articles/") or page_id.startswith("guides/")):
            raise ValueError("engagement is only defined for articles and guides")
        allowed_keys.add("bucket")
        bucket = payload.get("bucket")
        if bucket != "60s":
            raise ValueError("only the fixed 60-second engagement bucket is allowed")
        result["bucket"] = bucket
    elif event == "comparison_interaction":
        if page_id != "compare":
            raise ValueError("comparison interactions must originate on the comparison page")
        allowed_keys.add("target_id")
        target_id = payload.get("target_id")
        if not isinstance(target_id, str) or target_id not in allowed_product_ids():
            raise ValueError("comparison target must be an allow-listed product ID")
        result["target_id"] = target_id
    if set(payload) - allowed_keys:
        raise ValueError("unexpected event properties")
    return result


def _database_path(raw_path: str) -> Path:
    if not raw_path:
        raise ValueError("ZONE1_ANALYTICS_DB_PATH is required")
    path = Path(raw_path).expanduser().resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return path
    raise ValueError("analytics database must be outside the repository checkout")


def _origin(raw: str) -> str:
    parsed = urlsplit(raw)
    if parsed.scheme != "https" or not parsed.netloc or parsed.path or parsed.query or parsed.fragment:
        raise ValueError("public origin must be an HTTPS origin with no path")
    return f"https://{parsed.netloc.lower()}"


def environment_config(environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = os.environ if environ is None else environ
    enabled = env.get("ZONE1_ANALYTICS_ENABLED") == "1"
    privacy_ok = env.get("ZONE1_ANALYTICS_PRIVACY_NOTICE_APPROVED") == "1"
    origin_raw = env.get("ZONE1_ANALYTICS_PUBLIC_ORIGIN", "")
    db_raw = env.get("ZONE1_ANALYTICS_DB_PATH", "")
    origin = _origin(origin_raw) if origin_raw else ""
    db_path = _database_path(db_raw) if db_raw else None
    ready = bool(enabled and privacy_ok and origin and db_path)
    return {
        "enabled": enabled,
        "privacy_notice_approved": privacy_ok,
        "origin": origin,
        "db_path": db_path,
        "ready": ready,
    }


def record_event(db_path: str | Path, payload: Any, *, now: datetime | None = None) -> None:
    """Atomically increment a daily aggregate; raw payloads are never written."""
    event = validate_payload(payload)
    instant = now or datetime.now(timezone.utc)
    if instant.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    day = instant.astimezone(timezone.utc).date().isoformat()
    path = _database_path(str(db_path))
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute(
            """CREATE TABLE IF NOT EXISTS daily_events (
                 day TEXT NOT NULL,
                 event TEXT NOT NULL,
                 page_id TEXT NOT NULL,
                 target_id TEXT NOT NULL DEFAULT '',
                 bucket TEXT NOT NULL DEFAULT '',
                 count INTEGER NOT NULL CHECK(count > 0),
                 PRIMARY KEY(day, event, page_id, target_id, bucket)
               )"""
        )
        db.execute(
            """INSERT INTO daily_events(day,event,page_id,target_id,bucket,count)
               VALUES(?,?,?,?,?,1)
               ON CONFLICT(day,event,page_id,target_id,bucket)
               DO UPDATE SET count=count+1""",
            (day, event["event"], event["page_id"], event["target_id"], event["bucket"]),
        )
        # Keep only the proposed rolling retention window. This is aggregate-only data.
        db.execute(
            "DELETE FROM daily_events WHERE day < date(?, ?)",
            (day, "-395 days"),
        )


def _json_response(handler: BaseHTTPRequestHandler, status: int, body: dict[str, Any]) -> None:
    encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Length", str(len(encoded)))
    handler.end_headers()
    handler.wfile.write(encoded)


def make_handler(environ: Mapping[str, str] | None = None):
    config = environment_config(environ)

    class CollectorHandler(BaseHTTPRequestHandler):
        server_version = "Zone1AggregateCollector"
        sys_version = ""

        def log_message(self, _format: str, *args: Any) -> None:
            # BaseHTTPRequestHandler logs the remote address by default. Do not emit it.
            return

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
            if self.path != "/health":
                _json_response(self, 404, {"error": "not_found"})
                return
            if not config["ready"]:
                _json_response(self, 503, {"status": "disabled"})
                return
            _json_response(self, 200, {"status": "ready"})

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
            if self.path != ENDPOINT_PATH:
                _json_response(self, 404, {"error": "not_found"})
                return
            if not config["ready"]:
                _json_response(self, 503, {"error": "collector_disabled"})
                return
            if self.headers.get("Origin", "") != config["origin"]:
                _json_response(self, 403, {"error": "origin_not_allowed"})
                return
            content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            if content_type != "application/json":
                _json_response(self, 415, {"error": "json_required"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = 0
            if length < 2 or length > MAX_BODY_BYTES:
                _json_response(self, 413, {"error": "body_size_not_allowed"})
                return
            try:
                raw = self.rfile.read(length)
                payload = json.loads(raw.decode("utf-8"))
                record_event(config["db_path"], payload)
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError, OSError, sqlite3.Error):
                _json_response(self, 400, {"error": "invalid_event"})
                return
            _json_response(self, 202, {"accepted": True})

    return CollectorHandler


def serve(host: str | None = None, port: int | None = None) -> None:
    config = environment_config()
    if not config["ready"]:
        raise SystemExit(
            "Collector disabled. Set ZONE1_ANALYTICS_ENABLED=1, "
            "ZONE1_ANALYTICS_PRIVACY_NOTICE_APPROVED=1, an HTTPS "
            "ZONE1_ANALYTICS_PUBLIC_ORIGIN, and ZONE1_ANALYTICS_DB_PATH outside the checkout."
        )
    bind_host = host or os.environ.get("ZONE1_ANALYTICS_BIND", "127.0.0.1")
    bind_port = port or int(os.environ.get("ZONE1_ANALYTICS_PORT", "8078"))
    server = ThreadingHTTPServer((bind_host, bind_port), make_handler())
    print(f"Zone1 analytics collector listening on {bind_host}:{bind_port} (no access log)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    try:
        serve()
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        raise
