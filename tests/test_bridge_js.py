"""The page-side bridge: one `.js` file, run under Node with a fake window, and kept equal to the Python side."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from webapp_shell.__main__ import BRIDGE_FILES, copy_bridge, main
from webapp_shell.enums import NativeMethod

BRIDGE = Path(__file__).resolve().parents[1] / "src" / "webapp_shell" / "bridge" / "webapp-shell-bridge.js"
node = pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")


def run_js(body: str) -> object:
    """Runs `body` as an ES module with the bridge imported as `bridge` and `window` faked; returns its JSON result."""
    script = f"""
import * as bridge from {json.dumps(BRIDGE.as_uri())}
const listeners = {{}}
globalThis.window = {{
  addEventListener: (name, fn) => (listeners[name] ??= []).push(fn),
  removeEventListener: () => {{}},
  dispatch: (name) => (listeners[name] || []).forEach((fn) => fn()),
  open: (...args) => (globalThis.opened = args),
}}
const result = await (async () => {{ {body} }})()
console.log(JSON.stringify(result))
"""
    done = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True, timeout=30)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def test_the_js_list_of_standard_methods_equals_the_python_one():
    text = BRIDGE.read_text()
    listed = re.search(r"STANDARD_METHODS = \[(.*?)\]", text, re.S).group(1)
    assert re.findall(r"'(\w+)'", listed) == [method.value for method in NativeMethod]


def test_the_typings_describe_every_standard_method():
    typings = BRIDGE.with_suffix(".d.ts").read_text()
    for method in NativeMethod:
        assert re.search(rf"\b{method.value}\(", typings), method.value


@node
def test_inside_pywebview_a_call_unwraps_the_envelope_and_a_cancelled_dialog_is_null():
    result = run_js("""
      window.pywebview = { api: {
        pickFile: async (filters, start) => ({ ok: true, value: start + '/a.xlsx' }),
        pickFolder: async () => ({ ok: true, value: '' }),
      } }
      const b = await bridge.getBridge({ nativeGlobal: 'acmeNative' })
      return [b.kind, b.canPickPaths, await b.pickFile([], '/x'), await b.pickFolder()]
    """)
    assert result == ["pywebview", True, "/x/a.xlsx", None]


@node
def test_inside_qt_the_slug_global_is_used():
    result = run_js("""
      window.acmeNative = { reveal: async (path) => ({ ok: true, value: path === '/f' }) }
      const b = await bridge.getBridge({ nativeGlobal: 'acmeNative' })
      return [b.kind, await b.reveal('/f')]
    """)
    assert result == ["qt", True]


@node
def test_an_error_from_the_shell_rejects_and_a_project_function_is_called_by_name():
    result = run_js("""
      window.pywebview = { api: {
        greet: async (who) => ({ ok: true, value: 'hello ' + who }),
        refuse: async () => ({ ok: false, error: 'not allowed here' }),
      } }
      const b = await bridge.getBridge({ nativeGlobal: 'acmeNative' })
      let refused = null
      try { await b.call('refuse') } catch (e) { refused = [e instanceof bridge.NativeCallError, e.message] }
      let missing = null
      try { await b.call('nothing') } catch (e) { missing = e.message }
      return [await b.call('greet', 'Ada'), refused, missing]
    """)
    assert result == ["hello Ada", [True, "not allowed here"], 'the shell has no native function "nothing"']


@node
def test_the_bridge_waits_for_a_shell_that_announces_itself_late():
    result = run_js("""
      const pending = bridge.getBridge({ nativeGlobal: 'acmeNative', waitMs: 5000 })
      window.pywebview = { api: { setZoom: async () => ({ ok: true, value: true }) } }
      window.dispatch('pywebviewready')
      const b = await pending
      return [b.kind, await b.setZoom(1.2)]
    """)
    assert result == ["pywebview", True]


@node
def test_in_a_plain_browser_paths_are_null_links_open_and_own_functions_use_their_fallback():
    result = run_js("""
      const b = await bridge.getBridge({
        nativeGlobal: 'acmeNative', waitMs: 20, fallbacks: { greet: (who) => 'hi ' + who },
      })
      let notThere = null
      try { await b.call('other') } catch (e) { notThere = e.message }
      return [b.kind, b.canPickPaths, await b.pickFile(), await b.reveal('/x'), await b.openUrl('https://a.b'),
              globalThis.opened[0], await b.call('greet', 'Ada'), notThere]
    """)
    assert result == [
        "browser",
        False,
        None,
        False,
        True,
        "https://a.b",
        "hi Ada",
        '"other" is not available in a plain browser',
    ]


def test_the_command_copies_the_bridge_into_a_frontend(tmp_path, capsys):
    assert main(["bridge", "--out", str(tmp_path / "src" / "native")]) == 0
    assert sorted(p.name for p in (tmp_path / "src" / "native").iterdir()) == sorted(BRIDGE_FILES)
    assert (tmp_path / "src" / "native" / BRIDGE_FILES[0]).read_text() == BRIDGE.read_text()
    assert BRIDGE_FILES[0] in capsys.readouterr().out
    assert [p.name for p in copy_bridge(tmp_path / "again")] == list(BRIDGE_FILES)
