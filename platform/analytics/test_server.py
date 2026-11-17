#!/usr/bin/env python3
"""
Tests for the self-hosted analytics endpoint (platform/analytics/server.py).
Run: python3 platform/analytics/test_server.py

These tests exercise the guarantees the measurement page publishes:
  1. EV-01…EV-04 are accepted and recorded.
  2. EV-05 (reported_order) and any unknown event are rejected — the endpoint
     cannot be used to invent an order.
  3. Unknown fields are rejected — no accidental identifiers can enter the log.
  4. The log contains no client address, user-agent or referrer key, ever.
  5. Prefetch beacons are dropped unrecorded (Program Policies §3(s)).
  6. /report returns per-day aggregates only.
"""

import json
import shutil
import sys
import tempfile
import threading
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import server as analytics  # noqa: E402

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}  {detail}")


def post(port, payload, headers=None):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"http://127.0.0.1:{port}/e", data=body, method="POST")
    req.add_header("Content-Type", "text/plain")  # what sendBeacon sends
    req.add_header("User-Agent", "test-agent-should-never-be-stored/1.0")
    req.add_header("Referer", "https://example.invalid/should-never-be-stored")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read() or b"{}")


def get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}") as resp:
        return resp.status, json.loads(resp.read())


def main():
    tmp = Path(tempfile.mkdtemp(prefix="zone1-analytics-test-"))
    analytics.DATA_DIR = tmp
    analytics.EVENTS_FILE = tmp / "events.jsonl"

    httpd = analytics.serve("127.0.0.1", 0)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print(f"endpoint on 127.0.0.1:{port} (scratch data dir {tmp})")

    good = [
        {"event": "page_view", "page": "compare.html", "d": "2026-11-17", "from_campaign": False},
        {"event": "outbound_click", "page": "articles/basket-or-oven.html", "d": "2026-11-17",
         "asin": "B0CDY277D3", "tag": "shopnow047c-20"},
        {"event": "article_engagement", "page": "articles/basket-or-oven.html", "d": "2026-11-17"},
        {"event": "comparison_interaction", "page": "compare.html", "d": "2026-11-17"},
    ]

    print("1. EV-01…EV-04 accepted")
    for ev in good:
        code, _ = post(port, ev)
        check(f"{ev['event']} accepted", code == 204, f"got {code}")

    print("2. EV-05 and unknown events rejected")
    code, _ = post(port, {"event": "affiliate_report_import", "page": "x.html", "d": "2026-11-17",
                          "orders": 1, "revenue": 9.99})
    check("EV-05 (reported_order) rejected", code == 400, f"got {code}")
    code, _ = post(port, {"event": "revenue_forecast", "page": "x.html", "d": "2026-11-17"})
    check("invented event rejected", code == 400, f"got {code}")

    print("3. unknown fields rejected (no smuggled identifiers)")
    code, _ = post(port, {"event": "page_view", "page": "compare.html", "d": "2026-11-17",
                          "from_campaign": False, "ip": "203.0.113.9"})
    check("unknown field 'ip' rejected", code == 400, f"got {code}")
    code, _ = post(port, {"event": "article_engagement", "page": "articles/x.html", "d": "nope"})
    check("bad date rejected", code == 400, f"got {code}")
    code, _ = post(port, {"event": "outbound_click", "page": "compare.html",
                          "d": "2026-11-17", "asin": "short", "tag": "x"})
    check("bad ASIN rejected", code == 400, f"got {code}")

    print("4. log stores no address / user-agent / referrer")
    code, _ = post(port, {"event": "page_view", "page": "index.html", "d": "2026-11-17",
                          "from_campaign": True})
    check("event recorded before log scan", code == 204)
    raw = analytics.EVENTS_FILE.read_text(encoding="utf-8")
    low = raw.lower()
    check("no client address in log", "203.0.113" not in low and '"addr"' not in low
          and '"ip"' not in low and '"remote"' not in low)
    check("no user-agent in log", "user-agent" not in low and "test-agent-should-never-be-stored" not in low)
    check("no referrer in log", "referer" not in low and "should-never-be-stored" not in low)
    stored = [json.loads(line) for line in raw.strip().splitlines()]
    check("stored keys are exactly received + payload keys",
          all(set(ev.keys()) <= {"received", "event", "page", "d", "from_campaign", "asin", "tag"}
              for ev in stored), str(stored))

    print("5. prefetch beacons dropped unrecorded")
    before = len(analytics.load_events())
    code, _ = post(port, {"event": "page_view", "page": "compare.html", "d": "2026-11-17",
                          "from_campaign": False}, headers={"Sec-Purpose": "prefetch"})
    after = len(analytics.load_events())
    check("prefetch not recorded", code == 204 and after == before, f"{before} → {after}")

    print("6. /report aggregates per day only")
    code, rep = get(port, "/report")
    check("report served", code == 200)
    check("report totals match", rep["total_events"] == before, json.dumps(rep)[:200])
    check("report has per-day rows", all("d" in r and "count" in r for r in rep["rows"]))
    code, health = get(port, "/health")
    check("health ok", code == 200 and health["ok"] is True)

    print("7. batch accepted, oversized batch rejected")
    code, _ = post(port, good)
    check("batch of 4 accepted", code == 204, f"got {code}")
    code, _ = post(port, [good[0]] * 51)
    check("batch of 51 rejected", code == 400, f"got {code}")

    httpd.shutdown()
    shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
