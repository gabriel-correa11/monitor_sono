"""RF15 — Sinalizar quando a câmera não conseguir observar adequadamente o indivíduo.

Nesta versão a visibilidade é avaliada pela imagem: escura demais ou sem contraste (câmera tampada ou
fora de foco). Rosto ou corpo fora do enquadramento dependem da detecção de rosto e presença (RF03, RF04),
ainda não implementadas.
"""

import cv2
import numpy as np

from monitor_sono import config
from monitor_sono.tipos import Visibilidade


def avaliar_visibilidade(quadro: np.ndarray, segundo: float) -> Visibilidade:
    """RF15, RN07. Indica se a imagem permite observar a cena e, se não, por quê."""
    cinza = cv2.cvtColor(quadro, cv2.COLOR_BGR2GRAY) if quadro.ndim == 3 else quadro
    if float(cinza.mean()) < config.BRILHO_MINIMO:
        return Visibilidade(segundo, False, "escura")
    if float(cinza.std()) < config.CONTRASTE_MINIMO:
        return Visibilidade(segundo, False, "sem_contraste")
    return Visibilidade(segundo, True, "ok")


def verificar_visibilidade(quadro: np.ndarray) -> bool:
    """RF15. Retorna True se a câmera observa adequadamente, False caso contrário. RN07."""
    return avaliar_visibilidade(quadro, 0.0).adequada
