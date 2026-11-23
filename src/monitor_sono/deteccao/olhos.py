"""RF05 — Identificar se os olhos estão abertos, fechados ou indeterminado."""

import numpy as np


def detectar_estado_olhos(
    quadro: np.ndarray, regiao_rosto: tuple[int, int, int, int]
) -> str:
    """RF05. Retorna 'abertos', 'fechados' ou 'indeterminado'. RN06."""
    raise NotImplementedError("RF05: não implementado nesta versão: o OpenCV 5 usado no projeto não traz detector de rosto pronto; exige decisão da equipe sobre modelo ou biblioteca")
