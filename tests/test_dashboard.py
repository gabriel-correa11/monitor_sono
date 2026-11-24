"""Testes do dashboard (RF13, RF14, RNF10, RNF12) com o executor de testes do Streamlit e banco temporário."""

from datetime import datetime
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from monitor_sono import config
from monitor_sono.registro import banco

APP = Path(__file__).resolve().parent.parent / "src" / "monitor_sono" / "dashboard" / "app.py"


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Banco temporário: o dashboard lê pelo registro, que usa config.CAMINHO_BANCO."""
    caminho = tmp_path / "teste.db"
    monkeypatch.setattr(config, "CAMINHO_BANCO", caminho)
    return caminho


def abrir(sessao_id: int | None = None) -> AppTest:
    at = AppTest.from_file(str(APP), default_timeout=30)
    at.run()
    if sessao_id is not None:
        at.selectbox[0].select(sessao_id).run()
    assert not at.exception, [e.message for e in at.exception]
    return at


def metrica(at: AppTest, rotulo: str) -> str:
    return next(m.value for m in at.metric if m.label == rotulo)


def test_banco_vazio_mostra_orientacao(db):
    at = abrir()
    assert any("Nenhuma sessão gravada" in i.value for i in at.info)


def test_sessao_completa_mostra_resumo_e_aviso(db):
    sid = banco.criar_sessao(datetime(2026, 11, 20, 22, 30))
    banco.registrar_comportamento(sid, "movimento_corporal", datetime(2026, 11, 20, 22, 40), datetime(2026, 11, 20, 22, 41))
    banco.registrar_estado(sid, "indeterminado", datetime(2026, 11, 20, 22, 30), datetime(2026, 11, 21, 0, 10), False)
    banco.finalizar_sessao(sid, datetime(2026, 11, 21, 0, 10))

    at = abrir(sid)

    assert any(config.AVISO_NAO_DIAGNOSTICO in w.value for w in at.warning)  # RNF12
    assert metrica(at, "Períodos de movimento") == "1"


@pytest.mark.parametrize(
    ("fim", "esperado"),
    [
        (datetime(2026, 11, 20, 23, 15), "0 h 45 min"),
        (datetime(2026, 11, 21, 0, 10), "1 h 40 min"),  # antes aparecia "2 h 40 min"
        (datetime(2026, 11, 21, 6, 10), "7 h 40 min"),  # antes aparecia "8 h 40 min"
        (datetime(2026, 11, 21, 6, 29, 40), "8 h 0 min"),  # antes aparecia "8 h 60 min"
    ],
)
def test_duracao_em_horas_e_minutos(db, fim, esperado):
    sid = banco.criar_sessao(datetime(2026, 11, 20, 22, 30))
    banco.finalizar_sessao(sid, fim)

    assert metrica(abrir(sid), "Duração") == esperado


def test_sessao_sem_registros_nao_quebra(db):
    """RF14: sessão sem comportamentos nem estados ainda gera a página e o relatório."""
    sid = banco.criar_sessao(datetime(2026, 11, 21, 23, 0))
    banco.finalizar_sessao(sid, datetime(2026, 11, 21, 23, 0))

    abrir(sid)


def test_sessao_sem_fim_nao_quebra_e_e_sinalizada(db):
    """Sessão antiga deixada sem encerramento: é a mais recente, então abre por padrão."""
    completa = banco.criar_sessao(datetime(2026, 11, 20, 22, 30))
    banco.finalizar_sessao(completa, datetime(2026, 11, 20, 23, 30))
    banco.criar_sessao(datetime(2026, 11, 22, 23, 0))

    at = abrir()

    assert any("não tem horário de encerramento" in i.value for i in at.info)


def test_excluir_sessao_volta_para_outra_sessao(db):
    """RNF10: depois de excluir, a página recarrega sem erro."""
    antiga = banco.criar_sessao(datetime(2026, 11, 20, 22, 30))
    banco.finalizar_sessao(antiga, datetime(2026, 11, 20, 23, 30))
    nova = banco.criar_sessao(datetime(2026, 11, 21, 22, 30))
    banco.finalizar_sessao(nova, datetime(2026, 11, 21, 23, 30))

    at = abrir(nova)
    at.checkbox[0].check().run()
    at.button[0].click().run()

    assert not at.exception, [e.message for e in at.exception]
    assert [s["id"] for s in banco.listar_sessoes()] == [antiga]
