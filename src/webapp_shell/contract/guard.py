"""HTTP access control for a Starlette or FastAPI backend: the launch token, from a header or a cookie.

    app.add_middleware(TokenGuard, validator=TokenValidator(token, wire), wire=wire)

Needs `starlette` (`pip install "webapp-shell[backend]"`).
"""

from dataclasses import dataclass, field

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from ..protocol import WireProtocol
from .tokens import OriginPolicy, TokenValidator

ORIGIN_HEADER = "origin"
HOST_HEADER = "host"


@dataclass(frozen=True)
class GuardResponses:
    """What a refused request gets back. A project with its own error format replaces them."""

    unauthorized: dict = field(default_factory=lambda: {"code": "UNAUTHORIZED"})
    foreign_origin: dict = field(default_factory=lambda: {"code": "FOREIGN_ORIGIN"})


class TokenGuard(BaseHTTPMiddleware):
    """Protects the API with the launch token.

    Opening the app with `/?token=...` turns the token into a cookie and redirects to the clean URL,
    so a launcher only has to open one URL and needs no cookie code of its own.
    """

    def __init__(
        self,
        app,
        validator: TokenValidator,
        wire: WireProtocol,
        origins: OriginPolicy | None = None,
        responses: GuardResponses | None = None,
    ):
        super().__init__(app)
        self._validator = validator
        self._wire = wire
        self._origins = origins or OriginPolicy()
        self._responses = responses or GuardResponses()

    def _bearer(self, request: Request) -> str | None:
        return request.headers.get(self._wire.token_header) or request.cookies.get(self._wire.token_cookie)

    def _bootstrap_session(self, request: Request) -> RedirectResponse:
        response = RedirectResponse(str(request.url.remove_query_params(self._wire.token_query)))
        response.set_cookie(self._wire.token_cookie, self._validator.token, httponly=True, samesite="strict")
        return response

    async def dispatch(self, request: Request, call_next):
        wire = self._wire
        path = request.url.path
        in_api = path.startswith(wire.api_prefix)
        if self._validator.is_valid(request.query_params.get(wire.token_query)) and not in_api:
            return self._bootstrap_session(request)
        if in_api and not self._origins.allows(request.headers.get(ORIGIN_HEADER), request.headers.get(HOST_HEADER)):
            return JSONResponse(self._responses.foreign_origin, status_code=403)
        if in_api and path != wire.health_path and not self._validator.is_valid(self._bearer(request)):
            return JSONResponse(self._responses.unauthorized, status_code=401)
        return await call_next(request)
