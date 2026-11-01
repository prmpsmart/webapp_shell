import pytest

from webapp_shell.cli import build_parser, check_libraries, run, run_backend
from webapp_shell.enums import ShellKind
from webapp_shell.installation import Installation


def test_the_window_toolkit_defaults_to_pywebview(config):
    assert build_parser(config).parse_args([]).shell is ShellKind.WEBVIEW


def test_the_command_line_takes_the_projects_switches(config):
    parser = build_parser(config)
    assert parser.parse_args(["qt"]).sandbox is False
    args = parser.parse_args(["webview", "--sandbox"])
    assert args.sandbox is True and args.shell is ShellKind.WEBVIEW


def test_the_help_names_the_program(config):
    assert "Acme Notes" in build_parser(config).description


def test_an_unknown_toolkit_is_refused(config):
    with pytest.raises(SystemExit):
        build_parser(config).parse_args(["gtk"])


def test_the_backend_flag_runs_the_backend_not_a_shell(config, monkeypatch):
    ran = []
    monkeypatch.setattr("fake_backend.__main__.main", lambda argv: ran.append(argv))
    assert run(config, [Installation.RUN_BACKEND, "--port", "1"]) == 0
    assert ran == [["--port", "1"]]
    assert run_backend(config, ["x"]) == 0


def test_the_check_command_reports_through_the_exit_code(config, capsys):
    from dataclasses import replace

    assert check_libraries(replace(config, required_libraries=("json",))) == 0
    assert run(replace(config, required_libraries=("nothing_here",)), [Installation.CHECK_LIBRARIES]) == 1
    assert "nothing_here" in capsys.readouterr().out


def test_a_project_check_adds_its_problems_to_the_library_check(config, capsys):
    import dataclasses

    from webapp_shell import LibraryProblem
    from webapp_shell.cli import check_libraries

    def codec() -> list[LibraryProblem]:
        return [LibraryProblem("PIL", "no support for webp")]

    assert check_libraries(dataclasses.replace(config, library_checks=(codec,))) == 1
    assert "PIL: no support for webp" in capsys.readouterr().out
    assert check_libraries(config) == 0
