"""Where the program lives and how its backend is started: from the source tree, or frozen into one folder."""

import os
import sys
from pathlib import Path

from .backend import BackendSpec


class Installation:
    """A frozen program (PyInstaller) has one executable and no `python -m`: it starts its own backend by running
    itself with `RUN_BACKEND`. From the source tree the backend is `python -m <module>`, as always."""

    RUN_BACKEND = "--run-backend"
    CHECK_LIBRARIES = "--check-libraries"  # imports every required library; a build runs it on the frozen program
    COMMANDS = (RUN_BACKEND, CHECK_LIBRARIES)  # what a frozen program does instead of opening a window

    def __init__(self, source_root: Path, frozen: bool | None = None, bundle: Path | None = None):
        self.frozen = bool(getattr(sys, "frozen", False)) if frozen is None else frozen
        self._bundle = bundle if bundle is not None else Path(getattr(sys, "_MEIPASS", source_root))
        self._source_root = source_root

    @property
    def root(self) -> Path:
        """The folder that holds the compiled frontend (and whatever else the program ships)."""
        return self._bundle if self.frozen else self._source_root

    def package_dirs(self, backend: BackendSpec) -> tuple[Path, ...]:
        """Import roots to add by hand. A frozen program carries its packages inside."""
        return () if self.frozen else backend.package_dirs

    def backend_command(self, backend: BackendSpec) -> list[str]:
        return [sys.executable, self.RUN_BACKEND] if self.frozen else [sys.executable, "-m", backend.module]


def ensure_standard_streams() -> None:
    """A windowed program has no console: `sys.stdout` and `sys.stderr` are None, and libraries that ask a stream
    whether it is a terminal (the backend's web server does) fail. They get a stream that discards its text."""
    for name in ("stdout", "stderr"):
        if getattr(sys, name) is None:
            setattr(sys, name, open(os.devnull, "w", encoding="utf-8"))  # noqa: SIM115 - kept open for the whole run
