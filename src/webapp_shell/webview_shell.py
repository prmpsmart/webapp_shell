"""Shell 2: pywebview (no Qt): the operating system's own web view."""

import time
from collections.abc import Callable

import webview

from .backend_process import BackendProcess
from .enums import ShellKind
from .native.os_actions import OsActions
from .native.webview_background import WebviewBackground
from .native.webview_bridge import WebviewBridge
from .native.webview_icon import WebviewIcon
from .native.webview_window import WebviewWindow
from .native.window import NativeContext
from .preferences import ShellPreferences
from .settings import Settings
from .shell import Shell
from .smoke import SETTLE_SECONDS, page_probe_js


class WebviewShell(Shell):
    name = ShellKind.WEBVIEW

    def __init__(
        self,
        settings: Settings,
        backend: BackendProcess,
        preferences: ShellPreferences | None = None,
        smoke: bool = False,
    ):
        super().__init__(settings, backend, preferences, smoke)
        self._window: webview.Window | None = None

    @property
    def window(self) -> webview.Window:
        if self._window is None:
            raise RuntimeError("the window is not created yet")
        return self._window

    def event_loop(self, boot: Callable[[], None]) -> None:
        native_window = WebviewWindow()
        bridge = WebviewBridge(self.native, NativeContext(native_window, self.preferences, OsActions()))
        window = webview.create_window(  # pyright: ignore[reportUnknownMemberType]  # pywebview's `url` is left open
            self.settings.identity.name,
            html=self.splash.loading(),
            js_api=bridge,
            background_color=self.settings.background_color,
            width=self.settings.window_size[0],
            height=self.settings.window_size[1],
        )
        if window is None:
            raise RuntimeError("pywebview did not create the window")
        self._window = window
        native_window.bind(window)
        icon = str(self.settings.window_icon) if self.settings.window_icon else None
        background = WebviewBackground(self.settings.background_color)
        dock_icon = WebviewIcon(self.settings.icon_png)

        def start() -> None:
            background.apply(window)
            dock_icon.apply()
            boot()

        webview.start(
            start, icon=icon
        )  # `boot` runs on a worker thread once the GUI is up; the icon is a .ico on Windows, a PNG elsewhere

    def navigate(self, url: str) -> None:
        self.window.load_url(url)

    def show_page(self, html: str) -> None:
        self.window.load_html(html)

    def set_title(self, title: str) -> None:
        self.window.set_title(title)

    def quit(self) -> None:
        self.window.destroy()

    def on_navigated(self) -> None:
        if not self.smoke:
            return
        time.sleep(SETTLE_SECONDS)
        self.finish_smoke(self.window.evaluate_js(page_probe_js(self.settings.identity.native_global)))
        self.quit()
