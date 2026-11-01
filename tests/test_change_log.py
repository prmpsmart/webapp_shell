"""The change log of the current version is kept in the root; past versions live in change_logs/."""

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def project_version() -> str:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def test_the_root_change_log_is_about_the_current_version():
    title = (ROOT / "CHANGE_LOG.md").read_text(encoding="utf-8").splitlines()[0]
    assert title == f"# {project_version()}"


def test_past_versions_are_files_named_by_version():
    names = [path.stem for path in (ROOT / "change_logs").glob("*.md") if path.name != "README.md"]
    assert all(re.fullmatch(r"\d+\.\d+", name) for name in names), names
    assert project_version() not in names  # the current version is still in the root
