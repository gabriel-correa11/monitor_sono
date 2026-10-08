"""RF06 — Identificar eventos sonoros do escopo (tipos a definir em 22/10)."""

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np


@dataclass
class EventoSonoro:
    inicio_s: float
    fim_s: float
    tipo: str
    nivel: float


def detectar_eventos_sonoros(
    janelas: Iterator[tuple[float, np.ndarray]],
) -> list[EventoSonoro]:
    raise NotImplementedError("RF06: aguardando definição do escopo (22/10)")
