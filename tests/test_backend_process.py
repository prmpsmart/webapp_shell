"""The contract with a real child process: start, health, token, version, restart, stop."""

import httpx
import pytest

from webapp_shell.backend_process import BackendError, BackendProcess

from .conftest import SANDBOX


def test_the_backend_starts_answers_with_the_token_and_stops(settings):
    with BackendProcess(settings, flags=(SANDBOX,)) as process:
        version = process.version()
        assert version["version"] == "1.2.3"
        assert "--sandbox" in version["argv"]
        assert process.launch_url == f"{process.base_url}/?token={process.token}"
        wrong = httpx.get(f"{process.base_url}/api/version", headers={"x-acme-token": "nope"})
        assert wrong.status_code == 401
        assert not process.died
    assert process._proc is None


def test_a_restart_keeps_the_address_and_the_token(settings):
    with BackendProcess(settings) as process:
        url, token = process.base_url, process.token
        process.restart()
        assert (process.base_url, process.token) == (url, token)
        assert process.version()["version"] == "1.2.3"


def test_a_missing_compiled_frontend_is_named(settings):
    (settings.frontend_dist / "index.html").unlink()
    with pytest.raises(BackendError, match="compiled frontend is missing"):
        BackendProcess(settings).start()


def test_a_project_without_a_version_path_gets_an_empty_version(config):
    from dataclasses import replace

    from webapp_shell.settings import Settings

    wire = replace(config.backend.wire, version_path=None)
    settings = Settings.of(replace(config, backend=replace(config.backend, wire=wire)))
    assert BackendProcess(settings).version() == {}
