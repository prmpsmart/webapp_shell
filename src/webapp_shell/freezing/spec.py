# pyright: basic
"""The only module that imports PyInstaller: runs inside a PyInstaller build and describes it from the `FreezePlan`."""

import os
import sys
from pathlib import Path
from typing import cast

from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.build_main import Analysis
from PyInstaller.config import CONF
from PyInstaller.utils.hooks import collect_all, collect_submodules

from ..enums import ShellKind
from .builder import KIND_VARIABLE, PLAN_VARIABLE
from .entry import entry_source
from .plan import FreezePlan
from .profile import PROFILES

LIBRARY_PACKAGES = ("webapp_shell",)  # the registry loads its shells by name, so every submodule of this shell is in


def freeze() -> None:
    plan = FreezePlan.load(os.environ[PLAN_VARIABLE])
    kind = ShellKind(os.environ[KIND_VARIABLE])
    profile = PROFILES[kind]

    workpath = Path(cast(str, CONF["workpath"]))  # PyInstaller types CONF loosely; it is a path
    entry = workpath / f"entry_{kind.value}.py"
    entry.parent.mkdir(parents=True, exist_ok=True)
    entry.write_text(entry_source(plan, kind), encoding="utf-8")

    datas = [(str(folder.source), folder.target) for folder in plan.data_folders]
    binaries = []
    hiddenimports = []
    for package in plan.collect_all:
        found = collect_all(package)
        datas += found[0]
        binaries += found[1]
        hiddenimports += found[2]
    for package in (*LIBRARY_PACKAGES, *plan.packages):
        hiddenimports += collect_submodules(package, filter=profile.wanted_module)

    analysis = Analysis(
        [str(entry)],
        pathex=[],
        binaries=binaries,
        datas=datas,
        hiddenimports=hiddenimports,
        hookspath=[],
        runtime_hooks=[str(hook) for hook in plan.runtime_hooks],
        excludes=[*profile.excludes, *plan.excludes],
        noarchive=False,
    )
    pyz = PYZ(analysis.pure)
    exe = EXE(
        pyz,
        analysis.scripts,
        [],
        exclude_binaries=True,
        name=plan.product,
        debug=False,
        strip=False,
        upx=False,
        console=False,
        icon=str(plan.icon) if plan.icon and sys.platform == "win32" else None,
    )
    COLLECT(exe, analysis.binaries, analysis.datas, strip=False, upx=False, name=plan.product)
