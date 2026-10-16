"""RF07 — Detectar movimentos corporais e mudanças de posição."""

import numpy as np


def detectar_movimento_corporal(
    quadro_anterior: np.ndarray, quadro_atual: np.ndarray
) -> bool:
    """RF07. Retorna True se houve movimento corporal entre os quadros."""
    raise NotImplementedError("RF07: a implementar")


def detectar_mudanca_posicao(
    quadro_anterior: np.ndarray, quadro_atual: np.ndarray
) -> bool:
    """RF07. Retorna True se houve mudança de posição entre os quadros."""
    raise NotImplementedError("RF07: a implementar")
