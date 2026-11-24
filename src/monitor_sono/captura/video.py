"""RF02 — Capturar imagens em tempo real da câmera durante a sessão."""

from collections.abc import Iterator
from pathlib import Path
from time import monotonic

import cv2
import numpy as np

from monitor_sono import config


def eh_arquivo(fonte: int | str) -> bool:
    """RF02. Indica se a fonte é uma gravação em arquivo (e não uma câmera ao vivo)."""
    return isinstance(fonte, str) and Path(fonte).is_file()


def capturar_quadros(
    fonte: int | str,
    fps_analise: int,
    *,
    resolucao: tuple[int, int] | None = config.RESOLUCAO_ANALISE,
) -> Iterator[tuple[float, np.ndarray]]:
    """RF02. Devolve (segundo, quadro) a fps_analise quadros por segundo.

    - fonte: índice da câmera (ex.: 0), endereço do dispositivo ou caminho de uma gravação.
    - segundo: tempo desde o início da captura. Com câmera, vem do relógio; com gravação, do tempo do
      próprio vídeo, para que a leitura (mais rápida que o tempo real) não altere os horários.
    - quadro: imagem BGR redimensionada para `resolucao` (padrão: config.RESOLUCAO_ANALISE). Com
      resolucao=None, o quadro sai na resolução original da câmera, para a detecção de rosto e olhos
      (RF04, RF05), que precisa de mais detalhe.

    Os quadros não usados são só lidos (grab), sem decodificar a imagem, para poupar processamento.
    Com câmera, uma falha momentânea de leitura não encerra a captura (RNF08): ela só termina depois de
    config.FALHAS_LEITURA_MAX falhas seguidas. Com gravação, termina no fim do vídeo.
    """
    if fps_analise <= 0:
        raise ValueError("RF02: fps_analise deve ser maior que zero")

    arquivo = eh_arquivo(fonte)
    camera = cv2.VideoCapture(fonte)
    if not camera.isOpened():
        camera.release()
        # A fonte não aparece na mensagem: pode conter usuário e senha (RTSP).
        raise RuntimeError("RF02: não foi possível abrir a câmera")

    intervalo = 1.0 / fps_analise
    inicio = monotonic()
    proximo = 0.0
    falhas = 0
    try:
        while True:
            if not camera.grab():
                if arquivo:
                    break
                falhas += 1
                if falhas >= config.FALHAS_LEITURA_MAX:
                    break
                continue
            falhas = 0
            if arquivo:
                segundo = camera.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            else:
                segundo = monotonic() - inicio
            if segundo < proximo:
                continue
            ok, quadro = camera.retrieve()
            if not ok or quadro is None:
                continue
            proximo += intervalo
            if proximo <= segundo:  # câmera travou: não entregar rajada de quadros
                proximo = segundo + intervalo
            yield segundo, quadro if resolucao is None else cv2.resize(quadro, resolucao)
    finally:
        camera.release()
