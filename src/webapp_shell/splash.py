"""The two pages the shell shows itself, before and instead of the frontend. Deliberately text-light: the real
user interface (and its translations) belongs to the frontend."""

import base64
from html import escape
from pathlib import Path

from .preferences import BootColors

# A soft two-glow gradient over the base colour; a project's frontend can use the same geometry for its hero.
HERO_GRADIENT = (
    "radial-gradient(900px 600px at 20% 10%, {glow_a} 0, transparent 60%), "
    "radial-gradient(700px 500px at 90% 90%, {glow_b} 0, transparent 55%), {base}"
)

_PAGE = """<!doctype html><meta charset="utf-8"><title>%(title)s</title>
<style>
  html,body{height:100%%;margin:0}
  body{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;
       font:15px -apple-system,'Segoe UI',system-ui,sans-serif;background:%(background)s;color:#fff}
  .mark{width:64px;height:64px;image-rendering:auto}
  .spin{width:26px;height:26px;border:3px solid rgba(255,255,255,.25);border-top-color:#fff;border-radius:50%%;animation:s 0.9s linear infinite}
  @keyframes s{to{transform:rotate(360deg)}}
  .err{max-width:520px;text-align:center;color:#ffb4ab}
</style>
%(icon)s%(body)s"""


class SplashPage:
    def __init__(self, title: str, icon_png: Path | None, colors: BootColors):
        self._title = escape(title)
        self._icon_png = icon_png
        self._colors = colors

    def loading(self) -> str:
        return self._render('<div class="spin"></div>')

    def error(self, message: str) -> str:
        return self._render(f'<div class="err">{escape(message)}</div>')

    def _render(self, body: str) -> str:
        return _PAGE % {"title": self._title, "background": self._background(), "icon": self._icon_html(), "body": body}

    def _background(self) -> str:
        c = self._colors
        return HERO_GRADIENT.format(base=c.base, glow_a=c.glow_a, glow_b=c.glow_b)

    def _icon_html(self) -> str:
        if not self._icon_png:
            return ""
        data = base64.b64encode(self._icon_png.read_bytes()).decode()
        return f'<img class="mark" alt="" src="data:image/png;base64,{data}">'
