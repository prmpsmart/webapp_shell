"""Acme Notes' backend: the smallest Starlette app that follows the contract."""

from pathlib import Path

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute, Mount, Route
from starlette.staticfiles import StaticFiles

from webapp_shell import WireProtocol
from webapp_shell.contract import TokenValidator
from webapp_shell.contract.guard import TokenGuard

WIRE = WireProtocol.for_slug("acme")
VERSION = "0.1.0"


async def health(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


async def version(_request: Request) -> JSONResponse:
    return JSONResponse({"version": VERSION})


async def describe(request: Request) -> JSONResponse:
    """What the page sends after the shell gave it a path: the backend only ever sees the path as request data."""
    path = Path(str(request.query_params.get("path", "")))
    if not path.is_file():
        return JSONResponse({"error": "not a file"}, status_code=404)
    return JSONResponse({"name": path.name, "bytes": path.stat().st_size})


def create_app(token: str, frontend: Path | None) -> Starlette:
    routes: list[BaseRoute] = [
        Route("/api/health", health),
        Route("/api/version", version),
        Route("/api/describe", describe),
    ]
    if frontend is not None:
        routes.append(Mount("/", StaticFiles(directory=frontend, html=True)))
    app = Starlette(routes=routes)
    app.add_middleware(TokenGuard, validator=TokenValidator(token, WIRE), wire=WIRE)
    return app


def serve(token: str, frontend: Path | None, port: int, host: str = "127.0.0.1") -> None:
    uvicorn.run(create_app(token, frontend), host=host, port=port, log_level="warning")
