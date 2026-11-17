# The outbound-click endpoint — source for a host you control

**Nothing here is deployed, and nothing here is sending.** This folder is the
source code for the endpoint that the site's outbound-click counter posts to.
The site is static files on GitHub Pages, which cannot receive a `POST`, so the
sink has to live on a host the account holder controls. This repository builds
the counter (`assets/analytics.js`) and ships it with the switch **off**; it
cannot and does not run the sink.

| File | What it is |
|---|---|
| `endpoint.php` | Reference implementation for any PHP host (Apache, nginx + PHP-FPM, cPanel). Writes newline-delimited JSON to a file. |
| `worker.js` | Reference implementation for Cloudflare Workers. Writes to a KV namespace. |

Both store the **same seven fields** and nothing else:

| Field | Meaning |
|---|---|
| `event` | `EV-01` page view · `EV-02` outbound product click · `EV-03` article finished · `EV-04` comparison table seen |
| `page` | the path of the page, relative to the site root |
| `date` | `YYYY-MM-DD`, UTC, from the client's clock |
| `asin` | the product's ASIN (EV-02 only) |
| `tag` | the Associates tracking ID found on the clicked link (EV-02 only) |
| `page_type` | `article` · `product` · `comparison` · `guide` (EV-01 only) |
| `utm` | `1` when the arrival carried a `utm_source`/`utm_campaign` parameter (EV-01 only) |

Plus one field the server adds: `received_at`, the UTC time the line was
written.

## What is never stored

* **The client IP address.** It is visible to the web server that receives the
  request — that is unavoidable and outside the site's control — but neither
  implementation writes it into the event store.
* **The user agent.** It is read once, in memory, only to recognise obvious
  crawlers, and is then discarded.
* **The referrer, cookies, and any reader identifier.** None is ever sent by
  the client, and the endpoints refuse any field outside the list above.
* **Anything about an order.** The counter never sees what the reader bought.
  Reported orders come only from an Amazon Associates Central report, entered
  by hand into the campaign ledger.

The `assets/analytics.js` client is checked by the build guard
`check_analytics_consistency()`, which fails the build if the file contains
`document.cookie`, `localStorage`, `sessionStorage`, `indexedDB`,
`navigator.userAgent`, `document.referrer` or `window.name`, if it calls
`preventDefault()`, or if it does not check `event.isTrusted`.

## Why it stays off until you turn it on

Program Policies §3(e) requires an accurate statement of cookie and
third-party technology use on an Associate site, and §3(s) forbids
artificially generating clicks. Two consequences:

1. A counter with no sink behind it would report a number this site cannot
   source, so it ships **disabled**.
2. The footer's cookie/privacy paragraph is **generated from the same
   configuration block** that turns the counter on, so the statement cannot
   describe a behaviour the page does not have. When you switch the counter on,
   the build will also fail until every published sentence that says the site
   "runs no analytics" — in the footer *and* in the registers, which are
   quoted onto the pages — has been updated in the same commit. That failure is
   the guard working, not a nuisance: those sentences become false the moment
   the counter starts sending.

## Turning it on

1. Deploy one of the two files above on a host you control, over **https**.
   For the PHP version, put the NDJSON file outside the document root, or deny
   it with a `.htaccess` rule.
2. In `data/config.json`, set `analytics.enabled` to `true` and
   `analytics.endpoint` to the absolute `https://` URL of that endpoint.
3. Rebuild and deploy: `python3 build.py`.
4. The build will stop with a list of the published sentences that are now
   false. Update each one, and the register it is quoted from, in the same
   commit. The guard names the file for you.
5. Click a product link on the live site and confirm one request arrives.
6. Open the stored rows and confirm they contain **no IP address, no user
   agent and no reader identifier**. If they do, the endpoint is wrong, not the
   counter.

The enable procedure is also written out in `data/config.json` →
`analytics.enable_procedure`, and the events themselves are defined in
`data/measurement.json`.

## Reading the data afterwards

The event file is one JSON object per line, so it reads with ordinary tools:

```bash
# how many outbound product clicks, by ASIN
jq -r 'select(.event=="EV-02") | .asin' events.ndjson | sort | uniq -c | sort -rn

# which pages readers click from
jq -r 'select(.event=="EV-02") | .page' events.ndjson | sort | uniq -c | sort -rn

# every day, in order
jq -r '[.date, .event] | @tsv' events.ndjson | sort | uniq -c
```

A click count from this file is a **first-party measurement of a click**. It is
not a conversion, not an order, and not revenue. Reported orders come from the
Amazon Associates report and are entered into the campaign ledger by hand — see
`data/campaign-ledger.json` and `measurement.html`. The ledger stays empty until
a report is actually read; a filled ledger with invented numbers would be worse
than an empty one.
