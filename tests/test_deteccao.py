"""Testes da detecção: movimento (RF07) e visibilidade (RF15), com quadros gerados em código."""

import numpy as np

from monitor_sono import config
from monitor_sono.deteccao import movimento, visibilidade


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
