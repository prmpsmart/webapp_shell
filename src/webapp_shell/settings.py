"""Where things are and how the shell behaves, in one place: the project's config on this installation."""

import sys
from dataclasses import dataclass, replace
from pathlib import Path

from .config import ShellConfig
from .installation import Installation
from .preferences import BootColors, ShellPreferences


@dataclass(frozen=True)
class Settings:
    config: ShellConfig
    installation: Installation
    boot_colors: BootColors  # the opening colours: the identity's, or the ones the user's theme left behind

    @classmethod
    def of(
        cls,
        config: ShellConfig,
        preferences: ShellPreferences | None = None,
        installation: Installation | None = None,
        splash_seconds: float | None = None,
    ) -> "Settings":
        """The config on this installation, with the opening colours the user's theme left behind last time."""
        installation = installation or Installation(config.source_root)
        remembered = preferences.boot_colors if preferences else None
        if splash_seconds is not None:
            config = replace(config, splash_seconds=splash_seconds)
        return cls(config, installation, remembered or config.identity.boot_colors)

    @property
    def identity(self):
        return self.config.identity

    @property
    def host(self) -> str:
        return self.config.host

    @property
    def startup_timeout(self) -> float:
        return self.config.startup_timeout

    @property
    def splash_seconds(self) -> float:
        return self.config.splash_seconds

    @property
    def window_size(self) -> tuple[int, int]:
        return self.identity.window_size

    @property
    def background_color(self) -> str:
        """The solid colour behind everything (the gradient's base), used for the window and the web view."""
        return self.boot_colors.base

    @property
    def package_dirs(self) -> tuple[Path, ...]:
        return self.installation.package_dirs(self.config.backend)

    @property
    def frontend_dist(self) -> Path:
        return self.installation.root / self.config.backend.frontend_dist

    @property
    def icon_png(self) -> Path | None:
        return self._existing(self.identity.icon_png)

    @property
    def window_icon(self) -> Path | None:
        """The icon for the window frame. Windows draws it with `System.Drawing.Icon`, which reads only `.ico` files;
        the other systems take the PNG."""
        return self._existing(self.identity.icon_ico if sys.platform == "win32" else self.identity.icon_png)

    @staticmethod
    def _existing(path: Path | None) -> Path | None:
        return path if path is not None and path.is_file() else None
