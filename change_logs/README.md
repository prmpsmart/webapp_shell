# Change logs of past versions

One file per released version, named `<version>.md` (`0.1.md`, `0.2.md`, …), saying what changed compared with the version before it.

The version being worked on is `CHANGE_LOG.md` in the root of the repository. When a new version starts, the root `CHANGE_LOG.md` is moved here as `<its version>.md` and a new `CHANGE_LOG.md` is begun for the new version (`tests/test_change_log.py` checks that its title is the version in `pyproject.toml`).
