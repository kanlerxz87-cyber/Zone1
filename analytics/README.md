# Zone1 aggregate measurement — tested, not deployed

**Production collection is OFF.** GitHub Pages serves static files; it does not run
this collector. A local test or a preview is not a persistent production endpoint.
No traffic, orders or commission attribution have been observed by this project.

## One contract, five events

The canonical definitions are in [`../data/analytics-plan.json`](../data/analytics-plan.json).
`data/measurement.json` must match them or the site build fails.

| ID | Event | Trigger / permitted payload |
|---|---|---|
| EV-01 | `page_view` | Once when a canonical reader page is visible; `event`, `page_id` only. Not a session or unique reader. |
| EV-02 | `outbound_click` | Trusted primary/middle-button activation of an allow-listed Amazon host; `event`, `page_id`, `target_id` (our product slug). Includes supplied short links without guessing an ASIN or tag. |
| EV-03 | `article_engagement` | Once after 60 visible, focused seconds on an article/guide; `event`, `page_id`, `bucket: "60s"`. Not a completion measurement. |
| EV-04 | `comparison_interaction` | Trusted activation of an internal product-guide link on `compare.html`; `event`, `page_id`, `target_id`. Not table visibility. |
| EV-05 | `affiliate_report_import` | **Never from a browser.** Authorized aggregate import to the campaign ledger, preserving report timestamp, provenance label, channel, date range and reported fields. |

The browser transmits no URLs, query parameters, referrers, ASIN guesses, tracking IDs,
user agents, cookies or persistent reader identifiers. `fetch` uses `credentials: omit`,
`mode: same-origin`, and `referrerPolicy: no-referrer`. DNT/GPC suppress requests.
It never blocks, wraps, redirects or automatically opens an affiliate link.

The collector rejects unknown events, page IDs, product IDs, fields and oversized bodies.
It requires an exact HTTPS origin and JSON content type. EV-05 is rejected at this route.
Only `(UTC day, event, page_id, target_id, bucket, count)` is stored in SQLite; there is
no raw event stream. Atomic increments avoid the retired Worker's lost-update race.
Retention is 395 days, enforced when recording an event. No public reporting route exists.

**Limits:** Origin validation is not authentication. Network requests can be forged;
counts can contain bots and miss blocked scripts/opt-outs. Without a visitor ID these
are not unique visitors or eligible sessions. Do not divide unrelated click/order
windows and call the result a conversion rate.

## Supported files

- `client.js`: sole browser source, copied byte-for-byte to `assets/analytics.js` by the builder.
- `collector.py`: supported stdlib Python collector, `/api/analytics/events` and `/health` only.
- `report_import.py`: authorized aggregate importer; no Amazon scraping or login automation.
- `Dockerfile`: optional non-root container with a separate writable database volume.
- `endpoint.php`, `worker.js`: **retired** v1 adapters, return HTTP 410; no storage or forwarding.

## Deployment gate

A persistent host, TLS/reverse proxy, logging policy, privacy/retention review and production
receipt are needed. This session cannot create hosting or account authority by assertion.
The same-origin requirement means a proxy/custom origin is necessary; pointing the GitHub
Pages client at a foreign collector URL will be refused by both the build and client.

Run behind a TLS reverse proxy that forwards only the event route and health check, limits
request sizes/rates/connections and uses approved logging. The Python stdlib server is not
intended as an unprotected, high-volume edge server. Do not put it on the public Internet
without those controls. The app disables access logging, but **the hosting provider and
proxy still see connection metadata**. GitHub Pages logs IP addresses for security under
[its documented policy](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection).
No blanket GDPR/consent-exemption or full legal-compliance claim is made.

Required server environment (values must describe the real deployment):

```sh
ZONE1_ANALYTICS_ENABLED=1
ZONE1_ANALYTICS_PRIVACY_NOTICE_APPROVED=1
ZONE1_ANALYTICS_PUBLIC_ORIGIN=https://your-owned-publication.example
ZONE1_ANALYTICS_DB_PATH=/var/lib/zone1/events.sqlite3
ZONE1_ANALYTICS_BIND=0.0.0.0
ZONE1_ANALYTICS_PORT=8078
python3 -m analytics.collector
```

The database path must be **outside the checkout and public document root**. Container
operators should mount `/var/lib/zone1` writable for UID 10001. No secret is needed by the
public event route; do not put account credentials in frontend code.

Before enabling the site, record evidence for `runtime_selected`, `endpoint_deployed`,
`privacy_notice_approved`, `host_logging_reviewed`, `end_to_end_verified` in
`data/analytics-plan.json`. In the same change, enable both configuration switches and
set `data/config.json` → `analytics.endpoint` to `/api/analytics/events` (or that route
on the canonical HTTPS origin). One-sided switches, unsupported routes, drifted event
definitions or stale privacy claims fail the build. Confirm one authorized production
diagnostic arrives; keep diagnostics separate from campaign evidence. **Do not automate
clicks to Amazon.**

## Test before deployment

```sh
python3 build.py
python3 -m unittest discover -s tests -v
node --test tests/test_analytics_client.cjs
```

Node's built-in test runner executes the **generated browser script** in an instrumented
browser-like environment. Actual emitted payloads are passed to the Python collector's
validator. Python tests exercise HTTP acceptance/rejection and isolated SQLite storage,
including concurrent increments. Fixtures use temporary directories, never the real ledger.

## Import only reported values

```sh
python3 -m analytics.report_import /private/authorized-aggregate.json --authorized
```

Required keys: `timestamp_utc`, `source_report`, `channel`, `date_range`,
`eligible_sessions`, `clicks`, `reported_orders`. Unreported metrics must be `null`, not
zero. At least one metric must actually be reported. URLs, email addresses, order IDs,
customer details and unexpected fields are refused. Imports are locked, atomic and
idempotent; conflicting values for the same provenance key require review.

The acknowledgement flag cannot prove report authenticity. Only an authorized first-party
report establishes the values. The committed campaign ledger stays empty until one exists.
Policy references: [Amazon Program Policies](https://affiliate-program.amazon.com/help/operating/policies)
(privacy, no artificial clicks, no per-user sub-tags) and
[Tracking ID Summary Report](https://affiliate-program.amazon.com/help/node/topic/GJDYPQZK6E37RLPU).
