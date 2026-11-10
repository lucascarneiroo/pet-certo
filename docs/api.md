# API do Pet Certo

API REST em Python puro (`http.server`, sem framework), rodando sobre PostgreSQL.
Base URL local: `http://localhost:8000`.

## Autenticação

A maioria das rotas exige um token de sessão, obtido em `POST /api/auth/login`
e enviado em todas as chamadas seguintes no cabeçalho:

```
Authorization: Bearer <token>
```

Rotas sem esse cabeçalho (ou com um token inválido/expirado) retornam
**401 Unauthorized**. Rotas que exigem um perfil específico (ex.: só
administrador) retornam **403 Forbidden** quando o usuário autenticado
não tem o perfil certo.

Todas as respostas são JSON. Erros seguem o formato:
```json
{ "erro": "Mensagem descrevendo o problema." }
```

Perfis existentes: `adotante`, `instituicao`, `administrador`.

---

## Saúde

### `GET /api/health`
Sem autenticação. Usado para checar se a API está no ar.

**Resposta 200**
```json
{ "status": "ok", "servico": "Pet Certo API" }
```

---

## Autenticação e sessão

### `POST /api/auth/login`
Sem autenticação.

**Corpo**
```json
{ "email": "ana@example.com", "senha": "123456" }
```

**Resposta 200**
```json
{
  "token": "a1b2c3...",
  "usuario": { "id": 5, "nome": "Ana", "email": "ana@example.com", "perfil": "adotante", "cpf": "...", "endereco": "...", "score_perfil": 0.0 }
}
```
**Erros:** `401` — e-mail ou senha inválidos (mensagem genérica; não revela se o e-mail existe).

### `GET /api/auth/me`
Autenticado. Retorna os dados do usuário dono do token enviado.

### `POST /api/auth/logout`
Autenticado. Invalida o token enviado no cabeçalho `Authorization`.
**Resposta 200:** `{ "ok": true }`

---

## Usuários

### `POST /api/usuarios`
Sem autenticação (cadastro público). Campos variam por perfil.

**Corpo (comum a todos os perfis)**
```json
{ "nome": "Ana", "email": "ana@example.com", "senha": "123456", "perfil": "adotante" }
```
**Campos adicionais por perfil:**
- `adotante`: `cpf` (obrigatório), `endereco` (obrigatório)
- `instituicao`: `cnpj` (obrigatório), `localizacao` (obrigatório), `info_abrigo` (opcional)
- `administrador`: não aceita cadastro público — criado apenas via `ADMIN_EMAIL`/`ADMIN_SENHA` no `.env` do backend.

**Resposta 201:** objeto do usuário criado (sem a senha).
**Erros:** `400` e-mail inválido / senha curta (mín. 6 caracteres) / perfil inválido / campo obrigatório do perfil ausente. `409` e-mail já cadastrado.

### `GET /api/usuarios`
**Admin apenas.** Lista todos os usuários da plataforma (qualquer perfil), com os campos específicos de cada um.

### `GET /api/instituicoes`
Sem autenticação. Lista as instituições cadastradas (para telas públicas, ex.: escolher instituição no cadastro de horário).

---

## Painel administrativo

### `GET /api/admin/registros`
**Admin apenas.** Lista o log de ações administrativas (exclusão de animal, conclusão/cancelamento de processo), mais recentes primeiro.

**Resposta 200**
```json
[
  { "id": 3, "id_administrador": 1, "tipo_atividade": "Exclusão de Animal", "data_hora": "...", "descricao": "Animal 'Mia' removido da plataforma." }
]
```

---

## Etiquetas de características

### `GET /api/tags`
Sem autenticação. Retorna o vocabulário fixo de etiquetas usado em animais e no perfil de compatibilidade do adotante.

**Resposta 200**
```json
{ "tags": ["Espécie: Cão", "Espécie: Gato", "Porte: Pequeno", "..."] }
```

---

## Animais

### `GET /api/animais`
Sem autenticação. Parâmetros de query (todos opcionais):
- `status` — `Disponível` | `Em Processo` | `Adotado`
- `id_instituicao` — filtra por instituição
- `busca` — substring no nome (case-insensitive)
- `caracteristicas` — uma ou mais etiquetas (`?caracteristicas=A&caracteristicas=B` ou `?caracteristicas=A,B`); o animal precisa ter **todas** as etiquetas informadas

**Resposta 200:** lista de animais:
```json
[{
  "id": 8, "id_instituicao": 2, "nome_instituicao": "Abrigo X", "nome": "Pingo",
  "data_nascimento": "2023-10-02", "status": "Disponível",
  "caracteristicas": ["Espécie: Cão", "Porte: Pequeno"], "url_foto": "https://..."
}]
```

### `GET /api/animais/:id`
Sem autenticação. `404` se não existir.

### `POST /api/animais`
**Instituição ou admin.** Instituição cadastra para si mesma; admin precisa informar `id_instituicao` no corpo.

**Corpo**
```json
{ "nome": "Pingo", "data_nascimento": "2023-10-02", "caracteristicas": ["Espécie: Cão"], "url_foto": "https://..." }
```
**Erros:** `400` nome ausente/vazio, data em formato inválido (use `AAAA-MM-DD`), ou característica fora do vocabulário de `/api/tags`.

### `PUT /api/animais/:id`
**Dono (instituição) ou admin.** Corpo aceita os mesmos campos de `POST`, todos opcionais — só o que for enviado é atualizado — mais `status`.

### `DELETE /api/animais/:id`
**Admin apenas.** Registra a exclusão no log administrativo.

### `POST /api/animais/:id/favoritar` · `DELETE /api/animais/:id/favoritar`
**Adotante.** Adiciona/remove o animal dos favoritos do adotante autenticado.

### `GET /api/animais/:id/compatibilidade`
**Adotante.** Calcula o score de compatibilidade (0–100) entre o adotante autenticado e o animal, a partir do perfil aprendido dos seus favoritos.

**Resposta 200**
```json
{ "score": 72.4, "fatores": [{ "criterio": "Porte", "valor_do_animal": "Pequeno", "afinidade_pct": 90.0, "peso_pct": 20 }] }
```

---

## Favoritos e recomendações

### `GET /api/favoritos`
**Adotante.** Lista os animais favoritados pelo usuário autenticado.

### `GET /api/recomendacoes`
**Adotante.** Lista animais recomendados pelo núcleo de compatibilidade (ranking Gale-Shapley/score), a partir dos favoritos do adotante.

---

## Manifestações de interesse

### `GET /api/manifestacoes`
Autenticado. Adotante vê as próprias; instituição vê as dos seus animais; admin vê todas.

### `POST /api/manifestacoes`
**Adotante.** Corpo: `{ "id_animal": 8 }`.
**Erros:** `400` animal inexistente, animal não está `Disponível`, ou já existe manifestação pendente do mesmo adotante para o mesmo animal.

### `POST /api/manifestacoes/:id/aprovar`
**Instituição dona do animal, ou admin.** Cria o `ProcessoAdocao` com as 4 etapas padrão (Análise, Visita, Documentação, Aprovação) e muda o animal para `Em Processo`.

### `POST /api/manifestacoes/:id/recusar`
**Instituição dona do animal, ou admin.**

### `GET /api/manifestacoes/:id/compatibilidade`
**Instituição ou admin.** Mesmo cálculo de `/api/animais/:id/compatibilidade`, para a instituição avaliar o adotante por trás de uma manifestação.

---

## Processos de adoção

### `GET /api/processos`
Autenticado. Adotante vê os próprios; instituição vê os das suas manifestações; admin vê todos.

### `GET /api/processos/:id/etapas`
Autenticado. `404` se o processo não existir.

### `PUT /api/processos/:id/etapas/:idEtapa`
**Instituição dona do processo, ou admin.** Corpo: `{ "status": "Concluída", "observacao": "opcional" }` (`status` ∈ `Em Andamento | Concluída | Reprovada`). Ao concluir uma etapa, a próxima etapa pendente passa automaticamente para `Em Andamento`.

### `GET /api/processos/:id/visitas` · `POST /api/processos/:id/visitas`
Autenticado (GET) / **instituição dona ou admin** (POST). `POST` agenda uma visita a partir de um horário disponível: `{ "id_horario": 3 }`.

### `GET /api/processos/:id/documentos` · `POST /api/processos/:id/documentos`
Autenticado. `POST`: `{ "nome": "RG", "caminho_arquivo": "/uploads/rg.pdf" }`. `400` se `nome` vier vazio.

### `GET /api/processos/:id/historico`
Autenticado. Linha do tempo de auditoria do processo (criação, mudanças de etapa, visita, documento, conclusão/cancelamento).

### `POST /api/processos/:id/concluir`
**Instituição dona do processo, ou admin.** Exige que o processo esteja `Em Andamento` **e** que as 4 etapas estejam `Concluída` — senão retorna `400`. Muda o animal para `Adotado`.

### `POST /api/processos/:id/cancelar`
**Instituição dona do processo, ou admin.** Corpo opcional: `{ "motivo": "..." }`. Devolve o animal para `Disponível`, a menos que exista outro processo `Em Andamento` para o mesmo animal.

**Erros comuns às rotas de processo:** `404` processo inexistente; `403` processo pertence a outra instituição.

---

## Visitas e horários

### `PUT /api/visitas/:id`
**Instituição ou admin.** Corpo: `{ "status": "Realizada", "resultado": "opcional" }` (`status` ∈ `Agendada | Realizada | Cancelada`).

### `GET /api/instituicoes/:id/horarios`
Autenticado. Lista os horários de visita disponíveis de uma instituição.

### `POST /api/instituicoes/:id/horarios`
**A própria instituição, ou admin.** Corpo: `{ "data_hora": "2026-11-20T10:00:00" }`.

---

## Exemplo de uso completo (curl)

```bash
# 1. login
curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ana@example.com","senha":"123456"}'

# 2. usar o token retornado nas chamadas seguintes
curl -s http://localhost:8000/api/animais \
  -H "Authorization: Bearer <token>"
```

---

## Observações

- Erros de dados inválidos retornam `400` com mensagem explicando o campo problemático.
- Erros de autenticação retornam `401`; de autorização (perfil errado ou recurso de outra pessoa), `403`; de recurso inexistente, `404`.
- CORS está liberado (`Access-Control-Allow-Origin: *`) para o frontend poder chamar a API de `http://localhost:5173` em desenvolvimento.
- Não há paginação nas listagens — o volume de dados do projeto (uso acadêmico) não justifica.
