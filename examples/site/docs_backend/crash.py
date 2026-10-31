import os

from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import JSONResponse


async def crash(_request: Request) -> JSONResponse:
    """Answers, then ends the process without cleaning up, as a bug or the system killing it would."""
    return JSONResponse({"stopping": True}, background=BackgroundTask(os._exit, 1))
