"""Teste de ponta a ponta do pipeline com vídeo sintético (sem gravação real)."""

import cv2
import numpy as np

from monitor_sono import config, pipeline
from monitor_sono.deteccao import olhos
from monitor_sono.registro import banco
from monitor_sono.tipos import Rosto


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
    # A cena sintética não tem rosto: sem olhos (RF05), tudo fica indeterminado e não confiável (RN06, RN07, RNF09).
    assert estados and all(e["estado"] == "indeterminado" and e["confiavel"] == 0 for e in estados)
    sessao = banco.listar_sessoes(caminho=db)[0]
    assert sessao["fim"] is not None


def gerar_cena_parada(caminho, segundos: int, fps: int = 5) -> None:
    """Cena parada e com bastante textura (o "rosto" simulado precisa de contraste), sem nenhum movimento."""
    escritor = cv2.VideoWriter(str(caminho), cv2.VideoWriter_fourcc(*"MJPG"), fps, (320, 240))
    fundo = np.random.default_rng(3).integers(0, 256, size=(240, 320, 3), dtype=np.uint8)
    for _ in range(segundos * fps):
        escritor.write(fundo)
    escritor.release()


def test_olhos_chegam_ate_os_estados_no_banco(tmp_path, monkeypatch):
    # Detector simulado (sem foto de pessoa): rosto sempre visível; olhos abertos nos 40 primeiros quadros
    # e depois fechados. A cabeça se desloca no quadro 20.
    monkeypatch.setattr(config, "PERIODO_CONTINUO_OLHOS_S", 20.0)
    monkeypatch.setattr(config, "AUSENCIA_MINIMA_S", 10.0)
    monkeypatch.setattr(config, "AUSENCIA_PROLONGADA_S", 30.0)
    chamadas = {"rosto": 0, "olhos": 0}

    def rosto_falso(quadro, anterior=None):
        chamadas["rosto"] += 1
        x = 100 if chamadas["rosto"] < 20 else 160  # deslocamento de 0,4 largura de rosto (RF06)
        return Rosto(x, 60, 150, 150, frontal=True)

    def olhos_falsos(quadro, rosto):
        chamadas["olhos"] += 1
        return 2 if chamadas["olhos"] <= 40 else 0

    monkeypatch.setattr(pipeline, "detectar_rosto", rosto_falso)
    monkeypatch.setattr(olhos, "contar_olhos", olhos_falsos)
    video = tmp_path / "parado.avi"
    gerar_cena_parada(video, segundos=100)
    db = tmp_path / "teste.db"

    r = pipeline.analisar(str(video), caminho_banco=db)

    assert r.quadros_com_rosto == r.quadros
    # Só os primeiros quadros sem olhos (antes de QUADROS_OLHOS_FECHADOS seguidos) ficam indeterminados.
    assert r.quadros_olhos_determinaveis == r.quadros - (config.QUADROS_OLHOS_FECHADOS - 1)
    tipos = {c["tipo"] for c in banco.comportamentos_da_sessao(r.sessao_id, caminho=db)}
    assert {"olhos_abertos", "olhos_fechados", "movimento_cabeca", "ausencia_movimento"} <= tipos
    estados = {(e["estado"], e["confiavel"]) for e in banco.estados_da_sessao(r.sessao_id, caminho=db)}
    assert ("vigilia", 1) in estados  # RN01
    assert ("possivel_sono", 1) in estados  # RN02 + RN03: olhos fechados e ausência prolongada juntos
