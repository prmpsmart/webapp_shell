"""Decides whether a candidate is the launch token, and whether a request comes from the app's own page. No HTTP
framework code here."""

import hmac
from collections.abc import Mapping
from urllib.parse import urlsplit

from ..protocol import WireProtocol


class TokenValidator:
    def __init__(self, token: str, wire: WireProtocol):
        self._token = token
        self._wire = wire

    @property
    def token(self) -> str:
        return self._token

    def is_valid(self, candidate: str | None) -> bool:
        # Compared as bytes: `compare_digest` refuses text with non-ASCII characters, which a caller controls.
        return bool(candidate) and hmac.compare_digest(candidate.encode(), self._token.encode())

    def is_valid_connection(
        self, headers: Mapping[str, str], cookies: Mapping[str, str], query: Mapping[str, str]
    ) -> bool:
        """A socket can carry the token in a header (tools), the cookie (the browser) or the query string."""
        wire = self._wire
        candidate = headers.get(wire.token_header) or cookies.get(wire.token_cookie) or query.get(wire.token_query)
        return self.is_valid(candidate)


class OriginPolicy:
    """A browser tells which page made a request in `Origin`. Cookies are shared by every port of a host, so another
    program's page on 127.0.0.1 would otherwise be allowed to call this one: only the app's own page is."""

    def allows(self, origin: str | None, host: str | None) -> bool:
        """True when the request names no origin (a tool, not a page) or the origin is the host being called."""
        if origin is None:
            return True
        return bool(host) and urlsplit(origin).netloc == host
