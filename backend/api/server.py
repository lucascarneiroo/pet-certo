"""Servidor HTTP do backend do Pet Certo, usando só a biblioteca padrão do
Python (http.server) — sem Flask/Django, por exigência do curso para o
núcleo computacional. CORS liberado manualmente para o frontend em React
poder chamar a API de outra origem durante o desenvolvimento local."""
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from auth.auth_service import (
    CredenciaisInvalidasError,
    DadosInvalidosError,
    EmailJaCadastradoError,
    autenticar,
    buscar_usuario_por_email,
    buscar_usuario_por_id,
    criar_usuario,
    listar_instituicoes,
)
from auth.session_service import criar_sessao, encerrar_sessao, usuario_id_da_sessao
from database.adocao_repository import (
    FluxoDeAdocaoInvalidoError,
    agendar_visita,
    aprovar_manifestacao,
    atualizar_visita,
    cancelar_processo,
    concluir_processo,
    criar_horario_visita,
    criar_manifestacao,
    enviar_documento,
    listar_documentos,
    listar_etapas,
    listar_historico,
    listar_horarios_disponiveis,
    listar_manifestacoes,
    listar_processos,
    listar_visitas_do_processo,
    recusar_manifestacao,
    avancar_etapa,
)
from database.animal_repository import (
    DadosDoAnimalInvalidosError,
    atualizar_animal,
    buscar_animal_por_id,
    criar_animal,
    excluir_animal,
    listar_animais,
)
from database.interacoes_repository import (
    desfavoritar,
    favoritar,
    listar_favoritos,
    listar_recomendacoes,
    registrar_acao_admin,
    registrar_recomendacao,
    salvar_compatibilidade,
)
from database.tags_padrao import TODAS_AS_TAGS
from matching.compatibilidade import calcular_matriz_scores, vetor_de_preferencia, vetor_do_animal

ROTA_ANIMAL_COM_ID = re.compile(r"^/api/animais/(\d+)$")
ROTA_ANIMAL_FAVORITAR = re.compile(r"^/api/animais/(\d+)/favoritar$")
ROTA_ANIMAL_COMPATIBILIDADE = re.compile(r"^/api/animais/(\d+)/compatibilidade$")
ROTA_MANIFESTACAO_COM_ID = re.compile(r"^/api/manifestacoes/(\d+)$")
ROTA_MANIFESTACAO_APROVAR = re.compile(r"^/api/manifestacoes/(\d+)/aprovar$")
ROTA_MANIFESTACAO_RECUSAR = re.compile(r"^/api/manifestacoes/(\d+)/recusar$")
ROTA_PROCESSO_COM_ID = re.compile(r"^/api/processos/(\d+)$")
ROTA_PROCESSO_ETAPAS = re.compile(r"^/api/processos/(\d+)/etapas$")
ROTA_PROCESSO_ETAPA_COM_ID = re.compile(r"^/api/processos/(\d+)/etapas/(\d+)$")
ROTA_PROCESSO_VISITAS = re.compile(r"^/api/processos/(\d+)/visitas$")
ROTA_PROCESSO_DOCUMENTOS = re.compile(r"^/api/processos/(\d+)/documentos$")
ROTA_PROCESSO_HISTORICO = re.compile(r"^/api/processos/(\d+)/historico$")
ROTA_PROCESSO_CONCLUIR = re.compile(r"^/api/processos/(\d+)/concluir$")
ROTA_PROCESSO_CANCELAR = re.compile(r"^/api/processos/(\d+)/cancelar$")
ROTA_VISITA_COM_ID = re.compile(r"^/api/visitas/(\d+)$")
ROTA_HORARIOS_DA_INSTITUICAO = re.compile(r"^/api/instituicoes/(\d+)/horarios$")


class ErroHTTP(Exception):
    def __init__(self, status: int, mensagem: str):
        super().__init__(mensagem)
        self.status = status
        self.mensagem = mensagem


def _animal_para_json(animal) -> dict:
    return {
        "id": animal.id,
        "id_instituicao": animal.id_instituicao,
        "nome_instituicao": animal.nome_instituicao,
        "nome": animal.nome,
        "data_nascimento": animal.data_nascimento,
        "status": animal.status,
        "caracteristicas": animal.caracteristicas,
    }


def _usuario_para_json(usuario) -> dict:
    dado = {"id": usuario.id, "nome": usuario.nome, "email": usuario.email, "perfil": usuario.perfil}
    if usuario.perfil == "adotante":
        dado.update({"cpf": usuario.cpf, "endereco": usuario.endereco, "score_perfil": usuario.score_perfil})
    elif usuario.perfil == "instituicao":
        dado.update({"cnpj": usuario.cnpj, "localizacao": usuario.localizacao, "info_abrigo": usuario.info_abrigo})
    return dado


class PetCertoHandler(BaseHTTPRequestHandler):
    server_version = "PetCertoAPI/2.0"

    # ------------------------------------------------------------ utilitários

    def _enviar_json(self, status: int, corpo: dict) -> None:
        dados = json.dumps(corpo, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(dados)

    def _ler_corpo_json(self) -> dict:
        tamanho = int(self.headers.get("Content-Length", 0))
        if tamanho == 0:
            return {}
        bruto = self.rfile.read(tamanho)
        try:
            return json.loads(bruto.decode("utf-8"))
        except json.JSONDecodeError:
            raise ErroHTTP(400, "Corpo da requisição não é um JSON válido.")

    def _usuario_autenticado(self):
        cabecalho = self.headers.get("Authorization", "")
        if not cabecalho.startswith("Bearer "):
            raise ErroHTTP(401, "Token de autenticação ausente.")
        token = cabecalho[len("Bearer "):]
        usuario_id = usuario_id_da_sessao(token)
        if usuario_id is None:
            raise ErroHTTP(401, "Sessão inválida ou expirada. Faça login novamente.")
        usuario = buscar_usuario_por_id(usuario_id)
        if usuario is None:
            raise ErroHTTP(401, "Usuário não encontrado.")
        return usuario

    def _exigir_admin(self, usuario) -> None:
        if not usuario.eh_admin:
            raise ErroHTTP(403, "Apenas administradores podem realizar esta ação.")

    def _exigir_instituicao_ou_admin(self, usuario) -> None:
        if not (usuario.eh_admin or usuario.eh_instituicao):
            raise ErroHTTP(403, "Apenas administradores e instituições podem realizar esta ação.")

    def _exigir_dono_do_animal_ou_admin(self, usuario, animal) -> None:
        if usuario.eh_admin:
            return
        if usuario.eh_instituicao and animal.id_instituicao == usuario.id:
            return
        raise ErroHTTP(403, "Este animal pertence a outra instituição.")

    def _exigir_dono_do_processo_ou_admin(self, usuario, processo_id: int) -> None:
        if usuario.eh_admin:
            return
        if usuario.eh_instituicao:
            pertence = any(p["id"] == processo_id for p in listar_processos(id_instituicao=usuario.id))
            if pertence:
                return
        raise ErroHTTP(403, "Este processo de adoção pertence a outra instituição.")

    # --------------------------------------------------------------- roteamento

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        self._despachar("GET")

    def do_POST(self):
        self._despachar("POST")

    def do_PUT(self):
        self._despachar("PUT")

    def do_DELETE(self):
        self._despachar("DELETE")

    def _despachar(self, metodo: str) -> None:
        caminho_completo = urlparse(self.path)
        caminho = caminho_completo.path
        query = parse_qs(caminho_completo.query)
        try:
            resultado = self._rotear(metodo, caminho, query)
            status, corpo = resultado if isinstance(resultado, tuple) else (200, resultado)
            self._enviar_json(status, corpo)
        except ErroHTTP as erro:
            self._enviar_json(erro.status, {"erro": erro.mensagem})
        except (DadosInvalidosError, DadosDoAnimalInvalidosError, FluxoDeAdocaoInvalidoError) as erro:
            self._enviar_json(400, {"erro": str(erro)})
        except EmailJaCadastradoError as erro:
            self._enviar_json(409, {"erro": str(erro)})
        except CredenciaisInvalidasError as erro:
            self._enviar_json(401, {"erro": str(erro)})
        except Exception as erro:  # nunca deixar o servidor cair por um erro inesperado
            self._enviar_json(500, {"erro": f"Erro interno: {erro}"})

    def log_message(self, format, *args):
        print(f"[api] {self.address_string()} - {format % args}")

    # ------------------------------------------------------------------ rotas

    def _rotear(self, metodo: str, caminho: str, query: dict):
        if caminho == "/api/health":
            return {"status": "ok", "servico": "Pet Certo API"}

        if caminho == "/api/auth/login" and metodo == "POST":
            return self._login()
        if caminho == "/api/auth/me" and metodo == "GET":
            return _usuario_para_json(self._usuario_autenticado())
        if caminho == "/api/auth/logout" and metodo == "POST":
            return self._logout()

        if caminho == "/api/usuarios" and metodo == "POST":
            return self._cadastrar_usuario()

        if caminho == "/api/instituicoes" and metodo == "GET":
            return listar_instituicoes()

        if caminho == "/api/tags" and metodo == "GET":
            return {"tags": TODAS_AS_TAGS}

        if caminho == "/api/animais" and metodo == "GET":
            return self._listar_animais(query)
        if caminho == "/api/animais" and metodo == "POST":
            return self._criar_animal()

        m = ROTA_ANIMAL_COM_ID.match(caminho)
        if m:
            animal_id = int(m.group(1))
            if metodo == "GET":
                return self._buscar_animal(animal_id)
            if metodo == "PUT":
                return self._atualizar_animal(animal_id)
            if metodo == "DELETE":
                return self._excluir_animal(animal_id)

        m = ROTA_ANIMAL_FAVORITAR.match(caminho)
        if m:
            animal_id = int(m.group(1))
            if metodo == "POST":
                return self._favoritar(animal_id)
            if metodo == "DELETE":
                return self._desfavoritar(animal_id)

        m = ROTA_ANIMAL_COMPATIBILIDADE.match(caminho)
        if m and metodo == "GET":
            return self._compatibilidade(int(m.group(1)))

        if caminho == "/api/favoritos" and metodo == "GET":
            return self._listar_favoritos()
        if caminho == "/api/recomendacoes" and metodo == "GET":
            return self._listar_recomendacoes()

        if caminho == "/api/manifestacoes" and metodo == "GET":
            return self._listar_manifestacoes(query)
        if caminho == "/api/manifestacoes" and metodo == "POST":
            return self._criar_manifestacao()

        m = ROTA_MANIFESTACAO_APROVAR.match(caminho)
        if m and metodo == "POST":
            return self._aprovar_manifestacao(int(m.group(1)))
        m = ROTA_MANIFESTACAO_RECUSAR.match(caminho)
        if m and metodo == "POST":
            return self._recusar_manifestacao(int(m.group(1)))

        if caminho == "/api/processos" and metodo == "GET":
            return self._listar_processos(query)

        m = ROTA_PROCESSO_ETAPAS.match(caminho)
        if m and metodo == "GET":
            return self._listar_etapas(int(m.group(1)))
        m = ROTA_PROCESSO_ETAPA_COM_ID.match(caminho)
        if m and metodo == "PUT":
            return self._atualizar_etapa(int(m.group(1)), int(m.group(2)))

        m = ROTA_PROCESSO_VISITAS.match(caminho)
        if m:
            processo_id = int(m.group(1))
            if metodo == "GET":
                return self._listar_visitas(processo_id)
            if metodo == "POST":
                return self._agendar_visita(processo_id)

        m = ROTA_PROCESSO_DOCUMENTOS.match(caminho)
        if m:
            processo_id = int(m.group(1))
            if metodo == "GET":
                return self._listar_documentos(processo_id)
            if metodo == "POST":
                return self._enviar_documento(processo_id)

        m = ROTA_PROCESSO_HISTORICO.match(caminho)
        if m and metodo == "GET":
            return self._listar_historico(int(m.group(1)))

        m = ROTA_PROCESSO_CONCLUIR.match(caminho)
        if m and metodo == "POST":
            return self._concluir_processo(int(m.group(1)))
        m = ROTA_PROCESSO_CANCELAR.match(caminho)
        if m and metodo == "POST":
            return self._cancelar_processo(int(m.group(1)))

        m = ROTA_VISITA_COM_ID.match(caminho)
        if m and metodo == "PUT":
            return self._atualizar_visita(int(m.group(1)))

        m = ROTA_HORARIOS_DA_INSTITUICAO.match(caminho)
        if m:
            instituicao_id = int(m.group(1))
            if metodo == "GET":
                return self._listar_horarios(instituicao_id)
            if metodo == "POST":
                return self._criar_horario(instituicao_id)

        raise ErroHTTP(404, "Rota não encontrada.")

    # ---------------------------------------------------------------- auth

    def _login(self):
        corpo = self._ler_corpo_json()
        usuario = autenticar(corpo.get("email", ""), corpo.get("senha", ""))
        token = criar_sessao(usuario.id)
        return {"token": token, "usuario": _usuario_para_json(usuario)}

    def _logout(self):
        cabecalho = self.headers.get("Authorization", "")
        if cabecalho.startswith("Bearer "):
            encerrar_sessao(cabecalho[len("Bearer "):])
        return {"ok": True}

    def _cadastrar_usuario(self):
        corpo = self._ler_corpo_json()
        usuario = criar_usuario(
            nome=corpo.get("nome", ""),
            email=corpo.get("email", ""),
            senha=corpo.get("senha", ""),
            perfil=corpo.get("perfil", ""),
            cpf=corpo.get("cpf"),
            endereco=corpo.get("endereco"),
            cnpj=corpo.get("cnpj"),
            localizacao=corpo.get("localizacao"),
            info_abrigo=corpo.get("info_abrigo"),
        )
        return 201, _usuario_para_json(usuario)

    # -------------------------------------------------------------- animais

    def _listar_animais(self, query: dict):
        status = query.get("status", [None])[0]
        id_instituicao = query.get("id_instituicao", [None])[0]
        animais = listar_animais(status=status, id_instituicao=int(id_instituicao) if id_instituicao else None)
        return [_animal_para_json(a) for a in animais]

    def _buscar_animal(self, animal_id: int):
        animal = buscar_animal_por_id(animal_id)
        if animal is None:
            raise ErroHTTP(404, "Animal não encontrado.")
        return _animal_para_json(animal)

    def _criar_animal(self):
        usuario = self._usuario_autenticado()
        self._exigir_instituicao_ou_admin(usuario)
        corpo = self._ler_corpo_json()
        id_instituicao = usuario.id if usuario.eh_instituicao else corpo.get("id_instituicao")
        if not id_instituicao:
            raise ErroHTTP(400, "id_instituicao é obrigatório quando um administrador cadastra o animal.")
        animal = criar_animal(
            id_instituicao=id_instituicao,
            nome=corpo.get("nome", ""),
            data_nascimento=corpo.get("data_nascimento"),
            caracteristicas=corpo.get("caracteristicas", []),
        )
        return 201, _animal_para_json(animal)

    def _atualizar_animal(self, animal_id: int):
        usuario = self._usuario_autenticado()
        animal = buscar_animal_por_id(animal_id)
        if animal is None:
            raise ErroHTTP(404, "Animal não encontrado.")
        self._exigir_dono_do_animal_ou_admin(usuario, animal)
        corpo = self._ler_corpo_json()
        atualizado = atualizar_animal(
            animal_id,
            nome=corpo.get("nome"),
            data_nascimento=corpo.get("data_nascimento"),
            status=corpo.get("status"),
            caracteristicas=corpo.get("caracteristicas"),
        )
        return _animal_para_json(atualizado)

    def _excluir_animal(self, animal_id: int):
        usuario = self._usuario_autenticado()
        self._exigir_admin(usuario)
        excluir_animal(animal_id)
        return {"ok": True}

    # ---------------------------------------------------- favoritos / recomendação

    def _favoritar(self, animal_id: int):
        usuario = self._usuario_autenticado()
        if not usuario.eh_adotante:
            raise ErroHTTP(403, "Apenas adotantes podem favoritar animais.")
        favoritar(usuario.id, animal_id)
        return {"ok": True}

    def _desfavoritar(self, animal_id: int):
        usuario = self._usuario_autenticado()
        desfavoritar(usuario.id, animal_id)
        return {"ok": True}

    def _listar_favoritos(self):
        usuario = self._usuario_autenticado()
        return listar_favoritos(usuario.id)

    def _listar_recomendacoes(self):
        usuario = self._usuario_autenticado()
        if not usuario.eh_adotante:
            raise ErroHTTP(403, "Apenas adotantes têm recomendações.")
        historico = [f["nome_animal"] for f in []]  # placeholder não usado
        animais_disponiveis = [a for a in listar_animais(status="Disponível")]
        favoritados = {f["id_animal"] for f in listar_favoritos(usuario.id)}
        historico_tags = [a.caracteristicas for a in animais_disponiveis if a.id in favoritados]
        preferencia = vetor_de_preferencia(historico_tags)
        candidatos = [a for a in animais_disponiveis if a.id not in favoritados]
        if not candidatos:
            return []
        from matching.compatibilidade import matriz_dos_animais
        A = matriz_dos_animais([a.caracteristicas for a in candidatos])
        import numpy as np
        scores = calcular_matriz_scores(preferencia.reshape(1, -1), A)[0]
        ordenado = sorted(zip(candidatos, scores), key=lambda par: -par[1])[:10]
        resultado = []
        for animal, score in ordenado:
            registrar_recomendacao(usuario.id, animal.id)
            resultado.append({**_animal_para_json(animal), "score_compatibilidade": round(float(score), 1)})
        return resultado

    def _compatibilidade(self, animal_id: int):
        usuario = self._usuario_autenticado()
        if not usuario.eh_adotante:
            raise ErroHTTP(403, "Apenas adotantes têm score de compatibilidade.")
        animal = buscar_animal_por_id(animal_id)
        if animal is None:
            raise ErroHTTP(404, "Animal não encontrado.")
        favoritados = {f["id_animal"] for f in listar_favoritos(usuario.id)}
        todos = listar_animais()
        historico_tags = [a.caracteristicas for a in todos if a.id in favoritados]
        preferencia = vetor_de_preferencia(historico_tags)
        vetor_animal = vetor_do_animal(animal.caracteristicas)
        score = float(calcular_matriz_scores(preferencia.reshape(1, -1), vetor_animal.reshape(1, -1))[0, 0])
        fatores = {"caracteristicas_do_animal": animal.caracteristicas, "baseado_em_favoritos": len(historico_tags)}
        salvar_compatibilidade(usuario.id, animal_id, round(score), fatores)
        return {"animal_id": animal_id, "score": round(score, 1), "fatores": fatores}

    # -------------------------------------------------------- fluxo de adoção

    def _listar_manifestacoes(self, query: dict):
        usuario = self._usuario_autenticado()
        if usuario.eh_adotante:
            return listar_manifestacoes(id_adotante=usuario.id)
        if usuario.eh_instituicao:
            return listar_manifestacoes(id_instituicao=usuario.id)
        return listar_manifestacoes()

    def _criar_manifestacao(self):
        usuario = self._usuario_autenticado()
        if not usuario.eh_adotante:
            raise ErroHTTP(403, "Apenas adotantes podem manifestar interesse em um animal.")
        corpo = self._ler_corpo_json()
        manifestacao = criar_manifestacao(usuario.id, corpo.get("id_animal"))
        return 201, manifestacao.__dict__

    def _exigir_dono_da_manifestacao_ou_admin(self, usuario, manifestacao_id: int):
        if usuario.eh_admin:
            return
        pertence = [m for m in listar_manifestacoes(id_instituicao=usuario.id if usuario.eh_instituicao else None) if m["id"] == manifestacao_id]
        if not pertence:
            raise ErroHTTP(403, "Esta manifestação pertence a outra instituição.")

    def _aprovar_manifestacao(self, manifestacao_id: int):
        usuario = self._usuario_autenticado()
        self._exigir_instituicao_ou_admin(usuario)
        self._exigir_dono_da_manifestacao_ou_admin(usuario, manifestacao_id)
        processo = aprovar_manifestacao(manifestacao_id)
        return processo.__dict__

    def _recusar_manifestacao(self, manifestacao_id: int):
        usuario = self._usuario_autenticado()
        self._exigir_instituicao_ou_admin(usuario)
        self._exigir_dono_da_manifestacao_ou_admin(usuario, manifestacao_id)
        manifestacao = recusar_manifestacao(manifestacao_id)
        return manifestacao.__dict__

    def _listar_processos(self, query: dict):
        usuario = self._usuario_autenticado()
        if usuario.eh_adotante:
            return listar_processos(id_adotante=usuario.id)
        if usuario.eh_instituicao:
            return listar_processos(id_instituicao=usuario.id)
        return listar_processos()

    def _listar_etapas(self, processo_id: int):
        self._usuario_autenticado()
        return [e.__dict__ for e in listar_etapas(processo_id)]

    def _atualizar_etapa(self, processo_id: int, etapa_id: int):
        usuario = self._usuario_autenticado()
        self._exigir_instituicao_ou_admin(usuario)
        self._exigir_dono_do_processo_ou_admin(usuario, processo_id)
        corpo = self._ler_corpo_json()
        etapa = avancar_etapa(processo_id, etapa_id, corpo.get("status", ""), corpo.get("observacao"))
        return etapa.__dict__

    def _listar_visitas(self, processo_id: int):
        self._usuario_autenticado()
        return [v.__dict__ for v in listar_visitas_do_processo(processo_id)]

    def _agendar_visita(self, processo_id: int):
        usuario = self._usuario_autenticado()
        self._exigir_instituicao_ou_admin(usuario)
        self._exigir_dono_do_processo_ou_admin(usuario, processo_id)
        corpo = self._ler_corpo_json()
        visita = agendar_visita(processo_id, corpo.get("id_horario"))
        return 201, visita.__dict__

    def _atualizar_visita(self, visita_id: int):
        usuario = self._usuario_autenticado()
        self._exigir_instituicao_ou_admin(usuario)
        corpo = self._ler_corpo_json()
        visita = atualizar_visita(visita_id, corpo.get("status", ""), corpo.get("resultado"))
        return visita.__dict__

    def _listar_horarios(self, instituicao_id: int):
        self._usuario_autenticado()
        return [h.__dict__ for h in listar_horarios_disponiveis(instituicao_id)]

    def _criar_horario(self, instituicao_id: int):
        usuario = self._usuario_autenticado()
        if not (usuario.eh_admin or (usuario.eh_instituicao and usuario.id == instituicao_id)):
            raise ErroHTTP(403, "Você só pode criar horários para a própria instituição.")
        corpo = self._ler_corpo_json()
        horario = criar_horario_visita(instituicao_id, corpo.get("data_hora"))
        return 201, horario.__dict__

    def _listar_documentos(self, processo_id: int):
        self._usuario_autenticado()
        return [d.__dict__ for d in listar_documentos(processo_id)]

    def _enviar_documento(self, processo_id: int):
        self._usuario_autenticado()
        corpo = self._ler_corpo_json()
        documento = enviar_documento(processo_id, corpo.get("nome", ""), corpo.get("caminho_arquivo", ""))
        return 201, documento.__dict__

    def _listar_historico(self, processo_id: int):
        self._usuario_autenticado()
        return [h.__dict__ for h in listar_historico(processo_id)]

    def _concluir_processo(self, processo_id: int):
        usuario = self._usuario_autenticado()
        self._exigir_instituicao_ou_admin(usuario)
        self._exigir_dono_do_processo_ou_admin(usuario, processo_id)
        processo = concluir_processo(processo_id)
        if usuario.eh_admin:
            registrar_acao_admin(usuario.id, "Conclusão de Processo", f"Processo {processo_id} concluído.")
        return processo.__dict__

    def _cancelar_processo(self, processo_id: int):
        usuario = self._usuario_autenticado()
        self._exigir_instituicao_ou_admin(usuario)
        self._exigir_dono_do_processo_ou_admin(usuario, processo_id)
        corpo = self._ler_corpo_json()
        processo = cancelar_processo(processo_id, corpo.get("motivo"))
        return processo.__dict__


def iniciar_servidor(host: str = "0.0.0.0", port: int = 8000) -> None:
    servidor = ThreadingHTTPServer((host, port), PetCertoHandler)
    print(f"Pet Certo API rodando em http://{host}:{port}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
        servidor.shutdown()
