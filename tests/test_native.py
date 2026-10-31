from pathlib import Path
from typing import ClassVar

from webapp_shell.native.filters import FileFilter
from webapp_shell.native.os_actions import OsActions
from webapp_shell.splash import SplashPage

from .conftest import COLORS


class TestFileFilter:
    RAW: ClassVar[list[dict]] = [
        {"name": "Excel", "extensions": ["xlsx", "*.xls"]},
        {"name": "", "extensions": ["x"]},
        {"name": "None"},
    ]

    def test_parse_drops_incomplete_entries_and_strips_wildcards(self):
        assert FileFilter.parse_all(self.RAW) == [FileFilter("Excel", ("xlsx", "xls"))]

    def test_parse_handles_nothing(self):
        assert FileFilter.parse_all(None) == []

    def test_toolkit_formats(self):
        f = FileFilter("Excel", ("xlsx", "xls"))
        assert f.to_qt() == "Excel (*.xlsx *.xls)"
        assert f.to_webview() == "Excel (*.xlsx;*.xls)"


class TestOsActions:
    def test_refuses_dangerous_url_schemes(self):
        actions = OsActions()
        for url in ("file:///etc/passwd", "javascript:alert(1)", "ftp://host/x", "not a url"):
            assert actions.open_url(url) is False

    def test_reveal_refuses_missing_path(self, tmp_path: Path):
        assert OsActions().reveal(str(tmp_path / "missing")) is False


class TestSplashPage:
    def test_error_message_is_escaped(self):
        assert "&lt;b&gt;" in SplashPage("Acme", None, COLORS).error("<b>boom</b>")

    def test_icon_is_embedded_when_present(self, tmp_path: Path):
        icon = tmp_path / "icon.png"
        icon.write_bytes(b"\x89PNG")
        assert "data:image/png;base64," in SplashPage("Acme", icon, COLORS).loading()

    def test_no_icon_still_renders(self):
        assert "spin" in SplashPage("Acme", None, COLORS).loading()


def test_settings_find_the_icon_the_identity_names(settings):
    assert settings.icon_png is None  # named, but not there yet
    settings.identity.icon_png.write_bytes(b"x")
    assert settings.icon_png == settings.identity.icon_png


def test_the_window_icon_is_an_ico_on_windows_and_a_png_elsewhere(settings, monkeypatch):
    """pywebview on Windows builds the icon with `System.Drawing.Icon`, which fails on a PNG."""
    settings.identity.icon_png.write_bytes(b"x")
    settings.identity.icon_ico.write_bytes(b"x")
    monkeypatch.setattr("sys.platform", "win32")
    assert settings.window_icon == settings.identity.icon_ico
    monkeypatch.setattr("sys.platform", "linux")
    assert settings.window_icon == settings.identity.icon_png


def test_shell_kinds_match_the_registry():
    from webapp_shell import registry
    from webapp_shell.enums import ShellKind

    assert set(registry.kinds()) == set(ShellKind)


def test_zoom_factors_are_limited_and_only_numbers_count():
    from webapp_shell.native.zoom import MAX_ZOOM, MIN_ZOOM, clamp

    assert clamp(1.25) == 1.25 and clamp(1) == 1.0
    assert clamp(99) == MAX_ZOOM and clamp(0.01) == MIN_ZOOM
    assert clamp("1.2") is None and clamp(None) is None and clamp(True) is None
