"""Who the program is: the one place a project says its name, where it keeps things and how its opening looks."""

import re
from dataclasses import dataclass, field
from pathlib import Path

from .preferences import BootColors

_SLUG = re.compile(r"[a-z][a-z0-9]*")


@dataclass(frozen=True)
class AppIdentity:
    """What the shell shows and stores for one program. Nothing else in the library names the program."""

    name: str  # shown in the window title, the splash and the messages: "Acme Notes"
    slug: str  # lowercase letters and digits: names the page's native object, the Qt script, the default wire names
    storage_dir: Path  # the program's own folder for what the shell remembers: "~/.acme"
    boot_colors: BootColors  # the opening screen's colours until the page reports the user's own
    icon_png: Path | None = None  # window icon (macOS, Linux) and the splash mark
    icon_ico: Path | None = None  # window icon on Windows, which draws only `.ico` files
    window_size: tuple[int, int] = field(default=(1280, 800))

    def __post_init__(self) -> None:
        if not _SLUG.fullmatch(self.slug):
            raise ValueError(f"slug must be lowercase letters and digits, starting with a letter: {self.slug!r}")
        if not self.name.strip():
            raise ValueError("name must not be empty")

    @property
    def native_global(self) -> str:
        """The name of the object the Qt shell puts on the page: `window.<slug>Native`."""
        return f"{self.slug}Native"

    @property
    def native_ready_event(self) -> str:
        """The event the page waits for before using `native_global`."""
        return f"{self.slug}nativeready"

    @property
    def shell_preferences_path(self) -> Path:
        """What the shell itself needs before the app exists (the opening colours)."""
        return self.storage_dir / "shell.json"

    @property
    def app_preferences_path(self) -> Path:
        """The program's own preferences, one file for every shell, owned by the backend."""
        return self.storage_dir / "preferences.json"
