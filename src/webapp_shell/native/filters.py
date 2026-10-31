"""File-type filters in the one shape the frontend sends, converted for each toolkit."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FileFilter:
    """`{name: 'Excel', extensions: ['xlsx', 'xls']}` from the page. An extension may be written `xlsx` or `*.xlsx`."""

    name: str
    extensions: tuple[str, ...]

    @property
    def is_usable(self) -> bool:
        return bool(self.name) and bool(self.extensions)

    def _patterns(self) -> list[str]:
        return ["*." + extension.lstrip("*.") for extension in self.extensions]

    def to_qt(self) -> str:
        return f"{self.name} ({' '.join(self._patterns())})"

    def to_webview(self) -> str:
        return f"{self.name} ({';'.join(self._patterns())})"
