#!/usr/bin/env python3
"""
Dispatch local server.

Serves the app AND fetches feeds server-side from your own IP, so there is
no CORS problem, no dependence on public proxies, and no datacenter-IP blocks.
This is the reliable way to run Dispatch.

Usage:
    python3 serve.py
then open  http://localhost:8000  in your browser.

Needs only the Python standard library (Python 3.7+). No pip installs.
"""
import os
import sys
import http.server
import socketserver
import urllib.request
import urllib.parse

PORT = int(os.environ.get("PORT", "8000"))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path.startswith("/proxy?"):
            self.handle_proxy()
        else:
            super().do_GET()

    def handle_proxy(self):
        query = urllib.parse.urlparse(self.path).query
        target = (urllib.parse.parse_qs(query).get("url") or [""])[0]
        if not target.startswith(("http://", "https://")):
            self.send_error(400, "missing or invalid url")
            return
        try:
            req = urllib.request.Request(
                target,
                headers={
                    # A real UA + Accept stops many sites blocking the request.
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0 Safari/537.36 Dispatch-RSS"
                    ),
                    "Accept": (
                        "application/rss+xml, application/atom+xml, "
                        "application/xml, text/xml, */*"
                    ),
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                ctype = resp.headers.get("Content-Type", "application/xml")
        except Exception as exc:  # noqa: BLE001
            self.send_error(502, "fetch failed: %s" % exc)
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass  # keep the console quiet


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    os.chdir(DIRECTORY)
    try:
        server = ThreadingServer(("127.0.0.1", PORT), Handler)
    except OSError as exc:
        print("Could not start on port %d: %s" % (PORT, exc))
        print("Try a different port:  PORT=8090 python3 serve.py")
        sys.exit(1)
    url = "http://localhost:%d" % PORT
    print("Dispatch is running.")
    print("  Open:  %s" % url)
    print("  Stop:  Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
