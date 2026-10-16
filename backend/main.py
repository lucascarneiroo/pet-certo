"""Ponto de entrada do backend do Pet Certo."""
from api.server import iniciar_servidor
from database.db import init_db

if __name__ == "__main__":
    print("Inicializando banco de dados PostgreSQL (tabelas, etiquetas padrão)...")
    init_db()
    print("Banco pronto.\n")
    iniciar_servidor(host="0.0.0.0", port=8000)
