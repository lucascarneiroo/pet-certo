// Cliente da API do backend PetCerto.
//
// Centraliza toda chamada HTTP ao backend (login, cadastro, animais),
// guarda o token de sessão e trata erros de forma padronizada. Nenhuma
// tela deve usar fetch() diretamente — sempre passar por aqui.

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("petcerto_token");
}

function setToken(token) {
  if (token) localStorage.setItem("petcerto_token", token);
  else localStorage.removeItem("petcerto_token");
}

function getUsuario() {
  const raw = localStorage.getItem("petcerto_usuario");
  return raw ? JSON.parse(raw) : null;
}

function setUsuario(usuario) {
  if (usuario) localStorage.setItem("petcerto_usuario", JSON.stringify(usuario));
  else localStorage.removeItem("petcerto_usuario");
}

async function chamarApi(caminho, { metodo = "GET", corpo, autenticado = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (autenticado) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const resposta = await fetch(`${API_BASE_URL}${caminho}`, {
    method: metodo,
    headers,
    body: corpo ? JSON.stringify(corpo) : undefined,
  });

  const dados = await resposta.json().catch(() => ({}));

  if (!resposta.ok) {
    throw new Error(dados.erro || `Erro ${resposta.status} ao chamar ${caminho}`);
  }
  return dados;
}

// ---------- autenticação ----------

export async function login(email, senha) {
  const dados = await chamarApi("/api/auth/login", {
    metodo: "POST",
    corpo: { email, senha },
    autenticado: false,
  });
  setToken(dados.token);
  setUsuario(dados.usuario);
  return dados.usuario;
}

export function logout() {
  setToken(null);
  setUsuario(null);
}

export function usuarioLogado() {
  return getUsuario();
}

export function estaLogado() {
  return Boolean(getToken());
}

// perfil do frontend -> perfil que o backend entende
const PERFIL_FRONT_PARA_BACK = {
  adotante: "adotante",
  instituicao: "voluntario",
  administrador: "admin", // backend não deixa se autocadastrar como admin (ver cadastrarUsuario)
};

export async function cadastrarUsuario({ nome, email, senha, perfil, instituicao_nome, instituicao_cidade }) {
  return chamarApi("/api/usuarios", {
    metodo: "POST",
    corpo: {
      nome, email, senha,
      perfil: PERFIL_FRONT_PARA_BACK[perfil] || "adotante",
      instituicao_nome, instituicao_cidade,
    },
    autenticado: false,
  });
}

// ---------- animais ----------

// converte o formato do backend pro formato que as telas already esperam
function animalDoBackendParaFrontend(a) {
  const STATUS = { disponivel: "Disponível", em_processo: "Em processo", adotado: "Adotado" };
  const ESPECIE = { cachorro: "Cão", gato: "Gato", outro: "Outro" };
  const PORTE = { pequeno: "Porte pequeno", medio: "Porte médio", grande: "Porte grande" };

  return {
    id: a.id,
    name: a.nome,
    species: ESPECIE[a.especie] || a.especie,
    speciesTag: (ESPECIE[a.especie] || a.especie).toUpperCase(),
    breed: a.raca || "SRD",
    age: `${a.idade_anos} ${a.idade_anos === 1 ? "ano" : "anos"}`,
    size: PORTE[a.porte] || a.porte,
    status: STATUS[a.status] || a.status,
    temperament: a.temperamento || "",
    // campos que o backend ainda não tem — placeholder até existir Instituição/matching real
    institution: "—",
    city: "—",
    compat: null,
    _original: a, // guarda o objeto cru do backend, caso a tela precise
  };
}

export async function listarAnimais() {
  const dados = await chamarApi("/api/animais");
  return dados.animais.map(animalDoBackendParaFrontend);
}

export async function buscarAnimal(id) {
  const a = await chamarApi(`/api/animais/${id}`);
  return animalDoBackendParaFrontend(a);
}

export async function criarAnimal(animal) {
  const a = await chamarApi("/api/animais", { metodo: "POST", corpo: animal });
  return animalDoBackendParaFrontend(a);
}

export async function atualizarAnimal(id, campos) {
  const a = await chamarApi(`/api/animais/${id}`, { metodo: "PUT", corpo: campos });
  return animalDoBackendParaFrontend(a);
}

export async function excluirAnimal(id) {
  return chamarApi(`/api/animais/${id}`, { metodo: "DELETE" });
}
