"""RF10 — Estimar estados de sono a partir das características visuais detectadas.

Os estados são estimativas comportamentais, nunca estágios clínicos do sono (RN10, RNF12).
"""

from monitor_sono import config
from monitor_sono.classificacao.periodos import juntar_segundos
from monitor_sono.tipos import EstadoEstimado, EstadoOlhos, Intervalo


def _sobreposicao(a: Intervalo, b: Intervalo) -> tuple[float, float] | None:
    inicio, fim = max(a.inicio, b.inicio), min(a.fim, b.fim)
    return (inicio, fim) if fim > inicio else None


def _preencher(estados: list[EstadoEstimado], inicio: float, fim: float) -> list[EstadoEstimado]:
    """Cobre a sessão inteira: trechos sem estimativa ficam "indeterminado" (RN07) e iguais vizinhos se juntam."""
    resultado: list[EstadoEstimado] = []
    cursor = inicio
    for e in sorted(estados, key=lambda e: e.inicio):
        if e.inicio > cursor:
            resultado.append(EstadoEstimado("indeterminado", cursor, e.inicio, False))
        resultado.append(e)
        cursor = max(cursor, e.fim)
    if cursor < fim:
        resultado.append(EstadoEstimado("indeterminado", cursor, fim, False))

    juntos: list[EstadoEstimado] = []
    for e in resultado:
        if juntos and juntos[-1].estado == e.estado and juntos[-1].confiavel == e.confiavel:
            juntos[-1] = EstadoEstimado(e.estado, juntos[-1].inicio, max(juntos[-1].fim, e.fim), e.confiavel)
        else:
            juntos.append(e)
    return juntos


def estimar_estados(
    olhos: list[EstadoOlhos],
    periodos: list[Intervalo],
    inicio: float,
    fim: float,
) -> list[EstadoEstimado]:
    """RF10. Estima os estados ao longo da sessão, aplicando as regras de negócio.

    - RN01: olhos abertos por config.PERIODO_CONTINUO_OLHOS_S → "vigilia".
    - RN02 e RN03: olhos fechados por período contínuo **e**, no mesmo trecho, ausência de movimento por
      config.AUSENCIA_PROLONGADA_S → "possivel_sono". Nenhum dos dois sozinho é suficiente.
    - RN06 e RN07: sem informação sobre os olhos, o estado é "indeterminado" e não confiável (RNF09).
      Por isso, sem detecção ocular (RF05), a ausência de movimento sozinha nunca vira "possivel_sono".
    """
    estimados: list[EstadoEstimado] = []

    abertos = juntar_segundos(
        [o.segundo for o in olhos if o.estado == "abertos"], "olhos_abertos", config.JUNCAO_MOVIMENTO_S
    )
    for trecho in abertos:
        if trecho.fim - trecho.inicio >= config.PERIODO_CONTINUO_OLHOS_S:
            estimados.append(EstadoEstimado("vigilia", trecho.inicio, trecho.fim, True))

    fechados = juntar_segundos(
        [o.segundo for o in olhos if o.estado == "fechados"], "olhos_fechados", config.JUNCAO_MOVIMENTO_S
    )
    ausencias = [
        p for p in periodos
        if p.tipo == "ausencia_movimento" and p.fim - p.inicio >= config.AUSENCIA_PROLONGADA_S
    ]
    for trecho in fechados:
        if trecho.fim - trecho.inicio < config.PERIODO_CONTINUO_OLHOS_S:
            continue
        for ausencia in ausencias:
            comum = _sobreposicao(trecho, ausencia)
            if comum and comum[1] - comum[0] >= config.PERIODO_CONTINUO_OLHOS_S:
                estimados.append(EstadoEstimado("possivel_sono", comum[0], comum[1], True))

    return _preencher(estimados, inicio, fim)
