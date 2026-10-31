"""`NativeWindow` for the pywebview shell. The window is attached after pywebview creates it."""

import webview

from .filters import FileFilter
from .start_location import StartLocation
from .window import NativeWindow
from .zoom import WebviewZoom


class WebviewWindow(NativeWindow):
    def __init__(self, zoom: WebviewZoom | None = None):
        self._window: webview.Window | None = None
        self._zoom = zoom or WebviewZoom()

    def bind(self, window: webview.Window) -> None:
        self._window = window

    def pick_folder(self, start: str) -> str | None:
        location = StartLocation.of(start)
        return self._first(self._window.create_file_dialog(webview.FileDialog.FOLDER, directory=location.directory))

    def pick_file(self, filters: list[FileFilter], start: str) -> str | None:
        location = StartLocation.of(start)
        types = tuple(f.to_webview() for f in filters)
        return self._first(
            self._window.create_file_dialog(webview.FileDialog.OPEN, directory=location.directory, file_types=types)
        )

    def save_as(self, name: str, start: str) -> str | None:
        location = StartLocation.of(start)
        return self._first(
            self._window.create_file_dialog(
                webview.FileDialog.SAVE, directory=location.directory, save_filename=location.filename or name
            )
        )

    def set_zoom(self, factor: float) -> bool:
        return self._zoom.apply(self._window, factor)

    @staticmethod
    def _first(result) -> str | None:
        """pywebview returns a path, a list of paths, or nothing when cancelled."""
        if not result:
            return None
        return result if isinstance(result, str) else result[0]
