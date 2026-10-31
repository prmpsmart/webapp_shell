# Remaining

Everything still open before `webapp-shell` is published on PyPI as a library people can use, in one place. Only what is still open: finished items are deleted (what was done is in `HANDOVER.md` and the git log). Last updated 31 October 2026.

Versions are `x.y` (decided 31 October 2026): 0.1, 0.2 … 1.0, each release counts as stable; no patch number.

At a glance: **B** code still to write, **C** the example site and the documentation, **D** checks that have never been run, **E** publishing, **F** Pixeval adopts it (not needed to publish), **G** small items.

## B. Code still to write

- [ ] **Confirm the rule “the page talks to the shell, the backend never does”.** It is how Pixeval works and how the guides will explain a feature (page → shell → path → page → backend); the owner confirms it holds for the library too, or asks for a backend-to-shell channel.
- [ ] **WebSocket path.** The library has `is_valid_connection` and the close code only; decide whether to offer a ready `WebSocket` guard for Starlette too.
- [ ] **Own-function arguments and results are JSON only** (numbers, text, lists, objects, null). Say so in the guide; decide whether to offer typed argument parsing for project functions.
- [ ] **Public API review.** Decide what `webapp_shell.__init__` exports for good; mark everything else private. Add type hints check (`py.typed`).
- [ ] **Errors a stranger will meet**, in plain words: missing `frontend/dist`, a backend that never answers its health path, a missing WebView2 on Windows (the first-run check reports it).

## C. The example site and the documentation

- [ ] **The rest of the documentation website** (`examples/site`; done: frame, Overview, Getting started, nine native-function pages, token and health, when the backend stops). Still to add, each with a live demonstration and the three snippets (frontend, backend, shell): a running backend job (a long task with progress), the shell's own splash and first-run check.
- [ ] **Guides** (pages of the site, also Markdown in `docs/`): getting started; the contract (exact names, token handover, health, shutdown); configuring identity and backend; native functions; freezing with PyInstaller (the freeze profile in Pixeval is the model); troubleshooting (Windows icon format, the pywebview API walk, console noise, WebView2).
- [ ] **Reference** generated from the config classes and docstrings.
- [ ] **A page for frontend developers:** what the page may assume (the token cookie, the bridge object) and nothing else.
- [ ] **A security page:** loopback only, the per-launch token, the origin check, what the page may and may not ask the shell.
- [ ] **Tests for the samples of the pages still to come** (the existing pages are covered: backend, launcher sample, build freshness, headless Qt run).
- [ ] **Static copy on GitHub Pages**, demo buttons marked "run this in the shell".

## D. Checks that have never been run

- [ ] **A real window from the library on macOS:** pywebview (`python examples/minimal/app.py --smoke`, which shows a window for a few seconds) and a visible Qt window; click “Choose a file” and check the path reaches the backend.
- [ ] **Windows:** pywebview with WebView2 and `pythonnet`; the `.ico` window icon; the native bridge without the `[pywebview] Error while processing window.native` flood. Never run, in Pixeval either.
- [ ] **Linux** (GTK/Qt WebKit): at least a smoke run.
- [ ] **Starlette versions:** tested on 0.46.2 only; try the minimum in `pyproject.toml` (0.40) and a current one. Same for pywebview (`>=6.2`).
- [ ] **A frozen program** (PyInstaller) built with the library: the `--run-backend` path, the library check, the data files.
- [ ] **Clean install of the built wheel** into an empty environment; run the example.

## E. Publishing

- [ ] **Recheck the name.** `webapp-shell` and `webapp_shell` were free on PyPI on 28 October 2026.
- [ ] **Metadata in `pyproject.toml`:** URLs (repository, documentation `prmpsmart.github.io/webapp_shell`, issues), classifiers (Python 3.13, OS, framework), keywords, a final description. 
- [ ] **`README.md` polish** (badges only when the CI exists), a short `CONTRIBUTING.md` if wanted.
- [ ] **GitHub repository** `prmpsmart/webapp_shell` (public), push the first commit.
- [ ] **CI (GitHub Actions):** `pytest` and `ruff` on Linux, macOS and Windows for each push, on Python 3.13.
- [ ] **Build and check:** `python -m build`, `twine check dist/*`; the wheel holds `webapp_shell` and nothing else; the extras install.
- [ ] **Accounts:** PyPI and TestPyPI, with two-factor authentication.
- [ ] **Trusted publishing:** a GitHub Actions workflow that publishes on a version tag, so no token is stored.
- [ ] **Dry run on TestPyPI**, install from it, run the example.
- [ ] **Release `0.1`:** tag `v0.1`, publish to PyPI, check `pip install webapp-shell` in a clean environment.

## F. Pixeval adopts it (after publishing, or from the sibling folder before)

- [ ] **Part 4:** replace Pixeval's `shell/` and the backend's `protocol.py`, `tokens.py` and `security.py` with the package; build Pixeval's `ShellConfig` in `launch.py`; adapt Pixeval's tests (the title says `backend` instead of `engine`; `--sandbox` becomes a `CliFlag`, `--developer-tools` a source-only argument).
- [ ] **Keep in Pixeval:** the freeze profiles and their tests, the PIL picture-format check, the boot-colour tests tied to its frontend tokens.
- [ ] **Pixeval's frontend uses the library's bridge file** instead of its own `bridge/`.
- [ ] **Lock file and packaging:** Pixeval's `requirements.lock` pins `webapp-shell`; the PyInstaller builds still pass.
- [ ] **Update Pixeval's docs:** `rebranding-docs/12-webapp-shell.md` (the Pixeval repository's copy says nothing is built; point it to this repository), `02-architecture.md`, `05-delivery.md`, `shell/README.md`.

## G. Small items

- [ ] The splash page text is English only ("Close {name} and open it again" is the watchdog message); decide whether the library offers a way to translate its few messages.
- [ ] Zoom for Windows and Linux is unit-tested, never run.
- [ ] `HANDOVER.md` and this file overlap; once the library is published, shrink the handover to history and keep this file as the list.
