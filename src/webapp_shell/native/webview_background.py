"""Makes the web view itself paint the app's background before a page loads, so no white shows between the
splash and the frontend. Platform specific, and always safe: a platform it does not know is left alone."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownLambdaType=false
# pyright: reportUnknownArgumentType=false, reportMissingTypeStubs=false, reportMissingImports=false
# pyright: reportAttributeAccessIssue=false
# The lines below talk to AppKit (PyObjC), .NET and GTK, which publish no type stubs. Their inside is untyped by
# necessity; the signatures of this module are typed.

import sys

import webview


class WebviewBackground:
    def __init__(self, color: str):
        self.color = color

    def apply(self, window: webview.Window) -> None:
        if sys.platform == "darwin":
            self._apply_macos(window)

    def _apply_macos(self, window: webview.Window) -> None:
        """WKWebView paints white under a page until told otherwise (`underPageBackgroundColor`, macOS 12+)."""
        try:
            import AppKit
            from PyObjCTools import AppHelper

            red, green, blue = (int(self.color.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4))
            colour = AppKit.NSColor.colorWithSRGBRed_green_blue_alpha_(red, green, blue, 1.0)

            def paint() -> None:  # Cocoa views are touched on the main thread only
                webview = window.native.webview
                if webview.respondsToSelector_("setUnderPageBackgroundColor:"):
                    webview.setUnderPageBackgroundColor_(colour)

            AppHelper.callAfter(paint)
        except Exception:  # cosmetic only: never stop the app for a colour
            pass
