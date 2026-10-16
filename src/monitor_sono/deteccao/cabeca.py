"""RF06 — Detectar movimentos da cabeça durante o monitoramento."""

import numpy as np


def detectar_movimento_cabeca(
    quadro_anterior: np.ndarray, quadro_atual: np.ndarray
) -> bool:
    """RF06. Retorna True se houve movimento da cabeça entre os quadros."""
    raise NotImplementedError("RF06: a implementar")
