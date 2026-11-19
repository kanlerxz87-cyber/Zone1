# Zone1 first-party measurement

**Production state: disabled.** The GitHub Pages site has no deployed application runtime or
same-origin event route. No production counts, sessions, orders, conversion rates or revenue
have been measured by this implementation. Local test events are fixtures, not traffic.

## One schema, five events

[`data/analytics-plan.json`](../data/analytics-plan.json) is the canonical definition.
`data/measurement.json` is its build-checked readable projection, not a second event protocol.
The browser and collector use the **same named events and payloads**:

| ID | Name | Trigger | Allowed payload beyond event name | Definition / official context |
|---|---|---|---|---|
| EV-01 | `page_view` | First visible, non-prerendered display of a publication page | `page_id` | [Schema](../data/analytics-plan.json); [accurate privacy disclosures](https://affiliate-program.amazon.com/help/operating/policies) |
| EV-02 | `outbound_click` | Trusted primary, keyboard or middle-button activation of an explicitly marked supplied product link | `page_id`, `target_id` | [Schema](../data/analytics-plan.json); [no artificial clicks, Participation Requirements 6(s)](https://affiliate-program.amazon.com/help/operating/policies) |
| EV-03 | `article_engagement` | Individual article/guide visible and focused for 60 coarse one-second intervals | `page_id`, `bucket: "60s"` | [Schema](../data/analytics-plan.json); [privacy requirements](https://affiliate-program.amazon.com/help/operating/policies) |
| EV-04 | `comparison_interaction` | Trusted activation of a marked product-detail link on the comparison page | `page_id: "compare"`, `target_id` | [Schema](../data/analytics-plan.json); [privacy requirements](https://affiliate-program.amazon.com/help/operating/policies) |
| EV-05 | `affiliate_report_import` | Explicit import of an authorized aggregate report into the campaign ledger; **never a browser event** | Ledger report fields, not customer/order IDs | [Importer](report_import.py); [Tracking ID Summary Report](https://affiliate-program.amazon.com/help/node/topic/GJDYPQZK6E37RLPU) |

Engagement is not article completion. An interaction is not a table impression. A click is not
an order, a page view is not a unique person/session, and an absent report is not zero orders.
The endpoint is an aggregate counter, not an independent anti-fraud or attribution system.

## Implementation

- `client.js` is the reviewed browser source. `build.py` publishes it verbatim as
  `assets/analytics.js`; pages do not load it while collection is disabled.
- `collector.py` is the canonical stdlib-only Python HTTP service. It validates exact page/link
  IDs and a bounded JSON schema, then atomically increments **UTC-day SQLite aggregates**.
  It stores no raw event rows. The database must live outside the checkout and web root.
- `report_import.py` validates an explicit first-party aggregate report row and appends it
  atomically/idempotently to the empty campaign ledger. It does not fetch Associates Central,
  authenticate a report, or infer orders from clicks.
- `endpoint.php` and `worker.js` are **retired**. Their old EV-ID/raw-event protocol disagreed
  with the collector schema; the Worker also used a non-atomic array update. Both now return
  HTTP 410 and collect nothing. Do not deploy them.

## Privacy boundaries

The client uses same-origin `application/json` fetch with credentials omitted and a no-referrer
policy. It sends no IP, user agent, cookies, full URLs, query strings, referrers or persistent
reader identifiers; it uses no browser storage. DNT and Global Privacy Control suppress
collection, as do browser automation and prerendered/hidden displays. Link activations never
wait for measurement and are never redirected through a counter.

The server disables its own HTTP access log. **Hosting infrastructure necessarily sees
connection metadata**, and any proxy/CDN retention requires its own review. GitHub explicitly
[documents security IP logging for Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection).
The owner decision picker's local-only storage is separate and is disclosed in the footer.

## Deployment gate (not completed)

1. Provision a durable HTTPS host **and a same-origin reverse-proxy route**
   `/api/analytics/events`. GitHub Pages is a [static host](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages);
   checking this repository out does not provision a server, DNS or a proxy.
2. Review the actual visitor notice, host/proxy access logging, aggregate retention (proposed
   395 days), operational security and applicable privacy obligations. No conformance to a
   privacy law is asserted by these tests.
3. Run the service on that controlled host, behind TLS, for example:

   ```bash
   ZONE1_ANALYTICS_ENABLED=1 \
   ZONE1_ANALYTICS_PRIVACY_NOTICE_APPROVED=1 \
   ZONE1_ANALYTICS_PUBLIC_ORIGIN=https://YOUR-ACTUAL-PUBLIC-ORIGIN \
   ZONE1_ANALYTICS_DB_PATH=/srv/zone1-private/events.sqlite3 \
   ZONE1_ANALYTICS_BIND=127.0.0.1 \
   python3 analytics/collector.py
   ```

   The origin is the HTTPS scheme and hostname only. Use the real approved origin, not the
   example. Bind the private collector to loopback behind the host's reverse proxy; expose
   only the TLS route. No browser code should call localhost or the private collector port.
4. Record `runtime_selected`, `endpoint_deployed`, `privacy_notice_approved` and
   `collection.enabled` in `data/analytics-plan.json`. Set `analytics.enabled` in
   `data/config.json` in the same change, with `analytics.endpoint` set to
   `/api/analytics/events`. The build rejects partial enablement or a cross-origin endpoint.
5. Run the tests below, then a controlled end-to-end test against the deployed route.
   Inspect aggregate table columns and host/proxy log settings. Publish measured totals only
   after obtaining authorized reports, with a timestamp and provenance. Test requests must
   not be mixed with real-traffic reporting.

No hosting credentials, account access or approved notice exist in this session, so neither
switch has been enabled. Starting a temporary sandbox server is not production deployment.

## Verification

```bash
python3 -m unittest discover -s tests -v
node --test tests/analytics-client.test.cjs
python3 build.py
python3 verify.py
```

The JavaScript contract tests generate payloads from the actual client and pass them through
the actual Python validator. HTTP tests exercise disabled/allowed/origin-rejected requests
and inspect the resulting SQLite aggregates. Schema, privacy, retention and configuration
failures are regression-tested; no test opens an affiliate link or orders a product.

An authorized report import is an explicit command, not a background scraper:

```bash
python3 analytics/report_import.py /secure/path/to/authorized-aggregate-row.json
```

Do not commit raw reports, credentials, analytics databases or customer data.
