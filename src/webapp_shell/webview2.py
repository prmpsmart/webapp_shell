"""On Windows the pywebview window is drawn by the Microsoft WebView2 runtime (on Windows 11 and on most up-to-date
Windows 10). Without it the window cannot open, and the person would see nothing at all; this finds it first, so the
program can say what is missing in plain words."""

import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from .messages import MessageKey, ShellMessages

DOWNLOAD_URL = "https://developer.microsoft.com/microsoft-edge/webview2/"
RUNTIME_CLIENT = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"  # how the Edge updater lists the WebView2 runtime
NOT_INSTALLED = "0.0.0.0"


class RegistryHive(StrEnum):
    MACHINE = "HKEY_LOCAL_MACHINE"
    USER = "HKEY_CURRENT_USER"


@dataclass(frozen=True)
class RegistryLocation:
    hive: RegistryHive
    subkey: str  # holds the value `pv`: the runtime's version


RUNTIME_LOCATIONS = (
    RegistryLocation(RegistryHive.MACHINE, rf"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{RUNTIME_CLIENT}"),
    RegistryLocation(RegistryHive.MACHINE, rf"SOFTWARE\Microsoft\EdgeUpdate\Clients\{RUNTIME_CLIENT}"),
    RegistryLocation(RegistryHive.USER, rf"Software\Microsoft\EdgeUpdate\Clients\{RUNTIME_CLIENT}"),
)


def read_registry_version(location: RegistryLocation) -> str | None:
    """The runtime's version at `location`, or None when the key or the value is not there."""
    if sys.platform != "win32":
        return None
    import winreg

    hive = winreg.HKEY_LOCAL_MACHINE if location.hive is RegistryHive.MACHINE else winreg.HKEY_CURRENT_USER
    try:
        with winreg.OpenKey(hive, location.subkey) as key:
            value, _kind = winreg.QueryValueEx(key, "pv")
    except OSError:
        return None
    return value if isinstance(value, str) else None


class Webview2Check:
    def __init__(
        self,
        platform: str = sys.platform,
        read_version: Callable[[RegistryLocation], str | None] = read_registry_version,
    ):
        self._platform = platform
        self._read_version = read_version

    def is_missing(self) -> bool:
        """True only on Windows, when no WebView2 runtime is listed."""
        if self._platform != "win32":
            return False
        versions = (self._read_version(location) for location in RUNTIME_LOCATIONS)
        return not any(version and version != NOT_INSTALLED for version in versions)

    def problem(self, name: str, messages: ShellMessages) -> str | None:
        """The sentence to show when the runtime is missing, else None."""
        if not self.is_missing():
            return None
        return messages.text(MessageKey.WEBVIEW2_MISSING, name=name, url=DOWNLOAD_URL)


def show_message_box(title: str, text: str) -> None:
    """A windowed program has no console, so a problem before any window exists is shown in the system's own box."""
    if sys.platform == "win32":
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, text, title, 0x10)  # 0x10: the error icon
    else:
        print(text, file=sys.stderr)
