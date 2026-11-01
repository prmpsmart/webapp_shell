# Contributing

Thank you for helping. The library is small and typed on purpose; these are the rules that keep it so.

## Set up

Python 3.13 or newer, and Node (only for the documentation site and the Markdown checks).

```sh
git clone https://github.com/prmpsmart/webapp_shell.git
cd webapp_shell
python -m venv .venv && . .venv/bin/activate   # on Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]" pyright
```

## The checks

CI runs all of these on Ubuntu, macOS and Windows; run them before you push, with the newest `ruff`.

```sh
python -m ruff check .
python -m ruff format --check .
npx --yes prettier --check "**/*.md"
npx --yes markdownlint-cli "**/*.md" --ignore "**/node_modules/**"
python -m pyright
python -m pytest
python -m pytest -m freeze     # freezes the minimal example with PyInstaller (slow)
```

## How the code is written

- **Typed.** `pyright` is strict on `src/` and the examples. Use dataclasses and `StrEnum`s, not dictionaries and loose
  strings; everything that crosses between the page and Python is a `JsonValue`.
- **One job per class.** A window toolkit (`webview`, `PySide6`) is imported only by the modules of its own shell, never
  by a shared one, so a Qt-only build never reaches pywebview (a test checks it). `PyInstaller` is imported by
  `freezing/spec.py` alone.
- **The public API is what is exported.** A name is public when it is in the `__all__` of `webapp_shell`,
  `webapp_shell.contract`, `webapp_shell.contract.guard` or `webapp_shell.freezing`. Adding one is a decision: it needs a
  test and a line in `CHANGE_LOG.md`. Regenerate `docs/API.md` with `python tools/api_listing.py` (a test fails when it
  is out of date). The examples and the guides import only public names.
- **Tests.** Every behaviour has one. A fake backend lives in `tests/fake_backend`; tests are not type-checked because
  their fakes are not the real types.
- **Docs.** `CHANGE_LOG.md` holds the version in progress (`change_logs/` the past ones); `docs/REMAINING.md` lists only
  what is still open. Markdown is formatted by `prettier` and checked by `markdownlint`.

## The documentation site

`examples/site` is a React and TypeScript site that the library's own shell opens. Its compiled `frontend/dist` is
committed (a test checks that it contains the code it shows), so after changing the site:

```sh
cd examples/site
npm ci
npm run build
```

The guides in `docs/` are shown as pages of the site; editing one means rebuilding it.

## A change

Open an issue first for anything that changes the public API. A pull request needs the checks above to pass, a test for
the change, and a line in `CHANGE_LOG.md` when behaviour changes.
