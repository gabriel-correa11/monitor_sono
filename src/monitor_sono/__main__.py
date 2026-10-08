"""RF10, RNF07 — Linha de comando: python -m monitor_sono [sessoes]."""

import argparse

from monitor_sono import __version__, config
from monitor_sono.registro import banco


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="monitor_sono",
        description=config.AVISO_NAO_DIAGNOSTICO,
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="comando")
    sub.add_parser("sessoes", help="lista as sessões registradas (RF10)")
    args = parser.parse_args()

    if args.comando == "sessoes":
        sessoes = banco.listar_sessoes()
        if not sessoes:
            print("Nenhuma sessão registrada.")
        for s in sessoes:
            print(f"{s['id']}\t{s['inicio']}\t{s['fim'] or '(em andamento)'}\t{s['origem']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
