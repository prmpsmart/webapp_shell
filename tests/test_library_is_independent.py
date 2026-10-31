"""The library knows nothing about the project that uses it."""

from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "src" / "webapp_shell"
PROJECT_NAMES = ("pixeval", "piXeval", "Pixeval", "aescolan")


def test_no_project_name_appears_in_the_library():
    found = [
        f"{path.name}: {name}"
        for path in SOURCE.rglob("*.py")
        for name in PROJECT_NAMES
        if name in path.read_text(encoding="utf-8")
    ]
    assert found == []
