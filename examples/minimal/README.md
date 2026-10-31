# Minimal example: Acme Notes

The smallest program that uses `webapp-shell`: a Starlette backend that follows the contract, a one-page frontend
(plain HTML and JavaScript, already "compiled"), and a launcher of fifteen lines.

    pip install "webapp-shell[backend]" uvicorn
    python app.py              # a window, in pywebview
    python app.py qt           # the same page in Qt (needs "webapp-shell[qt]")
    python app.py --smoke      # headless self-check; prints what the page rendered

How a native feature travels (choose a file): the page asks the shell (`bridge.pickFile()`), the shell opens the
dialog and returns the path to the page, and the page then tells the backend (`/api/describe?path=...`). The backend
never talks to the shell.

| File                       | Job                                                    |
| -------------------------- | ------------------------------------------------------ |
| `app.py`                   | The launcher: describe the program, call `run(config)` |
| `acme_backend/spec.py`     | How the shell starts the backend (read by both sides)  |
| `acme_backend/__init__.py` | The backend app with the token guard                   |
| `acme_backend/__main__.py` | Reads the launch arguments the shell passes            |
| `frontend/dist/`           | The page and `webapp-shell-bridge.js` (copied in)      |
