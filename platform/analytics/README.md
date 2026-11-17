# Zone1 analytics endpoint (self-hosted)

The receiver for the site's cookie-free event counter. It implements exactly the
four automatic events defined in [`data/measurement.json`](../../data/measurement.json)
(EV-01…EV-04). **EV-05 (reported_order) is rejected by design** — reported orders
are entered by hand from the owner's Associates Central report into the campaign
ledger, never emitted by a browser.

## Run it (stdlib only, no dependencies)

```bash
python3 platform/analytics/server.py --host 0.0.0.0 --port 8090
```

Put TLS in front of it (Caddy, nginx, or a platform's automatic certificate) and
note the public `https://` URL — that is the whole deployment.

## Turn the counter on

1. Deploy this server somewhere the owner controls (a 1-node host, a container,
   or any always-on machine behind TLS).
2. Set `analytics_endpoint` in [`data/config.json`](../../data/config.json) to
   the public `https://…/e` URL.
3. Rebuild (`python3 build.py`). The same commit must keep the footer's
   cookie/analytics sentence truthful — the build guard
   `check_analytics_disclosure()` fails the build if the footer statement and the
   configured state disagree, so this cannot be forgotten.
4. Read counts at `GET /report?since=YYYY-MM-DD` (per-day aggregates only).

Until step 2 is done, the counter is inert: the shipped JavaScript exits before
sending anything, nothing is stored in the visitor's browser, and the footer says
so.

## What the endpoint records — and what it structurally cannot

| Event | Fields stored | Never stored |
|---|---|---|
| `page_view` | page slug, UTC date, did the arrival carry a utm parameter (boolean) | IP, user agent, referrer, visitor id |
| `outbound_product_click` | ASIN, page slug, UTC date, the Associates tag on the link | order value, what was bought, Amazon session data |
| `guide_completed` | page slug, UTC date | time on page, scroll depth, visitor id |
| `comparison_table_viewed` | page slug, UTC date | which rows, visitor id |

The server **never reads** the client address, `User-Agent` or `Referer`
headers; the tests in [`test_server.py`](test_server.py) prove the log cannot
contain them. Unknown event names and unknown fields are rejected with HTTP 400,
so nothing outside this table can be recorded. Prefetch/prerender beacons are
dropped unrecorded (Program Policies §3(s)).

Storage is `data/events.jsonl` in this directory (gitignored — measured data is
runtime data, not repository content). `/report` returns per-day aggregates only;
there is no per-reader dimension to expose, because none is collected.

## Tests

```bash
python3 platform/analytics/test_server.py   # 21 assertions; exit 0 = all passed
```
