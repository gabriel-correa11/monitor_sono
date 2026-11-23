"""Teste de ponta a ponta do pipeline com vídeo sintético (sem gravação real)."""

import cv2
import numpy as np

from monitor_sono import config, pipeline
from monitor_sono.registro import banco


def gerar_video(caminho, segundos: int, fps: int = 5) -> None:
    """Cena parada com um "movimento" (quadrado que aparece) aos 20 s e uma mudança grande aos 40 s."""
    escritor = cv2.VideoWriter(str(caminho), cv2.VideoWriter_fourcc(*"MJPG"), fps, (320, 240))
    gerador = np.random.default_rng(1)
    fundo = np.clip(120 + gerador.integers(-20, 21, size=(240, 320, 3)), 0, 255).astype(np.uint8)
    for i in range(segundos * fps):
        quadro = fundo.copy()
        t = i / fps
        if 20 <= t < 21:
            quadro[50:90, 50:90] = 255
        if t >= 40:
            quadro[0:140, 0:200] = 30
        escritor.write(quadro)
    escritor.release()


def test_analisa_gravacao_e_grava_no_banco(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "AUSENCIA_MINIMA_S", 10.0)
    video = tmp_path / "sintetico.avi"
    gerar_video(video, segundos=60)
    db = tmp_path / "teste.db"

    r = pipeline.analisar(str(video), caminho_banco=db)

    assert r.quadros >= 55
    tipos = {c["tipo"] for c in banco.comportamentos_da_sessao(r.sessao_id, caminho=db)}
    assert "movimento_corporal" in tipos
    assert "mudanca_posicao" in tipos
    assert "ausencia_movimento" in tipos
    estados = banco.estados_da_sessao(r.sessao_id, caminho=db)
    # Sem detecção de olhos (RF05), tudo fica indeterminado e não confiável (RN06, RN07, RNF09).
    assert estados and all(e["estado"] == "indeterminado" and e["confiavel"] == 0 for e in estados)
    sessao = banco.listar_sessoes(caminho=db)[0]
    assert sessao["fim"] is not None
