# Pet Certo — Frontend (React)

Interface do Pet Certo, consumindo a API REST do backend (ver
[`../backend/README.md`](../backend/README.md)). React 19 + Vite + React
Router 7 + Tailwind CSS.

## Rodando localmente

Com o backend já no ar em `http://localhost:8000` (ver instruções no README
da raiz do repositório):

```bash
npm install
npm run dev
```

Abra http://localhost:5173

Por padrão a API é consumida em `http://localhost:8000`. Para apontar para
outro endereço, defina `VITE_API_URL` antes de rodar (ex.:
`VITE_API_URL=http://localhost:8001 npm run dev`).

## Build de produção

```bash
npm run build
npm run preview
```

## Lint

```bash
npm run lint
```

## Estrutura

```
src/
├── pages/
│   ├── admin/      telas do administrador (usuários, instituições, animais)
│   ├── ong/         telas da instituição (animais, solicitações, visitas,
│   │                 documentos, indicadores)
│   ├── adopter/      telas do adotante (animais, solicitações, visitas,
│   │                 documentos, histórico)
│   ├── Landing.jsx, Login.jsx, Signup.jsx    páginas públicas
│   └── SystemStates.jsx                       vitrine de estados de UI
│                                               (loading, vazio, erro)
├── layouts/RoleLayout.jsx    casca comum das áreas logadas (sidebar + conteúdo)
├── components/               Sidebar, Logo, Panel/Row/Stat/ProgressBar,
│                              StatusBadge, RequireRole (guarda de rota)
├── services/api.js           todas as chamadas à API (fetch + mapeamento
│                              de campos backend ↔ frontend)
└── utils/exportarCsv.js      exportação de listas em CSV
```

## Navegação

- `/` — landing
- `/entrar` — login (aceita `?perfil=adotante|instituicao|administrador` para contexto)
- `/cadastro` — criar conta
- `/admin`, `/instituicao`, `/adotante` — painéis logados, cada um protegido por `RequireRole` (redireciona para `/entrar` se não estiver logado, ou para a própria área se o perfil não bate)
- `/estados` — vitrine dos estados de UI (loading, vazio, erro, status)

Todos os dados vêm da API real — não há mais dados mockados no projeto.
