# webapp-shell

A desktop window for a web app made of a **Python backend** and a **compiled frontend**. Your project describes itself
in one config object; the library starts the backend, waits until it is healthy, opens the frontend in a native window
(pywebview, or Qt on request) and gives the page a small set of native functions (file and folder dialogs, reveal in the
file manager, open a link, zoom).

> Status: 0.1.0 in preparation, not published. See `docs/HANDOVER.md`.

```python
from pathlib import Path

from webapp_shell import AppIdentity, BackendSpec, BootColors, ShellConfig, WireProtocol, run

ROOT = Path(__file__).resolve().parent

config = ShellConfig(
    identity=AppIdentity(
        name="Acme Notes",
        slug="acme",
        storage_dir=Path.home() / ".acme",
        boot_colors=BootColors(base="#102030", glow_a="#204060", glow_b="#4060a0"),
    ),
    backend=BackendSpec(module="acme_backend", wire=WireProtocol.for_slug("acme"), package_dirs=(ROOT / "backend",)),
    source_root=ROOT,  # holds frontend/dist, the compiled frontend
)

if __name__ == "__main__":
    raise SystemExit(run(config))
```

The backend reads the same contract with the library's helpers (Starlette or FastAPI):

```python
parser = argparse.ArgumentParser()
add_launch_arguments(parser, config.backend)          # --port, --frontend, --preferences-file, --token
launch = read_launch_arguments(parser, parser.parse_args(), config.backend.wire)
app.add_middleware(TokenGuard, validator=TokenValidator(launch.token, wire), wire=wire)
```

Install: `pip install webapp-shell` (pywebview is included); `pip install "webapp-shell[qt]"` adds Qt, and
`pip install "webapp-shell[backend]"` adds Starlette for the token guard.

On Windows the pywebview window needs the WebView2 runtime (present on Windows 11); `pythonnet` is installed by pywebview.

The design is in `docs/` (the decisions are in the Pixeval repository, `rebranding-docs/12-webapp-shell.md`).
