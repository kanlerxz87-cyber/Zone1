<?php
/** Retired 2026-11-19. This legacy raw-event schema was not compatible with the
 * supported aggregate collector. Fail closed; do not retain request bodies.
 * Use analytics/collector.py and the deployment gates in analytics/README.md.
 */
declare(strict_types=1);
http_response_code(410);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
echo json_encode(['error' => 'legacy_collector_retired']);
