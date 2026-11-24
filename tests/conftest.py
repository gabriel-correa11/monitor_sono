"""Recursos comuns dos testes."""

import cv2
import numpy as np
import pytest

from monitor_sono.captura import carimbo as modulo_carimbo


def desenhar_carimbo(quadro: np.ndarray, texto: str, x: int = 10, y: int = 30) -> np.ndarray:
    """Escreve um carimbo "AAAA-MM-DD hh:mm:ss" sintético no canto do quadro, como faz a câmera.

    Os dígitos são desenhados a partir dos próprios modelos (nenhuma imagem de gravação é usada); traços e
    dois-pontos viram pequenos retângulos, que a leitura deve ignorar.
    """
    modelos = modulo_carimbo._carregar_modelos()
    largura_digito, altura_digito = 20, 32
    for caractere in texto:
        if caractere.isdigit():
            digito = (modelos[int(caractere)] > 0.5).astype(np.uint8) * 255
            regiao = quadro[y:y + altura_digito, x:x + largura_digito]
            regiao[digito > 0] = 255
            x += largura_digito + 4
        elif caractere == " ":
            x += 16
        else:  # "-" e ":"
            cv2.rectangle(quadro, (x, y + 14), (x + 5, y + 18), (255, 255, 255), -1)
            x += 10
    return quadro


@pytest.fixture
def carimbo():
    """Função que escreve um carimbo sintético num quadro."""
    return desenhar_carimbo
