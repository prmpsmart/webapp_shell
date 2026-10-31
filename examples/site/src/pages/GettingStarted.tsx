const INSTALL = `pip install webapp-shell            # pywebview window, built in
pip install "webapp-shell[qt]"       # Qt window as well
pip install "webapp-shell[backend]"  # Starlette helpers for the backend contract`

const LAUNCHER = `from pathlib import Path
from webapp_shell import AppIdentity, BackendSpec, BootColors, ShellConfig, WireProtocol, run

wire = WireProtocol.for_slug("acme")
config = ShellConfig(
    identity=AppIdentity(
        name="Acme Notes",
        slug="acme",
        storage_dir=Path.home() / ".acme-notes",
        boot_colors=BootColors(base="#102030", glow_a="#204060", glow_b="#4060a0"),
    ),
    backend=BackendSpec(module="acme_backend", wire=wire, frontend_dist=Path("frontend/dist")),
    source_root=Path(__file__).parent,
)

raise SystemExit(run(config))`

export function GettingStarted() {
  return (
    <>
      <h1>Getting started</h1>
      <p className="lead">Python 3.13 or newer. A backend, a compiled frontend and about fifteen lines.</p>
      <h2>Install</h2>
      <pre>
        <code>{INSTALL}</code>
      </pre>
      <h2>The launcher</h2>
      <p>
        The launcher describes the program once. <code>run(config)</code> gives it the command line: the
        window toolkit, the backend, the splash and the checks.
      </p>
      <pre>
        <code>{LAUNCHER}</code>
      </pre>
      <p>
        <code>examples/minimal</code> in the repository is this, complete and runnable.
      </p>
    </>
  )
}
