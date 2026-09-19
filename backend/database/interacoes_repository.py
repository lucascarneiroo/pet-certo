"""Favoritos, recomendações, compatibilidade persistida e log administrativo."""
import json
from typing import List, Optional

from database.db import get_connection
from models.interacoes import Compatibilidade, Favorito, Recomendacao, RegistroAdministrativo


class InteracaoInvalidaError(Exception):
    pass


# --------------------------------------------------------------------- Favorito

def favoritar(id_adotante: int, id_animal: int) -> Favorito:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Favorito (idAdotante, idAnimal) VALUES (%s, %s) "
                "ON CONFLICT (idAdotante, idAnimal) DO NOTHING RETURNING idFavorito",
                (id_adotante, id_animal),
            )
            row = cur.fetchone()
            conn.commit()
            if row is None:
                cur.execute(
                    "SELECT * FROM Favorito WHERE idAdotante = %s AND idAnimal = %s",
                    (id_adotante, id_animal),
                )
                return Favorito.from_row(cur.fetchone())
            cur.execute("SELECT * FROM Favorito WHERE idFavorito = %s", (row["idfavorito"],))
            return Favorito.from_row(cur.fetchone())
    finally:
        conn.close()


def desfavoritar(id_adotante: int, id_animal: int) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM Favorito WHERE idAdotante = %s AND idAnimal = %s",
                (id_adotante, id_animal),
            )
        conn.commit()
    finally:
        conn.close()


def listar_favoritos(id_adotante: int) -> list:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT f.*, an.nome AS nomeAnimal, an.status AS statusAnimal
                FROM Favorito f JOIN Animal an ON an.idAnimal = f.idAnimal
                WHERE f.idAdotante = %s ORDER BY f.idFavorito DESC
                """,
                (id_adotante,),
            )
            resultado = []
            for row in cur.fetchall():
                fav = Favorito.from_row(row)
                resultado.append({
                    "id": fav.id, "id_animal": fav.id_animal, "data_favorito": fav.data_favorito,
                    "nome_animal": row["nomeanimal"], "status_animal": row["statusanimal"],
                })
            return resultado
    finally:
        conn.close()


# ----------------------------------------------------------------- Recomendação

def registrar_recomendacao(id_adotante: int, id_animal: int) -> Recomendacao:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Recomendacao (idAdotante, idAnimal) VALUES (%s, %s) RETURNING idRecomendacao",
                (id_adotante, id_animal),
            )
            novo_id = cur.fetchone()["idrecomendacao"]
            conn.commit()
            cur.execute("SELECT * FROM Recomendacao WHERE idRecomendacao = %s", (novo_id,))
            return Recomendacao.from_row(cur.fetchone())
    finally:
        conn.close()


def listar_recomendacoes(id_adotante: int) -> list:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT r.*, an.nome AS nomeAnimal
                FROM Recomendacao r JOIN Animal an ON an.idAnimal = r.idAnimal
                WHERE r.idAdotante = %s ORDER BY r.idRecomendacao DESC
                """,
                (id_adotante,),
            )
            resultado = []
            for row in cur.fetchall():
                r = Recomendacao.from_row(row)
                resultado.append({
                    "id": r.id, "id_animal": r.id_animal,
                    "data_gerada": r.data_gerada, "nome_animal": row["nomeanimal"],
                })
            return resultado
    finally:
        conn.close()


# --------------------------------------------------------------- Compatibilidade

def salvar_compatibilidade(id_adotante: int, id_animal: int, score: int, fatores: dict) -> Compatibilidade:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Compatibilidade (idAdotante, idAnimal, score, fatores) "
                "VALUES (%s, %s, %s, %s) RETURNING idCompatibilidade",
                (id_adotante, id_animal, score, json.dumps(fatores)),
            )
            novo_id = cur.fetchone()["idcompatibilidade"]
            conn.commit()
            cur.execute("SELECT * FROM Compatibilidade WHERE idCompatibilidade = %s", (novo_id,))
            return Compatibilidade.from_row(cur.fetchone())
    finally:
        conn.close()


def buscar_compatibilidade(id_adotante: int, id_animal: int) -> Optional[Compatibilidade]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM Compatibilidade WHERE idAdotante = %s AND idAnimal = %s "
                "ORDER BY idCompatibilidade DESC LIMIT 1",
                (id_adotante, id_animal),
            )
            row = cur.fetchone()
            return Compatibilidade.from_row(row) if row else None
    finally:
        conn.close()


# --------------------------------------------------------- RegistroAdministrativo

def registrar_acao_admin(id_administrador: int, tipo_atividade: str, descricao: str = "") -> RegistroAdministrativo:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO RegistroAdministrativo (idAdministrador, tipoAtividade, descricao) "
                "VALUES (%s, %s, %s) RETURNING idRegistroAdmin",
                (id_administrador, tipo_atividade, descricao),
            )
            novo_id = cur.fetchone()["idregistroadmin"]
            conn.commit()
            cur.execute("SELECT * FROM RegistroAdministrativo WHERE idRegistroAdmin = %s", (novo_id,))
            return RegistroAdministrativo.from_row(cur.fetchone())
    finally:
        conn.close()


def listar_registros_admin() -> List[RegistroAdministrativo]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM RegistroAdministrativo ORDER BY idRegistroAdmin DESC LIMIT 200")
            return [RegistroAdministrativo.from_row(r) for r in cur.fetchall()]
    finally:
        conn.close()
