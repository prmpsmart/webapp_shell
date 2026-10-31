"""The documentation site's backend: the contract, plus one route per live demonstration."""

from pathlib import Path

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from webapp_shell.contract import TokenValidator
from webapp_shell.contract.guard import TokenGuard
from webapp_shell.protocol import WireProtocol

from .crash import crash
from .describe import describe
from .job import job_status, start_job
from .list_folder import list_folder
from .save_note import save_note

WIRE = WireProtocol.for_slug("docs")
VERSION = "0.1.0"


async def health(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


async def version(_request: Request) -> JSONResponse:
    return JSONResponse({"version": VERSION})


def create_app(token: str, frontend: Path | None) -> Starlette:
    routes = [
        Route(WIRE.health_path, health),
        Route(WIRE.version_path, version),
        Route(f"{WIRE.api_prefix}/describe", describe),
        Route(f"{WIRE.api_prefix}/folder", list_folder),
        Route(f"{WIRE.api_prefix}/job", start_job, methods=["POST"]),
        Route(f"{WIRE.api_prefix}/job", job_status),
        Route(f"{WIRE.api_prefix}/crash", crash, methods=["POST"]),
        Route(f"{WIRE.api_prefix}/save", save_note, methods=["POST"]),
    ]
    if frontend is not None:
        routes.append(Mount("/", StaticFiles(directory=frontend, html=True)))
    app = Starlette(routes=routes)
    app.add_middleware(TokenGuard, validator=TokenValidator(token, WIRE), wire=WIRE)
    return app


def serve(token: str, frontend: Path | None, port: int, host: str = "127.0.0.1") -> None:
    uvicorn.run(create_app(token, frontend), host=host, port=port, log_level="warning")
