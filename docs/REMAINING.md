# Remaining

Everything still open before and just after `webapp-shell` `0.1` is on PyPI, in one place. Only what is still open: finished items are deleted (what was done is in the git log and `CHANGE_LOG.md`). Last updated 1 November 2026.

Versions are `x.y` (decided 31 October 2026): 0.1, 0.2 … 1.0, each release counts as stable; no patch number.

Policy (decided 31 October 2026): `shell/pixeval_shell` is stable (it has run in Pixeval on Windows and macOS, frozen builds included), so the library ports it and does not re-prove it.

At a glance: **A** publishing, **B** freezing, **C** the example site and the documentation, **D** Pixeval adopts it (not needed to publish), **E** small items.

## A. Publishing

CI is green on Ubuntu, macOS and Windows; the repository, Pages and the trusted publishers on PyPI and TestPyPI are set up.

- [ ] **Dry run on TestPyPI:** run the Release workflow by hand (it publishes to TestPyPI only), install from there in a clean environment (`--extra-index-url https://pypi.org/simple/`) and run the example.
- [ ] **Release `0.1`:** tag `v0.1`, which publishes to PyPI; check `pip install webapp-shell` in a clean environment.
- [ ] **Badges** in `README.md` (CI, PyPI version, Python version, licence) once the package is on PyPI; a short `CONTRIBUTING.md` if wanted.

## B. Freezing

Pixeval's frozen build (PyInstaller, `packaging/` in the Pixeval repository) is confirmed on Windows, so what is left is moving it into the library, not proving it again.

- [ ] **A ready PyInstaller spec** in the library, translated from Pixeval's `packaging/` (the spec, the freeze profiles, the build script and the checks that read the finished build), so `docs/FREEZING.md` can point to it instead of to Pixeval.
- [ ] **A frozen example:** `examples/minimal` built with it, as the proof that the spec is generic (the `--run-backend` path, the library check, the data files).

## C. The example site and the documentation

- [ ] **The rest of the documentation website** (`examples/site`; done: frame, Overview, Getting started, nine native-function pages, token and health, when the backend stops, a long task, For frontend developers, Security). Still to add: the shell's own splash and first-run check (a page with a demonstration), and the Reveal page in a plain browser (it needs the shell; it only says so).
- [ ] **Guides as site pages:** the Markdown guides exist in `docs/` (contract, configuration, native functions, freezing, translating, troubleshooting); show them in the site.
- [ ] **Tests for the samples of the pages still to come** (the existing pages are covered: backend, launcher sample, build freshness, headless Qt run).

## D. Pixeval adopts it (not needed to publish)

Done: Pixeval's `shell/` is only its `ShellConfig` and its picture-format check, the window runs on the library, the frontend uses the library's bridge file, the library is installed into the venv with `pip install -e` and its public names are imported from `webapp_shell`.

- [ ] **The backend's own `protocol.py`, `tokens.py` and `security.py`** are replaced by the library's contract (`webapp_shell.contract`).
- [ ] **Pin `webapp-shell` in `requirements.lock`** once it is on PyPI, and drop the editable install.
- [ ] **Run Pixeval's PyInstaller build** with the library in place of its own shell modules.
- [ ] **Try the native pickers** from Pixeval's `#/bridge` page in the real shell.
- [ ] **Pixeval's docs** (`02-architecture.md`, `05-delivery.md`) say where the shell now lives.

## E. Small items

- [ ] The WebView2 message box (`webapp_shell.webview2`) has never been seen on a real Windows machine; the registry read is covered (CI on Windows found version 156).
