# 0.1

The first version (not yet published). What it holds:

- **The shell as a library:** `run(config)` gives a program its command line; the backend is started, watched and restarted by the shell (`BackendProcess`, `BackendWatchdog`), with a splash and a first-run library check.
- **Config objects:** `AppIdentity`, `BackendSpec`, `WireProtocol`, `CliFlag` and `ShellConfig`; no program's name is built into the library.
- **Two windows:** pywebview (built in) and Qt (the `qt` extra).
- **The backend contract** (`webapp_shell.contract`): launch token, origin policy, launch arguments, and a Starlette `TokenGuard` (the `backend` extra).
- **WebSocket guard:** `WebSocketGuard` (Starlette) applies the same token and origin rules to a socket as `TokenGuard` does to a request, closing a refused one with code 4401.
- **Typed everywhere:** `pyright` strict passes on the whole library (`py.typed` ships); everything that crosses between the page and Python is a `JsonValue`.
- **Typed native arguments:** a function declares its arguments as a dataclass (`NativeFunction(name, Arguments, handler)`); the page's values are checked against the field types before the handler runs and nothing is converted silently.
- **Native functions:** the standard set (choose a file or folder, save as, show in the file manager, open a link, zoom, boot colours) and your own through `NativeFunction`, one envelope on both toolkits.
- **The page-side bridge:** `webapp-shell-bridge.js` with its `.d.ts`, copied into a frontend with `python -m webapp_shell bridge --out DIR`.
- **Documentation site:** fifteen pages with live demonstrations and Frontend/Backend/Shell code tabs, a page for frontend developers and a security page whose claims are checked by tests.
- **Examples:** `examples/minimal` and the documentation site `examples/site`.
- `ShellMessages` / `MessageKey`: the shell's own sentences as one catalogue a project can translate (`ShellConfig.messages`); `python -m webapp_shell messages` prints it as JSON for a frontend; `docs/TRANSLATING.md`.
- `docs/API.md`, generated from the source by `tools/api_listing.py` (a test keeps it current), lists only the public API: the names in the `__all__` of `webapp_shell`, `webapp_shell.contract` and `webapp_shell.contract.guard`. `Installation`, `FileFilter`, `standard_functions` and `build_parser` are exported for freezing and tuning; the guide samples and the examples are tested to import nothing else.
- **Freezing:** `webapp_shell.freezing` (`FreezePlan`, `DataFolder`) and `python -m webapp_shell freeze PLAN [qt] [webview]` freeze a program with PyInstaller (`webapp-shell[freeze]`): the library writes the entry file and the spec, leaves the other shell's libraries out, and checks the folder (required files, nothing of the other shell, the frozen program's own `--check-libraries`). `examples/minimal/freeze_plan.py` is a plan; the frozen Qt build was run headless (`--smoke`) and the frozen `--run-backend` path answered with the token guard on. The zoom limits moved to `native/zoom_range.py` so a Qt-only build does not reach pywebview.
- Guides: contract, configuration, native functions, freezing, troubleshooting (their Python samples are checked by a test).
- Pyright strict also covers the examples; CI (3 systems, Python 3.13), a Pages workflow and a trusted-publishing release workflow (TestPyPI, then PyPI on a tag).
- Package metadata (classifiers, URLs, keywords); the wheel and sdist pass `twine check`.
- Name checked free on PyPI on 1 November 2026. Checked: Starlette 0.40 and 1.10, pywebview 6.2 and 6.2.1; a clean install of the built wheel runs the example.
- Plainer start-up errors: a backend that stops while starting reports its exit code; one that never answers names the health path and the seconds waited.
- On Windows, a missing WebView2 runtime is found before any window opens and reported in a message box with the download page (`webapp_shell.webview2`).
- The example site colours every code block (Python, TypeScript, shell) with highlight.js; the README links to the documentation site.
- Example site: every code card has a Copy button; in a plain browser the demos use the browser's own features (file, folder and save pickers, zoom, theme colour, new-tab links), with a note that a browser never gives a path on the disk. Only "Show in the file manager" needs the shell.
