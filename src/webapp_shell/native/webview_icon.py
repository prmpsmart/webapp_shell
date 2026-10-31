"""The application icon in the Dock. pywebview applies its `icon` option on Qt and GTK only, so on macOS the Dock
shows a generic icon until it is set here. A packaged program has its icon from the bundle; this serves a run
from the source tree. Always safe: a platform it does not know is left alone."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownLambdaType=false
# pyright: reportUnknownArgumentType=false, reportMissingTypeStubs=false, reportMissingImports=false
# pyright: reportAttributeAccessIssue=false
# The lines below talk to AppKit (PyObjC), .NET and GTK, which publish no type stubs. Their inside is untyped by
# necessity; the signatures of this module are typed.

import sys
from pathlib import Path


class WebviewIcon:
    def __init__(self, path: Path | None):
        self.path = path

    def apply(self) -> bool:
        if sys.platform != "darwin" or self.path is None:
            return False
        try:
            import AppKit
            from PyObjCTools import AppHelper

            image = AppKit.NSImage.alloc().initWithContentsOfFile_(str(self.path))
            if image is None:
                return False
            AppHelper.callAfter(lambda: AppKit.NSApplication.sharedApplication().setApplicationIconImage_(image))
            return True
        except Exception:  # cosmetic only: never stop the app for an icon
            return False
