"""How Acme Notes is frozen: `python -m webapp_shell freeze freeze_plan:PLAN --path . webview` (from this folder)."""

from pathlib import Path

from webapp_shell.freezing import DataFolder, FreezePlan

HERE = Path(__file__).resolve().parent

PLAN = FreezePlan(
    product="AcmeNotes",
    config="app:config",  # the ShellConfig of app.py
    packages=("acme_backend", "uvicorn"),  # uvicorn loads its protocol and loop modules by name
    data_folders=(DataFolder(HERE / "frontend" / "dist", "frontend/dist"),),
    required=("frontend/dist/index.html",),
)
