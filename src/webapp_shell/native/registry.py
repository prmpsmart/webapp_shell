"""The native functions a page may call: a name, typed arguments, a handler, and one place that runs them for both
toolkits.

The page is untrusted, so a call is checked here: the name must be registered, the arguments must fit the declared
types, an error never leaks more than a plain message, and every result travels in the same envelope:
`{"ok": true, "value": ...}` or `{"ok": false, "error": "..."}`.
"""

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from ..json_types import JsonObject, JsonValue
from .arguments import Arguments
from .errors import NativeError
from .window import NativeContext

__all__ = ["NativeCallable", "NativeError", "NativeFunction", "NativeRegistry", "NoArguments"]

_NAME = re.compile(r"[a-z][A-Za-z0-9]*")
_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class NoArguments:
    """The arguments of a function that takes none."""


class NativeCallable(Protocol):
    """What the registry stores: any `NativeFunction`, whatever its arguments are."""

    @property
    def name(self) -> str: ...

    def run(self, context: NativeContext, values: list[JsonValue]) -> JsonValue: ...


class NativeFunction[A]:
    """A function the page can call by `name`. `arguments` is a dataclass (see `native.arguments`); the handler is
    called as `handler(context, arguments)` and returns anything JSON can carry."""

    def __init__(self, name: str, arguments: type[A], handler: Callable[[NativeContext, A], JsonValue]):
        if not _NAME.fullmatch(name):
            raise ValueError(f"a native function name is camelCase letters and digits: {name!r}")
        self._name = name
        self._arguments = Arguments(arguments)
        self._handler = handler

    @property
    def name(self) -> str:  # camelCase, starts with a lowercase letter: it is the name on the wire and in the page
        return self._name

    def run(self, context: NativeContext, values: list[JsonValue]) -> JsonValue:
        return self._handler(context, self._arguments.parse(values))


class NativeRegistry:
    def __init__(self, functions: tuple[NativeCallable, ...] = ()):
        self._functions: dict[str, NativeCallable] = {}
        for function in functions:
            self.add(function)

    def add(self, function: NativeCallable) -> None:
        if function.name in self._functions:
            raise ValueError(f"a native function named {function.name!r} is already registered")
        self._functions[function.name] = function

    @property
    def names(self) -> list[str]:
        return list(self._functions)

    def call(self, context: NativeContext, name: str, arguments: JsonValue) -> JsonObject:
        """Runs one call from the page and returns the envelope."""
        function = self._functions.get(name)
        if function is None:
            return self._failed("unknown native function")
        if not isinstance(arguments, list):
            return self._failed("the arguments must be a list")
        try:
            return {"ok": True, "value": function.run(context, arguments)}
        except NativeError as error:
            return self._failed(str(error))
        except Exception:
            _log.exception("native function %s failed", name)
            return self._failed("the native function failed")

    @staticmethod
    def _failed(message: str) -> JsonObject:
        return {"ok": False, "error": message}
