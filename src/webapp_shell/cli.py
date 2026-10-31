"""The command line every project gets: `<program> [webview|qt] [--smoke] [--splash-seconds N] [project switches]`."""

import argparse
import importlib
import sys

from . import registry
from .backend_process import BackendProcess
from .config import ShellConfig
from .enums import ShellKind
from .installation import Installation, ensure_standard_streams
from .library_check import LibraryCheck
from .preferences import ShellPreferences
from .settings import Settings


def build_parser(config: ShellConfig) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"Open {config.identity.name} in one of the desktop shells.")
    parser.add_argument(
        "shell", type=ShellKind, choices=registry.kinds(), nargs="?", default=ShellKind.WEBVIEW,
        help="the window toolkit (default: webview)",
    )  # fmt: skip
    parser.add_argument("--smoke", action="store_true", help="headless check: load the page, print the result, exit")
    parser.add_argument(
        "--splash-seconds",
        type=float,
        default=None,
        help="how long the splash stays at least (default: the setting; 0 with --smoke)",
    )
    for flag in config.backend.flags:
        parser.add_argument(flag.name, action="store_true", help=flag.help)
    return parser


def run_backend(config: ShellConfig, argv: list[str]) -> int:
    """A frozen program starts its backend by running itself with `Installation.RUN_BACKEND`."""
    importlib.import_module(f"{config.backend.module}.__main__").main(argv)
    return 0


def check_libraries(config: ShellConfig) -> int:
    problems = LibraryCheck(config.required_libraries).problems()
    print("\n".join(map(str, problems)) or "all libraries are present")
    return 1 if problems else 0


def run(config: ShellConfig, argv: list[str] | None = None, installation: Installation | None = None) -> int:
    """The entry point of a project's program: its launcher builds a `ShellConfig` and calls this."""
    ensure_standard_streams()
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == [Installation.RUN_BACKEND]:
        return run_backend(config, argv[1:])
    if argv[:1] == [Installation.CHECK_LIBRARIES]:
        return check_libraries(config)
    args = build_parser(config).parse_args(argv)

    # a headless check never reads or writes the user's own preferences file
    preferences = ShellPreferences(None if args.smoke else config.identity.shell_preferences_path)
    splash = 0.0 if args.smoke and args.splash_seconds is None else args.splash_seconds
    settings = Settings.of(config, preferences, installation, splash_seconds=splash)
    flags = tuple(flag for flag in config.backend.flags if getattr(args, flag.name.lstrip("-").replace("-", "_")))
    shell = registry.shell_class(args.shell)(
        settings,
        BackendProcess(settings, keeps_preferences=not args.smoke, flags=flags),
        preferences=preferences,
        smoke=args.smoke,
    )
    return shell.run()
