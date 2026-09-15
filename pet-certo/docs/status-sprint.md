# Status da Sprint — Backend

## Sprint anterior (imagem 1)

| # | Item exigido | Status | Onde está |
|---|---|---|---|
| 1 | Arquitetura do sistema | ✅ | [`docs/arquitetura.md`](arquitetura.md) |
| 2 | Diagrama de Classes | ✅ | [`docs/diagrama-classes.md`](diagrama-classes.md) |
| 3 | Modelo Entidade-Relacionamento (MER) | ✅ | [`docs/mer.md`](mer.md) |
| 4 | Modelo Relacional | ✅ | [`docs/modelo-relacional.md`](modelo-relacional.md) |
| 5 | Protótipo das telas principais | ⚠️ não é escopo do backend | Fica com quem for fazer o frontend (Figma ou similar) |
| 6 | Banco de dados criado | ✅ | [`backend/database/schema.sql`](../backend/database/schema.sql) |
| 7 | Projeto estruturado no GitHub | ✅ | Este repositório |

## Sprint atual (imagem 2)

| # | Item exigido | Status | Onde está |
|---|---|---|---|
| 1 | Banco de dados conectado | ✅ | `GET /api/health` comprova a conexão em tempo real |
| 2 | Login funcional | ✅ | `POST /api/auth/login` + `backend/auth/auth_service.py` |
| 3 | Cadastro de usuários | ✅ | `POST /api/usuarios` + `backend/auth/auth_service.py` |
| 4 | Controle de perfis | ✅ | `admin`, `voluntario`, `adotante` — checado em cada rota da API (`backend/api/server.py`) |
| 5 | CRUD principal funcionando | ✅ | Entidade `Animal`, rotas `/api/animais/*`, persistência real no banco |
| 6 | Primeiro deploy local funcionando | ✅ | Ver [`backend/README.md`](../backend/README.md) — `python main.py` sobe o servidor |

## Como foi testado (não é só "no papel")

Rodei o backend de verdade num servidor local e executei o script
[`backend/scripts/demo_cliente.py`](../backend/scripts/demo_cliente.py), que
simula um frontend batendo em cada rota, em sequência:

1. `GET /api/health` → confirma banco conectado
2. Login com o admin padrão → recebe token
3. Cadastro de um novo usuário adotante → persistido no banco
4. Criação de um animal (autenticado como admin) → persistido no banco
5. Listagem de animais → retorna o animal criado
6. Atualização do status do animal → persistida
7. Tentativa de exclusão por um usuário `adotante` → **corretamente bloqueada** (403), provando que o controle de perfil funciona de verdade, não só em teoria
8. Exclusão do mesmo animal pelo admin → executada com sucesso

Todos os passos passaram. O log completo dessa execução está reproduzido no
README do backend.

## O que ainda falta (próximas sprints)

- Algoritmo de compatibilidade adotante-animal (componente de IA/otimização) — módulo já reservado em `backend/matching/compatibilidade.py`
- Fluxo de solicitação de adoção (nova entidade `Solicitacao_Adocao`)
- Frontend consumindo esta API (responsabilidade de outro integrante da equipe)
