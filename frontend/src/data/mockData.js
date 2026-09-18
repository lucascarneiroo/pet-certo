export const animals = [
  {
    id: "luna",
    name: "Luna",
    species: "Cão",
    speciesTag: "CÃO",
    breed: "SRD",
    age: "2 anos",
    size: "Porte médio",
    status: "Disponível",
    institution: "Instituto Amor Animal",
    city: "Recife",
    compat: 94,
    temperament: "Carinhosa, tranquila e sociável. Gosta de passeios moderados e convive bem com adultos.",
    behavior: "Dócil, energia moderada, adaptação gradual a crianças.",
  },
  {
    id: "nino",
    name: "Nino",
    species: "Gato",
    speciesTag: "GATO",
    breed: "SRD",
    age: "2 anos",
    size: "Porte médio",
    status: "Em processo",
    institution: "Instituto Amor Animal",
    city: "Recife",
    compat: 89,
    temperament: "Independente, curioso e afetuoso quando ganha confiança.",
    behavior: "Sociável, energia moderada, prefere ambientes calmos.",
  },
  {
    id: "bento",
    name: "Bento",
    species: "Cão",
    speciesTag: "CÃO",
    breed: "SRD",
    age: "2 anos",
    size: "Porte médio",
    status: "Adotado",
    institution: "Instituto Amor Animal",
    city: "Recife",
    compat: 86,
    temperament: "Brincalhão e leal, adora companhia constante.",
    behavior: "Sociável, energia alta, já convive bem com crianças.",
  },
  {
    id: "mel",
    name: "Mel",
    species: "Cão",
    speciesTag: "CÃO",
    breed: "SRD",
    age: "1 ano",
    size: "Pequeno",
    status: "Disponível",
    institution: "Projeto Patinhas",
    city: "Campinas",
    compat: 78,
    temperament: "Dócil e curiosa, ainda se adaptando a novas rotinas.",
    behavior: "Dócil, energia moderada, adaptação gradual a crianças.",
  },
];

export const institutions = [
  { id: "amor-animal", name: "Instituto Amor Animal", city: "Recife", status: "Verificada" },
  { id: "patinhas", name: "Projeto Patinhas", city: "Campinas", status: "Pendente" },
  { id: "lar-feliz", name: "Lar Feliz", city: "Santos", status: "Revisão" },
];

export const users = [
  { id: "marina", name: "Marina Oliveira", role: "Adotante", email: "marina@email.com", status: "Ativo" },
  { id: "ana", name: "Ana Souza", role: "Gestora ONG", email: "Amor Animal", status: "Ativo" },
];

export const requests = [
  {
    id: "PC-1048",
    adopter: "Marina Oliveira",
    animalId: "luna",
    animal: "Luna",
    compat: 94,
    stage: "Documentos",
    status: "Em processo",
    tag: "Alta compatibilidade",
    factors: { moradia: 92, rotina: 96, experiencia: 95 },
    profile: "Apartamento próprio · 2 adultos · experiência com cães · rotina moderada",
    attention: "Luna precisa de adaptação gradual ao ficar sozinha.",
    steps: [
      { label: "Interesse", date: "08 set", done: true },
      { label: "Análise", date: "09 set", done: true },
      { label: "Visita", date: "15 set", done: true },
      { label: "Documentos", date: "em andamento", current: true },
      { label: "Aprovação", date: "", done: false },
      { label: "Conclusão", date: "", done: false },
    ],
  },
  {
    id: "PC-1047",
    adopter: "Paulo Mendes",
    animalId: "nino",
    animal: "Nino",
    compat: 81,
    stage: "Análise",
    status: "Em processo",
    tag: "Em análise",
    factors: { moradia: 80, rotina: 84, experiencia: 78 },
    profile: "Apartamento alugado · 1 adulto · sem experiência prévia · rotina agitada",
    attention: "Nino prefere ambientes silenciosos durante o dia.",
    steps: [
      { label: "Interesse", date: "10 set", done: true },
      { label: "Análise", date: "em andamento", current: true },
      { label: "Visita", date: "", done: false },
      { label: "Documentos", date: "", done: false },
      { label: "Aprovação", date: "", done: false },
      { label: "Conclusão", date: "", done: false },
    ],
  },
  {
    id: "PC-0981",
    adopter: "Juliana Costa",
    animalId: "mel",
    animal: "Mel",
    compat: 78,
    stage: "Concluído",
    status: "Concluído",
    tag: "Em análise",
    factors: { moradia: 75, rotina: 80, experiencia: 79 },
    profile: "Casa com quintal · 3 adultos · experiência com cães · rotina estável",
    attention: "Nenhum ponto de atenção registrado.",
    steps: [
      { label: "Interesse", date: "20 ago", done: true },
      { label: "Análise", date: "22 ago", done: true },
      { label: "Visita", date: "28 ago", done: true },
      { label: "Documentos", date: "02 set", done: true },
      { label: "Aprovação", date: "05 set", done: true },
      { label: "Conclusão", date: "10 set", done: true },
    ],
  },
];

export const visits = [
  { id: 1, date: "15 set", time: "14:30", people: "Marina + Luna", note: "Confirmada", status: "Agendada" },
  { id: 2, date: "15 set", time: "16:00", people: "Paulo + Nino", note: "Confirmada", status: "Agendada" },
  { id: 3, date: "17 set", time: "10:00", people: "Juliana + Mel", note: "Reagendada", status: "Reagendada" },
];

export const documents = [
  { id: 1, name: "RG ou CNH", detail: "aprovado", status: "Aprovado" },
  { id: 2, name: "Comprovante de renda", detail: "aprovado", status: "Aprovado" },
  { id: 3, name: "Comprovante de residência", detail: "v2 · nova versão", status: "Revisar" },
];

export const history = [
  { id: 1, date: "14 set, 10:20", label: "Documento rejeitado", by: "Ana Souza" },
  { id: 2, date: "12 set, 16:40", label: "Visita confirmada", by: "Carlos Lima" },
  { id: 3, date: "09 set, 11:05", label: "Solicitação aceita", by: "Ana Souza" },
  { id: 4, date: "08 set, 09:12", label: "Interesse enviado", by: "Marina Oliveira" },
];

export const compatibilityProfile = [
  { label: "Rotina", value: "ativa" },
  { label: "Moradia", value: "apartamento" },
  { label: "Experiência", value: "já teve cães" },
  { label: "Residência", value: "2 adultos" },
  { label: "Preferências", value: "porte médio" },
];
