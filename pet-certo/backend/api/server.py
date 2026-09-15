"""
Servidor HTTP do backend do PetCerto.

Implementado com a biblioteca padrão do Python (módulo http.server),
sem frameworks externos (Flask, FastAPI, Django etc.) — em linha com
a decisão da disciplina de priorizar Python "puro" no núcleo do
projeto.

Expõe uma API REST em JSON que pode ser consumida por qualquer
frontend que a equipe decidir usar (web, mobile, desktop), rodando em
outra tecnologia e até em outro processo/computador — é justamente
essa separação que caracteriza "backend" nesse projeto.

Ver docs/api.md (na raiz do repositório) para a lista completa de
rotas com exemplos de request/response.
"""

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from database.db import init_db, get_connection
from database.animal_repository import (
    listar_animais,
    buscar_animal_por_id,
    criar_animal,
    atualizar_animal,
    excluir_animal,
    DadosDoAnimalInvalidosError,
)
from auth.auth_service import (
    autenticar,
    criar_usuario,
    listar_usuarios,
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
    DadosInvalidosError,
)
from auth.session_service import criar_sessao, usuario_da_sessao


ROTA_ANIMAL_COM_ID = re.compile(r"^/api/animais/(\d+)$")


class ErroHTTP(Exception):
    """Erro de negócio/validação que deve virar uma resposta HTTP
    com status e mensagem específicos (em vez de um 500 genérico)."""

    def __init__(self, status: int, mensagem: str):
        super().__init__(mensagem)
        self.status = status
        self.mensagem = mensagem


class PetCertoHandler(BaseHTTPRequestHandler):

    # ---------- infraestrutura de request/response ----------

    def _enviar_json(self, status: int, payload: dict):
        corpo = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def _ler_corpo_json(self) -> dict:
        tamanho = int(self.headers.get("Content-Length", 0) or 0)
        if tamanho == 0:
            return {}
        bruto = self.rfile.read(tamanho)
        try:
            return json.loads(bruto.decode("utf-8")) if bruto else {}
        except json.JSONDecodeError:
            raise ErroHTTP(400, "Corpo da requisição não é um JSON válido.")

    def _usuario_autenticado(self):
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            raise ErroHTTP(
                401,
                "Token de autenticação ausente. Envie o cabeçalho "
                "'Authorization: Bearer <token>' obtido no login.",
            )
        token = header[len("Bearer "):].strip()
        usuario = usuario_da_sessao(token)
        if usuario is None:
            raise ErroHTTP(401, "Sessão inválida ou expirada. Faça login novamente.")
        return usuario

    def _exigir_perfil(self, usuario, perfis_permitidos):
        if usuario.perfil not in perfis_permitidos:
            raise ErroHTTP(
                403, f"Seu perfil ('{usuario.perfil}') não tem permissão para essa ação."
            )

    def log_message(self, format, *args):
        # log mais enxuto no console: método, caminho e status da resposta
        print(f"[api] {self.address_string()} - {format % args}")

    # ---------- CORS (necessário para o frontend, rodando em outra origem, poder chamar a API) ----------

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    # ---------- roteamento ----------

    def do_GET(self):
        self._rotear("GET")

    def do_POST(self):
        self._rotear("POST")

    def do_PUT(self):
        self._rotear("PUT")

    def do_DELETE(self):
        self._rotear("DELETE")

    def _rotear(self, metodo):
        caminho = urlparse(self.path).path
        try:
            status, corpo = self._despachar(metodo, caminho)
            self._enviar_json(status, corpo)
        except ErroHTTP as e:
            self._enviar_json(e.status, {"erro": e.mensagem})
        except Exception as e:  # nunca deixar a exceção crua vazar pro cliente
            self._enviar_json(500, {"erro": f"Erro interno no servidor: {e}"})

    def _despachar(self, metodo, caminho):
        if caminho == "/api/health" and metodo == "GET":
            return self._health()

        if caminho == "/api/auth/login" and metodo == "POST":
            return self._login()

        if caminho == "/api/auth/me" and metodo == "GET":
            return self._me()

        if caminho == "/api/usuarios" and metodo == "POST":
            return self._cadastrar_usuario()

        if caminho == "/api/usuarios" and metodo == "GET":
            return self._listar_usuarios()

        if caminho == "/api/animais" and metodo == "GET":
            return self._listar_animais()

        if caminho == "/api/animais" and metodo == "POST":
            return self._criar_animal()

        m = ROTA_ANIMAL_COM_ID.match(caminho)
        if m and metodo == "GET":
            return self._buscar_animal(int(m.group(1)))
        if m and metodo == "PUT":
            return self._atualizar_animal(int(m.group(1)))
        if m and metodo == "DELETE":
            return self._excluir_animal(int(m.group(1)))

        raise ErroHTTP(404, f"Rota não encontrada: {metodo} {caminho}")

    # ---------- handlers de cada rota ----------

    def _health(self):
        """Usado para comprovar 'banco de dados conectado' (item da sprint)."""
        try:
            conn = get_connection()
            conn.execute("SELECT 1")
            conn.close()
            return 200, {"status": "ok", "banco_de_dados": "conectado"}
        except Exception as e:
            return 500, {"status": "erro", "detalhe": str(e)}

    def _login(self):
        dados = self._ler_corpo_json()
        try:
            usuario = autenticar(dados.get("email", ""), dados.get("senha", ""))
        except CredenciaisInvalidasError as e:
            raise ErroHTTP(401, str(e))
        token = criar_sessao(usuario.id)
        return 200, {
            "token": token,
            "usuario": _usuario_para_dict(usuario),
        }

    def _me(self):
        usuario = self._usuario_autenticado()
        return 200, _usuario_para_dict(usuario)

    def _cadastrar_usuario(self):
        dados = self._ler_corpo_json()
        try:
            usuario = criar_usuario(
                nome=dados.get("nome", ""),
                email=dados.get("email", ""),
                senha=dados.get("senha", ""),
                perfil=dados.get("perfil", "adotante"),
            )
        except (EmailJaCadastradoError, DadosInvalidosError) as e:
            raise ErroHTTP(400, str(e))
        return 201, _usuario_para_dict(usuario)

    def _listar_usuarios(self):
        usuario = self._usuario_autenticado()
        self._exigir_perfil(usuario, {"admin"})
        usuarios = listar_usuarios()
        return 200, {"usuarios": [_usuario_para_dict(u) for u in usuarios]}

    def _listar_animais(self):
        self._usuario_autenticado()  # qualquer perfil logado pode consultar
        animais = listar_animais()
        return 200, {"animais": [_animal_para_dict(a) for a in animais]}

    def _buscar_animal(self, animal_id):
        self._usuario_autenticado()
        animal = buscar_animal_por_id(animal_id)
        if animal is None:
            raise ErroHTTP(404, "Animal não encontrado.")
        return 200, _animal_para_dict(animal)

    def _criar_animal(self):
        usuario = self._usuario_autenticado()
        self._exigir_perfil(usuario, {"admin", "voluntario"})
        dados = self._ler_corpo_json()
        try:
            animal = criar_animal(
                nome=dados.get("nome", ""),
                especie=dados.get("especie", ""),
                raca=dados.get("raca", ""),
                porte=dados.get("porte", ""),
                idade_anos=float(dados.get("idade_anos", 0) or 0),
                nivel_energia=dados.get("nivel_energia", ""),
                temperamento=dados.get("temperamento", ""),
                convive_criancas=bool(dados.get("convive_criancas", False)),
                convive_outros_pets=bool(dados.get("convive_outros_pets", False)),
                necessidades_especiais=dados.get("necessidades_especiais", ""),
                espaco_recomendado=dados.get("espaco_recomendado", ""),
                cadastrado_por=usuario.id,
            )
        except DadosDoAnimalInvalidosError as e:
            raise ErroHTTP(400, str(e))
        return 201, _animal_para_dict(animal)

    def _atualizar_animal(self, animal_id):
        usuario = self._usuario_autenticado()
        self._exigir_perfil(usuario, {"admin", "voluntario"})
        dados = self._ler_corpo_json()
        try:
            animal = atualizar_animal(animal_id, **dados)
        except DadosDoAnimalInvalidosError as e:
            raise ErroHTTP(400, str(e))
        return 200, _animal_para_dict(animal)

    def _excluir_animal(self, animal_id):
        usuario = self._usuario_autenticado()
        self._exigir_perfil(usuario, {"admin"})
        excluir_animal(animal_id)
        return 200, {"mensagem": "Animal excluído com sucesso."}


def _usuario_para_dict(usuario) -> dict:
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "perfil": usuario.perfil,
        "data_cadastro": usuario.data_cadastro,
    }


def _animal_para_dict(animal) -> dict:
    return {
        "id": animal.id,
        "nome": animal.nome,
        "especie": animal.especie,
        "raca": animal.raca,
        "porte": animal.porte,
        "idade_anos": animal.idade_anos,
        "nivel_energia": animal.nivel_energia,
        "temperamento": animal.temperamento,
        "convive_criancas": animal.convive_criancas,
        "convive_outros_pets": animal.convive_outros_pets,
        "necessidades_especiais": animal.necessidades_especiais,
        "espaco_recomendado": animal.espaco_recomendado,
        "status": animal.status,
        "data_cadastro": animal.data_cadastro,
        "cadastrado_por": animal.cadastrado_por,
    }


def iniciar_servidor(host: str = "0.0.0.0", port: int = 8000):
    init_db()
    servidor = ThreadingHTTPServer((host, port), PetCertoHandler)
    print(f"PetCerto backend rodando em http://localhost:{port}")
    print("Veja docs/api.md para a lista de rotas disponíveis.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
        servidor.shutdown()
