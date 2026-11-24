"""Linha de comando: python -m monitor_sono analisar <fonte>. RF01, RNF11, RNF12."""

import argparse
import sys
from collections import Counter
from datetime import datetime

from monitor_sono import __version__, config


def _progresso(segundo: float) -> None:
    if int(segundo) % 600 == 0:
        print(f"\r  {segundo / 60:.0f} min analisados...", end="", file=sys.stderr, flush=True)


def _analisar(args: argparse.Namespace) -> None:
    from monitor_sono import pipeline  # importa o OpenCV só quando for analisar

    if not args.autorizado:
        # RNF11: só tratar imagens com autorização da pessoa monitorada (LGPD).
        sys.exit(
            "RNF11: confirme que a pessoa monitorada assinou o termo de consentimento "
            "repetindo o comando com --autorizado."
        )
    fonte = int(args.fonte) if args.fonte.isdigit() else args.fonte
    inicio = datetime.strptime(args.inicio, "%Y-%m-%d %H:%M") if args.inicio else None

    print(config.AVISO_NAO_DIAGNOSTICO)
    print("Analisando... (com câmera, Ctrl+C encerra a sessão)")
    r = pipeline.analisar(fonte, inicio=inicio, ao_progredir=_progresso)

    tipos = Counter(c.tipo for c in r.comportamentos)
    tempo_estado = Counter()
    for e in r.estados:
        tempo_estado[e.estado] += e.fim - e.inicio
    print(f"\n\nSessão {r.sessao_id} gravada: {r.duracao_s / 60:.0f} min, {r.quadros} quadros analisados.")
    for tipo, qtd in sorted(tipos.items()):
        print(f"  {tipo}: {qtd}")
    for estado, seg in tempo_estado.items():
        pct = 100 * seg / r.duracao_s if r.duracao_s else 0
        print(f"  estado {estado}: {pct:.0f}% do tempo")
    print("Abra o dashboard: streamlit run src/monitor_sono/dashboard/app.py")


def main() -> None:
    parser = argparse.ArgumentParser(prog="monitor_sono", description=config.AVISO_NAO_DIAGNOSTICO)
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="comando")

    p = sub.add_parser("analisar", help="analisa uma câmera ou gravação e grava a sessão no banco")
    p.add_argument("fonte", help="índice da câmera (ex.: 0) ou caminho da gravação")
    p.add_argument("--inicio", help='data e hora real do início da gravação, ex.: "2026-11-20 22:30"')
    p.add_argument("--autorizado", action="store_true",
                   help="confirma que a pessoa monitorada autorizou o tratamento das imagens (RNF11)")
    p.set_defaults(funcao=_analisar)

    args = parser.parse_args()
    if getattr(args, "funcao", None):
        args.funcao(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
