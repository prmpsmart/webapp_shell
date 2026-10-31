"""The backend's side of the contract, against a small Starlette app: the same checks Pixeval's backend makes."""

import argparse
from pathlib import Path

import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from webapp_shell.backend_process import BackendProcess
from webapp_shell.contract import (
    OriginPolicy,
    TokenValidator,
    add_launch_arguments,
    read_launch_arguments,
)
from webapp_shell.contract.guard import GuardResponses, TokenGuard

TOKEN = "test-token"


@pytest.fixture
def wire(config):
    return config.backend.wire


@pytest.fixture
def make_client(wire):
    def make(**guard) -> TestClient:
        async def page(_request):
            return PlainTextResponse("the page")

        async def api(_request):
            return JSONResponse({"ok": True})

        app = Starlette(
            routes=[Route("/", page), Route("/api/health", api), Route("/api/version", api)],
        )
        app.add_middleware(TokenGuard, validator=TokenValidator(TOKEN, wire), wire=wire, **guard)
        return TestClient(app, follow_redirects=False)

    return make


@pytest.fixture
def client(make_client):
    return make_client()


def test_health_is_open(client):
    assert client.get("/api/health").status_code == 200


def test_the_api_requires_the_token(client):
    assert client.get("/api/version").status_code == 401
    assert client.get("/api/version", headers={"x-acme-token": "wrong"}).status_code == 401
    assert client.get("/api/version").json() == {"code": "UNAUTHORIZED"}


def test_the_header_token_is_accepted(client):
    assert client.get("/api/version", headers={"x-acme-token": TOKEN}).status_code == 200


def test_the_launch_url_sets_the_cookie_and_redirects_keeping_other_params(client):
    response = client.get(f"/?token={TOKEN}&lang=es")
    assert response.status_code == 307
    assert response.headers["location"].endswith("/?lang=es")
    assert "acme_token" in response.headers["set-cookie"]


def test_the_cookie_then_opens_the_api(make_client):
    session = make_client()
    session.follow_redirects = True
    session.get(f"/?token={TOKEN}")
    assert session.get("/api/version").status_code == 200


def test_a_wrong_launch_token_grants_nothing(make_client):
    session = make_client()
    session.get("/?token=nope")
    assert session.get("/api/version").status_code == 401


def test_the_frontend_is_served_without_a_token(client):
    assert client.get("/").status_code == 200


def test_a_token_with_characters_outside_ascii_is_refused_not_a_crash(client):
    assert client.get("/api/version", headers={"x-acme-token": "é".encode()}).status_code == 401
    assert client.get("/?token=t%C3%B6k%C3%A9n").status_code == 200


def test_another_page_of_the_same_machine_is_refused_even_with_the_cookie(make_client):
    session = make_client()
    session.cookies.set("acme_token", TOKEN)
    foreign = session.get("/api/version", headers={"origin": "http://127.0.0.1:9999"})
    assert foreign.status_code == 403 and foreign.json() == {"code": "FOREIGN_ORIGIN"}
    assert session.get("/api/version", headers={"origin": "http://testserver"}).status_code == 200


def test_a_project_can_use_its_own_error_bodies(make_client):
    custom = GuardResponses(unauthorized={"error": "no"}, foreign_origin={"error": "elsewhere"})
    assert make_client(responses=custom).get("/api/version").json() == {"error": "no"}


def test_a_socket_may_carry_the_token_in_a_header_the_cookie_or_the_query(wire):
    validator = TokenValidator(TOKEN, wire)
    assert validator.is_valid_connection({"x-acme-token": TOKEN}, {}, {})
    assert validator.is_valid_connection({}, {"acme_token": TOKEN}, {})
    assert validator.is_valid_connection({}, {}, {"token": TOKEN})
    assert not validator.is_valid_connection({}, {}, {})
    assert not validator.is_valid_connection({"x-acme-token": "no"}, {}, {})


def test_origin_policy_allows_tools_and_the_apps_own_page_only():
    policy = OriginPolicy()
    assert policy.allows(None, "127.0.0.1:1")
    assert policy.allows("http://127.0.0.1:1", "127.0.0.1:1")
    assert not policy.allows("http://127.0.0.1:2", "127.0.0.1:1")
    assert not policy.allows("http://x", None)


class TestLaunchArguments:
    def parse(self, config, argv, environ=None):
        parser = argparse.ArgumentParser()
        add_launch_arguments(parser, config.backend)
        return read_launch_arguments(parser, parser.parse_args(argv), config.backend.wire), parser

    def test_the_backend_reads_back_exactly_what_the_shell_builds(self, settings, monkeypatch):
        process = BackendProcess(settings)
        monkeypatch.setenv("ACME_TOKEN", process.token)
        process._port = 4321
        command = process._command()
        parser = argparse.ArgumentParser()
        add_launch_arguments(parser, settings.config.backend)
        args, _unknown = parser.parse_known_args(command[3:])  # after: python -m fake_backend
        launch = read_launch_arguments(parser, args, settings.config.backend.wire)
        assert launch.port == 4321
        assert launch.frontend == settings.frontend_dist
        assert launch.preferences_file == Path(settings.identity.app_preferences_path)
        assert launch.host == "127.0.0.1"

    def test_the_token_comes_from_the_environment(self, config, monkeypatch):
        monkeypatch.setenv("ACME_TOKEN", "from-env")
        launch, _ = self.parse(config, ["--port", "1"])
        assert launch.token == "from-env"

    def test_a_missing_token_is_reported_by_the_parser(self, config, monkeypatch, capsys):
        monkeypatch.delenv("ACME_TOKEN", raising=False)
        with pytest.raises(SystemExit):
            self.parse(config, ["--port", "1"])
        assert "ACME_TOKEN" in capsys.readouterr().err

    def test_a_backend_without_a_preferences_file_has_none(self, config, monkeypatch):
        from dataclasses import replace

        monkeypatch.setenv("ACME_TOKEN", "t")
        no_prefs = replace(config, backend=replace(config.backend, preferences_argument=None))
        launch, _ = self.parse(no_prefs, ["--port", "1"])
        assert launch.preferences_file is None


def test_the_core_of_the_contract_needs_no_web_framework():
    import subprocess
    import sys

    code = "import sys, webapp_shell.contract; sys.exit(1 if 'starlette' in sys.modules else 0)"
    source = str(Path(__file__).resolve().parents[1] / "src")
    assert subprocess.run([sys.executable, "-c", code], env={"PYTHONPATH": source}).returncode == 0
