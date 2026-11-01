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


def _settings_for(config, tmp_path, module, source, timeout):
    """A project whose backend is the one-line program `source`, found in `tmp_path`."""
    import dataclasses

    from webapp_shell.installation import Installation
    from webapp_shell.settings import Settings

    package = tmp_path / "backends" / module
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "__main__.py").write_text(source)
    backend = dataclasses.replace(config.backend, module=module, package_dirs=(tmp_path / "backends",), arguments=())
    config = dataclasses.replace(config, backend=backend, startup_timeout=timeout)
    return Settings.of(config, installation=Installation(config.source_root, frozen=False))


def test_a_backend_that_stops_while_starting_says_so_with_its_exit_code(config, tmp_path):
    settings = _settings_for(config, tmp_path, "quits_at_once", "raise SystemExit(3)", timeout=10.0)
    with pytest.raises(BackendError, match=r"stopped while starting \(exit code 3\)"):
        BackendProcess(settings).start()


def test_a_backend_that_never_answers_names_the_path_and_the_time(config, tmp_path):
    settings = _settings_for(config, tmp_path, "never_answers", "import time; time.sleep(30)", timeout=1.0)
    with pytest.raises(BackendError, match=r"did not answer /api/health within 1 seconds"):
        BackendProcess(settings).start()
