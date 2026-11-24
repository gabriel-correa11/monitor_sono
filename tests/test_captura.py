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


def test_resolucao_none_entrega_quadro_original(tmp_path):
    # RF04, RF05: rosto e olhos precisam do quadro na resolução original da câmera.
    caminho = tmp_path / "sintetico.avi"
    gerar_video(caminho, quadros=3, tamanho=(640, 480))
    for _, quadro in video.capturar_quadros(str(caminho), fps_analise=100, resolucao=None):
        assert quadro.shape[:2] == (480, 640)


def test_fonte_invalida_gera_erro(tmp_path):
    with pytest.raises(RuntimeError):
        next(video.capturar_quadros(str(tmp_path / "nao_existe.avi"), fps_analise=1))


def test_fps_invalido_gera_erro():
    with pytest.raises(ValueError):
        next(video.capturar_quadros(0, fps_analise=0))


# --- RNF04: carimbo de data e hora da câmera --------------------------------------------------------------

from datetime import datetime, timedelta  # noqa: E402

from monitor_sono.captura.carimbo import RelogioCarimbo, ler_carimbo  # noqa: E402


def quadro_escuro() -> np.ndarray:
    """Quadro 1600x900 com textura escura, no tamanho em que o carimbo sintético cabe na região."""
    return np.random.default_rng(5).integers(20, 90, size=(900, 1600, 3), dtype=np.uint8)


def test_le_o_carimbo_da_camera(carimbo):
    quadro = carimbo(quadro_escuro(), "2026-11-09 03:22:48")
    assert ler_carimbo(quadro) == datetime(2026, 11, 9, 3, 22, 48)


def test_todos_os_digitos_sao_reconhecidos(carimbo):
    quadro = carimbo(quadro_escuro(), "2026-10-27 13:45:59")
    assert ler_carimbo(quadro) == datetime(2026, 10, 27, 13, 45, 59)


def test_quadro_sem_carimbo_devolve_none():
    assert ler_carimbo(quadro_escuro()) is None


def test_carimbo_incompleto_devolve_none(carimbo):
    assert ler_carimbo(carimbo(quadro_escuro(), "2026-11-09 03:22")) is None


def test_carimbo_com_data_impossivel_devolve_none(carimbo):
    assert ler_carimbo(carimbo(quadro_escuro(), "2026-13-09 03:22:48")) is None


INICIO = datetime(2026, 11, 9, 3, 22, 48)


def hora(segundos: float) -> datetime:
    """Carimbo mostrado pela câmera: o segundo cheio."""
    return INICIO + timedelta(seconds=int(segundos))


def test_sem_carimbo_o_tempo_segue_o_video():
    relogio = RelogioCarimbo()
    assert [relogio.atualizar(s, None) for s in (0.0, 1.0, 2.0)] == [0.0, 1.0, 2.0]
    assert relogio.origem is None


def test_carimbo_define_a_origem_da_sessao():
    relogio = RelogioCarimbo()
    relogio.atualizar(0.0, hora(0))
    assert relogio.origem == INICIO


def test_video_adiantado_e_corrigido_pelo_carimbo():
    """O vídeo avança 1 s por quadro, mas o relógio real só 0,95 s: depois de 200 quadros, 190 s."""
    relogio = RelogioCarimbo()
    reais = [relogio.atualizar(float(i), hora(0.95 * i)) for i in range(201)]
    assert None not in reais
    assert 189.0 <= reais[-1] < 191.0
    assert reais == sorted(reais)


def test_interrupcao_da_gravacao_e_aceita_depois_de_confirmada():
    relogio = RelogioCarimbo()
    for s in range(5):
        relogio.atualizar(float(s), hora(s))
    assert relogio.atualizar(5.0, hora(905)) is None  # salto ainda em dúvida: quadro ignorado
    assert relogio.atualizar(6.0, hora(906)) == 906.0  # confirmado pelo quadro seguinte
    assert relogio.atualizar(7.0, hora(907)) == pytest.approx(907.0, abs=1)


def test_digito_mal_lido_isolado_nao_cria_interrupcao():
    relogio = RelogioCarimbo()
    for s in range(5):
        relogio.atualizar(float(s), hora(s))
    assert relogio.atualizar(5.0, hora(5 + 600)) is None  # um minuto lido errado
    assert relogio.atualizar(6.0, hora(6)) == pytest.approx(6.0, abs=1)


def test_trecho_repetido_pela_camera_nao_e_contado_duas_vezes():
    relogio = RelogioCarimbo()
    for s in range(30):
        relogio.atualizar(float(s), hora(s))
    # A câmera volta 20 s: esses quadros já foram cobertos e são ignorados.
    repetidos = [relogio.atualizar(float(30 + i), hora(10 + i)) for i in range(15)]
    assert repetidos[0] is None
    seguintes = [relogio.atualizar(float(60 + i), hora(30 + i)) for i in range(10)]
    aceitos = [r for r in repetidos + seguintes if r is not None]
    assert aceitos == sorted(aceitos)  # o tempo nunca volta
    assert min(aceitos) >= 29.0
    assert seguintes[-1] == pytest.approx(39.0, abs=1)


def test_primeiro_carimbo_mal_lido_nao_desloca_a_sessao():
    relogio = RelogioCarimbo()
    relogio.atualizar(0.0, hora(0) + timedelta(minutes=10))  # minuto lido errado no primeiro quadro
    reais = [relogio.atualizar(float(s), hora(s)) for s in range(1, 30)]
    assert relogio.origem == INICIO
    assert None not in reais
    assert reais[-1] == pytest.approx(29.0, abs=1)
