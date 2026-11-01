from webapp_shell.native.zoom import MacZoom, WebviewZoom, ZoomSurface
from webapp_shell.native.zoom_range import MAX_ZOOM, MIN_ZOOM, clamp


class FakeWebView:
    def __init__(self, fail=False):
        self.zoom, self.fail = None, fail

    def setPageZoom_(self, factor):
        if self.fail:
            raise AttributeError("no such selector")
        self.zoom = factor


class FakeWindow:
    """What pywebview gives on macOS: `native` is the window and its content view is the web view."""

    def __init__(self, view):
        self.native = type("Native", (), {"contentView": lambda _self: view})()


def immediately(call):
    call()


def test_clamp_keeps_a_factor_in_range():
    assert clamp(10) == MAX_ZOOM and clamp(0.1) == MIN_ZOOM and clamp(1.25) == 1.25


def test_the_mac_zoom_sets_the_page_zoom_of_the_content_view():
    view = FakeWebView()
    assert MacZoom(on_main=immediately).apply(FakeWindow(view), 1.5) is True
    assert view.zoom == 1.5


def test_a_zoom_that_fails_on_the_main_thread_is_reported_not_swallowed():
    assert MacZoom(on_main=immediately).apply(FakeWindow(FakeWebView(fail=True)), 1.5) is False


def test_a_main_thread_that_never_answers_is_reported(monkeypatch):
    monkeypatch.setattr("webapp_shell.native.zoom.MAIN_THREAD_WAIT", 0.05)
    assert MacZoom(on_main=lambda call: None).apply(FakeWindow(FakeWebView()), 1.5) is False


def test_the_zoom_goes_to_the_surface_of_this_system():
    class Always(ZoomSurface):
        def apply(self, window, factor):
            return True

    assert WebviewZoom(Always()).apply(object(), 1.5) is True  # type: ignore[arg-type]


def test_the_dock_icon_is_only_for_macos_and_needs_a_file(monkeypatch, tmp_path):
    from webapp_shell.native.webview_icon import WebviewIcon

    assert WebviewIcon(None).apply() is False
    monkeypatch.setattr("sys.platform", "win32")
    assert WebviewIcon(tmp_path / "icon.png").apply() is False
