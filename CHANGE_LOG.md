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
