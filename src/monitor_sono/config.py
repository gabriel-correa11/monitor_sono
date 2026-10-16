"""Configurações gerais do sistema."""

from pathlib import Path

RAIZ: Path = Path(__file__).resolve().parent.parent.parent
PASTA_DADOS: Path = RAIZ / "dados"
CAMINHO_BANCO: Path = PASTA_DADOS / "monitor_sono.db"

QUADROS_POR_SEGUNDO_ANALISE: int = 1
RESOLUCAO_ANALISE: tuple[int, int] = (320, 240)

# Seção 4 da lista de requisitos: comportamentos identificáveis (RF09)
COMPORTAMENTOS: frozenset[str] = frozenset({
    "olhos_abertos",                # RF05
    "olhos_fechados",               # RF05
    "movimento_cabeca",             # RF06
    "movimento_corporal",           # RF07
    "mudanca_posicao",              # RF07
    "ausencia_movimento",           # RF11
    "visibilidade_insuficiente",    # RF15
})

# RNF12
AVISO_NAO_DIAGNOSTICO: str = (
    "Os resultados deste sistema representam estimativas comportamentais "
    "e não constituem diagnósticos clínicos."
)
