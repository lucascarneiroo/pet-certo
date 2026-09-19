from dataclasses import dataclass
from typing import Optional


@dataclass
class Usuario:
    """Representa uma linha da tabela Usuario (a tabela-pai).
    O perfil (adotante / instituicao / administrador) não é uma coluna:
    é descoberto verificando em qual tabela filha existe uma linha com
    o mesmo idUsuario. Por isso este objeto carrega o campo `perfil` já
    resolvido pelo repositório que o montou, mais os dados específicos
    do perfil quando fizer sentido (ex.: instituicao_id para saber a quem
    um animal cadastrado pertence)."""

    id: int
    nome: str
    email: str
    perfil: str  # "adotante" | "instituicao" | "administrador"
    cpf: Optional[str] = None
    endereco: Optional[str] = None
    score_perfil: Optional[float] = None
    cnpj: Optional[str] = None
    localizacao: Optional[str] = None
    info_abrigo: Optional[str] = None
    permissoes: Optional[str] = None
    info_admin: Optional[str] = None

    @property
    def eh_admin(self) -> bool:
        return self.perfil == "administrador"

    @property
    def eh_instituicao(self) -> bool:
        return self.perfil == "instituicao"

    @property
    def eh_adotante(self) -> bool:
        return self.perfil == "adotante"

    @classmethod
    def from_row(cls, row: dict) -> "Usuario":
        return cls(
            id=row["idusuario"],
            nome=row["nomecompleto"],
            email=row["login"],
            perfil=row["perfil"],
            cpf=row.get("cpf"),
            endereco=row.get("endereco"),
            score_perfil=float(row["scoreperfil"]) if row.get("scoreperfil") is not None else None,
            cnpj=row.get("cnpj"),
            localizacao=row.get("localizacao"),
            info_abrigo=row.get("infoabrigo"),
            permissoes=row.get("permissoes"),
            info_admin=row.get("infoadmin"),
        )
