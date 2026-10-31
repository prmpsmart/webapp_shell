"""The shell's own native functions for this program: what only the shell can know or do."""

import platform
from dataclasses import dataclass

from webapp_shell import JsonValue, NativeContext, NativeFunction, NoArguments


@dataclass(frozen=True)
class Greeting:
    """The page's arguments, in order: `bridge.call('greet', who)` fills `who`."""

    who: str


def where_am_i(_context: NativeContext, _arguments: NoArguments) -> JsonValue:
    """The first argument is always the context (window, preferences, OS actions); then come the page's arguments."""
    return {"system": platform.system(), "release": platform.release(), "python": platform.python_version()}


def greet(_context: NativeContext, arguments: Greeting) -> JsonValue:
    return f"Hello, {arguments.who}. This text was made by the shell."


NATIVE_FUNCTIONS = (
    NativeFunction("whereAmI", NoArguments, where_am_i),
    NativeFunction("greet", Greeting, greet),
)
