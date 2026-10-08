"""RF03 — Receber imagens da câmera durante a sessão."""

from collections.abc import Iterator
from pathlib import Path

import numpy as np


def ler_quadros(origem: str | Path, fps_analise: int) -> Iterator[tuple[float, np.ndarray]]:
    """Devolve (segundo, quadro em cinza) amostrado a fps_analise."""
    raise NotImplementedError("RF03: implementar até 15/10")
