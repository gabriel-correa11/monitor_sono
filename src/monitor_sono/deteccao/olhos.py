"""RF05 — Identificar se os olhos estão abertos, fechados ou indeterminado.

Método: cascata Haar de olhos do OpenCV 4.x, só na parte de cima do rosto, recortada da imagem original. A
cascata encontra bem olho aberto e quase nunca olho fechado. Por isso, "não achei olho" **não** quer dizer
"fechados" (RN06). Um quadro sozinho só pode dar "abertos" ou "indeterminado"; "fechados" depende do
acompanhamento do mesmo rosto ao longo dos quadros (AcompanhamentoOlhos).
"""

import cv2
import numpy as np

from monitor_sono import config
from monitor_sono.deteccao.rosto import cascata, cinza, mesmo_rosto
from monitor_sono.tipos import EstadoOlhos, Rosto



def rosto_adequado_para_olhos(quadro: np.ndarray, rosto: Rosto | None) -> bool:
    """RF05, RN06. O rosto permite avaliar os olhos: de frente, grande o bastante e com contraste."""
    if rosto is None or not rosto.frontal or rosto.largura < config.TAMANHO_MINIMO_ROSTO:
        return False
    regiao = cinza(quadro)[rosto.y:rosto.y + rosto.altura, rosto.x:rosto.x + rosto.largura]
    return regiao.size > 0 and float(regiao.std()) >= config.CONTRASTE_MINIMO_ROSTO


def contar_olhos(quadro: np.ndarray, rosto: Rosto) -> int:
    """RF05. Quantos olhos (abertos) a cascata encontra na parte de cima do rosto."""
    altura = max(1, int(rosto.altura * config.ALTURA_REGIAO_OLHOS))
    recorte = cinza(quadro)[rosto.y:rosto.y + altura, rosto.x:rosto.x + rosto.largura]
    if recorte.size == 0:
        return 0
    escala = config.LARGURA_RECORTE_OLHOS / recorte.shape[1]
    recorte = cv2.equalizeHist(cv2.resize(recorte, None, fx=escala, fy=escala, interpolation=cv2.INTER_LINEAR))
    minimo = config.TAMANHO_MINIMO_OLHO
    olhos = cascata("haarcascade_eye.xml").detectMultiScale(
        recorte, scaleFactor=config.FATOR_ESCALA_OLHOS, minNeighbors=config.VIZINHOS_OLHOS, minSize=(minimo, minimo)
    )
    return len(olhos)


def detectar_estado_olhos(quadro: np.ndarray, rosto: Rosto | None, segundo: float) -> EstadoOlhos:
    """RF05, RN06. Estado dos olhos num único quadro: "abertos" ou "indeterminado", nunca "fechados".

    Sem rosto, rosto de perfil, pequeno ou borrado, ou nenhum olho achado: "indeterminado".
    """
    if rosto_adequado_para_olhos(quadro, rosto) and contar_olhos(quadro, rosto) > 0:
        return EstadoOlhos(segundo, "abertos")
    return EstadoOlhos(segundo, "indeterminado")


class AcompanhamentoOlhos:
    """RF05, RN06. Acompanha o mesmo rosto entre quadros e decide quando os olhos estão "fechados".

    "Fechados" só quando tudo vale:
    1. o rosto é adequado (de frente, com config.TAMANHO_MINIMO_ROSTO px e contraste mínimo);
    2. é o mesmo rosto acompanhado (pode sumir por até config.FOLGA_ROSTO_QUADROS quadros seguidos);
    3. olhos abertos já foram vistos nesse acompanhamento;
    4. os olhos estão sumidos há config.QUADROS_OLHOS_FECHADOS quadros adequados seguidos.
    Em qualquer outro caso: "indeterminado".

    Limitação: se o rosto some por mais que a folga, o acompanhamento reinicia e "fechados" só volta
    depois de os olhos serem vistos abertos de novo.
    """

    def __init__(self) -> None:
        self._reiniciar()

    def _reiniciar(self) -> None:
        self._rosto: Rosto | None = None
        self._perdidos = 0
        self._olhos_vistos = False
        self._sem_olhos = 0

    def avaliar(self, quadro: np.ndarray, rosto: Rosto | None, segundo: float) -> EstadoOlhos:
        """RF05, RN06. Estado dos olhos neste quadro, considerando os quadros anteriores."""
        indeterminado = EstadoOlhos(segundo, "indeterminado")
        if rosto is None:
            self._perdidos += 1
            if self._perdidos > config.FOLGA_ROSTO_QUADROS:
                self._reiniciar()
            return indeterminado
        if self._rosto is not None and not mesmo_rosto(self._rosto, rosto):
            self._reiniciar()
        self._rosto, self._perdidos = rosto, 0

        # Quadro em que não dá para avaliar (perfil, pequeno, borrado): não conta a favor nem contra.
        if not rosto_adequado_para_olhos(quadro, rosto):
            return indeterminado
        if contar_olhos(quadro, rosto) > 0:
            self._olhos_vistos, self._sem_olhos = True, 0
            return EstadoOlhos(segundo, "abertos")
        self._sem_olhos += 1
        if self._olhos_vistos and self._sem_olhos >= config.QUADROS_OLHOS_FECHADOS:
            return EstadoOlhos(segundo, "fechados")
        return indeterminado
