"""`NativeWindow` for the Qt shell: the dialogs of `QFileDialog` and the page zoom of the web view."""

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QWidget

from .filters import FileFilter
from .start_location import StartLocation
from .window import NativeWindow


class QtWindow(NativeWindow):
    def __init__(self, view: QWidget):
        self._view = view

    def pick_folder(self, start: str) -> str | None:
        return QFileDialog.getExistingDirectory(self._view, dir=StartLocation.of(start).qt_path()) or None

    def pick_file(self, filters: list[FileFilter], start: str) -> str | None:
        patterns = ";;".join(f.to_qt() for f in filters)
        location = StartLocation.of(start).qt_path()
        return QFileDialog.getOpenFileName(self._view, dir=location, filter=patterns)[0] or None

    def save_as(self, name: str, start: str) -> str | None:
        """Opens at the folder of the current choice (or the one it was in), proposing `name` unless a file is set."""
        location = StartLocation.of(start)
        proposed = location.filename or name
        where = str(Path(location.directory, proposed)) if location.directory else name
        return QFileDialog.getSaveFileName(self._view, dir=where)[0] or None

    def set_zoom(self, factor: float) -> bool:
        self._view.setZoomFactor(factor)
        return True
