"""Testes do RF02 — captura de quadros."""

import cv2
import numpy as np
import pytest

from monitor_sono import config
from monitor_sono.captura import video


class RelogioFalso:
    """Simula o relógio: cada consulta avança `passo` segundos."""

    def __init__(self, passo: float) -> None:
        self.agora = 0.0
        self.passo = passo

    def __call__(self) -> float:
        atual = self.agora
        self.agora += self.passo
        return atual


def gerar_video(caminho, quadros: int = 20, tamanho: tuple[int, int] = (640, 480)) -> None:
    """Cria um vídeo sintético (sem gravação real) para substituir a câmera."""
    escritor = cv2.VideoWriter(str(caminho), cv2.VideoWriter_fourcc(*"MJPG"), 10, tamanho)
    for i in range(quadros):
        escritor.write(np.full((tamanho[1], tamanho[0], 3), i * 10, dtype=np.uint8))
    escritor.release()


def test_entrega_um_quadro_por_intervalo(tmp_path, monkeypatch):
    caminho = tmp_path / "sintetico.avi"
    gerar_video(caminho, quadros=20)
    # 20 quadros lidos, cada um 0,25 s depois do anterior = 5 s de "câmera"
    monkeypatch.setattr(video, "monotonic", RelogioFalso(passo=0.25))

    resultado = list(video.capturar_quadros(str(caminho), fps_analise=1))

    segundos = [s for s, _ in resultado]
    assert len(resultado) == 5
    assert all(b - a == pytest.approx(1.0) for a, b in zip(segundos, segundos[1:]))


def test_quadros_na_resolucao_de_analise(tmp_path):
    caminho = tmp_path / "sintetico.avi"
    gerar_video(caminho, quadros=3)

    largura, altura = config.RESOLUCAO_ANALISE
    for _, quadro in video.capturar_quadros(str(caminho), fps_analise=100):
        assert isinstance(quadro, np.ndarray)
        assert quadro.shape[:2] == (altura, largura)


def test_fonte_invalida_gera_erro(tmp_path):
    with pytest.raises(RuntimeError):
        next(video.capturar_quadros(str(tmp_path / "nao_existe.avi"), fps_analise=1))


def test_fps_invalido_gera_erro():
    with pytest.raises(ValueError):
        next(video.capturar_quadros(0, fps_analise=0))