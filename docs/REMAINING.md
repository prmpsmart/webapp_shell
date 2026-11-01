# Remaining

Everything still open before and just after `webapp-shell` `0.1` is on PyPI, in one place. Only what is still open: finished items are deleted (what was done is in the git log and `CHANGE_LOG.md`). Last updated 1 November 2026.

Versions are `x.y` (decided 31 October 2026): 0.1, 0.2 … 1.0, each release counts as stable; no patch number.

Policy (decided 31 October 2026): `shell/pixeval_shell` is stable (it has run in Pixeval on Windows and macOS, frozen builds included), so the library ports it and does not re-prove it.

At a glance: **A** publishing, **B** Pixeval adopts it (not needed to publish), **C** small items.

## A. Publishing

CI is green on Ubuntu, macOS and Windows; the repository, Pages and the trusted publishers on PyPI and TestPyPI are set up.

- [ ] **Dry run on TestPyPI:** run the Release workflow by hand (it publishes to TestPyPI only), install from there in a clean environment (`--extra-index-url https://pypi.org/simple/`) and run the example.
- [ ] **Release `0.1`:** tag `v0.1`, which publishes to PyPI; check `pip install webapp-shell` in a clean environment.

## B. Pixeval adopts it (not needed to publish)

Done: Pixeval's `shell/` is only its `ShellConfig` and its picture-format check, the window runs on the library, the frontend uses the library's bridge file, the library is installed into the venv with `pip install -e` and its public names are imported from `webapp_shell`.

- [ ] **The backend's own `protocol.py`, `tokens.py` and `security.py`** are replaced by the library's contract (`webapp_shell.contract`).
- [ ] **Pin `webapp-shell` in `requirements.lock`** once it is on PyPI, and drop the editable install.
- [ ] **Pixeval's `packaging/`** uses `webapp_shell.freezing` (a `FreezePlan` instead of its own entry file, spec and verifier; it keeps its data folders, its `collect_all` list and its required files) and its PyInstaller build is run once with it.
- [ ] **Try the native pickers** from Pixeval's `#/bridge` page in the real shell.
- [ ] **Pixeval's docs** (`02-architecture.md`, `05-delivery.md`) say where the shell now lives.

## C. Small items

- [ ] The WebView2 message box (`webapp_shell.webview2`) has never been seen on a real Windows machine; the registry read is covered (CI on Windows found version 156).
