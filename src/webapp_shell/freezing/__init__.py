"""Freezing a program into one folder with PyInstaller: the project writes a `FreezePlan`, the library does the rest.

    python -m webapp_shell freeze acme_freeze:PLAN --path . qt webview

Needs `pyinstaller` (`pip install "webapp-shell[freeze]"`); only `webapp_shell.freezing.spec` imports it.
"""

from .plan import DataFolder, FreezePlan

__all__ = ["DataFolder", "FreezePlan"]
