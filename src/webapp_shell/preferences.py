"""What the shell itself remembers between launches: the colours of the app's opening screen, so the window and
the splash start in the colours of the theme the user chose (the shell cannot read the web page's storage before
the page loads)."""

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .json_types import JsonObject, JsonValue

_HEX_COLOUR = re.compile(r"#[0-9a-fA-F]{6}")


def is_colour(value: object) -> bool:
    """Only `#rrggbb` is accepted: these values are later written into HTML and CSS."""
    return isinstance(value, str) and _HEX_COLOUR.fullmatch(value) is not None


@dataclass(frozen=True)
class BootColors:
    """The three colours of the navy gradient (frontend tokens `--nav`, `--hero-a`, `--hero-b`)."""

    base: str
    glow_a: str
    glow_b: str

    @classmethod
    def from_values(cls, base: JsonValue, glow_a: JsonValue, glow_b: JsonValue) -> "BootColors | None":
        """From three stored values. None when one is not text or the three are not `#rrggbb` colours."""
        if not (isinstance(base, str) and isinstance(glow_a, str) and isinstance(glow_b, str)):
            return None
        colors = cls(base, glow_a, glow_b)
        return colors if colors.is_valid else None

    @property
    def is_valid(self) -> bool:
        return all(is_colour(c) for c in (self.base, self.glow_a, self.glow_b))

    def normalised(self) -> "BootColors":
        return BootColors(self.base.lower(), self.glow_a.lower(), self.glow_b.lower())


class ShellPreferences:
    """A tiny JSON file. With `path=None` it lives in memory only (headless checks must not touch the user's file)."""

    BOOT_KEY = "bootColors"

    def __init__(self, path: Path | None):
        self._path = path
        self._values: JsonObject = self._read()

    @property
    def boot_colors(self) -> BootColors | None:
        stored = self._values.get(self.BOOT_KEY)
        if not isinstance(stored, dict):
            return None
        return BootColors.from_values(stored.get("base"), stored.get("glow_a"), stored.get("glow_b"))

    def save_boot_colors(self, colors: BootColors) -> bool:
        if not colors.is_valid:
            return False
        self._values[self.BOOT_KEY] = asdict(colors.normalised())
        self._write()
        return True

    # storage -----------------------------------------------------------------------------------
    def _read(self) -> JsonObject:
        if self._path is None or not self._path.is_file():
            return {}
        try:
            data: JsonValue = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    def _write(self) -> None:
        if self._path is None:
            return
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(self._values, indent=2), encoding="utf-8")
        except OSError:  # colours are not worth failing for
            pass
