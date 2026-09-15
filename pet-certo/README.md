# PetCerto 🐾

Sistema de adoção de animais com matching inteligente — projeto da disciplina
de Fábrica de Software (integrado com Tópicos Avançados), UNINASSAU, 2026.2.

Repositório: https://github.com/lucascarneiroo/pet-certo

## O problema

Abrigos e ONGs fazem adoção de forma manual, quase sempre só pela foto do
animal. Isso gera uma taxa alta de devolução: o animal não combina com a
rotina, o espaço ou a experiência do adotante. O PetCerto resolve isso
casando adotante e animal por **compatibilidade real**.

## Organização do repositório

Este projeto é dividido entre backend e frontend, times separados que se
comunicam por uma API (não é um app único):

```
pet-certo/
├── backend/     ← API REST em Python (autenticação, regras de negócio, banco de dados)
├── frontend/    ← interface do sistema (tecnologia a definir pela equipe)
└── docs/        ← arquitetura, diagramas, modelo de dados, documentação da API
```

- **Backend:** ver [`backend/README.md`](backend/README.md) para rodar localmente.
- **Frontend:** ver [`frontend/README.md`](frontend/README.md) para saber como consumir a API.
- **Documentação técnica:** ver [`docs/`](docs/) — arquitetura, diagrama de classes, MER, modelo relacional e status de cada sprint.

## Status do projeto

| Entrega | Status |
|---|---|
| Arquitetura, diagrama de classes, MER, modelo relacional | ✅ [`docs/`](docs/) |
| Banco de dados criado e conectado | ✅ |
| Login funcional | ✅ |
| Cadastro de usuários | ✅ |
| Controle de perfis | ✅ |
| CRUD principal (animais) | ✅ |
| Deploy local do backend | ✅ |
| Frontend | ⏳ a cargo da equipe |
| Algoritmo de compatibilidade (IA/otimização) | ⏳ próxima sprint |

Detalhamento completo, item a item: [`docs/status-sprint.md`](docs/status-sprint.md).

## Tecnologias

- **Backend:** Python 3 (biblioteca padrão apenas, sem frameworks), SQLite
- **Frontend:** a definir pela equipe
- **Versionamento:** Git + GitHub

## Equipe

_Preencher com os nomes e papéis de cada integrante (Scrum Master, Product Owner, Dev Backend, Dev Frontend, Responsável por Banco/Documentação)._
