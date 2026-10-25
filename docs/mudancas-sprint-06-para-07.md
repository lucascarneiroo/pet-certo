# O que mudou — Sprint 06 → Sprint 07

Repositório: https://github.com/lucascarneiroo/pet-certo

Este documento resume, sprint a sprint, tudo que foi entregue entre a
Sprint 06 (Aprimoramento do Sistema) e a Sprint 07 (Processo de Adoção),
com os commits correspondentes no GitHub.

---

## Sprint 06 — Aprimoramento do Sistema

**Período:** 16/10/2026

| Commit | O que entrega |
|---|---|
| [`1e339d4`](https://github.com/lucascarneiroo/pet-certo/commit/1e339d4) | Trava de acesso por perfil, painéis reais e fluxo de visitas/documentos |
| [`75843c8`](https://github.com/lucascarneiroo/pet-certo/commit/75843c8) | Conecta as telas do admin e o histórico do adotante |
| [`d0f1baf`](https://github.com/lucascarneiroo/pet-certo/commit/d0f1baf) | Correções de segurança: bcrypt, remove admin fixo, indicadores reais |
| [`5dc5dbf`](https://github.com/lucascarneiroo/pet-certo/commit/5dc5dbf) | Documenta correções do feedback da professora (Sprints 3, 4 e 5) |

### O que mudou de verdade

**1. Navegação e acesso**
- Antes: qualquer pessoa digitando `/admin`, `/instituicao` ou `/adotante` na URL entrava, mesmo sem login ou logada com outro perfil.
- Agora: `RequireRole.jsx` bloqueia isso — sem login vai para `/entrar`, logado com perfil errado volta para a própria área.
- "Sair do painel" antes só navegava para a tela inicial sem apagar o token (a sessão continuava válida); agora desloga de verdade.

**2. Painéis com dados reais**
- Os quatro painéis que mostravam números fixos no código (Dashboard do admin, da instituição, do adotante, e Indicadores) passaram a buscar dados reais da API: nome de quem está logado, contagem de animais por situação, recomendações, solicitações, processos, taxa de conclusão, visitas realizadas.

**3. Processo de adoção conectado**
- `ong/Visits.jsx` e `adopter/Visits.jsx`: instituição cria horário, agenda visita, marca como realizada/cancelada; adotante acompanha.
- `ong/Documents.jsx` e `adopter/Documents.jsx`: adotante envia documento, instituição vê os documentos do processo.
- `adopter/Requests.jsx`: mostra as etapas reais do processo (Análise → Visita → Documentação → Aprovação).

**4. Telas do admin conectadas**
- `admin/Users.jsx`, `admin/Institutions.jsx`, `admin/Animals.jsx`: antes todas com listas fixas inventadas; agora dados reais, com exclusão de animal funcional e registro administrativo.
- Precisou de uma rota nova no backend (`GET /api/usuarios`), que não existia.

**5. Histórico do adotante**
- O "Perfil de Compatibilidade" (uma pesquisa de categorias que não existe no banco) foi trocado pelos dados reais de cadastro do adotante e pelo histórico real do processo de adoção.

**6. Segurança (feedback da professora)**
- Senhas: trocado SHA-256 simples por **bcrypt** (custo adaptativo).
- Removida a credencial de administrador fixa (`admin@petcerto.com` / `admin123`) que ficava no código — agora só é criada se `ADMIN_EMAIL`/`ADMIN_SENHA` estiverem no `.env` de cada pessoa.
- Driver do banco trocado de `psycopg2` para `pg8000` (resolve um bloqueio do Smart App Control do Windows em algumas máquinas, sem mexer em nenhuma configuração de segurança).

**7. Documentação**
- `docs/correcoes-feedback-professora.md`: cenários de teste documentados (23 + 14), regras de negócio, 12 bugs encontrados e corrigidos ao longo do projeto, explicação de como o núcleo de compatibilidade se integra ao backend.

---

## Sprint 07 — Processo de Adoção

**Período:** 22/10 a 25/10/2026

| Commit | O que entrega |
|---|---|
| [`ddff903`](https://github.com/lucascarneiroo/pet-certo/commit/ddff903) | Busca, filtros, exportação CSV e reforço dos logs administrativos |
| [`9003db5`](https://github.com/lucascarneiroo/pet-certo/commit/9003db5) | Fecha as lacunas de busca/filtro em Visitas, Documentos e Solicitações |

### O que mudou de verdade

**1. Etapas, visitas e documentação**
- Já estava pronto desde a Sprint 06 (ver acima) — não precisou de trabalho novo aqui, só foi confirmado que atende ao pedido específico desta sprint.

**2. Exportação (decisão da equipe: aplica-se, sim)**
- Nova utilidade `frontend/src/utils/exportarCsv.js`: gera CSV no navegador (sem biblioteca externa), separador `;` e BOM UTF-8 para abrir certo no Excel.
- Botão "Exportar CSV" em 5 telas: Animais e Processos (admin), Usuários (admin), Instituições (admin), Animais (instituição), Solicitações/manifestações (instituição).

**3. Pesquisas**
- Busca por nome adicionada em: Animais, Usuários, Instituições e Processos (admin); Visitas e Documentos (instituição). Antes só existia em Animais (instituição e adotante).

**4. Filtros**
- Filtro por situação adicionado em: Animais e Processos (admin), Solicitações (instituição e adotante), Visitas (instituição). Antes só existia em Animais (adotante, por característica).

**5. Logs**
- `registrar_acao_admin()` passou a cobrir também a **exclusão de animal** e o **cancelamento de processo** pelo administrador — antes só registrava a conclusão de processo.

**6. Relatórios**
- Decisão: em vez de criar uma tela nova e redundante, as telas de gestão do admin (Animais, Processos, Usuários, Instituições) passaram a funcionar como relatório — com busca, filtro e exportação juntos, que é exatamente o que o enunciado pede ("listagens, indicadores").

---

## Resumo — antes (Sprint 05) × depois (Sprint 07)

| Recurso | Antes | Depois |
|---|---|---|
| Acesso às telas por URL | Sem nenhuma trava | Bloqueado por perfil |
| "Sair do painel" | Não desligava a sessão | Desloga de verdade |
| Dashboards | Números fixos no código | Dados reais da API |
| Visitas/Documentos | Dados fixos | Conectados à API, dos dois lados |
| Telas do admin | Listas fixas inventadas | Dados reais, com ações funcionais |
| Senha de usuário | SHA-256 simples | bcrypt |
| Senha de admin | Fixa no código | Configurável, nunca commitada |
| Driver do banco | psycopg2 (bloqueado em algumas máquinas Windows) | pg8000 (sem esse problema) |
| Busca | Só em Animais | Em 7 telas diferentes |
| Filtro | Só em Animais (adotante) | Em 6 telas diferentes |
| Exportação | Não existia | CSV em 5 telas |
| Log administrativo | 1 tipo de ação registrada | 3 tipos de ação registradas |

---

## O que ainda fica de fora (de propósito, por decisão de escopo)

- `adopter/Visits.jsx` e `adopter/Documents.jsx` não têm busca/filtro — são listas pequenas, só com os dados do próprio adotante, de baixo valor para essa funcionalidade.
- Aprovação/rejeição de documento enviado (RF28) não existe, porque a tabela `Documento` no banco não tem uma coluna de status — isso exigiria alterar o `schema.sql`, que é responsabilidade do colega de banco de dados.
- Reescrever o histórico de commits antigos (Sprints 1 a 5) não foi feito, porque quebraria os clones locais dos outros integrantes do grupo — fica pendente de decisão do grupo.
