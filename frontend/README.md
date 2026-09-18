# Pet Certo — Front-end (React)

Front-end estático (mock, sem backend) do Pet Certo, reproduzindo as telas do
protótipo Figma para os três perfis: **Administrador**, **Instituição / ONG**
e **Adotante**, além de Landing, Login e Cadastro.

## Rodando localmente

```bash
npm install
npm run dev
```

Abra http://localhost:5173

## Build de produção

```bash
npm run build
npm run preview
```

## Estrutura

- `src/pages/` — páginas (Landing, Login, Cadastro, e uma pasta por perfil)
- `src/layouts/RoleLayout.jsx` — casca com sidebar colorida por perfil
- `src/components/` — Sidebar, Panel/Row/Stat/ProgressBar, StatusBadge
- `src/data/mockData.js` — dados mockados (animais, solicitações, visitas, documentos, histórico)

## Navegação rápida

- `/` — landing
- `/entrar` — login (tem atalhos de demonstração para os 3 perfis)
- `/cadastro` — criar conta
- `/admin` — painel do administrador
- `/instituicao` — painel da instituição/ONG
- `/adotante` — painel do adotante
- `/estados` — vitrine dos estados de sistema (loading, vazio, erro, status)

Todos os dados são mockados em memória (não há chamadas de API/backend).
