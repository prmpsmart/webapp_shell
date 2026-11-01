# Translating a program that uses webapp-shell

The user interface, and so almost every word a person reads, is the frontend's. The shell shows only a few sentences
of its own, and only when something goes wrong or when the frontend is not there: it never draws a menu, a button or a
dialog title that you did not write. (The native file dialogs use the operating system's own language.)

## The sentences

| Key (JSON)          | Field of `ShellMessages` | English default                                                             | Placeholders |
| ------------------- | ------------------------ | --------------------------------------------------------------------------- | ------------ |
| `frontendMissing`   | `frontend_missing`       | the compiled frontend is missing: {path}                                    | `{path}`     |
| `backendNotStarted` | `backend_not_started`    | the backend did not start                                                   |              |
| `versionNotObject`  | `version_not_object`     | the version path did not answer with an object                              |              |
| `backendGaveUp`     | `backend_gave_up`        | The backend stopped several times in a row. Close {name} and open it again. | `{name}`     |
| `librariesPresent`  | `libraries_present`      | all libraries are present                                                   |              |

`MessageKey` (a `StrEnum`) names the keys; `ShellMessages` holds the sentences. A test keeps the two in step.

## Give the shell your language

Python side: build a `ShellMessages` in your language and pass it in the config. The default is English.

```python
from webapp_shell import ShellConfig, ShellMessages

config = ShellConfig(
    identity=identity,
    backend=backend,
    source_root=ROOT,
    messages=ShellMessages(
        backend_gave_up="El servidor se detuvo varias veces. Cierre {name} y ábralo otra vez.",
        backend_not_started="el servidor no arrancó",
    ),
)
```

Fields you do not set keep their English text. A placeholder you drop is simply not shown; a placeholder you invent
fails when the sentence is shown, so keep to the ones in the table.

Which language to use is your program's decision (the shell has no language setting). A program whose language the
person can change keeps that choice in the backend or the frontend, and builds `ShellMessages` from it when it starts.

## Get the sentences into the frontend

The frontend can read the same catalogue as JSON, to put the keys beside its own translations:

```sh
python -m webapp_shell messages > shell-messages.en.json
```

```json
{
  "frontendMissing": "the compiled frontend is missing: {path}",
  "backendNotStarted": "the backend did not start",
  "versionNotObject": "the version path did not answer with an object",
  "backendGaveUp": "The backend stopped several times in a row. Close {name} and open it again.",
  "librariesPresent": "all libraries are present"
}
```

Translate the values, keep the keys. In Python, `ShellMessages().catalogue()` returns the same object, and
`ShellMessages(...).catalogue()` returns your translated one, which a backend route can serve to the page.

## What is not in the catalogue, on purpose

- The names of the native functions and their errors (`"start" must be text`, `missing argument "path"`) are for the
  developer. A page that calls `pickFile` shows its own message when the call fails.
- The splash page shows a spinner and, on failure, one of the sentences above. It has no other text.
- Command-line help (`--smoke`, `--splash-seconds`) is for the developer and stays in English.
