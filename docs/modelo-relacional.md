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

## Tabela: `instituicoes`

| Coluna | Tipo | Restrições |
|---|---|---|
| id | INTEGER | **PK**, auto incremento |
| nome | TEXT | NOT NULL |
| cidade | TEXT | opcional |
| status | TEXT | NOT NULL, CHECK IN (`verificada`, `pendente`, `revisao`), padrão `pendente` |
| data_cadastro | TEXT | NOT NULL, automático |

## Tabela: `solicitacoes_adocao`

| Coluna | Tipo | Restrições |
|---|---|---|
| id | INTEGER | **PK**, auto incremento |
| animal_id | INTEGER | **FK** → `animais.id`, NOT NULL |
| adotante_id | INTEGER | **FK** → `usuarios.id`, NOT NULL |
| etapa | TEXT | NOT NULL, CHECK IN (`interesse`, `analise`, `visita`, `documentos`, `aprovacao`, `concluida`), padrão `interesse` |
| status | TEXT | NOT NULL, CHECK IN (`em_andamento`, `aprovada`, `recusada`, `cancelada`), padrão `em_andamento` |
| observacoes | TEXT | opcional |
| data_solicitacao | TEXT | NOT NULL, automático |
| data_atualizacao | TEXT | NOT NULL, automático |

## Tabela: `visitas`

| Coluna | Tipo | Restrições |
|---|---|---|
| id | INTEGER | **PK**, auto incremento |
| solicitacao_id | INTEGER | **FK** → `solicitacoes_adocao.id`, NOT NULL |
| data_agendada | TEXT | NOT NULL |
| status | TEXT | NOT NULL, CHECK IN (`agendada`, `realizada`, `cancelada`, `reagendada`), padrão `agendada` |
| observacoes | TEXT | opcional |
| data_cadastro | TEXT | NOT NULL, automático |

## Coluna nova em `usuarios`

| Coluna | Tipo | Restrições |
|---|---|---|
| instituicao_id | INTEGER | **FK** → `instituicoes.id`, opcional (só preenchido para perfil `voluntario`) |

## Chaves estrangeiras

- `usuarios.instituicao_id` → `instituicoes.id`
- `animais.cadastrado_por` → `usuarios.id`
- `solicitacoes_adocao.animal_id` → `animais.id`
- `solicitacoes_adocao.adotante_id` → `usuarios.id`
- `visitas.solicitacao_id` → `solicitacoes_adocao.id`

## Por que SQLite nesta sprint

O enunciado permite PostgreSQL, MySQL, SQL Server ou MongoDB, mas a equipe
ainda não bateu o martelo. SQLite foi escolhido para esta sprint por não
exigir nenhuma instalação de servidor de banco — qualquer integrante roda o
projeto localmente sem configurar nada. Como todo o acesso ao banco está
concentrado em `backend/database/`, migrar para outro SGBD relacional
(PostgreSQL/MySQL) é uma mudança pontual, sem impacto no restante do
backend (auth, CRUD, API).
