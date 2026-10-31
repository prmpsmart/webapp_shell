"""The window title: the team sees the shell and the backend version while developing; users see the name."""

from types import SimpleNamespace

from webapp_shell.shell import Shell


def title(frozen: bool, name: str = "webview", version: str = "0.1.0") -> str:
    shell = SimpleNamespace(
        name=name,
        backend_version={"version": version},
        settings=SimpleNamespace(
            installation=SimpleNamespace(frozen=frozen), identity=SimpleNamespace(name="Acme Notes")
        ),
    )
    return Shell.window_title.fget(shell)


def test_running_from_the_source_names_the_shell_and_the_backend():
    assert title(frozen=False) == "Acme Notes (webview) · backend 0.1.0"
    assert title(frozen=False, name="qt", version="1.2.3") == "Acme Notes (qt) · backend 1.2.3"


def test_the_frozen_program_shows_only_its_name():
    assert title(frozen=True) == "Acme Notes"
    assert title(frozen=True, name="qt", version="1.2.3") == "Acme Notes"
