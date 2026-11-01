import dataclasses
import json
import os
import subprocess
import sys
from pathlib import Path

from webapp_shell.messages import MessageKey, ShellMessages
from webapp_shell.watchdog import BackendWatchdog

ROOT = Path(__file__).resolve().parents[1]


def test_every_key_has_a_field_and_every_field_a_key():
    fields = {field.name for field in dataclasses.fields(ShellMessages)}
    assert fields == {key.name.lower() for key in MessageKey}


def test_text_fills_the_placeholders():
    assert ShellMessages().text(MessageKey.BACKEND_GAVE_UP, name="Notes").endswith("Close Notes and open it again.")
    assert ShellMessages().text(MessageKey.FRONTEND_MISSING, path="/x") == "the compiled frontend is missing: /x"


def test_a_project_can_translate_the_sentences():
    spanish = ShellMessages(backend_gave_up="El servidor se detuvo. Cierre {name} y ábralo otra vez.")
    assert (
        spanish.text(MessageKey.BACKEND_GAVE_UP, name="Notas")
        == "El servidor se detuvo. Cierre Notas y ábralo otra vez."
    )


def test_the_watchdog_gives_up_in_the_projects_words():
    said: list[str] = []

    class Dead:
        died = True

        def restart(self) -> None:
            pass

    watchdog = BackendWatchdog(
        Dead(),
        said.append,
        "Notas",
        ShellMessages(backend_gave_up="Cierre {name}."),
        max_restarts=0,
    )
    watchdog.check()
    assert said == ["Cierre Notas."]


def test_the_catalogue_is_json_keyed_by_message_key():
    catalogue = ShellMessages().catalogue()
    assert set(catalogue) == {str(key) for key in MessageKey}
    json.dumps(catalogue)


def test_the_command_prints_the_same_catalogue():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}  # the library is not installed in the test environment
    out = subprocess.run(
        [sys.executable, "-m", "webapp_shell", "messages"], capture_output=True, text=True, check=True, env=env
    ).stdout
    assert json.loads(out) == ShellMessages().catalogue()


def test_the_translating_guide_shows_the_real_catalogue():
    guide = (ROOT / "docs" / "TRANSLATING.md").read_text(encoding="utf-8")
    shown = json.loads(guide.split("```json\n")[1].split("```")[0])
    assert shown == ShellMessages().catalogue()
    assert all(f"`{key}`" in guide for key in MessageKey)
