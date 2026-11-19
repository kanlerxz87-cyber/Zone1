/* Retired 2026-11-19: the old raw-event schema was incompatible with the
   canonical daily-aggregate contract. No body, header or event is retained.
   Deploy analytics/collector.py using analytics/README.md instead. */
export default {
  async fetch() {
    return new Response(JSON.stringify({ error: 'legacy_collector_retired' }), {
      status: 410,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Cache-Control': 'no-store',
        'X-Content-Type-Options': 'nosniff'
      }
    });
  }
};
