"""RF05 — Identificar se os olhos estão abertos, fechados ou indeterminado."""

import numpy as np


def detectar_estado_olhos(
    quadro: np.ndarray, regiao_rosto: tuple[int, int, int, int]
) -> str:
    """RF05. Retorna 'abertos', 'fechados' ou 'indeterminado'. RN06."""
    raise NotImplementedError("RF05: a implementar")
