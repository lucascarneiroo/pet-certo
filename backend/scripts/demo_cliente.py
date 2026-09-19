"""Demonstração simples do backend, para rodar manualmente e ver a API
respondendo de ponta a ponta (health check, listagem de animais e tags)."""
import json
import urllib.request

BASE = "http://localhost:8000"


def get(caminho):
    with urllib.request.urlopen(BASE + caminho) as resp:
        return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    print("Health check:", get("/api/health"))
    print("\nEtiquetas padrão de características:")
    for tag in get("/api/tags")["tags"]:
        print(f"  - {tag}")
    print("\nAnimais cadastrados:")
    for animal in get("/api/animais"):
        print(f"  #{animal['id']} {animal['nome']} ({animal['status']}) - {animal['caracteristicas']}")
    print("\nInstituições cadastradas:")
    for inst in get("/api/instituicoes"):
        print(f"  {inst['nome']} - {inst['localizacao']}")
