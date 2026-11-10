# Sprint 11 — Revisão de código e organização do GitHub

Repositório: https://github.com/lucascarneiroo/pet-certo

## 1. Revisão completa do código

**Código morto removido** (achado com `pyflakes` no backend e `oxlint` no frontend):

- `backend/api/server.py`: 2 imports nunca usados (`buscar_usuario_por_email`, `listar_recomendacoes`).
- `backend/auth/auth_service.py`: 1 import (`os`) e 1 variável local nunca usados.
- `frontend/src/data/mockData.js`: arquivo inteiro removido (166 linhas) — sobra da época do frontend só-mock.
- `frontend/src/pages/ong/Visits.jsx`: import de hook não usado (`useMemo`).
- `frontend/src/pages/Login.jsx`: o parâmetro `?perfil=` nunca era usado na tela — aproveitado para mostrar "Entrando como adotante/instituição/admin".

**Dados sensíveis:** nenhuma credencial hardcoded no código; `.env` nunca foi commitado, nem no histórico.

**Testes:** as 57 verificações automatizadas (compatibilidade + fluxo de adoção + validação) reconfirmadas passando após a limpeza.

## 2. Organização do GitHub

- **Bug encontrado:** o `.gitignore` da raiz tinha marcadores de conflito de merge (`<<<<<<<`, `=======`, `>>>>>>>`) commitados sem nunca terem sido resolvidos de verdade — apesar de existir um commit anterior chamado "Resolve conflito no .gitignore". Reescrito do zero.
- `.idea/` (configuração pessoal do IntelliJ) destravado do rastreamento — já estava no `.gitignore`, mas continuava versionado de antes da regra existir. Sem informação sensível.
- `package-lock.json` órfão na raiz (sem `package.json` correspondente, vazio) removido.
- `frontend/README.md` reescrito — ainda descrevia uma versão mock sem backend.
- Histórico de commits conferido: cronológico, organizado por sprint, mensagens descritivas.

Commits: [`acfb27b`](https://github.com/lucascarneiroo/pet-certo/commit/acfb27b), [`6562e42`](https://github.com/lucascarneiroo/pet-certo/commit/6562e42).
