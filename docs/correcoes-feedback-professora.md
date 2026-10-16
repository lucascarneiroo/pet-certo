# Correções do feedback da professora — Sprints 03, 04 e 05

Este documento reúne a resposta a cada ponto levantado nos feedbacks das
Sprints 03, 04 e 05, com o que foi feito, como foi testado e, onde fazia
sentido, a evidência real (comando, saída, mensagem de erro).

---

## Sprint 03 — Autenticação e Persistência

### 1. Integrar o cadastro de animais da instituição à API

Já estava feito desde a Sprint 4 ([commit `f0e4779`](https://github.com/lucascarneiroo/pet-certo/commit/f0e4779)):
`ong/Animals.jsx` cadastra, edita e muda a situação do animal chamando a
API real (`POST`/`PUT /api/animais`), com as etiquetas padronizadas em vez
de texto livre.

### 2. Bloquear, no frontend, o acesso a rotas incompatíveis com cada perfil

Feito na Sprint 06 ([commit `1e339d4`](https://github.com/lucascarneiroo/pet-certo/commit/1e339d4)):
`frontend/src/components/RequireRole.jsx` protege as rotas `/admin`,
`/instituicao` e `/adotante`. Sem login, redireciona para `/entrar`;
logado com outro perfil, redireciona para a área do próprio perfil.
Testado nos dois casos.

### 3. Substituir dados simulados dos painéis por dados reais

Feito em duas partes:

- Sprint 06 ([commit `1e339d4`](https://github.com/lucascarneiroo/pet-certo/commit/1e339d4)):
  os três painéis de "Visão geral" (`admin/Dashboard.jsx`,
  `ong/Dashboard.jsx`, `adopter/Dashboard.jsx`) passaram a buscar dados
  reais — nome do usuário logado, contagem de animais por situação,
  recomendações, solicitações e processos.
- Agora: `ong/Indicators.jsx`, que também tinha números fixos no código
  ("72%", "84 visitas realizadas" etc.), passou a calcular taxa de
  conclusão, visitas realizadas/comparecimento e manifestações pendentes
  a partir da API. Testado com dados reais:

  ```
  Taxa de conclusão: 0%  (0 de 1 processos)
  Visitas realizadas: 1  (100% comparecimento)
  Manifestações pendentes: 0
  Funil: 1 interesses → 1 processos → 1 visitas → 0 conclusões
  ```

### 4. Utilizar bcrypt ou Argon2id para o armazenamento seguro de senhas

Antes: `hashlib.sha256(salt + senha)` — um hash rápido, não projetado para
senha (vulnerável a força bruta em escala, mesmo com salt).

Agora: **bcrypt**, com custo adaptativo (`backend/auth/auth_service.py`).
O salt fica embutido no próprio hash gerado, não precisa mais de uma
coluna separada. Hashes do formato antigo (`salt$sha256`, de contas
criadas antes da migração) continuam sendo aceitos no login, para não
invalidar logins já existentes — mas todo cadastro novo e qualquer login
usam bcrypt a partir de agora.

Testado (banco limpo, direto no Python):

```
>>> hash salvo no banco: $2b$12$... (prefixo bcrypt confirmado)
>>> login com senha correta: OK
>>> login com senha errada: CredenciaisInvalidasError — "E-mail ou senha inválidos."
```

E a suíte completa (`scripts/teste_fluxo_adocao.py`, 23 verificações, que
cadastra e loga vários usuários) passou sem nenhuma alteração de
comportamento depois da migração.

### 5. Remover credenciais administrativas padrão fixas

Antes: `admin@petcerto.com` / `admin123` ficava **escrito no código-fonte**
(`backend/database/db.py`) e era criado automaticamente em toda
instalação — qualquer pessoa com acesso ao repositório sabia a senha de
admin de qualquer cópia rodando com a configuração padrão.

Agora: o administrador só é criado se `ADMIN_EMAIL` e `ADMIN_SENHA`
estiverem definidos no `.env` de quem está rodando (arquivo local, fora
do Git, com a senha de escolha da própria pessoa). Sem essas variáveis,
**nenhum admin é criado automaticamente** — o backend imprime um aviso
explicando como configurar. Documentado em `backend/.env.example` e
`backend/README.md`.

Testado:

```
$ python main.py          # sem ADMIN_EMAIL/ADMIN_SENHA no .env
Nenhum administrador padrão criado: defina ADMIN_EMAIL e ADMIN_SENHA
no seu .env para criar um automaticamente na primeira execução...

$ ADMIN_EMAIL=... ADMIN_SENHA=... python main.py
# admin criado normalmente, com a senha escolhida, em bcrypt
```

---

## Sprint 04 — Gerenciamento de Animais

### 6. Comprovar a persistência dos dados após reiniciar a aplicação e o banco

Teste real feito: com um animal (`Fred`, em processo de adoção) e outro já
adotado (`Rex`) gravados, **parei o processo do backend E o serviço do
PostgreSQL**, reiniciei os dois do zero, e consultei de novo:

```
--- ANTES de reiniciar ---
ANIMAIS: [{"id":3,"nome":"Fred","status":"Em Processo"},
          {"id":1,"nome":"Rex","status":"Adotado"}]

--- backend e banco parados, PostgreSQL reiniciado, backend reiniciado ---

--- DEPOIS de reiniciar backend + PostgreSQL ---
ANIMAIS: [{"id":3,"nome":"Fred","status":"Em Processo"},
          {"id":1,"nome":"Rex","status":"Adotado"}]
LOGIN ADMIN (bcrypt, pós-restart): OK - Administrador Padrão
```

Os mesmos registros, com os mesmos IDs e status — nada depende de estado
em memória do processo Python; tudo é lido de volta do PostgreSQL.

### 7. Documentar os cenários de teste, resultados esperados e mensagens de erro

O projeto tem dois scripts de teste automatizados, que rodam contra o
sistema de verdade (não são mocks):

- `backend/scripts/teste_fluxo_adocao.py` — ponta a ponta, contra a API
  HTTP real.
- `backend/scripts/teste_compatibilidade.py` — o núcleo de compatibilidade
  isolado (não precisa do servidor rodando).

#### `teste_fluxo_adocao.py` — 23 cenários

| # | Cenário | Resultado esperado |
|---|---|---|
| 1 | Cadastro de instituição | `201 Created` |
| 2 | Login da instituição | `200 OK`, token retornado |
| 3 | Cadastro de adotante | `201 Created` |
| 4 | Cadastro de animal com etiquetas | `201 Created` |
| 5 | Etiquetas do animal persistidas corretamente | etiquetas salvas = etiquetas enviadas |
| 6 | Cadastro de animal com etiqueta fora do vocabulário padrão | `400 Bad Request` — *"Características inválidas: ... Use apenas etiquetas do conjunto padrão."* |
| 7 | Favoritar animal | `200 OK` |
| 8 | Listar favoritos | `200 OK`, 1 item |
| 9 | Calcular compatibilidade | `200 OK`, score entre 0 e 100 |
| 10 | Manifestar interesse | `201 Created` |
| 11 | Manifestar interesse no mesmo animal de novo | `400 Bad Request` — *"Você já manifestou interesse por este animal."* |
| 12 | Instituição aprova a manifestação | `200 OK`, cria o processo |
| 13 | Animal muda para "Em Processo" após aprovação | status atualizado |
| 14 | Processo criado com as 4 etapas padrão | Análise, Visita, Documentação, Aprovação |
| 15 | Primeira etapa ativa, demais pendentes | `Análise = Em Andamento`, resto `Pendente` |
| 16 | Instituição cria horário de visita | `201 Created` |
| 17 | Concluir etapa "Análise" avança para a próxima | `Visita` passa a `Em Andamento` |
| 18 | Agendar visita | `201 Created` |
| 19 | Enviar documento | `201 Created` |
| 20 | Histórico do processo registra os eventos | pelo menos 3 entradas |
| 21 | Instituição **de outro abrigo** tenta concluir o processo | `403 Forbidden` — *"Este processo de adoção pertence a outra instituição."* |
| 22 | Instituição dona conclui o processo | `200 OK`, status `Concluído` |
| 23 | Animal muda para "Adotado" após conclusão | status atualizado |

#### `teste_compatibilidade.py` — 14 verificações (núcleo, sem precisar do servidor)

| # | Cenário | Resultado esperado |
|---|---|---|
| 1 | Perfil do adotante totalmente compatível com o animal | score alto (> 90) |
| 2 | Perfil totalmente incompatível | score baixo (< 40) |
| 3 | Comparação direta: compatível > incompatível | verdadeiro |
| 4 | Adotante sem histórico (cold start) | score neutro, entre os dois extremos acima |
| 5–9 | Cada categoria (porte, energia, espaço, espécie, experiência) deixando de bater, isoladamente | score cai a cada uma |
| 10 | Característica booleana concordando com o histórico | score mais alto que discordando |
| 11 | Animal sem nenhuma característica cadastrada | não quebra; score válido entre 0–100 |
| 12 | Implementação vetorizada vs. ingênua (conjunto fixo) | diferença numérica < 1e-9 |
| 13 | Pareamento Gale-Shapley usa todos os animais disponíveis | nº de pares = min(adotantes, animais) |
| 14 | Pareamento Gale-Shapley é estável | nenhum par fora dele prefere mutuamente trocar |

#### Outras mensagens de erro do sistema (validadas em uso real, não só nos scripts)

| Situação | Código | Mensagem |
|---|---|---|
| Senha de cadastro com menos de 6 caracteres | 400 | "Senha deve ter pelo menos 6 caracteres." |
| E-mail já cadastrado | 409 | "Já existe uma conta com este e-mail." |
| E-mail/senha incorretos no login | 401 | "E-mail ou senha inválidos." |
| Sem token de autenticação | 401 | "Token de autenticação ausente." |
| Adotante tentando cadastrar animal | 403 | "Apenas administradores e instituições podem realizar esta ação." |
| Instituição tentando favoritar/ver recomendações (ação de adotante) | 403 | "Apenas adotantes podem favoritar animais." / "Apenas adotantes têm recomendações." |
| Instituição tentando mexer em animal/processo de outra instituição | 403 | "Este animal pertence a outra instituição." / "Este processo de adoção pertence a outra instituição." |
| Excluir animal sem ser administrador | 403 | "Apenas administradores podem realizar esta ação." |
| Cadastro de adotante sem CPF/endereço | 400 | "Adotante precisa de CPF e endereço." |
| Cadastro de instituição sem CNPJ/localização | 400 | "Instituição precisa de CNPJ e localização." |

### 8. Organizar o histórico de commits por data, autor e funcionalidade

O histórico de commits já reflete data e autor automaticamente (metadados
do Git). O que fica a critério do grupo é **mensagens mais granulares por
funcionalidade** — a partir da Sprint 4, os commits já passaram a ser
divididos por entrega (ex.: "Sprint 4: gerenciamento de animais...",
"Sprint 06: trava de acesso por perfil...", "Correções de segurança..."),
em vez de um único commit grande por sprint.

**Não reescrevi o histórico já existente** (`git rebase`/`filter-branch`)
porque isso reescreve hashes de commit e pode quebrar os clones locais
dos outros integrantes do grupo (quem já tiver puxado o histórico antigo
teria conflito). Se o grupo quiser mesmo assim, é uma decisão para
combinar antes — me avisem se quiserem que eu faça.

---

## Sprint 05 — Núcleo de Compatibilidade

### 9. Comprovar a persistência e a recuperação dos dados no banco

A tabela `Compatibilidade` grava cada cálculo feito pelo adotante
(`salvar_compatibilidade`, chamado em `GET /api/animais/:id/compatibilidade`),
com `idAdotante`, `idAnimal`, `score` e os `fatores` (em JSON). Isso
sobrevive ao mesmo teste de reinício completo descrito no item 6 — os
dados do núcleo de compatibilidade (favoritos, recomendações e scores
calculados) seguem a mesma regra: tudo gravado no PostgreSQL, nada em
memória do processo.

### 10. Documentar as regras de negócio implementadas ou alteradas

Já documentado em detalhe em [`docs/algoritmo-compatibilidade.md`](algoritmo-compatibilidade.md)
(fórmula do score, pesos por critério, as três implementações, o
Gale-Shapley). Resumo das regras de negócio centrais do núcleo:

- O score é uma soma ponderada: Porte 20%, Energia 20%, Espaço 15%,
  Espécie 10%, Experiência 10%, mais três características booleanas
  (Convive com Crianças 10%, Convive com Outros Pets 10%, Necessidades
  Especiais 5%) — total 100%.
- A preferência do adotante é **aprendida**, não cadastrada: vem da
  frequência das etiquetas dos animais que ele já favoritou. Sem
  histórico, o sistema usa uma preferência neutra (cold start), nem
  favorece nem prejudica o adotante novo.
- O score é sempre limitado entre 0 e 100 (`np.clip`).
- Recomendações (`/api/recomendacoes`) nunca incluem um animal já
  favoritado pelo próprio adotante, e são limitadas às 10 melhores.

Regras de negócio do fluxo de adoção (fora do núcleo, mas também parte
desta sprint):

- Um adotante não pode manifestar interesse duas vezes pelo mesmo animal
  enquanto a manifestação anterior não for recusada.
- Só a instituição dona do animal (ou o administrador) pode aprovar,
  recusar, concluir ou cancelar um processo — nunca outra instituição.
- Aprovar uma manifestação cria o processo com 4 etapas em ordem fixa
  (Análise → Visita → Documentação → Aprovação); só a etapa atual fica
  "Em Andamento", as demais ficam "Pendente" até chegar a vez delas.
- Um horário de visita só pode ser reservado uma vez (`status` muda de
  "Disponível" para "Reservado" ao ser agendado).
- O status do animal muda sozinho, automaticamente: "Disponível" →
  "Em Processo" (ao aprovar) → "Adotado" (ao concluir), ou volta a
  "Disponível" se o processo for cancelado.
- Excluir animal é exclusivo do administrador (nem a própria instituição
  dona pode excluir, só alterar a situação).

### 11. Registrar os bugs encontrados e suas respectivas correções

| Bug encontrado | Como foi achado | Correção |
|---|---|---|
| `python matching/benchmark.py` falhava com `ModuleNotFoundError` | Tentando rodar o comando documentado no README | Trocado para `python -m matching.benchmark` (README e `docs/algoritmo-compatibilidade.md`) |
| Núcleo de compatibilidade não tinha nenhum teste de corretude com diferentes perfis, só o benchmark de performance | Revisão de cobertura (RNF25) | Criado `scripts/teste_compatibilidade.py`, 14 verificações |
| Busca/filtro de animais não existia no backend (só status/id_instituicao) | Revisão de requisitos da Sprint 4 | Adicionados parâmetros `busca` e `caracteristicas` em `GET /api/animais` |
| A tela de gerenciamento de animais da instituição não tinha botão de favoritar em lugar nenhum do sistema, mas o núcleo de compatibilidade inteiro depende de favoritos | Ao escrever o roteiro de teste da Sprint 6 | Botão "☆ Favoritar" adicionado em `AnimalDetail.jsx` |
| `admin/Animals.jsx` mostrava "undefined · undefined" no nome do animal/instituição | Teste manual pelo navegador, logo após conectar a tela | Campo errado (`a.nome`/`a.nome_instituicao`, nomes do backend) trocado pelos campos já traduzidos pelo frontend (`a.name`/`a.institution`) |
| "Sair do painel" não encerrava a sessão de verdade — só navegava para a tela inicial, o token continuava salvo | Revisão de navegação (Sprint 06) | `Sidebar.jsx` passou a chamar `logout()` antes de navegar |
| Nenhuma rota (`/admin`, `/instituicao`, `/adotante`) exigia login ou perfil correto | Revisão de navegação (Sprint 06) | Criado `RequireRole.jsx`, aplicado nas três áreas |
| A compatibilidade calculada só devolvia um resumo genérico ("baseado em N favoritos"), sem dizer qual critério pesou mais | Comparando com o que a Sprint 1 havia planejado (RF16) | `fatores_por_criterio()` no núcleo, retornando a afinidade por critério |
| A instituição não tinha como ver a compatibilidade de um adotante específico ao analisar uma manifestação | Implementando a tela de análise da instituição (Sprint 6) | Endpoint novo `GET /api/manifestacoes/:id/compatibilidade` |
| `psycopg2` bloqueado pelo Smart App Control do Windows em máquinas com essa proteção ativada | Ao tentar rodar o projeto numa máquina com Smart App Control ligado | Trocado por `pg8000` (driver 100% Python, sem binário nativo) |
| Senha de administrador fixa no código-fonte | Feedback da professora | Removida; agora só é criada via `ADMIN_EMAIL`/`ADMIN_SENHA` no `.env` |
| Hash de senha com SHA-256 simples (rápido, não resistente a força bruta) | Feedback da professora | Migrado para bcrypt |

### 12. Explicar a integração do núcleo computacional com o backend e o fluxo de recomendações

O núcleo (`backend/matching/compatibilidade.py`) é um **módulo Python
importado diretamente** pelo backend — não é um serviço externo chamado
por HTTP. O fluxo completo, do clique do usuário até a recomendação:

```
1. Adotante favorita um animal (POST /api/animais/:id/favoritar)
   → grava na tabela Favorito.

2. Em qualquer chamada de compatibilidade/recomendação, o backend monta
   o histórico de etiquetas dos animais favoritados
   (server.py: _preferencia_do_adotante)
   → chama vetor_de_preferencia(historico) do núcleo, que aprende a
     preferência do adotante a partir dessas etiquetas (ou devolve uma
     preferência neutra, se não houver histórico).

3a. Tela do animal (compatibilidade individual):
    GET /api/animais/:id/compatibilidade
    → vetor_do_animal(caracteristicas) + calcular_matriz_scores(P, A)
      → score (0-100) + fatores_por_criterio(P, caracteristicas)
      → salva em Compatibilidade e devolve {score, fatores} ao frontend.

3b. Ranking de recomendações:
    GET /api/recomendacoes
    → monta a matriz de TODOS os animais disponíveis que o adotante
      ainda não favoritou (matriz_dos_animais)
      → calcular_matriz_scores(preferencia, matriz) calcula o score de
        cada um de uma vez (vetorizado com NumPy)
      → ordena do maior score para o menor, devolve os 10 primeiros.

3c. Análise pela instituição:
    GET /api/manifestacoes/:id/compatibilidade
    → mesmo cálculo do passo 3a, mas usando a preferência do ADOTANTE da
      manifestação (não de quem está logado) — é assim que a instituição
      vê o quanto aquele adotante específico combina com o animal, sem
      ter acesso ao perfil de compatibilidade de ninguém mais.

4. Manifestação de interesse aprovada → ProcessoAdocao criado com as 4
   etapas; a partir daí, o fluxo de acompanhamento (visitas, documentos,
   histórico) é tratado pelo módulo de adoção (`adocao_repository.py`),
   que não depende mais do núcleo de compatibilidade.
```

Em nenhum ponto o frontend fala diretamente com o núcleo — ele sempre
passa pelo backend HTTP, que por sua vez importa e chama as funções do
núcleo como qualquer outro módulo Python do projeto. É isso que atende à
exigência da disciplina de o componente avançado ser desenvolvido e
integrado ao software, não apenas uma API externa consumida.
