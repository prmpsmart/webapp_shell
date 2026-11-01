from starlette.requests import Request
from starlette.responses import JSONResponse

from webapp_shell import ShellMessages


async def messages(_request: Request) -> JSONResponse:
    """The sentences the shell shows when something is wrong, as the library holds them (see TRANSLATING.md)."""
    return JSONResponse(ShellMessages().catalogue())
