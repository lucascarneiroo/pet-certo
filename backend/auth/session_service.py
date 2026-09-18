"""
Gerenciamento de sessões (tokens) para autenticação da API.

Como a API é stateless por natureza (cada requisição HTTP é
independente), o cliente (frontend) precisa provar quem é a cada
chamada. A solução mais simples, sem bibliotecas externas de JWT: ao
fazer login, o backend gera um token aleatório e guarda a relação
token -> usuário. O frontend guarda esse token e o envia no cabeçalho
'Authorization: Bearer <token>' em toda requisição autenticada.

Implementação em memória — adequada para desenvolvimento e
demonstração local desta sprint. Se, mais adiante, o backend precisar
rodar em vários processos/servidores ao mesmo tempo, essa é a peça a
trocar por algo como JWT (que não depende de estado guardado no
servidor) ou por uma tabela de sessões no banco.
"""

import secrets
import time
from typing import Optional

from models.usuario import Usuario
from auth.auth_service import buscar_usuario_por_id

_SESSOES: dict[str, dict] = {}  # token -> {"usuario_id": int, "criado_em": float}
_VALIDADE_SEGUNDOS = 8 * 60 * 60  # sessão expira em 8 horas


def criar_sessao(usuario_id: int) -> str:
    token = secrets.token_hex(32)
    _SESSOES[token] = {"usuario_id": usuario_id, "criado_em": time.time()}
    return token


def usuario_da_sessao(token: str) -> Optional[Usuario]:
    sessao = _SESSOES.get(token)
    if sessao is None:
        return None
    if time.time() - sessao["criado_em"] > _VALIDADE_SEGUNDOS:
        del _SESSOES[token]
        return None
    return buscar_usuario_por_id(sessao["usuario_id"])


def encerrar_sessao(token: str) -> None:
    _SESSOES.pop(token, None)
