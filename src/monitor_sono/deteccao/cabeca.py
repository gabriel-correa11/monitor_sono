"""RF06 — Detectar movimentos da cabeça durante o monitoramento.

Método: compara o rosto (RF04) de um quadro com o do quadro anterior. Há movimento da cabeça quando:
- o centro do rosto se desloca pelo menos config.DESLOCAMENTO_CABECA larguras de rosto, com as duas
  detecções na mesma orientação; ou
- a orientação muda (de frente para perfil ou o contrário) e a nova orientação se mantém por
  config.QUADROS_NOVA_ORIENTACAO quadros seguidos. O detector alterna entre frente e perfil no mesmo rosto
  parado; sem essa confirmação, a alternância viraria movimento falso.
Se os tamanhos forem muito diferentes (config.RAZAO_TAMANHO_ROSTO_MAX), é outra detecção, não movimento.
"""

from monitor_sono import config
from monitor_sono.deteccao.rosto import centro, razao_tamanho
from monitor_sono.tipos import Rosto


def detectar_movimento_cabeca(rosto_anterior: Rosto, rosto_atual: Rosto) -> bool:
    """RF06. True se o centro do rosto se deslocou o bastante entre dois quadros, na mesma orientação."""
    if rosto_anterior.frontal != rosto_atual.frontal:
        return False  # a caixa de frente e a de perfil não são comparáveis; a troca é tratada à parte
    if razao_tamanho(rosto_anterior, rosto_atual) > config.RAZAO_TAMANHO_ROSTO_MAX:
        return False
    (ax, ay), (bx, by) = centro(rosto_anterior), centro(rosto_atual)
    deslocamento = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
    largura = (rosto_anterior.largura + rosto_atual.largura) / 2
    return deslocamento >= config.DESLOCAMENTO_CABECA * largura


class AcompanhamentoCabeca:
    """RF06. Acompanha o rosto entre quadros e indica em quais houve movimento da cabeça.

    O rosto pode sumir por até config.FOLGA_ROSTO_QUADROS quadros seguidos: a comparação é feita com o último
    rosto visto. Depois disso, o acompanhamento reinicia e o rosto que reaparece não conta como movimento.
    """

    def __init__(self) -> None:
        self._reiniciar()

    def _reiniciar(self) -> None:
        self._anterior: Rosto | None = None
        self._perdidos = 0
        self._orientacao: bool | None = None  # orientação confirmada (True = de frente)
        self._seguidos_nova = 0  # quadros seguidos na orientação oposta à confirmada

    def atualizar(self, rosto: Rosto | None) -> bool:
        """RF06. Recebe o rosto do quadro atual (ou None) e devolve True se houve movimento da cabeça."""
        if rosto is None:
            self._perdidos += 1
            if self._perdidos > config.FOLGA_ROSTO_QUADROS:
                self._reiniciar()
            return False
        self._perdidos = 0

        movimento = False
        if self._anterior is not None:
            movimento = detectar_movimento_cabeca(self._anterior, rosto)

        if self._orientacao is None:
            self._orientacao = rosto.frontal
        elif rosto.frontal != self._orientacao:
            self._seguidos_nova += 1
            if self._seguidos_nova >= config.QUADROS_NOVA_ORIENTACAO:
                self._orientacao, self._seguidos_nova = rosto.frontal, 0
                movimento = True
        else:
            self._seguidos_nova = 0

        self._anterior = rosto
        return movimento
