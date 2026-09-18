"""Representação da entidade Instituição (ONG/abrigo)."""

from dataclasses import dataclass
from typing import Optional

STATUS_VALIDOS = ("verificada", "pendente", "revisao")


@dataclass
class Instituicao:
    id: Optional[int]
    nome: str
    cidade: str
    status: str = "pendente"
    data_cadastro: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Instituicao":
        return cls(
            id=row["id"],
            nome=row["nome"],
            cidade=row["cidade"],
            status=row["status"],
            data_cadastro=row["data_cadastro"],
        )
