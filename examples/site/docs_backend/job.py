import asyncio
from dataclasses import dataclass, field

from starlette.requests import Request
from starlette.responses import JSONResponse

STEPS = 10


@dataclass
class Job:
    done: int = 0
    running: bool = False
    task: asyncio.Task[None] | None = field(default=None, repr=False)  # kept, or the loop may drop a task nobody awaits


job = Job()


async def _work() -> None:
    for _ in range(STEPS):
        await asyncio.sleep(0.3)
        job.done += 1
    job.running = False


async def start_job(_request: Request) -> JSONResponse:
    """A long task runs in the backend; the page asks how far it is. The shell is not involved."""
    if job.running:
        return JSONResponse({"error": "a job is already running"}, status_code=409)
    job.done, job.running = 0, True
    job.task = asyncio.create_task(_work())
    return JSONResponse({"steps": STEPS})


async def job_status(_request: Request) -> JSONResponse:
    return JSONResponse({"running": job.running, "done": job.done, "steps": STEPS})
