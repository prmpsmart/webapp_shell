"""The backend's side of the contract with the shell.

The core (`tokens`, `launch`) needs no web framework. `guard` is a ready-made Starlette middleware (FastAPI apps are
Starlette apps) and is imported on its own: `from webapp_shell.contract.guard import TokenGuard`.
"""

from .launch import LaunchArguments, add_launch_arguments, read_launch_arguments
from .tokens import OriginPolicy, TokenValidator

__all__ = ["LaunchArguments", "OriginPolicy", "TokenValidator", "add_launch_arguments", "read_launch_arguments"]
