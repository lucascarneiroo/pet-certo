"""Repositório da entidade Instituição (ONG/abrigo)."""

from typing import Optional

from database.db import get_connection
from models.instituicao import Instituicao, STATUS_VALIDOS


class DadosDaInstituicaoInvalidosError(Exception):
    pass


def criar_instituicao(nome: str, cidade: str = "", status: str = "pendente") -> Instituicao:
    if not (nome or "").strip():
        raise DadosDaInstituicaoInvalidosError("O nome da instituição é obrigatório.")
    if status not in STATUS_VALIDOS:
        raise DadosDaInstituicaoInvalidosError(f"Status inválido: {status}")

    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO instituicoes (nome, cidade, status) VALUES (?, ?, ?)",
            (nome.strip(), cidade.strip(), status),
        )
        conn.commit()
        novo_id = cursor.lastrowid
    finally:
        conn.close()
    return buscar_instituicao_por_id(novo_id)


def listar_instituicoes() -> list[Instituicao]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM instituicoes ORDER BY nome").fetchall()
    finally:
        conn.close()
    return [Instituicao.from_row(r) for r in rows]


def buscar_instituicao_por_id(instituicao_id: int) -> Optional[Instituicao]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM instituicoes WHERE id = ?", (instituicao_id,)
        ).fetchone()
    finally:
        conn.close()
    return Instituicao.from_row(row) if row else None


def atualizar_instituicao(instituicao_id: int, **campos) -> Instituicao:
    atual = buscar_instituicao_por_id(instituicao_id)
    if atual is None:
        raise DadosDaInstituicaoInvalidosError("Instituição não encontrada.")

    permitido = {"nome", "cidade", "status"}
    campos_validos = {k: v for k, v in campos.items() if k in permitido and v is not None}
    if not campos_validos:
        return atual

    if "status" in campos_validos and campos_validos["status"] not in STATUS_VALIDOS:
        raise DadosDaInstituicaoInvalidosError("Status inválido.")

    set_clause = ", ".join(f"{campo} = ?" for campo in campos_validos)
    valores = list(campos_validos.values()) + [instituicao_id]

    conn = get_connection()
    try:
        conn.execute(f"UPDATE instituicoes SET {set_clause} WHERE id = ?", valores)
        conn.commit()
    finally:
        conn.close()
    return buscar_instituicao_por_id(instituicao_id)
