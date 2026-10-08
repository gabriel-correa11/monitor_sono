"""Configurações gerais do sistema. RF: todos. RNF05."""

from pathlib import Path

RAIZ: Path = Path(__file__).resolve().parent.parent.parent
PASTA_DADOS: Path = RAIZ / "dados"
PASTA_GRAVACOES: Path = PASTA_DADOS / "gravacoes"
CAMINHO_BANCO: Path = PASTA_DADOS / "monitor_sono.db"

QUADROS_POR_SEGUNDO_ANALISE: int = 1
RESOLUCAO_ANALISE: tuple[int, int] = (320, 240)

TIPOS_EVENTO: frozenset[str] = frozenset({"movimento", "som"})  # RF05, RF06

AVISO_NAO_DIAGNOSTICO: str = (
    "Estes resultados são dados de monitoramento e não representam diagnóstico médico."
)  # RNF07
