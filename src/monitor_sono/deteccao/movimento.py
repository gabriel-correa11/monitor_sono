"""RF05 — Identificar movimentos durante a sessão."""

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np


@dataclass
class Movimento:
    inicio_s: float
    fim_s: float
    intensidade: float


def detectar_movimentos(
    quadros: Iterator[tuple[float, np.ndarray]],
) -> list[Movimento]:
    raise NotImplementedError("RF05: implementar até 22/10")
