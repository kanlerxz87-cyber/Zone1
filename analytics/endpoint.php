<?php
/** Retired v1 raw-event adapter. It cannot satisfy the v2 aggregate-only contract.
 * Kept at its old path so a stale deployment fails closed rather than silently
 * collecting an incompatible event stream. See analytics/README.md for the
 * supported Python collector. This script performs no storage or forwarding.
 */
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
http_response_code(410);
echo json_encode(['error' => 'retired_adapter', 'replacement' => 'analytics/collector.py']);
