"""What each shell brings and what it must leave out, so a build carries one window toolkit and not the other."""

from dataclasses import dataclass

from ..enums import ShellKind


@dataclass(frozen=True)
class ShellProfile:
    """One shell, with the libraries of the other kept out of its build."""

    kind: ShellKind
    modules: tuple[str, ...]  # webapp_shell modules that belong to this shell only
    forbidden: tuple[str, ...]  # top-level names that must not be in the finished build

    @property
    def other_modules(self) -> tuple[str, ...]:
        return tuple(m for p in PROFILES.values() if p.kind is not self.kind for m in p.modules)

    @property
    def excludes(self) -> list[str]:
        """Libraries the freezer must leave out even if something imports them."""
        return [*COMMON_EXCLUDES, *self.forbidden, *self.other_modules]

    def wanted_module(self, name: str) -> bool:
        return not any(name == m or name.startswith(f"{m}.") for m in self.other_modules)


PROFILES: dict[ShellKind, ShellProfile] = {
    ShellKind.QT: ShellProfile(
        ShellKind.QT,
        modules=("webapp_shell.qt_shell", "webapp_shell.native.qt_bridge", "webapp_shell.native.qt_window"),
        forbidden=("webview", "pythonnet", "clr_loader", "proxy_tools", "bottle"),
    ),
    ShellKind.WEBVIEW: ShellProfile(
        ShellKind.WEBVIEW,
        modules=(
            "webapp_shell.webview_shell",
            "webapp_shell.native.webview_bridge",
            "webapp_shell.native.webview_background",
            "webapp_shell.native.webview_window",
            "webapp_shell.native.zoom",
        ),
        forbidden=("PySide6", "shiboken6", "PyQt5", "PyQt6", "qtpy"),
    ),
}

# Tools of the developer, never of the user.
COMMON_EXCLUDES = ["tkinter", "pytest", "ruff", "pip", "IPython", "notebook"]  # not setuptools: pkg_resources needs it
