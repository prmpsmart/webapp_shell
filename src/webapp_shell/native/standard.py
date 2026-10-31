"""The native functions every project gets. Written once, against `NativeContext`; the page sees them under the names
of `NativeMethod`."""

from ..enums import NativeMethod
from ..preferences import BootColors
from .filters import FileFilter
from .registry import NativeFunction
from .window import NativeContext
from .zoom import clamp


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def pick_folder(context: NativeContext, start: object = "") -> str | None:
    return context.window.pick_folder(_text(start))


def pick_file(context: NativeContext, filters: object = None, start: object = "") -> str | None:
    parsed = FileFilter.parse_all(filters if isinstance(filters, list) else None)
    return context.window.pick_file(parsed, _text(start))


def save_as(context: NativeContext, name: object = "", start: object = "") -> str | None:
    return context.window.save_as(_text(name), _text(start))


def reveal(context: NativeContext, path: object) -> bool:
    return context.actions.reveal(_text(path))


def open_url(context: NativeContext, url: object) -> bool:
    return context.actions.open_url(_text(url))


def set_boot_colors(context: NativeContext, colors: object) -> bool:
    parsed = BootColors.from_payload(colors)
    return parsed is not None and context.preferences.save_boot_colors(parsed)


def set_zoom(context: NativeContext, factor: object) -> bool:
    zoom = clamp(factor)
    return zoom is not None and context.window.set_zoom(zoom)


STANDARD = {
    NativeMethod.PICK_FOLDER: pick_folder,
    NativeMethod.PICK_FILE: pick_file,
    NativeMethod.SAVE_AS: save_as,
    NativeMethod.REVEAL: reveal,
    NativeMethod.OPEN_URL: open_url,
    NativeMethod.SET_BOOT_COLORS: set_boot_colors,
    NativeMethod.SET_ZOOM: set_zoom,
}


def standard_functions() -> tuple[NativeFunction, ...]:
    return tuple(NativeFunction(method.value, handler) for method, handler in STANDARD.items())
