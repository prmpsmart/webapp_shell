"""Owns the backend child process: start it, wait until it is healthy, ask it things, stop it."""

import os
import secrets
import socket
import subprocess
import time

import httpx

from .backend import CliFlag
from .json_types import JsonObject, JsonValue
from .settings import Settings


class BackendError(RuntimeError):
    """The backend could not be started or reached."""


class BackendProcess:
    def __init__(self, settings: Settings, keeps_preferences: bool = True, flags: tuple[CliFlag, ...] = ()):
        self._settings = settings
        self._wire = settings.config.backend.wire
        self._keeps_preferences = keeps_preferences
        self._flags = flags  # the project's switches that are on
        self._proc: subprocess.Popen[bytes] | None = None
        self._port = 0
        self.token = secrets.token_urlsafe(24)

    @property
    def base_url(self) -> str:
        return f"http://{self._settings.host}:{self._port}"

    @property
    def launch_url(self) -> str:
        """The URL a shell opens: it carries the token once; the backend turns it into a cookie."""
        return f"{self.base_url}/?{self._wire.token_query}={self.token}"

    def __enter__(self) -> "BackendProcess":
        self.start()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.stop()

    def start(self) -> None:
        if not (self._settings.frontend_dist / "index.html").is_file():
            raise BackendError(f"the compiled frontend is missing: {self._settings.frontend_dist}")
        self._port = self._port or self._free_port()  # a restart keeps the address the open page knows
        self._proc = subprocess.Popen(self._command(), env=self._environment())
        self._wait_until_healthy()

    @property
    def died(self) -> bool:
        """True when the process ended without `stop()` having been asked."""
        return self._proc is not None and self._proc.poll() is not None

    def restart(self) -> None:
        """Start the engine again on the same address and with the same token, so the page that is open reconnects
        by itself. What was open in it is closed (the person opens the database again); what was saved is safe."""
        self.stop()
        self.start()

    def stop(self) -> None:
        if self._proc is None:
            return
        self._proc.terminate()
        try:
            self._proc.wait(5)
        except subprocess.TimeoutExpired:
            self._proc.kill()
        self._proc = None

    def version(self) -> JsonObject:
        """What the backend says about itself, or nothing when the project has no version path."""
        if self._wire.version_path is None:
            return {}
        response = httpx.get(f"{self.base_url}{self._wire.version_path}", headers={self._wire.token_header: self.token})
        response.raise_for_status()
        body: JsonValue = response.json()
        if not isinstance(body, dict):
            raise BackendError("the version path did not answer with an object")
        return body

    def _command(self) -> list[str]:
        backend = self._settings.config.backend
        installation = self._settings.installation
        return [
            *installation.backend_command(backend),
            backend.port_argument, str(self._port),
            backend.frontend_argument, str(self._settings.frontend_dist),
            *self._preferences_arguments(),
            *backend.arguments,
            *([] if installation.frozen else backend.source_only_arguments),
            *(argument for flag in self._flags for argument in flag.passes),
        ]  # fmt: skip

    def _preferences_arguments(self) -> list[str]:
        """A headless check keeps its preferences in memory, so it never touches the user's file."""
        argument = self._settings.config.backend.preferences_argument
        if argument is None or not self._keeps_preferences:
            return []
        return [argument, str(self._settings.identity.app_preferences_path)]

    def _environment(self) -> dict[str, str]:
        paths = [str(p) for p in self._settings.package_dirs] + [os.environ.get("PYTHONPATH", "")]
        return {**os.environ, "PYTHONPATH": os.pathsep.join(paths), self._wire.token_env: self.token}

    def _free_port(self) -> int:
        with socket.socket() as s:
            s.bind((self._settings.host, 0))
            return s.getsockname()[1]

    def _wait_until_healthy(self) -> None:
        deadline = time.time() + self._settings.startup_timeout
        while time.time() < deadline and self._proc is not None and self._proc.poll() is None:
            try:
                if httpx.get(f"{self.base_url}{self._wire.health_path}", timeout=1).status_code == 200:
                    return
            except httpx.HTTPError:
                time.sleep(0.2)
        self.stop()
        raise BackendError("the backend did not start")
