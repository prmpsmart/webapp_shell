from dataclasses import replace

from webapp_shell.backend_process import BackendProcess
from webapp_shell.installation import Installation
from webapp_shell.settings import Settings

from .conftest import SANDBOX


def test_the_projects_switch_reaches_the_backend_only_when_it_is_on(settings):
    assert "--sandbox" not in BackendProcess(settings)._command()
    assert "--sandbox" in BackendProcess(settings, flags=(SANDBOX,))._command()


def test_the_token_is_handed_over_in_the_environment_not_on_the_command_line(settings):
    process = BackendProcess(settings)
    assert process.token not in " ".join(process._command())
    assert process._environment()["ACME_TOKEN"] == process.token


def test_the_command_names_the_module_the_port_and_the_compiled_frontend(settings):
    command = BackendProcess(settings)._command()
    assert command[1:3] == ["-m", "fake_backend"]
    assert command[command.index("--frontend") + 1] == str(settings.frontend_dist)
    assert "--port" in command and "--always" in command


def test_source_only_arguments_are_left_out_of_a_frozen_program(config, tmp_path):
    def command(frozen: bool) -> list[str]:
        settings = replace(
            Settings.of(config), installation=Installation(config.source_root, frozen=frozen, bundle=tmp_path)
        )
        return BackendProcess(settings)._command()

    assert "--developer" in command(frozen=False)
    assert "--developer" not in command(frozen=True)
    assert "--always" in command(frozen=True)


def test_a_headless_check_never_hands_over_the_users_preferences_file(settings):
    assert "--preferences-file" in BackendProcess(settings)._command()
    assert "--preferences-file" not in BackendProcess(settings, keeps_preferences=False)._command()


def test_a_backend_without_a_preferences_file_is_never_given_one(config):
    backend = replace(config.backend, preferences_argument=None)
    settings = Settings.of(replace(config, backend=backend))
    assert "--preferences-file" not in BackendProcess(settings)._command()
