"""Testes da detecção: movimento (RF07), visibilidade (RF15), rosto (RF04), olhos (RF05), cabeça (RF06) e
presença (RF03), com quadros gerados em código."""

import numpy as np

from monitor_sono import config
from monitor_sono.deteccao import movimento, olhos, rosto, visibilidade
from monitor_sono.tipos import Rosto


def cena(brilho: int = 120, altura: int = 240, largura: int = 320) -> np.ndarray:
    """Quadro BGR com textura leve, como uma cena parada."""
    gerador = np.random.default_rng(0)
    base = np.full((altura, largura, 3), brilho, dtype=np.int16)
    base += gerador.integers(-3, 4, size=base.shape, dtype=np.int16)
    return np.clip(base, 0, 255).astype(np.uint8)


def com_retangulo(quadro: np.ndarray, fracao: float) -> np.ndarray:
    """Copia o quadro e muda uma área retangular que ocupa `fracao` da imagem."""
    novo = quadro.copy()
    altura, largura = novo.shape[:2]
    lado = int((fracao * altura * largura) ** 0.5)
    novo[:lado, :lado] = 255
    return novo


def test_cena_parada_nao_e_movimento():
    q = cena()
    d = movimento.analisar_movimento(q, q.copy(), 1.0)
    assert not d.movimento and not d.mudanca_posicao and not d.mudanca_iluminacao


def test_mudanca_pequena_e_movimento():
    q = cena()
    d = movimento.analisar_movimento(q, com_retangulo(q, 0.03), 2.0)
    assert d.movimento and not d.mudanca_posicao
    assert d.segundo == 2.0


def test_mudanca_grande_e_mudanca_de_posicao():
    # RN05: mudança brusca de posição vira evento de movimentação corporal.
    q = cena()
    d = movimento.analisar_movimento(q, com_retangulo(q, 0.2), 3.0)
    assert d.movimento and d.mudanca_posicao


def test_luz_acesa_nao_conta_como_movimento():
    d = movimento.analisar_movimento(cena(60), cena(60 + config.LIMIAR_PIXEL + 15), 4.0)
    assert d.mudanca_iluminacao and not d.movimento


def test_funcoes_booleanas_do_rf07():
    q = cena()
    assert movimento.detectar_movimento_corporal(q, com_retangulo(q, 0.03))
    assert not movimento.detectar_mudanca_posicao(q, q.copy())


def test_imagem_escura_e_visibilidade_insuficiente():
    v = visibilidade.avaliar_visibilidade(cena(brilho=10), 5.0)
    assert not v.adequada and v.motivo == "escura"


def test_imagem_sem_contraste_e_visibilidade_insuficiente():
    plana = np.full((240, 320, 3), 128, dtype=np.uint8)
    v = visibilidade.avaliar_visibilidade(plana, 6.0)
    assert not v.adequada and v.motivo == "sem_contraste"


def test_cena_normal_e_visivel():
    q = com_retangulo(cena(), 0.1)  # cena com algum detalhe
    assert visibilidade.verificar_visibilidade(q)


# ---------------------------------------------------------------- RF04 — rosto
# Sem fotos de pessoas: o caminho "rosto encontrado" usa uma cascata simulada.


class CascataFalsa:
    """Substitui uma cascata Haar: devolve sempre as mesmas regiões e guarda o tamanho das imagens recebidas."""

    def __init__(self, regioes: list[tuple[int, int, int, int]]) -> None:
        self.regioes = regioes
        self.imagens: list[tuple[int, int]] = []

    def detectMultiScale(self, imagem, **_):
        self.imagens.append(imagem.shape[:2])
        return np.array(self.regioes, dtype=int).reshape(-1, 4)


def usar_cascatas(monkeypatch, frontal=(), perfil=()) -> dict[str, CascataFalsa]:
    falsas = {
        "haarcascade_frontalface_default.xml": CascataFalsa(list(frontal)),
        "haarcascade_profileface.xml": CascataFalsa(list(perfil)),
    }
    monkeypatch.setattr(rosto, "cascata", lambda nome: falsas[nome])
    return falsas


def test_cascatas_reais_estao_disponiveis():
    # RF04: o projeto exige OpenCV 4.x, que traz as cascatas Haar em cv2.data.haarcascades.
    assert not rosto.cascata("haarcascade_frontalface_default.xml").empty()
    assert not rosto.cascata("haarcascade_profileface.xml").empty()
    assert not rosto.cascata("haarcascade_eye.xml").empty()


def test_imagem_sem_rosto_devolve_none():
    assert rosto.detectar_rosto(np.full((540, 960, 3), 128, dtype=np.uint8)) is None


def test_rosto_volta_para_a_resolucao_original(monkeypatch):
    # Quadro 1920x1080 é reduzido para 960 de largura: a região achada (em px reduzidos) volta em dobro.
    falsas = usar_cascatas(monkeypatch, frontal=[(100, 50, 60, 60)])
    r = rosto.detectar_rosto(np.zeros((1080, 1920, 3), dtype=np.uint8))
    assert r == Rosto(200, 100, 120, 120, frontal=True)
    assert falsas["haarcascade_frontalface_default.xml"].imagens[0] == (540, 960)


def test_rosto_de_perfil_espelhado_vira_coordenada_original(monkeypatch):
    usar_cascatas(monkeypatch, perfil=[(10, 20, 50, 50)])
    r = rosto.detectar_rosto(np.zeros((540, 960), dtype=np.uint8))
    assert r is not None and not r.frontal
    # A primeira busca de perfil já acha (10, 20); a espelhada acha (960 - 10 - 50, 20). Ficam do mesmo tamanho.
    assert (r.x, r.y, r.largura) in {(10, 20, 50), (900, 20, 50)}


def test_busca_comeca_ao_redor_do_rosto_anterior(monkeypatch):
    falsas = usar_cascatas(monkeypatch, frontal=[(5, 5, 100, 100)])
    anterior = Rosto(400, 200, 100, 100, frontal=True)
    r = rosto.detectar_rosto(np.zeros((540, 960), dtype=np.uint8), anterior)
    # Janela com margem de 1 largura para cada lado: 300 x 300 px, começando em (300, 100).
    assert falsas["haarcascade_frontalface_default.xml"].imagens[0] == (300, 300)
    assert (r.x, r.y) == (305, 105)


def test_mesmo_rosto_perto_e_de_tamanho_parecido():
    a = Rosto(100, 100, 120, 120, True)
    assert rosto.mesmo_rosto(a, Rosto(150, 110, 130, 130, True))
    assert not rosto.mesmo_rosto(a, Rosto(500, 100, 120, 120, True))  # longe
    assert not rosto.mesmo_rosto(a, Rosto(100, 100, 300, 300, True))  # tamanho muito diferente


# ---------------------------------------------------------------- RF05 — olhos (RN06)
# O detector de olhos é simulado: a sequência diz quantos olhos "aparecem" em cada quadro.

ROSTO_GRANDE = Rosto(100, 100, 200, 200, frontal=True)
ROSTO_PEQUENO = Rosto(100, 100, 100, 100, frontal=True)
ROSTO_PERFIL = Rosto(100, 100, 200, 200, frontal=False)


def quadro_com_textura() -> np.ndarray:
    """Quadro com bastante contraste, para o rosto ser considerado nítido."""
    return np.random.default_rng(2).integers(0, 256, size=(480, 640), dtype=np.uint8)


def simular_olhos(monkeypatch, contagens: list[int]) -> None:
    fila = iter(contagens)
    monkeypatch.setattr(olhos, "contar_olhos", lambda quadro, rosto: next(fila))


def acompanhar(rostos: list[Rosto | None]) -> list[str]:
    q = quadro_com_textura()
    acompanhamento = olhos.AcompanhamentoOlhos()
    return [acompanhamento.avaliar(q, r, float(i)).estado for i, r in enumerate(rostos)]


def test_sem_rosto_olhos_indeterminados():
    # RN06: sem rosto, nunca "fechados".
    assert olhos.detectar_estado_olhos(quadro_com_textura(), None, 1.0).estado == "indeterminado"
    assert acompanhar([None] * 10) == ["indeterminado"] * 10


def test_rosto_pequeno_sem_olhos_e_indeterminado_nao_fechados(monkeypatch):
    simular_olhos(monkeypatch, [1] * 3 + [0] * 10)
    assert acompanhar([ROSTO_PEQUENO] * 13) == ["indeterminado"] * 13


def test_rosto_de_perfil_e_indeterminado(monkeypatch):
    simular_olhos(monkeypatch, [2] * 10)
    assert acompanhar([ROSTO_PERFIL] * 10) == ["indeterminado"] * 10


def test_rosto_borrado_e_indeterminado(monkeypatch):
    simular_olhos(monkeypatch, [2])
    plano = np.full((480, 640), 128, dtype=np.uint8)
    assert olhos.detectar_estado_olhos(plano, ROSTO_GRANDE, 1.0).estado == "indeterminado"


def test_rosto_grande_com_olhos_e_abertos(monkeypatch):
    simular_olhos(monkeypatch, [2])
    assert olhos.detectar_estado_olhos(quadro_com_textura(), ROSTO_GRANDE, 1.0).estado == "abertos"


def test_um_quadro_sozinho_nunca_da_fechados(monkeypatch):
    simular_olhos(monkeypatch, [0])
    assert olhos.detectar_estado_olhos(quadro_com_textura(), ROSTO_GRANDE, 1.0).estado == "indeterminado"


def test_olhos_vistos_e_depois_sumidos_viram_fechados(monkeypatch):
    n = config.QUADROS_OLHOS_FECHADOS
    simular_olhos(monkeypatch, [2] * 3 + [0] * (n + 2))
    estados = acompanhar([ROSTO_GRANDE] * (3 + n + 2))
    assert estados[:3] == ["abertos"] * 3
    assert estados[3:3 + n - 1] == ["indeterminado"] * (n - 1)  # ainda não são quadros seguidos suficientes
    assert estados[3 + n - 1:] == ["fechados"] * 3


def test_sem_olhos_vistos_antes_nunca_fechados(monkeypatch):
    # RN06: rosto em que os olhos nunca apareceram pode ser imagem ruim, não olho fechado.
    simular_olhos(monkeypatch, [0] * 20)
    assert acompanhar([ROSTO_GRANDE] * 20) == ["indeterminado"] * 20


def test_rosto_sumido_dentro_da_folga_mantem_acompanhamento(monkeypatch):
    folga, n = config.FOLGA_ROSTO_QUADROS, config.QUADROS_OLHOS_FECHADOS
    simular_olhos(monkeypatch, [2] + [0] * n)
    estados = acompanhar([ROSTO_GRANDE] + [None] * folga + [ROSTO_GRANDE] * n)
    assert estados[-1] == "fechados"


def test_rosto_sumido_alem_da_folga_reinicia_acompanhamento(monkeypatch):
    # Limitação registrada: depois de reiniciar, "fechados" só volta com olhos vistos abertos de novo.
    folga, n = config.FOLGA_ROSTO_QUADROS, config.QUADROS_OLHOS_FECHADOS
    simular_olhos(monkeypatch, [2] + [0] * (n + 3))
    estados = acompanhar([ROSTO_GRANDE] + [None] * (folga + 1) + [ROSTO_GRANDE] * (n + 3))
    assert "fechados" not in estados


def test_outro_rosto_reinicia_acompanhamento(monkeypatch):
    n = config.QUADROS_OLHOS_FECHADOS
    longe = Rosto(400, 250, 200, 200, frontal=True)
    simular_olhos(monkeypatch, [2] + [0] * (n + 2))
    estados = acompanhar([ROSTO_GRANDE] + [longe] * (n + 2))
    assert "fechados" not in estados
