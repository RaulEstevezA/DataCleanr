"""Entry point: `python -m datacleanr` or the `datacleanr` command."""

import sys


def main() -> None:
    from .ui.app import run

    sys.exit(run())


if __name__ == "__main__":
    main()
