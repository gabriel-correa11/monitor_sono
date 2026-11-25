"""Testes do dashboard (RF13, RF14, RNF09, RNF10, RNF12) com o executor de testes do Streamlit e banco temporário."""

import csv
from datetime import datetime
from pathlib import Path

import pytest
import streamlit as st
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


def test_relatorio_csv_tem_resumo_e_coluna_confiavel(db, monkeypatch):
    """RF14, RNF09, RNF12: aviso na 1ª linha, resumo antes dos eventos e coluna "Confiável"."""
    baixado = {}
    original = st.download_button

    def capturar(rotulo, data, *args, **kwargs):
        baixado["csv"] = data.decode("utf-8-sig")
        return original(rotulo, data, *args, **kwargs)

    monkeypatch.setattr(st, "download_button", capturar)

    sid = banco.criar_sessao(datetime(2026, 11, 20, 22, 30))
    banco.registrar_comportamento(sid, "movimento_corporal", datetime(2026, 11, 20, 22, 40), datetime(2026, 11, 20, 22, 41))
    banco.registrar_comportamento(sid, "mudanca_posicao", datetime(2026, 11, 20, 22, 41))
    banco.registrar_comportamento(sid, "movimento_cabeca", datetime(2026, 11, 20, 22, 50), datetime(2026, 11, 20, 22, 51))
    banco.registrar_comportamento(sid, "ausencia_movimento", datetime(2026, 11, 20, 23, 0), datetime(2026, 11, 20, 23, 30))
    banco.registrar_estado(sid, "vigilia", datetime(2026, 11, 20, 22, 30), datetime(2026, 11, 20, 23, 0), True)
    banco.registrar_estado(sid, "indeterminado", datetime(2026, 11, 20, 23, 0), datetime(2026, 11, 21, 0, 10), False)
    banco.finalizar_sessao(sid, datetime(2026, 11, 21, 0, 10))

    at = abrir(sid)

    linhas = baixado["csv"].split("\n")
    assert linhas[0] == "# " + config.AVISO_NAO_DIAGNOSTICO  # RNF12
    separador = linhas.index("")
    resumo = dict(list(csv.reader(linhas[1:separador]))[1:])
    assert resumo["Sessão"] == str(sid)
    assert resumo["Início"] == "2026-11-20 22:30:00"
    assert resumo["Fim"] == "2026-11-21 00:10:00"
    assert resumo["Duração"] == "1 h 40 min"
    assert resumo["Períodos de movimento"] == "1"
    assert resumo["Mudanças de posição"] == "1"
    assert resumo["Movimentos da cabeça"] == "1"
    assert resumo["Tempo sem movimento (min)"] == "30"
    assert resumo["Acordado (estimado) (min)"] == "30"
    assert resumo["Acordado (estimado) (%)"] == "30"
    assert resumo["Indeterminado (min)"] == "70"
    assert resumo["Indeterminado (%)"] == "70"

    eventos = list(csv.DictReader([l for l in linhas[separador + 1:] if l]))
    assert {e["Comportamento ou estado"]: e["Confiável"] for e in eventos if e["Categoria"] == "Estimado"} == {
        "Acordado (estimado)": "Sim",
        "Indeterminado": "Não",
    }
    assert all(e["Confiável"] == "" for e in eventos if e["Categoria"] == "Observado")
    assert len(eventos) == 6

    assert metrica(at, "Tempo não confiável") == "70 min (70%)"  # RNF09 na tela


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
