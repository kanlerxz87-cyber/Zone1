# First-party measurement — one tested contract

**Implemented and integration-tested; not deployed on the GitHub Pages site.**
`data/analytics-plan.json` is the canonical contract. EV-01..EV-05 are its stable
labels, not a second JSON schema. Synthetic tests never enter the campaign ledger.

| ID | Wire event | Trigger | Accepted application data |
|---|---|---|---|
| EV-01 | `page_view` | First visible state per reader-page load | `event`, allow-listed `page_id` |
| EV-02 | `outbound_click` | Trusted primary/middle activation of a marked supplied-product link | Above + allow-listed `target_id` (not an inferred ASIN) |
| EV-03 | `article_engagement` | 60 visible, focused one-second intervals on an article/guide | Above + fixed `bucket: "60s"`; no target |
| EV-04 | `comparison_interaction` | Trusted product-detail activation on `compare.html` | `event`, `page_id`, product `target_id` |
| EV-05 | `affiliate_report_import` | Operator-only authorised report import | Campaign ledger's dated aggregate fields; never accepted by the browser endpoint |

`analytics/client.js` is copied byte-for-byte to `assets/analytics.js` by the build.
It uses same-origin JSON `fetch`, `credentials: "omit"`, `referrerPolicy:
"no-referrer"`, and `keepalive`; never a credentialed beacon. It reads no cookies,
storage, reader identifiers, referrer, query string or outbound URL. DNT and GPC
opt out. Only public indexable reader pages may load it. JavaScript being enabled
is not evidence that a visitor is human; these counts are not unique people,
eligible sessions, conversions or revenue.

`analytics/collector.py` validates bounded payloads and stores **UTC-day aggregate
counts only** in SQLite. Unknown events/properties/IDs, an untrusted origin, and
browser order events are rejected. No raw rows, IP addresses, user agents,
referrers, cookies or order IDs are written by the application. The collector
suppresses HTTP access logs. Infrastructure sees connection metadata regardless;
review host/proxy logging and retention separately. GitHub Pages itself logs IPs
for security ([official hosting documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection)).

## Deployment gate — why production remains off

GitHub Pages is [static hosting](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages),
not a Python runtime. A workspace preview is not a durable production service.
No host, runtime account, privacy approval or authorised Associates report has
been supplied. Do not send production events to a temporary preview or invent
counts to fill a dashboard.

1. Host the publication and collector on one HTTPS origin. Proxy only
   `/api/analytics/events` to the collector; keep the database outside both the
   checkout and document root. Apply infrastructure body/rate limits and configure
   host/proxy logs and retention. The application origin check is an abuse
   reduction, **not authentication or proof of a human**.
2. Review the actual privacy notice, aggregate retention (395 days proposed),
   infrastructure logs and relevant jurisdiction before recording approval.
3. Start the application with the following operator-owned settings. No secrets
   belong in the repository or a browser payload:

   ```sh
   export ZONE1_ANALYTICS_ENABLED=1
   export ZONE1_ANALYTICS_PRIVACY_NOTICE_APPROVED=1
   export ZONE1_ANALYTICS_PUBLIC_ORIGIN=https://your-real-publication-origin
   export ZONE1_ANALYTICS_DB_PATH=/var/lib/zone1/events.sqlite3
   python3 -m analytics.collector
   ```

   Default bind: `0.0.0.0:8078`; put it behind a restrictive HTTPS reverse proxy.
   `/health` returns ready only after all required environment gates pass. There
   is no public reporting/read endpoint or order-ingestion endpoint.
4. In `data/analytics-plan.json`, record real deployment evidence and set
   `runtime_selected`, `endpoint_deployed`, `privacy_notice_approved`, and
   `collection.enabled` only when true. In `data/config.json`, set
   `analytics.enabled` to the same value and `analytics.endpoint` to
   `/api/analytics/events`. The build rejects drift, an external endpoint, or
   incomplete approvals. Review the generated notice and any now-stale register
   wording as part of that change.
5. Test the exact production origin/route in an isolated test database. Verify
   accepted requests, rejected extra fields, the stored aggregate schema, actual
   opt-outs and infrastructure logging before enabling real traffic. Do not add
   test clicks or test orders to the campaign ledger.

## Verification

```sh
python3 -m unittest discover -s tests -v
```

`tests/test_analytics_contract.py` executes the **actual** client with a Node VM,
then sends its generated JSON to the **real** HTTP handler and checks the SQLite
aggregates. It also covers opt-outs, synthetic clicks, short-link IDs, hidden-tab
engagement, event-name drift, the disabled gate and enabled script placement.
The old PHP and Worker implementations were incompatible with this protocol and
stored raw events. They now return `410` without reading or storing a payload;
their earlier implementations remain in Git history, not as deployable advice.

## Authorised report import

`analytics/report_import.py` accepts only the aggregate fields named by
`data/campaign-ledger.json`: timestamp, source, channel, date range, eligible
sessions, clicks and reported orders. It cannot authenticate a report. Obtain
one through authorised first-party access first, keep a private dated provenance
trail, and import only fields actually present. Never infer orders from clicks
or fill missing data with zero. No report has been imported; the ledger is empty.

Policy references: [Amazon Program Policies](https://affiliate-program.amazon.com/help/operating/policies)
(technology disclosures, no artificial clicks, no end-user sub-tags),
[tracking-ID reporting](https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA).
This is a technical implementation, not legal certification.


### Server error diagnostics

The production CLI uses `AggregateHTTPServer`, not the stdlib server’s default
`handle_error`. Request access logging alone is insufficient: an expected client
disconnect can otherwise print a client address in a fallback traceback. Expected
transport errors are silent; unexpected errors emit only a fixed diagnostic, with
no exception text, traceback, request, address or payload. Tests assert both paths.
This does not control reverse-proxy/host logs, which still need their own review.
