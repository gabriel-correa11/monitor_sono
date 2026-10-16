"""RF08, RF12, RNF04, RNF05, RNF09, RNF10 — Banco SQLite local."""

import sqlite3
from datetime import datetime
from pathlib import Path

from monitor_sono import config

ESQUEMA = """
CREATE TABLE IF NOT EXISTS sessoes (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    inicio  TEXT NOT NULL,
    fim     TEXT
);

CREATE TABLE IF NOT EXISTS comportamentos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    sessao_id  INTEGER NOT NULL REFERENCES sessoes(id) ON DELETE CASCADE,
    tipo       TEXT NOT NULL,
    inicio     TEXT NOT NULL,
    fim        TEXT
);

CREATE TABLE IF NOT EXISTS estados (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    sessao_id  INTEGER NOT NULL REFERENCES sessoes(id) ON DELETE CASCADE,
    estado     TEXT NOT NULL,
    inicio     TEXT NOT NULL,
    fim        TEXT,
    confiavel  INTEGER NOT NULL DEFAULT 1
);
"""


def conectar(caminho: Path | None = None) -> sqlite3.Connection:
    """Abre ou cria o banco, ativa chaves estrangeiras e aplica o esquema."""
    caminho = caminho or config.CAMINHO_BANCO
    caminho.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(caminho)
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.row_factory = sqlite3.Row
    conexao.executescript(ESQUEMA)
    return conexao


def criar_sessao(inicio: datetime, caminho: Path | None = None) -> int:
    """RF01. Cria sessão e devolve o id. RNF04."""
    with conectar(caminho) as c:
        cur = c.execute(
            "INSERT INTO sessoes (inicio) VALUES (?)",
            (inicio.isoformat(timespec="seconds"),),
        )
        return cur.lastrowid


def finalizar_sessao(sessao_id: int, fim: datetime, caminho: Path | None = None) -> None:
    """RF01. Registra o fim da sessão. RNF04."""
    with conectar(caminho) as c:
        c.execute(
            "UPDATE sessoes SET fim = ? WHERE id = ?",
            (fim.isoformat(timespec="seconds"), sessao_id),
        )


def excluir_sessao(sessao_id: int, caminho: Path | None = None) -> None:
    """RNF10. Exclui sessão e todos os registros associados (CASCADE). RNF05."""
    with conectar(caminho) as c:
        c.execute("DELETE FROM sessoes WHERE id = ?", (sessao_id,))


def registrar_comportamento(
    sessao_id: int,
    tipo: str,
    inicio: datetime,
    fim: datetime | None = None,
    caminho: Path | None = None,
) -> int:
    """RF08, RF09, RF12. Registra um comportamento observado. RNF04."""
    if tipo not in config.COMPORTAMENTOS:
        raise ValueError(f"Comportamento fora do escopo: {tipo}")
    with conectar(caminho) as c:
        cur = c.execute(
            "INSERT INTO comportamentos (sessao_id, tipo, inicio, fim) VALUES (?, ?, ?, ?)",
            (
                sessao_id,
                tipo,
                inicio.isoformat(timespec="seconds"),
                fim.isoformat(timespec="seconds") if fim else None,
            ),
        )
        return cur.lastrowid


def registrar_estado(
    sessao_id: int,
    estado: str,
    inicio: datetime,
    fim: datetime | None = None,
    confiavel: bool = True,
    caminho: Path | None = None,
) -> int:
    """RF10, RF12. Registra um estado estimado. RNF04, RNF09."""
    with conectar(caminho) as c:
        cur = c.execute(
            "INSERT INTO estados (sessao_id, estado, inicio, fim, confiavel) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                sessao_id,
                estado,
                inicio.isoformat(timespec="seconds"),
                fim.isoformat(timespec="seconds") if fim else None,
                1 if confiavel else 0,
            ),
        )
        return cur.lastrowid


def listar_sessoes(caminho: Path | None = None) -> list[sqlite3.Row]:
    """RF14, RNF10. Lista sessões em ordem decrescente."""
    with conectar(caminho) as c:
        return c.execute("SELECT * FROM sessoes ORDER BY inicio DESC").fetchall()


def comportamentos_da_sessao(sessao_id: int, caminho: Path | None = None) -> list[sqlite3.Row]:
    """RF13, RF14. Comportamentos de uma sessão em ordem cronológica."""
    with conectar(caminho) as c:
        return c.execute(
            "SELECT * FROM comportamentos WHERE sessao_id = ? ORDER BY inicio",
            (sessao_id,),
        ).fetchall()


def estados_da_sessao(sessao_id: int, caminho: Path | None = None) -> list[sqlite3.Row]:
    """RF13, RF14. Estados estimados de uma sessão em ordem cronológica."""
    with conectar(caminho) as c:
        return c.execute(
            "SELECT * FROM estados WHERE sessao_id = ? ORDER BY inicio",
            (sessao_id,),
        ).fetchall()
