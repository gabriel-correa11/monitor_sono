"""RF04 — Receber áudio durante o monitoramento, quando disponível."""

from collections.abc import Iterator
from pathlib import Path

import numpy as np


def ler_audio(origem: str | Path) -> Iterator[tuple[float, np.ndarray]] | None:
    """Devolve (segundo, janela mono) ou None se não houver áudio."""
    raise NotImplementedError("RF04: implementar até 15/10")
