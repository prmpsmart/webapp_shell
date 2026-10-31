"""Shell 2: pywebview (no Qt): the operating system's own web view."""

import time

import webview

from .enums import ShellKind
from .native.webview_background import WebviewBackground
from .native.webview_bridge import WebviewBridge
from .native.webview_icon import WebviewIcon
from .shell import Shell
from .smoke import SETTLE_SECONDS, page_probe_js


class WebviewShell(Shell):
    name = ShellKind.WEBVIEW

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._window: webview.Window | None = None

    def event_loop(self, boot) -> None:
        bridge = WebviewBridge(preferences=self.preferences)
        self._window = webview.create_window(
            self.settings.identity.name,
            html=self.splash.loading(),
            js_api=bridge,
            background_color=self.settings.background_color,
            width=self.settings.window_size[0],
            height=self.settings.window_size[1],
        )
        bridge.bind(self._window)
        icon = str(self.settings.window_icon) if self.settings.window_icon else None
        background = WebviewBackground(self.settings.background_color)
        dock_icon = WebviewIcon(self.settings.icon_png)

        def start(*args):
            background.apply(self._window)
            dock_icon.apply()
            boot(*args)

        webview.start(
            start, icon=icon
        )  # `boot` runs on a worker thread once the GUI is up; the icon is a .ico on Windows, a PNG elsewhere

    def navigate(self, url: str) -> None:
        self._window.load_url(url)

    def show_page(self, html: str) -> None:
        self._window.load_html(html)

    def set_title(self, title: str) -> None:
        self._window.set_title(title)

    def quit(self) -> None:
        self._window.destroy()

    def on_navigated(self) -> None:
        if not self.smoke:
            return
        time.sleep(SETTLE_SECONDS)
        self.finish_smoke(self._window.evaluate_js(page_probe_js(self.settings.identity.native_global)))
        self.quit()
