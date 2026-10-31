"""The native bridge of the Qt shell: a QObject published to the page through QWebChannel.

The page does not load `qwebchannel.js` itself. The shell injects it, from Qt's own resources, together with a small
script that exposes the same promise API (`window.<slug>Native.<name>(...)`) the page sees in every shell. One slot,
`call`, carries every native function: the name and the arguments as JSON text in, the envelope as JSON text out.
"""

import json

from PySide6.QtCore import QFile, QIODevice, QObject, Slot

from ..identity import AppIdentity
from ..json_types import JsonValue
from .registry import NativeRegistry
from .window import NativeContext

CHANNEL_OBJECT = "bridge"

_GLUE_JS = """
new QWebChannel(qt.webChannelTransport, function (channel) {
  var b = channel.objects.%(object)s;
  var api = {};
  %(names)s.forEach(function (name) {
    api[name] = function () {
      var args = JSON.stringify(Array.prototype.slice.call(arguments));
      return new Promise(function (resolve) {
        b.call(name, args, function (answer) { resolve(JSON.parse(answer)); });
      });
    };
  });
  window.%(global)s = api;
  window.dispatchEvent(new Event('%(ready)s'));
});
"""


class QtBridge(QObject):
    def __init__(self, registry: NativeRegistry, context: NativeContext, parent: QObject | None = None):
        super().__init__(parent)
        self._registry = registry
        self._context = context

    @Slot(str, str, result=str)
    def call(self, name: str, arguments_json: str) -> str:
        try:
            arguments: JsonValue = json.loads(arguments_json or "[]")
        except ValueError:
            arguments = None
        return json.dumps(self._registry.call(self._context, name, arguments))

    @staticmethod
    def page_script_source(identity: AppIdentity, registry: NativeRegistry) -> str:
        """qwebchannel.js (from Qt's resources) followed by the glue that defines the page's native object."""
        resource = QFile(":/qtwebchannel/qwebchannel.js")
        if not resource.open(QIODevice.OpenModeFlag.ReadOnly):
            raise RuntimeError("qwebchannel.js is not available in this Qt installation")
        return bytes(resource.readAll().data()).decode("utf-8") + _GLUE_JS % {
            "object": CHANNEL_OBJECT,
            "names": json.dumps(registry.names),
            "global": identity.native_global,
            "ready": identity.native_ready_event,
        }
