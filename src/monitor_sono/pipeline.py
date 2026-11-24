"""Pipeline: liga captura → detecção → classificação → registro (RF01 a RF12, RF15).

É o único módulo que importa captura, deteccao, classificacao e registro juntos. Roda em processo próprio,
separado do dashboard: python -m monitor_sono analisar <fonte>.

A captura entrega o quadro na resolução original. Movimento e visibilidade usam uma cópia reduzida para
config.RESOLUCAO_ANALISE (como antes); rosto e olhos usam o quadro original, que tem detalhe suficiente.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

import cv2

from monitor_sono import config
from monitor_sono.captura.video import capturar_quadros
from monitor_sono.classificacao.comportamentos import classificar_comportamentos
from monitor_sono.classificacao.estados import estimar_estados
from monitor_sono.classificacao.periodos import juntar_segundos
from monitor_sono.deteccao.cabeca import AcompanhamentoCabeca
from monitor_sono.deteccao.movimento import analisar_movimento
from monitor_sono.deteccao.olhos import AcompanhamentoOlhos
from monitor_sono.deteccao.presenca import AcompanhamentoPresenca
from monitor_sono.deteccao.rosto import detectar_rosto
from monitor_sono.deteccao.visibilidade import avaliar_visibilidade, considerar_presenca
from monitor_sono.registro import banco
from monitor_sono.tipos import DeteccaoMovimento, EstadoEstimado, EstadoOlhos, Intervalo, Rosto, Visibilidade


@dataclass
class Resultado:
    """Resumo de uma análise, para mostrar no terminal."""

    sessao_id: int
    duracao_s: float
    quadros: int
    comportamentos: list[Intervalo] = field(default_factory=list)
    estados: list[EstadoEstimado] = field(default_factory=list)
    quadros_com_rosto: int = 0  # RF04
    quadros_olhos_determinaveis: int = 0  # RF05: olhos "abertos" ou "fechados"


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
    - Se a captura falhar (ex.: fonte que não abre), a sessão criada é excluída e o erro é repassado.
    """
    inicio = (inicio or datetime.now()).replace(microsecond=0)
    sessao_id = banco.criar_sessao(inicio, caminho_banco)

    movimentos: list[DeteccaoMovimento] = []
    visibilidades: list[Visibilidade] = []
    olhos: list[EstadoOlhos] = []
    segundos_cabeca: list[float] = []
    acompanha_olhos = AcompanhamentoOlhos()
    acompanha_cabeca = AcompanhamentoCabeca()
    acompanha_presenca = AcompanhamentoPresenca()
    anterior = None
    rosto_anterior: Rosto | None = None
    ultimo = 0.0
    quadros = quadros_com_rosto = 0
    try:
        for segundo, original in capturar_quadros(fonte, config.QUADROS_POR_SEGUNDO_ANALISE, resolucao=None):
            quadro = cv2.resize(original, config.RESOLUCAO_ANALISE)  # RF07, RF15: mesma redução de antes
            movimento = analisar_movimento(anterior, quadro, segundo) if anterior is not None else None
            if movimento is not None:
                movimentos.append(movimento)

            rosto = detectar_rosto(original, rosto_anterior)  # RF04
            quadros_com_rosto += rosto is not None
            olhos.append(acompanha_olhos.avaliar(original, rosto, segundo))  # RF05, RN06
            if acompanha_cabeca.atualizar(rosto):  # RF06
                segundos_cabeca.append(segundo)

            presente = acompanha_presenca.atualizar(  # RF03
                segundo, rosto is not None, movimento is not None and movimento.movimento
            )
            visibilidades.append(considerar_presenca(avaliar_visibilidade(quadro, segundo), presente))  # RF15

            anterior, rosto_anterior, ultimo = quadro, rosto, segundo
            quadros += 1
            if ao_progredir:
                ao_progredir(segundo)
    except KeyboardInterrupt:
        pass
    except Exception:
        # RF01: a análise falhou antes de gravar qualquer resultado (ex.: fonte que não abre). A sessão
        # vazia é desfeita para não ficar no banco sem horário de encerramento.
        banco.excluir_sessao(sessao_id, caminho_banco)
        raise

    comportamentos = classificar_comportamentos(movimentos, visibilidades, olhos)
    comportamentos += juntar_segundos(segundos_cabeca, "movimento_cabeca", config.JUNCAO_MOVIMENTO_S)  # RF06
    comportamentos.sort(key=lambda i: (i.inicio, i.tipo))
    estados = estimar_estados(olhos, comportamentos, 0.0, ultimo)

    def hora(segundos: float) -> datetime:
        return inicio + timedelta(seconds=round(segundos))

    for c in comportamentos:
        banco.registrar_comportamento(sessao_id, c.tipo, hora(c.inicio), hora(c.fim), caminho_banco)
    for e in estados:
        banco.registrar_estado(sessao_id, e.estado, hora(e.inicio), hora(e.fim), e.confiavel, caminho_banco)
    banco.finalizar_sessao(sessao_id, hora(ultimo), caminho_banco)

    determinaveis = sum(o.estado in ("abertos", "fechados") for o in olhos)
    return Resultado(sessao_id, ultimo, quadros, comportamentos, estados, quadros_com_rosto, determinaveis)
