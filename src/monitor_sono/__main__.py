"""RNF12 — Linha de comando: python -m monitor_sono."""

import argparse

from monitor_sono import __version__, config


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="monitor_sono",
        description=config.AVISO_NAO_DIAGNOSTICO,
    )
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args()
    parser.print_help()


if __name__ == "__main__":
    main()
