"""RF07 — Detectar movimentos corporais e mudanças de posição.

Método: diferença entre quadros consecutivos em escala de cinza ("actigrafia por vídeo"). Conta-se a fração
da imagem em que a intensidade mudou mais que config.LIMIAR_PIXEL. Quando quase a imagem inteira muda de uma
vez (luz acesa ou apagada), não conta como movimento.
"""

import cv2
import numpy as np

from monitor_sono import config
from monitor_sono.tipos import DeteccaoMovimento


def _cinza(quadro: np.ndarray) -> np.ndarray:
    """Converte para escala de cinza e desfoca levemente para reduzir o ruído da imagem."""
    cinza = cv2.cvtColor(quadro, cv2.COLOR_BGR2GRAY) if quadro.ndim == 3 else quadro
    k = config.DESFOQUE_MOVIMENTO
    return cv2.GaussianBlur(cinza, (k, k), 0)


def analisar_movimento(
    quadro_anterior: np.ndarray, quadro_atual: np.ndarray, segundo: float
) -> DeteccaoMovimento:
    """RF07, RN05. Compara dois quadros e devolve a fração alterada e o que ela representa."""
    anterior = _cinza(quadro_anterior)
    atual = _cinza(quadro_atual)
    diferenca = cv2.absdiff(anterior, atual)
    fracao = float((diferenca > config.LIMIAR_PIXEL).mean())
    if fracao >= config.LIMIAR_MUDANCA_ILUMINACAO:
        return DeteccaoMovimento(segundo, fracao, False, False, True)
    return DeteccaoMovimento(
        segundo=segundo,
        fracao_alterada=fracao,
        movimento=fracao >= config.LIMIAR_MOVIMENTO,
        mudanca_posicao=fracao >= config.LIMIAR_MUDANCA_POSICAO,
        mudanca_iluminacao=False,
    )


def detectar_movimento_corporal(quadro_anterior: np.ndarray, quadro_atual: np.ndarray) -> bool:
    """RF07. Retorna True se houve movimento corporal entre os quadros."""
    return analisar_movimento(quadro_anterior, quadro_atual, 0.0).movimento


def detectar_mudanca_posicao(quadro_anterior: np.ndarray, quadro_atual: np.ndarray) -> bool:
    """RF07, RN05. Retorna True se houve mudança brusca de posição entre os quadros."""
    return analisar_movimento(quadro_anterior, quadro_atual, 0.0).mudanca_posicao
