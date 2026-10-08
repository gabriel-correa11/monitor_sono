"""RF07, RF10 — Registrar eventos e consultar sessões (SQLite local, RNF02)."""

import sqlite3
from datetime import datetime
from pathlib import Path

from monitor_sono import config

ESQUEMA = """
CREATE TABLE IF NOT EXISTS sessoes (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    origem  TEXT NOT NULL,
    inicio  TEXT NOT NULL,
    fim     TEXT
);

CREATE TABLE IF NOT EXISTS eventos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    sessao_id  INTEGER NOT NULL REFERENCES sessoes(id),
    tipo       TEXT NOT NULL,
    inicio     TEXT NOT NULL,
    fim        TEXT,
    nivel      REAL
);
"""


def conectar(caminho: Path | None = None) -> sqlite3.Connection:
    caminho = caminho or config.CAMINHO_BANCO
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    conexao.executescript(ESQUEMA)
    return conexao


def criar_sessao(origem: str, inicio: datetime, caminho: Path | None = None) -> int:
    with conectar(caminho) as c:
        cur = c.execute(
            "INSERT INTO sessoes (origem, inicio) VALUES (?, ?)",
            (origem, inicio.isoformat()),
        )
        return cur.lastrowid


def finalizar_sessao(sessao_id: int, fim: datetime, caminho: Path | None = None) -> None:
    with conectar(caminho) as c:
        c.execute("UPDATE sessoes SET fim = ? WHERE id = ?", (fim.isoformat(), sessao_id))


def registrar_evento(
    sessao_id: int,
    tipo: str,
    inicio: datetime,
    fim: datetime | None = None,
    nivel: float | None = None,
    caminho: Path | None = None,
) -> int:
    """RF07. Só aceita tipos em config.TIPOS_EVENTO."""
    if tipo not in config.TIPOS_EVENTO:
        raise ValueError(f"Tipo de evento fora dos requisitos: {tipo}")
    with conectar(caminho) as c:
        cur = c.execute(
            "INSERT INTO eventos (sessao_id, tipo, inicio, fim, nivel) VALUES (?, ?, ?, ?, ?)",
            (sessao_id, tipo, inicio.isoformat(), fim.isoformat() if fim else None, nivel),
        )
        return cur.lastrowid


def listar_sessoes(caminho: Path | None = None) -> list[sqlite3.Row]:
    """RF10."""
    with conectar(caminho) as c:
        return c.execute("SELECT * FROM sessoes ORDER BY inicio DESC").fetchall()


def eventos_da_sessao(sessao_id: int, caminho: Path | None = None) -> list[sqlite3.Row]:
    with conectar(caminho) as c:
        return c.execute(
            "SELECT * FROM eventos WHERE sessao_id = ? ORDER BY inicio", (sessao_id,)
        ).fetchall()
