#!/usr/bin/env python3
"""
Zone1 — self-hosted analytics endpoint (the receiver for the site's cookie-free
event counter). Stdlib only; run it anywhere the owner controls a host:

    python3 platform/analytics/server.py --host 127.0.0.1 --port 8090

It records exactly the four automatic events defined in data/measurement.json
(EV-01…EV-04) and nothing else. EV-05 (reported_order) is deliberately NOT
accepted here: it is entered by hand from the owner's Associates Central report
into the campaign ledger, never emitted by a browser.

Privacy posture — implemented, not aspirational:

  * No cookies are set or read. No session, no fingerprint, no visitor id.
  * The client address, the User-Agent header and the Referer header are never
    read into memory and never written to the event log. The log lines are the
    event payload verbatim plus a server-side receive timestamp.
  * Unknown fields are rejected (HTTP 400), so a future client cannot smuggle
    identifiers into the schema by accident.
  * Prefetch/prerender beacons are dropped unrecorded (Program Policies §3(s):
    clicks must be real human actions).

Storage is a JSONL file (platform/analytics/data/events.jsonl by default —
gitignored, because measured data is runtime data, not repository content).
GET /report aggregates it to per-day counts; it never exposes anything
per-reader, because nothing per-reader exists.
"""

import argparse
import json
import re
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
EVENTS_FILE = DATA_DIR / "events.jsonl"

MAX_BODY = 16 * 1024       # one beacon is a few hundred bytes; 16 KB allows a small batch
MAX_BATCH = 50

# The four automatic events of data/measurement.json v1.2, with exactly the fields
# each event's definition says it records. Names are the canonical vocabulary shared
# with data/analytics-plan.json (2026-11-17 merge of two parallel designs). EV-05
# "affiliate_report_import" is intentionally absent.
EVENT_SCHEMA = {
    "page_view": {
        "required": {"event", "page", "d", "from_campaign"},
        "optional": set(),
    },
    "outbound_click": {
        "required": {"event", "page", "d", "asin", "tag"},
        "optional": set(),
    },
    "article_engagement": {
        "required": {"event", "page", "d"},
        "optional": set(),
    },
    "comparison_interaction": {
        "required": {"event", "page", "d"},
        "optional": set(),
    },
}

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9/._-]*\.html$|^$")
ASIN_RE = re.compile(r"^[A-Z0-9]{10}$")
TAG_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9-]{2,}-(20|21|22))?$")  # "" allowed: links may carry no tag (flag F82)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_lock = threading.Lock()


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_event(ev):
    """Return None if valid, else a human-readable reason string."""
    if not isinstance(ev, dict):
        return "event must be a JSON object"
    name = ev.get("event")
    if name not in EVENT_SCHEMA:
        # EV-05 and anything unknown land here on purpose.
        return f"unknown event {name!r} — this endpoint accepts EV-01…EV-04 only (EV-05 is operator-only)"
    schema = EVENT_SCHEMA[name]
    keys = set(ev.keys())
    missing = schema["required"] - keys
    if missing:
        return f"{name}: missing field(s) {sorted(missing)}"
    extra = keys - schema["required"] - schema["optional"]
    if extra:
        return f"{name}: unknown field(s) {sorted(extra)} — the schema records only what measurement.json defines"
    if name != "outbound_click" and not SLUG_RE.match(str(ev.get("page", ""))):
        return "page must be a site-relative *.html slug"
    if name == "outbound_click":
        if not SLUG_RE.match(str(ev.get("page", ""))):
            return "page must be a site-relative *.html slug"
        if not ASIN_RE.match(str(ev.get("asin", ""))):
            return "asin must be a 10-character ASIN"
        if not TAG_RE.match(str(ev.get("tag", ""))):
            return "tag must look like an Associates tracking ID (xxxxx-20)"
    if not DATE_RE.match(str(ev.get("d", ""))):
        return "d must be a UTC date (YYYY-MM-DD)"
    if name == "page_view" and not isinstance(ev.get("from_campaign"), bool):
        return "from_campaign must be a boolean"
    return None


def record(ev):
    """Append one event. The payload is stored verbatim plus a receive stamp.

    Deliberately not stored: client address, User-Agent, Referer, cookies — the
    handler never reads them, so nothing can leak them into this file.
    """
    line = json.dumps({"received": utc_now(), **ev}, ensure_ascii=False, separators=(",", ":"))
    with _lock:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with EVENTS_FILE.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def load_events():
    if not EVENTS_FILE.exists():
        return []
    out = []
    with EVENTS_FILE.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def report(since=None):
    """Per-day aggregates only. No per-reader dimension exists to expose."""
    counts = {}
    total = 0
    for ev in load_events():
        d = ev.get("d", "")
        if since and d < since:
            continue
        total += 1
        name = ev.get("event", "?")
        key = (d, name, ev.get("asin") or ev.get("page", ""))
        counts[key] = counts.get(key, 0) + 1
    rows = [
        {"d": d, "event": name, "key": key, "count": n}
        for (d, name, key), n in sorted(counts.items())
    ]
    return {"total_events": total, "since": since or "", "rows": rows,
            "note": "Aggregates only. The log stores no IP address, user agent, "
                    "referrer or visitor identifier, so nothing per-reader can be reported."}


class Handler(BaseHTTPRequestHandler):
    server_version = "Zone1Analytics/1.0"

    def _cors(self):
        # The site is served from a different origin (GitHub Pages). The counter
        # sends text/plain beacons (no preflight), but /report is a browser GET.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send(self, code, payload=None):
        body = b"" if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self._cors()
        if body:
            self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def log_message(self, fmt, *args):  # keep the access log free of addresses too
        sys.stderr.write("%s %s\n" % (utc_now(), fmt % args))

    def do_OPTIONS(self):
        self._send(204)

    def do_GET(self):
        if self.path.startswith("/health"):
            self._send(200, {"ok": True, "events_recorded": report()["total_events"]})
            return
        if self.path.startswith("/report"):
            since = ""
            if "?" in self.path:
                from urllib.parse import parse_qs, urlparse
                since = (parse_qs(urlparse(self.path).query).get("since") or [""])[0]
                if since and not DATE_RE.match(since):
                    self._send(400, {"error": "since must be YYYY-MM-DD"})
                    return
            self._send(200, report(since or None))
            return
        self._send(404, {"error": "POST /e to record; GET /report or /health to read"})

    def do_POST(self):
        if not self.path.startswith("/e"):
            self._send(404, {"error": "POST /e to record"})
            return
        # Program Policies §3(s): never record a prefetch/prerender beacon.
        purpose = (self.headers.get("Purpose") or self.headers.get("Sec-Purpose") or "").lower()
        if "prefetch" in purpose or "prerender" in purpose:
            self._send(204)
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self._send(400, {"error": "body missing or too large"})
            return
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send(400, {"error": "body must be JSON"})
            return
        events = payload if isinstance(payload, list) else [payload]
        if not events or len(events) > MAX_BATCH:
            self._send(400, {"error": f"send 1…{MAX_BATCH} events per request"})
            return
        errors = []
        for i, ev in enumerate(events):
            reason = validate_event(ev)
            if reason:
                errors.append(f"event[{i}]: {reason}")
        if errors:
            self._send(400, {"error": "; ".join(errors)})
            return
        for ev in events:
            record(ev)
        self._send(204)


def serve(host="127.0.0.1", port=8090):
    httpd = ThreadingHTTPServer((host, port), Handler)
    return httpd


def main():
    ap = argparse.ArgumentParser(description="Zone1 self-hosted analytics endpoint")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8090)
    args = ap.parse_args()
    httpd = serve(args.host, args.port)
    print(f"Zone1 analytics endpoint on http://{args.host}:{args.port} — "
          f"events → {EVENTS_FILE}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
