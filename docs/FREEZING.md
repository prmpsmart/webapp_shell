# Freezing with PyInstaller

A frozen program is one executable. It has no `python -m`, so it starts its backend by running **itself** with
`--run-backend`; the library does this (`Installation.backend_command`). What the project must provide:

1. **The launcher** that builds the `ShellConfig` and calls `run(config)`. Nothing else is needed for the window.
2. **The backend package inside the bundle**, with `__main__.main(argv)`: `--run-backend` calls
   `<module>.__main__.main(argv)`.
3. **The compiled frontend** as data: the folder `BackendSpec.frontend_dist` (default `frontend/dist`) inside the
   bundle. The program finds it at `sys._MEIPASS/frontend/dist`.
4. **Hidden imports** for libraries the program loads lazily. List them in `ShellConfig.required_libraries`; then run
   the frozen program with `--check-libraries`: it imports each one and prints the problems (exit code 1), so the
   build finds a missing library, not the person using the program.
5. **A windowed build has no console.** `ensure_standard_streams()` (called by `run`) gives `sys.stdout` and
   `sys.stderr` a stream that discards text, because libraries ask a stream whether it is a terminal.
6. **The icon**: `.ico` for the Windows executable and window, `.png` for the others.

The library does not yet ship a ready PyInstaller spec; Pixeval's freeze profiles are the model.
