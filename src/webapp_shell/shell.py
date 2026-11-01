"""The shell contract. A concrete shell only knows how to show a window; everything else lives here."""

import time
from abc import ABC, abstractmethod
from collections.abc import Callable

from .backend_process import BackendError, BackendProcess
from .json_types import JsonObject
from .native.registry import NativeRegistry
from .native.standard import standard_functions
from .preferences import ShellPreferences
from .settings import Settings
from .smoke import SmokeReport
from .splash import SplashPage
from .watchdog import BackendWatchdog


class Shell(ABC):
    """Template: show a splash at once, start the backend off the UI thread, then show the frontend.

    `boot()` runs on a worker thread, so every method it calls on a subclass must be safe to call from there.
    """

    name: str = "shell"

    def __init__(
        self,
        settings: Settings,
        backend: BackendProcess,
        preferences: ShellPreferences | None = None,
        smoke: bool = False,
    ):
        self.settings = settings
        self.preferences = preferences or ShellPreferences(None)
        self.backend = backend
        self.smoke = smoke
        self.backend_version: JsonObject = {}
        self.failed = False
        self.splash = SplashPage(settings.identity.name, settings.icon_png, settings.boot_colors)
        self.watchdog = BackendWatchdog(backend, self.report_error, settings.identity.name, settings.config.messages)
        self.native = NativeRegistry((*standard_functions(), *settings.config.native_functions))

    @property
    def window_title(self) -> str:
        """The program's name. Running from the source it also names the shell and the backend version, for the team."""

        name = self.settings.identity.name
        if self.settings.installation.frozen:
            return name
        return f"{name} ({self.name}) · backend {self.backend_version.get('version', '?')}"

    def run(self) -> int:
        try:
            self.event_loop(self.boot)
        finally:
            self.watchdog.stop()
            self.backend.stop()
        return 1 if self.failed else 0

    def boot(self) -> None:
        started = time.monotonic()
        try:
            self.backend.start()
            self.backend_version = self.backend.version()
        except BackendError as error:
            self.report_error(str(error))
            return
        self.hold_splash(started)
        self.set_title(self.window_title)
        self.navigate(self.backend.launch_url)
        self.on_navigated()
        if not self.smoke:
            self.watchdog.start()

    def hold_splash(
        self,
        started: float,
        now: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        """Keep the splash up until `splash_seconds` have passed since `started` (the backend may be ready sooner)."""
        remaining = self.settings.splash_seconds - (now() - started)
        if remaining > 0:
            sleep(remaining)

    def report_error(self, message: str) -> None:
        self.failed = True
        print(message)
        self.show_page(self.splash.error(message))
        if self.smoke:
            self.quit()

    def finish_smoke(self, page: str) -> None:
        print(SmokeReport(self.name, self.backend_version, page))

    # --- what a concrete shell provides ---------------------------------------------------------

    @abstractmethod
    def event_loop(self, boot: Callable[[], None]) -> None:
        """Show the window with the loading splash, call `boot()` on a worker thread, block until closed."""

    @abstractmethod
    def navigate(self, url: str) -> None:
        """Load `url` in the window. Thread-safe."""

    @abstractmethod
    def show_page(self, html: str) -> None:
        """Replace the window content with an HTML page. Thread-safe."""

    @abstractmethod
    def set_title(self, title: str) -> None:
        """Thread-safe."""

    @abstractmethod
    def quit(self) -> None:
        """Close the window. Thread-safe."""

    def on_navigated(self) -> None:  # noqa: B027 - an optional hook, empty on purpose
        """Hook run on the worker thread after `navigate`; shells use it for the headless self-check."""
