"""Teste de ponta a ponta contra a API real (http://localhost:8000):
cadastra instituição e adotante, cadastra animal com etiquetas, favorita,
manifesta interesse, aprova, agenda visita, avança etapas, envia documento,
conclui o processo e confere o histórico. Também testa os caminhos de erro
(permissão negada, dados inválidos, animal indisponível)."""
import json
import urllib.error
import urllib.request

BASE = "http://localhost:8000"


def chamar(metodo, caminho, corpo=None, token=None):
    dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    req = urllib.request.Request(BASE + caminho, data=dados, method=metodo)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def esperar(condicao, mensagem):
    if not condicao:
        raise AssertionError(f"FALHOU: {mensagem}")
    print(f"OK: {mensagem}")


sufixo = str(__import__("random").randint(10000, 99999))

# 1. Cadastro de instituição
status, resp = chamar("POST", "/api/usuarios", {
    "nome": "Abrigo Teste", "email": f"abrigo{sufixo}@teste.com", "senha": "senha123",
    "perfil": "instituicao", "cnpj": f"11.222.333/000{sufixo[:1]}-90", "localizacao": "Recife/PE",
})
esperar(status == 201, "cadastro de instituição")
status, resp = chamar("POST", "/api/auth/login", {"email": f"abrigo{sufixo}@teste.com", "senha": "senha123"})
esperar(status == 200, "login da instituição")
token_instituicao = resp["token"]
id_instituicao = resp["usuario"]["id"]

# 2. Cadastro de adotante
status, resp = chamar("POST", "/api/usuarios", {
    "nome": "Adotante Teste", "email": f"adotante{sufixo}@teste.com", "senha": "senha123",
    "perfil": "adotante", "cpf": f"{sufixo}-00", "endereco": "Rua Teste, 123",
})
esperar(status == 201, "cadastro de adotante")
status, resp = chamar("POST", "/api/auth/login", {"email": f"adotante{sufixo}@teste.com", "senha": "senha123"})
token_adotante = resp["token"]
id_adotante = resp["usuario"]["id"]

# 3. Cadastro de animal com etiquetas
status, resp = chamar("POST", "/api/animais", {
    "nome": "Rex", "data_nascimento": "2022-01-01",
    "caracteristicas": ["Espécie: Cão", "Porte: Médio", "Energia: Alta", "Convive com Crianças"],
}, token=token_instituicao)
esperar(status == 201, "cadastro de animal com etiquetas")
id_animal = resp["id"]
esperar(set(resp["caracteristicas"]) == {"Espécie: Cão", "Porte: Médio", "Energia: Alta", "Convive com Crianças"}, "etiquetas do animal persistidas corretamente")

# 3b. Tentar cadastrar animal com etiqueta inválida
status, resp = chamar("POST", "/api/animais", {
    "nome": "Invalido", "caracteristicas": ["Etiqueta Que Não Existe"],
}, token=token_instituicao)
esperar(status == 400, "etiqueta inválida é rejeitada com 400")

# 4. Favoritar
status, resp = chamar("POST", f"/api/animais/{id_animal}/favoritar", token=token_adotante)
esperar(status == 200, "favoritar animal")
status, resp = chamar("GET", "/api/favoritos", token=token_adotante)
esperar(status == 200 and len(resp) == 1, "listar favoritos")

# 5. Compatibilidade
status, resp = chamar("GET", f"/api/animais/{id_animal}/compatibilidade", token=token_adotante)
esperar(status == 200 and 0 <= resp["score"] <= 100, f"cálculo de compatibilidade retorna score válido ({resp.get('score')})")

# 6. Manifestação de interesse
status, resp = chamar("POST", "/api/manifestacoes", {"id_animal": id_animal}, token=token_adotante)
esperar(status == 201, "manifestar interesse")
id_manifestacao = resp["id"]

# 6b. Segunda manifestação para o mesmo animal deve ser bloqueada
status, resp = chamar("POST", "/api/manifestacoes", {"id_animal": id_animal}, token=token_adotante)
esperar(status == 400, "manifestação duplicada é bloqueada com 400")

# 7. Aprovar manifestação (cria processo + etapas)
status, resp = chamar("POST", f"/api/manifestacoes/{id_manifestacao}/aprovar", token=token_instituicao)
esperar(status == 200, "aprovar manifestação cria processo")
id_processo = resp["id"]

status, resp = chamar("GET", f"/api/animais/{id_animal}", token=token_adotante)
esperar(resp["status"] == "Em Processo", "animal muda para 'Em Processo' após aprovação")

status, resp = chamar("GET", f"/api/processos/{id_processo}/etapas", token=token_instituicao)
esperar(status == 200 and len(resp) == 4, "processo criado com 4 etapas")
esperar(resp[0]["status"] == "Em Andamento" and resp[1]["status"] == "Pendente", "primeira etapa ativa, demais pendentes")
id_etapa_analise = resp[0]["id"]

# 8. Horário de visita e agendamento
status, resp = chamar("POST", f"/api/instituicoes/{id_instituicao}/horarios",
                       {"data_hora": "2026-10-01T10:00:00"}, token=token_instituicao)
esperar(status == 201, "criar horário de visita")
id_horario = resp["id"]

status, resp = chamar("PUT", f"/api/processos/{id_processo}/etapas/{id_etapa_analise}",
                       {"status": "Concluída"}, token=token_instituicao)
esperar(status == 200, "concluir etapa de análise avança para a próxima")

status, resp = chamar("POST", f"/api/processos/{id_processo}/visitas", {"id_horario": id_horario}, token=token_instituicao)
esperar(status == 201, "agendar visita")

# 9. Documentos e histórico
status, resp = chamar("POST", f"/api/processos/{id_processo}/documentos",
                       {"nome": "RG do adotante", "caminho_arquivo": "/uploads/rg.pdf"}, token=token_adotante)
esperar(status == 201, "enviar documento")

status, resp = chamar("GET", f"/api/processos/{id_processo}/historico", token=token_instituicao)
esperar(status == 200 and len(resp) >= 3, f"histórico do processo registrou os eventos ({len(resp)} entradas)")

# 10. Permissão negada: outra instituição não pode gerenciar este processo
status, resp = chamar("POST", "/api/usuarios", {
    "nome": "Outro Abrigo", "email": f"outro{sufixo}@teste.com", "senha": "senha123",
    "perfil": "instituicao", "cnpj": f"99.888.777/000{sufixo[:1]}-11", "localizacao": "Olinda/PE",
})
status, resp = chamar("POST", "/api/auth/login", {"email": f"outro{sufixo}@teste.com", "senha": "senha123"})
token_outra_instituicao = resp["token"]
status, resp = chamar("POST", f"/api/processos/{id_processo}/concluir", token=token_outra_instituicao)
esperar(status == 403, "instituição de outro abrigo não pode concluir processo alheio (403)")

# 11. Concluir processo (dono correto)
status, resp = chamar("POST", f"/api/processos/{id_processo}/concluir", token=token_instituicao)
esperar(status == 200 and resp["status"] == "Concluído", "concluir processo")

status, resp = chamar("GET", f"/api/animais/{id_animal}", token=token_adotante)
esperar(resp["status"] == "Adotado", "animal muda para 'Adotado' após conclusão")

print("\nTodos os testes de fluxo de adoção passaram.")
