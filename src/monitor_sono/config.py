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

# RF02, RNF04 — data e hora gravadas pela câmera na imagem (carimbo)
REGIAO_CARIMBO: tuple[float, float, float, float] = (0.0, 0.0, 0.32, 0.13)  # x0, y0, x1, y1 em fração do quadro (canto superior esquerdo)
LIMIAR_BRANCO_CARIMBO: int = 200  # menor valor (0 a 255) nos três canais para um pixel contar como texto branco
ALTURA_DIGITO_CARIMBO: tuple[float, float] = (0.015, 0.06)  # altura de um dígito, em fração da altura do quadro
TAMANHO_DIGITO_CARIMBO: tuple[int, int] = (20, 32)  # largura e altura para comparar cada dígito com os modelos
SEMELHANCA_MINIMA_CARIMBO: float = 0.80  # 0 a 1: abaixo disso o dígito não é reconhecido e o carimbo é descartado
TOLERANCIA_CARIMBO_S: float = 3.0  # diferença aceita entre o carimbo e o tempo previsto; acima disso exige confirmação
LACUNA_GRAVACAO_S: float = 10.0  # intervalo sem quadros acima do qual a gravação teve uma interrupção (RN07)

# RF07 — movimento (diferença entre quadros em escala de cinza)
DESFOQUE_MOVIMENTO: int = 5  # tamanho do desfoque gaussiano (ímpar), reduz o ruído do infravermelho
LIMIAR_PIXEL: int = 20  # PROVISÓRIO: diferença de intensidade (0 a 255) para um pixel contar como alterado
LIMIAR_MOVIMENTO: float = 0.005  # PROVISÓRIO: fração da imagem alterada para contar como movimento (0,5%)
LIMIAR_MUDANCA_POSICAO: float = 0.10  # PROVISÓRIO: fração alterada para mudança brusca de posição (RN05)
LIMIAR_MUDANCA_ILUMINACAO: float = 0.5  # PROVISÓRIO: fração alterada acima da qual a mudança é da imagem inteira (luz acesa/apagada), não movimento

# RF15 — visibilidade
BRILHO_MINIMO: float = 30.0  # PROVISÓRIO: brilho médio (0 a 255) abaixo do qual a imagem é escura demais
CONTRASTE_MINIMO: float = 8.0  # PROVISÓRIO: desvio padrão abaixo do qual a imagem não tem detalhe (câmera tampada)

# RF04 — rosto (cascatas Haar do OpenCV 4.x, frontal e de perfil)
RESOLUCAO_ROSTO: int = 960  # largura (px) da cópia reduzida em que o rosto é procurado; a altura segue a proporção
FATOR_ESCALA_ROSTO: float = 1.2  # PROVISÓRIO: passo entre os tamanhos testados pela cascata (maior = mais rápido, menos preciso)
VIZINHOS_ROSTO: int = 5  # PROVISÓRIO: detecções vizinhas exigidas para aceitar um rosto (maior = menos falso positivo)
TAMANHO_BUSCA_ROSTO: int = 60  # PROVISÓRIO: menor largura de rosto procurada, em px da imagem original
TAMANHO_MINIMO_HAAR: int = 24  # menor janela que as cascatas do OpenCV aceitam (são treinadas em 20 a 24 px)
MARGEM_BUSCA_ROSTO: float = 1.0  # janela ao redor do último rosto: margem de 1 largura do rosto para cada lado
DISTANCIA_MESMO_ROSTO: float = 1.0  # PROVISÓRIO: centros a até 1 largura de rosto = mesmo rosto acompanhado

# RF05 — olhos (cascata Haar dentro do rosto). RN06: na dúvida, "indeterminado", nunca "fechados"
TAMANHO_MINIMO_ROSTO: int = 120  # PROVISÓRIO: largura mínima do rosto (px da imagem original) para avaliar os olhos
CONTRASTE_MINIMO_ROSTO: float = 20.0  # PROVISÓRIO: desvio padrão mínimo da região do rosto (rosto borrado não serve)
LARGURA_RECORTE_OLHOS: int = 240  # largura (px) para a qual o recorte do rosto é ajustado antes de procurar os olhos
VIZINHOS_OLHOS: int = 5  # PROVISÓRIO: detecções vizinhas exigidas para aceitar um olho
FATOR_ESCALA_OLHOS: float = 1.1  # PROVISÓRIO: passo entre os tamanhos testados pela cascata de olhos
TAMANHO_MINIMO_OLHO: int = 30  # PROVISÓRIO: menor olho procurado, em px do recorte (cerca de 1/8 da largura do rosto)
ALTURA_REGIAO_OLHOS: float = 0.6  # fração de cima do rosto em que os olhos são procurados
FOLGA_ROSTO_QUADROS: int = 3  # PROVISÓRIO: quadros seguidos sem rosto que o acompanhamento tolera antes de reiniciar
QUADROS_OLHOS_FECHADOS: int = 5  # PROVISÓRIO: quadros seguidos sem olhos, num rosto em que já foram vistos, para "fechados"

# RF06 — cabeça
DESLOCAMENTO_CABECA: float = 0.25  # PROVISÓRIO: deslocamento do centro do rosto, em larguras de rosto, para movimento
RAZAO_TAMANHO_ROSTO_MAX: float = 1.5  # PROVISÓRIO: acima desta razão entre os tamanhos, é outra detecção, não movimento
QUADROS_NOVA_ORIENTACAO: int = 2  # PROVISÓRIO: quadros seguidos na nova orientação (frente/perfil) para contar movimento

# RF03 — presença; RF15 — sem presença vira visibilidade insuficiente
JANELA_PRESENCA_S: float = 1800.0  # PROVISÓRIO: presente se houve rosto ou movimento nos últimos 30 min

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
