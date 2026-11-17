/**
 * Zone1 Kitchen - outbound-click endpoint (Cloudflare Worker reference implementation).
 *
 * NOT DEPLOYED BY THIS REPOSITORY. GitHub Pages serves static files only, so
 * this Worker is published as source for the owner to deploy on a Cloudflare
 * account they control. Nothing in this repository sends anything to it until
 * data/config.json -> analytics.endpoint points at a live copy and
 * analytics.enabled is true.
 *
 * It stores exactly the same fields as analytics/endpoint.php and nothing else:
 * event, page, date, asin, tag, page_type, utm, plus a server-side
 * received_at. It never stores the client IP address, the user agent, the
 * referrer, a cookie, or any reader identifier.
 *
 * The one thing a Worker cannot avoid: Cloudflare's own edge logs record the
 * connection. What this code controls is what the site's own event store
 * contains.
 *
 * Deployment:
 *   1. `wrangler init zone1-collect && cd zone1-collect`
 *   2. Copy this file in as src/index.js
 *   3. Create a KV namespace and bind it as COLLECT (wrangler kv:namespace
 *      create COLLECT, then add the binding to wrangler.toml)
 *   4. `wrangler deploy` and note the https URL it prints
 *   5. Set data/config.json -> analytics.endpoint to that URL and
 *      analytics.enabled to true, then rebuild and deploy
 *   6. Confirm one request arrives, then confirm the stored rows contain no
 *      IP address, no user agent and no reader identifier
 *
 * The KV binding is deliberately not created by this repository: a namespace
 * belongs to an account, and a binding written here would point at a
 * namespace that does not exist.
 */

const ALLOWED_ORIGIN = 'https://kanlerxz87-cyber.github.io';
const ALLOWED_EVENTS = new Set(['EV-01', 'EV-02', 'EV-03', 'EV-04']);
const ALLOWED_FIELDS = ['event', 'page', 'date', 'asin', 'tag', 'page_type', 'utm'];
const MAX_BODY_BYTES = 1024;

/** Recognise obvious crawlers so their requests do not pollute the store. */
function isCrawler(userAgent) {
  if (!userAgent) return false;
  const needles = ['bot', 'crawler', 'spider', 'slurp', 'headless', 'preview', 'monitor', 'lighthouse'];
  const ua = userAgent.toLowerCase();
  return needles.some((n) => ua.includes(n));
}

function json(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff',
    },
  });
}

export default {
  async fetch(request, env) {
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ ok: false, error: 'method not allowed' }), {
        status: 405,
        headers: { Allow: 'POST', 'Content-Type': 'application/json' },
      });
    }

    const origin = request.headers.get('Origin');
    if (origin && origin !== ALLOWED_ORIGIN) {
      return json(403, { ok: false, error: 'origin not allowed' });
    }

    const raw = await request.text();
    if (!raw) {
      return json(400, { ok: false, error: 'empty body' });
    }
    if (raw.length > MAX_BODY_BYTES) {
      return json(413, { ok: false, error: 'body too large' });
    }

    let payload;
    try {
      payload = JSON.parse(raw);
    } catch (err) {
      return json(400, { ok: false, error: 'body is not a JSON object' });
    }
    if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
      return json(400, { ok: false, error: 'body is not a JSON object' });
    }

    const event = String(payload.event || '');
    if (!ALLOWED_EVENTS.has(event)) {
      return json(400, { ok: false, error: 'unknown event' });
    }

    // Bot filter. The user agent is used here and nowhere else.
    if (isCrawler(request.headers.get('User-Agent'))) {
      return new Response(null, { status: 204 });
    }

    // Keep only the allowed fields. Anything else the client sends is dropped.
    const row = { event };
    for (const field of ALLOWED_FIELDS) {
      if (field === 'event') continue;
      if (!Object.prototype.hasOwnProperty.call(payload, field)) continue;
      const value = payload[field];
      if (value === null || typeof value !== 'string' && typeof value !== 'number' && typeof value !== 'boolean') {
        continue;
      }
      row[field] = String(value).slice(0, 160);
    }
    // A fixed server-side field: when the line was received. No IP, no UA.
    row.received_at = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');

    if (!env || !env.COLLECT) {
      return json(500, { ok: false, error: 'no COLLECT KV binding is configured' });
    }
    // A dated key, so the store can be rotated or deleted by date without a
    // query language.
    const key = row.date && /^\d{4}-\d{2}-\d{2}$/.test(row.date) ? row.date : 'undated';
    const listKey = `events:${key}`;
    const existing = (await env.COLLECT.get(listKey, 'json')) || [];
    existing.push(row);
    // Keep a bounded window: 10,000 rows per day is far above any plausible
    // traffic for this site and keeps the store small and cheap.
    const trimmed = existing.slice(-10000);
    await env.COLLECT.put(listKey, JSON.stringify(trimmed));

    return new Response(null, { status: 204 });
  },
};
