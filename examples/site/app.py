"""The webapp_shell documentation site, opened by webapp_shell itself.

python app.py            # opens the window (pywebview)
python app.py qt         # the same page in Qt (pip install "webapp-shell[qt]")
python app.py --smoke    # headless self-check: load the page, print what it rendered, exit
"""

from pathlib import Path

from docs_backend.spec import BACKEND, HERE
from webapp_shell import AppIdentity, BootColors, ShellConfig, run

config = ShellConfig(
    identity=AppIdentity(
        name="webapp_shell",
        slug="docs",
        storage_dir=Path.home() / ".webapp-shell-docs",
        boot_colors=BootColors(base="#0f1420", glow_a="#1d2b4a", glow_b="#3b4f8a"),
    ),
    backend=BACKEND,
    source_root=HERE,  # holds frontend/dist, the compiled frontend
)

if __name__ == "__main__":
    raise SystemExit(run(config))
