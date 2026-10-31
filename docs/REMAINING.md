# Remaining

Everything still open before `webapp-shell` is published on PyPI as a library people can use, in one place. Only what is still open: finished items are deleted (what was done is in `HANDOVER.md` and the git log). Last updated 31 October 2026.

Versions are `x.y` (decided 31 October 2026): 0.1, 0.2 … 1.0, each release counts as stable; no patch number.

At a glance: **B** code still to write, **C** the example site and the documentation, **D** checks that have never been run, **E** publishing, **F** Pixeval adopts it (not needed to publish), **G** small items.

## B. Code still to write

Decided 31 October 2026: the page talks only to the shell and the backend never does, as in Pixeval. `shell/pixeval_shell` is stable (it runs in Pixeval on Windows and macOS, and Linux is expected to pass), so the library ports it and does not re-prove it.

- [ ] **A ready WebSocket guard for Starlette** (the contract has `is_valid_connection` and the close code only).
- [ ] **The whole library typed, no guessing** (pyright strict is clean on `src/`; the untyped OS surfaces are marked in three files). Remaining: run pyright over `tests/` and `examples/` too, and add it to CI.
- [ ] **The public API listing** (`docs/API.md`, generated from the code): every class, function and signature, so the owner decides what stays public; then mark the rest private.
- [ ] **The words the shell shows** (splash, give-up message, check messages) available to the frontend for translation, and a document in `docs/` about it.
- [ ] **Errors a stranger will meet**, in plain words: missing `frontend/dist`, a backend that never answers its health path, a missing WebView2 on Windows (the first-run check reports it).

## C. The example site and the documentation

- [ ] **The rest of the documentation website** (`examples/site`; done: frame, Overview, Getting started, nine native-function pages, token and health, when the backend stops, a long task, For frontend developers, Security). Still to add: the shell's own splash and first-run check (a page with a demonstration).
- [ ] **Guides** (pages of the site, also Markdown in `docs/`; Getting started, For frontend developers and Security exist as pages, not yet as Markdown): the contract (exact names, token handover, health, shutdown); configuring identity and backend; native functions as one guide; freezing with PyInstaller (the freeze profile in Pixeval is the model); troubleshooting (Windows icon format, the pywebview API walk, console noise, WebView2).
- [ ] **Reference** generated from the config classes and docstrings.
- [ ] **Tests for the samples of the pages still to come** (the existing pages are covered: backend, launcher sample, build freshness, headless Qt run).
- [ ] **Static copy on GitHub Pages**, demo buttons marked "run this in the shell".

## D. Checks that have never been run

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
- [ ] `HANDOVER.md` and this file overlap; once the library is published, shrink the handover to history and keep this file as the list.
