# Handover

Written on 31 October 2026, at the end of part 1; parts 2 and 3 were added the same day. It says what exists, what does not, and what is left before the
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

## What part 3 did

- **A registry of native functions** (`webapp_shell.native`): `NativeFunction(name, handler)` and `NativeRegistry`. A
  handler is called as `handler(context, *arguments)` and may raise `NativeError` to refuse in words the page shows.
  Names are camelCase; the page is untrusted, so an unknown name, wrong arguments or a crash all come back as a plain
  message (the details go to the log). Every answer is one envelope: `{"ok": true, "value": ...}` or
  `{"ok": false, "error": "..."}`.
- **The standard set written once** (`standard.py`) against `NativeContext` (a `NativeWindow`, the preferences and the OS
  actions). Each toolkit supplies only its window (`QtWindow`, `WebviewWindow`): the dialogs and the zoom that used to
  be duplicated in the two bridges.
- **Transports shrank:** Qt has one slot, `call(name, argumentsJson)`, with page glue built from the registered names;
  pywebview gets each registered function attached by name, with the window kept private (the Windows fix).
- **Projects add their own** with `ShellConfig(native_functions=(NativeFunction("greet", handler),))`.
- **The page-side bridge:** one ES module `bridge/webapp-shell-bridge.js` plus `.d.ts`, shipped in the wheel;
  `python -m webapp_shell bridge --out DIR` copies it into a frontend. `getBridge({ nativeGlobal })` finds the Qt
  object or pywebview's, waits for a late shell, unwraps the envelope, and falls back for a plain browser.
- **Tests (125):** the registry, the standard functions against a fake window, both transports (including a replica of
  pywebview's API walk), and the JavaScript client run under Node with a fake `window`. A wheel was built once and
  checked for the bridge files.
- **Wire change for Pixeval:** Pixeval's current frontend `bridge/` expects the old shapes (Qt returned `''` for a
  cancelled dialog; each method was its own slot). Part 4 switches Pixeval's frontend to this file.

## The minimal example

`examples/minimal/` (Acme Notes): backend, one-page frontend with `webapp-shell-bridge.js` copied in, launcher, README.
`tests/test_example_minimal.py` starts the backend through the shell's own `BackendProcess` and checks the token, and
runs the Qt shell headless (`app.py qt --smoke`, offscreen) to prove the glue, the channel and the bridge file work
together: the page reported `native: acmeNative` and its title from the bridge. 128 tests in all.

## What is not done

1. **The documentation site** (`12-webapp-shell.md`, sections 7 and 8): a modern documentation website
   that demonstrates every capability, with frontend, backend and shell snippets per feature; committed `dist`; a
   static copy for GitHub Pages. Only this README exists.
2. **Pixeval depends on the library** (part 4): replace `shell/` and the backend's `protocol.py`, `tokens.py` and
   `security.py` with the package; adapt Pixeval's tests; lock file.
3. **Never run through the library:** the real windows (pywebview on macOS and Windows, Qt) and `--smoke` have not been
   run from `webapp_shell`. The code is the same as Pixeval's, which was run on macOS; Windows was never run (see
   Pixeval's `10-remaining.md`).

## What is left before PyPI

Tracked in `REMAINING.md`, which is the list to work from (decisions, code, documentation and example site, checks never run, publishing steps, and Pixeval adopting the library).

## The documentation site (`examples/site`, started 31 October 2026)

React + Vite + TypeScript, built into `examples/site/frontend/dist` (committed). Run `npm install && npm run build` in `examples/site` after changing anything under `src/`; `npm run dev` serves it for design work (the bridge then reports a plain browser).

- `src/pages.ts` is the list of pages (an enum `PageId`, `Section`); a new page is a component plus one entry there.
- Each live feature page shows three snippets (`CodeTabs`): the frontend and the backend files are imported raw (`?raw`), so the shown code is the running code. The shell tab is `app.py`.
- `docs_backend/` is the site's backend (contract plus one route per demonstration); `app.py` is the launcher. Slug `docs`, so the native global is `docsNative`.
- `src/bridge/` is a copy made with `python -m webapp_shell bridge --out examples/site/src/bridge` (prettier ignores it; a test keeps it equal to the package's file).
- `tests/test_example_site.py`: backend through `BackendProcess`, the Getting started sample executed, the committed build checked against the code it shows, and a headless Qt run of the whole site.
- A native-function page is `FeaturePage` + `Demo` + a `src/demos/<feature>.ts` file (the code shown, also the code run) + `codeFor(...)` for the three tabs; a feature with no backend part passes `null` and the tab says so. `docs_backend/save_note.py` is the second backend sample.
- Pages now: Overview, Getting started; native functions (choose a file, choose a folder, save as, show in the file manager, open a link, zoom, boot colours, your own function); shell and backend (token and health, when the backend stops). `native_functions.py` holds the site's own shell functions; the crash demonstration ends the backend process on purpose and relies on the watchdog (three restarts within two minutes, then it gives up).
- Version numbers are `x.y` (0.1, 0.2 … 1.0), decided 31 October 2026.
- Change logs: `CHANGE_LOG.md` in the root is the version in progress (title `# <version>`, equal to `pyproject.toml`); `change_logs/<version>.md` are the past ones. On a new version, move the root file into `change_logs/` and begin a new one. Update `CHANGE_LOG.md` in every part that changes behaviour.
- Guides pages: `ForFrontend` and `Security` (static text; a test checks the Security page's claims against the library: URL schemes, host, close code). `BackendJob` is the third backend sample (`docs_backend/job.py`, a typed `Job` dataclass polled over HTTP).
- Typing: `npx pyright` (config in `pyproject.toml`, strict) must report 0 errors on `src/`. Only `native/zoom.py`, `native/webview_background.py` and `native/webview_icon.py` switch off the unknown-type rules (AppKit, .NET and GTK publish no stubs), plus a few one-line ignores in `qt_shell.py` and `webview_shell.py` where PySide6 and pywebview leave a callable type open; each says why.
- Native function arguments: `NativeFunction(name, ArgumentsDataclass, handler)`; supported field types are str, int, float, bool, `X | None`, `list[X]`, `tuple[X, ...]` and nested dataclasses (camelCase on the wire); an unsupported type fails when the function is declared. `NoArguments` is for a function with none.
- Policy (31 October 2026): `shell/pixeval_shell` is treated as stable and proven on Windows and macOS; port it and make only the changes the library needs, do not re-verify it.
