"""Repositório da entidade Visita — agendamento dentro do fluxo de adoção."""

from typing import Optional

from database.db import get_connection
from database.solicitacao_repository import buscar_solicitacao_por_id
from models.visita import Visita, STATUS_VALIDOS


class VisitaInvalidaError(Exception):
    pass


def agendar_visita(solicitacao_id: int, data_agendada: str, observacoes: str = "") -> Visita:
    if buscar_solicitacao_por_id(solicitacao_id) is None:
        raise VisitaInvalidaError("Solicitação de adoção não encontrada.")
    if not (data_agendada or "").strip():
        raise VisitaInvalidaError("Informe a data/horário da visita.")

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO visitas (solicitacao_id, data_agendada, observacoes)
            VALUES (?, ?, ?)
            """,
            (solicitacao_id, data_agendada, observacoes or ""),
        )
        conn.commit()
        novo_id = cursor.lastrowid
    finally:
        conn.close()
    return buscar_visita_por_id(novo_id)


def buscar_visita_por_id(visita_id: int) -> Optional[Visita]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM visitas WHERE id = ?", (visita_id,)).fetchone()
    finally:
        conn.close()
    return Visita.from_row(row) if row else None


def listar_visitas_da_solicitacao(solicitacao_id: int) -> list[Visita]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM visitas WHERE solicitacao_id = ? ORDER BY data_agendada",
            (solicitacao_id,),
        ).fetchall()
    finally:
        conn.close()
    return [Visita.from_row(r) for r in rows]


def atualizar_visita(visita_id: int, **campos) -> Visita:
    atual = buscar_visita_por_id(visita_id)
    if atual is None:
        raise VisitaInvalidaError("Visita não encontrada.")

    permitido = {"data_agendada", "status", "observacoes"}
    campos_validos = {k: v for k, v in campos.items() if k in permitido and v is not None}
    if not campos_validos:
        return atual

    if "status" in campos_validos and campos_validos["status"] not in STATUS_VALIDOS:
        raise VisitaInvalidaError("Status de visita inválido.")

    set_clause = ", ".join(f"{campo} = ?" for campo in campos_validos)
    valores = list(campos_validos.values()) + [visita_id]

    conn = get_connection()
    try:
        conn.execute(f"UPDATE visitas SET {set_clause} WHERE id = ?", valores)
        conn.commit()
    finally:
        conn.close()
    return buscar_visita_por_id(visita_id)
