# Documentação da API — PetCerto Backend

URL base local: `http://localhost:8000`

Todas as respostas são em JSON. Rotas marcadas como **autenticada** exigem
o cabeçalho:

```
Authorization: Bearer <token>
```

O token é obtido em `POST /api/auth/login`.

---

## Saúde do sistema

### `GET /api/health`
Verifica se o backend e o banco de dados estão respondendo. Não exige autenticação.

**Resposta 200:**
```json
{ "status": "ok", "banco_de_dados": "conectado" }
```

---

## Autenticação

### `POST /api/auth/login`
**Corpo:**
```json
{ "email": "admin@petcerto.com", "senha": "admin123" }
```
**Resposta 200:**
```json
{
  "token": "f262377ec4fcd6bad9a9c25...",
  "usuario": { "id": 1, "nome": "Administrador", "email": "admin@petcerto.com", "perfil": "admin", "data_cadastro": "..." }
}
```
**Resposta 401** (credenciais erradas):
```json
{ "erro": "E-mail ou senha inválidos." }
```

### `GET /api/auth/me` — autenticada
Retorna os dados do usuário dono do token enviado.

---

## Usuários

### `POST /api/usuarios`
Cadastro público (qualquer pessoa pode se cadastrar como `adotante` ou `voluntario` — o perfil `admin` não pode ser auto-atribuído por aqui).

**Corpo:**
```json
{ "nome": "Maria Silva", "email": "maria@teste.com", "senha": "senha123", "perfil": "adotante" }
```
**Resposta 201:** dados do usuário criado.
**Resposta 400:** e-mail já cadastrado ou dado inválido.

### `GET /api/usuarios` — autenticada, somente `admin`
Lista todos os usuários cadastrados.

---

## Animais (CRUD principal)

### `GET /api/animais` — autenticada (qualquer perfil)
Lista todos os animais cadastrados.

### `GET /api/animais/{id}` — autenticada (qualquer perfil)
Retorna um animal específico.

### `POST /api/animais` — autenticada, `admin` ou `voluntario`
**Corpo:**
```json
{
  "nome": "Rex",
  "especie": "cachorro",
  "raca": "SRD",
  "porte": "medio",
  "idade_anos": 2,
  "nivel_energia": "alto",
  "temperamento": "brincalhao",
  "convive_criancas": true,
  "convive_outros_pets": true,
  "necessidades_especiais": "",
  "espaco_recomendado": "casa_com_quintal"
}
```
Valores aceitos:
- `especie`: `cachorro`, `gato`, `outro`
- `porte`: `pequeno`, `medio`, `grande`
- `nivel_energia`: `baixo`, `medio`, `alto`
- `espaco_recomendado`: `apartamento`, `casa_com_quintal`, `indiferente`

**Resposta 201:** animal criado, com `id` gerado.

### `PUT /api/animais/{id}` — autenticada, `admin` ou `voluntario`
Envie só os campos que quer atualizar. Exemplo (mudar status):
```json
{ "status": "adotado" }
```

### `DELETE /api/animais/{id}` — autenticada, somente `admin`
**Resposta 200:**
```json
{ "mensagem": "Animal excluído com sucesso." }
```
**Resposta 403** (perfil sem permissão):
```json
{ "erro": "Seu perfil ('adotante') não tem permissão para essa ação." }
```

---

## Exemplo completo com `curl`

```bash
# login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@petcerto.com","senha":"admin123"}'

# criar animal (troque SEU_TOKEN pelo token recebido no login)
curl -X POST http://localhost:8000/api/animais \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{"nome":"Rex","especie":"cachorro","raca":"SRD","porte":"medio","idade_anos":2,"nivel_energia":"alto","temperamento":"brincalhao","convive_criancas":true,"convive_outros_pets":true,"necessidades_especiais":"","espaco_recomendado":"casa_com_quintal"}'
```

Um exemplo completo e automatizado (que roda todas as rotas em sequência e
confere se cada resposta está correta) está em
[`backend/scripts/demo_cliente.py`](../backend/scripts/demo_cliente.py).
