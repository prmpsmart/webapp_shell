"""The opening screen: the splash and the web view start in the colours of the user's last theme."""

import json

from webapp_shell.preferences import BootColors, ShellPreferences
from webapp_shell.settings import Settings
from webapp_shell.splash import HERO_GRADIENT, SplashPage

from .conftest import COLORS

GOOD = BootColors("#0b1630", "#2d4bd8", "#7a5af8")


def test_splash_paints_the_gradient_and_no_dark_variant():
    page = SplashPage("Acme Notes", None, COLORS).loading()
    assert HERO_GRADIENT.format(base=COLORS.base, glow_a=COLORS.glow_a, glow_b=COLORS.glow_b) in page
    assert "prefers-color-scheme" not in page


def test_splash_and_error_pages_carry_the_program_name():
    assert "<title>Acme Notes</title>" in SplashPage("Acme Notes", None, COLORS).loading()
    assert "&lt;i&gt;" in SplashPage("<i>", None, COLORS).loading()


def test_preferences_round_trip_and_survive_a_restart(tmp_path, config):
    path = tmp_path / "shell.json"
    assert ShellPreferences(path).save_boot_colors(GOOD)
    assert ShellPreferences(path).boot_colors == GOOD
    assert Settings.of(config, ShellPreferences(path)).boot_colors == GOOD


def test_preferences_reject_anything_that_is_not_a_hex_colour(tmp_path):
    path = tmp_path / "shell.json"
    prefs = ShellPreferences(path)
    for bad in (
        ("red", "#000000", "#000000"),
        ("#000000", "#12345", "#000000"),
        ("#000000", "#000000", "#11111;} body{display:none"),
        ("#000000", None, "#000000"),
        ("#000000", 5, "#000000"),
        (["#000000"], "#000000", "#000000"),
    ):
        assert BootColors.from_values(*bad) is None
    assert BootColors.from_values("#0B1630", "#2d4bd8", "#7a5af8") == BootColors("#0B1630", "#2d4bd8", "#7a5af8")
    assert not prefs.save_boot_colors(BootColors("x", "y", "z"))
    assert not path.exists()  # nothing was written


def test_a_damaged_preferences_file_is_ignored(tmp_path):
    path = tmp_path / "shell.json"
    path.write_text("{ broken")
    assert ShellPreferences(path).boot_colors is None
    path.write_text(
        json.dumps({"bootColors": {"base": "javascript:alert(1)", "glow_a": "#000000", "glow_b": "#000000"}})
    )
    assert ShellPreferences(path).boot_colors is None


def test_in_memory_preferences_never_touch_disk():
    prefs = ShellPreferences(None)
    assert prefs.save_boot_colors(GOOD)
    assert prefs.boot_colors is not None


def test_the_splash_is_held_until_its_minimum_time_has_passed(settings):
    from dataclasses import replace

    from webapp_shell.shell import Shell

    class Dummy(Shell):
        def event_loop(self, boot): ...
        def navigate(self, url): ...
        def show_page(self, html): ...
        def set_title(self, title): ...
        def quit(self): ...
        def on_navigated(self): ...

    slept = []
    shell = Dummy(replace(settings, config=replace(settings.config, splash_seconds=5.0)), backend=None)
    shell.hold_splash(started=100.0, now=lambda: 101.5, sleep=slept.append)  # 1.5 s already passed
    assert slept == [3.5]
    shell.hold_splash(started=100.0, now=lambda: 106.0, sleep=slept.append)  # the engine took longer than that
    assert slept == [3.5]
    shell = Dummy(replace(settings, config=replace(settings.config, splash_seconds=0)), backend=None)
    shell.hold_splash(started=100.0, now=lambda: 100.0, sleep=slept.append)
    assert slept == [3.5]


def test_headless_checks_do_not_wait_for_the_splash(config):
    assert Settings.of(config, ShellPreferences(None), splash_seconds=0.0).splash_seconds == 0
    assert Settings.of(config, ShellPreferences(None)).splash_seconds == config.splash_seconds


def test_without_a_remembered_theme_the_identitys_colours_open_the_window(config):
    assert Settings.of(config, ShellPreferences(None)).boot_colors == COLORS
    assert Settings.of(config).background_color == COLORS.base
