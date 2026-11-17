/**
 * Zone1 — reference analytics collector.
 *
 * This is the server half of the contract published on measurement.html and
 * defined in data/analytics.json. It is written for a Cloudflare Worker, but
 * nothing about it depends on that platform: it is a request handler that
 * accepts one JSON shape, keeps aggregates, and throws away everything that
 * could identify a person.
 *
 * WHY IT EXISTS SEPARATELY
 *   GitHub Pages serves static files. It cannot run this. A self-hosted
 *   endpoint has to run somewhere that executes code. Deploying this anywhere
 *   and putting its URL in data/analytics.json turns collection on with no
 *   other change — and, because the footer notice is generated from that same
 *   file, the privacy statement updates in the same commit.
 *
 * WHAT IT REFUSES TO STORE
 *   - the client IP address (a coarse country is derived in memory, then dropped)
 *   - the user agent string (a single isBot boolean is derived, then dropped)
 *   - any cookie, any identifier, any cross-site ID
 *   - any field outside the published payload shape
 *
 * There is deliberately no way to join two events to the same visitor. The
 * counter counts events, not people; two visits are indistinguishable, which
 * is the property that keeps the site's "sets no cookies" statement true.
 */

const ALLOWED_FIELDS = new Set(['e', 'p', 'r', 'a', 'l', 'v']);
const ALLOWED_EVENTS = new Set([
  'page_view', 'guide_read', 'chooser_complete', 'outbound_click', 'subscribe',
]);

const RETENTION_DAYS = 14;

export default {
  async fetch(request, env) {
    // ---- reject anything that is not a plain POST of a known shape ---------
    if (request.method !== 'POST') {
      return new Response(null, { status: 405 });
    }
    if (request.headers.get('cookie') || request.headers.get('authorization')) {
      return new Response(null, { status: 400 });
    }

    let body;
    try {
      body = await request.json();
    } catch (err) {
      return new Response(null, { status: 400 });
    }
    if (!body || typeof body !== 'object' || Array.isArray(body)) {
      return new Response(null, { status: 400 });
    }
    for (const key of Object.keys(body)) {
      if (!ALLOWED_FIELDS.has(key)) return new Response(null, { status: 400 });
    }
    if (!ALLOWED_EVENTS.has(body.e)) return new Response(null, { status: 400 });

    // ---- derive the two allowed facts, then discard the inputs -------------
    const ip = request.headers.get('cf-ipcountry') || '';
    const country = typeof ip === 'string' ? ip.slice(0, 2).toUpperCase() : '';
    const ua = request.headers.get('user-agent') || '';
    const isBot = /bot|crawler|spider|crawling|preview|fetcher|monitor/i.test(ua);
    // `ua` and the real IP are never written anywhere; they go out of scope here.

    // ---- keep an aggregate, never an event log ----------------------------
    const day = new Date().toISOString().slice(0, 10);
    const key = `z1:${day}:${body.e}:${body.p || ''}:${body.a || ''}:${country}:${isBot ? 1 : 0}`;
    const prior = Number((await env.Z1_COUNTS.get(key)) || 0);
    await env.Z1_COUNTS.put(key, String(prior + 1), {
      expirationTtl: RETENTION_DAYS * 86400,
    });

    return new Response(null, {
      status: 204,
      headers: { 'cache-control': 'no-store' },
    });
  },
};

/**
 * Reading it back
 * ---------------
 * The bucket keys are the report. `z1:2026-11-17:outbound_click:/products/x.html:B0CDY277D3::0`
 * reads as: on that day, that many outbound clicks for that ASIN from that page,
 * from visitors whose country was unknown, who did not look like a bot.
 *
 * Orders and earnings do NOT come from here. They come from Amazon Associates
 * Central and go into the campaign ledger, which stays empty until a real
 * report fills it. See data/ledger.json.
 */
