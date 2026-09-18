# Modelo Relacional — PetCerto

Conversão do MER (`docs/mer.md`) para tabelas relacionais. Schema completo
e executável em [`backend/database/schema.sql`](../backend/database/schema.sql).

## Tabela: `usuarios`

| Coluna | Tipo | Restrições |
|---|---|---|
| id | INTEGER | **PK**, auto incremento |
| nome | TEXT | NOT NULL |
| email | TEXT | NOT NULL, **UNIQUE** |
| senha_hash | TEXT | NOT NULL — hash SHA-256 da senha, nunca texto puro |
| salt | TEXT | NOT NULL — valor aleatório único por usuário, usado no hash |
| perfil | TEXT | NOT NULL, CHECK IN (`admin`, `voluntario`, `adotante`) |
| data_cadastro | TEXT | NOT NULL, preenchido automaticamente (`datetime('now')`) |

## Tabela: `animais`

| Coluna | Tipo | Restrições |
|---|---|---|
| id | INTEGER | **PK**, auto incremento |
| nome | TEXT | NOT NULL |
| especie | TEXT | NOT NULL, CHECK IN (`cachorro`, `gato`, `outro`) |
| raca | TEXT | opcional |
| porte | TEXT | NOT NULL, CHECK IN (`pequeno`, `medio`, `grande`) |
| idade_anos | REAL | NOT NULL, padrão 0 |
| nivel_energia | TEXT | NOT NULL, CHECK IN (`baixo`, `medio`, `alto`) |
| temperamento | TEXT | opcional |
| convive_criancas | INTEGER | NOT NULL, 0 ou 1 (boolean) |
| convive_outros_pets | INTEGER | NOT NULL, 0 ou 1 (boolean) |
| necessidades_especiais | TEXT | opcional |
| espaco_recomendado | TEXT | NOT NULL, CHECK IN (`apartamento`, `casa_com_quintal`, `indiferente`) |
| status | TEXT | NOT NULL, CHECK IN (`disponivel`, `em_processo`, `adotado`), padrão `disponivel` |
| data_cadastro | TEXT | NOT NULL, preenchido automaticamente |
| cadastrado_por | INTEGER | **FK** → `usuarios.id` (pode ser nulo) |

## Chaves estrangeiras

- `animais.cadastrado_por` → `usuarios.id`

## Por que SQLite nesta sprint

O enunciado permite PostgreSQL, MySQL, SQL Server ou MongoDB, mas a equipe
ainda não bateu o martelo. SQLite foi escolhido para esta sprint por não
exigir nenhuma instalação de servidor de banco — qualquer integrante roda o
projeto localmente sem configurar nada. Como todo o acesso ao banco está
concentrado em `backend/database/`, migrar para outro SGBD relacional
(PostgreSQL/MySQL) é uma mudança pontual, sem impacto no restante do
backend (auth, CRUD, API).
