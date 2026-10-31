# Handover

Written on 31 October 2026, at the end of part 1; part 2 was added the same day. It says what exists, what does not, and what is left before the
library can be published on PyPI. Nothing here is committed or published yet.

## Where it is

`Workspace/PRMPSmart/webapp_shell`, its own git repository. It was built inside the Pixeval rebuild repository
(`pixeval_rebranding`, branch `rebranding`) and moved here once isolated; the first commit here holds parts 1 and 2. It
imports nothing from Pixeval; a test (`tests/test_library_is_independent.py`) fails if a Pixeval name appears in
`src/`. Pixeval's own `shell/` and backend are untouched and still what Pixeval runs. Pixeval's design notes for the
library are in its `rebranding-docs/12-webapp-shell.md`.

## What part 1 did

- **Extracted the generic shell** from `shell/pixeval_shell/` into `src/webapp_shell/`: process owner, health wait,
  token handover, watchdog, splash, the two window toolkits, the native bridge, frozen-build launching.
- **Config objects** (all frozen dataclasses): `AppIdentity` (name, slug, storage folder, icons, opening colours, window
  size), `WireProtocol` (token header, cookie, query, environment variable, health and version paths; `for_slug` gives
  a consistent default), `BackendSpec` (the backend module, the compiled frontend, extra arguments, source-only
  arguments, `CliFlag` switches, import roots), `ShellConfig` (all of it, plus the root folder and timeouts).
- **`run(config)`** is the project's entry point. The command line is `<program> [webview|qt] [--smoke]
[--splash-seconds N]` plus the project's own `CliFlag`s. pywebview is the default toolkit.
- **Name-free:** the page's native object is `window.<slug>Native` (Qt shell); the Qt script, the window title, the
  splash and the watchdog message use the identity.
- **Tests:** 73, in `tests/`, written against a made-up project ("Acme Notes") with a real child process
  (`tests/fake_backend`) that honours the contract. ruff is clean (own config in `pyproject.toml`).

## Differences from Pixeval's shell (to settle when Pixeval switches)

- The window title says `backend` where Pixeval's says `engine`.
- `Installation` takes the source root explicitly; `Settings` is built with `Settings.of(config, ...)`.
- `--sandbox` and `--developer-tools` are no longer in the library: Pixeval will declare them as `CliFlag` and
  `source_only_arguments`.
- The libraries list and the PIL picture-format check of `library_check.py`: the list is now `required_libraries` in the
  config; the picture check stays Pixeval's (to be rewritten on its side).
- Pixeval's packaging tests (freeze profiles) and the tests tied to its frontend tokens (boot-colour equality) stay in
  Pixeval.

## What part 2 did

- **The backend's side of the contract**, in `webapp_shell.contract`: `TokenValidator` and `OriginPolicy` (no web
  framework), `add_launch_arguments` and `read_launch_arguments` (the backend reads the port, frontend, preferences file
  and token with the same argument names the shell builds the command from), and `guard.TokenGuard`, a Starlette
  middleware that also serves FastAPI (`pip install "webapp-shell[backend]"`). Its refusal bodies are
  `GuardResponses`, defaulting to Pixeval's (`{"code": "UNAUTHORIZED"}`, `{"code": "FOREIGN_ORIGIN"}`).
- **`WireProtocol`** gained `api_prefix`, `ws_close_unauthorized` and `token_from_environment`.
- **Tests (90):** the checks of Pixeval's `test_security.py` rewritten against a small Starlette app, and a round trip
  proving the backend reads back exactly what the shell builds. A test proves the core imports without Starlette.
- **Not done in part 2:** the WebSocket path (`WS_PATH`) stays the project's own; the library only offers
  `is_valid_connection` and the close code. Pixeval's backend still has its own `protocol.py`, `tokens.py` and
  `security.py`; they are replaced in part 4.

## What is not done

1. **Native registry** (part 3): the native functions are still the fixed `NativeMethod` list; projects cannot add
   their own yet. The frontend bridge package (the page-side client) does not exist.
2. **The example site and the documentation** (`12-webapp-shell.md`, sections 7 and 8): a modern documentation website
   that demonstrates every capability, with frontend, backend and shell snippets per feature; committed `dist`; a
   static copy for GitHub Pages. Only this README exists.
3. **Pixeval depends on the library** (part 4): replace `shell/` and the backend's `protocol.py`, `tokens.py` and
   `security.py` with the package; adapt Pixeval's tests; lock file.
4. **Never run through the library:** the real windows (pywebview on macOS and Windows, Qt) and `--smoke` have not been
   run from `webapp_shell`. The code is the same as Pixeval's, which was run on macOS; Windows was never run (see
   Pixeval's `10-remaining.md`).

## What is left before PyPI

1. **Decide the licence** and add a `LICENSE` file; put `license = { file = "LICENSE" }` back in `pyproject.toml`
   (removed so the build does not fail). Not decided yet.
2. **Recheck the name.** `webapp-shell` was free on PyPI on 28 October 2026; check again on the day.
3. **Metadata in `pyproject.toml`:** URLs (repository, documentation, issues), classifiers (Python versions, OS,
   framework), keywords, a real description. Confirm `requires-python` (>= 3.11; `StrEnum` is used).
4. **A repository on GitHub** (`prmpsmart/webapp_shell`, public) and the first commit.
5. **Finish enough to be useful:** at least part 3 and the README example run for real (a minimal backend and
   frontend in `examples/`), so a stranger can install it and see a window. Part 1 alone is a refactor, not yet a
   product.
6. **Build and check:** `python -m build`, then `twine check dist/*`; install the wheel into a clean environment and run
   the example; confirm the wheel holds `webapp_shell` and nothing else.
7. **Dry run on TestPyPI**, then PyPI. Create the accounts with two-factor authentication; prefer _trusted
   publishing_ (a GitHub Actions workflow that publishes on a version tag), so no token is stored.
8. **CI:** run `pytest` and `ruff` on Linux, macOS and Windows for each push (the Windows run is what has never
   happened).
9. **Version and changelog:** `0.1.0` as the first release, a `CHANGELOG.md`, tags `v0.1.0`.
