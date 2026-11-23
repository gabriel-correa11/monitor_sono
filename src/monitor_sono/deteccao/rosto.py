"""RF04 — Detectar a região facial do indivíduo, quando visível."""

import numpy as np


def detectar_rosto(quadro: np.ndarray) -> tuple[int, int, int, int] | None:
    """RF04. Retorna (x, y, largura, altura) do rosto ou None se não visível."""
    raise NotImplementedError("RF04: não implementado nesta versão: o OpenCV 5 usado no projeto não traz detector de rosto pronto; exige decisão da equipe sobre modelo ou biblioteca")
