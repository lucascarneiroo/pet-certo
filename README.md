# Pet Certo 🐾

Sistema de adoção de animais com matching inteligente entre adotantes e
abrigos/ONGs — projeto da disciplina de Fábrica de Software (integrado com
Tópicos Avançados), UNINASSAU, 2026.2.

Repositório: https://github.com/lucascarneiroo/pet-certo

## Objetivo da solução

Abrigos e ONGs fazem adoção de forma manual, quase sempre só pela foto do
animal. Isso gera uma taxa alta de devolução: o animal não combina com a
rotina, o espaço ou a experiência do adotante. O Pet Certo resolve isso
casando adotante e animal por **compatibilidade real** (porte, energia,
espaço, espécie, experiência e convivência), e acompanha todo o processo de
adoção — da manifestação de interesse até a conclusão — com etapas, visitas,
documentos e histórico auditável.

Perfis de uso: **adotante** (descobre animais compatíveis, acompanha a
adoção), **instituição/ONG** (cadastra animais, avalia solicitações, gerencia
o processo) e **administrador** (supervisiona usuários, instituições e a
saúde geral da plataforma).

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Backend | Python 3 (`http.server` da biblioteca padrão, sem framework web) |
| Banco de dados | PostgreSQL |
| Driver do banco | `pg8000` |
| Autenticação | `bcrypt` (hash de senha) + tokens de sessão em memória |
| Frontend | React 19 + Vite + React Router 7 + Tailwind CSS |
| Núcleo de compatibilidade | NumPy (versão vetorizada) + `multiprocessing` (versão paralela) |

## Requisitos necessários para execução

- Python 3.10 ou superior
- Node.js 18 ou superior (com `npm`)
- PostgreSQL 14 ou superior, rodando localmente (ou acessível pela rede)

## Instalação e configuração

### 1. Clonar o repositório

```bash
git clone https://github.com/lucascarneiroo/pet-certo.git
cd pet-certo
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

Abra o `.env` e preencha com as suas credenciais locais do PostgreSQL
(`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`). Esse arquivo
nunca é commitado — cada pessoa usa a própria senha.

Se quiser um administrador criado automaticamente na primeira execução,
defina também `ADMIN_EMAIL` e `ADMIN_SENHA` no mesmo `.env`. **Não existe
login de administrador fixo no código** — sem essas variáveis, nenhum admin
é criado sozinho (veja [`backend/README.md`](backend/README.md) para
promover um usuário manualmente).

### 3. Frontend

```bash
cd ../frontend
npm install
```

## Configurando o banco de dados

```bash
# dentro do psql, ou com createdb:
createdb petcerto
```

Não é preciso rodar nenhum script de migração à parte: na primeira execução
do backend (`python main.py`), o próprio sistema cria todas as tabelas (a
partir de [`backend/database/schema.sql`](backend/database/schema.sql)) e
popula o vocabulário fixo de etiquetas de características dos animais. Em
execuções seguintes, isso é feito de forma idempotente (`CREATE TABLE IF NOT
EXISTS` + `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` quando necessário) — não
apaga dados existentes.

## Executando o sistema

Em dois terminais separados:

```bash
# terminal 1 — backend, sobe em http://localhost:8000
cd backend
python main.py
```

```bash
# terminal 2 — frontend, sobe em http://localhost:5173
cd frontend
npm run dev
```

Abra `http://localhost:5173` no navegador.

### Verificando que está tudo funcionando

```bash
curl http://localhost:8000/api/health
# {"status": "ok", "servico": "Pet Certo API"}
```

Também há scripts de teste automatizado (rodar de dentro de `backend/`, com
o servidor já no ar):

```bash
python scripts/teste_fluxo_adocao.py    # fluxo completo ponta a ponta
python scripts/teste_validacao.py       # dados inválidos e regras de negócio
python -m scripts.teste_compatibilidade # núcleo de compatibilidade (não precisa do servidor rodando)
```

## Estrutura do projeto

```
pet-certo/
├── backend/
│   ├── main.py                   ponto de entrada da API
│   ├── database/
│   │   ├── schema.sql             DDL oficial do banco (Henrique)
│   │   ├── db.py                  conexão + inicialização
│   │   ├── animal_repository.py
│   │   ├── adocao_repository.py   manifestação → processo → etapas → visita → documentos
│   │   └── interacoes_repository.py  favoritos, recomendações, compatibilidade, log admin
│   ├── models/                   dataclasses que espelham as tabelas
│   ├── auth/                     cadastro, login, sessão, bcrypt
│   ├── matching/                 algoritmo de compatibilidade + benchmark
│   ├── api/server.py             servidor HTTP e roteamento
│   └── scripts/                  testes de ponta a ponta
├── frontend/
│   └── src/
│       ├── pages/{admin,ong,adopter}/  telas por perfil
│       ├── components/                 Panel, Sidebar, Logo, StatusBadge...
│       ├── layouts/RoleLayout.jsx       layout comum logado
│       └── services/api.js              chamadas à API
└── docs/
    ├── api.md                     referência completa da API
    ├── mer.md, arquitetura.md     modelo de dados e arquitetura
    └── (demais documentos de sprint, com evidências de cada entrega)
```

## Documentação adicional

- [`docs/api.md`](docs/api.md) — referência completa de todas as rotas da API (métodos, autenticação, parâmetros, respostas, exemplos).
- [`backend/README.md`](backend/README.md) — detalhes de configuração e scripts do backend.
- [`frontend/README.md`](frontend/README.md) — detalhes de configuração, lint e estrutura do frontend.
- [`docs/`](docs/) — demais documentos técnicos (arquitetura, modelo de dados, decisões de cada sprint).

## Equipe

- **PO / Scrum Master:** Monique Rafaela de Carvalho Lopes
- **Backend:** Lucas Oliveira Carneiro
- **Frontend:** José Carlos Moura Silva
- **Banco de dados e Documentação:** Henrique Márcio Silva da Hora
