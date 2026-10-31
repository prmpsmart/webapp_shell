"""Imports every third-party library a project lists. Heavy libraries load lazily, so a frozen program that lacks
one would only fail when the person reaches the feature; this finds it when the program is built."""

import importlib
from dataclasses import dataclass


@dataclass(frozen=True)
class LibraryProblem:
    name: str
    detail: str

    def __str__(self) -> str:
        return f"{self.name}: {self.detail}"


class LibraryCheck:
    def __init__(self, libraries: tuple[str, ...]):
        self._libraries = libraries

    def problems(self) -> list[LibraryProblem]:
        found = []
        for name in self._libraries:
            try:
                importlib.import_module(name)
            except Exception as error:
                found.append(LibraryProblem(name, f"{type(error).__name__}: {error}"))
        return found
