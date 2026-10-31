"""webapp_shell: a desktop window for a web app made of a Python backend and a compiled frontend.

A project describes itself with a `ShellConfig` and calls `run(config)`; the library starts the backend, waits until it
is healthy, opens the frontend in a window (pywebview by default, Qt on request) and gives the page a small set of
native functions.
"""

from .backend import BackendSpec, CliFlag
from .cli import run
from .config import ShellConfig
from .enums import NativeMethod, ShellKind
from .identity import AppIdentity
from .native.registry import NativeError, NativeFunction
from .native.window import NativeContext, NativeWindow
from .preferences import BootColors
from .protocol import WireProtocol

__all__ = [
    "AppIdentity",
    "BackendSpec",
    "BootColors",
    "CliFlag",
    "NativeContext",
    "NativeError",
    "NativeFunction",
    "NativeMethod",
    "NativeWindow",
    "ShellConfig",
    "ShellKind",
    "WireProtocol",
    "run",
]
