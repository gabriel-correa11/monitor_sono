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


class CameraFalsa:
    """Simula uma câmera ao vivo: entrega `total` quadros e pode falhar em leituras escolhidas."""

    def __init__(self, total: int, falhas: frozenset[int] = frozenset()) -> None:
        self.total = total
        self.falhas = falhas
        self.lidos = 0

    def isOpened(self) -> bool:
        return True

    def grab(self) -> bool:
        self.lidos += 1
        if self.lidos > self.total or self.lidos in self.falhas:
            return False
        return True

    def retrieve(self):
        return True, np.zeros((480, 640, 3), dtype=np.uint8)

    def release(self) -> None:
        pass


def gerar_video(caminho, quadros: int = 20, fps: int = 10, tamanho: tuple[int, int] = (640, 480)) -> None:
    """Cria um vídeo sintético (sem gravação real)."""
    escritor = cv2.VideoWriter(str(caminho), cv2.VideoWriter_fourcc(*"MJPG"), fps, tamanho)
    for i in range(quadros):
        escritor.write(np.full((tamanho[1], tamanho[0], 3), i * 10 % 255, dtype=np.uint8))
    escritor.release()


def usar_camera_falsa(monkeypatch, camera: CameraFalsa, passo: float) -> None:
    monkeypatch.setattr(video.cv2, "VideoCapture", lambda fonte: camera)
    # O relógio é consultado uma vez no início e uma vez por quadro lido com sucesso.
    monkeypatch.setattr(video, "monotonic", RelogioFalso(passo=passo))


def test_camera_entrega_um_quadro_por_intervalo(monkeypatch):
    usar_camera_falsa(monkeypatch, CameraFalsa(total=20), passo=0.25)
    # 20 quadros a cada 0,25 s (de 0,25 a 5,0 s): sai o primeiro e depois um por segundo cheio.
    segundos = [s for s, _ in video.capturar_quadros(0, fps_analise=1)]
    assert segundos == pytest.approx([0.25, 1.0, 2.0, 3.0, 4.0, 5.0])


def test_camera_a_5_fps_nao_perde_quadros(monkeypatch):
    # Câmera a 5 fps: 50 quadros = 10 s. Devem sair 10 quadros, um por segundo, sem perda por arredondamento.
    usar_camera_falsa(monkeypatch, CameraFalsa(total=50), passo=0.2)
    segundos = [s for s, _ in video.capturar_quadros(0, fps_analise=1)]
    assert len(segundos) == 10
    intervalos = [b - a for a, b in zip(segundos, segundos[1:])]
    assert sum(intervalos) / len(intervalos) == pytest.approx(1.0, abs=0.05)


def test_falha_momentanea_nao_encerra_captura(monkeypatch):
    # RNF08: falhas isoladas de leitura no meio da sessão não encerram a captura.
    usar_camera_falsa(monkeypatch, CameraFalsa(total=40, falhas=frozenset({5, 6, 20})), passo=0.25)
    segundos = [s for s, _ in video.capturar_quadros(0, fps_analise=1)]
    assert len(segundos) >= 8


def test_gravacao_usa_o_tempo_do_video(tmp_path):
    # Gravação de 30 quadros a 10 fps = 3 s de vídeo, lida bem mais rápido que o tempo real.
    caminho = tmp_path / "sintetico.avi"
    gerar_video(caminho, quadros=30, fps=10)
    segundos = [s for s, _ in video.capturar_quadros(str(caminho), fps_analise=1)]
    assert len(segundos) == 3
    assert segundos[-1] == pytest.approx(2.0, abs=0.15)


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
