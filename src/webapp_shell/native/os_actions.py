"""Operating-system actions both shells offer to the page. Inputs come from a web page, so they are validated."""

import subprocess
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlparse


class OsActions:
    ALLOWED_URL_SCHEMES = frozenset({"http", "https", "mailto"})

    def reveal(self, path: str) -> bool:
        """Show a file or folder in the file manager."""
        target = Path(path)
        if not target.exists():
            return False
        subprocess.Popen(self._reveal_command(target))
        return True

    def open_url(self, url: str) -> bool:
        """Open a web link in the default browser; other schemes (file:, javascript:, ...) are refused."""
        if urlparse(url).scheme.lower() not in self.ALLOWED_URL_SCHEMES:
            return False
        return webbrowser.open(url)

    @staticmethod
    def _reveal_command(target: Path) -> list[str]:
        if sys.platform == "darwin":
            return ["open", "-R", str(target)]
        if sys.platform == "win32":
            return ["explorer", f"/select,{target}"]
        return ["xdg-open", str(target if target.is_dir() else target.parent)]
