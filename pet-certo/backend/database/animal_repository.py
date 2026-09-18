"""
Repositório da entidade Animal — CRUD principal do sistema.

Todas as operações são feitas de fato contra o banco SQLite (não há
dados mockados em memória): cadastrar, consultar, atualizar e excluir.
"""

from typing import Optional

from database.db import get_connection
from models.animal import (
    Animal,
    ESPECIES_VALIDAS,
    PORTES_VALIDOS,
    ENERGIAS_VALIDAS,
    ESPACOS_VALIDOS,
)


class DadosDoAnimalInvalidosError(Exception):
    pass


def _validar_animal(
    nome: str,
    especie: str,
    porte: str,
    nivel_energia: str,
    espaco_recomendado: str,
) -> None:
    if not (nome or "").strip():
        raise DadosDoAnimalInvalidosError("O nome do animal é obrigatório.")
    if especie not in ESPECIES_VALIDAS:
        raise DadosDoAnimalInvalidosError(f"Espécie inválida: {especie}")
    if porte not in PORTES_VALIDOS:
        raise DadosDoAnimalInvalidosError(f"Porte inválido: {porte}")
    if nivel_energia not in ENERGIAS_VALIDAS:
        raise DadosDoAnimalInvalidosError(f"Nível de energia inválido: {nivel_energia}")
    if espaco_recomendado not in ESPACOS_VALIDOS:
        raise DadosDoAnimalInvalidosError(f"Espaço recomendado inválido: {espaco_recomendado}")


def criar_animal(
    nome: str,
    especie: str,
    raca: str,
    porte: str,
    idade_anos: float,
    nivel_energia: str,
    temperamento: str,
    convive_criancas: bool,
    convive_outros_pets: bool,
    necessidades_especiais: str,
    espaco_recomendado: str,
    cadastrado_por: Optional[int] = None,
) -> Animal:
    _validar_animal(nome, especie, porte, nivel_energia, espaco_recomendado)

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO animais (
                nome, especie, raca, porte, idade_anos, nivel_energia,
                temperamento, convive_criancas, convive_outros_pets,
                necessidades_especiais, espaco_recomendado, cadastrado_por
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nome.strip(), especie, raca, porte, idade_anos, nivel_energia,
                temperamento, int(convive_criancas), int(convive_outros_pets),
                necessidades_especiais, espaco_recomendado, cadastrado_por,
            ),
        )
        conn.commit()
        novo_id = cursor.lastrowid
    finally:
        conn.close()

    return buscar_animal_por_id(novo_id)


def listar_animais(status: Optional[str] = None) -> list[Animal]:
    conn = get_connection()
    try:
        if status:
            rows = conn.execute(
                "SELECT * FROM animais WHERE status = ? ORDER BY data_cadastro DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM animais ORDER BY data_cadastro DESC"
            ).fetchall()
    finally:
        conn.close()
    return [Animal.from_row(r) for r in rows]


def buscar_animal_por_id(animal_id: int) -> Optional[Animal]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM animais WHERE id = ?", (animal_id,)
        ).fetchone()
    finally:
        conn.close()
    return Animal.from_row(row) if row else None


def atualizar_animal(animal_id: int, **campos) -> Animal:
    """Atualiza os campos informados do animal. Ex:
    atualizar_animal(5, nome="Rex", status="adotado")"""

    atual = buscar_animal_por_id(animal_id)
    if atual is None:
        raise DadosDoAnimalInvalidosError("Animal não encontrado.")

    permitido = {
        "nome", "especie", "raca", "porte", "idade_anos", "nivel_energia",
        "temperamento", "convive_criancas", "convive_outros_pets",
        "necessidades_especiais", "espaco_recomendado", "status",
    }
    campos_validos = {k: v for k, v in campos.items() if k in permitido}
    if not campos_validos:
        return atual

    if "especie" in campos_validos and campos_validos["especie"] not in ESPECIES_VALIDAS:
        raise DadosDoAnimalInvalidosError("Espécie inválida.")
    if "porte" in campos_validos and campos_validos["porte"] not in PORTES_VALIDOS:
        raise DadosDoAnimalInvalidosError("Porte inválido.")

    # normaliza booleanos vindos como True/False (Python) ou 0/1 (JSON)
    for campo_bool in ("convive_criancas", "convive_outros_pets"):
        if campo_bool in campos_validos:
            campos_validos[campo_bool] = int(bool(campos_validos[campo_bool]))

    set_clause = ", ".join(f"{campo} = ?" for campo in campos_validos)
    valores = list(campos_validos.values()) + [animal_id]

    conn = get_connection()
    try:
        conn.execute(f"UPDATE animais SET {set_clause} WHERE id = ?", valores)
        conn.commit()
    finally:
        conn.close()

    return buscar_animal_por_id(animal_id)


def excluir_animal(animal_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM animais WHERE id = ?", (animal_id,))
        conn.commit()
    finally:
        conn.close()
