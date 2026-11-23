"""Pipeline: liga captura → detecção → classificação → registro (RF01, RF02, RF07 a RF12, RF15).

É o único módulo que importa captura, deteccao, classificacao e registro juntos. Roda em processo próprio,
separado do dashboard: python -m monitor_sono analisar <fonte>.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from monitor_sono import config
from monitor_sono.captura.video import capturar_quadros
from monitor_sono.classificacao.comportamentos import classificar_comportamentos
from monitor_sono.classificacao.estados import estimar_estados
from monitor_sono.deteccao.movimento import analisar_movimento
from monitor_sono.deteccao.visibilidade import avaliar_visibilidade
from monitor_sono.registro import banco
from monitor_sono.tipos import DeteccaoMovimento, EstadoEstimado, EstadoOlhos, Intervalo, Visibilidade


@dataclass
class Resultado:
    """Resumo de uma análise, para mostrar no terminal."""

    sessao_id: int
    duracao_s: float
    quadros: int
    comportamentos: list[Intervalo] = field(default_factory=list)
    estados: list[EstadoEstimado] = field(default_factory=list)


def analisar(
    fonte: int | str,
    inicio: datetime | None = None,
    caminho_banco: Path | None = None,
    ao_progredir: Callable[[float], None] | None = None,
) -> Resultado:
    """RF01 a RF12, RF15. Analisa uma câmera ou gravação e grava a sessão no banco.

    - inicio: data e hora real do início da gravação. Os eventos são gravados como inicio + segundo do
      quadro (RNF04). Sem valor, usa o momento atual.
    - Com câmera, a análise termina com Ctrl+C; o que foi capturado até ali é classificado e gravado.
    """
    inicio = (inicio or datetime.now()).replace(microsecond=0)
    sessao_id = banco.criar_sessao(inicio, caminho_banco)

    movimentos: list[DeteccaoMovimento] = []
    visibilidades: list[Visibilidade] = []
    anterior = None
    ultimo = 0.0
    quadros = 0
    try:
        for segundo, quadro in capturar_quadros(fonte, config.QUADROS_POR_SEGUNDO_ANALISE):
            visibilidades.append(avaliar_visibilidade(quadro, segundo))
            if anterior is not None:
                movimentos.append(analisar_movimento(anterior, quadro, segundo))
            anterior, ultimo = quadro, segundo
            quadros += 1
            if ao_progredir:
                ao_progredir(segundo)
    except KeyboardInterrupt:
        pass

    olhos: list[EstadoOlhos] = []  # RF05 não implementado nesta versão: estados ficam indeterminados (RN06)
    comportamentos = classificar_comportamentos(movimentos, visibilidades, olhos)
    estados = estimar_estados(olhos, comportamentos, 0.0, ultimo)

    def hora(segundos: float) -> datetime:
        return inicio + timedelta(seconds=round(segundos))

    for c in comportamentos:
        banco.registrar_comportamento(sessao_id, c.tipo, hora(c.inicio), hora(c.fim), caminho_banco)
    for e in estados:
        banco.registrar_estado(sessao_id, e.estado, hora(e.inicio), hora(e.fim), e.confiavel, caminho_banco)
    banco.finalizar_sessao(sessao_id, hora(ultimo), caminho_banco)

    return Resultado(sessao_id, ultimo, quadros, comportamentos, estados)
