"""The shell's own native functions for this program: what only the shell can know or do."""

import platform

from webapp_shell import NativeFunction


def where_am_i(_context) -> dict:
    """The first argument is always the context (window, preferences, OS actions); the page's arguments follow."""
    return {"system": platform.system(), "release": platform.release(), "python": platform.python_version()}


def greet(_context, who: str) -> str:
    return f"Hello, {who}. This text was made by the shell."


NATIVE_FUNCTIONS = (NativeFunction("whereAmI", where_am_i), NativeFunction("greet", greet))
