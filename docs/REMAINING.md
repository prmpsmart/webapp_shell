# Remaining

Everything still open before `webapp-shell` is published on PyPI as a library people can use, in one place. Only what is still open: finished items are deleted (what was done is in `HANDOVER.md` and the git log). Last updated 1 November 2026.

Versions are `x.y` (decided 31 October 2026): 0.1, 0.2 … 1.0, each release counts as stable; no patch number.

At a glance: **B** code still to write, **C** the example site and the documentation, **D** checks that have never been run, **E** publishing, **F** Pixeval adopts it (not needed to publish), **G** small items.

## B. Code still to write

Decided 31 October 2026: the page talks only to the shell and the backend never does, as in Pixeval. `shell/pixeval_shell` is stable (it runs in Pixeval on Windows and macOS, and Linux is expected to pass), so the library ports it and does not re-prove it.

## C. The example site and the documentation

- [ ] **The rest of the documentation website** (`examples/site`; done: frame, Overview, Getting started, nine native-function pages, token and health, when the backend stops, a long task, For frontend developers, Security). Still to add: the shell's own splash and first-run check (a page with a demonstration), and the Reveal page in a plain browser (it needs the shell; it only says so).
- [ ] **Guides as site pages:** the Markdown guides exist in `docs/` (contract, configuration, native functions, freezing, translating, troubleshooting); show them in the site. The freezing guide has no ready PyInstaller spec yet.
- [ ] **Tests for the samples of the pages still to come** (the existing pages are covered: backend, launcher sample, build freshness, headless Qt run).

## D. Checks that have never been run

- [ ] **A frozen program** (PyInstaller) built with the library: the `--run-backend` path, the library check, the data files.

## E. Publishing

- [ ] **Badges** in `README.md` once CI has run; a short `CONTRIBUTING.md` if wanted.
- [ ] **GitHub repository** `prmpsmart/webapp_shell` (public), push the first commit; enable Pages (source: GitHub Actions); the workflows are in `.github/workflows/` and have never run.
- [ ] **Build and check:** done locally (wheel and sdist pass `twine check`, wheel holds only `webapp_shell`); repeat in CI.
- [ ] **Accounts:** PyPI and TestPyPI, with two-factor authentication; add the trusted publisher on both (repo `prmpsmart/webapp_shell`, workflow `release.yml`; environment `testpypi` on TestPyPI, `pypi` on PyPI); create both environments in the GitHub repo settings.
- [ ] **Dry run on TestPyPI**, install from it, run the example.
- [ ] **Release `0.1`:** tag `v0.1`, publish to PyPI, check `pip install webapp-shell` in a clean environment.

## F. Pixeval adopts it (after publishing, or from the sibling folder before)

- [ ] **Part 4:** replace Pixeval's `shell/` and the backend's `protocol.py`, `tokens.py` and `security.py` with the package; build Pixeval's `ShellConfig` in `launch.py`; adapt Pixeval's tests (the title says `backend` instead of `engine`; `--sandbox` becomes a `CliFlag`, `--developer-tools` a source-only argument).
- [ ] **Keep in Pixeval:** the freeze profiles and their tests, the PIL picture-format check, the boot-colour tests tied to its frontend tokens.
- [ ] **Pixeval's frontend uses the library's bridge file** instead of its own `bridge/`.
- [ ] **Lock file and packaging:** Pixeval's `requirements.lock` pins `webapp-shell`; the PyInstaller builds still pass.
- [ ] **Update Pixeval's docs:** `rebranding-docs/12-webapp-shell.md` (the Pixeval repository's copy says nothing is built; point it to this repository), `02-architecture.md`, `05-delivery.md`, `shell/README.md`.

## G. Small items

- [ ] `HANDOVER.md` and this file overlap; once the library is published, shrink the handover to history and keep this file as the list.
