import sqlite3
from datetime import datetime

import pytest

from monitor_sono.registro import banco


def test_sessao_e_comportamento(tmp_path):
    db = tmp_path / "teste.db"
    sid = banco.criar_sessao(datetime(2026, 10, 8, 22, 0), caminho=db)
    banco.registrar_comportamento(
        sid, "olhos_fechados", datetime(2026, 10, 8, 23, 15), caminho=db,
    )
    banco.finalizar_sessao(sid, datetime(2026, 10, 9, 6, 0), caminho=db)

    sessoes = banco.listar_sessoes(caminho=db)
    assert len(sessoes) == 1 and sessoes[0]["fim"] is not None
    assert len(banco.comportamentos_da_sessao(sid, caminho=db)) == 1


def test_registrar_estado(tmp_path):
    db = tmp_path / "teste.db"
    sid = banco.criar_sessao(datetime(2026, 10, 8, 22, 0), caminho=db)
    eid = banco.registrar_estado(
        sid, "indeterminado", datetime(2026, 10, 8, 23, 0),
        fim=datetime(2026, 10, 9, 1, 0), confiavel=False, caminho=db,
    )
    estados = banco.estados_da_sessao(sid, caminho=db)
    assert len(estados) == 1
    assert estados[0]["confiavel"] == 0
    assert estados[0]["id"] == eid


def test_rejeita_comportamento_invalido(tmp_path):
    db = tmp_path / "teste.db"
    sid = banco.criar_sessao(datetime.now(), caminho=db)
    with pytest.raises(ValueError):
        banco.registrar_comportamento(sid, "fase_rem", datetime.now(), caminho=db)


def test_excluir_sessao(tmp_path):
    db = tmp_path / "teste.db"
    sid = banco.criar_sessao(datetime(2026, 10, 8, 22, 0), caminho=db)
    banco.registrar_comportamento(
        sid, "movimento_corporal", datetime(2026, 10, 8, 23, 0), caminho=db,
    )
    banco.registrar_estado(
        sid, "vigilia", datetime(2026, 10, 8, 23, 0), caminho=db,
    )
    banco.excluir_sessao(sid, caminho=db)

    assert len(banco.listar_sessoes(caminho=db)) == 0
    assert len(banco.comportamentos_da_sessao(sid, caminho=db)) == 0
    assert len(banco.estados_da_sessao(sid, caminho=db)) == 0


def test_rejeita_estado_fora_do_escopo(tmp_path):
    # RN10: estágios clínicos do sono não são estados válidos.
    db = tmp_path / "teste.db"
    sid = banco.criar_sessao(datetime.now(), caminho=db)
    with pytest.raises(ValueError):
        banco.registrar_estado(sid, "rem", datetime.now(), caminho=db)


def test_conexoes_sao_fechadas(tmp_path, monkeypatch):
    # RNF05: cada operação fecha a conexão; no Windows, conexão aberta pode prender o arquivo do banco.
    abertas = []
    conectar = banco.conectar

    def conectar_e_guardar(caminho=None):
        conexao = conectar(caminho)
        abertas.append(conexao)
        return conexao

    monkeypatch.setattr(banco, "conectar", conectar_e_guardar)
    db = tmp_path / "teste.db"
    sid = banco.criar_sessao(datetime(2026, 10, 8, 22, 0), caminho=db)
    banco.listar_sessoes(caminho=db)
    banco.excluir_sessao(sid, caminho=db)

    assert len(abertas) == 3
    for conexao in abertas:
        with pytest.raises(sqlite3.ProgrammingError):  # usar conexão fechada gera erro
            conexao.execute("SELECT 1")
    db.unlink()  # com tudo fechado, o arquivo pode ser apagado (no Windows, falharia se estivesse preso)
