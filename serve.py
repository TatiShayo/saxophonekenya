#!/usr/bin/env python3
"""
serve.py — Local development server for the Frederic Sax Ke site.
==========================================================================
* Runs the build first, so edits under `partials/`, `css/` or `js/` are
  never stale in `index.html`.
* Binds to 127.0.0.1 by default, not 0.0.0.0.
  The old server bound 0.0.0.0, which on a public Wi-Fi network exposed the
  whole site — and, with no access control, the 82 MB deployment archives —
  to every other device on the LAN. `--host 0.0.0.0` is still available but
  must now be passed explicitly and deliberately.
* Sends no-store cache headers so a reload always reflects the latest edit.
* Sends no cross-origin CORS header.
  The old server sent a wildcard origin, which meant any website in the
  world could have read responses from it. Nothing on this site is fetched
  cross-origin, so the header had no legitimate use and was pure attack
  surface.
"""

from __future__ import annotations

import argparse
import os
import socket
import socketserver
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class DevHandler(SimpleHTTPRequestHandler):
    """Static file handler with strict, no-store cache semantics.

    Also implements extensionless routing (`/rate-card` -> `rate-card.html`)
    so local development behaves the same way production does: Vercel does
    this via `cleanUrls`, Apache via the mod_rewrite rules in .htaccess.
    """

    server_version = "FredericSaxKeDev/3.0"

    def do_GET(self):
        path = self.translate_path(self.path)
        if not os.path.exists(path) and not self.path.endswith("/"):
            candidate = path + ".html"
            if os.path.isfile(candidate):
                self.path = self.path + ".html"
        return super().do_GET()

    def end_headers(self) -> None:
        # Never cache during development.
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        # No permissive CORS. See module docstring.
        super().end_headers()

    def version_string(self) -> str:  # hide the default Server header
        return self.server_version

    def log_message(self, fmt: str, *args) -> None:  # quieter console
        sys.stderr.write("  %s\n" % (fmt % args))

    def send_error(self, code, message=None, explain=None):
        """Serve our own 404 page instead of the plain-text default."""
        if code == 404 and (ROOT / "404.html").exists():
            try:
                body = (ROOT / "404.html").read_bytes()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except OSError:
                pass
        super().send_error(code, message, explain)


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    """Allow an immediate restart without 'Address already in use'."""
    allow_reuse_address = True
    daemon_threads = True


def run_build() -> bool:
    """Rebuild index.html from partials/ before serving."""
    build = ROOT / "build.py"
    if not build.exists():
        print("[build] build.py not found — serving the existing output.")
        return True

    print("[build] assembling partials/ -> index.html")
    result = subprocess.run(
        [sys.executable, str(build)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
        print("[build] FAILED — serving the previous index.html.", file=sys.stderr)
        return False
    return True


def free_port(port: int) -> int:
    """If the port is taken, find the next free one so the server still starts."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
            return port
        except OSError:
            for candidate in range(port + 1, port + 40):
                try:
                    sock.bind(("127.0.0.1", candidate))
                    return candidate
                except OSError:
                    continue
    raise SystemExit(f"No free port found in {port}–{port + 40}.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Frederic Sax Ke dev server",
        epilog="Both 'python serve.py 8080' and 'python serve.py --port 8080' work.",
    )
    parser.add_argument("port", nargs="?", type=int, default=None,
                        help="Port to listen on (default 8080)")
    parser.add_argument("--port", dest="port_flag", type=int, default=None,
                        help="Port to listen on (alternative to the positional form)")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Bind address. Use 0.0.0.0 ONLY on a trusted, "
                             "password-protected network.")
    parser.add_argument("--no-build", action="store_true",
                        help="Skip the partial build step")
    args = parser.parse_args()

    port = args.port or args.port_flag or 8080

    if not args.no_build:
        run_build()

    os.chdir(ROOT)

    port = free_port(port) if args.host == "127.0.0.1" else port
    display_host = "localhost" if args.host in ("127.0.0.1", "0.0.0.0") else args.host

    httpd = ReusableThreadingHTTPServer((args.host, port), DevHandler)

    print()
    print("=" * 68)
    print("  Frederic Sax Ke — development server")
    print("=" * 68)
    print(f"  Serving  : {ROOT}")
    print(f"  URL      : http://{display_host}:{port}/")
    print(f"  Rate card: http://{display_host}:{port}/rate-card.html")
    if args.host == "0.0.0.0":
        print("  WARNING  : bound to 0.0.0.0 — exposed to the whole network")
    print("=" * 68)
    print("  Ctrl+C to stop\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[stop] shutting down")
    finally:
        httpd.server_close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
