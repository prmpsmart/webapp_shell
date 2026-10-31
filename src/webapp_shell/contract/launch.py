"""The command line the shell starts a backend with, read by the backend: the port, the compiled frontend, the
preferences file and the token. The argument names come from the same `BackendSpec` the shell builds the command from,
so the two cannot drift."""

import argparse
from dataclasses import dataclass
from pathlib import Path

from ..backend import BackendSpec
from ..protocol import WireProtocol


@dataclass(frozen=True)
class LaunchArguments:
    port: int
    token: str
    frontend: Path | None
    preferences_file: Path | None
    host: str


def add_launch_arguments(parser: argparse.ArgumentParser, backend: BackendSpec) -> None:
    """Adds the standard arguments to a backend's parser. Read them back with `LaunchArguments.of(args, ...)`."""
    wire = backend.wire
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(backend.port_argument, dest="port", type=int, required=True)
    parser.add_argument(
        "--token",
        default=wire.token_from_environment(),
        help=f"the launch token; {wire.token_env} in the environment is safer, a command line is visible to other users",
    )
    parser.add_argument(backend.frontend_argument, dest="frontend", type=Path, default=None)
    if backend.preferences_argument:
        parser.add_argument(backend.preferences_argument, dest="preferences_file", type=Path, default=None)


def read_launch_arguments(
    parser: argparse.ArgumentParser, args: argparse.Namespace, wire: WireProtocol
) -> LaunchArguments:
    """Checks the token is there (the parser reports the error) and gathers the standard arguments."""
    if not args.token:
        parser.error(f"a token is needed: --token or {wire.token_env}")
    return LaunchArguments(
        port=args.port,
        token=args.token,
        frontend=args.frontend,
        preferences_file=getattr(args, "preferences_file", None),
        host=args.host,
    )
