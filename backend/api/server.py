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
from database.instituicao_repository import (
    listar_instituicoes,
    buscar_instituicao_por_id,
    criar_instituicao,
    atualizar_instituicao,
    DadosDaInstituicaoInvalidosError,
)
from database.solicitacao_repository import (
    criar_solicitacao,
    buscar_solicitacao_por_id,
    listar_solicitacoes_do_adotante,
    listar_solicitacoes_da_instituicao,
    listar_todas_solicitacoes,
    avancar_etapa,
    atualizar_status as atualizar_status_solicitacao,
    SolicitacaoInvalidaError,
)
from database.visita_repository import (
    agendar_visita,
    listar_visitas_da_solicitacao,
    atualizar_visita,
    VisitaInvalidaError,
)
from auth.auth_service import (
    autenticar,
    criar_usuario,
    listar_usuarios,
    buscar_usuario_por_id,
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
    DadosInvalidosError,
)
from auth.session_service import criar_sessao, usuario_da_sessao


ROTA_ANIMAL_COM_ID = re.compile(r"^/api/animais/(\d+)$")
ROTA_INSTITUICAO_COM_ID = re.compile(r"^/api/instituicoes/(\d+)$")
ROTA_SOLICITACAO_COM_ID = re.compile(r"^/api/solicitacoes/(\d+)$")
ROTA_SOLICITACAO_VISITAS = re.compile(r"^/api/solicitacoes/(\d+)/visitas$")
ROTA_VISITA_COM_ID = re.compile(r"^/api/visitas/(\d+)$")


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

    def _exigir_dono_da_instituicao_ou_admin(self, usuario, instituicao_id):
        if usuario.eh_admin:
            return
        if not (usuario.eh_voluntario and usuario.instituicao_id == instituicao_id):
            raise ErroHTTP(403, "Você não tem permissão para gerenciar esta instituição.")

    def _exigir_pode_gerenciar_solicitacao(self, usuario, solicitacao):
        """Admin pode tudo. Voluntário só pode mexer em solicitações de
        animais cadastrados por alguém da mesma instituição que ele."""
        if usuario.eh_admin:
            return
        if not usuario.eh_voluntario:
            raise ErroHTTP(403, "Apenas administradores e instituições podem gerenciar solicitações.")
        animal = buscar_animal_por_id(solicitacao.animal_id)
        dono_do_animal = buscar_usuario_por_id(animal.cadastrado_por) if animal and animal.cadastrado_por else None
        mesma_instituicao = (
            dono_do_animal is not None
            and dono_do_animal.instituicao_id is not None
            and dono_do_animal.instituicao_id == usuario.instituicao_id
        )
        if not mesma_instituicao:
            raise ErroHTTP(403, "Esta solicitação pertence a outra instituição.")

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

        if caminho == "/api/instituicoes" and metodo == "GET":
            return self._listar_instituicoes()
        if caminho == "/api/instituicoes" and metodo == "POST":
            return self._criar_instituicao()

        m = ROTA_INSTITUICAO_COM_ID.match(caminho)
        if m and metodo == "GET":
            return self._buscar_instituicao(int(m.group(1)))
        if m and metodo == "PUT":
            return self._atualizar_instituicao(int(m.group(1)))

        if caminho == "/api/solicitacoes" and metodo == "GET":
            return self._listar_solicitacoes()
        if caminho == "/api/solicitacoes" and metodo == "POST":
            return self._criar_solicitacao()

        m = ROTA_SOLICITACAO_COM_ID.match(caminho)
        if m and metodo == "GET":
            return self._buscar_solicitacao(int(m.group(1)))
        if m and metodo == "PUT":
            return self._atualizar_solicitacao(int(m.group(1)))

        m = ROTA_SOLICITACAO_VISITAS.match(caminho)
        if m and metodo == "GET":
            return self._listar_visitas(int(m.group(1)))
        if m and metodo == "POST":
            return self._agendar_visita(int(m.group(1)))

        m = ROTA_VISITA_COM_ID.match(caminho)
        if m and metodo == "PUT":
            return self._atualizar_visita(int(m.group(1)))

        raise ErroHTTP(404, f"Rota não encontrada: {metodo} {caminho}")

    # ---------- handlers: saúde / autenticação ----------

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

    # ---------- handlers: usuários ----------

    def _cadastrar_usuario(self):
        dados = self._ler_corpo_json()
        try:
            usuario = criar_usuario(
                nome=dados.get("nome", ""),
                email=dados.get("email", ""),
                senha=dados.get("senha", ""),
                perfil=dados.get("perfil", "adotante"),
                instituicao_nome=dados.get("instituicao_nome"),
                instituicao_cidade=dados.get("instituicao_cidade"),
            )
        except (EmailJaCadastradoError, DadosInvalidosError, DadosDaInstituicaoInvalidosError) as e:
            raise ErroHTTP(400, str(e))
        return 201, _usuario_para_dict(usuario)

    def _listar_usuarios(self):
        usuario = self._usuario_autenticado()
        self._exigir_perfil(usuario, {"admin"})
        usuarios = listar_usuarios()
        return 200, {"usuarios": [_usuario_para_dict(u) for u in usuarios]}

    # ---------- handlers: animais ----------

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

    # ---------- handlers: instituições ----------

    def _listar_instituicoes(self):
        self._usuario_autenticado()
        instituicoes = listar_instituicoes()
        return 200, {"instituicoes": [_instituicao_para_dict(i) for i in instituicoes]}

    def _buscar_instituicao(self, instituicao_id):
        self._usuario_autenticado()
        instituicao = buscar_instituicao_por_id(instituicao_id)
        if instituicao is None:
            raise ErroHTTP(404, "Instituição não encontrada.")
        return 200, _instituicao_para_dict(instituicao)

    def _criar_instituicao(self):
        usuario = self._usuario_autenticado()
        self._exigir_perfil(usuario, {"admin"})
        dados = self._ler_corpo_json()
        try:
            instituicao = criar_instituicao(
                nome=dados.get("nome", ""),
                cidade=dados.get("cidade", ""),
                status=dados.get("status", "pendente"),
            )
        except DadosDaInstituicaoInvalidosError as e:
            raise ErroHTTP(400, str(e))
        return 201, _instituicao_para_dict(instituicao)

    def _atualizar_instituicao(self, instituicao_id):
        usuario = self._usuario_autenticado()
        self._exigir_dono_da_instituicao_ou_admin(usuario, instituicao_id)
        dados = self._ler_corpo_json()
        # só admin pode alterar o status de verificação da instituição
        if "status" in dados and not usuario.eh_admin:
            raise ErroHTTP(403, "Só um administrador pode alterar o status de verificação.")
        try:
            instituicao = atualizar_instituicao(instituicao_id, **dados)
        except DadosDaInstituicaoInvalidosError as e:
            raise ErroHTTP(400, str(e))
        return 200, _instituicao_para_dict(instituicao)

    # ---------- handlers: solicitações de adoção ----------

    def _criar_solicitacao(self):
        usuario = self._usuario_autenticado()
        self._exigir_perfil(usuario, {"adotante"})
        dados = self._ler_corpo_json()
        try:
            solicitacao = criar_solicitacao(
                animal_id=int(dados.get("animal_id", 0)),
                adotante_id=usuario.id,
                observacoes=dados.get("observacoes", ""),
            )
        except SolicitacaoInvalidaError as e:
            raise ErroHTTP(400, str(e))
        return 201, _solicitacao_para_dict(solicitacao)

    def _listar_solicitacoes(self):
        usuario = self._usuario_autenticado()
        if usuario.eh_admin:
            solicitacoes = listar_todas_solicitacoes()
        elif usuario.eh_voluntario:
            solicitacoes = listar_solicitacoes_da_instituicao(usuario.instituicao_id) if usuario.instituicao_id else []
        else:  # adotante
            solicitacoes = listar_solicitacoes_do_adotante(usuario.id)
        return 200, {"solicitacoes": [_solicitacao_para_dict(s) for s in solicitacoes]}

    def _buscar_solicitacao(self, solicitacao_id):
        usuario = self._usuario_autenticado()
        solicitacao = buscar_solicitacao_por_id(solicitacao_id)
        if solicitacao is None:
            raise ErroHTTP(404, "Solicitação não encontrada.")
        if usuario.eh_adotante and solicitacao.adotante_id != usuario.id:
            raise ErroHTTP(403, "Esta solicitação não é sua.")
        if not usuario.eh_adotante:
            self._exigir_pode_gerenciar_solicitacao(usuario, solicitacao)
        return 200, _solicitacao_para_dict(solicitacao)

    def _atualizar_solicitacao(self, solicitacao_id):
        """Avança a etapa e/ou muda o status (aprovar/recusar/cancelar).
        Só quem gerencia a instituição dona do animal (ou admin) pode —
        exceto cancelamento, que o próprio adotante também pode fazer."""
        usuario = self._usuario_autenticado()
        solicitacao = buscar_solicitacao_por_id(solicitacao_id)
        if solicitacao is None:
            raise ErroHTTP(404, "Solicitação não encontrada.")

        dados = self._ler_corpo_json()
        novo_status = dados.get("status")
        nova_etapa = dados.get("etapa")

        eh_cancelamento_pelo_proprio_adotante = (
            usuario.eh_adotante
            and solicitacao.adotante_id == usuario.id
            and novo_status == "cancelada"
            and nova_etapa is None
        )
        if not eh_cancelamento_pelo_proprio_adotante:
            self._exigir_pode_gerenciar_solicitacao(usuario, solicitacao)

        try:
            if nova_etapa:
                solicitacao = avancar_etapa(solicitacao_id, nova_etapa)
            if novo_status:
                solicitacao = atualizar_status_solicitacao(
                    solicitacao_id, novo_status, observacoes=dados.get("observacoes")
                )
        except SolicitacaoInvalidaError as e:
            raise ErroHTTP(400, str(e))

        return 200, _solicitacao_para_dict(solicitacao)

    # ---------- handlers: visitas ----------

    def _agendar_visita(self, solicitacao_id):
        usuario = self._usuario_autenticado()
        solicitacao = buscar_solicitacao_por_id(solicitacao_id)
        if solicitacao is None:
            raise ErroHTTP(404, "Solicitação não encontrada.")
        self._exigir_pode_gerenciar_solicitacao(usuario, solicitacao)

        dados = self._ler_corpo_json()
        try:
            visita = agendar_visita(
                solicitacao_id=solicitacao_id,
                data_agendada=dados.get("data_agendada", ""),
                observacoes=dados.get("observacoes", ""),
            )
            avancar_etapa(solicitacao_id, "visita")
        except (VisitaInvalidaError, SolicitacaoInvalidaError) as e:
            raise ErroHTTP(400, str(e))
        return 201, _visita_para_dict(visita)

    def _listar_visitas(self, solicitacao_id):
        usuario = self._usuario_autenticado()
        solicitacao = buscar_solicitacao_por_id(solicitacao_id)
        if solicitacao is None:
            raise ErroHTTP(404, "Solicitação não encontrada.")
        if usuario.eh_adotante and solicitacao.adotante_id != usuario.id:
            raise ErroHTTP(403, "Esta solicitação não é sua.")
        if not usuario.eh_adotante:
            self._exigir_pode_gerenciar_solicitacao(usuario, solicitacao)
        visitas = listar_visitas_da_solicitacao(solicitacao_id)
        return 200, {"visitas": [_visita_para_dict(v) for v in visitas]}

    def _atualizar_visita(self, visita_id):
        usuario = self._usuario_autenticado()
        self._exigir_perfil(usuario, {"admin", "voluntario"})
        dados = self._ler_corpo_json()
        try:
            visita = atualizar_visita(visita_id, **dados)
        except VisitaInvalidaError as e:
            raise ErroHTTP(400, str(e))
        return 200, _visita_para_dict(visita)


def _usuario_para_dict(usuario) -> dict:
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "perfil": usuario.perfil,
        "instituicao_id": usuario.instituicao_id,
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


def _instituicao_para_dict(instituicao) -> dict:
    return {
        "id": instituicao.id,
        "nome": instituicao.nome,
        "cidade": instituicao.cidade,
        "status": instituicao.status,
        "data_cadastro": instituicao.data_cadastro,
    }


def _solicitacao_para_dict(solicitacao) -> dict:
    return {
        "id": solicitacao.id,
        "animal_id": solicitacao.animal_id,
        "adotante_id": solicitacao.adotante_id,
        "etapa": solicitacao.etapa,
        "status": solicitacao.status,
        "observacoes": solicitacao.observacoes,
        "data_solicitacao": solicitacao.data_solicitacao,
        "data_atualizacao": solicitacao.data_atualizacao,
    }


def _visita_para_dict(visita) -> dict:
    return {
        "id": visita.id,
        "solicitacao_id": visita.solicitacao_id,
        "data_agendada": visita.data_agendada,
        "status": visita.status,
        "observacoes": visita.observacoes,
        "data_cadastro": visita.data_cadastro,
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
