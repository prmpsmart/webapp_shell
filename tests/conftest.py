"""A made-up project, "Acme Notes", that plugs into the library the way a real one does."""

from pathlib import Path

import pytest

from webapp_shell import AppIdentity, BackendSpec, BootColors, CliFlag, ShellConfig, WireProtocol
from webapp_shell.installation import Installation
from webapp_shell.settings import Settings

HERE = Path(__file__).resolve().parent
COLORS = BootColors(base="#102030", glow_a="#204060", glow_b="#4060a0")
SANDBOX = CliFlag("--sandbox", "work on a copy", ("--sandbox",))


@pytest.fixture
def source_root(tmp_path: Path) -> Path:
    """A project folder with a compiled frontend in it."""
    dist = tmp_path / "frontend" / "dist"
    dist.mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><title>Acme</title>")
    return tmp_path


@pytest.fixture
def config(source_root: Path) -> ShellConfig:
    identity = AppIdentity(
        name="Acme Notes",
        slug="acme",
        storage_dir=source_root / "home",
        boot_colors=COLORS,
        icon_png=source_root / "frontend" / "dist" / "icon.png",
        icon_ico=source_root / "frontend" / "dist" / "icon.ico",
    )
    backend = BackendSpec(
        module="fake_backend",
        wire=WireProtocol.for_slug("acme"),
        arguments=("--always",),
        source_only_arguments=("--developer",),
        flags=(SANDBOX,),
        package_dirs=(HERE,),
    )
    return ShellConfig(identity=identity, backend=backend, source_root=source_root, startup_timeout=15.0)


@pytest.fixture
def settings(config: ShellConfig) -> Settings:
    return Settings.of(config, installation=Installation(config.source_root, frozen=False))
