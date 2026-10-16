"""RF02 — Capturar imagens em tempo real da câmera durante a sessão."""

from collections.abc import Iterator

import numpy as np


def capturar_quadros(fonte: int | str, fps_analise: int) -> Iterator[tuple[float, np.ndarray]]:
    """RF02. Devolve (segundo, quadro) capturados em tempo real a fps_analise."""
    raise NotImplementedError("RF02: a implementar")
