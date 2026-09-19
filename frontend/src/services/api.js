// Cliente central de acesso à API do backend (Python, sem framework).
// Todas as telas devem chamar as funções daqui, nunca fazer fetch direto,
// para manter num único lugar a URL base, o token de autenticação e o
// mapeamento entre os nomes de perfil usados no front e no back.

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// O front usa "instituicao"/"administrador", que já é exatamente o que o
// back manda agora (o back mudou para bater com o front nesta migração).
const TOKEN_KEY = "petcerto_token";
const USUARIO_KEY = "petcerto_usuario";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getUsuario() {
  const bruto = localStorage.getItem(USUARIO_KEY);
  return bruto ? JSON.parse(bruto) : null;
}

function setSessao(token, usuario) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USUARIO_KEY, JSON.stringify(usuario));
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USUARIO_KEY);
}

async function chamarApi(caminho, { metodo = "GET", corpo, autenticado = true } = {}) {
  const cabecalhos = { "Content-Type": "application/json" };
  if (autenticado) {
    const token = getToken();
    if (token) cabecalhos["Authorization"] = `Bearer ${token}`;
  }
  const resposta = await fetch(`${API_BASE_URL}${caminho}`, {
    method: metodo,
    headers: cabecalhos,
    body: corpo !== undefined ? JSON.stringify(corpo) : undefined,
  });
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) {
    throw new Error(dados.erro || `Erro ${resposta.status} ao chamar ${caminho}`);
  }
  return dados;
}

// ------------------------------------------------------------------- Auth

export async function login(email, senha) {
  const dados = await chamarApi("/api/auth/login", {
    metodo: "POST",
    corpo: { email, senha },
    autenticado: false,
  });
  setSessao(dados.token, dados.usuario);
  return dados.usuario;
}

export async function cadastrarUsuario({ nome, email, senha, perfil, cpf, endereco, cnpj, localizacao, info_abrigo }) {
  return chamarApi("/api/usuarios", {
    metodo: "POST",
    corpo: { nome, email, senha, perfil, cpf, endereco, cnpj, localizacao, info_abrigo },
    autenticado: false,
  });
}

// ------------------------------------------------------------------ Tags

export async function listarTagsPadrao() {
  const dados = await chamarApi("/api/tags", { autenticado: false });
  return dados.tags;
}

// ---------------------------------------------------------------- Animais

function animalDoBackendParaFrontend(a) {
  return {
    id: a.id,
    name: a.nome,
    status: a.status, // 'Disponível' | 'Em Processo' | 'Adotado'
    institution: a.nome_instituicao,
    idInstituicao: a.id_instituicao,
    dataNascimento: a.data_nascimento,
    caracteristicas: a.caracteristicas,
    compat: a.score_compatibilidade,
  };
}

export async function listarAnimais(filtros = {}) {
  const query = new URLSearchParams(filtros).toString();
  const dados = await chamarApi(`/api/animais${query ? `?${query}` : ""}`, { autenticado: false });
  return dados.map(animalDoBackendParaFrontend);
}

export async function buscarAnimal(id) {
  const dados = await chamarApi(`/api/animais/${id}`, { autenticado: false });
  return animalDoBackendParaFrontend(dados);
}

export async function criarAnimal({ nome, data_nascimento, caracteristicas, id_instituicao }) {
  const dados = await chamarApi("/api/animais", {
    metodo: "POST",
    corpo: { nome, data_nascimento, caracteristicas, id_instituicao },
  });
  return animalDoBackendParaFrontend(dados);
}

export async function atualizarAnimal(id, campos) {
  const dados = await chamarApi(`/api/animais/${id}`, { metodo: "PUT", corpo: campos });
  return animalDoBackendParaFrontend(dados);
}

export async function excluirAnimal(id) {
  return chamarApi(`/api/animais/${id}`, { metodo: "DELETE" });
}

// -------------------------------------------------------- Favoritos / matching

export async function favoritarAnimal(idAnimal) {
  return chamarApi(`/api/animais/${idAnimal}/favoritar`, { metodo: "POST" });
}

export async function desfavoritarAnimal(idAnimal) {
  return chamarApi(`/api/animais/${idAnimal}/favoritar`, { metodo: "DELETE" });
}

export async function listarFavoritos() {
  return chamarApi("/api/favoritos");
}

export async function buscarCompatibilidade(idAnimal) {
  return chamarApi(`/api/animais/${idAnimal}/compatibilidade`);
}

export async function listarRecomendacoes() {
  const dados = await chamarApi("/api/recomendacoes");
  return dados.map(animalDoBackendParaFrontend);
}

// --------------------------------------------------------- Fluxo de adoção

export async function manifestarInteresse(idAnimal) {
  return chamarApi("/api/manifestacoes", { metodo: "POST", corpo: { id_animal: idAnimal } });
}

export async function listarManifestacoes() {
  return chamarApi("/api/manifestacoes");
}

export async function aprovarManifestacao(id) {
  return chamarApi(`/api/manifestacoes/${id}/aprovar`, { metodo: "POST" });
}

export async function recusarManifestacao(id) {
  return chamarApi(`/api/manifestacoes/${id}/recusar`, { metodo: "POST" });
}

export async function listarProcessos() {
  return chamarApi("/api/processos");
}

export async function listarEtapas(idProcesso) {
  return chamarApi(`/api/processos/${idProcesso}/etapas`);
}

export async function atualizarEtapa(idProcesso, idEtapa, status, observacao) {
  return chamarApi(`/api/processos/${idProcesso}/etapas/${idEtapa}`, {
    metodo: "PUT",
    corpo: { status, observacao },
  });
}

export async function listarHorariosDisponiveis(idInstituicao) {
  return chamarApi(`/api/instituicoes/${idInstituicao}/horarios`);
}

export async function criarHorarioVisita(idInstituicao, dataHora) {
  return chamarApi(`/api/instituicoes/${idInstituicao}/horarios`, {
    metodo: "POST",
    corpo: { data_hora: dataHora },
  });
}

export async function agendarVisita(idProcesso, idHorario) {
  return chamarApi(`/api/processos/${idProcesso}/visitas`, { metodo: "POST", corpo: { id_horario: idHorario } });
}

export async function enviarDocumento(idProcesso, nome, caminhoArquivo) {
  return chamarApi(`/api/processos/${idProcesso}/documentos`, {
    metodo: "POST",
    corpo: { nome, caminho_arquivo: caminhoArquivo },
  });
}

export async function listarHistoricoProcesso(idProcesso) {
  return chamarApi(`/api/processos/${idProcesso}/historico`);
}

export async function concluirProcesso(idProcesso) {
  return chamarApi(`/api/processos/${idProcesso}/concluir`, { metodo: "POST" });
}

export async function cancelarProcesso(idProcesso, motivo) {
  return chamarApi(`/api/processos/${idProcesso}/cancelar`, { metodo: "POST", corpo: { motivo } });
}

// ---------------------------------------------------------------- Instituições

export async function listarInstituicoes() {
  return chamarApi("/api/instituicoes", { autenticado: false });
}
