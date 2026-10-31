"""What a native function can use: the window it opens dialogs on, the shell's preferences and the OS actions. Each
toolkit implements `NativeWindow`; the functions are written once, against it."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..preferences import ShellPreferences
from .filters import FileFilter
from .os_actions import OsActions


class NativeWindow(ABC):
    """The window of one toolkit. A dialog returns the chosen path, or None when the person cancelled."""

    @abstractmethod
    def pick_folder(self, start: str) -> str | None: ...

    @abstractmethod
    def pick_file(self, filters: list[FileFilter], start: str) -> str | None: ...

    @abstractmethod
    def save_as(self, name: str, start: str) -> str | None: ...

    @abstractmethod
    def set_zoom(self, factor: float) -> bool: ...


@dataclass(frozen=True)
class NativeContext:
    """Handed to every native function as its first argument."""

    window: NativeWindow
    preferences: ShellPreferences
    actions: OsActions
