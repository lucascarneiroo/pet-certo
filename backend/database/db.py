"""
Conexão com o PostgreSQL e inicialização do banco de dados.

As credenciais NUNCA ficam escritas no código. Elas vêm de variáveis de
ambiente (lidas de um arquivo .env que cada integrante mantém na própria
máquina e que fica fora do Git). Isso evita expor a senha do banco no
repositório e permite que cada um use suas próprias credenciais locais.

Variáveis esperadas (ver .env.example):
    PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
"""
import os
from pathlib import Path

import psycopg2
import psycopg2.extras

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "schema.sql"


def _carregar_dotenv() -> None:
    """Lê um arquivo .env simples (KEY=VALUE por linha) na raiz do backend,
    se existir, sem exigir a biblioteca python-dotenv como dependência."""
    env_path = BASE_DIR.parent / ".env"
    if not env_path.exists():
        return
    for linha in env_path.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        chave = chave.strip()
        valor = valor.strip().strip('"').strip("'")
        os.environ.setdefault(chave, valor)


_carregar_dotenv()


def _config_conexao() -> dict:
    return {
        "host": os.environ.get("PGHOST", "localhost"),
        "port": os.environ.get("PGPORT", "5432"),
        "dbname": os.environ.get("PGDATABASE", "petcerto"),
        "user": os.environ.get("PGUSER", "postgres"),
        "password": os.environ.get("PGPASSWORD", ""),
    }


def get_connection():
    """Retorna uma conexão nova com o PostgreSQL, com cursores em formato
    de dicionário (RealDictCursor), equivalente ao sqlite3.Row usado antes."""
    conn = psycopg2.connect(cursor_factory=psycopg2.extras.RealDictCursor, **_config_conexao())
    return conn


def init_db() -> None:
    """Cria as tabelas (se ainda não existirem), popula as etiquetas padrão
    de características e garante que exista um administrador padrão."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                cur.execute(f.read())
        conn.commit()
    finally:
        conn.close()
    _seed_caracteristicas_padrao()
    _seed_admin_padrao()


def _seed_caracteristicas_padrao() -> None:
    from database.tags_padrao import TODAS_AS_TAGS

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for tag in TODAS_AS_TAGS:
                cur.execute(
                    "INSERT INTO CaracteristicaAnimal (nome) VALUES (%s) "
                    "ON CONFLICT (nome) DO NOTHING",
                    (tag,),
                )
        conn.commit()
    finally:
        conn.close()


def _seed_admin_padrao() -> None:
    """Garante que exista pelo menos um administrador para acessar o sistema
    logo após clonar o projeto (login: admin@petcerto.com / senha: admin123)."""
    from auth.auth_service import gerar_hash_senha

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT idUsuario FROM Usuario WHERE login = %s", ("admin@petcerto.com",))
            if cur.fetchone():
                return
            senha_hash, salt = gerar_hash_senha("admin123")
            cur.execute(
                "INSERT INTO Usuario (login, senha, nomeCompleto) VALUES (%s, %s, %s) "
                "RETURNING idUsuario",
                ("admin@petcerto.com", f"{salt}${senha_hash}", "Administrador Padrão"),
            )
            novo_id = cur.fetchone()["idusuario"]
            cur.execute(
                "INSERT INTO Administrador (idUsuario, permissoes, infoAdmin) VALUES (%s, %s, %s)",
                (novo_id, "total", "Conta criada automaticamente na primeira inicialização."),
            )
        conn.commit()
    finally:
        conn.close()
