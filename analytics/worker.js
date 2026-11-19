/** Retired v1 raw-event/KV adapter. No events are accepted, stored or forwarded.
 * The old read-modify-write KV array also lost concurrent increments. Deploy the
 * tested atomic aggregate collector instead; see analytics/README.md.
 */
export default {
  async fetch() {
    return new Response(JSON.stringify({ error: 'retired_adapter', replacement: 'analytics/collector.py' }), {
      status: 410,
      headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }
    });
  }
};
