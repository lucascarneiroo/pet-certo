"""Modelos do fluxo de adoção: ManifestacaoInteresse, ProcessoAdocao, EtapaAdocao,
HorarioVisita, Visita, Documento, HistoricoProcesso."""
from dataclasses import dataclass
from typing import Optional

# Nomes das etapas, na ordem em que devem acontecer (usado por EtapaAdocao.nome).
ETAPAS_PADRAO = ["Análise", "Visita", "Documentação", "Aprovação"]


@dataclass
class ManifestacaoInteresse:
    id: int
    id_adotante: int
    id_animal: int
    data_manifestacao: str
    status: str  # Pendente | Aprovada | Recusada

    @classmethod
    def from_row(cls, row: dict) -> "ManifestacaoInteresse":
        return cls(
            id=row["idmanifestacao"],
            id_adotante=row["idadotante"],
            id_animal=row["idanimal"],
            data_manifestacao=str(row["datamanifestacao"]),
            status=row["status"],
        )


@dataclass
class ProcessoAdocao:
    id: int
    id_manifestacao: int
    status: str  # Em Andamento | Concluído | Cancelado

    @classmethod
    def from_row(cls, row: dict) -> "ProcessoAdocao":
        return cls(id=row["idprocesso"], id_manifestacao=row["idmanifestacao"], status=row["status"])


@dataclass
class EtapaAdocao:
    id: int
    id_processo: int
    nome: str
    status: str  # Pendente | Em Andamento | Concluída
    data_inicio: str
    data_fim: Optional[str]

    @classmethod
    def from_row(cls, row: dict) -> "EtapaAdocao":
        return cls(
            id=row["idetapa"],
            id_processo=row["idprocesso"],
            nome=row["nome"],
            status=row["status"],
            data_inicio=str(row["datainicio"]),
            data_fim=str(row["datafim"]) if row.get("datafim") else None,
        )


@dataclass
class HorarioVisita:
    id: int
    id_instituicao: int
    data_hora: str
    status: str  # Disponível | Reservado

    @classmethod
    def from_row(cls, row: dict) -> "HorarioVisita":
        return cls(
            id=row["idhorario"],
            id_instituicao=row["idinstituicao"],
            data_hora=str(row["datahora"]),
            status=row["status"],
        )


@dataclass
class Visita:
    id: int
    id_processo: int
    id_horario: Optional[int]
    data_visita: str
    status: str  # Agendada | Realizada | Cancelada
    resultado: Optional[str]

    @classmethod
    def from_row(cls, row: dict) -> "Visita":
        return cls(
            id=row["idvisita"],
            id_processo=row["idprocesso"],
            id_horario=row.get("idhorario"),
            data_visita=str(row["datavisita"]),
            status=row["status"],
            resultado=row.get("resultado"),
        )


@dataclass
class Documento:
    id: int
    id_processo: int
    nome: str
    caminho_arquivo: str
    data_envio: str

    @classmethod
    def from_row(cls, row: dict) -> "Documento":
        return cls(
            id=row["iddocumento"],
            id_processo=row["idprocesso"],
            nome=row["nome"],
            caminho_arquivo=row["caminhoarquivo"],
            data_envio=str(row["dataenvio"]),
        )


@dataclass
class HistoricoProcesso:
    id: int
    id_processo: int
    data_hora: str
    acao: str
    mudanca: Optional[str]

    @classmethod
    def from_row(cls, row: dict) -> "HistoricoProcesso":
        return cls(
            id=row["idhistorico"],
            id_processo=row["idprocesso"],
            data_hora=str(row["datahora"]),
            acao=row["acao"],
            mudanca=row.get("mudanca"),
        )
