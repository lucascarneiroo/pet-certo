from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Animal:
    id: int
    id_instituicao: int
    nome: str
    data_nascimento: Optional[str]
    status: str  # 'Disponível' | 'Em Processo' | 'Adotado'
    caracteristicas: List[str] = field(default_factory=list)
    nome_instituicao: Optional[str] = None

    @classmethod
    def from_row(cls, row: dict, caracteristicas: Optional[List[str]] = None) -> "Animal":
        return cls(
            id=row["idanimal"],
            id_instituicao=row["idinstituicao"],
            nome=row["nome"],
            data_nascimento=str(row["datanascimento"]) if row.get("datanascimento") else None,
            status=row["status"],
            caracteristicas=caracteristicas or [],
            nome_instituicao=row.get("nomeinstituicao"),
        )
