"""RF09 — Classificar comportamentos identificados conforme critérios estabelecidos."""

from monitor_sono import config
from monitor_sono.classificacao.periodos import identificar_periodos, juntar_segundos
from monitor_sono.tipos import DeteccaoMovimento, EstadoOlhos, Intervalo, Visibilidade


def periodos_maior_atividade(movimentos: list[DeteccaoMovimento]) -> list[Intervalo]:
    """RN04. Movimentos frequentes viram períodos de maior atividade motora.

    Um instante entra quando, nos config.JANELA_ATIVIDADE_S segundos anteriores, houve movimento em pelo
    menos config.MOVIMENTOS_FREQUENTES instantes analisados.
    """
    com_movimento = sorted(m.segundo for m in movimentos if m.movimento)
    marcados: list[float] = []
    inicio_janela = 0
    for i, s in enumerate(com_movimento):
        while com_movimento[inicio_janela] < s - config.JANELA_ATIVIDADE_S:
            inicio_janela += 1
        if i - inicio_janela + 1 >= config.MOVIMENTOS_FREQUENTES:
            marcados.append(s)
    return juntar_segundos(marcados, "maior_atividade_motora", config.JUNCAO_MOVIMENTO_S)


def classificar_comportamentos(
    movimentos: list[DeteccaoMovimento],
    visibilidades: list[Visibilidade],
    olhos: list[EstadoOlhos] | None = None,
) -> list[Intervalo]:
    """RF09. Transforma as detecções em intervalos dos comportamentos de config.COMPORTAMENTOS (RN08).

    - movimento_corporal e ausencia_movimento: períodos do RF11;
    - mudanca_posicao: cada mudança brusca de posição (RN05);
    - maior_atividade_motora: movimentos frequentes (RN04);
    - visibilidade_insuficiente: trechos em que a câmera não observa a cena (RF15);
    - olhos_abertos e olhos_fechados: trechos com o mesmo estado dos olhos (RF05), quando houver essa detecção.
    """
    intervalos = identificar_periodos(movimentos, visibilidades)
    intervalos += [
        Intervalo("mudanca_posicao", m.segundo, m.segundo) for m in movimentos if m.mudanca_posicao
    ]
    intervalos += periodos_maior_atividade(movimentos)
    intervalos += juntar_segundos(
        [v.segundo for v in visibilidades if not v.adequada],
        "visibilidade_insuficiente",
        config.JUNCAO_MOVIMENTO_S,
    )
    for estado, tipo in (("abertos", "olhos_abertos"), ("fechados", "olhos_fechados")):
        intervalos += juntar_segundos(
            [o.segundo for o in (olhos or []) if o.estado == estado], tipo, config.JUNCAO_MOVIMENTO_S
        )
    return sorted(intervalos, key=lambda i: (i.inicio, i.tipo))
