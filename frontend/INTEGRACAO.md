# Integração com o backend (pós-migração para PostgreSQL)

O backend trocou de banco (SQLite -> PostgreSQL, schema do Henrique) e o
formato de vários dados mudou. Este arquivo registra o que já está
conectado ao backend real e o que ainda depende de dados mocados, para
não perder o controle do que falta.

## Já conectado ao backend real

- Login (`/api/auth/login`)
- Cadastro de adotante e de instituição (`/api/usuarios`)
- Listagem de animais disponíveis, com as etiquetas (características) reais
  vindas do banco (`/api/animais`)

## Ainda usa dados mocados / precisa de trabalho

- Tela de detalhe do animal (`adopter/AnimalDetail.jsx`) — ainda lê de
  `data/mockData.js`; o backend já tem `/api/animais/:id` pronto.
- Favoritar animal, ver compatibilidade — endpoints prontos
  (`/api/animais/:id/favoritar`, `/api/animais/:id/compatibilidade`),
  faltando os botões nas telas.
- Fluxo de manifestação de interesse -> processo -> etapas -> visita ->
  documentos -> conclusão — todos os endpoints existem
  (`/api/manifestacoes`, `/api/processos/...`), mas as telas de
  instituição/admin que mostram "processos de adoção" ainda usam
  `data/mockData.js`.
- Cadastro de animal pela instituição/admin — precisa de um formulário
  que envie `nome`, `data_nascimento` e `caracteristicas` (lista de
  etiquetas; ver `/api/tags` para a lista válida) para `POST /api/animais`.

## Etiquetas de características (tags)

O banco não guarda mais porte/energia/etc como colunas do animal: agora
são etiquetas de um vocabulário fixo (ver `GET /api/tags`). Qualquer tela
de cadastro/edição de animal deve oferecer essas etiquetas como opções
(select ou checkboxes), nunca texto livre — o backend rejeita etiquetas
fora da lista.
