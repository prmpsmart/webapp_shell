"""Where a native dialog opens: the path the field already holds, or the nearest folder that still exists."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StartLocation:
    directory: str = ""
    filename: str = ""

    @classmethod
    def of(cls, path: str | None) -> "StartLocation":
        """A folder opens itself; a file opens its folder with the name preselected; a missing path falls back
        to the closest parent that exists; anything else leaves the choice to the toolkit."""
        if not path:
            return cls()
        target = Path(path).expanduser()
        if target.is_dir():
            return cls(str(target))
        for parent in target.parents:
            if parent.is_dir():
                return cls(str(parent), target.name if parent == target.parent and target.suffix else "")
        return cls()

    def qt_path(self) -> str:
        """Qt takes one `dir` argument: a folder, or a folder plus the name to preselect."""
        return str(Path(self.directory, self.filename)) if self.directory else ""
