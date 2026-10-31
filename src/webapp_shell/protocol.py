"""The names the shell and a backend must agree on. The backend reads the same names; the library never invents them
silently: `for_slug` gives a consistent default set and a project may write its own."""

import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class WireProtocol:
    token_header: str  # how an API call proves it comes from this launch
    token_cookie: str  # what the backend turns the first token into
    token_query: str  # where the launch URL carries the token once
    token_env: str  # how the shell hands the token over (a command line is visible to other users)
    api_prefix: str  # everything below it needs the token, except the health path
    health_path: str  # answers 200 when the backend is ready
    version_path: str | None  # answers JSON with a "version"; None when the backend has none
    ws_close_unauthorized: int = 4401  # the close code of a socket that came without a valid token

    @classmethod
    def for_slug(cls, slug: str) -> "WireProtocol":
        return cls(
            token_header=f"x-{slug}-token",
            token_cookie=f"{slug}_token",
            token_query="token",
            token_env=f"{slug.upper()}_TOKEN",
            api_prefix="/api",
            health_path="/api/health",
            version_path="/api/version",
        )

    def token_from_environment(self, environ: Mapping[str, str] | None = None) -> str | None:
        """The token the shell handed over, read by the backend."""
        return (os.environ if environ is None else environ).get(self.token_env)
