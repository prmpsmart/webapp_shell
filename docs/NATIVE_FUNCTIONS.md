# Native functions

The page calls the shell through the bridge file, never the backend.

## The standard set

`pickFile`, `pickFolder`, `saveAs`, `reveal`, `openUrl`, `setBootColors`, `setZoom` (the `NativeMethod` enum holds the
names). They are always there, in both window toolkits, with the same names and the same answers.

## Calling from the page

```
python -m webapp_shell bridge --out src/
```

```js
import { getBridge } from "./webapp-shell-bridge.js";

const bridge = await getBridge({ nativeGlobal: "acmeNative" }); // "<slug>Native"
const path = await bridge.pickFile([{ name: "Excel", extensions: ["xlsx"] }]);
const hello = await bridge.call("greet", "Ada"); // your own function
```

Every call answers `{ ok: true, value }` or `{ ok: false, error }` inside the bridge, which turns the second form into
a rejected promise. `webapp-shell-bridge.d.ts` types it all.

## Your own function

```python
@dataclass(frozen=True)
class Greeting:
    who: str


def greet(context: NativeContext, arguments: Greeting) -> JsonValue:
    return f"hello {arguments.who}"


ShellConfig(..., native_functions=(NativeFunction("greet", Greeting, greet),))
```

- The dataclass lists the arguments **in the order the page sends them**.
- Supported types: `str`, `int`, `float` (an `int` is accepted), `bool`, `X | None`, `list[X]`, `tuple[X, ...]` and
  nested dataclasses (their keys are camelCase on the wire). Anything else fails when the function is declared.
- Nothing is converted silently: `"1.2"` is not a number and `1` is not a `bool`. A wrong argument is a `NativeError`
  with a plain message (`"who" must be text`, `missing argument "who"`, `too many arguments`).
- Use `NoArguments` for a function that takes none.
- The handler gets a `NativeContext`: `.window` (the dialogs and zoom), `.preferences` (the shell's remembered
  colours), `.actions` (reveal, open a link).
- Raise `NativeError("message")` to refuse; any other exception is reported as an error too, never a crash.
- The return value must be JSON (`JsonValue`).
