# Integração com o backend

Este frontend agora conecta de verdade com o backend em algumas telas.
O restante ainda usa dados mockados (`src/data/mockData.js`) porque o
backend ainda não tem as tabelas/rotas correspondentes.

## O que já está conectado

| Tela | Status |
|---|---|
| Login (`src/pages/Login.jsx`) | ✅ conectado — valida e-mail/senha de verdade no backend |
| Cadastro (`src/pages/Signup.jsx`) | ✅ conectado — cria usuário real no banco (campo de senha foi adicionado, não existia antes) |
| Lista de animais do adotante (`src/pages/adopter/Animals.jsx`) | ✅ conectado — busca animais reais via `GET /api/animais` |
| Todo o resto (Instituições, Solicitações, Visitas, Documentos, Indicadores, CRUD de animais do admin/ONG) | ⏳ ainda mockado — backend não tem essas tabelas/rotas ainda |

## Como rodar os dois juntos

Terminal 1 — backend:
```bash
cd backend
python main.py
```

Terminal 2 — frontend:
```bash
cd pet-certo   # esta pasta
npm install
npm run dev
```

Abra o endereço que o Vite mostrar (geralmente `http://localhost:5173`).
O frontend já sabe chamar `http://localhost:8000` por padrão (configurável
em `.env`, veja `.env.example`).

## Mapeamento de perfis

O frontend usa os nomes `adotante`, `instituicao`, `administrador`. O
backend usa `adotante`, `voluntario`, `admin`. A conversão é feita
automaticamente em `src/services/api.js` (`PERFIL_FRONT_PARA_BACK`).
`instituicao` no frontend vira `voluntario` no backend — é o perfil mais
parecido disponível hoje. Se o grupo decidir criar um perfil próprio pra
instituição/ONG, isso muda no backend e nesse mapeamento.

## Onde fica a lógica de conexão

Tudo centralizado em `src/services/api.js`: guarda o token de sessão,
converte o formato dos dados do backend (campos em português, códigos
como `medio`/`grande`) pro formato que as telas esperam (`age: "2 anos"`,
`size: "Porte médio"`, etc.), e trata erros de forma padronizada. Nenhuma
tela deve chamar `fetch()` direto — sempre importar as funções desse
arquivo.

## O que falta pra conectar o resto

- **Instituições**: precisa de uma tabela nova no backend (`instituicoes`),
  hoje só existe `usuarios` com perfil `voluntario`
- **Solicitações de adoção**: precisa de uma tabela com o fluxo de etapas
  (Interesse → Análise → Visita → Documentos → Aprovação → Conclusão) e
  rotas de API pra cada transição de status
- **Visitas, Documentos, Indicadores**: idem — nenhuma dessas entidades
  existe no backend ainda
- **CRUD de animais nas telas de admin/ONG**: a lógica já existe no
  backend (mesma rota `/api/animais` usada pela tela do adotante), só
  falta trocar o `mockData` por chamadas reais nessas telas, do mesmo
  jeito que foi feito em `adopter/Animals.jsx`
- **Score de compatibilidade (`compat`)**: existe no backend
  (`backend/matching/compatibilidade.py`), mas ainda não está exposto
  como rota de API — por isso `api.js` devolve `compat: null` por
  enquanto
