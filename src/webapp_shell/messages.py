"""The few sentences the shell shows itself (in the splash page's error, and in what it prints), as one catalogue.

A project that translates its program gives its own `ShellMessages` (in the language it chose) to `ShellConfig`; the
frontend can read the same catalogue as JSON (`python -m webapp_shell messages`) to put the keys in its translation
files. The user interface itself belongs to the frontend; these are only the sentences that appear when there is no
frontend yet or any more.
"""

from dataclasses import dataclass
from enum import StrEnum

from .json_types import JsonObject


class MessageKey(StrEnum):
    """The name of each sentence. The member name, lower-cased, is the field of `ShellMessages`; the value is the key in
    the JSON catalogue."""

    FRONTEND_MISSING = "frontendMissing"
    BACKEND_NOT_STARTED = "backendNotStarted"
    VERSION_NOT_OBJECT = "versionNotObject"
    BACKEND_GAVE_UP = "backendGaveUp"
    LIBRARIES_PRESENT = "librariesPresent"


@dataclass(frozen=True)
class ShellMessages:
    """Every sentence, with its English default. `{name}` and `{path}` are filled in when the sentence is shown."""

    frontend_missing: str = "the compiled frontend is missing: {path}"
    backend_not_started: str = "the backend did not start"
    version_not_object: str = "the version path did not answer with an object"
    backend_gave_up: str = "The backend stopped several times in a row. Close {name} and open it again."
    libraries_present: str = "all libraries are present"

    def text(self, key: MessageKey, **values: str) -> str:
        """The sentence for `key` with its placeholders filled."""
        return self.sentences()[key].format(**values)

    def sentences(self) -> dict[MessageKey, str]:
        """Each key with its sentence, in the order of `MessageKey`."""
        return {key: getattr(self, key.name.lower()) for key in MessageKey}

    def catalogue(self) -> JsonObject:
        """The JSON object a frontend reads: key → sentence, placeholders left as `{name}`."""
        return {str(key): sentence for key, sentence in self.sentences().items()}


ENGLISH = ShellMessages()
