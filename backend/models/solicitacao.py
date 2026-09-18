"""Representação da entidade Solicitação de Adoção — o fluxo de adoção."""

from dataclasses import dataclass
from typing import Optional

ETAPAS_VALIDAS = ("interesse", "analise", "visita", "documentos", "aprovacao", "concluida")
STATUS_VALIDOS = ("em_andamento", "aprovada", "recusada", "cancelada")

# ordem das etapas, usada pra validar avanço/retrocesso e pra "próxima etapa"
ORDEM_ETAPAS = {etapa: indice for indice, etapa in enumerate(ETAPAS_VALIDAS)}


@dataclass
class SolicitacaoAdocao:
    id: Optional[int]
    animal_id: int
    adotante_id: int
    etapa: str = "interesse"
    status: str = "em_andamento"
    observacoes: Optional[str] = None
    data_solicitacao: Optional[str] = None
    data_atualizacao: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "SolicitacaoAdocao":
        return cls(
            id=row["id"],
            animal_id=row["animal_id"],
            adotante_id=row["adotante_id"],
            etapa=row["etapa"],
            status=row["status"],
            observacoes=row["observacoes"],
            data_solicitacao=row["data_solicitacao"],
            data_atualizacao=row["data_atualizacao"],
        )
