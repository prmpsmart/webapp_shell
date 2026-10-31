# Remaining

Everything still open before `webapp-shell` is published on PyPI as a library people can use, in one place. `[ ]` is open; `[x]` is done. Last updated 31 October 2026. Parts 1, 2 and 3 are done (see `HANDOVER.md`).

At a glance: **A** decisions for the owner, **B** code still to write, **C** the example site and the documentation, **D** checks that have never been run, **E** publishing, **F** Pixeval adopts it (not needed to publish), **G** small items.

## A. Decisions for the owner

- [x] **Licence: MIT** (decided 31 October 2026). `LICENSE` added (copyright holder “Miracle Apata (prmpsmart)”; prmpsmart is the handle, used for the GitHub account, the repository and the docs address); `pyproject.toml` has `license = "MIT"`.
- [x] **Page-side bridge: one `.js` file** (decided 31 October 2026), shipped inside the Python wheel (an ES module with a `.d.ts` beside it); the frontend copies it. No npm package. Light, and the stack stays Python-only; npm can be added later without breaking anyone.
- [x] **Python 3.13 and above** (decided 31 October 2026). `requires-python = ">=3.13"`, ruff targets 3.13, CI tests 3.13 (and later ones as they appear).
- [ ] **Version policy (still open).** `0.x` while the API may still change; when it becomes `1.0`.
- [x] **Documentation address: `prmpsmart.github.io/webapp_shell`** (decided 31 October 2026). Put it in the project URLs and the README.

## B. Code still to write

- [x] **Part 3: the native-method registry** (31 October 2026). `NativeFunction` / `NativeRegistry`: a project adds its own functions through `ShellConfig.native_functions`; one envelope (`{ok, value}` or `{ok, error}`) on both shells; the standard set is written once against a `NativeWindow`; 125 tests.
- [x] **The page-side bridge client** (31 October 2026): `bridge/webapp-shell-bridge.js` + `.d.ts` inside the wheel, `python -m webapp_shell bridge --out DIR` copies them. Tested under Node (both shells' objects, late announcement, plain-browser fallbacks, errors); a test keeps its method list equal to `NativeMethod`. Not yet tried in a real page.
- [ ] **Confirm the rule “the page talks to the shell, the backend never does”.** It is how Pixeval works and how the guides will explain a feature (page → shell → path → page → backend); the owner confirms it holds for the library too, or asks for a backend-to-shell channel.
- [ ] **WebSocket path.** The library has `is_valid_connection` and the close code only; decide whether to offer a ready `WebSocket` guard for Starlette too.
- [ ] **Own-function arguments and results are JSON only** (numbers, text, lists, objects, null). Say so in the guide; decide whether to offer typed argument parsing for project functions.
- [ ] **Public API review.** Decide what `webapp_shell.__init__` exports for good; mark everything else private. Add type hints check (`py.typed`).
- [ ] **Errors a stranger will meet**, in plain words: missing `frontend/dist`, a backend that never answers its health path, a missing WebView2 on Windows (the first-run check reports it).

## C. The example site and the documentation

- [ ] **`examples/`: a minimal app** (the README example, runnable): a small Python backend and a one-page frontend.
- [ ] **The documentation website** as the example: a modern docs look (sidebar, search, code samples, light and dark), opened by the library's own shell, a live demonstration of every capability: choose a file or folder, save as, reveal, open a link, zoom, boot colours, token handover and health, a running backend job, the backend stopping.
- [ ] **Three snippets per feature page:** frontend, backend and shell (`12-webapp-shell.md` of the Pixeval repository, section 8).
- [ ] **Committed `dist` of that frontend**, so running the example needs only Python.
- [ ] **Guides** (pages of the site, also Markdown in `docs/`): getting started; the contract (exact names, token handover, health, shutdown); configuring identity and backend; native functions; freezing with PyInstaller (the freeze profile in Pixeval is the model); troubleshooting (Windows icon format, the pywebview API walk, console noise, WebView2).
- [ ] **Reference** generated from the config classes and docstrings.
- [ ] **A page for frontend developers:** what the page may assume (the token cookie, the bridge object) and nothing else.
- [ ] **A security page:** loopback only, the per-launch token, the origin check, what the page may and may not ask the shell.
- [ ] **Tests that run the examples and the code samples**, so the docs cannot go stale.
- [ ] **Static copy on GitHub Pages**, demo buttons marked "run this in the shell".

## D. Checks that have never been run

- [ ] **A real window from the library on macOS:** pywebview, then Qt; `--smoke` too. (Same code as Pixeval's shell, but never run from here.)
- [ ] **Windows:** pywebview with WebView2 and `pythonnet`; the `.ico` window icon; the native bridge without the `[pywebview] Error while processing window.native` flood. Never run, in Pixeval either.
- [ ] **Linux** (GTK/Qt WebKit): at least a smoke run.
- [ ] **Starlette versions:** tested on 0.46.2 only; try the minimum in `pyproject.toml` (0.40) and a current one. Same for pywebview (`>=6.2`).
- [ ] **A frozen program** (PyInstaller) built with the library: the `--run-backend` path, the library check, the data files.
- [x] The wheel builds with `hatchling` and holds the bridge files, `__main__` and the licence (checked once, 31 October 2026); repeat in CI.
- [ ] **Clean install of the built wheel** into an empty environment; run the example.

## E. Publishing

- [ ] **Recheck the name.** `webapp-shell` and `webapp_shell` were free on PyPI on 28 October 2026.
- [ ] **Metadata in `pyproject.toml`:** URLs (repository, documentation `prmpsmart.github.io/webapp_shell`, issues), classifiers (Python 3.13, OS, framework), keywords, a final description. (`license` is done.)
- [ ] **`CHANGELOG.md`, `README.md` polish** (badges only when the CI exists), a short `CONTRIBUTING.md` if wanted.
- [ ] **GitHub repository** `prmpsmart/webapp_shell` (public), push the first commit.
- [ ] **CI (GitHub Actions):** `pytest` and `ruff` on Linux, macOS and Windows for each push, on Python 3.13.
- [ ] **Build and check:** `python -m build`, `twine check dist/*`; the wheel holds `webapp_shell` and nothing else; the extras install.
- [ ] **Accounts:** PyPI and TestPyPI, with two-factor authentication.
- [ ] **Trusted publishing:** a GitHub Actions workflow that publishes on a version tag, so no token is stored.
- [ ] **Dry run on TestPyPI**, install from it, run the example.
- [ ] **Release `0.1.0`:** tag `v0.1.0`, publish to PyPI, check `pip install webapp-shell` in a clean environment.

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
