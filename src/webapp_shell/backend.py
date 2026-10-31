"""How a project's backend is started: a Python module run as `python -m <module>` (or, in a frozen program, by the
program running itself)."""

from dataclasses import dataclass
from pathlib import Path

from .protocol import WireProtocol


@dataclass(frozen=True)
class CliFlag:
    """A command-line switch the project adds to its program (`--sandbox`). When given, the backend gets `passes`."""

    name: str
    help: str
    passes: tuple[str, ...]  # what the backend is started with when the switch is on


@dataclass(frozen=True)
class BackendSpec:
    module: str  # the backend's package: started as `python -m <module>`; its `__main__.main(argv)` runs when frozen
    wire: WireProtocol
    frontend_dist: Path = Path("frontend/dist")  # the compiled frontend, relative to the program's root
    frontend_argument: str = "--frontend"  # how the backend is told where the compiled frontend is
    port_argument: str = "--port"
    preferences_argument: str | None = "--preferences-file"  # None when the backend keeps no preferences file
    arguments: tuple[str, ...] = ()  # always passed
    source_only_arguments: tuple[str, ...] = ()  # passed only when running from the source, not when frozen
    flags: tuple[CliFlag, ...] = ()  # the project's own command-line switches
    package_dirs: tuple[Path, ...] = ()  # import roots to add by hand when running from the source
