"""What a project says about its frozen build. The rest (the entry file, what each shell leaves out, the checks of the
finished folder) belongs to the library."""

import importlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataFolder:
    """A folder of the project that goes into the build as data (the compiled frontend, files the backend reads)."""

    source: Path
    target: str  # the folder inside the build, e.g. "frontend/dist"


@dataclass(frozen=True)
class FreezePlan:
    product: str  # the name of the folder and of the executable
    config: str  # "module:attribute": the `ShellConfig` (or a function returning one) the program runs with
    packages: tuple[str, ...]  # whose submodules are all collected: the project's own, and any that load by name
    data_folders: tuple[DataFolder, ...] = ()
    required: tuple[
        str, ...
    ] = ()  # files that must be in the finished build, relative to its data, e.g. "frontend/dist/index.html"
    collect_all: tuple[str, ...] = ()  # third-party packages with data files or native libraries
    runtime_hooks: tuple[Path, ...] = ()  # scripts that run before anything else in the frozen program
    excludes: tuple[str, ...] = ()  # more libraries to keep out, besides the developer tools the library leaves out
    icon: Path | None = None  # `.ico`, used for the Windows executable

    @classmethod
    def load(cls, reference: str) -> "FreezePlan":
        """The plan named `module:attribute`; the module must be importable (`--path`)."""
        module, _, name = reference.partition(":")
        plan = getattr(importlib.import_module(module), name)
        if not isinstance(plan, cls):
            raise TypeError(f"{reference} is not a FreezePlan")
        return plan
