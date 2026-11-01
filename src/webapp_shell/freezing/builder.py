"""Freezes the program for each shell and checks the result: `python -m webapp_shell freeze PLAN [qt] [webview]`.

Each shell is built into `<output>/<shell>/<product>/`: the other shell's libraries must not be in it, the files the
plan requires must be, and the frozen program's own `--check-libraries` must pass. Nothing here makes an installer.
"""

import argparse
import importlib.util
import os
import subprocess
import sys
from importlib import resources
from pathlib import Path

from ..enums import ShellKind
from ..installation import Installation
from .plan import FreezePlan
from .profile import PROFILES
from .verify import BuildVerifier, Finding

PLAN_VARIABLE = "WEBAPP_SHELL_FREEZE_PLAN"  # how the spec learns what to freeze: the plan's reference ...
KIND_VARIABLE = "WEBAPP_SHELL_FREEZE_KIND"  # ... and the shell


class Builder:
    def __init__(self, plan: FreezePlan, reference: str, paths: tuple[Path, ...], output: Path, work: Path):
        self.plan, self.reference, self.paths = plan, reference, paths
        self.output, self.work = output, work

    def folder(self, kind: ShellKind) -> Path:
        return self.output / kind.value / self.plan.product

    def _program(self, kind: ShellKind) -> Path:
        program = self.folder(kind) / self.plan.product
        return program.with_suffix(".exe") if sys.platform == "win32" else program

    def _library_problems(self, kind: ShellKind) -> str:
        """Runs the frozen program's own check: every library the program loads on first use must be in it."""
        done = subprocess.run([str(self._program(kind)), Installation.CHECK_LIBRARIES], capture_output=True, text=True)
        return "" if done.returncode == 0 else (done.stdout + done.stderr).strip()

    def _environment(self, kind: ShellKind) -> dict[str, str]:
        roots = [str(path.resolve()) for path in self.paths]
        python_path = os.pathsep.join([*roots, *filter(None, [os.environ.get("PYTHONPATH")])])
        return {**os.environ, "PYTHONPATH": python_path, PLAN_VARIABLE: self.reference, KIND_VARIABLE: kind.value}

    def build(self, kind: ShellKind) -> int:
        if importlib.util.find_spec("PyInstaller") is None:
            print('PyInstaller is not installed: pip install "webapp-shell[freeze]"')
            return 1
        spec = resources.files("webapp_shell.freezing") / "app.spec"
        with resources.as_file(spec) as spec_path:
            command = [
                sys.executable, "-m", "PyInstaller", str(spec_path), "--noconfirm", "--clean",
                "--distpath", str(self.output / kind.value), "--workpath", str(self.work / kind.value),
            ]  # fmt: skip
            done = subprocess.run(command, env=self._environment(kind))
        if done.returncode:
            return done.returncode
        findings = BuildVerifier(self.folder(kind), PROFILES[kind], self.plan).findings()
        if not findings and (problem := self._library_problems(kind)):
            findings = [Finding("libraries", problem)]
        for finding in findings:
            print(f"{kind.value}: {finding.path}: {finding.problem}")
        print(f"{kind.value}: {self.folder(kind)} " + ("is not right" if findings else "checked"))
        return 1 if findings else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m webapp_shell freeze", description=(__doc__ or "").splitlines()[0])
    parser.add_argument("plan", help="module:attribute of the project's FreezePlan")
    parser.add_argument("shells", nargs="*", type=ShellKind, default=list(PROFILES), help="default: every shell")
    parser.add_argument(
        "--path", type=Path, action="append", default=[], help="a folder to import the project from (repeatable)"
    )
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--work", type=Path, default=Path("build"))
    args = parser.parse_args(argv)
    for path in args.path:
        sys.path.insert(0, str(path.resolve()))
    builder = Builder(FreezePlan.load(args.plan), args.plan, tuple(args.path), args.output, args.work)
    return max(builder.build(kind) for kind in args.shells)
