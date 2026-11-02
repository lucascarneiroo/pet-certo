# Sprint 08 — Gestão e conclusão

Repositório: https://github.com/lucascarneiroo/pet-certo

**Período:** 25/10 a 31/10/2026
**Tema:** Conclusão da adoção, histórico, dashboard, indicadores, usuários, permissões e registros.

Este documento cobre as 4 entregas obrigatórias da rubrica da Sprint 8.

---

## 1. Todas as funcionalidades implementadas

O que faltava: não existia **nenhuma tela** para a instituição avançar as etapas
de um processo de adoção, concluir a adoção ou cancelar um processo — apesar
do backend já suportar as três ações desde sprints anteriores.

**O que foi feito:** novo painel "Processos em andamento" em
[`ong/Requests.jsx`](frontend/src/pages/ong/Requests.jsx), com:
- lista das etapas do processo (Análise → Visita → Documentação → Aprovação),
  com a etapa atual destacada;
- botão para concluir a etapa em andamento;
- botão "Concluir adoção" (habilitado só quando as 4 etapas estão concluídas);
- botão "Cancelar processo", com motivo opcional.

Testado de ponta a ponta contra um banco descartável: avançar as 4 etapas,
concluir a adoção (o animal muda para "Adotado"), e cancelar um segundo
processo com motivo (o animal volta para "Disponível").

Commit: [`fde0695`](https://github.com/lucascarneiroo/pet-certo/commit/fde0695).

## 2. Controle de permissões

Revisado e reforçado nas duas pontas:

- **Frontend:** `RequireRole.jsx` continua bloqueando acesso a `/admin`,
  `/instituicao` e `/adotante` por quem não tem o perfil certo (ou não está
  logado) — confirmado tentando acessar `/admin` logado como instituição:
  redireciona de volta para `/instituicao`.
- **Backend:** toda rota sensível exige token válido (401 sem token/token
  inválido) e checa o perfil do usuário (403 se o perfil não bate) —
  confirmado testando `GET /api/usuarios` sem token, com token de adotante,
  e `POST /api/animais` com token de adotante.

A proteção não depende só da interface: mesmo chamando a API diretamente
(sem passar pela tela), o backend recusa a ação.

## 3. Melhorias de usabilidade

Revisão da navegação e dos estados de tela:

- Botões de ação crítica (concluir etapa, concluir adoção, cancelar
  processo, excluir animal) ficam desabilitados enquanto a ação está em
  andamento ("Processando...") para evitar duplo clique.
- "Concluir adoção" fica visivelmente desabilitado até que as 4 etapas
  estejam concluídas, para que a instituição veja de cara o que falta.
- Cancelamento de processo aceita um motivo opcional, que fica salvo no
  histórico do processo (visível ao adotante em "Histórico").
- Confirmado que `adopter/AnimalDetail.jsx` já impede manifestar interesse
  em um animal que não está "Disponível" (botão desabilitado).
- Mensagens de erro da API (ex.: "Este animal não está disponível no
  momento") aparecem na tela em vez de um erro genérico.

## 4. Revisão geral das regras de negócio

Revisão de `backend/database/adocao_repository.py` (fluxo de adoção).

**Bug encontrado e corrigido:** `concluir_processo()` só checava se o
processo estava "Em Andamento", sem verificar se as 4 etapas estavam
realmente concluídas. A tela nova bloqueava isso na interface, mas uma
chamada direta à API conseguia concluir a adoção pulando etapas — reproduzido
chamando o endpoint diretamente antes da correção (ver evidência 01).
Corrigido para o backend também validar isso, então a regra vale independente
de quem chama a API.

Commit: [`45762c6`](https://github.com/lucascarneiroo/pet-certo/commit/45762c6).

**Outras regras conferidas e já corretas:**
- só é possível manifestar interesse em animal "Disponível";
- não dá para manifestar interesse duas vezes no mesmo animal enquanto a
  manifestação anterior está pendente;
- aprovar a manifestação muda o animal para "Em Processo" e cria as 4
  etapas automaticamente (a primeira "Em Andamento", as demais "Pendente");
- cancelar um processo só devolve o animal para "Disponível" se não houver
  outro processo ativo para o mesmo animal (protege contra concorrência
  entre interessados);
- cada mudança de etapa, conclusão ou cancelamento gera uma linha em
  `HistoricoProcesso`, visível no histórico do adotante.

---

## Itens do cronograma desta sprint

| Item do cronograma | Status |
|---|---|
| Conclusão da adoção | Novo nesta sprint — item 1 acima |
| Histórico | Já existia (Sprint 06); confirmado mostrando a adoção concluída |
| Dashboard | Já existia (Sprint 06); confirmado com dados reais |
| Indicadores | Já existia (Sprint 06) |
| Usuários | Já existia (Sprint 06/07), com busca/filtro/exportação |
| Permissões | Reforçado nesta sprint — item 2 acima |
| Registros (log administrativo) | Já existia (Sprint 07) |

---

## Evidências

Capturas reais do sistema rodando (backend, PostgreSQL e frontend), numa
instância limpa do banco feita só para esta demonstração.

1. Tentativa de concluir a adoção sem etapas concluídas → bloqueada (HTTP 400).
2. Permissões reforçadas no backend: 401 sem token, 403 com perfil errado.
3. Instituição logada tentando acessar `/admin` → redirecionada para a própria área.
4. Painel "Processos em andamento" com o processo recém-aprovado.
5. As 4 etapas concluídas, "Concluir adoção" habilitado.
6. Depois de concluir: a lista de processos em andamento fica vazia.
7. Animal "Pingo" com status "Adotado" na tela de Animais da instituição.
8. Histórico do adotante mostrando toda a trilha do processo, da criação à conclusão.
9. Dashboard do admin com indicadores reais.
10. Lista de usuários do admin.

(Capturas em `docs/sprint8/evidencias/`, não versionadas no Git — enviadas
separadamente em um documento Word.)
