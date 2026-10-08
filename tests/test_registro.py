from datetime import datetime

import pytest

from monitor_sono.registro import banco


def test_sessao_e_evento(tmp_path):
    db = tmp_path / "teste.db"
    sid = banco.criar_sessao("teste.mp4", datetime(2026, 10, 8, 22, 0), caminho=db)
    banco.registrar_evento(sid, "movimento", datetime(2026, 10, 8, 23, 15), nivel=0.4, caminho=db)
    banco.finalizar_sessao(sid, datetime(2026, 10, 9, 6, 0), caminho=db)

    sessoes = banco.listar_sessoes(caminho=db)
    assert len(sessoes) == 1 and sessoes[0]["fim"] is not None
    assert len(banco.eventos_da_sessao(sid, caminho=db)) == 1


def test_rejeita_tipo_fora_dos_requisitos(tmp_path):
    db = tmp_path / "teste.db"
    sid = banco.criar_sessao("teste.mp4", datetime.now(), caminho=db)
    with pytest.raises(ValueError):
        banco.registrar_evento(sid, "fase_rem", datetime.now(), caminho=db)
