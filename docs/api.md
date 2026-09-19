# API do backend Pet Certo

Servidor HTTP em Python puro (`http.server`), porta 8000. Autenticação via
token em `Authorization: Bearer <token>`, obtido no login.

## Autenticação e cadastro

| Método | Rota | Autenticado | Descrição |
|---|---|---|---|
| POST | /api/auth/login | não | `{email, senha}` → `{token, usuario}` |
| GET | /api/auth/me | sim | dados do usuário logado |
| POST | /api/auth/logout | sim | encerra a sessão |
| POST | /api/usuarios | não | cadastra adotante/instituição/administrador |
| GET | /api/instituicoes | não | lista instituições cadastradas |
| GET | /api/tags | não | lista as etiquetas padrão de características |

## Animais

| Método | Rota | Quem pode | Descrição |
|---|---|---|---|
| GET | /api/animais?status=&id_instituicao= | qualquer | lista animais (filtros opcionais) |
| GET | /api/animais/:id | qualquer | detalhe de um animal |
| POST | /api/animais | instituição/admin | cadastra animal com etiquetas |
| PUT | /api/animais/:id | dono do animal/admin | atualiza dados/etiquetas/status |
| DELETE | /api/animais/:id | admin | remove animal |
| POST/DELETE | /api/animais/:id/favoritar | adotante | favoritar / desfavoritar |
| GET | /api/animais/:id/compatibilidade | adotante | calcula e salva score de compatibilidade |
| GET | /api/favoritos | adotante | lista favoritos do adotante logado |
| GET | /api/recomendacoes | adotante | top 10 recomendados pelo algoritmo |

## Fluxo de adoção

| Método | Rota | Quem pode | Descrição |
|---|---|---|---|
| GET/POST | /api/manifestacoes | adotante/instituição/admin | listar / manifestar interesse |
| POST | /api/manifestacoes/:id/aprovar | instituição dona/admin | cria o processo de adoção |
| POST | /api/manifestacoes/:id/recusar | instituição dona/admin | recusa a manifestação |
| GET | /api/processos | adotante/instituição/admin | lista processos |
| GET | /api/processos/:id/etapas | autenticado | lista as 4 etapas do processo |
| PUT | /api/processos/:id/etapas/:idEtapa | instituição dona/admin | atualiza status da etapa |
| GET/POST | /api/instituicoes/:id/horarios | autenticado | listar/criar horários de visita |
| GET/POST | /api/processos/:id/visitas | instituição dona/admin (POST) | listar/agendar visita |
| PUT | /api/visitas/:id | instituição/admin | atualiza status/resultado da visita |
| GET/POST | /api/processos/:id/documentos | autenticado | listar/enviar documento |
| GET | /api/processos/:id/historico | autenticado | log de auditoria do processo |
| POST | /api/processos/:id/concluir | instituição dona/admin | efetiva a adoção |
| POST | /api/processos/:id/cancelar | instituição dona/admin | cancela o processo |

Todas as respostas de erro têm o formato `{"erro": "mensagem"}`, com o
status HTTP correspondente (400 dados inválidos, 401 não autenticado, 403
sem permissão, 404 não encontrado, 409 e-mail já cadastrado).
