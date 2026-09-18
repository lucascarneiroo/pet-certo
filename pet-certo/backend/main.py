"""
PetCerto — Backend

Ponto de entrada do servidor. Inicializa o banco de dados (criando as
tabelas na primeira execução, se necessário) e sobe a API HTTP.

Como executar:
    python main.py

A API fica disponível em http://localhost:8000 — ver docs/api.md
(na raiz do repositório) para a lista de rotas.

Credenciais de administrador padrão (criadas automaticamente na
primeira execução):
    e-mail: admin@petcerto.com
    senha:  admin123
"""

from api.server import iniciar_servidor

if __name__ == "__main__":
    iniciar_servidor(host="0.0.0.0", port=8000)
