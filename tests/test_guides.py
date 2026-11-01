import ast
import re
from pathlib import Path

import pytest

import webapp_shell
from webapp_shell import contract
from webapp_shell.contract import guard

ROOT = Path(__file__).resolve().parents[1]
GUIDES = sorted([ROOT / "README.md", *(ROOT / "docs").glob("*.md")])
PUBLIC = {
    "webapp_shell": set(webapp_shell.__all__),
    "webapp_shell.contract": set(contract.__all__),
    "webapp_shell.contract.guard": set(guard.__all__),
}


def python_blocks(path: Path) -> list[str]:
    return re.findall(r"```python\n(.*?)```", path.read_text(encoding="utf-8"), flags=re.DOTALL)


@pytest.mark.parametrize("path", GUIDES, ids=lambda path: path.name)
def test_every_python_sample_is_valid_python(path):
    for block in python_blocks(path):
        ast.parse(block)


@pytest.mark.parametrize("path", GUIDES, ids=lambda path: path.name)
def test_names_a_guide_imports_from_the_library_exist(path):
    for block in python_blocks(path):
        for node in ast.walk(ast.parse(block)):
            if isinstance(node, ast.ImportFrom) and node.module in PUBLIC:
                for alias in node.names:
                    assert alias.name in PUBLIC[node.module], (
                        f"{path.name} imports {alias.name}, which the library does not export"
                    )


def library_imports(source: str) -> list[str]:
    """Every module of the library a source file imports from (`from webapp_shell.x import y`, `import webapp_shell.x`)."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "webapp_shell":
            found.append(node.module)
        elif isinstance(node, ast.Import):
            found += [alias.name for alias in node.names if alias.name.split(".")[0] == "webapp_shell"]
    return found


@pytest.mark.parametrize("path", sorted((ROOT / "examples").rglob("*.py")), ids=lambda path: path.name)
def test_the_examples_use_only_the_public_modules(path):
    """What an example shows is what a project may do: it reaches nothing that `docs/API.md` does not list."""
    if "node_modules" in path.parts:
        return
    for module in library_imports(path.read_text(encoding="utf-8")):
        assert module in PUBLIC, f"{path.name} imports {module}, which is not public"
