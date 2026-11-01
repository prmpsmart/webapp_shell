"""The native functions every project gets. Written once, against `NativeContext`; the page sees them under the names
of `NativeMethod`. Each declares its arguments as a dataclass."""

from dataclasses import dataclass, field

from ..enums import NativeMethod
from ..preferences import BootColors
from .filters import FileFilter
from .registry import NativeCallable, NativeFunction
from .window import NativeContext
from .zoom_range import clamp


@dataclass(frozen=True)
class PickFolderArguments:
    start: str = ""


@dataclass(frozen=True)
class PickFileArguments:
    filters: list[FileFilter] = field(default_factory=list[FileFilter])
    start: str = ""


@dataclass(frozen=True)
class SaveAsArguments:
    name: str = ""
    start: str = ""


@dataclass(frozen=True)
class RevealArguments:
    path: str


@dataclass(frozen=True)
class OpenUrlArguments:
    url: str


@dataclass(frozen=True)
class BootColorsArguments:
    colors: BootColors


@dataclass(frozen=True)
class ZoomArguments:
    factor: float


def pick_folder(context: NativeContext, arguments: PickFolderArguments) -> str | None:
    return context.window.pick_folder(arguments.start)


def pick_file(context: NativeContext, arguments: PickFileArguments) -> str | None:
    usable = [item for item in arguments.filters if item.is_usable]
    return context.window.pick_file(usable, arguments.start)


def save_as(context: NativeContext, arguments: SaveAsArguments) -> str | None:
    return context.window.save_as(arguments.name, arguments.start)


def reveal(context: NativeContext, arguments: RevealArguments) -> bool:
    return context.actions.reveal(arguments.path)


def open_url(context: NativeContext, arguments: OpenUrlArguments) -> bool:
    return context.actions.open_url(arguments.url)


def set_boot_colors(context: NativeContext, arguments: BootColorsArguments) -> bool:
    return context.preferences.save_boot_colors(arguments.colors)


def set_zoom(context: NativeContext, arguments: ZoomArguments) -> bool:
    return context.window.set_zoom(clamp(arguments.factor))


def standard_functions() -> tuple[NativeCallable, ...]:
    return (
        NativeFunction(NativeMethod.PICK_FOLDER.value, PickFolderArguments, pick_folder),
        NativeFunction(NativeMethod.PICK_FILE.value, PickFileArguments, pick_file),
        NativeFunction(NativeMethod.SAVE_AS.value, SaveAsArguments, save_as),
        NativeFunction(NativeMethod.REVEAL.value, RevealArguments, reveal),
        NativeFunction(NativeMethod.OPEN_URL.value, OpenUrlArguments, open_url),
        NativeFunction(NativeMethod.SET_BOOT_COLORS.value, BootColorsArguments, set_boot_colors),
        NativeFunction(NativeMethod.SET_ZOOM.value, ZoomArguments, set_zoom),
    )
