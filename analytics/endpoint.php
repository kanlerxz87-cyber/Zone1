<?php
/** Retired 2026-11-19: the old raw-event schema did not match the collector plan.
 * Use analytics/collector.py behind a same-origin HTTPS route instead.
 * This tombstone preserves existing source links without accepting or storing events.
 */
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
http_response_code(410);
echo '{"error":"retired_endpoint","replacement":"analytics/collector.py"}';
