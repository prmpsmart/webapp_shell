"""File-type filters in the one shape the frontend sends, converted for each toolkit."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FileFilter:
    name: str
    extensions: tuple[str, ...]

    @classmethod
    def parse_all(cls, raw: list[dict] | None) -> list["FileFilter"]:
        """`raw` comes from the page: [{name: 'Excel', extensions: ['xlsx', 'xls']}, ...]."""
        return [
            cls(str(item["name"]), tuple(str(e).lstrip("*.") for e in item.get("extensions", [])))
            for item in (raw or [])
            if item.get("name") and item.get("extensions")
        ]

    def to_qt(self) -> str:
        return f"{self.name} ({' '.join('*.' + e for e in self.extensions)})"

    def to_webview(self) -> str:
        return f"{self.name} ({';'.join('*.' + e for e in self.extensions)})"
