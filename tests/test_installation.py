import sys

from webapp_shell.installation import Installation, ensure_standard_streams


def test_from_the_source_tree_the_backend_is_a_module_and_the_packages_are_added_by_hand(config, tmp_path):
    here = Installation(tmp_path, frozen=False)
    assert here.backend_command(config.backend) == [sys.executable, "-m", "fake_backend"]
    assert here.root == tmp_path
    assert here.package_dirs(config.backend) == config.backend.package_dirs


def test_a_frozen_program_starts_its_backend_by_running_itself(config, tmp_path):
    frozen = Installation(tmp_path, frozen=True, bundle=tmp_path / "bundle")
    assert frozen.backend_command(config.backend) == [sys.executable, "--run-backend"]
    assert frozen.root == tmp_path / "bundle"
    assert frozen.package_dirs(config.backend) == ()


def test_a_windowed_program_gets_streams_that_discard_text(monkeypatch):
    monkeypatch.setattr(sys, "stdout", None)
    monkeypatch.setattr(sys, "stderr", None)
    ensure_standard_streams()
    print("nobody reads this")
    assert sys.stdout.isatty() is False and sys.stderr is not None
