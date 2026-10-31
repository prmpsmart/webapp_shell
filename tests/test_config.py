import pytest

from webapp_shell import AppIdentity, WireProtocol

from .conftest import COLORS


def identity(**changes) -> AppIdentity:
    from pathlib import Path

    values = {"name": "Acme", "slug": "acme", "storage_dir": Path("x"), "boot_colors": COLORS} | changes
    return AppIdentity(**values)


def test_the_slug_names_the_pages_native_object_and_its_ready_event():
    assert identity().native_global == "acmeNative"
    assert identity(slug="notes2").native_ready_event == "notes2nativeready"


@pytest.mark.parametrize("slug", ["", "Acme", "2acme", "my-app", "my app", "acme_"])
def test_a_slug_that_cannot_name_things_is_refused(slug):
    with pytest.raises(ValueError):
        identity(slug=slug)


def test_a_blank_name_is_refused():
    with pytest.raises(ValueError):
        identity(name="  ")


def test_the_shell_and_app_preferences_live_in_the_storage_folder(tmp_path):
    one = identity(storage_dir=tmp_path)
    assert one.shell_preferences_path == tmp_path / "shell.json"
    assert one.app_preferences_path == tmp_path / "preferences.json"


def test_the_default_wire_names_follow_the_slug():
    wire = WireProtocol.for_slug("acme")
    assert (wire.token_header, wire.token_cookie, wire.token_env) == ("x-acme-token", "acme_token", "ACME_TOKEN")
    assert wire.health_path == "/api/health"
