"""RF15 — Sinalizar quando a câmera não conseguir observar adequadamente o indivíduo.

A visibilidade é avaliada pela imagem (escura demais ou sem contraste: câmera tampada ou fora de foco) e
pela presença (RF03): sem rosto nem movimento por config.JANELA_PRESENCA_S, a pessoa pode estar fora do
enquadramento ou a câmera pode estar virada ("sem_presenca").
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


def considerar_presenca(visibilidade: Visibilidade, presente: bool) -> Visibilidade:
    """RF15, RF03, RN07. Sem presença, a câmera não observa o indivíduo: visibilidade insuficiente.

    Uma imagem já ruim (escura, sem contraste) mantém o motivo original.
    """
    if visibilidade.adequada and not presente:
        return Visibilidade(visibilidade.segundo, False, "sem_presenca")
    return visibilidade


def verificar_visibilidade(quadro: np.ndarray) -> bool:
    """RF15. Retorna True se a câmera observa adequadamente, False caso contrário. RN07."""
    return avaliar_visibilidade(quadro, 0.0).adequada
