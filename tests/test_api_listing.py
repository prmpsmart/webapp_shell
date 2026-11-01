import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_the_api_listing_is_current():
    """`docs/API.md` is generated from the source; regenerate it with `python tools/api_listing.py`."""
    result = subprocess.run([sys.executable, str(ROOT / "tools" / "api_listing.py"), "--check"], check=False)
    assert result.returncode == 0, "docs/API.md is out of date: run python tools/api_listing.py"


def test_every_public_name_is_in_the_listing_and_nothing_else():
    listing = (ROOT / "docs" / "API.md").read_text(encoding="utf-8")
    entries = [line for line in listing.splitlines() if line.startswith("- `")]
    assert len(entries) == int(listing.split("Public names: ")[1].split(".")[0])
