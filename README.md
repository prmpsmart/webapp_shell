# webapp-shell

A desktop window for a web app made of a **Python backend** and a **compiled frontend**. Your project describes itself
in one config object; the library starts the backend, waits until it is healthy, opens the frontend in a native window
(pywebview, or Qt on request) and gives the page a small set of native functions (file and folder dialogs, reveal in the
file manager, open a link, zoom).

> By Miracle Apata ([@prmpsmart](https://github.com/prmpsmart)). MIT licence.

```python
from pathlib import Path

from webapp_shell import AppIdentity, BackendSpec, BootColors, ShellConfig, WireProtocol, run

ROOT = Path(__file__).resolve().parent

config = ShellConfig(
    identity=AppIdentity(
        name="Acme Notes",
        slug="acme",
        storage_dir=Path.home() / ".acme",
        boot_colors=BootColors(base="#102030", glow_a="#204060", glow_b="#4060a0"),
    ),
    backend=BackendSpec(module="acme_backend", wire=WireProtocol.for_slug("acme"), package_dirs=(ROOT / "backend",)),
    source_root=ROOT,  # holds frontend/dist, the compiled frontend
)

if __name__ == "__main__":
    raise SystemExit(run(config))
```

The backend reads the same contract with the library's helpers (Starlette or FastAPI):

```python
parser = argparse.ArgumentParser()
add_launch_arguments(parser, config.backend)          # --port, --frontend, --preferences-file, --token
launch = read_launch_arguments(parser, parser.parse_args(), config.backend.wire)
app.add_middleware(TokenGuard, validator=TokenValidator(launch.token, wire), wire=wire)
```

Native functions: the standard set (file and folder dialogs, save as, reveal, open a link, zoom, boot colours) is always
there; a project adds its own and the page calls them by name.

```python
from dataclasses import dataclass
from webapp_shell import JsonValue, NativeContext, NativeFunction

@dataclass(frozen=True)
class Greeting:                   # the page's arguments, in order; each is type-checked before your code runs
    who: str

def greet(context: NativeContext, arguments: Greeting) -> JsonValue:  # context.window, .preferences, .actions
    return f"hello {arguments.who}"

config = ShellConfig(..., native_functions=(NativeFunction("greet", Greeting, greet),))
```

```js
// copy the bridge into the frontend once: python -m webapp_shell bridge --out src/
import { getBridge } from "./webapp-shell-bridge.js";

const bridge = await getBridge({ nativeGlobal: "acmeNative" });
const path = await bridge.pickFile([{ name: "Excel", extensions: ["xlsx"] }]);
const hello = await bridge.call("greet", "Ada");
```

Install: `pip install webapp-shell` (pywebview is included); `pip install "webapp-shell[qt]"` adds Qt, and
`pip install "webapp-shell[backend]"` adds Starlette for the token guard.

On Windows the pywebview window needs the WebView2 runtime (present on Windows 11); `pythonnet` is installed by pywebview.

A runnable minimal program is in `examples/minimal/`, and `examples/site/` is the documentation website, opened by the
library's own shell, with a live demonstration of every feature.

Guides (`docs/`): [the contract](docs/CONTRACT.md), [configuration](docs/CONFIGURATION.md),
[native functions](docs/NATIVE_FUNCTIONS.md), [freezing with PyInstaller](docs/FREEZING.md),
[translating](docs/TRANSLATING.md), [troubleshooting](docs/TROUBLESHOOTING.md), and the generated
[API listing](docs/API.md).
