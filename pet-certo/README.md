# PetCerto

Sistema de adoção de animais para a disciplina de Fábrica de Software (integrado com Tópicos Avançados) - UNINASSAU, 2026.2.

A ideia é resolver um problema real de abrigos: hoje a adoção é feita só pela foto do animal, e isso gera bastante devolução depois porque o bicho não combina com a rotina de quem adotou. O sistema vai cruzar o perfil do adotante com o perfil do animal pra sugerir adoções com mais chance de dar certo.

## Time

- PO / Scrum Master: Monique Rafaela de Carvalho Lopes
- Backend: Lucas Oliveira Carneiro
- Frontend: José Carlos Moura Silva
- Banco de dados e Documentação: Henrique Márcio Silva da Hora

## Como está organizado

O projeto é separado em backend e frontend, que conversam entre si por uma API. Não é um programa só, então backend e frontend podem ser desenvolvidos separado.

pet-certo/
├── backend/ -> API em Python (login, cadastro, permissões, CRUD, banco)
├── frontend/ -> interface (ainda sendo definida)
└── docs/ -> arquitetura, diagramas, documentação da API


## Tecnologias

- Backend: Python 3, sem framework (só biblioteca padrão), SQLite
- Frontend: a definir
- Git/GitHub pra versionamento

## Rodando o backend

Entra na pasta backend e roda:

```bash
python main.py
```

Isso sobe o servidor em `http://localhost:8000`. Na primeira vez ele já cria o banco e um usuário admin (`admin@petcerto.com` / `admin123`, só pra testes).

Pra testar se tá tudo funcionando sem precisar do frontend pronto, abre outro terminal e roda:

```bash
python scripts/demo_cliente.py
```

Ele simula um frontend chamando a API inteira (login, cadastro, criar/editar/excluir animal) e mostra se deu tudo certo.

Documentação das rotas da API: `docs/api.md`.
