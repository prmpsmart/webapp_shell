"""The native bridge of the pywebview shell. pywebview turns every public callable of this object into
`window.pywebview.api.<name>()`; the registered native functions are attached by name, each answering in the envelope."""

from collections.abc import Callable

from ..json_types import JsonObject, JsonValue
from .registry import NativeRegistry
from .window import NativeContext


class WebviewBridge:
    def __init__(self, registry: NativeRegistry, context: NativeContext):
        # Private on purpose: pywebview walks every public attribute of the API object (and went into the .NET window
        # when the window was public, which failed on Windows with thread and recursion errors).
        self._registry = registry
        self._context = context
        for name in registry.names:
            setattr(self, name, self._function(name))

    def _function(self, name: str) -> Callable[..., JsonObject]:
        def call(*arguments: JsonValue) -> JsonObject:
            return self._registry.call(self._context, name, list(arguments))

        call.__name__ = name
        return call
