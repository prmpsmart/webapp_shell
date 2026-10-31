"""The one object a project gives the library."""

from dataclasses import dataclass
from pathlib import Path

from .backend import BackendSpec
from .identity import AppIdentity


@dataclass(frozen=True)
class ShellConfig:
    identity: AppIdentity
    backend: BackendSpec
    source_root: Path  # running from the source: the folder that holds the compiled frontend (`frontend/dist`)
    host: str = "127.0.0.1"
    startup_timeout: float = 20.0  # seconds to wait for the backend to answer its health path
    # The splash stays at least this long, so the opening always reads as a deliberate, steady start.
    splash_seconds: float = 0.0
    required_libraries: tuple[str, ...] = ()  # imported by `--check-libraries` on a frozen program
