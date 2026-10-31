from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse


async def describe(request: Request) -> JSONResponse:
    """The shell gave the page a path; the page sent it here. The backend only sees ordinary request data."""
    path = Path(str(request.query_params.get("path", "")))
    if not path.is_file():
        return JSONResponse({"error": "not a file"}, status_code=404)
    return JSONResponse({"name": path.name, "bytes": path.stat().st_size})
