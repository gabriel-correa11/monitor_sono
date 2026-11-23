"""RF02 — Capturar imagens em tempo real da câmera durante a sessão."""

from collections.abc import Iterator
from time import monotonic

import cv2
import numpy as np

from monitor_sono import config


def capturar_quadros(fonte: int | str, fps_analise: int) -> Iterator[tuple[float, np.ndarray]]:
    """RF02. Devolve (segundo, quadro) capturados em tempo real a fps_analise.

    - fonte: índice da câmera (ex.: 0) ou endereço do dispositivo.
    - fps_analise: quadros por segundo entregues para análise
      (padrão do projeto: config.QUADROS_POR_SEGUNDO_ANALISE).
    - segundo: tempo decorrido desde o início da captura, em segundos.
    - quadro: imagem BGR redimensionada para config.RESOLUCAO_ANALISE.

    A câmera é lida continuamente, para que o quadro entregue seja sempre o
    mais recente, mas só um quadro a cada 1/fps_analise segundos é entregue.
    A captura termina quando a câmera deixa de enviar imagens.
    """
    if fps_analise <= 0:
        raise ValueError("RF02: fps_analise deve ser maior que zero")

    camera = cv2.VideoCapture(fonte)
    if not camera.isOpened():
        camera.release()
        # A fonte não aparece na mensagem: pode conter usuário e senha (RTSP).
        raise RuntimeError("RF02: não foi possível abrir a câmera")

    intervalo = 1.0 / fps_analise
    inicio = monotonic()
    proximo = 0.0
    try:
        while True:
            ok, quadro = camera.read()
            if not ok:
                break
            segundo = monotonic() - inicio
            if segundo < proximo:
                continue
            proximo = segundo + intervalo
            yield segundo, cv2.resize(quadro, config.RESOLUCAO_ANALISE)
    finally:
        camera.release()