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
        sid, "sono_leve", datetime(2026, 10, 8, 23, 0),
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
        sid, "acordado", datetime(2026, 10, 8, 23, 0), caminho=db,
    )
    banco.excluir_sessao(sid, caminho=db)

    assert len(banco.listar_sessoes(caminho=db)) == 0
    assert len(banco.comportamentos_da_sessao(sid, caminho=db)) == 0
    assert len(banco.estados_da_sessao(sid, caminho=db)) == 0
