"""Looks inside a finished build and fails when it holds something it must not, or lacks something it needs."""

from dataclasses import dataclass
from pathlib import Path

from .plan import FreezePlan
from .profile import ShellProfile


@dataclass(frozen=True)
class Finding:
    path: str
    problem: str


class BuildVerifier:
    """`folder` is the program's folder (the one that is handed over for installing)."""

    def __init__(self, folder: Path, profile: ShellProfile, plan: FreezePlan):
        self.folder, self.profile, self.plan = Path(folder), profile, plan

    def findings(self) -> list[Finding]:
        return [*self._missing(), *self._forbidden()]

    def _inside(self) -> Path:
        """PyInstaller puts the bundled files in `_internal` from version 6, beside the executable before."""
        internal = self.folder / "_internal"
        return internal if internal.is_dir() else self.folder

    def _missing(self) -> list[Finding]:
        found = [Finding(name, "missing") for name in self.plan.required if not (self._inside() / name).exists()]
        if not any((self.folder / f"{self.plan.product}{suffix}").exists() for suffix in ("", ".exe")):
            found.append(Finding(self.plan.product, "the executable is missing"))
        return found

    def _forbidden(self) -> list[Finding]:
        names = {name.lower() for name in self.profile.forbidden}
        found: list[Finding] = []
        for path in self.folder.rglob("*"):
            parts = {part.lower().split(".")[0] for part in path.relative_to(self.folder).parts}
            if parts & names:
                found.append(Finding(path.relative_to(self.folder).as_posix(), "belongs to the other shell"))
        return found
