"""Page zoom (Cmd/Ctrl +, -, 0). The page decides the factor and keeps it as an app preference; each shell only
applies it to its web view. Qt has `setZoomFactor`; pywebview has no zoom call, so each system's own web view is
reached here, one small class per system."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownLambdaType=false
# pyright: reportUnknownArgumentType=false, reportMissingTypeStubs=false, reportMissingImports=false
# pyright: reportAttributeAccessIssue=false
# The lines below talk to AppKit (PyObjC), .NET and GTK, which publish no type stubs. Their inside is untyped by
# necessity; the signatures of this module are typed.

import sys
import threading
from abc import ABC, abstractmethod
from collections.abc import Callable

import webview

MAIN_THREAD_WAIT = 2.0  # seconds to wait for the system's UI thread


class ZoomSurface(ABC):
    """How to set the page zoom of a pywebview window on one system. `apply` says whether it was applied."""

    @abstractmethod
    def apply(self, window: webview.Window, factor: float) -> bool: ...


class MacZoom(ZoomSurface):
    """The window's content view is the WKWebView; its `pageZoom` reflows the page like a browser's zoom does.
    Cocoa views are touched on the main thread only, and the call waits so a failure is reported."""

    def __init__(self, on_main: Callable[[Callable[[], None]], None] | None = None):
        self._on_main = on_main or self._app_helper

    def apply(self, window: webview.Window, factor: float) -> bool:
        done = threading.Event()
        result: list[bool] = []

        def zoom() -> None:
            try:
                window.native.contentView().setPageZoom_(factor)
                result.append(True)
            except Exception:  # cosmetic only: never stop the app for a zoom
                result.append(False)
            finally:
                done.set()

        try:
            self._on_main(zoom)
        except Exception:
            return False
        return done.wait(MAIN_THREAD_WAIT) and bool(result and result[0])

    @staticmethod
    def _app_helper(call: Callable[[], None]) -> None:
        from PyObjCTools import AppHelper

        AppHelper.callAfter(call)


class WindowsZoom(ZoomSurface):
    """WebView2's `ZoomFactor`. The browser's own Ctrl +/- are off in a released program, the page's shortcuts do it."""

    def apply(self, window: webview.Window, factor: float) -> bool:
        try:
            from System import Func, Type

            form = window.native

            def zoom() -> None:
                form.webview.ZoomFactor = factor

            form.Invoke(Func[Type](zoom))  # waits for the form's thread
            return True
        except Exception:
            return False


class GtkZoom(ZoomSurface):
    """WebKitGTK's `set_zoom_level`, called on the GTK main loop."""

    def apply(self, window: webview.Window, factor: float) -> bool:
        try:
            from gi.repository import GLib

            view = window.native.webview
            GLib.idle_add(lambda: view.set_zoom_level(factor) and False)
            return True
        except Exception:
            return False


class WebviewZoom:
    def __init__(self, surface: ZoomSurface | None = None):
        self._surface = surface or self._for_this_system()

    @staticmethod
    def _for_this_system() -> ZoomSurface:
        if sys.platform == "darwin":
            return MacZoom()
        return WindowsZoom() if sys.platform == "win32" else GtkZoom()

    def apply(self, window: webview.Window, factor: float) -> bool:
        return self._surface.apply(window, factor)
