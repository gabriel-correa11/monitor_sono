"""RF04 — Detectar a região facial do indivíduo, quando visível.

Método: cascatas Haar do OpenCV 4.x (frontal e de perfil, dos dois lados), numa cópia em escala de cinza
reduzida para config.RESOLUCAO_ROSTO de largura e com histograma equalizado, porque a imagem infravermelha
costuma ter pouco contraste. Quando há um rosto no quadro anterior, a busca começa numa janela ao redor
dele, o que é bem mais rápido; só se nada for achado ali a imagem inteira é percorrida.
"""

from functools import cache

import cv2
import numpy as np

from monitor_sono import config
from monitor_sono.tipos import Rosto

_TAMANHO_MINIMO_HAAR = 24  # menor janela das cascatas do OpenCV (são treinadas em 20 a 24 px)


@cache
def _cascata(nome: str) -> cv2.CascadeClassifier:
    """Carrega uma cascata de cv2.data.haarcascades uma única vez."""
    cascata = cv2.CascadeClassifier(cv2.data.haarcascades + nome)
    if cascata.empty():
        raise RuntimeError(f"RF04: cascata {nome} não encontrada; o projeto exige OpenCV 4.x")
    return cascata


def cinza(quadro: np.ndarray) -> np.ndarray:
    """Converte para escala de cinza, se ainda não estiver."""
    return cv2.cvtColor(quadro, cv2.COLOR_BGR2GRAY) if quadro.ndim == 3 else quadro


def centro(rosto: Rosto) -> tuple[float, float]:
    """RF04, RF06. Centro da região do rosto."""
    return rosto.x + rosto.largura / 2, rosto.y + rosto.altura / 2


def razao_tamanho(a: Rosto, b: Rosto) -> float:
    """RF06. Razão entre a maior e a menor largura (1 = mesmo tamanho)."""
    return max(a.largura, b.largura) / max(1, min(a.largura, b.largura))


def mesmo_rosto(a: Rosto, b: Rosto) -> bool:
    """RF04, RF05. Indica se duas detecções são o mesmo rosto acompanhado: perto e de tamanho parecido."""
    (ax, ay), (bx, by) = centro(a), centro(b)
    distancia = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
    largura = max(a.largura, b.largura)
    return (
        distancia <= config.DISTANCIA_MESMO_ROSTO * largura
        and razao_tamanho(a, b) <= config.RAZAO_TAMANHO_ROSTO_MAX
    )


def _procurar(imagem: np.ndarray, minimo: int) -> list[tuple[int, int, int, int, bool]]:
    """Procura rostos de frente e, se não achar, de perfil (olhando para os dois lados)."""
    parametros = {
        "scaleFactor": config.FATOR_ESCALA_ROSTO,
        "minNeighbors": config.VIZINHOS_ROSTO,
        "minSize": (minimo, minimo),
    }
    frontais = _cascata("haarcascade_frontalface_default.xml").detectMultiScale(imagem, **parametros)
    if len(frontais):
        return [(int(x), int(y), int(w), int(h), True) for x, y, w, h in frontais]

    perfil = _cascata("haarcascade_profileface.xml")
    achados = [(int(x), int(y), int(w), int(h), False) for x, y, w, h in perfil.detectMultiScale(imagem, **parametros)]
    largura = imagem.shape[1]
    espelhada = cv2.flip(imagem, 1)  # a cascata de perfil só olha para um lado
    achados += [
        (int(largura - x - w), int(y), int(w), int(h), False)
        for x, y, w, h in perfil.detectMultiScale(espelhada, **parametros)
    ]
    return achados


def detectar_rosto(quadro: np.ndarray, anterior: Rosto | None = None) -> Rosto | None:
    """RF04. Devolve a região do maior rosto visível (em px do quadro recebido) ou None.

    - quadro: imagem BGR ou em cinza, de preferência na resolução original da câmera.
    - anterior: rosto do quadro anterior, se houver; a busca começa ao redor dele.
    """
    original = cinza(quadro)
    altura, largura = original.shape[:2]
    escala = min(1.0, config.RESOLUCAO_ROSTO / largura)
    reduzida = (
        cv2.resize(original, None, fx=escala, fy=escala, interpolation=cv2.INTER_AREA)
        if escala < 1.0 else original
    )
    reduzida = cv2.equalizeHist(reduzida)
    minimo = max(_TAMANHO_MINIMO_HAAR, round(config.TAMANHO_BUSCA_ROSTO * escala))

    achados: list[tuple[int, int, int, int, bool]] = []
    if anterior is not None:
        margem = config.MARGEM_BUSCA_ROSTO * anterior.largura
        x0 = max(0, int((anterior.x - margem) * escala))
        y0 = max(0, int((anterior.y - margem) * escala))
        x1 = min(reduzida.shape[1], int((anterior.x + anterior.largura + margem) * escala))
        y1 = min(reduzida.shape[0], int((anterior.y + anterior.altura + margem) * escala))
        if x1 - x0 >= minimo and y1 - y0 >= minimo:
            achados = [(x + x0, y + y0, w, h, f) for x, y, w, h, f in _procurar(reduzida[y0:y1, x0:x1], minimo)]
    if not achados:
        achados = _procurar(reduzida, minimo)
    if not achados:
        return None

    x, y, w, h, frontal = max(achados, key=lambda a: a[2] * a[3])
    return Rosto(
        x=min(largura - 1, round(x / escala)),
        y=min(altura - 1, round(y / escala)),
        largura=min(largura, round(w / escala)),
        altura=min(altura, round(h / escala)),
        frontal=frontal,
    )
