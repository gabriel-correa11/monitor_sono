"""RF11 — Identificar períodos de movimentação e de ausência de movimentação observável."""

from monitor_sono import config
from monitor_sono.tipos import DeteccaoMovimento, Intervalo, Visibilidade


def juntar_segundos(segundos: list[float], tipo: str, folga: float) -> list[Intervalo]:
    """Agrupa instantes próximos (separados por até `folga` segundos) em intervalos do mesmo tipo."""
    intervalos: list[Intervalo] = []
    for s in sorted(segundos):
        if intervalos and s - intervalos[-1].fim <= folga:
            ultimo = intervalos[-1]
            intervalos[-1] = Intervalo(tipo, ultimo.inicio, s)
        else:
            intervalos.append(Intervalo(tipo, s, s))
    return intervalos


def sem_informacao(
    movimentos: list[DeteccaoMovimento], visibilidades: list[Visibilidade]
) -> set[float]:
    """RN07. Instantes em que a imagem não permite observar: visibilidade ruim ou troca de iluminação."""
    ruins = {v.segundo for v in visibilidades if not v.adequada}
    ruins |= {m.segundo for m in movimentos if m.mudanca_iluminacao}
    return ruins


def identificar_periodos(
    movimentos: list[DeteccaoMovimento], visibilidades: list[Visibilidade]
) -> list[Intervalo]:
    """RF11, RN03, RN05. Períodos de movimentação ("movimento_corporal") e de ausência ("ausencia_movimento").

    Movimentos próximos (até config.JUNCAO_MOVIMENTO_S) formam um único período. A ausência de movimento é
    o trecho observável sem movimento entre eles; só entra se durar pelo menos config.AUSENCIA_MINIMA_S.
    Trechos sem informação visual (RN07) interrompem a ausência: não se afirma que não houve movimento
    quando a cena não podia ser observada. Isso vale também para uma interrupção da gravação (mais de
    config.LACUNA_GRAVACAO_S sem quadros).
    """
    ruins = sem_informacao(movimentos, visibilidades)
    ordenados = sorted(movimentos, key=lambda m: m.segundo)
    periodos = juntar_segundos(
        [m.segundo for m in ordenados if m.movimento and m.segundo not in ruins],
        "movimento_corporal",
        config.JUNCAO_MOVIMENTO_S,
    )

    ausencias: list[Intervalo] = []
    inicio: float | None = None
    ultimo: float | None = None
    anterior: float | None = None

    def fechar() -> None:
        if inicio is not None and ultimo - inicio >= config.AUSENCIA_MINIMA_S:
            ausencias.append(Intervalo("ausencia_movimento", inicio, ultimo))

    for m in ordenados:
        if anterior is not None and m.segundo - anterior > config.LACUNA_GRAVACAO_S:
            fechar()  # gravação interrompida: sem informação (RN07)
            inicio = ultimo = None
        anterior = m.segundo
        if not m.movimento and m.segundo not in ruins:
            inicio = m.segundo if inicio is None else inicio
            ultimo = m.segundo
            continue
        fechar()
        inicio = ultimo = None
    fechar()

    return sorted(periodos + ausencias, key=lambda i: i.inicio)
