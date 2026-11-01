import ast
import re
from pathlib import Path

import pytest

import webapp_shell
from webapp_shell import contract

ROOT = Path(__file__).resolve().parents[1]
GUIDES = sorted([ROOT / "README.md", *(ROOT / "docs").glob("*.md")])
EXPORTED = set(webapp_shell.__all__) | set(contract.__all__)


def python_blocks(path: Path) -> list[str]:
    return re.findall(r"```python\n(.*?)```", path.read_text(), flags=re.DOTALL)


@pytest.mark.parametrize("path", GUIDES, ids=lambda path: path.name)
def test_every_python_sample_is_valid_python(path):
    for block in python_blocks(path):
        ast.parse(block)


@pytest.mark.parametrize("path", GUIDES, ids=lambda path: path.name)
def test_names_a_guide_imports_from_the_library_exist(path):
    for block in python_blocks(path):
        for node in ast.walk(ast.parse(block)):
            if isinstance(node, ast.ImportFrom) and node.module in ("webapp_shell", "webapp_shell.contract"):
                for alias in node.names:
                    assert alias.name in EXPORTED, (
                        f"{path.name} imports {alias.name}, which the library does not export"
                    )
