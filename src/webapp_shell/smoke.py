"""The headless self-check both shells share: what to ask the loaded page and how to report it."""

from dataclasses import dataclass

from .json_types import JsonObject


def page_probe_js(native_global: str) -> str:
    """What to ask the loaded page: its title, whether the app rendered, and which native bridge it can see."""
    return (
        "JSON.stringify({"
        "title: document.title,"
        "rootChildren: document.getElementById('root') ? document.getElementById('root').children.length : -1,"
        "hash: location.hash,"
        f"native: window.{native_global} ? '{native_global}' : "
        "(window.pywebview && window.pywebview.api ? 'pywebview' : 'none')})"
    )


SETTLE_SECONDS = 2.5


@dataclass(frozen=True)
class SmokeReport:
    shell: str
    backend: JsonObject
    page: str

    def __str__(self) -> str:
        return f"{self.shell}: backend={self.backend} page={self.page}"
