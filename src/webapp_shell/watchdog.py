"""Notices when the engine has stopped by itself and starts it again, a few times, before giving up."""

import threading
import time
from collections import deque
from collections.abc import Callable

from .backend_process import BackendError, BackendProcess
from .messages import ENGLISH, MessageKey, ShellMessages


class BackendWatchdog:
    def __init__(
        self,
        backend: BackendProcess,
        give_up: Callable[[str], None],
        name: str = "the program",
        messages: ShellMessages = ENGLISH,
        interval: float = 1.0,
        max_restarts: int = 3,
        window: float = 120.0,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.backend, self.give_up = backend, give_up
        self._give_up_message = messages.text(MessageKey.BACKEND_GAVE_UP, name=name)
        self.interval, self.max_restarts, self.window = interval, max_restarts, window
        self._clock = clock
        self._restarts: deque[float] = deque()
        self._stopped = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._loop, name="backend-watchdog", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stopped.set()

    def check(self) -> None:
        """One look. A dead engine is restarted unless that already happened `max_restarts` times within `window`."""
        if not self.backend.died:
            return
        now = self._clock()
        while self._restarts and now - self._restarts[0] > self.window:
            self._restarts.popleft()
        if len(self._restarts) >= self.max_restarts:
            return self._give_up(self._give_up_message)
        self._restarts.append(now)
        try:
            self.backend.restart()
        except BackendError as error:
            self._give_up(str(error))

    def _give_up(self, message: str) -> None:
        self.stop()
        self.give_up(message)

    def _loop(self) -> None:
        while not self._stopped.wait(self.interval):
            self.check()
