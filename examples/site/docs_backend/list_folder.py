from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse


async def list_folder(request: Request) -> JSONResponse:
    """The shell gave the page a folder; the page sent it here. The backend looks inside and answers with data."""
    folder = Path(str(request.query_params.get("path", "")))
    if not folder.is_dir():
        return JSONResponse({"error": "not a folder"}, status_code=404)
    names = sorted(entry.name for entry in folder.iterdir() if not entry.name.startswith("."))
    return JSONResponse({"count": len(names), "first": names[:5]})
