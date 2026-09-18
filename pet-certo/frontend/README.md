# Frontend do PetCerto

Esta pasta é reservada para a interface do sistema — tecnologia ainda a ser
definida pela equipe (web, mobile ou desktop).

O frontend deve consumir a API do backend, documentada em
[`../docs/api.md`](../docs/api.md). Resumo rápido para quem for começar:

1. `POST /api/auth/login` com e-mail e senha → recebe um `token`
2. Guardar esse token e enviá-lo em toda requisição seguinte, no cabeçalho:
   `Authorization: Bearer <token>`
3. A partir daí, `GET/POST/PUT/DELETE` em `/api/animais` fazem o CRUD principal

O backend já roda localmente em `http://localhost:8000` (instruções em
[`../backend/README.md`](../backend/README.md)) e aceita chamadas de
qualquer origem (CORS liberado), então o frontend pode ser desenvolvido e
testado de forma independente, sem precisar mexer no backend.
