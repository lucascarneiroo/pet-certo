# PetCerto — Documentação Técnica do Backend

**Disciplina:** Fábrica de Software (integrado com Tópicos Avançados) — UNINASSAU, 2026.2
**Repositório:** https://github.com/lucascarneiroo/pet-certo

**Equipe:**
- PO / Scrum Master: Monique Rafaela de Carvalho Lopes
- Backend: Lucas Oliveira Carneiro
- Frontend: José Carlos Moura Silva
- Banco de dados e Documentação: Henrique Márcio Silva da Hora

---

## 1. Visão geral do projeto

O PetCerto é um sistema de adoção de animais que resolve um problema real de
abrigos e ONGs: a adoção hoje é feita quase sempre só pela foto do animal,
sem considerar se ele realmente combina com a rotina, o espaço e a
experiência do adotante — o que gera uma taxa alta de devolução.

O sistema propõe casar adotante e animal por **compatibilidade real**,
calculada por um algoritmo que soma critérios objetivos (porte, energia,
convivência com crianças e outros pets, espaço disponível, experiência do
adotante) e resolve a alocação como um problema de otimização, e não apenas
uma lista ordenada.

O projeto é dividido em **backend** (API, regras de negócio, banco de
dados) e **frontend** (interface, tecnologia a definir pela equipe), que se
comunicam por uma API REST em HTTP/JSON.

---

## 2. Arquitetura do sistema

O sistema segue uma arquitetura cliente-servidor: o backend expõe uma API
REST, e qualquer frontend (web, mobile ou desktop) consome essa API sem
precisar conhecer sua implementação interna.

**Camadas do backend:**

| Camada | Responsabilidade |
|---|---|
| API (`backend/api/`) | Recebe requisições HTTP, converte JSON ↔ objetos Python, controla acesso por perfil, devolve respostas |
| Autenticação (`backend/auth/`) | Login, cadastro de usuário, hash de senha, gerenciamento de sessões (tokens) |
| Dados / regras de negócio (`backend/database/`) | CRUD da entidade Animal, conexão com o banco, schema |
| Modelos (`backend/models/`) | Representação das entidades (Usuário, Animal) |
| Matching (`backend/matching/`) | Algoritmo de compatibilidade adotante-animal — componente computacional avançado, integrado com Tópicos Avançados |

**Fluxo de uma requisição autenticada (exemplo — criar um animal):**
1. Frontend faz `POST /api/auth/login` com e-mail e senha → recebe um token
2. Frontend envia esse token no cabeçalho `Authorization: Bearer <token>` nas próximas requisições
3. Frontend faz `POST /api/animais` com os dados do animal
4. Backend valida o token, confere se o perfil do usuário tem permissão, valida os dados e grava no banco
5. Backend devolve o animal criado (com `id` gerado) em JSON

**Tecnologias:**
- Backend: Python 3, biblioteca padrão apenas (sem Flask/Django/FastAPI), SQLite
- Componente avançado (matching): Python + NumPy (vetorização) + multiprocessing (paralelismo)
- Frontend: a definir pela equipe
- Versionamento: Git + GitHub

**Justificativa da escolha de banco:** SQLite foi usado nesta fase por não
exigir instalação de servidor — qualquer integrante roda o projeto local sem
configurar nada. Toda a lógica de acesso ao banco está concentrada em
`backend/database/`, então migrar para PostgreSQL ou MySQL no futuro é uma
mudança pontual, sem impacto no resto do backend.

---

## 3. Diagrama de Classes

**Entidades principais:**

**Usuario**
- Atributos: id, nome, email, perfil, data_cadastro
- Métodos: eh_admin(), eh_voluntario(), eh_adotante()

**Animal**
- Atributos: id, nome, especie, raca, porte, idade_anos, nivel_energia, temperamento, convive_criancas, convive_outros_pets, necessidades_especiais, espaco_recomendado, status, data_cadastro, cadastrado_por

**Módulos de serviço (funções, não classes tradicionais):**
- `AuthService` — criar_usuario(), autenticar(), listar_usuarios()
- `SessionService` — criar_sessao(), usuario_da_sessao(), encerrar_sessao()
- `AnimalRepository` — criar_animal(), listar_animais(), buscar_animal_por_id(), atualizar_animal(), excluir_animal()
- `PetCertoHandler` (API) — do_GET(), do_POST(), do_PUT(), do_DELETE()
- `CompatibilidadeMatching` — calcular_matriz_scores(), gerar_pareamento_estavel()

**Relacionamentos:**
- `AuthService` cria e consulta `Usuario`
- `AnimalRepository` gerencia `Animal`, e associa cada animal ao `Usuario` que o cadastrou
- `PetCertoHandler` usa `AuthService`, `SessionService` e `AnimalRepository`
- `CompatibilidadeMatching` usa os atributos de `Usuario` (adotante) e `Animal` para calcular compatibilidade

*(Diagrama Mermaid renderizável disponível em `docs/diagrama-classes.md` no repositório — abre automaticamente como imagem ao visualizar no GitHub.)*

---

## 4. Modelo Entidade-Relacionamento (MER)

**Entidades:**

**USUARIO**: id (PK), nome, email (chave única), senha_hash, salt, perfil, data_cadastro

**ANIMAL**: id (PK), nome, especie, raca, porte, idade_anos, nivel_energia, temperamento, convive_criancas, convive_outros_pets, necessidades_especiais, espaco_recomendado, status, data_cadastro, cadastrado_por (FK)

**Relacionamento:** um USUARIO pode cadastrar vários ANIMAIS (relação 1:N), representado pela chave estrangeira `cadastrado_por` em ANIMAL, apontando para o `id` do usuário responsável.

**Relacionamento futuro previsto:** quando o fluxo de adoção for implementado, uma nova entidade `Solicitacao_Adocao` vai conectar `Usuario` (adotante) a `Animal`, representando o processo de interesse → avaliação → aprovação → adoção.

*(Diagrama ER renderizável em `docs/mer.md` no repositório.)*

---

## 5. Modelo Relacional

### Tabela `usuarios`

| Coluna | Tipo | Restrições |
|---|---|---|
| id | INTEGER | PK, auto incremento |
| nome | TEXT | NOT NULL |
| email | TEXT | NOT NULL, UNIQUE |
| senha_hash | TEXT | NOT NULL — hash SHA-256, nunca senha em texto puro |
| salt | TEXT | NOT NULL — valor aleatório único por usuário |
| perfil | TEXT | NOT NULL, CHECK IN (admin, voluntario, adotante) |
| data_cadastro | TEXT | NOT NULL, automático |

### Tabela `animais`

| Coluna | Tipo | Restrições |
|---|---|---|
| id | INTEGER | PK, auto incremento |
| nome | TEXT | NOT NULL |
| especie | TEXT | NOT NULL, CHECK IN (cachorro, gato, outro) |
| raca | TEXT | opcional |
| porte | TEXT | NOT NULL, CHECK IN (pequeno, medio, grande) |
| idade_anos | REAL | NOT NULL |
| nivel_energia | TEXT | NOT NULL, CHECK IN (baixo, medio, alto) |
| temperamento | TEXT | opcional |
| convive_criancas | INTEGER | NOT NULL, booleano (0/1) |
| convive_outros_pets | INTEGER | NOT NULL, booleano (0/1) |
| necessidades_especiais | TEXT | opcional |
| espaco_recomendado | TEXT | NOT NULL, CHECK IN (apartamento, casa_com_quintal, indiferente) |
| status | TEXT | NOT NULL, CHECK IN (disponivel, em_processo, adotado) |
| data_cadastro | TEXT | NOT NULL, automático |
| cadastrado_por | INTEGER | FK → usuarios.id |

Schema executável completo: `backend/database/schema.sql`.

---

## 6. Banco de dados criado e conectado

O banco (SQLite) é criado automaticamente na primeira execução do backend,
a partir do schema acima. A conexão é validada em tempo real pela rota
`GET /api/health`, que executa uma consulta simples e confirma o status:

```json
{ "status": "ok", "banco_de_dados": "conectado" }
```

---

## 7. Login funcional

Implementado via `POST /api/auth/login`. O backend valida e-mail e senha
contra o banco (a senha nunca é armazenada em texto puro — é transformada
em hash SHA-256 com um salt aleatório único por usuário) e, se corretos,
gera um token de sessão aleatório que o cliente deve enviar nas próximas
requisições autenticadas, no cabeçalho `Authorization: Bearer <token>`.

---

## 8. Cadastro de usuários

Implementado via `POST /api/usuarios`. Valida campos obrigatórios
(nome, e-mail válido, senha com mínimo de 6 caracteres) e impede e-mail
duplicado. O cadastro público só permite os perfis `adotante` e
`voluntario` — o perfil `admin` não pode ser auto-atribuído, por regra de
negócio (evita escalonamento indevido de privilégio).

---

## 9. Controle de perfis

Três perfis de usuário, cada um com permissões diferentes, checadas em
cada rota da API:

| Perfil | Pode fazer |
|---|---|
| admin | CRUD completo de animais (criar, editar, excluir) + consultar usuários cadastrados |
| voluntario | Criar e editar animais, não pode excluir |
| adotante | Apenas consultar a lista de animais (somente leitura) |

Tentativas de ação sem permissão retornam erro HTTP 403, com mensagem
explicando o motivo.

---

## 10. CRUD principal funcionando

Entidade principal: **Animal**. Todas as operações são persistidas de
fato no banco (não há dados simulados em memória):

| Operação | Rota | Quem pode |
|---|---|---|
| Cadastrar | `POST /api/animais` | admin, voluntario |
| Consultar (lista) | `GET /api/animais` | qualquer perfil autenticado |
| Consultar (um) | `GET /api/animais/{id}` | qualquer perfil autenticado |
| Atualizar | `PUT /api/animais/{id}` | admin, voluntario |
| Excluir | `DELETE /api/animais/{id}` | somente admin |

---

## 11. Primeiro deploy local funcionando

**Como executar:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```
O servidor sobe em `http://localhost:8000`, criando o banco e um usuário
administrador padrão automaticamente na primeira execução.

**Como comprovar o funcionamento**, sem depender do frontend (ainda em
desenvolvimento): o script `backend/scripts/demo_cliente.py` simula um
frontend chamando cada rota da API em sequência — login, cadastro, criação
de animal, listagem, atualização de status, tentativa de exclusão sem
permissão (bloqueada corretamente) e exclusão com permissão. Executado com:
```bash
python scripts/demo_cliente.py
```
Todas as etapas passaram, confirmando o sistema funcionando de ponta a
ponta em ambiente local.

---

## 12. Algoritmo de Compatibilidade e Otimização/Paralelismo

**Componente computacional avançado do projeto**, integrado com a
disciplina de Tópicos Avançados. Código em `backend/matching/compatibilidade.py`.

### O problema

Dado um grupo de adotantes e um grupo de animais disponíveis, encontrar a
melhor forma de casar cada adotante com um animal — um problema de
**otimização combinatória em grafo bipartido** (o mesmo tipo de problema
usado, por exemplo, para alocar médicos residentes a hospitais).

### Etapa 1 — Score de compatibilidade

Cada par (adotante, animal) recebe uma nota de 0 a 1, somando critérios
com pesos diferentes:

| Critério | Peso |
|---|---|
| Porte | 20% |
| Nível de energia | 20% |
| Convivência com crianças | 15% |
| Convivência com outros pets | 15% |
| Espaço disponível | 15% |
| Experiência do adotante | 15% |

### Etapa 2 — Pareamento estável (algoritmo de Gale-Shapley)

Em vez de apenas ordenar por nota, o sistema resolve o problema como uma
alocação global: cada adotante "propõe" ao animal com maior compatibilidade
disponível; se dois adotantes disputam o mesmo animal, ele fica
provisoriamente com o de maior score, e o outro tenta a próxima opção. O
processo se repete até estabilizar. O resultado final é **estável**: não
existe nenhuma dupla adotante-animal fora do pareamento que prefeririam
trocar entre si — essa é a definição formal de estabilidade do algoritmo,
e é o que garante que a solução é uma otimização real, e não uma
ordenação simples.

### Otimização de desempenho

Foram implementadas três versões do cálculo da matriz de compatibilidade,
para comparação de desempenho:

1. **Ingênua** — laço Python aninhado (par a par), usada só como referência
2. **Vetorizada (NumPy)** — calcula a matriz inteira de uma vez com
   operações de array (broadcasting), usando rotinas otimizadas em C
3. **Paralela (multiprocessing)** — divide os animais em blocos e
   distribui entre processos, usando múltiplos núcleos de CPU

**Resultados reais do benchmark** (`python -m matching.benchmark`):

| Tamanho da base | Ingênua | Vetorizada (NumPy) | Paralela (multiprocessing) |
|---|---|---|---|
| 50 × 50 (2.500 pares) | 0,0015s | 0,0003s — **5,2x mais rápido** | 0,0200s — mais lenta que a ingênua |
| 200 × 200 (40.000 pares) | 0,0209s | 0,0014s — **14,5x mais rápido** | 0,0092s — 2,3x mais rápido |
| 1.000 × 1.000 (1.000.000 pares) | 0,7325s | 0,0395s — **18,5x mais rápido** | 0,0833s — 8,8x mais rápido |

**Conclusão técnica:** a versão vetorizada superou a paralela em todos os
volumes testados — criar e coordenar processos tem um custo fixo que só
compensa em bases bem maiores que as de um abrigo real. Por isso, o
sistema usa a versão vetorizada como padrão; a versão paralela permanece
implementada, testada e documentada como caminho de escalabilidade, caso
o volume de dados cresça (por exemplo, uma rede de abrigos).

**Sobre GPU (CUDA/OpenCL):** avaliado e descartado nesta fase — o custo de
transferir dados para a GPU só se paga em volumes da ordem de milhões de
pares, muito acima da escala real do problema. A decisão de priorizar CPU
(vetorização + paralelismo sob demanda) foi técnica, não por limitação.

### Status de integração

O módulo de matching funciona de forma independente e já foi testado e
validado (inclusive a correção do resultado entre a versão ingênua e a
vetorizada foi conferida automaticamente no benchmark). A integração com a
API (rota para recomendar animais a um adotante específico) depende da
criação de uma tabela para armazenar as preferências do adotante no banco,
prevista para a próxima sprint.

---

## 13. Estrutura do repositório no GitHub

```
pet-certo/
├── backend/
│   ├── main.py                    # ponto de entrada — inicia o servidor
│   ├── requirements.txt
│   ├── api/server.py              # rotas HTTP, autenticação, CORS
│   ├── auth/                      # login, cadastro, hash de senha, sessões
│   ├── database/                  # schema, conexão, CRUD de animais
│   ├── models/                    # entidades Usuario e Animal
│   ├── matching/                  # algoritmo de compatibilidade + benchmark
│   ├── scripts/demo_cliente.py    # demonstração ponta a ponta
│   └── data/                      # banco SQLite (gerado em runtime)
├── frontend/                      # interface (a cargo da equipe)
├── docs/                          # arquitetura, diagramas, modelo de dados, API
└── README.md
```

Repositório: https://github.com/lucascarneiroo/pet-certo
