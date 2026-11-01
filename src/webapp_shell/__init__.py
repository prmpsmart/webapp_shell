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
from .json_types import JsonObject, JsonValue
from .library_check import LibraryProblem
from .messages import MessageKey, ShellMessages
from .native.errors import NativeError
from .native.registry import NativeCallable, NativeFunction, NoArguments
from .native.window import NativeContext, NativeWindow
from .preferences import BootColors
from .protocol import WireProtocol

__all__ = [
    "AppIdentity",
    "BackendSpec",
    "BootColors",
    "CliFlag",
    "JsonObject",
    "JsonValue",
    "LibraryProblem",
    "MessageKey",
    "NativeCallable",
    "NativeContext",
    "NativeError",
    "NativeFunction",
    "NativeMethod",
    "NativeWindow",
    "NoArguments",
    "ShellConfig",
    "ShellKind",
    "ShellMessages",
    "WireProtocol",
    "run",
]
