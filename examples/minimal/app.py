"""Acme Notes, the smallest program that uses webapp-shell.

python app.py            # opens the window (pywebview)
python app.py qt         # the same page in Qt (pip install "webapp-shell[qt]")
python app.py --smoke    # headless self-check: load the page, print what it rendered, exit
"""

from pathlib import Path

from acme_backend.spec import BACKEND, HERE
from webapp_shell import AppIdentity, BootColors, ShellConfig, run

config = ShellConfig(
    identity=AppIdentity(
        name="Acme Notes",
        slug="acme",
        storage_dir=Path.home() / ".acme-notes",
        boot_colors=BootColors(base="#102030", glow_a="#204060", glow_b="#4060a0"),
    ),
    backend=BACKEND,
    source_root=HERE,  # holds frontend/dist, the compiled frontend
)

if __name__ == "__main__":
    raise SystemExit(run(config))
