import ast
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

from webapp_shell.__main__ import main as tools_main
from webapp_shell.enums import ShellKind
from webapp_shell.freezing import DataFolder, FreezePlan
from webapp_shell.freezing.entry import entry_source
from webapp_shell.freezing.profile import PROFILES
from webapp_shell.freezing.verify import BuildVerifier

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
MINIMAL = ROOT / "examples" / "minimal"
PLAN = FreezePlan(
    product="Acme", config="app:config", packages=("acme_backend",), required=("frontend/dist/index.html",)
)


def test_a_plan_is_found_by_its_reference(monkeypatch):
    monkeypatch.syspath_prepend(str(MINIMAL))
    plan = FreezePlan.load("freeze_plan:PLAN")
    assert plan.product == "AcmeNotes" and plan.data_folders == (
        DataFolder(MINIMAL / "frontend" / "dist", "frontend/dist"),
    )


def test_a_reference_to_something_else_is_refused(monkeypatch):
    monkeypatch.syspath_prepend(str(MINIMAL))
    with pytest.raises(TypeError, match="not a FreezePlan"):
        FreezePlan.load("app:config")


@pytest.mark.parametrize("kind", list(ShellKind))
def test_the_entry_file_is_python_that_runs_the_config_with_its_shell(kind):
    source = entry_source(PLAN, kind)
    ast.parse(source)
    assert "from app import config as target" in source and f'["{kind.value}", *args]' in source


def test_each_shell_leaves_out_the_other_shells_modules_and_libraries():
    qt, webview = PROFILES[ShellKind.QT], PROFILES[ShellKind.WEBVIEW]
    assert not qt.wanted_module("webapp_shell.native.zoom") and qt.wanted_module("webapp_shell.native.qt_window")
    assert not webview.wanted_module("webapp_shell.qt_shell") and webview.wanted_module("webapp_shell.native.zoom")
    assert "webview" in qt.excludes and "PySide6" in webview.excludes and "tkinter" in qt.excludes


def test_every_module_a_profile_names_exists():
    for profile in PROFILES.values():
        for module in profile.modules:
            assert (SOURCE / Path(*module.split("."))).with_suffix(".py").is_file(), module


def test_the_library_loads_without_pywebview_so_a_qt_build_can_leave_it_out():
    """A Qt build excludes `webview`; reaching it from a shared module broke the frozen Qt program once."""
    code = "import sys; sys.modules['webview'] = None; import webapp_shell, webapp_shell.native.standard"
    done = subprocess.run(
        [sys.executable, "-c", code], env={**os.environ, "PYTHONPATH": str(SOURCE)}, capture_output=True, text=True
    )
    assert done.returncode == 0, done.stderr


def build_folder(tmp_path: Path, *, page: bool = True, executable: bool = True, extra: str = "") -> Path:
    folder = tmp_path / "Acme"
    (folder / "_internal" / "frontend" / "dist").mkdir(parents=True)
    if page:
        (folder / "_internal" / "frontend" / "dist" / "index.html").write_text("<title>x</title>")
    if executable:
        (folder / "Acme").write_text("")
    if extra:
        (folder / "_internal" / extra).mkdir(parents=True)
    return folder


def problems(folder: Path, kind: ShellKind) -> list[str]:
    return [f"{finding.path}: {finding.problem}" for finding in BuildVerifier(folder, PROFILES[kind], PLAN).findings()]


def test_a_complete_build_has_no_findings(tmp_path):
    assert problems(build_folder(tmp_path), ShellKind.WEBVIEW) == []


def test_a_missing_page_and_a_missing_executable_are_reported(tmp_path):
    found = problems(build_folder(tmp_path, page=False, executable=False), ShellKind.WEBVIEW)
    assert "frontend/dist/index.html: missing" in found and "Acme: the executable is missing" in found


def test_the_other_shells_libraries_in_a_build_are_reported(tmp_path):
    folder = build_folder(tmp_path, extra="PySide6")
    assert problems(folder, ShellKind.WEBVIEW) == ["_internal/PySide6: belongs to the other shell"]
    assert problems(folder, ShellKind.QT) == []


def test_the_freeze_command_has_its_own_help():
    with pytest.raises(SystemExit) as exit_:
        tools_main(["freeze", "--help"])
    assert exit_.value.code == 0


@pytest.mark.freeze
@pytest.mark.skipif(importlib.util.find_spec("PyInstaller") is None, reason="PyInstaller is not installed")
def test_the_minimal_example_freezes_and_the_frozen_program_checks_itself(tmp_path):
    """Slow (it runs PyInstaller): `python -m pytest -m freeze`. The command also runs the frozen `--check-libraries`."""
    done = subprocess.run(
        [sys.executable, "-m", "webapp_shell", "freeze", "freeze_plan:PLAN", "--path", ".", "webview",
         "--output", str(tmp_path / "dist"), "--work", str(tmp_path / "build")],
        cwd=MINIMAL, capture_output=True, text=True,
    )  # fmt: skip
    assert done.returncode == 0, done.stdout[-2000:] + done.stderr[-2000:]
    assert "checked" in done.stdout
