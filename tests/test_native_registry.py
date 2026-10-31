"""The native functions: the registry, the standard set against a fake window, the project's own functions, and the two
transports (Qt's single `call` slot and pywebview's attached functions)."""

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from webapp_shell import NativeError, NativeFunction, NoArguments
from webapp_shell.enums import NativeMethod
from webapp_shell.native.filters import FileFilter
from webapp_shell.native.os_actions import OsActions
from webapp_shell.native.registry import NativeRegistry
from webapp_shell.native.standard import standard_functions
from webapp_shell.native.webview_bridge import WebviewBridge
from webapp_shell.native.window import NativeContext, NativeWindow
from webapp_shell.preferences import ShellPreferences


@dataclass(frozen=True)
class Greeting:
    who: str


class FakeWindow(NativeWindow):
    def __init__(self):
        self.calls: list[tuple] = []
        self.answer: str | None = "/chosen/path"

    def pick_folder(self, start):
        self.calls.append(("pick_folder", start))
        return self.answer

    def pick_file(self, filters, start):
        self.calls.append(("pick_file", filters, start))
        return self.answer

    def save_as(self, name, start):
        self.calls.append(("save_as", name, start))
        return self.answer

    def set_zoom(self, factor):
        self.calls.append(("set_zoom", factor))
        return True


class FakeActions(OsActions):
    def __init__(self):
        self.revealed: list[str] = []

    def reveal(self, path):
        self.revealed.append(path)
        return True


@pytest.fixture
def window():
    return FakeWindow()


@pytest.fixture
def context(window):
    return NativeContext(window, ShellPreferences(None), FakeActions())


@pytest.fixture
def registry():
    return NativeRegistry(standard_functions())


def test_the_standard_set_is_exactly_the_native_methods(registry):
    assert registry.names == [method.value for method in NativeMethod]


def test_a_call_answers_in_the_envelope(registry, context, window):
    assert registry.call(context, "pickFolder", ["/start"]) == {"ok": True, "value": "/chosen/path"}
    assert window.calls == [("pick_folder", "/start")]


def test_a_cancelled_dialog_is_none(registry, context, window):
    window.answer = None
    assert registry.call(context, "pickFile", [[], ""]) == {"ok": True, "value": None}


def test_filters_from_the_page_are_parsed_before_they_reach_the_window(registry, context, window):
    sent = [{"name": "Excel", "extensions": ["*.xlsx"]}, {"name": "", "extensions": []}]
    assert registry.call(context, "pickFile", [sent, "/s"])["ok"] is True
    assert window.calls == [("pick_file", [FileFilter("Excel", ("*.xlsx",))], "/s")]  # the unusable one is dropped


def test_save_as_proposes_the_name(registry, context, window):
    registry.call(context, "saveAs", ["report.xlsx", ""])
    assert window.calls == [("save_as", "report.xlsx", "")]


def test_what_the_page_sends_must_fit_the_declared_types(registry, context, window):
    assert registry.call(context, "pickFolder", [{"not": "text"}]) == {"ok": False, "error": '"start" must be text'}
    assert registry.call(context, "saveAs", [None, 5])["ok"] is False
    assert registry.call(context, "pickFile", [[{"name": "x"}]])["error"] == '"filters[0]" needs the field "extensions"'
    assert window.calls == []  # a refused call never reaches the window


def test_reveal_and_open_url_go_through_the_os_actions(registry, context):
    assert registry.call(context, "reveal", ["/some/file"])["value"] is True
    assert context.actions.revealed == ["/some/file"]
    assert registry.call(context, "openUrl", ["javascript:alert(1)"]) == {"ok": True, "value": False}


def test_zoom_is_limited_and_only_numbers_count(registry, context, window):
    assert registry.call(context, "setZoom", [99])["value"] is True
    assert window.calls == [("set_zoom", 3.0)]
    assert registry.call(context, "setZoom", ["1.2"]) == {"ok": False, "error": '"factor" must be a number'}
    assert registry.call(context, "setZoom", [True])["ok"] is False  # true is not 1


def test_boot_colours_are_remembered_only_when_valid(registry, context):
    good = {"base": "#102030", "glowA": "#204060", "glowB": "#4060a0"}
    assert registry.call(context, "setBootColors", [good])["value"] is True
    assert context.preferences.boot_colors.base == "#102030"
    assert registry.call(context, "setBootColors", [{**good, "base": "red"}])["value"] is False
    assert registry.call(context, "setBootColors", [{"base": "#000000"}])["error"] == '"colors" needs the field "glowA"'
    assert registry.call(context, "setBootColors", [{**good, "extra": 1}])["error"] == '"colors" has no field "extra"'


def test_an_unknown_name_or_bad_arguments_are_refused_in_plain_words(registry, context):
    assert registry.call(context, "formatDisk", []) == {"ok": False, "error": "unknown native function"}
    assert registry.call(context, "pickFolder", "not a list")["error"] == "the arguments must be a list"
    assert registry.call(context, "reveal", [])["error"] == 'missing argument "path"'
    assert registry.call(context, "reveal", ["a", "b"])["error"] == "too many arguments"


def test_a_project_adds_its_own_function(context):
    def greet(_context: NativeContext, arguments: Greeting) -> str:
        return f"hello {arguments.who}"

    registry = NativeRegistry((*standard_functions(), NativeFunction("greet", Greeting, greet)))
    assert registry.call(context, "greet", ["Ada"]) == {"ok": True, "value": "hello Ada"}


def test_a_handler_may_refuse_in_words_the_page_shows(context):
    def refuse(_context: NativeContext, _arguments: NoArguments) -> None:
        raise NativeError("not allowed here")

    registry = NativeRegistry((NativeFunction("refuse", NoArguments, refuse),))
    assert registry.call(context, "refuse", []) == {"ok": False, "error": "not allowed here"}


def test_a_crash_in_a_handler_does_not_leak_its_details(context, caplog):
    def crash(_context: NativeContext, _arguments: NoArguments) -> None:
        raise RuntimeError("secret internals")

    registry = NativeRegistry((NativeFunction("crash", NoArguments, crash),))
    answer = registry.call(context, "crash", [])
    assert answer == {"ok": False, "error": "the native function failed"}
    assert "secret internals" not in json.dumps(answer) and "secret internals" in caplog.text


@pytest.mark.parametrize("name", ["", "Pick", "pick_file", "1pick", "pick file"])
def test_a_function_name_must_be_camel_case(name):
    with pytest.raises(ValueError):
        NativeFunction(name, NoArguments, lambda _context, _arguments: None)


def test_two_functions_cannot_share_a_name():
    with pytest.raises(ValueError):
        NativeRegistry(
            (*standard_functions(), NativeFunction("pickFile", NoArguments, lambda _context, _arguments: None))
        )


def test_the_projects_functions_reach_the_shell_registry(config):
    from dataclasses import replace

    from webapp_shell.settings import Settings
    from webapp_shell.shell import Shell

    class Dummy(Shell):
        def event_loop(self, boot): ...
        def navigate(self, url): ...
        def show_page(self, html): ...
        def set_title(self, title): ...
        def quit(self): ...

    own = NativeFunction("greet", NoArguments, lambda _context, _arguments: "hi")
    shell = Dummy(Settings.of(replace(config, native_functions=(own,))), backend=None)
    assert shell.native.names == [*(m.value for m in NativeMethod), "greet"]


class TestWebviewBridge:
    def test_every_registered_function_is_exposed_and_answers_in_the_envelope(self, registry, context):
        bridge = WebviewBridge(registry, context)
        assert bridge.pickFolder("/s") == {"ok": True, "value": "/chosen/path"}
        assert bridge.pickFolder.__name__ == "pickFolder"

    def test_the_api_exposes_only_functions(self, registry, context):
        """pywebview walks every public attribute of the API object. A public attribute holding the window sent it into
        the .NET window (`window.native...`), which failed on Windows with thread and recursion errors."""
        bridge = WebviewBridge(registry, context)
        public = {name: getattr(bridge, name) for name in dir(bridge) if not name.startswith("_")}
        assert all(callable(member) for member in public.values()), public
        assert set(public) == set(registry.names)

    def test_pywebviews_own_walk_finds_the_same_functions(self, registry, context):
        """The walk of `webview.util.inject_pywebview` (pywebview 6.2.1): every public name, a function or method is
        exposed, anything else is walked into. Its page-side wrapper forwards `arguments`, so no declared parameters
        are needed."""
        import inspect

        def walk(obj, found=None):
            found = {} if found is None else found
            for name in dir(obj):
                if name.startswith("_"):
                    continue
                attr = getattr(obj, name)
                if not getattr(attr, "_serializable", True):
                    continue
                if inspect.ismethod(attr) or inspect.isfunction(attr):
                    found[name] = attr
                elif inspect.isclass(attr) or (not callable(attr) and hasattr(attr, "__module__")):
                    walk(attr, found)
            return found

        assert set(walk(WebviewBridge(registry, context))) == set(registry.names)

    def test_a_project_function_is_exposed_too(self, context):
        registry = NativeRegistry(
            (*standard_functions(), NativeFunction("greet", NoArguments, lambda _context, _arguments: "hi"))
        )
        assert WebviewBridge(registry, context).greet() == {"ok": True, "value": "hi"}


class TestQtBridge:
    @pytest.fixture
    def bridge(self, registry, context):
        from webapp_shell.native.qt_bridge import QtBridge

        return QtBridge(registry, context)

    def test_one_slot_carries_every_function(self, bridge, window):
        answer = json.loads(bridge.call("pickFolder", json.dumps(["/s"])))
        assert answer == {"ok": True, "value": "/chosen/path"}
        assert window.calls == [("pick_folder", "/s")]

    def test_text_that_is_not_json_is_refused(self, bridge):
        assert json.loads(bridge.call("pickFolder", "{broken"))["ok"] is False

    def test_no_arguments_means_an_empty_list(self, bridge):
        assert json.loads(bridge.call("setZoom", ""))["ok"] is False  # called without its argument

    def test_the_page_script_lists_the_registered_names_and_the_slug(self, registry, config):
        from webapp_shell.native import qt_bridge

        glue = qt_bridge._GLUE_JS % {
            "object": qt_bridge.CHANNEL_OBJECT,
            "names": json.dumps(registry.names),
            "global": config.identity.native_global,
            "ready": config.identity.native_ready_event,
        }
        assert "window.acmeNative = api" in glue and "'acmenativeready'" in glue
        assert '"pickFolder"' in glue


def test_the_standard_functions_never_use_a_path_they_were_not_given(registry, context, window, tmp_path: Path):
    registry.call(context, "pickFolder", [str(tmp_path)])
    assert window.calls[0] == ("pick_folder", str(tmp_path))
