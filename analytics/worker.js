/** Retired 2026-11-19. Use the canonical aggregate-only Python collector.
 * The former read/modify/write raw-event KV array was not an atomic counter.
 * Preserve the source URL; do not receive, read or store any event payload.
 */
export default {
  async fetch() {
    return new Response(JSON.stringify({ error: "retired_endpoint", replacement: "analytics/collector.py" }), {
      status: 410,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store" }
    });
  }
};
