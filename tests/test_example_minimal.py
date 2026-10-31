"""The minimal example is run for real, so it cannot go stale."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from webapp_shell.backend_process import BackendProcess
from webapp_shell.settings import Settings

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "minimal"
BRIDGE = ROOT / "src" / "webapp_shell" / "bridge"


@pytest.fixture
def example_path(monkeypatch):
    monkeypatch.syspath_prepend(str(EXAMPLE))
    monkeypatch.setenv("PYTHONPATH", str(ROOT / "src"))  # the library is not installed in the test environment


@pytest.fixture
def example_settings(example_path, tmp_path):
    from dataclasses import replace

    import app  # the example's launcher

    identity = replace(app.config.identity, storage_dir=tmp_path)
    return Settings.of(replace(app.config, identity=identity))


def test_the_examples_bridge_copy_is_the_one_in_the_package():
    for name in ("webapp-shell-bridge.js", "webapp-shell-bridge.d.ts"):
        assert (EXAMPLE / "frontend" / "dist" / name).read_text() == (BRIDGE / name).read_text(), name


def test_the_backend_is_started_by_the_shell_and_follows_the_contract(example_settings, tmp_path):
    import httpx

    with BackendProcess(example_settings, keeps_preferences=False) as process:
        assert process.version() == {"version": "0.1.0"}
        headers = {"x-acme-token": process.token}
        file = tmp_path / "note.txt"
        file.write_text("hello")
        described = httpx.get(f"{process.base_url}/api/describe", params={"path": str(file)}, headers=headers)
        assert described.json() == {"name": "note.txt", "bytes": 5}
        assert (
            httpx.get(f"{process.base_url}/api/describe", params={"path": str(tmp_path)}, headers=headers).status_code
            == 404
        )
        assert httpx.get(f"{process.base_url}/api/describe").status_code == 401  # no token


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_page_finds_the_qt_shells_object_through_the_real_channel(tmp_path):
    """The headless Qt run: real QWebChannel, the injected glue, and the page's bridge file together."""
    pytest.importorskip("PySide6.QtWebEngineWidgets")
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(ROOT / "src"), str(EXAMPLE)]), "HOME": str(tmp_path)}
    done = subprocess.run(
        [sys.executable, str(EXAMPLE / "app.py"), "qt", "--smoke"],
        capture_output=True, text=True, timeout=120, env=env, cwd=EXAMPLE,
    )  # fmt: skip
    assert done.returncode == 0, done.stderr
    assert '"title":"Acme Notes (qt)"' in done.stdout
    assert '"native":"acmeNative"' in done.stdout
    assert '"rootChildren":1' in done.stdout
