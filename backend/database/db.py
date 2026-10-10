"""
Conexão com o PostgreSQL e inicialização do banco de dados.

Usa o pg8000 (driver de PostgreSQL escrito inteiramente em Python, sem
nenhuma extensão compilada) em vez do psycopg2. Motivo: em máquinas
Windows com o Smart App Control ativado, o arquivo .pyd compilado do
psycopg2 é bloqueado por não ser reconhecido como um binário confiável —
e, ao contrário do Windows Defender normal, não existe uma forma de
liberar exceções para o Smart App Control sem reinstalar o Windows. O
pg8000 evita o problema por completo, por não carregar nenhum binário
nativo. Para o resto do backend nada muda: get_connection() continua
devolvendo uma conexão cujo cursor aceita "%s" e cujo fetchone()/
fetchall() devolvem dicionários (coluna -> valor), exatamente como o
RealDictCursor do psycopg2 que era usado antes.

As credenciais NUNCA ficam escritas no código. Elas vêm de variáveis de
ambiente (lidas de um arquivo .env que cada integrante mantém na própria
máquina e que fica fora do Git). Isso evita expor a senha do banco no
repositório e permite que cada um use suas próprias credenciais locais.

Variáveis esperadas (ver .env.example):
    PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
"""
import os
from pathlib import Path

import pg8000.dbapi as pg8000

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
        "port": int(os.environ.get("PGPORT", "5432")),
        "database": os.environ.get("PGDATABASE", "petcerto"),
        "user": os.environ.get("PGUSER", "postgres"),
        "password": os.environ.get("PGPASSWORD", ""),
    }


class _CursorDicionario:
    """Envolve o cursor do pg8000 para que fetchone()/fetchall() devolvam
    dicionários (coluna em minúsculo -> valor), igual ao RealDictCursor do
    psycopg2 que o resto do backend já espera."""

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, params=None):
        self._cursor.execute(sql, params if params is not None else ())
        return self

    def _colunas(self):
        return [d[0] for d in self._cursor.description] if self._cursor.description else []

    def fetchone(self):
        linha = self._cursor.fetchone()
        return dict(zip(self._colunas(), linha)) if linha is not None else None

    def fetchall(self):
        colunas = self._colunas()
        return [dict(zip(colunas, linha)) for linha in self._cursor.fetchall()]

    def __enter__(self):
        return self

    def __exit__(self, *_exc_info):
        self._cursor.close()


class _ConexaoDicionario:
    def __init__(self, conexao):
        self._conexao = conexao

    def cursor(self):
        return _CursorDicionario(self._conexao.cursor())

    def commit(self):
        self._conexao.commit()

    def rollback(self):
        self._conexao.rollback()

    def close(self):
        self._conexao.close()


def get_connection():
    """Retorna uma conexão nova com o PostgreSQL, com cursores em formato
    de dicionário (equivalente ao RealDictCursor do psycopg2 / sqlite3.Row
    usado antes)."""
    conexao = pg8000.connect(**_config_conexao())
    return _ConexaoDicionario(conexao)


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
