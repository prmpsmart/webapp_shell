"""`python -m fake_backend --port N --frontend DIR [...]`: answers the health and version paths, needs the token."""

import json
import os
import socketserver
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN_ENV = "ACME_TOKEN"
TOKEN_HEADER = "x-acme-token"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/api/health":
            return self._send(200, {"ok": True})
        if self.path == "/api/version":
            if self.headers.get(TOKEN_HEADER) != os.environ.get(TOKEN_ENV):
                return self._send(401, {"detail": "token"})
            return self._send(200, {"version": "1.2.3", "argv": sys.argv[1:]})
        self._send(404, {})

    def _send(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_args) -> None:
        pass


class Server(HTTPServer):
    def server_bind(self) -> None:
        """`HTTPServer` asks the name service for the host's full name while binding, which can take half a minute on a
        busy macOS machine; the test backend has no use for it."""
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = self.server_address[0], self.server_address[1]


def main(argv: list[str]) -> None:
    port = int(argv[argv.index("--port") + 1])
    Server(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
