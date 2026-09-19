"""Cadastro e autenticação de usuários.

No schema do Henrique não existe uma coluna "perfil": existe uma tabela
Usuario (login/senha/nome) e três tabelas filhas (Adotante, Instituicao,
Administrador), cada uma com idUsuario como chave primária e estrangeira.
O perfil de um usuário é, portanto, "em qual tabela filha ele tem uma
linha" — por isso cadastrar um usuário sempre significa duas inserções:
uma em Usuario e outra na tabela do perfil escolhido.
"""
import hashlib
import os
import re
from typing import Optional

from database.db import get_connection
from models.usuario import Usuario

PERFIS_VALIDOS = ("adotante", "instituicao", "administrador")
_REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class DadosInvalidosError(Exception):
    pass


class EmailJaCadastradoError(Exception):
    pass


class CredenciaisInvalidasError(Exception):
    pass


def gerar_hash_senha(senha: str, salt: Optional[str] = None) -> tuple:
    salt = salt or os.urandom(16).hex()
    hash_senha = hashlib.sha256((salt + senha).encode("utf-8")).hexdigest()
    return hash_senha, salt


def _verificar_senha(senha_informada: str, senha_armazenada: str) -> bool:
    # senha_armazenada é guardada no formato "salt$hash" dentro da coluna Usuario.senha
    if "$" not in senha_armazenada:
        return False
    salt, hash_esperado = senha_armazenada.split("$", 1)
    hash_calculado, _ = gerar_hash_senha(senha_informada, salt)
    return hash_calculado == hash_esperado


def _validar_email(email: str) -> None:
    if not email or not _REGEX_EMAIL.match(email):
        raise DadosInvalidosError("E-mail inválido.")


def _montar_usuario(row: dict) -> Usuario:
    perfil = row["perfil"]
    return Usuario.from_row(row)


def _buscar_por_login_sql(cur, login: str) -> Optional[dict]:
    cur.execute(
        """
        SELECT u.idUsuario, u.login, u.senha, u.nomeCompleto,
               a.cpf, a.endereco, a.scorePerfil,
               i.cnpj, i.localizacao, i.infoAbrigo,
               ad.permissoes, ad.infoAdmin,
               CASE
                   WHEN a.idUsuario IS NOT NULL THEN 'adotante'
                   WHEN i.idUsuario IS NOT NULL THEN 'instituicao'
                   WHEN ad.idUsuario IS NOT NULL THEN 'administrador'
               END AS perfil
        FROM Usuario u
        LEFT JOIN Adotante a ON a.idUsuario = u.idUsuario
        LEFT JOIN Instituicao i ON i.idUsuario = u.idUsuario
        LEFT JOIN Administrador ad ON ad.idUsuario = u.idUsuario
        WHERE u.login = %s
        """,
        (login,),
    )
    return cur.fetchone()


def criar_usuario(
    nome: str,
    email: str,
    senha: str,
    perfil: str,
    cpf: Optional[str] = None,
    endereco: Optional[str] = None,
    cnpj: Optional[str] = None,
    localizacao: Optional[str] = None,
    info_abrigo: Optional[str] = None,
) -> Usuario:
    if not nome or not nome.strip():
        raise DadosInvalidosError("Nome é obrigatório.")
    _validar_email(email)
    if not senha or len(senha) < 6:
        raise DadosInvalidosError("Senha deve ter pelo menos 6 caracteres.")
    if perfil not in PERFIS_VALIDOS:
        raise DadosInvalidosError(f"Perfil inválido. Use um de: {', '.join(PERFIS_VALIDOS)}.")
    if perfil == "adotante" and (not cpf or not endereco):
        raise DadosInvalidosError("Adotante precisa de CPF e endereço.")
    if perfil == "instituicao" and (not cnpj or not localizacao):
        raise DadosInvalidosError("Instituição precisa de CNPJ e localização.")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT idUsuario FROM Usuario WHERE login = %s", (email,))
            if cur.fetchone():
                raise EmailJaCadastradoError("Já existe uma conta com este e-mail.")

            senha_hash, salt = gerar_hash_senha(senha)
            cur.execute(
                "INSERT INTO Usuario (login, senha, nomeCompleto) VALUES (%s, %s, %s) RETURNING idUsuario",
                (email, f"{salt}${senha_hash}", nome.strip()),
            )
            novo_id = cur.fetchone()["idusuario"]

            if perfil == "adotante":
                cur.execute(
                    "INSERT INTO Adotante (idUsuario, cpf, endereco, scorePerfil) VALUES (%s, %s, %s, %s)",
                    (novo_id, cpf.strip(), endereco.strip(), 0),
                )
            elif perfil == "instituicao":
                cur.execute(
                    "INSERT INTO Instituicao (idUsuario, cnpj, localizacao, infoAbrigo) VALUES (%s, %s, %s, %s)",
                    (novo_id, cnpj.strip(), localizacao.strip(), info_abrigo),
                )
            else:  # administrador
                cur.execute(
                    "INSERT INTO Administrador (idUsuario, permissoes, infoAdmin) VALUES (%s, %s, %s)",
                    (novo_id, "padrao", None),
                )
            conn.commit()
            row = _buscar_por_login_sql(cur, email)
            return _montar_usuario(row)
    finally:
        conn.close()


def autenticar(email: str, senha: str) -> Usuario:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            row = _buscar_por_login_sql(cur, email)
            if row is None or not _verificar_senha(senha, row["senha"]):
                raise CredenciaisInvalidasError("E-mail ou senha inválidos.")
            return _montar_usuario(row)
    finally:
        conn.close()


def buscar_usuario_por_email(email: str) -> Optional[Usuario]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            row = _buscar_por_login_sql(cur, email)
            return _montar_usuario(row) if row else None
    finally:
        conn.close()


def buscar_usuario_por_id(usuario_id: int) -> Optional[Usuario]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.idUsuario, u.login, u.senha, u.nomeCompleto,
                       a.cpf, a.endereco, a.scorePerfil,
                       i.cnpj, i.localizacao, i.infoAbrigo,
                       ad.permissoes, ad.infoAdmin,
                       CASE
                           WHEN a.idUsuario IS NOT NULL THEN 'adotante'
                           WHEN i.idUsuario IS NOT NULL THEN 'instituicao'
                           WHEN ad.idUsuario IS NOT NULL THEN 'administrador'
                       END AS perfil
                FROM Usuario u
                LEFT JOIN Adotante a ON a.idUsuario = u.idUsuario
                LEFT JOIN Instituicao i ON i.idUsuario = u.idUsuario
                LEFT JOIN Administrador ad ON ad.idUsuario = u.idUsuario
                WHERE u.idUsuario = %s
                """,
                (usuario_id,),
            )
            row = cur.fetchone()
            return _montar_usuario(row) if row else None
    finally:
        conn.close()


def listar_instituicoes() -> list:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.idUsuario, u.login, u.nomeCompleto, i.cnpj, i.localizacao, i.infoAbrigo
                FROM Instituicao i JOIN Usuario u ON u.idUsuario = i.idUsuario
                ORDER BY u.nomeCompleto
                """
            )
            linhas = cur.fetchall()
            return [
                {
                    "id": r["idusuario"],
                    "nome": r["nomecompleto"],
                    "email": r["login"],
                    "cnpj": r["cnpj"],
                    "localizacao": r["localizacao"],
                    "info_abrigo": r["infoabrigo"],
                }
                for r in linhas
            ]
    finally:
        conn.close()
