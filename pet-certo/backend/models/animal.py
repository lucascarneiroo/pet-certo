"""Representação da entidade Animal (entidade principal do CRUD)."""

from dataclasses import dataclass
from typing import Optional

ESPECIES_VALIDAS = ("cachorro", "gato", "outro")
PORTES_VALIDOS = ("pequeno", "medio", "grande")
ENERGIAS_VALIDAS = ("baixo", "medio", "alto")
ESPACOS_VALIDOS = ("apartamento", "casa_com_quintal", "indiferente")
STATUS_VALIDOS = ("disponivel", "em_processo", "adotado")


@dataclass
class Animal:
    id: Optional[int]
    nome: str
    especie: str
    raca: str
    porte: str
    idade_anos: float
    nivel_energia: str
    temperamento: str
    convive_criancas: bool
    convive_outros_pets: bool
    necessidades_especiais: str
    espaco_recomendado: str
    status: str = "disponivel"
    data_cadastro: Optional[str] = None
    cadastrado_por: Optional[int] = None

    @classmethod
    def from_row(cls, row) -> "Animal":
        return cls(
            id=row["id"],
            nome=row["nome"],
            especie=row["especie"],
            raca=row["raca"],
            porte=row["porte"],
            idade_anos=row["idade_anos"],
            nivel_energia=row["nivel_energia"],
            temperamento=row["temperamento"],
            convive_criancas=bool(row["convive_criancas"]),
            convive_outros_pets=bool(row["convive_outros_pets"]),
            necessidades_especiais=row["necessidades_especiais"],
            espaco_recomendado=row["espaco_recomendado"],
            status=row["status"],
            data_cadastro=row["data_cadastro"],
            cadastrado_por=row["cadastrado_por"],
        )
