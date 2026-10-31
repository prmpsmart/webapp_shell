"""How the shell starts this backend. The launcher and the backend read the same object, so they cannot drift."""

from pathlib import Path

from webapp_shell import BackendSpec

from . import WIRE

HERE = Path(__file__).resolve().parent.parent

BACKEND = BackendSpec(
    module="docs_backend",
    wire=WIRE,
    frontend_dist=Path("frontend/dist"),
    package_dirs=(HERE,),
)
