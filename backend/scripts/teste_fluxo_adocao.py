"""
Testa de ponta a ponta o fluxo de adoção completo: instituição,
animal, adotante, solicitação, visita, aprovação — e confere que as
regras de permissão (instituição só mexe no que é dela) funcionam.

Como usar:
    python main.py                       (em um terminal)
    python scripts/teste_fluxo_adocao.py  (em outro terminal)
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"


def chamar(metodo, caminho, corpo=None, token=None):
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
    print("\n" + "=" * 65)
    print(texto)
    print("=" * 65)


def main():
    titulo("1. Cadastro da instituição (ONG) via autocadastro")
    status, resp = chamar("POST", "/api/usuarios", {
        "nome": "Ana Souza", "email": "ana@amoranimal.org", "senha": "senha123",
        "perfil": "voluntario", "instituicao_nome": "Instituto Amor Animal", "instituicao_cidade": "Recife",
    })
    print(status, resp)
    assert status == 201
    instituicao_id = resp["instituicao_id"]
    assert instituicao_id is not None, "usuário deveria já vir vinculado à instituição criada"

    status, resp = chamar("POST", "/api/auth/login", {"email": "ana@amoranimal.org", "senha": "senha123"})
    token_instituicao = resp["token"]

    titulo("2. Segunda instituição, pra testar isolamento (não deve enxergar dados da primeira)")
    chamar("POST", "/api/usuarios", {
        "nome": "Carlos Lima", "email": "carlos@patinhas.org", "senha": "senha123",
        "perfil": "voluntario", "instituicao_nome": "Projeto Patinhas", "instituicao_cidade": "Campinas",
    })
    status, resp = chamar("POST", "/api/auth/login", {"email": "carlos@patinhas.org", "senha": "senha123"})
    token_outra_instituicao = resp["token"]

    titulo("3. Instituição cadastra um animal")
    status, resp = chamar("POST", "/api/animais", {
        "nome": "Luna", "especie": "cachorro", "raca": "SRD", "porte": "medio", "idade_anos": 2,
        "nivel_energia": "medio", "temperamento": "Carinhosa", "convive_criancas": True,
        "convive_outros_pets": True, "necessidades_especiais": "", "espaco_recomendado": "apartamento",
    }, token=token_instituicao)
    print(status, resp)
    animal_id = resp["id"]

    titulo("4. Adotante se cadastra e solicita adoção")
    chamar("POST", "/api/usuarios", {
        "nome": "Marina Oliveira", "email": "marina@email.com", "senha": "senha123", "perfil": "adotante",
    })
    status, resp = chamar("POST", "/api/auth/login", {"email": "marina@email.com", "senha": "senha123"})
    token_adotante = resp["token"]

    status, resp = chamar("POST", "/api/solicitacoes", {
        "animal_id": animal_id, "observacoes": "Tenho apartamento e experiência com cães.",
    }, token=token_adotante)
    print(status, resp)
    assert status == 201
    solicitacao_id = resp["id"]
    assert resp["etapa"] == "interesse"

    titulo("5. Animal deve ter virado 'em_processo' automaticamente")
    status, resp = chamar("GET", f"/api/animais/{animal_id}", token=token_adotante)
    print("status do animal:", resp["status"])
    assert resp["status"] == "em_processo"

    titulo("6. Segunda solicitação pro mesmo animal deve ser bloqueada (não está mais disponível)")
    chamar("POST", "/api/usuarios", {
        "nome": "Paulo Mendes", "email": "paulo@email.com", "senha": "senha123", "perfil": "adotante",
    })
    status, resp = chamar("POST", "/api/auth/login", {"email": "paulo@email.com", "senha": "senha123"})
    token_outro_adotante = resp["token"]
    status, resp = chamar("POST", "/api/solicitacoes", {"animal_id": animal_id}, token=token_outro_adotante)
    print(status, resp)
    assert status == 400

    titulo("7. A OUTRA instituição NÃO pode mexer nessa solicitação (isolamento)")
    status, resp = chamar("PUT", f"/api/solicitacoes/{solicitacao_id}", {"etapa": "analise"}, token=token_outra_instituicao)
    print(status, resp)
    assert status == 403

    titulo("8. A instituição dona do animal avança a etapa pra 'análise'")
    status, resp = chamar("PUT", f"/api/solicitacoes/{solicitacao_id}", {"etapa": "analise"}, token=token_instituicao)
    print(status, resp)
    assert status == 200 and resp["etapa"] == "analise"

    titulo("9. Instituição agenda uma visita (isso já avança a etapa pra 'visita' automaticamente)")
    status, resp = chamar("POST", f"/api/solicitacoes/{solicitacao_id}/visitas", {
        "data_agendada": "2026-10-05 14:00", "observacoes": "Levar comprovante de residência.",
    }, token=token_instituicao)
    print(status, resp)
    assert status == 201
    visita_id = resp["id"]

    status, resp = chamar("GET", f"/api/solicitacoes/{solicitacao_id}", token=token_instituicao)
    print("etapa da solicitação agora:", resp["etapa"])
    assert resp["etapa"] == "visita"

    titulo("10. Instituição marca a visita como realizada")
    status, resp = chamar("PUT", f"/api/visitas/{visita_id}", {"status": "realizada"}, token=token_instituicao)
    print(status, resp)
    assert status == 200 and resp["status"] == "realizada"

    titulo("11. Avança pra documentos e aprovação, depois aprova a adoção")
    chamar("PUT", f"/api/solicitacoes/{solicitacao_id}", {"etapa": "documentos"}, token=token_instituicao)
    chamar("PUT", f"/api/solicitacoes/{solicitacao_id}", {"etapa": "aprovacao"}, token=token_instituicao)
    status, resp = chamar("PUT", f"/api/solicitacoes/{solicitacao_id}", {"status": "aprovada"}, token=token_instituicao)
    print(status, resp)
    assert status == 200 and resp["status"] == "aprovada" and resp["etapa"] == "concluida"

    titulo("12. Animal deve estar 'adotado' agora")
    status, resp = chamar("GET", f"/api/animais/{animal_id}", token=token_adotante)
    print("status final do animal:", resp["status"])
    assert resp["status"] == "adotado"

    titulo("13. Adotante consegue ver a própria lista de solicitações")
    status, resp = chamar("GET", "/api/solicitacoes", token=token_adotante)
    print(status, "total:", len(resp["solicitacoes"]))
    assert len(resp["solicitacoes"]) == 1

    titulo("TUDO FUNCIONANDO — fluxo completo de adoção validado de ponta a ponta")


if __name__ == "__main__":
    main()
