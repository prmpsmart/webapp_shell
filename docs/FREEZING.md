# Freezing with PyInstaller

A frozen program is one folder with one executable. It has no `python -m`, so it starts its backend by running
**itself** with `--run-backend`; the library does this (`Installation.backend_command`). You describe your program in a
`FreezePlan`; the library writes the entry file, the PyInstaller spec, and checks the result.

```sh
pip install "webapp-shell[freeze]"
```

## The plan

```python
from pathlib import Path

from webapp_shell.freezing import DataFolder, FreezePlan

HERE = Path(__file__).resolve().parent

PLAN = FreezePlan(
    product="AcmeNotes",  # the name of the folder and of the executable
    config="app:config",  # module:attribute, the ShellConfig your launcher builds (or a function returning one)
    packages=("acme_backend", "uvicorn"),  # every submodule is collected: yours, and any that load by name
    data_folders=(DataFolder(HERE / "frontend" / "dist", "frontend/dist"),),  # the compiled frontend
    required=("frontend/dist/index.html",),  # must be in the finished build
)
```

Optional fields: `collect_all` (third-party packages with data files or native libraries, such as `reportlab`),
`runtime_hooks` (scripts that run before anything else), `excludes` (more libraries to leave out) and `icon` (`.ico`,
used for the Windows executable).

## The build

```sh
python -m webapp_shell freeze acme_freeze:PLAN --path . qt webview
```

`--path` is the folder the plan's module is imported from (repeat it for more folders). Each shell is built into
`dist/<shell>/<product>/` (`--output` and `--work` change the folders). Name `qt`, `webview` or both; with none, both are
built. PyInstaller does not cross-compile: build on the system you ship for.

| Shell     | The build carries | The build must not contain             |
| --------- | ----------------- | -------------------------------------- |
| `qt`      | Qt WebEngine      | pywebview, pythonnet, clr_loader       |
| `webview` | pywebview         | PySide6, shiboken6, PyQt5, PyQt6, qtpy |

After freezing, the command checks the folder and fails when:

- a library of the other shell is in it;
- a file in `required` or the executable is missing;
- the frozen program's own `--check-libraries` reports a problem: it imports every name in
  `ShellConfig.required_libraries` (and runs your `library_checks`), so the build finds a missing library, not the
  person using the program.

## What the frozen program does

- It opens its window on the shell it was built for (`program` takes no shell argument), and `--smoke` is a headless
  check of the page.
- It starts its backend by running itself with `--run-backend`, which calls `<module>.__main__.main(argv)`; the
  backend package must therefore be in `packages`.
- The compiled frontend is found at `sys._MEIPASS/frontend/dist`, the folder named by `BackendSpec.frontend_dist`;
  `data_folders` must put it there.
- A windowed build has no console. `ensure_standard_streams()` (called by `run`) gives `sys.stdout` and `sys.stderr`
  a stream that discards text, because libraries ask a stream whether it is a terminal.
- On Windows the pywebview build needs the **WebView2 runtime**; the program says so in a message box when it is
  missing. The Qt build carries its own browser and needs nothing.

`examples/minimal/freeze_plan.py` is a complete plan; `python -m pytest -m freeze` freezes it and runs the checks.
