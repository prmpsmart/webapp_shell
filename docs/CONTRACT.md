# The contract between the shell and a backend

The shell and a backend never share code at run time; they share a small contract, written once in `WireProtocol`
and `BackendSpec` and read by both sides, so it cannot drift.

## What the shell does

1. Picks a free port on `host` (127.0.0.1) and makes a token with `secrets.token_urlsafe(24)`.
2. Starts the backend as `python -m <BackendSpec.module>` (a frozen program runs itself with `--run-backend`) with
   `--port N`, `--frontend <dist>`, `--preferences-file <path>` (the names are `BackendSpec` fields), then
   `BackendSpec.arguments`, the source-only arguments (not when frozen) and the arguments of the project's switches
   that are on.
3. Hands the token over in the environment variable `WireProtocol.token_env` (a command line is visible to other
   users). The `--token` argument exists for tests only.
4. Polls `WireProtocol.health_path` until it answers 200, up to `ShellConfig.startup_timeout` (20 s).
5. Opens the window on `http://host:port/?<token_query>=<token>`: the token travels once, in the launch URL.
6. If the backend dies, a watchdog starts it again on the **same port and token** (so the open page reconnects by
   itself), at most 3 times within 120 s; then it shows the give-up sentence (see `TRANSLATING.md`).
7. On exit, terminates the backend (kills it after 5 s).

## What a backend must do

- Read the arguments with `add_launch_arguments` / `read_launch_arguments` (`webapp_shell.contract`).
- Answer `health_path` with 200 **without** a token (the shell has no cookie yet).
- Answer `version_path`, when the project has one, with a JSON object; running from the source, its `"version"` goes into the window title for the team.
- Require the token on everything under `api_prefix`, in the header `token_header` or the cookie `token_cookie`.
- Turn the `token_query` value of the first page request into the cookie, then redirect to the page without it.
- Serve the compiled frontend from `--frontend` (static files, `index.html` at `/`).
- Refuse requests from other origins (`OriginPolicy`) and sockets without a valid token (close code `4401`).

With Starlette all of it is one line each: `TokenGuard` (HTTP), `WebSocketGuard` (sockets), `TokenValidator`,
`OriginPolicy`. Any other framework implements the same checks with `TokenValidator`, which has no dependency.

## Names

`WireProtocol.for_slug("acme")` gives: header `x-acme-token`, cookie `acme_token`, query `token`, environment
variable `ACME_TOKEN`, prefix `/api`, health `/api/health`, version `/api/version`. A project may write its own.

## The page talks to the shell, never the backend to the shell

A native feature travels page → bridge → shell → page → HTTP → backend. The backend only ever sees the path of a chosen
file as ordinary request data. See the site's pages for each feature.
