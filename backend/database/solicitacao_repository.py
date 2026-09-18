"""
Repositório da entidade Solicitação de Adoção — o fluxo de adoção em si.

Regras de negócio implementadas aqui (não só CRUD):
- Só é possível solicitar um animal que esteja com status "disponivel".
- Ao criar uma solicitação, o animal passa automaticamente para
  "em_processo" (fica reservado enquanto o processo corre).
- Um mesmo adotante não pode ter duas solicitações em andamento para o
  mesmo animal.
- A etapa só pode avançar para frente (não dá pra "voltar o tempo"
  clicando errado) — reflete o funil mostrado nas telas do frontend:
  interesse -> análise -> visita -> documentos -> aprovação -> concluída.
- Aprovar a solicitação marca o animal como "adotado". Recusar ou
  cancelar devolve o animal para "disponivel" (a não ser que outra
  solicitação para o mesmo animal já esteja em andamento).
"""

from typing import Optional

from database.db import get_connection
from database.animal_repository import buscar_animal_por_id, atualizar_animal
from models.solicitacao import SolicitacaoAdocao, ETAPAS_VALIDAS, STATUS_VALIDOS, ORDEM_ETAPAS


class SolicitacaoInvalidaError(Exception):
    pass


def criar_solicitacao(animal_id: int, adotante_id: int, observacoes: str = "") -> SolicitacaoAdocao:
    animal = buscar_animal_por_id(animal_id)
    if animal is None:
        raise SolicitacaoInvalidaError("Animal não encontrado.")
    if animal.status != "disponivel":
        raise SolicitacaoInvalidaError(
            f"Este animal não está disponível para adoção no momento (status atual: {animal.status})."
        )

    conn = get_connection()
    try:
        ja_existe = conn.execute(
            """
            SELECT 1 FROM solicitacoes_adocao
            WHERE animal_id = ? AND adotante_id = ? AND status = 'em_andamento'
            """,
            (animal_id, adotante_id),
        ).fetchone()
        if ja_existe:
            raise SolicitacaoInvalidaError("Você já tem uma solicitação em andamento para este animal.")

        cursor = conn.execute(
            """
            INSERT INTO solicitacoes_adocao (animal_id, adotante_id, observacoes)
            VALUES (?, ?, ?)
            """,
            (animal_id, adotante_id, observacoes or ""),
        )
        conn.commit()
        novo_id = cursor.lastrowid
    finally:
        conn.close()

    atualizar_animal(animal_id, status="em_processo")
    return buscar_solicitacao_por_id(novo_id)


def buscar_solicitacao_por_id(solicitacao_id: int) -> Optional[SolicitacaoAdocao]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM solicitacoes_adocao WHERE id = ?", (solicitacao_id,)
        ).fetchone()
    finally:
        conn.close()
    return SolicitacaoAdocao.from_row(row) if row else None


def listar_solicitacoes_do_adotante(adotante_id: int) -> list[SolicitacaoAdocao]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM solicitacoes_adocao WHERE adotante_id = ? ORDER BY data_solicitacao DESC",
            (adotante_id,),
        ).fetchall()
    finally:
        conn.close()
    return [SolicitacaoAdocao.from_row(r) for r in rows]


def listar_solicitacoes_do_animal(animal_id: int) -> list[SolicitacaoAdocao]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM solicitacoes_adocao WHERE animal_id = ? ORDER BY data_solicitacao DESC",
            (animal_id,),
        ).fetchall()
    finally:
        conn.close()
    return [SolicitacaoAdocao.from_row(r) for r in rows]


def listar_solicitacoes_da_instituicao(instituicao_id: int) -> list[SolicitacaoAdocao]:
    """Todas as solicitações de animais cadastrados por usuários
    vinculados a essa instituição — é assim que a tela 'Solicitações' da
    ONG (frontend) enxerga o funil."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT s.* FROM solicitacoes_adocao s
            JOIN animais a ON a.id = s.animal_id
            JOIN usuarios u ON u.id = a.cadastrado_por
            WHERE u.instituicao_id = ?
            ORDER BY s.data_solicitacao DESC
            """,
            (instituicao_id,),
        ).fetchall()
    finally:
        conn.close()
    return [SolicitacaoAdocao.from_row(r) for r in rows]


def listar_todas_solicitacoes() -> list[SolicitacaoAdocao]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM solicitacoes_adocao ORDER BY data_solicitacao DESC"
        ).fetchall()
    finally:
        conn.close()
    return [SolicitacaoAdocao.from_row(r) for r in rows]


def avancar_etapa(solicitacao_id: int, nova_etapa: str) -> SolicitacaoAdocao:
    solicitacao = buscar_solicitacao_por_id(solicitacao_id)
    if solicitacao is None:
        raise SolicitacaoInvalidaError("Solicitação não encontrada.")
    if solicitacao.status != "em_andamento":
        raise SolicitacaoInvalidaError("Esta solicitação já foi encerrada (aprovada/recusada/cancelada).")
    if nova_etapa not in ETAPAS_VALIDAS:
        raise SolicitacaoInvalidaError(f"Etapa inválida: {nova_etapa}")
    if ORDEM_ETAPAS[nova_etapa] < ORDEM_ETAPAS[solicitacao.etapa]:
        raise SolicitacaoInvalidaError(
            f"Não é possível voltar de '{solicitacao.etapa}' para '{nova_etapa}'."
        )

    conn = get_connection()
    try:
        conn.execute(
            "UPDATE solicitacoes_adocao SET etapa = ?, data_atualizacao = datetime('now') WHERE id = ?",
            (nova_etapa, solicitacao_id),
        )
        conn.commit()
    finally:
        conn.close()
    return buscar_solicitacao_por_id(solicitacao_id)


def atualizar_status(solicitacao_id: int, novo_status: str, observacoes: Optional[str] = None) -> SolicitacaoAdocao:
    solicitacao = buscar_solicitacao_por_id(solicitacao_id)
    if solicitacao is None:
        raise SolicitacaoInvalidaError("Solicitação não encontrada.")
    if novo_status not in STATUS_VALIDOS:
        raise SolicitacaoInvalidaError(f"Status inválido: {novo_status}")

    conn = get_connection()
    try:
        if observacoes is not None:
            conn.execute(
                "UPDATE solicitacoes_adocao SET status = ?, observacoes = ?, data_atualizacao = datetime('now') WHERE id = ?",
                (novo_status, observacoes, solicitacao_id),
            )
        else:
            conn.execute(
                "UPDATE solicitacoes_adocao SET status = ?, data_atualizacao = datetime('now') WHERE id = ?",
                (novo_status, solicitacao_id),
            )
        if novo_status == "aprovada":
            conn.execute(
                "UPDATE solicitacoes_adocao SET etapa = 'concluida' WHERE id = ?", (solicitacao_id,)
            )
        conn.commit()
    finally:
        conn.close()

    if novo_status == "aprovada":
        atualizar_animal(solicitacao.animal_id, status="adotado")
    elif novo_status in ("recusada", "cancelada"):
        # só libera o animal de volta se não houver outra solicitação em andamento pra ele
        outras_em_andamento = [
            s for s in listar_solicitacoes_do_animal(solicitacao.animal_id)
            if s.id != solicitacao_id and s.status == "em_andamento"
        ]
        if not outras_em_andamento:
            atualizar_animal(solicitacao.animal_id, status="disponivel")

    return buscar_solicitacao_por_id(solicitacao_id)
