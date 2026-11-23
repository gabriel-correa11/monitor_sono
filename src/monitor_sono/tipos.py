"""Contratos entre módulos: formatos dos dados que passam da detecção para a classificação e o registro.

Todos os tempos são em segundos desde o início da sessão (`segundo`, `inicio`, `fim`). O pipeline converte
para data e hora real ao gravar no banco (RNF04).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DeteccaoMovimento:
    """RF07. Resultado da comparação entre dois quadros consecutivos."""

    segundo: float
    fracao_alterada: float  # 0 a 1
    movimento: bool  # RF07
    mudanca_posicao: bool  # RF07, RN05
    mudanca_iluminacao: bool  # luz acesa/apagada: não conta como movimento


@dataclass(frozen=True)
class Visibilidade:
    """RF15. Se a câmera observa adequadamente a cena neste quadro."""

    segundo: float
    adequada: bool
    motivo: str  # "ok", "escura", "sem_contraste" ou "sem_presenca" (RF03)


@dataclass(frozen=True)
class Rosto:
    """RF04. Região do rosto em px da imagem original e se ele está de frente (False = de perfil)."""

    x: int
    y: int
    largura: int
    altura: int
    frontal: bool


@dataclass(frozen=True)
class EstadoOlhos:
    """RF05. Estado dos olhos num quadro. RN06: olho não visível é "indeterminado", nunca "fechados"."""

    segundo: float
    estado: str  # "abertos", "fechados" ou "indeterminado"


@dataclass(frozen=True)
class Intervalo:
    """RF09, RF11. Comportamento ou período observado, com início e fim (RN08)."""

    tipo: str  # um de config.COMPORTAMENTOS
    inicio: float
    fim: float


@dataclass(frozen=True)
class EstadoEstimado:
    """RF10. Estado estimado num intervalo (RN08), com indicação de confiabilidade (RNF09)."""

    estado: str  # um de config.ESTADOS
    inicio: float
    fim: float
    confiavel: bool
