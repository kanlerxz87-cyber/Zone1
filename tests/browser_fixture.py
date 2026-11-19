#!/usr/bin/env python3
"""Local HTTPS test fixture, NEVER a production service or analytics deployment.

Uses the real collector with an ephemeral database outside the checkout. The
/__enabled__/ prefix injects build.py's actual emitter into disabled generated
pages, only in the response. No configuration, production HTML or ledger changes.
"""
import json
import mimetypes
import signal
import sqlite3
import ssl
import subprocess
import sys
import tempfile
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402
from analytics.collector import make_handler  # noqa: E402


def run():
    with tempfile.TemporaryDirectory(prefix='zone1-browser-fixture-') as tmp:
        temp = Path(tmp)
        key, cert, database = temp / 'fixture.key', temp / 'fixture.crt', temp / 'fixture.sqlite3'
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                        '-keyout', str(key), '-out', str(cert), '-days', '1',
                        '-subj', '/CN=127.0.0.1', '-addext', 'subjectAltName=IP:127.0.0.1'],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Reserve the port before deriving the exact allowed HTTPS Origin.
        server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler({}))
        origin = f'https://127.0.0.1:{server.server_port}'
        parent = make_handler({'ZONE1_ANALYTICS_ENABLED': '1',
            'ZONE1_ANALYTICS_PRIVACY_NOTICE_APPROVED': '1',
            'ZONE1_ANALYTICS_PUBLIC_ORIGIN': origin,
            'ZONE1_ANALYTICS_DB_PATH': str(database)})
        seen = []

        class Handler(parent):
            def do_POST(self):
                # Test assertion data held only in this process, never app storage.
                seen.append({'cookie': bool(self.headers.get('Cookie')),
                             'referrer': bool(self.headers.get('Referer')),
                             'origin': self.headers.get('Origin'),
                             'content_type': self.headers.get('Content-Type')})
                super().do_POST()

            def do_GET(self):
                path = unquote(urlsplit(self.path).path)
                if path == '/__fixture_state__':
                    rows = []
                    if database.exists():
                        with sqlite3.connect(database) as db:
                            rows = [dict(zip(('day', 'event', 'page_id', 'target_id', 'bucket', 'count'), row))
                                    for row in db.execute('SELECT day,event,page_id,target_id,bucket,count FROM daily_events ORDER BY event,page_id')]
                    body = json.dumps({'rows': rows, 'headers': seen}).encode()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                enabled = path.startswith('/__enabled__/')
                rel = path.removeprefix('/__enabled__/' if enabled else '/').rstrip('/') or 'index.html'
                file = (ROOT / rel).resolve()
                if not file.is_relative_to(ROOT) or not file.is_file() or file.suffix not in ('.html', '.css', '.js', '.svg', '.png', '.webp', '.xml'):
                    self.send_error(404)
                    return
                body = file.read_bytes()
                if enabled and file.suffix == '.html':
                    with patch.object(build, 'ANALYTICS_ON', True), patch.object(build, 'ANALYTICS_ENDPOINT', '/api/analytics/events'):
                        tag = build.analytics_script_tag(rel)
                    body = body.replace(b'</body>', (tag + '</body>').encode())
                self.send_response(200)
                self.send_header('Content-Type', mimetypes.guess_type(file.name)[0] or 'application/octet-stream')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        server.RequestHandlerClass = Handler
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls.load_cert_chain(cert, key)
        server.socket = tls.wrap_socket(server.socket, server_side=True)
        print(json.dumps({'origin': origin, 'fixture': True}), flush=True)
        signal.signal(signal.SIGTERM, lambda *_args: (_ for _ in ()).throw(KeyboardInterrupt()))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == '__main__':
    run()
