"""RF02, RNF04 — Ler a data e hora que a câmera grava na imagem (carimbo) e converter em tempo real da sessão.

O tempo do próprio arquivo de vídeo não é confiável: a câmera do estudo de caso grava com o relógio do vídeo
um pouco adiantado e para de gravar por trechos sem deixar marca no arquivo. O carimbo da imagem mostra o
horário real de cada quadro.

A leitura usa só OpenCV: o texto branco do canto da imagem é separado em dígitos, e cada dígito é comparado
com os modelos de `digitos_carimbo.npz` (um por algarismo, tirados do carimbo da câmera do estudo de caso).
"""

from datetime import datetime, timedelta
from pathlib import Path

import cv2
import numpy as np

from monitor_sono import config

CAMINHO_MODELOS: Path = Path(__file__).with_name("digitos_carimbo.npz")
DIGITOS_CARIMBO: int = 14  # AAAAMMDDhhmmss
_modelos: np.ndarray | None = None


def _carregar_modelos() -> np.ndarray:
    global _modelos
    if _modelos is None:
        with np.load(CAMINHO_MODELOS) as arquivo:
            _modelos = arquivo["digitos"].astype(np.float32)  # (10, altura, largura), 0 a 1
    return _modelos


def segmentar_digitos(quadro: np.ndarray) -> list[np.ndarray]:
    """RNF04. Separa os dígitos do carimbo, da esquerda para a direita, no tamanho de comparação.

    Devolve uma lista vazia se não encontrar exatamente uma linha com config.DIGITOS_CARIMBO dígitos.
    """
    altura, largura = quadro.shape[:2]
    x0, y0, x1, y1 = config.REGIAO_CARIMBO
    recorte = quadro[int(y0 * altura):int(y1 * altura), int(x0 * largura):int(x1 * largura)]
    branco = recorte.min(axis=2) if recorte.ndim == 3 else recorte
    mascara = (branco >= config.LIMIAR_BRANCO_CARIMBO).astype(np.uint8)

    total, _, caixas, _ = cv2.connectedComponentsWithStats(mascara, connectivity=8)
    minimo, maximo = (f * altura for f in config.ALTURA_DIGITO_CARIMBO)
    candidatos = [
        tuple(int(v) for v in caixas[i][:4])
        for i in range(1, total)
        if minimo <= caixas[i][3] <= maximo and caixas[i][3] >= caixas[i][2]  # dígito: mais alto que largo
    ]
    # Os dígitos do carimbo ficam na mesma linha: agrupa pelo topo e fica com a linha mais cheia.
    linhas: list[list[tuple[int, int, int, int]]] = []
    for caixa in sorted(candidatos, key=lambda c: c[1]):
        if linhas and abs(caixa[1] - linhas[-1][0][1]) <= 0.25 * caixa[3]:
            linhas[-1].append(caixa)
        else:
            linhas.append([caixa])
    linha = max(linhas, key=len, default=[])
    if len(linha) != DIGITOS_CARIMBO:
        return []

    tamanho = config.TAMANHO_DIGITO_CARIMBO
    return [
        cv2.resize(mascara[y:y + a, x:x + l].astype(np.float32), tamanho, interpolation=cv2.INTER_AREA)
        for x, y, l, a in sorted(linha)
    ]


def ler_carimbo(quadro: np.ndarray) -> datetime | None:
    """RF02, RNF04. Data e hora gravadas pela câmera no quadro, ou None se não der para ler com segurança."""
    digitos = segmentar_digitos(quadro)
    if not digitos:
        return None
    modelos = _carregar_modelos()
    texto = ""
    for digito in digitos:
        semelhanca = 1.0 - np.abs(modelos - digito).mean(axis=(1, 2))
        melhor = int(semelhanca.argmax())
        if semelhanca[melhor] < config.SEMELHANCA_MINIMA_CARIMBO:
            return None
        texto += str(melhor)
    try:
        return datetime.strptime(texto, "%Y%m%d%H%M%S")
    except ValueError:  # ex.: mês 13: algum dígito foi mal lido
        return None


class RelogioCarimbo:
    """RF02, RNF04, RN07. Converte o tempo do vídeo em segundos reais desde o início da sessão.

    A câmera do estudo de caso grava de forma irregular: o vídeo corre um pouco mais rápido que o relógio,
    há trechos sem gravação (o carimbo salta para a frente) e trechos gravados duas vezes (o carimbo volta
    alguns segundos). Regras:

    - Sem carimbo legível, o tempo avança junto com o vídeo a partir do último horário aceito.
    - Carimbo coerente com o previsto: o tempo fica dentro do segundo mostrado pelo carimbo.
    - Carimbo à frente do previsto (gravação interrompida): só é aceito quando o quadro seguinte confirma o
      salto, para que um dígito mal lido não crie uma interrupção falsa.
    - Carimbo atrás do tempo já aceito (trecho repetido ou leitura errada): o quadro é ignorado, para que o
      mesmo trecho não seja contado duas vezes.
    - `atualizar` devolve None para um quadro que deve ser ignorado.
    - `origem` é a data e hora real do segundo 0 da sessão, ou None se nenhum carimbo foi lido. Ela só fica
      fixa depois de dois carimbos coerentes seguidos.
    """

    def __init__(self) -> None:
        self.origem: datetime | None = None
        self._origem_confirmada = False
        self._ultimo_video: float | None = None  # segundo do vídeo do último quadro aceito
        self._ultimo_real = 0.0  # segundo real do último quadro aceito
        self._pendente: tuple[float, float] | None = None  # (segundo do vídeo, segundo lido) do salto em dúvida

    def _aceitar(self, segundo_video: float, real: float) -> float:
        self._ultimo_video, self._ultimo_real = segundo_video, real
        return real

    def atualizar(self, segundo_video: float, carimbo: datetime | None) -> float | None:
        """RNF04. Segundo real deste quadro desde o início da sessão, ou None se o quadro deve ser ignorado."""
        if self._ultimo_video is None:  # primeiro quadro: define a origem
            if carimbo is not None:
                self.origem = carimbo - timedelta(seconds=segundo_video)
            return self._aceitar(segundo_video, segundo_video)

        tolerancia = config.TOLERANCIA_CARIMBO_S
        previsto = self._ultimo_real + (segundo_video - self._ultimo_video)
        if carimbo is None:
            return self._aceitar(segundo_video, previsto)
        if not self._origem_confirmada:
            # A origem só vale depois de dois carimbos coerentes: um primeiro carimbo mal lido não pode
            # deslocar a sessão inteira. Enquanto isso, a origem acompanha o carimbo mais recente.
            if self.origem is not None and abs((carimbo - self.origem).total_seconds() - previsto) <= tolerancia:
                self._origem_confirmada = True
            else:
                self.origem = carimbo - timedelta(seconds=previsto)
        lido = (carimbo - self.origem).total_seconds()

        if lido < self._ultimo_real - tolerancia:  # trecho já coberto: repetido ou leitura errada
            self._pendente = None
            return None
        if lido <= previsto + tolerancia:
            self._pendente = None
            # O carimbo mostra o segundo cheio; o tempo nunca volta para trás.
            return self._aceitar(segundo_video, max(min(max(previsto, lido), lido + 0.999), self._ultimo_real))
        if self._pendente is not None and abs(
            (lido - self._pendente[1]) - (segundo_video - self._pendente[0])
        ) <= tolerancia:
            self._pendente = None
            return self._aceitar(segundo_video, lido)  # salto confirmado por dois quadros seguidos
        self._pendente = (segundo_video, lido)
        return None
