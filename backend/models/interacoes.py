"""Modelos de interações e análises: Favorito, Recomendacao, Compatibilidade,
e RegistroAdministrativo (log de ações administrativas)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Favorito:
    id: int
    id_adotante: int
    id_animal: int
    data_favorito: str

    @classmethod
    def from_row(cls, row: dict) -> "Favorito":
        return cls(
            id=row["idfavorito"],
            id_adotante=row["idadotante"],
            id_animal=row["idanimal"],
            data_favorito=str(row["datafavorito"]),
        )


@dataclass
class Recomendacao:
    id: int
    id_adotante: int
    id_animal: int
    data_gerada: str

    @classmethod
    def from_row(cls, row: dict) -> "Recomendacao":
        return cls(
            id=row["idrecomendacao"],
            id_adotante=row["idadotante"],
            id_animal=row["idanimal"],
            data_gerada=str(row["datagerada"]),
        )


@dataclass
class Compatibilidade:
    id: int
    id_adotante: int
    id_animal: int
    score: int
    fatores: Optional[dict]

    @classmethod
    def from_row(cls, row: dict) -> "Compatibilidade":
        return cls(
            id=row["idcompatibilidade"],
            id_adotante=row["idadotante"],
            id_animal=row["idanimal"],
            score=row["score"],
            fatores=row.get("fatores"),
        )


@dataclass
class RegistroAdministrativo:
    id: int
    id_administrador: int
    tipo_atividade: str
    data_hora: str
    descricao: Optional[str]

    @classmethod
    def from_row(cls, row: dict) -> "RegistroAdministrativo":
        return cls(
            id=row["idregistroadmin"],
            id_administrador=row["idadministrador"],
            tipo_atividade=row["tipoatividade"],
            data_hora=str(row["datahora"]),
            descricao=row.get("descricao"),
        )
