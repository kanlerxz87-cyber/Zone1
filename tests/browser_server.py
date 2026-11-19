#!/usr/bin/env python3
"""Ephemeral HTTPS browser-test fixture, never a production/preview collector.

It serves the committed static publication plus explicitly enabled test-only pages.
The latter call the actual production CollectorHandler over same-origin HTTPS into
one TemporaryDirectory database outside Git. No repository config/ledger is changed.
The /__test/* routes do not exist in analytics/collector.py or the published site.
"""
from __future__ import annotations

import importlib.util
import json
import os
import signal
import sqlite3
import ssl
import subprocess
import sys
import tempfile
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    build = module("browser_fixture_build", ROOT / "build.py")
    collector = module("browser_fixture_collector", ROOT / "analytics/collector.py")
    port = int(os.environ.get("ZONE1_TEST_PORT", "8123"))
    origin = f"https://localhost:{port}"
    with tempfile.TemporaryDirectory(prefix="zone1-browser-fixture-") as temp:
        tmp = Path(temp)
        database = tmp / "synthetic.sqlite3"
        key, cert = tmp / "key.pem", tmp / "cert.pem"
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1",
            "-subj", "/CN=localhost", "-keyout", str(key), "-out", str(cert),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        Handler = collector.make_handler({
            "ZONE1_ANALYTICS_ENABLED": "1",
            "ZONE1_ANALYTICS_PRIVACY_NOTICE_APPROVED": "1",
            "ZONE1_ANALYTICS_PUBLIC_ORIGIN": origin,
            "ZONE1_ANALYTICS_DB_PATH": str(database),
        })
        # These switches apply only inside this test process. The files stay disabled.
        build.ANALYTICS_ON = True
        build.ANALYTICS_ENDPOINT = "/api/analytics/events"
        fixtures = {
            "/__test/product.html": build.page_product(build.PRODUCT_LIST[0]),
            "/__test/compare.html": build.page_compare(),
            "/__test/article.html": build.page_article(build.ARTICLES["articles"][0]),
        }
        fixtures = {path: text.replace('="assets/', '="/assets/').replace('href="products/', 'href="/products/') for path, text in fixtures.items()}

        class FixtureHandler(Handler, SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(ROOT), **kwargs)

            def json_response(self, body):
                encoded = json.dumps(body).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def do_GET(self):  # noqa: N802
                path = urlsplit(self.path).path
                if path == "/__test/ready":
                    return self.json_response({"fixture": True, "production": False})
                if path == "/__test/stats":
                    rows = []
                    if database.exists():
                        with sqlite3.connect(database) as connection:
                            try:
                                connection.row_factory = sqlite3.Row
                                rows = [dict(r) for r in connection.execute("SELECT * FROM daily_events")]
                            except sqlite3.OperationalError:
                                pass
                    return self.json_response(rows)
                if path in fixtures:
                    content = fixtures[path].encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                return SimpleHTTPRequestHandler.do_GET(self)

            def do_POST(self):  # noqa: N802
                if self.path == "/__test/reset":
                    if database.exists():
                        with sqlite3.connect(database) as connection:
                            try:
                                connection.execute("DELETE FROM daily_events")
                            except sqlite3.OperationalError:
                                pass
                    return self.json_response({"reset": "synthetic fixture only"})
                return Handler.do_POST(self)

        server = collector.AggregateHTTPServer(("0.0.0.0", port), FixtureHandler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert, keyfile=key)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
        print(f"Synthetic browser fixture ready: {origin}; no production config changed", flush=True)
        try:
            server.serve_forever()
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
