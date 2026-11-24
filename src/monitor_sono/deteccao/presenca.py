"""RF03 — Identificar a presença de uma pessoa na área monitorada.

Regra: há presença se, nos últimos config.JANELA_PRESENCA_S segundos, houve rosto detectado (RF04) ou
movimento (RF07). A janela é longa de propósito: uma pessoa dormindo parada não gera movimento e muitas vezes
não mostra o rosto, e uma janela curta marcaria "sem presença" no meio do sono. No começo da sessão, antes de
passar uma janela inteira, a pessoa não é dada como ausente.
"""

from monitor_sono import config


def detectar_presenca(segundo: float, ultima_evidencia: float) -> bool:
    """RF03. True se a última evidência de pessoa (rosto ou movimento) está dentro da janela de presença.

    - ultima_evidencia: segundo do último rosto ou movimento; no começo da sessão, o segundo inicial.
    """
    return segundo - ultima_evidencia < config.JANELA_PRESENCA_S


class AcompanhamentoPresenca:
    """RF03. Guarda a última evidência de pessoa ao longo da sessão."""

    def __init__(self, inicio: float = 0.0) -> None:
        self._ultima_evidencia = inicio

    def atualizar(self, segundo: float, rosto: bool, movimento: bool) -> bool:
        """RF03. Registra o quadro atual e devolve se há presença."""
        if rosto or movimento:
            self._ultima_evidencia = segundo
        return detectar_presenca(segundo, self._ultima_evidencia)
