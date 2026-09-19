# Pet Certo — Backend

API REST em Python puro (sem framework), rodando sobre PostgreSQL. Todo o
schema de banco foi definido por Henrique (Banco de Dados e Documentação)
em `database/schema.sql` — o backend só o executa e trabalha em cima dele.

## Pré-requisitos

- Python 3.10+
- PostgreSQL 14+ rodando localmente (ou acessível pela rede)

## Configuração (uma vez, por máquina)

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Copie `.env.example` para `.env` e preencha com as suas credenciais
   locais do PostgreSQL:
   ```bash
   cp .env.example .env
   ```
   Abra o `.env` e coloque o `PGUSER`/`PGPASSWORD` do seu banco. **O
   arquivo `.env` nunca deve ser commitado** (já está no `.gitignore`) —
   cada pessoa do grupo usa a própria senha local, e a senha não deve ser
   compartilhada em nenhum lugar do repositório, chat ou print de tela.
3. Crie o banco de dados (uma vez):
   ```bash
   createdb petcerto
   # ou, dentro do psql:
   # CREATE DATABASE petcerto;
   ```

## Rodando

```bash
python main.py
```

Na primeira execução, o backend cria todas as tabelas do schema, popula o
vocabulário padrão de etiquetas de características (`GET /api/tags`) e
cria um administrador padrão:

- login: `admin@petcerto.com`
- senha: `admin123`

A API sobe em `http://localhost:8000`.

## Testando

```bash
# com o servidor já rodando em outro terminal:
python scripts/demo_cliente.py          # smoke test simples (GET)
python scripts/teste_fluxo_adocao.py    # fluxo completo: cadastro, login,
                                         # animal, favoritar, manifestação,
                                         # aprovação, visita, documentos,
                                         # conclusão — inclui casos de erro
python matching/benchmark.py            # benchmark do algoritmo de compatibilidade
```

## Estrutura

```
backend/
  main.py                 ponto de entrada
  database/
    schema.sql             DDL oficial (Henrique)
    tags_padrao.py          vocabulário fixo de características
    db.py                   conexão + inicialização
    animal_repository.py
    adocao_repository.py    manifestação → processo → etapas → visita → documentos
    interacoes_repository.py  favoritos, recomendações, compatibilidade, log admin
  models/                  dataclasses que espelham as tabelas
  auth/                    cadastro, login, sessão
  matching/                algoritmo de compatibilidade + benchmark
  api/server.py            servidor HTTP e rotas
  scripts/                 testes de ponta a ponta
```
