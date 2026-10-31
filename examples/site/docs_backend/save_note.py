from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse


async def save_note(request: Request) -> JSONResponse:
    """The shell gave the page a path to save to; the page sends it here with the text. The backend writes the file."""
    body = await request.json()
    path = Path(str(body.get("path", "")))
    if not path.parent.is_dir():
        return JSONResponse({"error": "the folder does not exist"}, status_code=400)
    path.write_text(str(body.get("text", "")), encoding="utf-8")
    return JSONResponse({"bytes": path.stat().st_size})
