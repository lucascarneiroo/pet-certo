"""
Serviço de autenticação e cadastro de usuários.

Regras de negócio implementadas aqui:
- Senhas nunca são guardadas em texto puro (hash SHA-256 + salt aleatório).
- E-mail é único no sistema (constraint UNIQUE no banco + verificação aqui).
- Perfil do usuário define o que ele pode acessar no sistema (ver api/server.py).
"""

import hashlib
import os
import sqlite3
from typing import Optional

from database.db import get_connection
from models.usuario import Usuario, PERFIS_VALIDOS


class CredenciaisInvalidasError(Exception):
    """Lançada quando e-mail ou senha estão incorretos no login."""


class EmailJaCadastradoError(Exception):
    """Lançada ao tentar cadastrar um e-mail que já existe."""


class DadosInvalidosError(Exception):
    """Lançada quando algum campo obrigatório é inválido."""


def _gerar_salt() -> str:
    return os.urandom(16).hex()


def _hash_senha(senha: str, salt: str) -> str:
    return hashlib.sha256((salt + senha).encode("utf-8")).hexdigest()


def criar_usuario(
    nome: str,
    email: str,
    senha: str,
    perfil: str,
    instituicao_nome: Optional[str] = None,
    instituicao_cidade: Optional[str] = None,
) -> Usuario:
    """Cadastra um novo usuário no banco. Levanta exceções de negócio
    caso os dados sejam inválidos ou o e-mail já exista.

    Se perfil == "voluntario" e `instituicao_nome` for informado, cria
    a instituição junto (fluxo de autocadastro de ONG) e já vincula o
    usuário a ela. Para vincular um voluntário a uma instituição já
    existente, usar vincular_usuario_a_instituicao() depois."""

    nome = (nome or "").strip()
    email = (email or "").strip().lower()

    if not nome:
        raise DadosInvalidosError("O nome é obrigatório.")
    if not email or "@" not in email:
        raise DadosInvalidosError("Informe um e-mail válido.")
    if not senha or len(senha) < 6:
        raise DadosInvalidosError("A senha deve ter pelo menos 6 caracteres.")
    if perfil not in PERFIS_VALIDOS:
        raise DadosInvalidosError(f"Perfil inválido: {perfil}")

    if buscar_usuario_por_email(email) is not None:
        raise EmailJaCadastradoError("Já existe um usuário cadastrado com esse e-mail.")

    instituicao_id = None
    if perfil == "voluntario" and (instituicao_nome or "").strip():
        from database.instituicao_repository import criar_instituicao
        instituicao = criar_instituicao(nome=instituicao_nome.strip(), cidade=(instituicao_cidade or "").strip())
        instituicao_id = instituicao.id

    salt = _gerar_salt()
    senha_hash = _hash_senha(senha, salt)

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash, salt, perfil, instituicao_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (nome, email, senha_hash, salt, perfil, instituicao_id),
        )
        conn.commit()
        novo_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise EmailJaCadastradoError("Já existe um usuário cadastrado com esse e-mail.")
    finally:
        conn.close()

    return buscar_usuario_por_id(novo_id)


def vincular_usuario_a_instituicao(usuario_id: int, instituicao_id: int) -> Usuario:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE usuarios SET instituicao_id = ? WHERE id = ?",
            (instituicao_id, usuario_id),
        )
        conn.commit()
    finally:
        conn.close()
    return buscar_usuario_por_id(usuario_id)


def autenticar(email: str, senha: str) -> Usuario:
    """Valida credenciais e retorna o Usuario autenticado.
    Levanta CredenciaisInvalidasError se e-mail ou senha estiverem errados."""

    email = (email or "").strip().lower()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise CredenciaisInvalidasError("E-mail ou senha inválidos.")

    senha_hash_calculado = _hash_senha(senha, row["salt"])
    if senha_hash_calculado != row["senha_hash"]:
        raise CredenciaisInvalidasError("E-mail ou senha inválidos.")

    return Usuario.from_row(row)


def buscar_usuario_por_email(email: str) -> Optional[Usuario]:
    email = (email or "").strip().lower()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()
    return Usuario.from_row(row) if row else None


def buscar_usuario_por_id(usuario_id: int) -> Optional[Usuario]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
    finally:
        conn.close()
    return Usuario.from_row(row) if row else None


def listar_usuarios() -> list[Usuario]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM usuarios ORDER BY nome"
        ).fetchall()
    finally:
        conn.close()
    return [Usuario.from_row(r) for r in rows]
