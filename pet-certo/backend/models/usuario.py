"""Representação da entidade Usuário."""

from dataclasses import dataclass

PERFIS_VALIDOS = ("admin", "voluntario", "adotante")


@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    perfil: str
    data_cadastro: str

    @property
    def eh_admin(self) -> bool:
        return self.perfil == "admin"

    @property
    def eh_voluntario(self) -> bool:
        return self.perfil == "voluntario"

    @property
    def eh_adotante(self) -> bool:
        return self.perfil == "adotante"

    @classmethod
    def from_row(cls, row) -> "Usuario":
        return cls(
            id=row["id"],
            nome=row["nome"],
            email=row["email"],
            perfil=row["perfil"],
            data_cadastro=row["data_cadastro"],
        )
