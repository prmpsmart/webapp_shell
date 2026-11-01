import sys

import pytest

from webapp_shell.messages import ShellMessages
from webapp_shell.webview2 import (
    DOWNLOAD_URL,
    NOT_INSTALLED,
    RUNTIME_LOCATIONS,
    RegistryLocation,
    Webview2Check,
)


def reader(versions: dict[RegistryLocation, str]):
    return lambda location: versions.get(location)


def test_only_windows_needs_the_runtime():
    assert not Webview2Check(platform="darwin", read_version=reader({})).is_missing()
    assert not Webview2Check(platform="linux", read_version=reader({})).is_missing()


def test_windows_without_a_listed_runtime_is_missing():
    assert Webview2Check(platform="win32", read_version=reader({})).is_missing()


def test_a_runtime_listed_in_any_of_the_three_places_is_enough():
    for location in RUNTIME_LOCATIONS:
        check = Webview2Check(platform="win32", read_version=reader({location: "120.0.2210.91"}))
        assert not check.is_missing()


def test_a_placeholder_version_does_not_count():
    versions = {location: NOT_INSTALLED for location in RUNTIME_LOCATIONS}
    assert Webview2Check(platform="win32", read_version=reader(versions)).is_missing()


def test_the_problem_is_a_sentence_with_the_name_and_the_download_page():
    sentence = Webview2Check(platform="win32", read_version=reader({})).problem("Acme Notes", ShellMessages())
    assert sentence is not None and "Acme Notes" in sentence and DOWNLOAD_URL in sentence


def test_nothing_is_said_when_the_runtime_is_there():
    check = Webview2Check(platform="win32", read_version=reader({RUNTIME_LOCATIONS[0]: "1.0"}))
    assert check.problem("Acme Notes", ShellMessages()) is None


@pytest.mark.skipif(sys.platform == "win32", reason="Windows has a registry to read")
def test_reading_the_registry_off_windows_finds_nothing():
    from webapp_shell.webview2 import read_registry_version

    assert read_registry_version(RUNTIME_LOCATIONS[0]) is None
