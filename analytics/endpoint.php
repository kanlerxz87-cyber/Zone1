<?php
/**
 * Zone1 Kitchen - outbound-click endpoint (self-hosted reference implementation).
 *
 * NOT DEPLOYED BY THIS REPOSITORY. GitHub Pages serves static files only, so
 * this script is published as source for the owner to deploy on a host they
 * control. Nothing in this repository sends anything to it until
 * data/config.json -> analytics.endpoint points at a live copy and
 * analytics.enabled is true.
 *
 * What it receives: one JSON object per event, POSTed as text/plain by
 * assets/analytics.js. The client sends at most five fields:
 *
 *   event      "EV-01" | "EV-02" | "EV-03" | "EV-04"
 *   page       the path of the page, relative to the site root, e.g.
 *              "articles/what-450f-actually-means.html"
 *   date       "YYYY-MM-DD" (UTC), taken from the client's clock
 *   asin       the product's ASIN, on EV-02 only
 *   tag        the Associates tracking ID found on the clicked link, EV-02 only
 *   page_type  "article" | "product" | "comparison" | "guide", EV-01 only
 *   utm        "1" when the arrival carried a utm_source/utm_campaign
 *              parameter, EV-01 only
 *
 * What it deliberately does NOT store:
 *   - the client IP address. It is visible to the web server that receives
 *     the request, but this script never writes it into the event file.
 *   - the user agent. It is read once, in memory, only to recognise obvious
 *     crawlers, and is never written.
 *   - the referrer, cookies, or any reader identifier. None is ever sent.
 *
 * Every field that is not on the list above is discarded before the row is
 * written, so a future change to the client cannot silently widen what is
 * collected.
 *
 * Storage: newline-delimited JSON, one object per line, in the file named by
 * $LOG_FILE below. Put that file outside the web root, or deny it with a
 * .htaccess rule, so the raw event stream is not publicly readable.
 *
 * Deployment:
 *   1. Copy this file to your host as e.g. /collect/endpoint.php
 *   2. Point $LOG_FILE at a writable path outside the document root
 *   3. Make sure the host serves it over https
 *   4. Set data/config.json -> analytics.endpoint to the https URL
 *   5. Set analytics.enabled to true, rebuild and deploy
 *   6. Confirm one request arrives, then confirm the stored rows contain no
 *      IP address, no user agent and no reader identifier
 */

declare(strict_types=1);

// Where the newline-delimited event file is written. Change this.
const LOG_FILE = __DIR__ . '/../analytics-data/events.ndjson';

// The site's own origin. A request whose Origin header is not this site is
// refused: the endpoint is for this site's counter and nothing else, and an
// open collector is an abuse target.
const ALLOWED_ORIGIN = 'https://kanlerxz87-cyber.github.io';

// The only event names the client may send.
const ALLOWED_EVENTS = ['EV-01', 'EV-02', 'EV-03', 'EV-04'];

// The only fields that are ever stored.
const ALLOWED_FIELDS = ['event', 'page', 'date', 'asin', 'tag', 'page_type', 'utm'];

// Largest body accepted, in bytes. The real payload is under 200 bytes.
const MAX_BODY_BYTES = 1024;

/**
 * Recognise obvious crawlers so their requests do not pollute the event file.
 * The user agent is compared here and then discarded; it is never stored.
 */
function is_crawler(string $ua): bool
{
    if ($ua === '') {
        return false;
    }
    foreach (['bot', 'crawler', 'spider', 'slurp', 'headless', 'preview', 'monitor', 'lighthouse'] as $needle) {
        if (stripos($ua, $needle) !== false) {
            return true;
        }
    }
    return false;
}

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'method not allowed']);
    exit;
}

$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin !== '' && $origin !== ALLOWED_ORIGIN) {
    http_response_code(403);
    echo json_encode(['ok' => false, 'error' => 'origin not allowed']);
    exit;
}

$raw = file_get_contents('php://input');
if ($raw === false || $raw === '') {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'empty body']);
    exit;
}
if (strlen($raw) > MAX_BODY_BYTES) {
    http_response_code(413);
    echo json_encode(['ok' => false, 'error' => 'body too large']);
    exit;
}

$payload = json_decode($raw, true);
if (!is_array($payload)) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'body is not a JSON object']);
    exit;
}

$event = (string)($payload['event'] ?? '');
if (!in_array($event, ALLOWED_EVENTS, true)) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'unknown event']);
    exit;
}

// Bot filter. The user agent is used here and nowhere else.
if (is_crawler((string)($_SERVER['HTTP_USER_AGENT'] ?? ''))) {
    http_response_code(204);
    exit;
}

// Keep only the allowed fields, with the allowed shapes. Anything else the
// client sends is dropped here rather than stored.
$row = [];
foreach (ALLOWED_FIELDS as $field) {
    if (!array_key_exists($field, $payload)) {
        continue;
    }
    $value = $payload[$field];
    if (!is_scalar($value)) {
        continue;
    }
    $value = (string)$value;
    if (strlen($value) > 160) {
        $value = substr($value, 0, 160);
    }
    $row[$field] = $value;
}
$row['event'] = $event;

// A fixed server-side field: when the line was received. No IP, no user agent.
$row['received_at'] = gmdate('Y-m-d\TH:i:s\Z');

$dir = dirname(LOG_FILE);
if (!is_dir($dir) && !@mkdir($dir, 0775, true) && !is_dir($dir)) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'log directory is not writable']);
    exit;
}

$line = json_encode($row, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
if ($line === false || @file_put_contents(LOG_FILE, $line . "\n", FILE_APPEND | LOCK_EX) === false) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'could not write the event']);
    exit;
}

http_response_code(204);
exit;
