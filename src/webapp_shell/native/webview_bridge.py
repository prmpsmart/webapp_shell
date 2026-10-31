"""The native bridge of the pywebview shell. Public methods become `window.pywebview.api.<name>()`."""

import webview

from ..preferences import BootColors, ShellPreferences
from .filters import FileFilter
from .os_actions import OsActions
from .start_location import StartLocation
from .zoom import WebviewZoom, clamp


class WebviewBridge:
    def __init__(self, actions: OsActions | None = None, preferences: ShellPreferences | None = None):
        self._window: webview.Window | None = None  # private: pywebview walks every public attribute of the API
        self._actions = actions or OsActions()
        self._preferences = preferences or ShellPreferences(None)
        self._zoom = WebviewZoom()

    def bind(self, window: webview.Window) -> None:
        """Gives the bridge the window it opens dialogs on. Not part of the page's API."""
        self._window = window

    bind._serializable = False  # pywebview leaves out what carries this mark

    def pickFolder(self, start: str = "") -> str | None:
        location = StartLocation.of(start)
        return self._first(self._window.create_file_dialog(webview.FileDialog.FOLDER, directory=location.directory))

    def pickFile(self, filters: list[dict] | None = None, start: str = "") -> str | None:
        types = tuple(f.to_webview() for f in FileFilter.parse_all(filters))
        location = StartLocation.of(start)
        return self._first(
            self._window.create_file_dialog(webview.FileDialog.OPEN, directory=location.directory, file_types=types)
        )

    def saveAs(self, name: str = "", start: str = "") -> str | None:
        location = StartLocation.of(start)
        return self._first(
            self._window.create_file_dialog(
                webview.FileDialog.SAVE, directory=location.directory, save_filename=location.filename or name
            )
        )

    def reveal(self, path: str) -> bool:
        return self._actions.reveal(path)

    def openUrl(self, url: str) -> bool:
        return self._actions.open_url(url)

    def setBootColors(self, colors) -> bool:
        parsed = BootColors.from_payload(colors)
        return parsed is not None and self._preferences.save_boot_colors(parsed)

    def setZoom(self, factor) -> bool:
        zoom = clamp(factor)
        return zoom is not None and self._zoom.apply(self._window, zoom)

    @staticmethod
    def _first(result) -> str | None:
        """pywebview returns a path, a list of paths, or nothing when cancelled."""
        if not result:
            return None
        return result if isinstance(result, str) else result[0]
