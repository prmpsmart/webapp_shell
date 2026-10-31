# 0.1

The first version (not yet published). What it holds:

- **The shell as a library:** `run(config)` gives a program its command line; the backend is started, watched and restarted by the shell (`BackendProcess`, `BackendWatchdog`), with a splash and a first-run library check.
- **Config objects:** `AppIdentity`, `BackendSpec`, `WireProtocol`, `CliFlag` and `ShellConfig`; no program's name is built into the library.
- **Two windows:** pywebview (built in) and Qt (the `qt` extra).
- **The backend contract** (`webapp_shell.contract`): launch token, origin policy, launch arguments, and a Starlette `TokenGuard` (the `backend` extra).
- **Native functions:** the standard set (choose a file or folder, save as, show in the file manager, open a link, zoom, boot colours) and your own through `NativeFunction`, one envelope on both toolkits.
- **The page-side bridge:** `webapp-shell-bridge.js` with its `.d.ts`, copied into a frontend with `python -m webapp_shell bridge --out DIR`.
- **Examples:** `examples/minimal` and the documentation site `examples/site`.
