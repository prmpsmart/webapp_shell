"""Shell 1: Qt WebEngine (bundled Chromium)."""

import os
import sys
import threading

from PySide6.QtCore import QObject, QTimer, QUrl, Signal
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineScript
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication

from .enums import ShellKind
from .native.qt_bridge import CHANNEL_OBJECT, QtBridge
from .shell import Shell
from .smoke import SETTLE_SECONDS, page_probe_js


class _Dispatcher(QObject):
    """Lets the worker thread ask the GUI thread to act (Qt widgets must only be touched there)."""

    navigate = Signal(str)
    show_page = Signal(str)
    set_title = Signal(str)
    quit = Signal()


class QtShell(Shell):
    name = ShellKind.QT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.smoke:
            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        self._app = QApplication(sys.argv)
        self._view = QWebEngineView()
        self._apply_icon()
        self._apply_background()
        self._dispatcher = _Dispatcher()
        self._wire_dispatcher()
        self._install_native_bridge()

    def event_loop(self, boot) -> None:
        self._view.setWindowTitle(self.settings.identity.name)
        self._view.resize(*self.settings.window_size)
        self._view.setHtml(self.splash.loading())
        if self.smoke:  # headless: never show the window (offscreen GPU rendering is unreliable)
            self._view.loadFinished.connect(self._on_load_finished)
            QTimer.singleShot(30_000, self._app.quit)
        else:
            self._view.show()
        QTimer.singleShot(0, lambda: threading.Thread(target=boot, daemon=True).start())
        self._app.exec()

    def navigate(self, url: str) -> None:
        self._dispatcher.navigate.emit(url)

    def show_page(self, html: str) -> None:
        self._dispatcher.show_page.emit(html)

    def set_title(self, title: str) -> None:
        self._dispatcher.set_title.emit(title)

    def quit(self) -> None:
        self._dispatcher.quit.emit()

    def _apply_icon(self) -> None:
        if self.settings.icon_png:
            icon = QIcon(str(self.settings.icon_png))
            self._app.setWindowIcon(icon)
            self._view.setWindowIcon(icon)

    def _apply_background(self) -> None:
        """The page and the widget behind it start in the app's colour, so nothing flashes white."""
        colour = self.settings.background_color
        self._view.page().setBackgroundColor(QColor(colour))
        self._view.setStyleSheet(f"background:{colour}")

    def _wire_dispatcher(self) -> None:
        d = self._dispatcher
        d.navigate.connect(lambda url: self._view.load(QUrl(url)))
        d.show_page.connect(self._view.setHtml)
        d.set_title.connect(self._view.setWindowTitle)
        d.quit.connect(self._app.quit)

    def _install_native_bridge(self) -> None:
        self._channel = QWebChannel(self._view.page())
        self._channel.registerObject(CHANNEL_OBJECT, QtBridge(self._view, preferences=self.preferences))
        self._view.page().setWebChannel(self._channel)
        script = QWebEngineScript()
        script.setName(f"{self.settings.identity.slug}-native")
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setSourceCode(QtBridge.page_script_source(self.settings.identity))
        self._view.page().scripts().insert(script)

    def _on_load_finished(self, _ok: bool) -> None:
        if self._view.url().scheme() == "http":  # the frontend, not the splash
            QTimer.singleShot(int(SETTLE_SECONDS * 1000), self._probe)

    def _probe(self) -> None:
        self._view.page().runJavaScript(page_probe_js(self.settings.identity.native_global), self._on_probe)

    def _on_probe(self, page: str) -> None:
        self.finish_smoke(page)
        self._app.quit()
