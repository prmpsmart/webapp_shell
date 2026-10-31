"""Available shells, imported lazily so choosing one never requires the other's dependencies."""

import importlib

from .enums import ShellKind
from .shell import Shell

_SHELLS = {
    ShellKind.QT: ("webapp_shell.qt_shell", "QtShell"),
    ShellKind.WEBVIEW: ("webapp_shell.webview_shell", "WebviewShell"),
}


def kinds() -> list[ShellKind]:
    return list(_SHELLS)


def shell_class(kind: ShellKind) -> type[Shell]:
    module, cls = _SHELLS[kind]
    return getattr(importlib.import_module(module), cls)
