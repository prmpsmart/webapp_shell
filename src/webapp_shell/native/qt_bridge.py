"""The native bridge of the Qt shell: a QObject published to the page through QWebChannel.

The page does not load `qwebchannel.js` itself. The shell injects it, from Qt's own resources, together with a
small script that exposes the same `window.<slug>Native` promise API the frontend uses in every shell.
"""

import json
from pathlib import Path

from PySide6.QtCore import QFile, QIODevice, QObject, Slot
from PySide6.QtWidgets import QFileDialog, QWidget

from ..enums import NativeMethod
from ..identity import AppIdentity
from ..preferences import BootColors, ShellPreferences
from .filters import FileFilter
from .os_actions import OsActions
from .start_location import StartLocation
from .zoom import clamp

CHANNEL_OBJECT = "bridge"
_METHOD_NAMES = json.dumps([method.value for method in NativeMethod])

_GLUE_JS = """
new QWebChannel(qt.webChannelTransport, function (channel) {
  var b = channel.objects.%(object)s;
  var call = function (name, args) {
    return new Promise(function (resolve) { b[name].apply(b, args.concat([resolve])); });
  };
  // One entry per native method, built from the list the shell sends. Objects travel as JSON text (Qt slots
  // take plain types); an empty result means "nothing chosen" and the frontend turns it into null.
  var api = {};
  %(names)s.forEach(function (name) {
    api[name] = function () {
      var args = Array.prototype.slice.call(arguments).map(function (a) {
        return a !== null && typeof a === 'object' ? JSON.stringify(a) : a === undefined ? '' : a;
      });
      return call(name, args);
    };
  });
  window.%(global)s = api;
  window.dispatchEvent(new Event('%(ready)s'));
});
"""


class QtBridge(QObject):
    def __init__(self, parent: QWidget, actions: OsActions | None = None, preferences: ShellPreferences | None = None):
        super().__init__(parent)
        self._preferences = preferences or ShellPreferences(None)
        self._parent_widget = parent
        self._actions = actions or OsActions()

    @Slot(str, result=str)
    def pickFolder(self, start: str) -> str:
        return QFileDialog.getExistingDirectory(self._parent_widget, dir=StartLocation.of(start).qt_path()) or ""

    @Slot(str, str, result=str)
    def pickFile(self, filters_json: str, start: str) -> str:
        filters = ";;".join(f.to_qt() for f in FileFilter.parse_all(json.loads(filters_json or "[]")))
        location = StartLocation.of(start).qt_path()
        return QFileDialog.getOpenFileName(self._parent_widget, dir=location, filter=filters)[0] or ""

    @Slot(str, str, result=str)
    def saveAs(self, name: str, start: str) -> str:
        """Opens at the folder of the current choice (or the one it was in), proposing `name` unless a file is set."""
        location = StartLocation.of(start)
        proposed = location.filename or name
        where = str(Path(location.directory, proposed)) if location.directory else name
        return QFileDialog.getSaveFileName(self._parent_widget, dir=where)[0] or ""

    @Slot(str, result=bool)
    def reveal(self, path: str) -> bool:
        return self._actions.reveal(path)

    @Slot(str, result=bool)
    def openUrl(self, url: str) -> bool:
        return self._actions.open_url(url)

    @Slot(str, result=bool)
    def setBootColors(self, colors) -> bool:
        parsed = BootColors.from_payload(colors)
        return parsed is not None and self._preferences.save_boot_colors(parsed)

    @Slot(float, result=bool)
    def setZoom(self, factor: float) -> bool:
        zoom = clamp(factor)
        if zoom is None:
            return False
        self._parent_widget.setZoomFactor(zoom)
        return True

    @staticmethod
    def page_script_source(identity: AppIdentity) -> str:
        """qwebchannel.js (from Qt's resources) followed by the glue that defines the page's native object."""
        resource = QFile(":/qtwebchannel/qwebchannel.js")
        if not resource.open(QIODevice.OpenModeFlag.ReadOnly):
            raise RuntimeError("qwebchannel.js is not available in this Qt installation")
        return bytes(resource.readAll()).decode("utf-8") + _GLUE_JS % {
            "object": CHANNEL_OBJECT,
            "names": _METHOD_NAMES,
            "global": identity.native_global,
            "ready": identity.native_ready_event,
        }
