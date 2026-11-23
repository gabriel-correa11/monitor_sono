"""Configurações gerais do sistema.

Valores marcados como PROVISÓRIO foram calibrados com as gravações do estudo de caso e devem ser
confirmados pela equipe (pesquisadores e analistas). As regras de negócio não definem esses números.
"""

from pathlib import Path

RAIZ: Path = Path(__file__).resolve().parent.parent.parent
PASTA_DADOS: Path = RAIZ / "dados"
CAMINHO_BANCO: Path = PASTA_DADOS / "monitor_sono.db"

# RF02 — captura
QUADROS_POR_SEGUNDO_ANALISE: int = 1
RESOLUCAO_ANALISE: tuple[int, int] = (320, 240)
FALHAS_LEITURA_MAX: int = 30  # RNF08: leituras seguidas com falha antes de encerrar a captura da câmera

# RF07 — movimento (diferença entre quadros em escala de cinza)
DESFOQUE_MOVIMENTO: int = 5  # tamanho do desfoque gaussiano (ímpar), reduz o ruído do infravermelho
LIMIAR_PIXEL: int = 20  # PROVISÓRIO: diferença de intensidade (0 a 255) para um pixel contar como alterado
LIMIAR_MOVIMENTO: float = 0.005  # PROVISÓRIO: fração da imagem alterada para contar como movimento (0,5%)
LIMIAR_MUDANCA_POSICAO: float = 0.10  # PROVISÓRIO: fração alterada para mudança brusca de posição (RN05)
LIMIAR_MUDANCA_ILUMINACAO: float = 0.5  # PROVISÓRIO: fração alterada acima da qual a mudança é da imagem inteira (luz acesa/apagada), não movimento

# RF15 — visibilidade
BRILHO_MINIMO: float = 30.0  # PROVISÓRIO: brilho médio (0 a 255) abaixo do qual a imagem é escura demais
CONTRASTE_MINIMO: float = 8.0  # PROVISÓRIO: desvio padrão abaixo do qual a imagem não tem detalhe (câmera tampada)

# RF11 e regras de negócio — tempos em segundos
JUNCAO_MOVIMENTO_S: float = 5.0  # movimentos separados por até este intervalo formam um único período
AUSENCIA_MINIMA_S: float = 60.0  # PROVISÓRIO: menor período registrado como ausência de movimento (RF11)
AUSENCIA_PROLONGADA_S: float = 300.0  # PROVISÓRIO: ausência prolongada de movimento (RN03)
JANELA_ATIVIDADE_S: float = 60.0  # PROVISÓRIO: janela para contar movimentos frequentes (RN04)
MOVIMENTOS_FREQUENTES: int = 10  # PROVISÓRIO: segundos com movimento dentro da janela para maior atividade (RN04)
PERIODO_CONTINUO_OLHOS_S: float = 60.0  # PROVISÓRIO: olhos abertos ou fechados por período contínuo (RN01, RN02)

# Seção 4 da lista de requisitos: comportamentos identificáveis (RF09)
COMPORTAMENTOS: frozenset[str] = frozenset({
    "olhos_abertos",                # RF05
    "olhos_fechados",               # RF05
    "movimento_cabeca",             # RF06
    "movimento_corporal",           # RF07
    "mudanca_posicao",              # RF07, RN05
    "ausencia_movimento",           # RF11
    "visibilidade_insuficiente",    # RF15
    "maior_atividade_motora",       # RN04: movimentos frequentes registrados como período de maior atividade
})

# RF10 — estados estimados. PROVISÓRIO: a lista de requisitos não define os estados; estes vêm das regras
# RN01 (vigília), RN02 (possível sono) e RN07 (indeterminado) e aguardam confirmação dos pesquisadores.
ESTADOS: tuple[str, ...] = ("vigilia", "possivel_sono", "indeterminado")

# RNF12
AVISO_NAO_DIAGNOSTICO: str = (
    "Os resultados deste sistema representam estimativas comportamentais "
    "e não constituem diagnósticos clínicos."
)
