"""CRUD de animais + gestão das etiquetas (características) via
CaracteristicaAnimal / AnimalCaracteristica."""
from typing import List, Optional

from database.db import get_connection
from database.tags_padrao import TODAS_AS_TAGS
from models.animal import Animal


class DadosDoAnimalInvalidosError(Exception):
    pass


def _buscar_caracteristicas_do_animal(cur, animal_id: int) -> List[str]:
    cur.execute(
        """
        SELECT ca.nome FROM AnimalCaracteristica ac
        JOIN CaracteristicaAnimal ca ON ca.idCaracteristica = ac.idCaracteristica
        WHERE ac.idAnimal = %s
        ORDER BY ca.nome
        """,
        (animal_id,),
    )
    return [r["nome"] for r in cur.fetchall()]


def _validar_tags(tags: List[str]) -> None:
    invalidas = [t for t in tags if t not in TODAS_AS_TAGS]
    if invalidas:
        raise DadosDoAnimalInvalidosError(
            f"Características inválidas: {', '.join(invalidas)}. "
            f"Use apenas etiquetas do conjunto padrão."
        )


def _definir_caracteristicas(cur, animal_id: int, tags: List[str]) -> None:
    _validar_tags(tags)
    cur.execute("DELETE FROM AnimalCaracteristica WHERE idAnimal = %s", (animal_id,))
    if not tags:
        return
    cur.execute(
        "SELECT idCaracteristica, nome FROM CaracteristicaAnimal WHERE nome = ANY(%s)",
        (tags,),
    )
    ids = [r["idcaracteristica"] for r in cur.fetchall()]
    for id_caracteristica in ids:
        cur.execute(
            "INSERT INTO AnimalCaracteristica (idAnimal, idCaracteristica) VALUES (%s, %s) "
            "ON CONFLICT DO NOTHING",
            (animal_id, id_caracteristica),
        )


def criar_animal(id_instituicao: int, nome: str, data_nascimento: Optional[str], caracteristicas: List[str]) -> Animal:
    if not nome or not nome.strip():
        raise DadosDoAnimalInvalidosError("Nome do animal é obrigatório.")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Animal (idInstituicao, nome, dataNascimento, status) "
                "VALUES (%s, %s, %s, 'Disponível') RETURNING idAnimal",
                (id_instituicao, nome.strip(), data_nascimento),
            )
            novo_id = cur.fetchone()["idanimal"]
            _definir_caracteristicas(cur, novo_id, caracteristicas or [])
            conn.commit()
            return buscar_animal_por_id(novo_id)
    finally:
        conn.close()


def listar_animais(status: Optional[str] = None, id_instituicao: Optional[int] = None) -> List[Animal]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            filtros, valores = [], []
            if status:
                filtros.append("a.status = %s")
                valores.append(status)
            if id_instituicao:
                filtros.append("a.idInstituicao = %s")
                valores.append(id_instituicao)
            where = f"WHERE {' AND '.join(filtros)}" if filtros else ""
            cur.execute(
                f"""
                SELECT a.*, u.nomeCompleto AS nomeInstituicao
                FROM Animal a JOIN Instituicao i ON i.idUsuario = a.idInstituicao
                JOIN Usuario u ON u.idUsuario = i.idUsuario
                {where}
                ORDER BY a.idAnimal DESC
                """,
                valores,
            )
            linhas = cur.fetchall()
            resultado = []
            for row in linhas:
                tags = _buscar_caracteristicas_do_animal(cur, row["idanimal"])
                resultado.append(Animal.from_row(row, tags))
            return resultado
    finally:
        conn.close()


def buscar_animal_por_id(animal_id: int) -> Optional[Animal]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT a.*, u.nomeCompleto AS nomeInstituicao
                FROM Animal a JOIN Instituicao i ON i.idUsuario = a.idInstituicao
                JOIN Usuario u ON u.idUsuario = i.idUsuario
                WHERE a.idAnimal = %s
                """,
                (animal_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            tags = _buscar_caracteristicas_do_animal(cur, animal_id)
            return Animal.from_row(row, tags)
    finally:
        conn.close()


def atualizar_animal(animal_id: int, **campos) -> Optional[Animal]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            caracteristicas = campos.pop("caracteristicas", None)
            colunas_permitidas = {"nome": "nome", "data_nascimento": "dataNascimento", "status": "status"}
            sets, valores = [], []
            for chave, valor in campos.items():
                if chave in colunas_permitidas and valor is not None:
                    sets.append(f"{colunas_permitidas[chave]} = %s")
                    valores.append(valor)
            if sets:
                valores.append(animal_id)
                cur.execute(f"UPDATE Animal SET {', '.join(sets)} WHERE idAnimal = %s", valores)
            if caracteristicas is not None:
                _definir_caracteristicas(cur, animal_id, caracteristicas)
            conn.commit()
            return buscar_animal_por_id(animal_id)
    finally:
        conn.close()


def excluir_animal(animal_id: int) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Animal WHERE idAnimal = %s", (animal_id,))
        conn.commit()
    finally:
        conn.close()
