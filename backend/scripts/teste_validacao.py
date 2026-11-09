"""Testes de validação da API: dados inválidos, campos obrigatórios,
formatos inadequados e violações de regras de negócio — confere que o
sistema rejeita com o status HTTP e a mensagem corretos, em vez de
aceitar silenciosamente ou estourar erro 500."""
import json
import sys
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
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {}


falhas = []


def esperar(condicao, mensagem):
    if not condicao:
        falhas.append(mensagem)
        print(f"FALHOU: {mensagem}")
    else:
        print(f"OK: {mensagem}")


sufixo = str(__import__("random").randint(10000, 99999))

# ---------------------------------------------------------- Cadastro de usuário

status, resp = chamar("POST", "/api/usuarios", {"nome": "", "email": f"semcampo{sufixo}@t.com", "senha": "123456", "perfil": "adotante"})
esperar(status in (400, 422), f"cadastro sem CPF/endereço (campo obrigatório do perfil) é rejeitado (veio {status})")

status, resp = chamar("POST", "/api/usuarios", {"nome": "X", "email": "nao-e-email", "senha": "123456", "perfil": "adotante", "cpf": f"{sufixo}-01", "endereco": "Rua X"})
esperar(status in (400, 422), f"e-mail em formato inválido é rejeitado (veio {status}: {resp})")

status, resp = chamar("POST", "/api/usuarios", {"nome": "X", "email": f"curta{sufixo}@t.com", "senha": "123", "perfil": "adotante", "cpf": f"{sufixo}-02", "endereco": "Rua X"})
esperar(status in (400, 422), f"senha muito curta é rejeitada (veio {status}: {resp})")

status, resp = chamar("POST", "/api/usuarios", {"nome": "X", "email": f"perfilinvalido{sufixo}@t.com", "senha": "123456", "perfil": "superusuario", "cpf": f"{sufixo}-03", "endereco": "Rua X"})
esperar(status in (400, 422), f"perfil fora do vocabulário (adotante/instituicao/admin) é rejeitado (veio {status}: {resp})")

email_dup = f"dup{sufixo}@t.com"
chamar("POST", "/api/usuarios", {"nome": "Original", "email": email_dup, "senha": "123456", "perfil": "adotante", "cpf": f"{sufixo}-04", "endereco": "Rua X"})
status, resp = chamar("POST", "/api/usuarios", {"nome": "Duplicado", "email": email_dup, "senha": "123456", "perfil": "adotante", "cpf": f"{sufixo}-05", "endereco": "Rua Y"})
esperar(status in (400, 409, 422), f"e-mail duplicado é rejeitado (veio {status}: {resp})")

# ---------------------------------------------------------- Login

status, resp = chamar("POST", "/api/auth/login", {"email": email_dup, "senha": "senha-errada"})
esperar(status == 401, f"login com senha errada retorna 401 (veio {status})")
esperar("senha" not in json.dumps(resp).lower() or "inv" in json.dumps(resp).lower(), "mensagem de erro de login não vaza detalhe sobre qual campo errou")

status, resp = chamar("POST", "/api/auth/login", {"email": "ninguem@inexistente.com", "senha": "123456"})
esperar(status == 401, f"login com e-mail inexistente retorna 401, não 404 (não revela se o e-mail existe) (veio {status})")

# ---------------------------------------------------------- Animal

status, resp = chamar("POST", "/api/usuarios", {"nome": "Abrigo Validacao", "email": f"abrigoval{sufixo}@t.com", "senha": "123456", "perfil": "instituicao", "cnpj": f"10.000.{sufixo[:3]}/0001-00", "localizacao": "Recife/PE"})
esperar(status == 201, "setup: instituição criada para os testes de animal")
status, resp = chamar("POST", "/api/auth/login", {"email": f"abrigoval{sufixo}@t.com", "senha": "123456"})
token_inst = resp["token"]

status, resp = chamar("POST", "/api/animais", {"nome": "", "caracteristicas": []}, token=token_inst)
esperar(status in (400, 422), f"cadastro de animal sem nome é rejeitado (veio {status}: {resp})")

status, resp = chamar("POST", "/api/animais", {"nome": "   ", "caracteristicas": []}, token=token_inst)
esperar(status in (400, 422), f"nome só com espaços em branco é rejeitado (veio {status}: {resp})")

status, resp = chamar("POST", "/api/animais", {"nome": "Fido", "caracteristicas": ["Etiqueta Fake"]}, token=token_inst)
esperar(status in (400, 422), f"característica fora do vocabulário padrão é rejeitada (veio {status}: {resp})")

status, resp = chamar("POST", "/api/animais", {"nome": "Fido"}, token=None)
esperar(status == 401, f"cadastrar animal sem autenticação retorna 401 (veio {status})")

status, resp = chamar("POST", "/api/animais", {"nome": "Fido", "data_nascimento": "não-é-uma-data"}, token=token_inst)
esperar(status in (400, 422, 500) and status != 201, f"data de nascimento em formato inválido não é aceita como válida (veio {status})")
if status == 500:
    falhas.append("data_nascimento inválida gera erro 500 (deveria ser 400) — ver observação no relatório")

# ---------------------------------------------------------- Manifestação / processo

status, resp = chamar("POST", "/api/animais", {"nome": "Rex Val", "caracteristicas": ["Espécie: Cão"]}, token=token_inst)
id_animal = resp["id"]
status, resp = chamar("POST", "/api/usuarios", {"nome": "Adotante Val", "email": f"adoval{sufixo}@t.com", "senha": "123456", "perfil": "adotante", "cpf": f"{sufixo}-06", "endereco": "Rua Z"})
status, resp = chamar("POST", "/api/auth/login", {"email": f"adoval{sufixo}@t.com", "senha": "123456"})
token_ado = resp["token"]

status, resp = chamar("POST", "/api/manifestacoes", {"id_animal": 9999999}, token=token_ado)
esperar(status in (400, 404, 422), f"manifestar interesse em animal inexistente é rejeitado (veio {status}: {resp})")

status, resp = chamar("POST", "/api/manifestacoes", {"id_animal": id_animal}, token=token_inst)
esperar(status == 403, f"instituição não pode manifestar interesse (ação exclusiva de adotante) (veio {status})")

status, resp = chamar("GET", "/api/processos/9999999/etapas", token=token_ado)
esperar(status in (400, 404), f"listar etapas de processo inexistente retorna erro, não 200 vazio silencioso (veio {status})")

status, resp = chamar("POST", "/api/processos/9999999/concluir", token=token_inst)
esperar(status in (400, 404), f"concluir processo inexistente é rejeitado (veio {status})")

print(f"\n{'='*60}")
if falhas:
    print(f"{len(falhas)} verificação(ões) com problema:")
    for f in falhas:
        print(f" - {f}")
    sys.exit(1)
else:
    print("Todas as verificações de validação passaram.")
