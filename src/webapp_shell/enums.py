from enum import StrEnum


class ShellKind(StrEnum):
    """The desktop shells. The value is what the command line and the run scripts use."""

    QT = "qt"
    WEBVIEW = "webview"


class NativeMethod(StrEnum):
    """The native functions a page may call (02-architecture.md). The value is the name on the wire, in both shells."""

    PICK_FOLDER = "pickFolder"
    PICK_FILE = "pickFile"
    SAVE_AS = "saveAs"
    REVEAL = "reveal"
    OPEN_URL = "openUrl"
    SET_BOOT_COLORS = "setBootColors"
    SET_ZOOM = "setZoom"
