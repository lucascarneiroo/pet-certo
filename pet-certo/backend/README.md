# PetCerto — Backend

API REST em Python puro (sem frameworks) que expõe autenticação, cadastro
de usuários, controle de perfis e o CRUD de animais. Qualquer frontend
(web, mobile, desktop) pode consumir esta API pela rede.

Documentação completa das rotas: [`../docs/api.md`](../docs/api.md).
Arquitetura, diagramas e modelo de dados: pasta [`../docs/`](../docs/).

## Pré-requisitos

- Python 3.10 ou superior (não precisa instalar mais nada — tudo aqui usa a biblioteca padrão)

## Como executar localmente

```bash
# 1. Entrar na pasta do backend
cd backend

# 2. (Recomendado) criar um ambiente virtual
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Instalar dependências (nenhuma externa nesta sprint)
pip install -r requirements.txt

# 4. Iniciar o servidor
python main.py
```

Você verá:
```
PetCerto backend rodando em http://localhost:8000
```

Na primeira execução, o banco `data/pet_certo.db` é criado automaticamente
com as tabelas e um usuário administrador padrão:

- **E-mail:** `admin@petcerto.com`
- **Senha:** `admin123`

## Como provar que está tudo funcionando

Com o servidor rodando, abra **outro terminal** (deixe o servidor rodando no primeiro) e execute:

```bash
cd backend
python scripts/demo_cliente.py
```

Esse script chama a API de verdade (login, cadastro, criar/listar/atualizar/excluir animal, checagem de permissão por perfil) e imprime cada resposta. Se tudo passar, aparece no final:

```
TUDO FUNCIONANDO — backend validado de ponta a ponta
```

Isso serve como demonstração do backend mesmo antes do frontend estar pronto.

## Testando manualmente com curl (opcional)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@petcerto.com","senha":"admin123"}'
```

Mais exemplos em [`../docs/api.md`](../docs/api.md).

## Estrutura desta pasta

```
backend/
├── main.py                    # ponto de entrada — inicia o servidor
├── requirements.txt
├── api/
│   └── server.py              # rotas HTTP, autenticação por token, CORS
├── auth/
│   ├── auth_service.py        # login, cadastro, hash de senha
│   └── session_service.py     # tokens de sessão
├── database/
│   ├── schema.sql             # estrutura do banco
│   ├── db.py                  # conexão + inicialização
│   └── animal_repository.py   # CRUD de animais
├── models/
│   ├── usuario.py
│   └── animal.py
├── matching/
│   └── compatibilidade.py     # reservado para a próxima sprint
├── scripts/
│   └── demo_cliente.py        # simula um frontend chamando a API
└── data/                      # banco SQLite gerado em runtime (não versionado)
```
