"""RF01, RF02 — Iniciar e encerrar sessões de monitoramento."""

from datetime import datetime

from monitor_sono.registro import banco


def iniciar_sessao(origem: str) -> int:
    """RF01. Cria a sessão e devolve o id."""
    return banco.criar_sessao(origem=origem, inicio=datetime.now())


def encerrar_sessao(sessao_id: int) -> None:
    """RF02. Marca o horário de término."""
    banco.finalizar_sessao(sessao_id, fim=datetime.now())
