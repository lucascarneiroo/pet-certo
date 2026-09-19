"""Sessões em memória (token -> usuario_id). Simples e suficiente para o
escopo do projeto; não sobrevive a um restart do servidor, o que é aceitável
para uma entrega acadêmica local."""
import os
import time
from typing import Optional

_SESSOES = {}
_DURACAO_SESSAO_SEGUNDOS = 8 * 60 * 60  # 8 horas


def criar_sessao(usuario_id: int) -> str:
    token = os.urandom(24).hex()
    _SESSOES[token] = {"usuario_id": usuario_id, "criada_em": time.time()}
    return token


def usuario_id_da_sessao(token: str) -> Optional[int]:
    sessao = _SESSOES.get(token)
    if sessao is None:
        return None
    if time.time() - sessao["criada_em"] > _DURACAO_SESSAO_SEGUNDOS:
        del _SESSOES[token]
        return None
    return sessao["usuario_id"]


def encerrar_sessao(token: str) -> None:
    _SESSOES.pop(token, None)
