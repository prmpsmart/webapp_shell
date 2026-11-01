# Configuring identity and backend

A project gives the library one `ShellConfig` and calls `run(config)`.

```python
ShellConfig(
    identity=AppIdentity(...),
    backend=BackendSpec(...),
    source_root=ROOT,
)
```

## `AppIdentity` — who the program is

| Field | Meaning |
| --- | --- |
| `name` | Shown in the window title, the splash and the messages ("Acme Notes"). Not empty. |
| `slug` | Lowercase letters and digits, starting with a letter. Names the page's native object (`window.<slug>Native`), the event `<slug>nativeready` and the default wire names. |
| `storage_dir` | The folder where the shell remembers things: `shell.json` (opening colours) and `preferences.json` (the backend's file). |
| `boot_colors` | `BootColors(base, glow_a, glow_b)`: the opening screen until the page reports the user's own. |
| `icon_png`, `icon_ico` | Window icon (macOS, Linux) and splash mark; Windows draws only `.ico` files. Both optional. |
| `window_size` | Default `(1280, 800)`. |

## `BackendSpec` — how the backend starts

| Field | Meaning |
| --- | --- |
| `module` | The backend package: `python -m <module>`; frozen, its `__main__.main(argv)` runs. |
| `wire` | The `WireProtocol` (see `CONTRACT.md`). |
| `frontend_dist` | Where the compiled frontend is, relative to the program's root (default `frontend/dist`). |
| `frontend_argument`, `port_argument`, `preferences_argument` | The names of the standard arguments (`None` for no preferences file). |
| `arguments` | Always passed. |
| `source_only_arguments` | Passed only when running from the source (for example a developer switch). |
| `flags` | `CliFlag(name, help, passes)`: a switch the program accepts (`--sandbox`); when given, the backend receives `passes`. |
| `package_dirs` | Import roots added by hand when running from the source. |

## `ShellConfig` — the rest

| Field | Meaning |
| --- | --- |
| `source_root` | Running from the source: the folder that holds `frontend/dist`. |
| `host` | `127.0.0.1`. |
| `startup_timeout` | Seconds to wait for the health path (20). |
| `splash_seconds` | Minimum time of the splash (0). |
| `native_functions` | The project's own native functions (see `NATIVE_FUNCTIONS.md`). |
| `required_libraries` | Imported by `--check-libraries` on a frozen program. |
| `messages` | The shell's few sentences in the project's language (see `TRANSLATING.md`). |

## The command line every project gets

`<program> [webview|qt] [--smoke] [--splash-seconds N] [the project's flags]`. `--smoke` loads the page headlessly,
prints a one-line JSON report and exits; it never reads or writes the user's preferences.
