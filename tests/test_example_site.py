"""The documentation site is run for real: its backend, its launcher, its code samples and its committed build."""

import importlib.util
import os
import re
import shutil
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from webapp_shell.backend_process import BackendProcess
from webapp_shell.settings import Settings

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "examples" / "site"
BRIDGE = ROOT / "src" / "webapp_shell" / "bridge"


@pytest.fixture
def site_path(monkeypatch):
    monkeypatch.syspath_prepend(str(SITE))
    monkeypatch.setenv("PYTHONPATH", str(ROOT / "src"))  # the library is not installed in the test environment


def load_launcher():
    """The site's app.py, loaded by path: the minimal example has a module of the same name."""
    spec = importlib.util.spec_from_file_location("site_app", SITE / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_sites_bridge_copy_is_the_one_in_the_package():
    for name in ("webapp-shell-bridge.js", "webapp-shell-bridge.d.ts"):
        assert (SITE / "src" / "bridge" / name).read_text() == (BRIDGE / name).read_text(), name


def test_the_backend_is_started_by_the_shell_and_follows_the_contract(site_path, tmp_path):
    import httpx

    config = load_launcher().config
    settings = Settings.of(replace(config, identity=replace(config.identity, storage_dir=tmp_path)))
    with BackendProcess(settings, keeps_preferences=False) as process:
        headers = {"x-docs-token": process.token}
        file = tmp_path / "note.txt"
        file.write_text("hello")
        described = httpx.get(f"{process.base_url}/api/describe", params={"path": str(file)}, headers=headers)
        assert described.json() == {"name": "note.txt", "bytes": 5}
        assert (
            httpx.get(f"{process.base_url}/api/describe", params={"path": str(tmp_path)}, headers=headers).status_code
            == 404
        )
        assert httpx.get(f"{process.base_url}/api/describe").status_code == 401  # no token

        target = tmp_path / "saved.txt"
        saved = httpx.post(f"{process.base_url}/api/save", json={"path": str(target), "text": "abc"}, headers=headers)
        assert saved.json() == {"bytes": 3}
        assert target.read_text() == "abc"
        missing = tmp_path / "no-such-folder" / "x.txt"
        refused = httpx.post(f"{process.base_url}/api/save", json={"path": str(missing), "text": ""}, headers=headers)
        assert refused.status_code == 400


def test_the_getting_started_launcher_sample_builds_a_config(tmp_path):
    page = (SITE / "src" / "pages" / "GettingStarted.tsx").read_text()
    sample = re.search(r"const LAUNCHER = `(.*?)`", page, re.S).group(1)
    sample = sample.replace("raise SystemExit(run(config))", "")  # building it is the test; running it opens a window
    scope = {"__file__": str(tmp_path / "launch.py")}
    exec(sample, scope)
    assert scope["config"].identity.slug == "acme"
    assert scope["config"].backend.module == "acme_backend"


def test_the_committed_build_contains_the_code_it_shows():
    """A stale `dist` would show code that is no longer the code: rebuild with `npm run build` in examples/site."""
    bundle = "".join(path.read_text() for path in (SITE / "frontend" / "dist" / "assets").glob("*.js"))
    assert "async def describe" in bundle
    for shown in ("chooseAndDescribe", "chooseAndSave", "chooseAndReveal", "openInBrowser", "applyZoom"):
        assert shown in bundle, shown
    assert "async def save_note" in bundle


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_site_renders_in_the_qt_shell(tmp_path):
    pytest.importorskip("PySide6.QtWebEngineWidgets")
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(ROOT / "src"), str(SITE)]), "HOME": str(tmp_path)}
    done = subprocess.run(
        [sys.executable, str(SITE / "app.py"), "qt", "--smoke"],
        capture_output=True, text=True, timeout=120, env=env, cwd=SITE,
    )  # fmt: skip
    assert done.returncode == 0, done.stderr
    assert '"native":"docsNative"' in done.stdout
    assert '"title":"Overview · webapp_shell"' in done.stdout
