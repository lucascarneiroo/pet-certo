"""Representação da entidade Visita, vinculada a uma solicitação de adoção."""

from dataclasses import dataclass
from typing import Optional

STATUS_VALIDOS = ("agendada", "realizada", "cancelada", "reagendada")


@dataclass
class Visita:
    id: Optional[int]
    solicitacao_id: int
    data_agendada: str
    status: str = "agendada"
    observacoes: Optional[str] = None
    data_cadastro: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Visita":
        return cls(
            id=row["id"],
            solicitacao_id=row["solicitacao_id"],
            data_agendada=row["data_agendada"],
            status=row["status"],
            observacoes=row["observacoes"],
            data_cadastro=row["data_cadastro"],
        )
