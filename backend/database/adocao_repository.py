"""Fluxo completo de adoção, seguindo o modelo do Henrique:

ManifestacaoInteresse (adotante demonstra interesse em um animal)
  -> quando aprovada, vira um ProcessoAdocao (1:1, idManifestacao é UNIQUE)
     -> o processo tem várias EtapaAdocao (uma linha por etapa: Análise,
        Visita, Documentação, Aprovação), cada uma com seu próprio status
     -> Visita liga o processo a um HorarioVisita oferecido pela instituição
     -> Documento guarda os arquivos enviados durante o processo
     -> HistoricoProcesso registra cada mudança relevante (auditoria)

Regras de negócio replicadas aqui (equivalentes às da versão SQLite):
- só é possível manifestar interesse em animal com status 'Disponível'
- aprovar a manifestação cria o processo e muda o animal para 'Em Processo'
- concluir o processo (adoção efetivada) muda o animal para 'Adotado'
- cancelar/recusar devolve o animal para 'Disponível', só se não houver
  outro processo em andamento para o mesmo animal
"""
from typing import List, Optional

from database.db import get_connection
from models.adocao import (
    Documento,
    EtapaAdocao,
    ETAPAS_PADRAO,
    HistoricoProcesso,
    HorarioVisita,
    ManifestacaoInteresse,
    ProcessoAdocao,
    Visita,
)


class FluxoDeAdocaoInvalidoError(Exception):
    pass


# ---------------------------------------------------------------- Manifestação

def criar_manifestacao(id_adotante: int, id_animal: int) -> ManifestacaoInteresse:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM Animal WHERE idAnimal = %s", (id_animal,))
            animal = cur.fetchone()
            if animal is None:
                raise FluxoDeAdocaoInvalidoError("Animal não encontrado.")
            if animal["status"] != "Disponível":
                raise FluxoDeAdocaoInvalidoError(
                    f"Este animal não está disponível no momento (status atual: {animal['status']})."
                )
            cur.execute(
                "SELECT idManifestacao FROM ManifestacaoInteresse "
                "WHERE idAdotante = %s AND idAnimal = %s AND status = 'Pendente'",
                (id_adotante, id_animal),
            )
            if cur.fetchone():
                raise FluxoDeAdocaoInvalidoError("Você já manifestou interesse por este animal.")
            cur.execute(
                "INSERT INTO ManifestacaoInteresse (idAdotante, idAnimal, status) "
                "VALUES (%s, %s, 'Pendente') RETURNING idManifestacao",
                (id_adotante, id_animal),
            )
            novo_id = cur.fetchone()["idmanifestacao"]
            conn.commit()
            return buscar_manifestacao_por_id(novo_id)
    finally:
        conn.close()


def buscar_manifestacao_por_id(manifestacao_id: int) -> Optional[ManifestacaoInteresse]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ManifestacaoInteresse WHERE idManifestacao = %s", (manifestacao_id,))
            row = cur.fetchone()
            return ManifestacaoInteresse.from_row(row) if row else None
    finally:
        conn.close()


def listar_manifestacoes(id_adotante: Optional[int] = None, id_instituicao: Optional[int] = None) -> list:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            filtros, valores = [], []
            if id_adotante:
                filtros.append("m.idAdotante = %s")
                valores.append(id_adotante)
            if id_instituicao:
                filtros.append("an.idInstituicao = %s")
                valores.append(id_instituicao)
            where = f"WHERE {' AND '.join(filtros)}" if filtros else ""
            cur.execute(
                f"""
                SELECT m.*, an.nome AS nomeAnimal, u.nomeCompleto AS nomeAdotante
                FROM ManifestacaoInteresse m
                JOIN Animal an ON an.idAnimal = m.idAnimal
                JOIN Usuario u ON u.idUsuario = m.idAdotante
                {where}
                ORDER BY m.idManifestacao DESC
                """,
                valores,
            )
            resultado = []
            for row in cur.fetchall():
                m = ManifestacaoInteresse.from_row(row)
                resultado.append({
                    "id": m.id, "id_adotante": m.id_adotante, "id_animal": m.id_animal,
                    "data_manifestacao": m.data_manifestacao, "status": m.status,
                    "nome_animal": row["nomeanimal"], "nome_adotante": row["nomeadotante"],
                })
            return resultado
    finally:
        conn.close()


def aprovar_manifestacao(manifestacao_id: int) -> ProcessoAdocao:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ManifestacaoInteresse WHERE idManifestacao = %s", (manifestacao_id,))
            manifestacao = cur.fetchone()
            if manifestacao is None:
                raise FluxoDeAdocaoInvalidoError("Manifestação não encontrada.")
            if manifestacao["status"] != "Pendente":
                raise FluxoDeAdocaoInvalidoError("Esta manifestação já foi analisada.")

            cur.execute(
                "UPDATE ManifestacaoInteresse SET status = 'Aprovada' WHERE idManifestacao = %s",
                (manifestacao_id,),
            )
            cur.execute(
                "INSERT INTO ProcessoAdocao (idManifestacao, status) VALUES (%s, 'Em Andamento') "
                "RETURNING idProcesso",
                (manifestacao_id,),
            )
            processo_id = cur.fetchone()["idprocesso"]

            for indice, nome_etapa in enumerate(ETAPAS_PADRAO):
                status_etapa = "Em Andamento" if indice == 0 else "Pendente"
                cur.execute(
                    "INSERT INTO EtapaAdocao (idProcesso, nome, status) VALUES (%s, %s, %s)",
                    (processo_id, nome_etapa, status_etapa),
                )

            cur.execute(
                "UPDATE Animal SET status = 'Em Processo' WHERE idAnimal = %s",
                (manifestacao["idanimal"],),
            )
            _registrar_historico(cur, processo_id, "Processo Criado",
                                  "Manifestação de interesse aprovada; processo de adoção iniciado.")
            conn.commit()
            return buscar_processo_por_id(processo_id)
    finally:
        conn.close()


def recusar_manifestacao(manifestacao_id: int) -> ManifestacaoInteresse:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM ManifestacaoInteresse WHERE idManifestacao = %s", (manifestacao_id,))
            row = cur.fetchone()
            if row is None:
                raise FluxoDeAdocaoInvalidoError("Manifestação não encontrada.")
            if row["status"] != "Pendente":
                raise FluxoDeAdocaoInvalidoError("Esta manifestação já foi analisada.")
            cur.execute(
                "UPDATE ManifestacaoInteresse SET status = 'Recusada' WHERE idManifestacao = %s",
                (manifestacao_id,),
            )
            conn.commit()
            return buscar_manifestacao_por_id(manifestacao_id)
    finally:
        conn.close()


# ------------------------------------------------------------------ Processo

def buscar_processo_por_id(processo_id: int) -> Optional[ProcessoAdocao]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ProcessoAdocao WHERE idProcesso = %s", (processo_id,))
            row = cur.fetchone()
            return ProcessoAdocao.from_row(row) if row else None
    finally:
        conn.close()


def _animal_do_processo(cur, processo_id: int) -> dict:
    cur.execute(
        """
        SELECT an.idAnimal, an.status FROM ProcessoAdocao p
        JOIN ManifestacaoInteresse m ON m.idManifestacao = p.idManifestacao
        JOIN Animal an ON an.idAnimal = m.idAnimal
        WHERE p.idProcesso = %s
        """,
        (processo_id,),
    )
    return cur.fetchone()


def listar_processos(id_instituicao: Optional[int] = None, id_adotante: Optional[int] = None) -> list:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            filtros, valores = [], []
            if id_instituicao:
                filtros.append("an.idInstituicao = %s")
                valores.append(id_instituicao)
            if id_adotante:
                filtros.append("m.idAdotante = %s")
                valores.append(id_adotante)
            where = f"WHERE {' AND '.join(filtros)}" if filtros else ""
            cur.execute(
                f"""
                SELECT p.*, m.idAdotante, m.idAnimal, an.nome AS nomeAnimal,
                       u.nomeCompleto AS nomeAdotante
                FROM ProcessoAdocao p
                JOIN ManifestacaoInteresse m ON m.idManifestacao = p.idManifestacao
                JOIN Animal an ON an.idAnimal = m.idAnimal
                JOIN Usuario u ON u.idUsuario = m.idAdotante
                {where}
                ORDER BY p.idProcesso DESC
                """,
                valores,
            )
            resultado = []
            for row in cur.fetchall():
                resultado.append({
                    "id": row["idprocesso"], "status": row["status"],
                    "id_manifestacao": row["idmanifestacao"],
                    "id_adotante": row["idadotante"], "id_animal": row["idanimal"],
                    "nome_animal": row["nomeanimal"], "nome_adotante": row["nomeadotante"],
                })
            return resultado
    finally:
        conn.close()


def _registrar_historico(cur, processo_id: int, acao: str, mudanca: str) -> None:
    cur.execute(
        "INSERT INTO HistoricoProcesso (idProcesso, acao, mudanca) VALUES (%s, %s, %s)",
        (processo_id, acao, mudanca),
    )


def listar_historico(processo_id: int) -> List[HistoricoProcesso]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM HistoricoProcesso WHERE idProcesso = %s ORDER BY idHistorico",
                (processo_id,),
            )
            return [HistoricoProcesso.from_row(r) for r in cur.fetchall()]
    finally:
        conn.close()


def avancar_etapa(processo_id: int, id_etapa: int, novo_status: str, observacao: Optional[str] = None) -> EtapaAdocao:
    if novo_status not in ("Em Andamento", "Concluída", "Reprovada"):
        raise FluxoDeAdocaoInvalidoError("Status de etapa inválido.")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM EtapaAdocao WHERE idEtapa = %s AND idProcesso = %s",
                (id_etapa, processo_id),
            )
            etapa = cur.fetchone()
            if etapa is None:
                raise FluxoDeAdocaoInvalidoError("Etapa não encontrada para este processo.")

            data_fim_sql = "dataFim = CURRENT_TIMESTAMP" if novo_status in ("Concluída", "Reprovada") else "dataFim = NULL"
            cur.execute(
                f"UPDATE EtapaAdocao SET status = %s, {data_fim_sql} WHERE idEtapa = %s",
                (novo_status, id_etapa),
            )
            _registrar_historico(
                cur, processo_id, f"Etapa Atualizada: {etapa['nome']}",
                observacao or f"Status alterado para '{novo_status}'.",
            )

            if novo_status == "Concluída":
                cur.execute(
                    "SELECT idEtapa FROM EtapaAdocao WHERE idProcesso = %s AND status = 'Pendente' "
                    "ORDER BY idEtapa LIMIT 1",
                    (processo_id,),
                )
                proxima = cur.fetchone()
                if proxima:
                    cur.execute(
                        "UPDATE EtapaAdocao SET status = 'Em Andamento' WHERE idEtapa = %s",
                        (proxima["idetapa"],),
                    )
                else:
                    # não há mais etapas pendentes: processo pronto para conclusão
                    pass

            conn.commit()
            cur.execute("SELECT * FROM EtapaAdocao WHERE idEtapa = %s", (id_etapa,))
            return EtapaAdocao.from_row(cur.fetchone())
    finally:
        conn.close()


def listar_etapas(processo_id: int) -> List[EtapaAdocao]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM EtapaAdocao WHERE idProcesso = %s ORDER BY idEtapa", (processo_id,))
            return [EtapaAdocao.from_row(r) for r in cur.fetchall()]
    finally:
        conn.close()


def concluir_processo(processo_id: int) -> ProcessoAdocao:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM ProcessoAdocao WHERE idProcesso = %s", (processo_id,))
            processo = cur.fetchone()
            if processo is None:
                raise FluxoDeAdocaoInvalidoError("Processo não encontrado.")
            if processo["status"] != "Em Andamento":
                raise FluxoDeAdocaoInvalidoError("Só é possível concluir um processo que está em andamento.")

            animal = _animal_do_processo(cur, processo_id)
            cur.execute("UPDATE ProcessoAdocao SET status = 'Concluído' WHERE idProcesso = %s", (processo_id,))
            cur.execute("UPDATE Animal SET status = 'Adotado' WHERE idAnimal = %s", (animal["idanimal"],))
            _registrar_historico(cur, processo_id, "Processo Concluído", "Adoção efetivada com sucesso.")
            conn.commit()
            return buscar_processo_por_id(processo_id)
    finally:
        conn.close()


def cancelar_processo(processo_id: int, motivo: Optional[str] = None) -> ProcessoAdocao:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM ProcessoAdocao WHERE idProcesso = %s", (processo_id,))
            processo = cur.fetchone()
            if processo is None:
                raise FluxoDeAdocaoInvalidoError("Processo não encontrado.")
            if processo["status"] != "Em Andamento":
                raise FluxoDeAdocaoInvalidoError("Este processo já foi finalizado.")

            animal = _animal_do_processo(cur, processo_id)
            cur.execute("UPDATE ProcessoAdocao SET status = 'Cancelado' WHERE idProcesso = %s", (processo_id,))

            cur.execute(
                """
                SELECT COUNT(*) AS total FROM ProcessoAdocao p
                JOIN ManifestacaoInteresse m ON m.idManifestacao = p.idManifestacao
                WHERE m.idAnimal = %s AND p.status = 'Em Andamento' AND p.idProcesso != %s
                """,
                (animal["idanimal"], processo_id),
            )
            outros_ativos = cur.fetchone()["total"]
            if outros_ativos == 0:
                cur.execute("UPDATE Animal SET status = 'Disponível' WHERE idAnimal = %s", (animal["idanimal"],))

            _registrar_historico(cur, processo_id, "Processo Cancelado", motivo or "Processo cancelado.")
            conn.commit()
            return buscar_processo_por_id(processo_id)
    finally:
        conn.close()


# --------------------------------------------------------------- HorarioVisita / Visita

def criar_horario_visita(id_instituicao: int, data_hora: str) -> HorarioVisita:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO HorarioVisita (idInstituicao, dataHora, status) VALUES (%s, %s, 'Disponível') "
                "RETURNING idHorario",
                (id_instituicao, data_hora),
            )
            novo_id = cur.fetchone()["idhorario"]
            conn.commit()
            cur.execute("SELECT * FROM HorarioVisita WHERE idHorario = %s", (novo_id,))
            return HorarioVisita.from_row(cur.fetchone())
    finally:
        conn.close()


def listar_horarios_disponiveis(id_instituicao: int) -> List[HorarioVisita]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM HorarioVisita WHERE idInstituicao = %s AND status = 'Disponível' ORDER BY dataHora",
                (id_instituicao,),
            )
            return [HorarioVisita.from_row(r) for r in cur.fetchall()]
    finally:
        conn.close()


def agendar_visita(processo_id: int, id_horario: int) -> Visita:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM HorarioVisita WHERE idHorario = %s", (id_horario,))
            horario = cur.fetchone()
            if horario is None:
                raise FluxoDeAdocaoInvalidoError("Horário não encontrado.")
            if horario["status"] != "Disponível":
                raise FluxoDeAdocaoInvalidoError("Este horário já foi reservado.")

            cur.execute(
                "INSERT INTO Visita (idProcesso, idHorario, dataVisita, status) "
                "VALUES (%s, %s, %s, 'Agendada') RETURNING idVisita",
                (processo_id, id_horario, horario["datahora"]),
            )
            novo_id = cur.fetchone()["idvisita"]
            cur.execute("UPDATE HorarioVisita SET status = 'Reservado' WHERE idHorario = %s", (id_horario,))
            _registrar_historico(cur, processo_id, "Visita Agendada", f"Visita marcada para {horario['datahora']}.")
            conn.commit()
            cur.execute("SELECT * FROM Visita WHERE idVisita = %s", (novo_id,))
            return Visita.from_row(cur.fetchone())
    finally:
        conn.close()


def listar_visitas_do_processo(processo_id: int) -> List[Visita]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Visita WHERE idProcesso = %s ORDER BY idVisita", (processo_id,))
            return [Visita.from_row(r) for r in cur.fetchall()]
    finally:
        conn.close()


def atualizar_visita(visita_id: int, status: str, resultado: Optional[str] = None) -> Visita:
    if status not in ("Agendada", "Realizada", "Cancelada"):
        raise FluxoDeAdocaoInvalidoError("Status de visita inválido.")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Visita SET status = %s, resultado = COALESCE(%s, resultado) WHERE idVisita = %s",
                (status, resultado, visita_id),
            )
            conn.commit()
            cur.execute("SELECT * FROM Visita WHERE idVisita = %s", (visita_id,))
            row = cur.fetchone()
            if row is None:
                raise FluxoDeAdocaoInvalidoError("Visita não encontrada.")
            return Visita.from_row(row)
    finally:
        conn.close()


# ------------------------------------------------------------------ Documento

def enviar_documento(processo_id: int, nome: str, caminho_arquivo: str) -> Documento:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Documento (idProcesso, nome, caminhoArquivo) VALUES (%s, %s, %s) "
                "RETURNING idDocumento",
                (processo_id, nome, caminho_arquivo),
            )
            novo_id = cur.fetchone()["iddocumento"]
            _registrar_historico(cur, processo_id, "Documento Enviado", f"Arquivo '{nome}' anexado ao processo.")
            conn.commit()
            cur.execute("SELECT * FROM Documento WHERE idDocumento = %s", (novo_id,))
            return Documento.from_row(cur.fetchone())
    finally:
        conn.close()


def listar_documentos(processo_id: int) -> List[Documento]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Documento WHERE idProcesso = %s ORDER BY idDocumento", (processo_id,))
            return [Documento.from_row(r) for r in cur.fetchall()]
    finally:
        conn.close()
