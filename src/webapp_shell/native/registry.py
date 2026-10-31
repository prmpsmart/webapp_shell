"""The native functions a page may call: a name, a handler, and one place that runs them for both toolkits.

The page is untrusted, so a call is checked here: the name must be registered, an error never leaks more than a plain
message, and every result travels in the same envelope: `{"ok": true, "value": ...}` or `{"ok": false, "error": "..."}`.
"""

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .window import NativeContext

_NAME = re.compile(r"[a-z][A-Za-z0-9]*")
_log = logging.getLogger(__name__)

Handler = Callable[..., Any]  # called as handler(context, *arguments); returns anything JSON can carry


class NativeError(Exception):
    """Raised by a handler to refuse a call in words the page may show."""


@dataclass(frozen=True)
class NativeFunction:
    name: str  # camelCase, starts with a lowercase letter: it is the name on the wire and in the page
    handler: Handler

    def __post_init__(self) -> None:
        if not _NAME.fullmatch(self.name):
            raise ValueError(f"a native function name is camelCase letters and digits: {self.name!r}")


class NativeRegistry:
    def __init__(self, functions: tuple[NativeFunction, ...] = ()):
        self._functions: dict[str, NativeFunction] = {}
        for function in functions:
            self.add(function)

    def add(self, function: NativeFunction) -> None:
        if function.name in self._functions:
            raise ValueError(f"a native function named {function.name!r} is already registered")
        self._functions[function.name] = function

    @property
    def names(self) -> list[str]:
        return list(self._functions)

    def call(self, context: NativeContext, name: str, arguments: object) -> dict:
        """Runs one call from the page and returns the envelope."""
        function = self._functions.get(name) if isinstance(name, str) else None
        if function is None:
            return self._failed("unknown native function")
        if not isinstance(arguments, list):
            return self._failed("the arguments must be a list")
        try:
            return {"ok": True, "value": function.handler(context, *arguments)}
        except NativeError as error:
            return self._failed(str(error))
        except TypeError:
            return self._failed("the arguments do not fit this function")
        except Exception:
            _log.exception("native function %s failed", name)
            return self._failed("the native function failed")

    @staticmethod
    def _failed(message: str) -> dict:
        return {"ok": False, "error": message}
