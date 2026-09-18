"""
Cliente de demonstração do backend do PetCerto.

Este script NÃO é o frontend do projeto — é uma ferramenta para provar,
sem precisar de nenhum frontend pronto, que a API está funcionando de
ponta a ponta: cadastro, login, e CRUD completo de animais, tudo
batendo de verdade no banco de dados.

Use isso para demonstrar o backend para o professor ou para o grupo
antes do frontend estar pronto.

Como usar:
    1. Em um terminal, inicie o servidor:
       python main.py
    2. Em outro terminal, rode este script:
       python scripts/demo_cliente.py
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"


def chamar(metodo: str, caminho: str, corpo: dict = None, token: str = None):
    url = BASE_URL + caminho
    dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=dados, headers=headers, method=metodo)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def titulo(texto):
    print("\n" + "=" * 60)
    print(texto)
    print("=" * 60)


def main():
    titulo("1. Verificando se o backend e o banco estão de pé")
    status, resp = chamar("GET", "/api/health")
    print(status, resp)
    assert status == 200 and resp["banco_de_dados"] == "conectado"

    titulo("2. Login com o admin padrão")
    status, resp = chamar("POST", "/api/auth/login", {
        "email": "admin@petcerto.com", "senha": "admin123",
    })
    print(status, resp)
    assert status == 200
    token_admin = resp["token"]

    titulo("3. Cadastrando um novo usuário (adotante)")
    status, resp = chamar("POST", "/api/usuarios", {
        "nome": "Maria Silva",
        "email": "maria.demo@teste.com",
        "senha": "senha123",
        "perfil": "adotante",
    })
    print(status, resp)

    titulo("4. Criando um animal (como admin)")
    status, resp = chamar("POST", "/api/animais", {
        "nome": "Rex",
        "especie": "cachorro",
        "raca": "SRD",
        "porte": "medio",
        "idade_anos": 2,
        "nivel_energia": "alto",
        "temperamento": "brincalhao",
        "convive_criancas": True,
        "convive_outros_pets": True,
        "necessidades_especiais": "",
        "espaco_recomendado": "casa_com_quintal",
    }, token=token_admin)
    print(status, resp)
    assert status == 201
    animal_id = resp["id"]

    titulo("5. Listando animais")
    status, resp = chamar("GET", "/api/animais", token=token_admin)
    print(status, resp)
    assert status == 200 and len(resp["animais"]) >= 1

    titulo("6. Atualizando o status do animal para 'adotado'")
    status, resp = chamar("PUT", f"/api/animais/{animal_id}", {
        "status": "adotado",
    }, token=token_admin)
    print(status, resp)
    assert status == 200 and resp["status"] == "adotado"

    titulo("7. Tentando excluir sem permissão (login como adotante)")
    status, resp = chamar("POST", "/api/auth/login", {
        "email": "maria.demo@teste.com", "senha": "senha123",
    })
    token_adotante = resp["token"]
    status, resp = chamar("DELETE", f"/api/animais/{animal_id}", token=token_adotante)
    print(status, resp)
    assert status == 403  # adotante não pode excluir — controle de perfil funcionando

    titulo("8. Excluindo o animal (como admin, agora com permissão)")
    status, resp = chamar("DELETE", f"/api/animais/{animal_id}", token=token_admin)
    print(status, resp)
    assert status == 200

    titulo("TUDO FUNCIONANDO — backend validado de ponta a ponta")


if __name__ == "__main__":
    main()
