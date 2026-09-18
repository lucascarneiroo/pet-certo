"""
Camada de acesso ao banco de dados (SQLite).

Centraliza a conexão e a inicialização do schema. Usar sempre
`get_connection()` para obter uma conexão nova por operação.

Se a equipe decidir trocar de banco no futuro (PostgreSQL, MySQL...),
esta é a única peça que precisa mudar de fato — todo o resto do
backend (auth, crud, api) usa apenas as funções deste módulo e do
animal_repository, sem SQL espalhado pelo código.
"""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "pet_certo.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão com o banco, com row_factory para acessar
    colunas pelo nome (ex: row["nome"])."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Cria as tabelas (se ainda não existirem), aplica migrações leves
    em bancos já existentes de versões anteriores, e garante um usuário
    administrador padrão para o primeiro acesso ao sistema."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()

    conn = get_connection()
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()

    _migrar_schema()
    _seed_admin_padrao()


def _coluna_existe(conn: sqlite3.Connection, tabela: str, coluna: str) -> bool:
    colunas = conn.execute(f"PRAGMA table_info({tabela})").fetchall()
    return any(c["name"] == coluna for c in colunas)


def _migrar_schema() -> None:
    """Ajusta bancos criados por uma versão anterior do schema, que não
    tinham a tabela `instituicoes` nem a coluna `usuarios.instituicao_id`.
    `CREATE TABLE IF NOT EXISTS` não adiciona coluna em tabela que já
    existe, por isso essa etapa é separada."""
    conn = get_connection()
    try:
        if not _coluna_existe(conn, "usuarios", "instituicao_id"):
            conn.execute("ALTER TABLE usuarios ADD COLUMN instituicao_id INTEGER REFERENCES instituicoes(id)")
            conn.commit()
    finally:
        conn.close()


def _seed_admin_padrao() -> None:
    """Garante que exista pelo menos um usuário admin para o primeiro
    acesso. Evita cadastrar duplicado se já existir."""
    from auth.auth_service import criar_usuario, buscar_usuario_por_email

    if buscar_usuario_por_email("admin@petcerto.com") is None:
        criar_usuario(
            nome="Administrador",
            email="admin@petcerto.com",
            senha="admin123",
            perfil="admin",
        )
