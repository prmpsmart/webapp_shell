"""`python -m webapp_shell bridge --out DIR`: copies the page-side bridge (one `.js` file and its `.d.ts`) into a frontend."""

import argparse
import shutil
import sys
from importlib import resources
from pathlib import Path

BRIDGE_FILES = ("webapp-shell-bridge.js", "webapp-shell-bridge.d.ts")


def copy_bridge(out: Path) -> list[Path]:
    """Copies the bridge files into `out` (created if needed) and returns where they went."""
    out.mkdir(parents=True, exist_ok=True)
    source = resources.files("webapp_shell") / "bridge"
    copied: list[Path] = []
    for name in BRIDGE_FILES:
        target = out / name
        with resources.as_file(source / name) as path:
            shutil.copyfile(path, target)
        copied.append(target)
    return copied


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m webapp_shell", description="webapp-shell tools")
    commands = parser.add_subparsers(dest="command", required=True)
    bridge = commands.add_parser("bridge", help="copy the page-side bridge into a frontend")
    bridge.add_argument("--out", type=Path, required=True, help="the folder to copy into, e.g. frontend/src")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    if args.command == "bridge":
        for path in copy_bridge(args.out):
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
