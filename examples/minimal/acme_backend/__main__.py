"""`python -m acme_backend --port N --frontend DIR`: started by the shell, never by hand."""

import argparse

from webapp_shell.contract import add_launch_arguments, read_launch_arguments

from . import WIRE, serve
from .spec import BACKEND


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    add_launch_arguments(parser, BACKEND)
    launch = read_launch_arguments(parser, parser.parse_args(argv), WIRE)
    serve(launch.token, launch.frontend, launch.port, launch.host)


if __name__ == "__main__":
    main()
