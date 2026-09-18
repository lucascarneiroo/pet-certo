"""Representação da entidade Usuário."""

from dataclasses import dataclass
from typing import Optional

PERFIS_VALIDOS = ("admin", "voluntario", "adotante")


@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    perfil: str
    data_cadastro: str
    instituicao_id: Optional[int] = None  # só preenchido para perfil = voluntario

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
        # instituicao_id pode não existir em bancos migrados de uma versão
        # anterior antes do primeiro init_db() rodar — acessa com segurança
        try:
            instituicao_id = row["instituicao_id"]
        except (IndexError, KeyError):
            instituicao_id = None
        return cls(
            id=row["id"],
            nome=row["nome"],
            email=row["email"],
            perfil=row["perfil"],
            data_cadastro=row["data_cadastro"],
            instituicao_id=instituicao_id,
        )
